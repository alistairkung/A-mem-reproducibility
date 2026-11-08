"""Bounded physical retries of a single unchanged native A-MEM request."""
from __future__ import annotations

import copy
import hashlib
import json
import time
from decimal import Decimal, InvalidOperation

from .adapter import AdapterError, _observed_payload
from .budget import BudgetStop
from .config import fingerprint
from .contracts import ContractError, validate_arguments
from .openrouter import MODEL, OpenRouterController, save_new, usage_charge


def retry_kind(event):
    """Classify evidence from one failed physical transmission, before financial admission."""
    attempts = event.get('attempts', [])
    if not event.get('error_type') or len(attempts) != 1:
        return None
    attempt = attempts[0]
    if attempt.get('budget_attempt_id') != event.get('budget_logical_id'):
        return None
    status = attempt.get('status_code')
    error = event['error_type']
    raw = attempt.get('response_body')
    if status is None and raw is None and error in {
        'ConnectTimeout', 'ReadTimeout', 'WriteTimeout', 'PoolTimeout', 'TimeoutException',
        'TimeoutError', 'ConnectError', 'ReadError', 'WriteError', 'ConnectionResetError',
        'ConnectionAbortedError', 'BrokenPipeError', 'RemoteProtocolError',
    }:
        return 'transport'
    if isinstance(raw, dict) and (
        raw.get('model') not in (None, MODEL) or raw.get('provider') not in (None, 'OpenAI')
    ):
        return None
    if type(status) is int and (500 <= status < 600 or status in (408, 429)):
        if isinstance(raw, dict):
            for choice in raw.get('choices') or []:
                if isinstance(choice, dict):
                    message = choice.get('message') or {}
                    if choice.get('finish_reason') == 'content_filter' or (
                        isinstance(message, dict) and (message.get('refusal') or message.get('tool_calls'))
                    ):
                        return None
            if ('usage' in raw or 'id' in raw) and attempt.get('charged_cost_usd') is None:
                return None
        # No generation identity or price is inferred from a gateway error.
        if error in ('HTTPStatusError', 'JSONDecodeError', 'UnicodeDecodeError'):
            return 'transient_http'
        return None
    if (status != 200 or not isinstance(raw, dict) or raw.get('provider') != 'OpenAI'
            or raw.get('model') != MODEL or event.get('actual_provider') != 'OpenAI'
            or event.get('returned_model') != MODEL or attempt.get('charged_cost_usd') is None):
        return None
    choices = raw.get('choices')
    if choices in (None, []) and error == 'BudgetStop' and event.get('error_message') == 'Unexpected response choices':
        return 'invalid_output'
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return None
    choice = choices[0]
    msg = choice.get('message')
    if msg is None and choice.get('finish_reason') in ('stop', 'length', 'error') and error in ('KeyError', 'AttributeError'):
        return 'invalid_output'
    if not isinstance(msg, dict) or msg.get('refusal') or msg.get('tool_calls'):
        return None
    finish = choice.get('finish_reason')
    if finish == 'error' and error == 'BudgetStop' and event.get('error_message') in (
        'Unexpected completion finish reason', 'Unsupported refusal/function response',
    ):
        return 'provider_error'
    if finish == 'length' and (
        error == 'AdapterError' or (error == 'BudgetStop' and event.get('error_message') == 'Unexpected completion finish reason')
    ):
        return 'invalid_output'
    if finish != 'stop' or error == 'AdapterError':
        # A normally finished author-recognized malformed evolution takes its existing fallback.
        return None
    if not (error == 'ContractError' or (error == 'ValueError' and event.get('error_message') == 'Nonfinite JSON')
            or (error == 'BudgetStop' and event.get('error_message') in
                ('Unsupported malformed output', 'Unsupported refusal/function response'))):
        return None
    content = msg.get('content')
    if not isinstance(content, str):
        return 'invalid_output'
    try:
        value = json.loads(content)
        validate_arguments(value, event['response_format']['json_schema']['schema'])
    except (json.JSONDecodeError, ContractError):
        return 'invalid_output'
    return None


class _PhysicalAdmission:
    """Route the native controller's reservation to its original or retry slot."""
    def __init__(self, ledger, prior):
        self.ledger = ledger
        self.prior = prior
        self.reason = None

    def reserve(self, phase, stage, body):
        if self.prior is None:
            return self.ledger.reserve(phase, stage, body)
        if stage != self.prior['stage'] or fingerprint(body) != self.prior['request_sha256']:
            raise BudgetStop('Retry request differs from its failed operation')
        return self.ledger.reserve_retry(phase, stage, body, self.prior['attempt_id'])

    def settle(self, attempt, response, limit):
        return self.ledger.settle(attempt, response, limit)

    def stop(self, phase, reason):
        # The outer controller persists/reviews the native event before retrying or halting.
        self.reason = reason


class _PhysicalObservation:
    def __init__(self, observer, first):
        self.observer = observer
        self.first = first
        self.event = None

    def begin_generation(self, event):
        if self.first and hasattr(self.observer, 'begin_generation'):
            self.observer.begin_generation(event)

    def __call__(self, event):
        self.event = event


