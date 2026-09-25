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

from bass_foundations.radial_basis import (
    RadialSpec,
    atomic_bank,
)

from bass_foundations.two_center import (
    Trajectory,
    Quadrature,
    assemble,
    basis_values,
    symmetric_channels,
)


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for block in iter(
            lambda: f.read(1 << 20),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("x") as f:
        json.dump(
            value,
            f,
            indent=2,
            allow_nan=False,
        )
        f.write("\n")


def rel(a, b):
    return float(
        np.linalg.norm(a - b)
        / max(
            float(np.linalg.norm(b)),
            1.0e-300,
        )
    )


def merged_breaks(values, lo, hi):
    vals = sorted(
        x for x in values
        if lo <= x <= hi
    )

    out = []

    for x in vals:
        if (
            not out
            or abs(x - out[-1])
            > 1.0e-12
        ):
            out.append(float(x))

    if not out or out[0] != lo:
        out.insert(0, float(lo))

    if out[-1] != hi:
        out.append(float(hi))

    return out


def outer_breakpoints(
    edges,
    separation,
):
    rmax = float(edges[-1])

    vals = {
        0.0,
        rmax,
    }

    for e in edges:
        e = float(e)

        vals.add(e)

        vals.add(
            abs(separation - e)
        )

        vals.add(
            separation + e
        )

    return merged_breaks(
        vals,
        0.0,
        rmax,
    )


def cross_indices(channels):
    target = [
        i
        for i, c in enumerate(channels)
        if c.center == 0
    ]

    projectile = [
        i
        for i, c in enumerate(channels)
        if c.center == 1
    ]

    return target, projectile


def accumulate_cross(
    *,
    S_tp,
    S_pt,
    H_tp,
    H_pt,
    D_tp,
    D_pt,
    points,
    weights,
    trajectory,
    channels,
    target,
    projectile,
    t,
):
    B, g, dot = basis_values(
        points,
        channels,
        trajectory,
        t,
    )

    BT = B[:, target]
    BP = B[:, projectile]

    dT = dot[:, target]
    dP = dot[:, projectile]

    centers = trajectory.centers(t)

    V = -sum(
        trajectory.charges[c]
        / np.linalg.norm(
            points - centers[c],
            axis=1,
        )
        for c in (0, 1)
    )

    S_tp += (
        BT.conj().T
        @ (weights[:, None] * BP)
    )

    S_pt += (
        BP.conj().T
        @ (weights[:, None] * BT)
    )

    H_tp += (
        BT.conj().T
        @ (
            (weights * V)[:, None]
            * BP
        )
    )

    H_pt += (
        BP.conj().T
        @ (
            (weights * V)[:, None]
            * BT
        )
    )

    for axis in range(3):
        gT = g[:, target, axis]
        gP = g[:, projectile, axis]

        H_tp += (
            0.5
            * gT.conj().T
            @ (
                weights[:, None]
                * gP
            )
        )

        H_pt += (
            0.5
            * gP.conj().T
            @ (
                weights[:, None]
                * gT
            )
        )

    D_tp += (
        BT.conj().T
        @ (weights[:, None] * dP)
    )

    D_pt += (
        BP.conj().T
        @ (weights[:, None] * dT)
    )


def geometry_aligned_cross(
    trajectory,
    channels,
    edges,
    t,
    radial_order,
    nphi,
):
    centers = trajectory.centers(t)

    delta = centers[1] - centers[0]

    R = float(
        np.linalg.norm(delta)
    )

    if R <= 0.0:
        raise ValueError(
            "nonzero focal separation required"
        )

    rmax = float(edges[-1])

    if R >= 2.0 * rmax:
        raise ValueError(
            "disjoint finite supports"
        )

    ez = delta / R

    axis = np.eye(3)[
        int(
            np.argmin(
                np.abs(ez)
            )
        )
    ]

    e1 = np.cross(
        ez,
        axis,
    )

    e1 /= np.linalg.norm(e1)

    e2 = np.cross(
        ez,
        e1,
    )

    xg, wg = leggauss(
        radial_order
    )

    phi = (
        2.0
        * np.pi
        * np.arange(nphi)
        / nphi
    )

    cp = np.cos(phi)
    sp = np.sin(phi)

    dphi = (
        2.0
        * np.pi
        / nphi
    )

    target, projectile = (
        cross_indices(channels)
    )

    nt = len(target)
    np_ = len(projectile)

    S_tp = np.zeros(
        (nt, np_),
        complex,
    )

    S_pt = np.zeros(
        (np_, nt),
        complex,
    )

    H_tp = np.zeros_like(S_tp)
    H_pt = np.zeros_like(S_pt)

    D_tp = np.zeros_like(S_tp)
    D_pt = np.zeros_like(S_pt)

    outer = outer_breakpoints(
        edges,
        R,
    )

    volume = 0.0
    point_count = 0
    radial_cells = 0

    for ia in range(
        len(outer) - 1
    ):
        a0 = outer[ia]
        b0 = outer[ia + 1]

        if b0 <= a0:
            continue

        r0_nodes = (
            0.5
            * (b0 - a0)
            * xg
            + 0.5
            * (a0 + b0)
        )

        r0_weights = (
            0.5
            * (b0 - a0)
            * wg
        )

        for r0, wr0 in zip(
            r0_nodes,
            r0_weights,
        ):
            lower = abs(
                R - r0
            )

            upper = min(
                R + r0,
                rmax,
            )

            if upper <= lower:
                continue

            inner_values = {
                float(lower),
                float(upper),
            }

            for e in edges:
                e = float(e)

                if (
                    lower
                    < e
                    < upper
                ):
                    inner_values.add(e)

            inner = merged_breaks(
                inner_values,
                lower,
                upper,
            )

            for ib in range(
                len(inner) - 1
            ):
                a1 = inner[ib]
                b1 = inner[ib + 1]

                if b1 <= a1:
                    continue

                radial_cells += 1

                r1_nodes = (
                    0.5
                    * (b1 - a1)
                    * xg
                    + 0.5
                    * (a1 + b1)
                )

                r1_weights = (
                    0.5
                    * (b1 - a1)
                    * wg
                )

                for r1, wr1 in zip(
                    r1_nodes,
                    r1_weights,
                ):
                    axial = (
                        r0*r0
                        - r1*r1
                        + R*R
                    ) / (2.0 * R)

                    perp2 = (
                        r0*r0
                        - axial*axial
                    )

                    if perp2 < -1.0e-11:
                        raise ArithmeticError(
                            "negative transverse "
                            "radius beyond roundoff"
                        )

                    perp = math.sqrt(
                        max(
                            perp2,
                            0.0,
                        )
                    )

                    points = (
                        centers[0]
                        + axial * ez
                        + perp
                        * (
                            cp[:, None]
                            * e1
                            + sp[:, None]
                            * e2
                        )
                    )

                    weight_scalar = (
                        wr0
                        * wr1
                        * r0
                        * r1
                        / R
                        * dphi
                    )

                    weights = np.full(
                        nphi,
                        weight_scalar,
                        dtype=float,
                    )

                    volume += float(
                        weights.sum()
                    )

                    point_count += nphi

                    accumulate_cross(
                        S_tp=S_tp,
                        S_pt=S_pt,
                        H_tp=H_tp,
                        H_pt=H_pt,
                        D_tp=D_tp,
                        D_pt=D_pt,
                        points=points,
                        weights=weights,
                        trajectory=trajectory,
                        channels=channels,
                        target=target,
                        projectile=projectile,
                        t=t,
                    )

    analytic_volume = (
        math.pi
        * (2.0*rmax - R)**2
        * (4.0*rmax + R)
        / 12.0
    )

    volume_rel_error = abs(
        volume - analytic_volume
    ) / analytic_volume

    return {
        "S_tp": S_tp,
        "S_pt": S_pt,
        "H_tp": H_tp,
        "H_pt": H_pt,
        "D_tp": D_tp,
        "D_pt": D_pt,

        "metadata": {
            "separation_a0": R,
            "rmax_a0": rmax,
            "outer_breakpoint_count":
                len(outer),
            "outer_interval_count":
                len(outer) - 1,
            "radial_cells":
                radial_cells,
            "quadrature_points":
                point_count,
            "numeric_intersection_volume":
                volume,
            "analytic_intersection_volume":
                analytic_volume,
            "volume_relative_error":
                volume_rel_error,
            "measure":
                "rT*rP/R drT drP dphi",
            "support":
                "EXACT_CROSS_BLOCK_INTERSECTION",
            "geometry_breakpoints":
                True,
        },
    }


def matrix_part(x):
    return {
        "S": x["S_tp"],
        "H": x["H_tp"],
        "D": x["D_tp"],
    }


def compare(a, b):
    aa = matrix_part(a)
    bb = matrix_part(b)

    return {
        key: rel(
            aa[key],
            bb[key],
        )
        for key in (
            "S",
            "H",
            "D",
        )
    }


def pair_defects(x):
    return {
        "S": rel(
            x["S_tp"],
            x["S_pt"].conj().T,
        ),
        "H": rel(
            x["H_tp"],
            x["H_pt"].conj().T,
        ),
    }


def standard_bound_reference(
    trajectory,
    channels,
    t,
    record,
):
    snap = assemble(
        trajectory,
        channels,
        t,
        Quadrature(
            record["nrad"],
            record["neta"],
            record["nphi"],
            record["scale"],
        ),
    )

    target, projectile = (
        cross_indices(channels)
    )

    ix_tp = np.ix_(
        target,
        projectile,
    )

    ix_pt = np.ix_(
        projectile,
        target,
    )

    return {
        "S_tp": snap.S[ix_tp],
        "S_pt": snap.S[ix_pt],
        "H_tp": snap.H[ix_tp],
        "H_pt": snap.H[ix_pt],
        "D_tp": snap.D[ix_tp],
        "D_pt": snap.D[ix_pt],
    }


def make_banks(spec_dict):
    full_spec = RadialSpec(
        **spec_dict
    )

    bound_spec = RadialSpec(
        **{
            **spec_dict,
            "positive_per_l": 0,
        }
    )

    return {
        "B_FEM_BOUND_ONLY":
            atomic_bank(bound_spec),

        "C_FEM_BOUND_PLUS_PSEUDOSTATE":
            atomic_bank(full_spec),
    }


def save_npz(path, x):
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    ap.add_argument(
        "--contract",
        required=True,
    )

    ap.add_argument(
        "--out",
        required=True,
    )

    args = ap.parse_args()

    contract_path = Path(
        args.contract
    )

    out = Path(args.out)

    if out.exists():
        raise FileExistsError(out)

    out.mkdir(parents=True)

    c = json.loads(
        contract_path.read_text()
    )

    if (
        sha256_file(
            c["d4b_result"]["path"]
        )
        !=
        c["d4b_result"]["sha256"]
    ):
        raise RuntimeError(
            "D4B identity mismatch"
        )

    parent = c["parent_commit"]

    if subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            parent,
            "HEAD",
        ]
    ).returncode:
        raise RuntimeError(
            "preregistration parent "
            "is not ancestor"
        )

    head = subprocess.check_output(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        text=True,
    ).strip()

    tree = subprocess.check_output(
        [
            "git",
            "rev-parse",
            "HEAD^{tree}",
        ],
        text=True,
    ).strip()

    speed = projectile_speed_au(
        c["energy_keV_per_u"]
    )

    b = float(c["b_a0"])
    z = float(c["z_a0"])

    t = z / speed

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

    banks = make_banks(
        c["fem_spec"]
    )

    screens = c["screens"]

    results = {}

    for basis_id in c[
        "basis_cases"
    ]:
        bank = banks[basis_id]

        channels = symmetric_channels(
            bank
        )

        edges = np.asarray(
            bank[0].edges
        )

        for mode in bank[1:]:
            if not np.array_equal(
                edges,
                mode.edges,
            ):
                raise RuntimeError(
                    "FEM edge identity mismatch"
                )

        ladder_rows = []
        runs = []

        for level in c[
            "element_pair_ladder"
        ]:
            tic = time.perf_counter()

            run = geometry_aligned_cross(
                trajectory,
                channels,
                edges,
                t,
                level["radial_order"],
                level["nphi"],
            )

            wall = (
                time.perf_counter()
                - tic
            )

            run["wall_seconds"] = wall

            matrix_path = (
                out
                / "matrices"
                / (
                    f"{basis_id}_"
                    f"{level['id']}.npz"
                )
            )

            save_npz(
                matrix_path,
                run,
            )

            row = {
                "level": level,
                "wall_seconds": wall,
                "matrix_sha256":
                    sha256_file(
                        matrix_path
                    ),
                "metadata":
                    run["metadata"],
                "pair_defects":
                    pair_defects(run),
            }

            ladder_rows.append(row)
            runs.append(run)

            print(
                json.dumps({
                    "basis": basis_id,
                    "level":
                        level["id"],
                    "seconds":
                        wall,
                    "points":
                        run[
                            "metadata"
                        ][
                            "quadrature_points"
                        ],
                    "radial_cells":
                        run[
                            "metadata"
                        ][
                            "radial_cells"
                        ],
                    "volume_rel_error":
                        run[
                            "metadata"
                        ][
                            "volume_relative_error"
                        ],
                }),
                flush=True,
            )

        G1, G2, G3 = runs

        changes = {
            "G1_to_G2":
                compare(
                    G1,
                    G2,
                ),
            "G2_to_G3":
                compare(
                    G2,
                    G3,
                ),
        }

        failures = []

        volume_limit = screens[
            "sphere_intersection_volume_relative_error_max"
        ]

        for idx, row in enumerate(
            ladder_rows
        ):
            verr = row[
                "metadata"
            ][
                "volume_relative_error"
            ]

            if verr > volume_limit:
                failures.append(
                    f"{row['level']['id']}: "
                    f"volume error={verr:.9e}"
                )

        matrix_limit = screens[
            "G2_to_G3_relative_matrix_change_max"
        ]

        for name, value in (
            changes[
                "G2_to_G3"
            ].items()
        ):
            if value > matrix_limit:
                failures.append(
                    f"{name} G2->G3="
                    f"{value:.9e}"
                )

        pair = pair_defects(
            G3
        )

        if (
            pair["S"]
            >
            screens[
                "S_cross_conjugacy_relative_max"
            ]
        ):
            failures.append(
                "S cross conjugacy="
                f"{pair['S']:.9e}"
            )

        if (
            pair["H"]
            >
            screens[
                "H_cross_conjugacy_relative_max"
            ]
        ):
            failures.append(
                "H cross conjugacy="
                f"{pair['H']:.9e}"
            )

        control = None

        if (
            basis_id
            == "B_FEM_BOUND_ONLY"
        ):
            reference = (
                standard_bound_reference(
                    trajectory,
                    channels,
                    t,
                    c[
                        "bound_control_reference"
                    ],
                )
            )

            control = compare(
                G3,
                reference,
            )

            control_limit = screens[
                "B_control_G3_vs_reference_relative_max"
            ]

            for name, value in (
                control.items()
            ):
                if value > control_limit:
                    failures.append(
                        f"B control {name}="
                        f"{value:.9e}"
                    )

        results[basis_id] = {
            "channel_count":
                len(channels),

            "ladder":
                ladder_rows,

            "changes":
                changes,

            "G3_pair_defects":
                pair,

            "G3_vs_bound_reference":
                control,

            "screen_pass":
                len(failures) == 0,

            "failures":
                failures,
        }

    Bpass = results[
        "B_FEM_BOUND_ONLY"
    ]["screen_pass"]

    Cpass = results[
        "C_FEM_BOUND_PLUS_PSEUDOSTATE"
    ]["screen_pass"]

    volume_pass = all(
        row["metadata"][
            "volume_relative_error"
        ]
        <= screens[
            "sphere_intersection_volume_relative_error_max"
        ]
        for result
        in results.values()
        for row
        in result["ladder"]
    )

    if not volume_pass:
        classification = (
            "GEOMETRY_JACOBIAN_"
            "DOMAIN_ORACLE_FAIL"
        )

    elif not Bpass:
        classification = (
            "GEOMETRY_ALIGNED_"
            "BOUND_CONTROL_FAIL"
        )

    elif not Cpass:
        classification = (
            "PSEUDOSTATE_CROSS_BLOCK_"
            "REMAINS_UNRESOLVED"
        )

    else:
        classification = (
            "GEOMETRY_ALIGNMENT_"
            "RESOLVES_LARGE_SEPARATION_"
            "CROSS_BLOCK"
        )

    result = {
        "schema":
            "BASS_FND_R3A_D4C_"
            "GEOMETRY_ALIGNED_"
            "CROSS_RESULT_V1",

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

        "z_a0":
            z,

        "separation_a0":
            float(
                math.sqrt(
                    b*b + z*z
                )
            ),

        "results":
            results,

        "volume_oracle_pass":
            volume_pass,

        "bound_control_pass":
            Bpass,

        "pseudostate_cross_pass":
            Cpass,

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

    print(
        json.dumps(
            {
                "classification":
                    classification,

                "volume_oracle_pass":
                    volume_pass,

                "bound_control_pass":
                    Bpass,

                "pseudostate_cross_pass":
                    Cpass,

                "result":
                    str(
                        out
                        / "RESULT.json"
                    ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
