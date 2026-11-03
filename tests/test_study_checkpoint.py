"""Two explicit study-parent recoveries at existing checkpoint/phase/permit/import seams."""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

import numpy as np
import pytest

from amem_repro import phases, checkpoint
from amem_repro.artifacts import restore_memory, snapshot_memory,CacheRejected
from amem_repro.budget import SCHEMA, BudgetStop, PhasePermit, ledger_summary
from amem_repro.config import load_config, fingerprint, source_fingerprint
from amem_repro.manifests import build_manifest
from test_study import study_approval, funded_ledger
from test_checkpoint import author_module

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def study_parent(tmp_path, monkeypatch, request):
    manifest=build_manifest(ROOT/'data/locomo10.json','fallback')
    conversation=getattr(request,'param','conv-49')
    count,counter,questions,parent_name,pin_name={
        'conv-49':(413,411,196,'t8-full-conv49-r0-20261102','STUDY_PARENT_SHA256'),
        'conv-44':(424,422,158,'t8-full-conv44-r0-20261103','CONV44_PARENT_SHA256'),
    }[conversation]
    conv=next(c for c in manifest['conversations'] if c['original_id']==conversation)
    config=load_config(); sources=source_fingerprint(ROOT)
    receipt={'assets':{'tokenizer_limitation':'offline'},'runtime':{'ok':True,'network_disabled':True},
             'source_sha256':fingerprint(sources)}
    auth=study_approval('full',conversation,ident=parent_name)
    auth['binding']['expected_system_fingerprints']=['bc19ba97cbe016479903222bb1578db6']
    auth['binding'].update(manifest_sha256=fingerprint(manifest),config_sha256=fingerprint(config),
        source_sha256=fingerprint(sources),preflight_sha256=fingerprint(receipt))
    state={'notes':[],'outcomes':[],'evo_cnt':counter,'evo_threshold':100,
           'retriever':{'corpus':[f'stale-{i}' for i in range(count)],
            'document_ids':{f'stale-{i}':i for i in range(count)},
            'embedding_dtype':'float32','embeddings':np.eye(count,384,dtype=np.float32).tolist()}}
    ident=auth['run_id']
    events=[{'type':'run_start','run_id':ident,'manifest':manifest,'configuration':config,
             'source_hashes':sources,'condition':'full','repetition':0,'provider_contract_policy':'canonical-index-strings-v1',
             'memory_actions':auth['binding']['memory_actions']}]
    usage={'prompt_tokens':20,'completion_tokens':5,'total_tokens':25}
    for i in range(count):
        state['notes'].append({'key':f'n{i}','index':i,'attributes':{'id':f'n{i}','content':f'content-{i}',
            'context':'evolved','keywords':['kw'],'tags':['tag'],'links':[1,1] if i==0 else [],'timestamp':'fixed'}})
        outcome={'turn_id':conv['turn_ids'][i],'counter_before':max(0,i-1),'counter_after':min(i,counter),
            'proposed_decision':None if i==count-1 else {'should_evolve':i>0},'changed_existing_note_ids':[],
            'enabled_actions':['strengthen','update_neighbor'],'suppressed_actions':[]}
        state['outcomes'].append(outcome)
        for stage in ('metadata','shared_decision'):
            event={'type':'generation','run_id':ident,'stage':stage,'attempts':[{'usage':usage}],'error_type':None}
            if i==count-1 and stage=='shared_decision':
                event.update(error_type='AdapterError',output=None,max_tokens=4000,
                    provider_response={'choices':[{'finish_reason':'length','message':{'tool_calls':[{'function':{'arguments':'{"new_tags_neighborhood":[["'}}]}}], 'usage':{'completion_tokens':4000}})
            events.append(event)
        events.append({'type':'evolution_outcome','run_id':ident,**outcome})
    failures=[{'type':'failure','run_id':ident,'kind':'evolve'},
              {'type':'failure','run_id':ident,'kind':'provider_contract_deviation',
               'compatibility_deviation':{'transformations':[{'path':'$.suggested_connections[0]','original':'0','validation_copy':0}]}}]
    events.extend(failures)
    ledger=tmp_path/'artifacts/study-budget.sqlite';ledger.parent.mkdir(parents=True)
    funded_ledger(ledger)
    with sqlite3.connect(ledger) as db:
        db.execute('INSERT INTO phases VALUES (?,?,?,?,?,?)',(auth['approval_id'],ident,json.dumps(auth),'old',10000000,'provider_contract_or_transport_failure'))
        db.execute('INSERT INTO study_jobs VALUES (?,?,?,?,0)',('d10a-fallback-once-v1','full',conversation,auth['approval_id']))
        for i,event in enumerate(e for e in events if e['type']=='generation'):
            seq=i+2;event['attempts'][0]['budget_attempt_id']=seq
            db.execute('INSERT INTO logical_calls VALUES (?,?,?)',(seq,auth['approval_id'],event['stage']))
            db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',(seq,seq,auth['approval_id'],'test','settled',12,319373,json.dumps(usage)))
    identity={'configuration':config,'source_hashes':sources,'conversation':conv,'dataset_sha256':manifest['dataset_sha256'],
              'condition':'full','repetition':0,'provider_contract_policy':'canonical-index-strings-v1'}
    directory=tmp_path/'artifacts/runs'/ident;directory.mkdir(parents=True)
    for name,value in {'approval.json':auth,'preflight.json':receipt,'run.json':{'run_id':ident,'expected_question_ids':[q['question_id'] for q in conv['questions']]},
        'summary.json':{'run_id':ident,'status':'incomplete','expected_questions':questions,'completed_questions':0,'failures':failures},
        'partial-memory.json':{'complete':False,'identity':identity,'state':state}}.items():phases._save(directory/name,value)
    (directory/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    phase={'phase':'baseline','run_id':ident,'status':'incomplete','usable_for_next_phase':False,'completed_questions':0,
        'expected_questions':questions,'conversation_ids':[conversation],'binding':auth['binding'],'budget':{'charged_or_reserved_microusd':count*2*12,'logical_calls':count*2,'physical_attempts':count*2,'unknown_attempts':0},
        'study_budget':ledger_summary(ledger),'returned_models':['deepseek-flash'],'system_fingerprints':['bc19ba97cbe016479903222bb1578db6'],
        'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}}
    phases._save(directory/'phase.json',phase)
    monkeypatch.setattr(checkpoint,pin_name,fingerprint(phase),raising=False)
    return NS(root=tmp_path,path=directory/'phase.json',manifest=manifest,config=config,sources=sources,receipt=receipt,
              auth=auth,phase=phase,state=state,ledger=ledger,events=events)


def verified(parent):
    return checkpoint.verify_study_checkpoint(parent.path,parent.root,parent.manifest,parent.config,parent.sources,parent.receipt)


def test_exact_conv49_snapshot_restores_without_encoding(study_parent):
    checked=verified(study_parent)
    assert checked['lineage']['completed_turns']==413
    assert checked['lineage']['remaining_logical_calls']==584
    assert checked['lineage']['policy']=='blk013-conv49-checkpoint-v1'
    m=author_module();system=NS(memories={},retriever=NS())
    restore_memory(system,checked['state'],note_type=m.MemoryNote)
    assert snapshot_memory(system,checked['state']['outcomes'])==study_parent.state
    assert system.evo_cnt==411
    assert system.retriever.embeddings.tobytes()==np.asarray(study_parent.state['retriever']['embeddings'],dtype=np.float32).tobytes()
    assert checked['state']['outcomes'][-1]['turn_id']=='D22:2'
    assert study_parent.manifest['conversations'][0]['turn_ids'][413]=='D22:3'


def child_approval(parent):
    auth=copy.deepcopy(parent.auth)
    auth.update(approval_id='child49',run_id='child49')
    auth['binding']['checkpoint']=verified(parent)['lineage']
    calls=auth['binding']['checkpoint']['remaining_logical_calls']
    auth['limits'].update(max_logical_calls=calls,max_attempts=3*calls)
    return auth


def test_conv49_recovery_claim_is_one_shot_and_keeps_serial_hold(study_parent):
    auth=child_approval(study_parent)
    before=ledger_summary(study_parent.ledger)
    permit=PhasePermit(auth,study_parent.ledger,auth['binding'])
    assert permit.summary()['logical_calls']==0
    assert ledger_summary(study_parent.ledger)==before
    with sqlite3.connect(study_parent.ledger) as db:
        assert db.execute('SELECT halted FROM phases WHERE approval_id=?',(study_parent.auth['approval_id'],)).fetchone()[0]
    other=study_approval('full','conv-44','next-cell')
    with pytest.raises(BudgetStop,match='unfinished'):
        PhasePermit(other,study_parent.ledger,other['binding'])
    another=copy.deepcopy(auth);another.update(run_id='another',approval_id='another')
    with pytest.raises(BudgetStop,match='claimed|unfinished'):
        PhasePermit(another,study_parent.ledger,another['binding'])
    permit.stop('offline interrupted child')
    with pytest.raises(BudgetStop):permit.start_logical('metadata')
    with pytest.raises(BudgetStop,match='unfinished'):
        PhasePermit(other,study_parent.ledger,other['binding'])


def input_patches(parent):
    conv50=next(c for c in parent.manifest['conversations'] if c['original_id']=='conv-50')
    child={'provider_contract_policy':'canonical-index-strings-v1','returned_models':['deepseek-flash'],
           'system_fingerprints':['bc19ba97cbe016479903222bb1578db6']}
    start={'manifest':{'conversations':[conv50]},'configuration':parent.config}
    return patch.multiple('amem_repro.study',verify_study_history=lambda *a:(child,start,[]),
                          balanced_cost_forecast=lambda *a:{'fits_ceiling':True})


def link_inputs(parent):
    for name in ('data','config','manifests'):
        if not (parent.root/name).exists():(parent.root/name).symlink_to(ROOT/name,target_is_directory=True)


def test_conv49_phase_plan_is_unapproved_exact_remaining_workload(study_parent):
    link_inputs(study_parent)
    with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources):
        proposal=phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
            condition='full',conversation_id='conv-49',checkpoint=study_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id='child49')
    assert proposal['approved'] is False
    assert proposal['limits']=={'phase_usd':'10','max_logical_calls':584,'max_attempts':1752}
    assert proposal['population']['turns']==96
    assert proposal['population']['questions']==196
    assert proposal['binding']['expected_turns']==509
    assert proposal['binding']['checkpoint']==verified(study_parent)['lineage']
    with pytest.raises(BudgetStop,match='approval'):
        PhasePermit(proposal,study_parent.ledger,proposal['binding'])


