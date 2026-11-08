"""Approved configuration and secret-free deterministic provenance."""

import hashlib
import copy
import json
from pathlib import Path
import subprocess

AUTHOR_REVISION = "f9a173dec325d84fcc97e7828775c7b241c33466"
UPSTREAM_README = "UPSTREAM_README.md"
# The scientific and report merge tips have different ancestry. Only
# their historical checkouts may use the old root README as the author copy.
LEGACY_README_TIPS = (
    "34f4ab5e96e9854c9b63492c473155ab4b65279a",  # PR #52 merge, includes 8485673
    "e736a007e243442ef65b156f184bb70b78c578a2",
)
STRICT_PROVIDER_POLICY = "strict-original-v1"
INDEX_STRING_POLICY = "canonical-index-strings-v1"
OUTPUT_TOKEN_POLICY = "d9a-shared-decision-4000-v1"


def validate_provider_policy(policy):
    if type(policy) is not str or policy not in (STRICT_PROVIDER_POLICY, INDEX_STRING_POLICY):
        raise ValueError("Unknown provider-contract policy")


DEFAULT_CONFIG = {
    "protocol_id": "amem-controlled-reproduction-v1",
    "model": {
        "id": "deepseek-flash",
        "base_url": "https://api.deepseek.com/beta",
        "route": "/chat/completions",
        "thinking": "disabled",
        "documented_version": "DeepSeek-V4.1-Flash-1017",
        "immutable_weights_pin": False,
    },
    "generation": {
        "temperature": 0.7,
        "temperature_c5": 0.5,
        "max_tokens": 1000,
        "shared_decision_max_tokens": 4000,
        "output_token_policy": OUTPUT_TOKEN_POLICY,
        "stream": False,
        "concurrency": 1,
    },
    "transport": {"timeout_seconds": 120, "max_retries": 2, "semantic_retries": 0},
    "retrieval": {"answer_k": 10, "construction_k": 5, "refresh_index": False},
    "memory": {
        "evo_threshold": 100,
        "counter_policy": "positive-decision",
        "initial_metadata": True,
    },
    "conditions": {
        "neither": {"strengthen": False, "update_neighbor": False},
        "linking_only": {"strengthen": True, "update_neighbor": False},
        "evolution_only": {"strengthen": False, "update_neighbor": True},
        "full": {"strengthen": True, "update_neighbor": True},
    },
    "selection_seed": 42,
    "option_order_seed": 42,
    "build_repetitions": 1,
    "scoring_policies": ["author-corrected-v1", "author-legacy-c5-v1"],
    "budget": {
        "ceiling_usd": 50,
        "contingency_usd": 8,
        "functional_allocation_usd": [1, 2],
        "pilot_allocation_usd": [5, 10],
    },
}


RUN2_CONFIG = copy.deepcopy(DEFAULT_CONFIG)
RUN2_CONFIG["protocol_id"] = "amem-controlled-reproduction-run2-v1"
RUN2_CONFIG["generation"].update(
    shared_decision_max_tokens=8192,
    output_token_policy="run2-shared-decision-8192-v1",
)

# Separate campaign: never relabel or migrate either DeepSeek campaign.
OPENROUTER_CONFIG = copy.deepcopy(DEFAULT_CONFIG)
OPENROUTER_CONFIG["protocol_id"] = "amem-gpt4omini-openrouter-20261104-v1"
OPENROUTER_CONFIG["model"] = {
    "id": "openai/gpt-4o-mini-2024-07-18",
    "base_url": "https://openrouter.ai/api/v1",
    "route": "/chat/completions",
    "documented_version": "gpt-4o-mini-2024-07-18",
    "immutable_weights_pin": False,
    "provider": {"order": ["openai"], "only": ["openai"],
                 "allow_fallbacks": False, "require_parameters": True},
}
OPENROUTER_CONFIG["generation"].update(
    shared_decision_max_tokens=4096,
    output_token_policy="gpt4omini-shared-decision-4096-v1",
)
OPENROUTER_CONFIG["transport"]["max_retries"] = 0
OPENROUTER_CONFIG["budget"] = {
    "ceiling_usd": 50, "contingency_usd": 8,
    "cell_allocation_usd": 5, "compatibility_allocation_usd": .25,
}


