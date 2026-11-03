"""Isolated strict-function compatibility boundary for the frozen A-MEM callers."""

from __future__ import annotations

import copy
import base64
import hashlib
import json
import os
import re
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
from .config import (
    reject_credentials, fingerprint, validate_provider_policy,
    STRICT_PROVIDER_POLICY, INDEX_STRING_POLICY,
    stage_output_limits,
    validate_config,
)

MODEL = "deepseek-flash"
BASE_URL = "https://api.deepseek.com/beta"
DOCUMENTED_MODEL_VERSION = "DeepSeek-V4.1-Flash-1017"
_ATTEMPTS: ContextVar[list | None] = ContextVar("amem_attempts", default=None)
_LOGICAL: ContextVar[int | None] = ContextVar("amem_logical", default=None)


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


def _validation_copy_deviation(value, schema, stage, policy, arguments):
    """Validate a temporary view; original arguments still go to the author parser."""
    try:
        validate_arguments(value, schema)
        return None
    except ContractError as raw_error:
        if (policy != INDEX_STRING_POLICY or stage != "shared_decision"
                or type(value) is not dict
                or type(value.get("suggested_connections")) is not list):
            raise
        shadow = copy.deepcopy(value)
        changes = []
        for index, item in enumerate(shadow["suggested_connections"]):
            if type(item) is str:
                # Deliberately narrower than str.isdigit()/as_index: canonical
                # unsigned ASCII decimals only, with no padding or whitespace.
                if re.fullmatch(r"0|[1-9][0-9]*", item, flags=re.ASCII) is None:
                    raise raw_error
                try:
                    converted = int(item)
                except ValueError:
                    raise raw_error from None
                shadow["suggested_connections"][index] = converted
                changes.append({"path": f"$.suggested_connections[{index}]",
                                "original": item, "validation_copy": converted})
        if not changes:
            raise
        # Every other field/item, required key and extra-key restriction remains strict.
        validate_arguments(shadow, schema)
        original_hash = hashlib.sha256(arguments.encode("utf-8")).hexdigest()
        return {
            "provider_contract_policy": policy,
            "affected_field": "$.suggested_connections",
            "raw_contract_violation": {
                "kind": "schema_type_violation", "expected": "integer", "observed": "string",
                "paths": [change["path"] for change in changes],
            },
            "raw_schema_valid": False,
            "validation_copy_schema_valid": True,
            "transformations": changes,
            "original_arguments_sha256": original_hash,
            "returned_arguments_sha256": original_hash,
            "original_value_sha256": fingerprint(value),
            "validation_copy_sha256": fingerprint(shadow),
            "hash_encoding": "arguments:utf8; values:canonical-json-sha256",
            "validation_copy_only": True,
            "algorithm_input_modified": False,
        }


def _observed_payload(value, credential=None):
    """Redact diagnostics only; provider values returned to author parsers are untouched."""
    if isinstance(value, dict):
        observed = {}
        for key, child in value.items():
            try:
                reject_credentials({key: None})
            except ValueError:
                observed["<redacted-field>"] = "<redacted>"
            else:
                safe_key = key.replace(credential, "<redacted>") if isinstance(key, str) and credential else key
                observed[safe_key] = _observed_payload(child, credential)
        return observed
    if isinstance(value, (list, tuple)):
        return [_observed_payload(item, credential) for item in value]
    if isinstance(value, str) and credential:
        return value.replace(credential, "<redacted>")
    return copy.deepcopy(value)


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
        phase_permit=None,
        provider_contract_policy=STRICT_PROVIDER_POLICY,
        generation_config=None,
    ):
        validate_provider_policy(provider_contract_policy)
        if generation_config is not None:
            validate_config(generation_config)
        self.output_limits = stage_output_limits(generation_config)
        self.client = client
        self.model = MODEL
        self.observer = observer
        self.stage = stage
        self.phase_permit = phase_permit
        self.provider_contract_policy = provider_contract_policy
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
        output_limit = self.output_limits[stage]
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
            "max_tokens": output_limit,
            "thinking": "disabled",
            "output": None,
            "usage": None,
            "system_fingerprint": None,
            "request_id": None,
            "error_type": None,
            "attempts": [],
            "provider_contract_policy": self.provider_contract_policy,
            "raw_schema_valid": None,
            "validation_copy_schema_valid": None,
            "compatibility_deviation": None,
        }
        token = _ATTEMPTS.set(event["attempts"])
        logical_token = None
        started = time.perf_counter()
        try:
            if self.phase_permit is not None:
                logical_id = self.phase_permit.start_logical(stage)
                event["budget_logical_id"] = logical_id
                logical_token = _LOGICAL.set(logical_id)
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
                    max_tokens=output_limit,
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
                event["raw_schema_valid"] = False
                deviation = _validation_copy_deviation(
                    value, schema, stage, self.provider_contract_policy, arguments
                )
                event["raw_schema_valid"] = deviation is None
                event["validation_copy_schema_valid"] = True if deviation else None
                event["compatibility_deviation"] = deviation
            except (ValueError, TypeError) as error:
                raise AdapterError(
                    "Function arguments violate the unchanged schema"
                ) from error
            return arguments
        except BaseException as error:
            event["error_type"] = type(error).__name__
            if self.phase_permit is not None:
                self.phase_permit.stop("provider_contract_or_transport_failure")
            raise
        finally:
            event["duration_seconds"] = time.perf_counter() - started
            if logical_token is not None:
                _LOGICAL.reset(logical_token)
            _ATTEMPTS.reset(token)
            if self.observer is not None:
                try:
                    self.observer(_observed_payload(event, getattr(self.client, "api_key", None)))
                except Exception as error:
                    self.observer_errors.append(
                        {"stage": stage, "error_type": type(error).__name__}
                    )