@pytest.mark.parametrize('study_parent',['conv-49','conv-44'],indirect=True)
@pytest.mark.parametrize('mode',['success','negative','memory_failure','late_question_failure','postprocessing_failure'])
def test_pinned_child_completes_exact_suffix_and_releases_one_cell(study_parent,monkeypatch,mode):
    import httpx
    from amem_repro.adapter import create_deepseek_controller,AdapterError
    from amem_repro.author import make_agent_factory
    from amem_repro.artifacts import CacheStore
    from amem_repro.measurements import TokenCounter
    from amem_repro.scoring import AuthorScorer
    from test_foundation import Provider
    from test_scoring import dependencies
    conversation=study_parent.phase['conversation_ids'][0]
    count,counter,total,questions,calls,child_name,boundaries={
        'conv-49':(413,411,509,196,584,'child49',[(500,88)]),
        'conv-44':(424,422,675,158,818,'child44',[(500,77),(600,177)]),
    }[conversation]
    selected=next(c for c in study_parent.manifest['conversations'] if c['original_id']==conversation)
    link_inputs(study_parent)
    provider=Provider();decisions=0;answers=0;agents=[];observed_boundaries=[]
    def handler(request):
        nonlocal decisions,answers
        body=json.loads(request.content);response=provider.complete(**body)
        fields=body['tools'][0]['function']['parameters']['properties']
        if 'context' in fields:
            system=agents[0].memory_system
            if len(provider.requests)==1:
                assert snapshot_memory(system,study_parent.state['outcomes'])==study_parent.state
            if system.evo_cnt in (500,600):
                expected=[n.content+' , '+f"{n.context} {' '.join(n.keywords)} {' '.join(n.tags)}" for n in system.memories.values()]
                assert system.retriever.corpus==expected
                observed_boundaries.append((system.evo_cnt,len(system.memories)))
        decisions+=int('should_evolve' in fields);answers+=int('answer' in fields)
        function=response['choices'][0]['message']['tool_calls'][0]['function']
        if (mode=='memory_failure' and decisions==1 and 'should_evolve' in fields) or (mode=='late_question_failure' and answers==questions and 'answer' in fields):
            function['arguments']='{"unfinished":'
        if mode=='negative' and decisions==1 and 'should_evolve' in fields:
            value=json.loads(function['arguments']);value['should_evolve']=False;function['arguments']=json.dumps(value)
        response['system_fingerprint']='bc19ba97cbe016479903222bb1578db6'
        return httpx.Response(200,json=response)
    def controller(**kwargs):
        return create_deepseek_controller(**kwargs,http_transport=httpx.MockTransport(handler))
    def factory(root,**kwargs):
        base=make_agent_factory(ROOT,memory_module=author_module(),**kwargs)
        def construct(**args):
            agent=base(**args);agents.append(agent);return agent
        return construct
    with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources),\
         patch('amem_repro.adapter.create_deepseek_controller',side_effect=controller),\
         patch('amem_repro.author.make_agent_factory',side_effect=factory),\
         patch.object(phases,'make_token_counter',return_value=TokenCounter(str.split,'offline','test')),\
         patch('amem_repro.scoring.AuthorScorer',side_effect=lambda root:AuthorScorer(ROOT,dependencies=dependencies())),\
         patch.dict('os.environ',{'DEEPSEEK_API_KEY':'offline-placeholder'}):
        proposal=phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
            condition='full',conversation_id=conversation,checkpoint=study_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id=child_name)
        proposal.update(approved=True,approved_by='offline only',approved_at='2026-11-03T00:00:00Z')
        if mode.endswith('failure'):
            from amem_repro.scoring import rescore_records
            def rescore(*args,**kwargs):
                if mode=='postprocessing_failure':raise RuntimeError('offline postprocessing failure')
                return rescore_records(*args,**kwargs)
            with patch('amem_repro.scoring.rescore_records',side_effect=rescore),pytest.raises((BudgetStop,RuntimeError,AdapterError)):
                phases.execute_phase(proposal,study_parent.receipt,study_parent.root/'assets',root=study_parent.root,checkpoint=study_parent.path)
            child=study_parent.root/'artifacts/runs'/child_name
            result=json.loads((child/'phase.json').read_text())
            assert result['status']=='incomplete' and result['usable_for_next_phase'] is False
            assert result['inherited_provider_contract_deviation_count']==1
            assert result['inherited_validation_copy_transformed_item_count']==1
            events=[json.loads(line) for line in (child/'events.jsonl').read_text().splitlines()]
            assert any(e.get('origin_run_id')==study_parent.auth['run_id'] and e.get('kind')=='evolve' for e in events)
            assert json.loads(study_parent.path.read_text())==study_parent.phase
            other=study_approval('full','conv-44','next-cell')
            with pytest.raises(BudgetStop,match='unfinished'):PhasePermit(other,study_parent.ledger,other['binding'])
            assert len(provider.requests)==(2 if mode=='memory_failure' else calls)
            assert result['completed_questions']=={'memory_failure':0,'late_question_failure':questions-1,'postprocessing_failure':questions}[mode]
            return
        result=phases.execute_phase(proposal,study_parent.receipt,study_parent.root/'assets',root=study_parent.root,checkpoint=study_parent.path)
    assert result['status']=='degraded' and result['usable_for_next_phase'] is True
    assert result['budget']['logical_calls']==calls and result['completed_questions']==questions
    assert result['inherited_provider_contract_deviation_count']==1
    assert result['inherited_validation_copy_transformed_item_count']==1
    child=study_parent.root/'artifacts/runs'/child_name
    events=[json.loads(line) for line in (child/'events.jsonl').read_text().splitlines()]
    outcomes=[e for e in events if e['type']=='evolution_outcome']
    assert [e['turn_id'] for e in outcomes]==selected['turn_ids'][count:]
    assert outcomes[0]['counter_before']==counter and outcomes[-1]['counter_after']==counter+total-count-int(mode=='negative')
    for threshold,offset in boundaries:
        assert next(i for i,e in enumerate(outcomes) if e['counter_after']==threshold)==offset+int(mode=='negative')
        assert (threshold,count+offset+1+int(mode=='negative')) in observed_boundaries
    assert [e['question_id'] for e in events if e['type']=='question_result']==[f'{conversation}:qa:{i}' for i in range(questions)]
    assert len(provider.requests)==calls
    saved_id=next((study_parent.root/'artifacts/cache').glob('*/identity.json'))
    saved=CacheStore(study_parent.root/'artifacts/cache').load(json.loads(saved_id.read_text()))
    assert len(saved['notes'])==total and saved['outcomes'][:count]==study_parent.state['outcomes']
    assert [n['key'] for n in saved['notes'][:count]]==[n['key'] for n in study_parent.state['notes']]
    assert json.loads(study_parent.path.read_text())==study_parent.phase
    assert verified(study_parent)['lineage']==proposal['binding']['checkpoint']
    with pytest.raises(BudgetStop):PhasePermit(proposal,study_parent.ledger,proposal['binding'])
    second=copy.deepcopy(proposal);second.update(run_id='another-child',approval_id='another-child')
    with pytest.raises(BudgetStop,match='Checkpoint already claimed'):
        PhasePermit(second,study_parent.ledger,second['binding'])
    identity=json.loads(saved_id.read_text())
    assert identity['condition']=='full' and identity['checkpoint']==proposal['binding']['checkpoint']
    store=CacheStore(study_parent.root/'artifacts/cache')
    from amem_repro.actions import action_configuration
    for condition in ('neither','linking_only','evolution_only'):
        isolated=copy.deepcopy(identity);isolated['condition']=condition
        isolated['memory_actions']=action_configuration(condition)
        assert store.path_for(isolated)!=store.path_for(identity)
        with pytest.raises(CacheRejected):store.load(isolated)
    next_auth=study_approval('full','conv-44','next-cell')
    if conversation=='conv-49':
        PhasePermit(next_auth,study_parent.ledger,next_auth['binding'])
    else:
        blocked=study_approval('neither','conv-49','blocked-ablation')
        with pytest.raises(BudgetStop,match='full-mode'):PhasePermit(blocked,study_parent.ledger,blocked['binding'])
    from amem_repro.comparison import load_saved_run,assemble_comparison
    loaded=load_saved_run(child/'phase.json',study_parent.manifest,root=ROOT,archive_root=study_parent.root)
    assert set(loaded['sources'])=={study_parent.auth['run_id'],child_name}
    assert loaded['telemetry']['generation_stages']['metadata']['logical_calls']==total
    assert loaded['telemetry']['generation_stages']['shared_decision']['logical_calls']==total
    comparison=assemble_comparison(study_parent.manifest,[child/'phase.json'],root=ROOT,archive_root=study_parent.root)
    assert comparison['status']=='incomplete'
    assert len(comparison['source_costs'])==2
    assert comparison['cost']['charged_or_reserved_microusd']==2*count*12+calls*42
    assert comparison['cost']['physical_attempts']==2*count+calls
    # Cheap 413-call prefixes must not disappear from cost means after recovery.
    for name in ('pilot-conv50-d9a','pilot-conv50-checkpoint-child'):
        path=study_parent.root/'artifacts/runs'/name;path.mkdir()
        (path/'approval.json').write_text(json.dumps({'approval_id':child_name}))
    from amem_repro.study import balanced_cost_forecast
    forecast=balanced_cost_forecast(study_parent.root,study_parent.manifest)
    target='conv-44' if conversation=='conv-49' else 'conv-49'
    estimated=next(r for r in forecast['remaining_jobs'] if r['condition']=='full' and r['conversation_id']==target)
    assert estimated['estimated_microusd']==(37111 if conversation=='conv-49' else 40037)
    # Means include cheap retained prefixes, not just the more expensive suffix.


