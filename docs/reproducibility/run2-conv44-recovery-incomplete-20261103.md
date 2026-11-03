# Run2 conv-44 recovery — incomplete after malformed provider output

3 November 2026. The one authorized checkpoint child has stopped. **Run2 has no completed cell or
primary quality scores.** No further paid phase was started. The frozen scientific configuration,
strict validation and historical evidence remain unchanged.

## Release and checkpoint verification

[PR#29](https://github.com/alistairkung/A-mem-reproducibility/pull/29) merged as
`afcecdbbfddbc6bc06bdbd4f2524dd58692dedac`. Source fingerprint:
`265094c0a6484105b3922862633b7063fd5a4f917663349fdf720658e0864fbf`.
The merged source/launcher, exact227-note checkpoint, counter226, stale float32 index, financial
receipt, credential proof, dataset/model and new observability policy were checked before admission.
The child resumed atD10:11, without rebuilding or recharging the original prefix.

- Parent: `run2-full-conv-44-r0-p0`.
- Child: `run2-full-conv-44-r0-p1`.
- Consumed child approval: `8854d11c-3202-4c38-948b-409c4be350f4`.
- Provider policy: `canonical-index-strings-v1`; observation policy: `run2-audit-essential-v1`.
- Generation policy remains `run2-shared-decision-8192-v1`, DeepSeek Flash, thinking disabled.

Release verification: **764 tests/92 subtests pass**, with17 expected warnings. Complete original
and full-candidate archive replays match all1,544 requests/568 notes/204 questions, every insertion,
index/context/prediction and both scoring views; only the implementation label differs. Independent
Standards and Spec reviews pass after the terminal request-admission correction. This is offline
regression evidence, not new primary benchmark results.

## Observed failure and preserved state

The child added339 original turns, reaching **566/675 notes, evolution counter564, zero of158 QA**.
AtD24:12, request `0d1fd874-a744-4be4-af5b-10983cfc41d4` returned HTTP200 with normal forced-function
`finish_reason=tool_calls`, but its inner function arguments are malformed JSON:

```text
Expecting ':' delimiter: line 1 column 7053 (char 7052)
```

Usage:3,438 prompt +3,016 completion =6,454 tokens; output allowance8,192. The response is below
the cap, so this is **BLK-014, not BLK-013**. The original strict schema, prompt and generation
settings were transmitted. The argument string retained by the adapter agrees with the saved
provider response; no validation-copy transformation applies to malformed JSON. Argument SHA256:
`3e3db33fd88fe5adfdb736d8c86d0b283eb6cdebcb4cadf2376ff769dc9d47f8`.

Strict rejection retained the original evolution failure/fallback. The final note keeps its generated
metadata and no new links; the counter does not increment for this failed decision. The phase
durably halted without semantic retry or JSON repair. Its receipt reports **Incomplete**,
`usable_for_next_phase=false`, `recoverable_length_failure=false`. Incomplete takes precedence
over inherited degradation; it is not a completed degraded baseline.

The immediate cause is invalid provider function-argument JSON. Why provider generation/strict
enforcement produced it is unknown. A larger cap is not supported as a remedy for this normal,
below-cap completion. Preserve the exact failure instead of weakening validation.

An independent offline audit passes the exact saved HTTP response through the real SDK/adapter
using one MockTransport request, matching the original request body. It reproduces the same
JSONDecodeError/offset; the original author evolution catch preserves the note, existing memories
and counter. No real network call, semantic retry, JSON repair or source change is involved.

## Spending and service verification

| Scope | Logical calls | Physical attempts | Settled USD | Reserved unknown USD | Conservative exposure USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent |454 |455 |0.720433 |0.324404 |1.044837 |
| Child |678 |678 |1.325173 |0 |1.325173 |
| Run2 total |1,132 |1,133 |2.045606 |0.324404 |2.370010 |

All678 child attempts are settled; the failed response itself costsUSD0.004651 conservatively.
Original attempt454 stays unknown, usage null, charge/reservationUSD0.324404. No old row is released
or reset and no new unknown is recorded. These are conservative ledger costs, not provider-invoice
reconciliation. The originalUSD5 cell has **USD2.629990** remaining. Run2's USD42 execution pool has
USD39.629990 unspent, with the separateUSD8 contingency protected. Run1 remainsUSD8.530133.

Rotated credentials authenticate/read existing traces in the intended project. Administration inventory
shows the replacement key and absence of the original pair, without testing or displaying the old
credential. The launcher uses only current `.env` values; BLK-023 remains Resolved.

All **2,048 child observations across483 traces** are verified against actual Langfuse readback,
including678 generations,676 applied-action observations,339 turn parents,349 inherited/new
integer-string deviation notices, checkpoint/lifecycle records and the provider failure/fallback.
The first final readback was incomplete during ingestion; the subsequent strict readback verified
the entire exact set. Both attempts are preserved. No evidence was dropped or verifier relaxed.
There are zero primary scores/Experiment results because no QA completed. The offline real-runner
GateB separately verified both saved-result Experiments (eight fixture items/112 scores), with no
paid model calls; those engineering scores must not be reported as primary results.

The read-only billing UI reports5,166 current-period units (hourly lag),9,457 daily-bucket units and
USD0 draft usage charge, below100K included units. These counters have different scopes; do not add
them. No incremental Langfuse overage or subscription change was committed. The user's existing
Core subscription is separate from incremental campaign usage.

## Cost-only forecast and next boundary

The unchanged forecast function credits1132 completed logical operations once. It projects
**USD36.887647 remaining / USD39.257657 total provider exposure**, including the retained unknown.
There is no completed Run2 cell, so remaining costs still use the documented Run1 stage proxies;
this is a point estimate, not an upper bound. No population or setting was selected using accuracy.
Finishing this cell would require **109 turns plus158 questions =534 logical calls**, with a
proxy point costUSD1.460438, below theUSD2.629990 cell remainder.

Carrying forward the preceding normal-service forecastUSD1.67464–2.74144 gives a conditional
provider/service/protected-reserve point ofUSD48.932297–49.999097. It excludes any new recovery
engineering ingestion, additional failures, other project traffic, tax and billing rounding. The
upper end leaves essentially no headroom; it is not evidence that the full campaign is safely
funded. No additional service allocation or contingency use is inferred.

Next unprocessed turn isD24:13. The reviewed financial-lineage implementation supports only the
consumed227-note checkpoint, not a child of this child. Automatic BLK-013 recovery cannot apply to
the current malformed, normally finished response. **Further work requires a separate decision**:
recommended scope is minimal exact566-note checkpoint engineering/review, preserving this failed
decision, counter564, stale index, both ancestors and the full unknown reservation, followed by a
separately authorized bounded paid continuation if affordable. Do not restart, repair JSON,
regenerate historical decisions, increase the cap or execute the next ablation under this grant.

## Evidence inventory

Local artifacts are intentionally ignored by Git. Paths are relative to the repository root.

- Immutable parent: `artifacts/run2/runs/run2-full-conv-44-r0-p0/`.
- Sealed child: `artifacts/run2/runs/run2-full-conv-44-r0-p1/`: `phase.json`, `approval.json`,
  `checkpoint.json`, `events.jsonl`, `partial-memory.json`, `failure-trace.json`, `trace-capture.json`,
  exact Langfuse readbacks and `observability.json`.
- Original cumulative Run2 ledger: `artifacts/run2/budget.sqlite`.
- Consumed approval: `artifacts/run2/observed-recovery/approved-child.json`.
- GateB: `artifacts/run2/observed-recovery/gate-b/265094c0a6484105b3922862633b7063fd5a4f917663349fdf720658e0864fbf/`.
- Release/audit/forecast evidence under `artifacts/run2-observed-recovery/`:
  `release-verification.json`, `full-suite-bounded.log`, `archive-equivalence.json`,
  `activation-verification.json`, `outcome-preservation.json`, `outcome-cost-only-forecast.json`,
  `outcome-billing-metadata.json`, `paid-child-execution.log` and independent outcome audits.

Post-run preservation verifies all557 Run1 files and393 pre-existing non-ledger Run2/preparation
files unchanged. The only permitted old-file change is the Run2 ledger's approved append; its
original financial prefix and unknown reservation are independently checked. Raw failure evidence,
snapshots and both phases remain immutable.
