"""Write reusable booktabs fragments and a deterministic Word table collection.

All numerical cells come from the caller's validated pandas DataFrames.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import re


def display(value, column):
    """Use the same presentation rounding for Word and LaTeX cells."""
    if "cost" in str(column).lower() or "usd" in str(column).lower():
        return f"{Decimal(str(value)):.6f}"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        label = str(column).lower()
        if "token" in label or label in ("n", "questions"):
            return f"{value:,.0f}"
        if "cost" in label or "usd" in label:
            return f"{value:.6f}"
        return f"{value:.2f}"
    return str(value)


def latex_text(value):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
                    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
                    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
                    "−": r"$-$", "–": "--", "—": "---", "×": r"$\times$",
                    "Δ": r"$\Delta$", "±": r"$\pm$"}
    return "".join(replacements.get(c, c) for c in str(value))


def table_views(name, frame):
    """Keep category comparisons narrow enough for portrait academic pages."""
    if not name.startswith("04_"):
        return [("", frame)]
    category = next(c for c in frame if "category" in str(c).lower())
    count = next(c for c in frame if str(c).lower() in ("n", "questions", "sample size"))
    config = next(c for c in frame if str(c).lower() in ("configuration", "condition"))
    views = []
    for metric in ("F1", "BLEU-1"):
        col = next(c for c in frame if metric.lower() in str(c).lower())
        wide = frame.pivot(index=[category, count], columns=config, values=col)
        configs = list(dict.fromkeys(frame[config]))
        cats = list(dict.fromkeys(frame[category]))
        wide = wide.reindex(columns=configs).reset_index()
        order = {cat: i for i, cat in enumerate(cats)}
        wide = wide.sort_values(category, key=lambda s: s.map(order))
        wide.columns.name = None
        views.append((f"Alternative-reference {metric} (%)", wide))
    return views


def write_latex(path, title, views):
    lines = ["% Generated from independently validated accepted results.",
             "% Include with \\input{...}; the parent document needs \\usepackage{booktabs,array}.",
             "% " + title, r"\begingroup", r"\small", r"\setlength{\tabcolsep}{4pt}"]
    for subtitle, frame in views:
        if subtitle:
            lines += [r"\noindent\textbf{" + latex_text(subtitle) + r"}\par\smallskip"]
        columns = len(frame.columns)
        fraction = 1 / columns
        gap = 8 * (columns - 1) / columns
        # Paragraph columns wrap long scientific labels without scaling the font.
        spec = "@{}" + "".join(
            r">{\raggedright\arraybackslash}p{\dimexpr" + f"{fraction:.8f}" +
            r"\linewidth-" + f"{gap:.8f}" + r"pt\relax}" for _ in frame.columns
        ) + "@{}"
        lines += [r"\noindent\begin{tabular}{" + spec + "}", r"\toprule",
                  " & ".join(latex_text(c) for c in frame.columns) + r" \\", r"\midrule"]
        for row in frame.itertuples(index=False, name=None):
            lines.append(" & ".join(latex_text(display(v, c)) for v, c in zip(row, frame.columns)) + r" \\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\par\medskip"]
    lines += [r"\endgroup", ""]
    path.write_text("\n".join(lines))


def _normalise_docx(path):
    """Remove ZIP clock variance so byte-for-byte regeneration is testable."""
    buf = BytesIO()
    with ZipFile(path) as original, ZipFile(buf, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted(original.namelist()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, original.read(name))
    path.write_bytes(buf.getvalue())


def _word_table(doc, frame):
    from docx.oxml import OxmlElement
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    table = doc.add_table(rows=1, cols=len(frame.columns))
    table.style = "AMEM Academic"
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        rule = OxmlElement("w:" + edge)
        for key, value in {"val": "single", "sz": "6", "color": "000000"}.items():
            rule.set(qn("w:" + key), value)
        borders.append(rule)
    table._tbl.tblPr.append(borders)
    table.autofit = False
    usable = 481.9  # A4 width less the document's two 20 mm margins, in points.
    # Give the configuration and state description readable space in Table 1.
    weights = [1.25 if i == 0 else 1 for i in range(len(frame.columns))]
    if any("state" in str(c).lower() or "description" in str(c).lower() for c in frame.columns):
        weights[-1] = 2.2
    widths = [usable * w / sum(weights) for w in weights]
    for c, width in zip(table.columns, widths):
        c.width = Pt(width)
    header = table.rows[0]
    repeat = OxmlElement("w:tblHeader")
    header._tr.get_or_add_trPr().append(repeat)
    for cell, title in zip(header.cells, frame.columns):
        cell.text = str(title)
    for row in frame.itertuples(index=False, name=None):
        cells = table.add_row().cells
        for cell, value, column in zip(cells, row, frame.columns):
            cell.text = display(value, column)
    for index, row in enumerate(table.rows):
        cant_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(cant_split)
        for cell, width in zip(row.cells, widths):
            cell.width = Pt(width)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:val"), "clear")
            shading.set(qn("w:color"), "auto")
            shading.set(qn("w:fill"), "E6E6E6" if index == 0 else "F2F2F2" if index % 2 else "FFFFFF")
            cell._tc.get_or_add_tcPr().append(shading)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(3)
                paragraph.paragraph_format.space_before = Pt(3)
                paragraph.paragraph_format.keep_with_next = False
                for run in paragraph.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                    run.bold = index == 0
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def export_tables(frames, captions, out):
    """Export six logical tables under out/latex and out/publication_tables.docx."""
    from docx import Document
    from docx.shared import Mm, Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    out = Path(out)
    latex = out / "latex"
    latex.mkdir(parents=True, exist_ok=True)
    doc = Document()
    from docx.enum.style import WD_STYLE_TYPE
    academic = doc.styles.add_style("AMEM Academic", WD_STYLE_TYPE.TABLE)
    academic.font.name = "Arial"
    academic.font.color.rgb = RGBColor(0, 0, 0)
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(18)
    section.left_margin = section.right_margin = Mm(20)
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.size = Pt(10 if name == "Normal" else 16 if name == "Title" else 13)
        style.paragraph_format.space_after = Pt(7)
    for border in doc.styles.element.xpath(".//w:pBdr"):
        border.getparent().remove(border)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.05
    stamp = datetime(2026, 11, 8, tzinfo=timezone.utc)
    props = doc.core_properties
    props.title = "A-MEM scientific tables"
    props.author = "FTEC5660 A-MEM reproducibility study"
    props.created = props.modified = stamp
    props.revision = 1
    props.last_modified_by = props.author
    footer = section.footer.paragraphs[0]
    footer.alignment = 2
    footer.add_run("FTEC5660 A-MEM  |  ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    for i, (name, frame) in enumerate(frames.items(), 1):
        if i > 1:
            doc.add_page_break()
        else:
            doc.add_paragraph("A-MEM scientific tables", style="Title")
            doc.add_paragraph("Twelve accepted GPT-4o-mini cells across 558 matched LoCoMo questions per configuration.")
        meta = captions[name]
        title = re.sub(r"^Table\s+\d+\s*[.:-]?\s*", "", meta["title"])
        doc.add_paragraph(f"Table {i}  {title}", style="Heading 1")
        doc.add_paragraph(meta["caption"])
        views = table_views(name, frame)
        for subtitle, view in views:
            if subtitle:
                doc.add_paragraph(subtitle, style="Heading 2")
            _word_table(doc, view)
        for key, label in (("interpretation", "Observation"), ("limitation", "Limitation")):
            if meta.get(key):
                p = doc.add_paragraph()
                p.add_run(label + ". ").bold = True
                p.add_run(meta[key])
        write_latex(latex / f"{name}.tex", title, views)
    path = out / "publication_tables.docx"
    doc.save(path)
    _normalise_docx(path)
    return path
