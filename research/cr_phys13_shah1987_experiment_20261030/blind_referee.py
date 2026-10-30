"""Bounded same-author adversarial verification. Never label distinct-author R6/C9."""
from __future__ import annotations
from pathlib import Path
import json,math,csv
import numpy as np
from scipy.integrate import quad
import phys13_shah as P
ROOT=Path(__file__).resolve().parent

def check():
    mod,(owner,edges,prep,params,dens)=P.load_original(ROOT/'sources/PR137_ORIGINAL_SOURCE.zip')
    table,meas,ss,err=P.load_shah(ROOT/'data_shah1987.csv')
    # Independent direct time integral with adaptive scipy.quad, not GL24.
    tested=[]
    for pp in prep:
      energy=np.asarray(pp['energy'],float)-13.60
      mask=np.where((energy>=14.6)&(energy<=20.99))[0]
      if not len(mask):continue
      for idx in (int(mask[0]),int(mask[len(mask)//2]),int(mask[-1])):
        ee=float(energy[idx]);sig=np.interp(ee,meas,ss)*1e-21
        nu=dens['HI']*sig*math.sqrt(2*ee*P.EV_J/P.ME)
        kH=float(pp['k'][idx]*pp['frac'][0][idx]);ka=float(pp['k'][idx]);dt=7.5e9
        value=float(P.second_p(np.array([kH]),np.array([ka]),np.array([nu]),dt)[0])
        direct=quad(lambda u:kH*math.exp(-ka*u)*(-math.expm1(-nu*(dt-u))),0,dt,epsabs=1e-15*max(value,1e-20),epsrel=1e-12)[0]
        tested.append(dict(energy_eV=ee,source=pp['source'],gauss=value,quad=direct,
                           relative=abs(value-direct)/max(abs(direct),1e-300)))
    # Source point measurement reconciliation and common normalization epistemics.
    o=json.loads((ROOT/'results/RESULT.json').read_text())
    problem=[]
    if any(z['relative']>1e-9 for z in tested): problem.append('GL24_QUAD_MISMATCH')
    if abs(o['final']['earliest']['first_total_m3']/1.719391366604854e-26-1)>1e-12:problem.append('PARENT_COUNT_MISMATCH')
    if not 0<o['final']['earliest']['Shah_measured_fraction_of_kinematic_cap']<1: problem.append('EXPERIMENT_COVERAGE_RECLASSIFY')
    verdict='PASS_SCOPED_CONDITIONAL' if not problem else 'CONCERN'
    res={'verdict':verdict,'direct_quad_cases':len(tested),'max_relative':max([x['relative'] for x in tested],default=0.),'samples':tested,
      'material_findings':problem,
      'limitations':['68percent normalization is one correlated source, not independent per knot',
                     'printed individual errors are 67% level not simultaneous hard interval',
                     '14.6 eV below is unmeasured rather than physically zero',
                     'measured knots only; interpolation is a model and original photon electron kinematic mapping remains frozen',
                     'no stopping/100K thermal relative-speed/transport, not actual collision rate or physical K',
                     'same author independent arithmetic, R06/C09 DISTINCT AUTHOR NOT_RUN']}
    (ROOT/'BLIND_REFEREE_EVIDENCE.json').write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps({'verdict':verdict,'cases':len(tested),'maxrel':res['max_relative'],'issues':problem}))
    if problem:raise SystemExit(1)
if __name__=='__main__':check()
