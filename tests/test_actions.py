"""T7 controlled action ablations; synthetic responses never represent live trials."""
import ast
import copy
import json
from pathlib import Path

import pytest

from amem_repro.actions import action_configuration, gated_evolution_tree, make_action_agent_factory
from amem_repro.artifacts import CacheRejected, CacheStore, snapshot_memory
from amem_repro.config import load_config
from amem_repro.replay import ReplayController, memory_view
from amem_repro.runner import run_manifest
from amem_repro.manifests import build_manifest
from amem_repro.adapter import DeepSeekController
from amem_repro.scoring import AuthorScorer
from test_foundation import original_memory_module, Provider
from test_replay import opening, synthetic_record, bind_synthetic_decision, decision
from test_scoring import dependencies

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ['neither', 'linking_only', 'evolution_only', 'full']


@pytest.mark.parametrize('condition', CONDITIONS)
def test_ast_delta_is_exactly_two_boolean_action_guards(condition):
    tree = gated_evolution_tree(ROOT, condition)
    restored = copy.deepcopy(tree.body[0])
    found = []
    for node in ast.walk(restored):
        if isinstance(node, ast.If) and isinstance(node.test, ast.BoolOp):
            if isinstance(node.test.values[0], ast.Compare) and isinstance(node.test.values[0].left, ast.Name) \
                    and node.test.values[0].left.id == 'action':
                original, gate = node.test.values
                action = original.comparators[0].value
                assert type(gate.value) is bool and gate.value is action_configuration(condition)[action]
                assert isinstance(node.test.op, ast.And)
                found.append(action)
                node.test = original
    source = ast.parse((ROOT/'memory_layer.py').read_text())
    cls = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'AgenticMemorySystem')
    original = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_evolve')
    assert sorted(found) == ['strengthen', 'update_neighbor']
    assert ast.dump(restored, include_attributes=True) == ast.dump(original, include_attributes=True)


@pytest.mark.parametrize('condition', CONDITIONS)
@pytest.mark.parametrize('actions', [[], ['strengthen'], ['update_neighbor'], ['strengthen','update_neighbor']])
@pytest.mark.parametrize('positive', [False, True])
@pytest.mark.parametrize('counter', [0, 99])
def test_all_action_configurations_preserve_decisions_counters_and_index(condition, actions, positive, counter):
    m = original_memory_module(); m.print = lambda *a, **k: None
    factory = make_action_agent_factory(ROOT, condition=condition, memory_module=m,
                                       controller_factory=lambda observer: None)
    agent = factory(config=load_config(), observer=lambda e: None)
    s = agent.memory_system
    old = m.MemoryNote('old', id='old', keywords=['kw'], context='old-context', tags=['old-tag'], timestamp='fixed')
    s.memories['old'] = old
    s.retriever.add_documents([m.note_document(old)])
    s.evo_cnt = counter
    record = synthetic_record('shared_decision', decision(actions, positive))
    replay = bind_synthetic_decision(s, record, 'new', 'new-context')
    consolidation = []; original = s.consolidate_memories
    def consolidate():
        consolidation.append(s.evo_cnt)
        return original()
    s.consolidate_memories = consolidate
    s.add_note('new', time='fixed', id='new', keywords=['kw'], context='new-context', tags=['initial'], category='fixture')
    replay.finish()
    flags = action_configuration(condition)
    linking = positive and 'strengthen' in actions and flags['strengthen']
    evolution = positive and 'update_neighbor' in actions and flags['update_neighbor']
    assert s.evo_cnt == counter + int(positive)
    assert consolidation == ([100] if positive and counter == 99 else [])
    assert s.memories['new'].links == ([0,0] if linking else [])
    assert s.memories['new'].tags == (['linked'] if linking else ['initial'])
    assert old.context == ('updated-context' if evolution else 'old-context')
    assert old.tags == (['updated-tag'] if evolution else ['old-tag'])
    assert not m.FAILURES
    if positive and counter == 99:
        assert s.retriever.corpus == [f'{n.content} , {n.context} {" ".join(n.keywords)} {" ".join(n.tags)}' for n in s.memories.values()]
    else:
        assert s.retriever.corpus[0] == 'content:old context:old-context keywords: kw tags: old-tag'
    assert s.find_related_memories_raw('q', k=10).count('memory content: old') == (3 if linking else 1)


