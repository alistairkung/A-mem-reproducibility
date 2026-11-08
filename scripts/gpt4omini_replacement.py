"""Local, bounded replacement group for Linking Only / conv-44."""
import argparse
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amem_repro.blk027 import sha
from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint, source_fingerprint
from amem_repro.gpt4omini_campaign import (
    execute_phase, file_signature, read, verify_inventory, verify_prior,
)
from amem_repro.linking44_replacement import (
    GROUP, GROUP_ROOT, GROUP_LIMITS, ReplacementLedger, attempt_store, classify_restart, phase_id,
)
from amem_repro.openrouter import BASE_URL, MODEL, CELL_SERVICE_UNITS, save_new
from scripts.gpt4omini_finance import compare, snapshot, verify_generations
from scripts.gpt4omini_service import ServiceUnits, MeteredRuntimeClient, bind_score_meter, bounded_filter

CAMPAIGN = ROOT / 'artifacts/gpt4omini'
GROUP_DIR = CAMPAIGN / GROUP_ROOT
LEGACY = CAMPAIGN / 'cells/linking_only-conv-44'
CLOSE = CAMPAIGN / 'verification/linking44-approved-recovery/child-stop-finance-v2/receipt.json'
PR50 = 'c8ed9e325d64b463ac0ef54054b8e58342bbce39'
OPENING_LEDGER = '8ca77ffcc281af64050b73ea79109bab37c297f2c62465524deb1e7f27767f16'
PR49_RELEASE = 'e988e1c2cf21b4b3d97f1880d2aed2e94a2a8137f83f3d0cc838fd3cc15f41e5'
PR50_CLOSE = 'ad259a2546b8c9ad2af1bcda01cad0e134f3e25f0e18719384aff3077d7695c6'
DRIVER_FILES = ('scripts/gpt4omini_replacement.py', 'scripts/gpt4omini-baseline.py',
                'scripts/gpt4omini_finance.py', 'scripts/gpt4omini_service.py',
                'scripts/safe_service_audit.py')


