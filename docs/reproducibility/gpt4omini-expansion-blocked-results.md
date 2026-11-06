# GPT-4o-mini expansion on LoCoMo: eight accepted cells and one reporting stop

Evolution Only passed independent acceptance on both additional conversations. Full and Evolution Only now have comparable results for all 558 original questions. Full averaged 36.91% F1 and 32.81% BLEU-1, versus 35.86% and 32.29% for Evolution Only. Full led on both metrics on conv-50. On conv-44 it gained F1 but lost BLEU-1, and on conv-49 it scored slightly lower on both. These differences describe one stochastic build per cell.

Neither / conv-50 collected every turn and answer but failed exact Langfuse score verification. The frozen order stops there. Eight cells are independently accepted, one is Incomplete and three are unstarted. Full four-condition contrasts and the interaction across all three conversations therefore remain unavailable. The [four-condition conv-49 results](gpt4omini-conv49-four-condition-results.md) remain the accepted comparison for that conversation.

## Execution inventory

Pairs are F1 / BLEU-1 in percent. The Incomplete row displays local scores for diagnosis. Only accepted cells contribute to the comparisons below or to the [558 public question-level records](gpt4omini-expansion-accepted-scores.jsonl). Each public record contains numeric values only for its accepted conditions.

| Conversation | Condition | Status | Turns / QA | Corrected F1 / BLEU-1 (%) | Historical F1 / BLEU-1 (%) | Adversarial correct | Strengthen / neighbour | Mean retrieval entries | Experiments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv-44 | Full | Degraded | 675 / 158 | 39.50 / 34.52 | 38.58 / 33.70 | 18/35 | 665 / 227 | 19.96 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b4a39a3e02e2f361) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=bd8af7375fe2248e) |
| conv-44 | Evolution Only | Clean | 675 / 158 | 39.15 / 34.85 | 33.77 / 29.45 | 22/35 | 0 / 235 | 10.00 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=877089259f1d95e1) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=6374428c15b01ed1) |
| conv-44 | Neither | Unstarted | — | — | — | — | — | — | — |
| conv-44 | Linking Only | Unstarted | — | — | — | — | — | — | — |
| conv-49 | Full | Clean | 509 / 196 | 35.17 / 31.40 | 32.30 / 28.49 | 22/40 | 495 / 178 | 19.93 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=548dc7ac3e4313b8) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=20e5a01c0f078a2b) |
| conv-49 | Evolution Only | Clean | 509 / 196 | 35.26 / 31.80 | 29.00 / 25.52 | 26/40 | 0 / 175 | 10.00 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=08a0e6f298cd60be) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=1482f918f8de0a32) |
| conv-49 | Neither | Clean | 509 / 196 | 36.19 / 31.78 | 26.87 / 22.44 | 29/40 | 0 / 0 | 10.00 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=ffb8015ce0c3a1fb) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=210a29a1178dde3d) |
| conv-49 | Linking Only | Clean | 509 / 196 | 36.41 / 32.74 | 30.92 / 27.27 | 25/40 | 497 / 0 | 20.13 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=3e0ff28564f58b74) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=a8f94a670e20e9e7) |
| conv-50 | Full | Clean | 568 / 204 | 36.58 / 32.84 | 28.50 / 24.86 | 31/46 | 562 / 178 | 20.08 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=d10820173a73dd38) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=c7db7b64fd2f6807) |
| conv-50 | Evolution Only | Clean | 568 / 204 | 33.88 / 30.77 | 26.08 / 22.94 | 31/46 | 0 / 179 | 10.00 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=946a968c94ade465) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=8e18ba9b4c3bdaf1) |
| conv-50 | Neither | Incomplete (local scores) | 568 / 204 | 38.53 / 35.53 | 29.75 / 26.72 | 32/46 | 0 / 0 | 10.00 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=adc0d9055c4d79ec) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=fc26ec074fa15cf0) |
| conv-50 | Linking Only | Unstarted | — | — | — | — | — | — | — |


## Matched scientific comparison

Full − Evolution Only measures the difference associated with strengthening when neighbour updates are enabled. Differences were calculated within each original question ID, then averaged. The pooled mean gives each of the 558 questions equal weight. All rows in the following two tables have the same population for both conditions.

**Corrected author scoring**

