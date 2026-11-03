"""Run2 profile, durable cell allocation and exact-state continuation contracts."""
import copy
import json
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from amem_repro.config import DEFAULT_CONFIG, RUN2_CONFIG, load_run2_config, stage_output_limits, validate_config
from amem_repro.adapter import DeepSeekController
from amem_repro.contracts import load_author_contracts
from test_adapter import Client, completion
from amem_repro import run2
from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.artifacts import restore_memory
from amem_repro.replay import memory_view

ROOT = Path(__file__).resolve().parents[1]


def test_run2_profile_changes_only_identity_and_shared_output_limit():
    actual = load_run2_config()
    expected = copy.deepcopy(DEFAULT_CONFIG)
    expected['protocol_id'] = 'amem-controlled-reproduction-run2-v1'
    expected['generation'].update(shared_decision_max_tokens=8192,
                                  output_token_policy='run2-shared-decision-8192-v1')
    assert actual == expected == RUN2_CONFIG
    assert stage_output_limits()['shared_decision'] == 4000
    assert stage_output_limits(actual) == {'metadata': 1000, 'shared_decision': 8192,
                                         'query_keywords': 1000, 'answer': 1000}
    changed = copy.deepcopy(actual)
    changed['retrieval']['answer_k'] = 9
    with pytest.raises(ValueError, match='frozen'):
        validate_config(changed)


def test_run2_adapter_keeps_original_arguments_and_schema_with_explicit_cap():
    raw = '{"should_evolve":false,"actions":[],"suggested_connections":[],"tags_to_update":[],"new_context_neighborhood":[],"new_tags_neighborhood":[]}'
    client = Client(completion(raw))
    controller = DeepSeekController(client, generation_config=load_run2_config())
    contract = load_author_contracts()['shared_decision']
    assert controller.get_completion('same prompt', contract) == raw
    assert client.requests[0]['max_tokens'] == 8192
    assert client.requests[0]['tools'][0]['function']['parameters'] == contract['json_schema']['schema']
    original = Client(completion(raw))
    DeepSeekController(original).get_completion('same prompt', contract)
    assert original.requests[0]['max_tokens'] == 4000


def approved_campaign():
    return {'campaign_id': run2.CAMPAIGN_ID, 'approved': True, 'approval_id': 'campaign',
            'approved_by': 'offline test', 'approved_at': '2026-11-03T00:00:00Z',
            'cells': [{'condition': c, 'conversation_id': v, 'turns': run2.CONVERSATIONS[v][0],
                       'questions': run2.CONVERSATIONS[v][1]} for c,v in run2.CELL_ORDER],
            'limits': {'campaign_usd': '42', 'cell_usd': '5', 'max_logical_calls': 18480, 'max_attempts':55440},
            'pricing': run2.PRICING,
            'initial_stage_costs': {s:{'calls':1,'cost_microusd':100}
                                    for s in ('metadata','shared_decision','query_keywords','answer')},
            'binding': {k: fingerprint(RUN2_CONFIG) if k=='config_sha256' else 'b'*64
                        for k in ('config_sha256','source_sha256','manifest_sha256','preflight_sha256',
                                  'gate_a_sha256','gate_b_sha256','run1_preservation_sha256')}}


def approved_phase(campaign, *, index=0, seq=0, checkpoint=None, cap='5'):
    b=run2._binding(campaign,index)
    if checkpoint is not None:b['checkpoint']=checkpoint
    n=2*(b['expected_turns']-(checkpoint['completed_turns'] if checkpoint else 0)+b['expected_questions'])
    return {'phase':'run2','phase_index':seq,'run_id':f"run2-{b['condition']}-{b['conversation_ids'][0]}-r0-p{seq}",
            'approved':True,'approval_id':f'phase-{index}-{seq}','approved_by':'offline test',
            'approved_at':'2026-11-03T00:00:00Z','binding':b,'pricing':run2.PRICING,
            'limits':{'phase_usd':cap,'max_logical_calls':n,'max_attempts':3*n}}


def reserve_and_settle(permit, output=10):
    ident=permit.start_logical('metadata')
    attempt=permit.reserve_attempt(ident,{'model':'deepseek-flash','endpoint':'https://api.deepseek.com/beta/chat/completions',
                                        'max_tokens':1000,'temperature':.7,'thinking':'disabled','stream':False,
                                        'provider_contract_policy':'canonical-index-strings-v1'})
    permit.settle(attempt,{'prompt_tokens':100,'completion_tokens':output})
    return attempt


