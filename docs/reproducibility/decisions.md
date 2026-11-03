# Approved study decisions

Recorded 1 November 2026, Hong Kong time. Status: accepted, subject to the explicit validation and
execution gates below. [experimental-protocol.md](experimental-protocol.md) is the consolidated
operational specification; this log preserves the decisions and their rationale.

## D1 — Frozen author baseline

Freeze f9a173d and test_advanced.py. Describe the work as a controlled reproduction against arXiv v11,
documenting released-code/data differences. Collect the original full-mode baseline, establish replay,
refactor action gates, prove full-mode equivalence, reconstruct the two missing ablations, then add
evolution-only. This provides a concrete preservation target despite uncertain historical artifacts.

## D2 — Controlled DeepSeek substitution

Use DeepSeek across the original algorithm baseline and every ablation, with identical stage settings.
Keep the algorithm/evaluator intact and isolate provider adaptation. Compare with GPT-4o-mini findings
as a cross-model reproduction, without treating absolute scores as directly comparable. Estimate usage
and obtain approval before paid requests; credentials remain private.

## D3 — Provisional strict-function compatibility

Use deepseek-flash with thinking explicitly disabled and a minimal isolated strict-function adapter.
Preserve messages, schemas, parsing, memory behavior and scoring; validate all four schemas offline.
Return arguments to the original parser without executing tools or adding a generation turn. Preserve
the OpenAI backend. Semantic schema changes require review. This is a protocol approval, not proof of
live compatibility or permission to implement/run it.

## D4 — Full released-data target

Use all ten complete conversations (5,882 turns, 1,986 QA) across all four conditions, subject to budget.
Use the separate 18-turn/four-question fixture only for functional checks. Preserve history and all
included questions. D10a supplies a conditional fallback; it does not immediately replace this target.

## D5 — Isolated caches and canonical memory snapshots

Isolate each configuration and independent build repetition with provenance fingerprints, complete
note/index state and completion markers. Reject incomplete/mismatched caches. Preserve ordered notes,
link indices/mappings, metadata and evolution outcomes for inspection. Distinguish fresh construction,
cached QA and recorded-response replay; repeated QA is not an independent build trial.

## D6 — Fixed retrieval and observational measurements

Fix answer k=10 and construction neighbors=5, with immediate index refresh disabled and no evaluation
tuning. Document these as released defaults rather than verified paper-specific settings. Capture
initial/expanded retrieval counts (including duplicates), documented context-token counts and API
prompt usage, without truncation, deduplication or context-budget changes. Use identical questions
and model settings across conditions.

## D7 — Existing action boundaries

Independently gate strengthen and update_neighbor while retaining initial metadata, shared decision
logic and prompts. Strengthen includes new-note tag rewriting, so linking-only does not isolate graph
links from enrichment. Cover all four decision action sets across all configurations. Label these
as reconstructed operational ablations, not verified copies of unavailable author code.

## D8 — Decision-driven counter and consolidation

Preserve increments on every valid positive decision, even with disabled actions; negative decisions
and the original failure result do not increment. Consolidate every 100 positives without changing
embedding content, timing or refresh policy. Test disabled-action positives, failures and 99 to 100.
This retains control overhead intentionally. Charge joint generation once and report action execution
and suppressed decisions explicitly.

## D9 — Original generation settings and two kinds of evidence

Preserve temperature 0.7 for metadata/decision/query and category 1–4 answers, 0.5 for category 5, and
1,000 output tokens for each completion. Explicitly disable thinking and record endpoint, identifier,
version, parameters and fingerprint. Replay proves equivalence; independent live repetitions measure
variability. The subsequently approved frozen specification also fixes serial non-streaming transport,
a 120-second timeout setting and at most two SDK retries without semantic repair.

## D10 — Progressive USD 50 budget

The proposed USD 250 ceiling and three full-dataset repetitions were rejected. Adopt an initial
USD 50 total ceiling including contingency, provisional USD 1–2 compatibility/functional testing
and USD 5–10 pilot allocations. Three independent full builds per condition are an optional extension,
not the initial target. Determine affordability using measured usage and fixed, performance-independent
scope selection; paid execution remains separately gated.

