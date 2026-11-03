"""The fixed twelve-cell Run2 campaign; old experiments and their ledger are read-only.

Reuse the author runner and reviewed transmission/settlement controls. Continuations
are new immutable phases of one cell, never fresh cell allowances or semantic retries.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import traceback
import uuid

from .budget import BudgetStop, PhasePermit, _canonical, ledger_summary
from .config import (RUN2_CONFIG, INDEX_STRING_POLICY, fingerprint, load_run2_config,
                     source_fingerprint, reject_credentials, stage_output_limits)
from .phases import _save

CAMPAIGN_ID = 'amem-run2-20261103-v1'
RECOVERY_POLICY = 'run2-blk013-exact-state-v1'
CONVERSATIONS = {'conv-49': (509, 196), 'conv-50': (568, 204), 'conv-44': (675, 158)}
CELL_ORDER = [('full', c) for c in ('conv-44', 'conv-49', 'conv-50')] + [
    (condition, c) for condition in ('neither', 'linking_only', 'evolution_only')
    for c in ('conv-49', 'conv-50', 'conv-44')]
PRICING = {'input_per_million': .3, 'output_per_million': 1.2,
           'max_context_tokens': 1048576, 'max_output_tokens': 8192,
           'pricing_id': 'deepseek-flash-peak-2026-11-03-run2',
           'source': 'https://api-docs.deepseek.com/quick_start/pricing/'}
MODEL_FINGERPRINT = 'bc19ba97cbe016479903222bb1578db6'
SCHEMA = '''
CREATE TABLE IF NOT EXISTS run2_campaign (singleton INTEGER PRIMARY KEY CHECK(singleton=1), auth_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS run2_cells (cell_index INTEGER PRIMARY KEY, root_approval TEXT NOT NULL UNIQUE,
 leaf_approval TEXT NOT NULL UNIQUE, complete INTEGER NOT NULL DEFAULT 0 CHECK(complete IN (0,1)));
CREATE TABLE IF NOT EXISTS run2_phases (approval_id TEXT PRIMARY KEY REFERENCES phases(approval_id),
 cell_index INTEGER NOT NULL REFERENCES run2_cells(cell_index), phase_index INTEGER NOT NULL,
 parent_approval TEXT UNIQUE, parent_receipt_sha256 TEXT UNIQUE, UNIQUE(cell_index,phase_index));
'''


def _read(path):
    return json.loads(Path(path).read_text())


def _digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _approved(value):
    reject_credentials(value)
    fingerprint(value)
    if value.get('approved') is not True:
        raise BudgetStop('Explicit immutable Run2 approval is required')
    for key in ('approval_id', 'approved_by'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise BudgetStop('Run2 approval identity is missing')
    try:
        approved_at = datetime.fromisoformat(value['approved_at'].replace('Z', '+00:00'))
    except (KeyError, TypeError, ValueError):
        raise BudgetStop('Run2 approval time is invalid') from None
    if approved_at.tzinfo is None:
        raise BudgetStop('Run2 approval time needs a timezone')


def _validate_campaign(campaign, *, require_approved=True):
    if require_approved:
        _approved(campaign)
    reject_credentials(campaign)
    expected = [{'condition': c, 'conversation_id': v, 'turns': CONVERSATIONS[v][0],
                 'questions': CONVERSATIONS[v][1]} for c, v in CELL_ORDER]
    if (campaign.get('campaign_id') != CAMPAIGN_ID or campaign.get('cells') != expected
            or campaign.get('limits') != {'campaign_usd': '42', 'cell_usd': '5',
                                        'max_logical_calls': 18480, 'max_attempts': 55440}
            or campaign.get('pricing') != PRICING
            or campaign.get('binding', {}).get('config_sha256') != fingerprint(RUN2_CONFIG)):
        raise BudgetStop('Campaign differs from the fixed Run2 protocol or budget')
    for key in ('config_sha256', 'source_sha256', 'manifest_sha256', 'preflight_sha256',
                'gate_a_sha256', 'gate_b_sha256', 'run1_preservation_sha256'):
        if not _digest(campaign['binding'].get(key)):
            raise BudgetStop('Campaign provenance is incomplete')
    costs = campaign.get('initial_stage_costs', {})
    if (set(costs) != {'metadata','shared_decision','query_keywords','answer'}
            or any(type(row.get('calls')) is not int or row['calls'] <= 0
                   or type(row.get('cost_microusd')) is not int or row['cost_microusd'] <= 0
                   for row in costs.values())):
        raise BudgetStop('Run2 cost-only stage basis is incomplete')


def _binding(campaign, cell_index):
    condition, conversation = CELL_ORDER[cell_index]
    turns, questions = CONVERSATIONS[conversation]
    return {**copy.deepcopy(campaign['binding']), 'campaign_id': CAMPAIGN_ID,
            'campaign_sha256': fingerprint(campaign), 'cell_index': cell_index,
            'condition': condition, 'conversation_ids': [conversation], 'repetition': 0,
            'population': 'fallback', 'expected_turns': turns, 'expected_questions': questions,
            'model': 'deepseek-flash', 'endpoint': 'https://api.deepseek.com/beta/chat/completions',
            'provider_contract_policy': INDEX_STRING_POLICY,
            'memory_actions': dict(RUN2_CONFIG['conditions'][condition]),
            'action_policy': 'released-action-boundaries-v1',
            'action_implementation': 'frozen-author' if condition == 'full' else 't7-action-gates',
            'max_output_tokens_by_stage': stage_output_limits(RUN2_CONFIG),
            'expected_returned_model': 'deepseek-flash',
            'expected_system_fingerprint': MODEL_FINGERPRINT}


def _validate_phase(approval, campaign):
    _approved(approval)
    _validate_campaign(campaign)
    b = approval.get('binding', {})
    index = b.get('cell_index')
    if type(index) is not int or not 0 <= index < len(CELL_ORDER):
        raise BudgetStop('Unknown Run2 cell')
    expected = _binding(campaign, index)
    checkpoint = b.get('checkpoint')
    if checkpoint is not None:
        expected['checkpoint'] = checkpoint
        if (checkpoint.get('campaign_id') != CAMPAIGN_ID
                or checkpoint.get('policy') != RECOVERY_POLICY
                or checkpoint.get('condition') != expected['condition']
                or checkpoint.get('conversation_id') != expected['conversation_ids'][0]
                or not _digest(checkpoint.get('parent_receipt_sha256'))
                or type(checkpoint.get('completed_turns')) is not int
                or not 0 < checkpoint['completed_turns'] <= expected['expected_turns']):
            raise BudgetStop('Run2 checkpoint identity differs')
    completed = checkpoint['completed_turns'] if checkpoint else 0
    logical = 2 * (expected['expected_turns'] - completed + expected['expected_questions'])
    limits = approval.get('limits', {})
    try:
        cap = Decimal(str(limits['phase_usd']))
    except (KeyError, ValueError, InvalidOperation):
        raise BudgetStop('Run2 phase cap is invalid') from None
    phase_index = approval.get('phase_index')
    name = f"run2-{expected['condition']}-{expected['conversation_ids'][0]}-r0-p{phase_index}"
    if (approval.get('phase') != 'run2' or b != expected or approval.get('pricing') != PRICING
            or not cap.is_finite() or not 0 < cap <= 5
            or type(phase_index) is not int or not 0 <= phase_index <= expected['expected_turns']
            or approval.get('run_id') != name
            or limits.get('max_logical_calls') != logical
            or type(limits.get('max_attempts')) is not int
            or not logical <= limits['max_attempts'] <= 3 * logical):
        raise BudgetStop('Phase differs from the frozen Run2 request/allocation contract')
    return int((cap * 1000000).to_integral_value(rounding=ROUND_FLOOR))


def _cell_totals(db, index):
    ids = [r[0] for r in db.execute('SELECT approval_id FROM run2_phases WHERE cell_index=?', (index,))]
    if not ids:
        return {'logical_calls': 0, 'physical_attempts': 0, 'charged_or_reserved_microusd': 0, 'unknown_attempts': 0}
    marks = ','.join('?' for _ in ids)
    calls = db.execute(f'SELECT COUNT(*) FROM logical_calls WHERE approval_id IN ({marks})', ids).fetchone()[0]
    count, cost, unknown = db.execute(f"SELECT COUNT(*),COALESCE(SUM(charge),0),COALESCE(SUM(status!='settled'),0) FROM attempts WHERE approval_id IN ({marks})", ids).fetchone()
    return {'logical_calls': calls, 'physical_attempts': count,
            'charged_or_reserved_microusd': cost, 'unknown_attempts': unknown}


def _cell_history(db, index, campaign):
    cell = db.execute('SELECT root_approval,leaf_approval,complete FROM run2_cells WHERE cell_index=?', (index,)).fetchone()
    rows = db.execute('SELECT approval_id,phase_index,parent_approval,parent_receipt_sha256 FROM run2_phases WHERE cell_index=? ORDER BY phase_index', (index,)).fetchall()
    if cell is None or not rows or cell[:2] != (rows[0][0], rows[-1][0]):
        raise BudgetStop('Run2 cell ownership/history is missing')
    for n, (ident, seq, parent, digest) in enumerate(rows):
        stored = db.execute('SELECT auth_json,halted FROM phases WHERE approval_id=?', (ident,)).fetchone()
        if stored is None:
            raise BudgetStop('Run2 phase accounting is missing')
        auth = json.loads(stored[0]);_validate_phase(auth, campaign)
        cp = auth['binding'].get('checkpoint')
        if seq != n or auth['phase_index'] != seq:
            raise BudgetStop('Run2 recovery sequence differs')
        if n == 0:
            if parent is not None or cp is not None or digest is not None:
                raise BudgetStop('Run2 root has an unexpected parent')
        else:
            if (parent != rows[n-1][0] or cp is None or cp['parent_approval_id'] != parent
                    or cp['parent_receipt_sha256'] != digest
                    or db.execute('SELECT approval_id FROM checkpoint_claims WHERE parent_phase_sha256=?', (digest,)).fetchone() != (ident,)):
                raise BudgetStop('Run2 recovery edge/claim differs')
        if n < len(rows)-1 and not stored[1]:
            raise BudgetStop('A Run2 ancestor is not durably halted')
        if n < len(rows)-1 or cell[2]:
            ledger_path = Path(db.execute('PRAGMA database_list').fetchone()[2])
            archive = ledger_path.parent/'runs'/auth['run_id']
            try:
                old = _read(archive/'phase.json')
                original = _read(archive/'approval.json')
                cost, attempts, unknown = db.execute("SELECT COALESCE(SUM(charge),0),COUNT(*),COALESCE(SUM(status!='settled'),0) FROM attempts WHERE approval_id=?", (ident,)).fetchone()
                logical = db.execute('SELECT COUNT(*) FROM logical_calls WHERE approval_id=?',(ident,)).fetchone()[0]
                if (_canonical(original) != stored[0] or old['binding'] != auth['binding']
                        or old['budget']['charged_or_reserved_microusd'] != cost
                        or old['budget']['physical_attempts'] != attempts
                        or old['budget']['logical_calls'] != logical
                        or old['budget']['unknown_attempts'] != unknown):
                    raise ValueError('Archived accounting mismatch')
                if cell[2] and n==len(rows)-1 and (
                        stored[1] is not None or old.get('status') not in ('complete','degraded')
                        or old.get('usable_for_next_phase') is not True
                        or old.get('completed_questions') != CONVERSATIONS[auth['binding']['conversation_ids'][0]][1]
                        or old.get('observability',{}).get('verified') is not True
                        or old.get('experiments',{}).get('verified') is not True):
                    raise ValueError('Completed frontier is halted or unconfirmed')
            except (OSError,KeyError,ValueError,TypeError):
                raise BudgetStop('Run2 historical archive/ledger accounting differs') from None
    ids = {r[0] for r in rows}
    touching = db.execute('SELECT approval_id,parent_approval FROM run2_phases WHERE parent_approval IS NOT NULL').fetchall()
    expected_edges = {(rows[i][0], rows[i-1][0]) for i in range(1, len(rows))}
    if {(a,p) for a,p in touching if a in ids or p in ids} != expected_edges:
        raise BudgetStop('Run2 recovery has an extra/missing ownership edge')
    return cell, rows


class Run2Permit(PhasePermit):
    """One phase session using the reviewed transport guard and one shared cell allowance."""
    def __init__(self, approval, root, campaign):
        root = Path(root).resolve()
        self.path = root / 'artifacts/run2/budget.sqlite'
        self.root = root
        self._check_storage_scope()
        self.campaign = copy.deepcopy(campaign)
        cap = _validate_phase(approval, campaign)
        if not self.path.exists() and any((self.path.parent/'runs').glob('*/approval.json')):
            raise BudgetStop('Run2 ledger is missing while historical phases exist')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.auth = json.loads(_canonical(approval));self.binding = copy.deepcopy(approval['binding'])
        self.approval_id = approval['approval_id'];self.owner = uuid.uuid4().hex;self.pid = os.getpid()
        self.reserve_micros = 324404;self.input_rate = Decimal('.3');self.output_rate = Decimal('1.2')
        self._terminal_reason = None;self._halt_persistence_error = None
        with self._transaction(initialize=True) as db:
            # Only this fresh campaign may inhabit the ledger. Never import Run1.
            db.executescript(SCHEMA)
            db.execute('BEGIN IMMEDIATE')
            stored = db.execute('SELECT auth_json FROM run2_campaign WHERE singleton=1').fetchone()
            if stored is None:
                if db.execute('SELECT COUNT(*) FROM phases').fetchone()[0] or db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]:
                    raise BudgetStop('Run2 cannot adopt a populated foreign ledger')
                db.execute('INSERT INTO run2_campaign VALUES (1,?)', (_canonical(campaign),))
            elif stored[0] != _canonical(campaign):
                raise BudgetStop('Run2 campaign approval changed')
            if db.execute('SELECT COUNT(*) FROM phases').fetchone()[0] != db.execute('SELECT COUNT(*) FROM run2_phases').fetchone()[0]:
                raise BudgetStop('Run2 ledger has unregistered/lost phase history')
            if db.execute("SELECT 1 FROM attempts WHERE status!='settled' LIMIT 1").fetchone():
                raise BudgetStop('Run2 has unknown or interrupted charges; continuation prohibited')
            for index, in db.execute('SELECT cell_index FROM run2_cells'):
                _cell_history(db, index, campaign)
            if db.execute('SELECT 1 FROM phases WHERE approval_id=? OR run_id=?',
                          (self.approval_id,self.auth['run_id'])).fetchone():
                raise BudgetStop('Run2 approval was already consumed')
            index = self.binding['cell_index'];cp = self.binding.get('checkpoint')
            prior = _cell_totals(db, index)
            remaining = 5000000 - prior['charged_or_reserved_microusd']
            if cap != remaining:
                raise BudgetStop('Phase allocation does not equal the original cell remainder')
            if self.auth['limits']['max_attempts'] != 3 * self.auth['limits']['max_logical_calls']:
                raise BudgetStop('Run2 attempt quota was reset or changed')
            if cp:
                cell, rows = _cell_history(db, index, campaign)
                parent = cp['parent_approval_id']
                path, archived = _read_phase_archive(self.path.parent/'runs'/cp['parent_run_id']/'phase.json', self.root)
                if (fingerprint(archived) != cp['parent_receipt_sha256']
                        or archived.get('observability',{}).get('verified') is not True
                        or archived.get('recoverable_length_failure') is not True):
                    raise BudgetStop('Run2 checkpoint parent receipt is unverified or changed')
                start = _read_lines(path.parent/'events.jsonl')[0]
                checked = verify_checkpoint(path, root=self.root, campaign=campaign,
                                            manifest=start['manifest'], sources=start['source_hashes'],
                                            receipt=_read(path.parent/'preflight.json'))
                if checked['lineage'] != cp:
                    raise BudgetStop('Run2 checkpoint binding differs from verified exact state')
                if (cell[2] or cell[1] != parent or self.auth['phase_index'] != len(rows)
                        or not db.execute('SELECT halted FROM phases WHERE approval_id=?', (parent,)).fetchone()[0]
                        or prior['logical_calls'] != 2 * cp['completed_turns']
                        or db.execute('SELECT 1 FROM checkpoint_claims WHERE parent_phase_sha256=?', (cp['parent_receipt_sha256'],)).fetchone()):
                    raise BudgetStop('Run2 checkpoint is forked, consumed or inconsistent')
            else:
                expected_index = db.execute('SELECT COUNT(*) FROM run2_cells WHERE complete=1').fetchone()[0]
                if (index != expected_index or self.auth['phase_index'] != 0
                        or db.execute('SELECT 1 FROM run2_cells WHERE complete=0').fetchone()
                        or db.execute('SELECT 1 FROM run2_cells WHERE cell_index=?', (index,)).fetchone()):
                    raise BudgetStop('Run2 cells must be fresh, unique and serial in frozen order')
            db.execute('INSERT INTO phases VALUES (?,?,?,?,?,NULL)', (self.approval_id,self.auth['run_id'],_canonical(self.auth),self.owner,cap))
            if cp:
                db.execute('UPDATE run2_cells SET leaf_approval=? WHERE cell_index=?', (self.approval_id,index))
                db.execute('INSERT INTO checkpoint_claims VALUES (?,?)', (cp['parent_receipt_sha256'],self.approval_id))
            else:
                db.execute('INSERT INTO run2_cells VALUES (?,?,?,0)', (index,self.approval_id,self.approval_id))
            db.execute('INSERT INTO run2_phases VALUES (?,?,?,?,?)',
                       (self.approval_id,index,self.auth['phase_index'],cp['parent_approval_id'] if cp else None,
                        cp['parent_receipt_sha256'] if cp else None))

    def _check_storage_scope(self):
        base=self.root/'artifacts/run2'
        if any(path.resolve()!=path for path in (base,base/'runs',base/'cache',self.path)):
            raise BudgetStop('Run2 storage scope must not alias an original/external directory')
        originals=[self.root/'artifacts/study-budget.sqlite']
        preservation=base/'gate-a/run1-preservation.json'
        if preservation.exists():
            originals.extend(self.root/name for name in _read(preservation)['files'] if name.endswith('.sqlite'))
        if self.path.exists() and any(old.exists() and self.path.samefile(old) for old in originals):
            raise BudgetStop('Run2 ledger must not be a hardlink/alias of preserved Run1 spending')

    @contextmanager
    def _transaction(self,initialize=False):
        self._check_storage_scope() # Before SQLite opens, including admission/settlement/restarts.
        with super()._transaction(initialize=initialize) as db:
            yield db

    def _phase(self, db, allow_halted=False):
        row = super()._phase(db, allow_halted)
        if not allow_halted:
            campaign = db.execute('SELECT auth_json FROM run2_campaign WHERE singleton=1').fetchone()
            if campaign is None or campaign[0] != _canonical(self.campaign):
                self._halt(db, 'Run2 campaign ledger changed')
            if (db.execute('SELECT COUNT(*) FROM phases').fetchone()[0]
                    != db.execute('SELECT COUNT(*) FROM run2_phases').fetchone()[0]
                    or db.execute('SELECT 1 FROM run2_cells WHERE complete=0 AND cell_index!=?',
                                  (self.binding['cell_index'],)).fetchone()):
                self._halt(db, 'Run2 serial cell/phase history changed')
            try:
                for prior, in db.execute('SELECT cell_index FROM run2_cells'):
                    prior_cell,_=_cell_history(db,prior,self.campaign)
                    if prior != self.binding['cell_index'] and not prior_cell[2]:
                        raise BudgetStop('Another Run2 cell is unfinished')
                cell, _ = _cell_history(db, self.binding['cell_index'], self.campaign)
            except BudgetStop:
                self._halt(db, 'Run2 cell or completed frontier provenance changed')
            if cell[1] != self.approval_id or cell[2]:
                self._halt(db, 'Run2 phase no longer owns an unfinished cell')
        return row

    def start_logical(self, stage):
        with self._transaction() as db:
            self._phase(db)
            if db.execute("SELECT 1 FROM attempts WHERE status!='settled' LIMIT 1").fetchone():
                self._halt(db, 'Unknown charge prevents another Run2 logical request')
        return super().start_logical(stage)

    def cell_summary(self):
        with self._transaction() as db:
            return _cell_totals(db, self.binding['cell_index'])

    def complete_cell(self, receipt, publish):
        with self._transaction() as db:
            self._phase(db)
            totals = _cell_totals(db, self.binding['cell_index'])
            turns, questions = CONVERSATIONS[self.binding['conversation_ids'][0]]
            ids = [r[0] for r in db.execute('SELECT approval_id FROM run2_phases WHERE cell_index=?', (self.binding['cell_index'],))]
            marks = ','.join('?' for _ in ids)
            stages = dict(db.execute(f'SELECT stage,COUNT(*) FROM logical_calls WHERE approval_id IN ({marks}) GROUP BY stage', ids))
            if (receipt.get('binding') != self.binding or receipt.get('run_id') != self.auth['run_id']
                    or receipt.get('status') not in ('complete','degraded')
                    or receipt.get('completed_questions') != questions or not receipt.get('usable_for_next_phase')
                    or receipt.get('cell_budget') != totals or totals['unknown_attempts']
                    or totals['logical_calls'] != 2 * (turns+questions)
                    or stages != {'metadata':turns,'shared_decision':turns,'query_keywords':questions,'answer':questions}
                    or not receipt.get('observability',{}).get('verified')
                    or not receipt.get('experiments',{}).get('verified') or not callable(publish)):
                self._halt(db, 'Incomplete/unobserved Run2 cell cannot release the frontier')
            _verify_attempt_journal(db,self.binding['cell_index'])
            publish()
            path = self.path.parent/'runs'/self.auth['run_id']/'phase.json'
            try:
                same = _canonical(_read(path)) == _canonical(receipt)
            except (OSError, ValueError):
                same = False
            if not same:
                self._halt(db, 'Run2 final receipt publication failed')
            changed = db.execute('UPDATE run2_cells SET complete=1 WHERE cell_index=? AND leaf_approval=? AND complete=0',
                                 (self.binding['cell_index'],self.approval_id))
            if changed.rowcount != 1:
                self._halt(db, 'Run2 completion ownership changed')


def _runtime_inputs(receipt, asset_root, root):
    from .phases import _verified_receipt
    from .manifests import expand_manifest
    root = Path(root).resolve()
    sources = _verified_receipt(receipt, asset_root, root)
    config = load_run2_config(root/'config/run2.json')
    manifest = expand_manifest(root/'data/locomo10.json', _read(root/'manifests/fallback.json'))
    found = {c['original_id']:(len(c['turn_ids']),len(c['questions'])) for c in manifest['conversations']}
    if found != CONVERSATIONS:
        raise ValueError('Run2 population differs from the frozen three complete conversations')
    return config, manifest, sources


def _validate_gates(gate_a, gate_b, sources):
    policy = RUN2_CONFIG['generation']['output_token_policy']
    if (gate_a.get('passed') is not True or gate_a.get('output_policy') != policy
            or type(gate_a.get('provider_max_output_tokens')) is not int
            or gate_a['provider_max_output_tokens'] < 8192
            or gate_a.get('sdk_serialization_verified') is not True
            or not _digest(gate_a.get('evidence_sha256'))):
        raise ValueError('GateA provider/output policy evidence is missing')
    required = ('passed','real_runner','remote_observations_verified','experiments_verified',
                'replay_equivalence','zero_additional_model_calls','output_exhaustion_verified',
                'tracing_failure_verified')
    if (any(gate_b.get(key) is not True for key in required)
            or gate_b.get('output_policy') != policy
            or gate_b.get('source_sha256') != fingerprint(sources)
            or not _digest(gate_b.get('evidence_sha256'))):
        raise ValueError('GateB actual runner/remote visibility/equivalence evidence is missing or stale')


def plan_campaign(receipt, gate_a, gate_b, *, root, asset_root):
    """Prepare an unapproved campaign; gate booleans bind independently reviewed evidence."""
    root = Path(root).resolve()
    config, manifest, sources = _runtime_inputs(receipt, asset_root, root)
    _validate_gates(gate_a, gate_b, sources)
    preservation = _read(root/'artifacts/run2/gate-a/run1-preservation.json')
    original_ledger = root/'artifacts/study-budget.sqlite'
    if hashlib.sha256(original_ledger.read_bytes()).hexdigest() != preservation['ledger_sha256']:
        raise ValueError('Run1 spending history changed during Run2 preparation')
    campaign = {'campaign_id':CAMPAIGN_ID,'approval_id':str(uuid.uuid4()),'approved':False,
                'approved_by':None,'approved_at':None,
                'cells':[{'condition':c,'conversation_id':v,'turns':CONVERSATIONS[v][0],
                          'questions':CONVERSATIONS[v][1]} for c,v in CELL_ORDER],
                'limits':{'campaign_usd':'42','cell_usd':'5','max_logical_calls':18480,'max_attempts':55440},
                'pricing':copy.deepcopy(PRICING),'initial_stage_costs':_run1_stage_costs(root),
                'binding':{'config_sha256':fingerprint(config),'source_sha256':fingerprint(sources),
                           'manifest_sha256':fingerprint(manifest),'preflight_sha256':fingerprint(receipt),
                           'gate_a_sha256':fingerprint(gate_a),'gate_b_sha256':fingerprint(gate_b),
                           'run1_preservation_sha256':fingerprint(preservation)}}
    _validate_campaign(campaign, require_approved=False)
    return campaign


def _check_campaign_runtime(campaign, receipt, asset_root, root):
    _validate_campaign(campaign)
    config, manifest, sources = _runtime_inputs(receipt, asset_root, root)
    b = campaign['binding']
    if any(b[key] != value for key,value in (
            ('config_sha256',fingerprint(config)),('manifest_sha256',fingerprint(manifest)),
            ('source_sha256',fingerprint(sources)),('preflight_sha256',fingerprint(receipt)))):
        raise ValueError('Run2 frozen source/configuration/preflight changed')
    preservation = _read(Path(root)/'artifacts/run2/gate-a/run1-preservation.json')
    if (fingerprint(preservation) != b['run1_preservation_sha256']
            or hashlib.sha256((Path(root)/'artifacts/study-budget.sqlite').read_bytes()).hexdigest() != preservation['ledger_sha256']):
        raise ValueError('Run1 preservation/ledger evidence changed')
    return config, manifest, sources


def _read_phase_archive(path, root):
    root = Path(root).resolve();path = Path(path).resolve()
    if (path.name != 'phase.json' or not path.is_relative_to(root/'artifacts/run2/runs')
            or path.parent.parent != root/'artifacts/run2/runs'):
        raise ValueError('Checkpoint must be an immutable Run2 phase')
    phase = _read(path)
    if path.parent.name != phase.get('run_id') or phase.get('phase') != 'run2':
        raise ValueError('Run2 archive identity differs')
    required = {'approval.json','preflight.json','events.jsonl','run.json','summary.json','observability.json'}
    if not required.issubset(phase.get('artifact_sha256',{})):
        raise ValueError('Run2 phase inventory is incomplete')
    for name,digest in phase['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path.parent/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Run2 archived evidence changed')
    if phase.get('observability') != _read(path.parent/'observability.json'):
        raise ValueError('Run2 observation receipt differs from its archived copy')
    return path,phase


def verify_checkpoint(path, *, root, campaign, manifest, sources, receipt):
    """Verify every exact-state ancestor, not just a mutable latest snapshot."""
    from .artifacts import _validate_state
    import numpy as np
    root = Path(root).resolve();path,phase = _read_phase_archive(path,root)
    chain=[];seen=set();cursor=path
    while True:
        p,prior = _read_phase_archive(cursor,root)
        if prior['run_id'] in seen or len(chain) > max(t for t,q in CONVERSATIONS.values()):
            raise ValueError('Run2 checkpoint cycle or non-progressing lineage')
        seen.add(prior['run_id']);auth=_read(p.parent/'approval.json');_validate_phase(auth,campaign)
        if (auth['binding'] != prior['binding'] or auth['run_id'] != prior['run_id']
                or prior['status'] != 'incomplete' or prior.get('completed_questions') != 0
                or prior.get('recoverable_length_failure') is not True
                or prior.get('secondary_failures')
                or prior.get('observability',{}).get('verified') is not True
                or prior['budget'].get('unknown_attempts') != 0 or not prior['budget'].get('halted')
                or prior['binding']['source_sha256'] != fingerprint(sources)
                or prior['binding']['preflight_sha256'] != fingerprint(receipt)
                or not _length_failure(p.parent,prior['binding'])):
            raise ValueError('Only verified BLK013 Run2 memory phases may continue')
        if chain and (prior['binding']['condition'],prior['binding']['conversation_ids']) != (phase['binding']['condition'],phase['binding']['conversation_ids']):
            raise ValueError('Run2 checkpoint condition/population differs')
        chain.append((p,prior,auth))
        cp=prior['binding'].get('checkpoint')
        if cp is None:break
        cursor=root/'artifacts/run2/runs'/cp['parent_run_id']/'phase.json'
        if fingerprint(_read(cursor)) != cp['parent_receipt_sha256']:
            raise ValueError('Run2 ancestor receipt changed')
    chain.reverse();b=phase['binding'];conversation=next(c for c in manifest['conversations'] if c['original_id']==b['conversation_ids'][0])
    events=[_read_lines(p.parent/'events.jsonl') for p,_,_ in chain]
    turns=[e for group in events for e in group if e['type']=='evolution_outcome']
    partial=_read(path.parent/'partial-memory.json');identity,state=partial['identity'],partial['state'];_validate_state(state)
    n=len(state['notes']);emb=np.asarray(state['retriever']['embeddings'],dtype=state['retriever']['embedding_dtype'])
    if (partial.get('complete') is not False or not 0 < n <= len(conversation['turn_ids'])
            or [e['turn_id'] for e in turns] != conversation['turn_ids'][:n]
            or len({e['turn_id'] for e in turns}) != n or len(state['outcomes']) != n
            or [o['turn_id'] for o in state['outcomes']] != conversation['turn_ids'][:n]
            or emb.shape != (n,384) or str(emb.dtype) != 'float32' or not np.isfinite(emb).all()
            or state['evo_threshold'] != 100 or state['evo_cnt'] != turns[-1]['counter_after']
            or identity['configuration'] != RUN2_CONFIG or identity['condition'] != b['condition']
            or identity['conversation'] != conversation or identity['source_hashes'] != sources
            or identity['dataset_sha256'] != manifest['dataset_sha256']
            or identity['provider_contract_policy'] != INDEX_STRING_POLICY):
        raise ValueError('Run2 exact checkpoint memory/index/provenance differs')
    for saved,event in zip(state['outcomes'],turns):
        if saved != {key:event[key] for key in saved}:
            raise ValueError('Run2 cached evolution outcomes differ from journal')
    last=turns[-1]
    if (last['proposed_decision'] is not None or last['changed_existing_note_ids']
            or last['counter_after'] != last['counter_before']):
        raise ValueError('Run2 failed evolution did not retain the original fallback')
    with sqlite3.connect((root/'artifacts/run2/budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        cell,rows=_cell_history(db,b['cell_index'],campaign)
        if cell[1] != chain[-1][2]['approval_id'] or cell[2] or len(rows) != len(chain):
            raise ValueError('Run2 latest checkpoint is no longer the exclusive leaf')
        cumulative=0
        for (p,prior,auth),row in zip(chain,rows):
            if row[0] != auth['approval_id'] or db.execute('SELECT auth_json FROM phases WHERE approval_id=?',(row[0],)).fetchone() != (_canonical(auth),):
                raise ValueError('Run2 archive/ledger approval differs')
            if ledger_summary(root/'artifacts/run2/budget.sqlite',auth['approval_id']) != prior['budget']:
                # Permit summary may additionally retain the explicit in-process halt flag.
                actual=ledger_summary(root/'artifacts/run2/budget.sqlite',auth['approval_id'])
                if any(prior['budget'].get(k)!=v for k,v in actual.items()):
                    raise ValueError('Run2 parent spending differs')
            local=[e for e in _read_lines(p.parent/'events.jsonl') if e['type']=='evolution_outcome']
            if not local or prior['budget']['logical_calls'] != 2*len(local):
                raise ValueError('Run2 recovered phase made extra/missing model calls')
            cumulative+=len(local)
        totals=_cell_totals(db,b['cell_index'])
        if cumulative != n or totals['logical_calls'] != 2*n or totals['unknown_attempts']:
            raise ValueError('Run2 checkpoint accounting is incomplete')
        _verify_attempt_journal(db,b['cell_index'])
    lineage={'policy':RECOVERY_POLICY,'campaign_id':CAMPAIGN_ID,'condition':b['condition'],
             'conversation_id':b['conversation_ids'][0],'parent_run_id':phase['run_id'],
             'parent_approval_id':chain[-1][2]['approval_id'],'parent_receipt_sha256':fingerprint(phase),
             'parent_snapshot_sha256':phase['artifact_sha256']['partial-memory.json'],
             'parent_events_sha256':phase['artifact_sha256']['events.jsonl'],'completed_turns':n,
             'remaining_logical_calls':2*(len(conversation['turn_ids'])-n+len(conversation['questions'])),
             'ancestor_receipts':[{'run_id':p0['run_id'],'approval_id':a0['approval_id'],
                                   'receipt_sha256':fingerprint(p0),'approval_sha256':fingerprint(a0)}
                                  for _,p0,a0 in chain]}
    failures=[e for e in events[-1] if e['type']=='failure']
    return {'lineage':lineage,'state':copy.deepcopy(state),'failures':copy.deepcopy(failures)}


def _read_lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def _verify_attempt_journal(db,cell_index):
    """Reject lost charges/calls even when aggregate counters happen to match."""
    ledger=Path(db.execute('PRAGMA database_list').fetchone()[2]);attempts={};logical={}
    ids=[]
    for ident,raw in db.execute('SELECT p.approval_id,f.auth_json FROM run2_phases p JOIN phases f ON f.approval_id=p.approval_id WHERE p.cell_index=? ORDER BY p.phase_index',(cell_index,)):
        ids.append(ident);auth=json.loads(raw)
        for event in _read_lines(ledger.parent/'runs'/auth['run_id']/'events.jsonl'):
            if event.get('type')!='generation' or not event.get('attempts'):continue
            logical_id=event.get('budget_logical_id')
            if logical_id in logical or type(logical_id) is not int:
                raise BudgetStop('Run2 generation journal has duplicate/missing logical IDs')
            logical[logical_id]=(ident,event['stage'])
            for attempt in event['attempts']:
                attempt_id=attempt.get('budget_attempt_id')
                if attempt_id in attempts or type(attempt_id) is not int:
                    raise BudgetStop('Run2 generation journal has duplicate/missing attempt IDs')
                attempts[attempt_id]=(logical_id,attempt.get('usage'))
    marks=','.join('?' for _ in ids)
    actual={i:(a,s) for i,a,s in db.execute(f'SELECT id,approval_id,stage FROM logical_calls WHERE approval_id IN ({marks})',ids)}
    if logical!=actual:raise BudgetStop('Run2 logical journal/accounting differs')
    rows=db.execute(f'SELECT id,logical_id,status,charge,usage_json FROM attempts WHERE approval_id IN ({marks})',ids).fetchall()
    if {r[0] for r in rows}!=set(attempts):raise BudgetStop('Run2 attempt journal/accounting differs')
    for ident,logical_id,status,charge,usage_json in rows:
        expected_logical,usage=attempts[ident]
        if status!='settled' or logical_id!=expected_logical or not isinstance(usage,dict) or json.loads(usage_json)!=usage:
            raise BudgetStop('Run2 attempt usage is missing, changed or unknown')
        calculated=int((Decimal('.3')*usage['prompt_tokens']+Decimal('1.2')*usage['completion_tokens']).to_integral_value(rounding=ROUND_CEILING))
        if charge!=calculated:raise BudgetStop('Run2 actual charge differs from retained provider usage')


def plan_phase(campaign, receipt, asset_root, *, root, condition, conversation_id, parent=None):
    root=Path(root).resolve();config,manifest,sources=_check_campaign_runtime(campaign,receipt,asset_root,root)
    if not forecast_campaign(campaign, root=root)['fits_execution_allocation']:
        raise ValueError('Run2 remaining cost-only forecast exceeds USD42; stop for a budget decision')
    try:index=CELL_ORDER.index((condition,conversation_id))
    except ValueError:raise ValueError('Unknown fixed Run2 cell') from None
    b=_binding(campaign,index);seq=0;prior={'charged_or_reserved_microusd':0,'physical_attempts':0}
    if parent is not None:
        cp=verify_checkpoint(parent,root=root,campaign=campaign,manifest=manifest,sources=sources,receipt=receipt)
        b['checkpoint']=cp['lineage'];seq=len(cp['lineage']['ancestor_receipts'])
        with sqlite3.connect((root/'artifacts/run2/budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
            prior=_cell_totals(db,index)
    remaining=2*(b['expected_turns']-(b.get('checkpoint',{}).get('completed_turns',0))+b['expected_questions'])
    return {'phase':'run2','phase_index':seq,'run_id':f'run2-{condition}-{conversation_id}-r0-p{seq}',
            'approval_id':str(uuid.uuid4()),'approved':False,'approved_by':None,'approved_at':None,
            'binding':b,'pricing':copy.deepcopy(PRICING),
            'limits':{'phase_usd':str(Decimal(5000000-prior['charged_or_reserved_microusd'])/1000000),
                      'max_logical_calls':remaining,'max_attempts':3*remaining}}


def _run1_stage_costs(root):
    """Read only financial evidence; never reuse Run1 predictions or memory caches."""
    names=('pilot-conv50-d9a','pilot-conv50-checkpoint-child','t8-full-conv49-r0-20261102',
           't8-full-conv49-checkpoint-child','t8-full-conv44-r0-20261103',
           't8-full-conv44-checkpoint-child','t8-full-conv44-checkpoint-grandchild')
    ids=[_read(Path(root)/'artifacts/runs'/name/'approval.json')['approval_id'] for name in names]
    with sqlite3.connect((Path(root)/'artifacts/study-budget.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db:
        rows=db.execute('''SELECT l.stage,COUNT(DISTINCT l.id),SUM(a.charge)
            FROM logical_calls l JOIN attempts a ON a.logical_id=l.id
            WHERE l.approval_id IN (?,?,?,?,?,?,?) GROUP BY l.stage''',ids)
        return {stage:{'calls':calls,'cost_microusd':cost} for stage,calls,cost in rows}


def forecast_campaign(campaign, *, root):
    """Point estimate from stage costs only, with remaining partial workload credited once."""
    _validate_campaign(campaign, require_approved=False)
    root=Path(root).resolve();ledger=root/'artifacts/run2/budget.sqlite'
    current=ledger_summary(ledger);base={s:Decimal(v['cost_microusd'])/v['calls'] for s,v in campaign['initial_stage_costs'].items()}
    completed=set();observed={};remaining_counts={};db=None
    try:
        if ledger.exists():
            db=sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
            stored=db.execute('SELECT auth_json FROM run2_campaign WHERE singleton=1').fetchone()
            if stored != (_canonical(campaign),):raise ValueError('Run2 financial history/campaign differs')
            completed={i for i, in db.execute('SELECT cell_index FROM run2_cells WHERE complete=1')}
            for i, in db.execute('SELECT cell_index FROM run2_cells'):_cell_history(db,i,campaign)
            for condition in RUN2_CONFIG['conditions']:
                indices=[i for i in completed if CELL_ORDER[i][0]==condition]
                if indices:
                    marks=','.join('?' for _ in indices)
                    rows=db.execute(f'''SELECT l.stage,COUNT(DISTINCT l.id),SUM(a.charge)
                        FROM logical_calls l JOIN attempts a ON a.logical_id=l.id
                        JOIN run2_phases p ON p.approval_id=l.approval_id
                        WHERE p.cell_index IN ({marks}) GROUP BY l.stage''',indices)
                    observed[condition]={s:Decimal(cost)/count for s,count,cost in rows}
            for i in range(len(CELL_ORDER)):
                remaining_counts[i]=dict(db.execute('''SELECT l.stage,COUNT(*) FROM logical_calls l
                    JOIN run2_phases p ON p.approval_id=l.approval_id WHERE p.cell_index=? GROUP BY l.stage''',(i,)))
        jobs=[]
        for i,(condition,conversation) in enumerate(CELL_ORDER):
            if i in completed:continue
            t,q=CONVERSATIONS[conversation];done=remaining_counts.get(i,{})
            workload={s:n-done.get(s,0) for s,n in {'metadata':t,'shared_decision':t,'query_keywords':q,'answer':q}.items()}
            if any(n<0 for n in workload.values()):raise ValueError('Run2 workload exceeds the frozen cell')
            # Once Run2 Full is measured, its larger-cap costs replace the old
            # exploratory proxy for conditions without their own observation.
            means=observed.get(condition,observed.get('full',base))
            if set(means)!=set(base):raise ValueError('Run2 measured stage coverage is incomplete')
            estimate=int(sum((means[s]*n for s,n in workload.items()),Decimal(0)).to_integral_value(rounding=ROUND_CEILING))
            jobs.append({'cell_index':i,'condition':condition,'conversation_id':conversation,
                         'remaining_logical_calls':sum(workload.values()),'estimated_microusd':estimate})
        remaining=sum(j['estimated_microusd'] for j in jobs);total=current['charged_or_reserved_microusd']+remaining
        return {'campaign_id':CAMPAIGN_ID,'basis':'stage cost means; no quality selection',
                'incurred_or_reserved_microusd':current['charged_or_reserved_microusd'],
                'remaining_estimate_microusd':remaining,'execution_estimate_microusd':total,
                'protected_contingency_microusd':8000000,'total_estimate_microusd':total+8000000,
                'fits_execution_allocation':total<=42000000,'remaining_jobs':jobs,
                'limitation':'Point estimate, not an upper bound; all actual charges remain hard-capped.'}
    finally:
        if db is not None:db.close()


def _length_failure(output, binding):
    """Recognise only a retained shared-decision exhaustion and original failure fallback."""
    try:
        events=_read_lines(Path(output)/'events.jsonl')
        if any(e['type']=='question_result' for e in events):return False
        paid=[e for e in events if e['type']=='generation' and e.get('attempts')]
        bad=[e for e in paid if e.get('error_type')]
        if len(bad)!=1 or bad[0] is not paid[-1] or bad[0]['stage']!='shared_decision':return False
        last=bad[0];choice=last['provider_response']['choices'][0]
        if (last['error_type']!='AdapterError' or choice['finish_reason']!='length'
                or last['usage']['completion_tokens']!=8192 or last['max_tokens']!=8192
                or last.get('returned_model')!='deepseek-flash'
                or last.get('system_fingerprint')!=binding['expected_system_fingerprint']):return False
        raw=choice['message']['tool_calls'][0]['function']['arguments']
        if raw!=last['attempts'][-1]['response_body']['choices'][0]['message']['tool_calls'][0]['function']['arguments']:return False
        from .contracts import load_author_contracts
        contract=load_author_contracts()['shared_decision'];wire=last['attempts'][-1]['request_body']
        if (last['response_format']!=contract or wire.get('max_tokens')!=8192
                or wire.get('temperature')!=.7 or wire.get('thinking')!={'type':'disabled'}
                or wire['tools'][0]['function'].get('strict') is not True
                or wire['tools'][0]['function']['parameters']!=contract['json_schema']['schema']
                or wire['messages'][1]['content']!=last['prompt']):return False
        outcomes=[e for e in events if e['type']=='evolution_outcome']
        if not outcomes:return False
        final=outcomes[-1]
        if final['proposed_decision'] is not None or final['changed_existing_note_ids'] or final['counter_before']!=final['counter_after']:return False
        kinds={e['kind'] for e in events if e['type']=='failure' and not e.get('inherited_from')}
        if kinds-{'provider_contract_deviation','provider_completion','evolve'}:return False
        partial=_read(Path(output)/'partial-memory.json')['state'];note=partial['notes'][-1]['attributes']
        metadata=[e for e in paid if e['stage']=='metadata'][-1]
        original=json.loads(metadata['output'])
        return (note['links']==[] and all(note[k]==original[k] for k in ('context','tags','keywords'))
                and partial['evo_cnt']==final['counter_after'])
    except (KeyError, IndexError, TypeError, ValueError, OSError):
        return False


def execute_phase(approval, campaign, receipt, asset_root, *, root, observer,
                  verify_observations, verify_results, controller_factory=None,
                  factory_builder=None, scorer=None, token_counter=None):
    """Execute one newly approved segment, preserving receipts on every failure.

    The caller loops only after verify_checkpoint succeeds; this function never
    repairs JSON, retries a semantic decision or invents an observability success.
    """
    from .adapter import create_deepseek_controller
    from .author import make_agent_factory
    from .actions import make_action_agent_factory
    from .runner import run_manifest
    from .scoring import AuthorScorer, rescore_records
    from .phases import _asset_environment
    from .preflight import make_token_counter
    root=Path(root).resolve();config,manifest,sources=_check_campaign_runtime(campaign,receipt,asset_root,root)
    _validate_phase(approval,campaign);binding=approval['binding']
    if any(binding.get(k)!=v for k,v in _binding(campaign,binding['cell_index']).items()):
        raise BudgetStop('Run2 phase binding changed')
    output=root/'artifacts/run2/runs'/approval['run_id']
    if output.exists():raise FileExistsError('Run2 phase identity is immutable and single use')
    if not callable(verify_observations) or not callable(verify_results) or observer is None:
        raise ValueError('Run2 requires actual observation/result verification callbacks')
    recovered=None
    if 'checkpoint' in binding:
        recovered=verify_checkpoint(root/'artifacts/run2/runs'/binding['checkpoint']['parent_run_id']/'phase.json',
                                    root=root,campaign=campaign,manifest=manifest,sources=sources,receipt=receipt)
        if recovered['lineage']!=binding['checkpoint']:raise ValueError('Run2 approved checkpoint binding differs')
    if controller_factory is None and not os.environ.get('DEEPSEEK_API_KEY'):
        raise ValueError('DEEPSEEK_API_KEY is required in the environment')
    permit=Run2Permit(approval,root,campaign)
    output.mkdir(parents=True);_save(output/'approval.json',approval);_save(output/'preflight.json',receipt)
    if recovered is not None:_save(output/'checkpoint.json',recovered['lineage'])
    clients=[];summary=None;failure=None;views=None;obs={'verified':False};experiments={'verified':False}
    expected_length_abort=False;secondary_failures=[]
    context={'campaign_id':CAMPAIGN_ID,'run_id':approval['run_id'],'condition':binding['condition'],
             'conversation_id':binding['conversation_ids'][0],'output_dir':str(output),
             'binding':copy.deepcopy(binding)}
    def controller(journal):
        def durable(event):
            try:journal(event)
            except BaseException as err:
                permit.stop('critical_generation_journal_failed')
                _save(output/('generation-journal-failure-'+uuid.uuid4().hex+'.json'),{'error_type':type(err).__name__,'event':event})
                raise BudgetStop('Critical Run2 generation journal failed') from err
        for hook in ('begin_generation','begin_action','begin_retrieval'):
            if hasattr(journal,hook):setattr(durable,hook,getattr(journal,hook))
        c=(controller_factory or create_deepseek_controller)(paid_authorized=True,observer=durable,
                phase_permit=permit,provider_contract_policy=INDEX_STRING_POLICY,generation_config=config)
        clients.append(c.client);return c
    def observe(event):
        observer(event)
        if event.get('type')=='generation' and event.get('attempts'):
            if (event.get('returned_model')!=binding['expected_returned_model']
                    or event.get('system_fingerprint')!=binding['expected_system_fingerprint']
                    or not event.get('usage')):
                permit.stop('provider_model_usage_or_fingerprint_changed')
    for hook in ('begin_generation','begin_action','begin_retrieval'):
        if hasattr(observer,hook):setattr(observe,hook,getattr(observer,hook))
    def boundary():
        try:observer.assert_healthy()
        except Exception as err:
            permit.stop('observability_failed')
            raise BudgetStop('Tracing failed; stop at the next original work boundary') from err
        permit.check_binding(binding)
    try:
        with _asset_environment(asset_root):
            counter=token_counter or make_token_counter(asset_root,receipt['assets'],root/'config/assets.json')
            scorer=scorer or AuthorScorer(root)
            if factory_builder is not None:factory=factory_builder(controller,counter,binding['condition'])
            elif binding['condition']=='full':factory=make_agent_factory(root,controller_factory=controller,token_counter=counter)
            else:factory=make_action_agent_factory(root,condition=binding['condition'],controller_factory=controller,token_counter=counter)
            summary=run_manifest(root/'data/locomo10.json',manifest,config,output_dir=output,
                cache_root=root/'artifacts/run2/cache',source_hashes=sources,agent_factory=factory,
                scorer=scorer,observer=observe,run_id=approval['run_id'],provider_contract_policy=INDEX_STRING_POLICY,
                checkpoint=recovered,execution_type='checkpoint_recovery' if recovered else 'fresh_build',
                condition=binding['condition'],conversation_ids=binding['conversation_ids'],boundary_check=boundary)
            if permit.summary().get('halted') or permit.summary()['unknown_attempts']:
                raise BudgetStop('Run2 phase halted or retained unknown charges')
            predictions=[e['result'] for e in _read_lines(output/'events.jsonl') if e['type']=='question_result']
            original_observer=scorer.observer;scorer.observer=None
            try:views=rescore_records(predictions,scorer)
            finally:scorer.observer=original_observer
            metric_failures=[]
            for policy,view in views.items():
                for row in view['individual_results']:
                    for problem in row.get('metric_failures',[]):
                        notice={**problem,'question_id':row['question_id'],
                                'conversation_id':row['conversation_id'],'scoring_policy':policy,
                                'execution_stage':'rescoring'}
                        original_observer(notice);metric_failures.append(notice)
            if metric_failures:
                from .phases import _replace_summary
                summary['status']='degraded'
                summary['failures']=[e for e in _read_lines(output/'events.jsonl') if e['type']=='failure']
                _replace_summary(output,summary)
            _save(output/'scoring-views.json',views)
    except BaseException as err:
        failure=err
        expected_length_abort=(type(err) is BudgetStop
                               and str(err)=='Phase stopped: provider_contract_or_transport_failure')
        try:permit.stop('run2_phase_aborted')
        except BaseException as halt_error:
            secondary_failures.append({'stage':'phase_halt','error_type':type(halt_error).__name__})
            expected_length_abort=False
    finally:
        for client in clients:
            try:client.close()
            except Exception as close_error:
                secondary_failures.append({'stage':'transport_close','error_type':type(close_error).__name__})
                failure=failure or close_error;expected_length_abort=False
        if summary is None and (output/'summary.json').exists():summary=_read(output/'summary.json')
        try:
            trace_receipt=observer.finish();observer.assert_healthy()
            obs=verify_observations(trace_receipt,context)
            if (obs.get('verified') is not True or not obs.get('trace_ids')
                    or not _digest(obs.get('evidence_sha256'))):raise ValueError('Actual Langfuse visibility was not verified')
        except Exception as err:
            try:permit.stop('run2_observability_not_verified')
            except BaseException as halt_error:
                secondary_failures.append({'stage':'observability_halt','error_type':type(halt_error).__name__})
            failure=failure or err;expected_length_abort=False
            obs={'verified':False,'error_type':type(err).__name__}
        _save(output/'observability.json',obs)
        if failure is None and views is not None:
            try:
                saved_results_sha256=fingerprint(views)
                experiments=verify_results(copy.deepcopy(views),context)
                if (experiments.get('verified') is not True
                        or set(experiments.get('experiment_ids',{}))!=set(RUN2_CONFIG['scoring_policies'])
                        or experiments.get('results_sha256')!=saved_results_sha256
                        or fingerprint(_read(output/'scoring-views.json'))!=saved_results_sha256
                        or not _digest(experiments.get('evidence_sha256'))):
                    raise ValueError('Saved-result Langfuse Experiments were not verified')
            except Exception as err:
                try:permit.stop('run2_experiments_not_verified')
                except BaseException as halt_error:
                    secondary_failures.append({'stage':'experiments_halt','error_type':type(halt_error).__name__})
                failure=err;expected_length_abort=False
                experiments={'verified':False,'error_type':type(err).__name__}
            _save(output/'experiments.json',experiments)
        budget=permit.summary();cell_budget=permit.cell_summary()
        if failure is not None:
            _save(output/'failure-trace.json',{'error_type':type(failure).__name__,
                  'frames':[{'file':f.filename,'line':f.lineno,'function':f.name}
                            for f in traceback.extract_tb(failure.__traceback__)]})
        if failure is not None and summary is not None and summary.get('status')!='incomplete':
            from .phases import _replace_summary
            notice={'type':'run_abort','error_type':type(failure).__name__,'run_id':approval['run_id'],
                    'level':'run','execution_stage':'run2_postprocessing_or_observability'}
            with (output/'events.jsonl').open('a') as stream:
                stream.write(json.dumps(notice,sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
            summary['status']='incomplete';_replace_summary(output,summary)
        recoverable=bool(expected_length_abort and not secondary_failures and obs.get('verified')
                         and budget.get('halt_persisted') is True
                         and budget.get('halted')=='provider_contract_or_transport_failure'
                         and not cell_budget['unknown_attempts']
                         and _length_failure(output,binding))
        events=_read_lines(output/'events.jsonl') if (output/'events.jsonl').exists() else []
        generations=[e for e in events if e['type']=='generation']
        outcomes=[e for e in events if e['type']=='evolution_outcome']
        schema_outcomes={}
        for event in generations:
            counts=schema_outcomes.setdefault(event['stage'],{'raw_valid':0,'accepted_with_deviation':0,'rejected':0,'not_transmitted':0})
            key=(('rejected' if event.get('attempts') else 'not_transmitted') if event.get('error_type') else
                 'accepted_with_deviation' if event.get('compatibility_deviation') else 'raw_valid')
            counts[key]+=1
        phase={'phase':'run2','campaign_id':CAMPAIGN_ID,'run_id':approval['run_id'],'binding':binding,
               'status':summary['status'] if summary and failure is None else 'incomplete',
               'completed_questions':summary['completed_questions'] if summary else 0,
               'processed_turns':len(outcomes),
               'total_memory_notes':binding.get('checkpoint',{}).get('completed_turns',0)+len(outcomes),
               'evolution_counter':outcomes[-1]['counter_after'] if outcomes else recovered['state']['evo_cnt'] if recovered else 0,
               'provider_contract_policy':INDEX_STRING_POLICY,
               **{key:(summary or {}).get(key,0) for key in ('provider_contract_deviation_count',
                     'validation_copy_transformed_item_count','inherited_provider_contract_deviation_count',
                     'inherited_validation_copy_transformed_item_count')},
               'returned_models':sorted({e['returned_model'] for e in generations if isinstance(e.get('returned_model'),str) and e['returned_model']}),
               'system_fingerprints':sorted({e['system_fingerprint'] for e in generations if isinstance(e.get('system_fingerprint'),str) and e['system_fingerprint']}),
               'schema_outcomes':schema_outcomes,
               'expected_questions':binding['expected_questions'],'error_type':type(failure).__name__ if failure else None,
               'budget':budget,'cell_budget':cell_budget,'campaign_budget':ledger_summary(permit.path),
               'observability':obs,'experiments':experiments,'recoverable_length_failure':recoverable,
               'secondary_failures':secondary_failures,
               'usable_for_next_phase':bool(summary and failure is None and not budget.get('halted')
                    and not cell_budget['unknown_attempts'] and obs.get('verified') and experiments.get('verified')),
               'completed_at':datetime.now(timezone.utc).isoformat(),
               'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}}
        try:
            if phase['usable_for_next_phase']:
                permit.complete_cell(phase,lambda:_save(output/'phase.json',phase))
            else:_save(output/'phase.json',phase)
        except BaseException as err:
            secondary_failures.append({'stage':'final_publication','error_type':type(err).__name__})
            try:permit.stop('run2_final_publication_failed')
            except BaseException as halt_error:
                secondary_failures.append({'stage':'publication_halt','error_type':type(halt_error).__name__})
            if (output/'phase.json').exists():os.replace(output/'phase.json',output/'phase-unconfirmed.json')
            phase.update(status='incomplete',usable_for_next_phase=False,recoverable_length_failure=False,
                         error_type=type(err).__name__,budget=permit.summary())
            phase['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
            _save(output/'phase.json',phase)
    return phase
