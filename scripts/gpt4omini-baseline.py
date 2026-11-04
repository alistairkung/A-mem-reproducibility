"""Freeze/execute only the reviewed Full conv-44 GPT-4o-mini lineage, never another cell."""
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


def read(path):return json.loads(Path(path).read_bytes())


def verify_release(release):
    from amem_repro.config import fingerprint,source_fingerprint
    from amem_repro.gpt4omini_campaign import verify_inventory,verify_prior
    if (ROOT/'artifacts/gpt4omini').absolute()!=(ROOT/'artifacts/gpt4omini').resolve():
        raise RuntimeError('Paid campaign namespace cannot alias another artifact directory')
    if release.get('approved') is not True or release['binding']['campaign_id']!='amem-gpt4omini-openrouter-20261104-v1':
        raise RuntimeError('Explicit reviewed one-cell campaign approval required')
    if fingerprint(source_fingerprint(ROOT))!=release['binding']['source_sha256']:
        raise RuntimeError('Frozen campaign source changed')
    verify_inventory(ROOT,release['files'])
    for commit in (release['reviewed_commit'],release['merge_commit']):
        subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT,check=True,capture_output=True)
    for axis in ('standards','spec'):
        review=read(DIRECTORY/f'verification/baseline-{axis}-review.json')
        if review.get('verdict')!='pass' or review.get('reviewed_commit')!=release['reviewed_commit']:
            raise RuntimeError('Baseline independent review is not bound to this release')
    verify_prior()


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
    verify_inventory(Path(gate_path).parent,gate['files'])
    if gate.get('gate_script_sha256')!=hashlib.sha256((ROOT/'scripts/gpt4omini-gate.py').read_bytes()).hexdigest():
        raise RuntimeError('Executed cloud-gate script differs from this release')
    for name,digest in gate.get('fixture_files',{}).items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Executed native gate fixture changed')
    compatibility=read(DIRECTORY/'compatibility/receipt.json')
    if compatibility['status']!='complete' or compatibility['calls']!=6:
        raise RuntimeError('Six-call native compatibility not complete')
    files=dict(sources['files'])
    paths=[Path(gate_path),DIRECTORY/'compatibility/receipt.json',DIRECTORY/'compatibility/plan-v2.json',
        DIRECTORY/'verification/baseline-preflight.json',DIRECTORY/'verification/baseline-full-suite.txt',
        DIRECTORY/'verification/baseline-standards-review.json',DIRECTORY/'verification/baseline-spec-review.json',
        DIRECTORY/'verification/archive-equivalence.json',
        ROOT/'scripts/gpt4omini-baseline.py',ROOT/'scripts/gpt4omini-gate.py',
        ROOT/'tests/gpt4omini_fixture.py',ROOT/'tests/gpt4omini_executor_fixture.py',
        ROOT/'tests/test_gpt4omini_executor.py',ROOT/'tests/test_gpt4omini_full_executor.py']
    for path in paths:files[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    suite=(DIRECTORY/'verification/baseline-full-suite.txt').read_text()
    if not re.search(r'(?m)^\d+ passed.*$',suite) or re.search(r'\b\d+ (failed|errors)\b',suite):
        raise RuntimeError('Whole frozen-source offline suite did not pass')
    replay=read(DIRECTORY/'verification/archive-equivalence.json')
    if replay.get('verified') is not True:raise RuntimeError('Fixed full archive equivalence gate failed')
    binding={**SCIENTIFIC_BINDING,'source_sha256':fingerprint(sources),
        'manifest_sha256':fingerprint(read(ROOT/'manifests/fallback.json')),
        'condition':'full','conversation_id':'conv-44','population':'fallback','repetition':0,
        'provider_contract_policy':'strict-original-v1',
        'max_output_tokens_by_stage':stage_output_limits(OPENROUTER_CONFIG),
        'observability_policy':'run2-audit-essential-v1'}
    release={'approved':True,'approved_by':'User4 November2026 GPT-4o-mini handover; one Full/conv-44 only',
        'approved_at':datetime.now(timezone.utc).isoformat(),'binding':binding,'files':files,
        'reviewed_commit':reviewed_commit,'merge_commit':merge_commit,
        'limits':{'cell_microusd':5000000,'usable_campaign_microusd':42000000,
                  'protected_microusd':8000000,'max_baseline_calls':1666},
        'gate_path':str(Path(gate_path).relative_to(ROOT)),
        'forecast':read(DIRECTORY/'compatibility/plan-v2.json')['forecast']}
    verify_release(release)
    save_new(DIRECTORY/'frozen/campaign-approval.json',release)
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


def reconcile(client, ledger, output):
    from amem_repro.openrouter import BASE_URL,MODEL,save_new
    details=[]
    with ledger.transaction() as db:
        rows=db.execute('SELECT provider_id,reported_cost FROM attempts ORDER BY id').fetchall()
    for request_id,cost in rows:
        response=client.get(BASE_URL+'/generation',params={'id':request_id})
        response.raise_for_status();data=response.json()['data']
        if (data.get('provider_name')!='OpenAI' or data.get('model')!=MODEL
                or abs(Decimal(str(data['total_cost']))-Decimal(cost))>Decimal('0.000000001')):
            raise RuntimeError('Independent request route/charge mismatch')
        details.append(data)
    response=client.get(BASE_URL+'/credits');response.raise_for_status();credits=response.json()['data']
    reported=Decimal(ledger.totals()['reported_cost_usd'])
    if abs(Decimal(str(credits['total_usage']))-reported)>Decimal('0.000000001'):
        raise RuntimeError('OpenRouter aggregate spending differs from admitted generations')
    result={'verified':True,'generation_count':len(details),'generations':details,'credits':credits,
            'accounting':ledger.totals(),'rounding_tolerance_usd':'0.000000001'}
    save_new(output,result)
    return result


def execute():
    import httpx
    from amem_repro.config import fingerprint
    from amem_repro.openrouter import BASE_URL,MODEL,CampaignLedger,save_new
    from amem_repro.gpt4omini_campaign import execute_phase,verify_prior,read
    from amem_repro.measurements import TokenCounter
    from amem_repro.phases import _verified_receipt
    environment()
    release=read(DIRECTORY/'frozen/campaign-approval.json');verify_release(release)
    preflight=read(DIRECTORY/'verification/baseline-preflight.json')
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
    ledger=CampaignLedger(DIRECTORY/'budget.sqlite',campaign_root=DIRECTORY,binding=release['binding'])
    key=os.environ['OPENROUTER_API_KEY']
    with httpx.Client(headers={'Authorization':'Bearer '+key},timeout=120,
                      transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        client._amem_credential=key
        endpoint=client.get(BASE_URL+'/models/openai/gpt-4o-mini-2024-07-18/endpoints')
        endpoint.raise_for_status();data=endpoint.json()['data']
        provider=next(e for e in data['endpoints'] if e['tag']=='openai')
        if (data['id']!=MODEL or provider['context_length']!=128000 or provider['max_completion_tokens']!=16384
                or Decimal(provider['pricing']['prompt'])!=Decimal('.00000015')
                or Decimal(provider['pricing']['completion'])!=Decimal('.0000006')
                or not {'temperature','response_format','structured_outputs','max_tokens'}<=set(provider['supported_parameters'])):
            raise RuntimeError('Frozen provider route/pricing/capabilities changed')
        save_new(DIRECTORY/'frozen/route-before-baseline.json',endpoint.json())
        parent=None
        for sequence in range(676):
            verify_release(release)
            if ledger.totals()['unknown_attempts']:raise RuntimeError('Unknown exposure forbids continuation')
            phase=f'gpt4omini-full-conv44-r0-p{sequence}'
            approval={'approved':True,'approved_by':release['approved_by'],
                'approved_at':datetime.now(timezone.utc).isoformat(),'binding':release['binding'],
                'kind':'baseline','condition':'full','conversation':'conv-44','phase':phase,
                'release_sha256':fingerprint(release)}
            if parent:
                approval.update(parent=parent['phase'],parent_seal=fingerprint(parent),
                    parent_path=str(DIRECTORY/'runs'/parent['phase']/'phase.json'))
            save_new(DIRECTORY/'frozen'/(phase+'-approval.json'),approval)
            cloud=Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],secret_key=os.environ['LANGFUSE_SECRET_KEY'],
                base_url='https://cloud.langfuse.com',flush_at=16,should_export_span=should_export_span,
                environment='amem-gpt4omini',release=release['binding']['source_sha256'])
            observer=LangfuseObserver(cloud,{**release['binding'],'run_id':phase,
                'execution_mode':'paid-gpt4omini-baseline','parent_run_id':parent['phase'] if parent else None})
            try:
                result=execute_phase(approval,ledger,observer=observer,client=client,token_counter=counter,root=ROOT)
            finally:cloud.shutdown()
            verify_release(release)
            verify_prior()
            print(json.dumps({k:result[k] for k in ('phase','status','notes','questions','evolution_counter',
                'error_type','recoverable_length_failure','budget')}),flush=True)
            if result['status'] in ('complete','degraded'):
                _verified_receipt(preflight,ROOT/'artifacts/assets',ROOT)
                reconcile(client,ledger,DIRECTORY/'reconciliation.json')
                return
            if not result['recoverable_length_failure']:raise RuntimeError('Material failure; paid frontier closed')
            parent=result
    raise RuntimeError('Finite original-turn continuation bound exhausted')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true');parser.add_argument('--gate')
    parser.add_argument('--reviewed-commit');parser.add_argument('--merge-commit')
    args=parser.parse_args()
    try:
        if args.execute:execute()
        else:freeze(args.gate,args.reviewed_commit,args.merge_commit)
    except BaseException as error:
        # Never print request headers, credentials, or arbitrary SDK exception text.
        from amem_repro.openrouter import save_new
        path=DIRECTORY/'driver-errors'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ.json')
        save_new(path,{'error_type':type(error).__name__,'message':'Execution stopped; original local phase evidence retained'})
        raise SystemExit('GPT-4o-mini campaign stopped; no automatic restart or extra cell.')
