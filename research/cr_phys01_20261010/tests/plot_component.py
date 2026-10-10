"""Reproduce the conditional energy-partition figure (not a history plot)."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from provider import convolve_secondary
from fs10 import FS10Table,IONIZATION_EV
import rudd
K=np.geomspace(1e6,4e6,120);table=FS10Table();ratio=.248/(4*(1-.248))
loss=np.zeros_like(K);v=np.zeros((len(K),9));primary=np.zeros_like(K)
for target,n in [('H',1),('He',ratio)]:
    m=rudd.cross_section_moments(K,target);loss+=n*m['loss_eV_m2']
    primary+=n*m['binding_eV_m2'];v+=n*convolve_secondary(K,target,table)
curves=[(v[:,0]/loss,'Heat','#c65a29'),((primary+v[:,5:8]@IONIZATION_EV)/loss,'Primary + secondary ionization','#2464a1'),(v[:,2]/loss,'Excitation radiation','#36815f')]
fig,ax=plt.subplots(figsize=(7.2,5.4));fig.subplots_adjust(bottom=.24,left=.12,right=.98,top=.91)
for y,label,color in curves:ax.plot(K/1e6,y,label=label,color=color,lw=2)
ax.set(xlabel='Proton kinetic energy (MeV)',ylabel='Fraction of modelled ionization-loss power',ylim=(0,.65),xlim=(1,4),title='CR proton → H/He terminal deposition')
ax.legend(frameon=False);ax.grid(alpha=.2)
fig.text(.5,.055,'Conditional Rudd + FS10 model; xHII = xHeII = 0.01, T = 100 K.\nNominal YHe = 0.248; ionization channel only.\nQuasistatic terminal yields, not an EoR history.',ha='center',fontsize=9)
for ext in ['png','pdf']:fig.savefig(ROOT/'evidence'/('CR_DEPOSITION_COMPONENT.'+ext),dpi=180)
np.savetxt(ROOT/'evidence'/'CR_DEPOSITION_COMPONENT.csv',np.column_stack([K,*[x[0] for x in curves]]),delimiter=',',header='Kproton_eV,heat_fraction,ionization_fraction,excitation_fraction',comments='')
