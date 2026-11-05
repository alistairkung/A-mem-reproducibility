"""Review-only helper: actual production execute_phase, original author, no network.

Import with PYTHONPATH=<worktree>:<worktree>/tests:/private/tmp. The supplied
root is the worktree. Failures are relative to this phase's decision count.
No helper-created fake checkpoint or fake receipt bypasses production functions.
"""
import copy,json,hashlib
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import httpx,numpy as np
from amem_repro.gpt4omini_campaign import execute_phase
from amem_repro.openrouter import (cell_store,cell_key,cell_parts,CELL_ORDER,ablation_policy,predecessor_filename,
                                  CampaignLedger,SCIENTIFIC_BINDING,MODEL,save_new)
from amem_repro.config import fingerprint,source_fingerprint
from amem_repro.measurements import TokenCounter
from amem_repro.observability import LangfuseObserver
from amem_repro.scoring import AuthorScorer
from amem_repro.artifacts import RunLedger
from test_foundation import Provider,original_memory_module,LocalRetriever
from test_observability import Client
from test_scoring import dependencies


def seed_predecessors(ledger, key):
    """Labelled offline financial prerequisites, never copied scientific memory."""
    previous=CELL_ORDER[:CELL_ORDER.index(key)]
    seals={}
    save_new(ledger.root/'fixture.json',{'synthetic_offline_ancestry':True})
    evidence_hash=hashlib.sha256((ledger.root/'fixture.json').read_bytes()).hexdigest()
    for index,prior in enumerate(previous):
        conversation,condition=cell_parts(prior)
        auth={'approved':True,'binding':{**ledger.binding,'conversation_id':conversation,'condition':condition},
              'phase':'synthetic-'+prior,'kind':'baseline','condition':condition,'conversation':conversation}
        seal=fingerprint({'synthetic_completed_predecessor':prior});seals[prior]=seal
        with ledger.transaction() as db:
            db.execute('INSERT INTO phases VALUES (?,?,NULL,?,?)',
                       (auth['phase'],json.dumps(auth,sort_keys=True),'complete',seal))
            history=ledger.access_snapshot(db)
        files={}
        for axis in ('spec','standards'):
            p=ledger.root/'outcomes'/prior/f'acceptance-{axis}.json'
            save_new(p,{'synthetic':True,'evidence_files':{'fixture.json':evidence_hash}})
            files[str(p.relative_to(ledger.root))]=hashlib.sha256(p.read_bytes()).hexdigest()
        certificate={'accepted_cells':list(previous[:index+1]),'phase_seals':dict(seals),
                     'next_cell':CELL_ORDER[index+1],'affordable':True,
                     'ledger_prefix_sha256':fingerprint(history),'files':files}
        path=ledger.root/'outcomes'/prior/'frontier.json'
        save_new(path,certificate)
        name=predecessor_filename(CELL_ORDER[index+1])
        if path.name!=name:
            path=path.with_name(name);save_new(path,certificate)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_actual_phase(directory, *, root, phase='p0', ledger=None, parent=None,
                     fail_decisions=None, summary_fault=False, on_request=None,
                     approval_updates=None, import_verify=None, cloud_client=None,
                     real_cloud=False, runtime_assets=False, conversation='conv-44',condition='full'):
    root=Path(root).resolve();directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True)
    binding={**SCIENTIFIC_BINDING,'source_sha256':fingerprint(source_fingerprint(root)),
             'condition':condition,'population':'fallback','manifest_sha256':fingerprint(json.loads((root/'manifests/fallback.json').read_text())),
             'repetition':0,'conversation_id':conversation,'provider_contract_policy':'strict-original-v1'}
    fresh=ledger is None
    ledger=ledger or CampaignLedger(directory/'budget.sqlite',campaign_root=directory,binding=binding)
    key=cell_key(conversation,condition)
    approval={'approved':True,'binding':binding,'phase':phase,'kind':'baseline','condition':condition,'conversation':conversation}
    if condition!='full':approval['ablation_policy']=ablation_policy(cell_key(conversation,condition))
    if fresh and key!='conv-44':
        approval['previous_acceptance_sha256']=seed_predecessors(ledger,key)
    elif parent and key!='conv-44':
        approval['previous_acceptance_sha256']=json.loads((cell_store(directory,key)/'runs'/parent['phase']/'approval.json').read_text())['previous_acceptance_sha256']
    if parent:
        approval.update(parent=parent['phase'],parent_seal=fingerprint(parent),
                        parent_path=str(cell_store(directory,key)/'runs'/parent['phase']/'phase.json'))
    approval.update(approval_updates or {})
    module=original_memory_module()
    class Retriever(LocalRetriever):
        def __init__(self,*a,**kw):
            super().__init__();self.embeddings=np.empty((0,384),dtype=np.float32)
        def add_documents(self,documents):
            for document in documents:
                self.document_ids[document]=len(self.corpus);self.corpus.append(document)
                vector=np.zeros((1,384),dtype=np.float32);vector[0,0]=len(document)
                self.embeddings=np.concatenate((self.embeddings,vector))
    module.SimpleEmbeddingRetriever=Retriever
    if runtime_assets:
        from amem_repro.author import _load_memory
        module=_load_memory(root)
    provider=Provider();requests=[];decisions=0
    def handle(request):
        nonlocal decisions
        body=json.loads(request.content);requests.append(body)
        if on_request:on_request(body,len(requests),ledger)
        synthetic=provider.complete(messages=body['messages'],tools=[{'function':{
            'parameters':body['response_format']['json_schema']['schema']}}])
        content=synthetic['choices'][0]['message']['tool_calls'][0]['function']['arguments']
        response={'id':'gen-'+phase+'-'+str(len(requests)),'provider':'OpenAI','model':MODEL,
                  'choices':[{'finish_reason':'stop','message':{'content':content}}],
                  'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':.000021}}
        if 'should_evolve' in body['response_format']['json_schema']['schema']['properties']:
            decisions+=1;kind=(fail_decisions or {}).get(decisions)
            if kind:
                response['choices'][0]['message']['content']='{"should_evolve":true,"actions"["strengthen"]}'
                if kind=='cleanup_parseable':
                    response['choices'][0]['message']['content']='\x1c'+content
                if kind=='length':
                    response['choices'][0]['finish_reason']='length'
                    response['usage'].update(completion_tokens=4096,cost=.0024726)
        return httpx.Response(200,json=response)
    client=httpx.Client(transport=httpx.MockTransport(handle))
    observer=LangfuseObserver(cloud_client or Client(),{**binding,'run_id':phase,
        'execution_mode':'offline-native-fixture','observability_policy':'run2-audit-essential-v1'})
    scorer=AuthorScorer(root,dependencies=None if runtime_assets else dependencies())
    def broken_finish(self):raise OSError('injected critical summary persistence failure')
    try:
        with ExitStack() as stack:
            if not real_cloud:
                stack.enter_context(patch('amem_repro.langfuse_verify.verify_observations',lambda *a,**k:{'verified':True}))
                stack.enter_context(patch('amem_repro.gpt4omini_reporting.import_results',
                    import_verify or (lambda *a,**k:{'verified':True,'offline_external_reporting_mock':True})))
            if summary_fault:stack.enter_context(patch.object(RunLedger,'finish',broken_finish))
            receipt=execute_phase(approval,ledger,observer=observer,client=client,
                token_counter=TokenCounter(str.split,'whitespace fixture only','synthetic-v1'),
                root=root,memory_module=module,scorer=scorer)
    finally:client.close()
    return {'receipt':receipt,'ledger':ledger,'requests':requests,'approval':approval,
            'directory':directory,'observer':observer}
