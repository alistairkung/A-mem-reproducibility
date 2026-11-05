"""Measure the full saved-result GPT reporting path without network access.

The immutable Run2 rows are engineering payload fixtures only. Their predictions,
metrics and provider-policy labels stay unchanged; no GPT scientific result is
created. The production import_results/AssociatedClient and Langfuse SDK execute
normally, with a measuring OTLP exporter and a local API-shaped readback fixture.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import uuid
from collections import Counter
from importlib.metadata import version
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amem_repro.config import fingerprint, source_fingerprint, stage_output_limits, OPENROUTER_CONFIG
from amem_repro.gpt4omini_reporting import import_results, original_qa_traces
from amem_repro.langfuse_verify import VerificationError
from amem_repro.observation_policy import should_export_span
from amem_repro.openrouter import SCIENTIFIC_BINDING, save_new
from amem_repro.phases import _deny_network

CEILING = 32 * 1024 * 1024


def sha(path):
    return hashlib.file_digest(Path(path).open('rb'), 'sha256').hexdigest()


def execute(fixture, output):
    # This proof neither loads .env nor permits an external exporter/score worker.
    os.environ['LANGFUSE_OTEL_MAX_BATCH_SIZE_BYTES'] = str(CEILING)
    from langfuse import Langfuse, LangfuseOtelSpanAttributes as A
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
    from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
    import amem_repro.langfuse_verify as verifier

    fixture, output = Path(fixture).resolve(), Path(output).resolve()
    namespace = (ROOT / 'artifacts/gpt4omini').resolve()
    if not output.is_relative_to(namespace) or output.exists():
        raise ValueError('Use a fresh proof receipt in the isolated GPT namespace')
    views_path, capture_path = fixture / 'scoring-views.json', fixture / 'trace-capture.json'
    views = json.loads(views_path.read_bytes())
    traces = original_qa_traces(json.loads(capture_path.read_bytes()))
    before = fingerprint(views)
    policies = {row['provider_contract_policy'] for view in views.values()
                for row in view['individual_results']}
    nqa=len(next(iter(views.values()))['individual_results'])
    if len(policies) != 1 or nqa not in (158,196,204) or sorted(len(v['individual_results']) for v in views.values()) != [nqa,nqa]:
        raise ValueError('Expected two complete original-conversation engineering views')
    expected_scores = Counter((policy, row['question_id'], name, value)
                              for policy, view in views.items()
                              for row in view['individual_results']
                              for name, value in row['metrics'].items())
    nitems=2*nqa
    nscores={158:4494,196:5568,204:5804}[nqa]
    if sum(expected_scores.values()) != nscores or len(traces) != nqa:
        raise ValueError('Original score/QA coverage differs')

    class Exporter(SpanExporter):
        def __init__(self, partial=False):
            self.partial = partial
            self.sizes, self.counts, self.spans = [], Counter(), []
            self.accepted_batches = 0

        def export(self, spans):
            self.sizes.append(len(encode_spans(spans).SerializePartialToString()))
            self.counts.update(span.name for span in spans)
            if self.partial and self.accepted_batches:
                return SpanExportResult.FAILURE
            self.accepted_batches += 1
            self.spans.extend(spans)
            return SpanExportResult.SUCCESS

        def shutdown(self):
            pass

    class LocalCloud:
        """Delegate generation of every span and score to the unmodified SDK."""
        def __init__(self, sdk, exporter, scores, partial=False):
            self.sdk, self.exporter, self.scores = sdk, exporter, scores
            self.partial, self.calls = partial, 0
            self.experiments = []
            self.mutation = None

        def run_experiment(self, **kwargs):
            self.calls += 1
            result = self.sdk.run_experiment(**kwargs)
            if self.partial:
                raise RuntimeError('Offline interruption after first-view partial export')
            self.experiments.append({'id': result.experiment_id, 'name': result.run_name,
                                     'itemCount': len(kwargs['data']),
                                     'metadata': copy.deepcopy(kwargs['metadata'])})
            return result

        def flush(self):
            self.sdk.flush()

        def items(self):
            by_subject = {}
            for score in self.scores:
                by_subject.setdefault(score['subject']['id'], []).append(score)
            return [{'id': span.attributes[A.EXPERIMENT_ITEM_ROOT_OBSERVATION_ID],
                     'experimentId': span.attributes[A.EXPERIMENT_ID],
                     'experimentItemId': span.attributes[A.EXPERIMENT_ITEM_ID],
                     'traceId': f'{span.context.trace_id:032x}',
                     'input': span.attributes[A.OBSERVATION_INPUT],
                     'output': span.attributes[A.OBSERVATION_OUTPUT],
                     'expectedOutput': span.attributes[A.EXPERIMENT_ITEM_EXPECTED_OUTPUT],
                     'experimentItemMetadata': span.attributes[A.EXPERIMENT_ITEM_METADATA],
                     'experimentMetadata': span.attributes[A.EXPERIMENT_METADATA],
                     'scores': by_subject.get(span.attributes[A.EXPERIMENT_ITEM_ROOT_OBSERVATION_ID], [])}
                    for span in self.exporter.spans if span.name == 'experiment-item-run']

        def query(self, resource, options):
            ids = options.get('id', options.get('experiment-id', '')).split(',')
            if resource == 'experiments':
                data = [x for x in self.experiments if x['id'] in ids]
            elif resource == 'experiment-items':
                data = [x for x in self.items() if x['experimentId'] in ids]
            elif resource == 'scores':
                wanted = options['trace-id'].split(',')
                assert len(wanted) <= 50
                data = [x for x in self.scores if x['subject']['traceId'] in wanted]
                if self.mutation == 'score-subject' and data:
                    data = copy.deepcopy(data)
                    data[0]['subject']['id'] = 'wrong-observation'
            else:
                raise AssertionError('Unexpected readback resource')
            return {'status': 200, 'body': {'data': data, 'meta': {'truncated': False}}}

    results = {}
    network_attempts = []
    def deny(*args, **kwargs):
        network_attempts.append(True)
        raise RuntimeError('Network denied by offline reporting proof')

    def immediate_readback(output, operation, attempts, delay_seconds):
        # A local deterministic API fixture has no indexing delay. Preserve the
        # production checks and evidence writes, without polling a fixture bug.
        paths = []
        return operation(paths), paths

    with tempfile.TemporaryDirectory(prefix='amem-gpt-reporting-') as directory, _deny_network(), \
            patch.object(socket.socket, 'connect', deny), patch.object(socket.socket, 'connect_ex', deny), \
            patch.object(socket, 'create_connection', deny), \
            patch.object(verifier, '_retry', side_effect=immediate_readback):
        for partial in (False, True):
            exporter, scores = Exporter(partial), []
            sdk = Langfuse(public_key='pk-lf-offline-' + uuid.uuid4().hex,
                secret_key='offline-placeholder', base_url='https://langfuse.invalid',
                tracer_provider=TracerProvider(), span_exporter=exporter,
                should_export_span=should_export_span, flush_at=16)
            cloud = LocalCloud(sdk, exporter, scores, partial)
            phase = 'partial' if partial else 'complete'
            dest = Path(directory) / 'artifacts/gpt4omini/reporting-proof' / phase
            binding = {**SCIENTIFIC_BINDING, 'source_sha256': fingerprint(source_fingerprint(ROOT)),
                       'condition': 'full', 'population': 'fallback', 'repetition': 0,
                       'conversation_id': 'conv-44',
                       'manifest_sha256': fingerprint(json.loads((ROOT / 'manifests/fallback.json').read_bytes())),
                       'run_id': 'offline-full-size-reporting-' + phase,
                       'provider_contract_policy': next(iter(policies)),
                       'max_output_tokens_by_stage': stage_output_limits(OPENROUTER_CONFIG)}
            context = {'binding': binding, 'output_dir': str(dest)}
            def capture_score(score, **kwargs):
                # Actual SDK.create_score has already normalized this payload.
                scores.append({'id': score['id'], 'name': score['name'], 'value': score['value'],
                               'subject': {'kind': 'observation', 'id': score['observationId'],
                                           'traceId': score['traceId']}})
            try:
                with patch.object(sdk, '_get_project_id', return_value='offline-project'), \
                        patch.object(sdk._resources, 'add_score_task', side_effect=capture_score):
                    if partial:
                        try:
                            import_results(views, context, client=cloud, traces=traces, query=cloud.query)
                        except RuntimeError:
                            pass
                        else:
                            raise AssertionError('Injected partial import unexpectedly completed')
                        assert (dest / 'langfuse-import-claim.json').exists()
                        assert not (dest / 'langfuse-imported.json').exists()
                        counts = cloud.calls, len(exporter.spans), len(scores)
                        try:
                            import_results(views, context, client=cloud, traces=traces, query=cloud.query)
                        except VerificationError:
                            pass
                        else:
                            raise AssertionError('Partial import was automatically repeated')
                        assert counts == (cloud.calls, len(exporter.spans), len(scores))
                        results[phase] = {'sdk_experiment_calls': cloud.calls,
                            'accepted_span_batches': exporter.accepted_batches,
                            'accepted_spans': len(exporter.spans), 'scores_prepared': len(scores),
                            'claim_retained_no_import_receipt': True,
                            'resume_rejected_without_additional_spans_scores_or_import': True}
                    else:
                        proof = import_results(views, context, client=cloud, traces=traces, query=cloud.query)
                        assert proof['items'] == nitems and proof['scores'] == nscores
                        # SDK5.1's item root/score subject is the task observation.
                        roots = {f'{s.context.span_id:016x}': s for s in exporter.spans
                                 if s.name == 'experiment-item-task'}
                        assert len(roots) == nitems and len(scores) == nscores
                        actual = Counter()
                        for score in scores:
                            root = roots[score['subject']['id']]
                            assert score['subject']['traceId'] == f'{root.context.trace_id:032x}'
                            assert root.attributes[A.EXPERIMENT_ITEM_ROOT_OBSERVATION_ID] == score['subject']['id']
                            md = json.loads(root.attributes[A.EXPERIMENT_ITEM_METADATA])
                            row = next(x for x in views[md['scoring_policy']]['individual_results']
                                       if x['question_id'] == md['question_id'])
                            assert md['original_record'] == row
                            assert md['original_trace_id'] == traces[row['question_id']]
                            actual[(md['scoring_policy'], row['question_id'], score['name'], score['value'])] += 1
                        assert actual == expected_scores
                        counts = cloud.calls, len(exporter.spans), len(scores)
                        assert import_results(views, context, client=cloud, traces=traces,
                                              query=cloud.query)['verified']
                        assert counts == (cloud.calls, len(exporter.spans), len(scores))
                        assert exporter.counts == {'experiment-item-run': nitems, 'experiment-item-task': nitems}
                        assert max(exporter.sizes) < CEILING
                        results[phase] = {'verified': True, 'items': nitems, 'scores': nscores,
                            'original_qa_associations': nqa, 'reporting_traces': nitems,
                            'all_metric_question_policy_values_and_score_subjects_exact': True,
                            'all_original_records_and_trace_associations_exact': True,
                            'sdk_experiment_calls': cloud.calls, 'span_counts': dict(exporter.counts),
                            'batch_count': len(exporter.sizes), 'batch_sizes_bytes': exporter.sizes,
                            'max_batch_bytes': max(exporter.sizes),
                            'readonly_resume_has_no_additional_export_or_score': True}
            finally:
                sdk.shutdown()
    assert not network_attempts and fingerprint(views) == before
    receipt = {'verified': True, 'engineering_payload_fixture_only': True,
        'not_gpt_scientific_results': True, 'actual_gpt_import_results_and_associated_client': True,
        'actual_sdk_create_score_and_otlp_encoding': True, 'sdk_version': version('langfuse'),
        'flush_at': 16, 'safety_ceiling_bytes': CEILING,
        'local_fixture_readback_attempts': 1,
        'source_sha256': fingerprint(source_fingerprint(ROOT)),
        'script': str(Path(__file__).relative_to(ROOT)), 'script_sha256': sha(__file__),
        'fixture_files': {str(views_path): sha(views_path), str(capture_path): sha(capture_path)},
        'fixture_rows_provider_policy_preserved': next(iter(policies)), 'results_sha256': before,
        'network_attempts': len(network_attempts), 'network_requests': 0, 'model_calls': 0,
        'cloud_writes': 0, 'existing_artifact_writes': 0, 'results': results}
    save_new(output, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-phase', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.fixture_phase is None:
        preservation = json.loads((ROOT / 'artifacts/gpt4omini/verification/prior-preservation-authoritative-v2.json').read_bytes())
        args.fixture_phase = Path(preservation['legacy_root']) / 'artifacts/run2/runs/run2-full-conv-44-r0-p2'
    execute(args.fixture_phase, args.output)
