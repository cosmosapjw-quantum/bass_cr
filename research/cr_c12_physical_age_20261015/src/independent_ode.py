"""Independent solve_ivp/DOP853 reference for the same local photon reservoir ODE.

Not a physical reionization-history calculation. Unlike the exponential
staged stepper, this integrates all photon packet occupancies and ion fractions
simultaneously with adaptive Runge-Kutta stages.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from physical_age import Gas,K_B_EV_PER_K,C_CM_PER_S
from owner_age_bridge import EmissionPackets


def solve_reference(ns:dict,p:EmissionPackets,initial:Gas,t_end:float,
                    rtol:float=5e-11,atol:float=5e-13) -> dict:
    nH=ns["model"].nh*5.**3
    nHe=ns["nhe"]
    yhe=nHe/nH
    n=len(p.flux)
    initial_thermal=initial.thermal_energy_ev_per_h(yhe)
    init=np.r_[p.flux,[initial.xhi,initial.xhei,initial.xheii,
                       initial.xheiii,initial_thermal]]
    def rhs(t,z):
        photons=z[:n]
        xhi,xhei,xheii,xheiii,thermal=z[n:]
        gas=np.array([nH*xhi,nHe*xhei,nHe*xheii])
        rates=C_CM_PER_S*p.sigma_cm2*gas
        reaction=np.sum(photons[:,None]*rates,axis=0)
        heats=np.sum(photons[:,None]*rates *
                     (p.physical_eV[:,None]-p.bind_eV),axis=0)
        dphotons=-photons*np.sum(rates,axis=1)
        return np.r_[dphotons,[-reaction[0],-reaction[1]/yhe,
                 (reaction[1]-reaction[2])/yhe,reaction[2]/yhe,
                 float(np.sum(heats))]]
    res=solve_ivp(rhs,(0,t_end),init,method="DOP853",
                   atol=atol,rtol=rtol)
    if not res.success:
        raise RuntimeError(res.message)
    z=res.y[:,-1]
    g=Gas(float(z[n]),float(z[n+1]),float(z[n+2]),float(z[n+3]),1.)
    g.temp_K=float(z[n+4])/(1.5*K_B_EV_PER_K*(1+yhe+g.electrons_per_h(yhe)))
    g.__post_init__()
    absorbed=np.array([initial.xhi-g.xhi,
                      yhe*(initial.xhei-g.xhei),
                      yhe*(g.xheiii-initial.xheiii)])
    photons=z[:n]
    return {
        "final_gas":g.__dict__.copy(),
        "nfev":res.nfev,
        "status":res.message,
        "photons_residual":float(p.flux.sum()-photons.sum()-sum(absorbed)),
        "energy_residual":float(np.dot(p.flux-photons,p.physical_eV)
             - (z[n+4]-initial_thermal) - np.dot(absorbed,p.bind_eV)),
    }
