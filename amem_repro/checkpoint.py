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


def _read_archive(path, root, expected=None):
    path = Path(path).resolve()
    if not path.is_relative_to((root / 'artifacts/runs').resolve()) or path.name != 'phase.json':
        raise ValueError('Checkpoint parent must be an archived study phase')
    phase = json.loads(path.read_text())
    if fingerprint(phase) != (PARENT_PHASE_SHA256 if expected is None else expected):
        raise ValueError('Only the frozen BLK-014 parent receipt is recoverable' if expected is None
                         else 'Only the frozen BLK-013 parent receipt is recoverable')
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
    study = ledger_summary(ledger)
    if study['unknown_attempts']:
        raise ValueError('Unknown study charges block checkpoint recovery')
    if any(study[key] < phase['study_budget'][key] for key in (
            'charged_or_reserved_microusd', 'physical_attempts', 'logical_calls')):
        raise ValueError('Shared ledger lost historical study charges or requests')
    with sqlite3.connect(ledger.resolve().as_uri() + '?mode=ro', uri=True) as db:
        row = db.execute('SELECT auth_json,halted FROM phases WHERE approval_id=?',
                         (approval['approval_id'],)).fetchone()
        if row is None or json.loads(row[0]) != approval or not row[1]:
            raise ValueError('Parent approval/halt missing from shared ledger')
        attempts = db.execute('SELECT id,status,usage_json,charge FROM attempts WHERE approval_id=? ORDER BY id',
                              (approval['approval_id'],)).fetchall()
        logical = db.execute('SELECT COUNT(*) FROM logical_calls WHERE approval_id=?',
                             (approval['approval_id'],)).fetchone()[0]
        last_logical = db.execute('SELECT MAX(id) FROM logical_calls WHERE approval_id=?',
                                  (approval['approval_id'],)).fetchone()[0]
        last_attempt = attempts[-1][0] if attempts else 0
        historical_charge, historical_attempts = db.execute(
            'SELECT COALESCE(SUM(charge),0),COUNT(*) FROM attempts WHERE id<=?', (last_attempt,)).fetchone()
        historical_logical = db.execute('SELECT COUNT(*) FROM logical_calls WHERE id<=?',
                                         (last_logical or 0,)).fetchone()[0]
        if (historical_charge != phase['study_budget']['charged_or_reserved_microusd']
                or historical_attempts != phase['study_budget']['physical_attempts']
                or historical_logical != phase['study_budget']['logical_calls']):
            raise ValueError('Historical ledger prefix differs from frozen study accounting')
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


STUDY_PARENT_SHA256 = '19e863ea00b066f358e3518a9d22ee3c9767a9311057a5a545712561348d511d'
STUDY_CHECKPOINT_POLICY = 'blk013-conv49-checkpoint-v1'
STUDY_MIGRATION_FILES = {
    'amem_repro/checkpoint.py','amem_repro/budget.py','amem_repro/phases.py',
    'amem_repro/study.py','amem_repro/comparison.py','amem_repro/runner.py',
}


CONV44_PARENT_SHA256 = 'dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b'
CONV44_CHECKPOINT_POLICY = 'blk013-conv44-checkpoint-v1'
CONV44_FIRST_CHILD_SHA256 = 'fb730968fc1eec7cd4df4bcae5dc89baa7ff507dc111c5c1868319f5106d7fd9'
CONV44_SECOND_CHECKPOINT_POLICY = 'blk013-conv44-second-checkpoint-v1'