def require(ok, message):
    if not ok:
        raise BudgetStop(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def verify_history():
    release_path = LEGACY / 'frozen/linking44-recovery-release.json'
    require(sha(release_path) == PR49_RELEASE and sha(CLOSE) == PR50_CLOSE, 'Historical release or close differs')
    old = read(release_path)
    verify_inventory(ROOT, {n: h for n, h in old['files'].items() if n.startswith('artifacts/')})
    pinned = {release_path: PR49_RELEASE, CLOSE: PR50_CLOSE}
    pinned.update({CLOSE.parent / n: h for n,h in read(CLOSE)['raw_journal_files'].items()})
    for number, expected in enumerate(('65d8f6a672863bdfbc2a5d5a6d5d95b3fd25c0a2b9b2dfd8cbef53032c80917b',
                                       'c2b2b83fed10b32d33e4275ab76705d0d82c21c58c7f32e2d6c9f0e922ef2c67')):
        path = LEGACY / 'runs' / f'gpt4omini-linking_only-conv44-r0-p{number}' / 'phase.json'
        require(sha(path) == expected, 'Original terminal evidence differs')
        pinned[path] = expected
        pinned.update({path.parent / n: h for n,h in read(path)['files'].items()})
    from amem_repro.artifacts import CacheStore
    retained = CacheStore(LEGACY / 'cache')
    cache = LEGACY / 'cache/3d148b77448c6834c8412f46dc7de16199b56bebaa096ee26f8cf3d152416d41'
    identity = read(cache / 'identity.json')
    require(retained.path_for(identity) == cache and len(retained.load(identity)['notes']) == 675,
            'Original completed build differs')
    pinned[cache / 'state.json'] = 'aa1b706ae9e74c9dff3d71e7555ba497c61aa69d6771f082250b688376170d51'
    pinned[cache / 'identity.json'] = cache.name
    pinned[cache / 'complete.json'] = sha(cache / 'complete.json')
    signatures = {}
    for path, expected in pinned.items():
        start = file_signature(path)
        require(path.resolve() == path and sha(path) == expected and file_signature(path) == start,
                'A protected historical artifact changed')
        signatures[path] = start
    verify_prior(ROOT)
    return old, signatures


def preflight():
    from amem_repro.phases import preflight as local_preflight
    original, _ = verify_history()
    require(sha(CAMPAIGN / 'budget.sqlite') == OPENING_LEDGER, 'Opening ledger changed')
    assets = local_preflight(ROOT / 'artifacts/assets', root=ROOT)
    require(assets['runtime']['ok'] and assets['assets'] == read(
        CAMPAIGN / 'verification/linking44-release/baseline-preflight.json')['assets'], 'Local assets differ')
    files = dict(source_fingerprint(ROOT)['files'])
    scientific = {k: v for k,v in original['files'].items() if k in files}
    changes = {k for k in scientific if files[k] != scientific[k]} | (files.keys() - scientific.keys())
    require(changes == {'amem_repro/gpt4omini_campaign.py', 'amem_repro/linking44_replacement.py'},
            'Unsupported support-source migration')
    return assets


def verify_capacity(cap, source, commit, *, as_of=None, campaign=CAMPAIGN):
    timestamp = datetime.fromisoformat(as_of) if as_of is not None else datetime.now(timezone.utc)
    age = (timestamp - datetime.fromisoformat(cap['observed_at'])).total_seconds()
    rolling = cap['snapshot']['rolling_units']
    require(type(rolling) is int and rolling >= 0, 'Invalid rolling service units')
    observed = 'verification/replacement-standards/opening-billing-observation.json'
    anchor = 'verification/linking44-release/capacity-after-child.json'
    anchor_sha = 'd4cfe4960e5a8995a16995dec10e0ba381cf92ef55f1b5b34590335ef12bd085'
    raw = (campaign / observed).read_bytes()
    evidence = json.loads(raw)
    require(cap.get('evidence_files',{}).get(observed) == hashlib.sha256(raw).hexdigest()
            and cap.get('opening_capacity_sha256') == anchor_sha == sha(campaign / anchor)
            and evidence['snapshot'] == cap['snapshot'] and evidence['observed_at'] == cap['observed_at']
            and cap['snapshot']['billing_period'] == '2026-11-03 to 2026-12-03',
            'Billing snapshot must match the observed project capacity and retained opening')
    growth = max(0, rolling - 146695)
    opening = 8788198 + 80 * growth
    require(cap['verified'] is True and cap['group_affordable'] is True and 0 <= age <= 3600
            and cap['project_id'] == 'cmvxd2aby005wad0ei7wt2d5o' and cap['snapshot']['plan'] == 'Core'
            and cap['project_auth']['project_match'] is True and cap['project_auth']['status'] == 'ok'
            and cap['reviewed_commit'] == commit and cap['source_sha256'] == source
            and cap['retained_allowance_units'] == 8 and cap['opening_metered_org_units'] == 146689
            and cap['opening_observed_org_units'] == 146695
            and cap['new_unallocated_org_growth_units'] == growth
            and cap['effective_conservative_org_units'] == 146697 + growth
            and cap['service_conservative_microusd'] == 4641840 + 80 * growth
            and cap['opening_conservative_model_microusd'] == 4146358
            and cap['group_cap_microusd'] == 10000000 and cap['campaign_planned_microusd'] == 42000000
            and cap['protected_contingency_microusd'] == 8000000
            and cap['opening_combined_conservative_microusd'] == opening
            and cap['campaign_headroom_after_group_microusd'] == 42000000 - opening - 10000000
            and opening + 10000000 <= 42000000, 'Service account or combined campaign capacity differs')


def reviewed_files(commit):
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == commit,
            'Reviewed commit must be checked out')
    subprocess.run(['git','merge-base','--is-ancestor',PR50,commit],cwd=ROOT,check=True)
    source = source_fingerprint(ROOT)
    files = {**source['files'], **{n:sha(ROOT / n) for n in DRIVER_FILES}}
    bootstrap = None
    for name, digest in files.items():
        blob = subprocess.check_output(['git','show',commit + ':' + name],cwd=ROOT)
        require(hashlib.sha256(blob).hexdigest() == digest, 'Reviewed Git source differs')
        if name == 'scripts/gpt4omini-baseline.py':
            bootstrap = blob
    return source, files, bootstrap


