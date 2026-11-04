# Run2 Full conv-44 — verified reporting recovery

4 November2026. **The675-turn/158-question Full conv-44 lineage is now fully verified locally and in Langfuse and classified Degraded.** The reporting-only acceptance supplement completes the lineage; the original p0/p1/p2 Incomplete receipts, failed import claim/halt, ledgers and paid frontier remain unchanged. No next paid cell is authorized.

## Engineering and release

[Implementation PR#33](https://github.com/alistairkung/A-mem-reproducibility/pull/33) merged normally as `513b44e11ff846035add3b5aefe32043cbd960a6`. Reviewed source: `35f89f7d72a1786560d35e8f42dd7eabb3500f85`. Independent Standards and Spec reviews pass separately, with no outstanding findings. Initial findings and superseded passes are preserved. Full offline suite: **809 passed, 17 warnings, 92 subtests passed in 1282.58s (0:21:22)**; independent focused reporting/Langfuse/sequential checks:60 passed.

Post-ingestion read-only correction: `f90d775f9f513cecc62d907f127fa7c0d295e7fe`, independently Standards/Spec PASS and59 focused tests passed. Initial item reads caught indexing lag (4,130 scores), then all4,494 were visible. The score endpoint’s local-Experiment filter returned0 despite exact explicit-ID/trace reads. Bounded item-trace queries corrected verification; the separate read-only entry requires the consumed claim and passes `client=None`. No second import, model call or modified approval occurred. The original19-pin approval remains immutable and consumed.

The recovery wrapper lives outside the scientific source inventory. Original exporter, author code and all scientific support bytes remain unchanged: fingerprint `fc5fc67e0a0276948b1c8ac38ec4bbd0fab2fa09b44badc4c2a517cee3503fa7`. It forwards the original saved-result task/evaluator callbacks, preserving predictions, references, all metrics, scorer/configuration/source/output-cap bindings and original QA traces.

## BLK-024 resolution and actual readback

Recovery import: `run2-full-conv-44-reporting-recovery-20261104-v1`. One durable exclusive claim precedes ingestion; subsequent invocations resume reads only. Original import IDs `7adb9c90792cb287`/`622ed0b34679ea04` and every failure record remain intact. Read-only inspection found0 original Experiments/items and0 experiment-scoped scores, but **4,494 original orphan scores across316 traces** (2,247 per view). Their saved policy/name/value multiset matches exactly. They remain preserved and excluded from canonical recovery; no record was deleted or reused.

Actual SDK offline reproduction:632 spans/316 items/4,494 exact policy-question-metric-value callbacks; default maximum155,912,209B produces two batches above64MiB. Sixteen-span batching produces40 batches, maximum9,075,061B below the stricter32MiB safety ceiling. All original records/trace mappings match; network/model calls zero.

| Scoring view | Recovery Experiment | Items | Scores |
| --- | --- | ---: | ---: |
| `author-corrected-v1` | [0bb2cccf10432f3d](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=0bb2cccf10432f3d) |158 |2,247 |
| `author-legacy-c5-v1` | [b1402704f1fb57e3](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b1402704f1fb57e3) |158 |2,247 |

Actual Langfuse readback verifies **316 question/view items,4,494 scores and316 distinct reporting traces**. Exact checks include Experiment/run/item/question identities, all inputs/predictions/references/original records, every metric name/value, exact score observation subjects and all158 original paid QA trace associations. Original partial-write traces and canonical recovery traces are disjoint. Complete cursor pagination is required; flush/authentication alone is not acceptance.

Fresh runtime readback verifies p0:1,278 observations/230 traces; p1:2,048/483; p2:1,771/623. Total **5,097 observations/1,336 traces**. Original strict input/output/settings/usage readback proofs and every referenced snapshot hash also verify. Reporting traces/timing do not represent original inference.

## Verified unchanged collection and metrics

All675 original turn identities/content/order, including the original image-caption loader,158 original raw QA records/indices, both views and all saved outputs verify. Final675-note/counter673 memory and675×384 finite float32 stale index/cache completion hashes match. Original malformed decision/fallback,429 cumulative D3a deviations and all inherited failure records remain retained; no prediction generation, metric computation or model execution is repeated.

Percentages, using unchanged author aggregation. Categories1–4 have identical corrected/historical values.

| Category | Questions | Corrected F1 | Corrected BLEU-1 | Historical F1 | Historical BLEU-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 |30 |35.26 |28.02 |35.26 |28.02 |
| 2 |24 |40.64 |37.70 |40.64 |37.70 |
| 3 |7 |9.53 |4.02 |9.53 |4.02 |
| 4 |62 |61.30 |54.00 |61.30 |54.00 |
| 5 |35 |75.46 |72.02 |21.25 |17.25 |
| Overall |158 |54.06 |48.37 |42.05 |36.24 |

Category5 adversarial correctness is separately **27/35 (77.14%)** in both views. Historical adversarial overlap is a reproduction view, not factual-quality evidence. This is a released-data/DeepSeek/k=10 reconstruction, not an absolute-score replication of the published GPT-4o-mini experiment.

## Spending and next-phase decision

Conservative Run2 exposure remains **USD4.166489**:USD3.842085 settled +unknown454/fullUSD0.324404 reservation. Parent/child/p2 exposures areUSD1.044837/1.325173/1.796479, each counted once across1,666 logical/1,667 physical attempts. Original cell remainderUSD0.833511; plannedUSD42 pool remainderUSD37.833511; protectedUSD8 untouched. Run1USD8.530133 and all1,741 historical/scientific file hashes remain unchanged. Recovery model spending is zero. Post-import billing refresh shows22,320 daily-bucket units (exactly+5,442 reporting units),13,174 hourly-lagged period units andUSD0 draft usage charge; these different-scope counters are never added. Included capacity covers reporting, with no service upgrade/overage or new budget authority. The draft is not a final invoice.

[The refreshed affordability analysis](run2-ablation-affordability-20261104.md) separates nine ablations (USD36.176358) from two missing Full baselines (USD7.892297). Original12-cell provider pointUSD48.235144 already exceedsUSD42 before projected normal serviceUSD2.526080–3.485360. BLK-009 remains Open.

Proposed balanced conv-44/49 ×four-condition scope: provider pointUSD31.819960, normal serviceUSD0 projected; combined20% growth/retry/unknown/checkpoint stress totalsUSD49.330258 including protectedUSD8. Per-cellUSD5 limits still bind. A one-conversation four-arm scope has greater campaign headroom; the Full/Neither/Linking-only minimum is a narrower published-ablation reconstruction. All subset/order/budget/paid-phase decisions remain explicit future authorizations; no manifest is changed or remaining cell executed. Recommend the balanced two-conversation scope, with the next fresh Full conv-49 phase considered only after that decision and refreshed phase-bound checks.

## Immutable evidence inventory and debug diary

All paths below are local evidence under `artifacts/run2/reporting-recovery/`:

- `preservation-before.json`:1,741 historical/scientific file hashes; the launcher and final verifier check all of them before/after reporting.
- `original-inspection/`, `original-inspection.log`: original partial-write investigation; complete raw score subjects remain preserved.
- `offline-payload-proof.json` and payload logs: exact-data SDK serialization and every policy/question/metric/value comparison.
- `standards-review.json`, `spec-review.json`, initial/previous reports, focused/full suite logs: independent review/fix/retest history.
- `historical-fixture/` uses the unchanged transport-stop ledger; `sequential-fixture/manifest.json` explicitly identifies a derived test-only p0/p1 projection, with every retained original row checked. Neither fixture is authoritative spending/phase evidence.
- `runtime-current/proof.json` and raw reads: fresh runtime identities and unchanged original strict proof hashes.
- `approved-reporting.json`:19 source/dependency/test/evidence pins, reviewed/merged commits, one import, zero model calls and zero new service fee allocation.
- Recovery subdirectory: `pre-ingestion-inventory.json`, `original-score-isolation.json`, `recovery-claim.json`, `sdk-returned.json` and hashed raw Experiment/item/score readbacks.
- `readback-standards-review.json`, `readback-spec-review.json`, `read-only-reconciliation.log`, `score-filter-diagnostic/` and `billing-after-import.json`: post-ingestion correction/review, actual full readback and UI billing evidence.
- `local-completion-check.json`, `verify-completion.py`, `lineage-completion.json`: independent local identities/aggregate/state/accounting checks and separate Degraded acceptance supplement.
- `forecast.json`, calculator/log and independent forecast reviews: measured cost-only scenarios; no paid approval.

Acceptance supplement SHA256: `642414039f25532f046c974a3d38e30ed77deafa0eedd9714f63a7b652f5fc3c`. Reporting proof SHA256: `da60f8a7a9203c67d109c242901b3a26bd70221112487db5daac39125b238ec0`. Authoritative ledger SHA256: `541ef873e38cc921abedc2d1898bfb9ebcb82da496ff74a55ccbd67a028343c3`.

Debug diary: initial offline reviews caught incomplete source pins, missing original configuration metadata, and insufficient score-observation/item identity checks; all were fixed and independently re-reviewed. Complete-suite attempts also exposed historical tests reading the later multi-phase ledger while copying only older phases. Preserve those failed/interrupted logs; final tests use explicitly selected historical/derived evidence roots, unchanged assertions and unchanged production gates. The forecast review corrected per-condition action-unit bounds and clarified that smaller scope improves campaign headroom rather than individual cell caps. No scientific rule was relaxed.

BLK-024 is **Resolved** at the reporting batch/isolation/readback boundary. BLK-014 and BLK-022 remain Mitigated with their original scientific/financial limitations. The completed lineage is **Degraded, never Clean**; the original Incomplete phase seal/halt/frontier remains immutable.
