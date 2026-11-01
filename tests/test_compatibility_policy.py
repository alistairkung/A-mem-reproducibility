"""Approved BLK-007 policy through the provider and experiment interfaces only."""

import copy
import hashlib
import json

import pytest

from amem_repro.adapter import DeepSeekController, AdapterError
from amem_repro.config import fingerprint
from amem_repro.contracts import ContractError, load_author_contracts, validate_arguments
from test_adapter import Client, completion

POLICY = "canonical-index-strings-v1"
STRICT = "strict-original-v1"


def decision(connections=None):
    return {
        "should_evolve": True,
        "actions": ["strengthen", "update_neighbor"],
        "suggested_connections": ["2", "3"] if connections is None else connections,
        "tags_to_update": ["new"],
        "new_context_neighborhood": ["context"],
        "new_tags_neighborhood": [["tag"]],
    }


def test_validation_copy_admits_only_the_approved_field_and_returns_original_bytes():
    contract = load_author_contracts()["shared_decision"]
    value = decision()
    raw = " \n" + json.dumps(value, indent=2) + "\n "
    client, events = Client(completion(raw)), []
    original_response = copy.deepcopy(client.response)
    with pytest.raises(ContractError):
        validate_arguments(value, contract["json_schema"]["schema"])

    result = DeepSeekController(client, observer=events.append,
                                provider_contract_policy=POLICY).get_completion("unchanged", contract)
    assert result == raw
    assert client.response == original_response
    assert len(client.requests) == 1
    assert client.requests[0]["tools"][0]["function"]["parameters"] == contract["json_schema"]["schema"]
    assert client.requests[0]["tools"][0]["function"]["strict"] is True
    event = events[0]
    assert event["provider_contract_policy"] == POLICY
    assert event["raw_schema_valid"] is False
    assert event["validation_copy_schema_valid"] is True
    audit = event["compatibility_deviation"]
    assert audit["provider_contract_policy"] == POLICY
    assert audit["affected_field"] == "$.suggested_connections"
    assert audit["raw_contract_violation"]["expected"] == "integer"
    assert audit["raw_contract_violation"]["observed"] == "string"
    assert audit["transformations"] == [
        {"path": "$.suggested_connections[0]", "original": "2", "validation_copy": 2},
        {"path": "$.suggested_connections[1]", "original": "3", "validation_copy": 3},
    ]
    assert audit["original_arguments_sha256"] == hashlib.sha256(raw.encode()).hexdigest()
    assert audit["returned_arguments_sha256"] == audit["original_arguments_sha256"]
    assert audit["original_value_sha256"] == fingerprint(value)
    assert audit["validation_copy_sha256"] == fingerprint({**value, "suggested_connections": [2, 3]})
    assert audit["algorithm_input_modified"] is False
    assert audit["validation_copy_only"] is True
    with pytest.raises(ContractError):
        validate_arguments(value, contract["json_schema"]["schema"])


@pytest.mark.parametrize("connections", [
    ["0"], ["2", 3, "99999", "2", 2.0], [], [0, 2, 2.0, -1],
])
def test_valid_mixed_and_unshown_values_are_not_filtered_or_rewritten(connections):
    raw = json.dumps(decision(connections))
    events = []
    out = DeepSeekController(Client(completion(raw)), observer=events.append,
                             provider_contract_policy=POLICY).get_completion(
        "same", load_author_contracts()["shared_decision"])
    assert out == raw
    changes = (events[0]["compatibility_deviation"] or {}).get("transformations", [])
    assert len(changes) == sum(type(value) is str for value in connections)
    assert events[0]["raw_schema_valid"] is (not changes)


@pytest.mark.parametrize("bad", [
    "", " 2", "2 ", "02", "+2", "-2", "2.0", "2e0", "0x2", "٢", "²",
    True, False, None, 1.5, {}, [], float("nan"), "1" * 5000,
])
def test_malformed_strings_booleans_and_bad_mixed_items_reject_once(bad):
    raw = json.dumps(decision(["2", bad]))
    client, events = Client(completion(raw)), []
    with pytest.raises(AdapterError):
        DeepSeekController(client, observer=events.append, provider_contract_policy=POLICY).get_completion(
            "same", load_author_contracts()["shared_decision"])
    assert len(client.requests) == 1
    assert events[0]["compatibility_deviation"] is None
    assert events[0]["output"] == raw


