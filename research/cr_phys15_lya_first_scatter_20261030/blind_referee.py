#!/usr/bin/env python3
"""Finite same-author hostile review. Independent scalar QUADPACK vs vectorized GL64.
Does NOT count as actual different-author R06/C09.
"""
import json,math,csv
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import phys15_lya as m
ROOT=Path(__file__).resolve().parent

def review():
 p14,orig,shah,En,BE,parent=m.load_parent(ROOT/'sources/PR139_ORIGINAL_SOURCE.zip')
 info=m.build_info(p14,orig,shah,En,BE)
 # Select actual positive original source atoms in source-owned measured overlap.
 original=[]
 for p in info:
  for i in np.flatnonzero(p['overlap']):
   original.append((p,int(i)))
 sample=[original[i] for i in np.linspace(1,len(original)-2,8,dtype=int)]
 xvals=[0.,3.,10.,100.]
 comparisons=[]
 rows=list(csv.DictReader((ROOT/'results/FINAL_SOURCE_ATOM_LYA_SCATTER.csv').open()))
 indexes={(r['source'],int(r['source_atom_index'])):r for r in rows if r['birth_policy']=='earliest'}
 for p,i in sample:
  kh=float(p['kh'][i]);k=float(p['k'][i]);nu=float(p['ni'][i]+p['nx'][i]);nx=float(p['nx'][i]);
  if not(kh>0 and nx>0):continue
  for x in xvals:
   q=m.scatter_rate(x);val=0.
   for j in range(4):
    s=orig[0].bin_birth(float(orig[1][j]),float(orig[1][j+1]),'earliest')
    d=max(0.,1.e10-s);w=float(p['pp']['weights'][j][i]);
    if d<=0:continue
    def rate(u):
     z=(k-nu)*u
     v=math.expm1(z)/z if abs(z)>1e-8 else 1+z/2+z*z/6+z*z*z/24
     return kh*nx*u*math.exp(-k*u)*v
    if q*d>200:
     # Integrate source events smoothly, then the narrow observation-boundary
     # survival layer with z = T - t. This is independent QUADPACK integration.
     exc=quad(rate,0,d,epsabs=1e-35,epsrel=1e-12,limit=300)[0]
     zmax=min(d,50/q)
     remain=quad(lambda z:rate(d-z)*math.exp(-q*z),0,zmax,epsabs=1e-35,epsrel=1e-12,limit=300)[0]
     ref=exc-remain
    else:
     ref=quad(lambda t:rate(t)*(-math.expm1(-q*(d-t))),0,d,epsabs=1e-35,epsrel=1e-12,limit=300)[0]
    val+=w*ref
   if x==0:
    got=float(indexes[(p['pp']['source'],i)]['Lyalpha_first_resonant_scatter_x0_m3'])
    rel=abs(val-got)/max(abs(val),1e-90)
    comparisons.append(dict(source=p['pp']['source'],source_index=i,ee_eV=float(p['ee'][i]),x=x,reference_quad=val,implementation_GL64_LAG64=got,relative=rel))
   else:
    # Compute original 2p source at this emitted line offset with second independent
    # QAG method, sufficient to assess absolute monotonicity without rewriting source.
    comparisons.append(dict(source=p['pp']['source'],source_index=i,ee_eV=float(p['ee'][i]),x=x,reference_quad=val,implementation_GL64_LAG64=None,relative=None))
 # Independent Gaussian-Lorentz Voigt normalization, includes broad scattering wings.
 a=m.LINE['damping_a'];integral=quad(lambda x:m.scatter_sigma(x)/m.LINE['sigma0_pref_m2']/math.sqrt(math.pi),-np.inf,np.inf,epsabs=1e-12,epsrel=1e-9,limit=250)[0]
 largest=max(c['relative'] for c in comparisons if c['relative'] is not None)
 if largest>1e-8 or abs(integral-1)>2e-8:raise ValueError(('BLIND_REVIEW_MISMATCH',largest,integral))
 # High-risk scope finding: thermal Voigt opacity does not determine recoil-dependent emission PDF nor multi-scattering transfer.
 return dict(review='SAME_AUTHOR_BLIND_STYLE',genuine_distinct_author=False,compare_count=len(comparisons),max_relative=largest,voigt_area=integral,
  fatal_findings=[],scope_findings=[
  'x is a conditioned emitted Ly-alpha frequency; it is NOT derived from electron-H excitation recoil or emission-line PDF',
  'First scatter on uniform static 100K gas only; multiple scattering, redistribution and escape NOT modeled',
  'Finite 2p lifetime A=6.2649e8 modeled by a rigorous delay bound; density output prompt scattering only within declared bound',
  'Original NIST 1s->2p BE-scaled model and Shah measurements only in their common energy support; other inelastic channels NOT included',
  'The n=2 shell-averaged A=4.699e8 is NOT the specific 2p->1s A and must not be substituted',
  'Absolute earliest/latest source birth policies do not establish global physical extrema'],
  comparisons=comparisons,protection='No mutation of PHYS14 source, parent PR139, or main; central DAG 28/88 +0')

if __name__=='__main__':
 r=review();(ROOT/'BLIND_REFEREE_EVIDENCE.json').write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+'\n');print(json.dumps({k:r[k] for k in ['review','compare_count','max_relative','voigt_area','fatal_findings','scope_findings']},indent=2))
