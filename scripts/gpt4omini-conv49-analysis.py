"""Describe four independently accepted conv-49 builds using matched saved scores."""
import argparse
from hashlib import sha256
import json
from math import fsum, isclose
from pathlib import Path
import sys

CONDITIONS = ("full", "evolution_only", "neither", "linking_only")
METRICS = ("f1", "bleu1")
POLICIES = ("author-corrected-v1", "author-legacy-c5-v1")
CONTRASTS = {
    "linking_minus_neither": {"linking_only": 1, "neither": -1},
    "evolution_minus_neither": {"evolution_only": 1, "neither": -1},
    "full_minus_linking": {"full": 1, "linking_only": -1},
    "full_minus_evolution": {"full": 1, "evolution_only": -1},
    "interaction": {"full": 1, "linking_only": -1, "evolution_only": -1, "neither": 1},
}


def require(test, message):
    if not test:
        raise ValueError(message)


def load_accepted_scores(campaign):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from amem_repro.gpt4omini_campaign import verify_accepted_cell
    from scripts.gpt4omini_finance import verify_accepted_finances

    evidence = {}

    def read(path):
        raw = path.read_bytes()
        evidence[str(path.relative_to(campaign))] = sha256(raw).hexdigest()
        return json.loads(raw)

    cells = {}
    scores = {}
    for condition in CONDITIONS:
        key = "conv-49" if condition == "full" else condition + "-conv-49"
        verify_accepted_cell(campaign, key)
        verify_accepted_finances(campaign, key)
        reviews = [read(campaign / "outcomes" / key / f"acceptance-{axis}.json")
                   for axis in ("spec", "standards")]
        require(all(r["accepted"] is True and r["verdict"] == "pass" for r in reviews), f"Unaccepted cell: {key}")
        require(reviews[0]["phase"] == reviews[1]["phase"], f"Review phase mismatch: {key}")
        phase_name = reviews[0]["phase"]
        run = campaign / "cells" / key / "runs" / phase_name
        phase = read(run / "phase.json")
        require(phase["status"] in ("complete", "degraded") and
                (phase["notes"], phase["questions"]) == (509, 196), f"Incomplete phase: {key}")
        require(phase["binding"]["condition"] == condition and phase["binding"]["conversation_id"] == "conv-49",
                f"Unexpected condition or conversation: {key}")
        scores[condition] = read(run / "scoring-views.json")
        cells[condition] = {"key": key, "phase": phase_name, "status": phase["status"],
                            "classification": reviews[0]["classification"]}
        corrected, historical = (scores[condition][policy]["individual_results"] for policy in POLICIES)
        require(len(corrected) == len(historical) == 196 and
                all((a["question_id"], a["prediction"]) == (b["question_id"], b["prediction"])
                    for a, b in zip(corrected, historical)), f"Scoring views used different predictions: {key}")

    return cells, scores, evidence


def align_policy(scores, policy):
    reference = scores["full"][policy]["individual_results"]
    ids = [r["question_id"] for r in reference]
    require(ids == [f"conv-49:qa:{n}" for n in range(196)], f"Unexpected Full question IDs: {policy}")
    aligned = {}
    for condition in CONDITIONS:
        view = scores[condition][policy]
        rows = view["individual_results"]
        require([r["question_id"] for r in rows] == ids, f"Question ID/order mismatch: {condition}, {policy}")
        require(view["scorer_sha256"] == scores["full"][policy]["scorer_sha256"],
                f"Scorer mismatch: {condition}, {policy}")
        for actual, expected in zip(rows, reference):
            for field in ("category", "conversation_id", "qa", "reference",
                          "original_qa_index", "original_sample_index", "scoring_policy"):
                require(actual[field] == expected[field], f'{condition}: {field} differs for {actual["question_id"]}')
            require(not actual["metric_failures"], f'{condition}: metric failure for {actual["question_id"]}')
        aligned[condition] = rows
    return aligned


def score_questions(aligned):
    reference = aligned["full"]
    question_rows = []
    for i, ref in enumerate(reference):
        values = {c: {m: aligned[c][i]["metrics"][m] for m in METRICS}
                  for c in CONDITIONS}
        contrast = {name: {m: fsum(weight * values[c][m] for c, weight in weights.items()) * 100
                           for m in METRICS}
                    for name, weights in CONTRASTS.items()}
        question_rows.append({"question_id": ref["question_id"], "category": ref["category"],
                              "scores_fraction": values, "contrasts_pp": contrast})
        if ref["category"] == 5:
            question_rows[-1]["adversarial_correct"] = {
                c: aligned[c][i]["metrics"]["adversarial_correct"] for c in CONDITIONS}
    return question_rows


def summarise_policy(scores, policy):
    aligned = align_policy(scores, policy)
    reference = aligned["full"]
    question_rows = score_questions(aligned)
    groups = {}
    for group, category in [("overall", None), *[(f"category_{n}", n) for n in range(1, 6)]]:
        selected = [i for i, row in enumerate(reference) if category is None or row["category"] == category]
        means = {c: {m: fsum(aligned[c][i]["metrics"][m] for i in selected) / len(selected) * 100
                     for m in METRICS} for c in CONDITIONS}
        for c in CONDITIONS:
            for m in METRICS:
                require(isclose(means[c][m] / 100, scores[c][policy]["aggregate_metrics"][group][m]["mean"],
                                rel_tol=0, abs_tol=1e-12), f"Frozen mean mismatch: {c}, {group}, {m}")
        groups[group] = {"questions": len(selected), "means_percent": means,
                         "contrasts_pp": {name: {m: fsum(question_rows[i]["contrasts_pp"][name][m]
                                                           for i in selected) / len(selected)
                                                   for m in METRICS} for name in CONTRASTS}}
    adversarial = {c: {"correct": sum(r["metrics"]["adversarial_correct"] for r in aligned[c] if r["category"] == 5),
                       "total": groups["category_5"]["questions"]} for c in CONDITIONS}
    return {"groups": groups, "adversarial_correct": adversarial,
                                        "matched_questions": question_rows}


def analyse(campaign):
    cells, scores, evidence = load_accepted_scores(campaign)
    return {"cells": cells, "scoring_views": {p: summarise_policy(scores, p) for p in POLICIES},
            "evidence_sha256": evidence,
            "aggregation": "Equal weight per matched original question; percentage points",
            "interpretation": "Descriptive single-build contrasts; no established causal confidence"}


def public_scores(analysis):
    """Yield only original identifiers, categories, and numeric scores for publication."""
    views = analysis["scoring_views"]
    corrected, historical = (views[p]["matched_questions"] for p in POLICIES)
    for first, second in zip(corrected, historical, strict=True):
        require(first["question_id"] == second["question_id"] and first["category"] == second["category"],
                "Question alignment differs between policies")
        row = {"question_id": first["question_id"], "category": first["category"],
               "corrected": first["scores_fraction"], "historical": second["scores_fraction"]}
        if first["category"] == 5:
            require(first["adversarial_correct"] == second["adversarial_correct"], "Binary correctness differs by view")
            row["adversarial_correct"] = first["adversarial_correct"]
        yield row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--public-scores", type=Path, help="Write one numeric-only JSON record per original question")
    args = parser.parse_args()
    result = analyse(args.campaign.resolve())
    with args.output.open("x") as target:
        json.dump(result, target, sort_keys=True, indent=2)
        target.write("\n")
    if args.public_scores is not None:
        with args.public_scores.open("x") as target:
            for row in public_scores(result):
                target.write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")
    print(json.dumps({p: v["groups"]["overall"] for p, v in result["scoring_views"].items()}, sort_keys=True))
