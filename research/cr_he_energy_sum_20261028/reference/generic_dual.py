"""Independent exact reference for CR_PHYS02_HE_ENERGY_SUM_V1.

Authored without reading/importing production energy_sum.py.  No scientific
execution was performed by the reference author.  The measured C6/C7 runner
owns all actual executions and result records.

The small oracle builds every allowed unordered pair, including loops, from
the explicit energies.  It minimizes the fractional vertex-cover dual by
enumerating labels z in {0,1,2}^n, representing y=z/2.  No high/low split,
tail-deficit formula, matching sweep, production helper, NumPy, or CAS is used.

The certificate evaluator consumes plain explicit records.  For large inputs
it verifies the SAME full dual graph by independent sorted-prefix minima;
it does not infer or assume the production dual's threshold form.
"""

from bisect import bisect_right
from collections.abc import Mapping
from fractions import Fraction
from itertools import product
from math import lcm


REFERENCE_ID = "CR_HE_ENERGY_SUM_GENERIC_DUAL_REFERENCE_V1"
AUTHORING_STATE = "NOT_EXECUTED_BY_AUTHOR"
MAX_ORACLE_ATOMS = 7
MAX_CERTIFICATE_ATOMS = 4096
MAX_CERTIFICATE_EVENTS = 2 * MAX_CERTIFICATE_ATOMS
FIXTURE_COUNT = 48


class ReferenceValidationError(ValueError):
    """A specific exact-input or certificate obligation failed."""


def _require(condition, message):
    if not condition:
        raise ReferenceValidationError(message)


