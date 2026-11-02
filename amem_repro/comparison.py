"""Offline T8 comparison of verified saved predictions; never run a model or scorer.

The original author aggregator combines per-question values. Incomplete cells remain
inventory evidence, and cannot be presented as complete population quality results.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

from .actions import action_configuration
from .config import AUTHOR_REVISION, fingerprint, load_config, reject_credentials
from .manifests import expand_manifest
from .scoring import AuthorScorer, CORRECTED, HISTORICAL

ROOT = Path(__file__).resolve().parents[1]
POLICIES = (CORRECTED, HISTORICAL)


def _read(path):
    value = json.loads(path.read_text())
    reject_credentials(value)
    return value


def _archive(path, archive_root):
    path = Path(path).resolve()
    if path.name != 'phase.json' or not path.is_relative_to((archive_root/'artifacts/runs').resolve()):
        raise ValueError('Expected an archived study phase receipt')
    phase = _read(path)
    if (path.parent/'finalization-error.json').exists() and phase.get('status')!='incomplete':
        raise ValueError('Failed finalization marker prohibits completed quality results')
    required = {'approval.json', 'preflight.json', 'events.jsonl', 'summary.json', 'run.json'}
    if not required.issubset(phase.get('artifact_sha256', {})):
        raise ValueError('Missing phase inventory')
    for name, digest in phase['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path.parent/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Archived artifact hash mismatch')
    approval = _read(path.parent/'approval.json')
    if (approval.get('approved') is not True or approval['binding'] != phase['binding']
            or approval['run_id'] != phase['run_id'] or approval['phase'] != phase['phase']):
        raise ValueError('Archived approval provenance mismatch')
    events = [json.loads(line) for line in (path.parent/'events.jsonl').read_text().splitlines()]
    reject_credentials(events)
    if not events or events[0].get('type') != 'run_start' or any(e.get('run_id') != phase['run_id'] for e in events):
        raise ValueError('Run identity or start record mismatch')
    return phase, events


def load_saved_run(phase_path, manifest, *, root=ROOT, archive_root=None):
    """Verify one saved phase against the frozen population, returning immutable copies.

    archive_root permits an explicitly supplied relocated artifact archive; root still
    supplies verified author source and the original frozen dataset. No dotenv/client.
    """
    root = Path(root).resolve()
    archive_root = Path(archive_root or root).resolve()
    manifest = expand_manifest(root/'data/locomo10.json', manifest)
    phase, events = _archive(phase_path, archive_root)
    start, binding = events[0], phase['binding']
    config = load_config(root/'config/study.json')
    condition = binding['condition']
    flags = action_configuration(condition)
    if (start.get('condition') != condition or start.get('repetition') != 0 or binding.get('repetition') != 0
            or start['configuration'] != config or binding['config_sha256'] != fingerprint(config)
            or binding['source_sha256'] != fingerprint(start['source_hashes'])
            or binding['manifest_sha256'] != fingerprint(start['manifest'])
            or binding['model'] != config['model']['id']
            or binding['endpoint'] != config['model']['base_url']+config['model']['route']
            or binding.get('provider_contract_policy') != 'canonical-index-strings-v1'
            or start.get('provider_contract_policy') != binding['provider_contract_policy']):
        raise ValueError('Scientific run provenance mismatch')
    science = ['memory_layer.py', 'test_advanced.py', 'utils.py', 'load_dataset.py',
               'amem_repro/author.py', 'amem_repro/adapter.py', 'amem_repro/contracts.py',
               'amem_repro/config.py','amem_repro/scoring.py','amem_repro/measurements.py',
               'config/study.json','config/assets.json','uv.lock','pyproject.toml']
    if condition != 'full' or 'amem_repro/actions.py' in start['source_hashes']['files']:
        science.append('amem_repro/actions.py')
    if (start['source_hashes'].get('author_revision') != AUTHOR_REVISION
            or any(start['source_hashes']['files'].get(name) != hashlib.sha256((root/name).read_bytes()).hexdigest()
                   for name in science)):
        raise ValueError('Scientific source differs from the frozen implementation')
    preflight=_read(Path(phase_path).parent/'preflight.json')
    if (binding.get('preflight_sha256')!=fingerprint(preflight)
            or preflight.get('source_sha256')!=binding['source_sha256']
            or preflight.get('runtime',{}).get('ok') is not True
            or preflight.get('runtime',{}).get('network_disabled') is not True):
        raise ValueError('Runtime preflight provenance mismatch')
    if (condition != 'full' and (start.get('memory_actions') != flags or binding.get('memory_actions') != flags
                                 or start.get('action_policy') != 'released-action-boundaries-v1'
                                 or binding.get('action_policy') != 'released-action-boundaries-v1')):
        raise ValueError('Missing ablation action provenance')
    if 'memory_actions' in start and start['memory_actions'] != flags:
        raise ValueError('Memory action configuration mismatch')
    stored = expand_manifest(root/'data/locomo10.json', start['manifest'])
    conversations = {c['original_id']:c for c in manifest['conversations']}
    selected = phase['conversation_ids']
    if (not selected or len(selected) != len(set(selected)) or any(c not in conversations for c in selected)
            or selected != [c for c in conversations if c in selected]):
        raise ValueError('Conversation population/order mismatch')
    for conv in stored['conversations']:
        if conv['original_id'] in selected and conv != conversations[conv['original_id']]:
            raise ValueError('Selected conversation differs from frozen population')
    if not set(selected).issubset({c['original_id'] for c in stored['conversations']}):
        raise ValueError('Selected conversation missing from run manifest')
    expected = [q for c in selected for q in conversations[c]['questions']]
    expected_ids = [q['question_id'] for q in expected]
    run = _read(Path(phase_path).parent/'run.json')
    summary = _read(Path(phase_path).parent/'summary.json')
    if (run['run_id'] != phase['run_id'] or run['expected_question_ids'] != expected_ids
            or phase['expected_questions'] != len(expected_ids) or summary['expected_questions'] != len(expected_ids)
            or summary['status'] != phase['status'] or summary['run_id'] != phase['run_id']):
        raise ValueError('Run completion provenance mismatch')
    if summary['failures'] != [e for e in events if e['type']=='failure']:
        raise ValueError('Failure classification/provenance differs from archived events')
    if ((phase['status']=='complete' and summary['failures'])
            or (phase['status']=='degraded' and not summary['failures'])):
        raise ValueError('Failure classification differs from retained failure evidence')
    results = [e['result'] for e in events if e['type']=='question_result']
    ids = [r['question_id'] for r in results]
    if (len(ids) != len(set(ids)) or ids != expected_ids[:len(ids)]
            or phase['completed_questions'] != len(ids) or summary['completed_questions'] != len(ids)):
        raise ValueError('Question identity/order/coverage mismatch')
    raw = json.loads((root/'data/locomo10.json').read_bytes())
    scorer = AuthorScorer(root, dependencies={})  # aggregate/QA only; no local models or scoring.
    for row, selection in zip(results, expected):
        conv = conversations[row['conversation_id']]
        if (row['original_sample_index'] != conv['sample_index']
                or row['original_qa_index'] != selection['original_qa_index']
                or row['qa'] != raw[conv['sample_index']]['qa'][selection['original_qa_index']]
                or row['category'] != selection['category'] or row['scoring_policy'] != CORRECTED
                or row['provider_contract_policy'] != binding['provider_contract_policy']):
            raise ValueError('Original question/reference data mismatch')
    completed = phase['status'] in ('complete','degraded')
    views = {}
    if completed:
        if (phase.get('usable_for_next_phase') is not True or ids != expected_ids
                or 'scoring-views.json' not in phase['artifact_sha256']):
            raise ValueError('Incomplete phase cannot supply completed quality results')
        views = _read(Path(phase_path).parent/'scoring-views.json')
        if set(views) != set(POLICIES):
            raise ValueError('Both scoring policies are required')
        for policy in POLICIES:
            view = views[policy]
            if (view['scoring_policy'] != policy or view['scorer_sha256'] != scorer.scorer_sha256
                    or [r['question_id'] for r in view['individual_results']] != expected_ids):
                raise ValueError('Saved scoring identity mismatch')
            for row, original in zip(view['individual_results'], results):
                allowed = {'reference','metrics','scoring_policy','metric_failures'}
                if ({k:v for k,v in row.items() if k not in allowed} != {k:v for k,v in original.items() if k not in allowed}
                        or row['scoring_policy'] != policy
                        or row['reference'] != scorer.qa(row['qa']).reference(policy==HISTORICAL)
                        or not {'f1','bleu1'}.issubset(row['metrics'])
                        or any(type(v) not in (int,float) or not math.isfinite(v) for v in row['metrics'].values())
                        or (row['category']==5 and 'adversarial_correct' not in row['metrics'])):
                    raise ValueError('Scoring views changed predictions/data or contain invalid metrics')
            aggregate = scorer.aggregate([r['metrics'] for r in view['individual_results']],
                                         [r['qa']['category'] for r in view['individual_results']])
            if view['aggregate_metrics'] != aggregate:
                raise ValueError('Saved aggregate differs from author semantics')
    elif phase['status'] != 'incomplete':
        raise ValueError('Unknown completion classification')
    sources = {phase['run_id']:phase}
    lineage_events = list(events)
    checkpoint = binding.get('checkpoint')
    if checkpoint:
        parent_id = checkpoint.get('parent_run_id')
        if (not isinstance(parent_id,str) or Path(parent_id).name != parent_id or parent_id==phase['run_id']
                or checkpoint.get('policy') != 'blk014-checkpoint-v1' or condition != 'full'):
            raise ValueError('Checkpoint parent identity/policy mismatch')
        parent_path = archive_root/'artifacts/runs'/parent_id/'phase.json'
        parent, _ = _archive(parent_path, archive_root)
        if (fingerprint(parent) != checkpoint.get('parent_phase_sha256')
                or parent['status'] != 'incomplete' or 'checkpoint' in parent['binding']
                or parent['conversation_ids'] != selected):
            raise ValueError('Checkpoint parent receipt mismatch')
        prior = load_saved_run(parent_path, manifest, root=root, archive_root=archive_root)
        if prior['results'] or prior['condition'] != condition:
            raise ValueError('Checkpoint parent cannot contain regenerated QA')
        sources.update(prior['sources'])
        lineage_events = prior['events'] + events
    return copy.deepcopy({'run_id':phase['run_id'], 'condition':condition, 'conversation_ids':selected,
                          'status':phase['status'], 'phase':phase, 'views':views, 'events':events,
                          'expected_questions':len(expected_ids),'completed_questions':len(results),
                          'sources':sources, 'results':results, 'lineage_events':lineage_events,
                          'failures':summary['failures'], 'telemetry':_telemetry(lineage_events)})


def assemble_comparison(manifest, phase_paths, *, root=ROOT, archive_root=None, study_budget=None):
    """Combine saved per-question values, retaining coverage and one-build provenance.

    Only a condition with every selected conversation has population aggregates.
    Comparisons require complete matched conditions; no question/trial is dropped.
    """
    root = Path(root).resolve()
    manifest = expand_manifest(root/'data/locomo10.json', manifest)
    conditions = list(load_config(root/'config/study.json')['conditions'])
    conversations = [c['original_id'] for c in manifest['conversations']]
    expected_ids = [q['question_id'] for c in manifest['conversations'] for q in c['questions']]
    bundles = [load_saved_run(p,manifest,root=root,archive_root=archive_root) for p in phase_paths]
    cells, sources = {}, {}
    for bundle in bundles:
        for conversation in bundle['conversation_ids']:
            cell = (bundle['condition'],conversation)
            if cell in cells:
                raise ValueError('Duplicate independent run for one condition/conversation')
            cells[cell] = bundle
        for run_id, source in bundle['sources'].items():
            if run_id in sources and sources[run_id] != source:
                raise ValueError('Conflicting lineage source receipts')
            sources[run_id] = source
    inventory = []
    missing = []
    for condition in conditions:
        for conversation in conversations:
            bundle = cells.get((condition,conversation))
            if bundle is None:
                missing.append({'condition':condition,'conversation_id':conversation})
            inventory.append({'condition':condition,'conversation_id':conversation,
                              'status':bundle['status'] if bundle else 'missing',
                              'run_id':bundle['run_id'] if bundle else None,
                              'expected_questions':len(next(c for c in manifest['conversations'] if c['original_id']==conversation)['questions']),
                              'completed_questions':sum(r['conversation_id']==conversation for r in bundle['results']) if bundle else 0})
    views, complete = {}, []
    scorer = AuthorScorer(root, dependencies={})
    for condition in conditions:
        selected = [cells.get((condition,c)) for c in conversations]
        if any(b is None or b['status']=='incomplete' for b in selected):
            continue
        by_run = {b['run_id']:b for b in selected}
        views[condition] = {}
        for policy in POLICIES:
            rows = {r['question_id']:copy.deepcopy(r) for b in by_run.values() for r in b['views'][policy]['individual_results']}
            if set(rows) != set(expected_ids):
                raise ValueError('Complete condition question coverage differs')
            ordered = [rows[q] for q in expected_ids]
            views[condition][policy] = {'scoring_policy':policy,'scorer_sha256':scorer.scorer_sha256,
                                       'individual_results':ordered,
                                       'aggregate_metrics':scorer.aggregate([r['metrics'] for r in ordered],
                                                                           [r['qa']['category'] for r in ordered])}
        complete.append(condition)
    version_sets = {(tuple(b['phase'].get('returned_models',[])),tuple(b['phase'].get('system_fingerprints',[])))
                    for b in bundles if b['status']!='incomplete'}
    if len(version_sets)>1 or any(len(v)!=1 or len(f)!=1 for v,f in version_sets):
        raise ValueError('Completed conditions mix provider versions or fingerprints')
    paired = {}
    if 'full' in views:
        for condition in complete:
            if condition=='full': continue
            paired[condition] = {}
            for policy in POLICIES:
                rows=[]
                for actual,baseline in zip(views[condition][policy]['individual_results'],views['full'][policy]['individual_results']):
                    if actual['question_id'] != baseline['question_id'] or actual['qa'] != baseline['qa']:
                        raise ValueError('Paired question/reference mismatch')
                    if set(actual['metrics']) != set(baseline['metrics']):
                        raise ValueError('Paired metric schemas differ')
                    rows.append({'question_id':actual['question_id'],'category':actual['qa']['category'],
                                 'metrics':{m:actual['metrics'][m]-baseline['metrics'][m] for m in baseline['metrics']},
                                 'condition_metric_failures':actual.get('metric_failures',[]),
                                 'baseline_metric_failures':baseline.get('metric_failures',[])})
                paired[condition][policy] = {'direction':'condition minus full', 'individual_results':rows,
                    'aggregate_metrics':scorer.aggregate([r['metrics'] for r in rows],[r['category'] for r in rows])}
    source_costs={}
    for run_id, phase in sources.items():
        budget=phase['budget']
        keys=('charged_or_reserved_microusd','logical_calls','physical_attempts','unknown_attempts')
        if any(type(budget.get(k)) is not int or budget[k]<0 for k in keys):
            raise ValueError('Missing conservative cost/attempt evidence')
        source_costs[run_id]={k:budget[k] for k in keys}
    totals={k:sum(v[k] for v in source_costs.values()) for k in
            ('charged_or_reserved_microusd','logical_calls','physical_attempts','unknown_attempts')}
    if study_budget is not None:
        if (type(study_budget.get('charged_or_reserved_microusd')) is not int
                or study_budget['charged_or_reserved_microusd']<totals['charged_or_reserved_microusd']):
            raise ValueError('Study ledger does not cover observed phase charges')
    status='incomplete' if len(complete)!=len(conditions) else ('degraded' if any(b['status']=='degraded' for b in bundles) else 'complete')
    return {'comparison_version':1,'population':manifest['scope'],'manifest_sha256':fingerprint(manifest),
            'status':status,'complete_conditions':complete,'missing_cells':missing,'inventory':inventory,
            'views':views,'paired_differences':paired,'source_costs':source_costs,'cost':totals,
            'study_budget':copy.deepcopy(study_budget),
            'runs':[{'run_id':b['run_id'],'condition':b['condition'],'status':b['status'],
                     'conversation_ids':b['conversation_ids'],'lineage_run_ids':list(b['sources']),
                     'phase_receipts':{run_id:{'path':f'artifacts/runs/{run_id}/phase.json','sha256':fingerprint(p)}
                                       for run_id,p in b['sources'].items()},
                     'returned_models':b['phase'].get('returned_models',[]),
                     'system_fingerprints':b['phase'].get('system_fingerprints',[]),
                     'provider_contract_policy':b['phase']['binding']['provider_contract_policy'],
                     'telemetry':b['telemetry'],'failures':b['failures']} for b in bundles],
            'interpretation':'One build per condition/conversation; descriptive question-paired differences, not stochastic trials or significance tests.'}


def write_comparison(comparison, directory, *, archive_root=ROOT):
    """Write fresh local exports only; Langfuse import remains an explicit separate call."""
    import csv
    from .reporting import write_tables

    reject_credentials(comparison)
    directory=Path(directory).resolve()
    if any(directory.is_relative_to(Path(archive_root).resolve()/p) for p in ('artifacts/runs','artifacts/cache')):
        raise ValueError('Comparison exports must not modify preserved runs or caches')
    directory.mkdir(parents=True,exist_ok=False)
    summary=copy.deepcopy({k:v for k,v in comparison.items() if k!='views'})
    summary['view_artifacts']={condition:f'{condition}/scoring_views.json' for condition in comparison['views']}
    (directory/'comparison.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    with (directory/'headline_metrics.csv').open('w',newline='') as handle:
        fields=['condition','population','manifest_sha256','repetition','scoring_policy','group','qa_count',
                'f1','bleu1','adversarial_correct','adversarial_count']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for condition,views in comparison['views'].items():
            write_tables(views,directory/condition)
            for policy,view in views.items():
                for group,metrics in view['aggregate_metrics'].items():
                    adversarial=metrics.get('adversarial_correct',{})
                    writer.writerow({'condition':condition,'population':comparison['population'],
                        'manifest_sha256':comparison['manifest_sha256'],'repetition':0,'scoring_policy':policy,
                        'group':group,'qa_count':metrics['f1']['count'],'f1':metrics['f1']['mean'],
                        'bleu1':metrics['bleu1']['mean'],'adversarial_correct':adversarial.get('mean'),
                        'adversarial_count':adversarial.get('count')})
    with (directory/'paired_question_differences.csv').open('w',newline='') as handle:
        fields=['condition','scoring_policy','question_id','category','metric','difference',
                'condition_metric_failures','baseline_metric_failures']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for condition,policies in comparison['paired_differences'].items():
            for policy,view in policies.items():
                for row in view['individual_results']:
                    for metric,value in row['metrics'].items():
                        writer.writerow({'condition':condition,'scoring_policy':policy,
                            'question_id':row['question_id'],'category':row['category'],'metric':metric,'difference':value,
                            **{k:json.dumps(row[k]) for k in ('condition_metric_failures','baseline_metric_failures')}})
    with (directory/'generation_usage.csv').open('w',newline='') as handle:
        fields=['condition','run_id','stage','logical_calls','physical_attempts','retry_attempts',
                'known_input_tokens','known_output_tokens','unknown_usage_attempts','rejected_generations',
                'compatibility_deviations','transformed_items','logical_duration_seconds']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for run in comparison['runs']:
            for stage,usage in run['telemetry']['generation_stages'].items():
                writer.writerow({'condition':run['condition'],'run_id':run['run_id'],'stage':stage,**usage})
    with (directory/'retrieval_observations.csv').open('w',newline='') as handle:
        fields=['condition','run_id','question_id','conversation_id','initial_count','expanded_count','context_tokens',
                'token_count_method','tokenizer_revision','token_count_exact','token_count_error','api_final_prompt_tokens']
        writer=csv.DictWriter(handle,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for run in comparison['runs']:
            for row in run['telemetry']['retrieval']:
                writer.writerow({'condition':run['condition'],'run_id':run['run_id'],**row})
    with (directory/'run_inventory.csv').open('w',newline='') as handle:
        fields=['condition','conversation_id','status','run_id','expected_questions','completed_questions']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(comparison['inventory'])


def _telemetry(events):
    stages, local_actions, retrieval, prompt_usage = {}, {}, [], {}
    blocked=0
    for event in events:
        if event['type']=='generation':
            attempts=event.get('attempts') or []
            if not attempts:
                blocked+=1
                continue
            stage=stages.setdefault(event['stage'], {'logical_calls':0,'physical_attempts':0,'retry_attempts':0,
                'known_input_tokens':0,'known_output_tokens':0,'unknown_usage_attempts':0,'rejected_generations':0,
                'compatibility_deviations':0,'transformed_items':0,'logical_duration_seconds':0.0})
            stage['logical_calls']+=1; stage['physical_attempts']+=len(attempts)
            stage['retry_attempts']+=len(attempts)-1
            stage['rejected_generations']+=bool(event.get('error_type'))
            audit=event.get('compatibility_deviation')
            stage['compatibility_deviations']+=bool(audit)
            stage['transformed_items']+=len(audit.get('transformations',[])) if audit else 0
            duration=event.get('duration_seconds')
            if type(duration) in (int,float) and math.isfinite(duration) and duration>=0:
                stage['logical_duration_seconds']+=duration
            for attempt in attempts:
                usage=attempt.get('usage') or {}
                if all(type(usage.get(k)) is int and usage[k]>=0 for k in ('prompt_tokens','completion_tokens')):
                    stage['known_input_tokens']+=usage['prompt_tokens']
                    stage['known_output_tokens']+=usage['completion_tokens']
                else:stage['unknown_usage_attempts']+=1
            if event['stage']=='answer':
                prompt_usage[event.get('question_id')]=(event.get('usage') or {}).get('prompt_tokens')
        elif event['type']=='local_action':
            action=local_actions.setdefault(event['action'],{'executions':0,'duration_seconds':0.0,'api_calls':0})
            action['executions']+=1
            action['duration_seconds']+=event.get('duration_seconds',0)
            action['api_calls']+=event.get('api_calls',0)
        elif event['type']=='retrieval':
            retrieval.append({k:copy.deepcopy(v) for k,v in event.items() if k not in ('type','run_id','build_id','level')})
    for item in retrieval:item['api_final_prompt_tokens']=prompt_usage.get(item.get('question_id'))
    return {'generation_stages':stages,'local_actions':local_actions,'retrieval':retrieval,
            'blocked_generation_notices':blocked,
            'cost_note':'Exact conservative costs are source_costs; stage tokens/latency are observations, not additional charges.'}


def main():
    import argparse
    from .budget import ledger_summary

    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--phase',action='append',default=[],help='Saved phase.json; repeat for each independent cell')
    parser.add_argument('--output',required=True)
    parser.add_argument('--root',default=str(ROOT))
    parser.add_argument('--archive-root')
    args=parser.parse_args()
    root=Path(args.root).resolve(); archive_root=Path(args.archive_root or root).resolve()
    ledger=archive_root/'artifacts/study-budget.sqlite'
    comparison=assemble_comparison(_read(Path(args.manifest)),args.phase,root=root,archive_root=archive_root,
                                   study_budget=ledger_summary(ledger) if ledger.exists() else None)
    write_comparison(comparison,args.output,archive_root=archive_root)
    print(json.dumps({'status':comparison['status'],'complete_conditions':comparison['complete_conditions'],
                      'missing_cells':len(comparison['missing_cells']),'output':str(Path(args.output).resolve())}))


if __name__=='__main__':main()
