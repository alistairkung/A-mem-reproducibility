"""Essential export changes neither scientific outputs nor saved metric identities."""
import copy
import hashlib
import json
import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from amem_repro.observation_policy import POLICY_ID, should_export_span, release_binding
from amem_repro.observability import LangfuseObserver
from amem_repro.reporting import export_experiments
from amem_repro.replay import memory_view
from observability_fixture import run_fixture
from test_observability import Client, identity
import test_reporting as reporting_fixtures


def test_real_runner_export_is_passive_and_preserves_original_scores(tmp_path):
    old = LangfuseObserver(Client(), identity('legacy-policy'))
    new = LangfuseObserver(Client(), {**identity('essential-policy'), 'observability_policy': POLICY_ID})
    before = run_fixture(tmp_path / 'before', observer=old)
    after = run_fixture(tmp_path / 'after', observer=new)
    assert before['requests'] == after['requests']
    assert memory_view(before['states'][0]) == memory_view(after['states'][0])
    assert before['views'] == after['views'] and before['results'] == after['results']
    a, b = old.finish(), new.finish()
    assert a['scores'] and b['scores'] == []
    assert len(a['observations']) == len(b['observations'])
    questions = [r for r in b['observations'] if r['name'] == 'A-MEM/question']
    scorers = [r for r in b['observations'] if r['name'] == 'author-scoring']
    for score in a['scores']:
        q = next(r for r in questions if r['metadata']['question_id'] == score['metadata']['question_id'])
        s = next(r for r in scorers if r['trace_id'] == q['trace_id'])
        assert q['output']['metrics'][score['name']] == s['output'][score['name']] == score['value']
    generations = [r for r in b['observations'] if r['type'] == 'generation']
    for generation in generations:
        assert generation['input']['prompt']
        assert generation['output']['provider_arguments']
        assert generation['output']['algorithm_input_modified'] is False
        assert 'wire_request' not in generation['metadata']
        assert len(generation['metadata']['wire_request_sha256']) == 64
        assert 'budget_logical_id' not in generation['metadata']['local_evidence']
        assert generation['usage_details']['total'] > 0
    assert after['network_llm_requests'] == 0


def sdk_client():
    from langfuse import Langfuse
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key='pk-lf-offline-' + uuid.uuid4().hex, secret_key='offline-placeholder',
        base_url='https://langfuse.invalid', tracer_provider=TracerProvider(),
        span_exporter=exporter, should_export_span=should_export_span)
    return client, exporter


def test_sdk_filter_keeps_every_saved_score_on_a_visible_experiment_root():
    from langfuse import LangfuseOtelSpanAttributes as A
    client, exporter = sdk_client()
    views = reporting_fixtures.ReportingTests().views()
    legacy = copy.deepcopy(next(iter(views.values())))
    legacy['scoring_policy'] = 'author-legacy-c5-v1'
    views[legacy['scoring_policy']] = legacy
    original = copy.deepcopy(views)
    scores = []
    try:
        with patch.object(client, '_get_project_id', return_value='offline-project'), \
             patch.object(client, 'create_score', side_effect=lambda **kw: scores.append(kw)):
            export_experiments(views, client=client, export_authorized=True,
                metadata={**identity(), 'observability_policy': POLICY_ID,
                          'provider_contract_policy': 'strict-original-v1'})
        spans = list(exporter.get_finished_spans())
        assert len(spans) == 4 and len(scores) == 2
        assert {s.name for s in spans} == {'experiment-item-run', 'experiment-item-task'}
        by_id = {f'{s.context.span_id:016x}':s for s in spans}
        for score in scores:
            subject = by_id[score['observation_id']]
            assert subject.attributes[A.EXPERIMENT_ITEM_ROOT_OBSERVATION_ID] == score['observation_id']
            assert f'{subject.context.trace_id:032x}' == score['trace_id']
            assert subject.attributes[A.OBSERVATION_OUTPUT] == 'saved answer'
            assert score['value'] == .5
        assert all(not s.parent or f'{s.parent.span_id:016x}' in by_id for s in spans)
        assert views == original
    finally:
        client.shutdown()


