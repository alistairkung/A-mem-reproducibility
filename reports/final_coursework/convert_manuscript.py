"""Regenerate the report from its SHA-pinned DOCX; never edits publication assets."""
import argparse
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'publication_assets'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
SOURCE_SHA = 'c433d42629e62eb70b050785c40ac691df4ec7a4e20d5315857ad870a2d642a5'  # Approved editorial-source fingerprint.


def esc(s):
    mapping = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '−': r'\ensuremath{-}', 'Δ': r'\ensuremath{\Delta}', '×': r'\ensuremath{\times}', '<': r'\ensuremath{<}', '>': r'\ensuremath{>}'}
    return ''.join(mapping.get(c, c) for c in s)


def prose(s):
    s = esc(s)
    s = re.sub(r'\b(Figure|Table) (\d+)', lambda m: m[0] if m[1]=='Table' and m[2]=='3' else m[1] + r'~\ref{' + ('fig' if m[1]=='Figure' else 'tab') + m[2] + '}', s)
    # Preserve visible wording; add links to the existing source references.
    for token, url in [('github.com/alistairkung/A-mem-reproducibility', 'https://github.com/alistairkung/A-mem-reproducibility'), ('arXiv:2502.12110 (v11)', 'https://arxiv.org/abs/2502.12110v11'), ('WujiangXu/A-mem', 'https://github.com/WujiangXu/A-mem/tree/f9a173dec325d84fcc97e7828775c7b241c33466'), ('8485673183d7b8018c841082d075b21158002700', 'https://github.com/alistairkung/A-mem-reproducibility/commit/8485673183d7b8018c841082d075b21158002700')]:
        s = s.replace(token, r'\href{' + url + '}{' + token + '}')
    if 'LoCoMo benchmark data distributed with the release' in s:
        s=s.replace('LoCoMo benchmark data', r'\href{https://snap-research.github.io/locomo/}{LoCoMo benchmark data}')
    return s


def fragment_rows(path):
    text=path.read_text().split(r'\midrule')[1].split(r'\bottomrule')[0]
    return [[v.strip() for v in line.strip().removesuffix(r'\\').split('&')] for line in text.strip().splitlines()]


def checked_tables(tables):
    # Source numerical cells from the verified fragments, retaining DOCX labels/precision.
    mappings={4: ('tables/latex/02_overall_results.tex', [1,2,3,4,5]), 5: ('tables/latex/03_factorial_contrasts.tex',[1,2]), 6: ('tables/latex/05_cost_retrieval.tex',[1,2,3,4]), 7: ('exploratory_deepseek/deepseek_results.tex',[1,2,3,4,5])}
    checks=[]
    for ti,(source, cols) in mappings.items():
        rows=fragment_rows(ASSETS/source)
        assert len(rows)==len(tables[ti])-1
        for ri,row in enumerate(rows,1):
            for ci,src in enumerate(cols,1):
                value=row[src]
                original=tables[ti][ri][ci]
                if ti==6 and ci==3: value='$'+str(Decimal(value).quantize(Decimal('0.00001')))
                assert Decimal(value.replace('$','').replace(',','')) == Decimal(original.replace('$','').replace(',','').replace('−','-').replace('+','')) if '/' not in value else value==original
                # Keep explicit positive signs and Unicode minus as in the manuscript.
                tables[ti][ri][ci]=original if original.startswith(('+','−')) else value
        checks.append({'table':ti+1,'source':source,'numerical_cells_checked':len(rows)*len(cols)})
    return checks


def main():
    global HERE
    ap=argparse.ArgumentParser();ap.add_argument('manuscript',type=Path);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
    if args.output_dir.resolve()==HERE:
        ap.error('Use a separate directory: this archival converter must not overwrite the polished report')
    HERE=args.output_dir.resolve()
    HERE.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(args.manuscript.read_bytes()).hexdigest()
    if SOURCE_SHA: assert digest==SOURCE_SHA, 'Different editorial source: review required'
    with ZipFile(args.manuscript) as z:
        root=E.fromstring(z.read('word/document.xml'))
        body=root.find('w:body',NS)
        records=[]; tables=[]
        for c in body:
            if c.tag.endswith('}tbl'):
                rows=[[''.join(a.xpath('.//w:t/text()',namespaces=NS)) for a in r.findall('w:tc',NS)] for r in c.findall('w:tr',NS)]
                tables.append(rows);records.append({'type':'table','index':len(tables),'rows':rows})
            elif c.tag.endswith('}p'):
                text=''.join(c.xpath('.//w:t/text()',namespaces=NS))
                style=c.find('w:pPr/w:pStyle',NS)
                records.append({'type':'paragraph','text':text,'style':style.get('{'+NS['w']+'}val') if style is not None else '', 'drawing':bool(c.xpath('.//w:drawing',namespaces=NS))})
        extras={name:len(E.fromstring(z.read(name)).xpath('//w:t',namespaces=NS)) for name in ['word/footnotes.xml','word/endnotes.xml','word/comments.xml'] if name in z.namelist()}
        revisions=len(root.xpath('//w:ins|//w:del',namespaces=NS))
    (HERE/'manuscript_extract.json').write_text(json.dumps({'sha256':digest,'records':records,'extra_text_nodes':extras,'tracked_revisions':revisions},ensure_ascii=False,indent=2)+'\n')
    checks=checked_tables(tables)
    paras=[r['text'] for r in records if r['type']=='paragraph']
    captions={}
    for s in paras:
        m=re.match(r'(Table|Figure|Listing) (\d+)\. (.*)',s)
        if m:captions[(m[1],int(m[2]))]=m[3]
    pre=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{fontspec}
