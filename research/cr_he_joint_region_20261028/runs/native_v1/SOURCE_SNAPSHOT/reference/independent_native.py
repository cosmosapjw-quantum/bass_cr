"""Independent raw-NPZ primal and same-state consumer certificate checks.

Only standard-library code and numpy's NPZ reader are used.  This module
does not import the joint constructor, event_union, energy_sum, a cross
envelope, or a flow backend.  It does not optimize D or X.  Their global
optimality remains the controller's hash-bound predecessor-proof reuse.

The certificate describes full selection of all four birth bins over the
single window [0, 10**10] proper seconds.  Each witness is an alternative
conditional measure; witnesses are not accumulated as sequential returns.

verify() returns a JSON-serializable PASS report or raises ValueError with
the failing field/atom.  Importing this file performs no scientific work.
Execution is reserved for the root's later bounded independent stage.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import hashlib
import io
import json
import math


NPZ_SHA256 = "1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47"
CONSUMER_SHA256 = "6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d"
ATOM_TUPLE_SHA256 = "2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690"
INPUT_KIND = "STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS"
CONSUMER_SCOPE = "CONDITIONAL_HE_SOURCE_EVENT_UNION"
STOP_TIME = 10_000_000_000
WINDOW_FACTOR = Q(STOP_TIME * STOP_TIME, 2)
NB = Q(8750, 47)
I1 = Q(2459, 100)
I2 = Q(5442, 100)
EV_TO_J = Q("1.602176634e-19")
NEUTRAL_HE_INVENTORY = Q(1085, 94) * Q(99, 100)

_REQUIRED_CONSUMER_NULLS = (
    "actual_full_native25",
    "actual_T",
    "actual_donor_work",
    "outside_partner_response",
    "actual_exclusive_event_measure",
    "global_physical_error",
)
_OPTIONAL_PHYSICAL_NULLS = (
    "actual_K",
    "actual_C",
    "actual_D",
    "actual_d",
    "actual_exclusive_He_kernel",
    "actual_exclusive_kernel",
    "actual_exclusive_event_measure",
    "outside_partner_response",
    "donor_work",
    "actual_donor_work",
    "EOS_T",
    "actual_T",
    "absolute_volume",
    "absolute_proper_volume_m3",
    "full_source_physical_native25",
    "actual_full_native25",
    "global_physical_completion",
    "global_physical_error",
)


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def _object(value, where):
    _need(type(value) is dict, where + ": object required")
    return value


def _field(record, key, where):
    _need(key in record, where + ": missing " + key)
    return record[key]


@lru_cache(maxsize=131072)
def _literal_fraction(text):
    # Cache exact literals only, never rounded numerical states.
    return Q(text)


def _fraction(value, where):
    if type(value) is Q:
        return value
    if type(value) is int:
        return Q(value)
    if type(value) is str:
        try:
            return _literal_fraction(value)
        except (ValueError, ZeroDivisionError, OverflowError):
            pass
    raise ValueError(where + ": exact integer/fraction string required")


def _equal_scalar(actual, expected, where, counts):
    _need(_fraction(actual, where) == expected, where + ": exact mismatch")
    counts["consumer_scalar_checks"] += 1


def _equal_vector(actual, expected, where, counts):
    _need(type(actual) is list and len(actual) == len(expected),
          where + ": vector length mismatch")
    for index, expected_value in enumerate(expected):
        _need(_fraction(actual[index], where) == expected_value,
              where + "[" + str(index) + "]: exact mismatch")
        counts["consumer_vector_component_checks"] += 1


def _numeric_record(actual, expected, where, counts):
    _object(actual, where)
    for key, value in expected.items():
        supplied = _field(actual, key, where)
        if isinstance(value, (tuple, list)):
            _equal_vector(supplied, value, where + "." + key, counts)
        else:
            _equal_scalar(supplied, value, where + "." + key, counts)


def _optional_physical_gates(record, where, counts):
    for key in _OPTIONAL_PHYSICAL_NULLS:
        if key in record:
            _need(record[key] is None, where + "." + key + ": must remain null")
            counts["physical_gate_checks"] += 1
    for key in ("physical_activation", "full_physical_consumer_activation"):
        if key in record:
            _need(record[key] is False, where + "." + key + ": must remain false")
            counts["physical_gate_checks"] += 1


def _load_atoms(npz_path):
    """Reconstruct the original binary64 source without its production loader.

    The keys and partition boundaries are the static convention at
    event_union.py:101-127, not imported code.  The content digest uses that
    consumer's tuple-array schema, not PR115's dictionary-array digest.
    """
    raw = Path(npz_path).read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    _need(actual_hash == NPZ_SHA256, "NPZ byte identity mismatch")
    import numpy as np

    atoms = []
    with np.load(io.BytesIO(raw), allow_pickle=False) as archive:
        energies = archive["energy_eV_with_cutoff"]
        coefficients = archive["identified_A_He_m3_s2"]
        _need(energies.shape == (3201,) and coefficients.shape == (3201,),
              "NPZ must contain 3201 original atoms")
        _need(energies.dtype == np.dtype("float64")
              and coefficients.dtype == np.dtype("float64"),
              "stored binary64 source required")
        previous_energy = None
        for index, (stored_energy, stored_mass) in enumerate(
                zip(energies, coefficients)):
            energy_float = float(stored_energy)
            mass_float = float(stored_mass)
            _need(math.isfinite(energy_float) and math.isfinite(mass_float),
                  "nonfinite stored source")
            _need(mass_float >= 0, "negative stored source mass")
            _need(previous_energy is None or energy_float > previous_energy,
                  "source energies must be strictly increasing")
            previous_energy = energy_float
            energy = Q.from_float(energy_float)
            mass = Q.from_float(mass_float)
            key = "cutoff_ghost" if index == 0 else "active_" + format(index, "04d")
            partition = 0 if index == 0 else (1 if energy <= 1 else (2 if energy <= 3 else 3))
            atoms.append((key, energy, mass, partition))

    _need(atoms[0][1] == Q.from_float(0.1) and atoms[-1][1] == 10,
          "fixed source endpoint mismatch")
    digest_rows = [
        [key, str(energy), str(mass), partition]
        for key, energy, mass, partition in atoms
    ]
    digest = hashlib.sha256(json.dumps(
        digest_rows, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()
    _need(digest == ATOM_TUPLE_SHA256, "reconstructed atom tuple digest mismatch")
    return atoms, actual_hash, digest


def _domain(atoms, cap):
    """Check positive same-bin low/high minima independently of all witnesses."""
    _need(cap >= 0, "negative cap")
    low_flags = []
    low_mass = Q(0)
    low_minima = {}
    high_minima = {}
    for key, energy, mass, partition in atoms:
        is_low = 2 * energy <= cap
        low_flags.append(is_low)
        if is_low:
            low_mass += mass
        if mass == 0:
            continue
        minima = low_minima if is_low else high_minima
        candidate = (energy, key)
        if partition not in minima or candidate < minima[partition]:
            minima[partition] = candidate
    forbidden = None
    for partition in sorted(set(low_minima) & set(high_minima)):
        low_energy, low_key = low_minima[partition]
        high_energy, high_key = high_minima[partition]
        if low_energy + high_energy <= cap:
            forbidden = (low_key, high_key)
            break
    return forbidden is None, forbidden, low_flags, low_mass


def _event_totals(events, atoms, indices, cap, low_flags, where, counts):
    _need(type(events) is list and bool(events), where + ": nonempty event list required")
    marginal = [Q(0) for _ in atoms]
    # Per-bin coefficients for a full partition claim: singleton, partial
    # double, and fully selected double.  These are not the global d and C.
    partition_counts = [[Q(0), Q(0), Q(0)] for _ in range(4)]
    double = Q(0)
    cross = Q(0)
    high_low = Q(0)
    for event_index, event in enumerate(events):
        position = where + ".events[" + str(event_index) + "]"
        _object(event, position)
        legs = _field(event, "electrons", position)
        _need(type(legs) is list and len(legs) in (1, 2),
              position + ": one or two atom keys required")
        _need(all(type(key) is str and key in indices for key in legs),
              position + ": unknown atom key")
        weight = _fraction(_field(event, "coefficient", position), position + ".coefficient")
        _need(weight > 0, position + ": strictly positive event coefficient required")
        leg_indices = [indices[key] for key in legs]
        for atom_index in leg_indices:
            marginal[atom_index] += weight  # Repeated diagonal keys count twice.
        left = leg_indices[0]
        left_partition = atoms[left][3]
        if len(leg_indices) == 1:
            partition_counts[left_partition][0] += weight
        else:
            right = leg_indices[1]
            _need(atoms[left][1] + atoms[right][1] <= cap,
                  position + ": pair energy support violated")
            counts["pair_support_checks"] += 1
            double += weight
            right_partition = atoms[right][3]
            if left_partition == right_partition:
                partition_counts[left_partition][2] += weight
            else:
                cross += weight
                partition_counts[left_partition][1] += weight
                partition_counts[right_partition][1] += weight
            if low_flags[left] != low_flags[right]:
                high_low += weight
        counts["event_records_checked"] += 1

    for index, atom in enumerate(atoms):
        _need(marginal[index] == atom[2],
              where + ": marginal mismatch at " + atom[0])
        counts["atom_marginal_checks"] += 1
    return double, cross, high_low, partition_counts


def _expected_return(single, partial, double, energy_coefficient):
    parents = single + partial + double
    electrons = single + partial + 2 * double
    ions = (-parents, single, partial + double)
    return {
        "s": single * WINDOW_FACTOR,
        "p": partial * WINDOW_FACTOR,
        "d": double * WINDOW_FACTOR,
        "parents": parents * WINDOW_FACTOR,
        "selected_electrons": electrons * WINDOW_FACTOR,
        "selected_energy_eV_m3": energy_coefficient * WINDOW_FACTOR,
        "ion_density_delta": tuple(value * WINDOW_FACTOR for value in ions),
        "ionic_charge_delta": (single + 2 * partial + 2 * double) * WINDOW_FACTOR,
        "recipient_chemical_eV_m3": (
            I1 * single + (I1 + I2) * (partial + double)
        ) * WINDOW_FACTOR,
    }


def _check_consumer(record, total, double, cross, energy_total,
                    partition_counts, partition_masses, partition_energies,
                    atom_digest, where, counts):
    _object(record, where)
    _need(_field(record, "scope", where) == CONSUMER_SCOPE,
          where + ": wrong consumer scope")
    _need(_field(record, "input_kind", where) == INPUT_KIND,
          where + ": wrong source provenance")
    _need(_field(record, "atom_content_sha256", where) == atom_digest,
          where + ": consumer atom identity mismatch")
    _need(_field(record, "attribution_npz_sha256", where) == NPZ_SHA256,
          where + ": consumer NPZ identity mismatch")

    single = total - 2 * double
    _need(single >= 0, where + ": negative full-selection singleton mass")
    union = _expected_return(single, Q(0), double, energy_total)
    _numeric_record(_field(record, "union", where), union, where + ".union", counts)
    _need(union["parents"] <= NEUTRAL_HE_INVENTORY,
          where + ": original neutral-He inventory exhausted")

    pieces = _field(record, "partition_returns", where)
    _need(type(pieces) is list and len(pieces) == 4,
          where + ": all four ordered partition returns required")
    for partition in range(4):
        s, p, d = partition_counts[partition]
        _need(s + p + 2 * d == partition_masses[partition],
              where + ": partition electron marginal mismatch")
        expected_piece = _expected_return(s, p, d, partition_energies[partition])
        _numeric_record(pieces[partition], expected_piece,
                        where + ".partition_returns[" + str(partition) + "]", counts)

    cross_density = cross * WINDOW_FACTOR
    ion21 = [Q(0) for _ in range(21)]
    correction21 = [Q(0) for _ in range(21)]
    ion21[10:13] = union["ion_density_delta"]
    correction21[10:13] = (cross_density, Q(0), -cross_density)

    vector_expectations = {
        "source_ion_density_delta21": ion21,
        "correction_to_sum_of_partition_ion_density21": correction21,
        "native_source_species21": [value / NB for value in ion21],
        "native_species_correction21": [value / NB for value in correction21],
    }
    for key, expected in vector_expectations.items():
        _equal_vector(_field(record, key, where), expected, where + "." + key, counts)

    scalar_expectations = {
        "cross_duplicate_parent_density": cross_density,
        "chemical_correction_eV_m3": -(I1 + I2) * cross_density,
        "ionic_charge_correction_m3": -2 * cross_density,
        "selected_electron_correction_m3": Q(0),
        "selected_kinetic_correction_eV_m3": Q(0),
        "RR_correction": Q(0),
        "retained_photon_correction": Q(0),
        "nb_m3": NB,
        "native_ionic_charge_correction": -2 * cross_density / NB,
        "selected_birth_zeta": total * WINDOW_FACTOR / NB,
        "selected_birth_wnt_J_per_baryon": energy_total * WINDOW_FACTOR * EV_TO_J / NB,
    }
    for key, expected in scalar_expectations.items():
        _equal_scalar(_field(record, key, where), expected, where + "." + key, counts)

    _need(_field(record, "new_source_normalization_applied", where) is False,
          where + ": source normalization must not be repeated")
    _need(_field(record, "full_physical_consumer_activation", where) is False,
          where + ": physical activation must remain false")
    counts["physical_gate_checks"] += 2
    for key in _REQUIRED_CONSUMER_NULLS:
        _need(_field(record, key, where) is None,
              where + "." + key + ": must remain null")
        counts["physical_gate_checks"] += 1
    _optional_physical_gates(record, where, counts)

    windows = _field(record, "accepted_windows", where)
    _need(type(windows) is list and len(windows) == 1,
          where + ": single full-window return required")
    _equal_vector(windows[0], (Q(0), Q(STOP_TIME)),
                  where + ".accepted_windows[0]", counts)


def verify(npz_path, certificate_path):
    """Check the complete frozen native-case certificate without a solver.

    The six accepted caps and three rejected caps are fixed by CONTRACT.
    Every supplied event record and all 3201 atom marginals are checked.
    Five named-vertex coordinate targets must be represented (coincident
    targets are deduplicated); all additional interior records are checked
    identically.  Vertex labels themselves do not establish feasibility.

    D/X optimality and the entire-polygon theorem are NOT reproved here.
    The checked vertex targets are certificate coverage, not a substitute
    for the separate exact small oracle, theory review, or saved D/X proofs.
    """
    _literal_fraction.cache_clear()
    atoms, npz_hash, atom_digest = _load_atoms(npz_path)
    certificate = json.loads(Path(certificate_path).read_text(encoding="utf-8"))
    _object(certificate, "certificate")
    _need(_field(certificate, "source_npz_sha256", "certificate") == npz_hash,
          "certificate NPZ identity mismatch")
    _need(_field(certificate, "consumer_sha256", "certificate") == CONSUMER_SHA256,
          "certificate consumer declaration differs from frozen source")
    _need(_field(certificate, "source_atom_digest", "certificate") == atom_digest,
          "certificate atom tuple digest mismatch")

    counts = {
        "domain_cases_checked": 0,
        "rejected_domain_cases_checked": 0,
        "witnesses_checked": 0,
        "event_records_checked": 0,
        "pair_support_checks": 0,
        "atom_marginal_checks": 0,
        "consumer_scalar_checks": 0,
        "consumer_vector_component_checks": 0,
        "physical_gate_checks": 0,
    }
    _optional_physical_gates(certificate, "certificate", counts)
    indices = {atom[0]: index for index, atom in enumerate(atoms)}
    _need(len(indices) == 3201, "unique original atom count mismatch")
    total = sum((atom[2] for atom in atoms), Q(0))
    energy_total = sum((atom[1] * atom[2] for atom in atoms), Q(0))
    partition_masses = [Q(0) for _ in range(4)]
    partition_energies = [Q(0) for _ in range(4)]
    for key, energy, mass, partition in atoms:
        partition_masses[partition] += mass
        partition_energies[partition] += energy * mass

    accepted_caps = {
        Q(0), Q(1, 5), 2 * atoms[0][1], Q(2), Q(6), Q(20)
    }
    rejected_caps = {Q(1), Q(3), Q(10)}
    cases = _field(certificate, "cases", "certificate")
    rejected_cases = _field(certificate, "rejected_cases", "certificate")
    _need(type(cases) is list and len(cases) == len(accepted_caps),
          "complete six accepted native caps required")
    _need(type(rejected_cases) is list and len(rejected_cases) == len(rejected_caps),
          "complete three rejected native caps required")

    observed_caps = set()
    observed_labels = set()
    reports = []
    for case_index, case in enumerate(cases):
        where = "cases[" + str(case_index) + "]"
        _object(case, where)
        label = _field(case, "label", where)
        _need(type(label) is str and bool(label) and label not in observed_labels,
              where + ": distinct nonempty case label required")
        observed_labels.add(label)
        cap = _fraction(_field(case, "K", where), where + ".K")
        _need(cap in accepted_caps and cap not in observed_caps,
              where + ": unexpected or duplicate accepted cap")
        observed_caps.add(cap)
        valid, forbidden, low_flags, low_mass = _domain(atoms, cap)
        _need(valid and forbidden is None, where + ": outside declared low/high domain")
        counts["domain_cases_checked"] += 1
        _need(_fraction(_field(case, "N", where), where + ".N") == total,
              where + ": source total mismatch")
        _need(_fraction(_field(case, "L", where), where + ".L") == low_mass,
              where + ": independently reconstructed low mass mismatch")
        M = _fraction(_field(case, "M", where), where + ".M")
        D = _fraction(_field(case, "D", where), where + ".D")
        X = _fraction(_field(case, "X", where), where + ".X")
        _need(0 <= M <= min(low_mass, total - low_mass),
              where + ": impossible high-low capacity mass")
        _need(D == (low_mass + M) / 2 and M <= X <= D,
              where + ": inconsistent reused scalar metadata")
        _optional_physical_gates(case, where, counts)

        witnesses = _field(case, "witnesses", where)
        _need(type(witnesses) is list and bool(witnesses),
              where + ": native witnesses required")
        witness_names = set()
        coordinates = set()
        witness_reports = []
        for witness_index, witness in enumerate(witnesses):
            wwhere = where + ".witnesses[" + str(witness_index) + "]"
            _object(witness, wwhere)
            name = _field(witness, "name", wwhere)
            aliases = _field(witness, "aliases", wwhere)
            _need(type(name) is str and bool(name) and name not in witness_names,
                  wwhere + ": distinct nonempty witness name required")
            _need(type(aliases) is list
                  and all(type(alias) is str and bool(alias) for alias in aliases),
                  wwhere + ": alias strings required")
            witness_names.add(name)
            _optional_physical_gates(witness, wwhere, counts)
            events = _field(witness, "events", wwhere)
            d, C, high_low, partition_counts = _event_totals(
                events, atoms, indices, cap, low_flags, wwhere, counts
            )
            _need(_fraction(_field(witness, "d", wwhere), wwhere + ".d") == d,
                  wwhere + ": double-event mass mismatch")
            _need(_fraction(_field(witness, "C", wwhere), wwhere + ".C") == C,
                  wwhere + ": cross-event mass mismatch")
            _need(d <= D and C <= X and high_low <= M,
                  wwhere + ": witness contradicts its reused bound metadata")
            if d == D:
                _need(high_low == M, wwhere + ": total-maximum high-low mass mismatch")
            _check_consumer(
                _field(witness, "consumer", wwhere), total, d, C, energy_total,
                partition_counts, partition_masses, partition_energies,
                atom_digest, wwhere + ".consumer", counts
            )
            coordinates.add((d, C))
            counts["witnesses_checked"] += 1
            witness_reports.append({
                "name": name,
                "aliases": aliases,
                "d": str(d),
                "C": str(C),
                "high_low_mass": str(high_low),
                "events": len(events),
                "marginals": len(atoms),
                "status": "PASS",
            })
        required_vertices = {
            (Q(0), Q(0)),
            (low_mass / 2, Q(0)),
            (D, M),
            (D, X),
            (X, X),
        }
        _need(required_vertices <= coordinates,
              where + ": missing supplied vertex-coordinate witness")
        reports.append({
            "label": label,
            "K": str(cap),
            "domain": "PASS",
            "distinct_required_vertex_points": len(required_vertices),
            "distinct_supplied_points": len(coordinates),
            "additional_nonvertex_points": len(coordinates - required_vertices),
            "witnesses": witness_reports,
        })

    rejected_reports = []
    observed_rejections = set()
    for index, record in enumerate(rejected_cases):
        where = "rejected_cases[" + str(index) + "]"
        _object(record, where)
        label = _field(record, "label", where)
        _need(type(label) is str and bool(label) and label not in observed_labels,
              where + ": distinct nonempty case label required")
        observed_labels.add(label)
        cap = _fraction(_field(record, "K", where), where + ".K")
        _need(cap in rejected_caps and cap not in observed_rejections,
              where + ": unexpected or duplicate rejected cap")
        observed_rejections.add(cap)
        valid, minimum_pair, low_flags, low_mass = _domain(atoms, cap)
        _need(not valid and minimum_pair is not None,
              where + ": independent domain test did not reject")
        domain = _object(_field(record, "domain", where), where + ".domain")
        _need(_field(domain, "valid", where + ".domain") is False,
              where + ": rejected case must declare valid=false")
        pair = _field(domain, "forbidden_pair", where + ".domain")
        _need(type(pair) is list and len(pair) == 2
              and all(type(key) is str and key in indices for key in pair),
              where + ": two known forbidden-pair keys required")
        left, right = (indices[key] for key in pair)
        _need(atoms[left][2] > 0 and atoms[right][2] > 0
              and low_flags[left] != low_flags[right]
              and atoms[left][3] == atoms[right][3]
              and atoms[left][1] + atoms[right][1] <= cap,
              where + ": supplied pair is not a positive same-bin allowed low/high pair")
        _optional_physical_gates(record, where, counts)
        counts["rejected_domain_cases_checked"] += 1
        rejected_reports.append({
            "label": label,
            "K": str(cap),
            "status": "PASS_EXPECTED_DOMAIN_REJECTION",
            "supplied_forbidden_pair": pair,
            "independent_minimum_pair": list(minimum_pair),
        })

    _need(observed_caps == accepted_caps and observed_rejections == rejected_caps,
          "native cap coverage mismatch")
    report = {
        "status": "PASS",
        "scope": "INDEPENDENT_RAW_NPZ_PRIMAL_AND_FULL_SELECTION_CONSUMER",
        "source_npz_sha256": npz_hash,
        "source_atom_digest": atom_digest,
        "atom_digest_schema": "CONSUMER_TUPLE_ARRAY",
        "consumer_sha256": CONSUMER_SHA256,
        "consumer_hash_check": "CERTIFICATE_DECLARATION_MATCHES_FROZEN_PIN",
        "consumer_file_identity_owner": "CONTROLLER_PREIMPORT_SOURCE_PIN",
        "unique_atoms": len(indices),
        "active_atoms": sum(atom[0].startswith("active_") for atom in atoms),
        "cutoff_ghosts": sum(atom[0] == "cutoff_ghost" for atom in atoms),
        "counts": counts,
        "cases": reports,
        "rejected_cases": rejected_reports,
        "arithmetic": "EXACT_FRACTION_FOR_STORED_BINARY64_INPUT",
        "global_D_X_optimality": "REUSED_PRIOR_CERTIFICATE_PROOF_NOT_RECOMPUTED",
        "entire_projection_proof": "SEPARATE_THEORY_AND_SMALL_ORACLE_OBLIGATION",
        "solver_calls": 0,
        "production_module_imports": 0,
        "physical_activation": False,
    }
    _literal_fraction.cache_clear()
    return report