## D10a — Exact conditional fallback and initial repetition count

Primary target remains all ten conversations and one independent build per conversation per condition.
If cost evidence excludes full scope, the approved fallback is exactly conv-49, conv-50 and conv-44:
sort by turn count/ID, strata 3/3/4, sequential draws with a separate Random(42), without redraws.

Freeze both manifests with original IDs/indices; pass offline contracts; obtain separate fixture and
pilot approvals; measure tokens/retries/context/cost. Forecast incurred plus remaining four-condition
cost with USD 8 contingency. Choose scope using cost evidence alone before comparative performance
inspection. If neither scope fits USD 50, stop for a revised decision. Preserve all selected questions,
context and model/retrieval settings. Additional repetitions require separate budget approval.

## D11 — Corrected primary and historical secondary scoring

Use current corrected author scoring as primary, per-category F1/BLEU-1 headlines and separate
category-5 adversarial_correct. Retain other author metrics/aggregation. Calculate the labelled legacy
view from identical immutable predictions/IDs/reference data without new model calls; higher historical
adversarial overlap is not better factual quality. Include scoring-policy IDs in every result surface
and test that rescoring cannot call a model or modify predictions.

## D12 — Transparent failure classification and recovery gates

Preserve original fallbacks and record run/build/question failures/retries. Distinguish failed-metric
zeros from actual zeros; never remove difficult cases or retry low-quality valid answers. Use a fixed
documented transport policy. Classify complete/degraded/incomplete runs, retain partial artifacts and
costs, and disclose limitations/exclusions without automatically discarding degraded runs. Paid recovery
requires approval. Test classification, metric-failure reporting and output preservation offline.

## D13 — Assignment requirements and discovery completion

The user supplied the authoritative requirements: deadline 13 November 2026 at midnight (Hong Kong time);
reproduce at least one result/behavior from a runnable agentic repository; make one isolated measurable
modification; meaningful subsets and controlled DeepSeek substitution are permitted. Three to five
stochastic trials are recommended, not unconditional. Submit a <=10-page report, reproducible GitHub
repository with commits and a <=15-minute recorded presentation. The current scope is accepted subject
to executing and documenting it. Conclude discovery and prioritize the smallest implementation.

## Approval to persist the plan and create tickets

After reviewing the frozen specification, the user authorized saving protocol/decisions in this repo
and creating GitHub issues T1–T8 with acceptance criteria and dependencies. This authorizes documentation
and tracker changes only. Implementation, commits and paid API calls remain unauthorized. Retain this
boundary in every ticket so a future agent does not infer execution permission from issue existence.


## T1–T4 implementation and commit authorization

The user subsequently authorized T1–T4 implementation and deterministic offline tests, preserving
frozen source and scientific decisions. The final branch instruction is one integration branch,
feature/reproducibility-foundation, with logically scoped T1/T2/T3/T4 commits and a consolidated PR.
Run ticket tests after each ticket and the complete offline suite at the end. Stop for review before
T5. No paid API calls or merge into main are authorized. Earlier parallel drafts are incorporated by
file review/copy; no branch merges are needed. The earlier separate-authorization requirement for
pushing is retained until explicitly resolved; prepare the local PR description before requesting it.

## PR #9 focused follow-up review

The user requested reviewability and safety corrections before merge. Compact version-2 selection
manifests replace duplicated dataset records while preserving the full dataset hash, original identities,
selection rules and exact expanded-manifest hashes. This changes representation, not the D4/D10a population.
Standalone AST loaders now verify frozen bytes, and direct uninstrumented/instrumented scoring parity is
tested. Optional reporting requires complete study identity. Default live execution is disabled until T5
has reviewed, durable phase/request/attempt/USD limits; a Boolean alone cannot enable paid execution.
No paid calls or T5 execution are authorized by these corrections.

## T5 fixture authorization and first compatibility result

The user subsequently authorized T5 implementation/preflight and then explicitly approved only the
USD2 compatibility fixture (44 logical calls, at most 132 physical attempts). Pilot, main execution,
recovery and branch pushing were excluded. See [the attempt report](t5-compatibility-20261101.md).

