"""Local, provenance-verified study artifacts; no model or network dependencies."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .config import (
    reject_credentials as _safe, STRICT_PROVIDER_POLICY, validate_provider_policy,
)


class CacheRejected(ValueError):
    """A cache cannot be used as a complete, matching memory build."""


def _json_bytes(value):
    return (
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _write(path, value):
    with path.open("wb") as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


class CacheStore:
    def __init__(self, root):
        self.root = Path(root)

    def path_for(self, identity):
        return self.root / _digest(_json_bytes(identity))

    def save(self, identity, state):
        _safe(identity)
        _safe(state)
        _validate_state(state)
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.path_for(identity)
        if destination.exists():
            raise CacheRejected(
                "A build already exists; use a new repetition or verify and load it"
            )
        temporary = Path(tempfile.mkdtemp(prefix=".incomplete-", dir=self.root))
        try:
            _write(temporary / "identity.json", identity)
            _write(temporary / "state.json", state)
            _write(
                temporary / "complete.json",
                {
                    "identity_sha256": _digest(
                        (temporary / "identity.json").read_bytes()
                    ),
                    "state_sha256": _digest((temporary / "state.json").read_bytes()),
                },
            )
            os.rename(temporary, destination)
        except BaseException:
            # Retain the partial bundle for diagnosis; it has no usable public cache identity.
            raise
        return destination

    def load(self, identity):
        path = self.path_for(identity)
        try:
            marker = json.loads((path / "complete.json").read_bytes())
            identity_bytes = (path / "identity.json").read_bytes()
            state_bytes = (path / "state.json").read_bytes()
            if marker != {
                "identity_sha256": _digest(identity_bytes),
                "state_sha256": _digest(state_bytes),
            }:
                raise CacheRejected("Cache integrity check failed")
            if json.loads(identity_bytes) != identity:
                raise CacheRejected("Cache provenance mismatch")
            state = json.loads(state_bytes)
            _safe(state)
            _validate_state(state)
            return state
        except (OSError, json.JSONDecodeError, KeyError) as error:
            raise CacheRejected("Missing, incomplete or malformed cache") from error


def build_identity(config, conversation, dataset_sha256, source_hashes, repetition=0,
                   *, provider_contract_policy=STRICT_PROVIDER_POLICY):
    from .config import validate_config

    validate_config(config)
    validate_provider_policy(provider_contract_policy)
    if not source_hashes or not dataset_sha256 or repetition < 0:
        raise ValueError(
            "Source/data fingerprints and nonnegative repetition are required"
        )
    identity = {
        "configuration": config,
        "dataset_sha256": dataset_sha256,
        "source_hashes": source_hashes,
        "repetition": repetition,
        "conversation": conversation,
        "provider_contract_policy": provider_contract_policy,
    }
    _safe(identity)
    return json.loads(_json_bytes(identity))


def _plain(value):
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _validate_state(state):
    try:
        notes = state["notes"]
        index = state["retriever"]
        if len(notes) != len(index["corpus"]) or len(notes) != len(index["embeddings"]):
            raise CacheRejected("Notes and index rows are not aligned")
        keys = [note["key"] for note in notes]
        if len(keys) != len(set(keys)) or [n["index"] for n in notes] != list(
            range(len(notes))
        ):
            raise CacheRejected("Note order or identities are invalid")
        for document, position in index["document_ids"].items():
            if (
                isinstance(position, bool)
                or not isinstance(position, int)
                or not 0 <= position < len(notes)
            ):
                raise CacheRejected("Invalid document row mapping")
            if index["corpus"][position] != document:
                raise CacheRejected("Document row mapping does not match corpus")
        for note in notes:
            if not isinstance(note["attributes"], dict):
                raise CacheRejected("Invalid note state")
            if note["attributes"].get("id") != note["key"]:
                raise CacheRejected("Note identity mismatch")
        if not isinstance(state["evo_threshold"], int) or state["evo_threshold"] <= 0:
            raise CacheRejected("Invalid consolidation threshold")
        if not isinstance(state["outcomes"], list):
            raise CacheRejected("Missing evolution outcomes")
        if not isinstance(state["evo_cnt"], int) or state["evo_cnt"] < 0:
            raise CacheRejected("Invalid evolution counter")
    except (KeyError, TypeError) as error:
        raise CacheRejected("Missing complete memory/index state") from error


def snapshot_memory(system, outcomes=(), *, validate=True):
    retriever = system.retriever
    embeddings = retriever.embeddings
    state = {
        "notes": [
            {"index": index, "key": key, "attributes": _plain(vars(note))}
            for index, (key, note) in enumerate(system.memories.items())
        ],
        "retriever": {
            "corpus": list(retriever.corpus),
            "embeddings": _plain(embeddings) if embeddings is not None else [],
            "embedding_dtype": str(embeddings.dtype)
            if hasattr(embeddings, "dtype")
            else None,
            "document_ids": _plain(retriever.document_ids),
        },
        "evo_cnt": system.evo_cnt,
        "evo_threshold": system.evo_threshold,
        "outcomes": _plain(list(outcomes)),
    }
    _safe(state)
    if validate:
        _validate_state(state)
    return json.loads(_json_bytes(state))


def restore_memory(system, state, *, note_type):
    _validate_state(state)
    restored = {}
    for saved in state["notes"]:
        note = note_type.__new__(note_type)
        note.__dict__.update(json.loads(_json_bytes(saved["attributes"])))
        restored[saved["key"]] = note
    index = state["retriever"]
    embeddings = index["embeddings"]
    if index.get("embedding_dtype"):
        import numpy as np

        embeddings = np.asarray(embeddings, dtype=index["embedding_dtype"])
    system.memories = restored
    system.retriever.corpus = list(index["corpus"])
    system.retriever.embeddings = embeddings
    system.retriever.document_ids = dict(index["document_ids"])
    system.evo_cnt = state["evo_cnt"]
    system.evo_threshold = state["evo_threshold"]


class RunLedger:
    """Durable events and output-based completion without hiding degraded runs."""

    def __init__(self, directory, run_id, expected_question_ids, *,
                 provider_contract_policy=STRICT_PROVIDER_POLICY):
        validate_provider_policy(provider_contract_policy)
        self.provider_contract_policy = provider_contract_policy
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "events.jsonl"
        if self.path.exists():
            raise FileExistsError(
                "Run already exists; paid recovery requires separate approval"
            )
        expected = list(expected_question_ids)
        if len(expected) != len(set(expected)):
            raise ValueError("Duplicate expected question identity")
        self.run_id = run_id
        self.expected = set(expected)
        self.results = set()
        self.events = []
        self.path.touch()
        _write(
            self.directory / "run.json",
            {"run_id": run_id, "expected_question_ids": expected,
             "provider_contract_policy": provider_contract_policy},
        )

    def record(self, event):
        _safe(event)
        value = json.loads(_json_bytes(event))
        if value.get("type") == "question_result":
            key = value["question_id"]
            if key not in self.expected or key in self.results:
                raise ValueError("Unexpected or duplicate question result")
            self.results.add(key)
        value["run_id"] = self.run_id
        with self.path.open("ab") as stream:
            stream.write(_json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        self.events.append(value)

    def preserve_partial_memory(self, identity, state):
        value = {"identity": identity, "state": state, "complete": False}
        _safe(value)
        _write(self.directory / "partial-memory.json", value)

    def status(self):
        if self.results != self.expected or any(
            e.get("type") == "run_abort" for e in self.events
        ):
            return "incomplete"
        if any(e.get("type") == "failure" for e in self.events):
            return "degraded"
        return "complete"

    def finish(self):
        deviations = [e for e in self.events if e.get("type") == "failure"
                      and e.get("kind") == "provider_contract_deviation"]
        current = [e for e in deviations if not e.get("from_cache")]
        inherited = [e for e in deviations if e.get("from_cache")]
        result = {
            "run_id": self.run_id,
            "status": self.status(),
            "expected_questions": len(self.expected),
            "completed_questions": len(self.results),
            "failures": [e for e in self.events if e.get("type") == "failure"],
            "provider_contract_policy": self.provider_contract_policy,
            "provider_contract_deviation_count": len(current),
            "inherited_provider_contract_deviation_count": len(inherited),
            "validation_copy_transformed_item_count": sum(
                len(e["compatibility_deviation"]["transformations"]) for e in current
            ),
            "inherited_validation_copy_transformed_item_count": sum(
                len(e["compatibility_deviation"]["transformations"]) for e in inherited
            ),
        }
        _write(self.directory / "summary.json", result)
        return result
