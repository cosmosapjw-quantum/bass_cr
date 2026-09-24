#!/usr/bin/env python3
"""Bounded local Coulomb singular-cell and trajectory-phase discriminator.

This never propagates a state or changes the production representation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import dblquad
from cr_repro.observables import projectile_speed_au
from cr_repro.r3m11 import source_digest


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "results/R3M29/DESIGN.json"


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def bind_design() -> dict:
    design = json.loads(DESIGN.read_text())
    if source_digest() != design["frozen_numerical_source_digest"]:
        raise ValueError("frozen numerical source changed")
    if design["input_head"] != "8656736dd1b45b748b0669f4a7dafdb71787e032":
        raise ValueError("unrecognized input HEAD")
    for relative, expected in design["input_sha256"].items():
        if sha(ROOT / relative) != expected:
            raise ValueError(f"frozen input changed: {relative}")
    if (design["nstep"] != 7172 or design["h_values"] != [0.25, 0.2]
            or design["singular_cell_phases"] != [0.0, 0.25, 0.5]
            or design["phase_bins"] != 32):
        raise ValueError("unexpected diagnostic design")
    return design


def integrand(y: float, x: float, alpha: float) -> float:
    rho = math.hypot(x, y)
    if rho == 0:
        return math.inf
    return math.asinh((1.0-alpha)/rho) + math.asinh(alpha/rho)


def cell_average_reference(alpha: float) -> tuple[float, float]:
    """Independent adaptive 2-D integration after exact z integration."""
    if not 0 <= alpha <= 1:
        raise ValueError("phase outside one cell")
    return dblquad(lambda y, x: integrand(y, x, alpha), 0, 1,
                   lambda _x: 0, lambda _x: 1, epsabs=1e-9, epsrel=1e-9)


def cell_average_gl(alpha: float, order: int) -> float:
    if not 0 <= alpha <= 1 or order < 2:
        raise ValueError("invalid phase or quadrature order")
    nodes, weights = leggauss(order)
    nodes = (nodes+1)/2
    weights = weights/2
    rho = np.hypot(nodes[:, None], nodes[None, :])
    value = np.arcsinh((1-alpha)/rho) + np.arcsinh(alpha/rho)
    return float(np.sum(weights[:, None]*weights[None, :]*value))


def midpoint(alpha: float) -> float:
    if not 0 <= alpha <= 1:
        raise ValueError("phase outside one cell")
    return 1/math.sqrt(0.5**2+0.5**2+(0.5-alpha)**2)


def phase_counts(h: float, nstep: int, z_start: float, z_stop: float,
                 bins: int) -> list[int]:
    if h <= 0 or nstep <= 0 or bins <= 0:
        raise ValueError("positive geometry required")
    # Match TDLRunner's scalar arithmetic order, including rounding at bins.
    speed = projectile_speed_au(100.0)
    horizon = (z_stop-z_start)/speed
    dt_actual = horizon/nstep
    t0 = z_start/speed
    z_mid = np.asarray([speed*(t0+(j+0.5)*dt_actual)
                        for j in range(nstep)], dtype=np.float64)
    phase = np.mod((z_mid-z_start)/h, 1.0)
    return np.histogram(phase, bins=bins, range=(0, 1))[0].astype(int).tolist()


def evaluate() -> dict:
    start = time.monotonic()
    d = bind_design()
    observed = json.loads((ROOT / "results/R3M28/SPATIAL_EVALUATION.json").read_text())
    if observed["status"] != "SPATIAL_PAIR_SCREEN_NO_GO":
        raise ValueError("R3M28 spatial trigger changed")
    for relative, h in (("configs/r3m28/A3.json", 0.25),
                        ("configs/r3m27/B3.json", 0.2)):
        cfg = json.loads((ROOT/relative).read_text())
        grid = cfg["grid"]
        if (grid["dx"] != h or cfg["b"] != 2.0 or
                grid["xlim"][0] != -30 or grid["ylim"][0] != -30 or
                grid["zlim"][0] != d["z_start"] or
                cfg["z_start"] != d["z_start"] or cfg["z_stop"] != d["z_stop"] or
                not math.isclose((cfg["b"]-grid["xlim"][0])/h,
                                 round((cfg["b"]-grid["xlim"][0])/h), abs_tol=1e-12)):
            raise ValueError("projectile/target vertex phase geometry changed")
    rows = []
    for alpha in d["singular_cell_phases"]:
        reference, reported_error = cell_average_reference(alpha)
        values = {str(n): cell_average_gl(alpha, n) for n in (64, 128, 256)}
        relative = abs(values["256"]-reference)/reference
        if relative > d["quadrature_relative_tolerance"]:
            raise ArithmeticError("local cell quadrature did not converge")
        point = midpoint(alpha)
        rows.append(dict(alpha=alpha, h_times_cell_mean=reference,
                         h_times_midpoint=point, midpoint_minus_cell_mean_relative=(point-reference)/reference,
                         adaptive_reported_absolute_error=reported_error,
                         gauss_legendre=values, gl256_relative_to_adaptive=relative))
    occupancies = {}
    for h in d["h_values"]:
        counts = phase_counts(h, d["nstep"], d["z_start"], d["z_stop"], d["phase_bins"])
        occupancies[str(h)] = dict(counts=counts, minimum=min(counts), maximum=max(counts),
                                   maximum_absolute_fraction_from_uniform=max(abs(c/d["nstep"]-1/d["phase_bins"])
                                                                      for c in counts))
    first = np.asarray(occupancies[str(d["h_values"][0])]["counts"], float)/d["nstep"]
    second = np.asarray(occupancies[str(d["h_values"][1])]["counts"], float)/d["nstep"]
    tv = float(0.5*np.abs(first-second).sum())
    min_bias = min(abs(r["midpoint_minus_cell_mean_relative"]) for r in rows)
    selected = (tv <= d["phase_total_variation_threshold"]
                and min_bias >= d["minimum_all_phase_local_midpoint_bias"])
    wall = time.monotonic()-start
    if wall > d["max_cpu_wall_seconds"]:
        raise TimeoutError("bounded local diagnostic wall exceeded")
    return dict(schema="R3M29_COULOMB_CELL_RESULT_V1",
                status=d["decision_if_pass"] if selected else d["decision_if_fail"],
                design_sha256=sha(DESIGN), input_head=d["input_head"],
                input_sha256=d["input_sha256"], local_cell_rows=rows,
                actual_midpoint_phase_histograms=occupancies,
                phase_histogram_total_variation=tv,
                trajectory_phase_arithmetic="FROZEN_TDLRUNNER_SCALAR_TMID_THEN_SPEED_PRODUCT",
                minimum_local_midpoint_bias=min_bias,
                local_1_over_r_cell_mean_scaling="h^-1",
                h_values=d["h_values"], nstep=d["nstep"],
                x_y_nuclear_vertex_alignment="VERIFIED_FOR_TARGET_AND_PROJECTILE_B2",
                cpu_wall_seconds=wall, gpu_runs=0, new_preparations=0,
                new_full_collisions=0,
                causal_attribution_of_final_capture_gap="NOT_ESTABLISHED",
                full_spatial_error_estimate="OPEN",
                representation_decision="PRIORITIZE_CELL_AVERAGED_POINT_COULOMB_FOR_BOUNDED_SAME_H_VALIDATION_ONLY" if selected else "HOLD_UNRESOLVED",
                production_representation_changed=False,
                production_admission=False, all_bound="OPEN", b_grid="NO_GO")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    value = evaluate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status=value["status"], output=str(args.out))))


if __name__ == "__main__":
    main()