\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\setsansfont{texgyreheros}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold]
\setmonofont{lmmono10-regular.otf}
\usepackage{microtype,booktabs,array,tabularx,graphicx,amsmath}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage{float,needspace,titlesec,fancyvrb,placeins}
\usepackage[hidelinks,unicode]{hyperref}
\urlstyle{same}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt plus 1pt}
\setlength{\textfloatsep}{10pt}
\setlength{\intextsep}{9pt}
\renewcommand{\arraystretch}{1.13}
\titleformat{\section}{\large\bfseries}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}
\titlespacing*{\section}{0pt}{10pt}{5pt}
\titlespacing*{\subsection}{0pt}{7pt}{3pt}
\clubpenalty=10000 \widowpenalty=10000
\emergencystretch=1em
\begin{document}
'''
    out=[pre, r'{\centering\LARGE\bfseries '+esc(paras[0])+r'\par}',r'\vspace{5pt}{\centering\small '+prose(paras[1])+r'\par}',r'{\centering\small '+prose(paras[2])+r'\par}\vspace{8pt}']
    figures=['architecture/amem_wrapper_architecture.svg','figures/01_scoring_comparison.svg','figures/02_category_heatmap.svg','figures/06_dual_scoring_f1_vs_cost.svg']
    figindex=0; code=[]; in_code=False; tablecheck=[]; paragraphcheck=[]
    for r in records[3:]:
        if r['type']=='table':
            i=r['index'];rows=tables[i-1];n=len(rows[0])
            widths={1:[.48,.25,.27],2:[.18,.12,.70],3:[.26,.36,.38],4:[.36,.30,.34],5:[.20,.14,.16,.14,.16,.20],6:[.52,.24,.24],7:[.22,.19,.23,.19,.17],8:[.19,.09,.18,.18,.18,.18],9:[.35,.325,.325]}[i]
            spec='@{}'+''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+str(w)+r'\linewidth-'+str((n-1)*8/n)+r'pt\relax}' for w in widths)+'@{}'
            out += [r'\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{'+spec+'}',r'\toprule']
            for j,row in enumerate(rows):
                out.append(' & '.join(esc(c) for c in row)+r' \\')
                if j==0:out.append(r'\midrule')
            caption=captions[('Table',i)]
            caption=re.sub(r'PR #\d+; ', '',caption)
            out += [r'\bottomrule\end{tabular}',r'\caption{'+prose(caption)+r'}\label{tab'+str(i)+'}',r'\end{table}']
            tablecheck.append({'number':i,'cells':sum(map(len,rows)),'caption':caption})
            continue
        s=r['text']
        if not s and r['drawing']:
            figindex+=1
            path=figures[figindex-1];stem=Path(path).stem
            caption=captions[('Figure',figindex)]
            caption=caption.replace(' (PR #57)','').replace('PR #54; ','')
            width=r'160mm' if figindex==1 else r'0.92\linewidth'
            out += [r'\begin{figure}['+('!htbp' if figindex==1 else 'H')+r']\centering',r'\includegraphics[width='+width+']{assets/'+stem+'.pdf}',r'\caption{'+prose(caption)+r'}\label{fig'+str(figindex)+'}',r'\end{figure}']
        elif not s:continue
        elif s.startswith(('Table ','Figure ')) and re.match(r'(Table|Figure) \d+\.',s):continue
        elif s.startswith('Listing 1.'):
            in_code=False
            out += [r'\begin{minipage}{\linewidth}',r'\VerbatimInput[fontsize=\footnotesize]{listing.py}',r'\captionof{listing}{'+prose(captions[('Listing',1)])+'}',r'\end{minipage}']
        elif r['style'].startswith('Code') or in_code or s.startswith('gates ='):
            in_code=True
            code.append(s)
        elif re.match(r'^\d+\.\d+ ',s):out.append(r'\subsection{'+esc(re.sub(r'^\d+\.\d+ ','',s))+'}');paragraphcheck.append(s)
        elif re.match(r'^\d+\. ',s):
            if s.startswith('5. '):out.append(r'\FloatBarrier')
            out.append(r'\section{'+esc(re.sub(r'^\d+\. ','',s))+'}');paragraphcheck.append(s)
        else:out.append(prose(s)+'\n');paragraphcheck.append(s)
    # Custom caption type avoids the floating-listing dependency and retains numbering.
    out[0]=out[0].replace(r'\begin{document}',r'\DeclareCaptionType{listing}[Listing][List of Listings]'+'\n'+r'\begin{document}')
    out.append(r'\end{document}')
    (HERE/'main.tex').write_text('\n'.join(out)+'\n')
    (HERE/'listing.py').write_text('\n'.join(code)+'\n')
    (HERE/'conversion_checks.json').write_text(json.dumps({'source_sha256':digest,'main_sections':sum(bool(re.match(r'^\d+\. ',s)) for s in paragraphcheck),'converted_heading_and_prose_paragraphs':len(paragraphcheck),'tables':tablecheck,'verified_fragments':checks,'figures':figures,'listing_lines':len(code),'extra_text_nodes':extras,'tracked_revisions':revisions},indent=2)+'\n')
    print(digest,'sections',len([s for s in paragraphcheck if re.match(r'^\d+\. ',s)]),'figures',figindex,'listing',len(code))

if __name__=='__main__': main()
