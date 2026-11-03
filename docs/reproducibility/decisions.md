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

### Verified PR17 merge and conv-49 child outcome

PR#17 merged as `78ac46b57fd3b89bbf75a315565c945fbb9713be` after fresh545 tests/92 subtests,
64 focused tests, clear final Standards/Spec reviews and no failed required checks or rule bypass.
The new immutable child approval `a550491a-d027-4752-a959-3b6bcdc1e0f6` executed once on synchronized
main. `t8-full-conv49-checkpoint-child` completed96 turns/196 QA with584 logical/physical requests,
USD1.850853, zero retries/unknown charges. Original failed `D22:2`, parent state/evidence, old ledger
rows and original conv-50 remain unchanged. Completed lineage509 notes/counter507 is Degraded.

Combined conv-49 cost is USD3.264099; cumulative study USD6.289898/3,020 settled requests. The child
approval is consumed. No other cell or paid recovery was executed. BLK-013 remains Open: the unchanged
4,000-token cap is not guaranteed adequate elsewhere. Corrected/historical scoring views and all
predictions/observations are saved; [verified outcome](t8-conv49-baseline-20261103.md).

The remaining balanced fixed-population point forecast is USD45.978600 including incurred spending
and USD8 contingency, with USD35.710102 usable actual budget remaining. This is not an upper bound.
The next unapproved full-conv44 plan proposes USD5/1,666 logical/4,998 attempts. Prioritize paired
Neither-conv49 after the existing full-conv44 baseline prerequisite; running it first would require an
explicit sequencing amendment and new reviewed plan. No such gate/population change or further paid
approval is made by this outcome record. T5/T8 remain open for the uncollected scope.

## Authorization — PR18 merge and one Full conv-44 phase

On 3 November 2026 the user authorized review/merge of documentation PR#18 if checks pass and exactly
one fresh Full A-MEM conv-44 phase under the existing frozen protocol. Scope: all675 turns/158 original
questions, maximum USD5 additional,1,666 logical calls and4,998 physical attempts under the existing
SDK retry policy. Use the cumulative ledger and preserve USD50 total/USD8 contingency, both completed
conv-49/conv-50 baselines, original algorithm, DeepSeek/D3a/D9a settings, retrieval and scoring.

Verify current-source preflight, immutable provenance, isolated fresh cache and spending controls
before transmission; create a new scope-bound immutable approval. Routine non-scientific engineering,
offline tests, blocker/documentation updates and scoped commits may proceed autonomously. On output,
provider, provenance or financial failure, preserve partial evidence/charges, investigate offline and
stop before any paid recovery. No ablation, repeat, restart, second recovery or other paid phase is
authorized. Stop after all three full-mode baselines verify, or a material blocker prevents continuation;
report conv-44 quality/status/cost, cumulative budget/forecast and readiness for the first ablation.

## Outcome — Full conv-44 stopped; BLK-013 remains Open

PR#18 merged as `f78215e3a6e127d19001df73011b27c273b1f65d` after clear reviews/checks;
production fingerprint remains `0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`.
Fresh preflight/provenance/cache/spending gates passed. Immutable approval
`295e4e88-5bd8-479f-951a-fbb4d4ef56e6` funded only `t8-full-conv44-r0-20261103` under USD5,
1,666 logical/4,998 physical ceilings. That single approval is consumed.

The424th shared decision (`D18:21`) exhausted unchanged D9a4,000 output tokens, HTTP200/`length`.
The original failure fallback,424 notes/counter422 and exact stale index are preserved. Zero of158
questions completed; F1/BLEU-1/c5 correctness are unavailable. All848 actual requests settled
USD1.415538 with zero retries/unknown charges. Cumulative study cost is USD7.705436/3,868 attempts;
USD34.294564 remains usable while preserving USD8. Prior baselines, historical ledger rows and raw
response evidence remain unchanged. Offline exact-request MockTransport replay reproduces rejection;
the subsequent metadata transmission and the Neither-conv49 planner are blocked.

The whole-fresh-cell cost-only scenario totals USD47.394138 including incurred costs and USD8 reserve;
it is neither an upper bound nor authority to restart. A non-executable exact-state checkpoint suffix
would require251 turns/158 QA,818 logical calls/2,454 maximum attempts; its conditional estimate is
USD1.936945 (balanced total USD46.075868). Conv-44 checkpoint support and paid continuation require
separate decisions/review. No output repair, cap/prompt/schema change, recovery or ablation was
implemented or executed. BLK-013 remains Open; T5/T8 and first-ablation readiness remain blocked.
See [verified outcome and evidence](t8-conv44-incomplete-20261103.md). Stop at the authorized failure
boundary; unused budget is not permission for another phase.

