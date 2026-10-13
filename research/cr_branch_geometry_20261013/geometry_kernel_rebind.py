# SPDX-License-Identifier: GPL-3.0-only
"""Prescribed Bianchi packet transport and source-pinned off-grid ionization.

The physical pushforward uses binary64 momenta and a cancellation-free massive
kinetic energy. Counts and bookkeeping for the resulting finite energies use
exact Fractions. Exact bookkeeping is not a roundoff certificate for transport.
The retained collision source is the existing nonrelativistic cold-target BED
model; using a massive geometry law does not change that collision model.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction as Q
import importlib.util
import math
from pathlib import Path
import sys
from typing import Callable

from scipy.constants import c as C_SI, m_e as ELECTRON_MASS_SI

ROOT = Path(__file__).resolve().parent
EV_J = Q("1.602176634e-19")


def load_bound_kernel():
    """Load the unchanged adapter at its own path, preserving its ROOT binding."""
    name = "bass_cr_branch_geometry_prior_adapter"
    if name not in sys.modules:
        path = ROOT / "inputs/prior/kernel_event_adapter.py"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name].BoundKernel()


def _finite_tuple3(values, name, *, positive=False):
    vals = tuple(float(x) for x in values)
    if len(vals) != 3 or any(not math.isfinite(x) for x in vals):
        raise ValueError(name + " must contain three finite numbers")
    if positive and any(x <= 0 for x in vals):
        raise ValueError(name + " must be strictly positive")
    return vals


def stable_kinetic_eV(momentum_si, *, mass_si=ELECTRON_MASS_SI, c_si=C_SI):
    """W=(pc)^2/(E+mc^2), evaluated without subtraction or squared tiny q.

    The final form also avoids forming E+mc^2 when both are very large.
    Nonfinite and underflowed positive results are rejected, not clipped.
    """
    q = _finite_tuple3(momentum_si, "momentum")
    mass, light = float(mass_si), float(c_si)
    if not (math.isfinite(mass) and mass > 0
            and math.isfinite(light) and light > 0):
        raise ValueError("mass and c must be finite and positive")
    rest = mass * light * light / float(EV_J)
    pc = tuple(x * light / float(EV_J) for x in q)
    if not math.isfinite(rest) or rest <= 0 or any(not math.isfinite(x) for x in pc):
        raise ValueError("energy representation is not finite")
    pnorm = math.hypot(*pc)
    total = math.hypot(rest, pnorm)
    kinetic = (pnorm / total) * pnorm / (1.0 + rest / total)
    if not math.isfinite(kinetic) or (any(q) and kinetic <= 0):
        raise ValueError("kinetic energy is outside the represented positive domain")
    return kinetic


def momentum_from_kinetic_eV(energy_eV, direction, *,
                             mass_si=ELECTRON_MASS_SI, c_si=C_SI):
    """Create an angular witness using pc=sqrt(W)*sqrt(W+2mc^2).

    This is a binary64 initialization; its recovered energy discrepancy is an
    initialization rounding error and must be recorded by its caller.
    """
    w = float(energy_eV)
    direction = _finite_tuple3(direction, "direction")
    norm = math.hypot(*direction)
    mass, light = float(mass_si), float(c_si)
    if (not math.isfinite(w) or w < 0 or norm <= 0
            or not math.isfinite(mass) or mass <= 0
            or not math.isfinite(light) or light <= 0):
        raise ValueError("invalid kinetic-energy initialization")
    rest = mass * light * light / float(EV_J)
    pc = math.sqrt(w) * math.sqrt(w + 2.0 * rest)
    magnitude = pc * float(EV_J) / light
    out = tuple(magnitude * (x / norm) for x in direction)
    if any(not math.isfinite(x) for x in out) or (w > 0 and not any(out)):
        raise ValueError("momentum initialization is not representable")
    return out


@dataclass(frozen=True)
class MomentumAtom:
    label: str
    count: Q
    momentum_si: tuple[float, float, float]

    def __post_init__(self):
        object.__setattr__(self, "count", Q(self.count))
        object.__setattr__(self, "momentum_si",
                           _finite_tuple3(self.momentum_si, "momentum"))
        if not self.label or self.count < 0:
            raise ValueError("atom labels must be nonempty and counts nonnegative")


@dataclass(frozen=True)
class MovedAtom:
    label: str
    count: Q
    before_momentum_si: tuple[float, float, float]
    momentum_si: tuple[float, float, float]
    before_eV: Q
    energy_eV: Q


@dataclass(frozen=True)
class GeometryPushforward:
    atoms: tuple[MovedAtom, ...]
    momentum_ratios: tuple[float, float, float]
    volume_ratio: Q
    before_energy_eV: Q
    after_energy_eV: Q
    geometry_ledger_increment_eV: Q

    @property
    def count(self):
        return sum((a.count for a in self.atoms), Q(0))

    @property
    def particle_work_eV(self):
        return self.after_energy_eV - self.before_energy_eV


def bianchi_pushforward(atoms, scale_before, scale_after, *,
                         mass_si=ELECTRON_MASS_SI, c_si=C_SI):
    """One fixed-reference homogeneous Bianchi-I packet pushforward.

    Input q is physical orthonormal momentum. Counts refer to a comoving cell.
    Volume ratio uses exact interpretations of the supplied finite scale factors.
    Only the resolved packets are moved; an unresolved bath needs its own closure.
    """
    initial = tuple(atoms)
    if len({a.label for a in initial}) != len(initial):
        raise ValueError("packet labels must be unique")
    old = _finite_tuple3(scale_before, "old scale factors", positive=True)
    new = _finite_tuple3(scale_after, "new scale factors", positive=True)
    ratios = tuple(x / y for x, y in zip(old, new))
    if any(not math.isfinite(r) or r <= 0 for r in ratios):
        raise ValueError("momentum transport ratios are not representable")
    volume_ratio = math.prod(Q(y) / Q(x) for x, y in zip(old, new))
    moved = []
    for atom in initial:
        q1 = tuple(r * q for r, q in zip(ratios, atom.momentum_si))
        if any(not math.isfinite(x) for x in q1):
            raise ValueError("transported momentum is not finite")
        if any(q != 0 and qp == 0 for q, qp in zip(atom.momentum_si, q1)):
            raise ValueError("nonzero momentum component underflowed")
        w0 = Q(stable_kinetic_eV(atom.momentum_si, mass_si=mass_si, c_si=c_si))
        w1 = Q(stable_kinetic_eV(q1, mass_si=mass_si, c_si=c_si))
        moved.append(MovedAtom(atom.label, atom.count, atom.momentum_si, q1, w0, w1))
    before = sum((a.count * a.before_eV for a in moved), Q(0))
    after = sum((a.count * a.energy_eV for a in moved), Q(0))
    return GeometryPushforward(tuple(moved), ratios, volume_ratio,
                               before, after, before - after)


def classify_fixed_atoms(atoms, cutoff_eV, *, unresolved_upper_eV=None):
    """Exact classification, equality thermal, with no cumulative state mutation.

    Each item is (label, energy_eV, count). A declared unresolved band prevents a
    downward cutoff from requesting a trace absent from the retained inventory.
    """
    cutoff = Q(cutoff_eV)
    if cutoff < 0:
        raise ValueError("cutoff must be nonnegative")
    if unresolved_upper_eV is not None and cutoff < Q(unresolved_upper_eV):
        raise ValueError("cutoff requests an unretained lower-band trace")
    active, thermal = [], []
    for label, energy, count in tuple(atoms):
        energy, count = Q(energy), Q(count)
        if energy < 0 or count < 0:
            raise ValueError("negative raw atom")
        (thermal if energy <= cutoff else active).append((label, energy, count))
    return {"active": tuple(active), "thermal": tuple(thermal),
            "thermal_count": sum((a[2] for a in thermal), Q(0)),
            "thermal_energy_eV": sum((a[1] * a[2] for a in thermal), Q(0))}


@dataclass(frozen=True)
class EnergyGrid:
    cutoff: Q
    nodes: tuple[Q, ...]

    def __post_init__(self):
        object.__setattr__(self, "cutoff", Q(self.cutoff))
        object.__setattr__(self, "nodes", tuple(Q(x) for x in self.nodes))
        if (self.cutoff < 0 or not self.nodes or self.nodes[0] <= self.cutoff
                or any(b <= a for a, b in zip(self.nodes, self.nodes[1:]))):
            raise ValueError("grid must increase strictly above its cutoff")


@dataclass(frozen=True)
class ProjectionCell:
    energy_eV: Q
    count: Q
    lower_eV: Q
    upper_eV: Q
    lower_count: Q
    upper_count: Q


@dataclass(frozen=True)
class ProjectionLift:
    raw_atoms: tuple[tuple[Q, Q], ...]
    active: dict[int, Q]
    actual_lower_atoms: tuple[tuple[Q, Q], ...]
    ghost_count: Q
    cutoff_eV: Q
    cells: tuple[ProjectionCell, ...]
    lipschitz_geometry_eV: Q
    curvature_geometry_eV2: Q

    @property
    def absorbed_count(self):
        return self.ghost_count + sum((n for _, n in self.actual_lower_atoms), Q(0))

    @property
    def absorbed_energy_eV(self):
        return (self.cutoff_eV * self.ghost_count
                + sum((w * n for w, n in self.actual_lower_atoms), Q(0)))

    def represented_atoms(self, grid):
        atoms = list(self.actual_lower_atoms)
        if self.ghost_count:
            atoms.append((self.cutoff_eV, self.ghost_count))
        atoms.extend((grid.nodes[j], n) for j, n in self.active.items())
        return tuple(atoms)

    def weak_error(self, grid, observable: Callable[[Q], Q]):
        represented = sum((n * Q(observable(w))
                           for w, n in self.represented_atoms(grid)), Q(0))
        raw = sum((n * Q(observable(w)) for w, n in self.raw_atoms), Q(0))
        return represented - raw


def barycentric_projection(atoms, grid):
    """Positive exact count/energy projection plus retained lower-atom trace.

    Input tuples are (energy_eV, count). The lower-atom lift and the aggregate
    absorbed fields are two representations of the same contribution.
    """
    raw = tuple((Q(w), Q(n)) for w, n in atoms)
    active, lower, cells = {}, [], []
    ghost = lip = curv = Q(0)
    for w, count in raw:
        if w < 0 or w > grid.nodes[-1] or count < 0:
            raise ValueError("atom outside the positive saved-grid domain")
        if w <= grid.cutoff:
            lower.append((w, count))
            cells.append(ProjectionCell(w, count, w, w, count, Q(0)))
            continue
        j = bisect_left(grid.nodes, w)
        upper = grid.nodes[j]
        if w == upper:
            active[j] = active.get(j, Q(0)) + count
            cells.append(ProjectionCell(w, count, w, w, count, Q(0)))
            continue
        lo = grid.cutoff if j == 0 else grid.nodes[j-1]
        beta = (w - lo) / (upper - lo)
        nl, nu = count * (1 - beta), count * beta
        active[j] = active.get(j, Q(0)) + nu
        if j:
            active[j-1] = active.get(j-1, Q(0)) + nl
        else:
            ghost += nl
        variance = count * (w-lo) * (upper-w)
        lip += 2 * variance / (upper-lo)
        curv += variance / 2
        cells.append(ProjectionCell(w, count, lo, upper, nl, nu))
    active = {j: n for j, n in active.items() if n}
    return ProjectionLift(raw, active, tuple(lower), ghost, grid.cutoff,
                          tuple(cells), lip, curv)


@dataclass(frozen=True)
class MovedIonizationEvent:
    name: str
    parent_key: str
    parent_energy_eV: Q
    species: str
    probability: Q
    coefficient_m3_s: Q
    binding_eV: Q
    daughters_eV: tuple[Q, Q]
    column: dict[str, Q]
    projection: ProjectionLift


@dataclass(frozen=True)
class MovedIonizationFamily:
    parent_key: str
    parent_energy_eV: Q
    species: str
    binding_eV: Q
    status: str
    total_coefficient_m3_s: Q
    slow_eV: tuple[Q, ...]
    probabilities: tuple[Q, ...]
    grid: EnergyGrid
    source_normalization_diagnostic: tuple | None

    def event(self, quadrature_index):
        if self.status != "ACTIVE":
            raise ValueError("inactive family has no positive sharing events")
        if not 0 <= quadrature_index < len(self.slow_eV):
            raise IndexError("quadrature index outside the rebound sharing rule")
        slow = self.slow_eV[quadrature_index]
        fast = self.parent_energy_eV - self.binding_eV - slow
        if slow < 0 or fast < 0:
            raise ArithmeticError("negative rebound daughter; no clipping allowed")
        projection = barycentric_projection(((slow, Q(1)), (fast, Q(1))), self.grid)
        column = {f"A:{j}": n for j, n in projection.active.items()}
        column[self.parent_key] = Q(-1)
        column["e_th"] = projection.absorbed_count
        column["U_th"] = EV_J * projection.absorbed_energy_eV
        column[self.species] = Q(-1)
        column[{"HI": "HII", "HeI": "HeII"}[self.species]] = Q(1)
        probability = self.probabilities[quadrature_index]
        return MovedIonizationEvent(
            f"moved:{self.species}:{self.parent_key}:{quadrature_index}",
            self.parent_key, self.parent_energy_eV, self.species, probability,
            probability * self.total_coefficient_m3_s, self.binding_eV,
            (slow, fast), {k: v for k, v in column.items() if v}, projection)


def rebind_moved_ionization(kernel, parent_key, parent_energy_eV, species, *,
                            initial_cutoff_eV=None):
    """Reevaluate the original total and sharing kernel at an actual moved W.

    No saved-grid parent index is substituted. The actual finite energy is frozen
    for this collision step; a later trial temperature does not move its parent.
    """
    if not parent_key.startswith("P:") or len(parent_key) <= 2:
        raise ValueError("moved parents require a distinct P:<label> stock key")
    if species not in ("HI", "HeI"):
        raise ValueError("only the source-pinned HI and HeI families are admitted")
    w = Q(parent_energy_eV)
    if not math.isfinite(float(w)) or Q(float(w)) != w:
        raise ValueError("source parent energy must be an exactly represented binary64 value")
    grid = EnergyGrid(kernel.cut, kernel.Eq)
    if w < 0 or w > grid.nodes[-1]:
        raise ValueError("moved energy outside saved-grid support; no extrapolation")
    cutoff = grid.cutoff if initial_cutoff_eV is None else Q(initial_cutoff_eV)
    if cutoff < grid.cutoff:
        raise ValueError("initial cutoff requests the inherited unresolved lower band")
    ion = kernel.ions[species]
    binding = Q(float(ion.B_eV))
    if w <= cutoff:
        status = "BLOCKED_INITIAL_CUTOFF"
    elif w <= binding:
        status = "ZERO_AT_OR_BELOW_IONIZATION_THRESHOLD"
    else:
        status = "ACTIVE"
    if status != "ACTIVE":
        return MovedIonizationFamily(parent_key, w, species, binding, status,
                                     Q(0), (), (), grid, None)
    sigma = float(ion.total_m2(float(w)))
    speed = math.sqrt(2.0 * float(w) * float(EV_J) / ELECTRON_MASS_SI)
    coefficient = speed * sigma
    if not math.isfinite(coefficient) or coefficient <= 0:
        raise ArithmeticError("positive source rate is not represented above threshold")
    slow, probabilities = kernel.original._sharing(ion, float(w))
    finite_probabilities = tuple(Q(float(x)) for x in probabilities)
    if any(x < 0 for x in finite_probabilities):
        raise ArithmeticError("negative source probability")
    normalizer = sum(finite_probabilities, Q(0))
    if normalizer <= 0:
        raise ArithmeticError("nonpositive source sharing normalization")
    exact_probabilities = tuple(x / normalizer for x in finite_probabilities)
    return MovedIonizationFamily(
        parent_key, w, species, binding, status, Q(coefficient),
        tuple(Q(float(x)) for x in slow), exact_probabilities, grid,
        tuple(kernel.original.normalization_diagnostics[-1]))


def event_invariant_residuals(event, kernel):
    """Exact nuclei, charge, energy residuals with the moved parent energy row."""
    col = event.column
    nuclei_h = col.get("HI", Q(0)) + col.get("HII", Q(0))
    nuclei_he = col.get("HeI", Q(0)) + col.get("HeII", Q(0))
    charge = col.get("HII", Q(0)) + col.get("HeII", Q(0)) - col.get("e_th", Q(0))
    energy = col.get("U_th", Q(0))
    for key, count in col.items():
        if key.startswith("A:"):
            charge -= count
            energy += EV_J * kernel.Eq[int(key[2:])] * count
        elif key == event.parent_key:
            charge -= count
            energy += EV_J * event.parent_energy_eV * count
    energy += EV_J * Q(float(kernel.ions["HI"].B_eV)) * col.get("HII", Q(0))
    energy += EV_J * Q(float(kernel.ions["HeI"].B_eV)) * col.get("HeII", Q(0))
    return {"hydrogen_nuclei": nuclei_h, "helium_nuclei": nuclei_he,
            "charge": charge, "total_energy_J": energy}


def _sqrt_upper_rational(value, digits=40):
    """An exact rational upper bound for sqrt(value), with no floating sqrt."""
    value = Q(value)
    if value < 0:
        raise ValueError("negative radicand")
    scale = 10**digits
    ceiling = (value.numerator * scale * scale + value.denominator - 1) // value.denominator
    root = math.isqrt(ceiling)
    if root * root < ceiling:
        root += 1
    return Q(root, scale)


def helium_rate_derivative_bounds(kernel, lower_eV, upper_eV):
    """Exact rational bounds for the ideal frozen-parameter HeI source formula.

    Bounds are for v_nr(W)*sigma_HeI(W), derivative in the eV coordinate. They
    require one interval strictly above the threshold. They do not bound runtime
    transcendental rounding, the HI integral, or a changed sharing quadrature.
    """
    lo, hi = Q(lower_eV), Q(upper_eV)
    ion = kernel.ions["HeI"]
    b = Q(float(ion.B_eV))
    if not b < lo <= hi <= kernel.Eq[-1]:
        raise ValueError("HeI derivative interval must be strictly above threshold and in support")
    t0, t1 = lo / b, hi / b
    a = Q(float(ion.U_eV)) / b + 1
    n, kappa = Q(float(ion.N)), abs(Q(float(ion.K)))
    coefficients = [(k, abs(Q(float(x)))) for k, x in enumerate(ion.coefficients, 2)]
    y0, y1 = 2 / (t0 + 1), 2 / (t1 + 1)
    d0 = sum((x / k * (1-y1**k) for k, x in coefficients), Q(0)) / n
    d1 = sum((x*y0**k for k, x in coefficients), Q(0)) / (n*(t0+1))
    d2 = sum(((k+1)*x*y0**k for k, x in coefficients), Q(0)) / (n*(t0+1)**2)
    log_upper = t1 - 1
    f0 = 1-1/t1 + log_upper/(t0+1)
    f1 = 1/(t0*t0*(t0+1)) + log_upper/(t0+1)**2
    f2 = ((3*t1+2)/(t0**3*(t0+1)**2) + 1/(t0*(t0+1)**2)
          + 2*log_upper/(t0+1)**3)
    b0 = d0*log_upper+kappa*f0
    b1 = d1*log_upper+d0/t0+kappa*f1
    b2 = d2*log_upper+2*d1/t0+d0/t0**2+kappa*f2
    sqrt_t1 = _sqrt_upper_rational(t1)
    g0 = sqrt_t1/(t0+a)
    g1 = 1/(2*(t0+a)) + sqrt_t1/(t0+a)**2
    g2 = 1/(4*t0*(t0+a)) + 1/(t0+a)**2 + 2*sqrt_t1/(t0+a)**3
    c_upper = Q(float(ion.S_m2))*_sqrt_upper_rational(
        2*b*EV_J/Q(float(ELECTRON_MASS_SI)))
    return {"L_m3_s_per_eV": c_upper/b*(g1*b0+g0*b1),
            "M2_m3_s_per_eV2": c_upper/b**2*(g2*b0+2*g1*b1+g0*b2),
            "lower_eV": lo, "upper_eV": hi,
            "interpretation": "ideal_real_formula_of_frozen_finite_source_parameters",
            "runtime_roundoff_included": False}
