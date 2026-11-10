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
    ['Saved response', 'Historical F1 / BLEU-1', 'Updated F1 / BLEU-1'],
    ['Audrey (Full A-MEM), abstained', '18.18 / 16.37', '100 / 100'],
    ['Dave (Evolution Only), chose distractor', '100 / 100', '0 / 0'],
]


HEADER_LABELS = {
    'Alternative F1': 'Updated F1', 'Alt. F1': 'Updated F1',
    'Alt. BLEU-1': 'Updated BLEU-1', 'Complementary evaluation': 'Updated evaluation',
}

PROVENANCE_EDITS = [
    (
        'I reproduce the authors’ evaluation procedure and examine whether the same directional conclusions hold.',
        'I reconstruct the historical scoring convention for comparison with the paper and apply the authors’ updated reference policy to the same saved predictions.',
    ),
    (
        'This reproduces the published overall ordering, although not its full category-level direction. Under the additional no-information reference,',
        'The three configurations shared with the paper follow its ordering on this subset, although individual categories differ. Under the upstream no-information reference,',
    ),
    ('our complementary adversarial reference', 'the upstream no-information reference'),
    (
        'The exact Table 3 question identities and retrieval settings are not fully specified.',
        'The March code establishes the historical implementation. The records do not independently establish the exact questions, retrieval settings and execution behind each published Table 3 result.',
    ),
    (
        'I set out to reproduce the mechanism-level comparison and investigate a missing fourth condition: Evolution Only, in which older memories can be updated without strengthening new memories.',
        'I reproduced the frozen Full workflow in deterministic replay and added the missing Evolution Only condition, which updates older memories without strengthening new notes.',
    ),
    (
        'Historical versus alternative-reference F1; the same 558 predictions yield different configuration rankings.',
        'Across 558 matched questions per configuration, the historical distractor puts Full first (32.69% F1). Scoring the same answers against the no-information reference puts Neither first (39.00%). Only the 121 Category 5 references change.',
    ),
    (
        'Therefore the evaluation-reference choice has a material effect on what counts as success, not merely on cosmetic presentation of results.',
        'All 437 questions in Categories 1–4 contribute identical scores under both policies. The change in the aggregate leader comes entirely from rescoring the 121 adversarial answers per configuration.',
    ),
    (
        'Evolution Only did not improve complementary F1 over Neither (−3.15 pp).',
        'Evolution Only scored below Neither on both aggregate complementary F1 (-3.15 pp) and temporal F1 (-2.44 pp), contrary to the independent temporal-benefit hypothesis.',
    ),
    (
        'The fourth condition completes a two-factor design and permits two questions: does neighbour evolution improve answers independently of linking, and do the additional memory operations justify their computational cost? Inspired by Professor Nguyen’s Pareto-oriented approach, I measured answer quality, retrieval expansion, token use and identified model charges. I also reproduced the paper-compatible evaluation and added a complementary measure for questions that require acknowledging missing information.',
        'Does neighbour evolution help independently of linking, and does the gain justify the cost? Following Professor Nguyen’s Pareto approach, I measured answer quality, retrieval, token use and identified model charges. The authors’ October 2026 update made the no-information reference the default. In the initial specification I selected updated author evaluation as primary and retained the historical distractor reference for comparison with the paper. Within this sample, changing only the Category 5 reference reversed the aggregate F1 winner. Across 558 matched questions per configuration, identical saved answers placed Full first under historical F1 (32.69%) and Neither first under updated F1 (39.00%).',
    ),
    (
        'In category 5, the agent chooses between an unsupported distractor and “Not mentioned in the conversation.” I reproduced the authors’ historical scoring method, which compares the generated answer against the supplied distractor. I also introduced a complementary evaluation to examine the agent’s ability to recognise missing information. This uses the same F1 and BLEU-1 calculations but compares against the no-information response. Binary adversarial correctness separately records whether that response was selected.',
        'The historical evaluator scored Category 5 answers against the supplied distractor. On 22 October 2026, the A-MEM authors made “Not mentioned in the conversation” the default reference and retained historical scoring through --legacy_c5_reference. Our initial specification (D11) chose updated author evaluation as primary to measure agreement with the no-information response. We retained historical evaluation as secondary for comparison with the published ablation. The T4 implementation applies the authors’ original F1 and BLEU-1 functions to the same saved predictions under both policies, changing only the Category 5 reference. Binary adversarial correctness separately measures recognition of missing information and is identical in both views for each answer.',
    ),
    (
        'Because adversarial questions contribute to overall F1 and BLEU-1, the selected reference can also change the aggregate ranking of memory configurations. Reporting both perspectives preserves the historical comparison while providing complementary evidence about unsupported answers. The binary measure is the more direct test of appropriate abstention.',
        'These two cases illustrate how identical answers can earn different overlap scores. To assess the effect on configuration rankings, I compared the question-weighted means across the full selected sample.',
    ),
    (
        'The overall ordering is not reproduced under the complementary adversarial evaluation, even though it scores precisely the same predictions using the same F1 formula. With “Not mentioned in the conversation” as category 5’s reference, Neither scores 39.00%, Linking Only 37.34% and Full 36.91%. Full also has the lowest binary adversarial correctness (71/121), compared with Neither (86/121). The two reference policies measure different aspects of the same behaviour; the complementary analysis does not invalidate or replace the historical metric.',
        'Under updated author evaluation, Neither leads at 39.00% F1, followed by Linking Only (37.34%), Full (36.91%) and Evolution Only (35.86%). The reference also changes which answers earn lexical credit. The separate abstention count is fixed across policies: Neither recognised missing information on 86/121 questions and Full on 71/121.',
    ),
    (
        'The methodological lesson is that reproducing an algorithm and reproducing a conclusion are distinct. The experiment recovers the original aggregate ordering under its own evaluation, while complementary measurement reveals how the conclusion depends on what answer quality is intended to reward.',
        'Beyond reproducing the historical convention and adding Evolution Only, this study quantified the consequences of the authors’ scoring update for the ablation. On these three conversations, Full led under historical F1 and Neither under updated F1. Every saved prediction stayed fixed.',
    ),
    ('Historical and complementary adversarial evaluation', 'Historical and updated author evaluation'),
    ('Complementary F1', 'Updated F1'),
    ('Complementary evaluation', 'Updated evaluation'),
    ('Alternative F1', 'Updated F1'),
    ('Alt. BLEU-1', 'Updated BLEU-1'),
    ('Alt. F1', 'Updated F1'),
    ('aggregate complementary F1', 'aggregate updated F1'),
    ('under complementary F1', 'under updated F1'),
    ('Alternative-reference F1', 'Updated F1'),
    ('Matched alternative-reference contrasts in percentage points', 'Matched contrasts under updated author evaluation, in percentage points'),
    ('ranks first under the paper-compatible scoring', 'ranks first under historical evaluation'),
    ('alternative-reference', 'updated'),
    ('Under the alternative reference', 'Under the updated reference'),
]


