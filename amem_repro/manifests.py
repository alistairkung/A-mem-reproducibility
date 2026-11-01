"""Freeze dataset identities without importing the author's runtime modules."""

import argparse
import hashlib
import json
import random
from pathlib import Path

DATASET_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
SCOPES = ("full", "fallback", "smoke", "pilot")


def _sessions(sample):
    return [
        (key, value)
        for key, value in sample["conversation"].items()
        if key.startswith("session_") and isinstance(value, list)
    ]


def build_manifest(dataset_path, scope):
    """Return immutable source identities; indices always refer to the full JSON file."""
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope: {scope}")
    raw = Path(dataset_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != DATASET_SHA256:
        raise ValueError("Dataset differs from frozen release")
    samples = json.loads(raw)
    conversations = []
    for sample_index, sample in enumerate(samples):
        original_id = sample["sample_id"]
        sessions = _sessions(sample)
        questions = []
        for index, qa in enumerate(sample["qa"]):
            questions.append(
                {
                    "question_id": f"{original_id}:qa:{index}",
                    "original_qa_index": index,
                    "category": qa["category"],
                    "question_sha256": hashlib.sha256(
                        qa["question"].encode()
                    ).hexdigest(),
                    "answer": qa.get("answer"),
                    "adversarial_answer": qa.get("adversarial_answer"),
                    "evidence": qa.get("evidence", []),
                }
            )
        conversations.append(
            {
                "original_id": original_id,
                "sample_index": sample_index,
                "session_keys": [key for key, _ in sessions],
                "turn_ids": [turn["dia_id"] for _, turns in sessions for turn in turns],
                "question_indices": list(range(len(questions))),
                "questions": questions,
            }
        )
    if scope == "fallback":
        ordered = sorted(
            conversations, key=lambda c: (len(c["turn_ids"]), c["original_id"])
        )
        rng = random.Random(42)
        conversations = [
            rng.choice(group) for group in (ordered[:3], ordered[3:6], ordered[6:])
        ]
    elif scope == "smoke":
        conversations = [conversations[0]]
        conversation = conversations[0]
        first_key, first_turns = _sessions(samples[0])[0]
        conversation["session_keys"] = [first_key]
        conversation["turn_ids"] = [t["dia_id"] for t in first_turns]
        conversation["question_indices"] = [0, 1, 2, 4]
        conversation["questions"] = [conversation["questions"][i] for i in [0, 1, 2, 4]]
    elif scope == "pilot":
        conversations = [c for c in conversations if c["original_id"] == "conv-50"]
    return {
        "manifest_version": 1,
        "protocol_id": "amem-controlled-reproduction-v1",
        "scope": scope,
        "dataset_path": "data/locomo10.json",
        "dataset_sha256": digest,
        "conversations": conversations,
        "totals": {
            "conversations": len(conversations),
            "turns": sum(len(c["turn_ids"]) for c in conversations),
            "questions": sum(len(c["questions"]) for c in conversations),
        },
    }


def write_manifests(dataset_path, output_dir):
    """Write deterministic reviewed manifests; never select using model performance."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for scope in SCOPES:
        path = directory / f"{scope}.json"
        path.write_text(
            json.dumps(
                build_manifest(dataset_path, scope), indent=2, ensure_ascii=False
            )
            + "\n"
        )
        paths.append(path)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="data/locomo10.json")
    parser.add_argument("--output", default="manifests")
    args = parser.parse_args()
    write_manifests(args.dataset, args.output)
