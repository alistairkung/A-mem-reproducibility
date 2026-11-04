"""Reporting-only BLK-024 recovery. No model/runner imports or credentials."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APPROVAL_FILES = frozenset({
    'amem_repro/reporting.py', 'amem_repro/reporting_recovery.py',
    'amem_repro/langfuse_verify.py', 'amem_repro/observation_policy.py',
    'amem_repro/config.py', 'amem_repro/phases.py', 'amem_repro/preflight.py',
    'amem_repro/manifests.py', 'pyproject.toml', 'uv.lock',
    'scripts/recover-run2-reporting.py', 'scripts/verify-run2-reporting-offline.py',
    'tests/test_reporting_recovery.py',
    'artifacts/run2/reporting-recovery/preservation-before.json',
    'artifacts/run2/reporting-recovery/offline-payload-proof.json',
    'artifacts/run2/reporting-recovery/full-offline-suite.log',
    'artifacts/run2/reporting-recovery/standards-review.json',
    'artifacts/run2/reporting-recovery/spec-review.json',
})


def reporting_environment():
    from dotenv import dotenv_values
    keys = ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_BASE_URL', 'LANGFUSE_HOST')
    values = dotenv_values(ROOT / '.env')
    for key in list(os.environ):
        if any(s in key.upper() for s in ('DEEPSEEK', 'OPENAI', 'ANTHROPIC', 'LANGFUSE', 'OTEL_')):
            os.environ.pop(key)
    for key in keys:
        if values.get(key): os.environ[key] = values[key]
    host = os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST')
    if host != 'https://cloud.langfuse.com':
        raise ValueError('Only the intended Langfuse host is permitted')
    os.environ['LANGFUSE_OTEL_MAX_BATCH_SIZE_BYTES'] = str(32 * 1024 * 1024)
    original_dns = socket.getaddrinfo
    def langfuse_dns(host, *args, **kwargs):
        if host not in ('cloud.langfuse.com', b'cloud.langfuse.com'):
            raise PermissionError('Reporting process may connect only to Langfuse')
        return original_dns(host, *args, **kwargs)
    socket.getaddrinfo = langfuse_dns
    class ReportingImports:
        def find_spec(self, fullname, path=None, target=None):
            if (fullname.split('.')[0] in ('openai', 'litellm', 'ollama')
                    or fullname in ('amem_repro.deepseek', 'amem_repro.runner',
                                    'amem_repro.run2', 'amem_repro.author_runtime')):
                raise PermissionError('Model and scientific runners are forbidden in reporting')
    sys.meta_path.insert(0, ReportingImports())


def verify_preservation():
    frozen = json.loads((ROOT / 'artifacts/run2/reporting-recovery/preservation-before.json').read_text())
    for name, digest in frozen.items():
        member = ROOT / name
        h = hashlib.sha256()
        with member.open('rb') as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''): h.update(chunk)
        if h.hexdigest() != digest:
            raise ValueError('Authoritative historical artifact changed: ' + name)
    return len(frozen)


def verify_approval():
    approval = json.loads((ROOT / 'artifacts/run2/reporting-recovery/approved-reporting.json').read_text())
    if (approval.get('recovery_import_id') != 'run2-full-conv-44-reporting-recovery-20261104-v1'
            or approval.get('authorized') is not True or approval.get('model_calls') != 0
            or approval.get('max_imports') != 1 or approval.get('max_incremental_langfuse_usd') != 0):
        raise ValueError('Reporting-only approval is missing or differs')
    if set(approval.get('files', {})) != APPROVAL_FILES:
        raise ValueError('Approval must pin the complete reporting source, tests and review evidence')
    for name, digest in approval['files'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Reviewed reporting source/evidence changed')
    for axis in ('standards', 'spec'):
        review = json.loads((ROOT / f'artifacts/run2/reporting-recovery/{axis}-review.json').read_text())
        if review.get('verdict') != 'pass' or review.get('reviewed_commit') != approval.get('reviewed_commit'):
            raise ValueError('Independent review is not bound to the release')
    merged = approval.get('merge_commit', '')
    if len(merged) != 40 or not approval.get('reviewed_commit'):
        raise ValueError('Merged/reviewed source commits are required')
    for commit in (merged, approval['reviewed_commit']):
        subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'],
                       cwd=ROOT, check=True, capture_output=True)


def main(read_only):
    os.chdir(ROOT)
    verify_approval()
    verify_preservation()
    reporting_environment()
    from amem_repro.reporting_recovery import recover, RECOVERY_ID, BATCH_SPANS
    from amem_repro.observation_policy import should_export_span
    from amem_repro.langfuse_verify import _query_cli, VerificationError
    from langfuse import Langfuse
    phase = ROOT / 'artifacts/run2/runs/run2-full-conv-44-r0-p2'
    views = json.loads((phase / 'scoring-views.json').read_text())
    original = json.loads((phase / 'langfuse-imported.json').read_text())
    capture = json.loads((phase / 'trace-capture.json').read_text())
    traces = {r['metadata']['question_id']: r['trace_id'] for r in capture['observations']
              if r['name'] == 'answer' and r['type'] == 'generation'}
    output = ROOT / 'artifacts/run2/reporting-recovery' / RECOVERY_ID
    if read_only and not (output / 'recovery-claim.json').exists():
        raise VerificationError('Read-only resume requires an existing claim')
    # Read current project before creating the SDK client; all CLI actions are reads.
    check = _query_cli('observations', {'trace-id': next(iter(traces.values())),
                       'fields': 'core,basic', 'limit': 20, 'all': True, 'max-items': 30})
    rows = (check.get('body') or {}).get('data') or []
    if check.get('status') != 200 or not rows or any(r.get('projectId') != 'cmvxd2aby005wad0ei7wt2d5o' for r in rows):
        raise VerificationError('Intended project readback failed')
    client = None
    if not read_only:
        client = Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],
            secret_key=os.environ['LANGFUSE_SECRET_KEY'], base_url='https://cloud.langfuse.com',
            environment='amem-run2', flush_at=BATCH_SPANS, should_export_span=should_export_span)
    try:
        binding = json.loads((phase / 'approval.json').read_text())['binding']
        proof = recover(views, original, output, original_trace_ids=traces,
                        original_binding=binding, client=client)
    finally:
        if client is not None: client.shutdown()
        verify_preservation()
    print(json.dumps(proof))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-only', action='store_true')
    args = parser.parse_args()
    try:
        main(args.read_only)
    except Exception as error:
        # Raw SDK exceptions may contain authentication headers; never echo them.
        print(json.dumps({'status': 'stopped', 'error_type': type(error).__name__,
                          'message': 'Preserve all evidence; no automatic ingestion retry.'}))
        raise SystemExit(1)
