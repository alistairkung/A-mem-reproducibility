import copy
import hashlib
import subprocess
import unittest
import pytest
from amem_repro.config import (
    AUTHOR_REVISION,
    UPSTREAM_README,
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


def test_author_file_inventory_and_readme_layouts(tmp_path):
    # A real Git tree exercises the same path-based lookups as the release guard.
    subprocess.run(["git", "clone", "--quiet", "--shared", str(ROOT), str(tmp_path)], check=True)
    original = subprocess.check_output(["git", "show", f"{AUTHOR_REVISION}:README.md"], cwd=tmp_path)
    readme_sha = hashlib.sha256(original).hexdigest()
    files = source_fingerprint(tmp_path)["files"]
    assert files[UPSTREAM_README] == readme_sha and "README.md" not in files
    for name, digest in files.items():
        assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest
    (tmp_path / "README.md").write_text("Coursework guide\n")
    assert source_fingerprint(tmp_path)["files"] == files
    frozen = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", AUTHOR_REVISION],
                                     cwd=tmp_path, text=True).splitlines()
    for name in frozen:
        if name.endswith((".py", ".sh")) or name in ("README.md", "LICENSE", "requirements.txt"):
            item = tmp_path / (UPSTREAM_README if name == "README.md" else name)
            saved = item.read_bytes()
            item.write_bytes(saved + b"altered")
            with pytest.raises(ValueError, match="Frozen author source changed"):
                source_fingerprint(tmp_path)
            item.write_bytes(saved)

    (tmp_path / "README.md").write_bytes(original)
    archive = tmp_path / UPSTREAM_README
    archive.unlink()
    with pytest.raises(ValueError, match=UPSTREAM_README):
        source_fingerprint(tmp_path)
    archive.symlink_to("README.md")
    with pytest.raises(ValueError, match=UPSTREAM_README):
        source_fingerprint(tmp_path)
    archive.unlink()
    subprocess.run(["git", "restore", "--", "README.md", UPSTREAM_README], cwd=tmp_path, check=True)
    for ref in (
        "8485673183d7b8018c841082d075b21158002700",  # accepted analysis
        "34f4ab5e96e9854c9b63492c473155ab4b65279a",  # PR #52 merge
        "e736a007e243442ef65b156f184bb70b78c578a2",  # merged coursework report
    ):
        subprocess.run(["git", "checkout", "--quiet", "--detach", ref], cwd=tmp_path, check=True)
        old = source_fingerprint(tmp_path)["files"]
        assert old["README.md"] == readme_sha and UPSTREAM_README not in old


if __name__ == "__main__":
    unittest.main()
