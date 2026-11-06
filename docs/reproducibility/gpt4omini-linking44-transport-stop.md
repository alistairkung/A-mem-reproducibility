# GPT-4o-mini: eleven accepted cells and the final conv-44 transport stop

**Status: incomplete study; paid execution stopped.** Eleven of twelve cells are independently accepted. Linking Only / conv-44 stopped after 231 of 675 turns, before any of its 158 questions. The requested 558-question four-condition comparison is unavailable. This report preserves the accepted results, the exact stop and the financial upper bounds; it does not authorize recovery.

## Protocol and accepted inventory

The frozen protocol remains the [accepted conv-49 specification](gpt4omini-conv49-four-condition-results.md): dated `openai/gpt-4o-mini-2024-07-18`, OpenRouter, OpenAI-only upstream and no fallback routing; original schemas/prompts; temperature 0.7 except category-5 answers at 0.5; 1,000 output tokens except 4,096 for shared evolution; retrieval k=10 and five construction neighbours. Original insertion, counter, consolidation and stale-index semantics remain intact. Only strengthening (links/new-note tags) and neighbour updates (existing context/tags) vary. Shared decisions are generated in every condition. Every new cell starts with its own empty memory and independent cache.

Expansion followed the preselected order Evolution Only / conv-50, conv-44; Neither / conv-50, conv-44; Linking Only / conv-50, conv-44. No completed cell was repeated. Full, conv-49 and DeepSeek evidence remain unchanged. DeepSeek remains historical engineering evidence, outside this primary analysis.

Scores are percentages, shown as **corrected F1 / BLEU-1**. Model costs below include scientific generations only; compatibility costs and unknown reservations are separate.

| Conversation | Condition | Status | Turns / QA | F1 / BLEU-1 | Identified model USD | Experiments: corrected / historical |
|---|---|---|---:|---:|---:|---|
| conv-44 | Neither | Clean | 675 / 158 | 43.11 / 38.35 | 0.35561970 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=9bbb08d6e8dbec66) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=c9cdb85f0e917bd8) |
| conv-44 | Evolution Only | Clean | 675 / 158 | 39.15 / 34.85 | 0.35714685 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=877089259f1d95e1) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=6374428c15b01ed1) |
| conv-44 | Linking Only | Incomplete | 231 / 0 | — | 0.10740285 known + unknown reserve | None: zero QA |
| conv-44 | Full | Degraded | 675 / 158 | 39.50 / 34.52 | 0.39390465 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b4a39a3e02e2f361) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=bd8af7375fe2248e) |
| conv-49 | Neither | Clean | 509 / 196 | 36.19 / 31.78 | 0.27892170 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=ffb8015ce0c3a1fb) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=210a29a1178dde3d) |
| conv-49 | Evolution Only | Clean | 509 / 196 | 35.26 / 31.80 | 0.28014945 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=08a0e6f298cd60be) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=1482f918f8de0a32) |
| conv-49 | Linking Only | Clean | 509 / 196 | 36.41 / 32.74 | 0.32385990 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=3e0ff28564f58b74) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=a8f94a670e20e9e7) |
| conv-49 | Full | Clean | 509 / 196 | 35.17 / 31.40 | 0.31996545 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=548dc7ac3e4313b8) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=20e5a01c0f078a2b) |
| conv-50 | Neither | Degraded | 568 / 204 | 38.53 / 35.53 | 0.31590645 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=adc0d9055c4d79ec) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=fc26ec074fa15cf0) |
| conv-50 | Evolution Only | Clean | 568 / 204 | 33.88 / 30.77 | 0.31603155 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=946a968c94ade465) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=8e18ba9b4c3bdaf1) |
| conv-50 | Linking Only | Clean | 568 / 204 | 37.18 / 33.88 | 0.36489600 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=3267f9cb9f6d61eb) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b02e293fd2a9f1c5) |
| conv-50 | Full | Clean | 568 / 204 | 36.58 / 32.84 | 0.36696630 | [corrected](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=d10820173a73dd38) / [historical](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=c7db7b64fd2f6807) |

