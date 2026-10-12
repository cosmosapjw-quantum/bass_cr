"""Focused author checks for the new feedback driver connection only.

The neutral FP7 endpoint and q are reused exact oracles from the theory and
the root's successful Wolfram run. No symbolic suite or physical ODE is run.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from event_capacity_step import K_B_SI, dot_state, temperature
from feedback_solver import (
    DomainContract, ThermalCertificate, solve_feedback, weighted_norm,
)

Q = Fraction
T_REF_K = Q(1)
E0 = Q(3, 2) * K_B_SI * T_REF_K
BASE = {"A": Q(1), "HI": Q(1), "HII": Q(1), "e_th": Q(0), "U_th": E0}
COLUMN = {"A": Q(-1), "HI": Q(-1), "HII": Q(1), "e_th": Q(2), "U_th": 3 * E0}
EVENTS = {"neutral_impact": COLUMN}
SCALES = {i: abs(v) for i, v in COLUMN.items()}
ROWS = {
    "H_nuclei": {"HI": Q(1), "HII": Q(1)},
    "charge_over_e": {"HII": Q(1), "A": Q(-1), "e_th": Q(-1)},
    "energy_J": {"A": 4 * E0, "HII": E0, "U_th": Q(1)},
}
ORACLE_X = Q(1, 4)
ORACLE_STATE = {i: BASE[i] + COLUMN[i] * ORACLE_X for i in BASE}
ORACLE_T_K = Q(7, 10) * T_REF_K
Q_BOUND = Q(170, 841)
H_SECONDS = Q(4, 17)


def in_domain(state):
    x = state["HII"] - 1
    return Q(0) <= x <= Q(1) and all(
        state[i] == BASE[i] + COLUMN[i] * x for i in BASE)


def proposals(base, trial):
    coefficient = (1 + temperature(trial) / T_REF_K) * trial["HII"]
    return {"neutral_impact": coefficient * base["A"] * base["HI"]}


def physical_rates(trial):
    coefficient = (1 + temperature(trial) / T_REF_K) * trial["HII"]
    return {"neutral_impact": coefficient * trial["A"] * trial["HI"]}


DOMAIN = DomainContract(
    name="FP7 neutral affine reaction segment, 0<=extent<=1",
    contains=in_domain,
    evidence="derivations/FEEDBACK_THEOREMS_KO.md FP.44-FP.50",
)
THERMAL = ThermalCertificate(count_lower_bound=Q(2), count_scale_bound=Q(2))


def run_driver(tolerance, maximum):
    return solve_feedback(
        BASE, EVENTS, proposals, H_SECONDS,
        scales=SCALES, contraction_bound=Q_BOUND,
        contraction_evidence="FP.49-FP.50; root Wolfram exact oracle reused",
        domain=DOMAIN, thermal=THERMAL,
        temperature_tolerance=tolerance, max_iterations=maximum,
        physical_rate_evaluator=physical_rates,
    )


def inspect_iterates(result):
    states = [record.state for record in result.history]
    if result.certifying_map_image is not None:
        states.append(result.certifying_map_image.state)
    invariant_values = {name: dot_state(row, BASE) for name, row in ROWS.items()}
    for state in states:
        assert all(value >= 0 for value in state.values())
        assert in_domain(state)
        for name, row in ROWS.items():
            assert dot_state(row, state) == invariant_values[name]
    for i in BASE:
        assert result.state[i] == BASE[i] + COLUMN[i] * result.event_extents["neutral_impact"]
    assert result.map_evaluations == result.iterations + 1
    assert len(result.history) == result.iterations + 1
    assert "caller supplied" in result.certificate_authority
    return len(states)


def converged_connection():
    tolerance = Q(1, 10**12) * T_REF_K
    result = run_driver(tolerance, 30)
    assert result.status == "CONVERGED"
    checked_states = inspect_iterates(result)
    state_error = weighted_norm(
        {i: result.state[i] - ORACLE_STATE[i] for i in BASE}, SCALES)
    temperature_error = abs(result.temperature - ORACLE_T_K)
    assert state_error <= result.discrete_state_error_bound
    assert temperature_error <= result.discrete_temperature_error_bound <= tolerance
    assert result.map_residual_norm > 0
    assert result.physical_ode_defect is not None
    assert result.physical_ode_defect.weighted_norm > Q(1, 10)
    assert result.physical_ode_defect.weighted_norm > result.map_residual_norm
    return {
        "status": result.status,
        "iterations": result.iterations,
        "map_evaluations": result.map_evaluations,
        "visited_states_with_exact_invariants": checked_states,
        "all_invariant_residuals": "0",
        "initial_iterate_is_base": result.history[0].state == BASE,
        "declared_q": str(result.contraction_bound),
        "q_proof_authority": result.certificate_authority,
        "temperature_tolerance_K": str(tolerance),
        "temperature_error_K_exact": str(temperature_error),
        "temperature_error_K_float": float(temperature_error),
        "certified_temperature_error_K_exact": str(result.discrete_temperature_error_bound),
        "certified_temperature_error_K_float": float(result.discrete_temperature_error_bound),
        "state_error_norm_exact": str(state_error),
        "state_error_bound_exact": str(result.discrete_state_error_bound),
        "map_residual_norm_exact": str(result.map_residual_norm),
        "physical_endpoint_rate_defect_norm_float": float(result.physical_ode_defect.weighted_norm),
        "physical_endpoint_defect_scope": result.physical_ode_defect.scope,
        "physical_endpoint_defect_units": result.physical_ode_defect.norm_units,
    }


def honest_iteration_limit():
    tolerance = Q(1, 10**30) * T_REF_K
    result = run_driver(tolerance, 1)
    assert result.status == "MAX_ITERATIONS"
    assert result.iterations == 1
    checked_states = inspect_iterates(result)
    temperature_error = abs(result.temperature - ORACLE_T_K)
    assert temperature_error <= result.discrete_temperature_error_bound
    assert result.discrete_temperature_error_bound > tolerance
    assert result.physical_ode_defect is not None
    return {
        "status": result.status,
        "iterations": result.iterations,
        "map_evaluations": result.map_evaluations,
        "visited_states_with_exact_invariants": checked_states,
        "all_invariant_residuals": "0",
        "returned_feasible": True,
        "accepted_extent_exact": str(result.event_extents["neutral_impact"]),
        "temperature_error_K_exact": str(temperature_error),
        "certified_temperature_error_K_exact": str(result.discrete_temperature_error_bound),
        "temperature_tolerance_K": str(tolerance),
        "convergence_claim": False,
        "physical_defect_returned_separately": True,
    }


def main():
    started = time.perf_counter()
    tests = [
        ("converged_capacity_picard_temperature_connection", converged_connection),
        ("honest_max_iterations_with_feasible_state", honest_iteration_limit),
    ]
    records = []
    for name, function in tests:
        try:
            records.append({"name": name, "status": "PASS", "details": function()})
        except Exception as error:
            records.append({"name": name, "status": "FAIL", "error": repr(error)})
            traceback.print_exc()
    hashes = {}
    for rel in (
        "feedback_solver.py", "event_capacity_step.py",
        "checks/run_feedback_checks.py", "derivations/FEEDBACK_THEOREMS_KO.md",
    ):
        data = (ROOT / rel).read_bytes()
        hashes[rel] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    result = {
        "schema": "bass-cr-feedback-driver-checks.v1",
        "unit_id": "CR-THEORY-FEEDBACK-20261013",
        "author": "/root/feedback_fixed_point",
        "scope": "New bounded Picard driver and thermal-certificate wiring on reused exact FP7 oracle",
        "status": "PASS" if all(row["status"] == "PASS" for row in records) else "FAIL",
        "checks_passed": sum(row["status"] == "PASS" for row in records),
        "checks_total": len(records),
        "arithmetic": "Python Fraction; SI k_B retained; E0=(3/2)*k_B*(1 K)",
        "runtime": {
            "python": platform.python_version(),
            "elapsed_seconds": time.perf_counter() - started,
            "scientific_ODE_solvers": 0,
            "NCP_jobs": 0,
            "previous_scientific_checks_repeated": 0,
            "symbolic_checks_repeated": 0,
        },
        "source_hashes": hashes,
        "checks": records,
    }
    output = ROOT / "results" / "FEEDBACK_DRIVER_CHECKS.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"], "passed": result["checks_passed"],
        "total": result["checks_total"], "elapsed_seconds": result["runtime"]["elapsed_seconds"],
        "output": str(output),
        "cases": [{"name": row["name"], "status": row["status"],
                   "iterations": row.get("details", {}).get("iterations")}
                  for row in records],
    }, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