def test_run2_permit_is_single_use_and_does_not_claim_run1_ledger(tmp_path):
    campaign=approved_campaign();phase=approved_phase(campaign)
    permit=run2.Run2Permit(phase,tmp_path,campaign)
    reserve_and_settle(permit)
    assert permit.summary()['charged_or_reserved_microusd']==42
    assert not (tmp_path/'artifacts/study-budget.sqlite').exists()
    with pytest.raises(BudgetStop,match='already consumed'):
        run2.Run2Permit(phase,tmp_path,campaign)
    with pytest.raises(BudgetStop,match='serial'):
        run2.Run2Permit(approved_phase(campaign,index=1),tmp_path,campaign)


class OfflineObserver:
    def __init__(self):self.events=[];self.errors=[]
    def __call__(self,event):self.events.append(copy.deepcopy(event))
    def assert_healthy(self):
        if self.errors:raise RuntimeError('offline tracing failure')
    def finish(self):return {'trace_ids':['offline-trace'],'events':self.events}


def observed(receipt,context):
    return {'verified':True,'trace_ids':['offline-trace'],'evidence_sha256':'a'*64}


def experiments(views,context):
    return {'verified':True,'experiment_ids':{k:'offline-'+k for k in views},
            'results_sha256':fingerprint(views),'evidence_sha256':'a'*64}


