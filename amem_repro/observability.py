"""Passive Langfuse observations around the existing scientific execution path.

This module never creates an LLM client or evaluates a prediction. SDK failures are
latched for the orchestrator to check between completed memory/QA operations.
Local run journals remain authoritative; a flush is not proof of cloud visibility.
"""
from __future__ import annotations

import copy
import hashlib
import uuid
from contextlib import contextmanager
from decimal import Decimal, ROUND_CEILING

from .config import reject_credentials
from .observation_policy import POLICY_ID


class ObservabilityError(RuntimeError):
    """The campaign must stop at its next safe boundary."""


class LangfuseObserver:
    captures_lifecycle = True

    def __init__(self, client, metadata):
        reject_credentials(metadata)
        required = ('campaign_id', 'condition', 'population', 'manifest_sha256',
                    'repetition', 'run_id', 'conversation_id', 'provider_contract_policy')
        if not isinstance(metadata, dict) or any(k not in metadata for k in required):
            raise ValueError('Tracing requires the complete campaign/cell/run identity')
        self.client = client
        self.metadata = copy.deepcopy(metadata)
        policy = metadata.get('observability_policy')
        if policy is not None and policy != POLICY_ID:
            raise ValueError('Unknown observability export policy')
        self.essential_export = policy == POLICY_ID
        self.session_id = '/'.join(str(metadata[k]) for k in
                                   ('campaign_id', 'condition', 'conversation_id', 'repetition', 'run_id'))
        self.errors = []
        self.observations = []
        self.scores = []
        self._unit = None
        self._phase = None
        self._generation = None
        self._action = None
        self._retrieval = None
        self._pending = {}
        self._finished = False

    def _attempt(self, operation, call):
        try:
            return call()
        except Exception as error:
            self.errors.append({'operation': operation, 'error_type': type(error).__name__})
            return None

    def _metadata(self, event):
        value = copy.deepcopy(self.metadata)
        if self._unit:
            value.update({k: self._unit[1]['metadata'][k] for k in
                          ('turn_id', 'question_id', 'conversation_id')
                          if k in self._unit[1]['metadata']})
        value.update({k: copy.deepcopy(event[k]) for k in
                      ('run_id', 'conversation_id', 'build_id', 'turn_id', 'question_id',
                       'provider_contract_policy', 'scoring_policy') if k in event})
        return value

    @contextmanager
    def _attributes(self):
        from langfuse import propagate_attributes
        with propagate_attributes(session_id=self.session_id,
                                  tags=['A-MEM', str(self.metadata['campaign_id']),
                                        str(self.metadata['condition'])]):
            yield

    def _open(self, name, kind, event, *, input=None, parent=True, **extra):
        if self.essential_export:
            from .observation_policy import MAX_PHASE_OBSERVATIONS
            if len(self.observations) >= MAX_PHASE_OBSERVATIONS:
                raise ObservabilityError('Phase observation ceiling reached; no further export')
        context = ({'trace_id': self._unit[0].trace_id,
                    'parent_span_id': self._unit[0].id} if parent and self._unit
                   else {'trace_id': uuid.uuid4().hex})
        value = {'trace_context': context, 'name': name, 'as_type': kind,
                 'input': copy.deepcopy(input), 'metadata': self._metadata(event), **extra}
        reject_credentials(value)
        with self._attributes():
            span = self.client.start_observation(**value)
        row = {'id': span.id, 'trace_id': span.trace_id, 'name': name, 'type': kind,
               'session_id': self.session_id,
               'parent_observation_id': context.get('parent_span_id'),
               'input': copy.deepcopy(input), 'output': None,
               'metadata': copy.deepcopy(value['metadata']), 'level': 'DEFAULT'}
        row.update({k: copy.deepcopy(extra[k]) for k in ('model', 'model_parameters') if k in extra})
        self.observations.append(row)
        self._pending[span.id] = (span, row)
        return span, row

    def _complete(self, observation, *, output=None, metadata=None, level=None, **extra):
        if observation is None:
            return
        span, row = observation
        if metadata:
            row['metadata'].update(copy.deepcopy(metadata))
        if level and {'DEFAULT': 0, 'WARNING': 1, 'ERROR': 2}[level] > \
                {'DEFAULT': 0, 'WARNING': 1, 'ERROR': 2}[row['level']]:
            row['level'] = level
        row.update(output=copy.deepcopy(output), **copy.deepcopy(extra))
        try:
            span.update(output=output, metadata=row['metadata'], level=row['level'], **extra)
        finally:
            try:
                span.end()
            finally:
                self._pending.pop(span.id, None)

    def begin_generation(self, event):
        def start():
            self._generation = self._open(
                event['stage'], 'generation', event,
                input={'prompt': event['prompt'], 'response_format': event['response_format']},
                model=event['model'], model_parameters={k: event[k] for k in
                    ('temperature', 'max_tokens', 'thinking')})
        self._attempt('begin_generation', start)

    def begin_action(self, event):
        self._attempt('begin_action', lambda: self._start_action(event))

    def _start_action(self, event):
        self._action = self._open(event['action'], 'tool', event, input=event.get('input'))

    def begin_retrieval(self, event):
        self._attempt('begin_retrieval', lambda: self._start_retrieval(event))

    def _start_retrieval(self, event):
        self._retrieval = self._open('memory-retrieval', 'retriever', event,
                                     input=event.get('input'))

    def __call__(self, event):
        self._attempt('event:' + str(event.get('type')), lambda: self._observe(event))

    def _observe(self, event):
        reject_credentials(event)
        kind = event['type']
        if kind == 'run_start':
            self._phase = self._open('A-MEM/execution-phase', 'chain', event,
                                    input={'configuration': event.get('configuration'),
                                           'conversation_ids': event.get('conversation_ids')}, parent=False)
        elif kind in ('memory_turn_start', 'question_start'):
            self._unit = self._open('A-MEM/memory-turn' if kind == 'memory_turn_start'
                                    else 'A-MEM/question', 'chain', event,
                                    input=event['input'], parent=False)
        elif kind == 'generation':
            self._generation_result(event)
        elif kind == 'local_action':
            if self._action is None:
                self._start_action(event)
            self._complete(self._action, output=event.get('output'),
                           metadata={'api_calls': 0, 'duration_seconds': event['duration_seconds'],
                                     'timing_method': event['timing_method']})
            self._action = None
        elif kind == 'retrieval':
            if self._retrieval is None:
                self._start_retrieval(event)
            self._complete(self._retrieval, output=event.get('output'), metadata={
                k: copy.deepcopy(v) for k, v in event.items()
                if k not in ('input', 'output', 'type')})
            self._retrieval = None
        elif kind == 'evolution_outcome':
            self._complete(self._unit, output={k: v for k, v in event.items()
                                              if k not in ('type', 'run_id', 'build_id')})
            self._unit = None
        elif kind == 'question_result':
            result = event['result']
            scored = self._open('author-scoring', 'evaluator', event,
                                input={'prediction': result['prediction'],
                                       'reference': result['reference'], 'qa': result['qa']})
            self._complete(scored, output=result['metrics'], metadata={
                'scoring_policy': result['scoring_policy'],
                'metric_failures': result.get('metric_failures', [])})
            if self._unit and not self.essential_export:
                for name, value in result['metrics'].items():
                    score = {'name': name, 'value': value, 'trace_id': self._unit[0].trace_id,
                             'score_id': uuid.uuid4().hex,
                             'observation_id': self._unit[0].id,
                             'metadata': {**self._metadata(event),
                                          'scoring_policy': result['scoring_policy'],
                                          'metric_failures': result.get('metric_failures', [])}}
                    def emit_score(score=score):
                        self.client.create_score(**score)
                        self.scores.append(copy.deepcopy(score))
                    self._attempt('score:' + name, emit_score)
            self._complete(self._unit, output=result)
            self._unit = None
        elif kind == 'failure':
            level = 'WARNING' if event.get('kind') == 'provider_contract_deviation' else 'ERROR'
            failed = self._open('A-MEM/' + str(event.get('kind', 'failure')), 'span', event,
                                input={k: v for k, v in event.items() if k != 'type'})
            self._complete(failed, output={'recorded_failure': True}, level=level)
            if self._unit:
                levels = {'DEFAULT': 0, 'WARNING': 1, 'ERROR': 2}
                if levels[level] > levels[self._unit[1]['level']]:
                    self._unit[1]['level'] = level
        elif kind in ('checkpoint_restore', 'build_start', 'build_complete'):
            span = self._open('A-MEM/' + kind, 'span', event,
                              input={k: v for k, v in event.items() if k != 'type'})
            self._complete(span, output={'recorded': True})
        elif kind in ('run_abort', 'run_complete'):
            for name in ('_generation', '_action', '_retrieval', '_unit'):
                opened = getattr(self, name)
                if opened:
                    self._complete(opened, output={'run_event': event},
                                   level='ERROR' if kind == 'run_abort' else None)
                    setattr(self, name, None)
            self._complete(self._phase, output=event,
                           level='ERROR' if kind == 'run_abort' else None)
            self._phase = None

    def _generation_result(self, event):
        if self._generation is None:
            self.begin_generation(event)
        usage = [a['usage'] for a in event.get('attempts', []) if a.get('usage')]
        unknown = sum(not a.get('usage') for a in event.get('attempts', []))
        if not usage and not event.get('attempts') and event.get('usage'):
            usage = [event['usage']]
        details = {'input': sum(u.get('prompt_tokens', 0) for u in usage),
                   'output': sum(u.get('completion_tokens', 0) for u in usage)}
        details['total'] = details['input'] + details['output']
        cost = None if unknown or not usage else {'total': sum(
            int((Decimal('.30') * u.get('prompt_tokens', 0)
                 + Decimal('1.20') * u.get('completion_tokens', 0))
                .to_integral_value(rounding=ROUND_CEILING)) for u in usage) / 1000000}
        response = event.get('provider_response') or next(
            (a['response_body'] for a in reversed(event.get('attempts', []))
             if isinstance(a.get('response_body'), dict) and a['response_body'].get('choices')), {})
        choices = response.get('choices') or []
        calls = ((choices[0].get('message') or {}).get('tool_calls') or []) if choices else []
        raw = (calls[0].get('function') or {}).get('arguments') if calls else event.get('output')
        extra = {'usage_details': details} if usage else {}
        if cost is not None:
            extra['cost_details'] = cost
        metadata = {k: copy.deepcopy(event.get(k)) for k in (
            'endpoint', 'documented_model_version', 'request_id', 'returned_model',
            'system_fingerprint', 'provider_contract_policy', 'raw_schema_valid',
            'validation_copy_schema_valid', 'compatibility_deviation', 'error_type')}
        attempts = event.get('attempts', [])
        if attempts and isinstance(attempts[0].get('request_body'), dict):
            # Already sanitized by the recording transport; no headers or credentials.
            if self.essential_export:
                from .config import fingerprint
                metadata['wire_request_sha256'] = fingerprint(attempts[0]['request_body'])
                metadata['local_evidence'] = {'journal': 'events.jsonl', 'stage': event.get('stage')}
                if event.get('budget_logical_id') is not None:
                    metadata['local_evidence']['budget_logical_id'] = event['budget_logical_id']
            else:
                metadata['wire_request'] = copy.deepcopy(attempts[0]['request_body'])
        for field, source in (('request_id', 'id'), ('returned_model', 'model'),
                              ('system_fingerprint', 'system_fingerprint')):
            if metadata[field] is None:
                metadata[field] = response.get(source)
        metadata.update(observed_generation_duration_seconds=event.get('duration_seconds'),
                        physical_attempts=len(event.get('attempts', [])),
                        transmitted=bool(event.get('attempts')),
                        unknown_usage_attempts=unknown,
                        usage_complete=unknown == 0 and bool(usage),
                        cost_complete=unknown == 0 and bool(usage),
                        ledger_reservations_authoritative=True,
                        accounting_notice='Known source usage only; unknown attempts retain durable ledger reservations. Reconcile the phase ledger for incurred spending.',
                        cost_basis='conservative-per-attempt-ceiling-not-invoice',
                        attempts=[{k: a.get(k) for k in
                                   ('attempt', 'status_code', 'error_type', 'usage', 'duration_seconds',
                                    'budget_attempt_id', 'charged_cost_usd', 'reservation_microusd')}
                                  for a in event.get('attempts', [])])
        accepted = event.get('error_type') is None and isinstance(event.get('output'), str)
        choices = response.get('choices') or []
        output = {'provider_arguments': raw, 'accepted': accepted,
                  'finish_reason': choices[0].get('finish_reason') if choices else None,
                  'parser_input_sha256': hashlib.sha256(event['output'].encode()).hexdigest()
                    if accepted else None,
                  'algorithm_input_modified': raw != event['output'] if accepted else None}
        self._complete(self._generation, output=output, metadata=metadata,
                       level='ERROR' if event.get('error_type') else
                       'WARNING' if event.get('compatibility_deviation') else None, **extra)
        self._generation = None

    def assert_healthy(self):
        if self.errors:
            raise ObservabilityError('Tracing failed; no next experimental operation is permitted')

    def finish(self):
        if not self._finished:
            self._attempt('finish_open_observations', lambda: self._observe(
                {'type': 'run_abort', 'reason': 'observer_finish_with_open_work'}))
            for opened in list(self._pending.values()):
                self._attempt('finish_orphaned_observation', lambda opened=opened: self._complete(
                    opened, output={'observer_finished_with_open_work': True}, level='ERROR'))
            self._attempt('flush', self.client.flush)
            self._finished = True
        return {'metadata': copy.deepcopy(self.metadata),
                'session_id': self.session_id,
                'trace_ids': sorted({r['trace_id'] for r in self.observations}),
                'observations': copy.deepcopy(self.observations),
                'scores': copy.deepcopy(self.scores), 'errors': copy.deepcopy(self.errors),
                'cloud_visibility_verified': False}
