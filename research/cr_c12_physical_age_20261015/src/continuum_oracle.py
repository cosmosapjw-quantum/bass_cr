"""Independent QUADPACK emitted-energy oracle for C12's fixed receiver.

Uses the owner's cross-section scalar formula and photon spectrum, not
the C11 packet-sigma vectorization or fixed GL16 emitted-energy nodes.
Preserves original 12-node angular rule, so only energy integration is
independent. Never claim a full angular/time quadrature certificate.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad_vec

def reference_eight(ns:dict,age:float,q:float,gas:np.ndarray)->np.ndarray:
    model,spectrum=ns["model"],ns["spec"]
    rp,rz=model.ratios(.2,q)
    rpa,rza=model.ratios(age,q)
    rp/=rpa;rz/=rza
    vec=np.zeros(8)
    for mu,wm in zip(ns["mu"],ns["muw"]):
        scale=float(np.hypot(rp*np.sqrt(1-mu*mu),rz*mu))
        cuts=sorted(set([13.6,100.]+[p[0]/scale for p in ns["fit"] if 13.6<p[0]/scale<100.]))
        def f(emit):
            E=emit*scale
            rates=np.array([ns["C"]*density*ns["sigma"](float(E),fit)
                for density,fit in zip(gas,ns["fit"])])
            rate=float(np.sum(rates))
            absorption=rates*(-np.expm1(-rate*ns["dt"])/rate) if rate>0 else np.zeros(3)
            heat=absorption*(E-np.asarray(ns["bind"]))
            return (wm/2)*float(spectrum.phi(emit))*np.r_[1.,E,absorption,heat]
        for lo,hi in zip(cuts,cuts[1:]):
            v,_=quad_vec(f,lo,hi,epsabs=1e-11,epsrel=1e-11,quadrature="gk21")
            vec+=v
    return vec
