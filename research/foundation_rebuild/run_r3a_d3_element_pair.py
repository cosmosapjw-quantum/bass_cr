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
    Quadrature,
    assemble,
    basis_values,
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


def summary(S, H, D):
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


def add_points(
    S,
    H,
    D,
    *,
    points,
    weights,
    trajectory,
    channels,
    t,
):
    centers = trajectory.centers(t)

    B, g, dot = basis_values(
        points,
        channels,
        trajectory,
        t,
    )

    V = -sum(
        trajectory.charges[c]
        / np.linalg.norm(
            points - centers[c],
            axis=1,
        )
        for c in (0, 1)
    )

    S += B.conj().T @ (
        weights[:, None] * B
    )

    H += B.conj().T @ (
        (weights * V)[:, None] * B
    )

    for j in range(3):
        H += (
            0.5
            * g[:, :, j].conj().T
            @ (
                weights[:, None]
                * g[:, :, j]
            )
        )

    D += B.conj().T @ (
        weights[:, None] * dot
    )


def element_pair_assemble(
    trajectory,
    channels,
    edges,
    t,
    radial_order,
    nphi,
):
    """
    Integrate directly in two-center distances:

        dV = r0*r1/R dr0 dr1 dphi

    Each r0/r1 interval is aligned to the FEM radial element
    boundaries. The triangle-domain boundary is imposed through
    the allowed r1 interval for each r0 node.
    """

    centers = trajectory.centers(t)

    delta = centers[1] - centers[0]
    R = float(np.linalg.norm(delta))

    if R < 1.0e-7:
        raise ValueError("unresolved coincident centers")

    ez = delta / R

    axis = np.eye(3)[
        int(np.argmin(np.abs(ez)))
    ]

    e1 = np.cross(ez, axis)
    e1 /= np.linalg.norm(e1)

    e2 = np.cross(ez, e1)

    xg, wg = leggauss(radial_order)

    phi = (
        2.0
        * np.pi
        * np.arange(nphi)
        / nphi
    )

    cosphi = np.cos(phi)
    sinphi = np.sin(phi)
    dphi = 2.0 * np.pi / nphi

    n = len(channels)

    S = np.zeros((n, n), complex)
    H = np.zeros_like(S)
    D = np.zeros_like(S)

    accepted_radial_pairs = 0
    point_count = 0

    for i in range(len(edges) - 1):
        a0 = float(edges[i])
        b0 = float(edges[i + 1])

        r0nodes = (
            0.5 * (b0 - a0) * xg
            + 0.5 * (a0 + b0)
        )

        r0weights = (
            0.5 * (b0 - a0) * wg
        )

        for r0, wr0 in zip(
            r0nodes,
            r0weights,
        ):
            # Triangle inequality:
            #
            # |r0-r1| <= R <= r0+r1
            #
            # => |R-r0| <= r1 <= R+r0
            r1_min_global = abs(R - r0)
            r1_max_global = min(
                R + r0,
                float(edges[-1]),
            )

            if (
                r1_max_global
                <= r1_min_global
            ):
                continue

            r1_all = []
            wr1_all = []

            for j in range(
                len(edges) - 1
            ):
                lo = max(
                    float(edges[j]),
                    r1_min_global,
                )

                hi = min(
                    float(edges[j + 1]),
                    r1_max_global,
                )

                if hi <= lo:
                    continue

                accepted_radial_pairs += 1

                r1 = (
                    0.5 * (hi - lo) * xg
                    + 0.5 * (hi + lo)
                )

                wr1 = (
                    0.5 * (hi - lo) * wg
                )

                r1_all.append(r1)
                wr1_all.append(wr1)

            if not r1_all:
                continue

            r1 = np.concatenate(r1_all)
            wr1 = np.concatenate(wr1_all)

            rr = np.repeat(
                r1,
                nphi,
            )

            wrr = np.repeat(
                wr1,
                nphi,
            )

            cp = np.tile(
                cosphi,
                len(r1),
            )

            sp = np.tile(
                sinphi,
                len(r1),
            )

            # distance along the internuclear axis
            # measured from center 0
            axial = (
                r0 * r0
                - rr * rr
                + R * R
            ) / (2.0 * R)

            perp2 = (
                r0 * r0
                - axial * axial
            )

            # only tiny negative roundoff is admissible
            if np.min(perp2) < -1.0e-10:
                raise ArithmeticError(
                    "triangle-domain mapping "
                    "produced negative transverse radius"
                )

            perp = np.sqrt(
                np.maximum(perp2, 0.0)
            )

            points = (
                centers[0]
                + axial[:, None] * ez
                + perp[:, None]
                * (
                    cp[:, None] * e1
                    + sp[:, None] * e2
                )
            )

            weights = (
                wr0
                * wrr
                * (r0 * rr / R)
                * dphi
            )

            add_points(
                S,
                H,
                D,
                points=points,
                weights=weights,
                trajectory=trajectory,
                channels=channels,
                t=t,
            )

            point_count += len(points)

    return S, H, D, {
        "internuclear_separation_a0": R,
        "accepted_radial_subintervals":
            accepted_radial_pairs,
        "quadrature_points": point_count,
        "radial_order": radial_order,
        "nphi": nphi,
        "coordinate_measure":
            "r0*r1/R dr0 dr1 dphi",
        "element_aligned": True,
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

    full_bank = atomic_bank(
        full_spec
    )

    bound_bank = atomic_bank(
        bound_spec
    )

    return {
        "B_FEM_BOUND_ONLY":
            bound_bank,
        "C_FEM_BOUND_PLUS_PSEUDOSTATE":
            full_bank,
    }


def standard_assemble(
    trajectory,
    channels,
    t,
    qrec,
):
    snap = assemble(
        trajectory,
        channels,
        t,
        Quadrature(
            qrec["nrad"],
            qrec["neta"],
            qrec["nphi"],
            qrec["scale"],
        ),
    )

    return snap.S, snap.H, snap.D


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

    contract = json.loads(
        contract_path.read_text()
    )

    d2 = contract["d2_result"]

    if (
        sha256_file(d2["path"])
        != d2["sha256"]
    ):
        raise RuntimeError(
            "D2 result identity mismatch"
        )

    parent = contract[
        "parent_commit"
    ]

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
            "D3 preregistration parent "
            "is not ancestor of HEAD"
        )

    execution_head = (
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            text=True,
        ).strip()
    )

    execution_tree = (
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD^{tree}",
            ],
            text=True,
        ).strip()
    )

    speed = projectile_speed_au(
        contract[
            "energy_keV_per_u"
        ]
    )

    b = float(
        contract["b_a0"]
    )

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
        contract["fem_spec"]
    )

    ladder = contract[
        "element_pair_ladder"
    ]

    standard = contract[
        "standard_control"
    ]

    screens = contract[
        "screens"
    ]

    results = {}

    for basis_id in contract[
        "basis_cases"
    ]:
        bank = banks[basis_id]

        channels = symmetric_channels(
            bank
        )

        edges = np.asarray(
            bank[0].edges
        )

        # All states must use the exact
        # same FEM radial partition.
        for mode in bank[1:]:
            if not np.array_equal(
                edges,
                mode.edges,
            ):
                raise RuntimeError(
                    "non-common FEM edges"
                )

        geometry = []
        failures = []

        for z in contract[
            "z_samples_a0"
        ]:
            t = float(z / speed)

            matrices = []

            for level in ladder:
                tic = time.perf_counter()

                S, H, D, meta = (
                    element_pair_assemble(
                        trajectory,
                        channels,
                        edges,
                        t,
                        level[
                            "radial_order"
                        ],
                        level["nphi"],
                    )
                )

                wall = (
                    time.perf_counter()
                    - tic
                )

                path = (
                    out
                    / "matrices"
                    / (
                        f"{basis_id}_"
                        f"z{z:+05.1f}_"
                        f"{level['id']}.npz"
                    )
                )

                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                with path.open(
                    "xb"
                ) as f:
                    np.savez_compressed(
                        f,
                        S=S,
                        H=H,
                        D=D,
                    )

                matrices.append(
                    {
                        "level":
                            level,
                        "S": S,
                        "H": H,
                        "D": D,
                        "wall_seconds":
                            wall,
                        "metadata":
                            meta,
                        "summary":
                            summary(
                                S,
                                H,
                                D,
                            ),
                        "matrix_sha256":
                            sha256_file(
                                path
                            ),
                    }
                )

                print(
                    json.dumps(
                        {
                            "basis":
                                basis_id,
                            "z_a0":
                                z,
                            "level":
                                level[
                                    "id"
                                ],
                            "wall_seconds":
                                wall,
                            "points":
                                meta[
                                    "quadrature_points"
                                ],
                            "metric_ratio":
                                matrices[
                                    -1
                                ][
                                    "summary"
                                ][
                                    "metric_ratio"
                                ],
                        }
                    ),
                    flush=True,
                )

            E1, E2, E3 = matrices

            E1E2 = {
                name: rel(
                    E1[name],
                    E2[name],
                )
                for name
                in ("S", "H", "D")
            }

            E2E3 = {
                name: rel(
                    E2[name],
                    E3[name],
                )
                for name
                in ("S", "H", "D")
            }

            tic = time.perf_counter()

            LS, LH, LD = (
                standard_assemble(
                    trajectory,
                    channels,
                    t,
                    standard,
                )
            )

            standard_wall = (
                time.perf_counter()
                - tic
            )

            E3_vs_standard = {
                "S": rel(
                    E3["S"],
                    LS,
                ),
                "H": rel(
                    E3["H"],
                    LH,
                ),
                "D": rel(
                    E3["D"],
                    LD,
                ),
            }

            row = {
                "z_a0":
                    float(z),
                "separation_a0":
                    float(
                        math.sqrt(
                            b*b
                            + z*z
                        )
                    ),
                "E1_to_E2":
                    E1E2,
                "E2_to_E3":
                    E2E3,
                "E3":
                    E3[
                        "summary"
                    ],
                "E3_metadata":
                    E3[
                        "metadata"
                    ],
                "E3_vs_standard_L6":
                    E3_vs_standard,
                "standard_L6":
                    summary(
                        LS,
                        LH,
                        LD,
                    ),
                "standard_wall_seconds":
                    standard_wall,
            }

            geometry.append(
                row
            )

            limit = screens[
                "E2_to_E3_relative_matrix_change_max"
            ]

            for name, value in (
                E2E3.items()
            ):
                if value > limit:
                    failures.append(
                        f"z={z}: "
                        f"{name} "
                        f"E2->E3="
                        f"{value:.9e}"
                    )

            if (
                E3["summary"][
                    "metric_ratio"
                ]
                < screens[
                    "metric_eigenvalue_ratio_min"
                ]
            ):
                failures.append(
                    f"z={z}: metric "
                    "ratio screen"
                )

            if (
                E3["summary"][
                    "S_hermiticity"
                ]
                > screens[
                    "S_hermiticity_relative_max"
                ]
            ):
                failures.append(
                    f"z={z}: S "
                    "hermiticity screen"
                )

            if (
                E3["summary"][
                    "H_hermiticity"
                ]
                > screens[
                    "H_hermiticity_relative_max"
                ]
            ):
                failures.append(
                    f"z={z}: H "
                    "hermiticity screen"
                )

            write_new(
                out
                / "partials"
                / (
                    f"{basis_id}_"
                    f"z{z:+05.1f}.json"
                ),
                row,
            )

        converged = (
            len(failures) == 0
        )

        # Only B is allowed to use the
        # standard L6 agreement as an
        # oracle-validation screen,
        # because D2 established that
        # L6 is not converged for C.
        if (
            basis_id
            == "B_FEM_BOUND_ONLY"
        ):
            ctrl_lim = screens[
                "B_control_E3_vs_standard_relative_max"
            ]

            for row in geometry:
                for name, value in (
                    row[
                        "E3_vs_standard_L6"
                    ].items()
                ):
                    if value > ctrl_lim:
                        failures.append(
                            "B control "
                            f"z={row['z_a0']}: "
                            f"{name} "
                            "E3-vs-L6="
                            f"{value:.9e}"
                        )

            converged = (
                len(failures) == 0
            )

        results[basis_id] = {
            "channel_count":
                len(channels),
            "radial_modes": [
                {
                    "l":
                        int(m.l),
                    "principal_n":
                        (
                            None
                            if m.principal_n
                            is None
                            else int(
                                m.principal_n
                            )
                        ),
                    "energy_Eh":
                        float(
                            m.energy
                        ),
                    "residual":
                        float(
                            m.residual
                        ),
                    "kind":
                        (
                            "POSITIVE_"
                            "PSEUDOSTATE"
                            if m.principal_n
                            is None
                            else "BOUND"
                        ),
                }
                for m in bank
            ],
            "screen_pass":
                converged,
            "failures":
                failures,
            "geometry":
                geometry,
        }

    Bpass = results[
        "B_FEM_BOUND_ONLY"
    ]["screen_pass"]

    Cpass = results[
        "C_FEM_BOUND_PLUS_PSEUDOSTATE"
    ]["screen_pass"]

    if not Bpass:
        classification = (
            "ELEMENT_PAIR_ORACLE_"
            "NOT_VALIDATED"
        )
    elif Cpass:
        classification = (
            "ELEMENT_ALIGNED_"
            "QUADRATURE_RESOLVES_"
            "PSEUDOSTATE_BLOCKER"
        )
    else:
        classification = (
            "PSEUDOSTATE_REMAINS_"
            "UNRESOLVED_AFTER_"
            "ELEMENT_ALIGNMENT"
        )

    result = {
        "schema":
            "BASS_FND_R3A_D3_"
            "ELEMENT_PAIR_RESULT_V1",
        "status":
            "DISCRIMINATOR_COMPLETE",
        "classification":
            classification,
        "execution_head":
            execution_head,
        "execution_tree":
            execution_tree,
        "contract_sha256":
            sha256_file(
                contract_path
            ),
        "projectile_speed_au":
            speed,
        "results":
            results,
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
                "B_control_pass":
                    Bpass,
                "C_pseudostate_pass":
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
