"""R3M13 preparation-only audit tools for the 100 keV/u, b=2 a0 CR lane.

These helpers do not admit a physical cross section. They compare two normalized
initial states and provide a sufficient bound on the change of a later finite-span
probability when both states are propagated by the same contraction and projected
with the same orthogonal projector.
"""
from __future__ import annotations

import math
from copy import deepcopy
from typing import Mapping, Any

import numpy as np


R3M12_REFERENCE_P_SPAN = 0.00775827737938
R3M12_SCREEN = 0.01


def _positive(x: float, name: str) -> float:
    x=float(x)
    if not math.isfinite(x) or x <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return x


def _normalized_flat(state, dv: float) -> tuple[np.ndarray,float]:
    dv=_positive(dv,'dv')
    a=np.asarray(state,dtype=np.complex128).reshape(-1)
    if a.size == 0 or not np.isfinite(a).all():
        raise ValueError('state must be nonempty and finite')
    n=float(np.vdot(a,a).real*dv)
    if not math.isfinite(n) or n <= 0:
        raise ValueError('state norm must be positive')
    return a/math.sqrt(n), n


def phase_aligned_distance(state_a, state_b, dv: float) -> float:
    """min_theta ||a-exp(i theta)b|| for the normalized pure states.

    The norm and overlap use the same uniform-grid measure `dv`.
    """
    a,_=_normalized_flat(state_a,dv)
    b,_=_normalized_flat(state_b,dv)
    if a.shape != b.shape:
        raise ValueError('state shapes do not match')
    amp=abs(np.vdot(a,b)*float(dv))
    amp=min(1.0,max(0.0,float(amp)))
    return math.sqrt(max(0.0,2.0-2.0*amp))


def probability_transfer_interval(p_ref: float, distance: float) -> tuple[float,float]:
    """Sufficient interval for p_new under a common contraction K and projector Q."""
    p=float(p_ref); d=float(distance)
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError('p_ref must lie in [0,1]')
    if not math.isfinite(d) or d < 0 or d > math.sqrt(2)+1e-12:
        raise ValueError('distance outside normalized pure-state range')
    r=math.sqrt(p)
    return max(0.0,r-d)**2, min(1.0,(r+d)**2)


def sufficient_screen_distance(p_ref: float, relative_screen: float) -> float:
    """Sufficient phase-L2 threshold for a symmetric relative probability screen."""
    p=float(p_ref); s=float(relative_screen)
    if not math.isfinite(p) or not 0 < p <= 1:
        raise ValueError('p_ref must lie in (0,1]')
    if not math.isfinite(s) or not 0 < s < 1:
        raise ValueError('relative_screen must lie in (0,1)')
    return math.sqrt(p)*(math.sqrt(1.0+s)-1.0)


def trace_distance_from_phase_l2(distance: float) -> float:
    """Pure-state trace distance implied by phase-aligned normalized L2 distance."""
    d=float(distance)
    if not math.isfinite(d) or not 0 <= d <= math.sqrt(2)+1e-12:
        raise ValueError('distance outside normalized pure-state range')
    return d*math.sqrt(max(0.0,1.0-d*d/4.0))


def build_preparation_configs(base: Mapping[str,Any]) -> tuple[dict,dict]:
    """Freeze the R3M12 dx=.25 lane and change only imaginary-time step/count."""
    c=deepcopy(dict(base))
    required=('grid','dt','absorber_reference_dt','imag_dt','imag_steps')
    if any(k not in c for k in required):
        raise ValueError('incomplete R3M12 preparation config')
    if abs(float(c['grid'].get('dx',math.nan))-.25) > 1e-15:
        raise ValueError('R3M13 is scoped to dx=.25 only')
    if abs(float(c['dt'])-.05) > 1e-15 or abs(float(c['absorber_reference_dt'])-.05) > 1e-15:
        raise ValueError('R3M13 keeps physical dt=.05 and fixed CAP reference dt=.05')
    if abs(float(c['imag_dt'])-.025) > 1e-15 or int(c['imag_steps']) != 1200:
        raise ValueError('base must be the R3M12 .025 x 1200 preparation')
    ref=deepcopy(c); new=deepcopy(c)
    new['imag_dt']=.0125; new['imag_steps']=2400
    return ref,new


def preparation_certificate(p_ref: float, relative_screen: float, distance: float) -> dict:
    threshold=sufficient_screen_distance(p_ref,relative_screen)
    lo,hi=probability_transfer_interval(p_ref,distance)
    rel=max(abs(lo-p_ref),abs(hi-p_ref))/p_ref
    return dict(
        schema='R3M13_PREPARATION_TRANSFER_CERTIFICATE_V1',
        p_ref=float(p_ref),relative_screen=float(relative_screen),
        phase_aligned_distance=float(distance),sufficient_distance_threshold=threshold,
        certified_below_screen=bool(distance <= threshold),
        probability_interval=[lo,hi],worst_relative_interval_excursion=rel,
        trace_distance=trace_distance_from_phase_l2(distance),
        semantics='SUFFICIENT_COMMON_CONTRACTION_AND_COMMON_ORTHOGONAL_PROJECTOR_BOUND_NOT_TOTAL_PHYSICAL_ERROR'
    )
