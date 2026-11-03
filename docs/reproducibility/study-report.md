# Controlled reproduction of A-MEM — report material

Working report material for FTEC5660, intended to fit within10 pages after final formatting. Results
remain explicitly partial until all selected cells verify; this document does not claim completion.

## Research question

We reproduce released A-MEM behaviour and test whether its two released memory actions contribute
independently to answer quality. The isolated modification independently enables strengthening and
neighbour updates while preserving the shared decision and the rest of the original algorithm.
Evolution-only is the fourth condition, additional to the three conditions reported in Table3.

The reference is author revision `f9a173d` and `test_advanced.py`, interpreted against
[A-MEM arXiv v11](https://arxiv.org/html/2502.12110v11). The paper reports GPT-4o-mini experiments;
we substitute DeepSeek Flash consistently. Released data/code, model, retrieval defaults and scoring
history differ, so our absolute scores cannot directly confirm or refute the published scores.

## Published comparison

Table3 reports the following F1/BLEU-1 percentages. These are published values, not our measurements.

| Condition | Multi-hop | Temporal | Open-domain | Single-hop | Adversarial |
| --- | --- | --- | --- | --- | --- |
| Neither (w/o LG & ME) |9.65 /7.09 |24.55 /19.48 |7.77 /6.70 |13.28 /10.30 |15.32 /18.02 |
| Linking only (w/o ME) |21.35 /15.13 |31.24 /27.31 |10.13 /10.85 |39.17 /34.70 |44.16 /45.33 |
| Full A-MEM |27.02 /20.09 |45.85 /36.67 |12.14 /12.00 |44.65 /37.06 |50.03 /49.47 |

Source: [paper Table3](https://arxiv.org/html/2502.12110v11#S4.T3). Our operational ablations are not
verified copies of unavailable author ablation code. Historical adversarial overlap scores are not
evidence of factual correctness.

## Experimental protocol

The released dataset is frozen by SHA256
`79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`:
10 conversations,5,882 turns and1,986 QA. The paper describes7,512 QA; the mapping to this release
is unavailable (BLK-003). We activate the previously specified cost-only fallback, not a selection
based on accuracy: conv-49, conv-50, conv-44,1,752 turns and558 questions. All questions remain.
One fresh build per conversation/condition is planned; repeated cached QA is not another build trial.

| Condition | Strengthening | Neighbour updates |
| --- | --- | --- |
| Neither | Off | Off |
| Linking only | On | Off |
| Evolution only | Off | On |
| Full | On | On |

Strengthening includes directed links and new-note tag enrichment. Neighbour updates rewrite existing
contexts/tags. Initial metadata and shared decisions remain in every condition. Every valid positive
decision increments the counter, including when all proposed actions are disabled; negatives and
original failed processing do not. Consolidation remains every100 positives, with stale embeddings
between consolidations and immediate refresh disabled.

We fix answer retrieval at10 initial notes and construction neighbours at5. Linked expansion retains
duplicates and original context, without truncation. Local tokenizer counts use a pinned asset;
hosted tokenizer parity is unverified (BLK-008), so API usage is the authority for prompt tokens.
All runs use `deepseek-flash`, the beta endpoint, thinking disabled, temperature0.7 except category5
answers at0.5,1,000 output tokens except shared decisions at4,000 under approved D9a. Request/response
metadata, retries, costs, failures and action outcomes are retained with phase/cache provenance.

## Implementation validity

Frozen author files remain untouched. T7 derives exactly two fixed Boolean guards in `_evolve` and
binds the method per instance; all original parsing/validation/action bodies, counter, indexing,
retrieval and scoring remain. Its96 action tests cover the matrix, failures, disabled positives and
99→100. Both the frozen reference and actual full-mode candidate match1,544 recorded requests,
568 per-insertion comparison hashes, historical states at263/568,204 QA, both scoring views and376
failure/audit records. See [T7 receipts](t7-action-gates.md).

Only UUID/access-time identities are normalized in memory comparisons. T6 intermediate hashes are
explicitly derived reference oracles, not independent historical snapshots; historical query vectors
were not recorded (BLK-015). Exact numeric replay was verified on the pinned local CPU runtime and
does not imply arbitrary cross-platform equality or stochastic equivalence.

## Evaluation and collection status

Primary metrics are the authors' corrected per-category F1 and BLEU-1; category5 adversarial correctness
is reported separately. Historical scoring is a labelled secondary view of identical saved predictions
and question IDs, with no new generation. Other author metrics and computation failures remain diagnostics.
Aggregation uses individual question scores, rather than averaging differently sized conversations.

The verified conv-50 full-mode lineage provides204 QA and568 notes. It is Degraded: the original
malformed evolution response and374 audited D3a deviations remain. Its corrected F1/BLEU-1 means are
0.482178 /0.435322; historical means0.417370 /0.371892. Category5 correctness is29/46. These are
single-conversation baseline observations, not fallback-population or four-condition results.
Detailed category values and evidence are in [the baseline report](t5-conv50-baseline-20261101.md).

T8 collection, paired condition tables and comparative interpretation are pending. A missing/incomplete
cell must remain explicit; no balanced population-quality conclusion is permitted until all558
question identities verify in each condition. One build per cell supports descriptive results only,
without claims of stochastic robustness or statistically established superiority.

The first T8 full conv-49 cell stopped before QA:413/509 notes, counter411, zero of196 questions.
Its shared decision at `D22:2` exhausted D9a4,000 tokens (`finish_reason=length`); BLK-013 is reopened.
Strict rejection and the spending halt worked. The partial state, raw response and270 prior D3a
deviations remain archived; no recovery or later cell ran. This is a reproduction challenge, not an
accuracy result. [Exact investigation and choices](t8-execution.md#paid-hold--blk-013-recurrence).

The subsequently authorized checkpoint child completed conv-49 without changing settings:509 notes,
196 QA, counter507, Degraded with the original failure retained. Corrected overall F1/BLEU-1 are
49.63%/46.31%, with category5 correctness27/40. These are conv-49-only descriptive results; the
selected-population baseline still needs conv-44, and no paired ablation result exists yet.
[Verified per-category results and evidence](t8-conv49-baseline-20261103.md).

## Practical challenges and debug diary

| Blocker | Investigation and response | Evidence or remaining limitation |
| --- | --- | --- |
| BLK-002 missing ablation runners | Trace released action boundaries; add two independent guards | T7 full-mode candidate replay passes; historical author ablation code unavailable |
| BLK-007 integer-string indices | Compare original `as_index`; validate a temporary schema copy only | Raw strings unchanged; narrow D3a audit; affected runs Degraded |
| BLK-013 output exhaustion | Preserve truncated response; approve shared-only4,000 cap uniformly | Fixture/conv-50 succeed; full conv-49 later reaches4,000 and halts; blocker reopened |
| BLK-014 malformed strict JSON | Offline replay proves provider contract failure; reject repair | Approved exact checkpoint recovery completes baseline with inherited degradation |
| BLK-016 persistence false positive | Reproduce benign corpus-text key as credential-field rejection | Narrow typed-map validation view; exact historical cache proof and final519-test/92-subtest suite pass |
| BLK-017 critical provenance failures | Inject invalid provider identity and durable-record failures | Terminal halt preserves evidence; optional reporting remains separate; independent reviews pass |
| BLK-018 completion-publication race | Interleave next-cell claim with failed receipt publication | SQL lock spans publication/readback; failure markers block continuation; six safeguards pass independently |
| BLK-004 scoring history | Rescore saved outputs using both author policies | Distinct references explain c5 differences; historical overlap is not correctness |
| BLK-009 costs and failures | Retain durable pre-request reservations/attempts, forecast fixed fallback | Hard USD50 total including USD8 reserve; no automatic paid recovery |

The append-only [blocker tracker](blockers.md) holds confirmed causes, hypotheses, unsuccessful attempts,
commits and tests. Provider-side reasons for strict-mode failures remain unknown; offline fixes do not
prove a provider guarantee. Dataset/retrieval differences and a mutable hosted model alias limit attribution.

## Computational cost and evidence

Before T8, the study spent conservative USD3.025799 across1,610 settled physical attempts. Full conv-50
construction/QA accounts for USD2.958514; previous compatibility attempts are retained overhead.
The incomplete T8 cell adds USD1.413246/826 attempts (metadata USD0.140616, shared decisions
USD1.272630); cumulative USD4.439045/2,436 attempts, zero retries in that cell and zero unknown charges.
The whole-fresh-cell point forecast now totals USD44.183331 including incurred costs and USD8 reserve;
this grants no recovery authority and does not credit the incomplete build as a completed cell.
After the separately approved child, cumulative cost is USD6.289898/3,020 settled attempts, zero
unknown charges. Combined conv-49 cost is USD3.264099 once. The remaining balanced point forecast
is now USD45.978600 including incurred spending and USD8 reserve; further paid cells are unapproved.
The subsequently authorized full conv-44 phase stopped Incomplete at424 notes/zero QA, adding
USD1.415538/848 calls after another4,000-token shared-decision truncation (BLK-013).
Current cumulative cost is USD7.705436/3,868 settled requests, zero unknown charges. Completed
conv-49/conv-50 evidence is unchanged; conv-44 F1/BLEU-1 are unavailable. The whole-fresh-cell
scenario now totals USD47.394138 including reserve, but grants no restart/recovery authority.
First-ablation readiness remains blocked; [verified failure](t8-conv44-incomplete-20261103.md).
The separately approved exact-state conv-44 child restored424 notes/counter422 and processed186
more turns before another4,000-token exhaustion at `D26:18`. It retains610 notes/counter607, both
failed decisions and zero QA; no full conv-44 quality metric is available. Child USD0.702421/372
calls; combined lineage USD2.117959/1,220; cumulative USD8.407857/4,240, zero unknown charges.
All inherited failures/deviations and original completed baselines remain unchanged. Current
whole-fresh-cell scenario: USD48.096559 including incurred charges and USD8 reserve. No further
recovery chain or ablation was authorized at that checkpoint; [verified child outcome](t8-conv44-recovery-incomplete-20261103.md).
The subsequently authorized second continuation, after PR#22 merge `5ddc96e`, restored610 notes/
counter607/exact stale index and processed26 more turns before another BLK-013 exhaustion at `D26:44`.
The lineage now preserves636 notes/counter632, all three failed decisions and zero of158 QA.
New52 requests/USD0.122276; combined conv-44 lineage1,272/USD2.240235; cumulative4,292/USD8.530133,
zero unknown charges. Root and independent audits preserve original baseline/ancestor/ledger evidence;
no complete cache or quality metrics exist for conv-44.39 turns/158 QA remain, next `D26:45`.
Current whole-fresh-cell point scenario is USD48.218835; hypothetical preserved-suffix scenario is
USD46.246007, each including incurred costs, nine ablations and USD8 reserve. The latter's suffix
estimate is USD1.282387 for394 logical calls. These are cost-only arithmetic, not upper bounds or
spending/recovery approvals. Third recovery is unsupported/unauthorized; first-ablation readiness
remains blocked. See [verified second-continuation outcome](t8-conv44-second-recovery-incomplete-20261103.md).
The original token-based forecast puts all ten conversations/four conditions at USD127.391486 and
the frozen fallback at USD42.762234 including incurred spending and contingency. Its2× cost sensitivity
exceeds USD50: the estimate is not a spending guarantee. T8 will reconcile actual stage costs and
remaining balanced scope before each phase, retaining all failed/partial costs.

Metadata, shared decisions, query keywords and QA generation are charged separately. Strengthening
and neighbour updates are local operations, not additional model calls. Suppressed shared-decision
outputs retain cost intentionally for experimental control. Imported Langfuse experiment timing is
not original inference latency/cost; authoritative local events/ledger supply those observations.

Reproducibility instructions, exact phase plans and artifact inventories: [T8 execution record](t8-execution.md).
Raw local runs/caches/receipts remain immutable and ignored by Git; compact manifests, code, tests,
provenance references and safe report material are versioned. Credentials and the separate HW3
repository remain outside this work. Final results, conclusions and cumulative costs must be updated
from verified T8 evidence before this working material is submitted.
