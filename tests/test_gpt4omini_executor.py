"""Production native executor, real checkpoint seals and critical-fault rejection."""
import copy
import json

import pytest

from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.gpt4omini_campaign import checkpoint_from,read
from gpt4omini_executor_fixture import run_actual_phase
from gpt4omini_fixture import ROOT


def test_secondary_summary_failure_after_length_is_terminal(tmp_path):
    result=run_actual_phase(tmp_path,root=ROOT,fail_decisions={2:'length'},summary_fault=True)
    receipt=result['receipt']
    assert receipt['status']=='incomplete' and receipt['error_type']=='OSError'
    assert not receipt['recoverable_length_failure']
    assert len(result['requests'])==4
    with pytest.raises(BudgetStop):checkpoint_from(tmp_path/'runs/p0/phase.json',result['ledger'],receipt['binding'],root=ROOT)


def test_exact_actual_executor_can_restore_a_sealed_parent_twice(tmp_path):
    first=run_actual_phase(tmp_path,root=ROOT,fail_decisions={2:'length'})
    assert first['receipt']['recoverable_length_failure'] and first['receipt']['notes']==2
    second=run_actual_phase(tmp_path,root=ROOT,phase='p1',ledger=first['ledger'],parent=first['receipt'],
                            fail_decisions={2:'length'})
    assert second['receipt']['recoverable_length_failure'] and second['receipt']['notes']==4
    third=run_actual_phase(tmp_path,root=ROOT,phase='p2',ledger=first['ledger'],parent=second['receipt'],
                           fail_decisions={2:'length'})
    assert third['receipt']['recoverable_length_failure'] and third['receipt']['notes']==6
    assert first['ledger'].totals()['attempts']==12
    state=read(tmp_path/'runs/p2/partial-memory.json')['state']
    assert state['evo_cnt']==3 and len(state['outcomes'])==6


def test_wrong_parent_path_cannot_duplicate_processed_turns(tmp_path):
    first=run_actual_phase(tmp_path,root=ROOT,fail_decisions={2:'length'})
    second=run_actual_phase(tmp_path,root=ROOT,phase='p1',ledger=first['ledger'],parent=first['receipt'],
                            fail_decisions={2:'length'})
    with pytest.raises(BudgetStop):
        run_actual_phase(tmp_path,root=ROOT,phase='p2',ledger=first['ledger'],parent=second['receipt'],
            approval_updates={'parent_path':str(tmp_path/'runs/p0/phase.json')})
    assert first['ledger'].totals()['attempts']==8


def test_parent_change_after_claim_stops_next_physical_admission(tmp_path):
    first=run_actual_phase(tmp_path,root=ROOT,fail_decisions={2:'length'})
    def change(body,count,ledger):
        if count==1:
            path=tmp_path/'runs/p0/events.jsonl'
            with path.open('a') as stream:stream.write('\n')
    child=run_actual_phase(tmp_path,root=ROOT,phase='p1',ledger=first['ledger'],parent=first['receipt'],on_request=change)
    assert len(child['requests'])==1 and child['receipt']['status']=='incomplete'
    assert not child['receipt']['recoverable_length_failure']


def test_running_leaf_foreign_child_edge_blocks_next_physical_admission(tmp_path):
    def change(body,count,ledger):
        if count==1:
            with ledger.transaction() as db:
                db.execute("INSERT INTO phases VALUES ('foreign','{}','p0','running',NULL)")
    result=run_actual_phase(tmp_path,root=ROOT,on_request=change)
    assert len(result['requests'])==1 and result['receipt']['status']=='incomplete'
    assert not result['receipt']['recoverable_length_failure']
