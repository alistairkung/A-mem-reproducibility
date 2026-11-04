"""New-campaign native contracts and financial failure boundaries, no network."""
import copy
import json
import sqlite3
from pathlib import Path

import httpx
import pytest

from amem_repro.adapter import AdapterError
from amem_repro.budget import BudgetStop
from amem_repro.config import OPENROUTER_CONFIG, validate_config, stage_output_limits
from amem_repro.contracts import load_author_contracts
from amem_repro.openrouter import (
    CAMPAIGN, MODEL, SCIENTIFIC_BINDING, CampaignLedger, OpenRouterController, fingerprint, usage_charge,
)

VALUES = {
    'metadata':{'keywords':['cat'],'context':'A cat.','tags':['cat']},
    'shared_decision':{'should_evolve':False,'actions':[],'suggested_connections':[],
                       'new_context_neighborhood':[],'tags_to_update':[],'new_tags_neighborhood':[]},
    'query_keywords':{'keywords':'cat'},'answer':{'answer':'cat'},
}


def setup(tmp_path, *, stage='metadata', change=None, handler=None, observer=None):
    binding={**SCIENTIFIC_BINDING,'source_sha256':'a'*64}
    ledger=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=binding)
    approval={'approved':True,'binding':binding,'kind':'compatibility','phase':'smoke',
              'condition':'full','conversation':'conv-44'}
    phase=ledger.claim(approval)
    requests=[]
    def respond(request):
        requests.append(json.loads(request.content))
        if handler:return handler(request)
        response={'id':'gen-'+str(len(requests)),'model':MODEL,'provider':'OpenAI',
                  'choices':[{'finish_reason':'stop','message':{'content':json.dumps(VALUES[stage])}}],
                  'usage':{'prompt_tokens':100,'completion_tokens':100,'cost':.000075}}
        if change:change(response)
        return httpx.Response(200,json=response)
    client=httpx.Client(transport=httpx.MockTransport(respond),follow_redirects=False)
    events=[]
    controller=OpenRouterController(client,ledger=ledger,phase=phase,journal=tmp_path/'raw',
                                    observer=observer or events.append)
    return controller,ledger,requests,events,approval


@pytest.mark.parametrize('stage',VALUES)
def test_native_original_contracts_and_exact_bytes(tmp_path,stage):
    c,l,requests,events,_=setup(tmp_path,stage=stage)
    contract=load_author_contracts()[stage]
    result=c.get_completion('Unchanged original prompt',contract)
    assert result==json.dumps(VALUES[stage])
    assert len(requests)==1
    body=requests[0]
    assert body['response_format']==contract
    assert body['messages']==[{'role':'system','content':'You must respond with a JSON object.'},
                              {'role':'user','content':'Unchanged original prompt'}]
    assert body['provider']=={'order':['openai'],'only':['openai'],
                             'allow_fallbacks':False,'require_parameters':True}
    assert not {'thinking','tools','tool_choice','models','plugins','transforms'} & body.keys()
    assert body['model']==MODEL and body['max_tokens']==stage_output_limits(OPENROUTER_CONFIG)[stage]
    assert l.totals()=={'attempts':1,'conservative_microusd':75,'unknown_attempts':0,
                        'reported_cost_usd':'0.000075'}
    assert events[0]['raw_schema_valid'] and events[0]['conservative_cost_usd']==.000075
    assert (tmp_path/'raw/000001-request.json').exists()
    assert (tmp_path/'raw/000001-response.bin').exists()


def test_new_config_does_not_mutate_deepseek_profiles():
    from amem_repro.config import DEFAULT_CONFIG,RUN2_CONFIG
    validate_config(OPENROUTER_CONFIG)
    assert DEFAULT_CONFIG['model']['id']==RUN2_CONFIG['model']['id']=='deepseek-flash'
    assert stage_output_limits()['shared_decision']==4000
    assert stage_output_limits(RUN2_CONFIG)['shared_decision']==8192
    assert stage_output_limits(OPENROUTER_CONFIG)['shared_decision']==4096
    changed=copy.deepcopy(OPENROUTER_CONFIG);changed['model']['provider']['allow_fallbacks']=True
    with pytest.raises(ValueError):validate_config(changed)


