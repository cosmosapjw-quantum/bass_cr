#!/usr/bin/env python3
"""Produce four physical figures from the saved PHYS24 source-clock/transport CSVs."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
def read(name):
 with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))
def save(name):
 plt.grid(alpha=.2);plt.tight_layout();plt.savefig(OUT/name,dpi=190);plt.close()

source=read('SOURCE_TIME_INTERVAL_INJECTION.csv')
plt.figure(figsize=(8,4.6))
for birth in ('earliest','latest'):
 d=[r for r in source if r['birth']==birth];times=[float(r['t_end_s'])/1e9 for r in d]
 vals=[float(r['delta_2p_m3'])/1e-31 for r in d]
 plt.step([0]+times,[vals[0]]+vals,where='post',label=birth)
plt.xlabel('Source observer proper time, $t$ [$10^9$ s]')
plt.ylabel(r'PHYS15 interval $\Delta N_{2p}$ [$10^{-31}$ m$^{-3}$]')
plt.title('Original PHYS15 time-binned Ly$\\alpha$ source injection')
plt.legend();save('FIG01_PHYS15_ORIGINAL_TIME_INJECTION.png')

hist=read('EINSTEIN_BIANCHI_DUST_BACKGROUND.csv')
plt.figure(figsize=(8,4.6))
for m in ('axisymmetric_dust','triaxial_dust'):
 d=[r for r in hist if r['model']==m]
 t=np.array([float(x['t_s']) for x in d])/1e9
 for i in 'xyz':
  plt.plot(t,np.array([float(x['beta_'+i]) for x in d])*1e6,label=f'{m.split("_")[0]}, $\\beta_{i}$')
plt.xlabel('Cosmic proper time $t$ [$10^9$ s]')
plt.ylabel('Bianchi anisotropy $\\beta_i(t)$ [$10^{-6}$]')
plt.title('Conditional exact Einstein-dust Bianchi-I geometry (not source-owned)')
plt.legend(ncol=2,fontsize=8);save('FIG02_EINSTEIN_DUST_BIANCHI_SHEAR_HISTORY.png')

diags=read('DIAGNOSTICS.csv')
plt.figure(figsize=(8,4.6))
for m in ('flrw_dust','axisymmetric_dust','triaxial_dust'):
 d=[r for r in diags if r['birth']=='earliest' and r['scenario']=='isotropic_RR_photon_bath' and r['Bray_upper_eV']=='35' and r['shear']==m]
 xs=['start','midpoint','end']
 vals=[next(float(r['quadrupole_P2_z']) for r in d if r['timing']==x)*1e6 for x in xs]
 plt.plot(xs,vals,'o-',label=m)
plt.ylabel('Source-normalized $\\langle P_2(\\mu)\\rangle$ [$10^{-6}$]')
plt.xlabel('Conditional within-source-bin emission clock')
plt.title('Time-resolution changes sky quadrupole without creating Q/U/V')
plt.legend();save('FIG03_SOURCE_CLOCK_BIANCHI_SKY_QUADRUPOLE.png')

spectra=read('TIME_RESOLVED_SPECTRA_FIRST_HI.csv')
plt.figure(figsize=(8,4.6))
for m in ('flrw_dust','axisymmetric_dust','triaxial_dust'):
 d=[r for r in spectra if r['birth']=='earliest' and r['scenario']=='linear_polarized_photons_kz_epsx' and r['Bray_upper_eV']=='35' and r['shear']==m and r['timing']=='midpoint' and r['ray']=='4']
 xs=[float(r['x_obs']) for r in d];free=np.array([float(r['I_free']) for r in d]);no=np.array([float(r['I_no_first_scatter']) for r in d])
 plt.semilogy(xs,free/1e-31,label=m+' free')
 plt.semilogy(xs,np.maximum(no/1e-31,1e-19),linestyle='--',label=m+' unscattered')
plt.xlabel('Observer Doppler units $x_o=(\\nu_o-\\nu_0)/\\Delta\\nu_D$')
plt.ylabel('$I_{\\nu}$ [$10^{-31}$ m$^{-3}$ sr$^{-1}$ per $x$]')
plt.title('Polarized E1 source: collisionless vs first-HI-loss spectrum')
plt.ylim(1e-18,1)
plt.legend(ncol=2,fontsize=8);save('FIG04_LYA_SPECTRA_FIRST_HI_LOSS_ONLY.png')
print('FIGURES',[(p.name,p.stat().st_size)for p in sorted(OUT.glob('FIG*.png'))])