@pytest.mark.parametrize('damage',['charge_redistribution','logical_reassignment','lost_cell_claim'])
def test_checkpoint_rejects_corrupted_accounting_or_claim_history(study_parent,damage):
    with sqlite3.connect(study_parent.ledger) as db:
        if damage=='charge_redistribution':
            db.execute('UPDATE attempts SET charge=11 WHERE id=2');db.execute('UPDATE attempts SET charge=13 WHERE id=3')
        elif damage=='logical_reassignment':db.execute('UPDATE attempts SET logical_id=2 WHERE id=3')
        else:db.execute('DELETE FROM study_jobs')
    with pytest.raises(ValueError,match='accounting|claim'):
        verified(study_parent)


@pytest.mark.parametrize('damage',['artifact','scientific_source','assets','manifest','unknown_charge','missing_history'])
def test_conv49_parent_provenance_and_unknown_cost_rejected(study_parent,damage):
    if damage=='artifact':(study_parent.path.parent/'partial-memory.json').write_text('{}')
    elif damage=='scientific_source':
        study_parent.sources=copy.deepcopy(study_parent.sources)
        study_parent.sources['files']['amem_repro/adapter.py']='changed'
    elif damage=='assets':study_parent.receipt={'assets':{'different':True}}
    elif damage=='manifest':
        study_parent.manifest=copy.deepcopy(study_parent.manifest)
        study_parent.manifest['conversations'][0]['turn_ids'][413]='D22:4'
    else:
        with sqlite3.connect(study_parent.ledger) as db:
            if damage=='unknown_charge':db.execute("UPDATE attempts SET status='unknown' WHERE id=2")
            else:db.execute('DELETE FROM attempts WHERE id=1')
    with pytest.raises((ValueError,sqlite3.OperationalError)):
        verified(study_parent)


