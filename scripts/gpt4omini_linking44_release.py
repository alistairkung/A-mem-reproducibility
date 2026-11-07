"""Freeze the reviewed PR #48 supplement and the single funded tail of conv-44."""
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import re
import subprocess

from amem_repro.blk027 import sha, verify_merged_review
from amem_repro.config import fingerprint, source_fingerprint
from amem_repro.gpt4omini_campaign import read, verify_inventory, verify_prior
from amem_repro.linking44_reconstruction import (
    CELL, CHILD, PARENT, PARENT_HASH, PARENT_PATH, PARENT_SEAL, SUPPLEMENT, require,
)
from amem_repro.openrouter import save_new
from amem_repro.linking44_finance import RECOVERY_LIMITS, RELEASE_PATH, STOP_CLOSE


PARENT_RELEASE_HASH = 'c108d9803eff91fff9af9b1133c1fb1849a10a48ee697f937abed86e38e019e5'
PARENT_LEDGER_HASH = '9f425359b58c0f8167eeb5446b7ad5d0063e94ebd02b350259491829e5b28d46'
DIRECTORY = Path('verification/linking44-release')
MIGRATIONS = {'amem_repro/openrouter.py', 'amem_repro/gpt4omini_campaign.py',
              'scripts/gpt4omini-baseline.py'}
ADDITIONS = {'amem_repro/linking44_finance.py', 'amem_repro/linking44_reconstruction.py',
             'scripts/gpt4omini_linking44_release.py'}


SERVICE_FORECAST = Path('verification/linking44-release/standards/service-forecast.json')
FORECAST = Path('verification/linking44-approved-recovery/finance-completion-forecast.json')
VERIFICATIONS = ('capacity.json', 'baseline-preflight.json', 'full-suite.txt',
                 'full-suite-invocation.json', 'full-size-conv-44.json', 'baseline-spec-review.json',
                 'baseline-standards-review.json', 'reconstruction-spec.json', 'reconstruction-standards.json')


def release_files(root, old):
    campaign = root / 'artifacts/gpt4omini'
    files = dict(old['files'])
    for name in MIGRATIONS | ADDITIONS:
        files[name] = sha(root / name)
    evidence = [CELL / 'frozen/campaign-approval.json', SUPPLEMENT, PARENT_PATH, STOP_CLOSE,
                FORECAST, SERVICE_FORECAST, *(DIRECTORY / name for name in VERIFICATIONS)]
    for name in evidence:
        path = campaign / name
        files[str(path.relative_to(root))] = sha(path)
    return files


def current_capacity(capacity):
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(capacity['observed_at'])).total_seconds()
    billing = capacity['snapshot']
    counts = (billing['rolling_units'], billing['current_period_hour_lagged'], capacity['metered_org_units'])
    require(all(type(n) is int and n >= 0 for n in counts), 'Invalid service unit counts')
    require(0 <= age <= 3600 and capacity['verified'] is True
            and capacity['project_id'] == 'cmvxd2aby005wad0ei7wt2d5o'
            and capacity['project_auth']['project_match'] is True and capacity['project_auth']['status'] == 'ok'
            and billing['plan'] == 'Core' and capacity['metered_org_units'] == 143942
            and capacity['baseline_study_meter_units'] == 55268
            and capacity['terminal_parent_units'] == 1155 and capacity['same_cell_service_units_remaining'] == 12345
            and capacity['same_cell_service_remaining_microusd'] == 987600
            and capacity['historical_retained_units'] == 2 and capacity['historical_retained_margin_microusd'] == 160
            and capacity['existing_service_program_reserve_microusd'] == 6769440,
            'Fresh capacity and retained service allowance required')
    effective = max(billing['rolling_units'], capacity['metered_org_units']) + 2
    growth = effective - 143944
    require(capacity['effective_conservative_org_units'] == effective
            and (55268 + 2 + growth + 12345) * 80 <= 6769440, 'Existing service funding is insufficient')


