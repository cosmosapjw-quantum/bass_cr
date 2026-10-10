# SPDX-License-Identifier: GPL-3.0-only
"""Render the conditional component, never a total IGM history."""
from pathlib import Path
import sys,json,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from causal_subthreshold import CoulombClock,DirectElectronSource,aggregate,YEAR_S,ROOT

out=ROOT/'evidence'
clock=CoulombClock();source=DirectElectronSource(64)
times=np.linspace(1,1e10/YEAR_S,81)
rows=[aggregate(source,clock,float(t*YEAR_S),64,64) for t in times]
cols=['time_year','stopping_heat_power_J_m3_s','terminal_selected_heat_power_J_m3_s',
      'deposited_stopping_energy_J_m3','active_electron_kinetic_J_m3',
      'cutoff_residual_kinetic_J_m3','injected_selected_electron_energy_J_m3']
with (out/'CAUSAL_SUBTHRESHOLD.csv').open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader()
    wr.writerows({k:r[k] for k in cols} for r in rows)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
                     'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(12.2,4.6),layout='constrained')
causal=np.array([r[cols[1]] for r in rows])/1e-43
term=np.array([r[cols[2]] for r in rows])/1e-43
axs[0].plot(times,term,color='#778695',lw=2,ls='--',label='Terminal heat proxy')
axs[0].plot(times,causal,color='#087f8c',lw=2.8,label='Causal Coulomb stopping')
axs[0].set(xlabel='Time since proton source turn-on [yr]',ylabel=r'Power [$10^{-43}$ J m$^{-3}$ s$^{-1}$]',
           title='Instantaneous power: same direct-electron band',xlim=(0,times[-1]),ylim=(0,1.2))
axs[0].annotate('22.08% of terminal proxy',xy=(times[-1],causal[-1]),xytext=(120,.51),
               arrowprops={'arrowstyle':'->','color':'#087f8c'},color='#065f69',fontsize=10)
axs[0].legend(loc='upper left',frameon=False,fontsize=10)
f=np.array([[r['deposited_stopping_energy_J_m3'],r['active_electron_kinetic_J_m3'],r['cutoff_residual_kinetic_J_m3']]
            for r in rows])/np.array([r['injected_selected_electron_energy_J_m3'] for r in rows])[:,None]*100
axs[1].stackplot(times,f.T,colors=['#087f8c','#c9d7e2','#eab75a'],
                 labels=['Deposited stopping energy','Active electron kinetic energy','Cutoff residual (unresolved)'])
axs[1].set(xlabel='Time since proton source turn-on [yr]',ylabel='Fraction of cumulative band injection [%]',
           title='Cumulative energy ledger',xlim=(0,times[-1]),ylim=(0,100))
axs[1].text(145,63,'83.89% active',color='#334657',fontsize=12)
axs[1].text(145,7,'15.58% deposited',color='white',fontsize=11)
axs[1].text(230,95,'0.53% cutoff',color='#5e4707',fontsize=10)
axs[1].legend(loc='center left',bbox_to_anchor=(0,-.28),frameon=False,fontsize=9)
fig.suptitle('CR-PHYS02A  |  directly ejected 0.1–10 eV electrons',fontsize=16,fontweight='bold')
fig.supxlabel('Fixed 100 K bath; leading-log classical Coulomb model; local ramp source. Full secondary cascade remains open.',fontsize=9)
fig.savefig(out/'CAUSAL_SUBTHRESHOLD.png',dpi=180)
fig.savefig(out/'CAUSAL_SUBTHRESHOLD.svg')
print(json.dumps({'rows':len(rows),'files':['CAUSAL_SUBTHRESHOLD.csv','CAUSAL_SUBTHRESHOLD.png','CAUSAL_SUBTHRESHOLD.svg']}))
