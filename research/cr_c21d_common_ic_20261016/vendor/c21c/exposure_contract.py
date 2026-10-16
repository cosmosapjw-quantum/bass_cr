"""C21C independent positive exact-pair *exposure* and native point-rate seam.

Research-only.  The exposure-averaged rate is NOT a drop-in replacement for an
endpoint backward-Euler per-absorber rate.  The two lanes have separate types.
Inputs/outputs are normalized per TOTAL H nucleus, not per neutral H atom.
No Case-A/CI/RR/DR/thermal/native Rust invocation is performed by this module.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Literal, Sequence

EV_ERG = 1.602176634e-12
BIND_EV = (13.598434599702, 24.587389011, 54.41776)
A_REF = 1.0 / 21.0


def good(*v: float) -> bool:
    return all(math.isfinite(float(x)) and x >= 0.0 for x in v)


def exprelminus(z: float) -> float:
    """Positive (1-exp(-z))/z, with a cancellation-free z->0 limit."""
    if not good(z):
        raise ValueError("nonnegative finite optical increment required")
    if z == 0.0:
        return 1.0
    if z < 1.0e-5:
        return 1-z/2+z*z/6-z**3/24+z**4/120
    return -math.expm1(-z)/z


@dataclass(frozen=True)
class PairExposure:
    photon_before: float
    absorber_before: float
    photon_after: float
    absorber_after: float
    events_per_H: float
    absorber_exposure_H_s: float
    photon_exposure_H_s: float
    elapsed_s: float
    rate_coefficient_s: float

    @property
    def gamma_exposure_s(self) -> float:
        if self.absorber_exposure_H_s == 0.0:
            if self.events_per_H:
                raise ValueError("event with zero absorber exposure")
            return 0.0
        return self.events_per_H/self.absorber_exposure_H_s

    @property
    def gamma_endpoint_BE_s(self) -> float | None:
        if self.elapsed_s == 0.0 or self.absorber_after == 0.0:
            return None if self.events_per_H > 0 else 0.0
        return self.events_per_H/(self.elapsed_s*self.absorber_after)

    def validate(self) -> None:
        if not good(self.photon_before,self.absorber_before,self.photon_after,
                    self.absorber_after,self.events_per_H,self.absorber_exposure_H_s,
                    self.photon_exposure_H_s,self.elapsed_s,self.rate_coefficient_s):
            raise ValueError("nonpositive/nonfinite exact pair")
        scale=max(1.0,self.photon_before,self.absorber_before)
        if abs((self.photon_before-self.photon_after)-self.events_per_H)>2e-14*scale:
            raise ValueError("photon event ledger mismatch")
        if abs((self.absorber_before-self.absorber_after)-self.events_per_H)>2e-14*scale:
            raise ValueError("absorber event ledger mismatch")
        if self.absorber_exposure_H_s > 0:
            # Microscopic event integrals: dN/dt=-kNA. NOT equal to k*∫A dt alone.
            if self.events_per_H > self.photon_before*(1+1e-13):
                raise ValueError("pair events exceed initial photons")


def exact_pair_exposure(photon: float, absorber: float,
                        coefficient: float, elapsed: float) -> PairExposure:
    """Solve P' = A' = -coefficient*P*A with exact ∫Pdt, ∫Adt.

    `coefficient` is s^-1 because P,A are per-H dimensionless stocks.
    Robust even when z=coefficient*abs(P-A)*elapsed is small or large.
    """
    if not good(photon,absorber,coefficient,elapsed):
        raise ValueError("pair domain")
    if photon == 0 or absorber == 0 or coefficient == 0 or elapsed == 0:
        p=PairExposure(photon,absorber,photon,absorber,0.0,
                       absorber*elapsed,photon*elapsed,elapsed,coefficient)
        p.validate()
        return p
    d=abs(photon-absorber)
    m=min(photon,absorber)
    z=coefficient*d*elapsed
    if not math.isfinite(z):
        raise ValueError("unbounded coefficient-time domain")
    phi=coefficient*elapsed*exprelminus(z)
    if not math.isfinite(phi):
        raise ValueError("nonfinite integrated pair exposure")
    theta=-math.expm1(-z)
    denom=1+m*phi
    if not math.isfinite(denom):
        raise ValueError("nonfinite positive pair denominator")
    small_after=m*math.exp(-z)/denom
    loss=m*(theta+m*phi)/denom
    # Represent the minority and their shared difference rather than subtracting
    # a nearly saturated loss from the larger stock.
    if photon>=absorber:
        photon_after=d+small_after
        absorber_after=small_after
        abs_extra=0.0
        pho_extra=d*elapsed
    else:
        photon_after=small_after
        absorber_after=d+small_after
        abs_extra=d*elapsed
        pho_extra=0.0
    common_exposure=math.log1p(m*phi)/coefficient
    p=PairExposure(photon,absorber,photon_after,absorber_after,loss,
                   abs_extra+common_exposure,pho_extra+common_exposure,
                   elapsed,coefficient)
    p.validate()
    return p


def q20_to_qref(q20:float)->float:
    if not math.isfinite(q20) or q20<=0:
        raise ValueError("positive photon q20 required")
    return q20/A_REF


def energy_from_qref(qref:float,scale_a:float)->float:
    if not good(scale_a) or scale_a<=0 or not math.isfinite(qref) or qref<=0:
        raise ValueError("positive epoch and photon energy required")
    return qref*A_REF/scale_a


@dataclass(frozen=True)
class NativeRateBridge:
    """Explicitly distinct exposure and endpoint BE per-absorber photo-rate lanes."""
    events_H: tuple[float,float,float]
    photoheat_ev_H: tuple[float,float,float]
    exposure_H_s: tuple[float,float,float]
    absorber_end_H: tuple[float,float,float]
    delta_t_s: float
    nH_total_cm3: float
    gamma_exposure_s: tuple[float,float,float]
    heat_exposure_erg_abs_s: tuple[float,float,float]
    gamma_endpoint_s: tuple[float|None,float|None,float|None]
    heat_endpoint_erg_abs_s: tuple[float|None,float|None,float|None]
    endpoint_condition: tuple[float|None,float|None,float|None]
    status: tuple[str,str,str]
    events_cm3_s: tuple[float,float,float]


def native_photo_rates(events_per_H: Sequence[float], heat_ev_per_H: Sequence[float],
                       absorber_exposure_H_s: Sequence[float], absorber_endpoint_H: Sequence[float],
                       dt_s: float, nH_total_cm3: float,
                       ill_conditioned_ratio:float=1.0e6) -> NativeRateBridge:
    """For physical-time exposure, construct two noninterchangeable rate lanes.

    Never use `gamma_exposure_s` as `igm_point_rhs` endpoint BE gamma without a
    time-integrated reaction adapter. `gamma_endpoint_s` may be undefined when
    no absorber survives. The code does not clip/regularize depleted gas.
    """
    arrays=[tuple(map(float,v)) for v in (events_per_H,heat_ev_per_H,
                                         absorber_exposure_H_s,absorber_endpoint_H)]
    if any(len(v)!=3 for v in arrays) or not good(dt_s,nH_total_cm3,ill_conditioned_ratio) or dt_s<=0 or nH_total_cm3<=0 or ill_conditioned_ratio<=1:
        raise ValueError("native adapter domain or shape")
    if not all(good(*v) for v in arrays):
        raise ValueError("negative/unbounded source moments/exposure")
    events,heat,expos,end=arrays
    averaged=[];averaged_heat=[];terminal=[];terminal_heat=[];condition=[];status=[]
    for e,q,integrated,afinal in zip(events,heat,expos,end):
        if integrated==0.0 and e>0.0:
            raise ValueError("photon event cannot occur with no true absorber exposure")
        gamma_exp=e/integrated if integrated>0.0 else 0.0
        power_exp=q*EV_ERG/integrated if integrated>0.0 else 0.0
        averaged.append(gamma_exp);averaged_heat.append(power_exp)
        if afinal==0.0:
            if e>0:
                terminal.append(None);terminal_heat.append(None);condition.append(None)
                status.append("HOLD_ENDPOINT_RATE_UNREPRESENTABLE")
            else:
                terminal.append(0.0);terminal_heat.append(0.0);condition.append(0.0)
                status.append("ZERO_EVENTS_ZERO_ABSORBER")
            continue
        t=e/(dt_s*afinal)
        th=q*EV_ERG/(dt_s*afinal)
        relative=(integrated/(dt_s*afinal)) if integrated>0 else 0.0
        terminal.append(t);terminal_heat.append(th);condition.append(relative)
        status.append("HOLD_ENDPOINT_ILL_CONDITIONED" if relative>ill_conditioned_ratio else "ENDPOINT_BE_REPRESENTABLE")
    rates=[e*nH_total_cm3/dt_s for e in events]
    return NativeRateBridge(events,heat,expos,end,dt_s,nH_total_cm3,
       tuple(averaged),tuple(averaged_heat),tuple(terminal),tuple(terminal_heat),
       tuple(condition),tuple(status),tuple(rates))


def pair_to_native(p:PairExposure, energy_ev:float, species:int,
                   proper_nH_cm3:float)->NativeRateBridge:
    """A single exact pair channel maps into its own slot, not a full H/He step."""
    if species not in range(3) or not good(energy_ev,proper_nH_cm3) or energy_ev < BIND_EV[species]:
        raise ValueError("invalid species, energy, or total hydrogen density")
    event=[0.]*3;heat=[0.]*3;exp=[0.]*3;end=[0.]*3
    event[species]=p.events_per_H
    heat[species]=p.events_per_H*(energy_ev-BIND_EV[species])
    exp[species]=p.absorber_exposure_H_s
    end[species]=p.absorber_after
    return native_photo_rates(event,heat,exp,end,p.elapsed_s,proper_nH_cm3)
