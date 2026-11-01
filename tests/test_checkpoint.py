"""Portable offline BLK-014 recovery evidence; no private study artifacts required."""
import ast
import copy
from decimal import Decimal
import hashlib
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

import httpx
import numpy as np
import pytest
from sklearn.metrics.pairwise import cosine_similarity

from amem_repro import phases
from amem_repro.adapter import create_deepseek_controller
from amem_repro.adapter import DeepSeekController, AdapterError
from amem_repro.artifacts import restore_memory, snapshot_memory, CacheStore
from amem_repro.author import make_agent_factory
from amem_repro.budget import SCHEMA, BudgetStop, PhasePermit, ledger_summary
from amem_repro.checkpoint import verify_checkpoint
from amem_repro.config import DEFAULT_CONFIG, INDEX_STRING_POLICY, fingerprint, stage_output_limits
from amem_repro.manifests import build_manifest
from amem_repro.measurements import TokenCounter
from amem_repro.scoring import AuthorScorer
from test_foundation import Provider, original_memory_module
from test_scoring import dependencies
from test_adapter import Client, completion

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def parent(tmp_path, monkeypatch):
    manifest = build_manifest(ROOT / 'data/locomo10.json', 'pilot')
    sources = {'author_revision': 'frozen-test', 'files': {'adapter.py': 'unchanged'}}
    receipt = {'assets': {'tokenizer_limitation': 'offline'}, 'runtime': {'ok': True}}
    binding = {'manifest_sha256': fingerprint(manifest), 'config_sha256': fingerprint(DEFAULT_CONFIG),
               'source_sha256': fingerprint(sources), 'preflight_sha256': fingerprint(receipt),
               'condition': 'full', 'repetition': 0, 'population': 'pilot',
               'model': 'deepseek-flash', 'endpoint': 'https://api.deepseek.com/beta/chat/completions',
               'provider_contract_policy': INDEX_STRING_POLICY, 'max_output_tokens_by_stage': stage_output_limits()}
    compat = {'run_id': 'compatibility', 'binding': copy.deepcopy(binding),
              'returned_models': ['deepseek-flash'], 'system_fingerprints': ['mock-backend']}
    binding['compatibility_sha256'] = fingerprint(compat)
    auth = {'approval_id': 'parent', 'run_id': 'parent', 'phase': 'pilot', 'approved': True,
            'approved_by': 'offline only', 'approved_at': '2026-11-01T00:00:00Z', 'binding': binding,
            'limits': {'phase_usd': 10, 'max_logical_calls': 1544, 'max_attempts': 4632},
            'pricing': {'pricing_id': 'offline', 'input_per_million': .3, 'output_per_million': 1.2,
                        'max_context_tokens': 1048576, 'max_output_tokens': 4000}}
    state = {'notes': [], 'outcomes': [], 'evo_cnt': 261, 'evo_threshold': 100,
             'retriever': {'corpus': [f'stale-{i}' for i in range(263)],
                           'document_ids': {f'stale-{i}': i for i in range(263)},
                           'embeddings': np.eye(263, 384, dtype=np.float32).tolist(),
                           'embedding_dtype': 'float32'}}
    events = [{'type': 'run_start', 'source_hashes': sources, 'manifest': manifest, 'configuration': DEFAULT_CONFIG}]
    usage = {'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25}
    for i in range(263):
        state['notes'].append({'key': f'n{i}', 'index': i, 'attributes': {
            'id': f'n{i}', 'content': f'content-{i}', 'context': 'evolved-context',
            'keywords': ['kw'], 'tags': ['tag'], 'links': [1, 1] if i == 0 else [], 'timestamp': 'fixed'}})
        outcome = {'turn_id': manifest['conversations'][0]['turn_ids'][i],
                   'counter_before': max(0, i - 1), 'counter_after': min(i, 261),
                   'proposed_decision': None if i == 262 else {'should_evolve': i > 0},
                   'changed_existing_note_ids': [], 'enabled_actions': ['strengthen', 'update_neighbor'],
                   'suppressed_actions': []}
        state['outcomes'].append(outcome)
        for j, stage in enumerate(('metadata', 'shared_decision')):
            event = {'type': 'generation', 'stage': stage, 'run_id': 'parent',
                     'attempts': [{'budget_attempt_id': 2*i+j+2, 'usage': usage}], 'error_type': None}
            if i == 262 and stage == 'shared_decision':
                event.update(error_type='AdapterError', output='{"new_tags_neighborhood":[["x"]}',
                             provider_response={'choices': [{'finish_reason': 'tool_calls'}]})
            events.append(event)
        events.append({'type': 'evolution_outcome', **outcome})
    events.append({'type': 'failure', 'kind': 'evolve', 'run_id': 'parent'})
    events.append({'type': 'failure', 'kind': 'provider_contract_deviation', 'run_id': 'parent',
                   'compatibility_deviation': {'transformations': [
                       {'path':'$.suggested_connections[0]', 'original':'0', 'validation_copy':0}]}})
    identity = {'configuration': DEFAULT_CONFIG, 'source_hashes': sources,
                'dataset_sha256': manifest['dataset_sha256'], 'conversation': manifest['conversations'][0],
                'condition': 'full', 'repetition': 0, 'provider_contract_policy': INDEX_STRING_POLICY}
    directory = tmp_path / 'artifacts/runs/parent'
    directory.mkdir(parents=True)
    for name, value in {'approval.json': auth, 'preflight.json': receipt, 'run.json': {'run_id': 'parent'},
                        'summary.json': {'status': 'incomplete'},
                        'partial-memory.json': {'complete': False, 'identity': identity, 'state': state}}.items():
        phases._save(directory / name, value)
    (directory / 'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    phase = {'phase': 'pilot', 'run_id': 'parent', 'status': 'incomplete', 'usable_for_next_phase': False,
             'completed_questions': 0, 'conversation_ids': ['conv-50'], 'binding': binding,
             'budget': {'charged_or_reserved_microusd': 526*12},
             'study_budget': {'charged_or_reserved_microusd': 527*12, 'physical_attempts':527, 'logical_calls':527},
             'artifact_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}}
    phases._save(directory / 'phase.json', phase)
    monkeypatch.setattr('amem_repro.checkpoint.PARENT_PHASE_SHA256', fingerprint(phase))
    ledger = tmp_path / 'artifacts/study-budget.sqlite'
    with sqlite3.connect(ledger) as db:
        db.executescript(SCHEMA)
        db.execute('INSERT INTO phases VALUES (?,?,?,?,?,?)', ('history','history','{}','old-owner',1000000,'done'))
        db.execute('INSERT INTO phases VALUES (?,?,?,?,?,?)', ('parent', 'parent', json.dumps(auth), 'old-owner', 10000000, 'failed'))
        for i in range(526):
            db.execute('INSERT INTO logical_calls VALUES (?,?,?)', (i+2, 'parent', ('metadata','shared_decision')[i%2]))
            db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',
                       (i+2, i+2, 'parent', 'hash', 'settled', 12, 319373, json.dumps(usage)))
        db.execute('INSERT INTO logical_calls VALUES (?,?,?)',(1,'history','answer'))
        db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)',
                   (1,1,'history','hash','settled',12,319373,json.dumps(usage)))
    return NS(root=tmp_path, path=directory/'phase.json', manifest=manifest, sources=sources,
              receipt=receipt, compat=compat, auth=auth, phase=phase, state=state, ledger=ledger)


