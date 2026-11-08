"""Offline exploratory reporting checks. No inference or score recomputation."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('deepseek_publication',HERE/'generate_assets.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

@pytest.fixture(scope='module')
def inputs():
    return [json.loads(s) for s in (HERE/'inputs/question_scores.jsonl').read_bytes().splitlines()],json.loads((HERE/'inputs/evidence.json').read_bytes())


def test_source_populations_policies_and_weighted_pool(inputs):
    rows,evidence=inputs
    conv,pool,gpt,_=g.validate(rows,evidence)
    assert len(rows)==558 and set(conv)=={'conv-44','conv-49','conv-50'}
    assert {v['classification'] for v in evidence['conversations'].values()}=={'Degraded'}
    for p in g.POLICIES:
        for m in g.METRICS:
            assert abs(pool[p][m]-sum(g.COUNTS[c]*conv[c][p][m] for c in conv)/558)<1e-12
    assert pool['historical']!=pool['alternative']
    assert gpt['corrected']['groups']['overall']['n']==558


@pytest.mark.parametrize('damage',['identity','category','score','policy','classification','count','aggregate'])
def test_invalid_exploratory_inputs_rejected(inputs,damage):
    rows,e=copy.deepcopy(inputs)
    if damage=='identity':rows[0]['question_id']=rows[1]['question_id']
    if damage=='category':rows[0]['category']=5
    if damage=='score':rows[0]['alternative']['f1']=float('nan')
    if damage=='policy':rows[0]['historical'],rows[0]['alternative']=rows[0]['alternative'],rows[0]['historical'];rows[0]['historical']['f1']=.123
    if damage=='classification':e['conversations']['conv-44']['classification']='Clean'
    if damage=='count':e['conversations']['conv-44']['question_count']=159
    if damage=='aggregate':e['derived_pooled_percent']['alternative']['f1']+=1
    with pytest.raises((ValueError,ZeroDivisionError)):g.validate(rows,e)


def test_rendered_values_axes_and_caveat(inputs):
    import matplotlib.pyplot as plt
    rows,e=inputs;_,pool,gpt,_=g.validate(rows,e)
    expected=gpt['corrected']['groups']['overall']['means_percent']['full']
    fig=g.make_figure(pool['alternative'],expected)
    try:
        assert 'not a controlled model benchmark' in fig._suptitle.get_text()
        for ax,m in zip(fig.axes,g.METRICS):
            assert ax.get_ylim()[0]==0
            assert [p.get_height() for p in ax.patches]==[pool['alternative'][m],expected[m]]
            assert [t.get_text() for t in ax.get_xticklabels()]==['DeepSeek Flash','GPT-4o-mini']
    finally:plt.close(fig)


def test_deterministic_outputs_and_manifest(inputs):
    from PIL import Image
    import xml.etree.ElementTree as E
    m=json.loads((HERE/'source_manifest.json').read_text())
    assert set(m['outputs'])=={'deepseek_results.csv','deepseek_results.tex','deepseek_results.docx','deepseek_vs_gpt4omini.svg','deepseek_vs_gpt4omini.png','dual_policy_full_comparison.svg','dual_policy_full_comparison.png'}
    for name,digest in m['outputs'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
    before=(HERE/'source_manifest.json').read_bytes()
    subprocess.run([sys.executable,str(HERE/'generate_assets.py')],check=True,capture_output=True)
    assert (HERE/'source_manifest.json').read_bytes()==before
    assert E.parse(HERE/'deepseek_vs_gpt4omini.svg').getroot().tag.endswith('svg')
    with Image.open(HERE/'deepseek_vs_gpt4omini.png') as image:assert all(abs(d-300)<.1 for d in image.info['dpi'])
    assert 'Pooled (derived)' in (HERE/'deepseek_results.csv').read_text()


def test_raw_source_fingerprint_mismatch_is_rejected(tmp_path):
    spec=importlib.util.spec_from_file_location('deepseek_raw_source_verifier',HERE/'verify_sources.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    path=tmp_path/'evidence.json';path.write_text('{}')
    with pytest.raises(ValueError):verifier.pinned(path,'0'*64)


def test_original_publication_outputs_unchanged():
    manifest=json.loads((HERE.parent/'source_manifest.json').read_bytes())
    for name,digest in manifest['generated_outputs'].items():
        assert hashlib.sha256((HERE.parent/name).read_bytes()).hexdigest()==digest


def test_dual_policy_bars_match_question_weighted_means(inputs):
    from math import fsum
    import matplotlib.pyplot as plt
    rows, evidence = inputs
    _, overall, pooled, raw = g.validate(rows, evidence)
    gpt_rows = [json.loads(line) for line in raw[g.publication.FILES[0]].splitlines()]
    policies = [('historical', 'historical'), ('alternative', 'corrected')]
    gpt = {p: pooled[q]['groups']['overall']['means_percent']['full'] for p, q in policies}
    fig = g.dual_policy_figure(overall, gpt, len(rows))
    try:
        assert fig.axes[0].get_ylim() == fig.axes[1].get_ylim() == (0, 60)
        assert 'not a controlled model benchmark' in fig._suptitle.get_text()
        for ax, (ds_policy, gpt_policy) in zip(fig.axes, policies):
            expected = [100 * fsum(r[ds_policy][m] for r in rows) / len(rows) for m in g.METRICS]
            expected += [100 * fsum(r[gpt_policy]['full'][m] for r in gpt_rows) / len(gpt_rows)
                         for m in g.METRICS]
            assert [b.get_height() for b in ax.patches] == expected
            assert [t.get_text() for t in ax.texts] == [f'{v:.2f}' for v in expected]
        from PIL import Image
        from xml.etree import ElementTree
        assert ElementTree.parse(HERE/'dual_policy_full_comparison.svg').getroot().tag.endswith('svg')
        with Image.open(HERE/'dual_policy_full_comparison.png') as image:
            assert all(abs(d - 300) < .1 for d in image.info['dpi'])
    finally:
        plt.close(fig)