def test_failed_import_retains_error_and_parent_group_without_a_fake_score():
    from langfuse import LangfuseOtelSpanAttributes as A
    client, exporter = sdk_client()
    def failure(**kwargs):
        raise RuntimeError('synthetic import failure')
    try:
        with patch.object(client, '_get_project_id', return_value='offline-project'), \
             patch.object(client, 'create_score') as score:
            client.run_experiment(name='offline', data=[{'input':'q'}], task=lambda **kw:'saved',
                evaluators=[failure], metadata={'observability_policy':POLICY_ID,
                                               'execution_mode':'imported_results'})
            client.flush()
            spans = list(exporter.get_finished_spans())
            assert len(spans) == 4 and score.call_count == 0
            by_name = {s.name:s for s in spans}
            assert by_name['failure'].attributes[A.OBSERVATION_LEVEL] == 'ERROR'
            assert json.loads(by_name['experiment-item-evaluation'].attributes[A.OBSERVATION_OUTPUT])['failed_evaluator_count'] == 1
    finally:
        client.shutdown()


@pytest.mark.parametrize('level', ['ERROR', 'WARNING'])
def test_filter_does_not_remove_failures_or_unscoped_author_scoring(level):
    from langfuse import LangfuseOtelSpanAttributes as A
    span = SimpleNamespace(name='author-scoring', instrumentation_scope=SimpleNamespace(name='langfuse-sdk'),
                           attributes={A.OBSERVATION_TYPE:'evaluator'})
    assert should_export_span(span)
    span.attributes.update({A.EXPERIMENT_ID:'experiment', A.OBSERVATION_LEVEL:level,
        A.EXPERIMENT_METADATA:json.dumps({'observability_policy':POLICY_ID,
                                          'execution_mode':'imported_results'})})
    assert should_export_span(span)


def test_release_gate_requires_exact_source_evidence_and_revocation(tmp_path):
    from amem_repro.observation_policy import GATE_DIRECTORY, LAUNCHER
    gate_path = tmp_path / GATE_DIRECTORY / ('a'*64)
    gate_path.mkdir(parents=True)
    member = gate_path / 'proof.json'
    member.write_text('{"verified":true}')
    script = tmp_path / LAUNCHER
    script.parent.mkdir(); script.write_text('offline reviewed launcher')
    credential = tmp_path / 'artifacts/run2-observed-recovery/credential-rotation-verified.json'
    credential.parent.mkdir(parents=True)
    credential.write_text(json.dumps({k:True for k in ('new_authentication_verified',
        'read_existing_trace_verified','original_1_nov_key_absent')}))
    gate = {'observability_policy':POLICY_ID,'source_sha256':'a'*64,'network_llm_requests':0,
        **{k:True for k in ('real_runner','remote_observations_verified','experiments_verified',
            'replay_equivalence','output_exhaustion_verified','tracing_failure_verified')},
        'files':{'proof.json':hashlib.sha256(member.read_bytes()).hexdigest()}}
    (gate_path/'receipt.json').write_text(json.dumps(gate))
    assert release_binding(tmp_path, 'a'*64)['policy'] == POLICY_ID
    with pytest.raises((ValueError, FileNotFoundError)): release_binding(tmp_path, 'b'*64)
    member.write_text('altered')
    with pytest.raises(ValueError): release_binding(tmp_path, 'a'*64)


def test_export_ceiling_latches_a_failure_instead_of_sampling_or_silent_loss(monkeypatch):
    from amem_repro import observation_policy
    from amem_repro.observability import ObservabilityError
    monkeypatch.setattr(observation_policy, 'MAX_PHASE_OBSERVATIONS', 1)
    client = Client()
    observer = LangfuseObserver(client, {**identity(), 'observability_policy':POLICY_ID})
    observer({'type':'run_start','configuration':{},'conversation_ids':['conv-26']})
    event = {'type':'memory_turn_start','turn_id':'D1:1','input':{'content':'unchanged'}}
    saved = copy.deepcopy(event)
    observer(event)
    assert len(client.spans) == 1 and event == saved
    with pytest.raises(ObservabilityError): observer.assert_healthy()
