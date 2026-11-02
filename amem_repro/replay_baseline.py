"""Offline audit of the saved conv-50 lineage with the frozen author implementation.

Requires the local immutable T5 artifacts and pinned assets. Produces separate replay
artifacts; never opens a paid permit or writes the study ledger/baseline caches.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import redirect_stdout
import hashlib
import json
from pathlib import Path

from .artifacts import CacheStore, snapshot_memory
from .config import AUTHOR_REVISION, fingerprint, load_config, source_fingerprint
from .checkpoint import _read_archive
from .phases import _verified_phase, _deny_network, _asset_environment, _save
from .replay import ReplayController, ReplayMismatch, memory_view
from .runner import run_manifest

ROOT = Path(__file__).resolve().parents[1]


def require_equal(actual, expected, label):
    if actual != expected:
        raise ReplayMismatch(f'Baseline replay differs: {label}')


def load_lineage(root=ROOT):
    root = Path(root)
    parent_dir = root / 'artifacts/runs/pilot-conv50-d9a'
    child_dir = root / 'artifacts/runs/pilot-conv50-checkpoint-child'
    _, parent = _read_archive(parent_dir / 'phase.json', root)
    child = _verified_phase(child_dir / 'phase.json', root)
    require_equal(child['binding']['checkpoint']['parent_phase_sha256'], fingerprint(parent), 'parent receipt')
    def events(directory):
        return [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    old, new = events(parent_dir), events(child_dir)
    start = new[0]
    config, manifest = start['configuration'], start['manifest']
    require_equal(config, load_config(root / 'config/study.json'), 'configuration')
    require_equal(hashlib.sha256((root / 'data/locomo10.json').read_bytes()).hexdigest(),
                  manifest['dataset_sha256'], 'dataset')
    current = source_fingerprint(root)
    # T6 may add replay code/runner mode. Existing author, provider, scorer and
    # assets remain pinned; an algorithm/contract change cannot redefine this oracle.
    for name, digest in start['source_hashes']['files'].items():
        if name != 'amem_repro/runner.py':
            require_equal(current['files'].get(name), digest, f'source {name}')
    records = [e for e in old + new if e['type'] == 'generation' and e.get('attempts')]
    require_equal(len(records), 1544, 'generation coverage')
    require_equal(sum(bool(e.get('error_type')) for e in records), 1, 'rejected decision count')
    expected_outcomes = [e for e in old + new if e['type'] == 'evolution_outcome']
    partial = json.loads((parent_dir / 'partial-memory.json').read_text())['state']
    build_id = next(e['build_id'] for e in new if e['type'] == 'build_complete')
    cache = root / 'artifacts/cache' / build_id
    identity = json.loads((cache / 'identity.json').read_text())
    final = CacheStore(root / 'artifacts/cache').load(identity)
    require_equal(identity['source_hashes'], start['source_hashes'], 'cache source')
    require_equal(identity['checkpoint'], child['binding']['checkpoint'], 'cache lineage')
    return dict(parent=parent, child=child, records=records, outcomes=expected_outcomes,
                partial=partial, final=final, config=config, manifest=manifest,
                questions=[e['result'] for e in new if e['type'] == 'question_result'],
                retrieval=[e for e in new if e['type'] == 'retrieval'],
                views=json.loads((child_dir / 'scoring-views.json').read_text()),
                preflight=json.loads((child_dir / 'preflight.json').read_text()))


def replay_baseline(asset_root, output, *, root=ROOT, factory_builder=None, oracle_path=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists() or any(output.is_relative_to(root / p) for p in ('artifacts/runs', 'artifacts/cache')):
        raise ValueError('Use a fresh separate replay output directory')
    baseline = load_lineage(root)
    oracle_path = Path(oracle_path) if oracle_path is not None else root / 'tests/fixtures/conv50-replay-state-hashes.json'
    oracle = json.loads(oracle_path.read_text())
    require_equal(oracle['author_revision'], AUTHOR_REVISION, 'oracle author revision')
    require_equal(oracle['dataset_sha256'], baseline['manifest']['dataset_sha256'], 'oracle dataset')
    require_equal(oracle['parent_phase_sha256'], fingerprint(baseline['parent']), 'oracle parent')
    require_equal(oracle['child_phase_sha256'], fingerprint(baseline['child']), 'oracle child')
    require_equal(len(oracle['per_insertion_comparison_hashes']), 568, 'oracle coverage')
    protected = [root / 'artifacts/study-budget.sqlite']
    for directory in ('pilot-conv50-d9a', 'pilot-conv50-checkpoint-child'):
        protected.extend((root / 'artifacts/runs' / directory).iterdir())
    build_id = next(e['build_id'] for e in baseline['retrieval'])
    protected.extend((root / 'artifacts/cache' / build_id).iterdir())
    original_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected if path.is_file()}
    # Import heavyweight local dependencies only inside the network-denied context.
    with _deny_network(), _asset_environment(asset_root):
        from .preflight import verify_asset_report, make_token_counter
        from .author import make_agent_factory
        from .scoring import AuthorScorer, rescore_records
        verify_asset_report(baseline['preflight']['assets'], asset_root, root / 'config/assets.json')
        counter = make_token_counter(asset_root, baseline['preflight']['assets'], root / 'config/assets.json')
        replay = ReplayController(baseline['records'], provider_contract_policy=baseline['child']['provider_contract_policy'])
        agent_holder, outcomes, traces, retrieval, consolidations = [], [], [], [], []
        expected_ids = {note['key']: f'note:{i}' for i, note in enumerate(baseline['final']['notes'])}

        def controller(observer):
            replay.observer = observer
            return replay

        original_factory = (factory_builder or make_agent_factory)(
            root, controller_factory=controller, token_counter=counter)
        def factory(**kwargs):
            agent = original_factory(**kwargs)
            system = agent.memory_system
            original_consolidate = system.consolidate_memories
            def consolidate():
                consolidations.append({'notes': len(system.memories), 'counter': system.evo_cnt})
                return original_consolidate()
            system.consolidate_memories = consolidate
            agent_holder.append(agent)
            return agent

        def observe(event):
            if event['type'] == 'evolution_outcome':
                expected = baseline['outcomes'][len(outcomes)]
                keys = baseline['final']['outcomes'][0].keys()
                actual = {k: event[k] for k in keys}
                outcomes.append(actual)
                system = agent_holder[0].memory_system
                ids = {key: f'note:{i}' for i, key in enumerate(system.memories)}
                a, b = copy.deepcopy(actual), {k: copy.deepcopy(expected[k]) for k in keys}
                a['changed_existing_note_ids'] = [ids[key] for key in a['changed_existing_note_ids']]
                b['changed_existing_note_ids'] = [expected_ids[key] for key in b['changed_existing_note_ids']]
                require_equal(a, b, f'evolution outcome {len(outcomes)}')
                state = snapshot_memory(system, outcomes)
                traces.append(fingerprint(memory_view(state)))
                require_equal(traces[-1], oracle['per_insertion_comparison_hashes'][len(outcomes)-1],
                              f'T6 comparison-state oracle {len(outcomes)}')
                if len(outcomes) in (263, 568):
                    reference = baseline['partial'] if len(outcomes) == 263 else baseline['final']
                    require_equal(memory_view(state), memory_view(reference), f'memory checkpoint {len(outcomes)}')
            elif event['type'] == 'retrieval':
                expected = baseline['retrieval'][len(retrieval)]
                for key in ('initial_count', 'expanded_count', 'context_tokens', 'token_count_method',
                            'tokenizer_revision', 'token_count_exact', 'token_count_error'):
                    require_equal(event[key], expected[key], f'retrieval {key}')
                retrieval.append(event)
            elif event['type'] == 'question_result':
                expected = baseline['questions'][len(retrieval) - 1]
                require_equal(event['result'], expected, f'question {expected["question_id"]}')

        output.mkdir(parents=True)
        try:
            with (output / 'author-output.log').open('x') as log, redirect_stdout(log):
                scorer = AuthorScorer(root)
                summary = run_manifest(
                    root / 'data/locomo10.json', baseline['manifest'], baseline['config'],
                    output_dir=output / 'run', cache_root=output / 'cache',
                    source_hashes=source_fingerprint(root), agent_factory=factory, scorer=scorer,
                    observer=observe, execution_type='deterministic_replay',
                    run_id='conv50-deterministic-replay',
                    provider_contract_policy=baseline['child']['provider_contract_policy'])
                replay.finish()
                expected_consolidations = [
                    {'notes': i+1, 'counter': e['counter_after']}
                    for i, e in enumerate(baseline['outcomes'])
                    if e['counter_after'] > e['counter_before'] and e['counter_after'] % 100 == 0]
                require_equal(consolidations, expected_consolidations, 'consolidation events')
                scorer.observer = None
                views = rescore_records(baseline['questions'], scorer)
                require_equal(views, baseline['views'], 'both author scoring views')
                for path, digest in original_hashes.items():
                    require_equal(hashlib.sha256(path.read_bytes()).hexdigest(), digest, f'protected evidence {path.name}')
            result = {'execution_type': 'deterministic_replay', 'network_disabled': True,
                      'paid_calls': 0, 'recorded_calls': replay.position, 'turns': len(outcomes),
                      'questions': summary['completed_questions'], 'status': summary['status'],
                      'consolidations': consolidations,
                      'parent_phase_sha256': fingerprint(baseline['parent']),
                      'child_phase_sha256': fingerprint(baseline['child']),
                      'per_insertion_comparison_hashes': traces,
                      'normalisation': 'UUID identities by insertion index and last_accessed only',
                      'historical_full_state_checkpoints': [263, 568],
                      'protected_baseline_files_and_ledger_unchanged': True,
                      'all_recorded_outcomes_requests_retrieval_predictions_scores_exact': True}
            _save(output / 'verification.json', result)
            return result
        except BaseException as error:
            _save(output / 'failure.json', {'error_type': type(error).__name__,
                    'message': str(error), 'consumed_records': replay.position, 'turns': len(outcomes)})
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--oracle', default=str(ROOT / 'tests/fixtures/conv50-replay-state-hashes.json'))
    args = parser.parse_args()
    result = replay_baseline(args.assets, args.output, oracle_path=args.oracle)
    print(json.dumps({k: v for k, v in result.items() if k != 'per_insertion_comparison_hashes'}))


if __name__ == '__main__':
    main()
