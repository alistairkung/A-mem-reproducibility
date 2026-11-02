"""T8 execution controls at the phase, permit and frozen-manifest runner seams."""
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import copy

import pytest

from amem_repro.config import load_config
from amem_repro.config import INDEX_STRING_POLICY
from amem_repro.manifests import build_manifest
from amem_repro.runner import run_manifest
from amem_repro.artifacts import CacheStore, CacheRejected
from test_runner import Agent, score
from test_budget import approval, request
from amem_repro.budget import BudgetStop, PhasePermit, ledger_summary
from amem_repro.actions import action_configuration

ROOT = Path(__file__).resolve().parents[1]


def test_runner_partitions_only_whole_frozen_conversations(tmp_path):
    manifest = build_manifest(ROOT/'data/locomo10.json', 'fallback')
    result = run_manifest(ROOT/'data/locomo10.json', manifest, load_config(),
        conversation_ids=['conv-49'], output_dir=tmp_path/'run', cache_root=tmp_path/'cache',
        source_hashes={'test':'partition'}, agent_factory=lambda **kwargs: Agent(), scorer=score)
    events = [json.loads(line) for line in (tmp_path/'run/events.jsonl').read_text().splitlines()]
    assert result['completed_questions']==196
    assert [e['question_id'] for e in events if e['type']=='question_result']==[f'conv-49:qa:{i}' for i in range(196)]
    assert events[0]['conversation_ids']==['conv-49']
    assert events[0]['manifest']==manifest
    for ids in ([], ['conv-26'], ['conv-49','conv-49'], ['conv-44','conv-49']):
        with pytest.raises(ValueError,match='partition'):
            run_manifest(ROOT/'data/locomo10.json', manifest, load_config(), conversation_ids=ids,
                output_dir=tmp_path/'invalid', cache_root=tmp_path/'cache', source_hashes={'test':'bad'},
                agent_factory=lambda **kwargs: pytest.fail('must reject before construction'), scorer=score)


def test_document_text_is_data_but_other_credential_keys_still_rejected(tmp_path):
    agent = Agent(); agent.add_memory('A harmless secret in the frozen conversation')
    from amem_repro.artifacts import snapshot_memory
    state = snapshot_memory(agent.memory_system)
    store = CacheStore(tmp_path)
    identity = {'test':'dynamic-corpus-keys'}
    store.save(identity, state)
    assert store.load(identity)==state
    import copy
    bad=copy.deepcopy(state);bad['notes'][0]['attributes']['api_key']='forbidden'
    with pytest.raises(ValueError,match='credential'):
        store.save({'test':'credentials'},bad)
    with pytest.raises(ValueError,match='credential'):
        store.load({'api_key':'forbidden'})
    for mapping in ({'not a corpus document':0}, {state['retriever']['corpus'][0]:True}):
        bad=copy.deepcopy(state);bad['retriever']['document_ids']=mapping
        with pytest.raises(CacheRejected): store.save({'test':'invalid-map'},bad)


def study_approval(condition='neither', conversation='conv-49', ident='study-one'):
    value=approval('baseline','3',ident,ident)
    calls={'conv-49':1410,'conv-50':1544,'conv-44':1666}[conversation]
    value['binding'].update(population='fallback',condition=condition,repetition=0,
        provider_contract_policy=INDEX_STRING_POLICY,
        conversation_ids=[conversation],memory_actions=action_configuration(condition),
        action_policy='released-action-boundaries-v1',
        action_implementation='frozen-author' if condition=='full' else 't7-action-gates',
        study_budget={'additional_ceiling_microusd':38974201,'cumulative_usable_microusd':42000000,'contingency_microusd':8000000},
        expected_returned_models=['deepseek-flash'],expected_system_fingerprints=['mock-backend'],
        expected_questions={'conv-49':196,'conv-50':204,'conv-44':158}[conversation],
        expected_turns={'conv-49':509,'conv-50':568,'conv-44':675}[conversation],
        study_job={'study_id':'d10a-fallback-once-v1','conversation_id':conversation,
                   'expected_logical_calls':calls,'initial_study_microusd':3025799})
    value['limits'].update(max_logical_calls=calls,max_attempts=3*calls)
    return value