The first attempt stopped after ten physical requests because DeepSeek returned string connection
indices under the unchanged integer schema despite strict mode. The conservative ledger cost is
USD0.005851, with no unknown charges. The run is incomplete and is not compatibility acceptance or
a baseline result. This is observed evidence, not a revision of D3: preserve the contract and outputs,
and obtain a separate decision before paid recovery or any semantic/protocol change.

## D3a — BLK-007 validation-copy compatibility policy

On 1 November 2026, after the offline investigation, the user explicitly approved implementation and
offline testing of `canonical-index-strings-v1`. The default remains `strict-original-v1`.

Only `shared_decision.suggested_connections[*]` may admit strings matching ASCII `0|[1-9][0-9]*`
that Python `int` can parse. This is narrower than the frozen `as_index` tolerance. Validate an integer
copy against the unchanged complete schema, then return the original argument string byte-for-byte.
Do not convert booleans, signed/padded/Unicode/decimal strings, other fields or other schemas. Do not
filter unshown indices, reorder/deduplicate links, rewrite prompts, alter parsers or add semantic retries.
Original `as_index` and shown-neighbor checks retain those responsibilities.

Record raw schema invalidity, the affected field/items, validation-copy transformation, raw/returned
argument hashes, canonical original/copy hashes and policy ID. Accepted deviations mark a completed
run degraded; aborted/missing-output runs remain incomplete. Count affected completions separately
from transformed items and inherited cache deviations. Bind policy to approval, cache and reporting
identity; every experimental arm must use the same reviewed policy. The integer wire schema, author
algorithm, generation settings and scoring remain unchanged.

Preserve the rejected response and incomplete run. BLK-007 remains Investigating until a separately
authorized live compatibility test succeeds; offline success does not establish provider compliance.
No paid recovery, resumed fixture, conv-50 pilot, push or merge is authorized by this decision.
See [implementation and offline verification](blk-007-compatibility-review.md).

## Authorization — autonomous T5 baseline readiness

The user subsequently authorized remaining T5 implementation, offline verification, specialist reviews,
commits/pushes and merging PR #11 after all required checks pass. Resolve BLK-012 and other material
engineering defects before paid execution; preserve frozen author behavior and D3a. This does not
authorize T6–T8 or changes to algorithms, prompts, schemas, parsing/scoring, populations or settings.

Exactly one **fresh** compatibility phase is authorized under `canonical-index-strings-v1`: the frozen
18-turn/four-QA fixture, up to 44 logical calls, at most three attempts each and USD2 **additional**
spending including failures/retries, within the study ceiling and USD8 contingency. Up to four extra
schema probes are permitted if required; the planned fixture itself covers every schema, so the
existing 44-call/132-attempt limits are retained and no probes are planned. Record a new immutable
approval/source/preflight/run identity; never resume or overwrite the first failed fixture.

Compatibility may succeed with degradation solely from fully audited D3a deviations. Investigate any
other degradation; an incomplete/failed phase consumes this one authorization. Offline fixes may
continue, but another paid phase needs a separate decision. After successful compatibility, verify
runtime/assets/manifests/caches/results and prepare the exact unapproved 1,544-call conv-50 pilot plan
and command. **Stop before the pilot or full benchmark**; both remain separately gated.

## Execution record — fresh D3a phase incomplete

PR #11 merged as `167470b` after BLK-012 correction, 247 offline tests/71 subtests and clear repeat
Standards/Spec reviews. The authorized fresh phase `compatibility-d3a-20261101` then made 12 physical
requests, charged a conservative USD0.008316 and completed zero QA. One D3a response was correctly
admitted with unchanged input; the sixth evolution decision exhausted the frozen 1,000-token output
limit and returned incomplete JSON (BLK-013). The phase halted, preserving all evidence and charges.

The single fresh-phase authorization is consumed. No further paid recovery, pilot or full benchmark
is authorized. A larger output limit would amend D9 and needs explicit approval; a retry under unchanged
settings still needs separate paid-phase approval. The proposed change in the [readiness report](baseline-readiness.md)
is pending, not an approved decision or implemented setting. Preserve both failed runs as historical evidence.

