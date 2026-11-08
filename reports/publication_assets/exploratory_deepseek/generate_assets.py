"""Exploratory DeepSeek reporting. Consumes frozen numeric evidence only; no service clients."""
from pathlib import Path
from math import fsum
import hashlib
import io
import json
import os
import sys
import subprocess
import tempfile
import platform
import zlib
from importlib.metadata import version
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'amem-publication-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import generate_assets as publication
from document_exports import export_tables

COUNTS={'conv-44':158,'conv-49':196,'conv-50':204}
POLICIES=('alternative','historical')
METRICS=('f1','bleu1')

def require(ok,message):
    if not ok:raise ValueError(message)


def summarize(rows):
    return {policy:{m:100*fsum(r[policy][m] for r in rows)/len(rows) for m in METRICS} for policy in POLICIES}


def validate(rows,evidence):
    require(len(rows)==sum(COUNTS.values()),'Incomplete DeepSeek population')
    require(evidence['source_commit']==publication.COMMIT,'Evidence source commit differs')
    require(set(evidence['conversations'])==set(COUNTS),'Conversation lineage set differs')
    from importlib.util import spec_from_file_location, module_from_spec
    spec=spec_from_file_location('deepseek_source_pins',HERE/'verify_sources.py')
    pins=module_from_spec(spec);spec.loader.exec_module(pins)
    require(evidence['policy_names']==pins.POLICIES,'Scoring policy identities differ')
    for path, item in evidence['documents'].items():
        data=subprocess.check_output(['git','show',publication.COMMIT+':'+path],cwd=publication.ROOT)
        require(item['commit']==publication.COMMIT and hashlib.sha256(data).hexdigest()==item['sha256'],'Pinned document evidence differs')
    for conv,n in COUNTS.items():
        group=[r for r in rows if r['conversation_id']==conv]
        require([r['question_id'] for r in group]==[f'{conv}:qa:{i}' for i in range(n)],'Original question identity/order differs')
        origin=evidence['conversations'][conv]
        anchor=pins.SOURCES[conv]
        require(origin['raw_scoring_sha256']==anchor['scoring'] and origin['phase_sha256']==anchor['phase']
                and origin['raw_scoring_path']==anchor['run']+'/scoring-views.json'
                and origin['acceptance']['sha256']==anchor['acceptance_sha256']
                and origin['acceptance']['path']==anchor['acceptance_path'],'Completion evidence pin differs')
        require(origin['classification']=='Degraded' and origin['question_count']==n,'Acceptance classification/count differs')
        for category in [None,1,2,3,4,5]:
            subset=group if category is None else [r for r in group if r['category']==category]
            original_key='overall' if category is None else f'category_{category}'
            for policy in POLICIES:
                original=origin['original_aggregates'][policy][original_key]
                require(original['count']==len(subset),'Raw aggregate count differs')
                for m in METRICS:
                    require(all(np.isfinite(r[policy][m]) and 0<=r[policy][m]<=1 for r in subset),'Invalid score')
                    require(abs(fsum(r[policy][m] for r in subset)/len(subset)-original[m])<1e-12,'Question scores disagree with raw accepted aggregates')
    raw={n:publication.blob(n) for n in publication.FILES}
    gpt_rows,pooled,panels,cost=publication.validate(raw)
    require([r['question_id'] for r in rows]==[r['question_id'] for r in gpt_rows],'Model populations differ')
    require(all(a['category']==b['category'] for a,b in zip(rows,gpt_rows)),'Model category identities differ')
    summaries={conv:summarize([r for r in rows if r['conversation_id']==conv]) for conv in COUNTS}
    overall=summarize(rows)
    for policy in POLICIES:
        for m in METRICS:
            weighted=fsum(COUNTS[c]*summaries[c][policy][m] for c in COUNTS)/sum(COUNTS.values())
            require(abs(weighted-overall[policy][m])<1e-12,'Weighted pooled mean differs')
            require(abs(overall[policy][m]-evidence['derived_pooled_percent'][policy][m])<1e-12,'Independent pooled evidence differs')
    return summaries,overall,pooled,raw


