"""Directed Volterra slabs and correlation-preserving affine state storage."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
from interval_decimal import IV,D,UP,DOWN,NEAR

def total(v):
    return sum(v,IV(0))

def matvec(A,v):return [total(a*b for a,b in zip(row,v)) for row in A]
def transpose(A):return list(map(list,zip(*A)))
def center(v):return NEAR.divide(NEAR.add(v.lo,v.hi),D(2))
def symmetric(r):return IV(r.copy_negate(),r)
def intersect(a,b):return IV(max(a.lo,b.lo),min(a.hi,b.hi))

def volterra_tube(A,g,start,dt):
    """All-time slab using an outward Neumann/Picard radius, no point extrema."""
    if len(A)!=len(start) or any(len(row)!=len(start) for row in A) or len(g)!=len(start):
        raise ValueError('DIMENSION')
    if dt<=0:raise ValueError('CLOCK_LENGTH')
    M=[[a.mag() for a in row] for row in A]
    norm=max(sum((IV(v) for v in row),IV(0)).hi for row in M)
    q=UP.multiply(dt,norm)
    if q>=1:raise ValueError('VOL TERRA_CONTRACTION_FAIL')
    initial=matvec(A,start);forcing=[(a+b).mag() for a,b in zip(initial,g)]
    v=[UP.multiply(dt,f) for f in forcing];rho=list(v)
    for _ in range(6):
        v=[UP.multiply(dt,total(IV(a)*IV(b) for a,b in zip(row,v)).hi) for row in M]
        rho=[UP.add(a,b) for a,b in zip(rho,v)]
    tail=UP.divide(UP.multiply(q,max(v)),DOWN.subtract(D(1),q))
    rho=[UP.add(x,tail) for x in rho]
    tube=[x+symmetric(r) for x,r in zip(start,rho)]
    for _ in range(3):
        field=[x+y for x,y in zip(matvec(A,tube),g)]
        refinement=[x+IV(min(D(0),DOWN.multiply(dt,f.lo)),max(D(0),UP.multiply(dt,f.hi))) for x,f in zip(start,field)]
        tube=[intersect(x,y) for x,y in zip(tube,refinement)]
    return tube,rho,{'q':str(q),'neumann_terms':7,'tail_upper':str(tail)}

def backward_step(A,g,end,dt):
    At=transpose(A)
    tube,_,_=volterra_tube(At,g,end,dt)
    left=[x+IV(dt)*f for x,f in zip(end,[a+b for a,b in zip(matvec(At,tube),g)])]
    return left,tube

class Aff:
    def __init__(self,c=0,noise=None):self.c=IV(c);self.noise=dict(noise or {})
    def box(self):
        radius=total(IV(v.mag()) for v in self.noise.values()).hi
        return self.c+symmetric(radius)
    def __add__(self,b):
        if not isinstance(b,Aff):b=Aff(b)
        noises={k:self.noise.get(k,IV(0))+b.noise.get(k,IV(0)) for k in self.noise.keys()|b.noise.keys()}
        return Aff(self.c+b.c,{k:v for k,v in noises.items() if v.lo!=0 or v.hi!=0})
    def scale(self,a):return Aff(self.c*IV(a),{k:v*IV(a) for k,v in self.noise.items()})
    def add_box(self,v,label):
        c=center(v);r=(v-IV(c)).mag()
        return self+Aff(c,{label:IV(r)})
    def compress(self,label):
        keep={k:v for k,v in self.noise.items() if k.startswith('theta_birth')}
        radius=total(IV(v.mag()) for k,v in self.noise.items() if k not in keep).hi
        if radius:keep[label]=IV(radius)
        return Aff(self.c,keep)

def birth_transpose(lam,old_dimension):
    if len(lam) not in (old_dimension,old_dimension+1):raise ValueError('BIRTH_DIMENSION')
    return list(lam[:old_dimension])