def freeze(commit):
    from amem_repro.phases import _verified_receipt
    sources, files, _ = reviewed_files(commit)
    assets = read(GROUP_DIR / 'preflight.json')
    _verified_receipt(assets, ROOT / 'artifacts/assets', ROOT)
    old, _ = verify_history()
    require(sha(CAMPAIGN / 'budget.sqlite') == OPENING_LEDGER, 'Original ledger changed')
    binding = {**old['binding'], 'source_sha256': fingerprint(sources)}
    reviews = {}
    for axis in ('spec', 'standards'):
        path = GROUP_DIR / f'{axis}-review.json'
        review = read(path)
        require(review.get('verdict') == 'pass' and review['reviewed_commit'] == commit
                and review['source_sha256'] == binding['source_sha256'], 'Fixed-head independent review required')
        reviews[axis] = sha(path)
    cap = read(GROUP_DIR / 'capacity.json')
    verify_capacity(cap, binding['source_sha256'], commit)
    release = {'approved': True, 'approved_by': 'User approval of scoped local overnight replacement group',
               'approved_at': now(), 'group': GROUP, 'binding': binding, 'limits': GROUP_LIMITS,
               'reviewed_commit': commit, 'implementation_files': files, 'reviews': reviews,
               'capacity_sha256': sha(GROUP_DIR / 'capacity.json'), 'preflight_sha256': sha(GROUP_DIR / 'preflight.json'),
               'historical_release_sha256': PR49_RELEASE, 'opened_from_ledger_sha256': OPENING_LEDGER}
    save_new(GROUP_DIR / 'release.json', release)


def account_and_route(client, store, prior):
    account = snapshot(client, store / 'opening-reads')
    require(account == prior, 'Opening account or key differs from previous verified close')
    funds = Decimal(account['credits']['total_credits']) - Decimal(account['credits']['total_usage'])
    require(funds >= 10 and Decimal(account['key']['limit_remaining']) >= 10, 'Insufficient provider credit')
    response = client.get(BASE_URL + '/models/openai/gpt-4o-mini-2024-07-18/endpoints')
    response.raise_for_status()
    data = response.json()['data']
    p = next(v for v in data['endpoints'] if v['tag'] == 'openai')
    require(data['id'] == MODEL and p['context_length'] == 128000 and p['max_completion_tokens'] == 16384
            and Decimal(p['pricing']['prompt']) == Decimal('.00000015')
            and Decimal(p['pricing']['completion']) == Decimal('.0000006')
            and {'temperature','response_format','structured_outputs','max_tokens'} <= set(p['supported_parameters']),
            'Provider route or price differs')
    save_new(store / 'opening-route.json', response.json())
    return account


def close_attempt(client, ledger, phase, store, receipt, opening, units):
    with ledger.transaction() as db:
        rows = db.execute('SELECT * FROM attempts WHERE phase=? ORDER BY id',(phase,)).fetchall()
        require(db.execute('SELECT seal FROM phases WHERE id=?',(phase,)).fetchone() == (fingerprint(receipt),),
                'Attempt seal differs')
    settled = [r for r in rows if r[6] == 'settled']
    journal = store / 'financial-readbacks'
    details = verify_generations(client, [(r[9],r[10]) for r in settled], journal)
    for row, generation in zip(settled, details, strict=True):
        usage = json.loads(row[8])
        require((generation.get('native_tokens_prompt'),generation.get('native_tokens_completion')) ==
                (usage['prompt_tokens'],usage['completion_tokens']), 'Native token accounting differs')
    closing = snapshot(client, journal / 'account')
    known = sum((Decimal(r[10]) for r in settled), Decimal(0))
    movement = compare(opening,closing,0,known)
    verified = movement['verified'] and (Decimal(opening['key']['limit_remaining'])
                                          - Decimal(closing['key']['limit_remaining']) == known)
    record = {'phase': phase, 'verified': verified, 'phase_seal': fingerprint(receipt),
              'settled_attempts_sha256': fingerprint(settled), 'settled_count': len(settled),
              'known_cost_usd': str(known), 'model_conservative_microusd': sum(r[5] for r in rows),
              'unknown_attempt_ids':[r[0] for r in rows if r[6] != 'settled'],
              'movement':movement, 'opening':{'account':opening}, 'closing':closing, 'service_units':units,
              'generations':details,'generation_journal':str(journal)}
    save_new(store / 'reconciliation.json', record)
    require(verified, 'Unexplained provider movement; stop and retain all reservations')
    return record


