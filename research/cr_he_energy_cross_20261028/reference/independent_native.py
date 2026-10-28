"""Independent evaluation of saved native cross-bound certificates.

Authored without executing/importing this file, loading NPZ, or calling a
scientific solver. Root owns the bounded execution ledger. This evaluator
imports neither production code nor a source loader. The public predecessor
consumer/output interface and the new Solution record were read for schema
alignment; this is not a blinded review.

All source atoms are independently reconstructed from the byte-pinned NPZ.
All allowed dual edges are checked through exact sorted-prefix minima: this
is complete constraint verification, not sparse-edge sampling. For cases
without a primal witness, the output explicitly separates an upper certificate
from theorem-dependent sharpness and marks primal attainment NOT_RUN.
"""

from bisect import bisect_right
from fractions import Fraction as F
from pathlib import Path
import hashlib
import io
import json
import math


NPZ_SHA = "1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47"
SOURCE_SHA = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
NB = F(8750, 47)
I1, I2 = F(2459, 100), F(5442, 100)
EV_J = F("1.602176634e-19")
H_NEUTRAL = F(1085, 94) * F(99, 100)
HISTORY_END = F(10_000_000_000)


def require(condition, name):
    if not condition:
        raise ValueError(name)


def q(value, name="rational"):
    require(type(value) in (str, int), name + ": exact serialized rational required")
    try:
        answer = F(value)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError(name + ": malformed rational") from None
    return answer


def equal(raw, expected, name):
    require(q(raw, name) == expected, name + ": exact mismatch")


def sequence_equal(raw, expected, name):
    require(type(raw) is list and len(raw) == len(expected), name + ": dimension mismatch")
    for i, value in enumerate(expected):
        equal(raw[i], value, name + "[" + str(i) + "]")


def digest_atoms(atoms):
    rows = [[key, str(e), str(w), part] for key, e, w, part in atoms]
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def reconstruct_source(npz_path, saved_atoms, asserted_digest):
    """Independently read the original arrays, not production-derived atoms."""
    import numpy as np

    raw = Path(npz_path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == NPZ_SHA, "NPZ byte SHA256 mismatch")
    require(type(saved_atoms) is list and len(saved_atoms) == 3201,
            "saved native atom count must be 3201")
    with np.load(io.BytesIO(raw), allow_pickle=False) as source:
        energy = source["energy_eV_with_cutoff"]
        weight = source["identified_A_He_m3_s2"]
        require(energy.shape == (3201,) and weight.shape == (3201,),
                "original NPZ array shape mismatch")
        require(energy.dtype == np.dtype("float64") and weight.dtype == np.dtype("float64"),
                "original NPZ arrays must be binary64")
        atoms = []
        last_energy = None
        for i in range(3201):
            ef, wf = float(energy[i]), float(weight[i])
            require(math.isfinite(ef) and math.isfinite(wf) and wf >= 0,
                    "nonfinite original scalar or negative weight")
            e, w = F.from_float(ef), F.from_float(wf)
            require(last_energy is None or e > last_energy, "original energies not strictly ordered")
            last_energy = e
            key = "cutoff_ghost" if i == 0 else "active_" + format(i, "04d")
            part = 0 if i == 0 else (1 if e <= 1 else (2 if e <= 3 else 3))
            row = saved_atoms[i]
            require(type(row) is dict, "saved atom must be a mapping")
            require(row.get("key") == key, "saved atom key/order differs from original")
            equal(row.get("energy_eV"), e, "original atom energy")
            equal(row.get("coefficient"), w, "original atom coefficient")
            require(type(row.get("partition")) is int and row["partition"] == part,
                    "saved birth partition differs from original")
            atoms.append((key, e, w, part))
    require(atoms[0][1] == F.from_float(0.1) and atoms[-1][1] == 10,
            "native support endpoints changed")
    computed_digest = digest_atoms(atoms)
    require(type(asserted_digest) is str and asserted_digest == computed_digest,
            "original atom content digest mismatch")
    return tuple(atoms), {
        "npz_bytes": len(raw), "npz_sha256": NPZ_SHA,
        "atom_content_sha256": computed_digest,
        "source_atoms_compared": 3201, "source_fields_compared": 12804,
        "native_active_atoms": 3200, "separate_cutoff_ghost_atoms": 1,
        "numpy_version": np.__version__, "production_source_imports": 0,
        "source_fit_replays": 0, "npz_loads": 1,
    }


def grouped_atoms(atoms):
    groups = {}
    for key, energy, weight, part in atoms:
        groups.setdefault(part, []).append((energy, key, weight))
    for rows in groups.values():
        rows.sort(key=lambda x: (x[0], x[1]))
    return groups


