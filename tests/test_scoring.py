import copy
import unittest
from pathlib import Path
from types import SimpleNamespace
from amem_repro.scoring import AuthorScorer, rescore_records, CORRECTED, HISTORICAL

ROOT = Path(__file__).resolve().parents[1]


def dependencies(bert_failure=False):
    def bert(*args, **kwargs):
        if bert_failure:
            raise RuntimeError("missing local model")
        return [SimpleNamespace(item=lambda: 0.8)] * 3

    return {
        "nltk": SimpleNamespace(word_tokenize=lambda s: s.split()),
        "sentence_bleu": lambda *a, **k: 0.4,
        "SmoothingFunction": lambda: SimpleNamespace(method1=None),
        "rouge_scorer": SimpleNamespace(
            RougeScorer=lambda *a, **k: SimpleNamespace(
                score=lambda *a: {
                    k: SimpleNamespace(fmeasure=0.5)
                    for k in ["rouge1", "rouge2", "rougeL"]
                }
            )
        ),
        "bert_score": bert,
        "meteor_score": lambda *a: 0.6,
        "sentence_model": SimpleNamespace(encode=lambda *a, **k: 1),
        "pytorch_cos_sim": lambda *a: SimpleNamespace(item=lambda: 0.7),
    }


class ScoringTests(unittest.TestCase):
    def test_dual_views_preserve_predictions_and_use_author_category5_references(self):
        records = [
            {
                "question_id": "conv-50:0",
                "prediction": "Not mentioned in the conversation",
                "qa": {
                    "question": "Who?",
                    "category": 5,
                    "answer": None,
                    "adversarial_answer": "Alice",
                    "evidence": [],
                },
            }
        ]
        before = copy.deepcopy(records)
        scorer = AuthorScorer(ROOT, dependencies=dependencies())
        views = rescore_records(records, scorer)
        self.assertEqual(records, before)
        self.assertEqual(
            views[CORRECTED]["individual_results"][0]["metrics"]["f1"], 1.0
        )
        self.assertEqual(
            views[HISTORICAL]["individual_results"][0]["metrics"]["f1"], 0.0
        )
        self.assertEqual(
            views[CORRECTED]["individual_results"][0]["metrics"]["adversarial_correct"],
            1,
        )
        self.assertEqual(
            views[HISTORICAL]["individual_results"][0]["prediction"],
            before[0]["prediction"],
        )

    def test_caught_metric_error_is_identified_without_changing_author_zero(self):
        events = []
        scorer = AuthorScorer(
            ROOT, dependencies=dependencies(True), observer=events.append
        )
        qa = scorer.qa(
            {"question": "What?", "category": 4, "answer": "apple pear", "evidence": []}
        )
        reference, metrics = scorer.score("apple", qa)
        self.assertEqual(reference, "apple pear")
        self.assertAlmostEqual(metrics["f1"], 2 / 3)
        self.assertEqual(metrics["bert_f1"], 0.0)
        self.assertTrue(
            any(
                e["kind"] == "metric_computation"
                and e["metric_function"] == "calculate_bert_scores"
                for e in events
            )
        )
        self.assertEqual(metrics["exact_match"], 0)

    def test_actual_zero_has_no_failure_event(self):
        events = []
        scorer = AuthorScorer(ROOT, dependencies=dependencies(), observer=events.append)
        _, metrics = scorer.score(
            "orange",
            scorer.qa(
                {"question": "What?", "category": 4, "answer": "pear", "evidence": []}
            ),
        )
        self.assertEqual(metrics["f1"], 0.0)
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()


class AssetFallbackTests(unittest.TestCase):
    def test_unavailable_sbert_keeps_author_zero_and_failure_notice(self):
        deps = dependencies()
        deps["sentence_model"] = None
        scorer = AuthorScorer(ROOT, dependencies=deps)
        _, metrics = scorer.score(
            "pear", scorer.qa({"question": "What?", "answer": "pear", "category": 4})
        )
        self.assertEqual(metrics["sbert_similarity"], 0.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(
            scorer.failures[0]["metric_function"], "calculate_sentence_similarity"
        )

    def test_offline_asset_environment_covers_scoring_and_is_restored(self):
        import os
        from unittest.mock import patch

        deps = dependencies()
        previous = deps["bert_score"]

        def bert(*args, **kwargs):
            self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
            self.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "1")
            return previous(*args, **kwargs)

        deps["bert_score"] = bert
        with patch.dict(
            os.environ, {"HF_HUB_OFFLINE": "prior", "TRANSFORMERS_OFFLINE": "prior"}
        ):
            scorer = AuthorScorer(ROOT, dependencies=deps)
            scorer.score(
                "pear",
                scorer.qa({"question": "What?", "answer": "pear", "category": 4}),
            )
            self.assertEqual(os.environ["HF_HUB_OFFLINE"], "prior")
            self.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "prior")


class FailedMetricIdentityTests(unittest.TestCase):
    def test_failure_notice_identifies_only_the_failed_bleu_variant(self):
        deps = dependencies()

        def bleu(*args, weights, **kwargs):
            if weights == (1, 0, 0, 0):
                raise RuntimeError("BLEU-1 fixture failure")
            return 0.0

        deps["sentence_bleu"] = bleu
        scorer = AuthorScorer(ROOT, dependencies=deps)
        _, metrics = scorer.score(
            "pear", scorer.qa({"question": "What?", "answer": "pear", "category": 4})
        )
        self.assertEqual(metrics["bleu1"], 0.0)
        self.assertEqual(metrics["bleu2"], 0.0)
        self.assertEqual([e["affected_metrics"] for e in scorer.failures], [["bleu1"]])


class OriginalScoringParityTests(unittest.TestCase):
    def test_instrumented_results_equal_uninstrumented_frozen_functions(self):
        import ast

        for failing in (False, True):
            scorer = AuthorScorer(ROOT, dependencies=dependencies(failing))
            plain = dict(scorer.namespace)
            nodes = [
                n
                for n in ast.parse((ROOT / "utils.py").read_bytes()).body
                if isinstance(n, ast.FunctionDef)
            ]
            exec(
                compile(
                    ast.Module(body=nodes, type_ignores=[]),
                    str(ROOT / "utils.py"),
                    "exec",
                ),
                plain,
            )
            for legacy in (False, True):
                actual = []
                expected = []
                categories = []
                for prediction, category, answer, trap in [
                    ("pear pear", 4, "pear apple", None),
                    ("", 1, "pear", None),
                    (None, 2, "date", None),
                    ("Not mentioned in the conversation", 5, None, "Alice"),
                    ("Alice", 5, None, "Alice"),
                ]:
                    qa = scorer.qa(
                        {
                            "question": "Which?",
                            "category": category,
                            "answer": answer,
                            "adversarial_answer": trap,
                        }
                    )
                    with self.subTest(
                        failing=failing, legacy=legacy, prediction=prediction
                    ):
                        result = scorer.score(prediction, qa, legacy)
                        original = plain["score_prediction"](prediction, qa, legacy)
                        self.assertEqual(result, original)
                        actual.append(result[1])
                        expected.append(original[1])
                        categories.append(category)
                self.assertEqual(
                    scorer.aggregate(actual, categories),
                    plain["aggregate_metrics"](expected, categories),
                )
