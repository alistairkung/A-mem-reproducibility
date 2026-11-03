"""Verify actual Langfuse delivery without model calls or a second evaluator.

The pinned CLI reads modern APIs. Only saved predictions/metrics are imported;
readback retries never re-execute an experiment. Local journals remain authoritative.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from .config import fingerprint
from .phases import _save

CLI_VERSION = '1.2.4'
IDENTITY_KEYS = ('campaign_id', 'condition', 'population', 'manifest_sha256',
                 'repetition', 'run_id', 'conversation_id', 'provider_contract_policy')


class VerificationError(RuntimeError):
    """Missing or mismatched cloud evidence prohibits campaign continuation."""


def _output(context):
    path=Path(context['output_dir']).resolve()
    if not any(a=='artifacts' and b=='run2' for a,b in zip(path.parts,path.parts[1:])):
        raise VerificationError('Cloud evidence must use a separate Run2 artifact directory')
    path.mkdir(parents=True,exist_ok=True)
    return path


def _redact(value):
    if isinstance(value,dict):return {k:_redact(v) for k,v in value.items()}
    if isinstance(value,list):return [_redact(v) for v in value]
    if isinstance(value,str):
        for name in ('LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY'):
            secret=os.environ.get(name)
            if secret:value=value.replace(secret,'[redacted]')
    return value


def _query_cli(resource, options):
    if resource not in ('observations','scores','experiments','experiment-items'):
        raise VerificationError('Unsupported Langfuse read resource')
    env={k:v for k,v in os.environ.items() if not any(
        token in k.upper() for token in ('DEEPSEEK','OPENAI_API','ANTHROPIC_API'))}
    host=env.get('LANGFUSE_BASE_URL') or env.get('LANGFUSE_HOST')
    if not host or not all(env.get(k) for k in ('LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY')):
        raise VerificationError('Langfuse project keys and explicit host are required')
    env.update(LANGFUSE_BASE_URL=host,LANGFUSE_HOST=host)
    env.setdefault('npm_config_cache',str(Path(tempfile.gettempdir())/'amem-run2-langfuse-cli-cache'))
    command=[shutil.which('npx') or 'npx','--yes',f'langfuse-cli@{CLI_VERSION}',
             'api',resource,'list','--json']
    for key,value in options.items():
        if value is True:command.append('--'+key)
        elif value is not None and value is not False:command.extend(['--'+key,str(value)])
    result=subprocess.run(command,env=env,text=True,capture_output=True,timeout=120)
    try:payload=json.loads(result.stdout)
    except ValueError as error:raise VerificationError('CLI returned no JSON evidence') from error
    if result.returncode and payload.get('status')==200:
        raise VerificationError('Langfuse CLI read did not succeed')
    return payload


def _read(query, resource, options, output, paths):
    path=output/f'langfuse-readback-{resource}-{uuid.uuid4().hex}.json'
    try:payload=query(resource,options)
    except Exception as error:
        _save(path,{'resource':resource,'options':options,'error_type':type(error).__name__})
        paths.append(path)
        raise
    # Request/response headers are deliberately excluded from scientific evidence.
    snapshot={'resource':resource,'options':options,'status':payload.get('status'),
              'body':_redact(payload.get('body'))}
    _save(path,snapshot);paths.append(path)
    if payload.get('status')!=200:raise VerificationError('Langfuse read status is not200')
    body=payload.get('body')
    if not isinstance(body,dict) or not isinstance(body.get('data'),list):
        raise VerificationError('Langfuse response lacks a data array')
    if body.get('meta',{}).get('truncated') is not False:
        raise VerificationError('Langfuse pagination is incomplete or truncated')
    return body['data']


def _equal(expected, actual, path):
    # Decode JSON transport containers only; never parse/normalize an expected string.
    if not isinstance(expected,str) and isinstance(actual,str):
        try:actual=json.loads(actual)
        except ValueError:pass
    if isinstance(expected,dict):
        if not isinstance(actual,dict) or set(expected)!=set(actual):
            raise VerificationError('Remote object differs at '+path)
        for key,value in expected.items():_equal(value,actual[key],path+'/'+key)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(expected)!=len(actual):
            raise VerificationError('Remote list differs at '+path)
        for index,(left,right) in enumerate(zip(expected,actual)):_equal(left,right,path+f'/{index}')
    elif ((type(expected) is bool or type(actual) is bool) and type(expected) is not type(actual)) or expected!=actual:
        raise VerificationError('Remote value differs at '+path)


def _leaves(value,prefix=''):
    if isinstance(value,dict) and value:
        return {path:leaf for key,child in value.items()
                for path,leaf in _leaves(child,prefix+key+'.').items()}
    return {prefix[:-1]:value}


def _metadata(expected,actual,path):
    if isinstance(actual,str):
        try:actual=json.loads(actual)
        except ValueError:pass
    if not isinstance(actual,dict):raise VerificationError('Remote metadata missing at '+path)
    for key,value in expected.items():
        nested={k:v for k,v in actual.items() if k.startswith(key+'.')}
        if key in actual:
            if nested:raise VerificationError('Ambiguous metadata encoding at '+path+'/'+key)
            _equal(value,actual[key],path+'/'+key)
        elif isinstance(value,dict) and value:
            # SDK5 flattens metadata dictionaries into dotted OTel attributes.
            leaves=_leaves(value,key+'.')
            if set(nested)-set(leaves):raise VerificationError('Unexpected metadata fields at '+path+'/'+key)
            for leaf,wanted in leaves.items():_equal(wanted,actual.get(leaf),path+'/'+leaf)
        else:
            if nested:raise VerificationError('Unexpected nested metadata at '+path+'/'+key)
            _equal(value,None,path+'/'+key)


def _identity(context):
    binding=context['binding']
    value={key:context.get(key,binding.get(key)) for key in IDENTITY_KEYS}
    if any(value[k] is None for k in IDENTITY_KEYS):
        raise VerificationError('Cloud verification requires the complete campaign identity')
    return value


def _indexed(rows,key,expected_ids):
    expected_ids=list(expected_ids)
    indexed={r[key]:r for r in rows}
    if len(set(expected_ids))!=len(expected_ids) or len(indexed)!=len(rows) or set(indexed)!=set(expected_ids):
        raise VerificationError('Cloud identifiers are missing, duplicated or unexpected')
    return indexed


def _check_observations(receipt,rows,scores):
    remote=_indexed(rows,'id',[r['id'] for r in receipt['observations']])
    logical_roots={}
    for expected in receipt['observations']:
        actual=remote[expected['id']];where='observations/'+expected['id']
        for left,right in (('trace_id','traceId'),
                           ('session_id','sessionId'),('name','name'),('level','level')):
            _equal(expected.get(left),actual.get(right),where+'/'+right)
        parent=actual.get('parentObservationId')
        if expected.get('parent_observation_id') is None and parent is not None:
            # SDK5.1 seeds trace_id-only contexts with an unexported remote parent.
            # Accept only the API's logical-root classification, never a wrong known parent.
            if actual.get('isRootObservation') is not True or parent in remote:
                raise VerificationError('Remote root hierarchy differs at '+where)
            logical_roots[expected['id']]=parent
        else:_equal(expected.get('parent_observation_id'),parent,where+'/parentObservationId')
        _equal(expected['type'].upper(),actual.get('type'),where+'/type')
        for key in ('input','output'):_equal(expected.get(key),actual.get(key),where+'/'+key)
        _metadata(expected['metadata'],actual.get('metadata'),where+'/metadata')
        for left,right in (('model','model'),('model_parameters','modelParameters'),
                           ('usage_details','usageDetails'),('cost_details','costDetails')):
            if left in expected:_equal(expected[left],actual.get(right),where+'/'+right)
    remote_scores=_indexed(scores,'id',[s['score_id'] for s in receipt['scores']])
    for expected in receipt['scores']:
        actual=remote_scores[expected['score_id']];where='scores/'+expected['score_id']
        for key in ('name','value'):_equal(expected[key],actual.get(key),where+'/'+key)
        _metadata(expected['metadata'],actual.get('metadata'),where+'/metadata')
        _equal({'kind':'observation','id':expected['observation_id'],'traceId':expected['trace_id']},
               actual.get('subject'),where+'/subject')
    return logical_roots


def _retry(output,operation,attempts,delay_seconds):
    if type(attempts) is not int or not 1<=attempts<=6 or not 0<=delay_seconds<=10:
        raise ValueError('Readback retries must be bounded')
    paths=[]
    for number in range(attempts):
        try:return operation(paths),paths
        except Exception as error:
            path=output/f'langfuse-verification-failure-{uuid.uuid4().hex}.json'
            _save(path,{'attempt':number+1,'error_type':type(error).__name__,
                        'reason':str(error) if isinstance(error,VerificationError) else 'Readback operation failed'})
            paths.append(path)
            if number+1<attempts:time.sleep(delay_seconds)
    raise VerificationError('Langfuse readback did not verify; all attempts retained')


def _proof(output,kind,body,paths):
    value={**body,'kind':kind,'cli_version':CLI_VERSION,
           'readback_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    path=output/f'langfuse-{kind}-verified-{uuid.uuid4().hex}.json';_save(path,value)
    return {**body,'evidence_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'evidence_path':str(path)}


def verify_observations(receipt,context,*,query=None,attempts=6,delay_seconds=6):
    """Require full scoped observation and original-score readback before release."""
    output=_output(context);identity=_identity(context)
    _metadata(identity,receipt.get('metadata'),'receipt/metadata')
    if receipt.get('errors') or not receipt.get('observations'):
        raise VerificationError('Observer failed or supplied no observations')
    expected_ids=[r['id'] for r in receipt['observations']]
    trace_ids=sorted({r['trace_id'] for r in receipt['observations']})
    if len(set(expected_ids))!=len(expected_ids) or trace_ids!=sorted(receipt['trace_ids']):
        raise VerificationError('Local observation identity is inconsistent')
    for row in receipt['observations']:
        _metadata(identity,row['metadata'],'receipt/observation/metadata')
        if row['type']=='generation':
            key='turn_id' if row['name'] in ('metadata','shared_decision') else 'question_id'
            if not row['metadata'].get(key):raise VerificationError('Generation lacks its original work identity')
    query=query or _query_cli
    def operation(paths):
        keys=sorted({k for row in receipt['observations']
                     for k in (*row['metadata'],*_leaves(row['metadata']))})
        rows=_read(query,'observations',{'session-id':receipt['session_id'],
            'fields':'core,basic,io,metadata,model,usage,metrics,trace_context',
            'expand-metadata':','.join(keys),'limit':1000,'all':True,
            'max-items':len(expected_ids)+100},output,paths)
        scores=[];score_ids=[s['score_id'] for s in receipt['scores']]
        for start in range(0,len(score_ids),50):
            batch=score_ids[start:start+50]
            scores.extend(_read(query,'scores',{'id':','.join(batch),'fields':'details,subject',
                'limit':100,'all':True,'max-items':len(batch)+10},output,paths))
        roots=_check_observations(receipt,rows,scores)
        return {'verified':True,'trace_ids':trace_ids,'observation_count':len(rows),
                'score_count':len(scores),'identity':identity,'session_id':receipt['session_id'],
                'logical_root_parents':roots}
    value,paths=_retry(output,operation,attempts,delay_seconds)
    return _proof(output,'observations',value,paths)


def _check_experiments(views,imported,identity,experiments,items):
    ids={r['id'] for r in imported['experiments'].values()}
    remote=_indexed(experiments,'id',ids)
    if len(items)!=sum(len(v['individual_results']) for v in views.values()):
        raise VerificationError('Saved-result experiment question coverage is incomplete')
    if len({r['id'] for r in items})!=len(items):
        raise VerificationError('Saved-result experiment items are duplicated')
    for policy,view in views.items():
        saved=imported['experiments'][policy];actual=remote[saved['id']]
        # SDK5.1 .name identifies the logical group; modern API .name is .run_name.
        _equal(saved['run_name'],actual.get('name'),'experiment/name')
        _equal(len(view['individual_results']),actual.get('itemCount'),'experiment/itemCount')
        expected={**identity,'scoring_policy':policy,'scorer_sha256':view['scorer_sha256'],
                  'execution_mode':'imported_results'}
        _metadata(expected,actual.get('metadata'),'experiment/metadata')
        selected=[r for r in items if r.get('experimentId')==saved['id']]
        questions={r['question_id']:r for r in view['individual_results']}
        by_question={}
        for item in selected:
            value=item.get('input')
            if isinstance(value,str):value=json.loads(value)
            if not isinstance(value,dict):raise VerificationError('Experiment input is not a question object')
            by_question[value.get('question_id')]=item
        if len(by_question)!=len(selected) or set(by_question)!=set(questions):
            raise VerificationError('Experiment question identities differ from saved predictions')
        for key,row in questions.items():
            item=by_question[key];where='experiment-items/'+key
            _equal({'question':row['qa'].get('question',''),'question_id':key},item.get('input'),where+'/input')
            _equal(row['prediction'],item.get('output'),where+'/output')
            _equal(row['reference'],item.get('expectedOutput'),where+'/reference')
            _metadata({**expected,'question_id':key,'category':row['qa']['category'],
                       'original_record':row},item.get('experimentItemMetadata'),where+'/metadata')
            _metadata(expected,item.get('experimentMetadata'),where+'/experimentMetadata')
            scores=item.get('scores')
            if not isinstance(scores,list):raise VerificationError('Experiment scores are missing')
            by_name=_indexed(scores,'name',row['metrics'])
            for name,value in row['metrics'].items():_equal(value,by_name[name].get('value'),where+'/scores/'+name)


def import_and_verify_results(views,context,*,client=None,query=None,attempts=6,delay_seconds=6):
    """Import immutable saved results once, then require visible Experiments and scores.

    A recorded completed import can be re-read. An interrupted import claim is
    deliberately not retried automatically: it might already have reached cloud.
    """
    output=_output(context);identity=_identity(context);before=fingerprint(views)
    policies={'author-corrected-v1','author-legacy-c5-v1'}
    if set(views)!=policies or any(not v.get('individual_results') for v in views.values()):
        raise VerificationError('Both nonempty saved scoring views are required')
    claim_path=output/'langfuse-import-claim.json';import_path=output/'langfuse-imported.json'
    expected_claim={'identity':identity,'results_sha256':before}
    if claim_path.exists():
        claim=json.loads(claim_path.read_text())
        _metadata(expected_claim,claim,'import-claim')
        if not import_path.exists():
            raise VerificationError('A prior import may be partial; automatic re-import is prohibited')
        imported=json.loads(import_path.read_text())
        _metadata(expected_claim,imported,'imported-results')
    else:
        claim={**expected_claim,'from_start_time':(datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat()}
        _save(claim_path,claim)
        from .reporting import export_experiments
        metadata={**identity,**{k:context['binding'][k] for k in
                  ('config_sha256','source_sha256','max_output_tokens_by_stage') if k in context['binding']}}
        policy=context['binding'].get('support_migration',{}).get('observability',{}).get('policy')
        if policy is not None:
            metadata['observability_policy']=policy
        results=export_experiments(views,client=client,export_authorized=True,metadata=metadata)
        if fingerprint(views)!=before:raise VerificationError('Saved predictions changed during import')
        imported={**claim,'experiments':{policy:{'id':result.experiment_id,'name':result.name,
                  'run_name':result.run_name,'url':result.experiment_url} for policy,result in results.items()}}
        if set(imported['experiments'])!=policies or any(not r['id'] or not r['name'] or not r['run_name']
                                                       for r in imported['experiments'].values()):
            raise VerificationError('SDK import returned incomplete experiment identities')
        _save(import_path,imported)
    if any(not row.get('run_name') for row in imported['experiments'].values()):
        raise VerificationError('Saved SDK import lacks the exact run name; existing evidence is immutable')
    if len({r['id'] for r in imported['experiments'].values()})!=len(policies):
        raise VerificationError('Scoring policies share an experiment identity')
    query=query or _query_cli
    ids=','.join(r['id'] for r in imported['experiments'].values())
    def operation(paths):
        experiments=_read(query,'experiments',{'id':ids,'from-start-time':claim['from_start_time'],
            'fields':'core,metadata,scores','limit':100,'all':True,'max-items':len(policies)+10},output,paths)
        items=_read(query,'experiment-items',{'experiment-id':ids,
            'from-start-time':claim['from_start_time'],
            'fields':'core,io,metadata,itemMetadata,experimentMetadata,scores',
            'score-limit':50,'limit':100,'all':True,
            'max-items':sum(len(v['individual_results']) for v in views.values())+100},output,paths)
        _check_experiments(views,imported,identity,experiments,items)
        if fingerprint(views)!=before:raise VerificationError('Saved predictions changed during readback')
        return {'verified':True,'experiment_ids':{p:r['id'] for p,r in imported['experiments'].items()},
                'experiment_urls':{p:r['url'] for p,r in imported['experiments'].items()},
                'results_sha256':before,'identity':identity}
    value,paths=_retry(output,operation,attempts,delay_seconds)
    return _proof(output,'experiments',value,paths)
