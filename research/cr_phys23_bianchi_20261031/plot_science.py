#!/usr/bin/env python3
"""PHYS23 source-conditioned Bianchi I transfer science figures."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;R=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
a=pd.read_csv(R/'BIANCHI_3D_SKY_STOKES_92160.csv');s=pd.read_csv(R/'BIANCHI_ANGULAR_LYA_SPECTRA.csv');d=pd.read_csv(R/'BIANCHI_ANGLE_NORMALIZATION_80.csv')

def save(name):
 plt.tight_layout();plt.savefig(F/name,dpi=165);plt.close()

v=a.query("scenario=='isotropic_RR_photon_bath' and upper_anchor_eV==35 and birth=='earliest'")
plt.figure(figsize=(8,4.6))
for model in ['flrw_zero','biax_plus2e-6','biax_minus2e-6','triax_3e-6']:
 q=v[v.shear==model].groupby('theta_obs_deg',as_index=False).mean(numeric_only=True)
 base=3.315890693452162e-31/(4*np.pi)
 plt.plot(q.theta_obs_deg,q.I_photons_m3_sr/base-1,label=model)
plt.xlabel(r'Observer polar angle $\theta_o$ (deg)');plt.ylabel(r'$4\pi I_o/N_{\rm source}-1$')
plt.title('Shear-only Lyα angular anisotropy from original PHYS22 source')
plt.legend(fontsize=8);save('FIG1_BIANCHI_ISOTROPIC_SOURCE_ANISOTROPY.png')

v=s.query("scenario=='isotropic_RR_photon_bath' and upper_anchor_eV==35 and birth=='earliest' and abs(theta_obs_deg-45)<1e-4 and abs(phi_obs_deg-0)<1e-4")
plt.figure(figsize=(8,4.6))
for model in ['flrw_zero','biax_plus2e-6','biax_minus2e-6','triax_3e-6']:
 q=v[v.shear==model].sort_values('x_obs')
 plt.plot(q.x_obs,q.I_photons_m3_sr_per_x/3.315890693452162e-31*4*np.pi,label=model)
plt.xlabel(r'Observer Doppler frequency $x_o$');plt.ylabel(r'Photon line profile $4\pi I(x_o)/N$')
plt.title('100 K NIST $A_{21}$ Voigt line shifted by exact Bianchi I geodesics')
plt.xlim(-6,6);plt.legend(fontsize=8);save('FIG2_BIANCHI_REDSHIFT_VOIGT_LINE.png')

v=a.query("scenario=='linear_polarized_photons_kz_epsx' and upper_anchor_eV==35 and birth=='earliest' and abs(phi_obs_deg-45)<1e-4")
plt.figure(figsize=(8,4.6))
# The grid phi = 45 is an exact member of the 48-point azimuthal sampling.
for model in ['flrw_zero','biax_plus2e-6','triax_3e-6']:
 q=v[v.shear==model].sort_values('theta_obs_deg')
 plt.plot(q.theta_obs_deg,q.UoverI,label=model)
plt.xlabel(r'Observer polar angle $\theta_o$ (deg)');plt.ylabel(r'$U/I$ in fixed transported observer screen')
plt.title('Conditional E1 linear polarization after parallel screen transport')
plt.legend(fontsize=8);save('FIG3_PHYS22_LINEAR_SOURCE_U_OVER_I_TRANSFER.png')

v=d.query("scenario=='isotropic_RR_photon_bath' and upper_anchor_eV==35 and birth=='earliest'")
plt.figure(figsize=(7.5,4.4))
plt.bar(v.shear.astype(str),v.quadrupole_I_theta_z)
plt.ylabel(r'Photon angular quadrupole $\langle P_2(n_z)\rangle$')
plt.xticks(rotation=18,ha='right');plt.title('Pure geometric quadrupole with zero Stokes $Q,U,V$')
save('FIG4_SKY_QUADRUPOLE_WITH_UNPOLARIZED_SOURCE.png')
print('FIGURES',sorted(p.name for p in F.iterdir()))