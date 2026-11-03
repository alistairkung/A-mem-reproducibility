"""Observational retrieval counts and usage accounting; never transform context."""

from dataclasses import dataclass
from numbers import Integral

from .config import verified_author_bytes


@dataclass(frozen=True)
class TokenCounter:
    encode: object
    method: str
    revision: str
    exact: bool = False

    def count(self, text):
        return len(self.encode(text))


def observe_retrieval(system, query, k, counter, *, observer=None):
    """Capture the author's actual search once; retain raw return bytes and duplicates.

    Execution is serial under the protocol. The temporary instance observer is
    restored even when retrieval raises. Counts mirror the original k+1 link cap.
    """
    if not counter.method or not counter.revision:
        raise ValueError("Document token counting method and revision")
    import time
    started = time.perf_counter()
    begin = getattr(observer, 'begin_retrieval', None)
    if begin is not None:
        try:
            begin({'type': 'retrieval_start', 'input': {'query': query, 'k': k}})
        except Exception:
            pass  # A passive hook cannot change original retrieval or context.
    retriever = system.retriever
    previous = retriever.search
    had_override = "search" in getattr(retriever, "__dict__", {})
    indices = []

    def observed(*args, **kwargs):
        result = previous(*args, **kwargs)
        indices.extend(list(result))
        return result

    retriever.search = observed
    try:
        context = system.find_related_memories_raw(query, k=k)
    finally:
        if had_override:
            retriever.search = previous
        else:
            del retriever.search
    notes = list(system.memories.values())
    expanded = len(indices)
    for index in indices:
        valid = [
            n
            for n in notes[index].links
            if isinstance(n, Integral)
            and not isinstance(n, bool)
            and 0 <= n < len(notes)
        ]
        expanded += len(valid[: k + 1])
    count_error = None
    try:
        context_tokens = counter.count(context) if isinstance(context, str) else 0
    except Exception as error:
        context_tokens = None
        count_error = type(error).__name__
    event = {
        "type": "retrieval",
        "initial_count": len(indices),
        "expanded_count": expanded,
        "context_tokens": context_tokens,
        "token_count_error": count_error,
        "token_count_method": counter.method,
        "tokenizer_revision": counter.revision,
        "token_count_exact": counter.exact,
    }
    if begin is not None:
        event.update(input={'query': query, 'k': k},
                     output={'context': context, 'initial_count': len(indices),
                             'expanded_count': expanded, 'context_tokens': context_tokens},
                     duration_seconds=time.perf_counter() - started)
    return context, event


def summarize_generations(events, pricing=None):
    """Prefer physical attempts over their logical summary; unknown charges stay unknown.

    Prices are an explicitly supplied, dated estimate, not provider billing. Input
    cache discounts are not assumed; observed charged_cost_usd takes precedence.
    """
    totals = {}
    for event in events:
        if event.get("type", "generation") != "generation":
            continue
        stage = event.get("stage") or "unknown"
        total = totals.setdefault(
            stage,
            {
                "logical_calls": 0,
                "physical_attempts": 0,
                "unknown_attempts": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "known_cost_usd": 0.0,
                "total_cost_usd": None,
                "cost_basis": pricing.get("pricing_id") if pricing else "reported-only",
            },
        )
        total["logical_calls"] += 1
        attempts = event.get("attempts") or [event]
        for attempt in attempts:
            total["physical_attempts"] += 1
            usage = attempt.get("usage")
            if (
                not usage
                or usage.get("prompt_tokens") is None
                or usage.get("completion_tokens") is None
            ):
                total["unknown_attempts"] += 1
                continue
            input_tokens = usage["prompt_tokens"]
            output_tokens = usage["completion_tokens"]
            total["input_tokens"] += input_tokens
            total["output_tokens"] += output_tokens
            cost = attempt.get("charged_cost_usd")
            if cost is None and pricing:
                cost = (
                    input_tokens * pricing["input_per_million"]
                    + output_tokens * pricing["output_per_million"]
                ) / 1_000_000
            if cost is None:
                total["unknown_attempts"] += 1
            else:
                total["known_cost_usd"] += cost
        total["total_cost_usd"] = (
            None if total["unknown_attempts"] else total["known_cost_usd"]
        )
    return totals


def observe_actions(root, observer):
    """Time the original two action branches with passive line events.

    This adds no statements to author functions. Serial execution is required;
    an existing debugger/coverage tracer must be disabled before live runs.
    Timings include observational overhead and are not separate API charges.
    """
    import ast
    import copy
    import sys
    import time
    from contextlib import contextmanager
    from pathlib import Path

    path = Path(root).resolve() / "memory_layer.py"
    tree = ast.parse(verified_author_bytes(path.parent, "memory_layer.py"))
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "AgenticMemorySystem"
    )
    method = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_evolve"
    )
    ranges = {}
    for node in ast.walk(method):
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "action"
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
        ):
            name = node.test.comparators[0].value
            if name in ("strengthen", "update_neighbor"):
                ranges[name] = (node.body[0].lineno, node.body[-1].end_lineno)
    if set(ranges) != {"strengthen", "update_neighbor"}:
        raise ValueError("Frozen action boundaries not found")

    @contextmanager
    def watching():
        if sys.gettrace() is not None:
            raise RuntimeError(
                "Action measurement requires an unoccupied thread tracing hook"
            )
        active = {}
        errors = []

        begin = getattr(observer, 'begin_action', None)

        def view(frame):
            values = frame.f_locals
            notes = list(values['self'].memories.values())
            def note_view(note):
                return {name: copy.deepcopy(getattr(note, name, None))
                        for name in ('id', 'content', 'context', 'keywords', 'tags', 'links')}
            return {'new_note': note_view(values['note']),
                    'neighbors': [{'index': int(i), 'note': note_view(notes[int(i)])}
                                  for i in values.get('indices', [])],
                    'decision': copy.deepcopy(values.get('response_json'))}

        def close(frame_id):
            action, started, frame, before = active.pop(frame_id)
            try:
                event = {
                        "type": "local_action",
                        "action": action,
                        "api_calls": 0,
                        "duration_seconds": time.perf_counter() - started,
                        "timing_method": "python-line-trace; includes observer overhead",
                    }
                if begin is not None:
                    event.update(input=before, output=view(frame))
                observer(event)
            except Exception as error:
                errors.append(type(error).__name__)

        def trace(frame, event, arg):
            if (
                frame.f_code.co_filename != str(path)
                or frame.f_code.co_name != "_evolve"
            ):
                return None
            key = id(frame)
            selected = (
                next(
                    (
                        name
                        for name, (start, end) in ranges.items()
                        if start <= frame.f_lineno <= end
                    ),
                    None,
                )
                if event == "line"
                else None
            )
            if key in active and (
                event in ("return", "exception")
                or (event == "line" and active[key][0] != selected)
            ):
                close(key)
            if event == "line" and selected and key not in active:
                before = None
                if begin is not None:
                    try:
                        before = view(frame)
                        begin({'type': 'local_action_start', 'action': selected, 'input': before})
                    except Exception as error:
                        errors.append(type(error).__name__)
                active[key] = (selected, time.perf_counter(), frame, before)
            return trace

        sys.settrace(trace)
        try:
            yield errors
        finally:
            sys.settrace(None)
            for key in list(active):
                close(key)

    return watching()
