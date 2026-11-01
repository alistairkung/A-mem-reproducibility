"""Lazy provider binding around the frozen author agent; no author-file edits."""

from __future__ import annotations

import __future__
import ast
import hashlib
import importlib.util
import json
import os
import random
import sys
import threading
from functools import wraps
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from .config import validate_config

_BINDING_LOCK = threading.RLock()


@contextmanager
def _local_models_only():
    names = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    previous = {name: os.environ.get(name) for name in names}
    try:
        for name in names:
            os.environ[name] = "1"
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _load_memory(root):
    name = "_amem_repro_memory_" + hashlib.sha256(str(root).encode()).hexdigest()[:12]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, root / "memory_layer.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            with _local_models_only():
                spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    return sys.modules[name]


def make_agent_factory(
    repo_root,
    *,
    paid_authorized=False,
    controller_factory=None,
    memory_module=None,
    token_counter=None,
):
    """Return the unchanged original agent with isolated controller construction.

    Inject controller_factory/memory_module for offline contracts. The live path requires separate
    paid approval and a documented context-token counter before creating any client. The original
    module's temporary controller binding is restored, including if agent construction fails.
    """
    if controller_factory is None:
        if paid_authorized is not True:
            raise PermissionError("Separate paid execution approval is required")
        if token_counter is None:
            raise ValueError(
                "A documented context-token counter is required before live execution"
            )
        from .adapter import create_deepseek_controller

        controller_factory = lambda observer: create_deepseek_controller(
            paid_authorized=True, observer=observer
        )
    root = Path(repo_root).resolve()
    tree = ast.parse((root / "test_advanced.py").read_text())
    original_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "advancedMemAgent"
    )
    compiled = compile(
        ast.Module(body=[original_class], type_ignores=[]),
        str(root / "test_advanced.py"),
        "exec",
        flags=__future__.annotations.compiler_flag,
    )

    def factory(*, config, observer):
        validate_config(config)
        module = memory_module if memory_module is not None else _load_memory(root)
        controllers = []
        measurement_errors = []

        def controller_binding(*args, **kwargs):
            controller = controller_factory(observer)
            controllers.append(controller)
            return SimpleNamespace(llm=controller)

        namespace = {
            "AgenticMemorySystem": module.AgenticMemorySystem,
            "LLMController": controller_binding,
            "json": json,
            "random": random,
        }
        exec(compiled, namespace)
        with _BINDING_LOCK, _local_models_only():
            previous = module.LLMController
            try:
                module.LLMController = controller_binding
                agent = namespace["advancedMemAgent"](
                    config["model"]["id"],
                    "openai",
                    config["retrieval"]["answer_k"],
                    config["generation"]["temperature_c5"],
                    refresh_index=False,
                )
            finally:
                module.LLMController = previous

        def offline_assets(method):
            @wraps(method)
            def wrapped(*args, **kwargs):
                with _BINDING_LOCK, _local_models_only():
                    return method(*args, **kwargs)

            return wrapped

        original_add = agent.add_memory

        @wraps(original_add)
        def measured_add(*args, **kwargs):
            from .measurements import observe_actions

            with _local_models_only(), observe_actions(root, observer) as errors:
                try:
                    return original_add(*args, **kwargs)
                finally:
                    measurement_errors.extend({"error_type": name} for name in errors)

        agent.add_memory = offline_assets(measured_add)
        agent.answer_question = offline_assets(agent.answer_question)
        agent._repro_note_type = module.MemoryNote
        agent._repro_failure_counts = lambda: dict(module.FAILURES)
        agent._repro_observer_errors = (
            lambda: [error for c in controllers for error in c.observer_errors]
            + measurement_errors
        )
        if token_counter is not None:
            from .measurements import observe_retrieval

            def retrieve(content, k=10):
                context, event = observe_retrieval(
                    agent.memory_system, content, k, token_counter
                )
                try:
                    observer(event)
                except Exception as error:
                    measurement_errors.append({"error_type": type(error).__name__})
                return context

            agent.retrieve_memory = retrieve
        return agent

    return factory
