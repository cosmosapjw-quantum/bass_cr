"""Same-author adversarial implementation checks using independent QUADPACK path."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import phys14_compete as m

def main():
  p,owner,shah,_=m.load_parent(m.ROOT/'sources/PR138_ORIGINAL_SOURCE.zip')
  _,edges,prep,params,dens=owner
  _,En,BE=m.load_nist(m.ROOT/'nist_h_2p_cross_sections.csv')
  _,Es,Ss,_=shah
  tests=[]
  for pp in prep:
    EE=np.asarray(pp['energy']);ee=EE-13.6
    for desired in (11.5,13.8,15.1,17.6,20.8):
      ix=int(np.argmin(abs(ee-desired)))
      if abs(float(ee[ix])-desired)>1.0:continue
      if pp['source']=='H' and desired>10:continue
      kh=float(pp['k'][ix]*pp['frac'][0][ix]);kt=float(pp['k'][ix]);E=float(ee[ix])
      v=float(m.velocity(np.array([E]))[0]);nu_exc=v*float(dens['HI'])*float(np.interp(E,En,BE))*m.NIST_SIGMA_UNIT if 11<=E<=21 else 0.
      nu_i=v*float(dens['HI'])*float(np.interp(E,Es,Ss))*p.SIGMA_UNIT if 14.6<=E<=21.4 else 0.
      if nu_exc+nu_i==0:continue
      d=8e9
      comp=m.second_first_event(np.array([kh]),np.array([kt]),np.array([nu_i]),np.array([nu_exc]),d)
      for channel,nu in zip(('ion','exc'),(nu_i,nu_exc)):
        fun=lambda u: kh*math.exp(-kt*u)*(nu/(nu_exc+nu_i))*(-math.expm1(-(nu_exc+nu_i)*(d-u)))
        q=quad(fun,0,d,epsabs=1e-38,epsrel=1e-12,limit=200)[0]
        vcalc=float(comp[0 if channel=='ion' else 1][0]);rel=abs(vcalc-q)/max(abs(q),1e-300)
        tests.append(dict(Ee_eV=E,channel=channel,GL24=vcalc,scipy_quad=q,relative_error=rel))
  if not tests:raise ValueError('NO_INDEPENDENT_TESTS')
  worst=max(x['relative_error'] for x in tests)
  if worst>=1e-9:raise AssertionError(f'QUAD_MISMATCH:{worst}')
  result=dict(cases=len(tests),max_relative_error=worst,details=tests,
     adversarial_findings=[
         'NIST BE-scaled data are model, not direct experiment; NIST CCC crosscheck is method contrast, not independent confidence interval',
         'Electron 1s2s, 1s3p, elastic and stopping unresolved: two-channel first-inelastic process is conditional not full electron kinetics',
         'Unknown H-impact cross section in 13.6..14.6 eV: 2p-only rate there is upper conditional scenario, not actual Lyalpha production',
         'A first 2p excitation leaves sufficient energy for second 2p only for a high-energy tail of 192 source energy atoms; NIST tabulated data do not cover resulting Ee<11 eV',
         'Radiative 2p decay may create Lyalpha photons, but escape/radiative transfer and photon feedback are not modeled',
         'All computations same model author; distinct-author R06/C09 NOT_RUN'
      ],same_author=True,independent_author_R06='NOT_RUN',independent_author_C09='NOT_RUN')
  (m.ROOT/'BLIND_REFEREE_EVIDENCE.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({'cases':len(tests),'max_relative_error':worst,'findings':len(result['adversarial_findings'])}))
if __name__=='__main__':main()
