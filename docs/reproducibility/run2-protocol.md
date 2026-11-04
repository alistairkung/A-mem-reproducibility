# Run 2 — fully observed controlled campaign

Current verified baseline: **Full conv-44 is complete Degraded through the separate4 November
reporting acceptance supplement**. [Completion and readback](run2-conv44-reporting-complete-20261104.md).
BLK-024 is Resolved; original Incomplete phase receipts/failed import/ledger frontier stay immutable.
BLK-009 remains Open; [cost-only alternatives](run2-ablation-affordability-20261104.md) require an
explicit scope/budget/paid decision. No remaining cell or contingency use is authorized.

The following stopping record is historical and preserved:

Current stop: **all675 Full conv-44 memory turns and158 QA are locally verified, but p2 is sealed
Incomplete on BLK-024**. Runtime1,771 observations/623 traces verify; both full-cell Experiment
exports exceed the local64MiB OTLP batch guard and visibility fails. The original claim/IDs/halt
remain immutable. Read [the verified outcome](run2-conv44-collected-export-blocked-20261103.md).

PR#31 merged `66d3ffa` after784 tests/92 subtests, exact reference/full-candidate archive equivalence,
real-runner cloud GateB and independent reviews. The narrow original evolution fallback is verified;
provider reliability is not repaired. Sole566-note p2 grant is consumed:534 calls/USD1.796479,
no new malformed output/retry/unknown, total Run2USD4.166489 includingUSD0.324404 unknown/full-reserved.
BLK-014 is Mitigated, BLK-022 remains Mitigated and BLK-023 Resolved. BLK-024 and renewed BLK-009
are Open. Measured Full-stage sensitivity projectsUSD48.235144 provider total aboveUSD42 usable,
before service fees; protectedUSD8 is untouched. No further paid cell/recovery, automatic import,
frontier release, scope/settings change or reserve use is authorized. Reporting-only reconciliation
and acceptance require a separate decision. The scientific profile below remains frozen.

