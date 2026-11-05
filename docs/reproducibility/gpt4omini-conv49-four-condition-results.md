# Four matched A-MEM builds on LoCoMo conv-49

Linking Only scored highest on corrected overlap (36.41% F1 / 32.74% BLEU-1), while Neither answered the most adversarial questions correctly (29/40). Enabling both memory actions did not reproduce a consistent gain on this conversation. The matched interaction was −0.31 F1 points / −1.36 BLEU-1 points. These are four single builds on one shared question set.

## What changed between builds

Each condition processed the same 509 original turns, then answered the same 196 original questions in benchmark order. Full was the [previously accepted reference](gpt4omini-three-full-results.md). Evolution Only, Neither and Linking Only ran in that order, each from an empty memory store and cache, with a new run identity and a single-use financial approval. No earlier cell supplied memory construction or provider outputs to a later cell.

| Condition | Strengthen the new note (links and tags) | Update existing neighbours (contexts and tags) |
| --- | --- | --- |
| Full | Yes | Yes |
| Evolution Only | No | Yes |
| Neither | No | No |
| Linking Only | Yes | No |

All four used the same native author schemas and prompts, dated model `openai/gpt-4o-mini-2024-07-18` through OpenRouter, OpenAI as the only upstream with fallbacks disabled, temperature 0.7 (0.5 for adversarial answers), and output limits of 1,000 tokens for metadata, keywords and answering and 4,096 for shared evolution decisions. Construction used five neighbours; question retrieval started at k=10 with the author's linked-memory expansion. Both action gates come *after* the shared decision. The original insertion, counter, consolidation every 100 positive evolutions and stale retrieval-index behavior remained in place. See the [frozen specification](gpt4omini-conv49-ablation.md) and [action gates](t7-action-gates.md).

## Results

The primary scores are corrected author F1 / BLEU-1 in percent. Overall is the mean of the 196 individual question scores; categories have different sizes. On adversarial questions the author’s separate binary metric checks whether the answer declines to supply information missing from the conversation and avoids giving the trap answer.

| Questions | n | Full | Evolution Only | Neither | Linking Only |
| --- | --- | --- | --- | --- | --- |
| Overall | 196 | 35.17 / 31.40 | 35.26 / 31.80 | 36.19 / 31.78 | 36.41 / 32.74 |
| Multi-hop | 37 | 18.96 / 12.33 | 14.98 / 9.63 | 16.43 / 10.31 | 21.44 / 14.57 |
| Temporal | 33 | 31.12 / 28.90 | 37.51 / 36.89 | 31.93 / 28.80 | 33.40 / 31.31 |
| Open-domain | 13 | 29.84 / 30.29 | 13.85 / 13.45 | 22.05 / 22.97 | 23.31 / 23.70 |
| Single-hop | 73 | 33.21 / 27.85 | 30.99 / 25.06 | 29.70 / 22.65 | 32.34 / 27.13 |
| Adversarial | 40 | 58.85 / 57.95 | 66.92 / 66.39 | 74.42 / 73.65 | 64.42 / 63.89 |

Adversarial correctness: Full **22/40** (55%), Evolution Only **26/40** (65%), Neither **29/40** (72.5%) and Linking Only **25/40** (62.5%).

Each difference below is in percentage points: subtract the two scores for each original question, then average over the indicated questions. The interaction is (Full − Linking Only) − (Evolution Only − Neither), equivalently (Full − Evolution Only) − (Linking Only − Neither). It measures how much the observed difference for one mechanism changes when the other mechanism is on.

| Questions | Linking − Neither | Evolution − Neither | Full − Linking | Full − Evolution | Interaction |
| --- | --- | --- | --- | --- | --- |
| Overall | +0.22 / +0.95 | -0.93 / +0.02 | -1.23 / -1.34 | -0.09 / -0.40 | -0.31 / -1.36 |
| Multi-hop | +5.01 / +4.26 | -1.45 / -0.68 | -2.48 / -2.24 | +3.98 / +2.70 | -1.04 / -1.57 |
| Temporal | +1.47 / +2.50 | +5.58 / +8.08 | -2.28 / -2.40 | -6.40 / -7.98 | -7.86 / -10.48 |
| Open-domain | +1.26 / +0.73 | -8.20 / -9.52 | +6.53 / +6.59 | +15.99 / +16.84 | +14.73 / +16.11 |
| Single-hop | +2.64 / +4.48 | +1.29 / +2.41 | +0.87 / +0.72 | +2.22 / +2.79 | -0.42 / -1.70 |
| Adversarial | -10.00 / -9.76 | -7.50 / -7.26 | -5.58 / -5.94 | -8.08 / -8.44 | +1.92 / +1.32 |

