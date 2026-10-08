"""Complex rectangular interval arithmetic for holomorphy and magnitude bounds.

Uses the pinned R4AE 256-bit outward integer operations. No complex sqrt,
log or fractional power is used, so there is no concealed branch choice.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import factorial
from dyadic import I,ONE,ZERO,SCALE


def square(x):
    x=I(x)
    if x.lo<=0<=x.hi:return I.raw(0,(x.abs_upper()**2).hi)
    return x*x


def exp_positive(x):
    """Outward upper majorant e^x for x>=0, Taylor plus a geometric tail."""
    x=I(x).abs_upper()
    if x.hi>I(1024).hi:raise OverflowError('majorant exponent exceeds registered analytic cap')
    k=0;y=x
    while y.hi>I(F(1,2)).hi:y=y/2;k+=1
    s=ONE;t=ONE;N=80
    for j in range(1,N):t=t*y/j;s=s+t
    tail=(y**N)/factorial(N)/(ONE-y/(N+1))
    s=s+I.raw(0,tail.hi)
    for _ in range(k):s=s*s
    return s.abs_upper()


class C:
    __slots__=('re','im')
    def __init__(self,re=0,im=0):
        if isinstance(re,C):self.re,self.im=re.re,re.im
        else:self.re,self.im=I(re),I(im)
    def __add__(self,o):o=C(o);return C(self.re+o.re,self.im+o.im)
    __radd__=__add__
    def __neg__(self):return C(-self.re,-self.im)
    def __sub__(self,o):return self+-C(o)
    def __rsub__(self,o):return C(o)+-self
    def __mul__(self,o):
        o=C(o);return C(self.re*o.re-self.im*o.im,self.re*o.im+self.im*o.re)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=C(o);d=square(o.re)+square(o.im)
        if d.lo<=0:raise ZeroDivisionError('complex rectangle may contain a pole')
        return C((self.re*o.re+self.im*o.im)/d,(self.im*o.re-self.re*o.im)/d)
    def __rtruediv__(self,o):return C(o)/self
    def __pow__(self,n):
        if type(n) is not int or n<0:raise ValueError('nonnegative integer powers only')
        p=C(1);x=self
        while n:
            if n&1:p=p*x
            n//=2
            if n:x=x*x
        return p
    def mag(self):return (square(self.re)+square(self.im)).sqrt().abs_upper()


def ellipse_box(center,half,rho=F(2)):
    rho=F(rho)
    if half<=0 or rho<=1:raise ValueError('positive half-width and rho>1 required')
    xx=F(half)*(rho+1/rho)/2; yy=F(half)*(rho-1/rho)/2
    return C(I.bounds(F(center)-xx,F(center)+xx),I.bounds(-yy,yy))