## D9a — Approved shared-decision output allowance and one fresh verification phase

After the blocked-readiness record was merged in PR #12 (`5078459`), the user explicitly approved a
controlled generation-setting deviation: raise **only** shared-decision maximum output from 1,000 to
4,000 tokens. Metadata, query-keyword and answer generations remain at 1,000; all temperatures,
prompts, schemas, parsers, retrieval, memory actions and scoring stay unchanged. Apply these stage
limits identically across all four experimental arms. Preserve the original author files and label
the deviation in every future run under output policy `d9a-shared-decision-4000-v1`.

The frozen configuration records the output-policy ID; its configuration hash and the explicit
stage-cap map bind phase approval and run/cache provenance. Request validation/reporting use
`metadata:1000`, `shared_decision:4000`, `query_keywords:1000`, `answer:1000`.
The reviewed pricing bound is `pricing.max_output_tokens:4000` while each actual request still obeys
its own stage cap. At the existing peak rates, reserve 319,373 microUSD for a shared decision
and 315,773 microUSD for each other-stage attempt before transmission. The USD2 phase hard cap,
USD42 cumulative usable allowance and USD8 contingency within USD50 are unchanged. Keep the existing
SDK retry policy and terminal accounting-failure guard.

Exactly **one further fresh compatibility phase** is authorized after implementation, full offline
tests, Standards/Spec review and refreshed runtime preflight. It uses the frozen 18-turn/four-question
fixture, D3a `canonical-index-strings-v1`, at most 44 logical calls and 132 physical attempts (three per
logical call), and at most USD2 **additional** expenditure including failures/retries. No extra schema
probes are planned. Create a new immutable phase/run identity and explicit approval artifact only
after those gates pass; do not reuse either consumed phase's identity, approval, cache or artifacts.
All prior charges remain in the same durable study ledger.

At this decision, the D9a phase has **not** run and has no approved execution plan. A higher cap is not
proof of compatibility or sufficient output space for the fixture/pilot. BLK-013 remains Investigating
and BLK-007 remains Investigating until supported by the fresh live result. If this single phase fails,
preserve it and investigate offline; another paid recovery needs a new explicit decision. The ongoing
baseline-readiness task permits T5 engineering, commits/pushes and reviews; the conv-50 pilot, full
benchmark and T6–T8 remain unauthorized.

## Execution record — D9a fixture verified; pilot approval pending

The authorized phase `compatibility-d9a-20261101` completed all 18 turns and four original questions
under reviewed D9a implementation `4e7f82b`, source bundle
`02dc368e77f1a1e36d7d2deeffe1e6b0c9a7e8de9e715864852566e704ad7285`. It made 44 logical/physical
requests with zero retries or unknown charges. Conservative phase charge: USD0.053118; cumulative
study charge: USD0.067285 across 66 physical requests, retaining both earlier failed phases.

Status is **degraded solely by seven audited D3a completions/19 string indices**. All 44 original
argument strings, schema/stage settings and relevant hashes verify. All 18 notes/outcomes and 18×384
index rows are preserved; evolution counter 17. Both scoring views use the same four saved predictions
without metric failures. Maximum shared-decision output was 1,572 tokens; this verifies the fixture,
not a guarantee that 4,000 will suffice throughout the pilot. This functional fixture is not a quality
benchmark. BLK-007 is Mitigated; BLK-013 is Resolved for this fixture under D9a; BLK-012 stays Resolved.

The D9a phase authorization is now consumed. The user approved PR #13 for merge after its successful
verification; no PR #13 merge commit is claimed at this checkpoint. Offline suite: 268 tests/92 subtests,
with clear independent Standards/Spec reviews. See [readiness evidence](baseline-readiness.md) for
artifacts and the exact pilot command.

`artifacts/pilot-conv50-d9a-plan.json` is a verified **unapproved** plan: complete conv-50, 568 turns,
204 original QA, 1,544 logical calls, at most 4,632 physical attempts and USD10 cap. No pilot cache,
run or execution exists. Obtain separate explicit pilot authorization and record a new approved file
before execution. The full benchmark, further paid recovery and T6–T8 remain unauthorized. T5 remains
open until its later approved pilot/baseline acceptance criteria are fulfilled.

