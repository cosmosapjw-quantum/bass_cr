#!/usr/bin/env python3
"""Scientific plots for immutable BASS-CR PHYS14 results. No source mutation."""
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def load(path):
    with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def draw():
    R=ROOT/'results'; F=ROOT/'figures';F.mkdir(exist_ok=True)
    atom=load(R/'SOURCE_ATOM_NIST_SHAH_CROSSWALK.csv')
    vals=load(R/'TIME_TOTAL_COMPETITION.csv')
    ccc=load(R/'NIST_BE_VS_CCC_CROSSCHECK.csv')
    ee,si,sp=[],[],[]
    for x in atom:
        if x['Shah_H_impact_measured']=='1' and x['NIST_2p_table_covered']=='1' and x['source']=='He':
            ee.append(float(x['first_H_photoelectron_eV']))
            si.append(float(x['sigma_Shah_ion_m2']))
            sp.append(float(x['sigma_NIST_BE_2p_m2']))
    sort=np.argsort(ee);ee=np.array(ee)[sort];si=np.array(si)[sort];sp=np.array(sp)[sort]
    fig,ax=plt.subplots(figsize=(9,5.2))
    ax.plot(ee,si/1e-21,label='Shah 1987 H ionization (measured-knot interpolation)')
    ax.plot(ee,sp/1e-21,label='NIST/Stone 2002 1s→2p (BE-scaled model)')
    ax.scatter([float(x['Ee_eV']) for x in ccc],[float(x['sigma_CCC_m2'])/1e-21 for x in ccc],s=25,label='NIST CCC comparison knots')
    ax.set_xlabel('Initial photoelectron kinetic energy (eV)')
    ax.set_ylabel('Electron-impact cross section (10⁻²¹ m²)')
    ax.set_title('Original RR electron: H ionization versus H 1s→2p excitation')
    ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(F/'PHYS14_CROSS_SECTIONS.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.2))
    for policy in ('earliest','latest'):
        rows=[x for x in vals if x['birth_policy']==policy]
        t=[float(x['observation_s'])/1e9 for x in rows]
        ax.plot(t,[float(x['H_ion_first_inelastic_measured_overlap_m3'])/1e-31 for x in rows],marker='o',label=policy+' H second ion')
        ax.plot(t,[float(x['H_2p_first_inelastic_measured_overlap_m3'])/1e-31 for x in rows],marker='s',label=policy+' H 2p excitation')
    ax.set_title('Causal first-inelastic channels after original H photoabsorption')
    ax.set_xlabel('Observer proper time (10⁹ s)')
    ax.set_ylabel('Source-conditioned channel count (10⁻³¹ m⁻³)')
    ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(F/'PHYS14_CAUSAL_COMPETITION.png',dpi=170);plt.close(fig)
    print('WROTE 2 SCIENTIFIC FIGURES')
if __name__=='__main__':draw()
