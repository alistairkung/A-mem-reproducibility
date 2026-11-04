"""Read-only, request-ID based reconciliation of the OpenRouter study ledger."""
from decimal import Decimal
from pathlib import Path
import time
from base64 import b64encode
from uuid import uuid4
from amem_repro.openrouter import BASE_URL, MODEL, save_new

def decimal(value):
    number=Decimal(str(value))
    if not number.is_finite():
        raise ValueError('Non-finite billing value')
    return number

def snapshot(client):
    values={}
    for endpoint,fields in [('credits',('total_usage','total_credits')),('key',('usage','limit_remaining'))]:
        response=client.get(BASE_URL+'/'+endpoint)
        response.raise_for_status()
        data=response.json()['data']
        values[endpoint]={key:str(decimal(data[key])) for key in fields}
    return values

def compare(opening,closing,known_before,known_after):
    delta=decimal(known_after)-decimal(known_before)
    account=decimal(closing['credits']['total_usage'])-decimal(opening['credits']['total_usage'])
    key=decimal(closing['key']['usage'])-decimal(opening['key']['usage'])
    credits=decimal(closing['credits']['total_credits'])-decimal(opening['credits']['total_credits'])
    return {'campaign_delta':str(delta),'account_usage_delta':str(account),'key_usage_delta':str(key),
            'unexplained_account_delta':str(account-delta),'unexplained_key_delta':str(key-delta),
            'credit_adjustment':str(credits),'verified':delta>=0 and account==key==delta and credits==0}

def verify_generations(client,rows,journal):
    results=[]
    seen=set()
    for index,(request_id,cost) in enumerate(rows):
        if not request_id or request_id in seen or cost is None:
            save_new(journal/f'{index}-invalid.json',{'id':request_id,'cost':cost})
            raise ValueError('Missing or duplicate settled generation')
        seen.add(request_id)
        for poll in range(9):
            path=journal/f'{index}-{poll}.json'
            try:
                response=client.get(BASE_URL+'/generation',params={'id':request_id})
            except Exception as exc:
                key=client.headers.get('Authorization','').removeprefix('Bearer ')
                message=str(exc).replace(key,'[redacted]') if key else str(exc)
                save_new(path,{'requested_id':request_id,'error':type(exc).__name__,'message':message})
                raise
            save_new(path,{'requested_id':request_id,'status':response.status_code,
                           'response_base64':b64encode(response.content).decode('ascii')})
            if response.status_code not in (404,429) or poll==8:break
            time.sleep(min(30,2**poll))
        response.raise_for_status()
        data=response.json()['data']
        hops=data.get('provider_responses') or []
        if (data.get('id')!=request_id or data.get('model')!=MODEL or data.get('provider_name')!='OpenAI'
                or len(hops)!=1 or hops[0].get('status')!=200 or hops[0].get('provider_name')!='OpenAI'
                or hops[0].get('model_permaslug')!=MODEL or decimal(data['total_cost'])!=decimal(cost)):
            raise ValueError('Generation identity, upstream attempt or charge differs')
        results.append(data)
    return results

def reconcile(client,ledger,output,opening):
    with ledger.transaction() as db:
        rows=db.execute("SELECT provider_id,reported_cost FROM attempts WHERE state='settled' ORDER BY id").fetchall()
    if ledger.unaccepted_unknowns(opening['approval']):
        raise ValueError('New unknown financial exposure')
    journal=Path(output).parent/('generation-readback-'+uuid4().hex)
    details=verify_generations(client,rows,journal)
    closing=snapshot(client)
    totals=ledger.totals()
    change=compare(opening['account'],closing,opening['reported_cost_usd'],totals['reported_cost_usd'])
    record={'verified':change['verified'],'generations':details,'generation_count':len(details),
            'generation_journal':str(journal),'opening':opening,'closing':closing,'movement':change,'accounting':totals}
    save_new(output,record)
    if not change['verified']: raise ValueError('Unreconciled account or key movement')
    return record
