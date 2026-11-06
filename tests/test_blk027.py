"""Fail-closed, identity-specific numerical adjudication; no model or cloud calls."""
import copy
import json
import math
from pathlib import Path

import pytest

from amem_repro import blk027
from amem_repro.config import fingerprint
from amem_repro.langfuse_verify import VerificationError, _check_experiments


@pytest.fixture
def population(monkeypatch):
    """Full-sized synthetic payload, with the real two exception identities."""
    pins = copy.deepcopy(blk027.rules())
    identity = {'campaign_id': pins['campaign_id'], 'run_id': blk027.PHASE,
                'condition': 'neither', 'conversation_id': 'conv-50'}
    imported = {'identity': identity, 'experiments': {}}
    views, experiments, items, scores = {}, [], [], []
    traces = {f'conv-50:qa:{n}': f'qa-trace-{n}' for n in range(204)}
    traces['conv-50:qa:76'] = pins['tuples'][0]['original_qa_trace_id']
    for pin in pins['tuples']:
        policy = pin['scoring_policy']
        imported['experiments'][policy] = {'id': pin['experiment_id'], 'run_name': policy}
        meta = {**identity, 'scoring_policy': policy, 'scorer_sha256': 'a'*64,
                'execution_mode': 'imported_results'}
        experiments.append({'id': pin['experiment_id'], 'name': policy, 'itemCount': 204, 'metadata': meta})
        view = {'scorer_sha256': 'a'*64, 'individual_results': []}
        views[policy] = view
        for n in range(204):
            q = f'conv-50:qa:{n}'
            metrics = dict.fromkeys(['f1', 'bleu1', 'bleu4', *[f'metric{k}' for k in range(11)]], 0.25)
            if n >= 158: metrics['adversarial_correct'] = 1
            if n == 76: metrics['bleu4'] = float.fromhex(pin['expected_binary64_hex'])
            row = {'question_id': q, 'qa': {'question': f'synthetic {n}', 'category': 5 if n >=158 else 4},
                   'prediction': 'synthetic answer', 'reference': 'synthetic reference', 'metrics': metrics}
            view['individual_results'].append(row)
            item_id = pin['item_observation_id'] if n==76 else f'item-{policy}-{n}'
            trace = pin['experiment_trace_id'] if n==76 else f'trace-{policy}-{n}'
            item = {'id': item_id, 'traceId': trace, 'experimentId': pin['experiment_id'],
                    'experimentItemId': pin['experiment_item_id'] if n==76 else f'example-{n}',
                    'input': {'question_id': q, 'question': row['qa']['question']},
                    'output': row['prediction'], 'expectedOutput': row['reference'],
                    'experimentMetadata': meta,
                    'experimentItemMetadata': {**meta, 'question_id': q, 'category': row['qa']['category'],
                                               'original_record': row, 'original_trace_id': traces[q]}, 'scores': []}
            for name,value in metrics.items():
                selected = n==76 and name=='bleu4'
                score = {'id': pin['score_id'] if selected else f'score-{policy}-{n}-{name}',
                         'name': name, 'value': float.fromhex(pin['allowed_remote_binary64_hex']) if selected else value,
                         'dataType': 'NUMERIC', 'subject': {'kind':'observation','id':item_id,'traceId':trace},
                         'projectId': pin['project_id'], 'environment': pin['score_environment'],
                         'source': pin['score_source'], 'timestamp': pin['native_timestamp']}
                item['scores'].append(score)
                scores.append(copy.deepcopy(score))
            items.append(item)
            if n==76: pin['original_record_sha256'] = fingerprint(row)
    pins['original_scoring_views_canonical_sha256'] = fingerprint(views)
    monkeypatch.setattr(blk027, 'rules', lambda: pins)
    return views, imported, experiments, items, scores, traces


