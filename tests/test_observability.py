"""Real-runner tracing is passive; Langfuse stores observations, never generates."""
import copy
import hashlib
import json
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from amem_repro.observability import LangfuseObserver
from amem_repro.observability import ObservabilityError
from amem_repro.budget import BudgetStop
from amem_repro.replay import memory_view
from observability_fixture import run_fixture


class Span:
    def __init__(self, client, value):
        self.client = client
        self.value = value
        self.id = f'{len(client.spans) + 1:016x}'
        self.trace_id = value['trace_context']['trace_id']
        value['id'] = self.id
        value['trace_id'] = self.trace_id
        self.ended = False

    def update(self, **value):
        self.value.update(copy.deepcopy(value))
        return self

    def end(self):
        self.ended = True
        return self


class Client:
    def __init__(self):
        self.spans = []
        self.scores = []
        self.flushes = 0

    def start_observation(self, **value):
        span = Span(self, copy.deepcopy(value))
        self.spans.append(span)
        return span

    def create_score(self, **value):
        self.scores.append(copy.deepcopy(value))

    def flush(self):
        self.flushes += 1


def identity(run_id='offline-observability'):
    return {'campaign_id': 'gate-b-offline', 'condition': 'full', 'population': 'smoke',
            'manifest_sha256': 'a' * 64, 'repetition': 0, 'run_id': run_id,
            'conversation_id': 'conv-26', 'provider_contract_policy': 'canonical-index-strings-v1',
            'execution_mode': 'offline_fixture'}


def test_live_generation_retains_original_arguments_usage_and_unit_identity():
    client = Client()
    observer = LangfuseObserver(client, identity())
    observer({'type': 'memory_turn_start', 'turn_id': 'D1:1', 'conversation_id': 'conv-26',
              'input': {'content': 'original content', 'timestamp': 'fixed'}})
    event = {'type': 'generation', 'stage': 'metadata', 'prompt': 'unchanged prompt',
             'response_format': {'unchanged': 'schema'}, 'model': 'deepseek-flash',
             'temperature': .7, 'max_tokens': 1000, 'thinking': 'disabled',
             'turn_id': 'D1:1', 'conversation_id': 'conv-26', 'output': None,
             'usage': None, 'attempts': [], 'error_type': None}
    observer.begin_generation(event)
    raw = '{ "context": "verbatim" }'
    event.update(output=raw, usage={'prompt_tokens': 100, 'completion_tokens': 10},
                 duration_seconds=.25, request_id='offline-response',
                 attempts=[{'attempt': 1, 'status_code': 200,
                            'usage': {'prompt_tokens': 100, 'completion_tokens': 10}}])
    observer(event)
    observer({'type': 'evolution_outcome', 'turn_id': 'D1:1', 'counter_before': 0,
              'counter_after': 0, 'changed_existing_note_ids': []})
    receipt = observer.finish()
    assert receipt['errors'] == []
    assert client.flushes == 1
    generation = next(s for s in client.spans if s.value['as_type'] == 'generation')
    parent = next(s for s in client.spans if s.value['name'] == 'A-MEM/memory-turn')
    assert generation.ended and parent.ended
    assert generation.value['trace_context']['parent_span_id'] == parent.id
    assert generation.value['input'] == {'prompt': 'unchanged prompt', 'response_format': {'unchanged': 'schema'}}
    assert generation.value['output']['provider_arguments'] == raw
    assert generation.value['output']['accepted'] is True
    assert generation.value['output']['algorithm_input_modified'] is False
    assert generation.value['usage_details'] == {'input': 100, 'output': 10, 'total': 110}
    assert generation.value['cost_details']['total'] == .000042
    assert generation.value['metadata']['turn_id'] == 'D1:1'
    assert generation.value['metadata']['campaign_id'] == 'gate-b-offline'
    assert generation.value['metadata']['observed_generation_duration_seconds'] == .25
    assert receipt['observations'][-1]['id'] == generation.id
    observer.assert_healthy()
    assert receipt['cloud_visibility_verified'] is False
    assert 'wire_request' not in generation.value['metadata']  # No captured physical request.


