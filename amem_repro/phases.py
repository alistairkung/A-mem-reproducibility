"""T5 preflight and separately approved, bounded compatibility/pilot execution.

Plans are deliberately unapproved. Nothing in this module reads a dotenv file.
The shared ledger and phase artifacts must travel with the study between machines.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import platform
import re
import socket
import time
import uuid
from unittest.mock import patch

from .config import (
    fingerprint, load_config, source_fingerprint, reject_credentials,
    STRICT_PROVIDER_POLICY, INDEX_STRING_POLICY, validate_provider_policy,
    stage_output_limits,
)
from .manifests import expand_manifest
from .preflight import (
    asset_environment, build_asset_report, make_token_counter,
    prepare_asset_layout, verify_asset_report,
)

ROOT = Path(__file__).resolve().parents[1]
PHASES = {
    "compatibility": {"population": "smoke", "calls": 44, "cap": 2},
    "pilot": {"population": "pilot", "calls": 1544, "cap": 10},
    "baseline": {"population": "fallback", "calls": 0, "cap": 42},
}


def _save(path, value):
    reject_credentials(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _replace_summary(output, summary):
    temporary = output / ".summary-updated.json"
    _save(temporary, summary)
    os.replace(temporary, output / "summary.json")


def _publish_study_phase(output, value):
    """A failed fsync must leave an unpublished temp, never a false final receipt."""
    if (output/'phase.json').exists():
        raise FileExistsError('Final study receipt already exists')
    temporary=output/('.phase-final-'+uuid.uuid4().hex+'.json')
    _save(temporary,value)
    os.replace(temporary,output/'phase.json')


def _finalize_study_phase(output, value, permit, summary, observer):
    from .budget import BudgetStop
    try:
        if value['usable_for_next_phase']:
            permit.complete_study_job(value,lambda:_publish_study_phase(output,value))
        else:
            _publish_study_phase(output,value)
    except BaseException as error:
        failure={'type':'failure','kind':'phase_finalization','error_type':type(error).__name__,
                 'level':'run','question_id':None,'conversation_id':None,'build_id':None}
        secondary={}
        try:
            permit.stop('study_finalization_failed_no_automatic_recovery')
        except BaseException as halt_error:
            secondary['halt_error_type']=type(halt_error).__name__
        try:
            if observer is not None:
                observer(failure)
                observer({'type':'run_abort','level':'run','question_id':None,'conversation_id':None,
                          'build_id':None,'execution_stage':'study_finalization','error_type':type(error).__name__})
            if summary is not None:
                summary['status']='incomplete'
                summary['failures']=[json.loads(line) for line in (output/'events.jsonl').read_text().splitlines()
                                     if json.loads(line).get('type')=='failure']
                _replace_summary(output,summary)
        except BaseException as report_error:
            secondary['report_error_type']=type(report_error).__name__
        value.update(status='incomplete',usable_for_next_phase=False,
                     error_type=value.get('error_type') or type(error).__name__,finalization_error_type=type(error).__name__)
        try:
            value['budget']=permit.summary()
            _save(output/'finalization-error.json',{'error_type':type(error).__name__,'status':'incomplete',**secondary})
            if (output/'phase.json').exists():
                os.replace(output/'phase.json',output/'phase-unconfirmed.json')
            value['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(output.iterdir()) if p.is_file() and p.name!='phase.json'}
            _publish_study_phase(output,value)
        except BaseException:
            # Missing final phase.json remains unusable; a halted/unfinished cell
            # and retained raw events/charges prohibit paid continuation.
            pass
        raise BudgetStop('Study finalization failed; paid continuation is prohibited') from error


@contextmanager
def _asset_environment(root):
    values = asset_environment(root)
    values["MPLCONFIGDIR"] = str(Path(root).resolve() / "runtime_cache/matplotlib")
    values["XDG_CACHE_HOME"] = str(Path(root).resolve() / "runtime_cache")
    with patch.dict(os.environ, values):
        yield


@contextmanager
def _deny_network():
    def deny(*args, **kwargs):
        raise RuntimeError("Network disabled during local runtime preflight")

    with patch.object(socket.socket, "connect", deny), \
         patch.object(socket.socket, "connect_ex", deny), \
         patch.object(socket, "create_connection", deny):
        yield


def _runtime_check(root):
    """Exercise original local embeddings and every author metric, without a client."""
    import math
    from .author import _load_memory
    from .scoring import AuthorScorer

    started = time.perf_counter()
    memory = _load_memory(root)
    retriever = memory.SimpleEmbeddingRetriever()
    retriever.add_documents(["A cat sat on the mat.", "Paris is a city."])
    indices = retriever.search("Where is the cat?", k=1)
    if retriever.embeddings.shape != (2, 384) or len(indices) != 1:
        raise ValueError("Original embedding/retrieval smoke failed")
    scorer = AuthorScorer(root)
    qa = scorer.qa({"question": "Where is the cat?", "answer": "The cat sat on the mat.",
                    "category": 1, "evidence": []})
    _, metrics = scorer.score("The cat sat on the mat.", qa)
    if scorer.failures or not all(math.isfinite(float(v)) for v in metrics.values()):
        raise ValueError("Original metric runtime failed; paid execution remains disabled")
    if metrics["f1"] != 1 or metrics["bert_f1"] < .99 or metrics["sbert_similarity"] < .99:
        raise ValueError("Original self-match metric smoke failed")
    # Force the WordNet resource path, which self-match METEOR can avoid.
    from nltk.corpus import wordnet
    if not wordnet.synsets("cat"):
        raise ValueError("WordNet runtime smoke failed")
    return {
        "ok": True, "network_disabled": True,
        "embedding_shape": list(retriever.embeddings.shape),
        "embedding_device": str(retriever.model.device),
        "metrics": metrics, "metric_failures": [],
        "duration_seconds": time.perf_counter() - started,
        "python": platform.python_version(), "platform": platform.platform(),
        "scorer_sha256": scorer.scorer_sha256,
    }


def preflight(asset_root, *, root=ROOT):
    """Run in a fresh process so offline/cache settings precede library imports."""
    root = Path(root)
    source = source_fingerprint(root)
    prepare_asset_layout(asset_root, root / "config/assets.json")
    report = build_asset_report(root / "config/assets.json", asset_root, lock_path=root / "uv.lock")
    receipt = {"receipt_version": 1, "assets": report, "source_sha256": fingerprint(source),
               "runtime": {"ok": False}, "paid_execution_authorized": False}
    if report["ready"]:
        with _asset_environment(asset_root), _deny_network():
            counter = make_token_counter(asset_root, report, root / "config/assets.json")
            if counter.count("A cat sat on the mat.") <= 0:
                raise ValueError("Local tokenizer smoke failed")
            receipt["runtime"] = _runtime_check(root)
    return receipt


def _verified_receipt(receipt, asset_root, root):
    if receipt.get("receipt_version") != 1 or receipt.get("runtime", {}).get("ok") is not True:
        raise ValueError("Successful local metric/embedding runtime preflight is required")
    if receipt["runtime"].get("network_disabled") is not True:
        raise ValueError("Runtime preflight must have disabled network access")
    verify_asset_report(receipt["assets"], asset_root, root / "config/assets.json")
    source = source_fingerprint(root)
    if receipt.get("source_sha256") != fingerprint(source):
        raise ValueError("Code/configuration changed since runtime preflight")
    return source


def _verified_phase(path, root):
    path = Path(path).resolve()
    if not path.is_relative_to((root / "artifacts/runs").resolve()):
        raise ValueError("Phase receipt must belong to this study's archived runs")
    if (path.parent/'finalization-error.json').exists():
        raise ValueError('Failed phase finalization cannot supply a completed phase')
    value = json.loads(path.read_text())
    required = {"approval.json", "preflight.json", "events.jsonl", "summary.json", "run.json", "scoring-views.json"}
    if not required.issubset(value.get("artifact_sha256", {})):
        raise ValueError("Incomplete phase artifact inventory")
    for name, digest in value["artifact_sha256"].items():
        if Path(name).name != name or hashlib.sha256((path.parent / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Archived phase artifact changed")
    if not value.get("usable_for_next_phase"):
        raise ValueError("A completed verified phase is required")
    approval = json.loads((path.parent / "approval.json").read_text())
    if (approval.get("approved") is not True or approval["binding"] != value["binding"]
            or approval["run_id"] != value["run_id"] or approval["phase"] != value["phase"]):
        raise ValueError("Archived phase approval/provenance differs")
    return value


def _phase_inputs(phase, receipt, asset_root, root, compatibility=None, *,
                  provider_contract_policy=STRICT_PROVIDER_POLICY, checkpoint=None,
                  condition='full', conversation_id=None):
    validate_provider_policy(provider_contract_policy)
    if phase == 'baseline':
        if compatibility is not None:
            raise ValueError('Main execution cannot reuse a fixture approval')
        from .study import baseline_inputs
        return baseline_inputs(receipt,asset_root,root,condition,conversation_id,provider_contract_policy,checkpoint=checkpoint)
    if condition != 'full' or conversation_id is not None:
        raise ValueError('Only baseline phases support complete-conversation partitions/action conditions')
    if phase not in PHASES:
        raise ValueError("Only separately approved compatibility and pilot phases are enabled")
    spec = PHASES[phase]
    sources = _verified_receipt(receipt, asset_root, root)
    config = load_config(root / "config/study.json")
    compact = json.loads((root / "manifests" / (spec["population"] + ".json")).read_text())
    manifest = expand_manifest(root / "data/locomo10.json", compact)
    binding = {
        "manifest_sha256": fingerprint(manifest), "config_sha256": fingerprint(config),
        "source_sha256": fingerprint(sources), "preflight_sha256": fingerprint(receipt),
        "condition": "full", "repetition": 0, "population": spec["population"],
        "model": config["model"]["id"],
        "endpoint": config["model"]["base_url"] + config["model"]["route"],
        "provider_contract_policy": provider_contract_policy,
        "max_output_tokens_by_stage": stage_output_limits(),
    }
    if phase == "pilot":
        if compatibility is None:
            raise ValueError("Archive successful strict-schema compatibility before the paid pilot")
        previous = _verified_phase(compatibility, root)
        if previous["phase"] != "compatibility":
            raise ValueError("The pilot requires a compatibility receipt")
        if checkpoint is None:
            for key in ("config_sha256", "source_sha256", "preflight_sha256", "model", "endpoint",
                        "provider_contract_policy", "max_output_tokens_by_stage"):
                if previous["binding"].get(key) != binding[key]:
                    raise ValueError("Compatibility provenance differs; stop for review")
        else:
            from .checkpoint import verify_checkpoint
            recovered = verify_checkpoint(checkpoint, root, manifest, config, sources, receipt, previous)
            if (recovered['phase']['binding']['provider_contract_policy'] != provider_contract_policy
                    or recovered['phase']['binding']['max_output_tokens_by_stage'] != stage_output_limits()):
                raise ValueError('Checkpoint provider policy differs')
            binding['checkpoint'] = recovered['lineage']
        binding["compatibility_sha256"] = fingerprint(previous)
    elif checkpoint is not None:
        raise ValueError('Only the pilot supports checkpoint recovery')
    return config, manifest, sources, binding


def plan_phase(phase, receipt, asset_root, *, run_id=None, root=ROOT, compatibility=None,
               provider_contract_policy=STRICT_PROVIDER_POLICY, checkpoint=None,
               condition='full', conversation_id=None):
    root = Path(root)
    _, manifest, _, binding = _phase_inputs(
        phase, receipt, asset_root, root, compatibility,
        provider_contract_policy=provider_contract_policy,
        checkpoint=checkpoint,
        condition=condition, conversation_id=conversation_id,
    )
    run_id = run_id or f"{phase}-{uuid.uuid4().hex[:12]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", run_id):
        raise ValueError("run_id must be a safe, unique local artifact name")
    spec = PHASES[phase]
    calls = binding.get('checkpoint',{}).get('remaining_logical_calls',
                binding.get('study_job',{}).get('expected_logical_calls',spec['calls']))
    cap = spec['cap']
    population = manifest['totals']
    if phase == 'baseline':
        from .budget import STUDY_JOB_CAPS, MICROS
        from decimal import Decimal
        cap = str(Decimal(STUDY_JOB_CAPS[(binding['condition'],binding['study_job']['conversation_id'])])/MICROS)
        selected = next(c for c in manifest['conversations'] if c['original_id']==binding['study_job']['conversation_id'])
        population = {'conversations':1,'turns':len(selected['turn_ids'])-binding.get('checkpoint',{}).get('completed_turns',0),'questions':len(selected['questions'])}
    return {
        "approval_id": str(uuid.uuid4()), "approved": False,
        "approved_by": None, "approved_at": None, "run_id": run_id, "phase": phase,
        "binding": binding,
        "limits": {"phase_usd": cap, "max_logical_calls": calls,
                   "max_attempts": calls * 3},
        "pricing": {
            "pricing_id": "deepseek-flash-peak-2026-11-01",
            "source": "https://api-docs.deepseek.com/quick_start/pricing/",
            "input_per_million": .30, "output_per_million": 1.20,
            "max_context_tokens": 1048576, "max_output_tokens": max(stage_output_limits().values()),
        },
        "population": population,
        "stop_policy": "No subsequent request after provider/contract failure; no automatic recovery",
        "token_count_limitation": receipt["assets"]["tokenizer_limitation"],
    }


def execute_phase(approval, receipt, asset_root, *, root=ROOT, compatibility=None, checkpoint=None):
    """No paid request occurs until explicit approval and all bindings verify.

    The caller supplies a reviewed approval artifact. Implementation permission,
    API credentials and an unapproved plan are individually insufficient.
    """
    from .budget import PhasePermit, ledger_summary, validate_approval
    from .adapter import create_deepseek_controller
    from .author import make_agent_factory
    from .runner import run_manifest
    from .scoring import AuthorScorer, rescore_records

    root = Path(root)
    provider_contract_policy = approval["binding"].get("provider_contract_policy", STRICT_PROVIDER_POLICY)
    config, manifest, sources, binding = _phase_inputs(
        approval["phase"], receipt, asset_root, root, compatibility,
        provider_contract_policy=provider_contract_policy,
        checkpoint=checkpoint,
        condition=approval['binding'].get('condition','full'),
        conversation_id=approval['binding'].get('study_job',{}).get('conversation_id'),
    )
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", approval["run_id"]):
        raise ValueError("Invalid run identity")
    output = root / "artifacts/runs" / approval["run_id"]
    if output.exists():
        raise FileExistsError("Existing run requires separately approved recovery")
    validate_approval(approval, binding)
    recovered = None
    if checkpoint is not None:
        from .checkpoint import verify_checkpoint,verify_study_checkpoint
        recovered = (verify_study_checkpoint(checkpoint,root,manifest,config,sources,receipt)
                     if approval['phase']=='baseline' else
                     verify_checkpoint(checkpoint,root,manifest,config,sources,receipt,
                                       _verified_phase(compatibility,root)))
        if (approval['limits']['max_logical_calls'] > binding['checkpoint']['remaining_logical_calls']
                or approval['limits']['max_attempts'] > 3 * binding['checkpoint']['remaining_logical_calls']):
            raise ValueError('Recovery request limits exceed remaining workload')
    elif 'checkpoint' in approval['binding']:
        raise ValueError('Checkpoint-bound approval requires its parent')
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY is required in the environment")
    # A single fixed study ledger prevents a fresh per-run file resetting spending.
    ledger_path = root / "artifacts/study-budget.sqlite"
    permit = PhasePermit(approval, ledger_path, binding)
    output.mkdir(parents=True)
    _save(output / "approval.json", approval)
    _save(output / "preflight.json", receipt)
    if recovered is not None:
        _save(output / 'checkpoint.json', recovered['lineage'])
    clients = []
    versions, fingerprints, schema_outcomes = set(), set(), {}
    if approval['phase'] == 'baseline':
        versions.update(binding['expected_returned_models'])
        fingerprints.update(binding['expected_system_fingerprints'])
    deviations = {"completions": 0, "items": 0}
    inherited_deviations = [e for e in recovered['failures']
                           if e.get('kind') == 'provider_contract_deviation'] if recovered else []
    if compatibility is not None:
        previous = _verified_phase(compatibility, root)
        versions.update(previous["returned_models"])
        fingerprints.update(previous["system_fingerprints"])

    def controller(observer):
        def durable_journal(event):
            from .budget import BudgetStop
            try:
                observer(event)
            except BudgetStop:
                raise
            except BaseException as error:
                try:
                    permit.stop('critical_generation_journal_failed')
                except BaseException:
                    pass
                try:
                    _save(output/('generation-journal-failure-'+uuid.uuid4().hex+'.json'),
                          {'error_type':type(error).__name__,'event':event})
                except BaseException:
                    pass
                raise BudgetStop('Critical generation journal failed; no paid continuation') from error
        c = create_deepseek_controller(paid_authorized=True,
                                       observer=durable_journal if approval['phase']=='baseline' else observer, phase_permit=permit,
                                       provider_contract_policy=provider_contract_policy)
        clients.append(c.client)
        return c

    def observe(event):
        if event.get("type") != "generation":
            return
        stage = event["stage"]
        schema_outcomes.setdefault(stage, {
            "raw_valid": 0, "accepted_with_deviation": 0, "rejected": 0, "not_transmitted": 0,
        })
        if event.get("error_type"):
            outcome = "rejected" if event.get("attempts") else "not_transmitted"
        else:
            outcome = "accepted_with_deviation" if event.get("compatibility_deviation") else "raw_valid"
        schema_outcomes[stage][outcome] += 1
        if event.get("compatibility_deviation"):
            deviations["completions"] += 1
            deviations["items"] += len(event["compatibility_deviation"]["transformations"])
        if approval['phase']=='baseline':
            for field,expected in (('returned_model',binding['expected_returned_models']),
                                   ('system_fingerprint',binding['expected_system_fingerprints'])):
                actual=event.get(field)
                if type(actual) is not str or not actual or actual not in expected:
                    permit.stop('provider_model_or_fingerprint_invalid_or_changed')
                    return  # No set insertion or other potentially failing metadata work.
        if event.get("returned_model"):
            versions.add(event["returned_model"])
        if event.get("system_fingerprint"):
            fingerprints.add(event["system_fingerprint"])
        if len(versions) > 1 or len(fingerprints) > 1:
            permit.stop("provider_model_or_fingerprint_changed")
        if event.get("usage") is None:
            permit.stop("missing_provider_usage")

    summary, error_type = None, None
    try:
        with _asset_environment(asset_root):
            counter = make_token_counter(asset_root, receipt["assets"], root / "config/assets.json")
            scorer = AuthorScorer(root)
            if approval['phase']=='baseline' and binding['condition']!='full':
                from .actions import make_action_agent_factory
                factory=make_action_agent_factory(root,condition=binding['condition'],controller_factory=controller,token_counter=counter)
            else:
                factory = make_agent_factory(root, controller_factory=controller, token_counter=counter)
            summary = run_manifest(
                root / "data/locomo10.json", manifest, config,
                output_dir=output, cache_root=root / "artifacts/cache", source_hashes=sources,
                agent_factory=factory, scorer=scorer, observer=observe, run_id=approval["run_id"],
                provider_contract_policy=provider_contract_policy,
                execution_type='checkpoint_recovery' if recovered else 'fresh_build',
                checkpoint=recovered,
                condition=binding['condition'],
                conversation_ids=binding.get('conversation_ids'),
            )
            if approval['phase']=='baseline' and (permit.summary().get('halted') or permit.summary()['unknown_attempts']):
                from .budget import BudgetStop
                raise BudgetStop('Halted study phase cannot be completed or continue to another cell')
            events = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
            # The two views consume saved predictions and cannot make model calls.
            predictions = [e["result"] for e in events if e["type"] == "question_result"]
            # The runner's callback still has its last-question context. Collect
            # rescore failures from each saved row instead, then record their
            # actual question/policy without modifying original predictions.
            inference_observer = scorer.observer
            scorer.observer = None
            try:
                views = rescore_records(predictions, scorer)
            finally:
                scorer.observer = inference_observer
            rescore_failures = []
            for policy, view in views.items():
                for row in view["individual_results"]:
                    for failure in row["metric_failures"]:
                        notice = {**failure, "question_id": row["question_id"],
                                  "conversation_id": row["conversation_id"],
                                  "scoring_policy": policy, "execution_stage": "rescoring"}
                        inference_observer(notice)
                        rescore_failures.append(notice)
            if rescore_failures:
                events = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
                summary["status"] = "degraded"
                summary["failures"] = [e for e in events if e["type"] == "failure"]
                _replace_summary(output, summary)
            _save(output / "scoring-views.json", views)
    except BaseException as error:
        error_type = type(error).__name__
        permit.stop("phase_aborted_no_automatic_recovery")
        if summary is not None:
            # Inference completed, but its required saved-output processing did
            # not. Keep the original question records and charges, and classify
            # the overall run consistently with the incomplete phase receipt.
            scorer.observer({"type": "run_abort", "error_type": error_type,
                             "level": "run", "question_id": None,
                             "conversation_id": None, "build_id": None,
                             "execution_stage": "phase_validation" if permit.summary().get('halted') and approval['phase']=='baseline' else "postprocessing"})
            summary["status"] = "incomplete"
            _replace_summary(output, summary)
        raise
    finally:
        for client in clients:
            client.close()
        if summary is None and (output/'summary.json').exists():
            try:
                summary=json.loads((output/'summary.json').read_text())
            except (OSError,ValueError):
                pass  # Unreadable partial accounting never becomes a completed phase.
        budget = permit.summary()
        phase_result = {
            "phase": approval["phase"], "run_id": approval["run_id"],
            "population": binding["population"],
            "conversation_ids": binding.get('conversation_ids',[c["original_id"] for c in manifest["conversations"]]),
            "binding": binding, "status": summary["status"] if summary and error_type is None else "incomplete",
            "provider_contract_policy": provider_contract_policy,
            "provider_contract_deviation_count": deviations["completions"],
            "validation_copy_transformed_item_count": deviations["items"],
            'inherited_provider_contract_deviation_count': len(inherited_deviations),
            'inherited_validation_copy_transformed_item_count': sum(
                len(e['compatibility_deviation']['transformations']) for e in inherited_deviations),
            "expected_questions": binding.get('expected_questions',manifest["totals"]["questions"]),
            "completed_questions": summary["completed_questions"] if summary else 0,
            "error_type": error_type, "budget": budget,
            "study_budget": ledger_summary(ledger_path),
            "schema_outcomes": schema_outcomes,
            "usable_for_next_phase": bool(summary and not budget["halted"]
                and budget["unknown_attempts"] == 0
                and error_type is None and summary['status'] in ('complete', 'degraded')
                and budget["logical_calls"] == binding.get('checkpoint',{}).get('remaining_logical_calls',
                    binding.get('study_job',{}).get('expected_logical_calls',PHASES[approval["phase"]]["calls"]))
                and set(schema_outcomes) == {"metadata", "shared_decision", "query_keywords", "answer"}),
            "returned_models": sorted(versions), "system_fingerprints": sorted(fingerprints),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "artifact_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(output.iterdir()) if p.is_file()},
        }
        if approval['phase']=='baseline':
            _finalize_study_phase(output,phase_result,permit,summary,getattr(locals().get('scorer'),'observer',None))
        else:
            _save(output / "phase.json", phase_result)
    return phase_result


def forecast_pilot(path, *, root=ROOT, provider_contract_policy=STRICT_PROVIDER_POLICY):
    """Read cost evidence only; never select from quality results or execute a run."""
    from .budget import ledger_summary
    from .forecast import forecast_scope

    validate_provider_policy(provider_contract_policy)
    root = Path(root)
    pilot = _verified_phase(path, root)
    if pilot["phase"] != "pilot":
        raise ValueError("A completed cost pilot is required")
    current_sources = fingerprint(source_fingerprint(root))
    config = load_config(root / "config/study.json")
    manifest = expand_manifest(root / "data/locomo10.json", json.loads((root / "manifests/pilot.json").read_text()))
    reusable = (pilot["binding"]["source_sha256"] == current_sources
                and pilot["binding"]["config_sha256"] == fingerprint(config)
                and pilot["binding"]["manifest_sha256"] == fingerprint(manifest)
                and pilot["binding"]["condition"] == "full" and pilot["binding"]["repetition"] == 0
                and pilot["binding"].get("provider_contract_policy", STRICT_PROVIDER_POLICY) == provider_contract_policy)
    # Read generation records only. Do not read the saved scoring views or predictions.
    events = (json.loads(line) for line in (Path(path).parent / "events.jsonl").read_text().splitlines())
    generations = [event for event in events if event.get("type") == "generation"]
    retained_failure = None
    if 'checkpoint' in pilot['binding']:
        from .checkpoint import verify_checkpoint
        lineage = pilot['binding']['checkpoint']
        def archived(run_id):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', run_id):
                raise ValueError('Invalid checkpoint archive identity')
            return root / 'artifacts/runs' / run_id / 'phase.json'
        child_start = json.loads((Path(path).parent / 'events.jsonl').open().readline())
        recovered = verify_checkpoint(
            archived(lineage['parent_run_id']), root, manifest, config,
            child_start['source_hashes'], json.loads((Path(path).parent / 'preflight.json').read_text()),
            _verified_phase(archived(lineage['compatibility_run_id']), root))
        if recovered['lineage'] != lineage:
            raise ValueError('Recovered pilot lineage differs')
        generations = recovered['generations'] + generations
        retained_failure = fingerprint(recovered['generations'][-1])
    result = forecast_scope(generations, pilot, ledger_summary(root / "artifacts/study-budget.sqlite"),
                            pilot_reusable=reusable, retained_failure_sha256=retained_failure)
    result["pilot_receipt_sha256"] = fingerprint(pilot)
    result["provider_contract_policy"] = provider_contract_policy
    if retained_failure is not None:
        result['retained_checkpoint_failure_sha256'] = retained_failure
        result['checkpoint'] = pilot['binding']['checkpoint']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("preflight")
    check.add_argument("--assets", required=True)
    check.add_argument("--output", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--phase", choices=PHASES, required=True)
    plan.add_argument("--run-id")
    plan.add_argument("--assets", required=True)
    plan.add_argument("--preflight", required=True)
    plan.add_argument("--compatibility")
    plan.add_argument('--checkpoint', help='Immutable incomplete conv-50 parent phase.json')
    plan.add_argument("--provider-contract-policy", choices=(STRICT_PROVIDER_POLICY, INDEX_STRING_POLICY),
                      default=STRICT_PROVIDER_POLICY)
    plan.add_argument("--output", required=True)
    run = sub.add_parser("execute")
    run.add_argument("--approval", required=True)
    run.add_argument("--assets", required=True)
    run.add_argument("--preflight", required=True)
    run.add_argument("--compatibility")
    run.add_argument('--checkpoint')
    forecast = sub.add_parser("forecast")
    forecast.add_argument("--pilot", required=True)
    forecast.add_argument("--provider-contract-policy", choices=(STRICT_PROVIDER_POLICY, INDEX_STRING_POLICY),
                          default=STRICT_PROVIDER_POLICY)
    forecast.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        result = preflight(args.assets)
        _save(args.output, result)
        print(json.dumps({"ready": result["assets"]["ready"], "runtime": result["runtime"]["ok"]}))
    elif args.command == "plan":
        receipt = json.loads(Path(args.preflight).read_text())
        result = plan_phase(args.phase, receipt, args.assets, run_id=args.run_id,
                            compatibility=args.compatibility, provider_contract_policy=args.provider_contract_policy,
                            checkpoint=args.checkpoint)
        _save(args.output, result)
        print(json.dumps({"approved": False, "phase": args.phase, "limits": result["limits"]}))
    elif args.command == "execute":
        approval = json.loads(Path(args.approval).read_text())
        receipt = json.loads(Path(args.preflight).read_text())
        print(json.dumps(execute_phase(approval, receipt, args.assets, compatibility=args.compatibility,
                                      checkpoint=args.checkpoint)))
    else:
        result = forecast_pilot(args.pilot, provider_contract_policy=args.provider_contract_policy)
        _save(args.output, result)
        print(json.dumps({"recommended_population": result["recommended_population"],
                          "requires_main_execution_approval": True}))


if __name__ == "__main__":
    main()
