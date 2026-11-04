# Three Full A-MEM baselines with GPT-4o-mini

The three preselected conversations completed in three independent fresh builds. All 1,752 original turns and 558 questions were processed in order. Both independent reviewers accepted each cell after its final scientific, Langfuse and financial checks. The primary result is the mean over 558 individual questions, giving each question equal weight.

## Scores

Pairs below are F1 / BLEU-1 in percent. Both views score the same saved predictions. Adversarial correctness is a separate binary author metric.

| Full cell | Turns | Questions | Corrected | Historical | Adversarial correct | Classification |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| conv-44 | 675 | 158 | 39.50 / 34.52 | 38.58 / 33.70 | 18/35 | Degraded |
| conv-49 | 509 | 196 | 35.17 / 31.40 | 32.30 / 28.49 | 22/40 | Clean |
| conv-50 | 568 | 204 | 36.58 / 32.84 | 28.50 / 24.86 | 31/46 | Clean |
| Combined | 1,752 | 558 | 36.91 / 32.81 | 32.69 / 28.64 | 71/121 | Three accepted builds |

| Question category | Count | Corrected | Historical | Published Full |
| --- | ---: | ---: | ---: | ---: |
| Multi-hop | 99 | 17.54 / 11.29 | 17.54 / 11.29 | 27.02 / 20.09 |
| Temporal | 89 | 34.29 / 30.13 | 34.29 / 30.13 | 45.85 / 36.67 |
| Open-domain | 27 | 15.92 / 16.41 | 15.92 / 16.41 | 12.14 / 12.00 |
| Single-hop | 222 | 35.94 / 30.40 | 35.94 / 30.40 | 44.65 / 37.06 |
| Adversarial | 121 | 61.16 / 60.48 | 41.70 / 41.24 | 50.03 / 49.47 |

Single-hop F1 exceeded multi-hop F1 in both evaluations. This subset scored lower on multi-hop, temporal and single-hop overlap, and higher on open-domain overlap. Open-domain contains only 27 questions. On adversarial questions the corrected overlap exceeds the published Full scores, while the historical view falls below them. Adversarial correctness was 71/121 (58.68%). Table 3 supplies category scores only. [A-MEM paper, Table 3](https://arxiv.org/html/2502.12110v11#S4.T3)

Section 4.1 describes 7,512 LoCoMo QA pairs. The released ten-conversation file has 1,986 questions, and the preselected three-conversation subset has 558. Table 3 does not identify the exact evaluated question IDs. The paper labels the model GPT-4o-mini. Our gateway and snapshot are pinned below. Table 8 lists GPT-4o-mini retrieval depths of 40, 40, 50, 50 and 40 by category. The exact setting used for Table 3 is undocumented. We used the released author default of 10 for every question. Each conversation contributed one stochastic build. The comparisons describe these populations and settings. Estimating the contribution of linking or evolution requires the paired ablation cells. [Paper and supplementary tables](https://arxiv.org/html/2502.12110v11)

## Protocol and verification

The campaign used `openai/gpt-4o-mini-2024-07-18` through OpenRouter at `https://openrouter.ai/api/v1`, restricted to OpenAI with provider fallbacks disabled and required parameters enforced. Every settled generation had the dated model, one successful upstream OpenAI request and a matching request-level charge. The route advertised 128,000 context tokens, 16,384 maximum output tokens and US$0.15 / US$0.60 per million input / output tokens. Each cell rechecked provider capabilities and the key and prepaid balances before model execution.

The four native author JSON schemas, prompts, strengthening and neighbour updates remained active. The frozen output limits were 1,000 tokens for metadata, query keywords and answering, and 4,096 for shared evolution decisions. Temperature was 0.7 except category-5 answering at 0.5. Construction used five neighbours. All builds retained author consolidation and stale-index behavior, with exact CPU re-encoding of the saved retrieval corpus. The final note counts and evolution counters were 675, 509 and 568. The saved indexes had 43, zero and 22 stale rows, respectively, with 384 float32 dimensions per row. All benchmark calls completed without provider errors, malformed decisions, length exhaustion, semantic retries, recovery children or scoring failures.

[PR #36](https://github.com/alistairkung/A-mem-reproducibility/pull/36) merged as `61d527a4edbc2d2f4d542e322dd347ab4d54ab4d`. The release passed 885 offline tests and 92 subtests. Its full-size SDK proof preserved all 316 scoring items, 4,494 scores and 158 original QA associations and detected partial writes. It used 40 batches with the largest serialized batch below the 32 MiB limit. The native cloud gate and full-scale remote readback verified actual records. [Conv-44 release evidence](gpt4omini-conv44-release.md)

[PR #40](https://github.com/alistairkung/A-mem-reproducibility/pull/40) merged as `8944356202516ec0c9789a71c1a357f1a77f367e` after independent Standards and Spec passes at `0c9d45c99e1d28981f1133def7f101f43517e147`. The complete suite passed 890 tests and 92 subtests. Frozen author versus Full replay matched 568 per-insertion hashes, 1,544 saved requests and 204 answers. Full-size offline tests covered both new conversations, independent stores, multiple checkpoint continuations, native fallback, financial and provenance faults. The two baseline releases retain separate source fingerprints and byte-identical scientific settings. GitHub had no required CI contexts. Both PRs merged normally.

## Langfuse evidence

Local immutable raw files, hash-verified phase inventories and the campaign ledger are authoritative. Readback compared original QA trace IDs, questions, predictions, references, score names and values for both Experiment policies. The runtime counts below exclude Experiment reporting records.

| Conversation | Runtime observations / traces | Items / scores | Original QA links | Remote records |
| --- | ---: | ---: | ---: | --- |
| conv-44 | 3,710 / 836 | 316 / 4,494 | 158 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b4a39a3e02e2f361) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=bd8af7375fe2248e) · [First QA trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/c3370356dbcc49afadc9310c7dbf86b7) |
| conv-49 | 3,183 / 708 | 392 / 5,568 | 196 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=548dc7ac3e4313b8) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=20e5a01c0f078a2b) · [First QA trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/f888c3e39e7c4657863b08f62dd350d1) |
| conv-50 | 3,467 / 775 | 408 / 5,804 | 204 | [Corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=d10820173a73dd38) · [Historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=c7db7b64fd2f6807) · [First QA trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/3b134d4c229842e793f914ea17a8cf31) |

