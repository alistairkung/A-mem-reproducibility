"""Seal independently accepted Full evidence and reforecast the remaining cells."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from amem_repro.config import fingerprint
from amem_repro.openrouter import CampaignLedger,FULL_CELLS,cell_store,save_new

def read(p):return json.loads(p.read_bytes())

def seal(campaign,cell,org_units):
    from amem_repro.gpt4omini_campaign import verify_accepted_cell
    verify_accepted_cell(campaign,cell)
    order=list(FULL_CELLS)
    accepted=order[:order.index(cell)+1]
    out=campaign/'outcomes'/cell
    store=cell_store(campaign,cell)
    reviews=[read(out/f'acceptance-{axis}.json') for axis in ('standards','spec')]
    if any(r['accepted'] is not True or r['verdict']!='pass' for r in reviews) or len({r['phase'] for r in reviews})!=1:
        raise ValueError('Independent scientific and financial acceptance required')
    phase=reviews[0]['phase'];record=read(store/'runs'/phase/'phase.json')
    if record['binding']['conversation_id']!=cell or record['status'] not in ('degraded','complete'):
        raise ValueError('Foreign or incomplete phase')
    finance=read(store/'reconciliation.json')
    if not finance['verified']:raise ValueError('Financial reconciliation incomplete')
    with sqlite3.connect((campaign/'budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        history=CampaignLedger.access_snapshot(db)
        seals={};rates={}
        for c in accepted:
            cell_reviews=read(campaign/'outcomes'/c/'acceptance-spec.json')
            end=cell_reviews['phase']
            seals[c]=db.execute("SELECT seal FROM phases WHERE id=? AND state='complete'",(end,)).fetchone()[0]
            if seals[c]!=fingerprint(read(cell_store(campaign,c)/'runs'/end/'phase.json')):
                raise ValueError('Original phase seal differs')
            rows=db.execute("""SELECT a.stage,COUNT(*),SUM(a.charge) FROM attempts a JOIN phases p ON a.phase=p.id
                WHERE json_extract(p.approval,'$.kind')='baseline' AND
                json_extract(p.approval,'$.conversation')=? AND a.state='settled' GROUP BY a.stage""",(c,)).fetchall()
            if sum(r[1] for r in rows)!=2*sum(FULL_CELLS[c]):raise ValueError('Incomplete settled baseline')
            for stage,n,cost in rows:
                rates[stage]=max(rates.get(stage,Decimal(0)),Decimal(cost)/n/1000000)
    costs={c:sum(rate*(turns if s in ('metadata','shared_decision') else questions)
                 for s,rate in rates.items()) for c,(turns,questions) in FULL_CELLS.items()}
    next_cells=order[len(accepted):];future=sum(costs[c] for c in next_cells)+3*sum(costs.values())
    spent=Decimal(finance['accounting']['conservative_microusd'])/1000000
    # Plan up to 16K units per remaining cell, with marginal Core pricing.
    service_fee=max(Decimal(0),Decimal(org_units+16000*(len(next_cells)+9)-100000)*8/100000)
    affordable=(spent+2*future+service_fee<=42 and all(2*costs[c]<=5 for c in next_cells)
                and (not next_cells or org_units+32500<=100000))
    files={}
    paths=[store/'reconciliation.json',*store.glob('generation-readback-*'),store/'runs',store/'cache',store/'frozen',
           out/'acceptance-spec.json',out/'acceptance-standards.json']
    for path in paths:
        for f in ([path] if path.is_file() else path.rglob('*')):
            if f.is_file():files[str(f.relative_to(campaign))]=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
    result={'accepted_cells':accepted,'phase_seals':seals,'next_cell':next_cells[0] if next_cells else None,
            'ledger_prefix_sha256':fingerprint(history),'files':files,'affordable':affordable,
            'forecast':{'conservative_so_far_usd':str(spent),'stage_unit_costs':{s:str(r) for s,r in rates.items()},
            'cell_model_scenario_usd':{c:str(v) for c,v in costs.items()},'nine_ablation_usd':str(3*sum(costs.values())),
            'model_total_usd':str(spent+future),'model_and_service_double_remaining_sensitivity_usd':str(spent+2*future+service_fee),
            'service_fee_scenario_usd':str(service_fee),'org_units_conservative':org_units,'remaining_contingency_usd':8}}
    save_new(out/'frontier.json',result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cell',required=True,choices=FULL_CELLS)
    parser.add_argument('--org-units',type=int,required=True);args=parser.parse_args()
    result=seal((ROOT/'artifacts/gpt4omini').resolve(),args.cell,args.org_units)
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))
