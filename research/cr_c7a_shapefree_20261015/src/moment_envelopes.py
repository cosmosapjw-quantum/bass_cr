"""Distribution-free sharp moment envelopes with certified smooth-piece remainder.

A scope-limited mathematical interface for SOURCE07 C7_A: nonnegative photons in a
FIXED reference q-bin with *known physical support* and exact mass/first moment.
Any spectrum with those moments is permitted, including spectral hardening and
mixed source ages. True photoevents/photoelectron heat of frozen proper H/He gas
lie between continuous convex/concave moment envelopes. No assumption of BB50K,
exponential-in-energy maximum entropy, or reusing the original injected spectrum.

Numerical verification tiers:
* mathematically proven interpolation remainder: |g-PL(g)|<=M h²/8 on every
  threshold-free segment using analytically sufficient Verner derivative bounds;
* source float constants are exact dyadics, derivative bounds use the imported
  Decimal85 directed algorithm; node response values use mpmath.iv 55 dps;
* convex hull and moment interpolation performed exactly with Fraction over saved
  outward binary64 upper/lower nodal values. Thus finite arithmetic introduces
  no unrecorded hull tolerance; reference input physical uncertainties are NOT
  included, and a coupled nonlinear cosmological history is NOT certified.

Fit cutoffs 13.60/24.59/54.42 eV are distinct from binding energies
13.598434599702/24.587389011/54.41776 eV. Source-neutral state and proper dt
belong to one genuine owner clock. Unsupported ray-angle mixing is forbidden.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from math import inf, isfinite, nextafter
from typing import Sequence

import mpmath as mp
import numpy as np

from threshold_rt import ATOMIC, ION_NAMES, C_CM_S
from directed_curvature import (
    D, ZERO, ONE, TWO, plus, times, subup, divup, adddown, muldown,
    second_sigma_up,
)

BINDING = (13.598434599702,24.587389011,54.41776)
mp.iv.dps = 55


def _positive_finite(values: Sequence[float], count: int) -> tuple[float, ...]:
    if len(values) != count or any(not isfinite(v) or v < 0 for v in values):
        raise ValueError('expected nonnegative finite physical input')
    return tuple(float(v) for v in values)


def _radius(value: float, up: bool) -> float:
    """Outward conversion for mpmath interval endpoints."""
    return nextafter(nextafter(float(value), inf if up else -inf), inf if up else -inf)


def _iv(x: float):
    if not isfinite(x):
        raise ValueError('finite model input required')
    return mp.iv.mpf(x)


def _verner_iv(ion: str, energy: float, active_side: bool) -> object:
    fit,e0,sigma0,ya,p,yw,y0,y1=ATOMIC[ion]
    if not active_side or energy < fit:
        return mp.iv.mpf(0)
    e=_iv(energy)
    x=e/_iv(e0)-_iv(y0)
    y=mp.iv.sqrt(x*x+_iv(y1)**2)
    a=(x-1)**2+_iv(yw)**2
    return _iv(sigma0)*a*y**(_iv(p)/2-mp.iv.mpf('5.5'))*(1+mp.iv.sqrt(y/_iv(ya)))**(-_iv(p))*_iv(1e-18)


def _response_interval(energy: float, neutrals: tuple[float,...], dt: float,
                       kind: int, heat: bool, below: frozenset[str]):
    """Single photon response, respecting the LEFT and RIGHT limits at cutoffs."""
    rates=[]
    for name,n in zip(ION_NAMES,neutrals):
        rates.append(_iv(dt)*_iv(C_CM_S)*_iv(n)*_verner_iv(name,energy,name not in below))
    tau=sum(rates,mp.iv.mpf(0))
    # Avoid ill-conditioned 0/0. For exactly inactive spectrum all outputs 0.
    if all(n==0 or name in below or energy < ATOMIC[name][0] for name,n in zip(ION_NAMES,neutrals)):
        return mp.iv.mpf(0)
    frac=rates[kind]*(-mp.iv.expm1(-tau))/tau
    return frac*(_iv(energy)-_iv(BINDING[kind])) if heat else frac


def _curvature_upper(lo: float, hi: float, neutrals: tuple[float,...],dt:float,
                     kind:int, heat:bool):
    """Sufficient upper for |d²(g)/dE²| on ONE open fit-threshold branch."""
    B0=[];B1=[];B2=[]
    for name,n in zip(ION_NAMES,neutrals):
        if hi<=ATOMIC[name][0] and lo<ATOMIC[name][0]:
            B0.append(ZERO);B1.append(ZERO);B2.append(ZERO);continue
        if hi<ATOMIC[name][0] or n==0:
            B0.append(ZERO);B1.append(ZERO);B2.append(ZERO);continue
        if lo<ATOMIC[name][0]<hi:
            raise ValueError('threshold crossing in a smooth segment')
        p0,p1,p2=second_sigma_up(name,D(lo),D(hi))
        alpha=times(times(D(dt),D(C_CM_S)),D(n))
        B0.append(times(alpha,p0));B1.append(times(alpha,p1));B2.append(times(alpha,p2))
    L1=ZERO;L2=ZERO
    for a,b in zip(B1,B2):L1=plus(L1,a);L2=plus(L2,b)
    p1=plus(B1[kind],divup(times(B0[kind],L1),TWO))
    p2=plus(plus(B2[kind],times(B1[kind],L1)),
            times(B0[kind],plus(divup(times(L1,L1),Decimal(3)),divup(L2,TWO))))
    if not heat:
        return p2
    # On active branch E>=fit>=binding, so the offset is nonnegative.
    delta=max(ZERO,subup(D(hi),D(BINDING[kind])))
    return plus(times(TWO,p1),times(delta,p2))


def _outer_piece_epsilon(lo:float,hi:float,neutrals:tuple[float,...],dt:float,kind:int,heat:bool):
    if hi==lo:return 0.
    M=_curvature_upper(lo,hi,neutrals,dt,kind,heat)
    h=subup(D(hi),D(lo))
    if h<=0:raise ValueError('positive segment required')
    # All positive factors and directed upward arithmetic.
    delta=divup(times(M,times(h,h)),Decimal(8))
    return 0. if delta==0 else _radius(float(delta),True)


def _hull(x: list[float],y: list[float],upper:bool):
    """Exact dyadic lower-convex/upper-concave hull, including jump duplicates."""
    if len(x)!=len(y) or len(x)<2:raise ValueError('bad node list')
    XY=[]
    for xx,yy in zip(x,y):
        p=(Fraction.from_float(xx),Fraction.from_float(yy))
        if XY and p[0]<XY[-1][0]:raise ValueError('unsorted support')
        if XY and p[0]==XY[-1][0]:
            best=max(XY[-1][1],p[1]) if upper else min(XY[-1][1],p[1])
            XY[-1]=(p[0],best)
        else:XY.append(p)
    out=[]
    for point in XY:
        while len(out)>=2:
            a,b=out[-2],out[-1];c=point
            orientation=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
            if orientation>=0 if upper else orientation<=0:out.pop()
            else:break
        out.append(point)
    return tuple(out)


def _hull_at(hull,mean:float,upper:bool):
    m=mean if isinstance(mean,Fraction) else Fraction.from_float(float(mean))
    if m<hull[0][0] or m>hull[-1][0]:raise ValueError('mean outside support')
    idx=bisect_right([p[0] for p in hull],m)-1
    if idx>=len(hull)-1:exact=hull[-1][1]
    else:
        x0,y0=hull[idx];x1,y1=hull[idx+1]
        exact=y0+(y1-y0)*(m-x0)/(x1-x0)
    if exact==0:return 0.
    v=_radius(float(exact),upper)
    return max(0.,v) if not upper else max(0.,v)


@dataclass(frozen=True)
class ShapeFreeTemplate:
    support: tuple[float,float]
    neutrals_cm3: tuple[float,float,float]
    dt_s:float
    knots: int
    hulls: tuple # for 3 species times (event,heat) times (lower,upper)
    max_remainder:tuple
    # Only per-model one-step rate uncertainty is covered, not full REI history.

    def evaluate(self, mass:float, mean_energy_eV:float):
        if not(isfinite(mass) and isfinite(mean_energy_eV) and mass>=0):
            raise ValueError('nonnegative mass, finite mean required')
        lo,hi=self.support
        if mean_energy_eV<lo or mean_energy_eV>hi:
            raise ValueError('mean outside certified support')
        if mass==0:
            return {'event':tuple((0.,0.) for _ in range(3)),
                    'heat':tuple((0.,0.) for _ in range(3))}
        output=[]
        for i in range(6):
            low,up=self.hulls[i]
            vl=_hull_at(low,mean_energy_eV,False)
            vu=_hull_at(up,mean_energy_eV,True)
            # Multiplication outward, no sign of negative physical response.
            exact_mass=mass if isinstance(mass,Fraction) else Fraction.from_float(float(mass))
            a=0. if vl<=0 else _radius(float(exact_mass*Fraction.from_float(vl)),False)
            b=0. if vu==0. else _radius(float(exact_mass*Fraction.from_float(vu)),True)
            if i<3:b=min(_radius(float(exact_mass),True),b)
            output.append((max(0.,a),max(0.,b)))
        return {'event':tuple(output[:3]),'heat':tuple(output[3:])}

    def vector_preview(self,masses,means):
        """Fast O(6*knots + cases) floating readout, NOT the directed certificate."""
        masses=np.asarray(masses,float);means=np.asarray(means,float)
        if masses.shape!=means.shape or not np.all(np.isfinite(masses)) or not np.all(np.isfinite(means)) or np.any(masses<0) or np.any(means<self.support[0]) or np.any(means>self.support[1]):
            raise ValueError('bad vector moments')
        low=[];high=[]
        for hlo,hhi in self.hulls:
            def interp(h):
                x=np.asarray([float(t[0]) for t in h]);y=np.asarray([float(t[1]) for t in h])
                return np.maximum(0.,np.interp(means,x,y))*masses
            low.append(interp(hlo));high.append(interp(hhi))
        return {'event_lower':np.stack(low[:3]),'event_upper':np.stack(high[:3]),
                'heat_lower':np.stack(low[3:]),'heat_upper':np.stack(high[3:])}


def make_template(support:Sequence[float],neutrals_cm3:Sequence[float],dt_s:float,
                  nodes_per_branch:int=6)->ShapeFreeTemplate:
    if len(support)!=2 or not all(isfinite(v) for v in support) or not (0<support[0]<support[1]<=50000):
        raise ValueError('positive bounded physical support required')
    if not(isfinite(dt_s) and dt_s>=0):raise ValueError('nonnegative proper time required')
    rho=_positive_finite(neutrals_cm3,3)
    if not 2<=nodes_per_branch<=48:raise ValueError('bounded spectral resolution')
    a,b=map(float,support)
    cut=[t for t in (13.6,24.59,54.42) if a<t<b]
    split=[a]+cut+[b]
    # Build smooth segments and preserve the distinct sides of each fit jump.
    nodes=[];segs=[];branch_idx=[]
    for k,(lo,hi) in enumerate(zip(split[:-1],split[1:])):
        branch=[]
        for j in range(nodes_per_branch+1):
            x=lo+(hi-lo)*j/nodes_per_branch
            if j==0:x=lo
            if j==nodes_per_branch:x=hi
            branch.append(x)
            nodes.append(x)
            # strictly below the cutoff on the left replica, even at x=chi.
            branch_idx.append(k)
        segs.extend([(branch[j],branch[j+1]) for j in range(nodes_per_branch)])
    hulls=[];max_err=[]
    for heat in (False,True):
        for ion_id in range(3):
            actual_lo=[];actual_hi=[]
            for j,x in enumerate(nodes):
                # Right threshold node carries the active value; left node carries zero.
                below=frozenset(name for name in ION_NAMES if (x < ATOMIC[name][0] or
                    (j>0 and j<len(nodes)-1 and x==ATOMIC[name][0]
                     and branch_idx[j]==branch_idx[j-1])))
                iv=_response_interval(x,rho,dt_s,ion_id,heat,below)
                if float(iv.a)==0. and float(iv.b)==0.:
                    actual_lo.append(0.);actual_hi.append(0.)
                else:
                    actual_lo.append(_radius(float(iv.a),False))
                    actual_hi.append(_radius(float(iv.b),True))
            eps=[]
            for k,(lo,hi) in enumerate(zip(split[:-1],split[1:])):
                for j in range(nodes_per_branch):
                    qlo=nodes[k*(nodes_per_branch+1)+j]
                    qhi=nodes[k*(nodes_per_branch+1)+j+1]
                    eps.append(_outer_piece_epsilon(qlo,qhi,rho,dt_s,ion_id,heat))
            low=[];upper=[]
            for j in range(len(nodes)):
                segment=j//(nodes_per_branch+1)
                sub=j%(nodes_per_branch+1)
                err=0.
                if sub>0:err=max(err,eps[segment*nodes_per_branch+sub-1])
                if sub<nodes_per_branch:err=max(err,eps[segment*nodes_per_branch+sub])
                if err==0 and actual_lo[j]==0 and actual_hi[j]==0:
                    low.append(0.);upper.append(0.)
                else:
                    low.append(nextafter(actual_lo[j]-err,-inf))
                    upper.append(nextafter(actual_hi[j]+err,inf))
            hulls.append((_hull(nodes,low,False),_hull(nodes,upper,True)))
            max_err.append(max(eps))
    return ShapeFreeTemplate((a,b),rho,dt_s,nodes_per_branch,tuple(hulls),tuple(max_err))


def threshold_occupation_bounds(lo:float,hi:float,mean:float,threshold:float):
    """Sharp mass-fraction bounds for E>=threshold given mean and support.

    Endpoints at a discontinuity are understood as infimum/supremum: strict
    below-threshold support can tend to threshold without crossing it.
    """
    if not(0<lo<=mean<=hi<=50000 and isfinite(threshold)):
        raise ValueError('invalid support/mean')
    if hi<threshold:return (0.,0.)
    if lo>=threshold:return (1.,1.)
    if hi==threshold:
        if mean==threshold:return (1.,1.)
        return (0.,min(1.,(mean-lo)/(threshold-lo)))
    return (max(0.,(mean-threshold)/(hi-threshold)),
            min(1.,(mean-lo)/(threshold-lo)))

@lru_cache(maxsize=512)
def cached_template(a:float,b:float,neutrals_cm3:tuple[float,float,float],dt_s:float,
                    nodes_per_branch:int=6):
    """Bounded cache: template depends on support+actual gas+proper dt, not source age.

    An age change that changes physical R/support or gas values creates a NEW key;
    a caller cannot reuse a template with different source owner/clock.
    """
    return make_template((a,b),neutrals_cm3,dt_s,nodes_per_branch)


def enclose_q_bins(ref_edges,number,moment_ref_ev,ratio_R:float,
                   neutrals_cm3,dt_s,nodes_per_branch:int=4):
    """One ray/one current proper clock: q-grid shape-free one-step envelopes.

    Input N and U_ref are physical nonnegative moments of the ACTUAL current stock,
    never an inferred BB50K shape. Each q-bin support is fixed by E_ref edges and
    physical energy R*E_ref. The source R*J Jacobian belongs to the caller.
    """
    ed=np.asarray(ref_edges,float);ns=np.asarray(number,float);us=np.asarray(moment_ref_ev,float)
    if ed.ndim!=1 or len(ed)!=len(ns)+1 or ns.shape!=us.shape or not np.all(np.isfinite(ed)) or not np.all(np.diff(ed)>0):
        raise ValueError('inconsistent fixed-q grid')
    if not(isfinite(ratio_R) and ratio_R>0) or np.any(~np.isfinite(ns)) or np.any(~np.isfinite(us)) or np.any(ns<0):
        raise ValueError('nonphysical current mass/moment')
    if np.any((ns==0)&(us!=0)) or np.any((ns>0)&((us/ns.clip(min=np.finfo(float).tiny)<ed[:-1])|(us/ns.clip(min=np.finfo(float).tiny)>ed[1:]))):
        raise ValueError('current moments do not lie in the supplied q support')
    gas=_positive_finite(neutrals_cm3,3)
    # Every element of N,U,R,energy edges is treated as its STORED dyadic input.
    # Moment mean and summed upper/lower observables are exact Fraction arithmetic;
    # the final binary64 bounds alone are rounded outwards.
    total_low=[Fraction(0)]*6
    total_high=[Fraction(0)]*6
    for i in np.flatnonzero(ns>0):
        r=Fraction.from_float(float(ratio_R))
        a=Fraction.from_float(float(ed[i]))*r
        b=Fraction.from_float(float(ed[i+1]))*r
        lo=nextafter(float(a),-inf)
        hi=nextafter(float(b),inf)
        template=cached_template(lo,hi,gas,float(dt_s),nodes_per_branch)
        n=Fraction.from_float(float(ns[i]))
        u=Fraction.from_float(float(us[i]))
        obs=template.evaluate(n,u*r/n)
        for j in range(3):
            for k,v in enumerate((obs['event'][j],obs['heat'][j])):
                index=j+3*k
                total_low[index]+=Fraction.from_float(v[0])
                total_high[index]+=Fraction.from_float(v[1])
    totals=np.zeros((6,2),float)
    for j in range(6):
        totals[j,0]=0. if total_low[j]<=0 else _radius(float(total_low[j]),False)
        totals[j,1]=0. if total_high[j]==0 else _radius(float(total_high[j]),True)
    n_used=int(np.count_nonzero(ns))
    return {'event':totals[:3],'heat':totals[3:],
            'number':float(ns.sum()),'physical_energy_ev':float((us*ratio_R).sum()),
            'support_bins':n_used,'numerics':'dyadic_Fraction_exact_mean_and_global_sum; outward_binary64_endpoints'}
