"""Stable, nonnegative convolution kernels for a conservative donor-error bound.
Rates are inverse proper seconds. Returned units are s**2 and s, respectively.
This module evaluates real-arithmetic formulas in FP64, not interval arithmetic.
"""
from __future__ import annotations
import math

def _valid(*args: float) -> None:
    if any(not math.isfinite(x) or x < 0 for x in args):
        raise ValueError('finite nonnegative rates and time required')

def _phi2_signed(rate: float, h: float) -> float:
    x=rate*h
    if abs(x)<.5:
        term=total=.5
        for k in range(1,100):
            term*=x/(k+2); total+=term
            if abs(term)<2e-17*abs(total): break
        return h*h*total
    return (math.expm1(x)-x)/(rate*rate)

def phi2_rate(rate: float, h: float) -> float:
    """Integral_0^h exp(rate*(h-t))*t dt, continuous at rate=0."""
    _valid(rate,h)
    return _phi2_signed(rate,h)

def saturated_convolution(rate: float, hazard: float, h: float) -> float:
    """Integral_0^h exp(rate*(h-t))*(1-exp(-hazard*t)) dt."""
    _valid(rate,hazard,h)
    if hazard==0 or h==0: return 0.0
    return hazard/(rate+hazard)*(rate*_phi2_signed(rate,h)+hazard*_phi2_signed(-hazard,h))
