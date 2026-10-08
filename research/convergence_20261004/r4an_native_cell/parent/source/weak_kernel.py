"""Origin-safe weak H,D,K cross kernels for the finite s+p atomic candidate.

Coordinates carry complex rectangular intervals for analytic majorants, but
conjugation is applied ONLY to the constant target harmonic coefficients.
No global strong Laplacian and no implicit integration by parts are used.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import numpy as np
from dyadic import I,SCALE,ZERO,sincos
from complex_box import C,exp_positive
from geometry import polygons,Triangle,TopologyError
from moments import P,U,V,dot

@dataclass(frozen=True)
class Candidate:
    edges:tuple
    coeffs:tuple
    ells:tuple
    identity:str
    profile:str='SYNTHETIC_FIXTURE'
    @property
    def channels(self):return tuple((a,l,m) for a,l in enumerate(self.ells) for m in range(-l,l+1))
    @classmethod
    def load(cls,path,metadata):
        meta=json.loads(Path(metadata).read_text())
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=meta['candidate_npz_sha256']:raise ValueError('candidate bytes mismatch')
        with np.load(path,allow_pickle=False) as d:
            e=d['edges'];p=d['shared_endpoint_values'];b=d['bubble_coefficients']
            if e.shape!=(41,) or p.shape!=(5,41) or b.shape!=(5,40,3):raise ValueError('unregistered shape')
            if not all(np.isfinite(x).all() for x in (e,p,b)):raise ValueError('nonfinite candidate')
            if e[0]!=0 or np.any(e[1:]<=e[:-1]) or np.any(p[:,0]!=0) or np.any(p[:,-1]!=0):raise ValueError('invalid edges/endpoints')
            coeff=[]
            for a in range(5):
                row=[]
                for j in range(40):
                    L,R=map(lambda x:F(float(x)),p[a,j:j+2]);q0,q1,q2=map(lambda x:F(float(x)),b[a,j])
                    row.append((L,R-L+q0,q1-q0,q2-q1,-q2))
                coeff.append(tuple(row))
        ell=tuple(x['l'] for x in meta['modes'])
        if ell!=(0,0,0,1,1):raise ValueError('registered full multiplets required')
        return cls(tuple(F(float(x)) for x in e),tuple(coeff),ell,meta['identity'],'FINITE_CANDIDATE')
    def radial(self,a,j,r):
        if not 0<=a<len(self.ells) or not 0<=j<len(self.edges)-1:raise ValueError('mode/panel out of range')
        r=C(r);lo,hi=self.edges[j:j+2];d=hi-lo;s=(r-lo)/d;c=self.coeffs[a][j]
        u=C();du=C()
        for q in reversed(c):u=u*s+q
        for k in range(len(c)-1,0,-1):du=du*s+k*c[k]
        return u,du/d
    def first_F(self,a,r):
        """Exact F=u/r and F'=dF/dr for the first panel, including r=0."""
        c=self.coeffs[a][0];d=self.edges[1]
        if self.edges[0]!=0 or c[0]!=0:raise ValueError('first-panel zero trace is required')
        s=C(r)/d;val=C();der=C()
        for q in reversed(c[1:]):val=val*s+q
        for k in range(len(c)-1,1,-1):der=der*s+(k-1)*c[k]
        return val/d,der/(d*d)

@dataclass(frozen=True)
class Context:
    b:F
    z:F
    v:F
    t:F
    def __post_init__(self):
        for n in ('b','z','v','t'):object.__setattr__(self,n,F(getattr(self,n)))
        if self.b<0 or self.v<0 or self.b*self.b+self.z*self.z==0:raise ValueError('noncoincident nonnegative speed/frame required')
    @property
    def R(self):return I(self.b*self.b+self.z*self.z).sqrt()
    @property
    def nu(self):return self.v*self.v/2

@dataclass(frozen=True)
class Cell:
    kind:str
    i:int
    j:int
    triangle:Triangle|None=None
    def dump(self):return {'kind':self.kind,'i':self.i,'j':self.j,'triangle':self.triangle.dump() if self.triangle else None}

