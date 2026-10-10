"""Exact causal-CDF transfer of an inherited FT03 source-error proof.

Only the measure algebra and goal transfer are new. No native/atomic/ODE calls.
All physical constants and bounds entering the public mathematical API are
Fractions; producer binary64 values are explicitly realified by the caller.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import factorial
from typing import Sequence


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Piece:
    left: F
    right: F
    intercept: F
    slope: F

    def value(self, t: F) -> F:
        return self.intercept + self.slope*t


def _exact(*values: F) -> None:
    if any(not isinstance(x,F) for x in values):
        raise ContractError('EXACT_FRACTION_INPUT_REQUIRED')


def cdf_pieces(duration: F, source: F,
               births: Sequence[tuple[F,F,F]]) -> list[Piece]:
    """Envelope max(|sum(lo)-S*t|,|sum(hi)-S*t|), including mass defect.

    Atom values at isolated times do not change Lebesgue integrals. Birth
    times must be strictly ordered in [0,T]; no mass renormalization occurs.
    """
    _exact(duration,source)
    if duration<=0 or source<0: raise ContractError('TIME_OR_SOURCE_DOMAIN')
    prev=None
    for row in births:
        if len(row)!=3: raise ContractError('BIRTH_ROW')
        b,lo,hi=row;_exact(b,lo,hi)
        if not 0<=b<=duration or not 0<=lo<=hi:
            raise ContractError('BIRTH_DOMAIN')
        if prev is not None and b<=prev: raise ContractError('BIRTH_CLOCK_ORDER')
        prev=b
    pieces=[];left=F(0);lo_total=F(0);hi_total=F(0)
    for right,lo,hi in list(births)+[(duration,F(0),F(0))]:
        knots=[left,right]
        if source:
            cross=(lo_total+hi_total)/(2*source)
            if left<cross<right: knots.insert(1,cross)
        for a,b in zip(knots,knots[1:]):
            if b==a: continue
            mid=(a+b)/2
            if hi_total-source*mid >= source*mid-lo_total:
                p=Piece(a,b,hi_total,-source)
            else:
                p=Piece(a,b,-lo_total,source)
            if min(p.value(a),p.value(b))<0: raise ArithmeticError('NEGATIVE_ENVELOPE')
            pieces.append(p)
        lo_total+=lo;hi_total+=hi;left=right
    if not pieces or pieces[0].left!=0 or pieces[-1].right!=duration:
        raise ArithmeticError('INCOMPLETE_TIME_COVERAGE')
    return pieces


def piece_moment(p: Piece, order: int) -> F:
    if order<0: raise ContractError('MOMENT_ORDER')
    a,b=p.left,p.right
    return (p.intercept*(b**(order+1)-a**(order+1))/(order+1)
            +p.slope*(b**(order+2)-a**(order+2))/(order+2))


def cdf_moments(duration: F, source: F, births: Sequence[tuple[F,F,F]],
                max_order: int=8) -> list[F]:
    if not isinstance(max_order,int) or not 0<=max_order<=20:
        raise ContractError('MOMENT_ORDER')
    pieces=cdf_pieces(duration,source,births)
    return [sum((piece_moment(p,n) for p in pieces),F(0))
            for n in range(max_order+1)]


def response_moment(duration: F, k: F, kb: F, moments: Sequence[F], n: int) -> F:
    """Integral t^n B(t) dt, B(t)=int_0^t D(b)[k+(t-b)kb] db."""
    T=duration
    if len(moments)<n+3: raise ContractError('INSUFFICIENT_MOMENTS')
    return (k*(T**(n+1)*moments[0]-moments[n+1])/(n+1)
            +kb*((T**(n+2)*moments[0]-moments[n+2])/(n+2)
                 -(T**(n+1)*moments[1]-moments[n+2])/(n+1)))


def certify_source_goal(duration: F, source: F, births: Sequence[tuple[F,F,F]],
                        *, k: F,kb: F,qmax: F,qb: F,w0: F,gain: F,
                        hubble: F,n_h0: F,f_he: F,c_thomson: F) -> dict:
    """Conditional coupled source-only optical bound, not a signed estimate.

    Requires inherited all-path k,kb,physical tube, and full-horizon
    contraction gain with prefix scaling gain(t)<=gain*t/T. The caller must
    bind those scientific premises; this algebraic function cannot prove them.
    """
    _exact(duration,source,k,kb,qmax,qb,w0,gain,hubble,n_h0,f_he,c_thomson)
    if min(k,kb,qmax,qb,gain,hubble,f_he)<0 or min(w0,n_h0,c_thomson)<=0:
        raise ContractError('NONPOSITIVE_PHYSICAL_PREMISE')
    if not 0<=gain<1: raise ContractError('CONTRACTION_REQUIRED')
    if duration<=0 or 3*hubble*duration>1:
        raise ContractError('EXPONENTIAL_BRACKET_DOMAIN')
    T=duration
    # d_b integrated primary heat <= H0+v H1+v^2 H2, v=t-b.
    heat_variation=(qmax*k + T*(qb*k+qmax*kb+qmax*k*k)
                    +T*T*qmax*k*kb/2)/w0
    if heat_variation>k:
        raise ContractError('HEAT_DOMINATION_NOT_ESTABLISHED')
    pieces=cdf_pieces(T,source,births)
    mm=[sum((piece_moment(p,n) for p in pieces),F(0)) for n in range(9)]
    B_T=k*mm[0]+kb*(T*mm[0]-mm[1])
    E_inf=B_T/(1-gain)
    def integral(n):
        return (response_moment(T,k,kb,mm,n)
                +gain*E_inf*T**(n+1)/(n+2))
    alpha=3*hubble
    polys=[sum(((-alpha)**n/F(factorial(n))*integral(n)
                for n in range(degree+1)),F(0)) for degree in (5,6)]
    if not 0<=polys[0]<=polys[1]: raise ArithmeticError('EXP_BRACKET_ORDER')
    factor=c_thomson*n_h0*(1+3*f_he)
    upper=factor*polys[1]
    feedback=factor*sum(((-alpha)**n/F(factorial(n))*
                        (gain*E_inf*T**(n+1)/(n+2))
                        for n in range(7)),F(0))
    return dict(cdf_pieces=[vars(p) for p in pieces],cdf_raw_moments=mm,
                cdf_sup=max(max(p.value(p.left),p.value(p.right)) for p in pieces),
                source_mass_defect=(sum((r[1] for r in births),F(0))-source*T,
                                    sum((r[2] for r in births),F(0))-source*T),
                heat_normalized_derivative_upper=heat_variation,
                heat_to_absorption_derivative_ratio=heat_variation/k if k else F(0),
                prefix_direct_at_T=B_T,gas_sup_new=E_inf,
                positive_budget_integral=(factor*polys[0],factor*polys[1]),
                source_tau_abs_upper=upper,
                direct_optical_budget_upper=upper-feedback,
                feedback_optical_budget_upper=feedback,
                density_flat_budget=factor*integral(0),
                density_bracket_width=factor*(polys[1]-polys[0]),
                source_signed_interval=(-upper,upper),
                actual_source_sign=None,full_IVP_run=False,
                requires_inherited_prefix_contraction=True)


def combine_time_source(time_interval: tuple[F,F], source_upper: F)->tuple[F,F]:
    a,b=time_interval;_exact(a,b,source_upper)
    if a>b or source_upper<0: raise ContractError('INTERVAL_OR_RADIUS_DOMAIN')
    return a-source_upper,b+source_upper


def polynomial_source_action(duration:F,source:F,births:Sequence[tuple[F,F,F]],
                             coefficients:Sequence[F])->tuple[F,F]:
    """Exact interval action int P(b) d(mu_Q-mu_S), with shared atom weights.

    Useful for independently checking mass defects and polynomial controls.
    It neither assumes Gauss polynomial exactness nor certifies an unknown K.
    """
    cdf_pieces(duration,source,births)
    _exact(*coefficients)
    continuous=source*sum((v*duration**(n+1)/(n+1)
                           for n,v in enumerate(coefficients)),F(0))
    lower=upper=-continuous
    for b,lo,hi in births:
        value=sum((v*b**n for n,v in enumerate(coefficients)),F(0))
        ends=[lo*value,hi*value];lower+=min(ends);upper+=max(ends)
    return lower,upper
