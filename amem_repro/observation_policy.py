"""Run2 export policy: retain scientific work, omit duplicate import bookkeeping."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

POLICY_ID = 'run2-audit-essential-v1'
GATE_DIRECTORY = 'artifacts/run2/observed-recovery/gate-b'
LAUNCHER = 'scripts/run2-checkpoint.py'


def should_export_span(span):
    """Only successful saved-result evaluator bookkeeping is removable.

    Keep failed groups and their error children, avoiding orphaned observations.
    Ordinary author-scoring, LLM and action spans are never import bookkeeping.
    """
    from langfuse import LangfuseOtelSpanAttributes as A
    from langfuse.span_filter import is_default_export_span
    attrs = span.attributes or {}
    try:
        meta = json.loads(attrs.get(A.EXPERIMENT_METADATA, '{}'))
    except (ValueError, TypeError):
        meta = {}
    scoped = (attrs.get(A.EXPERIMENT_ID) and isinstance(meta, dict)
              and meta.get('observability_policy') == POLICY_ID
              and meta.get('execution_mode') == 'imported_results')
    if not scoped:
        return is_default_export_span(span)
    try:
        output = json.loads(attrs.get(A.OBSERVATION_OUTPUT, '{}'))
    except (ValueError, TypeError):
        output = {}
    failed = (attrs.get(A.OBSERVATION_LEVEL) in ('ERROR', 'WARNING')
              or bool(attrs.get(A.OBSERVATION_STATUS_MESSAGE))
              or (isinstance(output, dict) and bool(output.get('failed_evaluator_count'))))
    bookkeeping = (span.name == 'experiment-item-evaluation'
                   or attrs.get(A.OBSERVATION_TYPE) == 'evaluator')
    return is_default_export_span(span) and (failed or not bookkeeping)


def release_binding(root, source_sha256):
    """Bind the fixed one-cell launcher and secured, source-bound cloud gate."""
    root = Path(root).resolve()
    path = root / GATE_DIRECTORY / source_sha256 / 'receipt.json'
    gate = json.loads(path.read_text())
    required = ('real_runner', 'remote_observations_verified', 'experiments_verified',
                'replay_equivalence', 'output_exhaustion_verified', 'tracing_failure_verified')
    if (gate.get('observability_policy') != POLICY_ID
            or gate.get('source_sha256') != source_sha256
            or gate.get('network_llm_requests') != 0
            or any(gate.get(k) is not True for k in required)
            or not gate.get('files')):
        raise ValueError('Source-bound essential-observation GateB is missing or invalid')
    for name, digest in gate['files'].items():
        member = (path.parent / name).resolve()
        if not member.is_relative_to(path.parent) or hashlib.sha256(member.read_bytes()).hexdigest() != digest:
            raise ValueError('Essential-observation gate evidence changed')
    credential_path = root / 'artifacts/run2-observed-recovery/credential-rotation-verified.json'
    credential = json.loads(credential_path.read_text())
    if any(credential.get(k) is not True for k in (
            'new_authentication_verified', 'read_existing_trace_verified', 'original_1_nov_key_absent')):
        raise ValueError('Replacement credential/project/revocation verification is missing')
    return {'policy': POLICY_ID,
            'gate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'credential_receipt_sha256': hashlib.sha256(credential_path.read_bytes()).hexdigest(),
            'execution_script_sha256': hashlib.sha256((root / LAUNCHER).read_bytes()).hexdigest()}
