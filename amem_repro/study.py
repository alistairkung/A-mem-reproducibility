"""One-shot T8 fallback cells through the existing durable paid-phase controls.

Planning never grants approval. This module never reads dotenv files or repairs
provider responses; failed/unfinished cells require a separate recovery decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
from decimal import Decimal, ROUND_CEILING

from .actions import ACTION_POLICY, action_configuration
from .artifacts import CacheStore
from .budget import STUDY_JOB_CAPS, ledger_summary
from .config import fingerprint, load_config, INDEX_STRING_POLICY, stage_output_limits
from .manifests import expand_manifest

ROOT = Path(__file__).resolve().parents[1]
T7_SOURCE = '2206fa3f23e6f9b36f3721a4e6d75383f3a0db21081d5ed6308313f5cbb237d3'
CHILD_RECEIPT = 'c1b3195f7b5e61d9998588c4754cd82891962d38aa2f515c2398918aadbf39fd'
REPLAY_RECEIPTS = {
    't7-reviewed-reference':'552b0e86057c9da7d2e0d03ac04a5b4db1c26e6ca25abaf5cec8878655d5d4d1',
    't7-reviewed-candidate':'3bcf45c32a874f12850df6ab509c8983c13d49a7011af4598b163212762ecdc6',
}
SUPPORT_MIGRATION = {'amem_repro/budget.py','amem_repro/phases.py','amem_repro/runner.py',
                     'amem_repro/artifacts.py','amem_repro/study.py','amem_repro/comparison.py'}


def _read(path):
    return json.loads(Path(path).read_text())


def verify_study_history(root, sources):
    """Check pinned baseline/T7 evidence and original ledger prefix, without writes."""
    from .phases import _verified_phase
    from .checkpoint import _read_archive
    root = Path(root)
    for name, expected in REPLAY_RECEIPTS.items():
        path=root/'artifacts/replays'/name/'verification.json'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('T7 full-mode equivalence receipt differs')
    with (root/'artifacts/replays/t7-reviewed-candidate/run/events.jsonl').open() as stream:
        reference=json.loads(next(stream))['source_hashes']
    if fingerprint(reference)!=T7_SOURCE:
        raise ValueError('T7 source provenance differs')
    old,new=reference['files'],sources['files']
    changed={name for name in old.keys()|new.keys() if old.get(name)!=new.get(name)}
    if changed-SUPPORT_MIGRATION or sources['author_revision']!=reference['author_revision']:
        raise ValueError('T8 migration changed scientific, provider or action implementation')
    parent_path=root/'artifacts/runs/pilot-conv50-d9a/phase.json'
    _read_archive(parent_path,root)
    child_dir=root/'artifacts/runs/pilot-conv50-checkpoint-child'
    child=_verified_phase(child_dir/'phase.json',root)
    if fingerprint(child)!=CHILD_RECEIPT:
        raise ValueError('Original baseline receipt differs')
    ledger=root/'artifacts/study-budget.sqlite'
    current=ledger_summary(ledger)
    if current['unknown_attempts'] or current['charged_or_reserved_microusd']<3025799:
        raise ValueError('Historical study ledger is missing or has unresolved charges')
    approval=_read(child_dir/'approval.json')
    with sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro',uri=True) as db:
        row=db.execute('SELECT auth_json FROM phases WHERE approval_id=?',(approval['approval_id'],)).fetchone()
        if row is None or json.loads(row[0])!=approval:
            raise ValueError('Historical child approval is missing from the shared ledger')
        last_attempt=db.execute('SELECT MAX(id) FROM attempts WHERE approval_id=?',(approval['approval_id'],)).fetchone()[0]
        last_logical=db.execute('SELECT MAX(id) FROM logical_calls WHERE approval_id=?',(approval['approval_id'],)).fetchone()[0]
        charge,count,unknown=db.execute("SELECT COALESCE(SUM(charge),0),COUNT(*),SUM(status!='settled') FROM attempts WHERE id<=?",(last_attempt,)).fetchone()
        logical=db.execute('SELECT COUNT(*) FROM logical_calls WHERE id<=?',(last_logical,)).fetchone()[0]
        if (charge,count,logical,unknown)!=(3025799,1610,1610,0):
            raise ValueError('Historical ledger prefix differs; later spending cannot mask loss')
        recorded=[]
        for directory in (parent_path.parent,child_dir):
            for line in (directory/'events.jsonl').read_text().splitlines():
                event=json.loads(line)
                if event['type']=='generation': recorded.extend(event.get('attempts',[]))
        if len(recorded)!=1544:
            raise ValueError('Original baseline attempt inventory differs')
        for attempt in recorded:
            row=db.execute('SELECT status,usage_json,charge FROM attempts WHERE id=?',(attempt['budget_attempt_id'],)).fetchone()
            usage=attempt['usage']
            cost=int((usage['prompt_tokens']*Decimal('.30')+usage['completion_tokens']*Decimal('1.20')).to_integral_value(rounding=ROUND_CEILING))
            if row is None or row[0]!='settled' or json.loads(row[1])!=usage or row[2]!=cost:
                raise ValueError('Original baseline attempt/usage/charge differs in the shared ledger')
        # An old ledger snapshot is not a fresh spending allowance. Even partial
        # main runs retain their approval artifacts and must retain their claims.
        for path in (root/'artifacts/runs').glob('*/approval.json'):
            prior=_read(path)
            if prior.get('phase')!='baseline': continue
            row=db.execute('SELECT auth_json,halted FROM phases WHERE approval_id=?',(prior['approval_id'],)).fetchone()
            if row is None or fingerprint(json.loads(row[0]))!=fingerprint(prior):
                raise ValueError('Archived main run missing from cumulative study ledger')
            try:
                claim=db.execute('SELECT study_id,condition,conversation_id,complete FROM study_jobs WHERE approval_id=?',(prior['approval_id'],)).fetchone()
            except sqlite3.OperationalError:
                raise ValueError('Archived main run lost its durable cell claim') from None
            prior_job=prior['binding'].get('study_job',{})
            if claim is None or claim[:3]!=(prior_job.get('study_id'),prior['binding'].get('condition'),prior_job.get('conversation_id')):
                raise ValueError('Archived main run lost its durable cell claim')
            if claim[3]:
                try:
                    if row[1] is not None:
                        raise ValueError('Completed ledger cell is halted')
                    _verified_phase(path.parent/'phase.json',root)
                except (ValueError,OSError,KeyError):
                    raise ValueError('Completed main ledger cell lacks a valid final phase receipt') from None
    with (child_dir/'events.jsonl').open() as stream:
        start=json.loads(next(stream))
    build=next(json.loads(line)['build_id'] for line in (child_dir/'events.jsonl').read_text().splitlines()
               if json.loads(line)['type']=='build_complete')
    identity=_read(root/'artifacts/cache'/build/'identity.json')
    state=CacheStore(root/'artifacts/cache').load(identity)
    if len(state['notes'])!=568 or state['evo_cnt']!=566:
        raise ValueError('Completed original full-mode cache differs')
    return child,start,sorted(changed)


def balanced_cost_forecast(root,manifest):
    """Use incurred ledger costs and measured stage means, never accuracy/predictions."""
    root=Path(root)
    ledger=root/'artifacts/study-budget.sqlite'
    current=ledger_summary(ledger)
    base_ids=[_read(root/'artifacts/runs'/name/'approval.json')['approval_id']
              for name in ('pilot-conv50-d9a','pilot-conv50-checkpoint-child')]
    with sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro',uri=True) as db:
        def means(ids):
            marks=','.join('?' for _ in ids)
            rows=db.execute(f'''SELECT l.stage,COUNT(DISTINCT l.id),SUM(a.charge)
                FROM logical_calls l JOIN attempts a ON a.logical_id=l.id
                WHERE l.approval_id IN ({marks}) GROUP BY l.stage''',ids)
            values={stage:Decimal(charge)/count for stage,count,charge in rows}
            if set(values)!={'metadata','shared_decision','query_keywords','answer'}:
                raise ValueError('Cost forecast requires complete measured stage coverage')
            return values
        completed={}
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='study_jobs'").fetchone():
            completed={(condition,conversation):approval_id for condition,conversation,approval_id in db.execute(
                'SELECT condition,conversation_id,approval_id FROM study_jobs WHERE study_id=? AND complete=1',('d10a-fallback-once-v1',))}
        full_ids=base_ids+[v for (condition,_),v in completed.items() if condition=='full']
        full=means(full_ids)
        observations={condition:means([v for (c,_),v in completed.items() if c==condition])
                      for condition in ('neither','linking_only','evolution_only')
                      if any(c==condition for c,_ in completed)}
        remaining=[]
        for condition,conversation in STUDY_JOB_CAPS:
            if (condition,conversation) in completed: continue
            selected=next(c for c in manifest['conversations'] if c['original_id']==conversation)
            turns,questions=len(selected['turn_ids']),len(selected['questions'])
            sample=observations.get(condition,full)
            cost=int((turns*(sample['metadata']+sample['shared_decision'])+
                      questions*(sample['query_keywords']+sample['answer'])).to_integral_value(rounding=ROUND_CEILING))
            remaining.append({'condition':condition,'conversation_id':conversation,'estimated_microusd':cost})
    estimate=sum(r['estimated_microusd'] for r in remaining)
    total=current['charged_or_reserved_microusd']+estimate+8000000
    return {'basis':'conservative-ledger-stage-means; no quality selection',
            'incurred_or_reserved_microusd':current['charged_or_reserved_microusd'],
            'remaining_estimate_microusd':estimate,'contingency_microusd':8000000,
            'total_estimate_microusd':total,'fits_ceiling':total<=50000000,'remaining_jobs':remaining,
            'limitation':'Point estimate is not an upper bound; retries and context/output growth can exhaust caps'}


def baseline_inputs(receipt, asset_root, root, condition, conversation_id, provider_policy):
    """Reconstruct an exact approved execution partition before any permit/client."""
    from .phases import _verified_receipt, _verified_phase
    root=Path(root)
    if (condition,conversation_id) not in STUDY_JOB_CAPS or provider_policy!=INDEX_STRING_POLICY:
        raise ValueError('Only the eleven fresh approved fallback cells and D3a are enabled')
    sources=_verified_receipt(receipt,asset_root,root)
    config=load_config(root/'config/study.json')
    manifest=expand_manifest(root/'data/locomo10.json',_read(root/'manifests/fallback.json'))
    child,start,migrated=verify_study_history(root,sources)
    expected50=next(c for c in manifest['conversations'] if c['original_id']=='conv-50')
    if (start['manifest']['conversations']!=[expected50] or start['configuration']!=config
            or child['provider_contract_policy']!=provider_policy
            or child['returned_models']!=['deepseek-flash']
            or child['system_fingerprints']!=['bc19ba97cbe016479903222bb1578db6']):
        raise ValueError('Original baseline scientific/model provenance differs')
    if condition!='full':
        completed=set()
        for path in (root/'artifacts/runs').glob('*/phase.json'):
            value=_read(path)
            if value.get('phase')=='baseline' and value.get('binding',{}).get('condition')=='full':
                value=_verified_phase(path,root)
                b=value['binding']
                if (b.get('manifest_sha256')==fingerprint(manifest) and b.get('config_sha256')==fingerprint(config)
                        and b.get('provider_contract_policy')==provider_policy
                        and value['returned_models']==child['returned_models']
                        and value['system_fingerprints']==child['system_fingerprints']):
                    completed.update(value['conversation_ids'])
        if not {'conv-49','conv-44'}<=completed:
            raise ValueError('Finish the two remaining original full-mode baseline conversations first')
    conversation=next(c for c in manifest['conversations'] if c['original_id']==conversation_id)
    forecast=balanced_cost_forecast(root,manifest)
    if not forecast['fits_ceiling']:
        raise ValueError('Balanced approved study no longer fits USD50 including USD8 contingency')
    calls=2*(len(conversation['turn_ids'])+len(conversation['questions']))
    binding={
        'manifest_sha256':fingerprint(manifest), 'config_sha256':fingerprint(config),
        'source_sha256':fingerprint(sources), 'preflight_sha256':fingerprint(receipt),
        'condition':condition,'repetition':0,'population':'fallback',
        'conversation_ids':[conversation_id], 'expected_questions':len(conversation['questions']),
        'expected_turns':len(conversation['turn_ids']),
        'memory_actions':action_configuration(condition),'action_policy':ACTION_POLICY,
        'action_implementation':'frozen-author' if condition=='full' else 't7-action-gates',
        'model':config['model']['id'],'endpoint':config['model']['base_url']+config['model']['route'],
        'provider_contract_policy':provider_policy,'max_output_tokens_by_stage':stage_output_limits(),
        'expected_returned_models':child['returned_models'],'expected_system_fingerprints':child['system_fingerprints'],
        'baseline_receipt_sha256':CHILD_RECEIPT,
        't7_replay_receipts':REPLAY_RECEIPTS,
        'source_migration':{'policy':'t8-financial-artifact-support-v1','from_source_sha256':T7_SOURCE,'changed_files':migrated},
        'study_job':{'study_id':'d10a-fallback-once-v1','conversation_id':conversation_id,
                     'expected_logical_calls':calls,'initial_study_microusd':3025799},
        'study_budget':{'additional_ceiling_microusd':38974201,'cumulative_usable_microusd':42000000,'contingency_microusd':8000000},
        'cost_only_forecast':forecast,
    }
    return config,manifest,sources,binding


def main():
    from .phases import plan_phase, execute_phase, _save
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('plan','run'):
        p=sub.add_parser(name)
        p.add_argument('--receipt',required=True)
        p.add_argument('--assets',required=True)
        if name=='plan':
            p.add_argument('--condition',required=True,choices=('full','neither','linking_only','evolution_only'))
            p.add_argument('--conversation',required=True,choices=('conv-49','conv-50','conv-44'))
            p.add_argument('--run-id',required=True)
            p.add_argument('--output',required=True)
        else:
            p.add_argument('--approval',required=True)
    args=parser.parse_args()
    receipt=_read(args.receipt)
    if args.command=='plan':
        value=plan_phase('baseline',receipt,args.assets,root=ROOT,condition=args.condition,
                         conversation_id=args.conversation,run_id=args.run_id,provider_contract_policy=INDEX_STRING_POLICY)
        _save(args.output,value)
        print(json.dumps({'plan':str(args.output),'approved':False,'limits':value['limits']}))
    else:
        value=execute_phase(_read(args.approval),receipt,args.assets,root=ROOT)
        print(json.dumps({'run_id':value['run_id'],'status':value['status'],'budget':value['budget']}))


if __name__=='__main__':
    main()
