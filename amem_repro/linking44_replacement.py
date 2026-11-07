"""Financial admission for up to three fresh Linking Only / conv-44 attempts."""
from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from base64 import b64decode
from datetime import datetime
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from .budget import BudgetStop
from .config import OPENROUTER_CONFIG, fingerprint, stage_output_limits
from .contracts import load_author_contracts
from .openrouter import (CELL_SERVICE_RESERVE, CELL_SERVICE_UNITS, CONTEXT, INPUT_RATE,
                         MODEL, OUTPUT_RATE, CampaignLedger, usage_charge)

GROUP = 'linking44-overnight-v1'
GROUP_ROOT = Path('cells/linking_only-conv-44/replacement')
GROUP_LIMITS = {
    'group_microusd': 10_000_000, 'max_attempts': 3, 'max_calls_per_attempt': 1666,
    'max_langfuse_units_per_attempt': CELL_SERVICE_UNITS,
    'service_reserve_per_attempt_microusd': CELL_SERVICE_RESERVE,
    'planned_campaign_microusd': 42_000_000, 'protected_microusd': 8_000_000,
}
PR50_SQL = 'e78153d9b0c86e4572473861899d8673e67f0afa0112d46e4d3ecaa38055c81d'
PR50_LEDGER = '8ca77ffcc281af64050b73ea79109bab37c297f2c62465524deb1e7f27767f16'
PR50_EXPOSURE = 8_788_198
PR49_RELEASE = Path('cells/linking_only-conv-44/frozen/linking44-recovery-release.json')
PR49_SHA = 'e988e1c2cf21b4b3d97f1880d2aed2e94a2a8137f83f3d0cc838fd3cc15f41e5'
LAST_OLD_ID = 18348
STAGES = ('metadata', 'shared_decision') * 675 + ('query_keywords', 'answer') * 158
ROOT = Path(__file__).resolve().parents[1]


def require(ok, reason):
    if not ok:
        raise BudgetStop(reason)


def phase_id(ordinal):
    require(type(ordinal) is int and 1 <= ordinal <= 3, 'Invalid replacement ordinal')
    return f'gpt4omini-linking_only-conv44-replacement-r{ordinal}'


PHASES = tuple(phase_id(n) for n in (1, 2, 3))


def attempt_store(campaign, ordinal):
    phase_id(ordinal)
    path = Path(campaign) / GROUP_ROOT / f'attempt-{ordinal}'
    require(path.absolute() == path.resolve(), 'Aliased replacement namespace')
    return path


def file_bytes(path):
    require(path.absolute() == path.resolve() and path.is_file() and path.stat().st_nlink == 1,
            'Replacement evidence is missing or aliases foreign storage')
    return path.read_bytes()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bound_json(path, expected):
    raw = file_bytes(path)
    require(digest(raw) == expected, 'Replacement evidence hash differs')
    return json.loads(raw)


def signature(path):
    st = path.lstat()
    require(path.resolve() == path and st.st_nlink == 1, 'Replacement evidence alias')
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def history(db):
    full = CampaignLedger.access_snapshot(db)
    prior = {key: [r for r in rows if r[1 if key == 'attempts' else 0] not in PHASES]
             for key, rows in full.items()}
    require(fingerprint(prior) == PR50_SQL, 'PR50 financial history changed')
    phases = [r for r in full['phases'] if r[0] in PHASES]
    require([r[0] for r in phases] == list(PHASES[:len(phases)]), 'Foreign or out-of-order replacement phase')
    issued = {r[0] for r in phases}
    attempts = [r for r in full['attempts'] if r[1] in PHASES]
    require(all(r[1] in issued and r[0] == LAST_OLD_ID+i for i,r in enumerate(attempts,1))
            and all(r[0] in issued for r in full['halts'] if r[0] in PHASES), 'Unowned replacement attempt or halt')
    return phases, attempts


def validate_bounds(phases, attempts, extra_model=0, new_claims=0):
    spent = sum(r[5] for r in attempts) + extra_model
    exposure = spent + CELL_SERVICE_RESERVE * (len(phases) + new_claims)
    require(exposure <= GROUP_LIMITS['group_microusd']
            and PR50_EXPOSURE + exposure <= GROUP_LIMITS['planned_campaign_microusd'],
            'Replacement group or campaign spending limit reached')


