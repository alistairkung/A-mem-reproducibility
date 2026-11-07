"""One approved transport recovery for the stopped Linking Only / conv-44 cell."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

from .budget import BudgetStop
from .config import fingerprint, source_fingerprint

PARENT = 'gpt4omini-linking_only-conv44-r0-p0'
CHILD = 'gpt4omini-linking_only-conv44-r0-p1'
CELL = Path('cells/linking_only-conv-44')
RELEASE_PATH = CELL / 'frozen/linking44-recovery-release.json'
RECONSTRUCTION_PATH = CELL / 'frozen/linking44-reconstruction.json'
PARENT_PATH = CELL / 'runs' / PARENT / 'phase.json'
STOP_CLOSE = Path('verification/blk027-release/stop-linking44-finance/receipt.json')
STOP_CLOSE_SHA = 'f6b8d90b9bba780e9c0fb4fd9ef23314b7b51fd2c053c15a72d8eb9a9b629797'
PARENT_SEAL = '97dbd9f331503b15d97a73d7b3f210a0c4ed13363b0bfe33e63fedbc4e2b32aa'
PARENT_FILE_SHA = '65d8f6a672863bdfbc2a5d5a6d5d95b3fd25c0a2b9b2dfd8cbef53032c80917b'
PARENT_SQL = '7225636ba5352c6ae3c2f0570ae8cbd2f2b89b03509b80b9e312a249d0dd8681'
STOP_SQL = '0655aa81ab199b60094e07fb14c20122eed232ba2dfbb7b9786a59c7b3b8917e'
FRONTIER = '01692a4e78c27e7ee9fe67e63d9a5b858ab5540dfacf3c679c1d82ffd2b63d67'
REPORTING = '7858b88ca5df5dbbe13ad36aaa05c860e8f8d2c4e1af14fe1387dc91d5ada012'
ACCESS = '3b3bb2e36098b84f5881e65079a23943427ea3276216f731adb0d590a37a32f1'
RELEASE_KEY = 'linking44_recovery_release_sha256'
STAGES = ('metadata', 'shared_decision') * 443 + ('query_keywords', 'answer') * 158
RECOVERY_LIMITS = {
    'cell_microusd': 5_000_000, 'service_reserve_microusd': 1_080_000,
    'max_new_langfuse_units': 12_345, 'child_model_microusd': 3_791_333,
    'child_service_microusd': 987_600, 'child_combined_microusd': 4_778_933,
    'max_child_calls': 1202, 'max_baseline_calls': 1666,
    'usable_campaign_microusd': 42_000_000, 'protected_microusd': 8_000_000,
}


def require(ok, message):
    if not ok:
        raise BudgetStop(message)


def bound_bytes(root, relative, digest):
    path = root / relative
    require(path.resolve() == path and path.is_file() and path.stat().st_nlink == 1,
            'Recovery evidence must use its original regular path')
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'Recovery evidence digest changed')
    return raw


def signature(path):
    stat = path.stat()
    require(path.resolve() == path and stat.st_nlink == 1, 'Aliased recovery evidence')
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def review_files(campaign, release):
    from .blk027 import verify_merged_review

    code_root = Path(__file__).resolve().parents[1]
    verify_merged_review(code_root, release['reviewed_commit'], release['merge_commit'])
    paths = []
    for axis in ('spec', 'standards'):
        evidence = Path('verification/linking44-release')
        review_path = evidence / f'baseline-{axis}-review.json'
        proof_path = evidence / f'reconstruction-{axis}.json'
        def bound_review(path):
            key = (Path('artifacts/gpt4omini') / path).as_posix()
            return json.loads(bound_bytes(campaign, path, release['files'].get(key)))
        review, proof = bound_review(review_path), bound_review(proof_path)
        require(review.get('verdict') == 'pass' and review.get('reviewed_commit') == release['reviewed_commit']
                and review.get('source_sha256') == proof.get('source_sha256') == release['binding']['source_sha256']
                and proof.get('verified') is True and proof.get('reconstruction_sha256') == release['reconstruction_sha256'],
                'Financial approval does not bind independently reviewed reconstruction/source')
        paths.extend((review_path, proof_path))
    return paths


def verify_release(ledger, db, approval):
    """Run at physical claim or for a pre-claim financial exposure check."""
    require(approval.get('phase') == CHILD and approval.get('parent') == PARENT
            and approval.get('parent_seal') == PARENT_SEAL and approval.get('kind') == 'baseline'
            and approval.get('approved') is True and not approval.get('access_retest')
            and approval.get('condition') == 'linking_only' and approval.get('conversation') == 'conv-44'
            and approval.get('retained_access_prefix') == ACCESS
            and approval.get('previous_acceptance_sha256') == FRONTIER
            and approval.get('reporting_acceptance_sha256') == REPORTING
            and approval.get('parent_path') == str(ledger.root / PARENT_PATH),
            'Recovery is restricted to the one approved final child')
    release = json.loads(bound_bytes(ledger.root, RELEASE_PATH, approval.get(RELEASE_KEY)))
    binding = approval['binding']
    require(release.get('approved') is True and release.get('phase') == CHILD
            and release.get('parent') == PARENT and release.get('parent_seal') == PARENT_SEAL
            and release.get('binding') == binding and binding == ledger.binding
            and release.get('limits') == RECOVERY_LIMITS
            and approval.get('release_sha256') == fingerprint(release), 'Recovery release differs')
    parent = json.loads(bound_bytes(ledger.root, PARENT_PATH, PARENT_FILE_SHA))
    require(binding == {**parent['binding'], 'source_sha256': binding['source_sha256']},
            'Recovery changed parent scientific binding')
    require(binding['source_sha256'] == fingerprint(source_fingerprint(Path(__file__).resolve().parents[1])),
            'Recovery source differs from the release')
    require(fingerprint(ledger.access_snapshot(db, exclude_phase=CHILD)) == STOP_SQL,
            'Stopped financial history changed')
    bound_bytes(ledger.root, RECONSTRUCTION_PATH, release.get('reconstruction_sha256'))
    bound_bytes(ledger.root, STOP_CLOSE, STOP_CLOSE_SHA)
    paths = (RELEASE_PATH, RECONSTRUCTION_PATH, PARENT_PATH, STOP_CLOSE, *review_files(ledger.root, release))
    return {ledger.root / path: signature(ledger.root / path) for path in paths}


def check_parent(db):
    """Other historical cells are checked by the existing predecessor prefix guard."""
    parent = {
        'phases': db.execute('SELECT * FROM phases WHERE id=?', (PARENT,)).fetchall(),
        'attempts': db.execute('SELECT * FROM attempts WHERE phase=? ORDER BY id', (PARENT,)).fetchall(),
        'halts': db.execute('SELECT * FROM halts WHERE phase=?', (PARENT,)).fetchall(),
    }
    require(fingerprint(parent) == PARENT_SQL, 'Retained parent or unknown 17286 changed')


def admit_request(db, stage, request):
    count = db.execute('SELECT COUNT(*) FROM attempts WHERE phase=?', (CHILD,)).fetchone()[0]
    require(count < len(STAGES) and stage == STAGES[count], 'Wrong recovery request stage or count')
    request_hash = fingerprint(request)
    require(not db.execute('SELECT 1 FROM attempts WHERE id IN (17285,17286) AND request_hash=?',
                           (request_hash,)).fetchone(), 'Cannot resend either partial-turn request')


def verify_opening(campaign, account):
    """Compare newly supplied redacted account/key GETs with the exact stopped close."""
    from scripts.gpt4omini_finance import compare
    previous = json.loads(bound_bytes(Path(campaign), STOP_CLOSE, STOP_CLOSE_SHA))
    known = previous['campaign_identified_model_usd']
    change = compare(previous['closing'], account, known, known)
    require(change['verified'] and previous['closing'] == account,
            'Account/key movement or limit differs from the stopped close')
    funds = Decimal(account['credits']['total_credits']) - Decimal(account['credits']['total_usage'])
    require(funds >= 13 and Decimal(account['key']['limit_remaining']) >= 5,
            'Insufficient prepaid balance or key limit')
    return {'account': account, 'reported_cost_usd': known, 'previous_snapshot': str(STOP_CLOSE),
            'previous_snapshot_sha256': STOP_CLOSE_SHA, 'movement': change}


def reconcile_child(client, ledger, output, opening):
    """Verify only the new known IDs, retaining all four unresolved reservations."""
    from .openrouter import save_new
    from scripts.gpt4omini_finance import compare, snapshot, verify_generations
    from uuid import uuid4

    require(opening == verify_opening(ledger.root, opening['account']), 'Foreign recovery opening')
    with ledger.transaction() as db:
        check_parent(db)
        require(fingerprint(ledger.access_snapshot(db, exclude_phase=CHILD)) == STOP_SQL,
                'Cannot roll forward a changed financial close')
        child = db.execute('SELECT approval,state,seal FROM phases WHERE id=? AND parent=?',
                           (CHILD, PARENT)).fetchone()
        require(child and child[1] == 'complete' and child[2], 'Recovery scientific phase incomplete')
        approval = json.loads(child[0])
        verify_release(ledger, db, approval)
        snapshot_before = fingerprint(ledger.access_snapshot(db))
        rows = db.execute('SELECT stage,provider_id,reported_cost,usage,state FROM attempts '
                          'WHERE phase=? ORDER BY id', (CHILD,)).fetchall()
    require(tuple(r[0] for r in rows) == STAGES and all(r[4] == 'settled' for r in rows),
            'Recovery contains missing or unresolved requests')
    journal = Path(output).parent / ('recovery-financial-readback-' + uuid4().hex)
    details = verify_generations(client, [(r[1], r[2]) for r in rows], journal)
    for (_, _, _, usage, _), generation in zip(rows, details, strict=True):
        usage = json.loads(usage)
        require(generation.get('native_tokens_prompt') == usage['prompt_tokens']
                and generation.get('native_tokens_completion') == usage['completion_tokens'],
                'Child generation native usage differs from original response')
    closing = snapshot(client, journal / 'account')
    with ledger.transaction() as db:
        require(fingerprint(ledger.access_snapshot(db)) == snapshot_before,
                'Ledger changed during child financial readback')
    totals = ledger.totals()
    change = compare(opening['account'], closing, opening['reported_cost_usd'], totals['reported_cost_usd'])
    known_child_cost = sum((Decimal(r[2]) for r in rows), Decimal(0))
    key_delta = Decimal(opening['account']['key']['limit_remaining']) - Decimal(closing['key']['limit_remaining'])
    require(change['verified'] and Decimal(change['campaign_delta']) == key_delta == known_child_cost
            and totals['unknown_attempts'] == 4 and totals['attempts'] == 18488,
            'New account/key movement or child request count differs')
    record = {'verified': True, 'scope': 'known-generation roll-forward with four retained unknowns',
              'original_stop_close_sha256': STOP_CLOSE_SHA, 'retained_verified_generations': 17282,
              'generation_count': len(details), 'generations': details, 'generation_journal': str(journal),
              'opening': opening, 'closing': closing, 'movement': change, 'accounting': totals,
              'unresolved_attempt_ids': [1, 2, 3, 17286], 'reserved_unknown_microusd': 79994,
              'request_level_unknowns_adjudicated': False}
    save_new(output, record)
    return record