@pytest.mark.parametrize('change',[
    lambda r:r.update(model='openai/gpt-4o-mini'),lambda r:r.update(provider='Azure'),
    lambda r:r['choices'][0].update(finish_reason='tool_calls'),
    lambda r:r['choices'][0]['message'].update(refusal='refused'),
    lambda r:r['choices'][0]['message'].update(content='{"keywords":[],"context":0,"tags":[]}'),
])
def test_unsupported_outputs_are_terminal_and_not_retried(tmp_path,change):
    c,l,requests,events,_=setup(tmp_path,change=change)
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert len(requests)==1 and events[0]['error_type']
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    reopened=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=l.binding)
    with pytest.raises(BudgetStop):reopened.reserve('smoke','metadata',requests[0])
    assert len(requests)==1


@pytest.mark.parametrize('change',[
    lambda r:r.pop('usage'),lambda r:r['usage'].pop('cost'),
    lambda r:r['usage'].update(completion_tokens=True),
    lambda r:r['usage'].update(cost=-1),lambda r:r['usage'].update(cost='NaN'),
])
def test_unknown_usage_retains_full_reservation_and_blocks_admission(tmp_path,change):
    c,l,requests,events,_=setup(tmp_path,change=change)
    for _ in range(2):
        with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert len(requests)==1 and l.totals()['unknown_attempts']==1
    assert l.totals()['conservative_microusd']==19650


@pytest.mark.parametrize('status',[429,500,503])
def test_http_errors_do_not_trigger_transport_or_gateway_retries(tmp_path,status):
    c,l,requests,events,_=setup(tmp_path,handler=lambda _:httpx.Response(status,json={'error':{'message':'test'}}))
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert len(requests)==1 and l.totals()['unknown_attempts']==1


def test_transport_failure_does_not_retry_or_release_unknown(tmp_path):
    def fail(request):raise httpx.ReadError('original body read failure',request=request)
    c,l,requests,events,_=setup(tmp_path,handler=fail)
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert len(requests)==1 and l.totals()['unknown_attempts']==1
    assert events[0]['error_message']=='original body read failure'
    assert len(events[0]['attempts'])==1
    assert events[0]['attempts'][0]['error_type']=='ReadError'
    assert events[0]['attempts'][0]['usage'] is None


def test_malformed_evolution_rejected_and_pending_until_state_verified(tmp_path):
    bad='{"should_evolve":true,"actions"["strengthen"]}'
    c,l,requests,events,_=setup(tmp_path,stage='shared_decision',
        change=lambda r:r['choices'][0]['message'].update(content=bad))
    with pytest.raises(AdapterError):c.get_completion('original',load_author_contracts()['shared_decision'])
    assert events[0]['output']==bad and c.pending['kind']=='malformed'
    assert l.totals()['unknown_attempts']==0
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['shared_decision'])
    assert len(requests)==1


def test_length_evolution_is_settled_once_and_pending_exact_fallback(tmp_path):
    def change(r):
        r['choices'][0].update(finish_reason='length')
        r['choices'][0]['message']['content']='{"should_evolve":'
        r['usage']['completion_tokens']=4096;r['usage']['cost']=.0024726
    c,l,requests,events,_=setup(tmp_path,stage='shared_decision',change=change)
    with pytest.raises(AdapterError):c.get_completion('original',load_author_contracts()['shared_decision'])
    assert c.pending['kind']=='length' and l.totals()['unknown_attempts']==0
    assert len(requests)==1


def test_single_use_approval_cannot_restart_even_after_completion(tmp_path):
    c,l,requests,events,approval=setup(tmp_path)
    l.finish('smoke',{'status':'complete'},'complete')
    with pytest.raises(BudgetStop):l.claim(approval)


@pytest.mark.parametrize('kind',['symlink','hardlink','root-symlink'])
def test_ledger_alias_rejected_before_older_file_is_opened(tmp_path,kind):
    old=tmp_path/'old.sqlite';old.write_bytes(b'immutable old ledger')
    campaign=tmp_path/'new';campaign.mkdir()
    if kind=='root-symlink':
        campaign.rmdir();campaign.symlink_to(tmp_path,target_is_directory=True)
    elif kind=='symlink':(campaign/'budget.sqlite').symlink_to(old)
    else:
        import os
        os.link(old,campaign/'budget.sqlite')
    with pytest.raises(BudgetStop):CampaignLedger(campaign/'budget.sqlite',campaign_root=campaign,binding={})
    assert old.read_bytes()==b'immutable old ledger'


