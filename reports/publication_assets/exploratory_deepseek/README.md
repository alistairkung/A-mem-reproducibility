# Exploratory DeepSeek Full A-MEM results

This supplementary collection supports Section 6.1, The Unplanned DeepSeek Detour. The table is the main deliverable. The optional two-panel figure compares observed scores across models while prominently identifying the comparison as exploratory.

## Results

All scores below are percentages of saved author-defined per-question metrics. All three DeepSeek lineages are completed and **Degraded**.

| Conversation | Questions | Alternative F1 | Alternative BLEU-1 | Historical F1 | Historical BLEU-1 |
|---|---:|---:|---:|---:|---:|
| conv-44 | 158 | 54.06 | 48.37 | 42.05 | 36.24 |
| conv-49 | 196 | 49.63 | 46.31 | 43.22 | 39.95 |
| conv-50 | 204 | 48.22 | 43.53 | 41.74 | 37.19 |
| Pooled (derived) | 558 | 50.37 | 45.88 | 42.35 | 37.89 |

The pooled row is derived in this reporting task from all 558 unrounded saved question scores, with equal question weighting. It is cross-checked against weighting the unrounded conversation means by 158, 196 and 204. It is not a previously published or independently accepted campaign total. CSV contains ten decimal places for numerical inspection; formatted tables and bar labels use two. Aggregation comparisons allow 1e-12 in normalized score or percentage units as indicated in code, solely for floating-point accumulation differences. Input fingerprints are exact.

## Table caption

**Exploratory DeepSeek Flash Full A-MEM results on three LoCoMo conversations.** F1 and BLEU-1 scores under both evaluation policies. Each conversation represents one completed but Degraded DeepSeek Full A-MEM lineage. These exploratory results are excluded from the primary GPT-4o-mini factorial analysis. The pooled row is a newly derived question-weighted aggregate.

## Figures

[Both evaluation policies](dual_policy_full_comparison.svg) show pooled Full A-MEM F1 and BLEU-1 on a common zero-based scale. Historical F1/BLEU-1 are 42.35/37.89 for DeepSeek Flash and 32.69/28.64 for GPT-4o-mini. Complementary scores are 50.37/45.88 and 36.91/32.81 respectively. The original [complementary-only figure](deepseek_vs_gpt4omini.svg) remains available.

### Original figure caption

**Exploratory cross-model comparison, not a controlled model benchmark.** Question-weighted alternative-reference F1 and BLEU-1 for DeepSeek Flash and GPT-4o-mini Full A-MEM on the same 558 questions from three conversations. The bars report descriptive saved-score aggregates, with zero-based axes. Different models, generation policies, providers and execution histories, including DeepSeek's Degraded recovery lineages, preclude causal or statistical superiority claims.

DeepSeek has higher observed overlap scores here, but this does not establish that it is the better language model. Each model–conversation combination contributes one stochastic build. There are no repeated builds for estimating model-level variability. Both models use Full A-MEM, but this is a cross-lineage exploratory comparison, separate from the twelve-cell GPT-4o-mini factorial analysis.

## Provenance and limitations

The source map in `inputs/evidence.json` and `source_manifest.json` includes exact original score-view hashes, phase hashes, separate acceptance records, source/config/scorer hashes, model endpoint and generation limits, and pinned documents with their last-change commits. The scientific documentation is pinned to Git commit `8485673183d7b8018c841082d075b21158002700`.

- [conv-44 reporting completion](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/run2-conv44-reporting-complete-20261104.md) establishes the Degraded completed Run2 lineage via `artifacts/run2/reporting-recovery/lineage-completion.json`. The original p2 receipt remains Incomplete on its reporting halt. Its score-view hash matches the preserved original phase inventory. The acceptance supplement verifies the original predictions, two views and remote reporting. This task preserves that distinction.
- [conv-49 completed checkpoint lineage](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/t8-conv49-baseline-20261103.md) supplies 196 original questions from `t8-full-conv49-checkpoint-child`, with its Degraded phase and independent completion audit.
- [conv-50 completed checkpoint lineage](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/t5-conv50-baseline-20261101.md) supplies 204 original questions from `pilot-conv50-checkpoint-child`, with its Degraded phase and final verification receipt.

DeepSeek used `deepseek-flash` at the native DeepSeek beta endpoint and the approved canonical-index-strings compatibility policy. The shared evolution output limit was 8,192 for conv-44 and 4,000 for conv-49 and conv-50. GPT-4o-mini used OpenRouter with OpenAI-only routing, native original schemas and a 4,096-token evolution allowance. All three DeepSeek lineages inherit failures and checkpoint recovery evidence. They form a heterogeneous exploratory summary. The common saved scorer revision is recorded in each lineage's evidence. Historical and alternative-reference views use the same predictions with their respective adversarial references.

The GPT-4o-mini comparison is derived directly from the accepted question-level JSONL at the pinned commit, and checked against the complete publication analysis. Its Full alternative-reference scores are 36.91% F1 and 32.81% BLEU-1. No costs, reservations, model calls or new score computations enter this reporting task.

## Reproduce

Use the parent publication environment in `../requirements.txt`, then run from the repository root:

```sh
python reports/publication_assets/exploratory_deepseek/generate_assets.py
python -m pytest -q reports/publication_assets/exploratory_deepseek/test_assets.py
```

The default pipeline reads compact, lossless numeric extracts in `inputs/question_scores.jsonl`; it does not require private experiment artifacts. These extracts carry original question IDs, categories and both saved metric views. The generator verifies their fingerprint, exact source/acceptance pins, identities, category and overall aggregates and the independently derived pooled values. No source predictions or scores are regenerated.

To independently re-extract the reporting inputs when the original immutable local evidence is available, use a temporary destination and compare it with the committed inputs:

```sh
python reports/publication_assets/exploratory_deepseek/verify_sources.py \
  --evidence-root /path/to/original/evidence-bearing/repository \
  --output-dir /tmp/deepseek-input-check
```

This offline extractor checks each original artifact's pinned bytes, completion status or supplement, scored question identities, unchanged predictions between views, zero metric failures and all saved aggregate values. It reads original artifacts without modifying them. The source manifest records both the numerical extract fingerprint and the original evidence fingerprints. Anyone without the private artifacts can regenerate and validate all publication assets from the committed numeric evidence, but cannot independently recheck the original raw execution receipts.

## Files and rendering

- `deepseek_results.csv`, `deepseek_results.tex` and `deepseek_results.docx` contain the compact table. The LaTeX fragment requires `booktabs` and `array`. The Word file reuses the explicit black/white/grey academic formatting from the main collection and renders as one A4 page.
- `deepseek_vs_gpt4omini.svg` and `.png` are the optional 15 cm-wide, two-panel figure. The PNG is 300 DPI.
- `generate_assets.py` reuses the accepted publication validator and academic table exporter. `verify_sources.py` supplies the original-evidence verification path.
- `source_manifest.json` records input, source, original-evidence and generated-output hashes and actual library versions. The existing scientific figures and primary tables are not regenerated.

Both the DOCX and the plotted figure were rendered and visually inspected. The LaTeX fragment compiled successfully. Repeat generation produces identical assets in the recorded environment. Independent Standards and Spec reviews verify the original evidence, derived aggregates, publication labels and separation from the primary experiment.
