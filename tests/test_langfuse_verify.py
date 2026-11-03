"""Cloud acceptance is a readback assertion, never a flush/authentication check."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from amem_repro.langfuse_verify import verify_observations, VerificationError


def fixture(tmp_path):
    output=tmp_path/'artifacts/run2/runs/fixture';output.mkdir(parents=True)
    identity={'campaign_id':'run2-fixture','condition':'full','population':'smoke',
              'manifest_sha256':'a'*64,'repetition':0,'run_id':'fixture',
              'conversation_id':'conv-26','provider_contract_policy':'canonical-index-strings-v1'}
    context={**{k:identity[k] for k in ('campaign_id','condition','run_id','conversation_id')},
             'output_dir':str(output),'binding':copy.deepcopy(identity)}
    row={'id':'observation-1','trace_id':'trace-1','parent_observation_id':None,
         'session_id':'run2-fixture/full/conv-26/0/fixture','name':'shared_decision','type':'generation',
         'input':{'prompt':'exact prompt','response_format':{'type':'json_schema'}},
         'output':{'provider_arguments':' { "answer": "exact" } ', 'accepted':True},
         'metadata':{**identity,'turn_id':'D1:1','compatibility_deviation':{'original':'0','validation_copy':0}},
         'model':'deepseek-flash','model_parameters':{'temperature':.7,'max_tokens':8192,'thinking':'disabled'},
         'usage_details':{'input':3,'output':2,'total':5},'cost_details':{'total':.000004},'level':'WARNING'}
    score={'score_id':'score-1','name':'f1','value':.5,'trace_id':'trace-1','observation_id':'observation-1',
           'metadata':{**identity,'question_id':'conv-26:0','scoring_policy':'author-corrected-v1'}}
    receipt={'metadata':identity,'session_id':row['session_id'],'trace_ids':['trace-1'],
             'observations':[row],'scores':[score],'errors':[],'cloud_visibility_verified':False}
    remote={'id':row['id'],'traceId':row['trace_id'],'parentObservationId':None,'sessionId':row['session_id'],
            'name':row['name'],'type':'GENERATION','input':copy.deepcopy(row['input']),
            'output':copy.deepcopy(row['output']),'metadata':copy.deepcopy(row['metadata']),
            'model':row['model'],'modelParameters':copy.deepcopy(row['model_parameters']),
            'usageDetails':copy.deepcopy(row['usage_details']),'costDetails':copy.deepcopy(row['cost_details']),
            'level':'WARNING','latency':.01}
    remote_score={'id':'score-1','name':'f1','value':.5,'metadata':score['metadata'],
                  'subject':{'kind':'observation','id':'observation-1','traceId':'trace-1'}}
    def query(resource,options):
        return {'status':200,'body':{'data':copy.deepcopy([remote] if resource=='observations' else [remote_score]),
                                  'meta':{'truncated':False}}}
    return receipt,context,remote,remote_score,query


def test_remote_io_usage_audit_and_scores_are_required(tmp_path):
    receipt,context,remote,score,query=fixture(tmp_path)
    original=copy.deepcopy(receipt)
    proof=verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)
    assert proof['verified'] is True and proof['trace_ids']==['trace-1']
    assert len(proof['evidence_sha256'])==64
    assert receipt==original
    assert list(Path(context['output_dir']).glob('langfuse-*'))


def test_a_flush_receipt_without_cloud_observations_is_rejected(tmp_path):
    receipt,context,*_=fixture(tmp_path)
    query=lambda *a:{'status':200,'body':{'data':[],'meta':{'truncated':False}}}
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)


@pytest.mark.parametrize('field', ['output','raw_whitespace','input','metadata','usage','cost','model','hierarchy','score','score_identity','truncated'])
def test_scientifically_meaningful_readback_differences_stop_release(tmp_path,field):
    receipt,context,remote,score,query=fixture(tmp_path)
    if field=='output':remote['output']['accepted']=False
    elif field=='raw_whitespace':remote['output']['provider_arguments']='{"answer":"exact"}'
    elif field=='input':remote['input']['prompt']='changed prompt'
    elif field=='metadata':remote['metadata']['condition']='neither'
    elif field=='usage':remote['usageDetails']['input']=4
    elif field=='cost':remote['costDetails']['total']=0
    elif field=='model':remote['model']='another model'
    elif field=='hierarchy':remote['parentObservationId']='unexpected parent'
    elif field=='score':score['value']=0
    elif field=='score_identity':score['subject']['traceId']='another trace'
    original=query
    if field=='truncated':
        def query(*args):
            payload=original(*args);payload['body']['meta']['truncated']=True;return payload
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)
    assert list(Path(context['output_dir']).glob('langfuse-verification-failure-*'))


def test_boolean_usage_cannot_masquerade_as_an_integer_count(tmp_path):
    receipt,context,remote,score,query=fixture(tmp_path)
    receipt['observations'][0]['usage_details']={'input':1,'output':2,'total':3}
    remote['usageDetails']={'input':True,'output':2,'total':3}
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)


def test_sdk_trace_context_synthetic_parent_is_a_verified_logical_root(tmp_path):
    receipt,context,remote,score,query=fixture(tmp_path)
    remote['parentObservationId']='sdk-generated-unexported-parent'
    remote['isRootObservation']=True
    proof=verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)
    assert proof['logical_root_parents']=={'observation-1':'sdk-generated-unexported-parent'}


def test_sdk_flattened_metadata_is_compared_losslessly(tmp_path):
    receipt,context,remote,score,query=fixture(tmp_path)
    remote['metadata'].pop('compatibility_deviation')
    remote['metadata'].update({'compatibility_deviation.original':'0',
                               'compatibility_deviation.validation_copy':0})
    assert verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)['verified']
    remote['metadata']['compatibility_deviation.original']='00'
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)


def test_score_readback_uses_bounded_exact_ids_instead_of_session_semantics(tmp_path):
    receipt,context,remote,score,_=fixture(tmp_path)
    receipt['scores']=[{**copy.deepcopy(receipt['scores'][0]),'score_id':f'score-{i}'} for i in range(56)]
    queries=[]
    def query(resource,options):
        if resource=='observations':data=[remote]
        else:
            assert 'session-id' not in options
            ids=options['id'].split(',');assert len(ids)<=50;queries.extend(ids)
            data=[{**copy.deepcopy(score),'id':key} for key in ids]
        return {'status':200,'body':{'data':data,'meta':{'truncated':False}}}
    result=verify_observations(receipt,context,query=query,attempts=1,delay_seconds=0)
    assert result['score_count']==56 and len(queries)==len(set(queries))==56


def saved_views():
    result={}
    for policy in ('author-corrected-v1','author-legacy-c5-v1'):
        result[policy]={'scoring_policy':policy,'scorer_sha256':'b'*64,
                       'individual_results':[{'question_id':'conv-26:0','prediction':'saved prediction',
                         'reference':'saved reference','provider_contract_policy':'canonical-index-strings-v1',
                         'qa':{'question':'original question','category':1},
                         'metrics':{'f1':.5,'bleu1':.25},'metric_failures':[]}],
                       'aggregate_metrics':{}}
    return result


class ImportClient:
    def __init__(self):self.calls=[]
    def run_experiment(self,**kwargs):
        self.calls.append(kwargs)
        for item in kwargs['data']:
            assert kwargs['task'](item=item)=='saved prediction'
            for evaluate in kwargs['evaluators']:
                assert evaluate(metadata=item['metadata']).value in (.5,.25)
        return NS(experiment_id=f'exp-{len(self.calls)}',experiment_url='https://example.test/experiment',name=kwargs['name'])
    def flush(self):pass


def import_query(client):
    def query(resource,options):
        rows=[]
        for index,call in enumerate(client.calls,1):
            if resource=='experiments':
                rows.append({'id':f'exp-{index}','name':call['name'],'itemCount':len(call['data']),
                             'metadata':call['metadata']})
            else:
                for item in call['data']:
                    metrics=item['metadata']['original_record']['metrics']
                    rows.append({'id':f'item-{index}','experimentId':f'exp-{index}',
                                 'input':item['input'],'output':'saved prediction',
                                 'expectedOutput':item['expected_output'],
                                 'experimentItemMetadata':item['metadata'],
                                 'experimentMetadata':call['metadata'],
                                 'scores':[{'name':k,'value':v} for k,v in metrics.items()]})
        return {'status':200,'body':{'data':rows,'meta':{'truncated':False}}}
    return query


def test_import_reads_saved_predictions_and_metrics_once_across_readback_retries(tmp_path,monkeypatch):
    from amem_repro.langfuse_verify import import_and_verify_results
    from amem_repro.config import fingerprint
    _,context,*_=fixture(tmp_path);views=saved_views();original=copy.deepcopy(views);client=ImportClient()
    good=import_query(client);reads=[]
    def query(resource,options):
        reads.append(resource)
        return {'status':200,'body':{'data':[],'meta':{'truncated':False}}} if len(reads)==1 else good(resource,options)
    result=import_and_verify_results(views,context,client=client,query=query,attempts=2,delay_seconds=0)
    assert result['verified'] and result['results_sha256']==fingerprint(views)
    assert len(client.calls)==2 and views==original
    # A repeated verification reuses the recorded import, not another SDK run.
    again=import_and_verify_results(views,context,client=client,query=good,attempts=1,delay_seconds=0)
    assert again['experiment_ids']==result['experiment_ids'] and len(client.calls)==2


@pytest.mark.parametrize('difference',['prediction','reference','score','question','policy','missing_experiment','extra_item'])
def test_saved_result_import_requires_exact_remote_views(tmp_path,difference):
    from amem_repro.langfuse_verify import import_and_verify_results
    _,context,*_=fixture(tmp_path);client=ImportClient();good=import_query(client)
    def query(resource,options):
        response=good(resource,options);rows=response['body']['data']
        if resource=='experiments' and difference=='missing_experiment':rows.pop()
        if resource=='experiment-items':
            if difference=='prediction':rows[0]['output']='changed'
            elif difference=='reference':rows[0]['expectedOutput']='changed'
            elif difference=='score':rows[0]['scores'][0]['value']=0
            elif difference=='question':rows[0]['input']={**rows[0]['input'],'question_id':'different'}
            elif difference=='policy':rows[0]['experimentMetadata']={**rows[0]['experimentMetadata'],'scoring_policy':'different'}
            elif difference=='extra_item':rows.append(copy.deepcopy(rows[0]))
        return response
    with pytest.raises(VerificationError):
        import_and_verify_results(saved_views(),context,client=client,query=query,attempts=2,delay_seconds=0)
    assert len(client.calls)==2


def test_partial_import_is_not_reexecuted_and_changed_views_cannot_reuse_import(tmp_path):
    from amem_repro.langfuse_verify import import_and_verify_results
    _,context,*_=fixture(tmp_path)
    class BrokenClient(ImportClient):
        def run_experiment(self,**kwargs):
            super().run_experiment(**kwargs)
            raise RuntimeError('simulated failure after export may have reached cloud')
    broken=BrokenClient()
    with pytest.raises(RuntimeError):
        import_and_verify_results(saved_views(),context,client=broken,query=lambda *a:None,attempts=1)
    replacement=ImportClient()
    with pytest.raises(VerificationError,match='partial'):
        import_and_verify_results(saved_views(),context,client=replacement,query=lambda *a:None,attempts=1)
    assert not replacement.calls
    changed=saved_views();changed['author-corrected-v1']['individual_results'][0]['prediction']='changed'
    with pytest.raises(VerificationError):
        import_and_verify_results(changed,context,client=replacement,query=lambda *a:None,attempts=1)


def test_real_cli_seam_omits_headers_strips_llm_keys_and_redacts_lf_values(tmp_path,monkeypatch):
    import amem_repro.langfuse_verify as verification
    receipt,context,remote,score,fake=fixture(tmp_path)
    monkeypatch.setenv('LANGFUSE_PUBLIC_KEY','fixture-public-key')
    monkeypatch.setenv('LANGFUSE_SECRET_KEY','fixture-secret-key')
    monkeypatch.setenv('LANGFUSE_BASE_URL','https://example.invalid')
    monkeypatch.setenv('DEEPSEEK_API_KEY','must-not-reach-cli')
    monkeypatch.setenv('OPENAI_API_KEY','must-not-reach-cli')
    remote['metadata']['extra']='fixture-secret-key'
    def process(command,*,env,**kwargs):
        assert not any('DEEPSEEK' in k or 'OPENAI_API' in k for k in env)
        assert 'fixture-secret-key' not in command
        assert 'langfuse-cli@1.2.4' in command
        resource=command[command.index('api')+1]
        data=fake(resource,{})
        data['headers']={'Authorization':'must-not-be-saved'}
        return NS(returncode=0,stdout=json.dumps(data))
    monkeypatch.setattr(verification.subprocess,'run',process)
    assert verify_observations(receipt,context,attempts=1,delay_seconds=0)['verified']
    logs=''.join(p.read_text() for p in Path(context['output_dir']).glob('*.json'))
    assert 'fixture-secret-key' not in logs and 'must-not-be-saved' not in logs
    assert '[redacted]' in logs


def test_observer_failure_or_foreign_identity_is_rejected_before_query(tmp_path):
    receipt,context,*_=fixture(tmp_path)
    def forbidden(*args):raise AssertionError('query must not be called')
    receipt['errors']=[{'operation':'flush','error_type':'RuntimeError'}]
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=forbidden,attempts=1)
    receipt['errors']=[];receipt['metadata']['condition']='neither'
    with pytest.raises(VerificationError):
        verify_observations(receipt,context,query=forbidden,attempts=1)
