"""One isolated Full/conv-44 lineage through the existing author runner.

This module shares scientific functions and tested passive reporting, never the
DeepSeek campaign's approvals, ledger, cache or recovery exceptions.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

from .artifacts import snapshot_memory, restore_memory
from .budget import BudgetStop
from .config import OPENROUTER_CONFIG, fingerprint, source_fingerprint, stage_output_limits
from .evolution_fallback import verify_fallback_state
from .openrouter import CAMPAIGN, CampaignLedger, OpenRouterController, save_new

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'artifacts/gpt4omini'


def read(path):
    return json.loads(Path(path).read_bytes())


def inventory(directory):
    directory = Path(directory)
    return {p.relative_to(directory).as_posix():hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file()}


def verify_inventory(directory, files):
    for name,digest in files.items():
        path = (Path(directory)/name).resolve()
        if (not path.is_relative_to(Path(directory).resolve()) or path.is_symlink()
                or hashlib.file_digest(path.open('rb'),'sha256').hexdigest()!=digest):
            raise BudgetStop('Preserved evidence or provenance changed: '+name)


def verify_prior(root=ROOT):
    files=read(root/'artifacts/gpt4omini/verification/prior-preservation-all.json')
    verify_inventory(root,files)
    return len(files)


class FallbackGuard:
    """Permit only the unchanged author's verified failed-evolution transition."""
    def __init__(self, controller, healthy, note_document):
        self.controller, self.healthy, self.note_document = controller, healthy, note_document
        self.recoverable = False

    def before(self, agent):
        return snapshot_memory(agent.memory_system,validate=False)

    def after(self, agent, before, outcome, generations, record):
        pending=self.controller.pending
        if pending is None:return
        try:
            errors=[e for e in generations if e.get('error_type')]
            metadata=[e for e in generations if e['stage']=='metadata' and not e.get('error_type')]
            if (len(generations)!=2 or len(errors)!=1 or len(metadata)!=1
                    or errors[0]['budget_logical_id']!=pending['event']['budget_logical_id']
                    or self.controller.ledger.totals()['unknown_attempts']):
                raise BudgetStop('Fallback does not match exactly one settled original decision')
            self.healthy()
            proof=verify_fallback_state(before,snapshot_memory(agent.memory_system),outcome,
                    json.loads(metadata[0]['output']),self.note_document)
            record({'type':'failure','kind':'original_evolution_fallback',
                    'provider_deviation':pending['kind'],'turn_id':outcome['turn_id'],
                    'original_fallback_verified':True,'provider_output_accepted':False,
                    'raw_arguments_sha256':hashlib.sha256(errors[0]['output'].encode()).hexdigest(),
                    **proof})
            self.healthy()
            self.controller.pending=None
            if pending['kind']=='length':
                self.recoverable=True
                raise BudgetStop('Settled decision exhaustion; exact-state child required')
        except BudgetStop:raise
        except BaseException:raise BudgetStop('Fallback verification failed') from None


def checkpoint_from(parent_path, ledger, binding, *, root=ROOT):
    """Verify the full immutable ancestry, exact state and the next original turn."""
    path=Path(parent_path).resolve()
    lineage=[];seen=set();parent=None
    with ledger.transaction() as db:
        while path:
            if (not path.is_relative_to((ledger.root/'runs').resolve()) or path.name!='phase.json'
                    or str(path) in seen):
                raise BudgetStop('Foreign or cyclic checkpoint ancestry')
            seen.add(str(path));value=read(path)
            row=db.execute('SELECT approval,state,seal FROM phases WHERE id=?',(value['phase'],)).fetchone()
            if (not row or row[1]!='recoverable' or row[2]!=fingerprint(value)
                    or value['binding']!=binding or value['status']!='incomplete'
                    or not value.get('recoverable_length_failure')):
                raise BudgetStop('Unsealed, foreign or unsupported checkpoint')
            verify_inventory(path.parent,value['files'])
            auth=read(path.parent/'approval.json')
            if json.loads(row[0])!=auth or auth['binding']!=binding:
                raise BudgetStop('Checkpoint approval changed')
            lineage.append({'phase':value['phase'],'seal':row[2]})
            if parent is None:parent=value;leaf_path=path
            path=Path(value['parent_path']) if value.get('parent_path') else None
    state=read(leaf_path.parent/'partial-memory.json')['state']
    from .manifests import expand_manifest
    manifest=expand_manifest(root/'data/locomo10.json',read(root/'manifests/fallback.json'))
    conversation=next(c for c in manifest['conversations'] if c['original_id']=='conv-44')
    prefix=[o['turn_id'] for o in state['outcomes']]
    if (not prefix or prefix!=conversation['turn_ids'][:len(prefix)]
            or len(prefix)!=len(state['notes']) or len(prefix)!=parent['notes']
            or len(prefix)>675 or parent['questions']!=0
            or ledger.totals()['unknown_attempts']):
        raise BudgetStop('Checkpoint is not an exact advancing original turn prefix')
    failures=[]
    for line in (leaf_path.parent/'events.jsonl').read_text().splitlines():
        event=json.loads(line)
        if event['type']=='failure':failures.append(event)
    return {'state':state,'failures':failures,'lineage':{'policy':'gpt4omini-exact-state-v1',
            'campaign_id':CAMPAIGN,'condition':'full','parent_run_id':parent['phase'],
            'ancestors':lineage,'next_turn_id':conversation['turn_ids'][len(prefix)] if len(prefix)<675 else None}}


