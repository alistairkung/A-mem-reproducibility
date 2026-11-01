"""Paid-phase boundaries exercised through the SDK with deterministic local responses."""
import copy
import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from amem_repro import phases
from amem_repro.adapter import create_deepseek_controller
from amem_repro.author import make_agent_factory
from amem_repro.budget import BudgetStop, ledger_summary
from amem_repro.config import DEFAULT_CONFIG, fingerprint
from amem_repro.manifests import build_manifest
from amem_repro.measurements import TokenCounter
from amem_repro.scoring import AuthorScorer, rescore_records
from test_foundation import Provider, original_memory_module
from test_scoring import dependencies

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    manifest = build_manifest(ROOT / "data/locomo10.json", "smoke")
    sources = {"offline-test": "only"}
    binding = {
        "manifest_sha256": fingerprint(manifest), "source_sha256": fingerprint(sources),
        "config_sha256": fingerprint(DEFAULT_CONFIG), "preflight_sha256": "b" * 64,
        "condition": "full", "repetition": 0, "population": "smoke",
        "model": "deepseek-flash", "endpoint": "https://api.deepseek.com/beta/chat/completions",
    }
    return DEFAULT_CONFIG, manifest, sources, binding


def plan(tmp_path):
    with patch.object(phases, "_phase_inputs", return_value=inputs()):
        return phases.plan_phase("compatibility", {"assets": {"tokenizer_limitation": "test only"}},
                                 tmp_path / "assets", root=tmp_path, run_id="offline-test")


def test_plan_is_not_permission_to_spend(tmp_path):
    proposal = plan(tmp_path)
    assert proposal["approved"] is False
    assert proposal["limits"] == {"phase_usd": 2, "max_logical_calls": 44, "max_attempts": 132}
    with patch.object(phases, "_phase_inputs", return_value=inputs()), \
         patch("amem_repro.adapter.os.environ.get", side_effect=AssertionError("credential read")):
        with pytest.raises(BudgetStop, match="approval"):
            phases.execute_phase(proposal, {}, tmp_path / "assets", root=tmp_path)
    assert ledger_summary(tmp_path / "artifacts/study-budget.sqlite")["physical_attempts"] == 0


def test_runtime_preflight_is_required_before_planning(tmp_path):
    with pytest.raises(ValueError, match="runtime preflight"):
        phases.plan_phase("compatibility", {"runtime": {"ok": False}}, tmp_path / "assets")


def test_pilot_cannot_skip_compatibility(tmp_path):
    with patch.object(phases, "_verified_receipt", return_value={"test": "only"}):
        with pytest.raises(ValueError, match="compatibility"):
            phases.plan_phase("pilot", {}, tmp_path / "assets")


def test_approved_binding_mismatch_stops_before_credentials(tmp_path):
    proposal = plan(tmp_path)
    proposal.update(approved=True, approved_by="offline test", approved_at="2026-11-01T00:00:00Z")
    proposal["binding"]["manifest_sha256"] = "c" * 64
    with patch.object(phases, "_phase_inputs", return_value=inputs()), \
         patch("amem_repro.adapter.os.environ.get", side_effect=AssertionError("credential read")):
        with pytest.raises(BudgetStop, match="binding mismatch"):
            phases.execute_phase(proposal, {}, tmp_path / "assets", root=tmp_path)


def test_missing_credentials_do_not_claim_approval_or_create_run_artifacts(tmp_path):
    proposal = plan(tmp_path)
    proposal.update(approved=True, approved_by="offline test", approved_at="2026-11-01T00:00:00Z")
    from types import SimpleNamespace

    with patch.object(phases, "_phase_inputs", return_value=inputs()), \
         patch.object(phases, "make_token_counter", return_value=TokenCounter(str.split, "offline", "test")), \
         patch("amem_repro.scoring.AuthorScorer", return_value=SimpleNamespace()), \
         patch("amem_repro.author.make_agent_factory", side_effect=ValueError("DEEPSEEK_API_KEY is required")), \
         patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            phases.execute_phase(proposal, {"assets": {}}, tmp_path / "assets", root=tmp_path)
    assert not (tmp_path / "artifacts/study-budget.sqlite").exists()
    assert not (tmp_path / "artifacts/runs/offline-test").exists()


