"""Eight-hour fresh conv-44 group: bounded physical retries and separate durable accounting."""
from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from .budget import BudgetStop
from .config import OPENROUTER_CONFIG, fingerprint, stage_output_limits
from .contracts import load_author_contracts
from .openrouter import (BASE_URL, CELL_SERVICE_RESERVE, CELL_SERVICE_UNITS, CONTEXT, INPUT_RATE,
                         MODEL, OUTPUT_RATE, CampaignLedger, save_new, usage_charge, micros)

GROUP = 'linking44-final-eight-hour-v1'
GROUP_ROOT = Path('cells/linking_only-conv-44/final-eight-hour')
PAID_DEADLINE = datetime(2026,11,8,8,30,tzinfo=timezone.utc)
HARD_DEADLINE = datetime(2026,11,8,9,10,tzinfo=timezone.utc)
OPENING_MODEL = 4_417_062
OPENING_COMMITTED = 10_138_902
OPENING_DB = '3d63745c4a4d257e868b7ca3bffbf50f64c12a82d936f3cbe71b159be41b811d'
OPENING_SQL = '9430f4cb85c1cbb51e52188dfffbe7a63cf56ef59111bfeeb33c7aa8f3c7ba9d'
R1_CLOSE = Path('cells/linking_only-conv-44/replacement/attempt-1/reconciliation.json')
R1_ENVELOPE = Path('verification/replacement-finance/final-group-campaign-envelope.json')
ENVELOPE_SHA = 'f7b4dc89b1003a96b1f5a4e143eec81ec3e5294879f8a58e7db023b0fbe2ab29'
LAST_ID = 19482
STAGES = ('metadata','shared_decision')*675 + ('query_keywords','answer')*158
GROUP_LIMITS = {'group_microusd':10_000_000, 'max_attempts':3, 'max_calls_per_attempt':1666,
                'max_group_retries':6, 'max_retries_per_operation':1,
                'max_langfuse_units_per_attempt':CELL_SERVICE_UNITS,
                'service_reserve_per_attempt_microusd':CELL_SERVICE_RESERVE,
                'planned_campaign_microusd':42_000_000, 'protected_microusd':8_000_000}


def require(ok, text):
    if not ok: raise BudgetStop(text)


def now():
    return datetime.now(timezone.utc)


def phase_id(ordinal):
    require(type(ordinal) is int and ordinal in (1,2,3), 'Invalid final-run ordinal')
    return f'gpt4omini-linking_only-conv44-final-r{ordinal}'


def attempt_store(campaign, ordinal):
    phase_id(ordinal)
    path=Path(campaign)/GROUP_ROOT/f'attempt-{ordinal}'
    require(path.absolute()==path.resolve(), 'Aliased final attempt store')
    return path


def raw(path):
    path=Path(path)
    require(path.resolve()==path.absolute() and path.is_file() and path.stat().st_nlink==1,
            'Missing or aliased financial evidence')
    return path.read_bytes()


def read(path):
    return json.loads(raw(path))


def sha(path):
    return hashlib.sha256(raw(path)).hexdigest()


def signature(path):
    st=path.stat()
    return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)


def opening_history(campaign):
    path=campaign/'budget.sqlite'; original_signature=signature(path)
    require(sha(path)==OPENING_DB and sha(campaign/R1_ENVELOPE)==ENVELOPE_SHA
            and sha(campaign/R1_CLOSE)=='1a2ce0e93f16210d75d3971de2f6f4150e779b66ac92cd163cab362e090196a5',
            'Original R1 ledger or financial envelope changed')
    with sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True) as db:
        require(fingerprint(CampaignLedger.access_snapshot(db))==OPENING_SQL, 'Original financial history changed')
        historical_ids=frozenset(r[0] for r in db.execute("SELECT provider_id FROM attempts WHERE state='settled'"))
    require(signature(path)==original_signature,'Opening history changed during verification')
    return path, original_signature, historical_ids


def db_file(campaign):
    return Path(campaign)/GROUP_ROOT/'finance/budget.sqlite'


def _current(db,phase):
    return db.execute('SELECT id,stage,request_hash,reservation,charge,state,response_hash,usage,provider_id,reported_cost '
                      'FROM attempts WHERE phase=? ORDER BY id',(phase,)).fetchall()


def _bounds(db,extra_model=0,extra_claims=0):
    count=db.execute('SELECT count(*) FROM phases').fetchone()[0]+extra_claims
    model=db.execute('SELECT coalesce(sum(charge),0) FROM attempts').fetchone()[0]+extra_model
    total=model+count*CELL_SERVICE_RESERVE
    require(total<=GROUP_LIMITS['group_microusd'] and OPENING_COMMITTED+total<=42_000_000,
            'Final group or planned campaign budget exhausted')
    return model,total


