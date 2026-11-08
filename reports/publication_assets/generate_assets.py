"""Deterministic reporting from the accepted Git objects. No service clients or inference."""
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
import platform
import zlib
from importlib.metadata import version
from math import fsum

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'amem-publication-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

COMMIT = '8485673183d7b8018c841082d075b21158002700'
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FILES = ['gpt4omini-558q-four-condition-scores.jsonl', 'gpt4omini-twelve-cell-analysis.json',
         'gpt4omini-f1-vs-cost.csv', 'gpt4omini-twelve-cell-results.md']
ORDER = ['neither','linking_only','evolution_only','full']
LABELS = ['Neither','Linking Only','Evolution Only','Full A-MEM']
CATEGORIES = ['Multi-hop','Temporal','Open-domain','Single-hop','Adversarial']
POLICIES = {'historical':'Historical', 'corrected':'Alternative-reference'}
CONTRASTS = {'Linking Only − Neither':{'linking_only':1,'neither':-1},
             'Evolution Only − Neither':{'evolution_only':1,'neither':-1},
             'Full − Linking Only':{'full':1,'linking_only':-1},
             'Full − Evolution Only':{'full':1,'evolution_only':-1},
             'Four-term interaction':{'full':1,'linking_only':-1,'evolution_only':-1,'neither':1}}
KEYS = ['linking_minus_neither','evolution_minus_neither','full_minus_linking','full_minus_evolution','interaction']

def require(test, message):
    if not test:
        raise ValueError(message)


def blob(name):
    return subprocess.check_output(['git','show',f'{COMMIT}:docs/reproducibility/{name}'],cwd=ROOT)


def summarize(rows):
    result = {}
    for policy in POLICIES:
        groups = {}
        for category in [None,1,2,3,4,5]:
            group = rows if category is None else [r for r in rows if r['category']==category]
            means = {arm:{metric:100*fsum(r[policy][arm][metric] for r in group)/len(group)
                          for metric in ('f1','bleu1')} for arm in ORDER}
            diffs = {key:{metric:100*fsum(fsum(w*r[policy][arm][metric] for arm,w in weights.items())
                         for r in group)/len(group) for metric in ('f1','bleu1')}
                     for key,weights in zip(KEYS,CONTRASTS.values())}
            groups['overall' if category is None else f'category_{category}'] = {
                'n':len(group),'means_percent':means,'paired_contrasts_pp':diffs}
        adv = [r for r in rows if r['category']==5]
        result[policy] = {'groups':groups,'adversarial_correct':{
            arm:{'correct':sum(r['adversarial_correct'][arm] for r in adv),'total':len(adv)} for arm in ORDER}}
    return result