@pytest.fixture
def short_runner(tmp_path,monkeypatch,request):
    """Original runner/algorithm, explicitly smaller offline execution partition."""
    import httpx
    import numpy as np
    from amem_repro import runner
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.actions import make_action_agent_factory
    from amem_repro.author import make_agent_factory
    from amem_repro.config import source_fingerprint
    from amem_repro.manifests import build_manifest
    from amem_repro.measurements import TokenCounter
    from amem_repro.scoring import AuthorScorer
    from test_foundation import Provider, LocalRetriever, original_memory_module
    from test_scoring import dependencies
    monkeypatch.setenv('DEEPSEEK_API_KEY','offline-placeholder')
    manifest=build_manifest(ROOT/'data/locomo10.json','fallback')
    conversation=next(c for c in manifest['conversations'] if c['original_id']=='conv-44')
    raw=json.loads((ROOT/'data/locomo10.json').read_text())[conversation['sample_index']]
    variant=getattr(request,'param',('full',1))
    condition,session_count=variant if isinstance(variant,tuple) else ('full',variant)
    selected_sessions=conversation['session_keys'][:session_count]
    n=sum(len(raw['conversation'][key]) for key in selected_sessions)
    conversation['session_keys']=selected_sessions;conversation['turn_ids']=conversation['turn_ids'][:n]
    conversation['questions']=conversation['questions'][:1]
    monkeypatch.setitem(run2.CONVERSATIONS,'conv-44',(n,1))
    if condition!='full':
        order=list(run2.CELL_ORDER);index=order.index((condition,'conv-44'));order[0],order[index]=order[index],order[0]
        monkeypatch.setattr(run2,'CELL_ORDER',order) # Offline same-condition recovery seam, not production order.
    sources=source_fingerprint(ROOT);receipt={'assets':{},'runtime':{'ok':True}}
    campaign=approved_campaign();campaign['binding'].update(source_sha256=fingerprint(sources),
            manifest_sha256=fingerprint(manifest),preflight_sha256=fingerprint(receipt))
    (tmp_path/'data').symlink_to(ROOT/'data',target_is_directory=True)
    monkeypatch.setattr(run2,'_check_campaign_runtime',lambda *a,**kw:(copy.deepcopy(RUN2_CONFIG),copy.deepcopy(manifest),sources))
    # Only the fixture partition changes; production expand_manifest is separately
    # strict and never accepts this first-session synthetic test selection.
    monkeypatch.setattr(runner,'expand_manifest',lambda *a:copy.deepcopy(manifest))
    # The other implementer adds this exact optional safe-boundary hook. Until
    # integration, this slice still executes the complete unchanged runner.
    import inspect
    if 'boundary_check' not in inspect.signature(runner.run_manifest).parameters:
        original=runner.run_manifest
        def runner_until_integration(*a,**kw):
            check=kw.pop('boundary_check',None)
            if check is not None:check()
            return original(*a,**kw)
        monkeypatch.setattr(runner,'run_manifest',runner_until_integration)
    class Retriever(LocalRetriever):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.embeddings=np.empty((0,384),dtype=np.float32)
        def add_documents(self,documents):
            for document in documents:
                self.document_ids[document]=len(self.corpus);self.corpus.append(document)
                self.embeddings=np.vstack((self.embeddings,np.ones((1,384),dtype=np.float32)))
    provider=Provider();shared=0;failure_turns={2,4} if session_count==1 else {99,101}
    def sdk(request):
        nonlocal shared
        wire=json.loads(request.content);response=provider.complete(**wire)
        response['system_fingerprint']=run2.MODEL_FINGERPRINT
        fields=wire['tools'][0]['function']['parameters']['properties']
        if 'should_evolve' in fields:
            shared+=1
            value=json.loads(response['choices'][0]['message']['tool_calls'][0]['function']['arguments'])
            value['suggested_connections']=[str(v) for v in value['suggested_connections']]
            response['choices'][0]['message']['tool_calls'][0]['function']['arguments']=json.dumps(value)
            if shared in failure_turns:
                response['choices'][0]['finish_reason']='length'
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments']='{"should_evolve":'
                response['usage']={'prompt_tokens':100,'completion_tokens':8192}
        return httpx.Response(200,json=response)
    def controller(**kwargs):return create_deepseek_controller(**kwargs,http_transport=httpx.MockTransport(sdk))
    def factory(controller,counter,condition):
        module=original_memory_module();module.SimpleEmbeddingRetriever=Retriever;module.print=lambda *a,**kw:None
        build=make_agent_factory if condition=='full' else make_action_agent_factory
        kw={} if condition=='full' else {'condition':condition}
        return build(ROOT,memory_module=module,controller_factory=lambda observer:controller(observer),token_counter=counter,**kw)
    return {'campaign':campaign,'receipt':receipt,'root':tmp_path,'asset_root':tmp_path/'assets',
            'observer':OfflineObserver(),'verify_observations':observed,'verify_results':experiments,
            'controller_factory':controller,'factory_builder':factory,
            'scorer':AuthorScorer(ROOT,dependencies=dependencies()),
            'token_counter':TokenCounter(str.split,'offline','fixture'),
            '_manifest':manifest,'_sources':sources,'_provider':provider,'_failure_turns':failure_turns}


def execute_fixture(approval,fixture,**overrides):
    kwargs={k:v for k,v in fixture.items() if not k.startswith('_')}
    kwargs.update(overrides)
    return run2.execute_phase(approval,**kwargs)


@pytest.mark.parametrize('short_runner',[(c,1) for c in ('full','neither','linking_only','evolution_only')],indirect=True)
def test_two_successive_output_exhaustions_recover_same_cell_without_extra_calls(short_runner):
    fixture=short_runner;campaign=fixture['campaign'];receipt=fixture['receipt'];root=fixture['root']
    first=execute_fixture(approved_phase(campaign),fixture)
    assert first['status']=='incomplete' and first['recoverable_length_failure'] is True
    assert first['budget']['logical_calls']==first['budget']['physical_attempts']==4
    parent=root/'artifacts/run2/runs'/first['run_id']/'phase.json'
    first_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in parent.parent.iterdir() if p.is_file()}
    condition=campaign['cells'][0]['condition']
    a=run2.plan_phase(campaign,receipt,fixture['asset_root'],root=root,condition=condition,conversation_id='conv-44',parent=parent)
    a.update(approved=True,approved_by='offline test',approved_at='2026-11-03T00:00:00Z')
    second=execute_fixture(a,fixture,observer=OfflineObserver())
    assert second['status']=='incomplete' and second['recoverable_length_failure'] is True
    assert second['budget']['logical_calls']==4
    parent2=root/'artifacts/run2/runs'/second['run_id']/'phase.json'
    second_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in parent2.parent.iterdir() if p.is_file()}
    a2=run2.plan_phase(campaign,receipt,fixture['asset_root'],root=root,condition=condition,conversation_id='conv-44',parent=parent2)
    a2.update(approved=True,approved_by='offline test',approved_at='2026-11-03T00:00:00Z')
    final=execute_fixture(a2,fixture,observer=OfflineObserver())
    turns,questions=run2.CONVERSATIONS['conv-44']
    assert final['status']=='degraded' and final['usable_for_next_phase'] is True
    assert final['completed_questions']==questions==1
    assert final['cell_budget']['logical_calls']==final['cell_budget']['physical_attempts']==2*(turns+questions)
    assert len(fixture['_provider'].requests)==2*(turns+questions)
    assert final['cell_budget']['charged_or_reserved_microusd']==sum(p['budget']['charged_or_reserved_microusd'] for p in (first,second,final))
    assert Decimal(a2['limits']['phase_usd'])==Decimal(5)-Decimal(first['budget']['charged_or_reserved_microusd']+second['budget']['charged_or_reserved_microusd'])/1000000
    assert final['budget']['unknown_attempts']==0
    assert not (root/'artifacts/study-budget.sqlite').exists()
    assert all(hashlib.sha256((parent.parent/name).read_bytes()).hexdigest()==digest for name,digest in first_hashes.items())
    assert all(hashlib.sha256((parent2.parent/name).read_bytes()).hexdigest()==digest for name,digest in second_hashes.items())
    completed=root/'artifacts/run2/runs'/final['run_id']
    events=run2._read_lines(completed/'events.jsonl')
    inherited=[e for e in events if e['type']=='failure' and e.get('inherited_from')]
    old=[e for e in run2._read_lines(parent2.parent/'events.jsonl') if e['type']=='failure']
    assert len(inherited)==len(old)
    assert all(all(child[k]==value for k,value in previous.items() if k not in ('run_id','build_id'))
               for previous,child in zip(old,inherited))