Without neighbour updates, strengthening was associated with higher F1 and BLEU-1 in each of the four non-adversarial categories. Across those 156 questions, Linking Only − Neither was +2.84 / +3.70 points. On the 40 adversarial questions it was −10.00 / −9.76 points, leaving an overall difference of just +0.22 / +0.95. With neighbour updates enabled, the observed strengthening difference was −0.09 / −0.40 overall.

Without strengthening, neighbour updates produced little overall change in BLEU-1 (+0.02) and a lower F1 (−0.93). With strengthening enabled, both scores were lower (−1.23 / −1.34). The negative overall interaction does not hold in every category: temporal questions had an interaction of −7.86 / −10.48, whereas open-domain questions had +14.73 / +16.11. Open-domain contains only 13 questions.

### Historical scoring

The secondary historical policy rescored exactly the same predictions. Categories 1–4 are identical under the two policies; only the adversarial overlap reference changes. Corrected scoring rewards overlap with “Not mentioned in the conversation”; the historical scorer instead measures overlap with the supplied trap answer. The historical values below therefore account for the entire change in the overall scores and contrasts.

| Questions | n | Full | Evolution Only | Neither | Linking Only |
| --- | --- | --- | --- | --- | --- |
| Overall | 196 | 32.30 / 28.49 | 29.00 / 25.52 | 26.87 / 22.44 | 30.92 / 27.27 |
| Adversarial | 40 | 44.77 / 43.70 | 36.27 / 35.58 | 28.77 / 27.87 | 37.52 / 37.09 |

| Questions | Linking − Neither | Evolution − Neither | Full − Linking | Full − Evolution | Interaction |
| --- | --- | --- | --- | --- | --- |
| Overall | +4.05 / +4.83 | +2.13 / +3.07 | +1.38 / +1.22 | +3.30 / +2.98 | -0.75 / -1.85 |
| Adversarial | +8.75 / +9.22 | +7.50 / +7.71 | +7.25 / +6.61 | +8.50 / +8.12 | -0.25 / -1.10 |

Historical overlap ranks Full first overall, although it had the fewest correct adversarial responses. A positive historical adversarial contrast can mean greater overlap with an incorrect answer. The binary correctness counts are identical under both scoring policies.

## Comparison with the published ablation

