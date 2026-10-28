"""Exact two-threshold dual and same-state adapter for cross-bin events."""
from __future__ import annotations
from bisect import bisect_left, bisect_right
from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import cross_flow

Atom = cross_flow.Atom
CONSUMER_SHA = "6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d"
NB = F(8750, 47)
_CONSUMER = None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def exact(x):
    require(type(x) in (int, F), "EXACT_INT_OR_FRACTION_REQUIRED")
    return F(x)


def serial(x):
    if isinstance(x, F):
        return str(x)
    if is_dataclass(x):
        return serial(asdict(x))
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    return x


def digest(x):
    return hashlib.sha256(json.dumps(serial(x), sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Bound:
    atom_digest: str
    K_eV: F
    total: F
    deficit: F
    cmax: F
    independent: tuple[str, ...]
    neighbors: tuple[str, ...]
    dual: tuple[tuple[str, F], ...]
    partition: int | None
    e_threshold: F | None
    h_threshold: F | None


@dataclass(frozen=True)
class ConstructedWitness:
    cross_C: F
    pairs: tuple
    singles: tuple
    method: str = "PR112_HALF_SHIFT_FILTERED_CROSS"
    flow_value: None = None
    mincut_capacity: None = None
    mincut_dual: None = None


class _Cumulative:
    def __init__(self, atoms):
        rows = sorted(atoms, key=lambda a: (a.energy_eV, a.key))
        self.energy = [a.energy_eV for a in rows]
        self.levels = sorted(set(self.energy))
        self.prefix = [F(0)]
        for a in rows:
            self.prefix.append(self.prefix[-1] + a.coefficient)
        self.total = self.prefix[-1]

    def below_equal(self, e):
        return self.prefix[bisect_right(self.energy, e)]

    def above_equal(self, e):
        return self.total - self.prefix[bisect_left(self.energy, e)]


def upper_bound(atoms, K_eV):
    atoms = cross_flow.validate_atoms(atoms)
    K = exact(K_eV)
    require(K >= 0, "NEGATIVE_CAP")
    total = sum((a.coefficient for a in atoms), F(0))
    best, choice = F(0), None
    for r in sorted({a.partition for a in atoms}):
        own = _Cumulative([a for a in atoms if a.partition == r])
        other = _Cumulative([a for a in atoms if a.partition != r])
        h = other.levels
        # The last index is the empty-outside (h=infinity) candidate.
        suffix = [(F(0), None)] * (len(h) + 1)
        for j in range(len(h) - 1, -1, -1):
            value = other.above_equal(h[j]) - own.below_equal(K - h[j])
            suffix[j] = (value, h[j]) if value > suffix[j + 1][0] else suffix[j + 1]
        for e in own.levels:
            j = max(bisect_left(h, e), bisect_right(h, K - e))
            g, hv = suffix[j]
            value = own.above_equal(e) - other.below_equal(K - e) + g
            if value > best:
                best, choice = value, (r, e, hv)
    independent = set()
    if choice is not None:
        r, e, h = choice
        independent = {a.key for a in atoms if
            (a.partition == r and a.energy_eV >= e) or
            (a.partition != r and h is not None and a.energy_eV >= h)}
    minima = {}
    for a in atoms:
        if a.key in independent:
            minima[a.partition] = min(minima.get(a.partition, a.energy_eV), a.energy_eV)
    neighbors = {a.key for a in atoms if any(
        r != a.partition and v + a.energy_eV <= K for r, v in minima.items())}
    dual = tuple((a.key, F(0) if a.key in independent else
        F(1) if a.key in neighbors else F(1, 2)) for a in atoms)
    result = Bound(digest(atoms), K, total, best, (total - best) / 2,
        tuple(sorted(independent)), tuple(sorted(neighbors)), dual,
        choice[0] if choice else None, choice[1] if choice else None,
        choice[2] if choice else None)
    verify_bound(atoms, result)
    return result


def verify_bound(atoms, bound):
    """Check every edge by partition/dual-group minima; no threshold sweep."""
    atoms = cross_flow.validate_atoms(atoms)
    require(type(bound) is Bound, "BOUND_RECORD_REQUIRED")
    K = exact(bound.K_eV)
    require(K >= 0 and bound.atom_digest == digest(atoms), "BOUND_INPUT_IDENTITY")
    for x in (bound.total, bound.deficit, bound.cmax):
        exact(x)
    require(type(bound.dual) is tuple and len(bound.dual) == len(atoms), "DUAL_LENGTH")
    y = dict(bound.dual)
    require(len(y) == len(atoms) and set(y) == {a.key for a in atoms}, "DUAL_KEYS")
    groups = {}
    for a in atoms:
        v = exact(y[a.key])
        require(v in (F(0), F(1, 2), F(1)), "DUAL_DOMAIN")
        key = (a.partition, v)
        groups[key] = min(groups.get(key, a.energy_eV), a.energy_eV)
    groups = list(groups.items())
    for ((r, u), er) in groups:
        for ((s, v), es) in groups:
            if r != s and u + v < 1:
                require(er + es > K, "DUAL_EDGE_INFEASIBLE")
    I = {key for key, v in bound.dual if v == 0}
    minI = {}
    for a in atoms:
        if a.key in I:
            minI[a.partition] = min(minI.get(a.partition, a.energy_eV), a.energy_eV)
    J = {a.key for a in atoms if any(
        r != a.partition and e + a.energy_eV <= K for r, e in minI.items())}
    require(set(bound.independent) == I and set(bound.neighbors) == J and not I & J,
        "INDEPENDENT_NEIGHBOR_IDENTITY")
    require(all(y[a.key] == (1 if a.key in J else 0 if a.key in I else F(1, 2))
        for a in atoms), "DUAL_CANONICAL_LABELS")
    N = sum((a.coefficient for a in atoms), F(0))
    delta = sum((a.coefficient for a in atoms if a.key in I), F(0)) - sum(
        (a.coefficient for a in atoms if a.key in J), F(0))
    objective = sum((a.coefficient * y[a.key] for a in atoms), F(0))
    require(N == bound.total and delta == bound.deficit and delta >= 0,
        "DEFICIT_VALUE")
    require(objective == bound.cmax == (N - delta) / 2, "DUAL_OBJECTIVE")
    if I:
        r, e, h = bound.partition, bound.e_threshold, bound.h_threshold
        require(type(r) is int and r >= 0, "THRESHOLD_PARTITION")
        e = exact(e)
        require(any(a.partition == r and a.energy_eV == e for a in atoms), "THRESHOLD_E_LEVEL")
        if h is not None:
            h = exact(h)
            require(h >= e and h > K-e and any(
                a.partition != r and a.energy_eV == h for a in atoms), "THRESHOLD_H_LEVEL")
        expected = {a.key for a in atoms if
            (a.partition == r and a.energy_eV >= e) or
            (a.partition != r and h is not None and a.energy_eV >= h)}
        require(I == expected, "THRESHOLD_SET_MISMATCH")
    else:
        require(bound.partition is None and bound.e_threshold is None and
            bound.h_threshold is None, "EMPTY_THRESHOLD_METADATA")
    return {"status": "PASS_UPPER_CERTIFICATE", "dual_objective": objective,
            "all_allowed_edges_checked": True}


def verify_primal(atoms, bound, solution):
    atoms = cross_flow.validate_atoms(atoms)
    verify_bound(atoms, bound)
    bykey = {a.key: a for a in atoms}
    used = {a.key: F(0) for a in atoms}
    seen = set()
    C = F(0)
    for event in solution.pairs:
        require(type(event.electrons) is tuple and len(event.electrons) == 2,
            "PAIR_ARITY")
        x = exact(event.coefficient)
        require(x > 0, "PAIR_NONPOSITIVE")
        i, j = event.electrons
        require(i in bykey and j in bykey and i != j, "PAIR_KEYS")
        edge = tuple(sorted((i, j)))
        require(edge not in seen, "DUPLICATE_PAIR")
        seen.add(edge)
        ai, aj = bykey[i], bykey[j]
        require(ai.partition != aj.partition and ai.energy_eV + aj.energy_eV <= bound.K_eV,
            "PAIR_SUPPORT")
        used[i] += x
        used[j] += x
        C += x
    single_seen = set()
    for event in solution.singles:
        require(type(event.electrons) is tuple and len(event.electrons) == 1,
            "SINGLE_ARITY")
        key = event.electrons[0]
        require(key in bykey and key not in single_seen, "SINGLE_KEYS")
        x = exact(event.coefficient)
        require(x > 0, "SINGLE_NONPOSITIVE")
        single_seen.add(key)
        used[key] += x
    require(all(used[a.key] == a.coefficient for a in atoms), "EXACT_MARGINAL")
    require(C == bound.cmax == solution.cross_C, "PRIMAL_DUAL_GAP")
    if solution.flow_value is None:
        require(type(solution) is ConstructedWitness and
            solution.method == "PR112_HALF_SHIFT_FILTERED_CROSS" and
            solution.mincut_capacity is None and solution.mincut_dual is None,
            "DIRECT_WITNESS_METHOD")
        return {"status": "PASS_EXACT_OPTIMUM", "atoms_checked": len(atoms),
            "pairs_checked": len(solution.pairs), "singles_checked": len(solution.singles),
            "primal_dual_gap": F(0), "max_marginal_residual": F(0),
            "flow_min_cut": "NOT_PROVIDED_DIRECT_PRIMAL_CERTIFICATE"}
    require(solution.flow_value == solution.mincut_capacity == 2 * C, "FLOW_CUT_GAP")
    # Validate the additional flow-cut dual as an independent exposed certificate.
    require(len(solution.mincut_dual) == len(atoms), "CUT_DUAL_LENGTH")
    z = dict(solution.mincut_dual)
    require(len(z) == len(atoms) and set(z) == set(bykey), "CUT_DUAL_KEYS")
    minima = {}
    for a in atoms:
        v = exact(z[a.key])
        require(v in (F(0), F(1, 2), F(1)), "CUT_DUAL_DOMAIN")
        group = (a.partition, v)
        minima[group] = min(minima.get(group, a.energy_eV), a.energy_eV)
    for (r, u), er in minima.items():
        for (s, v), es in minima.items():
            if r != s and u+v < 1:
                require(er+es > bound.K_eV, "CUT_DUAL_INFEASIBLE")
    require(sum((a.coefficient*z[a.key] for a in atoms), F(0)) == C, "CUT_DUAL_OBJECTIVE")
    return {"status": "PASS_EXACT_OPTIMUM", "atoms_checked": len(atoms),
        "pairs_checked": len(solution.pairs), "singles_checked": len(solution.singles),
        "primal_dual_gap": F(0), "max_marginal_residual": F(0)}


def maximum_cross(atoms, K_eV):
    bound = upper_bound(atoms, K_eV)
    witness = cross_flow.solve(atoms, K_eV)
    verify_primal(atoms, bound, witness)
    return bound, witness


def native_module():
    global _CONSUMER
    if _CONSUMER is None:
        p = Path(__file__).resolve().parents[2] / "cr_he_event_union_20261028/implementation/event_union.py"
        require(hashlib.sha256(p.read_bytes()).hexdigest() == CONSUMER_SHA, "CONSUMER_BYTE_IDENTITY")
        spec = importlib.util.spec_from_file_location("cr_cross_original_consumer", p)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _CONSUMER = module
    return _CONSUMER


def native_atoms(source):
    previous = native_module()
    previous.validate_source(source)
    require(source.provenance_kind == "STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS",
        "ACTUAL_PINNED_SOURCE_REQUIRED")
    return tuple(Atom(a.key, a.energy_eV, a.coefficient, a.partition) for a in source.atoms)


def complete_support_witness(source, bound):
    """Reuse the PR112 half-shift construction only after all-cross support check."""
    atoms = native_atoms(source)
    verify_bound(atoms, bound)
    maxima = {}
    for a in atoms:
        maxima[a.partition] = max(maxima.get(a.partition, a.energy_eV), a.energy_eV)
    require(all(e+f <= bound.K_eV for r,e in maxima.items() for s,f in maxima.items() if r!=s),
        "ALL_CROSS_EDGES_REQUIRED_FOR_HALF_SHIFT")
    previous = native_module()
    original = previous.half_shift_events(source.atoms)
    bykey = {a.key:a for a in atoms}
    combined = {}
    for event in original:
        i,j = event.electrons
        if bykey[i].partition != bykey[j].partition:
            pair = tuple(sorted((i,j)))
            combined[pair] = combined.get(pair,F(0)) + event.coefficient
    used = {a.key:F(0) for a in atoms}
    pairs = []
    for pair,x in sorted(combined.items()):
        pairs.append(cross_flow.Event(pair,x))
        for key in pair:
            used[key] += x
    singles = tuple(cross_flow.Event((a.key,),a.coefficient-used[a.key])
        for a in atoms if a.coefficient>used[a.key])
    result = ConstructedWitness(sum(combined.values(),F(0)),tuple(pairs),singles)
    verify_primal(atoms,bound,result)
    return result


def consume_native(source, bound, witness, window, *, assumption, nb_m3=NB, previous_windows=()):
    require(type(assumption) is str and bool(assumption.strip()), "EXPLICIT_CONDITIONAL_CAP_ASSUMPTION")
    require(exact(nb_m3) == NB, "EXPLICIT_SAME_STATE_NB_REQUIRED")
    atoms = native_atoms(source)
    check = verify_primal(atoms, bound, witness)
    previous = native_module()
    events = tuple(previous.Event(f"energy_cross:{i:05d}", event.electrons, event.coefficient)
        for i, event in enumerate(witness.pairs + witness.singles))
    binding = previous.binding(window, source)
    claims = previous.claims_by_partition(events, source, binding)
    result = previous.consume_event_union(claims, source, nb_m3=nb_m3,
        previous_windows=previous_windows)
    result.update(conditional_K_eV=bound.K_eV, conditional_assumption=assumption,
        cap_binding_digest=digest({"source": source.atom_content_sha256,
            "state": previous.STATE, "K": bound.K_eV, "assumption": assumption,
            "consumer": CONSUMER_SHA, "atom_digest": bound.atom_digest}),
        maximum_cross_coefficient=bound.cmax, certificate=check,
        actual_physical_K=None, actual_C=None, actual_D=None,
        cross_interval_scope="MARGINAL_ENERGY_PARTITION; NATIVE_ENDPOINT_MUST_PASS_OWN_INVENTORY",
        total_double_scope="CROSS_ONLY_ATTAINING_WITNESS_NOT_FIXED_D_PARETO")
    return result
