# Final submission fidelity audit

## Current Section 3.4

Table 3 now compares two verified predictions from the accepted GPT-4o-mini
builds. The current verifier checks its nine cells separately from the 169 cells
of the eight retained tables. The 184-cell comparisons below describe earlier
manuscript revisions. The [current fidelity receipt](fidelity_results.json)
records the checks on the ten-page report.

## Original conversion and scope

The approved DOCX remains `/Users/alistair/Downloads/AMEM_FTEC5660_Sections_3_7_Updated.docx`,
SHA-256 `c433d42629e62eb70b050785c40ac691df4ec7a4e20d5315857ad870a2d642a5`.
This polish directly edits the existing LaTeX from `86af3cc`; it does not regenerate
the manuscript. The extraction JSON retains the original editorial evidence.

The final output has **10 A4 pages**, including a rendered BibTeX bibliography.
Body text remains 11 pt TeX Gyre Termes with 22 mm margins. No scientific paragraph was removed or shortened to fit the page limit. The user
subsequently approved the cost-scope paragraph correction documented below.
No accepted experimental result changed.

## Content preserved

All seven sections, 19 subsections, nine tables, four figures and the original
16-line code abridgement remain. Independent DOCX comparison verifies 26 headings,
43 prose/title paragraphs, 14 captions and all **184 table cells** (183 unchanged cells and the approved `Pooled (derived)`
label replacement; all numerical values, signs and precision unchanged). The listing caption is an explicitly authorised replacement.
The comparison allows only citation markers, the one authorised terminology
sentence, the exact approved cost paragraph and the one approved table label; it does not normalise away scientific wording changes. Original prose
and heading order is preserved. `fidelity_results.json` records the checks.

The reproduction target, fourth factorial condition, F1/BLEU-1 definitions, five
categories, both evaluation perspectives, complete twelve-cell/558-question
results, interactions, evaluation-dependent frontiers, exploratory DeepSeek
caveats and stochastic/sample-size limitations remain intact.

| Table | Authority used in original conversion, retained unchanged |
|---|---|
| 1–4, 9 | Approved DOCX; no identical-schema generated fragment |
| 5 | `tables/latex/02_overall_results.tex`, manuscript headings |
| 6 | `tables/latex/03_factorial_contrasts.tex`, manuscript labels/signs |
| 7 | `tables/latex/05_cost_retrieval.tex`, manuscript five-column subset and five-decimal dollar display |
| 8 | `exploratory_deepseek/deepseek_results.tex`, manuscript labels |

Paths are relative to `reports/publication_assets/`. All figure PDFs and their
manifest hashes are unchanged during polish: Figure 1 uses the PR #57 architecture;
Figures 2–4 use `01_scoring_comparison.svg`, `02_category_heatmap.svg` and
`06_dual_scoring_f1_vs_cost.svg`. Source-native heatmap rasters remain; other assets
preserve vector paths/text. No scientific graphic was regenerated or redesigned.

## Authorised editorial and formatting changes

- Figure 1 moves before the listing on page 4, immediately after its Section 4.2
  introduction on page 3. At 150 mm width, diagram body lettering is approximately
  8.16 pt. It shares page 4 with Listing 1 and replay-methodology text. There are
  no figure-only pages. Figure 4 now uses the full text width for improved labels.
- Listing 1 is explicitly **abridged**, not a continuous verbatim source excerpt.
  The caption pins `amem_repro/actions.py` at accepted commit `8485673` through a
  full-commit hyperlink. Its equality-operator guard, `found` tracking and final
  validation/compilation are absent from the displayed abridgement; the caption
  discloses the omitted guard and validation/compilation steps. Displayed code is
  unchanged from the approved manuscript; no invented code was introduced.
- Section 3.4 adds only: “Throughout the figures, this complementary evaluation is
  labelled alternative-reference scoring.” Existing scientific explanations remain.
- Five numbered BibTeX references are cited from Sections 1–2 and rendered after
  Section 7.4. The original source paragraphs and frozen/evidence revisions remain.
  References use readable 9 pt text; body font size was not reduced.
