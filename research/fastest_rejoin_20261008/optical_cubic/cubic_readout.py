"""Exact four-node, three-cell cubic optical readout.

This defines a new interpolant, not dense output from a producer. All nodes and
values must be exact Fractions. Positive quadrature weights are required; this
does not by itself prove that the interpolating polynomial is nonnegative.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from typing import Sequence

class ReadoutError(ValueError):
    """The declared exact readout contract is not satisfied."""

class MissingPremise(ReadoutError):
    """No continuous-output enclosure without explicit error premises."""


def exact(values: Sequence[F]) -> tuple[F, ...]:
    v=tuple(values)
    if any(type(x) is not F for x in v):
        raise ReadoutError('EXACT_FRACTION_INPUT_REQUIRED')
    return v


def multiply(a: Sequence[F], b: Sequence[F]) -> tuple[F, ...]:
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return tuple(out)


def evaluate(a: Sequence[F], x: F) -> F:
    out=F(0)
    for v in reversed(a): out=out*x+v
    return out


def integral(a: Sequence[F], left: F, right: F) -> F:
    return sum((x*(right**(j+1)-left**(j+1))/(j+1)
                for j,x in enumerate(a)),F(0))


@dataclass(frozen=True)
class Panel:
    nodes: tuple[F, ...]
    weights: tuple[F, ...]
    basis: tuple[tuple[F, ...], ...]
    remainder_kernel_abs: F

    def coefficients(self, values: Sequence[F]) -> tuple[F, ...]:
        v=exact(values)
        if len(v)!=4: raise ReadoutError('FOUR_VALUES_REQUIRED')
        return tuple(sum((v[j]*self.basis[j][k] for j in range(4)),F(0))
                     for k in range(4))

    def bernstein_coefficients(self, values: Sequence[F]) -> tuple[F, ...]:
        """Nonnegative coefficients suffice for nonnegative panel interpolation."""
        a=self.coefficients(values)
        return tuple(sum((a[i]*F(comb(k,i),comb(3,i)) for i in range(k+1)),F(0))
                     for k in range(4))


@lru_cache(maxsize=2048)
def panel(nodes: tuple[F, ...]) -> Panel:
    x=exact(nodes)
    if len(x)!=4 or any(x[i+1]<=x[i] for i in range(3)):
        raise ReadoutError('FOUR_ORDERED_DISTINCT_NODES_REQUIRED')
    h=x[-1]-x[0]; u=tuple((z-x[0])/h for z in x)
    bases=[]; weights=[]
    for j in range(4):
        a=(F(1),); den=F(1)
        for k in range(4):
            if k!=j:
                a=multiply(a,(-u[k],F(1)));den*=u[j]-u[k]
        a=tuple(z/den for z in a);bases.append(a)
        weights.append(h*integral(a,F(0),F(1)))
    if any(w<0 for w in weights):
        raise ReadoutError('NEGATIVE_QUADRATURE_WEIGHT')
    omega=(F(1),)
    for z in u:omega=multiply(omega,(-z,F(1)))
    # Nodal polynomial has no other roots. Its sign is fixed in each subcell.
    area=sum((abs(integral(omega,u[i],u[i+1])) for i in range(3)),F(0))
    kernel=h**5*area/24
    return Panel(x,tuple(weights),tuple(bases),kernel)


def panels(nodes: Sequence[F]) -> tuple[Panel, ...]:
    x=exact(nodes)
    if len(x)<4 or (len(x)-1)%3:
        raise ReadoutError('INTERVAL_COUNT_MUST_BE_POSITIVE_MULTIPLE_OF_THREE')
    if any(b<=a for a,b in zip(x,x[1:])):raise ReadoutError('NONINCREASING_CLOCK')
    return tuple(panel(x[i:i+4]) for i in range(0,len(x)-1,3))


def integrate(nodes: Sequence[F], values: Sequence[F]) -> F:
    p=panels(nodes);v=exact(values)
    if len(nodes)!=len(v):raise ReadoutError('NODE_VALUE_COUNT_MISMATCH')
    return sum((sum((w*y for w,y in zip(a.weights,v[3*i:3*i+4])),F(0))
                for i,a in enumerate(p)),F(0))


def geometry(nodes: Sequence[F]) -> dict:
    p=panels(nodes)
    return {'panels':len(p),'kernel_abs_sum':sum((a.remainder_kernel_abs for a in p),F(0)),
        'weight_abs_sum':sum((sum(map(abs,a.weights),F(0)) for a in p),F(0)),
        'min_normalized_weight':min(w/(a.nodes[-1]-a.nodes[0]) for a in p for w in a.weights)}


def conditional_enclosure(nodes: Sequence[F], values: Sequence[F],
                          node_error: Sequence[F] | None,
                          fourth_derivative_bounds: Sequence[F] | None,
                          *, piecewise_C4_asserted: bool=False) -> dict:
    """Conditional on externally justified node errors and per-panel C4 bounds.

    This function checks arithmetic/contracts, not the external proof. Derivative
    values from finite differences are not substituted for a uniform bound.
    Node error must include any background and state errors relative to the
    same continuous target; clocks are fixed, exact, declared inputs.
    """
    if node_error is None or fourth_derivative_bounds is None or not piecewise_C4_asserted:
        raise MissingPremise('NODE_ERROR_AND_PANEL_C4_PREMISES_REQUIRED')
    p=panels(nodes);e=exact(node_error);m=exact(fourth_derivative_bounds)
    if len(e)!=len(nodes) or len(m)!=len(p) or any(z<0 for z in e+m):
        raise ReadoutError('ERROR_BOUND_SHAPE_OR_SIGN')
    center=integrate(nodes,values)
    propagated=sum((sum((abs(w)*b for w,b in zip(a.weights,e[3*i:3*i+4])),F(0))
                    for i,a in enumerate(p)),F(0))
    smooth=sum((a.remainder_kernel_abs*m[i] for i,a in enumerate(p)),F(0))
    radius=propagated+smooth
    return {'center':center,'node_error_radius':propagated,'interpolation_radius':smooth,
            'interval':(center-radius,center+radius),
            'status':'CONDITIONAL_ON_SUPPLIED_PREMISES_NOT_SELF_VALIDATED'}


def restrict(coarse: Sequence[F], fine: Sequence[F], values: Sequence[F]) -> tuple[F, ...]:
    c=exact(coarse);f=exact(fine);v=exact(values)
    if len(f)!=len(v) or len(set(f))!=len(f):raise ReadoutError('INVALID_FINE_SERIES')
    if not c or not f or c[0]!=f[0] or c[-1]!=f[-1]:raise ReadoutError('DOMAIN_MISMATCH')
    mapping=dict(zip(f,v))
    try:return tuple(mapping[x] for x in c)
    except KeyError:raise ReadoutError('MISSING_ACTUAL_COMMON_NODE') from None


def decompose(coarse_nodes: Sequence[F], coarse_values: Sequence[F],
              fine_nodes: Sequence[F], fine_values: Sequence[F]) -> dict:
    restricted=restrict(coarse_nodes,fine_nodes,fine_values)
    c=integrate(coarse_nodes,coarse_values); r=integrate(coarse_nodes,restricted)
    f=integrate(fine_nodes,fine_values)
    return {'total':f-c,'stored_history':r-c,'readout_grid':f-r,
            'identity_residual':(f-c)-((r-c)+(f-r))}
