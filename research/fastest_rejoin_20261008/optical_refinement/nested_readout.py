"""Exact readout differences on nested grids, not bounds on a physical IVP.

Every abscissa and ordinate must already be a Fraction. Construct native inputs
with Fraction.from_float(float(text)); parsing the decimal text as a rational
would select a different source interpretation. Signed contrasts are permitted.
"""
from __future__ import annotations
from fractions import Fraction as F
from typing import Sequence

class ReadoutError(ValueError):
    """A readout has incompatible clocks, values or refinement semantics."""


def checked_series(x: Sequence[F], y: Sequence[F]) -> None:
    if len(x) != len(y) or len(x) < 2:
        raise ReadoutError('INCOMPLETE_SERIES')
    if not all(isinstance(v, F) for v in (*x, *y)):
        raise ReadoutError('EXACT_FRACTIONS_REQUIRED')
    if any(b <= a for a,b in zip(x,x[1:])):
        raise ReadoutError('NONINCREASING_CLOCK')


def cumulative(x: Sequence[F], y: Sequence[F]) -> list[F]:
    checked_series(x,y)
    out=[F(0)]
    for a,b,fa,fb in zip(x,x[1:],y,y[1:]):
        out.append(out[-1]+(b-a)*(fa+fb)/2)
    return out


def integrate(x: Sequence[F], y: Sequence[F]) -> F:
    return cumulative(x,y)[-1]


def restrict(coarse_x: Sequence[F], fine_x: Sequence[F], fine_y: Sequence[F]) -> list[F]:
    checked_series(fine_x,fine_y)
    checked_series(coarse_x,[F(0)]*len(coarse_x))
    if (coarse_x[0],coarse_x[-1]) != (fine_x[0],fine_x[-1]):
        raise ReadoutError('TIME_WINDOWS_DIFFER')
    mapping=dict(zip(fine_x,fine_y))
    if any(t not in mapping for t in coarse_x):
        raise ReadoutError('COARSE_NODES_NOT_EXACTLY_IN_FINE_GRID')
    return [mapping[t] for t in coarse_x]


def decompose_refinement(coarse_x: Sequence[F], coarse_y: Sequence[F],
                         fine_x: Sequence[F], fine_y: Sequence[F]) -> dict:
    """T_f(y_f)-T_c(y_c) = T_c(y_f|c-y_c) + [T_f(y_f)-T_c(y_f|c)].

    The first term changes the stored history at common nodes; the second
    changes the interpolated readout of ONE fine history. Neither is a true
    continuous-solution error estimate. Local grid defects can have either sign.
    """
    checked_series(coarse_x,coarse_y)
    fy=restrict(coarse_x,fine_x,fine_y)
    trajectory=integrate(coarse_x,[b-a for a,b in zip(coarse_y,fy)])
    fine_total=integrate(fine_x,fine_y)
    coarse_total=integrate(coarse_x,coarse_y)
    grid=fine_total-integrate(coarse_x,fy)
    idx={t:i for i,t in enumerate(fine_x)}
    cells=[]
    for k,(a,b) in enumerate(zip(coarse_x,coarse_x[1:])):
        lo,hi=idx[a],idx[b]
        cells.append(integrate(fine_x[lo:hi+1],fine_y[lo:hi+1])-(b-a)*(fy[k]+fy[k+1])/2)
    total=fine_total-coarse_total
    if trajectory+grid != total or sum(cells,F(0)) != grid:
        raise ArithmeticError('EXACT_DECOMPOSITION_FAILED')
    return {'coarse':coarse_total,'fine':fine_total,'total':total,
            'trajectory':trajectory,'readout_grid':grid,'grid_cells':cells,
            'sum_abs_grid_cells':sum(map(abs,cells),F(0)),
            'sum_abs_two_terms':abs(trajectory)+abs(grid)}


def signed_pair(xa: Sequence[F], ya: Sequence[F], xb: Sequence[F], yb: Sequence[F]) -> list[F]:
    checked_series(xa,ya);checked_series(xb,yb)
    if tuple(xa)!=tuple(xb):
        raise ReadoutError('PAIRED_CLOCKS_DIFFER')
    return [b-a for a,b in zip(ya,yb)]


def cancellation_condition(terms: Sequence[F]) -> F | None:
    """Absolute sum divided by absolute signed sum; null when sum is zero."""
    if not terms or not all(isinstance(v,F) for v in terms):
        raise ReadoutError('EXACT_NONEMPTY_TERMS_REQUIRED')
    signed=sum(terms,F(0))
    return sum(map(abs,terms),F(0))/abs(signed) if signed else None
