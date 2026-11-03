"""Strict rejection may use only the verified original per-turn evolution fallback."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from amem_repro.adapter import AdapterError, DeepSeekController
from amem_repro.contracts import load_author_contracts
from amem_repro.config import RUN2_CONFIG
from test_adapter import Client, completion

ROOT = Path(__file__).resolve().parents[1]
BAD = '{"should_evolve":true,"actions"["strengthen"]}'


def test_malformed_decision_reaches_explicit_failure_adjudicator_without_returning_json():
    calls=[]
    permit=SimpleNamespace(start_logical=lambda stage:1,
        handle_generation_failure=lambda event,error:calls.append(('adjudicate',event['output'],type(error.__cause__).__name__)),
        stop=lambda reason:calls.append(('stop',reason)))
    event=completion(BAD);event['system_fingerprint']='bc19ba97cbe016479903222bb1578db6'
    client=Client(event)
    controller=DeepSeekController(client,phase_permit=permit,generation_config=RUN2_CONFIG)
    with pytest.raises(AdapterError):
        controller.get_completion('original',load_author_contracts()['shared_decision'])
    assert calls == [('adjudicate',BAD,'JSONDecodeError')]
    assert len(client.requests)==1

from test_run2 import short_runner, approved_phase, execute_fixture
from amem_repro import run2
from amem_repro.evolution_fallback import POLICY_ID, malformed_decision


@pytest.fixture
def fallback_runner(short_runner, monkeypatch):
    import httpx
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.observability import LangfuseObserver
    from test_observability import Client as CloudClient, identity
    original=run2._binding
    def binding(campaign,index):
        return {**original(campaign,index),'evolution_failure_policy':POLICY_ID}
    monkeypatch.setattr(run2,'_binding',binding)
    fixture=short_runner; shared=0
    (fixture['root']/'.git').symlink_to(ROOT/'.git',target_is_directory=True)
    (fixture['root']/'memory_layer.py').symlink_to(ROOT/'memory_layer.py')
    fixture['_malformed_turns']={2,4}
    fixture['_response_kind']='malformed'
    def sdk(request):
        nonlocal shared
        wire=json.loads(request.content);response=fixture['_provider'].complete(**wire)
        response['system_fingerprint']=run2.MODEL_FINGERPRINT
        if 'should_evolve' in wire['tools'][0]['function']['parameters']['properties']:
            shared+=1
            if shared in fixture['_malformed_turns']:
                args=BAD
                kind=fixture['_response_kind']
                if isinstance(kind,dict):kind=kind.get(shared,'malformed')
                if kind=='wrapped':
                    args='wrapper\n'+json.dumps({'should_evolve':True,'actions':[], 'suggested_connections':[],
                       'tags_to_update':[],'new_context_neighborhood':[],'new_tags_neighborhood':[]})+'\ntrailer'
                if kind=='length':
                    response['choices'][0]['finish_reason']='length'
                    response['usage']['completion_tokens']=8192
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments']=args
                if fixture.get('_saved_response') is not None:
                    response=copy.deepcopy(fixture['_saved_response'])
        return httpx.Response(200,json=response)
    fixture['controller_factory']=lambda **kw:create_deepseek_controller(**kw,http_transport=httpx.MockTransport(sdk))
    fixture['observer']=LangfuseObserver(CloudClient(),{**identity('fallback-test'),
        'campaign_id':run2.CAMPAIGN_ID,'condition':'full','conversation_id':'conv-44',
        'evolution_failure_policy':POLICY_ID})
    return fixture


def test_successive_malformed_decisions_keep_original_fallback_and_finish_degraded(fallback_runner):
    f=fallback_runner;p=execute_fixture(approved_phase(f['campaign']),f)
    n=len(next(c for c in f['_manifest']['conversations'] if c['original_id']=='conv-44')['turn_ids'])
    assert p['status']=='degraded' and p['usable_for_next_phase']
    assert p['total_memory_notes']==n and p['completed_questions']==1
    assert p['budget']['logical_calls']==2*n+2==p['budget']['physical_attempts']
    events=run2._read_lines(f['root']/'artifacts/run2/runs'/p['run_id']/'events.jsonl')
    proof=[e for e in events if e.get('kind')=='original_evolution_fallback']
    assert len(proof)==2 and all(e['original_fallback_verified'] for e in proof)
    for e in proof:
        assert e['counter_before']==e['counter_after']
    bad=[e for e in events if e['type']=='generation' and e.get('error_type')]
    assert len(bad)==2 and all(e['output']==BAD for e in bad)
    capture=f['observer'].finish()
    assert len([e for e in capture['observations'] if e['name']=='A-MEM/original_evolution_fallback'])==2
    assert all(e['level']=='ERROR' for e in capture['observations'] if e['name']=='shared_decision' and e['output']==BAD)
    assert (f['root']/'artifacts/run2/runs'/p['run_id']/'scoring-views.json').is_file()


@pytest.mark.parametrize('kind',['wrapped','length'])
def test_cleanup_parsable_wrappers_and_exhaustion_remain_fatal(fallback_runner,kind):
    f=fallback_runner;f['_response_kind']=kind
    p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='incomplete' and not p['usable_for_next_phase']
    assert p['total_memory_notes']==2 and p['completed_questions']==0
    assert p['budget']['physical_attempts']==4
    assert p['recoverable_length_failure'] is (kind=='length')


def test_real_saved_malformed_arguments_are_eligible_without_repair():
    path=ROOT/'artifacts/run2/runs/run2-full-conv-44-r0-p1/events.jsonl'
    if not path.exists():pytest.skip('Optional immutable incident archive')
    bad=[e for e in run2._read_lines(path) if e['type']=='generation' and e.get('error_type')][-1]
    raw=bad['output']
    assert malformed_decision(bad)
    assert bad['output']==raw
    for field,value in [('stage','metadata'),('max_tokens',4000),('returned_model','other')]:
        changed=copy.deepcopy(bad);changed[field]=value
        assert not malformed_decision(changed)


def test_malformed_then_output_exhaustion_keeps_both_failures(fallback_runner):
    f=fallback_runner;f['_response_kind']={2:'malformed',4:'length'}
    p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='incomplete' and p['total_memory_notes']==4
    assert p['recoverable_length_failure'] and p['budget']['physical_attempts']==8


@pytest.mark.parametrize('change',['neighbour','counter','index','new_metadata'])
def test_unverified_fallback_state_cannot_release_next_transmission(fallback_runner,monkeypatch,change):
    from amem_repro.evolution_fallback import OriginalFallbackGuard
    original=OriginalFallbackGuard.after
    def changed(self,agent,*args):
        if self.permit._pending_evolution:
            system=agent.memory_system
            if change=='neighbour':next(iter(system.memories.values())).tags.append('unexpected')
            if change=='counter':system.evo_cnt+=1
            if change=='index':system.retriever.embeddings[0,0]+=1
            if change=='new_metadata':list(system.memories.values())[-1].context='unexpected'
        return original(self,agent,*args)
    monkeypatch.setattr(OriginalFallbackGuard,'after',changed)
    f=fallback_runner;p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='incomplete' and not p['usable_for_next_phase']
    assert p['budget']['physical_attempts']==4 and p['total_memory_notes']==2
    assert p['budget']['halt_persisted']


def test_pending_fallback_is_not_a_restart_or_an_unhalt(fallback_runner,monkeypatch):
    from amem_repro.evolution_fallback import OriginalFallbackGuard
    from amem_repro.budget import BudgetStop
    original=OriginalFallbackGuard.after
    def interrupt(self,agent,*args):
        if self.permit._pending_evolution:
            with pytest.raises(BudgetStop):self.permit.start_logical('metadata')
        return original(self,agent,*args)
    monkeypatch.setattr(OriginalFallbackGuard,'after',interrupt)
    f=fallback_runner;approval=approved_phase(f['campaign']);p=execute_fixture(approval,f)
    assert p['status']=='incomplete' and p['budget']['physical_attempts']==4
    with pytest.raises(BudgetStop):run2.Run2Permit(approval,f['root'],f['campaign'])


@pytest.mark.parametrize('stage',['metadata','query_keywords','answer'])
def test_other_generation_stages_remain_fatal(fallback_runner,stage):
    import httpx
    from amem_repro.adapter import create_deepseek_controller
    f=fallback_runner;f['_malformed_turns']=set()
    contracts=load_author_contracts()
    def sdk(request):
        wire=json.loads(request.content);response=f['_provider'].complete(**wire)
        response['system_fingerprint']=run2.MODEL_FINGERPRINT
        if wire['tools'][0]['function']['parameters']==contracts[stage]['json_schema']['schema']:
            response['choices'][0]['message']['tool_calls'][0]['function']['arguments']=BAD
        return httpx.Response(200,json=response)
    f['controller_factory']=lambda **kw:create_deepseek_controller(**kw,http_transport=httpx.MockTransport(sdk))
    p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='incomplete' and not p['usable_for_next_phase']
    assert p['budget']['halt_persisted'] and p['completed_questions']==0


def test_classifier_storage_fault_is_terminal_before_author_can_absorb_it(fallback_runner,monkeypatch):
    from amem_repro import evolution_fallback
    def fail(*args,**kwargs):raise OSError('offline injected classifier storage failure')
    monkeypatch.setattr(evolution_fallback,'malformed_decision',fail)
    f=fallback_runner;p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='incomplete' and p['budget']['physical_attempts']==4
    assert p['budget']['halt_persisted'] and p['total_memory_notes']==1


def test_instrumented_policy_matches_uninstrumented_original_response_replay(fallback_runner,tmp_path):
    from amem_repro import runner
    from amem_repro.replay import ReplayController, memory_view
    f=fallback_runner;p=execute_fixture(approved_phase(f['campaign']),f)
    directory=f['root']/'artifacts/run2/runs'/p['run_id']
    records=[e for e in run2._read_lines(directory/'events.jsonl') if e['type']=='generation']
    controller=None
    def replay(journal):
        nonlocal controller
        if controller is None:
            controller=ReplayController(records,observer=journal,provider_contract_policy='canonical-index-strings-v1',generation_config=RUN2_CONFIG)
        return controller
    factory=f['factory_builder'](replay,f['token_counter'],'full')
    replay_dir=tmp_path/'original-replay'
    summary=runner.run_manifest(f['root']/'data/locomo10.json',f['_manifest'],RUN2_CONFIG,
        output_dir=replay_dir,cache_root=tmp_path/'replay-cache',source_hashes=f['_sources'],
        agent_factory=factory,scorer=f['scorer'],run_id='original-replay',condition='full',
        conversation_ids=['conv-44'],execution_type='deterministic_replay',
        provider_contract_policy='canonical-index-strings-v1')
    controller.finish()
    original=json.loads(next((tmp_path/'replay-cache').rglob('state.json')).read_text())
    observed_state=json.loads(next((f['root']/'artifacts/run2/cache').rglob('state.json')).read_text())
    assert memory_view(original)==memory_view(observed_state)
    from amem_repro.scoring import rescore_records
    predictions=[e['result'] for e in run2._read_lines(replay_dir/'events.jsonl') if e['type']=='question_result']
    assert json.loads((directory/'scoring-views.json').read_text())==rescore_records(predictions,f['scorer'])
    assert summary['status']=='degraded'


def test_exact_saved_blk014_response_uses_original_fallback_and_next_turn(fallback_runner):
    path=ROOT/'artifacts/run2/runs/run2-full-conv-44-r0-p1/events.jsonl'
    if not path.exists():pytest.skip('Optional exact provider evidence')
    bad=[e for e in run2._read_lines(path) if e['type']=='generation' and e.get('error_type')][-1]
    f=fallback_runner;f['_saved_response']=bad['provider_response'];f['_malformed_turns']={2}
    p=execute_fixture(approved_phase(f['campaign']),f)
    assert p['status']=='degraded' and p['usable_for_next_phase']
    events=run2._read_lines(f['root']/'artifacts/run2/runs'/p['run_id']/'events.jsonl')
    rejected=[e for e in events if e['type']=='generation' and e.get('error_type')]
    assert len(rejected)==1 and rejected[0]['output']==bad['output']
    with pytest.raises(json.JSONDecodeError) as error:json.loads(rejected[0]['output'])
    assert error.value.pos==7052
    proof=[e for e in events if e.get('kind')=='original_evolution_fallback']
    assert len(proof)==1 and proof[0]['original_fallback_verified']


def test_author_strip_parseable_control_wrapper_is_not_a_supported_fallback():
    path=ROOT/'artifacts/run2/runs/run2-full-conv-44-r0-p1/events.jsonl'
    if not path.exists():pytest.skip('Optional incident fixture')
    event=copy.deepcopy([e for e in run2._read_lines(path) if e['type']=='generation' and e.get('error_type')][-1])
    raw='\x1c'+json.dumps({'should_evolve':True,'actions':[], 'suggested_connections':[],
        'tags_to_update':[],'new_context_neighborhood':[],'new_tags_neighborhood':[]})+'\x1c'
    event['output']=raw
    event['provider_response']['choices'][0]['message']['tool_calls'][0]['function']['arguments']=raw
    event['attempts'][-1]['response_body']['choices'][0]['message']['tool_calls'][0]['function']['arguments']=raw
    assert json.loads(raw.strip())['should_evolve'] is True
    assert not malformed_decision(event)