def parse_dual(raw, keys, name):
    require(type(raw) is list and len(raw) == len(keys), name + ": dual length mismatch")
    dual = {}
    for row in raw:
        require(type(row) is list and len(row) == 2, name + ": malformed dual entry")
        key = row[0]
        require(type(key) is str and key in keys and key not in dual,
                name + ": unknown/duplicate dual key")
        value = q(row[1], name + ": dual value")
        require(value >= 0, name + ": negative dual value")
        dual[key] = value
    require(set(dual) == keys, name + ": incomplete dual domain")
    return dual


def check_all_dual_edges(atoms, groups, cap, dual):
    """All edges checked by the minimum y in each exact eligible prefix."""
    data = {}
    for part, rows in groups.items():
        energies = []
        prefix_min = []
        current_min = None
        for energy, key, _weight in rows:
            energies.append(energy)
            value = dual[key]
            current_min = value if current_min is None else min(current_min, value)
            prefix_min.append(current_min)
        data[part] = (energies, prefix_min)
    groups_checked = 0
    directed_edges = 0
    for key, energy, _weight, part in atoms:
        for other, (energies, prefix_min) in data.items():
            if part == other:
                continue
            count = bisect_right(energies, cap - energy)
            if count:
                groups_checked += 1
                directed_edges += count
                require(dual[key] + prefix_min[count - 1] >= 1,
                        "dual infeasible in a complete allowed prefix")
    require(directed_edges % 2 == 0, "undirected edge symmetry failed")
    return {"eligible_prefix_groups_checked": groups_checked,
            "undirected_allowed_edges_covered": directed_edges // 2,
            "dual_vertices_checked": len(atoms),
            "edge_check_method": "ALL_ALLOWED_EDGES_VIA_EXACT_PREFIX_MINIMA"}


def check_independent_set(atoms, cap, raw_independent, raw_neighbors):
    keys = {a[0] for a in atoms}
    for name, raw in (("independent", raw_independent), ("neighbors", raw_neighbors)):
        require(type(raw) is list and all(type(v) is str for v in raw),
                name + ": key list required")
        require(len(set(raw)) == len(raw) and set(raw) <= keys,
                name + ": duplicate/unknown atom key")
    independent = set(raw_independent)
    minimum = {}
    for key, energy, _weight, part in atoms:
        if key in independent:
            minimum[part] = min(energy, minimum.get(part, energy))
    parts = sorted(minimum)
    for pos, part in enumerate(parts):
        for other in parts[pos + 1:]:
            require(minimum[part] + minimum[other] > cap,
                    "asserted independent set contains a permitted cross edge")
    neighbors = set()
    for key, energy, _weight, part in atoms:
        if any(other != part and energy + e0 <= cap for other, e0 in minimum.items()):
            neighbors.add(key)
    require(neighbors == set(raw_neighbors), "asserted open neighborhood incomplete or changed")
    require(not independent.intersection(neighbors), "independent set intersects its neighborhood")
    selected_mass = sum((w for key, _e, w, _p in atoms if key in independent), F(0))
    neighbor_mass = sum((w for key, _e, w, _p in atoms if key in neighbors), F(0))
    return independent, neighbors, selected_mass - neighbor_mass