def _journal_digest(db):
    base=CampaignLedger.access_snapshot(db)
    base['slots']=db.execute('SELECT * FROM final_slots ORDER BY attempt').fetchall()
    base['failures']=db.execute('SELECT * FROM final_failures ORDER BY attempt').fetchall()
    return fingerprint(base)


def _all_reservations_are_explained(db):
    return not db.execute("SELECT a.id FROM attempts a LEFT JOIN final_failures f ON f.attempt=a.id "
                          "WHERE a.state!='settled' AND (f.attempt IS NULL OR a.charge!=a.reservation) LIMIT 1").fetchone()


def _failure_kind(campaign, phase, row, evidence):
    from .linking44_retry import retry_kind
    n=next((n for n in (1,2,3) if phase_id(n)==phase),None)
    expected=attempt_store(campaign,n)/'runs'/phase/'raw'/f'{row[0]:06d}-failure.json'
    require(evidence.get('attempt_id')==row[0] and evidence.get('stage')==row[1]
            and evidence.get('request_sha256')==row[2] and evidence.get('physical_evidence_file')==str(expected),
            'Failed physical request binding differs')
    data=raw(expected)
    require(hashlib.sha256(data).hexdigest()==evidence.get('physical_evidence_sha256'), 'Failed generation evidence changed')
    event=json.loads(data); kind=retry_kind(event)
    physical,=event['attempts']
    require(kind in ('transport','transient_http','provider_error','invalid_output') and evidence.get('kind')==kind
            and event.get('stage')==row[1] and event.get('budget_logical_id')==row[0]
            and physical.get('budget_attempt_id')==row[0] and fingerprint(physical['request_body'])==row[2],
            'Unsupported failure or mismatched original input')
    if row[5]=='settled':
        require(physical.get('response_body') is not None and fingerprint(physical['response_body'])==row[6]
                and physical['response_body'].get('id')==row[8], 'Failed response differs from settlement')
    else:
        response=physical.get('response_body')
        ambiguous=isinstance(response,dict) and any(response.get(k) is not None for k in ('id','usage','cost'))
        require(row[5]=='reserved' and row[3]==row[4] and row[8] is None and not ambiguous,
                'Unknown request is not fully reserved or supplied unresolved billing evidence')
    return kind


def _phase_financial_seal(db,phase):
    return fingerprint({
        'phase': db.execute('SELECT * FROM phases WHERE id=?',(phase,)).fetchall(),
        'rows': _current(db,phase),
        'slots': db.execute('SELECT * FROM final_slots WHERE phase=? ORDER BY attempt',(phase,)).fetchall(),
        'failures': db.execute('SELECT f.* FROM final_failures f JOIN final_slots s ON s.attempt=f.attempt '
                               'WHERE s.phase=? ORDER BY f.attempt',(phase,)).fetchall(),
        'halt': db.execute('SELECT * FROM halts WHERE phase=?',(phase,)).fetchall(),
    })


def _length_fallback(directory,last,event):
    events=[json.loads(line) for line in raw(directory/'events.jsonl').splitlines()]
    gens=[e for e in events if e.get('type')=='generation']
    outcomes=[e for e in events if e.get('type')=='evolution_outcome']
    failures=[e for e in events if e.get('type')=='failure']
    require(gens and outcomes and failures,'Missing terminal author transition')
    generation,outcome,proof=gens[-1],outcomes[-1],failures[-1]
    response=event['attempts'][0]['response_body']
    require(last[1]=='shared_decision' and last[5]=='settled' and generation['budget_logical_id']==last[0]
            and response['choices'][0]['finish_reason']=='length' and event.get('error_type')=='AdapterError'
            and generation.get('turn_id') and generation['turn_id']==outcome.get('turn_id')==proof.get('turn_id')
            and outcome['counter_before']==outcome['counter_after'] and not outcome['changed_existing_note_ids']
            and proof.get('kind')=='original_evolution_fallback' and proof.get('provider_deviation')=='length'
            and proof.get('original_fallback_verified') is True and proof.get('provider_output_accepted') is False
            and proof.get('raw_arguments_sha256')==hashlib.sha256(response['choices'][0]['message']['content'].encode()).hexdigest()
            and all(isinstance(proof.get(k),str) and len(proof[k])==64 for k in ('before_state_sha256','after_state_sha256'))
            and all(f.get('kind') in ('provider_completion','original_evolution_fallback','evolution_parse') for f in failures),
            'Terminal exhausted decision lacks the verified frozen author fallback')


