"""Read-only reconciliation of the consumed reporting import; no ingestion client."""
from pathlib import Path
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    launcher = runpy.run_path(str(ROOT / 'scripts/recover-run2-reporting.py'))
    launcher['reporting_environment']()
    launcher['verify_preservation']()
    from scripts.run2_reporting_recovery import RECOVERY_ID, recover
    output = ROOT / 'artifacts/run2/reporting-recovery' / RECOVERY_ID
    claim = output / 'recovery-claim.json'
    if not claim.is_file():
        raise ValueError('Read-only verification requires the existing consumed claim')
    saved = json.loads(claim.read_text())
    phase = ROOT / 'artifacts/run2/runs/run2-full-conv-44-r0-p2'
    views = json.loads((phase / 'scoring-views.json').read_text())
    original = json.loads((phase / 'langfuse-imported.json').read_text())
    binding = json.loads((phase / 'approval.json').read_text())['binding']
    try:
        proof = recover(views, original, output, client=None,
            original_trace_ids=saved['original_trace_ids'], original_binding=binding)
    finally:
        launcher['verify_preservation']()
    print(json.dumps(proof))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'verified':False, 'error_type':type(error).__name__,
                          'message':'Read-only reconciliation stopped; no ingestion performed.'}))
        raise SystemExit(1)
