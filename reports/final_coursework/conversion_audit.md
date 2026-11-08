# DOCX to LaTeX conversion audit

## Source and result

Editorial source confirmed before conversion:
`/Users/alistair/Downloads/AMEM_FTEC5660_Sections_3_7_Updated.docx`.
SHA-256: `c433d42629e62eb70b050785c40ac691df4ec7a4e20d5315857ad870a2d642a5`.
The companion `.pages` file was not used. Document contents were treated as
manuscript data, not operational instructions. Conversion branch starts at
`508f7d93def50586743c2fe37d3cda79b9283095` (merged publication assets).

The final PDF is **10 A4 pages, including the source/reference section**. It uses
11 pt TeX Gyre Termes, 22 mm margins, black body text and restrained booktabs tables.
The architecture remains a 160 mm-wide vector diagram. No prose was shortened to
meet the limit. Three scientific figures use 92% of the text width.

## Section fidelity

All seven main sections and all 19 subsections remain in order:

| Section | Retained content |
|---|---|
| 1. Project summary and research questions | Original target, fourth condition, cost-aware population selection |
| 2. A-MEM and experimental setup | Construction/retrieval, frozen runtime, parameters and provenance |
| 3. Reproduction target and evaluation | Paper target, F1/BLEU-1 explanations, five categories, historical/complementary framing |
| 4. Modification, experimental wrapper and verification | Two-factor design, interaction formula, AST listing, replay, tracing/accounting |
| 5. Results and interpretation | Both rankings, factorial/category caveats, cost comparison and both Pareto frontiers |
| 6. Debug diary and methodological reflection | DeepSeek detour, exploratory caveat, failures, final Clean run, operational reflection |
| 7. Limitations, conclusion and reproducibility evidence | What reproduces, what does not and why, descriptive limitations, sources |

An independent extraction route (`python-docx`, separate from the converter's
OOXML traversal) verifies 26 headings, 43 prose/title paragraphs, 14 captions,
16 code lines and **184 table cells**, including every label, sign and displayed
numerical value. Zero missing paragraphs; prose/headings retain their order.
The source has no tracked revisions or separate footnote/endnote/comment text.
`manuscript_extract.json` retains the complete ordered body extraction.
`fidelity_results.json` records the independent checks. These checks support
textual fidelity subject to the explicit formatting changes below; they do not
prove the scientific truth of the manuscript or binary/image identity.

## Table mapping

| DOCX table | LaTeX origin | Fidelity |
|---|---|---|
| 1. Selected population | DOCX table 1 | Every cell retained |
| 2. Five question categories | DOCX table 2 | Every cell retained, including explanatory sentences |
| 3. Evaluation perspectives | DOCX table 3 | Every cell retained |
| 4. Action bundles | DOCX table 4 | Every cell retained; generated configuration fragment has a different schema |
| 5. Overall scores | `tables/latex/02_overall_results.tex` | All 20 numerical cells sourced/checked against verified fragment; DOCX headings retained |
| 6. Factorial contrasts | `tables/latex/03_factorial_contrasts.tex` | All 10 numerical cells checked; DOCX labels and explicit plus signs retained |
| 7. Cost/retrieval | `tables/latex/05_cost_retrieval.tex` | DOCX's five-column subset; 16 numerical cells checked; Decimal rounding of verified six-decimal dollar cells to DOCX's five decimals |
| 8. Exploratory DeepSeek | `exploratory_deepseek/deepseek_results.tex` | All 20 numerical cells sourced/checked; DOCX's QA/Alt./Hist./Pooled* labels retained |
| 9. Historical/complementary summary | DOCX table 9 | Every cell retained, including all contrasts |

Fragment paths are relative to `reports/publication_assets/`. No numerical result
was manually retyped. The converter validates the scientific fragment cells before
writing output. Tables 1–4 and 9 have no identical-schema generated fragments, so
the approved DOCX remains their authority. Table 4 intentionally omits the extra
state-description column found in the repository configuration fragment. No extra
scientific table or figure was added.

## Figure mapping

