"""Focused exact-rational checks for the constructive reaction map."""
from pathlib import Path
import hashlib
import json
import sys
import time
from fractions import Fraction as Q

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from event_capacity_step import (
    build_h_he_family, column_invariant_residuals, base_mass_action_proposals,
    capacity_step, dot_state, temperature, thermal_count,
)

start = time.perf_counter()
checks = []

def record(key, passed, detail):
    checks.append({"id": key, "pass": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(key)

family = build_h_he_family(
    cutoff_energy=2, I_H=3, I_HeI=5, I_HeII=7,
    capture_H=1, capture_HeI=2, capture_HeII=3,
)
y = dict(zip(family.state_order, map(Q, (2, 1, 1, 1, 2, 2, 3, 2, 1, 1, 33, 0))))
coeff = {r: Q(i+1, 11) for i, r in enumerate(family.events)}
rates = base_mass_action_proposals(family, y, coeff, 3)
all_columns = column_invariant_residuals(family)
record("ES01_column_invariants",
       all(v == 0 for row in all_columns.values() for v in row.values()),
       {"event_columns": len(family.events), "invariant_rows": len(all_columns),
        "exact_zero_residuals": sum(v == 0 for row in all_columns.values() for v in row.values())})

def invariants_same(before, after):
    return all(dot_state(row, before) == dot_state(row, after)
               for row in family.invariant_rows.values())

large = capacity_step(y, family.events, rates, 10**12)
record("ES02_shared_all_channel_capacity",
       all(large.state[i] >= large.retained_lower_bounds[i] for i in y)
       and all(large.state[i] > 0 for i in y if y[i] > 0)
       and invariants_same(y, large.state),
       {"step_size": "1000000000000",
        "initial_charge_over_e": str(dot_state(family.invariant_rows["charge_over_e"], y)),
        "initial_total_energy": str(dot_state(family.invariant_rows["kinetic_chemical_radiative_energy"], y)),
        "all_four_linear_invariants": "exactly unchanged",
        "minimum_final_positive_stock_scaled_by_initial":
            float(min(large.state[i]/y[i] for i in y if y[i] > 0))})

zero_h = {**y, "HI": Q(0)}
zero_h_rates = base_mass_action_proposals(family, zero_h, coeff, 3)
zero_h_out = capacity_step(zero_h, family.events, zero_h_rates, 9)
record("ES03_zero_donor_local_support",
       zero_h_out.extents["impact_H"] == 0
       and zero_h_out.extents["thermal_ionize_H"] == 0
       and zero_h_out.extents["thermalize_L"] > 0
       and zero_h_out.extents["impact_HeI"] > 0
       and invariants_same(zero_h, zero_h_out.state),
       {"inactive_zero_donor_events": list(zero_h_out.inactive_zero_donor_events),
        "unrelated_helium_and_terminal_channels": "positive extents"})

low_u = {**y, "U_th": Q(1, 1000)}
low_rates = {r: (Q(100) if r.startswith(("thermal_ionize_", "recombine_")) else Q(0))
             for r in family.events}
low_out = capacity_step(low_u, family.events, low_rates, 10**9)
record("ES04_shared_thermal_energy_capacity",
       low_out.state["U_th"] > 0 and invariants_same(low_u, low_out.state)
       and low_out.state["U_th"] >= low_out.retained_lower_bounds["U_th"],
       {"initial_thermal_energy": "1/1000",
        "final_thermal_energy": float(low_out.state["U_th"]),
        "all_six_endothermic_channels": "share the same U_th consumption load"})

zero_u = {**y, "U_th": Q(0)}
zero_u_out = capacity_step(zero_u, family.events, rates, 5)
record("ES05_zero_energy_with_heating",
       all(zero_u_out.extents[r] == 0 for r in family.events
           if r.startswith(("thermal_ionize_", "recombine_")))
       and zero_u_out.extents["thermalize_L"] > 0
       and zero_u_out.state["U_th"] > 0
       and invariants_same(zero_u, zero_u_out.state),
       {"scope": "algebraic support-boundary check for the proposal-to-state map",
        "zero_energy_consumers": "inactive",
        "exothermic_channels": "active"})

ci_rates = {r: Q(r == "thermal_ionize_H") for r in family.events}
ci = capacity_step(y, family.events, ci_rates, Q(3, 4))
xi = ci.extents["thermal_ionize_H"]
t0 = temperature(y, 1)
t1 = temperature(ci.state, 1)
packet_delta = (-family.thresholds["H"] - Q(3, 2)*t0)*xi/(Q(3, 2)*thermal_count(ci.state))
record("ES06_ionization_EOS_packet",
       t1-t0 == packet_delta and t1 < t0 and invariants_same(y, ci.state)
       and ci.state["e_th"]-y["e_th"] == xi,
       {"initial_temperature": str(t0), "final_temperature": str(t1),
        "finite_packet_identity_residual": "0", "thermal_particle_increment": str(xi)})

capture_family = build_h_he_family(
    cutoff_energy=2, I_H=3, I_HeI=5, I_HeII=7,
    capture_H=3, capture_HeI=2, capture_HeII=3,
)
capture_y = {i: Q(0) for i in family.state_order}
capture_y.update({"HII": Q(1), "e_th": Q(1), "U_th": Q(6)})
capture_rates = {r: Q(r == "recombine_H") for r in capture_family.events}
capture = capacity_step(capture_y, capture_family.events, capture_rates, Q(3, 7))
record("ES07_capture_mean_energy_temperature",
       temperature(capture_y, 1) == temperature(capture.state, 1) == 2
       and all(dot_state(row, capture_y) == dot_state(row, capture.state)
               for row in capture_family.invariant_rows.values())
       and capture.state["E_rad"] == 6*capture.extents["recombine_H"],
       {"captured_energy_per_event": "3", "initial_U_over_Nth": "3",
        "temperature_before_and_after": "2",
        "photon_energy_per_event": "6", "energy_invariant_residual": "0"})

binary_y = {"A": Q(1), "B": Q(1), "P": Q(0)}
binary_s = {"reaction": {"A": Q(-1), "B": Q(-1), "P": Q(1)}}
binary_errors = []
for h in (Q(1, 8), Q(1, 16), Q(1, 32)):
    out = capacity_step(binary_y, binary_s, {"reaction": Q(1)}, h)
    exact_extent = h/(1+h)
    error = exact_extent-out.extents["reaction"]
    predicted = h*h/((1+h)*(1+2*h))
    binary_errors.append({"h": str(h), "actual_error": str(error),
                          "closed_formula_error": str(predicted)})
record("ES08_nonlinear_binary_first_order",
       all(x["actual_error"] == x["closed_formula_error"] for x in binary_errors),
       {"continuous_exact_extent": "h/(1+h)",
        "discrete_extent": "h/(1+2*h)", "exact_local_error": "h^2/((1+h)*(1+2*h))",
        "values": binary_errors})

zero = capacity_step(y, family.events, rates, 0)
rejections = 0
for bad_h, bad_rates in ((-1, rates), (1, {**rates, "impact_H": Q(-1)})):
    try:
        capacity_step(y, family.events, bad_rates, bad_h)
    except ValueError:
        rejections += 1
record("ES09_zero_step_and_physical_input_contract",
       zero.state == y and all(x == 0 for x in zero.extents.values()) and rejections == 2,
       {"zero_step": "identity", "negative_step_and_rate_rejected": rejections})

manifest = []
for rel in ("event_capacity_step.py", "checks/run_event_checks.py",
            "examples/H_HE_EVENT_FAMILY.json"):
    content = (ROOT/rel).read_bytes()
    manifest.append({"path": rel, "bytes": len(content),
                     "sha256": hashlib.sha256(content).hexdigest()})
result = {
    "schema": "bass-cr-exact-event-checks.v1",
    "unit_id": "CR-THEORY-FEEDBACK-20261013",
    "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
    "passed": sum(c["pass"] for c in checks),
    "total": len(checks),
    "method": "Python standard-library Fraction exact-rational arithmetic",
    "attribution": "event-construction author",
    "independent_reviewer_execution": False,
    "scope": "finite algebraic event family and reference capacity map",
    "atomic_threshold_data": "dimensionless rational fixture; not measured H/He thresholds",
    "full_atomic_kernel_runs": 0,
    "scientific_ODE_integrations": 0,
    "NCP_jobs": 0,
    "elapsed_seconds": time.perf_counter()-start,
    "python": sys.version.split()[0],
    "checks": checks,
    "identity_manifest": manifest,
}
out_path = ROOT/"results"/"EVENT_CHECKS.json"
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
print(json.dumps({"status": result["status"], "passed": result["passed"],
                  "total": result["total"], "elapsed_seconds": result["elapsed_seconds"],
                  "result": str(out_path)}, ensure_ascii=False))