def decode(s):
    s=s.replace(r'\verb|--legacy_c5_reference|', '--legacy_c5_reference')
    s=re.sub(r'\\textbf\{([^}]+)\}',r'\1',s)
    s=re.sub(r'\\cite\{[^}]*\}', '', s)
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
        for earlier, revised in PROVENANCE_EDITS:
            expected = expected.replace(earlier, revised)
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
                expected_cell = HEADER_LABELS.get(expected_cell, expected_cell)
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
    required_links = [AUDIT_URL,
                      'https://github.com/WujiangXu/A-mem/commit/236670fefd1407ac63bcae29dd0de7fb206f569a',
                      'https://github.com/WujiangXu/A-mem/commit/b31a1dddf56f87ec762cce3539418602d7e2ffb1',
                      'https://github.com/WujiangXu/A-mem/commit/f9a173dec325d84fcc97e7828775c7b241c33466',
                      'https://github.com/alistairkung/A-mem-reproducibility/commit/5aaa5f693b7315bf2e668d7540cebbe7523f96b7',
                      'https://github.com/alistairkung/A-mem-reproducibility/commit/60e109ef4de25db97f3f0fea6bd65fffc276515c',
                      ]
    pdf_urls = {a.get('/A', {}).get('/URI') for a in links}
    assert set(required_links) <= pdf_urls, set(required_links) - pdf_urls
    for phrase in ['conv-44:qa:126', 'conv-50:qa:183', 'Not mentioned in the conversation',
                   'Strengthen the bond with her pets', 'Transforming something old and beat-up into something beautiful']:
        assert phrase in norm(pdftext), phrase
    assert not re.search(r'\b(complementary|alternative-reference|alternative F1|Alt\. (?:F1|BLEU-1))\b', pdftext, re.I)
    assert '??' not in pdftext
    for key in ['xu2025amem','locomo','amemsource','reproduction','acceptedresults','xu2026scoring']:
        assert 'cite.'+key in reader.named_destinations
    assert 'cite.xu2026scoring' in {str(d) for d in internal}
    assert '--legacy_c5_reference' in pdftext
    assert 'Student name: Alistair Chi Chuen Kung' in norm(pdftext)
    assert 'Student ID: 1155012046' in norm(pdftext)
    assert 'Figure 1:' in reader.pages[3].extract_text() and 'Listing 1:' in reader.pages[3].extract_text()
    log=(HERE/'main.log').read_text()
    assert not re.search(r'Overfull|Underfull|undefined references|Missing character|^!',log,re.M)
    result={'manuscript_sha256':hashlib.sha256(args.manuscript.read_bytes()).hexdigest(),'comparison':'pass','counts':stats,'prose_order':'preserved','authorized_changes':'citation markers; one terminology clarification; listing caption explicitly abridged/pinned; completed student attribution; policy-invariant categories; approved exploratory comparison paragraph; audited Table 3 and explanation; D11 primary/secondary policy attribution, formal upstream citation, bounded comparison with Table 3, display labels and sample-bounded ranking reversal; rendered bibliography; approved cost-scope paragraph; Pooled (derived) label','pdf_pages':len(reader.pages),'internal_links_checked':len(internal),'missing_paragraphs':missing,'table_comparison':'169 retained DOCX table cells checked (including the approved pooled label); all nine cells of replacement Table 3 checked against the verified examples','log_checks':'no overfull/underfull boxes, missing glyphs or undefined references'}
    (HERE/'fidelity_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
