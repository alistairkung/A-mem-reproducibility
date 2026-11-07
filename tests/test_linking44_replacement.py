"""Bounded fresh replacement claims, native admissions and transient restart evidence."""
import base64
import copy
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from amem_repro import linking44_replacement as group
from amem_repro.budget import BudgetStop
from amem_repro.config import OPENROUTER_CONFIG, fingerprint
from amem_repro.openrouter import MODEL, SCIENTIFIC_BINDING, CampaignLedger, save_new


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True))


@pytest.fixture
def setup(tmp_path,monkeypatch):
    root=tmp_path/'source'
    c=root/'artifacts/gpt4omini'
    money=c/'budget.sqlite'
    source='scripts/gpt4omini_replacement.py'
    write(root/source,{'offline':True})
    sources={'files':{source:sha(root/source)}}
    monkeypatch.setattr(group,'ROOT',root)
    from scripts import gpt4omini_replacement as driver
    monkeypatch.setattr(driver,'reviewed_files',lambda commit:(sources,sources['files'],None))
    monkeypatch.setattr(driver,'verify_capacity',lambda cap,source,commit,as_of,campaign:None)
    original={**SCIENTIFIC_BINDING,'condition':'linking_only','conversation_id':'conv-44','source_sha256':'old','repetition':0}
    binding={**original,'source_sha256':fingerprint(sources)}
    parent=CampaignLedger(money,campaign_root=c,binding=original)
    with parent.transaction() as db:
        db.execute("INSERT INTO phases VALUES ('original','{}',NULL,'terminal','frozen')")
        for i,charge in [(1,19650),(2,19650),(3,19650),(17286,21044),(18348,19650)]:
            db.execute("INSERT INTO attempts (id,phase,stage,request_hash,reservation,charge,state) VALUES (?,'original','answer','hash',?,?,'reserved')",(i,charge,charge))
        monkeypatch.setattr(group,'PR50_SQL',fingerprint(parent.access_snapshot(db)))
    monkeypatch.setattr(group,'PR50_LEDGER',sha(money))
    d=c/group.GROUP_ROOT
    save_new(c/group.PR49_RELEASE,{'binding':original})
    monkeypatch.setattr(group,'PR49_SHA',sha(c/group.PR49_RELEASE))
    save_new(d/'preflight.json',{'verified':True})
    save_new(d/'capacity.json',{'verified':True})
    reviews={}
    for axis in ('spec','standards'):
        f=d/f'{axis}-review.json'
        save_new(f,{'verdict':'pass','reviewed_commit':'a'*40,'source_sha256':binding['source_sha256']})
        reviews[axis]=sha(f)
    save_new(d/'release.json',{'approved':True,'approved_by':'user','approved_at':datetime.now(timezone.utc).isoformat(),'group':group.GROUP,'binding':binding,'capacity_sha256':sha(d/'capacity.json'),
             'limits':group.GROUP_LIMITS,'reviewed_commit':'a'*40,'implementation_files':sources['files'],
             'reviews':reviews,'historical_release_sha256':group.PR49_SHA,'opened_from_ledger_sha256':group.PR50_LEDGER,
             'preflight_sha256':sha(d/'preflight.json')})
    def prepare(n):
        ledger=group.ReplacementLedger(money,campaign_root=c,binding=binding)
        phase=group.phase_id(n)
        a={'approved':True,'kind':'replacement','ordinal':n,'group':group.GROUP,'phase':phase,'binding':binding,
           'approved_at':datetime.now(timezone.utc).isoformat(),'condition':'linking_only','conversation':'conv-44',
           'release_sha256':sha(d/'release.json'),'service_reserve_microusd':1080000}
        if n>1:
            prev=group.attempt_store(c,n-1)/'reconciliation.json'
            a['previous_reconciliation_sha256']=sha(prev) if prev.is_file() else 'unavailable'
        write(group.attempt_store(c,n)/'frozen/approval.json',a)
        return ledger,a
    return c,prepare


def start(setup,n=1):
    _,prepare=setup
    l,a=prepare(n)
    p=l.claim(a)
    l.set_guard(p,lambda db:None)
    l.observe_phase(p,lambda:None)
    return l,p


def request(l,stage):
    return {'max_tokens':4096 if stage=='shared_decision' else 1000,'model':MODEL,
            'provider':copy.deepcopy(OPENROUTER_CONFIG['model']['provider']),
            'response_format':l.contracts[stage],'temperature':.7}


