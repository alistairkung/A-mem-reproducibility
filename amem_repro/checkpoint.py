"""Verified, one-parent continuation of the BLK-014 conv-50 pilot.

This module grants no paid authorization and never repairs provider output.
The incomplete parent remains immutable; child approvals bind its receipt hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3

from .artifacts import _validate_state
from .config import fingerprint

MIGRATION_FILES = {
    'amem_repro/checkpoint.py', 'amem_repro/runner.py',
    'amem_repro/phases.py', 'amem_repro/forecast.py',
    'amem_repro/budget.py',
}
PARENT_PHASE_SHA256 = 'a3d90514404a454cb894e9c716ffaccb26a1b054364aa8c8f3cd1f4509d7a231'


def _read_archive(path, root):
    path = Path(path).resolve()
    if not path.is_relative_to((root / 'artifacts/runs').resolve()) or path.name != 'phase.json':
        raise ValueError('Checkpoint parent must be an archived study phase')
    phase = json.loads(path.read_text())
    if fingerprint(phase) != PARENT_PHASE_SHA256:
        raise ValueError('Only the frozen BLK-014 parent receipt is recoverable')
    required = {'approval.json', 'preflight.json', 'events.jsonl', 'run.json',
                'summary.json', 'partial-memory.json'}
    if not required.issubset(phase['artifact_sha256']):
        raise ValueError('Incomplete checkpoint inventory')
    for name, digest in phase['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path.parent / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Checkpoint parent artifact changed')
    return path, phase


def verify_checkpoint(path, root, manifest, config, sources, receipt, compatibility):
    """Read and validate parent state/ledger before a child permit can be claimed."""
    root = Path(root).resolve()
    path, phase = _read_archive(path, root)
    def read(name):
        return json.loads((path.parent / name).read_text())
    approval, preflight = read('approval.json'), read('preflight.json')
    run = read('run.json')
    events = [json.loads(line) for line in (path.parent / 'events.jsonl').read_text().splitlines()]
    start = events[0]
    partial = read('partial-memory.json')
    identity, state = partial['identity'], partial['state']
    binding = phase['binding']
    if (path.parent.name != phase['run_id']
            or phase['phase'] != 'pilot' or phase['status'] != 'incomplete'
            or phase['usable_for_next_phase'] or phase['completed_questions'] != 0
            or phase['conversation_ids'] != ['conv-50'] or 'checkpoint' in binding
            or approval['approved'] is not True or approval['binding'] != binding
            or approval['run_id'] != phase['run_id'] or run['run_id'] != phase['run_id']
            or partial['complete'] is not False):
        raise ValueError('Only the incomplete original conv-50 pilot is recoverable')
    if (fingerprint(manifest) != binding['manifest_sha256']
            or fingerprint(config) != binding['config_sha256']
            or fingerprint(preflight) != binding['preflight_sha256']
            or fingerprint(start['source_hashes']) != binding['source_sha256']
            or preflight['assets'] != receipt['assets']):
        raise ValueError('Checkpoint inputs or runtime assets differ')
    if (start['manifest'] != manifest or start['configuration'] != config
            or identity['configuration'] != config or identity['source_hashes'] != start['source_hashes']
            or identity['conversation'] != manifest['conversations'][0]
            or identity['dataset_sha256'] != manifest['dataset_sha256']
            or identity['condition'] != 'full' or identity['repetition'] != 0
            or identity['provider_contract_policy'] != binding['provider_contract_policy']):
        raise ValueError('Checkpoint memory provenance differs')
    if sources['author_revision'] != start['source_hashes']['author_revision']:
        raise ValueError('Checkpoint author revision differs')
    old, new = start['source_hashes']['files'], sources['files']
    changed = {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}
    if changed - MIGRATION_FILES:
        raise ValueError('Checkpoint migration changed scientific or provider code')
    for key in ('config_sha256', 'source_sha256', 'preflight_sha256', 'model', 'endpoint',
                'provider_contract_policy', 'max_output_tokens_by_stage'):
        if compatibility['binding'].get(key) != binding.get(key):
            raise ValueError('Parent compatibility provenance differs')
    if fingerprint(compatibility) != binding['compatibility_sha256']:
        raise ValueError('Parent compatibility receipt differs')

    _validate_state(state)
    # A partial checkpoint needs stronger checks than a complete-cache structural check.
    import numpy as np
    index = state['retriever']
    embeddings = np.asarray(index['embeddings'], dtype=index['embedding_dtype'])
    if (len(state['notes']) != 263 or len(state['outcomes']) != 263
            or embeddings.shape != (263, 384) or str(embeddings.dtype) != 'float32'
            or not np.isfinite(embeddings).all() or state['evo_cnt'] != 261
            or state['evo_threshold'] != 100
            or index['document_ids'] != {doc: i for i, doc in enumerate(index['corpus'])}):
        raise ValueError('Invalid BLK-014 checkpoint state')
    outcomes = [e for e in events if e['type'] == 'evolution_outcome']
    if ([e['turn_id'] for e in outcomes] != manifest['conversations'][0]['turn_ids'][:263]
            or [{k: v for k, v in e.items() if k in state['outcomes'][0]} for e in outcomes] != state['outcomes']
            or state['outcomes'][-1]['proposed_decision'] is not None
            or state['outcomes'][-1]['counter_before'] != 261
            or state['outcomes'][-1]['counter_after'] != 261
            or any(e['type'] in ('question_result', 'build_complete') for e in events)):
        raise ValueError('Checkpoint prefix/outcome mismatch')
    generations = [e for e in events if e['type'] == 'generation' and e.get('attempts')]
    rejected = [e for e in generations if e.get('error_type')]
    if ([e['stage'] for e in generations] != ['metadata', 'shared_decision'] * 263
            or len(rejected) != 1 or rejected[0] is not generations[-1]
            or rejected[0]['error_type'] != 'AdapterError'
            or rejected[0]['provider_response']['choices'][0]['finish_reason'] != 'tool_calls'):
        raise ValueError('Checkpoint generation coverage differs')
    try:
        json.loads(rejected[0]['output'])
    except json.JSONDecodeError:
        pass
    else:
        raise ValueError('Checkpoint is not the malformed-JSON failure')
    # Require durable original accounting; a new or relocated empty ledger cannot reset spend.
    ledger = root / 'artifacts/study-budget.sqlite'
    from .budget import ledger_summary
    if ledger_summary(ledger)['unknown_attempts']:
        raise ValueError('Unknown study charges block checkpoint recovery')
    with sqlite3.connect(ledger.resolve().as_uri() + '?mode=ro', uri=True) as db:
        row = db.execute('SELECT auth_json,halted FROM phases WHERE approval_id=?',
                         (approval['approval_id'],)).fetchone()
        if row is None or json.loads(row[0]) != approval or not row[1]:
            raise ValueError('Parent approval/halt missing from shared ledger')
        attempts = db.execute('SELECT id,status,usage_json,charge FROM attempts WHERE approval_id=? ORDER BY id',
                              (approval['approval_id'],)).fetchall()
        logical = db.execute('SELECT COUNT(*) FROM logical_calls WHERE approval_id=?',
                             (approval['approval_id'],)).fetchone()[0]
    recorded = [a for e in generations for a in e['attempts']]
    if (len(attempts) != 526 or logical != 526 or len(recorded) != len(attempts)
            or any(row[0] != a['budget_attempt_id'] or row[1] != 'settled'
                   or json.loads(row[2]) != a['usage'] for row, a in zip(attempts, recorded))
            or sum(row[3] for row in attempts) != phase['budget']['charged_or_reserved_microusd']):
        raise ValueError('Parent accounting differs or contains unknown charges')
    failures = [e for e in events if e['type'] == 'failure']
    if not any(e.get('kind') == 'evolve' for e in failures):
        raise ValueError('Original evolution failure missing')
    lineage = {
        'policy': 'blk014-checkpoint-v1', 'parent_run_id': phase['run_id'],
        'parent_phase_sha256': fingerprint(phase),
        'parent_snapshot_sha256': phase['artifact_sha256']['partial-memory.json'],
        'parent_events_sha256': phase['artifact_sha256']['events.jsonl'],
        'parent_source_sha256': binding['source_sha256'],
        'compatibility_run_id': compatibility['run_id'],
        'migrated_files': sorted(changed), 'completed_turns': 263,
        'remaining_logical_calls': 1018,
    }
    return {'lineage': lineage, 'state': state, 'failures': failures,
            'generations': generations, 'phase': phase}
