"""Reproduce BLK-024 and verify the exact bounded recovery payload offline."""
import json
from pathlib import Path
import sys
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from amem_repro.config import fingerprint
from amem_repro.reporting import export_experiments
from amem_repro.reporting_recovery import recovery_plan, RECOVERY_ID, PAYLOAD_CEILING
from amem_repro.observation_policy import should_export_span, POLICY_ID
from amem_repro.phases import _deny_network, _save
from langfuse import Langfuse, LangfuseOtelSpanAttributes as A
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans


def main():
    phase = ROOT / 'artifacts/run2/runs/run2-full-conv-44-r0-p2'
    views = json.loads((phase / 'scoring-views.json').read_text())
    original = json.loads((phase / 'langfuse-imported.json').read_text())
    capture = json.loads((phase / 'trace-capture.json').read_text())
    traces = {r['metadata']['question_id']: r['trace_id'] for r in capture['observations']
              if r['name'] == 'answer' and r['type'] == 'generation'}
    plan = recovery_plan(views, original, traces)
    before = fingerprint(views)
    class Exporter(SpanExporter):
        def __init__(self): self.sizes=[]; self.roots=[]; self.span_count=0
        def export(self, spans):
            self.sizes.append(len(encode_spans(spans).SerializePartialToString()))
            self.span_count += len(spans)
            self.roots.extend(s for s in spans if s.name == 'experiment-item-run')
            return SpanExportResult.SUCCESS
        def shutdown(self): pass
    results = []
    for batch in (None, 16):
        exporter = Exporter(); scores=[]
        client = Langfuse(public_key='pk-lf-offline-' + uuid.uuid4().hex,
            secret_key='offline-placeholder', base_url='https://langfuse.invalid',
            tracer_provider=TracerProvider(), span_exporter=exporter,
            should_export_span=should_export_span, flush_at=batch)
        metadata = {**plan['identity'], 'recovery_import_id': RECOVERY_ID,
                    'observability_policy': POLICY_ID,
                    'supersedes_failed_import': {p:r['id'] for p,r in original['experiments'].items()}}
        binding = json.loads((phase / 'approval.json').read_text())['binding']
        metadata.update({k: binding[k] for k in
                         ('config_sha256', 'source_sha256', 'max_output_tokens_by_stage')})
        with _deny_network(), patch.object(client, '_get_project_id', return_value='offline'), patch.object(
                client, 'create_score', side_effect=lambda **kw: scores.append(kw)):
            export_experiments(views, client=client, export_authorized=True, metadata=metadata,
                experiment_ids={p:r['id'] for p,r in plan['experiments'].items()}, original_trace_ids=traces)
            client.flush()
        client.shutdown()
        for span in exporter.roots:
            md = json.loads(span.attributes[A.EXPERIMENT_ITEM_METADATA])
            row = next(r for r in views[md['scoring_policy']]['individual_results'] if r['question_id'] == md['question_id'])
            assert md['original_record'] == row
            assert md['original_trace_id'] == traces[row['question_id']]
        assert len(exporter.roots) == 316 and len(scores) == 4494 and fingerprint(views) == before
        if batch is None: assert max(exporter.sizes) > 64 * 1024 * 1024
        else: assert max(exporter.sizes) < PAYLOAD_CEILING
        results.append({'flush_at': batch, 'span_count': exporter.span_count,
                        'item_count': len(exporter.roots), 'score_count': len(scores),
                        'batch_count': len(exporter.sizes), 'max_batch_bytes': max(exporter.sizes),
                        'over_64mib': sum(s > 64*1024*1024 for s in exporter.sizes),
                        'all_original_records_and_trace_associations_exact': True})
    evidence = {'recovery_import_id': RECOVERY_ID, 'results_sha256': before, 'results': results,
                'network_calls': 0, 'model_calls': 0, 'safety_ceiling_bytes': PAYLOAD_CEILING,
                'sdk_version': '5.1.0'}
    _save(ROOT / 'artifacts/run2/reporting-recovery/offline-payload-proof.json', evidence)
    print(json.dumps(evidence))


if __name__ == '__main__': main()
