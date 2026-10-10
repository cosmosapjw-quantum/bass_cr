"""Separate MPFR256 directed arithmetic; shared physical RHS is explicit."""
import sys,json,argparse
from pathlib import Path
import gmpy2 as g
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
DOWN=g.context(precision=256,round=g.RoundDown);UP=g.context(precision=256,round=g.RoundUp)
def op(ctx,fn):
 with g.context(ctx):return fn()
class M:
 def __init__(self,a=0,b=None):
  if isinstance(a,M):self.lo,self.hi=a.lo,a.hi;return
  bb=a if b is None else b
  self.lo=op(DOWN,lambda:g.mpfr(a if isinstance(a,(float,int,g.mpfr)) else str(a)))
  self.hi=op(UP,lambda:g.mpfr(bb if isinstance(bb,(float,int,g.mpfr)) else str(bb)))
  if not g.is_finite(self.lo) or not g.is_finite(self.hi) or self.lo>self.hi:raise ValueError('FINITE_ORDERED')
 def __add__(self,b):
  if (isinstance(b,G) or hasattr(b,'h')):return b+self
  b=M(b);return ends(op(DOWN,lambda:self.lo+b.lo),op(UP,lambda:self.hi+b.hi))
 __radd__=__add__
 def __neg__(self):return ends(op(DOWN,lambda:-self.hi),op(UP,lambda:-self.lo))
 def __sub__(self,b):return self+-b if (isinstance(b,G) or hasattr(b,'h')) else self+-M(b)
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  if (isinstance(b,G) or hasattr(b,'h')):return b*self
  b=M(b);pairs=[(x,y) for x in (self.lo,self.hi) for y in (b.lo,b.hi)]
  return ends(min(op(DOWN,lambda:x*y) for x,y in pairs),max(op(UP,lambda:x*y) for x,y in pairs))
 __rmul__=__mul__
 def reciprocal(self):
  if self.lo<=0<=self.hi:raise ValueError('ZERO_DIVISION')
  return ends(op(DOWN,lambda:1/self.hi),op(UP,lambda:1/self.lo))
 def __truediv__(self,b):return self*(b.reciprocal() if (isinstance(b,(M,G)) or hasattr(b,'h')) else M(b).reciprocal())
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):return ends(op(DOWN,lambda:g.exp(self.lo)),op(UP,lambda:g.exp(self.hi)))
 def ln(self):
  if self.lo<=0:raise ValueError('LOG_DOMAIN')
  return ends(op(DOWN,lambda:g.log(self.lo)),op(UP,lambda:g.log(self.hi)))
 def __pow__(self,p):
  if isinstance(p,int) and p>=0:
   v=M(1)
   for _ in range(p):v=v*self
   return v
  return (self.ln()*M(p)).exp()
 def mag(self):return max(op(UP,lambda:abs(self.lo)),op(UP,lambda:abs(self.hi)))
 def data(self):
  # Emit safe base10 intervals widened by one MPFR step first. 80 decimal
  # digits exceed 256-bit precision and do not erase the extra MPFR ulp.
  return [format(op(DOWN,lambda:g.next_below(self.lo)),'.82g'),format(op(UP,lambda:g.next_above(self.hi)),'.82g')]
def ends(a,b):
 v=object.__new__(M);v.lo,v.hi=a,b;assert a<=b;return v
class G:
 def __init__(self,v,grad=None):self.v=M(v);self.g=[M(0)]*4 if grad is None else grad
 @classmethod
 def variable(cls,v,j):
  row=[M(0) for _ in range(4)];row[j]=M(1);return cls(v,row)
 def __add__(self,b):
  b=b if (isinstance(b,G) or hasattr(b,'h')) else G(b);return G(self.v+b.v,[x+y for x,y in zip(self.g,b.g)])
 __radd__=__add__
 def __neg__(self):return G(-self.v,[-v for v in self.g])
 def __sub__(self,b):return self+-b if (isinstance(b,G) or hasattr(b,'h')) else self+-G(b)
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  b=b if (isinstance(b,G) or hasattr(b,'h')) else G(b);return G(self.v*b.v,[x*b.v+self.v*y for x,y in zip(self.g,b.g)])
 __rmul__=__mul__
 def reciprocal(self):return G(self.v.reciprocal(),[-v/(self.v*self.v) for v in self.g])
 def __truediv__(self,b):return self*(b if (isinstance(b,G) or hasattr(b,'h')) else G(b)).reciprocal()
 def __rtruediv__(self,b):return self.reciprocal()*b
 def exp(self):
  v=self.v.exp();return G(v,[v*x for x in self.g])
 def ln(self):return G(self.v.ln(),[x/self.v for x in self.g])
 def __pow__(self,p):return (self.ln()*p).exp()

def check():
 import homotopy as hm,interval_rhs as rhs,ad2 as ad,interval_backend as ib
 original=hm.compute()
 hm.I=rhs.I=ad.I=ib.I=M
 independent=hm.compute()
 checks=0
 for name in ['nonphoto_Jacobian','nonphoto_Hessian']:
  def walk(a,b):
   nonlocal checks
   if isinstance(a[0],list):
    for x,y in zip(a,b):walk(x,y)
   else:
    x=M(*a);y=M(*b);assert max(x.lo,y.lo)<=min(x.hi,y.hi),(name,a,b);checks+=1
  walk(original[name],independent[name])
 with g.context(precision=300):
  for name in ['q_contraction','source_signed_interval_candidate','source_nonlinearity_nominal_tangent_remainder_radius','mixed_g_source_gain','full_gas_path_Hessian_majorant']:
   a=[g.mpfr(x) for x in original[name]];b=[g.mpfr(x) for x in independent[name]]
   assert max(abs(x-y) for x,y in zip(a,b))<g.mpfr('1e-68');checks+=1
 return dict(status='WHOLE_CONTINUUM_HOMOTOPY_AND_SECOND_VARIATION_MPFR_PASS',checks=checks,shared_RHS_formula=True,independent_directed_arithmetic=True,independent=independent)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();r=check()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(r['status'],r['checks'])
