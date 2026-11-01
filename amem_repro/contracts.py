"""Read the four frozen author output contracts without importing model code."""

from __future__ import annotations

import ast
import math
from pathlib import Path
from typing import Any

from .config import verified_author_bytes


class ContractError(ValueError):
    """A contract cannot be represented without changing its semantics."""


_LOCATIONS = {
    "metadata": ("memory_layer.py", "MemoryNote", "analyze_content"),
    "shared_decision": ("memory_layer.py", "AgenticMemorySystem", "_evolve"),
    "query_keywords": ("test_advanced.py", "advancedMemAgent", "generate_query_llm"),
    "answer": ("test_advanced.py", "advancedMemAgent", "answer_question"),
}


def load_author_contracts(root: str | Path | None = None) -> dict[str, dict]:
    """Extract exact response_format literals; do not run author imports or initialization."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contracts = {}
    for stage, (filename, class_name, method_name) in _LOCATIONS.items():
        tree = ast.parse(verified_author_bytes(root, filename))
        cls = next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name
        )
        method = next(
            n
            for n in cls.body
            if isinstance(n, ast.FunctionDef) and n.name == method_name
        )
        values = [
            ast.literal_eval(kw.value)
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            for kw in node.keywords
            if kw.arg == "response_format"
        ]
        if len(values) != 1:
            raise ContractError(
                f"{stage}: expected exactly one author response contract"
            )
        contract = values[0]
        if (
            contract.get("type") != "json_schema"
            or contract.get("json_schema", {}).get("strict") is not True
        ):
            raise ContractError(f"{stage}: expected original strict JSON schema")
        validate_strict_schema(contract["json_schema"]["schema"])
        contracts[stage] = contract
    return contracts


def validate_strict_schema(schema: dict[str, Any], path: str = "$") -> None:
    """Fail closed on unsupported schema syntax; never transform a schema."""
    if not isinstance(schema, dict):
        raise ContractError(f"{path}: schema must be an object")
    kind = schema.get("type")
    allowed = {"type", "description", "enum"}
    if kind == "object":
        allowed |= {"properties", "required", "additionalProperties"}
        properties = schema.get("properties")
        required = schema.get("required")
        if (
            not isinstance(properties, dict)
            or not isinstance(required, list)
            or len(required) != len(properties)
            or set(required) != set(properties)
            or schema.get("additionalProperties") is not False
        ):
            raise ContractError(
                f"{path}: strict objects require all properties and additionalProperties=false"
            )
        for key, value in properties.items():
            validate_strict_schema(value, f"{path}.{key}")
    elif kind == "array":
        allowed |= {"items"}
        validate_strict_schema(schema.get("items"), f"{path}[]")
    elif kind not in {"string", "integer", "number", "boolean"}:
        raise ContractError(f"{path}: unsupported schema type {kind!r}")
    if set(schema) - allowed:
        raise ContractError(
            f"{path}: unsupported constraints {sorted(set(schema) - allowed)}"
        )


def validate_arguments(value: Any, schema: dict, path: str = "$") -> None:
    """Check returned JSON against the unchanged, supported contract without repairing it."""
    kind = schema["type"]
    types = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
    }
    integral_float = (
        kind == "integer"
        and isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    )
    if (not isinstance(value, types[kind]) and not integral_float) or (
        kind in {"integer", "number"}
        and (
            isinstance(value, bool)
            or (isinstance(value, float) and not math.isfinite(value))
        )
    ):
        raise ContractError(f"{path}: expected {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{path}: value outside enum")
    if kind == "object":
        if set(value) != set(schema["properties"]):
            raise ContractError(f"{path}: unexpected or missing fields")
        for name, child in schema["properties"].items():
            validate_arguments(value[name], child, f"{path}.{name}")
    elif kind == "array":
        for i, item in enumerate(value):
            validate_arguments(item, schema["items"], f"{path}[{i}]")
