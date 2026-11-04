"""Isolated native-schema OpenRouter transport and durable one-cell accounting.

No SDK, implicit retry, function translation, JSON repair or historical ledger is
used. A physical request is admitted durably before HTTP and settled only from a
complete response with usage and cost. Unknown exposure is terminal.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from .adapter import AdapterError, _observed_payload
from .budget import BudgetStop
from .config import AUTHOR_REVISION, OPENROUTER_CONFIG, fingerprint, stage_output_limits
from .contracts import load_author_contracts, validate_arguments

CAMPAIGN = 'amem-gpt4omini-openrouter-20261104-v1'
MODEL = OPENROUTER_CONFIG['model']['id']
BASE_URL = OPENROUTER_CONFIG['model']['base_url']
CONTEXT = 128000
INPUT_RATE = Decimal('.15')  # microUSD / token, without cache discounts
OUTPUT_RATE = Decimal('.60')
SCIENTIFIC_BINDING = {'campaign_id':CAMPAIGN,'config_sha256':fingerprint(OPENROUTER_CONFIG),
    'dataset_sha256':'79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4',
    'author_revision':AUTHOR_REVISION}


def save_new(path, value):
    """Exclusive durable evidence; callers never overwrite consumed evidence."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def micros(value):
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        raise BudgetStop('Invalid financial value')
    return int((number * 1000000).to_integral_value(rounding=ROUND_CEILING))


def usage_charge(usage, output_limit):
    if (not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0
            for k in ('prompt_tokens', 'completion_tokens'))
            or usage['prompt_tokens'] + usage['completion_tokens'] > CONTEXT
            or usage['completion_tokens'] > output_limit or 'cost' not in usage):
        raise BudgetStop('Incomplete or out-of-bounds provider usage/cost')
    conservative = int((INPUT_RATE * usage['prompt_tokens'] + OUTPUT_RATE * usage['completion_tokens'])
                       .to_integral_value(rounding=ROUND_CEILING))
    return max(conservative, micros(usage['cost']))


