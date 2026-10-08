"""R4AF analytic continuation of the pinned finite-candidate ring integral.

Conjugation is applied ONLY to constant spherical-harmonic coefficients,
never to complex cubature coordinates. No sqrt(Q) or complex Bessel branch.
"""
from __future__ import annotations
from fractions import Fraction as F
from dataclasses import dataclass
from pathlib import Path
import json,hashlib
import numpy as np
from dyadic import I,ZERO,ONE,SCALE,pi_interval
from complex_box import C,ellipse_box,exp_positive
from quadrature import tensor_errors,radius_l1_bound
from geometry import polygons

@dataclass(frozen=True)
class Candidate:
    edges:tuple
    coeffs:tuple
    identity:str
    ells:tuple=(0,0,0,1,1)
    @property
    def channels(self):return tuple((a,l,m) for a,l in enumerate(self.ells) for m in range(-l,l+1))
    @classmethod
    def load(cls,path,meta_path):
        meta=json.loads(Path(meta_path).read_text())
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=meta['candidate_npz_sha256']:raise ValueError('candidate hash')
        with np.load(path,allow_pickle=False) as d:
            e=d['edges'];p=d['shared_endpoint_values'];b=d['bubble_coefficients']
            if e.shape!=(41,) or p.shape!=(5,41) or b.shape!=(5,40,3):raise ValueError('candidate shape')
            if not all(np.isfinite(x).all() for x in [e,p,b]):raise ValueError('nonfinite candidate')
            if e[0]!=0 or np.any(e[1:]<=e[:-1]) or np.any(p[:,0]!=0) or np.any(p[:,-1]!=0):raise ValueError('invalid edges/endpoints')
            coeff=[]
            for a in range(5):
                row=[]
                for j in range(40):
                    L,R=map(lambda x:F(float(x)),p[a,j:j+2]);q0,q1,q2=map(lambda x:F(float(x)),b[a,j])
                    row.append((L,R-L+q0,q1-q0,q2-q1,-q2))
                coeff.append(tuple(row))
        if tuple(x['l'] for x in meta['modes'])!=(0,0,0,1,1):raise ValueError('ordered channel identity')
        return cls(tuple(F(float(x)) for x in e),tuple(coeff),meta['identity'])
    def radial(self,a,e,r):
        r=C(r);low,high=self.edges[e:e+2];d=high-low;c=self.coeffs[a][e];s=(r-low)/d
        if a>=3 and low==0:
            if c[0]!=0:raise ValueError('origin not removable')
            q=C(c[4])
            for k in range(3,0,-1):q=q*s+c[k]
            return q/d
        q=C(c[4])
        for k in range(3,-1,-1):q=q*s+c[k]
        return q if a<3 else q/r


def solid_coeffs(A,R,b,z,conjugated=False):
    q3=I(3).sqrt();q32=I(F(3,2)).sqrt()
    X=A*b/R;Z=A*z/R;cx=C(-z/R);cz=C(b/R)
    # Target conjugation flips constant i only. A and coordinates remain holomorphic.
    si=C(0,-q32 if conjugated else q32)
    return ((C(1),C(),C()),(X*q32,cx*q32,si),(Z*q3,cz*q3,C()),(-X*q32,-cx*q32,si))


def magnitude_matrix(candidate,tri,b,z,v,R,u,w,epoch):
    verts=[(C(x.at(R)),C(y.at(R))) for x,y in tri.vertices]
    p0,p1,p2=verts
    r0=p0[0]+u*((p1[0]-p0[0])+w*(p2[0]-p1[0]))
    r1=p0[1]+u*((p1[1]-p0[1])+w*(p2[1]-p1[1]))
    A=(r0*r0-r1*r1+R*R)/(2*R)
    Q=((r0+r1+R)*(r0+r1-R)*(r0-r1+R)*(r1-r0+R))/(4*R*R)
    k=v*b/R;qm=Q.mag();xm=(Q*(-k*k/4)).mag()
    # sum |x|^j/[j!(j+n)!] <= exp(2sqrt(|x|))/n!.
    e=exp_positive(2*xm.sqrt());f0=e;f1=e;f2=e/2
    t1=k*qm*f1/2;t2=k*k*qm*qm*f2/4;m2=(qm*f0+t2)/2
    left=solid_coeffs(A,R,b,z,True);right=solid_coeffs(A-R,R,b,z,False)
    angular=[]
    for a0,ac,ass in left:
        row=[]
        for b0,bc,bs in right:
            row.append((a0*b0).mag()*f0+(a0*bc+ac*b0).mag()*t1+(ac*bc).mag()*m2+(ass*bs).mag()*m2)
        angular.append(row)
    phase=(r0*r0-r1*r1)*(z*v/(2*R*R))+epoch
    det=tri.det_range(R);jac=u*det
    common=exp_positive(phase.im.abs_upper())*jac.mag()/(2*R)
    ra=[candidate.radial(a,tri.i,r0).mag() for a in range(5)]
    rb=[candidate.radial(a,tri.j,r1).mag() for a in range(5)]
    slot={(0,0):0,(1,-1):1,(1,0):2,(1,1):3}
    return [[(angular[slot[l,m]][slot[ll,mm]]*common*ra[a]*rb[bb]).abs_upper()
             for bb,ll,mm in candidate.channels] for a,l,m in candidate.channels]


def prepare_cell(candidate,tri,b,z,v,R,epoch,box,tol,degrees,rho=F(2)):
    u0,u1,w0,w1=map(F,box);uc=(u0+u1)/2;hu=(u1-u0)/2;wc=(w0+w1)/2;hw=(w1-w0)/2
    mu=magnitude_matrix(candidate,tri,b,z,v,R,ellipse_box(uc,hu,rho),C(I.bounds(w0,w1)),epoch)
    mw=magnitude_matrix(candidate,tri,b,z,v,R,C(I.bounds(u0,u1)),ellipse_box(wc,hw,rho),epoch)
    for n in degrees:
        err=tensor_errors(mu,mw,hu,hw,n,rho)
        if radius_l1_bound(err).hi<=I(tol).lo:
            return {'n':n,'mu':mu,'mw':mw,'errors':err,'box':box,'radius_upper':radius_l1_bound(err)}
    return None


def write_native(path,candidate,b,z,v,R,epoch,rules,tasks):
    with open(path,'x') as f:
        f.write('R4AF_NATIVE_V1\n')
        def val(x):
            x=I(x);f.write(f'{x.lo} {x.hi}\n')
        for x in [b,z,v,R,epoch,I(3).sqrt(),I(F(3,2)).sqrt(),pi_interval()]:val(x)
        for e in candidate.edges:val(e)
        for a in candidate.coeffs:
            for e in a:
                for c in e:val(c)
        f.write(str(len(rules))+'\n');idx={}
        for k,(n,(nodes,weights,_)) in enumerate(sorted(rules.items())):
            idx[n]=k;f.write(str(n)+'\n')
            for x,w in zip(nodes,weights):val(x);val(w)
        f.write(str(len(tasks))+'\n')
        for task in tasks:
            tri=task['triangle'];u0,u1,w0,w1=map(F,task['box'])
            f.write(f"{task['id']} {tri.i} {tri.j} {idx[task['n']]}\n")
            for x,y in tri.vertices:val(x.at(R));val(y.at(R))
            for a in [tri.det_range(R),(u0+u1)/2,(u1-u0)/2,(w0+w1)/2,(w1-w0)/2]:val(a)
