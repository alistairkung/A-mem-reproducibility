import json
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

from amem_repro.config import DEFAULT_CONFIG
from amem_repro.manifests import build_manifest
from amem_repro.runner import run_manifest

ROOT = Path(__file__).resolve().parents[1]


class Agent:
    def __init__(self):
        self.memory_system = NS(
            memories={},
            retriever=NS(corpus=[], embeddings=[], document_ids={}),
            evo_cnt=0,
            evo_threshold=100,
        )
        self.added = []
        self.random_draws = []

    def add_memory(self, content, time=None):
        self.added.append((content, time))
        key = str(len(self.added))
        self.memory_system.memories[key] = NS(
            id=key, content=content, links=[], context="General", tags=[], keywords=[]
        )
        r = self.memory_system.retriever
        r.document_ids[content] = len(r.corpus)
        r.corpus.append(content)
        r.embeddings.append([1.0, 0.0])

    def answer_question(self, question, category, answer, rng):
        self.random_draws.append(rng.random())
        return '{"answer":"preserved"}', "original prompt", "original context"


def score(prediction, qa, legacy_c5=False):
    reference = qa.reference(legacy_c5)
    return reference, {"f1": float(prediction == reference)}


class RunnerTests(unittest.TestCase):
    def test_original_indices_order_and_predictions_survive_manifest_execution(self):
        manifest = build_manifest(ROOT / "data/locomo10.json", "pilot")
        conv = manifest["conversations"][0]
        raw = json.loads((ROOT / "data/locomo10.json").read_text())
        agents = []

        def factory(config, observer):
            agent = Agent()
            agents.append(agent)
            return agent

        with tempfile.TemporaryDirectory() as directory:
            result = run_manifest(
                ROOT / "data/locomo10.json",
                manifest,
                DEFAULT_CONFIG,
                output_dir=Path(directory) / "run",
                cache_root=Path(directory) / "cache",
                source_hashes={"wrapper": "test"},
                agent_factory=factory,
                scorer=score,
            )
            self.assertEqual(result["status"], "complete")
            events = [
                json.loads(line)
                for line in (Path(directory) / "run/events.jsonl")
                .read_text()
                .splitlines()
            ]
            results = [e["result"] for e in events if e["type"] == "question_result"]
            self.assertEqual(len(results), 204)
            self.assertEqual(
                [r["question_id"] for r in results[:2]],
                ["conv-50:qa:0", "conv-50:qa:1"],
            )
            self.assertEqual(results[0]["prediction"], "preserved")
            self.assertEqual(results[0]["raw_response"], '{"answer":"preserved"}')
            self.assertEqual(results[0]["qa"], raw[9]["qa"][0])
            self.assertEqual(
                agents[0].random_draws[0], random.Random("42:9:0").random()
            )
            expected = raw[9]["conversation"][conv["session_keys"][0]][0]
            self.assertEqual(
                agents[0].added[0][0],
                "Speaker " + expected["speaker"] + "says : " + expected["text"],
            )

    def test_live_calls_and_non_full_conditions_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = build_manifest(ROOT / "data/locomo10.json", "smoke")
            with self.assertRaises(PermissionError):
                run_manifest(
                    ROOT / "data/locomo10.json",
                    manifest,
                    DEFAULT_CONFIG,
                    output_dir=Path(directory) / "run",
                    cache_root=Path(directory) / "cache",
                    source_hashes={"wrapper": "test"},
                )
            with self.assertRaises(ValueError):
                run_manifest(
                    ROOT / "data/locomo10.json",
                    manifest,
                    DEFAULT_CONFIG,
                    condition="neither",
                    output_dir=Path(directory) / "run",
                    cache_root=Path(directory) / "cache",
                    source_hashes={"wrapper": "test"},
                    agent_factory=lambda **kw: Agent(),
                    scorer=score,
                )

    def test_cached_qa_reuses_verified_state_without_rebuilding(self):
        manifest = build_manifest(ROOT / "data/locomo10.json", "smoke")
        agents = []

        def factory(config, observer):
            agent = Agent()
            agents.append(agent)
            return agent

        with tempfile.TemporaryDirectory() as directory:
            args = dict(
                dataset_path=ROOT / "data/locomo10.json",
                manifest=manifest,
                config=DEFAULT_CONFIG,
                cache_root=Path(directory) / "cache",
                source_hashes={"wrapper": "test"},
                agent_factory=factory,
                scorer=score,
            )
            run_manifest(**args, output_dir=Path(directory) / "fresh")
            result = run_manifest(
                **args, output_dir=Path(directory) / "qa", execution_type="cached_qa"
            )
            self.assertEqual(result["status"], "complete")
            self.assertEqual(len(agents[0].added), 18)
            self.assertEqual(agents[1].added, [])
            self.assertEqual(len(agents[1].memory_system.memories), 18)

    def test_aborted_build_preserves_partial_state_and_provider_cost(self):
        manifest = build_manifest(ROOT / "data/locomo10.json", "smoke")

        def factory(config, observer):
            class BrokenAgent(Agent):
                def add_memory(self, content, time=None):
                    observer(
                        {
                            "stage": "metadata",
                            "usage": {"prompt_tokens": 100, "completion_tokens": 10},
                        }
                    )
                    if self.added:
                        raise RuntimeError("provider failed")
                    super().add_memory(content, time)

            return BrokenAgent()

        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            with self.assertRaises(RuntimeError):
                run_manifest(
                    ROOT / "data/locomo10.json",
                    manifest,
                    DEFAULT_CONFIG,
                    output_dir=run,
                    cache_root=Path(directory) / "cache",
                    source_hashes={"wrapper": "test"},
                    agent_factory=factory,
                    scorer=score,
                )
            self.assertEqual(
                json.loads((run / "summary.json").read_text())["status"], "incomplete"
            )
            partial = json.loads((run / "partial-memory.json").read_text())
            self.assertFalse(partial["complete"])
            self.assertEqual(len(partial["state"]["notes"]), 1)
            events = [
                json.loads(line)
                for line in (run / "events.jsonl").read_text().splitlines()
            ]
            self.assertEqual(
                [
                    e["usage"]["prompt_tokens"]
                    for e in events
                    if e["type"] == "generation"
                ],
                [100, 100],
            )


