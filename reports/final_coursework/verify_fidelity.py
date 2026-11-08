"""Independently compare DOCX paragraphs, captions, listing and all 184 table cells."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from docx import Document
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent

def decode(s):
    s=re.sub(r'\\cite\{[^}]*\}', '', s)
    s=s.replace('Throughout the figures, this complementary evaluation is labelled alternative-reference scoring. ', '')
    s=re.sub(r'\\href\{[^}]*\}\{([^}]*)\}',r'\1',s)
    s=re.sub(r'\\ref\{(?:fig|tab)(\d+)\}',r'\1',s)
    s=re.sub(r'\\ensuremath\{([^}]*)\}',r'\1',s)
    for a,b in [(r'\Delta','Δ'),(r'\times','×'),(r'\&','&'),(r'\%','%'),(r'\$','$'),(r'\#','#'),(r'\_','_'),('~',' ')]:s=s.replace(a,b)
    return s.replace('−','-')

def norm(s): return ' '.join(s.replace('−','-').split())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('manuscript',type=Path);args=ap.parse_args()
    source=Document(args.manuscript)
    tex=(HERE/'main.tex').read_text();plain=decode(tex)
    code=(HERE/'listing.py').read_text().splitlines()
    missing=[];stats={'headings':0,'prose_and_title_paragraphs':0,'captions':0,'listing_lines':0,'table_cells':0}
    positions=[]
    for p in source.paragraphs:
        s=p.text
        if not s:continue
        if p.style.name.startswith('Code') or s in code:
            assert s in code,s;stats['listing_lines']+=1;continue
        m=re.match(r'^(Table|Figure|Listing) (\d+)\. (.*)',s)
        if m and m[1]=='Listing':
            assert 'Abridged excerpt from' in plain
            assert 'commit 8485673' in plain
            assert 'not a continuous verbatim extract' in plain
            stats['captions']+=1
            continue
        if m:
            expected=m[3].replace(' (PR #57)','').replace('PR #54; ','').replace('PR #56; ','')
            stats['captions']+=1
        elif p.style.name.startswith('Heading'):
            expected=re.sub(r'^\d+(?:\.\d+)?\.? ', '',s);stats['headings']+=1
        else:expected=s;stats['prose_and_title_paragraphs']+=1
        if norm(expected) not in norm(plain):missing.append(s)
        if not m:positions.append(norm(plain).find(norm(expected)))
    assert positions==sorted(positions),'Prose/headings reordered'
    latex_tables=re.findall(r'\\begin\{tabular\}.*?\\toprule(.*?)\\bottomrule',tex,re.S)
    assert len(latex_tables)==len(source.tables)==9
    for i,(table,content) in enumerate(zip(source.tables,latex_tables),1):
        content=re.sub(r'\\midrule','',content)
        rows=[line.strip() for line in content.split(r'\\') if line.strip()]
        assert len(rows)==len(table.rows),(i,len(rows))
        for sr,lr in zip(table.rows,rows):
            cells=re.split(r'(?<!\\)&',lr)
            assert len(cells)==len(sr.cells)
            for a,b in zip(sr.cells,cells):
                assert norm(a.text)==norm(decode(b)),(i,a.text,b)
                stats['table_cells']+=1
    assert not missing,missing
    reader=PdfReader(HERE/'AMEM_FTEC5660_Report.pdf')
    assert len(reader.pages)<=10
    assert all(abs(float(p.mediabox.width)-595.28)<1 and abs(float(p.mediabox.height)-841.89)<1 for p in reader.pages)
    pdftext='\n'.join(p.extract_text() for p in reader.pages)
    # Verify all internal destinations resolve and all intended source links survive.
    links=[a.get_object() for p in reader.pages for a in p.get('/Annots',[])]
    internal=[a['/A']['/D'] for a in links if a.get('/A',{}).get('/S')=='/GoTo']
    assert all(str(d) in reader.named_destinations for d in internal)
    for url in ['https://arxiv.org/abs/2502.12110v11','https://snap-research.github.io/locomo/','https://github.com/alistairkung/A-mem-reproducibility/commit/8485673183d7b8018c841082d075b21158002700']:
        assert any(a.get('/A',{}).get('/URI')==url for a in links),url
    assert '??' not in pdftext
    for key in ['xu2025amem','locomo','amemsource','reproduction','acceptedresults']:
        assert 'cite.'+key in reader.named_destinations
    assert 'Student name:' in pdftext and 'Student ID:' in pdftext
    assert 'Figure 1:' in reader.pages[3].extract_text() and 'Listing 1:' in reader.pages[3].extract_text()
    log=(HERE/'main.log').read_text()
    assert not re.search(r'Overfull|Underfull|undefined references|Missing character|^!',log,re.M)
    result={'manuscript_sha256':hashlib.sha256(args.manuscript.read_bytes()).hexdigest(),'comparison':'pass','counts':stats,'prose_order':'preserved','authorized_changes':'citation markers; one terminology clarification; listing caption explicitly abridged/pinned; student placeholders; rendered bibliography','pdf_pages':len(reader.pages),'internal_links_checked':len(internal),'missing_paragraphs':missing,'table_comparison':'all cells equal, including labels and displayed precision','log_checks':'no overfull/underfull boxes, missing glyphs or undefined references'}
    (HERE/'fidelity_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
