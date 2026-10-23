"""Exact atomic inventory, support, event-ledger, and isotope-quotient contracts.

No empirical rate is defined here. Fractions describe declared exact test/input
numbers, not physical uncertainty. No computation or file write runs on import.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import Mapping, Sequence


class ContractError(ValueError):
    pass


def rational(value, name="value") -> Fraction:
    """Read exact integers/decimal strings/Fractions; reject binary floats/bools."""
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ContractError(f"{name}: exact integer, decimal string or Fraction required")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError(f"{name}: finite rational required") from exc


@dataclass(frozen=True)
class Species:
    label: str
    nuclide: str | None
    mass_number: int
    nuclear_charge: int
    charge: int


NUCLIDES = (("n", 1, 0), ("H1", 1, 1), ("D", 2, 1), ("T", 3, 1),
            ("He3", 3, 2), ("He4", 4, 2), ("Li6", 6, 3), ("Li7", 7, 3))
POPULATIONS = tuple(Species(f"{name}:{q}", name, a, z, q)
                    for name, a, z in NUCLIDES for q in range(z + 1))
SPECIES = POPULATIONS + (Species("e", None, 0, 0, -1),)
LABELS = tuple(s.label for s in SPECIES)
POPULATION_LABELS = LABELS[:-1]
INDEX = {s.label: i for i, s in enumerate(SPECIES)}


def inventory(values: Mapping[str, object]) -> tuple[Fraction, ...]:
    """Require all 21 declared populations, including explicit zero n/T entries."""
    if not isinstance(values, Mapping) or set(values) != set(POPULATION_LABELS):
        raise ContractError("inventory must explicitly name all and only 21 populations")
    out = tuple(rational(values[k], k) for k in POPULATION_LABELS)
    if any(v < 0 for v in out):
        raise ContractError("inventory populations must be nonnegative")
    return out


@dataclass(frozen=True)
class Reaction:
    identifier: str
    kind: str
    nuclide: str
    lower_charge: int
    reactants: tuple[tuple[str, int], ...]
    products: tuple[tuple[str, int], ...]
    radiation_owner: str

    def net(self) -> tuple[int, ...]:
        out = [0] * len(SPECIES)
        for label, count in self.reactants:
            out[INDEX[label]] -= count
        for label, count in self.products:
            out[INDEX[label]] += count
        return tuple(out)


def rung(nuclide: str, lower_charge: int, kind="CI") -> Reaction:
    info = {n: z for n, _, z in NUCLIDES}
    if nuclide not in info or isinstance(lower_charge, bool) or not isinstance(lower_charge, int):
        raise ContractError("unknown nuclide or non-integer charge")
    if not 0 <= lower_charge < info[nuclide]:
        raise ContractError("charge rung outside the declared inventory")
    lo, hi = f"{nuclide}:{lower_charge}", f"{nuclide}:{lower_charge + 1}"
    if kind == "CI":
        reactants, products, rad = ((lo, 1), ("e", 1)), ((hi, 1), ("e", 2)), "none"
    elif kind == "PI":
        reactants, products, rad = ((lo, 1),), ((hi, 1), ("e", 1)), "incoming_photon"
    elif kind == "RR":
        reactants, products, rad = ((hi, 1), ("e", 1)), ((lo, 1),), "outgoing_photon"
    else:
        raise ContractError("kind must be CI, PI or RR")
    return Reaction(f"{kind}:{lo}->{hi}", kind, nuclide, lower_charge, reactants, products, rad)


def all_rungs(kind="CI") -> tuple[Reaction, ...]:
    return tuple(rung(n, q, kind) for n, _, z in NUCLIDES for q in range(z))


def conservation_residuals(net: Sequence[int]) -> dict[str, int]:
    """Eight separate nuclides plus electric charge; total baryons also returned."""
    if len(net) != len(SPECIES) or any(isinstance(v, bool) or not isinstance(v, int) for v in net):
        raise ContractError("stoichiometry requires exactly 22 integer components")
    out = {n: sum(v for v, s in zip(net, SPECIES) if s.nuclide == n) for n, _, _ in NUCLIDES}
    out["charge"] = sum(s.charge * v for s, v in zip(SPECIES, net))
    out["baryon"] = sum(s.mass_number * v for s, v in zip(SPECIES, net))
    return out


@dataclass(frozen=True)
class SupportDecision:
    status: str
    known_value: Fraction | None
    source_identity: str

    def require_physical_value(self) -> Fraction:
        if self.known_value is None:
            raise ContractError("no scalar rate/cross section supplied by coverage metadata")
        return self.known_value


@dataclass(frozen=True)
class SourceSupport:
    """Incident-energy support in eV for one explicitly named target/process.

    threshold_eV is the provider's explicitly admitted kinematic zero threshold.
    It need not equal a chemical binding defect or a table's first knot. Unknown
    threshold is None. A covered point still needs an actual provider evaluation.
    """
    target: str
    process: str
    source_identity: str
    lower_eV: Fraction
    upper_eV: Fraction
    threshold_eV: Fraction | None = None

    def __post_init__(self):
        if not all(isinstance(x, str) and x.strip() == x and x for x in
                   (self.target, self.process, self.source_identity)):
            raise ContractError("explicit target, process and source identity required")
        lo, hi = rational(self.lower_eV), rational(self.upper_eV)
        th = None if self.threshold_eV is None else rational(self.threshold_eV)
        if lo < 0 or hi <= lo or (th is not None and (th < 0 or th > lo)):
            raise ContractError("invalid support/threshold ordering")
        object.__setattr__(self, "lower_eV", lo)
        object.__setattr__(self, "upper_eV", hi)
        object.__setattr__(self, "threshold_eV", th)

    def classify(self, energy_eV) -> SupportDecision:
        e = rational(energy_eV, "incident energy")
        if e < 0:
            raise ContractError("incident energy must be nonnegative")
        if self.threshold_eV is not None and e < self.threshold_eV:
            return SupportDecision("PHYSICAL_THRESHOLD_ZERO", Fraction(0), self.source_identity)
        if self.lower_eV <= e <= self.upper_eV:
            return SupportDecision("SOURCE_COVERED_VALUE_NOT_EVALUATED", None, self.source_identity)
        return SupportDecision("UNCOVERED_UNKNOWN", None, self.source_identity)


def ionization_ledger(*, chemical_defect_eV, incoming_electron_eV,
                      outgoing_electrons_eV: Sequence[object],
                      incoming_photon_eV="0", recoil_eV="0", escaped_photon_eV="0") -> dict[str, Fraction]:
    """Exact supplied-event accounting. No closure remainder is manufactured.

    All electron energies are kinetic energies of the chosen explicit electron
    pool. An independently supplied outgoing sum is essential; this function
    does not infer missing secondary-electron energies or thermalization.
    """
    chi = rational(chemical_defect_eV, "chemical defect")
    kin = rational(incoming_electron_eV, "incoming electron")
    photon = rational(incoming_photon_eV, "incoming photon")
    recoil = rational(recoil_eV, "recoil")
    escaped = rational(escaped_photon_eV, "escaped photon")
    if isinstance(outgoing_electrons_eV, (str, bytes)) or not outgoing_electrons_eV:
        raise ContractError("explicit outgoing electron energy sequence required")
    outs = tuple(rational(x, "outgoing electron") for x in outgoing_electrons_eV)
    if chi <= 0 or min((kin, photon, recoil, escaped) + outs) < 0:
        raise ContractError("positive binding defect and nonnegative kinetic/radiative energies required")
    de = sum(outs, Fraction(0)) - kin
    dr = escaped - photon
    return {"electron_kinetic_change_eV": de, "binding_change_eV": chi,
            "radiation_change_eV": dr, "recoil_change_eV": recoil,
            "residual_eV": de + chi + dr + recoil}


def recoil_momentum_transfer_factor(electron_mass, target_mass) -> Fraction:
    """2*m*M/(m+M)^2: stationary-target elastic loss = factor*E*sigma_mt.

    Both masses use the same unit; sigma_mt=int(1-cos theta_cm)d sigma.
    A physical cross section and moving-target averaging remain caller inputs.
    """
    m, M = rational(electron_mass), rational(target_mass)
    if min(m, M) <= 0:
        raise ContractError("positive masses required")
    return 2 * m * M / (m + M)**2


def relative_maxwell_parameters(*, projectile_mass, target_mass,
                               projectile_temperature, target_temperature) -> dict[str, Fraction]:
    """No-drift, NR isotropic independent Maxwellians; theta_rel = k_B*T_rel."""
    m, M = rational(projectile_mass), rational(target_mass)
    te, ta = rational(projectile_temperature), rational(target_temperature)
    if min(m, M) <= 0 or min(te, ta) < 0:
        raise ContractError("positive masses and nonnegative temperatures required")
    mu = m * M / (m + M)
    return {"reduced_mass": mu, "relative_temperature": mu * (te / m + ta / M)}


def _generator(matrix: Sequence[Sequence[object]]) -> tuple[tuple[Fraction, ...], ...]:
    g = tuple(tuple(rational(x, "generator coefficient") for x in row) for row in matrix)
    n = len(g)
    if n < 2 or any(len(row) != n for row in g):
        raise ContractError("square generator with at least two charge states required")
    if any(g[i][j] < 0 for i in range(n) for j in range(n) if i != j):
        raise ContractError("generator off-diagonal entries must be nonnegative")
    if any(sum(g[i][j] for i in range(n)) != 0 for j in range(n)):
        raise ContractError("column-oriented generator must conserve nuclei")
    return g


def isotope_quotient_at_state(generators: Mapping[str, Sequence[Sequence[object]]],
                              binding_energies: Mapping[str, Sequence[object]]) -> dict:
    """Exact algebra at one supplied bath state; no all-T/function claim follows.

    For arbitrary isotope inventories, number closure uses the same G for each
    isotope. A common energy source further needs epsilon_A^T G_A independent
    of isotope. Connected common G makes this equivalent to constant offsets
    between epsilon_A and a representative epsilon. No tolerance is invented.
    """
    if len(generators) < 2 or set(generators) != set(binding_energies):
        raise ContractError("matching explicit generators/energies for >=2 isotopes required")
    names = tuple(generators)
    if any(not isinstance(k, str) or not k for k in names):
        raise ContractError("explicit isotope names required")
    gs = {a: _generator(generators[a]) for a in names}
    n = len(gs[names[0]])
    if any(len(g) != n for g in gs.values()):
        raise ContractError("all grouped isotopes must have the same charge-state count")
    es = {a: tuple(rational(x, "binding energy") for x in binding_energies[a]) for a in names}
    if any(len(e) != n for e in es.values()):
        raise ContractError("binding energy shape mismatch")
    rows = {a: tuple(sum(es[a][i] * gs[a][i][j] for i in range(n)) for j in range(n))
            for a in names}
    ref = names[0]
    number_ok = all(gs[a] == gs[ref] for a in names)
    energy_ok = all(rows[a] == rows[ref] for a in names)
    return {"scope": "EXACT_FOR_SUPPLIED_GENERATORS_AT_ONE_STATE",
            "reference_isotope": ref, "number_quotient": number_ok,
            "binding_source_quotient": energy_ok,
            "joint_quotient": number_ok and energy_ok,
            "energy_source_rows": rows,
            "energy_row_differences": {a: tuple(x - y for x, y in zip(rows[a], rows[ref])) for a in names},
            "all_state_physical_equivalence": None}