## Authorization — one conv-50 D9a pilot and cost-only forecast

On 1 November 2026 the user explicitly authorized one pilot using the frozen
`artifacts/pilot-conv50-d9a-plan.json`: full-mode conv-50, all 568 turns/204 questions,
USD10 cap, 1,544 logical calls and at most 4,632 physical attempts including SDK retries.
Preserve the reviewed D3a/D9a settings, source/preflight/compatibility bindings and fresh-build
identity. Record approval in a new file without overwriting the unapproved plan. Retain every
result, failure, partial artifact and incurred or reserved charge in the shared study ledger.

After the pilot, use measured usage/cost to forecast remaining four-condition expenditure with
already incurred costs and USD8 contingency. Inspect cost evidence for that decision, not comparative
quality. A failed/incomplete pilot does not authorize automatic recovery or a forecast that assumes
complete representative coverage. Stop before the full benchmark or T6–T8; neither those phases
nor another paid pilot/recovery phase is authorized by this instruction.

### Outcome — pilot incomplete; approval consumed

`pilot-conv50-d9a` executed on merged main `c659856` with the approved immutable binding. It retained
263 notes/outcomes and a 263×384 index before a shared-decision response failed JSON parsing.
The response finished with `tool_calls` at 970/4,000 tokens; a missing outer array bracket makes this
BLK-014, distinct from BLK-013 output-cap exhaustion. No repair or retry was applied. The following
metadata event was blocked before transmission by the durable halt.

The phase made 526 logical/physical requests, no retries, and answered zero of 204 questions.
Conservative charge: USD0.739432; study total USD0.806717/592 requests, with zero unknown charges.
Remaining balance is USD49.193283 including contingency, or USD41.193283 while preserving USD8.
These are ledger balances, not approval for new spending or full/fallback affordability estimates.
The existing cost forecaster rejects this incomplete pilot; no population change is made.

All raw phase artifacts and historical ledger rows verify unchanged. The approved D3a deviations
(176 completions/661 indices) survive the later failure; incomplete status takes precedence.
The [pilot report](t5-pilot-conv50-d9a-20261101.md) records exact evidence and offline replay.
This authorization is consumed. No further paid phase, full benchmark or T6–T8 was started.

## Authorization — BLK-014 checkpoint engineering only

The user approved implementation/offline tests and a PR for checkpoint recovery, preserving all 263
notes, the failed evolution, stale index and parent provenance. Strict validation remains unchanged.
No JSON repair or raw-malformed-response acceptance exception is approved. Paid continuation is not
authorized; T6–T8 and main benchmark remain gated.

The child must have a new immutable approval and phase identity, with the same shared study ledger
and an exclusive durable claim on its parent checkpoint. Restore the exact saved prefix and begin at
`D15:8`; do not regenerate note263 or its failed decision. New support-code/preflight fingerprints
must remain explicit: the reviewed migration permits only checkpoint/runner/phase/forecast/budget
support changes, while author files, provider adapter, scoring and scientific settings match the parent.
Retain inherited failures/deviations and charges once; child completion is degraded and the parent
remains incomplete. See the [recovery runbook](checkpoint-recovery.md).

## Authorization — merge PR #14 and one paid checkpoint child

On 1 November 2026 the user explicitly authorized merging reviewed PR #14 after the complete offline
suite and normal check gates. The exact reviewed head `77afc36` passed 287 tests/92 subtests. GitHub
reported no required checks or branch rules; the normal merge produced
`ca6c68f0f109b474a5206f59085474b683a4f9ca`, now local `main`. Frozen author/provider/schema/scoring/
retrieval/configuration files remain unchanged.

Exactly one paid child of `pilot-conv50-d9a` is authorized under `blk014-checkpoint-v1` and
`canonical-index-strings-v1`, model `deepseek-flash`: restore 263 notes, failed evolution, original
stale index and counter261; resume at `D15:8`; process 305 remaining turns and all 204 original QA.
Hard additional cap USD10, at most 1,018 new logical calls / 3,054 physical attempts, with existing
per-call retry limits. Use a new bound approval/run identity and the existing shared ledger, retaining
all USD0.806717 prior charges and preserving USD8 contingency within USD50. No output repair or
scientific-setting change is authorized.

