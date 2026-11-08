# Slide storyboard

The slide numbers follow the recording script and the PowerPoint notes. Section references point to the approved coursework report. Technical-report headings are reproduced here as published, including its terminology for the complementary reference.

[Approved report](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/final_coursework/AMEM_FTEC5660_Report.pdf) · [Accepted twelve-cell report](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md) · [Recording script](speaker_script.md)

## Slide 1 — Reproducing A-MEM

Introduce the two research questions. Target 0:35.

**On screen** — Title and two research questions.

**Narration** — Identify the absent ablation and introduce scoring as a question that emerged during reproduction. [Read slide 1](speaker_script.md#slide-1--reproducing-a-mem).

**Scientific evidence** — Report §§1, 3.1, 7. Accepted technical report, “Protocol and population; Interpretation”.

## Slide 2 — How A-MEM works

Explain the frozen memory workflow. Target 1:05.

**On screen** — Editable insertion, action and QA diagram.

**Narration** — Use the new-job example to distinguish actions on the new note and on older neighbours. Follow retrieval after construction. [Read slide 2](speaker_script.md#slide-2--how-a-mem-works).

**Scientific evidence** — Report §2.1. Accepted technical report, “Protocol and population”.

**Publication sources** — [01_configurations.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/01_configurations.csv) · [README.md](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/architecture/README.md).

## Slide 3 — The missing ablation

Explain what Evolution Only adds. Target 1:00.

**On screen** — Editable 2 × 2 factor table.

**Narration** — Compare adjacent cells within each linking row. State the temporal-reasoning hypothesis. [Read slide 3](speaker_script.md#slide-3--the-missing-ablation).

**Scientific evidence** — Report §4.1. Accepted technical report, “Protocol and population; Interpretation”.

**Publication sources** — [01_configurations.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/01_configurations.csv).

## Slide 4 — Experimental wrapper and fidelity

Establish what the replay verifies. Target 1:10.

**On screen** — Verified nested wrapper diagram with editable replay counts.

**Narration** — Follow the decision through the gates, describe cell isolation, and explain why identical recorded responses can test implementation fidelity. [Read slide 4](speaker_script.md#slide-4--experimental-wrapper-and-fidelity).

**Scientific evidence** — Report §§2.2, 4.2–4.3. Accepted technical report, “Protocol and population”.

**Publication sources** — [amem_wrapper_architecture.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/architecture/amem_wrapper_architecture.svg) · [README.md](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/architecture/README.md).

**Replay evidence** — [T7 action-gate equivalence](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/docs/reproducibility/t7-action-gates.md).

## Slide 5 — Experimental population and metrics

Define the matched population and outcomes. Target 0:55.

**On screen** — Editable population table and metric definitions.

**Narration** — Explain preselection, one build per cell, per-question weighting and the three measures. [Read slide 5](speaker_script.md#slide-5--experimental-population-and-metrics).

**Scientific evidence** — Report §§1.1, 3.2–3.4. Accepted technical report, “Protocol and population; Results by conversation”.

**Publication sources** — [06_conversation_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/06_conversation_results.csv).

## Slide 6 — Historical and complementary adversarial evaluation

Demonstrate the two reference objectives. Target 1:10.

**On screen** — Editable synthetic salary example.

**Narration** — Map each salary answer to its reference. Reuse the same predictions for both overlap scores and explain binary abstention. [Read slide 6](speaker_script.md#slide-6--historical-and-complementary-adversarial-evaluation).

**Scientific evidence** — Report §3.4. Accepted technical report, “Protocol and population; Interpretation”.

Alice’s salary is a synthetic teaching example supplied in the presentation brief.

## Slide 7 — Did we reproduce the paper’s conclusion?

Answer the historical reproduction question. Target 1:20.

**On screen** — Scoring comparison and editable choice counts.

**Narration** — Read the three historical bars, switch to the complementary ranking, then compare the two correct-abstention counts. [Read slide 7](speaker_script.md#slide-7--did-we-reproduce-the-papers-conclusion).

**Scientific evidence** — Report §§5.1, 7.1–7.2. Accepted technical report, “Overall question-weighted scores; Interpretation”.

**Publication sources** — [01_scoring_comparison.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/figures/01_scoring_comparison.svg) · [02_overall_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/02_overall_results.csv).

## Slide 8 — Which mechanisms helped?

Test mechanism-level hypotheses by question type. Target 1:10.

**On screen** — Category heatmap and three editable contrasts.

**Narration** — Read the multi-hop and temporal rows and distinguish those results from the pooled contrast. [Read slide 8](speaker_script.md#slide-8--which-mechanisms-helped).

**Scientific evidence** — Report §5.2. Accepted technical report, “Corrected matched contrasts; Category contrasts (pp); Interpretation”.

**Publication sources** — [02_category_heatmap.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/figures/02_category_heatmap.svg) · [03_factorial_contrasts.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/03_factorial_contrasts.csv) · [04_category_performance.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/04_category_performance.csv).

## Slide 9 — Factorial interaction

Interpret the descriptive interaction. Target 0:55.

**On screen** — Interaction plot and editable difference of differences.

**Narration** — Compare the vertical gaps with linking off and on. Explain the sign and the different conversation results. [Read slide 9](speaker_script.md#slide-9--factorial-interaction).

**Scientific evidence** — Report §§5.2, 7.3. Accepted technical report, “Corrected matched contrasts; Interpretation”.

**Publication sources** — [04_factorial_interaction.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/figures/04_factorial_interaction.svg) · [03_factorial_contrasts.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/03_factorial_contrasts.csv) · [06_conversation_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/06_conversation_results.csv).

## Slide 10 — Is additional complexity worth its cost?

Compare quality and accepted-build model charges. Target 1:20.

**On screen** — Dual cost–F1 plot with editable retrieval and token counts.

**Narration** — Read the filled points under each policy. Connect retrieval expansion to answer-input overhead. [Read slide 10](speaker_script.md#slide-10--is-additional-complexity-worth-its-cost).

**Scientific evidence** — Report §5.3. Accepted technical report, “Retrieval, memory actions and cost; Spending and retained evidence”.

**Publication sources** — [06_dual_scoring_f1_vs_cost.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/figures/06_dual_scoring_f1_vs_cost.svg) · [05_cost_retrieval.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/05_cost_retrieval.csv) · [07_dual_scoring_cost_performance.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/07_dual_scoring_cost_performance.csv).

## Slide 11 — The unplanned DeepSeek detour

Explain the unplanned provider detour. Target 1:15.

**On screen** — Editable timeline and exploratory comparison figure.

**Narration** — Explain the initial choice, structured-output failures, Degraded lineages and decision to return to GPT-4o-mini. [Read slide 11](speaker_script.md#slide-11--the-unplanned-deepseek-detour).

**Scientific evidence** — Report §6.1. Accepted technical report, “Interpretation (GPT-4o-mini baseline only)”.

**Publication sources** — [deepseek_vs_gpt4omini.svg](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/exploratory_deepseek/deepseek_vs_gpt4omini.svg) · [deepseek_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/exploratory_deepseek/deepseek_results.csv) · [README.md](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/exploratory_deepseek/README.md) · [02_overall_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/02_overall_results.csv).

## Slide 12 — Operational reliability versus research focus

Separate scientific cost from operational exposure. Target 1:00.

**On screen** — Editable cost scopes, lessons and final-cell receipt.

**Narration** — Describe provenance, bounded recovery and the clean first transmissions. Distinguish identified charges from the exposure upper bound. [Read slide 12](speaker_script.md#slide-12--operational-reliability-versus-research-focus).

**Scientific evidence** — Report §§4.3, 6.2. Accepted technical report, “Final cell verification; Spending and retained evidence”.

**Publication sources** — [05_cost_retrieval.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/05_cost_retrieval.csv).

## Slide 13 — Conclusions

State what reproduced and limit the inference. Target 1:05.

**On screen** — Editable findings and closing sentence.

**Narration** — Distinguish replay, historical ordering, absolute scores and complementary results. Name sample, retrieval and stochastic limits. [Read slide 13](speaker_script.md#slide-13--conclusions).

**Scientific evidence** — Report §§7.1–7.3. Accepted technical report, “Interpretation”.

**Publication sources** — [02_overall_results.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/02_overall_results.csv) · [03_factorial_contrasts.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/03_factorial_contrasts.csv) · [04_category_performance.csv](https://github.com/alistairkung/A-mem-reproducibility/blob/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619/reports/publication_assets/tables/04_category_performance.csv).
