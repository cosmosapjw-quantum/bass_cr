"""Exact positive functionals and conditional a posteriori bounds.

Rational endpoints control *arithmetic*, not the truth of caller-supplied
source/continuum bounds. No function in this module grants physical admission.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isfinite, isqrt
from typing import Iterable, Sequence

class ContractError(ValueError):
    """Input is outside this explicitly scoped reference contract."""

def rational(value) -> F:
    if isinstance(value, bool):
        raise ContractError('boolean is not a scalar')
    if isinstance(value, float) and not isfinite(value):
        raise ContractError('non-finite scalar')
    try:
        return F(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as e:
        raise ContractError('invalid finite rational scalar') from e

def nonnegative(value) -> F:
    v = rational(value)
    if v < 0:
        raise ContractError('negative scalar')
    return v

def interval(pair) -> tuple[F,F]:
    if not isinstance(pair,(list,tuple)) or len(pair) != 2:
        raise ContractError('interval requires two endpoints')
    lo, hi = map(nonnegative, pair)
    if lo > hi:
        raise ContractError('reversed interval')
    return lo, hi

def sqrt_interval(value, bits: int=128) -> tuple[F,F]:
    """Integer-isqrt enclosure; exact zero and rational perfect squares allowed."""
    x = nonnegative(value)
    if not isinstance(bits,int) or isinstance(bits,bool) or not 16 <= bits <= 4096:
        raise ContractError('bits outside [16,4096]')
    scale = 1 << bits
    n = isqrt((x.numerator * scale * scale)//x.denominator)
    lo = F(n,scale)
    return lo, lo if lo*lo == x else F(n+1,scale)

def weighted_intervals(weights: Sequence, intervals: Sequence) -> tuple[F,F]:
    if len(weights) != len(intervals) or not weights:
        raise ContractError('empty or incompatible positive functional')
    lo=hi=F(0)
    for w,pair in zip(weights,intervals):
        w=nonnegative(w); a,b=interval(pair)
        lo+=w*a; hi+=w*b
    return lo,hi

def cx_delta(extent) -> tuple[F,...]:
    """Species order: p_CR, H_g(1s), H_CR(1s), p_g, e_free."""
    x=nonnegative(extent)
    return -x,-x,x,x,F(0)

def cx_update(densities: Sequence, extent) -> tuple[F,...]:
    if len(densities)!=5:
        raise ContractError('five reservoir densities required')
    n=tuple(map(nonnegative,densities)); x=nonnegative(extent)
    if x>min(n[0],n[1]):
        raise ContractError('extent exceeds either reactant reservoir')
    return tuple(a+b for a,b in zip(n,cx_delta(x)))

def conserved_ledger(densities: Sequence) -> dict[str,F]:
    if len(densities)!=5:
        raise ContractError('five reservoir densities required')
    a,b,c,d,e=map(nonnegative,densities)
    return {'nuclei':a+b+c+d,'charge_in_e':a+d-e,
            'total_HII':a+d,'total_HI':b+c,'free_electrons':e}

def exp_positive_interval(value, tolerance=F(1,10**45), max_terms=10000) -> tuple[F,F]:
    """Positive Taylor series and geometric tail; mathematical enclosure for x>=0."""
    x=nonnegative(value); tol=nonnegative(tolerance)
    if tol==0 or max_terms<1:
        raise ContractError('positive tolerance and term budget required')
    s=t=F(1)
    for n in range(max_terms):
        nxt=t*x/(n+1)
        ratio=x/(n+2)
        if ratio<1:
            tail=nxt/(1-ratio)
            if tail<=tol:
                return s,s+tail
        s+=nxt; t=nxt
    raise ContractError('exponential enclosure term budget exhausted')

def state_error_bound(initial, segments: Iterable[Sequence]) -> F:
    """Conditional upper bound, segments=(dt, kappa_upper>=0, rho_upper>=0).

    y' <= kappa*y/2 + rho in the S-norm. Caller must separately justify
    continuous-time kappa/rho bounds, state identity, units and interval cover.
    Pointwise residual samples alone do not satisfy these premises.
    """
    y=nonnegative(initial)
    for seg in segments:
        if len(seg)!=3:
            raise ContractError('segment=(dt,kappa,rho) required')
        dt,k,r=map(nonnegative,seg); x=k*dt/2
        if x==0:
            y+=r*dt
        else:
            _,ex=exp_positive_interval(x)
            y=ex*y+r*dt*(ex-1)/x
    return y

def population_error_bound(state_error, approximate_norm) -> F:
    """For a fixed orthogonal physical projector: |P-Ptilde|<=eps(2N+eps)."""
    e=nonnegative(state_error); n=nonnegative(approximate_norm)
    return e*(2*n+e)

def continuous_rate_budget(core: Sequence, low_tail=None, high_tail=None,
                           quadrature_error=None) -> dict:
    """Known core plus positive tails. Missing is never interpreted as zero.

    All inputs refer to the *same K in m^3/s*. This helper checks arithmetic;
    provenance and justification of supplied bounds belong to the caller.
    """
    lo,hi=interval(core)
    named={'low_tail':low_tail,'high_tail':high_tail,'quadrature_error':quadrature_error}
    missing=[k for k,v in named.items() if v is None]
    checked={k:(None if v is None else nonnegative(v)) for k,v in named.items()}
    if missing:
        return {'status':'MISSING_BOUNDS','lower':None,'upper':None,
                'missing':missing,'physical_admission':False}
    q=checked['quadrature_error']
    return {'status':'CONDITIONAL_ON_INPUT_BOUNDS','lower':max(F(0),lo-q),
            'upper':hi+checked['low_tail']+checked['high_tail']+q,
            'missing':[],'physical_admission':False}

def coefficient_residual_upper(s_min, eps_s, eps_h, eps_d,
                               c_norm, dc_norm, approximate_residual_norm,
                               hbar):
    """Conditional dual-S residual bound in one fixed coefficient basis.

    Assumes continuous operator-2-norm error bounds for S,H,D, S>=s_min I,
    Euclidean vector norm bounds, and common units/frame/time. A pointwise
    diagnostic does not meet these premises. Result is an exact rational upper.
    """
    sm=nonnegative(s_min);h=nonnegative(hbar)
    if sm==0 or h==0: raise ContractError('positive metric lower bound and hbar required')
    es,eh,ed,n,dn,r=map(nonnegative,(eps_s,eps_h,eps_d,c_norm,dc_norm,approximate_residual_norm))
    # lower sqrt endpoint gives an upper reciprocal; refine if subnormal-scale
    # input is smaller than the default dyadic resolution.
    bits=max(128,(sm.denominator.bit_length()-sm.numerator.bit_length())//2+16)
    if bits>4096: raise ContractError('metric bound below supported rational sqrt resolution')
    sl,_=sqrt_interval(sm,bits)
    if sl==0: raise ContractError('positive sqrt lower endpoint unavailable')
    return (es*dn+(eh/h+ed)*n+r)/sl
