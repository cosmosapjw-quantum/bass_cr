"""Independent direct generalized-ODE reference for TP1."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve


def find_target_1s(channels):
    hits=[]
    for i,c in enumerate(channels):
        if (getattr(c,'center',None)==0 and getattr(c.radial,'principal_n',None)==1
            and getattr(c.radial,'l',None)==0 and getattr(c,'m',None)==0):
            hits.append(i)
    if len(hits)!=1:
        raise ValueError('unique target 1s channel not resolved')
    return hits[0]


def metric_norm(c,S):
    value=np.vdot(c,S@c)
    if abs(value.imag)>1e-10*max(1.,abs(value.real)) or value.real<=0 or not np.isfinite(value):
        raise ArithmeticError('metric norm unresolved')
    return float(value.real)


def normalize_metric_state(c,S):
    c=np.asarray(c,complex)
    return c/np.sqrt(metric_norm(c,S))


def generalized_rhs(t,c,provider):
    s=provider.at(float(t))
    rhs=(-1j*s.H-s.D)@np.asarray(c,complex)
    return solve(s.S,rhs,assume_a='her',check_finite=False)


@dataclass(frozen=True)
class ReferenceResult:
    success: bool
    message: str
    method: str
    rtol: float
    atol: float
    nfev: int
    times: np.ndarray
    states: np.ndarray
    initial_state: np.ndarray
    final_state: np.ndarray
    norm_history: np.ndarray
    max_norm_drift: float


def run_reference(provider,channels,t0,tf,*,c0=None,rtol=1e-10,atol=1e-12,sample_times=None):
    t0=float(t0);tf=float(tf)
    if not np.isfinite([t0,tf]).all() or not tf>t0:
        raise ValueError('finite increasing time interval required')
    if c0 is None:
        s0=provider.at(t0)
        c0=np.zeros(len(channels),complex);c0[find_target_1s(channels)]=1.
        c0=normalize_metric_state(c0,s0.S)
    else:
        s0=provider.at(t0)
        c0=normalize_metric_state(np.asarray(c0,complex),s0.S)
    if sample_times is None:
        sample_times=np.linspace(t0,tf,9)
    sample_times=np.asarray(sample_times,float)
    if sample_times.ndim!=1 or len(sample_times)<2 or sample_times[0]!=t0 or sample_times[-1]!=tf or np.any(np.diff(sample_times)<=0):
        raise ValueError('sample_times must strictly span [t0,tf]')
    out=solve_ivp(lambda t,y:generalized_rhs(t,y,provider),(t0,tf),c0,
                  method='DOP853',rtol=float(rtol),atol=float(atol),t_eval=sample_times)
    if not out.success or not np.isfinite(out.y).all():
        raise ArithmeticError('reference solve_ivp failed: '+str(out.message))
    states=out.y.T.copy()
    norms=np.array([metric_norm(c,provider.at(t).S) for t,c in zip(out.t,states)],float)
    drift=float(np.max(np.abs(norms-norms[0])))
    return ReferenceResult(True,str(out.message),'DOP853',float(rtol),float(atol),int(out.nfev),
                           out.t.copy(),states,c0.copy(),states[-1].copy(),norms,drift)
