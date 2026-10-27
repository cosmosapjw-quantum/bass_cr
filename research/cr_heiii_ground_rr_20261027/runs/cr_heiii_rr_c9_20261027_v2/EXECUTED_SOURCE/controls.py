"""36 controls for the changed HeIII consumer and integrated return.

Only tiny analytic fixtures and newly admitted HeII point evaluations run here.
The 31 historical HeI controls and historical primary solves are not replayed.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import resource
import time

import numpy as np

import dispatch
import engine as e
import export_adapter as export


def rejected(call, expected=ValueError, text=None):
    try:
        call()
    except expected as error:
        if text is not None:
            e.need(text in str(error), "WRONG_REJECTION_REASON:" + str(error))
        return str(error)
    raise AssertionError("EXPECTED_REJECTION_NOT_OBSERVED")


def fixture():
    energy = np.array([1.0, 10.0])
    first = np.array([[.2, .3, 1.0, 1.0, 2.0, 3.0]])
    baths = np.array([[9.0, 0, 0, 0, 0, 0]])
    h, he = np.array([.05]), np.array([.04])
    d0 = np.array([1.0 + .2 + .3 + .05 + .04])
    physical = np.column_stack((first, h, h * 10, he, he * 10, baths))
    old_solution = physical / d0[:, None]  # exact analytic one-state construction, not an old solver
    base = {"E_eV": energy, "K_diag": np.array([1.5]),
            "K_lower": np.empty(0), "K_upper": np.empty(0),
            "rhs_first6": first, "rhs_bath6": baths,
            "source_toy": np.array([0.0, 2.0]), "active_mask_toy": np.array([True, False])}
    old = {"E_eV": energy, "K_diag": d0, "K_lower": np.empty(0), "K_upper": np.empty(0),
           "rhs_physical16": physical, "lambda_H1": h, "lambda_He": he,
           "u_s": old_solution[:, 0], "u_p": old_solution[:, 1],
           "t": old_solution[:, 3], "p_H1": old_solution[:, 6], "p_He": old_solution[:, 8]}
    source = {"W_eV": np.array([10.0, .5]), "pulse_count_cm3": np.array([2.0, 3.0])}
    return base, old, source


def run(unit, out, runid):
    started = time.process_time()
    checks, fixture_rhs = [], 0

    def test(name, action):
        try:
            detail = action()
            checks.append({"name": name, "pass_scoped": True, "detail": detail})
        except Exception as error:
            checks.append({"name": name, "pass_scoped": False,
                           "error": {"type": type(error).__name__, "message": str(error)}})

    def require(condition):
        e.need(bool(condition), "CONTROL_ASSERTION")
        return "PASS"

    def count(n):
        nonlocal fixture_rhs
        fixture_rhs += n

    try:
        c = e.verify(unit)
        dispatch.authorize_run(unit, c, "controls", runid)

        def runtime_resources():
            # NumPy/SciPy were imported by engine above; inspect their actual pools.
            from threadpoolctl import threadpool_info
            pools = threadpool_info()
            affinity = sorted(os.sched_getaffinity(0))
            address_limits = list(resource.getrlimit(resource.RLIMIT_AS))
            native_env = {key: os.environ.get(key) for key in dispatch.THREADS}
            omp_env = {key: os.environ.get(key) for key in dispatch.OMP_CONTROLS}
            conditions = {
                "worker_affinity_is_CPU0": affinity == [0],
                "address_limits_are_512MiB": address_limits == [512 * 1024**2] * 2,
                "all_native_thread_env_are_one": all(value == "1" for value in native_env.values()),
                "openmp_dynamic_and_nested_disabled": omp_env == dispatch.OMP_CONTROLS,
                "threadpools_observed_after_numpy_scipy_import": bool(pools),
                "all_observed_threadpools_are_one": bool(pools) and all(pool.get("num_threads") == 1 for pool in pools),
            }
            record = {"schema": "CR_HEIII_WORKER_RUNTIME_RESOURCE_READBACK_V1",
                "status": "PASS" if all(conditions.values()) else "FAILED_RETAINED",
                "affinity": affinity, "RLIMIT_AS_soft_hard_bytes": address_limits,
                "native_thread_environment": native_env, "openmp_controls": omp_env,
                "threadpool_info": pools, "process_memory": dispatch.process_memory_snapshot(),
                "checks": conditions, "science_started_before_this_readback": False}
            e.writej(out / "WORKER_RUNTIME_RESOURCE_READBACK.json", record)
            require(all(conditions.values()))
            return record

        test("worker_runtime_resource_readback", runtime_resources)
        if not checks[-1]["pass_scoped"]:
            e.writej(out / "CONTROL_RESULTS.json", {
                "schema": "CR_HEIII_CHANGED_CONTROLS_V1", "checks": checks,
                "status": "FAILED_RETAINED_BEFORE_SCIENCE", "historical_31_controls_replayed": 0,
                "new_toy_consume_RHS_attempted": 0})
            raise RuntimeError("WORKER_RUNTIME_RESOURCE_READBACK_FAILED")

        atom = e.provider(unit)
        q = e.source_qualification(unit, c)
        base, old, src = fixture()
        new, metrics, valid = e.consume(base, old, c, atom, count)
        sample = e.coefficients(np.array([.1, 1.0, 10.0, 100.0]), c, atom, .01)

        def mutant_config(key, value):
            changed = deepcopy(c)
            changed[key] = value
            return e.validate_config(changed)

        def mutant_event(event, change):
            altered = deepcopy(event)
            change(altered)
            return export.validate_event(altered)

        def event(*, n=1.25, u=2.5, nb=None, qualification=q, frame=export.FRAME):
            return export.integrated_event(input_id=c["input_id"], case="analytic-C6", z="2.316",
                count_cm3=n, kinetic_eV_cm3=u, frame=frame, source_qualification=qualification, nb_m3=nb)

        positive = event(nb=2.5e6)
        without_nb = event()
        zero = event(n=0.0, u=0.0)
        test("native_HeII_row_and_positive_points", lambda: require(
            atom.channel == "HeII" and atom.threshold_eV == 54.42 and atom.maximum_eV == 50000
            and all(np.all(sample[key] > 0) for key in sample)))
        test("capturing_HeIII_density_not_electron_density", lambda:
             rejected(lambda: mutant_config("n_HeIII_cm3", .14), text="n_HeIII_cm3"))
        test("HeII_d1_statistical_convention", lambda:
             rejected(lambda: mutant_config("d_HeII", 4), text="d_HeII"))
        test("new_hazard_density_linear", lambda: require(np.allclose(
            e.coefficients([.1, 1, 10, 100], c, atom, .02)["lambda_HeII"],
            2 * sample["lambda_HeII"], rtol=2e-15, atol=0)))

        def zero_hazard():
            zc = deepcopy(c)
            zc["n_HeIII_cm3"] = 0.0
            zn, zm, passed = e.consume(base, old, zc, atom, count)
            row = e.source_average(base, old, zn, src, "toy", zc)
            require(passed and np.all(zn["lambda_HeII"] == 0) and np.all(zn["p_HeII"] == 0)
                    and np.all(zn["solution_response4"] == 0) and np.all(zn["w"] == 0)
                    and row["conditional_HeII_RR_time_s"] is None
                    and row["conditional_HeII_RR_kinetic_eV"] is None)
            return {"capture_count": row["expected_HeII_events_cm3"], "conditional": None}

        test("zero_target_hazard_and_null_conditionals", zero_hazard)

        def invalid_densities():
            return [rejected(lambda x=value: e.coefficients([1.0], c, atom, x))
                    for value in (None, True, -.01, float("nan"), float("inf"))]

        test("missing_boolean_signed_nonfinite_density_rejected", invalid_densities)
        test("invalid_kinetic_domains_rejected", lambda: [
            rejected(lambda x=value: e.coefficients(x, c, atom, .01))
            for value in ([0.0], [-1.0], [float("nan")], [float("inf")], [True], [True, 1], [], [[1.0]], [None])])
        test("native_PI_support_not_extended", lambda:
             rejected(lambda: e.coefficients([50000.0], c, atom, .01), text="FINITE_PI_SUPPORT"))
        test("physical18_insertion_and_bath_slice", lambda: require(
            valid and new["rhs_physical18"].shape == (1, 18)
            and np.array_equal(new["rhs_physical18"][:, :10], old["rhs_physical16"][:, :10])
            and np.array_equal(new["rhs_physical18"][:, 12:18], old["rhs_physical16"][:, 10:16])
            and np.array_equal(new["rhs_physical18"][:, 10], new["lambda_HeII"])))
        test("conditional5_uses_shared_new_probabilities", lambda: require(np.array_equal(
            new["rhs_conditional5"], new["solution_physical18"][:, [0, 1, 6, 8, 10]])))
        test("stable4_uses_exact_stored_HeI_columns", lambda: require(np.array_equal(
            new["rhs_response4"], -new["lambda_HeII"][:, None]
            * np.column_stack((old["u_s"] + old["u_p"], old["t"], old["p_H1"], old["p_He"])))))

        def shared_three():
            old_rate, added = 1.59, .7
            hazards = np.array([[.05, .04, added]])
            values, residuals = e.solve(np.array([old_rate + added]), np.empty(0), np.empty(0), hazards)
            require(np.allclose(values, hazards / (old_rate + added), rtol=2e-15, atol=0)
                    and max(residuals) <= 2e-12)
            return {"probabilities": values[0].tolist(), "shared_denominator": old_rate + added}

        test("three_RR_share_one_competing_operator", shared_three)
        test("disjoint_RR_probability_sum_is_detectably_wrong", lambda: require(
            abs(.7 / (1.5 + .7) - .7 / (1.5 + .05 + .04 + .7)) > 1e-3))
        test("four_stored_column_responses_nonpositive", lambda: require(np.all(new["solution_response4"] <= 0)))
        test("single_added_hazard_two_sided_bound", lambda: require(
            np.all(new["w"] / (1 + new["w"].max()) <= new["p_HeII"] * (1 + 5e-10))
            and np.all(new["p_HeII"] <= new["w"] * (1 + 5e-10))))
        test("strict_positive_Thomas_pivot_rejection", lambda: rejected(lambda:
            e.solve(np.array([1., 1.]), np.array([-2.]), np.array([-2.]), np.ones(2)),
            text="STRICT_POSITIVE_THOMAS_PIVOT"))
        test("Z_matrix_sign_rejection", lambda: rejected(lambda:
            e.solve(np.array([2., 2.]), np.array([.1]), np.array([-.1]), np.ones(2)),
            text="VALID_Z_MATRIX"))

        def own_residual():
            rhs = np.array([[1e-60, 1e60], [2e-60, 2e60]])
            _, values = e.solve(np.array([2., 2.]), np.array([-1.]), np.array([-1.]), rhs)
            require(len(values) == 2 and max(values) <= 2e-12)
            return {"own_column_scaled_backward": values, "column_scale_ratio": 1e120}

        test("backward_residual_each_column_own_scale", own_residual)
        test("three_binding_energies_and_final_reward_ownership", lambda: require(
            metrics["energy_scaled_residual"] <= 2e-8
            and max(metrics["RR_own_energy_residuals"].values()) <= 5e-13
            and e.source_average(base, old, new, src, "toy", c)["ledger"]["scaled_residual"] <= 2e-8
            and all(np.allclose(new["photon_" + name] + new["internal_" + name], new["r_" + name],
                                rtol=5e-13, atol=0) for name in ("H1", "HeI", "HeII"))))

        def positive_native():
            delta = positive["native25"]["delta"]
            require(positive["integrated_count_m3"] == 1.25e6
                    and positive["density_delta_m3"] == {"He4:2": -1.25e6, "He4:1": 1.25e6,
                                                         "e:fast": -1.25e6, "photon": 1.25e6}
                    and delta[11] == .5 and delta[12] == -.5 and delta[21] == -.5
                    and math.isclose(delta[22], -export.EV_J, rel_tol=2e-13, abs_tol=0)
                    and delta[23] == delta[24] == 0
                    and all(delta[j] == 0 for j in range(25) if j not in (11, 12, 21, 22)))
            validation = export.validate_event(positive)
            e.writej(out / "NATIVE25_POSITIVE_NB_CONTROL.json", {
                "schema": "CR_HEIII_POSITIVE_NB_CONTROL_V1", "status": "PASS",
                "input": {"count_cm3": 1.25, "kinetic_eV_cm3": 2.5, "nb_m3": 2.5e6},
                "event": positive, "validation": validation})
            return validation

        test("SI_and_native25_explicit_positive_nb", positive_native)
        test("no_implicit_nb_rate_or_heating", lambda: require(
            without_nb["native25"] is None and without_nb["retained_photon_port"]["count_per_baryon"] is None
            and without_nb["retained_photon_port"]["energy_J_per_baryon"] is None
            and all(without_nb[k] is None for k in ("event_rate_m3_s", "exposure_s", "instantaneous_rhs", "physical_heating_J_m3"))
            and without_nb["irreversible_assimilation"] is False))
        test("zero_integrated_counterpart_is_explicit", lambda: require(
            zero["integrated_count_m3"] == 0 and all(v == 0 for v in zero["integrated_energy_J_m3"].values())
            and zero["per_event_template"]["conditional_mean_kinetic_eV"] is None))
        test("signed_nonfinite_integrated_moments_rejected", lambda: [
            rejected(lambda v=value: event(n=v)) for value in (-1, True, float("nan"), float("inf"))])

        def duplicate():
            book = export.IntegratedBook(export.FRAME, case="analytic-C6", z="2.316")
            book.append(positive)
            return rejected(lambda: book.append(positive), export.ExportError, "DUPLICATE_CANONICAL_INTEGRATED_EVENT")

        test("integrated_duplicate_event_id_rejected", duplicate)

        def cross_frame():
            book = export.IntegratedBook(export.FRAME, case="analytic-C6", z="2.316")
            altered = deepcopy(positive)
            altered["frame"] = "unadmitted_comoving_frame"
            return rejected(lambda: book.append(altered), export.ExportError, "INTEGRATED_BOOK_FRAME_MISMATCH")

        test("integrated_cross_frame_rejected", cross_frame)
        test("source_provider_pin_mismatch_rejected", lambda: rejected(lambda:
            event(qualification={**q, "provider_sha256": "0" * 64}), export.ExportError, "SOURCE_QUALIFICATION"))
        test("missing_theory_review_pin_rejected", lambda: rejected(lambda:
            event(qualification={k: v for k, v in q.items() if k != "review_sha256"}),
            export.ExportError, "SOURCE_REVIEW_PIN_REQUIRED"))
        test("retained_photon_not_native_w_ext", lambda: rejected(lambda:
            mutant_event(positive, lambda value: value["native25"]["delta"].__setitem__(23, 1.0)),
            export.ExportError, "NATIVE25_INTEGRATED_PROJECTION"))
        test("integrated_energy_mismatch_rejected", lambda: rejected(lambda:
            mutant_event(positive, lambda value: value["integrated_energy_J_m3"].__setitem__("radiation", 0.0)),
            export.ExportError, "ENERGY_CLOSURE"))
        test("pulse_count_not_event_rate", lambda: rejected(lambda:
            mutant_event(positive, lambda value: value.__setitem__("event_rate_m3_s", value["integrated_count_m3"])),
            export.ExportError, "INTEGRATED_NOT_RATE_OR_HEATING"))
        test("invalid_explicit_nb_rejected", lambda: [rejected(lambda v=value: event(nb=v), export.ExportError)
             for value in (0, -1, True, float("nan"), float("inf"))])
        test("nonzero_energy_with_zero_count_rejected", lambda:
             rejected(lambda: event(n=0.0, u=1.0), export.ExportError, "ZERO_COUNTERPART_REQUIRED"))

        def missing_budget():
            root = out / "budget_missing_fixture"
            (root / "attempt").mkdir(parents=True)
            return rejected(lambda: dispatch.prior_attempts(root), RuntimeError, "UNKNOWN_PRIOR_ATTEMPT_BUDGET")

        test("prior_attempt_missing_receipt_is_unknown", missing_budget)

        def invalid_budget():
            messages = []
            for index, value in enumerate((None, True, -1, float("nan"), float("inf"))):
                root = out / ("budget_invalid_fixture_" + str(index))
                directory = root / "attempt"
                directory.mkdir(parents=True)
                # JSON nonfinite tokens here are deliberate invalid-input fixtures.
                (directory / "DISPATCH_RECEIPT.json").write_text(json.dumps({
                    "run_id": "attempt", "mode": "primary", "worker_cpu_s": value, "coordinator_cpu_s": 0.0}))
                messages.append(rejected(lambda p=root: dispatch.prior_attempts(p), RuntimeError,
                                         "UNKNOWN_PRIOR_ATTEMPT_BUDGET"))
            return messages

        test("prior_attempt_boolean_negative_nonfinite_cost_is_unknown", invalid_budget)

        def lease_exclusive():
            lease = out / "control_owned_lease"
            dispatch.acquire_lease(lease, {"run_id": "control_owner"})
            try:
                return rejected(lambda: dispatch.acquire_lease(lease, {"run_id": "second"}), FileExistsError)
            finally:
                lease.unlink()

        test("task_lease_is_create_only", lease_exclusive)
        e.need(len(checks) == 36, "EXPECTED_36_CHANGED_CONTROLS")
        e.writej(out / "CONTROL_RESULTS.json", {
            "schema": "CR_HEIII_CHANGED_CONTROLS_V1", "checks": checks,
            "historical_31_controls_replayed": 0,
            "new_toy_consume_RHS_attempted": fixture_rhs,
            "additional_tiny_analytic_RHS_solved": 5,
            "invalid_operator_solve_requests_rejected": 2,
            "positive_nb_evidence": "NATIVE25_POSITIVE_NB_CONTROL.json"})
        passed = all(row["pass_scoped"] for row in checks)
        result = {"schema": "CR_HEIII_CONTROLS_RESULT_V1", "status": "PASS" if passed else "FAILED_RETAINED",
                  "run_id": runid, "changed_controls": len(checks),
                  "passed_controls": sum(row["pass_scoped"] for row in checks),
                  "failures": [row for row in checks if not row["pass_scoped"]],
                  "old_primary_replay": 0, "old_generator_calls": 0,
                  "old_source_projection_calls": 0, "source_quadrature": 0,
                  "thermal_rate_quadrature": 0, "new_ODE": 0,
                  "process_cpu_s": time.process_time() - started,
                  "physical_heating": None, "N6": "PREDECESSOR_GATED", "N7": "PREDECESSOR_GATED"}
        e.writej(out / "RESULT.json", result)
        print(json.dumps(result))
        return 0 if passed else 1
    except Exception as error:
        e.writej(out / "FAILURE.json", {"status": "FAILED_RETAINED", "type": type(error).__name__,
            "message": str(error), "completed_checks": checks, "toy_consume_RHS_attempted": fixture_rhs,
            "process_cpu_s": time.process_time() - started})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit.resolve(), args.output.resolve(), args.run_id))