Table 3 of the paper reports higher F1 and BLEU-1 for Linking Only than Neither, and higher scores again for Full, in all five categories. Evolution Only is an additional condition in this study. [A-MEM, Table 3](https://arxiv.org/html/2502.12110v11#S4.T3)

On corrected F1 and BLEU-1, conv-49 reproduced the full published ordering only for **open-domain and single-hop**. Linking Only exceeded Neither for both metrics in four of five categories; adversarial reversed. Full exceeded Linking Only for both metrics only in open-domain and single-hop; multi-hop, temporal and adversarial reversed. Under the secondary historical scoring, the adversarial ordering also matches the published direction. The historical scoring agreement does not imply better adversarial correctness.

Section 4.1 describes 7,512 QA pairs; the released ten-conversation file has 1,986, and the exact Table 3 question IDs are not identified. Our comparison is restricted to one conversation and 196 questions. Supplementary Table 8 lists GPT-4o-mini retrieval depths of 40/40/50/50/40 by category, while the exact retrieval setting used for Table 3 is not specified. We used the released default of 10 throughout. Absolute score differences therefore do not measure reproduction error on the same evaluation population. [A-MEM, evaluation and supplementary tables](https://arxiv.org/html/2502.12110v11)

## Scientific verification, failures and remote evidence

[PR #42](https://github.com/alistairkung/A-mem-reproducibility/pull/42) merged as `be5c9745e5226ac95ad56616c243dc53c3853e3d` after independent Standards and Spec reviews. The full offline suite passed 903 tests and 92 subtests. In deterministic replay of the fixed archive, the released author implementation and Full candidate matched on all 568 insertion states, 1,544 recorded calls, 204 answers, both scoring views and failure provenance. That verifies Full equivalence on known inputs; it does not make fresh stochastic builds deterministic. Fault tests covered supported checkpoint continuation, strict routing, budget exhaustion and unknown-charge retention. The full-size reporting proof used 50 bounded batches for both scoring views of conv-49 (392 items, 5,568 scores); independent cloud verification followed each real cell.

| Cell | Strengthen | Update neighbour | Existing notes changed (events) | Retrieved entries (range) |
| --- | --- | --- | --- | --- |
| Full | 495 | 178 | 252 | 18–23 |
| Evolution Only | 0 | 175 | 221 | 10 |
| Neither | 0 | 0 | 0 | 10 |
| Linking Only | 497 | 0 | 0 | 18–25 |

There were 509 metadata generations, 509 shared decisions, 196 keyword generations and 196 answer generations in **each** condition: 1,410 settled requests per cell, 4,230 new and 5,640 across the four runs. All four built 509 notes and reached counter 509; the original consolidation boundaries were 100, 200, 300, 400 and 500. Both reviewers checked the ordered inputs, independent caches, action fields, final memory/index and scoring. Re-encoding each saved retrieval corpus on CPU reproduced its 509 × 384 float32 index exactly. No ablation reused Full construction outputs. There were zero provider failures, malformed decisions, output exhaustions, recovery children or scoring failures in these four benchmark runs.

Evolution Only suppressed 499 proposed strengthening actions; Neither suppressed 496 strengthening and 185 neighbour actions. Linking Only suppressed 187 neighbour actions and finished with 529 link entries across 496 notes. In the two cells without neighbour updates, existing note contexts and tags remained as built. In the two cells without strengthening, links remained empty. One applied neighbour action can change more than one existing note; the table counts such changes per turn, including repeat changes to a note across turns. Retrieval counts include duplicate entries in the author’s linked expansion. Every question started at 10 entries; all 196 expanded in both cells with strengthening. This is visible in provider usage: the 196 answer prompts used 511,652 input tokens in Linking Only and 500,782 in Full, compared with 252,355 in Neither and 252,619 in Evolution Only.

| Cell | Runtime observations | Runtime traces | Items | Scores | Original QA links | Experiments |
| --- | --- | --- | --- | --- | --- | --- |
| Full | 3183 | 708 | 392 | 5568 | 196 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=548dc7ac3e4313b8) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=20e5a01c0f078a2b) |
| Evolution Only | 2685 | 708 | 392 | 5568 | 196 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=08a0e6f298cd60be) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=1482f918f8de0a32) |
| Neither | 2510 | 708 | 392 | 5568 | 196 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=ffb8015ce0c3a1fb) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=210a29a1178dde3d) |
| Linking Only | 3007 | 708 | 392 | 5568 | 196 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=3e0ff28564f58b74) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=a8f94a670e20e9e7) |

Remote verification matched original generation inputs and outputs, usage, timing and provider identity; applied local actions; retrieval and answer traces; and each question's reference, numeric scores, metric names and original trace ID in both Experiments.

All four scientific classifications are **Clean**. Initial remote snapshots contained all 392 items but only some embedded scores: Full showed 5,162 and then 5,567; Evolution Only 5,200; Neither 5,025; Linking Only 5,079 and then 5,565. Subsequent readback verified all 5,568 in each cell, without new inference or re-import. Those transient reads and the final authoritative records were retained.

