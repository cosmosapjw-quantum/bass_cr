"""Bounded two-center Galerkin S,H,D assembly, in atomic units.

Coulomb potentials are not softened. Kinetic energy uses the weak gradient
form; a finite radial domain/basis and numerical quadrature remain explicit.
This is not an all-bound or full-collision production solver.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
import hashlib
import math
import numpy as np
from scipy import special
from numpy.polynomial.legendre import leggauss
from .radial_basis import HydrogenRadial, digest, integer, positive, readonly


def solid_harmonic(xyz,l,m):
    """r^l Y_lm and Cartesian gradient, complex Condon-Shortley convention."""
    integer(l,'l',0,3);integer(m,'m',-l,l)
    x=np.asarray(xyz,float)
    if x.ndim!=2 or x.shape[1]!=3 or not np.isfinite(x).all():raise ValueError('finite points[N,3] required')
    # Positive m homogeneous harmonic polynomials. Negative m follows conjugacy.
    root=lambda a:math.sqrt(a/math.pi)
    pp={
      (0,0):{(0,0,0):root(1/4)},
      (1,0):{(0,0,1):root(3/4)},
      (1,1):{(1,0,0):-root(3/8),(0,1,0):-1j*root(3/8)},
      (2,0):{(0,0,2):2*root(5/16),(2,0,0):-root(5/16),(0,2,0):-root(5/16)},
      (2,1):{(1,0,1):-root(15/8),(0,1,1):-1j*root(15/8)},
      (2,2):{(2,0,0):root(15/32),(1,1,0):2j*root(15/32),(0,2,0):-root(15/32)},
      (3,0):{(0,0,3):2*root(7/16),(2,0,1):-3*root(7/16),(0,2,1):-3*root(7/16)},
      (3,1):{(1,0,2):-4*root(21/64),(0,1,2):-4j*root(21/64),(3,0,0):root(21/64),(1,2,0):root(21/64),(2,1,0):1j*root(21/64),(0,3,0):1j*root(21/64)},
      (3,2):{(2,0,1):root(105/32),(1,1,1):2j*root(105/32),(0,2,1):-root(105/32)},
      (3,3):{(3,0,0):-root(35/64),(2,1,0):-3j*root(35/64),(1,2,0):3*root(35/64),(0,3,0):1j*root(35/64)}}
    f=np.zeros(len(x),complex);g=np.zeros_like(x,dtype=complex)
    for powers,c in pp[l,abs(m)].items():
        f+=c*np.prod(x**np.asarray(powers),axis=1)
        for j in range(3):
            if powers[j]:
                v=list(powers);v[j]-=1
                g[:,j]+=c*powers[j]*np.prod(x**np.asarray(v),axis=1)
    if m<0:f=(-1)**abs(m)*f.conj();g=(-1)**abs(m)*g.conj()
    return f,g


@dataclass(frozen=True)
class Trajectory:
    origins: object
    velocities: object=((0.,0.,0.),(0.,0.,0.))
    charges: object=(1.,1.)

    def __post_init__(self):
        for key,shape in [('origins',(2,3)),('velocities',(2,3)),('charges',(2,))]:
            a=np.asarray(getattr(self,key),float)
            if a.shape!=shape or not np.isfinite(a).all():raise ValueError('finite two-center '+key+' required')
            if key=='charges' and np.any(a<=0):raise ValueError('positive charges required')
            object.__setattr__(self,key,readonly(a))

    def centers(self,t):
        if not np.isfinite(t):raise ValueError('finite time required')
        return self.origins+self.velocities*t

    def record(self):return {k:getattr(self,k).tolist() for k in ('origins','velocities','charges')}


@dataclass(frozen=True)
class Quadrature:
    nrad: int=40
    neta: int=32
    nphi: int=32
    scale: float=1.

    def __post_init__(self):
        integer(self.nrad,'nrad',8,128);integer(self.neta,'neta',8,128);integer(self.nphi,'nphi',8,128)
        positive(self.scale,'scale')
        if self.nrad*self.neta*self.nphi>1_000_000:raise ValueError('bounded quadrature exceeds one million points')


@dataclass(frozen=True)
class Channel:
    center: int
    radial: object
    m: int

    def __post_init__(self):
        integer(self.center,'center',0,1);integer(self.radial.l,'l',0,3);integer(self.m,'m',-self.radial.l,self.radial.l)

    def record(self):return {'center':self.center,'radial':self.radial.identity,'l':self.radial.l,'m':self.m,'energy':self.radial.energy}


def symmetric_channels(bank):
    bank=tuple(bank)
    if not bank:raise ValueError('nonempty radial bank required')
    channels=tuple(Channel(c,r,m) for c in (0,1) for r in bank for m in range(-r.l,r.l+1))
    if len(channels)>128:raise ValueError('bounded basis exceeds 128 channels')
    return channels


def hydrogen_channels(nmax):
    integer(nmax,'nmax',1,4)
    return symmetric_channels(HydrogenRadial(n,l) for n in range(1,nmax+1) for l in range(n))


def prolate_grid(trajectory,t,q):
    """All-space positive Laguerre x Legendre x periodic-phi rule.

    rho=(rT+rP-R)/2>=0. Only integration weights are exponentially rescaled;
    the Hamiltonian and wavefunctions are not modified. Nodes miss both nuclei.
    """
    centers=trajectory.centers(t);delta=centers[1]-centers[0];R=float(np.linalg.norm(delta))
    if R<1e-7:raise ValueError('coincident/unresolved foci need a separate spherical chart')
    ez=delta/R;axis=np.eye(3)[int(np.argmin(abs(ez)))];e1=np.cross(ez,axis);e1/=np.linalg.norm(e1);e2=np.cross(ez,e1)
    x,wx=special.roots_laguerre(q.nrad);eta,we=leggauss(q.neta);phi=2*np.pi*np.arange(q.nphi)/q.nphi
    if np.any(wx<=0):raise ArithmeticError('Laguerre weight underflow')
    mu=1+2*x/(q.scale*R)
    transverse=(R/2)*np.sqrt((mu[:,None,None]**2-1)*(1-eta[None,:,None]**2))
    along=(R/2)*mu[:,None,None]*eta[None,:,None]
    points=(centers.mean(axis=0)+along[...,None]*ez+
        transverse[...,None]*(np.cos(phi)[None,None,:,None]*e1+np.sin(phi)[None,None,:,None]*e2))
    weights=(R**2/(4*q.scale))*(mu[:,None]**2-eta[None,:]**2)*np.exp(np.log(wx)+x)[:,None]*we[None,:]*(2*np.pi/q.nphi)
    weights=np.broadcast_to(weights[:,:,None],points.shape[:-1]).ravel().copy()
    if not np.isfinite(points).all() or not np.isfinite(weights).all():raise ArithmeticError('nonfinite prolate rule')
    return points.reshape(-1,3),weights


def basis_values(points,channels,trajectory,t):
    """Return chi, spatial grad chi, and DIRECT fixed-lab-point d_t chi.

    chi=exp(i v.r-i v^2 t/2) phi(r-A-vt).
    dot_chi=phase*(-v.grad(phi)-i v^2 phi/2), not inferred from dot(S).
    """
    p=np.asarray(points,float);channels=tuple(channels)
    if p.ndim!=2 or p.shape[1]!=3 or not np.isfinite(p).all():raise ValueError('finite points[N,3] required')
    if not channels or len(channels)>128:raise ValueError('bounded nonempty basis required')
    if len(p)*len(channels)>4_000_000:raise ValueError('basis evaluation scratch cap exceeded; use assembly chunks')
    B=np.empty((len(p),len(channels)),complex);g=np.empty((*B.shape,3),complex);dot=np.empty_like(B)
    centers=trajectory.centers(t)
    for j,c in enumerate(channels):
        xyz=p-centers[c.center];r=np.linalg.norm(xyz,axis=1);ell=c.radial.l
        if np.any(r==0):raise ValueError('classical cusp derivative at a nucleus is undefined')
        solid,ds=solid_harmonic(xyz,ell,c.m);u,du=c.radial.evaluate(r)
        a=u/r**(ell+1);da=du/r**(ell+1)-(ell+1)*u/r**(ell+2)
        f=a*solid;df=a[:,None]*ds+(da*solid/r)[:,None]*xyz
        v=trajectory.velocities[c.center];phase=np.exp(1j*(p@v)-.5j*(v@v)*t)
        B[:,j]=phase*f;g[:,j]=phase[:,None]*(df+1j*f[:,None]*v)
        dot[:,j]=phase*(-df@v-.5j*(v@v)*f)
    if not np.isfinite(B).all() or not np.isfinite(g).all() or not np.isfinite(dot).all():raise ArithmeticError('nonfinite basis action')
    return B,g,dot


@dataclass(frozen=True)
class Snapshot:
    S: np.ndarray
    H: np.ndarray
    D: np.ndarray
    identity: str
    metadata: dict


def assemble(trajectory,channels,t,q=Quadrature(),*,chunk=1024):
    integer(chunk,'chunk',1,8192);channels=tuple(channels)
    if not channels or len(channels)>128:raise ValueError('bounded nonempty basis required')
    points,weights=prolate_grid(trajectory,t,q);n=len(channels)
    S=np.zeros((n,n),complex);H=np.zeros_like(S);D=np.zeros_like(S)
    centers=trajectory.centers(t)
    for start in range(0,len(points),chunk):
        p=points[start:start+chunk];w=weights[start:start+chunk]
        B,g,dot=basis_values(p,channels,trajectory,t)
        V=-sum(trajectory.charges[c]/np.linalg.norm(p-centers[c],axis=1) for c in (0,1))
        S+=B.conj().T@(w[:,None]*B)
        H+=B.conj().T@((w*V)[:,None]*B)
        for j in range(3):H+=.5*g[:,:,j].conj().T@(w[:,None]*g[:,:,j])
        D+=B.conj().T@(w[:,None]*dot)
    record={'trajectory':trajectory.record(),'time':float(t),'channels':[c.record() for c in channels],
        'quadrature':q.__dict__,'points':len(points),'units':'a0_Eh_ta','basis_kind':'FINITE_TWO_CENTER_SELECTED_BASIS',
        'kinetic':'WEAK_GRADIENT_FORM','connection':'DIRECT_FIXED_LAB_BASIS_DERIVATIVE','softening':False,
        'production_admitted':False,'all_bound':'OPEN','b_grid':'NO_GO'}
    record['matrix_sha256']={name:hashlib.sha256(a.tobytes()).hexdigest() for name,a in [('S',S),('H',H),('D',D)]}
    return Snapshot(readonly(S),readonly(H),readonly(D),digest(record),record)


def selected_population(c,S,indices):
    """Gram population on a declared finite span, never a continuum/all-bound label."""
    S=np.asarray(S,complex);c=np.asarray(c,complex);ix=list(indices)
    if c.ndim!=1 or S.shape!=(len(c),len(c)) or not np.isfinite(S).all() or not np.isfinite(c).all():raise ValueError('finite metric/coefficient shape required')
    if not ix or len(set(ix))!=len(ix):raise ValueError('nonempty unique indices required')
    for j in ix:integer(j,'index',0,len(c)-1)
    if np.linalg.norm(S-S.conj().T)>1e-11*max(1.,np.linalg.norm(S)):raise ValueError('non-Hermitian metric')
    ev=np.linalg.eigvalsh(S)
    if ev[0]<=1e-10*ev[-1] or ev[-1]<=0:raise ValueError('metric rank loss')
    G=S[np.ix_(ix,ix)];d=S[ix,:]@c
    p=float(np.vdot(d,np.linalg.solve(G,d)).real);norm=float(np.vdot(c,S@c).real)
    if p < -1e-10 or p>norm+1e-10:raise ArithmeticError('projector probability outside norm')
    return p
