import unittest
from pathlib import Path
from amem_repro.manifests import build_manifest

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_full_keeps_original_identities_and_counts(self):
        manifest = build_manifest(ROOT / "data/locomo10.json", "full")
        self.assertEqual(
            manifest["totals"], {"conversations": 10, "turns": 5882, "questions": 1986}
        )
        self.assertEqual(manifest["conversations"][9]["original_id"], "conv-50")
        self.assertEqual(manifest["conversations"][9]["sample_index"], 9)
        self.assertEqual(
            manifest["conversations"][9]["questions"][0]["question_id"], "conv-50:qa:0"
        )

    def test_fallback_and_pilot_preserve_original_positions(self):
        fallback = build_manifest(ROOT / "data/locomo10.json", "fallback")
        self.assertEqual(
            [c["original_id"] for c in fallback["conversations"]],
            ["conv-49", "conv-50", "conv-44"],
        )
        self.assertEqual(
            [c["sample_index"] for c in fallback["conversations"]], [8, 9, 5]
        )
        self.assertEqual(
            fallback["totals"], {"conversations": 3, "turns": 1752, "questions": 558}
        )
        pilot = build_manifest(ROOT / "data/locomo10.json", "pilot")
        self.assertEqual(
            pilot["totals"], {"conversations": 1, "turns": 568, "questions": 204}
        )
        self.assertEqual(pilot["conversations"][0]["sample_index"], 9)

    def test_smoke_is_evidence_contained_and_indices_not_renumbered(self):
        smoke = build_manifest(ROOT / "data/locomo10.json", "smoke")
        self.assertEqual(
            smoke["totals"], {"conversations": 1, "turns": 18, "questions": 4}
        )
        conversation = smoke["conversations"][0]
        self.assertEqual(conversation["question_indices"], [0, 1, 2, 4])
        for question in conversation["questions"]:
            self.assertTrue(set(question["evidence"]) <= set(conversation["turn_ids"]))
        self.assertEqual(conversation["questions"][-1]["question_id"], "conv-26:qa:4")

    def test_changed_dataset_is_rejected(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.json"
            path.write_text("[]")
            with self.assertRaisesRegex(ValueError, "frozen"):
                build_manifest(path, "full")


if __name__ == "__main__":
    unittest.main()
