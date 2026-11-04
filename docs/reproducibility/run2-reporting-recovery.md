# Run2 reporting-only recovery

4 November2026. Authorized scope: [latest decision](decisions.md#authorization--blk-024-reporting-only-recovery-and-cost-reforecast).
BLK-024 remains Open until actual recovery readback passes. No model execution is authorized.

## Implementation boundary

Use pinned Langfuse5.1.0, `flush_at=16`, serial saved-result callbacks and the frozen essential
observation filter. A stricter32MiB serialized batch ceiling leaves50% headroom under the original
64MiB limit. No evaluator, name, score value, reference-selection or original-record change.
A separate reporting wrapper supplies explicit Experiment IDs and original QA trace associations.
The historical exporter and every scientific source fingerprint remain byte-identical.

Recovery ID: `run2-full-conv-44-reporting-recovery-20261104-v1`. Keep original inference run ID
`run2-full-conv-44-r0-p2`, campaign, condition, population/scorer/provider-policy and manifest pins.
The recovery ID participates in the new run-name fingerprint and explicit separate Experiment IDs.
Each item carries its unchanged original record and original paid QA trace ID; new import trace
IDs describe reporting, not paid inference. Only fresh recovery IDs are canonical for acceptance.

Before ingestion, read original and fresh Experiments/items/scores and original import-window
scores. Preserve original cloud records; do not delete/relabel/reuse them. Reject unidentified or
excess original score writes, preexisting unclaimed recovery IDs, duplicate/missing/foreign items,
score values/counts/subjects or overlapping original/recovery traces. Preserve all raw readbacks.
A durable exclusive claim precedes the one SDK import. Any later invocation resumes readback only,
even if the process crashed before persisting the SDK return. Partial recovery writes stop; they
never trigger automatic re-ingestion. Readback can accept a fully delivered interrupted import.

The launcher loads only Langfuse credentials, rejects model/runner imports and non-Langfuse DNS,
checks reviewed phase-bound reporting approval and hashes of all1,741 existing scientific/artifact
files before/after, and never opens a budget for writing. Output is isolated under
`artifacts/run2/reporting-recovery/`. The old sealed Incomplete phase and ledger/frontier are untouched.

## Offline gates and debug diary

- Pre-change snapshot:1,741 historical/scientific files, including both ledgers, all Run1 artifacts,
  all three Run2 phases, caches/checkpoints, author files, population/configuration and prior evidence.
- Read-only inspection: original Experiments/items/experiment-scoped scores0/0/0, but original
  import-window query finds4,494 orphan scores (2,247 per scoring view), attached to original
  observation/trace subjects. These explain why empty Experiment reads did not prove no writes.
  Preserve them as original failed-import evidence, excluded from canonical recovery.
- Actual saved-data SDK serialization, network blocked: default632 spans/316 items/4,494 scores,
  two batches, max155,912,209B (both above64MiB). Sixteen-span batching:40 batches, max9,075,061B,
  all records and original trace mappings exact, no oversized batch, zero network/model calls.
- Regression tests cover exact import/read-only resume, partial/interrupted writes, unclaimed
  duplicates, foreign Run1 identities, altered values/counts/trace subjects and model/DNS exclusion.
- Full offline suite and independent Standards/Spec reviews are required before merge/ingestion;
  final results and review commits will be recorded below and in the outcome report.

## Evidence inventory

`artifacts/run2/reporting-recovery/`: `preservation-before.json`, `original-inspection/`,
`original-inspection.log`, `offline-payload-proof.json`, `offline-payload.log`, focused/full test logs,
review reports and the later merged-source immutable reporting approval. Recovery-specific claim,
pre-ingestion inventory, original-score isolation, SDK return and exact readback proofs live in the
subdirectory named by the recovery ID. No original receipt is superseded in place.

Current billing read-only refresh: Core,3 November–3 December2026,13,174 hourly-lagged period units,
16,878 daily-bucket units (different scopes; never add), draft usageUSD0, existing subscriptionUSD29
separate. Recovery nominal5,442 units (632 observations +316 traces +4,494 scores) fits100K included.
Allow one bounded import only; no service-overage allocation is created.

## Operator commands

After independent review, normal implementation merge, successful full offline suite and a reviewed
approval bound to current source, evidence and zero additional service fee:

```sh
.venv/bin/python scripts/recover-run2-reporting.py
# On interruption: reads only; never repeats the import.
.venv/bin/python scripts/recover-run2-reporting.py --read-only
```

Successful readback must verify316 question/view items,4,494 exact scores, distinct reporting traces,
all158 original QA trace associations and both full scoring views. Reconcile immutable local
collection/accounting and runtime proofs before a separately verified Degraded lineage supplement.
BLK-009 remains Open and all future paid cells remain blocked pending a cost-only scope decision.

Debug diary addendum: the default historical BLK-022 tests read the current multi-phase ledger but
copy only p0, causing missing-p1 evidence failures. Preserve those failed suite logs. Run the complete
suite using the tests’ existing `AMEM_BLK022_EVIDENCE_ROOT` option, pointing to an isolated fixture
whose ledger is copied exactly from immutable `budget-at-transport-stop.sqlite`; other incident
evidence/assets are read-only links. No test expectation, production provenance gate or ledger is
weakened. The new support module lives in `scripts/run2_reporting_recovery.py`, outside the frozen
scientific source inventory; original `amem_repro/reporting.py` remains byte-identical.

```sh
AMEM_BLK022_EVIDENCE_ROOT="$PWD/artifacts/run2/reporting-recovery/historical-fixture" .venv/bin/pytest -q
```
