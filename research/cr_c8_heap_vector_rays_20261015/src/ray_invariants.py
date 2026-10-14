"""Owner-preserving 1+3 photon moment check for independent Bianchi ray lanes.

This module does NOT generate k_i, redshift E, tetrads, or the source R*J angular
Jacobian. The rei_bianchi SOURCE07 producer owns those and supplies fixed local
normal-tetrad direction for each ray at this time. Do not merge different ray ID,
source-epoch, or proper clock: an energy-only merge across directions could conserve
scalar energy and break total spatial photon momentum/current.

Metric (-,+,+,+), u.u=-1, e.e=1, u.e=0, p^a=(E/c)(u^a+e^a).
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite,sqrt
from typing import Sequence
from threshold_rt import C_CM_S
from ray_parallel import compress_rays


@dataclass(frozen=True)
class RayLane:
    ray_id: str
    source_epoch_s: float
    clock_s: float
    direction: tuple[float,float,float]
    cohorts: tuple[tuple[float,float],...]

    def __post_init__(self):
        if not self.ray_id or not(isfinite(self.source_epoch_s) and isfinite(self.clock_s)):
            raise ValueError('ray identity and finite clock/source epoch are required')
        if self.source_epoch_s>self.clock_s:
            raise ValueError('source epoch cannot be after current proper clock')
        if len(self.direction)!=3 or not all(isfinite(v) for v in self.direction):
            raise ValueError('finite 3-vector ray required')
        norm2=sum(x*x for x in self.direction)
        if abs(norm2-1.)>1.e-12:
            raise ValueError('normal-tetrad ray direction must be unit length')
        for E,n in self.cohorts:
            if not(isfinite(E) and isfinite(n)) or not 0<E<=50000 or n<0:
                raise ValueError('physical photon energy/count outside domain')


def normal_tetrad_photon_moments(lanes:Sequence[RayLane]):
    """(total photon count, total physical energy, spatial energy vector/c).

    For a fixed current normal tetrad and all counts normalized by same per-H
    source measure, this is the component form of sum N*p^a.
    """
    num=energy=0.
    momentum=[0.]*3
    for lane in lanes:
        for E,n in lane.cohorts:
            num+=n; energy+=E*n
            for k in range(3):momentum[k]+=E*n*lane.direction[k]/C_CM_S
    return (num,energy,tuple(momentum))


def compress_bianchi_ray_lanes(lanes:Sequence[RayLane], caps:Sequence[int],
                              neutrals_cm3:Sequence[Sequence[float]],dt_s:Sequence[float],
                              min_redshift_ratio:Sequence[float],
                              event_budget=.01,heat_budget_eV=.1,workers=1):
    """Atomic all-lane compression, immutable inputs and preserved ray identities.

    No angular reweighting: source Jacobian must already have been applied once by
    owner SOURCE07. Budgets are per ray per short frozen-neutral step, not global.
    """
    keys=[(x.ray_id,x.source_epoch_s,x.clock_s) for x in lanes]
    if len(keys)!=len(set(keys)):
        raise ValueError('duplicate ray/epoch/clock lane; aggregate it before certification')
    results=compress_rays([x.cohorts for x in lanes],caps,neutrals_cm3,dt_s,
                         min_redshift_ratio,event_budget,heat_budget_eV,workers)
    out=[RayLane(x.ray_id,x.source_epoch_s,x.clock_s,x.direction,tuple(c))
         for x,(c,cert) in zip(lanes,results)]
    # This is a code-level structural invariant check, not an interval theorem.
    before=normal_tetrad_photon_moments(lanes)
    after=normal_tetrad_photon_moments(out)
    if abs(before[0]-after[0])>3e-13*max(1.,before[0]) or abs(before[1]-after[1])>3e-13*max(1.,before[1]):
        raise ArithmeticError('photon number or energy changed')
    for m0,m1 in zip(before[2],after[2]):
        if abs(m0-m1)>3e-13*max(1.e-20,abs(before[1]/C_CM_S)):
            raise ArithmeticError('ray-resolved 3-momentum changed')
    return out,[c for _,c in results]
