#!/usr/bin/env python3
"""Focused new wiring checks for the thermal-cutoff reference implementation.

This file does not rerun the prior event/Picard suites or Wolfram identities.
The exact fixture endpoints serve as supplied oracles for this new moment/solver
connection. No physical ODE, NCP job, or atomic cross-section call is performed.
"""

from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
from datetime import datetime, timezone

UNIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_DIR))

from thermal_cutoff_solver import (  # noqa: E402
    Atom,
    AtomicInventory,
    Box,
    BoxSpectrum,
    ContinuousCutoffProblem,
    construct_atomic_root,
    continue_atomic_energy,
    enumerate_atomic_roots,
    solve_continuous_cutoff,
)

F = Fraction


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_error(callable_, error_type: type[Exception], message: str) -> None:
    try:
        callable_()
    except error_type:
        return
    raise AssertionError(message)


def rational_json(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): rational_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [rational_json(item) for item in value]
    return value


def continuous_problem(delta: Fraction) -> ContinuousCutoffProblem:
    return ContinuousCutoffProblem(
        spectrum=BoxSpectrum((Box(3, 6, F(1, 4)),)),
        common_count=F(5, 2),
        common_energy=F(11, 2) + delta,
        nucleus_count=F(1),
        reference_cutoff=F(4),
        k_b=F(1),
        chi=F(4),
        temperature_lower=F(3, 4),
        temperature_upper=F(5, 4),
    )


def check_continuous_fixed_reference_and_certificate() -> dict:
    tolerance = F(1, 10**12)
    summaries = []
    for name, delta, exact_temperature in (
        ("heating", F(2, 25), F(6, 5)),
        ("cooling", -F(3, 25), F(4, 5)),
        ("zero_step", F(0), F(1)),
    ):
        problem = continuous_problem(delta)
        before = asdict(problem)
        result = solve_continuous_cutoff(
            problem, temperature_tolerance=tolerance, max_iterations=128
        )
        require(result.converged, name + " did not converge.")
        require(result.derivative_lower_bound == F(1, 4),
                "The finite box slope certificate differs from the fixture bound.")
        actual_error = abs(result.state.temperature - exact_temperature)
        require(actual_error <= result.temperature_error_bound <= tolerance,
                name + " violated its temperature certificate.")
        for state in result.evaluations:
            require(state.thermal_count + state.active_count == problem.common_count,
                    "A recorded EOS candidate changed the common count.")
            require(state.thermal_energy + state.active_energy == problem.common_energy,
                    "A recorded EOS candidate changed the common energy.")
            require(min(state.thermal_count, state.thermal_energy,
                        state.active_count, state.active_energy) >= 0,
                    "A recorded candidate has a negative stock.")
            require(problem.temperature_lower <= state.temperature <= problem.temperature_upper,
                    "A recorded candidate escaped its bracket.")
            require(state == problem.evaluate(state.temperature),
                    "A repeated evaluation accumulated a transfer or changed memory.")
        require(asdict(problem) == before, "Solver mutated the fixed reference problem.")
        if name == "zero_step":
            require(result.status == "EXACT_ROOT" and result.iterations == 0,
                    "h=0 identity was not returned at the fixed reference.")
            require(result.state.transferred_count == result.state.transferred_energy == 0,
                    "h=0 performed a cutoff transfer.")
        else:
            sign = 1 if name == "heating" else -1
            require(sign * result.state.transferred_count > 0,
                    "The finite count transfer has the wrong direction.")
            require(sign * result.state.transferred_energy > 0,
                    "The finite energy transfer has the wrong direction.")
        summaries.append({
            "case": name,
            "input_delta": delta,
            "exact_temperature_oracle": exact_temperature,
            "status": result.status,
            "iterations": result.iterations,
            "recorded_EOS_candidates": len(result.evaluations),
            "temperature": result.state.temperature,
            "actual_temperature_error": actual_error,
            "certified_temperature_error": result.temperature_error_bound,
            "verified_slope": result.derivative_lower_bound,
            "signed_transfer": {
                "count": result.state.transferred_count,
                "energy": result.state.transferred_energy,
            },
            "all_candidate_count_energy_residuals": "exact zero",
            "all_candidate_stocks": "nonnegative",
            "fixed_reference_unchanged": True,
        })
    incomplete = solve_continuous_cutoff(
        continuous_problem(F(2, 25)),
        temperature_tolerance=F(1, 10**40),
        max_iterations=1,
    )
    require(not incomplete.converged and incomplete.status == "MAX_ITERATIONS",
            "A deliberately capped nonlinear solve was falsely marked converged.")
    require(abs(incomplete.state.temperature - F(6, 5))
            <= incomplete.temperature_error_bound,
            "The capped solve lost its honest remaining-error bound.")
    require_error(
        lambda: solve_continuous_cutoff(
            continuous_problem(F(1)),
            temperature_tolerance=tolerance,
        ),
        ValueError,
        "An unbracketed EOS root was accepted.",
    )
    require_error(
        lambda: continuous_problem(-F(3)),
        ValueError,
        "Negative unresolved base energy was silently corrected.",
    )
    summaries.append({
        "case": "bounded_failure_paths",
        "maxiter_status": incomplete.status,
        "maxiter_converged": incomplete.converged,
        "maxiter_temperature_bound": incomplete.temperature_error_bound,
        "unbracketed_input": "rejected",
        "negative_base_energy": "rejected_without_clipping",
    })
    return {
        "id": "TC-DRIVER-1",
        "name": "continuous fixed-reference bisection and temperature certificate",
        "status": "PASS",
        "cases": summaries,
    }


