"""Offline audit of the saved conv-50 lineage with the frozen author implementation.

Requires the local immutable T5 artifacts and pinned assets. Produces separate replay
artifacts; never opens a paid permit or writes the study ledger/baseline caches.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import redirect_stdout
from functools import wraps
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .artifacts import CacheStore, snapshot_memory
from .config import AUTHOR_REVISION, UPSTREAM_README, fingerprint, load_config, source_fingerprint, stage_output_limits
from .checkpoint import _read_archive
from .phases import _verified_phase, _deny_network, _asset_environment, _save
from .replay import ReplayController, ReplayMismatch, memory_view, failure_view
from .runner import run_manifest

ROOT = Path(__file__).resolve().parents[1]

# The existing T5 support files changed by reviewed T8/Run2 execution safeguards,
# the explicit generation profile and passive observation. No author, contract,
# scorer, asset or original study-configuration pin is exempted.
REVIEWED_SUPPORT_FILES = frozenset({
    'amem_repro/adapter.py', 'amem_repro/artifacts.py', 'amem_repro/author.py',
    'amem_repro/budget.py', 'amem_repro/checkpoint.py', 'amem_repro/config.py',
    'amem_repro/measurements.py', 'amem_repro/phases.py', 'amem_repro/reporting.py',
    'amem_repro/runner.py',
})
RUN1_OUTPUT_LIMITS = {'metadata': 1000, 'shared_decision': 4000,
                      'query_keywords': 1000, 'answer': 1000}


def require_equal(actual, expected, label):
    if actual != expected:
        raise ReplayMismatch(f'Baseline replay differs: {label}')


def require_failure_evidence(summary, expected):
    require_equal(summary['status'], 'degraded', 'failure classification')
    require_equal(failure_view(summary['failures']), failure_view(expected), 'failure evidence')


def verify_replay_sources(root, archived, current, *, support_reference=None):
    """Keep historical pins unless exact reviewed support bytes are requested.

    A caller must name a full commit SHA; branch names and current HEAD are never
    inferred. Even then all other historical pins remain authoritative and every
    current source/config file, including additions, must match that commit.
    """
    if support_reference is None:
        # Preserve T6's original runner-only exemption and strict default gate.
        for name, digest in archived['files'].items():
            if name != 'amem_repro/runner.py':
                require_equal(current['files'].get(name), digest, f'source {name}')
        return None
    if not isinstance(support_reference, str) or not re.fullmatch(r'[0-9a-f]{40}', support_reference):
        raise ReplayMismatch('Support reference must be a full immutable commit SHA')
    try:
        kind = subprocess.check_output(
            ['git', 'cat-file', '-t', support_reference], cwd=root, stderr=subprocess.DEVNULL,
            text=True).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReplayMismatch('Support reference commit is unavailable') from error
    if kind != 'commit':
        raise ReplayMismatch('Support reference must identify a commit')
    require_equal(current['author_revision'], archived['author_revision'], 'author revision')
    archived_files = archived['files'].copy()
    relocated = {}
    if 'README.md' in archived_files and UPSTREAM_README in current['files']:
        # A reviewed offline comparison can match these two physical paths to
        # the same immutable author blob. Keep the original inventory in the receipt.
        require_equal(archived['author_revision'], AUTHOR_REVISION, 'README author revision')
        require_equal(UPSTREAM_README in archived_files or 'README.md' in current['files'],
                      False, 'ambiguous upstream README paths')
        original = subprocess.check_output(['git', 'show', f'{AUTHOR_REVISION}:README.md'], cwd=root)
        require_equal(archived_files['README.md'], hashlib.sha256(original).hexdigest(), 'archived README.md')
        archived_files[UPSTREAM_README] = archived_files.pop('README.md')
        relocated['README.md'] = UPSTREAM_README
    for name, digest in archived_files.items():
        if name not in REVIEWED_SUPPORT_FILES or name not in current['files']:
            require_equal(current['files'].get(name), digest, f'source {name}')
    references = {}
    for name, digest in current['files'].items():
        try:
            blob = subprocess.check_output(
                ['git', 'show', f'{support_reference}:{name}'], cwd=root,
                stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError) as error:
            raise ReplayMismatch(f'Support reference has no source {name}') from error
        references[name] = hashlib.sha256(blob).hexdigest()
        require_equal(digest, references[name], f'support reference source {name}')
    require_equal(stage_output_limits(), RUN1_OUTPUT_LIMITS, 'Run1 output limits')
    return {
        'policy': 'explicit-reviewed-replay-support-v1',
        'reference_commit': support_reference,
        'archived_source_sha256': fingerprint(archived),
        'current_source_sha256': fingerprint(current),
        'changed_existing_files': {
            name: {'archived_sha256': digest, 'current_sha256': current['files'][name],
                   'reference_sha256': references[name]}
            for name, digest in archived_files.items() if digest != current['files'][name]},
        'added_files': {name: digest for name, digest in current['files'].items()
                        if name not in archived_files},
        **({'relocated_files': relocated} if relocated else {}),
        'all_current_sources_match_reference': True,
        'archived_critical_pins_retained': True,
        'run1_output_limits': dict(RUN1_OUTPUT_LIMITS),
    }


def load_lineage(root=ROOT, *, support_reference=None):
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
    source_migration = verify_replay_sources(
        root, start['source_hashes'], current, support_reference=support_reference)
    records = [e for e in old + new if e['type'] == 'generation' and e.get('attempts')]
    require_equal(len(records), 1544, 'generation coverage')
    require_equal(sum(bool(e.get('error_type')) for e in records), 1, 'rejected decision count')
    blocked = [e for e in old if e['type'] == 'generation' and not e.get('attempts')]
    require_equal([(e['stage'], e['error_type']) for e in blocked], [('metadata', 'BudgetStop')],
                  'excluded zero-attempt parent event')
    failures = [e for e in old + new if e['type'] == 'failure' and not e.get('from_cache')]
    excluded = [e for e in failures if e.get('kind') == 'provider_completion' and e.get('error_type') == 'BudgetStop']
    require_equal(len(excluded), 1, 'excluded parent stop notice')
    failures = [e for e in failures if e not in excluded]
    expected_outcomes = [e for e in old + new if e['type'] == 'evolution_outcome']
    partial = json.loads((parent_dir / 'partial-memory.json').read_text())['state']
    build_id = next(e['build_id'] for e in new if e['type'] == 'build_complete')
    cache = root / 'artifacts/cache' / build_id
    identity = json.loads((cache / 'identity.json').read_text())
    final = CacheStore(root / 'artifacts/cache').load(identity)
    require_equal(identity['source_hashes'], start['source_hashes'], 'cache source')
    require_equal(identity['checkpoint'], child['binding']['checkpoint'], 'cache lineage')
    return dict(parent=parent, child=child, records=records, outcomes=expected_outcomes, failures=failures,
                partial=partial, final=final, config=config, manifest=manifest,
                questions=[e['result'] for e in new if e['type'] == 'question_result'],
                retrieval=[e for e in new if e['type'] == 'retrieval'],
                views=json.loads((child_dir / 'scoring-views.json').read_text()),
                preflight=json.loads((child_dir / 'preflight.json').read_text()),
                source_migration=source_migration)


def replay_baseline(asset_root, output, *, root=ROOT, factory_builder=None, oracle_path=None,
                    support_reference=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    protected_roots = [(root / p).resolve() for p in ('artifacts/runs', 'artifacts/cache')]
    if output.exists() or any(output.is_relative_to(directory) for directory in protected_roots):
        raise ValueError('Use a fresh separate replay output directory')
    baseline = load_lineage(root, support_reference=support_reference)
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
        @wraps(original_factory)
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
                require_failure_evidence(summary, baseline['failures'])
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
                      'implementation': 't7-action-gates' if getattr(original_factory, '_repro_condition', None) else 'frozen-author',
                      'questions': summary['completed_questions'], 'status': summary['status'],
                      'consolidations': consolidations,
                      'parent_phase_sha256': fingerprint(baseline['parent']),
                      'child_phase_sha256': fingerprint(baseline['child']),
                      'per_insertion_comparison_hashes': traces,
                      'normalisation': 'UUID identities by insertion index and last_accessed only',
                      'historical_full_state_checkpoints': [263, 568],
                      'protected_baseline_files_and_ledger_unchanged': True,
                      'logical_failure_records_exact': len(summary['failures']),
                      'support_source_migration': baseline['source_migration'],
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
    parser.add_argument('--full-mode-candidate', action='store_true', help='Exercise T7 gates, both actions enabled')
    parser.add_argument('--support-reference', help='Full reviewed commit SHA for the named support-source delta')
    args = parser.parse_args()
    if args.full_mode_candidate:
        from .actions import make_action_agent_factory
    result = replay_baseline(args.assets, args.output, oracle_path=args.oracle,
                             support_reference=args.support_reference,
                             factory_builder=make_action_agent_factory if args.full_mode_candidate else None)
    print(json.dumps({k: v for k, v in result.items() if k != 'per_insertion_comparison_hashes'}))


if __name__ == '__main__':
    main()
