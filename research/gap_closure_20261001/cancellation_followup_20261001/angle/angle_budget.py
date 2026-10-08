"""Exact rational audit of state-aware rate budgets; no physical evaluator.

Inputs are certified rational endpoints supplied by the caller. Returning a
certificate here does not certify those inputs. No floats are admitted.
"""
from fractions import Fraction as F
from math import isqrt

def rational(x):
    if not isinstance(x, (int, F)) or isinstance(x, bool):
        raise TypeError('exact int/Fraction input required')
    return F(x)

def sqrt_upper(x, bits=80):
    x=rational(x)
    if x<0 or not isinstance(bits,int) or isinstance(bits,bool) or bits<1:
        raise ValueError('nonnegative x and positive integer bits required')
    d=2**bits
    n=isqrt((x.numerator*d*d)//x.denominator)
    if F(n*n,d*d)<x: n+=1
    return F(n,d)

def _inputs(lo,hi,a):
    lo,hi,a=map(rational,(lo,hi,a))
    if not 0<=lo<=hi<=1 or a<0:
        raise ValueError('0<=lo<=hi<=1, a>=0 required')
    return lo,hi,a

def initial_coherence_upper(lo,hi,bits=80):
    lo,hi,_=_inputs(lo,hi,F(0))
    p=min(hi,max(lo,F(1,2)))
    return sqrt_upper(p*(1-p),bits)

def rate_budget(lo,hi,a,bits=80):
    """Bound |p1-p0| with p0 in [lo,hi] and certified integral rho <= a.

    Uses min(1,a,2*r*a+a*a). The sharper trigonometric theorem is recorded
    separately; this is an outward rational sufficient bound.
    """
    lo,hi,a=_inputs(lo,hi,a)
    r=initial_coherence_upper(lo,hi,bits)
    return min(F(1),a,2*r*a+a*a)

def population_interval(lo,hi,a,bits=80):
    lo,hi,a=_inputs(lo,hi,a)
    b=rate_budget(lo,hi,a,bits)
    return max(F(0),lo-b),min(F(1),hi+b)

def admitted_angle(lo,hi,epsilon,bits=80):
    """Largest dyadic a obeying a*a+2*r_upper*a <= epsilon.

    This is maximal only for this sufficient polynomial with the chosen
    outward r, not for the exact trigonometric envelope or actual dynamics.
    """
    lo,hi,e=_inputs(lo,hi,epsilon)
    r=initial_coherence_upper(lo,hi,bits)
    d=2**bits
    left,right=0,int(sqrt_upper(e,bits)*d)+1
    while right-left>1:
        mid=(left+right)//2
        a=F(mid,d)
        if a*a+2*r*a<=e: left=mid
        else: right=mid
    return F(left,d),r