| Matched questions | n | Full (%) | Evolution Only (%) | Full − Evolution Only (pp) |
| --- | --- | --- | --- | --- |
| conv-44 | 158 | 39.50 / 34.52 | 39.15 / 34.85 | +0.35 / -0.33 |
| conv-49 | 196 | 35.17 / 31.40 | 35.26 / 31.80 | -0.09 / -0.40 |
| conv-50 | 204 | 36.58 / 32.84 | 33.88 / 30.77 | +2.70 / +2.07 |
| Overall | 558 | 36.91 / 32.81 | 35.86 / 32.29 | +1.06 / +0.52 |
| Multi-hop | 99 | 17.54 / 11.29 | 15.72 / 10.54 | +1.83 / +0.75 |
| Temporal | 89 | 34.29 / 30.13 | 34.17 / 31.27 | +0.12 / -1.15 |
| Open-domain | 27 | 15.92 / 16.41 | 8.09 / 7.88 | +7.83 / +8.53 |
| Single-hop | 222 | 35.94 / 30.40 | 32.18 / 26.90 | +3.75 / +3.50 |
| Adversarial | 121 | 61.16 / 60.48 | 66.51 / 66.15 | -5.35 / -5.67 |

**Historical scoring**

| Matched questions | n | Full (%) | Evolution Only (%) | Full − Evolution Only (pp) |
| --- | --- | --- | --- | --- |
| conv-44 | 158 | 38.58 / 33.70 | 33.77 / 29.45 | +4.81 / +4.26 |
| conv-49 | 196 | 32.30 / 28.49 | 29.00 / 25.52 | +3.30 / +2.98 |
| conv-50 | 204 | 28.50 / 24.86 | 26.08 / 22.94 | +2.42 / +1.92 |
| Overall | 558 | 32.69 / 28.64 | 29.29 / 25.69 | +3.40 / +2.95 |
| Multi-hop | 99 | 17.54 / 11.29 | 15.72 / 10.54 | +1.83 / +0.75 |
| Temporal | 89 | 34.29 / 30.13 | 34.17 / 31.27 | +0.12 / -1.15 |
| Open-domain | 27 | 15.92 / 16.41 | 8.09 / 7.88 | +7.83 / +8.53 |
| Single-hop | 222 | 35.94 / 30.40 | 32.18 / 26.90 | +3.75 / +3.50 |
| Adversarial | 121 | 41.70 / 41.24 | 36.21 / 35.71 | +5.49 / +5.53 |

Full scored higher on corrected open-domain overlap (+7.83 / +8.53 points on 27 questions) and single-hop overlap (+3.75 / +3.50 on 222). Evolution Only had greater corrected adversarial overlap and answered 79/121 adversarial questions correctly, versus 71/121 for Full. The temporal comparison was mixed (+0.12 / −1.15 for Full − Evolution Only). These observations concern strengthening with evolution enabled. Estimating evolution relative to Neither, or whether evolution helps temporal reasoning at the expense of adversarial correctness, still requires the missing matched cells.

Category differences vary across conversations. Each entry below is corrected Full − Evolution Only F1 / BLEU-1 in percentage points; the parenthesized number is the matched question count. The positive pooled temporal F1 difference combines negative differences on conv-44 and conv-49 with a larger positive difference on conv-50. Historical differences are identical for categories 1–4; category 5 uses a different historical reference and is reported separately above.

| Category | conv-44 | conv-49 | conv-50 |
| --- | --- | --- | --- |
| Multi-hop | +0.39 / −0.29 (30) | +3.98 / +2.70 (37) | +0.69 / −0.51 (32) |
| Temporal | −0.77 / −2.85 (24) | −6.40 / −7.98 (33) | +7.51 / +7.18 (32) |
| Open-domain | −0.56 / +0.12 (7) | +15.99 / +16.84 (13) | +1.06 / +1.50 (7) |
| Single-hop | +6.75 / +6.21 (62) | +2.22 / +2.79 (73) | +2.90 / +2.16 (87) |
| Adversarial | −10.07 / −10.29 (35) | −8.08 / −8.44 (40) | +0.62 / +0.24 (46) |

The complete factorial comparison remains limited to the 196 conv-49 questions. These values reproduce the accepted report using question-level differences; they are not estimates across all three conversations.

