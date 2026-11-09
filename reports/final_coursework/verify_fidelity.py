"""Independently compare DOCX paragraphs, captions, listing and the approved example table alongside the retained DOCX tables."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from docx import Document
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
# Explicit user-approved editorial replacements; all other DOCX content stays fixed.
ORIGINAL_COST_PARAGRAPH = 'There was also an important difference between scientific inference cost and the cost of conducting research. The twelve accepted GPT-4o-mini builds incurred approximately $4.70 in identified model charges, while broader conservative campaign exposure, including failed attempts, held reservations and metered Langfuse service, reached $10.46. Only the accepted-build model charges belong in Section 5’s like-for-like Pareto comparison.'
APPROVED_COST_PARAGRAPH = 'There was also an important difference between scientific inference cost and the cost of conducting research. The twelve accepted GPT-4o-mini builds incurred approximately $4.06 in identified model charges. Campaign-wide identified model charges, including earlier failed attempts and compatibility checks, totalled approximately $4.70. Broader conservative campaign exposure, including held reservations and a conservative upper bound for Langfuse service, reached $10.46. Only the accepted-build model charges belong in Section 5’s like-for-like Pareto comparison.'


CATEGORY_CLARIFICATION = 'Multi-hop, temporal, open-domain and single-hop F1 are identical under both policies because only the adversarial reference changes.'
ORIGINAL_DEEPSEEK_PARAGRAPH = 'Despite these obstacles, three DeepSeek Flash Full A-MEM lineages completed in Degraded status. Table 8 summarises their saved scores, including a newly derived question-weighted pooled row. DeepSeek produced higher observed word-overlap scores than the GPT-4o-mini Full baselines (alternative F1 50.37% versus 36.91%), but this was not a controlled comparison: model, generation caps, provider, compatibility policy and recovery history differed. I eventually recognised that I was optimising a model-porting exercise rather than reproducing the paper’s mechanism experiment. I returned to GPT-4o-mini for the primary factorial study. API compatibility, I learned, is not experimental equivalence.'
APPROVED_DEEPSEEK_PARAGRAPH = 'Three DeepSeek Flash Full A-MEM lineages completed in Degraded status. Table 8 pools their saved scores by question. On the same 558 questions, DeepSeek had higher observed F1 and BLEU-1 than GPT-4o-mini Full A-MEM under both policies. This comparison was exploratory. Each model contributed one build per conversation, and provider routes, generation caps, compatibility handling and recovery histories differed. I had spent more time porting the model than testing the memory mechanisms. I returned to GPT-4o-mini to follow the paper’s model choice more closely in the primary factorial study.'


AUDIT_URL = ('https://github.com/alistairkung/A-mem-reproducibility/blob/'
             '930254d9c4c1c430899a25fe42a94fa164a85812/reports/adversarial_scoring_audit/five_examples.md')
EXAMPLE_CAPTION = ('Two verified Category 5 predictions from the accepted GPT-4o-mini experiment. '
                   'Each row scores one saved answer under both references (percent). '
                   'The cases illustrate the scoring rule; aggregate estimates use the full question population.')
EXAMPLE_ROWS = [
    ['Saved response', 'Historical F1 / BLEU-1', 'Complementary F1 / BLEU-1'],
    ['Audrey (Full A-MEM), abstained', '18.18 / 16.37', '100 / 100'],
    ['Dave (Evolution Only), chose distractor', '100 / 100', '0 / 0'],
]


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
    assert CATEGORY_CLARIFICATION in plain
    replacements = {ORIGINAL_COST_PARAGRAPH: APPROVED_COST_PARAGRAPH,
                    ORIGINAL_DEEPSEEK_PARAGRAPH: APPROVED_DEEPSEEK_PARAGRAPH}
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
            if m[1] == 'Table' and m[2] == '3':
                expected = EXAMPLE_CAPTION
            stats['captions']+=1
        elif p.style.name.startswith('Heading'):
            expected=re.sub(r'^\d+(?:\.\d+)?\.? ', '',s);stats['headings']+=1
        else:
            expected=replacements.get(s, s)
            stats['prose_and_title_paragraphs']+=1
        if norm(expected) not in norm(plain):missing.append(s)
        if not m:positions.append(norm(plain).find(norm(expected)))
    assert positions==sorted(positions),'Prose/headings reordered'
    latex_tables=re.findall(r'\\begin\{tabular\}.*?\\toprule(.*?)\\bottomrule',tex,re.S)
    assert len(latex_tables)==len(source.tables)==9
    for i,(table,content) in enumerate(zip(source.tables,latex_tables),1):
        content=re.sub(r'\\midrule','',content)
        rows=[line.strip() for line in content.split(r'\\') if line.strip()]
        if i == 3:
            assert [[norm(cell) for cell in row.split('&')] for row in rows] == EXAMPLE_ROWS
            stats['verified_example_table_cells'] = sum(map(len, EXAMPLE_ROWS))
            continue
        assert len(rows)==len(table.rows),(i,len(rows))
        for sr,lr in zip(table.rows,rows):
            cells=re.split(r'(?<!\\)&',lr)
            assert len(cells)==len(sr.cells)
            for a,b in zip(sr.cells,cells):
                expected_cell='Pooled (derived)' if i==8 and a.text=='Pooled*' else a.text
                assert norm(expected_cell)==norm(decode(b)),(i,a.text,b)
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
    assert any(a.get('/A', {}).get('/URI') == AUDIT_URL for a in links)
    for phrase in ['conv-44:qa:126', 'conv-50:qa:183', 'Not mentioned in the conversation',
                   'Strengthen the bond with her pets', 'Transforming something old and beat-up into something beautiful']:
        assert phrase in norm(pdftext), phrase
    assert '??' not in pdftext
    for key in ['xu2025amem','locomo','amemsource','reproduction','acceptedresults']:
        assert 'cite.'+key in reader.named_destinations
    assert 'Student name: Alistair Chi Chuen Kung' in norm(pdftext)
    assert 'Student ID: 1155012046' in norm(pdftext)
    assert 'Figure 1:' in reader.pages[3].extract_text() and 'Listing 1:' in reader.pages[3].extract_text()
    log=(HERE/'main.log').read_text()
    assert not re.search(r'Overfull|Underfull|undefined references|Missing character|^!',log,re.M)
    result={'manuscript_sha256':hashlib.sha256(args.manuscript.read_bytes()).hexdigest(),'comparison':'pass','counts':stats,'prose_order':'preserved','authorized_changes':'citation markers; one terminology clarification; listing caption explicitly abridged/pinned; completed student attribution; policy-invariant categories; approved exploratory comparison paragraph; audited Table 3 and explanation; rendered bibliography; approved cost-scope paragraph; Pooled (derived) label','pdf_pages':len(reader.pages),'internal_links_checked':len(internal),'missing_paragraphs':missing,'table_comparison':'169 retained DOCX table cells checked (including the approved pooled label); all nine cells of replacement Table 3 checked against the verified examples','log_checks':'no overfull/underfull boxes, missing glyphs or undefined references'}
    (HERE/'fidelity_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
