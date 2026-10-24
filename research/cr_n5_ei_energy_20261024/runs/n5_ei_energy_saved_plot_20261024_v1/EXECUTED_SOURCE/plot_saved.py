"""Saved numerical arrays only; no coefficient, generator or solver import."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main(unit,out,run_id):
    t=time.process_time();c=json.loads((unit/'inputs/CASE.json').read_text());assert run_id==c['plot_run_id'];p=unit/'runs'/c['primary_run_id'];paths=[p/'COEFFICIENT_PLOT_DATA.npz',p/'SOURCE_WEIGHTED_RESULTS.json'];pins=[]
    for f in paths:
        d=f.read_bytes();pins.append(dict(path=str(f.relative_to(unit)),bytes=len(d),sha256=hashlib.sha256(d).hexdigest()))
    a=np.load(paths[0]);rows=json.loads(paths[1].read_text());E=a['plot_E_eV'];colors=['#c43c39','#2378b4','#25935e'];labels=[s['label'] for s in c['species']]
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    ax=axs[0,0];ax.plot(E,a['plot_EE_mu'],label='EE',color='#555555')
    for color,label in zip(colors,labels):ax.plot(E,a['plot_'+label+'_mu'],label=label,color=color)
    ax.set(xscale='log',yscale='symlog',xlabel='Tagged energy (eV)',ylabel='Signed drift (eV / s)',title='Maxwellian energy drift');ax.set_yscale('symlog',linthresh=1e-10);ax.axhline(0,color='#bbbbbb',lw=.7);ax.legend(fontsize=8)
    ax=axs[0,1]
    for color,label in zip(colors,labels):ax.plot(E,a['plot_'+label+'_D']/a['plot_EE_D'],label=label,color=color)
    total=sum(a['plot_'+label+'_D'] for label in labels)/a['plot_EE_D'];ax.plot(E,total,label='EI total',color='black',ls='--');ax.set(xscale='log',yscale='log',xlabel='Tagged energy (eV)',ylabel='EI / EE diffusion',title='Diffusion ratio at the same energy');ax.legend(fontsize=8)
    ax=axs[1,0]
    for j,chi in enumerate(c['chi']):
      for N,style in [(1024,':'),(2048,'-')]:
        rr=[r for r in rows if r['chi']==chi and r['R']==80 and r['N']==N];rr.sort(key=lambda x:x['z']);ax.plot([float(r['z']) for r in rr],[r['new']['ion_heat_eV_per_selected'] for r in rr],style+'o',color=['#7d4da3','#db8929'][j],label=f'χ={chi:g}, N={N}')
    ax.set(xlabel='Source redshift z',ylabel='Ion bath gain (eV / selected electron)',title='Integrated first-stop ion heat, R=80');ax.legend(fontsize=8)
    ax=axs[1,1];ax2=ax.twinx()
    for j,chi in enumerate(c['chi']):
      for N,style in [(1024,':'),(2048,'-')]:
        rr=[r for r in rows if r['chi']==chi and r['R']==80 and r['N']==N];rr.sort(key=lambda x:x['z']);z=[float(r['z']) for r in rr];color=['#7d4da3','#db8929'][j]
        ax.plot(z,[100*r['new']['EI_induced_relative_CE_change'] for r in rr],style+'o',color=color,label=f'CE χ={chi:g}, N={N}')
        ax2.plot(z,[100*(r['new']['no_CE_MFPT_s_active']/r['old']['no_CE_MFPT_s_active']-1) for r in rr],style+'s',color=color,alpha=.45)
    ax.set(xlabel='Source redshift z',ylabel='CE probability change (%)',title='Paired EI effects; circles CE, squares entry time');ax2.set_ylabel('No-CE first-entry mean change (%)');ax.legend(fontsize=7,loc='best')
    for ax in axs.flat:ax.grid(True,alpha=.2)
    fig.suptitle('Selected H1⁺ / He4⁺ / He4²⁺ energy exchange at T = 10,000 K',fontsize=14)
    fig.savefig(out/'EI_ENERGY_DIAGNOSTICS.png',dpi=160);plt.close(fig)
    with (out/'PLOT_RECEIPT.json').open('x') as f:json.dump(dict(status='PASS',source_pins=pins,science_recomputation=0,process_cpu_s=time.process_time()-t,figure='EI_ENERGY_DIAGNOSTICS.png'),f,indent=2);f.write('\n')
    return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))
