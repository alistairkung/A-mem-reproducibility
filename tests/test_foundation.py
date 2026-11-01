"""Offline vertical slice through unchanged author memory/answer methods."""

import ast
import collections
import datetime
import json
import re
import tempfile
import types
import typing
import unittest
import uuid
from pathlib import Path

from amem_repro.adapter import DeepSeekController
from amem_repro.author import make_agent_factory
from amem_repro.config import load_config, source_fingerprint
from amem_repro.manifests import build_manifest
from amem_repro.measurements import TokenCounter, summarize_generations
from amem_repro.runner import run_manifest
from amem_repro.scoring import AuthorScorer, rescore_records, CORRECTED, HISTORICAL
from test_scoring import dependencies

ROOT = Path(__file__).resolve().parents[1]


class LocalRetriever:
    """Deterministic embedding-service boundary; no models or vector packages."""

    def __init__(self, *args, **kwargs):
        self.corpus = []
        self.embeddings = []
        self.document_ids = {}

    def add_documents(self, documents):
        for document in documents:
            self.document_ids[document] = len(self.corpus)
            self.corpus.append(document)
            self.embeddings.append([1.0, 0.0])

    def search(self, query, k=5):
        return list(range(len(self.corpus) - 1, max(-1, len(self.corpus) - k - 1), -1))


class Provider:
    def __init__(self):
        self.requests = []
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(create=self.complete)
        )

    def complete(self, **request):
        self.requests.append(request)
        fields = request["tools"][0]["function"]["parameters"]["properties"]
        if "context" in fields:
            value = {"keywords": ["kw"], "context": "context", "tags": ["tag"]}
        elif "should_evolve" in fields:
            neighbors = re.findall(
                r"memory index:(\d+)", request["messages"][1]["content"]
            )
            value = {
                "should_evolve": True,
                "actions": ["strengthen", "update_neighbor"],
                "suggested_connections": [int(x) for x in neighbors],
                "tags_to_update": ["linked"],
                "new_context_neighborhood": ["updated"] * len(neighbors),
                "new_tags_neighborhood": [["updated"] for _ in neighbors],
            }
        elif "answer" in fields:
            value = {"answer": "saved"}
        else:
            value = {"keywords": "kw"}
        return {
            "id": "offline",
            "model": "deepseek-flash",
            "system_fingerprint": "mock-backend",
            "usage": {"prompt_tokens": 100, "completion_tokens": 10},
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "response",
                                    "arguments": json.dumps(value),
                                },
                            }
                        ]
                    },
                }
            ],
        }


def original_memory_module():
    module = types.ModuleType("offline_author_memory")
    module.__dict__.update(vars(typing))
    module.__dict__.update(
        json=json,
        re=re,
        datetime=datetime.datetime,
        uuid=uuid,
        np=types.SimpleNamespace(integer=int),
        FAILURES=collections.Counter(),
        SimpleEmbeddingRetriever=LocalRetriever,
        LLMController=object(),
    )
    tree = ast.parse((ROOT / "memory_layer.py").read_text())
    names = {
        "MemoryNote",
        "AgenticMemorySystem",
        "as_index",
        "valid_link",
        "note_document",
    }
    nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names
    ]
    exec(
        compile(
            ast.Module(body=nodes, type_ignores=[]),
            str(ROOT / "memory_layer.py"),
            "exec",
        ),
        module.__dict__,
    )
    return module


class FoundationTests(unittest.TestCase):
    def test_smoke_manifest_uses_original_algorithm_and_provider_boundary_offline(self):
        provider = Provider()
        factory = make_agent_factory(
            ROOT,
            memory_module=original_memory_module(),
            controller_factory=lambda observer: DeepSeekController(
                provider, observer=observer
            ),
            token_counter=TokenCounter(
                str.split, "whitespace-test-only", "fixture-v1", False
            ),
        )
        scorer = AuthorScorer(ROOT, dependencies=dependencies())
        with tempfile.TemporaryDirectory() as directory:
            result = run_manifest(
                ROOT / "data/locomo10.json",
                build_manifest(ROOT / "data/locomo10.json", "smoke"),
                load_config(),
                output_dir=Path(directory) / "run",
                cache_root=Path(directory) / "cache",
                source_hashes=source_fingerprint(ROOT),
                agent_factory=factory,
                scorer=scorer,
            )
            self.assertEqual(result["status"], "complete")
            self.assertEqual(len(provider.requests), 44)
            events = [
                json.loads(line)
                for line in (Path(directory) / "run/events.jsonl")
                .read_text()
                .splitlines()
            ]
            stage_counts = collections.Counter(
                e["stage"] for e in events if e["type"] == "generation"
            )
            self.assertEqual(
                stage_counts,
                {
                    "metadata": 18,
                    "shared_decision": 18,
                    "query_keywords": 4,
                    "answer": 4,
                },
            )
            actions = collections.Counter(
                e["action"] for e in events if e["type"] == "local_action"
            )
            self.assertEqual(actions, {"strengthen": 18, "update_neighbor": 18})
            retrieval = [e for e in events if e["type"] == "retrieval"]
            self.assertEqual(len(retrieval), 4)
            self.assertTrue(
                all(e["expanded_count"] > e["initial_count"] for e in retrieval)
            )
            records = [e["result"] for e in events if e["type"] == "question_result"]
            views = rescore_records(records, scorer)
            self.assertEqual(len(provider.requests), 44)
            self.assertEqual(
                [r["prediction"] for r in views[CORRECTED]["individual_results"]],
                ["saved"] * 4,
            )
            self.assertEqual(
                [r["question_id"] for r in views[CORRECTED]["individual_results"]],
                [r["question_id"] for r in views[HISTORICAL]["individual_results"]],
            )
            costs = summarize_generations(
                events,
                {
                    "input_per_million": 0.3,
                    "output_per_million": 1.2,
                    "pricing_id": "mock",
                },
            )
            self.assertEqual(sum(x["logical_calls"] for x in costs.values()), 44)
