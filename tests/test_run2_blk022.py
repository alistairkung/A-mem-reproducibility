"""Financial-only BLK-022 adjudication and exact-state admission boundaries."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3

import pytest

from amem_repro import run2
from amem_repro import run2_blk022 as incident
from amem_repro.budget import BudgetStop, ledger_summary

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_SOURCE_ROOT = Path(os.environ.get('AMEM_RUN2_REVIEWED_SOURCE_ROOT', ROOT)).resolve()


@pytest.fixture
def evidence(tmp_path):
    source = Path(os.environ.get('AMEM_BLK022_EVIDENCE_ROOT', ROOT))
    base = source / 'artifacts/run2'
    if not (base / 'budget.sqlite').exists():
        pytest.skip('Optional immutable BLK-022 evidence is not present')
    target = tmp_path / 'artifacts/run2'
    target.mkdir(parents=True)
    shutil.copy2(base / 'budget.sqlite', target / 'budget.sqlite')
    shutil.copytree(base / 'runs' / incident.PARENT_RUN,
                    target / 'runs' / incident.PARENT_RUN)
    campaign = json.loads((base / 'frozen/campaign-approval.json').read_text())
    return tmp_path, campaign


def approve(plan):
    plan = copy.deepcopy(plan)
    plan.update(approved=True, approved_by='offline financial review',
                approved_at='2026-11-03T12:00:00Z')
    return plan


def test_financial_receipt_retains_original_unknown_and_cannot_authorize_paid_phase(evidence):
    root, campaign = evidence
    ledger = root / 'artifacts/run2/budget.sqlite'
    before = ledger.read_bytes()
    plan = incident.plan_financial_adjudication(root=root, campaign=campaign)
    assert plan['paid_execution_authorized'] is False
    with pytest.raises(BudgetStop, match='approval'):
        incident.verify_financial_adjudication(plan, root=root, campaign=campaign)
    receipt = incident.verify_financial_adjudication(approve(plan), root=root, campaign=campaign)
    assert receipt['accounting'] == {
        'unknown_attempts': 1, 'unadjudicated_unknown_attempts': 0,
        'retained_unknown_microusd': 324404, 'known_settled_microusd': 720433,
        'charged_or_reserved_microusd': 1044837,
        'original_cell_cap_microusd': 5000000, 'remaining_cell_cap_microusd': 3955163}
    assert ledger_summary(ledger)['unknown_attempts'] == 1
    assert ledger.read_bytes() == before
    with pytest.raises(BudgetStop):
        run2.Run2Permit(receipt, root, campaign)


@pytest.mark.parametrize('change', [
    lambda a: a['binding'].update(attempt_id=455),
    lambda a: a['binding'].update(reservation_microusd=1),
    lambda a: a['binding'].update(request_sha256='0' * 64),
    lambda a: a.update(paid_execution_authorized=True),
    lambda a: a.update(scope='paid'),
    lambda a: a['accounting'].update(unknown_attempts=0),
])
def test_financial_receipt_cannot_waive_another_attempt_or_reduce_exposure(evidence, change):
    root, campaign = evidence
    approval = approve(incident.plan_financial_adjudication(root=root, campaign=campaign))
    change(approval)
    with pytest.raises(BudgetStop):
        incident.verify_financial_adjudication(approval, root=root, campaign=campaign)


@pytest.mark.parametrize('sql', [
    'UPDATE attempts SET reservation=1 WHERE id=454',
    'UPDATE attempts SET charge=0 WHERE id=454',
    "UPDATE attempts SET status='settled',usage_json='{}' WHERE id=454",
    "UPDATE attempts SET request_sha256='forged' WHERE id=454",
    "UPDATE attempts SET status='unknown',usage_json='null',charge=reservation WHERE id=453",
    'DELETE FROM logical_calls WHERE id=453',
    "UPDATE run2_phases SET receipt_sha256='forged' WHERE phase_index=0",
])
def test_tampered_original_ledger_rejects_financial_admission(evidence, sql):
    root, campaign = evidence
    approval = approve(incident.plan_financial_adjudication(root=root, campaign=campaign))
    with sqlite3.connect(root / 'artifacts/run2/budget.sqlite') as db:
        db.execute(sql)
    with pytest.raises(BudgetStop):
        incident.verify_financial_adjudication(approval, root=root, campaign=campaign)


def test_checkpoint_restores_exact_227_notes_without_repeating_valid_retry(evidence):
    root, campaign = evidence
    receipt = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    directory = root / 'artifacts/run2/runs' / incident.PARENT_RUN
    events = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    preflight = json.loads((directory / 'preflight.json').read_text())
    state = run2.verify_checkpoint(directory / 'phase.json', root=root, campaign=campaign,
        manifest=events[0]['manifest'], sources=events[0]['source_hashes'], receipt=preflight,
        financial_adjudication=receipt)
    original = json.loads((directory / 'partial-memory.json').read_text())['state']
    assert state['state'] == original
    assert state['state']['evo_cnt'] == 226
    assert state['lineage']['completed_turns'] == 227
    assert state['lineage']['next_turn_id'] == 'D10:11'
    assert state['lineage']['remaining_logical_calls'] == 1212
    assert state['lineage']['parent_receipt_sha256'] == incident.PARENT_RECEIPT
    with pytest.raises(ValueError, match='BLK013'):
        run2.verify_checkpoint(directory / 'phase.json', root=root, campaign=campaign,
            manifest=events[0]['manifest'], sources=events[0]['source_hashes'], receipt=preflight)


def test_financial_permission_admits_only_known454_and_still_stops_any_new_unknown(evidence):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    with sqlite3.connect(root / 'artifacts/run2/budget.sqlite') as db:
        assert incident.unknown_counts(db)['unadjudicated_unknown_attempts'] == 1
        assert incident.unknown_counts(db, financial) == {
            'unknown_attempts': 1, 'unadjudicated_unknown_attempts': 0}
        db.execute("INSERT INTO attempts VALUES (456,454,?,'new-request','unknown',324404,324404,'null')",
                   (incident.PARENT_APPROVAL,))
        with pytest.raises(BudgetStop, match='prefix'):
            incident.unknown_counts(db, financial)


def test_source_migration_rejects_dynamic_reference_before_any_source_trust(evidence):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    with pytest.raises(ValueError, match='full immutable'):
        incident.verify_support_migration(root=root, campaign=campaign, sources={}, receipt={},
            financial_adjudication=financial, reviewed_commit='HEAD')


def approved_child(root, campaign, financial):
    directory = root / 'artifacts/run2/runs' / incident.PARENT_RUN
    start = json.loads((directory / 'events.jsonl').read_text().splitlines()[0])
    checked = run2.verify_checkpoint(directory / 'phase.json', root=root, campaign=campaign,
        manifest=start['manifest'], sources=start['source_hashes'],
        receipt=json.loads((directory / 'preflight.json').read_text()), financial_adjudication=financial)
    binding = run2._binding(campaign, 0)
    # The permit seam checks the immutable approved allocation; production runtime
    # independently verifies these pins against every explicit reviewed Git blob.
    migration = {'policy': incident.MIGRATION_POLICY, 'reviewed_commit': 'b' * 40,
        'original_source_sha256': binding['source_sha256'],
        'original_preflight_sha256': binding['preflight_sha256'],
        'candidate_source_sha256': 'c' * 64, 'candidate_preflight_sha256': 'd' * 64,
        'financial_receipt_sha256': run2.fingerprint(financial),
        'changed_files': sorted(incident.MIGRATION_FILES)}
    binding.update(checkpoint=checked['lineage'], financial_adjudication=financial,
        support_migration=migration, source_sha256='c' * 64, preflight_sha256='d' * 64)
    return {'phase': 'run2', 'phase_index': 1, 'run_id': 'run2-full-conv-44-r0-p1',
        'approval_id': 'offline-child-only', 'approved': True, 'approved_by': 'offline test',
        'approved_at': '2026-11-03T12:00:00Z', 'binding': binding, 'pricing': run2.PRICING,
        'limits': {'phase_usd': '3.955163', 'max_logical_calls': 1212, 'max_attempts': 3636}}


def test_separately_approved_child_keeps_cell_cap_and_parent_one_shot(evidence):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    permit = run2.Run2Permit(child, root, campaign)
    assert permit.cell_summary() == {'logical_calls': 454, 'physical_attempts': 455,
        'charged_or_reserved_microusd': 1044837, 'unknown_attempts': 1,
        'unadjudicated_unknown_attempts': 0}
    assert permit.start_logical('metadata') == 455
    assert permit.summary()['phase_cap_microusd'] == 3955163
    with pytest.raises(BudgetStop, match='consumed'):
        run2.Run2Permit(child, root, campaign)
    assert ledger_summary(root / 'artifacts/run2/budget.sqlite')['unknown_attempts'] == 1


def test_second_unknown_from_genuine_sdk_retry_is_never_covered_by_original_receipt(evidence, monkeypatch):
    import httpx
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.config import RUN2_CONFIG
    from amem_repro.contracts import load_author_contracts
    from test_adapter_budget import response
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    permit = run2.Run2Permit(child, root, campaign)
    sent = []
    def sdk(request):
        sent.append(request)
        if len(sent) == 1:
            raise httpx.RemoteProtocolError('synthetic body-read failure')
        return httpx.Response(200, json=response('{"keywords":["a","b","c"],"context":"saved suffix","tags":["a","b","c"]}'))
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'offline-placeholder')
    controller = create_deepseek_controller(paid_authorized=True, phase_permit=permit,
        generation_config=RUN2_CONFIG, provider_contract_policy='canonical-index-strings-v1',
        http_transport=httpx.MockTransport(sdk))
    try:
        raw = controller.get_completion('original next metadata', load_author_contracts()['metadata'])
        assert json.loads(raw)['context'] == 'saved suffix'
        assert len(sent) == 2
        assert permit.cell_summary()['unknown_attempts'] == 2
        assert permit.cell_summary()['unadjudicated_unknown_attempts'] == 1
        assert permit.cell_summary()['charged_or_reserved_microusd'] >= 1360610
        with pytest.raises(BudgetStop, match='Unknown charge'):
            controller.get_completion('must not transmit', load_author_contracts()['metadata'])
        assert len(sent) == 2
    finally:
        controller.client.close()


@pytest.mark.parametrize('target', ['prompt', 'foreign_condition', 'extra_field', 'approval'])
def test_child_binding_cannot_change_frozen_science_or_reuse_financial_approval(evidence, target):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    if target == 'prompt':
        child['binding']['max_output_tokens_by_stage']['shared_decision'] = 9000
    elif target == 'foreign_condition':
        child['binding']['condition'] = 'neither'
    elif target == 'extra_field':
        child['binding']['checkpoint']['completed_turns'] = 228
    else:
        child['approved'] = False
    with pytest.raises(BudgetStop):
        run2.Run2Permit(child, root, campaign)


def test_child_cannot_restore_original_five_dollar_cap(evidence):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    child['limits']['phase_usd'] = '5'
    with pytest.raises(BudgetStop, match='remainder'):
        run2.Run2Permit(child, root, campaign)


@pytest.fixture
def candidate(evidence, monkeypatch):
    from amem_repro.config import source_fingerprint
    import subprocess
    root, campaign = evidence
    # Historical paid-migration tests must use their original source inventory.
    # New campaign modules are intentionally ineligible for that consumed grant.
    sources = source_fingerprint(REVIEWED_SOURCE_ROOT)
    for name in sources['files']:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(REVIEWED_SOURCE_ROOT / name)
    (root / '.git').symlink_to(REVIEWED_SOURCE_ROOT / '.git')
    (root / 'data').symlink_to(REVIEWED_SOURCE_ROOT / 'data', target_is_directory=True)
    (root / 'manifests').symlink_to(REVIEWED_SOURCE_ROOT / 'manifests', target_is_directory=True)
    from amem_repro import observation_policy
    # This existing fixture mocks the external preflight; mock the independently
    # tested cloud/credential gate too. Never treat it as historical cloud proof.
    monkeypatch.setattr(observation_policy, 'release_binding', lambda *a: {
        'policy': observation_policy.POLICY_ID, 'gate_sha256':'a'*64,
        'credential_receipt_sha256':'b'*64,
        'execution_script_sha256':hashlib.sha256((ROOT/observation_policy.LAUNCHER).read_bytes()).hexdigest()})
    # The same mocked external gate now includes the original-fallback proof.
    # This is fixture admission data, never a claim of actual cloud verification.
    gate = root / observation_policy.GATE_DIRECTORY / run2.fingerprint(sources)
    gate.mkdir(parents=True)
    (gate/'receipt.json').write_text(json.dumps({'malformed_fallback_verified':True}))
    origin = Path(os.environ.get('AMEM_BLK022_EVIDENCE_ROOT', ROOT))
    (root / 'artifacts/run2/gate-a').mkdir()
    shutil.copy2(origin / 'artifacts/run2/gate-a/run1-preservation.json',
                 root / 'artifacts/run2/gate-a/run1-preservation.json')
    shutil.copy2(origin / 'artifacts/study-budget.sqlite', root / 'artifacts/study-budget.sqlite')
    directory = root / 'artifacts/run2/runs' / incident.PARENT_RUN
    preflight = json.loads((directory / 'preflight.json').read_text())
    # A copied preflight represents the external runtime boundary in these tests.
    # Production must generate a new network-disabled runtime receipt after merge.
    preflight['source_sha256'] = run2.fingerprint(sources)
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    reference = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REVIEWED_SOURCE_ROOT, text=True).strip()
    return root, campaign, sources, preflight, financial, reference, origin / 'artifacts/assets'


def test_reviewed_source_plan_is_unapproved_and_cannot_claim_or_transmit(candidate):
    root, campaign, sources, preflight, financial, reference, assets = candidate
    ledger = root / 'artifacts/run2/budget.sqlite'
    before = ledger.read_bytes()
    plan = run2.plan_phase(campaign, preflight, assets, root=root, condition='full',
        conversation_id='conv-44', parent=root / 'artifacts/run2/runs' / incident.PARENT_RUN / 'phase.json',
        financial_adjudication=financial, support_reference=reference)
    assert plan['approved'] is False
    assert plan['limits'] == {'phase_usd': '3.955163', 'max_logical_calls': 1212, 'max_attempts': 3636}
    assert plan['binding']['source_sha256'] == run2.fingerprint(sources)
    assert plan['binding']['checkpoint']['next_turn_id'] == 'D10:11'
    assert plan['binding']['support_migration']['reviewed_commit'] == reference
    with pytest.raises(BudgetStop, match='approval'):
        run2.execute_phase(plan, campaign, preflight, assets, root=root,
            observer=object(), verify_observations=lambda: None, verify_results=lambda: None)
    assert ledger.read_bytes() == before


@pytest.mark.parametrize('name', ['amem_repro/adapter.py', 'amem_repro/budget.py',
                                 'memory_layer.py', 'config/run2.json'])
def test_explicit_reviewed_commit_rejects_science_or_unreviewed_bytes(candidate, name):
    root, campaign, sources, preflight, financial, reference, assets = candidate
    sources = copy.deepcopy(sources)
    sources['files'][name] = 'e' * 64
    # Adapter is now a named reviewed file; stale bytes also invalidate preflight
    # before the exact Git-blob check. Every branch must still reject admission.
    with pytest.raises(ValueError, match='outside|explicit reviewed commit|candidate preflight'):
        incident.verify_support_migration(root=root, campaign=campaign, sources=sources,
            receipt=preflight, financial_adjudication=financial, reviewed_commit=reference)


@pytest.mark.parametrize('complete', [False, True])
def test_real_runner_resumes_D10_11_once_and_retains_exact_prefix(candidate, monkeypatch, complete):
    import httpx
    import numpy as np
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.author import make_agent_factory
    from amem_repro.measurements import TokenCounter
    from amem_repro.scoring import AuthorScorer
    from test_foundation import LocalRetriever, Provider, original_memory_module
    from test_scoring import dependencies
    from test_run2 import OfflineObserver, observed, experiments
    root, campaign, sources, preflight, financial, reference, assets = candidate
    parent = root / 'artifacts/run2/runs' / incident.PARENT_RUN
    original_state = json.loads((parent / 'partial-memory.json').read_text())['state']
    original_inventory = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in parent.iterdir() if p.is_file()}
    child = run2.plan_phase(campaign, preflight, assets, root=root, condition='full',
        conversation_id='conv-44', parent=parent / 'phase.json',
        financial_adjudication=financial, support_reference=reference)
    child = approve(child)
    class Retriever(LocalRetriever):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.embeddings = np.empty((0, 384), dtype=np.float32)
        def add_documents(self, documents):
            for document in documents:
                self.document_ids[document] = len(self.corpus)
                self.corpus.append(document)
                self.embeddings = np.vstack((self.embeddings, np.ones((1, 384), dtype=np.float32)))
    class StopAfterNextNote(OfflineObserver):
        pending = False
        def __call__(self, event):
            super().__call__(event)
            if not complete and event.get('type') == 'evolution_outcome' and event.get('turn_id') == 'D10:11':
                self.pending = True
        def assert_healthy(self):
            if self.pending:
                self.pending = False
                raise RuntimeError('synthetic safe-boundary stop after next original note')
    provider = Provider()
    def sdk(request):
        wire = json.loads(request.content)
        response = provider.complete(**wire)
        response['system_fingerprint'] = run2.MODEL_FINGERPRINT
        fields = wire['tools'][0]['function']['parameters']['properties']
        if 'should_evolve' in fields:
            response['choices'][0]['message']['tool_calls'][0]['function']['arguments'] = json.dumps({
                'should_evolve': False, 'actions': [], 'suggested_connections': [],
                'tags_to_update': [], 'new_context_neighborhood': [], 'new_tags_neighborhood': []})
        return httpx.Response(200, json=response)
    def controller(**kw):
        return create_deepseek_controller(**kw, http_transport=httpx.MockTransport(sdk))
    def factory(controller, counter, condition):
        assert condition == 'full'
        module = original_memory_module()
        module.SimpleEmbeddingRetriever = Retriever
        module.print = lambda *a, **kw: None
        return make_agent_factory(ROOT, memory_module=module,
            controller_factory=lambda observer: controller(observer), token_counter=counter)
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'offline-placeholder')
    phase = run2.execute_phase(child, campaign, preflight, assets, root=root,
        observer=StopAfterNextNote(), verify_observations=observed, verify_results=experiments,
        controller_factory=controller, factory_builder=factory,
        scorer=AuthorScorer(ROOT, dependencies=dependencies()),
        token_counter=TokenCounter(str.split, 'offline', 'fixture'))
    directory = root / 'artifacts/run2/runs' / phase['run_id']
    events = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    generated = [e for e in events if e['type'] == 'generation']
    assert [e['stage'] for e in generated[:2]] == ['metadata', 'shared_decision']
    original_events = [json.loads(line) for line in (parent / 'events.jsonl').read_text().splitlines()]
    assert generated[0]['prompt'] == [e for e in original_events if e['type'] == 'generation'][-1]['prompt']
    outcomes = [e for e in events if e['type'] == 'evolution_outcome']
    assert outcomes[0]['turn_id'] == 'D10:11'
    assert len(provider.requests) == (1212 if complete else 2)
    assert phase['status'] == ('degraded' if complete else 'incomplete')
    assert phase['total_memory_notes'] == (675 if complete else 228)
    assert phase['evolution_counter'] == 226
    assert phase['cell_budget']['unknown_attempts'] == 1
    assert phase['cell_budget']['unadjudicated_unknown_attempts'] == 0
    assert phase['campaign_budget']['unknown_attempts'] == 1
    assert phase['campaign_budget']['unadjudicated_unknown_attempts'] == 0
    if complete:
        build = next(e['build_id'] for e in events if e['type'] == 'build_complete')
        saved = json.loads((root / 'artifacts/run2/cache' / build / 'state.json').read_text())
        assert phase['usable_for_next_phase'] is True and phase['completed_questions'] == 158
        assert len(outcomes) == 448 and len({e['turn_id'] for e in outcomes}) == 448
        assert phase['cell_budget']['logical_calls'] == 1666
        assert phase['cell_budget']['physical_attempts'] == 1667
        next_plan = run2.plan_phase(campaign, preflight, assets, root=root, condition='full',
            conversation_id='conv-49', financial_adjudication=financial, support_reference=reference)
        next_permit = run2.Run2Permit(approve(next_plan), root, campaign)
        assert next_permit.campaign_summary()['unknown_attempts'] == 1
        assert next_permit.campaign_summary()['unadjudicated_unknown_attempts'] == 0
        assert next_permit.campaign_summary()['charged_or_reserved_microusd'] == 1095741
        logical = next_permit.start_logical('metadata')
        assert logical == 1667
        attempt = next_permit.reserve_attempt(logical, {'model': 'deepseek-flash',
            'endpoint': 'https://api.deepseek.com/beta/chat/completions', 'max_tokens': 1000,
            'temperature': .7, 'thinking': 'disabled', 'stream': False,
            'provider_contract_policy': 'canonical-index-strings-v1'})
        next_permit.settle(attempt, None)
        assert next_permit.campaign_summary()['unknown_attempts'] == 2
        assert next_permit.campaign_summary()['unadjudicated_unknown_attempts'] == 1
        assert next_permit.campaign_summary()['charged_or_reserved_microusd'] == 1411514
        with pytest.raises(BudgetStop, match='Unknown charge'):
            next_permit.start_logical('metadata')
    else:
        saved = json.loads((directory / 'partial-memory.json').read_text())['state']
    assert saved['notes'][:227] == original_state['notes']
    assert saved['retriever']['embeddings'][:227] == original_state['retriever']['embeddings']
    assert saved['outcomes'][:227] == original_state['outcomes']
    assert all(hashlib.sha256((parent / name).read_bytes()).hexdigest() == digest
               for name, digest in original_inventory.items())


@pytest.mark.parametrize('tamper', ['source', 'preflight', 'both', None])
def test_fresh_cell_execution_checks_approved_runtime_before_admission(candidate, tamper):
    root, campaign, sources, preflight, financial, reference, assets = candidate
    plan = approve(run2.plan_phase(campaign, preflight, assets, root=root, condition='full',
        conversation_id='conv-49', financial_adjudication=financial, support_reference=reference))
    binding = plan['binding']
    if tamper in ('source', 'both'):
        binding['source_sha256'] = binding['support_migration']['candidate_source_sha256'] = '1' * 64
    if tamper in ('preflight', 'both'):
        binding['preflight_sha256'] = binding['support_migration']['candidate_preflight_sha256'] = '2' * 64
    ledger = root / 'artifacts/run2/budget.sqlite'
    before = ledger.read_bytes()
    def no_client(**kwargs):
        pytest.fail('Admission failure must precede client creation or transmission')
    # With valid pins, execution reaches the existing cell-seriality guard:
    # this fixture intentionally retains the original incomplete first cell.
    expected = 'approved runtime' if tamper else 'fresh, unique and serial'
    with pytest.raises(BudgetStop, match=expected):
        run2.execute_phase(plan, campaign, preflight, assets, root=root, observer=object(),
            verify_observations=lambda *a: None, verify_results=lambda *a: None,
            controller_factory=no_client)
    assert ledger.read_bytes() == before
    assert not (root / 'artifacts/run2/runs' / plan['run_id']).exists()


def test_observed_child_unknown_usage_stops_before_sdk_retransmission(evidence):
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    migration = child['binding']['support_migration']
    migration.update(policy=incident.OBSERVED_MIGRATION_POLICY,
        changed_files=sorted(incident.OBSERVED_FILES), observability={
            'policy':'run2-audit-essential-v1','gate_sha256':'a'*64,
            'credential_receipt_sha256':'b'*64,'execution_script_sha256':'c'*64})
    permit = run2.Run2Permit(child, root, campaign)
    logical = permit.start_logical('metadata')
    request = {'model':'deepseek-flash','endpoint':'https://api.deepseek.com/beta/chat/completions',
        'max_tokens':1000,'temperature':.7,'thinking':'disabled','stream':False,
        'provider_contract_policy':'canonical-index-strings-v1'}
    attempt = permit.reserve_attempt(logical, request)
    permit.settle(attempt, None)
    with pytest.raises(BudgetStop, match='Unknown charge'):
        permit.reserve_attempt(logical, request)
    assert permit.summary()['physical_attempts'] == 1
    assert permit.cell_summary()['unknown_attempts'] == 2
    assert permit.cell_summary()['charged_or_reserved_microusd'] == 1044837 + 315773


def test_observed_admission_database_failure_cannot_enter_sdk_retry(evidence, monkeypatch):
    import httpx
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.contracts import load_author_contracts
    from amem_repro.config import RUN2_CONFIG
    root, campaign = evidence
    financial = incident.verify_financial_adjudication(
        approve(incident.plan_financial_adjudication(root=root, campaign=campaign)),
        root=root, campaign=campaign)
    child = approved_child(root, campaign, financial)
    child['binding']['support_migration'].update(policy=incident.OBSERVED_MIGRATION_POLICY,
        changed_files=sorted(incident.OBSERVED_FILES), observability={
            'policy':'run2-audit-essential-v1','gate_sha256':'a'*64,
            'credential_receipt_sha256':'b'*64,'execution_script_sha256':'c'*64})
    permit = run2.Run2Permit(child, root, campaign)
    original = incident.unknown_counts
    checks = []
    def fault(db, receipt=None):
        checks.append(1)
        if len(checks) == 2:  # after logical admission, inside physical precheck
            raise sqlite3.OperationalError('synthetic observed admission failure')
        return original(db, receipt)
    monkeypatch.setattr(incident, 'unknown_counts', fault)
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'offline-placeholder')
    sent = []
    def transport(request):
        sent.append(request)
        pytest.fail('Financial precheck fault must prevent transmission')
    controller = create_deepseek_controller(paid_authorized=True, phase_permit=permit,
        generation_config=RUN2_CONFIG, provider_contract_policy='canonical-index-strings-v1',
        http_transport=httpx.MockTransport(transport))
    try:
        with pytest.raises(BudgetStop, match='Attempt admission failed'):
            controller.get_completion('next original metadata', load_author_contracts()['metadata'])
        assert not sent and len(checks) == 2
        assert permit.summary()['halted'] == 'attempt_admission_failed'
        assert permit.summary()['halt_persisted'] is True
        assert permit.summary()['physical_attempts'] == 0
    finally:
        controller.client.close()
