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

from .artifacts import CacheStore, build_identity, snapshot_memory, restore_memory
from .budget import BudgetStop
from .config import OPENROUTER_CONFIG, fingerprint, source_fingerprint, stage_output_limits
from .evolution_fallback import verify_fallback_state
from .openrouter import (FULL_CELLS, CELL_ORDER, cell_key, cell_parts, approval_cell,
                         cell_store, CAMPAIGN, CampaignLedger, OpenRouterController, save_new)

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'artifacts/gpt4omini'


class RecoverableLength(BudgetStop):
    """Only this intentional safe-boundary stop can authorize a checkpoint child."""


def file_signature(path):
    path=Path(path)
    if path.is_symlink():raise BudgetStop('Protected source/artifact became a symlink')
    stat=path.stat()
    return stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns


def predecessor_files(campaign, cell):
    """Include audit dependencies omitted by the first immutable frontier."""
    outcome=campaign/'outcomes'/cell
    files=dict(read(outcome/'frontier.json')['files'])
    for axis in ('spec','standards'):
        receipt=outcome/f'acceptance-{axis}.json'
        raw=receipt.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=files[str(receipt.relative_to(campaign))]:
            raise BudgetStop('Predecessor acceptance receipt changed')
        audit=json.loads(raw)
        evidence=audit.get('evidence_files') or audit['evidence_sha256']
        for key,digest in evidence.items():
            name=key.removeprefix('artifacts/gpt4omini/')
            if files.setdefault(name,digest)!=digest:
                raise BudgetStop('Disagreement over predecessor artifact')
    return files


def admission_guard(approval, ledger, root):
    """Recheck sealed ancestry edges and immutable file identity at EVERY call.

    Full hashes are checked before the signatures are captured. ctime/inode/size/
    mtime checks avoid re-reading gigabytes of old raw responses per admission.
    Any changed signature is terminal; it is never refreshed or trusted anew.
    """
    sources=source_fingerprint(root)
    if fingerprint(sources)!=approval['binding']['source_sha256']:
        raise BudgetStop('Reviewed source changed')
    protected={root/name:file_signature(root/name) for name in sources['files']}
    data=root/'data/locomo10.json';manifest=root/'manifests/fallback.json'
    if (hashlib.file_digest(data.open('rb'),'sha256').hexdigest()!=approval['binding']['dataset_sha256']
            or fingerprint(read(manifest))!=approval['binding']['manifest_sha256']):
        raise BudgetStop('Frozen dataset or selection changed')
    protected.update({data:file_signature(data),manifest:file_signature(manifest)})
    key=approval_cell(approval)
    previous=CELL_ORDER[:CELL_ORDER.index(key)]
    for cell in previous:
        certificate=ledger.root/'outcomes'/cell/'frontier.json'
        files=predecessor_files(ledger.root,cell)
        protected[certificate]=file_signature(certificate)
        for name,digest in files.items():
            path=(ledger.root/name).absolute()
            if path.resolve()!=path or not path.is_relative_to(ledger.root):
                raise BudgetStop('Predecessor file path aliases foreign storage')
            signature=file_signature(path)
            if hashlib.file_digest(path.open('rb'),'sha256').hexdigest()!=digest or file_signature(path)!=signature:
                raise BudgetStop('Predecessor artifact changed')
            protected[path]=signature
    ancestors=[]
    path=Path(approval['parent_path']) if approval.get('parent_path') else None
    while path:
        value=read(path);phase=value['phase']
        verify_inventory(path.parent,value['files'])
        files={path.parent/name:file_signature(path.parent/name) for name in value['files']}
        files[path]=file_signature(path)
        protected.update(files)
        ancestors.append((phase,fingerprint(value),value.get('parent_path'),read(path.parent/'approval.json')))
        path=Path(value['parent_path']) if value.get('parent_path') else None
    def check(db):
        for path,signature in protected.items():
            if file_signature(path)!=signature:raise BudgetStop('Protected ancestor/source changed after claim')
        source_names={str(p.relative_to(root)) for p in (*root.glob('amem_repro/**/*.py'),*root.glob('config/*.json'))}
        expected={n for n in sources['files'] if n.startswith(('amem_repro/','config/'))}
        if source_names!=expected:raise BudgetStop('Source inventory changed after claim')
        own=db.execute('SELECT approval,parent,state,seal FROM phases WHERE id=?',(approval['phase'],)).fetchone()
        if own!=(json.dumps(approval,sort_keys=True),approval.get('parent'),'running',None):
            raise BudgetStop('Current phase ownership changed')
        if db.execute('SELECT COUNT(*) FROM phases WHERE parent=?',(approval['phase'],)).fetchone()[0]:
            raise BudgetStop('An active leaf cannot already have a checkpoint child')
        for phase,seal,parent_path,auth in ancestors:
            row=db.execute('SELECT approval,parent,state,seal FROM phases WHERE id=?',(phase,)).fetchone()
            if row!=(json.dumps(auth,sort_keys=True),auth.get('parent'),'recoverable',seal):
                raise BudgetStop('Ancestor seal, state or approval changed')
            incoming=db.execute('SELECT id FROM phases WHERE parent=?',(phase,)).fetchall()
            expected_child=approval['phase'] if phase==approval.get('parent') else next(
                (p for p,s,path,a in ancestors if a.get('parent')==phase),None)
            if incoming!=[(expected_child,)]:raise BudgetStop('Foreign or missing checkpoint edge')
    return check


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


