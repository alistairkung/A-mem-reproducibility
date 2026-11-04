"""Scientific native replay, original fallbacks and sequential exact restoration."""
import copy
import json

import pytest

from amem_repro.replay import memory_view
from amem_repro.observability import LangfuseObserver
from amem_repro.config import fingerprint
from amem_repro.budget import BudgetStop
from amem_repro.openrouter import SCIENTIFIC_BINDING,CampaignLedger
from test_observability import Client
from gpt4omini_fixture import run_fixture,ROOT


def identity(run):
    return {**SCIENTIFIC_BINDING,'condition':'full','population':'smoke','manifest_sha256':'a'*64,
            'conversation_id':'conv-26','repetition':0,'run_id':run,
            'provider_contract_policy':'strict-original-v1','observability_policy':'run2-audit-essential-v1'}


def scientific_state(state):
    saved=copy.deepcopy(state);saved.pop('build_failures',None)
    return memory_view(saved)


def test_native_saved_response_replay_matches_unchanged_author_and_full_action_gates(tmp_path):
    reference=run_fixture(tmp_path/'reference')
    candidate=run_fixture(tmp_path/'candidate',records=reference['generations'],candidate=True)
    assert len(reference['generations'])==44
    assert reference['requests']==candidate['requests']
    assert scientific_state(reference['state'])==scientific_state(candidate['state'])
    assert reference['results']==candidate['results']
    assert reference['views']==candidate['views']
    assert reference['summary']['status']==candidate['summary']['status']=='complete'


def test_native_tracing_does_not_change_requests_results_or_memory(tmp_path):
    ref=run_fixture(tmp_path/'reference')
    observer=LangfuseObserver(Client(),identity('traced'))
    traced=run_fixture(tmp_path/'traced',records=ref['generations'],observer=observer)
    capture=observer.finish()
    assert not capture['errors']
    assert ref['requests']==traced['requests'] and ref['results']==traced['results']
    assert scientific_state(ref['state'])==scientific_state(traced['state'])
    gens=[r for r in capture['observations'] if r['type']=='generation']
    assert len(gens)==44
    assert all(r['cost_details']=={'total':.000021} for r in gens)
    assert all(r['metadata']['actual_provider']=='OpenAI' for r in gens)


def test_malformed_native_evolution_uses_exact_original_fallback_without_repair(tmp_path):
    result=run_fixture(tmp_path/'malformed',fail_decisions={2:'malformed',4:'malformed'})
    assert result['summary']['status']=='degraded'
    assert len(result['state']['notes'])==18 and len(result['results'])==4
    failures=[e for e in result['events'] if e.get('kind')=='original_evolution_fallback']
    assert len(failures)==2 and all(e['original_fallback_verified'] for e in failures)
    assert result['state']['evo_cnt']==16
    assert len(result['requests'])==44
    assert result['ledger'].totals()['unknown_attempts']==0


def test_two_successive_native_checkpoint_children_match_uninterrupted_failure_history(tmp_path):
    reference=run_fixture(tmp_path/'reference',fail_decisions={2:'malformed',4:'malformed'})
    first=run_fixture(tmp_path/'first',fail_decisions={2:'length'})
    assert first['receipt']['recoverable_length_failure'] and len(first['state']['notes'])==2
    second=run_fixture(tmp_path/'second',fail_decisions={2:'length'},checkpoint=first['checkpoint'],
                       ledger=first['ledger'],parent=first['receipt'])
    assert second['receipt']['recoverable_length_failure'] and len(second['state']['notes'])==4
    third=run_fixture(tmp_path/'third',checkpoint=second['checkpoint'],
                      ledger=first['ledger'],parent=second['receipt'])
    assert third['summary']['status']=='degraded' and len(third['results'])==4
    assert scientific_state(third['state'])==scientific_state(reference['state'])
    assert third['results']==reference['results']
    assert len(first['requests'])+len(second['requests'])+len(third['requests'])==44
    assert first['ledger'].totals()['attempts']==44
    assert first['ledger'].totals()['unknown_attempts']==0


def test_changed_phase_approval_cannot_turn_smoke_into_baseline(tmp_path):
    binding=copy.deepcopy(SCIENTIFIC_BINDING)
    ledger=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=binding)
    approval={'approved':True,'binding':binding,'phase':'smoke','kind':'compatibility',
              'condition':'full','conversation':'conv-44'}
    ledger.claim(approval)
    with ledger.transaction() as db:
        changed=copy.deepcopy(approval);changed['kind']='baseline'
        db.execute('UPDATE phases SET approval=?',(json.dumps(changed,sort_keys=True),))
    with pytest.raises(BudgetStop):ledger.reserve('smoke','metadata',{'max_tokens':1000})
