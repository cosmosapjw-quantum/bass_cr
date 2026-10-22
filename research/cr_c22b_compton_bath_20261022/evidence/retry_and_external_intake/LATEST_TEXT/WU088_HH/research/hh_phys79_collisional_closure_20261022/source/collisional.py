"""Domain-guarded finite CI and D/H nonradiative charge-exchange operator.

Units: K, cm^-3, cm^3/s, eV, proper seconds, abundance/reference H1.
The CI rate's fitted dE is distinct from the global thermodynamic ionic
potential. D uses I_D-I_H=43*k_B K; other potentials are the pinned PHYS78
rounded elemental values. D/T CI kinetics share the H fit explicitly.
No PI/RR/cosmological trajectory is silently modified by this module.
He/Li charge transfer with unresolved final-state/photon energy is not active.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from phys78_bridge import atomic

KB_EV_K = atomic.KB_EV_K
D_DEFECT_K = 43.0
D_DEFECT_EV = D_DEFECT_K * KB_EV_K
CI_LABELS = ('H_I','He_I','He_II','Li_I','Li_II','Li_III')
# dE/eV, P, A/(cm^3/s), X, K, Tmin/eV, Tmax/keV.
# Voronov1997 author table first six records, numeric transcription.
CI_FITS = (
    (13.6,0.,2.91e-8,.2320,.39,1.,20.),
    (24.6,0.,1.75e-8,.1800,.35,1.,20.),
    (54.4,1.,2.05e-9,.2650,.25,3.,20.),
    (5.4,0.,1.39e-7,.4380,.41,1.,20.),
    (75.6,1.,2.01e-9,.2090,.23,4.,20.),
    (122.4,1.,9.60e-10,.5820,.17,5.,20.),
)
CI_MIN_K = np.array([r[5]/KB_EV_K for r in CI_FITS])
CI_MAX_K = np.array([1000*r[6]/KB_EV_K for r in CI_FITS])
ELEMENT_ROW = {(1,0):0,(2,0):1,(2,1):2,(3,0):3,(3,1):4,(3,2):5}
MODEL_ID = 'PHYS79_DOMAIN_GUARDED_CI_DCX_V1'

class RateDomainError(ValueError):
    """A requested sourced rate is not admitted at the supplied temperature."""

class UnresolvedClosureError(ValueError):
    """The full requested physical process has an unresolved source obligation."""

def _temperature(T):
    t = float(T)
    if not math.isfinite(t) or t <= 0:
        raise RateDomainError('TEMPERATURE_MUST_BE_FINITE_POSITIVE')
    return t

def ci_domain_mask(temperature_K):
    t = np.asarray(temperature_K,dtype=float)
    return np.isfinite(t[...,None]) & (t[...,None]>=CI_MIN_K) & (t[...,None]<=CI_MAX_K)

def ci_rate(row, temperature_K):
    """One elemental ground-ion electron impact rate; no extrapolation/floor."""
    if isinstance(row,bool) or not isinstance(row,(int,np.integer)) or not 0<=row<6:
        raise ValueError('UNKNOWN_CI_ROW')
    t = _temperature(temperature_K)
    if not CI_MIN_K[row] <= t <= CI_MAX_K[row]:
        raise RateDomainError(f'CI_OUTSIDE_AUTHOR_DOMAIN:{CI_LABELS[row]}:{t!r}')
    dE,p,a,x,k,_,_ = CI_FITS[row]
    u = dE/(KB_EV_K*t)
    rate = math.exp(math.log(a)+math.log1p(p*math.sqrt(u))-math.log(x+u)+k*math.log(u)-u)
    if not math.isfinite(rate) or rate<=0:
        raise ArithmeticError('CI_NONPOSITIVE_OR_NONFINITE_INSIDE_DOMAIN')
    return rate

def d_cx_rates(temperature_K, closure='detailed_balance'):
    """D+H+ -> D+ +H, reverse, in cm^3/s.

    raw_fit is Savin2002 Eq6/Table2's two independent fits, each with its
    own source approximation. detailed_balance retains the reverse fit and
    sets forward/reverse=exp(-43/T) in a declared equal-charge-mass,
    ground-degeneracy model. It is a NEW model, not the original forward fit
    or a guarantee of that fit's quoted6% accuracy across the whole domain.
    """
    t=_temperature(temperature_K)
    if not 2.7<=t<=2e5:
        raise RateDomainError('D_CX_OUTSIDE_SAVIN_2P7_TO_2E5_K')
    reverse=2.06e-10*t**.396*math.exp(-33./t)+2.03e-9*t**(-.332)
    if closure=='detailed_balance':
        forward=reverse*math.exp(-D_DEFECT_K/t)
    elif closure=='raw_fit':
        forward=2.00e-10*t**.402*math.exp(-37.1/t)-3.31e-17*t**1.48
    else:
        raise ValueError('UNKNOWN_D_CX_CLOSURE')
    if not (math.isfinite(forward) and math.isfinite(reverse) and forward>0 and reverse>0):
        raise ArithmeticError('D_CX_NONPOSITIVE_OR_NONFINITE')
    return forward,reverse

def _immutable(value, dtype=float):
    a=np.ascontiguousarray(value,dtype=dtype)
    return np.frombuffer(a.tobytes(),dtype=a.dtype).reshape(a.shape)

def _particle_state(y):
    y=np.asarray(y,dtype=float)
    if y.shape!=(atomic.N_SPECIES,) or not np.isfinite(y).all() or np.any(y<0):
        raise ValueError('SPECIES_MUST_BE_FINITE_NONNEGATIVE_21_VECTOR')
    with np.errstate(over='ignore',invalid='ignore'):
        xe=float(atomic.CHARGE@y);N=float(y.sum()+xe)
    if not math.isfinite(xe) or not math.isfinite(N) or N<=0:
        raise ValueError('PARTICLE_NUMBER_MUST_BE_FINITE_POSITIVE')
    return y,xe,N

def ionic_potential_eV():
    """Global positive cumulative potential, with the explicit D43K correction."""
    eps=np.zeros(atomic.N_SPECIES)
    for i,s in enumerate(atomic.SPECIES):
        if s.charge<s.atomic_number:
            eps[i+1]=eps[i]+atomic.PHOTO_COEFFICIENTS[ELEMENT_ROW[(s.atomic_number,s.charge)]][0]
    eps[atomic.SPECIES_INDEX['D_II']]+=D_DEFECT_EV
    return _immutable(eps)

@dataclass(frozen=True)
class CollisionRhs:
    d_species_per_H_dt: np.ndarray
    heat_eV_per_H_s: float
    binding_derivative_eV_per_H_s: float
    d_electron_per_H_dt: float
    event_per_H_s: np.ndarray
    event_names: tuple
    energy_ledger_residual_eV_per_H_s: float
    electron_abundance_per_H: float
    binding_eV_per_H: float
    temperature_derivative_K_per_s: float
    diagnostics: dict

class CollisionNetwork:
    """An explicitly selected subnetwork, with immutable stoichiometry.

    ci_rows must be supplied: () is the D-CX-only operator; (0,1,3) is
    neutral CI only; tuple(range(6)) admits all13 isotopic CI transitions
    ONLY inside the intersection of those rate domains. A zero population
    does not authorize evaluating an out-of-domain rate or suppressing it.
    """
    def __init__(self, *, ci_rows, d_cx, d_cx_closure='detailed_balance'):
        ci_rows=tuple(ci_rows)
        if (len(ci_rows)!=len(set(ci_rows)) or any(isinstance(i,bool) or not isinstance(i,(int,np.integer)) or not 0<=i<6 for i in ci_rows)):
            raise ValueError('CI_ROWS_MUST_BE_UNIQUE_KNOWN_INDICES')
        if not isinstance(d_cx,bool):raise ValueError('D_CX_SELECTION_MUST_BE_BOOL')
        if d_cx_closure not in ('detailed_balance','raw_fit'):raise ValueError('UNKNOWN_D_CX_CLOSURE')
        self.ci_rows=ci_rows;self.d_cx=d_cx;self.d_cx_closure=d_cx_closure
        self.binding_eV=ionic_potential_eV()
        cols=[];names=[];specs=[]
        for i,s in enumerate(atomic.SPECIES):
            if s.charge>=s.atomic_number:continue
            row=ELEMENT_ROW[(s.atomic_number,s.charge)]
            if row not in ci_rows:continue
            col=np.zeros(atomic.N_SPECIES,dtype=np.int64);col[i]=-1;col[i+1]=1
            cols.append(col);names.append('CI:'+s.name);specs.append(('ci',row,i,-1))
        ix=atomic.SPECIES_INDEX
        if d_cx:
            col=np.zeros(atomic.N_SPECIES,dtype=np.int64)
            col[ix['D_I']]=-1;col[ix['H1_II']]=-1;col[ix['D_II']]=1;col[ix['H1_I']]=1
            cols.extend([col,-col]);names.extend(['CX:D_I+H1_II','CX:D_II+H1_I'])
            specs.extend([('d_cx',0,ix['D_I'],ix['H1_II']),('d_cx',1,ix['D_II'],ix['H1_I'])])
        self.stoichiometry=_immutable(np.column_stack(cols) if cols else np.zeros((atomic.N_SPECIES,0)),np.int64)
        self.event_names=tuple(names);self.event_specs=tuple(specs)
        self.delta_binding_eV=_immutable(self.binding_eV@self.stoichiometry)
        self.delta_electron=_immutable(atomic.CHARGE@self.stoichiometry)
        if np.any(atomic.ISOTOPE_SUM@self.stoichiometry!=0):raise ArithmeticError('NUCLEUS_STOICHIOMETRY_DEFECT')

    def rate_coefficients(self,T_K):
        t=_temperature(T_K)
        ci={r:ci_rate(r,t) for r in self.ci_rows}
        cx=d_cx_rates(t,self.d_cx_closure) if self.d_cx else ()
        return np.array([ci[row] if kind=='ci' else cx[row] for kind,row,_,_ in self.event_specs])

    def rhs(self,T_K,nH_cm3,species_abundance_per_H,*,H_per_s=0.):
        t=_temperature(T_K);nH=float(nH_cm3);H=float(H_per_s)
        y,xe,N=_particle_state(species_abundance_per_H)
        if not math.isfinite(nH) or nH<=0:raise ValueError('REFERENCE_DENSITY_MUST_BE_FINITE_POSITIVE')
        if not math.isfinite(H):raise ValueError('HUBBLE_RATE_MUST_BE_FINITE')
        coeff=self.rate_coefficients(t)
        flux=np.array([nH*y[a]*(xe if kind=='ci' else y[b])*k for (kind,_,a,b),k in zip(self.event_specs,coeff)])
        dydt=self.stoichiometry@flux
        # Sum small reaction defects directly. Subtracting the two large H/D
        # ionic potentials after forming dY loses precision in the 43K defect.
        binding_dot=math.fsum(float(de)*float(v) for de,v in zip(self.delta_binding_eV,flux))
        heat=-binding_dot
        binding_dot_state=float(self.binding_eV@dydt)
        constituent_scale=float(np.abs(self.binding_eV*dydt).sum())
        binding=float(self.binding_eV@y)
        dxedt=float(atomic.CHARGE@dydt)
        dT=-2*H*t+2*heat/(3*KB_EV_K*N)-t*dxedt/N
        if not np.isfinite(np.r_[dydt,flux,heat,binding_dot,binding_dot_state,constituent_scale,binding,dxedt,dT]).all():
            raise ArithmeticError('NONFINITE_COLLISION_RESULT')
        return CollisionRhs(_immutable(dydt),heat,binding_dot,dxedt,_immutable(flux),self.event_names,
            heat+binding_dot,xe,binding,dT,
            {'model':MODEL_ID,'ci_rows':self.ci_rows,'d_cx':self.d_cx,'d_cx_closure':self.d_cx_closure,
             'units':'K,cm^-3,eV,proper_s,per_reference_H1','escaping_photon_energy':0.,
             'species_projection':'NONE','isotope_atomic_kinetics':'ELEMENT_SHARED_CI',
             'ionic_potential':'PHYS78_PLUS_D43K','full_cosmological_admission':'NOT_ISSUED',
             'binding_derivative_direct_state_eV_per_H_s':binding_dot_state,
             'binding_derivative_direct_minus_event_eV_per_H_s':binding_dot_state-binding_dot,
             'binding_derivative_constituent_energy_scale_eV_per_H_s':constituent_scale})

    def thermal_energy(self,T_K,y):
        y,xe,N=_particle_state(y)
        u=1.5*KB_EV_K*_temperature(T_K)*N
        if not math.isfinite(u) or u<=0:raise ValueError('THERMAL_ENERGY_MUST_BE_FINITE_POSITIVE')
        return u

    def temperature(self,u_eV_per_H,y):
        u=float(u_eV_per_H);y,xe,N=_particle_state(y)
        if not math.isfinite(u) or u<=0:raise ValueError('NONPOSITIVE_THERMAL_STATE')
        t=(u/N)*(2/(3*KB_EV_K))
        if not math.isfinite(t) or t<=0:raise ValueError('TEMPERATURE_MUST_BE_FINITE_POSITIVE')
        return t

def require_full_cosmological_admission():
    raise UnresolvedClosureError('OPEN:low_temperature_CI;He_Li_CX_state_and_radiative_energy;D_PI_RR_potential_adapter;z20_initial_charge')
