"""One isolated Run2 saved-result import. Interrupted imports resume reads only.

No runner, provider, scorer, cache writer or budget writer is imported here.
The original failed phase is evidence, never an output directory.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from .config import fingerprint
from .langfuse_verify import (
    VerificationError, _read, _retry, _proof, _check_experiments, _equal,
    _metadata, _indexed, _query_cli,
)
from .phases import _save
from .reporting import export_experiments

RECOVERY_ID = 'run2-full-conv-44-reporting-recovery-20261104-v1'
ORIGINAL_RUN = 'run2-full-conv-44-r0-p2'
POLICIES = ('author-corrected-v1', 'author-legacy-c5-v1')
BATCH_SPANS = 16
TRANSPORT_LIMIT = 64 * 1024 * 1024
# Fail before transmission, with at least 50% headroom under the existing guard.
PAYLOAD_CEILING = TRANSPORT_LIMIT // 2


def recovery_plan(views, original, original_trace_ids):
    identity = original['identity']
    required = {'campaign_id': 'amem-run2-20261103-v1', 'condition': 'full',
                'population': 'fallback', 'run_id': ORIGINAL_RUN,
                'conversation_id': 'conv-44', 'repetition': 0,
                'provider_contract_policy': 'canonical-index-strings-v1',
                'manifest_sha256': 'b9d41746ba8eac2b94d401570e9083b24ed1d3f2d20a9ece1de68600f33ad8a3'}
    _equal(required, identity, 'original/identity')
    if set(views) != set(POLICIES) or fingerprint(views) != original['results_sha256']:
        raise VerificationError('Saved views differ from the failed import')
    questions = None
    for policy, view in views.items():
        rows = view['individual_results']
        ids = [r['question_id'] for r in rows]
        if (view['scoring_policy'] != policy or len(rows) != 158
                or len(set(ids)) != 158 or any(not q.startswith('conv-44:') for q in ids)):
            raise VerificationError('Expected exactly the original158 Run2 conv-44 questions')
        if questions is not None and questions != ids:
            raise VerificationError('Scoring views have different question identities/order')
        questions = ids
    experiments = {}
    if (set(original_trace_ids) != set(questions)
            or len(set(original_trace_ids.values())) != 158
            or any(not isinstance(t, str) or len(t) != 32 for t in original_trace_ids.values())):
        raise VerificationError('All158 original QA trace associations are required')
    for policy in POLICIES:
        export_identity = {**identity, 'scoring_policy': policy, 'recovery_import_id': RECOVERY_ID}
        experiments[policy] = {
            'id': hashlib.sha256((RECOVERY_ID + '/' + policy).encode()).hexdigest()[:16],
            'name': original['experiments'][policy]['name'],
            'run_name': 'repetition-0/' + fingerprint(export_identity),
        }
    if set(r['id'] for r in experiments.values()) & set(r['id'] for r in original['experiments'].values()):
        raise VerificationError('Recovery must not reuse a consumed import identity')
    return {'recovery_import_id': RECOVERY_ID, 'identity': identity,
            'results_sha256': fingerprint(views), 'experiments': experiments,
            'from_start_time': original['from_start_time'], 'flush_at': BATCH_SPANS}


def inspect_import(imported, output, query):
    """Snapshot all visible records under the specified IDs without changing any."""
    ids = ','.join(r['id'] for r in imported['experiments'].values())
    paths = []
    common = {'from-start-time': imported['from_start_time'], 'limit': 100,
              'all': True, 'max-items': 1000}
    experiments = _read(query, 'experiments', {**common, 'id': ids,
                        'fields': 'core,metadata,scores'}, output, paths)
    items = _read(query, 'experiment-items', {**common, 'experiment-id': ids,
                  'fields': 'core,io,metadata,itemMetadata,experimentMetadata,scores',
                  'score-limit': 50}, output, paths)
    scores = _read(query, 'scores', {'experiment-id': ids, 'fields': 'details,subject',
                   'limit': 100, 'all': True, 'max-items': 6000}, output, paths)
    return experiments, items, scores, paths


def isolate_original_scores(views, original, output, query):
    """Scores can arrive even when their original experiment spans were dropped."""
    paths = []
    rows = _read(query, 'scores', {'from-timestamp': original['from_start_time'],
        'to-timestamp': '2026-11-03T14:10:00Z', 'fields': 'details,subject',
        'limit': 100, 'all': True, 'max-items': 6000}, output, paths)
    expected = Counter((p, name, value) for p, v in views.items()
                       for row in v['individual_results'] for name, value in row['metrics'].items())
    observed = Counter()
    traces = set()
    for row in rows:
        try:
            policy = json.loads(row['comment'])['scoring_policy']
            trace = row['subject']['traceId']
            observed[policy, row['name'], row['value']] += 1
            traces.add(trace)
        except (KeyError, TypeError, ValueError) as error:
            raise VerificationError('Unidentified partial score write') from error
    if observed - expected or len({r['id'] for r in rows}) != len(rows):
        raise VerificationError('Unexpected or duplicated original partial score writes')
    value = {'score_count': len(rows), 'trace_ids': sorted(traces),
             'score_ids_sha256': fingerprint(sorted(r['id'] for r in rows)),
             'readbacks': [p.name for p in paths],
             'policy': 'Preserved original partial scores are excluded from canonical recovery.'}
    _save(output / 'original-score-isolation.json', value)
    return value


def _check_associations(views, plan, items, scores, original_trace_ids):
    """Exact score cardinality, unique subjects and the original QA trace association."""
    from langfuse._client.attributes import _serialize
    all_scores = _indexed(scores, 'id', [s['id'] for i in items for s in i['scores']])
    traces = set()
    for policy, view in views.items():
        by_question = {r['question_id']: r for r in view['individual_results']}
        for item in (i for i in items if i['experimentId'] == plan['experiments'][policy]['id']):
            inp = item['input']
            if isinstance(inp, str): inp = json.loads(inp)
            row = by_question[inp['question_id']]
            expected_item_id = hashlib.sha256(_serialize(inp).encode()).hexdigest()[:16]
            _equal(expected_item_id, item.get('experimentItemId'), 'recovery/experimentItemId')
            trace = item.get('traceId')
            if not trace or trace in traces:
                raise VerificationError('Recovery item trace association is missing or duplicated')
            traces.add(trace)
            for local_score in item['scores']:
                score = all_scores[local_score['id']]
                _equal(local_score['name'], score['name'], 'score/name')
                _equal(local_score['value'], score['value'], 'score/value')
                _equal({'kind': 'observation', 'id': item['id'], 'traceId': trace},
                       score.get('subject'), 'recovery/score/subject')
            expected = {**plan['identity'], 'scoring_policy': policy,
                        'recovery_import_id': RECOVERY_ID, 'original_record': row,
                        'original_trace_id': original_trace_ids[row['question_id']],
                        **plan['original_binding']}
            _metadata(expected, item.get('experimentItemMetadata'), 'recovery/item')
            _metadata({'recovery_import_id': RECOVERY_ID, **plan['original_binding']},
                      item.get('experimentMetadata'), 'recovery/experiment')
    return len(all_scores), len(traces)


def recover(views, original, output, *, original_trace_ids, original_binding, client=None, query=None,
            attempts=6, delay_seconds=6):
    """Write at most once. After a claim, only readback is allowed, even on failure."""
    output = Path(output)
    if not output.resolve().is_relative_to(Path('artifacts/run2/reporting-recovery').resolve()):
        raise VerificationError('Recovery output must be isolated under artifacts/run2/reporting-recovery')
    output.mkdir(parents=True, exist_ok=True)
    plan = recovery_plan(views, original, original_trace_ids)
    plan['original_trace_ids'] = original_trace_ids
    plan['original_binding'] = {k: original_binding[k] for k in
        ('config_sha256', 'source_sha256', 'max_output_tokens_by_stage')}
    query = query or _query_cli
    claim = output / 'recovery-claim.json'
    if claim.exists():
        _equal(plan, json.loads(claim.read_text()), 'recovery/claim')
        isolation = json.loads((output / 'original-score-isolation.json').read_text())
    else:
        # Old writes remain noncanonical and untouched. The fresh IDs must be absent.
        old = inspect_import(original, output, query)
        fresh = inspect_import(plan, output, query)
        _save(output / 'pre-ingestion-inventory.json', {
            'original_counts': [len(v) for v in old[:3]],
            'recovery_counts': [len(v) for v in fresh[:3]],
            'old_experiments': original['experiments'], 'canonical_recovery': plan['experiments'],
            'policy': 'Retain all original writes; only fresh recovery IDs are canonical.',
            'readbacks': [p.name for p in old[3] + fresh[3]],
        })
        if any(fresh[:3]):
            raise VerificationError('Unclaimed recovery identity already has cloud writes')
        if client is None:
            raise VerificationError('An explicitly bounded reporting client is required')
        isolation = isolate_original_scores(views, original, output, query)
        _save(claim, plan)  # exclusive durable one-shot admission, before any write
        metadata = {**plan['identity'], **plan['original_binding'], 'recovery_import_id': RECOVERY_ID,
                    'observability_policy': 'run2-audit-essential-v1',
                    'supersedes_failed_import': {p: v['id'] for p, v in original['experiments'].items()}}
        results = export_experiments(views, client=client, export_authorized=True,
            metadata=metadata, experiment_ids={p: r['id'] for p, r in plan['experiments'].items()},
            original_trace_ids=original_trace_ids)
        for policy, result in results.items():
            _equal(plan['experiments'][policy]['id'], result.experiment_id, 'SDK/experiment_id')
            _equal(plan['experiments'][policy]['run_name'], result.run_name, 'SDK/run_name')
        _save(output / 'sdk-returned.json', {'experiments': {
            p: {'id': r.experiment_id, 'run_name': r.run_name, 'url': r.experiment_url,
                'item_traces': [i.trace_id for i in r.item_results]} for p, r in results.items()}})
    def operation(paths):
        experiments, items, scores, readbacks = inspect_import(plan, output, query)
        paths.extend(readbacks)
        _check_experiments(views, plan, plan['identity'], experiments, items)
        for experiment in experiments:
            _metadata(plan['original_binding'], experiment.get('metadata'), 'recovery/binding')
        if set(isolation['trace_ids']) & {i.get('traceId') for i in items}:
            raise VerificationError('Recovery overlaps original partial-write traces')
        score_count, traces = _check_associations(views, plan, items, scores, original_trace_ids)
        if fingerprint(views) != plan['results_sha256']:
            raise VerificationError('Saved views changed during recovery')
        return {'verified': True, 'recovery_import_id': RECOVERY_ID,
                'experiment_ids': {p: r['id'] for p, r in plan['experiments'].items()},
                'results_sha256': plan['results_sha256'], 'item_count': len(items),
                'score_count': score_count, 'trace_count': traces, 'identity': plan['identity'],
                'status': 'Degraded', 'original_phase_status': 'Incomplete',
                'usable_for_next_phase': False, 'model_calls': 0}
    value, paths = _retry(output, operation, attempts, delay_seconds)
    return _proof(output, 'reporting-recovery', value, paths)
