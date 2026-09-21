"""Analytic Cartesian GTO integrals with plane-wave electron translation factors.

Independent research implementation. Spatial integrals are analytic: a Gaussian
moment polynomial is contracted with complex Boys functions, not 6D quadrature.
Shell coefficients normalize *each primitive*, including Cartesian powers.
The electronic collision Hamiltonian deliberately omits common nuclear 1/R.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np
from scipy.special import hyp1f1, erf


def boys(n: int, z):
    """Entire F_n(z)=integral_0^1 u^(2n) exp(-z u^2) du."""
    if not isinstance(n,int) or n<0: raise ValueError('nonnegative integer n required')
    z=np.asarray(z,dtype=complex)
    if not np.all(np.isfinite(z)): raise ValueError('finite Boys argument required')
    flat=z.ravel(); v=np.empty_like(flat)
    # Upward recurrence is stable for Re(z)>0 with |z| well above n.
    # Complex hyp1f1 overflows internally even at a purely real z=780;
    # evaluate the erf base directly there, without any large exponentials.
    large=(flat.real>0)&(np.abs(flat)>max(20.,2*n+4.))
    zl=flat[large]; root=np.sqrt(zl)
    f=.5*np.sqrt(np.pi)*erf(root)/root
    for j in range(n): f=((2*j+1)*f-np.exp(-zl))/(2*zl)
    v[large]=f
    v[~large]=hyp1f1(n+.5,n+1.5,-flat[~large])/(2*n+1)
    if not np.all(np.isfinite(v)): raise FloatingPointError('Boys evaluation nonfinite')
    v=v.reshape(z.shape)
    return v.item() if v.ndim==0 else v


def dfact(n):
    return math.prod(range(n,0,-2)) if n>0 else 1

@dataclass
class Shell:
    alpha: np.ndarray
    powers: tuple[int,int,int]
    center: np.ndarray
    k: np.ndarray
    def __post_init__(self):
        self.alpha=np.asarray(self.alpha,dtype=float)
        self.center=np.asarray(self.center,dtype=float)
        self.k=np.asarray(self.k,dtype=float)
        self.powers=tuple(self.powers)
        if self.alpha.ndim!=1 or np.any(self.alpha<=0) or not np.all(np.isfinite(self.alpha)):
            raise ValueError('finite positive 1D exponents required')
        if len(self.powers)!=3 or any(int(x)!=x or x<0 for x in self.powers):
            raise ValueError('three nonnegative Cartesian powers required')
        if self.center.shape!=(3,) or self.k.shape!=(3,) or not np.all(np.isfinite([self.center,self.k])):
            raise ValueError('finite 3-vectors required')
    @property
    def norm(self):
        L=sum(self.powers)
        return (2*self.alpha/np.pi)**.75*(4*self.alpha)**(L/2)/np.sqrt(math.prod(dfact(2*x-1) for x in self.powers))


def _pair(a,b):
    aa=a.alpha[:,None]; bb=b.alpha[None,:]; p=aa+bb
    q=b.k-a.k; delta=a.center-b.center
    realP=(aa[...,None]*a.center+bb[...,None]*b.center)/p[...,None]
    P=realP+.5j*q/p[...,None]
    # Expanded product exponent avoids cancellation at widely separated centres.
    expo=-aa*bb/p*np.dot(delta,delta)-np.dot(q,q)/(4*p)+1j*np.sum(q*realP,axis=-1)
    K=a.norm[:,None]*b.norm[None,:]*np.exp(expo)
    return p,P,K


def _factors(powers,center,e):
    return [(e,d,float(center[d])) for d in range(3) for _ in range(powers[d])]


def _add(a,b):
    c=[0]*(max(len(a),len(b)))
    for i,x in enumerate(a):c[i]=c[i]+x
    for i,x in enumerate(b):c[i]=c[i]+x
    return c


def _mul(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]=c[i+j]+x*y
    return c


def _moment(factors,mu0,mu1,cov0,cov1):
    """Noncentral Gaussian moments by Wick pairing, polynomial in t^2.

    Covariances are scalar per Cartesian component and electron pair. Complex
    centres use a bilinear dot, never an absolute square or complex conjugation.
    """
    means=[[mu0[e][...,d]-A,mu1[e][...,d]] for e,d,A in factors]
    @lru_cache(None)
    def rec(ids):
        if not ids:return [1.]
        i=ids[0]; rest=ids[1:]
        out=_mul(means[i],rec(rest))
        e,d,_=factors[i]
        for loc,j in enumerate(rest):
            f,dd,_=factors[j]
            if d==dd:
                out=_add(out,_mul([cov0[e][f],cov1[e][f]],rec(rest[:loc]+rest[loc+1:])))
        return out
    return rec(tuple(range(len(factors))))


def _overlap_raw(a,b,pa=None,pb=None):
    p,P,K=_pair(a,b)
    pa=a.powers if pa is None else pa; pb=b.powers if pb is None else pb
    if any(x<0 for x in pa+pb):return np.zeros_like(p,complex)
    fs=_factors(pa,a.center,0)+_factors(pb,b.center,0)
    # Only the constant moment is needed for an unweighted Gaussian.
    means=[P];zeros=[np.zeros_like(P)]
    poly=_moment(fs,means,zeros,[[1/(2*p)]],[[0.]])
    return K*(np.pi/p)**1.5*poly[0]


def overlap(a,b):return _overlap_raw(a,b)


def _raised(powers,axis,n):
    out=list(powers);out[axis]+=n;return tuple(out)


def kinetic(a,b):
    """Exact -1/2 Laplacian including plane-wave and polynomial derivatives."""
    beta=b.alpha[None,:]; pb=b.powers; L=sum(pb)
    base=_overlap_raw(a,b)
    out=(beta*(2*L+3)+.5*np.dot(b.k,b.k))*base
    for d in range(3):
        out-=2*beta**2*_overlap_raw(a,b,pb=_raised(pb,d,2))
        if pb[d]>=2:out-=.5*pb[d]*(pb[d]-1)*_overlap_raw(a,b,pb=_raised(pb,d,-2))
        if b.k[d]!=0:
            out+=2j*beta*b.k[d]*_overlap_raw(a,b,pb=_raised(pb,d,1))
            if pb[d]:out-=1j*b.k[d]*pb[d]*_overlap_raw(a,b,pb=_raised(pb,d,-1))
    return out


def moving_ket_overlap(a,b,velocity):
    """<a| partial_t b> for fixed k, translated centre, no time phase."""
    v=np.asarray(velocity,float); beta=b.alpha[None,:];out=np.zeros((len(a.alpha),len(b.alpha)),complex)
    for d in range(3):
        if v[d]:
            out+=v[d]*2*beta*_overlap_raw(a,b,pb=_raised(b.powers,d,1))
            if b.powers[d]:out-=v[d]*b.powers[d]*_overlap_raw(a,b,pb=_raised(b.powers,d,-1))
    return out


def nuclear(a,b,center,Z=1.):
    p,P,K=_pair(a,b); delta=P-np.asarray(center,float)
    fs=_factors(a.powers,a.center,0)+_factors(b.powers,b.center,0)
    poly=_moment(fs,[P],[-delta],[[1/(2*p)]],[[-1/(2*p)]])
    arg=p*np.sum(delta*delta,axis=-1)
    out=sum(c*boys(i,arg) for i,c in enumerate(poly))
    return -Z*2*np.pi/p*K*out


def eri(a,b,c,d):
    """(ab|cd)=integral a*(1)b(1) |r1-r2|^-1 c*(2)d(2)."""
    p,P,K1=_pair(a,b);q,Q,K2=_pair(c,d)
    p=p[:,:,None,None];q=q[None,None,:,:]
    P=P[:,:,None,None,:];Q=Q[None,None,:,:,:]
    delta=P-Q; pq=p+q; rho=p*q/pq
    mu0=[P,Q];mu1=[-q[...,None]/pq[...,None]*delta,p[...,None]/pq[...,None]*delta]
    cov0=[[1/(2*p),0.],[0.,1/(2*q)]]
    cov1=[[-q/(2*p*pq),1/(2*pq)],[1/(2*pq),-p/(2*q*pq)]]
    fs=_factors(a.powers,a.center,0)+_factors(b.powers,b.center,0)+_factors(c.powers,c.center,1)+_factors(d.powers,d.center,1)
    poly=_moment(fs,mu0,mu1,cov0,cov1)
    arg=rho*np.sum(delta*delta,axis=-1)
    out=sum(coef*boys(n,arg) for n,coef in enumerate(poly))
    return K1[:,:,None,None]*K2[None,None,:,:]*(2*np.pi**2.5/(p*q*np.sqrt(pq)))*out
