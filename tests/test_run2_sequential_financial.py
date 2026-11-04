"""Copied actual ancestry; every generation is an offline MockTransport response."""
import copy
import json
import os
import shutil
import sqlite3
from pathlib import Path

import httpx
import pytest

from amem_repro import run2, run2_blk022 as incident
from amem_repro.config import RUN2_CONFIG, fingerprint, source_fingerprint
from amem_repro.evolution_fallback import POLICY_ID, RECOVERY_POLICY
from test_run2 import short_runner, execute_fixture
from test_foundation import Provider
from amem_repro.adapter import create_deepseek_controller

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def sequential(short_runner,monkeypatch):
    f=short_runner;root=f['root']
    origin=Path(os.environ.get('AMEM_RUN2_SEQUENTIAL_EVIDENCE_ROOT',ROOT))/'artifacts/run2'
    if not (origin/'runs/run2-full-conv-44-r0-p1/phase.json').exists():
        pytest.skip('Optional immutable p0/p1 incident archive')
    target=root/'artifacts/run2';target.mkdir(parents=True)
    shutil.copy2(origin/'budget.sqlite',target/'budget.sqlite')
    for name in [incident.PARENT_RUN,'run2-full-conv-44-r0-p1']:
        shutil.copytree(origin/'runs'/name,target/'runs'/name)
    # No original file is opened for writing. P2 admission mutates only this copy.
    (target/'frozen').symlink_to(origin/'frozen',target_is_directory=True)
    (target/'gate-a').symlink_to(origin/'gate-a',target_is_directory=True)
    (root/'artifacts/study-budget.sqlite').symlink_to(ROOT/'artifacts/study-budget.sqlite')
    (root/'.git').symlink_to(ROOT/'.git',target_is_directory=True)
    (root/'memory_layer.py').symlink_to(ROOT/'memory_layer.py')
    monkeypatch.setitem(run2.CONVERSATIONS,'conv-44',(675,158))
    campaign=json.loads((origin/'frozen/campaign-approval.json').read_text())
    path=target/'runs/run2-full-conv-44-r0-p1/phase.json'
    start=run2._read_lines(path.parent/'events.jsonl')[0]
    manifest=start['manifest'];sources=source_fingerprint(ROOT);receipt={'assets':{},'runtime':{'ok':True,'network_disabled':True},'source_sha256':fingerprint(sources)}
    financial=json.loads((ROOT/'artifacts/blk022-recovery/financial-receipt.json').read_text())
    migration={'policy':incident.FALLBACK_MIGRATION_POLICY,'reviewed_commit':'c'*40,
        'original_source_sha256':campaign['binding']['source_sha256'],
        'candidate_source_sha256':fingerprint(sources),
        'original_preflight_sha256':campaign['binding']['preflight_sha256'],
        'candidate_preflight_sha256':fingerprint(receipt),'financial_receipt_sha256':fingerprint(financial),
        'changed_files':sorted(incident.FALLBACK_FILES),'evolution_failure_policy':POLICY_ID,
        'observability':{'policy':'run2-audit-essential-v1','gate_sha256':'a'*64,
            'credential_receipt_sha256':'b'*64,'execution_script_sha256':'c'*64}}
    monkeypatch.setattr(incident,'verify_support_migration',lambda **kw:copy.deepcopy(migration))
    monkeypatch.setattr(run2,'_check_campaign_runtime',lambda *a,**kw:(copy.deepcopy(RUN2_CONFIG),copy.deepcopy(manifest),sources))
    from amem_repro import runner
    monkeypatch.setattr(runner,'expand_manifest',lambda *a:copy.deepcopy(manifest))
    f.update(campaign=campaign,receipt=receipt,_manifest=manifest,_sources=sources,_financial=financial,_parent=path)
    provider=Provider();shared=0;f['_length_turns']=set();f['_bad_turns']={2,4}
    def sdk(request):
        nonlocal shared
        wire=json.loads(request.content);response=provider.complete(**wire)
        response['system_fingerprint']=run2.MODEL_FINGERPRINT
        if 'should_evolve' in wire['tools'][0]['function']['parameters']['properties']:
            shared+=1
            if shared in f['_length_turns']:
                response['choices'][0]['finish_reason']='length';response['usage']['completion_tokens']=8192
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments']='{"should_evolve":'
            elif shared in f['_bad_turns']:
                response['choices'][0]['message']['tool_calls'][0]['function']['arguments']='{"should_evolve":true,"actions"["strengthen"]}'
        return httpx.Response(200,json=response)
    f['controller_factory']=lambda **kw:create_deepseek_controller(**kw,http_transport=httpx.MockTransport(sdk))
    f['observer'].captures_lifecycle=True
    return f


def plan(f,parent=None):
    p=run2.plan_phase(f['campaign'],f['receipt'],f['asset_root'],root=f['root'],
        condition='full',conversation_id='conv-44',parent=parent or f['_parent'],
        financial_adjudication=f['_financial'],support_reference='c'*40)
    p.update(approved=True,approved_by='offline copied-ledger test only',approved_at='2026-11-03T13:00:00Z')
    return p


def test_exact566_prefix_completes_mock_suffix_without_rebuild_or_budget_reset(sequential):
    f=sequential;approval=plan(f)
    assert approval['binding']['checkpoint']['policy']==RECOVERY_POLICY
    assert approval['binding']['checkpoint']['completed_turns']==566
    assert approval['binding']['checkpoint']['next_turn_id']=='D24:13'
    assert approval['limits']=={'phase_usd':'2.62999','max_logical_calls':534,'max_attempts':1602}
    p=execute_fixture(approval,f)
    assert p['status']=='degraded' and p['usable_for_next_phase']
    assert (p['total_memory_notes'],p['completed_questions'])==(675,158)
    assert p['budget']['logical_calls']==p['budget']['physical_attempts']==534
    assert p['cell_budget']['logical_calls']==1666 and p['cell_budget']['physical_attempts']==1667
    assert p['cell_budget']['charged_or_reserved_microusd']==2370010+p['budget']['charged_or_reserved_microusd']
    with sqlite3.connect(f['root']/'artifacts/run2/budget.sqlite') as db:
        incident._check_prefix(db)
        assert db.execute('SELECT status,charge,usage_json FROM attempts WHERE id=454').fetchone()==('unknown',324404,'null')
    events=run2._read_lines(f['root']/'artifacts/run2/runs'/p['run_id']/'events.jsonl')
    turns=[e['turn_id'] for e in events if e['type']=='evolution_outcome']
    conv=next(c for c in f['_manifest']['conversations'] if c['original_id']=='conv-44')
    assert turns==conv['turn_ids'][566:]
    assert len({e['question_id'] for e in events if e['type']=='question_result'})==158
    assert all(e['turn_id']!='D24:12' for e in events if e['type']=='generation' and e['stage'] in ('metadata','shared_decision'))


def test_two_successive_financial_lineage_length_checkpoints_preserve_quota_and_unknown(sequential):
    f=sequential;f['_bad_turns']=set();f['_length_turns']={2,4}
    first=execute_fixture(plan(f),f)
    assert first['recoverable_length_failure'] and first['total_memory_notes']==568
    parent=f['root']/'artifacts/run2/runs'/first['run_id']/'phase.json'
    second_approval=plan(f,parent)
    assert second_approval['phase_index']==3
    second=execute_fixture(second_approval,f)
    assert second['recoverable_length_failure'] and second['total_memory_notes']==570
    third=plan(f,f['root']/'artifacts/run2/runs'/second['run_id']/'phase.json')
    assert third['phase_index']==4 and third['limits']['max_logical_calls']==526
    assert len(third['binding']['checkpoint']['ancestor_receipts'])==4
    assert second['cell_budget']['unknown_attempts']==1
    assert second['cell_budget']['unadjudicated_unknown_attempts']==0
