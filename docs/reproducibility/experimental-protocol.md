# Frozen A-MEM experimental protocol

Status: approved by the user on 1 November 2026 (Hong Kong time).
Protocol ID: amem-controlled-reproduction-v1.
Decision authority: [decisions.md](decisions.md).
Work breakdown: [implementation-tickets.md](implementation-tickets.md).

## Authorization boundary

Current authorization covers T5 engineering through baseline readiness, commits/pushes, offline tests
and reviews. PR #11 and the blocked-readiness documentation in PR #12 are merged. The user approved
[D9a](decisions.md#d9a--approved-shared-decision-output-allowance-and-one-fresh-verification-phase)
and the bounded D9a fixture has now succeeded with degradation solely from audited D3a deviations.
PR #13 is merged as `c659856`. The user then authorized one conv-50 pilot under the frozen plan:
USD10, 1,544 logical calls and at most 4,632 attempts. It is now incomplete after a normally finished
but malformed provider response (BLK-014); its approval and all compatibility approvals are consumed.
See the [pilot record](t5-pilot-conv50-d9a-20261101.md). Preserve partial results and charges; a complete
cost-only scope forecast is blocked by missing QA coverage. Further paid recovery, main execution and
T6–T8 require separate decisions. Stop after recording this pilot and budget status.
The user subsequently authorized checkpoint recovery implementation/offline tests and a PR, preserving
the exact 263-note failure state and strict validation; see [engineering authorization](decisions.md#authorization--blk-014-checkpoint-engineering-only).
The recovery approval must explicitly bind the reviewed support-code migration and new preflight to
the immutable parent. This granted no paid continuation, JSON repair or acceptance-policy exception.
Subsequently the user authorized PR #14's merge and one USD10 checkpoint child. That child has now
completed all568 turns/204 QA with inherited degradation; its approval is consumed. The cost-only
forecast recommends the frozen fallback (USD42.762234 including USD8 contingency), versus
USD127.391486 for all10 conversations. See the [verified outcome](t5-conv50-baseline-20261101.md).
Further collection, paid recovery and T6–T8 still require separate decisions.
On 2 November the user separately authorized offline T6 implementation, review, commits/push,
PR and merge based on the completed conv-50 lineage. See [T6 authorization](decisions.md#authorization--t6-deterministic-replay-on-the-completed-conv-50-lineage)
and [the replay gate](t6-replay.md). This does not authorize T7/T8, further paid collection or a
population change; T5 remains open for the remaining selected-conversation collection.
The user subsequently authorized T7 independent action gates, offline tests/reviews and merge after
both reference and actual full-mode candidate pass T6's fixed regression gate. See
[T7 authorization](decisions.md#authorization--t7-independent-action-gates) and [action-gate instructions](t7-action-gates.md).
This grants no T8 implementation, paid requests or additional collection.
Subsequently the user invoked implement-spec T8 and authorized paid main execution within the existing
ceiling/contingency. [Latest authority](decisions.md#authorization--t8-implementation-and-paid-main-execution)
activates D10a's fallback using the saved cost-only forecast; [T8 record](t8-execution.md) binds the
remaining eleven fresh cells, current provenance and phase controls. Recovery/repetitions remain separately gated.
Keep all work inside this repository; the separate FTEC5660 HW3 repository is out of scope.
Credentials stay in the environment and outside code, public records, logs and committed artifacts.

## Research question and authorities

Reproduce released A-MEM behavior, reconstruct its two missing published ablations, and add
evolution-only by independently gating the released strengthening and neighbor-update actions.

- Author source: `f9a173dec325d84fcc97e7828775c7b241c33466` (`f9a173d`).
- Authoritative baseline: `test_advanced.py`, its original memory implementation and scoring utilities.
- Published comparison: [A-MEM arXiv v11](https://arxiv.org/abs/2502.12110v11), Table 3.
- Dataset: `data/locomo10.json`.
- Dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`.

Describe this as a controlled cross-model reproduction. Released source/data and the historical paper
experiments may differ. Published GPT-4o-mini absolute scores are not directly comparable with DeepSeek.
The robust pipeline is a substantive variant and is not a substitute for this baseline.
Preserve the frozen author implementation; isolate provider, orchestration and observational additions.

Execution sequence:
1. Prepare compatibility contracts and collect/archive the original full-mode baseline after approval.
2. Establish deterministic replay and regression checks.
3. Refactor action execution into independent gates.
4. Prove original full-mode replay equivalence.
5. Reconstruct neither/linking-only and compare all three published conditions with Table 3.
6. Execute evolution-only as the fourth, novel condition.

## Model and provider contract

| Setting | Frozen value |
| --- | --- |
| Request model ID | `deepseek-flash` |
| Base URL | `https://api.deepseek.com/beta` |
| Completion route | `/chat/completions` |
| Thinking | Explicitly disabled |
| Metadata / shared decision / query-keyword temperature | 0.7 |
| Category 1–4 answer temperature | 0.7 |
| Category 5 answer temperature | 0.5 |
| Metadata / query-keyword / answer maximum output tokens | 1,000 |
| Shared-decision maximum output tokens | 4,000 under D9a; historical D9 was 1,000 |
| Output-token policy | `d9a-shared-decision-4000-v1` |
| Execution | Serial, non-streaming |
| Transport | Explicit 120-second timeout setting; at most two SDK retries (three attempts total) |
| Additional retries | No second retry layer, semantic repair, or answer-quality retries |

The retry policy covers transient transport/provider failures consistently across conditions;
record actual retryable statuses/exceptions, SDK version, backoff behavior and attempts in the manifest.
Bounded retries must be included in the approval and budget for each paid phase.
Retain existing caller failure/fallback behavior after exhausted retries.

D9a is a controlled generation-setting deviation made after a DeepSeek shared decision exhausted the
historical 1,000-token allowance (BLK-013). Preserve original prompts/schemas/parsers and author files;
use the same stage limits in every arm and label original failed results separately. Bind the output
policy and stage-cap map to approval, request validation, run/cache identity and reporting. Pricing
validation uses a 4,000-token bound, with per-attempt conservative reservations of 319,373 microUSD for
shared decisions and 315,773 for other stages. Phase/study caps and retry limits remain unchanged.
Offline verification and the D9a live fixture establish functional compatibility for the frozen
18-turn/four-question fixture. Its maximum shared-decision output was 1,572 tokens; a higher limit
does not establish that output growth will fit it throughout conv-50. Preserve the earlier failed
1,000-token runs and identify D9a as a controlled generation-setting deviation.

At discovery, the [provider model documentation](https://api-docs.deepseek.com/quick_start/pricing/)
mapped this identifier to DeepSeek-V4.1-Flash-1017. Record the actual request ID, endpoint, model-version
information, generation settings and returned fingerprint per run. The hosted alias does not guarantee
immutable weights; report observed changes before continuing a purportedly identical-model comparison.

Translate the original JSON-schema response contract into one forced strict function definition:
- Preserve original system/user messages, schema semantics and downstream parsers.
- Validate metadata, shared evolution, query-keyword and answer schemas against the provider's strict restrictions.
- Return the function argument string unchanged; execute no function and add no second generation turn.
- Preserve availability of the original OpenAI backend.
- Establish offline contracts before requesting paid compatibility approval.
- Stop and report any required schema-semantic changes.

Documentation supports this approach; live beta acceptance/reliability is unverified.

### Approved BLK-007 provider-acceptance addendum (D3a)

The separately approved `canonical-index-strings-v1` policy permits only canonical unsigned ASCII
integer strings (`0|[1-9][0-9]*`, parseable by Python `int`) in the shared decision's
`suggested_connections` list. The unchanged schema validates a temporary integer copy; the original
argument string goes unchanged to the original parser. All other types/fields/contracts remain strict.
The wire schema still requests integers, so an admitted response is recorded as a provider-contract
violation, not strict compliance. No additional model call, index filtering or semantic retry is added.

Bind the selected policy to phase approval, cache provenance and experiment/reporting identity. Use
one policy across all arms. Record affected fields, transformations, exact argument hashes and canonical
original/copy hashes. Affected completed runs are degraded; incomplete classification takes precedence.
Cached-build deviations remain visible and are counted separately from new calls. Default strict
rejection remains available. See [D3a](decisions.md#d3a--blk-007-validation-copy-compatibility-policy)
and [offline verification](blk-007-compatibility-review.md). This addendum authorizes offline
implementation/testing only; new live compatibility and subsequent paid phases need separate approval.
See [strict tools](https://api-docs.deepseek.com/guides/tool_calls/) and
[thinking mode](https://api-docs.deepseek.com/guides/thinking_mode/).

## Memory conditions and invariants

| Condition | Strengthening | Neighbor updates |
| --- | --- | --- |
| Neither | Off | Off |
| Linking only | On | Off |
| Full A-MEM | On | On |
| Evolution only | Off | On |

Initial note creation and generated metadata remain enabled throughout.
Strengthening includes directed links AND new-note tag updates. Linking-only therefore does not
isolate graph links from metadata enrichment. Neighbor updates change existing-note context/tags.
These are our operational reconstructions, not verified copies of unavailable author ablation code.

Preserve:
- Original shared evolution-decision logic, calls, prompts and schemas in all four conditions.
- Construction search over five neighbors; answer retrieval `retrieve_k=10`, with no evaluation-set tuning.
- Original embedding content, index-consolidation behavior and disabled immediate index refresh.
- Valid negative decision: no counter increment.
- Valid positive decision: increment once, even when all proposed actions are disabled or no action executes.
- Failed processing returning the original failure result: no increment.
- Consolidation every 100 positive decisions.

Fixed k=10 is the released runner default, not a verified match for the paper's category-specific settings.
Consolidation can affect retrieval even when actions are disabled. Do not optimize away the retained
decision calls or change consolidation timing.

## Populations, identities and scope selection

Primary: all 10 conversations, 5,882 turns and 1,986 QA.
Initial replication: one fresh memory build per selected conversation per condition.
This means 40 per-conversation stores for full scope, or 12 for the fallback, across four conditions.

Conditional fallback (D10a):

| Conversation | Original sample index | Turns | QA |
| --- | --- | --- | --- |
| conv-49 | 8 | 509 | 196 |
| conv-50 | 9 | 568 | 204 |
| conv-44 | 5 | 675 | 158 |
| Total | | 1,752 | 558 |

Selection: sort by (turn count, original ID), split sorted conversations into strata of 3/3/4,
and use one independent `random.Random(42)` instance to choose once per stratum in order. No redraws.
Category counts 1–5 are 99, 89, 27, 222 and 121.

Freeze full and fallback manifests before paid execution. Identify each QA by original conversation ID
and original zero-based QA-array index; preserve native IDs if present. Preserve original sample/QA
indices for author category-5 option-order seed derivation. Selection and option-order RNGs are separate.
Seed 42 controls selection/option ordering, not deterministic live model generation.

Functional fixture: conv-26's first complete session, all 18 turns and original QA indices 0,1,2,4.
Evidence for those four questions is contained in that session. This fixture is not an accuracy estimate.
Cost pilot: full-mode conv-50, all 568 turns and 204 QA.

Keep all questions and turns within the chosen conversations. No context truncation, deduplication,
model-setting changes, performance-based subset selection or evaluation-set tuning.
All conditions use identical evaluation identities/settings. Select full scope or the predefined fallback
from cost evidence alone before examining comparative performance.
Additional independent repetitions require a separate budget decision; three full repetitions are optional.
One repetition supports descriptive comparisons, not claims of stochastic robustness.

## Budget and approval gates

Overall planning ceiling: USD 50, including contingency.
- Compatibility and functional fixture: provisional USD 1–2, separate execution approval.
- Representative pilot: provisional USD 5–10, separate execution approval.
- Reserve USD 8 contingency in the total forecast.
- Main execution: separate approval within remaining budget.

Before main execution, forecast:
`incurred spending + remaining four-condition execution cost + USD 8 contingency <= USD 50`.

Use measured tokens, retries, context expansion and stage costs. Full-mode pilot cost is not a guaranteed
upper bound for other conditions. Reconcile forecasts as arm-specific measurements become available.
If neither full scope nor the predefined fallback fits, stop and request a revised decision.
Retain charges from failed/incomplete attempts; unknown charges are not zero.
Credit the pilot to the scored original full-mode baseline only when exact configuration, manifests and
provenance remain valid; otherwise its charges are overhead. Avoid counting a reusable pilot twice.

Nominal logical calls (before retries), including the shared decision in every condition:

| Work | Calls |
| --- | --- |
| Functional fixture | 44 |
| Full-mode conv-50 pilot | 1,544 (1,136 construction + 408 QA) |
| Full dataset, one condition | 15,736 |
| Full dataset, all four conditions once | 62,944 |
| Fallback, all four conditions once | 18,480 |

Calls do not determine dollars without token measurements. Preserve separate metadata, joint-decision,
query-keyword and answer usage/cost. Strengthening and neighbor updates execute locally after the joint
response: report their counts/latency, charge the generation once, and identify suppressed decision
outputs as overhead retained for experimental control.

## Cache and artifact protocol

Fingerprint dataset/identities, code/adapter, prompts/schemas, model/endpoint/generation settings,
memory condition, index policy and build repetition. Independent conditions and build repetitions have
isolated caches. Reuse requires an exact verified manifest match; stale state is rejected.

Save complete notes and corresponding corpus/embedding/index state together, completion markers,
and provenance. Canonical ordered snapshots preserve content, context, tags, keywords, link indices
and mappings, evolution decisions/outcomes, counters and applied/suppressed actions.

Execution types:
- Fresh build: memory-construction behavior and cost.
- Cached QA: answer performance conditional on that verified memory build.
- Deterministic replay: refactor equivalence using recorded model responses.

Repeated cached QA does not count as an independent memory-build trial. Preserve partial artifacts and
costs from aborted runs. Never use the old finished cache as proof that new construction is equivalent.

## Scoring, measurements and reporting

Use the authors' existing metric definitions and aggregation semantics.
- Primary: corrected reference policy; per-category F1 and BLEU-1 headlines.
- Category 5: report existing `adversarial_correct` separately.
- Secondary: exact match and the other existing author metrics.
- Historical reproduction view: existing legacy category-5 reference, clearly labelled.
- Both views use identical saved predictions, question IDs and reference data; rescoring makes no model calls.
- Historical adversarial overlap scores are not evidence of better factual answer quality.

Record explicit scoring-policy IDs in manifests, Langfuse records and tables. The implementation must
assign stable identifiers to the corrected and legacy policies and pin the scorer revision.

Per-question observations: initial retrieved note count, expanded entries including duplicates,
retrieved-context tokens with documented method/tokenizer revision, and API final prompt usage where
available. Distinguish tokenizer counts/estimates from API-reported usage; verify the counting method
before claiming actual model-token counts. Observations must not change context.

Prefer minimal Langfuse Experiments integration around existing author functions and results.
Record config, stable IDs, outputs/references, scores, failures/retries, tokens, cost and latency.
Keep local artifacts authoritative and preserve the evaluator. Do not add an LLM judge or replace the
evaluation framework. Pin a supported tested SDK; discovery candidate was Langfuse 5.1.0 / Python >=3.11.

## Failures and regression evidence

Preserve original failure and fallback outputs without silent repair. Record failures/retries at run,
memory-build and question levels. Distinguish genuine metric zeros from computation failures converted
to zero. Do not drop difficult questions or retry valid outputs because of low scores.

| Status | Meaning |
| --- | --- |
| Complete | All expected results present; no detected processing/scoring failure |
| Degraded | All expected results present; original fallbacks or metric failures occurred |
| Incomplete | Aborted execution or missing expected results |

Retain degraded results with limitations and transparent exclusions; preserve incomplete artifacts/costs
without presenting their aggregate as a completed benchmark. Paid recovery/reruns require separate approval.

Offline tests must cover:
- Four provider schemas, unchanged request/output contracts and bounded retry behavior.
- Provenance rejection, completion classification, failed metric reporting and original output preservation.
- Rescoring without model/network calls or prediction mutation.
- All four proposed action sets across four configurations (16 combinations), negative decisions,
  disabled-action positive decisions, failure paths and counter transition 99 to 100.
- Full-mode replay: request order/messages/schemas/settings; note transitions/links/metadata/counters;
  consolidation events; index corpus/row order/embeddings; retrieved context; predictions and scores.

Normalize incidental UUID/time values only in comparison views; preserve raw originals.
Deterministic replay verifies implementation equivalence. Independent live repetitions measure
stochastic variability; neither substitutes for the other.

## Coursework submission

Authoritative requirements were supplied by the user (D13). Deadline wording: 13 November 2026 at
midnight, Hong Kong time. Meaningful benchmark subsets and documented controlled DeepSeek substitution
are permitted. Three to five stochastic trials are recommended, not unconditional.

- [ ] Reproduce at least one reported result or behavior from a runnable agentic repository.
- [ ] Demonstrate one isolated, measurable modification.
- [ ] Report <=10 pages: target, deviations, protocol, quality, failures, cost and limitations.
- [ ] GitHub repository: reproducible instructions, locked dependencies, manifests, tests and reviewed commits.
- [ ] Evidence: original and modified artifacts, both scoring views, cost ledger and replay equivalence.
- [ ] Recorded presentation <=15 minutes.
- [ ] Credentials absent from code/logs/committed artifacts; separate HW3 repository untouched.
- [ ] Obtain commit/push/publication authorization when those actions are requested.

## Discovery references and limits

- [Author evaluation/memory fixes](https://github.com/WujiangXu/A-mem/commit/b31a1dddf56f87ec762cce3539418602d7e2ffb1)
  document changed category-5 scoring, memory repairs and index-refresh behavior.
- Paper reports 7,512 QA; the checked-in file contains 1,986. Historical evaluated population is unresolved.
- Paper Table 8 gives category-specific GPT-4o-mini k values, without explicitly binding them to Table 3.
- Current cache keys are insufficient for the approved protocol; test_advanced*.py are evaluation entrypoints,
  not an existing offline regression suite.
- Hosted model snapshots, historical memory checkpoints and the missing ablation implementations limit
  claims of exact historical reproduction. Preserve these limitations in the report.