def create_deepseek_controller(
    *, paid_authorized: bool = False, observer=None, http_transport=None,
    phase_permit=None,
    provider_contract_policy=STRICT_PROVIDER_POLICY,
    generation_config=None,
):
    """Explicit execution gate; implementation approval alone cannot create a live client."""
    if paid_authorized is not True:
        raise PermissionError("Separate paid execution authorization is required")
    validate_provider_policy(provider_contract_policy)
    import httpx

    # The old MockTransport seam remains useful for offline SDK contracts. Real
    # transmissions additionally require a claimed durable phase, never a Boolean.
    if phase_permit is None and not isinstance(http_transport, httpx.MockTransport):
        raise NotImplementedError(
            "T5 live execution requires a provenance-bound spending permit"
        )
    if phase_permit is not None:
        from .budget import PhasePermit

        if not isinstance(phase_permit, PhasePermit):
            raise TypeError("A durable PhasePermit is required")
        if phase_permit.binding.get("provider_contract_policy", STRICT_PROVIDER_POLICY) != provider_contract_policy:
            raise ValueError("Provider-contract policy differs from phase approval")
        phase_permit.check_binding(phase_permit.binding)
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is required in the environment")
    from openai import OpenAI

    transport = _recording_transport(
        http_transport if http_transport is not None else httpx.HTTPTransport(retries=0),
        phase_permit,
        provider_contract_policy,
    )
    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL,
        timeout=120.0,
        max_retries=2,
        http_client=httpx.Client(transport=transport, timeout=120.0),
    )
    return DeepSeekController(client, observer=observer, phase_permit=phase_permit,
                              provider_contract_policy=provider_contract_policy,
                              generation_config=generation_config)


def _recording_transport(delegate, permit=None, provider_contract_policy=STRICT_PROVIDER_POLICY):
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
            budget_id = None
            transmitted = False
            authorization = request.headers.get("authorization", "")
            credential = authorization.partition(" ")[2] if authorization.lower().startswith("bearer ") else None
            try:
                body = json.loads(request.content)
                attempt["request_body"] = _observed_payload(body, credential)
                if permit is not None:
                    # Only noncredential body/route information enters the ledger.
                    # The hash also prevents a retry from changing prompts/tools.
                    budget_id = permit.reserve_attempt(
                        _LOGICAL.get(),
                        {
                            "model": body.get("model"),
                            "endpoint": str(request.url),
                            "max_tokens": body.get("max_tokens"),
                            "temperature": body.get("temperature"),
                            "thinking": body.get("thinking"),
                            "stream": body.get("stream"),
                            "body_sha256": hashlib.sha256(request.content).hexdigest(),
                            "method": request.method,
                            "provider_contract_policy": provider_contract_policy,
                        },
                    )
                    attempt["budget_attempt_id"] = budget_id
                transmitted = True
                response = delegate.handle_request(request)
                attempt["status_code"] = response.status_code
                if response.status_code >= 400:
                    attempt["error_type"] = "HTTPStatusError"
                response.read()
                # Preserve the received payload before accounting can stop the
                # phase. In particular, invalid usage must not erase arguments
                # that arrived successfully. Headers are never recorded.
                try:
                    body = response.json()
                    attempt["response_body"] = _observed_payload(body, credential)
                    if isinstance(body, dict):
                        for key in ("usage", "model", "system_fingerprint", "id"):
                            if key in body:
                                attempt[key] = _observed_payload(body[key], credential)
                except (ValueError, UnicodeError):
                    payload = response.content
                    if credential:
                        payload = payload.replace(credential.encode(), b"<redacted>")
                    attempt["response_body_base64"] = base64.b64encode(payload).decode("ascii")
                return response
            except BaseException as error:
                attempt["error_type"] = type(error).__name__
                raise
            finally:
                attempt["duration_seconds"] = time.perf_counter() - started
                if attempts is not None and transmitted:
                    attempts.append(attempt)
                if budget_id is not None:
                    try:
                        permit.settle(budget_id, attempt["usage"])
                    except BaseException as error:
                        attempt["error_type"] = type(error).__name__
                        attempt["settlement_error_type"] = type(error.__cause__ or error).__name__
                        raise

        def close(self):
            delegate.close()

    return RecordingTransport()
