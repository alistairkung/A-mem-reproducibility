"""Execute one explicitly approved BLK-022 child; no approval creation or recovery loop."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import sys
import traceback

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT))


def main(approval_path, preflight_path):
    from dotenv import dotenv_values
    from amem_repro import run2
    from amem_repro.config import fingerprint
    from amem_repro.langfuse_verify import verify_observations, import_and_verify_results
    from amem_repro.observation_policy import POLICY_ID, should_export_span
    from amem_repro.observability import LangfuseObserver
    from amem_repro.phases import _save
    approval = json.loads(Path(approval_path).read_text())
    preflight = json.loads(Path(preflight_path).read_text())
    campaign = json.loads((ROOT / 'artifacts/run2/frozen/campaign-approval.json').read_text())
    run2._validate_phase(approval, campaign)
    binding = approval['binding']
    migration = binding['support_migration']
    if (approval['run_id'] != 'run2-full-conv-44-r0-p1'
            or binding['checkpoint']['completed_turns'] != 227
            or approval['limits'] != {'phase_usd': '3.955163', 'max_logical_calls': 1212,
                                      'max_attempts': 3636}
            or migration['observability']['policy'] != POLICY_ID
            or hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
               != migration['observability']['execution_script_sha256']):
        raise ValueError('One-cell recovery approval or launcher differs')
    run2._check_campaign_runtime(campaign, preflight, ROOT / 'artifacts/assets', ROOT,
        financial_adjudication=binding['financial_adjudication'],
        support_reference=migration['reviewed_commit'], phase_binding=binding)
    values = dotenv_values(ROOT / '.env')
    keys = ('DEEPSEEK_API_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY',
            'LANGFUSE_BASE_URL', 'LANGFUSE_HOST')
    for key in keys:
        os.environ.pop(key, None)
        if values.get(key):
            os.environ[key] = values[key]
    host = os.environ.get('LANGFUSE_BASE_URL') or os.environ.get('LANGFUSE_HOST')
    if host != 'https://cloud.langfuse.com' or not all(os.environ.get(k) for k in keys[:3]):
        raise ValueError('Current private provider/project configuration is incomplete')
    from amem_repro.langfuse_verify import _query_cli
    check = _query_cli('observations', {'trace-id': 'ed1dc6012ed690a995ccf3f023a82ae4',
                                      'fields': 'core,basic', 'limit': 1})
    rows = (check.get('body') or {}).get('data') or []
    if check.get('status') != 200 or not rows or any(
            row.get('projectId') != 'cmvxd2aby005wad0ei7wt2d5o' for row in rows):
        raise ValueError('Current Langfuse credentials cannot read the intended project')
    from langfuse import Langfuse
    client = Langfuse(public_key=os.environ['LANGFUSE_PUBLIC_KEY'],
        secret_key=os.environ['LANGFUSE_SECRET_KEY'], base_url=host,
        environment='amem-run2', release=binding['source_sha256'],
        tracing_enabled=True, debug=False, should_export_span=should_export_span)
    metadata = {k:binding[k] for k in ('campaign_id', 'condition', 'population',
        'manifest_sha256', 'repetition', 'provider_contract_policy', 'source_sha256',
        'config_sha256', 'max_output_tokens_by_stage')}
    metadata.update(run_id=approval['run_id'], conversation_id='conv-44',
        observability_policy=POLICY_ID, execution_mode='paid_primary_run2',
        parent_run_id=binding['checkpoint']['parent_run_id'],
        financial_receipt_sha256=fingerprint(binding['financial_adjudication']),
        support_migration=migration)
    observer = LangfuseObserver(client, metadata)
    def observations(capture, context):
        _save(Path(context['output_dir']) / 'trace-capture.json', capture)
        return verify_observations(capture, context)
    try:
        phase = run2.execute_phase(approval, campaign, preflight, ROOT / 'artifacts/assets',
            root=ROOT, observer=observer, verify_observations=observations,
            verify_results=lambda views, context: import_and_verify_results(views, context, client=client))
    finally:
        client.shutdown()
    print(json.dumps({k:phase[k] for k in ('run_id', 'status', 'total_memory_notes',
        'completed_questions', 'cell_budget', 'campaign_budget', 'error_type', 'usable_for_next_phase')}))
    return 0 if phase['usable_for_next_phase'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approval', required=True)
    parser.add_argument('--preflight', required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(main(args.approval, args.preflight))
    except Exception:
        from safe_service_audit import redact_operator_text
        secrets = [os.environ.get(k) for k in
                   ('DEEPSEEK_API_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY')]
        secrets.append(base64.b64encode((str(secrets[1] or '') + ':' + str(secrets[2] or '')).encode()).decode())
        # An operator copy only; original scientific/provider journals stay untouched.
        message = redact_operator_text(traceback.format_exc(), secrets=secrets)
        target = ROOT / 'artifacts/run2-observed-recovery/launcher-errors'
        target.mkdir(parents=True, exist_ok=True)
        import uuid
        with (target / (uuid.uuid4().hex + '.txt')).open('x') as handle:
            handle.write(message)
        raise SystemExit('Run2 stopped; one-shot approval is not retried. Redacted evidence preserved.')