def test_only_two_original_identities_are_authorised():
    policy = blk027.rules()
    assert policy['cell']=='neither-conv-50' and policy['phase_id']==blk027.PHASE
    assert {p['score_id'] for p in policy['tuples']} == {'11db9dd69284d175','03f14c429aa18b91'}
    assert len(policy['tuples']) == 2
    for pin in policy['tuples']:
        assert pin['question_id']=='conv-50:qa:76' and pin['score_name']=='bleu4'
        assert math.nextafter(float.fromhex(pin['expected_binary64_hex']), 0).hex()==pin['allowed_remote_binary64_hex']


def test_full_population_exception_does_not_change_inputs_or_strict_verifier(population):
    before = fingerprint(population)
    views, imported, experiments, items, _, _ = population
    with pytest.raises(VerificationError):
        _check_experiments(views, imported, imported['identity'], experiments, items)
    result = blk027.check_readback(*population)
    assert (result['items'],result['scores'],result['exact_scores'],result['original_qa_traces'])==(408,5804,5802,204)
    assert fingerprint(population)==before
    with pytest.raises(VerificationError):
        _check_experiments(views, imported, imported['identity'], experiments, items)


@pytest.mark.parametrize('field', ['id','name','dataType','projectId','timestamp','environment','source','subject'])
@pytest.mark.parametrize('projection', ['item','native'])
def test_each_pinned_score_identity_is_required(population, field, projection):
    items, scores = population[3:5]
    rows = scores if projection=='native' else [s for i in items for s in i['scores']]
    target = next(s for s in rows if s['id']=='11db9dd69284d175')
    target[field] = 'foreign'
    with pytest.raises((VerificationError,KeyError,TypeError)):
        blk027.check_readback(*population)


@pytest.mark.parametrize('value', [False, '4.019497244339897e-7', float('nan'), float('inf'),
                                  float.fromhex('0x1.af971954baf8bp-22'),
                                  float.fromhex('0x1.af971954baf8ep-22'),
                                  float.fromhex('0x1.af971954baf8dp-22')])
def test_only_the_documented_remote_bit_pattern_is_accepted(population, value):
    for rows in (population[4], [s for i in population[3] for s in i['scores']]):
        next(s for s in rows if s['id']=='11db9dd69284d175')['value']=value
    with pytest.raises((VerificationError,ValueError)):
        blk027.check_readback(*population)


@pytest.mark.parametrize('metric', ['f1','bleu1','bleu4'])
def test_any_third_one_ulp_difference_is_rejected(population, metric):
    item = population[3][0]
    score = next(s for s in item['scores'] if s['name']==metric)
    score['value']=math.nextafter(score['value'],0)
    next(s for s in population[4] if s['id']==score['id'])['value']=score['value']
    with pytest.raises(VerificationError): blk027.check_readback(*population)


@pytest.mark.parametrize('field', ['id','traceId','experimentId','experimentItemId','input','output','expectedOutput',
                                  'experimentItemMetadata','experimentMetadata'])
def test_exception_cannot_excuse_changed_subject_reference_or_metadata(population, field):
    next(i for i in population[3] if i['id']=='23208ab4fba94152')[field]='foreign'
    with pytest.raises((VerificationError,KeyError,TypeError,ValueError)):
        blk027.check_readback(*population)


@pytest.mark.parametrize('part', [2,3,4])
@pytest.mark.parametrize('fault', ['missing','duplicate'])
def test_complete_unique_cloud_population_required(population, part, fault):
    if fault=='missing': population[part].pop()
    else: population[part][-1]=copy.deepcopy(population[part][0])
    with pytest.raises((VerificationError,KeyError)): blk027.check_readback(*population)


