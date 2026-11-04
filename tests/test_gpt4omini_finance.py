import httpx
import pytest
from scripts.gpt4omini_finance import compare, verify_generations
from amem_repro.openrouter import MODEL

def account(usage,key,credits='50'):
    return {'credits':{'total_usage':usage,'total_credits':credits},'key':{'usage':key}}

@pytest.mark.parametrize('closing,expected',[
    (account('0.512','0.5'),True),
    (account('0.812','0.5'),False),
    (account('0.512','0.49'),False),
    (account('0.512','0.5','51'),False),
])
def test_preserved_opening_balance_distinguishes_movements(closing,expected):
    result=compare(account('0.412','0.4'),closing,'0.4','0.5')
    assert result['verified']==expected

@pytest.mark.parametrize('fault',['missing','foreign-id','wrong-charge','extra-hop'])
def test_request_specific_proof_required(fault,tmp_path):
    data={'id':'gen-test','provider_name':'OpenAI','model':MODEL,'total_cost':'.1',
          'provider_responses':[{'provider_name':'OpenAI','status':200,'model_permaslug':MODEL}]}
    if fault=='foreign-id':data['id']='gen-other'
    if fault=='wrong-charge':data['total_cost']='.11'
    if fault=='extra-hop':data['provider_responses']*=2
    client=httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'data':data})))
    with pytest.raises(ValueError):
        verify_generations(client,[(None if fault=='missing' else 'gen-test','.1')],tmp_path)
    assert len(list(tmp_path.glob('*.json')))==1

def test_new_unknown_blocks_reconciliation_before_any_remote_lookup(tmp_path):
    from contextlib import contextmanager
    from unittest.mock import Mock
    from scripts.gpt4omini_finance import reconcile
    class Ledger:
        @contextmanager
        def transaction(self):
            yield Mock()
        def unaccepted_unknowns(self,approval):
            return 1
    client=Mock()
    with pytest.raises(ValueError,match='unknown'):
        reconcile(client,Ledger(),tmp_path/'receipt.json',{'approval':{}})
    assert not client.get.called and not (tmp_path/'receipt.json').exists()


@pytest.mark.parametrize('bad',[b'not JSON',b'{"data":{}}'])
def test_snapshot_preserves_unusable_billing_response(tmp_path,bad):
    from base64 import b64decode
    import json
    from scripts.gpt4omini_finance import snapshot
    client=httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,content=bad)))
    with pytest.raises((ValueError,KeyError)):
        snapshot(client,tmp_path)
    record=json.loads((tmp_path/'credits.json').read_bytes())
    assert record['status']==200 and b64decode(record['response_base64'])==bad
