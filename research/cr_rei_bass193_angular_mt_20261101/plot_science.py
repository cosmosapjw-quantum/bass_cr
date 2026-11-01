#!/usr/bin/env python3
"""Plot source-conditioned moments, not an admitted ion-neutral dynamical prediction."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'BASS193_CX_ANGULAR_MOMENT_V1'
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parent
R=list(csv.DictReader((BASE/'results/BASS193_CX_A7_LINEAR_DRAG_192.csv').open()))
def v(col):return np.array([float(r[col]) for r in R])
z=v('z_low')
x=v('T_saved_K')
fig,ax=plt.subplots(figsize=(7.8,4.8))
ax.scatter(x,v('k_mt_A7_over_piA4'),s=15,marker='o',alpha=0.8)
ax.set(xlabel='Saved BASS193 T (K)',ylabel='Linear drag K(A7) / K(pi, A4)',
       title='Resonant CX: published angular fit versus pi-deflection limit')
ax.grid(alpha=0.2)
fig.tight_layout()
for ext in ('png','svg'):fig.savefig(BASE/'figures'/f'CX_ANGULAR_DRAG_CORRECTION.{ext}',dpi=180,metadata={'Date':'2026-11-01T00:00:00'})
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.8,4.8))
ax.semilogy(z,v('nu_rel_over_H_effective'),lw=1.7,label=r'Frozen-end $\nu_\mathrm{rel}/H_\mathrm{eff}$')
ax.set(xlabel='Source z (decreasing along time)',ylabel=r'Source-conditional $\nu_\mathrm{rel}/H_\mathrm{eff}$',
       title='Linear-response ion-neutral coupling (no Bianchi tilt, no evolved IVP)')
ax.invert_xaxis()
ax.grid(alpha=0.2)
fig.tight_layout()
for ext in ('png','svg'):fig.savefig(BASE/'figures'/f'BASS193_CX_LINEAR_DRAG_OVER_H.{ext}',dpi=180,metadata={'Date':'2026-11-01T00:00:00'})
plt.close(fig)
# Make generated SVG git-whitespace clean and deterministic (the science geometry is unchanged).
for f in sorted((BASE/'figures').glob('*.svg')):
    f.write_bytes(b'\n'.join(line.rstrip() for line in f.read_bytes().splitlines())+b'\n')
print('PLOTS',len(list((BASE/'figures').iterdir())))
