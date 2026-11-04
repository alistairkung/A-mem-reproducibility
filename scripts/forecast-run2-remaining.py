"""Read-only measured Run2 cost forecast; does not plan or approve paid phases."""
from fractions import Fraction
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/run2/reporting-recovery/forecast.json'
CONVERSATIONS = {'conv-44': (675,158,35), 'conv-49': (509,196,40), 'conv-50': (568,204,46)}
CONDITIONS = ('full','neither','linking_only','evolution_only')
CELL_ORDER = [('full','conv-44'),('full','conv-49'),('full','conv-50')] + [
    (c,v) for c in CONDITIONS[1:] for v in ('conv-49','conv-50','conv-44')]


def ceil(x):
    if isinstance(x,Fraction):return (x.numerator+x.denominator-1)//x.denominator
    return int(x.to_integral_value(rounding=ROUND_CEILING))
def usd(n): return format(Decimal(n)/1000000,'.6f')


def main():
    ledger = ROOT / 'artifacts/run2/budget.sqlite'
    before = hashlib.sha256(ledger.read_bytes()).hexdigest()
    db = sqlite3.connect(f'file:{ledger}?mode=ro',uri=True)
    stages = {}
    for stage,logical,physical,settled,reserved in db.execute('''
        SELECT l.stage,COUNT(DISTINCT l.id),COUNT(a.id),
        SUM(CASE WHEN a.status='settled' THEN a.charge ELSE 0 END),
        SUM(CASE WHEN a.status!='settled' THEN a.reservation ELSE 0 END)
        FROM logical_calls l JOIN attempts a ON a.logical_id=l.id GROUP BY l.stage'''):
        stages[stage] = {'logical_calls':logical,'physical_attempts':physical,
            'settled_microusd':settled,'reserved_microusd':reserved,
            'conservative_mean_microusd':str(Decimal(settled+reserved)/logical)}
    db.close()
    settled=sum(s['settled_microusd'] for s in stages.values())
    reserved=sum(s['reserved_microusd'] for s in stages.values())
    exposure=settled+reserved
    assert (settled,reserved,exposure)==(3842085,324404,4166489)
    means={k:Fraction(s['settled_microusd']+s['reserved_microusd'],s['logical_calls']) for k,s in stages.items()}
    costs={}
    for name,(t,q,c5) in CONVERSATIONS.items():
        costs[name]={'construction_microusd':ceil(t*(means['metadata']+means['shared_decision'])),
                     'qa_microusd':ceil(q*(means['query_keywords']+means['answer'])),
                     'total_microusd':ceil(t*(means['metadata']+means['shared_decision'])+q*(means['query_keywords']+means['answer']))}
    future=[{'cell_index':i,'condition':c,'conversation_id':v,**costs[v]} for i,(c,v) in enumerate(CELL_ORDER) if i]
    scenarios=[]
    definitions=[('original_scope',tuple(CONVERSATIONS),CONDITIONS),
                 ('balanced_two',('conv-44','conv-49'),CONDITIONS),
                 ('balanced_one',('conv-44',),CONDITIONS),
                 ('minimum_published_comparison',('conv-44',),('full','neither','linking_only'))]
    # Conservative starting capacity uses the larger of two differently scoped displays,
    # plus the new recovery import not yet present in the lagged billing counters.
    starting_units=max(13174,16878)+5442
    for name,convs,conds in definitions:
        jobs=[j for j in future if j['conversation_id'] in convs and j['condition'] in conds]
        remaining=sum(j['total_microusd'] for j in jobs)
        low=high=0
        for j in jobs:
            t,q,c5=CONVERSATIONS[j['conversation_id']]
            low+=4*t+40*q+6+2*c5
            high+=(5+{'full':2,'neither':0,'linking_only':1,'evolution_only':1}[j['condition']])*t+40*q+6+2*c5
        units=(starting_units+low,starting_units+high)
        fees=tuple(ceil(Decimal(max(0,u-100000))*80) for u in units) #80microUSD/unit
        sensitivity=[]
        for factor in ('0.8','1.0','1.1','1.2','1.5'):
            total=exposure+ceil(Decimal(remaining)*Decimal(factor))
            sensitivity.append({'future_cost_factor':factor,'provider_total_usd':usd(total),
                'service_upper_usd':usd(fees[1]),'total_with_protected8_usd':usd(total+fees[1]+8000000),
                'fits42_including_service':total+fees[1]<=42000000})
        # Stressed exposure is incremental beyond the allowance already in stage means.
        retry=ceil(Decimal(remaining)*Decimal('0.01'))
        unknown=len(jobs)*324404
        checkpoint_extra_units=len(jobs)*2*1500
        stress_service=ceil(Decimal(max(0,units[1]+checkpoint_extra_units-100000))*80)
        stress=exposure+ceil(Decimal(remaining)*Decimal('1.2'))+retry+unknown
        scenarios.append({'name':name,'conversations':convs,'conditions':conds,'new_cells':len(jobs),
            'additional_provider_usd':usd(remaining),'provider_total_usd':usd(exposure+remaining),
            'remaining_planned42_after_provider_usd':usd(42000000-exposure-remaining),
            'normal_units_range':units,'normal_service_fee_usd':[usd(x) for x in fees],
            'sensitivity':sensitivity,
            'combined_stress':{'future_growth':'20%','additional_settled_retry_allowance':'1%',
                'extra_unknown_reservations':len(jobs),'extra_unknown_usd':usd(unknown),
                'checkpoint_units':checkpoint_extra_units,'checkpoint_basis':'two extra continuations/cell,1500units each, rounded planning proxy',
                'provider_total_usd':usd(stress),'service_fee_usd':usd(stress_service),
                'total_with_protected8_usd':usd(stress+stress_service+8000000),
                'fits42_including_service':stress+stress_service<=42000000},
            'max_nominal_cell_usd':usd(max((j['total_microusd'] for j in jobs),default=0))})
    assert sum(j['total_microusd'] for j in future)+exposure==48235144
    result={'basis':'Actual first Full conv44 Run2 stages. Cost-only scenarios; no execution authority.',
        'ledger_sha256':before,'settled_usd':usd(settled),'reserved_unknown454_usd':usd(reserved),
        'conservative_exposure_usd':usd(exposure),'original_cell_remainder_usd':usd(5000000-exposure),
        'remaining_planned42_usd':usd(42000000-exposure),'protected_contingency_usd':'8.000000',
        'stages':stages,'conversation_costs':costs,'remaining_eleven_cells':future,
        'remaining_nine_ablation_provider_usd':usd(sum(j['total_microusd'] for j in future if j['condition']!='full')),
        'missing_two_full_provider_usd':usd(sum(j['total_microusd'] for j in future if j['condition']=='full')),
        'starting_units_conservative':starting_units,'alternatives':scenarios,
        'limitations':['Only one Full cell measured; no ablation/shorter-conversation stage costs measured.',
            'Conservative means embed a proportional full unknown-charge reservation. It is not settled usage.',
            'Temperature0.7/0.5, context/action changes, retry/fallback frequency and hosted pricing/caching may shift future costs.',
            'Sensitivity factors are scenarios, not confidence intervals or guaranteed upper bounds.',
            'Continuation restores state with no repeated scientific work; additional failures still cost and may stop.',
            'Normal service range uses frozen essential policy structural action/D3 bounds; lag,other traffic,tax and new failures may add units.',
            'USD29 existing Core subscription is separate; projected overage needs explicit allocation.',
            'Every cell retains USD5 cap, USD42 planned pool and protectedUSD8. Scenarios cannot grant cap increases or recovery.',
            'Reduced subsets require explicit cost-only population/order authorization; no selection by observed quality.']}
    assert hashlib.sha256(ledger.read_bytes()).hexdigest()==before
    with OUT.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ('conservative_exposure_usd','remaining_nine_ablation_provider_usd','missing_two_full_provider_usd')}))
    for s in scenarios:print(s['name'],s['provider_total_usd'],s['normal_service_fee_usd'],s['sensitivity'][3],s['combined_stress'])


if __name__=='__main__': main()