@pytest.mark.parametrize('short_runner',[1,5],indirect=True)
def test_recovered_state_matches_original_uninterrupted_failure_fallbacks(short_runner,tmp_path):
    """Control still receives both rejected responses; nothing is repaired/retried."""
    from amem_repro.adapter import DeepSeekController
    from amem_repro.runner import run_manifest
    from amem_repro.scoring import AuthorScorer
    from test_foundation import Provider
    from test_scoring import dependencies
    fixture=short_runner;campaign=fixture['campaign'];root=fixture['root'];receipt=fixture['receipt']
    phases=[];approval=approved_phase(campaign)
    for n in range(3):
        phase=execute_fixture(approval,fixture,observer=OfflineObserver());phases.append(phase)
        if n<2:
            approval=run2.plan_phase(campaign,receipt,fixture['asset_root'],root=root,condition='full',conversation_id='conv-44',
                                    parent=root/'artifacts/run2/runs'/phase['run_id']/'phase.json')
            approval.update(approved=True,approved_by='offline test',approved_at='2026-11-03T00:00:00Z')
    final_dir=root/'artifacts/run2/runs'/phases[-1]['run_id'];final_events=run2._read_lines(final_dir/'events.jsonl')
    final_build=next(e['build_id'] for e in final_events if e['type']=='build_complete')
    actual=json.loads((root/'artifacts/run2/cache'/final_build/'state.json').read_text())
    requests=fixture['_provider'].requests;responses=[]
    # Reuse the exact transmitted argument outputs/requests in original order.
    for phase in phases:
        responses.extend(e for e in run2._read_lines(root/'artifacts/run2/runs'/phase['run_id']/'events.jsonl')
                         if e['type']=='generation' and e.get('attempts'))
    position=0
    from types import SimpleNamespace as NS
    def control_factory(observer):
        def generate(**kwargs):
            nonlocal position
            wire=copy.deepcopy(kwargs);wire.update(wire.pop('extra_body'))
            assert wire==requests[position]
            response=copy.deepcopy(responses[position]['provider_response']);position+=1
            return response
        return DeepSeekController(NS(chat=NS(completions=NS(create=generate))),observer=observer,
                                  provider_contract_policy='canonical-index-strings-v1',generation_config=RUN2_CONFIG)
    factory=fixture['factory_builder'](control_factory,fixture['token_counter'],'full')
    control=tmp_path/'uninterrupted-original'
    run_manifest(ROOT/'data/locomo10.json',fixture['_manifest'],RUN2_CONFIG,output_dir=control,
                 cache_root=tmp_path/'control-cache',source_hashes=fixture['_sources'],agent_factory=factory,
                 scorer=AuthorScorer(ROOT,dependencies=dependencies()),condition='full',conversation_ids=['conv-44'],
                 provider_contract_policy='canonical-index-strings-v1',run_id='offline-uninterrupted')
    ce=run2._read_lines(control/'events.jsonl');build=next(e['build_id'] for e in ce if e['type']=='build_complete')
    expected=json.loads((tmp_path/'control-cache'/build/'state.json').read_text())
    assert position==len(responses)==len(requests)
    assert memory_view(actual)==memory_view(expected)
    assert actual['evo_cnt']==run2.CONVERSATIONS['conv-44'][0]-2
    if run2.CONVERSATIONS['conv-44'][0]>100:
        assert phases[1]['evolution_counter']==99
        suffix=[e for e in final_events if e['type']=='evolution_outcome']
        assert suffix[0]['counter_before']==99 and suffix[0]['counter_after']==100
    assert [e['result']['prediction'] for e in final_events if e['type']=='question_result']==[e['result']['prediction'] for e in ce if e['type']=='question_result']
    assert [e['result']['metrics'] for e in final_events if e['type']=='question_result']==[e['result']['metrics'] for e in ce if e['type']=='question_result']


