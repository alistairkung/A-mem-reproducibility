import copy
import unittest
from amem_repro.reporting import export_experiments, write_tables
from amem_repro.scoring import CORRECTED
from tempfile import TemporaryDirectory
from pathlib import Path


class FakeClient:
    def __init__(self):
        self.runs = []
        self.flushed = False

    def run_experiment(self, **kwargs):
        self.runs.append(kwargs)
        row = kwargs["data"][0]
        assert kwargs["task"](item=row) == "saved answer"
        assert kwargs["evaluators"][0](metadata=row["metadata"])["value"] == 0.5
        return "saved-url"

    def flush(self):
        self.flushed = True


class ReportingTests(unittest.TestCase):
    def views(self):
        return {
            CORRECTED: {
                "scoring_policy": CORRECTED,
                "scorer_sha256": "abc",
                "aggregate_metrics": {},
                "individual_results": [
                    {
                        "question_id": "conv-50:qa:0",
                        "prediction": "saved answer",
                        "reference": "gold",
                        "qa": {"category": 1, "question": "Which?"},
                        "metrics": {"f1": 0.5},
                        "metric_failures": [],
                    }
                ],
            }
        }

    def test_optional_export_uses_saved_outputs_and_scores_only(self):
        client = FakeClient()
        views = self.views()
        before = copy.deepcopy(views)
        with self.assertRaises(PermissionError):
            export_experiments(views, client=client)
        self.assertEqual(client.runs, [])
        result = export_experiments(
            views,
            client=client,
            export_authorized=True,
            evaluation_factory=lambda **k: k,
            metadata={"run_id": "r1"},
        )
        self.assertEqual(result[CORRECTED], "saved-url")
        self.assertEqual(
            client.runs[0]["metadata"]["execution_mode"], "imported_results"
        )
        self.assertEqual(client.runs[0]["max_concurrency"], 1)
        self.assertEqual(views, before)
        self.assertTrue(client.flushed)

    def test_csv_has_policy_and_stable_ids(self):
        with TemporaryDirectory() as d:
            write_tables(self.views(), d)
            text = (Path(d) / "question_metrics.csv").read_text()
            self.assertIn("scoring_policy", text)
            self.assertIn("conv-50:qa:0", text)
            self.assertIn(CORRECTED, text)


class ExportSafetyTests(unittest.TestCase):
    def test_credentials_are_rejected_before_any_export(self):
        client = FakeClient()
        with self.assertRaises(ValueError):
            export_experiments(
                {},
                client=client,
                export_authorized=True,
                evaluation_factory=lambda **k: k,
                metadata={"api_key": "fixture"},
            )
        self.assertEqual(client.runs, [])
