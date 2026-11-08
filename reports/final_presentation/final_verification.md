# FTEC5660 A-MEM final verification

**READY WITH MINOR CAVEATS · 8 November 2026.** The scientific results and recording package pass. Full cost **$0.00144540 more** than Linking Only across the accepted builds. The historical frontier on slide 10 is correct. One timed rehearsal and the report’s manual student details remain.

## A. Scientific verification

| Audit category | Result | Evidence and check |
|---|---|---|
| Population and eligibility | PASS | Original turn IDs and all ordered question IDs, indices, questions, references, evidence and categories matched the dataset in each cell. Twelve distinct fresh builds and cache identities. Two accepted Degraded exceptions are documented below. |
| Historical and complementary metrics | PASS | Independently rescored the saved predictions for all 2,232 primary answers under both policies. Maximum absolute difference from saved F1/BLEU-1 was below `2e-16` on the 0–1 scale. |
| Categories, paired contrasts and abstention | PASS | All 20 heatmap labels, five category sizes, category-weighted means, four binary counts and the interaction signs agree. Calculations appear in B. |
| Pareto frontier and retrieval | PASS | Joined 18,480 unique accepted generation IDs to settled ledger entries. Applied the dominance test to unrounded costs and pooled F1. Recounted expanded entries and provider-reported answer prompt tokens. |
| Deterministic Full fidelity | PASS | Rehashed both original replay receipts. After removing the implementation label the receipts are equal, including parent/child recording hashes, 568 per-insertion comparisons, 1,544 matched requests and 204 answers. |
| Financial scopes and final replacement | PASS | Read the historical and final ledgers in immutable read-only mode. The new phase, two acceptances, readback reconciliation and independent programme close match the digests in the accepted report. |
| Exploratory DeepSeek comparison | PASS | Independently rescored the three completed Full lineages, verified each phase and acceptance digest, and kept these 558 questions outside the primary dataset. |
| Report, slides, notes and recording copy | PASS | The 10-page report, all slide XML and notes, six source vectors, 13 slide renders and 13 Word pages were inspected or compared. The script agrees across the three recording formats. |
| Actual elapsed narration | UNVERIFIED | The 14:00 target and word-count estimates pass. Recording length requires a timed delivery. |
| Submission identification | FAIL · administrative | The approved PDF retains manual name and student-ID fields on page 1. Fill them in the private submission copy before upload. |

### Authority and selection