def _restart_reason(campaign,db,ordinal,close=None):
    phase=phase_id(ordinal);store=attempt_store(campaign,ordinal)
    phase_row=db.execute('SELECT state,seal FROM phases WHERE id=?',(phase,)).fetchone()
    receipt=read(store/'runs'/phase/'phase.json'); close=read(store/'reconciliation.json') if close is None else close
    require(phase_row==('terminal',fingerprint(receipt)) and receipt.get('status')=='incomplete'
            and receipt.get('error_type') in ('BudgetStop','RecoverableLength') and not receipt.get('post_scoring_failure_count')
            and receipt.get('observations',{}).get('verified') is True and close.get('verified') is True
            and close.get('phase')==phase and close.get('phase_seal')==phase_row[1], 'Incomplete verified predecessor closure')
    directory=store/'runs'/phase
    for name,h in receipt['files'].items():
        p=directory/name
        require(p.is_relative_to(directory) and sha(p)==h, 'Stopped phase evidence changed')
    observations=receipt['observations']; path=Path(observations['evidence_path'])
    require(path.parent==directory and sha(path)==observations['evidence_sha256']==receipt['files'].get(path.name),
            'Critical observation evidence differs')
    proof=read(path);capture=read(directory/'trace-capture.json');meter=read(store/'service'/f'{phase}.json')
    units=len(capture['observations'])+len(set(capture['trace_ids']))+len(capture['scores'])
    require(proof.get('verified') is True and proof['identity'].get('run_id')==phase and not capture['errors']
            and units==meter['runtime_units_admitted']==meter['admitted_units']==close['service_units']
            and units<=CELL_SERVICE_UNITS and not meter['stopped'], 'Critical observation/service evidence is incomplete')
    rows=_current(db,phase)
    require(rows and close.get('physical_rows_sha256')==fingerprint(rows) and close.get('journal_seal')==_phase_financial_seal(db,phase)
            and _all_reservations_are_explained(db), 'Unknown or changed physical accounting')
    _verify_financial_pages(store,rows,close)
    prior=campaign/R1_CLOSE if ordinal==1 else attempt_store(campaign,ordinal-1)/'reconciliation.json'
    require(close['opening']['account']==read(prior)['closing'], 'Prior attempt opening differs')
    all_rows=[r for n in range(1,ordinal+1) for r in _current(db,phase_id(n))]
    total_known=sum((Decimal(r[9]) for r in all_rows if r[5]=='settled'),Decimal(0))
    local_known=sum((Decimal(r[9]) for r in rows if r[5]=='settled'),Decimal(0))
    hold=sum(r[4] for r in all_rows if r[5]!='settled')
    m,ok=_movement(close['opening']['account'],close['closing'],local_known,hold)
    gm,gok=_movement(read(campaign/R1_CLOSE)['closing'],close['closing'],total_known,hold)
    require(ok and gok and close['movement']==m and close['group_movement']==gm
            and close['model_conservative_microusd']==sum(r[4] for r in rows)
            and close['group_unresolved_reservations_microusd']==hold,'Prior monetary close differs')
    last=rows[-1]
    fail=db.execute('SELECT evidence FROM final_failures WHERE attempt=?',(last[0],)).fetchone()
    require(fail and db.execute('SELECT seq FROM final_slots WHERE attempt=?',(last[0],)).fetchone()==(1,),
            'Only an exhausted, bounded operational retry can support a fresh restart')
    final_failure=json.loads(fail[0])
    kind=_failure_kind(campaign,phase,last,final_failure)
    event=read(final_failure['physical_evidence_file'])
    reason=event['error_type']
    if receipt['error_type']=='RecoverableLength':
        require(kind=='invalid_output','Only an actual truncated shared decision can use length fallback')
        _length_fallback(directory,last,event)
        reason='verified_length_fallback'
    require(db.execute('SELECT reason FROM halts WHERE phase=?',(phase,)).fetchall()==[(reason,)],
            'Terminal cause does not match the bounded operational failure')
    require(db.execute('SELECT count(*) FROM final_slots WHERE seq=1').fetchone()[0]<6,
            'Group retry circuit breaker reached')
    return kind


def classify_restart(campaign, phase):
    try:
        n=next(n for n in (1,2) if phase_id(n)==phase)
        with sqlite3.connect(db_file(campaign).as_uri()+'?mode=ro',uri=True) as db:
            kind=_restart_reason(Path(campaign),db,n)
            return n==1 or kind!=_restart_reason(Path(campaign),db,n-1)
    except (BudgetStop, StopIteration, OSError, sqlite3.Error, ValueError, TypeError, KeyError, IndexError):
        return False


