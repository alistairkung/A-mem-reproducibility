"""Synthetic native responses through the real author runner; no paid transport."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import httpx
import numpy as np

from amem_repro.author import make_agent_factory
from amem_repro.actions import make_action_agent_factory
from amem_repro.config import OPENROUTER_CONFIG,source_fingerprint,fingerprint
from amem_repro.manifests import build_manifest
from amem_repro.measurements import TokenCounter
from amem_repro.openrouter import (
    SCIENTIFIC_BINDING,MODEL,CampaignLedger,OpenRouterController,
)
from amem_repro.gpt4omini_campaign import FallbackGuard,read
from amem_repro.runner import run_manifest
from amem_repro.scoring import AuthorScorer,rescore_records
from test_foundation import Provider,original_memory_module,LocalRetriever
from test_scoring import dependencies

ROOT=Path(__file__).resolve().parents[1]


def run_fixture(directory, *, observer=None, records=None, candidate=False,
                fail_decisions=None, checkpoint=None, ledger=None, parent=None,
                use_runtime_assets=False, token_counter=None, boundary_check=None):
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True)
    binding={**SCIENTIFIC_BINDING,'source_sha256':fingerprint(source_fingerprint(ROOT))}
    ledger=ledger or CampaignLedger(directory/'accounting/budget.sqlite',
                                  campaign_root=directory/'accounting',binding=binding)
    phase=directory.name
    approval={'approved':True,'binding':binding,'phase':phase,'kind':'baseline',
              'condition':'full','conversation':'conv-44'}
    if parent:approval.update(parent=parent['phase'],parent_seal=fingerprint(parent))
    ledger.claim(approval)
    provider=Provider();requests=[];responses=[];decisions=0
    def handle(request):
        nonlocal decisions
        body=json.loads(request.content);index=len(requests);requests.append(body)
        if records is not None:
            assert fingerprint(body)==fingerprint(records[index]['attempts'][0]['request_body'])
            response=copy.deepcopy(records[index]['provider_response'])
        else:
            # Adapt a labelled synthetic TEST provider, never the actual wire request.
            synthetic=provider.complete(messages=body['messages'],tools=[{'function':{
                'parameters':body['response_format']['json_schema']['schema']}}])
            content=synthetic['choices'][0]['message']['tool_calls'][0]['function']['arguments']
            response={'id':f'gen-{phase}-{index}','provider':'OpenAI','model':MODEL,
                      'system_fingerprint':'offline-native-fixture',
                      'choices':[{'finish_reason':'stop','message':{'content':content}}],
                      'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':.000021}}
            if 'should_evolve' in body['response_format']['json_schema']['schema']['properties']:
                decisions+=1
                kind=(fail_decisions or {}).get(decisions)
                if kind:
                    response['choices'][0]['message']['content']='{"should_evolve":true,"actions"["strengthen"]}'
                    if kind=='length':
                        response['choices'][0]['finish_reason']='length'
                        response['usage'].update(completion_tokens=4096,cost=.0024726)
        responses.append(copy.deepcopy(response))
        return httpx.Response(200,json=response)
    client=httpx.Client(transport=httpx.MockTransport(handle))
    controller=OpenRouterController(client,ledger=ledger,phase=phase,journal=directory/'raw')
    def controllers(record):controller.observer=record;return controller
    module=None
    if not use_runtime_assets:
        module=original_memory_module()
        class Retriever(LocalRetriever):
            def __init__(self,*args,**kwargs):
                super().__init__();self.embeddings=np.empty((0,384),dtype=np.float32)
            def add_documents(self,documents):
                for document in documents:
                    self.document_ids[document]=len(self.corpus);self.corpus.append(document)
                    vector=np.zeros((1,384),dtype=np.float32);vector[0,0]=len(document)
                    self.embeddings=np.concatenate((self.embeddings,vector))
        module.SimpleEmbeddingRetriever=Retriever
    else:
        from amem_repro.author import _load_memory
        module=_load_memory(ROOT)
    counter=token_counter or TokenCounter(str.split,'whitespace test only','synthetic-v1')
    factory=make_action_agent_factory if candidate else make_agent_factory
    options={'condition':'full'} if candidate else {}
    build=factory(ROOT,controller_factory=controllers,memory_module=module,token_counter=counter,**options)
    healthy=boundary_check or (observer.assert_healthy if observer else lambda:None)
    guard=FallbackGuard(controller,healthy,lambda note:module.note_document(SimpleNamespace(**note)))
    scorer=AuthorScorer(ROOT,dependencies=None if use_runtime_assets else dependencies())
    error=None
    try:
        summary=run_manifest(ROOT/'data/locomo10.json',build_manifest(ROOT/'data/locomo10.json','smoke'),
            copy.deepcopy(OPENROUTER_CONFIG),output_dir=directory/'run',cache_root=directory/'cache',
            source_hashes=source_fingerprint(ROOT),agent_factory=build,scorer=scorer,observer=observer,
            run_id=phase,checkpoint=checkpoint,
            execution_type='checkpoint_recovery' if checkpoint else 'fresh_build',
            boundary_check=healthy,evolution_guard=guard)
    except BaseException as exc:
        error=type(exc).__name__;summary=read(directory/'run/summary.json')
    finally:client.close()
    events=[json.loads(l) for l in (directory/'run/events.jsonl').read_text().splitlines()]
    generations=[e for e in events if e['type']=='generation']
    results=[e['result'] for e in events if e['type']=='question_result']
    if (directory/'run/partial-memory.json').exists():state=read(directory/'run/partial-memory.json')['state']
    else:state=read(next((directory/'cache').glob('*/state.json')))
    receipt={'phase':phase,'status':summary['status'],'notes':len(state['notes']),
             'recoverable_length_failure':guard.recoverable,'error_type':error}
    ledger.finish(phase,receipt,'recoverable' if guard.recoverable else 'complete' if not error else 'terminal')
    failures=[e for e in events if e['type']=='failure']
    return {'summary':summary,'events':events,'generations':generations,'results':results,
            'state':state,'requests':requests,'responses':responses,'ledger':ledger,'receipt':receipt,
            'views':rescore_records(results,scorer) if results else None,
            'checkpoint':{'state':state,'failures':failures,
                          'lineage':{'policy':'offline-native-fixture','parent_run_id':phase}}}