def validate(raw):
    rows = [json.loads(line) for line in raw[FILES[0]].splitlines()]
    analysis = json.loads(raw[FILES[1]])
    cost = pd.read_csv(io.BytesIO(raw[FILES[2]]),dtype={'selected_model_usd':str}).set_index('condition')
    require(len(rows)==558 and len({r['question_id'] for r in rows})==558,'Question IDs must be unique and complete')
    require([sum(r['category']==c for r in rows) for c in range(1,6)]==[99,89,27,222,121],'Category population differs')
    for conv,n in [('conv-44',158),('conv-49',196),('conv-50',204)]:
        require([r['question_id'] for r in rows if r['question_id'].startswith(conv+':')]==
                [f'{conv}:qa:{i}' for i in range(n)],'Conversation identities differ')
    for r in rows:
        for policy in POLICIES:
            require(set(r[policy])==set(ORDER),'Condition identities differ')
            for values in r[policy].values():
                require(set(values)=={'f1','bleu1'} and all(isinstance(x,(int,float)) and np.isfinite(x)
                       and 0<=x<=1 for x in values.values()),'Invalid metric')
        if r['category']==5:
            require(set(r['adversarial_correct'])==set(ORDER) and all(v in (0,1) for v in r['adversarial_correct'].values()),'Invalid binary correctness')
    pooled = summarize(rows)
    panels = {conv:summarize([r for r in rows if r['question_id'].startswith(conv+':')])
              for conv in ('conv-44','conv-49','conv-50')}
    # 1e-12 pp only covers accumulation-order rounding; saved question scores are never altered.
    def compare(actual,expected,path='aggregate'):
        require(type(actual)==type(expected) or isinstance(actual,(int,float)) and isinstance(expected,(int,float)),path+' type differs')
        if isinstance(actual,dict):
            require(actual.keys()==expected.keys(),path+' keys differ')
            for k in actual:compare(actual[k],expected[k],path+'/'+k)
        elif isinstance(actual,(int,float)):
            require(abs(actual-expected)<=1e-12,path+' value differs')
        else:require(actual==expected,path+' differs')
    compare(pooled,analysis['pooled']);compare(panels,analysis['by_conversation'])
    require(set(cost.index)==set(ORDER),'Cost conditions differ')
    for arm in ORDER:
        a = analysis['f1_vs_cost'][arm]
        for col in ('f1','bleu1','native_answer_input_tokens','mean_retrieved_entries','strengthen_actions','neighbour_update_actions'):
            require(abs(float(cost.loc[arm,col])-a[col])<1e-12,'CSV and analysis disagree on '+col)
        from decimal import Decimal
        cells = [conv if arm=='full' else arm+'-'+conv for conv in panels]
        require(sum(Decimal(analysis['selected_cell_costs'][key]) for key in cells)==Decimal(cost.loc[arm,'selected_model_usd'])==Decimal(a['selected_model_usd']),'Scientific cell cost provenance differs')
        require(int(cost.loc[arm,'questions'])==558,'Cost population differs')
        for metric in ('f1','bleu1'):
            require(abs(a[metric]-pooled['corrected']['groups']['overall']['means_percent'][arm][metric])<1e-12,'Cost score differs')
    report = raw[FILES[3]].decode()
    for arm in ORDER:
        m=pooled['corrected']['groups']['overall']['means_percent'][arm]
        require(f"{m['f1']:.2f}" in report and f"{m['bleu1']:.2f}" in report,'Report rounded cross-check differs')
    return rows,pooled,panels,cost


def tables(pooled,panels,cost):
    overall = lambda policy,arm,metric:pooled[policy]['groups']['overall']['means_percent'][arm][metric]
    frames = {}
    frames['01_configurations'] = pd.DataFrame([
        [label, 'Yes' if arm in ('linking_only','full') else 'No','Yes' if arm in ('evolution_only','full') else 'No',description]
        for arm,label,description in zip(ORDER,LABELS,[
            'Original insertion; no gated memory changes','New-note links and tags','Existing-neighbour contexts and tags',
            'New-note links/tags and existing-neighbour contexts/tags'])],columns=['Configuration','Strengthening','Neighbour evolution','Affected state'])
    frames['02_overall_results'] = pd.DataFrame([[label,*[overall(policy,arm,m) for policy in POLICIES for m in ('f1','bleu1')],
            f"{pooled['corrected']['adversarial_correct'][arm]['correct']}/{pooled['corrected']['adversarial_correct'][arm]['total']}"] for arm,label in zip(ORDER,LABELS)],
            columns=['Configuration','Historical F1 (%)','Historical BLEU-1 (%)','Alternative F1 (%)','Alternative BLEU-1 (%)','Adversarial correct (n/121)'])
    frames['03_factorial_contrasts'] = pd.DataFrame([[label,*[pooled['corrected']['groups']['overall']['paired_contrasts_pp'][key][m]
        for m in ('f1','bleu1')]] for label,key in zip(CONTRASTS,KEYS)],columns=['Contrast','F1 difference (pp)','BLEU-1 difference (pp)'])
    frames['04_category_performance'] = pd.DataFrame([[cat,pooled['corrected']['groups'][f'category_{i}']['n'],label,
        *[pooled['corrected']['groups'][f'category_{i}']['means_percent'][arm][m] for m in ('f1','bleu1')]]
        for i,cat in enumerate(CATEGORIES,1) for arm,label in zip(ORDER,LABELS)],
        columns=['Category','n','Configuration','Alternative F1 (%)','Alternative BLEU-1 (%)'])
    frames['05_cost_retrieval'] = pd.DataFrame([[label,float(cost.loc[arm,'mean_retrieved_entries']),int(cost.loc[arm,'native_answer_input_tokens']),
        cost.loc[arm,'selected_model_usd'],overall('corrected',arm,'f1'),overall('corrected',arm,'bleu1')] for arm,label in zip(ORDER,LABELS)],
        columns=['Configuration','Mean retrieved entries','Native answer input tokens','Identified model cost (USD)','Alternative F1 (%)','Alternative BLEU-1 (%)'])
    frames['06_conversation_results'] = pd.DataFrame([[conv,p['corrected']['groups']['overall']['n'],label,
        *[p['corrected']['groups']['overall']['means_percent'][arm][m] for m in ('f1','bleu1')]]
        for conv,p in panels.items() for arm,label in zip(ORDER,LABELS)],
        columns=['Conversation','n','Configuration','Alternative F1 (%)','Alternative BLEU-1 (%)'])
    return frames