def response(identifier):
    return {'provider':'OpenAI','model':MODEL,'id':identifier,
            'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':.000021}}


def test_one_contiguous_stage_sequence_and_five_old_reserves(setup):
    l,p=start(setup);a=l.claimed[p]
    assert l.unaccepted_unknowns(a)==0
    i,reserve=l.reserve(p,'metadata',request(l,'metadata'))
    assert (i,reserve)==(18349,19650) and l.unaccepted_unknowns(a)==1
    assert l.settle(i,response('gen-1'),1000)==21 and l.unaccepted_unknowns(a)==0
    j,reserve=l.reserve(p,'shared_decision',request(l,'shared_decision'))
    assert j==18350 and reserve==21044
    with pytest.raises(BudgetStop):
        l.reserve(p,'metadata',request(l,'metadata'))
    with pytest.raises(BudgetStop):
        l.settle(j,response('gen-late'),4096)
    assert l.totals()['unknown_attempts']==6
    with l.transaction() as db:
        assert db.execute('SELECT sum(charge) FROM attempts WHERE phase="original"').fetchone()==(99644,)


@pytest.mark.parametrize('key,value',[('ordinal',False),('phase','gpt4omini-linking_only-conv44-r0-p1'),
    ('kind','baseline'),('group','other'),('binding',{}),('parent','other'),('release_sha256','f'*64),
    ('service_reserve_microusd',0),('condition','neither'),('conversation','conv-50')])
def test_rejects_wrong_or_unfunded_claim(setup,key,value):
    _,prepare=setup;l,a=prepare(1);a[key]=value
    with pytest.raises(BudgetStop):l.claim(a)


@pytest.mark.parametrize('case',['cache','foreign extension','old reserved charge','missing earlier attempt','double claim',
                                'tampered file','service cap','group budget','wrong stage','wrong provider','wrong model','wrong limit'])
def test_claim_and_admission_fail_closed(setup,case,monkeypatch):
    c,prepare=setup
    if case=='missing earlier attempt':
        l,a=prepare(2)
        with pytest.raises(BudgetStop): l.claim(a)
        return
    l,a=prepare(1);p=a['phase']
    if case=='cache':
        (group.attempt_store(c,1)/'cache').mkdir()
        with pytest.raises(BudgetStop): l.claim(a)
        return
    l.claim(a);l.set_guard(p,lambda db:None);l.observe_phase(p,lambda:None)
    if case=='double claim':
        second,_=prepare(1)
        with pytest.raises(BudgetStop): second.claim(a)
        return
    req=request(l,'metadata');stage='metadata'
    if case=='foreign extension':
        with l.transaction() as db: db.execute("INSERT INTO halts VALUES ('unapproved','failure')")
    elif case=='old reserved charge':
        with l.transaction() as db: db.execute("UPDATE attempts SET charge=100 WHERE id=18348")
    elif case=='tampered file':
        write(c/group.GROUP_ROOT/'spec-review.json',{'verdict':'pass'})
    elif case=='service cap':
        monkeypatch.setitem(group.GROUP_LIMITS,'group_microusd',1080000)
    elif case=='group budget':
        monkeypatch.setitem(group.GROUP_LIMITS,'planned_campaign_microusd',group.PR50_EXPOSURE+1080000)
    elif case=='wrong stage':stage='answer'
    elif case=='wrong provider':req['provider']['allow_fallbacks']=True
    elif case=='wrong model':req['model']='dynamic'
    elif case=='wrong limit':req['max_tokens']=2000
    with pytest.raises(BudgetStop):l.reserve(p,stage,req)


@pytest.mark.parametrize('id_',[1,2,3,17286,18348,18349])
def test_never_settles_inherited_or_unowned_unknown(setup,id_):
    l,_=start(setup)
    with pytest.raises(BudgetStop): l.settle(id_,response('gen-foreign'),1000)
    assert l.totals()['unknown_attempts']==5


def raw_get(path, endpoint, params, data):
    write(path,{'endpoint':endpoint,'params':params,'status':200,
               'response_base64':base64.b64encode(json.dumps({'data':data}).encode()).decode()})