def test_length_failure_cannot_hide_a_later_halt_persistence_fault(short_runner,monkeypatch):
    original=run2.Run2Permit.stop
    def faulty(permit,reason):
        original(permit,reason)
        if reason=='run2_phase_aborted':
            raise BudgetStop('offline halt commit uncertainty after the provider failure')
    monkeypatch.setattr(run2.Run2Permit,'stop',faulty)
    try:phase=execute_fixture(approved_phase(short_runner['campaign']),short_runner)
    except BudgetStop:
        phase=json.loads((short_runner['root']/'artifacts/run2/runs/run2-full-conv-44-r0-p0/phase.json').read_text())
    assert phase['status']=='incomplete'
    assert phase['recoverable_length_failure'] is False
    assert phase['secondary_failures']==[{'stage':'phase_halt','error_type':'BudgetStop'}]


def test_original_cell_allocation_cannot_reset_after_a_paid_failure(short_runner):
    fixture=short_runner;campaign=fixture['campaign'];root=fixture['root']
    first=execute_fixture(approved_phase(campaign),fixture)
    parent=root/'artifacts/run2/runs'/first['run_id']/'phase.json'
    child=run2.plan_phase(campaign,fixture['receipt'],fixture['asset_root'],root=root,
                         condition='full',conversation_id='conv-44',parent=parent)
    child.update(approved=True,approved_by='offline test',approved_at='2026-11-03T00:00:00Z')
    child['limits']['phase_usd']='5'
    before=list(fixture['_provider'].requests)
    with pytest.raises(BudgetStop,match='original cell remainder'):
        execute_fixture(child,fixture,observer=OfflineObserver())
    assert fixture['_provider'].requests==before
    assert not (root/'artifacts/run2/runs'/child['run_id']).exists()


def test_unknown_usage_keeps_reservation_and_blocks_new_logical_requests(tmp_path):
    campaign=approved_campaign();permit=run2.Run2Permit(approved_phase(campaign),tmp_path,campaign)
    ident=permit.start_logical('shared_decision')
    attempt=permit.reserve_attempt(ident,{'model':'deepseek-flash','endpoint':'https://api.deepseek.com/beta/chat/completions',
        'max_tokens':8192,'temperature':.7,'thinking':'disabled','stream':False,
        'provider_contract_policy':'canonical-index-strings-v1'})
    permit.settle(attempt,None)
    assert permit.summary()['charged_or_reserved_microusd']==324404
    assert permit.summary()['unknown_attempts']==1
    with pytest.raises(BudgetStop,match='Unknown charge'):
        permit.start_logical('metadata')
    assert permit.summary()['charged_or_reserved_microusd']==324404