def pareto_mask(costs, scores):
    """Minimize identified model cost and maximize the chosen F1 perspective."""
    return [not any(c <= own_cost and s >= own_score and (c < own_cost or s > own_score)
                    for c, s in zip(costs, scores)) for own_cost, own_score in zip(costs, scores)]


def dual_cost_data(pooled, cost):
    frame = pd.DataFrame({'Configuration': LABELS,
                          'Identified model cost (USD)': [cost.loc[a, 'selected_model_usd'] for a in ORDER]})
    for policy, label in [('historical', 'Historical'), ('corrected', 'Alternative')]:
        scores = [pooled[policy]['groups']['overall']['means_percent'][a]['f1'] for a in ORDER]
        frame[f'{label} F1 (%)'] = scores
        frame[f'{label} Pareto status'] = ['Efficient' if efficient else 'Dominated' for efficient in
            pareto_mask([float(c) for c in frame['Identified model cost (USD)']], scores)]
    return frame[['Configuration', 'Identified model cost (USD)', 'Historical F1 (%)', 'Alternative F1 (%)',
                  'Historical Pareto status', 'Alternative Pareto status']]


def dual_cost_figure(frame, n):
    """Both panels use identical point costs, ranges, condition styles and status encodings."""
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True, layout='constrained')
    costs = frame['Identified model cost (USD)'].astype(float).tolist()
    all_scores = frame[['Historical F1 (%)', 'Alternative F1 (%)']].to_numpy()
    colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7']
    markers = ['o', '^', 's', 'D']
    xspan = max(costs) - min(costs)
    for ax, policy, panel in zip(axes, ['Historical', 'Alternative'], ['A', 'B']):
        scores = frame[f'{policy} F1 (%)'].tolist()
        efficient = pareto_mask(costs, scores)
        frontier = sorted((c, s) for c, s, e in zip(costs, scores, efficient) if e)
        if len(frontier) > 1:
            ax.plot(*zip(*frontier), color='#555555', linestyle=':', linewidth=1.3, zorder=1)
        for i, (label, c, score, e, color, marker) in enumerate(zip(LABELS, costs, scores, efficient, colors, markers)):
            ax.scatter(c, score, s=65, marker=marker, facecolor=color if e else 'white',
                       edgecolor=color, linewidth=1.6, zorder=3)
            # Fixed label positions reflect condition identity, never measured correctness.
            dx, dy, align = (-8, -19, 'right') if i == 3 else (7, -17, 'left') if i == 2 else (7, 8, 'left')
            ax.annotate(label, (c, score), xytext=(dx, dy), textcoords='offset points',
                        ha=align, fontsize=10)
        title = 'Historical F1' if policy == 'Historical' else 'Alternative-reference F1'
        ax.set_title(f'{panel}  {title}', loc='left', fontsize=11, pad=9)
        ax.set_xlabel('Identified model cost (USD)')
        ax.set_ylabel(title + ' (%)')
        ax.set_xlim(min(costs) - .16*xspan, max(costs) + .33*xspan)
        ax.set_ylim(float(all_scores.min()) - 1.2, float(all_scores.max()) + 1.5)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f'${value:.2f}'))
        ax.tick_params(labelleft=True)
        ax.grid(axis='y', alpha=.16)
    fig.suptitle('Cost–performance trade-offs under two evaluation policies', fontsize=13)
    fig.supxlabel(f'{n} matched questions per configuration · Three accepted scientific builds each', fontsize=9)
    handles = [Line2D([], [], marker='o', linestyle='none', markerfacecolor='black', color='black', label='Pareto-efficient'),
               Line2D([], [], marker='o', linestyle='none', markerfacecolor='white', color='black', label='Pareto-dominated')]
    axes[0].legend(handles=handles, frameon=False, loc='upper left', fontsize=9)
    return fig