def funded_ledger(path):
    historical=approval('pilot','10','historical','historical')
    historical['pricing']['input_per_million']='3'
    permit=PhasePermit(historical,path,historical['binding'])
    token=permit.reserve_attempt(permit.start_logical('metadata'),request())
    permit.settle(token,{'prompt_tokens':1008599,'completion_tokens':1})
    assert ledger_summary(path)['charged_or_reserved_microusd']==3025799


@pytest.mark.parametrize('condition',['neither','linking_only','evolution_only','full'])
def test_main_permit_binds_actions_and_cannot_reclaim_a_job(tmp_path,condition):
    path=tmp_path/'ledger';funded_ledger(path)
    auth=study_approval(condition)
    if condition!='full':
        with pytest.raises(BudgetStop,match='full-mode'):
            PhasePermit(auth,path,auth['binding'])
        return
    permit=PhasePermit(auth,path,auth['binding'])
    permit.reserve_attempt(permit.start_logical('metadata'),request()|{'provider_contract_policy':INDEX_STRING_POLICY})
    second=study_approval(condition,ident='another-approval')
    with pytest.raises(BudgetStop,match='job|study'):
        PhasePermit(second,path,second['binding'])
    assert ledger_summary(path)['physical_attempts']==2


@pytest.mark.parametrize('change',[{'condition':'other'}, {'memory_actions':{'strengthen':True,'update_neighbor':True}},
    {'repetition':1}, {'conversation_ids':['conv-49','conv-44']}])
def test_main_binding_mismatch_is_rejected_before_ledger_claim(tmp_path,change):
    auth=study_approval();auth['binding'].update(change)
    with pytest.raises(BudgetStop): PhasePermit(auth,tmp_path/'ledger',auth['binding'])
    assert not (tmp_path/'ledger').exists()


def test_main_permit_refuses_an_empty_replacement_study_ledger(tmp_path):
    auth=study_approval()
    with pytest.raises(BudgetStop,match='historical'):
        PhasePermit(auth,tmp_path/'ledger',auth['binding'])


def test_baseline_cannot_bypass_cell_claims_by_omitting_study_job(tmp_path):
    auth=approval('baseline','42')
    with pytest.raises(BudgetStop,match='study job'):
        PhasePermit(auth,tmp_path/'ledger',auth['binding'])
    assert not (tmp_path/'ledger').exists()


def test_baseline_plan_is_unapproved_exact_partition_and_allocation(tmp_path):
    from unittest.mock import patch
    from amem_repro import phases
    auth=study_approval('linking_only','conv-49')
    config=load_config();manifest=build_manifest(ROOT/'data/locomo10.json','fallback')
    with patch.object(phases,'_phase_inputs',return_value=(config,manifest,{'test':'source'},auth['binding'])):
        proposal=phases.plan_phase('baseline',{'assets':{'tokenizer_limitation':'test'}},tmp_path/'assets',
                                  root=tmp_path,condition='linking_only',conversation_id='conv-49',run_id='new-main')
    assert proposal['approved'] is False
    assert proposal['limits']=={'phase_usd':'10','max_logical_calls':1410,'max_attempts':4230}
    assert proposal['population']['questions']==196
    with pytest.raises(BudgetStop): PhasePermit(proposal,tmp_path/'ledger',proposal['binding'])


def test_forged_completion_cannot_release_frontier_or_continue_transmission(tmp_path):
    path=tmp_path/'ledger';funded_ledger(path)
    auth=study_approval('full');permit=PhasePermit(auth,path,auth['binding'])
    forged={'binding':auth['binding'],'run_id':auth['run_id'],'usable_for_next_phase':True,
            'status':'complete','budget':{'unknown_attempts':0,'logical_calls':1410}}
    with pytest.raises(BudgetStop,match='Actual ledger'):
        permit.complete_study_job(forged)
    assert permit.summary()['halted']
    with pytest.raises(BudgetStop): permit.start_logical('metadata')
    second=study_approval('full','conv-44','next-cell')
    with pytest.raises(BudgetStop,match='unfinished'):
        PhasePermit(second,path,second['binding'])


def test_lost_cell_claim_cannot_erase_an_existing_main_authority(tmp_path):
    path=tmp_path/'ledger';funded_ledger(path)
    auth=study_approval('full');PhasePermit(auth,path,auth['binding'])
    with sqlite3.connect(path) as db: db.execute('DELETE FROM study_jobs')
    other=study_approval('full','conv-44','different-cell')
    with pytest.raises(BudgetStop,match='claim/history'):
        PhasePermit(other,path,other['binding'])


