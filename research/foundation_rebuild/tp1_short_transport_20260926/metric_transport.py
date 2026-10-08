"""Cholesky metric-frame candidate transport for TP1."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.linalg import solve_triangular, expm

from reference_transport import normalize_metric_state


@dataclass(frozen=True)
class MetricGenerator:
    R: np.ndarray
    Ht: np.ndarray
    Dt: np.ndarray
    W: np.ndarray
    X: np.ndarray
    G: np.ndarray
    antihermitian_defect: float


def metric_frame_generator(snapshot):
    S=np.asarray(snapshot.S,complex);H=np.asarray(snapshot.H,complex);D=np.asarray(snapshot.D,complex)
    L=np.linalg.cholesky((S+S.conj().T)/2)
    R=L.conj().T
    Ri=solve_triangular(R,np.eye(len(S),dtype=complex),lower=False,check_finite=False)
    Ht=Ri.conj().T@H@Ri
    Dt=Ri.conj().T@D@Ri
    W=Dt+Dt.conj().T
    X=np.triu(W,1)+np.diag(np.real(np.diag(W))/2)
    G=X-Dt-1j*Ht
    defect=float(np.linalg.norm(G+G.conj().T)/max(np.linalg.norm(G),1e-300))
    return MetricGenerator(R,Ht,Dt,W,X,G,defect)


def phase_aligned_metric_distance(a,b,S):
    a=np.asarray(a,complex);b=np.asarray(b,complex);S=np.asarray(S,complex)
    overlap=np.vdot(a,S@b)
    phase=1.+0j if abs(overlap)==0 else np.exp(-1j*np.angle(overlap))
    d=a-phase*b
    value=np.vdot(d,S@d)
    if abs(value.imag)>1e-10*max(1.,abs(value.real)) or value.real < -1e-13:
        raise ArithmeticError('metric distance unresolved')
    return float(np.sqrt(max(value.real,0.)))


@dataclass(frozen=True)
class CandidateResult:
    success: bool
    nstep: int
    dt: float
    initial_state: np.ndarray
    final_state: np.ndarray
    norm_history: np.ndarray
    max_norm_drift: float
    max_generator_defect: float


def candidate_step(provider,y,ta,tb):
    ta=float(ta);tb=float(tb)
    if not tb>ta:
        raise ValueError('candidate step requires tb>ta')
    tm=0.5*(ta+tb)
    gen=metric_frame_generator(provider.at(tm))
    return expm((tb-ta)*gen.G)@np.asarray(y,complex),gen


def run_candidate(provider,c0,t0,tf,nstep):
    t0=float(t0);tf=float(tf)
    if type(nstep) is not int or nstep<1:
        raise ValueError('positive integer nstep required')
    if not tf>t0:
        raise ValueError('increasing time interval required')
    s0=provider.at(t0)
    c0=normalize_metric_state(np.asarray(c0,complex),s0.S)
    g0=metric_frame_generator(s0)
    y=g0.R@c0
    norm0=float(np.vdot(y,y).real)
    norms=[norm0]
    maxdef=g0.antihermitian_defect
    dt=(tf-t0)/nstep
    for j in range(nstep):
        ta=t0+j*dt;tb=ta+dt
        y,g=candidate_step(provider,y,ta,tb)
        maxdef=max(maxdef,g.antihermitian_defect)
        norms.append(float(np.vdot(y,y).real))
    sf=provider.at(tf)
    Rf=metric_frame_generator(sf).R
    cf=solve_triangular(Rf,y,lower=False,check_finite=False)
    norms=np.asarray(norms,float)
    return CandidateResult(True,nstep,dt,c0.copy(),cf,norms,
                           float(np.max(np.abs(norms-norms[0]))),float(maxdef))
