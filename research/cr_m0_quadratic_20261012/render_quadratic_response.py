"""Render existing M0 quadratic results without repeating exact arithmetic."""
from pathlib import Path
from fractions import Fraction as F
import json
import hashlib
import time
import sys
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent

def unpack(x):
    return F(int(x['numerator']), int(x['denominator']))

def render(result, source, out):
    if (out/'QUADRATIC_RESPONSE.png').exists() or (out/'QUADRATIC_RESPONSE.pdf').exists():
        raise FileExistsError('Existing figure must be preserved')
    HISTORIES = result['polynomials_power_basis']
    comparison = result['comparison']
    vals = {}
    indexed = {(r['model'],r['representation']): r for r in result['rows']}
    for row in source['rows']:
        h,p,r,s = (unpack(row['moments'][k]) for k in ('H0','p','R','S'))
        key = row['model'], row['representation']
        vals[key] = {'h':h,'p':p,'r':r,'s':s,
                     'response':{k:unpack(v) for k,v in indexed[key]['response_over_H0_qstar'].items()}}
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(2,2,figsize=(13,9),layout='constrained')
    labels = ['Constant','Linear rise','Convex rise','Concave rise','Decline to zero','Parabolic pulse']
    colors = ['#6b7280','#3483bd','#20639b','#49a078','#c27035','#8d5fa8']
    x = np.linspace(0,1,301)
    for (name,poly),label,color in zip(HISTORIES.items(),labels,colors):
        axes[0,0].plot(x,poly[0]+poly[1]*x+poly[2]*x*x,label=label,color=color,lw=1.8)
    axes[0,0].set(xlabel=r'Source time $t/T$',ylabel=r'$q(t)/q_\star$',
                  title='A. Controlled source histories',xlim=(0,1),ylim=(0,1.07))
    axes[0,0].legend(frameon=False,fontsize=8,ncol=2)
    f,l = vals['fullBED','selected_record'],vals['legacy','selected_record']
    values = [100*float(f['response'][name]) for name in HISTORIES]
    bars=axes[0,1].bar(range(6),values,color=colors,width=.7)
    axes[0,1].bar_label(bars,fmt='%.4f',fontsize=8,padding=3)
    axes[0,1].set_xticks(range(6),['Const.','Linear','Convex','Concave','Decline','Pulse'])
    axes[0,1].set(ylabel=r'$\mathcal{P}_h(T)/(H_0q_\star)$ (%)',ylim=(0,7.4),
                  title='B. Heating at T (fullBED)')
    cmp=comparison['selected_record']
    broad=cmp['all_nonnegative_quadratics']
    n0=float(unpack(broad['lower_square_witness']['node_x']))
    n1=float(unpack(broad['upper_square_witness']['node_x']))
    node=np.linspace(min(0,n0,n1)-.015,max(1,n0,n1)+.015,801)
    ff=float(f['h'])*(float(f['p'])*node**2-2*float(f['r'])*node+float(f['s']))
    ll=float(l['h'])*(float(l['p'])*node**2-2*float(l['r'])*node+float(l['s']))
    axes[1,0].plot(node,100*(ff/ll-1),color='#20639b',lw=2,label=r'$f(x)\propto(x-r)^2$')
    for bound,style,label in [('outer_ratio_lower','--','All nonnegative quadratics: bounds'),('outer_ratio_upper','--',None)]:
        axes[1,0].axhline(100*float(unpack(broad[bound])-1),color='#b14d35',ls=style,lw=1.1,label=label)
    rl=100*float(unpack(cmp['rising_class']['ratio_minimum'])-1)
    ru=100*float(unpack(cmp['rising_class']['ratio_maximum'])-1)
    axes[1,0].axhspan(rl,ru,color='#49a078',alpha=.2,label='Nondecreasing normalized subclass')
    axes[1,0].axhline(0,color='#909090',lw=.6)
    axes[1,0].set(xlabel=r'Position $r$ of source minimum',ylabel='(fullBED / legacy - 1) (%)',
                  title='C. Source shape and model difference')
    axes[1,0].legend(frameon=False,fontsize=8,loc='best')
    grid=np.linspace(0,1,101)
    aa,bb=np.meshgrid(grid,grid)
    def rising_heat(v):
        return float(v['h'])*(aa*float(v['p'])+(bb-aa)*float(2*v['r']-v['s'])+(1-bb)*float(v['s']))
    dd=np.ma.array(100*(rising_heat(f)/rising_heat(l)-1),mask=aa>bb)
    im=axes[1,1].pcolormesh(aa,bb,dd,shading='auto',cmap='viridis',rasterized=True)
    axes[1,1].plot([0,1],[0,1],color='#555555',lw=.8)
    axes[1,1].set(xlabel=r'$a=q(0)/q_\star$',ylabel=r'Bernstein coefficient $b$',
                  title=r'D. Rising family: $0\leq a\leq b\leq1$',xlim=(0,1),ylim=(0,1))
    fig.colorbar(im,ax=axes[1,1],label='Heating difference (%)',shrink=.85)
    for ax in axes.flat:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(alpha=.12)
        ax.set_axisbelow(True)
    fig.suptitle(r'Quadratic source response at $T=10^{10}$ s (316.88 yr)',fontsize=14)
    fig.supxlabel('Fixed bath and spectrum; zero prehistory; selected records.\nExact bounds use rational PSD certificates, not plot sampling. No physical-truth error bound is implied.',fontsize=9)
    fig.savefig(out/'QUADRATIC_RESPONSE.png',dpi=170)
    fig.savefig(out/'QUADRATIC_RESPONSE.pdf')
    plt.close(fig)

if __name__ == '__main__':
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    result_path = BASE/'results/QUADRATIC_RESPONSE.json'
    source_path = BASE/'inputs/CACHED_RESPONSE.json'
    result_raw, source_raw = result_path.read_bytes(), source_path.read_bytes()
    render(json.loads(result_raw), json.loads(source_raw), BASE/'results')
    receipt = {'schema':'cr-m0-graphics-recovery.v1',
       'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
       'in_process_wall_s':time.monotonic()-begin,'python':sys.version,
       'mode':'RENDER_EXISTING_RESULTS_ONLY','exact_calculation_reruns':0,
       'result_sha256':hashlib.sha256(result_raw).hexdigest(),
       'source_sha256':hashlib.sha256(source_raw).hexdigest(),
       'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'outputs':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in [BASE/'results/QUADRATIC_RESPONSE.png',BASE/'results/QUADRATIC_RESPONSE.pdf']]}
    (BASE/'evidence/GRAPHICS_RECOVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':'GRAPHICS_COMPLETE','in_process_wall_s':receipt['in_process_wall_s'],'exact_calculation_reruns':0}))
