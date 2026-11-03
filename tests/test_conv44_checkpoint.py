"""Second pinned parent: conv-44 recovery, with no new scientific policy."""
import copy
import json
import sqlite3
from types import SimpleNamespace as NS

import numpy as np
import pytest

from amem_repro import phases
from amem_repro.artifacts import restore_memory,snapshot_memory
from amem_repro.budget import PhasePermit,BudgetStop,ledger_summary
from test_study_checkpoint import study_parent,verified,child_approval,input_patches,link_inputs
from test_checkpoint import author_module

pytestmark=pytest.mark.parametrize('study_parent',['conv-44'],indirect=True)


def test_conv44_restores_exact_failed_prefix_and_stale_index(study_parent):
    checked=verified(study_parent)
    assert checked['lineage']['completed_turns']==424
    assert checked['lineage']['remaining_logical_calls']==818
    assert checked['lineage']['policy']=='blk013-conv44-checkpoint-v1'
    assert checked['state']['outcomes'][-1]['turn_id']=='D18:21'
    conv=next(c for c in study_parent.manifest['conversations'] if c['original_id']=='conv-44')
    assert conv['turn_ids'][424]=='D18:22'
    m=author_module();system=NS(memories={},retriever=NS())
    restore_memory(system,checked['state'],note_type=m.MemoryNote)
    assert snapshot_memory(system,checked['state']['outcomes'])==study_parent.state
    assert system.evo_cnt==422
    assert system.retriever.embeddings.shape==(424,384)
    assert system.retriever.embeddings.tobytes()==np.asarray(study_parent.state['retriever']['embeddings'],dtype=np.float32).tobytes()


def test_conv44_permit_claim_is_bounded_and_cannot_restart(study_parent):
    auth=child_approval(study_parent)
    before=ledger_summary(study_parent.ledger)
    permit=PhasePermit(auth,study_parent.ledger,auth['binding'])
    assert auth['limits']['max_logical_calls']==818 and auth['limits']['max_attempts']==2454
    assert ledger_summary(study_parent.ledger)==before
    with pytest.raises(BudgetStop):PhasePermit(auth,study_parent.ledger,auth['binding'])
    second=copy.deepcopy(auth);second.update(run_id='second-child44',approval_id='second-child44')
    with pytest.raises(BudgetStop):PhasePermit(second,study_parent.ledger,second['binding'])
    from test_study import study_approval
    ablation=study_approval('neither','conv-49','blocked-ablation')
    with pytest.raises(BudgetStop):PhasePermit(ablation,study_parent.ledger,ablation['binding'])
    permit.stop('offline interrupted child')
    with pytest.raises(BudgetStop):permit.start_logical('metadata')


def test_conv44_plan_is_unapproved_and_exactly_usd3_818_calls(study_parent):
    from unittest.mock import patch
    link_inputs(study_parent)
    before=study_parent.ledger.read_bytes()
    with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources):
        proposal=phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
            condition='full',conversation_id='conv-44',checkpoint=study_parent.path,
            provider_contract_policy='canonical-index-strings-v1',run_id='child44')
    assert proposal['approved'] is False
    assert proposal['limits']=={'phase_usd':'3','max_logical_calls':818,'max_attempts':2454}
    assert proposal['population']=={'conversations':1,'turns':251,'questions':158}
    assert proposal['binding']['expected_turns']==675
    assert proposal['binding']['checkpoint']==verified(study_parent)['lineage']
    with pytest.raises(BudgetStop,match='approval'):PhasePermit(proposal,study_parent.ledger,proposal['binding'])
    assert study_parent.ledger.read_bytes()==before


@pytest.mark.parametrize('change',[
    {'phase_usd':'3.000001'},{'phase_usd':10},
    {'max_logical_calls':819},{'max_logical_calls':817},{'max_attempts':2455},
])
def test_conv44_recovery_limits_cannot_exceed_exact_authority(study_parent,change):
    auth=child_approval(study_parent);auth['limits'].update(change)
    before=study_parent.ledger.read_bytes()
    with pytest.raises(BudgetStop):PhasePermit(auth,study_parent.ledger,auth['binding'])
    assert study_parent.ledger.read_bytes()==before


@pytest.mark.parametrize('damage',['artifact','rehash_parent','scientific_source','manifest','unknown','charge','claim'])
def test_conv44_parent_integrity_and_cost_tampering_are_rejected(study_parent,damage):
    from hashlib import sha256
    path=study_parent.path.parent/'partial-memory.json'
    if damage=='artifact':path.write_text('{}')
    elif damage=='rehash_parent':
        value=json.loads(path.read_text());value['state']['notes'][0]['attributes']['context']='repair'
        path.write_text(json.dumps(value))
        phase=copy.deepcopy(study_parent.phase)
        phase['artifact_sha256']['partial-memory.json']=sha256(path.read_bytes()).hexdigest()
        study_parent.path.write_text(json.dumps(phase))
    elif damage=='scientific_source':
        study_parent.sources=copy.deepcopy(study_parent.sources)
        study_parent.sources['files']['amem_repro/adapter.py']='changed'
    elif damage=='manifest':
        study_parent.manifest=copy.deepcopy(study_parent.manifest)
        conv=next(c for c in study_parent.manifest['conversations'] if c['original_id']=='conv-44')
        conv['turn_ids'][424]='D18:21'
    else:
        with sqlite3.connect(study_parent.ledger) as db:
            if damage=='unknown':db.execute("UPDATE attempts SET status='unknown' WHERE id=2")
            elif damage=='claim':db.execute('DELETE FROM study_jobs')
            else:
                db.execute('UPDATE attempts SET charge=11 WHERE id=2')
                db.execute('UPDATE attempts SET charge=13 WHERE id=3')
    with pytest.raises(ValueError):verified(study_parent)


@pytest.mark.parametrize('key,value',[('policy','blk013-conv49-checkpoint-v1'),('parent_phase_sha256','0'*64),
    ('completed_turns',423),('remaining_logical_calls',819)])
def test_conv44_cannot_reuse_another_parent_or_workload(study_parent,key,value):
    auth=child_approval(study_parent);auth['binding']['checkpoint'][key]=value
    with pytest.raises(BudgetStop):PhasePermit(auth,study_parent.ledger,auth['binding'])
    assert ledger_summary(study_parent.ledger)['physical_attempts']==849


def test_conv44_parent_cannot_seed_other_condition_or_conversation(study_parent):
    from unittest.mock import patch
    link_inputs(study_parent)
    for condition,conversation in (('neither','conv-44'),('full','conv-49')):
        with input_patches(study_parent),patch.object(phases,'_verified_receipt',return_value=study_parent.sources):
            with pytest.raises(ValueError,match='checkpoint|Checkpoint'):
                phases.plan_phase('baseline',study_parent.receipt,study_parent.root/'assets',root=study_parent.root,
                    condition=condition,conversation_id=conversation,checkpoint=study_parent.path,
                    provider_contract_policy='canonical-index-strings-v1')
