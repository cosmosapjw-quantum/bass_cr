"""Small outward Decimal interval and first-derivative algebra.
Basic ops use directed rounding. exp/ln use correctly rounded nearest Decimal
primitives plus one outward representable neighbor. No Decimal.power promise
is assumed: fractional powers are exp(p*ln(x)). This is not a generic solver.
"""
from decimal import Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
P=60
DOWN=Context(prec=P,rounding=ROUND_FLOOR,Emin=-999999,Emax=999999)
UP=Context(prec=P,rounding=ROUND_CEILING,Emin=-999999,Emax=999999)
NEAR=Context(prec=P,rounding=ROUND_HALF_EVEN,Emin=-999999,Emax=999999)
def dec(x):
    if isinstance(x,D): return x
    if isinstance(x,float): return D.from_float(x)
    return D(x)
class IV:
    __slots__=('lo','hi')
    def __init__(self,lo=0,hi=None):
        if isinstance(lo,IV): self.lo,self.hi=lo.lo,lo.hi;return
        self.lo=dec(lo);self.hi=dec(lo if hi is None else hi)
        if not self.lo.is_finite() or not self.hi.is_finite() or self.lo>self.hi:raise ValueError('invalid interval')
    def __add__(self,b):
        if isinstance(b,AD):return b+self
        b=IV(b);return IV(DOWN.add(self.lo,b.lo),UP.add(self.hi,b.hi))
    __radd__=__add__
    def __neg__(self):return IV(self.hi.copy_negate(),self.lo.copy_negate())
    def __sub__(self,b):return self+-b if isinstance(b,AD) else self+-IV(b)
    def __rsub__(self,b):return IV(b)+-self
    def __mul__(self,b):
        if isinstance(b,AD):return b*self
        b=IV(b);pairs=[(x,y) for x in (self.lo,self.hi) for y in (b.lo,b.hi)]
        return IV(min(DOWN.multiply(x,y) for x,y in pairs),max(UP.multiply(x,y) for x,y in pairs))
    __rmul__=__mul__
    def reciprocal(self):
        if self.lo<=0<=self.hi:raise ValueError('division through zero')
        return IV(DOWN.divide(D(1),self.hi),UP.divide(D(1),self.lo))
    def __truediv__(self,b):
        if isinstance(b,AD):return AD(self)*b.reciprocal()
        return self*IV(b).reciprocal()
    def __rtruediv__(self,b):return IV(b)*self.reciprocal()
    def exp(self):
        return IV(NEAR.next_minus(NEAR.exp(self.lo)),NEAR.next_plus(NEAR.exp(self.hi)))
    def ln(self):
        if self.lo<=0:raise ValueError('log domain')
        return IV(NEAR.next_minus(NEAR.ln(self.lo)),NEAR.next_plus(NEAR.ln(self.hi)))
    def __pow__(self,p):
        if isinstance(p,int) and p>=0:
            out=IV(1)
            for _ in range(p):out=out*self
            return out
        return (self.ln()*IV(p)).exp()
    def mag(self):return max(self.lo.copy_abs(),self.hi.copy_abs())
    def contains(self,x):return self.lo<=dec(x)<=self.hi
    def data(self):return [str(self.lo),str(self.hi)]
    def __repr__(self):return f'IV({self.lo},{self.hi})'
DIM=13
class AD:
    __slots__=('v','g')
    def __init__(self,v,g=None):self.v=IV(v);self.g=[IV(0) for _ in range(DIM)] if g is None else g
    @classmethod
    def var(cls,v,j):
        g=[IV(0) for _ in range(DIM)];g[j]=IV(1);return cls(v,g)
    def __add__(self,b):
        b=b if isinstance(b,AD) else AD(b);return AD(self.v+b.v,[x+y for x,y in zip(self.g,b.g)])
    __radd__=__add__
    def __neg__(self):return AD(-self.v,[-x for x in self.g])
    def __sub__(self,b):return self+-(b if isinstance(b,AD) else AD(b))
    def __rsub__(self,b):return AD(b)+-self
    def __mul__(self,b):
        b=b if isinstance(b,AD) else AD(b)
        return AD(self.v*b.v,[x*b.v+self.v*y for x,y in zip(self.g,b.g)])
    __rmul__=__mul__
    def reciprocal(self):return AD(1/self.v,[-x/(self.v*self.v) for x in self.g])
    def __truediv__(self,b):return self*(b if isinstance(b,AD) else AD(b)).reciprocal()
    def __rtruediv__(self,b):return AD(b)*self.reciprocal()
    def exp(self):
        e=self.v.exp();return AD(e,[e*x for x in self.g])
    def ln(self):return AD(self.v.ln(),[x/self.v for x in self.g])
    def __pow__(self,p):return (self.ln()*p).exp()
