# Run 2 — fully observed controlled campaign

Status: engineering draft; GateA reviewed/merged in PR#25 (`c7cd12b`). GateB live visibility, complete
offline/replay checks, independent reviews and final current-source preflight remain unsatisfied.
No paid Run2 benchmark cell may start until this status is replaced by an evidenced freeze.
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

GateA recommends `run2-shared-decision-8192-v1`: shared decision8,192 output tokens; metadata,
query-keyword and answer stages1,000. This policy will be frozen identically across all12 cells.
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
Initial measured point estimate: USD38.764609 execution +USD8 reserve =USD46.764609. It is not an
upper bound;10% execution growth exceedsUSD42. Update stage means as completed conditions become
available. Stop for a material financial decision if the balanced remaining campaign cannot fit;
preserve the fixed population/settings and do not silently spend contingency. No next-cell release
with missing accounting, observability or final receipt. Run1 costs/results remain separate throughout.

## Freeze checklist

- [x] Current official output constraints, actual SDK path and Run1 size evidence independently reviewed.
- [x]8,192 recommendation and Run1 preservation recorded; GateA PR#25 merged.
- [ ] Instrumented real-runner fixture visible and independently fetched/audited in Langfuse.
- [ ] Saved question-level results visible in Langfuse Experiments with unique scoring identities.
- [ ] Instrumented/uninstrumented replay, trace-failure and two successive checkpoint regressions pass.
- [ ] Full offline suite, actual candidate replay and independent Standards/Spec reviews pass.
- [ ] Final source/config/population/assets/gate receipts and affordable campaign approval are immutable.
- [ ] Run all12 bounded cells only after all prior boxes pass; reconcile each before the next.

This draft is not a paid execution artifact. Final commands/identities and evidence will be appended
only after the implementation and gates are verified.