Full / conv-44 retains its historical Degraded classification from compatibility/financial history; its scientific baseline has no recorded generation/schema/fallback/scoring failure. Neither / conv-50 is Degraded solely under the explicitly authorised two-score representation supplement below. Neither / conv-44 and Linking Only / conv-50 are Clean. The latter has 563 strengthening actions, zero neighbour updates, 568 exact embeddings, 3,290 observations/775 runtime traces, 408 Experiment items, 5,804 exact scores and all 204 original QA associations verified. Neither / conv-44 has zero applied actions, 675 exact embeddings, 2,818 observations/836 runtime traces, 316 items, 4,494 exact scores and 158 QA associations verified.

## BLK-027 acceptance

PR #46 merged normally as `4542368a8f5dc7e6a218b23701140becf2d25930`, reviewed second parent `0c61f42405bebf13c4efe68f6323899bd66ea3fb`. The release passed 1,003 offline tests and 92 subtests, independent Standards/Spec reviews, author/Full replay equivalence and a source-bound 1,118-unit cloud gate without provider/model-generation requests. Scientific support-source fingerprint: `817d3d06017d8d119c80eae3b487b482c0977ee6b8e383f8bd080d9c2c35b17d`.

The original Neither / conv-50 Incomplete receipt and terminal SQL state are preserved. Supplement `7858b88ca5df5dbbe13ad36aaa05c860e8f8d2c4e1af14fe1387dc91d5ada012` accepts it as Degraded after all 204 questions, 408 items, 5,804 scores, associations, cache and finances were verified. Only corrected BLEU-4 score `11db9dd69284d175` and historical BLEU-4 score `03f14c429aa18b91`, both `conv-50:qa:76`, admit the pinned local `4.0194972443398975e-7` (`0x1.af971954baf8dp-22`) versus remote `4.019497244339897e-7` (`0x1.af971954baf8cp-22`). [The complete identity tuples and policies](../../config/blk027-acceptance.json) are unchanged. Every other score, including all primary metrics, matches exactly. No general tolerance, scorer change, overwrite, re-import or inference repetition occurred. The responsible remote component remains unconfirmed.

## Final cell: terminal no-response failure

The final phase `gpt4omini-linking_only-conv44-r0-p0` began under fresh approval `c108d9803eff91fff9af9b1133c1fb1849a10a48ee697f937abed86e38e019e5`, after all 149,688 bound files and eleven accepted predecessors were independently checked. Its opening account/key movement was exactly zero. On original turn `D10:15` (232nd), metadata attempt 17285 settled; shared-decision attempt **17286** failed after **62.742986 seconds** with `RemoteProtocolError: Server disconnected without sending a response.`

