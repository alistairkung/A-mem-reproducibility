"""Editable nested wrapper layout, verified against the accepted A-MEM source."""
from pathlib import Path
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'amem-publication-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent


def generate():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.7,
                         'svg.fonttype':'path','svg.hashsalt':'amem-wrapper-architecture'})
    fig = plt.figure(figsize=(16/2.54,15/2.54),facecolor='white')
    ax = fig.add_axes([0,0,1,1])
    ax.set(xlim=(0,160),ylim=(0,150))
    ax.axis('off')

    def text(x,y,label,**kwargs):
        ax.text(x,y,label,ha=kwargs.pop('ha','center'),va='center',color='#222222',
                linespacing=1.2,zorder=3,**kwargs)

    def box(x,y,width,height,label,gate=False):
        ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0,rounding_size=2',
                     facecolor='#EFF3F5' if gate else 'white',
                     edgecolor='#527083' if gate else '#777777',lw=1 if gate else .7,zorder=2))
        text(x+width/2,y+height/2,label)

    def arrow(points):
        for a,b in zip(points[:-2],points[1:-1]):
            ax.plot([a[0],b[0]],[a[1],b[1]],color='#666666',lw=.8,zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',
                     mutation_scale=8,lw=.8,color='#666666',zorder=1))

    ax.add_patch(Rectangle((3,22),154,125,facecolor='#F1F1F1',edgecolor='#888888',lw=.8))
    text(80,142,'Experimental wrapper',fontsize=11,fontweight='bold')
    box(25,124,110,13,'Frozen configuration · Provider adapter\nExecution controls · Langfuse · Accounting\nSeparate memory store and index per cell')
    ax.add_patch(Rectangle((8,28),144,91,facecolor='#FAFAFA',edgecolor='#AAAAAA',lw=.7))
    text(12,114,'Frozen A-MEM workflow\nwith experimental action gates',ha='left',fontweight='bold')
    box(43,99,74,10,'Create memory note\nLLM keywords / context / tags')
    box(43,86,74,9,'Retrieve up to five neighbours')
    box(38,71,84,11,'Shared LLM evolution decision\nRuns in every configuration')
    box(14,54,62,13,'Neighbour-update gate\nExisting-note contexts + tags\nSelected AND enabled',gate=True)
    box(84,54,62,13,'Strengthen gate\nNew-note links + tags\nSelected AND enabled',gate=True)
    box(43,42,74,8,'Insert new note')
    box(23,30,114,9,'QA from the completed memory store\nLLM keywords → top 10 + links → LLM answer')
    box(15,3,130,13,'Experimental evidence\nMemory states · Predictions · Scores · Traces · Costs')

    arrow([(80,124),(80,109)])
    arrow([(80,99),(80,95)])
    arrow([(80,86),(80,82)])
    # The symmetric branches identify independent mutation scopes, not parallel execution.
    arrow([(80,71),(80,69),(45,69),(45,67)])
    arrow([(80,71),(80,69),(115,69),(115,67)])
    arrow([(45,54),(45,52),(80,52),(80,50)])
    arrow([(115,54),(115,52),(80,52),(80,50)])
    arrow([(80,42),(80,39)])
    arrow([(80,30),(80,16)])

    for extension in ('svg','png'):
        path = OUT/f'amem_wrapper_architecture.{extension}'
        fig.savefig(path,dpi=300,metadata={'Date':None} if extension=='svg' else {'Software':'A-MEM architecture'})
        if extension=='svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


if __name__=='__main__':
    generate()
