# T8 conv-49 full-mode baseline — verified degraded lineage

Verified 3 November 2026, Hong Kong time. PR #17 merged normally as
`78ac46b57fd3b89bbf75a315565c945fbb9713be`; local main was synchronized before execution.
Author revision remains `f9a173d`. Source fingerprint:
`0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`.

## Outcome and integrity

The baseline is **Degraded and complete**: 509 original turns/outcomes,196 uniquely identified
questions in frozen order,509×384 finite float32 retrieval state and evolution counter507.
The original `conv-50` baseline and cache are byte-identical to the before-run inventory.
No remaining benchmark cell or additional recovery was executed.

| Segment | Status | Turns in segment | QA | Logical / physical calls | Conservative USD |
| --- | --- | ---: | ---: | ---: | ---: |
| `t8-full-conv49-r0-20261102` | Incomplete; immutable parent | 413 | 0 | 826 /826 | 1.413246 |
| `t8-full-conv49-checkpoint-child` | Degraded; complete child | 96 | 196 | 584 /584 | 1.850853 |
| Completed lineage | Degraded | 509 | 196 | 1,410 /1,410 | 3.264099 |

Fresh final checks passed 545 tests/92 subtests (16 intentional SDK malformed-metadata warnings),
64 focused checkpoint/adapter-budget tests and clear independent Standards/Spec reviews. GitHub
reported no required status/workflow/review-thread blocker and no applicable branch protection/rules;
no bypass was used. Current-source runtime preflight passed with network disabled.

Approval `a550491a-d027-4752-a959-3b6bcdc1e0f6` authorized only this child: USD3,584 logical calls,
at most1,752 attempts. It is consumed. Its immutable artifact is
`artifacts/t8/approvals/t8-full-conv49-checkpoint-child-20261103.json`.
The child restored all 413 notes, metadata, links, counter411 and exact stale embeddings, resumed
`D22:3`, and preserved failed `D22:2` without regenerating or repairing its response. Original
periodic consolidation occurred naturally at counter500, `D25:13`/overall note502; restoration
itself did not re-encode the checkpoint or change the refresh policy.

Degradation retains one original truncated shared decision, its evolution-failure notice and the
subsequent untransmitted metadata-block notice. The child added only72 approved D3a deviations/
276 validation-copy transformations; total lineage342 deviations/1,342 transformations. All1,409
accepted argument strings match provider bytes; the original rejected response remains unchanged.
There were zero new processing failures, metric failures, retries or unknown charges. No prompt,
schema, parser, action, retrieval, scoring, model or generation setting changed.

## Author-scored quality — conv-49 only

Scores below are percentages of the authors' existing per-question metric means. Primary policy:
`author-corrected-v1`. These are single-conversation cross-model baseline results, not the full558-QA
fallback or a comparison of conditions. The executor rescored saved predictions offline with the
existing author scorer; subsequent verification read those saved views and checked aggregation.
Neither operation made model calls or introduced new scoring logic.

| Category | Questions | F1 (%) | BLEU-1 (%) |
| --- | ---: | ---: | ---: |
| 1 | 37 | 33.73 | 26.30 |
| 2 | 33 | 43.91 | 45.57 |
| 3 | 13 | 27.14 | 26.10 |
| 4 | 73 | 55.51 | 50.70 |
| 5 | 40 | 65.63 | 64.00 |
| Overall | 196 | 49.63 | 46.31 |

Category5 `adversarial_correct` is **27/40 (67.50%)**, reported separately from overlap metrics.
Secondary author metrics remain in the saved results and CSV tables.

Historical policy `author-legacy-c5-v1` uses exactly the same predictions and original question/
reference data, changing only the historical category5 reference semantics. Categories1–4 match
the primary view. Category5 historical F1/BLEU-1 are34.22%/32.84%; historical overall values are
43.22%/39.95%. These are reproduction diagnostics, not alternative factual-correctness measures.
No prediction was changed or regenerated; zero metric-computation failures were found in either view.

## Usage, accounting and computational observations

| Generation stage, whole lineage | Logical calls | API prompt tokens | API output tokens | Conservative USD |
| --- | ---: | ---: | ---: | ---: |
| answer | 196 | 4,843,185 | 7,817 | 1.462418 |
| metadata | 509 | 285,553 | 72,705 | 0.173142 |
| query_keywords | 196 | 67,931 | 9,263 | 0.031586 |
| shared_decision | 509 | 1,508,982 | 953,360 | 1.596953 |

The lineage used6,705,651 API prompt tokens and1,043,145 output tokens. Shared decisions are charged
once; strengthening/neighbour updates are local actions with no additional model requests.
Per-question initial/expanded retrieval counts (including duplicates), local-tokenizer estimates,
API final prompt usage, action counts and latency remain in the event/CSV artifacts. Hosted/local
tokenizer equivalence remains unverified (BLK-008); API usage is authoritative for cost.