def transient(setup,n):
    c,_=setup;l,p=start(setup,n);store=group.attempt_store(c,n);out=store/'runs'/p
    req=request(l,'metadata');i,_=l.reserve(p,'metadata',req)
    raw=response(f'gen-{n}');l.settle(i,raw,1000)
    l.stop(p,'ConnectionResetError')
    write(out/'raw'/f'{i:06d}-response.bin',raw)
    write(out/'raw'/f'{i:06d}-request.json',req)
    write(out/'events.jsonl',{'type':'generation','error_type':'ConnectionResetError','error_message':'connection reset by peer',
            'budget_logical_id':i,'stage':'metadata','provider_response':raw,
            'attempts':[{'budget_attempt_id':i,'status_code':200,'response_body':raw}]})
    # Model a financially known transient: these synthetic verified artifacts
    # exercise the policy boundary. A response-less OpenRouter request cannot pass.
    proof=out/'remote-proof.json';write(out/'observed-page.json',{'raw_remote':True})
    write(out/'trace-capture.json',{'observations':[{'id':'i','trace_id':'t'}],'scores':[],'trace_ids':['t'],'errors':[]})
    write(proof,{'verified':True,'kind':'observations','identity':{'run_id':p,'repetition':n,'condition':'linking_only','conversation_id':'conv-44'},
                 'observation_count':1,'trace_ids':['t'],'score_count':0,'readback_files':{'observed-page.json':sha(out/'observed-page.json')}})
    phase={'phase':p,'status':'incomplete','error_type':'BudgetStop','observations':{'verified':True,'observation_count':1,'score_count':0,'trace_ids':['t'],'evidence_path':str(proof),'evidence_sha256':sha(proof)},
           'files':{str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file()}}
    write(out/'phase.json',phase);seal=l.finish(p,phase,'terminal')
    write(store/'service'/f'{p}.json',{'runtime_units_admitted':2,'admitted_units':2,'maximum_units':13500,'stopped':False})
    g={'id':raw['id'],'provider_name':'OpenAI','model':MODEL,'native_tokens_prompt':100,'native_tokens_completion':10,
       'total_cost':.000021,'provider_responses':[{'provider_name':'OpenAI','model_permaslug':MODEL,'status':200}]}
    j=store/'financial-readbacks';raw_get(j/'0-0.json','generation',{'id':raw['id']},g)
    old=Decimal('.000021')*(n-1);new=old+Decimal('.000021')
    def account(usage):return {'credits':{'total_credits':'50','total_usage':str(usage)},
                               'key':{'usage':str(usage),'limit_remaining':str(Decimal(50)-usage)}}
    for folder,values in [(store/'opening-reads',account(old)),(j/'account',account(new))]:
        for endpoint,data in values.items():raw_get(folder/f'{endpoint}.json',endpoint,{},data)
    with l.transaction() as db:
        rows=db.execute('SELECT * FROM attempts WHERE phase=? ORDER BY id',(p,)).fetchall()
    write(store/'reconciliation.json',{'verified':True,'phase':p,'phase_seal':seal,'settled_attempts_sha256':fingerprint(rows),
          'unknown_attempt_ids':[],'service_units':2,'movement':{'verified':True},'generation_journal':str(j),'generations':[g],
          'opening':{'account':account(old)},'closing':account(new)})
    return l,p,store


def test_three_fresh_ordinals_share_all_earmarks_and_stop(setup):
    c,_=setup
    for n in (1,2,3):
        l,p,_=transient(setup,n)
        assert group.classify_restart(c,p) is (n<3)
        with l.transaction() as db:
            phases,rows=group.history(db)
            assert sum(json.loads(r[1])['service_reserve_microusd'] for r in phases)==1080000*n
            assert sum(r[5] for r in rows)==21*n
            group.validate_bounds(phases,rows,extra_model=10000000-1080000*n-21*n)
            with pytest.raises(BudgetStop):group.validate_bounds(phases,rows,extra_model=10000001-1080000*n-21*n)
    with pytest.raises(BudgetStop):group.phase_id(4)


