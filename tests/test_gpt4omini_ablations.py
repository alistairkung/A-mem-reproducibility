"""Native conv-49 executor: four isolated builds and same-condition recovery."""
import json
from collections import Counter

import pytest

from amem_repro.actions import action_configuration
from amem_repro.budget import BudgetStop
from amem_repro.gpt4omini_campaign import checkpoint_from, read
from amem_repro.manifests import expand_manifest
from amem_repro.openrouter import (ABLATION_CONDITIONS, cell_key, cell_store,
                                  CampaignLedger, SCIENTIFIC_BINDING)
from gpt4omini_executor_fixture import run_actual_phase, seed_predecessors
from gpt4omini_fixture import ROOT


@pytest.mark.parametrize('condition', ('full', *ABLATION_CONDITIONS))
@pytest.mark.parametrize('conversation,turns,questions', [('conv-49',509,196),('conv-50',568,204),('conv-44',675,158)])
def test_complete_native_coverage_and_isolated_actions(tmp_path, condition, conversation, turns, questions):
    result=run_actual_phase(tmp_path,root=ROOT,conversation=conversation,condition=condition)
    receipt=result['receipt']
    assert (receipt['status'],receipt['notes'],receipt['questions'],receipt['evolution_counter'])==('complete',turns,questions,turns)
    output=cell_store(tmp_path,cell_key(conversation,condition))/'runs/p0'
    state=read(output/'final-memory.json')
    events=[json.loads(line) for line in (output/'events.jsonl').read_text().splitlines()]
    manifest=expand_manifest(ROOT/'data/locomo10.json',read(ROOT/'manifests/fallback.json'))
    selected=next(c for c in manifest['conversations'] if c['original_id']==conversation)
    assert [o['turn_id'] for o in state['outcomes']]==selected['turn_ids']
    views=read(output/'scoring-views.json')
    for view in views.values():
        assert [r['question_id'] for r in view['individual_results']]==[q['question_id'] for q in selected['questions']]
    assert len(result['requests'])==2*(turns+questions)
    stage_counts=Counter(e['stage'] for e in events if e['type']=='generation')
    assert stage_counts=={'metadata':turns,'shared_decision':turns,'query_keywords':questions,'answer':questions}
    attributes=[n['attributes'] for n in state['notes']]
    flags=action_configuration(condition)
    assert any(n['links'] for n in attributes)==flags['strengthen']
    assert any(n['context']=='updated' for n in attributes)==flags['update_neighbor']
    if condition=='neither':assert all(n['tags']==['tag'] for n in attributes)
    if condition=='linking_only':assert all(n['tags']==['linked'] for n in attributes)
    if condition=='evolution_only':assert attributes[-1]['tags']==['tag']
    actions=Counter(e['action'] for e in events if e['type']=='local_action')
    assert actions=={k:turns for k,v in flags.items() if v}
    cache=read(output/'cache-proof.json')
    identity=read(tmp_path/cache['directory']/'identity.json')
    assert identity['condition']==condition and identity['memory_actions']==flags
    with pytest.raises(BudgetStop):
        result['ledger'].claim({**result['approval'],'phase':'repeat'})


@pytest.mark.parametrize('condition', ABLATION_CONDITIONS)
@pytest.mark.parametrize('conversation', ('conv-49','conv-50','conv-44'))
def test_native_ablations_restore_twice_and_retain_author_fallback(tmp_path, condition, conversation):
    prior=None;ledger=None
    for sequence in range(3):
        result=run_actual_phase(tmp_path,root=ROOT,conversation=conversation,condition=condition,
            phase=f'p{sequence}',ledger=ledger,parent=prior,fail_decisions={1:'malformed',2:'length'})
        prior=result['receipt'];ledger=result['ledger']
        assert prior['recoverable_length_failure'] and prior['notes']==2*(sequence+1)
        assert prior['evolution_counter']==0 and prior['questions']==0
    assert ledger.totals()['attempts']==12
    path=cell_store(tmp_path,cell_key(conversation,condition))/'runs/p2/phase.json'
    checkpoint=checkpoint_from(path,ledger,prior['binding'],root=ROOT)
    assert checkpoint['lineage']['condition']==condition
    assert len(checkpoint['state']['outcomes'])==6
    with pytest.raises(BudgetStop):
        checkpoint_from(path,ledger,{**prior['binding'],'condition':'full'},root=ROOT)


def test_ablation_cap_and_predecessor_history_are_condition_specific(tmp_path):
    binding={**SCIENTIFIC_BINDING,'condition':'evolution_only','conversation_id':'conv-49'}
    ledger=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=binding)
    seal=seed_predecessors(ledger,'evolution_only-conv-49')
    from amem_repro.openrouter import ABLATION_POLICY
    auth={'approved':True,'binding':binding,'kind':'baseline','phase':'test',
          'condition':'evolution_only','conversation':'conv-49','ablation_policy':ABLATION_POLICY,
          'previous_acceptance_sha256':seal}
    for change in ({'condition':'neither'},{'conversation':'conv-44'},{'ablation_policy':None}):
        with pytest.raises(BudgetStop):ledger.claim({**auth,**change})
    ledger.claim(auth)
    with ledger.transaction() as db:
        db.execute("INSERT INTO attempts(phase,stage,request_hash,reservation,charge,state) VALUES ('test','metadata','synthetic',4999000,4999000,'settled')")
    with pytest.raises(BudgetStop):ledger.reserve('test','metadata',{'max_tokens':1000})


def test_ablation_namespace_cannot_alias_full(tmp_path):
    full=cell_store(tmp_path,'conv-49');full.mkdir(parents=True)
    (tmp_path/'cells/evolution_only-conv-49').symlink_to(full)
    with pytest.raises(BudgetStop):cell_store(tmp_path,'evolution_only-conv-49')


@pytest.mark.parametrize('condition', ('full', *ABLATION_CONDITIONS))
def test_author_cleanup_parseable_decision_is_terminal_not_fallback(tmp_path, condition):
    result=run_actual_phase(tmp_path,root=ROOT,conversation='conv-49',condition=condition,
                            fail_decisions={1:'cleanup_parseable',2:'length'})
    receipt=result['receipt']
    assert receipt['status']=='incomplete' and not receipt['recoverable_length_failure']
    assert len(result['requests'])==2 and receipt['notes']==0
    output=cell_store(tmp_path,cell_key('conv-49',condition))/'runs/p0'
    events=[json.loads(line) for line in (output/'events.jsonl').read_text().splitlines()]
    assert not any(e.get('kind')=='original_evolution_fallback' for e in events)
    raw=next(e['output'] for e in events if e['type']=='generation' and e['stage']=='shared_decision')
    assert json.loads(raw.strip())['should_evolve'] is True
    with pytest.raises(json.JSONDecodeError):json.loads(raw)
