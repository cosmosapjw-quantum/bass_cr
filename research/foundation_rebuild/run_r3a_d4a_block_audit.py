#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from cr_repro.observables import projectile_speed_au
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import symmetric_channels


def load_npz(path):
    with np.load(path) as f:
        return {k: np.array(f[k]) for k in ("S", "H", "D")}


def channel_labels():
    spec = RadialSpec(
        radius=64.0,
        elements=40,
        degree=4,
        lmax=1,
        bound_nmax=2,
        positive_per_l=1,
        positive_emax=2.0,
        quad_order=12,
        grading=2.0,
    )

    bank = atomic_bank(spec)
    ch = symmetric_channels(bank)

    labels = []
    for i, c in enumerate(ch):
        labels.append({
            "index": i,
            "center": "T" if c.center == 0 else "P",
            "kind": (
                "PSEUDO"
                if c.radial.principal_n is None
                else "BOUND"
            ),
            "n": c.radial.principal_n,
            "l": c.radial.l,
            "m": c.m,
            "energy_Eh": float(c.radial.energy),
        })

    return labels


def block_stats(a, b, labels):
    d = a - b
    total2 = float(np.vdot(d, d).real)

    groups = {}
    for center in ("T", "P"):
        for kind in ("BOUND", "PSEUDO"):
            name = f"{center}_{kind}"
            groups[name] = [
                x["index"]
                for x in labels
                if x["center"] == center
                and x["kind"] == kind
            ]

    rows = []

    for ga, ia in groups.items():
        if not ia:
            continue

        for gb, ib in groups.items():
            if not ib:
                continue

            ix = np.ix_(ia, ib)

            dd = d[ix]
            bb = b[ix]

            err2 = float(np.vdot(dd, dd).real)

            rows.append({
                "row_group": ga,
                "col_group": gb,
                "relative_error": float(
                    np.linalg.norm(dd)
                    / max(np.linalg.norm(bb), 1e-300)
                ),
                "error_fraction": (
                    err2 / total2
                    if total2 > 0
                    else 0.0
                ),
                "reference_norm": float(
                    np.linalg.norm(bb)
                ),
            })

    rows.sort(
        key=lambda x: x["error_fraction"],
        reverse=True,
    )

    absd = np.abs(d)
    i, j = np.unravel_index(
        np.argmax(absd),
        absd.shape,
    )

    same_center_pseudo = np.zeros_like(
        absd,
        dtype=bool,
    )
    cross_center_pseudo = np.zeros_like(
        absd,
        dtype=bool,
    )

    for i0, a0 in enumerate(labels):
        for j0, b0 in enumerate(labels):
            contains_pseudo = (
                a0["kind"] == "PSEUDO"
                or b0["kind"] == "PSEUDO"
            )

            if not contains_pseudo:
                continue

            if a0["center"] == b0["center"]:
                same_center_pseudo[i0, j0] = True
            else:
                cross_center_pseudo[i0, j0] = True

    def frac(mask):
        if total2 == 0:
            return 0.0
        return float(
            np.sum(absd[mask] ** 2)
            / total2
        )

    return {
        "global_relative_error": float(
            np.linalg.norm(d)
            / max(np.linalg.norm(b), 1e-300)
        ),
        "same_center_pseudostate_error_fraction":
            frac(same_center_pseudo),
        "cross_center_pseudostate_error_fraction":
            frac(cross_center_pseudo),
        "largest_entry": {
            "abs_difference": float(absd[i, j]),
            "row": labels[i],
            "col": labels[j],
        },
        "top_blocks": rows[:8],
    }


def compare(name, coarse, fine, labels):
    out = {"name": name, "components": {}}

    for component in ("S", "H", "D"):
        out["components"][component] = block_stats(
            coarse[component],
            fine[component],
            labels,
        )

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--d2",
        default="runs/fnd_r3a_d2_20260925",
    )
    p.add_argument(
        "--d3",
        default="runs/fnd_r3a_d3_20260925",
    )
    p.add_argument("--out", required=True)
    a = p.parse_args()

    out = Path(a.out)
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)

    d2 = Path(a.d2)
    d3 = Path(a.d3)

    labels = channel_labels()

    v = projectile_speed_au(100.0)
    b = 2.0
    rmax = 64.0

    result = {
        "schema":
            "BASS_FND_R3A_D4A_MATRIX_BLOCK_AUDIT_V1",
        "scope":
            "POSTMORTEM_EXISTING_MATRICES_NO_NEW_INTEGRATION",
        "channel_labels": labels,
        "pseudo_scales": [],
        "geometry": [],
        "capture_execution_allowed": False,
        "production_admission": "HOLD",
        "all_bound": "OPEN",
        "b_grid": "NO_GO",
    }

    seen = set()
    for x in labels:
        if x["kind"] != "PSEUDO":
            continue

        key = (x["l"], x["energy_Eh"])
        if key in seen:
            continue
        seen.add(key)

        E = x["energy_Eh"]
        k = math.sqrt(2.0 * E)

        result["pseudo_scales"].append({
            "l": x["l"],
            "energy_Eh": E,
            "free_particle_k_a0_inv": k,
            "free_particle_wavelength_a0":
                2.0 * math.pi / k,
            "diagnostic_only": True,
        })

    for z in (-12.0, 0.0):
        zs = f"{z:+05.1f}"

        L5 = load_npz(
            d2 / "matrices"
            / f"C_z{zs}_L5.npz"
        )
        L6 = load_npz(
            d2 / "matrices"
            / f"C_z{zs}_L6.npz"
        )
        F5 = load_npz(
            d2 / "matrices"
            / f"C_z{zs}_F5.npz"
        )
        F6 = load_npz(
            d2 / "matrices"
            / f"C_z{zs}_F6.npz"
        )

        E3 = load_npz(
            d3 / "matrices"
            / (
                "C_FEM_BOUND_PLUS_PSEUDOSTATE_"
                f"z{zs}_E3.npz"
            )
        )

        sep = math.sqrt(b*b + z*z)
        sin_alpha = b / sep

        row = {
            "z_a0": z,
            "separation_a0": sep,
            "sin_axis_velocity_angle": sin_alpha,
            "ETF_kappa_upper_diagnostic":
                v * rmax * sin_alpha,
            "comparisons": [
                compare(
                    "D2_L5_TO_L6",
                    L5, L6, labels,
                ),
                compare(
                    "D2_F5_TO_F6",
                    F5, F6, labels,
                ),
                compare(
                    "D2_F6_VS_L6",
                    F6, L6, labels,
                ),
                compare(
                    "D3_E3_VS_D2_L6",
                    E3, L6, labels,
                ),
            ],
        }

        result["geometry"].append(row)

    path = out / "RESULT.json"
    path.write_text(
        json.dumps(
            result,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )

    print(json.dumps({
        "result": str(path),
        "pseudo_scales":
            result["pseudo_scales"],
        "kappa": [
            {
                "z_a0": x["z_a0"],
                "ETF_kappa_upper_diagnostic":
                    x["ETF_kappa_upper_diagnostic"],
            }
            for x in result["geometry"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
