"""One new-user-authorized exact metadata access probe, retaining the original403."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from amem_repro.config import fingerprint,source_fingerprint
from amem_repro.openrouter import BASE_URL,CampaignLedger,OpenRouterController,save_new


def read(p): return json.loads(p.read_bytes())


def execute():
    import httpx
    from dotenv import dotenv_values
    out=ROOT/'artifacts/gpt4omini/compatibility-v3'
    approval=read(out/'approval.json')
    source=fingerprint(source_fingerprint(ROOT))
    if (approval['binding']['source_sha256']!=source
            or approval['script_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
        raise RuntimeError('Reviewed access-probe source/script changed')
    for axis in ('standards','spec'):
        review=read(out/f'{axis}-review.json')
        if (review.get('verdict')!='pass' or review.get('reviewed_commit')!=approval['reviewed_commit']
                or fingerprint(review)!=approval['review_receipts'][axis]):
            raise RuntimeError('Independent exact access-probe review missing')
    for name,digest in source_fingerprint(ROOT)['files'].items():
        blob=subprocess.check_output(['git','show',approval['reviewed_commit']+':'+name],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=digest:raise RuntimeError('Reviewed source bytes differ')
    if subprocess.check_output(['git','show',approval['reviewed_commit']+':scripts/gpt4omini-access-retest.py'],cwd=ROOT)!=Path(__file__).read_bytes():
        raise RuntimeError('Reviewed access launcher differs')
    for name,digest in approval['evidence_files'].items():
        if hashlib.file_digest((ROOT/name).open('rb'),'sha256').hexdigest()!=digest:
            raise RuntimeError('Retained access/provenance evidence differs')
    prior=ROOT/'artifacts/gpt4omini/compatibility-v2'
    request=read(prior/'raw/000001-request.json')
    raw=read(prior/'raw/000001-response.bin')
    if (raw.get('error',{}).get('code')!=403
            or raw['error'].get('message')!='The request is prohibited due to a violation of provider Terms Of Service.'
            or fingerprint(request)!=approval['access_retest']['request_sha256']):
        raise RuntimeError('Not the exact original denied metadata request')
    spec=importlib.util.spec_from_file_location('compatibility_preservation',ROOT/'scripts/gpt4omini-compatibility.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUTPUT=out;module.verify_prior()
    key=dotenv_values(ROOT/'.env').get('OPENROUTER_API_KEY')
    if not key or hashlib.sha256(key.encode()).hexdigest()!=read(out/'private-credential-binding.json')['sha256']:
        raise RuntimeError('Authenticated private credential changed')
    ledger=CampaignLedger(out.parent/'budget.sqlite',campaign_root=out.parent,binding=approval['binding'])
    phase=ledger.claim(approval);events=[];error=None
    def record(event):
        save_new(out/f'generation-{len(events)+1}.json',event);events.append(event)
    ledger.set_guard(phase,lambda db:module.verify_prior())
    with httpx.Client(headers={'Authorization':'Bearer '+key},timeout=120,
                      transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
        client._amem_credential=key
        controller=OpenRouterController(client,ledger=ledger,phase=phase,journal=out/'raw',observer=record)
        try:
            controller.get_completion(request['messages'][1]['content'],request['response_format'],request['temperature'])
        except BaseException as exc:
            error=type(exc).__name__;ledger.stop(phase,error)
    receipt={'campaign_id':approval['binding']['campaign_id'],'phase':phase,'status':'incomplete' if error else 'access-probe-complete',
             'error_type':error,'calls':len(events),'budget':ledger.totals(),
             'native_contracts_verified':sorted({e['stage'] for e in events if e.get('raw_schema_valid')}),
             'baseline_released':False,'prior_unknown_reservation_retained':True,
             'completed_at':datetime.now(timezone.utc).isoformat()}
    save_new(out/'receipt.json',receipt);ledger.finish(phase,receipt,'terminal' if error else 'complete')
    module.verify_prior();print(json.dumps(receipt),flush=True)
    if error:raise SystemExit('Access probe stopped; all original evidence/reservations retained')


if __name__=='__main__':execute()
