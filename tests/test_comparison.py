"""Synthetic archived-result fixtures; no historical response or live metric is invented."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from amem_repro.config import fingerprint, load_config, source_fingerprint
from amem_repro.manifests import build_manifest
from amem_repro.scoring import AuthorScorer, CORRECTED, HISTORICAL
from amem_repro.comparison import load_saved_run

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False) + '\n')


def seal(directory, phase):
    phase['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in directory.iterdir() if p.is_file() and p.name != 'phase.json'}
    write_json(directory/'phase.json', phase)
    return directory/'phase.json'


def archive(tmp_path, manifest, condition='full', *, run_id='fixture', status='complete', selected=None, score=1.0):
    """Explicit synthetic saved predictions/metrics, not a simulated paid experiment."""
    directory = tmp_path/'artifacts/runs'/run_id
    directory.mkdir(parents=True)
    selected = selected or [c['original_id'] for c in manifest['conversations']]
    conversations = [c for c in manifest['conversations'] if c['original_id'] in selected]
    config = load_config()
    sources = source_fingerprint(ROOT)
    scorer = AuthorScorer(ROOT, dependencies={})
    raw = json.loads((ROOT/'data/locomo10.json').read_text())
    rows = []
    for conv in conversations:
        for q in conv['questions']:
            qa = raw[conv['sample_index']]['qa'][q['original_qa_index']]
            rows.append({'question_id': q['question_id'], 'conversation_id': conv['original_id'],
                         'original_sample_index': conv['sample_index'], 'original_qa_index': q['original_qa_index'],
                         'qa': qa, 'prediction': 'synthetic prediction', 'raw_response': '{"answer":"synthetic prediction"}',
                         'reference': scorer.qa(qa).reference(False), 'metrics': {'f1': score, 'bleu1': score},
                         'category': qa['category'], 'scoring_policy': CORRECTED,
                         'provider_contract_policy': 'canonical-index-strings-v1', 'metric_failures': []})
    views = {}
    for policy in [CORRECTED, HISTORICAL]:
        results = copy.deepcopy(rows)
        for row in results:
            row['scoring_policy'] = policy
            row['reference'] = scorer.qa(row['qa']).reference(policy == HISTORICAL)
            if row['category']==5: row['metrics']['adversarial_correct']=0
        views[policy] = {'scoring_policy': policy, 'scorer_sha256': scorer.scorer_sha256,
                         'individual_results': results,
                         'aggregate_metrics': scorer.aggregate([r['metrics'] for r in results], [r['category'] for r in results])}
    start = {'type':'run_start', 'run_id':run_id, 'configuration':config, 'manifest':manifest,
             'source_hashes':sources, 'condition':condition, 'repetition':0,
             'provider_contract_policy':'canonical-index-strings-v1',
             'memory_actions':config['conditions'][condition],'action_policy':'released-action-boundaries-v1'}
    failures = ([{'type':'failure','kind':'synthetic-retained-fallback','run_id':run_id}] if status=='degraded' else [])
    events = [start] + failures + [{'type':'question_result','run_id':run_id,'question_id':r['question_id'], 'result':r} for r in rows]
    (directory/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    binding = {'manifest_sha256':fingerprint(manifest), 'config_sha256':fingerprint(config),
               'source_sha256':fingerprint(sources), 'condition':condition, 'population':manifest['scope'],
               'repetition':0, 'model':config['model']['id'],
               'endpoint':config['model']['base_url']+config['model']['route'],
               'provider_contract_policy':'canonical-index-strings-v1',
               'memory_actions':config['conditions'][condition],'action_policy':'released-action-boundaries-v1'}
    write_json(directory/'run.json', {'run_id':run_id,'expected_question_ids':[r['question_id'] for r in rows]})
    write_json(directory/'approval.json', {'approved':True,'run_id':run_id,'phase':'baseline','binding':binding})
    write_json(directory/'preflight.json', {'synthetic':True})
    write_json(directory/'summary.json', {'run_id':run_id,'status':status,'expected_questions':len(rows),
                                         'completed_questions':len(rows),'failures':failures})
    write_json(directory/'scoring-views.json', views)
    phase = {'run_id':run_id,'phase':'baseline','population':manifest['scope'],'binding':binding,
             'status':status,'usable_for_next_phase':status!='incomplete','conversation_ids':selected,
             'expected_questions':len(rows),'completed_questions':len(rows),
             'returned_models':['synthetic-model-version'],'system_fingerprints':['synthetic-fingerprint'],
             'budget':{'charged_or_reserved_microusd':100,'logical_calls':0,'physical_attempts':0,'unknown_attempts':0}}
    return seal(directory, phase)


def test_load_verifies_saved_predictions_and_both_policy_views_without_scoring(tmp_path, monkeypatch):
    manifest = build_manifest(ROOT/'data/locomo10.json','smoke')
    phase = archive(tmp_path, manifest)
    before = {p:p.read_bytes() for p in phase.parent.iterdir() if p.is_file()}
    monkeypatch.setattr(AuthorScorer,'score',lambda *a,**k:pytest.fail('saved-result import cannot rescore'))
    bundle = load_saved_run(phase, manifest, root=ROOT, archive_root=tmp_path)
    assert bundle['condition']=='full' and bundle['status']=='complete'
    assert list(bundle['views'])==[CORRECTED,HISTORICAL]
    assert len(bundle['views'][CORRECTED]['individual_results'])==4
    assert {p:p.read_bytes() for p in before}==before


def test_saved_phase_cannot_relabel_changed_scientific_source_as_original(tmp_path):
    manifest = build_manifest(ROOT/'data/locomo10.json','smoke')
    path = archive(tmp_path,manifest)
    phase=json.loads(path.read_text())
    events=[json.loads(line) for line in (path.parent/'events.jsonl').read_text().splitlines()]
    events[0]['source_hashes']['files']['memory_layer.py']='0'*64
    phase['binding']['source_sha256']=fingerprint(events[0]['source_hashes'])
    (path.parent/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    approval=json.loads((path.parent/'approval.json').read_text());approval['binding']=phase['binding']
    write_json(path.parent/'approval.json',approval);seal(path.parent,phase)
    with pytest.raises(ValueError,match='Scientific source'):
        load_saved_run(path,manifest,root=ROOT,archive_root=tmp_path)


def test_checkpoint_lineage_credits_parent_charge_once_and_rejects_wrong_parent(tmp_path):
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    parent_path=archive(tmp_path,manifest,run_id='parent',status='incomplete')
    parent=json.loads(parent_path.read_text())
    (parent_path.parent/'events.jsonl').write_text((parent_path.parent/'events.jsonl').read_text().splitlines()[0]+'\n')
    summary=json.loads((parent_path.parent/'summary.json').read_text());summary['completed_questions']=0
    write_json(parent_path.parent/'summary.json',summary);parent['completed_questions']=0
    seal(parent_path.parent,parent)
    child_path=archive(tmp_path,manifest,run_id='child',status='degraded')
    child=json.loads(child_path.read_text())
    child['binding']['checkpoint']={'parent_run_id':'parent','parent_phase_sha256':fingerprint(parent),
                                  'policy':'blk014-checkpoint-v1'}
    approval=json.loads((child_path.parent/'approval.json').read_text());approval['binding']=child['binding']
    write_json(child_path.parent/'approval.json',approval);seal(child_path.parent,child)
    bundle=load_saved_run(child_path,manifest,root=ROOT,archive_root=tmp_path)
    assert set(bundle['sources'])=={'parent','child'}
    assert sum(p['budget']['charged_or_reserved_microusd'] for p in bundle['sources'].values())==200
    child['binding']['checkpoint']['parent_phase_sha256']='0'*64
    approval['binding']=child['binding'];write_json(child_path.parent/'approval.json',approval);seal(child_path.parent,child)
    with pytest.raises(ValueError,match='Checkpoint parent'):
        load_saved_run(child_path,manifest,root=ROOT,archive_root=tmp_path)


def test_population_aggregation_weights_questions_not_conversation_means(tmp_path):
    from amem_repro.comparison import assemble_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','fallback')
    paths=[archive(tmp_path,manifest,run_id=c['original_id'],selected=[c['original_id']],score=float(i==0))
           for i,c in enumerate(manifest['conversations'])]
    comparison=assemble_comparison(manifest,paths,root=ROOT,archive_root=tmp_path)
    assert comparison['status']=='incomplete'
    assert comparison['complete_conditions']==['full']
    assert comparison['views']['full'][CORRECTED]['aggregate_metrics']['overall']['f1']['mean']==pytest.approx(196/558)
    assert len(comparison['missing_cells'])==9
    assert comparison['paired_differences']=={}
    assert comparison['cost']['charged_or_reserved_microusd']==300


def test_complete_matched_conditions_export_saved_views_and_descriptive_differences(tmp_path):
    from amem_repro.comparison import assemble_comparison, write_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    paths=[archive(tmp_path,manifest,condition=c,run_id=c,score=(.75 if c=='full' else .25))
           for c in load_config()['conditions']]
    comparison=assemble_comparison(manifest,paths,root=ROOT,archive_root=tmp_path)
    before=copy.deepcopy(comparison)
    assert comparison['status']=='complete' and comparison['missing_cells']==[]
    assert comparison['paired_differences']['neither'][CORRECTED]['aggregate_metrics']['overall']['f1']['mean']==-.5
    assert all(row['question_id']==q['question_id'] for row,q in zip(
        comparison['views']['full'][HISTORICAL]['individual_results'],manifest['conversations'][0]['questions']))
    write_comparison(comparison,tmp_path/'exports')
    summary=json.loads((tmp_path/'exports/comparison.json').read_text())
    assert 'views' not in summary and summary['view_artifacts']['full']=='full/scoring_views.json'
    assert (tmp_path/'exports/headline_metrics.csv').is_file()
    assert (tmp_path/'exports/paired_question_differences.csv').is_file()
    assert comparison==before
    with pytest.raises(FileExistsError):write_comparison(comparison,tmp_path/'exports')


def test_incomplete_phase_retains_costs_and_failures_but_cannot_supply_population_quality(tmp_path):
    from amem_repro.comparison import assemble_comparison, write_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    path=archive(tmp_path,manifest,status='incomplete')
    comparison=assemble_comparison(manifest,[path],root=ROOT,archive_root=tmp_path)
    assert comparison['status']=='incomplete' and comparison['views']=={}
    assert comparison['cost']['charged_or_reserved_microusd']==100
    write_comparison(comparison,tmp_path/'incomplete')
    assert json.loads((tmp_path/'incomplete/comparison.json').read_text())['complete_conditions']==[]
    assert not (tmp_path/'incomplete/full').exists()


def test_a_complete_label_cannot_hide_a_recorded_failure(tmp_path):
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    path=archive(tmp_path,manifest)
    phase=json.loads(path.read_text()); summary=json.loads((path.parent/'summary.json').read_text())
    summary['failures']=[{'type':'failure','kind':'metric_computation'}]
    write_json(path.parent/'summary.json',summary);seal(path.parent,phase)
    with pytest.raises(ValueError,match='Failure classification'):
        load_saved_run(path,manifest,root=ROOT,archive_root=tmp_path)


@pytest.mark.parametrize('change',['duplicate','reorder','drop','qa','prediction','reference','policy','aggregate','scorer','actions','hash'])
def test_mismatched_or_altered_evidence_is_rejected(tmp_path,change):
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    path=archive(tmp_path,manifest)
    phase=json.loads(path.read_text())
    events=[json.loads(line) for line in (path.parent/'events.jsonl').read_text().splitlines()]
    views=json.loads((path.parent/'scoring-views.json').read_text())
    if change=='duplicate':events[2]=copy.deepcopy(events[1])
    elif change=='reorder':events[1],events[2]=events[2],events[1]
    elif change=='drop':events.pop()
    elif change=='qa':events[1]['result']['qa']['answer']='tampered'
    elif change=='prediction':views[HISTORICAL]['individual_results'][0]['prediction']='tampered'
    elif change=='reference':views[CORRECTED]['individual_results'][0]['reference']='tampered'
    elif change=='policy':views.pop(HISTORICAL)
    elif change=='aggregate':views[CORRECTED]['aggregate_metrics']['overall']['f1']['mean']=.123
    elif change=='scorer':views[CORRECTED]['scorer_sha256']='0'*64
    elif change=='actions':events[0]['memory_actions']['strengthen']=False
    elif change=='hash':
        (path.parent/'run.json').write_text('tampered')
        with pytest.raises(ValueError,match='hash mismatch'):
            load_saved_run(path,manifest,root=ROOT,archive_root=tmp_path)
        return
    (path.parent/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    write_json(path.parent/'scoring-views.json',views);seal(path.parent,phase)
    with pytest.raises(ValueError):load_saved_run(path,manifest,root=ROOT,archive_root=tmp_path)


def test_duplicate_cells_and_mixed_provider_fingerprints_cannot_be_compared(tmp_path):
    from amem_repro.comparison import assemble_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    first=archive(tmp_path,manifest,run_id='full')
    with pytest.raises(ValueError,match='Duplicate independent'):
        assemble_comparison(manifest,[first,first],root=ROOT,archive_root=tmp_path)
    second=archive(tmp_path,manifest,condition='neither',run_id='neither')
    phase=json.loads(second.read_text());phase['system_fingerprints']=['changed'];seal(second.parent,phase)
    with pytest.raises(ValueError,match='provider versions'):
        assemble_comparison(manifest,[first,second],root=ROOT,archive_root=tmp_path)


def test_exports_cannot_be_written_inside_preserved_run_or_cache(tmp_path):
    from amem_repro.comparison import assemble_comparison, write_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    result=assemble_comparison(manifest,[],root=ROOT,archive_root=tmp_path)
    for area in ['runs','cache']:
        with pytest.raises(ValueError,match='preserved'):
            write_comparison(result,tmp_path/'artifacts'/area/'new-export',archive_root=tmp_path)
    assert not (tmp_path/'artifacts').exists()


def test_degraded_conditions_are_retained_and_unknown_reservations_are_not_zero(tmp_path):
    from amem_repro.comparison import assemble_comparison
    manifest=build_manifest(ROOT/'data/locomo10.json','smoke')
    paths=[archive(tmp_path,manifest,condition=c,run_id=c,status=('degraded' if c=='full' else 'complete'),score=0)
           for c in load_config()['conditions']]
    result=assemble_comparison(manifest,paths,root=ROOT,archive_root=tmp_path)
    assert result['status']=='degraded' and len(result['complete_conditions'])==4
    assert result['views']['full'][CORRECTED]['aggregate_metrics']['overall']['f1']['mean']==0
    assert result['runs'][-1]['failures'][0]['kind']=='synthetic-retained-fallback'
    phase=json.loads(paths[-1].read_text());phase['budget']['unknown_attempts']=1
    phase['budget']['charged_or_reserved_microusd']=319373
    phase['status']='incomplete';phase['usable_for_next_phase']=False
    summary=json.loads((paths[-1].parent/'summary.json').read_text());summary['status']='incomplete'
    write_json(paths[-1].parent/'summary.json',summary);seal(paths[-1].parent,phase)
    partial=assemble_comparison(manifest,paths,root=ROOT,archive_root=tmp_path)
    assert partial['status']=='incomplete' and 'full' not in partial['views']
    assert partial['cost']['charged_or_reserved_microusd']==319673
    assert partial['cost']['unknown_attempts']==1
