"""One incident's financial upper-bound decision; never evidence of paid authority.

The fixed original attempt remains unknown. Neither this receipt nor a successful
retry supplies its missing usage. All original rows and archive files are read-only.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import uuid

from .budget import BudgetStop
from .config import fingerprint

POLICY = 'run2-blk022-attempt454-upper-bound-v1'
CHECKPOINT_POLICY = 'run2-blk022-exact227-state-v1'
PARENT_RUN = 'run2-full-conv-44-r0-p0'
PARENT_APPROVAL = '15f24bf6-aefb-4737-8bbd-a093cfc7d82d'
PARENT_RECEIPT = '517ce475e6b9b7e3de6d566c35d79b85d8c44630f00a6b6959910551963fe384'
CAMPAIGN_SHA256 = 'e434a3752119f537ab5546b45e3a36ca81d97561ceca077535a4586b17414500'
REQUEST_SHA256 = 'bf588f2e1ff4ad369525bd3ac534313c6dc60b4326a70aa7929037077ff23c25'
BODY_SHA256 = 'd7d8c143e67422705f5853ff845df3eca2503bbb5b29a0b26b939f7dcbccce3b'
PREFIX = {
    'phases': '0647646a4f7251c8ea9fdba691688d6d55f25cd390899470d23bf9c2241122d8',
    'logical_calls': 'ba14d6f6f97e967a3520047a667152bc74aaf91ac1b777d8ff5084801bb7daa9',
    'attempts': '2070c35c82de441b2a3731e24e28b82defb540889b4a24b39f736055e821bb12',
    'run2_phases': '25d9e4225a5ced5f4efd78f786f86d37c99423e50d48970d59a6d1b35901b817',
    'run2_campaign': 'ca8d03debcd9847e831d28ceefbc023623e024444d14d372917e2fe88ae3ca41',
}
ACCOUNTING = {
    'unknown_attempts': 1, 'unadjudicated_unknown_attempts': 0,
    'retained_unknown_microusd': 324404, 'known_settled_microusd': 720433,
    'charged_or_reserved_microusd': 1044837,
    'original_cell_cap_microusd': 5000000, 'remaining_cell_cap_microusd': 3955163,
}
BINDING = {
    'campaign_sha256': CAMPAIGN_SHA256, 'parent_run_id': PARENT_RUN,
    'parent_approval_id': PARENT_APPROVAL, 'parent_receipt_sha256': PARENT_RECEIPT,
    'attempt_id': 454, 'logical_id': 454, 'status': 'unknown', 'usage_json': 'null',
    'charge_microusd': 324404, 'reservation_microusd': 324404,
    'request_sha256': REQUEST_SHA256, 'body_sha256': BODY_SHA256,
    'ledger_prefix_sha256': PREFIX,
}


def _ledger(root):
    path = Path(root).resolve() / 'artifacts/run2/budget.sqlite'
    return sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)


def _check_prefix(db):
    for table, expected in PREFIX.items():
        where = '' if table == 'run2_campaign' else ' WHERE approval_id=?'
        params = () if not where else (PARENT_APPROVAL,)
        cursor = db.execute('SELECT * FROM ' + table + where + ' ORDER BY 1', params)
        columns = [c[0] for c in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor]
        if fingerprint(rows) != expected:
            raise BudgetStop('BLK-022 immutable ledger prefix differs')
    cell = db.execute('SELECT root_approval FROM run2_cells WHERE cell_index=0').fetchone()
    if cell != (PARENT_APPROVAL,):
        raise BudgetStop('BLK-022 original cell ownership differs')


def _check_approval(approval, *, approved=True):
    from .run2 import _approved
    if not isinstance(approval, dict):
        raise BudgetStop('BLK-022 financial approval is malformed')
    if approved:
        _approved(approval)
    allowed = {'kind', 'policy', 'approval_id', 'approved', 'approved_by', 'approved_at',
               'scope', 'paid_execution_authorized', 'binding', 'accounting'}
    if (set(approval) != allowed or approval.get('kind') != 'financial_adjudication'
            or approval.get('policy') != POLICY or approval.get('scope') != 'financial_only'
            or approval.get('paid_execution_authorized') is not False
            or fingerprint(approval.get('binding')) != fingerprint(BINDING)
            or fingerprint(approval.get('accounting')) != fingerprint(ACCOUNTING)):
        raise BudgetStop('BLK-022 financial approval differs from the fixed retained upper bound')
    fingerprint(approval)


def validate_financial_receipt(receipt):
    """Validate the standalone decision without treating it as a phase approval."""
    if not isinstance(receipt, dict) or set(receipt) != {
            'policy', 'financial_approval', 'financial_approval_sha256', 'accounting',
            'paid_execution_authorized'}:
        raise BudgetStop('BLK-022 financial receipt is malformed')
    approval = receipt['financial_approval']
    _check_approval(approval)
    if (receipt['policy'] != POLICY or receipt['financial_approval_sha256'] != fingerprint(approval)
            or fingerprint(receipt['accounting']) != fingerprint(ACCOUNTING)
            or receipt['paid_execution_authorized'] is not False):
        raise BudgetStop('BLK-022 financial receipt differs from its approval')
    return receipt


def adjudicated_unknown_ids(db, receipt):
    """Only attempt454 can be admitted; every additional unknown remains blocking."""
    if receipt is None:
        return set()
    validate_financial_receipt(receipt)
    _check_prefix(db)
    return {454}


def unknown_counts(db, receipt=None):
    allowed = adjudicated_unknown_ids(db, receipt)
    ids = {row[0] for row in db.execute("SELECT id FROM attempts WHERE status!='settled'")}
    return {'unknown_attempts': len(ids),
            'unadjudicated_unknown_attempts': len(ids - allowed)}


def _check_original(root, campaign):
    from .run2 import _read_phase_archive, _read_lines
    if fingerprint(campaign) != CAMPAIGN_SHA256:
        raise BudgetStop('BLK-022 financial decision belongs to another campaign')
    path, phase = _read_phase_archive(
        Path(root) / 'artifacts/run2/runs' / PARENT_RUN / 'phase.json', root)
    if fingerprint(phase) != PARENT_RECEIPT:
        raise BudgetStop('BLK-022 original parent receipt differs')
    with _ledger(root) as db:
        _check_prefix(db)
    events = _read_lines(path.parent / 'events.jsonl')
    shared = [e for e in events if e.get('budget_logical_id') == 454]
    if len(shared) != 1:
        raise BudgetStop('BLK-022 original retry journal differs')
    attempt, retry = shared[0]['attempts']
    if (shared[0]['stage'] != 'shared_decision' or shared[0]['turn_id'] != 'D10:10'
            or attempt.get('budget_attempt_id') != 454 or attempt.get('usage') is not None
            or attempt.get('status_code') != 200 or attempt.get('error_type') != 'RemoteProtocolError'
            or retry.get('budget_attempt_id') != 455 or retry.get('error_type') is not None
            or any(fingerprint(a['request_body'])
                   != BODY_SHA256 for a in (attempt, retry))):
        raise BudgetStop('BLK-022 original request/body/retry evidence differs')
    return phase


def plan_financial_adjudication(*, root, campaign):
    """Return an unapproved financial-only decision, without opening a writable ledger."""
    _check_original(root, campaign)
    return {'kind': 'financial_adjudication', 'policy': POLICY,
            'approval_id': str(uuid.uuid4()), 'approved': False,
            'approved_by': None, 'approved_at': None, 'scope': 'financial_only',
            'paid_execution_authorized': False, 'binding': copy.deepcopy(BINDING),
            'accounting': copy.deepcopy(ACCOUNTING)}


def verify_financial_adjudication(approval, *, root, campaign):
    """Produce a deterministic receipt for the reviewed, fixed financial decision."""
    _check_approval(approval)
    _check_original(root, campaign)
    receipt = {'policy': POLICY, 'financial_approval': copy.deepcopy(approval),
               'financial_approval_sha256': fingerprint(approval),
               'accounting': copy.deepcopy(ACCOUNTING), 'paid_execution_authorized': False}
    from .run2 import _verify_attempt_journal
    with _ledger(root) as db:
        _verify_attempt_journal(db, 0, financial_adjudication=receipt)
        if unknown_counts(db, receipt)['unadjudicated_unknown_attempts']:
            raise BudgetStop('BLK-022 has another unknown charge; no financial admission')
    return receipt


def verify_exact_checkpoint(path, *, root, campaign, manifest, sources, receipt,
                            financial_adjudication, support_migration=None, allow_consumed=False):
    """Restore the sole approved prefix; the final valid decision is never replayed."""
    import numpy as np
    from .artifacts import _validate_state
    from .run2 import _read, _read_lines, _read_phase_archive, _cell_history, _verify_attempt_journal
    root = Path(root).resolve()
    path, phase = _read_phase_archive(path, root)
    validate_financial_receipt(financial_adjudication)
    _check_original(root, campaign)
    if fingerprint(phase) != PARENT_RECEIPT:
        raise ValueError('BLK-022 only permits the fixed original parent, not another recovery')
    events = _read_lines(path.parent / 'events.jsonl')
    archived_sources = events[0]['source_hashes']
    archived_preflight = _read(path.parent / 'preflight.json')
    if support_migration is None:
        if sources != archived_sources or receipt != archived_preflight:
            raise ValueError('BLK-022 source migration requires an explicit reviewed commit')
    else:
        expected = verify_support_migration(root=root, campaign=campaign, sources=sources,
            receipt=receipt, financial_adjudication=financial_adjudication,
            reviewed_commit=support_migration.get('reviewed_commit'))
        if support_migration != expected:
            raise ValueError('BLK-022 reviewed source migration differs')
    conversation = next(c for c in manifest['conversations'] if c['original_id'] == 'conv-44')
    partial = _read(path.parent / 'partial-memory.json')
    identity, state = partial['identity'], partial['state']
    _validate_state(state)
    turns = [e for e in events if e['type'] == 'evolution_outcome']
    emb = np.asarray(state['retriever']['embeddings'], dtype=state['retriever']['embedding_dtype'])
    if (manifest != events[0]['manifest'] or partial.get('complete') is not False
            or len(state['notes']) != 227 or len(state['outcomes']) != 227 or len(turns) != 227
            or [e['turn_id'] for e in turns] != conversation['turn_ids'][:227]
            or [o['turn_id'] for o in state['outcomes']] != conversation['turn_ids'][:227]
            or conversation['turn_ids'][227] != 'D10:11'
            or emb.shape != (227, 384) or str(emb.dtype) != 'float32' or not np.isfinite(emb).all()
            or state['evo_cnt'] != 226 or state['evo_threshold'] != 100
            or identity['source_hashes'] != archived_sources
            or identity['conversation'] != conversation
            or identity['dataset_sha256'] != manifest['dataset_sha256']):
        raise ValueError('BLK-022 exact ordered memory/index/counter prefix differs')
    from .config import RUN2_CONFIG, INDEX_STRING_POLICY
    if (identity['configuration'] != RUN2_CONFIG or identity['condition'] != 'full'
            or identity['provider_contract_policy'] != INDEX_STRING_POLICY):
        raise ValueError('BLK-022 scientific checkpoint identity differs')
    for saved, event in zip(state['outcomes'], turns):
        if saved != {key: event[key] for key in saved}:
            raise ValueError('BLK-022 evolution outcomes differ from the original journal')
    # The sealed inventory pins all fields above and the final original arguments;
    # additionally prove the failed admission itself made no model request.
    last = [e for e in events if e['type'] == 'generation'][-1]
    if (last.get('turn_id') != 'D10:11' or last.get('stage') != 'metadata'
            or last.get('attempts') or last.get('error_type') != 'BudgetStop'
            or turns[-1]['turn_id'] != 'D10:10' or turns[-1]['counter_after'] != 226):
        raise ValueError('BLK-022 next original turn was already transmitted')
    with _ledger(root) as db:
        _check_prefix(db)
        cell, rows = _cell_history(db, 0, campaign)
        if not allow_consumed and (cell != (PARENT_APPROVAL, PARENT_APPROVAL, 0) or len(rows) != 1):
            raise ValueError('BLK-022 parent is no longer the exclusive unconsumed leaf')
        if not allow_consumed and db.execute('SELECT 1 FROM checkpoint_claims WHERE parent_phase_sha256=?',
                      (PARENT_RECEIPT,)).fetchone():
            raise ValueError('BLK-022 parent checkpoint was already claimed')
        _verify_attempt_journal(db, 0, financial_adjudication=financial_adjudication)
        if unknown_counts(db, financial_adjudication)['unadjudicated_unknown_attempts']:
            raise BudgetStop('BLK-022 has another unknown charge')
    approval = _read(path.parent / 'approval.json')
    lineage = {'policy': CHECKPOINT_POLICY, 'campaign_id': phase['campaign_id'],
        'condition': 'full', 'conversation_id': 'conv-44', 'parent_run_id': PARENT_RUN,
        'parent_approval_id': PARENT_APPROVAL, 'parent_receipt_sha256': PARENT_RECEIPT,
        'parent_snapshot_sha256': phase['artifact_sha256']['partial-memory.json'],
        'parent_events_sha256': phase['artifact_sha256']['events.jsonl'],
        'completed_turns': 227, 'next_turn_id': 'D10:11', 'remaining_logical_calls': 1212,
        'ancestor_receipts': [{'run_id': PARENT_RUN, 'approval_id': PARENT_APPROVAL,
            'receipt_sha256': PARENT_RECEIPT, 'approval_sha256': fingerprint(approval)}]}
    return {'lineage': lineage, 'state': copy.deepcopy(state),
            'failures': copy.deepcopy([e for e in events if e['type'] == 'failure'])}


MIGRATION_POLICY = 'run2-blk022-explicit-reviewed-support-v1'
MIGRATION_FILES = {'amem_repro/run2.py', 'amem_repro/run2_blk022.py'}
OBSERVED_MIGRATION_POLICY = 'run2-blk022-observed-support-v2'
OBSERVED_FILES = MIGRATION_FILES | {'amem_repro/observability.py',
    'amem_repro/langfuse_verify.py', 'amem_repro/observation_policy.py'}
FALLBACK_MIGRATION_POLICY = 'run2-original-fallback-reviewed-support-v3'
FALLBACK_FILES = OBSERVED_FILES | {'amem_repro/adapter.py', 'amem_repro/runner.py',
                                  'amem_repro/evolution_fallback.py'}


def validate_support_migration(value, financial_adjudication, campaign):
    """Check phase-bound pins; the runtime additionally verifies every Git blob."""
    validate_financial_receipt(financial_adjudication)
    fallback = isinstance(value, dict) and value.get('policy') == FALLBACK_MIGRATION_POLICY
    observed = fallback or isinstance(value, dict) and value.get('policy') == OBSERVED_MIGRATION_POLICY
    fields = {
            'policy', 'reviewed_commit', 'original_source_sha256', 'candidate_source_sha256',
            'original_preflight_sha256', 'candidate_preflight_sha256',
            'financial_receipt_sha256', 'changed_files'} | ({'observability'} if observed else set()) | ({'evolution_failure_policy'} if fallback else set())
    if not isinstance(value, dict) or set(value) != fields:
        raise BudgetStop('BLK-022 support migration is malformed')
    if (value['policy'] != (FALLBACK_MIGRATION_POLICY if fallback else OBSERVED_MIGRATION_POLICY if observed else MIGRATION_POLICY)
            or not isinstance(value['reviewed_commit'], str)
            or not re.fullmatch('[0-9a-f]{40}', value['reviewed_commit'])
            or value['original_source_sha256'] != campaign['binding']['source_sha256']
            or value['original_preflight_sha256'] != campaign['binding']['preflight_sha256']
            or value['financial_receipt_sha256'] != fingerprint(financial_adjudication)
            or value['changed_files'] != sorted(FALLBACK_FILES if fallback else OBSERVED_FILES if observed else MIGRATION_FILES)
            or any(not isinstance(value[key], str) or not re.fullmatch('[0-9a-f]{64}', value[key])
                   for key in ('candidate_source_sha256', 'candidate_preflight_sha256'))):
        raise BudgetStop('BLK-022 support migration differs from the narrow reviewed policy')
    if fallback:
        from .evolution_fallback import POLICY_ID
        if value['evolution_failure_policy'] != POLICY_ID:
            raise BudgetStop('Original evolution fallback policy differs')
    if observed:
        from .observation_policy import POLICY_ID
        policy = value['observability']
        if (not isinstance(policy, dict) or set(policy) != {
                'policy', 'gate_sha256', 'credential_receipt_sha256', 'execution_script_sha256'}
                or policy['policy'] != POLICY_ID
                or any(not isinstance(policy[k], str) or not re.fullmatch('[0-9a-f]{64}', policy[k])
                       for k in policy if k != 'policy')):
            raise BudgetStop('BLK-022 observability release binding is invalid')


def verify_support_migration(*, root, campaign, sources, receipt,
                             financial_adjudication, reviewed_commit):
    """An explicit reviewed commit may change only the named support files."""
    from .run2 import _read, _read_lines
    if not isinstance(reviewed_commit, str) or not re.fullmatch('[0-9a-f]{40}', reviewed_commit):
        raise ValueError('BLK-022 support migration requires a full immutable reviewed commit SHA')
    validate_financial_receipt(financial_adjudication)
    if fingerprint(campaign) != CAMPAIGN_SHA256:
        raise ValueError('BLK-022 support migration belongs to another campaign')
    directory = Path(root) / 'artifacts/run2/runs' / PARENT_RUN
    archived = _read_lines(directory / 'events.jsonl')[0]['source_hashes']
    original_receipt = _read(directory / 'preflight.json')
    if (fingerprint(archived) != campaign['binding']['source_sha256']
            or fingerprint(original_receipt) != campaign['binding']['preflight_sha256']
            or sources.get('author_revision') != archived['author_revision']
            or set(sources.get('files', {})) not in (
                set(archived['files']) | {'amem_repro/run2_blk022.py'},
                set(archived['files']) | {'amem_repro/run2_blk022.py', 'amem_repro/observation_policy.py'},
                set(archived['files']) | {'amem_repro/run2_blk022.py', 'amem_repro/observation_policy.py', 'amem_repro/evolution_fallback.py'})):
        raise ValueError('BLK-022 original scientific/source inventory changed')
    changed = {name for name, digest in sources['files'].items()
               if digest != archived['files'].get(name)}
    if changed not in (MIGRATION_FILES, OBSERVED_FILES, FALLBACK_FILES):
        raise ValueError('BLK-022 migration changed files outside the named reviewed support files')
    if (receipt.get('source_sha256') != fingerprint(sources)
            or receipt.get('assets') != original_receipt['assets']
            or receipt.get('runtime', {}).get('ok') is not True
            or receipt.get('runtime', {}).get('network_disabled') is not True
            or receipt.get('paid_execution_authorized') is not False):
        raise ValueError('BLK-022 candidate preflight/assets are missing or changed')
    try:
        kind = subprocess.check_output(['git', 'cat-file', '-t', reviewed_commit], cwd=root,
                                       stderr=subprocess.DEVNULL, text=True).strip()
        if kind != 'commit':
            raise ValueError('BLK-022 reviewed reference must be a commit')
        for name, digest in sources['files'].items():
            blob = subprocess.check_output(['git', 'show', f'{reviewed_commit}:{name}'],
                                            cwd=root, stderr=subprocess.DEVNULL)
            if hashlib.sha256(blob).hexdigest() != digest:
                raise ValueError('BLK-022 candidate sources differ from the explicit reviewed commit')
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError('BLK-022 reviewed source commit is unavailable') from error
    result = {'policy': MIGRATION_POLICY, 'reviewed_commit': reviewed_commit,
        'original_source_sha256': fingerprint(archived), 'candidate_source_sha256': fingerprint(sources),
        'original_preflight_sha256': fingerprint(original_receipt), 'candidate_preflight_sha256': fingerprint(receipt),
        'financial_receipt_sha256': fingerprint(financial_adjudication), 'changed_files': sorted(changed)}
    if changed in (OBSERVED_FILES, FALLBACK_FILES):
        from .observation_policy import release_binding, LAUNCHER
        result['policy'] = OBSERVED_MIGRATION_POLICY
        result['observability'] = release_binding(root, fingerprint(sources))
        try:
            script = subprocess.check_output(['git', 'show', f'{reviewed_commit}:{LAUNCHER}'],
                                             cwd=root, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError) as error:
            raise ValueError('Reviewed one-cell launcher is unavailable') from error
        if hashlib.sha256(script).hexdigest() != result['observability']['execution_script_sha256']:
            raise ValueError('One-cell launcher differs from the reviewed commit')
        if changed == FALLBACK_FILES:
            from .evolution_fallback import POLICY_ID
            result.update(policy=FALLBACK_MIGRATION_POLICY, evolution_failure_policy=POLICY_ID)
            gate = _read(Path(root)/'artifacts/run2/observed-recovery/gate-b'/fingerprint(sources)/'receipt.json')
            if gate.get('malformed_fallback_verified') is not True:
                raise ValueError('Actual-runner malformed fallback cloud evidence is missing')
    validate_support_migration(result, financial_adjudication, campaign)
    return result


def main():
    """Offline-only immutable artifact preparation; no executor or client is exposed."""
    import argparse
    from .phases import _save
    from .run2 import _read, plan_phase
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('plan-adjudication', 'verify-adjudication', 'plan-child'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--financial-approval', type=Path)
    parser.add_argument('--preflight', type=Path)
    parser.add_argument('--assets', type=Path)
    parser.add_argument('--support-reference')
    args = parser.parse_args()
    campaign = _read(args.campaign)
    if args.operation == 'plan-adjudication':
        result = plan_financial_adjudication(root=args.root, campaign=campaign)
    else:
        if args.financial_approval is None:
            parser.error('--financial-approval is required')
        financial = verify_financial_adjudication(_read(args.financial_approval), root=args.root, campaign=campaign)
        if args.operation == 'verify-adjudication':
            result = financial
        else:
            if args.preflight is None or args.assets is None or args.support_reference is None:
                parser.error('plan-child needs --preflight, --assets and --support-reference')
            result = plan_phase(campaign, _read(args.preflight), args.assets, root=args.root,
                condition='full', conversation_id='conv-44',
                parent=args.root / 'artifacts/run2/runs' / PARENT_RUN / 'phase.json',
                financial_adjudication=financial, support_reference=args.support_reference)
    _save(args.output, result)


if __name__ == '__main__':
    main()