@pytest.mark.parametrize('failure',[None,'decision','first_fingerprint','last_fingerprint'])
def test_main_execution_preserves_cells_costs_and_terminal_failures(tmp_path,failure):
    import httpx
    from unittest.mock import patch
    from amem_repro import phases
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.author import make_agent_factory
    from amem_repro.measurements import TokenCounter
    from amem_repro.scoring import AuthorScorer
    from test_foundation import Provider, original_memory_module
    from test_scoring import dependencies
    from amem_repro.adapter import AdapterError
    (tmp_path/'data').symlink_to(ROOT/'data',target_is_directory=True)
    auth=study_approval('full');manifest=build_manifest(ROOT/'data/locomo10.json','fallback')
    funded_ledger(tmp_path/'artifacts/study-budget.sqlite')
    provider=Provider()
    def handler(request):
        response=provider.complete(**json.loads(request.content))
        function=response['choices'][0]['message']['tool_calls'][0]['function']
        value=json.loads(function['arguments'])
        if 'suggested_connections' in value:
            value['suggested_connections']=[str(i) for i in value['suggested_connections']]
            function['arguments']=json.dumps(value)
        if failure=='decision' and len(provider.requests)==6:
            function['arguments']='{"malformed":['
        if ((failure=='first_fingerprint' and len(provider.requests)==1)
                or (failure=='last_fingerprint' and len(provider.requests)==1410)):
            response['system_fingerprint']='changed-provider'
        return httpx.Response(200,json=response)
    def controller(**kwargs):
        return create_deepseek_controller(**kwargs,http_transport=httpx.MockTransport(handler))
    def factory(root,**kwargs):
        module=original_memory_module();module.print=lambda *a,**k:None
        return make_agent_factory(ROOT,memory_module=module,**kwargs)
    with patch.object(phases,'_phase_inputs',return_value=(load_config(),manifest,{'test':'source'},auth['binding'])), \
         patch('amem_repro.adapter.create_deepseek_controller',side_effect=controller), \
         patch('amem_repro.author.make_agent_factory',side_effect=factory), \
         patch.object(phases,'make_token_counter',return_value=TokenCounter(str.split,'offline','test')), \
         patch('amem_repro.scoring.AuthorScorer',side_effect=lambda root:AuthorScorer(ROOT,dependencies=dependencies())), \
         patch.dict('os.environ',{'DEEPSEEK_API_KEY':'offline-placeholder'}):
        if failure is None:
            result=phases.execute_phase(auth,{'assets':{}},tmp_path/'assets',root=tmp_path)
        else:
            with pytest.raises((BudgetStop,AdapterError)):
                phases.execute_phase(auth,{'assets':{}},tmp_path/'assets',root=tmp_path)
            result=json.loads((tmp_path/'artifacts/runs/study-one/phase.json').read_text())
        count=len(provider.requests)
        with pytest.raises(FileExistsError):
            phases.execute_phase(auth,{'assets':{}},tmp_path/'assets',root=tmp_path)
        assert len(provider.requests)==count
    events=[json.loads(line) for line in (tmp_path/'artifacts/runs/study-one/events.jsonl').read_text().splitlines()]
    assert result['conversation_ids']==['conv-49'] and result['expected_questions']==196
    assert result['budget']['physical_attempts']=={None:1410,'decision':6,'first_fingerprint':1,'last_fingerprint':1410}[failure]
    assert result['status']==('degraded' if failure is None else 'incomplete')
    assert result['usable_for_next_phase'] is (failure is None)
    assert result['budget']['unknown_attempts']==0
    if failure=='decision':
        partial=json.loads((tmp_path/'artifacts/runs/study-one/partial-memory.json').read_text())
        assert len(partial['state']['notes'])==3 and partial['state']['evo_cnt']==2
        assert any(e.get('kind')=='provider_contract_deviation' for e in events)
        assert any(e.get('kind')=='evolve' for e in events)
    if failure=='last_fingerprint':
        assert result['completed_questions']==196
        assert json.loads((tmp_path/'artifacts/runs/study-one/summary.json').read_text())['status']=='incomplete'
    next_auth=study_approval('full','conv-44','next-cell')
    if failure:
        with pytest.raises(BudgetStop):
            PhasePermit(next_auth,tmp_path/'artifacts/study-budget.sqlite',next_auth['binding'])
    else:
        PhasePermit(next_auth,tmp_path/'artifacts/study-budget.sqlite',next_auth['binding'])


