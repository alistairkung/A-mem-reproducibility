"""Release and run the final local Linking Only / conv-44 campaign."""
import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amem_repro.blk027 import sha
from amem_repro.config import fingerprint
from amem_repro.gpt4omini_campaign import file_signature, read
from amem_repro.linking44_final_ledger import (
    GROUP, GROUP_LIMITS, GROUP_ROOT, HARD_DEADLINE, PAID_DEADLINE, phase_id,
)
from amem_repro.openrouter import CELL_SERVICE_RESERVE, save_new
from amem_repro.phases import _verified_receipt, preflight as offline_preflight
from scripts import gpt4omini_replacement as previous

CAMPAIGN = previous.CAMPAIGN
DIRECTORY = CAMPAIGN / GROUP_ROOT
HISTORICAL = previous.GROUP_DIR / 'attempt-1'
CLOSE = HISTORICAL / 'reconciliation.json'
BASE = '7b290a3d418b90c32f93143c639bd6343e4523a7'
PAID_END = PAID_DEADLINE
END = HARD_DEADLINE
# Observed full build and QA require about three hours. Reserve forty minutes for
# remote readback, independent science, reconciliation and the matched analysis.
FRESH_DURATION = timedelta(hours=3)
LIMITS = GROUP_LIMITS
HISTORY = {
    CAMPAIGN/'budget.sqlite': '3d63745c4a4d257e868b7ca3bffbf50f64c12a82d936f3cbe71b159be41b811d',
    CAMPAIGN/'verification/replacement-finance/final-group-campaign-envelope.json':
        'f7b4dc89b1003a96b1f5a4e143eec81ec3e5294879f8a58e7db023b0fbe2ab29',
    HISTORICAL/'standards-preservation.json': '99685cb9e11360f410b64cd7bbad1d723d4c862bc7ad5fff3256bf41c699fa13',
    HISTORICAL/'runs/gpt4omini-linking_only-conv44-replacement-r1/phase.json':
        '0532f333e34e8379572a3e19ec22674a5793b26b6433e47377cf9f78c437cd42',
    CLOSE: '1a2ce0e93f16210d75d3971de2f6f4150e779b66ac92cd163cab362e090196a5',
    previous.GROUP_DIR/'release.json': 'fc0e075f9851e14fb1bb56d402413677781215c00e726e340ea3ef00da40d897',
}
require = previous.require


def before_request(request):
    if request.method == 'POST':
        require(str(request.url) == previous.BASE_URL + '/chat/completions'
                and datetime.now(timezone.utc) < PAID_END, 'Paid transmission window or route differs')


def start_allowed():
    require(datetime.now(timezone.utc) + FRESH_DURATION < PAID_END,
            'Insufficient time for a fresh build and final verification')


def checked_file(path, digest):
    before = file_signature(path)
    require(path.resolve() == path and path.stat().st_nlink == 1 and sha(path) == digest
            and file_signature(path) == before, f'Changed financial or release evidence: {path.name}')
    return before


def protected_r1():
    phase = HISTORICAL/'runs/gpt4omini-linking_only-conv44-replacement-r1/phase.json'
    checked_file(phase, HISTORY[phase])
    protected = {}
    for name, digest in read(phase)['files'].items():
        path = phase.parent/name
        require(path.is_relative_to(phase.parent) and path.resolve() == path, 'Foreign r1 phase file')
        protected[path] = checked_file(path, digest)
    return protected


def runtime_files(commit):
    source, files, bootstrap = previous.reviewed_files(commit)
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, commit], cwd=ROOT, check=True)
    name = 'scripts/gpt4omini_final_fresh.py'
    expected = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
    require(expected == (ROOT/name).read_bytes(), 'Final driver differs from reviewed commit')
    files[name] = hashlib.sha256(expected).hexdigest()
    old = read(previous.GROUP_DIR/'release.json')['implementation_files']
    changed = {key for key in files.keys() | old.keys() if files.get(key) != old.get(key)}
    allowed = {'amem_repro/linking44_final_ledger.py', 'amem_repro/linking44_retry.py',
               'amem_repro/gpt4omini_campaign.py', 'amem_repro/observability.py',
               'scripts/gpt4omini_replacement.py', name}
    require(changed <= allowed, f'Unexpected change to frozen runtime files: {sorted(changed - allowed)}')
    return source, files, bootstrap


