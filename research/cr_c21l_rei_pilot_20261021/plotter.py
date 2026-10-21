"""Plot saved actual endpoints only; four signed LRS initial-source branches."""
import argparse,csv,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'runtime/mplconfig'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(out):
    out=Path(out);rows=[]
    for p in sorted((out/'cases').glob('*/RESULT.json')):
        r=json.loads(p.read_text())
        if r['status']=='COMPLETE':rows.append(r)
    if not rows:raise RuntimeError('NO_COMPLETED_SAVED_RESULTS')
    plotdir=out/'plots';plotdir.mkdir(exist_ok=False)
    for field,label in [('Sigma_F',r'Final $\Sigma_F$'),('Pi_F',r'Final $\Pi_F$')]:
        fig,axes=plt.subplots(2,2,figsize=(10.4,8.5),layout='constrained',sharex=True,sharey=True)
        values=[r['endpoint'][field] for r in rows];norm=matplotlib.colors.Normalize(vmin=min(values),vmax=max(values))
        for ax,(ss,ps) in zip(axes.flat,[(1,1),(1,-1),(-1,1),(-1,-1)]):
            # Membership uses requested source-family signs; coordinates use actual fields.
            rr=[r for r in rows if ss*r['mapping']['requested_S0']>=0 and ps*r['mapping']['requested_P0']>=0]
            x=[r['mapping']['actual']['Sigma_F'] for r in rr];y=[r['mapping']['actual']['Pi_F'] for r in rr];c=[r['endpoint'][field] for r in rr]
            im=ax.scatter(x,y,c=c,s=115,cmap='viridis',norm=norm,edgecolors='white',linewidths=.6)
            ax.set_title(r'$S_0\ %s\ 0,\ P_0\ %s\ 0$'%('≥' if ss>0 else '≤','≥' if ps>0 else '≤'))
            ax.set_xlabel(r'Actual initial $\Sigma_{F,0}=\sqrt{6}|s_0|/H_0$')
            ax.set_ylabel(r'Actual initial $\Pi_{F,0}=(8\pi G/c^2)\sqrt{6}|p_0|/H_0^2$')
            ax.grid(alpha=.2);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        fig.colorbar(im,ax=axes,label=label,shrink=.85)
        fig.suptitle('EXPLORATORY / PRELIMINARY — LRS collisionless Einstein–Boltzmann–Vlasov\nz=20 → 4; Frobenius norms, H in s⁻¹; zero-axis cases shared between panels',fontsize=12)
        for suffix in ('png','pdf'):fig.savefig(plotdir/('initial_norms_final_'+field+'.'+suffix),dpi=180)
        plt.close(fig)
    print(json.dumps({'plotted_completed_cases':len(rows),'directory':str(plotdir),'global_error_bound':None}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);plot(ap.parse_args().out)
