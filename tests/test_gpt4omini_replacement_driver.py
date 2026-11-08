"""Admission before local execution and the outer process-per-attempt loop."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone

import pytest

from amem_repro.budget import BudgetStop
from scripts import gpt4omini_replacement as driver


@pytest.fixture
def capacity(tmp_path,monkeypatch):
    c = {'observed_at':datetime.now(timezone.utc).isoformat(), 'verified':True, 'group_affordable':True,
            'snapshot':{'plan':'Core','billing_period':'2026-11-03 to 2026-12-03','rolling_units':146695}, 'project_id':'cmvxd2aby005wad0ei7wt2d5o',
            'project_auth':{'status':'ok','project_match':True}, 'reviewed_commit':'head', 'source_sha256':'source',
            'opening_metered_org_units':146689, 'opening_observed_org_units':146695, 'retained_allowance_units':8,
            'new_unallocated_org_growth_units':0, 'effective_conservative_org_units':146697,
            'group_cap_microusd':10000000,'campaign_planned_microusd':42000000,'protected_contingency_microusd':8000000,
            'service_conservative_microusd':4641840,'opening_conservative_model_microusd':4146358,
            'opening_combined_conservative_microusd':8788198, 'campaign_headroom_after_group_microusd':23211802}


    observed = 'verification/replacement-standards/opening-billing-observation.json'
    path = tmp_path / observed
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({k:c[k] for k in ('observed_at','snapshot')}))
    c['evidence_files'] = {observed:hashlib.sha256(path.read_bytes()).hexdigest()}
    c['opening_capacity_sha256'] = 'd4cfe4960e5a8995a16995dec10e0ba381cf92ef55f1b5b34590335ef12bd085'
    monkeypatch.setattr(driver,'sha',lambda path:c['opening_capacity_sha256'])
    return c


def test_capacity_carries_retained_and_new_org_units(capacity,tmp_path):
    c = capacity
    driver.verify_capacity(c,'source','head',campaign=tmp_path)
    c['snapshot']['rolling_units'] += 400000
    with pytest.raises(BudgetStop):
        driver.verify_capacity(c,'source','head',campaign=tmp_path)


@pytest.mark.parametrize('field,value', [('retained_allowance_units',0),('opening_metered_org_units',1),
    ('group_affordable',False),('reviewed_commit','earlier'),('observed_at','2000-01-01T00:00:00+00:00')])
def test_rejects_stale_or_unbound_capacity(field,value,capacity,tmp_path):
    c = capacity
    c[field] = value
    with pytest.raises(BudgetStop):
        driver.verify_capacity(c,'source','head',campaign=tmp_path)


@pytest.mark.parametrize('statuses,eligible,expected', [
    (['complete'],False,1), (['degraded'],False,1), (['incomplete'],False,1),
    (['incomplete','complete'],True,2), (['incomplete']*3,True,3),
])
def test_dispatches_a_new_local_process_only_for_eligible_attempts(tmp_path,monkeypatch,statuses,eligible,expected):
    seen = []
    monkeypatch.setattr(driver,'CAMPAIGN',tmp_path)
    monkeypatch.setattr(driver,'classify_restart',lambda campaign,phase:eligible)
    def launch(command, *, cwd, check):
        ordinal = int(command[-1])
        assert command[:2] == [driver.sys.executable,'-u']
        assert command[-3:-1] == ['attempt','--ordinal']
        assert check is True and ordinal == len(seen)+1
        phase = driver.phase_id(ordinal)
        folder = driver.attempt_store(tmp_path,ordinal) / 'runs' / phase
        folder.mkdir(parents=True,exist_ok=False)
        (folder/'phase.json').write_text(json.dumps({'status':statuses[ordinal-1]}))
        seen.append(phase)
    monkeypatch.setattr(driver.subprocess,'run',launch)
    if statuses[-1] == 'incomplete':
        with pytest.raises(BudgetStop):
            driver.execute()
    else:
        driver.execute()
    assert len(seen) == expected == len(set(seen))


def test_unclassified_process_failure_stops_immediately(monkeypatch):
    def fail(command, **kw):
        assert command[-1] == '1'
        raise subprocess.CalledProcessError(2, command)
    monkeypatch.setattr(driver.subprocess,'run',fail)
    with pytest.raises(subprocess.CalledProcessError):
        driver.execute()