def execute_phase(approval, ledger, *, observer, client, token_counter,
                  root=ROOT, memory_module=None, scorer=None):
    """Run one immutable root/child; cloud verification is required before sealing."""
    from .author import make_agent_factory, _load_memory
    from .runner import run_manifest
    from .scoring import AuthorScorer, rescore_records
    from .langfuse_verify import verify_observations
    from .gpt4omini_reporting import import_results, original_qa_traces
    root=Path(root)
    scorer=scorer or AuthorScorer(root)
    binding=approval['binding']
    if fingerprint(source_fingerprint(root))!=binding['source_sha256']:
        raise BudgetStop('Source changed since reviewed phase freeze')
    parent_path=approval.get('parent_path')
    checkpoint=checkpoint_from(parent_path,ledger,binding,root=root) if parent_path else None
    phase=ledger.claim(approval)
    output=ledger.root/'runs'/phase
    output.mkdir(parents=True,exist_ok=False)
    save_new(output/'approval.json',approval)
    controller=OpenRouterController(client,ledger=ledger,phase=phase,journal=output/'raw')
    def factory(record):
        controller.observer=record
        return controller
    memory=memory_module or _load_memory(root)
    guard=FallbackGuard(controller,observer.assert_healthy,
                        lambda note:memory.note_document(SimpleNamespace(**note)))
    def boundary():
        observer.assert_healthy()
        if ledger.totals()['unknown_attempts']:raise BudgetStop('Unknown financial exposure')
    agent_factory=make_agent_factory(root,controller_factory=factory,memory_module=memory,
                                     token_counter=token_counter)
    agents=[]
    def tracked_factory(**kwargs):
        agent=agent_factory(**kwargs)
        if checkpoint:
            restore_memory(agent.memory_system,checkpoint['state'],note_type=agent._repro_note_type)
            restored=snapshot_memory(agent.memory_system,checkpoint['state']['outcomes'])
            if restored!=checkpoint['state']:raise BudgetStop('Exact checkpoint restoration failed')
        agents.append(agent)
        return agent
    error=None;summary=None
    try:
        summary=run_manifest(root/'data/locomo10.json',read(root/'manifests/fallback.json'),
            copy.deepcopy(OPENROUTER_CONFIG),output_dir=output,cache_root=ledger.root/'cache',
            source_hashes=source_fingerprint(root),condition='full',agent_factory=tracked_factory,
            scorer=scorer,observer=observer,run_id=phase,conversation_ids=['conv-44'],
            boundary_check=boundary,evolution_guard=guard,checkpoint=checkpoint,
            execution_type='checkpoint_recovery' if checkpoint else 'fresh_build')
        boundary()
    except BaseException as exc:
        error=type(exc).__name__
    capture=observer.finish()
    save_new(output/'trace-capture.json',capture)
    events=[json.loads(l) for l in (output/'events.jsonl').read_text().splitlines()]
    results=[e['result'] for e in events if e['type']=='question_result']
    # The runner's complete cache/partial bundle contains the ordered outcomes.
    if (output/'partial-memory.json').exists():state=read(output/'partial-memory.json')['state']
    else:
        caches=[p for p in (ledger.root/'cache').glob('*/state.json')
                if read(p.parent/'identity.json').get('condition')=='full']
        if not caches:raise BudgetStop('No complete memory artifact')
        state=read(caches[-1])
    receipt={'phase':phase,'binding':binding,'parent_path':str(parent_path) if parent_path else None,
             'status':'incomplete','notes':len(state['notes']),'questions':len(results),
             'evolution_counter':state['evo_cnt'],'error_type':error,
             'recoverable_length_failure':False,'budget':ledger.totals()}
    try:
        observer.assert_healthy()
        context={'binding':{**binding,'run_id':phase},'output_dir':str(output)}
        receipt['observations']=verify_observations(capture,context)
        if not error:
            if receipt['notes']!=675 or receipt['questions']!=158:
                raise BudgetStop('Original turn/question coverage incomplete')
            views=rescore_records(results,scorer)
            save_new(output/'scoring-views.json',views)
            receipt['experiments']=import_results(views,context,client=observer.client,
                                                traces=original_qa_traces(capture))
            receipt['status']=summary['status']
            save_new(output/'final-memory.json',state)
        elif guard.recoverable and not ledger.totals()['unknown_attempts']:
            receipt['recoverable_length_failure']=True
    except BaseException as exc:
        receipt['error_type']=type(exc).__name__
        receipt['status']='incomplete'
        receipt['recoverable_length_failure']=False
    receipt['files']=inventory(output)
    save_new(output/'phase.json',receipt)
    ledger.finish(phase,receipt,'recoverable' if receipt['recoverable_length_failure'] else
                  'complete' if receipt['status'] in ('complete','degraded') else 'terminal')
    return receipt