A separate OpenRouter billing GET timed out (HTTP 408) after Evolution Only had sealed. It concerned a historical Full / conv-50 generation that was already settled. A reviewed, read-only recovery preserved the original journal and error, checked its 3,818 successful rows, and finished reconciliation of all 6,035 generation IDs. There was no repeated inference, extra charge or new unknown. Neither and Linking Only completed their ordinary reconciliations. See [BLK-026](blockers.md#blk-026).

## Cost and limits

| Collection | Identified charges (US$) | Conservative exposure (US$) |
| --- | --- | --- |
| Full | 0.31996545 | 0.320705 |
| Evolution Only | 0.28014945 | 0.280813 |
| Neither | 0.27892170 | 0.279592 |
| Linking Only | 0.32385990 | 0.324609 |
| **Three new cells** | **0.88293105** | **0.885014** |

The four conv-49 builds together account for US$1.205719 conservative exposure. Full / conv-49 is already included in the **US$1.147803** opening campaign exposure. Adding only the three new builds gives **US$2.032817 conservative** and **US$1.96951635 identified** across all GPT-4o-mini compatibility and collection work. Each new build finished below the US$5 per-cell cap and the US$0.3376 planning estimate. All 8,855 settled generation IDs were reconciled against native token usage, upstream OpenAI route, and cost. Three earlier compatibility denials still carry their full US$0.058950 unknown-charge reservation; there are no new unknowns or unexplained account movements.

Closing prepaid credit was **US$48.01883265** and the key allowance was **US$48.03048365**. Unused conservative capacity under the planned US$42 was **US$39.967183**; the protected US$8 was untouched. No top-up occurred. The DeepSeek Run1 and Run2 ledgers remain separate.

Langfuse counted 10,137 units for Evolution Only, 9,962 for Neither and 10,459 for Linking Only (30,558 total), plus 1,252 for release verification. The final organization view showed **88,671** units; conservative usage was **88,674 / 100,000**. The existing Core subscription was US$29; incremental service overage was **US$0**. No plan change or overage was authorized. [Langfuse pricing](https://langfuse.com/pricing)

## Interpretation and next experiment

The traces establish that enabling strengthening created links and expanded retrieved context. Extra retrieved entries did not translate into uniformly better answers. Strengthening also changes new-note tags, so this comparison cannot attribute a score difference to link expansion alone. The same limitation applies to existing-neighbour context and tag changes. Matching question IDs removes differences in question mix; it does not remove variability in generated metadata, decisions, keywords or answers. All 196 questions in a condition share one stochastic memory build. These estimates do not establish a causal effect, statistical confidence or generalization to other conversations.

The next useful comparison is the same four-condition design on conv-44 and conv-50. Their Full baselines already exist, so six additional fresh ablation builds would bring the matched population from 196 to 558 questions across three conversations. That would show whether the observed directions persist across conversations. Repeated independent builds would still be needed to characterize generation variability. This campaign authorized neither expansion nor repetitions.

The [matched question scores](gpt4omini-conv49-question-scores.jsonl) contain all 196 original IDs, categories, both overlap scores under both references, and binary correctness for category 5. Values are fractions; average them before multiplying by 100. No prompts, responses, credentials or account identifiers are included.

With the private sealed campaign mounted in its original checkout, the [analysis command](../../scripts/gpt4omini-conv49-analysis.py) verifies both acceptances and the financial journal for each cell before reading its scores. Use unused output paths:

```sh
python scripts/gpt4omini-conv49-analysis.py artifacts/gpt4omini analysis.json --public-scores scores.jsonl
```

Independent acceptance and sealed phase SHA-256 prefixes:

| Cell | Spec | Standards | Phase |
| --- | --- | --- | --- |
| Full | 7977f5ab9c4d | f005147cd15b | 92fe3b717e81 |
| Evolution Only | a83b8dea0dbc | 1cb1ca163f2e | eafd6e232a91 |
| Neither | b019c25397e2 | 13e9c0a95e3b | 7011d1d06e83 |
| Linking Only | d0738dd433a8 | 642db4b72a55 | c78aab22d002 |

Full-precision analysis SHA-256: `009433a483f1255d4bb5fe0ef9b17de3c390fe03f21cceb793536b40023d67b2`. Public scores SHA-256: `54aec59012e4f7f912b30cddb90c29b94babcd5bd883eb375196e654e484ef02`. The three single-use approvals are consumed; the final frontier releases no additional cell.