@pytest.fixture
def saved_history(tmp_path):
    """Read-only historical evidence; skip in clones without private study archives."""
    shared=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=ROOT,text=True).strip())
    if not shared.is_absolute(): shared=ROOT/shared
    main=shared.resolve().parent
    original=main/'artifacts/checkpoint-child-ledger-after.sqlite'
    if not original.exists(): pytest.skip('Preserved private T5/T7 evidence is not present in this clone')
    (tmp_path/'artifacts').mkdir()
    for name in ('runs','replays','cache'):
        (tmp_path/'artifacts'/name).symlink_to(main/'artifacts'/name,target_is_directory=True)
    shutil.copy2(original,tmp_path/'artifacts/study-budget.sqlite')
    for name in ('data','config','manifests'):
        (tmp_path/name).symlink_to(ROOT/name,target_is_directory=True)
    from amem_repro.config import source_fingerprint
    return tmp_path,source_fingerprint(ROOT)


def test_original_history_and_scientific_migration_are_verified(saved_history):
    from amem_repro.study import verify_study_history
    root,sources=saved_history
    verify_study_history(root,sources)
    bad=copy.deepcopy(sources);bad['files']['amem_repro/actions.py']='0'*64
    with pytest.raises(ValueError,match='scientific'):
        verify_study_history(root,bad)


@pytest.mark.parametrize('corruption',['usage','missing_prefix_masked_by_later_spend'])
def test_original_usage_and_prefix_cannot_be_replaced_or_masked(saved_history,corruption):
    from amem_repro.study import verify_study_history
    root,sources=saved_history
    with sqlite3.connect(root/'artifacts/study-budget.sqlite') as db:
        if corruption=='usage':
            raw=db.execute('SELECT usage_json FROM attempts WHERE id=593').fetchone()[0]
            usage=json.loads(raw);usage['total_tokens']+=1
            db.execute('UPDATE attempts SET usage_json=? WHERE id=593',(json.dumps(usage),))
        else:
            row=db.execute('SELECT logical_id,approval_id,request_sha256,status,charge,reservation,usage_json FROM attempts WHERE id=593').fetchone()
            db.execute('DELETE FROM attempts WHERE id=593')
            db.execute('INSERT INTO attempts VALUES (9999,?,?,?,?,?,?,?)',row)
    with pytest.raises(ValueError,match='attempt/usage/charge|prefix'):
        verify_study_history(root,sources)


def test_old_ledger_snapshot_cannot_hide_an_archived_failed_main_run(saved_history):
    from amem_repro.study import verify_study_history
    root,sources=saved_history
    runs=root/'artifacts/runs'
    original=runs.resolve();runs.unlink();shutil.copytree(original,runs)
    failed=runs/'old-failed-main';failed.mkdir()
    (failed/'approval.json').write_text(json.dumps(study_approval('full')))
    with pytest.raises(ValueError,match='Archived main run missing'):
        verify_study_history(root,sources)


def test_balanced_cost_forecast_blocks_overspend_before_paid_approval(saved_history):
    from unittest.mock import patch
    from amem_repro import phases
    root,sources=saved_history
    extra=approval('pilot','10','other-incurred-cost','other-incurred-cost')
    extra['pricing']['input_per_million']='9'
    permit=PhasePermit(extra,root/'artifacts/study-budget.sqlite',extra['binding'])
    token=permit.reserve_attempt(permit.start_logical('metadata'),request())
    permit.settle(token,{'prompt_tokens':900000,'completion_tokens':1})
    with patch.object(phases,'_verified_receipt',return_value=sources):
        with pytest.raises(ValueError,match='Balanced approved study'):
            phases.plan_phase('baseline',{'assets':{'tokenizer_limitation':'offline fixture'}},root/'unused-assets',
                             root=root,condition='full',conversation_id='conv-49',provider_contract_policy=INDEX_STRING_POLICY)
