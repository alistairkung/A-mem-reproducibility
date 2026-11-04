"""Bounded saved-result import and independent score/trace-subject readback."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import fingerprint
from .langfuse_verify import (
    VerificationError, _read, _retry, _proof, _query_cli,
    _check_experiments, _equal, _indexed, _metadata, import_and_verify_results,
)


def original_qa_traces(capture):
    rows=[r for r in capture['observations'] if r['name']=='A-MEM/question']
    traces={r['metadata']['question_id']:r['trace_id'] for r in rows}
    if len(traces)!=len(rows) or len(set(traces.values()))!=len(rows):
        raise VerificationError('Original QA traces missing or duplicated')
    return traces


def import_results(views, context, *, client, traces, query=None):
    expected=[r['question_id'] for r in next(iter(views.values()))['individual_results']]
    if set(expected)!=set(traces):raise VerificationError('QA trace identity differs from saved results')
    class AssociatedClient:
        def run_experiment(self, **kwargs):
            identity=kwargs['metadata']['experiment_identity']
            kwargs['experiment_id']=hashlib.sha256(fingerprint(identity).encode()).hexdigest()[:16]
            for item in kwargs['data']:
                item['metadata']['original_trace_id']=traces[item['metadata']['question_id']]
            return client.run_experiment(**kwargs)
        def flush(self):client.flush()
    imported=import_and_verify_results(views,context,client=AssociatedClient(),query=query)
    output=Path(context['output_dir'])
    saved=json.loads((output/'langfuse-imported.json').read_text())
    query=query or _query_cli
    def operation(paths):
        ids=','.join(r['id'] for r in saved['experiments'].values())
        common={'from-start-time':saved['from_start_time'],'limit':100,'all':True,'max-items':1000}
        experiments=_read(query,'experiments',{**common,'id':ids,'fields':'core,metadata,scores'},output,paths)
        items=_read(query,'experiment-items',{**common,'experiment-id':ids,
            'fields':'core,io,metadata,itemMetadata,experimentMetadata,scores','score-limit':50},output,paths)
        _check_experiments(views,saved,saved['identity'],experiments,items)
        scores=[]
        item_traces=sorted({i['traceId'] for i in items})
        if len(item_traces)!=len(items):raise VerificationError('Experiment trace identities overlap')
        for start in range(0,len(item_traces),50):
            scores+=_read(query,'scores',{'trace-id':','.join(item_traces[start:start+50]),
                'fields':'details,subject','limit':1000,'all':True,'max-items':10000},output,paths)
        indexed=_indexed(scores,'id',[s['id'] for item in items for s in item['scores']])
        for item in items:
            question=item['input']['question_id']
            _metadata({'original_trace_id':traces[question]},item.get('experimentItemMetadata'),'item/QA-trace')
            for score in item['scores']:
                actual=indexed[score['id']]
                _equal(score['name'],actual.get('name'),'score/name')
                _equal(score['value'],actual.get('value'),'score/value')
                _equal({'kind':'observation','id':item['id'],'traceId':item['traceId']},
                       actual.get('subject'),'score/subject')
        return {'verified':True,'items':len(items),'scores':len(scores),'traces':len(item_traces),
                'original_qa_traces':len(traces),'experiment_ids':imported['experiment_ids'],
                'experiment_urls':imported['experiment_urls']}
    body,paths=_retry(output,operation,6,6)
    return _proof(output,'experiment-associations',body,paths)