@pytest.mark.parametrize('alias',['direct','ancestor'])
def test_foreign_sqlite_is_unchanged_even_when_target_is_regular(tmp_path,alias):
    older=tmp_path/'older';older.mkdir()
    path=older/'budget.sqlite'
    with sqlite3.connect(path) as db:db.execute('CREATE TABLE historical_evidence (value TEXT)')
    before=path.read_bytes()
    root=older
    if alias=='ancestor':
        link=tmp_path/'alias';link.symlink_to(tmp_path,target_is_directory=True)
        root=link/'older'
    with pytest.raises(BudgetStop):
        CampaignLedger(root/'budget.sqlite',campaign_root=root,binding=SCIENTIFIC_BINDING)
    assert path.read_bytes()==before


def test_failed_settlement_is_outside_retry_and_preserves_raw_response(tmp_path,monkeypatch):
    c,l,requests,events,_=setup(tmp_path)
    from contextlib import contextmanager
    original=l.transaction
    count=0
    @contextmanager
    def broken():
        nonlocal count
        count+=1
        if count==2:raise sqlite3.OperationalError('offline settlement fault')
        with original() as db:yield db
    monkeypatch.setattr(l,'transaction',broken)
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert len(requests)==1 and (tmp_path/'raw/000001-response.bin').exists()
    assert l.totals()['unknown_attempts']==1


def test_smoke_and_cell_spending_cannot_be_reset_by_child_phase(tmp_path):
    c,l,requests,events,approval=setup(tmp_path)
    with l.transaction() as db:
        db.execute("INSERT INTO attempts (phase,stage,request_hash,reservation,charge,state) VALUES ('smoke','metadata','old',240000,240000,'settled')")
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert requests==[]


def test_known_charge_anomaly_retains_full_reported_liability(tmp_path):
    c,l,requests,events,_=setup(tmp_path,change=lambda r:r['usage'].update(cost=.03))
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    assert l.totals()['conservative_microusd']==30000
    assert l.totals()['reported_cost_usd']=='0.03'
    assert len(requests)==1
    assert events[0]['conservative_cost_usd']==.03


def test_fresh_ledger_cannot_attach_to_another_process_claim(tmp_path):
    c,l,requests,events,approval=setup(tmp_path)
    another=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=l.binding)
    with pytest.raises(BudgetStop):another.reserve('smoke','metadata',{'max_tokens':1000})
    assert requests==[]


def test_both_original_c5_temperatures_are_preserved(tmp_path):
    c,l,requests,events,_=setup(tmp_path,stage='answer')
    c.get_completion('original',load_author_contracts()['answer'],temperature=.5)
    assert requests[0]['temperature']==.5


def access_retest_approval(ledger, original, request):
    ledger.finish(original['phase'],{'status':'incomplete'},'terminal')
    with ledger.transaction() as db:snapshot=ledger.access_snapshot(db)
    return {**original,'phase':'access-retest','parent':original['phase'],
            'parent_seal':snapshot['phases'][0][4],'limits':{'max_physical_calls':1},
            'access_retest':{'policy':'updated-key-one-probe-20261104-v1',
                             'request_sha256':fingerprint(request),'retained_snapshot':snapshot}}


def test_explicit_updated_key_probe_retains_denied_history_and_cannot_release_baseline(tmp_path):
    c,l,requests,events,original=setup(tmp_path,handler=lambda _:httpx.Response(403,json={'error':{'code':403}}))
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    approval=access_retest_approval(l,original,requests[0])
    reopened=CampaignLedger(l.path,campaign_root=tmp_path,binding=l.binding)
    phase=reopened.claim(approval)
    before=approval['access_retest']['retained_snapshot']
    attempt,_=reopened.reserve(phase,'metadata',requests[0]);assert attempt==2
    with reopened.transaction() as db:assert reopened.access_snapshot(db,phase)==before
    assert reopened.totals()['conservative_microusd']==39300
    with pytest.raises(BudgetStop):reopened.reserve(phase,'metadata',requests[0])
    reopened.finish(phase,{'status':'incomplete'},'terminal')
    other=CampaignLedger(l.path,campaign_root=tmp_path,binding=l.binding)
    with pytest.raises(BudgetStop):other.claim({**original,'kind':'baseline','phase':'baseline'})
    with pytest.raises(BudgetStop):other.claim(approval)
    with other.transaction() as db:assert other.access_snapshot(db,phase)==before


