"""D7/D8 action gates derived from verified frozen source, leaving its file intact."""
from __future__ import annotations

import ast
import copy
from pathlib import Path
from types import MethodType, MappingProxyType

from .author import make_agent_factory
from .config import DEFAULT_CONFIG, verified_author_bytes

ACTION_POLICY = 'released-action-boundaries-v1'


def action_configuration(condition):
    if type(condition) is not str or condition not in DEFAULT_CONFIG['conditions']:
        raise ValueError('Unknown memory action condition')
    return dict(DEFAULT_CONFIG['conditions'][condition])


def gated_evolution_tree(root, condition):
    """The sole algorithm delta: AND each original action guard with a fixed Boolean.

    Original parsing/validation, action order/bodies and return value remain intact.
    Locations stay unchanged so the existing passive action observer still applies.
    """
    gates = action_configuration(condition)
    tree = ast.parse(verified_author_bytes(Path(root), 'memory_layer.py'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AgenticMemorySystem')
    method = copy.deepcopy(next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_evolve'))
    found = []
    for node in ast.walk(method):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            test = node.test
            if (isinstance(test.left, ast.Name) and test.left.id == 'action'
                    and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1 and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value in gates):
                action = test.comparators[0].value
                node.test = ast.copy_location(ast.BoolOp(op=ast.And(), values=[test, ast.Constant(gates[action])]), test)
                found.append(action)
    if sorted(found) != sorted(gates):
        raise ValueError('Frozen action guards must occur exactly once each')
    return ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))


def make_action_agent_factory(repo_root, *, condition='full', **kwargs):
    """Bind two immutable action guards per instance; never patch the reference class.

    Same controller/measurement seams as make_agent_factory. No provider, parser,
    prompt, counter, retrieval or index implementation is replaced.
    """
    root = Path(repo_root).resolve()
    gates = MappingProxyType(action_configuration(condition))
    code = compile(gated_evolution_tree(root, condition), str(root / 'memory_layer.py'), 'exec')
    original = make_agent_factory(root, **kwargs)

    def factory(*, config, observer):
        agent = original(config=config, observer=observer)
        system = agent.memory_system
        namespace = dict(system._evolve.__func__.__globals__)
        exec(code, namespace)
        system._evolve = MethodType(namespace['_evolve'], system)
        agent._repro_condition = condition
        agent._repro_action_configuration = gates
        return agent

    factory._repro_condition = condition
    factory._repro_action_configuration = gates
    return factory