def run_attempt(client, ledger, release, ordinal, opening, protected, *, final_approval=None,
                final_store=None, financial_close=close_attempt):
    from langfuse import Langfuse
    import tiktoken
    from importlib.metadata import version
    from amem_repro.measurements import TokenCounter
    from amem_repro.observability import LangfuseObserver
    from amem_repro.observation_policy import should_export_span

    if final_approval is None:
        store = attempt_store(CAMPAIGN, ordinal)
        phase = phase_id(ordinal)
        approval = {'approved':True,'approved_at':now(),'kind':'replacement','group':GROUP,
                    'ordinal':ordinal,'phase':phase,'conversation':'conv-44','condition':'linking_only',
                    'binding': release['binding'], 'release_sha256':sha(GROUP_DIR / 'release.json'),
                    'service_reserve_microusd':GROUP_LIMITS['service_reserve_per_attempt_microusd']}
        if ordinal > 1:
            approval['previous_reconciliation_sha256'] = sha(attempt_store(CAMPAIGN,ordinal-1) / 'reconciliation.json')
        save_new(store / 'frozen/approval.json',approval)
        repetition = ordinal
    else:
        store = final_store
        approval = final_approval
        phase = approval['phase']
        repetition = approval['repetition']
    encoded = tiktoken.get_encoding('o200k_base')
    counter = TokenCounter(lambda t:encoded.encode(t,disallowed_special=()),'tiktoken o200k_base; hosted prompt overhead unverified; API usage authoritative',version('tiktoken'))
    export = ServiceUnits(CELL_SERVICE_UNITS)
    runtime = ServiceUnits(CELL_SERVICE_UNITS - 36 * 158)
    try:
        with ExitStack() as life:
            cloud = Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],secret_key=os.environ['LANGFUSE_SECRET_KEY'],
                             base_url='https://cloud.langfuse.com',flush_at=16,
                             should_export_span=bounded_filter(should_export_span,export),
                             environment='amem-gpt4omini',release=release['binding']['source_sha256'])
            original = bind_score_meter(cloud,export)
            life.callback(setattr,cloud._resources,'add_score_task',original)
            life.callback(cloud.shutdown)
            observer = LangfuseObserver(MeteredRuntimeClient(cloud,runtime),
                        {**release['binding'],'run_id':phase,'repetition':repetition,'execution_mode':'paid-gpt4omini-baseline'})
            healthy = observer.assert_healthy
            def check():
                healthy()
                require(all(file_signature(p) == sig for p,sig in protected.items()), 'Protected stopped evidence changed')
                require(not export.exhausted and not runtime.exhausted, 'Service ceiling exhausted')
            observer.assert_healthy = check
            ledger.observe_phase(phase,check)
            receipt = execute_phase(approval, ledger, observer=observer, client=client, token_counter=counter,root=ROOT)
            cloud.flush()
    finally:
        save_new(store / 'service' / (phase+'.json'), {'maximum_units':export.limit,'admitted_units':export.spent,
                 'runtime_units_admitted':runtime.spent,'stopped':export.exhausted or runtime.exhausted})
    check()
    return receipt, financial_close(client,ledger,phase,store,receipt,opening,export.spent)