def check_capacity(cap, commit, source_sha, as_of=None):
    observed = datetime.fromisoformat(cap['observed_at'])
    age = ((as_of or datetime.now(timezone.utc)) - observed).total_seconds()
    snapshot = cap['snapshot']
    rolling = snapshot['rolling_units']
    require(type(rolling) is int and rolling >= 0 and 0 <= age <= 3600
            and cap['verified'] and cap['group_affordable'] and snapshot['plan'] == 'Core'
            and snapshot['billing_period'] == '2026-11-03 to 2026-12-03'
            and cap['project_id'] == 'cmvxd2aby005wad0ei7wt2d5o' and cap['project_auth']['project_match'] is True
            and cap['reviewed_commit'] == commit and cap['source_sha256'] == source_sha,
            'Final service observation is unverified, unbound or stale')
    growth = max(0, rolling - 149525)
    opening = 10138902 + 80 * growth
    expected = {'opening_metered_org_units':149519, 'opening_org_high_water_units':149525,
                'retained_allowance_units':8, 'new_unallocated_org_growth_units':growth,
                'effective_conservative_org_units':149527 + growth, 'opening_model_microusd':4417062,
                'opening_measured_service_microusd':4868240 + 80 * growth,
                'opening_service_commitment_microusd':5721840 + 80 * growth,
                'opening_combined_conservative_microusd':opening, 'group_cap_microusd':10000000,
                'campaign_planned_microusd':42000000, 'protected_contingency_microusd':8000000,
                'campaign_headroom_after_group_microusd':32000000 - opening}
    require(all(cap.get(k) == v for k,v in expected.items()) and opening + 10000000 <= 42000000,
            'Final group exceeds service or campaign capacity')
    raw = 'verification/final-eight-hour-standards/opening-billing-observation.json'
    for name, digest in cap['evidence_files'].items():
        path = CAMPAIGN/name
        require(path.is_relative_to(CAMPAIGN), 'Foreign service capacity evidence')
        checked_file(path, digest)
    observation = read(CAMPAIGN/raw)
    require(raw in cap['evidence_files'] and observation['snapshot'] == snapshot
            and observation['observed_at'] == cap['observed_at']
            and cap['opening_capacity_sha256'] == sha(HISTORICAL/'standards-closing-capacity.json')
            and cap['opening_finance_sha256'] == HISTORY[CAMPAIGN/'verification/replacement-finance/final-group-campaign-envelope.json'],
            'Unbound service billing or opening financial receipt')


def make_release(commit, as_of=None):
    start_allowed()
    source, files, _ = runtime_files(commit)
    for path, digest in HISTORY.items():
        checked_file(path, digest)
    assets = read(DIRECTORY/'preflight.json')
    _verified_receipt(assets, ROOT/'artifacts/assets', ROOT)
    require(assets['assets'] == read(previous.GROUP_DIR/'preflight.json')['assets'],
            'Frozen runtime assets differ')
    source_sha = fingerprint(source)
    reviews = {}
    for axis in ('spec', 'standards'):
        path = DIRECTORY/f'{axis}-review.json'
        review = read(path)
        require(review.get('verdict') == 'pass' and review.get('reviewed_commit') == commit
                and review.get('source_sha256') == source_sha and not review.get('open_material_findings'),
                'Independent final implementation review missing')
        reviews[axis] = sha(path)
    cap = read(DIRECTORY/'capacity.json')
    check_capacity(cap, commit, source_sha, as_of)
    binding = {**read(previous.GROUP_DIR/'release.json')['binding'], 'source_sha256':source_sha}
    return {'approved': True, 'group': GROUP, 'reviewed_commit': commit, 'implementation_files': files,
            'binding': binding, 'limits': LIMITS, 'reviews': reviews,
            'historical_artifacts': {str(p.relative_to(CAMPAIGN)): h for p,h in HISTORY.items()},
            'preflight_sha256':sha(DIRECTORY/'preflight.json'), 'capacity_sha256':sha(DIRECTORY/'capacity.json'),
            'paid_cutoff':PAID_END.isoformat(), 'deadline':END.isoformat()}