def stage_output_limits(config=None):
    """Return the explicitly selected frozen profile; Run1 remains the default."""
    if config is not None:
        validate_config(config)
    generation = (DEFAULT_CONFIG if config is None else config)["generation"]
    return {stage: generation["shared_decision_max_tokens"] if stage == "shared_decision"
            else generation["max_tokens"]
            for stage in ("metadata", "shared_decision", "query_keywords", "answer")}


_SECRET_KEYS = {
    "api_key",
    "secret",
    "secret_key",
    "password",
    "authorization",
    "access_token",
    "credentials",
    "langfuse_secret_key",
    "deepseek_api_key",
    "openai_api_key",
    "langfuse_public_key",
}


def reject_credentials(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower().replace("-", "_") in _SECRET_KEYS or any(
                part in str(key).lower().replace("-", "_")
                for part in (
                    "api_key",
                    "authorization",
                    "secret",
                    "password",
                    "access_token",
                )
            ):
                raise ValueError("Provenance contains a credential field")
            reject_credentials(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            reject_credentials(child)


def fingerprint(value):
    """Hash canonical JSON only after rejecting credential-bearing fields."""
    reject_credentials(value)
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_config(config):
    """Reject deviations rather than silently adjusting the approved protocol."""
    reject_credentials(config)
    if fingerprint(config) not in (fingerprint(DEFAULT_CONFIG), fingerprint(RUN2_CONFIG),
                                 fingerprint(OPENROUTER_CONFIG)):
        raise ValueError("Configuration differs from the frozen protocol")


def load_config(path=None):
    path = (
        Path(path)
        if path
        else Path(__file__).resolve().parents[1] / "config/study.json"
    )
    config = json.loads(path.read_text())
    validate_config(config)
    return config


def load_run2_config(path=None):
    config = json.loads((Path(path) if path else Path(__file__).resolve().parents[1] / "config/run2.json").read_text())
    validate_config(config)
    if config != RUN2_CONFIG:
        raise ValueError("Configuration differs from the frozen Run2 protocol")
    return config


def _author_readme_path(root):
    for tip in LEGACY_README_TIPS:
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", tip], cwd=root,
            stderr=subprocess.DEVNULL,
        ).returncode == 0:
            return "README.md"
    return UPSTREAM_README


def _verified_author_file(root, upstream_path):
    name = _author_readme_path(root) if upstream_path == "README.md" else upstream_path
    path = root / name
    if name == UPSTREAM_README and (path.is_symlink() or not path.is_file()):
        raise ValueError(f"Missing or invalid frozen author file: {name}")
    expected = subprocess.check_output(
        ["git", "show", f"{AUTHOR_REVISION}:{upstream_path}"], cwd=root
    )
    current = path.read_bytes()
    if current != expected:
        raise ValueError(f"Frozen author source changed: {name}")
    return name, current


def verified_author_bytes(repo_root, relative_path):
    """Return only the exact bytes checked against the frozen Git blob."""
    return _verified_author_file(Path(repo_root), relative_path)[1]


def source_fingerprint(repo_root):
    """Verify frozen author files against Git blobs without importing their code."""
    root = Path(repo_root)
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", AUTHOR_REVISION], cwd=root, text=True
    ).splitlines()
    paths = [
        p
        for p in paths
        if p.endswith((".py", ".sh"))
        or p in ("requirements.txt", "README.md", "LICENSE")
    ]
    hashes = {}
    for path in paths:
        name, current = _verified_author_file(root, path)
        hashes[name] = hashlib.sha256(current).hexdigest()
    support = [*root.glob("amem_repro/**/*.py"), *root.glob("config/*.json")]
    support += [
        root / name for name in ("pyproject.toml", "uv.lock") if (root / name).exists()
    ]
    for path in sorted(support):
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    return {"author_revision": AUTHOR_REVISION, "files": hashes}
