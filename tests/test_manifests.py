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


class CompactManifestTests(unittest.TestCase):
    def test_compact_files_reconstruct_exact_original_expanded_manifests(self):
        import json
        from amem_repro.config import fingerprint
        from amem_repro.manifests import build_compact_manifest, expand_manifest

        original_hashes = {
            "full": "3571295e5e03dcb69b83e16f55cb3a8c5b0508e85cd59afaf95ef01de4abbf54",
            "fallback": "b9d41746ba8eac2b94d401570e9083b24ed1d3f2d20a9ece1de68600f33ad8a3",
            "pilot": "af6fac0af149d64cf6612caf3cb99dd515d8017c98487b19055833336c36529a",
            "smoke": "d4e5652bcc8e7f3c5054c1f6c4547906b130e36bb2e21b7cf50c40a85153ec99",
        }
        for scope, expected in original_hashes.items():
            compact = build_compact_manifest(ROOT / "data/locomo10.json", scope)
            expanded = expand_manifest(ROOT / "data/locomo10.json", compact)
            self.assertEqual(fingerprint(expanded), expected)
            self.assertEqual(
                compact, json.loads((ROOT / "manifests" / f"{scope}.json").read_text())
            )
            self.assertTrue(
                all(
                    "questions" not in c and "turn_ids" not in c
                    for c in compact["conversations"]
                )
            )

    def test_modified_compact_selection_or_configuration_is_rejected(self):
        import copy
        from amem_repro.manifests import build_compact_manifest, expand_manifest

        original = build_compact_manifest(ROOT / "data/locomo10.json", "fallback")
        for mutate in [
            lambda m: m["conversations"][0]["question_indices"].pop(),
            lambda m: m["selection"].update(seed=43),
            lambda m: m.update(dataset_sha256="0" * 64),
        ]:
            changed = copy.deepcopy(original)
            mutate(changed)
            with self.assertRaises(ValueError):
                expand_manifest(ROOT / "data/locomo10.json", changed)
