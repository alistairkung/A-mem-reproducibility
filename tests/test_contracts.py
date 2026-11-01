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


if __name__ == "__main__":
    unittest.main()
