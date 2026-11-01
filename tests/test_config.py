import copy
import unittest
from amem_repro.config import (
    load_config,
    validate_config,
    fingerprint,
    source_fingerprint,
)
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def test_frozen_defaults_and_secret_safe_fingerprint(self):
        config = load_config(ROOT / "config/study.json")
        self.assertEqual(config["model"]["id"], "deepseek-flash")
        self.assertEqual(config["model"]["base_url"], "https://api.deepseek.com/beta")
        self.assertEqual(config["generation"]["temperature_c5"], 0.5)
        self.assertEqual(config["retrieval"]["answer_k"], 10)
        self.assertEqual(fingerprint({"b": 2, "a": 1}), fingerprint({"a": 1, "b": 2}))
        with self.assertRaisesRegex(ValueError, "credential"):
            fingerprint({"api_key": "do-not-persist"})
        config["retrieval"]["answer_k"] = 40
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_bool_is_not_a_numeric_configuration_value(self):
        config = load_config(ROOT / "config/study.json")
        config["build_repetitions"] = True
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_original_source_is_verified_without_imports(self):
        provenance = source_fingerprint(ROOT)
        self.assertEqual(
            provenance["author_revision"], "f9a173dec325d84fcc97e7828775c7b241c33466"
        )
        self.assertIn("memory_layer.py", provenance["files"])
        self.assertEqual(len(provenance["files"]["utils.py"]), 64)


if __name__ == "__main__":
    unittest.main()