def verified(parent):
    return verify_checkpoint(parent.path, parent.root, parent.manifest, DEFAULT_CONFIG,
                             parent.sources, parent.receipt, parent.compat)


def author_module():
    m = original_memory_module()
    m.print = lambda *args, **kwargs: None
    m.np, m.cosine_similarity = np, cosine_similarity
    class Encoder:
        def encode(self, texts):
            return np.asarray([[1.0 if j == hashlib.sha256(t.encode()).digest()[0] else 0.0
                                for j in range(384)] for t in texts], dtype=np.float32)
    m.SentenceTransformer = lambda *args: Encoder()
    tree = ast.parse((ROOT/'memory_layer.py').read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SimpleEmbeddingRetriever')
    exec(compile(ast.Module(body=[cls], type_ignores=[]), 'frozen-retriever', 'exec'), m.__dict__)
    return m


def test_snapshot_and_stale_index_are_preserved_without_encoding(parent):
    checked = verified(parent)
    m = author_module()
    s = NS(memories={}, retriever=NS())
    restore_memory(s, checked['state'], note_type=m.MemoryNote)
    assert snapshot_memory(s, checked['state']['outcomes']) == parent.state
    assert s.retriever.embeddings.dtype == np.float32
    assert s.retriever.embeddings.tobytes() == np.asarray(parent.state['retriever']['embeddings'], dtype=np.float32).tobytes()
    assert s.retriever.corpus[0] != m.note_document(s.memories['n0'])


@pytest.mark.parametrize('mutation', ['artifact', 'assets', 'scientific_source', 'unknown', 'missing_ledger'])
def test_invalid_parent_rejected(parent, mutation):
    if mutation == 'artifact':
        (parent.path.parent/'partial-memory.json').write_text('{}')
    elif mutation == 'assets':
        parent.receipt = {'assets': {'different': True}}
    elif mutation == 'scientific_source':
        parent.sources = copy.deepcopy(parent.sources)
        parent.sources['files']['adapter.py'] = 'changed'
    elif mutation == 'unknown':
        with sqlite3.connect(parent.ledger) as db:
            db.execute("UPDATE attempts SET status='unknown' WHERE id=1")
    else:
        parent.ledger.unlink()
    with pytest.raises((ValueError, sqlite3.OperationalError)):
        verified(parent)


def test_approval_and_checkpoint_claim_are_one_shot(parent):
    recovered = verified(parent)
    auth = copy.deepcopy(parent.auth)
    auth.update(approval_id='child', run_id='child')
    auth['binding']['checkpoint'] = recovered['lineage']
    auth['limits'].update(max_logical_calls=1018, max_attempts=3054)
    permit = PhasePermit(auth, parent.ledger, auth['binding'])
    permit.stop('interrupted')
    auth.update(approval_id='second-child', run_id='second-child')
    with pytest.raises(BudgetStop, match='Checkpoint already claimed'):
        PhasePermit(auth, parent.ledger, auth['binding'])
    assert ledger_summary(parent.ledger)['physical_attempts'] == 527


@pytest.mark.parametrize('abort', [False, 'memory', 'question', 'postprocessing'])
def test_full_child_phase_and_composite_forecast(parent, abort):
    recovered = verified(parent)
    binding = {**parent.phase['binding'], 'checkpoint': recovered['lineage']}
    (parent.root/'data').symlink_to(ROOT/'data', target_is_directory=True)
    for name in ('config','manifests'):
        (parent.root/name).symlink_to(ROOT/name, target_is_directory=True)
    provider = Provider()
    original_complete = provider.complete
    def complete(**request):
        fields = request['tools'][0]['function']['parameters']['properties']
        if (abort == 'question' and 'answer' in fields) or (abort == 'memory' and 'should_evolve' in fields):
            response = original_complete(**request)
            response['choices'][0]['message']['tool_calls'][0]['function']['arguments'] = '{"answer":'
            return response
        return original_complete(**request)
    def controller(**kwargs):
        return create_deepseek_controller(**kwargs, http_transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=complete(**json.loads(request.content)))))
    def factory(root, **kwargs):
        return make_agent_factory(ROOT, memory_module=author_module(), **kwargs)
    original_verified = phases._verified_phase
    def receipt(path, root):
        return parent.compat if str(path) == 'unused' or Path(path).parent.name == 'compatibility' else original_verified(path, root)
    with patch.object(phases, '_phase_inputs', return_value=(DEFAULT_CONFIG, parent.manifest, parent.sources, binding)), \
         patch.object(phases, '_verified_phase', side_effect=receipt), \
         patch('amem_repro.adapter.create_deepseek_controller', side_effect=controller), \
         patch('amem_repro.author.make_agent_factory', side_effect=factory), \
         patch.object(phases, 'make_token_counter', return_value=TokenCounter(str.split, 'offline', 'test')), \
         patch('amem_repro.scoring.AuthorScorer', side_effect=lambda root: AuthorScorer(ROOT, dependencies=dependencies())), \
         patch.dict('os.environ', {'DEEPSEEK_API_KEY':'offline-placeholder'}):
        proposal = phases.plan_phase('pilot', parent.receipt, parent.root/'assets', root=parent.root,
                                    compatibility='unused', checkpoint=parent.path, run_id='child',
                                    provider_contract_policy=INDEX_STRING_POLICY)
        assert proposal['limits']['max_logical_calls'] == 1018
        with pytest.raises(BudgetStop, match='approval'):
            phases.execute_phase(proposal, parent.receipt, parent.root/'assets', root=parent.root,
                                 compatibility='unused', checkpoint=parent.path)
        proposal.update(approved=True, approved_by='offline only', approved_at='2026-11-01T00:00:00Z')
        if abort:
            from amem_repro.scoring import rescore_records
            def rescore(*args):
                if abort == 'postprocessing':
                    raise RuntimeError('offline postprocessing failure')
                return rescore_records(*args)
            with patch('amem_repro.scoring.rescore_records', side_effect=rescore):
                with pytest.raises((BudgetStop, RuntimeError, AdapterError)):
                    phases.execute_phase(proposal, parent.receipt, parent.root/'assets', root=parent.root,
                                         compatibility='unused', checkpoint=parent.path)
            child = parent.root/'artifacts/runs/child'
            result = json.loads((child/'phase.json').read_text())
            assert result['status'] == 'incomplete'
            assert result['usable_for_next_phase'] is False
            summary = json.loads((child/'summary.json').read_text())
            assert any(e.get('origin_run_id')=='parent' and e['kind']=='evolve' for e in summary['failures'])
            assert result['inherited_provider_contract_deviation_count']==1
            assert result['inherited_validation_copy_transformed_item_count']==1
            assert json.loads(parent.path.read_text())==parent.phase
            return
        result = phases.execute_phase(proposal, parent.receipt, parent.root/'assets', root=parent.root,
                                      compatibility='unused', checkpoint=parent.path)
        assert result['status'] == 'degraded'
        assert result['usable_for_next_phase'] is True
        assert result['budget']['logical_calls'] == 1018
        assert result['study_budget']['physical_attempts'] == 1545
        assert result['completed_questions'] == 204
        child = parent.root/'artifacts/runs/child'
        events = [json.loads(line) for line in (child/'events.jsonl').read_text().splitlines()]
        assert len([e for e in events if e['type']=='evolution_outcome']) == 305
        questions = [e['question_id'] for e in events if e['type']=='question_result']
        assert questions == [q['question_id'] for q in parent.manifest['conversations'][0]['questions']]
        inherited = [e for e in events if e.get('inherited_from')=='checkpoint']
        assert len(inherited)==2 and inherited[0]['kind']=='evolve'
        assert result['inherited_provider_contract_deviation_count']==1
        assert result['inherited_validation_copy_transformed_item_count']==1
        views=json.loads((child/'scoring-views.json').read_text())
        assert len(views)==2
        cache_identity=next((parent.root/'artifacts/cache').glob('*/identity.json'))
        saved=CacheStore(parent.root/'artifacts/cache').load(json.loads(cache_identity.read_text()))
        assert [n['key'] for n in saved['notes'][:263]]==[n['key'] for n in parent.state['notes']]
        assert saved['outcomes'][:263]==parent.state['outcomes']
        from amem_repro.runner import run_manifest
        cached_provider=Provider()
        cached_factory=make_agent_factory(ROOT,memory_module=author_module(),
            controller_factory=lambda observer:DeepSeekController(cached_provider,observer=observer,
                                                                 provider_contract_policy=INDEX_STRING_POLICY))
        cached=run_manifest(parent.root/'data/locomo10.json',parent.manifest,DEFAULT_CONFIG,
                            output_dir=parent.root/'artifacts/runs/cached-qa',
                            cache_root=parent.root/'artifacts/cache',source_hashes=parent.sources,
                            execution_type='cached_qa',checkpoint=recovered,agent_factory=cached_factory,
                            scorer=AuthorScorer(ROOT,dependencies=dependencies()),
                            provider_contract_policy=INDEX_STRING_POLICY)
        assert cached['completed_questions']==204 and cached['status']=='degraded'
        assert len(cached_provider.requests)==408
        assert all('should_evolve' not in request['tools'][0]['function']['parameters']['properties']
                   for request in cached_provider.requests)
        with patch.object(phases, 'source_fingerprint', return_value=parent.sources):
            forecast=phases.forecast_pilot(child/'phase.json',root=parent.root,provider_contract_policy=INDEX_STRING_POLICY)
        assert forecast['pilot_credited_once'] is True
        assert forecast['pilot_stage_usage']['shared_decision']['logical_calls']==568
        assert Decimal(forecast['incurred_or_reserved_usd'])==Decimal(ledger_summary(parent.ledger)['charged_or_reserved_usd'])
    assert json.loads(parent.path.read_text())==parent.phase