| conv-49 contrast | Corrected F1 / BLEU-1 (pp) | Historical F1 / BLEU-1 (pp) |
| --- | --- | --- |
| Linking Only − Neither | +0.22 / +0.95 | +4.05 / +4.83 |
| Evolution Only − Neither | −0.93 / +0.02 | +2.13 / +3.07 |
| Full − Linking Only | −1.23 / −1.34 | +1.38 / +1.22 |
| Full − Evolution Only | −0.09 / −0.40 | +3.30 / +2.98 |
| Full − Linking Only − Evolution Only + Neither | −0.31 / −1.36 | −0.75 / −1.85 |

The additional accepted cells cannot establish whether Linking Only consistently beats Neither, Full beats Linking Only, or the negative conv-49 interaction persists. Both linking-enabled conditions also alter new-note tags, and all builds are stochastic. Greater retrieval expansion with modest or mixed quality differences is an observation; distraction from larger contexts is only a hypothesis.

The two accepted new evolution-only builds always retrieved ten entries per question. Their 204 conv-50 answer prompts used 277,708 input tokens (US$0.04317840 in identified answer-generation charges), compared with 558,814 (US$0.08534550) in Full. On conv-44 the corresponding numbers were 218,699 (US$0.03397785) and 444,195 (US$0.06779085). Full also changes new-note tags, so these scores cannot identify the effect of context length alone.

