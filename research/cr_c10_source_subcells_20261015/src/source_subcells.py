"""Source-conditioned, positive threshold-resolved fixed-q spectral quadrature.

Research supplier for the frozen SOURCE07 C5 q-grid, NOT a replacement of its
running H/He history. Source physical 50,000K blackbody over 13.6..100eV,
original 48 Simpson-32 normalized photon fractions, fit cutoffs 13.60,
24.59,54.42eV, *binding* values distinct. Proper seconds and cm units.

Physical photon energy E = R * E_reference; angular R, J, birth clock and
species gas state belong to the external owner and must be applied once.
Current module treats one positive externally weighted ray only.

Exact count and energy moments are source-cell conditioned quadrature moments;
results compared against continuum oracle are empirical quadrature (not an
all-time certified continuum bound). After arbitrary attenuation/redshift,
N,U alone do not determine within-cell species opacities. No extrapolation
of this source-conditioned closure is allowed without new source information.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Sequence
import numpy as np
from scipy.integrate import quad
from threshold_rt import ATOMIC, ION_NAMES, SOURCE_EDGES, C_CM_S, BOLTZMANN_EV_K, frozen_source, frozen_grid, source_shape, verner

PHYSICAL_BINDING=(13.598434599702,24.587389011,54.41776)
NATIVE_AXIS=16
Q_ENERGY_MIN=13.6
Q_ENERGY_MAX=433.0
SCALE_TOL=2e-12

@dataclass(frozen=True)
class SourceQuadrature:
    q_index:np.ndarray
    energy_eV:np.ndarray
    photon_weight_per_initial_H:np.ndarray
    energy_nodes_ref_eV:np.ndarray
    source_weight_photons:np.ndarray
    n_cells:int
    ratio_R:float

    def number_and_energy(self):
        n=np.bincount(self.q_index,weights=self.photon_weight_per_initial_H,minlength=self.n_cells)
        u=np.bincount(self.q_index,weights=self.photon_weight_per_initial_H*self.energy_nodes_ref_eV,minlength=self.n_cells)
        return n,u

    @property
    def count(self): return float(np.sum(self.photon_weight_per_initial_H))

    @property
    def physical_energy(self):
        return float(np.sum(self.photon_weight_per_initial_H*self.energy_eV))


def reference_edges(n_energy:int,max_ref_eV:float=Q_ENERGY_MAX):
    if not isinstance(n_energy,int) or n_energy<16 or n_energy>8192 or not(isfinite(max_ref_eV) and 432.2293723204678<=max_ref_eV<=50000):
        raise ValueError('invalid fixed-q grid contract')
    return np.geomspace(Q_ENERGY_MIN,float(max_ref_eV),n_energy+1)

@lru_cache(maxsize=3)
def _nodes(n:int):
    if n not in (4,8,12,16,24,32): raise ValueError('unsupported GL order')
    return np.polynomial.legendre.leggauss(n)

@lru_cache(maxsize=2)
def _native_source():
    native_grid=frozen_grid(NATIVE_AXIS)
    fractions=[weight for _,weight in frozen_source(NATIVE_AXIS)]
    return np.asarray(native_grid),np.asarray(fractions)


def source_quadrature(n_energy:int,ratio_R:float=1.,order:int=8,max_ref_eV:float=Q_ENERGY_MAX)->SourceQuadrature:
    """Positive GL subcells split at EVERY native source and q-grid edge.

    Native source fractions fixed from its Simpson32 discrete source. Each native
    cell's quadrature mass is renormalized to the same original source fraction.
    Thus the returned q-bin N,U are *source moments*, not centroid guesses.
    """
    if not(isfinite(ratio_R) and 0<ratio_R<=1):
        raise ValueError('the current owner q-grid lower bound assumes R<=1; reject rather than extrapolate')
    q_edges=reference_edges(n_energy,max_ref_eV)
    physical_edges=ratio_R*q_edges
    if physical_edges[-1]<SOURCE_EDGES[-1]*(1-SCALE_TOL):
        raise ValueError('mapped source above reference support')
    if physical_edges[0]>SOURCE_EDGES[0]*(1+SCALE_TOL):
        raise ValueError('mapped source below reference support')
    native_edges,native_fractions=_native_source()
    x,w=_nodes(order)
    energies=[];weights=[];indices=[]
    for j,(low,high,portion) in enumerate(zip(native_edges[:-1],native_edges[1:],native_fractions)):
        i0=max(0,int(np.searchsorted(physical_edges,low,side='right'))-1)
        i1=min(n_energy-1,int(np.searchsorted(physical_edges,high,side='left')))
        ownE=[];ownW=[];ownI=[]
        for qi in range(i0,i1+1):
            a=max(low,physical_edges[qi]);b=min(high,physical_edges[qi+1])
            if not b>a:continue
            e=(a+b)*.5+(b-a)*.5*x
            v=(b-a)*.5*w*np.asarray([source_shape(float(ee)) for ee in e])
            ownE.extend(e.tolist());ownW.extend(v.tolist());ownI.extend([qi]*order)
        mass=sum(ownW)
        if mass<=0:raise ArithmeticError('empty native source intersection')
        # Postintersection normalization is exact to ordinary float tolerance,
        # preserves NativeSimpson fraction rather than replacing original source.
        fac=float(portion)/mass
        energies.extend(ownE)
        weights.extend([float(z*fac) for z in ownW])
        indices.extend(ownI)
    E=np.asarray(energies,dtype=np.float64)
    W=np.asarray(weights,dtype=np.float64)
    I=np.asarray(indices,dtype=np.int32)
    if len(E)!=len(W) or not np.all(W>0) or np.min(E)<SOURCE_EDGES[0]-1e-12 or np.max(E)>100+1e-12:
        raise ArithmeticError('source positivity/domain contract violated')
    return SourceQuadrature(I,E,W,E/ratio_R,W,n_energy,ratio_R)


def verner_numpy(kind:str,energy:np.ndarray)->np.ndarray:
    if kind not in ATOMIC:raise ValueError('unknown absorber')
    en=np.asarray(energy,dtype=np.float64)
    if np.any(~np.isfinite(en)) or np.any((en<0)|(en>50000)):
        raise ValueError('out of Verner fit domain')
    eth,e0,s0,ya,p,yw,y0,y1=ATOMIC[kind]
    out=np.zeros_like(en)
    active=en>=eth
    if np.any(active):
        x=en[active]/e0-y0
        y=np.hypot(x,y1)
        out[active]=s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18
    return out


def _parameters(neutrals_cm3:Sequence[float],dt_s:float):
    vals=np.asarray(neutrals_cm3,dtype=np.float64)
    if vals.shape!=(3,) or np.any(~np.isfinite(vals)) or np.any(vals<0) or not(isfinite(dt_s) and dt_s>=0):
        raise ValueError('invalid frozen proper absorber/dt state')
    return vals,float(dt_s)


def reaction_fraction(energy_eV:np.ndarray,neutrals_cm3:Sequence[float],dt_s:float):
    """Exact-in-time exponential frozen-neutral destruction at fixed energy.

    Return species fractions per incident photon in shape (3, n) and survival.
    Consistently uses owner q-grid exponential, NOT the parent's BE readout.
    """
    rho,dt=_parameters(neutrals_cm3,dt_s)
    en=np.asarray(energy_eV,dtype=np.float64)
    if en.ndim!=1:raise ValueError('flat energy vector expected')
    rates=np.stack([rho[j]*C_CM_S*verner_numpy(k,en) for j,k in enumerate(ION_NAMES)])
    optical=dt*np.sum(rates,axis=0)
    killed=-np.expm1(-optical)
    fractions=np.divide(rates,np.sum(rates,axis=0),out=np.zeros_like(rates),where=np.sum(rates,axis=0)>0)
    return fractions*killed, np.exp(-optical)


def source_and_reaction(q:SourceQuadrature,neutrals_cm3:Sequence[float],dt_s:float,total_emitted_per_H:float=1.,binding_eV:Sequence[float]=PHYSICAL_BINDING):
    """Source-conditioned N/U plus all three frozen-gas reaction moments per q bin."""
    if not(isfinite(total_emitted_per_H) and total_emitted_per_H>=0):raise ValueError('invalid external source weight')
    b=np.asarray(binding_eV,dtype=np.float64)
    if b.shape!=(3,) or np.any(~np.isfinite(b)) or np.any((b<0)|(b>np.array([ATOMIC[k][0] for k in ION_NAMES]))):
        raise ValueError('invalid binding/fit threshold ownership')
    N,U=q.number_and_energy()
    mass=q.photon_weight_per_initial_H*total_emitted_per_H
    events,remaining=reaction_fraction(q.energy_eV,neutrals_cm3,dt_s)
    absorbed=np.stack([np.bincount(q.q_index,weights=mass*events[j],minlength=q.n_cells) for j in range(3)])
    after_n=np.bincount(q.q_index,weights=mass*remaining,minlength=q.n_cells)
    after_u=np.bincount(q.q_index,weights=mass*remaining*q.energy_nodes_ref_eV,minlength=q.n_cells)
    heat=np.stack([np.bincount(q.q_index,weights=mass*events[j]*(q.energy_eV-b[j]),minlength=q.n_cells) for j in range(3)])
    binding=absorbed*b[:,None]
    before_n=N*total_emitted_per_H
    before_ref_u=U*total_emitted_per_H
    before_phys_u=before_ref_u*q.ratio_R
    after_phys_u=after_u*q.ratio_R
    return {
        'N':before_n,'U_ref':before_ref_u,'N_after':after_n,'U_ref_after':after_u,
        'absorb_species':absorbed,'heat_species':heat,'binding_species':binding,
        'number_residual':float(before_n.sum()-after_n.sum()-absorbed.sum()),
        'energy_residual_eV':float(before_phys_u.sum()-after_phys_u.sum()-heat.sum()-binding.sum()),
        'physical_energy_per_H':float(before_phys_u.sum()),
        'emitted_per_H':float(before_n.sum()),
    }


def centroid_control(q:SourceQuadrature,neutrals_cm3:Sequence[float],dt_s:float,total_emitted_per_H:float=1.,binding_eV:Sequence[float]=PHYSICAL_BINDING):
    N,U=q.number_and_energy()
    means=np.divide(U,N,out=np.zeros_like(U),where=N>0)*q.ratio_R
    events,remaining=reaction_fraction(means,neutrals_cm3,dt_s)
    b=np.asarray(binding_eV)
    absorbed=(N[None,:]*events)*total_emitted_per_H
    heat=absorbed*(means[None,:]-b[:,None])
    return dict(absorb_species=absorbed,heat_species=heat,
                total_absorbed=float(absorbed.sum()),total_heat=float(heat.sum()))


def source_continuum_reference(neutrals_cm3:Sequence[float],dt_s:float,total_emitted_per_H:float=1.,ratio_R:float=1.):
    """Independent adaptive 1D SciPy oracle for same physical 50kK native source fractions.

    Rate evaluated at photon physical E at emission; ratio_R changes E_ref
    mapping, not the actual source shape. No time-varying gas/geometry assumed.
    """
    if not(isfinite(ratio_R) and ratio_R>0):raise ValueError('invalid ratio')
    native_edges,native_fractions=_native_source()
    integrals=[quad(source_shape,float(a),float(b),epsabs=0,epsrel=3e-13)[0] for a,b in zip(native_edges[:-1],native_edges[1:])]
    vals=np.zeros((3,2),dtype=float)
    for i,(low,high,portion,denom) in enumerate(zip(native_edges[:-1],native_edges[1:],native_fractions,integrals)):
        for j,kind in enumerate(ION_NAMES):
            def kernel(E,heat):
                rate=np.array([rho*C_CM_S*verner(k,E) for rho,k in zip(neutrals_cm3,ION_NAMES)])
                total=sum(rate);ev=(-np.expm1(-total*dt_s))*rate[j]/total if total>0 else 0.
                return source_shape(E)*ev*((E-PHYSICAL_BINDING[j]) if heat else 1)
            for heat in (0,1):
                vals[j,heat]+=portion*quad(lambda E:kernel(E,heat),float(low),float(high),epsabs=0,epsrel=2e-11)[0]/denom
    return {'event':vals[:,0]*total_emitted_per_H,'heat':vals[:,1]*total_emitted_per_H}

@dataclass(frozen=True)
class CachedReactionKernel:
    """Precomputed positive original Verner opacities at source GL nodes.

    All arrays are non-writeable. These are direct source-shape coefficients and
    do not change on a frozen-neutral readout. Cache is local to geometry R and
    does NOT persist after a spectral redshift/chemistry shape change.
    """
    quad: SourceQuadrature
    sigma_cm2:np.ndarray # (3,nQuadrature)


def precompute_reaction_kernel(quad:SourceQuadrature):
    op=np.stack([verner_numpy(k,quad.energy_eV) for k in ION_NAMES]);op.flags.writeable=False
    return CachedReactionKernel(quad,op)


@lru_cache(maxsize=16)
def cached_source_kernel(n_energy:int,ratio_R:float=1.,order:int=8):
    quad=source_quadrature(n_energy,ratio_R,order)
    for ar in (quad.q_index,quad.energy_eV,quad.photon_weight_per_initial_H,quad.energy_nodes_ref_eV,quad.source_weight_photons):
        ar.flags.writeable=False
    return precompute_reaction_kernel(quad)


def batched_frozen_reactions(kernel:CachedReactionKernel,
                             neutrals_cm3:np.ndarray,dt_s:np.ndarray,
                             emitted_per_H:float=1.,batch_size:int=16):
    """Many independent frozen neutral systems on the SAME source quadrature.

    Vectorized across energy and bounded ray batch chunks. Inputs have one
    neutral triplet and one proper dt per independent ray; this does NOT merge
    their photon moments, directions or source age. Returns shape (n_rays,3)
    for events and heating. No gas feedback or source Jacobian is applied.
    """
    gas=np.asarray(neutrals_cm3,dtype=float)
    dt=np.asarray(dt_s,dtype=float)
    if gas.ndim!=2 or gas.shape[1]!=3 or dt.shape!=(gas.shape[0],) or not(np.all(np.isfinite(gas)) and np.all(gas>=0) and np.all(np.isfinite(dt)) and np.all(dt>=0)):
        raise ValueError('invalid distinct-ray frozen neutral states or dt')
    if not(isfinite(emitted_per_H) and emitted_per_H>=0) or not isinstance(batch_size,int) or batch_size<1 or batch_size>256:
        raise ValueError('invalid emission normalization or batch size')
    n=len(dt);events=np.zeros((n,3));heats=np.zeros((n,3));
    S=kernel.sigma_cm2
    E=kernel.quad.energy_eV
    mass=kernel.quad.photon_weight_per_initial_H*emitted_per_H
    weights=(E[None,:]-np.asarray(PHYSICAL_BINDING)[:,None])*mass[None,:]
    for left in range(0,n,batch_size):
        right=min(n,left+batch_size)
        # B x species x source quadrature nodes
        rates=C_CM_S*gas[left:right,:,None]*S[None,:,:]
        total=rates.sum(axis=1)
        absorption=-np.expm1(-dt[left:right,None]*total)
        fractions=np.divide(rates,total[:,None,:],out=np.zeros_like(rates),where=total[:,None,:]>0)
        species_fraction=fractions*absorption[:,None,:]
        events[left:right]=np.einsum('bkn,n->bk',species_fraction,mass,optimize=False)
        heats[left:right]=np.einsum('bkn,kn->bk',species_fraction,weights,optimize=False)
    return events,heats


def scalar_frozen_reactions(kernel:CachedReactionKernel,neutrals_cm3:Sequence[float],dt_s:float,emitted_per_H:float=1.):
    """Independent pure-Python scalar oracle for matched energy/neutral inputs."""
    from math import expm1
    gas,dt=_parameters(neutrals_cm3,dt_s)
    event=[0.]*3;heat=[0.]*3
    for E,wt in zip(kernel.quad.energy_eV,kernel.quad.photon_weight_per_initial_H):
        lam=[C_CM_S*gas[j]*verner(ion,float(E)) for j,ion in enumerate(ION_NAMES)]
        total=sum(lam)
        if total==0:continue
        absorbed=-expm1(-dt*total)
        for j in range(3):
            p=wt*emitted_per_H*lam[j]/total*absorbed
            event[j]+=p;heat[j]+=p*(E-PHYSICAL_BINDING[j])
    return np.asarray(event),np.asarray(heat)


def scalar_cached_reactions(kernel:CachedReactionKernel,neutrals_cm3:Sequence[float],dt_s:float,emitted_per_H:float=1.):
    """Scalar oracle using the SAME precomputed original Verner coefficients.

    Separates savings from one-time opacity caching and from NumPy batching.
    """
    from math import expm1
    gas,dt=_parameters(neutrals_cm3,dt_s)
    event=[0.]*3;heat=[0.]*3
    Earr=kernel.quad.energy_eV;warr=kernel.quad.photon_weight_per_initial_H
    S=kernel.sigma_cm2
    for a in range(len(Earr)):
        lam=[C_CM_S*gas[j]*S[j,a] for j in range(3)]
        total=lam[0]+lam[1]+lam[2]
        if total==0:continue
        lost=-expm1(-dt*total)
        for j in range(3):
            p=warr[a]*emitted_per_H*lam[j]/total*lost
            event[j]+=p;heat[j]+=p*(Earr[a]-PHYSICAL_BINDING[j])
    return np.asarray(event),np.asarray(heat)