def cover(candidate:Candidate,R:I):
    """Exact replacement of first-panel shell regions by two origin charts."""
    a=candidate.edges[1]
    if I(2*a).hi>=R.lo:raise TopologyError('first-panel origin balls overlap')
    ann=R+I.bounds(-a,a)
    js=[j for j in range(1,len(candidate.edges)-1) if I(candidate.edges[j]).hi<ann.lo and ann.hi<I(candidate.edges[j+1]).lo]
    if len(js)!=1:raise TopologyError('remote origin annulus crosses a radial interface')
    j=js[0];tris=polygons(candidate.edges,R)
    retained=[];replaced=[]
    for tri in tris:
        if tri.i==0 or tri.j==0:
            if (tri.i,tri.j) not in ((0,j),(j,0)):raise TopologyError('unexpected origin shell pair')
            replaced.append(tri)
        else:retained.append(Cell('regular',tri.i,tri.j,tri))
    # In the distance plane each origin region has exact area a². This is
    # checked coefficient-by-coefficient, uniformly in R, not at its midpoint.
    for pair in ((0,j),(j,0)):
        sums=[sum((t.det_polynomial[k]/2 for t in replaced if (t.i,t.j)==pair),F(0)) for k in range(3)]
        if sums!=[a*a,F(0),F(0)]:raise TopologyError('origin replacement area identity failed')
    if not replaced:raise TopologyError('missing origin region')
    cells=retained+[Cell('origin_T',0,j),Cell('origin_P',j,0)]
    return cells,{'original_triangles':len(tris),'regular_triangles':len(retained),'replaced_origin_triangles':len(replaced),'origin_charts':2,'dropped_regions':0,'remote_panel':j,'origin_radius_a0':str(a),'distance_plane_origin_area_each':str(a*a),'remote_annulus':ann.dump(),'uniform_R':R.dump(),'cover_sha256':hashlib.sha256(json.dumps([x.dump() for x in cells],sort_keys=True).encode()).hexdigest()}

def harmonic_vector(l,m,conjugated=False):
    if (l,m)==(0,0):return None
    if l!=1 or m not in (-1,0,1):raise ValueError('only s+p harmonics are registered')
    r3=I(3).sqrt();r32=I(F(3,2)).sqrt()
    if m==0:return (C(),C(),C(r3))
    return (C(r32 if m==-1 else -r32),C(0,r32 if conjugated else -r32),C())

def regular_field(candidate,a,j,r,x,m,conjugated=False):
    l=candidate.ells[a];c=harmonic_vector(l,m,conjugated);u,du=candidate.radial(a,j,r)
    r=C(r);q=u/(r**(l+1));qr=du/(r**(l+1))-(l+1)*u/(r**(l+2))
    g=P(1) if c is None else dot(c,x)
    val=g*q
    grad=[g*x[k]*(qr/r)+(P() if c is None else P(c[k])*q) for k in range(3)]
    return val,grad

def origin_field(candidate,a,r,n,m,conjugated=False):
    """Return field and r*gradient, with no origin denominator."""
    l=candidate.ells[a];c=harmonic_vector(l,m,conjugated);f,fp=candidate.first_F(a,r)
    if c is None:return P(f),[P(x)*(C(r)*fp) for x in n]
    g=dot(c,n)
    return g*f,[g*n[k]*(C(r)*fp)+(P(c[k])-g*n[k])*f for k in range(3)]

@dataclass
class Kernel:
    polys:dict
    Q:C
    k:C
    phase:C
    prefactor:C
    real_path_certified:bool
    def value(self):
        if not self.real_path_certified:raise ValueError("value requested outside a real unit-square path")
        if not(self.Q.im.iszero() and self.k.im.iszero() and self.phase.im.iszero()):raise ValueError('real path required for a value enclosure')
        # In these validated real coordinate charts, Q is nonnegative. The
        # intersection removes interval dependency around collinear Q=0 only.
        if self.Q.re.hi<0:raise ValueError('inconsistent physical Q')
        Q=I.raw(max(0,self.Q.re.lo),self.Q.re.hi)
        sn,cs=sincos(self.phase.re);factor=C(cs,sn)*self.prefactor
        return {key:p.average(Q,self.k.re)*factor for key,p in self.polys.items()}
    def upper(self):
        factor=self.prefactor.mag()*exp_positive(self.phase.im.abs_upper())
        return {key:p.majorant(self.Q,self.k)*factor for key,p in self.polys.items()}