@pytest.mark.parametrize('condition', CONDITIONS)
@pytest.mark.parametrize('raw', ['{"new_tags_neighborhood":[["x"]}', '{"should_evolve":true,"actions":["strengthen"]}'])
def test_rejected_outputs_keep_original_fallback_even_when_action_disabled(condition, raw):
    m = original_memory_module(); m.print = lambda *a, **k: None
    factory = make_action_agent_factory(ROOT, condition=condition, memory_module=m,
                                       controller_factory=lambda observer: None)
    s = factory(config=load_config(), observer=lambda e: None).memory_system
    s.evo_cnt = 99
    replay = bind_synthetic_decision(s, synthetic_record('shared_decision', None, raw=raw), 'new', 'original')
    s.add_note('new', time='fixed', id='new', keywords=['kw'], context='original', tags=['original'], category='fixture')
    replay.finish()
    assert s.evo_cnt == 99 and dict(m.FAILURES) == {'evolve': 1}
    assert s.memories['new'].links == [] and s.memories['new'].tags == ['original']
    assert replay.observations[0]['output'] == raw


def test_candidate_full_mode_uses_captured_opening_golden_without_modifying_reference_class():
    fixture = opening(); m = original_memory_module(); m.print = lambda *a, **k: None
    original = m.AgenticMemorySystem._evolve
    replay = ReplayController(fixture['records'], provider_contract_policy='canonical-index-strings-v1')
    factory = make_action_agent_factory(ROOT, memory_module=m, controller_factory=lambda observer: replay)
    agent = factory(config=load_config(), observer=lambda e: None)
    assert agent.memory_system._evolve.__func__ is not original
    for turn, golden in zip(fixture['turns'], fixture['comparison_states']):
        agent.add_memory(turn['content'], time=turn['timestamp'])
        assert memory_view(snapshot_memory(agent.memory_system)) == golden
    replay.finish()
    assert m.AgenticMemorySystem._evolve is original


@pytest.mark.parametrize('condition', CONDITIONS)
def test_initial_metadata_shared_calls_observations_and_cache_isolation(tmp_path, condition):
    provider = Provider(); m = original_memory_module(); m.print = lambda *a, **k: None
    factory = make_action_agent_factory(ROOT, condition=condition, memory_module=m,
                controller_factory=lambda observer: DeepSeekController(provider, observer=observer))
    flags = action_configuration(condition)
    run = tmp_path/'run'; cache = tmp_path/'cache'
    result = run_manifest(ROOT/'data/locomo10.json', build_manifest(ROOT/'data/locomo10.json', 'smoke'), load_config(),
                    output_dir=run, cache_root=cache, source_hashes={'test':'fixed'},
                    condition=condition, agent_factory=factory, scorer=AuthorScorer(ROOT, dependencies=dependencies()))
    assert result['status'] == 'complete' and len(provider.requests) == 44
    events = [json.loads(s) for s in (run/'events.jsonl').read_text().splitlines()]
    start = events[0]
    assert start['memory_actions'] == flags and start['condition'] == condition
    assert start['action_implementation'] == 't7-action-gates'
    outcomes = [e for e in events if e['type']=='evolution_outcome']
    assert len(outcomes)==18 and all(e['counter_after']==i+1 for i,e in enumerate(outcomes))
    assert all(e['enabled_actions']==[a for a, on in flags.items() if on] for e in outcomes)
    assert all(e['suppressed_actions']==[a for a, on in flags.items() if not on] for e in outcomes)
    measured = [e['action'] for e in events if e['type']=='local_action']
    assert all(measured.count(a)==(18 if on else 0) for a,on in flags.items())
    path = next(cache.glob('*/identity.json')); identity = json.loads(path.read_text())
    state = CacheStore(cache).load(identity)
    assert identity['memory_actions'] == flags and identity['condition']==condition
    assert len(state['notes'])==18
    assert all(n['attributes']['keywords']==['kw'] for n in state['notes'])
    for other in CONDITIONS:
        if other==condition: continue
        changed = {**identity, 'condition':other, 'memory_actions':action_configuration(other)}
        with pytest.raises(CacheRejected): CacheStore(cache).load(changed)


@pytest.mark.parametrize('requested', CONDITIONS)
def test_factory_condition_mismatch_is_rejected_before_construction(tmp_path, requested):
    other = 'neither' if requested=='full' else 'full'
    factory = make_action_agent_factory(ROOT, condition=other, memory_module=original_memory_module(),
                                       controller_factory=lambda observer: pytest.fail('must not create a controller'))
    with pytest.raises(ValueError, match='matching action-gated'):
        run_manifest('unused', {}, load_config(), output_dir=tmp_path/'run', cache_root=tmp_path/'cache',
                     condition=requested, agent_factory=factory)
    assert not (tmp_path/'run').exists()


def test_full_checkpoint_cannot_seed_ablated_memory(tmp_path):
    factory = make_action_agent_factory(ROOT, condition='neither', controller_factory=lambda observer: None)
    with pytest.raises(ValueError, match='checkpoint cannot seed'):
        run_manifest('unused', {}, load_config(), output_dir=tmp_path/'run', cache_root=tmp_path/'cache',
                     condition='neither', agent_factory=factory, checkpoint={'historical':'full'})


