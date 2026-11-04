import json
import hashlib
import pytest
from amem_repro.budget import BudgetStop
from amem_repro.openrouter import CampaignLedger,SCIENTIFIC_BINDING,cell_store,fingerprint,save_new

def fixture(tmp_path):
    a={**SCIENTIFIC_BINDING,'source_sha256':'a'*64,'conversation_id':'conv-44'}
    ledger=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=a)
    auth={'approved':True,'binding':a,'condition':'full','conversation':'conv-44','kind':'baseline','phase':'A'}
    ledger.claim(auth)
    with ledger.transaction() as db:
        db.execute("INSERT INTO attempts(phase,stage,request_hash,reservation,charge,state) VALUES ('A','metadata','old',4999000,4999000,'settled')")
    seal=ledger.finish('A',{'notes':675},'complete')
    with ledger.transaction() as db:history=ledger.access_snapshot(db)
    cert={'accepted_cells':['conv-44'],'phase_seals':{'conv-44':seal},'next_cell':'conv-49',
          'affordable':True,'ledger_prefix_sha256':fingerprint(history)}
    p=tmp_path/'outcomes/conv-44/frontier.json';save_new(p,cert)
    b={**a,'conversation_id':'conv-49'}
    auth={**auth,'phase':'B','conversation':'conv-49','binding':b,
          'previous_acceptance_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    return CampaignLedger(ledger.path,campaign_root=tmp_path,binding=b),auth

def test_caps_are_per_cell_and_accepted_ancestry_is_rechecked(tmp_path):
    ledger,auth=fixture(tmp_path);phase=ledger.claim(auth)
    i,_=ledger.reserve(phase,'metadata',{'max_tokens':1000})
    ledger.settle(i,{'id':'gen-b1','usage':{'prompt_tokens':100,'completion_tokens':10,'cost':.000021}},1000)
    with ledger.transaction() as db:db.execute("UPDATE attempts SET charge=1 WHERE phase='A'")
    with pytest.raises(BudgetStop):ledger.reserve(phase,'metadata',{'max_tokens':1000})

def test_cannot_skip_a_baseline_or_borrow_its_approval(tmp_path):
    ledger,auth=fixture(tmp_path)
    with pytest.raises(BudgetStop):ledger.claim({**auth,'conversation':'conv-50'})
    with pytest.raises(BudgetStop):ledger.claim({**auth,'previous_acceptance_sha256':'other'})
    with pytest.raises(BudgetStop):ledger.claim({**auth,'condition':'neither'})

def test_cells_reject_namespace_alias(tmp_path):
    (tmp_path/'cells').mkdir()
    (tmp_path/'cells/conv-49').symlink_to(tmp_path)
    with pytest.raises(BudgetStop):cell_store(tmp_path,'conv-49')

def test_prior_unused_budget_does_not_increase_next_cell_cap(tmp_path):
    ledger,auth=fixture(tmp_path);phase=ledger.claim(auth)
    with ledger.transaction() as db:
        db.execute("INSERT INTO attempts(phase,stage,request_hash,reservation,charge,state) VALUES ('B','metadata','other',4999000,4999000,'settled')")
    with pytest.raises(BudgetStop):ledger.reserve(phase,'metadata',{'max_tokens':1000})
