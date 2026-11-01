"""Approved D9a changes only the shared-decision output allowance."""

import json

import pytest

from amem_repro.adapter import DeepSeekController
from amem_repro.contracts import load_author_contracts
from test_adapter import Client, completion


@pytest.mark.parametrize("stage,value,limit", [
    ("metadata", {"keywords": [], "context": "context", "tags": []}, 1000),
    ("shared_decision", {"should_evolve": False, "actions": [], "suggested_connections": [],
                         "tags_to_update": [], "new_context_neighborhood": [],
                         "new_tags_neighborhood": []}, 4000),
    ("query_keywords", {"keywords": "query"}, 1000),
    ("answer", {"answer": "saved"}, 1000),
])
def test_wire_and_observations_use_approved_stage_limit_without_changing_raw_contract(stage, value, limit):
    raw = " \n" + json.dumps(value, indent=2) + "\n "
    client, events = Client(completion(raw)), []
    contract = load_author_contracts()[stage]
    assert DeepSeekController(client, observer=events.append).get_completion("same prompt", contract) == raw
    assert len(client.requests) == 1
    assert client.requests[0]["max_tokens"] == events[0]["max_tokens"] == limit
    assert client.requests[0]["temperature"] == .7
    assert client.requests[0]["tools"][0]["function"]["parameters"] == contract["json_schema"]["schema"]
    assert events[0]["output"] == raw


def test_unapproved_plan_binds_exact_stage_limits_and_conservative_output_bound(tmp_path):
    from pathlib import Path
    from unittest.mock import patch
    from amem_repro import phases

    root = Path(__file__).resolve().parents[1]
    with patch.object(phases, "_verified_receipt", return_value={"test": "source"}):
        plan = phases.plan_phase("compatibility", {"assets": {"tokenizer_limitation": "offline"}},
                                 tmp_path / "assets", root=root)
    assert plan["approved"] is False
    assert plan["binding"]["max_output_tokens_by_stage"] == {
        "metadata": 1000, "shared_decision": 4000, "query_keywords": 1000, "answer": 1000,
    }
    assert plan["pricing"]["max_output_tokens"] == 4000
    assert plan["limits"] == {"phase_usd": 2, "max_logical_calls": 44, "max_attempts": 132}


def test_cost_forecast_accepts_approved_shared_decision_usage_above_1000():
    from amem_repro.forecast import forecast_scope
    from test_forecast import pilot_events, pilot_summary, ledger

    events = list(pilot_events())
    decision = next(e for e in events if e["stage"] == "shared_decision")
    decision["attempts"][0]["usage"]["completion_tokens"] = 4000
    forecast = forecast_scope(events, pilot_summary(), ledger(), pilot_reusable=False)
    assert forecast["pilot_stage_usage"]["shared_decision"]["output_tokens"] == 60700


@pytest.mark.parametrize("stage,output", [("shared_decision", 4001), ("metadata", 1001),
                                         ("query_keywords", 1001), ("answer", 1001)])
def test_cost_forecast_rejects_usage_outside_each_approved_stage(stage, output):
    from amem_repro.forecast import forecast_scope
    from test_forecast import pilot_events, pilot_summary, ledger

    events = list(pilot_events())
    target = next(e for e in events if e["stage"] == stage)
    target["attempts"][0]["usage"]["completion_tokens"] = output
    with pytest.raises(ValueError, match="usage"):
        forecast_scope(events, pilot_summary(), ledger(), pilot_reusable=False)
