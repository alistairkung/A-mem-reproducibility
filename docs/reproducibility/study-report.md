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

## Practical challenges and debug diary

| Blocker | Investigation and response | Evidence or remaining limitation |
| --- | --- | --- |
| BLK-002 missing ablation runners | Trace released action boundaries; add two independent guards | T7 full-mode candidate replay passes; historical author ablation code unavailable |
| BLK-007 integer-string indices | Compare original `as_index`; validate a temporary schema copy only | Raw strings unchanged; narrow D3a audit; affected runs Degraded |
| BLK-013 output exhaustion | Preserve truncated response; approve shared-only4,000 cap uniformly | D9a fixture/conv-50 succeed; not a guarantee for all future memories |
| BLK-014 malformed strict JSON | Offline replay proves provider contract failure; reject repair | Approved exact checkpoint recovery completes baseline with inherited degradation |
| BLK-016 persistence false positive | Reproduce benign corpus-text key as credential-field rejection | Verify map structure before temporary validation view; preserve state; final T8 checks pending |
| BLK-004 scoring history | Rescore saved outputs using both author policies | Distinct references explain c5 differences; historical overlap is not correctness |
| BLK-009 costs and failures | Retain durable pre-request reservations/attempts, forecast fixed fallback | Hard USD50 total including USD8 reserve; no automatic paid recovery |

The append-only [blocker tracker](blockers.md) holds confirmed causes, hypotheses, unsuccessful attempts,
commits and tests. Provider-side reasons for strict-mode failures remain unknown; offline fixes do not
prove a provider guarantee. Dataset/retrieval differences and a mutable hosted model alias limit attribution.

## Computational cost and evidence

Before T8, the study spent conservative USD3.025799 across1,610 settled physical attempts. Full conv-50
construction/QA accounts for USD2.958514; previous compatibility attempts are retained overhead.
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
