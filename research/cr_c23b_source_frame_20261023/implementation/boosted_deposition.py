"""Positive exact angular contraction into the finite C23A FS2010 table.

The tabulated interpolation is linear in energy and ionized fraction. Integrate
its energy hat basis once against the boosted positive atomic measure, then
reuse the resulting nonnegative node weights. This closes the angular integral
of the adopted finite interpolant, not the physical transport outside its grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import fsum
from boost_kernel import AngularBox, Boost, ElectronMeasure
from vendor.fs2010_operator import (
    FS2010Response, CONTRACTED_COLUMNS, affine_product_integral, blend, bracket,
)


@dataclass(frozen=True)
class PreparedBoostedResponse:
    ionized_grid: tuple[float, ...]
    rows: tuple[tuple[float, ...], ...]
    number_basis: tuple[float, ...]
    energy_basis: tuple[float, ...]
    partition: dict
    source_axis: str
    source_identity: str
    units: str
    boost_u: float
    actual_overlap_cells: int

    def at(self, ionized_fraction: float) -> dict:
        i, t = bracket(self.ionized_grid, ionized_fraction)
        values = tuple(blend(a, b, t) for a, b in zip(self.rows[i], self.rows[i+1]))
        result = dict(zip(CONTRACTED_COLUMNS, values))
        covered = self.partition["covered"]
        result.update(
            covered_number=covered.number,
            covered_kinetic_energy=covered.kinetic_ev,
            all_number=self.partition["all"].number,
            all_kinetic_energy=self.partition["all"].kinetic_ev,
            below_number=self.partition["below"].number,
            below_kinetic_energy=self.partition["below"].kinetic_ev,
            above_number=self.partition["above"].number,
            above_kinetic_energy=self.partition["above"].kinetic_ev,
            reported_energy_defect=covered.kinetic_ev-fsum(values[:3]),
            Lya_energy_subset_of_excitation=10.2*values[3],
            unresolved_tail_heat=None,
            unresolved_tail_ionization=None,
            source_axis=self.source_axis,
            source_identity=self.source_identity,
            spectrum_units=self.units,
            boost_u=self.boost_u,
            status="FINITE_SOURCE_COMPONENT_ONLY",
            physical_gas_coupling="NOT_ADMITTED",
            global_error_bound=None,
        )
        return result


def prepare_boosted(response: FS2010Response, source: ElectronMeasure,
                    boost: Boost) -> PreparedBoostedResponse:
    """Precontract a positive measure with no inferred or zero-filled tails."""
    source.require_boost(boost)
    grid = response.energy
    nterms = [[] for _ in grid]
    eterms = [[] for _ in grid]
    cells = 0
    for k, weight in zip(source.kinetic_ev, source.number):
        if weight == 0:
            continue
        box = AngularBox.from_energy(k, boost)
        if box.half_width_ev == 0:
            e = box.center_ev
            if not grid[0] <= e <= grid[-1]:
                continue
            j, t = bracket(grid, e)
            nterms[j].append(weight*(1-t)); nterms[j+1].append(weight*t)
            eterms[j].append(weight*e*(1-t)); eterms[j+1].append(weight*e*t)
            cells += 1
            continue
        for j, (left, right) in enumerate(zip(grid[:-1], grid[1:])):
            mu_lo, mu_hi = box.angular_interval(left, right)
            if mu_hi <= mu_lo:
                continue
            a = box.lower_ev if mu_lo == -1 else left
            b = box.upper_ev if mu_hi == 1 else right
            t0, t1 = (a-left)/(right-left), (b-left)/(right-left)
            factor = weight*(mu_hi-mu_lo)/2
            # Integrate in normalized angle, which remains resolved even when
            # bath-energy endpoints round to the same float at tiny boosts.
            nl = affine_product_integral(0, 1, (1-t0, 1-t1))*factor
            nr = affine_product_integral(0, 1, (t0, t1))*factor
            el = affine_product_integral(0, 1, (a, b), (1-t0, 1-t1))*factor
            er = affine_product_integral(0, 1, (a, b), (t0, t1))*factor
            nterms[j].append(nl); nterms[j+1].append(nr)
            eterms[j].append(el); eterms[j+1].append(er)
            cells += 1
    nbase, ebase = tuple(map(fsum, nterms)), tuple(map(fsum, eterms))
    if any(x < 0 for x in (*nbase, *ebase)):
        raise ArithmeticError("positive interpolation basis produced a negative weight")
    rows = []
    for table in response.rows:
        rows.append(tuple(fsum((ebase if c < 3 else nbase)[j]*row[c]
                               for j, row in enumerate(table)) for c in range(7)))
    return PreparedBoostedResponse(
        response.ionized_grid, tuple(rows), nbase, ebase,
        source.finite_domain(boost, grid[0], grid[-1]), response.axis,
        source.identity, source.units, boost.u, cells,
    )