@pytest.mark.parametrize('point',['write','commit'])
def test_run2_sdk_settlement_fault_is_terminal_without_regeneration(tmp_path,monkeypatch,point):
    import sqlite3,httpx
    from amem_repro import budget
    from amem_repro.adapter import create_deepseek_controller
    from test_adapter_budget import response
    campaign=approved_campaign();permit=run2.Run2Permit(approved_phase(campaign),tmp_path,campaign)
    connect=sqlite3.connect;armed=False;failed=False
    class Fault(sqlite3.Connection):
        def execute(self,sql,*a,**kw):
            nonlocal armed,failed
            if sql.startswith('UPDATE attempts SET status=') and not failed:
                armed=True
                if point=='write':failed=True;raise sqlite3.OperationalError('offline settlement write failure')
            return super().execute(sql,*a,**kw)
        def commit(self):
            nonlocal failed
            if armed and not failed:
                failed=True;raise sqlite3.OperationalError('offline settlement commit failure')
            return super().commit()
    def faulty(*a,**kw):return connect(*a,**kw,factory=Fault)
    monkeypatch.setattr(budget.sqlite3,'connect',faulty);monkeypatch.setenv('DEEPSEEK_API_KEY','offline-placeholder')
    requests=[];events=[]
    def handler(request):requests.append(request);return httpx.Response(200,json=response())
    c=create_deepseek_controller(paid_authorized=True,http_transport=httpx.MockTransport(handler),
            observer=events.append,phase_permit=permit,generation_config=RUN2_CONFIG,
            provider_contract_policy='canonical-index-strings-v1')
    try:
        with pytest.raises(BudgetStop,match='settlement'):
            c.get_completion('same prompt',load_author_contracts()['answer'])
        assert len(requests)==1 and events[0]['attempts'][0]['response_body']['choices']
        assert permit.summary()['unknown_attempts']==1 and permit.summary()['charged_or_reserved_microusd']==315773
        assert permit.summary()['halted']=='usage_settlement_failed'
        with pytest.raises(BudgetStop):c.get_completion('same prompt',load_author_contracts()['answer'])
        assert len(requests)==1
    finally:c.client.close()


def test_run2_genuine_sdk_retry_policy_is_preserved(tmp_path,monkeypatch):
    import httpx
    from amem_repro.adapter import create_deepseek_controller
    from test_adapter_budget import response
    campaign=approved_campaign();permit=run2.Run2Permit(approved_phase(campaign),tmp_path,campaign)
    monkeypatch.setenv('DEEPSEEK_API_KEY','offline-placeholder');requests=[]
    def handler(request):
        requests.append(request)
        if len(requests)==1:return httpx.Response(429,json={'error':{'message':'offline retry'}},headers={'retry-after-ms':'1'})
        return httpx.Response(200,json=response())
    c=create_deepseek_controller(paid_authorized=True,http_transport=httpx.MockTransport(handler),
            phase_permit=permit,generation_config=RUN2_CONFIG,provider_contract_policy='canonical-index-strings-v1')
    try:assert c.get_completion('same prompt',load_author_contracts()['answer'])=='{"answer":"saved"}'
    finally:c.client.close()
    assert len(requests)==2 and permit.summary()['physical_attempts']==2
    assert permit.summary()['unknown_attempts']==1 # First potentially charged attempt remains reserved.
    with pytest.raises(BudgetStop,match='Unknown charge'):permit.start_logical('metadata')


def test_missing_cloud_delivery_blocks_otherwise_valid_length_recovery(short_runner):
    def missing(*a):return {'verified':False}
    phase=execute_fixture(approved_phase(short_runner['campaign']),short_runner,verify_observations=missing)
    assert phase['status']=='incomplete' and phase['recoverable_length_failure'] is False
    assert phase['observability']['verified'] is False
    assert phase['budget']['physical_attempts']==4


def test_unverified_saved_result_import_keeps_frontier_closed(short_runner):
    fixture=short_runner;fixture['_failure_turns'].clear()
    def missing(*a):return {'verified':False}
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture,verify_results=missing)
    assert phase['completed_questions']==1 and phase['status']=='incomplete'
    assert phase['usable_for_next_phase'] is False
    before=list(fixture['_provider'].requests)
    with pytest.raises(BudgetStop,match='serial'):
        run2.Run2Permit(approved_phase(fixture['campaign'],index=1),fixture['root'],fixture['campaign'])
    assert fixture['_provider'].requests==before


def test_unapproved_or_stale_gates_cannot_prepare_campaign(monkeypatch,tmp_path):
    sources={'offline':'source'}
    monkeypatch.setattr(run2,'_runtime_inputs',lambda *a:(RUN2_CONFIG,{},sources))
    gate_a={'passed':True,'output_policy':'run2-shared-decision-8192-v1','provider_max_output_tokens':393216,
            'sdk_serialization_verified':True,'evidence_sha256':'a'*64}
    with pytest.raises(ValueError,match='GateB'):
        run2.plan_campaign({},gate_a,{'passed':True},root=tmp_path,asset_root=tmp_path/'assets')
    assert not (tmp_path/'artifacts/run2/budget.sqlite').exists()