## Authorization — exact conv-44 checkpoint engineering, merge and one child

On 3 November 2026 the user explicitly authorized autonomous conv-44 checkpoint implementation,
offline tests, Standards/Spec review, scoped commits/pushes and merge after all required checks pass.
Documentation PR#19 may also merge after review; it merged as `11685b228f75e508d763be5417af5a5cef2a6d26`.
This supersedes the previous paid hold only for the single child described here; it grants no ablation.

Recover only parent `t8-full-conv44-r0-20261103`, canonical receipt SHA256
`dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b`.
Preserve424 notes, links/metadata, counter422, failed `D18:21` and its original fallback, and exact
stale424×384 float32 index. Resume `D18:22`, process251 remaining turns and all158 original QA.
Do not regenerate the prefix/rejected decision, refresh embeddings, repair JSON or change scientific
settings. Use the existing DeepSeek Flash, D3a and D9a policies, prompts/schemas/parser/retrieval/scoring.

Exactly one new immutable child approval may authorize **USD3 additional,818 logical calls and2,454
physical attempts**, including the existing permitted SDK retries. Bind the exact parent, current
reviewed source, dataset, assets/preflight, model and provider policy. Retain the existing cumulative
USD50 study ledger, USD8 reserve, pre-request reservations, durable halt and one-shot checkpoint
ownership. Do not reopen the parent, reuse an approval or reset historical accounting.

After verified merge/preflight/safeguards, execute this single phase without further confirmation.
If provider truncation/contract violation or provenance/spending failure recurs, halt, preserve partial
state/raw responses/charges and investigate offline. No second paid recovery or automatic restart is
authorized. On success verify675 ordered turns/158 unique QA, final memory/index, inherited degradation,
both scoring views and separate adversarial correctness, once-only parent/child costs and a cost-only
affordability forecast. Stop after verified completion or a material blocker. No ablation or further
paid phase is authorized by this grant. BLK-013 remains Open until the evidence supports a narrower
mitigation claim; checkpoint completion would not prove output-cap adequacy generally.

### Verified conv-44 recovery engineering before merge

Implementation `563e8f4` and PR#20 pass570 offline tests/92 subtests,146 focused tests/60 subtests
and clear independent Standards/Spec reviews. Source fingerprint:
`eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`.
Current-source preflight and exact real-parent restore/export pass; all43 protected files and the
cumulative USD7.705436/3,868-request ledger remain unchanged, zero unknown charges. Unapproved
execution rejects before client/claim creation. The prepared plan remains `approved:false`, exactly
USD3/818 logical/2,454 physical,251 new turns/158 QA. The existing user grant permits merge and one
fresh approved child after final gates, but no child has executed at this checkpoint. No scientific
or provider policy changed; BLK-013 remains Open. No ablation or second recovery is authorized.

## Outcome — authorized conv-44 child stopped; all grants consumed

PR#20 merged normally as `3d0e04ac3054266cce8a82c3408d734de76a0fda`; post-merge preflight and exact
parent/current-source/ledger/cache checks passed. New approval `ad09fe3d-5401-4898-a64e-294491a6dc64`
funded only `t8-full-conv44-checkpoint-child`, USD3/818-logical/2,454-attempt ceilings. It restored424
notes/counter422/stale index and resumed `D18:22` without regenerating the prefix or failed decision.

After186 new turns, `D26:18` exhausted the unchanged4,000-token cap, HTTP200/`length`. Original
fallback/failed decision,610 total notes/counter607 and610×384 partial index are retained. Natural
original consolidations at500/600 are observed; no refresh occurred during restoration. Zero of158
QA completed, so corrected/historical metrics and adversarial correctness are unavailable. Status is
Incomplete, not a completed Degraded baseline. No second recovery/restart or ablation was executed.

Child372 settled requests/USD0.702421; parent+child1,220/USD2.117959; cumulative USD8.407857/4,240,
zero retries in the child and zero unknown charges. All274 inherited failure records,131 new/271
inherited D3a deviations and all original parent/baseline hashes/old ledger rows verify. Exact offline
SDK replay reproduces rejection;97 post-failure regressions pass. The child is durably halted and
its grant consumed. No complete cache, new question result or scoring view exists for conv-44.

