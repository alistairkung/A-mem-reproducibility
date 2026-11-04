"""Run the four remaining original-schema compatibility probes under the renewed grant."""
import hashlib
import json
import subprocess
import time
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from amem_repro.config import fingerprint, source_fingerprint
from amem_repro.gpt4omini_campaign import read, verify_prior
from amem_repro.openrouter import BASE_URL, MODEL, CampaignLedger, OpenRouterController, save_new

CAMPAIGN = ROOT / 'artifacts/gpt4omini'
OUT = CAMPAIGN / 'compatibility-release'
PLAN = CAMPAIGN / 'compatibility-v2/plan-v2.json'


def execute():
    import httpx
    from dotenv import dotenv_values
    approval = read(OUT / 'approval.json')
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if (approval['reviewed_commit'] != head or approval['binding']['source_sha256'] != fingerprint(source_fingerprint(ROOT))
            or approval['script_sha256'] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or fingerprint(read(PLAN)) != 'a4eb0f587fe50d7f64bee80993f77ada062b7a6bbb90da6527edb460546088a8'):
        raise RuntimeError('Reviewed source or frozen compatibility plan differs')
    for axis in ('standards','spec'):
        review = read(OUT / f'{axis}-review.json')
        if review['verdict'] != 'pass' or review['reviewed_commit'] != head or fingerprint(review) != approval['reviews'][axis]:
            raise RuntimeError('Source-bound independent review missing')
    verify_prior()
    key = dotenv_values(ROOT / '.env')['OPENROUTER_API_KEY']
    if hashlib.sha256(key.encode()).hexdigest() != read(CAMPAIGN/'compatibility-v5/private-credential-binding.json')['sha256']:
        raise RuntimeError('Verified credential differs')
    ledger = CampaignLedger(CAMPAIGN/'budget.sqlite', campaign_root=CAMPAIGN, binding=approval['binding'])
    probes = [read(PLAN)['probes'][i] for i in (2,3,4,5)]
    events = []
    def record(event):
        save_new(OUT/f'generation-{len(events)+1}.json',event)
        events.append(event)
    with httpx.Client(headers={'Authorization':'Bearer '+key}, timeout=120,
                      transport=httpx.HTTPTransport(retries=0), follow_redirects=False) as client:
        client._amem_credential = key
        phase = ledger.claim(approval)
        controller = OpenRouterController(client,ledger=ledger,phase=phase,journal=OUT/'raw',observer=record)
        error = None
        try:
            for i,probe in enumerate(probes):
                controller.get_completion(probe['prompt'],probe['response_format'],probe['temperature'])
                event = events[-1]
                for poll in range(4):
                    r = client.get(BASE_URL+'/generation', params={'id':event['request_id']})
                    save_new(OUT/f'provider-{i+1}-{poll}.json',{'status':r.status_code,'body':r.json()})
                    if r.status_code != 404 or poll==3: break
                    time.sleep(2**poll)
                r.raise_for_status()
                d = r.json()['data']
                if (d['id']!=event['request_id'] or d['provider_name']!='OpenAI' or d['model']!=MODEL
                        or Decimal(str(d['total_cost']))!=Decimal(str(event['usage']['cost']))):
                    raise RuntimeError('Generation identity or cost did not reconcile')
        except BaseException as exc:
            error = type(exc).__name__
            ledger.stop(phase,error)
        receipt = {'phase':phase,'status':'complete' if not error else 'incomplete','error':error,
                   'stages':[e['stage'] for e in events if e.get('raw_schema_valid')],
                   'calls':len(events),'budget':ledger.totals(),'source_sha256':approval['binding']['source_sha256']}
        save_new(OUT/'receipt.json',receipt)
        ledger.finish(phase,receipt,'terminal' if error else 'complete')
    verify_prior()
    print(json.dumps(receipt))
    if error: raise SystemExit(1)


if __name__=='__main__':
    execute()