def test_preclaimed_next_cell_stops_if_prior_completion_becomes_halted(short_runner):
    import sqlite3
    fixture=short_runner;fixture['_failure_turns'].clear();campaign=fixture['campaign']
    first=execute_fixture(approved_phase(campaign),fixture)
    assert first['usable_for_next_phase'] is True
    next_permit=run2.Run2Permit(approved_phase(campaign,index=1),fixture['root'],campaign)
    with sqlite3.connect(next_permit.path) as db:
        db.execute('UPDATE phases SET halted=? WHERE approval_id=?',
                   ('offline post-publication uncertainty','phase-0-0'))
    before=len(fixture['_provider'].requests)
    with pytest.raises(BudgetStop,match='history|completion|frontier'):
        next_permit.start_logical('metadata')
    assert len(fixture['_provider'].requests)==before
    assert next_permit.summary()['halted']


def test_lost_attempt_cannot_publish_a_complete_cell(short_runner):
    import sqlite3
    fixture=short_runner;fixture['_failure_turns'].clear()
    def lose_row(views,context):
        ledger=fixture['root']/'artifacts/run2/budget.sqlite'
        with sqlite3.connect(ledger) as db:db.execute('DELETE FROM attempts WHERE id=(SELECT MAX(id) FROM attempts)')
        return experiments(views,context)
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture,verify_results=lose_row)
    assert phase['status']=='incomplete' and phase['usable_for_next_phase'] is False
    assert phase['recoverable_length_failure'] is False
    assert phase['secondary_failures'][-1]['stage']=='final_publication'


def test_changed_checkpoint_state_rejects_before_another_transmission(short_runner):
    fixture=short_runner;campaign=fixture['campaign'];root=fixture['root']
    phase=execute_fixture(approved_phase(campaign),fixture)
    parent=root/'artifacts/run2/runs'/phase['run_id']/'phase.json'
    path=parent.parent/'partial-memory.json';state=json.loads(path.read_text())
    state['state']['evo_cnt']+=1;path.write_text(json.dumps(state))
    before=len(fixture['_provider'].requests)
    with pytest.raises(ValueError,match='evidence changed'):
        run2.plan_phase(campaign,fixture['receipt'],fixture['asset_root'],root=root,
                         condition='full',conversation_id='conv-44',parent=parent)
    assert len(fixture['_provider'].requests)==before


def test_missing_ledger_with_phase_artifacts_cannot_reset_campaign(short_runner):
    fixture=short_runner;campaign=fixture['campaign'];root=fixture['root']
    execute_fixture(approved_phase(campaign),fixture)
    ledger=root/'artifacts/run2/budget.sqlite';ledger.rename(ledger.with_suffix('.preserved.sqlite'))
    with pytest.raises(BudgetStop,match='ledger is missing'):
        run2.Run2Permit(approved_phase(campaign),root,campaign)
    assert not ledger.exists()


@pytest.mark.parametrize('alias',['file-symlink','directory-symlink','hardlink'])
def test_run2_rejects_symlink_to_original_ledger_before_any_write(tmp_path,alias):
    import sqlite3
    from amem_repro.budget import SCHEMA
    old=tmp_path/'artifacts/study-budget.sqlite';old.parent.mkdir(parents=True)
    with sqlite3.connect(old) as db:
        db.executescript(SCHEMA)
        db.execute('INSERT INTO phases VALUES (?,?,?,?,?,NULL)',('old','old','{}','old-owner',1000000))
    before=old.read_bytes();new=tmp_path/'artifacts/run2/budget.sqlite'
    if alias=='directory-symlink':
        new.parent.symlink_to(old.parent,target_is_directory=True)
    else:
        new.parent.mkdir()
        if alias=='file-symlink':new.symlink_to(old)
        else:new.hardlink_to(old)
    with pytest.raises(BudgetStop):run2.Run2Permit(approved_phase(approved_campaign()),tmp_path,approved_campaign())
    assert old.read_bytes()==before


def test_unmeasured_conditions_forecast_uses_new_run2_full_costs(short_runner):
    fixture=short_runner;fixture['_failure_turns'].clear()
    execute_fixture(approved_phase(fixture['campaign']),fixture)
    forecast=run2.forecast_campaign(fixture['campaign'],root=fixture['root'])
    neither=next(j for j in forecast['remaining_jobs'] if j['condition']=='neither' and j['conversation_id']=='conv-49')
    assert neither['estimated_microusd']==59220 # 1,410 calls × observed42µUSD, not old100µUSD fixture mean.