After completion, verify all 568 turns/204 questions, both scoring views, complete cache, inherited
failures/deviations and degraded classification; forecast full versus predefined fallback using cost
evidence only. If a new malformed response, contract violation or spending/provenance failure stops
the phase, preserve partial evidence/charges and investigate offline. No second paid phase/restart/
recovery, full benchmark or T6–T8 is authorized. Stop at completed reporting/forecast or a material blocker.

### Outcome — completed degraded conv-50 lineage and cost-only recommendation

`pilot-conv50-checkpoint-child` completed all 305 remaining turns and 204 original QA on merged main
`ca6c68f`, restoring the exact 263-note prefix and resuming at `D15:8`. Final cache: 568 notes/outcomes,
568×384 index, counter566. The parent remains immutable and Incomplete; the completed lineage is
Degraded with the original failed evolution and all compatibility audits retained. No JSON repair,
new acceptance exception, scientific change or unexpected new failure occurred.

Child calls: 1,018 logical/physical, zero retries/unknown charges, USD2.219082 conservative charge.
Combined baseline: 1,544 calls / USD2.958514. Cumulative study, including prior compatibility phases:
1,610 calls / USD3.025799. The sole child authorization is consumed; no further paid request is approved.
All accepted argument bytes, QA identities/order, complete cache, historical ledger rows and both
saved-prediction scoring views verify. The full pre-merge suite passed 287 tests/92 subtests.

The forecast was generated before inspecting quality summaries. At one build per conversation/arm,
all ten conversations project USD127.391486 total; the frozen fallback projects USD42.762234,
each including incurred spending and USD8 contingency, crediting this baseline once. Recommend
`conv-49`, `conv-50`, `conv-44` under D10a's cost-only rule; no further execution followed. The fallback's
2× remaining-cost diagnostic is USD74.498668, so it is not a guaranteed bound. Review/approval and
ongoing cost reconciliation are required for further collection. No performance-based selection occurred.

See [baseline outcome and evidence](t5-conv50-baseline-20261101.md). Before T6, review the degraded
baseline and scope recommendation, separately approve remaining selected-scope T5 full-mode work
(two other conversations for fallback) and T6 itself. T6–T8 and further paid phases are unstarted.

## Authorization — T6 deterministic replay on the completed conv-50 lineage

On 2 November 2026 the user explicitly authorized T6 implementation/offline tests, documentation,
commits/push, focused PR, Standards/Spec review and merge after acceptance. The completed conv-50
parent/child lineage is the replay reference; this authorizes offline T6 before the still-gated
remaining selected-conversation T5 collection. It does not close T5 or change the population.

Preserve frozen author/provider/scoring/configuration and all raw evidence. Replay exact captured
response strings and request identities; distinguish approved D3a deviations and rejected outputs.
Normalise only incidental UUID identities/wall-clock access fields in comparison copies. Historical
per-insertion snapshots/query vectors are unavailable, so retain that limitation and use labelled
portable fixtures plus frozen-author-derived comparison hashes, verified against recorded checkpoints,
requests, outcomes, retrieval and scores. This is not new historical evidence or independent live trials.
No paid model calls, T7 switches, new compatibility policy or additional benchmark experiment is approved.

## Authorization — T7 independent action gates

On 2 November 2026 the user authorized issue #7 implementation, deterministic tests, Standards/Spec
reviews, routine corrections, documentation/blocker updates, commits/push, a focused PR and merge
after all tests and full-mode candidate replay pass. Use merged T6 (`87f34d7`) as the fixed oracle;
run both the frozen reference and the actual T7 candidate against it. Preserve the author source,
all baseline evidence, scientific settings and D3a/D9a policies. Independently gate only the released
strengthen and update_neighbor action execution under D7/D8; positive decisions still count even
when all actions are disabled. This authorizes no paid calls, T8 implementation or ablation collection.

### Verified T7 outcome

