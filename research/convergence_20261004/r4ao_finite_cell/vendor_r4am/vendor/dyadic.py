"""Outward fixed-point intervals. Endpoints are integers / 2**BITS.

Trust base: Python integer/Fraction/isqrt arithmetic, not libm rounding.
Objects are immutable. No NaN, infinity, implicit approximate conversions.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt, factorial
from functools import lru_cache
BITS = 256
SCALE = 1 << BITS

def ceildiv(a: int, b: int) -> int:
    return -((-a)//b)

class I:
    __slots__ = ('lo','hi')
    def __setattr__(self, n, v):
        if hasattr(self,n): raise AttributeError('immutable interval')
        object.__setattr__(self,n,v)
    def __init__(self, value=0):
        if isinstance(value,I): a,b=value.lo,value.hi
        else:
            f=F(value); a=(f.numerator*SCALE)//f.denominator
            b=ceildiv(f.numerator*SCALE,f.denominator)
        self.lo,self.hi=a,b
    @classmethod
    def raw(cls,a,b):
        if a>b: raise ValueError('reversed interval')
        o=object.__new__(cls);o.lo,o.hi=int(a),int(b);return o
    @classmethod
    def bounds(cls,a,b): return cls.raw(I(a).lo,I(b).hi)
    def __add__(self,b):
        b=I(b);return I.raw(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return I.raw(-self.hi,-self.lo)
    def __sub__(self,b):return self+-I(b)
    def __rsub__(self,b):return I(b)+-self
    def __mul__(self,b):
        b=I(b)
        if self.iszero() or b.iszero():return ZERO
        p=(self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi)
        return I.raw(min(p)//SCALE,ceildiv(max(p),SCALE))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=I(b)
        if b.lo<=0<=b.hi: raise ZeroDivisionError('interval divisor contains zero')
        if b.hi<0:return (-self)/(-b)
        low=min((x*SCALE)//y for x in (self.lo,self.hi) for y in (b.lo,b.hi))
        high=max(ceildiv(x*SCALE,y) for x in (self.lo,self.hi) for y in (b.lo,b.hi))
        return I.raw(low,high)
    def __rtruediv__(self,b):return I(b)/self
    def __pow__(self,n):
        if type(n) is not int: raise TypeError('integer powers only')
        if n<0:return ONE/(self**(-n))
        r=ONE;b=self
        while n:
            if n&1:r=r*b
            n//=2
            if n:b=b*b
        return r
    def sqrt(self):
        if self.lo<0:raise ValueError('negative interval in sqrt')
        a=isqrt(self.lo*SCALE);t=self.hi*SCALE;b=isqrt(t)
        return I.raw(a,b+(b*b<t))
    def abs_upper(self):return I.raw(max(abs(self.lo),abs(self.hi)),max(abs(self.lo),abs(self.hi)))
    def intersect(self,b):
        b=I(b);return I.raw(max(self.lo,b.lo),min(self.hi,b.hi))
    def contains(self,value):
        f=F(value);n=f.numerator*SCALE;d=f.denominator
        return self.lo*d<=n<=self.hi*d
    def contains_interval(self,b):return self.lo<=b.lo and self.hi>=b.hi
    def iszero(self):return self.lo==0==self.hi
    def mid(self):return F(self.lo+self.hi,2*SCALE)
    def radius(self):return F(self.hi-self.lo,2*SCALE)
    def width(self):return F(self.hi-self.lo,SCALE)
    def floats(self):return (float(F(self.lo,SCALE)),float(F(self.hi,SCALE)))
    def dump(self):return {'lower_numerator':str(self.lo),'upper_numerator':str(self.hi),'denominator_power2':BITS}
    @classmethod
    def load(cls,d):
        if d['denominator_power2']!=BITS:raise ValueError('precision mismatch')
        return cls.raw(int(d['lower_numerator']),int(d['upper_numerator']))
    def __repr__(self):return f'I{self.floats()}'
ZERO=I(0);ONE=I(1)

def sym(radius):
    r=I(radius).abs_upper().hi;return I.raw(-r,r)

@lru_cache(None)
def pi_interval():
    def atan(q):
        # Alternating exact rational series; next term encloses the remainder.
        n=128;s=sum((F((-1)**j,(2*j+1)*q**(2*j+1)) for j in range(n)),F(0))
        nxt=F(1,(2*n+1)*q**(2*n+1))
        return I.bounds(s,s+nxt) # n even: next term positive
    return 16*atan(5)-4*atan(239)

def sincos(x: I):
    """Real sine/cosine enclosure, with certified pi and Lipschitz widening."""
    x=I(x)
    if x.iszero():return ZERO,ONE
    if x.width()>=2:return I.bounds(-1,1),I.bounds(-1,1)
    c=I(x.mid());halfpi=pi_interval()/2
    k=round(c.mid()/halfpi.mid()) # any integer k gives an exact periodic identity
    y=c-k*halfpi;y2=y*y
    ts=y;tc=ONE;ss=y;cc=ONE
    N=48
    for j in range(1,N):
        ts=-(ts*y2)/((2*j)*(2*j+1));tc=-(tc*y2)/((2*j-1)*(2*j))
        ss=ss+ts;cc=cc+tc
    B=y.abs_upper();q=B*B/((2*N+1)*(2*N+2))
    if q.hi>=SCALE:raise ArithmeticError('trig tail ratio failed')
    rs=(B**(2*N+1))/factorial(2*N+1)/(ONE-q)
    rc=(B**(2*N))/factorial(2*N)/(ONE-q)
    ss=ss+sym(rs);cc=cc+sym(rc)
    ss,cc=((ss,cc),(cc,-ss),(-ss,-cc),(-cc,ss))[k%4]
    lim=I.bounds(-1,1);r=x.radius()
    return (ss+sym(r)).intersect(lim),(cc+sym(r)).intersect(lim)

def phi(n: int,x: I):
    """Phi_n(x)=sum x**j/[j!(j+n)!], real x<=0.

    Phi_n^(k)=Phi_(n+k). For x<=0 its normalized Poisson integral implies
    |Phi_n(x)|<=1/n!, and |Phi_n'(x)|<=1/(n+1)!.
    Midpoint series is widened by that global derivative bound.
    """
    if type(n) is not int or n<0:raise ValueError('nonnegative integer index')
    x=I(x)
    if x.hi>0:raise ValueError('physical Phi argument must be nonpositive')
    bnd=sym(F(1,factorial(n)))
    if x.iszero():return I(F(1,factorial(n)))
    # Wide interval: exact integral majorant avoids false cancellation estimates.
    if x.width()>F(1,2):return bnd
    m=I(x.mid());B=m.abs_upper();t=I(F(1,factorial(n)));s=t;N=128
    for j in range(1,N):
        t=t*m/(j*(j+n));s=s+t
    q=B/((N+1)*(N+1+n))
    if q.hi>=SCALE:raise ArithmeticError('Phi tail ratio failed')
    tail=B**N/factorial(N)/factorial(N+n)/(ONE-q)
    return (s+sym(tail)+sym(x.radius()/factorial(n+1))).intersect(bnd)
