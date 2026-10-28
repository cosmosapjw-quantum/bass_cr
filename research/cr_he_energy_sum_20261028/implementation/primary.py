"""Measured primary cases and once-only native returns for energy-sum support.

The independent reference module supplies fixed fixture data only.  Neither
its oracle nor its certificate verifier is invoked here.  All scientific
solver/checker calls use energy_sum.py; no old source/RR calculation is replayed.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import sys

import energy_sum as es

REFERENCE_SHA = "58ede1228866a8ca29cce838b7fbfb473c872ea9ef20ec0faf69066df276983b"
NPZ_RELATIVE = "research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz"
CANONICAL_RELATIVE = "research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json"
PREDECESSOR_RELATIVE = "research/cr_he_event_union_20261028/implementation/event_union.py"
T = F(10000000000)
I1, I2 = F(2459, 100), F(5442, 100)


def write_new(path, value):
    raw = (json.dumps(es.serial(value), indent=2, allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
    return {"name": path.name, "path": str(path), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def atom_records(atoms):
    return [{"key": a.key, "energy_eV": a.energy_eV,
             "coefficient": a.coefficient, "partition": a.partition} for a in atoms]


def certificate_record(ident, solution, atoms=None):
    row = {"id": ident, "K_eV": solution.K_eV, "dmax": solution.dmax,
           "target_d": solution.target_d, "dual_by_key": dict(solution.dual),
           "max_events": solution.max_events, "events": solution.events}
    if atoms is not None:
        row["atoms"] = atom_records(atoms)
    return row


def main():
    out = Path(sys.argv[1])
    unit = Path(__file__).resolve().parents[1]
    repo = unit.parents[1]
    reference_path = unit / "reference/generic_dual.py"
    reference_sha = hashlib.sha256(reference_path.read_bytes()).hexdigest()
    es.require(reference_sha == REFERENCE_SHA, "FIXED_REFERENCE_FIXTURE_BYTES_MISMATCH")
    sys.path.insert(0, str(unit / "reference"))
    from generic_dual import deterministic_fixtures

    fixtures = deterministic_fixtures()  # Fixed input data and scalar parsing only.
    es.require(len(fixtures) == 48 and [row["id"].split("_", 1)[0] for row in fixtures]
               == [f"F{i:03d}" for i in range(1, 49)], "EXACT_48_FIXTURE_ORDER_REQUIRED")
    checks, small_cases, small_summary = [], [], []
    solve_calls = {"small_optimum": 0, "small_selected_target": 0,
                   "native_optimum": 0, "native_selected_target": 0}

    def check(name, condition, evidence=None):
        row = {"name": name, "passed": bool(condition)}
        if evidence is not None:
            row["evidence"] = evidence
        checks.append(row)

    for index, fixture in enumerate(fixtures):
        atoms = tuple(es.Atom(f"a{i}", energy, weight, i % 4)
                      for i, (energy, weight) in enumerate(zip(fixture["energies"], fixture["weights"])))
        maximum = es.solve(atoms, fixture["K"])
        solve_calls["small_optimum"] += 1
        target = F(index % 3, 2) * maximum.dmax
        if target == maximum.dmax:
            chosen = maximum
        else:
            chosen = es.solve(atoms, fixture["K"], target_d=target)
            solve_calls["small_selected_target"] += 1
        certificate = es.verify(atoms, chosen)
        check("small_certificate_" + fixture["id"],
              certificate["status"] == "PASS_EXACT_CONDITIONAL_ENERGY_SUM"
              and chosen.dmax == maximum.dmax and certificate["target_d"] == target,
              {"atoms": len(atoms), "dmax": chosen.dmax, "target_d": target,
               "primal_dual_gap": certificate["primal_dual_gap"]})
        if fixture["analytic_anchor_dmax"] is not None:
            check("small_analytic_anchor_" + fixture["id"],
                  chosen.dmax == fixture["analytic_anchor_dmax"],
                  {"actual": chosen.dmax, "anchor": fixture["analytic_anchor_dmax"]})
        small_cases.append(certificate_record(fixture["id"], chosen, atoms))
        small_summary.append({"id": fixture["id"], "tags": fixture["tags"],
                              "N": chosen.N, "K_eV": chosen.K_eV, "dmax": chosen.dmax,
                              "target_d": chosen.target_d, "delta": chosen.delta,
                              "maximum_event_records": len(chosen.max_events),
                              "chosen_event_records": len(chosen.events),
                              "primal_dual_gap": certificate["primal_dual_gap"],
                              "marginal_residual": certificate["chosen"]["marginal_residual"]})

    manifest_path = unit / "inputs/INPUT_MANIFEST.json"
    manifest_raw = manifest_path.read_bytes()
    inputs = {row["path"]: row for row in json.loads(manifest_raw)["files"]}
    source = es.load_native(repo / NPZ_RELATIVE)
    native_atoms = tuple(es.Atom(a.key, a.energy_eV, a.coefficient, a.partition) for a in source.atoms)
    total = sum((a.coefficient for a in native_atoms), F(0))
    kinetic = sum((a.energy_eV * a.coefficient for a in native_atoms), F(0))
    positive_count = sum(a.coefficient > 0 for a in native_atoms)
    check("actual_pinned_input_manifest_identities",
          inputs[NPZ_RELATIVE]["sha256"] == source.attribution_npz_sha256
          and inputs[CANONICAL_RELATIVE]["sha256"] == source.canonical_source_sha256
          and inputs[PREDECESSOR_RELATIVE]["sha256"] == es.PREDECESSOR_SHA
          and len(native_atoms) == 3201 and source.atom_content_sha256 == es.atom_content_id(native_atoms))
    check("native_positive_total", total > 0, {"N": total})
    source_pins = {"npz_path_relative_to_repo": NPZ_RELATIVE,
                   "npz_sha256": source.attribution_npz_sha256,
                   "npz_byte_identity_verified_by_pinned_loader": True,
                   "canonical_source_path_relative_to_repo": CANONICAL_RELATIVE,
                   "canonical_source_sha256": source.canonical_source_sha256,
                   "canonical_source_identity_basis": "PINNED_PREDECESSOR_AND_INPUT_MANIFEST_REUSE",
                   "predecessor_module_path_relative_to_repo": PREDECESSOR_RELATIVE,
                   "predecessor_module_sha256": es.PREDECESSOR_SHA,
                   "atom_content_sha256": source.atom_content_sha256,
                   "input_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
                   "reference_fixture_file_sha256": reference_sha,
                   "production_module_sha256": hashlib.sha256(Path(es.__file__).read_bytes()).hexdigest()}
    cutoff = F.from_float(0.1)
    caps = (F(0), F(1, 5), 2 * cutoff, F(1), F(2), F(3), F(6), F(10), F(20))
    native_cases, cap_rows, native_runs = [], [], {}
    for index, cap_value in enumerate(caps, 1):
        cap = es.bind_cap(source, cap_value,
                          f"Conditional cumulative Ea+Eb<={cap_value} eV finite-source envelope; actual physical K is null.")
        maximum = es.native_plan(source, cap)
        solve_calls["native_optimum"] += 1
        if cap_value == 3:
            chosen = es.native_plan(source, cap, target_d=maximum.dmax / 2)
            solve_calls["native_selected_target"] += 1
        else:
            chosen = maximum
        certificate = es.verify(native_atoms, chosen)
        ident = f"N{index:03d}"
        check("native_certificate_" + ident,
              certificate["status"] == "PASS_EXACT_CONDITIONAL_ENERGY_SUM"
              and chosen.N == total and chosen.dmax == maximum.dmax
              and len(chosen.max_events) <= positive_count and len(chosen.events) <= 2 * positive_count,
              {"K_eV": cap_value, "dmax": chosen.dmax, "target_d": chosen.target_d,
               "maximum_event_records": len(chosen.max_events), "chosen_event_records": len(chosen.events),
               "primal_dual_gap": certificate["primal_dual_gap"]})
        native_cases.append(certificate_record(ident, chosen))
        cap_rows.append({"id": ident, "K_eV": cap_value, "N": total,
                         "low_mass": chosen.low_mass, "high_mass": chosen.high_mass,
                         "dmax": chosen.dmax, "target_d": chosen.target_d, "delta": chosen.delta,
                         "dmax_over_N": chosen.dmax / total if total else None,
                         "parent_min_over_N": (total - chosen.dmax) / total if total else None,
                         "witness_C": certificate["chosen"]["cross_C"],
                         "witness_C_scope": "CHOSEN_WITNESS_ONLY_NOT_MAX_C",
                         "maximum_event_records": len(chosen.max_events),
                         "chosen_event_records": len(chosen.events),
                         "primal_dual_gap": certificate["primal_dual_gap"],
                         "marginal_residual": certificate["chosen"]["marginal_residual"],
                         "cap_binding": cap})
        native_runs[cap_value] = (cap, chosen)
    check("native_decimal_cutoff_excludes_all_doubles", native_runs[F(1, 5)][1].dmax == 0)
    ghost = next(a for a in native_atoms if a.key == "cutoff_ghost")
    check("native_exact_twice_cutoff_admits_ghost_diagonal",
          native_runs[2 * cutoff][1].dmax == ghost.coefficient / 2,
          {"stored_cutoff_eV": cutoff, "cap_eV": 2 * cutoff, "ghost_coefficient": ghost.coefficient})
    check("native_complete_support_K20", native_runs[F(20)][1].dmax == total / 2)
    check("native_cap_samples_monotone",
          all(native_runs[left][1].dmax <= native_runs[right][1].dmax for left, right in zip(caps, caps[1:])),
          {"scope": "Nine saved cap samples; no continuous or physical kernel inference."})

    def checked_consumer(label, cap, solution, window, previous_windows=()):
        value = es.consume_native(source, cap, solution, window, nb_m3=es.NB,
                                  previous_windows=previous_windows)
        port = value["source_return"]
        union = port["union"]
        left, right = window
        factor = (right * right - left * left) / 2
        n, d = solution.N, solution.target_d
        ions = tuple(factor * x for x in (-n + d, n - 2 * d, d))
        check(label + "_proper_factor_once", value["proper_window_factor_s2"] == factor and factor > 0
              and value["source_normalization_reapplied"] is False
              and port["new_source_normalization_applied"] is False)
        check(label + "_full_selected_marginal",
              union["selected_electrons"] == factor * n
              and union["selected_energy_eV_m3"] == factor * kinetic and union["p"] == 0)
        check(label + "_parent_single_double_identity",
              union["parents"] == factor * (n - d)
              and union["s"] == factor * (n - 2 * d) and union["d"] == factor * d)
        check(label + "_species_charge_chemical",
              tuple(union["ion_density_delta"]) == ions
              and union["ionic_charge_delta"] == factor * n
              and union["recipient_chemical_eV_m3"] == factor * (I1 * n + (I2 - I1) * d)
              and tuple(port["source_ion_density_delta21"][10:13]) == ions
              and all(x == 0 for i, x in enumerate(port["source_ion_density_delta21"]) if i not in (10, 11, 12)))
        check(label + "_nb_normalization_once", port["nb_m3"] == es.NB
              and port["native_source_species21"] == [x / es.NB for x in port["source_ion_density_delta21"]]
              and port["selected_birth_zeta"] == factor * n / es.NB
              and port["selected_birth_wnt_J_per_baryon"] == factor * kinetic * F("1.602176634e-19") / es.NB)
        check(label + "_RR_photon_separate", port["RR_correction"] == 0
              and port["retained_photon_correction"] == 0)
        check(label + "_physical_nulls", all(x is None for x in value["actual_physical_nulls"].values())
              and value["physical_activation"] is False and port["full_physical_consumer_activation"] is False
              and port["actual_full_native25"] is None and port["actual_T"] is None)
        return value

    full_window = {}
    for cap_value in (F(0), F(3), F(20)):
        cap, solution = native_runs[cap_value]
        full_window[str(cap_value)] = checked_consumer("full_K" + str(cap_value), cap, solution, (F(0), T))
    cap3, solution3 = native_runs[F(3)]
    first_half = checked_consumer("first_half_K3", cap3, solution3, (F(0), T / 2))
    second_half = checked_consumer("second_half_K3", cap3, solution3, (T / 2, T),
                                   first_half["source_return"]["accepted_windows"])
    full_port = full_window["3"]["source_return"]
    first_port, second_port = first_half["source_return"], second_half["source_return"]
    additive_fields = ("s", "p", "d", "parents", "selected_electrons", "selected_energy_eV_m3",
                       "ionic_charge_delta", "recipient_chemical_eV_m3")
    check("adjacent_half_window_scalar_additivity", all(
        first_port["union"][key] + second_port["union"][key] == full_port["union"][key]
        for key in additive_fields))
    check("adjacent_half_window_species_additivity", all(
        first_port[key][i] + second_port[key][i] == full_port[key][i]
        for key in ("source_ion_density_delta21", "native_source_species21",
                    "correction_to_sum_of_partition_ion_density21", "native_species_correction21")
        for i in range(21)))
    check("adjacent_half_window_normalized_birth_additivity", all(
        first_port[key] + second_port[key] == full_port[key]
        for key in ("selected_birth_zeta", "selected_birth_wnt_J_per_baryon")))
    check("adjacent_half_window_replay_ledger", second_port["accepted_windows"] == [[F(0), T / 2], [T / 2, T]])

    unique = len({row["name"] for row in checks}) == len(checks)
    passed = sum(row["passed"] for row in checks)
    status = "PASS_SCOPED_ENERGY_SUM" if unique and passed == len(checks) else "FAIL"
    certificates = {"schema": "CR_HE_ENERGY_SUM_PRIMARY_CERTIFICATES_V1", "unit": es.UNIT_ID,
                    "small_cases": small_cases, "native_atoms": atom_records(native_atoms),
                    "native_cases": native_cases, "source_pins": source_pins,
                    "certificate_scope": "CONDITIONAL_FINITE_SOURCE; actual K and exclusive kernel are null"}
    cert_meta = write_new(out / "PRIMARY_CERTIFICATES.json", certificates)
    summary = {"schema": "CR_HE_ENERGY_SUM_PRIMARY_SUMMARY_V1", "unit": es.UNIT_ID,
               "status": status, "N": total, "kinetic_coefficient_eV": kinetic,
               "native_atom_count": len(native_atoms),
               "active_atom_count": sum(a.key.startswith("active_") for a in native_atoms),
               "cutoff_ghost_count": sum(a.key == "cutoff_ghost" for a in native_atoms),
               "cutoff_energy_eV": ghost.energy_eV, "cutoff_coefficient": ghost.coefficient,
               "positive_native_atoms": positive_count, "small_case_count": len(small_cases),
               "native_case_count": len(native_cases), "native_cap_rows": cap_rows,
               "small_case_summary": small_summary, "full_window_consumers": full_window,
               "half_window_consumers_K3": [first_half, second_half], "source_pins": source_pins,
               "physical_activation": False, "actual_physical_K_eV": None,
               "full_source_physical_native25": None, "logical_checks": len(checks), "passed": passed,
               "recombination_photon_composition": "These are alternative source event returns; saved RR once, photon separately. Do not sum full and half-window alternatives."}
    summary_meta = write_new(out / "SUMMARY.json", summary)
    result = {"schema": "CR_HE_ENERGY_SUM_PRIMARY_RESULT_V1", "unit": es.UNIT_ID,
              "status": status, "logical_checks": len(checks), "passed": passed,
              "failed": len(checks) - passed, "unique_check_names": unique, "checks": checks,
              "small_cases": len(small_cases), "native_cases": len(native_cases),
              "actual_pinned_NPZ_loads": 1, "production_solve_calls": solve_calls,
              "native_consumer_calls": 5, "reference_usage": "FIXED_INPUT_DATA_ONLY; oracle and independent verifier not called",
              "source_pins": source_pins, "artifacts": {"certificates": cert_meta, "summary": summary_meta},
              "physical_activation": False, "actual_physical_nulls": {key: None for key in (
                  "K_eV", "exclusive_He_kernel", "C", "D", "outside_partner_response",
                  "projectile_donor_work", "EOS_T", "absolute_volume", "full_source_native25",
                  "global_physical_error", "global_budget_remaining", "currency")},
              "source_fit_transport_RR_photon_replays": 0, "worker_budget_measurement": None,
              "budget_accounting": "OWNED_RUN_BOUNDED_RECEIPT"}
    write_new(out / "RESULT.json", result)
    print(json.dumps({key: result[key] for key in ("status", "logical_checks", "passed", "failed")}))
    return 0 if status == "PASS_SCOPED_ENERGY_SUM" else 2


if __name__ == "__main__":
    sys.exit(main())
