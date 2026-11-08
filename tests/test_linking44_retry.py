"""Final campaign physical retries: one author return and durable evidence for every wire try."""
import copy
import hashlib
import json
from decimal import Decimal

import httpx
import pytest

from amem_repro.adapter import AdapterError
from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.contracts import load_author_contracts
from amem_repro.linking44_retry import FinalController
from amem_repro.observability import LangfuseObserver
from amem_repro.openrouter import MODEL, usage_charge
from test_observability import Client, identity
from test_openrouter import VALUES


@pytest.fixture(autouse=True)
def backoff(monkeypatch):
    sleeps = []
    monkeypatch.setattr('amem_repro.linking44_retry.time.sleep', sleeps.append)
    return sleeps


class Ledger:
    """All physical rows start fully reserved. The finance tests exercise the production ledger."""
    def __init__(self):
        self.rows = []
        self.failures = []
        self.halts = []
        self.allow_retry = True
        self.retained = []

    def reserve(self, phase, stage, body):
        assert not self.halts
        self.rows.append([copy.deepcopy(body), 21044 if stage == 'shared_decision' else 19650, None])
        return len(self.rows), self.rows[-1][1]

    def settle(self, attempt, raw, limit):
        charge = usage_charge(raw['usage'], limit)
        self.rows[attempt-1][2] = charge
        if charge > self.rows[attempt-1][1]:
            raise BudgetStop('Known liability exceeds its reservation')
        return charge

    def retain_reported_liability(self, phase, attempt, amount):
        self.retained.append((attempt, amount))

    def reserve_retry(self, phase, stage, body, previous):
        assert self.failures[-1]['attempt_id'] == previous
        assert self.rows[previous-1][0] == body and not self.halts
        if not self.allow_retry:
            raise BudgetStop('Insufficient remaining model or service allowance')
        return self.reserve(phase, stage, body)

    def record_failure(self, phase, attempt, evidence):
        self.failures.append(evidence)

    def stop(self, phase, reason):
        self.halts.append(reason)


def run(tmp_path, stage, replies, cloud=False):
    calls = []
    def respond(request):
        calls.append(json.loads(request.content))
        mode = replies[len(calls)-1]
        if mode == 'timeout':
            raise httpx.ReadTimeout('native read timeout')
        if mode == 'disconnect':
            raise httpx.RemoteProtocolError('peer disconnected')
        if mode in (502, 429, 401):
            return httpx.Response(mode, content=b'gateway failure')
        raw = {'id':f'gen-{len(calls)}','model':MODEL,'provider':'OpenAI',
               'choices':[{'finish_reason':'stop','message':{'content':json.dumps(VALUES[stage])}}],
               'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':0.000021}}
        if mode in ('billed-502','expensive-502','unidentified-502','bad-usage-200'):
            if mode != 'billed-502':raw['usage']['cost']=1
            if mode=='unidentified-502':del raw['id']
            if mode=='bad-usage-200':del raw['usage']['completion_tokens']
            return httpx.Response(200 if mode=='bad-usage-200' else 502,json=raw)
        if mode == 'empty-choices':
            raw['choices'] = []
            return httpx.Response(200, json=raw)
        choice = raw['choices'][0]
        if mode == 'absent-message':
            del choice['message']
            return httpx.Response(200, json=raw)
        if mode in ('error','length','content_filter'):
            choice.update(finish_reason=mode);choice['message']['content']='{"x":'
        if mode == 'malformed':
            choice['message']['content']='{"x" [}'
        if mode == 'truncated':
            choice['message']['content']='{"x":'
        if mode == 'wrong-schema':
            choice['message']['content']='{"unexpected": true}'
        if mode == 'refusal':
            choice['message']['refusal']='declined'
        if mode == 'foreign':
            raw['provider']='other'
        return httpx.Response(200,json=raw)
    ledger = Ledger()
    native = httpx.Client(transport=httpx.MockTransport(respond))
    events = []
    observer = None
    if cloud:
        observer=LangfuseObserver(Client(),{**identity(),'observability_policy':'run2-audit-essential-v1'})
    def record(event):
        events.append(event)
        if observer:
            observer({**event,'type':'generation','question_id':'conv-44:qa:0'})
    if observer:
        record.begin_generation=lambda event:observer.begin_generation({**event,'question_id':'conv-44:qa:0'})
    c=FinalController(native,ledger=ledger,phase='fixture',journal=tmp_path/'raw',observer=record)
    return c,ledger,calls,events,observer


