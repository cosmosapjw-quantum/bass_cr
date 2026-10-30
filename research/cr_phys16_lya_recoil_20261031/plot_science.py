#!/usr/bin/env python3
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)

def read(n):
 with (ROOT/'results'/n).open() as f:return list(csv.DictReader(f))

F=read('SOURCE_EMISSION_FREQUENCY_ATLAS.csv')
fig,ax=plt.subplots(figsize=(9.0,5.2))
for model in ['BORN_DIPOLE','ISOTROPIC_IMPACT_DIPOLE','BORN_ISOTROPIC_EMISSION']:
 rr=[r for r in F if r['birth_policy']=='earliest' and r['angular_model']==model]
 x=np.array([float(r['x_Doppler']) for r in rr]);y=np.array([float(r['source_emission_normalized_pdf_per_Doppler']) for r in rr])
 ax.plot(x,y,label=model.replace('_',' ').title())
ax.set_xlim(-6,6);ax.set_xlabel(r'Emission offset $x=(\nu-\nu_0)/\Delta\nu_D$');ax.set_ylabel('Conditional source PDF per Doppler width')
ax.set_title('Source-owned 2p events: three angular closures (100 K)')
ax.legend(fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'PHYS16_SOURCE_EMISSION_SPECTRUM.png',dpi=160);plt.close(fig)

R=read('TIME_ORDERED_MODEL_FIRST_SCATTER_SPECTRA.csv')
fig,ax=plt.subplots(figsize=(9.,5.2))
for model in ['BORN_DIPOLE','ISOTROPIC_IMPACT_DIPOLE','BORN_ISOTROPIC_EMISSION']:
 rr=[r for r in R if r['policy']=='earliest' and r['model']==model]
 x=np.array([float(r['x_Doppler']) for r in rr]);y=np.array([float(r['source_qualified_first_scatter_spectral_density_per_x_m3'])/1e-31 for r in rr])
 ax.plot(x,y,label=model.replace('_',' ').title())
ax.set_xlim(-6,6);ax.set_xlabel(r'First-scattered source-photon offset $x$');ax.set_ylabel(r'$dN_{1}/dx$ ($10^{-31}$ m$^{-3}$ Doppler$^{-1}$)')
ax.set_title(r'Time-ordered first HI resonance scatter, $T=10^{10}$ s')
ax.legend(fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'PHYS16_TIME_ORDERED_FIRST_SCATTER.png',dpi=160);plt.close(fig)

K=read('ONE_SCATTER_REDIS_KERNEL_ATLAS.csv')
fig,ax=plt.subplots(figsize=(9.,5.2))
for xin in [-3.,0.,3.]:
 rr=[r for r in K if float(r['xin_Doppler'])==xin]
 xo=[float(r['xout_Doppler']) for r in rr];dd=[float(r['kernel_density_per_Doppler']) for r in rr]
 ax.plot(xo,dd,label=f'$x_{{in}}={xin:g}$')
ax.set_xlim(-9,9);ax.set_xlabel(r'Outgoing frequency offset $x_{out}$');ax.set_ylabel('Single-scatter probability density per Doppler width')
ax.set_title('Absorption-selected, recoil-aware, static-HI redistribution model')
ax.legend();ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'PHYS16_ONE_SCATTER_REDIS_KERNEL.png',dpi=160);plt.close(fig)
print('FIGURES',[(p.name,p.stat().st_size) for p in OUT.glob('*.png')])
