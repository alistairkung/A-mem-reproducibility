import ast
from collections import Counter
import re
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from amem_repro.adapter import (
    DeepSeekController,
    AdapterError,
    create_deepseek_controller,
)
from amem_repro.contracts import load_author_contracts

ROOT = Path(__file__).resolve().parents[1]


def completion(arguments=' {"answer": "Paris"} ', **overrides):
    result = {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {"name": "response", "arguments": arguments},
                        }
                    ]
                },
            }
        ],
        "model": "deepseek-flash",
        "system_fingerprint": "backend-test",
        "id": "request-test",
        "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
    }
    result.update(overrides)
    return result


class Client:
    def __init__(self, response):
        self.response = response
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **request):
        self.requests.append(copy.deepcopy(request))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class AdapterTest(unittest.TestCase):
    def setUp(self):
        self.contracts = load_author_contracts(ROOT)

    def test_translates_contract_once_and_returns_original_arguments(self):
        client = Client(completion())
        events = []
        contract = self.contracts["answer"]
        original = copy.deepcopy(contract)
        out = DeepSeekController(client, observer=events.append).get_completion(
            "Original prompt", contract, 0.5
        )
        self.assertEqual(out, ' {"answer": "Paris"} ')
        self.assertEqual(contract, original)
        self.assertEqual(
            client.requests,
            [
                {
                    "model": "deepseek-flash",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You must respond with a JSON object.",
                        },
                        {"role": "user", "content": "Original prompt"},
                    ],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "response",
                                "strict": True,
                                "parameters": contract["json_schema"]["schema"],
                            },
                        }
                    ],
                    "tool_choice": {
                        "type": "function",
                        "function": {"name": "response"},
                    },
                    "extra_body": {"thinking": {"type": "disabled"}},
                    "temperature": 0.5,
                    "max_tokens": 1000,
                    "stream": False,
                }
            ],
        )
        self.assertEqual(events[0]["stage"], "answer")
        self.assertEqual(events[0]["usage"]["prompt_tokens"], 20)
        self.assertEqual(events[0]["system_fingerprint"], "backend-test")
        self.assertEqual(events[0]["output"], out)

    def test_live_factory_refuses_before_reading_credentials_or_importing_sdk(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(PermissionError):
                create_deepseek_controller()

    def test_rejects_missing_wrong_multiple_truncated_or_bad_arguments_without_retry(
        self,
    ):
        variants = []
        for mutate in [
            lambda r: r["choices"][0].update(finish_reason="length"),
            lambda r: r["choices"][0]["message"].update(tool_calls=[]),
            lambda r: r["choices"][0]["message"]["tool_calls"].append(
                copy.deepcopy(r["choices"][0]["message"]["tool_calls"][0])
            ),
            lambda r: r["choices"][0]["message"]["tool_calls"][0]["function"].update(
                name="other"
            ),
            lambda r: r["choices"][0]["message"]["tool_calls"][0]["function"].update(
                arguments='{"answer":'
            ),
            lambda r: r["choices"][0]["message"]["tool_calls"][0]["function"].update(
                arguments='{"answer": 3}'
            ),
            lambda r: r["choices"][0]["message"]["tool_calls"][0]["function"].update(
                arguments='{"response": "Paris"}'
            ),
        ]:
            response = completion()
            mutate(response)
            variants.append(response)
        for response in variants:
            with self.subTest(response=response):
                client = Client(response)
                events = []
                with self.assertRaises(AdapterError):
                    DeepSeekController(client, observer=events.append).get_completion(
                        "Prompt", self.contracts["answer"]
                    )
                self.assertEqual(len(client.requests), 1)
                self.assertEqual(events[0]["error_type"], "AdapterError")

    def test_all_four_original_schemas_pass_through_and_reject_unsupported_contract(
        self,
    ):
        values = {
            "metadata": {
                "keywords": ["Paris"],
                "context": "A city",
                "tags": ["geography"],
            },
            "shared_decision": {
                "should_evolve": True,
                "actions": ["strengthen"],
                "suggested_connections": [2],
                "new_context_neighborhood": [],
                "tags_to_update": ["geography"],
                "new_tags_neighborhood": [],
            },
            "query_keywords": {"keywords": "Paris"},
            "answer": {"answer": "Paris"},
        }
        for stage, value in values.items():
            args = json.dumps(value, indent=2)
            client = Client(completion(args))
            events = []
            result = DeepSeekController(client, observer=events.append).get_completion(
                "Unchanged", self.contracts[stage]
            )
            self.assertEqual(result, args)
            self.assertEqual(events[0]["stage"], stage)
        client = Client(completion())
        invalid = copy.deepcopy(self.contracts["answer"])
        invalid["json_schema"]["schema"]["properties"]["answer"]["maxLength"] = 10
        with self.assertRaises(ValueError):
            DeepSeekController(client).get_completion("Prompt", invalid)
        self.assertEqual(client.requests, [])

    def test_failure_record_has_no_exception_text_and_observer_cannot_change_output(
        self,
    ):
        client = Client(RuntimeError("sensitive fake credential in exception"))
        events = []
        with self.assertRaises(RuntimeError):
            DeepSeekController(client, observer=events.append).get_completion(
                "Prompt", self.contracts["answer"]
            )
        self.assertEqual(events[0]["error_type"], "RuntimeError")
        self.assertNotIn("sensitive", json.dumps(events))

        def broken_observer(event):
            raise OSError("observer failed")

        controller = DeepSeekController(Client(completion()), observer=broken_observer)
        self.assertEqual(
            controller.get_completion("Prompt", self.contracts["answer"]),
            ' {"answer": "Paris"} ',
        )
        self.assertEqual(
            controller.observer_errors, [{"stage": "answer", "error_type": "OSError"}]
        )

    def test_existing_metadata_and_query_parsers_consume_adapter_outputs(self):
        # Compile only these original functions: imports and model initialization never execute.
        def author_function(filename, class_name, method_name):
            tree = ast.parse((ROOT / filename).read_text())
            cls = next(
                n
                for n in tree.body
                if isinstance(n, ast.ClassDef) and n.name == class_name
            )
            fn = copy.deepcopy(
                next(
                    n
                    for n in cls.body
                    if isinstance(n, ast.FunctionDef) and n.name == method_name
                )
            )
            fn.decorator_list = []
            fn.returns = None
            for arg in fn.args.args:
                arg.annotation = None
            module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
            scope = {
                "json": json,
                "re": re,
                "FAILURES": Counter(),
                "print": lambda *args: None,
            }
            exec(compile(module, filename, "exec"), scope)
            return scope[method_name]

        metadata = {"keywords": ["Paris"], "context": "A city", "tags": ["geography"]}
        controller = DeepSeekController(Client(completion(json.dumps(metadata))))
        analyze = author_function("memory_layer.py", "MemoryNote", "analyze_content")
        self.assertEqual(
            analyze("Paris is a city", SimpleNamespace(llm=controller)), metadata
        )
        query = author_function(
            "test_advanced.py", "advancedMemAgent", "generate_query_llm"
        )
        controller = DeepSeekController(Client(completion('{"keywords":"Paris"}')))
        self.assertEqual(
            query(
                SimpleNamespace(retriever_llm=SimpleNamespace(llm=controller)),
                "Which city?",
            ),
            "Paris",
        )

    def test_sdk_retries_are_bounded_and_each_physical_attempt_is_recorded(self):
        import httpx

        events, requests = [], []

        def handler(request):
            requests.append(request)
            if len(requests) < 3:
                return httpx.Response(
                    429,
                    json={"error": {"message": "rate limited"}},
                    headers={"retry-after-ms": "1"},
                )
            return httpx.Response(200, json=completion())

        with patch.dict(
            "os.environ", {"DEEPSEEK_API_KEY": "offline-placeholder"}, clear=True
        ):
            controller = create_deepseek_controller(
                paid_authorized=True,
                observer=events.append,
                http_transport=httpx.MockTransport(handler),
            )
            result = controller.get_completion("Prompt", self.contracts["answer"])
            controller.client.close()
        self.assertEqual(result, ' {"answer": "Paris"} ')
        self.assertEqual(len(requests), 3)
        self.assertEqual(
            [a["status_code"] for a in events[0]["attempts"]], [429, 429, 200]
        )
        self.assertEqual(events[0]["attempts"][2]["usage"]["prompt_tokens"], 20)
        self.assertNotIn("offline-placeholder", json.dumps(events))
        self.assertEqual(events[0]["returned_model"], "deepseek-flash")
        self.assertEqual(
            str(requests[0].url), "https://api.deepseek.com/beta/chat/completions"
        )
        self.assertEqual(requests[0].extensions["timeout"]["read"], 120.0)

    def test_sdk_exhaustion_preserves_failed_attempts_and_does_not_semantically_retry(
        self,
    ):
        import httpx

        events, requests = [], []

        def handler(request):
            requests.append(request)
            return httpx.Response(
                503,
                json={"error": {"message": "offline failure"}},
                headers={"retry-after-ms": "1"},
            )

        with patch.dict(
            "os.environ", {"DEEPSEEK_API_KEY": "offline-placeholder"}, clear=True
        ):
            controller = create_deepseek_controller(
                paid_authorized=True,
                observer=events.append,
                http_transport=httpx.MockTransport(handler),
            )
            with self.assertRaises(Exception):
                controller.get_completion("Prompt", self.contracts["answer"])
            controller.client.close()
        self.assertEqual(len(requests), 3)
        self.assertEqual(
            [a["status_code"] for a in events[0]["attempts"]], [503, 503, 503]
        )
        self.assertEqual(events[0]["error_type"], "InternalServerError")
        self.assertTrue(all(a["usage"] is None for a in events[0]["attempts"]))


if __name__ == "__main__":
    unittest.main()


class LiveExecutionFuseTests(unittest.TestCase):
    def test_boolean_approval_cannot_enable_uncapped_live_factory(self):
        with patch(
            "amem_repro.adapter.os.environ.get",
            side_effect=AssertionError("credential access"),
        ):
            with self.assertRaisesRegex(NotImplementedError, "T5"):
                create_deepseek_controller(paid_authorized=True)

    def test_real_transport_cannot_bypass_t5_fuse(self):
        import httpx

        transport = httpx.HTTPTransport()
        try:
            with self.assertRaisesRegex(NotImplementedError, "T5"):
                create_deepseek_controller(
                    paid_authorized=True, http_transport=transport
                )
        finally:
            transport.close()
