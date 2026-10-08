#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

from cr_repro.observables import projectile_speed_au
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import (
    Trajectory,
    Quadrature,
    assemble,
    hydrogen_channels,
    symmetric_channels,
)


SCHEMA = "BASS_FND_R3A_D1_QUADRATURE_BASIS_DISCRIMINATOR_RESULT_V1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        text=True,
    ).strip()


def write_new_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def rel_change(coarse: np.ndarray, fine: np.ndarray) -> float:
    den = max(float(np.linalg.norm(fine)), 1.0e-300)
    return float(np.linalg.norm(fine - coarse) / den)


def hermiticity_relative(a: np.ndarray) -> float:
    den = max(float(np.linalg.norm(a)), 1.0e-300)
    return float(np.linalg.norm(a - a.conj().T) / den)


def check_sha(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(
            f"source identity mismatch: {path}: "
            f"expected={expected}, actual={actual}"
        )


def radial_rows(bank):
    rows = []
    for r in bank:
        row = {
            "l": int(r.l),
            "principal_n": (
                None if r.principal_n is None
                else int(r.principal_n)
            ),
            "energy_Eh": float(r.energy),
            "residual": float(r.residual),
            "identity": r.identity,
            "kind": (
                "BOUND_FINITE_DOMAIN"
                if r.principal_n is not None
                else "POSITIVE_FINITE_DOMAIN_PSEUDOSTATE"
            ),
        }
        if r.principal_n is not None:
            exact = -0.5 / r.principal_n**2
            row["exact_Eh"] = float(exact)
            row["abs_energy_error_Eh"] = float(
                abs(r.energy - exact)
            )
        rows.append(row)
    return rows


def build_basis(case):
    kind = case["kind"]

    if kind == "ANALYTIC_HYDROGEN":
        channels = hydrogen_channels(int(case["nmax"]))
        return {
            "channels": channels,
            "radial_rows": [],
            "max_bound_energy_error_Eh": 0.0,
        }

    if kind == "RADIAL_FEM":
        spec = RadialSpec(**case["radial_spec"])
        bank = atomic_bank(spec)
        channels = symmetric_channels(bank)

        rows = radial_rows(bank)
        errors = [
            r["abs_energy_error_Eh"]
            for r in rows
            if r["principal_n"] is not None
        ]

        return {
            "channels": channels,
            "radial_spec": spec.__dict__,
            "radial_rows": rows,
            "max_bound_energy_error_Eh": max(errors),
        }

    raise ValueError(f"unknown basis kind {kind!r}")


def q_from_record(qr):
    return Quadrature(
        int(qr["nrad"]),
        int(qr["neta"]),
        int(qr["nphi"]),
        float(qr["scale"]),
    )


def matrix_summary(snapshot):
    ev = np.linalg.eigvalsh(snapshot.S)

    return {
        "identity": snapshot.identity,
        "S_hermiticity_relative": hermiticity_relative(snapshot.S),
        "H_hermiticity_relative": hermiticity_relative(snapshot.H),
        "metric_lambda_min": float(ev[0]),
        "metric_lambda_max": float(ev[-1]),
        "metric_ratio": float(ev[0] / ev[-1]),
        "S_norm": float(np.linalg.norm(snapshot.S)),
        "H_norm": float(np.linalg.norm(snapshot.H)),
        "D_norm": float(np.linalg.norm(snapshot.D)),
    }


def evaluate_geometry(
    *,
    outdir: Path,
    basis_id: str,
    channels,
    trajectory,
    z: float,
    speed: float,
    qrecords,
    screens,
):
    t = float(z / speed)

    snapshots = []
    qrows = []

    for qr in qrecords:
        qid = qr["id"]
        q = q_from_record(qr)

        tic = time.perf_counter()
        snap = assemble(
            trajectory,
            channels,
            t,
            q,
        )
        wall = time.perf_counter() - tic

        matrix_path = (
            outdir
            / "matrices"
            / f"{basis_id}_z{z:+05.1f}_{qid}.npz"
        )
        matrix_path.parent.mkdir(parents=True, exist_ok=True)

        if matrix_path.exists():
            raise FileExistsError(matrix_path)

        with matrix_path.open("xb") as f:
            np.savez_compressed(
                f,
                S=snap.S,
                H=snap.H,
                D=snap.D,
            )

        row = {
            "quadrature_id": qid,
            "quadrature": qr,
            "wall_seconds": wall,
            "matrix_file": str(matrix_path),
            "matrix_file_sha256": sha256_file(matrix_path),
            **matrix_summary(snap),
        }

        qrows.append(row)
        snapshots.append(snap)

        partial_path = (
            outdir
            / "partials"
            / f"{basis_id}_z{z:+05.1f}_{qid}.json"
        )
        write_new_json(partial_path, row)

        print(json.dumps({
            "basis": basis_id,
            "z_a0": z,
            "quadrature": qid,
            "wall_seconds": wall,
            "metric_ratio": row["metric_ratio"],
        }), flush=True)

    if len(snapshots) != 3:
        raise RuntimeError("D1 contract requires exactly Q3,Q4,Q5")

    q3, q4, q5 = snapshots

    q3q4 = {
        name: rel_change(
            getattr(q3, name),
            getattr(q4, name),
        )
        for name in ("S", "H", "D")
    }

    q4q5 = {
        name: rel_change(
            getattr(q4, name),
            getattr(q5, name),
        )
        for name in ("S", "H", "D")
    }

    refined = matrix_summary(q5)

    failures = []

    limit = screens[
        "final_q4_to_q5_relative_matrix_change_max"
    ]

    for name, value in q4q5.items():
        if value > limit:
            failures.append(
                f"{name} Q4->Q5={value:.9e} > {limit:.9e}"
            )

    if (
        refined["metric_ratio"]
        < screens["metric_eigenvalue_ratio_min"]
    ):
        failures.append(
            "metric_ratio="
            f"{refined['metric_ratio']:.9e} < "
            f"{screens['metric_eigenvalue_ratio_min']:.9e}"
        )

    if (
        refined["S_hermiticity_relative"]
        > screens["S_hermiticity_relative_max"]
    ):
        failures.append(
            "S_hermiticity="
            f"{refined['S_hermiticity_relative']:.9e}"
        )

    if (
        refined["H_hermiticity_relative"]
        > screens["H_hermiticity_relative_max"]
    ):
        failures.append(
            "H_hermiticity="
            f"{refined['H_hermiticity_relative']:.9e}"
        )

    return {
        "z_a0": float(z),
        "t_au": t,
        "separation_a0": float(
            np.sqrt(
                trajectory.origins[1, 0] ** 2
                + z**2
            )
        ),
        "quadratures": qrows,
        "q3_to_q4": q3q4,
        "q4_to_q5": q4q5,
        "refined_Q5": refined,
        "screen_pass": not failures,
        "failures": failures,
    }


def classification(case_results):
    by_id = {
        row["basis_id"]: row
        for row in case_results
    }

    A = by_id["A_ANALYTIC_BOUND"]["screen_pass"]
    B = by_id["B_FEM_BOUND_ONLY"]["screen_pass"]
    C = by_id[
        "C_FEM_BOUND_PLUS_PSEUDOSTATE"
    ]["screen_pass"]

    if not A:
        return (
            "ANALYTIC_BOUND_CROSS_CENTER_"
            "QUADRATURE_UNRESOLVED"
        )

    if not B:
        return (
            "FEM_BOUND_CROSS_CENTER_"
            "INTEGRATION_UNRESOLVED"
        )

    if not C:
        return (
            "POSITIVE_PSEUDOSTATE_CROSS_CENTER_"
            "INTEGRATION_UNRESOLVED"
        )

    return "ORIGINAL_R3A_QUADRATURE_LADDER_TOO_COARSE_SUPPORTED"


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--contract",
        default=(
            "research/foundation_rebuild/"
            "R3A_D1_DISCRIMINATOR_CONTRACT.json"
        ),
    )
    p.add_argument("--out", required=True)
    args = p.parse_args()

    contract_path = Path(args.contract)
    outdir = Path(args.out)

    if outdir.exists():
        raise FileExistsError(
            f"create-only output already exists: {outdir}"
        )

    outdir.mkdir(parents=True)

    contract = json.loads(
        contract_path.read_text(encoding="utf-8")
    )

    if contract["schema"] != (
        "BASS_FND_R3A_D1_QUADRATURE_"
        "BASIS_DISCRIMINATOR_V1"
    ):
        raise RuntimeError("unexpected D1 contract schema")

    if contract["status"] != "PREREGISTERED_NOT_RUN":
        raise RuntimeError("contract status is not preregistered")

    check_sha(
        Path(contract["upstream_r3a_contract"]["path"]),
        contract["upstream_r3a_contract"]["sha256"],
    )

    check_sha(
        Path(contract["upstream_r3a_failure"]["path"]),
        contract["upstream_r3a_failure"]["sha256"],
    )

    required_ancestor = contract[
        "preregistration_parent_commit"
    ]

    ancestry = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            required_ancestor,
            "HEAD",
        ]
    )

    if ancestry.returncode != 0:
        raise RuntimeError(
            "preregistration parent is not an ancestor of HEAD"
        )

    execution_head = git("rev-parse", "HEAD")
    execution_tree = git("rev-parse", "HEAD^{tree}")

    speed = projectile_speed_au(
        contract["energy_keV_per_u"]
    )

    b = float(contract["b_a0"])

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

    screens = contract["screens"]
    qrecords = contract["quadrature_ladder"]

    case_results = []

    for case in contract["basis_cases"]:
        basis_id = case["id"]

        print(
            json.dumps({
                "event": "basis_start",
                "basis": basis_id,
            }),
            flush=True,
        )

        built = build_basis(case)
        channels = built["channels"]

        if len(channels) != case["expected_channel_count"]:
            raise RuntimeError(
                f"{basis_id}: expected "
                f"{case['expected_channel_count']} channels, "
                f"got {len(channels)}"
            )

        failures = []

        energy_error = built[
            "max_bound_energy_error_Eh"
        ]

        if (
            case["kind"] == "RADIAL_FEM"
            and energy_error
            > screens[
                "fem_bound_state_abs_energy_error_Eh_max"
            ]
        ):
            failures.append(
                "FEM bound energy max error="
                f"{energy_error:.9e}"
            )

        geometry_rows = []

        for z in contract["z_samples_a0"]:
            row = evaluate_geometry(
                outdir=outdir,
                basis_id=basis_id,
                channels=channels,
                trajectory=trajectory,
                z=float(z),
                speed=speed,
                qrecords=qrecords,
                screens=screens,
            )

            geometry_rows.append(row)

            failures.extend(
                f"z={z}: {msg}"
                for msg in row["failures"]
            )

        result = {
            "basis_id": basis_id,
            "kind": case["kind"],
            "channel_count": len(channels),
            "radial_spec": built.get("radial_spec"),
            "radial_rows": built["radial_rows"],
            "max_bound_energy_error_Eh": energy_error,
            "geometry": geometry_rows,
            "screen_pass": not failures,
            "failures": failures,
        }

        case_results.append(result)

        write_new_json(
            outdir
            / f"{basis_id}_RESULT.json",
            result,
        )

        print(
            json.dumps({
                "event": "basis_complete",
                "basis": basis_id,
                "screen_pass": result["screen_pass"],
                "failure_count": len(failures),
            }),
            flush=True,
        )

    discrim = classification(case_results)

    all_pass = all(
        row["screen_pass"]
        for row in case_results
    )

    final = {
        "schema": SCHEMA,
        "status": (
            "PASS_ALL_DECLARED_CASES"
            if all_pass
            else "DISCRIMINATOR_IDENTIFIED_BLOCKER"
        ),
        "classification": discrim,
        "scope": (
            "QUADRATURE_BASIS_DISCRIMINATOR_"
            "NOT_COLLISION"
        ),
        "contract_path": str(contract_path),
        "contract_sha256": sha256_file(contract_path),
        "execution_head": execution_head,
        "execution_tree": execution_tree,
        "energy_keV_per_u": contract[
            "energy_keV_per_u"
        ],
        "projectile_speed_au": speed,
        "b_a0": b,
        "z_samples_a0": contract[
            "z_samples_a0"
        ],
        "screens": screens,
        "cases": case_results,
        "capture_execution_allowed": all_pass,
        "capture_run_performed": False,
        "production_admission": "HOLD",
        "all_bound": "OPEN",
        "b_grid": "NO_GO",
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "OMP_NUM_THREADS": os.getenv(
                "OMP_NUM_THREADS"
            ),
            "OPENBLAS_NUM_THREADS": os.getenv(
                "OPENBLAS_NUM_THREADS"
            ),
        },
    }

    write_new_json(
        outdir / "RESULT.json",
        final,
    )

    print()
    print(json.dumps({
        "status": final["status"],
        "classification": discrim,
        "capture_execution_allowed": all_pass,
        "result": str(outdir / "RESULT.json"),
    }, indent=2))

    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
