"""Isolated strict-function compatibility boundary for the frozen A-MEM callers."""

from __future__ import annotations

import copy
import json
import os
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Callable

from .contracts import (
    ContractError,
    load_author_contracts,
    validate_arguments,
    validate_strict_schema,
)

MODEL = "deepseek-flash"
BASE_URL = "https://api.deepseek.com/beta"
DOCUMENTED_MODEL_VERSION = "DeepSeek-V4.1-Flash-1017"
_ATTEMPTS: ContextVar[list | None] = ContextVar("amem_attempts", default=None)


class AdapterError(ValueError):
    """The provider did not return the single unchanged requested output contract."""


def _mapping(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return vars(value)


def _invalid_constant(value):
    raise AdapterError("Non-finite JSON constant")


class DeepSeekController:
    """Drop-in get_completion seam. Construction never creates a client or reads credentials.

    Tests inject deterministic clients. Live construction must use the explicitly guarded factory.
    The observer is observational: its failure is retained without changing author output.
    """

    def __init__(
        self,
        client,
        *,
        observer: Callable[[dict], None] | None = None,
        stage: str | None = None,
    ):
        self.client = client
        self.model = MODEL
        self.observer = observer
        self.stage = stage
        self.observer_errors = []
        self.contracts = load_author_contracts()

    def get_completion(
        self, prompt: str, response_format: dict, temperature: float = 0.7
    ) -> str:
        matched = [
            name
            for name, contract in self.contracts.items()
            if contract == response_format
        ]
        if len(matched) != 1:
            raise ContractError(
                "Only the four unchanged frozen author contracts are supported"
            )
        stage = matched[0]
        if self.stage is not None and self.stage != stage:
            raise ContractError("Explicit stage does not match the author contract")
        if temperature not in ({0.5, 0.7} if stage == "answer" else {0.7}):
            raise ContractError("Temperature differs from frozen generation settings")
        contract = response_format["json_schema"]
        schema = contract["schema"]
        validate_strict_schema(schema)
        name = contract["name"]
        event = {
            "stage": stage,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "response_format": copy.deepcopy(response_format),
            "model": MODEL,
            "endpoint": BASE_URL + "/chat/completions",
            "documented_model_version": DOCUMENTED_MODEL_VERSION,
            "temperature": temperature,
            "max_tokens": 1000,
            "thinking": "disabled",
            "output": None,
            "usage": None,
            "system_fingerprint": None,
            "request_id": None,
            "error_type": None,
            "attempts": [],
        }
        token = _ATTEMPTS.set(event["attempts"])
        started = time.perf_counter()
        try:
            response = _mapping(
                self.client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You must respond with a JSON object.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": name,
                                "strict": True,
                                "parameters": copy.deepcopy(schema),
                            },
                        }
                    ],
                    tool_choice={"type": "function", "function": {"name": name}},
                    extra_body={"thinking": {"type": "disabled"}},
                    temperature=temperature,
                    max_tokens=1000,
                    stream=False,
                )
            )
            event["provider_response"] = copy.deepcopy(response)
            for field, source in [
                ("returned_model", "model"),
                ("usage", "usage"),
                ("system_fingerprint", "system_fingerprint"),
                ("request_id", "id"),
            ]:
                event[field] = copy.deepcopy(response.get(source))
            choices = response.get("choices")
            if not isinstance(choices, list) or len(choices) != 1:
                raise AdapterError("Expected exactly one completion choice")
            choice = _mapping(choices[0])
            if choice.get("finish_reason") != "tool_calls":
                raise AdapterError("Expected a completed strict function call")
            message = _mapping(choice.get("message") or {})
            calls = message.get("tool_calls")
            if not isinstance(calls, list) or len(calls) != 1:
                raise AdapterError("Expected exactly one function call")
            call = _mapping(calls[0])
            function = _mapping(call.get("function") or {})
            if call.get("type") != "function" or function.get("name") != name:
                raise AdapterError("Unexpected function name or type")
            arguments = function.get("arguments")
            event["output"] = arguments
            if not isinstance(arguments, str):
                raise AdapterError("Function arguments must be a JSON string")
            try:
                value = json.loads(arguments, parse_constant=_invalid_constant)
                validate_arguments(value, schema)
            except (ValueError, TypeError) as error:
                raise AdapterError(
                    "Function arguments violate the unchanged schema"
                ) from error
            return arguments
        except Exception as error:
            event["error_type"] = type(error).__name__
            raise
        finally:
            event["duration_seconds"] = time.perf_counter() - started
            _ATTEMPTS.reset(token)
            if self.observer is not None:
                try:
                    self.observer(copy.deepcopy(event))
                except Exception as error:
                    self.observer_errors.append(
                        {"stage": stage, "error_type": type(error).__name__}
                    )


def create_deepseek_controller(
    *, paid_authorized: bool = False, observer=None, http_transport=None
):
    """Explicit execution gate; implementation approval alone cannot create a live client."""
    if paid_authorized is not True:
        raise PermissionError("Separate paid execution authorization is required")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is required in the environment")
    import httpx
    from openai import OpenAI

    transport = _recording_transport(
        http_transport if http_transport is not None else httpx.HTTPTransport()
    )
    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL,
        timeout=120.0,
        max_retries=2,
        http_client=httpx.Client(transport=transport, timeout=120.0),
    )
    return DeepSeekController(client, observer=observer)


def _recording_transport(delegate):
    """Wrap SDK transport; retries remain entirely owned by the SDK."""
    import httpx

    class RecordingTransport(httpx.BaseTransport):
        def handle_request(self, request):
            attempts = _ATTEMPTS.get()
            attempt = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "attempt": len(attempts) + 1 if attempts is not None else None,
                "status_code": None,
                "usage": None,
                "error_type": None,
            }
            started = time.perf_counter()
            try:
                response = delegate.handle_request(request)
                attempt["status_code"] = response.status_code
                if response.status_code >= 400:
                    attempt["error_type"] = "HTTPStatusError"
                response.read()
                try:
                    body = response.json()
                    if isinstance(body, dict):
                        for key in ("usage", "model", "system_fingerprint", "id"):
                            if key in body:
                                attempt[key] = copy.deepcopy(body[key])
                except (ValueError, UnicodeError):
                    pass
                return response
            except Exception as error:
                attempt["error_type"] = type(error).__name__
                raise
            finally:
                attempt["duration_seconds"] = time.perf_counter() - started
                if attempts is not None:
                    attempts.append(attempt)

        def close(self):
            delegate.close()

    return RecordingTransport()
