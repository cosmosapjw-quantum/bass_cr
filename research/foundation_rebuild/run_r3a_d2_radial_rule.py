#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

from cr_repro.observables import projectile_speed_au
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import (
    Trajectory,
    Quadrature,
    assemble,
    basis_values,
    hydrogen_channels,
    symmetric_channels,
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def rel(a, b):
    return float(
        np.linalg.norm(a - b)
        / max(float(np.linalg.norm(b)), 1.0e-300)
    )


def herm(a):
    return float(
        np.linalg.norm(a - a.conj().T)
        / max(float(np.linalg.norm(a)), 1.0e-300)
    )


def matrix_summary(S, H, D):
    ev = np.linalg.eigvalsh(S)

    return {
        "S_hermiticity": herm(S),
        "H_hermiticity": herm(H),
        "metric_lambda_min": float(ev[0]),
        "metric_lambda_max": float(ev[-1]),
        "metric_ratio": float(ev[0] / ev[-1]),
        "S_norm": float(np.linalg.norm(S)),
        "H_norm": float(np.linalg.norm(H)),
        "D_norm": float(np.linalg.norm(D)),
    }


def finite_rho_grid(
    trajectory,
    t,
    nrho,
    neta,
    nphi,
    rho_max,
):
    centers = trajectory.centers(t)
    delta = centers[1] - centers[0]
    R = float(np.linalg.norm(delta))

    if R < 1.0e-7:
        raise ValueError("unresolved coincident foci")

    ez = delta / R

    axis = np.eye(3)[int(np.argmin(abs(ez)))]

    e1 = np.cross(ez, axis)
    e1 /= np.linalg.norm(e1)

    e2 = np.cross(ez, e1)

    xr, wr = leggauss(nrho)
    eta, we = leggauss(neta)

    rho = 0.5 * rho_max * (xr + 1.0)
    wr = 0.5 * rho_max * wr

    phi = 2.0 * np.pi * np.arange(nphi) / nphi

    mu = 1.0 + 2.0 * rho / R

    transverse = (
        (R / 2.0)
        * np.sqrt(
            (mu[:, None, None] ** 2 - 1.0)
            * (1.0 - eta[None, :, None] ** 2)
        )
    )

    along = (
        (R / 2.0)
        * mu[:, None, None]
        * eta[None, :, None]
    )

    points = (
        centers.mean(axis=0)
        + along[..., None] * ez
        + transverse[..., None]
        * (
            np.cos(phi)[None, None, :, None] * e1
            + np.sin(phi)[None, None, :, None] * e2
        )
    )

    weights = (
        (R**2 / 4.0)
        * (mu[:, None] ** 2 - eta[None, :] ** 2)
        * wr[:, None]
        * we[None, :]
        * (2.0 * np.pi / nphi)
    )

    weights = np.broadcast_to(
        weights[:, :, None],
        points.shape[:-1],
    ).ravel().copy()

    return points.reshape(-1, 3), weights


def assemble_from_grid(
    trajectory,
    channels,
    t,
    points,
    weights,
    chunk=1024,
):
    channels = tuple(channels)
    centers = trajectory.centers(t)

    n = len(channels)

    S = np.zeros((n, n), complex)
    H = np.zeros_like(S)
    D = np.zeros_like(S)

    for start in range(0, len(points), chunk):
        p = points[start:start + chunk]
        w = weights[start:start + chunk]

        B, g, dot = basis_values(
            p,
            channels,
            trajectory,
            t,
        )

        V = -sum(
            trajectory.charges[c]
            / np.linalg.norm(
                p - centers[c],
                axis=1,
            )
            for c in (0, 1)
        )

        S += B.conj().T @ (w[:, None] * B)

        H += B.conj().T @ (
            (w * V)[:, None] * B
        )

        for j in range(3):
            H += (
                0.5
                * g[:, :, j].conj().T
                @ (w[:, None] * g[:, :, j])
            )

        D += B.conj().T @ (w[:, None] * dot)

    return S, H, D


def save_matrix(path, S, H, D):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("xb") as f:
        np.savez_compressed(
            f,
            S=S,
            H=H,
            D=D,
        )

    return sha256_file(path)


def make_bases(spec):
    analytic = hydrogen_channels(2)

    bound_spec = RadialSpec(
        **{
            **spec,
            "positive_per_l": 0,
        }
    )

    full_spec = RadialSpec(**spec)

    bound_bank = atomic_bank(bound_spec)
    full_bank = atomic_bank(full_spec)

    return {
        "A_ANALYTIC_BOUND": analytic,
        "B_FEM_BOUND_ONLY": symmetric_channels(
            bound_bank
        ),
        "C_FEM_BOUND_PLUS_PSEUDOSTATE":
            symmetric_channels(full_bank),
    }


def run_laguerre(
    trajectory,
    channels,
    t,
    record,
):
    q = Quadrature(
        record["nrad"],
        record["neta"],
        record["nphi"],
        record["scale"],
    )

    tic = time.perf_counter()
    snap = assemble(
        trajectory,
        channels,
        t,
        q,
    )

    return (
        snap.S,
        snap.H,
        snap.D,
        time.perf_counter() - tic,
    )


def run_finite(
    trajectory,
    channels,
    t,
    record,
):
    tic = time.perf_counter()

    p, w = finite_rho_grid(
        trajectory,
        t,
        record["nrho"],
        record["neta"],
        record["nphi"],
        record["rho_max_a0"],
    )

    S, H, D = assemble_from_grid(
        trajectory,
        channels,
        t,
        p,
        w,
    )

    return S, H, D, time.perf_counter() - tic


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--contract",
        required=True,
    )

    ap.add_argument(
        "--out",
        required=True,
    )

    args = ap.parse_args()

    contract_path = Path(args.contract)
    out = Path(args.out)

    if out.exists():
        raise FileExistsError(out)

    out.mkdir(parents=True)

    contract = json.loads(
        contract_path.read_text()
    )

    d1 = contract["d1_result"]

    if sha256_file(d1["path"]) != d1["sha256"]:
        raise RuntimeError(
            "D1 result identity mismatch"
        )

    parent = contract["parent_commit"]

    rc = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            parent,
            "HEAD",
        ]
    ).returncode

    if rc:
        raise RuntimeError(
            "D2 preregistration parent is not ancestor"
        )

    execution_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()

    execution_tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"],
        text=True,
    ).strip()

    speed = projectile_speed_au(
        contract["energy_keV_per_u"]
    )

    b = contract["b_a0"]

    trajectory = Trajectory(
        origins=(
            (0.0, 0.0, 0.0),
            (b, 0.0, 0.0),
        ),
        velocities=(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, speed),
        ),
        charges=(1.0, 1.0),
    )

    bases = make_bases(
        contract["fem_spec"]
    )

    screens = contract["screens"]

    lag_records = contract[
        "laguerre_ladder"
    ]

    fin_records = contract[
        "finite_rho_ladder"
    ]

    controls = {}
    main_rows = []

    # Independent-rule controls:
    # compare only the most refined L6/F6 results
    # for bases already known to converge in D1.
    for basis_id in contract["controls"]:
        channels = bases[basis_id]

        basis_rows = []

        for z in contract["z_samples_a0"]:
            t = z / speed

            LS, LH, LD, lt = run_laguerre(
                trajectory,
                channels,
                t,
                lag_records[-1],
            )

            FS, FH, FD, ft = run_finite(
                trajectory,
                channels,
                t,
                fin_records[-1],
            )

            differences = {
                "S": rel(FS, LS),
                "H": rel(FH, LH),
                "D": rel(FD, LD),
            }

            row = {
                "z_a0": z,
                "laguerre_wall_seconds": lt,
                "finite_rho_wall_seconds": ft,
                "finite_vs_laguerre": differences,
                "laguerre": matrix_summary(
                    LS, LH, LD
                ),
                "finite_rho": matrix_summary(
                    FS, FH, FD
                ),
            }

            basis_rows.append(row)

            write_new(
                out
                / "partials"
                / f"{basis_id}_z{z:+05.1f}.json",
                row,
            )

        limit = screens[
            "independent_rule_control_difference_max"
        ]

        passed = all(
            max(
                row[
                    "finite_vs_laguerre"
                ].values()
            )
            <= limit
            for row in basis_rows
        )

        controls[basis_id] = {
            "screen_pass": passed,
            "geometry": basis_rows,
        }

    # Main C case: compare successive refinement
    # within both integration rules.
    channels = bases[
        contract["main_case"]
    ]

    for z in contract["z_samples_a0"]:
        t = z / speed

        lag = []
        fin = []

        for rec in lag_records:
            S, H, D, wall = run_laguerre(
                trajectory,
                channels,
                t,
                rec,
            )

            path = (
                out
                / "matrices"
                / f"C_z{z:+05.1f}_{rec['id']}.npz"
            )

            digest = save_matrix(
                path, S, H, D
            )

            lag.append(
                {
                    "record": rec,
                    "S": S,
                    "H": H,
                    "D": D,
                    "wall_seconds": wall,
                    "matrix_sha256": digest,
                    "summary": matrix_summary(
                        S, H, D
                    ),
                }
            )

        for rec in fin_records:
            S, H, D, wall = run_finite(
                trajectory,
                channels,
                t,
                rec,
            )

            path = (
                out
                / "matrices"
                / f"C_z{z:+05.1f}_{rec['id']}.npz"
            )

            digest = save_matrix(
                path, S, H, D
            )

            fin.append(
                {
                    "record": rec,
                    "S": S,
                    "H": H,
                    "D": D,
                    "wall_seconds": wall,
                    "matrix_sha256": digest,
                    "summary": matrix_summary(
                        S, H, D
                    ),
                }
            )

        lchange = {
            name: rel(
                lag[0][name],
                lag[1][name],
            )
            for name in ("S", "H", "D")
        }

        fchange = {
            name: rel(
                fin[0][name],
                fin[1][name],
            )
            for name in ("S", "H", "D")
        }

        cross = {
            name: rel(
                fin[1][name],
                lag[1][name],
            )
            for name in ("S", "H", "D")
        }

        row = {
            "z_a0": z,
            "separation_a0": float(
                math.sqrt(b*b + z*z)
            ),
            "laguerre_L5_to_L6": lchange,
            "finite_F5_to_F6": fchange,
            "F6_vs_L6": cross,
            "L6": lag[1]["summary"],
            "F6": fin[1]["summary"],
            "timing_seconds": {
                "L5": lag[0]["wall_seconds"],
                "L6": lag[1]["wall_seconds"],
                "F5": fin[0]["wall_seconds"],
                "F6": fin[1]["wall_seconds"],
            },
        }

        main_rows.append(row)

        write_new(
            out
            / "partials"
            / f"C_z{z:+05.1f}_SUMMARY.json",
            row,
        )

        print(
            json.dumps({
                "z_a0": z,
                "L5_to_L6": lchange,
                "F5_to_F6": fchange,
                "F6_vs_L6": cross,
            }),
            flush=True,
        )

    limit = screens[
        "final_relative_matrix_change_max"
    ]

    controls_pass = all(
        x["screen_pass"]
        for x in controls.values()
    )

    laguerre_pass = all(
        max(
            row[
                "laguerre_L5_to_L6"
            ].values()
        ) <= limit
        for row in main_rows
    )

    finite_pass = all(
        max(
            row[
                "finite_F5_to_F6"
            ].values()
        ) <= limit
        for row in main_rows
    )

    if not controls_pass:
        classification = (
            "FINITE_RHO_RULE_NOT_VALIDATED"
        )
    elif finite_pass and not laguerre_pass:
        classification = (
            "LAGUERRE_RADIAL_RULE_MISMATCH_SUPPORTED"
        )
    elif finite_pass and laguerre_pass:
        classification = (
            "PSEUDOSTATE_EVENTUALLY_CONVERGES_"
            "AND_D1_LADDER_WAS_TOO_COARSE"
        )
    else:
        classification = (
            "PSEUDOSTATE_INTEGRATION_REMAINS_"
            "UNRESOLVED_UNDER_FINITE_RHO"
        )

    result = {
        "schema": (
            "BASS_FND_R3A_D2_PSEUDOSTATE_"
            "RADIAL_RULE_DISCRIMINATOR_RESULT_V1"
        ),
        "status": "DISCRIMINATOR_COMPLETE",
        "classification": classification,
        "execution_head": execution_head,
        "execution_tree": execution_tree,
        "contract_sha256": sha256_file(
            contract_path
        ),
        "projectile_speed_au": speed,
        "controls": controls,
        "main_case": contract["main_case"],
        "main_geometry": main_rows,
        "controls_pass": controls_pass,
        "laguerre_pass": laguerre_pass,
        "finite_rho_pass": finite_pass,
        "capture_execution_allowed": False,
        "capture_run_performed": False,
        "production_admission": "HOLD",
        "all_bound": "OPEN",
        "b_grid": "NO_GO",
    }

    write_new(
        out / "RESULT.json",
        result,
    )

    print()
    print(
        json.dumps(
            {
                "classification": classification,
                "controls_pass": controls_pass,
                "laguerre_pass": laguerre_pass,
                "finite_rho_pass": finite_pass,
                "result": str(
                    out / "RESULT.json"
                ),
            },
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
