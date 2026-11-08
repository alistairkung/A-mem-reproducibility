"""Offline extraction of compact numeric reporting snapshots from immutable local evidence.

Run with --evidence-root pointing to the original evidence-bearing repository.
No provider, scorer or metric implementation is invoked. Existing saved scores are read only.
"""
from pathlib import Path
import argparse
import hashlib
import json
from math import fsum
import subprocess

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
COMMIT = '8485673183d7b8018c841082d075b21158002700'
POLICIES = {'alternative':'author-corrected-v1','historical':'author-legacy-c5-v1'}
SOURCES = {
    'conv-44': {'questions':158,'run':'artifacts/run2/runs/run2-full-conv-44-r0-p2',
                'scoring':'075c26e2792eb5852b164dcbc7c699d802729f2e5964126edb4d1064ffec5b8e',
                'phase':'e38b16965b23400205d14e64908176a31687055ffe31bf564777b55579c1db36',
                'acceptance_path':'artifacts/run2/reporting-recovery/lineage-completion.json',
                'acceptance_sha256':'642414039f25532f046c974a3d38e30ed77deafa0eedd9714f63a7b652f5fc3c',
                'document':'docs/reproducibility/run2-conv44-reporting-complete-20261104.md'},
    'conv-49': {'questions':196,'run':'artifacts/runs/t8-full-conv49-checkpoint-child',
                'scoring':'835c702c1a4d72226a7ab38d2f79d257714aec68b10b126129676dfca4bc8bdd',
                'phase':'b94572b488e34a8f5d87fb05217545345a2733cc669a8e1bc0637de4bba393c3',
                'acceptance_path':'artifacts/t8/offline/review/conv49-completed-audit.json',
                'acceptance_sha256':'8b0c68044bab9f8f7e2d9d5f0deaf5bbbb6ad282179567abb2b08469a7126537',
                'document':'docs/reproducibility/t8-conv49-baseline-20261103.md'},
    'conv-50': {'questions':204,'run':'artifacts/runs/pilot-conv50-checkpoint-child',
                'scoring':'fbda62088c71be6123a67c39bcae6c7a8cc6033781b2ec22f6e6e36287113218',
                'phase':'2cffc264ce81242f985cd018784f683e64b57dfabaf0675a5d87c20a164bddb1',
                'acceptance_path':'artifacts/checkpoint-child-final-verification.json',
                'acceptance_sha256':'3abcd78be2435768020e88d722b78942ab081f482021b9bc948acad3bcf37866',
                'document':'docs/reproducibility/t5-conv50-baseline-20261101.md'},
}


def require(test,message):
    if not test:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path,digest):
    data = path.read_bytes()
    require(sha(data)==digest,'Evidence fingerprint differs: '+str(path))
    return json.loads(data)