def check_witness(atoms, groups, cap, optimum, witness):
    require(type(witness) is dict, "witness must be a mapping")
    amap = {key: (energy, weight, part) for key, energy, weight, part in atoms}
    incidence = {key: F(0) for key in amap}
    pair_sum = F(0)
    single_sum = F(0)
    pair_seen, single_seen = set(), set()
    pair_incidence_by_partition = {part: F(0) for part in groups}
    single_mass_by_partition = {part: F(0) for part in groups}
    for array_name, arity in (("pairs", 2), ("singles", 1)):
        records = witness.get(array_name)
        require(type(records) is list, "witness event list missing")
        for record in records:
            require(type(record) is dict, "event mapping required")
            electrons = record.get("electrons")
            require(type(electrons) is list and len(electrons) == arity,
                    "event electron arity mismatch")
            require(all(type(key) is str and key in amap for key in electrons),
                    "event electron identity mismatch")
            mass = q(record.get("coefficient"), "event coefficient")
            require(mass > 0, "event coefficient must be positive")
            if arity == 2:
                left, right = electrons
                edge = tuple(sorted((left, right)))
                require(left != right and edge not in pair_seen, "duplicate or diagonal cross pair")
                pair_seen.add(edge)
                require(amap[left][2] != amap[right][2], "same-bin pair entered cross witness")
                require(amap[left][0] + amap[right][0] <= cap, "pair violates exact energy support")
                pair_sum += mass
                pair_incidence_by_partition[amap[left][2]] += mass
                pair_incidence_by_partition[amap[right][2]] += mass
            else:
                key = electrons[0]
                require(key not in single_seen, "duplicate atomwise single")
                single_seen.add(key)
                single_sum += mass
                single_mass_by_partition[amap[key][2]] += mass
            for key in electrons:
                incidence[key] += mass
    for key, _energy, weight, _part in atoms:
        require(incidence[key] == weight, "full native marginal exact equality failed")
    total = sum((a[2] for a in atoms), F(0))
    require(pair_sum == optimum and single_sum + 2 * pair_sum == total,
            "witness objective/count identity failed")
    equal(witness.get("cross_C"), pair_sum, "reported cross C")
    method = witness.get("method")
    if method == "PR112_HALF_SHIFT_FILTERED_CROSS":
        # The caller has already checked the complete formula dual and its
        # exact objective.  An explicit supported primal attaining that same
        # objective proves optimality without any flow or cut claim.  The
        # recorded construction label is not a reconstruction of that method.
        for name in ("flow_value", "mincut_capacity", "mincut_dual"):
            require(name in witness and witness[name] is None,
                    "filtered half-shift witness must leave flow/cut fields null")
        dual_checks = None
        flow_scaling_matches = None
        cut_status = "NOT_PROVIDED_NOT_RUN"
        network_status = "NOT_RUN_NO_FLOW_OR_MINCUT_CLAIM"
        optimality_basis = "EXPLICIT_PRIMAL_EQUALS_SEPARATELY_CHECKED_FORMULA_DUAL"
    else:
        # Preserve every existing compact-flow check.  A method label cannot
        # bypass these checks unless it is the explicitly supported non-flow
        # construction above, whose null fields are required in full.
        equal(witness.get("flow_value"), 2 * pair_sum, "reported flow scaling")
        equal(witness.get("mincut_capacity"), 2 * pair_sum, "reported cut scaling")
        cut_dual = parse_dual(witness.get("mincut_dual"), set(amap), "cut dual")
        dual_checks = check_all_dual_edges(atoms, groups, cap, cut_dual)
        require(sum((w * cut_dual[key] for key, _e, w, _p in atoms), F(0)) == pair_sum,
                "cut dual exact objective failed")
        flow_scaling_matches = True
        cut_status = "PASS_EXPLICIT_CUT_DUAL_AND_REPORTED_CAPACITY_SCALING"
        network_status = "NOT_RUN_NOT_REQUIRED_BY_PRIMAL_DUAL_CERTIFICATE"
        optimality_basis = "EXPLICIT_PRIMAL_EQUALS_FORMULA_DUAL_AND_CUT_DUAL"
    return {
        "pairs_checked": len(pair_seen), "singles_checked": len(single_seen),
        "atom_marginals_checked": len(atoms), "primal_dual_gap": "0",
        "marginal_max_residual": "0", "cut_dual_checks": dual_checks,
        "construction_method_as_recorded": method,
        "reported_flow_scaling_matches": flow_scaling_matches,
        "mincut_certificate": cut_status,
        "optimality_basis": optimality_basis,
        "network_reconstruction": network_status,
    }, pair_incidence_by_partition, single_mass_by_partition


