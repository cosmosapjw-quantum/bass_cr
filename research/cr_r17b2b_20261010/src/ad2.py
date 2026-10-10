"""State value/gradient/Hessian with directed interval scalar backend.
Hessians store actual second derivatives, not factorial coefficients.
"""
from interval_backend import I
class D2:
 def __init__(self,v,g=None,h=None):
  self.v=I(v);self.g=[I(0) for _ in range(4)] if g is None else g
  self.h=[[I(0) for _ in range(4)] for _ in range(4)] if h is None else h
 @classmethod
 def var(cls,v,j):
  row=[I(0) for _ in range(4)];row[j]=I(1);return cls(v,row)
 def __add__(self,b):
  b=b if isinstance(b,D2) else D2(b)
  return D2(self.v+b.v,[x+y for x,y in zip(self.g,b.g)],[[x+y for x,y in zip(ar,br)] for ar,br in zip(self.h,b.h)])
 __radd__=__add__
 def __neg__(self):return D2(-self.v,[-x for x in self.g],[[-x for x in row] for row in self.h])
 def __sub__(self,b):return self+-b if isinstance(b,D2) else self+-D2(b)
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  b=b if isinstance(b,D2) else D2(b)
  h=[[self.h[i][j]*b.v+self.v*b.h[i][j]+self.g[i]*b.g[j]+self.g[j]*b.g[i] for j in range(4)] for i in range(4)]
  return D2(self.v*b.v,[x*b.v+self.v*y for x,y in zip(self.g,b.g)],h)
 __rmul__=__mul__
 def compose(self,value,first,second):
  return D2(value,[first*x for x in self.g],[[second*self.g[i]*self.g[j]+first*self.h[i][j] for j in range(4)] for i in range(4)])
 def reciprocal(self):return self.compose(1/self.v,-1/(self.v*self.v),2/(self.v*self.v*self.v))
 def __truediv__(self,b):return self*(b if isinstance(b,D2) else D2(b)).reciprocal()
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):
  v=self.v.exp();return self.compose(v,v,v)
 def ln(self):return self.compose(self.v.ln(),1/self.v,-1/(self.v*self.v))
 def __pow__(self,p):return (self.ln()*p).exp()
