"""User-authorised representation exception for two immutable BLEU-4 observations.

This verifier has no export or inference path. The ordinary scorer and cloud
verifier remain strict. Only comparison copies of the two pinned numeric fields
are substituted after checking the complete approved identities and bit patterns.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from .budget import BudgetStop
from .config import fingerprint
from .langfuse_verify import (
    VerificationError, _check_experiments, _equal, _indexed, _metadata,
    _read, _proof, _query_cli,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'blk027-two-exact-bleu4-observations-v1'
CELL = 'neither-conv-50'
PHASE = 'gpt4omini-neither-conv50-r0-p0'
SUCCESSORS = ('neither-conv-44', 'linking_only-conv-50', 'linking_only-conv-44')
SUPPLEMENT = f'outcomes/{CELL}/blk027-acceptance/supplement.json'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rules():
    return read(ROOT/'config/blk027-acceptance.json')


def require(value, message):
    if not value:
        raise VerificationError(message)


def verify_merged_review(root, reviewed_commit, merge_commit):
    """Require a normal merge whose reviewed feature head is its second parent."""
    import subprocess
    subprocess.run(['git', 'merge-base', '--is-ancestor', merge_commit, 'HEAD'],
                   cwd=root, check=True, capture_output=True)
    subprocess.run(['git', 'merge-base', '--is-ancestor', reviewed_commit, merge_commit],
                   cwd=root, check=True, capture_output=True)
    parents = subprocess.check_output(
        ['git', 'show', '-s', '--format=%P', merge_commit], cwd=root, text=True).split()
    require(len(parents) == 2 and parents[1] == reviewed_commit,
            'Normal merge must contain the exact independently reviewed head')


def pinned_inputs(campaign):
    from .gpt4omini_campaign import verify_inventory
    policy = rules()
    verify_inventory(campaign, policy['artifact_files'])
    directory = campaign/'cells'/CELL/'runs'/PHASE
    phase = read(directory/'phase.json')
    require(phase['status'] == 'incomplete'
            and phase['error_type'] == 'VerificationError'
            and (phase['notes'], phase['questions']) == (568, 204)
            and fingerprint(phase) == policy['original_phase_canonical_sha256'],
            'BLK-027 original terminal receipt changed')
    require(not (directory/'cache-proof.json').exists()
            and not (directory/'final-memory.json').exists(),
            'Original missing receipts must not be synthesised')
    verify_inventory(directory, phase['files'])
    return policy, directory, phase


def check_readback(views, imported, experiments, items, scores, traces):
    """Verify all records, allowing only the two preselected binary64 pairs."""
    policy = rules()
    require(fingerprint(views) == policy['original_scoring_views_canonical_sha256'],
            'Original author scores changed')
    require(imported['identity']['campaign_id'] == policy['campaign_id']
            and imported['identity']['run_id'] == PHASE
            and imported['identity']['condition'] == 'neither'
            and imported['identity']['conversation_id'] == 'conv-50',
            'Exception belongs to a different execution')
    require(len(items) == policy['items'] and len(scores) == policy['scores']
            and set(traces) == {f'conv-50:qa:{n}' for n in range(204)}
            and len(set(traces.values())) == 204, 'BLK-027 full population required')
    originals = fingerprint({'views': views, 'items': items, 'scores': scores})
    comparison = copy.deepcopy(items)
    by_item = _indexed(comparison, 'id', [i['id'] for i in items])
    score_ids = [s['id'] for item in items for s in item['scores']]
    require(len(score_ids) == len(set(score_ids)) == policy['scores'],
            'Missing or duplicate score identity')
    native = _indexed(scores, 'id', score_ids)
    for pin in policy['tuples']:
        scoring_policy = pin['scoring_policy']
        require(imported['experiments'][scoring_policy]['id'] == pin['experiment_id'],
                'Exception experiment changed')
        item = by_item[pin['item_observation_id']]
        require(item['experimentId'] == pin['experiment_id']
                and item['experimentItemId'] == pin['experiment_item_id']
                and item['traceId'] == pin['experiment_trace_id'],
                'Exception item or trace changed')
        value = item['input']
        if isinstance(value, str):
            value = json.loads(value)
        require(value['question_id'] == pin['question_id']
                and traces[pin['question_id']] == pin['original_qa_trace_id'],
                'Exception question association changed')
        row = views[scoring_policy]['individual_results'][pin['original_qa_index']]
        require(fingerprint(row) == pin['original_record_sha256']
                and type(row['metrics']['bleu4']) is float
                and row['metrics']['bleu4'].hex() == pin['expected_binary64_hex'],
                'Exception original score changed')
        selected = [s for s in item['scores'] if s['id'] == pin['score_id']]
        require(len(selected) == 1, 'Exception score missing or duplicated')
        for score in (selected[0], native[pin['score_id']]):
            require(score['name'] == pin['score_name'] == 'bleu4'
                    and score['dataType'] == pin['score_data_type'] == 'NUMERIC'
                    and type(score['value']) is float
                    and score['value'].hex() == pin['allowed_remote_binary64_hex'],
                    'Unapproved numeric representation')
            _equal(pin['subject'], score.get('subject'), 'exception/subject')
        for actual in (selected[0], native[pin['score_id']]):
            for name, expected in (('projectId', pin['project_id']),
                                   ('timestamp', pin['native_timestamp']),
                                   ('source', pin['score_source']),
                                   ('environment', pin['score_environment'])):
                _equal(expected, actual.get(name), 'exception/'+name)
        selected[0]['value'] = row['metrics']['bleu4']
    # The original strict checker validates inputs, references, original-record
    # metadata, identities and every metric using the comparison copy only.
    _check_experiments(views, imported, imported['identity'], experiments, comparison)
    require(len({i['traceId'] for i in items}) == policy['items'],
            'Experiment trace identities overlap')
    for item in items:
        value = item['input']
        if isinstance(value, str):
            value = json.loads(value)
        _metadata({'original_trace_id': traces[value['question_id']]},
                  item.get('experimentItemMetadata'), 'item/QA-trace')
        for score in item['scores']:
            actual = native[score['id']]
            _equal(score['name'], actual.get('name'), 'score/name')
            _equal(score['value'], actual.get('value'), 'score/value')
            _equal({'kind': 'observation', 'id': item['id'], 'traceId': item['traceId']},
                   actual.get('subject'), 'score/subject')
    require(fingerprint({'views': views, 'items': items, 'scores': scores}) == originals,
            'Verifier modified original evidence')
    return {'verified': True, 'policy': POLICY, 'items': len(items),
            'scores': len(scores), 'exact_scores': len(scores)-2,
            'original_qa_traces': len(traces), 'exceptions': policy['tuples']}


def verify_remote(campaign, output, *, query=None):
    """Fresh GET-only readback into a separate immutable evidence namespace."""
    from .gpt4omini_reporting import original_qa_traces
    _, directory, _ = pinned_inputs(campaign)
    imported = read(directory/'langfuse-imported.json')
    views = read(directory/'scoring-views.json')
    traces = original_qa_traces(read(directory/'trace-capture.json'))
    query = query or _query_cli
    paths = []
    common = {'from-start-time': imported['from_start_time'], 'limit': 100,
              'all': True, 'max-items': 1000}
    ids = ','.join(r['id'] for r in imported['experiments'].values())
    experiments = _read(query, 'experiments', {**common, 'id': ids,
                        'fields': 'core,metadata,scores'}, output, paths)
    items = _read(query, 'experiment-items', {**common, 'experiment-id': ids,
                  'fields': 'core,io,metadata,itemMetadata,experimentMetadata,scores',
                  'score-limit': 50}, output, paths)
    scores = []
    trace_ids = sorted({i['traceId'] for i in items})
    for start in range(0, len(trace_ids), 50):
        scores += _read(query, 'scores', {'trace-id': ','.join(trace_ids[start:start+50]),
                        'fields': 'details,subject', 'limit': 100, 'all': True,
                        'max-items': 1000}, output, paths)
    result = check_readback(views, imported, experiments, items, scores, traces)
    pinned_inputs(campaign)
    return _proof(output, 'blk027-readback', result, paths)


def verify_supplement(campaign, *, evidence=True):
    """Require the separate supplement; never reinterpret or update phase.json."""
    from .gpt4omini_campaign import verify_inventory
    policy = rules()
    value = read(campaign/SUPPLEMENT)
    require(value['policy'] == POLICY and value['cell'] == CELL
            and value['phase'] == PHASE and value['accepted'] is True
            and value['classification'] == 'Degraded'
            and value['original_phase_sha256'] == policy['original_phase_file_sha256']
            and value['original_phase_seal'] == policy['original_phase_canonical_sha256']
            and value['exceptions'] == policy['tuples']
            and value['cache_proof'] == f'outcomes/{CELL}/blk027-acceptance/cache-proof.json',
            'Unapproved reporting acceptance supplement')
    if evidence:
        import subprocess
        require(fingerprint(value['verification_source']) == value['verification_source_sha256'],
                'Verification source fingerprint changed')
        verify_merged_review(ROOT, value['reviewed_commit'], value['merge_commit'])
        require(set(value['verifier_scripts']) ==
                {'scripts/gpt4omini-blk027-accept.py', 'scripts/safe_service_audit.py'},
                'Supplement omitted a reviewed verifier script')
        for name,digest in {**value['verification_source']['files'], **value['verifier_scripts']}.items():
            blob = subprocess.check_output(['git','show',value['reviewed_commit']+':'+name],cwd=ROOT)
            require(hashlib.sha256(blob).hexdigest()==digest, 'Supplement verifier was not reviewed')
        for axis in ('spec','standards'):
            name=f'verification/blk027-release/baseline-{axis}-review.json'
            review=read(campaign/name)
            require(value['files'].get(name)==sha(campaign/name) and review['verdict']=='pass'
                    and review['reviewed_commit']==value['reviewed_commit']
                    and review['source_sha256']==value['verification_source_sha256'],
                    'Supplement release review changed')
        _, directory, _ = pinned_inputs(campaign)
        require(set(policy['artifact_files']) | {value['readback_proof'], value['cache_proof'],
                'verification/blk027-release/full-suite.txt'}
                <= value['files'].keys(), 'Supplement omitted protected evidence')
        verify_inventory(campaign, value['files'])
        proof = read(campaign/value['readback_proof'])
        require(proof['verified'] is True and proof['policy'] == POLICY
                and (proof['items'], proof['scores'], proof['exact_scores'],
                     proof['original_qa_traces']) == (408, 5804, 5802, 204)
                and proof['exceptions'] == policy['tuples'], 'Incomplete exception readback')
        from .gpt4omini_reporting import original_qa_traces
        captured = {'experiments': [], 'experiment-items': [], 'scores': []}
        for name, digest in proof['readback_files'].items():
            path = (campaign/value['readback_proof']).parent/name
            require(path.parent == (campaign/SUPPLEMENT).parent
                    and value['files'].get(str(path.relative_to(campaign))) == digest,
                    'Foreign or unbound supplementary readback')
            saved = read(path)
            captured[saved['resource']].extend(saved['body']['data'])
        check_readback(read(directory/'scoring-views.json'), read(directory/'langfuse-imported.json'),
                       captured['experiments'], captured['experiment-items'], captured['scores'],
                       original_qa_traces(read(directory/'trace-capture.json')))
        require(value['runtime']['verified'] is True and value['runtime']['observation_count'] == 2727,
                'Runtime readback incomplete')
    return value


def retained_terminal(campaign, db, approval):
    """Recognize one reporting-only terminal phase, never a halt or unknown."""
    from .openrouter import approval_cell
    digest = approval.get('reporting_acceptance_sha256')
    if digest is None:
        return None
    require(approval_cell(approval) in SUCCESSORS
            and sha(campaign/SUPPLEMENT) == digest,
            'Foreign reporting acceptance approval')
    value = verify_supplement(campaign, evidence=False)
    row = db.execute('SELECT state,seal FROM phases WHERE id=?', (PHASE,)).fetchone()
    require(row == ('terminal', value['original_phase_seal'])
            and not db.execute('SELECT 1 FROM halts WHERE phase=?', (PHASE,)).fetchone()
            and db.execute("SELECT COUNT(*) FROM attempts WHERE phase=? AND state='settled'",
                           (PHASE,)).fetchone()[0] == 1544
            and not db.execute("SELECT 1 FROM attempts WHERE phase=? AND state!='settled'",
                               (PHASE,)).fetchone(),
            'Reporting exception cannot excuse a financial or provider failure')
    return PHASE
