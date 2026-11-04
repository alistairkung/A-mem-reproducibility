"""Prepare or execute one reviewed six-call native-schema compatibility phase."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import subprocess
from datetime import datetime,timezone
from decimal import Decimal,ROUND_CEILING

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from amem_repro.config import fingerprint,source_fingerprint,OPENROUTER_CONFIG,stage_output_limits
from amem_repro.openrouter import (
    CAMPAIGN,MODEL,BASE_URL,SCIENTIFIC_BINDING,CampaignLedger,OpenRouterController,save_new,
)

OUTPUT=ROOT/'artifacts/gpt4omini/compatibility'


def read(path):
    return json.loads(Path(path).read_bytes())


def verify_prior():
    evidence=read(OUTPUT.parent/'verification/prior-preservation-authoritative-v2.json')
    legacy=Path(evidence['legacy_root']).resolve()
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=legacy,text=True).strip()!=evidence['legacy_commit']:
        raise RuntimeError('Historical source checkout changed')
    for name,digest in {**evidence['files'],**evidence['input_files']}.items():
        path=(legacy/name).resolve()
        if not path.is_relative_to(legacy) or hashlib.file_digest(path.open('rb'),'sha256').hexdigest()!=digest:
            raise RuntimeError('Preserved historical evidence changed')
    for name,target in evidence['symlinks'].items():
        path=legacy/name
        if not path.is_symlink() or os.readlink(path)!=target:
            raise RuntimeError('Historical artifact link changed')


def prepare():
    import tiktoken
    encoding=tiktoken.get_encoding('o200k_base')
    stages={}
    for phase in range(3):
        path=ROOT/f'artifacts/run2/runs/run2-full-conv-44-r0-p{phase}/events.jsonl'
        origin_hash=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
        for index,line in enumerate(path.open()):
            event=json.loads(line)
            if event.get('type')=='generation' and event.get('attempts'):
                stages.setdefault(event['stage'],[]).append({
                    'stage':event['stage'],'prompt':event['prompt'],
                    'response_format':event['response_format'],'temperature':event['temperature'],
                    'engineering_origin':str(path.relative_to(ROOT)), 'origin_line':index+1,
                    'origin_file_sha256':origin_hash,
                    'local_prompt_tokens':len(encoding.encode(event['prompt'],disallowed_special=()))})
    probes=[stages[s][0] for s in ('metadata','shared_decision','query_keywords','answer')]
    probes+=sorted(stages['shared_decision'],key=lambda e:e['local_prompt_tokens'],reverse=True)[:2]
    limits=stage_output_limits(OPENROUTER_CONFIG)
    rows={};total=Decimal('.25')
    for stage,events in stages.items():
        n=675 if stage in ('metadata','shared_decision') else 158
        maximum=max(e['local_prompt_tokens'] for e in events)
        # Large-prefix engineering stress, NOT imported GPT results or a hard bound.
        schema_tokens=len(encoding.encode(json.dumps(events[0]['response_format']),disallowed_special=()))
        overhead=2*schema_tokens+256
        prompt_allowance=int((Decimal(maximum)*Decimal('1.5')).to_integral_value(rounding=ROUND_CEILING))+overhead
        cost=Decimal(n)*(Decimal('.15')*prompt_allowance+Decimal('.60')*limits[stage])/1000000
        rows[stage]={'calls':n,'engineering_samples':len(events),'max_local_prompt_tokens':maximum,
                     'planning_prompt_tokens':prompt_allowance,'schema_local_tokens':schema_tokens,
                     'overhead_allowance':overhead,'all_outputs_at_cap':limits[stage],
                     'conservative_scenario_usd':str(cost)}
        total+=cost
    forecast={'campaign_id':CAMPAIGN,'pricing_input_per_million_usd':'.15',
        'pricing_output_per_million_usd':'.60','compatibility_allowance_usd':'.25',
        'stages':rows,'cell_conservative_scenario_usd':str(total),'fits_cell_cap':total<=5,
        'basis':'1.5x maximum o200k prompt count per stage plus twice native-schema tokens+256 overhead; every output at cap; '
                'DeepSeek prompts are separate engineering size evidence only, never GPT results; '
                'not a guaranteed upper bound; durable per-request/cell caps remain authoritative'}
    save_new(OUTPUT/'plan-v2.json',{'probes':probes,'forecast':forecast,'model_calls':6})
    print(json.dumps(forecast),flush=True)


def execute():
    import httpx
    from dotenv import dotenv_values
    approval=read(OUTPUT/'approval.json');plan=read(OUTPUT/'plan-v2.json')
    actual_source=fingerprint(source_fingerprint(ROOT))
    if (approval['binding']['source_sha256']!=actual_source
            or approval['plan_sha256']!=fingerprint(plan)
            or approval['script_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or not plan['forecast']['fits_cell_cap'] or len(plan['probes'])!=6):
        raise RuntimeError('Reviewed compatibility plan/source/script/affordability changed')
    for axis in ('spec','standards'):
        review=read(ROOT/f'artifacts/gpt4omini/verification/compatibility-{axis}-review.json')
        if (review.get('verdict')!='pass' or review.get('reviewed_commit')!=approval['reviewed_commit']
                or fingerprint(review)!=approval.get('review_receipts',{}).get(axis)):
            raise RuntimeError('Independent reviewed-source proof missing')
    for name,digest in source_fingerprint(ROOT)['files'].items():
        blob=subprocess.check_output(['git','show',approval['reviewed_commit']+':'+name],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=digest:
            raise RuntimeError('Current sources differ from the reviewed immutable commit')
    if subprocess.check_output(['git','show',approval['reviewed_commit']+':scripts/gpt4omini-compatibility.py'],cwd=ROOT)!=Path(__file__).read_bytes():
        raise RuntimeError('Compatibility launcher differs from reviewed commit')
    if fingerprint(read(OUTPUT.parent/'verification/prior-preservation-authoritative-v2.json'))!=approval.get('preservation_sha256'):
        raise RuntimeError('Approved historical preservation evidence changed')
    verify_prior()
    values=dotenv_values(ROOT/'.env');key=values.get('OPENROUTER_API_KEY')
    if not key:raise RuntimeError('Private OpenRouter credential missing')
    ledger=CampaignLedger(OUTPUT.parent/'budget.sqlite',campaign_root=OUTPUT.parent,binding=approval['binding'])
    phase=ledger.claim(approval);events=[];error=None
    def record(event):
        save_new(OUTPUT/f'generation-{len(events)+1}.json',event);events.append(event)
    with httpx.Client(headers={'Authorization':'Bearer '+key},timeout=120,
                      transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        client._amem_credential=key
        controller=OpenRouterController(client,ledger=ledger,phase=phase,journal=OUTPUT/'raw',observer=record)
        try:
            for probe in plan['probes']:
                controller.get_completion(probe['prompt'],probe['response_format'],probe['temperature'])
                print(json.dumps({'stage':probe['stage'],'request_id':events[-1]['request_id'],
                    'provider':events[-1]['actual_provider'],'model':events[-1]['returned_model'],
                    'usage':events[-1]['usage']}),flush=True)
            details=[]
            for event in events:
                response=client.get(BASE_URL+'/generation',params={'id':event['request_id']})
                save_new(OUTPUT/(event['request_id']+'-details.json'),
                         {'status':response.status_code,'body':response.json()})
                response.raise_for_status();data=response.json()['data']
                if (data.get('provider_name')!='OpenAI' or data.get('model')!=MODEL
                        or Decimal(str(data.get('total_cost')))!=Decimal(str(event['usage']['cost']))):
                    raise RuntimeError('Independent generation route/charge reconciliation failed')
                details.append(data)
            credits=client.get(BASE_URL+'/credits');credits.raise_for_status()
            save_new(OUTPUT/'credits-after.json',credits.json())
            if Decimal(str(credits.json()['data']['total_usage']))!=Decimal(ledger.totals()['reported_cost_usd']):
                raise RuntimeError('Account aggregate and exact generation charges do not reconcile')
        except BaseException as exc:
            error=type(exc).__name__
            ledger.stop(phase,error)
    receipt={'campaign_id':CAMPAIGN,'phase':phase,'status':'incomplete' if error else 'complete',
             'error_type':error,'calls':len(events),'budget':ledger.totals(),
             'native_contracts_verified':sorted({e['stage'] for e in events if e.get('raw_schema_valid')}),
             'max_shared_output_tokens':max((e['usage']['completion_tokens'] for e in events
                        if e['stage']=='shared_decision' and e.get('usage')),default=0),
             'completed_at':datetime.now(timezone.utc).isoformat()}
    save_new(OUTPUT/'receipt.json',receipt)
    ledger.finish(phase,receipt,'terminal' if error else 'complete')
    verify_prior()
    print(json.dumps(receipt),flush=True)
    if error:raise SystemExit('Compatibility stopped; immutable error/charges retained')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--directory',default=str(OUTPUT))
    args=parser.parse_args()
    proposed=Path(args.directory).absolute()
    if (proposed!=proposed.resolve() or proposed.parent!=(ROOT/'artifacts/gpt4omini').resolve()
            or not re.fullmatch(r'compatibility(?:-v[2-9][0-9]*)?',proposed.name)):
        raise SystemExit('Compatibility requires a canonical campaign subdirectory')
    OUTPUT=proposed
    if args.execute:execute()
    else:prepare()
