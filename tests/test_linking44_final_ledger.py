"""Offline physical admission, retry identity, year-independent deadlines and durable credits."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
import base64
import copy
import json
import sqlite3

import httpx
import pytest

from amem_repro import linking44_final_ledger as fin
from amem_repro.budget import BudgetStop
from amem_repro.config import OPENROUTER_CONFIG, fingerprint
from amem_repro.openrouter import SCIENTIFIC_BINDING, MODEL, save_new


def read(p):return json.loads(p.read_bytes())
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,sort_keys=True))


@pytest.fixture
def env(tmp_path,monkeypatch):
    c=tmp_path/'campaign';c.mkdir()
    old=c/'budget.sqlite';old.write_bytes(b'offline immutable opening')
    monkeypatch.setattr(fin,'opening_history',lambda campaign:(old,fin.signature(old),frozenset({'gen-original-frozen'})))
    fixed=datetime(2026,11,8,1,25,tzinfo=timezone.utc);monkeypatch.setattr(fin,'now',lambda:fixed)
    account={'credits':{'total_credits':'50','total_usage':'4.31925395'},'key':{'usage':'4.30760295','limit_remaining':'45.69239705'}}
    put(c/fin.R1_CLOSE,{'closing':account})
    def prepare(n=1):
        store=fin.attempt_store(c,n)
        prior=c/fin.R1_CLOSE if n==1 else fin.attempt_store(c,n-1)/'reconciliation.json'
        opening=read(prior)['closing'] if prior.is_file() else account
        a={'approved':True,'kind':'final_fresh','group':fin.GROUP,'ordinal':n,'repetition':3+n,'phase':fin.phase_id(n),
           'conversation':'conv-44','condition':'linking_only','binding':{**SCIENTIFIC_BINDING,'condition':'linking_only','conversation_id':'conv-44'},
           'release_sha256':'a'*64,'service_reserve_microusd':1080000,'opening_account':opening}
        put(store/'frozen/approval.json',a)
        def verify(v):
            if v!=a or v!=read(store/'frozen/approval.json'):raise BudgetStop('test approval mismatch')
        return fin.FinalLedger(c,a,verify_approval=verify),a
    return c,prepare


def start(env,n=1):
    l,a=env[1](n)
    p=l.claim(a)
    l.observe_phase(p,lambda:None)
    l.set_guard(p,lambda db:None)
    return l,p


def body(l,stage,text='frozen prompt'):
    return {'model':MODEL,'max_tokens':4096 if stage=='shared_decision' else 1000,'temperature':.7,
            'provider':copy.deepcopy(OPENROUTER_CONFIG['model']['provider']),'response_format':l.contracts[stage],'messages':[{'role':'user','content':text}]}


def paid(l,p,stage,*,previous=None):
    b=body(l,stage)
    (idx,hold)=l.reserve(p,stage,b) if previous is None else l.reserve_retry(p,stage,b,previous)
    folder=fin.attempt_store(l.root,l.claimed[p]['ordinal'])/'runs'/p/'raw'
    save_new(folder/f'{idx:06d}-request.json',b)
    return b,idx,hold,folder


def mark(l,p,operation):
    b,idx,hold,folder=operation
    event={'stage':next(k for k,v in l.contracts.items() if v==b['response_format']),'budget_logical_id':idx,
           'error_type':'RemoteProtocolError','error_message':'Server disconnected without sending a response.',
           'attempts':[{'budget_attempt_id':idx,'request_body':b,'status_code':None,'error_type':'RemoteProtocolError','response_body':None}]}
    file=folder/f'{idx:06d}-failure.json';save_new(file,event)
    proof={'kind':'transport','stage':event['stage'],'attempt_id':idx,'request_sha256':fingerprint(b),
           'physical_evidence_file':str(file),'physical_evidence_sha256':fin.sha(file)}
    l.record_failure(p,idx,proof);return proof


def settle(l,operation):
    b,idx,_,folder=operation
    response={'id':f'gen-{idx}','model':MODEL,'provider':'OpenAI','usage':{'prompt_tokens':10,'completion_tokens':10,'cost':.0000075}}
    save_new(folder/f'{idx:06d}-response.bin',response); assert l.settle(idx,response,b['max_tokens'])==8
    return response


def test_response_less_retry_charges_and_recovery_of_logical_order(env):
    l,p=start(env); first=paid(l,p,'metadata')
    assert first[1:3]==(19483,19650)
    mark(l,p,first); assert l.unaccepted_unknowns(l.claimed[p])==0
    second=paid(l,p,'metadata',previous=first[1]);settle(l,second)
    third=paid(l,p,'shared_decision'); assert third[1:3]==(19485,21044)
    assert l.logical_count(p)==2 and l.retry_count(p)==1
    assert l.totals()['unknown_attempts']==2
    with pytest.raises(BudgetStop):l.settle(first[1],{'id':'gen-late'},1000)


@pytest.mark.parametrize('mutation',['changed prompt','repeated retry','no recognized failure','foreign phase','unresolved next slot',
                                    'new retry without six capacity','tampered evidence','wrong stage','unexpected schema','late'])
def test_unsafe_physical_transmissions_never_admitted(env,monkeypatch,mutation):
    l,p=start(env);first=paid(l,p,'metadata')
    if mutation=='no recognized failure':
        with pytest.raises(BudgetStop):l.reserve_retry(p,'metadata',first[0],first[1])
        return
    evidence=mark(l,p,first)
    if mutation=='tampered evidence':Path(evidence['physical_evidence_file']).write_text('{}')
    elif mutation=='late':monkeypatch.setattr(fin,'now',lambda:fin.PAID_DEADLINE)
    elif mutation=='changed prompt':first[0]['messages'][0]['content']='different'
    elif mutation=='unexpected schema':first[0]['response_format']={}
    elif mutation=='foreign phase':p=fin.phase_id(2)
    elif mutation=='repeated retry':
        second=paid(l,p,'metadata',previous=first[1]);mark(l,p,second);first=second
    elif mutation=='unresolved next slot':
        with pytest.raises(BudgetStop):l.reserve(p,'shared_decision',body(l,'shared_decision'))
        return
    elif mutation=='new retry without six capacity':
        # Simulate upstream occupancy, including earlier phases, and accept that
        # image as the opening digest. The independent SQL cap still applies.
        with l.transaction() as db:
            for i in range(6):db.execute('insert into final_slots values(?,?,?,?,?)',(-i-1,'earlier',i,1,-10-i))
            l.expected_digest=fin._journal_digest(db)
    with pytest.raises(BudgetStop):l.reserve_retry(p,'answer' if mutation=='wrong stage' else 'metadata',first[0],first[1])


def test_settled_cost_repricing_and_unknown_liability(env):
    l,p=start(env);first=paid(l,p,'metadata');settle(l,first)
    with l.transaction() as db:db.execute('update attempts set charge=0 where id=?',(first[1],))
    with pytest.raises(BudgetStop): l.reserve(p,'shared_decision',body(l,'shared_decision'))


def test_known_above_reservation_and_unidentified_liability_held(env):
    l,p=start(env);op=paid(l,p,'metadata')
    l.retain_reported_liability(p,op[1],'1.00000001')
    assert l.totals()['conservative_microusd']==1000001 and l.totals()['unknown_attempts']==1
    with pytest.raises(BudgetStop):l.reserve_retry(p,'metadata',op[0],op[1])


def test_known_overage_kept_settled_and_idempotently_held(env):
    l,p=start(env);op=paid(l,p,'metadata')
    resp={'id':'gen-known-price','usage':{'prompt_tokens':1,'completion_tokens':1,'cost':1.0}}
    with pytest.raises(BudgetStop):l.settle(op[1],resp,1000)
    l.retain_reported_liability(p,op[1],'.1')
    assert l.totals()['reported_cost_usd']=='1.0' and l.totals()['conservative_microusd']==1000000
    assert l.totals()['unknown_attempts']==0


def test_money_bound_includes_earmark_and_external_wallet(env,monkeypatch):
    l,p=start(env)
    monkeypatch.setitem(fin.GROUP_LIMITS,'group_microusd',1080000+19649)
    with pytest.raises(BudgetStop):l.reserve(p,'metadata',body(l,'metadata'))


def test_deadline_and_unissued_ordinal(env,monkeypatch):
    l,a=env[1](2)
    with pytest.raises((BudgetStop,FileNotFoundError)):l.claim(a)
    l,a=env[1](1);monkeypatch.setattr(fin,'now',lambda:fin.PAID_DEADLINE)
    with pytest.raises(BudgetStop):l.claim(a)


def test_cumulative_residual_is_bounded_not_charge_attribution():
    account=lambda n:{'credits':{'total_credits':'50','total_usage':str(n)},'key':{'usage':str(n),'limit_remaining':str(Decimal(50)-n)}}
    x=account(Decimal(0));closing=account(Decimal('.021'))
    m,ok=fin._movement(x,closing,Decimal('.002'),19650)
    assert ok and not m['verified'] and Decimal(m['unexplained_account_delta'])==Decimal('.019')
    assert not fin._movement(x,account(Decimal('.022')),Decimal('.002'),19650)[1]


def test_financial_deadline_prevents_any_late_get(env,monkeypatch):
    class NoNetwork:
        headers={}
        def get(self,*args,**kwargs): raise AssertionError('unexpected HTTP')
    reader=fin._DeadlineReads(NoNetwork(),{'gen-known'})
    with pytest.raises(BudgetStop):reader.get(fin.BASE_URL+'/generation',params={'id':'gen-foreign'})
    monkeypatch.setattr(fin,'now',lambda:fin.HARD_DEADLINE)
    with pytest.raises(BudgetStop):reader.get(fin.BASE_URL+'/key')


def test_non200_generation_hop_requires_its_exact_failed_known_physical_response(env):
    l,p=start(env);op=paid(l,p,'metadata');b,i,_,folder=op;resp=settle(l,op)
    e={'stage':'metadata','budget_logical_id':i,'error_type':'HTTPStatusError','returned_model':MODEL,'actual_provider':'OpenAI',
       'attempts':[{'budget_attempt_id':i,'request_body':b,'response_body':resp,'status_code':502,'charged_cost_usd':.0000075}]}
    save_new(folder/f'{i:06d}-failure.json',e)
    with l.transaction() as db: row=fin._current(db,p)[-1]
    store=fin.attempt_store(l.root,1)
    g={'id':resp['id'],'model':MODEL,'provider_name':'OpenAI','provider_responses':[{'status':502,'model_permaslug':MODEL,'provider_name':'OpenAI'}]}
    fin._check_hop(store,p,row,g)
    g['provider_responses'][0]['status']=503
    with pytest.raises(BudgetStop):fin._check_hop(store,p,row,g)
    g['provider_responses'][0]['status']=200
    fin._check_hop(store,p,row,g)


def test_historical_generation_id_cannot_populate_final_run(env):
    l,p=start(env);op=paid(l,p,'metadata')
    with pytest.raises(BudgetStop): l.settle(op[1],{'id':'gen-original-frozen','usage':{'prompt_tokens':1,'completion_tokens':1,'cost':1}},1000)
    assert l.totals()['unknown_attempts']==1 and l.totals()['conservative_microusd']==1000000


@pytest.mark.parametrize('damage',[None,'wrong generation','wrong turn','unverified','wrong raw hash','wrong counter','reporting error'])
def test_second_settled_length_restart_requires_original_fallback(tmp_path,damage):
    row=[19488,'shared_decision','q',21044,1,'settled','h','{}','gen-length','0.000001']
    wire={'choices':[{'message':{'content':'truncated text'},'finish_reason':'length'}]}
    event={'attempts':[{'response_body':wire}],'error_type':'AdapterError'}
    gen={'type':'generation','budget_logical_id':19488,'turn_id':'D4:2'}
    outcome={'type':'evolution_outcome','turn_id':'D4:2','changed_existing_note_ids':[],'counter_before':3,'counter_after':3}
    import hashlib
    proof={'type':'failure','kind':'original_evolution_fallback','provider_deviation':'length','turn_id':'D4:2',
           'original_fallback_verified':True,'provider_output_accepted':False,'before_state_sha256':'a'*64,'after_state_sha256':'b'*64,
           'raw_arguments_sha256':hashlib.sha256(b'truncated text').hexdigest()}
    entries=[gen,outcome,proof]
    if damage=='wrong generation':gen['budget_logical_id']=19487
    elif damage=='wrong turn':outcome['turn_id']='D4:1'
    elif damage=='unverified':proof['original_fallback_verified']=False
    elif damage=='wrong raw hash':proof['raw_arguments_sha256']='c'*64
    elif damage=='wrong counter':outcome['counter_after']=4
    elif damage=='reporting error':entries.append({'type':'failure','kind':'reporting'})
    (tmp_path/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in entries))
    if damage is None:fin._length_fallback(tmp_path,row,event)
    else:
        with pytest.raises(BudgetStop):fin._length_fallback(tmp_path,row,event)


def test_unknown_operational_close_rolls_forward_only_with_original_gets(env):
    l,p=start(env);c=l.root;store=fin.attempt_store(c,1);out=store/'runs'/p
    # One settled request and two failed transmissions for the next logical slot.
    ok=paid(l,p,'metadata');resp=settle(l,ok)
    bad=paid(l,p,'shared_decision');mark(l,p,bad)
    retry=paid(l,p,'shared_decision',previous=bad[1]);mark(l,p,retry)
    l.stop(p,'RemoteProtocolError')
    capture={'observations':[{'trace_id':'t'}],'trace_ids':['t'],'scores':[],'errors':[]}
    save_new(out/'trace-capture.json',capture)
    proof=out/'langfuse-verified.json'
    save_new(proof,{'verified':True,'identity':{'run_id':p}})
    receipt={'phase':p,'status':'incomplete','error_type':'BudgetStop','notes':0,'questions':0,
             'observations':{'verified':True,'evidence_path':str(proof),'evidence_sha256':fin.sha(proof)},
             'files':{str(f.relative_to(out)):fin.sha(f) for f in out.rglob('*') if f.is_file()}}
    save_new(out/'phase.json',receipt);l.finish(p,receipt,'terminal')
    save_new(store/'service'/f'{p}.json',{'runtime_units_admitted':2,'admitted_units':2,'maximum_units':13500,'stopped':False})
    opening=l.claimed[p]['opening_account'];gross=Decimal('.0090075') # unknown aggregate .009 bounded by .042088.
    closing={'credits':{'total_credits':'50','total_usage':str(Decimal(opening['credits']['total_usage'])+gross)},
             'key':{'usage':str(Decimal(opening['key']['usage'])+gross),'limit_remaining':str(Decimal(opening['key']['limit_remaining'])-gross)}}
    for endpoint,fields in opening.items():
        save_new(store/'opening-reads'/f'{endpoint}.json',{'endpoint':endpoint,'params':{},'status':200,
                 'response_base64':base64.b64encode(json.dumps({'data':fields}).encode()).decode()})
    def handler(r):
        assert r.method=='GET'
        endpoint=r.url.path.rsplit('/',1)[-1]
        if endpoint=='generation':
            assert r.url.params['id']==resp['id']
            return httpx.Response(200,json={'data':{'id':resp['id'],'model':MODEL,'provider_name':'OpenAI','total_cost':.0000075,
                      'native_tokens_prompt':10,'native_tokens_completion':10,'provider_responses':[{'status':200,'provider_name':'OpenAI','model_permaslug':MODEL}]}})
        return httpx.Response(200,json={'data':closing[endpoint]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        record=fin.close_attempt(client,l,p,store,receipt,opening,2)
    assert record['verified'] and record['restart_eligible'] and not record['known_only_exact_movement']
    assert record['unknown_attempt_ids']==[bad[1],retry[1]] and record['group_unresolved_reservations_microusd']==42088
    assert fin.classify_restart(c,p)
    # Archive tampering, despite a still-valid sealed scientific phase and untouched SQL, blocks a successor.
    journal=store/'financial-readbacks';page=read(journal/'0-0.json');page['response_base64']=base64.b64encode(b'{"data":{}}').decode()
    put(journal/'0-0.json',page)
    assert not fin.classify_restart(c,p)
    l2,a2=env[1](2)
    with pytest.raises(BudgetStop):l2.claim(a2)
