#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

from cr_repro.observables import projectile_speed_au
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import (
    Trajectory,
    basis_values,
    symmetric_channels,
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def rel(a, b):
    return float(
        np.linalg.norm(a - b)
        / max(np.linalg.norm(b), 1e-300)
    )


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

    ez = delta / R

    axis = np.eye(3)[
        int(np.argmin(abs(ez)))
    ]

    e1 = np.cross(ez, axis)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ez, e1)

    xr, wr = leggauss(nrho)
    eta, we = leggauss(neta)

    rho = 0.5 * rho_max * (xr + 1.0)
    wr = 0.5 * rho_max * wr

    phi = (
        2.0 * np.pi
        * np.arange(nphi)
        / nphi
    )

    mu = 1.0 + 2.0 * rho / R

    transverse = (
        (R / 2.0)
        * np.sqrt(
            (mu[:, None, None] ** 2 - 1.0)
            * (
                1.0
                - eta[None, :, None] ** 2
            )
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
            np.cos(phi)[None, None, :, None]
            * e1
            + np.sin(phi)[None, None, :, None]
            * e2
        )
    )

    weights = (
        (R**2 / 4.0)
        * (
            mu[:, None] ** 2
            - eta[None, :] ** 2
        )
        * wr[:, None]
        * we[None, :]
        * (2.0 * np.pi / nphi)
    )

    weights = np.broadcast_to(
        weights[:, :, None],
        points.shape[:-1],
    ).ravel().copy()

    return points.reshape(-1, 3), weights


def cross_assemble(
    trajectory,
    channels,
    t,
    nrho,
    neta,
    nphi,
    rho_max=64.0,
    chunk=1024,
):
    points, weights = finite_rho_grid(
        trajectory,
        t,
        nrho,
        neta,
        nphi,
        rho_max,
    )

    target = [
        i for i, c in enumerate(channels)
        if c.center == 0
    ]

    projectile = [
        i for i, c in enumerate(channels)
        if c.center == 1
    ]

    nt = len(target)
    np_ = len(projectile)

    S_tp = np.zeros((nt, np_), complex)
    H_tp = np.zeros_like(S_tp)
    D_tp = np.zeros_like(S_tp)

    S_pt = np.zeros((np_, nt), complex)
    H_pt = np.zeros_like(S_pt)
    D_pt = np.zeros_like(S_pt)

    centers = trajectory.centers(t)

    for start in range(
        0,
        len(points),
        chunk,
    ):
        p = points[start:start + chunk]
        w = weights[start:start + chunk]

        B, g, dot = basis_values(
            p,
            channels,
            trajectory,
            t,
        )

        BT = B[:, target]
        BP = B[:, projectile]

        dT = dot[:, target]
        dP = dot[:, projectile]

        V = -sum(
            trajectory.charges[c]
            / np.linalg.norm(
                p - centers[c],
                axis=1,
            )
            for c in (0, 1)
        )

        S_tp += (
            BT.conj().T
            @ (w[:, None] * BP)
        )

        S_pt += (
            BP.conj().T
            @ (w[:, None] * BT)
        )

        H_tp += (
            BT.conj().T
            @ ((w * V)[:, None] * BP)
        )

        H_pt += (
            BP.conj().T
            @ ((w * V)[:, None] * BT)
        )

        for j in range(3):
            gT = g[:, target, j]
            gP = g[:, projectile, j]

            H_tp += (
                0.5
                * gT.conj().T
                @ (w[:, None] * gP)
            )

            H_pt += (
                0.5
                * gP.conj().T
                @ (w[:, None] * gT)
            )

        D_tp += (
            BT.conj().T
            @ (w[:, None] * dP)
        )

        D_pt += (
            BP.conj().T
            @ (w[:, None] * dT)
        )

    return {
        "S_tp": S_tp,
        "S_pt": S_pt,
        "H_tp": H_tp,
        "H_pt": H_pt,
        "D_tp": D_tp,
        "D_pt": D_pt,
        "points": len(points),
    }


def compact(x):
    return {
        "S": x["S_tp"],
        "H": x["H_tp"],
        "D": x["D_tp"],
    }


def compare(a, b):
    aa = compact(a)
    bb = compact(b)

    return {
        name: rel(
            aa[name],
            bb[name],
        )
        for name in ("S", "H", "D")
    }


def defects(x):
    return {
        "S_TP_vs_PT_dagger": rel(
            x["S_tp"],
            x["S_pt"].conj().T,
        ),
        "H_TP_vs_PT_dagger": rel(
            x["H_tp"],
            x["H_pt"].conj().T,
        ),
    }


