"""R4AF Gaussian nodes and tensor holomorphic error bound.

Scipy/mpmath only propose brackets. Every root is then certified by exact
rational sign changes in n disjoint brackets inside (-1,1). The degree n
excludes unaccounted roots. Weight intervals use the exact Legendre formula.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import factorial
from functools import lru_cache
from dyadic import I,ONE,ZERO,SCALE


def gauss_constant(n:int,rho:F)->F:
    rho=F(rho)
    if type(n) is not int or n<1 or rho<=1: raise ValueError('n>=1 and rho>1 required')
    return F(64,15)/((rho-1)*rho**(2*n-1))


def legendre(n,x):
    a=1; b=x
    if n==0:return a
    for k in range(1,n):a,b=b,((2*k+1)*x*b-k*a)/(k+1)
    return b


def tensor_errors(mu,mw,hu,hw,n,rho=F(2)):
    """Complex modulus bounds per element; mapped from [-1,1]^2.

    (Iu-Qu)Iw + Qu(Iw-Qw); positive Gaussian weights sum to 2.
    M_u is uniform for complex u ellipse and real w interval, and vice versa.
    """
    k=I(2*F(hu)*F(hw)*gauss_constant(n,rho))
    return [[k*(a+b) for a,b in zip(ra,rb)] for ra,rb in zip(mu,mw)]


def radius_l1_bound(errors):
    # Independent [-e,e] added to real and imaginary parts gives full-cross
    # radius 2 sqrt(sum e_ab^2) <= 2 sum e_ab. No sqrt rounding is hidden.
    return 2*sum((x.abs_upper() for row in errors for x in row),ZERO)


@lru_cache(None)
def certified_rule(n:int):
    if type(n) is not int or not 1<=n<=128:raise ValueError('supported degree 1..128')
    import mpmath as mp
    from scipy.special import roots_legendre
    proposals=roots_legendre(n)[0]
    nodes=[]; receipts=[]
    bits=220; unit=1<<bits
    with mp.workdps(100):
        for a in proposals:
            x=mp.mpf(float(a))
            for _ in range(12):
                pn=legendre(n,x);pn1=legendre(n-1,x)
                derivative=n*(x*pn-pn1)/(x*x-1)
                dx=pn/derivative;x-=dx
                if abs(dx)<mp.mpf('1e-95'):break
            k=int(mp.floor(x*unit));lo=F(k-4,unit);hi=F(k+5,unit)
            sl=legendre(n,lo);sh=legendre(n,hi)
            if not (-1<lo<hi<1) or sl*sh>=0:raise ArithmeticError('exact root bracket failed')
            if nodes and F(nodes[-1].hi,SCALE)>=lo:raise ArithmeticError('overlapping root brackets')
            root=I.bounds(lo,hi); nodes.append(root)
            receipts.append({'lower':str(lo),'upper':str(hi),'P_lower_sign':1 if sl>0 else -1,'P_upper_sign':1 if sh>0 else -1})
    weights=[]
    for x in nodes:
        d=n*(x*legendre(n,x)-legendre(n-1,x))/(x*x-1)
        w=2/((1-x*x)*d*d)
        if w.lo<=0:raise ArithmeticError('nonpositive weight enclosure')
        weights.append(w)
    if not sum(weights,ZERO).contains(2):raise ArithmeticError('weight sum excludes 2')
    return tuple(nodes),tuple(weights),tuple(receipts)
