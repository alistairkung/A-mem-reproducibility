# How one saved answer earns two A-MEM scores

The [five worked examples](five_examples.md) use original Category 5 answers from the twelve accepted GPT-4o-mini cells. Start with C to see one answer earn credit against both references while receiving a binary zero. E shows why even a prediction containing every word of the distractor can earn historical F1 of only 0.5.

## Provenance

The scientific revision is `8485673183d7b8018c841082d075b21158002700`. The three conversations are conv-44, conv-49 and conv-50. Each was evaluated in four gate configurations using the dated GPT-4o-mini model. The allowlist in the manifest identifies each local run directory and the SHA-256 of its scoring views. It includes the accepted fresh Linking Only / conv-44 completion. [Accepted twelve-cell report](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md) · [Accepted question-level scores](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-558q-four-condition-scores.jsonl)

A question ID joins the original LoCoMo sample and zero-based QA index to each condition’s `events.jsonl` question result, the two `scoring-views.json` records and the question-level report. For each example we also extracted the answer string from the event’s saved raw response. The excerpts are substrings of the dataset’s cited turns. A citation can supply the distractor for a different speaker, action or premise. The full conversation and retrieval prompts stay in the archive. [Original dataset](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/data/locomo10.json)

## How the scores were checked

1. **Saved evidence.** Match the question, prediction, reference, F1 and BLEU-1 across the original dataset and applicable archive and reporting fields. The two policy IDs are `author-legacy-c5-v1` (historical) and `author-corrected-v1` (complementary). On Category 5 the former uses the supplied distractor and the latter uses `Not mentioned in the conversation`. [Reference selection](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/load_dataset.py) · [Dual-view wrapper](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/scoring.py)
2. **Frozen implementation.** The verifier reads the Git objects directly, loads the original QA class and executes the released `score_prediction`, `calculate_metrics`, `simple_tokenize`, `calculate_bleu_scores` and `is_not_mentioned` definitions. Import-time download code is bypassed. Other metrics have inert call boundaries. Only F1, BLEU-1 and binary correctness are recomputed. [Frozen author functions](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/utils.py)
3. **Independent arithmetic.** A separate calculation reconstructs the F1 sets, NLTK token sequences, unigram counts and length penalty. It compares every displayed intermediate against the structured extract and both final values against the unrounded scientific records. It shares the experiment’s NLTK tokenizer, and calculates BLEU without calling NLTK’s BLEU scorer. [Offline verifier](verify_examples.py) · [Exact example data](examples.json)
4. **Fresh Langfuse GETs.** On 9 November 2026, authenticated CLI reads returned the five `A-MEM/question` observations and both saved-result Experiment items for each. The question observation’s input carries the offered distractor and its output carries the complementary reference, policy and metrics. Each item’s output, expected output, policy, run, original trace association and three observation-bound score values matched the local evidence. The two views can share an Experiment item ID for the same question, so the lookup used the Experiment ID and item ID together. Raw cloud payloads were discarded. The saved readback projections include the UTC times, observation IDs and score IDs. Rerunning the offline verifier checks these projections locally. [Readback and local results](verification_results.json) · [Langfuse CLI](https://langfuse.com/docs/api-and-data-platform/features/cli)

### Reading the derivations

**F1.** For the nonempty strings here the author strips surrounding whitespace, lowercases, replaces each of `.`, `,`, `!` and `?` with a space, and splits on whitespace. Precision is the intersection size divided by the unique prediction-token count. Recall uses the unique reference-token count. F1 is their harmonic mean, or zero for zero overlap. An empty set also gives zero F1. Articles, hyphens and apostrophes survive. B shows the actual repeated word `something`.

**BLEU-1.** NLTK 3.10.4 receives lowercased strings via `word_tokenize`, with its default English sentence and word tokenisation. For the single reference, each unigram contributes the smaller of its two occurrence counts. With prediction length *c* and reference length *r*, the brevity penalty for these nonempty predictions is exp(min(0, 1 − r/c)). The author calls `sentence_bleu` with weights `(1, 0, 0, 0)`, default `auto_reweigh=False`, and `SmoothingFunction().method1` (epsilon 0.1). With zero matching unigrams NLTK returns zero **before smoothing**. Otherwise method 1 leaves positive unigram precision intact. Zero counts at higher orders can be smoothed, but their weights are zero. The final operation is BP × exp(log(unigram precision)). The audit preserves the implementation’s floating-point order. All selected strings are nonempty and all ten calls reproduce successfully. [NLTK implementation](https://www.nltk.org/_modules/nltk/translate/bleu_score.html)

**Binary adversarial correctness.** The author lowercases the prediction and looks for either substring `not mentioned` or `no information available`. A simultaneous occurrence of the lowercased distractor, stripped of outer spaces and periods, disqualifies the response unless the distractor itself starts with `not mentioned`. This rule is independent of the selected lexical reference. It tests a response pattern. Whether the question’s premise fits the dialogue requires reading the cited turn.

## Selection

The sampling frame contains 121 original adversarial questions × four configurations. Pools were formed across all 484 predictions and can overlap. Counts below precede the choice of five distinct IDs. Selection favoured interpretable evidence turns, multiple configurations and different token behaviours. The aggregate rankings played no part. [Selection rules, allowlist and chosen IDs](selection_manifest.json)

| Pool | Accepted predictions | Distinct questions |
| --- | ---: | ---: |
| A · Exact abstention, historical F1 ≤ 0.25 | 305 | 93 |
| B · Exact distractor, complementary F1 ≤ 0.25 | 154 | 62 |
| C · Both F1 values strictly intermediate, neither raw reference matched | 5 | 2 |
| D · Clean abstention with different words | 0 | 0 |
| D substitute · Same words with a final period | 1 | 1 |
| E · Neither raw reference matched and within-policy F1/BLEU-1 gap ≥ 0.05 | 9 | 4 |

The entire response inventory breaks down into 315 exact canonical abstentions, 160 exact distractors, five answers joining the abstention and distractor with “or”, one canonical abstention with a period, and three punctuation variants of distractors. This inventory rules out a hidden standalone paraphrase among the remaining responses. C uses one of the mixed answers. D uses the sole punctuation variant of the canonical abstention.

## Full-population check

The two scoring views reuse the same prediction for **all 2,232 question–configuration pairs**. The complete saved metric dictionaries and references agree on all 437 Category 1–4 questions in every condition (1,748 paired records). Only the 121 Category 5 questions switch reference. The published question-level F1 and BLEU-1 match their cell files throughout.

| Configuration | Historical F1 · `author-legacy-c5-v1` | Complementary F1 · `author-corrected-v1` |
| --- | ---: | ---: |
| Neither | 30.03% | 39.00% |
| Linking Only | 30.21% | 37.34% |
| Evolution Only | 29.29% | 35.86% |
| Full A-MEM | 32.69% | 36.91% |

Each percentage is 100 times the sum of the 558 individual F1 values divided by 558. The verifier matches all eight full-precision published means before display rounding. Full A-MEM leads under historical scoring, and Neither leads under complementary scoring. Because the predictions are fixed and all other categories contribute identical terms, the entire change in ranking comes from the Category 5 reference switch. The five deliberately selected examples illustrate the mechanics. Population conclusions here use all 558 questions. [Published aggregate data](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-analysis.json)

## Run offline

From the repository root, with the accepted commit in the local Git object database, use the study environment and its cached English Punkt tables.

```sh
.venv/bin/python -B reports/adversarial_scoring_audit/verify_examples.py
```

The default run reads the twelve archived cells under `artifacts/gpt4omini`. If stored in a separate study checkout, pass `--archive-root /path/to/study-checkout`. A clone with the accepted Git objects and NLTK 3.10.4 plus its local English `punkt_tab` data can run `--without-archive` to verify the extracts, scorer, arithmetic, saved readback projections and published aggregates. The archive is required to repeat the original-event joins, all-cell prediction comparison and selection census.
