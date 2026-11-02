"""T6 portable regression gate: captured opening calls + labelled synthetic edge cases."""
import copy
import json
import random
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

import pytest

from amem_repro.adapter import DeepSeekController, AdapterError
from amem_repro.artifacts import snapshot_memory, restore_memory
from amem_repro.author import make_agent_factory
from amem_repro.config import load_config
from amem_repro.contracts import load_author_contracts
from amem_repro.replay import ReplayController, ReplayMismatch, memory_view
from test_adapter import Client, completion
from test_foundation import original_memory_module
from test_scoring import dependencies
from amem_repro.scoring import AuthorScorer

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'canonical-index-strings-v1'
FIXTURE = ROOT / 'tests/fixtures/conv50-opening-replay.json'


def opening():
    return json.loads(FIXTURE.read_text())


def synthetic_record(stage, value, *, temperature=.7, raw=None):
    """Explicit synthetic provider fixture, never presented as historical output."""
    contract = load_author_contracts()[stage]
    raw = json.dumps(value) if raw is None else raw
    response = completion(raw)
    client, observed = Client(response), []
    try:
        DeepSeekController(client, observer=observed.append, provider_contract_policy=POLICY).get_completion(
            f'synthetic {stage}', contract, temperature)
    except AdapterError:
        pass
    record = observed[0]
    wire = copy.deepcopy(client.requests[0])
    wire.update(wire.pop('extra_body'))
    record.update(type='generation', attempts=[{'request_body': wire}])
    return record


def replay_record(replay, record):
    return replay.get_completion(record['prompt'], record['response_format'], record['temperature'])


def test_captured_opening_responses_match_each_insertion_golden_state():
    fixture = opening()
    originals = copy.deepcopy(fixture)
    replay = ReplayController(fixture['records'], provider_contract_policy=POLICY)
    m = original_memory_module()
    m.print = lambda *a, **k: None
    factory = make_agent_factory(ROOT, memory_module=m, controller_factory=lambda observer: replay)
    agent = factory(config=load_config(), observer=lambda e: None)
    for turn, expected in zip(fixture['turns'], fixture['comparison_states']):
        agent.add_memory(turn['content'], time=turn['timestamp'])
        assert memory_view(snapshot_memory(agent.memory_system)) == expected
    replay.finish()
    assert fixture == originals
    assert replay.position == 4
    assert replay.observations[-1]['compatibility_deviation']['transformations'] == [
        {'path': '$.suggested_connections[0]', 'original': '0', 'validation_copy': 0}]
    # The first note's changed context/tags do not refresh its old corpus row.
    assert agent.memory_system.memories[next(iter(agent.memory_system.memories))].context not in agent.memory_system.retriever.corpus[0]


@pytest.mark.parametrize('field,value', [
    ('prompt', 'different prompt'), ('temperature', .5), ('stage', 'answer'),
    ('response_format', {'type': 'json_object'}), ('max_tokens', 1),
    ('thinking', 'enabled'), ('model', 'another-model'), ('endpoint', 'https://elsewhere'),
    ('provider_contract_policy', 'strict-original-v1'),
])
def test_record_or_call_mismatch_latches_without_consuming_another_response(field, value):
    record = opening()['records'][0]
    modified = copy.deepcopy(record)
    modified[field] = value
    replay = ReplayController([modified], provider_contract_policy=POLICY)
    with pytest.raises(ReplayMismatch):
        replay_record(replay, record)
    position = replay.position
    with pytest.raises(ReplayMismatch):
        replay_record(replay, modified)
    assert replay.position == position


@pytest.mark.parametrize('field,value', [('max_tokens', 1001), ('thinking', {'type': 'enabled'}),
                                       ('model','another-model'), ('stream',True)])
def test_wire_generation_settings_mismatch_is_terminal(field, value):
    record = copy.deepcopy(opening()['records'][0])
    record['attempts'][0]['request_body'][field] = value
    replay = ReplayController([record], provider_contract_policy=POLICY)
    with pytest.raises(ReplayMismatch, match='wire'):
        replay_record(replay, record)
    assert replay.position == 0


def test_replay_exhaustion_missing_extra_and_reordered_requests():
    records = opening()['records']
    r = ReplayController(records, provider_contract_policy=POLICY)
    with pytest.raises(ReplayMismatch, match='missing'):
        r.finish()
    r = ReplayController(records, provider_contract_policy=POLICY)
    with pytest.raises(ReplayMismatch):
        replay_record(r, records[1])
    assert r.position == 0
    r = ReplayController(records[:1], provider_contract_policy=POLICY)
    assert replay_record(r, records[0]) == records[0]['output']
    r.finish()
    with pytest.raises(ReplayMismatch, match='exhaustion'):
        replay_record(r, records[0])


def decision(actions, positive=True):
    return {'should_evolve': positive, 'actions': actions, 'suggested_connections': ['0',0],
            'tags_to_update':['linked'], 'new_context_neighborhood':['updated-context'],
            'new_tags_neighborhood':[['updated-tag']]}


