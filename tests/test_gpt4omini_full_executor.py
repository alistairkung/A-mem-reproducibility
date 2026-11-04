"""Complete675/158 production orchestration with labelled offline model/metric mocks."""
import json

from amem_repro.gpt4omini_campaign import read
from gpt4omini_executor_fixture import run_actual_phase
from gpt4omini_fixture import ROOT


def test_actual_full_executor_uses_exact_complete_cache_and_all_original_questions(tmp_path):
    foreign=tmp_path/'cache/zz-foreign';foreign.mkdir(parents=True)
    (foreign/'identity.json').write_text(json.dumps({'condition':'full'}))
    (foreign/'state.json').write_text(json.dumps({'notes':[None]*675,'evo_cnt':123}))
    result=run_actual_phase(tmp_path,root=ROOT)
    receipt=result['receipt']
    assert receipt['status']=='complete' and receipt['notes']==675 and receipt['questions']==158
    assert receipt['evolution_counter']==675
    assert len(result['requests'])==1666 and result['ledger'].totals()['attempts']==1666
    proof=read(tmp_path/'runs/p0/cache-proof.json')
    assert 'complete.json' in proof['files'] and proof['directory']!='cache/zz-foreign'
    state=read(tmp_path/'runs/p0/final-memory.json')
    assert state['evo_cnt']==675 and len(state['outcomes'])==675
    views=read(tmp_path/'runs/p0/scoring-views.json')
    assert all(len(view['individual_results'])==158 for view in views.values())


def test_saved_output_metric_failure_is_degraded_and_in_verified_capture(tmp_path,monkeypatch):
    from amem_repro.scoring import AuthorScorer
    original=AuthorScorer.score
    def fail_one(self,*args,**kwargs):
        result=original(self,*args,**kwargs)
        self._test_calls=getattr(self,'_test_calls',0)+1
        if self._test_calls==159:
            self._failure('calculate_f1_score',metric='f1',exception_type='OfflineInjectedFailure')
        return result
    monkeypatch.setattr(AuthorScorer,'score',fail_one)
    result=run_actual_phase(tmp_path,root=ROOT)
    assert result['receipt']['status']=='degraded'
    assert result['receipt']['post_scoring_failure_count']==1
    capture=read(tmp_path/'runs/p0/trace-capture.json')
    failures=[r for r in capture['observations'] if r['name']=='A-MEM/metric_computation']
    assert len(failures)==1
    assert failures[0]['metadata']['question_id']=='conv-44:qa:0'
    assert failures[0]['metadata']['scoring_policy']=='author-corrected-v1'