@pytest.mark.parametrize('stage',['metadata','shared_decision','query_keywords','answer'])
@pytest.mark.parametrize('failure,kind',[
    ('error','provider_error'),('length','invalid_output'),('truncated','invalid_output'),
    ('wrong-schema','invalid_output'),('timeout','transport'),('disconnect','transport'),
    (502,'transient_http'),(429,'transient_http'),('empty-choices','invalid_output'),('absent-message','invalid_output'),
])
def test_physical_retry_returns_one_original_result(tmp_path,stage,failure,kind,backoff):
    c,ledger,calls,events,_=run(tmp_path,stage,[failure,'valid'])
    result=c.get_completion('unchanged',load_author_contracts()[stage],.5 if stage=='answer' else .7)
    assert result==json.dumps(VALUES[stage]) and c.pending is None
    assert len(calls)==2 and calls[0]==calls[1] and backoff==[2]
    assert len(events)==1 and not events[0]['error_type'] and events[0]['budget_logical_id']==2
    assert len(events[0]['attempts'])==2 and [r['attempt'] for r in events[0]['attempts']]==[1,2]
    assert ledger.failures[0]['kind']==kind and not ledger.halts
    saved=tmp_path/'raw/000001-failure.json'; event=json.loads(saved.read_bytes())
    assert event['error_type'] and event['attempts'][0]['request_body']==calls[0]
    assert hashlib.sha256(saved.read_bytes()).hexdigest()==ledger.failures[0]['physical_evidence_sha256']
    assert ledger.failures[0]['request_sha256']==fingerprint(calls[1])
    if failure in ('timeout','disconnect',502,429):
        assert ledger.rows[0][2] is None
    else:
        assert ledger.rows[0][2]==21
    assert events[0]['conservative_cost_usd']==float(
        Decimal((ledger.rows[0][2] if ledger.rows[0][2] is not None else ledger.rows[0][1])+21)/1000000)


@pytest.mark.parametrize('failure',['refusal','foreign','content_filter',401])
def test_unsupported_route_and_refusal_are_terminal(tmp_path,failure):
    c,l,calls,events,_=run(tmp_path,'answer',[failure])
    with pytest.raises(BudgetStop):
        c.get_completion('unchanged',load_author_contracts()['answer'])
    assert len(calls)==1 and not l.failures and l.halts and len(events)==1


def test_native_malformed_author_fallback_precedes_retry(tmp_path):
    c,l,calls,events,_=run(tmp_path,'shared_decision',['malformed'])
    contract=load_author_contracts()['shared_decision']
    with pytest.raises(AdapterError):c.get_completion('unchanged',contract)
    assert c.pending['kind']=='malformed' and len(calls)==1 and not l.halts and not l.failures
    assert events[0]['budget_logical_id']==c.pending['event']['budget_logical_id']==1
    with pytest.raises(BudgetStop):c.get_completion('again',contract)
    assert len(calls)==1


@pytest.mark.parametrize('second',['malformed','length'])
def test_retry_then_original_fallback_identifies_settled_last_attempt(tmp_path,second):
    c,l,calls,events,_=run(tmp_path,'shared_decision',['disconnect',second])
    with pytest.raises(AdapterError):c.get_completion('unchanged',load_author_contracts()['shared_decision'])
    assert len(calls)==2 and len(events)==1 and events[0]['error_type']=='AdapterError'
    assert c.pending['kind']==second and c.pending['event']['budget_logical_id']==events[0]['budget_logical_id']==2
    assert l.rows[0][2] is None and l.rows[1][2]==21 and not l.halts


def test_repeated_unsupported_output_stops_with_both_raw_failures(tmp_path):
    c,l,calls,events,_=run(tmp_path,'answer',['error','wrong-schema'])
    with pytest.raises(BudgetStop):c.get_completion('unchanged',load_author_contracts()['answer'])
    assert len(calls)==2 and [e['kind'] for e in l.failures]==['provider_error','invalid_output']
    assert len(events)==1 and len(events[0]['attempts'])==2 and l.halts
    assert len(list((tmp_path/'raw').glob('*-failure.json')))==2


def test_financial_rejection_never_sends_second_post(tmp_path):
    c,l,calls,events,_=run(tmp_path,'metadata',['timeout']);l.allow_retry=False
    with pytest.raises(BudgetStop):c.get_completion('unchanged',load_author_contracts()['metadata'])
    assert len(l.rows)==len(calls)==len(events[0]['attempts'])==1 and l.halts
    assert events[0]['physical_generations'][0]['response'] is None


def test_one_accepted_response_is_not_retried_or_changed(tmp_path):
    c,l,calls,events,_=run(tmp_path,'answer',['valid'])
    assert c.get_completion('unchanged',load_author_contracts()['answer'])==json.dumps(VALUES['answer'])
    assert len(calls)==1 and not l.failures and not l.halts and 'physical_generations' not in events[0]