def figures(pooled,cost):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,
        'svg.fonttype':'none','svg.hashsalt':'amem-publication-v1','axes.spines.top':False,'axes.spines.right':False,
        'savefig.dpi':300,'figure.facecolor':'white'})
    output=OUT/'figures';output.mkdir(exist_ok=True)
    def save(fig,name):
        fig.savefig(output/(name+'.svg'),metadata={'Date':None})
        vector=output/(name+'.svg')
        vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines())+'\n')
        fig.savefig(output/(name+'.png'),dpi=300,metadata={'Software':'A-MEM publication assets'})
        plt.close(fig)
    means=pooled['corrected']['groups']['overall']['means_percent'];x=np.arange(4)
    n=pooled['corrected']['groups']['overall']['n']
    fig,ax=plt.subplots(figsize=(7,3.9),layout='constrained')
    for offset,policy,color,hatch in [(-.19,'historical','#456b88',''),(.19,'corrected','#d49b45','///')]:
        vals=[pooled[policy]['groups']['overall']['means_percent'][a]['f1'] for a in ORDER]
        bars=ax.bar(x+offset,vals,.36,label=POLICIES[policy],color=color,hatch=hatch,edgecolor='white')
        ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    ax.set(xticks=x,xticklabels=LABELS,ylabel='F1 (%)',ylim=(0,48),title='Evaluation reference changes configuration ranking')
    ax.legend(loc='upper left',frameon=False,ncols=2,fontsize=9);ax.text(.99,.82,f'{n} matched questions per configuration',transform=ax.transAxes,ha='right',fontsize=8)
    save(fig,'01_scoring_comparison')
    fig,ax=plt.subplots(figsize=(6.7,4),layout='constrained')
    data=np.array([[pooled['corrected']['groups'][f'category_{i}']['means_percent'][a]['f1'] for a in ORDER] for i in range(1,6)])
    image=ax.imshow(data,cmap='cividis',vmin=0,vmax=100,aspect='auto')
    for i in range(5):
        for j in range(4):ax.text(j,i,f'{data[i,j]:.2f}',ha='center',va='center',color='white' if data[i,j]<48 else 'black',fontsize=11)
    ax.set(xticks=x,xticklabels=['Neither','Linking\nOnly','Evolution\nOnly','Full\nA-MEM'],yticks=np.arange(5),yticklabels=[f"{cat} (n={pooled['corrected']['groups'][f'category_{i}']['n']})" for i,cat in enumerate(CATEGORIES,1)],title='Alternative-reference F1 by category')
    fig.colorbar(image,ax=ax,label='Alternative-reference F1 (%)',shrink=.85)
    save(fig,'02_category_heatmap')
    fig,ax=plt.subplots(figsize=(6.7,3.8),layout='constrained')
    xs=[float(cost.loc[a,'selected_model_usd']) for a in ORDER];ys=[means[a]['f1'] for a in ORDER]
    frontier=[not any(xx<=xx0 and yy>=yy0 and (xx<xx0 or yy>yy0) for xx,yy in zip(xs,ys)) for xx0,yy0 in zip(xs,ys)]
    for i,(label,xx,yy,efficient) in enumerate(zip(LABELS,xs,ys,frontier)):
        ax.scatter(xx,yy,s=75,marker='o' if efficient else 'x',color='#245879' if efficient else '#8b532f',label='Observed Pareto frontier' if efficient else ('Pareto-dominated' if i==1 else None))
        ax.annotate(label,(xx,yy),xytext=(-7 if i==3 else 7,7),textcoords='offset points',ha='right' if i==3 else 'left')
    ax.set(xlabel='Identified model cost across three accepted builds (USD)',ylabel='Alternative-reference F1 (%)',title=f'F1 and model cost on the accepted {n} questions')
    ax.margins(x=.24,y=.22);ax.xaxis.set_major_formatter(FuncFormatter(lambda value,_:f'${value:.2f}'));ax.legend(frameon=False,loc='center left',fontsize=9)
    save(fig,'03_f1_vs_cost')
    fig,ax=plt.subplots(figsize=(6.2,3.8),layout='constrained')
    for arms,label,color,marker,style in [(['neither','linking_only'],'Evolution OFF','#245879','o','-'),(['evolution_only','full'],'Evolution ON','#a96c22','s','--')]:
        vals=[means[a]['f1'] for a in arms];ax.plot([0,1],vals,label=label,color=color,marker=marker,linestyle=style,linewidth=2)
        for k,val in enumerate(vals):ax.annotate(f'{val:.2f}',(k,val),xytext=(0,7 if label.endswith('OFF') else -15),textcoords='offset points',ha='center')
    interaction=pooled['corrected']['groups']['overall']['paired_contrasts_pp']['interaction']['f1']
    ax.set(xticks=[0,1],xticklabels=['Linking OFF','Linking ON'],ylabel='Alternative-reference F1 (%)',ylim=(34.5,40.2),title='Linking and neighbour evolution interaction')
    ax.text(.5,.94,f'Interaction = +{interaction:.2f} percentage points',transform=ax.transAxes,ha='center',fontsize=10)
    ax.legend(frameon=False,loc='lower right');save(fig,'04_factorial_interaction')
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.7),layout='constrained',gridspec_kw={'width_ratios':[1.5,1]})
    for ax,col,scale,ylabel in [(axes[0],'native_answer_input_tokens',1e6,'Native answer input tokens (millions)'),(axes[1],'mean_retrieved_entries',1,'Mean retrieved entries per question')]:
        vals=[float(cost.loc[a,col])/scale for a in ORDER];bars=ax.bar(x,vals,color=['#456b88','#d49b45','#456b88','#d49b45'])
        ax.bar_label(bars,labels=[f'{v:.3f}' if scale==1e6 else f'{v:.2f}' for v in vals],padding=3,fontsize=9)
        ax.set(xticks=x,xticklabels=LABELS,ylabel=ylabel,ylim=(0,max(vals)*1.22));ax.tick_params(axis='x',labelrotation=27,labelsize=8)
    fig.suptitle('Linking-expanded retrieval increases answer input volume',fontsize=12);save(fig,'05_token_overhead')
    save(dual_cost_figure(dual_cost_data(pooled, cost), n), '06_dual_scoring_f1_vs_cost')


