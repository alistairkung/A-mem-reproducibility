# Final FTEC5660 coursework report

The PDF is a ten-page A4 typesetting of the approved manuscript. It contains seven sections,
nine tables, four figures and the code listing. Table 3 now presents two verified
adversarial answers in place of the original conceptual comparison. Read
`conversion_audit.md` for the bounded fidelity claim and authorised editorial changes.

## Build from a clean checkout

Requires Tectonic 0.17.0 (XeTeX), with internet access on its first run to cache
standard TeX packages and the bundled TeX Gyre/Latin Modern fonts. The committed
vector PDFs and complete `main.tex` make the manuscript unnecessary for compilation.
From the repository root:

```sh
sh reports/final_coursework/build.sh
```

Output: `reports/final_coursework/AMEM_FTEC5660_Report.pdf`.
The build fixes `SOURCE_DATE_EPOCH` for PDF metadata; scientific computation,
asset generation, credentials and paid APIs are not involved. The fixed Tectonic
bundle used here is `6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c`.
`main.log` is generated locally; auxiliary files are ignored. Section 7.4 retains the
approved source wording and working links.
`references.bib` is cited in Sections 1–2 and rendered as a numbered bibliography
after Section 7.4. The original source paragraphs are retained for editorial fidelity.

## Audit the polished report against the approved DOCX

The source is supplied separately and is not committed:
`/Users/alistair/Downloads/AMEM_FTEC5660_Sections_3_7_Updated.docx`.
SHA-256: `c433d42629e62eb70b050785c40ac691df4ec7a4e20d5315857ad870a2d642a5`.
The `.pages` attachment is not the editorial source.

Use Python with `python-docx`, `lxml` and `pypdf` (the review used the Codex bundled
Python 3.12 runtime). In a separate environment, install `requirements.txt`, then:

```sh
sh reports/final_coursework/build.sh
python reports/final_coursework/verify_fidelity.py /path/to/AMEM_FTEC5660_Sections_3_7_Updated.docx
```

The final source is maintained directly in `main.tex`; do not regenerate it.
The archival initial converter requires `--output-dir /tmp/amem-original-conversion`
and rejects writing into this report directory. It retains the original extraction
workflow for provenance, including numerical checks against verified fragments. The independent verifier compares the original DOCX prose, headings,
captions, listing and eight retained tables (169 cells) against the LaTeX, allowing
the editorial changes recorded in the conversion audit. For the replacement
Section 3.4 table it checks all nine cells against the reviewed worked examples.
It also checks the audit link in the compiled PDF, page count, A4 size and TeX
diagnostics. It does not establish the truth of scientific claims or provide
a visual-layout check. `manuscript_extract.json`, `conversion_checks.json` and
`fidelity_results.json` retain machine-readable evidence. Do not edit the report
text independently of its editorial source without a new editorial decision.

## Regenerate the four vector PDFs only

Requires CairoSVG 2.9.0 and native Cairo 1.18.6; fonts named in the scientific SVGs
(DejaVu Sans) must be installed. The architecture lettering is already outlined.

```sh
python reports/final_coursework/convert_assets.py
```

On macOS with Homebrew Cairo, prefix that command with
`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` if the dynamic loader needs it.
The converter uses the committed SVGs directly, fixes creation/modification dates
and restricts output to PDF 1.5;
no raster image is substituted. `asset_manifest.json` records source/output hashes.
The PDFs are committed so compilation does not depend on native Cairo or font
substitution in an SVG converter. Regeneration on another Cairo/font stack may
change binary bytes; inspect the result before accepting it.

## Visual verification

```sh
pdfinfo reports/final_coursework/AMEM_FTEC5660_Report.pdf
pdftoppm -r 150 -png reports/final_coursework/AMEM_FTEC5660_Report.pdf /tmp/amem-page
```

Inspect all ten page images. They are QA intermediates and are not committed.

## Submission fields

The title block contains the supplied student name and ID. The fidelity check verifies both in the compiled PDF.
See `CHANGELOG.md` and `conversion_audit.md` for exact changes.