There is **no recorded HTTP status, response body, provider generation ID or usage**, and exactly one physical attempt. Do not infer that it was unbilled or that OpenAI completed it. The requested route was frozen; the failed response supplies no independent upstream confirmation. The driver stopped with `BudgetStop`, sealed Incomplete and left SQL terminal with the transport halt. This is a new occurrence in [BLK-022’s unknown-charge transport family](blockers.md#blk-022), distinct from the earlier HTTP200/body-read/successful-SDK-retry sequence. The old incident-specific exception does not apply.

The committed prefix contains **231 notes, counter 231, 222 strengthening actions, zero neighbour updates and zero QA**. The failed turn was not inserted. No original-evolution-fallback event or supported length-recovery flag exists. The failed turn’s already-paid metadata is preserved; any future recovery must explicitly account for this partial turn instead of silently repeating or discarding it. The raw request, failure, partial memory/index, source binding and every charge remain intact. Independent audits verify the exact 231×384 embeddings, stale index, consolidations at 100/200 and every prior accepted artifact. Remote readback verifies 921 observations and 234 traces, metered as 1,155 units; incomplete usage/cost is explicitly recorded for the failed generation. Original initial identifier-visibility errors and successful final readbacks are both retained. No Experiment import exists because no answers exist.

Phase file SHA-256: `65d8f6a672863bdfbc2a5d5a6d5d95b3fd25c0a2b9b2dfd8cbef53032c80917b`; canonical SQL seal: `97dbd9f331503b15d97a73d7b3f210a0c4ed13363b0bfe33e63fedbc4e2b32aa`. No retry, new paid continuation, configuration change or additional experiment was launched.

## Available matched results

**Different populations are reported separately.** Four conditions are available only on the same 400 questions from conv-49 and conv-50. Full, Evolution Only and Neither are available on all 558 questions. Comparisons give each original question equal weight; differences are calculated per question before aggregation. The missing Linking Only / conv-44 scores are not imputed. The linked aggregate artifact includes every available conversation/category/condition group and contrast under `by_conversation`, before pooling. Historical scoring is secondary and uses the same saved predictions.

| Population | Condition | Corrected F1 / BLEU-1 | Historical F1 / BLEU-1 | Adversarial correct |
|---|---|---:|---:|---:|
| 400 questions, two conversations | Neither | 37.38 / 33.69 | 28.34 / 24.62 | 61/86 |
| 400 questions, two conversations | Evolution Only | 34.55 / 31.28 | 27.51 / 24.20 | 57/86 |
| 400 questions, two conversations | Linking Only | 36.80 / 33.32 | 28.99 / 25.57 | 58/86 |
| 400 questions, two conversations | Full | 35.89 / 32.14 | 30.36 / 26.64 | 53/86 |
| 558 questions, three conversations | Neither | 39.00 / 35.01 | 30.03 / 25.95 | 86/121 |
| 558 questions, three conversations | Evolution Only | 35.86 / 32.29 | 29.29 / 25.69 | 79/121 |
| 558 questions, three conversations | Full | 36.91 / 32.81 | 32.69 / 28.64 | 71/121 |

Four-condition contrasts below apply **only to 400 matched questions**. Values are percentage points.

| Contrast | Corrected ΔF1 / ΔBLEU-1 | Historical ΔF1 / ΔBLEU-1 |
|---|---:|---:|
| Linking Only − Neither | -0.58 / -0.37 | 0.65 / 0.95 |
| Evolution Only − Neither | -2.83 / -2.42 | -0.83 / -0.42 |
| Full − Linking Only | -0.91 / -1.18 | 1.37 / 1.07 |
| Full − Evolution Only | 1.33 / 0.86 | 2.85 / 2.44 |
| Full − Linking Only − Evolution Only + Neither | 1.91 / 1.23 | 2.20 / 1.49 |

Corrected category contrasts on those **400 matched questions**:

| Category | n | Linking − Neither | Evolution − Neither | Full − Linking | Full − Evolution | Interaction |
|---|---:|---:|---:|---:|---:|---:|
| Multi-hop | 69 | 5.52 / 4.16 | -1.54 / -2.22 | -4.61 / -5.17 | 2.45 / 1.21 | -3.07 / -2.95 |
| Temporal | 65 | -2.05 / -1.17 | -0.65 / 0.51 | 1.85 / 1.17 | 0.45 / -0.52 | 2.50 / 0.65 |
| Open-domain | 20 | 1.67 / 1.01 | -5.33 / -6.45 | 3.76 / 4.01 | 10.76 / 11.47 | 9.09 / 10.46 |
| Single-hop | 160 | -1.51 / -0.63 | -2.97 / -2.05 | 1.13 / 1.03 | 2.59 / 2.45 | 4.10 / 3.08 |
| Adversarial | 86 | -3.16 / -3.25 | -4.65 / -4.54 | -4.92 / -5.09 | -3.42 / -3.79 | -0.27 / -0.55 |

On **558 matched questions**, Evolution Only − Neither is **−3.146863 / −2.722550 pp** corrected F1/BLEU-1 (historical −0.740309 / −0.260013 pp). Adversarial correctness is 79/121 versus 86/121. The corrected category differences are:

| Category | n | Evolution Only − Neither |
|---|---:|---:|
| Multi-hop | 99 | -1.14 / -1.40 |
| Temporal | 89 | -2.44 / -1.53 |
| Open-domain | 27 | -6.28 / -6.27 |
| Single-hop | 222 | -2.64 / -1.82 |
| Adversarial | 121 | -5.55 / -5.55 |


Retrieval and provider-input comparisons below use the same **400-question population** (conv-49 and conv-50). Answer prompt tokens are native provider counts; expansion entries describe retrieved context, not unique independent evidence.

| Condition | Mean retrieved entries | Native answer prompt tokens | Identified model USD (both cells) | Strengthen / neighbour actions |
|---|---:|---:|---:|---:|
| Neither | 10.00 | 527,828 | 0.59482815 | 0 / 0 |
| Evolution Only | 10.00 | 530,327 | 0.59618100 | 0 / 354 |
| Linking Only | 20.14 | 1,070,159 | 0.68875590 | 1060 / 0 |
| Full | 20.01 | 1,059,596 | 0.68693175 | 1057 / 356 |

## Interpretation and limits

Linking Only does not consistently improve on Neither: the conv-49 corrected contrast is +0.22 / +0.95 pp, while conv-50 is −1.35 / −1.65 pp. Full falls below Linking Only on both completed four-condition conversations. The interaction reverses from −0.31 / −1.36 pp on conv-49 to +4.05 / +3.72 pp on conv-50; its 400-question pooled value is positive despite Full remaining below Neither. No 558-question interaction can yet be computed.

Evolution Only has lower corrected F1 than Neither in all three conversations; its pooled temporal-category contrast is also negative. These builds therefore do not show a consistent independent temporal-reasoning benefit. Binary adversarial correctness is separate from category-5 text-overlap scores; historical category-5 scoring changes the apparent pooled pattern.

Linking Only / conv-50 expands ten initial retrieval hits to 18–23 entries (mean 20.151961), with mean locally estimated retrieved-context length 2,642.460784 tokens. This larger context accompanies lower corrected scores than Neither on that conversation; it does not establish that context length caused the loss. Strengthening also changes tags, and stochastic memory construction and answering vary. Actual provider prompt-token costs remain in the sealed evidence; local context estimates are not billed token counts.

The published [A-MEM Table 3](https://arxiv.org/html/2502.12110v11#S4.T3) orders Neither below Linking Only below Full in its reported categories. The completed comparisons here do not consistently follow that ordering. This is a different evaluation population and retrieval configuration (our k=10), not a direct numerical replication. Evolution Only is an additional condition.

These are descriptive single stochastic builds, not established causal effects or statistically significant estimates. Questions share each conversation’s memory build; sequential hosted-model execution and category composition also limit generalisation. A dated model identifier is not a measured weight hash. The earlier Evolution Only / conv-50 interpreter repair remains disclosed in the prior outcome: restored files matched the distribution and rescoring passed, but no contemporaneous complete pre-incident runtime-tree hash existed. The final coursework report/presentation is not ready as a completed twelve-cell study.

## Spending and verification

The terminal cell added US$0.10740285 identified charges across 463 settled generations, US$0.107623 conservative settled exposure, and a new US$0.021044 unknown reservation. Its 1,155 service units cost at most US$0.092400 at the full marginal rate; its combined partial-cell upper bound is US$0.221067, below US$5. Budget exhaustion did not cause the stop.

A separately reviewed GET-only helper verified the 463 new known generation IDs against their exact native usage, OpenAI route and charge, preserving the previous 16,819-ID financial close. Both raw account/key responses match the known US$0.10740285 movement with zero aggregate residual. **This is not request-level evidence that attempt 17286 was unbilled.** All four unknown reservations remain held, and the campaign is explicitly not fully reconciled. The helper cannot change the ledger, accept the cell or release paid execution. Independent reviews passed 39 Spec and 30 Standards adverse checks before its one-shot read-only execution.

| Closing quantity | USD |
|---|---:|
| Identified campaign model charges | 3.78651975 |
| Conservative campaign model exposure | 3.874865 |
| Included old unknown reservations | 0.058950 |
| Included new unknown reservation | 0.021044 |
| Measured incremental service, 55,268 units at full marginal rate | 4.421440 |
| Retained historical organisation allowance, two units | 0.000160 |
| Combined conservative model/service upper bound | 8.296465 |
| Remaining US$42 planned allocation | 33.703535 |
| Protected contingency consumed | 0 |
| Protected contingency retained | 8 |
| OpenRouter prepaid credit | 46.20182925 |
| OpenRouter key allowance remaining | 46.21348025 |

The model total includes five compatibility checks (US$0.00574890 identified), separate from scientific-generation costs. The external account opening offset US$0.011651 is not a campaign request. The service meter includes all three 1,118-unit verification gates and all six expansion attempts, including the stopped cell. The US$6.769440 programme reservation is a funding envelope, not an extra charge to add to measured usage. It covers all six service caps, all three gates and the retained two-unit allowance. The latter is preserved separately when a later organisation counter equals the local meter; the original certificate, failed service-audit log and independently reviewed carry-forward supplements remain unchanged. No general accounting tolerance or reservation release was introduced.

Authenticated Langfuse billing observed at **2026-11-06 21:48:53.360 UTC** shows 143,942 rolling units, 139,631 current-period units (hour-lagged), and **US$3.17 draft usage + US$29 subscription = US$32.17** for 3 November–3 December. Paid usage is US$0. The rolling counter exactly matches the local metered lower bound; the prior two-unit allowance remains separately retained, producing a conservative 143,944-unit equivalent. The rolling window, lagged billing-period counter and measured study emissions are distinct populations. The existing US$29 subscription is separate from incremental usage; a draft invoice is not a settled charge. No automatic top-up, plan change or contingency use occurred.

Selected immutable evidence (paths are relative to `artifacts/gpt4omini`):

| Evidence | SHA-256 |
|---|---|
| `outcomes/neither-conv-44/acceptance-spec.json` | `a208ae73625da74ac588037d10e40c40acbb3ed16f50ee2c48e2816b067a9056` |
| `outcomes/neither-conv-44/acceptance-standards.json` | `ac5d7e1849575b40b1fcaaee0545167bc9ed67cc6660ddd5dfea435936670b3a` |
| `outcomes/linking_only-conv-50/acceptance-spec.json` | `5501fc907d9856f301f43580342717570bce9db409cac0904dd122d8b96aa529` |
| `outcomes/linking_only-conv-50/acceptance-standards.json` | `9a2fdd1e3caab2ca60a94058587c347df722508de2de9c5d12a72eb922c95261` |
| `outcomes/linking_only-conv-44/spec-terminal-prefix.json` | `b266b0adc3e8b20397c4e295c23cd211d15a322520e8dc0ccca67f3b351bc15b` |
| `outcomes/linking_only-conv-44/standards-stopped-prefix.json` | `044f39e77fab923317e1a3c7c04ac5f05f8e7badc9b2e73c743b087a621e88b7` |
| `outcomes/linking_only-conv-44/standards-stopped-outcome-review.json` | `f850d651f3d2ab61678f284508c6c13d2c0b8876e5f46fd5a8c6bfc66bb7cc3c` |
| `verification/blk027-release/stop-linking44-finance/receipt.json` | `f6b8d90b9bba780e9c0fb4fd9ef23314b7b51fd2c053c15a72d8eb9a9b629797` |
| `verification/blk027-release/stop-linking44-finance/verification-spec.json` | `e19f8d5cb8a7cab113efdc3a601b3b079a0868d530ac152ba1518c9c6cbd98a7` |
| `outcomes/linking_only-conv-44/standards-stopped-finance.json` | `24c24520f24e63afe6a2a8002431ec538755eb694b958d131cabde055e6152e0` |
| `verification/blk027-release/capacity-after-linking44-stop.json` | `2282a97bd7f032907ef14880c8be83bc5fef0dbadd3da007f4e88abaf29bcd23` |

These stopped-outcome proofs are not scientific acceptance receipts. The original terminal phase, new reservation and refusal to advance remain in force.

## Recomputable artifacts and provenance

- [400-question four-condition numeric scores](gpt4omini-400q-four-condition-scores.jsonl).
- [558-question three-condition numeric scores](gpt4omini-558q-three-condition-scores.jsonl).
- [Population-specific aggregate results and receipt hashes](gpt4omini-eleven-cell-analysis.json).

These exports contain original question identities, categories and numeric scores only. They preserve corrected and historical policies separately. No 558-question four-condition result is produced from this incomplete inventory. Existing Full, conv-49, prior expansion reports, raw outputs, caches, receipts and DeepSeek history remain unchanged. Independent stopped-state, financial and data checks pass: 958 exact exported rows, 932 aggregate/category/contrast checks, native token/cost/action accounting and all 22 Experiment URLs were independently verified. All accepted scientific generation attempts succeeded without hidden retries; inherited classification history and earlier GET-only billing recovery remain separate. This documentation does not release paid execution.