def release_evidence(campaign, approval, binding):
    ordinal = approval['ordinal']
    group = campaign / GROUP_ROOT
    store = attempt_store(campaign, ordinal)
    release_file = group / 'release.json'
    release = bound_json(release_file, approval.get('release_sha256'))
    old = bound_json(campaign / PR49_RELEASE, PR49_SHA)
    from scripts.gpt4omini_replacement import reviewed_files, verify_capacity
    source, expected_files, _ = reviewed_files(release['reviewed_commit'])
    require(release['implementation_files']==expected_files, 'Release omits or changes reviewed runtime bytes')
    capacity_file = group/'capacity.json'
    capacity = bound_json(capacity_file,release.get('capacity_sha256'))
    as_of=None if ordinal==1 else release['approved_at']
    verify_capacity(capacity,binding['source_sha256'],release['reviewed_commit'],as_of=as_of,campaign=campaign)
    require(binding == {**old['binding'], 'source_sha256': fingerprint(source)}
            and release.get('approved') is True and release.get('approved_by')
            and release.get('group') == GROUP and release.get('binding') == binding
            and release.get('limits') == GROUP_LIMITS and release.get('historical_release_sha256') == PR49_SHA
            and release.get('opened_from_ledger_sha256') == PR50_LEDGER, 'Replacement group release differs')
    commit=release.get('reviewed_commit')
    require(isinstance(commit,str) and len(commit)==40 and all(c in '0123456789abcdef' for c in commit),
            'Missing reviewed commit')
    require(all(release.get('implementation_files', {}).get(k) == v for k,v in source['files'].items())
            and 'scripts/gpt4omini_replacement.py' in release['implementation_files'],
            'Replacement release omitted reviewed source')
    files = [release_file, campaign / PR49_RELEASE, group/'preflight.json', store/'frozen/approval.json',capacity_file]
    require(digest(file_bytes(files[2])) == release.get('preflight_sha256'), 'Replacement preflight differs')
    require(json.loads(file_bytes(files[3])) == approval, 'Replacement phase approval differs')
    for name, expected in release['implementation_files'].items():
        path = ROOT/name
        require(path.is_relative_to(ROOT) and digest(file_bytes(path)) == expected, 'Reviewed implementation changed')
        files.append(path)
    for axis in ('spec','standards'):
        path = group / f'{axis}-review.json'
        review = bound_json(path, release.get('reviews', {}).get(axis))
        require(review.get('verdict') == 'pass' and review.get('reviewed_commit') == release.get('reviewed_commit')
                and review.get('source_sha256') == binding['source_sha256'] and not review.get('open_material_findings')
                and not review.get('hard_standard_violations') and not review.get('findings'), 'Independent replacement review differs')
        files.append(path)
    return {p:signature(p) for p in files}