def test_saved_result_import_cannot_change_local_predictions(short_runner):
    fixture=short_runner;fixture['_failure_turns'].clear()
    def mutate(views,context):
        next(iter(views.values()))['individual_results'][0]['prediction']='changed by exporter'
        return experiments(views,context)
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture,verify_results=mutate)
    assert phase['status']=='incomplete' and phase['usable_for_next_phase'] is False
    saved=json.loads((fixture['root']/'artifacts/run2/runs'/phase['run_id']/'scoring-views.json').read_text())
    assert next(iter(saved.values()))['individual_results'][0]['prediction']!='changed by exporter'


def test_invalid_provider_identity_is_archived_and_stops_without_secondary_type_error(short_runner,monkeypatch):
    fixture=short_runner;provider=fixture['_provider'];original=provider.complete
    def invalid(**request):
        result=original(**request);result['model']={'invalid':'model identifier'};return result
    monkeypatch.setattr(provider,'complete',invalid)
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture)
    assert phase['status']=='incomplete' and phase['recoverable_length_failure'] is False
    assert phase['budget']['physical_attempts']==1 and phase['returned_models']==[]
    assert phase['budget']['halted']=='provider_model_usage_or_fingerprint_changed'


def test_rewritten_checkpoint_and_inventory_cannot_replace_sealed_state(short_runner):
    fixture=short_runner;campaign=fixture['campaign'];root=fixture['root']
    phase=execute_fixture(approved_phase(campaign),fixture)
    parent=root/'artifacts/run2/runs'/phase['run_id']/'phase.json'
    snapshot=parent.parent/'partial-memory.json';value=json.loads(snapshot.read_text())
    value['state']['notes'][0]['attributes']['context']='corrupted earlier note'
    snapshot.write_text(json.dumps(value))
    rewritten=json.loads(parent.read_text());rewritten['artifact_sha256']['partial-memory.json']=hashlib.sha256(snapshot.read_bytes()).hexdigest()
    parent.write_text(json.dumps(rewritten))
    with pytest.raises((ValueError,BudgetStop),match='sealed|receipt|archive'):
        run2.plan_phase(campaign,fixture['receipt'],fixture['asset_root'],root=root,
                         condition='full',conversation_id='conv-44',parent=parent)


@pytest.mark.parametrize('point',['before','after'])
def test_completion_commit_uncertainty_retains_spending_and_blocks_next_cell(short_runner,monkeypatch,point):
    import sqlite3
    from amem_repro import budget
    fixture=short_runner;fixture['_failure_turns'].clear();original=sqlite3.connect;armed=False;failed=False
    class Fault(sqlite3.Connection):
        def execute(self,sql,*a,**kw):
            nonlocal armed
            if sql.startswith('UPDATE run2_cells SET complete=1'):armed=True
            return super().execute(sql,*a,**kw)
        def commit(self):
            nonlocal failed
            if armed and not failed:
                failed=True
                if point=='after':super().commit()
                raise sqlite3.OperationalError('offline completion commit uncertainty')
            return super().commit()
    def connect(*a,**kw):return original(*a,**kw,factory=Fault)
    monkeypatch.setattr(budget.sqlite3,'connect',connect)
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture)
    assert phase['status']=='incomplete' and phase['usable_for_next_phase'] is False
    assert phase['recoverable_length_failure'] is False
    assert phase['budget']['physical_attempts']==2*sum(run2.CONVERSATIONS['conv-44'])
    assert phase['budget']['unknown_attempts']==0 and phase['budget']['charged_or_reserved_microusd']>0
    output=fixture['root']/'artifacts/run2/runs'/phase['run_id']
    assert json.loads((output/'summary.json').read_text())['status']=='incomplete'
    with pytest.raises(BudgetStop):run2.Run2Permit(approved_phase(fixture['campaign'],index=1),fixture['root'],fixture['campaign'])


def test_campaign_observer_wrapper_preserves_real_runner_lifecycle(short_runner):
    fixture=short_runner;fixture['_failure_turns'].clear();observer=OfflineObserver();observer.captures_lifecycle=True
    phase=execute_fixture(approved_phase(fixture['campaign']),fixture,observer=observer)
    assert phase['usable_for_next_phase'] is True
    kinds={e['type'] for e in observer.events}
    assert {'run_start','build_start','memory_turn_start','question_start','question_result','run_complete'} <= kinds
