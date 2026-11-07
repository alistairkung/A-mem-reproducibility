"""Freeze and execute the next independently admitted GPT-4o-mini Full baseline."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime,timezone
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
DIRECTORY=(ROOT/'artifacts/gpt4omini').resolve()


from amem_repro.openrouter import FULL_CELLS,CELL_ORDER,ABLATION_CONDITIONS,CELL_SERVICE_UNITS,CELL_SERVICE_RESERVE,PROGRAM_SERVICE_RESERVE,EXPANSION_CELLS,ablation_policy,predecessor_filename,cell_key,cell_store
CELL='conv-44'
CONDITION='full'
KEY=CELL
STORE=DIRECTORY
FIRST_VERIFY=DIRECTORY/'verification/renewed'
VERIFICATION=FIRST_VERIFY
PREFIX = '3b3bb2e36098b84f5881e65079a23943427ea3276216f731adb0d590a37a32f1'

def read(path):return json.loads(Path(path).read_bytes())


def verify_release(release):
    from amem_repro.config import fingerprint,source_fingerprint
    from amem_repro.gpt4omini_campaign import verify_inventory,verify_prior
    if (ROOT/'artifacts/gpt4omini').absolute()!=(ROOT/'artifacts/gpt4omini').resolve():
        raise RuntimeError('Paid campaign namespace cannot alias another artifact directory')
    if release['binding']['conversation_id']!=CELL:raise RuntimeError('Approval belongs to another cell')
    if release['binding']['condition']!=CONDITION:raise RuntimeError('Approval belongs to another condition')
    if CONDITION!='full' and release.get('ablation_policy')!=ablation_policy(KEY):
        raise RuntimeError('Explicit three-cell ablation grant required')
    if release.get('approved') is not True or release['binding']['campaign_id']!='amem-gpt4omini-openrouter-20261104-v1':
        raise RuntimeError('Explicit reviewed one-cell campaign approval required')
    if fingerprint(source_fingerprint(ROOT))!=release['binding']['source_sha256']:
        raise RuntimeError('Frozen campaign source changed')
    if KEY in EXPANSION_CELLS:
        if (release['limits'].get('max_new_langfuse_units') != CELL_SERVICE_UNITS
                or release['limits'].get('service_reserve_microusd') != CELL_SERVICE_RESERVE
                or release['forecast'].get('program_service_reserve_microusd') != PROGRAM_SERVICE_RESERVE):
            raise RuntimeError('Expansion service allocation differs from reviewed policy')
    verify_inventory(ROOT,release['files'])
    for name,digest in release['files'].items():
        if name.startswith('artifacts/'):
            continue
        blob=subprocess.check_output(['git','show',release['reviewed_commit']+':'+name],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=digest:
            raise RuntimeError('Frozen runtime file differs from reviewed Git bytes')
    if KEY in ('neither-conv-44', 'linking_only-conv-50', 'linking_only-conv-44'):
        from amem_repro.blk027 import verify_merged_review
        verify_merged_review(ROOT, release['reviewed_commit'], release['merge_commit'])
    else:
        for commit in (release['reviewed_commit'],release['merge_commit']):
            subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT,check=True,capture_output=True)
    for axis in ('standards','spec'):
        review=read(VERIFICATION/f'baseline-{axis}-review.json')
        if review.get('verdict')!='pass' or review.get('reviewed_commit')!=release['reviewed_commit']:
            raise RuntimeError('Baseline independent review is not bound to this release')
    verify_prior(ROOT)


def freeze(gate_path, reviewed_commit, merge_commit):
    from amem_repro.config import source_fingerprint,fingerprint,stage_output_limits,OPENROUTER_CONFIG
    from amem_repro.openrouter import SCIENTIFIC_BINDING,save_new
    from amem_repro.gpt4omini_campaign import verify_inventory
    sources=source_fingerprint(ROOT)
    gate=read(gate_path)
    required=('real_runner','native_contracts_verified','remote_observations_verified',
              'experiments_verified','replay_equivalence','full_action_equivalence',
              'two_actual_checkpoint_continuations')
    if (gate.get('source_sha256')!=fingerprint(sources) or gate.get('network_llm_requests')!=0
            or any(gate.get(k) is not True for k in required)):
        raise RuntimeError('Source-bound real-runner native/cloud gate incomplete')
    if CONDITION!='full' and gate.get('ablated_checkpoint_conditions')!=list(ABLATION_CONDITIONS):
        raise RuntimeError('All ablation executor/cloud gates required')
    if KEY in EXPANSION_CELLS and gate.get('expansion_checkpoint_cells')!=list(EXPANSION_CELLS):
        raise RuntimeError('All six expansion checkpoint gates required')
    verify_inventory(Path(gate_path).parent,gate['files'])
    if gate.get('gate_script_sha256')!=hashlib.sha256((ROOT/'scripts/gpt4omini-gate.py').read_bytes()).hexdigest():
        raise RuntimeError('Executed cloud-gate script differs from this release')
    for name,digest in gate.get('fixture_files',{}).items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Executed native gate fixture changed')
    compatibility=read(DIRECTORY/'compatibility-release-tail/receipt.json')
    metadata=read(DIRECTORY/'compatibility-v5/final-access-acceptance.json')
    if (compatibility['status']!='complete' or compatibility['calls']!=3
            or compatibility['stages']!=['answer','shared_decision','shared_decision']
            or metadata['native_contracts_verified']!=['metadata']):
        raise RuntimeError('Native compatibility coverage incomplete')
    original_finance=DIRECTORY/'compatibility-v5/financial-readback-after-success.json'
    evidence=read(DIRECTORY/'compatibility-v5/final-access-acceptance.json')
    if hashlib.sha256(original_finance.read_bytes()).hexdigest()!=evidence['files'][str(original_finance.relative_to(DIRECTORY))]:
        raise RuntimeError('Original reconciled account snapshot changed')
    payload=read(VERIFICATION/(f'full-size-{CELL}.json' if KEY in EXPANSION_CELLS else 'full-size-export.json'))
    full=payload['results']['complete']
    if (not payload['verified'] or payload['source_sha256']!=fingerprint(sources)
            or payload['script_sha256']!=hashlib.sha256((ROOT/'scripts/gpt4omini-reporting-proof.py').read_bytes()).hexdigest()
            or (full['items'],full['scores'],full['original_qa_associations'])!=(
                {'conv-50':(408,5804,204),'conv-44':(316,4494,158)}[CELL] if KEY in EXPANSION_CELLS else (392,5568,196) if CONDITION!='full' else (316,4494,158))
            or full['max_batch_bytes']>=32*1024*1024 or not full['readonly_resume_has_no_additional_export_or_score']
            or not payload['results']['partial']['resume_rejected_without_additional_spans_scores_or_import']):
        raise RuntimeError('Full-size reporting integrity evidence failed')
    verify_inventory(ROOT,read(DIRECTORY/'compatibility-release-tail/approval.json')['query_evidence'])
    files=dict(sources['files'])
    paths=[FIRST_VERIFY/'programme-cost-plan.json',VERIFICATION/(f'full-size-{CELL}.json' if KEY in EXPANSION_CELLS else 'full-size-export.json'),VERIFICATION/'capacity-refresh.json',FIRST_VERIFY/'forecast.json',FIRST_VERIFY/'provider-audit.json',Path(gate_path),DIRECTORY/'compatibility-v5/final-access-acceptance.json',DIRECTORY/'compatibility-v5/financial-readback-after-success.json',DIRECTORY/'compatibility-v5/private-credential-binding.json',
        *[p for name in ('compatibility-release','compatibility-release-tail') for p in (DIRECTORY/name).rglob('*') if p.is_file()],
        DIRECTORY/'compatibility-v2/plan-v2.json',
        DIRECTORY/'verification/prior-preservation-authoritative-v2.json',
        DIRECTORY/'verification/preservation-reconciliation.json',
        VERIFICATION/'baseline-preflight.json',VERIFICATION/'full-suite.txt' if KEY!='conv-44' else FIRST_VERIFY/'full-final-60cabea.txt',
        VERIFICATION/'baseline-standards-review.json',VERIFICATION/'baseline-spec-review.json',
        VERIFICATION/'archive-equivalence.json',
        ROOT/'scripts/gpt4omini_service.py',ROOT/'scripts/gpt4omini-accept.py',ROOT/'scripts/gpt4omini-baseline.py',ROOT/'scripts/gpt4omini-gate.py',ROOT/'scripts/gpt4omini_gate_supplement.py',ROOT/'scripts/gpt4omini_finance.py',ROOT/'scripts/gpt4omini-reporting-proof.py',
        ROOT/'tests/gpt4omini_fixture.py',ROOT/'tests/gpt4omini_executor_fixture.py',
        ROOT/'tests/test_gpt4omini_executor.py',ROOT/'tests/test_gpt4omini_full_executor.py']
    if KEY!='conv-44':
        previous=CELL_ORDER[CELL_ORDER.index(KEY)-1]
        frontier_path=DIRECTORY/'outcomes'/previous/predecessor_filename(KEY)
        frontier=read(frontier_path)
        if frontier['next_cell']!=KEY or not frontier['affordable']:
            raise RuntimeError('Predecessor acceptance or affordability failed')
        prior_cells=CELL_ORDER[:CELL_ORDER.index(KEY)]
        from amem_repro.gpt4omini_campaign import predecessor_files,verify_accepted_cell
        for c in prior_cells:
            verify_accepted_cell(DIRECTORY,c)
            from scripts.gpt4omini_finance import verify_accepted_finances
            verify_accepted_finances(DIRECTORY,c)
            prior_store=cell_store(DIRECTORY,c)
            audits=[read(DIRECTORY/'outcomes'/c/f'acceptance-{axis}.json') for axis in ('standards','spec')]
            if not all(audit.get('accepted') is True and audit.get('verdict')=='pass' for audit in audits):
                raise RuntimeError('Missing prior independent acceptance')
            if audits[0]['phase']!=audits[1]['phase'] or not read(prior_store/'reconciliation.json')['verified']:
                raise RuntimeError('Prior audits or financial proof differ')
            proof=DIRECTORY/'outcomes'/c/'frontier.json'
            paths.append(proof)
            for name,digest in predecessor_files(DIRECTORY,c).items():
                files[str((DIRECTORY/name).relative_to(ROOT))]=digest
        if KEY in EXPANSION_CELLS:
            capacity_path=DIRECTORY/'outcomes'/previous/'expansion-capacity.json'
            if hashlib.sha256(capacity_path.read_bytes()).hexdigest()!=frontier['forecast']['capacity_sha256']:
                raise RuntimeError('Expansion capacity proof changed')
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(read(capacity_path)['observed_at'])).total_seconds()
            if not 0<=age<=3600:raise RuntimeError('Expansion capacity proof expired')
            paths.append(capacity_path)
        paths.append(frontier_path)
    for path in paths:files[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    suite=(VERIFICATION/'full-suite.txt' if KEY!='conv-44' else FIRST_VERIFY/'full-final-60cabea.txt').read_text()
    if not re.search(r'(?m)^\d+ passed.*$',suite) or re.search(r'\b\d+ (failed|errors)\b',suite):
        raise RuntimeError('Whole frozen-source offline suite did not pass')
    replay=read(VERIFICATION/'archive-equivalence.json')
    if replay.get('verified') is not True:raise RuntimeError('Fixed full archive equivalence gate failed')
    binding={**SCIENTIFIC_BINDING,'source_sha256':fingerprint(sources),
        'manifest_sha256':fingerprint(read(ROOT/'manifests/fallback.json')),
        'condition':CONDITION,'conversation_id':CELL,'population':'fallback','repetition':0,
        'initial_checkpoint':'fresh-empty','accepted_financial_prefix':PREFIX,
        'provider_contract_policy':'strict-original-v1',
        'max_output_tokens_by_stage':stage_output_limits(OPENROUTER_CONFIG),
        'observability_policy':'run2-audit-essential-v1'}
    release={'approved':True,'approved_by':('User 5 November six-cell expansion; ' if KEY in EXPANSION_CELLS else 'User 5 November three conv-49 ablations; ' if CONDITION!='full'
                else 'User three Full baselines in order; this approval covers ')+KEY,
        'approved_at':datetime.now(timezone.utc).isoformat(),'binding':binding,'files':files,
        'reviewed_commit':reviewed_commit,'merge_commit':merge_commit,
        'limits':{'cell_microusd':5000000,'usable_campaign_microusd':42000000,
                  'protected_microusd':8000000,'max_baseline_calls':2*sum(FULL_CELLS[CELL]),
                  'max_new_langfuse_units':13500 if CONDITION!='full' else 30000},
        'gate_path':str(Path(gate_path).relative_to(ROOT)),
        'forecast':read(FIRST_VERIFY/'forecast.json') if KEY=='conv-44' else frontier['forecast']}
    if CONDITION!='full':release['ablation_policy']=ablation_policy(KEY)
    if KEY!='conv-44':
        release['previous_acceptance_sha256']=hashlib.sha256(frontier_path.read_bytes()).hexdigest()
    if KEY in EXPANSION_CELLS:release['limits']['service_reserve_microusd']=CELL_SERVICE_RESERVE
    from amem_repro.blk027 import SUCCESSORS, SUPPLEMENT, sha, verify_supplement
    if KEY in SUCCESSORS:
        verify_supplement(DIRECTORY)
        release['reporting_acceptance_sha256'] = sha(DIRECTORY/SUPPLEMENT)
    verify_release(release)
    save_new(STORE/'frozen/campaign-approval.json',release)
    print(json.dumps({'approved':True,'campaign':binding['campaign_id'],'source':binding['source_sha256']}))


def environment():
    from dotenv import dotenv_values
    from amem_repro.preflight import asset_environment
    os.environ.update(asset_environment(ROOT/'artifacts/assets'))
    for name in list(os.environ):
        if any(k in name.upper() for k in ('OPENAI_API','DEEPSEEK','OPENROUTER','LANGFUSE','OTEL_')):
            os.environ.pop(name)
    values=dotenv_values(ROOT/'.env')
    for name in ('OPENROUTER_API_KEY','LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY','LANGFUSE_BASE_URL','LANGFUSE_HOST'):
        if values.get(name):os.environ[name]=values[name]
    if (not all(os.environ.get(k) for k in ('OPENROUTER_API_KEY','LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY'))
            or (os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST'))!='https://cloud.langfuse.com'):
        raise RuntimeError('Intended private provider/project configuration missing')
    os.environ['LANGFUSE_OTEL_MAX_BATCH_SIZE_BYTES']=str(32*1024*1024)


def execute(*, recovery=False):
    import httpx
    from amem_repro.config import fingerprint
    from amem_repro.openrouter import BASE_URL,MODEL,CampaignLedger,save_new
    from amem_repro.gpt4omini_campaign import execute_phase,verify_prior,read
    from amem_repro.measurements import TokenCounter
    from amem_repro.phases import _verified_receipt
    environment()
    from amem_repro import linking44_finance as recovery_finance
    from scripts import gpt4omini_linking44_release as recovery_release
    from amem_repro.blk027 import sha
    if recovery:
        if KEY != 'linking_only-conv-44':
            raise RuntimeError('PR #48 authorises only the last cell')
        release = read(DIRECTORY / recovery_finance.RELEASE_PATH)
        def verify_current():
            recovery_release.verify_release(ROOT, release)
        frozen = STORE / 'frozen/recovery-admission'
    else:
        release = read(STORE / 'frozen/campaign-approval.json')
        def verify_current():
            verify_release(release)
        frozen = STORE / 'frozen'
    verify_current()
    preflight=read(VERIFICATION/'baseline-preflight.json')
    _verified_receipt(preflight,ROOT/'artifacts/assets',ROOT)
    from scripts.safe_service_audit import check_langfuse_project_auth
    auth=check_langfuse_project_auth(ROOT/'.env','cmvxd2aby005wad0ei7wt2d5o')
    if auth.get('project_match') is not True:raise RuntimeError('Intended Langfuse project not verified')
    from langfuse import Langfuse
    from amem_repro.observation_policy import should_export_span
    from amem_repro.observability import LangfuseObserver
    import tiktoken
    from importlib.metadata import version
    encoding=tiktoken.get_encoding('o200k_base')
    counter=TokenCounter(lambda text:encoding.encode(text,disallowed_special=()),
                         'tiktoken o200k_base; hosted prompt overhead unverified; API usage authoritative',version('tiktoken'))
    if recovery:
        runs = STORE / 'runs'
        if (STORE / 'cache').exists() or {p.name for p in runs.iterdir()} != {recovery_finance.PARENT}:
            raise RuntimeError('Recovery requires the exact stopped cell and unused child')
    elif (STORE/'cache').exists() or (STORE/'runs').exists():
        raise RuntimeError('Fresh baseline requires an unused primary cache and run namespace')
    from scripts.gpt4omini_service import ObservedCampaignLedger
    ledger_type = ObservedCampaignLedger if KEY in EXPANSION_CELLS else CampaignLedger
    ledger=ledger_type(DIRECTORY/'budget.sqlite',campaign_root=DIRECTORY,binding=release['binding'])
    key=os.environ['OPENROUTER_API_KEY']
    if hashlib.sha256(key.encode()).hexdigest()!=read(DIRECTORY/'compatibility-v5/private-credential-binding.json')['sha256']:
        raise RuntimeError('Verified provider credential changed')
    from contextlib import ExitStack
    with ExitStack() as lifecycle, httpx.Client(headers={'Authorization':'Bearer '+key},timeout=120,
                      transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        client._amem_credential=key
        from scripts.gpt4omini_finance import compare, snapshot, reconcile
        account=snapshot(client,frozen/'opening-account-reads')
        if recovery:
            opening = recovery_finance.verify_opening(DIRECTORY, account)
        else:
            prior=read(DIRECTORY/'compatibility-v5/financial-readback-after-success.json')
            previous={r['probe']:r['data'] for r in prior['account_readbacks']}
            previous_cost=prior['generation']['total_cost']
            prior_path=DIRECTORY/'compatibility-v5/financial-readback-after-success.json'
            if KEY!='conv-44':
                previous_cell=CELL_ORDER[CELL_ORDER.index(KEY)-1]
                prior_path=cell_store(DIRECTORY,previous_cell)/'reconciliation.json'
                settlement=read(prior_path)
                if not settlement['verified']:raise RuntimeError('Preceding cell reconciliation failed')
                previous=settlement['closing']
                previous_cost=settlement['accounting']['reported_cost_usd']
            known=ledger.totals()['reported_cost_usd']
            opening={'account':account,'reported_cost_usd':known,'approval':{'retained_access_prefix':PREFIX},
                     'previous_snapshot':str(prior_path),
                     'movement':compare(previous,account,previous_cost,known)}
        save_new(frozen/'account-before-baseline.json',opening)
        funds=Decimal(account['credits']['total_credits'])-Decimal(account['credits']['total_usage'])
        if not opening['movement']['verified'] or funds<13 or Decimal(account['key']['limit_remaining'])<5:
            raise RuntimeError('Prepaid funds, key limit or unaccounted movement')
        endpoint=client.get(BASE_URL+'/models/openai/gpt-4o-mini-2024-07-18/endpoints')
        endpoint.raise_for_status();data=endpoint.json()['data']
        provider=next(e for e in data['endpoints'] if e['tag']=='openai')
        if (data['id']!=MODEL or provider['context_length']!=128000 or provider['max_completion_tokens']!=16384
                or Decimal(provider['pricing']['prompt'])!=Decimal('.00000015')
                or Decimal(provider['pricing']['completion'])!=Decimal('.0000006')
                or not {'temperature','response_format','structured_outputs','max_tokens'}<=set(provider['supported_parameters'])):
            raise RuntimeError('Frozen provider route/pricing/capabilities changed')
        save_new(frozen/'route-before-baseline.json',endpoint.json())
        if KEY in EXPANSION_CELLS:
            capacity_path=DIRECTORY/release['forecast']['capacity_path']
            if hashlib.sha256(capacity_path.read_bytes()).hexdigest()!=release['forecast']['capacity_sha256']:
                raise RuntimeError('Cell capacity evidence changed before launch')
            elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(read(capacity_path)['observed_at'])).total_seconds()
            if not 0<=elapsed<=3600:
                raise RuntimeError('Cell capacity reading expired before launch')
        from scripts.gpt4omini_service import ServiceUnits, bind_score_meter, bounded_filter, MeteredRuntimeClient
        service_limit = release['limits']['max_new_langfuse_units']
        export_meter = ServiceUnits(service_limit) if KEY in EXPANSION_CELLS else None
        span_filter = bounded_filter(should_export_span, export_meter) if export_meter else should_export_span
        cloud=Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],secret_key=os.environ['LANGFUSE_SECRET_KEY'],
            base_url='https://cloud.langfuse.com',flush_at=16,should_export_span=span_filter,
            environment='amem-gpt4omini',release=release['binding']['source_sha256'])
        if export_meter:
            original_score_task = bind_score_meter(cloud,export_meter)
            lifecycle.callback(setattr,cloud._resources,'add_score_task',original_score_task)
        lifecycle.callback(cloud.shutdown)
        parent = read(DIRECTORY / recovery_finance.PARENT_PATH) if recovery else None
        prior_runtime_units = 0
        sequences = (1,) if recovery else range(FULL_CELLS[CELL][0]+1)
        for sequence in sequences:
            verify_current()
            phase=f"gpt4omini-{CONDITION}-{CELL.replace('-', '')}-r0-p{sequence}"
            approval={'approved':True,'approved_by':release['approved_by'],
                'approved_at':datetime.now(timezone.utc).isoformat(),'binding':release['binding'],
                'kind':'baseline','condition':CONDITION,'conversation':CELL,'phase':phase,
                'release_sha256':fingerprint(release),'retained_access_prefix':PREFIX}
            if CONDITION!='full':approval['ablation_policy']=ablation_policy(KEY)
            if KEY!='conv-44':approval['previous_acceptance_sha256']=release['previous_acceptance_sha256']
            if 'reporting_acceptance_sha256' in release:
                approval['reporting_acceptance_sha256'] = release['reporting_acceptance_sha256']
            if parent:
                approval.update(parent=parent['phase'],parent_seal=fingerprint(parent),
                    parent_path=str(STORE/'runs'/parent['phase']/'phase.json'))
            if recovery:
                approval[recovery_finance.RELEASE_KEY] = sha(DIRECTORY / recovery_finance.RELEASE_PATH)
            if ledger.unaccepted_unknowns(approval):
                raise RuntimeError('Unknown exposure forbids continuation')
            save_new(frozen/(phase+'-approval.json'),approval)
            runtime_meter = None
            previously_exported = export_meter.spent if export_meter else 0
            if export_meter:
                runtime_meter = ServiceUnits(service_limit - previously_exported - 36*FULL_CELLS[CELL][1])
            runtime_client=MeteredRuntimeClient(cloud,runtime_meter) if runtime_meter else cloud
            observer=LangfuseObserver(runtime_client,{**release['binding'],'run_id':phase,
                'execution_mode':'paid-gpt4omini-baseline','parent_run_id':parent['phase'] if parent else None})
            original_healthy=observer.assert_healthy
            from amem_repro.gpt4omini_campaign import file_signature
            legacy_manifest=read(DIRECTORY/'verification/prior-preservation-authoritative-v2.json')
            legacy=Path(legacy_manifest['legacy_root'])
            legacy_signatures={legacy/name:file_signature(legacy/name) for name in legacy_manifest['files']
                               if not (legacy/name).is_symlink()}
            # Aliases are checked through their immutable original target as well.
            for name in legacy_manifest['files']:
                target=(legacy/name).resolve();legacy_signatures[target]=file_signature(target)
            for name in legacy_manifest['input_files']:
                legacy_signatures[legacy/name]=file_signature(legacy/name)
            legacy_links={legacy/name:(target,(legacy/name).lstat()) for name,target in legacy_manifest['symlinks'].items()}
            legacy_signatures[legacy/'.git/HEAD']=file_signature(legacy/'.git/HEAD')
            legacy_signatures[DIRECTORY/'verification/prior-preservation-authoritative-v2.json']=file_signature(
                DIRECTORY/'verification/prior-preservation-authoritative-v2.json')
            if KEY!='conv-44':
                for name in release['files']:
                    if name.startswith('artifacts/gpt4omini/'):
                        path=(ROOT/name).resolve(); legacy_signatures[path]=file_signature(path)
            def observation_health():
                original_healthy()
                if export_meter and (export_meter.exhausted or runtime_meter.exhausted):
                    raise RuntimeError('Service allocation exhausted')
            if export_meter: ledger.observe_phase(phase, observation_health)
            def service_healthy():
                observation_health()
                if any(file_signature(path)!=signature for path,signature in legacy_signatures.items()):
                    raise RuntimeError('Historical evidence changed; no next paid operation')
                for path,(target,stat) in legacy_links.items():
                    current=path.lstat()
                    if (not path.is_symlink() or os.readlink(path)!=target
                            or (current.st_dev,current.st_ino,current.st_mtime_ns,current.st_ctime_ns)
                               !=(stat.st_dev,stat.st_ino,stat.st_mtime_ns,stat.st_ctime_ns)):
                        raise RuntimeError('Historical artifact link changed; no next paid operation')
                units=len(observer.observations)+len({r['trace_id'] for r in observer.observations})+len(observer.scores)
                # Retain room for all158 questions in both complete Experiments.
                reporting_units=(36 if CONDITION!='full' else 68)*FULL_CELLS[CELL][1]
                if prior_runtime_units+units+reporting_units>release['limits']['max_new_langfuse_units']:
                    raise RuntimeError('Included-service unit allocation reached; no further paid operation')
            observer.assert_healthy=service_healthy
            try:
                result=execute_phase(approval,ledger,observer=observer,client=client,token_counter=counter,root=ROOT)
            finally:
                cloud.flush()
                if export_meter:
                    save_new(STORE/'service'/f'{phase}.json',{
                        'maximum_units':export_meter.limit-previously_exported,'admitted_units':export_meter.spent-previously_exported,
                        'runtime_units_admitted':runtime_meter.spent,
                        'stopped':export_meter.exhausted or runtime_meter.exhausted})
            if export_meter and (export_meter.exhausted or runtime_meter.exhausted):
                raise RuntimeError('Service limit reached; no continuation')
            capture=read(STORE/'runs'/phase/'trace-capture.json')
            prior_runtime_units += max(len(capture['observations'])+len(capture['trace_ids'])+len(capture['scores']),
                                       export_meter.spent - previously_exported if export_meter else 0)
            verify_current()
            verify_prior(ROOT)
            print(json.dumps({k:result[k] for k in ('phase','status','notes','questions','evolution_counter',
                'error_type','recoverable_length_failure','budget')}),flush=True)
            if result['status'] in ('complete','degraded'):
                _verified_receipt(preflight,ROOT/'artifacts/assets',ROOT)
                close = recovery_finance.reconcile_child if recovery else reconcile
                close(client,ledger,STORE/'reconciliation.json',opening)
                return
            if not result['recoverable_length_failure']:raise RuntimeError('Material failure; paid frontier closed')
            parent=result
    raise RuntimeError('Finite original-turn continuation bound exhausted')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--prepare-reconstruction', action='store_true')
    parser.add_argument('--gate')
    parser.add_argument('--reviewed-commit');parser.add_argument('--merge-commit')
    parser.add_argument('--cell',choices=FULL_CELLS,default='conv-44')
    parser.add_argument('--condition',choices=('full',*ABLATION_CONDITIONS),default='full')
    parser.add_argument('--pr48-recovery', action='store_true')
    args=parser.parse_args()
    CELL=args.cell;CONDITION=args.condition;KEY=cell_key(CELL,CONDITION);STORE=cell_store(DIRECTORY,KEY)
    VERIFICATION=(DIRECTORY/'verification/blk027-release' if KEY in ('neither-conv-44','linking_only-conv-50','linking_only-conv-44') else DIRECTORY/'verification/six-cell-release-v2' if KEY in EXPANSION_CELLS else DIRECTORY/'verification/conv49-ablation-release' if CONDITION!='full' else
                  FIRST_VERIFY if CELL=='conv-44' else DIRECTORY/'verification/remaining-full-release')
    if args.prepare_reconstruction and not args.pr48_recovery:
        parser.error('Reconstruction requires --pr48-recovery')
    try:
        if args.pr48_recovery:
            if KEY != 'linking_only-conv-44':
                raise RuntimeError('PR #48 authorises only Linking Only / conv-44')
            from scripts import gpt4omini_linking44_release as recovery_release
            VERIFICATION = DIRECTORY / recovery_release.DIRECTORY
            if args.prepare_reconstruction:
                from amem_repro.linking44_reconstruction import SUPPLEMENT, reconstruct
                from amem_repro.openrouter import save_new
                recovery_release.verify_preparation(ROOT, args.reviewed_commit, args.merge_commit)
                output = DIRECTORY / SUPPLEMENT
                if output.exists():
                    raise RuntimeError('The operational reconstruction is already sealed')
                save_new(output, reconstruct(ROOT, DIRECTORY))
            elif args.execute:
                execute(recovery=True)
            else:
                recovery_release.freeze(ROOT, args.reviewed_commit, args.merge_commit)
        elif args.execute:execute()
        else:freeze(args.gate,args.reviewed_commit,args.merge_commit)
    except BaseException as error:
        # Never print request headers, credentials, or arbitrary SDK exception text.
        from amem_repro.openrouter import save_new
        path=DIRECTORY/'driver-errors'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ.json')
        save_new(path,{'error_type':type(error).__name__,'message':'Execution stopped; original local phase evidence retained'})
        raise SystemExit('GPT-4o-mini campaign stopped; no automatic restart or extra cell.')
