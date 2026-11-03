"""Run from the repository root: one frozen Run2 cell, verified BLK013 continuations only."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys,traceback
from datetime import datetime,timezone
ROOT=Path.cwd().resolve();sys.path.insert(0,str(ROOT))
from amem_repro import run2
from amem_repro.config import fingerprint
from amem_repro.phases import _save
from amem_repro.observability import LangfuseObserver
from amem_repro.langfuse_verify import verify_observations,import_and_verify_results

def read(path):return json.loads(Path(path).read_text())
def preserved():
 inventory=read(ROOT/'artifacts/run2/gate-a/run1-preservation.json')
 for name,digest in inventory['files'].items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Run1 artifact changed: '+name)
 if hashlib.sha256((ROOT/'artifacts/study-budget.sqlite').read_bytes()).hexdigest()!=inventory['ledger_sha256']:raise RuntimeError('Run1 ledger changed')
def main(index):
 from dotenv import dotenv_values
 from langfuse import Langfuse
 frozen=ROOT/'artifacts/run2/frozen'
 campaign=read(frozen/'campaign-approval.json');receipt=read(frozen/'preflight.json')
 if campaign['binding']['execution_script_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():raise RuntimeError('Frozen execution script changed')
 if not 0<=index<len(run2.CELL_ORDER):raise ValueError('Unknown frozen cell index')
 condition,conversation=run2.CELL_ORDER[index]
 preserved()
 # Load only the explicitly required project/provider secrets, never expose them.
 values=dotenv_values(ROOT/'.env')
 for key in ('DEEPSEEK_API_KEY','LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY','LANGFUSE_BASE_URL','LANGFUSE_HOST'):
  if values.get(key):os.environ[key]=values[key]
 host=os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST')
 if not host or not all(os.environ.get(k) for k in ('DEEPSEEK_API_KEY','LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY')):raise RuntimeError('Required private provider/project configuration is missing')
 parent=None
 for _ in range(run2.CONVERSATIONS[conversation][0]+1):
  forecast=run2.forecast_campaign(campaign,root=ROOT)
  if not forecast['fits_execution_allocation']:raise RuntimeError('Cost-only forecast exceedsUSD42; stop')
  approval=run2.plan_phase(campaign,receipt,ROOT/'artifacts/assets',root=ROOT,condition=condition,conversation_id=conversation,parent=parent)
  approval.update(approved=True,approved_by='User Run2 fully observed campaign grant, decisions.md; verified BLK013 continuations within original cell allocation only',approved_at=datetime.now(timezone.utc).isoformat())
  _save(frozen/(approval['run_id']+'-approval.json'),approval)
  binding=approval['binding']
  metadata={k:binding[k] for k in ('campaign_id','condition','population','manifest_sha256','repetition','provider_contract_policy')}
  metadata.update(run_id=approval['run_id'],conversation_id=conversation,config_sha256=binding['config_sha256'],source_sha256=binding['source_sha256'],output_token_policy='run2-shared-decision-8192-v1',max_output_tokens_by_stage=binding['max_output_tokens_by_stage'],execution_mode='paid_primary_run2',parent_run_id=binding.get('checkpoint',{}).get('parent_run_id'),execution_script_sha256=campaign['binding']['execution_script_sha256'])
  client=Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],secret_key=os.environ['LANGFUSE_SECRET_KEY'],base_url=host,environment='amem-run2',release=campaign['binding']['source_sha256'])
  observer=LangfuseObserver(client,metadata)
  def observations(capture,context):
   _save(Path(context['output_dir'])/'trace-capture.json',capture)
   return verify_observations(capture,context)
  try:
   phase=run2.execute_phase(approval,campaign,receipt,ROOT/'artifacts/assets',root=ROOT,observer=observer,verify_observations=observations,verify_results=lambda views,context:import_and_verify_results(views,context,client=client))
  finally:client.shutdown()
  preserved()
  print(json.dumps({k:phase[k] for k in ('run_id','status','total_memory_notes','completed_questions','recoverable_length_failure','cell_budget','campaign_budget','error_type')}),flush=True)
  if phase['usable_for_next_phase']:
   forecast=run2.forecast_campaign(campaign,root=ROOT)
   _save(ROOT/'artifacts/run2/forecasts'/(phase['run_id']+'-after.json'),forecast)
   print(json.dumps({'cell_complete':index,'forecast':forecast}),flush=True)
   return
  if not phase['recoverable_length_failure']:
   raise RuntimeError('Material failure; no further paid phase may start')
  parent=ROOT/'artifacts/run2/runs'/phase['run_id']/'phase.json'
 raise RuntimeError('Finite original-turn recovery bound reached')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cell-index',type=int,required=True)
 args=parser.parse_args()
 try:main(args.cell_index)
 except BaseException:
  text=traceback.format_exc()
  values=[os.environ.get('DEEPSEEK_API_KEY',''),os.environ.get('LANGFUSE_PUBLIC_KEY',''),os.environ.get('LANGFUSE_SECRET_KEY','')]
  values.append(base64.b64encode((values[1]+':'+values[2]).encode()).decode())
  for value in values:
   if value:text=text.replace(value,'[redacted]')
  path=ROOT/'artifacts/run2/driver-failures';path.mkdir(exist_ok=True)
  with (path/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.txt')).open('x') as f:f.write(text)
  raise SystemExit('Run2 stopped; preserved redacted evidence. No automatic restart or unapproved continuation.')
