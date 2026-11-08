# A-MEM publication assets

This collection supplies six scientific tables, a compact companion table and six figures for the twelve accepted GPT-4o-mini cells on 558 matched LoCoMo questions. Configuration order is Neither, Linking Only, Evolution Only, Full A-MEM throughout. The additional alternative-reference policy retains the accepted internal name `author-corrected-v1`; public labels use alternative-reference to avoid implying universal superiority over the authors' historical policy.

## Reproduce and validate

Run from the repository root with Python 3.11.17 and access to Git object `8485673183d7b8018c841082d075b21158002700`.

```sh
python -m venv /tmp/amem-publication-env
/tmp/amem-publication-env/bin/pip install -r reports/publication_assets/requirements.txt
/tmp/amem-publication-env/bin/python reports/publication_assets/generate_assets.py
/tmp/amem-publication-env/bin/python -m pytest -q reports/publication_assets/test_assets.py
```

The generator reads the four accepted inputs directly with `git show` at the exact source commit. It never reads a floating working-tree version of the scientific data. Their SHA-256 digests, the generator and helper digests, library/runtime versions and every generated output digest are in [source_manifest.json](source_manifest.json). A checkout whose main branch lacks the accepted source files can still generate the assets when that Git object is available. PR #52 was merged into its parent branch after PR #51 merged into main; this reporting branch does not copy that experimental implementation into main.

The authoritative question JSONL supplies both score perspectives and binary adversarial flags. The generator reproduces all overall, category and conversation means and all factorial contrasts, checking 864 values against the accepted analysis. A maximum difference of 1e-12 percentage points allows floating-point accumulation rounding only. Question scores remain unmodified. Cost CSV fields cross-check the accepted analysis and Decimal sums of the three selected scientific cell costs per configuration. The report supplies an additional rounded-value cross-check. Retrieval counts and token totals retain the accepted scientific accounting basis.

CSV metric values retain eight decimal places. Word, LaTeX and graphical scores use two decimals, costs use six decimals in formatted tables, and integer token/count fields retain exact counts. Percentages and percentage-point contrasts are labelled separately. Only identified model charges from accepted builds appear in cost outputs.

## Output collection

- `tables/01_configurations.csv` through `06_conversation_results.csv` contain the six machine-readable tables.
- `tables/latex/` contains six standalone booktabs fragments. Load `booktabs`, `array` and `graphicx` in a UTF-8 LaTeX document. Table 4 supplies two metric panels, and Table 6 supplies per-conversation supplementary detail.
- [publication_tables.docx](tables/publication_tables.docx) is a six-page A4 Word collection with one numbered table per page, suggested captions, interpretation and caveats.
- `figures/01_scoring_comparison` through `05_token_overhead` each have SVG and 300-DPI PNG versions. Figure 6 adds a shared-scale historical/alternative cost comparison in the same formats. SVG retains text for vector workflows. PNG is suitable for Word and PowerPoint.
- [captions.json](captions.json) contains a suggested academic title, caption, interpretation and limitation for every table and figure.

SVG IDs, figure dates, DOCX core properties and ZIP timestamps are stabilized. Tests regenerate the collection and require byte-identical output hashes on the recorded environment. Different font stacks or compression/runtime versions can affect binary outputs; scientific validation still runs before exports.

## Editorial recommendations

For the ten-page report, prioritise Figures 1, 2 and 3 with Tables 1, 2, 3 and 5. Figure 2 communicates Table 4's category pattern without duplicating its wide numerical views. Table 6 is supplementary. Figure 4 can be supplementary because Table 3 already presents the factorial contrasts. Figure 5 can support the input-overhead discussion if space permits.

For a 15-minute presentation, use Figures 1, 2, 4, 3 and 5 in that order, progressing from reference-dependent rankings to category patterns, interactions, inference cost and input overhead. The observed Pareto result applies to these accepted builds. The positive pooled interaction varies by conversation, and these single-build descriptive results establish no statistical significance.

## Inspection

All six actual PNGs were inspected for label clipping, scale, contrast and legibility. Both bar figures use zero-based axes. The interaction and scatter axes are zoomed and labelled with point values. Figure 2 uses the sequential cividis scale with two-decimal annotations. Its full 0–100 scale avoids rescaling each category. Figure 3 marks the observed frontier with a circle and dominated points with crosses. Figure 5 uses separate axes for tokens and retrieved entries.

The DOCX was rendered with LibreOffice and checked across all six pages. The LaTeX fragments were compiled in a local test wrapper. Rendering intermediates are kept outside this deliverable directory. No final coursework report or presentation is included.

## Suggested titles and captions

### Table 1 Experimental configurations

The two action factors define four configurations. All configurations generate shared evolution decisions; the gates determine which resulting memory changes are applied.

The design isolates strengthening and neighbour evolution and their combination.

