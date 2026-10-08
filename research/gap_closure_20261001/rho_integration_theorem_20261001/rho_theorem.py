"""Small audit kernel for the fixed-J finite moving-basis theorem, atomic units.

This synthetic reference is not a replacement for the project physical probe.
It validates algebraic compatibility; it does not independently validate Sdot.
No clipping, diagonal shifts, pseudoinverses, or explicit inverse operations.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import cholesky, eigh, solve


@dataclass(frozen=True)
class RateForms:
    A: np.ndarray
    Pi: np.ndarray
    Q: np.ndarray
    Qdot: np.ndarray
    W: np.ndarray
    eigenvalues: np.ndarray
    rho: float


def _hermitian(name, a, tol):
    scale = max(1.0, float(np.linalg.norm(a, 2)))
    if np.linalg.norm(a-a.conj().T, 2) > tol*scale:
        raise ValueError(f'{name} must be Hermitian within the audit tolerance')


def rate_forms(S, H, D, Sdot, J, *, validation_tolerance=1e-12):
    """Return Pi,Q,Qdot,W and rho for compatible inputs with fixed J.

    S/H/D/Sdot are n-by-n; J is n-by-k, 1<=k<=n, full column rank.
    Tolerance validates input roundoff only: it never repairs the supplied data.
    H is in inverse atomic-time units (hbar=1). For SI inputs use H/hbar.
    A finite tolerance pass is a synthetic implementation check, not a proof of
    the underlying physical Sdot=D+D† implementation.
    """
    S, H, D, Sdot, J = (np.asarray(x, dtype=np.complex128) for x in (S,H,D,Sdot,J))
    if S.ndim != 2 or S.shape[0] != S.shape[1]:
        raise ValueError('S must be square')
    n = S.shape[0]
    if n == 0 or any(x.shape != (n,n) for x in (H,D,Sdot)):
        raise ValueError('S,H,D,Sdot must have the same nonempty square shape')
    if J.ndim != 2 or J.shape[0] != n or not 1 <= J.shape[1] <= n:
        raise ValueError('J must be n-by-k with 1 <= k <= n')
    if not all(np.all(np.isfinite(x)) for x in (S,H,D,Sdot,J)):
        raise ValueError('all inputs must be finite')
    if not np.isfinite(validation_tolerance) or validation_tolerance <= 0:
        raise ValueError('validation_tolerance must be finite and positive')
    for name, x in (('S',S),('H',H),('Sdot',Sdot)):
        _hermitian(name,x,validation_tolerance)
    cholesky(S, lower=True, check_finite=False)
    defect = np.linalg.norm(Sdot-D-D.conj().T, 2)
    scale = max(1.0, float(np.linalg.norm(Sdot,2)), float(np.linalg.norm(D+D.conj().T,2)))
    if defect > validation_tolerance*scale:
        raise ValueError('Sdot compatibility with D+D† failed')
    G = J.conj().T@S@J
    cholesky(G, lower=True, check_finite=False)
    F = solve(G,J.conj().T@S,assume_a='pos',check_finite=False)
    Pi = J@F
    Q = S@Pi
    Gdot = J.conj().T@Sdot@J
    Fdot = solve(G,J.conj().T@Sdot-Gdot@F,assume_a='pos',check_finite=False)
    Qdot = Sdot@Pi+S@J@Fdot
    A = solve(S,-1j*H-D,assume_a='pos',check_finite=False)
    W = Qdot+A.conj().T@Q+Q@A
    _hermitian('W',W,20*validation_tolerance)
    eigenvalues = eigh(W,S,eigvals_only=True,check_finite=False)
    return RateForms(A,Pi,Q,Qdot,W,eigenvalues,float(np.max(np.abs(eigenvalues))))
