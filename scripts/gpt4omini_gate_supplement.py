"""One additional metered release check under the BLK-027 continuation grant."""
from pathlib import Path
import hashlib
import json
import subprocess

from amem_repro.blk027 import verify_merged_review
from amem_repro.config import fingerprint, source_fingerprint
from amem_repro.openrouter import BLK027_GATE_UNITS, PROGRAM_SERVICE_RESERVE, save_new
from scripts.gpt4omini_service import ServiceUnits


GATE_RUNTIME_FILES = (
    'scripts/gpt4omini-gate.py', 'scripts/gpt4omini_gate_supplement.py',
    'scripts/gpt4omini_service.py', 'tests/gpt4omini_fixture.py',
    'tests/gpt4omini_executor_fixture.py', 'tests/test_foundation.py',
    'tests/test_scoring.py', 'tests/test_observability.py',
    'tests/observability_fixture.py',
)


def reserve(root, output):
    root = Path(root)
    directory = root/'artifacts/gpt4omini/verification/blk027-release'
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    plan = read(directory/'gate-approval.json')
    if (plan.get('approved') is not True or plan.get('policy') != 'blk027-single-release-gate-v1'
            or plan['units'] != BLK027_GATE_UNITS or plan['marginal_microusd'] != 89440
            or plan['program_service_reserve_microusd'] != PROGRAM_SERVICE_RESERVE
            or plan['source_sha256'] != fingerprint(source_fingerprint(root))
            or output.parent != directory or output.name != plan['output']):
        raise RuntimeError('Unapproved additional cloud verification')
    verify_merged_review(root, plan['reviewed_commit'], plan['merge_commit'])
    for axis in ('standards','spec'):
        review = read(directory/f'baseline-{axis}-review.json')
        if (review['verdict'] != 'pass' or review['reviewed_commit'] != plan['reviewed_commit']
                or review['source_sha256'] != plan['source_sha256']):
            raise RuntimeError('Exact gate implementation review required')
    for name, digest in plan['files'].items():
        path = root/name
        if path.resolve() != path or not path.is_file() or sha(path) != digest:
            raise RuntimeError('Bound gate funding/source/evidence changed')
    for name,digest in {**source_fingerprint(root)['files'],
                        **{n:h for n,h in plan['files'].items() if not n.startswith('artifacts/')}}.items():
        blob = subprocess.check_output(['git','show',plan['reviewed_commit']+':'+name],cwd=root)
        if hashlib.sha256(blob).hexdigest()!=digest:
            raise RuntimeError('Cloud verifier differs from reviewed Git bytes')
    required = set(GATE_RUNTIME_FILES) | {
                'artifacts/gpt4omini/budget.sqlite',
                'artifacts/gpt4omini/verification/six-cell-expansion/final-cloud-verification-claim.json',
                'artifacts/gpt4omini/verification/six-cell-expansion/six-cell-final-2b65f2e/receipt.json'}
    if not required <= plan['files'].keys():
        raise RuntimeError('Prior gate and current funding evidence required')
    save_new(directory/'cloud-verification-claim.json', {
        'approval_sha256': sha(directory/'gate-approval.json'), 'units_reserved': BLK027_GATE_UNITS,
        'marginal_microusd_reserved': 89440, 'source_sha256': plan['source_sha256'],
        'output': output.name})
    return ServiceUnits(BLK027_GATE_UNITS)
