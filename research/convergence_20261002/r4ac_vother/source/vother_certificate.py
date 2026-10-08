"""Certified same-center Coulomb projection for real s+p radial candidates.

Exact input floats define rational endpoint/bubble polynomials. Only radius
square roots and panel logarithms are nonrational; both have integer interval
bounds. Matrices are restricted to the registered x-z plane, not silently
extended to other angular conventions or geometries.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb
import numpy as np
from dyadic_interval import Interval as I


def validate_arrays(edges, endpoints, bubbles):
    if any(np.iscomplexobj(x) for x in (edges,endpoints,bubbles)):
        raise ValueError('real endpoint/bubble bank required')
    e,p,q=(np.asarray(x,dtype=np.float64) for x in (edges,endpoints,bubbles))
    if e.ndim!=1 or len(e)<2 or len(e)>4097 or e[0]!=0 or not np.isfinite(e).all() or np.any(np.diff(e)<=0):
        raise ValueError('finite increasing mesh from zero required')
    if p.ndim!=2 or not 1<=len(p)<=32 or p.shape[1]!=len(e) or q.shape!=(len(p),len(e)-1,3) or not np.isfinite(p).all() or not np.isfinite(q).all():
        raise ValueError('finite degree4 bank shape mismatch')
    return e,p,q

def local_coefficients(left,right,bubble):
    a,b=F(float(left)),F(float(right));q0,q1,q2=(F(float(x)) for x in bubble)
    return (a,b-a+q0,q1-q0,q2-q1,-q2)

def radial_polynomial(c, a, h):
    """Exact coefficients in r, not sampled/interpolated polynomial values."""
    return [sum((c[i]*comb(i,j)*(-a)**(i-j)/h**i for i in range(j,5)),F(0)) for j in range(5)]

class PolynomialBank:
    def __init__(self,edges,endpoints,bubbles):
        self.edges,self.endpoints,self.bubbles=validate_arrays(edges,endpoints,bubbles)
        self.nm=len(self.endpoints);self.ne=len(self.edges)-1
        self.qedges=tuple(F(float(x)) for x in self.edges)
        self.products=[]
        for e in range(self.ne):
            a=self.qedges[e];h=self.qedges[e+1]-a
            c=[radial_polynomial(local_coefficients(self.endpoints[i,e],self.endpoints[i,e+1],self.bubbles[i,e]),a,h) for i in range(self.nm)]
            self.products.append({(i,j):tuple(I.point(sum((c[i][k]*c[j][n-k] for k in range(5) if 0<=n-k<5),F(0))) for n in range(9)) for i in range(self.nm) for j in range(i,self.nm)})

    def radial(self, distance):
        R=I.point(distance)
        if R.lo<=0:raise ValueError('strictly separated centers required')
        z=I.point(0)
        out=[[[z for _ in range(self.nm)] for _ in range(self.nm)] for _ in range(3)]
        for e in range(self.ne):
            a,b=I.point(self.qedges[e]),I.point(self.qedges[e+1])
            if b.hi<=R.lo:parts=[(a,b,True)]
            elif a.lo>=R.hi:parts=[(a,b,False)]
            elif a.hi<R.lo and R.hi<b.lo:parts=[(a,R,True),(R,b,False)]
            else:raise ValueError('radius enclosure straddles a mesh boundary; refine arithmetic or split geometry')
            for x,y,inner in parts:
                if inner:
                    powers={n:(y**(n+1)-x**(n+1))/(n+1) for n in range(11)}
                else:
                    # Outer intervals are separated from zero. log is bounded
                    # on [1/2,2]; larger panel ratios require an explicit split.
                    powers={n:((y/x).log() if n==-1 else (y**(n+1)-x**(n+1))/(n+1)) for n in range(-3,8)}
                for ell in range(3):
                    factor=1/R**(ell+1) if inner else R**ell
                    for (i,j),p in self.products[e].items():
                        val=sum((p[k]*powers[k+ell if inner else k-ell-1] for k in range(9)),z)*factor
                        out[ell][i][j]=out[ell][i][j]+val
        # Exact integral symmetry, not projection of a computed raw operator.
        for ell in range(3):
            for i in range(self.nm):
                for j in range(i):out[ell][i][j]=out[ell][j][i]
        return out

def radial_certificate(edges,endpoints,bubbles,distance):
    return PolynomialBank(edges,endpoints,bubbles).radial(distance)

def geometry_interval(delta):
    d=np.asarray(delta,dtype=np.float64)
    if d.shape!=(3,) or not np.isfinite(d).all() or d[1]!=0:
        raise ValueError('finite x-z plane vector required by scoped adapter')
    dd=[I.point(F(float(x))) for x in d]
    R=sum((x*x for x in dd),I.point(0)).sqrt()
    if R.lo<=0:raise ValueError('strictly separated centers required')
    return R,[x/R for x in dd]

def projected_matrix(radial,lm,mode_indices,direction,charge=1.):
    """Exact finite angular projection in Condon-Shortley convention."""
    if any(l not in (0,1) or not -l<=m<=l for l,m in lm):raise ValueError('s+p required')
    if len(lm)!=len(mode_indices) or any(not 0<=i<len(radial[0]) for i in mode_indices):raise ValueError('channel map mismatch')
    z=I.point(0);n=len(lm);q=I.point(F(float(charge)))
    if q.lo<=0:raise ValueError('positive external nuclear charge required')
    if direction[1].lo!=0 or direction[1].hi!=0:raise ValueError('x-z plane required')
    v={-1:direction[0]/I.point(2).sqrt(),0:direction[2],1:-direction[0]/I.point(2).sqrt()}
    out=[[z for _ in range(n)] for _ in range(n)]
    for a,(la,ma) in enumerate(lm):
        for b,(lb,mb) in enumerate(lm):
            ia,ib=mode_indices[a],mode_indices[b];val=z
            if la==lb and ma==mb:val=val+radial[0][ia][ib]
            if la==0 and lb==1:val=val+radial[1][ia][ib]*v[mb]/I.point(3).sqrt()
            if la==1 and lb==0:val=val+radial[1][ia][ib]*v[ma]/I.point(3).sqrt()
            if la==lb==1:val=val+radial[2][ia][ib]*(3*v[ma]*v[mb]-int(ma==mb))/5
            out[a][b]=-q*val
    return out
