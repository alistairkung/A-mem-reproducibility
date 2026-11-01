"""Exercise the real SDK retry loop against a durable permit, without sockets."""

import json
from unittest.mock import patch

import httpx
import pytest

from amem_repro.adapter import create_deepseek_controller, AdapterError
from amem_repro.budget import PhasePermit, BudgetStop
from amem_repro.contracts import load_author_contracts


def approval(cap=2, logical=44):
    binding = {
        **{name: "a" * 64 for name in (
            "manifest_sha256", "config_sha256", "source_sha256", "preflight_sha256"
        )},
        "condition": "full", "repetition": 0, "population": "smoke",
        "model": "deepseek-flash",
        "endpoint": "https://api.deepseek.com/beta/chat/completions",
    }
    return {
        "approval_id": "test-only", "approved": True, "approved_by": "offline test",
        "approved_at": "2026-11-01T00:00:00+00:00", "phase": "compatibility",
        "run_id": "test-run", "binding": binding,
        "limits": {"phase_usd": cap, "max_logical_calls": logical, "max_attempts": logical * 3},
        "pricing": {"pricing_id": "test-peak", "input_per_million": 0.30,
                    "output_per_million": 1.20, "max_context_tokens": 1048576,
                    "max_output_tokens": 1000},
    }


def response(arguments='{"answer":"saved"}'):
    return {
        "id": "offline-id", "model": "deepseek-flash",
        "choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant",
            "tool_calls": [{"id": "call-1", "type": "function", "function": {
                "name": "response", "arguments": arguments}}]}}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
    }


def controller(permit, handler, events):
    with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "offline-placeholder"}, clear=True):
        return create_deepseek_controller(
            paid_authorized=True, phase_permit=permit,
            http_transport=httpx.MockTransport(handler), observer=events.append,
        )


def test_attempt_is_reserved_before_transmission_and_settled_once(tmp_path):
    auth = approval()
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    requests, events = [], []

    def handler(request):
        assert permit.summary()["physical_attempts"] == len(requests) + 1
        assert permit.summary()["unknown_attempts"] == 1
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=response())

    c = controller(permit, handler, events)
    try:
        assert c.get_completion("same prompt", load_author_contracts()["answer"]) == '{"answer":"saved"}'
    finally:
        c.client.close()
    assert len(requests) == 1
    assert permit.summary()["charged_or_reserved_microusd"] == 12
    assert events[0]["attempts"][0]["budget_attempt_id"] == 1
    assert events[0]["attempts"][0]["request_body"] == requests[0]
    assert "offline-placeholder" not in json.dumps(events)


def test_retry_cannot_transmit_when_next_reservation_exceeds_cap(tmp_path):
    auth = approval(cap=0.40)
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    requests, events = [], []

    def handler(request):
        requests.append(request)
        return httpx.Response(429, json={"error": {"message": "rate limit"}},
                              headers={"retry-after-ms": "1"})

    c = controller(permit, handler, events)
    try:
        with pytest.raises(BudgetStop):
            c.get_completion("same prompt", load_author_contracts()["answer"])
    finally:
        c.client.close()
    assert len(requests) == 1
    assert permit.summary()["charged_or_reserved_microusd"] == 315773
    assert events[0]["error_type"] == "BudgetStop"
    assert len(events[0]["attempts"]) == permit.summary()["physical_attempts"] == 1


def test_schema_failure_stops_following_calls_without_semantic_retry(tmp_path):
    auth = approval()
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    requests, events = [], []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=response('{"answer":17}'))

    c = controller(permit, handler, events)
    try:
        with pytest.raises(AdapterError):
            c.get_completion("prompt", load_author_contracts()["answer"])
        with pytest.raises(BudgetStop):
            c.get_completion("prompt", load_author_contracts()["answer"])
    finally:
        c.client.close()
    assert len(requests) == 1
    assert permit.summary()["halted"]


def test_untrusted_usage_stop_preserves_the_received_function_arguments(tmp_path):
    auth = approval()
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    events = []
    received = response(' {"answer": "preserve these original bytes"} ')
    received["usage"]["prompt_tokens"] = -1
    c = controller(permit, lambda request: httpx.Response(
        200, json=received, headers={"sensitive-test-header": "never-record"}), events)
    try:
        with pytest.raises(BudgetStop, match="Untrusted usage"):
            c.get_completion("same prompt", load_author_contracts()["answer"])
    finally:
        c.client.close()
    assert permit.summary()["charged_or_reserved_microusd"] == 315773
    attempt = events[0]["attempts"][0]
    assert attempt["status_code"] == 200
    assert attempt["response_body"] == received
    assert attempt["response_body"]["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] == ' {"answer": "preserve these original bytes"} '
    assert "sensitive-test-header" not in json.dumps(events)
    assert "never-record" not in json.dumps(events)


def test_error_payload_redacts_echoed_credentials_but_retains_diagnostics(tmp_path):
    auth = approval()
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    events = []

    def handler(request):
        return httpx.Response(401, json={
            "error": {"type": "authentication_error", "message": "invalid offline-placeholder",
                      "nested": [{"api_key": "offline-placeholder", "detail": "keep this",
                                  "offline-placeholder": "provider echoed a credential as a field name"}]},
        })

    c = controller(permit, handler, events)
    try:
        with pytest.raises(Exception):
            c.get_completion("same prompt", load_author_contracts()["answer"])
    finally:
        c.client.close()
    serialized = json.dumps(events)
    assert "offline-placeholder" not in serialized
    assert "authentication_error" in serialized
    assert "keep this" in serialized
    assert events[0]["attempts"][0]["status_code"] == 401
    from amem_repro.config import reject_credentials
    reject_credentials(events)


def test_serialized_request_is_observationally_redacted_without_changing_parser_output(tmp_path):
    auth = approval()
    permit = PhasePermit(auth, tmp_path / "budget.sqlite", auth["binding"])
    events, prompts = [], []
    arguments = '{"answer":"offline-placeholder stays in the returned original"}'

    def handler(request):
        prompts.append(json.loads(request.content)["messages"][1]["content"])
        return httpx.Response(200, json=response(arguments))

    c = controller(permit, handler, events)
    try:
        result = c.get_completion("original offline-placeholder prompt", load_author_contracts()["answer"])
    finally:
        c.client.close()
    assert prompts == ["original offline-placeholder prompt"]
    assert result == arguments
    assert events[0]["attempts"][0]["request_body"]["messages"][1]["content"] == "original <redacted> prompt"
    assert "offline-placeholder" not in json.dumps(events)
