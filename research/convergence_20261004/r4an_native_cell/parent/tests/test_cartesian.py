from fractions import Fraction as F
from math import sqrt,pi
import numpy as np
import pytest
from weak_kernel import Candidate,Context,cover,kernel,Cell
from complex_box import C


def smooth_fixture():
    edges=tuple(map(F,[0,F(1,8),1,2,4,8]));rows=[]
    # u_a(r) = scale*r*(1-r/8)^2. p radial has nonzero u'(0).
    for scale in (F(1),F(2,3)):
        row=[]
        for lo,hi in zip(edges,edges[1:]):
            d=hi-lo
            row.append((scale*(lo-lo*lo/4+lo**3/64),scale*d*(1-lo/2+3*lo*lo/64),scale*d*d*(-F(1,4)+3*lo/64),scale*d**3/64,F(0)))
        rows.append(tuple(row))
    return Candidate(edges,tuple(rows),(0,1),'analytic-fixture-C0','SYNTHETIC_FIXTURE')


def geom(cell,c,ct,u,w):
    b,z,v,t=map(float,(ct.b,ct.z,ct.v,ct.t));R=sqrt(b*b+z*z)
    e=np.array([b/R,0,z/R]);e1=np.array([-z/R,0,b/R]);e2=np.array([0,-1,0.])
    if cell.kind=='regular':
        pts=np.array([[float(x.a+x.b*F.from_float(R)),float(y.a+y.b*F.from_float(R))] for x,y in cell.triangle.vertices])
        r0,r1=pts[0]+u*(pts[1]-pts[0]+w*(pts[2]-pts[1]))
        A=(r0*r0-r1*r1+R*R)/(2*R);rho=sqrt(max(0,r0*r0-A*A));
        jac=float(cell.triangle.det_range(ct.R).mid())*u*r0*r1/R
    else:
        rad=float(c.edges[1]);r=rad*u;eta=2*w-1;other=R+r*eta
        if cell.kind=='origin_T':r0,r1=r,other
        else:r0,r1=other,r
        A=(r0*r0-r1*r1+R*R)/(2*R);rho=sqrt(max(0,r0*r0-A*A))
        jac=2*rad*r*r*other/R
    ph=np.arange(4096)*(2*pi/4096)
    xt=A*e+rho*np.cos(ph)[:,None]*e1+rho*np.sin(ph)[:,None]*e2
    xp=xt-R*e
    return xt,xp,jac,v,t

def direct_field(points,scale,l,m):
    r=np.linalg.norm(points,axis=1);u=scale*r*(1-r/8)**2;du=scale*(1-r/2+3*r*r/64)
    q=u/r**(l+1);qp=du/r**(l+1)-(l+1)*u/r**(l+2)
    if l==0:g=np.ones(len(r));cg=np.zeros(3,dtype=complex)
    elif m==0:cg=np.array([0,0,sqrt(3)]);g=points@cg
    else:
        cg=np.array([sqrt(1.5)*(1 if m==-1 else -1),-1j*sqrt(1.5),0]);g=points@cg
    return q*g,(qp*g/r)[:,None]*points+q[:,None]*cg

CHANNELS=[(0,0),(1,-1),(1,0),(1,1)]
@pytest.mark.parametrize('ca',CHANNELS)
@pytest.mark.parametrize('cb',CHANNELS)
@pytest.mark.parametrize('kind',['regular','origin_T','origin_P'])
def test_ring_weak_kernel_matches_independent_cartesian_angle_sum(ca,cb,kind):
    c=smooth_fixture();ct=Context(1,3,F(4,5),F(17,5));
    if kind=='regular':
        # Deterministic synthetic interior triangle from the proven cover.
        cells,_=cover(c,ct.R);cell=next(x for x in cells if x.kind=='regular' and (x.i,x.j)==(2,3))
    else:cell=Cell(kind,0 if kind=='origin_T' else 3,3 if kind=='origin_T' else 0)
    u,w=F(3,5),F(2,5);a,ma=ca;b,mb=cb
    val=kernel(c,cell,ct,u,w,a,b,ma,mb).value()
    xt,xp,jac,v,t=geom(cell,c,ct,float(u),float(w))
    ft,gt=direct_field(xt,1 if a==0 else 2/3,a,ma);fp,gp=direct_field(xp,1 if b==0 else 2/3,b,mb)
    ft=np.conj(ft);gt=np.conj(gt);phase=np.exp(1j*(v*xt[:,2]-v*v*t/2))
    s=ft*fp
    h=.5*np.sum(gt*gp,axis=1)+.5j*v*gt[:,2]*fp-(1/np.linalg.norm(xt,axis=1)+1/np.linalg.norm(xp,axis=1))*s
    d=-v*ft*gp[:,2]-.5j*v*v*s
    refs={'S_TP':s,'H_TP':h,'D_TP':d,'K_TP':h-1j*d}
    for name,f in refs.items():
        ref=(phase*f).mean()*jac/2
        q=val[name];calc=complex(float(q.re.mid()),float(q.im.mid()))
        assert abs(calc-ref)<2e-11*max(1,abs(ref)),(kind,ca,cb,name,calc,ref)