class FinalLedger:
    """Physical reservations are durable before POST. A retry never replaces its original row."""
    def __init__(self,campaign,approval,*,verify_approval,check_observations=None):
        self.root=Path(campaign).absolute()
        require(self.root.resolve()==self.root and callable(verify_approval), 'Invalid campaign or approval verifier')
        self.approved=copy.deepcopy(approval);self.verify=verify_approval
        require(self.verify(copy.deepcopy(approval)) is not False,'Financial release verification failed')
        self.original,self.old_signature,self.historical_ids=opening_history(self.root)
        self.path=db_file(self.root)
        self.core=CampaignLedger(self.path,campaign_root=self.path.parent,binding=approval['binding'])
        self.transaction=self.core.transaction
        self.claimed={};self.guards={};self.observations={}
        self.pending=None;self.failed=False;self.contracts=load_author_contracts();self.failure_files={}
        if check_observations is not None:self.observe_phase(approval['phase'],check_observations)
        with self.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS final_slots (attempt INTEGER PRIMARY KEY, phase TEXT NOT NULL, '
                       'slot INTEGER NOT NULL, seq INTEGER NOT NULL CHECK(seq IN (0,1)), retry_of INTEGER UNIQUE, UNIQUE(phase,slot,seq))')
            db.execute('CREATE TABLE IF NOT EXISTS final_failures (attempt INTEGER PRIMARY KEY, kind TEXT NOT NULL, evidence TEXT NOT NULL)')

    def observe_phase(self,phase,check):
        require(phase==self.approved['phase'] and phase not in self.observations and callable(check),'Invalid observation owner')
        self.observations[phase]=check

    def set_guard(self,phase,guard):
        require(phase in self.claimed and phase not in self.guards and callable(guard),'Invalid admission guard')
        self.guards[phase]=guard

    def claim(self,approval):
        require(now()<PAID_DEADLINE and approval==self.approved and not self.claimed,'Consumed, stale or expired final approval')
        require(self.verify(copy.deepcopy(approval)) is not False,'Financial release verification failed')
        n=approval['ordinal'];phase=phase_id(n);store=attempt_store(self.root,n)
        require(approval['phase']==phase and approval.get('approved') is True and approval.get('group')==GROUP
                and approval.get('kind')=='final_fresh' and approval.get('conversation')=='conv-44'
                and approval.get('condition')=='linking_only' and approval.get('repetition')==3+n
                and approval.get('service_reserve_microusd')==CELL_SERVICE_RESERVE and not approval.get('parent')
                and not approval.get('parent_path') and read(store/'frozen/approval.json')==approval,
                'Final approval differs from its allowed fresh run')
        require(not any((store/k).exists() or (store/k).is_symlink() for k in ('runs','cache','service','reconciliation.json')),
                'Fresh attempt store is used')
        previous=self.root/R1_CLOSE if n==1 else attempt_store(self.root,n-1)/'reconciliation.json'
        require(approval['opening_account']==read(previous)['closing'],'Unexplained opening wallet/key movement')
        with self.transaction() as db:
            phases=db.execute('SELECT id FROM phases ORDER BY rowid').fetchall()
            require(phases==[(phase_id(i),) for i in range(1,n)], 'Fresh attempt order differs')
            if n==1:
                require(all(not db.execute('SELECT 1 FROM '+table+' LIMIT 1').fetchone()
                            for table in ('attempts','halts','final_slots','final_failures')),'Foreign rows in new journal')
            if n>1:
                kind=_restart_reason(self.root,db,n-1)
                require(n<3 or kind!=_restart_reason(self.root,db,n-2),'Repeated same-class terminal failure')
            _bounds(db,extra_model=19650,extra_claims=1)
            db.execute("INSERT INTO phases VALUES (?,?,NULL,'running',NULL)",(phase,json.dumps(approval,sort_keys=True)))
            self.expected_digest=_journal_digest(db)
        self.claimed[phase]=copy.deepcopy(approval)
        self.approval_path=store/'frozen/approval.json';self.approval_sig=signature(self.approval_path)
        return phase

    def _check_journal(self,db):
        require(_journal_digest(db)==self.expected_digest,'Financial history changed outside the live owner')

    def logical_count(self,phase,db=None):
        if db is None:
            with self.transaction() as conn:return self.logical_count(phase,conn)
        return db.execute('SELECT count(*) FROM final_slots WHERE phase=? AND seq=0',(phase,)).fetchone()[0]

    def retry_count(self,phase=None):
        with self.transaction() as db:
            return db.execute('SELECT count(*) FROM final_slots WHERE seq=1'+(' AND phase=?' if phase else ''),
                              (phase,) if phase else ()).fetchone()[0]

    def unaccepted_unknowns(self,approval):
        with self.transaction() as db:
            return db.execute("SELECT count(*) FROM attempts a LEFT JOIN final_failures f ON f.attempt=a.id "
                              "WHERE a.state!='settled' AND (f.attempt IS NULL OR a.charge!=a.reservation)").fetchone()[0]

    def _reserve(self,phase,stage,body,failed_id):
        try:
            require(now()<PAID_DEADLINE and not self.failed and self.pending is None and phase in self.claimed
                    and phase in self.guards and phase in self.observations, 'Expired or unowned paid admission')
            self.observations[phase]()
            require(signature(self.original)==self.old_signature and signature(self.approval_path)==self.approval_sig
                    and all(signature(p)==v for p,v in self.failure_files.items()),
                    'Historical campaign or approved owner changed')
            limit=stage_output_limits(OPENROUTER_CONFIG)[stage]
            require(body['model']==MODEL and body['max_tokens']==limit and body['provider']==OPENROUTER_CONFIG['model']['provider']
                    and body['response_format']==self.contracts[stage] and body['temperature'] in ((.5,.7) if stage=='answer' else (.7,)),
                    'Unapproved generation contract')
            request_hash=fingerprint(body)
            reserve=int((INPUT_RATE*(CONTEXT-limit)+OUTPUT_RATE*limit).to_integral_value(rounding=ROUND_CEILING))
            with self.transaction() as db:
                self._check_journal(db)
                owner=db.execute('SELECT approval,state FROM phases WHERE id=?',(phase,)).fetchone()
                require(owner==(json.dumps(self.claimed[phase],sort_keys=True),'running') and not db.execute(
                    'SELECT 1 FROM halts WHERE phase=?',(phase,)).fetchone() and _all_reservations_are_explained(db),
                    'Stopped or unaccounted exposure')
                self.guards[phase](db)
                slot=self.logical_count(phase,db)
                last=db.execute('SELECT a.id,s.slot,s.seq,a.stage,a.request_hash,a.state,f.evidence FROM attempts a '
                                'JOIN final_slots s ON s.attempt=a.id LEFT JOIN final_failures f ON f.attempt=a.id '
                                'WHERE a.phase=? ORDER BY a.id DESC LIMIT 1',(phase,)).fetchone()
                if failed_id is None:
                    require(not last or (last[5]=='settled' and last[6] is None),'Previous logical operation unresolved')
                    seq=0
                else:
                    require(last and last[0]==failed_id and last[2]==0 and last[3:5]==(stage,request_hash)
                            and last[6] is not None and db.execute('SELECT count(*) FROM final_slots WHERE seq=1').fetchone()[0]<6,
                            'Not the one exact retry of the latest failed operation')
                    failed_row=_current(db,phase)[-1];_failure_kind(self.root,phase,failed_row,json.loads(last[6]))
                    slot=last[1];seq=1
                require(slot<len(STAGES) and STAGES[slot]==stage,'Unexpected logical operation stage')
                _bounds(db,extra_model=reserve)
                account=self.claimed[phase]['opening_account']
                phase_spend=db.execute('SELECT coalesce(sum(charge),0) FROM attempts WHERE phase=?',(phase,)).fetchone()[0]
                remaining=min(Decimal(account['credits']['total_credits'])-Decimal(account['credits']['total_usage']),
                              Decimal(account['key']['limit_remaining']))
                require(remaining*1000000 >= phase_spend+reserve, 'Insufficient verified wallet/key balance')
                require(now()<PAID_DEADLINE,'Paid admission deadline')
                attempt=db.execute('SELECT coalesce(max(id),?) + 1 FROM attempts',(LAST_ID,)).fetchone()[0]
                db.execute("INSERT INTO attempts(id,phase,stage,request_hash,reservation,charge,state) VALUES(?,?,?,?,?,?,'reserved')",
                           (attempt,phase,stage,request_hash,reserve,reserve))
                db.execute('INSERT INTO final_slots VALUES(?,?,?,?,?)',(attempt,phase,slot,seq,failed_id))
                self.expected_digest=_journal_digest(db)
            self.pending=(attempt,limit);self.latest=attempt
            return attempt,reserve
        except BaseException:
            self.failed=True
            raise BudgetStop('Final physical admission failed; no transmission') from None

    def reserve(self,phase,stage,body):
        return self._reserve(phase,stage,body,None)

    def reserve_retry(self,phase,stage,body,failed_attempt):
        return self._reserve(phase,stage,body,failed_attempt)

    def settle(self,attempt,response,output_limit):
        require(not self.failed and self.pending==(attempt,output_limit),'Cannot settle inherited, failed or unowned reservation')
        self.pending=None
        try:
            charge=usage_charge(response['usage'],output_limit)
            require(isinstance(response.get('id'),str) and response['id'].startswith('gen-'),'Missing provider identity')
            if response['id'] in self.historical_ids:
                self.retain_reported_liability(self.approved['phase'],attempt,response['usage']['cost'])
                raise BudgetStop('Original generation ID already belongs to a historical request')
            with self.transaction() as db:
                self._check_journal(db)
                row=db.execute('SELECT reservation,state FROM attempts WHERE id=?',(attempt,)).fetchone()
                require(row and row[1]=='reserved','No owned unsettled attempt')
                db.execute("UPDATE attempts SET charge=?,state='settled',response_hash=?,usage=?,provider_id=?,reported_cost=? WHERE id=?",
                           (charge,fingerprint(response),json.dumps(response['usage'],sort_keys=True),
                            response['id'],str(response['usage']['cost']),attempt))
                self.expected_digest=_journal_digest(db)
            require(charge<=row[0],'Observed provider charge exceeds reservation; actual charge retained')
            return charge
        except BaseException:
            self.failed=True
            raise

    def retain_reported_liability(self,phase,attempt,amount):
        require(phase in self.claimed and getattr(self,'latest',None)==attempt, 'Foreign unresolved liability')
        self.failed=True;self.pending=None
        charge=micros(amount)
        with self.transaction() as db:
            self._check_journal(db)
            changed=db.execute("UPDATE attempts SET charge=max(charge,?) WHERE id=? AND phase=?",
                               (charge,attempt,phase)).rowcount
            require(changed==1,'Unknown liability is not an active reservation')
            self.expected_digest=_journal_digest(db)

    def record_failure(self,phase,attempt,evidence):
        require(not self.failed and phase in self.claimed and attempt==getattr(self,'latest',None),'Foreign failure evidence')
        with self.transaction() as db:
            self._check_journal(db)
            rows=_current(db,phase);require(rows and rows[-1][0]==attempt,'Failed attempt is not latest owned physical request')
            kind=_failure_kind(self.root,phase,rows[-1],evidence)
            db.execute('INSERT INTO final_failures VALUES(?,?,?)',(attempt,kind,json.dumps(evidence,sort_keys=True)))
            self.expected_digest=_journal_digest(db)
        path=Path(evidence['physical_evidence_file']);self.failure_files[path]=signature(path)
        self.pending=None

    def stop(self,phase,reason):
        require(phase in self.claimed,'Foreign financial halt')
        self.failed=True
        with self.transaction() as db:
            self._check_journal(db)
            db.execute('INSERT OR IGNORE INTO halts VALUES (?,?)',(phase,reason))
            self.expected_digest=_journal_digest(db)

    def totals(self):
        return self.core.totals()

    def finish(self,phase,receipt,state):
        require(phase in self.claimed and receipt.get('phase')==phase,'Foreign financial seal')
        if state=='complete':
            with self.transaction() as db:
                bad=db.execute("SELECT count(*) FROM final_slots s JOIN attempts a ON a.id=s.attempt "
                        "LEFT JOIN final_failures f ON a.id=f.attempt WHERE s.phase=? AND "
                        "s.seq=(SELECT max(t.seq) FROM final_slots t WHERE t.phase=s.phase AND t.slot=s.slot) "
                        "AND (a.state!='settled' OR f.attempt IS NOT NULL)",(phase,)).fetchone()[0]
                require(self.logical_count(phase,db)==len(STAGES) and bad==0 and not self.failed,'Incomplete logical population')
        require(state in ('terminal','recoverable','complete'),'Unknown terminal state')
        seal=fingerprint(receipt)
        with self.transaction() as db:
            self._check_journal(db)
            count=db.execute("UPDATE phases SET state=?,seal=? WHERE id=? AND state='running'",
                             ('terminal' if state=='recoverable' else state,seal,phase)).rowcount
            require(count==1,'Already sealed')
            self.expected_digest=_journal_digest(db)
        return seal