@pytest.mark.parametrize('counter', [99, 299])
def test_interrupted_author_construction_matches_uninterrupted_at_consolidation(counter):
    m = author_module()
    decision = json.dumps({'should_evolve': True, 'actions': ['strengthen', 'update_neighbor'],
                          'suggested_connections': [0], 'tags_to_update': ['new'],
                          'new_context_neighborhood': ['changed'], 'new_tags_neighborhood': [['changed']]})
    malformed = '{"new_tags_neighborhood":[["x"]}'
    baseline_prompts, restored_prompts = [], []
    def make(outputs, prompts):
        outputs=iter(outputs)
        def generate(prompt, **kwargs):
            prompts.append(prompt)
            return next(outputs)
        m.LLMController=lambda *a,**k:NS(llm=NS(get_completion=generate))
        return m.AgenticMemorySystem()
    def add(system, index):
        system.add_note(f'note {index}',time='fixed',id=f'n{index}',keywords=['kw'],context='initial',
                        tags=['initial'],category='fixture',last_accessed='fixed')
    live=make([malformed,decision,decision],baseline_prompts)
    live.evo_cnt=counter
    add(live,0)
    assert live.evo_cnt==counter and dict(m.FAILURES)=={'evolve':1}
    checkpoint=snapshot_memory(live)
    loaded=make([decision,decision],restored_prompts)
    restore_memory(loaded,checkpoint,note_type=m.MemoryNote)
    for index in (1,2):
        add(live,index)
        add(loaded,index)
    assert baseline_prompts[1:]==restored_prompts
    assert snapshot_memory(live)==snapshot_memory(loaded)
    assert loaded.evo_cnt==counter+2
    assert live.find_related_memories_raw('q',10)==loaded.find_related_memories_raw('q',10)


