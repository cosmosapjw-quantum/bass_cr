"""Plot only saved integrated source physics, never MTCS coefficient curves."""
import argparse,json,time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import engine_v3 as e

def main(unit,out,runid):
    start=time.process_time();c=json.loads((unit/'inputs/CASE_V3.json').read_text());e.need(runid==c['plot_run_id'],'RUN_ID_MISMATCH')
    source=unit/'runs'/c['primary_run_id'];rows=json.loads((source/'SOURCE_WEIGHTED_RESULTS.json').read_text())
    result=json.loads((source/'RESULT.json').read_text());e.need(result['status']=='PASS','PRIMARY_NOT_PASS')
    finest=[r for r in rows if r['N']==2048 and r['R']==80];zs=c['source_z']
    fig,axes=plt.subplots(1,3,figsize=(12.5,4),constrained_layout=True)
    for chi,marker in [(1.5,'o'),(3,'s')]:
        rr=[next(r for r in finest if r['chi']==chi and r['z']==z) for z in zs];x=np.arange(len(zs));label=f'q / theta = {chi:g}'
        axes[0].plot(x,[1e6*r['new']['P_CE_active'] for r in rr],marker=marker,label=label)
        axes[1].plot(x,[-100*r['new']['neutral_induced_relative_CE_change'] for r in rr],marker=marker,label=label)
        axes[2].plot(x,[r['new']['neutral_heat_eV_per_selected'] for r in rr],marker=marker,label=label)
    labels=['CE probability per active electron (parts per million)','Neutral-induced CE reduction (%)','Neutral bath gain (eV per selected electron)']
    for ax,label in zip(axes,labels):
        ax.set_xticks(np.arange(len(zs)),zs);ax.set_xlabel('Saved source redshift');ax.set_ylabel(label);ax.grid(alpha=.25)
    axes[0].legend();fig.suptitle('Conditional neutral elastic finite-chain outcomes — N=2048, U/theta=80')
    fig.savefig(out/'NEUTRAL_INTEGRATED_OUTCOMES.png',dpi=160);plt.close(fig)
    e.writej(out/'PLOT_RESULT.json',dict(schema='N5_NEUTRAL_SAVED_PLOT_V3',status='PASS',run_id=runid,source_run_id=c['primary_run_id'],saved_source_rows=len(finest),figure='NEUTRAL_INTEGRATED_OUTCOMES.png',raw_MTCS_read=False,dense_coefficient_curves=False,new_matrices=0,new_RHS=0,new_ODE=0,process_cpu_s=time.process_time()-start))
    return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True)
    a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))