def test_actual_runner_logs_exact_safe_wire_request_without_changing_parser_input_or_calls(tmp_path):
    client = Client();observer = LangfuseObserver(client, identity('wire-request-fixture'))
    traced = run_fixture(tmp_path/'traced', observer=observer)
    plain = run_fixture(tmp_path/'plain')
    receipt = observer.finish()
    generations = [row for row in receipt['observations'] if row['type'] == 'generation']
    events = [event for event in traced['events'] if event['type'] == 'generation']
    assert receipt['errors'] == []
    assert traced['requests'] == plain['requests']
    assert len(generations) == len(traced['requests']) == 44
    assert [row['metadata']['wire_request'] for row in generations] == traced['requests']
    assert [span.value['metadata']['wire_request'] for span in client.spans
            if span.value['as_type'] == 'generation'] == traced['requests']
    for row, event in zip(generations, events):
        assert row['input'] == {'prompt': event['prompt'], 'response_format': event['response_format']}
        assert row['metadata']['wire_request']['messages'][0]['role'] == 'system'
        assert row['metadata']['wire_request']['tool_choice']['type'] == 'function'
        assert row['output']['provider_arguments'] == event['output']
        assert row['output']['parser_input_sha256'] == hashlib.sha256(event['output'].encode()).hexdigest()
        assert row['output']['algorithm_input_modified'] is False


def test_unknown_attempt_usage_is_explicitly_partial_and_never_invented_as_zero_cost():
    client = Client();observer = LangfuseObserver(client, identity())
    observer({'type': 'generation', 'stage': 'metadata', 'prompt': 'same prompt',
              'response_format': {}, 'model': 'deepseek-flash', 'temperature': .7,
              'max_tokens': 1000, 'thinking': 'disabled', 'output': '{}', 'error_type': None,
              'usage': {'prompt_tokens': 100, 'completion_tokens': 10},
              'attempts': [{'attempt': 1, 'usage': None, 'error_type': 'HTTPStatusError'},
                           {'attempt': 2, 'usage': {'prompt_tokens': 100, 'completion_tokens': 10}}]})
    receipt = observer.finish()
    generation = next(s.value for s in client.spans if s.value['as_type'] == 'generation')
    assert generation['usage_details'] == {'input': 100, 'output': 10, 'total': 110}
    assert 'cost_details' not in generation
    assert generation['metadata']['unknown_usage_attempts'] == 1
    assert generation['metadata']['cost_complete'] is False
    assert generation['metadata']['usage_complete'] is False
    assert generation['metadata']['ledger_reservations_authoritative'] is True
    assert receipt['errors'] == []


def test_response_retained_before_failed_settlement_remains_visible_without_claiming_parser_acceptance():
    client = Client();observer = LangfuseObserver(client, identity())
    raw = '{ "answer": "received before settlement failed" }'
    response = {'id': 'settlement-evidence', 'model': 'deepseek-flash',
                'system_fingerprint': 'offline', 'usage': {'prompt_tokens': 100, 'completion_tokens': 10},
                'choices': [{'finish_reason': 'tool_calls', 'message': {'tool_calls': [
                    {'function': {'arguments': raw}}]}}]}
    observer({'type': 'generation', 'stage': 'answer', 'prompt': 'unchanged question',
              'response_format': {}, 'model': 'deepseek-flash', 'temperature': .7,
              'max_tokens': 1000, 'thinking': 'disabled', 'output': None,
              'usage': None, 'error_type': 'BudgetStop',
              'attempts': [{'attempt': 1, 'usage': response['usage'], 'response_body': response,
                            'error_type': 'BudgetStop'}]})
    observer.finish()
    generation = next(s.value for s in client.spans if s.value['as_type'] == 'generation')
    assert generation['output']['provider_arguments'] == raw
    assert generation['output']['accepted'] is False
    assert generation['output']['parser_input_sha256'] is None
    assert generation['metadata']['request_id'] == 'settlement-evidence'


