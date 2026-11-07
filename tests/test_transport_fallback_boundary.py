"""Characterise the author boundary; these tests grant no recovery permission."""
import copy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from amem_repro.actions import make_action_agent_factory
from amem_repro.artifacts import snapshot_memory
from amem_repro.budget import BudgetStop
from amem_repro.config import load_config, verified_author_bytes
from test_foundation import original_memory_module

ROOT = Path(__file__).resolve().parents[1]


def system(condition, error):
    verified_author_bytes(ROOT, 'memory_layer.py')
    module = original_memory_module()
    module.print = lambda *args, **kwargs: None
    calls = []

    def fail(prompt, response_format, **kwargs):
        calls.append((prompt, copy.deepcopy(response_format)))
        raise error

    factory = make_action_agent_factory(
        ROOT, condition=condition, memory_module=module,
        controller_factory=lambda observer: SimpleNamespace(
            get_completion=fail, observer_errors=[]))
    memory = factory(config=load_config(), observer=lambda event: None).memory_system
    old = module.MemoryNote('old', id='old', keywords=['kw'], context='old',
                            tags=['old'], timestamp='dataset', last_accessed='saved')
    memory.memories[old.id] = old
    memory.retriever.add_documents([module.note_document(old)])
    memory.evo_cnt = 99
    return module, memory, calls


@pytest.mark.parametrize('condition', ['full', 'neither', 'linking_only', 'evolution_only'])
@pytest.mark.parametrize('financial_stop', [False, True])
def test_author_transport_fallback_and_financial_stop_have_distinct_boundaries(
        condition, financial_stop):
    error = (BudgetStop('financial stop') if financial_stop else
             httpx.RemoteProtocolError('Server disconnected without sending a response.'))
    module, memory, calls = system(condition, error)
    before = snapshot_memory(memory)
    consolidations = []
    memory.consolidate_memories = lambda: consolidations.append(True)

    def insert():
        return memory.add_note('new', time='dataset', id='new', last_accessed='fixed',
                               keywords=['kw'], context='metadata', tags=['tag'],
                               category='fixture')

    if financial_stop:
        with pytest.raises(BudgetStop):
            insert()
        assert snapshot_memory(memory) == before
        assert not module.FAILURES
    else:
        assert insert() == 'new'
        after = snapshot_memory(memory)
        assert after['notes'][:-1] == before['notes']
        assert after['retriever']['corpus'][:-1] == before['retriever']['corpus']
        assert after['retriever']['embeddings'][:-1] == before['retriever']['embeddings']
        assert memory.memories['new'].links == []
        assert memory.memories['new'].tags == ['tag']
        assert memory.memories['new'].context == 'metadata'
        assert dict(module.FAILURES) == {'evolve': 1}
    assert memory.evo_cnt == 99
    assert consolidations == []
    assert len(calls) == 1


def test_committed_snapshot_cannot_identify_an_uninserted_note(monkeypatch):
    snapshots, pending_ids = [], []
    for identity in ('first-pending-identity', 'second-pending-identity'):
        module, memory, calls = system('linking_only', BudgetStop('financial stop'))
        monkeypatch.setattr(module, 'uuid', SimpleNamespace(uuid4=lambda: identity))
        original = memory.process_memory

        def observe(note):
            pending_ids.append(note.id)
            return original(note)

        memory.process_memory = observe
        with pytest.raises(BudgetStop):
            memory.add_note('new', time='dataset', keywords=['kw'], context='metadata',
                            tags=['tag'], category='fixture')
        snapshots.append(snapshot_memory(memory))
        assert len(calls) == 1
    assert pending_ids == ['first-pending-identity', 'second-pending-identity']
    assert snapshots[0] == snapshots[1]
