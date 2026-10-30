#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)

def rows(name):
 with (ROOT/'results'/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

w=rows('WILLIAMS_MEASURED_N2_VS_KFB_UB_N2.csv')
fig,ax=plt.subplots(figsize=(8.4,5.3))
for en,mark in [(13.87,'o'),(16.46,'s'),(19.58,'^')]:
 d=[r for r in w if float(r['energy_eV'])==en];t=np.array([float(r['angle_deg']) for r in d]);obs=np.array([float(r['measured_N2_DCS_a0_sq_sr']) for r in d]);err=np.array([float(r['measured_uncertainty_a0_sq_sr']) for r in d]);model=np.array([float(r['KFB_UB_N2_sum_model_DCS_a0_sq_sr']) for r in d])
 aa=ax.errorbar(t,obs,yerr=err,fmt=mark,ms=3.3,linewidth=.9,capsize=2,label=f'Williams n=2 measured, {en:.2f} eV')
 ax.plot(t,model,linestyle='--',linewidth=1.4,color=aa[0].get_color(),label=f'KFB UBorn (2s+2p), {en:.2f} eV')
ax.set_yscale('log');ax.set_xlim(10,155);ax.set_xlabel('Electron scattering angle (degrees)');ax.set_ylabel(r'Differential cross section ($a_0^2\,\mathrm{sr}^{-1}$)');ax.set_title('Primary experimental n=2 vs predicted UBorn 2s+2p');ax.legend(fontsize=7,ncol=2);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'PHYS17_WILLIAMS_N2_VS_KFB_UB.png',dpi=160);plt.close(fig)

s=rows('SOURCE_UB2P_EMISSION_SPECTRA.csv');fig,ax=plt.subplots(figsize=(8.1,5.0))
for model in ('KFB_UB2P_E1','KFB_UB2P_ISOTROPIC_EMISSION','PWBA_E1_PARENT'):
 d=[r for r in s if r['policy']=='earliest' and r['model']==model];x=np.array([float(r['x_Doppler']) for r in d]);p=np.array([float(r['source_weighted_emission_pdf']) for r in d]);ax.plot(x,p,label=model.replace('_',' '))
ax.set_xlim(-5,5);ax.set_xlabel(r'Ly$\alpha$ frequency offset $x$ (Doppler widths)');ax.set_ylabel('Source-weighted conditional PDF per Doppler width');ax.set_title('Original 2,066 emitter events: primary-table angular model');ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'PHYS17_SOURCE_EMISSION_UB2P.png',dpi=160);plt.close(fig)

s=rows('TIME_ORDERED_MODEL_FIRST_SCATTER_SPECTRA.csv');fig,ax=plt.subplots(figsize=(8.1,5.0))
for model in ('KFB_UB2P_E1','KFB_UB2P_ISOTROPIC_EMISSION','PWBA_E1_PARENT'):
 d=[r for r in s if r['policy']=='earliest' and r['model']==model];x=np.array([float(r['x_Doppler']) for r in d]);n=np.array([float(r['source_qualified_first_scatter_spectral_density_per_x_m3']) for r in d])/1e-31;ax.plot(x,n,label=model.replace('_',' '))
ax.set_xlim(-5,5);ax.set_xlabel(r'First-scatter source photon $x$ (Doppler widths)');ax.set_ylabel(r'$dN_1/dx$ ($10^{-31}\,\mathrm{m}^{-3}$)');ax.set_title(r'Time-ordered, original H I first scatter: $T=10^{10}$ s');ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'PHYS17_FIRST_SCATTER_UB2P.png',dpi=160);plt.close(fig)
print('FIGURES', [(p.name,p.stat().st_size) for p in sorted(OUT.glob('*.png'))])
