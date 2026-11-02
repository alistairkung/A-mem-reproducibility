"""Durable, conservative spending limits before each physical transmission.

A permit is one approved phase session, not a Boolean permission to spend.
Unknown or interrupted attempts retain their maximum reservation. Token-based
charges use the approved peak rates without cache discounts; they are not invoices.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path

from .config import (
    fingerprint, reject_credentials, validate_provider_policy, STRICT_PROVIDER_POLICY,
    stage_output_limits,
    DEFAULT_CONFIG,
)

MICROS = Decimal(1_000_000)
GLOBAL_USABLE_MICROS = 42_000_000  # USD 50 total less the USD 8 contingency.
STAGES = {'metadata', 'shared_decision', 'query_keywords', 'answer'}
STUDY_JOB_CAPS = {
    (condition,conversation):10_000_000
    for condition,conversations in [('full',('conv-49','conv-44')),
        ('neither',('conv-49','conv-50','conv-44')),('linking_only',('conv-49','conv-50','conv-44')),
        ('evolution_only',('conv-49','conv-50','conv-44'))]
    for conversation in conversations
}
# Per-cell USD10 ceilings share the SAME USD42 cumulative ledger bound; they are
# not additive spending authority. Prior USD3.025799 leaves USD38.974201 new spend.


class BudgetStop(BaseException):
    """Protocol stop; deliberately escapes frozen author/SDK Exception fallbacks."""


def _number(value, label):
    if isinstance(value, bool):
        raise BudgetStop(f'{label} must be a finite positive number')
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise BudgetStop(f'{label} must be a finite positive number') from None
    if not number.is_finite() or number <= 0:
        raise BudgetStop(f'{label} must be a finite positive number')
    return number


def _integer(value, label, minimum=1):
    if type(value) is not int or value < minimum:
        raise BudgetStop(f'{label} must be an integer >= {minimum}')
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _validate(auth, binding):
    try:
        reject_credentials(auth)
        fingerprint(auth)
        if auth['approved'] is not True:
            raise BudgetStop('Separate explicit paid approval is required')
        for name in ('approval_id', 'approved_by', 'run_id'):
            if not isinstance(auth[name], str) or not auth[name].strip():
                raise BudgetStop(f'{name} is required')
        approved_at = datetime.fromisoformat(auth['approved_at'].replace('Z', '+00:00'))
        if approved_at.tzinfo is None:
            raise BudgetStop('Approval time requires an explicit timezone')
        phase = auth['phase']
        phase_max = {'compatibility':Decimal(2), 'pilot':Decimal(10), 'baseline':Decimal(42)}
        if phase not in phase_max or auth['binding'] != binding:
            raise BudgetStop('Approval phase or immutable binding mismatch')
        validate_provider_policy(binding.get('provider_contract_policy', STRICT_PROVIDER_POLICY))
        output_limits = binding['max_output_tokens_by_stage']
        expected_limits = stage_output_limits()
        if (type(output_limits) is not dict or output_limits != expected_limits
            or any(type(limit) is not int for limit in output_limits.values())):
            raise BudgetStop('Stage output limits differ from the approved policy')
        for name in ('manifest_sha256', 'config_sha256', 'source_sha256', 'preflight_sha256'):
            digest = binding[name]
            if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
                raise BudgetStop(f'{name} must be a complete SHA-256 fingerprint')
        study_job = binding.get('study_job')
        if phase=='baseline' and study_job is None:
            raise BudgetStop('Baseline execution requires its exact one-shot study job binding')
        if study_job is not None:
            condition = binding['condition']
            conversation = study_job['conversation_id']
            calls = {'conv-49':1410, 'conv-50':1544, 'conv-44':1666}
            if (phase != 'baseline' or binding['population'] != 'fallback'
                    or condition not in DEFAULT_CONFIG['conditions']
                    or type(binding.get('memory_actions')) is not dict
                    or binding.get('memory_actions') != DEFAULT_CONFIG['conditions'][condition]
                    or any(type(v) is not bool for v in binding['memory_actions'].values())
                    or binding.get('action_policy') != 'released-action-boundaries-v1'
                    or binding.get('action_implementation') != ('frozen-author' if condition == 'full' else 't7-action-gates')
                    or binding.get('conversation_ids') != [conversation]
                    or study_job != {'study_id':'d10a-fallback-once-v1', 'conversation_id':conversation,
                                     'expected_logical_calls':calls.get(conversation), 'initial_study_microusd':3025799}
                    or conversation not in calls or condition == 'full' and conversation == 'conv-50'
                    or type(study_job.get('expected_logical_calls')) is not int
                    or type(study_job.get('initial_study_microusd')) is not int
                    or binding.get('study_budget') != {'additional_ceiling_microusd':38974201,
                        'cumulative_usable_microusd':42000000,'contingency_microusd':8000000}
                    or binding['repetition'] != 0):
                raise BudgetStop('Main study job/action binding differs from the frozen fallback')
        if (binding['condition'] != 'full' and study_job is None) or binding['model'] != 'deepseek-flash':
            raise BudgetStop('T5 permits only original full-mode DeepSeek execution')
        if binding['endpoint'] != 'https://api.deepseek.com/beta/chat/completions':
            raise BudgetStop('Endpoint differs from the frozen protocol')
        if (phase == 'compatibility' and binding['population'] != 'smoke') or (phase == 'pilot' and binding['population'] != 'pilot'):
            raise BudgetStop('Phase population mismatch')
        if phase == 'baseline' and binding['population'] not in ('full','fallback'):
            raise BudgetStop('Baseline requires an approved full or fallback population')
        _integer(binding['repetition'], 'repetition', 0)
        limits = auth['limits']
        logical = _integer(limits['max_logical_calls'], 'max_logical_calls')
        attempts = _integer(limits['max_attempts'], 'max_attempts')
        max_calls = {'compatibility':44, 'pilot':1544, 'baseline':15736}[phase]
        if logical > max_calls or attempts > 3*logical:
            raise BudgetStop('Request limits exceed the approved phase or retry protocol')
        if study_job is not None and logical != study_job['expected_logical_calls']:
            raise BudgetStop('Main request limit differs from the complete conversation')
        if 'checkpoint' in binding:
            checkpoint = binding['checkpoint']
            if (phase != 'pilot' or not isinstance(checkpoint, dict)
                    or checkpoint.get('policy') != 'blk014-checkpoint-v1'
                    or checkpoint.get('completed_turns') != 263
                    or checkpoint.get('remaining_logical_calls') != 1018 or logical > 1018):
                raise BudgetStop('Checkpoint request limits or policy differ')
            for name in ('parent_phase_sha256', 'parent_snapshot_sha256',
                         'parent_events_sha256', 'parent_source_sha256'):
                digest = checkpoint.get(name)
                if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                    raise BudgetStop('Checkpoint requires complete parent fingerprints')
        cap = _number(limits['phase_usd'], 'phase_usd')
        if cap > phase_max[phase]:
            raise BudgetStop('Phase ceiling exceeds the frozen allocation')
        cap_micros = int((cap*MICROS).to_integral_value(rounding=ROUND_FLOOR))
        if cap_micros <= 0:
            raise BudgetStop('Phase ceiling is below one microdollar')
        if study_job is not None and cap_micros > STUDY_JOB_CAPS[(condition,conversation)]:
            raise BudgetStop('Main phase ceiling exceeds its authorized allocation')
        pricing = auth['pricing']
        if not isinstance(pricing['pricing_id'],str) or not pricing['pricing_id'].strip():
            raise BudgetStop('A reviewed pricing identifier is required')
        input_rate = _number(pricing['input_per_million'], 'input price')
        output_rate = _number(pricing['output_per_million'], 'output price')
        if input_rate < Decimal('.30') or output_rate < Decimal('1.20'):
            raise BudgetStop('Rates cannot undercut the reviewed peak-price bound')
        context = _integer(pricing['max_context_tokens'], 'max_context_tokens')
        max_output = max(expected_limits.values())
        if context < 1048576 or pricing['max_output_tokens'] != max_output or type(pricing['max_output_tokens']) is not int:
            raise BudgetStop('Token bounds differ from the frozen conservative limits')
        reserve = int((context*input_rate+max_output*output_rate).to_integral_value(rounding=ROUND_CEILING))
        return cap_micros, reserve, input_rate, output_rate
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise BudgetStop(f'Malformed approval: {type(error).__name__}') from None


SCHEMA = '''
CREATE TABLE IF NOT EXISTS phases (
 approval_id TEXT PRIMARY KEY, run_id TEXT UNIQUE NOT NULL, auth_json TEXT NOT NULL,
 owner TEXT NOT NULL, phase_cap INTEGER NOT NULL, halted TEXT
);
CREATE TABLE IF NOT EXISTS logical_calls (
 id INTEGER PRIMARY KEY, approval_id TEXT NOT NULL REFERENCES phases, stage TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
 id INTEGER PRIMARY KEY, logical_id INTEGER NOT NULL REFERENCES logical_calls,
 approval_id TEXT NOT NULL REFERENCES phases, request_sha256 TEXT NOT NULL,
 status TEXT NOT NULL, charge INTEGER NOT NULL, reservation INTEGER NOT NULL, usage_json TEXT
);
CREATE TABLE IF NOT EXISTS checkpoint_claims (
 parent_phase_sha256 TEXT PRIMARY KEY, approval_id TEXT UNIQUE NOT NULL REFERENCES phases
);
CREATE TABLE IF NOT EXISTS study_jobs (
 study_id TEXT NOT NULL, condition TEXT NOT NULL, conversation_id TEXT NOT NULL,
 approval_id TEXT UNIQUE NOT NULL REFERENCES phases, complete INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(study_id,condition,conversation_id)
);
'''


def validate_approval(auth, binding):
    """Validate explicit approval without claiming its one-shot ledger session."""
    _validate(auth, binding)


class PhasePermit:
    def __init__(self, auth, ledger_path, binding):
        cap, reserve, self.input_rate, self.output_rate = _validate(auth, binding)
        self.auth = json.loads(_canonical(auth))
        self.binding = json.loads(_canonical(binding))
        self.path = Path(ledger_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.approval_id = auth['approval_id']
        self.owner = uuid.uuid4().hex
        self.pid = os.getpid()
        self.reserve_micros = reserve
        self._terminal_reason = None
        self._halt_persistence_error = None
        with self._transaction(initialize=True) as db:
            if 'study_job' in binding:
                job = binding['study_job']
                for prior_id,raw in db.execute('SELECT approval_id,auth_json FROM phases'):
                    prior=json.loads(raw)
                    if prior.get('phase')!='baseline': continue
                    claim=db.execute('SELECT study_id,condition,conversation_id FROM study_jobs WHERE approval_id=?',(prior_id,)).fetchone()
                    prior_job=prior['binding'].get('study_job',{})
                    if claim!=(prior_job.get('study_id'),prior['binding'].get('condition'),prior_job.get('conversation_id')):
                        raise BudgetStop('Study cell claim/history is missing or changed')
                historical = db.execute('SELECT COALESCE(SUM(charge),0) FROM attempts').fetchone()[0]
                if historical < job['initial_study_microusd']:
                    raise BudgetStop('Shared ledger lost historical study spending')
                if db.execute('SELECT 1 FROM study_jobs j JOIN phases p ON p.approval_id=j.approval_id WHERE j.study_id=? AND (j.complete=0 OR p.halted IS NOT NULL)', (job['study_id'],)).fetchone():
                    raise BudgetStop('A study job is unfinished; paid recovery requires separate approval')
                if binding['condition']!='full':
                    full={row[0] for row in db.execute('SELECT conversation_id FROM study_jobs WHERE study_id=? AND condition=? AND complete=1',
                                                      (job['study_id'],'full'))}
                    if not {'conv-49','conv-44'}<=full:
                        raise BudgetStop('Complete the original full-mode study jobs before ablations')
                if db.execute('SELECT 1 FROM study_jobs WHERE study_id=? AND condition=? AND conversation_id=?',
                              (job['study_id'],binding['condition'],job['conversation_id'])).fetchone():
                    raise BudgetStop('Study job already claimed; repeated builds require separate approval')
            if db.execute('SELECT 1 FROM phases WHERE approval_id=? OR run_id=?',
                          (self.approval_id, auth['run_id'])).fetchone():
                raise BudgetStop('Phase already claimed; paid recovery requires a new explicit approval')
            db.execute('INSERT INTO phases VALUES (?,?,?,?,?,NULL)',
                       (self.approval_id, auth['run_id'], _canonical(auth), self.owner, cap))
            if 'study_job' in binding:
                db.execute('INSERT INTO study_jobs(study_id,condition,conversation_id,approval_id) VALUES (?,?,?,?)',
                           (job['study_id'],binding['condition'],job['conversation_id'],self.approval_id))
            if 'checkpoint' in binding:
                parent = binding['checkpoint']['parent_phase_sha256']
                if db.execute('SELECT 1 FROM checkpoint_claims WHERE parent_phase_sha256=?', (parent,)).fetchone():
                    raise BudgetStop('Checkpoint already claimed; another recovery requires review')
                db.execute('INSERT INTO checkpoint_claims VALUES (?,?)', (parent, self.approval_id))

    def complete_study_job(self, receipt, publish=None):
        """Hold the serial SQL frontier through verified final-receipt publication."""
        if 'study_job' not in self.binding:
            return
        with self._transaction() as db:
            self._phase(db)
            if (receipt.get('binding') != self.binding or receipt.get('run_id') != self.auth['run_id']
                    or receipt.get('usable_for_next_phase') is not True
                    or receipt.get('status') not in ('complete','degraded')
                    or receipt.get('budget',{}).get('unknown_attempts') != 0
                    or receipt.get('budget',{}).get('logical_calls') != self.auth['limits']['max_logical_calls']):
                self._halt(db,'Incomplete study receipt cannot release the next paid job')
            turns,questions={'conv-49':(509,196),'conv-50':(568,204),'conv-44':(675,158)}[self.binding['study_job']['conversation_id']]
            stages=dict(db.execute('SELECT stage,COUNT(*) FROM logical_calls WHERE approval_id=? GROUP BY stage',(self.approval_id,)))
            expected={'metadata':turns,'shared_decision':turns,'query_keywords':questions,'answer':questions}
            missing=db.execute('SELECT COUNT(*) FROM logical_calls l WHERE l.approval_id=? AND NOT EXISTS (SELECT 1 FROM attempts a WHERE a.logical_id=l.id)',(self.approval_id,)).fetchone()[0]
            unknown=db.execute("SELECT COUNT(*) FROM attempts WHERE approval_id=? AND status!='settled'",(self.approval_id,)).fetchone()[0]
            if stages!=expected or missing or unknown:
                self._halt(db,'Actual ledger does not contain a complete settled study workload')
            cost,attempts=db.execute('SELECT SUM(charge),COUNT(*) FROM attempts WHERE approval_id=?',(self.approval_id,)).fetchone()
            if (receipt['budget'].get('charged_or_reserved_microusd')!=cost
                    or receipt['budget'].get('physical_attempts')!=attempts):
                self._halt(db,'Study receipt costs/attempts differ from the actual ledger')
            if not callable(publish):
                self._halt(db,'Study completion requires final receipt publication')
            # Keep BEGIN IMMEDIATE held: no next-cell claim may observe complete=1
            # until publication succeeds and this transaction commits.
            publish()
            path=self.path.parent/'runs'/self.auth['run_id']/'phase.json'
            try:
                published=json.loads(path.read_text())
                matched=_canonical(published)==_canonical(receipt)
            except (OSError,ValueError,TypeError):
                matched=False
            if not matched:
                self._halt(db,'Published study receipt does not match the verified workload')
            updated=db.execute('UPDATE study_jobs SET complete=1 WHERE approval_id=?', (self.approval_id,))
            if updated.rowcount!=1:
                self._halt(db,'Study cell claim missing at completion')

    @contextmanager
    def _transaction(self, initialize=False):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('PRAGMA synchronous=FULL')
            if initialize:
                db.executescript(SCHEMA)
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def _phase(self, db, allow_halted=False):
        if self._terminal_reason and not allow_halted:
            raise BudgetStop(f'Phase stopped: {self._terminal_reason}')
        row = db.execute('SELECT owner,phase_cap,halted,auth_json FROM phases WHERE approval_id=?',
                         (self.approval_id,)).fetchone()
        if row is None:
            raise BudgetStop('Phase session or immutable approval mismatch')
        try:
            unchanged = row[3] == _canonical(self.auth) and self.binding == self.auth['binding']
        except (TypeError,ValueError,KeyError):
            unchanged = False
        if os.getpid()!=self.pid or row[0]!=self.owner or not unchanged:
            self._halt(db,'Phase session or immutable approval mismatch')
        if row[2] and not allow_halted:
            raise BudgetStop(f'Phase stopped: {row[2]}')
        if not allow_halted and 'study_job' in self.binding:
            other=db.execute('''SELECT 1 FROM study_jobs j JOIN phases p ON p.approval_id=j.approval_id
                WHERE j.study_id=? AND j.approval_id!=? AND (j.complete=0 OR p.halted IS NOT NULL)''',
                (self.binding['study_job']['study_id'],self.approval_id)).fetchone()
            if other:
                self._halt(db,'Another study cell is unfinished or failed; no paid continuation')
        return row

    def _halt(self, db, reason):
        db.execute('UPDATE phases SET halted=COALESCE(halted,?) WHERE approval_id=?',
                   (reason,self.approval_id))
        db.commit()  # Stop survives the escaping BaseException and process restart.
        raise BudgetStop(reason)

    def check_binding(self, binding):
        with self._transaction() as db:
            self._phase(db)
            if binding != self.binding:
                self._halt(db,'Execution binding mismatch')

    def start_logical(self, stage):
        with self._transaction() as db:
            self._phase(db)
            if stage not in STAGES:
                self._halt(db,'Unknown generation stage')
            count = db.execute('SELECT COUNT(*) FROM logical_calls WHERE approval_id=?',
                               (self.approval_id,)).fetchone()[0]
            if count >= self.auth['limits']['max_logical_calls']:
                self._halt(db,'Logical request ceiling reached')
            return db.execute('INSERT INTO logical_calls(approval_id,stage) VALUES (?,?)',
                              (self.approval_id,stage)).lastrowid

    def reserve_attempt(self, logical_id, request):
        with self._transaction() as db:
            phase = self._phase(db)
            logical = db.execute('SELECT stage FROM logical_calls WHERE id=? AND approval_id=?',
                                 (logical_id,self.approval_id)).fetchone()
            if logical is None:
                self._halt(db,'Logical request belongs to another phase')
            output_limit = self.binding['max_output_tokens_by_stage'][logical[0]]
            expected_temp = (.5,.7) if logical[0]=='answer' else (.7,)
            if (not isinstance(request,dict) or request.get('model') != self.binding['model'] or request.get('endpoint') != self.binding['endpoint']
                or type(request.get('max_tokens')) is not int or request['max_tokens'] != output_limit
                or request.get('stream') is not False or request.get('temperature') not in expected_temp
                or request.get('provider_contract_policy', STRICT_PROVIDER_POLICY) != self.binding.get('provider_contract_policy', STRICT_PROVIDER_POLICY)
                or request.get('thinking') not in ('disabled', {'type':'disabled'})):
                self._halt(db,'Physical request differs from the frozen contract')
            try:
                request_hash = fingerprint(request)
            except (ValueError,TypeError):
                self._halt(db,'Request contains unsupported or credential-bearing metadata')
            count = db.execute('SELECT COUNT(*) FROM attempts WHERE approval_id=?',
                               (self.approval_id,)).fetchone()[0]
            original = db.execute('SELECT request_sha256 FROM attempts WHERE logical_id=? ORDER BY id LIMIT 1',
                                  (logical_id,)).fetchone()
            if original is not None and original[0] != request_hash:
                self._halt(db,'Transport retry changed the logical request')
            per_call = db.execute('SELECT COUNT(*) FROM attempts WHERE logical_id=?',(logical_id,)).fetchone()[0]
            if count >= self.auth['limits']['max_attempts'] or per_call >= 3:
                self._halt(db,'Physical attempt ceiling reached')
            total = db.execute('SELECT COALESCE(SUM(charge),0) FROM attempts').fetchone()[0]
            phase_total = db.execute('SELECT COALESCE(SUM(charge),0) FROM attempts WHERE approval_id=?',
                                     (self.approval_id,)).fetchone()[0]
            reservation = int((self.auth['pricing']['max_context_tokens']*self.input_rate
                               +output_limit*self.output_rate).to_integral_value(rounding=ROUND_CEILING))
            if total+reservation > GLOBAL_USABLE_MICROS or phase_total+reservation > phase[1]:
                self._halt(db,'Conservative reservation would exceed phase or study ceiling')
            return db.execute('INSERT INTO attempts(logical_id,approval_id,request_sha256,status,charge,reservation) VALUES (?,?,?,?,?,?)',
                              (logical_id,self.approval_id,request_hash,'reserved',reservation,reservation)).lastrowid

    def settle(self, attempt_id, usage):
        try:
            self._settle(attempt_id, usage)
        except Exception as error:
            # The transaction rolled back; retain the pre-send reservation.
            # Accounting errors must never become SDK connection retries.
            try:
                self.stop('usage_settlement_failed')
            except BudgetStop:
                pass  # stop() has latched locally even if SQLite remains unavailable.
            raise BudgetStop('Usage settlement failed; reservation retained') from error

    def _settle(self, attempt_id, usage):
        with self._transaction() as db:
            self._phase(db,allow_halted=True)
            row = db.execute('SELECT a.status,a.reservation,a.usage_json,l.stage FROM attempts AS a '
                             'JOIN logical_calls AS l ON l.id=a.logical_id '
                             'WHERE a.id=? AND a.approval_id=?',
                             (attempt_id,self.approval_id)).fetchone()
            if row is None:
                self._halt(db,'Unknown physical attempt')
            if row[0]!='reserved':
                try:
                    encoded = _canonical(usage)
                except (ValueError,TypeError):
                    self._halt(db,'Untrusted duplicate attempt settlement')
                if row[2] == encoded:
                    return  # Identical settlement is idempotent, never a second charge.
                self._halt(db,'Conflicting attempt settlement')
            cost = row[1]
            status = 'unknown'
            valid = usage is None
            if isinstance(usage,dict):
                inp,out=usage.get('prompt_tokens'),usage.get('completion_tokens')
                output_limit = self.binding['max_output_tokens_by_stage'][row[3]]
                valid = (type(inp) is int and type(out) is int and 0<=inp<=self.auth['pricing']['max_context_tokens'] and 0<=out<=output_limit)
                if 'total_tokens' in usage:
                    total = usage['total_tokens']
                    valid = valid and type(total) is int and total == inp+out
                # Cache counters describe subsets of prompt_tokens. They never
                # add tokens or obtain a cache discount in this upper estimate.
                hit,miss = usage.get('prompt_cache_hit_tokens'),usage.get('prompt_cache_miss_tokens')
                for count in (hit,miss):
                    if count is not None:
                        valid = valid and type(count) is int and 0<=count<=inp
                if hit is not None and miss is not None:
                    valid = valid and hit+miss == inp
                details = usage.get('prompt_tokens_details')
                if details is not None:
                    valid = valid and isinstance(details,dict)
                    cached = details.get('cached_tokens') if isinstance(details,dict) else None
                    if cached is not None:
                        valid = valid and type(cached) is int and 0<=cached<=inp
                if valid:
                    cost=int((inp*self.input_rate+out*self.output_rate).to_integral_value(rounding=ROUND_CEILING))
                    valid=cost<=row[1]
                    status='settled' if valid else 'unknown'
            try:
                encoded = _canonical(usage)
            except (ValueError,TypeError):
                encoded = None
                valid = False
            db.execute('UPDATE attempts SET status=?,charge=?,usage_json=? WHERE id=?',
                       (status,cost if valid else row[1],encoded,attempt_id))
            if not valid:
                self._halt(db,'Untrusted usage; maximum reservation retained')

    def stop(self, reason):
        # Reasons are categories supplied by orchestration, not raw provider error text.
        self._terminal_reason = self._terminal_reason or str(reason)
        try:
            with self._transaction() as db:
                self._phase(db,allow_halted=True)
                db.execute('UPDATE phases SET halted=COALESCE(halted,?) WHERE approval_id=?',
                           (self._terminal_reason,self.approval_id))
            self._halt_persistence_error = None
        except Exception as error:
            self._halt_persistence_error = type(error).__name__
            raise BudgetStop('Phase stopped locally; halt persistence failed') from error

    def summary(self):
        result = ledger_summary(self.path,self.approval_id)
        if self._terminal_reason:
            result['halt_persisted'] = result['halted'] is not None
            result['halted'] = result['halted'] or self._terminal_reason
            if self._halt_persistence_error:
                result['halt_persistence_error_type'] = self._halt_persistence_error
        return result


def ledger_summary(path, approval_id=None):
    path=Path(path)
    if not path.exists():
        return {'charged_or_reserved_microusd':0,'charged_or_reserved_usd':'0.000000',
                'physical_attempts':0,'logical_calls':0,'unknown_attempts':0,
                'cost_basis':'conservative-approved-peak-bound-not-invoice'}
    db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        suffix=' WHERE approval_id=?' if approval_id else ''
        params=(approval_id,) if approval_id else ()
        charge,count,unknown=db.execute("SELECT COALESCE(SUM(charge),0),COUNT(*),COALESCE(SUM(status != 'settled'),0) FROM attempts"+suffix,params).fetchone()
        logical=db.execute('SELECT COUNT(*) FROM logical_calls'+suffix,params).fetchone()[0]
        result={'charged_or_reserved_microusd':charge,'charged_or_reserved_usd':str(Decimal(charge)/MICROS),
                'physical_attempts':count,'logical_calls':logical,'unknown_attempts':unknown,
                'cost_basis':'conservative-approved-peak-bound-not-invoice'}
        if approval_id:
            phase=db.execute('SELECT halted,phase_cap FROM phases WHERE approval_id=?',(approval_id,)).fetchone()
            result.update(halted=phase[0],phase_cap_microusd=phase[1])
        return result
    finally:
        db.close()