All 2,436 pre-existing attempt/logical rows and six pre-existing phase rows match the before-run
backup exactly. Parent halt/authority and earlier checkpoint claims remain intact. The original study
cell is owned by its completed child through the reviewed one-shot edge, not duplicated as another trial.
Cumulative conservative study spending is **USD6.289898 across3,020 settled requests**, zero unknown.
USD35.710102 remains usable under the USD42 execution limit, preserving USD8 of the USD50 ceiling.

Pricing was rechecked3 November: the existing peak cache-miss input/output bounds USD0.30/1.20 per
million tokens still apply to Flash. Ledger charges conservatively ignore cache/off-peak discounts;
they are not provider invoices. [Provider pricing](https://api-docs.deepseek.com/quick_start/pricing/).

## Cost-only forecast and next approval boundary

The frozen population stays `conv-49`, `conv-50`, `conv-44`, all turns/questions and four conditions,
one independent build per cell. Remaining work is full `conv-44` plus nine ablation cells:
15,526 logical generations. The cost-only ledger-stage forecast, including full parent prefixes once,
is **USD31.688702 remaining + USD6.289898 incurred + USD8 contingency = USD45.978600**.
This fits the planning ceiling with USD4.021400 forecast headroom; it is not an upper bound.
The2× remaining-cost sensitivity exceeds USD50. No population or order was selected using accuracy.

Current frozen ordering requires all selected full-mode baselines before ablations. The next executable
proposal is **Full conv-44**:675 turns/158 QA,1,666 logical calls, at most4,998 attempts,
point estimate USD3.255215, proposed hard additional ceiling **USD5**. It is **unapproved**:
`artifacts/t8/conv49-baseline-20261103/next-full44-plan.json`, SHA256
`dbf2064485722d092c6497614528fc869e0dabea97ec6e477095a1d0a6e921f6`.
No full-conv44 run, permit claim or approved artifact exists.

Prioritize **Neither conv-49** immediately after that prerequisite: a fresh independent509-turn build
and the same196 question IDs,1,410 logical calls/4,230 maximum attempts, current point estimate
USD2.989249. The current planner deliberately rejects it until full conv-44 completes. Running that
paired condition first would require an explicit sequencing amendment plus a newly reviewed plan;
no gate was relaxed, and no paid arm was launched. Retaining the frozen order is recommended.

Separate authorization must approve one full-conv44 phase under the exact proposed limits, same
cumulative ledger and unchanged D3a/D9a/settings, excluding recovery/repetition/other cells.
After that future approval only, materialize a fresh immutable approval and run from the repo root:

```sh
.venv/bin/python -m amem_repro.study run \
  --approval artifacts/t8/approvals/t8-full-conv44-r0-20261103.json \
  --receipt artifacts/t8/conv49-resume-preflight-20261103.json --assets artifacts/assets
```

That approval path is deliberately absent. Recheck source, assets, ledger, price bounds and affordability
before any later paid execution. The consumed child approval cannot fund another request.

## Preserved local evidence

- Parent: `artifacts/runs/t8-full-conv49-r0-20261102/`.
- Child: `artifacts/runs/t8-full-conv49-checkpoint-child/`: raw events, predictions/references,
  checkpoint, summary, complete phase inventory and both scoring views.
- Complete memory cache: `artifacts/cache/b7c3caaa6c09e0c1ee7e5806f3b7f20e9398eb6c99befe79e70dbeb99e0e6246/`.
- `artifacts/t8/conv49-baseline-20261103/verification.json`, `additional-integrity.json`,
  `stage-costs.json`, `cost-only-forecast.json`, `author-views/` and `selected-population-inventory/`.
- Immutable before/after SQLite backups: `artifacts/t8/conv49-resume-ledger-{before,after}-20261103.sqlite`;
  the actual cumulative ledger is `artifacts/study-budget.sqlite` and was never reset/replaced.
- Preflight/approval readiness and final tests: `artifacts/t8/conv49-resume-pre-execution-20261103.json`,
  `artifacts/t8/offline/conv49-resume-{full-suite,focused}-20261103.txt` and review receipts.

Raw artifacts stay local/ignored and contain no committed credentials. Authoritative local collection
is independent of optional Langfuse; no new cloud import or live tracing claim is made here.

## Remaining limitations and stopping condition

BLK-013 stays **Open**: the single checkpoint completed this degraded lineage, but does not resolve
output growth. Maximum new shared-decision output was3,982/4,000 tokens; another conversation can
exhaust the unchanged cap. BLK-007/014 remain Mitigated, BLK-008/011 remain Open, and the documented
data/retrieval limitations remain. One build supports descriptive findings, not stochastic robustness;
published GPT-4o-mini absolute scores are not directly comparable. No subset/configuration tuning or
quality-based retry occurred. T5 remains open for conv-44; T8 remains open for the ablation study.

The authorized child is complete and its grant consumed. Stop before every further paid cell/recovery.