def check_consumer(atoms, optimum, consumer, pair_bins, single_bins, source_digest):
    require(type(consumer) is dict, "consumer must be a mapping")
    windows = consumer.get("accepted_windows")
    require(type(windows) is list and bool(windows), "consumer accepted window missing")
    for window in windows:
        require(type(window) is list and len(window) == 2, "window pair required")
        a0, b0 = (q(x, "proper window") for x in window)
        require(0 <= a0 < b0 <= HISTORY_END, "window outside supplied proper history")
    a, b = (q(x, "last proper window") for x in windows[-1])
    for old in windows[:-1]:
        c, d = (q(x, "prior proper window") for x in old)
        require(b <= c or d <= a, "returned window overlaps a prior accepted window")
    W = (b * b - a * a) / 2
    N = sum((x[2] for x in atoms), F(0))
    U = sum((energy * weight for _key, energy, weight, _part in atoms), F(0))
    C = optimum * W
    n, energy_density = N * W, U * W
    d_count = C
    s_count = n - 2 * C
    parent_count = n - C
    require(parent_count <= H_NEUTRAL, "selected witness exhausts native neutral inventory")
    ion = (-n + C, n - 2 * C, C)
    correction = (C, F(0), -C)
    ion21, corr21 = [F(0)] * 21, [F(0)] * 21
    ion21[10:13], corr21[10:13] = ion, correction
    require(consumer.get("atom_content_sha256") == source_digest,
            "consumer atom identity changed")
    require(consumer.get("attribution_npz_sha256") == NPZ_SHA,
            "consumer source NPZ identity changed")
    require(consumer.get("input_kind") == "STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS",
            "consumer native provenance label missing")
    require(consumer.get("scope") == "CONDITIONAL_HE_SOURCE_EVENT_UNION",
            "consumer scope changed")
    equal(consumer.get("nb_m3"), NB, "same-state nb")
    sequence_equal(consumer.get("source_ion_density_delta21"), ion21, "source ion21")
    sequence_equal(consumer.get("correction_to_sum_of_partition_ion_density21"), corr21,
                   "source correction21")
    sequence_equal(consumer.get("native_source_species21"), [x / NB for x in ion21],
                   "native source species21")
    sequence_equal(consumer.get("native_species_correction21"), [x / NB for x in corr21],
                   "native correction21")
    scalar_values = {
        "cross_duplicate_parent_density": C,
        "chemical_correction_eV_m3": -(I1 + I2) * C,
        "ionic_charge_correction_m3": -2 * C,
        "native_ionic_charge_correction": -2 * C / NB,
        "selected_birth_zeta": n / NB,
        "selected_birth_wnt_J_per_baryon": energy_density * EV_J / NB,
        "selected_electron_correction_m3": F(0),
        "selected_kinetic_correction_eV_m3": F(0),
        "RR_correction": F(0), "retained_photon_correction": F(0),
    }
    for name, expected in scalar_values.items():
        equal(consumer.get(name), expected, name)
    union = consumer.get("union")
    require(type(union) is dict, "union return missing")
    for name, expected in {
        "s": s_count, "p": F(0), "d": d_count, "parents": parent_count,
        "selected_electrons": n, "selected_energy_eV_m3": energy_density,
        "ionic_charge_delta": n,
        "recipient_chemical_eV_m3": I1 * n + (I2 - I1) * C,
    }.items():
        equal(union.get(name), expected, "union " + name)
    sequence_equal(union.get("ion_density_delta"), ion, "union ion delta")
    pieces = consumer.get("partition_returns")
    require(type(pieces) is list and len(pieces) == 4, "all four partition returns required")
    for part, piece in enumerate(pieces):
        part_n = sum((w for _key, _energy, w, p in atoms if p == part), F(0)) * W
        part_u = sum((w * e for _key, e, w, p in atoms if p == part), F(0)) * W
        part_s, part_p = single_bins[part] * W, pair_bins[part] * W
        require(part_s + part_p == part_n, "per-partition leg accounting failed")
        for name, expected in {
            "s": part_s, "p": part_p, "d": F(0), "parents": part_n,
            "selected_electrons": part_n, "selected_energy_eV_m3": part_u,
            "ionic_charge_delta": part_n + part_p,
            "recipient_chemical_eV_m3": I1 * part_n + I2 * part_p,
        }.items():
            equal(piece.get(name), expected, "partition " + str(part) + " " + name)
        sequence_equal(piece.get("ion_density_delta"), (-part_n, part_s, part_p),
                       "partition ion delta")
    for name in ("actual_full_native25", "actual_T", "actual_donor_work",
                 "outside_partner_response", "actual_exclusive_event_measure",
                 "global_physical_error"):
        require(name in consumer and consumer[name] is None, "physical input null changed: " + name)
    require(consumer.get("full_physical_consumer_activation") is False,
            "full physical consumer was activated")
    require(consumer.get("new_source_normalization_applied") is False,
            "extra source normalization was applied")
    return {"proper_factor_W_s2": str(W), "same_state_nb_m3": str(NB),
            "cross_parent_density_m3": str(C), "chemical_correction_eV_m3": str(-(I1 + I2) * C),
            "native_HeI_correction": str(C / NB),
            "source_factor_applications": 1, "nb_divisions": 1,
            "whole_algebraic_C_interval_inventory_inactive": n <= H_NEUTRAL,
            "selected_witness_inventory_pass": True,
            "interpretation": "PARTITION_UNION_CORRECTION; FULL_PHYSICAL_NATIVE25_NULL"}


