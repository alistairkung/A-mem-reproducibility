"""Offline regression for the sole authorized terminal-parent financial exception."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

from amem_repro import blk027, linking44_finance as finance
from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.openrouter import CampaignLedger, EXPANSION_POLICY, SCIENTIFIC_BINDING, save_new


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def recovery(tmp_path, monkeypatch):
    # Other cell acceptances and scientific author evidence have their own tests.
    # Pin the reduced synthetic stopped history to this fixture's exact digests.
    sources = {'files': {'synthetic.py': 'b' * 64}}
    binding = {**SCIENTIFIC_BINDING, 'condition': 'linking_only', 'conversation_id': 'conv-44',
               'source_sha256': fingerprint(sources)}
    ledger = CampaignLedger(tmp_path / 'budget.sqlite', campaign_root=tmp_path, binding=binding)
    monkeypatch.setattr(finance, 'source_fingerprint', lambda root: sources)
    monkeypatch.setattr(ledger, 'check_previous_cells', lambda db, approval: None)
    monkeypatch.setattr(ledger, 'retained_prefix', lambda db, approval: set())
    monkeypatch.setattr(blk027, 'retained_terminal', lambda root, db, approval: None)
    prior = {'binding': {**binding, 'source_sha256': 'a' * 64}, 'phase': finance.PARENT,
             'condition': 'linking_only', 'conversation': 'conv-44', 'kind': 'baseline'}
    save_new(tmp_path / finance.PARENT_PATH, prior)
    save_new(tmp_path / finance.RECONSTRUCTION_PATH, {'next_turn': 'D10:16'})
    stop = {'closing': {'credits': {'total_credits': '50', 'total_usage': '3.79817075'},
                        'key': {'limit_remaining': '46.21348025', 'usage': '3.78651975'}},
            'campaign_identified_model_usd': '3.78651975'}
    save_new(tmp_path / finance.STOP_CLOSE, stop)
    monkeypatch.setattr(finance, 'PARENT_FILE_SHA', digest(tmp_path / finance.PARENT_PATH))
    monkeypatch.setattr(finance, 'STOP_CLOSE_SHA', digest(tmp_path / finance.STOP_CLOSE))
    with ledger.transaction() as db:
        db.execute('INSERT INTO phases VALUES (?,?,NULL,?,?)',
                   (finance.PARENT, json.dumps(prior), 'terminal', finance.PARENT_SEAL))
        db.execute('INSERT INTO halts VALUES (?,?)', (finance.PARENT, 'RemoteProtocolError'))
        db.execute('INSERT INTO attempts VALUES (17285,?,?,?,?,?,?,?,?,?,?)',
                   (finance.PARENT, 'metadata', fingerprint({'max_tokens': 1000, 'metadata': 'D10:15'}),
                    19650, 107623, 'settled', 'response', '{}', 'gen-known', '0.10740285'))
        db.execute('INSERT INTO attempts VALUES (17286,?,?,?,?,?,?,NULL,NULL,NULL,NULL)',
                   (finance.PARENT, 'shared_decision', fingerprint({'max_tokens': 4096, 'decision': 'D10:15'}),
                    21044, 21044, 'reserved'))
        snapshot = fingerprint(ledger.access_snapshot(db))
    monkeypatch.setattr(finance, 'PARENT_SQL', snapshot)
    monkeypatch.setattr(finance, 'STOP_SQL', snapshot)
    release = {'phase': finance.CHILD, 'approved': True, 'parent': finance.PARENT,
               'parent_seal': finance.PARENT_SEAL, 'binding': binding,
               'limits': dict(finance.RECOVERY_LIMITS),
               'reconstruction_sha256': digest(tmp_path / finance.RECONSTRUCTION_PATH)}
    release.update(files={}, reviewed_commit='a'*40, merge_commit='b'*40)
    monkeypatch.setattr(blk027, 'verify_merged_review', lambda root, reviewed, merge: None)
    for axis in ('spec', 'standards'):
        for filename, value in [
                (f'baseline-{axis}-review.json', {'verdict': 'pass', 'reviewed_commit': release['reviewed_commit'],
                 'source_sha256': binding['source_sha256']}),
                (f'reconstruction-{axis}.json', {'verified': True, 'source_sha256': binding['source_sha256'],
                 'reconstruction_sha256': release['reconstruction_sha256']})]:
            relative = Path('verification/linking44-release') / filename
            save_new(tmp_path / relative, value)
            release['files'][(Path('artifacts/gpt4omini') / relative).as_posix()] = digest(tmp_path / relative)
    save_new(tmp_path / finance.RELEASE_PATH, release)
    approval = {'binding': binding, 'phase': finance.CHILD, 'parent': finance.PARENT,
                'parent_path': str(tmp_path / finance.PARENT_PATH), 'parent_seal': finance.PARENT_SEAL,
                'approved': True, 'condition': 'linking_only', 'conversation': 'conv-44',
                'kind': 'baseline', 'ablation_policy': EXPANSION_POLICY,
                'retained_access_prefix': finance.ACCESS, 'previous_acceptance_sha256': finance.FRONTIER,
                'reporting_acceptance_sha256': finance.REPORTING, 'release_sha256': fingerprint(release),
                finance.RELEASE_KEY: digest(tmp_path / finance.RELEASE_PATH)}
    return ledger, approval


def start(recovery):
    ledger, approval = recovery
    assert ledger.claim(approval) == finance.CHILD
    ledger.set_guard(finance.CHILD, lambda db: None)
    return ledger


def test_one_owned_child_preserves_unknown_and_stops_on_new_unknown(recovery):
    ledger, approval = recovery
    assert ledger.unaccepted_unknowns(approval) == 0
    start(recovery)
    attempt, _ = ledger.reserve(finance.CHILD, 'metadata', {'max_tokens': 1000, 'metadata': 'D10:16'})
    assert attempt == 17287 and ledger.unaccepted_unknowns(approval) == 1
    with pytest.raises(BudgetStop):
        ledger.reserve(finance.CHILD, 'shared_decision', {'max_tokens': 4096})
    with ledger.transaction() as db:
        finance.check_parent(db)
        assert db.execute('SELECT COUNT(*) FROM attempts WHERE phase=?',(finance.CHILD,)).fetchone() == (1,)


@pytest.mark.parametrize('field,value', [
    ('phase', 'gpt4omini-linking_only-conv44-r0-p2'), ('parent', 'foreign'), ('parent_seal', 'f'*64),
    ('previous_acceptance_sha256', 'f'*64), ('reporting_acceptance_sha256', 'f'*64),
    ('retained_access_prefix', 'f'*64), ('release_sha256', '0'*64), (finance.RELEASE_KEY, '0'*64),
    ('parent_path', '/tmp/unrelated'), ('condition', 'neither'), ('conversation', 'conv-50'),
    ('approved', False),
])
def test_forged_release_cannot_claim(recovery, field, value):
    ledger, approval = recovery
    with pytest.raises(BudgetStop):
        ledger.claim({**approval, field:value})
    with ledger.transaction() as db:
        assert not db.execute('SELECT 1 FROM phases WHERE parent=?',(finance.PARENT,)).fetchone()


def test_parent_halt_still_blocks_ordinary_child_and_repeated_grant(recovery):
    ledger, approval = recovery
    plain = dict(approval)
    del plain[finance.RELEASE_KEY]
    with pytest.raises(BudgetStop):
        ledger.claim(plain)
    start(recovery)
    with pytest.raises(BudgetStop):
        ledger.claim(approval)
    ledger.finish(finance.CHILD, {'status': 'incomplete'}, 'recoverable')
    with ledger.transaction() as db:
        assert db.execute('SELECT state FROM phases WHERE id=?',(finance.CHILD,)).fetchone() == ('terminal',)


@pytest.mark.parametrize('mutation', ['charge', 'halt', 'reserve', 'reconstruction', 'release', 'source'])
def test_changed_bound_evidence_or_sql_denies_request(recovery, mutation):
    ledger, _ = recovery
    start(recovery)
    if mutation in ('charge','reserve','halt'):
        with ledger.transaction() as db:
            if mutation == 'halt':
                db.execute('DELETE FROM halts WHERE phase=?', (finance.PARENT,))
            else:
                col = 'charge' if mutation == 'charge' else 'reservation'
                db.execute(f'UPDATE attempts SET {col}=3 WHERE id=17286')
    else:
        if mutation == 'source':
            with ledger.transaction() as db:
                db.execute('UPDATE phases SET approval=? WHERE id=?', ('{}', finance.CHILD))
        else:
            rel = finance.RECONSTRUCTION_PATH if mutation == 'reconstruction' else finance.RELEASE_PATH
            (ledger.root / rel).write_text('{}')
    with pytest.raises(BudgetStop):
        ledger.reserve(finance.CHILD,'metadata',{'max_tokens':1000})


@pytest.mark.parametrize('stage,payload', [
    ('metadata', {'max_tokens':1000,'metadata':'D10:15'}),
    ('shared_decision', {'max_tokens':4096,'decision':'D10:15'}),
    ('query_keywords', {'max_tokens':1000}), ('answer', {'max_tokens':1000}),
])
def test_no_partial_turn_duplicate_or_out_of_order_request(recovery, stage, payload):
    ledger = start(recovery)
    with pytest.raises(BudgetStop):
        ledger.reserve(finance.CHILD, stage, payload)


def test_unknown_remains_unsettleable(recovery):
    ledger = start(recovery)
    with pytest.raises(BudgetStop):
        ledger.settle(17286, {'id':'gen-fake','usage':{'prompt_tokens':1,'completion_tokens':1,'cost':0}}, 4096)
    with ledger.transaction() as db:
        finance.check_parent(db)


def test_exact_initial_account_and_key_movement(recovery):
    ledger, _ = recovery
    correct = json.loads((ledger.root / finance.STOP_CLOSE).read_text())['closing']
    assert finance.verify_opening(ledger.root,correct)['movement']['verified']
    for endpoint, field in [('credits','total_usage'),('credits','total_credits'),
                            ('key','usage'),('key','limit_remaining')]:
        changed = {k: dict(v) for k,v in correct.items()}
        changed[endpoint][field] = str(Decimal(changed[endpoint][field])+Decimal('0.000001'))
        with pytest.raises(BudgetStop):
            finance.verify_opening(ledger.root,changed)


@pytest.mark.parametrize('bad', [None, 'native_tokens', 'price', 'extra_account_movement', 'additional_unknown'])
def test_roll_forward_new_ids_only_and_keep_unresolved(recovery, monkeypatch, bad):
    import httpx

    ledger, approval = recovery
    # Keep the production row counts and outstanding IDs while constructing
    # cheap synthetic prior records with the already verified total charge.
    with ledger.transaction() as db:
        prior_rows = [(i, 'prior', 'metadata', str(i), 19650,
                       19650 if i <= 3 else 0, 'reserved' if i <= 3 else 'settled',
                       None if i <= 3 else f'gen-prior-{i}',
                       None if i <= 3 else ('3.67911690' if i == 4 else '0'))
                      for i in range(1,17285)]
        db.executemany('INSERT INTO attempts (id,phase,stage,request_hash,reservation,charge,state,provider_id,reported_cost)'
                       ' VALUES (?,?,?,?,?,?,?,?,?)', prior_rows)
        monkeypatch.setattr(finance, 'STOP_SQL', fingerprint(ledger.access_snapshot(db)))
    start(recovery)
    with ledger.transaction() as db:
        new = [(finance.CHILD, stage, str(i), 19650, 1, 'settled', json.dumps({'prompt_tokens': 1, 'completion_tokens': 1}),
                f'gen-child-{i}', '0.000001') for i,stage in enumerate(finance.STAGES)]
        db.executemany('INSERT INTO attempts (phase,stage,request_hash,reservation,charge,state,usage,provider_id,reported_cost)'
                       ' VALUES (?,?,?,?,?,?,?,?,?)', new)
        if bad == 'additional_unknown':
            db.execute("UPDATE attempts SET state='reserved' WHERE id=17287")
    ledger.finish(finance.CHILD, {'verified': True}, 'complete')
    nominal = json.loads((ledger.root/finance.STOP_CLOSE).read_text())['closing']
    opening = finance.verify_opening(ledger.root, nominal)
    requested = []
    def get(request):
        assert request.method == 'GET'
        endpoint = request.url.path.split('/')[-1]
        if endpoint == 'generation':
            ident = request.url.params['id']
            assert ident.startswith('gen-child-')
            requested.append(ident)
            data = {'id':ident,'model':'openai/gpt-4o-mini-2024-07-18','provider_name':'OpenAI',
                    'native_tokens_prompt': 2 if bad == 'native_tokens' else 1,
                    'native_tokens_completion':1, 'total_cost':'0.000002' if bad == 'price' else '0.000001',
                    'provider_responses':[{'provider_name':'OpenAI','status':200,
                                           'model_permaslug':'openai/gpt-4o-mini-2024-07-18'}]}
        else:
            delta = Decimal('0.001202')
            data = dict(nominal[endpoint])
            if endpoint == 'credits':
                if bad == 'extra_account_movement':
                    delta += Decimal('0.000001')
                data['total_usage'] = str(Decimal(data['total_usage']) + delta)
            else:
                assert endpoint == 'key'
                data['usage'] = str(Decimal(data['usage']) + delta)
                data['limit_remaining'] = str(Decimal(data['limit_remaining']) - delta)
        return httpx.Response(200, json={'data': data})
    receipt_path = ledger.root/'reconciliation.json'
    with httpx.Client(transport=httpx.MockTransport(get)) as client:
        if bad is None:
            result = finance.reconcile_child(client, ledger, receipt_path, opening)
            assert result['verified'] and result['generation_count'] == len(set(requested)) == 1202
            assert result['accounting']['unknown_attempts'] == 4
            assert result['reserved_unknown_microusd'] == 79994
        else:
            with pytest.raises((BudgetStop,ValueError)):
                finance.reconcile_child(client, ledger, receipt_path, opening)
            assert not receipt_path.exists()
            if bad == 'additional_unknown':
                assert requested == []


def test_remaining_model_cap_includes_parent_and_unknown(recovery, monkeypatch):
    ledger = start(recovery)
    # Parent SQL is a fixed real-cost proof. Add a settled child with sufficient
    # known expenditure to make another maximum reservation unaffordable.
    with ledger.transaction() as db:
        db.execute('INSERT INTO attempts (phase,stage,request_hash,charge,reservation,state) VALUES (?,?,?,?,?,?)',
                   (finance.CHILD, 'metadata','earlier-child',3_780_000,3_780_000,'settled'))
    with pytest.raises(BudgetStop):
        ledger.reserve(finance.CHILD,'shared_decision',{'max_tokens':4096})


def test_review_file_swap_between_claim_and_admission(recovery):
    ledger = start(recovery)
    (ledger.root/'verification/linking44-release/baseline-spec-review.json').write_text('{}')
    with pytest.raises(BudgetStop):
        ledger.reserve(finance.CHILD,'metadata',{'max_tokens':1000})
