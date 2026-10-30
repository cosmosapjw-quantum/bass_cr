#!/usr/bin/env python3
"""MP70 independent expression: direct age-integral competing-risk derivative.
Not another independent *author*. Runs on actual source atoms, not synthetic inputs.
"""
import json,math,argparse
from pathlib import Path
import mpmath as mp
import numpy as np
import neutral_response as N
mp.mp.dps=70
p=Path(__file__).resolve().parent
ed,prep,params,dens,prev=N.original_source()
max_abs=mp.mpf('0'); max_rel=mp.mpf('0'); checked=0
for pp in prep:
 for idx in [0,100,319,750,1210,1750,2280,3199]:
  a=mp.mpf(str(float(pp['k'][idx]*pp['frac'][0,idx])))
  b=mp.mpf(str(float(pp['k'][idx]*pp['frac'][1,idx])))
  af=float(a);bf=float(b)
  for s,T,u,v in [(0.,1e10,1.25e9,3.75e9),(2.5e9,7.5e9,3.75e9,6.25e9),(5e9,1e10,2.5e9,5e9),(7.5e9,1e10,8.75e9,1e10)]:
   lo=max(s,u);hi=min(T,v)
   for target,par in [(0,0),(0,1),(1,0),(1,1)]:
    ka=(a,b)[target];kb=(a,b)[par];k=a+b
    if hi<=lo or s>=T or k==0:truth=mp.mpf('0')
    else:
     # Distinct evaluation by the Volterra response, integrated in event time.
     term1=(kb*mp.quad(lambda age:mp.exp(-k*(age-mp.mpf(s))),[mp.mpf(lo),mp.mpf(hi)])) if target==par else mp.mpf('0')
     term2=ka*kb*mp.quad(lambda event:mp.exp(-k*(event-mp.mpf(s)))*max(mp.mpf('0'),min(event,mp.mpf(hi))-mp.mpf(lo)),[mp.mpf(lo),mp.mpf(hi),mp.mpf(T)])
     truth=term1-term2
    obs=mp.mpf(str(float(N.log_response(np.array([af]),np.array([bf]),s,T,u,v,target,par)[0])))
    err=abs(truth-obs);max_abs=max(max_abs,err)
    if truth: max_rel=max(max_rel,err/max(abs(truth),mp.mpf('1e-40')))
    checked+=1
r={'unit':'CR_PHYS09_FROZEN_NEUTRAL_CAUSAL_SUSCEPTIBILITY_V1','same_author_independent_formula':True,'precision_dps':mp.mp.dps,'actual_original_atom_pair_cases':len(prep)*8*4,'scalar_checks':checked,'max_abs_error':str(max_abs),'max_relative_error':str(max_rel),'verdict':'PASS' if max_rel<mp.mpf('5e-12') else 'FAIL'}
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=p/'results'/'MP70.json');args=ap.parse_args()
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps(r,indent=2))
if r['verdict']!='PASS':raise SystemExit(1)
