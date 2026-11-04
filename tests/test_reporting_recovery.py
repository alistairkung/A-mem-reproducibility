"""Reporting failures cannot regenerate models or overwrite scientific evidence."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from amem_repro.config import fingerprint
from amem_repro.langfuse_verify import VerificationError
from scripts.run2_reporting_recovery import recover, recovery_plan, RECOVERY_ID, POLICIES


def fixture(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = Path('artifacts/run2/reporting-recovery') / RECOVERY_ID
    identity = {'campaign_id': 'amem-run2-20261103-v1', 'condition': 'full',
        'population': 'fallback', 'run_id': 'run2-full-conv-44-r0-p2',
        'conversation_id': 'conv-44', 'repetition': 0,
        'provider_contract_policy': 'canonical-index-strings-v1',
        'manifest_sha256': 'b9d41746ba8eac2b94d401570e9083b24ed1d3f2d20a9ece1de68600f33ad8a3'}
    views = {p: {'scoring_policy': p, 'scorer_sha256': 'a'*64,
        'individual_results': [{'question_id': f'conv-44:qa:{i}',
            'prediction': '  exact saved response  ', 'reference': 'saved reference',
            'qa': {'question': f'q{i}', 'category': 1}, 'metrics': {'f1': .5, 'bleu1': .2},
            'provider_contract_policy': identity['provider_contract_policy']}
            for i in range(158)]} for p in POLICIES}
    original = {'identity': identity, 'results_sha256': fingerprint(views),
        'from_start_time': '2026-11-03T13:59:00Z',
        'experiments': {p: {'id': 'old-'+p, 'name': 'A-MEM/'+p} for p in POLICIES}}
    traces = {f'conv-44:qa:{i}': f'{i+1:032x}' for i in range(158)}
    class Cloud:
        def __init__(self): self.calls=[]; self.experiments=[]; self.items=[]; self.scores=[]; self.fail=False; self.mutation=None
        def flush(self): pass
        def run_experiment(self, **kw):
            self.calls.append(kw)
            self.experiments.append({'id': kw['experiment_id'], 'name': kw['run_name'],
                'itemCount': len(kw['data']), 'metadata': kw['metadata']})
            for i, item in enumerate(kw['data']):
                trace = f'{len(self.calls)*1000+i:032x}'
                scores=[]
                for j, evaluator in enumerate(kw['evaluators']):
                    value = evaluator(metadata=item['metadata'])
                    if value is not None:
                        score={'id': f'{trace}/{j}', 'name':value.name, 'value':value.value,
                               'subject': {'kind':'observation', 'id':f'{trace}/item', 'traceId':trace}}
                        scores.append(score);self.scores.append(score)
                self.items.append({'id': f'{trace}/item', 'experimentId': kw['experiment_id'],
                    'experimentItemId': hashlib.sha256(__import__('langfuse')._client.attributes._serialize(item['input']).encode()).hexdigest()[:16],
                    'traceId':trace, 'input':item['input'], 'output':kw['task'](item=item),
                    'expectedOutput':item['expected_output'], 'experimentItemMetadata':item['metadata'],
                    'experimentMetadata':kw['metadata'], 'scores':scores})
                if self.fail: raise RuntimeError('interrupted after a partial write')
            return NS(experiment_id=kw['experiment_id'], run_name=kw['run_name'],
                      experiment_url='https://example.test', item_results=[NS(trace_id=i['traceId']) for i in self.items])
        def query(self, resource, options):
            ids=options.get('experiment-id',options.get('id','')).split(',')
            data = self.experiments if resource=='experiments' else self.items if resource=='experiment-items' else self.scores
            if resource=='experiments': data=[x for x in data if x['id'] in ids]
            elif resource=='experiment-items': data=[x for x in data if x['experimentId'] in ids]
            elif 'trace-id' in options:
                data=[x for x in data if x['subject']['traceId'] in options['trace-id'].split(',')]
            elif not any(x['id'] in ids for x in self.experiments):data=[]
            data=copy.deepcopy(data)
            if self.mutation: self.mutation(resource, data)
            return {'status':200,'body':{'data':data, 'meta':{'truncated':False}}}
    cloud=Cloud()
    def run():
        return recover(views, original, output, original_trace_ids=traces,
                       original_binding={'config_sha256':'b'*64, 'source_sha256':'c'*64,
                         'max_output_tokens_by_stage':{'shared_decision':8192}}, client=cloud,
                       query=cloud.query, attempts=1, delay_seconds=0)
    return views, original, traces, output, cloud, run


def test_exact_import_readonly_resume_and_immutable_results(tmp_path, monkeypatch):
    views, original, traces, output, cloud, run=fixture(tmp_path,monkeypatch)
    before=copy.deepcopy((views,original,traces))
    proof=run()
    assert proof['item_count']==316 and proof['score_count']==632 and proof['trace_count']==316
    assert proof['status']=='Degraded' and not proof['usable_for_next_phase']
    assert len(cloud.calls)==2
    assert run()['verified'] and len(cloud.calls)==2
    assert (views,original,traces)==before
    assert json.loads((output/'pre-ingestion-inventory.json').read_text())['recovery_counts']==[0,0,0]


def test_partial_write_never_reingests_on_resume(tmp_path,monkeypatch):
    *_,cloud,run=fixture(tmp_path,monkeypatch);cloud.fail=True
    with pytest.raises(RuntimeError):run()
    assert len(cloud.calls)==1 and len(cloud.items)==1
    cloud.fail=False
    with pytest.raises(VerificationError):run()
    assert len(cloud.calls)==1 and len(cloud.items)==1


@pytest.mark.parametrize('mode',['foreign_campaign','foreign_run','missing_question','score_change',
                                'duplicate_item','duplicate_score','foreign_item_id','foreign_trace','wrong_observation','missing_binding','missing_original_trace'])
def test_readback_mismatch_blocks_acceptance(tmp_path,monkeypatch,mode):
    *_,cloud,run=fixture(tmp_path,monkeypatch)
    assert run()['verified']
    def mutate(resource, data):
        if resource=='experiment-items':
            if mode=='foreign_campaign':data[0]['experimentItemMetadata']['campaign_id']='run1'
            if mode=='foreign_run':data[0]['experimentItemMetadata']['run_id']='run1'
            if mode=='missing_question':data.pop()
            if mode=='score_change':data[0]['scores'][0]['value']=0
            if mode=='duplicate_item':data.append(data[0])
            if mode=='foreign_item_id':data[0]['experimentItemId']='foreign-item'
            if mode=='missing_binding':data[0]['experimentItemMetadata'].pop('source_sha256')
            if mode=='missing_original_trace':data[0]['experimentItemMetadata'].pop('original_trace_id')
        if resource=='scores':
            if mode=='duplicate_score':data.append(data[0])
            if mode=='foreign_trace':data[0]['subject']['traceId']='wrong'
            if mode=='wrong_observation':data[0]['subject']['id']='wrong'
    cloud.mutation=mutate
    with pytest.raises(VerificationError):run()
    assert len(cloud.calls)==2


@pytest.mark.parametrize('field',['campaign_id','run_id','manifest_sha256','condition'])
def test_run1_or_other_identity_cannot_enter_recovery(tmp_path,monkeypatch,field):
    views,original,traces,_,cloud,run=fixture(tmp_path,monkeypatch)
    original['identity'][field]='run1'
    with pytest.raises(VerificationError):run()
    assert not cloud.calls


def test_unclaimed_preexisting_recovery_is_rejected(tmp_path,monkeypatch):
    views,original,traces,_,cloud,run=fixture(tmp_path,monkeypatch)
    plan=recovery_plan(views,original,traces)
    cloud.experiments=[{'id':plan['experiments'][POLICIES[0]]['id']}]
    with pytest.raises(VerificationError,match='already has cloud writes'):run()
    assert not cloud.calls


def test_completed_writes_can_resume_without_sdk_return_receipt(tmp_path,monkeypatch):
    *_,output,cloud,run=fixture(tmp_path,monkeypatch)
    run();(output/'sdk-returned.json').unlink()
    assert run()['verified'] and len(cloud.calls)==2


def test_local_experiment_score_filter_can_be_empty_but_explicit_traces_verify(tmp_path,monkeypatch):
    views,original,traces,output,cloud,run=fixture(tmp_path,monkeypatch)
    original_query=cloud.query
    def query(resource,options):
        if resource=='scores' and 'experiment-id' in options:
            return {'status':200,'body':{'data':[], 'meta':{'truncated':False}}}
        if resource=='scores':assert len(options['trace-id'].split(','))<=50
        return original_query(resource,options)
    cloud.query=query
    assert run()['score_count']==632
    assert run()['verified'] and len(cloud.calls)==2


def test_reporting_process_removes_provider_credentials_and_denies_provider_import_and_dns(tmp_path,monkeypatch):
    import importlib.util
    import os
    import socket
    import sys
    script=Path(__file__).resolve().parents[1]/'scripts/recover-run2-reporting.py'
    spec=importlib.util.spec_from_file_location('reporting_launcher',script)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'ROOT',tmp_path)
    (tmp_path/'.env').write_text('LANGFUSE_BASE_URL=https://cloud.langfuse.com\nDEEPSEEK_API_KEY=forbidden\n')
    monkeypatch.setenv('DEEPSEEK_API_KEY','forbidden')
    monkeypatch.setattr(sys,'meta_path',list(sys.meta_path))
    monkeypatch.setattr(socket,'getaddrinfo',lambda *args,**kw:[])
    # The launcher owns the final patch; ensure pytest restores it afterwards.
    monkeypatch.setattr(socket,'getaddrinfo',socket.getaddrinfo)
    module.reporting_environment()
    assert 'DEEPSEEK_API_KEY' not in os.environ
    with pytest.raises(PermissionError):socket.getaddrinfo('api.deepseek.com',443)
    with pytest.raises(PermissionError):sys.meta_path[0].find_spec('openai')
    with pytest.raises(PermissionError):sys.meta_path[0].find_spec('amem_repro.run2')
    with pytest.raises(PermissionError):sys.meta_path[0].find_spec('amem_repro.adapter')
    assert socket.getaddrinfo('cloud.langfuse.com',443)==[]


@pytest.mark.parametrize('mode',['missing_all','missing_launcher','changed_source','failed_review','wrong_revision'])
def test_reporting_release_requires_complete_current_source_and_independent_reviews(tmp_path,monkeypatch,mode):
    import hashlib
    import importlib.util
    script=Path(__file__).resolve().parents[1]/'scripts/recover-run2-reporting.py'
    spec=importlib.util.spec_from_file_location('approval_launcher',script)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'ROOT',tmp_path)
    approval={'authorized':True,'model_calls':0,'max_imports':1,'max_incremental_langfuse_usd':0,
              'recovery_import_id':RECOVERY_ID,'merge_commit':'a'*40,'reviewed_commit':'b'*40,'files':{}}
    for name in module.APPROVAL_FILES:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True)
        if name.endswith('-review.json'):
            path.write_text(json.dumps({'verdict':'pass','reviewed_commit':'b'*40}))
        else:path.write_text('bound original content')
        approval['files'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(module.subprocess,'run',lambda *a,**kw:None)
    if mode=='missing_all':approval['files']={}
    if mode=='missing_launcher':approval['files'].pop('scripts/recover-run2-reporting.py')
    if mode=='changed_source':(tmp_path/'amem_repro/reporting.py').write_text('changed after review')
    if mode in ('failed_review','wrong_revision'):
        p=tmp_path/'artifacts/run2/reporting-recovery/spec-review.json'
        p.write_text(json.dumps({'verdict':'changes_requested' if mode=='failed_review' else 'pass',
                                'reviewed_commit':'c'*40 if mode=='wrong_revision' else 'b'*40}))
        approval['files'][str(p.relative_to(tmp_path))]=hashlib.sha256(p.read_bytes()).hexdigest()
    p=tmp_path/'artifacts/run2/reporting-recovery/approved-reporting.json';p.write_text(json.dumps(approval))
    with pytest.raises(ValueError):module.verify_approval()