@pytest.mark.parametrize('condition', ['full', 'neither', 'linking_only', 'evolution_only'])
def test_actual_runner_traces_every_stage_without_changing_memory_requests_or_scores(tmp_path, condition):
    metadata = identity();metadata['condition'] = condition
    client = Client();observer = LangfuseObserver(client, metadata)
    traced = run_fixture(tmp_path/'traced', observer=observer, condition=condition)
    untraced = run_fixture(tmp_path/'untraced', condition=condition)
    receipt = observer.finish()
    assert receipt['errors'] == []
    assert len(traced['requests']) == len(untraced['requests']) == 44
    assert traced['requests'] == untraced['requests']
    assert memory_view(traced['states'][0]) == memory_view(untraced['states'][0])
    assert traced['views'] == untraced['views']
    spans = [s.value for s in client.spans]
    generations = [s for s in spans if s['as_type'] == 'generation']
    assert len(generations) == 44
    assert all(s['metadata'].get('turn_id') for s in generations[:36])
    assert all(s['metadata'].get('question_id') for s in generations[36:])
    assert all('turn_id' not in s['metadata'] for s in generations[36:])
    assert len([s for s in spans if s['as_type'] == 'retriever']) == 4
    assert len([s for s in spans if s['as_type'] == 'evaluator']) == 4
    actions = {s['name'] for s in spans if s['as_type'] == 'tool'}
    assert actions == {'full': {'strengthen', 'update_neighbor'}, 'neither': set(),
                       'linking_only': {'strengthen'}, 'evolution_only': {'update_neighbor'}}[condition]
    for s in spans:
        if s['as_type'] in ('tool', 'retriever'):
            assert s['input'] is not None and s['output'] is not None
    assert len(client.scores) == sum(len(r['metrics']) for r in traced['results'])


def test_ordered_response_replay_is_identical_with_and_without_actual_runner_tracing(tmp_path):
    captured = run_fixture(tmp_path/'captured')
    records = [e for e in captured['events'] if e['type'] == 'generation']
    original_records = copy.deepcopy(records)
    observer = LangfuseObserver(Client(), identity('ordered-replay-fixture'))
    plain = run_fixture(tmp_path/'plain-replay', records=records)
    traced = run_fixture(tmp_path/'traced-replay', observer=observer, records=records)
    receipt = observer.finish()
    assert receipt['errors'] == []
    assert traced['replay_positions'] == plain['replay_positions'] == [44, 44]
    assert traced['requests'] == plain['requests'] == []
    assert records == original_records
    assert memory_view(traced['states'][0]) == memory_view(plain['states'][0])
    assert traced['views'] == plain['views'] == captured['views']
    generations = [r for r in receipt['observations'] if r['type'] == 'generation']
    assert len(generations) == 44
    assert [r['output']['provider_arguments'] for r in generations] == [r['output'] for r in records]


@pytest.mark.parametrize('failure', ['start', 'update', 'end', 'score', 'flush'])
def test_export_failures_cannot_change_original_outputs_requests_memory_or_scores(tmp_path, failure):
    class BrokenClient(Client):
        def start_observation(self, **value):
            if failure == 'start':
                raise OSError('fixture tracing failure')
            span = super().start_observation(**value)
            def fail(**kwargs):
                raise OSError('fixture tracing failure')
            if failure == 'update':
                span.update = fail
            if failure == 'end':
                span.end = fail
            return span

        def create_score(self, **value):
            if failure == 'score':
                raise OSError('fixture tracing failure')
            super().create_score(**value)

        def flush(self):
            if failure == 'flush':
                raise OSError('fixture tracing failure')
            super().flush()

    observer = LangfuseObserver(BrokenClient(), identity())
    traced = run_fixture(tmp_path/'traced', observer=observer)
    plain = run_fixture(tmp_path/'plain')
    receipt = observer.finish()
    assert receipt['errors']
    assert traced['requests'] == plain['requests']
    assert len(traced['requests']) == 44
    assert memory_view(traced['states'][0]) == memory_view(plain['states'][0])
    assert traced['views'] == plain['views']
    with pytest.raises(ObservabilityError):
        observer.assert_healthy()