def bind_synthetic_decision(system, record, content, context):
    record=copy.deepcopy(record)
    neighbors,indices=system.find_related_memories(content,k=5)
    prompt=system.evolution_system_prompt.format(context=context,content=content,keywords=['kw'],
                nearest_neighbors_memories=neighbors,neighbor_number=len(indices))
    record['prompt']=prompt
    record['attempts'][0]['request_body']['messages'][1]['content']=prompt
    replay=ReplayController([record],provider_contract_policy=POLICY)
    system.llm_controller.llm=replay
    return replay


@pytest.mark.parametrize('actions', [[], ['strengthen'], ['update_neighbor'], ['strengthen','update_neighbor']])
@pytest.mark.parametrize('positive', [False, True])
@pytest.mark.parametrize('counter', [0, 99])
def test_original_action_decisions_and_counter_continuity(actions, positive, counter):
    record = synthetic_record('shared_decision', decision(actions, positive))
    m = original_memory_module()
    m.print = lambda *a,**k:None
    # Original algorithm, synthetic local embedding boundary; metadata is explicitly supplied.
    m.LLMController = lambda *a,**k:NS(llm=None)
    s = m.AgenticMemorySystem()
    old = m.MemoryNote('old', id='old', keywords=['kw'], context='old-context',tags=['old-tag'],timestamp='fixed')
    s.memories[old.id]=old
    s.retriever.add_documents([m.note_document(old)])
    s.evo_cnt=counter
    replay=bind_synthetic_decision(s,record,'new','new-context')
    calls=[];original_consolidate=s.consolidate_memories
    def consolidate():
        calls.append(s.evo_cnt)
        return original_consolidate()
    s.consolidate_memories=consolidate
    s.add_note('new',time='fixed',id='new',keywords=['kw'],context='new-context',tags=['initial'],category='fixture')
    replay.finish()
    assert s.evo_cnt==counter+int(positive)
    assert calls==([100] if positive and counter==99 else [])
    assert s.memories['new'].links==([0,0] if positive and 'strengthen' in actions else [])
    assert s.memories['new'].tags==(['linked'] if positive and 'strengthen' in actions else ['initial'])
    assert old.context==('updated-context' if positive and 'update_neighbor' in actions else 'old-context')
    assert old.tags==(['updated-tag'] if positive and 'update_neighbor' in actions else ['old-tag'])
    if positive and counter==99:
        assert s.retriever.corpus==[f'{n.content} , {n.context} {" ".join(n.keywords)} {" ".join(n.tags)}' for n in s.memories.values()]
    else:
        assert s.retriever.corpus[0]=='content:old context:old-context keywords: kw tags: old-tag'
    # Linked neighbours, including duplicates, remain expanded by the author.
    context=s.find_related_memories_raw('q',k=10)
    assert context.count('memory content: old')==(3 if positive and 'strengthen' in actions else 1)
    saved=snapshot_memory(s)
    restored=NS(retriever=NS())
    restore_memory(restored,saved,note_type=m.MemoryNote)
    assert snapshot_memory(restored)==saved


def test_recorded_rejection_and_original_fallback_are_not_repaired():
    raw='{"new_tags_neighborhood":[["x"]}'
    record=synthetic_record('shared_decision',None,raw=raw)
    m=original_memory_module();m.print=lambda *a,**k:None
    m.LLMController=lambda *a,**k:NS(llm=None)
    s=m.AgenticMemorySystem();s.evo_cnt=99
    replay=bind_synthetic_decision(s,record,'stored unevolved','original')
    s.add_note('stored unevolved',time='fixed',id='new',keywords=['kw'],context='original',tags=['original'],category='fixture')
    replay.finish()
    assert s.evo_cnt==99 and dict(m.FAILURES)=={'evolve':1}
    assert s.memories['new'].links==[] and s.memories['new'].context=='original'
    assert replay.observations[0]['output']==raw
    assert replay.observations[0]['error_type']=='AdapterError'


def test_mismatch_escapes_original_broad_failure_handler():
    replay=ReplayController(opening()['records'],provider_contract_policy=POLICY)
    m=original_memory_module();m.print=lambda *a,**k:None
    m.LLMController=lambda *a,**k:NS(llm=replay)
    s=m.AgenticMemorySystem()
    with pytest.raises(ReplayMismatch):
        s.add_note('unexpected memory',time='fixed')
    assert not s.memories