def kernel(candidate:Candidate,cell:Cell,ctx:Context,u,w,a:int,b:int,ma:int,mb:int):
    """Raw normalized cross kernel. u,w always in the reference unit square.

    For the reverse block, K_PT = H_TP^dagger because the T columns are static.
    This defines the exact model and does not symmetrize any saved arrays.
    """
    u,w=C(u),C(w)
    real_path=(u.im.iszero() and w.im.iszero() and 0<=u.re.lo<=u.re.hi<=SCALE and 0<=w.re.lo<=w.re.hi<=SCALE)
    if cell.kind=='origin_T' and cell.i!=0:raise ValueError('origin_T panel identity')
    if cell.kind=='origin_P' and cell.j!=0:raise ValueError('origin_P panel identity')
    R=C(ctx.R);ex=C(ctx.b)/R;ez=C(ctx.z)/R
    e=(ex,C(),ez);e1=(-ez,C(),ex);e2=(C(),C(-1),C())
    xtrans=[U*e1[k]+V*e2[k] for k in range(3)]
    v=ctx.v;nu=ctx.nu
    if cell.kind=='regular':
        if cell.triangle is None or min(cell.i,cell.j)<1:raise ValueError('regular cell must exclude both origins')
        tri=cell.triangle;pts=[(C(x.at(ctx.R)),C(y.at(ctx.R))) for x,y in tri.vertices]
        r0=pts[0][0]+u*(pts[1][0]-pts[0][0]+w*(pts[2][0]-pts[1][0]))
        r1=pts[0][1]+u*(pts[1][1]-pts[0][1]+w*(pts[2][1]-pts[1][1]))
        A=(r0*r0-r1*r1+R*R)/(2*R)
        xt=[P(A*e[k])+xtrans[k] for k in range(3)]
        xp=[xt[k]-R*e[k] for k in range(3)]
        ft,gt=regular_field(candidate,a,cell.i,r0,xt,ma,True)
        fp,gp=regular_field(candidate,b,cell.j,r1,xp,mb,False)
        product=ft*fp
        h=dot(gt,gp)/2+gt[2]*fp*C(0,v/2)-product*(1/r0+1/r1)
        d=ft*gp[2]*(-v)+product*C(0,-nu)
        s=product
        pref=r0*r1*u*C(tri.det_range(ctx.R))/(2*R)
        Q=((r0+r1+R)*(r0+r1-R)*(R+r0-r1)*(R-r0+r1))/(4*R*R)
        kk=C(v*ctx.b)/R;phase=A*ez*v-nu*ctx.t
    elif cell.kind in ('origin_T','origin_P'):
        radius=candidate.edges[1];r=u*radius;eta=w*2-1;other=R+r*eta
        aa=-eta+r*(1-eta*eta)/(2*R)
        if cell.kind=='origin_P':aa=-aa
        n=[P(aa*e[k])+xtrans[k] for k in range(3)]
        local=[x*r for x in n]
        if cell.kind=='origin_T':
            xp=[local[k]-R*e[k] for k in range(3)]
            ft,gts=origin_field(candidate,a,r,n,ma,True)
            fp,gp=regular_field(candidate,b,cell.j,other,xp,mb,False)
            h=dot(gts,gp)*r/2+gts[2]*fp*(r*C(0,v/2))
            d=ft*gp[2]*(-v)*(r*r)+ft*fp*((r*r)*C(0,-nu))
            phase=r*aa*ez*v-nu*ctx.t
        else:
            xt=[local[k]+R*e[k] for k in range(3)]
            ft,gt=regular_field(candidate,a,cell.i,other,xt,ma,True)
            fp,gps=origin_field(candidate,b,r,n,mb,False)
            h=dot(gt,gps)*r/2+gt[2]*fp*((r*r)*C(0,v/2))
            d=ft*gps[2]*(-v)*r+ft*fp*((r*r)*C(0,-nu))
            phase=ctx.v*ctx.z+r*aa*ez*v-nu*ctx.t
        h=h-ft*fp*(r+r*r/other)
        s=ft*fp*(r*r)
        # r² was multiplied into H/D/S above. dr*deta=2*radius*du*dw.
        pref=other*(2*radius)/(2*R);Q=1-aa*aa;kk=C(v*ctx.b)*r/R
    else:raise ValueError('unknown chart kind')
    kkpoly=h-d*C(0,1)
    vals={'S_TP':s,'H_TP':h,'D_TP':d,'K_TP':kkpoly}
    if any(p.degree>4 for p in vals.values()):raise ValueError('unexpected angular degree')
    return Kernel(vals,C(Q),C(kk),C(phase),C(pref),real_path)
