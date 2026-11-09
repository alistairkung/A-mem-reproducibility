"""Read-only verification of the five worked examples at the accepted Git revision."""

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Dict, List, Optional

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[1]
COMMIT = "8485673183d7b8018c841082d075b21158002700"
REPORTS = "docs/reproducibility/"
HIST = "author-legacy-c5-v1"
COMP = "author-corrected-v1"
POLICIES = {HIST: "historical", COMP: "corrected"}
MODES = ("neither", "linking_only", "evolution_only", "full")


def equal(actual, expected, label):
    if actual != expected:
        raise ValueError(f"Mismatch in {label}")


def pinned(path):
    return subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=ROOT)


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def author_functions():
    # Load the same definitions as amem_repro/scoring.py, without module-level
    # downloads. Only unrelated metric calls are stubbed at the call boundary.
    ns = dict(
        nltk=nltk,
        sentence_bleu=sentence_bleu,
        SmoothingFunction=SmoothingFunction,
        Dict=Dict,
        List=List,
        Optional=Optional,
        dataclass=dataclass,
    )
    for name in ("calculate_rouge_scores", "calculate_bert_scores"):
        ns[name] = lambda *args: {}
    for name in ("calculate_meteor_score", "calculate_sentence_similarity"):
        ns[name] = lambda *args: 0.0
    dataset = ast.parse(pinned("load_dataset.py"))
    qa_nodes = [
        n for n in dataset.body if isinstance(n, ast.ClassDef) and n.name == "QA"
    ]
    for n in dataset.body:
        if isinstance(n, ast.Assign) and any(
            getattr(t, "id", "") == "NOT_MENTIONED" for t in n.targets
        ):
            ns["NOT_MENTIONED"] = ast.literal_eval(n.value)
    names = {
        "score_prediction",
        "calculate_metrics",
        "simple_tokenize",
        "is_not_mentioned",
        "calculate_bleu_scores",
    }
    nodes = [
        n
        for n in ast.parse(pinned("utils.py")).body
        if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    exec(
        compile(
            ast.Module(qa_nodes + nodes, type_ignores=[]),
            "accepted Git definitions",
            "exec",
        ),
        ns,
    )
    return ns


def arithmetic(prediction, reference):
    """Independent set and count arithmetic for the nonempty strings in the audit."""

    def tokens(text):
        return (
            text.strip()
            .lower()
            .translate(str.maketrans({p: " " for p in ".,!?"}))
            .split()
        )

    p, r = tokens(prediction), tokens(reference)
    ps, rs = set(p), set(r)
    shared = ps & rs
    precision, recall = len(shared) / len(ps), len(shared) / len(rs)
    f1 = 2 * precision * recall / (precision + recall) if shared else 0.0
    pt = nltk.word_tokenize(prediction.strip().lower())
    rt = nltk.word_tokenize(reference.strip().lower())
    clipped = Counter(pt) & Counter(rt)
    unigram = sum(clipped.values()) / len(pt)
    penalty = math.exp(min(0.0, 1 - len(rt) / len(pt)))
    # NLTK returns early for zero unigram matches. Otherwise it evaluates the
    # weighted log sum, even with (1,0,0,0). Preserve that rounding order.
    bleu = penalty * math.exp(math.log(unigram)) if clipped else 0.0
    return {
        "f1": dict(
            prediction_tokens=p,
            reference_tokens=r,
            prediction_set=sorted(ps),
            reference_set=sorted(rs),
            intersection=sorted(shared),
            precision=precision,
            recall=recall,
            value=f1,
        ),
        "bleu1": dict(
            prediction_tokens=pt,
            reference_tokens=rt,
            clipped_counts=dict(clipped),
            matches=sum(clipped.values()),
            precision=unigram,
            prediction_length=len(pt),
            reference_length=len(rt),
            brevity_penalty=penalty,
            value=bleu,
        ),
    }


def candidate_classes(historical, complementary):
    """Overlapping explanatory pools, counted before selection."""
    prediction = complementary["prediction"]
    distractor, abstention = historical["reference"], complementary["reference"]
    historical_metrics = historical["metrics"]
    complementary_metrics = complementary["metrics"]
    both_metrics = (historical_metrics, complementary_metrics)
    binary = complementary_metrics["adversarial_correct"]
    if prediction == abstention and binary and historical_metrics["f1"] <= 0.25:
        yield "A"
    if prediction == distractor and not binary and complementary_metrics["f1"] <= 0.25:
        yield "B"
    if prediction not in (distractor, abstention):
        if all(0 < m["f1"] < 1 for m in both_metrics):
            yield "C"
        if any(abs(m["f1"] - m["bleu1"]) >= 0.05 for m in both_metrics):
            yield "E"
    if binary and prediction != abstention:
        yield "D_punctuation" if prediction == abstention + "." else "D"


def response_form(prediction, distractor, abstention):
    """Exhaustive inventory of the raw responses observed in this population."""
    if prediction == abstention:
        return "canonical"
    if prediction == distractor:
        return "distractor"
    if prediction == f"{abstention} or {distractor}":
        return "both_options"
    if prediction == abstention + ".":
        return "abstention_final_period"
    if prediction == distractor + "." or distractor == f"'{prediction}'":
        return "distractor_punctuation"
    return "other"


def score_examples(examples, samples, report, ns):
    equal([r["label"] for r in examples], list("ABCDE"), "example labels")
    equal(len({r["question_id"] for r in examples}), 5, "distinct questions")
    for x in examples:
        sample = samples[x["conversation_id"]]
        qa = sample["qa"][x["original_qa_index"]]
        key = x["question_id"]
        equal(key, f"{sample['sample_id']}:qa:{x['original_qa_index']}", "original ID")
        equal(
            (qa["category"], x["category"], qa["question"]), (5, 5, x["question"]), key
        )
        quote = x["evidence"]
        (turn,) = [
            t
            for turns in sample["conversation"].values()
            if isinstance(turns, list)
            for t in turns
            if t["dia_id"] == quote["turn_id"]
        ]
        equal([quote["turn_id"]], qa["evidence"], key + " turn")
        equal(quote["speaker"], turn["speaker"], key + " speaker")
        equal(
            bool(quote["excerpt"]) and quote["excerpt"] in turn["text"],
            True,
            key + " excerpt",
        )
        for policy, report_key in POLICIES.items():
            view = x["views"][policy]
            ref, scores = ns["score_prediction"](
                x["prediction"],
                ns["QA"](
                    answer=qa.get("answer"),
                    question=qa["question"],
                    evidence=qa["evidence"],
                    category=5,
                    adversarial_answer=qa["adversarial_answer"],
                ),
                policy == HIST,
            )
            equal(ref, view["reference"], key + " reference")
            equal(scores["adversarial_correct"], x["binary"], key + " binary")
            steps = arithmetic(x["prediction"], ref)
            equal(steps, view["arithmetic"], key + " token derivation")
            for metric in ("f1", "bleu1"):
                published = report[key][report_key][x["configuration"]][metric]
                for number in (scores[metric], steps[metric]["value"], view[metric]):
                    equal(number, published, key + " " + policy + " " + metric)


def verify_readback_extract(x, receipt):
    """Compare the retained projection of the live GETs. This makes no HTTP requests."""
    key = x["question_id"]
    equal(
        (receipt["question_id"], receipt["run_id"]),
        (key, x["run_id"]),
        "readback subject",
    )
    trace = receipt["question_trace"]
    equal(
        (
            trace["trace_id"],
            trace["observation_id"],
            trace["prediction"],
            trace["input_reference"],
        ),
        (
            x["trace_id"],
            x["question_observation_id"],
            x["prediction"],
            x["views"][HIST]["reference"],
        ),
        key,
    )
    for policy, v in x["views"].items():
        item = receipt["experiment_items"][policy]
        equal(
            (
                item["experiment_item_id"],
                item["observation_id"],
                item["original_trace_id"],
            ),
            (v["experiment_item_id"], v["observation_id"], trace["trace_id"]),
            key + " item association",
        )
        scores = {
            "f1": v["f1"],
            "bleu1": v["bleu1"],
            "adversarial_correct": x["binary"],
        }
        equal(
            (
                item["prediction"],
                item["reference"],
                item["scoring_policy"],
                item["scores"],
            ),
            (x["prediction"], v["reference"], policy, scores),
            key + " readback fields",
        )
        if policy == COMP:
            equal(
                (trace["output_policy"], trace["output_reference"], trace["scores"]),
                (policy, v["reference"], scores),
                key + " trace output",
            )


def population(report, analysis):
    equal(len(report), 558, "matched population")
    counts = Counter(r["category"] for r in report.values())
    equal(counts, {1: 99, 2: 89, 3: 27, 4: 222, 5: 121}, "category counts")
    overall = {}
    for row in report.values():
        for name in POLICIES.values():
            equal(set(row[name]), set(MODES), "four-cell coverage")
        if row["category"] != 5:
            equal(row["historical"], row["corrected"], row["question_id"])
    for name in POLICIES.values():
        overall[name] = {}
        for mode in MODES:
            values = [r[name][mode]["f1"] for r in report.values()]
            percent = 100 * math.fsum(values) / len(values)
            recorded = analysis["pooled"][name]["groups"]["overall"]["means_percent"][
                mode
            ]["f1"]
            equal(percent, recorded, f"{name} {mode} pooled F1")
            overall[name][mode] = percent
    return overall


def verify_archive(archive, manifest, examples, report, samples, analysis, ns):
    pools = {k: [] for k in ("A", "B", "C", "D", "D_punctuation", "E")}
    selected = {(r["configuration"], r["question_id"]): r for r in examples}
    coverage = set()
    forms = Counter()
    scorer_hash = digest(pinned("utils.py"))
    for cell in manifest["cells"]:
        directory = archive / cell["directory"]
        phase = read(directory / "phase.json")
        mode = phase["binding"]["condition"]
        conv = phase["binding"]["conversation_id"]
        tag = conv if mode == "full" else f"{mode}-{conv}"
        imported = read(directory / "langfuse-imported.json")
        equal(
            {p: v["url"] for p, v in imported["experiments"].items()},
            analysis["experiments"][tag],
            tag,
        )
        data = (directory / "scoring-views.json").read_bytes()
        equal(digest(data), cell["scoring_views_sha256"], tag + " saved file")
        equal(digest(data), phase["files"]["scoring-views.json"], tag + " phase seal")
        views = json.loads(data)
        events = {}
        event_path = directory / "events.jsonl"
        with event_path.open() as stream:
            for line in stream:
                event = json.loads(line)
                if event["type"] == "question_result":
                    key = event["question_id"]
                    equal(key in events, False, key + " duplicate event")
                    events[key] = event["result"]
        expected = [f"{conv}:qa:{i}" for i in range(len(samples[conv]["qa"]))]
        equal(list(events), expected, tag + " saved answers")
        for policy in POLICIES:
            view = views[policy]
            equal(view["scorer_sha256"], scorer_hash, tag + " frozen scorer")
            equal([r["question_id"] for r in view["individual_results"]], expected, tag)
        for i, key in enumerate(expected):
            h, c = (views[p]["individual_results"][i] for p in POLICIES)
            original = samples[conv]["qa"][i]
            equal(
                original["category"],
                report[key]["category"],
                key + " published category",
            )
            saved = events[key]
            for row, policy in ((h, HIST), (c, COMP)):
                equal(
                    (
                        row["qa"],
                        row["original_qa_index"],
                        row["prediction"],
                        row["scoring_policy"],
                    ),
                    (original, i, saved["prediction"], policy),
                    key + " saved QA",
                )
                metrics = {m: row["metrics"][m] for m in ("f1", "bleu1")}
                equal(
                    metrics, report[key][POLICIES[policy]][mode], key + " public scores"
                )
            pair = (mode, key)
            equal(pair in coverage, False, key + " duplicate cell")
            coverage.add(pair)
            if original["category"] != 5:
                equal(h["metrics"], c["metrics"], key + " Category 1–4 metrics")
                equal(h["reference"], c["reference"], key + " Category 1–4 reference")
                continue
            pred = c["prediction"]
            equal(
                (h["reference"], c["reference"]),
                (original["adversarial_answer"], ns["NOT_MENTIONED"]),
                key,
            )
            forms[response_form(pred, h["reference"], c["reference"])] += 1
            classes = list(candidate_classes(h, c))
            for group in classes:
                pools[group].append(key)
            if pair in selected:
                x = selected[pair]
                equal(
                    (
                        directory.name,
                        cell["directory"],
                        pred,
                        json.loads(saved["raw_response"])["answer"],
                    ),
                    (x["run_id"], x["directory"], x["prediction"], pred),
                    key + " original prediction",
                )
                equal(
                    "D_punctuation" if x["label"] == "D" else x["label"],
                    manifest["selected"][x["label"]]["pool"],
                    key,
                )
                equal(
                    manifest["selected"][x["label"]]["pool"] in classes,
                    True,
                    key + " selection",
                )
                for row in (h, c):
                    equal(row["metrics"]["adversarial_correct"], x["binary"], key)
    equal(dict(forms), manifest["response_inventory"], "raw response inventory")
    equal(coverage, {(m, q) for q in report for m in MODES}, "accepted pairs")
    return {
        k: {"predictions": len(v), "questions": len(set(v))} for k, v in pools.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=ROOT,
        help="repository root containing artifacts/",
    )
    parser.add_argument(
        "--without-archive",
        action="store_true",
        help="check extracts and pinned Git records only",
    )
    args = parser.parse_args()
    equal(nltk.__version__, "3.10.4", "NLTK version")
    nltk.data.path.insert(0, str(args.archive_root / "artifacts/assets/nltk_data"))
    examples = read(AUDIT / "examples.json")
    manifest = read(AUDIT / "selection_manifest.json")
    results = read(AUDIT / "verification_results.json")
    equal(manifest["accepted_commit"], COMMIT, "revision")
    equal(
        manifest["scoring_policies"],
        {"historical": HIST, "complementary": COMP},
        "manifest policies",
    )
    samples = {s["sample_id"]: s for s in json.loads(pinned("data/locomo10.json"))}
    rows = [
        json.loads(line)
        for line in pinned(
            REPORTS + "gpt4omini-558q-four-condition-scores.jsonl"
        ).splitlines()
    ]
    equal(len(rows), 558, "published row count")
    report = {r["question_id"]: r for r in rows}
    analysis = json.loads(pinned(REPORTS + "gpt4omini-twelve-cell-analysis.json"))
    ns = author_functions()
    score_examples(examples, samples, report, ns)
    equal(
        population(report, analysis),
        results["pooled_f1_percent"],
        "published aggregates",
    )
    equal([r["label"] for r in results["examples"]], list("ABCDE"), "receipt coverage")
    for x, receipt in zip(examples, results["examples"]):
        verify_readback_extract(x, receipt["langfuse_readback"])
        choice = manifest["selected"][x["label"]]
        equal(
            (choice["question_id"], choice["configuration"]),
            (x["question_id"], x["configuration"]),
            "selected ID",
        )
    if not args.without_archive:
        counts = verify_archive(
            args.archive_root, manifest, examples, report, samples, analysis, ns
        )
        equal(counts, manifest["candidates"], "selection census")
        print(
            "PASS 12 accepted cells, 2,232 matched predictions, all saved metrics in Categories 1–4, selection census"
        )
    print(
        "PASS five original questions, ten author scores per metric, ten arithmetic derivations, eight pooled F1 means"
    )
    print(
        "Offline run. Live Langfuse readback is documented separately in verification_results.json."
    )


if __name__ == "__main__":
    main()