@pytest.mark.parametrize('tamper',['response-less','source evidence','route','native usage','price','movement','raw GET','service','terminal seal','observation proof','coordinated meter corruption'])
def test_restart_requires_actual_preserved_financial_and_science_evidence(setup,tamper):
    c,prepare=setup;l,p,store=transient(setup,1)
    assert group.classify_restart(c,p)
    rec=store/'reconciliation.json';d=json.loads(rec.read_bytes())
    if tamper=='response-less':
        with l.transaction() as db:db.execute("UPDATE attempts SET state='reserved',charge=reservation,provider_id=NULL,reported_cost=NULL WHERE phase=?",(p,))
    elif tamper=='source evidence':write(store/'runs'/p/'events.jsonl',{})
    elif tamper=='observation proof':write(store/'runs'/p/'remote-proof.json',{})
    elif tamper=='native usage':d['generations'][0]['native_tokens_prompt']=1
    elif tamper=='route':d['generations'][0]['provider_name']='other'
    elif tamper=='price':d['generations'][0]['total_cost']=0
    elif tamper=='movement':d['closing']['key']['usage']='1'
    elif tamper=='raw GET':write(store/'financial-readbacks/0-0.json',{})
    elif tamper=='coordinated meter corruption':
        d['service_units']=0
        write(store/'service'/f'{p}.json',{'runtime_units_admitted':0,'admitted_units':0,'maximum_units':13500,'stopped':False})
    elif tamper=='service':write(store/'service'/f'{p}.json',{'stopped':True})
    elif tamper=='terminal seal':
        with l.transaction() as db:db.execute("UPDATE phases SET seal='bad' WHERE id=?",(p,))
    write(rec,d)
    assert not group.classify_restart(c,p)
    second,a=prepare(2)
    with pytest.raises((BudgetStop,KeyError)):second.claim(a)


def test_prior_group_ledger_cannot_be_repriced_after_next_claim(setup):
    _,p,_=transient(setup,1)
    second,next_phase=start(setup,2)
    with second.transaction() as db:
        db.execute('UPDATE attempts SET charge=0 WHERE phase=?',(p,))
    with pytest.raises(BudgetStop):second.reserve(next_phase,'metadata',request(second,'metadata'))

def test_forbids_foreign_halt_and_premature_completion(setup):
    l,p=start(setup)
    with pytest.raises(BudgetStop):l.stop('historic-other','fake')
    with pytest.raises(BudgetStop):l.finish(p,{'phase':p,'status':'complete','notes':675,'questions':158},'complete')
    with l.transaction() as db:
        assert not db.execute('select 1 from halts').fetchall()
        assert db.execute('select state from phases where id=?',(p,)).fetchone()==('running',)


def test_release_validation_discovers_real_git_head_and_tampered_bytes(tmp_path,monkeypatch):
    import subprocess
    from scripts import gpt4omini_replacement as driver
    root=tmp_path/'actual-git';root.mkdir()
    def git(*args):
        return subprocess.check_output(['git','-C',str(root),'-c','user.name=Offline Test',
            '-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q')
    for f in driver.DRIVER_FILES:write(root/f,{'fixture':f})
    src=root/'amem_repro/scientific.py';write(src,{'fixture':'source'})
    git('add','.');git('commit','-qm','fixed offline source');head=git('rev-parse','HEAD')
    monkeypatch.setattr(driver,'ROOT',root)
    monkeypatch.setattr(driver,'PR50',head)
    monkeypatch.setattr(driver,'source_fingerprint',lambda path:{'files':{'amem_repro/scientific.py':sha(src)}})
    _,files,_=driver.reviewed_files(head)
    assert set(files)==set(driver.DRIVER_FILES)|{'amem_repro/scientific.py'}
    with pytest.raises(BudgetStop):driver.reviewed_files('c'*40)
    (root/'scripts/gpt4omini_finance.py').write_text('changed')
    with pytest.raises(BudgetStop):driver.reviewed_files(head)


@pytest.mark.parametrize('what',['missing driver','review finding','capacity bytes','omitted source'])
def test_untrusted_release_direct_claim_fails(setup,what):
    c,prepare=setup;l,a=prepare(1);d=c/group.GROUP_ROOT
    f=d/'release.json';r=json.loads(f.read_bytes())
    if what in ('omitted source','missing driver'):
        r['implementation_files']={} if what=='omitted source' else {'unreviewed.py':'f'*64}
    elif what=='review finding':
        review=d/'spec-review.json';v=json.loads(review.read_bytes());v['open_material_findings']=['direct claim'];write(review,v)
        r['reviews']['spec']=sha(review)
    else:write(d/'capacity.json',{'modified':True})
    write(f,r);a['release_sha256']=sha(f);write(group.attempt_store(c,1)/'frozen/approval.json',a)
    with pytest.raises(BudgetStop):l.claim(a)
