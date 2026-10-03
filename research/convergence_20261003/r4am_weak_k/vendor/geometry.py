"""Complete shell-pair distance polygons with affine-R vertices.

No sliver omission and no guessed topology. All half-plane signs are proved
uniformly on the registered separation interval before a triangle is emitted.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from dataclasses import dataclass
from math import atan2
from dyadic import I,SCALE

class TopologyError(ValueError):pass
@dataclass(frozen=True)
class Affine:
    a: F
    b: F=F(0)
    def at(self,R):return R*self.b+self.a
    def __add__(self,o):
        if not isinstance(o,Affine):o=Affine(F(o))
        return Affine(self.a+o.a,self.b+o.b)
    def __neg__(self):return Affine(-self.a,-self.b)
    def __sub__(self,o):return self+-o
    def scale(self,v):return Affine(self.a*v,self.b*v)
    def dump(self):return [str(self.a),str(self.b)]

def product(a,b):return [a.a*b.a,a.a*b.b+a.b*b.a,a.b*b.b]
def quadratic_range(c,R):
    lo,hi=F(R.lo,SCALE),F(R.hi,SCALE)
    f=lambda x:c[0]+c[1]*x+c[2]*x*x
    a=[f(lo),f(hi)]
    if c[2]:
        s=-c[1]/(2*c[2])
        if lo<=s<=hi:a.append(f(s))
    return I.bounds(min(a),max(a))

@dataclass(frozen=True)
class Triangle:
    i: int
    j: int
    vertices: tuple
    det_polynomial: tuple
    def det_range(self,R):return quadratic_range(self.det_polynomial,R)
    def dump(self):return {'i':self.i,'j':self.j,'vertices':[[x.dump(),y.dump()] for x,y in self.vertices],'det_R_polynomial':[str(x) for x in self.det_polynomial]}

def polygons(edges,R):
    e=tuple(F(x) for x in edges)
    if len(e)<2 or e[0]!=0 or any(a>=b for a,b in zip(e,e[1:])):raise ValueError('strict edges starting at 0')
    if R.lo<=0:raise TopologyError('coincident foci')
    # All nonzero sum/difference contacts must be outside the closed R domain.
    for a in e:
        for b in e:
            for c in (a+b,abs(a-b)):
                if c and R.contains(c):raise TopologyError('shell contact in R domain')
    out=[]
    for i,(a,b) in enumerate(zip(e,e[1:])):
      for j,(c,d) in enumerate(zip(e,e[1:])):
        hp=[(-1,0,Affine(-a)),(1,0,Affine(b)),(0,-1,Affine(-c)),(0,1,Affine(d)),
            (-1,-1,Affine(F(0),F(-1))),(1,-1,Affine(F(0),F(1))),(-1,1,Affine(F(0),F(1)))]
        vertices=[]
        for (ax,ay,q),(bx,by,t) in combinations(hp,2):
            det=ax*by-ay*bx
            if not det:continue
            x=(q.scale(by)-t.scale(ay)).scale(F(1,det))
            y=(t.scale(ax)-q.scale(bx)).scale(F(1,det))
            bad=False
            for px,py,rhs in hp:
                s=x.scale(px)+y.scale(py)-rhs
                if s.a==s.b==0:continue
                w=s.at(R)
                if w.lo>0:bad=True;break
                if w.hi>=0:raise TopologyError('unresolved affine constraint; no clipping by midpoint')
            if not bad and (x,y) not in vertices:vertices.append((x,y))
        if len(vertices)<3:continue
        mid=R.mid();pts=[(float(x.a+x.b*mid),float(y.a+y.b*mid)) for x,y in vertices]
        cx=sum(x for x,y in pts)/len(pts);cy=sum(y for x,y in pts)/len(pts)
        vertices=[v for _,v in sorted(zip([atan2(y-cy,x-cx) for x,y in pts],vertices),key=lambda a:a[0])]
        # Floating angles only propose the order. All vertices must stay on the
        # left of every oriented boundary edge throughout the R domain.
        for k in range(len(vertices)):
            va=vertices[k]; vb=vertices[(k+1)%len(vertices)]
            for vc in vertices:
                aa=product(vb[0]-va[0],vc[1]-va[1]);bb=product(vb[1]-va[1],vc[0]-va[0])
                pol=tuple(a-b for a,b in zip(aa,bb))
                if any(pol) and quadratic_range(pol,R).lo<0:
                    raise TopologyError('boundary order does not uniformly certify a convex cover')
        # Positive signed fan determinants then certify no overlap/sliver loss.
        for k in range(1,len(vertices)-1):
            v0,v1,v2=vertices[0],vertices[k],vertices[k+1]
            p=product(v1[0]-v0[0],v2[1]-v0[1]);q=product(v1[1]-v0[1],v2[0]-v0[0])
            detp=tuple(a-b for a,b in zip(p,q));rng=quadratic_range(detp,R)
            if rng.lo<=0:raise TopologyError('uncertified orientation or degenerate triangle')
            out.append(Triangle(i,j,(v0,v1,v2),detp))
    return out
