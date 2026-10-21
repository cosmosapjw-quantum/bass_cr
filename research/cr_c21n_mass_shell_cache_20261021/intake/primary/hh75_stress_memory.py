"""Vectorized LRS shear-memory diagnostics on immutable saved trajectories.

All inputs use SIGNED half-contraction coordinates and the SAME normal frame:
S = sqrt(3)*s/H; P_A = sqrt(3)*(8*pi*G/c**2)*p_A/H**2.
Multiply returned linear amplitudes by sqrt(2) for full Frobenius coordinates.
These sampled-data integrals are not continuum error certificates.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np

@lru_cache(maxsize=16)
def _weights(n: int, length: float) -> np.ndarray:
    w=np.ones(n,dtype=np.float64)
    w[1:-1:2]=4.; w[2:-1:2]=2.
    w*=length/(3*(n-1)); w.flags.writeable=False
    return w

def simpson_weights(x: np.ndarray) -> np.ndarray:
    """Shared read-only weights for an odd, uniform, increasing sample grid."""
    if np.iscomplexobj(x): raise ValueError("REAL_GRID_REQUIRED")
    x=np.asarray(x,dtype=np.float64)
    if x.ndim!=1 or x.size<3 or x.size%2!=1 or not np.isfinite(x).all():
        raise ValueError('GRID_REQUIRES_ODD_FINITE_1D_SAMPLES')
    h=np.diff(x)
    if np.any(h<=0) or not np.allclose(h,h.mean(),rtol=2e-12,atol=0):
        raise ValueError('GRID_REQUIRES_UNIFORM_INCREASING_COORDINATE')
    return _weights(len(x),float(x[-1]-x[0]))

def _arrays(x,H,S,Pm,Pr):
    if any(np.iscomplexobj(v) for v in (x,H,S,Pm,Pr)): raise ValueError("REAL_INPUTS_REQUIRED")
    x=np.asarray(x,dtype=np.float64); simpson_weights(x)
    values=[np.asarray(v,dtype=np.float64) for v in (H,S,Pm,Pr)]
    shape=values[0].shape
    if not shape or shape[-1]!=len(x) or any(v.shape!=shape for v in values):
        raise ValueError('SAME_CASE_AND_TIME_SHAPE_REQUIRED')
    if any(not np.isfinite(v).all() for v in values) or np.any(values[0]<=0):
        raise ValueError('FINITE_INPUTS_AND_POSITIVE_H_REQUIRED')
    return x,values

def memory_budget(x,H,shear_signed,pi_m_signed,pi_r_signed):
    """Return a separate matter/radiation decomposition for each leading index.

    D*S_i + int[e^(3*(x-x_f))*H/H_f*P_m dx] + analogous radiation.
    The components follow the actual coupled path; they are NOT counterfactual
    solutions obtained by switching a species off. No input arrays are changed.
    """
    x,(H,S,Pm,Pr)=_arrays(x,H,shear_signed,pi_m_signed,pi_r_signed)
    kernel=np.exp(3*(x-x[-1]))*(H/H[...,-1,None])
    w=simpson_weights(x)
    fm=kernel*Pm; fr=kernel*Pr
    matter=np.sum(fm*w,axis=-1); radiation=np.sum(fr*w,axis=-1)
    initial=kernel[...,0]*S[...,0]
    predicted=initial+matter+radiation
    observed=S[...,-1]; defect=observed-predicted
    scale=np.abs(initial)+np.abs(matter)+np.abs(radiation)+np.abs(observed)
    rel=np.divide(np.abs(defect),scale,out=np.zeros_like(defect),where=scale>0)
    subtotal=np.abs(matter)+np.abs(radiation)
    cancellation=1-np.divide(np.abs(matter+radiation),subtotal,out=np.ones_like(matter),where=subtotal>0)
    result={'initial_memory':initial,'matter_memory':matter,'radiation_memory':radiation,
            'predicted_signed_shear':predicted,'observed_signed_shear':observed,
            'closure_defect':defect,'closure_scaled_defect':rel,
            'stress_memory_cancellation':cancellation,'has_stress_memory':subtotal>0}
    if len(x)>=5 and (len(x)-1)%4==0:
        wc=simpson_weights(x[::2])
        mc=np.sum(fm[...,::2]*wc,axis=-1); rc=np.sum(fr[...,::2]*wc,axis=-1)
        result.update(matter_halfgrid_difference=matter-mc,
                      radiation_halfgrid_difference=radiation-rc,
                      total_halfgrid_difference=(matter+radiation)-(mc+rc))
    if any(not np.isfinite(v).all() for v in result.values()):
        raise FloatingPointError('NONFINITE_MEMORY_OUTPUT')
    return result

def sector_observables(shear_signed,pi_m_signed,pi_r_signed):
    """Preserve signed tensors before norm; both common normalizations retained."""
    if any(np.iscomplexobj(v) for v in (shear_signed,pi_m_signed,pi_r_signed)): raise ValueError("REAL_SECTORS_REQUIRED")
    s,pm,pr=[np.asarray(v,dtype=np.float64) for v in (shear_signed,pi_m_signed,pi_r_signed)]
    if not (s.shape==pm.shape==pr.shape) or any(not np.isfinite(v).all() for v in (s,pm,pr)):
        raise ValueError('SAME_FINITE_SECTOR_SHAPE_REQUIRED')
    root2=np.sqrt(2.)
    return {'Sigma_half':np.abs(s),'Pi_m_half':np.abs(pm),'Pi_r_half':np.abs(pr),
            'Pi_total_half':np.abs(pm+pr),'Sigma_F':root2*np.abs(s),
            'Pi_m_F':root2*np.abs(pm),'Pi_r_F':root2*np.abs(pr),
            'Pi_total_F':root2*np.abs(pm+pr),
            'signed_Sigma_F':root2*s,'signed_Pi_m_F':root2*pm,'signed_Pi_r_F':root2*pr,
            'work_loss_m_dimensionless':-2*s*pm,'work_loss_r_dimensionless':-2*s*pr,
            'matter_radiation_cross_F_squared':4*pm*pr}
