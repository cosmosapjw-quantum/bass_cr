"""Finite radial FEM eigenfunctions and analytic hydrogen reference channels.

Atomic units. Positive eigenvalues are finite-domain pseudostates, not a
certified continuum quadrature. No threshold floor or hidden mode deletion.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
import numpy as np
from numpy.polynomial import Polynomial
from scipy import linalg, special
from .kernels import radial_fem


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def integer(x,name,lo,hi):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,(int,np.integer)) or not lo<=x<=hi:
        raise ValueError(f'{name} must be an integer in [{lo},{hi}]')
    return int(x)


def positive(x,name):
    if isinstance(x,(bool,np.bool_)) or not np.isscalar(x) or not np.isfinite(x) or x<=0:
        raise ValueError(f'{name} must be positive finite')
    return float(x)


def readonly(a):
    a=np.array(a,copy=True);a.setflags(write=False);return a


@dataclass(frozen=True)
class HydrogenRadial:
    principal_n: int
    l: int

    def __post_init__(self):
        integer(self.principal_n,'principal_n',1,4)
        integer(self.l,'l',0,self.principal_n-1)

    @property
    def energy(self):return -.5/self.principal_n**2

    @property
    def identity(self):return digest({'kind':'ANALYTIC_HYDROGEN','n':self.principal_n,'l':self.l})

    def evaluate(self,r):
        """Return u=r R_nl and du/dr, with int |u|^2 dr = 1."""
        r=np.asarray(r,float)
        if np.any(r<0) or not np.isfinite(r).all():raise ValueError('nonnegative finite radii required')
        n=self.principal_n;l=self.l;k=n-l-1;x=2*r/n
        norm=2/n**2*math.sqrt(math.factorial(k)/math.factorial(n+l))
        lag=special.eval_genlaguerre(k,2*l+1,x)
        dlag=-special.eval_genlaguerre(k-1,2*l+2,x) if k else np.zeros_like(r)
        R=norm*np.exp(-r/n)*x**l*lag
        dR=norm*np.exp(-r/n)*((-x**l/n)*lag+x**l*dlag*2/n)
        if l:dR+=norm*np.exp(-r/n)*l*x**(l-1)*lag*2/n
        return r*R,R+r*dR


@dataclass(frozen=True)
class RadialSpec:
    radius: float=64.
    elements: int=32
    degree: int=4
    lmax: int=3
    bound_nmax: int=4
    positive_per_l: int=0
    positive_emax: float=2.
    quad_order: int=12
    grading: float=2.

    def __post_init__(self):
        positive(self.radius,'radius');positive(self.grading,'grading')
        integer(self.elements,'elements',2,120);integer(self.degree,'degree',1,8)
        integer(self.lmax,'lmax',0,3);integer(self.bound_nmax,'bound_nmax',1,4)
        integer(self.positive_per_l,'positive_per_l',0,2)
        integer(self.quad_order,'quad_order',self.degree+1,32)
        positive(self.positive_emax,'positive_emax')
        if self.elements*self.degree>600:raise ValueError('bounded radial bank exceeds 600 DOFs')


@dataclass(frozen=True)
class FEMRadial:
    l: int
    principal_n: int|None
    energy: float
    edges: np.ndarray
    polynomial_coefficients: np.ndarray
    identity: str
    residual: float

    def evaluate(self,r):
        r=np.asarray(r,float)
        if np.any(r<0) or not np.isfinite(r).all():raise ValueError('nonnegative finite radii required')
        flat=r.ravel();u=np.zeros_like(flat);du=np.zeros_like(flat)
        inside=flat<self.edges[-1];v=flat[inside]
        cell=np.searchsorted(self.edges,v,side='right')-1
        h=self.edges[cell+1]-self.edges[cell];s=(v-self.edges[cell])/h
        coef=self.polynomial_coefficients[cell];powers=np.arange(coef.shape[1])
        u[inside]=np.sum(coef*s[:,None]**powers,axis=1)
        du[inside]=np.sum(coef[:,1:]*powers[1:]*s[:,None]**powers[:-1],axis=1)/h
        return u.reshape(r.shape),du.reshape(r.shape)


def atomic_bank(spec=RadialSpec()):
    """Retain declared bound and positive modes from each isolated H_l.

    Each l uses the same radial mesh and weak Coulomb form. m degeneracy is
    represented by separate angular channels, not duplicated eigensolves.
    Failure to resolve a requested state raises; it does not shrink the basis.
    """
    p=spec.degree;nodes=np.linspace(0,1,p+1)
    polys=[Polynomial.fromroots(np.delete(nodes,j))/np.prod(nodes[j]-np.delete(nodes,j)) for j in range(p+1)]
    transform=np.array([f.coef for f in polys]);bank=[]
    for ell in range(spec.lmax+1):
        H,M,meta=radial_fem(spec.radius,spec.elements,p,l=ell,quad_order=spec.quad_order,grading=spec.grading)
        energy,coef=linalg.eigh(H,M)
        nb=max(0,spec.bound_nmax-ell)
        neg=np.flatnonzero(energy<0);pos=np.flatnonzero((energy>0)&(energy<=spec.positive_emax))
        if len(neg)<nb or len(pos)<spec.positive_per_l:
            raise ValueError(f'l={ell}: requested finite-domain states unavailable')
        selected=[(int(j),ell+i+1) for i,j in enumerate(neg[:nb])]
        selected += [(int(j),None) for j in pos[:spec.positive_per_l]]
        for j,n in selected:
            c=coef[:,j].copy()
            # Deterministic near-origin radial sign, not dominant outer lobe.
            nz=np.flatnonzero(abs(c)>1e-12*max(abs(c)))
            if c[nz[0]]<0:c=-c
            residual=float(np.linalg.norm(H@c-energy[j]*M@c))
            if residual>2e-8 or abs(energy[j])<=100*residual:
                raise ArithmeticError('radial residual or energy sign unresolved')
            full=np.concatenate(([0.],c,[0.]))
            local=np.array([full[e*p:e*p+p+1]@transform for e in range(spec.elements)])
            identity=digest({'kind':'RADIAL_FEM','spec':spec.__dict__,'l':ell,'eigen_index':j,
                'coeff_sha256':hashlib.sha256(local.tobytes()).hexdigest()})
            bank.append(FEMRadial(ell,n,float(energy[j]),readonly(meta['edges']),readonly(local),identity,residual))
    return tuple(bank)
