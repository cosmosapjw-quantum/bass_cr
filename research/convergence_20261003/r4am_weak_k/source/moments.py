"""Degree-four azimuthal moment closures without sqrt(Q) branches.

All value enclosures use the immutable 256-bit dyadic arithmetic. Complex
majorants are distinct from real-path evaluations and prove no accuracy alone.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import factorial,comb
from dyadic import I,ZERO,ONE,phi
from complex_box import C,square,exp_positive

def _check(a:int,b:int)->None:
    if type(a) is not int or type(b) is not int or min(a,b)<0 or a+b>4:
        raise ValueError('registered angular total degree is 0..4')

def _u(n,Q,k):
    x=-(square(k)*Q)/4
    out=ZERO
    for j in range(n//2+1):
        out=out+F(factorial(n),factorial(n-2*j)*factorial(j))*phi(n-j,x)*((-k*Q/2)**(n-2*j))*((-Q/4)**j)
    return C(out)*[C(1),C(0,-1),C(-1),C(0,1)][n%4]

def moment(a:int,b:int,Q,k)->C:
    """Enclose <U^a V^b exp(i k U)>; real Q>=0 and U²+V²=Q."""
    _check(a,b);Q=I(Q);k=I(k)
    if Q.lo<0:raise ValueError('Q must be proved nonnegative on the real path')
    if b%2:return C()
    s=b//2;out=C()
    for j in range(s+1):out=out+_u(a+2*j,Q,k)*(((-1)**j)*comb(s,j))*(Q**(s-j))
    return out

def moment_upper(a:int,b:int,Q,k)->I:
    """Holomorphic modulus majorant, valid for complex rectangular Q,k."""
    _check(a,b)
    if b%2:return ZERO
    qm=C(Q).mag();km=C(k).mag();x=qm*km*km/4
    ph=exp_positive(2*x.sqrt())
    def u(n):
        return sum((F(factorial(n),factorial(n-2*j)*factorial(j)*factorial(n-j))*ph*((km*qm/2)**(n-2*j))*((qm/4)**j) for j in range(n//2+1)),ZERO)
    s=b//2
    return sum((comb(s,j)*(qm**(s-j))*u(a+2*j) for j in range(s+1)),ZERO).abs_upper()

class P:
    """Sparse polynomial in transverse U,V with complex interval coefficients."""
    __slots__=('terms',)
    def __init__(self,value=0):
        if isinstance(value,P):self.terms=value.terms.copy();return
        if isinstance(value,dict):
            self.terms={}
            for ab,c in value.items():
                if len(ab)!=2 or any(type(x) is not int or x<0 for x in ab):raise ValueError('bad exponent')
                q=C(c)
                if not(q.re.iszero() and q.im.iszero()):self.terms[ab]=q
        else:
            c=C(value);self.terms={} if c.re.iszero() and c.im.iszero() else {(0,0):c}
    def __add__(self,b):
        b=P(b);d=self.terms.copy()
        for ab,c in b.terms.items():d[ab]=d.get(ab,C())+c
        return P(d)
    __radd__=__add__
    def __neg__(self):return P({ab:-c for ab,c in self.terms.items()})
    def __sub__(self,b):return self+-P(b)
    def __rsub__(self,b):return P(b)+-self
    def __mul__(self,b):
        b=P(b);d={}
        for (a,c),v in self.terms.items():
            for (bb,e),w in b.terms.items():
                key=(a+bb,c+e);d[key]=d.get(key,C())+v*w
        return P(d)
    __rmul__=__mul__
    def __truediv__(self,b):
        if isinstance(b,P):raise TypeError('polynomial denominators are not supported')
        return P({ab:c/C(b) for ab,c in self.terms.items()})
    def __pow__(self,n):
        if type(n) is not int or n<0:raise ValueError('nonnegative integer powers')
        r=P(1)
        for _ in range(n):r=r*self
        return r
    def evaluate(self,u,v):
        return sum((c*(C(u)**a)*(C(v)**b) for (a,b),c in self.terms.items()),C())
    def average(self,Q,k):
        return sum((c*moment(a,b,Q,k) for (a,b),c in self.terms.items()),C())
    def majorant(self,Q,k):
        return sum((c.mag()*moment_upper(a,b,Q,k) for (a,b),c in self.terms.items()),ZERO).abs_upper()
    @property
    def degree(self):return max((sum(ab) for ab in self.terms),default=0)
U=P({(1,0):C(1)});V=P({(0,1):C(1)})

def dot(a,b):
    if len(a)!=len(b):raise ValueError('dimension mismatch')
    return sum((P(x)*P(y) for x,y in zip(a,b)),P())
