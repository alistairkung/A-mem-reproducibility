# Five worked Category 5 examples

Each table uses one saved prediction twice. Scores are on the 0–1 scale. Decimals preserve the stored numeric precision. The turn excerpts come from the original dataset’s evidence pointers. The [audit method and full-population results](README.md) explain the scoring rules and selection.

## A. Correct abstention

**Why did Audrey sign up for a workshop about car maintenance?**

`conv-44:qa:126` · Full A-MEM · `conv-44`, original QA index 126 (zero-based). Run `gpt4omini-full-conv44-r0-p0`.

Evidence `D6:2` · Audrey, excerpt · “I signed up for a workshop about bonding with my pet next month.”

| Field | Historical evaluation | Complementary evaluation |
| --- | --- | --- |
| Scoring policy | `author-legacy-c5-v1` | `author-corrected-v1` |
| Model prediction | `Not mentioned in the conversation` | `Not mentioned in the conversation` |
| Reference | `Strengthen the bond with her pets` | `Not mentioned in the conversation` |
| F1 precision | 0.2 | 1.0 |
| F1 recall | 0.16666666666666666 | 1.0 |
| **F1** | 0.1818181818181818 | 1.0 |
| **BLEU-1** | 0.1637461506155964 | 1.0 |

**F1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Normalised prediction tokens | `["not", "mentioned", "in", "the", "conversation"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Normalised reference tokens | `["strengthen", "the", "bond", "with", "her", "pets"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Unique prediction tokens | `["conversation", "in", "mentioned", "not", "the"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Unique reference tokens | `["bond", "her", "pets", "strengthen", "the", "with"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Set intersection | `["the"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Precision (P) | 1/5 | 5/5 |
| Recall (R) | 1/6 | 5/5 |
| 2PR / (P + R) | 2 × (1/5) × (1/6) / ((1/5) + (1/6)) = 0.1818181818181818 | 2 × (5/5) × (5/5) / ((5/5) + (5/5)) = 1.0 |

**BLEU-1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Prediction sequence | `["not", "mentioned", "in", "the", "conversation"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Reference sequence | `["strengthen", "the", "bond", "with", "her", "pets"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Clipped matches by token | `{"the": 1}` | `{"not": 1, "mentioned": 1, "in": 1, "the": 1, "conversation": 1}` |
| Lengths (prediction, reference) | 5, 6 | 5, 5 |
| Unigram precision | 1/5 = 0.2 | 5/5 = 1.0 |
| Brevity penalty (BP) | exp(min(0, 1 − 6/5)) = 0.8187307530779819 | exp(min(0, 1 − 5/5)) = 1.0 |
| Method 1 | Positive unigram precision retained | Positive unigram precision retained |
| BLEU-1 | BP × exp(log(1/5)) = 0.1637461506155964 | BP × exp(log(5/5)) = 1.0 |

**Binary adversarial correctness · 1**

Audrey describes a workshop on bonding with her pet. The saved abstention matches the complementary reference exactly, but it also shares the article `the` with the distractor. Historical BLEU-1 discounts that single match again because the five-token prediction is shorter than the six-token reference.

Exact saved-score, frozen-scorer, arithmetic and live readback checks passed. [Question trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/c5cb3bb5bedc45a58bee3c3f53d0d768?observation=bb70b2797bee74d2) · [Historical item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/8b598bf8a3f30534ef3375a797b7721a?observation=0ca42d433367a22f) · [Complementary item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/ed74259d0e9b33e791aa1ecfce4dc644?observation=b5f7c085a44b6835)

## B. Unsupported distractor selected

**What does Dave find satisfying about destroying old cars?**

`conv-50:qa:183` · Evolution Only · `conv-50`, original QA index 183 (zero-based). Run `gpt4omini-evolution_only-conv50-r0-p0`.

Evidence `D21:10` · Dave, excerpt · “I love being able to transform something old and beat-up into something beautiful.”

| Field | Historical evaluation | Complementary evaluation |
| --- | --- | --- |
| Scoring policy | `author-legacy-c5-v1` | `author-corrected-v1` |
| Model prediction | `Transforming something old and beat-up into something beautiful` | `Transforming something old and beat-up into something beautiful` |
| Reference | `Transforming something old and beat-up into something beautiful` | `Not mentioned in the conversation` |
| F1 precision | 1.0 | 0.0 |
| F1 recall | 1.0 | 0.0 |
| **F1** | 1.0 | 0.0 |
| **BLEU-1** | 1.0 | 0 |

**F1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Normalised prediction tokens | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` |
| Normalised reference tokens | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Unique prediction tokens | `["and", "beat-up", "beautiful", "into", "old", "something", "transforming"]` | `["and", "beat-up", "beautiful", "into", "old", "something", "transforming"]` |
| Unique reference tokens | `["and", "beat-up", "beautiful", "into", "old", "something", "transforming"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Set intersection | `["and", "beat-up", "beautiful", "into", "old", "something", "transforming"]` | `[]` |
| Precision (P) | 7/7 | 0/7 |
| Recall (R) | 7/7 | 0/5 |
| 2PR / (P + R) | 2 × (7/7) × (7/7) / ((7/7) + (7/7)) = 1.0 | 0 (no overlap) |

**BLEU-1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Prediction sequence | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` |
| Reference sequence | `["transforming", "something", "old", "and", "beat-up", "into", "something", "beautiful"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Clipped matches by token | `{"transforming": 1, "something": 2, "old": 1, "and": 1, "beat-up": 1, "into": 1, "beautiful": 1}` | `{}` |
| Lengths (prediction, reference) | 8, 8 | 8, 5 |
| Unigram precision | 8/8 = 1.0 | 0/8 = 0.0 |
| Brevity penalty (BP) | exp(min(0, 1 − 8/8)) = 1.0 | exp(min(0, 1 − 5/8)) = 1.0 |
| Method 1 | Positive unigram precision retained | Early zero before smoothing |
| BLEU-1 | BP × exp(log(8/8)) = 1.0 | 0 (no matching unigram) |

**Binary adversarial correctness · 0**

Dave describes transforming an old car, while the question asks about destroying one. Reproducing the distractor earns full historical credit and zero complementary credit. The two occurrences of `something` contribute one member to each F1 set and two clipped matches to historical BLEU-1.

Exact saved-score, frozen-scorer, arithmetic and live readback checks passed. [Question trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/fa25afbdd45948dc9a91f6224608719c?observation=c88e06373e9d23d9) · [Historical item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/11fa9ac2166d6047bd48b3a4fdf45049?observation=d7d0c556706a2647) · [Complementary item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/bf09fc2e2dd577efde1d77cb00b1f62b?observation=78d23b47ebc60216)

## C. Both options in one prediction

**What did Sam mention he had been searching for fruitlessly for half an hour?**

`conv-49:qa:166` · Neither · `conv-49`, original QA index 166 (zero-based). Run `gpt4omini-neither-conv49-r0-p0`.

Evidence `D6:13` · Evan, excerpt · “I've been searching for my keys for the last half hour with no luck!”

| Field | Historical evaluation | Complementary evaluation |
| --- | --- | --- |
| Scoring policy | `author-legacy-c5-v1` | `author-corrected-v1` |
| Model prediction | `Not mentioned in the conversation or his keys` | `Not mentioned in the conversation or his keys` |
| Reference | `his keys` | `Not mentioned in the conversation` |
| F1 precision | 0.25 | 0.625 |
| F1 recall | 1.0 | 1.0 |
| **F1** | 0.4 | 0.7692307692307693 |
| **BLEU-1** | 0.25 | 0.625 |

**F1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Normalised prediction tokens | `["not", "mentioned", "in", "the", "conversation", "or", "his", "keys"]` | `["not", "mentioned", "in", "the", "conversation", "or", "his", "keys"]` |
| Normalised reference tokens | `["his", "keys"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Unique prediction tokens | `["conversation", "his", "in", "keys", "mentioned", "not", "or", "the"]` | `["conversation", "his", "in", "keys", "mentioned", "not", "or", "the"]` |
| Unique reference tokens | `["his", "keys"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Set intersection | `["his", "keys"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Precision (P) | 2/8 | 5/8 |
| Recall (R) | 2/2 | 5/5 |
| 2PR / (P + R) | 2 × (2/8) × (2/2) / ((2/8) + (2/2)) = 0.4 | 2 × (5/8) × (5/5) / ((5/8) + (5/5)) = 0.7692307692307693 |

**BLEU-1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Prediction sequence | `["not", "mentioned", "in", "the", "conversation", "or", "his", "keys"]` | `["not", "mentioned", "in", "the", "conversation", "or", "his", "keys"]` |
| Reference sequence | `["his", "keys"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Clipped matches by token | `{"his": 1, "keys": 1}` | `{"not": 1, "mentioned": 1, "in": 1, "the": 1, "conversation": 1}` |
| Lengths (prediction, reference) | 8, 2 | 8, 5 |
| Unigram precision | 2/8 = 0.25 | 5/8 = 0.625 |
| Brevity penalty (BP) | exp(min(0, 1 − 2/8)) = 1.0 | exp(min(0, 1 − 5/8)) = 1.0 |
| Method 1 | Positive unigram precision retained | Positive unigram precision retained |
| BLEU-1 | BP × exp(log(2/8)) = 0.25 | BP × exp(log(5/8)) = 0.625 |

**Binary adversarial correctness · 0**

The cited speaker who lost the keys is Evan. Naming both options earns partial lexical credit under each policy, including 0.7692307692307693 complementary F1 for containing all five abstention tokens. The binary rule detects the distractor `his keys` in the same prediction and returns zero.

Exact saved-score, frozen-scorer, arithmetic and live readback checks passed. [Question trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/5f408264227541b7b04aad4d93318819?observation=f75752c4b6ce9870) · [Historical item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/0eb89b86e9e108156801ffddd363b3cb?observation=ac6f471c226406f1) · [Complementary item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/70d98b618bce27f1e221b8effb1af7cc?observation=06ec3a8603dfb552)

## D. Abstention with a final period (substitute)

**How did Sam get into watercolor painting?**

`conv-49:qa:157` · Neither · `conv-49`, original QA index 157 (zero-based). Run `gpt4omini-neither-conv49-r0-p0`.

Evidence `D1:16` · Evan, excerpt · “My friend got me into it and gave me some advice”

| Field | Historical evaluation | Complementary evaluation |
| --- | --- | --- |
| Scoring policy | `author-legacy-c5-v1` | `author-corrected-v1` |
| Model prediction | `Not mentioned in the conversation.` | `Not mentioned in the conversation.` |
| Reference | `friend's advice` | `Not mentioned in the conversation` |
| F1 precision | 0.0 | 1.0 |
| F1 recall | 0.0 | 1.0 |
| **F1** | 0.0 | 1.0 |
| **BLEU-1** | 0 | 0.8333333333333334 |

**F1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Normalised prediction tokens | `["not", "mentioned", "in", "the", "conversation"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Normalised reference tokens | `["friend's", "advice"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Unique prediction tokens | `["conversation", "in", "mentioned", "not", "the"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Unique reference tokens | `["advice", "friend's"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Set intersection | `[]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Precision (P) | 0/5 | 5/5 |
| Recall (R) | 0/2 | 5/5 |
| 2PR / (P + R) | 0 (no overlap) | 2 × (5/5) × (5/5) / ((5/5) + (5/5)) = 1.0 |

**BLEU-1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Prediction sequence | `["not", "mentioned", "in", "the", "conversation", "."]` | `["not", "mentioned", "in", "the", "conversation", "."]` |
| Reference sequence | `["friend", "'s", "advice"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Clipped matches by token | `{}` | `{"not": 1, "mentioned": 1, "in": 1, "the": 1, "conversation": 1}` |
| Lengths (prediction, reference) | 6, 3 | 6, 5 |
| Unigram precision | 0/6 = 0.0 | 5/6 = 0.8333333333333334 |
| Brevity penalty (BP) | exp(min(0, 1 − 3/6)) = 1.0 | exp(min(0, 1 − 5/6)) = 1.0 |
| Method 1 | Early zero before smoothing | Positive unigram precision retained |
| BLEU-1 | 0 (no matching unigram) | BP × exp(log(5/6)) = 0.8333333333333334 |

**Binary adversarial correctness · 1**

Evan describes his own introduction to the activity. The period leaves the five complementary F1 tokens intact and adds a sixth prediction token to BLEU-1, lowering precision to 5/6. This is the only noncanonical clean abstention in the accepted records, and its words are identical to the canonical ones.

Exact saved-score, frozen-scorer, arithmetic and live readback checks passed. [Question trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/862f6109716c469f81d2a9ee738ff5d8?observation=681ea92ecb8ebdca) · [Historical item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/e6e5832ac7dfab49e6df5db17de4aa5b?observation=57960470a0daab68) · [Complementary item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/870e6f4eba718086675e9990b7e0300b?observation=5228dda70c6e7c49)

## E. The missing quotation marks

**What is the motto of Sam's family?**

`conv-49:qa:185` · Linking Only · `conv-49`, original QA index 185 (zero-based). Run `gpt4omini-linking_only-conv49-r0-p0`.

Evidence `D19:7` · Evan, excerpt · “We have this sign in the frame that says 'Bring it on Home' - it's our family's motto”

| Field | Historical evaluation | Complementary evaluation |
| --- | --- | --- |
| Scoring policy | `author-legacy-c5-v1` | `author-corrected-v1` |
| Model prediction | `Bring it on Home` | `Bring it on Home` |
| Reference | `'Bring it on Home'` | `Not mentioned in the conversation` |
| F1 precision | 0.5 | 0.0 |
| F1 recall | 0.5 | 0.0 |
| **F1** | 0.5 | 0.0 |
| **BLEU-1** | 0.6065306597126334 | 0 |

**F1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Normalised prediction tokens | `["bring", "it", "on", "home"]` | `["bring", "it", "on", "home"]` |
| Normalised reference tokens | `["'bring", "it", "on", "home'"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Unique prediction tokens | `["bring", "home", "it", "on"]` | `["bring", "home", "it", "on"]` |
| Unique reference tokens | `["'bring", "home'", "it", "on"]` | `["conversation", "in", "mentioned", "not", "the"]` |
| Set intersection | `["it", "on"]` | `[]` |
| Precision (P) | 2/4 | 0/4 |
| Recall (R) | 2/4 | 0/5 |
| 2PR / (P + R) | 2 × (2/4) × (2/4) / ((2/4) + (2/4)) = 0.5 | 0 (no overlap) |

**BLEU-1 derivation**

| Step | Historical | Complementary |
| --- | --- | --- |
| Prediction sequence | `["bring", "it", "on", "home"]` | `["bring", "it", "on", "home"]` |
| Reference sequence | `["'", "bring", "it", "on", "home", "'"]` | `["not", "mentioned", "in", "the", "conversation"]` |
| Clipped matches by token | `{"bring": 1, "it": 1, "on": 1, "home": 1}` | `{}` |
| Lengths (prediction, reference) | 4, 6 | 4, 5 |
| Unigram precision | 4/4 = 1.0 | 0/4 = 0.0 |
| Brevity penalty (BP) | exp(min(0, 1 − 6/4)) = 0.6065306597126334 | exp(min(0, 1 − 5/4)) = 0.7788007830714049 |
| Method 1 | Positive unigram precision retained | Early zero before smoothing |
| BLEU-1 | BP × exp(log(4/4)) = 0.6065306597126334 | 0 (no matching unigram) |

**Binary adversarial correctness · 0**

Evan attributes the motto to his family. The historical F1 tokenizer keeps the apostrophes attached to the reference’s outer words, leaving only `it` and `on` in the intersection. NLTK separates the quotation marks, so all four predicted tokens match, but the 4-to-6 length ratio reduces historical BLEU-1 to exp(−0.5).

Exact saved-score, frozen-scorer, arithmetic and live readback checks passed. [Question trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/683a1326239f430da280d9955415a172?observation=ea76963787797f79) · [Historical item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/0150c621a51fcedb136fcbac366b2101?observation=922a00ed97652f19) · [Complementary item observation](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/ea7cf26fd8224f3c6c74475a4dd3945b?observation=fd59df8badd53f09)