def generate():
    raw={name:blob(name) for name in FILES}
    rows,pooled,panels,cost=validate(raw)
    frames=tables(pooled,panels,cost)
    captions=json.loads((OUT/'captions.json').read_text())
    (OUT/'tables').mkdir(exist_ok=True)
    for name,frame in frames.items():frame.to_csv(OUT/'tables'/f'{name}.csv',index=False,float_format='%.8f',lineterminator='\n')
    from document_exports import export_tables
    export_tables(frames,captions,OUT/'tables')
    companion = dual_cost_data(pooled, cost)
    companion.to_csv(OUT/'tables/07_dual_scoring_cost_performance.csv', index=False, float_format='%.8f', lineterminator='\n')
    from document_exports import write_latex
    write_latex(OUT/'tables/latex/07_dual_scoring_cost_performance.tex',
                'Cost–performance under both evaluation policies', [("", companion)])
    figures(pooled,cost)
    outputs=[p for folder in ('tables','figures') for p in sorted((OUT/folder).rglob('*')) if p.is_file()]
    digest=lambda b:hashlib.sha256(b).hexdigest()
    manifest={'source_commit':COMMIT,'inputs':{f'docs/reproducibility/{n}':digest(b) for n,b in raw.items()},
        'generated_outputs':{str(p.relative_to(OUT)):digest(p.read_bytes()) for p in outputs},
        'population':{'questions_per_condition':len(rows),'conversations':{'conv-44':158,'conv-49':196,'conv-50':204},'category_counts':[99,89,27,222,121]},
        'scoring_names':{'historical':'author-legacy-c5-v1','alternative_reference':'author-corrected-v1'},
        'aggregate_rounding_tolerance_pp':1e-12,'display_decimals':2,'versions':{'pandas':pd.__version__,'matplotlib':matplotlib.__version__,'numpy':np.__version__, 'python':platform.python_version(), 'python-docx':version('python-docx'), 'lxml':version('lxml'), 'pillow':version('pillow'), 'zlib':zlib.ZLIB_RUNTIME_VERSION},
        'code':{p.name:digest(p.read_bytes()) for p in [OUT/'generate_assets.py',OUT/'document_exports.py',OUT/'captions.json']}}
    (OUT/'source_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(f'Validated 558 matched questions and 864 aggregate metrics; generated {len(outputs)} assets.')

if __name__=='__main__':generate()
