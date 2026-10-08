"""Small-matrix reference diagnostics; no interval or physical admission."""
from __future__ import annotations
import numpy as np
from bridge import ContractError

def _square(x):
    x=np.asarray(x,dtype=np.complex128)
    if x.ndim!=2 or x.shape[0]!=x.shape[1] or not np.all(np.isfinite(x)):
        raise ContractError('finite square matrix required')
    return x

def span_projector(S,J):
    """Projector onto span(J) in d=L^dagger c, S=L L^dagger coordinates.

    Does not normalize individual nonorthogonal columns and add them.
    Floating diagnostic only. Non-Hermitian S is not silently projected.
    """
    S=_square(S);J=np.asarray(J,dtype=np.complex128)
    if J.ndim!=2 or J.shape[0]!=len(S) or J.shape[1]<1 or J.shape[1]>len(S) or not np.all(np.isfinite(J)):
        raise ContractError('finite independent selector columns required')
    if not np.array_equal(S,S.conj().T):raise ContractError('Hermitian metric required')
    try:
        L=np.linalg.cholesky(S);V=L.conj().T@J
        C=V.conj().T@V
        np.linalg.cholesky(C)
        return V@np.linalg.solve(C,V.conj().T)
    except np.linalg.LinAlgError as e:raise ContractError('SPD metric and full rank selector required') from e

def frame_generator(H,D,M,Mdot,hbar):
    """h=M^{-dagger}(H-i*hbar*D)M^{-1}+i*hbar*Mdot*M^{-1}.

    M must satisfy M^dagger M=S in the caller's declared representation.
    Return the unprojected generator, so metric defects remain visible.
    """
    H,D,M,Mdot=map(_square,(H,D,M,Mdot))
    if len({x.shape for x in (H,D,M,Mdot)})!=1 or not np.isfinite(hbar) or hbar<=0:
        raise ContractError('matching matrices and positive hbar required')
    try:Mi=np.linalg.inv(M)
    except np.linalg.LinAlgError as e:raise ContractError('singular frame') from e
    return Mi.conj().T@(H-1j*hbar*D)@Mi+1j*hbar*Mdot@Mi
