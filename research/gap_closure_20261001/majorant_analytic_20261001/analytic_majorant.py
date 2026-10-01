"""Conditional research formulas, not a physical/interval certificate.

Fixed full-rank J only. No native assembly, propagation, input regularization,
or substitution of a tail-point state. All time rates use atomic hbar=1.
"""
from __future__ import annotations
import math
import numpy as np


def cancellation_rate(S,H,D,J):
    """Return exact-algebra cancellation form, evaluated in ordinary float64.

    Requires H Hermitian, S SPD, and Sdot=D+D† in the mathematical model.
    Floating evaluation alone does not establish that kinematic identity.
    """
    S,H,D,J=[np.asarray(x,dtype=complex) for x in (S,H,D,J)]
    n=S.shape[0]
    if (S.shape!=(n,n) or H.shape!=S.shape or D.shape!=S.shape
        or J.ndim!=2 or J.shape[0]!=n or not 0<J.shape[1]<=n
        or not all(np.isfinite(x).all() for x in (S,H,D,J))):
        raise ValueError('finite consistent matrix dimensions required')
    for label,x in [('S',S),('H',H)]:
        if np.linalg.norm(x-x.conj().T,2)>1e-11*max(1,np.linalg.norm(x,2)):
            raise ValueError(label+' must be Hermitian')
    L=np.linalg.cholesky(S)
    G=J.conj().T@S@J
    np.linalg.cholesky(G)
    Pi=J@np.linalg.solve(G,J.conj().T@S)
    F=(np.eye(n)-Pi.conj().T)@(1j*H+D)@Pi
    W=F+F.conj().T
    left=np.linalg.solve(L,F)
    whitened_F=np.linalg.solve(L,left.conj().T).conj().T
    return {'Pi':Pi,'F':F,'W':W,
            'rho_offdiagonal':float(np.linalg.norm(whitened_F,2)),
            'certification':'ORDINARY_FLOAT_SYNTHETIC_OR_RESEARCH_CHECK_ONLY'}


def _scalars(*values):
    if not all(np.isscalar(v) and not isinstance(v,(bool,np.bool_)) and math.isfinite(v) for v in values):
        raise ValueError('finite real scalar parameters required')


def compact_support_tail(Z,b,a,v,charge=1.,hbar=1.):
    """Integrate charge*a/[hbar*v*(z²+b²-a²)] from Z to infinity.

    Caller must establish exact isolated-span invariance, zero cross blocks,
    metric compatibility, and compact support; this function does not do so.
    The disjoint-support region R(Z)>2*a is enforced, but not certified outward.
    """
    _scalars(Z,b,a,v,charge,hbar)
    if min(Z,a,v,hbar)<=0 or min(b,charge)<0 or math.hypot(Z,b)<=2*a:
        raise ValueError('positive parameters and disjoint support R(Z)>2a required')
    if b<a:
        k=math.sqrt((a-b)*(a+b))
        integral=math.atanh(k/Z)/k
    elif b>a:
        k=math.sqrt((b-a)*(b+a))
        integral=math.atan(k/Z)/k
    else:
        integral=1/Z
    return charge*a*integral/(hbar*v)


def inverse_square_tail(C,Z,b,v):
    """Stable conditional p=2 integral; C must come from an actual majorant."""
    _scalars(C,Z,b,v)
    if C<0 or Z<=0 or b<0 or v<=0:
        raise ValueError('C,b nonnegative; Z,v positive required')
    return C/(v*Z) if b==0 else (C/v)*(math.atan(b/Z)/b)