def test_tracing_health_stops_at_next_unit_after_preserving_current_memory_operation(tmp_path):
    class FailedGenerationClient(Client):
        def start_observation(self, **value):
            if value['name'] == 'metadata':
                raise OSError('fixture generation tracing unavailable')
            return super().start_observation(**value)

    observer = LangfuseObserver(FailedGenerationClient(), identity())
    with pytest.raises(ObservabilityError):
        run_fixture(tmp_path, observer=observer, boundary_check=observer.assert_healthy)
    observer.finish()
    state = json.loads((tmp_path/'run/partial-memory.json').read_text())['state']
    events = [json.loads(line) for line in (tmp_path/'run/events.jsonl').read_text().splitlines()]
    assert len(state['notes']) == 1
    assert len(state['outcomes']) == 1
    assert state['evo_cnt'] == 1
    assert [e['stage'] for e in events if e['type'] == 'generation'] == ['metadata', 'shared_decision']
    assert events[-1]['type'] == 'run_abort'
    assert events[-1]['turn_id'] == 'D1:2'  # The next unit was rejected, not the completed first one.
    assert not (tmp_path/'cache').exists()


def test_output_exhaustion_is_visible_with_raw_rejection_and_original_fallback(tmp_path):
    client = Client();observer = LangfuseObserver(client, identity())
    def boundary():
        if any(s.value.get('metadata', {}).get('error_type') == 'AdapterError' for s in client.spans):
            raise BudgetStop('synthetic failure stops before another turn')
    with pytest.raises(BudgetStop):
        run_fixture(tmp_path, observer=observer, fail_decision=2, boundary_check=boundary)
    receipt = observer.finish()
    state = json.loads((tmp_path/'run/partial-memory.json').read_text())['state']
    bad = next(s.value for s in client.spans if s.value.get('metadata', {}).get('error_type') == 'AdapterError')
    assert bad['level'] == 'ERROR'
    assert bad['output'] == {'provider_arguments': '{"should_evolve":true,"actions":[',
                             'accepted': False, 'finish_reason': 'length',
                             'parser_input_sha256': None, 'algorithm_input_modified': None}
    assert bad['usage_details']['output'] == 4000
    assert len(state['notes']) == len(state['outcomes']) == 2
    assert state['notes'][-1]['attributes']['links'] == []
    assert state['notes'][-1]['attributes']['tags'] == ['tag']
    assert state['outcomes'][-1]['proposed_decision'] is None
    assert state['outcomes'][-1]['changed_existing_note_ids'] == []
    assert state['evo_cnt'] == 1
    assert receipt['errors'] == []
    assert all(s.ended for s in client.spans)


def test_real_langfuse_sdk_exports_actual_runner_tree_with_no_cloud_or_llm_requests(tmp_path):
    from langfuse import Langfuse
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key='pk-lf-offline-' + uuid.uuid4().hex,
                      secret_key='offline-placeholder', base_url='https://langfuse.invalid',
                      tracer_provider=TracerProvider(), span_exporter=exporter)
    observer = LangfuseObserver(client, identity('real-sdk-offline-fixture'))
    scores = []
    with patch.object(client, 'create_score', side_effect=lambda **kw: scores.append(kw)):
        result = run_fixture(tmp_path, observer=observer)
        receipt = observer.finish()
    exported = list(exporter.get_finished_spans())
    assert receipt['errors'] == []
    assert result['network_llm_requests'] == 0 and len(result['requests']) == 44
    assert len([s for s in exported if s.name in ('metadata', 'shared_decision', 'query_keywords', 'answer')]) == 44
    metadata = next(s for s in exported if s.name == 'metadata')
    output = json.loads(metadata.attributes['langfuse.observation.output'])
    assert output['accepted'] is True
    assert isinstance(output['provider_arguments'], str)
    assert json.loads(output['provider_arguments'])['context'] == 'context'
    assert metadata.parent is not None
    assert metadata.end_time >= metadata.start_time
    assert len(scores) == sum(len(r['metrics']) for r in result['results'])
    assert {f'{s.context.span_id:016x}' for s in exported} == {r['id'] for r in receipt['observations']}
    client.shutdown()