def freeze(root, reviewed, merge):
    from amem_repro.phases import _verified_receipt
    campaign = root / 'artifacts/gpt4omini'
    records = campaign / DIRECTORY
    old_path = campaign / CELL / 'frozen/campaign-approval.json'
    require(sha(old_path) == PARENT_RELEASE_HASH and sha(campaign / PARENT_PATH) == PARENT_HASH
            and sha(campaign / 'budget.sqlite') == PARENT_LEDGER_HASH, 'Stopped parent changed')
    old = read(old_path)
    verify_merged_review(root, reviewed, merge)
    sources = source_fingerprint(root)
    source = fingerprint(sources)
    supplement = campaign / SUPPLEMENT
    reconstruction_sha = sha(supplement)
    require(read(supplement)['source_sha256'] == source, 'Reconstruction source differs')
    for axis in ('spec', 'standards'):
        review = read(records / f'baseline-{axis}-review.json')
        proof = read(records / f'reconstruction-{axis}.json')
        require(review.get('verdict') == 'pass' and review.get('reviewed_commit') == reviewed
                and review.get('source_sha256') == source and proof.get('verified') is True
                and proof.get('reconstruction_sha256') == reconstruction_sha
                and proof.get('source_sha256') == source, 'Independent approval or state check differs')
    suite = (records / 'full-suite.txt').read_text()
    invocation = read(records / 'full-suite-invocation.json')
    require(invocation['reviewed_commit'] == reviewed and invocation['source_sha256'] == source
            and re.search(r'(?m)^\d+ passed.*$', suite) and not re.search(r'\b\d+ (failed|errors)\b', suite),
            'Complete offline suite required')
    preflight = read(records / 'baseline-preflight.json')
    _verified_receipt(preflight, root / 'artifacts/assets', root)
    require(preflight['assets'] == read(campaign / 'verification/blk027-release/baseline-preflight.json')['assets'],
            'Frozen runtime assets differ')
    export = read(records / 'full-size-conv-44.json')
    complete = export['results']['complete']
    require(export['verified'] and export['source_sha256'] == source
            and (complete['items'], complete['scores'], complete['original_qa_associations']) == (316,4494,158)
            and complete['max_batch_bytes'] < 32 * 1024 * 1024
            and complete['readonly_resume_has_no_additional_export_or_score']
            and export['results']['partial']['resume_rejected_without_additional_spans_scores_or_import'],
            'Conv-44 full-size reporting proof required')
    capacity_path = records / 'capacity.json'
    capacity = read(capacity_path)
    current_capacity(capacity)
    verify_prior(root)
    files = dict(old['files'])
    # Migrate only reviewed support code. The old release is immutable and binds
    # the original Git bytes of every replaced file as well as historical data.
    for name in MIGRATIONS:
        original = subprocess.check_output(['git', 'show', old['reviewed_commit'] + ':' + name], cwd=root)
        require(hashlib.sha256(original).hexdigest() == files[name], 'Parent source migration differs')
        files[name] = sha(root / name)
    for name in ADDITIONS:
        require(name not in files, 'Recovery source shadows a parent input')
        files[name] = sha(root / name)
    require(all(files.get(name) == digest for name, digest in sources['files'].items()),
            'Unreviewed scientific source migration')
    files = release_files(root, old)
    require(sha(campaign / FORECAST) == '0ffacb293a11ea56b4c64753315895859070b35e52a06ceb3050d71247591614',
            'Reviewed stage-weighted completion forecast differs')
    require(sha(campaign / SERVICE_FORECAST) == 'd386a6cf6730292579e27b1e2689e9c95a00b9d6813b280f310fb517f2960c6a',
            'Independent child service forecast changed')
    # The parent links all prior scientific/financial evidence. Recheck it all
    # before publishing any new release under the existing combined cap.
    verify_inventory(root, files)
    new = dict(old)
    parent_spend = Decimal('0.221067')
    model_estimate = Decimal('0.401235')  # entire cell's conservative planning estimate before interruption
    service_upper = Decimal('0.987600')
    require(parent_spend + model_estimate + service_upper < Decimal('5')
            and model_estimate + service_upper < Decimal('33.703535'), 'Unfunded completion')
    new.update(binding={**old['binding'], 'source_sha256': source},
               approved_by='User approval of PR #48 reconstruction and one final continuation',
               approved_at=datetime.now(timezone.utc).isoformat(), phase=CHILD, parent=PARENT,
               parent_seal=PARENT_SEAL, parent_path=str(campaign / PARENT_PATH),
               reconstruction_sha256=reconstruction_sha, files=files, reviewed_commit=reviewed,
               merge_commit=merge, limits=dict(RECOVERY_LIMITS),
               forecast={**old['forecast'], 'capacity_path': str(capacity_path.relative_to(campaign)),
                         'capacity_sha256': sha(capacity_path), 'remaining_model_planning_usd': str(model_estimate),
                         'remaining_service_upper_usd': str(service_upper), 'remaining_stage_weighted_model_estimate_usd': '0.288076', 'remaining_requests': 1202})
    verify_release(root, new)
    save_new(campaign / RELEASE_PATH, new)
    return new


def verify_release(root, release):
    campaign = root / 'artifacts/gpt4omini'
    require(release['approved'] is True and release['phase'] == CHILD and release['parent'] == PARENT
            and release['parent_seal'] == PARENT_SEAL and release['limits'] == RECOVERY_LIMITS
            and sha(campaign / SUPPLEMENT) == release['reconstruction_sha256']
            and sha(campaign / PARENT_PATH) == PARENT_HASH, 'Recovery release differs')
    parent_release = campaign / CELL / 'frozen/campaign-approval.json'
    records = campaign / DIRECTORY
    require(sha(parent_release) == PARENT_RELEASE_HASH, 'Parent release changed')
    parent = read(parent_release)
    required = release_files(root, parent)
    require(release['files'] == required and release['binding'] == {
        **parent['binding'], 'source_sha256': fingerprint(source_fingerprint(root))},
        'Recovery did not bind the complete original inventory and permitted migration')
    require(release['forecast']['capacity_path'] == str(DIRECTORY / 'capacity.json')
            and release['forecast']['capacity_sha256'] == sha(records / 'capacity.json'),
            'Release capacity differs')
    for axis in ('spec', 'standards'):
        review = read(records / f'baseline-{axis}-review.json')
        proof = read(records / f'reconstruction-{axis}.json')
        require(review.get('verdict') == 'pass' and review['reviewed_commit'] == release['reviewed_commit']
                and review['source_sha256'] == release['binding']['source_sha256']
                and proof.get('verified') is True and proof['source_sha256'] == review['source_sha256']
                and proof['reconstruction_sha256'] == release['reconstruction_sha256'],
                'Recovery reviews differ')
    verify_merged_review(root, release['reviewed_commit'], release['merge_commit'])
    require(release['binding']['source_sha256'] == fingerprint(source_fingerprint(root)),
            'Recovery source differs')
    verify_inventory(root, release['files'])
    for name, digest in release['files'].items():
        if name.startswith('artifacts/'):
            continue
        blob = subprocess.check_output(['git', 'show', release['reviewed_commit'] + ':' + name], cwd=root)
        require(hashlib.sha256(blob).hexdigest() == digest, 'Runtime file differs from reviewed Git bytes')
    verify_prior(root)
