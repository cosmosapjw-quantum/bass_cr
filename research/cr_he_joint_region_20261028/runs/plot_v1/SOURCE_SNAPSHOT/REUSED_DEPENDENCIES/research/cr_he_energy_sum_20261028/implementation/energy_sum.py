"""Exact conditional atomwise pair-energy support, with a byte-pinned native port.

The pure core uses finite nonnegative rational masses, singles, and unordered
doubles with E_a + E_b <= K (including the loop test 2 E_a <= K).  K is a
declared conditional cumulative cap, not a measured exclusive kernel.  No
source fit, quadrature, transport, RR, or photon calculation is imported.
"""
from dataclasses import dataclass, fields, is_dataclass, replace
from fractions import Fraction as F
from itertools import groupby
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

UNIT_ID = "CR_PHYS02_HE_ENERGY_SUM_V1"
PREDECESSOR_SHA = "6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d"
NB = F(8750, 47)
HALF = F(1, 2)
ZERO = F(0)
_PREDECESSOR = None


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def exact(value):
    """Core input: int or Fraction only; bool, float and strings are refused."""
    require(type(value) in (int, F), "EXACT_INT_OR_FRACTION_REQUIRED")
    return F(value)


def serial(value):
    if isinstance(value, F):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: serial(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def content_id(value):
    return hashlib.sha256(json.dumps(serial(value), sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Atom:
    key: str
    energy_eV: F
    coefficient: F
    partition: int = 0


@dataclass(frozen=True)
class Event:
    key: str
    electrons: tuple
    coefficient: F


@dataclass(frozen=True)
class Solution:
    K_eV: F
    atom_content_sha256: str
    N: F
    low_mass: F
    high_mass: F
    delta: F
    dmax: F
    target_d: F
    threshold_h_eV: F | None
    dual: tuple
    max_events: tuple
    events: tuple
    cap_digest: str | None = None


def validate_atoms(atoms):
    require(type(atoms) in (tuple, list), "FINITE_ATOM_SEQUENCE_REQUIRED")
    out, seen = [], set()
    for atom in atoms:
        require(type(atom) is Atom, "TYPED_GENERAL_ATOM_REQUIRED")
        require(type(atom.key) is str and bool(atom.key), "NONEMPTY_ATOM_KEY_REQUIRED")
        require(atom.key not in seen, "DUPLICATE_ATOM_KEY")
        seen.add(atom.key)
        energy, weight = exact(atom.energy_eV), exact(atom.coefficient)
        require(energy >= 0 and weight >= 0, "NONNEGATIVE_ATOM_DATA_REQUIRED")
        require(type(atom.partition) is int and atom.partition >= 0,
                "NONNEGATIVE_INTEGER_PARTITION_REQUIRED")
        out.append(Atom(atom.key, energy, weight, atom.partition))
    return tuple(out)


def atom_content_id(atoms):
    return content_id([(a.key, a.energy_eV, a.coefficient, a.partition) for a in atoms])


def solve(atoms, K_eV, *, target_d=None):
    """O(n log n) comparisons and O(n) sweep arithmetic; bit costs are separate.

    Both the maximum witness and requested witness are retained.  The former
    certifies dmax even when the requested target is smaller than dmax.
    """
    atoms, cap = validate_atoms(atoms), exact(K_eV)
    require(cap >= 0, "NONNEGATIVE_ENERGY_CAP_REQUIRED")
    low = sorted((a for a in atoms if a.coefficient and 2 * a.energy_eV <= cap),
                 key=lambda a: (a.energy_eV, a.key))
    high = sorted((a for a in atoms if a.coefficient and 2 * a.energy_eV > cap),
                  key=lambda a: (-a.energy_eV, a.key))
    low_mass = sum((a.coefficient for a in low), ZERO)
    high_mass = sum((a.coefficient for a in high), ZERO)
    total = low_mass + high_mass
    cumulative_high = eligible_low = delta = ZERO
    threshold = None
    pos = 0
    for energy, level in groupby(high, key=lambda a: a.energy_eV):
        cumulative_high += sum((a.coefficient for a in level), ZERO)
        while pos < len(low) and low[pos].energy_eV <= cap - energy:
            eligible_low += low[pos].coefficient
            pos += 1
        deficit = cumulative_high - eligible_low
        if deficit > delta:
            delta, threshold = deficit, energy
    dmax = (total - delta) / 2
    target = dmax if target_d is None else exact(target_d)
    require(0 <= target <= dmax, "TARGET_DOUBLE_OUTSIDE_EXACT_INTERVAL")

    residual = {a.key: a.coefficient for a in atoms}
    maximum = []

    def add(legs, weight):
        if weight:
            maximum.append(Event(f"energy:max:{len(maximum):05d}", legs, weight))

    pos = 0
    for hi in high:
        while residual[hi.key] and pos < len(low):
            lo = low[pos]
            if hi.energy_eV + lo.energy_eV > cap:
                break
            amount = min(residual[hi.key], residual[lo.key])
            add((lo.key, hi.key), amount)
            residual[hi.key] -= amount
            residual[lo.key] -= amount
            if not residual[lo.key]:
                pos += 1
    for atom in atoms:
        remainder = residual[atom.key]
        if remainder:
            is_low = 2 * atom.energy_eV <= cap
            add((atom.key, atom.key) if is_low else (atom.key,),
                remainder / 2 if is_low else remainder)
    maximum = tuple(maximum)
    if target == dmax:
        chosen = maximum
    else:
        # This branch necessarily has dmax > 0; dmax == 0 admits only target 0.
        scale, chosen = target / dmax, []
        residual = {a.key: a.coefficient for a in atoms}
        for event in maximum:
            if len(event.electrons) == 2 and event.coefficient * scale:
                amount = event.coefficient * scale
                chosen.append(Event(f"energy:target:{len(chosen):05d}", event.electrons, amount))
                for key in event.electrons:
                    residual[key] -= amount
        for atom in atoms:
            if residual[atom.key]:
                chosen.append(Event(f"energy:target:{len(chosen):05d}", (atom.key,), residual[atom.key]))
        chosen = tuple(chosen)

    def dual_at(atom):
        if not delta:
            return HALF
        if 2 * atom.energy_eV > cap and atom.energy_eV >= threshold:
            return ZERO
        if 2 * atom.energy_eV <= cap and atom.energy_eV <= cap - threshold:
            return F(1)
        return HALF

    return Solution(cap, atom_content_id(atoms), total, low_mass, high_mass, delta,
                    dmax, target, threshold, tuple((a.key, dual_at(a)) for a in atoms),
                    maximum, chosen)


def _check_events(atoms, events, cap):
    require(type(events) is tuple, "IMMUTABLE_EVENT_TUPLE_REQUIRED")
    amap = {a.key: a for a in atoms}
    marginal = dict.fromkeys(amap, ZERO)
    ids, double, single, cross = set(), ZERO, ZERO, ZERO
    for event in events:
        require(type(event) is Event, "TYPED_ENERGY_EVENT_REQUIRED")
        require(type(event.key) is str and bool(event.key), "NONEMPTY_EVENT_KEY_REQUIRED")
        require(event.key not in ids, "DUPLICATE_EVENT_ID")
        ids.add(event.key)
        weight = exact(event.coefficient)
        require(weight > 0, "POSITIVE_EVENT_WEIGHT_REQUIRED")
        require(type(event.electrons) is tuple and len(event.electrons) in (1, 2)
                and all(type(k) is str and k in amap for k in event.electrons),
                "EVENT_LEG_SUPPORT_MISMATCH")
        for key in event.electrons:
            marginal[key] += weight
        if len(event.electrons) == 2:
            left, right = map(amap.__getitem__, event.electrons)
            require(left.energy_eV + right.energy_eV <= cap, "PAIR_ENERGY_SUPPORT_VIOLATION")
            double += weight
            if left.partition != right.partition:
                cross += weight
        else:
            single += weight
    require(all(marginal[a.key] == a.coefficient for a in atoms), "EXACT_ATOM_MARGINAL_MISMATCH")
    return {"double": double, "single": single, "cross_C": cross,
            "event_records": len(events), "marginal_residual": ZERO}


def verify(atoms, solution):
    """Check primal marginals/support and every dual pair/loop constraint.

    For each dual-value group, its minimum energy is sufficient: a forbidden
    dual sum y+y'<1 has an allowed pair iff those two minimum energies sum to
    <=K.  For the same group the minimum atom may pair with itself, precisely
    the loop condition.  Thus at most six group comparisons cover all pairs,
    including zero-mass vertices, without enumerating n(n+1)/2 pairs.
    """
    atoms = validate_atoms(atoms)
    require(type(solution) is Solution, "TYPED_ENERGY_SOLUTION_REQUIRED")
    cap = exact(solution.K_eV)
    require(cap >= 0, "NONNEGATIVE_ENERGY_CAP_REQUIRED")
    require(solution.atom_content_sha256 == atom_content_id(atoms), "SOLUTION_ATOM_IDENTITY_MISMATCH")
    total = sum((a.coefficient for a in atoms), ZERO)
    low_mass = sum((a.coefficient for a in atoms if 2 * a.energy_eV <= cap), ZERO)
    high_mass = total - low_mass
    require(exact(solution.N) == total and exact(solution.low_mass) == low_mass
            and exact(solution.high_mass) == high_mass, "SOLUTION_MASS_COUNTER_MISMATCH")
    dmax, delta, target = map(exact, (solution.dmax, solution.delta, solution.target_d))
    require(0 <= target <= dmax <= total / 2 and delta == total - 2 * dmax,
            "SOLUTION_OBJECTIVE_IDENTITY_MISMATCH")
    if delta:
        threshold = exact(solution.threshold_h_eV)
        require(any(a.energy_eV == threshold and 2 * a.energy_eV > cap for a in atoms),
                "COMPLETE_HIGH_THRESHOLD_REQUIRED")
        tail = sum((a.coefficient for a in atoms if a.energy_eV >= threshold), ZERO)
        prefix = sum((a.coefficient for a in atoms if 2 * a.energy_eV <= cap
                      and a.energy_eV <= cap - threshold), ZERO)
        require(tail - prefix == delta, "TAIL_DEFICIT_WITNESS_MISMATCH")
    else:
        require(solution.threshold_h_eV is None, "ZERO_DEFICIT_THRESHOLD_MUST_BE_NULL")

    require(type(solution.dual) is tuple, "IMMUTABLE_DUAL_TUPLE_REQUIRED")
    amap, dual, minima = {a.key: a for a in atoms}, {}, {}
    for pair in solution.dual:
        require(type(pair) is tuple and len(pair) == 2, "DUAL_ENTRY_REQUIRED")
        key, value = pair
        require(type(key) is str and key in amap and key not in dual, "DUAL_ATOM_SET_MISMATCH")
        value = exact(value)
        require(value in (ZERO, HALF, F(1)), "HALF_INTEGRAL_DUAL_REQUIRED")
        dual[key] = value
        energy = amap[key].energy_eV
        minima[value] = energy if value not in minima else min(energy, minima[value])
    require(set(dual) == set(amap), "DUAL_ATOM_SET_MISMATCH")
    groups = tuple(minima)
    for i, left in enumerate(groups):
        for right in groups[i:]:
            if left + right < 1:
                require(minima[left] + minima[right] > cap, "DUAL_PAIR_OR_LOOP_INFEASIBLE")
    objective = sum((a.coefficient * dual[a.key] for a in atoms), ZERO)
    maximum = _check_events(atoms, solution.max_events, cap)
    chosen = maximum if solution.events is solution.max_events else _check_events(atoms, solution.events, cap)
    require(maximum["double"] == dmax == objective, "PRIMAL_DUAL_EXACT_GAP_NONZERO")
    require(chosen["double"] == target and chosen["single"] == total - 2 * target,
            "TARGET_DOUBLE_MISMATCH")
    positive = sum(a.coefficient > 0 for a in atoms)
    require(maximum["event_records"] <= positive and chosen["event_records"] <= 2 * positive,
            "SPARSE_WITNESS_RECORD_BOUND_EXCEEDED")
    require(solution.cap_digest is None or (type(solution.cap_digest) is str
            and len(solution.cap_digest) == 64
            and all(c in "0123456789abcdef" for c in solution.cap_digest)), "CAP_DIGEST_FORMAT_MISMATCH")
    return {"status": "PASS_EXACT_CONDITIONAL_ENERGY_SUM", "N": total, "dmax": dmax,
            "target_d": target, "delta": delta, "dual_objective": objective,
            "primal_dual_gap": ZERO, "maximum": maximum, "chosen": chosen,
            "dual_coverage": "ALL_ALLOWED_PAIRS_AND_LOOPS_BY_GROUP_MINIMA",
            "cross_C_scope": "CHOSEN_WITNESS_ONLY_NOT_MAX_C", "physical_activation": False}


def _native_module(path=None):
    global _PREDECESSOR
    if _PREDECESSOR is not None and path is None:
        return _PREDECESSOR
    path = (Path(path) if path is not None else Path(__file__).resolve().parents[2]
            / "cr_he_event_union_20261028/implementation/event_union.py")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == PREDECESSOR_SHA,
            "PREDECESSOR_MODULE_BYTE_IDENTITY_MISMATCH")
    if _PREDECESSOR is None:
        name = "_cr_he_energy_sum_pinned_event_union"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        _PREDECESSOR = module
    return _PREDECESSOR


def load_native(npz_path, *, predecessor_path=None):
    """Only the unchanged byte-pinned predecessor loads/attests the saved NPZ."""
    return _native_module(predecessor_path).load_pinned_source(npz_path)


def _native_atoms(source):
    previous = _native_module()
    previous.validate_source(source)
    require(source.provenance_kind == "STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS"
            and len(source.atoms) == 3201, "ATTESTED_COMPLETE_PHYS02_SOURCE_REQUIRED")
    atoms = tuple(Atom(a.key, a.energy_eV, a.coefficient, a.partition) for a in source.atoms)
    require(atom_content_id(atoms) == source.atom_content_sha256, "NATIVE_CORE_ATOM_IDENTITY_MISMATCH")
    return previous, atoms


def bind_cap(source, K_eV, assumption):
    previous, _ = _native_atoms(source)
    cap = exact(K_eV)
    require(cap >= 0, "NONNEGATIVE_ENERGY_CAP_REQUIRED")
    require(type(assumption) is str and bool(assumption.strip()), "EXPLICIT_CONDITIONAL_ASSUMPTION_REQUIRED")
    value = {"schema": "CR_HE_ENERGY_SUM_CONDITIONAL_CAP_V1", "unit": UNIT_ID,
             "K_eV": cap, "energy_unit": "eV", "assumption": assumption,
             "cap_kind": "CONDITIONAL_CUMULATIVE_PAIR_ENERGY_SUPPORT",
             "atom_content_sha256": source.atom_content_sha256,
             "canonical_source_sha256": source.canonical_source_sha256,
             "attribution_npz_sha256": source.attribution_npz_sha256,
             "predecessor_module_sha256": PREDECESSOR_SHA, "state_id": previous.STATE,
             "actual_physical_K_eV": None}
    return dict(value, digest=content_id(value))


def validate_cap(source, cap):
    require(type(cap) is dict and "K_eV" in cap and "assumption" in cap,
            "TYPED_CONDITIONAL_CAP_BINDING_REQUIRED")
    expected = bind_cap(source, cap["K_eV"], cap["assumption"])
    require(cap == expected, "CONDITIONAL_CAP_BINDING_IDENTITY_MISMATCH")
    return expected


def native_plan(source, cap, *, target_d=None):
    cap = validate_cap(source, cap)
    _, atoms = _native_atoms(source)
    return replace(solve(atoms, cap["K_eV"], target_d=target_d), cap_digest=cap["digest"])


def consume_native(source, cap, solution, window, *, nb_m3=NB, previous_windows=(), bound=None):
    """Full four-partition source return through the unchanged once-only consumer.

    No RR/photon contribution is calculated or added here.  A caller may pass
    an explicit original binding for validation; it must match this window.
    The inventory diagnostic never bypasses the original depletion guard.
    """
    cap = validate_cap(source, cap)
    previous, atoms = _native_atoms(source)
    require(type(solution) is Solution and solution.cap_digest == cap["digest"]
            and solution.K_eV == cap["K_eV"], "SOLUTION_CAP_BINDING_MISMATCH")
    certificate = verify(atoms, solution)
    require(exact(nb_m3) == NB, "EXPLICIT_SAME_STATE_NB_REQUIRED")
    factor = previous.known_window_factor(window)
    if bound is None:
        bound = previous.binding(window, source)
    previous.validate_binding(bound, source)
    require(bound["window"] == tuple(map(previous.exact, window)), "EXPLICIT_WINDOW_BINDING_MISMATCH")
    events = tuple(previous.Event(e.key, e.electrons, e.coefficient) for e in solution.events)
    claims = previous.claims_by_partition(events, source, bound)
    require(tuple(c["partition"] for c in claims) == (0, 1, 2, 3), "FULL_SELECTED_SUPPORT_REQUIRED")
    result = previous.consume_event_union(claims, source, nb_m3=NB, previous_windows=previous_windows)
    lower = max(ZERO, solution.N - F(1085, 94) * F(99, 100) / factor)
    return {"unit": UNIT_ID, "scope": "CONDITIONAL_ENERGY_SUM_FULL_SELECTED_SUPPORT",
            "cap": cap, "certificate": certificate, "source_return": result,
            "coefficient_parent_interval": (solution.N - solution.dmax, solution.N),
            "native_inventory_double_interval": (lower, solution.dmax),
            "proper_window_factor_s2": factor, "source_normalization_reapplied": False,
            "actual_physical_nulls": {key: None for key in (
                "K_eV", "exclusive_He_kernel", "C", "D", "outside_partner_response",
                "projectile_donor_work", "EOS_T", "absolute_volume", "full_source_native25",
                "global_physical_error", "global_budget_remaining", "currency")},
            "physical_activation": False}