Langfuse used 9,988, 10,635 and 11,270 included units for the three baselines, for 31,893 total. The post-collection organization reading was 56,863 units. The conservative count used for planning is 56,864 after allowing for the one-unit difference between the display and the usage tally. All three fit in the existing Core subscription with zero attributable overage. [Langfuse pricing](https://langfuse.com/pricing)

## OpenRouter and remaining budget

| Allocation | Identified model charges (US$) | Conservative exposure (US$) |
| --- | ---: | ---: |
| Compatibility, allocated to conv-44 | 0.00574890 | 0.064702 |
| conv-44 collection | 0.39390465 | 0.394715 |
| conv-49 collection | 0.31996545 | 0.320705 |
| conv-50 collection | 0.36696630 | 0.367681 |
| **Campaign** | **1.08658530** | **1.147803** |

There were 4,620 benchmark requests and eight compatibility attempts. All 4,625 settled generation IDs, upstream records and costs reconciled against the ledger and OpenRouter key and account movement. Three initial HTTP 403 compatibility attempts lacked request-level billing records. Their actual charges remain unknown. The authorized permanent US$0.058950 upper bound remains charged to the compatibility and conv-44 allocations. Conv-44 therefore carries the **Degraded** classification. Prior unrelated account usage of US$0.011651 is anchored to the original account snapshot. No new unknown charge arose.

The prepaid balance after conv-50 was US$48.9017637 and key allowance remaining was US$48.9134147. The conservative campaign allocation remaining under US$42 is US$40.852197. The protected US$8 remains intact.

Using the highest observed conservative per-stage mean across these three Full builds, the nine remaining ablation cells project to **US$3.3262** in model costs. The model forecast per future condition is US$0.4012 for conv-44, US$0.3376 for conv-49 and US$0.3700 for conv-50. The resulting whole-study model scenario is US$4.4740, including exposures already incurred. With remaining model costs doubled and 16,000 Langfuse units allowed per future cell, the combined model-and-marginal-service scenario is US$15.87, including US$8.07 of possible future service overage. Action settings can change prompt and output lengths. Service overage and the nine cells require their own authorization.

The first planned pair is **Neither / conv-49 against this accepted Full / conv-49**. It estimates the joint contribution of both mechanisms on identical question IDs. Preserve the preselected order within each remaining condition (conv-49, conv-50, conv-44), then compare Linking Only and Evolution Only to separate the two contributions. Each requires a fresh independent build, the frozen model policy, a new reviewed execution path, service capacity and its own financial admission.

## Debug diary and provenance

- The three denied compatibility attempts and the temporary generation-lookup delay retain their original evidence. A later GET settled the delayed successful generation without resending its model request.
- The first conv-44 scoring read showed 4,059 of 4,494 scores. A later read verified all scores with no further import or inference. All published scoring rows retain their original QA associations.
- The conv-44 Spec diagnostic compared consolidated corpus text using the append-time document format, yielding 602 apparent differences. Comparing each row with the author's matching consolidation or insertion format yields 43 stale rows, the independently verified count in the original public acceptance. Both counts and the original sealed receipts remain available.
- PR #40 review reproduced tampering with accepted state, audit dependencies, raw billing GETs and ledger rows in isolated copies. The final release rejected each before subsequent paid admission. A test invocation omitted the historical fixture selectors. Its log was retained and the entire suite reran successfully using the pinned fixtures.
- A conv-50 private verifier transcription incorrectly changed an expected compatibility reservation while adapting the question count. The check halted before cloud access. The retained original reservation matched its immutable ledger. The corrected verifier passed without model calls or modifications to study evidence.
- The combined Full estimates use the independently accepted GPT-4o-mini receipts for all three conversations and the frozen dataset. DeepSeek source bindings, financial history, caches and Langfuse records remain intact in their original campaigns.

The private campaign namespace is `artifacts/gpt4omini`. Each acceptance has separate Spec and Standards records at `outcomes/<conversation>/acceptance-*.json` and a sealed frontier with the ledger digest. The question-weighted result is `outcomes/three-full-aggregate.json`. It binds its input score files, the fixed manifest and both independent approvals for every conversation. Experiment payloads, model responses and credentials are excluded from this public report.