@pytest.mark.parametrize("rescore_failure", [False, True, "abort"])
def test_complete_fixture_archives_original_outputs_and_cannot_restart(tmp_path, rescore_failure):
    (tmp_path / "data").symlink_to(ROOT / "data", target_is_directory=True)
    proposal = plan(tmp_path)
    proposal.update(approved=True, approved_by="offline test", approved_at="2026-11-01T00:00:00Z")
    provider = Provider()

    def sdk_handler(request):
        return httpx.Response(200, json=provider.complete(**json.loads(request.content)))

    def controller(**kwargs):
        return create_deepseek_controller(**kwargs, http_transport=httpx.MockTransport(sdk_handler))

    def factory(root, **kwargs):
        return make_agent_factory(ROOT, memory_module=original_memory_module(), **kwargs)

    metric_dependencies = dependencies()
    bert = metric_dependencies["bert_score"]
    metric_calls = 0

    def transient_metric(*args, **kwargs):
        nonlocal metric_calls
        metric_calls += 1
        if rescore_failure is True and metric_calls == 5:
            raise RuntimeError("offline failure only during first saved-output rescore")
        return bert(*args, **kwargs)

    metric_dependencies["bert_score"] = transient_metric

    def rescore(*args, **kwargs):
        if rescore_failure == "abort":
            raise RuntimeError("offline post-inference export/scoring failure")
        return rescore_records(*args, **kwargs)

    with patch.object(phases, "_phase_inputs", return_value=inputs()), \
         patch("amem_repro.adapter.create_deepseek_controller", side_effect=controller), \
         patch("amem_repro.author.make_agent_factory", side_effect=factory), \
         patch.object(phases, "make_token_counter", return_value=TokenCounter(str.split, "offline", "test")), \
         patch("amem_repro.scoring.AuthorScorer", side_effect=lambda root: AuthorScorer(ROOT, dependencies=metric_dependencies)), \
         patch("amem_repro.scoring.rescore_records", side_effect=rescore), \
         patch.dict("os.environ", {"DEEPSEEK_API_KEY": "offline-placeholder"}):
        if rescore_failure == "abort":
            with pytest.raises(RuntimeError, match="post-inference"):
                phases.execute_phase(proposal, {"assets": {}}, tmp_path / "assets", root=tmp_path)
            result = json.loads((tmp_path / "artifacts/runs/offline-test/phase.json").read_text())
        else:
            result = phases.execute_phase(proposal, {"assets": {}}, tmp_path / "assets", root=tmp_path)
        expected_status = "incomplete" if rescore_failure == "abort" else "degraded" if rescore_failure else "complete"
        assert result["status"] == expected_status
        assert result["usable_for_next_phase"] is (rescore_failure != "abort")
        assert result["completed_questions"] == 4
        assert result["budget"]["physical_attempts"] == 44
        assert set(result["schema_outcomes"]) == {"metadata", "shared_decision", "query_keywords", "answer"}
        if rescore_failure != "abort":
            assert phases._verified_phase(tmp_path / "artifacts/runs/offline-test/phase.json", tmp_path) == result
        before = copy.deepcopy(provider.requests)
        with pytest.raises(FileExistsError):
            phases.execute_phase(proposal, {"assets": {}}, tmp_path / "assets", root=tmp_path)
        assert provider.requests == before
    if rescore_failure != "abort":
        archived = (tmp_path / "artifacts/runs/offline-test/scoring-views.json").read_text()
        assert "author-corrected-v1" in archived and "author-legacy-c5-v1" in archived
        assert "offline-placeholder" not in archived
    events_path = tmp_path / "artifacts/runs/offline-test/events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()]
    saved = [event["result"] for event in events if event["type"] == "question_result"]
    assert [row["prediction"] for row in saved] == ["saved"] * 4
    assert saved[0]["metrics"]["bert_f1"] == .8
    assert saved[0]["metric_failures"] == []
    summary = json.loads((events_path.parent / "summary.json").read_text())
    assert summary["status"] == result["status"]
    if rescore_failure is True:
        failures = [event for event in events if event.get("kind") == "metric_computation"]
        assert len(failures) == 1
        assert failures[0]["question_id"] == "conv-26:qa:0"
        assert failures[0]["scoring_policy"] == "author-corrected-v1"
        assert summary["failures"][0]["question_id"] == "conv-26:qa:0"
    elif rescore_failure == "abort":
        aborts = [event for event in events if event["type"] == "run_abort"]
        assert len(aborts) == 1
        assert aborts[0]["execution_stage"] == "postprocessing"
    events_path.write_text(events_path.read_text() + "\n")
    with pytest.raises(ValueError, match="Incomplete phase artifact" if rescore_failure == "abort" else "artifact changed"):
        phases._verified_phase(tmp_path / "artifacts/runs/offline-test/phase.json", tmp_path)