@pytest.mark.parametrize("stage,value", [
    ("metadata", {"keywords": "word", "context": "context", "tags": ["tag"]}),
    ("metadata", {"keywords": ["word"], "context": ["context"], "tags": ["tag"]}),
    ("metadata", {"keywords": ["word"], "context": "context", "tags": [1]}),
    ("query_keywords", {"keywords": ["word"]}),
    ("query_keywords", {"keywords": None}),
    ("answer", {"answer": 0}), ("answer", {"answer": False}),
    ("answer", {"answer": ["word"]}),
    ("shared_decision", {**decision(), "should_evolve": "false"}),
    ("shared_decision", {**decision(), "actions": "strengthen"}),
    ("shared_decision", {**decision(), "tags_to_update": "tag"}),
    ("shared_decision", {**decision(), "new_context_neighborhood": [1]}),
    ("shared_decision", {**decision(), "new_tags_neighborhood": ["tag"]}),
    ("shared_decision", {k: v for k, v in decision().items() if k != "new_tags_neighborhood"}),
    ("shared_decision", {**decision(), "extra": "field"}),
    ("shared_decision", {**decision(), "suggested_connections": "2"}),
])
def test_every_other_schema_field_remains_strict(stage, value):
    raw = json.dumps(value)
    client = Client(completion(raw))
    with pytest.raises(AdapterError):
        DeepSeekController(client, provider_contract_policy=POLICY).get_completion(
            "same", load_author_contracts()[stage])
    assert len(client.requests) == 1


def test_strict_is_default_and_unknown_policies_cannot_enable_admission():
    client = Client(completion(json.dumps(decision())))
    with pytest.raises(AdapterError):
        DeepSeekController(client).get_completion("same", load_author_contracts()["shared_decision"])
    for policy in ["", "automatic", None, True, {}]:
        with pytest.raises(ValueError):
            DeepSeekController(client, provider_contract_policy=policy)


def test_incomplete_or_wrong_tool_output_is_not_salvaged_by_policy():
    for change in ("length", "wrong_name"):
        response = completion(json.dumps(decision()))
        if change == "length":
            response["choices"][0]["finish_reason"] = "length"
        else:
            response["choices"][0]["message"]["tool_calls"][0]["function"]["name"] = "wrong"
        client = Client(response)
        with pytest.raises(AdapterError):
            DeepSeekController(client, provider_contract_policy=POLICY).get_completion(
                "same", load_author_contracts()["shared_decision"])
        assert len(client.requests) == 1


def test_admitted_deviation_degrades_run_and_survives_cache_reuse(tmp_path):
    from pathlib import Path
    from amem_repro.artifacts import CacheRejected
    from amem_repro.config import load_config
    from amem_repro.manifests import build_manifest
    from amem_repro.runner import run_manifest
    from test_runner import Agent, score

    root = Path(__file__).resolve().parents[1]
    contract = load_author_contracts()["shared_decision"]

    def factory(config, observer):
        agent = Agent()
        add = agent.add_memory
        controller = DeepSeekController(Client(completion(json.dumps(decision()))),
                                        observer=observer, provider_contract_policy=POLICY)

        def measured_add(*args, **kwargs):
            if not agent.added:
                controller.get_completion("unchanged", contract)
            return add(*args, **kwargs)

        agent.add_memory = measured_add
        return agent

    args = dict(dataset_path=root / "data/locomo10.json",
                manifest=build_manifest(root / "data/locomo10.json", "smoke"),
                config=load_config(), cache_root=tmp_path / "cache",
                source_hashes={"wrapper": "same"}, agent_factory=factory, scorer=score,
                provider_contract_policy=POLICY)
    result = run_manifest(**args, output_dir=tmp_path / "fresh")
    assert result["status"] == "degraded"
    assert result["provider_contract_policy"] == POLICY
    assert result["provider_contract_deviation_count"] == 1
    assert result["validation_copy_transformed_item_count"] == 2
    assert result["completed_questions"] == 4
    assert json.loads((tmp_path / "fresh/run.json").read_text())["provider_contract_policy"] == POLICY
    events = [json.loads(line) for line in (tmp_path / "fresh/events.jsonl").read_text().splitlines()]
    assert events[0]["provider_contract_policy"] == POLICY
    failure = next(e for e in events if e.get("kind") == "provider_contract_deviation")
    assert failure["compatibility_deviation"]["affected_field"] == "$.suggested_connections"
    assert all(e["result"]["prediction"] == "preserved"
               and e["result"]["provider_contract_policy"] == POLICY
               for e in events if e["type"] == "question_result")
    identity = json.loads(next((tmp_path / "cache").glob("*/identity.json")).read_text())
    assert identity["provider_contract_policy"] == POLICY
    reused = run_manifest(**args, output_dir=tmp_path / "cached", execution_type="cached_qa")
    assert reused["status"] == "degraded"
    assert reused["provider_contract_deviation_count"] == 0
    assert reused["inherited_provider_contract_deviation_count"] == 1
    with pytest.raises(CacheRejected):
        run_manifest(**{**args, "provider_contract_policy": STRICT},
                     output_dir=tmp_path / "wrong-policy", execution_type="cached_qa")


