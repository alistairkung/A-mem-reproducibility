import subprocess
from datetime import datetime, timedelta

import pytest

from amem_repro.budget import BudgetStop
from amem_repro.config import fingerprint
from amem_repro.openrouter import save_new
from scripts import gpt4omini_final_fresh as final


@pytest.mark.parametrize('sequence', [
    [('complete', False)], [('degraded', False)],
    [('incomplete', True), ('complete', False)], [('incomplete', False)],
    [('incomplete', True)] * 3,
])
def test_only_an_accounted_eligible_failure_starts_another_fresh_process(tmp_path, monkeypatch, sequence):
    launched = []
    monkeypatch.setattr(final, 'DIRECTORY', tmp_path)
    monkeypatch.setattr(final, 'start_allowed', lambda: None)

    def launch(command, *, cwd, check):
        ordinal = int(command[-1])
        assert check and command[-3:-1] == ['attempt', '--ordinal']
        assert ordinal == len(launched) + 1
        run_id = final.phase_id(ordinal)
        status, eligible = sequence[ordinal - 1]
        record = {'status': status, 'phase':run_id}
        store = tmp_path/f'attempt-{ordinal}'
        save_new(store/'runs'/run_id/'phase.json', record)
        save_new(store/'reconciliation.json', {'phase_seal':fingerprint(record), 'verified':True,
                                                'restart_eligible':eligible})
        launched.append(run_id)

    monkeypatch.setattr(subprocess, 'run', launch)
    if sequence[-1][0] == 'incomplete':
        with pytest.raises(BudgetStop):
            final.execute()
    else:
        final.execute()
    assert len(set(launched)) == len(sequence)


def test_no_new_attempt_when_build_would_overrun_collection_cutoff(monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz):
            return final.PAID_END - final.FRESH_DURATION + timedelta(seconds=1)
    monkeypatch.setattr(final, 'datetime', Clock)
    with pytest.raises(BudgetStop):
        final.start_allowed()


def test_deadline_rechecked_on_physical_post_after_durable_reservation(monkeypatch):
    import httpx
    class Clock(datetime):
        @classmethod
        def now(cls, tz):
            return final.PAID_END
    monkeypatch.setattr(final, 'datetime', Clock)
    final.before_request(httpx.Request('GET', final.previous.BASE_URL + '/credits'))
    with pytest.raises(BudgetStop):
        final.before_request(httpx.Request('POST', final.previous.BASE_URL + '/chat/completions'))
