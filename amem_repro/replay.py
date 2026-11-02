"""Ordered response replay through the existing strict adapter, without an SDK/client.

No paid factory, environment credentials, transport or model is constructed here.
Request mismatches escape the author's broad Exception fallbacks and latch terminally.
"""
from __future__ import annotations

import copy
from types import SimpleNamespace

from .adapter import DeepSeekController, AdapterError
from .config import fingerprint, STRICT_PROVIDER_POLICY


class ReplayMismatch(BaseException):
    """A regression failure, never a substitute model response or author fallback."""


class ReplayController:
    def __init__(self, records, *, provider_contract_policy=STRICT_PROVIDER_POLICY, observer=None):
        self._records = copy.deepcopy(list(records))
        self._position = 0
        self._failure = None
        self.observations = []
        self.observer = observer
        self._adapter = DeepSeekController(
            SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=self._create))),
            observer=self._observe, provider_contract_policy=provider_contract_policy,
        )
        for record in self._records:
            if (record.get('type') != 'generation' or len(record.get('attempts', [])) != 1
                    or record.get('error_type') not in (None, 'AdapterError')):
                self._fail('Only recorded transmitted completions/adapter rejections can replay')

    def _observe(self, event):
        self.observations.append(copy.deepcopy(event))
        if self.observer is not None:
            self.observer(event)

    @property
    def position(self):
        return self._position

    @property
    def observer_errors(self):
        return self._adapter.observer_errors

    def _fail(self, reason):
        self._failure = self._failure or f'Replay request {self._position}: {reason}'
        raise ReplayMismatch(self._failure)

    def _next(self):
        if self._failure:
            raise ReplayMismatch(self._failure)
        if self._position >= len(self._records):
            self._fail('unexpected request after exhaustion')
        return self._records[self._position]

    def _create(self, **kwargs):
        record = self._next()
        wire = copy.deepcopy(kwargs)
        wire.update(wire.pop('extra_body'))
        if fingerprint(wire) != fingerprint(record['attempts'][0]['request_body']):
            self._fail('wire generation settings/messages/schema differ')
        # A retry is not a second logical response. The archive preserves the final
        # received response; T5 conv-50 has exactly one physical attempt per call.
        response = copy.deepcopy(record['provider_response'])
        self._position += 1
        return response

    def _check_output(self, record):
        observed = self.observations[-1]
        for name in ('stage', 'output', 'error_type', 'raw_schema_valid',
                     'validation_copy_schema_valid', 'compatibility_deviation',
                     'model', 'endpoint', 'temperature', 'max_tokens', 'thinking',
                     'provider_contract_policy'):
            if observed.get(name) != record.get(name):
                self._fail(f'recorded {name} differs from adapter outcome')

    def get_completion(self, prompt, response_format, temperature=0.7, **unexpected):
        if unexpected:
            self._fail('unsupported generation arguments')
        record = self._next()
        contracts = self._adapter.contracts
        if (record['stage'] not in contracts or response_format != contracts[record['stage']]
                or response_format != record['response_format'] or prompt != record['prompt']
                or temperature != record['temperature']):
            self._fail('stage, prompt, schema or temperature differs')
        try:
            result = self._adapter.get_completion(prompt, response_format, temperature)
        except AdapterError:
            self._check_output(record)
            if record.get('error_type') != 'AdapterError':
                self._fail('unexpected rejected output')
            raise  # Preserve the original ordinary exception/fallback boundary.
        except Exception as error:
            self._fail(f'unexpected adapter failure: {type(error).__name__}')
        else:
            self._check_output(record)
            if record.get('error_type'):
                self._fail('recorded rejection was unexpectedly accepted')
            return result  # Original argument string, byte-for-byte unchanged.

    def finish(self):
        if self._failure:
            raise ReplayMismatch(self._failure)
        if self._position != len(self._records):
            self._fail('missing requests; recorded responses remain')


def memory_view(state):
    """Comparison copy only: UUID identities -> insertion indices; omit wall-clock access time.

    Dataset/conversation timestamps, links, arrays, metadata, corpus and embeddings
    remain exact. Build-failure provenance is checked separately from memory state.
    """
    value = copy.deepcopy(state)
    value.pop('build_failures', None)
    identities = {note['key']: f'note:{index}' for index, note in enumerate(value['notes'])}
    for note in value['notes']:
        if note['attributes']['id'] != note['key']:
            raise ReplayMismatch('Note identity is inconsistent')
        note['key'] = identities[note['key']]
        note['attributes']['id'] = note['key']
        note['attributes'].pop('last_accessed', None)
    for outcome in value['outcomes']:
        outcome['changed_existing_note_ids'] = [identities[key] for key in outcome['changed_existing_note_ids']]
    return value
