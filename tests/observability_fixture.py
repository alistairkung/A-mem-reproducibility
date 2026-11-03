"""Explicit synthetic LLM fixture through the actual author runner, never benchmark data.

The optional runtime-assets path uses the same local embeddings and metric models
as paid execution. The default keeps unit tests small with the existing deterministic
model-service dependencies. Neither option can transmit to an LLM: HTTPX handles
every provider request in-process and the provider credential is a placeholder.
"""
import copy
import json
import os
from pathlib import Path
from unittest.mock import patch

import httpx

from amem_repro.actions import make_action_agent_factory
from amem_repro.adapter import create_deepseek_controller
from amem_repro.author import make_agent_factory
from amem_repro.config import load_config, source_fingerprint
from amem_repro.manifests import build_manifest
from amem_repro.measurements import TokenCounter
from amem_repro.runner import run_manifest
from amem_repro.replay import ReplayController
from amem_repro.scoring import AuthorScorer, rescore_records
from test_foundation import Provider, original_memory_module
from test_scoring import dependencies

ROOT = Path(__file__).resolve().parents[1]


def run_fixture(directory, *, observer=None, condition='full', fail_decision=None,
                config=None, controller_options=None, use_runtime_assets=False,
                token_counter=None, boundary_check=None, records=None):
    """Return local evidence for the18-turn/four-question smoke manifest.

    The response selected by fail_decision has a literal incomplete argument string
    and a length marker. It is a labelled failure fixture, not a repaired history.
    """
    directory = Path(directory)
    provider = Provider()
    decision_count = 0

    def handle(request):
        nonlocal decision_count
        body = json.loads(request.content)
        response = provider.complete(**body)
        fields = body['tools'][0]['function']['parameters']['properties']
        if 'should_evolve' in fields:
            decision_count += 1
            if fail_decision == decision_count:
                response['choices'][0]['finish_reason'] = 'length'
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments'] = '{"should_evolve":true,"actions":['
                response['usage']['completion_tokens'] = body['max_tokens']
            elif decision_count > 1:
                function = response['choices'][0]['message']['tool_calls'][0]['function']
                value = json.loads(function['arguments'])
                value['suggested_connections'] = [str(i) for i in value['suggested_connections']]
                function['arguments'] = json.dumps(value)
        return httpx.Response(200, json=response)

    controllers = []
    shared_replay = None

    def controller(record):
        nonlocal shared_replay
        if records is not None:
            if shared_replay is None:
                shared_replay = ReplayController(records, observer=record,
                                                 provider_contract_policy='canonical-index-strings-v1',
                                                 **(controller_options or {}))
            value = shared_replay
        else:
            value = create_deepseek_controller(
                paid_authorized=True, observer=record, http_transport=httpx.MockTransport(handle),
                provider_contract_policy='canonical-index-strings-v1', **(controller_options or {}))
        controllers.append(value)
        return value

    scorer = AuthorScorer(ROOT, dependencies=None if use_runtime_assets else dependencies())
    factory_fn = make_agent_factory if condition == 'full' else make_action_agent_factory
    options = {} if condition == 'full' else {'condition': condition}
    factory = factory_fn(
        ROOT, memory_module=None if use_runtime_assets else original_memory_module(),
        controller_factory=controller,
        token_counter=token_counter or TokenCounter(str.split, 'whitespace-fixture-only', 'v1'),
        **options)
    try:
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'offline-placeholder'}):
            summary = run_manifest(
                ROOT/'data/locomo10.json', build_manifest(ROOT/'data/locomo10.json', 'smoke'),
                config or load_config(), output_dir=directory/'run', cache_root=directory/'cache',
                source_hashes=source_fingerprint(ROOT), condition=condition,
                agent_factory=factory, scorer=scorer, observer=observer,
                run_id=(observer.metadata['run_id'] if observer else 'uninstrumented-fixture'),
                provider_contract_policy='canonical-index-strings-v1', boundary_check=boundary_check)
    finally:
        for value in controllers:
            if hasattr(value, 'client'):
                value.client.close()
    if records is not None:
        for value in controllers:
            value.finish()
    events = [json.loads(line) for line in (directory/'run/events.jsonl').read_text().splitlines()]
    results = [event['result'] for event in events if event['type'] == 'question_result']
    states = [json.loads(path.read_text()) for path in (directory/'cache').glob('*/state.json')]
    return {'summary': summary, 'requests': copy.deepcopy(provider.requests),
            'events': events, 'results': results, 'views': rescore_records(results, scorer),
            'states': states, 'network_llm_requests': 0,
            'replay_positions': [v.position for v in controllers] if records is not None else [],
            'fixture_kind': 'synthetic-provider-real-author-runner'}
