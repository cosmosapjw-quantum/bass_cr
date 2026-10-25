"""Render only six saved finest-grid rows; no provider or solver import."""
import argparse,csv,json,time
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def writej(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main(unit,out,runid):
    started=time.process_time();c=json.loads((unit/'inputs/CONFIG.json').read_text())
    if runid!=c['plot_run_id']:raise ValueError('RUN_ID_MISMATCH')
    result=unit/'runs'/c['primary_run_id']/'SOURCE_WEIGHTED_RESULTS.json'
    allrows=json.loads(result.read_text())['rows']
    rows=sorted((r for r in allrows if r['R']==80 and r['N']==2048),key=lambda r:(r['chi'],float(r['z'])))
    if len(rows)!=6:raise ValueError('SIX_FINEST_ROWS_REQUIRED')
    fields=['chi','z','P_He_RR_active','conditional_He_RR_photon_eV','delta_time_s_active','delta_CE_active','delta_H1_RR_active']
    values=[{k:r[k] for k in fields} for r in rows]
    writej(out/'PLOT_ROWS.json',{'source':str(result.relative_to(unit)),'rows':values,'source_RHS_replay':0})
    with (out/'PLOT_ROWS.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(values)
    fig,axs=plt.subplots(1,3,figsize=(12.5,4.0),layout='constrained')
    plt.rcParams.update({'font.size':10})
    for chi,color in [(1.5,'#186ca5'),(3,'#b75121')]:
        r=[v for v in rows if v['chi']==chi];z=[float(v['z']) for v in r]
        ys=[[v['P_He_RR_active'] for v in r],[v['conditional_He_RR_photon_eV'] for v in r],[-1e3*v['delta_time_s_active'] for v in r]]
        for ax,y in zip(axs,ys):ax.plot(z,y,'o-',color=color,label=fr'$\chi={chi:g}$',linewidth=1.6,markersize=5)
    titles=['He ground capture probability','Conditional emitted photon energy','Mean stopping-time reduction']
    labels=['Probability per active initial electron','Energy (eV)','Reduction (ms; positive = earlier stop)']
    for ax,title,label in zip(axs,titles,labels):
        ax.set(title=title,xlabel='Saved source redshift z',ylabel=label)
        ax.grid(alpha=.22);ax.set_xticks([2.316,2.479,2.649]);ax.legend(frameon=False)
        ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,4),useOffset=False)
    fig.suptitle('Conditional He4 smooth-ground spontaneous RR on saved H1 chains\nT = 10000 K; R = 80; N = 2048; retained photons, frozen bath',fontsize=11)
    png=out/'HE4_RR_SAVED_RESULTS.png';pdf=out/'HE4_RR_SAVED_RESULTS.pdf'
    fig.savefig(png,dpi=180);fig.savefig(pdf);plt.close(fig)
    writej(out/'RESULT.json',{'schema':'CR_HE4_SAVED_PLOT_V1','status':'PASS','rows':6,'new_solver_calls':0,'source_provider_calls':0,'new_ODE':0,'process_cpu_s':time.process_time()-started})
    print('PASS six saved finest rows rendered')
    return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
