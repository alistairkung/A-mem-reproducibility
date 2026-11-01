import copy
import json
from pathlib import Path
import unittest

from amem_repro.contracts import (
    load_author_contracts,
    validate_strict_schema,
    validate_arguments,
    ContractError,
)

ROOT = Path(__file__).resolve().parents[1]


class AuthorContractsTest(unittest.TestCase):
    def test_extracts_four_original_contracts_without_importing_authors(self):
        contracts = load_author_contracts(ROOT)
        self.assertEqual(
            set(contracts), {"metadata", "shared_decision", "query_keywords", "answer"}
        )
        self.assertEqual(
            contracts["answer"],
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": {
                        "type": "object",
                        "properties": {"answer": {"type": "string"}},
                        "required": ["answer"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
        )
        self.assertEqual(
            contracts["shared_decision"]["json_schema"]["schema"]["properties"][
                "new_tags_neighborhood"
            ],
            {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
        )
        for contract in contracts.values():
            validate_strict_schema(contract["json_schema"]["schema"])

    def test_rejects_semantic_changes_instead_of_repairing_them(self):
        schema = {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": [],
            "additionalProperties": False,
        }
        original = copy.deepcopy(schema)
        with self.assertRaises(ContractError):
            validate_strict_schema(schema)
        self.assertEqual(schema, original)
        with self.assertRaises(ContractError):
            validate_strict_schema(
                {"type": "array", "items": {"type": "string"}, "minItems": 1}
            )

    def test_json_schema_integral_numbers_preserve_integer_semantics(self):
        validate_arguments(1.0, {"type": "integer"})
        for value in [True, 1.5]:
            with self.assertRaises(ContractError):
                validate_arguments(value, {"type": "integer"})

    def test_observed_deepseek_connection_strings_violate_the_frozen_contract(self):
        from jsonschema import Draft202012Validator

        schema = load_author_contracts(ROOT)["shared_decision"]["json_schema"]["schema"]
        decision = {
            "should_evolve": True,
            "actions": ["strengthen"],
            "suggested_connections": ["2", "3"],
            "tags_to_update": [],
            "new_context_neighborhood": [],
            "new_tags_neighborhood": [],
        }
        original = copy.deepcopy(decision)
        with self.assertRaisesRegex(ContractError, r"suggested_connections\[0\].*integer"):
            validate_arguments(decision, schema)
        self.assertEqual(decision, original)
        self.assertEqual(
            [list(error.path) for error in Draft202012Validator(schema).iter_errors(decision)],
            [["suggested_connections", 0], ["suggested_connections", 1]],
        )
        control = {**decision, "suggested_connections": [2, 3]}
        validate_arguments(control, schema)
        self.assertTrue(Draft202012Validator(schema).is_valid(control))


if __name__ == "__main__":
    unittest.main()


class FrozenSourceTests(unittest.TestCase):
    def test_standalone_schema_loader_rejects_changed_author_bytes(self):
        from unittest.mock import patch

        read = Path.read_bytes

        def changed(path):
            value = read(path)
            return (
                value + b"\n# changed\n" if path == ROOT / "memory_layer.py" else value
            )

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "Frozen author source changed"):
                load_author_contracts(ROOT)

    def test_standalone_agent_loader_rejects_changed_author_bytes(self):
        from unittest.mock import patch
        from amem_repro.author import make_agent_factory

        read = Path.read_bytes

        def changed(path):
            value = read(path)
            return (
                value + b"\n# changed\n" if path == ROOT / "test_advanced.py" else value
            )

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "Frozen author source changed"):
                make_agent_factory(ROOT, controller_factory=lambda observer: None)