- The title block adds `[enter name]` and `[enter ID]` placeholders. Module code,
  title and report title remain. No personal identifier was inferred.
- The initial converter is now archival and requires a separate output directory;
  it cannot overwrite the polished source. Build the report from `main.tex`.

## Citation verification

On 8 November 2026, bibliographic authors, title, year, version and DOI for A-MEM
were verified against [arXiv v11](https://arxiv.org/abs/2502.12110v11). LoCoMo's six
authors, ACL 2024 proceedings title, pages 13851–13870 and DOI were verified against
[ACL Anthology](https://aclanthology.org/2024.acl-long.747/). Repository references
link to the released source at frozen `f9a173d`, the reproduction repository and
accepted scientific evidence `8485673183d7b8018c841082d075b21158002700`. No venue,
publication date or personal author identity was invented for repository entries.
No substantive citation ambiguity was identified.

## Approved corrections following cost investigation

The user approved the proposed replacement of Section 6.2's cost paragraph and
requested `Pooled*` → `Pooled (derived)` in Table 8. Both are applied verbatim.
The original DOCX/extraction and all accepted scientific assets remain immutable.

The twelve accepted cells sum to **USD 4.06400310**, displayed as approximately
**$4.06**. Campaign-wide identified charges are **USD 4.69823805**, approximately
**$4.70**, including **USD 0.62848605** from earlier stopped attempts/continuation
and **USD 0.00574890** from compatibility checks. Broader conservative campaign
exposure is **USD 10.457057**, comprising USD 4.808497 conservative model exposure
and USD 5.648560 service upper bound. It is not a final invoice total.

These values were verified with Decimal arithmetic against accepted scientific
commit `8485673183d7b8018c841082d075b21158002700` and the hash-bound receipts:
`artifacts/gpt4omini/verification/final-eight-hour-finance/model-cost-inventory.json`
and `final-programme-reconciliation.json`. Table 7, Figure 4 and every experimental
score/cost cell remain unchanged. The verifier whitelists only the exact approved
paragraph and exact Table 8 label replacement; it retains all other comparisons.

## Submission fields

The supplied student name and ID now appear in the title block. The cost-scope and
`Pooled*` editorial issues are resolved by the explicit approval above.

## Validation

The build, independent comparison and all ten rendered-page inspections pass.
A4 size, page limit, eight internal links (including bibliography destinations),
source hyperlinks, citation keys and student placeholders are checked. No overfull
or underfull boxes, missing glyphs or unresolved references occur. No accepted
asset, scientific pipeline, result, financial record or experimental setting changed.
Independent final Standards and Spec reviews are recorded below.

### Independent Standards review before approved corrections

**PASS — zero unresolved findings.** A clean temporary build with all auxiliary
and bibliography files removed reproduced PDF SHA-256
`b64314e27ed32c2f10deff23c8b615811fe87e537dcec577ceb3673921777d6c`
byte-for-byte. Updated fidelity checks and documented workflows passed; no hard
standards violations or actionable heuristic findings were identified.

### Independent Spec review before approved corrections

**PASS — zero blocking findings.** Independently verified ten A4 pages, all five
rendered references, all 98 unchanged source text items in the PDF (after the
approved additions/caption changes), all 184 table cells and unchanged listing.
All ten rendered pages were inspected. Figure 1 and Listing 1 share page 4;
Figure 4 uses full text width; citation metadata and links pass. Reviewed PDF hash
matches the Standards review above. The submission fields are documented above.

### Approved-correction validation

Final PDF: **10 A4 pages**, SHA-256
`662720d75e1953d850e5c6973eedb21f78ff90119c2ec98da4e82ffcbc93bf4f`.
The DOCX comparison passes with the two explicit replacements. No compilation
warnings or layout diagnostics occur. Focused independent Standards and Spec re-reviews both **PASS with zero findings**.
Standards reproduced this hash from a clean temporary build. Spec independently
verified the exact approved paragraph, receipt-bound totals and unchanged numerical
cells; page 8 is clean and the other nine rendered pages are pixel-identical to
the previously inspected version. The submission fields were completed in the subsequent two-policy editorial revision.