def test_sdk_policy_is_bound_to_approval_and_never_enters_provider_payload(tmp_path):
    import httpx
    from unittest.mock import patch
    from amem_repro.adapter import create_deepseek_controller
    from amem_repro.budget import PhasePermit
    from test_adapter_budget import approval

    auth = approval(logical=1)
    auth["binding"]["provider_contract_policy"] = POLICY
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    requests, events = [], []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=completion(json.dumps(decision())))

    with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "offline-placeholder"}, clear=True):
        with pytest.raises(ValueError, match="policy"):
            create_deepseek_controller(paid_authorized=True, phase_permit=permit,
                                       http_transport=httpx.MockTransport(handler))
        controller = create_deepseek_controller(
            paid_authorized=True, phase_permit=permit, observer=events.append,
            provider_contract_policy=POLICY, http_transport=httpx.MockTransport(handler))
        try:
            controller.get_completion("unchanged", load_author_contracts()["shared_decision"])
        finally:
            controller.client.close()
    assert len(requests) == permit.summary()["physical_attempts"] == 1
    assert permit.summary()["halted"] is None
    assert "provider_contract_policy" not in requests[0]
    assert requests[0]["tools"][0]["function"]["parameters"]["properties"]["suggested_connections"]["items"] == {"type": "integer"}
    assert events[0]["compatibility_deviation"]["provider_contract_policy"] == POLICY


def test_unapproved_phase_plan_explicitly_binds_selected_policy(tmp_path):
    from pathlib import Path
    from unittest.mock import patch
    from amem_repro import phases

    root = Path(__file__).resolve().parents[1]
    receipt = {"assets": {"tokenizer_limitation": "offline test only"}}
    with patch.object(phases, "_verified_receipt", return_value={"test": "source"}):
        plan = phases.plan_phase("compatibility", receipt, tmp_path / "assets", root=root,
                                 provider_contract_policy=POLICY)
    assert plan["approved"] is False
    assert plan["binding"]["provider_contract_policy"] == POLICY
    assert plan["limits"]["max_logical_calls"] == 44
    assert plan["limits"]["max_attempts"] == 132


def test_pilot_cannot_reuse_compatibility_from_another_provider_policy(tmp_path):
    from pathlib import Path
    from unittest.mock import patch
    from amem_repro import phases

    root = Path(__file__).resolve().parents[1]
    receipt = {"assets": {"tokenizer_limitation": "offline test only"}}
    with patch.object(phases, "_verified_receipt", return_value={"test": "source"}):
        _, _, _, strict_binding = phases._phase_inputs("compatibility", receipt, tmp_path, root)
        previous = {"phase": "compatibility", "binding": strict_binding}
        with patch.object(phases, "_verified_phase", return_value=previous):
            with pytest.raises(ValueError, match="provenance"):
                phases._phase_inputs("pilot", receipt, tmp_path, root, "receipt.json",
                                     provider_contract_policy=POLICY)