class _DeadlineReads:
    """Limit the financial readback to known IDs and account endpoints within the window."""
    def __init__(self, client, ids):
        self.client=client
        self.headers=client.headers
        self.ids=set(ids)

    def get(self,url,*,params=None):
        left=(HARD_DEADLINE-now()).total_seconds()
        require(left>0,'Final reconciliation deadline reached')
        require((url==BASE_URL+'/generation' and set(params or {})=={'id'} and params['id'] in self.ids)
                or (url in (BASE_URL+'/credits',BASE_URL+'/key') and not params),'Unapproved readback endpoint or ID')
        return self.client.get(url,params=params,timeout=min(30,left))


def _check_hop(store,phase,row,generation):
    from .linking44_retry import retry_kind
    hop,=generation['provider_responses']
    require(hop.get('model_permaslug')==MODEL and hop.get('provider_name')=='OpenAI'
            and generation.get('provider_name')=='OpenAI' and generation.get('model')==MODEL
            and generation.get('id')==row[8], 'Unverified physical provider or version')
    if hop.get('status')!=200:
        event=read(store/'runs'/phase/'raw'/f'{row[0]:06d}-failure.json')
        attempt,=event['attempts']
        require(retry_kind(event)=='transient_http' and attempt['status_code']==hop.get('status')
                and attempt['budget_attempt_id']==row[0] and fingerprint(attempt['request_body'])==row[2]
                and fingerprint(attempt['response_body'])==row[6] and attempt['response_body']['id']==row[8],
                'Non-200 upstream lacks matching attributable failed native response')