def verify_accepted_cell(campaign, cell):
    """Verify source receipts and independent audits before sealing newer hashes."""
    import sqlite3
    from base64 import b64decode
    store=cell_store(campaign,cell)
    conversation,condition=cell_parts(cell)
    with sqlite3.connect((campaign/'budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        phases=db.execute("""SELECT id,seal FROM phases WHERE json_extract(approval,'$.kind')='baseline'
                           AND json_extract(approval,'$.conversation')=?
                           AND json_extract(approval,'$.condition')=? ORDER BY rowid""",(conversation,condition)).fetchall()
    if not phases: raise BudgetStop('No prior collection')
    for phase,seal in phases:
        directory=store/'runs'/phase
        record=read(directory/'phase.json')
        if fingerprint(record)!=seal: raise BudgetStop('Prior scientific receipt differs from ledger')
        verify_inventory(directory,record['files'])
    if (record['status'] not in ('complete','degraded')
            or record['binding']['conversation_id']!=conversation
            or record['binding']['condition']!=condition):
        raise BudgetStop('Predecessor scientific collection incomplete')
    cache=read(directory/'cache-proof.json')
    verify_inventory(campaign/cache['directory'],cache['files'])
    for axis in ('spec','standards'):
        review=read(campaign/'outcomes'/cell/f'acceptance-{axis}.json')
        if review.get('accepted') is not True or review.get('verdict')!='pass' or review['phase']!=phase:
            raise BudgetStop('Predecessor independent acceptance incomplete')
        files=review.get('evidence_files') or review.get('evidence_sha256')
        if not files:raise BudgetStop('Missing prior independent proof digests')
        verify_inventory(campaign,{n.removeprefix('artifacts/gpt4omini/'):d for n,d in files.items()})
    finance=read(store/'reconciliation.json')
    if not finance['verified']:raise BudgetStop('Predecessor financial proof incomplete')
    journal=Path(finance['generation_journal'])
    if not journal.resolve().is_relative_to(store.resolve()): raise BudgetStop('Foreign billing journal')
    for i,generation in enumerate(finance['generations']):
        matches=list(journal.glob(f'{i}-*.json'))
        if not any((r:=read(f))['status']==200 and json.loads(b64decode(r['response_base64'])).get('data')==generation
                   for f in matches):
            raise BudgetStop('Prior generation evidence changed')


def verify_prior(root=ROOT):
    import subprocess
    evidence=read(root/'artifacts/gpt4omini/verification/prior-preservation-authoritative-v2.json')
    legacy=Path(evidence['legacy_root']).resolve()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=legacy,text=True).strip()
    if head!=evidence['legacy_commit']:
        raise BudgetStop('Historical source checkout is no longer frozen')
    verify_inventory(legacy,evidence['files'])
    verify_inventory(legacy,evidence['input_files'])
    for name,target in evidence['symlinks'].items():
        path=legacy/name
        if not path.is_symlink() or os.readlink(path)!=target:
            raise BudgetStop('Historical artifact link changed')
    return len(evidence['files'])


class FallbackGuard:
    """Permit only the unchanged author's verified failed-evolution transition."""
    def __init__(self, controller, healthy, note_document):
        self.controller, self.healthy, self.note_document = controller, healthy, note_document
        self.recoverable = False
        self.policy_id='gpt4omini-original-fallback-v1'

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
                    or self.controller.ledger.unaccepted_unknowns(self.controller.ledger.claimed[self.controller.phase])):
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
                raise RecoverableLength('Settled decision exhaustion; exact-state child required')
        except BudgetStop:raise
        except BaseException:raise BudgetStop('Fallback verification failed') from None


def checkpoint_from(parent_path, ledger, binding, *, root=ROOT):
    """Verify the full immutable ancestry, exact state and the next original turn."""
    cell=binding['conversation_id']
    condition=binding['condition']
    store=cell_store(ledger.root,cell_key(cell,condition))
    nturns,_=FULL_CELLS[cell]
    path=Path(parent_path).resolve()
    lineage=[];seen=set();parent=None
    with ledger.transaction() as db:
        while path:
            if (not path.is_relative_to((store/'runs').resolve()) or path.name!='phase.json'
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
    conversation=next(c for c in manifest['conversations'] if c['original_id']==cell)
    prefix=[o['turn_id'] for o in state['outcomes']]
    if (not prefix or prefix!=conversation['turn_ids'][:len(prefix)]
            or len(prefix)!=len(state['notes']) or len(prefix)!=parent['notes']
            or len(prefix)>nturns or parent['questions']!=0
            or ledger.unaccepted_unknowns(read(leaf_path.parent/'approval.json'))):
        raise BudgetStop('Checkpoint is not an exact advancing original turn prefix')
    failures=[]
    for line in (leaf_path.parent/'events.jsonl').read_text().splitlines():
        event=json.loads(line)
        if event['type']=='failure':failures.append(event)
    return {'state':state,'failures':failures,'lineage':{'policy':'gpt4omini-exact-state-v1',
            'campaign_id':CAMPAIGN,'condition':condition,'parent_run_id':parent['phase'],
            'ancestors':lineage,'next_turn_id':conversation['turn_ids'][len(prefix)] if len(prefix)<nturns else None}}


def execute_phase(approval, ledger, *, observer, client, token_counter,
                  root=ROOT, memory_module=None, scorer=None):
    """Run one immutable root/child; cloud verification is required before sealing."""
    from .author import make_agent_factory, _load_memory
    from .actions import make_action_agent_factory, action_configuration
    from .runner import run_manifest
    from .scoring import AuthorScorer, rescore_records
    from .langfuse_verify import verify_observations
    from .gpt4omini_reporting import import_results, original_qa_traces
    root=Path(root)
    scorer=scorer or AuthorScorer(root)
    binding=approval['binding']
    cell=approval['conversation']
    condition=approval['condition']
    if binding['conversation_id']!=cell or binding['condition']!=condition:
        raise BudgetStop('Cell identity differs from source-bound approval')
    store=cell_store(ledger.root,cell_key(cell,condition))
    nturns,nqa=FULL_CELLS[cell]
    if fingerprint(source_fingerprint(root))!=binding['source_sha256']:
        raise BudgetStop('Source changed since reviewed phase freeze')
    parent_path=approval.get('parent_path')
    if bool(parent_path)!=bool(approval.get('parent')):
        raise BudgetStop('Continuation requires both its exact parent identity and path')
    if parent_path:
        claimed_parent=read(parent_path)
        if (claimed_parent['phase']!=approval['parent']
                or fingerprint(claimed_parent)!=approval.get('parent_seal')):
            raise BudgetStop('Parent path and approved immutable parent edge differ')
    checkpoint=checkpoint_from(parent_path,ledger,binding,root=root) if parent_path else None
    phase=ledger.claim(approval)
    ledger.set_guard(phase,admission_guard(approval,ledger,root))
    output=store/'runs'/phase
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
        if ledger.unaccepted_unknowns(approval):raise BudgetStop('Unknown financial exposure')
    agent_factory=make_agent_factory(root,controller_factory=factory,memory_module=memory,
                                     token_counter=token_counter) if condition=='full' else make_action_agent_factory(
        root,condition=condition,controller_factory=factory,memory_module=memory,token_counter=token_counter)
    agents=[]
    def tracked_factory(**kwargs):
        agent=agent_factory(**kwargs)
        if checkpoint:
            restore_memory(agent.memory_system,checkpoint['state'],note_type=agent._repro_note_type)
            restored=snapshot_memory(agent.memory_system,checkpoint['state']['outcomes'])
            if restored!=checkpoint['state']:raise BudgetStop('Exact checkpoint restoration failed')
        agents.append(agent)
        return agent
    if condition!='full':
        tracked_factory._repro_condition=condition
        tracked_factory._repro_action_configuration=action_configuration(condition)
    error=None;summary=None;failure=None
    try:
        summary=run_manifest(root/'data/locomo10.json',read(root/'manifests/fallback.json'),
            copy.deepcopy(OPENROUTER_CONFIG),output_dir=output,cache_root=store/'cache',
            source_hashes=source_fingerprint(root),condition=condition,agent_factory=tracked_factory,
            scorer=scorer,observer=observer,run_id=phase,conversation_ids=[cell],
            boundary_check=boundary,evolution_guard=guard,checkpoint=checkpoint,
            execution_type='checkpoint_recovery' if checkpoint else 'fresh_build')
        boundary()
    except BaseException as exc:
        error=type(exc).__name__;failure=exc
    events=[json.loads(l) for l in (output/'events.jsonl').read_text().splitlines()]
    results=[e['result'] for e in events if e['type']=='question_result']
    views=None;post_scoring_failures=0
    if not error:
        callback=scorer.observer
        scorer.observer=None
        try:
            views=rescore_records(results,scorer)
            for policy,view in views.items():
                for result in view['individual_results']:
                    for failed in result.get('metric_failures',[]):
                        post_scoring_failures+=1
                        callback({**failed,'question_id':result['question_id'],
                                  'conversation_id':cell,'scoring_policy':policy})
            save_new(output/'scoring-views.json',views)
        except BaseException as exc:
            error=type(exc).__name__;failure=exc
        finally:scorer.observer=callback
    capture=observer.finish()
    save_new(output/'trace-capture.json',capture)
    events=[json.loads(l) for l in (output/'events.jsonl').read_text().splitlines()]
    outcomes=copy.deepcopy(checkpoint['state']['outcomes']) if checkpoint else []
    outcomes += [{k:v for k,v in e.items() if k not in ('type','run_id','build_id','conversation_id','level')}
                 for e in events if e['type']=='evolution_outcome']
    state=snapshot_memory(agents[-1].memory_system,outcomes) if agents else None
    identity=None
    if (output/'partial-memory.json').exists():
        if read(output/'partial-memory.json')['state']!=state:
            raise BudgetStop('Partial checkpoint differs from actual final author state')
    elif not error:
        start=next(e for e in events if e['type']=='run_start')
        conversation=next(c for c in start['manifest']['conversations'] if c['original_id']==cell)
        identity=build_identity(OPENROUTER_CONFIG,conversation,start['manifest']['dataset_sha256'],
                                start['source_hashes'],provider_contract_policy='strict-original-v1')
        identity.update(condition=condition,memory_actions=action_configuration(condition),
                        action_policy='released-action-boundaries-v1',
                        action_implementation='frozen-author' if condition=='full' else 't7-action-gates',
                        evolution_failure_policy=guard.policy_id)
        if checkpoint:identity['checkpoint']=checkpoint['lineage']
        saved=CacheStore(store/'cache').load(identity)
        if {k:v for k,v in saved.items() if k!='build_failures'}!=state:
            raise BudgetStop('Exact completed cache differs from actual final author state')
        state=saved
    if state is None:raise BudgetStop('No author state could be preserved')
    receipt={'phase':phase,'binding':binding,'parent_path':str(parent_path) if parent_path else None,
             'status':'incomplete','notes':len(state['notes']),'questions':len(results),
             'evolution_counter':state['evo_cnt'],'error_type':error,
             'error_message':str(failure) if failure else None,
             'post_scoring_failure_count':post_scoring_failures,
             'recoverable_length_failure':False,'budget':ledger.totals()}
    try:
        observer.assert_healthy()
        context={'binding':{**binding,'run_id':phase},'output_dir':str(output)}
        receipt['observations']=verify_observations(capture,context)
        if not error:
            if receipt['notes']!=nturns or receipt['questions']!=nqa:
                raise BudgetStop('Original turn/question coverage incomplete')
            if approval.get('retained_access_prefix'):
                if [o['turn_id'] for o in outcomes]!=conversation['turn_ids']:
                    raise BudgetStop('Ordered original turn coverage differs')
                if [r['question_id'] for r in results]!=[q['question_id'] for q in conversation['questions']]:
                    raise BudgetStop('Ordered benchmark questions differ')
                with ledger.transaction() as db:
                    count=db.execute("SELECT COUNT(*) FROM attempts a JOIN phases p ON a.phase=p.id WHERE json_extract(p.approval,'$.kind')='baseline' AND json_extract(p.approval,'$.conversation')=? AND json_extract(p.approval,'$.condition')=? AND a.state='settled'",(cell,condition)).fetchone()[0]
                if count!=2*(nturns+nqa):raise BudgetStop('Full baseline original request count differs')
            receipt['experiments']=import_results(views,context,client=observer.client,
                                                traces=original_qa_traces(capture))
            receipt['status']='degraded' if post_scoring_failures or checkpoint or (cell=='conv-44' and approval.get('retained_access_prefix')) else summary['status']
            save_new(output/'final-memory.json',state)
            # Cloud work must not conceal a changed cache/source after initial validation.
            if CacheStore(store/'cache').load(identity)!=state:
                raise BudgetStop('Completed cache changed during reporting')
            cache_path=CacheStore(store/'cache').path_for(identity)
            save_new(output/'cache-proof.json',{'directory':str(cache_path.relative_to(ledger.root)),
                                               'files':inventory(cache_path)})
            if fingerprint(source_fingerprint(root))!=binding['source_sha256']:
                raise BudgetStop('Reviewed source changed during reporting')
        elif (type(failure) is RecoverableLength and guard.recoverable
                and (output/'summary.json').exists() and (output/'partial-memory.json').exists()
                and not any(e.get('kind') in ('partial_artifact','reporting','token_measurement') for e in events)
                and not ledger.unaccepted_unknowns(approval)):
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
