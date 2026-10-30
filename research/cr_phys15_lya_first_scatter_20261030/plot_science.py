#!/usr/bin/env python3
"""Native physical figures from source-locked CSV, no invented measurements."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results'; FIGS=ROOT/'figures'
def load(n):
 with (RESULTS/n).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def make():
 FIGS.mkdir(parents=True,exist_ok=True)
 lines=load('LINE_MICROPHYSICS.csv')
 xs=np.array([float(p['x_Doppler']) for p in lines]); sig=np.array([float(p['sigma_first_Lya_HI_scatter_m2']) for p in lines]);
 fig,ax=plt.subplots(figsize=(8.5,5.4));ax.semilogy(xs,sig,'o-',lw=1.3,ms=3.5)
 ax.set(xlabel=r'$x=(\nu-\nu_\alpha)/\Delta\nu_D$  at 100 K',ylabel=r'First H I resonant scatter cross section $\sigma_\alpha$ (m$^2$)',title='Source-qualified H I Lyα Voigt first scattering (static 100 K)')
 ax.grid(alpha=.23);fig.tight_layout();fig.savefig(FIGS/'PHYS15_LYA_VOIGT_CROSS_SECTION.png',dpi=180);plt.close(fig)
 atlas=load('FREQUENCY_FIRST_SCATTER_ATLAS.csv');T=1.e10
 fig,ax=plt.subplots(figsize=(8.5,5.4))
 for pol in ('earliest','midpoint','latest'):
  rows=[p for p in atlas if float(p['observation_s'])==T and p['birth_policy']==pol]
  x=np.array([float(p['x_Doppler']) for p in rows]);fraction=np.array([float(p['P_first_scatter_given_excitation']) for p in rows])
  ax.plot(x,fraction,marker='.',label=pol,lw=1.4)
 ax.set(xlabel=r'Conditional emitted photon offset $x$ (Doppler widths)',ylabel='Probability of first H I scatter before 10$^{10}$ s',title='Same-source Lyα photons: frequency-conditioned first scatter')
 ax.legend(frameon=False);ax.grid(alpha=.22);ax.set_ylim(-.02,1.03);fig.tight_layout();fig.savefig(FIGS/'PHYS15_FREQUENCY_SCATTER_PROBABILITY.png',dpi=180);plt.close(fig)
 rows=load('TIME_LYA_2P_RADIATION_LEDGER.csv')
 fig,ax=plt.subplots(figsize=(8.5,5.4))
 for pol in ('earliest','latest'):
  v=[r for r in rows if r['birth_policy']==pol];t=np.array([float(r['observation_s']) for r in v])/1.e9
  a=np.array([float(r['calculated_2p_excitations_m3']) for r in v]);b=np.array([float(r['first_scatter_line_centre_prompt_m3']) for r in v]);c=np.array([float(r['first_scatter_x10_prompt_m3']) for r in v]);
  ax.plot(t,a,marker='o',label=pol+' 2p event');ax.plot(t,b,ls='--',label=pol+' first scatter x=0');ax.plot(t,c,ls=':',label=pol+' first scatter x=10')
 ax.set(xlabel='Observation proper time (10$^9$ s)',ylabel='Conditional event number density (m$^{-3}$)',title='Frozen original H/He source: 2p → Lyα first resonance scatter')
 ax.legend(frameon=False,fontsize=8);ax.grid(alpha=.23);fig.tight_layout();fig.savefig(FIGS/'PHYS15_PROPER_TIME_FIRST_SCATTER.png',dpi=180);plt.close(fig)
 print([(p.name,p.stat().st_size) for p in sorted(FIGS.glob('*.png'))])
if __name__=='__main__':make()