def extract(evidence_root,output):
    rows=[]
    evidence={'source_commit':COMMIT,'policy_names':POLICIES,'documents':{},'conversations':{}}
    gpt_data = subprocess.check_output(['git','show',COMMIT+':docs/reproducibility/gpt4omini-558q-four-condition-scores.jsonl'],cwd=REPOSITORY)
    gpt_rows={r['question_id']:r for r in map(json.loads,gpt_data.splitlines())}
    evidence['gpt4omini_selection_sha256']=sha(gpt_data)
    for conv,source in SOURCES.items():
        run=evidence_root/source['run']
        phase=pinned(run/'phase.json',source['phase'])
        views=pinned(run/'scoring-views.json',source['scoring'])
        acceptance=pinned(evidence_root/source['acceptance_path'],source['acceptance_sha256'])
        require(phase['artifact_sha256']['scoring-views.json']==source['scoring'],'Phase-scoring binding differs')
        require(phase['completed_questions']==phase['expected_questions']==source['questions'],'Incomplete question population')
        require(phase['binding']['model']=='deepseek-flash','Wrong provider model')
        if conv=='conv-44':
            require(phase['status']=='incomplete' and acceptance['status']=='Degraded'
                    and acceptance['questions']==158 and acceptance['original_phase_sha256']==source['phase']
                    and acceptance['question_view_items']==316 and acceptance['imported_scores']==4494,
                    'Run2 separate reporting completion is not verified')
        else:
            require(phase['status']=='degraded' and phase['usable_for_next_phase'] is True,'No completed Degraded lineage')
            require(acceptance['status']=='degraded' and acceptance['questions']==source['questions'], 'Acceptance population differs')
            if conv=='conv-49':
                require(acceptance['accepted'] is True and not acceptance['metric_failures'], 'Independent conv-49 acceptance is incomplete')
            else:
                require(acceptance['all_paid_execution_finished'] and acceptance['phase_inventory_verified'] and not acceptance['metric_failures'], 'Independent conv-50 completion is incomplete')
        aggregated={}
        selected={}
        for label,policy in POLICIES.items():
            view=views[policy]
            require(view['scoring_policy']==policy,'Wrong scoring policy')
            items=view['individual_results']
            require([r['question_id'] for r in items]==[f'{conv}:qa:{i}' for i in range(source['questions'])], 'Question identities differ')
            require(not any(r['metric_failures'] for r in items),'Metric failure retained in selected scores')
            selected[label]=items
            aggregated[label]={}
            for category in [None,1,2,3,4,5]:
                subset=items if category is None else [r for r in items if r['category']==category]
                key='overall' if category is None else f'category_{category}'
                original=view['aggregate_metrics'][key]
                aggregate={'count':len(subset)}
                for metric in ('f1','bleu1'):
                    saved=original[metric]['mean']
                    require(original[metric]['count']==len(subset) and abs(fsum(r['metrics'][metric] for r in subset)/len(subset)-saved)<1e-15,'Question scores and saved aggregate disagree')
                    aggregate[metric]=saved
                aggregated[label][key]=aggregate
            if conv=='conv-44':
                require(aggregated[label]==acceptance['metrics'][policy],'Accepted reporting supplement differs')
        for a,h in zip(selected['alternative'],selected['historical'],strict=True):
            require(a['question_id']==h['question_id'] and a['prediction']==h['prediction'] and a['category']==h['category'], 'Policy views use different predictions')
            require(a['conversation_id']==h['conversation_id']==conv and a['category']==gpt_rows[a['question_id']]['category'],'Cross-model selection differs')
            rows.append({'question_id':a['question_id'],'conversation_id':conv,'category':a['category'],
                         **{label:{m:row['metrics'][m] for m in ('f1','bleu1')} for label,row in [('alternative',a),('historical',h)]}})
        checkpoint=phase['binding'].get('checkpoint',{})
        parent=checkpoint.get('parent_run_id') or checkpoint.get('parent_phase')
        evidence['conversations'][conv]={'question_count':source['questions'],'classification':'Degraded',
            'run_id':phase['run_id'],'raw_scoring_path':source['run']+'/scoring-views.json','raw_scoring_sha256':source['scoring'],
            'phase_path':source['run']+'/phase.json','phase_sha256':source['phase'],'phase_status':phase['status'],
            'scorer_sha256':views[POLICIES['alternative']]['scorer_sha256'],'original_aggregates':aggregated,
            'acceptance':{'path':source['acceptance_path'],'sha256':source['acceptance_sha256'],'status':acceptance['status']},
            'generation_binding':{k:phase['binding'].get(k) for k in ['model','endpoint','provider_contract_policy','max_output_tokens_by_stage','config_sha256','source_sha256']},
            'parent_run_id':parent}
        doc=source['document']
        data=subprocess.check_output(['git','show',COMMIT+':'+doc],cwd=REPOSITORY)
        last=subprocess.check_output(['git','log','-1','--format=%H',COMMIT,'--',doc],cwd=REPOSITORY,text=True).strip()
        evidence['documents'][doc]={'commit':COMMIT,'sha256':sha(data),'last_changed_commit':last}
    require(len(rows)==558 and set(r['question_id'] for r in rows)==set(gpt_rows),'Cross-model question IDs differ')
    raw=('\n'.join(json.dumps(r,sort_keys=True,separators=(',',':')) for r in rows)+'\n').encode()
    evidence['snapshot_sha256']=sha(raw)
    evidence['derived_pooled_percent']={policy:{m:100*fsum(r[policy][m] for r in rows)/len(rows) for m in ('f1','bleu1')} for policy in POLICIES}
    evidence['pooled_status']='Derived question-weighted aggregate; not a previously accepted campaign total'
    output.mkdir(parents=True,exist_ok=True)
    (output/'question_scores.jsonl').write_bytes(raw)
    (output/'evidence.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps(evidence['derived_pooled_percent'],indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,default=HERE/'inputs')
    args=parser.parse_args()
    extract(args.evidence_root.resolve(),args.output_dir.resolve())