def _read_known(client,store,phase,rows,journal):
    import time
    from scripts.gpt4omini_finance import journal_get
    details=[]
    for i,r in enumerate(rows):
        for poll in range(9):
            response=journal_get(client,'generation',{'id':r[8]},journal/f'{i}-{poll}.json')
            if response.status_code not in (404,429) or poll==8:break
            left=(HARD_DEADLINE-now()).total_seconds()
            require(left>0,'Financial GET deadline')
            time.sleep(min(30,2**poll,left))
        response.raise_for_status()
        g=response.json()['data'];_check_hop(store,phase,r,g)
        require(Decimal(str(g['total_cost']))==Decimal(r[9]),'Provider charge differs')
        details.append(g)
    return details


def _verify_financial_pages(store,rows,record):
    """Recheck the exact archived GETs, including native tokens, before allowing a successor."""
    from base64 import b64decode
    known=[r for r in rows if r[5]=='settled']
    journal=store/'financial-readbacks'
    require(record['generation_journal']==str(journal) and len(record['generations'])==len(known),'Readback population differs')
    for i,(r,g) in enumerate(zip(known,record['generations'],strict=True)):
        physical=read(store/'runs'/record['phase']/'raw'/f'{r[0]:06d}-response.bin')
        usage=json.loads(r[7])
        require(fingerprint(physical)==r[6] and physical['id']==g['id']==r[8] and physical['usage']==usage
                and physical['provider']==g['provider_name']=='OpenAI' and physical['model']==g['model']==MODEL
                and g['native_tokens_prompt']==usage['prompt_tokens'] and g['native_tokens_completion']==usage['completion_tokens']
                and Decimal(str(g['total_cost']))==Decimal(r[9])==Decimal(str(usage['cost']))
                and r[4]>=usage_charge(usage, 4096 if r[1]=='shared_decision' else 1000),'Known provider record differs')
        _check_hop(store,record['phase'],r,g)
        pages=sorted(journal.glob(f'{i}-*.json')); require(1<=len(pages)<=9,'Generation journal differs')
        for poll,p in enumerate(pages):
            item=read(p)
            require(p.name==f'{i}-{poll}.json' and item['endpoint']=='generation' and item['params']=={'id':r[8]},
                    'Foreign generation readback')
            if poll+1==len(pages):
                require(item['status']==200 and json.loads(b64decode(item['response_base64']))['data']==g,'Archived provider GET differs')
            else:
                require(item['status'] in (404,429),'Unsupported financial readback')
    for folder,account in ((store/'opening-reads',record['opening']['account']),(journal/'account',record['closing'])):
        for endpoint in ('credits','key'):
            page=read(folder/f'{endpoint}.json')
            require(page['status']==200 and page['endpoint']==endpoint and not page['params'],'Account readback differs')
            data=json.loads(b64decode(page['response_base64']))['data']
            require(all(Decimal(str(data[k]))==Decimal(v) for k,v in account[endpoint].items()),'Original account reading differs')