def test_answer_strings_original_scoring_and_no_network_or_credentials():
    records=[synthetic_record('query_keywords',{'keywords':'kw'}),synthetic_record('answer',{'answer':'Paris'})]
    replay=ReplayController(records,provider_contract_policy=POLICY)
    with patch('socket.create_connection',side_effect=AssertionError('network forbidden')), \
         patch('os.getenv',side_effect=AssertionError('credentials forbidden')):
        assert replay_record(replay,records[0])==records[0]['output']
        raw=replay_record(replay,records[1]);replay.finish()
    scorer=AuthorScorer(ROOT,dependencies=dependencies())
    qa=scorer.qa({'question':'Where?','answer':'Paris','category':1})
    reference,metrics=scorer.score(json.loads(raw)['answer'],qa)
    assert reference=='Paris' and metrics['f1']==metrics['exact_match']==1
    assert metrics['bleu1']==.4  # Existing deterministic dependency stub, not historical BLEU.


@pytest.mark.parametrize('category',[1,2,3,4,5])
def test_original_question_prompt_prediction_and_scoring_replay(category):
    answer='Not mentioned in the conversation' if category==5 else 'Paris'
    class QuestionClient(Client):
        def create(self, **request):
            self.response=completion(json.dumps({'keywords':'kw'} if 'keywords' in
                request['tools'][0]['function']['parameters']['properties'] else {'answer':answer}))
            return super().create(**request)
    client=QuestionClient(None);observed=[]
    recording=DeepSeekController(client,observer=observed.append,provider_contract_policy=POLICY)
    factory=make_agent_factory(ROOT,memory_module=original_memory_module(),controller_factory=lambda observer:recording)
    agent=factory(config=load_config(),observer=lambda e:None)
    expected=agent.answer_question('Where?',category,'Paris',random.Random(42))
    records=[]
    for e,request in zip(observed,client.requests):
        wire=copy.deepcopy(request);wire.update(wire.pop('extra_body'))
        records.append({**e,'type':'generation','attempts':[{'request_body':wire}]})
    replay=ReplayController(records,provider_contract_policy=POLICY)
    factory=make_agent_factory(ROOT,memory_module=original_memory_module(),controller_factory=lambda observer:replay)
    actual=factory(config=load_config(),observer=lambda e:None).answer_question('Where?',category,'Paris',random.Random(42))
    replay.finish()
    assert actual==expected
    scorer=AuthorScorer(ROOT,dependencies=dependencies())
    qa=scorer.qa({'question':'Where?','answer':'Paris','adversarial_answer':'Paris','category':category})
    assert scorer.score(json.loads(actual[0])['answer'],qa)==scorer.score(json.loads(expected[0])['answer'],qa)


def test_comparison_views_preserve_scientific_differences_and_raw_evidence():
    state=opening()['comparison_states'][-1]
    raw=copy.deepcopy(state);changed=copy.deepcopy(state)
    changed['notes'][0]['attributes']['last_accessed']='incidental'
    assert memory_view(changed)==memory_view(raw)
    for mutate in [lambda s:s['notes'][1]['attributes']['links'].append(0),
                   lambda s:s['notes'][0]['attributes']['tags'].reverse(),
                   lambda s:s['notes'][0]['attributes'].__setitem__('timestamp','different date'),
                   lambda s:s['retriever']['embeddings'][0].__setitem__(0,.99999999),
                   lambda s:s['retriever']['corpus'].reverse()]:
        changed=copy.deepcopy(raw);mutate(changed)
        assert memory_view(changed)!=memory_view(raw)
    assert state==raw


def test_replay_execution_mode_cannot_construct_a_paid_default_factory(tmp_path):
    from amem_repro.runner import run_manifest
    with patch('amem_repro.author.make_agent_factory', side_effect=AssertionError('paid factory forbidden')):
        with pytest.raises(PermissionError,match='explicit offline'):
            run_manifest(tmp_path/'data.json',{},load_config(),output_dir=tmp_path/'run',
                         cache_root=tmp_path/'cache',paid_authorized=True,execution_type='deterministic_replay')


def test_full_replay_refuses_existing_or_protected_output_directories(tmp_path):
    from amem_repro.replay_baseline import replay_baseline
    for directory in (tmp_path, ROOT/'artifacts/runs/forbidden-replay', ROOT/'artifacts/cache/forbidden-replay'):
        with pytest.raises(ValueError,match='fresh separate'):
            replay_baseline('unused-assets',directory)


def test_pinned_state_hash_oracle_identifies_derived_not_historical_states():
    oracle=json.loads((ROOT/'tests/fixtures/conv50-replay-state-hashes.json').read_text())
    assert 'not historical' in oracle['oracle_kind']
    assert len(oracle['per_insertion_comparison_hashes'])==568
    assert all(len(digest)==64 for digest in oracle['per_insertion_comparison_hashes'])


def test_extra_generation_arguments_latch_even_after_consuming_all_records():
    record=opening()['records'][0]
    replay=ReplayController([record],provider_contract_policy=POLICY)
    replay_record(replay,record)
    with pytest.raises(ReplayMismatch,match='unsupported generation'):
        replay.get_completion(record['prompt'],record['response_format'],max_tokens=1000)
    with pytest.raises(ReplayMismatch):
        replay.finish()
