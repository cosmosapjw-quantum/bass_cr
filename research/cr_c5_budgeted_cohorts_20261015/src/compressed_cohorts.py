"""Bounded-memory, reaction-aware photon cohort compression research prototype.

Every accepted merge is positive and preserves photon count and first energy moment.
It is accepted only if all photoionization thresholds are avoided by the *whole*
forecast redshift tube, and if the sum of analytical frozen-neutral BE-event and
photoheat Lipschitz upper bounds stays within declared budgets.

This is an exact-real functional error estimate evaluated in floating arithmetic,
NOT a directed floating-point enclosure or a full coupled transport error bound.
A budget hold is explicit and transactional; no loss of physical information is
silently hidden behind a compressed output.

E in eV; n in photon count/H; rho in cm^-3; time in seconds; c in cm/s.
Signature (-,+,+,+) and proper time inherited from threshold_rt.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import hypot, sqrt, isfinite
from typing import Sequence
from threshold_rt import (
    CohortTransport, ATOMIC, ION_NAMES, C_CM_S, SOURCE_EDGES,
    frozen_source, verner,
)


class CompressionHold(RuntimeError):
    """A mathematical budget/threshold condition prevented a requested cap."""


@dataclass(frozen=True)
class CompressionCertificate:
    initial_cohorts: int
    final_cohorts: int
    merges: int
    event_absolute_bounds: tuple[float, float, float]
    heat_absolute_bounds_eV: tuple[float, float, float]
    forecast_min_redshift_ratio: float
    baseline_density_cm3: tuple[float, float, float]
    baseline_dt_s: float
    status: str = 'LOCAL_FROZEN_NEUTRAL_ONE_STEP_EXACT_REAL_FORMULA_FLOAT_EVALUATED'


def _validate_neutrals(neutrals_cm3: Sequence[float], dt_s: float) -> tuple[float,float,float]:
    if len(neutrals_cm3)!=3 or any(not isfinite(x) or x < 0 for x in neutrals_cm3):
        raise ValueError('three finite nonnegative neutral proper densities required')
    if not isfinite(dt_s) or dt_s<0:
        raise ValueError('finite nonnegative proper timestep required')
    return tuple(float(x) for x in neutrals_cm3)


def _min_dist(lo: float, hi: float, target: float) -> float:
    return 0.0 if lo<=target<=hi else min(abs(lo-target),abs(hi-target))


def _verner_derivative_bound(kind:str, lo:float, hi:float) -> tuple[float,float]:
    """Conservative sup(|sigma|), sup(|d sigma/dE|) on a smooth interval.

    This bound is analytic from the published Verner expression, not fitted to
    derivatives on sampled energies. If interval straddles the absorber's step,
    it is rejected, including threshold equality from the active side.
    """
    if not (isfinite(lo) and isfinite(hi) and 0<lo<=hi<=50000):
        raise ValueError('invalid Verner interval')
    eth,e0,s0,ya,p,yw,y0,y1=ATOMIC[kind]
    if hi<eth: return 0.,0.
    if lo<eth<=hi: raise CompressionHold('HOLD_THRESHOLD_IN_FORECAST_TUBE')
    x0=lo/e0-y0;x1=hi/e0-y0
    X=max(abs(x0),abs(x1)); Xm1=max(abs(x0-1),abs(x1-1))
    ymin=hypot(_min_dist(x0,x1,0.),y1)
    ymax=hypot(X,y1)
    amin=_min_dist(x0,x1,1.)**2+yw*yw
    amax=Xm1*Xm1+yw*yw
    exponent=p/2-5.5
    if ymin<=0 or amin<=0:raise CompressionHold('HOLD_DEGENERATE_VERNER_LOG_DERIVATIVE')
    power=(ymin if exponent<0 else ymax)**exponent
    sigma_max=s0*amax*power*1e-18   # (1+sqrt(y/ya))^-p <= 1, p>0
    log_slope=(2*Xm1/(e0*amin)
               +(abs(exponent)+p/2)*X/(e0*ymin*ymin))
    upper=sigma_max*log_slope
    if not(isfinite(upper) and isfinite(sigma_max)):
        raise CompressionHold('HOLD_UNBOUNDED_RATE_SLOPE')
    # Float evaluated, with a small numerical cushion; not a directed proof.
    return sigma_max*1.0000000001,upper*1.0000000001


def one_step_pair_bounds(
    e1:float,n1:float,e2:float,n2:float,
    neutrals_cm3: Sequence[float],dt_s:float,
    min_future_redshift_ratio:float,
) -> tuple[tuple[float,...], tuple[float,...]]:
    """Upper bounds on a single merger's three BE events and direct heat readouts.

    For EVERY ratio r in [min_ratio,1], provided the same fixed neutral density
    and time step apply. Does not bound differential nonlinear gas coupling.
    """
    nn=_validate_neutrals(neutrals_cm3,dt_s)
    if not (0<min_future_redshift_ratio<=1 and isfinite(min_future_redshift_ratio)):
        raise ValueError('forecast redshift must be within (0,1]')
    if not(0<e1<=e2<=50000. and n1>=0 and n2>=0):
        raise ValueError('nonnegative ordered photon cohorts in Verner fit support required')
    if not all(isfinite(x) for x in (e1,e2,n1,n2)):
        raise ValueError('nonfinite photon cohort')
    total=n1+n2
    if total==0 or e1==e2:
        return (0.,0.,0.),(0.,0.,0.)
    lo=min_future_redshift_ratio*e1; hi=e2
    if lo<SOURCE_EDGES[0]:
        raise CompressionHold('HOLD_BOUNDARY_CROSSING_FORECAST')
    derivative=[]; active=[]
    for name,density in zip(ION_NAMES,nn):
        eth=ATOMIC[name][0]
        if lo<eth<=hi:
            raise CompressionHold('HOLD_THRESHOLD_CROSSING_FORECAST')
        if hi<eth:
            derivative.append(0.)
            active.append(False)
            continue
        _,slope=_verner_derivative_bound(name,lo,hi)
        derivative.append(dt_s*C_CM_S*density*slope)
        active.append(True)
    sum_d=sum(derivative)
    mean=(n1*e1+n2*e2)/total
    dispersion=n1*abs(e1-mean)+n2*abs(e2-mean)
    events=[];heats=[]
    for k,valid in enumerate(active):
        # |d P_k / dE| <= |d p_k/dE|+sum_j|d p_j/dE| for p/(1+sum p).
        lip=derivative[k]+sum_d
        events.append(lip*dispersion if valid else 0.)
        heat_lip=1.+max(0.,hi-ATOMIC[ION_NAMES[k]][0])*lip if valid else 0.
        heats.append(heat_lip*dispersion)
    return tuple(events),tuple(heats)


def _total_moments(cohorts):
    return sum(n for _,n in cohorts),sum(e*n for e,n in cohorts)


class CompressedCohortTransport(CohortTransport):
    """An admitted cap or an explicit hold, never silently unsafe compression.

    If compression is successful, a certificate bounds the pair-merge error for
    FROZEN-NEUTRAL ONE-STEP BE events and heat over a future redshift tube. The
    certificate is local to each compress operation and is NOT an error bound for
    arbitrary repeated gas/RT evolution.
    """
    def __init__(self,cohorts:Sequence[tuple[float,float]],max_cohorts:int=32):
        super().__init__(cohorts)
        if any(e>50000. for e,_ in self.cohorts):
            raise ValueError('above Verner 50keV support')
        if isinstance(max_cohorts,bool) or not isinstance(max_cohorts,int) or max_cohorts<1:
            raise ValueError('max_cohorts must be a positive integer')
        self.max_cohorts=max_cohorts
        self.last_certificate=None

    @classmethod
    def frozen_source(cls,axis:int=16,max_cohorts:int=32):
        return cls(frozen_source(axis),max_cohorts=max_cohorts)

    def compress(self,neutrals_cm3:Sequence[float],dt_s:float,
                 min_future_redshift_ratio:float=1.,
                 event_abs_budget:float=0.01,
                 heat_abs_budget_eV:float=0.1):
        nn=_validate_neutrals(neutrals_cm3,dt_s)
        if any(not isfinite(v) or v<0 for v in (event_abs_budget,heat_abs_budget_eV)):
            raise ValueError('finite nonnegative budgets required')
        if not isfinite(min_future_redshift_ratio) or not(0<min_future_redshift_ratio<=1):
            raise ValueError('invalid redshift forecast')
        trial=sorted((float(e),float(n)) for e,n in self.cohorts if n>0)
        initial_count=len(trial)
        old_moments=_total_moments(trial)
        event_spent=[0.]*3;heat_spent=[0.]*3
        merges=0
        while len(trial)>self.max_cohorts:
            best=None
            for i in range(len(trial)-1):
                (e1,n1),(e2,n2)=trial[i:i+2]
                try:
                    eb,hb=one_step_pair_bounds(e1,n1,e2,n2,nn,dt_s,min_future_redshift_ratio)
                except CompressionHold:
                    continue
                if any(event_spent[k]+eb[k]>event_abs_budget for k in range(3)):
                    continue
                if any(heat_spent[k]+hb[k]>heat_abs_budget_eV for k in range(3)):
                    continue
                score=max(max(eb,default=0.)/(event_abs_budget or 1),
                          max(hb,default=0.)/(heat_abs_budget_eV or 1))
                if best is None or (score,e2-e1,i)<(best[0],best[1],best[2]):
                    best=(score,e2-e1,i,eb,hb)
            if best is None:
                # Transactional: prior self.cohorts and certificate remain intact.
                raise CompressionHold(
                    f'HOLD_BUDGET_OR_THRESHOLD target={self.max_cohorts} '
                    f'currently={len(trial)} n_initial={initial_count}')
            _,_,i,eb,hb=best
            (e1,n1),(e2,n2)=trial[i:i+2]
            n=n1+n2
            E=(n1*e1+n2*e2)/n
            trial[i:i+2]=[(E,n)]
            for k in range(3):
                event_spent[k]+=eb[k];heat_spent[k]+=hb[k]
            merges+=1
        new_moments=_total_moments(trial)
        if not (abs(old_moments[0]-new_moments[0])<=3e-13*max(old_moments[0],1)
                and abs(old_moments[1]-new_moments[1])<=3e-13*max(old_moments[1],1)):
            raise ArithmeticError('number or energy moment changed')
        cert=CompressionCertificate(initial_count,len(trial),merges,
                                    tuple(event_spent),tuple(heat_spent),
                                    min_future_redshift_ratio,nn,dt_s)
        self.cohorts=trial
        self.last_certificate=cert
        return cert

    def inject_and_compress(self,injection:Sequence[tuple[float,float]],
                            neutrals_cm3:Sequence[float],dt_s:float,
                            min_future_redshift_ratio:float=1.,
                            event_abs_budget:float=0.01,
                            heat_abs_budget_eV:float=0.1):
        # Source injection is committed only after acceptance of the full cap.
        combined=type(self)([ *self.cohorts, *injection ],self.max_cohorts)
        certificate=combined.compress(neutrals_cm3,dt_s,min_future_redshift_ratio,
                                      event_abs_budget,heat_abs_budget_eV)
        self.cohorts=combined.cohorts
        self.last_certificate=certificate
        return certificate

    def redshift(self,energy_ratio:float):
        """Redshift physical energies including separately versioned high-energy
        SOURCE07 q-reference rays (up to its supplied 432.23 eV). No angular
        Jacobian is applied here: the q-ray producer owns that factor exactly once.
        """
        if not isfinite(energy_ratio) or energy_ratio<=0:
            raise ValueError('invalid redshift factor')
        before=self.moments();next_state=[];bound_n=bound_u=0.
        for energy,n in self.cohorts:
            shifted=energy*energy_ratio
            if shifted<SOURCE_EDGES[0]:
                bound_n+=n;bound_u+=n*shifted
            elif shifted>50000.:
                raise ValueError('above Verner fit energy domain')
            else:
                next_state.append((shifted,n))
        self.cohorts=next_state
        after=self.moments()
        work=before[1]-after[1]-bound_u
        self.last_certificate=None
        return {'boundary_count':bound_n,'boundary_energy_eV':bound_u,
                'photon_work_eV':work,
                'number_residual':before[0]-after[0]-bound_n,
                'energy_residual_eV':before[1]-after[1]-bound_u-work}

    def absorb_backward_euler(self,neutrals_cm3:Sequence[float],dt_s:float):
        result=super().absorb_backward_euler(neutrals_cm3,dt_s)
        self.last_certificate=None
        return result


def frozen_be_readout(cohorts,neutrals_cm3,dt_s,ratio=1.):
    """Species-resolved BE event and heat of a source cohort state at redshift r.

    Packet count at the initial characteristic is kept unchanged. This computes
    only a single frozen-neutral step; no intermediate source or opacity coupling.
    """
    nn=_validate_neutrals(neutrals_cm3,dt_s)
    ev=[0.]*3;heat=[0.]*3
    for E,n in cohorts:
        e=ratio*E
        if e<SOURCE_EDGES[0]:continue
        if e>50000.:raise ValueError('forecast above Verner energy support')
        rates=[dt_s*C_CM_S*d*verner(name,e) for d,name in zip(nn,ION_NAMES)]
        n1=n/(1+sum(rates))
        for k,rate in enumerate(rates):
            de=n1*rate
            ev[k]+=de
            heat[k]+=de*(e-ATOMIC[ION_NAMES[k]][0])
    return tuple(ev),tuple(heat)