def _exact(value):
    """Accept only plain int, str or Fraction; bool/float are not exact inputs."""
    _require(type(value) in (int, str, Fraction), "EXACT_SCALAR_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ReferenceValidationError("FINITE_EXACT_SCALAR_REQUIRED") from exc


def _sequence(value, label):
    _require(type(value) in (tuple, list), label + "_SEQUENCE_REQUIRED")
    return value


def _problem(energies, weights, K, atom_limit):
    _sequence(energies, "ENERGIES")
    _sequence(weights, "WEIGHTS")
    _require(len(energies) == len(weights), "ENERGY_WEIGHT_LENGTH_MISMATCH")
    _require(len(energies) <= atom_limit, "REFERENCE_ATOM_LIMIT_EXCEEDED")
    e = tuple(_exact(x) for x in energies)
    w = tuple(_exact(x) for x in weights)
    cap = _exact(K)
    _require(cap >= 0, "NONNEGATIVE_CAP_REQUIRED")
    _require(all(x >= 0 for x in e), "NONNEGATIVE_ENERGIES_REQUIRED")
    _require(all(x >= 0 for x in w), "NONNEGATIVE_WEIGHTS_REQUIRED")
    return e, w, cap


def _allowed_pairs(energies, cap):
    """The generic full graph, not the theorem's high/low reduction."""
    return tuple(
        (i, j)
        for i in range(len(energies))
        for j in range(i, len(energies))
        if energies[i] + energies[j] <= cap
    )


def dual_oracle(energies, weights, K):
    """Return the exact small-graph optimum and a minimizing explicit dual.

    Inputs are tuple/list exact scalars with n <= MAX_ORACLE_ATOMS.  Empty
    input is permitted and returns zero.  A loop (i,i) is checked as
    z_i+z_i>=2, which is exactly 2*y_i>=1.

    Returned Fractions are intentionally not converted to floats.  The
    caller may serialize each Fraction as str(value).
    """
    energies, weights, cap = _problem(
        energies, weights, K, MAX_ORACLE_ATOMS
    )
    pairs = _allowed_pairs(energies, cap)

    # A common positive denominator makes the objective comparison integer
    # arithmetic.  This is exact scaling, not numerical rounding.
    denominator = 1
    for weight in weights:
        denominator = lcm(denominator, weight.denominator)
    scaled_weights = tuple(
        weight.numerator * (denominator // weight.denominator)
        for weight in weights
    )

    best_numerator = None
    best_labels = None
    visited = feasible = 0
    for labels in product((0, 1, 2), repeat=len(energies)):
        visited += 1
        if any(labels[i] + labels[j] < 2 for i, j in pairs):
            continue
        feasible += 1
        numerator = sum(w * z for w, z in zip(scaled_weights, labels))
        if best_numerator is None or numerator < best_numerator:
            best_numerator = numerator
            best_labels = labels

    _require(best_labels is not None, "INTERNAL_NO_FEASIBLE_DUAL")
    optimum = Fraction(best_numerator, 2 * denominator)
    total = sum(weights, Fraction(0))
    return {
        "reference_id": REFERENCE_ID,
        "method": "EXHAUSTIVE_HALF_INTEGRAL_DUAL_ON_EXPLICIT_FULL_GRAPH",
        "atom_count": len(energies),
        "K": cap,
        "N": total,
        "dmax": optimum,
        "parent_min": total - optimum,
        "dual": tuple(Fraction(z, 2) for z in best_labels),
        "pairs": pairs,
        "loop_count": sum(i == j for i, j in pairs),
        "assignments_examined": visited,
        "feasible_assignments": feasible,
    }


def _field(record, field, label):
    _require(isinstance(record, Mapping), label + "_RECORD_REQUIRED")
    _require(field in record, label + "_MISSING_" + field)
    return record[field]


def _read_atoms(atom_records):
    _sequence(atom_records, "ATOMS")
    _require(
        len(atom_records) <= MAX_CERTIFICATE_ATOMS,
        "CERTIFICATE_ATOM_LIMIT_EXCEEDED",
    )
    keys = []
    energies = []
    weights = []
    partitions = []
    partition_present = []
    seen = set()
    for record in atom_records:
        key = _field(record, "key", "ATOM")
        _require(type(key) is str and bool(key), "NONEMPTY_ATOM_KEY_REQUIRED")
        _require(key not in seen, "DUPLICATE_ATOM_KEY:" + key)
        seen.add(key)
        keys.append(key)
        energies.append(_field(record, "energy_eV", "ATOM"))
        weights.append(_field(record, "coefficient", "ATOM"))
        partition_present.append("partition" in record)
        if "partition" in record:
            p = record["partition"]
            _require(type(p) is int and 0 <= p < 4, "INVALID_ATOM_PARTITION")
            partitions.append(p)
        else:
            partitions.append(None)
    _require(
        not any(partition_present) or all(partition_present),
        "PARTIAL_PARTITION_METADATA",
    )
    return tuple(keys), tuple(energies), tuple(weights), tuple(partitions)


def _check_explicit_dual(energies, dual, cap):
    """Verify every allowed graph constraint, with two independent modes.

    For n<=7, enumerate every unordered pair/loop explicitly.
    Otherwise, sorted energy prefixes describe each vertex's full neighbor
    set.  Checking y_i + min(neighbor y) >= 1 is logically equivalent to
    checking y_i+y_j>=1 for every allowed j.  This includes self-neighbors.
    """
    _require(all(x >= 0 for x in dual), "NEGATIVE_DUAL_COORDINATE")
    if len(energies) <= MAX_ORACLE_ATOMS:
        pairs = _allowed_pairs(energies, cap)
        minimum_slack = None
        for i, j in pairs:
            slack = dual[i] + dual[j] - 1
            _require(slack >= 0, "INFEASIBLE_DUAL_PAIR:" + str((i, j)))
            if minimum_slack is None or slack < minimum_slack:
                minimum_slack = slack
        return {
            "dual_check_method": "EXPLICIT_ALL_UNORDERED_PAIRS_AND_LOOPS",
            "pair_constraints_covered_exactly": len(pairs),
            "constraint_checks": len(pairs),
            "loop_constraints": sum(i == j for i, j in pairs),
            "minimum_pair_slack": minimum_slack,
        }

    order = sorted(range(len(energies)), key=lambda i: (energies[i], i))
    ordered_energies = [energies[i] for i in order]
    prefix_minimum = []
    running_minimum = None
    for i in order:
        if running_minimum is None or dual[i] < running_minimum:
            running_minimum = dual[i]
        prefix_minimum.append(running_minimum)

    ordered_edges = loops = checks = 0
    minimum_slack = None
    for i, energy in enumerate(energies):
        # bisect_right enforces the declared closed inequality at equality.
        count = bisect_right(ordered_energies, cap - energy)
        ordered_edges += count
        loops += int(energy + energy <= cap)
        if count == 0:
            continue
        checks += 1
        slack = dual[i] + prefix_minimum[count - 1] - 1
        _require(slack >= 0, "INFEASIBLE_DUAL_NEIGHBOR_PREFIX:" + str(i))
        if minimum_slack is None or slack < minimum_slack:
            minimum_slack = slack

    _require((ordered_edges + loops) % 2 == 0, "INTERNAL_GRAPH_COUNT_PARITY")
    return {
        "dual_check_method": "ALL_GRAPH_CONSTRAINTS_BY_SORTED_PREFIX_MINIMUM",
        "pair_constraints_covered_exactly": (ordered_edges + loops) // 2,
        "constraint_checks": checks,
        "prefix_queries": len(energies),
        "loop_constraints": loops,
        "minimum_pair_slack": minimum_slack,
    }


def verify_certificate(
    atom_records,
    K,
    event_records,
    dual_by_key,
    *,
    expected_dmax=None,
    target_d=None,
    require_optimal=True,
):
    """Independently evaluate plain saved atoms, events and explicit dual.

    Atom record: {"key": str, "energy_eV": exact, "coefficient": exact}.
    Optional integer "partition" (0..3) must be supplied for every atom if
    supplied for any atom; it enables an independent cross-C evaluation.

    Event record: {"key": str, "electrons": [one or two atom keys],
                   "coefficient": positive exact}.
    A repeated atom key denotes a diagonal and is counted twice.

    dual_by_key must contain exactly the atom keys and nonnegative exact
    values.  require_optimal=True certifies an optimum by exact primal-dual
    equality.  For an intermediate target, use require_optimal=False and
    optionally expected_dmax from a separately certified maximum witness;
    this call then certifies the target witness and its dual upper bound.

    All measures are coefficients.  No proper-time factor, density-to-nb
    normalization, source provenance authentication or physical closure is
    applied by this generic mathematical reference.
    """
    _require(type(require_optimal) is bool, "BOOLEAN_OPTIMALITY_MODE_REQUIRED")
    keys, raw_energies, raw_weights, partitions = _read_atoms(atom_records)
    energies, weights, cap = _problem(
        raw_energies, raw_weights, K, MAX_CERTIFICATE_ATOMS
    )
    _sequence(event_records, "EVENTS")
    _require(
        len(event_records) <= MAX_CERTIFICATE_EVENTS,
        "CERTIFICATE_EVENT_LIMIT_EXCEEDED",
    )
    _require(isinstance(dual_by_key, Mapping), "EXPLICIT_DUAL_MAP_REQUIRED")
    _require(set(dual_by_key) == set(keys), "DUAL_ATOM_KEY_SET_MISMATCH")
    dual = tuple(_exact(dual_by_key[key]) for key in keys)

    index = {key: i for i, key in enumerate(keys)}
    marginal = [Fraction(0) for _ in keys]
    singles = doubles = loops = kinetic = Fraction(0)
    cross = Fraction(0) if keys and partitions[0] is not None else None
    single_records = double_records = loop_records = 0
    event_keys = set()
    for event in event_records:
        event_key = _field(event, "key", "EVENT")
        _require(
            type(event_key) is str and bool(event_key),
            "NONEMPTY_EVENT_KEY_REQUIRED",
        )
        _require(event_key not in event_keys, "DUPLICATE_EVENT_KEY:" + event_key)
        event_keys.add(event_key)
        electrons = _sequence(_field(event, "electrons", "EVENT"), "ELECTRONS")
        _require(len(electrons) in (1, 2), "ONE_OR_TWO_EVENT_LEGS_REQUIRED")
        _require(
            all(type(key) is str and key in index for key in electrons),
            "UNKNOWN_EVENT_ATOM",
        )
        coefficient = _exact(_field(event, "coefficient", "EVENT"))
        _require(coefficient > 0, "POSITIVE_EVENT_COEFFICIENT_REQUIRED")
        atom_indices = tuple(index[key] for key in electrons)
        event_energy = sum((energies[i] for i in atom_indices), Fraction(0))
        if len(atom_indices) == 2:
            _require(event_energy <= cap, "PAIR_ENERGY_CAP_VIOLATION:" + event_key)
            doubles += coefficient
            double_records += 1
            if atom_indices[0] == atom_indices[1]:
                loops += coefficient
                loop_records += 1
            if cross is not None and partitions[atom_indices[0]] != partitions[atom_indices[1]]:
                cross += coefficient
        else:
            singles += coefficient
            single_records += 1
        for i in atom_indices:
            marginal[i] += coefficient
        kinetic += coefficient * event_energy

    for i, key in enumerate(keys):
        _require(marginal[i] == weights[i], "EXACT_MARGINAL_MISMATCH:" + key)

    total = sum(weights, Fraction(0))
    atom_kinetic = sum(
        (energy * weight for energy, weight in zip(energies, weights)),
        Fraction(0),
    )
    _require(kinetic == atom_kinetic, "EXACT_KINETIC_MARGINAL_MISMATCH")
    _require(singles + 2 * doubles == total, "EXACT_TOTAL_LEG_MISMATCH")
    parents = singles + doubles
    _require(parents == total - doubles, "EXACT_PARENT_IDENTITY_MISMATCH")

    graph_check = _check_explicit_dual(energies, dual, cap)
    dual_objective = sum(
        (weight * y for weight, y in zip(weights, dual)), Fraction(0)
    )
    gap = dual_objective - doubles
    _require(gap >= 0, "PRIMAL_EXCEEDS_FEASIBLE_DUAL")
    if require_optimal:
        _require(gap == 0, "NONZERO_PRIMAL_DUAL_GAP")
    if expected_dmax is not None:
        declared_maximum = _exact(expected_dmax)
        _require(declared_maximum >= 0, "NONNEGATIVE_EXPECTED_MAXIMUM_REQUIRED")
        _require(
            dual_objective == declared_maximum,
            "DECLARED_MAXIMUM_DUAL_OBJECTIVE_MISMATCH",
        )
    if target_d is not None:
        requested = _exact(target_d)
        _require(requested >= 0, "NONNEGATIVE_TARGET_REQUIRED")
        _require(doubles == requested, "TARGET_DOUBLE_MASS_MISMATCH")

    return {
        "reference_id": REFERENCE_ID,
        "status": "PASS_EXACT_EXPLICIT_CERTIFICATE",
        "atom_count": len(keys),
        "event_count": len(event_records),
        "single_record_count": single_records,
        "double_record_count": double_records,
        "loop_record_count": loop_records,
        "K": cap,
        "N": total,
        "single_coefficient": singles,
        "double_coefficient": doubles,
        "loop_coefficient": loops,
        "parent_coefficient": parents,
        "selected_kinetic_eV_coefficient": kinetic,
        "cross_duplicate_coefficient": cross,
        "p0_ion_coefficients": (-parents, singles, doubles),
        "p0_charge_coefficient": singles + 2 * doubles,
        "p0_chemical_eV_coefficient": (
            Fraction("24.59") * singles
            + (Fraction("24.59") + Fraction("54.42")) * doubles
        ),
        "marginal_max_abs_residual": Fraction(0),
        "dual_objective": dual_objective,
        "primal_dual_gap": gap,
        "optimality_certified": gap == 0,
        "upper_bound_certified": True,
        **graph_check,
    }


# Each fixture is explicitly authored; no random generator and no optimum
# from the production formula are used.  The small set of stated anchor
# values follows immediate one-atom/all-low/all-high constructions.
# Tuple fields: id, energy literals, weight literals, cap, tags, anchor.
_CASES = (
    ("F001_empty_zero", (), (), 0, ("empty",), "0"),
    ("F002_empty_nonbinary", (), (), "7/3", ("empty", "nonbinary"), "0"),
    ("F003_zero_atom_zero_mass", (0,), (0,), 0, ("zero", "loop"), "0"),
    ("F004_zero_energy_mass", (0,), (3,), 0, ("zero_energy", "loop"), "3/2"),
    ("F005_single_forbidden", (1,), (3,), 1, ("allhigh", "isolated"), "0"),
    ("F006_single_equality", (1,), (3,), 2, ("exact_threshold", "loop"), "3/2"),
    ("F007_single_above", (1,), (3,), 3, ("alllow",), "3/2"),
    ("F008_zero_weight_high", (4,), (0,), 0, ("zero_weight", "allhigh"), "0"),
    ("F009_equal_zero_energies", (0, 0), (1, 3), 0, ("ties", "zero_energy"), "2"),
    (
        "F010_stored_cutoff_decimal_cap",
        ("3602879701896397/36028797018963968",),
        (2,), "1/5", ("stored_cutoff", "decimal_cap", "below_threshold"), "0",
    ),
    (
        "F011_stored_cutoff_exact_cap",
        ("3602879701896397/36028797018963968",),
        (2,), "3602879701896397/18014398509481984",
        ("stored_cutoff", "exact_threshold"), "1",
    ),
    (
        "F012_stored_cutoff_above",
        ("3602879701896397/36028797018963968",),
        (2,), "1/4", ("stored_cutoff", "above_threshold"), "1",
    ),
    ("F013_rational_loop_below", ("1/3",), ("5/7",), "1/2", ("nonbinary", "below_threshold"), "0"),
    ("F014_rational_loop_equal", ("1/3",), ("5/7",), "2/3", ("nonbinary", "exact_threshold"), "5/14"),
    ("F015_rational_loop_above", ("1/3",), ("5/7",), "3/4", ("nonbinary", "above_threshold"), "5/14"),
    ("F016_no_edges", (1, 2, 3), (1, 2, 3), 1, ("allhigh", "disconnected"), "0"),
    ("F017_all_low", (0, "1/2", 1), (2, 3, 4), 2, ("alllow", "exact_threshold"), "9/2"),
    ("F018_all_high", (2, 3, 4), (2, 3, 4), 3, ("allhigh",), "0"),
    ("F019_cross_equal", (1, 3), (1, 1), 4, ("exact_threshold", "cross"), None),
    ("F020_cross_below", (1, 3), (1, 1), "399/100", ("below_threshold", "cross"), None),
    ("F021_high_imbalance", (1, 3), (1, 5), 4, ("imbalanced_tail",), None),
    ("F022_low_imbalance", (1, 3), (5, 1), 4, ("imbalanced_low",), None),
    ("F023_equal_low_levels", (2, 2, 2), (1, 2, 3), 4, ("ties", "alllow"), "3"),
    ("F024_equal_high_levels", (2, 2, 2), (1, 2, 3), "399/100", ("ties", "allhigh"), "0"),
    ("F025_mixed_zero_weights", (0, 1, 2, 3), (0, 1, 0, 1), 3, ("zero_weight", "disconnected"), None),
    ("F026_high_zero_weight", (1, 3, 10), (2, 2, 0), 4, ("zero_weight", "isolated"), None),
    ("F027_low_zero_weight", (0, 1, 3), (0, 1, 4), 4, ("zero_weight", "imbalanced_tail"), None),
    ("F028_equal_high_tail", (0, 1, 3, 3), (1, 1, 1, 2), 4, ("ties", "imbalanced_tail"), None),
    ("F029_equal_low_capacity", (1, 1, 3, 4), (1, 2, 2, 1), 5, ("ties", "nested_neighbors"), None),
    ("F030_isolated_high", (0, 1, 2, 7), (1, 2, 3, 4), 4, ("disconnected", "isolated"), None),
    ("F031_zero_cap_isolates", (0, 0, 1, 2), (1, 2, 3, 4), 0, ("zero_cap", "disconnected"), None),
    ("F032_zero_weight_isolates", (0, 2, 5, 9), (0, 2, 3, 1), 4, ("zero_weight", "disconnected"), None),
    ("F033_ladder_balanced", (0, 1, 2, 3, 4), (1, 1, 1, 1, 1), 4, ("nested_neighbors",), None),
    ("F034_ladder_high_heavy", (0, 1, 2, 3, 4), (1, 1, 1, 3, 3), 4, ("imbalanced_tail",), None),
    ("F035_ladder_low_heavy", (0, 1, 2, 3, 4), (3, 3, 3, 1, 1), 4, ("imbalanced_low",), None),
    ("F036_nonfinal_tail_deficit", (0, 1, 2, 3, 4), (1, 4, 1, 1, 4), 4, ("nonfinal_max_deficit",), None),
    ("F037_final_tail_deficit", (0, 1, 2, 3, 4), (3, 1, 1, 4, 1), 4, ("final_max_deficit",), None),
    ("F038_rational_weights", (0, "1/3", "2/3", 1), ("1/2", "2/3", "3/4", "4/5"), 1, ("nonbinary", "fractional_weights"), None),
    ("F039_rational_tie", ("1/7", "2/7", "2/7", "5/7"), (1, 2, 3, 4), 1, ("nonbinary", "ties"), None),
    ("F040_rational_cross_equal", ("1/7", "2/7", "5/7", "6/7"), (1, 1, 1, 1), 1, ("nonbinary", "exact_threshold"), None),
    ("F041_rational_cross_below", ("1/7", "2/7", "5/7", "6/7"), (1, 1, 1, 1), "999/1000", ("nonbinary", "below_threshold"), None),
    ("F042_mixed_diagonal", ("1/4", "1/2", "3/4", 1), (1, 1, 1, 1), 1, ("loop", "cross", "isolated"), None),
    ("F043_seven_ladder", (0, 1, 2, 3, 4, 5, 6), (1, 1, 1, 1, 1, 1, 1), 6, ("seven_atoms", "nested_neighbors"), None),
    ("F044_seven_imbalanced", (0, 1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 5, 6, 7), 6, ("seven_atoms", "imbalanced_tail"), None),
    ("F045_seven_zero_weights", (0, 1, 2, 3, 4, 5, 6), (0, 0, 0, 0, 0, 0, 0), 6, ("seven_atoms", "zero_weight"), "0"),
    ("F046_permuted_ladder", (6, 0, 5, 1, 4, 2, 3), (1, 1, 1, 1, 1, 1, 1), 6, ("seven_atoms", "permutation"), None),
    ("F047_seven_nonbinary", (0, "1/7", "2/7", "3/7", "4/7", "5/7", "6/7"), (1, 2, 3, 4, 5, 6, 7), "6/7", ("seven_atoms", "nonbinary", "exact_threshold"), None),
    ("F048_seven_disconnected", (0, 1, 2, 3, 4, 9, 10), (1, 1, 1, 1, 1, 1, 1), 4, ("seven_atoms", "disconnected"), None),
)


def deterministic_fixtures():
    """Return 48 fresh plain-record fixtures, without solving any of them."""
    _require(len(_CASES) == FIXTURE_COUNT, "INTERNAL_FIXTURE_COUNT_MISMATCH")
    fixtures = []
    for ident, energies, weights, cap, tags, anchor in _CASES:
        energies, weights, cap = _problem(
            energies, weights, cap, MAX_ORACLE_ATOMS
        )
        fixtures.append({
            "id": ident,
            "energies": energies,
            "weights": weights,
            "K": cap,
            "tags": tags,
            "analytic_anchor_dmax": None if anchor is None else _exact(anchor),
            "atoms": [
                {"key": "atom_%03d" % i, "energy_eV": energy, "coefficient": weight}
                for i, (energy, weight) in enumerate(zip(energies, weights))
            ],
        })
    return fixtures

