"""Separate FP64 inner-arc panel rule; original radial Gauss rule on each panel.

At fixed r0, a=r0*cos(theta), rho=r0*sin(theta), hence every azimuthal
ETF phase satisfies |dPhi/dtheta| <= |k|*r0. The panel budget bounds phase
variation, NOT quadrature error. In atomic units speed=|vP-vT|=|k|.
Original outer cells/nodes and inner FEM boundaries are retained verbatim.
"""
from __future__ import annotations

import math
import numpy as np
from numpy.polynomial.legendre import leggauss


def _positive(value, name, *, zero=False):
    if np.ndim(value) != 0 or isinstance(value, (bool, np.bool_)):
        raise ValueError(f'{name} must be a finite scalar')
    value = float(value)
    if not math.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError(f'invalid {name}')
    return value


def _cap(max_segments):
    if type(max_segments) is not int or not 1 <= max_segments <= 65536:
        raise ValueError('max_segments must be an integer in 1..65536')
    return max_segments


def arc_inner_edges(inner, r0, R, speed, *, beta=24., max_segments=8192):
    """Preserve all input endpoints; bound segments per one outer Gauss node.

    Constructed triangle endpoints use their exact angles 0/pi; remaining
    acos arguments are clipped ONLY within 64*eps of [-1,1]. Other invalid
    geometry, nonfinite arithmetic or rounded duplicate cuts is rejected.
    """
    r0 = _positive(r0, 'r0'); R = _positive(R, 'R')
    speed = _positive(speed, 'speed', zero=True)
    beta = _positive(beta, 'beta'); _cap(max_segments)
    inner = np.asarray(inner, dtype=float)
    if (inner.ndim != 1 or not 2 <= len(inner) <= max_segments + 1
            or not np.isfinite(inner).all() or inner[0] < 0
            or np.any(np.diff(inner) <= 0)):
        raise ValueError('finite increasing bounded inner edges required')
    lo, hi = abs(R-r0), R+r0
    if inner[0] < lo or inner[-1] > hi:
        raise ValueError('inner endpoints outside distance triangle')
    if speed == 0:
        return inner.copy()
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        cosine = ((r0-inner)*(r0+inner)+R*R)/(2*R*r0)
    # The distance law loses relative digits when r0/R is small. These are
    # known triangle-boundary angles, not a clamp of an invalid interior point.
    cosine[inner == lo] = 1.
    cosine[inner == hi] = -1.
    tol = 64*np.finfo(float).eps
    if not np.isfinite(cosine).all() or np.any(abs(cosine) > 1+tol):
        raise ArithmeticError('unresolved acos geometry')
    theta = np.arccos(np.clip(cosine, -1., 1.))
    width = np.diff(theta)
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        required = (speed*r0/beta)*width
    if (not np.isfinite(required).all() or np.any(width <= 0)
            or np.any(required > max_segments)):
        raise ValueError('phase segmentation exceeds cap or angular resolution')
    counts = np.maximum(1, np.ceil(required).astype(np.int64))
    if int(counts.sum()) > max_segments:
        raise ValueError('phase segmentation exceeds per-packet cap')
    if np.all(counts == 1):
        return inner.copy()
    parts = [inner[:1]]
    for i, count in enumerate(counts):
        if count > 1:
            angles = theta[i] + width[i]*np.arange(1, count)/count
            with np.errstate(over='ignore', invalid='ignore'):
                cuts = np.sqrt((r0-R)**2+4*R*r0*np.sin(angles/2)**2)
            if (not np.isfinite(cuts).all() or np.any(cuts <= inner[i])
                    or np.any(cuts >= inner[i+1]) or np.any(np.diff(cuts) <= 0)):
                raise ArithmeticError('unresolved interior arc cuts')
            parts.append(cuts)
        parts.append(inner[i+1:i+2])
    return np.concatenate(parts)


def phase_pairs(edges, R, order, speed, *, phase_budget=24., max_segments=8192):
    """pair_rule(edges,R,order,speed) API for continuous_exact_cross.cross.

    max_segments bounds each emitted packet by max_segments*order nodes;
    packets are streamed. Outer splitting and Gauss arithmetic match the
    original geometry_pairs. This algorithm changes numerical quadrature
    and requires its own context and convergence qualification.
    """
    edges = np.asarray(edges, dtype=float)
    _cap(max_segments)
    if (edges.ndim != 1 or not 2 <= len(edges) <= max_segments+1
            or edges[0] != 0 or not np.isfinite(edges).all()
            or np.any(np.diff(edges) <= 0)):
        raise ValueError('finite increasing bounded edges starting at zero required')
    R = _positive(R, 'R'); speed = _positive(speed, 'speed', zero=True)
    beta = _positive(phase_budget, 'phase_budget')
    if type(order) is not int or not 2 <= order <= 64:
        raise ValueError('order must be an integer in 2..64')
    L = float(edges[-1])
    if not np.isfinite(R+L) or not np.isfinite(2*L):
        raise ValueError('unresolved radius scale')
    if R >= 2*L:
        return
    v = np.r_[edges, abs(R-edges), R+edges, 0., L]
    outer = np.unique(v[(v >= 0) & (v <= L)])
    x, w = leggauss(order)
    for a, b in zip(outer[:-1], outer[1:]):
        if b-a <= 64*np.finfo(float).eps*max(1., L):
            continue
        r0s = (b+a)/2+(b-a)*x/2; w0s = (b-a)*w/2
        for r0, w0 in zip(r0s, w0s):
            lo = abs(R-r0); hi = min(R+r0, L)
            if hi <= lo:
                continue
            inner = np.r_[lo, edges[(edges > lo) & (edges < hi)], hi]
            panel = arc_inner_edges(inner, r0, R, speed, beta=beta,
                                    max_segments=max_segments)
            aa, bb = panel[:-1], panel[1:]
            r1 = ((bb+aa)[:, None]/2+(bb-aa)[:, None]*x/2).ravel()
            w1 = ((bb-aa)[:, None]*w/2).ravel()
            weight = w0*w1*r0*r1/R
            if (not np.isfinite(r1).all() or not np.isfinite(weight).all()
                    or np.any(weight <= 0) or np.any(np.diff(r1) <= 0)
                    or r1[0] <= lo or r1[-1] >= hi):
                raise ArithmeticError('unresolved Gauss packet')
            yield np.full_like(r1, r0), r1, weight