One stochastic memory build was accepted per conversation and configuration.

### Table 2 Evaluation across 558 matched questions

Question-weighted F1 and BLEU-1 percentages under the authors' historical policy and the additional alternative-reference policy. Binary adversarial correctness covers 121 questions.

Historical scoring ranks Full A-MEM highest; alternative-reference scoring ranks Neither highest.

The policies differ in adversarial references. Neither policy is presented as universally superior.

### Table 3 Alternative-reference factorial contrasts

Matched question differences, averaged over 558 questions, in percentage points. Interaction = Full − Linking Only − Evolution Only + Neither.

The pooled interaction is positive, while the individual aggregate contrasts vary in direction.

These are descriptive contrasts from single builds, without statistical significance claims.

### Table 4 Alternative-reference category performance

Separate F1 and BLEU-1 percentage panels show all four configurations and the five original category populations.

Linking Only has the highest multi-hop F1, while Neither has the highest pooled alternative-reference F1.

Categories differ in size and difficulty; open-domain contains only 27 questions.

### Table 5 Scientific inference cost and retrieval

Mean retrieved entries per question, total native answer input tokens and identified model costs for the three accepted builds per configuration, covering 558 questions. Fees and historical attempts are excluded.

Linking approximately doubles answer input tokens. Neither has the highest aggregate alternative F1 at the lowest identified model cost in this population.

Observed inference costs apply to this model, population and retrieval configuration.

### Table 6 Alternative-reference results by conversation

F1 and BLEU-1 percentages for all four conditions on conv-44, conv-49 and conv-50. Each question has equal weight within a conversation.

Linking Only exceeds Neither on conv-49 and scores lower on the other two conversations.

Three conversations and one build per cell do not establish run-to-run variability.

### Figure 1 Evaluation reference changes configuration ranking

Historical and alternative-reference F1 for 558 matched questions per configuration, using a zero-based bar axis.

Full A-MEM ranks highest historically and Neither ranks highest with the alternative reference.

Both policies score the same predictions; the alternative reference is an additional evaluation perspective.

### Figure 2 Alternative-reference F1 by category

Each cell gives F1 (%) to two decimals on a shared 0–100 sequential scale. Row labels include category sample sizes.

Linking Only leads multi-hop F1, although its aggregate F1 is below Neither.

Small numerical differences and uneven category sizes warrant caution; no significance is implied.

### Figure 3 Alternative-reference F1 and scientific model cost

Each point represents three accepted scientific builds and 558 matched questions. Circles indicate the observed Pareto frontier and crosses indicate dominated configurations.

Neither strictly Pareto-dominates the other configurations on aggregate alternative F1 and identified model cost within this population.

Costs exclude failed historical attempts and observability fees; this frontier is specific to the observed experiment.

### Figure 4 Interaction between linking and evolution

Alternative-reference F1 (%) with linking OFF and ON, at both evolution settings. The four-term interaction is +2.72 percentage points, indicating that evolution's effect differs according to linking status.

Evolution's F1 contrast is less negative when linking is enabled. Full A-MEM does not have the highest pooled F1.

The pooled interaction varies by conversation and is descriptive. The line axis is zoomed; endpoint values are shown.

### Figure 5 Retrieval expansion and token overhead

Separate zero-based panels show native answer input tokens in millions and mean retrieved entries per question for 558 questions per configuration.

Linking-expanded retrieval approximately doubles the answer input token volume.

Token volume measures input overhead, not answer quality or a universal efficiency effect.

## Section 5.3 two-policy cost comparison

Use `figures/06_dual_scoring_f1_vs_cost.svg` or its 300-DPI PNG to compare historical and alternative-reference F1 at identical identified model costs. Both panels have the same numerical ranges, direct condition labels and stable condition colours and marker shapes. Filled markers are efficient, hollow markers are dominated, and the dotted line connects the historical frontier. `tables/07_dual_scoring_cost_performance.csv` and its standalone LaTeX fragment expose the values and computed statuses. The six-page Word collection is preserved.

The historical frontier contains Neither, Linking Only and Full A-MEM. This differs from the proposed two-point historical frontier. Linking Only has historical F1 of 30.21% versus Neither's 30.03%, and costs USD 1.079391 versus Full's USD 1.080836. Neither therefore cannot dominate Linking Only on historical F1, and Full cannot dominate it on cost. Evolution Only is dominated. Under the alternative reference, Neither is the sole frontier point. The classifications are calculated from unrounded question-level means and accepted scientific model charges; display rounding does not control membership.

These frontiers describe only the 558 matched questions and three accepted scientific builds per configuration. Observability fees, historical failed attempts and financial reservations do not enter the cost axis. No statistical significance or universal efficiency is implied. Figure 3 remains byte-identical for compatibility. The new figure can replace Figure 3 in Section 5.3 when both evaluation perspectives are discussed.
