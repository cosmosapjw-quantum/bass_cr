"""Independent small-graph exact oracle for cross-bin double-event mass.

Authoring status: authored without importing/executing this module.  Root owns
all bounded execution and acceptance.  This reference imports no production
code and does not use a threshold-tail formula or max-flow implementation.

The oracle explicitly constructs the unordered cross-edge set and enumerates
all half-integral vertex covers.  A second, 2**n enumeration checks the exact
independent-set deficiency identity.  This is intentionally limited to n <= 7.
"""

from fractions import Fraction
from itertools import product


MAX_ATOMS = 7


def _rational(value, name):
    if type(value) is int:
        return Fraction(value)
    if type(value) is Fraction:
        return value
    raise TypeError(name + " must be an int or Fraction, excluding bool")


def _data(weights, energies, partitions, cap):
    if not all(type(v) in (tuple, list) for v in (weights, energies, partitions)):
        raise TypeError("weights, energies and partitions must be tuples/lists")
    n = len(weights)
    if n != len(energies) or n != len(partitions):
        raise ValueError("parallel lengths differ")
    if n > MAX_ATOMS:
        raise ValueError("small-graph oracle limit is seven atoms")
    w = tuple(_rational(v, "weight") for v in weights)
    e = tuple(_rational(v, "energy") for v in energies)
    k = _rational(cap, "cap")
    if k < 0 or any(v < 0 for v in w + e):
        raise ValueError("weights, energies and cap must be nonnegative")
    if any(type(v) is not int or v < 0 for v in partitions):
        raise TypeError("partitions must be nonnegative ints, excluding bool")
    b = tuple(partitions)
    edges = tuple((i, j) for i in range(n) for j in range(i + 1, n)
                  if b[i] != b[j] and e[i] + e[j] <= k)
    return w, e, b, k, edges


def cross_oracle(weights, energies, partitions, cap):
    """Return the exact optimum by a generic half-integral dual enumeration.

    No supplied production witness, ordering or status is used.  Integer codes
    (0,1,2) represent dual values (0,1/2,1).  Edge feasibility and weighted
    objectives are evaluated exactly.  All candidates, including infeasible
    ones, count in ``dual_candidates_evaluated``.
    """
    w, e, b, k, edges = _data(weights, energies, partitions, cap)
    n = len(w)
    best_twice = None
    best_codes = None
    feasible = 0
    evaluated = 0
    for codes in product((0, 1, 2), repeat=n):
        evaluated += 1
        if any(codes[i] + codes[j] < 2 for i, j in edges):
            continue
        feasible += 1
        value_twice = sum((w[i] * codes[i] for i in range(n)), Fraction(0))
        if best_twice is None or value_twice < best_twice:
            best_twice = value_twice
            best_codes = codes
    # The all-ones cover (and the empty cover for n=0) is always feasible.
    if best_twice is None:
        raise AssertionError("half-integral feasible set unexpectedly empty")

    # This second enumeration uses a different exact representation: an
    # independent set I, its full open neighborhood, and w(I)-w(N(I)).
    best_deficit = Fraction(0)
    best_set = ()
    best_neighbors = ()
    independent_count = 0
    for mask in range(1 << n):
        if any((mask >> i) & 1 and (mask >> j) & 1 for i, j in edges):
            continue
        independent_count += 1
        selected = tuple(i for i in range(n) if (mask >> i) & 1)
        neighbors = set()
        for i, j in edges:
            if (mask >> i) & 1:
                neighbors.add(j)
            if (mask >> j) & 1:
                neighbors.add(i)
        delta = (sum((w[i] for i in selected), Fraction(0))
                 - sum((w[i] for i in neighbors), Fraction(0)))
        if delta > best_deficit:
            best_deficit = delta
            best_set = selected
            best_neighbors = tuple(sorted(neighbors))
    total = sum(w, Fraction(0))
    optimum = best_twice / 2
    if optimum != (total - best_deficit) / 2:
        raise AssertionError("independent exact dual/deficiency disagreement")
    return {
        "cmax": optimum,
        "dual": tuple(Fraction(v, 2) for v in best_codes),
        "edges": edges,
        "total_mass": total,
        "deficit": best_deficit,
        "independent_set": best_set,
        "independent_neighbors": best_neighbors,
        "dual_candidates_evaluated": evaluated,
        "dual_feasible_candidates": feasible,
        "independent_sets_evaluated": independent_count,
        "production_imports": 0,
        "algorithm": "ALL_HALF_INTEGRAL_DUALS_PLUS_ALL_INDEPENDENT_SETS",
    }