def audit_atomic_path(result) -> None:
    inventory = result.inventory
    for state in result.path:
        require(state.thermal_count + state.active_count == inventory.common_count,
                "Atomic candidate changed its fixed common count.")
        require(state.thermal_energy + state.active_energy == inventory.common_energy,
                "Atomic candidate changed its fixed common energy.")
        require(state.thermal_count >= inventory.nucleus_count
                and state.thermal_energy > 0 and state.temperature > 0,
                "Atomic candidate lost its positive thermal domain.")
        require(min(state.active_count, state.active_energy) >= 0,
                "Atomic candidate produced a negative active inventory.")
        require(state == inventory.state(state.thermal_groups),
                "Atomic candidate depended on accumulated prior trial updates.")
    require(result.state.threshold_consistent,
            "Atomic scan returned an inconsistent branch.")
    require(result.crossing_count <= len(inventory.atoms),
            "Atomic scan exceeded its proved finite index bound.")


def check_atomic_kernel_prefix_connection() -> dict:
    reference = AtomicInventory(
        atoms=(Atom(5, 1), Atom(9, 1), Atom(30, 1)),
        base_count=F(10), base_energy=F(15), nucleus_count=F(10),
        k_b=F(1), chi=F(4),
    )
    original = asdict(reference)
    heating = continue_atomic_energy(reference, 0, 135)
    cooling = continue_atomic_energy(heating.inventory, 3, -135)
    zero = continue_atomic_energy(reference, 0, 0)
    existence = construct_atomic_root(heating.inventory)
    for result in (heating, cooling, zero, existence):
        audit_atomic_path(result)
    require([s.thermal_groups for s in heating.path] == [0, 1, 2, 3],
            "The heating index path is wrong.")
    require([s.temperature for s in heating.path]
            == [F(10), F(310, 33), F(82, 9), F(388, 39)],
            "Heating did not use fixed energy/count prefix moments.")
    require(heating.path[1].temperature < heating.path[0].temperature
            and heating.path[2].temperature < heating.path[1].temperature,
            "The targeted decreasing-temperature inclusion case was not exercised.")
    require([s.thermal_groups for s in cooling.path] == [3, 2, 1, 0],
            "The cooling index path is wrong.")
    require([s.temperature for s in cooling.path]
            == [F(118, 39), F(29, 18), F(40, 33), F(1)],
            "Cooling did not use fixed energy/count prefix moments.")
    require(zero.crossing_count == 0 and zero.state == reference.state(0),
            "Zero base-energy change did not preserve the inherited branch.")
    require(cooling.state == reference.state(0),
            "This exact heating/cooling fixture did not recover its initial state.")
    require(asdict(reference) == original, "Atomic reference was mutated.")
    require(existence.state == heating.state,
            "Existence scan and continuation disagree in the unique-branch fixture.")

    # Three legitimate roots show why enumeration and branch continuation have
    # distinct semantics. A zero update must retain the supplied branch.
    multiple = AtomicInventory(
        atoms=(Atom(5, 1), Atom(9, 1)),
        base_count=F(1), base_energy=F(3, 2), nucleus_count=F(1),
        k_b=F(1), chi=F(4),
    )
    roots = enumerate_atomic_roots(multiple)
    require([s.thermal_groups for s in roots] == [0, 1, 2],
            "Atomic root enumeration lost distinct admissible branches.")
    retained = continue_atomic_energy(multiple, 2, 0)
    require(retained.state == multiple.state(2)
            and retained.state != construct_atomic_root(multiple).state,
            "The zero-step branch policy was replaced by a different existence root.")

    # Thermal equality ownership is exercised with duplicate energy atoms.
    equality = AtomicInventory(
        atoms=(Atom(5, F(1, 3)), Atom(5, F(2, 3)), Atom(20, 0)),
        base_count=F(10), base_energy=F(75, 4), nucleus_count=F(10),
        k_b=F(1), chi=F(4),
    )
    require(len(equality.atoms) == 1 and equality.atoms[0].count == 1,
            "Equal energies or zero weights were not canonically handled.")
    equality_scan = construct_atomic_root(equality)
    audit_atomic_path(equality_scan)
    require(equality_scan.state.thermal_groups == 1,
            "A node exactly at the initial cutoff was not assigned to thermal.")
    require_error(
        lambda: continue_atomic_energy(equality, 0, 0), ValueError,
        "Inconsistent initial equality ownership was silently changed.",
    )
    require_error(
        lambda: continue_atomic_energy(reference, 0, -15), ValueError,
        "Zero-temperature base energy was silently floored.",
    )
    return {
        "id": "TC-DRIVER-2",
        "name": "atomic prefix energy/count bridge and finite branch continuation",
        "status": "PASS",
        "heating": {
            "indices": [s.thermal_groups for s in heating.path],
            "temperatures": [s.temperature for s in heating.path],
            "common_count": heating.inventory.common_count,
            "common_energy": heating.inventory.common_energy,
            "first_two_inclusions_decrease_temperature": True,
        },
        "cooling": {
            "indices": [s.thermal_groups for s in cooling.path],
            "temperatures": [s.temperature for s in cooling.path],
            "common_count": cooling.inventory.common_count,
            "common_energy": cooling.inventory.common_energy,
            "recovered_fixture_reference": True,
        },
        "all_audited_path_count_energy_residuals": "exact zero",
        "all_audited_path_stocks": "nonnegative; N>=N_nuc and U,T>0",
        "multiple_root_indices": [s.thermal_groups for s in roots],
        "zero_step_retains_inherited_root": True,
        "thermal_equality_ownership": "enforced",
        "equal_energy_grouping": "exact",
        "invalid_initial_ownership": "rejected",
        "zero_base_energy": "rejected_without_flooring",
    }


