"""Cost evidence selects a frozen population without inspecting model quality."""

from amem_repro.forecast import forecast_scope
import pytest


def pilot_events(prompt_tokens=1000, completion_tokens=100):
    for stage, count in {
        "metadata": 568, "shared_decision": 568,
        "query_keywords": 204, "answer": 204,
    }.items():
        for _ in range(count):
            yield {"type": "generation", "stage": stage, "attempts": [{
                "usage": {"prompt_tokens": prompt_tokens,
                          "completion_tokens": completion_tokens},
            }]}


def pilot_summary():
    return {"status": "complete", "population": "pilot",
            "conversation_ids": ["conv-50"], "expected_questions": 204,
            "completed_questions": 204}


def ledger(spent=1):
    return {"charged_or_reserved_microusd": spent * 1_000_000,
            "unknown_attempts": 0}


def test_prefers_primary_when_planning_total_fits_but_sensitivity_does_not():
    result = forecast_scope(list(pilot_events()), pilot_summary(), ledger(),
                            pilot_reusable=True)
    assert result["recommended_population"] == "full"
    assert result["requires_main_execution_approval"] is True
    assert result["populations"]["fallback"]["conversation_ids"] == [
        "conv-49", "conv-50", "conv-44"]
    assert result["populations"]["full"]["remaining_logical_calls"] == 61400
    assert result["populations"]["fallback"]["remaining_logical_calls"] == 16936
    assert result["populations"]["full"]["sensitivity_total_usd"] == "60.576000"
    assert result["populations"]["fallback"]["sensitivity_total_usd"] == "23.226240"
    assert result["populations"]["full"]["fits_planning_ceiling"] is True
    assert result["populations"]["full"]["fits_sensitivity_ceiling"] is False
    assert result["full_mode_is_upper_bound"] is False


def test_recommends_only_predefined_fallback_when_primary_planning_total_exceeds_cap():
    result = forecast_scope(list(pilot_events(2000, 100)), pilot_summary(), ledger(2),
                            pilot_reusable=True)
    assert result["recommended_population"] == "fallback"
    assert result["populations"]["full"]["point_total_usd"] == "54.208000"
    assert result["populations"]["full"]["fits_planning_ceiling"] is False
    assert result["populations"]["fallback"]["point_total_usd"] == "22.193920"
    assert result["populations"]["fallback"]["fits_planning_ceiling"] is True


@pytest.mark.parametrize("change", [
    lambda events, summary, costs: summary.update(status="incomplete"),
    lambda events, summary, costs: summary.update(population="smoke"),
    lambda events, summary, costs: summary.update(conversation_ids=["conv-49"]),
    lambda events, summary, costs: summary.update(completed_questions=203),
    lambda events, summary, costs: costs.update(unknown_attempts=1),
    lambda events, summary, costs: events.pop(),
    lambda events, summary, costs: events[0].update(error_type="AdapterError"),
    lambda events, summary, costs: events[0]["attempts"][0].update(usage=None),
])
def test_refuses_scope_selection_without_complete_known_pilot_cost(change):
    events, summary, costs = list(pilot_events()), pilot_summary(), ledger()
    change(events, summary, costs)
    with pytest.raises(ValueError):
        forecast_scope(events, summary, costs, pilot_reusable=True)


@pytest.mark.parametrize("bad_usage", [
    {"prompt_tokens": -1, "completion_tokens": 100},
    {"prompt_tokens": True, "completion_tokens": 100},
    {"prompt_tokens": float("nan"), "completion_tokens": 100},
    {"prompt_tokens": 1048577, "completion_tokens": 100},
    {"prompt_tokens": 1000, "completion_tokens": 1001},
    {"prompt_tokens": 1000, "completion_tokens": 100, "total_tokens": 1},
    {"completion_tokens": 100},
])
def test_refuses_untrusted_usage_instead_of_an_affordable_forecast(bad_usage):
    events = list(pilot_events())
    events[0]["attempts"][0]["usage"] = bad_usage
    with pytest.raises(ValueError):
        forecast_scope(events, pilot_summary(), ledger(), pilot_reusable=True)


@pytest.mark.parametrize("overrides", [
    {"safety_multiplier": 0}, {"safety_multiplier": float("nan")},
    {"safety_multiplier": True}, {"pilot_reusable": "yes"},
])
def test_requires_explicit_valid_planning_assumptions(overrides):
    kwargs = {"pilot_reusable": True, **overrides}
    with pytest.raises(ValueError):
        forecast_scope(list(pilot_events()), pilot_summary(), ledger(), **kwargs)


def test_low_cost_prefers_full_and_never_reads_saved_quality_fields():
    class Unreadable:
        def __getitem__(self, key):
            raise AssertionError("quality fields must remain unread")

    events = list(pilot_events(20, 5))
    events.append({"type": "question_result", "result": Unreadable()})
    result = forecast_scope(events, pilot_summary(), ledger(), pilot_reusable=False)
    assert result["recommended_population"] == "full"
    assert result["pilot_credited_once"] is False
    assert result["populations"]["full"]["remaining_logical_calls"] == 62944
    assert result["populations"]["fallback"]["remaining_logical_calls"] == 18480


def test_all_physical_retry_costs_are_included_and_high_cost_stops():
    events = list(pilot_events(10000, 1000))
    # The metadata logical request succeeded after one billed transport retry.
    events[0]["attempts"].append({"usage": {"prompt_tokens": 10000,
                                            "completion_tokens": 1000}})
    result = forecast_scope(events, pilot_summary(), ledger(10), pilot_reusable=True)
    assert result["recommended_population"] == "stop"
    assert result["pilot_stage_usage"]["metadata"]["physical_attempts"] == 569
    assert result["pilot_stage_usage"]["metadata"]["peak_estimate_usd"] == "2.389800"


@pytest.mark.parametrize("bad_ledger", [
    {"charged_or_reserved_microusd": -1, "unknown_attempts": 0},
    {"charged_or_reserved_microusd": False, "unknown_attempts": 0},
    {"charged_or_reserved_microusd": 0, "unknown_attempts": 0},
    {"charged_or_reserved_microusd": 1_000_000, "unknown_attempts": False},
])
def test_refuses_ledger_that_cannot_account_for_pilot_charges(bad_ledger):
    with pytest.raises(ValueError):
        forecast_scope(list(pilot_events()), pilot_summary(), bad_ledger,
                       pilot_reusable=True)
