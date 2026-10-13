"""New fixed-branch endpoint/certificate checks; no previous suite reruns."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import platform
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coupled_branch_solver import (as_strings, dot, exact_state, file_identity,
    ion_map, load_module, log_ratio_bounds, parameters, solve,
    stopping_map_bounds, stopping_rate_bounds, thermal_from_raw,
    thermal_temperature)


def json_fraction(value):
    if isinstance(value, Q):
        return {"exact": str(value), "decimal": float(value)}
    if isinstance(value, dict):
        return {name: json_fraction(item) for name, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_fraction(item) for item in value]
    return value


def main():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    input_path = ROOT/"examples/COUPLED_BRANCH_INPUT.json"
    inputs = json.loads(input_path.read_text())
    for record in inputs["source_files"]:
        raw = (ROOT/record["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record["sha256"]
    p = parameters(inputs)
    result = solve(inputs)
    x, s = result["x"], result["s"]
    rows = inputs["invariant_rows_exact"]
    y0 = {key: Q(value) for key, value in inputs["initial_state_exact"].items()}
    assert dot(rows["charge_over_e"], y0) == 0
    column_residuals = {kind: {name: dot(row, event["column_exact"])
                             for name, row in rows.items()}
                        for kind, event in inputs["events"].items()}
    assert all(value == 0 for values in column_residuals.values() for value in values.values())

    # Compare the reduced equations with the unchanged full shared-stock map.
    capacity_path = ROOT/"inputs/prior/inputs/prior/event_capacity_step.py"
    capacity = load_module(capacity_path, "cb_unmodified_capacity")
    lambda_lo, lambda_hi = stopping_rate_bounds(x, p, terms=8)
    lambda_mid = (lambda_lo+lambda_hi)/2
    cols = {key: {name: Q(v) for name, v in event["column_exact"].items()}
            for key, event in inputs["events"].items()}
    rates = {"ion": p["k_ion_m3_s"]*(p["X0_HI"]-x)/p["volume_m3"],
             "stop": lambda_mid}
    actual_step = capacity.capacity_step(y0, cols, rates, p["step_s"])
    assert actual_step.extents["ion"] == ion_map(x, p)
    slo, shi = stopping_map_bounds(x, p)
    assert slo <= actual_step.extents["stop"] <= shi
    assert all(dot(row, actual_step.state)-dot(row, y0) == 0 for row in rows.values())

    # Independent exact polynomial signs enclose the nonlinear ion root.
    a = p["step_s"]*p["k_ion_m3_s"]/p["volume_m3"]
    b = 1+1/p["X0_HI"]
    def polynomial(value):
        return b*a*value*value-(1+a+b*a*p["X0_HI"])*value+a*p["X0_HI"]
    xl = x-result["x_error_upper"]
    xu = x+result["x_error_upper"]
    assert 0 < xl < xu < p["x_max"]
    assert polynomial(xl) >= 0 and polynomial(xu) <= 0
    assert max(2*b*a*value-(1+a+b*a*p["X0_HI"]) for value in (xl, xu)) < 0
    exact_root_stop_lo = stopping_map_bounds(xl, p)[0]
    exact_root_stop_hi = stopping_map_bounds(xu, p)[1]
    assert s-result["s_error_upper"] <= exact_root_stop_lo <= exact_root_stop_hi <= s+result["s_error_upper"]

    # Direct raw ownership verifies the one-electron and actual-energy response.
    for xx, ss in ((Q(0), Q(0)), (p["x_max"], Q(1)), (x, s)):
        state = exact_state(inputs, xx, ss)
        therm = thermal_from_raw(inputs, state)
        assert therm["thermal_electron_count"] == p["n_e0_m3"]+xx
        assert therm["thermal_total_count"] == p["N0_thermal"]+xx
        assert therm["thermal_U_J"] == p["c_v"]*p["N0_thermal"]*p["T0_K"]+p["EV_J"]*(p["slow_daughter_eV"]*xx+p["stop_delta_eV"]*ss)
        assert therm["T_K"] == thermal_temperature(xx, ss, p)
    log_lo, log_hi = log_ratio_bounds(x, p["n_e0_m3"], terms=8)
    assert log_hi >= log_lo >= 0
    assert result["fixed_point_weighted_radius_upper"] < Q("2.154e-25")
    assert result["T_error_K_upper"] < Q("8.107e-26")

    domain = result["domain"]
    endpoint = result["thermal"]
    endpoint_cutoff = p["chi"]*p["k_B"]*endpoint["T_K"]/p["EV_J"]
    raw_nodes = [{"key": key, "W_eV_exact": value, "W_eV": float(Q(value)),
                  "count_exact": str(result["state"].get(key, Q(0))),
                  "count": float(result["state"].get(key, Q(0))),
                  "owner": "thermal_retained_trace" if key in inputs["thermal_raw_keys"] else "active"}
                 for key, value in inputs["raw_energies_eV_exact"].items()]
    sources = [file_identity(ROOT/rel) for rel in
        ("coupled_branch_solver.py", "checks/check_coupled_branch.py",
         "examples/COUPLED_BRANCH_INPUT.json", "inputs/prior/inputs/prior/event_capacity_step.py")]
    record = {
        "schema": "bass-cr-coupled-branch-checks.v1",
        "unit_id": "CR-THEORY-BRANCH-GEOMETRY-20261013", "status": "pass",
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic()-timer,
        "runtime": {"python": sys.version, "executable": sys.executable, "platform": platform.platform()},
        "files": sources, "source_input_identities_reused_and_matched": True,
        "old_suite_reruns": 0, "full_generator_built": False, "ODE_or_NCP_run": False,
        "fixture_status": inputs["state_status"], "model_scope": inputs["model_scope"],
        "domain_certificate": json_fraction(domain),
        "endpoint": json_fraction({"x": x, "s": s, **endpoint, "cutoff_eV": endpoint_cutoff,
                                     "HI_count": result["state"]["HI"], "HII_count": result["state"]["HII"]}),
        "error_certificate": json_fraction({key: result[key] for key in
            ("residual_x", "residual_s_upper", "residual_weighted_norm_upper",
             "fixed_point_weighted_radius_upper", "x_error_upper", "s_error_upper",
             "T_error_K_upper", "cutoff_error_eV_upper")}),
        "error_semantics": "Rigorous algebraic endpoint error for the declared exact finite-input collision map; not time-discretization or physical-model error",
        "log_enclosure": {"method": "positive atanh series and exact rational geometric tail",
                           "terms": 8, "width": json_fraction(log_hi-log_lo)},
        "unchanged_capacity_map_match": {"ion_extent_exact": True, "stopping_extent_in_rigorous_enclosure": True,
                                         "all_four_invariants_exact": True},
        "independent_polynomial_sign_enclosure": {"lower_sign_nonnegative": True,
                                                  "upper_sign_nonpositive": True,
                                                  "polynomial_strictly_decreasing_on_enclosure": True},
        "column_invariant_residuals": json_fraction(column_residuals),
        "endpoint_invariant_changes": json_fraction(result["invariant_changes"]),
        "initial_charge_exact": "0", "endpoint_state_nonnegative": True,
        "raw_ownership_moment_response_exact": True,
        "raw_nodes": raw_nodes,
        "iterations": {"exact_scalar_ion_updates": result["scalar_iterations"],
                       "stop_evaluation": "rigorous log enclosure at final x", "decimal_places": result["decimal_places"]},
        "source_baseline_rounding_comparison": inputs["source_rate_rounding"],
    }
    out = ROOT/"results/COUPLED_BRANCH_CHECKS.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n")
    example = {"schema": "bass-cr-coupled-branch-endpoint.v1", "state_status": inputs["state_status"],
               "initial_state_exact": inputs["initial_state_exact"],
               "endpoint_state_exact": as_strings(result["state"]),
               "thermal_physical_state_exact": as_strings(endpoint),
               "endpoint_extents_exact": {"x": str(x), "s": str(s)},
               "cutoff_eV_exact": str(endpoint_cutoff), "raw_nodes": raw_nodes,
               "certificate": "results/COUPLED_BRANCH_CHECKS.json"}
    (ROOT/"examples/COUPLED_BRANCH_ENDPOINT.json").write_text(json.dumps(example, indent=2)+"\n")
    wl = {"schema": "bass-cr-coupled-branch-wolfram-input.v1",
          "exact_parameters": as_strings({"a": a, "b": b, "X0": p["X0_HI"],
              "N0": p["N0_thermal"], "ne0": p["n_e0_m3"], "h": p["step_s"],
              "Astop": p["stop_A"], "L0": p["stop_L0"], "cv": p["c_v"],
              "epsEV": p["EV_J"], "w": p["slow_daughter_eV"], "delta": p["stop_delta_eV"],
              "T0": p["T0_K"], "chi": p["chi"], "kB": p["k_B"],
              "xmax": p["x_max"], "xhat": x, "shat": s, "qbar": domain["q_reported_bound"]}),
          "expected_numbers": {"T_K": float(endpoint["T_K"]), "x": float(x), "s": float(s),
                               "q_ion": float(domain["q_ion"]), "q_stop_weighted": float(domain["q_stop_weighted"])} }
    (ROOT/"examples/COUPLED_BRANCH_WOLFRAM_INPUT.json").write_text(json.dumps(wl, indent=2)+"\n")
    print(json.dumps({"status": "pass", "started_utc": started,
        "x": float(x), "s": float(s), "T_K": float(endpoint["T_K"]),
        "ne_m3": float(endpoint["n_e_m3"]), "cutoff_eV": float(endpoint_cutoff),
        "q_certified": float(domain["q_reported_bound"]),
        "endpoint_norm_radius_upper": float(result["fixed_point_weighted_radius_upper"]),
        "T_error_K_upper": float(result["T_error_K_upper"])}, indent=2))


if __name__ == "__main__":
    main()