def save_npz(path, x):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("xb") as f:
        np.savez_compressed(
            f,
            S_tp=x["S_tp"],
            S_pt=x["S_pt"],
            H_tp=x["H_tp"],
            H_pt=x["H_pt"],
            D_tp=x["D_tp"],
            D_pt=x["D_pt"],
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    contract_path = Path(a.contract)
    out = Path(a.out)

    if out.exists():
        raise FileExistsError(out)

    out.mkdir(parents=True)

    c = json.loads(
        contract_path.read_text()
    )

    d4a = c["d4a_result"]

    if (
        sha256_file(d4a["path"])
        != d4a["sha256"]
    ):
        raise RuntimeError(
            "D4A identity mismatch"
        )

    if subprocess.run([
        "git",
        "merge-base",
        "--is-ancestor",
        c["parent_commit"],
        "HEAD",
    ]).returncode:
        raise RuntimeError(
            "preregistration parent "
            "is not ancestor"
        )

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()

    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"],
        text=True,
    ).strip()

    speed = projectile_speed_au(
        c["energy_keV_per_u"]
    )

    b = float(c["b_a0"])

    spec = RadialSpec(
        **c["fem_spec"]
    )

    bank = atomic_bank(spec)
    channels = symmetric_channels(bank)

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

    cache = {}
    rows = []

    for z in c["z_samples_a0"]:
        key = str(float(z))

        t = float(z / speed)

        sep = math.sqrt(
            b*b + z*z
        )

        sin_alpha = b / sep

        kappa = (
            speed
            * spec.radius
            * sin_alpha
        )

        def run(rec):
            k = (
                float(z),
                rec["nrho"],
                rec["neta"],
                rec["nphi"],
            )

            if k in cache:
                return cache[k]

            tic = time.perf_counter()

            x = cross_assemble(
                trajectory,
                channels,
                t,
                rec["nrho"],
                rec["neta"],
                rec["nphi"],
                spec.radius,
            )

            x["wall_seconds"] = (
                time.perf_counter()
                - tic
            )

            cache[k] = x

            tag = (
                f"z{z:+05.1f}_"
                f"r{rec['nrho']}_"
                f"e{rec['neta']}_"
                f"p{rec['nphi']}"
            )

            save_npz(
                out / "matrices"
                / f"{tag}.npz",
                x,
            )

            print(json.dumps({
                "z_a0": z,
                "nrho": rec["nrho"],
                "neta": rec["neta"],
                "nphi": rec["nphi"],
                "points": x["points"],
                "seconds":
                    x["wall_seconds"],
            }), flush=True)

            return x

        phase_records = c[
            "phase_ladders"
        ][key]

        phase_runs = [
            run(x)
            for x in phase_records
        ]

        radial_records = c[
            "radial_eta_ladders"
        ][key]

        radial_runs = [
            run(x)
            for x in radial_records
        ]

        p12 = compare(
            phase_runs[0],
            phase_runs[1],
        )

        p23 = compare(
            phase_runs[1],
            phase_runs[2],
        )

        r12 = compare(
            radial_runs[0],
            radial_runs[1],
        )

        r23 = compare(
            radial_runs[1],
            radial_runs[2],
        )

        final = radial_runs[-1]

        row = {
            "z_a0": z,
            "separation_a0": sep,
            "sin_axis_velocity_angle":
                sin_alpha,
            "ETF_kappa_upper_diagnostic":
                kappa,

            "phase_ladder":
                phase_records,
            "phase_1_to_2":
                p12,
            "phase_2_to_3":
                p23,

            "radial_eta_ladder":
                radial_records,
            "radial_eta_1_to_2":
                r12,
            "radial_eta_2_to_3":
                r23,

            "final_pair_defects":
                defects(final),
        }

        rows.append(row)

        write_new(
            out
            / "partials"
            / f"z{z:+05.1f}.json",
            row,
        )

    phase_limit = c["screens"][
        "final_phase_relative_change_max"
    ]

    radial_limit = c["screens"][
        "final_radial_eta_relative_change_max"
    ]

    pair_limit = c["screens"][
        "cross_S_H_hermitian_pair_defect_max"
    ]

    phase_pass = all(
        max(
            r["phase_2_to_3"].values()
        ) <= phase_limit
        for r in rows
    )

    radial_pass = all(
        max(
            r[
                "radial_eta_2_to_3"
            ].values()
        ) <= radial_limit
        for r in rows
    )

    pair_pass = all(
        max(
            r[
                "final_pair_defects"
            ].values()
        ) <= pair_limit
        for r in rows
    )

    if not phase_pass:
        classification = (
            "ETF_AZIMUTHAL_"
            "RESOLUTION_UNRESOLVED"
        )
    elif not radial_pass:
        classification = (
            "CROSS_CENTER_RADIAL_ETA_"
            "RESOLUTION_UNRESOLVED"
        )
    elif not pair_pass:
        classification = (
            "CROSS_BLOCK_CONJUGACY_"
            "DEFECT_UNRESOLVED"
        )
    else:
        classification = (
            "FINITE_RHO_CROSS_BLOCK_"
            "QUALIFIED_FOR_R3A_SCOPE"
        )

    result = {
        "schema":
            "BASS_FND_R3A_D4B_"
            "CROSS_BLOCK_AXIS_RESULT_V1",
        "status":
            "DISCRIMINATOR_COMPLETE",
        "classification":
            classification,
        "execution_head":
            head,
        "execution_tree":
            tree,
        "contract_sha256":
            sha256_file(
                contract_path
            ),
        "rows":
            rows,
        "phase_pass":
            phase_pass,
        "radial_eta_pass":
            radial_pass,
        "pair_conjugacy_pass":
            pair_pass,
        "capture_execution_allowed":
            False,
        "capture_run_performed":
            False,
        "production_admission":
            "HOLD",
        "all_bound":
            "OPEN",
        "b_grid":
            "NO_GO",
    }

    write_new(
        out / "RESULT.json",
        result,
    )

    print()
    print(json.dumps({
        "classification":
            classification,
        "phase_pass":
            phase_pass,
        "radial_eta_pass":
            radial_pass,
        "pair_conjugacy_pass":
            pair_pass,
        "result":
            str(out / "RESULT.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
