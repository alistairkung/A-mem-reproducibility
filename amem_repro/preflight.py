"""Verify frozen local assets without creating clients or downloading models.

Local tokenizer counts are reproducible observations. Equivalence to the hosted
DeepSeek tokenizer remains unverified; API usage is the billing/prompt authority.
"""
import hashlib
from importlib import metadata
import json
from pathlib import Path
import tomllib
import zipfile

from .config import fingerprint

_ROOT = Path(__file__).resolve().parents[1]
_PACKAGES = (
    "numpy", "sentence-transformers", "scikit-learn", "torch", "transformers",
    "nltk", "rank-bm25", "openai", "litellm", "ollama", "rouge-score",
    "bert-score", "tqdm", "pandas", "python-dotenv", "requests", "jsonschema",
    "huggingface-hub", "tokenizers", "safetensors", "packaging", "httpx", "httpcore", "scipy",
)


def _config(path):
    path = Path(path or _ROOT / "config/assets.json")
    value = json.loads(path.read_text())
    if value.get("asset_manifest_version") != 2:
        raise ValueError("Unsupported local asset manifest version")
    return value


def _inside(root, relative):
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError("Asset path escapes prepared asset root")
    return path


def _digest(path, algorithm="sha256", git_blob=False):
    digest = hashlib.new(algorithm)
    if git_blob:
        digest.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as source:
        for part in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def _snapshot(root, asset):
    name = "models--" + asset["repository"].replace("/", "--")
    return _inside(root, f"huggingface/hub/{name}/snapshots/{asset['revision']}")


def _verify_snapshot_inventory(root, asset):
    """Optional tokenizer/adapter files can change model loading too."""
    snapshot = _snapshot(root, asset)
    files = {Path(item["path"]) for item in asset["files"]}
    directories = {parent for file in files for parent in file.parents if parent != Path(".")}
    for path in snapshot.rglob("*"):
        relative = path.relative_to(snapshot)
        if path.is_dir() and not path.is_symlink():
            allowed = relative in directories
        else:
            # Ordinary HF blob symlinks are valid only for listed files; directory
            # symlinks are rejected rather than traversed into an unverified tree.
            allowed = relative in files and path.is_file()
        if not allowed:
            raise ValueError(f"Unexpected snapshot entry: {relative.as_posix()}")
        _inside(root, path.relative_to(root))


def _verify_file(path, specification):
    if not path.is_file():
        raise ValueError(f"Missing asset file: {path.name}")
    if "size" in specification and path.stat().st_size != specification["size"]:
        raise ValueError(f"Asset size mismatch: {path.name}")
    sha256 = _digest(path)
    if "sha256" in specification:
        if sha256 != specification["sha256"]:
            raise ValueError(f"Asset checksum mismatch: {path.name}")
    elif "git_blob" in specification:
        if _digest(path, "sha1", git_blob=True) != specification["git_blob"]:
            raise ValueError(f"Asset Git blob mismatch: {path.name}")
    else:
        raise ValueError("Asset has no frozen checksum")
    return sha256


def _archive_members(archive):
    for member in archive.infolist():
        if member.is_dir():
            continue
        # Archives are immutable official data, but still reject extraction escapes.
        name = Path(member.filename)
        if name.is_absolute() or ".." in name.parts or (member.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError("Unsafe NLTK archive member")
        yield member


def prepare_asset_layout(asset_root, asset_config_path=None):
    """Prepare only verified local bytes; never download or replace changed refs.

    Call after downloading the exact files listed in config/assets.json to the
    documented cache layout. Original model identifiers remain untouched.
    """
    root = Path(asset_root).resolve()
    config = _config(asset_config_path)
    # Validate all sources before changing the usable cache layout.
    for asset in config["assets"]:
        _verify_snapshot_inventory(root, asset)
        for file in asset["files"]:
            _verify_file(_inside(root, _snapshot(root, asset).relative_to(root) / file["path"]), file)
    for item in config["nltk"]["archives"]:
        _verify_file(_inside(root, "nltk_archives/" + item["filename"]), item)
    for asset in config["assets"]:
        cache = _snapshot(root, asset).parent.parent
        ref = cache / "refs/main"
        if ref.exists() and ref.read_text().strip() != asset["revision"]:
            raise ValueError("Prepared asset main ref differs from frozen revision")
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text(asset["revision"])
        for alias in asset.get("cache_aliases", []):
            target = _inside(root, "huggingface/hub/models--" + alias.replace("/", "--"))
            if target.exists() or target.is_symlink():
                if target.resolve() != cache.resolve():
                    raise ValueError("Prepared asset alias differs from frozen cache")
            else:
                target.symlink_to(cache, target_is_directory=True)
    for item in config["nltk"]["archives"]:
        with zipfile.ZipFile(root / "nltk_archives" / item["filename"]) as archive:
            for member in _archive_members(archive):
                path = _inside(root, f"nltk_data/{item['directory']}/{member.filename}")
                payload = archive.read(member)
                if path.exists() and path.read_bytes() != payload:
                    raise ValueError("Prepared NLTK data differs from frozen archive")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)


