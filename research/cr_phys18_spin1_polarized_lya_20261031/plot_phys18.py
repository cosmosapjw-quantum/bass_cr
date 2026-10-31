from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent;D=R/'results';P=R/'figures';P.mkdir(exist_ok=True)
e=pd.read_csv(D/'SOURCE_2P_ALIGNMENT_MOMENTS.csv')
a=pd.read_csv(D/'SOURCE_DIRECTIONAL_STOKES_ATLAS.csv');s=pd.read_csv(D/'SOURCE_DIRECTIONAL_STOKES_FREQUENCY_ATLAS.csv')
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':10,'figure.dpi':135})
fig,ax=plt.subplots(figsize=(8.2,4.9));ax.plot(e.Ee_eV,e.q_quadrupole_A2,lw=2,label=r'$A_2=\langle P_2(\hat q \cdot \hat k_e)\rangle$');ax.set_xlabel('Original source photoelectron energy (eV)');ax.set_ylabel('KFB-1976 UBorn 2p recoil-axis quadrupole');ax.set_title('Actual 2,066 source-owned e–H(1s→2p) events');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(P/'PHYS18_SOURCE_QUADRUPOLE.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.2,5));p=a[a.birth_policy=='earliest'];
for xi in [-.5,0.,.5,1.]:
 d=p[p.xi_alignment==xi];ax.plot(d.observer_theta_deg,d.linear_polarization_QoverI,marker='.',label=rf'$\xi={xi:g}$')
ax.axhline(0,lw=.6,color='grey');ax.set_xlabel('Observer polar angle to fixed incident electron axis (deg)');ax.set_ylabel('Source-weighted Stokes Q/I');ax.set_title('Conditional Lyα polarization: PSD 2p density-matrix family');ax.grid(alpha=.2);ax.legend(ncol=2);fig.tight_layout();fig.savefig(P/'PHYS18_SOURCE_POLARIZATION_QOVERI.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.2,5));p=a[(a.birth_policy=='earliest')];
for xi in [-.5,0.,1.]:
 d=p[p.xi_alignment==xi];ref=3.3158906934521573e-31/(4*np.pi);ax.plot(d.observer_theta_deg,d.dN_dOmega_m3_sr/ref,marker='.',label=rf'$\xi={xi:g}$')
ax.set_xlabel('Observer polar angle (deg)');ax.set_ylabel(r'$[dN_I/d\Omega] / [N_{2p}/4\pi]$');ax.set_title('Directional Lyα source intensity, number conserved');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(P/'PHYS18_SOURCE_ANGULAR_INTENSITY.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.2,5));p=s[(s.birth_policy=='earliest')&(s.xi_alignment==1.)];N=3.3158906934521573e-31/(4*np.pi)
for t in [0.,90.,180.]:
 d=p[p.observer_theta_deg==t];ax.plot(d.x_Doppler,d.d2N_dOmega_dx_m3_sr/N,label=rf'$I$, $\theta={t:g}^\circ$')
d=p[p.observer_theta_deg==90];ax.plot(d.x_Doppler,d.d2Q_dOmega_dx_m3_sr/N,ls='--',label=r'$Q$, $\theta=90^\circ$')
ax.set_xlim(-4,4);ax.set_xlabel(r'$x=(\nu-\nu_0)/\Delta\nu_D$');ax.set_ylabel(r'Stokes source per Doppler width / $(N_{2p}/4\pi)$');ax.set_title(r'100 K polarized Lyα directional spectrum, KFB 2p and $\xi=1$');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(P/'PHYS18_DIRECTIONAL_STOKES_SPECTRA.png',dpi=160);plt.close(fig)
print('SCIENCE_FIGURES',[(x.name,x.stat().st_size) for x in P.glob('*.png')])
