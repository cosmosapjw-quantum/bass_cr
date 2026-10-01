"""Cancellation-preserving finite moving-basis projector rate, small-matrix reference.

No native kernel, propagation, matrix repair, explicit inverse or new B0 query.
This FP64 implementation is not an outward-rounded enclosure. hbar is explicit.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import cholesky, qr, solve, solve_triangular


@dataclass(frozen=True)
class CancellationRate:
    S: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    G: np.ndarray
    M: np.ndarray
    residual: np.ndarray
    E: np.ndarray
    rho: float
    Q: np.ndarray
    W: np.ndarray


@dataclass(frozen=True)
class StateRate:
    norm: float
    population: float
    complement_population: float
    rate: float
    bound: float


def _hermitian(name, value, tolerance):
    if np.linalg.norm(value-value.conj().T,2) > tolerance*max(1.,np.linalg.norm(value,2)):
        raise ValueError(name+' is not Hermitian within input validation tolerance')


def _right_whiten(value, lower):
    """value @ lower^{-dagger}, using triangular solves."""
    return solve_triangular(lower.conj(),value.T,lower=True,check_finite=False).T


def cancellation_rate(S,H,D,Sdot,J,*,hbar,Jdot=None,K=None,validation_tolerance=1e-12):
    """Return E=Y†[(D+iH/hbar)J+S Jdot] L_G^{-†} and rho=||E||2.

    J spans the selected coefficient subspace. K is any optional completion;
    default K comes from a complete Euclidean QR of J. X,Y are S-orthonormal.
    Sdot is independently supplied and checked, never repaired. A tolerance
    pass only checks the provided matrices; assigning Sdot=D+D† beforehand
    is an algebraic replay, not physical overlap-derivative validation.

    The Schur residual is assembled before whitening or taking a norm, keeping
    selected/complement and Hamiltonian/connection cancellations intact.
    Small ill-conditioned metrics or cancellations still need numerical error
    analysis; this function does not claim certified floating-point bounds.
    """
    S,H,D,Sdot,J=(np.asarray(x,dtype=np.complex128) for x in (S,H,D,Sdot,J))
    if S.ndim!=2 or S.shape[0]!=S.shape[1] or not S.shape[0]:raise ValueError('nonempty square S required')
    n=S.shape[0]
    if any(x.shape!=(n,n) for x in (H,D,Sdot)):raise ValueError('operator shape mismatch')
    if J.ndim!=2 or J.shape[0]!=n or not 1<=J.shape[1]<=n:raise ValueError('J must be n by k, 1<=k<=n')
    if not np.isscalar(hbar) or np.iscomplexobj(hbar) or not np.isfinite(hbar) or hbar<=0:raise ValueError('positive finite hbar required')
    if not np.isfinite(validation_tolerance) or validation_tolerance<=0:raise ValueError('positive finite validation tolerance required')
    Jdot=np.zeros_like(J) if Jdot is None else np.asarray(Jdot,dtype=np.complex128)
    if Jdot.shape!=J.shape:raise ValueError('Jdot shape mismatch')
    if not all(np.isfinite(x).all() for x in (S,H,D,Sdot,J,Jdot)):raise ValueError('finite inputs required')
    for name,value in (('S',S),('H',H),('Sdot',Sdot)):_hermitian(name,value,validation_tolerance)
    cholesky(S,lower=True,check_finite=False)
    delta=Sdot-D-D.conj().T
    scale=max(1.,np.linalg.norm(Sdot,2),np.linalg.norm(D+D.conj().T,2))
    if np.linalg.norm(delta,2)>validation_tolerance*scale:raise ValueError('Sdot compatibility with D+D† failed')
    k=J.shape[1]
    G=J.conj().T@S@J
    lg=cholesky(G,lower=True,check_finite=False)
    X=_right_whiten(J,lg)
    sx=S@X
    Q=sx@sx.conj().T
    if k==n:
        if K is not None and np.asarray(K).shape!=(n,0):raise ValueError('full selected span has an empty complement')
        return CancellationRate(S,X,np.empty((n,0),complex),G,np.empty((0,0),complex),
                                np.empty((0,k),complex),np.empty((0,k),complex),0.,Q,np.zeros_like(S))
    if K is None:
        complete,_=qr(J,mode='full',check_finite=False)
        K=complete[:,k:]
    else:
        K=np.asarray(K,dtype=np.complex128)
        if K.shape!=(n,n-k) or not np.isfinite(K).all():raise ValueError('K must be a finite n by n-k completion')
    # Reject a deficient completion explicitly; no pseudoinverse is allowed.
    if np.linalg.matrix_rank(np.column_stack((J,K)))!=n:
        raise np.linalg.LinAlgError('[J,K] must be nonsingular')
    B=J.conj().T@S@K
    ginv_b=solve(G,B,assume_a='pos',check_finite=False)
    U=K-J@ginv_b
    # This is the Schur complement C-B†G^-1B, evaluated as U†SU to
    # avoid subtracting two large positive matrices a second time.
    M=U.conj().T@S@U
    lm=cholesky(M,lower=True,check_finite=False)
    Y=_right_whiten(U,lm)
    FJ=(D+1j*H/hbar)@J+S@Jdot
    residual=K.conj().T@FJ-B.conj().T@solve(G,J.conj().T@FJ,assume_a='pos',check_finite=False)
    E=_right_whiten(solve_triangular(lm,residual,lower=True,check_finite=False),lg)
    rho=float(np.linalg.svd(E,compute_uv=False)[0])
    sy=S@Y
    half=sy@E@sx.conj().T
    W=half+half.conj().T
    if not all(np.isfinite(x).all() for x in (X,Y,M,residual,E,Q,W)) or not np.isfinite(rho):
        raise ArithmeticError('nonfinite factorization result')
    return CancellationRate(S,X,Y,G,M,residual,E,rho,Q,W)


def state_rate(forms,c):
    """Exact-state formula evaluated in FP64; no propagated state is supplied."""
    c=np.asarray(c,dtype=np.complex128)
    if c.shape!=(forms.S.shape[0],) or not np.isfinite(c).all():raise ValueError('finite coefficient vector required')
    a=forms.X.conj().T@forms.S@c
    b=forms.Y.conj().T@forms.S@c
    p=float(np.vdot(a,a).real)
    complement=float(np.vdot(b,b).real)
    # Complement norm avoids subtracting P from N near a pure selected state.
    return StateRate(p+complement,p,complement,float(2*np.real(np.vdot(b,forms.E@a))),
                     float(2*np.linalg.norm(a)*np.linalg.norm(b)*forms.rho))