def test_normal_finish_malformed_inner_json_remains_strict():
    from amem_repro.contracts import load_author_contracts
    raw='{"new_tags_neighborhood":[["x"]}'
    client=Client(completion(raw))
    events=[]
    with pytest.raises(AdapterError):
        DeepSeekController(client,observer=events.append,provider_contract_policy=INDEX_STRING_POLICY).get_completion(
            'original prompt',load_author_contracts()['shared_decision'])
    assert len(client.requests)==1 and events[0]['output']==raw
    assert events[0]['compatibility_deviation'] is None


def test_rehashed_parent_tampering_cannot_change_frozen_checkpoint(parent):
    path=parent.path.parent/'partial-memory.json'
    value=json.loads(path.read_text())
    value['state']['notes'][0]['attributes']['context']='silently repaired'
    path.write_text(json.dumps(value))
    phase=copy.deepcopy(parent.phase)
    phase['artifact_sha256']['partial-memory.json']=hashlib.sha256(path.read_bytes()).hexdigest()
    parent.path.write_text(json.dumps(phase))
    with pytest.raises(ValueError,match='frozen BLK-014'):
        verified(parent)


def test_recovery_permit_cannot_exceed_remaining_request_limit(parent):
    auth=copy.deepcopy(parent.auth)
    auth.update(run_id='child',approval_id='child')
    auth['binding']['checkpoint']=verified(parent)['lineage']
    auth['limits'].update(max_logical_calls=1019,max_attempts=3057)
    with pytest.raises(BudgetStop,match='Checkpoint request limits'):
        PhasePermit(auth,parent.ledger,auth['binding'])
    assert ledger_summary(parent.ledger)['physical_attempts']==527


