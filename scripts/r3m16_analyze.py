#!/usr/bin/env python3
"""Create the preregistered R3M16 h x dt collision decomposition."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ALLOWED = {
    "CURRENT_REPRESENTATION_RETAINED__COUPLED_H_DT_PROTOCOL_REQUIRED",
    "COUPLED_H_DT_PROMISING_BUT_BUDGET_OPEN",
    "POINT_COULOMB_FFT_SPATIAL_REPRESENTATION_BLOCKER",
    "POINT_COULOMB_FFT_REPRESENTATION_CHANGE_REQUIRED",
    "TIME_REFINEMENT_STILL_OPEN",
}


def sha256(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _term(value: float, denominator: float, meaning: str) -> dict:
    if not math.isfinite(denominator) or denominator == 0:
        raise ValueError("relative denominator must be finite and nonzero")
    return {"value": value, "absolute": abs(value), "relative": abs(value) / abs(denominator),
            "relative_denominator": abs(denominator), "meaning": meaning}


def decompose(a0: float, b0: float, a1: float, b1: float) -> dict:
    values = (a0, b0, a1, b1)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("finite matrix values required")
    return {
        "Delta_h_dt05": _term(b0 - a0, b0, "B0-A0; denominator abs(B0)"),
        "Delta_h_dt025": _term(b1 - a1, b1, "B1-A1; denominator abs(B1)"),
        "Delta_t_h025": _term(a1 - a0, a1, "A1-A0; denominator abs(A1)"),
        "Delta_t_h020": _term(b1 - b0, b1, "B1-B0; denominator abs(B1)"),
        "I_ht": _term(b1 - a1 - b0 + a0, b1,
                      "B1-A1-B0+A0; denominator abs(B1); nonadditivity diagnostic"),
    }


def decide(time_rel_h020: float, spatial_rel_dt025: float, target_only_clean: bool) -> str:
    if not all(math.isfinite(x) and x >= 0 for x in (time_rel_h020, spatial_rel_dt025)):
        raise ValueError("finite nonnegative decision metrics required")
    if time_rel_h020 <= 0.001 and spatial_rel_dt025 > 0.003:
        return "POINT_COULOMB_FFT_SPATIAL_REPRESENTATION_BLOCKER"
    if time_rel_h020 > 0.001:
        if spatial_rel_dt025 <= 0.003:
            return "CURRENT_REPRESENTATION_RETAINED__COUPLED_H_DT_PROTOCOL_REQUIRED"
        if spatial_rel_dt025 <= 0.01:
            return "COUPLED_H_DT_PROMISING_BUT_BUDGET_OPEN"
        return ("POINT_COULOMB_FFT_REPRESENTATION_CHANGE_REQUIRED" if target_only_clean
                else "TIME_REFINEMENT_STILL_OPEN")
    # Both allocations are met. N1_TDL still has preparation and boundary/CAP work.
    return "CURRENT_REPRESENTATION_RETAINED__COUPLED_H_DT_PROTOCOL_REQUIRED"


def _row(name: str, result: dict, path: Path, requested_dt: float, dx: float) -> dict:
    audit = result["analysis"]["gram_audit"]
    spans = audit["P_span_by_nmax"]
    return {
        "id": name, "dx": dx, "requested_dt": requested_dt,
        "actual_dt": result["dt_actual"], "nstep": result["nstep"],
        "P1": spans["1"], "P2": spans["2"], "P3": spans["3"],
        "P_region": audit["P_region"], "norm": audit["wavefunction_norm"],
        "Gram_condition": audit["Gram_condition"],
        "Gram_eigenvalues": audit["Gram_eigenvalues"],
        "raw_channel_norms": audit["finite_grid_state_norms"],
        "Hamiltonian_residual_Eh": result["initial"]["stationary_residual_Eh"],
        "result_sha256": sha256(path),
        "source_digest": result["config"]["_r3m11_source_digest"],
    }


def _old_row(name: str, source: dict) -> dict:
    keys = ("dx", "P1", "P2", "P3", "P_region", "norm", "Gram_condition",
            "Gram_eigenvalues", "raw_channel_norms", "Hamiltonian_residual_Eh",
            "actual_dt", "result_sha256", "source_digest")
    return {"id": name, "requested_dt": 0.05, **{key: source[key] for key in keys}}


def analyze(r3m15_matrix: Path, a1_path: Path, b1_path: Path,
            target_a: Path, target_b: Path) -> dict:
    old = json.loads(Path(r3m15_matrix).read_text())
    a1_raw = json.loads(Path(a1_path).read_text())
    b1_raw = json.loads(Path(b1_path).read_text())
    ta = json.loads(Path(target_a).read_text())
    tb = json.loads(Path(target_b).read_text())
    a0 = _old_row("A0", old["rows"]["A"])
    b0 = _old_row("B0", old["rows"]["B"])
    a1 = _row("A1", a1_raw, Path(a1_path), 0.025, 0.25)
    b1 = _row("B1", b1_raw, Path(b1_path), 0.025, 0.20)
    per_observable = {}
    for observable in ("P1", "P2", "P3"):
        per_observable[observable] = decompose(
            a0[observable], b0[observable], a1[observable], b1[observable])
    clean = bool(ta["fixed_horizon"]["clean_second_order_diagnostic"] and
                 tb["fixed_horizon"]["clean_second_order_diagnostic"])
    p3 = per_observable["P3"]
    decision = decide(p3["Delta_t_h020"]["relative"],
                      p3["Delta_h_dt025"]["relative"], clean)
    if decision not in ALLOWED:
        raise AssertionError("unregistered decision")
    return {
        "schema": "BASS_CR_R3M16_H_DT_MATRIX_V1",
        "status": "COMPLETE_2_NEW_COLLISIONS",
        "rows": {"A0": a0, "B0": b0, "A1": a1, "B1": b1},
        "decomposition": per_observable,
        "decision_metrics": {
            "P3_time_h020_relative": p3["Delta_t_h020"]["relative"],
            "P3_spatial_dt025_relative": p3["Delta_h_dt025"]["relative"],
            "target_only_both_clean_second_order": clean,
            "time_allocation": 0.001, "spatial_allocation": 0.003,
        },
        "scientific_decision": decision,
        "claim_ceiling": {
            "global_spatial_convergence": "NO_GO", "all_bound_completion": "OPEN",
            "bgrid_admission": "NO_GO", "cross_section_convergence": "NOT_ESTABLISHED",
            "energies_50_225": "NOT_RUN", "physical_rate": "NOT_ADMITTED",
            "nichols_code_reproduction": False,
        },
        "inputs": {"r3m15_matrix_sha256": sha256(r3m15_matrix),
                   "A1_result_sha256": sha256(a1_path), "B1_result_sha256": sha256(b1_path),
                   "target_A_sha256": sha256(target_a), "target_B_sha256": sha256(target_b)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r3m15-matrix", type=Path, required=True)
    parser.add_argument("--a1", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--target-a", type=Path, required=True)
    parser.add_argument("--target-b", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    value = analyze(args.r3m15_matrix, args.a1, args.b1, args.target_a, args.target_b)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")
    print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
