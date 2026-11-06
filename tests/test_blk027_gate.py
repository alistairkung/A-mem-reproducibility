"""The additional cloud check is a single bounded, reviewed service allocation."""
import json
from pathlib import Path
import subprocess

import pytest

from amem_repro.blk027 import sha
from amem_repro.config import fingerprint
from amem_repro.openrouter import PROGRAM_SERVICE_RESERVE
from scripts import gpt4omini_gate_supplement as gate


@pytest.fixture
def approval(tmp_path, monkeypatch):
    names = ('scripts/gpt4omini-gate.py','scripts/gpt4omini_gate_supplement.py',
             'artifacts/gpt4omini/budget.sqlite',
             'artifacts/gpt4omini/verification/six-cell-expansion/final-cloud-verification-claim.json',
             'artifacts/gpt4omini/verification/six-cell-expansion/six-cell-final-2b65f2e/receipt.json')
    for name in names:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('synthetic offline fixture')
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    subprocess.run(['git','add','scripts'],cwd=tmp_path,check=True)
    subprocess.run(['git','-c','user.name=Offline Test','-c','user.email=test@example.invalid',
                    'commit','-qm','fixture'],cwd=tmp_path,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=tmp_path,text=True).strip()
    source={'files':{n:sha(tmp_path/n) for n in names[:2]}}
    monkeypatch.setattr(gate,'source_fingerprint',lambda root:source)
    directory=tmp_path/'artifacts/gpt4omini/verification/blk027-release';directory.mkdir(parents=True)
    plan={'approved':True,'policy':'blk027-single-release-gate-v1','units':1118,
          'marginal_microusd':89440,'program_service_reserve_microusd':PROGRAM_SERVICE_RESERVE,
          'source_sha256':fingerprint(source),'output':'exact-gate','reviewed_commit':commit,
          'merge_commit':commit,'files':{n:sha(tmp_path/n) for n in names}}
    (directory/'gate-approval.json').write_text(json.dumps(plan))
    for axis in ('standards','spec'):
        (directory/f'baseline-{axis}-review.json').write_text(json.dumps({
            'verdict':'pass','reviewed_commit':commit,'source_sha256':fingerprint(source)}))
    return tmp_path,directory,plan


def test_claim_is_consumed_and_the_1119th_unit_is_denied(approval):
    root,directory,plan=approval
    meter=gate.reserve(root,directory/plan['output'])
    for _ in range(1118):meter.admit()
    with pytest.raises(RuntimeError):meter.admit()
    assert meter.spent==1118 and meter.exhausted
    with pytest.raises(FileExistsError):gate.reserve(root,directory/plan['output'])
    plan['output']='another-name';(directory/'gate-approval.json').write_text(json.dumps(plan))
    with pytest.raises(FileExistsError):gate.reserve(root,directory/plan['output'])


@pytest.mark.parametrize('field,value',[('source_sha256','foreign'),('units',1119),
                                       ('marginal_microusd',0),('program_service_reserve_microusd',6680000),
                                       ('reviewed_commit','missing'),('merge_commit','missing')])
def test_changed_source_or_funding_is_rejected_before_claim(approval,field,value):
    root,directory,plan=approval;plan[field]=value
    (directory/'gate-approval.json').write_text(json.dumps(plan))
    with pytest.raises((RuntimeError,subprocess.CalledProcessError)):
        gate.reserve(root,directory/plan['output'])
    assert not (directory/'cloud-verification-claim.json').exists()


@pytest.mark.parametrize('axis', ['standards','spec'])
def test_stale_review_cannot_admit_cloud_units(approval,axis):
    root,directory,plan=approval
    path=directory/f'baseline-{axis}-review.json';review=json.loads(path.read_bytes())
    review['source_sha256']='foreign';path.write_text(json.dumps(review))
    with pytest.raises(RuntimeError):gate.reserve(root,directory/plan['output'])
    assert not (directory/'cloud-verification-claim.json').exists()


def test_updated_plan_cannot_approve_unreviewed_script_bytes(approval):
    root,directory,plan=approval
    path=root/'scripts/gpt4omini-gate.py';path.write_text('changed after review')
    plan['files']['scripts/gpt4omini-gate.py']=sha(path)
    (directory/'gate-approval.json').write_text(json.dumps(plan))
    with pytest.raises(RuntimeError,match='reviewed Git bytes'):
        gate.reserve(root,directory/plan['output'])
    assert not (directory/'cloud-verification-claim.json').exists()