def test_four_independent_caches_and_condition_bound_cached_qa(tmp_path):
    manifest = build_manifest(ROOT/'data/locomo10.json', 'smoke')
    cache = tmp_path/'cache'
    for condition in CONDITIONS:
        provider = Provider(); m = original_memory_module(); m.print = lambda *a, **k: None
        factory = make_action_agent_factory(ROOT, condition=condition, memory_module=m,
                    controller_factory=lambda observer: DeepSeekController(provider, observer=observer))
        options = dict(cache_root=cache, source_hashes={'test':'same-source'}, condition=condition,
                       agent_factory=factory, scorer=AuthorScorer(ROOT, dependencies=dependencies()))
        run_manifest(ROOT/'data/locomo10.json', manifest, load_config(), output_dir=tmp_path/condition, **options)
        assert len(provider.requests)==44
        before = {p: p.read_bytes() for p in cache.glob('*/*')}
        provider.requests.clear()
        run_manifest(ROOT/'data/locomo10.json', manifest, load_config(), output_dir=tmp_path/(condition+'-qa'),
                     execution_type='cached_qa', **options)
        assert len(provider.requests)==8
        assert {p: p.read_bytes() for p in before}==before
    identities = [json.loads(p.read_text()) for p in cache.glob('*/identity.json')]
    assert len(identities)==4 and {i['condition'] for i in identities}==set(CONDITIONS)
    states = {i['condition']: CacheStore(cache).load(i) for i in identities}
    assert all(not n['attributes']['links'] for c in ('neither','evolution_only') for n in states[c]['notes'])
    assert any(n['attributes']['links'] for c in ('linking_only','full') for n in states[c]['notes'])
    assert all(n['attributes']['tags']==['tag'] for n in states['neither']['notes'])
    assert states['evolution_only']['notes'][0]['attributes']['tags']==['updated']
    assert all(n['attributes']['tags']==['linked'] for n in states['linking_only']['notes'])


def test_binding_does_not_leak_between_instances_of_the_same_author_class():
    m = original_memory_module(); m.print = lambda *a, **k: None
    original = m.AgenticMemorySystem._evolve
    agents = [make_action_agent_factory(ROOT, condition=c, memory_module=m,
                controller_factory=lambda observer: None)(config=load_config(), observer=lambda e:None)
              for c in CONDITIONS]
    assert m.AgenticMemorySystem._evolve is original
    assert len({a.memory_system._evolve.__func__ for a in agents})==4
    assert [dict(a._repro_action_configuration) for a in agents]==[action_configuration(c) for c in CONDITIONS]
    with pytest.raises(TypeError): agents[0]._repro_action_configuration['strengthen']=True


@pytest.mark.parametrize('condition', CONDITIONS)
def test_rejected_positive_json_is_a_failure_not_gate_suppression(tmp_path, condition):
    class RejectedDecisionProvider(Provider):
        def complete(self, **request):
            response = super().complete(**request)
            if 'should_evolve' in request['tools'][0]['function']['parameters']['properties']:
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments'] = json.dumps({
                    'should_evolve': True, 'actions': ['strengthen', 'update_neighbor']})
            return response
    provider = RejectedDecisionProvider(); m = original_memory_module(); m.print = lambda *a, **k: None
    factory = make_action_agent_factory(ROOT, condition=condition, memory_module=m,
                controller_factory=lambda observer: DeepSeekController(provider, observer=observer))
    result = run_manifest(ROOT/'data/locomo10.json', build_manifest(ROOT/'data/locomo10.json', 'smoke'), load_config(),
                          output_dir=tmp_path/'run', cache_root=tmp_path/'cache', source_hashes={'test':'rejection'},
                          condition=condition, agent_factory=factory, scorer=AuthorScorer(ROOT, dependencies=dependencies()))
    events = [json.loads(s) for s in (tmp_path/'run/events.jsonl').read_text().splitlines()]
    outcomes = [e for e in events if e['type']=='evolution_outcome']
    assert len(outcomes)==18 and result['status']=='degraded'
    assert all(e['counter_before']==e['counter_after']==0 for e in outcomes)
    assert all(e['proposed_decision']=={'should_evolve':True,'actions':['strengthen','update_neighbor']} for e in outcomes)
    assert all(e['suppressed_actions']==[] for e in outcomes)
    assert len([e for e in result['failures'] if e['kind']=='provider_completion'])==18
    assert len([e for e in result['failures'] if e['kind']=='evolve'])==18


@pytest.mark.parametrize('condition', [None, True, [], 'other'])
def test_unknown_conditions_rejected(condition):
    with pytest.raises(ValueError): action_configuration(condition)
