"""Exact-rational photo-source projection at a fixed gas state.

This is readout algebra, not a chemistry solver or an atomic-rate certificate.
A quadrature-rule difference is NOT an observed temporal jump.  Counts/energy
moments use the same spectral weights, density, energy, and sigma samples.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Iterable, Sequence
import math

SPECIES = ('HI', 'HeI', 'HeII')

class ContractError(ValueError):
    """Inputs violate the explicit fixed-state contract."""

class MissingPremise(ContractError):
    """An error estimate was requested without its external hypotheses."""


def binary64(value: str | float | int) -> F:
    if isinstance(value, bool):
        raise ContractError('BOOLEAN_NOT_PHYSICAL_VALUE')
    value = float(value)
    if not math.isfinite(value):
        raise ContractError('NONFINITE_BINARY64')
    return F.from_float(value)


def exact(value: F) -> F:
    if not isinstance(value, F):
        raise ContractError('EXACT_FRACTION_REQUIRED')
    return value


def thermal_response(heat: F, electron_rate: F, w: F,
                     particles_per_h: F, kb: F) -> F:
    """dT at fixed state: heat includes energy, not the particle-number term.

    w: erg/H; heat: erg/H/s; electron_rate: electron/H/s; kb: erg/K.
    Synthetic tests may use explicitly rescaled energy units consistently.
    """
    for v in (heat, electron_rate, w, particles_per_h, kb): exact(v)
    if particles_per_h <= 0 or kb <= 0 or w <= 0:
        raise ContractError('EOS_DOMAIN')
    return F(2,3) / (kb*particles_per_h) * (heat-w*electron_rate/particles_per_h)


@dataclass(frozen=True)
class State:
    h: F
    y: F
    z: F
    w_erg_h: F
    n_h: F
    n_he: F
    hubble_s: F
    kb_erg_k: F
    ev_erg: F
    c_thomson_cm3_s: F

    def __post_init__(self):
        for v in self.__dict__.values(): exact(v)
        if not (0 <= self.h <= 1 and self.y >= 0 and self.z >= 0 and self.y+self.z <= 1):
            raise ContractError('FRACTION_SIMPLEX')
        if min(self.w_erg_h,self.n_h,self.hubble_s,self.kb_erg_k,self.ev_erg,self.c_thomson_cm3_s) <= 0 or self.n_he < 0:
            raise ContractError('STATE_DOMAIN')

    @property
    def f_he(self): return self.n_he/self.n_h
    @property
    def electrons(self): return self.h+self.f_he*(self.y+2*self.z)
    @property
    def particles(self): return 1+self.f_he+self.electrons
    @property
    def temperature(self): return 2*self.w_erg_h/(3*self.kb_erg_k*self.particles)
    @property
    def targets(self): return 1-self.h, self.f_he*(1-self.y-self.z), self.f_he*self.y


@dataclass(frozen=True)
class Moments:
    gamma: tuple[F,F,F]       # per absorber /s
    energy_ev_s: tuple[F,F,F] # incident-energy moment eV per absorber /s
    def __post_init__(self):
        if len(self.gamma)!=3 or len(self.energy_ev_s)!=3:
            raise ContractError('THREE_SPECIES_REQUIRED')
        for v in (*self.gamma,*self.energy_ev_s): exact(v)
        # Differences are signed; do not clip them here.
    def __sub__(self, other):
        return Moments(tuple(a-b for a,b in zip(self.gamma,other.gamma)),
                       tuple(a-b for a,b in zip(self.energy_ev_s,other.energy_ev_s)))


def spectral_moments(rows: Iterable[dict], c_cm_s: F, n_h: F) -> Moments:
    """Exact finite sum of supplied samples, NOT their continuum integral."""
    exact(c_cm_s);exact(n_h)
    if c_cm_s<=0 or n_h<=0: raise ContractError('DENSITY_OR_C_DOMAIN')
    gamma=[F(0)]*3; energy=[F(0)]*3
    for idx,row in enumerate(rows):
        if int(row['index'])!=idx: raise ContractError('SAMPLE_INDEX')
        weight=exact(row['weight']);density=exact(row['density']);e=exact(row['energy_eV'])
        if weight<=0 or density<0 or e<=0: raise ContractError('SPECTRAL_DOMAIN')
        mass=weight*density
        for a,s in enumerate(SPECIES):
            sigma=exact(row['sigma_'+s])
            if sigma<0:raise ContractError('NEGATIVE_SIGMA')
            rate=mass*sigma
            gamma[a]+=rate;energy[a]+=rate*e
    pre=c_cm_s*n_h
    return Moments(tuple(pre*v for v in gamma),tuple(pre*v for v in energy))


def project(state: State, moments: Moments, chi_ev: Sequence[F]) -> dict[str,F]:
    """Photo contribution or signed difference at this SAME state.

    q_ell_source is the photo RHS contribution to d(c*sigmaT*ne/H)/dln(a).
    It is not the slope of a prescribed gas interpolant or an observed jump.
    """
    if len(chi_ev)!=3 or any(exact(v)<=0 for v in chi_ev):raise ContractError('THRESHOLDS')
    gh,gy,gz=moments.gamma
    dh=(1-state.h)*gh
    dy=(1-state.y-state.z)*gy-state.y*gz
    dz=state.y*gz
    terms=tuple(t*g for t,g in zip(state.targets,moments.gamma))
    xe=sum(terms,F(0))
    absorbed=state.ev_erg*sum((t*e for t,e in zip(state.targets,moments.energy_ev_s)),F(0))
    binding=state.ev_erg*sum((t*c*g for t,c,g in zip(state.targets,chi_ev,moments.gamma)),F(0))
    heat=absorbed-binding
    heat_T=F(2,3)*heat/(state.kb_erg_k*state.particles)
    particle_T=-state.temperature*xe/state.particles
    temp=thermal_response(heat,xe,state.w_erg_h,state.particles,state.kb_erg_k)
    q_action=state.c_thomson_cm3_s*state.n_h*xe/state.hubble_s**2
    assert xe==dh+state.f_he*(dy+2*dz)
    assert absorbed==heat+binding and temp==heat_T+particle_T
    return dict(h_dt_s=dh,heii_dt_s=dy,heiii_dt_s=dz,
                electron_dt_per_h_s=xe,heat_erg_h_s=heat,binding_erg_h_s=binding,
                absorbed_erg_h_s=absorbed,temperature_dt_k_s=temp,
                heating_temperature_dt_k_s=heat_T,particle_temperature_dt_k_s=particle_T,
                photo_q_ell_source=q_action)


def fixed_difference(a_state: State, a: Moments, b_state: State, b: Moments,
                     chi_ev: Sequence[F]) -> dict[str,F]:
    if a_state != b_state: raise ContractError('SAME_STATE_REQUIRED')
    return project(a_state,b-a,chi_ev)


def conditional_source_box(state: State, chi_ev: Sequence[F],
                           gamma_box, energy_box, *, premises: str | None) -> dict:
    """Linear image of supplied moment-error boxes, not proof of those boxes.

    Gamma-only bounds cannot provide arbitrary spectral heating bounds.
    Endpoints must be exact; joint correlations may be lost conservatively.
    """
    if gamma_box is None or energy_box is None or not premises:
        raise MissingPremise('JOINT_RATE_ENERGY_ERROR_PREMISES_REQUIRED')
    if len(gamma_box)!=3 or len(energy_box)!=3:raise ContractError('BOX_SHAPE')
    boxes=list(gamma_box)+list(energy_box)
    for b in boxes:
        if len(b)!=2 or exact(b[0])>exact(b[1]):raise ContractError('BOX_ORDER')
    mid=[(a+b)/2 for a,b in boxes];rad=[(b-a)/2 for a,b in boxes]
    center=project(state,Moments(tuple(mid[:3]),tuple(mid[3:])),chi_ev)
    radii={k:F(0) for k in center}
    for j,r in enumerate(rad):
        v=[F(0)]*6;v[j]=F(1)
        col=project(state,Moments(tuple(v[:3]),tuple(v[3:])),chi_ev)
        for k in radii:radii[k]+=abs(col[k])*r
    return {k:(v-radii[k],v+radii[k]) for k,v in center.items()}


def temporal_jump_from_rule_difference(*args, **kwargs):
    """E4 quadrature alternatives are not left/right time traces."""
    raise MissingPremise('ONE_SIDED_SAME_CONTINUOUS_TARGET_TRACES_REQUIRED')