class FinalController(OpenRouterController):
    """One scientific event per operation, retaining every raw physical request and response."""

    def __init__(self, client, *, ledger, phase, journal, observer=None):
        super().__init__(client, ledger=ledger, phase=phase, journal=journal, observer=observer)
        self._native = OpenRouterController(client, ledger=ledger, phase=phase, journal=journal)

    def _account_failed_response(self, event):
        """The base controller raises on HTTP errors before its normal success settlement."""
        if not event.get('attempts'):
            return
        attempt, = event['attempts']
        raw = attempt.get('response_body')
        if not isinstance(raw, dict) or 'charged_cost_usd' in attempt or not ('usage' in raw or 'id' in raw):
            return
        usage = raw.get('usage')
        aid = attempt['budget_attempt_id']
        if (attempt['status_code'] != 200 and isinstance(raw.get('id'), str) and raw['id'].startswith('gen-')
                and raw.get('model') == MODEL and raw.get('provider') == 'OpenAI'):
            try:
                usage_charge(usage, event['max_tokens'])
            except (BudgetStop, KeyError, TypeError, ValueError, ArithmeticError):
                pass
            else:
                charge = self.ledger.settle(aid, raw, event['max_tokens'])
                attempt['charged_cost_usd'] = charge / 1_000_000
                event.update(usage=usage, request_id=raw['id'], actual_provider=raw['provider'],
                             returned_model=raw['model'], conservative_cost_usd=attempt['charged_cost_usd'])
                return
        # A response with billing or generation identity must never be retried as an anonymous gateway error.
        try:
            amount = Decimal(str(usage['cost']))
        except (KeyError, TypeError, InvalidOperation):
            amount = Decimal(0)
        self.ledger.retain_reported_liability(self.phase, aid, amount if amount.is_finite() and amount >= 0 else Decimal(0))
        raise BudgetStop('Unverified response billing; no further model transmission')

    def _failure_receipt(self, event, kind):
        attempt, = event['attempts']
        number = attempt['budget_attempt_id']
        path = self.journal / f'{number:06d}-failure.json'
        save_new(path, event)
        return {'kind': kind, 'stage': event['stage'], 'attempt_id': number,
                'request_sha256': fingerprint(attempt['request_body']),
                'physical_evidence_file': str(path.absolute()),
                'physical_evidence_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def _publish(self, events, started):
        if not self.observer or not events:
            return
        final = dict(events[-1])
        physical = [dict(a, attempt=i) for i, e in enumerate(events, 1) for a in e.get('attempts', [])]
        final.update(started_at=events[0]['started_at'], duration_seconds=time.perf_counter()-started,
                     attempts=physical)
        if len(events) > 1:
            final['retry_of_physical_id'] = events[0]['budget_logical_id']
            final['physical_generations'] = []
            for event in events:
                for attempt in event['attempts']:
                    aid = attempt['budget_attempt_id']
                    path = self.journal / f'{aid:06d}-response.bin'
                    raw = path.read_bytes() if path.is_file() else None
                    response = attempt.get('response_body')
                    if raw is not None and response is None:
                        response = _observed_payload(raw.decode('utf-8', errors='replace'),
                                                     getattr(self.client, '_amem_credential', None))
                    final['physical_generations'].append({
                        'budget_attempt_id': aid, 'stage': event['stage'], 'started_at': event['started_at'],
                        'wire_request_sha256': fingerprint(attempt['request_body']),
                        'response_sha256': hashlib.sha256(raw).hexdigest() if raw is not None else None,
                        'response': response, 'status_code': attempt['status_code'],
                        'error_type': event.get('error_type'), 'error_message': event.get('error_message'),
                        'duration_seconds': attempt['duration_seconds'], 'usage': attempt.get('usage'),
                        'reservation_microusd': attempt['reservation_microusd'],
                        'charged_cost_usd': attempt.get('charged_cost_usd'),
                    })
            # Individual attempts still distinguish known charges and full outstanding reservations.
            final['conservative_cost_usd'] = float(sum((
                Decimal(str(a['charged_cost_usd'])) if 'charged_cost_usd' in a
                else Decimal(a['reservation_microusd']) / 1_000_000 for a in physical), Decimal(0)))
        self.observer(final)

    def get_completion(self, prompt, response_format, temperature=.7):
        if self.pending:
            raise BudgetStop('Original fallback must be independently verified before another request')
        started = time.perf_counter()
        contract = copy.deepcopy(response_format)
        events = []
        prior = None
        reason = 'generation_control_failure'
        try:
            for number in range(2):
                admission = _PhysicalAdmission(self.ledger, prior)
                capture = _PhysicalObservation(self.observer, number == 0)
                native = self._native
                native.ledger, native.observer, native.pending = admission, capture, None
                try:
                    result = native.get_completion(prompt, contract, temperature)
                except (BudgetStop, AdapterError) as failure:
                    event = capture.event
                    if event is None:
                        raise
                    events.append(event)
                    reason = admission.reason or event.get('error_type') or reason
                    try:
                        self._account_failed_response(event)
                    except BaseException:
                        self._failure_receipt(event, None)
                        raise
                    kind = retry_kind(event)
                    record = self._failure_receipt(event, kind) if event.get('attempts') else None
                    if kind:
                        self.ledger.record_failure(self.phase, record['attempt_id'], record)
                        if number == 0:
                            # One fixed delay before re-admission. The ledger rechecks time and funds afterward.
                            time.sleep(2)
                            prior = record
                            continue
                    self.pending = native.pending
                    if isinstance(failure, AdapterError) and self.pending:
                        raise
                    raise BudgetStop('Unsuccessful physical operation; no additional retry') from None
                else:
                    events.append(capture.event)
                    return result
        except AdapterError:
            raise
        except BaseException:
            self.ledger.stop(self.phase, reason)
            raise BudgetStop('Final campaign operation halted') from None
        finally:
            try:
                self._publish(events, started)
            except BaseException:
                self.ledger.stop(self.phase, 'generation_evidence_failed')
                raise BudgetStop('Logical generation observation failed') from None
