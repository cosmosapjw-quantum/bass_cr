"""80-digit rest-angle reference, independent of the producer energy-box code."""
from __future__ import annotations
import mpmath as mp


def reference(k_float, u_float, mass_float, lo_float, hi_float, *, lower_closed=True, upper_closed=False):
    """Exact-float inputs; two-node angular Gauss integrates affine moments."""
    k, u, mass, lo = map(mp.mpf, (k_float, u_float, mass_float, lo_float))
    hi = mp.inf if hi_float == float('inf') else mp.mpf(hi_float)
    gamma = mp.sqrt(1 + u*u)
    q = mp.sqrt(k*(k+2*mass))
    center = gamma*(k+mass)-mass
    width = u*q
    if u == 0 or k == 0:
        inside = (center > lo or (lower_closed and center == lo)) and (center < hi or (upper_closed and center == hi))
        return (mp.mpf(1), center, center+mass, u*(k+mass)) if inside else (mp.mpf(0),)*4
    ml = max(mp.mpf(-1), (lo-center)/width)
    mu = min(mp.mpf(1), (hi-center)/width)
    if mu <= ml:
        return (mp.mpf(0),)*4
    mid, half = (ml+mu)/2, (mu-ml)/2
    nodes = (mid-half/mp.sqrt(3), mid+half/mp.sqrt(3))
    answers=[]
    for cosine in nodes:
        kinetic = gamma*(k+mass)+u*q*cosine-mass
        parallel = gamma*q*cosine+u*(k+mass)
        answers.append((mp.mpf(1), kinetic, kinetic+mass, parallel))
    return tuple(half*(answers[0][i]+answers[1][i])/2 for i in range(4))


def endpoints(k_float, u_float, mass_float):
    k,u,m = map(mp.mpf, (k_float,u_float,mass_float))
    g=mp.sqrt(1+u*u)
    a=g*(k+m)-m
    b=u*mp.sqrt(k*(k+2*m))
    return a-b,a+b,a,b
