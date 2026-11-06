"""Verify saved Neither/conv-50 evidence without inference or re-import."""
from pathlib import Path
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amem_repro.blk027 import (
    CELL, PHASE, POLICY, SUPPLEMENT, pinned_inputs, read, sha, require, verify_remote,
    verify_merged_review,
)
from amem_repro.config import fingerprint, source_fingerprint
from amem_repro.openrouter import save_new


def verify_release(campaign, reviewed_commit, merge_commit):
    verify_merged_review(ROOT, reviewed_commit, merge_commit)
    verification = campaign/'verification/blk027-release'
    sources = source_fingerprint(ROOT)
    for axis in ('spec', 'standards'):
        review = read(verification/f'baseline-{axis}-review.json')
        require(review['verdict'] == 'pass' and review['reviewed_commit'] == reviewed_commit
                and review['source_sha256'] == fingerprint(sources),
                'Exact merged implementation reviews required')
    scripts = {name: sha(ROOT/name) for name in
               ('scripts/gpt4omini-blk027-accept.py', 'scripts/safe_service_audit.py')}
    for name, digest in {**sources['files'], **scripts}.items():
        import hashlib
        content = subprocess.check_output(['git', 'show', reviewed_commit+':'+name], cwd=ROOT)
        require(hashlib.sha256(content).hexdigest() == digest, 'Unreviewed runtime source')
    evidence = {str((verification/f'baseline-{axis}-review.json').relative_to(campaign)):
                sha(verification/f'baseline-{axis}-review.json') for axis in ('spec','standards')}
    evidence[str((verification/'full-suite.txt').relative_to(campaign))] = sha(verification/'full-suite.txt')
    return sources, scripts, evidence


def execute(reviewed_commit, merge_commit):
    from dotenv import dotenv_values
    from amem_repro.artifacts import CacheStore, restore_memory, snapshot_memory
    from amem_repro.gpt4omini_campaign import inventory
    from amem_repro.langfuse_verify import verify_observations
    campaign = ROOT/'artifacts/gpt4omini'
    sources, scripts, release_evidence = verify_release(campaign, reviewed_commit, merge_commit)
    current_source = fingerprint(sources)
    policy, directory, phase = pinned_inputs(campaign)
    before_ledger = sha(campaign/'budget.sqlite')
    output = (campaign/SUPPLEMENT).parent
    output.mkdir(parents=True, exist_ok=False)
    # No SDK client is instantiated. The existing CLI seam permits GET resources
    # only and independently removes model credentials from its environment.
    for key in list(os.environ):
        if any(x in key.upper() for x in ('OPENAI_API', 'OPENROUTER', 'DEEPSEEK', 'LANGFUSE')):
            os.environ.pop(key)
    private = dotenv_values(ROOT/'.env')
    for key in ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_BASE_URL', 'LANGFUSE_HOST'):
        if private.get(key): os.environ[key] = private[key]
    require((os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST'))
            == 'https://cloud.langfuse.com', 'Wrong cloud host')
    from scripts.safe_service_audit import check_langfuse_project_auth
    require(check_langfuse_project_auth(ROOT/'.env', 'cmvxd2aby005wad0ei7wt2d5o')['project_match'],
            'Wrong cloud project')
    cache_path = campaign/policy['cache_directory']
    identity = read(cache_path/'identity.json')
    cache = CacheStore(cache_path.parent)
    state = cache.load(identity)
    require(cache.path_for(identity) == cache_path and len(state['notes']) == 568
            and state['evo_cnt'] == 568 and not state['build_failures'], 'Cache incomplete')
    restored = SimpleNamespace(retriever=SimpleNamespace())
    restore_memory(restored, state, note_type=SimpleNamespace)
    require(snapshot_memory(restored, state['outcomes']) ==
            {k: v for k, v in state.items() if k != 'build_failures'}, 'Cache restoration differs')
    require(read(directory/'scoring-views.json')['author-corrected-v1']['individual_results']
            and [r['question_id'] for r in read(directory/'scoring-views.json')
                 ['author-corrected-v1']['individual_results']] == [f'conv-50:qa:{n}' for n in range(204)],
            'Original questions incomplete')
    with sqlite3.connect((campaign/'budget.sqlite').as_uri()+'?mode=ro&immutable=1', uri=True) as db:
        require(db.execute('SELECT state,seal FROM phases WHERE id=?', (PHASE,)).fetchone()
                == ('terminal', policy['original_phase_canonical_sha256']), 'Terminal ledger changed')
    context = {'binding': phase['binding'], 'output_dir': str(output)}
    # Original capture metadata owns the immutable run identity, not a new run.
    capture = read(directory/'trace-capture.json')
    context['binding'] = {**phase['binding'], 'run_id': PHASE}
    runtime = verify_observations(capture, context)
    remote = verify_remote(campaign, output)
    cache_proof = {'directory': policy['cache_directory'], 'files': inventory(cache_path)}
    save_new(output/'cache-proof.json', cache_proof)
    save_new(output/'restored-state-proof.json', {'verified': True, 'notes': 568, 'counter': 568,
             'state_sha256': sha(cache_path/'state.json'), 'network_inference': 0})
    pinned_inputs(campaign)
    require(sha(campaign/'budget.sqlite') == before_ledger
            and fingerprint(source_fingerprint(ROOT)) == current_source, 'State/source changed during readback')
    require(read(campaign/'cells'/CELL/'reconciliation.json')['verified'], 'Finance not reconciled')
    files = dict(policy['artifact_files'])
    files.update(release_evidence)
    files.update({str(p.relative_to(campaign)): sha(p) for p in output.rglob('*') if p.is_file()})
    files.update({str((cache_path/n).relative_to(campaign)): h for n,h in cache_proof['files'].items()})
    proof_path = next(output.glob('langfuse-blk027-readback-verified-*.json'))
    supplement = {'accepted': True, 'classification': 'Degraded', 'policy': POLICY,
        'cell': CELL, 'phase': PHASE, 'original_phase_sha256': policy['original_phase_file_sha256'],
        'original_phase_seal': policy['original_phase_canonical_sha256'], 'exceptions': policy['tuples'],
        'cache_proof': str((output/'cache-proof.json').relative_to(campaign)),
        'readback_proof': str(proof_path.relative_to(campaign)), 'runtime': runtime,
        'verification_source_sha256': current_source, 'verification_source': sources,
        'verifier_scripts': scripts, 'reviewed_commit': reviewed_commit,
        'merge_commit': merge_commit, 'files': files, 'inference_requests': 0,
        'cloud_ingestion': 0, 'ledger_writes': 0, 'original_receipt_status': 'incomplete'}
    save_new(campaign/SUPPLEMENT, supplement)
    print(json.dumps({'verified': remote['verified'], 'classification': 'Degraded',
                      'supplement_sha256': sha(campaign/SUPPLEMENT), 'independent_acceptance_pending': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reviewed-commit', required=True)
    parser.add_argument('--merge-commit', required=True)
    args = parser.parse_args()
    execute(args.reviewed_commit, args.merge_commit)
