"""The historical failed-turn fixture is optional on a clean, public checkout."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.gpt4omini_campaign import read
from amem_repro.linking44_reconstruction import (
    CHILD, PARENT, PARENT_PATH, PARENT_SEAL, SUPPLEMENT, load_checkpoint, reconstruct,
)
from amem_repro.linking44_finance import RELEASE_PATH
from amem_repro.blk027 import sha

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / 'artifacts/gpt4omini'
PARENT_FILE = CAMPAIGN / PARENT_PATH


@pytest.mark.skipif(not PARENT_FILE.exists(), reason='requires the sealed private transport incident')
def test_offline_reconstruction_matches_independent_frozen_author_oracle(tmp_path):
    value = reconstruct(ROOT, CAMPAIGN)
    before = read(PARENT_FILE.parent / 'partial-memory.json')['state']
    after = value['state']
    assert after['notes'][:-1] == before['notes']
    assert after['outcomes'][:-1] == before['outcomes']
    assert after['retriever']['embeddings'][:-1] == before['retriever']['embeddings']
    assert len(after['notes']) == 232 and after['evo_cnt'] == 231
    assert value['lineage']['next_turn_id'] == 'D10:16'
    assert value['network_requests'] == 0
    assert set(value['newly_generated_fields']) == {'id', 'last_accessed'}
    oracle_path = CAMPAIGN / 'verification/linking44-recovery-assessment/standards-boundary-assessment.json'
    assert sha(oracle_path) == '5135fbca88cb544572ff7feb7fbb6316f3f1fa67ffd98564f421f6ae99abdadd'
    oracle = read(oracle_path)['scenarios'][0]
    comparison = copy.deepcopy(after)
    note = comparison['notes'][-1]
    note['key'] = oracle['synthetic_incidental_fields']['id']
    note['attributes'].update(oracle['synthetic_incidental_fields'])
    assert fingerprint(comparison) == oracle['derived_after_state_sha256']

    # Exercise the actual runner's first suffix boundary with transmission disabled.
    from amem_repro.actions import make_action_agent_factory
    from amem_repro.config import OPENROUTER_CONFIG, source_fingerprint
    from amem_repro.phases import _asset_environment, _deny_network
    from amem_repro.runner import run_manifest
    from amem_repro.scoring import AuthorScorer
    from test_scoring import dependencies

    calls, observed = [], []
    class StopAtFirstRequest:
        observer_errors = ()
        def get_completion(self, prompt, response_format, **kwargs):
            calls.append((prompt, response_format))
            raise BudgetStop('offline first suffix request')

    def observe(event):
        observed.append(event)
    observe.captures_lifecycle = True
    factory = make_action_agent_factory(ROOT, condition='linking_only',
                                        controller_factory=lambda _: StopAtFirstRequest())
    with _asset_environment(ROOT / 'artifacts/assets'), _deny_network():
        with pytest.raises(BudgetStop, match='offline first suffix request'):
            run_manifest(ROOT / 'data/locomo10.json', read(ROOT / 'manifests/fallback.json'),
                         OPENROUTER_CONFIG, condition='linking_only', conversation_ids=['conv-44'],
                         run_id='offline-pr48-first-suffix', source_hashes=source_fingerprint(ROOT),
                         agent_factory=factory, checkpoint=value, execution_type='checkpoint_recovery',
                         scorer=AuthorScorer(ROOT, dependencies=dependencies()), observer=observe,
                         output_dir=tmp_path / 'run', cache_root=tmp_path / 'cache')
    assert len(calls) == 1
    assert [e['turn_id'] for e in observed if e['type'] == 'memory_turn_start'] == ['D10:16']
    assert [e['newly_generated_fields'] for e in observed if e['type'] == 'checkpoint_restore'] == [
        value['newly_generated_fields']]
    assert read(tmp_path / 'run/partial-memory.json')['state'] == value['state']


def test_checkpoint_rejects_wrong_child_before_consulting_any_evidence(tmp_path):
    with pytest.raises(BudgetStop):
        load_checkpoint({'phase': 'wrong-child'}, SimpleNamespace(root=tmp_path), ROOT)


@pytest.mark.skipif(not PARENT_FILE.exists(), reason='requires the sealed private transport incident')
def test_altered_supplement_cannot_be_loaded(tmp_path):
    from shutil import copyfile
    path = tmp_path / PARENT_PATH
    path.parent.mkdir(parents=True)
    copyfile(PARENT_FILE, path)
    supplement = tmp_path / SUPPLEMENT
    supplement.parent.mkdir(parents=True)
    supplement.write_text('{"altered":true}')
    release = tmp_path / RELEASE_PATH
    release.write_text(json.dumps({'reconstruction_sha256': '0' * 64}))
    approval = {'phase': CHILD, 'parent': PARENT, 'parent_path': str(path),
                'parent_seal': PARENT_SEAL, 'linking44_recovery_release_sha256': sha(release)}
    with pytest.raises(BudgetStop, match='reconstruction or parent differs'):
        load_checkpoint(approval, SimpleNamespace(root=tmp_path), ROOT)