The whole-fresh-cell cost-only scenario totals USD48.096559 including incurred costs and USD8
reserve. A hypothetical further suffix (65 turns/158 QA,446 calls/1,338 attempts) estimates
USD1.344443, conditional balanced total USD46.185787; another recovery chain is unsupported and
unauthorized. These are planning arithmetic, not bounds or spending approvals. BLK-013 remains Open;
T5/T8 and first-ablation readiness remain blocked. Stop at the explicit provider-failure boundary.
See [verified outcome](t8-conv44-recovery-incomplete-20261103.md). No population, schema, prompt,
model, generation limit, scoring, retrieval or memory change is approved by this outcome record.

## Authorization — second pinned conv-44 continuation

On 3 November 2026 the user explicitly authorized the smallest implementation, focused/full offline
tests, independent Standards/Spec reviews, commits/pushes and merge for one additional conv-44
continuation, plus a separate reviewed/merged outcome-documentation PR. No intermediate approval is
required after the safeguards pass. This supersedes the previous hold only for this one continuation.

Immediate parent: `t8-full-conv44-checkpoint-child`, canonical phase SHA256
`fb730968fc1eec7cd4df4bcae5dc89baa7ff507dc111c5c1868319f5106d7fd9`.
Verify its full lineage to original `t8-full-conv44-r0-20261103`, canonical phase SHA256
`dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b`, including both immutable
snapshots, approvals, source/configuration and all ledger prefixes. Preserve both original failures
(`D18:21`, `D26:18`) and their unchanged fallbacks; restore610 ordered notes/metadata/links,
counter607 and exact stale610×384 float32 retrieval state without re-embedding. Resume `D26:19`,
process65 original turns, then all158 original QA in frozen order. Do not repeat historical requests.

One new single-use approval may authorize **USD3 additional,446 logical calls and1,338 physical
attempts**, including permitted SDK retries. The workload is130 memory calls plus316 question calls.
Bind exact parent/root lineage, reviewed current source, dataset/configuration, assets/preflight,
model and provider policy. Keep the existing USD8.407857/4,240-request cumulative ledger, USD50
ceiling and USD8 reserve; do not reset accounting or reuse earlier grants. Enforce one-shot chain
ownership and charge all three phases once. Permit only this named second continuation, not an
arbitrary chain or third recovery. Support policy: `blk013-conv44-second-checkpoint-v1`.

Frozen algorithm/prompts/schema/parser/model, temperatures, D3a policy,4,000-token shared-decision
cap, retrieval, index policy and scoring remain unchanged. Preserve existing origin IDs when copying
inherited failure records across the second hop. A support-only runner annotation correction is
within scope; no memory algorithm change is permitted. All prior raw artifacts and completed
conv-49/conv-50 baselines stay immutable.

After offline validation, reviews, merge and exact-state preflight, execute this phase once. On new
invalid/truncated provider output or provenance/spending-control failure, halt paid transmission,
preserve partial state/responses/charges and investigate offline. Apply only original fallbacks;
no JSON repair, cap increase, semantic retry or third paid recovery is authorized. Stop on another
material blocker or verified675-turn/158-QA completion. A completed lineage must be Degraded with
all inherited failures/audits, dual author scoring and separate adversarial correctness. Reconcile
costs without duplication and reforecast by cost evidence alone. No ablation or other paid phase is
authorized. BLK-013 stays Open unless evidence supports a narrower mitigation claim.

### Verified second-continuation engineering

Feature `f49da9a`, provenance fix `acefbfa` (BLK-019) and terminal admission fix `59ab9ae` (BLK-020),
integrated at `7211a4a`, pass613 offline tests/92 subtests (16 intentional SDK metadata warnings),
189 focused tests/60 subtests and two clear independent62-test reviews. Source fingerprint:
`0341a2a579842725c9ac6a18a110e2816a2896c32e07cf883fd36e2ef1ab681f`.
Actual610-note/counter607/stale-index restore/export matches exactly, with both ancestor pins and
408 failure records verified; all51 protected files and the real ledger stay unchanged. Fresh runtime
preflight passes with sockets disabled; unapproved execution rejects before client/claim creation.
The root SDK admission-fault replay now halts with zero transmissions and retained reservations;
genuine transport/provider retries remain unchanged. BLK-019/020 are Resolved; BLK-013 stays Open.
PR#22, final merge and the new single-use approved copy/live continuation are pending at this checkpoint.
The unapproved plan binds USD3/446 logical/1,338 physical limits; no new paid phase has executed.

## Outcome — second conv-44 continuation stopped at the paid boundary

On 3 November2026, PR#22 merged normally as `5ddc96ef8653bcf8997f2d7840435c4630826e09` after
613 offline tests/92 subtests,189 focused tests/60 subtests and clear independent Standards/Spec
reviews. Current-main runtime preflight and exact610-note/counter607/stale-index verification passed
with both pinned ancestors and unchanged historical ledger/baselines. The fresh single-use approval
`a35ef8a2-78f1-44c6-9f67-1c36d605b2c2` executed once under USD3/446-call/1,338-attempt limits.

