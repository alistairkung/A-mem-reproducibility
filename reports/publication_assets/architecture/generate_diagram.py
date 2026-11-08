"""Render the editable, source-verified architecture at its intended 16 cm width."""
from pathlib import Path
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'amem-publication-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT=Path(__file__).resolve().parent

def generate():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'svg.fonttype':'path','svg.hashsalt':'amem-wrapper-architecture'})
    fig=plt.figure(figsize=(16/2.54,16.6/2.54),facecolor='white')
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,160),ylim=(0,166));ax.axis('off')
    def text(x,y,s,**kw):
        kw.setdefault('ha','center')
        ax.text(x,y,s,va='center',color='#222222',**kw)
    def area(x,y,w,h,title):
        ax.add_patch(Rectangle((x,y),w,h,facecolor='#F6F6F6',edgecolor='#888888',lw=.7,zorder=0))
        text(x+3,y+h-4,title,ha='left',fontweight='bold')
    def box(x,y,w,h,s,accent=False):
        ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='#41657A' if accent else '#666666',lw=1 if accent else .7,zorder=2))
        text(x+w/2,y+h/2,s,linespacing=1.3,zorder=3)
    def arrow(points,dashed=False,double=False):
        for p,q in zip(points[:-2],points[1:-1]):ax.plot([p[0],q[0]],[p[1],q[1]],color='#666666',lw=.8,ls=(0,(3,2)) if dashed else '-',zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='<->' if double else '-|>',mutation_scale=7,lw=.8,linestyle=(0,(3,2)) if dashed else '-',color='#666666',zorder=1))
    area(3,122,154,41,'Experimental inputs and wrapper controls')
    box(6,145,35,10,'Frozen author source\nUnchanged files')
    box(44,145,35,10,'LoCoMo + manifest\nFrozen turn / QA IDs')
    box(82,145,35,10,'Four configurations\nTwo action factors')
    box(120,145,34,10,'GPT-4o-mini\nFrozen settings')
    box(6,126,47,14,'Bound evolution copy\nGate original action guards',True)
    box(57,126,44,14,'Isolated execution\nNew store / index per cell')
    box(105,126,49,14,'Controlled model adapter\nOpenRouter → OpenAI only\nReserve → call → account')
    arrow([(23,145),(23,140)]);arrow([(61,145),(71,140)])
    arrow([(99,145),(99,142),(30,142),(30,140)])
    arrow([(137,145),(137,140)])
    area(3,42,154,76,'Author scientific workflow with bound action gates')
    # Construction follows the unchanged author methods, with only action guards gated.
    box(6,97,27,12,'Conversation\nturn')
    box(37,97,34,12,'LLM metadata\nKeywords / context\nTags')
    box(75,97,34,12,'Retrieve up to\nfive neighbours')
    box(113,97,41,12,'Shared LLM decision\nAll configurations')
    for p,q in [(33,37),(71,75),(109,113)]:arrow([(p,103),(q,103)])
    # The group is a single action application stage. The two guards are independent.
    box(6,74,89,17,'',True)
    text(50.5,88,'Apply only selected and enabled actions',fontsize=8)
    text(28,79.5,'strengthen\nNew links / tags',fontsize=8)
    text(71,79.5,'update_neighbor\nNeighbour context / tags',fontsize=8)
    ax.plot([49,49],[75,84],color='#BBBBBB',lw=.6)
    box(106,74,48,17,'Insert new note\nAuthor counter / consolidation')
    arrow([(133.5,97),(133.5,94),(50.5,94),(50.5,91)])
    arrow([(95,82.5),(106,82.5)])
    arrow([(30,126),(30,120),(1,120),(1,82.5),(6,82.5)])
    # One boundary-level bidirectional link covers all four marked LLM stages.
    arrow([(79,126),(79,118)])
    arrow([(130,126),(130,118)],double=True)
    text(111,121,'All LLM calls',fontsize=8)
    text(42,66,'QA reads the completed cell store',fontsize=8)
    arrow([(130,74),(130,69),(92,69),(92,60)])
    box(6,47,27,13,'Question')
    box(37,47,34,13,'LLM question\nkeywords')
    box(75,47,34,13,'Initial top 10\n+ author\nlink expansion')
    box(113,47,41,13,'LLM answer')
    for p,q in [(33,37),(71,75),(109,113)]:arrow([(p,53.5),(q,53.5)])
    area(3,3,154,34,'Evidence')
    box(6,9,34,19,'Memory states\nRetrieval index\nLocal evidence')
    box(44,9,47,19,'Saved predictions → scores\nHistorical / alternative\nF1 · BLEU-1\nBinary adversarial')
    box(95,9,27,19,'Passive capture\nLangfuse traces\n+ Experiments')
    box(126,9,28,19,'Request ledger\nProvider-charge\nreconciliation')
    arrow([(130,74),(155.5,74),(155.5,40),(23,40),(23,28)])
    arrow([(133.5,47),(133.5,39),(67.5,39),(67.5,28)])
    arrow([(108.5,42),(108.5,28)],dashed=True)
    arrow([(91,18.5),(95,18.5)],dashed=True)
    arrow([(154,133),(159,133),(159,31),(140,31),(140,28)],dashed=True)
    for ext in ('svg','png'):
        target=OUT/f'amem_wrapper_architecture.{ext}'
        fig.savefig(target,dpi=300,metadata={'Date':None} if ext=='svg' else {'Software':'A-MEM architecture'})
        if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
    plt.close(fig)

if __name__=='__main__':generate()
