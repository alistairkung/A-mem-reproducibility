"""Source-bound real-runner Langfuse gate. All model requests are in-process mocks."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import socket
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]


def main(output):
    from dotenv import dotenv_values
    from amem_repro.preflight import asset_environment
    os.environ.update(asset_environment(ROOT/'artifacts/assets'))
    for name in list(os.environ):
        if any(k in name.upper() for k in ('OPENAI_API','DEEPSEEK','OPENROUTER','LANGFUSE','OTEL_')):
            os.environ.pop(name)
    values=dotenv_values(ROOT/'.env')
    for name in ('LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY','LANGFUSE_BASE_URL','LANGFUSE_HOST'):
        if values.get(name):os.environ[name]=values[name]
    host=os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST')
    if host!='https://cloud.langfuse.com':raise RuntimeError('Wrong Langfuse host')
    os.environ['LANGFUSE_OTEL_MAX_BATCH_SIZE_BYTES']=str(32*1024*1024)
    original_dns=socket.getaddrinfo
    def dns(host,*args,**kwargs):
        if host not in ('cloud.langfuse.com',b'cloud.langfuse.com'):
            raise PermissionError('Gate permits no model/network endpoint')
        return original_dns(host,*args,**kwargs)
    socket.getaddrinfo=dns
    from langfuse import Langfuse
    from amem_repro.observation_policy import should_export_span
    from amem_repro.observability import LangfuseObserver
    from amem_repro.config import fingerprint,source_fingerprint
    from amem_repro.openrouter import CAMPAIGN,SCIENTIFIC_BINDING,ABLATION_CONDITIONS,save_new
    from amem_repro.measurements import TokenCounter
    from amem_repro.replay import memory_view
    from amem_repro.langfuse_verify import verify_observations
    from amem_repro.gpt4omini_reporting import import_results,original_qa_traces
    from amem_repro.gpt4omini_campaign import inventory
    from gpt4omini_fixture import run_fixture
    from gpt4omini_executor_fixture import run_actual_phase
    import tiktoken
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    source=fingerprint(source_fingerprint(ROOT))
    client=Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],secret_key=os.environ['LANGFUSE_SECRET_KEY'],
        base_url=host,flush_at=16,should_export_span=should_export_span,environment='amem-gpt4omini-gate',release=source)
    enc=tiktoken.get_encoding('o200k_base')
    counter=TokenCounter(lambda text:enc.encode(text,disallowed_special=()),
                         'tiktoken o200k_base; API usage authoritative',__import__('importlib.metadata').metadata.version('tiktoken'))
    def state(value):
        saved=copy.deepcopy(value);saved.pop('build_failures',None);return memory_view(saved)
    metadata={**SCIENTIFIC_BINDING,'source_sha256':source,'condition':'full','population':'smoke',
        'manifest_sha256':fingerprint(json.loads((ROOT/'manifests/smoke.json').read_text())),
        'repetition':0,'conversation_id':'conv-26','provider_contract_policy':'strict-original-v1',
        'run_id':output.name+'-real-runner','observability_policy':'run2-audit-essential-v1',
        'execution_mode':'offline-saved-response-gate'}
    try:
        reference=run_fixture(output/'reference',use_runtime_assets=True,token_counter=counter)
        observer=LangfuseObserver(client,metadata)
        traced=run_fixture(output/metadata['run_id'],observer=observer,
            records=reference['generations'],use_runtime_assets=True,token_counter=counter)
        candidate=run_fixture(output/'candidate',records=reference['generations'],candidate=True,
                              use_runtime_assets=True,token_counter=counter)
        if not (reference['requests']==traced['requests']==candidate['requests']
                and reference['results']==traced['results']==candidate['results']
                and reference['views']==traced['views']==candidate['views']
                and state(reference['state'])==state(traced['state'])==state(candidate['state'])):
            raise RuntimeError('Native original/candidate/tracing equivalence failed')
        capture=observer.finish();save_new(output/'trace-capture.json',capture)
        context={'binding':metadata,'output_dir':str(output)}
        runtime=verify_observations(capture,context)
        experiments=import_results(traced['views'],context,client=client,traces=original_qa_traces(capture))
        save_new(output/'scoring-views.json',traced['views'])
        phases=[];ledger=None;parent=None
        for seq in range(3):
            phase=run_actual_phase(output/'executor',root=ROOT,phase=f'{output.name}-p{seq}',
                ledger=ledger,parent=parent,fail_decisions={2:'length'},cloud_client=client,
                real_cloud=True,runtime_assets=True)
            parent=phase['receipt'];ledger=phase['ledger'];phases.append(parent)
            if not parent['recoverable_length_failure'] or parent['notes']!=2*(seq+1):
                raise RuntimeError('Actual executor checkpoint/observation gate failed')
        if ledger.totals()['attempts']!=12:raise RuntimeError('Duplicate checkpoint transmission')
        ablated=[]
        for condition in ABLATION_CONDITIONS:
            leaf=None;accounting=None
            for seq in range(3):
                actual=run_actual_phase(output/condition,root=ROOT,phase=f'{output.name}-{condition}-p{seq}',
                    ledger=accounting,parent=leaf,fail_decisions={1:'malformed',2:'length'},
                    cloud_client=client,real_cloud=True,runtime_assets=True,
                    conversation='conv-49',condition=condition)
                leaf=actual['receipt'];accounting=actual['ledger']
                if not leaf['recoverable_length_failure'] or (leaf['notes'],leaf['evolution_counter'])!=(2*(seq+1),0):
                    raise RuntimeError('Ablation original fallback/checkpoint cloud gate failed')
            if accounting.totals()['attempts']!=12:raise RuntimeError('Ablation repeated a processed request')
            ablated.append(condition)
        result={'campaign_id':CAMPAIGN,'source_sha256':source,'real_runner':True,
            'native_contracts_verified':True,'remote_observations_verified':runtime['verified'],
            'experiments_verified':experiments['verified'],'replay_equivalence':True,
            'full_action_equivalence':True,'two_actual_checkpoint_continuations':True,
            'ablated_checkpoint_conditions':ablated,
            'network_llm_requests':0,'mock_native_completions':44*3+48,
            'observability_policy':'run2-audit-essential-v1','flush_at':16,
            'runtime':runtime,'experiments':experiments,'executor_phases':phases,
            'gate_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'fixture_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (ROOT/'tests/gpt4omini_fixture.py',ROOT/'tests/gpt4omini_executor_fixture.py')}}
        result['files']=inventory(output)
        save_new(output/'receipt.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('files','executor_phases')}),flush=True)
    finally:client.shutdown()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    main(parser.parse_args().output)