class CampaignLedger:
    """One fresh ledger; immutable phase approvals, exclusive ownership and SQL caps."""
    def __init__(self, path, *, campaign_root, binding):
        if Path(campaign_root).absolute()!=Path(campaign_root).resolve():
            raise BudgetStop('Campaign root cannot alias historical storage')
        self.root = Path(campaign_root).resolve()
        self.path = Path(path)
        # Resolve BEFORE connecting, including a symlink/hardlink to any older ledger.
        if (self.path.is_symlink() or self.path.resolve() != self.root / 'budget.sqlite'
                or (self.path.exists() and self.path.stat().st_nlink != 1)):
            raise BudgetStop('Campaign ledger must be its own regular isolated file')
        self.root.mkdir(parents=True, exist_ok=True)
        self.binding = copy.deepcopy(binding)
        if any(binding.get(k)!=v for k,v in SCIENTIFIC_BINDING.items()):
            raise BudgetStop('Campaign scientific binding differs from the authorized identity')
        self.failed = False
        self.claimed = {}
        self.guards = {}
        self._file_identity=None
        self._root_identity=None
        encoded=json.dumps(SCIENTIFIC_BINDING,sort_keys=True)
        if self.path.exists():
            # A foreign ledger is inspected read-only before ANY schema/pragma write.
            try:
                with sqlite3.connect(self.path.resolve().as_uri()+'?mode=ro',uri=True) as db:
                    previous=db.execute('SELECT binding FROM campaign WHERE id=?',(CAMPAIGN,)).fetchone()
                    if previous!=(encoded,):raise BudgetStop('Existing file belongs to another campaign')
            except sqlite3.Error:
                raise BudgetStop('Existing file is not this campaign ledger') from None
        with self.transaction() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS campaign (id TEXT PRIMARY KEY, binding TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS phases (id TEXT PRIMARY KEY, approval TEXT NOT NULL,
                    parent TEXT UNIQUE, state TEXT NOT NULL, seal TEXT);
                CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, phase TEXT NOT NULL,
                    stage TEXT NOT NULL, request_hash TEXT NOT NULL, reservation INTEGER NOT NULL,
                    charge INTEGER NOT NULL, state TEXT NOT NULL, response_hash TEXT, usage TEXT,
                    provider_id TEXT UNIQUE, reported_cost TEXT);
                CREATE TABLE IF NOT EXISTS halts (phase TEXT PRIMARY KEY, reason TEXT NOT NULL);
            ''')
            previous = db.execute('SELECT binding FROM campaign WHERE id=?', (CAMPAIGN,)).fetchone()
            if previous and previous[0] != encoded:
                raise BudgetStop('Campaign configuration/provenance changed')
            db.execute('INSERT OR IGNORE INTO campaign VALUES (?,?)', (CAMPAIGN, encoded))
        self._file_identity=(self.path.stat().st_dev,self.path.stat().st_ino)
        self._root_identity=(self.root.stat().st_dev,self.root.stat().st_ino)

    @contextmanager
    def transaction(self):
        if (self.root.absolute()!=self.root.resolve() or self.path.is_symlink()
                or self.path.resolve()!=self.root/'budget.sqlite'
                or (self.path.exists() and self.path.stat().st_nlink!=1)
                or (self._file_identity is not None and
                    self._file_identity!=(self.path.stat().st_dev,self.path.stat().st_ino))
                or (self._root_identity is not None and
                    self._root_identity!=(self.root.stat().st_dev,self.root.stat().st_ino))):
            self.failed=True
            raise BudgetStop('Campaign storage changed or aliases other evidence')
        db = sqlite3.connect(self.path, timeout=30)
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def access_snapshot(db, exclude_phase=None):
        """Exact prior financial history; retained rows are never rewritten."""
        return {
            'phases': [list(r) for r in db.execute('SELECT * FROM phases ORDER BY rowid')
                       if r[0] != exclude_phase],
            'attempts': [list(r) for r in db.execute('SELECT * FROM attempts ORDER BY id')
                         if r[1] != exclude_phase],
            'halts': [list(r) for r in db.execute('SELECT * FROM halts ORDER BY phase')
                      if r[0] != exclude_phase],
        }

    def _access_retest(self, db, approval, *, exclude_phase=None):
        """Narrow new user grant: one metadata access check after the retained403.

        This cannot release baseline execution or adjudicate the prior charge.
        The original terminal phase/halt/unknown reservation remain authoritative.
        """
        grant = approval.get('access_retest', {})
        snapshot = self.access_snapshot(db, exclude_phase)
        phases, attempts, halts = (snapshot[k] for k in ('phases','attempts','halts'))
        if (grant.get('policy') != 'updated-key-one-probe-20261104-v1'
                or approval.get('kind') != 'compatibility'
                or approval.get('limits',{}).get('max_physical_calls') != 1
                or grant.get('retained_snapshot') != snapshot
                or len(phases) != 1 or len(attempts) != 1 or len(halts) != 1):
            raise BudgetStop('Exact one-probe updated-key authorization required')
        previous, attempt = phases[0], attempts[0]
        if (previous[3] != 'terminal' or not previous[4]
                or approval.get('parent') != previous[0]
                or approval.get('parent_seal') != previous[4]
                or json.loads(previous[1]).get('kind') != 'compatibility'
                or attempt[1] != previous[0] or attempt[2] != 'metadata'
                or attempt[4:7] != [19650,19650,'reserved']
                or attempt[9] is not None or attempt[10] is not None
                or halts[0][0] != previous[0]
                or not isinstance(grant.get('request_sha256'),str)
                or len(grant['request_sha256']) != 64):
            raise BudgetStop('Retained denial lineage changed')

    def claim(self, approval):
        if (approval.get('approved') is not True or approval.get('binding') != self.binding
                or approval.get('kind') not in ('compatibility', 'baseline')
                or approval.get('condition') != 'full' or approval.get('conversation') != 'conv-44'):
            raise BudgetStop('Explicit exact campaign/cell approval required')
        phase = approval['phase']
        parent = approval.get('parent')
        with self.transaction() as db:
            rows = db.execute('SELECT id,approval,state,seal FROM phases ORDER BY rowid').fetchall()
            retest = bool(approval.get('access_retest'))
            if retest:
                self._access_retest(db, approval)
            if not retest and any(row[2] not in ('complete','recoverable') for row in rows):
                raise BudgetStop('An earlier phase is unfinished or terminal')
            same = [r for r in rows if json.loads(r[1])['kind'] == approval['kind']]
            if parent and not retest:
                if (not same or same[-1][0] != parent or same[-1][2] != 'recoverable'
                        or not same[-1][3] or approval.get('parent_seal') != same[-1][3]):
                    raise BudgetStop('Continuation must own the last sealed recoverable parent')
            elif same and not retest:
                raise BudgetStop('A fresh root cannot repeat a consumed campaign phase')
            db.execute('INSERT INTO phases VALUES (?,?,?,\'running\',NULL)',
                       (phase,json.dumps(approval,sort_keys=True),parent))
        self.claimed[phase]=copy.deepcopy(approval)
        return phase

    def reserve(self, phase, stage, request):
        if self.failed:
            raise BudgetStop('Financial control already failed')
        try:
            limits = stage_output_limits(OPENROUTER_CONFIG)
            if stage not in limits or request['max_tokens'] != limits[stage]:
                raise BudgetStop('Unapproved output allowance')
            reserve = int((INPUT_RATE * (CONTEXT-limits[stage]) + OUTPUT_RATE*limits[stage])
                          .to_integral_value(rounding=ROUND_CEILING))
            with self.transaction() as db:
                row = db.execute('SELECT approval,state FROM phases WHERE id=?',(phase,)).fetchone()
                if (not row or row[1] != 'running' or phase not in self.claimed
                        or json.loads(row[0])!=self.claimed[phase]):
                    raise BudgetStop('Phase is not an active one-shot owner')
                approval = json.loads(row[0])
                retest = bool(approval.get('access_retest'))
                if retest:
                    self._access_retest(db, approval, exclude_phase=phase)
                    if (db.execute('SELECT COUNT(*) FROM halts WHERE phase=?',(phase,)).fetchone()[0]
                            or stage != 'metadata'
                            or fingerprint(request) != approval['access_retest']['request_sha256']
                            or db.execute('SELECT COUNT(*) FROM attempts WHERE phase=?',(phase,)).fetchone()[0]):
                        raise BudgetStop('Updated-key access grant permits one exact metadata request')
                elif db.execute('SELECT COUNT(*) FROM halts').fetchone()[0]:
                    raise BudgetStop('A terminal campaign failure forbids further transmissions')
                if phase in self.guards:self.guards[phase](db)
                if approval['binding'] != self.binding:
                    raise BudgetStop('Immutable approval changed')
                if not retest and db.execute("SELECT COUNT(*) FROM attempts WHERE state!='settled'").fetchone()[0]:
                    raise BudgetStop('Unknown financial exposure; no further transmission')
                spent, count = db.execute('SELECT COALESCE(SUM(charge),0),COUNT(*) FROM attempts').fetchone()
                kind = approval['kind']
                kind_count = db.execute('SELECT COUNT(*) FROM attempts a JOIN phases p ON a.phase=p.id '
                    "WHERE json_extract(p.approval,'$.kind')=?",(kind,)).fetchone()[0]
                kind_spent = db.execute('SELECT COALESCE(SUM(a.charge),0) FROM attempts a JOIN phases p ON a.phase=p.id '
                    "WHERE json_extract(p.approval,'$.kind')=?",(kind,)).fetchone()[0]
                if (spent+reserve > 5_000_000 or spent+reserve > 42_000_000
                        or (kind=='compatibility' and kind_spent+reserve > 250_000)
                        or kind_count >= (8 if kind=='compatibility' else 1666)):
                    raise BudgetStop('Cell/smoke/campaign call or spending cap reached')
                cursor = db.execute('INSERT INTO attempts (phase,stage,request_hash,reservation,charge,state) '
                    "VALUES (?,?,?,?,?,'reserved')",(phase,stage,fingerprint(request),reserve,reserve))
                return cursor.lastrowid, reserve
        except BaseException:
            self.failed = True
            raise BudgetStop('Financial admission failed; no transmission permitted') from None

    def set_guard(self, phase, guard):
        if phase not in self.claimed or phase in self.guards:
            raise BudgetStop('Admission guard must bind exactly once to the claimed owner')
        self.guards[phase]=guard

    def settle(self, attempt, response, output_limit):
        try:
            usage = response['usage']
            charge = usage_charge(usage, output_limit)
            if not isinstance(response.get('id'),str) or not response['id'].startswith('gen-'):
                raise BudgetStop('Missing original provider generation identity')
            over_reservation=False
            with self.transaction() as db:
                row = db.execute('SELECT state,reservation FROM attempts WHERE id=?',(attempt,)).fetchone()
                if not row or row[0] != 'reserved':
                    raise BudgetStop('Duplicate settlement')
                over_reservation=charge>row[1]
                db.execute("UPDATE attempts SET state='settled',charge=?,response_hash=?,usage=?,provider_id=?,reported_cost=? WHERE id=?",
                    (charge,fingerprint(response),json.dumps(usage,sort_keys=True),response['id'],str(usage['cost']),attempt))
        except BaseException:
            self.failed = True
            raise BudgetStop('Usage settlement failed; full reservation retained') from None
        if over_reservation:
            self.failed=True
            raise BudgetStop('Actual provider charge exceeds reservation; full known charge retained')
        return charge

    def stop(self, phase, reason):
        self.failed=True
        try:
            with self.transaction() as db:
                db.execute('INSERT OR IGNORE INTO halts VALUES (?,?)',(phase,reason))
        except BaseException:
            # The claimed unfinished phase and this process latch remain closed.
            pass

    def finish(self, phase, receipt, state):
        if state not in ('complete','recoverable','terminal'):
            raise BudgetStop('Invalid terminal phase state')
        seal = fingerprint(receipt)
        if phase not in self.claimed:raise BudgetStop('Only the claimed phase owner can seal')
        with self.transaction() as db:
            changed = db.execute("UPDATE phases SET state=?,seal=? WHERE id=? AND state='running'",
                                 (state,seal,phase)).rowcount
            if changed != 1:
                raise BudgetStop('Phase has already been sealed')
        return seal

    def totals(self):
        with self.transaction() as db:
            rows = db.execute('SELECT charge,state,reported_cost FROM attempts').fetchall()
        return {'attempts':len(rows),'conservative_microusd':sum(r[0] for r in rows),
                'unknown_attempts':sum(r[1]!='settled' for r in rows),
                'reported_cost_usd':str(sum((Decimal(r[2]) for r in rows if r[2] is not None),Decimal(0)))}


class OpenRouterController:
    """The author's four exact JSON-schema requests and unchanged content strings."""
    def __init__(self, client, *, ledger, phase, journal, observer=None):
        self.client, self.ledger, self.phase = client, ledger, phase
        self.journal, self.observer = Path(journal), observer
        self.observer_errors = []
        self.contracts = load_author_contracts()
        self.pending = None

    def get_completion(self, prompt, response_format, temperature=.7):
        stages = [k for k,v in self.contracts.items() if fingerprint(v)==fingerprint(response_format)]
        if len(stages)!=1 or temperature not in ({.5,.7} if stages[0]=='answer' else {.7}):
            raise BudgetStop('Request differs from the frozen author contracts/settings')
        if self.pending:
            raise BudgetStop('Original fallback must be independently verified before another request')
        stage = stages[0]
        limit = stage_output_limits(OPENROUTER_CONFIG)[stage]
        body = {'model':MODEL,'messages':[{'role':'system','content':'You must respond with a JSON object.'},
                {'role':'user','content':prompt}],'response_format':copy.deepcopy(response_format),
                'temperature':temperature,'max_tokens':limit,'stream':False,
                'provider':copy.deepcopy(OPENROUTER_CONFIG['model']['provider'])}
        event = {'stage':stage,'started_at':datetime.now(timezone.utc).isoformat(),'prompt':prompt,
                 'response_format':copy.deepcopy(response_format),'model':MODEL,
                 'endpoint':BASE_URL+'/chat/completions','documented_model_version':MODEL,
                 'temperature':temperature,'max_tokens':limit,'thinking':'not-applicable',
                 'provider_contract_policy':'strict-original-v1','output':None,'usage':None,
                 'campaign_cost_policy':'openrouter-ledger-v1',
                 'error_type':None,'attempts':[],'raw_schema_valid':False,
                 'validation_copy_schema_valid':False,'compatibility_deviation':None}
        started = time.perf_counter()
        try:
            if hasattr(self.observer,'begin_generation'):
                self.observer.begin_generation(copy.deepcopy(event))
            attempt, reserve = self.ledger.reserve(self.phase,stage,body)
            save_new(self.journal/f'{attempt:06d}-request.json',body)
            event['budget_logical_id'] = attempt
            event['attempts']=[{'attempt':1,'status_code':None,'error_type':None,
                'request_body':body,'response_body':None,'usage':None,
                'budget_attempt_id':attempt,'reservation_microusd':reserve}]
            raw = self.client.post(BASE_URL+'/chat/completions',json=body)
            event['attempts'][0]['status_code']=raw.status_code
            # Preserve exact bytes as well as parsed objects, without headers/secrets.
            path = self.journal/f'{attempt:06d}-response.bin'
            with path.open('xb') as stream:
                stream.write(raw.content);stream.flush();os.fsync(stream.fileno())
            response = raw.json()
            event['provider_response'] = response
            event['attempts'] = [{'attempt':1,'status_code':raw.status_code,'error_type':None,
                'request_body':body,'response_body':response,'usage':response.get('usage'),
                'budget_attempt_id':attempt,'reservation_microusd':reserve}]
            raw.raise_for_status()
            # Keep known price evidence even when anomalous liability forces a stop.
            event['conservative_cost_usd']=usage_charge(response.get('usage'),limit)/1000000
            charge = self.ledger.settle(attempt,response,limit)
            event['attempts'][0]['charged_cost_usd'] = charge/1000000
            event.update(usage=response['usage'],request_id=response.get('id'),
                returned_model=response.get('model'),system_fingerprint=response.get('system_fingerprint'),
                actual_provider=response.get('provider'),conservative_cost_usd=charge/1000000)
            if response.get('model') != MODEL or response.get('provider') != 'OpenAI':
                raise BudgetStop('Actual provider or dated model differs from the frozen route')
            choices = response.get('choices')
            if not isinstance(choices,list) or len(choices)!=1:
                raise BudgetStop('Unexpected response choices')
            choice = choices[0]; message = choice['message']
            content = message.get('content')
            event['output'] = content
            if (message.get('refusal') or message.get('tool_calls') or not isinstance(content,str)):
                raise BudgetStop('Unsupported refusal/function response')
            if choice.get('finish_reason') == 'length' and stage=='shared_decision':
                self.pending = {'kind':'length','event':event}
                raise AdapterError('Shared decision output exhausted; original fallback only')
            if choice.get('finish_reason') != 'stop':
                raise BudgetStop('Unexpected completion finish reason')
            try:
                value = json.loads(content,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
            except json.JSONDecodeError as error:
                if stage=='shared_decision' and content.strip().startswith('{') and content.strip().endswith('}'):
                    self.pending = {'kind':'malformed','event':event}
                    raise AdapterError('Malformed shared decision; unchanged original fallback') from error
                raise BudgetStop('Unsupported malformed output') from None
            validate_arguments(value,response_format['json_schema']['schema'])
            event.update(raw_schema_valid=True,validation_copy_schema_valid=True)
            return content
        except AdapterError:
            event['error_type']='AdapterError'
            raise
        except BaseException as error:
            event['error_type']=type(error).__name__
            event['error_message']=str(error)
            if event['attempts']:
                event['attempts'][0].update(error_type=type(error).__name__,error_message=str(error))
            self.ledger.stop(self.phase,event['error_type'])
            raise BudgetStop('Provider/validation/control failure; no further paid request') from None
        finally:
            event['duration_seconds'] = time.perf_counter()-started
            if event['attempts']:
                event['attempts'][0]['duration_seconds']=event['duration_seconds']
            safe = _observed_payload(event,getattr(self.client,'_amem_credential',None))
            # Critical local observation failure is terminal, outside author catches.
            if self.observer:
                try:self.observer(safe)
                except BaseException:
                    self.ledger.stop(self.phase,'generation_evidence_failed')
                    raise BudgetStop('Generation evidence persistence failed') from None
