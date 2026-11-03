"""Only the approved conv44 root → first child → second child lineage."""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

import numpy as np
import pytest

from amem_repro import checkpoint, phases
from amem_repro.artifacts import restore_memory, snapshot_memory
from amem_repro.budget import PhasePermit, BudgetStop, ledger_summary, study_job_claim
from amem_repro.config import fingerprint
from test_study_checkpoint import study_parent, verified, child_approval, link_inputs, input_patches, ROOT
from test_checkpoint import author_module

pytestmark=pytest.mark.parametrize('study_parent',['conv-44'],indirect=True)


@pytest.fixture
def second_parent(study_parent,monkeypatch):
    original=study_parent
    first=child_approval(original)
    first.update(run_id='t8-full-conv44-checkpoint-child',approval_id='middle44')
    identity=copy.deepcopy(json.loads((original.path.parent/'partial-memory.json').read_text())['identity'])
    identity['checkpoint']=first['binding']['checkpoint']
    state=copy.deepcopy(original.state)
    state['evo_cnt']=607
    conv=next(c for c in original.manifest['conversations'] if c['original_id']=='conv-44')
    events=[dict(original.events[0],run_id=first['run_id'])]
    failures=[]
    for index,f in enumerate(e for e in original.events if e['type']=='failure'):
        inherited={**f,'run_id':first['run_id'],'inherited_from':'checkpoint',
                   'origin_run_id':f['run_id'],'origin_failure_index':index,'from_cache':True}
        events.append(inherited);failures.append(inherited)
    for i in range(186):
        number=424+i
        state['notes'].append({'key':f'n{number}','index':number,'attributes':{'id':f'n{number}',
            'content':f'content-{number}','context':'evolved','keywords':['kw'],'tags':['tag'],'links':[],'timestamp':'fixed'}})
        outcome={'turn_id':conv['turn_ids'][number],'counter_before':422+i,'counter_after':min(423+i,607),
                 'proposed_decision':None if i==185 else {'should_evolve':True},'changed_existing_note_ids':[],
                 'enabled_actions':['strengthen','update_neighbor'],'suppressed_actions':[]}
        state['outcomes'].append(outcome)
        for stage in ('metadata','shared_decision'):
            usage={'prompt_tokens':20,'completion_tokens':15,'total_tokens':35}
            event={'type':'generation','run_id':first['run_id'],'stage':stage,'attempts':[{'usage':usage}],
                   'error_type':None,'usage':usage}
            if i==185 and stage=='shared_decision':
                usage={'prompt_tokens':20,'completion_tokens':4000,'total_tokens':4020}
                event.update(error_type='AdapterError',output=None,max_tokens=4000,usage=usage,
                    attempts=[{'usage':usage}],provider_response={'choices':[{'finish_reason':'length'}], 'usage':usage})
            events.append(event)
        events.append({'type':'evolution_outcome','run_id':first['run_id'],**outcome})
    state['retriever']={'corpus':[f'stale-{i}' for i in range(610)],
        'document_ids':{f'stale-{i}':i for i in range(610)},'embedding_dtype':'float32',
        'embeddings':np.eye(610,384,dtype=np.float32).tolist()}
    for f in ({'kind':'evolve'}, {'kind':'provider_contract_deviation','compatibility_deviation':{
        'transformations':[{'path':'$.suggested_connections[1]','original':'1','validation_copy':1}]}}):
        notice={'type':'failure','run_id':first['run_id'],**f};events.append(notice);failures.append(notice)
    with sqlite3.connect(original.ledger) as db:
        db.execute('INSERT INTO phases VALUES (?,?,?,?,?,?)',(first['approval_id'],first['run_id'],json.dumps(first),
            'middle-owner',3000000,'provider_contract_or_transport_failure'))
        db.execute('UPDATE study_jobs SET approval_id=? WHERE approval_id=?',(first['approval_id'],original.auth['approval_id']))
        db.execute('INSERT INTO checkpoint_claims VALUES (?,?)',(fingerprint(original.phase),first['approval_id']))
        db.execute('INSERT INTO study_recovery_edges VALUES (?,?,?,?,?)',(original.auth['approval_id'],first['approval_id'],
            'd10a-fallback-once-v1','full','conv-44'))
        seq=db.execute('SELECT MAX(id) FROM attempts').fetchone()[0]
        for e in (e for e in events if e['type']=='generation'):
            seq+=1;e['attempts'][0]['budget_attempt_id']=seq;u=e['usage']
            db.execute('INSERT INTO logical_calls VALUES (?,?,?)',(seq,first['approval_id'],e['stage']))
            charge=4806 if u['completion_tokens']==4000 else 24
            db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',(seq,seq,first['approval_id'],'test','settled',charge,319373,json.dumps(u)))
    directory=original.root/'artifacts/runs'/first['run_id'];directory.mkdir()
    for name,value in {'approval.json':first,'preflight.json':original.receipt,'checkpoint.json':first['binding']['checkpoint'],
        'run.json':{'run_id':first['run_id'],'expected_question_ids':[q['question_id'] for q in conv['questions']]},
        'summary.json':{'run_id':first['run_id'],'status':'incomplete','expected_questions':158,'completed_questions':0,'failures':failures},
        'partial-memory.json':{'complete':False,'identity':identity,'state':state}}.items():phases._save(directory/name,value)
    (directory/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    phase={'phase':'baseline','run_id':first['run_id'],'status':'incomplete','usable_for_next_phase':False,'completed_questions':0,
        'expected_questions':158,'conversation_ids':['conv-44'],'binding':first['binding'],
        'budget':ledger_summary(original.ledger,first['approval_id']),'study_budget':ledger_summary(original.ledger),
        'returned_models':['deepseek-flash'],'system_fingerprints':['bc19ba97cbe016479903222bb1578db6'],
        'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}}
    phases._save(directory/'phase.json',phase)
    monkeypatch.setattr(checkpoint,'CONV44_FIRST_CHILD_SHA256',fingerprint(phase),raising=False)
    return NS(**{**vars(original),'original':original,'path':directory/'phase.json','phase':phase,'state':state,
                 'auth':first,'events':events})


def test_second_conv44_restore_keeps_both_failed_decisions_and_stale_index(second_parent):
    checked=verified(second_parent)
    assert checked['lineage']['policy']=='blk013-conv44-second-checkpoint-v1'
    assert checked['lineage']['completed_turns']==610 and checked['lineage']['remaining_logical_calls']==446
    assert checked['lineage']['parent_checkpoint']==second_parent.auth['binding']['checkpoint']
    system=NS(memories={},retriever=NS());m=author_module()
    restore_memory(system,checked['state'],note_type=m.MemoryNote)
    assert snapshot_memory(system,checked['state']['outcomes'])==second_parent.state
    assert system.evo_cnt==607 and system.retriever.embeddings.shape==(610,384)
    assert system.retriever.embeddings.tobytes()==np.asarray(second_parent.state['retriever']['embeddings'],dtype=np.float32).tobytes()
    assert checked['state']['outcomes'][423]['turn_id']=='D18:21'
    assert checked['state']['outcomes'][609]['turn_id']=='D26:18'
    assert checked['state']['outcomes'][423]['proposed_decision'] is None
    assert checked['state']['outcomes'][609]['proposed_decision'] is None


def grandchild_approval(parent):
    value=copy.deepcopy(parent.auth);value.update(approval_id='grand44',run_id='grand44')
    value['binding']['checkpoint']=verified(parent)['lineage']
    value['limits']={'phase_usd':'3','max_logical_calls':446,'max_attempts':1338}
    return value


def test_second_conv44_one_shot_claim_retains_entire_accounting_chain(second_parent):
    auth=grandchild_approval(second_parent);before=ledger_summary(second_parent.ledger)
    permit=PhasePermit(auth,second_parent.ledger,auth['binding'])
    assert ledger_summary(second_parent.ledger)==before
    with sqlite3.connect(second_parent.ledger) as db:
        for ident in (second_parent.original.auth['approval_id'],second_parent.auth['approval_id'],'grand44'):
            assert study_job_claim(db,ident)==('d10a-fallback-once-v1','full','conv-44',0)
        assert db.execute('SELECT approval_id FROM study_jobs').fetchall()==[('grand44',)]
    with pytest.raises(BudgetStop):PhasePermit(auth,second_parent.ledger,auth['binding'])
    another=copy.deepcopy(auth);another.update(approval_id='another-grand',run_id='another-grand')
    with pytest.raises(BudgetStop):PhasePermit(another,second_parent.ledger,another['binding'])
    permit.stop('offline stopped')
    with pytest.raises(BudgetStop):permit.start_logical('metadata')


def test_second_plan_is_unapproved_and_has_only_the_65_turn_suffix(second_parent):
    link_inputs(second_parent);before=second_parent.ledger.read_bytes()
    with input_patches(second_parent),patch.object(phases,'_verified_receipt',return_value=second_parent.sources):
        plan=phases.plan_phase('baseline',second_parent.receipt,second_parent.root/'assets',root=second_parent.root,
            condition='full',conversation_id='conv-44',checkpoint=second_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id='grand44')
    assert plan['approved'] is False
    assert plan['limits']=={'phase_usd':'3','max_logical_calls':446,'max_attempts':1338}
    assert plan['population']=={'conversations':1,'turns':65,'questions':158}
    assert plan['binding']['expected_turns']==675
    assert plan['binding']['checkpoint']==verified(second_parent)['lineage']
    assert second_parent.ledger.read_bytes()==before


@pytest.mark.parametrize('mode',['success','negative','memory_failure','late_question_failure','postprocessing_failure'])
def test_second_child_replays_exact_suffix_and_keeps_original_origins(second_parent,monkeypatch,mode):
    import httpx
    from amem_repro.adapter import create_deepseek_controller,AdapterError
    from amem_repro.author import make_agent_factory
    from amem_repro.artifacts import CacheStore,CacheRejected
    from amem_repro.measurements import TokenCounter
    from amem_repro.scoring import AuthorScorer
    from test_foundation import Provider
    from test_scoring import dependencies
    link_inputs(second_parent)
    provider=Provider();decisions=0;answers=0;agents=[]
    original_bytes=np.asarray(second_parent.state['retriever']['embeddings'],dtype=np.float32).tobytes()
    original_corpus=list(second_parent.state['retriever']['corpus'])
    def handler(request):
        nonlocal decisions,answers
        body=json.loads(request.content);response=provider.complete(**body)
        fields=body['tools'][0]['function']['parameters']['properties']
        if len(provider.requests)==1:
            assert snapshot_memory(agents[0].memory_system,second_parent.state['outcomes'])==second_parent.state
        system=agents[0].memory_system
        assert system.retriever.embeddings[:610].tobytes()==original_bytes
        assert system.retriever.corpus[:610]==original_corpus
        decisions+=int('should_evolve' in fields);answers+=int('answer' in fields)
        function=response['choices'][0]['message']['tool_calls'][0]['function']
        if (mode=='memory_failure' and decisions==1 and 'should_evolve' in fields) or (mode=='late_question_failure' and answers==158 and 'answer' in fields):
            function['arguments']='{"unfinished":'
        if mode=='negative' and decisions==1 and 'should_evolve' in fields:
            value=json.loads(function['arguments']);value['should_evolve']=False;function['arguments']=json.dumps(value)
        response['system_fingerprint']='bc19ba97cbe016479903222bb1578db6'
        return httpx.Response(200,json=response)
    def controller(**kwargs):return create_deepseek_controller(**kwargs,http_transport=httpx.MockTransport(handler))
    def factory(root,**kwargs):
        base=make_agent_factory(ROOT,memory_module=author_module(),**kwargs)
        def construct(**args):
            agent=base(**args);agents.append(agent);return agent
        return construct
    def execute():
        from amem_repro.scoring import rescore_records
        def rescore(*a,**kw):
            if mode=='postprocessing_failure':raise RuntimeError('offline postprocessing failure')
            return rescore_records(*a,**kw)
        with patch('amem_repro.scoring.rescore_records',side_effect=rescore):
            return phases.execute_phase(plan,second_parent.receipt,second_parent.root/'assets',root=second_parent.root,checkpoint=second_parent.path)
    with input_patches(second_parent),patch.object(phases,'_verified_receipt',return_value=second_parent.sources),\
         patch('amem_repro.adapter.create_deepseek_controller',side_effect=controller),\
         patch('amem_repro.author.make_agent_factory',side_effect=factory),\
         patch.object(phases,'make_token_counter',return_value=TokenCounter(str.split,'offline','test')),\
         patch('amem_repro.scoring.AuthorScorer',side_effect=lambda root:AuthorScorer(ROOT,dependencies=dependencies())),\
         patch.dict('os.environ',{'DEEPSEEK_API_KEY':'offline-placeholder'}):
        plan=phases.plan_phase('baseline',second_parent.receipt,second_parent.root/'assets',root=second_parent.root,
            condition='full',conversation_id='conv-44',checkpoint=second_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id='grand44')
        plan.update(approval_id='grand44',approved=True,approved_by='offline only',approved_at='2026-11-03T00:00:00Z')
        if mode.endswith('failure'):
            with pytest.raises((BudgetStop,AdapterError,RuntimeError)):execute()
        else:execute()
    directory=second_parent.root/'artifacts/runs/grand44';phase=json.loads((directory/'phase.json').read_text())
    events=[json.loads(s) for s in (directory/'events.jsonl').read_text().splitlines()]
    inherited=[e for e in events if e['type']=='failure' and e.get('inherited_from')=='checkpoint']
    assert len(inherited)==4
    assert [(e['origin_run_id'],e['origin_failure_index']) for e in inherited]==[
        (second_parent.original.auth['run_id'],0),(second_parent.original.auth['run_id'],1),
        (second_parent.auth['run_id'],2),(second_parent.auth['run_id'],3)]
    assert phase['inherited_provider_contract_deviation_count']==2
    assert phase['inherited_validation_copy_transformed_item_count']==2
    assert json.loads(second_parent.original.path.read_text())==second_parent.original.phase
    assert json.loads(second_parent.path.read_text())==second_parent.phase
    with pytest.raises(BudgetStop):PhasePermit(plan,second_parent.ledger,plan['binding'])
    repeat=copy.deepcopy(plan);repeat.update(run_id='repeat-grand44',approval_id='repeat-grand44')
    with pytest.raises(BudgetStop):PhasePermit(repeat,second_parent.ledger,repeat['binding'])
    with input_patches(second_parent),patch.object(phases,'_verified_receipt',return_value=second_parent.sources):
        with pytest.raises(ValueError,match='pinned study checkpoint parents'):
            phases.plan_phase('baseline',second_parent.receipt,second_parent.root/'assets',root=second_parent.root,
                condition='full',conversation_id='conv-44',checkpoint=directory/'phase.json',
                provider_contract_policy='canonical-index-strings-v1')
    if mode.endswith('failure'):
        assert phase['status']=='incomplete' and phase['usable_for_next_phase'] is False
        assert phase['completed_questions']=={'memory_failure':0,'late_question_failure':157,'postprocessing_failure':158}[mode]
        assert len(provider.requests)==(2 if mode=='memory_failure' else 446)
        return
    assert phase['status']=='degraded' and phase['usable_for_next_phase'] is True
    assert phase['budget']['logical_calls']==phase['budget']['physical_attempts']==446
    assert phase['completed_questions']==158 and len(provider.requests)==446
    outcomes=[e for e in events if e['type']=='evolution_outcome']
    conv=next(c for c in second_parent.manifest['conversations'] if c['original_id']=='conv-44')
    assert [e['turn_id'] for e in outcomes]==conv['turn_ids'][610:]
    assert outcomes[0]['turn_id']=='D26:19' and outcomes[0]['counter_before']==607
    assert outcomes[-1]['counter_after']==672-int(mode=='negative')
    assert [e['question_id'] for e in events if e['type']=='question_result']==[f'conv-44:qa:{i}' for i in range(158)]
    identity=json.loads(next((second_parent.root/'artifacts/cache').glob('*/identity.json')).read_text())
    saved=CacheStore(second_parent.root/'artifacts/cache').load(identity)
    assert len(saved['notes'])==675 and saved['outcomes'][:610]==second_parent.state['outcomes']
    assert np.asarray(saved['retriever']['embeddings'],dtype=np.float32)[:610].tobytes()==original_bytes
    assert saved['retriever']['corpus'][:610]==original_corpus
    assert saved['evo_cnt']==672-int(mode=='negative')
    from amem_repro.actions import action_configuration
    store=CacheStore(second_parent.root/'artifacts/cache')
    for condition in ('neither','linking_only','evolution_only'):
        other=copy.deepcopy(identity);other['condition']=condition;other['memory_actions']=action_configuration(condition)
        assert store.path_for(other)!=store.path_for(identity)
        with pytest.raises(CacheRejected):store.load(other)
    old_identity=json.loads((second_parent.path.parent/'partial-memory.json').read_text())['identity']
    assert store.path_for(old_identity)!=store.path_for(identity)
    with sqlite3.connect(second_parent.ledger) as db:
        for ancestor in (second_parent.original.auth['approval_id'],second_parent.auth['approval_id']):
            assert study_job_claim(db,ancestor)==('d10a-fallback-once-v1','full','conv-44',0)
        assert study_job_claim(db,'grand44')==('d10a-fallback-once-v1','full','conv-44',1)
    from amem_repro.comparison import load_saved_run,assemble_comparison
    loaded=load_saved_run(directory/'phase.json',second_parent.manifest,root=ROOT,archive_root=second_parent.root)
    assert set(loaded['sources'])=={second_parent.original.auth['run_id'],second_parent.auth['run_id'],'grand44'}
    assert loaded['telemetry']['generation_stages']['metadata']['logical_calls']==675
    assert loaded['telemetry']['generation_stages']['shared_decision']['logical_calls']==675
    comp=assemble_comparison(second_parent.manifest,[directory/'phase.json'],root=ROOT,archive_root=second_parent.root)
    assert comp['cost']['charged_or_reserved_microusd']==42618
    assert comp['cost']['logical_calls']==comp['cost']['physical_attempts']==1666
    for name in ('pilot-conv50-d9a','pilot-conv50-checkpoint-child'):
        p=second_parent.root/'artifacts/runs'/name;p.mkdir();(p/'approval.json').write_text(json.dumps({'approval_id':'grand44'}))
    from amem_repro.study import balanced_cost_forecast
    forecast=balanced_cost_forecast(second_parent.root,second_parent.manifest)
    estimate=next(r for r in forecast['remaining_jobs'] if r['condition']=='full' and r['conversation_id']=='conv-49')
    assert estimate['estimated_microusd']==38594


@pytest.mark.parametrize('damage',[
    {'phase_usd':'3.000001'},{'max_logical_calls':445},{'max_logical_calls':447},{'max_attempts':1339},
])
def test_second_recovery_limits_reject_unapproved_capacity(second_parent,damage):
    auth=grandchild_approval(second_parent);auth['limits'].update(damage)
    before=second_parent.ledger.read_bytes()
    with pytest.raises(BudgetStop):PhasePermit(auth,second_parent.ledger,auth['binding'])
    assert second_parent.ledger.read_bytes()==before


@pytest.mark.parametrize('field,value',[
    ('policy','blk013-conv44-checkpoint-v1'),('parent_phase_sha256','0'*64),
    ('parent_run_id','grand44'),('completed_turns',609),('remaining_logical_calls',447),
    ('parent_checkpoint',{}),
])
def test_second_recovery_requires_exact_parent_and_root_binding(second_parent,field,value):
    auth=grandchild_approval(second_parent);auth['binding']['checkpoint'][field]=value
    before=second_parent.ledger.read_bytes()
    with pytest.raises(BudgetStop):PhasePermit(auth,second_parent.ledger,auth['binding'])
    assert second_parent.ledger.read_bytes()==before


@pytest.mark.parametrize('damage',['root_artifact','middle_artifact','root_receipt','middle_receipt',
    'source','assets','manifest','root_charge','middle_charge','unknown'])
def test_second_verifier_rejects_damage_in_either_ancestor(second_parent,damage):
    if damage=='root_artifact':(second_parent.original.path.parent/'partial-memory.json').write_text('{}')
    elif damage=='middle_artifact':(second_parent.path.parent/'partial-memory.json').write_text('{}')
    elif damage in ('root_receipt','middle_receipt'):
        p=second_parent.original.path if damage=='root_receipt' else second_parent.path
        value=json.loads(p.read_text());value['status']='complete';p.write_text(json.dumps(value))
    elif damage=='source':
        second_parent.sources=copy.deepcopy(second_parent.sources);second_parent.sources['files']['memory_layer.py']='changed'
    elif damage=='assets':second_parent.receipt={'assets':{'wrong':True}}
    elif damage=='manifest':
        second_parent.manifest=copy.deepcopy(second_parent.manifest)
        conv=next(c for c in second_parent.manifest['conversations'] if c['original_id']=='conv-44');conv['turn_ids'][610]='D26:18'
    else:
        with sqlite3.connect(second_parent.ledger) as db:
            aid=second_parent.original.auth['approval_id'] if damage=='root_charge' else second_parent.auth['approval_id']
            ident=db.execute('SELECT MIN(id) FROM attempts WHERE approval_id=?',(aid,)).fetchone()[0]
            if damage=='unknown':db.execute("UPDATE attempts SET status='unknown' WHERE id=?",(ident,))
            else:
                db.execute('UPDATE attempts SET charge=charge-1 WHERE id=?',(ident,))
                db.execute('UPDATE attempts SET charge=charge+1 WHERE id=?',(ident+1,))
    with pytest.raises(ValueError):verified(second_parent)


@pytest.mark.parametrize('damage',['missing_root_edge','missing_middle_edge','cycle','extra_edge','wrong_cell','missing_claim'])
def test_broken_two_hop_ownership_halts_before_another_logical_call(second_parent,damage):
    auth=grandchild_approval(second_parent);permit=PhasePermit(auth,second_parent.ledger,auth['binding'])
    with sqlite3.connect(second_parent.ledger) as db:
        if damage=='missing_root_edge':db.execute('DELETE FROM study_recovery_edges WHERE parent_approval_id=?',(second_parent.original.auth['approval_id'],))
        elif damage=='missing_middle_edge':db.execute('DELETE FROM study_recovery_edges WHERE parent_approval_id=?',(second_parent.auth['approval_id'],))
        elif damage=='cycle':db.execute('UPDATE study_recovery_edges SET child_approval_id=? WHERE parent_approval_id=?',(second_parent.original.auth['approval_id'],second_parent.auth['approval_id']))
        elif damage=='extra_edge':db.execute('INSERT INTO study_recovery_edges VALUES (?,?,?,?,?)',('forged','fork','d10a-fallback-once-v1','full','conv-44'))
        elif damage=='wrong_cell':db.execute("UPDATE study_recovery_edges SET conversation_id='conv-49' WHERE parent_approval_id=?",(second_parent.auth['approval_id'],))
        else:db.execute('DELETE FROM checkpoint_claims WHERE approval_id=?',(second_parent.auth['approval_id'],))
    calls=ledger_summary(second_parent.ledger)['logical_calls']
    with pytest.raises(BudgetStop):permit.start_logical('metadata')
    assert ledger_summary(second_parent.ledger)['logical_calls']==calls
    assert permit.summary()['halted']


def test_second_migration_records_support_changes_without_note_field_shadowing(second_parent):
    sources=copy.deepcopy(second_parent.sources);sources['files']['amem_repro/runner.py']='reviewed-new-support'
    checked=checkpoint.verify_study_checkpoint(second_parent.path,second_parent.root,second_parent.manifest,
        second_parent.config,sources,second_parent.receipt)
    assert checked['lineage']['migrated_files']==['amem_repro/runner.py']


def test_second_lineage_copy_does_not_mutate_its_verified_parent(second_parent):
    checked=verified(second_parent);before=copy.deepcopy(checked['phase'])
    checked['lineage']['parent_checkpoint']['completed_turns']=0
    assert checked['phase']==before


def test_cross_cell_incoming_edge_into_root_blocks_leaf_transmission(second_parent):
    auth=grandchild_approval(second_parent);permit=PhasePermit(auth,second_parent.ledger,auth['binding'])
    with sqlite3.connect(second_parent.ledger) as db:
        db.execute('INSERT INTO study_recovery_edges VALUES (?,?,?,?,?)',('foreign-owner',
            second_parent.original.auth['approval_id'],'other-study','full','conv-49'))
    with pytest.raises(BudgetStop):permit.start_logical('metadata')