def make_figure(deepseek,gpt):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none','svg.hashsalt':'amem-deepseek-exploratory',
        'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':300,'figure.facecolor':'white'})
    fig,axes=plt.subplots(1,2,figsize=(15/2.54,10/2.54),sharey=True,layout='constrained')
    ymax=max(deepseek[m] for m in METRICS)*1.35
    for ax,m,label in zip(axes,METRICS,['Alternative-reference F1','Alternative-reference BLEU-1']):
        values=[deepseek[m],gpt[m]]
        bars=ax.bar([0,1],values,width=.58,color=['#456b88','#d49b45'],edgecolor='white')
        bars[1].set_hatch('///')
        ax.bar_label(bars,fmt='%.2f',padding=4,fontsize=10)
        ax.set(xticks=[0,1],xticklabels=['DeepSeek Flash','GPT-4o-mini'],ylim=(0,ymax),title=label,ylabel='Score (%)')
        ax.tick_params(axis='x',labelsize=9);ax.tick_params(labelleft=True)
    fig.suptitle('Exploratory comparison\nnot a controlled model benchmark',fontsize=12)
    fig.supxlabel('558 matched questions per model · Three Full A-MEM builds each',fontsize=8)
    return fig


def dual_policy_figure(deepseek, gpt, count):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.65), sharey=True)
    fig.subplots_adjust(left=.074, right=.985, bottom=.18, top=.67, wspace=.14)
    fig.suptitle('Exploratory — not a controlled model benchmark', x=.5, y=.985,
                 fontsize=19, weight='bold')
    fig.text(.5, .868, f'Full A-MEM · Question-weighted scores across {count} matched LoCoMo questions',
             ha='center', fontsize=13)
    for ax, policy, title in zip(axes, ['historical', 'alternative'],
                                  ['A   Historical evaluation', 'B   Complementary evaluation']):
        x = np.arange(len(METRICS))
        for offset, model, scores, color, hatch in [
            (-.19, 'DeepSeek Flash', deepseek[policy], '#456b88', ''),
            (.19, 'GPT-4o-mini', gpt[policy], '#d49b45', '///'),
        ]:
            bars = ax.bar(x + offset, [scores[m] for m in METRICS], .36, color=color,
                          edgecolor='white', hatch=hatch, label=model)
            ax.bar_label(bars, fmt='%.2f', fontsize=14, padding=3)
        ax.set_title(title, fontsize=16, loc='left', pad=8)
        ax.set(xticks=x, xticklabels=['F1', 'BLEU-1'], ylim=(0, 60), yticks=[0, 20, 40, 60])
        ax.tick_params(axis='both', labelsize=12, labelleft=True)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, alpha=.22)
    axes[0].set_ylabel('Score (%)', fontsize=12)
    fig.legend(*axes[0].get_legend_handles_labels(), loc='lower center', ncols=2,
               bbox_to_anchor=(.5, -.008), frameon=False, fontsize=13)
    return fig


