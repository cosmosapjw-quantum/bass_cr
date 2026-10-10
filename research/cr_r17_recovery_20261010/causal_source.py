"""Exact causal CDF-to-optical bound, conditional on supplied kernel/tube premises.

Coordinates: u=t/T in [0,1], cumulative counts per H. No gas or photon IVP is
solved. A positive lower endpoint of an envelope integral is NOT a lower bound
on the magnitude of a physical error. Actual source error is signed-unknown.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import factorial
from typing import Sequence

Poly = list[F]

class ContractError(ValueError):
    pass

def exact(x: F) -> F:
    if not isinstance(x, F):
        raise ContractError('EXACT_FRACTION_REQUIRED')
    return x

def add(a: Sequence[F], b: Sequence[F]) -> Poly:
    c = [F(0)]*max(len(a),len(b))
    for i,v in enumerate(a): c[i] += v
    for i,v in enumerate(b): c[i] += v
    return c

def scale(a: Sequence[F], b: F) -> Poly:
    return [x*b for x in a]

def mul(a: Sequence[F], b: Sequence[F]) -> Poly:
    c = [F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j] += x*y
    return c

def value(p: Sequence[F], x: F) -> F:
    y = F(0)
    for v in reversed(p): y = y*x+v
    return y

def primitive(p: Sequence[F]) -> Poly:
    return [F(0)] + [x/F(i+1) for i,x in enumerate(p)]

def integral(p: Sequence[F], a: F, b: F) -> F:
    q = primitive(p)
    return value(q,b)-value(q,a)

@dataclass(frozen=True)
class Segment:
    left: F
    right: F
    cdf: tuple[F,F]  # d(u)=cdf[0]+cdf[1]*u, nonnegative on this segment


def cdf_envelope(births: Sequence[F], weights: Sequence[tuple[F,F]],
                 rate: F, total_time: F) -> tuple[list[Segment],F,F]:
    exact(rate); exact(total_time)
    if rate < 0 or total_time <= 0: raise ContractError('SOURCE_DOMAIN')
    if len(births) != len(weights): raise ContractError('BIRTH_WEIGHT_LENGTH')
    if any(not isinstance(t,F) for t in births): raise ContractError('EXACT_CLOCK_REQUIRED')
    if any(t<0 or t>total_time for t in births): raise ContractError('BIRTH_OUTSIDE_WINDOW')
    if any(a>=b for a,b in zip(births,births[1:])): raise ContractError('STRICT_BIRTH_ORDER_REQUIRED')
    for w in weights:
        if len(w)!=2 or any(not isinstance(x,F) for x in w) or not 0<=w[0]<=w[1]:
            raise ContractError('NONNEGATIVE_ORDERED_WEIGHT_BOX_REQUIRED')
    mass=rate*total_time
    lo=hi=F(0); cursor=F(0); result=[]; peak=F(0)
    for i,end in enumerate([t/total_time for t in births]+[F(1)]):
        if end>cursor:
            cuts=[cursor,end]
            if mass:
                switch=(lo+hi)/(2*mass)
                if cursor<switch<end: cuts.insert(1,switch)
            for a,b in zip(cuts,cuts[1:]):
                mid=(a+b)/2
                p=(hi,-mass) if hi-mass*mid >= mass*mid-lo else (-lo,mass)
                assert value(p,a)>=0 and value(p,b)>=0
                result.append(Segment(a,b,p))
                peak=max(peak,value(p,a),value(p,b))
        cursor=end
        if i<len(weights): lo+=weights[i][0]; hi+=weights[i][1]
        peak=max(peak,abs(lo-mass*end),abs(hi-mass*end))
    mismatch=max(abs(lo-mass),abs(hi-mass))
    if not result or result[0].left != 0 or result[-1].right != 1:
        raise ContractError('INCOMPLETE_CDF_COVERAGE')
    return result,peak,mismatch


def causal_moments(births,weights,rate,total_time):
    segments,peak,mismatch=cdf_envelope(births,weights,rate,total_time)
    moments=[]
    weight=[F(1)]
    for j in range(3):
        moments.append(sum((integral(mul(s.cdf,weight),s.left,s.right) for s in segments),F(0)))
        weight=mul(weight,[F(1),F(-1)])
    return {'segments':segments,'cdf_sup':peak,'mass_mismatch':mismatch,
            'area':moments[0],'weighted_area':moments[1], 'weighted_area2':moments[2]}


def response_polynomials(segments: Sequence[Segment], k: F, kb: F):
    """A(u)=k int_0^u d(v)dv+kb int_0^u (u-v)d(v)dv."""
    exact(k);exact(kb)
    if k<0 or kb<0: raise ContractError('NEGATIVE_KERNEL_BOUND')
    int0=int1=F(0); start=F(0); answer=[]
    for s in segments:
        if s.left != start: raise ContractError('DISCONTIGUOUS_SEGMENTS')
        i0=primitive(s.cdf); i0[0]=int0-value(i0,s.left)
        i1=primitive(i0); i1[0]=int1-value(i1,s.left)
        a=add(scale(i0,k),scale(i1,kb))
        answer.append((s.left,s.right,a))
        int0=value(i0,s.right); int1=value(i1,s.right); start=s.right
    if start!=1: raise ContractError('INCOMPLETE_RESPONSE_COVERAGE')
    return answer


def optical_envelope(moments: dict, k: F, kb: F, gamma: F, alpha: F,
                     *, exp_order: int=8, geometric_order: int=8) -> dict:
    """Enclose I=int exp(-alpha*u) A(u)/(1-gamma*u)du.

    All-prefix gas contraction <=gamma*u and heat-row dominance are EXTERNAL
    physical premises, checked for the actual donor by run_research.py.
    Polynomial integrations are exact. The bound on |source delta_tau| is an
    external positive normalization times I.upper, not I.lower.
    """
    exact(gamma);exact(alpha)
    if not 0<=gamma<1: raise ContractError('PREFIX_CONTRACTION_REQUIRED')
    if not 0<=alpha<=1: raise ContractError('EXP_ALTERNATING_DOMAIN')
    if exp_order<2 or exp_order%2 or geometric_order<0:
        raise ContractError('INVALID_SERIES_ORDER')
    polys=response_polynomials(moments['segments'],k,kb)
    exp_upper=[(-alpha)**i/F(factorial(i)) for i in range(exp_order+1)]
    exp_lower=exp_upper+[(-alpha)**(exp_order+1)/F(factorial(exp_order+1))]
    geo_lower=[gamma**i for i in range(geometric_order+1)]
    geo_upper=geo_lower+[gamma**(geometric_order+1)/(1-gamma)]
    p_lo=mul(exp_lower,geo_lower); p_hi=mul(exp_upper,geo_upper)
    lo=hi=F(0); panel=[]
    for a,b,p in polys:
        l=integral(mul(p,p_lo),a,b); h=integral(mul(p,p_hi),a,b)
        assert 0<=l<=h
        lo+=l;hi+=h;panel.append({'u':[a,b],'response_polynomial':p,'envelope_integral':[l,h]})
    A1=k*moments['area']+kb*moments['weighted_area']
    flat=(k*moments['weighted_area']+kb*moments['weighted_area2']/2)/(1-gamma)
    global_area=A1/(1-gamma)
    global_peak=moments['cdf_sup']*(k+kb)/(1-gamma)
    assert hi<=flat<=global_area<=global_peak
    return {'integral':[lo,hi], 'prefix_state_sup_at_T':A1/(1-gamma),
            'global_peak_integral_bound':global_peak,'global_area_integral_bound':global_area,
            'causal_flat_integral_bound':flat,'panels':panel,
            'source_error_has_signed_lower_bound':False,
            'exp_degree':exp_order,'geometric_degree':geometric_order}