def terminal_ledger(tmp_path, key):
    from amem_repro.openrouter import CampaignLedger, SCIENTIFIC_BINDING, cell_parts, ablation_policy, save_new
    from gpt4omini_executor_fixture import seed_predecessors
    conversation, condition=cell_parts(key)
    binding={**SCIENTIFIC_BINDING,'conversation_id':conversation,'condition':condition}
    ledger=CampaignLedger(tmp_path/'budget.sqlite',campaign_root=tmp_path,binding=binding)
    seed_predecessors(ledger,key)
    policy=blk027.rules()
    supplement={'policy':blk027.POLICY,'cell':blk027.CELL,'phase':blk027.PHASE,'accepted':True,
                'classification':'Degraded','original_phase_sha256':policy['original_phase_file_sha256'],
                'original_phase_seal':policy['original_phase_canonical_sha256'], 'exceptions':policy['tuples'],
                'cache_proof':f'outcomes/{blk027.CELL}/blk027-acceptance/cache-proof.json'}
    save_new(tmp_path/blk027.SUPPLEMENT,supplement)
    with ledger.transaction() as db:
        db.execute("UPDATE phases SET id=?,state='terminal',seal=? WHERE id='synthetic-neither-conv-50'",
                   (blk027.PHASE,policy['original_phase_canonical_sha256']))
        db.executemany("INSERT INTO attempts(phase,stage,request_hash,reservation,charge,state) VALUES (?,'metadata','fixture',1,1,'settled')",
                       [(blk027.PHASE,)]*1544)
        snapshot=ledger.access_snapshot(db)
    from amem_repro.openrouter import CELL_ORDER
    previous=CELL_ORDER[CELL_ORDER.index(key)-1]
    certificate=tmp_path/'outcomes'/previous/'frontier.json'
    cert=json.loads(certificate.read_bytes())
    cert['phase_seals'][blk027.CELL]=policy['original_phase_canonical_sha256']
    cert['ledger_prefix_sha256']=fingerprint(snapshot)
    certificate.write_text(json.dumps(cert))
    approval={'approved':True,'binding':binding,'kind':'baseline','phase':'new','conversation':conversation,
              'condition':condition,'ablation_policy':ablation_policy(key),
              'previous_acceptance_sha256':blk027.sha(certificate),
              'reporting_acceptance_sha256':blk027.sha(tmp_path/blk027.SUPPLEMENT)}
    return ledger,approval


@pytest.mark.parametrize('key', blk027.SUCCESSORS)
def test_remaining_cells_accept_only_reviewed_terminal_predecessor(tmp_path, key):
    ledger,approval=terminal_ledger(tmp_path,key)
    ledger.claim(approval)
    assert ledger.reserve('new','metadata',{'max_tokens':1000})[0]==1545
    with ledger.transaction() as db:
        assert db.execute('SELECT state FROM phases WHERE id=?',(blk027.PHASE,)).fetchone()==('terminal',)


@pytest.mark.parametrize('fault', ['missing-approval','changed-supplement','changed-seal','halt','unknown'])
def test_reporting_exception_cannot_excuse_other_failures(tmp_path, fault):
    from amem_repro.budget import BudgetStop
    ledger,approval=terminal_ledger(tmp_path,'neither-conv-44')
    if fault=='missing-approval':approval.pop('reporting_acceptance_sha256')
    elif fault=='changed-supplement': (tmp_path/blk027.SUPPLEMENT).write_text('{}')
    else:
        with ledger.transaction() as db:
            if fault=='changed-seal':db.execute("UPDATE phases SET seal='foreign' WHERE id=?",(blk027.PHASE,))
            elif fault=='halt':db.execute('INSERT INTO halts VALUES (?,?)',(blk027.PHASE,'foreign-failure'))
            else:db.execute("UPDATE attempts SET state='reserved' WHERE id=1")
    with pytest.raises((BudgetStop,VerificationError,KeyError)):ledger.claim(approval)
    assert ledger.totals()['attempts']==1544


def test_changed_supplement_after_claim_stops_before_admission(tmp_path):
    from amem_repro.budget import BudgetStop
    ledger,approval=terminal_ledger(tmp_path,'neither-conv-44')
    ledger.claim(approval)
    (tmp_path/blk027.SUPPLEMENT).write_text('{}')
    with pytest.raises(BudgetStop):ledger.reserve('new','metadata',{'max_tokens':1000})
    assert ledger.totals()['attempts']==1544