@pytest.mark.parametrize('field,value',[('completed_turns',412),('remaining_logical_calls',585),
    ('parent_phase_sha256','0'*64),('policy','blk014-checkpoint-v1')])
def test_conv49_permit_cannot_change_pinned_recovery_workload(study_parent,field,value):
    auth=child_approval(study_parent);auth['binding']['checkpoint'][field]=value
    with pytest.raises(BudgetStop):PhasePermit(auth,study_parent.ledger,auth['binding'])
    assert ledger_summary(study_parent.ledger)['physical_attempts']==827


@pytest.mark.parametrize('missing',['edge','parent_authority','exclusive_claim'])
def test_lost_recovery_edge_halts_child_and_prevents_new_main_cell(study_parent,missing):
    auth=child_approval(study_parent);permit=PhasePermit(auth,study_parent.ledger,auth['binding'])
    with sqlite3.connect(study_parent.ledger) as db:
        if missing=='edge':db.execute('DELETE FROM study_recovery_edges')
        elif missing=='exclusive_claim':db.execute('DELETE FROM checkpoint_claims')
        else:db.execute('DELETE FROM phases WHERE approval_id=?',(study_parent.auth['approval_id'],))
    with pytest.raises(BudgetStop,match='ownership|history'):permit.start_logical('metadata')
    other=study_approval('full','conv-44','next-cell')
    with pytest.raises(BudgetStop):PhasePermit(other,study_parent.ledger,other['binding'])


def test_conv49_checkpoint_cannot_seed_an_ablation_or_another_conversation(study_parent):
    link_inputs(study_parent)
    for condition,conversation in (('neither','conv-49'),('full','conv-44')):
        with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources),pytest.raises(ValueError,match='checkpoint|Checkpoint'):
            phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
                condition=condition,conversation_id=conversation,checkpoint=study_parent.path,
                provider_contract_policy='canonical-index-strings-v1')



def test_planning_against_pre_recovery_schema_never_migrates_the_ledger(study_parent):
    with sqlite3.connect(study_parent.ledger) as db:db.execute('DROP TABLE study_recovery_edges')
    before=study_parent.ledger.read_bytes()
    assert verified(study_parent)['lineage']['remaining_logical_calls']==584
    link_inputs(study_parent)
    with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources):
        plan=phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
            condition='full',conversation_id='conv-49',checkpoint=study_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id='child49')
    assert plan['approved'] is False
    assert study_parent.ledger.read_bytes()==before
    with pytest.raises(BudgetStop,match='approval'):PhasePermit(plan,study_parent.ledger,plan['binding'])
    assert study_parent.ledger.read_bytes()==before
