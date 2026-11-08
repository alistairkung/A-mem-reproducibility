"""Offline population, arithmetic, provenance and deliverable checks."""
import copy
import importlib.util
import json
from pathlib import Path
import hashlib
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('publication_generator',HERE/'generate_assets.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

@pytest.fixture(scope='module')
def raw():
    return {n:g.blob(n) for n in g.FILES}


def test_frozen_source_population_and_policy_separation(raw):
    rows,pooled,panels,cost=g.validate(raw)
    assert g.COMMIT=='8485673183d7b8018c841082d075b21158002700'
    assert len(rows)==558 and len(panels)==3
    assert pooled['historical']!=pooled['corrected']
    assert max(pooled['historical']['groups']['overall']['means_percent'],key=lambda a:pooled['historical']['groups']['overall']['means_percent'][a]['f1'])=='full'
    assert max(pooled['corrected']['groups']['overall']['means_percent'],key=lambda a:pooled['corrected']['groups']['overall']['means_percent'][a]['f1'])=='neither'


@pytest.mark.parametrize('damage',['duplicate','category','condition','policy','nan','aggregate','cost','tokens','binary'])
def test_corrupted_reporting_inputs_fail(raw,damage):
    data=copy.deepcopy(raw)
    rows=[json.loads(l) for l in data[g.FILES[0]].splitlines()]
    if damage=='duplicate':rows[1]['question_id']=rows[0]['question_id']
    if damage=='category':rows[0]['category']=1
    if damage=='condition':rows[0]['corrected']['unknown']=rows[0]['corrected']['full']
    if damage=='policy':rows[0]['historical']['full']['f1']=.123
    if damage=='nan':rows[0]['corrected']['full']['f1']=float('nan')
    if damage=='binary':next(r for r in rows if r['category']==5)['adversarial_correct']['full']=2
    if damage in ('duplicate','category','condition','policy','nan','binary'):
        data[g.FILES[0]]='\n'.join(json.dumps(r) for r in rows).encode()
    elif damage=='aggregate':
        a=json.loads(data[g.FILES[1]]);a['pooled']['corrected']['groups']['overall']['paired_contrasts_pp']['interaction']['f1']*=100
        data[g.FILES[1]]=json.dumps(a).encode()
    else:
        text=data[g.FILES[2]].decode();lines=text.splitlines();cells=lines[1].split(',');cells[2 if damage=='cost' else 5]='999';lines[1]=','.join(cells);data[g.FILES[2]]='\n'.join(lines).encode()
    with pytest.raises((ValueError,KeyError)):g.validate(data)


def test_output_inventory_hashes_labels_and_units(raw):
    manifest=json.loads((HERE/'source_manifest.json').read_text())
    assert manifest['inputs']=={'docs/reproducibility/'+n:hashlib.sha256(b).hexdigest() for n,b in raw.items()}
    expected={f'figures/{n}.{ext}' for n in ['01_scoring_comparison','02_category_heatmap','03_f1_vs_cost','04_factorial_interaction','05_token_overhead','06_dual_scoring_f1_vs_cost'] for ext in ['svg','png']}
    stems=['01_configurations','02_overall_results','03_factorial_contrasts','04_category_performance','05_cost_retrieval','06_conversation_results']
    expected|={f'tables/{s}.csv' for s in stems}|{f'tables/latex/{s}.tex' for s in stems}|{'tables/publication_tables.docx','tables/07_dual_scoring_cost_performance.csv','tables/latex/07_dual_scoring_cost_performance.tex'}
    assert set(manifest['generated_outputs'])==expected
    for name,digest in manifest['generated_outputs'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
    assert 'Historical F1 (%)' in (HERE/'tables/02_overall_results.csv').read_text()
    assert 'difference (pp)' in (HERE/'tables/03_factorial_contrasts.csv').read_text()
    assert 'Alternative-reference' in (HERE/'figures/01_scoring_comparison.svg').read_text()
    assert 'Pareto-dominated' in (HERE/'figures/03_f1_vs_cost.svg').read_text()


def test_deterministic_regeneration_and_png_resolution():
    import subprocess,sys
    from PIL import Image
    before=(HERE/'source_manifest.json').read_bytes()
    subprocess.run([sys.executable,str(HERE/'generate_assets.py')],cwd=g.ROOT,check=True,capture_output=True)
    assert (HERE/'source_manifest.json').read_bytes()==before
    for p in (HERE/'figures').glob('*.png'):
        with Image.open(p) as image:
            assert all(abs(dpi-300)<.1 for dpi in image.info['dpi'])
            assert image.width>=1800 and image.height>=1000


def test_word_tables_use_explicit_academic_greyscale():
    from zipfile import ZipFile
    from lxml import etree
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    attr=lambda name:'{'+ns['w']+'}'+name
    with ZipFile(HERE/'tables/publication_tables.docx') as archive:
        xml=etree.fromstring(archive.read('word/document.xml'))
        tables=xml.findall('.//w:tbl',ns)
        assert len(tables)==7  # Table 4 has separate F1 and BLEU-1 panels.
        for table in tables:
            assert table.find('w:tblPr/w:tblStyle',ns).get(attr('val'))=='AMEMAcademic'
            for row in table.findall('w:tr',ns):
                for cell in row.findall('w:tc',ns):
                    shade=cell.find('w:tcPr/w:shd',ns)
                    assert shade.get(attr('fill')) in {'FFFFFF','E6E6E6','F2F2F2'}
                    assert all('theme' not in key.lower() for key in shade.attrib)
                    for color in cell.findall('.//w:rPr/w:color',ns):
                        assert color.get(attr('val'))=='000000'
                        assert all('theme' not in key.lower() for key in color.attrib)



def test_dual_policy_costs_scores_frontiers_and_axes(raw):
    import matplotlib.pyplot as plt
    _, pooled, _, cost = g.validate(raw)
    frame = g.dual_cost_data(pooled, cost)
    assert frame['Historical Pareto status'].tolist() == ['Efficient','Efficient','Dominated','Efficient']
    assert frame['Alternative Pareto status'].tolist() == ['Efficient','Dominated','Dominated','Dominated']
    fig = g.dual_cost_figure(frame, len([json.loads(l) for l in raw[g.FILES[0]].splitlines()]))
    try:
        left, right = fig.axes
        assert left.get_xlim() == right.get_xlim() and left.get_ylim() == right.get_ylim()
        for ax, policy, name in [(left,'historical','Historical'), (right,'corrected','Alternative')]:
            for i, arm in enumerate(g.ORDER):
                point = ax.collections[i]
                c, f1 = point.get_offsets()[0]
                assert c == float(cost.loc[arm,'selected_model_usd'])
                assert f1 == pooled[policy]['groups']['overall']['means_percent'][arm]['f1']
                assert frame.iloc[i][name+' F1 (%)'] == f1
                assert any(t.get_text()==g.LABELS[i] for t in ax.texts)
        for a,b in zip(left.collections,right.collections):
            assert (a.get_edgecolors()==b.get_edgecolors()).all()
            assert (a.get_paths()[0].vertices==b.get_paths()[0].vertices).all()
        assert g.pareto_mask([1,1,2],[2,2,1]) == [True,True,False]
    finally:
        plt.close(fig)


def test_dual_exports_are_valid_and_old_figure_compatible():
    import xml.etree.ElementTree as ET
    import subprocess
    path=HERE/'figures/06_dual_scoring_f1_vs_cost.svg'
    assert ET.parse(path).getroot().tag.endswith('svg')
    assert 'Historical F1' in path.read_text() and 'Alternative-reference F1' in path.read_text()
    for ext in ('png','svg'):
        p=HERE/f'figures/03_f1_vs_cost.{ext}'
        old=subprocess.check_output(['git','show','bd520b1:reports/publication_assets/figures/'+p.name],cwd=g.ROOT)
        assert p.read_bytes()==old
