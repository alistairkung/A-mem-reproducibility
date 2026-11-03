"""Manifest orchestration around the original agent and scoring interfaces."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import random
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

from .artifacts import (
    CacheStore,
    RunLedger,
    build_identity,
    snapshot_memory,
    restore_memory,
)
from .config import (
    validate_config, source_fingerprint, STRICT_PROVIDER_POLICY, validate_provider_policy,
)
from .manifests import expand_manifest
from .actions import ACTION_POLICY, action_configuration


def load_dataset_module(repo_root):
    """The original parser is stdlib-only and has no model-initialization side effects."""
    name = "_amem_repro_original_dataset"
    path = Path(repo_root) / "load_dataset.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _counts(agent):
    read = getattr(agent, "_repro_failure_counts", None)
    return dict(read()) if read else {}


def _report_failures(ledger, previous, current, **context):
    for kind, count in current.items():
        for _ in range(max(0, count - previous.get(kind, 0))):
            ledger.record({"type": "failure", "kind": kind, **context})


def run_manifest(
    dataset_path,
    manifest,
    config,
    *,
    output_dir,
    cache_root,
    source_hashes=None,
    condition="full",
    repetition=0,
    execution_type="fresh_build",
    agent_factory=None,
    scorer=None,
    observer=None,
    paid_authorized=False,
    run_id=None,
    token_counter=None,
    provider_contract_policy=STRICT_PROVIDER_POLICY,
    checkpoint=None,
    conversation_ids=None,
    boundary_check=None,
):
    """Run an approved manifest. Injected interfaces support deterministic offline contracts.

    An ablated condition requires the explicitly bound T7 action factory.
    A true paid_authorized value is a declaration of separately obtained user approval, never permission
    inferred from environment credentials or the existence of a planning ticket.
    """
    validate_config(config)
    validate_provider_policy(provider_contract_policy)
    actions = action_configuration(condition)
    bound_condition = getattr(agent_factory, '_repro_condition', None)
    if ((bound_condition is not None and bound_condition != condition)
            or (condition != 'full' and bound_condition != condition)):
        raise ValueError('Condition requires its matching action-gated factory')
    if checkpoint is not None and condition != 'full':
        from .config import RUN2_CONFIG
        lineage = checkpoint.get('lineage', {})
        if (config != RUN2_CONFIG or lineage.get('policy') != 'run2-blk013-exact-state-v1'
                or lineage.get('campaign_id') != 'amem-run2-20261103-v1'
                or lineage.get('condition') != condition):
            raise ValueError('The frozen full-mode checkpoint cannot seed an ablation')
    action_implementation = 't7-action-gates' if bound_condition is not None else 'frozen-author'
    if execution_type not in ("fresh_build", "cached_qa", "checkpoint_recovery", "deterministic_replay"):
        raise ValueError("This runner supports fresh_build and cached_qa; replay is T6")
    if execution_type == 'deterministic_replay' and agent_factory is None:
        raise PermissionError('Replay requires an explicit offline controller/agent factory')
    if ((checkpoint is not None and execution_type not in ('checkpoint_recovery', 'cached_qa'))
            or (checkpoint is None and execution_type == 'checkpoint_recovery')):
        raise ValueError('Checkpoint state requires explicit recovery execution')
    if agent_factory is None and not paid_authorized:
        raise PermissionError("Separate paid execution approval is required")
    dataset_path = Path(dataset_path).resolve()
    root = dataset_path.parent.parent
    manifest = expand_manifest(dataset_path, manifest)
    conversations = manifest['conversations']
    if conversation_ids is not None:
        if type(conversation_ids) is not list or not conversation_ids:
            raise ValueError('Execution partition must be a nonempty list of whole frozen conversations')
        selected = [c for c in conversations if c['original_id'] in conversation_ids]
        if [c['original_id'] for c in selected] != conversation_ids:
            raise ValueError('Execution partition must select whole frozen conversations in original order')
        conversations = selected
    if agent_factory is None:
        actual_sources = source_fingerprint(root)
        if source_hashes is not None and source_hashes != actual_sources:
            raise ValueError("Live source provenance does not match current files")
        source_hashes = actual_sources
        from .author import make_agent_factory

        agent_factory = make_agent_factory(
            root, paid_authorized=True, token_counter=token_counter
        )
    if not source_hashes:
        raise ValueError("Source fingerprints are required")
    if scorer is None:
        from .scoring import AuthorScorer

        scorer = AuthorScorer(root)
    score_fn = scorer.score if hasattr(scorer, "score") else scorer
    parser = load_dataset_module(root)
    raw = json.loads(dataset_path.read_bytes())
    expected = [q["question_id"] for c in conversations for q in c["questions"]]
    ledger = RunLedger(output_dir, run_id or uuid.uuid4().hex, expected,
                       provider_contract_policy=provider_contract_policy)
    cache = CacheStore(cache_root)
    active = {}
    generations = []
    lifecycle = bool(getattr(observer, 'captures_lifecycle', False))
    local_record = ledger.record

    if lifecycle:
        def publish(event):
            local_record(event)  # Durable local evidence precedes optional cloud work.
            try:
                observer(copy.deepcopy(ledger.events[-1]))
            except Exception as error:
                local_record({'type': 'failure', 'kind': 'reporting',
                              'error_type': type(error).__name__, **active})
        ledger.record = publish

    def record(event):
        value = dict(event)
        value.setdefault("type", "generation")
        for key, item in active.items():
            value.setdefault(key, item)
        ledger.record(value)
        if value["type"] == "generation":
            generations.append(value)
            if value.get("compatibility_deviation"):
                ledger.record({
                    "type": "failure", "kind": "provider_contract_deviation",
                    "provider_contract_policy": provider_contract_policy,
                    "compatibility_deviation": value["compatibility_deviation"],
                    **active,
                })
            if value.get("error_type"):
                ledger.record(
                    {
                        "type": "failure",
                        "kind": "provider_completion",
                        "error_type": value["error_type"],
                        **active,
                    }
                )
        if value.get("token_count_error"):
            ledger.record(
                {
                    "type": "failure",
                    "kind": "token_measurement",
                    "error_type": value["token_count_error"],
                    **active,
                }
            )
        if observer and not lifecycle:
            try:
                observer(copy.deepcopy(value))
            except Exception as error:
                ledger.record(
                    {
                        "type": "failure",
                        "level": active.get("level", "run"),
                        "kind": "reporting",
                        "error_type": type(error).__name__,
                        **active,
                    }
                )

    for hook in ('begin_generation', 'begin_action', 'begin_retrieval'):
        callback = getattr(observer, hook, None)
        if callback is not None:
            def begin(event, callback=callback):
                try:
                    callback(copy.deepcopy({**active, **event, 'run_id': ledger.run_id}))
                except Exception as error:
                    ledger.record({'type': 'failure', 'kind': 'reporting',
                                   'error_type': type(error).__name__, **active})
            setattr(record, hook, begin)

    if hasattr(scorer, "observer"):
        scorer.observer = record
    ledger.record(
        {
            "type": "run_start",
            "execution_type": execution_type,
            "configuration": config,
            "manifest": manifest,
            "conversation_ids": [c['original_id'] for c in conversations],
            "source_hashes": source_hashes,
            "condition": condition,
            "memory_actions": actions,
            "action_policy": ACTION_POLICY,
            "action_implementation": action_implementation,
            "repetition": repetition,
            "provider_contract_policy": provider_contract_policy,
        }
    )
    try:
        for conversation in conversations:
            identity = build_identity(
                config,
                conversation,
                manifest["dataset_sha256"],
                source_hashes,
                repetition,
                provider_contract_policy=provider_contract_policy,
            )
            identity["condition"] = condition
            identity['memory_actions'] = actions
            identity['action_policy'] = ACTION_POLICY
            identity['action_implementation'] = action_implementation
            if execution_type == 'deterministic_replay':
                identity['execution_type'] = execution_type
            if checkpoint is not None:
                identity['checkpoint'] = checkpoint['lineage']
            build_id = cache.path_for(identity).name
            active.clear()
            active.update(
                level="memory_build",
                conversation_id=conversation["original_id"],
                build_id=build_id,
            )
            if execution_type != "cached_qa" and cache.path_for(identity).exists():
                raise ValueError(
                    "Fresh build already exists; approve a new independent repetition"
                )
            saved = cache.load(identity) if execution_type == "cached_qa" else None
            agent = agent_factory(config=config, observer=record)
            if bound_condition is not None and (
                    getattr(agent, '_repro_condition', None) != condition
                    or dict(getattr(agent, '_repro_action_configuration', {})) != actions):
                raise ValueError('Constructed agent action configuration differs')
            note_type = getattr(agent, "_repro_note_type", SimpleNamespace)
            sample = raw[conversation["sample_index"]]
            if sample["sample_id"] != conversation["original_id"]:
                raise ValueError("Original conversation identity mismatch")
            ledger.record(
                {"type": "build_start", **active, "execution_type": execution_type}
            )
            if saved is not None:
                outcomes = saved.get("outcomes", [])
                restore_memory(agent.memory_system, saved, note_type=note_type)
                for failure in saved.get("build_failures", []):
                    ledger.record(
                        {
                            **failure,
                            **active,
                            "origin_run_id": failure.get("origin_run_id", failure.get("run_id")),
                            "from_cache": True,
                        }
                    )
            else:
                outcomes = []
                prefix = []
                if checkpoint is not None:
                    restore_memory(agent.memory_system, checkpoint['state'], note_type=note_type)
                    outcomes = copy.deepcopy(checkpoint['state']['outcomes'])
                    prefix = [o['turn_id'] for o in outcomes]
                    if prefix != conversation['turn_ids'][:len(prefix)]:
                        raise ValueError('Checkpoint turn prefix differs')
                    record({'type': 'checkpoint_restore', **checkpoint['lineage']})
                    for index, failure in enumerate(checkpoint['failures']):
                        ledger.record({**failure, **active, 'from_cache': True,
                                       'inherited_from': 'checkpoint',
                                       'origin_run_id': failure.get('origin_run_id',failure['run_id']),
                                       'origin_failure_index': failure.get('origin_failure_index',index)})
                parsed = parser.parse_conversation(sample["conversation"])
                sessions = {
                    f"session_{key}": session
                    for key, session in parsed.sessions.items()
                }
                processed_turns = list(prefix)
                turn_offset = 0
                for session_key in conversation["session_keys"]:
                    session = sessions[session_key]
                    for turn in session.turns:
                        turn_offset += 1
                        if turn_offset <= len(prefix):
                            continue
                        if lifecycle:
                            active.update(turn_id=turn.dia_id)
                        if boundary_check is not None:
                            boundary_check()
                        if lifecycle:
                            record({'type': 'memory_turn_start',
                                    'input': {'content': 'Speaker ' + turn.speaker + 'says : ' + turn.text,
                                              'timestamp': session.date_time}})
                        previous = _counts(agent)
                        before = {
                            key: {"context": note.context, "tags": list(note.tags)}
                            for key, note in agent.memory_system.memories.items()
                        }
                        counter_before = agent.memory_system.evo_cnt
                        generation_start = len(generations)
                        agent.add_memory(
                            "Speaker " + turn.speaker + "says : " + turn.text,
                            time=session.date_time,
                        )
                        processed_turns.append(turn.dia_id)
                        _report_failures(ledger, previous, _counts(agent), **active)
                        decisions = [
                            event
                            for event in generations[generation_start:]
                            if event.get("stage") == "shared_decision"
                        ]
                        decision = None
                        if decisions and decisions[-1].get("output"):
                            try:
                                decision = json.loads(decisions[-1]["output"])
                            except (TypeError, json.JSONDecodeError):
                                pass  # Observation only; original caller already handled parsing.
                        changed = [
                            key
                            for key, note in agent.memory_system.memories.items()
                            if key in before
                            and before[key]
                            != {"context": note.context, "tags": list(note.tags)}
                        ]
                        proposal = decision if isinstance(decision, dict) else {}
                        proposed_actions = proposal.get('actions')
                        if not isinstance(proposed_actions, list):
                            proposed_actions = []
                        outcome = {
                            "turn_id": turn.dia_id,
                            "counter_before": counter_before,
                            "counter_after": agent.memory_system.evo_cnt,
                            "proposed_decision": decision,
                            "changed_existing_note_ids": changed,
                            "suppressed_actions": [a for a in proposed_actions
                                                   if agent.memory_system.evo_cnt == counter_before + 1 and isinstance(a, str)
                                                   and a in actions and not actions[a]],
                            "enabled_actions": [a for a, enabled in actions.items() if enabled],
                        }
                        outcomes.append(outcome)
                        record({"type": "evolution_outcome", **outcome})
                if processed_turns != conversation["turn_ids"]:
                    raise ValueError(
                        "Turn selection/order differs from the frozen manifest"
                    )
                state = snapshot_memory(agent.memory_system, outcomes)
                state["build_failures"] = [
                    event
                    for event in ledger.events
                    if event.get("type") == "failure"
                    and event.get("build_id") == build_id
                ]
                cache.save(identity, state)
            ledger.record(
                {"type": "build_complete", **active, "execution_type": execution_type}
            )
            for selection in conversation["questions"]:
                if lifecycle:
                    active.pop('turn_id', None)
                    active.update(level='question', question_id=selection['question_id'])
                if boundary_check is not None:
                    boundary_check()
                index = selection["original_qa_index"]
                qa_raw = sample["qa"][index]
                qa = parser.QA(
                    question=qa_raw["question"],
                    answer=qa_raw.get("answer"),
                    evidence=qa_raw.get("evidence", []),
                    category=qa_raw.get("category"),
                    adversarial_answer=qa_raw.get("adversarial_answer"),
                )
                active.update(level="question", question_id=selection["question_id"])
                if lifecycle:
                    record({'type': 'question_start',
                            'input': {'question': qa.question, 'category': qa.category,
                                      'reference': qa.final_answer}})
                previous = _counts(agent)
                prediction, prompt, context = agent.answer_question(
                    qa.question,
                    qa.category,
                    qa.final_answer,
                    random.Random(
                        f"{config['option_order_seed']}:{conversation['sample_index']}:{index}"
                    ),
                )
                raw_response = prediction
                try:
                    prediction = json.loads(prediction)["answer"]
                except Exception:
                    record(
                        {"type": "failure", "kind": "answer_parse", "level": "question"}
                    )
                _report_failures(ledger, previous, _counts(agent), **active)
                reference, metrics = score_fn(prediction, qa, False)
                result = {
                    "question_id": selection["question_id"],
                    "conversation_id": conversation["original_id"],
                    "original_sample_index": conversation["sample_index"],
                    "original_qa_index": index,
                    "qa": qa_raw,
                    "prediction": prediction,
                    "raw_response": raw_response,
                    "user_prompt": prompt,
                    "raw_context": context,
                    "reference": reference,
                    "metrics": metrics,
                    "category": qa.category,
                    "scoring_policy": config["scoring_policies"][0],
                    "provider_contract_policy": provider_contract_policy,
                    "metric_failures": copy.deepcopy(getattr(scorer, "failures", [])),
                }
                record(
                    {
                        "type": "question_result",
                        "question_id": selection["question_id"],
                        "result": result,
                    }
                )
            for observer_error in getattr(
                agent, "_repro_observer_errors", lambda: []
            )():
                error_type = (
                    observer_error.get("error_type")
                    if isinstance(observer_error, dict)
                    else observer_error
                )
                record(
                    {"type": "failure", "kind": "reporting", "error_type": error_type}
                )
        summary = ledger.finish()
        if lifecycle:
            ledger.record({'type': 'run_complete', 'status': summary['status'],
                           'completed_questions': summary['completed_questions']})
        return summary
    except BaseException as error:
        if "agent" in locals():
            try:
                ledger.preserve_partial_memory(
                    identity,
                    snapshot_memory(
                        agent.memory_system,
                        locals().get("outcomes", []),
                        validate=False,
                    ),
                )
            except Exception as artifact_error:
                ledger.record(
                    {
                        "type": "failure",
                        "kind": "partial_artifact",
                        "error_type": type(artifact_error).__name__,
                        **active,
                    }
                )
        ledger.record(
            {"type": "run_abort", "error_type": type(error).__name__, **active}
        )
        ledger.finish()
        raise