def build_asset_report(asset_config_path, asset_root, *, required_packages=None, lock_path=None):
    """Collect local checksums and installed versions; readiness fails closed."""
    root = Path(asset_root).resolve()
    config = _config(asset_config_path)
    checks, blockers = {}, []
    for asset in config["assets"]:
        try:
            snapshot = _snapshot(root, asset)
            _verify_snapshot_inventory(root, asset)
            for file in asset["files"]:
                path = _inside(root, snapshot.relative_to(root) / file["path"])
                checks[str(path.relative_to(root))] = _verify_file(path, file)
            cache = snapshot.parent.parent
            if (cache / "refs/main").read_text().strip() != asset["revision"]:
                raise ValueError("Prepared main ref differs from frozen revision")
            for alias in asset.get("cache_aliases", []):
                target = _inside(root, "huggingface/hub/models--" + alias.replace("/", "--"))
                if target.resolve() != cache.resolve():
                    raise ValueError("Prepared alias differs from frozen cache")
        except (ValueError, OSError) as error:
            blockers.append(f"{asset['id']}: {error}")
    for item in config["nltk"]["archives"]:
        try:
            path = _inside(root, "nltk_archives/" + item["filename"])
            checks[str(path.relative_to(root))] = _verify_file(path, item)
            with zipfile.ZipFile(path) as archive:
                for member in _archive_members(archive):
                    path = _inside(root, f"nltk_data/{item['directory']}/{member.filename}")
                    expected = hashlib.sha256(archive.read(member)).hexdigest()
                    checks[str(path.relative_to(root))] = _verify_file(path, {"sha256": expected})
        except (ValueError, OSError, zipfile.BadZipFile) as error:
            blockers.append(f"NLTK {item['id']}: {error}")
    if required_packages is None:
        lock = tomllib.loads(Path(lock_path or _ROOT / "uv.lock").read_text())
        from packaging.markers import Marker

        required_packages = {}
        for name in _PACKAGES:
            versions = {
                package["version"]
                for package in lock["package"]
                if package["name"] == name and "version" in package
                and (
                    not package.get("resolution-markers")
                    or any(Marker(marker).evaluate() for marker in package["resolution-markers"])
                )
            }
            if len(versions) > 1:
                raise ValueError(f"Ambiguous locked versions for {name} in active environment")
            if not versions:
                raise ValueError(f"No active locked version for {name}")
            required_packages[name] = versions.pop()
    installed = {}
    for package, expected in required_packages.items():
        try:
            actual = metadata.version(package)
            installed[package] = actual
            if actual != expected:
                blockers.append(f"Dependency {package}: expected {expected}, installed {actual}")
        except metadata.PackageNotFoundError:
            blockers.append(f"Missing dependency: {package}")
    return {
        "preflight_version": 1,
        "verification_scope": "local-asset-integrity-and-dependency-versions-only",
        "runtime_verified": False,
        "paid_execution_authorized": False,
        "asset_manifest_version": config["asset_manifest_version"],
        "asset_config_fingerprint": fingerprint(config),
        "assets": {a["id"]: {"repository": a["repository"], "revision": a["revision"]} for a in config["assets"]},
        "nltk_revision": config["nltk"]["revision"],
        "files": checks,
        "required_packages": required_packages,
        "installed_packages": installed,
        "tokenizer_hosted_parity": config["tokenizer"]["hosted_parity"],
        "tokenizer_official_reference": config["tokenizer"].get("official_reference"),
        "tokenizer_limitation": "Pinned local text-token counts; hosted DeepSeek equivalence is unverified. API usage is authoritative for final prompt tokens and billing.",
        "ready": not blockers,
        "blockers": blockers,
    }


def verify_asset_report(report, asset_root, asset_config_path=None, *, required_packages=None, lock_path=None):
    """Recheck a saved receipt before execution, including dependency drift."""
    if report.get("preflight_version") != 1:
        raise ValueError("Unsupported asset preflight version")
    current = build_asset_report(asset_config_path, asset_root, required_packages=required_packages, lock_path=lock_path)
    if not current["ready"] or not report.get("ready") or current != report:
        raise ValueError("Asset preflight failed or differs from saved receipt")


def make_token_counter(asset_root, report, asset_config_path=None, *, required_packages=None):
    """Load verified local tokenizer bytes; never assert hosted token parity."""
    verify_asset_report(report, asset_root, asset_config_path, required_packages=required_packages)
    config = _config(asset_config_path)
    asset = next(item for item in config["assets"] if item["id"] == config["tokenizer"]["asset_id"])
    path = _inside(asset_root, _snapshot(asset_root, asset).relative_to(Path(asset_root).resolve()) / "tokenizer.json")
    from tokenizers import Tokenizer
    from .measurements import TokenCounter

    tokenizer = Tokenizer.from_file(str(path))
    return TokenCounter(
        encode=lambda text: tokenizer.encode(text, add_special_tokens=False).ids,
        method=f"{asset['repository']} tokenizer.json; tokenizers={metadata.version('tokenizers')}; add_special_tokens=False; hosted parity unverified",
        revision=asset["revision"],
        exact=False,
    )


def asset_environment(asset_root):
    """Apply these values before importing model libraries in a fresh process."""
    root = Path(asset_root).resolve()
    return {
        "HF_HOME": str(root / "huggingface"),
        "HF_HUB_CACHE": str(root / "huggingface/hub"),
        "SENTENCE_TRANSFORMERS_HOME": str(root / "huggingface/hub"),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        # Avoid LiteLLM's unrelated import-time HTTP price-map refresh.
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        # Credentials must come from the explicitly configured process, never dotenv.
        "LITELLM_MODE": "PRODUCTION",
        "PYTHON_DOTENV_DISABLED": "1",
        "NLTK_DATA": str(root / "nltk_data"),
    }