Implementation `84ec320`, observational review correction `a591ea8`, PR #16. All96 action tests,
mandatory103-test T6 portable gate and complete429-test/92-subtest offline suite pass. Standards
and Spec re-reviews are clear. The final frozen-reference and actual T7 full-mode candidate each
match1,544 requests,568 fixed state hashes/outcomes,204 QA, both scoring views and376 logical
failure/audit records; both remain Degraded. Direct receipts differ only by implementation label,
and both run source fingerprints match current source. Original run/cache/ledger hashes are unchanged;
no paid calls or ablation experiments occurred. See [T7 evidence and commands](t7-action-gates.md).
BLK-002 is Mitigated by operational reconstructions; unavailable historical ablation code and BLK-015's
recording/runtime limits remain explicit. T8 and further paid collection still need separate approval.

## Authorization — T8 implementation and paid main execution

On 2 November 2026, after T7 merge `577a1e3`, the user invoked `implement-spec T8` and explicitly
authorized paid execution. This authorizes T8 implementation/offline tests/reviews, the skill's
integration branch/commits/push/draft PR workflow, and the frozen one-build-per-conversation/condition
study within the existing USD50 total ceiling including USD8 contingency. It is not permission to
increase the ceiling, add repetitions, change scientific settings or automatically recover paid failures.
The skill ends with a PR ready for review; no new T8 merge authorization is inferred.

D10a's predefined fallback is activated using the existing completed-pilot cost-only forecast:
full scope USD127.391486 does not fit; fallback USD42.762234 including incurred spending/contingency
does. Population remains exactly conv-49, conv-50, conv-44, all turns/questions, across four conditions.
The archived full-mode conv-50 lineage is credited once. Complete full-mode conv-49/conv-44 (T5)
before the remaining nine ablation cells (T8); do not duplicate the existing baseline or claim T5 closed
before its remaining selected-scope collection verifies.

At authorization, the read-only cumulative ledger verifies1610 settled attempts / USD3.025799,
zero unknown charges, SHA256 `dcdb729c7f291da2d07949b374bdebc18952668548f691802f744da2ea1141c2`.
Thus at most USD38.974201 additional is usable while preserving the USD8 contingency. Remaining
nominal workload is16936 logical calls, at most50808 physical attempts, partitioned into eleven fresh
complete-conversation phases. Each needs a fresh immutable approval bound to its exact condition,
action flags, population partition, repetition0, current source/preflight and unchanged provider policy.
Use the same durable study ledger; all earlier approvals remain consumed and historical artifacts immutable.

Verify/review the main-phase controls and compatibility-source migration offline before transmission.
Retain DeepSeek/D3a/D9a, original prompts/schemas/parsing/retrieval/scoring and T7 action implementation;
financial/report support changes cannot redefine that scientific reference. Reconcile measured usage
and cost-only affordability between phases. On a provider/contract, provenance or spending failure,
preserve all evidence/charges and stop paid collection; recovery/reruns require a separate decision.
No tuning, dropped questions, context truncation, silent repairs or quality-based retries are authorized.

Issue #8 also authorizes saved-result local exports and Langfuse comparisons using the existing
author metrics and pinned SDK5.1.0, without model/LLM-judge calls. Local artifacts remain authoritative
if optional reporting fails. See [T8 execution record](t8-execution.md) for exact plans and outcomes.

## Execution hold — T8 conv-49 cap exhaustion (BLK-013 reopened)

On2 November2026 the authorized first T8 cell `t8-full-conv49-r0-20261102` stopped Incomplete at
`D22:2`: HTTP200/`finish_reason=length` at the frozen D9a4,000-token shared-decision cap. Preserve
413 notes, counter411, failed evolution, stale413-row index,270 audited D3a deviations/1,066 items
and all raw evidence. The next metadata call was blocked without transmission. All826 actual attempts
settled conservative USD1.413246; cumulative study cost is USD4.439045/2,436 attempts, zero unknown.
The exact approval is consumed. Conv-44/ablations/recovery remain unexecuted.