def test_removing_earlier_failed_phase_cannot_reset_recovery_spending(parent):
    with sqlite3.connect(parent.ledger) as db:
        db.execute("DELETE FROM attempts WHERE approval_id='history'")
        db.execute("DELETE FROM logical_calls WHERE approval_id='history'")
        db.execute("DELETE FROM phases WHERE approval_id='history'")
    with pytest.raises(ValueError,match='historical study charges'):
        verified(parent)


def test_later_spending_cannot_mask_missing_historical_charges(parent):
    with sqlite3.connect(parent.ledger) as db:
        db.execute("DELETE FROM attempts WHERE approval_id='history'")
        db.execute("DELETE FROM logical_calls WHERE approval_id='history'")
        db.execute("INSERT INTO logical_calls VALUES (528,'history','answer')")
        db.execute("INSERT INTO attempts VALUES (528,528,'history','later','settled',1000,1000,'{}')")
    with pytest.raises(ValueError,match='Historical ledger prefix'):
        verified(parent)


def test_only_reviewed_support_migration_is_allowed(parent):
    parent.sources=copy.deepcopy(parent.sources)
    parent.sources['files']['amem_repro/checkpoint.py']='new-support-code'
    assert verified(parent)['lineage']['migrated_files']==['amem_repro/checkpoint.py']
