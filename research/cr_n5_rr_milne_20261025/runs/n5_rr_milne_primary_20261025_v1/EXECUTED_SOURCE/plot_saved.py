"""Plot only six finest source-weighted saved consumer rows."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import rr_engine as e

def main(unit,out,runid):
    c=e.verify(unit);e.need(runid==c['plot_run_id'],'RUN_ID_MISMATCH')
    saved=unit/'runs'/c['primary_run_id']/'SOURCE_WEIGHTED_RESULTS.json'
    rows=[x for x in json.loads(saved.read_text())['rows'] if x['R']==80 and x['N']==2048]
    e.need(len(rows)==6,'EXACT_SIX_FINEST_ROWS_REQUIRED')
    rows.sort(key=lambda x:(x['chi'],x['z']))
    labels=[f"χ={v['chi']:g}\nz={v['z']}" for v in rows]
    fig,axs=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
    specs=[('P_RR_active','RR chance per active electron'),('conditional_RR_photon_eV','Conditional RR photon energy [eV]'),('delta_time_s_active','Stable change in mean stop time [s]'),('delta_CE_active','Stable change in CE probability')]
    for ax,(key,title) in zip(axs.flat,specs):
        ax.bar(range(6),[r[key] for r in rows],color=['#1b778c']*3+['#a95c24']*3)
        ax.set_xticks(range(6),labels,fontsize=9);ax.set_title(title,fontsize=11)
        ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,3));ax.grid(axis='y',alpha=.22);ax.set_axisbelow(True)
    fig.suptitle('H1 ground spontaneous RR — saved finite-chain consumer\nR/θ=80, nominal N=2048; prescribed bath, no post-capture feedback',fontsize=13)
    fig.savefig(out/'RR_SAVED_RESULTS.png',dpi=180);fig.savefig(out/'RR_SAVED_RESULTS.pdf');plt.close(fig)
    e.writej(out/'PLOT_ROWS.json',dict(source=str(saved),rows=rows))
    e.writej(out/'RESULT.json',dict(status='PASS',saved_rows=6,new_RHS=0,new_quadrature=0,EXECUTION='COMPLETED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN'))
    return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
