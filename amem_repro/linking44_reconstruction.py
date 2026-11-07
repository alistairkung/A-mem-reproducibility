"""Apply the PR #48 exception at the sole interrupted Linking Only turn."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

from .actions import make_action_agent_factory
from .artifacts import restore_memory, snapshot_memory
from .blk027 import sha
from .budget import BudgetStop
from .config import OPENROUTER_CONFIG, fingerprint, source_fingerprint
from .evolution_fallback import verify_fallback_state
from .gpt4omini_campaign import read, verify_inventory
from .openrouter import CAMPAIGN
from .phases import _asset_environment, _deny_network

from .linking44_finance import (CELL, CHILD, PARENT, PARENT_PATH, PARENT_SEAL,
                              PARENT_FILE_SHA as PARENT_HASH, RECONSTRUCTION_PATH as SUPPLEMENT)
POLICY = 'pr48-d10-15-new-uuid-and-last-accessed'
DISCONNECT = 'Server disconnected without sending a response.'


def require(condition, message):
    if not condition:
        raise BudgetStop(message)


def reconstruct(root, campaign):
    """Produce a candidate or sealed supplement with the author's new UUID and clock."""
    from httpx import RemoteProtocolError
    from .author import _load_memory
    from .manifests import expand_manifest

    path = campaign / PARENT_PATH
    require(path.absolute() == path.resolve() and sha(path) == PARENT_HASH,
            'Exact terminal parent required')
    receipt = read(path)
    require(fingerprint(receipt) == PARENT_SEAL, 'Terminal parent seal differs')
    verify_inventory(path.parent, receipt['files'])
    before = read(path.parent / 'partial-memory.json')['state']
    events = [json.loads(line) for line in (path.parent / 'events.jsonl').read_text().splitlines()]
    selected = [e for e in events if e.get('turn_id') == 'D10:15']
    start, metadata, failed = selected[:3]
    require([e['type'] for e in selected] == ['memory_turn_start', 'generation', 'generation',
                                              'failure', 'run_abort'], 'Partial turn event order differs')
    require(metadata['budget_logical_id'] == 17285 and metadata['stage'] == 'metadata'
            and metadata['provider_response'] == read(path.parent / 'raw/017285-response.bin')
            and metadata['output'] == metadata['provider_response']['choices'][0]['message']['content'],
            'Saved metadata differs')
    require(failed['budget_logical_id'] == 17286 and failed['stage'] == 'shared_decision'
            and failed['error_type'] == 'RemoteProtocolError' and failed['error_message'] == DISCONNECT
            and failed['output'] is None and failed['usage'] is None and len(failed['attempts']) == 1
            and failed['attempts'][0]['request_body'] == read(path.parent / 'raw/017286-request.json')
            and not (path.parent / 'raw/017286-response.bin').exists(), 'Failed request differs')
    manifest = expand_manifest(root / 'data/locomo10.json', read(root / 'manifests/fallback.json'))
    conversation = next(c for c in manifest['conversations'] if c['original_id'] == 'conv-44')
    turn_ids = conversation['turn_ids']
    require(len(turn_ids) == 675 and len(conversation['questions']) == 158
            and turn_ids[231:233] == ['D10:15', 'D10:16']
            and [o['turn_id'] for o in before['outcomes']] == turn_ids[:231]
            and len(before['notes']) == before['evo_cnt'] == 231, 'Committed prefix differs')
    fields = json.loads(metadata['output'])
    calls = []

    class RecordedDecisionFailure:
        observer_errors = ()

        def get_completion(self, prompt, response_format, temperature=.7):
            require(not calls and prompt == failed['prompt'] and response_format == failed['response_format']
                    and temperature == failed['temperature'], 'Reconstructed shared decision input differs')
            calls.append(17286)
            raise RemoteProtocolError(DISCONNECT)

    with _asset_environment(root / 'artifacts/assets'), _deny_network():
        memory = _load_memory(root)
        controller = RecordedDecisionFailure()
        factory = make_action_agent_factory(root, condition='linking_only', memory_module=memory,
                                            controller_factory=lambda _: controller)
        agent = factory(config=OPENROUTER_CONFIG, observer=lambda _: None)
        system = agent.memory_system
        restore_memory(system, before, note_type=memory.MemoryNote)
        require(snapshot_memory(system, before['outcomes']) == before, 'Prefix restoration differs')
        initial_failures = dict(memory.FAILURES)
        note_id = system.add_note(start['input']['content'], time=start['input']['timestamp'],
                                  category='Uncategorized', **fields)
        expected = copy.deepcopy(initial_failures)
        expected['evolve'] = expected.get('evolve', 0) + 1
        require(calls == [17286] and dict(memory.FAILURES) == expected,
                'Original transport fallback did not execute exactly once')
        outcome = {'turn_id': 'D10:15', 'counter_before': 231, 'counter_after': 231,
                   'proposed_decision': None, 'changed_existing_note_ids': [],
                   'enabled_actions': ['strengthen'], 'suppressed_actions': []}
        after = snapshot_memory(system, before['outcomes'] + [outcome])
        proof = verify_fallback_state(before, after, outcome, fields,
                                      lambda note: memory.note_document(SimpleNamespace(**note)))
        note = system.memories[note_id]
        require(note.content == start['input']['content'] and note.timestamp == start['input']['timestamp']
                and after['notes'][-1]['key'] == note_id, 'Reconstructed note differs')
        import numpy as np
        require(np.array_equal(system.retriever.embeddings[-1],
                               system.retriever.model.encode([memory.note_document(note)])[0]),
                'Reconstructed embedding differs')

    generated = {'id': note_id, 'last_accessed': note.last_accessed}
    lineage = {'policy': 'gpt4omini-exact-state-v1', 'reconstruction_policy': POLICY,
               'campaign_id': CAMPAIGN, 'condition': 'linking_only', 'parent_run_id': PARENT,
               'ancestors': [{'phase': PARENT, 'seal': PARENT_SEAL}], 'next_turn_id': 'D10:16',
               'turn_id_reconstructed': 'D10:15', 'newly_generated_fields': generated,
               'metadata_attempt': 17285, 'failed_attempt': 17286, **proof}
    failures = [e for e in events if e['type'] == 'failure']
    failures.append({'type': 'failure', 'kind': 'original_evolution_fallback',
                     'provider_deviation': 'recorded_no_response_transport_exception',
                     'run_id': PARENT, 'turn_id': 'D10:15', 'budget_logical_id': 17286,
                     'origin': 'pr48_reconstruction_supplement', 'newly_generated_fields': generated,
                     'provider_output_accepted': False, 'original_fallback_verified': True, **proof})
    return {'lineage': lineage, 'state': after, 'failures': failures,
            'newly_generated_fields': generated, 'parent_file_sha256': PARENT_HASH,
            'source_sha256': fingerprint(source_fingerprint(root)), 'network_requests': 0}


def load_checkpoint(approval, ledger, root):
    from .linking44_finance import RELEASE_PATH
    release_path = ledger.root / RELEASE_PATH
    path = ledger.root / SUPPLEMENT
    require(approval['phase'] == CHILD and approval['parent'] == PARENT
            and Path(approval['parent_path']) == ledger.root / PARENT_PATH
            and sha(ledger.root / PARENT_PATH) == PARENT_HASH
            and approval['parent_seal'] == PARENT_SEAL
            and sha(release_path) == approval['linking44_recovery_release_sha256']
            and path.resolve() == path and sha(path) == read(release_path)['reconstruction_sha256'],
            'Approved reconstruction or parent differs')
    value = read(path)
    require(value['source_sha256'] == fingerprint(source_fingerprint(root))
            and value['source_sha256'] == approval['binding']['source_sha256']
            and fingerprint(value['state']) == value['lineage']['after_state_sha256']
            and value['lineage']['reconstruction_policy'] == POLICY,
            'Sealed reconstruction differs')
    return {name: value[name] for name in ('state', 'failures', 'lineage')}