def execute_one(ordinal):
    import httpx
    from amem_repro.linking44_final_ledger import FinalLedger, close_attempt
    from scripts.safe_service_audit import check_langfuse_project_auth

    phase = phase_id(ordinal)
    release = read(DIRECTORY/'release.json')
    expected = make_release(release['reviewed_commit'], datetime.fromisoformat(release['approved_at']) if ordinal > 1 else None)
    require({k:release.get(k) for k in expected} == expected, 'Final release differs from verified evidence')
    _, _, bootstrap = runtime_files(release['reviewed_commit'])
    bootstrap_path = ROOT/'scripts/gpt4omini-baseline.py'
    ns = {'__name__':'_final_local_environment', '__file__':str(bootstrap_path)}
    exec(compile(bootstrap, str(bootstrap_path), 'exec'), ns)
    ns['environment']()
    auth = check_langfuse_project_auth(ROOT/'.env', 'cmvxd2aby005wad0ei7wt2d5o')
    require(auth.get('project_match') is True, 'Langfuse project mismatch')
    key = os.environ['OPENROUTER_API_KEY']
    require(hashlib.sha256(key.encode()).hexdigest() ==
            read(CAMPAIGN/'compatibility-v5/private-credential-binding.json')['sha256'], 'Provider key mismatch')
    store = DIRECTORY/f'attempt-{ordinal}'
    require(store.resolve() == store and not os.path.lexists(store), 'Final namespace is already used or aliased')
    prior = CLOSE if ordinal == 1 else DIRECTORY/f'attempt-{ordinal-1}/reconciliation.json'
    protected = {p:checked_file(p, h) for p,h in HISTORY.items()}
    for p in (DIRECTORY/'release.json', DIRECTORY/'spec-review.json', DIRECTORY/'standards-review.json',
              DIRECTORY/'capacity.json', DIRECTORY/'preflight.json', prior):
        protected[p] = file_signature(p)
    protected.update(protected_r1())
    capacity = read(DIRECTORY/'capacity.json')
    for name, digest in capacity['evidence_files'].items():
        protected[CAMPAIGN/name] = checked_file(CAMPAIGN/name, digest)
    for n,digest in release['implementation_files'].items():
        protected[ROOT/n] = checked_file(ROOT/n, digest)
    approval = {'approved':True, 'approved_at':previous.now(), 'kind':'final_fresh','group':GROUP,
                'ordinal':ordinal,'repetition':3+ordinal,'phase':phase,'conversation':'conv-44',
                'condition':'linking_only','binding':release['binding'], 'release_sha256':sha(DIRECTORY/'release.json'),
                'previous_reconciliation_sha256':sha(prior), 'service_reserve_microusd':CELL_SERVICE_RESERVE}
    def verify_approval(actual):
        require(actual == approval and read(store/'frozen/approval.json') == actual
                and release['limits'] == LIMITS, 'Approval differs from reviewed financial envelope')
        require(all(file_signature(p) == sig for p,sig in protected.items()), 'Changed approval evidence')
    with httpx.Client(headers={'Authorization':'Bearer '+key}, timeout=120,
                      transport=httpx.HTTPTransport(retries=0), follow_redirects=False,
                      event_hooks={'request':[before_request]}) as client:
        client._amem_credential = key
        opening = previous.account_and_route(client, store, read(prior)['closing'])
        approval['opening_account'] = opening
        save_new(store/'frozen/approval.json', approval)
        ledger = FinalLedger(CAMPAIGN, approval, verify_approval=verify_approval)
        with (store/'runner.log').open('x', buffering=1) as log, redirect_stdout(log), redirect_stderr(log):
            receipt, finance = previous.run_attempt(client, ledger, release, ordinal, opening, protected,
                final_approval=approval, final_store=store, financial_close=close_attempt)
    print(phase, receipt['status'], receipt['notes'], receipt['questions'], finance['verified'], flush=True)


def execute():
    for ordinal in range(1, 4):
        start_allowed()
        subprocess.run([sys.executable, '-u', __file__, 'attempt', '--ordinal', str(ordinal)], cwd=ROOT, check=True)
        store = DIRECTORY/f'attempt-{ordinal}'
        receipt = read(store/'runs'/phase_id(ordinal)/'phase.json')
        finance = read(store/'reconciliation.json')
        require(finance['verified'] and finance['phase_seal'] == fingerprint(receipt),
                'Unreconciled scientific phase')
        if receipt['status'] in ('complete','degraded'):
            return
        require(ordinal < 3 and finance.get('restart_eligible') is True,
                'Final attempt is terminal or campaign allowance exhausted')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('preflight','freeze','execute','attempt'))
    parser.add_argument('--commit')
    parser.add_argument('--ordinal', type=int, choices=(1,2,3))
    args = parser.parse_args()
    if args.action == 'preflight':
        save_new(DIRECTORY/'preflight.json', offline_preflight(ROOT/'artifacts/assets', root=ROOT))
    elif args.action == 'freeze':
        save_new(DIRECTORY/'release.json', {**make_release(args.commit), 'approved_at':previous.now()})
    elif args.action == 'attempt':
        execute_one(args.ordinal)
    else:
        execute()