def evaluate(certificate_path, npz_path):
    """Return JSON-compatible independent validation of saved exact data."""
    raw = Path(certificate_path).read_bytes()
    certificate = json.loads(raw)
    require(type(certificate) is dict, "top-level certificate mapping required")
    require(certificate.get("npz_sha256") == NPZ_SHA, "certificate NPZ pin mismatch")
    atoms, source = reconstruct_source(npz_path, certificate.get("atoms"),
                                       certificate.get("source_atom_digest"))
    groups = grouped_atoms(atoms)
    keys = {a[0] for a in atoms}
    total = sum((a[2] for a in atoms), F(0))
    cases = certificate.get("cases")
    require(type(cases) is list and bool(cases), "nonempty saved case array required")
    labels = [c.get("label") for c in cases if type(c) is dict]
    require(len(labels) == len(cases) and all(type(v) is str and v for v in labels)
            and len(set(labels)) == len(labels), "case labels invalid or duplicated")
    output = []
    for case in cases:
        result = {"label": case["label"], "status": "FAIL"}
        try:
            bound = case.get("bound")
            require(type(bound) is dict, "bound mapping required")
            cap = q(bound.get("K_eV"), "cap")
            require(cap >= 0, "negative cap")
            equal(bound.get("total"), total, "bound total mass")
            delta, optimum = q(bound.get("deficit"), "deficit"), q(bound.get("cmax"), "optimum")
            require(0 <= delta <= total and 0 <= optimum <= total / 2,
                    "bound scalar outside finite mass range")
            require(optimum == (total - delta) / 2, "bound deficit identity failed")
            dual = parse_dual(bound.get("dual"), keys, "formula dual")
            dual_checks = check_all_dual_edges(atoms, groups, cap, dual)
            dual_objective = sum((w * dual[key] for key, _e, w, _p in atoms), F(0))
            require(dual_objective == optimum, "formula dual exact objective failed")
            independent, neighbors, explicit_delta = check_independent_set(
                atoms, cap, bound.get("independent"), bound.get("neighbors"))
            require(explicit_delta == delta, "explicit independent deficiency mismatch")
            for key in keys:
                expected_y = F(0) if key in independent else (F(1) if key in neighbors else F(1, 2))
                require(dual[key] == expected_y, "dual/independent-set representation mismatch")
            result.update({"K_eV": str(cap), "cmax": str(optimum), "deficit": str(delta),
                           "dual_checks": dual_checks, "dual_objective_gap": "0",
                           "independent_set_vertices": len(independent),
                           "open_neighborhood_vertices": len(neighbors),
                           "upper_certificate": "PASS_EXACT",
                           "primal_attainment": "NOT_RUN",
                           "optimality_status": "THEOREM_DEPENDENT_BOUND_ONLY",
                           "consumer_status": "NOT_RUN"})
            witness = case.get("witness")
            if witness is not None:
                checked, pair_bins, single_bins = check_witness(atoms, groups, cap, optimum, witness)
                result.update({"witness_checks": checked, "primal_attainment": "PASS_EXACT",
                               "optimality_status": "PASS_EXACT_PRIMAL_DUAL_EQUALITY"})
                if case.get("consumer") is not None:
                    result["consumer_checks"] = check_consumer(
                        atoms, optimum, case["consumer"], pair_bins, single_bins,
                        source["atom_content_sha256"])
                    result["consumer_status"] = "PASS_EXACT_SAME_STATE_ONCE_ONLY"
            else:
                require(case.get("consumer") is None, "consumer without independently checked witness")
            result["status"] = "PASS"
        except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError) as exc:
            result["failure"] = type(exc).__name__ + ": " + str(exc)
        output.append(result)
    failed = sum(row["status"] != "PASS" for row in output)
    return {"status": "PASS_INDEPENDENT_NATIVE_CERTIFICATES" if failed == 0 else "FAIL",
            "certificate_bytes": len(raw),
            "certificate_sha256": hashlib.sha256(raw).hexdigest(),
            "source": source, "cases": output, "cases_evaluated": len(output),
            "passed_cases": len(output) - failed, "failed_cases": failed,
            "primal_attainment_cases": sum(row.get("primal_attainment") == "PASS_EXACT" for row in output),
            "consumer_cases": sum(row.get("consumer_status") == "PASS_EXACT_SAME_STATE_ONCE_ONLY" for row in output),
            "production_imports": 0, "production_solver_calls": 0,
            "source_fit_transport_RR_replays": 0,
            "maxflow_network_reconstruction": "NOT_RUN; EXPLICIT_PRIMAL_DUAL_CERTIFICATES_CHECKED",
            "independence": "SEPARATE_EVALUATOR; PUBLIC_OUTPUT_SCHEMA_READ; NOT_BLINDED"}