@pytest.mark.parametrize('change',['snapshot','seal','kind','calls','grant-and-request','request','new-halt'])
def test_access_retest_rejects_changed_scope_or_history_before_second_post(tmp_path,change):
    c,l,requests,events,original=setup(tmp_path,handler=lambda _:httpx.Response(403,json={'error':{'code':403}}))
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    approval=access_retest_approval(l,original,requests[0])
    if change=='snapshot':approval['access_retest']['retained_snapshot']['attempts'][0][5]=0
    if change=='seal':approval['parent_seal']='changed'
    if change=='kind':approval['kind']='baseline'
    if change=='calls':approval['limits']['max_physical_calls']=2
    if change=='grant-and-request':approval['access_retest']['request_sha256']='b'*64
    reopened=CampaignLedger(l.path,campaign_root=tmp_path,binding=l.binding)
    if change not in ('request','new-halt'):
        with pytest.raises(BudgetStop):reopened.claim(approval)
    else:
        phase=reopened.claim(approval)
        if change=='new-halt':
            with reopened.transaction() as db:db.execute('INSERT INTO halts VALUES (?,?)',(phase,'new control failure'))
        request=copy.deepcopy(requests[0])
        if change=='request':request['messages'][1]['content']='different'
        with pytest.raises(BudgetStop):reopened.reserve(phase,'metadata',request)
    assert reopened.totals()['attempts']==1 and len(requests)==1


def third_access_approval(tmp_path):
    c,l,requests,events,original=setup(tmp_path,handler=lambda _:httpx.Response(403,json={'error':{'code':403}}))
    with pytest.raises(BudgetStop):c.get_completion('original',load_author_contracts()['metadata'])
    second=access_retest_approval(l,original,requests[0])
    ledger=CampaignLedger(l.path,campaign_root=tmp_path,binding=l.binding)
    phase=ledger.claim(second);ledger.reserve(phase,'metadata',requests[0])
    ledger.stop(phase,'HTTPStatusError');ledger.finish(phase,{'status':'incomplete'},'terminal')
    with ledger.transaction() as db:snapshot=ledger.access_snapshot(db)
    third={**second,'phase':'explicit-third-access','parent':phase,'parent_seal':snapshot['phases'][-1][4],
           'access_retest':{'policy':'third-access-one-probe-20261104-v1',
                           'request_sha256':fingerprint(requests[0]),'retained_snapshot':snapshot}}
    return ledger,third,requests[0],snapshot


def test_separate_third_access_grant_retains_both_unknowns_and_is_single_use(tmp_path):
    old,approval,request,before=third_access_approval(tmp_path)
    ledger=CampaignLedger(old.path,campaign_root=tmp_path,binding=old.binding)
    phase=ledger.claim(approval);attempt,_=ledger.reserve(phase,'metadata',request)
    assert attempt==3 and ledger.totals()['conservative_microusd']==58950
    with ledger.transaction() as db:assert ledger.access_snapshot(db,phase)==before
    with pytest.raises(BudgetStop):ledger.reserve(phase,'metadata',request)
    ledger.stop(phase,'HTTPStatusError');ledger.finish(phase,{'status':'incomplete'},'terminal')
    reopened=CampaignLedger(old.path,campaign_root=tmp_path,binding=old.binding)
    with pytest.raises(BudgetStop):reopened.claim({**approval,'phase':'fourth'})
    with pytest.raises(BudgetStop):reopened.claim({**approval,'kind':'baseline','phase':'baseline'})


@pytest.mark.parametrize('change',['old-policy','first-request','parent-seal','prior-charge','prior-parent','prior-seal'])
def test_third_access_rejects_wrong_grant_or_changed_ancestry(tmp_path,change):
    old,approval,request,before=third_access_approval(tmp_path)
    if change=='old-policy':approval['access_retest']['policy']='updated-key-one-probe-20261104-v1'
    if change=='first-request':
        with old.transaction() as db:db.execute("UPDATE attempts SET request_hash='different' WHERE id=1")
    if change=='parent-seal':approval['parent_seal']='different'
    if change=='prior-charge':
        with old.transaction() as db:db.execute('UPDATE attempts SET charge=0 WHERE id=1')
    if change=='prior-parent':
        with old.transaction() as db:db.execute("UPDATE phases SET parent='different' WHERE id='access-retest'")
    if change=='prior-seal':
        with old.transaction() as db:db.execute("UPDATE phases SET seal='different' WHERE id='smoke'")
    if change not in ('old-policy','parent-seal'):
        with old.transaction() as db:approval['access_retest']['retained_snapshot']=old.access_snapshot(db)
    ledger=CampaignLedger(old.path,campaign_root=tmp_path,binding=old.binding)
    with pytest.raises(BudgetStop):ledger.claim(approval)
    assert ledger.totals()['attempts']==2
