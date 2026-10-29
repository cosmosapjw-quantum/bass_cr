#!/usr/bin/env python3
"""Numerical/observable audit of actual PR125 atomwise physical data."""
from pathlib import Path
from rr_boundfree import read_source,load_verner,verner_sigma,evaluate,HI,HEI,EV_J
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).parent
_,atoms,density=read_source(root/'BASS_CR_PHYS02_RR_IONIZING_PHOTON_SOURCE_20261029.zip')
param,_=load_verner()
result,rows,samples,full=evaluate(atoms,density,param)
ind=json.loads((root/'results/INDEPENDENT_MPMATH65.json').read_text())
maxsig=maxnr=0.
for control in ind['controls']:
 ch=control['channel'];j=control['time_bin']-1;i=control['atom_index'];a=control['target']
 E=atoms[f'photon_{ch}_eV'][i];w=atoms[f'capture_{ch}_bins_m3'][j]
 ss=verner_sigma([E],param[a])[0]
 nlo=full[f'abs_{ch}_{a}_bin{j+1}_lo_m3'][i]
 nhi=full[f'abs_{ch}_{a}_bin{j+1}_hi_m3'][i]
 if ss and control['sigma_m2']:
  maxsig=max(maxsig,abs(ss-control['sigma_m2'])/control['sigma_m2'])
 for v,r in [(nlo,control['count_lower_m3']),(nhi,control['count_upper_m3'])]:
  if r>0:maxnr=max(maxnr,abs(v-r)/r)
  else:assert v==0.
assert maxsig<1e-12 and maxnr<1e-12,(maxsig,maxnr)
# Source atom-level consistency: target partitions, total photon energy, source occupancy.
source_counts={ch:float(atoms[f'capture_{ch}_bins_m3'].sum()) for ch in ('H','He')}
assert abs(sum(source_counts.values())-result['source_photons_m3'])<1e-12*result['source_photons_m3']
# Endpoint availability is not deposited heat, and no negative photoelectron excess.
assert all(row['photoelectron_excess_avail_lower_J_m3']>=0 for row in rows)
# Counts: per channel/target endpoint range
matrix={}
for ch in ('H','He'):
 for tar in ('HI','HeI'):
  matrix[f'{ch}_to_{tar}']={v:float(result['channels'][ch][tar][v]) for v in ('lo','hi')}
metrics={'independent_mpmath65_controls':len(ind['controls']), 'max_rel_sigma_deviation':maxsig,
         'max_rel_probability_oracle_deviation':maxnr,
         'source_counts_m3':source_counts,'total_absorb_lower_m3':result['absorbed_lower_m3'],
         'total_absorb_upper_m3':result['absorbed_upper_m3'],
         'total_fraction_bounds':[result['absorption_fraction_lower'],result['absorption_fraction_upper']],
         'target_matrix':matrix,'source_restoration':'original_sha256+CRC+PR110_nested_SHA_PASS',
         'scientific_status':'CONDITIONAL_BALLISTIC_HOMOGENEOUS_FIRST_ABSORPTION_ONLY'}
(root/'results/VALIDATION.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n')

fig,ax=plt.subplots(figsize=(7.2,4.5),dpi=160)
Es=np.linspace(13.5,35.,600)
for target in ('HI','HeI'):
 alpha=density[target]*verner_sigma(Es,param[target])
 ax.plot(Es,alpha,label=f'{target} opacity (m⁻¹)')
ax.axvline(13.6,ls=':',lw=.8,color='gray');ax.axvline(24.59,ls='--',lw=.8,color='gray')
ax.set(xlabel='Photon energy (eV)',ylabel='Absorption coefficient α(E) (m⁻¹)',title='Verner 1996 fit × frozen H I / He I number density')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(root/'results/OPACITY_ENERGY.png');plt.close(fig)

# Distinguish source H/He time bins and bound; 2 real source channels, no model-fitted midpoint.
fig,ax=plt.subplots(figsize=(7.2,4.5),dpi=160)
for ch in ('H','He'):
    vals=[]
    for j in range(1,5):
        rr=[r for r in rows if r['source_channel']==ch and r['time_bin']==j]
        nsrc=rr[0]['photons_emitted_m3']
        lo=sum(r['absorbed_lower_m3'] for r in rr)/nsrc
        hi=sum(r['absorbed_upper_m3'] for r in rr)/nsrc
        vals.append((lo,hi))
    xx=np.arange(1,5)
    ax.plot(xx,[x[0] for x in vals],marker='o',label=f'{ch} lower')
    ax.plot(xx,[x[1] for x in vals],marker='x',linestyle='--',label=f'{ch} upper')
ax.set(xlabel='Original proper-time bin',ylabel='First absorption fraction by final epoch',
       title='Conditional endpoint bounds; no within-bin emission times assumed',xticks=[1,2,3,4])
ax.set_ylim(bottom=0);ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(root/'results/ABSORPTION_ENVELOPE.png');plt.close(fig)
print(json.dumps(metrics,indent=2))
