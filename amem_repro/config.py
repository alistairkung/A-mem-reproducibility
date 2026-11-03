"""Approved configuration and secret-free deterministic provenance."""

import hashlib
import copy
import json
from pathlib import Path
import subprocess

AUTHOR_REVISION = "f9a173dec325d84fcc97e7828775c7b241c33466"
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
    if fingerprint(config) not in (fingerprint(DEFAULT_CONFIG), fingerprint(RUN2_CONFIG)):
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


def verified_author_bytes(repo_root, relative_path):
    """Return only the exact bytes checked against the frozen Git blob."""
    root = Path(repo_root)
    expected = subprocess.check_output(
        ["git", "show", f"{AUTHOR_REVISION}:{relative_path}"], cwd=root
    )
    current = (root / relative_path).read_bytes()
    if current != expected:
        raise ValueError(f"Frozen author source changed: {relative_path}")
    return current


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
        current = verified_author_bytes(root, path)
        hashes[path] = hashlib.sha256(current).hexdigest()
    support = [*root.glob("amem_repro/**/*.py"), *root.glob("config/*.json")]
    support += [
        root / name for name in ("pyproject.toml", "uv.lock") if (root / name).exists()
    ]
    for path in sorted(support):
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    return {"author_revision": AUTHOR_REVISION, "files": hashes}
