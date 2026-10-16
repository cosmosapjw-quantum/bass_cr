"""Independent continuous-source, age-marginalized ODE for E-independent opacity.

Only a manufactured verification lane. Verner opacities are energy-dependent and
must NOT use this age-marginalized ODE as a native/continuum reference.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.integrate import solve_ivp
from c21b_age_reactor import C_CM_S,BIND_EV,md14_rate_per_total_h_s,hubble,nH_total


def solve_continuous_mono(initial_state, xend, energy_birth_ev=80.,
                          sigma_const=(1e-18,3e-18,5e-18),
                          source_scale=2.,opacity_scale=1e-4):
    s=initial_state
    assert all(abs(p.energy_emitted_ev-energy_birth_ev)<1e-8 for p in s.photons)
    N0=s.number_photons();U0=s.energy_photons()
    # photon N, physical U, H0,H+,He0,He+,He++,thermal,work_gamma,work_gas,
    # 3 species events and 3 separate species photoheat eV per H.
    old=[N0,U0,*s.atoms,s.thermal_ev,0.,0.,0.,0.,0.,0.,0.,0.]
    def rhs(x,z):
        N,U=z[:2]
        hh0,hhp,he0,hep,hepp=z[2:7]
        w=z[7]
        dt_dx=1./hubble(x)
        coeff=[C_CM_S*nH_total(x)*opacity_scale*sg*dt_dx for sg in sigma_const]
        rates=[hh0*coeff[0],he0*coeff[1],hep*coeff[2]]
        sumrate=sum(rates)
        src=source_scale*md14_rate_per_total_h_s(x)*dt_dx
        ev=[N*r for r in rates]
        heating=[r*(U-N*BIND_EV[i]) for i,r in enumerate(rates)]
        return np.array([
          src-N*sumrate,
          src*energy_birth_ev-U-U*sumrate,
          -ev[0],ev[0],-ev[1],ev[1]-ev[2],ev[2],
          sum(heating)-2*w,
          U,2*w,
          *ev,*heating,
        ],dtype=float)
    r=solve_ivp(rhs,(s.x,xend),old,method='Radau',atol=2e-14,rtol=8e-12,
                max_step=(xend-s.x)/12)
    if not r.success:raise RuntimeError(r.message)
    return {'final':r.y[:,-1].tolist(),'function_evals':r.nfev,'status':r.message}
