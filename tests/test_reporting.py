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
            metadata={
                "run_id": "r1",
                "condition": "full",
                "population": "pilot",
                "manifest_sha256": "a" * 64,
                "repetition": 0,
            },
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


class ExperimentIdentityTests(unittest.TestCase):
    def test_each_study_dimension_changes_export_identity(self):
        identity = {
            "run_id": "r1",
            "condition": "full",
            "population": "pilot",
            "manifest_sha256": "a" * 64,
            "repetition": 0,
        }
        identities = [
            identity,
            {**identity, "condition": "linking_only"},
            {**identity, "population": "fallback"},
            {**identity, "manifest_sha256": "b" * 64},
            {**identity, "repetition": 1},
            {**identity, "run_id": "r2"},
        ]
        names = []
        for metadata in identities:
            client = FakeClient()
            export_experiments(
                ReportingTests().views(),
                client=client,
                export_authorized=True,
                evaluation_factory=lambda **k: k,
                metadata=metadata,
            )
            run = client.runs[0]
            names.append((run["name"], run["run_name"]))
            self.assertEqual(run["metadata"]["condition"], metadata["condition"])
            self.assertEqual(
                run["data"][0]["metadata"]["manifest_sha256"],
                metadata["manifest_sha256"],
            )
        self.assertEqual(len(names), len(set(names)))
        views = ReportingTests().views()
        from amem_repro.scoring import HISTORICAL

        views[HISTORICAL] = views.pop(CORRECTED)
        views[HISTORICAL]["scoring_policy"] = HISTORICAL
        client = FakeClient()
        export_experiments(
            views,
            client=client,
            export_authorized=True,
            evaluation_factory=lambda **k: k,
            metadata=identity,
        )
        self.assertNotIn((client.runs[0]["name"], client.runs[0]["run_name"]), names)

    def test_missing_or_invalid_identity_rejected_before_sdk_initialization(self):
        from unittest.mock import patch

        valid = {
            "run_id": "r1",
            "condition": "full",
            "population": "pilot",
            "manifest_sha256": "a" * 64,
            "repetition": 0,
        }
        for field in valid:
            metadata = {k: v for k, v in valid.items() if k != field}
            with (
                self.subTest(missing=field),
                patch(
                    "langfuse.get_client", side_effect=AssertionError("client created")
                ),
            ):
                with self.assertRaises(ValueError):
                    export_experiments(
                        ReportingTests().views(),
                        export_authorized=True,
                        metadata=metadata,
                    )
        for field, value in [
            ("repetition", True),
            ("manifest_sha256", "short"),
            ("condition", "arbitrary"),
        ]:
            with self.assertRaises(ValueError):
                export_experiments(
                    ReportingTests().views(),
                    export_authorized=True,
                    metadata={**valid, field: value},
                )