A-MEM Table 3 orders Full above Linking Only above Neither in all five categories on both metrics. Among the accepted cells, only conv-49 supports a complete check of that ordering: open-domain and single-hop follow it under corrected scoring. Evolution Only is an additional condition. The paper describes a different population, does not identify the exact Table 3 IDs, and gives different category-specific retrieval depths in Supplementary Table 8. This study used the released default k=10 throughout. [Paper, Table 3](https://arxiv.org/html/2502.12110v11#S4.T3) · [Supplement, Table 8](https://arxiv.org/html/2502.12110v11#A1.T8)

## Protocol, verification and deviations

[PR #44](https://github.com/alistairkung/A-mem-reproducibility/pull/44) merged as `8f0481d53a5b69a7343753d72012fb4effccc1cd`. It extended the [conv-49 executor](gpt4omini-conv49-ablation.md) in the preselected order. Every new build started with an empty memory/cache. All used the dated GPT-4o-mini model through OpenRouter with OpenAI as sole upstream, no fallback routing, the original four JSON schemas and prompts, temperatures 0.7 / category-5 answer 0.5, limits 1,000 / shared decision 4,096, five construction neighbours and base retrieval k=10. Shared decisions, counters, consolidation and stale index semantics were preserved under every gate.

Independent Standards and Spec reviews passed at `2b65f2e429d5f0df0052d07344d52ddbc95814c9`. The offline suite passed 922 tests and 92 subtests with 17 warnings. Frozen author and Full replay matched 568 insertion states, 1,544 recorded calls, 204 answers, both scoring policies and failure provenance. Full-size SDK proofs covered 4,494 scores on conv-44 and 5,804 on conv-50. The final 22-session real-runner verification used mock model calls and 1,118 measured service units. A preliminary gate also used 1,118. The original Full, conv-49 and DeepSeek evidence remains in its own lineage.

- **Evolution Only / conv-50.** The two independent audits verified 568 shared decisions, 179 neighbour actions, zero strengthening and 204 original QA associations. The runtime had 2,906 observations and 775 traces. Both Experiments together held 408 items and 5,804 scores. During QA, a new Python process could not start because the temporary base installation had lost standard-library files. The existing driver continued. Missing files were restored from the matching CPython 3.11.17 distribution after checking both surviving regular files, including the interpreter. Post-repair checks verified the distribution tree, 28,179 installed dependency files, native preflight and all 1,534 historical files. The prior full runtime tree lacked contemporaneous hashes. A fresh, network-disabled author rescoring reproduced all 5,804 saved metric values. The cell was accepted Clean.
- **Evolution Only / conv-44.** All 675 shared decisions and 158 QA verified, with 235 neighbour actions, zero strengthening, 3,053 runtime observations and 836 traces. Both Experiments contained 316 items and 4,494 scores. Independent checks re-encoded all 675 embedding rows and verified all six consolidations. The accepted cell was Clean. The Full / conv-44 baseline retains its historical Degraded classification.
- **Neither / conv-50.** All 568 shared decisions, 204 predictions and both local scoring views were saved. The runtime verified 2,727 observations and 775 traces. The initial read contained 5,686 scores. The final five reads each contained 408 items and all 5,804 score records. Native numeric readback differs from the local author score for one BLEU-4 value in each policy. See [BLK-027](blockers.md#blk-027). Six original reads and subsequent direct HTTP reads reproduced the discrepancy. Both affected subjects have the correct original QA association and exact original-record metadata. No provider request was repeated. The terminal phase, original import claim and IDs, final cache and all readbacks are retained. Independent checks restored the original cache and reproduced its saved memory snapshot. A fresh, network-disabled author rescoring reproduced all 5,804 values and both aggregates. The normal final-memory and cache-proof receipts were never written after verification failed. Changing the comparison to a tolerance or substituting the metadata value would alter the accepted verification policy.

The affected author value is `4.0194972443398975e-7`; Langfuse returns `4.019497244339897e-7` for the native score in both policies. They differ by one binary64 step (about 5.29 × 10⁻²³). The pinned SDK sent the exact author value in an offline wire test. The direct Experiment-item, per-trace score and score-ID-filtered Metrics endpoints corroborated the lower remote value. Numeric equality filtering accepted both adjacent inputs. The precise server-side cause remains open. An idempotent overwrite with the same value lacks a demonstrated corrective effect. There was no re-import. [Langfuse score update semantics](https://langfuse.com/faq/all/tracing-data-updates)

A fresh read at 12:43 HKT on 6 November, after the user-requested pause, still returned the same two discrepancies. The original phase remains Incomplete. The saved raw response and `outcomes/neither-conv-50/spec-direct-readback/after-pause-score-proof.json` (SHA-256 `061acde34572b520208fabf228c45e1400213ef4d2555699b3dab14574104606`) distinguish the continuing blocker from temporary initial score visibility.

The merged execution source fingerprint is `395df897546256d879304807fd5fc0eb94413a5d1ee7bde1a1ed773baca265b8`. The following local evidence files are retained beneath `artifacts/gpt4omini/`; their contents include the detailed identity, scoring, action, cloud and financial checks. They are not new replacements for the original cell receipts.

| Evidence | Relative path | SHA-256 |
| --- | --- | --- |
| Evolution Only / conv-50, Spec | `outcomes/evolution_only-conv-50/acceptance-spec.json` | `a1175958d92bdfa0ea95f8ca06664b24ce6daa7afaa6ea23e9705fcfd8ad620a` |
| Evolution Only / conv-50, Standards | `outcomes/evolution_only-conv-50/acceptance-standards.json` | `6cf33c42713b80510db2a061545a5108fe7003c034d5b5762426df8cdb8e0fe0` |
| Evolution Only / conv-44, Spec | `outcomes/evolution_only-conv-44/acceptance-spec.json` | `5e7fa5fc240323162384929796c414fcd3960dfd9ac1b14d32078d3f69fe037d` |
| Evolution Only / conv-44, Standards | `outcomes/evolution_only-conv-44/acceptance-standards.json` | `5ee8cf3d74f911512efa78086b0d612890b336377c9476d80c3f984e5aa5f106` |
| Neither / conv-50 terminal phase | `cells/neither-conv-50/runs/gpt4omini-neither-conv50-r0-p0/phase.json` | `259a14e7b1c7c6ace8056e26415fbade72ff766d2bc245496254cbf65519023d` |
| Neither / conv-50 independent Spec diagnosis | `outcomes/neither-conv-50/spec-direct-readback/independent-spec-report.json` | `e9d10b6bbfc6ec2b7c02699b676bdf5a13ea1a990d703152d9924009eeec0b0c` |
| Neither / conv-50 independent Standards diagnosis | `outcomes/neither-conv-50/standards-precision/independent-diagnosis.json` | `70667984514ac6bf33a5f9b3ab8ae6c1ed0380f45a65df7e1ecca6cdce256d26` |

## Financial close

All costs below are US dollars. Conservative model exposure rounds individual settled requests up to whole microdollars and retains the three original unknown-charge reservations. Prior accepted costs are repeated for inventory only, not charged again.

| Allocation | Identified model charges | Conservative model exposure |
| --- | ---: | ---: |
| Compatibility, allocated to Full / conv-44 | 0.00574890 | 0.064702 |
| Full / conv-44 collection | 0.39390465 | 0.394715 |
| Full / conv-49 | 0.31996545 | 0.320705 |
| Full / conv-50 | 0.36696630 | 0.367681 |
| Evolution Only / conv-49 | 0.28014945 | 0.280813 |
| Neither / conv-49 | 0.27892170 | 0.279592 |
| Linking Only / conv-49 | 0.32385990 | 0.324609 |
| Evolution Only / conv-50 | 0.31603155 | 0.316764 |
| Evolution Only / conv-44 | 0.35714685 | 0.357947 |
| Neither / conv-50 (Incomplete) | 0.31590645 | 0.316637 |
| **GPT-4o-mini campaign** | **2.95860120** | **3.024165** |

The three newly collected cells add US$0.98908485 in identified model charges and US$0.991348 conservative model exposure to the accepted opening position. No new inference request failed or required a fallback, semantic retry or checkpoint continuation. The three older compatibility reservations remain US$0.058950 in the campaign total. The unrelated US$0.011651 account opening offset is preserved separately.

| New service allocation | Measured units | Service at full marginal rate | Model plus full-rate service upper bound |
| --- | ---: | ---: | ---: |
| Two release verification gates | 2,236 | 0.178880 | 0.178880 |
| Evolution Only / conv-50 | 10,709 | 0.856720 | 1.173484 |
| Evolution Only / conv-44 | 9,331 | 0.746480 | 1.104427 |
| Neither / conv-50 | 10,530 | 0.842400 | 1.159037 |
| **New service total** | **32,806** | **2.624480** | **3.615828** |

The service upper bounds apply US$8 per 100,000 units even to units covered by the included allowance. Each combined cell bound is below its US$5 cap. The existing Core subscription is US$29 per month and is not an incremental charge for these six cells. Authenticated billing read at 12:39 HKT on 6 November showed a US$1.42 draft usage charge, US$30.42 draft total including the subscription, 117,801 current-period units and 121,479 rolling units. The current-period count implies US$1.42408 before invoice rounding. The conservative organization count is 121,480, implying US$1.718400 overage if all those units were in the current period. These counts and the draft invoice can lag ingestion; the durable campaign bound remains the larger US$2.624480 full-rate amount. No plan change or automatic top-up occurred. [Langfuse pricing](https://langfuse.com/pricing)

Model exposure plus the full marginal service bound totals **US$5.648645**, leaving **US$36.351355** of the US$42 planned allocation. The US$8 contingency remains protected. Applying the prior highest-stage model forecasts to the three unstarted cells gives US$1.17239286 model costs; doubling that scenario and reserving 13,500 service units per remaining cell gives a whole-campaign bound of **US$11.233431**. This is a planning sensitivity, not a replacement for per-cell admission. Funding is sufficient under that scenario; BLK-027 blocks execution.

The post-pause request-level financial close is pending. The original read-only process was unavailable on resume. Its 10,161 saved successful generation lookups were preserved and independently validated; a separately reviewed GET-only continuation must verify the remaining 3,448 settled generation IDs and closing account/key movement. It cannot transmit inference, write the ledger or accept the scientific cell.

## Reproducibility and remaining work

The public numeric records contain 558 unique original question IDs and 1,508 accepted condition–question pairs, with corrected and historical F1/BLEU-1. They exclude the Incomplete cell from pooled analysis. Raw outputs, cache states, original trace associations, request accounting and independent audit manifests remain under `artifacts/gpt4omini/`; prior Full, conv-49 and DeepSeek evidence is unchanged. DeepSeek remains historical engineering evidence, separate from these primary GPT-4o-mini comparisons.

This is a descriptive analysis of one stochastic build per cell. Questions within a conversation are not independent replications of memory construction. Three conversations are a limited subset of the benchmark, category sizes differ, and the matched conditions can follow different stochastic memory trajectories. No significance test, confidence claim or established causal effect is made. The tiny BLEU-4 discrepancy does not change the displayed primary metrics, but exact remote metric equality is a mandatory acceptance gate and cannot be silently relaxed.

The final twelve-cell coursework report and presentation are not ready. Complete the reporting gate for Neither / conv-50 using a reviewed correction with exact native readback, or obtain an explicit decision on the verification policy, before admitting the remaining three fresh builds in the frozen order. Do not repeat collected inference. Then recalculate all four conditions on 558 matched IDs and review the complete outcome. No final coursework PDF or presentation was created.