def execute_one(ordinal):
    import httpx
    from amem_repro.phases import _verified_receipt
    from scripts.safe_service_audit import check_langfuse_project_auth
    release = read(GROUP_DIR / 'release.json')
    _, files, bootstrap = reviewed_files(release['reviewed_commit'])
    require(files == release['implementation_files'], 'Released implementation inventory differs')
    path = ROOT / 'scripts/gpt4omini-baseline.py'
    namespace = {'__name__':'_reviewed_replacement_environment','__file__':str(path)}
    exec(compile(bootstrap,str(path),'exec'),namespace)
    namespace['environment']()
    _, protected = verify_history()
    assets = GROUP_DIR / 'preflight.json'
    require(sha(assets) == release['preflight_sha256'], 'Preflight receipt differs')
    _verified_receipt(read(assets), ROOT / 'artifacts/assets', ROOT)
    cap = GROUP_DIR / 'capacity.json'
    require(sha(cap) == release['capacity_sha256'], 'Opening service capacity differs')
    if ordinal == 1:
        verify_capacity(read(cap), release['binding']['source_sha256'], release['reviewed_commit'])
    capacity_paths = (cap, CAMPAIGN/'verification/replacement-standards/opening-billing-observation.json',
                      CAMPAIGN/'verification/linking44-release/capacity-after-child.json')
    protected.update({p:file_signature(p) for p in capacity_paths})
    auth = check_langfuse_project_auth(ROOT / '.env','cmvxd2aby005wad0ei7wt2d5o')
    require(auth.get('project_match') is True, 'Incorrect Langfuse project')
    key = os.environ['OPENROUTER_API_KEY']
    require(hashlib.sha256(key.encode()).hexdigest() == read(CAMPAIGN/'compatibility-v5/private-credential-binding.json')['sha256'],
            'Provider credential changed')
    prior = read(CLOSE) if ordinal == 1 else read(attempt_store(CAMPAIGN, ordinal-1) / 'reconciliation.json')
    ledger = ReplacementLedger(CAMPAIGN / 'budget.sqlite',campaign_root=CAMPAIGN,binding=release['binding'])
    store = attempt_store(CAMPAIGN,ordinal)
    require(not os.path.lexists(store), 'Consumed attempt directory cannot be reused')
    with httpx.Client(headers={'Authorization':'Bearer '+key},timeout=120,
                      transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        client._amem_credential = key
        opening = account_and_route(client,store,prior['closing'])
        with (store/'runner.log').open('x',buffering=1) as log, redirect_stdout(log), redirect_stderr(log):
            receipt, finance = run_attempt(client,ledger,release,ordinal,opening,protected)
    print(json.dumps({'phase':phase_id(ordinal),'status':receipt['status'],'notes':receipt['notes'],
                      'questions':receipt['questions'],'unknowns':finance['unknown_attempt_ids']}),flush=True)


def execute():
    # Each SDK, exporter, model client and memory builder lives for one ordinal.
    for ordinal in range(1, GROUP_LIMITS['max_attempts'] + 1):
        subprocess.run([sys.executable,'-u',__file__,'attempt','--ordinal',str(ordinal)],cwd=ROOT,check=True)
        phase = phase_id(ordinal)
        receipt = read(attempt_store(CAMPAIGN,ordinal) / 'runs' / phase / 'phase.json')
        if receipt['status'] in ('complete','degraded'):
            return
        if ordinal == GROUP_LIMITS['max_attempts'] or not classify_restart(CAMPAIGN,phase):
            raise BudgetStop('Attempt sealed Incomplete; no eligible next attempt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('preflight','freeze','execute','attempt'))
    parser.add_argument('--reviewed-commit')
    parser.add_argument('--ordinal',type=int,choices=(1,2,3))
    args = parser.parse_args()
    if args.action == 'preflight':
        save_new(GROUP_DIR / 'preflight.json', preflight())
    elif args.action == 'freeze':
        freeze(args.reviewed_commit)
    elif args.action == 'attempt':
        execute_one(args.ordinal)
    else:
        execute()