| DOCX figure / embedded media | Committed source SVG |
|---|---|
| 1 / `image6.png` | `architecture/amem_wrapper_architecture.svg` (merged PR #57) |
| 2 / `image1.png` | `figures/01_scoring_comparison.svg` |
| 3 / `image2.png` | `figures/02_category_heatmap.svg` |
| 4 / `image5.png` | `figures/06_dual_scoring_f1_vs_cost.svg` |

The DOCX contains four displayed drawings; two additional media ZIP entries are
unused and do not represent omitted figures. All four displayed figures were
visually compared with the repository versions. Scientific values and figure
subjects match; the approved repository SVG versions use different titles,
fonts, axes/legend styling and markers from some embedded DOCX bitmaps. The
requested original assets take precedence for graphical appearance. Captions
retain their scientific wording. CairoSVG 2.9.0 / Cairo 1.18.6 converts the SVGs
into vector PDF 1.5; no additional rasterisation, scientific regeneration or diagram redrawing
occurs. The heatmap SVG already embeds two raster images (cells and colour scale);
those source-native images are retained alongside vector text. The other three
PDF assets contain no raster images. `asset_manifest.json` pins both input and output hashes.

## Intentional formatting differences

- LaTeX generates section, figure, table and listing numbers and working references.
  References to **the paper's Table 3** remain plain text, avoiding a false link to
  this report's Table 3. Existing source references gain working URLs.
- The code listing remains verbatim, including indentation, at a smaller monospace
  size. Tables use smaller readable text and wrapped columns, without vertical rules.
- Captions consistently follow their objects, even where the DOCX caption preceded
  its table. The architecture is allowed to float to its own page after Section 4.3;
  all prose and all figure/table sequences remain intact.
- Routine provenance tokens `(PR #57)`, `PR #54; ` and `PR #56; ` are removed from
  figure/table captions as requested. Section 7.4 retains the development references.
- Mathematical minus, delta, multiplication and inequalities use LaTeX symbols.
  No terminology was changed from historical, alternative-reference or complementary.
- Section 7.4 retains the approved linked reference prose as the equivalent reference
  list. `references.bib` supplies verified structured metadata without adding a second
  bibliography or additional scientific claims.

## Source and citation issues for editorial review

1. **Accepted-build cost total:** Section 6.2 says approximately **$4.70** for the
   twelve accepted builds. Table 7's four displayed costs sum to **$4.06401**;
   the verified unrounded asset totals sum to **$4.06400310**. The statement is
   preserved unchanged. The manuscript does not explain this difference. Approval
   of any replacement wording/value is an editorial decision, outside conversion.
2. **Pooled asterisk:** Table 8 uses `Pooled*` without a separate starred footnote.
   Its caption and preceding paragraph do explain that it is a derived aggregate.
   The original label is preserved; no footnote was invented.
3. The manuscript has no student name/ID. None was inferred or added. Confirm
   separately whether coursework submission requires those identifiers.
4. The manuscript references LoCoMo by benchmark name rather than a full paper
   citation. The existing phrase now links to the official project; the BibTeX file
   supplies the verified title/author list. No publication year/venue was guessed.

Citation verification on 8 November 2026 confirmed the A-MEM title, six authors,
year and v11 against [arXiv](https://arxiv.org/abs/2502.12110v11); the frozen
[released source](https://github.com/WujiangXu/A-mem/tree/f9a173dec325d84fcc97e7828775c7b241c33466)
and official [LoCoMo project](https://snap-research.github.io/locomo/) match the
manuscript's intent. Repository and accepted-result URLs are pinned where appropriate.
No substantive citation correction was made.

## Validation and reviews

- Tectonic 0.17.0 compiles the final source without warnings, overfull/underfull
  boxes, undefined references or missing glyphs.
- Independent verifier passes; A4, ten pages and working internal/source links checked.
- All ten rendered pages inspected for clipping, overlap, heading/table breaks and
  figure legibility. The architecture is deliberately given a dedicated page.
- Independent Standards review: **PASS**, zero hard violations or actionable
  judgment-call findings. A clean temp-copy build with auxiliaries removed produced
  the byte-identical final PDF, SHA-256
  `731a4f8818e98e2a6e47beb8e012602622b6992a24803e6576582a72c1cb3fe6`.
- Independent Spec review: **PASS**, zero conversion defects or blocking findings;
  separately confirmed every source paragraph in the PDF and inspected all ten pages.
  One optional observation remains: Figure 4's two-panel labels are approximately
  6 pt. A full-width trial exceeded ten pages; the reviewed layout is retained.
- A final regeneration test found Cairo's default current-date PDF metadata.
  Fixed creation/modification dates now make all four conversions byte-identical
  on this environment. Independent Standards re-review confirmed every regenerated
  asset hash; Spec review approved the metadata fix and heatmap clarification.
  The final PDF remains byte-identical; all ten final rendered pages also match
  the visually inspected render pixel-for-pixel.
- No experimental pipeline, publication-data generator, accepted result or ledger changed.