@pytest.mark.parametrize("current_policy,credited", [(STRICT, False), (POLICY, True)])
def test_forecast_never_credits_a_pilot_under_another_policy(tmp_path, current_policy, credited):
    from pathlib import Path
    from unittest.mock import patch
    from amem_repro import phases
    from amem_repro.config import load_config
    from amem_repro.manifests import expand_manifest

    root = Path(__file__).resolve().parents[1]
    config = load_config(root / "config/study.json")
    manifest = expand_manifest(root / "data/locomo10.json", json.loads((root / "manifests/pilot.json").read_text()))
    pilot = {"phase": "pilot", "binding": {
        "source_sha256": fingerprint({"test": "same"}), "config_sha256": fingerprint(config),
        "manifest_sha256": fingerprint(manifest), "condition": "full", "repetition": 0,
        "provider_contract_policy": POLICY,
    }}
    (tmp_path / "events.jsonl").write_text("\n".join(json.dumps(event) for event in [
        {"type": "generation", "stage": "metadata"},
        # Forecast reads generation records only, never scoring or predictions.
        {"type": "question_result", "result": "ignored"},
    ]))
    with patch.object(phases, "_verified_phase", return_value=pilot), \
         patch.object(phases, "source_fingerprint", return_value={"test": "same"}), \
         patch("amem_repro.budget.ledger_summary", return_value={}), \
         patch("amem_repro.forecast.forecast_scope", return_value={}) as forecast:
        result = phases.forecast_pilot(tmp_path / "phase.json", root=root,
                                       provider_contract_policy=current_policy)
    assert forecast.call_args.kwargs["pilot_reusable"] is credited
    assert forecast.call_args.args[0] == [{"type": "generation", "stage": "metadata"}]
    assert result["provider_contract_policy"] == current_policy


@pytest.mark.parametrize("positive", [False, True])
@pytest.mark.parametrize("counter", [0, 99])
@pytest.mark.parametrize("actions", [[], ["strengthen"], ["update_neighbor"],
                                     ["strengthen", "update_neighbor"]])
def test_adapter_raw_strings_preserve_original_parser_state_retrieval_and_counter(positive, counter, actions):
    from test_type_compatibility_characterization import evolve

    events = []

    def supplied(raw):
        return DeepSeekController(Client(completion(raw)), observer=events.append,
                                  provider_contract_policy=POLICY)

    def integer_control(raw):
        return DeepSeekController(Client(completion(raw)))

    options = dict(positive=positive, counter=counter, actions=actions)
    a, state_a, failures_a, calls_a = evolve(["2", 99, "2", "3"], controller_factory=supplied, **options)
    b, state_b, failures_b, calls_b = evolve([2, 99, 2, 3], controller_factory=integer_control, **options)
    assert state_a == state_b
    assert failures_a == failures_b
    assert calls_a == calls_b
    assert a.find_related_memories_raw("query", k=10) == b.find_related_memories_raw("query", k=10)
    assert a.evo_cnt == b.evo_cnt == counter + int(positive)
    assert json.loads(events[0]["output"])["suggested_connections"] == ["2", 99, "2", "3"]
    assert events[0]["compatibility_deviation"]["algorithm_input_modified"] is False
    if positive and "strengthen" in actions:
        assert a.memories["new"].links == [2, 2, 3]
        assert failures_a == {"invalid_link": 1}


def test_saved_result_exports_keep_provider_policy_distinct_from_scoring_policy(tmp_path):
    from amem_repro.reporting import export_experiments, write_tables
    from amem_repro.scoring import CORRECTED
    from test_reporting import FakeClient, ReportingTests

    views = ReportingTests().views()
    views[CORRECTED]["individual_results"][0]["provider_contract_policy"] = POLICY
    metadata = {"run_id": "unit", "condition": "full", "population": "smoke",
                "manifest_sha256": "a" * 64, "repetition": 0,
                "provider_contract_policy": POLICY}
    client = FakeClient()
    export_experiments(views, client=client, export_authorized=True,
                       evaluation_factory=lambda **kwargs: kwargs, metadata=metadata)
    assert client.runs[0]["metadata"]["experiment_identity"]["provider_contract_policy"] == POLICY
    assert client.runs[0]["metadata"]["scoring_policy"] == CORRECTED
    mismatched = FakeClient()
    with pytest.raises(ValueError, match="policy"):
        export_experiments(views, client=mismatched, export_authorized=True,
                           evaluation_factory=lambda **kwargs: kwargs,
                           metadata={**metadata, "provider_contract_policy": STRICT})
    assert mismatched.runs == []
    write_tables(views, tmp_path)
    assert "provider_contract_policy" in (tmp_path / "question_metrics.csv").read_text()
    assert POLICY in (tmp_path / "question_metrics.csv").read_text()
