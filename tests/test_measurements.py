import unittest
from types import SimpleNamespace
from amem_repro.measurements import (
    observe_retrieval,
    TokenCounter,
    summarize_generations,
)


class MeasurementsTests(unittest.TestCase):
    def test_counts_follow_original_search_without_extra_calls_or_context_changes(self):
        class Retriever:
            calls = 0

            def search(self, query, k):
                self.calls += 1
                return [0, 1]

        retriever = Retriever()
        system = SimpleNamespace(
            retriever=retriever,
            memories={
                "a": SimpleNamespace(links=[1, 1, -1]),
                "b": SimpleNamespace(links=[0]),
            },
        )

        def raw(query, k):
            self.assertEqual(list(system.retriever.search(query, k)), [0, 1])
            return "original context unchanged"

        system.find_related_memories_raw = raw
        text, event = observe_retrieval(
            system,
            "query",
            2,
            TokenCounter(str.split, "whitespace", "fixture-v1", False),
        )
        self.assertEqual(text, "original context unchanged")
        self.assertEqual(retriever.calls, 1)
        self.assertEqual(event["initial_count"], 2)
        self.assertEqual(event["expanded_count"], 5)
        self.assertEqual(event["context_tokens"], 3)
        self.assertFalse(event["token_count_exact"])
        self.assertEqual(retriever.search("x", 1), [0, 1])

    def test_physical_attempt_usage_is_counted_once_and_missing_usage_is_unknown(self):
        rows = [
            {
                "stage": "shared_decision",
                "usage": {"prompt_tokens": 100, "completion_tokens": 10},
                "attempts": [
                    {"usage": {"prompt_tokens": 50, "completion_tokens": 5}},
                    {"usage": {"prompt_tokens": 100, "completion_tokens": 10}},
                ],
            },
            {"stage": "answer", "usage": None, "attempts": [{"usage": None}]},
        ]
        summary = summarize_generations(
            rows,
            {"input_per_million": 0.3, "output_per_million": 1.2, "pricing_id": "test"},
        )
        self.assertEqual(summary["shared_decision"]["input_tokens"], 150)
        self.assertEqual(summary["shared_decision"]["output_tokens"], 15)
        self.assertEqual(summary["answer"]["unknown_attempts"], 1)
        self.assertIsNone(summary["answer"]["total_cost_usd"])
        self.assertAlmostEqual(summary["shared_decision"]["total_cost_usd"], 0.000063)


class TokenFailureTests(unittest.TestCase):
    def test_failed_counter_keeps_original_context_and_records_unknown(self):
        retriever = SimpleNamespace(search=lambda *a, **k: [0])
        system = SimpleNamespace(
            retriever=retriever, memories={"a": SimpleNamespace(links=[])}
        )
        system.find_related_memories_raw = lambda query, k: (
            system.retriever.search(query, k) and "original bytes"
        )

        def failed(text):
            raise RuntimeError("counter unavailable")

        text, event = observe_retrieval(
            system, "q", 10, TokenCounter(failed, "verified-candidate", "v1")
        )
        self.assertEqual(text, "original bytes")
        self.assertIsNone(event["context_tokens"])
        self.assertEqual(event["token_count_error"], "RuntimeError")


class ActionTimingTests(unittest.TestCase):
    def test_observer_counts_real_branches_without_changing_return(self):
        import ast, json
        from pathlib import Path
        from amem_repro.measurements import observe_actions

        root = Path(__file__).resolve().parents[1]
        tree = ast.parse((root / "memory_layer.py").read_text())
        cls = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "AgenticMemorySystem"
        )
        fn = next(
            n
            for n in cls.body
            if isinstance(n, ast.FunctionDef) and n.name == "_evolve"
        )
        ns = {"json": json, "MemoryNote": object, "as_index": lambda x: x}
        exec(
            compile(
                ast.Module(body=[fn], type_ignores=[]),
                str(root / "memory_layer.py"),
                "exec",
            ),
            ns,
        )
        decision = {
            "should_evolve": True,
            "actions": ["strengthen", "update_neighbor"],
            "suggested_connections": [0],
            "tags_to_update": ["new"],
            "new_context_neighborhood": ["updated"],
            "new_tags_neighborhood": [["updated"]],
        }
        older = SimpleNamespace(context="old", tags=["old"])
        new = SimpleNamespace(
            context="new", content="text", keywords=[], links=[], tags=[]
        )
        system = SimpleNamespace(
            find_related_memories=lambda *a, **k: ("neighbor", [0]),
            evolution_system_prompt="{content}",
            memories={"old": older},
            refresh_index=False,
            llm_controller=SimpleNamespace(
                llm=SimpleNamespace(get_completion=lambda *a, **k: json.dumps(decision))
            ),
        )
        events = []
        with observe_actions(root, events.append):
            result = ns["_evolve"](system, new)
        self.assertEqual(result, (True, new))
        self.assertEqual(new.links, [0])
        self.assertEqual(older.context, "updated")
        self.assertEqual(
            [e["action"] for e in events], ["strengthen", "update_neighbor"]
        )
        self.assertTrue(
            all(e["duration_seconds"] >= 0 and e["api_calls"] == 0 for e in events)
        )


class ObservationFailureTests(unittest.TestCase):
    def test_observer_failure_does_not_change_author_action_result(self):
        import ast, json
        from pathlib import Path
        from amem_repro.measurements import observe_actions

        root = Path(__file__).resolve().parents[1]
        tree = ast.parse((root / "memory_layer.py").read_text())
        cls = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "AgenticMemorySystem"
        )
        fn = next(
            n
            for n in cls.body
            if isinstance(n, ast.FunctionDef) and n.name == "_evolve"
        )
        ns = {"json": json, "MemoryNote": object, "as_index": lambda x: x}
        exec(
            compile(
                ast.Module(body=[fn], type_ignores=[]),
                str(root / "memory_layer.py"),
                "exec",
            ),
            ns,
        )
        decision = {
            "should_evolve": True,
            "actions": ["strengthen"],
            "suggested_connections": [0],
            "tags_to_update": ["new"],
        }
        new = SimpleNamespace(
            context="new", content="text", keywords=[], links=[], tags=[]
        )
        system = SimpleNamespace(
            find_related_memories=lambda *a, **k: ("neighbor", [0]),
            evolution_system_prompt="{content}",
            memories={"old": SimpleNamespace(context="old", tags=[])},
            llm_controller=SimpleNamespace(
                llm=SimpleNamespace(get_completion=lambda *a, **k: json.dumps(decision))
            ),
        )

        def broken(event):
            raise OSError("observer unavailable")

        with observe_actions(root, broken) as failures:
            result = ns["_evolve"](system, new)
        self.assertEqual(result, (True, new))
        self.assertEqual(new.links, [0])
        self.assertEqual(failures, ["OSError"])