def study_checkpoint_profile(conversation_id, policy=None):
    """Only three approved recovery boundaries; at most two hops for conv-44."""
    if conversation_id=='conv-44' and policy==CONV44_SECOND_CHECKPOINT_POLICY:
        return {'conversation_id':'conv-44','parent_phase_sha256':CONV44_FIRST_CHILD_SHA256,
            'policy':CONV44_SECOND_CHECKPOINT_POLICY,'parent_run_id':'t8-full-conv44-checkpoint-child',
            'completed_turns':610,'evolution_counter':607,'failed_turn':'D26:18',
            'remaining_logical_calls':446,'phase_cap_usd':'3'}
    if policy is not None and policy not in (STUDY_CHECKPOINT_POLICY,CONV44_CHECKPOINT_POLICY):
        raise ValueError('Only the pinned study checkpoint policies are enabled')
    if conversation_id == 'conv-49':
        return {'conversation_id':'conv-49','parent_phase_sha256':STUDY_PARENT_SHA256,
            'policy':STUDY_CHECKPOINT_POLICY,'parent_run_id':'t8-full-conv49-r0-20261102',
            'completed_turns':413,'evolution_counter':411,'failed_turn':'D22:2',
            'remaining_logical_calls':584,'phase_cap_usd':'10'}
    if conversation_id == 'conv-44':
        return {'conversation_id':'conv-44','parent_phase_sha256':CONV44_PARENT_SHA256,
            'policy':CONV44_CHECKPOINT_POLICY,'parent_run_id':'t8-full-conv44-r0-20261103',
            'completed_turns':424,'evolution_counter':422,'failed_turn':'D18:21',
            'remaining_logical_calls':818,'phase_cap_usd':'3'}
    raise ValueError('Only the pinned conv-49/conv-44 checkpoints are enabled')