def generate():
    evidence_path=HERE/'inputs/evidence.json';score_path=HERE/'inputs/question_scores.jsonl'
    evidence=json.loads(evidence_path.read_bytes())
    require(hashlib.sha256(score_path.read_bytes()).hexdigest()==evidence['snapshot_sha256'],'Numeric snapshot fingerprint differs')
    rows=[json.loads(line) for line in score_path.read_bytes().splitlines()]
    summaries,overall,gpt,raw=validate(rows,evidence)
    records=[]
    for conv,n in [*COUNTS.items(),('Pooled (derived)',sum(COUNTS.values()))]:
        result=overall if conv=='Pooled (derived)' else summaries[conv]
        records.append([conv,n,*[result[p][m] for p in POLICIES for m in METRICS]])
    frame=pd.DataFrame(records,columns=['Conversation','Questions','Alternative F1 (%)','Alternative BLEU-1 (%)','Historical F1 (%)','Historical BLEU-1 (%)'])
    frame.to_csv(HERE/'deepseek_results.csv',index=False,float_format='%.10f',lineterminator='\n')
    caption={'01_deepseek_results':{'title':'Exploratory DeepSeek Flash Full A-MEM results on three LoCoMo conversations',
        'caption':'F1 and BLEU-1 scores under both evaluation policies. Each conversation represents one completed but Degraded DeepSeek Full A-MEM lineage. These exploratory results are excluded from the primary GPT-4o-mini factorial analysis.',
        'interpretation':'The pooled row is derived here by weighting the unrounded saved question scores across 558 questions.',
        'limitation':'Generation limits and recovery histories differ across these lineages. The pooled row is a derived descriptive summary, not a previously accepted campaign total.'}}
    # Reuse the academic table exports; render only this supplementary table.
    export_tables({'01_deepseek_results':frame},caption,HERE)
    (HERE/'latex/01_deepseek_results.tex').replace(HERE/'deepseek_results.tex')
    (HERE/'latex').rmdir()
    (HERE/'publication_tables.docx').replace(HERE/'deepseek_results.docx')
    from docx import Document
    from document_exports import _normalise_docx
    # Preserve shared academic table formatting while giving the collection its exploratory identity.
    document=Document(HERE/'deepseek_results.docx')
    document.paragraphs[0].text='Exploratory DeepSeek Full A-MEM results'
    document.paragraphs[0].style='Title'
    document.paragraphs[1].text='Three completed Degraded lineages on 558 matched LoCoMo questions.'
    document.core_properties.title='Exploratory DeepSeek Full A-MEM results'
    document.save(HERE/'deepseek_results.docx');_normalise_docx(HERE/'deepseek_results.docx')
    gpt_means=gpt['corrected']['groups']['overall']['means_percent']['full']
    gpt_both = {'historical': gpt['historical']['groups']['overall']['means_percent']['full'],
                'alternative': gpt_means}
    outputs = ['deepseek_results.csv', 'deepseek_results.tex', 'deepseek_results.docx']
    for name, fig in [
        ('deepseek_vs_gpt4omini', make_figure(overall['alternative'], gpt_means)),
        ('dual_policy_full_comparison', dual_policy_figure(overall, gpt_both, len(rows))),
    ]:
        vector = HERE / (name + '.svg')
        fig.savefig(vector, metadata={'Date': None})
        vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines()) + '\n')
        fig.savefig(HERE / (name + '.png'), dpi=300, metadata={'Software': 'A-MEM exploratory reporting'})
        plt.close(fig)
        outputs.extend([vector.name, name + '.png'])
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={'scientific_source_commit':publication.COMMIT,'deepseek_evidence':evidence,
        'gpt_inputs':{'docs/reproducibility/'+n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
        'snapshot_inputs':{str(p.relative_to(HERE)):sha(p) for p in [evidence_path,score_path]},
        'outputs':{n:sha(HERE/n) for n in outputs},'code':{'generate_assets.py':sha(HERE/'generate_assets.py'),
        'verify_sources.py':sha(HERE/'verify_sources.py'), '../document_exports.py':sha(HERE.parent/'document_exports.py'),'../generate_assets.py':sha(HERE.parent/'generate_assets.py')},
        'versions':{'python':platform.python_version(),'matplotlib':matplotlib.__version__,'pandas':pd.__version__,'numpy':np.__version__,'python-docx':version('python-docx'),'lxml':version('lxml'),'pillow':version('pillow'),'zlib':zlib.ZLIB_RUNTIME_VERSION},
        'pooled_row':'Derived aggregate from 558 saved question scores; not a previously accepted campaign total',
        'aggregation_rounding_tolerance':1e-12,'table_display_decimals':2,'csv_decimals':10,
        'gpt_full_historical_percent':gpt_both['historical'],'gpt_full_alternative_percent':gpt_means,'deepseek_derived_pooled_percent':overall}
    (HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(frame.to_string(index=False))

if __name__=='__main__':generate()