This is an observed hold under the existing protocol, **not** a new setting or execution approval.
Offline saved-response replay confirms identical request/schema/raw response and correct terminal
rejection, with zero network requests. Remaining scope must not continue automatically after failure.
See [T8 evidence and proposed choices](t8-execution.md#paid-hold--blk-013-recurrence).
Checkpoint continuation would need a new conv-49 lineage policy/approval, preserving this exact state
and starting `D22:3` (96 turns/196 QA;584 logical calls, at most1,752 attempts). Raising the cap instead
would require an explicit protocol amendment and treatment of existing4,000-token baseline evidence.
Neither is authorized or implemented by this hold record. T5/T8 remain open and PR#17 remains draft.

## Authorization — BLK-013 conv-49 checkpoint engineering only

On3 November2026 the user approved implementing and offline-testing exact-state checkpoint recovery
for `t8-full-conv49-r0-20261102`, keeping the frozen D9a4,000-token shared-decision cap. Preserve all
413 notes, counter411, failed `D22:2` evolution, stale index, parent provenance, raw output and charges;
resume at `D22:3` only under a future separately approved paid phase. Remaining scope is96 turns plus
all196 original questions,584 logical calls and at most1,752 physical attempts.

This authorizes narrow support code, deterministic offline tests, documentation and review on existing
T8 PR#17. It grants no paid continuation/recovery, new main cell, cap/prompt/schema/parser/scoring/
retrieval/model change or merge. Reuse existing checkpoint/phase/permit/runner/result-import seams;
retain one-shot parent claims, cumulative ledger history, immutable evidence and inherited degradation.
Keep BLK-013 Open: engineering verification cannot resolve the observed output-cap limitation.

### Verified conv-49 checkpoint engineering outcome

Implementation `1ffa184`, integrated as `a5695be`, passes545 offline tests/92 subtests and clear
independent Standards/Spec reviews. Network-disabled current-source preflight and exact real-parent
restoration pass, with unchanged parent artifacts and cumulative USD4.439045/2,436-attempt ledger.
Unapproved execution rejects before client creation, phase claim or schema migration. Frozen author,
provider, scoring, retrieval, model/settings and benchmark inputs remain unchanged.

Prepared `artifacts/t8/conv49-checkpoint-plan.json` stays `approved:false`: proposed USD3 ceiling,
584 logical calls and at most1,752 attempts, source
`0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`.
Its historical-cost estimate is USD1.566190, not an upper bound or spending grant. No approved child
artifact exists and no paid recovery was executed. BLK-013 remains Open because truncation can recur;
PR#17 remains draft and unmerged. Separate paid approval after review is still required.

## Authorization — PR17 merge and one conv-49 recovery child

On 3 November 2026 the user explicitly authorized merging PR#17 into main after fresh complete and
focused offline tests, required checks and Standards/Spec reviews pass, then executing exactly one
fresh checkpoint child for `t8-full-conv49-r0-20261102` under `blk013-conv49-checkpoint-v1`.
Restore413 notes/outcomes, counter411, failed `D22:2` and the exact stale413×384 float32 index;
resume `D22:3`, process96 remaining turns and all196 original QA in frozen order. Preserve D3a,
D9a4,000, original algorithm/prompts/schemas/parsers/retrieval/scoring/model/settings and all evidence.

The hard additional ceiling is USD3,584 logical calls and at most1,752 physical attempts under the
existing SDK retry rules. Use the existing cumulative ledger, USD50 total/USD8 contingency and a new
immutable parent/source/preflight-bound approval; do not reuse consumed approvals or reset history.
No other experimental cell, child restart, second recovery chain or repetition is authorized.
On any new provider/contract, provenance or financial failure, halt further paid transmission, retain
all partial results/charges and investigate offline. Non-scientific engineering corrections may be
made/reviewed autonomously, but no paid restart is implied.

After successful completion, verify509 unique turns/196 ordered QA, complete cache/index, both
scoring views, inherited Degraded classification and once-only parent/child accounting. Verify original
conv-50 unchanged, reforecast the remaining balanced fallback using cost evidence and prepare the next
phase for separate approval, prioritizing a paired Full/Neither comparison subject to the existing
baseline dependencies. Stop after that preparation or a material blocker; do not execute another cell.
