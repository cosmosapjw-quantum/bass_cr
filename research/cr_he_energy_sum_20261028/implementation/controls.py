"""Targeted rejection/acceptance controls; run only through run_bounded.py.

One pinned actual NPZ load and one K=3 native plan are shared by this process.
The neutral-inventory rejection is a labelled algebraic fixture of the pinned
consumer, not an assertion that the retained 3201-atom source is depleted.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import sys

import energy_sum as es


def main():
    out = Path(sys.argv[1])
    unit = Path(__file__).resolve().parents[1]
    repo = unit.parents[1]
    rows = []

    def reject(name, scope, reason, action, details=None):
        row = {"name": name, "scope": scope, "kind": "REJECTION",
               "expected_exception_category": "ValueError", "expected_reason": reason}
        if details is not None:
            row["details"] = details
        try:
            returned = action()
            row.update(passed=False, actual_exception_category=None,
                       actual_reason=None, unexpected_return_type=type(returned).__name__)
        except Exception as error:
            row.update(passed=type(error) is ValueError and str(error) == reason,
                       actual_exception_category=type(error).__name__, actual_reason=str(error))
        rows.append(row)

    def accept(name, scope, action, predicate, details=None):
        row = {"name": name, "scope": scope, "kind": "ACCEPTANCE"}
        if details is not None:
            row["details"] = details
        try:
            returned = action()
            row.update(passed=predicate(returned) is True,
                       actual_exception_category=None, actual_reason=None)
        except Exception as error:
            row.update(passed=False, actual_exception_category=type(error).__name__,
                       actual_reason=str(error))
        rows.append(row)

    core = "GENERAL_EXACT_FINITE_ATOM_CORE"
    atoms = (es.Atom("low", F(1), F(2), 1), es.Atom("high", F(3), F(2), 2))
    cap_value = F(4)
    solved = es.solve(atoms, cap_value)
    edge = solved.max_events[0]
    bad_scalars = (("bool", True), ("float", 3.0), ("string", "3"),
                   ("nan", float("nan")), ("inf", float("inf")))
    for label, value in bad_scalars:
        reject("cap_scalar_" + label, core, "EXACT_INT_OR_FRACTION_REQUIRED",
               lambda value=value: es.solve(atoms, value))
        for field in ("energy_eV", "coefficient"):
            reject(field + "_scalar_" + label, core, "EXACT_INT_OR_FRACTION_REQUIRED",
                   lambda field=field, value=value: es.solve(
                       (replace(atoms[0], **{field: value}), atoms[1]), cap_value))
    reject("negative_cap", core, "NONNEGATIVE_ENERGY_CAP_REQUIRED", lambda: es.solve(atoms, F(-1)))
    for field in ("energy_eV", "coefficient"):
        reject("negative_" + field, core, "NONNEGATIVE_ATOM_DATA_REQUIRED",
               lambda field=field: es.solve((replace(atoms[0], **{field: F(-1)}), atoms[1]), cap_value))
    reject("duplicate_atom_keys", core, "DUPLICATE_ATOM_KEY",
           lambda: es.solve((atoms[0], replace(atoms[1], key="low")), cap_value))
    reject("empty_atom_key", core, "NONEMPTY_ATOM_KEY_REQUIRED",
           lambda: es.solve((replace(atoms[0], key=""),), cap_value))
    for label, value in (("bool", True), ("float", 1.0), ("negative", -1)):
        reject("partition_" + label, core, "NONNEGATIVE_INTEGER_PARTITION_REQUIRED",
               lambda value=value: es.solve((replace(atoms[0], partition=value),), cap_value))
    reject("untyped_atom_record", core, "TYPED_GENERAL_ATOM_REQUIRED",
           lambda: es.solve(({"key": "untyped"},), cap_value))
    reject("nonsequence_atom_declaration", core, "FINITE_ATOM_SEQUENCE_REQUIRED",
           lambda: es.solve(iter(atoms), cap_value))
    reject("negative_target", core, "TARGET_DOUBLE_OUTSIDE_EXACT_INTERVAL",
           lambda: es.solve(atoms, cap_value, target_d=F(-1)))
    reject("target_above_exact_maximum", core, "TARGET_DOUBLE_OUTSIDE_EXACT_INTERVAL",
           lambda: es.solve(atoms, cap_value, target_d=F(3)))
    reject("inexact_target", core, "EXACT_INT_OR_FRACTION_REQUIRED",
           lambda: es.solve(atoms, cap_value, target_d=1.0))

    checker = "EXPLICIT_PRIMAL_DUAL_CERTIFICATE_CHECKER"
    reject("maximum_event_removed", checker, "EXACT_ATOM_MARGINAL_MISMATCH",
           lambda: es.verify(atoms, replace(solved, max_events=())))
    reject("chosen_event_removed", checker, "EXACT_ATOM_MARGINAL_MISMATCH",
           lambda: es.verify(atoms, replace(solved, events=())))
    reject("forbidden_high_diagonal", checker, "PAIR_ENERGY_SUPPORT_VIOLATION",
           lambda: es.verify(atoms, replace(solved, max_events=(replace(edge, electrons=("high", "high")),))))
    reject("forged_dual_violates_low_loop", checker, "DUAL_PAIR_OR_LOOP_INFEASIBLE",
           lambda: es.verify(atoms, replace(solved, dual=(("low", F(0)), ("high", F(1, 2))))))
    reject("changed_atom_digest", checker, "SOLUTION_ATOM_IDENTITY_MISMATCH",
           lambda: es.verify(atoms, replace(solved, atom_content_sha256="0" * 64)))
    reject("changed_input_weight", checker, "SOLUTION_ATOM_IDENTITY_MISMATCH",
           lambda: es.verify((replace(atoms[0], coefficient=F(3)), atoms[1]), solved))
    reject("forged_total_counter", checker, "SOLUTION_MASS_COUNTER_MISMATCH",
           lambda: es.verify(atoms, replace(solved, N=F(5))))
    reject("forged_low_counter", checker, "SOLUTION_MASS_COUNTER_MISMATCH",
           lambda: es.verify(atoms, replace(solved, low_mass=F(3))))
    reject("forged_dmax", checker, "SOLUTION_OBJECTIVE_IDENTITY_MISMATCH",
           lambda: es.verify(atoms, replace(solved, dmax=F(3))))
    reject("chosen_target_counter_mismatch", checker, "TARGET_DOUBLE_MISMATCH",
           lambda: es.verify(atoms, replace(solved, target_d=F(1))))
    reject("untyped_solution", checker, "TYPED_ENERGY_SOLUTION_REQUIRED",
           lambda: es.verify(atoms, {}))
    reject("untyped_event_record", checker, "TYPED_ENERGY_EVENT_REQUIRED",
           lambda: es.verify(atoms, replace(solved, max_events=({},))))
    reject("mutable_event_sequence", checker, "IMMUTABLE_EVENT_TUPLE_REQUIRED",
           lambda: es.verify(atoms, replace(solved, events=list(solved.events))))
    reject("duplicate_event_ids", checker, "DUPLICATE_EVENT_ID",
           lambda: es.verify(atoms, replace(solved, max_events=(
               replace(edge, coefficient=F(1)), replace(edge, coefficient=F(1))))))
    reject("zero_event_coefficient", checker, "POSITIVE_EVENT_WEIGHT_REQUIRED",
           lambda: es.verify(atoms, replace(solved, max_events=(replace(edge, coefficient=F(0)),))))
    reject("mutable_event_legs", checker, "EVENT_LEG_SUPPORT_MISMATCH",
           lambda: es.verify(atoms, replace(solved, max_events=(replace(edge, electrons=["low", "high"]),))))
    reject("missing_dual_atom", checker, "DUAL_ATOM_SET_MISMATCH",
           lambda: es.verify(atoms, replace(solved, dual=(("low", F(1, 2)),))))
    reject("inexact_dual_scalar", checker, "EXACT_INT_OR_FRACTION_REQUIRED",
           lambda: es.verify(atoms, replace(solved, dual=(("low", 0.5), ("high", F(1, 2))))))
    reject("spurious_zero_deficit_threshold", checker, "ZERO_DEFICIT_THRESHOLD_MUST_BE_NULL",
           lambda: es.verify(atoms, replace(solved, threshold_h_eV=F(3))))
    accept("empty_exact_problem", core, lambda: es.verify((), es.solve((), F(0))),
           lambda value: value["dmax"] == 0 and value["maximum"]["event_records"] == 0)
    zero_atoms = (es.Atom("zero", F(0), F(0), 0),)
    accept("zero_mass_zero_cap", core, lambda: es.verify(zero_atoms, es.solve(zero_atoms, F(0))),
           lambda value: value["dmax"] == 0 and value["chosen"]["event_records"] == 0)
    accept("intermediate_target", core,
           lambda: es.verify(atoms, es.solve(atoms, cap_value, target_d=F(1))),
           lambda value: value["dmax"] == 2 and value["target_d"] == 1
           and value["chosen"]["single"] == 2 and value["primal_dual_gap"] == 0)

    manifest_path = unit / "inputs/INPUT_MANIFEST.json"
    manifest_raw = manifest_path.read_bytes()
    inputs = {row["path"]: row for row in json.loads(manifest_raw)["files"]}
    npz_relative = "research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz"
    canonical_relative = "research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json"
    predecessor_relative = "research/cr_he_event_union_20261028/implementation/event_union.py"
    source = es.load_native(repo / npz_relative)
    previous = es._native_module()
    native_cap = es.bind_cap(source, F(3), "Conditional cumulative Ea+Eb<=3 eV guard-control assumption; actual K remains null.")
    native_solution = es.native_plan(source, native_cap)
    source_pins = {"npz_path_relative_to_repo": npz_relative,
                   "npz_sha256": source.attribution_npz_sha256,
                   "npz_byte_identity_verified_by_pinned_loader": True,
                   "canonical_source_path_relative_to_repo": canonical_relative,
                   "canonical_source_sha256": source.canonical_source_sha256,
                   "canonical_source_identity_basis": "PINNED_PREDECESSOR_AND_INPUT_MANIFEST_REUSE",
                   "predecessor_module_path_relative_to_repo": predecessor_relative,
                   "predecessor_module_sha256": es.PREDECESSOR_SHA,
                   "atom_content_sha256": source.atom_content_sha256,
                   "unit_input_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
                   "native_atom_count": len(source.atoms)}
    accept("manifest_source_pins", "PINNED_INPUT_IDENTITY",
           lambda: (inputs[npz_relative]["sha256"] == source.attribution_npz_sha256
                    and inputs[canonical_relative]["sha256"] == source.canonical_source_sha256
                    and inputs[predecessor_relative]["sha256"] == es.PREDECESSOR_SHA
                    and len(source.atoms) == 3201), lambda value: value is True)
    cap_scope = "ATTESTED_SOURCE_CONDITIONAL_CAP_BINDING"
    reject("cap_empty_assumption", cap_scope, "EXPLICIT_CONDITIONAL_ASSUMPTION_REQUIRED",
           lambda: es.bind_cap(source, F(3), "  "))
    missing_assumption = {key: value for key, value in native_cap.items() if key != "assumption"}
    reject("cap_missing_assumption_field", cap_scope, "TYPED_CONDITIONAL_CAP_BINDING_REQUIRED",
           lambda: es.validate_cap(source, missing_assumption))
    cap_mutations = (("K_eV", F(4)), ("canonical_source_sha256", "0" * 64),
                     ("atom_content_sha256", "0" * 64), ("attribution_npz_sha256", "0" * 64),
                     ("state_id", "FOREIGN_STATE"), ("digest", "0" * 64),
                     ("energy_unit", "keV"), ("actual_physical_K_eV", F(3)),
                     ("unit", "FOREIGN_UNIT"))
    for field, value in cap_mutations:
        reject("cap_tampered_" + field, cap_scope, "CONDITIONAL_CAP_BINDING_IDENTITY_MISMATCH",
               lambda field=field, value=value: es.validate_cap(source, dict(native_cap, **{field: value})))

    # For b=1/(N+1), N*b^2 <=1/4.  Both adjacent windows have
    # parent exposure <=3/8, below retained H_neutral=1085/94*99/100.
    step = F(1) / (native_solution.N + 1)
    window = (F(0), step)
    binding = previous.binding(window, source)
    alternate_cap = es.bind_cap(source, F(4), "Separate conditional cap for stale-solution rejection only.")
    reject("solution_from_different_cap", cap_scope, "SOLUTION_CAP_BINDING_MISMATCH",
           lambda: es.consume_native(source, alternate_cap, native_solution, window))

    fixture = previous.fixture_source((previous.Atom("guard_fixture", F(1), F(1), 1),))
    reject("fixture_cannot_enter_attested_native_adapter", cap_scope, "ATTESTED_COMPLETE_PHYS02_SOURCE_REQUIRED",
           lambda: es.bind_cap(fixture, F(2), "Synthetic fixture must not acquire actual source provenance."))

    port_scope = "NATIVE_ADAPTER_WITH_UNCHANGED_SAME_STATE_BINDING"
    bound_mutations = (
        ("state", "state_id", "FOREIGN_STATE", "SAME_STATE_REQUIRED"),
        ("window", "window", (F(0), 2 * step), "EXPLICIT_WINDOW_BINDING_MISMATCH"),
        ("source", "source_sha256", "0" * 64, "SOURCE_BINDING_IDENTITY_MISMATCH"),
        ("support", "support_eV", (F(0), F(10)), "NATIVE_SUPPORT_EXTENSION_REFUSED"),
        ("frame", "frame", "unbound_lab_frame", "MIXED_FRAME_REFUSED"),
        ("clock", "clock", "coordinate_s", "PROPER_CLOCK_REQUIRED"),
        ("volume_mode", "proper_volume_mode", "expanding", "FIXED_DENSITY_SCOPE_REQUIRED"),
        ("absolute_volume", "absolute_proper_volume_m3", F(1), "FIXED_DENSITY_SCOPE_REQUIRED"))
    for name, field, value, reason in bound_mutations:
        reject("explicit_binding_" + name, port_scope, reason,
               lambda field=field, value=value: es.consume_native(
                   source, native_cap, native_solution, window, bound=dict(binding, **{field: value})))
    reject("wrong_same_state_nb", port_scope, "EXPLICIT_SAME_STATE_NB_REQUIRED",
           lambda: es.consume_native(source, native_cap, native_solution, window, nb_m3=F(1)))
    reject("missing_explicit_nb", port_scope, "EXACT_INT_OR_FRACTION_REQUIRED",
           lambda: es.consume_native(source, native_cap, native_solution, window, nb_m3=None))
    reject("inexact_nb", port_scope, "EXACT_INT_OR_FRACTION_REQUIRED",
           lambda: es.consume_native(source, native_cap, native_solution, window, nb_m3=float(es.NB)))
    reject("overlapping_previous_window", port_scope, "OVERLAPPING_TIME_RETURN_OR_REPLAY_REFUSED",
           lambda: es.consume_native(source, native_cap, native_solution, window, previous_windows=(window,)))
    reject("history_before_known_start", port_scope, "FINITE_KNOWN_PROPER_HISTORY_REQUIRED",
           lambda: es.consume_native(source, native_cap, native_solution, (F(-1), F(1))))
    reject("history_after_known_end", port_scope, "FINITE_KNOWN_PROPER_HISTORY_REQUIRED",
           lambda: es.consume_native(source, native_cap, native_solution, (F(0), previous.T + 1)))

    def adjacent_windows():
        first = es.consume_native(source, native_cap, native_solution, window)
        second = es.consume_native(source, native_cap, native_solution, (step, 2 * step),
                                   previous_windows=first["source_return"]["accepted_windows"])
        return {"accepted": second["source_return"]["accepted_windows"],
                "first_factor": first["proper_window_factor_s2"],
                "second_factor": second["proper_window_factor_s2"],
                "actual_K_is_null": second["actual_physical_nulls"]["K_eV"] is None}

    accept("adjacent_windows_are_not_replay", port_scope, adjacent_windows,
           lambda value: value["accepted"] == [[F(0), step], [step, 2 * step]]
           and value["second_factor"] == 3 * value["first_factor"] and value["actual_K_is_null"],
           {"first_window": window, "second_window": (step, 2 * step),
            "inventory_safety_basis": "For b=1/(N+1), both window parent exposures <=3/8 < H_neutral."})

    def depleted_fixture():
        fixture_events = previous.single_lift(fixture.atoms)
        fixture_binding = previous.binding((F(0), F(10)), fixture)
        fixture_claims = previous.claims_by_partition(fixture_events, fixture, fixture_binding)
        return previous.consume_event_union(fixture_claims, fixture, nb_m3=es.NB)

    reject("synthetic_neutral_inventory_exhaustion", "PINNED_CONSUMER_ALGEBRAIC_FIXTURE_ONLY",
           "CONDITIONAL_NEUTRAL_INVENTORY_EXHAUSTED", depleted_fixture,
           {"input_kind": "ALGEBRAIC_FIXTURE", "energy_eV": F(1), "coefficient": F(1),
            "conditional_fixture_K_eV": F(2), "events": "single only; pair cap imposes no further restriction",
            "proper_window_s": (F(0), F(10)), "parent_density_m3": F(50),
            "neutral_inventory_m3": F(1085, 94) * F(99, 100),
            "actual_3201_source_depletion_claim": False})

    names = [row["name"] for row in rows]
    distinct = len(names) == len(set(names))
    passed = sum(row["passed"] for row in rows)
    result = {"schema": "CR_HE_ENERGY_SUM_CONTROLS_V1", "unit": es.UNIT_ID,
              "status": "PASS_SCOPED_ENERGY_SUM" if distinct and passed == len(rows) else "FAIL",
              "logical_controls": len(rows), "passed": passed, "failed": len(rows) - passed,
              "unique_control_names": distinct, "source_pins": source_pins,
              "actual_pinned_NPZ_loads": 1, "native_plan_count": 1,
              "native_sample_cap_eV": F(3), "native_sample_cap_scope": "EXPLICIT_CONDITIONAL_ASSUMPTION",
              "controls": rows, "physical_activation": False,
              "actual_physical_nulls": {name: None for name in (
                  "K_eV", "exclusive_He_kernel", "C", "D", "outside_partner_response",
                  "projectile_donor_work", "EOS_T", "absolute_volume", "full_source_native25",
                  "global_physical_error", "global_budget_remaining", "currency")},
              "worker_budget_measurement": None, "budget_accounting": "OWNED_RUN_BOUNDED_RECEIPT",
              "source_fit_transport_RR_photon_replays": 0}
    raw = json.dumps(es.serial(result), indent=2, allow_nan=False) + "\n"
    with (out / "RESULT.json").open("x") as stream:
        stream.write(raw)
    print(json.dumps({key: result[key] for key in ("status", "logical_controls", "passed", "failed")}))
    return 0 if result["status"] == "PASS_SCOPED_ENERGY_SUM" else 2


if __name__ == "__main__":
    sys.exit(main())