Grandchild `t8-full-conv44-checkpoint-grandchild` resumed `D26:19`, then stopped after26 new turns
at `D26:44`: HTTP200/`length`,4,000 output/5,638 input tokens, request
`633454cd-c049-4132-9754-f9ba24ea63bf`. BLK-013 recurred. Original fallback retains note636,
counter632 and no new links/neighbour changes for that decision; next metadata is blocked before
transmission. The entire lineage is **Incomplete**, not completed Degraded:636/675 notes,0/158 QA.
Both scoring views and adversarial correctness are unavailable. Preserve all original failures,
408 inherited records,417 total D3a deviations/1,654 transformations and exact stale index history.

The new52 logical/physical calls cost conservative USD0.122276, zero retries/unknown charges.
Conv-44 totals1,272 requests/USD2.240235; cumulative study4,292/USD8.530133, zero unknown charges.
All prior artifacts/ledger rows and completed conv-49/conv-50 baselines verify unchanged. Exact
offline MockTransport replay and independent original catch-boundary replay reproduce the failure;
62 post-failure tests and separate root/independent state/audit/accounting checks pass. This verifies
safe stopping, not provider-cap adequacy. BLK-019/020 remain Resolved; BLK-013 remains Open.

The consumed grant cannot fund another phase.39 turns and158 QA remain, next `D26:45` (394 logical
calls/1,182 maximum attempts hypothetically). Third recovery is unsupported and unauthorized; actual
third-recovery and ablation planning reject without a transmission. No further recovery, restart,
ablation, cap/compatibility/schema change or population revision is approved by this record.

Cost-only whole-fresh-cell point scenario: USD48.218835 including incurred costs and USD8 reserve.
Hypothetical preserved-suffix estimate: USD1.282387, conditional balanced total USD46.246007 with
nine ablations and reserve. These are not upper bounds, executable plans or spending grants. No
accuracy result influenced them. Stop at the material provider-failure boundary; no further paid
execution occurred. See [verified outcome and inventory](t8-conv44-second-recovery-incomplete-20261103.md).

## Authorization — Run 2 fully observed campaign

