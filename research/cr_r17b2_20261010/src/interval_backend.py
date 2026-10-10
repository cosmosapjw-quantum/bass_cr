"""Directed Decimal80 intervals, state gradients, and birth Taylor jets.
exp/ln Decimal correctly-rounded primitives are widened one representable step.
No sample extremum defines an interval. MPFR checks are separate code.
Jets store c_r=f^(r)/r!; derivatives() restores the factorial once.
"""
from decimal import Decimal as D,Context,ROUND_FLOOR,ROUND_CEILING,ROUND_HALF_EVEN
from math import factorial
DN=Context(prec=80,rounding=ROUND_FLOOR);UP=Context(prec=80,rounding=ROUND_CEILING);RN=Context(prec=80,rounding=ROUND_HALF_EVEN)
def d(x):
 if isinstance(x,D):return x
 if isinstance(x,float):return D.from_float(x)
 return D(x)
class I:
 def __init__(self,a=0,b=None):
  if isinstance(a,I):self.lo,self.hi=a.lo,a.hi;return
  self.lo=d(a);self.hi=d(a if b is None else b)
  if not self.lo.is_finite() or not self.hi.is_finite() or self.lo>self.hi:raise ValueError('ORDERED_FINITE_INTERVAL')
 def __add__(self,b):
  if isinstance(b,(AD,Jet)):return b+self
  b=I(b);return I(DN.add(self.lo,b.lo),UP.add(self.hi,b.hi))
 __radd__=__add__
 def __neg__(self):return I(self.hi.copy_negate(),self.lo.copy_negate())
 def __sub__(self,b):return self+-b if isinstance(b,(AD,Jet)) else self+-I(b)
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  if isinstance(b,(AD,Jet)):return b*self
  b=I(b);v=[(x,y) for x in (self.lo,self.hi) for y in (b.lo,b.hi)]
  return I(min(DN.multiply(x,y) for x,y in v),max(UP.multiply(x,y) for x,y in v))
 __rmul__=__mul__
 def reciprocal(self):
  if self.lo<=0<=self.hi:raise ValueError('ZERO_DIVISION')
  return I(DN.divide(D(1),self.hi),UP.divide(D(1),self.lo))
 def __truediv__(self,b):return self*(b.reciprocal() if isinstance(b,(I,AD,Jet)) else I(b).reciprocal())
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):return I(RN.next_minus(RN.exp(self.lo)),RN.next_plus(RN.exp(self.hi)))
 def ln(self):
  if self.lo<=0:raise ValueError('LOG_DOMAIN')
  return I(RN.next_minus(RN.ln(self.lo)),RN.next_plus(RN.ln(self.hi)))
 def __pow__(self,p):
  if isinstance(p,int) and p>=0:
   v=I(1)
   for _ in range(p):v=v*self
   return v
  return (self.ln()*I(p)).exp()
 def contains(self,x):return self.lo<=d(x)<=self.hi
 def mag(self):return max(self.lo.copy_abs(),self.hi.copy_abs())
 def data(self):return [str(self.lo),str(self.hi)]

class AD:
 def __init__(self,v,g=None):self.v=I(v);self.g=[I(0) for _ in range(4)] if g is None else g
 @classmethod
 def variable(cls,v,j):
  g=[I(0) for _ in range(4)];g[j]=I(1);return cls(v,g)
 def __add__(self,b):
  b=b if isinstance(b,AD) else AD(b);return AD(self.v+b.v,[x+y for x,y in zip(self.g,b.g)])
 __radd__=__add__
 def __neg__(self):return AD(-self.v,[-x for x in self.g])
 def __sub__(self,b):return self+-b if isinstance(b,AD) else self+-AD(b)
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  b=b if isinstance(b,AD) else AD(b);return AD(self.v*b.v,[x*b.v+self.v*y for x,y in zip(self.g,b.g)])
 __rmul__=__mul__
 def reciprocal(self):return AD(self.v.reciprocal(),[-x/(self.v*self.v) for x in self.g])
 def __truediv__(self,b):return self*(b if isinstance(b,AD) else AD(b)).reciprocal()
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):
  v=self.v.exp();return AD(v,[v*x for x in self.g])
 def ln(self):return AD(self.v.ln(),[x/self.v for x in self.g])
 def __pow__(self,p):return (self.ln()*p).exp()

class Jet:
 N=4
 def __init__(self,c):self.c=[I(x) for x in c]+[I(0)]*(self.N+1-len(c))
 @classmethod
 def variable(cls,v):return cls([v,1])
 def __add__(self,b):
  b=b if isinstance(b,Jet) else Jet([b]);return Jet([x+y for x,y in zip(self.c,b.c)])
 __radd__=__add__
 def __neg__(self):return Jet([-x for x in self.c])
 def __sub__(self,b):return self+-b if isinstance(b,Jet) else self+-Jet([b])
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  b=b if isinstance(b,Jet) else Jet([b]);return Jet([sum((self.c[j]*b.c[k-j] for j in range(k+1)),I(0)) for k in range(self.N+1)])
 __rmul__=__mul__
 def reciprocal(self):
  v=[self.c[0].reciprocal()]
  for k in range(1,self.N+1):v.append(-sum((self.c[j]*v[k-j] for j in range(1,k+1)),I(0))/self.c[0])
  return Jet(v)
 def __truediv__(self,b):return self*(b if isinstance(b,Jet) else Jet([b])).reciprocal()
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):
  v=[self.c[0].exp()]
  for k in range(1,self.N+1):v.append(sum((j*self.c[j]*v[k-j] for j in range(1,k+1)),I(0))/k)
  return Jet(v)
 def ln(self):
  q=Jet([self.c[k+1]*(k+1) if k<self.N else I(0) for k in range(self.N+1)])/self
  return Jet([self.c[0].ln()]+[q.c[k-1]/k for k in range(1,self.N+1)])
 def __pow__(self,p):
  if isinstance(p,int) and p>=0:
   v=Jet([1])
   for _ in range(p):v=v*self
   return v
  return (self.ln()*p).exp()
 def derivatives(self):return [c*factorial(k) for k,c in enumerate(self.c)]