def verify_study_checkpoint(path, root, manifest, config, sources, receipt):
    """Verify a fixed recovery boundary, including only the approved second hop."""
    root = Path(root).resolve()
    profiles=(study_checkpoint_profile('conv-49'),study_checkpoint_profile('conv-44'),
              study_checkpoint_profile('conv-44',CONV44_SECOND_CHECKPOINT_POLICY))
    profile=next((p for p in profiles if p['parent_run_id']==Path(path).parent.name),None)
    if profile is None:
        raise ValueError('Only the pinned study checkpoint parents are recoverable')
    count,counter=profile['completed_turns'],profile['evolution_counter']
    path, phase = _read_archive(path, root, profile['parent_phase_sha256'])
    def read(name):
        return json.loads((path.parent / name).read_text())
    approval, preflight = read('approval.json'), read('preflight.json')
    events = [json.loads(line) for line in (path.parent/'events.jsonl').read_text().splitlines()]
    start, binding = events[0], phase['binding']
    partial = read('partial-memory.json')
    identity, state = partial['identity'], partial['state']
    conversation = next(c for c in manifest['conversations'] if c['original_id']==profile['conversation_id'])
    second=profile['policy']==CONV44_SECOND_CHECKPOINT_POLICY
    ancestor=None
    if second:
        ancestor=verify_study_checkpoint(root/'artifacts/runs/t8-full-conv44-r0-20261103/phase.json',
            root,manifest,config,start['source_hashes'],preflight)
        if (binding.get('checkpoint')!=ancestor['lineage']
                or read('checkpoint.json')!=binding['checkpoint']
                or identity.get('checkpoint')!=binding['checkpoint']):
            raise ValueError('Second checkpoint ancestry differs from the original root')
    elif 'checkpoint' in binding:
        raise ValueError('Only the pinned first-child continuation may have an ancestor')
    prefix=424 if second else 0
    new_count=count-prefix
    if (phase['run_id'] != profile['parent_run_id'] or path.parent.name != phase['run_id']
            or phase['phase'] != 'baseline' or phase['status'] != 'incomplete'
            or phase['usable_for_next_phase'] or phase['completed_questions'] != 0
            or phase['conversation_ids'] != [profile['conversation_id']]
            or binding['condition'] != 'full' or binding['repetition'] != 0
            or approval.get('approved') is not True or approval['binding'] != binding
            or approval['run_id'] != phase['run_id'] or read('run.json')['run_id'] != phase['run_id']
            or partial['complete'] is not False):
        raise ValueError('Only the frozen incomplete study baseline is recoverable')
    if (fingerprint(manifest) != binding['manifest_sha256']
            or fingerprint(config) != binding['config_sha256']
            or fingerprint(preflight) != binding['preflight_sha256']
            or fingerprint(start['source_hashes']) != binding['source_sha256']
            or preflight['assets'] != receipt['assets'] or start['manifest'] != manifest
            or start['configuration'] != config or identity['configuration'] != config
            or identity['source_hashes'] != start['source_hashes']
            or identity['conversation'] != conversation
            or identity['dataset_sha256'] != manifest['dataset_sha256']
            or identity['condition'] != 'full' or identity['repetition'] != 0
            or identity['provider_contract_policy'] != binding['provider_contract_policy']
            or binding['provider_contract_policy'] != 'canonical-index-strings-v1'):
        raise ValueError('Pinned study checkpoint inputs or provenance differ')
    from .config import stage_output_limits
    if binding['max_output_tokens_by_stage'] != stage_output_limits():
        raise ValueError('Pinned study checkpoint generation policy differs')
    old, new = start['source_hashes']['files'], sources['files']
    changed = {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}
    if (changed - STUDY_MIGRATION_FILES
            or sources['author_revision'] != start['source_hashes']['author_revision']):
        raise ValueError('Pinned study checkpoint migration changed scientific or provider code')
    _validate_state(state)
    import numpy as np
    index = state['retriever']
    embeddings = np.asarray(index['embeddings'],dtype=index['embedding_dtype'])
    outcomes = [e for e in events if e['type']=='evolution_outcome']
    if second:
        prior=ancestor['state']
        if (state['outcomes'][:424]!=prior['outcomes']
                or [n['key'] for n in state['notes'][:424]]!=[n['key'] for n in prior['notes']]):
            raise ValueError('Second checkpoint altered the original memory prefix')
        for old,note in zip(prior['notes'],state['notes']):
            note_fields={k for k in old['attributes'].keys()|note['attributes'].keys()
                         if old['attributes'].get(k)!=note['attributes'].get(k)}
            if note_fields-{'context','tags'}:
                raise ValueError('Second checkpoint altered immutable original note attributes')
    if (len(state['notes']) != count or len(state['outcomes']) != count
            or embeddings.shape != (count,384) or str(embeddings.dtype) != 'float32'
            or not np.isfinite(embeddings).all() or state['evo_cnt'] != counter
            or state['evo_threshold'] != 100
            or index['document_ids'] != {doc:i for i,doc in enumerate(index['corpus'])}
            or [e['turn_id'] for e in outcomes] != conversation['turn_ids'][prefix:count]
            or [{k:v for k,v in e.items() if k in state['outcomes'][0]} for e in outcomes] != state['outcomes'][prefix:]
            or state['outcomes'][-1]['turn_id'] != profile['failed_turn']
            or state['outcomes'][-1]['proposed_decision'] is not None
            or state['outcomes'][-1]['counter_before'] != counter
            or state['outcomes'][-1]['counter_after'] != counter
            or state['outcomes'][-1]['changed_existing_note_ids']
            or any(e['type'] in ('question_result','build_complete') for e in events)):
        raise ValueError('Invalid study checkpoint state or prefix')
    generations = [e for e in events if e['type']=='generation' and e.get('attempts')]
    rejected = [e for e in generations if e.get('error_type')]
    if ([e['stage'] for e in generations] != ['metadata','shared_decision']*new_count
            or len(rejected) != 1 or rejected[0] is not generations[-1]
            or rejected[0]['error_type'] != 'AdapterError'
            or rejected[0]['provider_response']['choices'][0]['finish_reason'] != 'length'
            or rejected[0]['provider_response']['usage']['completion_tokens'] != 4000):
        raise ValueError('Pinned study checkpoint generation/failure differs')
    from .budget import ledger_summary,study_job_claim
    from decimal import Decimal,ROUND_CEILING
    ledger = root/'artifacts/study-budget.sqlite'
    study = ledger_summary(ledger)
    if study['unknown_attempts']:
        raise ValueError('Unknown study charges block checkpoint recovery')
    with sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro',uri=True) as db:
        parent = db.execute('SELECT auth_json,halted FROM phases WHERE approval_id=?',
                            (approval['approval_id'],)).fetchone()
        if parent is None or json.loads(parent[0]) != approval or not parent[1]:
            raise ValueError('Pinned study parent approval/halt missing from shared ledger')
        claim=study_job_claim(db,approval['approval_id'])
        if claim != ('d10a-fallback-once-v1','full',profile['conversation_id'],0):
            raise ValueError('Pinned study historical cell claim differs')
        attempts = db.execute('SELECT id,status,usage_json,charge,logical_id FROM attempts WHERE approval_id=? ORDER BY id',
                              (approval['approval_id'],)).fetchall()
        logical = db.execute('SELECT id,stage FROM logical_calls WHERE approval_id=? ORDER BY id',
                             (approval['approval_id'],)).fetchall()
        recorded = [a for e in generations for a in e['attempts']]
        if (len(attempts) != 2*new_count or len(logical) != 2*new_count or len(recorded) != 2*new_count
                or [row[1] for row in logical] != ['metadata','shared_decision']*new_count
                or any(row[0] != a['budget_attempt_id'] or row[1] != 'settled'
                       or json.loads(row[2]) != a['usage'] for row,a in zip(attempts,recorded))
                or sum(row[3] for row in attempts) != phase['budget']['charged_or_reserved_microusd']):
            raise ValueError('Pinned study parent accounting differs')
        rates=approval['pricing']
        for row,call,record in zip(attempts,logical,recorded):
            usage=record['usage']
            expected=int((usage['prompt_tokens']*Decimal(str(rates['input_per_million']))+
                usage['completion_tokens']*Decimal(str(rates['output_per_million']))).to_integral_value(rounding=ROUND_CEILING))
            if row[3]!=expected or row[4]!=call[0]:
                raise ValueError('Pinned study per-attempt accounting differs')
        for key,query,last in (
            ('charged_or_reserved_microusd','SELECT COALESCE(SUM(charge),0) FROM attempts WHERE id<=?',attempts[-1][0]),
            ('physical_attempts','SELECT COUNT(*) FROM attempts WHERE id<=?',attempts[-1][0]),
            ('logical_calls','SELECT COUNT(*) FROM logical_calls WHERE id<=?',logical[-1][0])):
            if db.execute(query,(last,)).fetchone()[0] != phase['study_budget'][key]:
                raise ValueError('Pinned study historical ledger prefix differs')
    failures = [e for e in events if e['type']=='failure']
    if second:
        inherited=[e for e in failures if e.get('inherited_from')=='checkpoint']
        if (read('summary.json')['failures']!=failures or len(inherited)!=len(ancestor['failures'])):
            raise ValueError('Second checkpoint inherited failure inventory differs')
        for index,(original,notice) in enumerate(zip(ancestor['failures'],inherited)):
            if (any(notice.get(k)!=v for k,v in original.items() if k not in ('run_id','build_id'))
                    or notice.get('origin_run_id')!=original.get('origin_run_id',original['run_id'])
                    or notice.get('origin_failure_index')!=original.get('origin_failure_index',index)):
                raise ValueError('Second checkpoint lost original failure provenance')
    if not any(e.get('kind')=='evolve' for e in failures):
        raise ValueError('Pinned study failed evolution missing')
    lineage = {'policy':profile['policy'],'parent_run_id':phase['run_id'],
        'parent_approval_id':approval['approval_id'],'parent_phase_sha256':fingerprint(phase),
        'parent_snapshot_sha256':phase['artifact_sha256']['partial-memory.json'],
        'parent_events_sha256':phase['artifact_sha256']['events.jsonl'],
        'parent_source_sha256':binding['source_sha256'],'migrated_files':sorted(changed),
        'completed_turns':count,'remaining_logical_calls':profile['remaining_logical_calls']}
    if second:
        lineage['parent_checkpoint']=json.loads(json.dumps(binding['checkpoint']))
    return {'lineage':lineage,'state':state,'failures':failures,'generations':generations,'phase':phase}
