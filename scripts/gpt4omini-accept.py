"""Seal independently accepted Full evidence and reforecast the remaining cells."""
import argparse
from decimal import Decimal
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from amem_repro.config import fingerprint
from amem_repro.openrouter import CampaignLedger,FULL_CELLS,CELL_ORDER,ACCEPTED_ORDER,EXPANSION_CELLS,PROGRAM_SERVICE_RESERVE,cell_parts,approval_cell,cell_store,save_new

def read(p):return json.loads(p.read_bytes())

def seal(campaign,cell,org_units,*,ablation=False,expansion=False):
    from amem_repro.gpt4omini_campaign import verify_accepted_cell
    from scripts.gpt4omini_finance import verify_accepted_finances
    verify_accepted_cell(campaign,cell)
    verify_accepted_finances(campaign,cell)
    order=list(CELL_ORDER if expansion else ACCEPTED_ORDER if ablation else FULL_CELLS)
    accepted=order[:order.index(cell)+1]
    out=campaign/'outcomes'/cell
    store=cell_store(campaign,cell)
    reviews=[read(out/f'acceptance-{axis}.json') for axis in ('standards','spec')]
    if any(r['accepted'] is not True or r['verdict']!='pass' for r in reviews) or len({r['phase'] for r in reviews})!=1:
        raise ValueError('Independent scientific and financial acceptance required')
    phase=reviews[0]['phase'];record=read(store/'runs'/phase/'phase.json')
    conversation,condition=cell_parts(cell)
    if (record['binding']['conversation_id']!=conversation or record['binding']['condition']!=condition
            or record['status'] not in ('degraded','complete')):
        raise ValueError('Foreign or incomplete phase')
    finance=read(store/'reconciliation.json')
    if not finance['verified']:raise ValueError('Financial reconciliation incomplete')
    with sqlite3.connect((campaign/'budget.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        history=CampaignLedger.access_snapshot(db)
        seals={};rates={}
        for c in accepted:
            verify_accepted_cell(campaign,c)
            verify_accepted_finances(campaign,c)
            cell_reviews=read(campaign/'outcomes'/c/'acceptance-spec.json')
            end=cell_reviews['phase']
            seals[c]=db.execute("SELECT seal FROM phases WHERE id=? AND state='complete'",(end,)).fetchone()[0]
            if seals[c]!=fingerprint(read(cell_store(campaign,c)/'runs'/end/'phase.json')):
                raise ValueError('Original phase seal differs')
            rows=db.execute("""SELECT a.stage,COUNT(*),SUM(a.charge) FROM attempts a JOIN phases p ON a.phase=p.id
                WHERE json_extract(p.approval,'$.kind')='baseline' AND
                json_extract(p.approval,'$.conversation')=? AND json_extract(p.approval,'$.condition')=?
                AND a.state='settled' GROUP BY a.stage""",cell_parts(c)).fetchall()
            if sum(r[1] for r in rows)!=2*sum(FULL_CELLS[cell_parts(c)[0]]):raise ValueError('Incomplete settled baseline')
            for stage,n,cost in rows:
                rates[stage]=max(rates.get(stage,Decimal(0)),Decimal(cost)/n/1000000)
    costs={c:sum(rate*(turns if s in ('metadata','shared_decision') else questions)
                 for s,rate in rates.items()) for c,(turns,questions) in FULL_CELLS.items()}
    next_cells=order[len(accepted):]
    future=sum(costs[cell_parts(c)[0]] for c in next_cells)+(0 if ablation else 3*sum(costs.values()))
    spent=Decimal(finance['accounting']['conservative_microusd'])/1000000
    # Plan up to 16K units per remaining cell, with marginal Core pricing.
    service_units=org_units+(13500*len(next_cells)+2500 if ablation else 16000*(len(next_cells)+9))
    service_fee=max(Decimal(0),Decimal(service_units-100000)*8/100000)
    affordable=(spent+2*future+service_fee<=42 and all(2*costs[cell_parts(c)[0]]<=5 for c in next_cells)
                and (service_units<=100000 if ablation else (not next_cells or org_units+32500<=100000)))
    if expansion:
        if not ablation or cell not in (ACCEPTED_ORDER[-1], *EXPANSION_CELLS) or org_units < 88674:
            raise ValueError('Expansion requires verified service usage and the accepted six-cell prefix')
        affordable = (spent + 2*future + PROGRAM_SERVICE_RESERVE/Decimal(1000000) <= 42
                      and all(2*costs[cell_parts(c)[0]] + Decimal('1.08') <= 5 for c in next_cells))
    capacity_path = None
    if expansion:
        capacity_path = out/'expansion-capacity.json'
        capacity = read(capacity_path)
        observed = datetime.fromisoformat(capacity['observed_at'])
        age = (datetime.now(timezone.utc)-observed).total_seconds()
        if (capacity.get('verified') is not True or capacity.get('accepted_cell') != cell
                or capacity.get('plan') != 'Core' or capacity.get('included_units') != 100000
                or Decimal(capacity['marginal_usd_per_100k']) != 8
                or capacity['org_units_conservative'] != org_units or not 0 <= age <= 3600
                or org_units < max(capacity['observed_units'],capacity['metered_units_lower_bound'])
                or capacity.get('phase_sha256') != hashlib.sha256((store/'runs'/phase/'phase.json').read_bytes()).hexdigest()):
            raise ValueError('Fresh phase-bound organization capacity proof required')
    files={}
    paths=[store/'reconciliation.json',*store.glob('generation-readback-*'),store/'runs',store/'cache',store/'frozen',
           out/'acceptance-spec.json',out/'acceptance-standards.json']
    if capacity_path: paths.append(capacity_path)
    for path in paths:
        for f in ([path] if path.is_file() else path.rglob('*')):
            if f.is_file():files[str(f.relative_to(campaign))]=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
    result={'accepted_cells':accepted,'phase_seals':seals,'next_cell':next_cells[0] if next_cells else None,
            'ledger_prefix_sha256':fingerprint(history),'files':files,'affordable':affordable,
            'forecast':{'conservative_so_far_usd':str(spent),'stage_unit_costs':{s:str(r) for s,r in rates.items()},
            'cell_model_scenario_usd':{c:str(v) for c,v in costs.items()},'nine_ablation_usd':str(3*sum(costs.values())),
            'model_total_usd':str(spent+future),'model_and_service_double_remaining_sensitivity_usd':str(spent+2*future+service_fee),
            'service_fee_scenario_usd':str(service_fee),'org_units_conservative':org_units,'remaining_contingency_usd':8}}
    result['forecast']['remaining_authorised_model_usd']=str(future)
    result['forecast']['service_capacity_scenario_units']=service_units
    if expansion:
        result['forecast']['program_service_reserve_microusd']=PROGRAM_SERVICE_RESERVE
        result['forecast']['capacity_path']=str(capacity_path.relative_to(campaign))
        result['forecast']['capacity_sha256']=files[result['forecast']['capacity_path']]
    save_new(out/('expansion-frontier.json' if expansion and cell==ACCEPTED_ORDER[-1] else 'ablation-frontier.json' if ablation and cell=='conv-50' else 'frontier.json'),result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cell',required=True,choices=CELL_ORDER)
    parser.add_argument('--expansion',action='store_true');parser.add_argument('--ablation',action='store_true')
    parser.add_argument('--org-units',type=int,required=True);args=parser.parse_args()
    result=seal((ROOT/'artifacts/gpt4omini').resolve(),args.cell,args.org_units,ablation=args.ablation,expansion=args.expansion)
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))
