"""Exact constructive joint (d, C) region in the admitted low-high domain.

The core represents a complete event measure as a dictionary from a
canonical one-key or unordered two-key tuple to a positive Fraction.
Every returned measure includes residual singles and has the original
atom marginals.  Energies/caps and event coefficients are never rounded.

``assemble`` consumes caller-certified scalar optima and saved witnesses;
it does not rerun the old native scalar optimizations.  ``solve`` obtains
fresh exact optima for general fixtures.  Native source attestation and
the original consumer adapter are intentionally separate interfaces.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from fractions import Fraction as F

import cpp_backend as cb


cf = cb.cf
Atom = cf.Atom
Measure = dict[tuple[str, ...], F]
ZERO = F(0)


@dataclass(frozen=True)
class Region:
    atoms: tuple[Atom, ...]
    K: F
    N: F
    L: F
    M: F
    D: F
    X: F
    vertices: dict[str, Measure]
    metadata: dict


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _exact(value, label):
    _require(type(value) in (int, F), label + "_REQUIRES_INT_OR_FRACTION")
    return F(value)


def _nonnegative(value, label):
    result = _exact(value, label)
    _require(result >= 0, label + "_NEGATIVE")
    return result


def _input(atoms, K):
    return cf.validate_atoms(atoms), _nonnegative(K, "K")


def _measure(measure):
    """Copy/normalize a public measure, enforcing its canonical key contract."""
    _require(type(measure) is dict, "MEASURE_DICTIONARY_REQUIRED")
    out = {}
    for legs, coefficient in measure.items():
        _require(type(legs) is tuple and len(legs) in (1, 2)
                 and all(type(key) is str and bool(key) for key in legs),
                 "MEASURE_KEY_REQUIRES_ONE_OR_TWO_STRING_KEYS")
        _require(len(legs) == 1 or legs[0] <= legs[1],
                 "MEASURE_PAIR_MUST_BE_CANONICAL_UNORDERED")
        weight = _nonnegative(coefficient, "MEASURE_COEFFICIENT")
        _require(weight > 0, "MEASURE_ZERO_RECORD_MUST_BE_OMITTED")
        out[legs] = weight
    return dict(sorted(out.items()))


def _record_measure(events):
    """Canonicalize the known predecessor Event records, merging pairs."""
    result = {}
    for event in events:
        legs = tuple(sorted(event.electrons))
        amount = _nonnegative(event.coefficient, "EVENT_COEFFICIENT")
        _require(amount > 0, "EVENT_COEFFICIENT_MUST_BE_POSITIVE")
        result[legs] = result.get(legs, ZERO) + amount
    return _measure(result)


def domain_report(atoms, K):
    """Check the exact domain in O(n) comparisons after atom validation.

    Zero-mass endpoints are ignored only for the same-bin HL predicate.
    ``forbidden_pair`` is (low_key, high_key), with its actual energy sum.
    Invalid scalar/atom data raises ValueError; a well-formed graph outside
    the theorem domain returns ``valid=False`` and a concrete pair.
    """
    data, cap = _input(atoms, K)
    total = sum((atom.coefficient for atom in data), ZERO)
    low_mass = ZERO
    minima = {}
    positive_low = positive_high = 0
    for atom in data:
        low = 2 * atom.energy_eV <= cap
        if low:
            low_mass += atom.coefficient
        if not atom.coefficient:
            continue
        positive_low += int(low)
        positive_high += int(not low)
        group = (atom.partition, low)
        old = minima.get(group)
        if old is None or (atom.energy_eV, atom.key) < (old.energy_eV, old.key):
            minima[group] = atom
    report = {
        "valid": True, "K": cap, "N": total, "L": low_mass,
        "H": total - low_mass, "atom_count": len(data),
        "positive_low_atoms": positive_low, "positive_high_atoms": positive_high,
        "forbidden_pair": None, "forbidden_partition": None,
        "forbidden_pair_energy_eV": None,
    }
    for (partition, is_low), low in minima.items():
        if not is_low:
            continue
        high = minima.get((partition, False))
        if high is not None and low.energy_eV + high.energy_eV <= cap:
            report.update(valid=False, forbidden_pair=(low.key, high.key),
                          forbidden_partition=partition,
                          forbidden_pair_energy_eV=low.energy_eV + high.energy_eV)
            break
    return report


def _admitted(report):
    if not report["valid"]:
        low, high = report["forbidden_pair"]
        raise ValueError("JOINT_DOMAIN_HAS_ALLOWED_SAME_BIN_HL:" + low + ":" + high)


def metrics(atoms, K, measure):
    """Direct exact support/marginal verification for a complete measure.

    This verifier is valid even outside the specialized joint theorem's
    domain.  Only ``assemble``/``solve`` make that additional region claim.
    Repeated diagonal keys are counted as two legs.  The returned counters
    are event coefficients, before any proper-time or baryon factor.
    """
    data, cap = _input(atoms, K)
    events = _measure(measure)
    bykey = {atom.key: atom for atom in data}
    used = {atom.key: ZERO for atom in data}
    low = {atom.key for atom in data if 2 * atom.energy_eV <= cap}
    N = sum((atom.coefficient for atom in data), ZERO)
    L = sum((atom.coefficient for atom in data if atom.key in low), ZERO)
    d = C = s = HL = LL = HH = low_used = high_used = ZERO
    low_singles = high_singles = ZERO
    pair_records = single_records = 0
    for legs, weight in events.items():
        _require(all(key in bykey for key in legs), "MEASURE_UNKNOWN_ATOM_KEY")
        for key in legs:
            used[key] += weight
        if len(legs) == 1:
            s += weight
            single_records += 1
            if legs[0] in low:
                low_singles += weight
            else:
                high_singles += weight
            continue
        left, right = (bykey[key] for key in legs)
        _require(left.energy_eV + right.energy_eV <= cap,
                 "MEASURE_PAIR_ENERGY_SUPPORT_VIOLATION")
        d += weight
        pair_records += 1
        if left.partition != right.partition:
            C += weight
        low_legs = int(left.key in low) + int(right.key in low)
        low_used += low_legs * weight
        high_used += (2 - low_legs) * weight
        if low_legs == 2:
            LL += weight
        elif low_legs == 1:
            HL += weight
        else:
            HH += weight
    for atom in data:
        _require(used[atom.key] == atom.coefficient,
                 "MEASURE_ATOM_MARGINAL_MISMATCH:" + atom.key)
    _require(s + 2 * d == N and HL + LL + HH == d,
             "MEASURE_EVENT_COUNT_IDENTITY")
    _require(HH == 0 and low_used == HL + 2 * LL and high_used == HL,
             "MEASURE_LOW_HIGH_LEG_IDENTITY")
    _require(low_used + low_singles == L
             and high_used + high_singles == N - L,
             "MEASURE_LOW_HIGH_MARGINAL_IDENTITY")
    return {
        "status": "PASS_EXACT_MEASURE", "N": N, "L": L, "H": N - L,
        "d": d, "C": C, "s": s, "HL": HL, "LL": LL, "HH": HH,
        "low_used": low_used, "high_used": high_used,
        "low_singles": low_singles, "high_singles": high_singles,
        "parents": s + d, "atom_count": len(data), "event_records": len(events),
        "pair_records": pair_records, "single_records": single_records,
        "marginal_residual": ZERO, "max_marginal_residual": ZERO,
    }


def _all_singles(data):
    return dict(sorted(((atom.key,), atom.coefficient)
                       for atom in data if atom.coefficient))


def _all_low_diagonals(data, cap):
    return dict(sorted(
        ((atom.key, atom.key), atom.coefficient / 2)
        if 2 * atom.energy_eV <= cap else ((atom.key,), atom.coefficient)
        for atom in data if atom.coefficient))


def _cross_only(data, measure):
    bykey = {atom.key: atom for atom in data}
    used = {atom.key: ZERO for atom in data}
    result = {}
    for legs, weight in measure.items():
        if len(legs) == 2 and bykey[legs[0]].partition != bykey[legs[1]].partition:
            result[legs] = weight
            for key in legs:
                used[key] += weight
    for atom in data:
        remainder = atom.coefficient - used[atom.key]
        _require(remainder >= 0, "CROSS_EXTRACTION_MARGINAL_OVERRUN")
        if remainder:
            result[(atom.key,)] = remainder
    return dict(sorted(result.items()))


def _add(measure, legs, change):
    value = measure.get(legs, ZERO) + change
    _require(value >= 0, "EVENT_UPDATE_NEGATIVE_COEFFICIENT")
    if value:
        measure[legs] = value
    else:
        measure.pop(legs, None)


def _fill_low_diagonals(data, cap, cross_measure):
    result = dict(cross_measure)
    for atom in data:
        if 2 * atom.energy_eV <= cap:
            remainder = result.pop((atom.key,), ZERO)
            if remainder:
                _add(result, (atom.key, atom.key), remainder / 2)
    return dict(sorted(result.items()))


def _cross_metrics(data, cap, measure, X):
    result = metrics(data, cap, measure)
    _require(result["d"] == result["C"] == X,
             "CROSS_WITNESS_MUST_ATTAIN_CERTIFIED_X_WITH_CROSS_PAIRS_ONLY")
    return result


def _repair_high_low(data, cap, cross_measure, M, X):
    """Lemma 3's finite rational residual-path construction.

    This general path materializes permitted positive HL adjacency.  The
    native equality branches in assemble avoid this potentially quadratic
    structure.  Each step preserves C exactly and strictly increases HL.
    """
    result = dict(cross_measure)
    first = _cross_metrics(data, cap, result, X)
    current = first["HL"]
    _require(current <= M, "CROSS_WITNESS_HL_EXCEEDS_CERTIFIED_M")
    N = first["N"]
    low = {atom.key: atom for atom in data if atom.coefficient and 2 * atom.energy_eV <= cap}
    high = {atom.key: atom for atom in data if atom.coefficient and 2 * atom.energy_eV > cap}
    low_keys, high_keys = tuple(sorted(low)), tuple(sorted(high))
    neighbors = {h: tuple(l for l in low_keys if high[h].energy_eV + low[l].energy_eV <= cap)
                 for h in high_keys}
    flow = {}
    low_low_edges = []
    for legs, weight in result.items():
        if len(legs) != 2:
            continue
        left, right = legs
        if left in high:
            flow[(left, right)] = weight
        elif right in high:
            flow[(right, left)] = weight
        else:
            low_low_edges.append(legs)
    low_low_edges.sort()
    iterations = maximum_path = 0
    while current < M:
        high_used = dict.fromkeys(high, ZERO)
        low_hl_used = dict.fromkeys(low, ZERO)
        reverse = {key: [] for key in low}
        for (h, l), weight in sorted(flow.items()):
            high_used[h] += weight
            low_hl_used[l] += weight
            reverse[l].append(h)
        parent = {}
        queue = deque()
        for h in high_keys:
            if high_used[h] < high[h].coefficient:
                parent[h] = None
                queue.append(h)
        endpoint = None
        while queue and endpoint is None:
            vertex = queue.popleft()
            if vertex in high:
                for l in neighbors[vertex]:
                    if l not in parent and flow.get((vertex, l), ZERO) < N:
                        parent[l] = (vertex, 1)
                        queue.append(l)
            else:
                if low_hl_used[vertex] < low[vertex].coefficient:
                    endpoint = vertex
                    break
                for h in reverse[vertex]:
                    if h not in parent:
                        parent[h] = (vertex, -1)
                        queue.append(h)
        _require(endpoint is not None,
                 "CERTIFIED_HL_MAXIMUM_HAS_NO_REQUIRED_AUGMENTING_PATH")

        path = []
        vertex = endpoint
        while parent[vertex] is not None:
            previous, direction = parent[vertex]
            if direction == 1:
                path.append((previous, vertex, 1))
            else:
                path.append((vertex, previous, -1))
            vertex = previous
        start = vertex
        _require(start in high and bool(path), "HL_RESIDUAL_PATH_TERMINALS")
        if result.get((endpoint,), ZERO) > 0:
            raise ValueError("CERTIFIED_CROSS_OPTIMUM_HAS_SINGLE_ENDING_AUGMENTING_PATH")
        removed = next((edge for edge in low_low_edges
                        if endpoint in edge and result.get(edge, ZERO) > 0), None)
        _require(removed is not None, "HL_ENDPOINT_HAS_NO_LOW_LOW_CROSS_MASS")
        other = removed[1] if removed[0] == endpoint else removed[0]
        _require(other != endpoint and other in low, "HL_REMOVED_EDGE_NOT_LOW_LOW_CROSS")
        available = [M - current, high[start].coefficient - high_used[start],
                     low[endpoint].coefficient - low_hl_used[endpoint], result[removed]]
        available.extend(N - flow.get((h, l), ZERO) if direction == 1 else flow[(h, l)]
                         for h, l, direction in path)
        epsilon = min(available)
        _require(epsilon > 0 and result.get((start,), ZERO) >= epsilon,
                 "HL_RESIDUAL_PATH_HAS_NO_POSITIVE_INCREMENT")
        old_current = current
        for h, l, direction in path:
            amount = flow.get((h, l), ZERO) + direction * epsilon
            _require(amount >= 0, "HL_REVERSE_EDGE_OVERDRAW")
            if amount:
                flow[(h, l)] = amount
            else:
                flow.pop((h, l), None)
            _add(result, tuple(sorted((h, l))), direction * epsilon)
        _add(result, removed, -epsilon)
        _add(result, (start,), -epsilon)
        _add(result, (other,), epsilon)
        current += epsilon
        iterations += 1
        maximum_path = max(maximum_path, len(path))
        checked = _cross_metrics(data, cap, result, X)
        _require(checked["HL"] == current and old_current < current <= M,
                 "HL_AUGMENTATION_DID_NOT_PRESERVE_OBJECTIVE_AND_PROGRESS")
    return dict(sorted(result.items())), {
        "residual_augmentations": iterations, "maximum_residual_path_edges": maximum_path,
        "initial_HL": str(first["HL"]), "final_HL": str(current),
    }


def _scalar_contract(N, L, D, X):
    M = 2 * D - L
    _require(0 <= M <= X <= D <= L and M <= N - L and D <= N / 2,
             "CERTIFIED_SCALARS_INCONSISTENT_WITH_LOW_HIGH_MASSES")
    return M


def assemble(atoms, K, D, X, B_events, G_events=None, cpp_executable=None):
    """Assemble all five complete vertex witnesses from certified optima.

    D/X must be independently certified for these exact atoms and K.  The
    native caller checks the saved input hashes and certificate bindings.
    B_events is a complete measure at (D,M), with HL=M.  G_events, when
    supplied, is a complete cross-only optimum at (X,X).  Missing G is
    constructed only in branches which need it.  No scalar optimizer is
    called by this function.
    """
    data, cap = _input(atoms, K)
    domain = domain_report(data, cap)
    _admitted(domain)
    D, X = _nonnegative(D, "D"), _nonnegative(X, "X")
    N, L = domain["N"], domain["L"]
    M = _scalar_contract(N, L, D, X)
    B = _measure(B_events)
    b_check = metrics(data, cap, B)
    _require(b_check["d"] == D and b_check["C"] == b_check["HL"] == M
             and b_check["low_used"] == L, "B_WITNESS_COORDINATE_OR_HL_MISMATCH")
    supplied_G = None
    if G_events is not None:
        supplied_G = _measure(G_events)
        check = _cross_metrics(data, cap, supplied_G, X)
        _require(check["HL"] <= M, "SUPPLIED_G_HL_EXCEEDS_CERTIFIED_M")
    O = _all_singles(data)
    A = _all_low_diagonals(data, cap)
    metadata = {
        "optima_source": "CALLER_CERTIFIED_EXACT_D_AND_X",
        "domain_positive_atoms": domain["positive_low_atoms"] + domain["positive_high_atoms"],
        "cross_primal_computed": False, "supplied_G_present": supplied_G is not None,
        "supplied_G_used": False, "residual_augmentations": 0,
        "maximum_residual_path_edges": 0,
    }
    if X == 0:
        # The scalar contract implies M=0 and D=L/2, including N=0.
        F_measure, G = dict(B), dict(O)
        metadata.update(method="ZERO_CROSS", cross_primal_source="ALL_SINGLES")
    elif X == M:
        F_measure = dict(B)
        G = _cross_only(data, B)
        metadata.update(method="X_EQUALS_M", cross_primal_source="SAVED_OR_CERTIFIED_B")
    else:
        if supplied_G is None:
            solution = (cf.solve(data, cap) if cpp_executable is None
                        else cb.solve(data, cap, cpp_executable))
            _require(solution.cross_C == X, "NEW_CROSS_PRIMAL_DISAGREES_WITH_CERTIFIED_X")
            G = _record_measure(solution.pairs + solution.singles)
            metadata.update(
                cross_primal_computed=True,
                cross_primal_source="PYTHON_EXACT_FLOW" if cpp_executable is None else "CPP_EXACT_FLOW",
                flow_value=str(solution.flow_value), mincut_capacity=str(solution.mincut_capacity),
                network_nodes=solution.network_nodes, network_edges=solution.network_edges,
                capacity_denominator=str(solution.capacity_denominator),
                dinic_phases=solution.dinic_phases, flow_augmentations=solution.augmentations,
            )
        else:
            G = dict(supplied_G)
            metadata.update(supplied_G_used=True, cross_primal_source="CALLER_SUPPLIED_G")
        g_check = _cross_metrics(data, cap, G, X)
        _require(g_check["HL"] <= M, "G_HL_EXCEEDS_CERTIFIED_M")
        if X == D:
            _require(g_check["HL"] == M and g_check["low_used"] == L,
                     "X_EQUALS_D_DID_NOT_FORCE_MAXIMUM_HL")
            F_measure = dict(G)
            metadata["method"] = "X_EQUALS_D"
        elif M == 0:
            _require(g_check["HL"] == 0, "M_ZERO_WITNESS_HAS_HIGH_LOW_PAIR")
            F_measure = _fill_low_diagonals(data, cap, G)
            metadata["method"] = "M_ZERO"
        else:
            G, repair = _repair_high_low(data, cap, G, M, X)
            F_measure = _fill_low_diagonals(data, cap, G)
            metadata.update(repair)
            metadata["method"] = "RESIDUAL_HL_AUGMENTATION"
    vertices = {"O": O, "A": A, "B": B, "F": F_measure, "G": G}
    coordinates = {"O": (ZERO, ZERO), "A": (L / 2, ZERO), "B": (D, M),
                   "F": (D, X), "G": (X, X)}
    for label, measure in vertices.items():
        check = metrics(data, cap, measure)
        _require((check["d"], check["C"]) == coordinates[label],
                 "VERTEX_COORDINATE_MISMATCH:" + label)
        if label in ("B", "F", "G"):
            _require(check["HL"] == M, "VERTEX_HL_MISMATCH:" + label)
    metadata["vertex_event_counts"] = {label: len(value) for label, value in vertices.items()}
    return Region(data, cap, N, L, M, D, X,
                  {label: dict(sorted(value.items())) for label, value in vertices.items()}, metadata)


def solve(atoms, K, cpp_executable=None):
    """Fresh general-fixture optima, exact certificates, and complete region.

    The old pure total-double solver is used only here.  The cross upper
    certificate is matched to the constructed G primal.  Native callers
    use assemble with hash-verified saved optima instead.
    """
    data, cap = _input(atoms, K)
    _admitted(domain_report(data, cap))
    energy = cb.load_pinned_module(
        "energy_sum", "cr_he_energy_sum_20261028/implementation/energy_sum.py",
        "6cacfa7ba046ea21740beb91b9fd20797f8c06fa43ea525f0c9a555e933d981a")
    envelope = cb.load_pinned_module(
        "cross_envelope", "cr_he_energy_cross_20261028/implementation/cross_envelope.py",
        "653a3011bbcf6af115c4f55ebb4035a46020d72c3e8e5d43fcb3f95fd4e028d3")
    total_atoms = tuple(energy.Atom(atom.key, atom.energy_eV, atom.coefficient, atom.partition)
                        for atom in data)
    total_solution = energy.solve(total_atoms, cap)
    total_check = energy.verify(total_atoms, total_solution)
    bound = envelope.upper_bound(data, cap)
    region = assemble(data, cap, total_solution.dmax, bound.cmax,
                      _record_measure(total_solution.max_events),
                      cpp_executable=cpp_executable)
    metadata = dict(region.metadata)
    metadata.update(optima_source="FRESH_GENERAL_EXACT_PRIMAL_DUAL",
                    total_dual_objective=str(total_check["dual_objective"]),
                    cross_dual_objective=str(bound.cmax), primal_dual_gap="0")
    return replace(region, metadata=metadata)


def _blend(left, right, weight):
    """weight*left + (1-weight)*right, including every singleton."""
    _require(ZERO <= weight <= 1, "CONVEX_WEIGHT_OUTSIDE_UNIT_INTERVAL")
    if weight == 0:
        return dict(right)
    if weight == 1:
        return dict(left)
    result = {}
    for measure, factor in ((left, weight), (right, 1 - weight)):
        for legs, value in measure.items():
            amount = factor * value
            if amount:
                result[legs] = result.get(legs, ZERO) + amount
    return dict(sorted(result.items()))


def mix_at(region, d, C):
    """Construct the complete measure at any rational feasible (d,C)."""
    _require(type(region) is Region, "REGION_RECORD_REQUIRED")
    _admitted(domain_report(region.atoms, region.K))
    d, C = _nonnegative(d, "TARGET_D"), _nonnegative(C, "TARGET_C")
    N, L, M, D, X = (_nonnegative(value, label) for value, label in (
        (region.N, "REGION_N"), (region.L, "REGION_L"), (region.M, "REGION_M"),
        (region.D, "REGION_D"), (region.X, "REGION_X")))
    _require(_scalar_contract(N, L, D, X) == M, "REGION_M_IDENTITY")
    _require(d <= D and C <= X and C <= d and 2 * d - C <= L,
             "TARGET_OUTSIDE_EXACT_JOINT_REGION")
    vertices = region.vertices
    _require(type(vertices) is dict and set(vertices) == {"O", "A", "B", "F", "G"},
             "REGION_VERTEX_SET_REQUIRED")
    coordinates = {"O": (ZERO, ZERO), "A": (L / 2, ZERO), "B": (D, M),
                   "F": (D, X), "G": (X, X)}
    result = None
    for label, point in coordinates.items():
        if point == (d, C):
            result = dict(vertices[label])
            break
    if result is None and X == 0:
        # D=0 was already the O coordinate above; never divide by zero.
        _require(D > 0 and C == 0, "ZERO_CROSS_DEGENERACY")
        result = _blend(vertices["A"], vertices["O"], d / D)
    elif result is None:
        Q = _blend(vertices["G"], vertices["O"], C / X)
        upper_d = min(D, (L + C) / 2)
        if M > 0 and C <= M:
            U = _blend(vertices["B"], vertices["A"], C / M)
        elif M == 0:
            U = _blend(vertices["F"], vertices["A"], C / X)
        else:
            _require(X > M and C > M, "UPPER_BOUND_INTERPOLATION_BRANCH")
            U = _blend(vertices["F"], vertices["B"], (C - M) / (X - M))
        if upper_d == C:
            result = Q
        else:
            _require(upper_d > C, "UPPER_AND_LOWER_BOUND_ORDER")
            result = _blend(U, Q, (d - C) / (upper_d - C))
    result = _measure(result)
    check = metrics(region.atoms, region.K, result)
    _require(check["N"] == N and check["L"] == L
             and check["d"] == d and check["C"] == C,
             "MIXED_MEASURE_TARGET_OR_SOURCE_MISMATCH")
    return result
