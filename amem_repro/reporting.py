"""Optional import of already-scored outputs; no task or grader is rerun."""

import copy
import csv
import hashlib
import json
from pathlib import Path

from .config import reject_credentials, fingerprint


def write_tables(views, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "scoring_views.json").write_text(
        json.dumps(views, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    fields = [
        "scoring_policy",
        "question_id",
        "category",
        "prediction",
        "reference",
        "metric",
        "value",
        "metric_failures",
    ]
    with (directory / "question_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for policy, view in views.items():
            for row in view["individual_results"]:
                for metric, value in row["metrics"].items():
                    writer.writerow(
                        dict(
                            scoring_policy=policy,
                            question_id=row["question_id"],
                            category=row["qa"]["category"],
                            prediction=row["prediction"],
                            reference=row["reference"],
                            metric=metric,
                            value=value,
                            metric_failures=json.dumps(row.get("metric_failures", [])),
                        )
                    )
    with (directory / "aggregate_metrics.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scoring_policy", "group", "metric", "statistic", "value"])
        for policy, view in views.items():
            for group, metrics in view["aggregate_metrics"].items():
                for metric, stats in metrics.items():
                    for statistic, value in stats.items():
                        writer.writerow([policy, group, metric, statistic, value])


def _study_identity(metadata):
    required = ("condition", "population", "manifest_sha256", "repetition", "run_id")
    if not isinstance(metadata, dict) or any(key not in metadata for key in required):
        raise ValueError(
            "Reporting requires condition, population, manifest_sha256, repetition and run_id"
        )
    identity = {key: metadata[key] for key in required}
    if identity["condition"] not in (
        "full",
        "neither",
        "linking_only",
        "evolution_only",
    ):
        raise ValueError("Unknown experimental condition")
    if identity["population"] not in ("full", "fallback", "smoke", "pilot"):
        raise ValueError("Unknown population")
    digest = identity["manifest_sha256"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(c not in "0123456789abcdef" for c in digest)
    ):
        raise ValueError("Population requires its full manifest fingerprint")
    if type(identity["repetition"]) is not int or identity["repetition"] < 0:
        raise ValueError("Repetition must be a nonnegative integer")
    if not isinstance(identity["run_id"], str) or not identity["run_id"].strip():
        raise ValueError("Original run_id is required")
    return identity


def export_experiments(
    views,
    *,
    client=None,
    export_authorized=False,
    evaluation_factory=None,
    metadata=None,
):
    """Export immutable saved results, explicitly marked as an import.

    Import timing is not original inference timing/cost. Those remain in the
    original run artifacts/metadata. The default makes no network requests.
    """
    if not export_authorized:
        raise PermissionError("Explicit reporting-export authorization required")
    reject_credentials(metadata or {})
    reject_credentials(views)
    identity = _study_identity(metadata)
    if client is None or evaluation_factory is None:
        from langfuse import Evaluation, get_client

        client = client or get_client()
        evaluation_factory = evaluation_factory or Evaluation
    saved = copy.deepcopy(views)
    artifact_hash = hashlib.sha256(
        json.dumps(saved, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    results = {}
    try:
        for policy, view in saved.items():
            if view["scoring_policy"] != policy:
                raise ValueError("Scoring policy identity mismatch")
            export_identity = {**identity, "scoring_policy": policy}
            by_id = {r["question_id"]: r for r in view["individual_results"]}
            if len(by_id) != len(view["individual_results"]) or not by_id:
                raise ValueError("Expected nonempty unique question IDs")

            def task(*, item, **kwargs):
                return by_id[item["metadata"]["question_id"]]["prediction"]

            # One evaluator per existing metric; no new grading logic.
            names = sorted({name for row in by_id.values() for name in row["metrics"]})
            evaluators = []
            for name in names:

                def metric(*, metadata, _name=name, **kwargs):
                    row = by_id[metadata["question_id"]]
                    if _name not in row["metrics"]:
                        return None  # e.g. adversarial_correct is category-5-only
                    return evaluation_factory(
                        name=_name,
                        value=row["metrics"][_name],
                        comment=json.dumps(
                            {
                                "scoring_policy": policy,
                                "metric_failures": row.get("metric_failures", []),
                            }
                        ),
                    )

                evaluators.append(metric)
            run_metadata = {
                **copy.deepcopy(metadata or {}),
                "scoring_policy": policy,
                "scorer_sha256": view["scorer_sha256"],
                "artifact_sha256": artifact_hash,
                "execution_mode": "imported_results",
                "experiment_identity": export_identity,
            }
            data = [
                {
                    "input": {
                        "question": r["qa"].get("question", ""),
                        "question_id": r["question_id"],
                    },
                    "expected_output": r["reference"],
                    "metadata": {
                        **run_metadata,
                        "question_id": r["question_id"],
                        "category": r["qa"]["category"],
                        "original_record": r,
                    },
                }
                for r in by_id.values()
            ]
            results[policy] = client.run_experiment(
                name=f"A-MEM/{identity['condition']}/{identity['population']}/{policy}",
                run_name=f"repetition-{identity['repetition']}/{fingerprint(export_identity)}",
                data=data,
                task=task,
                evaluators=evaluators,
                max_concurrency=1,
                metadata=run_metadata,
            )
    finally:
        client.flush()
    return results