On3 November2026 the user authorized a new campaign, after output-limit investigation (GateA) and
verified real-runner Langfuse observability (GateB). Track [issue#24](https://github.com/alistairkung/A-mem-reproducibility/issues/24).
All existing runs remain immutable exploratory Run1 evidence, including the USD8.530133/4,292-request
ledger, completed conv-49/50 and incomplete conv-44 lineage. Do not overwrite/relabel them or pool
their predictions with Run2 primary evaluation. Run2 has a separate USD50 conservative ceiling:
USD42 usable, USD8 protected reserve; Run1 spending remains separately recorded.

Engineering, offline tests, focused PRs/reviews/merges and all12 fresh Run2 cells are authorized once
both gates, frozen configuration, independent reviews/preflight and affordability pass. Preserve the
four action conditions, all questions from conv-49/50/44, model, prompts/schemas/parsers, temperatures,
disabled thinking, k=10/five neighbours, index/counter/action/scoring semantics. A documented supported
larger shared-decision allowance may be selected/frozen uniformly before any Run2 benchmark call.
GateA recommends8,192 with1,000 elsewhere; [evidence](run2-output-limit-investigation.md). Hosted
long-output reliability remains untested; official support and offline SDK serialization are distinct
from a paid probe. No exploratory paid probe is implicitly authorized or charged to experimental cells.

Run2 may automatically continue sequential BLK-013 checkpoints within each original cell's allocation,
retaining original failed output/fallback, exact ordered notes/counter/stale embeddings, immutable
lineage and cumulative charges. Never repeat/repair a failed semantic decision or reset cell quotas.
At least two successive simulated failures must pass before execution. Other provider/transport,
provenance/scientific, observability or spending failures stop; no schema/compatibility changes,
contingency top-up or silent population reduction are authorized.

GateB must exercise the real instrumented runner with offline responses, fetch actual observations
from the configured project, verify all stage/action/retrieval/QA inputs/outputs/usage/failures/IDs,
import saved question results into Experiments, prove instrumented/uninstrumented replay equivalence
and zero extra model calls, and simulate output exhaustion/tracing failure. Authentication or a
standalone synthetic trace is insufficient. Local immutable artifacts remain authoritative.

Execute one bounded verified cell at a time, reconcile cost/observations and reforecast before each
next cell. Stop on an unsatisfied gate/material scientific change or unaffordable continuation;
otherwise proceed autonomously. At this authorization checkpoint no Run2 code or paid benchmark
execution exists. Final generation policy, live observability gate and campaign preflight are pending.

### Run2 verified freeze before primary execution

On3 November2026, GateA PR#25 and the reviewed PR#26 implementation establish the frozen
`run2-shared-decision-8192-v1` policy:8,192 shared-decision output tokens,1,000 at every other stage,
identical across all12 fresh cells. Official maximum support and real SDK offline serialization
are verified; no exploratory paid probe or hosted reliability guarantee is claimed. Preserve the
Run1 default4K profile, original author source/prompts/schemas/parsers/model/temperatures/retrieval/
index/counter/scoring semantics and D3a unchanged.

Source fingerprint `184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe` passes715
offline tests/92 subtests (17 expected warnings), current-source network-disabled runtime preflight
and both complete568-note/204-Q archive replays. All1,544 recorded requests, per-insertion memory/
index, retrieval, predictions, scoring, consolidation and376 logical failure records match between
original and full candidate; only the implementation label differs. An explicit immutable reviewed
support-source reference permits named support deltas without relaxing author/schema/scorer/assets/
config pins, raw evidence or fixed behavioral oracles. Legacy Run1 execution still rejects Run2 source.

GateB's actual8K real-assets18-turn/four-Q fixture has130 visible observations/56 scores and both
saved scoring-policy Experiments verified by exact readback. Traced/untraced ordered replay and
simulated tracing failure preserve memory/index/predictions/scoring, with zero network LLM calls.
The actual campaign executor separately completes two successive mocked length-failure recoveries,
50 mock calls and final QA/Experiments in an isolated fixture ledger. Independent Standards/Spec
audits verify raw proof/readback hashes and exact values; no auth-only or standalone trace substitutes.
BLK-011 is Resolved for Run2; Run1 remains historically unwired. BLK-017/018/019/021 corrections also
pass final tests/reviews. BLK-013 remains Open as a provider reliability risk.

The frozen [Run2 protocol](run2-protocol.md) and local `artifacts/run2/frozen/manifest.json`
(`5ebd46fd99635d1f74f16935648856de1e5e3c0dc2d6c35ae8b8fef581a7c1c6`) bind source, compact
population, configuration, assets, preflight, gates, reviews, cost forecast and the independently
reviewed one-cell script (`b86e7471d76b73ad81564911f166dd92806658ee8c9efaa3a692b648b3ad37a1`).
Final campaign preparation is unapproved until the final factual audit and normal PR merge pass;
then the user's existing grant authorizes an immutable approved copy and phase-bound single-use
approvals. The superseded draft plan stays unapproved and cannot be reused.

Cost-only initial execution forecastUSD38.764612 plus protectedUSD8 =USD46.764612; three extra
microUSD relative to GateA result from per-cell rounding. Run2 enforcesUSD42 usable, an originalUSD5
maximum per cell and18,480 logical/55,440 physical campaign maxima. Recoveries share the original
cell allocation and remaining quotas. Execute in frozen order (Full44/49/50, then Neither49/50/44,
Linking49/50/44, Evolution49/50/44), reconcile each cell and reforecast from measured Run2 stage costs
before the next. No quality-based selection, extra provider policy, semantic retry, JSON repair,
contingency use or automatic top-up is authorized. All557 Run1 artifacts and USD8.530133 ledger bytes
verify unchanged. No paid Run2 request existed at this freeze checkpoint.

### Run2 outcome — first cell stopped on unknown transport usage

PR#26 merged normally as `207eac03fb92e32fb4d0571cd67359da6875463d`; the final independent freeze
audit passed and only approval metadata changed in the approved copy. Cell0
`run2-full-conv-44-r0-p0` then executed once under itsUSD5/1,666-logical/4,998-attempt limits.

At `D10:10`, shared logical454's first physical attempt454 returned HTTP200 but raised a body-read
`RemoteProtocolError` after60.529s, with no captured body/usage. The permitted SDK transport retry455
returned valid arguments after34.465s (3,611 input/2,822 output tokens); those unchanged arguments
completed note227/counter226. The first charge remains unknown and retains its fullUSD0.324404
reservation. Next-turn `D10:11` metadata was rejected before transmission by the durable financial
guard. This is not BLK-013, a confirmed timeout, malformed JSON or a settlement-retry defect.

The phase is **Incomplete**:227/675 notes, exact227×384 float32 stale index, zero/158 QA,
454 logical/455 physical calls. Known settled conservative costUSD0.720433 plus retained reservation
=USD1.044837 exposure. All1,278 real paid observations/230 traces verify in Langfuse, with partial
usage/cost explicitly labelled.140 D3a deviations/521 transformations and all original arguments
are retained. No `length` occurred; maximum successful shared output3,512 does not establish that
the larger cap fits later growth. Run1's557 files and USD8.530133 ledger remain byte-identical.

No continuation or later cell ran. BLK-022 is Investigating; a valid retry cannot establish that the
first attempt was unbilled. Exact state serialization restores offline without model/embedding calls,
but the current approval only permits automatic BLK-013 recovery and unknown-charge guards forbid
paid admission.448 turns/158 QA (1,212 logical/at most3,636 physical calls) remain hypothetically.
Seek request-level billing/usage first; if unavailable, a narrowly scoped upper-bound financial
adjudication and exact-state continuation require an explicit decision. Never edit the historical
attempt to fabricate usage, release its reservation or silently reuse the consumed phase.

The provider-only point forecast remainsUSD39.056674 including exposure, plusUSD8 protected reserve
=USD47.056674; incomplete Run2 stages still use Run1 cost proxies. It is not recovery authority.
Separately, the user upgraded Langfuse to Core, verified in the billing UI for a new3 November–
3 December period. Actual SDK offline capacity analysis projects221,508–235,524 normal campaign
units and approximatelyUSD9.72–10.84 incremental overage beyond100K included units; two continuations
per cell give a structural scenario nearUSD11.98. Scores are not the whole bill: SDK imports create
per-metric evaluator observations even when returning no value. Fees, discounts/tax, future failure
volume and allocation of service charges need a separate financial decision; no agent upgrade or
incremental overage grant is inferred. If these fees shareUSD42, the current whole campaign forecast
does not fit. Preserve the population, model, settings and reserve while resolving the budget.

See [the stopping report](run2-first-cell-incomplete-20261103.md),
[BLK-022](blockers.md#blk-022), the immutable first phase and
`artifacts/run2/transport-incident.json`. Corrected/historical quality metrics and published-ablation
comparisons are unavailable; no partial or Run1 result substitutes for a complete Run2 condition.

Final post-incident verification: the test-only HTTP200 body-read regression and full offline suite
pass716 tests/92 subtests (17 expected warnings). Independent Standards/Spec audits confirm correct
SDK retry/unknown-charge stopping, exact state/cloud proof and the SDK unit forecast. PR#27 records
the outcome. Neither verification nor its merge settles the unknown usage or grants a new paid phase.

### Authorization — BLK-022 one-off retained-upper-bound adjudication and offline recovery preparation

On3 November2026 the user authorized an isolated-branch PR to investigate BLK-022 and prepare
continuation, explicitly excluding new paid requests, automatic merge and additional Langfuse
spending. The unknown first physical454 may be adjudicated only by retaining its fullUSD0.324404
exposure and unknown status, with an explicit incident-specific financial record. Confirmed metered
conservative charges remainUSD0.720433; total conservative exposureUSD1.044837. The originalUSD5
cell cap, USD42 usable campaign allocation and protectedUSD8 remain unchanged. A valid retry is
not proof of unbilled usage; no authoritative first-attempt reconciliation was found.

Implement fixed `run2-blk022-attempt454-upper-bound-v1` admission, preserving all original rows,
raw response/phase evidence and cost sums. A financial-only receipt distinguishes the one retained
adjudicated unknown from every future blocking unknown; it must never become paid authority.
Prepare `run2-blk022-exact227-state-v1`:227 ordered notes/counter226, exact stale float32 index,
successful D10:10 decision retained, next turnD10:11,448 turns/158 QA remaining. The child plan
stays unapproved and bounded by1,212 new logical/3,636 physical calls and residualUSD3.955163.
The current support migration is restricted to the two reviewed Run2 incident/control modules;
all scientific files/assets/settings and the historical source receipt remain pinned.

Investigate lower-cost Langfuse observation/export options without dropping required auditability.
The existingUSD9.72–10.84 normal overage forecast has a possible offline-verified reduction to
approximatelyUSD1.53–2.65 after the current displayed-period usage adjustment. This is a proposed
prospective export policy, not an adopted change, cloud GateB proof, budget allocation or guarantee.
No additional cloud ingestion or service fee is authorized. A displayed unexpired original project
key is potentially compromised; document safe user-only replacement/revocation steps and redacted
operator tooling. No agent rotation or use of the exposed value is authorized or performed.

Keep Run1/Run2 archives and ledgers immutable; no model, prompt, schema, parsing, retrieval, action,
counter, scoring, generation or population change is permitted. Current scope ends at reviewed PR
and offline readiness evidence. See [recovery preparation](blk022-recovery-preparation.md),
[BLK-022](blockers.md#blk-022), [affordability](blockers.md#blk-009) and
[credential security](blockers.md#blk-023) for implementation, costs and remaining gates.

### Authorization — essential Run2 observations and one BLK-022 paid child

On3 November2026 the user confirmed PR#28 merged and private Langfuse rotation, then authorized
engineering, independent reviews, normal merge, exactly one paid checkpoint continuation and an
outcome-documentation PR/merge. Preserve all historical Run1/Run2 artifacts and the original ledger.
The grant supersedes the earlier preparation-only boundary for this child; it grants no later cell,
additional paid recovery, top-up, contingency use or scientific change.

Verify new project authentication/existing-trace access and old-key revocation with safe evidence;
do not regenerate keys. Adopt the smallest verified observability cost policy retaining generations,
usage/latency/errors, identities, actions, retrieval/answers, complete question-level Experiments,
checkpoint/degradation and authoritative local journals. Freeze `run2-audit-essential-v1`, successful
import-bookkeeping filtering, omission of duplicate original Scores and redundant wire envelopes,
and a30K original-observation fail-closed phase ceiling. Preserve prompts/schema/raw argument strings,
all metric values and original algorithm/settings. Offline equivalence and actual cloud GateB must
pass, with source-bound preflight and independent Standards/Spec reviews before paid execution.

Authorize child `run2-full-conv-44-r0-p1` from exactly227 ordered notes/counter226/stale index, nextD10:11:
448 turns and all158 questions; maximum1,212 new logical calls/3,636 attempts andUSD3.955163 new
conservative spending. Retain knownUSD0.720433 plus unknownUSD0.324404 =USD1.044837 exposure, original
USD5 cell, fresh Run2 USD50 ceiling/USD8 protected reserve and all historical accounting. Generate a
new single-use approval bound to the merged source, dataset/model, secured policy gate and exact
checkpoint. A forecast above the remainder prohibits transmission. Never repair/regenerate history.

New unknown usage, authentication/ingestion, provenance or financial-control failure stops. Use only
already reviewed recovery capabilities; this financial lineage has no further supported child, and
the one-shot launcher never loops. Any length exhaustion therefore preserves fallback/evidence and
stops without inventing another continuation. No semantic retries or scientific-setting changes.

For this child the policy's structural capacity check fits included Langfuse units without extra
overage: at most79,833 units including conservative original/import/existing/verification capacity.
No additional service charge or upgrade is committed. Normal whole-campaign provider/service/reserve
pointUSD48.731314–49.798114 remains conditional and tight; reforecast from this completed cell before
requesting another scope. Stop after verified completion or a material failure, preserve incurred
charges and failures, update blockers/report/forecast and merge the outcome documentation.
See [release specification and evidence](run2-observation-policy.md).

### Outcome — sole BLK-022 observed child consumed, Run2 stopped on BLK-014

PR#29 merged as `afcecdbbfddbc6bc06bdbd4f2524dd58692dedac` after764 tests/92 subtests, exact
original/full-candidate archive replays, source-bound real-runner GateB and independent Standards/Spec
reviews. Rotated credential authentication/readback and original-pair absence are verified without
exposing or retesting the old key. The essential policy is frozen and the financial exception remains
limited to original unknown attempt454/fullUSD0.324404 reservation.

The fresh approval `8854d11c-3202-4c38-948b-409c4be350f4` authorized exactly child
`run2-full-conv-44-r0-p1`. It restored227 notes/counter226/stale index and resumedD10:11. AtD24:12,
a normally finished shared decision (`tool_calls`,3,016 output tokens below8,192) returned malformed
JSON. Strict rejection/original fallback are preserved; no semantic retry or repair occurred.
The child stops Incomplete at566 notes/counter564, zero of158 QA. BLK-014 is reopened Open; this is
not BLK-013 output exhaustion. All2,048 child observations/483 traces verify in Langfuse, including
the failure. No primary quality scores or Experiments exist.

New678 logical/physical calls costUSD1.325173. Combined1,132 logical/1,133 physical attempts have
knownUSD2.045606 +retained unknownUSD0.324404 =USD2.370010 exposure. Cell remainderUSD2.629990;
Run1's USD8.530133 and all previous evidence remain unchanged. Cost-only provider pointUSD39.257657
for the full campaign still uses documented proxies (no completed Run2 cell); carrying the old
normal-service range andUSD8 reserve givesUSD48.932297–49.999097 before any new recovery or other
growth. This does not establish safe affordability. No contingency or extra Langfuse fee is committed.

The sole paid grant is consumed. Next turnD24:13;109 turns and158 questions remain (534 logical
calls). Existing financial recovery supports only the consumed227-note prefix. A new exact566-note
checkpoint extension and another bounded paid phase require a separate decision; neither is
authorized or implemented here. No later cell may start. The separately authorized outcome-
documentation PR/merge records this material stop without changing the scientific protocol.
Read [the complete verified outcome](run2-conv44-recovery-incomplete-20261103.md).

### Authorization — original evolution fallback and one exact566-note Run2 continuation

On3 November2026 the user authorized investigation, narrow implementation/offline tests, independent
reviews, normal merge and one new paid continuation from p1, plus an outcome-documentation PR/merge.
Verify the author's supported fallback before changing experiment-level fatality. Do not repair or
accept invalid JSON, retry a semantic decision, weaken schemas, or change scientific settings.

The verified scope is `run2-original-evolution-fallback-v1`: only normal, correctly identified strict
shared-decision syntax errors whose object-delimited text also fails the unchanged author cleanup.
Keep strict rejection/AdapterError and original fallback; verify complete memory/index/counter and
settled accounting before another transmission. Other stages, schema types, wrappers, length,
transport, storage, provenance, observability and financial failures stay terminal. A completed cell
with these failures is Degraded. This replaces excessive wrapper fatality for a supported author
fallback while preserving its effective algorithm and all prior Run2 state.

Authorize exact566-note/counter564/stale-index recovery from `run2-full-conv-44-r0-p1` atD24:13,
with both ancestors and all inherited failures/charges. Permit the smallest sequential checkpoint
extension, exclusive ownership, cumulative budgets and single-use approval. Historical sources are
validated against their own archived bindings; only the new candidate uses current release pins.

Exactly one fresh p2 paid phase:109 turns/158 questions,534 logical calls,1,602 physical attempts,
maximumUSD2.629990 additional conservative exposure. OriginalUSD5 cell and Run2USD50 ceiling/8
protected reserve remain; unknown454 retainsUSD0.324404 and existing exposureUSD2.370010 is not
reset. Require all offline/cloud/review/merge/preflight and conservative affordability gates before
transmission. No further actual recovery, later cell, additional budget or contingency use is granted.
See [verified design and execution boundary](run2-author-fallback-recovery.md).


### Outcome — exact566-note p2 consumed; local collection complete, Experiment release blocked

PR#31 merged as `66d3ffa6af82560d50658a9077439becc01681ba` after784 tests/92 subtests,
exact original/full-candidate archive replays, source-bound real-runner cloud GateB, network-disabled
preflight and clear independent Standards/Spec reviews. `run2-original-evolution-fallback-v1`
keeps strict rejection and the unchanged author catch, then verifies state/settlement/tracing before
further transmission; provider malformed-output reliability is not repaired.

Fresh approval `94021561-b115-4e79-83db-de93e3464c4f` is consumed. Sole p2 restores566 notes/counter564,
resumesD24:13 and collects109 new turns plus158 QA: final675 notes/counter673. All534 logical/physical
requests settle once, zero retries/new malformed outputs/new unknown;80 new D3a deviations retain
original argument strings. Inherited failures/unknown charges and all historical artifacts persist.
P2USD1.796479 is withinUSD2.629990. Total Run2USD3.842085 known +USD0.324404 retained unknown
=USD4.166489; originalUSD5 cell remainderUSD0.833511. Run1 remains separateUSD8.530133.

All1,771 runtime observations/623 traces verify, but the sole saved-result Experiment export drops
two serialized155.6MB batches above64MiB. Both scoring views/readbacks fail visibility; partial
remote writes are unknown. The sealed phase is Incomplete (`run2_experiments_not_verified`),
not completedDegraded; do not change its receipt/halt/claim or silently release another cell.
BLK-014 is Mitigated at the tested fallback boundary; BLK-024 is Open for reporting-only recovery.
Offline SDK batching16 spans preserves all316 result roots/4,494 score callbacks and metadata,
with max9.06MB/zero oversized batches; it is a proposal, not implemented/live-verified recovery.

Measured Full-stage cost sensitivity projectsUSD48.235144 provider total (remaining11USD44.068655),
exceedingUSD42 execution allowance byUSD6.235144 before service fees. BLK-009 is reopened Open;
no population/design/settings/budget decision is inferred from quality. USD8 contingency is protected.
No further paid phase, additional import or frontier release is authorized. A separate explicit
reporting-only recovery/partial-write/acceptance decision and later cost-only budget decision are
needed. Read [complete evidence and local scores](run2-conv44-collected-export-blocked-20261103.md).