def main() -> None:
    start = perf_counter()
    checks = [
        check_continuous_fixed_reference_and_certificate(),
        check_atomic_kernel_prefix_connection(),
    ]
    elapsed = perf_counter() - start
    source_paths = [
        UNIT_DIR / "thermal_cutoff_solver.py",
        Path(__file__).resolve(),
    ]
    report = {
        "schema": "bass-cr-thermal-cutoff-driver-checks.v1",
        "unit": "CR-THEORY-KERNEL-CUTOFF-20261013",
        "status": "PASS",
        "check_groups": len(checks),
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "wall_seconds": elapsed,
            "arithmetic": "fractions.Fraction exact rational",
            "workers": 1,
        },
        "source_identity": [
            {
                "path": str(path.relative_to(UNIT_DIR)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for path in source_paths
        ],
        "checks": checks,
        "scope": {
            "new_physical_ODE_integrations": 0,
            "new_NCP_jobs": 0,
            "old_suite_reruns": 0,
            "cross_section_calls": 0,
            "duplicate_Wolfram_runs": 0,
            "meaning": "New finite-cutoff implementation wiring only; no physical-kernel qualification.",
            "continuous_certificate": "Exact finite box representation; physical spectral representation error is separate.",
        },
    }
    destination = UNIT_DIR / "results" / "THERMAL_CUTOFF_CHECKS.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(rational_json(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "check_groups": len(checks),
        "wall_seconds": elapsed,
        "result": str(destination),
    }))


if __name__ == "__main__":
    main()

