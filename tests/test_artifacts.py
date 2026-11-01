import json
import tempfile
import unittest
from pathlib import Path

from amem_repro.artifacts import (
    CacheRejected,
    CacheStore,
    RunLedger,
    snapshot_memory,
    restore_memory,
)


class CacheTests(unittest.TestCase):
    def test_completed_bundle_roundtrips_and_tampering_is_rejected(self):
        identity = {"dataset": "abc", "condition": "full", "repetition": 0}
        state = {
            "notes": [],
            "retriever": {"corpus": [], "embeddings": [], "document_ids": {}},
            "evo_cnt": 0,
            "evo_threshold": 100,
            "outcomes": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            store = CacheStore(directory)
            path = store.save(identity, state)
            self.assertEqual(store.load(identity), state)
            payload = json.loads((path / "state.json").read_text())
            payload["evo_cnt"] = 100
            (path / "state.json").write_text(json.dumps(payload))
            with self.assertRaises(CacheRejected):
                store.load(identity)


class LifecycleTests(unittest.TestCase):
    def test_incomplete_mismatched_or_duplicate_build_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CacheStore(directory)
            identity = {"dataset": "a", "condition": "full", "repetition": 0}
            state = {
                "notes": [],
                "retriever": {"corpus": [], "embeddings": [], "document_ids": {}},
                "evo_cnt": 0,
                "evo_threshold": 100,
                "outcomes": [],
            }
            path = store.save(identity, state)
            with self.assertRaises(CacheRejected):
                store.load(dict(identity, condition="neither"))
            with self.assertRaises(CacheRejected):
                store.save(identity, state)
            (path / "complete.json").unlink()
            with self.assertRaises(CacheRejected):
                store.load(identity)

    def test_snapshot_preserves_note_order_links_index_and_counter(self):
        from types import SimpleNamespace as NS

        system = NS(
            memories={
                "b": NS(id="b", content="B", links=[1, 1], context="old", tags=["b"]),
                "a": NS(id="a", content="A", links=[], context="new", tags=["a"]),
            },
            retriever=NS(
                corpus=["first", "second"],
                embeddings=[[1.0, 0.0], [0.0, 1.0]],
                document_ids={"first": 0, "second": 1},
            ),
            evo_cnt=99,
            evo_threshold=100,
        )
        snapshot = snapshot_memory(system, outcomes=[{"should_evolve": True}])
        self.assertEqual([n["key"] for n in snapshot["notes"]], ["b", "a"])
        self.assertEqual(snapshot["notes"][0]["attributes"]["links"], [1, 1])
        restored = NS(memories={}, retriever=NS(embeddings=[]), evo_cnt=0)
        restore_memory(restored, snapshot, note_type=NS)
        self.assertEqual(restored.memories["b"].links, [1, 1])
        self.assertEqual(restored.retriever.corpus, ["first", "second"])
        self.assertEqual(restored.evo_cnt, 99)
        snapshot["retriever"]["corpus"].pop()
        with self.assertRaises(CacheRejected):
            restore_memory(restored, snapshot, note_type=NS)

    def test_ledger_classifies_without_losing_partial_results_or_costs(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = RunLedger(directory, "run-1", ["c:0", "c:1"])
            ledger.record({"type": "generation", "cost_usd": 0.25})
            ledger.record(
                {
                    "type": "question_result",
                    "question_id": "c:0",
                    "result": {"prediction": "unchanged"},
                }
            )
            self.assertEqual(ledger.status(), "incomplete")
            ledger.record(
                {
                    "type": "failure",
                    "level": "question",
                    "question_id": "c:1",
                    "kind": "metric_computation",
                }
            )
            ledger.record(
                {
                    "type": "question_result",
                    "question_id": "c:1",
                    "result": {"prediction": "zero", "metrics": {"f1": 0.0}},
                }
            )
            self.assertEqual(ledger.finish()["status"], "degraded")
            events = [
                json.loads(line)
                for line in (Path(directory) / "events.jsonl").read_text().splitlines()
            ]
            self.assertEqual(events[0]["cost_usd"], 0.25)
            self.assertEqual(events[1]["result"]["prediction"], "unchanged")
            with self.assertRaises(ValueError):
                ledger.record(
                    {"type": "question_result", "question_id": "c:0", "result": {}}
                )
            with self.assertRaises(ValueError):
                ledger.record({"type": "generation", "api_key": "secret"})


if __name__ == "__main__":
    unittest.main()