- **Manuscript and presentation.** The final coursework PDF is revision `c7c2b0e`, SHA-256 `662720d75e1953d850e5c6973eedb21f78ff90119c2ec98da4e82ffcbc93bf4f`. The audited presentation, notes and two script formats are revision `433fb75`. [Manuscript](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/final_coursework/AMEM_FTEC5660_Report.pdf) · [Presentation](https://github.com/alistairkung/A-mem-reproducibility/blob/433fb75a34790302c4b754f1eccbe69c97282fa8/reports/final_presentation/AMEM_FTEC5660_Presentation.pptx) · [Narration](https://github.com/alistairkung/A-mem-reproducibility/blob/433fb75a34790302c4b754f1eccbe69c97282fa8/reports/final_presentation/speaker_script.md)
- **Frozen population and scoring.** `manifests/fallback.json` binds the dataset, seed 42, original indices and three conversations. The full release has 10 conversations, 5,882 turns and 1,986 questions. Each accepted phase binds the fingerprint of the same manifest and configuration. The model was `openai/gpt-4o-mini-2024-07-18`, routed by OpenRouter to OpenAI. The observed request temperatures were 0.7, or 0.5 for Category 5 answering. The output limits were 4,096 for shared decisions and 1,000 for other stages. [Population manifest](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/manifests/fallback.json) · [Configuration](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/config/gpt4omini.json) · [Frozen reference rules](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/load_dataset.py) · [Metric definitions](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/utils.py)
- **Accepted build inventory.** The twelve-cell analysis at `8485673` identifies the twelve selected cell costs and the winning replacement. The frozen selection manifest defines the sample. Eligibility comes from the two signed-off axis receipts per cell. Local evidence below uses `G = artifacts/gpt4omini` and `F = G/cells/linking_only-conv-44/final-eight-hour/attempt-1`. Eleven receipt pairs are at `G/outcomes/<cell>/acceptance-{standards,spec}.json` (Full uses the conversation ID as its cell key). The winning pair is at `F/acceptance-{standards,spec}.json`. Each identifies the exact run. [Accepted report](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md) · [Twelve-cell analysis](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-analysis.json) · [558 matched score rows](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-558q-four-condition-scores.jsonl)
- **Raw evidence.** For each selected run, read `events.jsonl`, `phase.json`, `run.json`, `scoring-views.json`, and the sealed memory/cache evidence. The event journal’s saved prediction matched both scoring views. Consult `G/budget.sqlite`, `F/../finance/budget.sqlite`, `F/reconciliation.json`, `F/standards-closing-capacity.json`, and `G/verification/final-eight-hour-finance/final-programme-reconciliation.json` for costs. These local, Git-ignored records were present. Public charts were checked against the recalculation. [Public evidence digests](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md#verification-receipts)
- **Replay and DeepSeek.** Full replay used `artifacts/replays/t7-reviewed-{reference,candidate}/verification.json` and `artifacts/t7-equivalence-comparison.json`. Both implementations consumed the same archived conv-50 responses. The exploratory source map gives separate raw score, phase and acceptance paths for each DeepSeek lineage. [Replay provenance](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/t7-action-gates.md) · [Exploratory evidence map](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/exploratory_deepseek/inputs/evidence.json)

**Eligibility exceptions.** Ten primary builds were accepted Clean. Full / conv-44 was accepted Degraded because its compatibility lineage retained failures and financial holds. Its scientific build had complete QA and no provider-generation failure. Neither / conv-50 had a sealed Incomplete reporting phase and a separately authorised Degraded acceptance for two adjacent binary64 BLEU-4 readback values. Its original final-memory and cache-proof receipt files are absent as documented. The supplement verifies the original 568-note cache and all 204 questions. This audit checked its sealed cache bytes and recalculated its F1 and BLEU-1 from the saved answers. Both exceptions are included once in the accepted twelve. Earlier Linking Only / conv-44 attempts stopped at 231 notes, 87 answers after continuation, or 566 notes in the earlier replacement. They contribute zero answers to the comparison. [BLK-027 acceptance](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-linking44-transport-stop.md#blk-027-acceptance) · [Final selection](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md#final-cell-verification)

## B. Numerical reconciliation

**How the scores were checked.** Each saved prediction was paired with the original QA record. F1 used distinct tokens after the frozen lowercasing and punctuation handling. BLEU-1 used the archived NLTK tokenizer and the author’s unigram weights and smoothing. For Category 5, the historical reference is the supplied distractor and the complementary reference is the no-information response. Binary correctness recognises either accepted abstention phrase and rejects an answer that also supplies the trap. Other categories share the same reference. The pooled percentage is 100 times the mean of 558 question scores. A difference between two percentages is given in percentage points (pp).

**Pooled metrics.** Values are ordered as historical F1 / BLEU-1, then complementary F1 / BLEU-1. The discrepancy is calculated at display precision.

| Condition | Reported (%) | Recalculated (%) | Correct abstentions, reported = recalculated | Discrepancy / disposition |
|---|---|---|---:|---|
| Neither | 30.03 / 25.95 / 39.00 / 35.01 | 30.02713 / 25.94708 / 39.00301 / 35.01065 | 86/121 | 0.00 pp · retain |
| Linking Only | 30.21 / 26.43 / 37.34 / 33.57 | 30.20565 / 26.43294 / 37.34248 / 33.57407 | 80/121 | 0.00 pp · retain |
| Evolution Only | 29.29 / 25.69 / 35.86 / 32.29 | 29.28682 / 25.68706 / 35.85615 / 32.28810 | 79/121 | 0.00 pp · retain |
| Full | 32.69 / 28.64 / 36.91 / 32.81 | 32.69135 / 28.64085 / 36.91176 / 32.81203 | 71/121 | 0.00 pp · retain |

**Slide 8 heatmap.** Each cell is displayed F1 / independently recalculated F1 (%). Every label agrees at two decimals. Weighting the unrounded rows by their question counts reproduces each pooled F1 and BLEU-1 to within `1e-12` pp, under both policies.

| Category | Questions | Neither | Linking Only | Evolution Only | Full |
|---|---:|---:|---:|---:|---:|
| Multi-hop | 99 | 16.86 / 16.85621 | 20.25 / 20.25292 | 15.72 / 15.71803 | 17.54 / 17.54403 |
| Temporal | 89 | 36.61 / 36.61373 | 31.62 / 31.62284 | 34.17 / 34.17413 | 34.29 / 34.29403 |
| Open-domain | 27 | 14.37 / 14.37001 | 12.78 / 12.78283 | 8.09 / 8.08901 | 15.92 / 15.91511 |
| Single-hop | 222 | 34.82 / 34.81832 | 33.75 / 33.74754 | 32.18 / 32.18260 | 35.94 / 35.93562 |
| Adversarial | 121 | 72.05 / 72.05483 | 67.61 / 67.60776 | 66.51 / 66.50583 | 61.16 / 61.15966 |

| Complementary contrast | Reported | Recalculated | Disposition |
|---|---:|---:|---|
| Multi-hop, Linking Only − Neither | +3.40 pp | +3.39672 pp | Agrees |
| Temporal, Evolution Only − Neither | −2.44 pp | −2.43960 pp | Agrees |
| Temporal, Full − Linking Only | +2.67 pp | +2.67119 pp | Agrees |
| Overall, Linking Only − Neither | −1.66 pp | −1.66053 pp | Agrees |
| Overall, Evolution Only − Neither | −3.15 pp | −3.14686 pp | Agrees |
| Overall, Full − Linking Only | −0.43 pp | −0.43072 pp | Agrees |
| Overall, Full − Evolution Only | +1.06 pp | +1.05562 pp | Agrees |
| Four-term interaction, F1 | +2.72 pp | +2.71615 pp | Agrees |
| Four-term interaction, BLEU-1 | +1.96 pp | +1.96051 pp | Agrees |

Slide 9 uses `(Full − Linking Only) − (Evolution Only − Neither)`. Evolution’s observed F1 change moves from −3.14686 pp without linking to −0.43072 pp with linking. The smaller loss produces a positive interaction. The conversation-specific F1 interactions were **+4.75002**, **−0.30709** and **+4.04557** pp in conv-44, conv-49 and conv-50 respectively. One build per cell supports descriptive contrasts only.

**Cell coverage and costs.** Each condition has 675 + 509 + 568 = **1,752 turns** and 158 + 196 + 204 = **558 answers**. The rows below identify the per-conversation share of each unrounded model charge. Every value matches the accepted cost inventory. Entries include duplicates after link expansion. Tokens are native input tokens from answer calls only.

| Condition | conv-44 USD | conv-49 USD | conv-50 USD | Total USD | Entries / 558 → displayed mean | Answer input tokens | Historical / complementary frontier |
|---|---:|---:|---:|---:|---|---:|---|
| Neither | 0.35561970 | 0.27892170 | 0.31590645 | 0.95044785 | 5,580 / 558 → 10.00 | 747,640 | Efficient / Efficient |
| Linking Only | 0.39063510 | 0.32385990 | 0.36489600 | 1.07939100 | 11,242 / 558 → 20.15 | 1,511,478 | Efficient / Dominated |
| Evolution Only | 0.35714685 | 0.28014945 | 0.31603155 | 0.95332785 | 5,580 / 558 → 10.00 | 749,026 | Dominated / Dominated |
| Full | 0.39390465 | 0.31996545 | 0.36696630 | 1.08083640 | 11,156 / 558 → 19.99 | 1,503,791 | Efficient / Dominated |

**Slide 10.** Full − Linking Only = $1.08083640 − $1.07939100 = **+$0.00144540**, with **+2.48571 pp** historical F1. Both costs round to $1.08 at cent precision. At full precision, neither condition dominates the other historically. Neither dominates Evolution Only under historical F1 and all three alternatives under complementary F1. The two panels use identical accepted-build costs.

| Other material quantity | Reported | Independent result | Discrepancy / disposition |
|---|---|---|---|
| Full replay, insertions / requests / answers | 568 / 1,544 / 204 | 568 hashes / 1,544 recorded requests / 204 answers | Exact · direct receipt comparison |
| Accepted GPT-4o-mini model charges | ≈ $4.06 | $4.06400310 across 18,480 identified generations | $0.00 at cents |
| Campaign identified model charges | ≈ $4.70 | $4.30760295 historical + $0.39063510 final = $4.69823805, across 21,143 settled IDs | $0.00 at cents |
| Campaign conservative exposure | ≈ $10.46 | $4.808497 conservative model + $5.648560 service upper bound = $10.457057 | $0.00 at cents |
| Final fresh Linking Only / conv-44 | 675 memories, 158 answers, 1,666 requests, 0 retries | 675 metadata + 675 shared decisions + 158 keyword calls + 158 answers, all first transmission | Exact · clean replacement `gpt4omini-linking_only-conv44-final-r1` |
| DeepSeek vs GPT-4o-mini Full, complementary F1 | 50.37% / 36.91% | 50.36716% / 36.91176% | 0.00 pp at display precision |
| Same comparison, complementary BLEU-1 | 45.88% / 32.81% | 45.87840% / 32.81203% | 0.00 pp at display precision |

The campaign model bound includes five unresolved reservations totalling **$0.099644**, plus conservative settlement rounding. Service is the carried-forward measured upper bound of **$4.868240** plus **$0.780320** for the final cell. Held reservations are included once. The separate full-earmark commitment and the existing subscription are outside the $10.46 measure. The close establishes exposure at the accounting cutoff. A final invoice is a separate quantity.

All three DeepSeek Full lineages were accepted Degraded. Conv-44 has a separate reporting-completion supplement over its sealed Incomplete export phase. Conv-49 and conv-50 have completed checkpoint lineages. Their complementary F1 / BLEU-1 pairs were 54.06 / 48.37, 49.63 / 46.31 and 48.22 / 43.53 respectively. The pooled row weights 158, 196 and 204 questions. Provider, contracts, generation limits and recovery histories differ from the primary campaign.

## C. Presentation consistency

All slide numbers, section references, titles, cue text, timing lines and spoken paragraphs matched between their applicable formats. The six SVG embeddings matched their committed sources. All 13 fresh LibreOffice slide renders were pixel-identical to the inspected production renders. The labels, legends and paragraph breaks are legible at presentation size. No material clipping or overlap was observed.

| Slide | Report sections | Claim or visual checked | Result |
|---:|---|---|---|
| 1 | 1, 3.1, 7 | Missing condition, temporal hypothesis and cost question | PASS |
| 2 | 2.1 | Up to five construction neighbours, shared decision, target fields, top-ten initial QA retrieval | PASS |
| 3 | 4.1 | Both factors, four cells, added Evolution Only quadrant | PASS |
| 4 | 2.2, 4.2–4.3 | Gated author workflow and recorded conv-50 Full replay | PASS |
| 5 | 1.1, 3.2–3.4 | Three conversations, per-condition totals, fresh state and metric definitions | PASS |
| 6 | 3.4 | Alice’s $150,000 salary is explicitly synthetic. Only the Category 5 reference changes. | PASS |
| 7 | 5.1, 7.1–7.2 | All eight F1 bars, abstention counts and historical ordering | PASS |
| 8 | 5.2 | All 20 heatmap labels and the three highlighted F1 differences | PASS |
| 9 | 5.2, 7.3 | Vertical gaps, interaction sign, conversation variation and absence of a significance claim | PASS |
| 10 | 5.3 | Unrounded dominance, identical x-coordinates across panels, entries and answer tokens | PASS |
| 11 | 6.1 | Four plotted model scores, Degraded status and prominent exploratory qualification | PASS |
| 12 | 4.3, 6.2 | Three cost scopes, first-completion rule and clean final cell | PASS |
| 13 | 7.1–7.3 | Replay, directional finding, absolute-score limits, sample, retrieval and stochastic limitations | PASS |

**Paper comparison.** Table 3 reports five category pairs for each configuration. Every category gives Neither < Linking Only < Full on both metrics, which implies the same ordering under any common positive category weighting. Our historical pooled F1 follows that direction. Table 3 supplies no pooled numeric target and does not fully specify the matching question IDs or retrieval depths. For example, our historical Full multi-hop F1 was 17.54%, versus 27.02% in Table 3. None of our five complementary F1 rows has the paper’s complete three-condition ranking. [Xu et al., Table 3](https://arxiv.org/html/2502.12110v11#S4.T3)

## D. Findings and corrections

- **BLOCKER** — No scientific or recording blocker identified.
- **IMPORTANT** — The page 1 student-name and ID placeholders require the student’s own details before submission. The source report records these as manual fields.
- **OPTIONAL** — When narrating slides 7 and 13, “our pooled result follows the ordering in the paper’s five categories” makes the Table 3 comparison explicit.

This verification record is the only repository addition. The evidence supports retaining the submitted report, presentation and narration. Tests used archived events, saved predictions, local tokenizers, sealed receipts, read-only ledgers, document extraction and rendering. The audit issued zero model requests and executed zero experimental cells.

## E. Recording readiness

The 13 section targets sum to **840 seconds**. The script contains **1,751 spoken words**, excluding delivery cues, section headings and timing lines. The 14-minute target corresponds to **125.1 words/minute including pauses**. At 120, 130 and 140 spoken words/minute, the estimated speech-only durations are **14:36, 13:28 and 12:30**. At 130, allow about 32 seconds for transitions to reach 14:00, or 1:32 before the 15-minute cap.

**Remaining actions.** Do one timed rehearsal with slides and pointer pauses, aiming for 14:00. If it finishes under 15:00 at a comfortable pace, record that version. No cuts are indicated by the word count. If the rehearsal overruns, the single-hop/open-domain aside at the end of slide 8 and the optional final future-work sentence before the closing line on slide 13 can be omitted without losing the central result. Fill the report’s name and ID in the private submission copy before upload.