def check_certificate(weights, energies, partitions, cap,
                      pair_masses, dual, claimed_cmax):
    """Check an explicit small-instance primal/dual certificate exactly.

    ``pair_masses`` contains (i,j,mass), with i<j.  Duplicate edge entries,
    zero-mass records, forbidden edges and diagonals are rejected.  Residual
    singles are implicit as w minus incidence.  A valid certificate requires
    exact equality of both objectives and the independently enumerated optimum.
    """
    w, e, b, k, edges = _data(weights, energies, partitions, cap)
    n = len(w)
    if type(pair_masses) not in (tuple, list) or type(dual) not in (tuple, list):
        raise TypeError("certificate arrays must be tuples/lists")
    if len(dual) != n:
        raise ValueError("dual dimension mismatch")
    y = tuple(_rational(v, "dual") for v in dual)
    c = _rational(claimed_cmax, "claimed optimum")
    if c < 0 or any(v < 0 for v in y):
        raise ValueError("negative certificate scalar")
    if any(y[i] + y[j] < 1 for i, j in edges):
        raise ValueError("dual infeasible on a permitted cross edge")
    used = [Fraction(0) for _ in w]
    seen = set()
    edge_set = set(edges)
    objective = Fraction(0)
    for record in pair_masses:
        if type(record) not in (tuple, list) or len(record) != 3:
            raise ValueError("a pair record must contain i,j,mass")
        i, j, raw = record
        if type(i) is not int or type(j) is not int or not (0 <= i < j < n):
            raise ValueError("pair endpoints must be distinct ordered indices")
        edge = (i, j)
        if edge in seen or edge not in edge_set:
            raise ValueError("duplicate or forbidden pair")
        seen.add(edge)
        mass = _rational(raw, "pair mass")
        if mass <= 0:
            raise ValueError("pair mass must be positive")
        used[i] += mass
        used[j] += mass
        objective += mass
    if any(a > z for a, z in zip(used, w)):
        raise ValueError("primal atom capacity exceeded")
    dual_objective = sum((wi * yi for wi, yi in zip(w, y)), Fraction(0))
    oracle = cross_oracle(w, e, b, k)
    if not (objective == dual_objective == c == oracle["cmax"]):
        raise ValueError("exact primal/dual/oracle objective mismatch")
    return {
        "status": "PASS_EXACT_SMALL_GRAPH_CERTIFICATE",
        "cmax": c,
        "singles": tuple(z - a for a, z in zip(used, w)),
        "primal_dual_gap": Fraction(0),
        "oracle_gap": Fraction(0),
        "permitted_edges_checked": len(edges),
        "explicit_pairs_checked": len(pair_masses),
    }


def named_cases():
    """Authored diagnostic fixtures; expected optima derived in the report.

    Calling this function only constructs input data; it does not run the
    reference solver.  It has not been called by the reference author.
    """
    q = Fraction
    raw = (
        ("empty", (), (), (), 0, 0),
        ("one_atom_loop_does_not_count", (5,), (1,), (0,), 2, 0),
        ("same_bin_only", (2, 3), (1, 2), (0, 0), 3, 0),
        ("closed_energy_boundary", (2, 5), (1, 2), (0, 1), 3, 2),
        ("strictly_below_boundary", (2, 5), (1, 2), (0, 1), q(299, 100), 0),
        ("fractional_triangle", (1, 1, 1), (0, 0, 0), (0, 1, 2), 0, q(3, 2)),
        ("dominant_triangle", (5, 1, 1), (0, 0, 0), (0, 1, 2), 0, 2),
        ("energy_star", (1, 2, 2), (0, 1, 2), (0, 1, 2), 2, 1),
        ("isolated_heavy_high", (1, 1, 100), (0, 0, 100), (0, 1, 2), 0, 1),
        ("zero_capacity_bridge", (2, 0, 2), (0, 0, 0), (0, 1, 0), 0, 0),
        ("all_zero_weights", (0, 0, 0), (0, 0, 0), (0, 1, 2), 0, 0),
        ("rational_triangle", (q(1, 3), q(1, 2), q(2, 3)),
         (0, 0, 0), (0, 1, 2), 0, q(3, 4)),
        ("complete_four_bins", (1, 1, 1, 1), (0, 0, 0, 0), (0, 1, 2, 3), 0, 2),
        ("two_bins_energy_restriction", (1, 3, 1, 3),
         (0, 4, 0, 4), (0, 0, 1, 1), 4, 2),
        ("partition_and_energy_intersection", (1, 1, 1),
         (0, 2, 2), (0, 0, 1), 2, 1),
        ("all_high_isolated", (2, 3), (2, 3), (0, 1), 1, 0),
        ("equal_energy_triangle_boundary", (1, 2, 2),
         (1, 1, 1), (0, 1, 2), 2, q(5, 2)),
        ("rational_capacity_scaling", (q(2, 7), q(5, 7)),
         (1, 2), (0, 1), 3, q(2, 7)),
        ("noncontiguous_partition_labels", (3, 4, 1),
         (0, 0, 0), (2, 100, 500), 0, 4),
        ("two_disjoint_energy_components_with_zero", (0, 1, 1, 3),
         (0, 0, 0, 100), (0, 1, 2, 3), 0, 1),
    )
    return tuple({"id": name, "weights": tuple(q(v) for v in w),
                  "energies": tuple(q(v) for v in e), "partitions": b,
                  "cap": q(k), "expected_cmax": q(expected)}
                 for name, w, e, b, k, expected in raw)

