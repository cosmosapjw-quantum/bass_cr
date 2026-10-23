"""Finite-source FS2010 response and exact contraction of declared PL spectra.

This is independently written code. It does not execute the upstream C reader,
renormalize source channels, extrapolate, or authorize a physical gas coupling.
All energies are eV. The response's first column is *electron* kinetic energy,
despite the original ASCII table heading 'Photon Energy'.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from itertools import product
from math import factorial, fsum, isfinite
from pathlib import Path
from typing import Sequence


AUTHOR_GRID = (
    (0.0001, "log_xi_-4.0.dat"), (0.0002318, "log_xi_-3.6.dat"),
    (0.0004677, "log_xi_-3.3.dat"), (0.001, "log_xi_-3.0.dat"),
    (0.002318, "log_xi_-2.6.dat"), (0.004677, "log_xi_-2.3.dat"),
    (0.01, "log_xi_-2.0.dat"), (0.02318, "log_xi_-1.6.dat"),
    (0.04677, "log_xi_-1.3.dat"), (0.1, "log_xi_-1.0.dat"),
    (0.5, "xi_0.500.dat"), (0.9, "xi_0.900.dat"),
    (0.99, "xi_0.990.dat"), (0.999, "xi_0.999.dat"),
)
RESPONSE_COLUMNS = ("f_ion", "f_heat", "f_exc", "n_Lya", "n_ion_HI", "n_ion_HeI", "n_ion_HeII")
CONTRACTED_COLUMNS = ("ionization_energy_reported", "heat_energy", "excitation_energy", "Lya_number", "HI_ionizations", "HeI_ionizations", "HeII_ionizations")


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def bracket(grid: Sequence[float], value: float) -> tuple[int, float]:
    value = _finite(value, "query")
    if value < grid[0] or value > grid[-1]:
        raise ValueError("query outside finite source grid; extrapolation is not admitted")
    i = min(len(grid) - 2, max(0, bisect_right(grid, value) - 1))
    return i, (value - grid[i]) / (grid[i + 1] - grid[i])


def blend(lo: float, hi: float, t: float) -> float:
    # Explicit endpoints preserve the stored value, including its bit pattern.
    if t == 0.0:
        return lo
    if t == 1.0:
        return hi
    return (1.0 - t) * lo + t * hi


def affine_product_integral(a: float, b: float, *endpoints: tuple[float, float]) -> float:
    """Integral of a product of affine functions using positive Bernstein weights.

    At most three factors are needed here. The polynomial identity is exact;
    floating-point roundoff remains. No cancellation-prone monomial powers.
    """
    n = len(endpoints)
    if not 1 <= n <= 3 or not b > a:
        raise ValueError("need one to three affine factors on a nonempty interval")
    terms = []
    for choices in product((0, 1), repeat=n):
        k = sum(choices)
        weight = factorial(k) * factorial(n - k) / factorial(n + 1)
        term = weight
        for pair, choice in zip(endpoints, choices):
            term *= pair[choice]
        terms.append(term)
    return (b - a) * fsum(terms)


@dataclass(frozen=True)
class PLSpectrum:
    energy: tuple[float, ...]
    number_rate: tuple[float, ...]
    units: str = "electrons_per_Href_per_eta_per_eV"

    def __post_init__(self):
        if self.units != "electrons_per_Href_per_eta_per_eV":
            raise ValueError("spectral number-rate units are required explicitly")
        if len(self.energy) < 2 or len(self.energy) != len(self.number_rate):
            raise ValueError("spectrum needs matching arrays and at least two nodes")
        if not all(isfinite(x) and x > 0 for x in self.energy):
            raise ValueError("spectrum energies must be finite and positive")
        if not all(isfinite(x) and x >= 0 for x in self.number_rate):
            raise ValueError("spectrum number rates must be finite and nonnegative")
        if not all(a < b for a, b in zip(self.energy[:-1], self.energy[1:])):
            raise ValueError("spectrum energy grid must be strictly increasing")

    def at(self, energy: float) -> float:
        i, t = bracket(self.energy, energy)
        return blend(self.number_rate[i], self.number_rate[i + 1], t)

    def injected_energy(self) -> float:
        return fsum(affine_product_integral(a, b, (a, b), (q0, q1))
                    for a, b, q0, q1 in zip(self.energy[:-1], self.energy[1:], self.number_rate[:-1], self.number_rate[1:]))


@dataclass(frozen=True)
class PreparedResponse:
    ionized_grid: tuple[float, ...]
    rows: tuple[tuple[float, ...], ...]
    injected_energy: float
    source_axis: str
    interval_count: int

    def at(self, ionized_fraction: float) -> dict[str, float | str]:
        i, t = bracket(self.ionized_grid, ionized_fraction)
        values = tuple(blend(a, b, t) for a, b in zip(self.rows[i], self.rows[i + 1]))
        result = dict(zip(CONTRACTED_COLUMNS, values))
        result["injected_kinetic_energy"] = self.injected_energy
        result["reported_energy_defect"] = self.injected_energy - fsum(values[:3])
        result["Lya_energy_subset_of_excitation"] = 10.2 * values[3]
        result["source_axis"] = self.source_axis
        result["status"] = "FINITE_SOURCE_RESPONSE_ONLY"
        return result


class FS2010Response:
    """Immutable finite-table response; axis convention is an explicit input.

    `published_c_axis` reproduces the supplied C coordinate vector while exposing
    metadata conflicts. `unambiguous_high_ionization` uses its last five rows,
    whose C coordinates and gas headers agree exactly at printed precision.
    Neither policy supplies a missing primordial He/H ratio or transport closure.
    """

    def __init__(self, table_directory: str | Path, *, axis: str):
        if axis not in ("published_c_axis", "unambiguous_high_ionization"):
            raise ValueError("an explicit supported source-axis convention is required")
        entries = AUTHOR_GRID if axis == "published_c_axis" else AUTHOR_GRID[9:]
        rows, headers, grids = [], [], []
        for x, filename in entries:
            lines = (Path(table_directory) / filename).read_text().splitlines()
            header = tuple(float(z) for z in lines[1].split())
            data = tuple(tuple(float(z) for z in line.split()) for line in lines[3:] if line.strip())
            if len(header) != 5 or len(data) != 258 or any(len(r) != 9 for r in data):
                raise ValueError(f"malformed source table: {filename}")
            if not all(isfinite(v) for row in data for v in row):
                raise ValueError("nonfinite source value")
            grid = tuple(r[0] for r in data)
            if not all(a < b for a, b in zip(grid[:-1], grid[1:])):
                raise ValueError("source energies are not strictly ordered")
            if any(v < 0 for row in data for v in row[1:8]):
                raise ValueError("negative tabulated response")
            if axis == "unambiguous_high_ionization" and (abs(header[0] - (1-x)) > 1e-14 or abs(header[1] - (1-x)) > 1e-14 or abs(header[2] - x) > 1e-14):
                raise ValueError("high-ionization source-state metadata changed")
            grids.append(grid)
            rows.append(tuple(tuple(r[1:8]) for r in data))
            headers.append(header)
        if any(g != grids[0] for g in grids[1:]):
            raise ValueError("different source energy grids")
        self.energy = grids[0]
        self.ionized_grid = tuple(x for x, _ in entries)
        self.rows = tuple(rows)
        self.headers = tuple(headers)
        self.axis = axis

    def at(self, electron_energy_eV: float, ionized_fraction: float) -> tuple[float, ...]:
        j, te = bracket(self.energy, electron_energy_eV)
        i, tx = bracket(self.ionized_grid, ionized_fraction)
        lo = tuple(blend(a, b, te) for a, b in zip(self.rows[i][j], self.rows[i][j + 1]))
        hi = tuple(blend(a, b, te) for a, b in zip(self.rows[i + 1][j], self.rows[i + 1][j + 1]))
        return tuple(blend(a, b, tx) for a, b in zip(lo, hi))

    def require_physical_coupling(self, *, x_HII: float, x_HeII: float, x_HeIII: float, source_He_over_H: float | None, model_He_over_H: float, closure_resolved: bool) -> None:
        """Check necessary conditions; no zero fill or inferred source abundance."""
        for name, value in (("x_HII", x_HII), ("x_HeII", x_HeII), ("x_HeIII", x_HeIII), ("model_He_over_H", model_He_over_H)):
            _finite(value, name)
        bracket(self.ionized_grid, x_HII)
        if x_HII != x_HeII or x_HeIII != 0.0:
            raise ValueError("FS source-state restriction x_HII=x_HeII, x_HeIII=0 fails")
        if source_He_over_H is None:
            raise ValueError("source He/H is not numerically specified by the recovered table package")
        if not isfinite(source_He_over_H) or source_He_over_H <= 0 or model_He_over_H != source_He_over_H:
            raise ValueError("helium abundance does not match the source contract")
        if not closure_resolved:
            raise ValueError("raw source energy defect and photon/loss-time closures remain unresolved")

    def prepare(self, spectrum: PLSpectrum) -> PreparedResponse:
        if spectrum.energy[0] < self.energy[0] or spectrum.energy[-1] > self.energy[-1]:
            raise ValueError("spectrum support exceeds finite source energy domain")
        knots = tuple(sorted(set(spectrum.energy) | {e for e in self.energy if spectrum.energy[0] < e < spectrum.energy[-1]}))
        prepared = []
        for xi in self.ionized_grid:
            channel_terms = [[] for _ in RESPONSE_COLUMNS]
            for a, b in zip(knots[:-1], knots[1:]):
                qa, qb = spectrum.at(a), spectrum.at(b)
                ya, yb = self.at(a, xi), self.at(b, xi)
                for k in range(len(RESPONSE_COLUMNS)):
                    pairs = ((qa, qb), (ya[k], yb[k]))
                    if k < 3:
                        pairs += ((a, b),)
                    channel_terms[k].append(affine_product_integral(a, b, *pairs))
            prepared.append(tuple(fsum(terms) for terms in channel_terms))
        return PreparedResponse(self.ionized_grid, tuple(prepared), spectrum.injected_energy(), self.axis, len(knots)-1)