def _movement(opening,closing,known,held):
    """A zero residual cannot adjudicate an unobserved charge."""
    from scripts.gpt4omini_finance import compare
    m=compare(opening,closing,0,known)
    residue=Decimal(m['unexplained_account_delta'])
    key_drop=Decimal(opening['key']['limit_remaining'])-Decimal(closing['key']['limit_remaining'])
    safe=(Decimal(m['credit_adjustment'])==0 and residue==Decimal(m['unexplained_key_delta'])
          and Decimal(0)<=residue<=Decimal(held)/1_000_000 and key_drop==Decimal(m['key_usage_delta']))
    return m,safe


def close_attempt(client,ledger,phase,store,receipt,opening,units):
    from scripts.gpt4omini_finance import snapshot
    store=Path(store)
    require(now()<HARD_DEADLINE and phase in ledger.claimed and opening==ledger.claimed[phase]['opening_account']
            and store==attempt_store(ledger.root,ledger.claimed[phase]['ordinal']), 'Foreign or expired attempt close')
    meter=read(store/'service'/f'{phase}.json')
    require(units==meter['admitted_units'] and 0<=units<=meter['maximum_units']==CELL_SERVICE_UNITS,
            'Service accounting exceeds authorization')
    with ledger.transaction() as db:
        require(db.execute('SELECT seal FROM phases WHERE id=?',(phase,)).fetchone()==(fingerprint(receipt),),'Phase seal differs')
        ledger._check_journal(db)
        journal_seal=_phase_financial_seal(db,phase)
        rows=_current(db,phase)
        phases=db.execute('SELECT id FROM phases ORDER BY rowid').fetchall()
        cumulative=[r for p, in phases for r in _current(db,p)]
        _bounds(db)
    known=[r for r in rows if r[5]=='settled'];unknown=[r for r in rows if r[5]!='settled']
    journal=store/'financial-readbacks'
    reader=_DeadlineReads(client,[r[8] for r in known])
    details=_read_known(reader,store,phase,known,journal)
    closing=snapshot(reader,journal/'account')
    cost=sum((Decimal(r[9]) for r in known),Decimal(0))
    group_open=read(ledger.root/R1_CLOSE)['closing']
    group_known=sum((Decimal(r[9]) for r in cumulative if r[5]=='settled'),Decimal(0))
    full_hold=sum(r[4] for r in cumulative if r[5]!='settled')
    movement,local_safe=_movement(opening,closing,cost,full_hold)
    group_movement,group_safe=_movement(group_open,closing,group_known,full_hold)
    record={'verified':local_safe and group_safe,'phase':phase,'phase_seal':fingerprint(receipt),
            'physical_rows_sha256':fingerprint(rows),'journal_seal':journal_seal,'logical_operations':ledger.logical_count(phase),
            'physical_transmissions':len(rows),'retries':ledger.retry_count(phase),'group_retries':ledger.retry_count(),
            'settled_count':len(known),'settled_attempts_sha256':fingerprint(known),'known_cost_usd':str(cost),
            'model_conservative_microusd':sum(r[4] for r in rows),'unknown_attempt_ids':[r[0] for r in unknown],
            'group_unresolved_reservations_microusd':full_hold,'historical_unresolved_reservations_microusd':99644,
            'known_only_exact_movement':movement['verified'],'movement':movement,'group_movement':group_movement,
            'opening':{'account':opening},'closing':closing,'closing_prepaid_usd':str(Decimal(closing['credits']['total_credits'])-Decimal(closing['credits']['total_usage'])),
            'service_units':units,'service_earmark_microusd':CELL_SERVICE_RESERVE,'group_earmarks_microusd':len(phases)*CELL_SERVICE_RESERVE,
            'generations':details,'generation_journal':str(journal),'individual_unknown_adjudicated':False,'restart_eligible':False}
    _verify_financial_pages(store,rows,record)
    n=ledger.claimed[phase]['ordinal']
    if record['verified'] and receipt['status']=='incomplete' and n<3 and now()<PAID_DEADLINE:
        with ledger.transaction() as db:
            try:
                kind=_restart_reason(ledger.root,db,n,record)
                record['restart_eligible']=n==1 or kind!=_restart_reason(ledger.root,db,n-1)
            except (BudgetStop,KeyError,ValueError,TypeError,OSError,IndexError):
                pass
    with ledger.transaction() as db:ledger._check_journal(db)
    require(signature(ledger.original)==ledger.old_signature and now()<HARD_DEADLINE,'History or deadline changed before financial verification')
    save_new(store/'reconciliation.json',record)
    require(record['verified'],'Unbounded or unexplained account/key movement')
    return record
