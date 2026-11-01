"""Characterize the frozen author parser, not a proposed provider-policy implementation."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from amem_repro.artifacts import snapshot_memory
from amem_repro.author import make_agent_factory
from amem_repro.config import load_config
from amem_repro.config import verified_author_bytes
from amem_repro.contracts import ContractError, load_author_contracts, validate_arguments
from amem_repro.scoring import AuthorScorer
from test_foundation import original_memory_module
from test_scoring import dependencies

ROOT = Path(__file__).resolve().parents[1]


def author_module():
    verified_author_bytes(ROOT, "memory_layer.py")
    module = original_memory_module()
    module.print = lambda *args, **kwargs: None
    return module


@pytest.mark.parametrize("value,expected", [
    (2, 2), (2.0, 2), ("2", 2), (" 2 ", 2), ("02", 2), ("٢", 2),
    (True, None), (False, None), (1.5, None), ("2.0", None), ("2e0", None),
    ("+2", None), ("-1", None), ("", None), (None, None), (-1, -1),
])
def test_original_as_index_domains(value, expected):
    assert author_module().as_index(value) == expected


def test_isdigit_does_not_guarantee_original_conversion_succeeds():
    # Python considers this a digit, but int() does not accept it.
    assert "²".isdigit()
    with pytest.raises(ValueError):
        author_module().as_index("²")


def evolve(connections, *, positive=True, actions=None, counter=0, controller_factory=None):
    module = author_module()
    decision = {
        "should_evolve": positive,
        "actions": ["strengthen", "update_neighbor"] if actions is None else actions,
        "suggested_connections": copy.deepcopy(connections),
        "tags_to_update": ["new-tag"],
        "new_context_neighborhood": [f"updated-{i}" for i in range(4)],
        "new_tags_neighborhood": [[f"tag-{i}"] for i in range(4)],
    }
    raw = json.dumps(decision)
    calls = []
    controller = controller_factory(raw) if controller_factory else None

    def completion(prompt, **kwargs):
        calls.append((prompt, kwargs))
        return controller.get_completion(prompt, **kwargs) if controller else raw

    module.LLMController = lambda *args, **kwargs: NS(llm=NS(get_completion=completion))
    system = module.AgenticMemorySystem()
    system.evo_cnt = counter
    for i in range(4):
        note = NS(id=f"old-{i}", content=f"old content {i}", context="old-context",
                  tags=["old-tag"], keywords=["keyword"], links=[], timestamp="fixed")
        system.memories[note.id] = note
    system.retriever.add_documents([module.note_document(n) for n in system.memories.values()])
    system.add_note("new content", time="fixed", id="new", keywords=["new"],
                    context="new-context", tags=["initial-tag"], category="fixture")
    state = snapshot_memory(system)
    # Comparison views only; no saved experimental artifact is changed.
    for note in state["notes"]:
        note["attributes"].pop("last_accessed", None)
    return system, state, dict(module.FAILURES), calls


@pytest.mark.parametrize("actions", [[], ["strengthen"], ["update_neighbor"],
                                     ["strengthen", "update_neighbor"]])
@pytest.mark.parametrize("positive", [False, True])
@pytest.mark.parametrize("counter", [0, 99])
def test_strings_and_integers_have_identical_original_state_and_retrieval(actions, positive, counter):
    a, state_a, failures_a, calls_a = evolve(["2", "3"], actions=actions, positive=positive, counter=counter)
    b, state_b, failures_b, calls_b = evolve([2, 3], actions=actions, positive=positive, counter=counter)
    assert state_a == state_b
    assert failures_a == failures_b
    assert calls_a == calls_b
    assert a.find_related_memories_raw("query", k=10) == b.find_related_memories_raw("query", k=10)
    assert a.evo_cnt == counter + int(positive)
    if positive and "strengthen" in actions:
        assert a.memories["new"].links == [2, 3]


def test_original_filter_retains_order_duplicates_and_invalid_link_accounting():
    _, strings, string_failures, _ = evolve(["2", "99", "2", "3"])
    system, integers, integer_failures, _ = evolve([2, 99, 2, 3])
    assert strings == integers
    assert system.memories["new"].links == [2, 2, 3]
    assert string_failures == integer_failures == {"invalid_link": 1}


def test_schema_invalid_strings_remain_invalid_even_when_original_parser_accepts_them():
    schema = load_author_contracts(ROOT)["shared_decision"]["json_schema"]["schema"]
    for value in ["2", True, "2.0", "²"]:
        with pytest.raises(ContractError):
            validate_arguments([value], schema["properties"]["suggested_connections"])
    validate_arguments([2, 2.0], schema["properties"]["suggested_connections"])


def test_global_array_or_boolean_coercion_would_change_author_behavior():
    module = author_module()
    raw = module.MemoryNote(content="note", keywords="ab", context="context", tags=["tag"])
    cast = module.MemoryNote(content="note", keywords=["ab"], context="context", tags=["tag"])
    assert module.note_document(raw) != module.note_document(cast)
    tolerated_context = module.MemoryNote(content="note", keywords=["word"],
                                         context=["first", "second"], tags=["tag"])
    assert tolerated_context.context == "first second"
    raw_system, _, _, _ = evolve(["2", "3"], positive="false")
    coerced_system, _, _, _ = evolve([2, 3], positive=False)
    assert raw_system.memories["new"].links == [2, 3]
    assert coerced_system.memories["new"].links == []
    assert raw_system.evo_cnt == coerced_system.evo_cnt == 0


def test_query_parser_returns_wrong_typed_field_without_normalizing_it():
    module = author_module()
    controller = NS(get_completion=lambda *args, **kwargs: '{"keywords":["alpha","beta"]}',
                    observer_errors=[])
    factory = make_agent_factory(ROOT, memory_module=module,
                                 controller_factory=lambda observer: controller)
    agent = factory(config=load_config(), observer=lambda event: None)
    assert agent.generate_query_llm("Which words?") == ["alpha", "beta"]


def test_answer_zero_stringification_would_change_original_scoring():
    scorer = AuthorScorer(ROOT, dependencies=dependencies())
    qa = scorer.qa({"question": "Which number?", "answer": "0", "category": 1})
    _, raw = scorer.score(0, qa)
    _, coerced = scorer.score("0", qa)
    assert raw["f1"] == raw["exact_match"] == 0
    assert coerced["f1"] == coerced["exact_match"] == 1
