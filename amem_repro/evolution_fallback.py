"""Verify one unchanged author fallback; never repair or accept rejected JSON."""
from __future__ import annotations

import hashlib
import json

from .budget import BudgetStop
from .config import fingerprint
from .contracts import load_author_contracts

POLICY_ID = 'run2-original-evolution-fallback-v1'
RECOVERY_POLICY = 'run2-financial-sequential-state-v1'
# Historical normal-finish failure: approval and receipt remain immutable.
NORMAL_FAILURE_RECEIPT = '695b8e082ed5913f83db3f4fbca4ec3f106bb8f86503e258313abf1677d7d96d'


def malformed_decision(event, error=None):
    """Only syntax-invalid object text the frozen cleanup cannot change is eligible.

    Restrict to object-delimited text: the author's leading/trailing wrapper cleanup
    is then a no-op. A raw JSONDecodeError in cleanup-parsable text is NOT fallback.
    Length, schema/type, nonfinite, transport and other stages remain fatal.
    """
    from .adapter import AdapterError
    if error is not None and (type(error) is not AdapterError
                             or type(error.__cause__) is not json.JSONDecodeError):
        return False
    try:
        contract = load_author_contracts()['shared_decision']
        choice = event['provider_response']['choices']
        raw = event['output']
        if (event['stage'] != 'shared_decision' or event['error_type'] != 'AdapterError'
                or event['response_format'] != contract or event['temperature'] != .7
                or event['max_tokens'] != 8192 or event['thinking'] != 'disabled'
                or event['returned_model'] != 'deepseek-flash'
                or event['system_fingerprint'] != 'bc19ba97cbe016479903222bb1578db6'
                or not isinstance(raw, str) or not raw.strip().startswith('{')
                or not raw.strip().endswith('}') or len(choice) != 1
                or choice[0]['finish_reason'] != 'tool_calls'):
            return False
        calls = choice[0]['message']['tool_calls']
        if (len(calls) != 1 or calls[0]['type'] != 'function'
                or calls[0]['function']['name'] != contract['json_schema']['name']
                or calls[0]['function']['arguments'] != raw):
            return False
        usage = event['usage']
        if (any(type(usage[k]) is not int or usage[k] < 0
                for k in ('prompt_tokens', 'completion_tokens'))
                or not 0 < usage['completion_tokens'] < 8192):
            return False
        attempts = event['attempts']
        last = attempts[-1]
        wire = last['request_body']
        if (last.get('status_code') != 200 or last.get('error_type') is not None
                or last['response_body']['choices'][0]['message']['tool_calls'][0]['function']['arguments'] != raw
                or wire.get('model') != 'deepseek-flash' or wire.get('max_tokens') != 8192
                or wire.get('temperature') != .7 or wire.get('thinking') != {'type':'disabled'}
                or wire.get('stream') is not False
                or wire['messages'] != [{'role':'system','content':'You must respond with a JSON object.'},
                                        {'role':'user','content':event['prompt']}]
                or wire['tools'] != [{'type':'function','function':{'name':contract['json_schema']['name'],
                    'strict':True,'parameters':contract['json_schema']['schema']}}]
                or wire['tool_choice'] != {'type':'function','function':{'name':contract['json_schema']['name']}}):
            return False
        try:
            json.loads(raw.strip())
        except json.JSONDecodeError:
            return True
        return False
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def verify_fallback_state(before, after, outcome, metadata, note_document):
    """Compare actual state, including exact stale rows, after the author catch."""
    import numpy as np
    from .artifacts import _validate_state
    _validate_state(after)
    n = len(before['notes'])
    if (len(after['notes']) != n+1 or after['notes'][:-1] != before['notes']
            or before['evo_cnt'] != after['evo_cnt']
            or before['evo_threshold'] != after['evo_threshold']
            or outcome['counter_before'] != before['evo_cnt']
            or outcome['counter_after'] != before['evo_cnt']
            or outcome['proposed_decision'] is not None or outcome['changed_existing_note_ids']):
        raise BudgetStop('Original evolution fallback changed memory or counter')
    note = after['notes'][-1]['attributes']
    if (note.get('links') != [] or note.get('evolution_history') != []
            or any(note[k] != metadata[k] for k in ('context','tags','keywords'))):
        raise BudgetStop('Original failed note metadata or links changed')
    old, new = before['retriever'], after['retriever']
    document = note_document(note)
    expected_map = {**old['document_ids'], document:n}
    rows = np.asarray(new['embeddings'], dtype=new['embedding_dtype'])
    prior = np.asarray(old['embeddings'], dtype=old['embedding_dtype'])
    if (new['corpus'] != old['corpus']+[document] or new['document_ids'] != expected_map
            or new['embedding_dtype'] != 'float32' or rows.shape != (n+1,384)
            or not np.isfinite(rows).all() or (n and (prior.dtype != rows.dtype
                or prior.tobytes() != rows[:-1].tobytes()))):
        raise BudgetStop('Original evolution fallback changed stale retrieval state')
    return {'before_state_sha256':fingerprint(before), 'after_state_sha256':fingerprint(after)}


class OriginalFallbackGuard:
    """Observe before/after each original turn; block calls until fallback is proven."""
    def __init__(self, permit, healthy, note_document):
        self.permit, self.healthy, self.note_document = permit, healthy, note_document

    def before(self, agent):
        from .artifacts import snapshot_memory
        return snapshot_memory(agent.memory_system, validate=False)

    def after(self, agent, before, outcome, generations, record):
        pending = self.permit._pending_evolution
        if pending is None:
            return
        from .artifacts import snapshot_memory
        bad = [e for e in generations if e.get('error_type')]
        metadata = [e for e in generations if e['stage']=='metadata' and not e.get('error_type')]
        if (len(generations) != 2 or len(metadata) != 1 or len(bad) != 1
                or bad[0].get('budget_logical_id') != pending['budget_logical_id']
                or not malformed_decision(bad[0]) or fingerprint(bad[0]['output']) != pending['output_sha256']):
            raise BudgetStop('Evolution fallback does not match the rejected generation')
        self.healthy()
        after = snapshot_memory(agent.memory_system)
        proof = verify_fallback_state(before, after, outcome, json.loads(metadata[0]['output']), self.note_document)
        event = {'type':'failure', 'kind':'original_evolution_fallback',
                 'provider_deviation':'malformed_shared_decision_json',
                 'evolution_failure_policy':POLICY_ID, 'turn_id':outcome['turn_id'],
                 'budget_logical_id':pending['budget_logical_id'], 'provider_output_accepted':False,
                 'raw_arguments_sha256':hashlib.sha256(bad[0]['output'].encode()).hexdigest(),
                 'counter_before':outcome['counter_before'], 'counter_after':outcome['counter_after'],
                 'original_fallback_verified':True, **proof}
        record(event) # Durable local journal and cloud input precede releasing the gate.
        self.healthy()
        self.permit.confirm_evolution_fallback(pending)