Historical freeze: PR#25 `c7cd12b`, PR#26 `207eac0`; original715-test/92-subtest release and GateA/B
passed. P0 stopped on BLK-022 at227 notes; p1 stopped on BLK-014 at566 notes. Preserve both sealed
phases. [Historical first stop](run2-first-cell-incomplete-20261103.md),
[p1 outcome](run2-conv44-recovery-incomplete-20261103.md),
[essential observation policy](run2-observation-policy.md),
[original-fallback design](run2-author-fallback-recovery.md).
Authority: [user grant](decisions.md#authorization--run-2-fully-observed-campaign),
[issue#24](https://github.com/alistairkung/A-mem-reproducibility/issues/24).

## Scientific identity and Run 1 separation

Run2 is a new12-cell primary campaign, one fresh build per cell, not a continuation/relabeling of
Run1. Preserve all557 prior artifact files, old cache/checkpoint lineages, original labels and
`artifacts/study-budget.sqlite` (USD8.530133/4,292 requests) unchanged. Run1 completed conv-49/50 and
incomplete conv-44 remain exploratory engineering results and debugging evidence; no primary score
or cost credit is carried into Run2. Reference them only as separate exploratory observations.
New scientific artifacts, ledger, approvals, runs and caches live under `artifacts/run2/`.

Preserve author revision `f9a173d`, `test_advanced.py`, `memory_layer.py`, original prompts/schemas/
parsers and scorer. Dataset SHA256:
`79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`.
Reuse the compact frozen fallback population selection/indices from `manifests/fallback.json`,
not Run1 saved predictions or memories. All selected turns/questions and original ordering remain.

| Conversation | Turns | Questions |
| --- | ---: | ---: |
| conv-49 |509 |196 |
| conv-50 |568 |204 |
| conv-44 |675 |158 |
| Per condition |1,752 |558 |

| Condition | Strengthening | Neighbour updates |
| --- | --- | --- |
| Neither |Off |Off |
| Linking only |On |Off |
| Evolution only |Off |On |
| Full |On |On |

Full uses the frozen author factory; ablations use the T7 replay-verified action gates. Initial note
metadata and shared evolution decisions remain enabled everywhere. Strengthening includes directed
links and new-note tag updates; linking-only does not isolate graph edges from metadata enrichment.
Keep decision-driven counters, positive decisions with suppressed actions, consolidation every100,
five construction neighbours, k=10, duplicates/context expansion and intentionally stale embeddings.

## Generation policy selected from Gate A

Freeze `run2-shared-decision-8192-v1`: shared decision8,192 output tokens; metadata,
query-keyword and answer stages1,000. This policy applies identically across all12 cells.
Run1's default config/replay stays4,000. See [evidence and limitations](run2-output-limit-investigation.md).

Keep `deepseek-flash`, documented DeepSeek-V4.1-Flash-1017,
`https://api.deepseek.com/beta/chat/completions`, explicit thinking disabled, non-streaming serial
execution, original forced strict functions and `canonical-index-strings-v1`. The original argument
string reaches A-MEM unchanged; retain every validation-copy audit. Temperatures remain0.7 for
metadata/decision/query/categories1–4 answers and0.5 for category5 answers. Transport retains120-second
timeout and at most two SDK retries; no semantic retry, second generation or JSON repair.
Pin/record returned model and provider fingerprint; a model-identity change stops the controlled run.

The cap change is the sole new generation-policy deviation, not retrospective repair. Provider
documentation and offline serialization verify support; they cannot guarantee hosted completion.
Local tokenizer estimates remain labelled estimates; API usage drives conservative costs.

## Mandatory observability gate

Use actual `run_manifest`, original author/action factories and existing scoring with offline LLM
responses. The same observer path must produce real visible Langfuse observations in the configured
project. Read back with the current Langfuse CLI/API, checking exact inputs/outputs, stage IDs,
campaign/condition/conversation/turn/question/repetition, usage/settings, errors/fallbacks and recovery
provenance. Authentication, SDK flush or a standalone trace is not evidence of this gate.

Capture metadata/shared-decision/query/answer generations; strengthening/neighbor-update action
inputs/outputs; retrieval/context/counts; predictions/references/scores; failures and D3a deviations.
Use per-turn/per-question trace parents and stable campaign/cell/phase identities. Preserve authoritative
local journals. Tracing exceptions preserve original outputs and complete the current atomic operation;
check health at the next safe turn/question boundary and halt further paid work if health failed.
Before recovery/next-cell release, verify actual visible observations, not only observer health.

Import both saved scoring views into uniquely identified Langfuse Experiments without calling a model
or rerunning predictions. Distinguish import timing from original inference latency/cost. Prove traced
and untraced deterministic memory/index/context/prediction/scoring equivalence, zero extra generations,
captured simulated output exhaustion and unchanged results under tracing failures. Use the tested
Langfuse5.1.0 SDK and modern observations/experiments APIs; preserve dependency locks.

## Bounded cells and sequential recovery

Freeze the execution order before primary quality inspection: Full conv-44, conv-49, conv-50; then
Neither conv-49/50/44; Linking-only conv-49/50/44; Evolution-only conv-49/50/44. Starting Full conv-44
tests the known output-growth workload, not a performance-selected subset. No population redraw,
question removal or generation/retrieval tuning follows results.

There are18,480 planned logical calls and at most55,440 physical attempts across12 cells. Each cell
has an original **USD5 maximum allocation**, pooled under the **USD42 campaign usable ceiling**;
these caps are not additive authority. ProtectUSD8 insideUSD50; no contingency use/top-up is approved.
Use a separate durable ledger, pre-transmission reservations and terminal admission/settlement
guards. Unknown charges retain their full reservation and cannot support an accepted recovery.
Actual usage/retries/failures count once. No ledger reset, phase restart, repeated root build or paid
exploratory probe is authorized by this protocol.

Only a verified shared-decision BLK-013 `length` exhaustion may trigger an automatic continuation.
The failed note keeps the original author fallback, counter and no silently repaired decision.
Restore exact ordered notes/metadata/links/outcomes, stale float32 corpus/index/map and evolution
state; resume at the next original turn in the same cell/condition. Each child binds all ancestors,
immutable inventories/approval/config/data/source/provider policy and original cell allocation.
Preserve original failure/deviation origins. One-shot parent ownership and cumulative cell logical,
attempt and cost quotas prohibit reset/replay/forks. Every continuation must advance the original
turn prefix; finite conversation length bounds the sequence. Completed recovered cells are Degraded.

Test at least two successive simulated failures/continuations before a paid cell, including stale
index/counter/consolidation and original-fallback equivalence, unchanged prefix, quota carry and
rejection of foreign conditions, missing/changed ancestry, duplicate claims or unknown usage.
Other invalid provider output, exhausted transport retries, provenance/scientific inconsistency,
tracing failure or spending-control failure stops instead of auto-recovering.

## Completion, comparison and affordability

One cell at a time: verify its exact turn/question identities, raw responses, state/index, both
author scoring views, deviation/fallback history, settled ledger and visible Langfuse observations/
saved-result experiment import. Publish a verified immutable receipt before releasing the next cell.
Retain partial artifacts/costs on failure. Incomplete takes precedence over Degraded.

Corrected per-category F1/BLEU-1 are primary; report category5 `adversarial_correct` separately.
Historical category5 scoring uses the identical predictions/references/IDs as a labelled reproduction
view. Keep other existing metrics diagnostic. No new grader/evaluator or model judge is introduced.
Report all558 questions per completed condition, action/suppression counts, failures and original
API latency/cost. Compare reconstructed neither/linking/full to Table3 with cross-model/population/
retrieval/scoring caveats; evolution-only is novel. One build/cell supports descriptive comparisons,
not stochastic confidence claims. Never interpret higher historical adversarial overlap as quality.

Before each next cell, reconcile Run2 incurred/reserved charges and cost-only remaining forecasts.
Initial measured point estimate: USD38.764612 execution +USD8 reserve =USD46.764612 (summing per-cell
rounded microUSD estimates adds three microUSD to GateA's combined estimate). It is not an
upper bound;10% execution growth exceedsUSD42. Update stage means as completed conditions become
available. Stop for a material financial decision if the balanced remaining campaign cannot fit;
preserve the fixed population/settings and do not silently spend contingency. No next-cell release
with missing accounting, observability or final receipt. Run1 costs/results remain separate throughout.

## Freeze checklist

- [x] Current official output constraints, actual SDK path and Run1 size evidence independently reviewed.
- [x]8,192 recommendation and Run1 preservation recorded; GateA PR#25 merged.
- [x] Instrumented real-runner fixture visible and independently fetched/audited in Langfuse.
- [x] Saved question-level results visible in Langfuse Experiments with unique scoring identities.
- [x] Instrumented/uninstrumented replay, trace-failure and two successive checkpoint regressions pass.
- [x] Full offline suite, actual candidate replay and independent Standards/Spec reviews pass.
- [x] Final source/config/population/assets/gate receipts and affordable final campaign plan are frozen.
- [ ] Run all12 bounded cells only after all prior boxes pass; reconcile each before the next.

## Frozen evidence and execution

Campaign: `amem-run2-20261103-v1`. Source fingerprint:
`184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe`.
Reviewed support-source commit: `c96daa296544e2396db2b46477a0af50bc88712c`.
The committed one-cell launch script is independently pinned in the approval to SHA256
`b86e7471d76b73ad81564911f166dd92806658ee8c9efaa3a692b648b3ad37a1`.
Source fingerprints cover the author/support modules and configurations; the explicit extra script
hash covers the launch boundary. Run from the repository root.

Local immutable `artifacts/run2/frozen/manifest.json` pins the source, compact population selection,
generation config, runtime assets/preflight, both gates, initial cost forecast, launch script and
review/test evidence. Its SHA256 is
`5ebd46fd99635d1f74f16935648856de1e5e3c0dc2d6c35ae8b8fef581a7c1c6`.
`campaign-plan-final.json` is unapproved preparation. After successful final audit/merge, copy it
to `campaign-approval.json`, changing only authorization metadata under the user's existing grant.
The earlier `campaign-plan.json` is retained as an unapproved draft with the superseded launch-script
hash; it must not be activated. Every actual segment writes a new immutable single-use approval.

Evidence: `artifacts/run2/offline/final-full-suite-20261103.txt` records715 tests/92 subtests and17
expected warnings. `archive-equivalence.json` links the exact568-note/204-Q original and candidate
receipts; all1,544 recorded requests, every insertion/index/context/prediction/score and376 preserved
failure records match, with only the implementation label differing. All557 Run1 hashes still match.
The replay migration is explicit and restricted to reviewed support files; default invocation remains
fail-closed, and original author/schema/scorer/assets/config pins and fixed oracles are unchanged.

```sh
.venv/bin/pytest -q
.venv/bin/python -m amem_repro.replay_baseline --assets artifacts/assets \
  --output /tmp/run2-reference-new \
  --support-reference c96daa296544e2396db2b46477a0af50bc88712c
.venv/bin/python -m amem_repro.replay_baseline --assets artifacts/assets \
  --output /tmp/run2-candidate-new --full-mode-candidate \
  --support-reference c96daa296544e2396db2b46477a0af50bc88712c
```

Read [GateB's actual-runner proof](run2-observability-verification.md). The paid command below uses
the frozen approval/preflight, privately loads only required credentials, verifies all Run1 hashes,
reforecasts costs and enforces the reviewed phase controls. It executes one cell and only verified
BLK-013 continuations of that cell. It cannot reuse a consumed run identity. Local outputs remain
under `artifacts/run2/runs/`, with the separate `budget.sqlite`, caches and post-cell forecasts.

```sh
.venv/bin/python scripts/run2-cell.py --cell-index 0
```

| Indices | Condition | Conversation order |
| --- | --- | --- |
|0,1,2 |Full |conv-44, conv-49, conv-50 |
|3,4,5 |Neither |conv-49, conv-50, conv-44 |
|6,7,8 |Linking only |conv-49, conv-50, conv-44 |
|9,10,11 |Evolution only |conv-49, conv-50, conv-44 |

Proceed to each next index only after the preceding sealed receipt, complete question identities,
both scoring views, settled charges and real Langfuse readback verify, and the new cost-only forecast
still fitsUSD42. Approval cannot override a failed gate or authorize contingency use.