class BridgeTests(unittest.TestCase):
    def test_original_agent_constructor_uses_injected_controller_and_restores_module(
        self,
    ):
        from amem_repro.author import make_agent_factory

        calls = []
        original_controller = object()
        module = NS(LLMController=original_controller, MemoryNote=NS, FAILURES={})

        class MemorySystem:
            def __init__(self, **kwargs):
                self.llm_controller = module.LLMController(
                    kwargs["llm_backend"], kwargs["llm_model"]
                )
                self.kwargs = kwargs

        module.AgenticMemorySystem = MemorySystem

        def controller_factory(observer):
            controller = NS(observer_errors=[])
            calls.append(controller)
            return controller

        factory = make_agent_factory(
            ROOT, controller_factory=controller_factory, memory_module=module
        )
        agent = factory(config=DEFAULT_CONFIG, observer=lambda event: None)
        self.assertEqual(len(calls), 2)
        self.assertIs(agent.memory_system.llm_controller.llm, calls[0])
        self.assertIs(agent.retriever_llm.llm, calls[1])
        self.assertIs(module.LLMController, original_controller)
        self.assertEqual(agent.retrieve_k, 10)
        self.assertFalse(agent.memory_system.kwargs["refresh_index"])

    def test_bridge_has_no_implicit_live_client(self):
        from amem_repro.author import make_agent_factory

        with self.assertRaises(PermissionError):
            make_agent_factory(ROOT)


if __name__ == "__main__":
    unittest.main()
