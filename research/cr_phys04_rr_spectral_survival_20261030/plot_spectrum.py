#!/usr/bin/env python3
"""Plot physically source-derived final-time conditional photon spectrum."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'results'/'SURVIVING_PHOTON_ENERGY.csv').open(encoding='utf-8')))
fig,ax=plt.subplots(figsize=(9,5))
for ch in ('H','He'):
    sub=[r for r in rows if float(r['T_s'])==1e10 and r['source']==ch]
    x=[(float(r['Elo_eV'])+float(r['Ehi_eV']))/2 for r in sub]
    lo=[float(r['survive_lo_m3']) for r in sub]
    hi=[float(r['survive_hi_m3']) for r in sub]
    line=ax.plot(x,hi,label=f'{ch} photons: survivor upper')[0]
    ax.fill_between(x,lo,hi,alpha=0.2,color=line.get_color())
ax.set(xlabel='Photon energy at emission (eV)',ylabel='Surviving photon count per 1 eV bin (m$^{-3}$)',title='Frozen 100 K H/He: source-locked survived photon spectrum at $T=10^{10}$ s')
ax.legend();ax.grid(alpha=.2)
fig.tight_layout()
fig.savefig(ROOT/'results'/'SURVIVING_PHOTON_SPECTRUM.png',dpi=160)
plt.close(fig)