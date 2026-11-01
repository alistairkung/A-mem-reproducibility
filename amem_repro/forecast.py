"""Cost-only planning from the fixed full-mode pilot; never execute a phase.

Peak-rate token estimates and a declared sensitivity multiplier are planning
evidence, not provider invoices or an upper bound on unmeasured conditions.
"""

from decimal import Decimal, InvalidOperation
from .config import stage_output_limits


PILOT_COUNTS = {
    "metadata": 568, "shared_decision": 568,
    "query_keywords": 204, "answer": 204,
}
POPULATIONS = {
    "full": {"turns": 5882, "questions": 1986,
             "conversation_ids": ["conv-26", "conv-30", "conv-41", "conv-42",
                                  "conv-43", "conv-44", "conv-47", "conv-48",
                                  "conv-49", "conv-50"]},
    "fallback": {"turns": 1752, "questions": 558,
                 "conversation_ids": ["conv-49", "conv-50", "conv-44"]},
}
INPUT_RATE = Decimal("0.30")
OUTPUT_RATE = Decimal("1.20")
MILLION = Decimal(1_000_000)


def _usd(value):
    return format(value, ".6f")


def forecast_scope(pilot_events, pilot_summary, study_ledger_summary, *,
                   pilot_reusable, safety_multiplier=2):
    """Recommend full/fallback/stop using usage only, pending separate approval.

    The caller verifies provenance before passing pilot_reusable=True. A reusable
    pilot replaces precisely one full-mode conv-50 build/QA, never all four arms.
    """
    if type(pilot_reusable) is not bool or isinstance(safety_multiplier, bool):
        raise ValueError("Pilot reuse and sensitivity assumptions must be explicit")
    try:
        multiplier = Decimal(str(safety_multiplier))
    except InvalidOperation:
        raise ValueError("Invalid sensitivity multiplier") from None
    if not multiplier.is_finite() or multiplier < 1:
        raise ValueError("Sensitivity multiplier must be finite and >= 1")
    if (pilot_summary.get("status") not in ("complete", "degraded")
        or pilot_summary.get("population") != "pilot"
        or pilot_summary.get("conversation_ids") != ["conv-50"]
        or pilot_summary.get("expected_questions") != 204
        or pilot_summary.get("completed_questions") != 204):
        raise ValueError("A complete fixed conv-50 pilot is required")
    if type(study_ledger_summary.get("unknown_attempts")) is not int or study_ledger_summary["unknown_attempts"] != 0:
        raise ValueError("Unknown study charges block a scope decision")
    totals = {stage: {"logical_calls": 0, "physical_attempts": 0,
                      "input_tokens": 0, "output_tokens": 0,
                      "cost": Decimal(0)} for stage in PILOT_COUNTS}
    for event in pilot_events:
        if event.get("type", "generation") != "generation":
            continue
        if event.get("error_type") or event.get("stage") not in totals:
            raise ValueError("Failed or unknown pilot generation")
        stage = totals[event["stage"]]
        stage["logical_calls"] += 1
        attempts = event.get("attempts")
        if not isinstance(attempts, list) or not 1 <= len(attempts) <= 3:
            raise ValueError("Physical pilot attempts must be recorded")
        for attempt in attempts:
            usage = attempt.get("usage")
            if not isinstance(usage, dict):
                raise ValueError("Unknown attempt usage blocks a scope decision")
            inp, out = usage.get("prompt_tokens"), usage.get("completion_tokens")
            if (type(inp) is not int or type(out) is not int
                or not 0 <= inp <= 1048576 or not 0 <= out <= stage_output_limits()[event["stage"]]
                or ("total_tokens" in usage and (type(usage["total_tokens"]) is not int
                                                or usage["total_tokens"] != inp + out))):
                raise ValueError("Invalid physical attempt usage")
            stage["physical_attempts"] += 1
            stage["input_tokens"] += inp
            stage["output_tokens"] += out
            stage["cost"] += (inp * INPUT_RATE + out * OUTPUT_RATE) / MILLION
    if {stage: total["logical_calls"] for stage, total in totals.items()} != PILOT_COUNTS:
        raise ValueError("Pilot generation coverage differs from the fixed workload")
    charged = study_ledger_summary.get("charged_or_reserved_microusd")
    if type(charged) is not int or charged < 0:
        raise ValueError("Study ledger must supply a nonnegative integer charge")
    spent = Decimal(charged) / MILLION
    if spent < sum((total["cost"] for total in totals.values()), Decimal(0)):
        raise ValueError("Study ledger does not account for all pilot usage")
    populations = {}
    recommendation = "stop"
    for population, size in POPULATIONS.items():
        counts = {stage: 4 * size["turns" if stage in ("metadata", "shared_decision")
                                else "questions"] for stage in PILOT_COUNTS}
        if pilot_reusable:
            counts = {stage: count - PILOT_COUNTS[stage] for stage, count in counts.items()}
        remaining = sum((totals[stage]["cost"] / totals[stage]["logical_calls"] * count
                         for stage, count in counts.items()), Decimal(0))
        total = spent + remaining + 8
        sensitivity = spent + remaining * multiplier + 8
        populations[population] = {
            **size, "conditions": 4, "independent_builds_per_condition": 1,
            "remaining_stage_calls": counts, "remaining_logical_calls": sum(counts.values()),
            "remaining_estimate_usd": _usd(remaining),
            "point_total_usd": _usd(total), "sensitivity_total_usd": _usd(sensitivity),
            "fits_planning_ceiling": total <= 50,
            "fits_sensitivity_ceiling": sensitivity <= 50,
        }
        if recommendation == "stop" and total <= 50:
            recommendation = population
    stages = {
        stage: {**{key: value for key, value in total.items() if key != "cost"},
                "peak_estimate_usd": _usd(total["cost"]),
                "mean_cost_per_logical_call_usd": str(total["cost"] / total["logical_calls"])}
        for stage, total in totals.items()
    }
    return {
        "forecast_version": 1, "recommended_population": recommendation,
        "requires_main_execution_approval": True,
        "full_mode_is_upper_bound": False,
        "cost_basis": "usage-at-reviewed-peak-rates-not-invoice",
        "input_per_million_usd": str(INPUT_RATE), "output_per_million_usd": str(OUTPUT_RATE),
        "safety_multiplier": str(multiplier),
        "selection_basis": "incurred-plus-remaining-peak-estimate-plus-contingency",
        "sensitivity_diagnostic_only": True,
        "incurred_or_reserved_usd": _usd(spent), "contingency_usd": "8.000000",
        "ceiling_usd": "50.000000", "pilot_credited_once": pilot_reusable,
        "pilot_stage_usage": stages, "populations": populations,
        "limitations": [
            "The full-mode pilot does not bound other conditions or conversations.",
            "The sensitivity multiplier is a planning assumption, not a measured guarantee.",
            "Reconcile estimates against new arm-specific usage before further execution.",
        ],
    }