def _restart(campaign, db, phase):
    require(phase in PHASES[:-1], 'No remaining replacement ordinal')
    phases, all_attempts = history(db)
    matching = [r for r in phases if r[0] == phase]
    require(len(matching) == 1 and matching[0][3] == 'terminal', 'Prior attempt is not terminal')
    store = attempt_store(campaign, PHASES.index(phase)+1)
    directory = store / 'runs' / phase
    receipt = json.loads(file_bytes(directory/'phase.json'))
    require(receipt.get('phase') == phase and receipt.get('status') == 'incomplete'
            and receipt.get('error_type') == 'BudgetStop' and receipt.get('observations',{}).get('verified') is True
            and fingerprint(receipt) == matching[0][4],
            'Prior stopped scientific phase differs')
    for name,h in receipt['files'].items():
        path = directory/name
        require(path.is_relative_to(directory) and digest(file_bytes(path)) == h, 'Prior stopped evidence differs')
    observations=receipt['observations']
    evidence_path=Path(observations['evidence_path'])
    require(evidence_path.parent==directory and receipt['files'].get(evidence_path.name)==observations['evidence_sha256'],
            'Missing observation readback proof in phase seal')
    evidence=bound_json(evidence_path,observations['evidence_sha256'])
    require(evidence.get('verified') is True and evidence.get('kind')=='observations'
            and evidence.get('identity',{}).get('run_id')==phase and evidence['identity'].get('condition')=='linking_only'
            and evidence['identity'].get('conversation_id')=='conv-44' and evidence['identity'].get('repetition')==PHASES.index(phase)+1
            and evidence.get('observation_count',0)>0 and evidence.get('readback_files')
            and all(receipt['files'].get(name)==h for name,h in evidence['readback_files'].items()),
            'Critical runtime observations lack verified raw readbacks')
    capture=json.loads(file_bytes(directory/'trace-capture.json'))
    traces=sorted({x['trace_id'] for x in capture['observations']})
    require(not capture.get('errors') and evidence.get('observation_count')==len(capture['observations'])
            and evidence.get('score_count')==len(capture['scores']) and traces==sorted(capture['trace_ids'])==sorted(evidence['trace_ids'])
            and observations.get('observation_count')==evidence['observation_count']
            and observations.get('score_count')==evidence['score_count'] and sorted(observations['trace_ids'])==traces,
            'Observed counts differ from the sealed capture')
    runtime_units=len(capture['observations'])+len(traces)+len(capture['scores'])
    rows = [r for r in all_attempts if r[1] == phase]
    require(rows and all(r[6] == 'settled' and r[9] and r[10] is not None for r in rows),
            'Unresolved physical request forbids restart')
    events = [json.loads(line) for line in file_bytes(directory/'events.jsonl').splitlines()]
    errors = [e for e in events if e.get('type') == 'generation' and e.get('error_type')]
    # A supported in-phase malformed decision may have been handled before the final halt.
    failures = [e for e in events if e.get('type')=='failure']
    require(all(e.get('kind') in ('provider_completion','original_evolution_fallback') for e in failures)
            and all(e.get('original_fallback_verified') is True for e in failures if e.get('kind')=='original_evolution_fallback')
            and all(e.get('error_type')=='AdapterError' and any(f.get('kind')=='original_evolution_fallback'
                    and f.get('turn_id')==e.get('turn_id') for f in failures) for e in errors[:-1]),
            'Unresolved non-transport failure forbids restart')
    last = errors[-1] if errors else {}
    err = last.get('error_type')
    message = last.get('error_message','').lower()
    require(err in ('ConnectionResetError','ReadError','RemoteProtocolError')
            and ('connection reset' in message or 'server disconnected' in message or 'peer closed' in message)
            and db.execute('SELECT reason FROM halts WHERE phase=?',(phase,)).fetchall() == [(err,)]
            and last.get('budget_logical_id') == rows[-1][0] and last.get('stage') == rows[-1][2],
            'Prior halt is not an identified transient generation transport failure')
    attempt, = last['attempts']
    require(attempt.get('status_code') == 200 and attempt.get('response_body') and last.get('provider_response') == attempt['response_body']
            and fingerprint(attempt['response_body']) == rows[-1][7] and attempt.get('budget_attempt_id') == rows[-1][0],
            'Transient failure has no settled original response evidence')
    meter = json.loads(file_bytes(store/'service'/f'{phase}.json'))
    record = json.loads(file_bytes(store/'reconciliation.json'))
    require(record.get('verified') is True and record.get('phase') == phase and record.get('phase_seal') == matching[0][4]
            and record.get('settled_attempts_sha256') == fingerprint(rows) and record.get('unknown_attempt_ids') == []
            and record.get('movement',{}).get('verified') is True and record.get('service_units') == meter['admitted_units']
            and runtime_units == meter['runtime_units_admitted'] == meter['admitted_units']
            and 0 <= meter['admitted_units'] <= meter['maximum_units'] == CELL_SERVICE_UNITS and not meter['stopped'],
            'Prior attempt has no verified financial and service close')
    journal = Path(record['generation_journal'])
    require(journal.resolve() == journal and journal.is_relative_to(store), 'Foreign generation readback journal')
    require(len(record['generations']) == len(rows), 'Missing known-generation readbacks')
    for i,(r,g) in enumerate(zip(rows,record['generations'],strict=True)):
        raw = json.loads(file_bytes(directory/'raw'/f'{r[0]:06d}-response.bin'))
        usage = json.loads(r[8])
        require(raw['id'] == g['id'] == r[9] and raw['usage'] == usage and fingerprint(raw) == r[7]
                and g['provider_name'] == raw['provider'] == 'OpenAI' and g['model'] == raw['model'] == MODEL
                and g['native_tokens_prompt'] == usage['prompt_tokens']
                and g['native_tokens_completion'] == usage['completion_tokens']
                and Decimal(str(g['total_cost'])) == Decimal(r[10]) == Decimal(str(usage['cost']))
                and r[5] == usage_charge(usage, 4096 if r[2]=='shared_decision' else 1000),
                'Prior generation, route, usage or charge differs')
        hop, = g['provider_responses']
        require(hop['provider_name']=='OpenAI' and hop['model_permaslug']==MODEL and hop['status']==200,
                'Unverified upstream route')
        found = []
        paths=sorted(journal.glob(f'{i}-*.json'))
        require(1<=len(paths)<=9,'Missing or unbounded generation GET readback')
        for poll,path in enumerate(paths):
            item = json.loads(file_bytes(path))
            require(path.name == f'{i}-{poll}.json' and item['endpoint']=='generation'
                    and item['params']=={'id':r[9]}, 'Foreign journal lookup')
            if item.get('status') == 200:
                require(poll == len(paths)-1,'Additional readback following a successful GET')
                found.append(json.loads(b64decode(item['response_base64']))['data'])
            else:
                require(item.get('status') in (404,429),'Unsupported financial readback failure')
        require(found == [g], 'Original GET evidence missing')
    known = sum(Decimal(r[10]) for r in rows)
    opening, closing = record['opening']['account'], record['closing']
    for base, captured in ((store/'opening-reads',opening),(journal/'account',closing)):
        for endpoint in ('credits','key'):
            item = json.loads(file_bytes(base/f'{endpoint}.json'))
            require(item['endpoint']==endpoint and not item['params'] and item['status']==200,
                    'Missing original account GET')
            actual = json.loads(b64decode(item['response_base64']))['data']
            require(all(Decimal(str(actual[k]))==Decimal(v) for k,v in captured[endpoint].items()),
                    'Original account or key evidence differs')
    require(Decimal(closing['credits']['total_credits']) == Decimal(opening['credits']['total_credits'])
            and Decimal(closing['credits']['total_usage'])-Decimal(opening['credits']['total_usage'])
            == Decimal(closing['key']['usage'])-Decimal(opening['key']['usage'])
            == Decimal(opening['key']['limit_remaining'])-Decimal(closing['key']['limit_remaining']) == known,
            'Unexplained previous-attempt account movement')


