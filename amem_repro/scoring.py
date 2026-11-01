"""Run the frozen author's scoring functions without import-time downloads.

Only function definitions and QA are loaded from author source. An observational
hook in caught exception handlers records failed metrics while preserving their
original fallback values. All numerical scoring expressions remain author code.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from .config import source_fingerprint
from .author import _local_models_only

CORRECTED = "author-corrected-v1"
HISTORICAL = "author-legacy-c5-v1"


def _local_dependencies():
    # Importing this package never initializes models or contacts a provider.
    import nltk
    from rouge_score import rouge_scorer
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    from bert_score import score as bert_score
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import pytorch_cos_sim

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception as error:
        print(f"Warning: Could not load SentenceTransformer model: {error}")
        model = None
    return dict(
        nltk=nltk,
        rouge_scorer=rouge_scorer,
        sentence_bleu=sentence_bleu,
        SmoothingFunction=SmoothingFunction,
        meteor_score=meteor_score,
        bert_score=bert_score,
        sentence_model=model,
        pytorch_cos_sim=pytorch_cos_sim,
    )


class _FailureNotices(ast.NodeTransformer):
    def __init__(self, function):
        self.function = function

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)
        node.body.insert(
            0,
            ast.Expr(
                ast.Call(
                    func=ast.Name("_metric_failure", ast.Load()),
                    args=[ast.Constant(self.function)],
                    keywords=[
                        ast.keyword(
                            arg="metric",
                            value=ast.JoinedStr(
                                values=[
                                    ast.Constant("bleu"),
                                    ast.FormattedValue(
                                        value=ast.Name("n", ast.Load()), conversion=-1
                                    ),
                                ]
                            ),
                        )
                    ]
                    if self.function == "calculate_bleu_scores"
                    else [],
                )
            ),
        )
        return node


class AuthorScorer:
    def __init__(self, root, dependencies=None, observer=None):
        self.root = Path(root)
        source_fingerprint(self.root)
        self.observer = observer
        self.failures = []
        self._missing_sbert = False
        self.namespace = dict(
            __name__=__name__,
            dataclass=dataclass,
            Dict=Dict,
            List=List,
            Optional=Optional,
            Union=Union,
            statistics=statistics,
            defaultdict=defaultdict,
            _metric_failure=self._failure,
        )
        with _local_models_only():
            self.namespace.update(
                _local_dependencies() if dependencies is None else dependencies
            )
        self._missing_sbert = self.namespace.get("sentence_model") is None
        dataset = ast.parse((self.root / "load_dataset.py").read_text())
        nodes = [
            n for n in dataset.body if isinstance(n, ast.ClassDef) and n.name == "QA"
        ]
        self.namespace["NOT_MENTIONED"] = next(
            ast.literal_eval(n.value)
            for n in dataset.body
            if isinstance(n, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "NOT_MENTIONED" for t in n.targets
            )
        )
        exec(
            compile(
                ast.Module(body=nodes, type_ignores=[]),
                str(self.root / "load_dataset.py"),
                "exec",
            ),
            self.namespace,
        )
        source = (self.root / "utils.py").read_bytes()
        self.scorer_sha256 = hashlib.sha256(source).hexdigest()
        functions = [
            n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
        ]
        for node in functions:
            if node.name.startswith("calculate_"):
                _FailureNotices(node.name).visit(node)
        module = ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[]))
        exec(compile(module, str(self.root / "utils.py"), "exec"), self.namespace)

    def _failure(self, function, metric=None, exception_type=None):
        event = {
            "type": "failure",
            "level": "question",
            "kind": "metric_computation",
            "metric_function": function,
            "exception_type": exception_type or type(sys.exc_info()[1]).__name__,
            "affected_metrics": [metric]
            if metric
            else {
                "calculate_bert_scores": ["bert_precision", "bert_recall", "bert_f1"],
                "calculate_meteor_score": ["meteor"],
                "calculate_sentence_similarity": ["sbert_similarity"],
                "calculate_rouge_scores": ["rouge1_f", "rouge2_f", "rougeL_f"],
            }.get(function, []),
        }
        self.failures.append(event)
        if self.observer:
            try:
                self.observer(copy.deepcopy(event))
            except Exception as error:
                self.failures.append(
                    {
                        "type": "failure",
                        "level": "question",
                        "kind": "observation_failure",
                        "exception_type": type(error).__name__,
                    }
                )

    def qa(self, raw):
        return self.namespace["QA"](
            question=raw.get("question", ""),
            answer=raw.get("answer"),
            evidence=copy.deepcopy(raw.get("evidence", [])),
            category=raw["category"],
            adversarial_answer=raw.get("adversarial_answer"),
        )

    def score(self, prediction, qa, legacy_c5=False):
        self.failures = []
        if self._missing_sbert and prediction and qa.reference(legacy_c5):
            self._failure(
                "calculate_sentence_similarity", exception_type="AssetUnavailable"
            )
        with _local_models_only():
            return self.namespace["score_prediction"](prediction, qa, legacy_c5)

    def aggregate(self, metrics, categories):
        return self.namespace["aggregate_metrics"](metrics, categories)


def rescore_records(records, scorer):
    """Produce two views of saved outputs; never regenerate or mutate predictions."""
    saved = copy.deepcopy(records)
    ids = [r["question_id"] for r in saved]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate question IDs")
    views = {}
    for policy, legacy in [(CORRECTED, False), (HISTORICAL, True)]:
        rows = []
        for row in saved:
            qa = scorer.qa(row["qa"])
            reference, metrics = scorer.score(row["prediction"], qa, legacy_c5=legacy)
            rows.append(
                {
                    **copy.deepcopy(row),
                    "reference": reference,
                    "metrics": metrics,
                    "scoring_policy": policy,
                    "metric_failures": copy.deepcopy(scorer.failures),
                }
            )
        views[policy] = {
            "scoring_policy": policy,
            "scorer_sha256": scorer.scorer_sha256,
            "individual_results": rows,
            "aggregate_metrics": scorer.aggregate(
                [r["metrics"] for r in rows], [r["qa"]["category"] for r in rows]
            ),
        }
    return views
