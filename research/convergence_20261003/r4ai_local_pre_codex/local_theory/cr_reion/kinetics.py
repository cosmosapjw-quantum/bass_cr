"""Floating-point diagnostic reduction for an isotropic Maxwellian target.

The reference functions return numerical values, NOT certified intervals.
Caller must cover source support and tails before computing physical rates.
"""
from __future__ import annotations
import math
from .core import ContractError

def relative_speed_pdf_scaled(y:float,a:float) -> float:
    """PDF of y=g/s for drift magnitude a=V/s; s is per-component thermal sigma."""
    if not all(math.isfinite(x) and x>=0 for x in (y,a)):
        raise ContractError('nonnegative finite scaled speeds required')
    if y==0: return 0.0
    if a==0:
        logp=0.5*math.log(2/math.pi)+2*math.log(y)-0.5*y*y
    else:
        # expm1 prevents subtracting two nearly equal Gaussian tails.
        t=2*a*y
        log_ratio=(math.log(-math.expm1(-t))-math.log(t)) if 0<t<math.inf else (
            0.0 if t==0 else -math.log(2)-math.log(a)-math.log(y))
        logp=0.5*math.log(2/math.pi)+2*math.log(y)-0.5*(y-a)**2+log_ratio
    return math.exp(logp)

def constant_sigma_mean_speed_scaled(a:float) -> float:
    """Analytic mean g/s for a constant sigma fixture; not an atomic cross section."""
    if not math.isfinite(a) or a<0: raise ContractError('invalid drift')
    c=math.sqrt(2/math.pi)
    if a<1e-3:
        x=a*a
        return 2*c*(1+x/6-x*x/120+x*x*x/1680)
    return c*math.exp(-a*a/2)+(a+1/a)*math.erf(a/math.sqrt(2))

def maxwell_shell_tail_majorant(a:float,L:float) -> tuple[float,float]:
    """Mathematical formula, numerically evaluated: omitted probability and E[y].

    For |y-a|>L, triangle inequality implies target |w|/s>L.
    A uniform sigma_max then gives K_tail <= sigma_max*s*second.
    Underflow of this floating diagnostic is NOT a zero-tail certificate.
    """
    if not all(math.isfinite(x) and x>=0 for x in (a,L)):
        raise ContractError('invalid nonnegative tail parameters')
    ex=math.exp(-L*L/2); c=math.sqrt(2/math.pi)
    prob=math.erfc(L/math.sqrt(2))+c*L*ex
    return prob,a*prob+c*(L*L+2)*ex
