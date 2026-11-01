"""Offline asset verification through the public preflight boundary."""
import hashlib
import json
from pathlib import Path
import zipfile

import pytest


def fixture_assets(tmp_path):
    root = tmp_path / "assets"
    snapshot = root / "huggingface/hub/models--example--encoder/snapshots/frozen"
    snapshot.mkdir(parents=True)
    payload = b"verified model bytes"
    (snapshot / "model.safetensors").write_bytes(payload)
    archive = root / "nltk_archives/words.zip"
    archive.parent.mkdir()
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("words/en.txt", "offline words\n")
    config = {
        "asset_manifest_version": 2,
        "assets": [{"id": "encoder", "repository": "example/encoder", "revision": "frozen",
                    "files": [{"path": "model.safetensors", "sha256": hashlib.sha256(payload).hexdigest()}],
                    "cache_aliases": ["encoder"]}],
        "nltk": {"revision": "frozen-nltk", "archives": [{"id": "words", "directory": "corpora", "filename": "words.zip",
                       "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}]},
        "tokenizer": {"asset_id": "encoder", "hosted_parity": "unverified"},
    }
    path = tmp_path / "assets.json"
    path.write_text(json.dumps(config))
    return root, path


def test_verified_offline_assets_are_reusable_and_tampering_is_rejected(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout, verify_asset_report

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    report = build_asset_report(config, root, required_packages={})
    assert report["ready"] is True
    assert report["tokenizer_hosted_parity"] == "unverified"
    verify_asset_report(report, root, config, required_packages={})
    (root / "nltk_data/corpora/words/en.txt").write_text("changed data")
    with pytest.raises(ValueError, match="Asset preflight"):
        verify_asset_report(report, root, config, required_packages={})


def test_missing_or_wrong_dependency_versions_block_execution(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    report = build_asset_report(config, root, required_packages={"amem-nonexistent-runtime": "1.0", "pytest": "0.0"})
    assert report["ready"] is False
    assert "Missing dependency: amem-nonexistent-runtime" in report["blockers"]
    assert any("Dependency pytest: expected 0.0" in issue for issue in report["blockers"])


def test_old_asset_manifest_and_unverified_bytes_are_rejected(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    (root / "huggingface/hub/models--example--encoder/snapshots/frozen/model.safetensors").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        prepare_asset_layout(root, config)
    data = json.loads(config.read_text())
    data["asset_manifest_version"] = 1
    config.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="manifest version"):
        build_asset_report(config, root, required_packages={})


def test_preflight_does_not_follow_assets_outside_root_or_repoint_refs(tmp_path):
    from amem_repro.preflight import prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    model = root / "huggingface/hub/models--example--encoder/snapshots/frozen/model.safetensors"
    external = tmp_path / "external"
    external.write_bytes(model.read_bytes())
    model.unlink()
    model.symlink_to(external)
    with pytest.raises(ValueError, match="escapes"):
        prepare_asset_layout(root, config)
    model.unlink()
    model.write_bytes(external.read_bytes())
    refs = model.parent.parent.parent / "refs"
    refs.mkdir()
    (refs / "main").write_text("another-revision")
    with pytest.raises(ValueError, match="ref differs"):
        prepare_asset_layout(root, config)


def test_standard_huggingface_blob_symlinks_are_verified(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    model = root / "huggingface/hub/models--example--encoder/snapshots/frozen/model.safetensors"
    blob = model.parent.parent.parent / "blobs/pinned"
    blob.parent.mkdir()
    blob.write_bytes(model.read_bytes())
    model.unlink()
    model.symlink_to(blob)
    prepare_asset_layout(root, config)
    assert build_asset_report(config, root, required_packages={})["ready"]


def test_local_tokenizer_count_is_reproducible_without_claiming_hosted_parity(tmp_path):
    tokenizers = pytest.importorskip("tokenizers")
    from amem_repro.preflight import build_asset_report, make_token_counter, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    path = root / "huggingface/hub/models--example--encoder/snapshots/frozen/tokenizer.json"
    tokenizer = tokenizers.Tokenizer(tokenizers.models.WordLevel({"[UNK]": 0, "hello": 1, "world": 2}, unk_token="[UNK]"))
    tokenizer.pre_tokenizer = tokenizers.pre_tokenizers.Whitespace()
    tokenizer.save(str(path))
    data = json.loads(config.read_text())
    data["assets"][0]["files"].append({"path": "tokenizer.json", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    config.write_text(json.dumps(data))
    prepare_asset_layout(root, config)
    report = build_asset_report(config, root, required_packages={})
    counter = make_token_counter(root, report, config, required_packages={})
    assert counter.count("hello world") == 2
    assert counter.exact is False
    assert counter.revision == "frozen"
    assert "hosted parity unverified" in counter.method
    path.write_text("tampered tokenizer")
    with pytest.raises(ValueError, match="Asset preflight"):
        make_token_counter(root, report, config, required_packages={})


def test_saved_receipt_cannot_remove_locked_dependency_requirements(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout, verify_asset_report

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    report = build_asset_report(config, root, required_packages={})
    with pytest.raises(ValueError, match="Asset preflight"):
        verify_asset_report(report, root, config)


def test_small_huggingface_files_match_frozen_git_blob_ids(tmp_path):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    model = root / "huggingface/hub/models--example--encoder/snapshots/frozen/model.safetensors"
    # Git's published example object for the literal "test content\n".
    model.write_bytes(b"test content\n")
    data = json.loads(config.read_text())
    data["assets"][0]["files"] = [{"path": "model.safetensors", "git_blob": "d670460b4b4aece5915caf5c68d12f560a9fe3e4"}]
    config.write_text(json.dumps(data))
    prepare_asset_layout(root, config)
    assert build_asset_report(config, root, required_packages={})["ready"]
    model.write_bytes(b"test xontent\n")
    report = build_asset_report(config, root, required_packages={})
    assert not report["ready"]
    assert any("Git blob mismatch" in issue for issue in report["blockers"])


def test_lock_resolution_uses_active_markers_and_rejects_ambiguous_versions(tmp_path):
    from importlib import metadata
    import tomllib
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    original = tomllib.loads((Path(__file__).resolve().parents[1] / "uv.lock").read_text())
    packages = [item for item in original["package"] if item["name"] != "numpy"]
    packages += [
        {"name": "numpy", "version": metadata.version("numpy"), "resolution-markers": ["python_full_version < '99' and sys_platform != 'nonexistent-platform'"]},
        {"name": "numpy", "version": "0.0-inactive", "resolution-markers": ["python_full_version >= '99' or sys_platform == 'nonexistent-platform'"]},
    ]
    lock = tmp_path / "uv.lock"

    def save_lock():
        lock.write_text("\n".join("[[package]]\n" + "\n".join(f"{key} = {json.dumps(item[key])}" for key in ("name", "version", "resolution-markers") if key in item) for item in packages))

    save_lock()
    report = build_asset_report(config, root, lock_path=lock)
    assert report["required_packages"]["numpy"] == metadata.version("numpy")
    packages.append({"name": "numpy", "version": "0.0-ambiguous"})
    save_lock()
    with pytest.raises(ValueError, match="Ambiguous locked versions.*numpy"):
        build_asset_report(config, root, lock_path=lock)


def test_model_environment_disables_import_time_price_map_network(tmp_path):
    from amem_repro.preflight import asset_environment

    environment = asset_environment(tmp_path / "assets")
    assert environment["LITELLM_LOCAL_MODEL_COST_MAP"] == "True"
    assert environment["LITELLM_MODE"] == "PRODUCTION"
    assert environment["PYTHON_DOTENV_DISABLED"] == "1"
    assert environment["HF_HUB_OFFLINE"] == "1"
    assert environment["TRANSFORMERS_OFFLINE"] == "1"
    assert environment["NLTK_DATA"].endswith("/assets/nltk_data")


@pytest.mark.parametrize("kind", ["tokenizer-file", "directory", "symlink"])
def test_extra_snapshot_entries_invalidate_prepared_assets(tmp_path, kind):
    from amem_repro.preflight import build_asset_report, prepare_asset_layout, verify_asset_report

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    report = build_asset_report(config, root, required_packages={})
    snapshot = root / "huggingface/hub/models--example--encoder/snapshots/frozen"
    if kind == "tokenizer-file":
        (snapshot / "added_tokens.json").write_text('{"different": 123}')
    elif kind == "directory":
        (snapshot / "unverified-model").mkdir()
    else:
        (snapshot / "special_tokens_map.json").symlink_to(snapshot / "model.safetensors")
    with pytest.raises(ValueError, match="Unexpected snapshot"):
        prepare_asset_layout(root, config)
    changed = build_asset_report(config, root, required_packages={})
    assert not changed["ready"]
    assert any("Unexpected snapshot" in issue for issue in changed["blockers"])
    with pytest.raises(ValueError, match="Asset preflight"):
        verify_asset_report(report, root, config, required_packages={})


@pytest.mark.parametrize("package", ["httpx", "httpcore", "scipy"])
def test_transport_and_embedding_dependency_drift_blocks_preflight(tmp_path, monkeypatch, package):
    from importlib import metadata
    from amem_repro.preflight import build_asset_report, prepare_asset_layout

    root, config = fixture_assets(tmp_path)
    prepare_asset_layout(root, config)
    installed_version = metadata.version
    monkeypatch.setattr(metadata, "version", lambda name: "0.0-drift" if name == package else installed_version(name))
    report = build_asset_report(config, root)
    assert not report["ready"]
    assert any(f"Dependency {package}:" in issue for issue in report["blockers"])
