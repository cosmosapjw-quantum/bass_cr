"""Piecewise-source Maxwellian core quadrature, MODEL diagnostics only.

This is a floating reference for a stationary isotropic Maxwell target and a
single projectile drift speed. It is not a host adapter or interval quadrature.
No source extrapolation is performed and omitted tails are never set to zero.
"""
from __future__ import annotations
import math
from fractions import Fraction as F
from .core import ContractError
from .provider import SourceModel
from .kinetics import relative_speed_pdf_scaled

def maxwellian_core(source:SourceModel,*,reduced_mass_kg:float,
                    thermal_sigma_m_s:float,drift_m_s:float,
                    epsabs=1e-12,epsrel=1e-10):
    from scipy.integrate import quad
    if not isinstance(source,SourceModel):raise ContractError('typed MODEL source required')
    mu,s,V=map(float,(reduced_mass_kg,thermal_sigma_m_s,drift_m_s))
    if not all(math.isfinite(x) for x in (mu,s,V,epsabs,epsrel)) or min(mu,s)<=0 or V<0 or epsabs<=0 or not 0<epsrel<1:
        raise ContractError('finite positive masses/thermal scale/tolerances required')
    escale=mu*s*s/2;a=V/s
    if not math.isfinite(escale) or escale<=0 or not math.isfinite(a):raise ContractError('unsupported scaled dynamic range')
    # E=mu*s^2*y^2/2; source knots are preserved exactly in the model, while
    # this floating diagnostic uses the corresponding rounded y endpoints.
    y=[math.sqrt(float(e)/escale) for e in source.energies]
    if any(not math.isfinite(v) for v in y) or any(u>=v for u,v in zip(y,y[1:])):
        raise ContractError('source knots cannot be represented as distinct scaled endpoints')
    panels=[];tot=[0.,0.];err=[0.,0.]
    for i,(l,h) in enumerate(zip(y,y[1:])):
        vals=[];errs=[]
        for k in (0,1):
            s0,s1=map(float,(source.envelopes[i][k],source.envelopes[i+1][k]))
            def f(t):
                # Interpolate by y^2 within this energy panel, not in y.
                weight=(t*t-l*l)/(h*h-l*l)
                sigma=(1-weight)*s0+weight*s1
                return s*t*relative_speed_pdf_scaled(t,a)*sigma
            # Important for narrow drifting distributions: force subdivisions
            # around the Gaussian core rather than trusting a wide single panel.
            pts=sorted(set(v for v in [a-8,a-4,a,a+4,a+8] if l<v<h))
            v,e=quad(f,l,h,points=pts,epsabs=epsabs/max(1,len(y)-1),epsrel=epsrel,limit=250)
            if not math.isfinite(v) or not math.isfinite(e) or v<0:raise ContractError('invalid quadrature result')
            vals.append(v);errs.append(e);tot[k]+=v;err[k]+=e
        panels.append({'energy_J':[str(source.energies[i]),str(source.energies[i+1])],
                       'estimate':vals,'quadrature_error_estimate':errs})
    return {'schema':'CX_MAXWELLIAN_CORE_REFERENCE_V1','status':'FLOATING_MODEL_CORE_ONLY',
            'profile':'MODEL','source_sha256':source.payload_sha256,
            'K_core_interval_estimate_m3_s':tot,'quadrature_error_estimate_m3_s':err,
            'error_type':'QUADPACK_ESTIMATE_NOT_ENCLOSURE',
            'low_energy_tail_bound':None,'high_energy_tail_bound':None,
            'source_model_discrepancy':None,'total_K_upper':None,'physical_admission':False,
            'actual_host_bound':False,'thermal_scale_definition':'s^2=k_B*T/m_target',
            'distribution':'stationary isotropic Maxwell target; fixed projectile speed',
            'panels':panels}