def classify_restart(campaign, phase):
    """Whether a verified, financially closed transient permits a fresh next ordinal."""
    campaign = Path(campaign).resolve()
    try:
        with sqlite3.connect((campaign/'budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
            _restart(campaign, db, phase)
        return True
    except (BudgetStop, OSError, ValueError, TypeError, KeyError, sqlite3.Error, ArithmeticError):
        return False


class ReplacementLedger(CampaignLedger):
    """One group of fresh roots in the existing ledger, with a shared USD10 limit."""
    def __init__(self, path, *, campaign_root, binding):
        path=Path(path)
        require(path.is_file() and path.absolute()==path.resolve()==Path(campaign_root).resolve()/'budget.sqlite'
                and path.stat().st_nlink==1, 'Replacement requires the existing PR50 campaign file')
        # Check the sealed history on a read-only connection before the inherited
        # constructor can initialize tables or write an existing campaign row.
        with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as opening:
            history(opening)
        super().__init__(path,campaign_root=campaign_root,binding=binding)
        self.contracts = load_author_contracts()
        self.observations = {}
        self.protected = {}
        self.pending_attempt = None
        self.previous_history = None
        self.closed_attempts = []

    def observe_phase(self, phase, check):
        require(phase in PHASES and phase not in self.observations, 'Invalid replacement observation owner')
        self.observations[phase] = check

    def claim(self, approval):
        ordinal=approval.get('ordinal')
        phase=phase_id(ordinal)
        require(approval.get('approved') is True and approval.get('kind')=='replacement'
                and approval.get('group')==GROUP and approval.get('binding')==self.binding
                and approval.get('phase')==phase and approval.get('conversation')=='conv-44'
                and approval.get('condition')=='linking_only' and not approval.get('parent')
                and not approval.get('parent_path') and not approval.get('parent_seal')
                and approval.get('service_reserve_microusd')==CELL_SERVICE_RESERVE
                and datetime.fromisoformat(approval['approved_at']).tzinfo is not None,
                'Exact fresh replacement approval required')
        store=attempt_store(self.root,ordinal)
        require(not any((store/n).exists() or (store/n).is_symlink() for n in ('cache','runs','service','reconciliation.json')),
                'Replacement attempt namespace already used')
        protected = release_evidence(self.root,approval,self.binding)
        with self.transaction() as db:
            phases,attempts=history(db)
            require(len(phases)+1==ordinal and not self.claimed,'Previous ordinal, group owner, or attempt count differs')
            if ordinal==1:
                require(not approval.get('previous_reconciliation_sha256') and digest(file_bytes(self.path))==PR50_LEDGER,
                        'Opening requires the exact PR50 ledger')
            else:
                previous=PHASES[ordinal-2]
                for prior in phases:
                    _restart(self.root,db,prior[0])
                previous_file=attempt_store(self.root,ordinal-1)/'reconciliation.json'
                require(digest(file_bytes(previous_file))==approval.get('previous_reconciliation_sha256'),
                        'Earlier close differs from successor authorization')
                protected[previous_file]=signature(previous_file)
            validate_bounds(phases,attempts,new_claims=1)
            self.previous_history = fingerprint([phases,attempts])
            db.execute("INSERT INTO phases VALUES (?,?,NULL,'running',NULL)",(phase,json.dumps(approval,sort_keys=True)))
        self.claimed[phase]=copy.deepcopy(approval)
        self.protected[phase]=protected
        return phase

    def unaccepted_unknowns(self, approval):
        with self.transaction() as db:
            _,attempts=history(db)
            return sum(r[6]!='settled' for r in attempts)

    def reserve(self,phase,stage,request):
        try:
            require(not self.failed and phase in self.claimed and phase in self.guards and phase in self.observations,
                    'No live replacement owner, observations or admission guard')
            self.observations[phase]()
            require(all(signature(p)==s for p,s in self.protected[phase].items()),'Bound replacement approval or code changed')
            limit=stage_output_limits(OPENROUTER_CONFIG)[stage]
            require(request['max_tokens']==limit and request['model']==MODEL
                    and request['provider']==OPENROUTER_CONFIG['model']['provider']
                    and request['response_format']==self.contracts[stage]
                    and request['temperature'] in ((.5,.7) if stage=='answer' else (.7,)),
                    'Model, route, schema or generation settings changed')
            reservation=int((INPUT_RATE*(CONTEXT-limit)+OUTPUT_RATE*limit).to_integral_value(rounding=ROUND_CEILING))
            with self.transaction() as db:
                phases,attempts=history(db)
                require(phases[-1] == [phase,json.dumps(self.claimed[phase],sort_keys=True),None,'running',None]
                        and not db.execute('SELECT 1 FROM halts WHERE phase=?',(phase,)).fetchone()
                        and all(r[6]=='settled' for r in attempts), 'Unknown, terminal or foreign replacement request')
                require(fingerprint([phases[:-1],[r for r in attempts if r[1]!=phase]]) == self.previous_history,
                        'Earlier replacement history changed after claim')
                own=[r for r in attempts if r[1]==phase]
                require(own == self.closed_attempts and len(own)<len(STAGES) and stage==STAGES[len(own)],
                        'Replacement request order or limit differs')
                self.guards[phase](db)
                validate_bounds(phases,attempts,extra_model=reservation)
                cur=db.execute("INSERT INTO attempts(phase,stage,request_hash,reservation,charge,state) VALUES(?,?,?,?,?,'reserved')",
                               (phase,stage,fingerprint(request),reservation,reservation))
                attempt=cur.lastrowid
            self.pending_attempt=(attempt,limit,phase,stage,fingerprint(request),reservation)
            return attempt,reservation
        except BaseException:
            self.failed=True
            raise BudgetStop('Replacement admission failed; no model transmission') from None

    def settle(self, attempt, response, output_limit):
        pending=self.pending_attempt
        require(not self.failed and pending is not None and pending[:2]==(attempt,output_limit),
                'Only the owned live request can settle')
        self.pending_attempt=None
        charge=super().settle(attempt,response,output_limit)
        _,_,phase,stage,request_hash,reservation=pending
        self.closed_attempts.append([attempt,phase,stage,request_hash,reservation,charge,'settled',
                                    fingerprint(response),json.dumps(response['usage'],sort_keys=True),
                                    response['id'],str(response['usage']['cost'])])
        return charge

    def stop(self, phase, reason):
        require(phase in self.claimed, 'Cannot modify another financial phase')
        return super().stop(phase,reason)

    def finish(self, phase, receipt, state):
        require(phase in self.claimed and receipt.get('phase')==phase, 'Cannot seal another replacement')
        if state=='complete':
            require(not self.failed and len(self.closed_attempts)==len(STAGES)
                    and receipt.get('status') in ('complete','degraded')
                    and (receipt.get('notes'),receipt.get('questions'))==(675,158),
                    'A completed replacement requires its entire declared population')
        return super().finish(phase,receipt,'terminal' if state=='recoverable' else state)
