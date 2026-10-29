#!/usr/bin/env python3
"""Independent high precision direct formula (not native distinct-author audit)."""
import json
import os
from pathlib import Path
import sys
import numpy as np
import mpmath as mp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import generate as g
import rr_boundfree as old
mp.mp.dps=75
src=Path(os.environ['PR125_SOURCE_ZIP'])
params,_=old.load_verner()
_,arr,density=old.read_source(src)

# Direct Verner fitting expression separately implemented in mpmath,
# without calling old.verner_sigma/old.evaluate for independent calculation.
def mp_sigma(e, par):
    eth,emax,e0,s0,ya,P,yw,y0,y1=map(lambda x: mp.mpf(float(x)),par)
    E=mp.mpf(float(e))
    if E<eth or E>emax:return mp.mpf('0')
    x=E/e0-y0; y=mp.sqrt(x*x+y1*y1)
    return s0*mp.mpf('1e-22')*((x-1)**2+yw*yw)*y**(P/2-mp.mpf('5.5'))*(1+mp.sqrt(y/ya))**(-P)

checks=[]; maxsigma=mp.mpf('0');maxp=mp.mpf('0')
for ch in ('H','He'):
  E=arr[f'photon_{ch}_eV'];atot=np.zeros_like(E)
  ss={}
  for a in ('HI','HeI'):
    ss[a]=old.verner_sigma(E,params[a])
    atot+=ss[a]*density[a]
  for idx in (0,13,99,290,600,999,1500,2100,2799,3199):
    eng=mp.mpf(float(E[idx]))
    mp_s={a:mp_sigma(E[idx],params[a]) for a in ('HI','HeI')}
    mp_a={a:mp.mpf(float(density[a]))*mp_s[a] for a in ('HI','HeI')}
    mp_atot=sum(mp_a.values())
    for a in ('HI','HeI'):
      if mp_s[a]:maxsigma=max(maxsigma,abs(mp.mpf(float(ss[a][idx]))/mp_s[a]-1))
      for T,birth in ((mp.mpf('5e9'),mp.mpf('0')),(mp.mpf('5e9'),mp.mpf('3.75e9')),(mp.mpf('1e10'),mp.mpf('7.5e9'))):
        test=(mp_a[a]/mp_atot)*(-mp.expm1(-mp_atot*mp.mpf(299792458)*(T-birth)))
        obs=(ss[a][idx]*density[a]/atot[idx])*(-np.expm1(-atot[idx]*g.C*float(T-birth)))
        if test:maxp=max(maxp,abs(mp.mpf(float(obs))/test-1))
        checks.append((ch,int(idx),a,float(T),float(birth)))
assert maxsigma<mp.mpf('2e-13'),maxsigma
assert maxp<mp.mpf('2e-13'),maxp
report={'method':'independent mpmath 75dps direct original Verner + competing targets',
        'comparison':'represented float64 source atoms and fixed gas model',
        'controls':len(checks),'max_sigma_rel':mp.nstr(maxsigma,12),
        'max_absorption_probability_rel':mp.nstr(maxp,12),
        'status':'PASS','distinct_author_review':False}
(HERE/'results'/'INDEPENDENT_MP75.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
