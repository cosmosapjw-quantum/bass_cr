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

from cr_repro.observables import projectile_speed_au
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import Trajectory, symmetric_channels

from run_r3a_d4b_cross_block import (
    cross_assemble,
    compare,
    defects,
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

    c = json.loads(contract_path.read_text())

    if sha256_file(c["d4c_result"]["path"]) != c["d4c_result"]["sha256"]:
        raise RuntimeError("D4C result identity mismatch")

    if subprocess.run([
        "git",
        "merge-base",
        "--is-ancestor",
        c["parent_commit"],
        "HEAD",
    ]).returncode:
        raise RuntimeError("preregistration parent is not ancestor")

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()

    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"],
        text=True,
    ).strip()

    v = projectile_speed_au(c["energy_keV_per_u"])
    b = float(c["b_a0"])
    z = float(c["z_a0"])

    R = math.sqrt(b*b + z*z)
    t = z / v

    spec = RadialSpec(**c["fem_spec"])
    bank = atomic_bank(spec)
    channels = symmetric_channels(bank)

    trajectory = Trajectory(
        origins=((0., 0., 0.), (b, 0., 0.)),
        velocities=((0., 0., 0.), (0., 0., v)),
        charges=(1., 1.),
    )

    # Cross-support diagnostic maximum occurs at eta=0:
    # rho_max = Rbox - R/2, mu_max = 2 Rbox / R.
    rho_support_max = max(0.0, spec.radius - 0.5*R)
    mu_support_max = 1.0 + 2.0*rho_support_max/R

    q_eta_max = 0.5 * abs(v*z) * mu_support_max
    q_phi_max = (
        0.5 * abs(v*b)
        * math.sqrt(max(mu_support_max**2 - 1.0, 0.0))
    )

    cache = {}

    def run(rec, label):
        key = (
            int(rec["nrho"]),
            int(rec["neta"]),
            int(rec["nphi"]),
        )

        if key in cache:
            return cache[key]

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

        x["wall_seconds"] = time.perf_counter() - tic
        cache[key] = x

        tag = (
            f"{label}_"
            f"r{rec['nrho']}_"
            f"e{rec['neta']}_"
            f"p{rec['nphi']}"
        )

        matrix_path = out / "matrices" / f"{tag}.npz"
        save_npz(matrix_path, x)

        receipt = {
            "label": label,
            "nrho": rec["nrho"],
            "neta": rec["neta"],
            "nphi": rec["nphi"],
            "points": x["points"],
            "wall_seconds": x["wall_seconds"],
            "matrix_sha256": sha256_file(matrix_path),
            "pair_defects": defects(x),
        }

        write_new(
            out / "partials" / f"{tag}.json",
            receipt,
        )

        print(json.dumps(receipt), flush=True)

        return x

    eta_records = c["eta_ladder"]
    eta_runs = [
        run(rec, "ETA")
        for rec in eta_records
    ]

    eta_changes = [
        compare(eta_runs[i], eta_runs[i+1])
        for i in range(len(eta_runs)-1)
    ]

    eta_final = eta_changes[-1]
    eta_pair = defects(eta_runs[-1])

    eta_limit = c["screens"]["eta_final_relative_change_max"]
    pair_limit = c["screens"]["S_H_cross_conjugacy_max"]

    eta_pass = (
        max(eta_final.values()) <= eta_limit
        and max(eta_pair.values()) <= pair_limit
    )

    rho_records = []
    rho_changes = []
    rho_pair = None
    rho_pass = None

    if eta_pass:
        rho_records = c["rho_ladder_if_eta_passes"]

        rho_runs = [
            run(rec, "RHO")
            for rec in rho_records
        ]

        rho_changes = [
            compare(rho_runs[i], rho_runs[i+1])
            for i in range(len(rho_runs)-1)
        ]

        rho_final = rho_changes[-1]
        rho_pair = defects(rho_runs[-1])

        rho_limit = c["screens"]["rho_final_relative_change_max"]

        rho_pass = (
            max(rho_final.values()) <= rho_limit
            and max(rho_pair.values()) <= pair_limit
        )

    if not eta_pass:
        classification = "LONGITUDINAL_ETA_RESOLUTION_UNRESOLVED"
    elif not rho_pass:
        classification = "RHO_RESOLUTION_UNRESOLVED_AFTER_ETA_QUALIFICATION"
    else:
        classification = "FINITE_RHO_CROSS_BLOCK_AXIS_QUALIFIED"

    result = {
        "schema": "BASS_FND_R3A_D5A_AXIS_RESULT_V1",
        "status": "DISCRIMINATOR_COMPLETE",

        "classification": classification,

        "execution_head": head,
        "execution_tree": tree,
        "contract_sha256": sha256_file(contract_path),

        "z_a0": z,
        "separation_a0": R,
        "projectile_speed_au": v,

        "phase_diagnostics": {
            "rho_cross_support_max_a0": rho_support_max,
            "mu_cross_support_max": mu_support_max,
            "eta_linear_phase_coefficient_max": q_eta_max,
            "eta_phase_cycles_across_minus1_plus1":
                q_eta_max / math.pi,
            "phi_phase_coefficient_max": q_phi_max
        },

        "eta": {
            "records": eta_records,
            "successive_changes": eta_changes,
            "final_change": eta_final,
            "pair_defects": eta_pair,
            "pass": eta_pass
        },

        "rho": {
            "executed": eta_pass,
            "records": rho_records,
            "successive_changes": rho_changes,
            "pair_defects": rho_pair,
            "pass": rho_pass
        },

        "capture_execution_allowed": False,
        "capture_run_performed": False,

        "production_admission": "HOLD",
        "all_bound": "OPEN",
        "b_grid": "NO_GO"
    }

    write_new(out / "RESULT.json", result)

    print()
    print(json.dumps({
        "classification": classification,
        "eta_pass": eta_pass,
        "rho_executed": eta_pass,
        "rho_pass": rho_pass,
        "q_eta_max": q_eta_max,
        "q_phi_max": q_phi_max,
        "result": str(out / "RESULT.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
