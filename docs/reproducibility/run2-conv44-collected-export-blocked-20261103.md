# Run2 conv-44 — complete local collection, Experiment export blocked

3 November2026. **All675 memory turns and158 questions are collected and locally verified. The
sealed phase is Incomplete because Langfuse Experiments failed its visibility gate (BLK-024).**
Its halt/receipt remain unchanged; do not label this a completed Degraded cell or release another
paid cell. The author runner completed with inherited Degraded status before postprocessing failed;
final persisted `summary.json` and `phase.json` are Incomplete. No model request, paid restart or
re-import occurred after that failure.

## Implementation and original fallback

[PR#31](https://github.com/alistairkung/A-mem-reproducibility/pull/31) merged as
`66d3ffa6af82560d50658a9077439becc01681ba`. Reviewed source commit:
`7921b15cccb7b6517e2b2e77a35576cdb04285eb`; fingerprint:
`fc5fc67e0a0276948b1c8ac38ec4bbd0fab2fa09b44badc4c2a517cee3503fa7`.

The author handles the actual malformed shared decision as a per-turn failure, retaining the new
note and metadata without evolution/counter increment. Our previous adapter halt was unnecessarily
fatal for that verified case. The approved phase-bound verifier preserves strict rejection and the
original error/catch; it blocks further transmission until complete state, stale-index, counter,
settlement, journal and tracing checks pass. No JSON repair, semantic retry or changed parser input.
Other schema/stage/transport/persistence/accounting faults remain terminal. See
[the precise eligibility and limits](run2-author-fallback-recovery.md).

Release checks: **784 tests/92 subtests passed**,17 expected warnings,1164.19s; independent Standards
and Spec reviews clear. Original/full-candidate archive replays match1,544 requests/568 notes/204QA,
including state/index/context/predictions/both scoring views, differing only by implementation label.
Current-source real-runner cloud GateB and merged-source network-disabled runtime preflight pass.
The first full suite's783 passes/one obsolete negative-test message assertion and subsequent corrected
four-case/full-suite passes remain preserved; no production change was made to satisfy that assertion.

## One authorized continuation and integrity

| Phase | New memory turns | QA | Logical | Physical | Conservative USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `run2-full-conv-44-r0-p0` |227 |0 |454 |455 |1.044837 |
| `run2-full-conv-44-r0-p1` |339 |0 |678 |678 |1.325173 |
| `run2-full-conv-44-r0-p2` |109 |158 |534 |534 |1.796479 |
| Lineage |675 |158 |1,666 |1,667 |4.166489 |

P2 approval `94021561-b115-4e79-83db-de93e3464c4f` is consumed. Its additional capUSD2.629990,
534logical/1,602physical limits and originalUSD5 cell were respected. It restored exactly566 notes,
counter564 and the stale566×384 float32 index, resumingD24:13 and endingD28:18. No historical
memory/decision or failed response was regenerated. Final counter673; the original599→600
consolidation occurs atD26:10. Final675×384 index/corpus/map and all ordered outcomes verify.

Independent audits verify prefix identities/content/timestamps/order and inherited outcomes, all
109 new turns,158 original question identities/order/references and seeded category5 prompts.
Offline author replay of the109 new turns matches notes/actions/corpus/counter using recorded
neighbors/saved vectors; this is not a claim to re-encode every historical intermediate embedding.
All352 cumulative parent failure records remain inherited once. Both parent inventories,557Run1
files and164 pre-existing non-ledger Run2 files remain unchanged. The final memory-build cache is
complete and verified; it does not override the outer experiment's Incomplete release gate.

P2 has **zero new rejected generations, semantic retries, transport retries or unknown charges**.
It records80 approved D3a integer-string deviations/319 validation-copy transformations; original
HTTP/SDK/parser argument strings remain unchanged. Total inherited+new D3a counts429/1,694.
The historical malformed decision and transport/unknown-charge incident remain preserved. BLK-014
is Mitigated at the wrapper/verified-fallback boundary; provider strict-output reliability is not repaired.

## Verified local quality results

These are the unchanged authors' aggregate means, reported as percentages. All158 predictions and
references are retained; no question was dropped or retried based on score. No metric failures were
reported. These local scores do not establish successful Langfuse Experiment visibility.

| Category | Questions | Corrected F1 | Corrected BLEU-1 |
| --- | ---: | ---: | ---: |
|1 |30 |35.26 |28.02 |
|2 |24 |40.64 |37.70 |
|3 |7 |9.53 |4.02 |
|4 |62 |61.30 |54.00 |
|5 |35 |75.46 |72.02 |
| Overall |158 |54.06 |48.37 |

Category5 `adversarial_correct`: **27/35 (77.14%)**. Historical scoring uses identical saved
predictions/IDs/raw reference data, with the frozen policy-specific category5 reference selection: overallF1 **42.05%**, BLEU-1 **36.24%**; category5F1 **21.25%**, BLEU-1
**17.25%**. Categories1–4 and adversarial correctness are unchanged across scoring views. Preserve
all other metrics as diagnostics. Historical overlap is a reproduction view, not factual-quality evidence.
This remains a DeepSeek/released-dataset/subset reproduction; absolute scores are not directly
comparable with the paper's GPT-4o-mini experiment.

## Langfuse: runtime verified, Experiments not verified

The final strict readback verifies **1,771 runtime observations across623 traces**, zero duplicate
original Score objects. Five initial bulk reads timed out with no CLI JSON; the sixth completed and
all expected inputs/outputs/settings/usage/metadata/errors matched. This is separate from the
subsequent Experiment failure. The CLI diagnostic confirms timeout/empty stdout, not JSON truncation.

The single saved-result import allocated two SDK Experiment IDs:
`author-corrected-v1`: `7adb9c90792cb287`; `author-legacy-c5-v1`: `622ed0b34679ea04`.
All six bounded Experiment and item readbacks returnedHTTP200 with empty data. The exporter logged
**two local dropped OTLP batches**,155,623,154 and155,624,770 bytes, above67,108,864 bytes (64MiB).
The installed exporter checks serialized size before HTTP transmission. The existing import claim,
IDs, readbacks, warning lines and phase receipt are immutable. Empty readbacks/local batch drops
do not prove absence of every score or partial remote write; automatic re-import is prohibited.

An offline SDK5.1.0 reproduction using the exact saved views confirms the narrow batch-only remedy:

| Offline SDK setting | Spans / item roots / scores | Largest individual span | Largest batch | Batches above64MiB |
| --- | --- | ---: | ---: | ---: |
| Default |632 /316 /4,494 |701,572B |155,621,489B |2 |
| `flush_at=16` |632 /316 /4,494 |701,560B |9,060,149B |0 |

All original-record metadata and saved values remain exact; network/model calls are zero. This is
an offline proposal, not an implemented production change or successful cloud re-import. It retains
the frozen observation policy and size guard. Raising the size guard, dropping metadata/scores,
re-running predictions, deleting failed imports, clearing the halt or overwriting the claim is rejected.
A reporting-only recovery needs a separate explicit decision to reconcile possible partial writes,
authorize one controlled import identity and independently verify it. No new LLM request is needed.
Any acceptance supplement must reference the original failed phase without rewriting its status/seal;
financial/frontier release must remain closed until explicitly resolved.

## Spending and remaining-study forecast

Known settled Run2 cost **USD3.842085** plus original unknown454/full reserved **USD0.324404** gives
**USD4.166489** exposure. Unknown status/null usage/full reservation are unchanged. Run1 remains
separate/immutable atUSD8.530133. Remaining original cell **USD0.833511**; Run2USD42 execution pool
**USD37.833511** remains, withUSD8 protected. No contingency or extra model/service allocation used.
Read-only Core billing shows8,657 lagged period units/16,878 daily-bucket units andUSD0 draft usage
charge; these different-scope counters must not be added or treated as a final invoice. The user's
existingUSD29 subscription is separate from incremental study fees.

The unchanged official forecast retains the Incomplete frontier and therefore still uses Run1 stage
proxies:USD39.593698 provider total plusUSD8 reserve. That is not an adequate new affordability
assurance after this complete model collection. A separate cost-only sensitivity uses all actual
Full-stage counts/charges (675metadata/675decisions/158queries/158answers, including the retained
unknown), without promoting the cell: **USD48.235144 projected provider total**, including
USD44.068655 for the remaining11 cells. This exceedsUSD42 usable by **USD6.235144**; adding reserve
already reachesUSD56.235144 before service fees. Other-condition costs are unmeasured and may
differ. Neither forecast is an upper bound. No cases, population or settings were selected by accuracy.

**First paired ablation is blocked by BLK-024 and renewed BLK-009.** The local Full reference is
collected, but the fully observed acceptance gate and a cost-only decision for the remaining balanced
experiment are unresolved. Keep the frozen population/design; do not automatically spend, reduce
scope, change generation/retrieval, reuse Run1 or launch another cell.

## Evidence inventory and remaining decision

- Sealed phases/cache/ledger: `artifacts/run2/runs/run2-full-conv-44-r0-p{0,1,2}/`,
  `artifacts/run2/cache/`, `artifacts/run2/budget.sqlite`.
- P2 final `phase.json`, `summary.json`, `events.jsonl`, `scoring-views.json`, `trace-capture.json`,
  observation proof/readbacks, `langfuse-import-claim.json`, `langfuse-imported.json` and all failed
  readbacks stay unchanged. Phase halt: `run2_experiments_not_verified`; usablefalse.
- `artifacts/run2-fallback-recovery/`: approvals/activation, full-suite logs, archive proofs,
  `memory-build-audit.json`, `outcome-{spec,standards}-audit.json`, `local-quality-summary.json`,
  `experiment-drop-evidence.json`, `cli-readback-diagnostic.json`, `outcome-billing-metadata.json`,
  `measured-stage-cost-sensitivity.json` and `outcome-forecast-incomplete-frontier.json`.
- `export-characterization/characterize.py`, `results.json`, `run.log`: exact offline payload test.

Stop at the material reporting/budget gates. Proposed next decision: approve a reporting-only repair
with reviewed16-span batches, partial-write reconciliation and one explicit import identity, plus a
verification/acceptance supplement preserving the original Incomplete receipt/halt. Any frontier or
next paid-cell authorization is separate. No additional model execution is required for reporting repair.