def test_observation_preserves_both_physical_outputs_and_charges(tmp_path):
    c,l,calls,events,obs=run(tmp_path,'answer',['error','valid'],cloud=True)
    expected=c.get_completion('unchanged',load_author_contracts()['answer'])
    capture=obs.finish();gens=[r for r in capture['observations'] if r['type']=='generation']
    assert len(gens)==1 and not capture['errors']
    g=gens[0];physical=g['metadata']['physical_generations']
    assert [a['response']['choices'][0]['message']['content'] for a in physical]==['{"x":',expected]
    assert [a['error_type'] for a in physical]==['BudgetStop',None]
    assert all(a['duration_seconds']>=0 and a['wire_request_sha256']==fingerprint(calls[0]) for a in physical)
    assert g['output']['accepted'] and g['usage_details']=={'input':200,'output':20,'total':220}
    assert g['cost_details']['total']==.000042


@pytest.mark.parametrize('mode',['expensive-502','unidentified-502','bad-usage-200'])
def test_retains_known_or_ambiguous_liability_above_reserve_without_another_post(tmp_path, mode):
    c,l,calls,events,_=run(tmp_path,'answer',[mode])
    with pytest.raises(BudgetStop):c.get_completion('unchanged',load_author_contracts()['answer'])
    assert len(calls)==1 and not l.failures and l.halts and events[0]['error_type']
    if mode=='expensive-502':
        assert l.rows[0][2]==1_000_000 and not l.retained
    else:
        assert l.retained==[(1,Decimal(1))]
    assert (tmp_path/'raw/000001-response.bin').is_file() and (tmp_path/'raw/000001-failure.json').is_file()


def test_identified_billed_gateway_failure_is_settled_before_repeat(tmp_path):
    c,l,calls,events,_=run(tmp_path,'answer',['billed-502','valid'])
    assert c.get_completion('unchanged',load_author_contracts()['answer'])==json.dumps(VALUES['answer'])
    assert l.rows[0][2]==21 and l.rows[1][2]==21 and len(calls)==2 and not l.halts
    assert l.failures[0]['kind']=='transient_http'
    assert events[0]['conservative_cost_usd']==.000042


def test_actual_author_guard_observes_one_decision_after_retry(tmp_path, monkeypatch):
    from amem_repro import gpt4omini_campaign
    from amem_repro.openrouter import CampaignLedger, cell_store
    from gpt4omini_executor_fixture import run_actual_phase
    from gpt4omini_fixture import ROOT
    monkeypatch.setattr(gpt4omini_campaign, 'OpenRouterController', FinalController)
    # Here finance uses synthetic, all-settled responses. The separate ledger tests exercise its admission.
    monkeypatch.setattr(CampaignLedger, 'reserve_retry',
                        lambda self,phase,stage,body,failed:self.reserve(phase,stage,body), raising=False)
    monkeypatch.setattr(CampaignLedger, 'record_failure', lambda *a:None, raising=False)
    post=httpx.Client.post
    decisions=[]
    def native_mock(self,url,**kwargs):
        response=post(self,url,**kwargs)
        if 'should_evolve' not in kwargs['json']['response_format']['json_schema']['schema']['properties']:
            return response
        decisions.append(None)
        if len(decisions) not in (1,3):
            return response
        data=response.json()
        data['choices'][0].update(finish_reason='error',message={'content':'{"should_evolve":'})
        return httpx.Response(200,json=data,request=response.request)
    monkeypatch.setattr(httpx.Client,'post',native_mock)
    r=run_actual_phase(tmp_path,root=ROOT,conversation='conv-44',condition='linking_only',
                       fail_decisions={4:'malformed',5:'length',6:'length'})
    d=cell_store(tmp_path,'linking_only-conv-44')/'runs/p0'
    events=[json.loads(l) for l in (d/'events.jsonl').open()]
    gen=[e for e in events if e['type']=='generation']
    dd=[e for e in gen if e['stage']=='shared_decision']
    assert len(r['requests'])==9 and len(gen)==6 and len(dd)==3
    assert [len(e['attempts']) for e in dd]==[2,2,2]
    assert [e['error_type'] for e in dd]==[None,'AdapterError','AdapterError']
    assert [e['budget_logical_id'] for e in dd]==[3,6,9]
    assert r['receipt']['evolution_counter']==1 and r['receipt']['notes']==3
    fallback=[e for e in events if e.get('kind')=='original_evolution_fallback']
    assert [e['provider_deviation'] for e in fallback]==['malformed','length']
    assert all(e['original_fallback_verified'] for e in fallback)
