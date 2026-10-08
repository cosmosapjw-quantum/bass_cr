"""Small, auditable outward-rounded interval arithmetic on a fixed dyadic grid.

All endpoints are integers divided by 2**320. No floating-point operation is
used in the interval algebra, square root, or log certificate. log is restricted
to [1/2,2], the only ratios needed by the registered exterior panels. This is
not a general-purpose validated-numerics library.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt

BITS = 320
SCALE = 1 << BITS
LOG_TERMS = 120

def _ceildiv(a: int, b: int) -> int:
    if b < 0: a,b=-a,-b
    return -((-a)//b)

@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int

    def __post_init__(self):
        if not isinstance(self.lo,int) or not isinstance(self.hi,int) or self.lo>self.hi:
            raise ValueError('ordered integer endpoints required')

    @classmethod
    def point(cls, x):
        if isinstance(x, cls): return x
        q=F(x)
        return cls(q.numerator*SCALE//q.denominator,
                   _ceildiv(q.numerator*SCALE,q.denominator))

    @classmethod
    def bounds(cls, lo, hi):
        a,b=F(lo),F(hi)
        if a>b:raise ValueError('reversed bounds')
        return cls(cls.point(a).lo,cls.point(b).hi)

    def fractions(self): return F(self.lo,SCALE),F(self.hi,SCALE)
    def width(self): return F(self.hi-self.lo,SCALE)
    def contains(self,x):
        q=F(x);return self.lo*q.denominator<=q.numerator*SCALE<=self.hi*q.denominator
    def midpoint(self):return F(self.lo+self.hi,2*SCALE)
    def __add__(self,x):
        x=Interval.point(x);return Interval(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,x):return self+-Interval.point(x)
    def __rsub__(self,x):return Interval.point(x)+-self
    def __mul__(self,x):
        x=Interval.point(x)
        p=(self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi)
        return Interval(min(p)//SCALE,_ceildiv(max(p),SCALE))
    __rmul__=__mul__
    def reciprocal(self):
        if self.lo<=0<=self.hi:raise ZeroDivisionError('interval contains zero')
        return Interval((SCALE*SCALE)//self.hi,_ceildiv(SCALE*SCALE,self.lo))
    def __truediv__(self,x):return self*Interval.point(x).reciprocal()
    def __rtruediv__(self,x):return Interval.point(x)*self.reciprocal()
    def __pow__(self,n):
        if not isinstance(n,int):raise TypeError('integer exponent required')
        if n<0:return self.reciprocal()**(-n)
        y=Interval.point(1);x=self
        while n:
            if n&1:y=y*x
            n//=2
            if n:x=x*x
        return y
    def sqrt(self):
        if self.lo<0:raise ValueError('sqrt of negative interval')
        a=isqrt(self.lo*SCALE);b=isqrt(self.hi*SCALE)
        if b*b<self.hi*SCALE:b+=1
        return Interval(a,b)
    def abs_upper(self):return F(max(abs(self.lo),abs(self.hi)),SCALE)
    def log(self):return _log_interval(self.lo,self.hi)
    def record(self):
        lo,hi=self.fractions();return [str(lo),str(hi)]

@lru_cache(maxsize=4096)
def _log_interval(lo: int, hi: int) -> Interval:
    x=Interval(lo,hi)
    if lo<SCALE//2 or hi>2*SCALE:
        raise ValueError('certified log supports only [1/2,2]')
    if lo==hi==SCALE:return Interval.point(0)
    t=(x-1)/(x+1);t2=t*t;power=t;acc=Interval.point(0)
    for n in range(LOG_TERMS):
        acc=acc+power/(2*n+1);power=power*t2
    # Uniform absolute remainder, valid also for a negative t interval.
    a=Interval.point(t.abs_upper())
    remainder=2*(a**(2*LOG_TERMS+1))/((2*LOG_TERMS+1)*(1-a*a))
    s=2*acc
    return Interval(s.lo-remainder.hi,s.hi+remainder.hi)

def sqrt_bounds(x):return Interval.point(x).sqrt().fractions()
def log_bounds(x):return Interval.point(x).log().fractions()

def error_upper(z: complex, real: Interval) -> F:
    """Certified bound for |z-exact_real|; includes any spurious imaginary part."""
    zr,zi=F(float(z.real)),F(float(z.imag));lo,hi=real.fractions()
    a=max(abs(zr-lo),abs(zr-hi));q=a*a+zi*zi
    return Interval.point(q).sqrt().fractions()[1]

def upward_float(q: F) -> float:
    import math
    x=float(q)
    if F(x)<q:x=math.nextafter(x,math.inf)
    return x
