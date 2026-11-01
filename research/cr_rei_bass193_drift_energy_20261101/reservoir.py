#!/usr/bin/env python3
"""REI BASS193 snapshot H+/H relative-drift energy reservoir and conditional relaxation.

Original upstream ZIP stays private. Only consumes immutable PUBLIC PR155
source-conditioned 192-row CSV. Energy capacity is cross-section independent.
Any linear-CX relaxation output uses the MODEL-CONDITIONAL A7 coefficient and
is NOT a Bianchi/REI ion-neutral evolution or exact elastic+CX joint kernel.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_CSV = (HERE.parent / "cr_rei_bass193_angular_mt_20261101" /
              "results" / "BASS193_CX_A7_LINEAR_DRAG_192.csv")
SOURCE_SHA256 = "f47f1379503dba93f1583a8cb2b2cdb61fa856f9e0e485140d62fce329600f03"
SOURCE_GIT_BLOB_SHA1 = "62290340fd338e1105e44739823d2ff267377f52"
SOURCE_REI_PR = 311
SOURCE_BASS_PR = 155
SOURCE_REI_ZIP_REPORTED_SHA256 = (
    "4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52"
)
MP_G = 1.67262192595e-24
MH_G = 1.6735575e-24
KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
EXPECTED_INTERVALS = 192


def hash256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mass_general_max_ratio(epsilon: float, mi=MP_G, mn=MH_G) -> float:
    """Maximum reservoir / H-only heat, optimized over x in [0,1]."""
    return (2. / 3.) * (mi + mn) / (math.sqrt(mi) + math.sqrt(mn))**2 * epsilon**2


def snapshot_budget(ni: float, nn: float, T: float, epsilon: float = 0.1,
                    mi: float = MP_G, mn: float = MH_G,
                    nu: float | None = None, dt: float | None = None) -> dict:
    """Exact kinematic ceiling, optional FROZEN linear A7 collision-only substep.

    No impulse from ionization, pressure, external acceleration or Bianchi shear.
    epsilon is prescribed |U|/a (NOT a measured REI tilt).
    """
    vals = (ni, nn, T, epsilon, mi, mn)
    if any(not math.isfinite(x) for x in vals):
        raise ValueError("finite input required")
    if ni < 0 or nn < 0 or ni + nn <= 0 or T <= 0 or epsilon < 0:
        raise ValueError("physical densities, temperature and epsilon required")
    if mi <= 0 or mn <= 0:
        raise ValueError("positive ion and neutral masses required")
    if (nu is None) != (dt is None):
        raise ValueError("nu and proper dt must be supplied together")
    if nu is not None and (
        not math.isfinite(nu) or not math.isfinite(dt) or nu < 0 or dt < 0
    ):
        raise ValueError("nonnegative finite rate and proper interval required")
    rhoi, rhon = mi * ni, mn * nn
    rho_red = rhoi * rhon / (rhoi + rhon) if rhoi > 0 and rhon > 0 else 0.
    mu = mi * mn / (mi + mn)
    a2 = 2 * KB_ERG_K * T / mu
    U2 = epsilon**2 * a2
    ed = 0.5 * rho_red * U2
    eth = 1.5 * (ni + nn) * KB_ERG_K * T
    exact_ratio = ed / eth
    independent_ratio = (2./3.) * (mi+mn)*ni*nn / (
        (mi*ni+mn*nn)*(ni+nn)) * epsilon**2
    if not math.isclose(exact_ratio, independent_ratio, rel_tol=3e-14, abs_tol=0):
        raise AssertionError("mass-resolved reservoir identity violated")
    if nu is None:
        attenuation_exponent = None
        remaining_u = None
        conversion = None
        edep = None
    else:
        attenuation_exponent = nu * dt
        remaining_u = math.exp(-attenuation_exponent)
        conversion = -math.expm1(-2. * attenuation_exponent)
        edep = ed * conversion
    return {
        "H_ion_fraction": ni / (ni+nn),
        "rho_reduced_g_cm3": rho_red,
        "a_relative_cm_s": math.sqrt(a2),
        "initial_drift_cm_s": math.sqrt(U2),
        "relative_energy_erg_cm3": ed,
        "H_thermal_energy_erg_cm3": eth,
        "capacity_ratio_DeltaT_over_T": exact_ratio,
        "capacity_DeltaT_K": ed * (2./(3.*(ni+nn)*KB_ERG_K)),
        "capacity_eV_per_H": ed / ((ni+nn)*EV_ERG),
        "nu_dt_A7_conditional": attenuation_exponent,
        "U_survival_A7_conditional": remaining_u,
        "drift_energy_conversion_fraction_A7_conditional": conversion,
        "deposited_eV_per_H_A7_conditional": (
            edep / ((ni+nn)*EV_ERG) if edep is not None else None),
        "DeltaT_K_A7_conditional": (
            edep*(2./(3.*(ni+nn)*KB_ERG_K)) if edep is not None else None),
    }


def load_source(path: Path = SOURCE_CSV):
    if hash256(path) != SOURCE_SHA256:
        raise ValueError("source-conditioned parent CSV byte-lock failed")
    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != EXPECTED_INTERVALS:
        raise ValueError("expected exactly 192 source-clock intervals")
    last_z = math.inf
    for k, row in enumerate(rows):
        if int(row["interval"]) != k:
            raise ValueError("nonsequential original proper clock")
        z = float(row["z_low"])
        T = float(row["T_saved_K"])
        ni, nn = float(row["nHII_cm3"]), float(row["nHI_cm3"])
        dt = float(row["proper_interval_s"])
        rate = float(row["nu_rel_linear_drag_s_minus1"])
        x = float(row["x_HII_end"])
        if not all(math.isfinite(q) for q in (z, T, ni, nn, dt, rate, x)):
            raise ValueError("nonfinite source field")
        if z >= last_z or z < 0 or dt <= 0 or T <= 0 or rate < 0:
            raise ValueError("malformed chronological source")
        if ni < 0 or nn < 0 or ni+nn <= 0 or not (0 <= x <= 1):
            raise ValueError("invalid source H populations")
        if not math.isclose(ni/(ni+nn), x, rel_tol=3e-12, abs_tol=1e-14):
            raise ValueError("REI source ion fraction mismatch")
        last_z = z
    return rows


def generate(source=SOURCE_CSV, epsilon=0.1):
    rows = load_source(source)
    if epsilon > 0.2:
        raise ValueError("this diagnostic is explicitly restricted to small drift epsilon<=0.2")
    out = []
    for r in rows:
        b = snapshot_budget(
            ni=float(r["nHII_cm3"]), nn=float(r["nHI_cm3"]),
            T=float(r["T_saved_K"]), epsilon=epsilon,
            nu=float(r["nu_rel_linear_drag_s_minus1"]),
            dt=float(r["proper_interval_s"]))
        out.append({
            "interval": int(r["interval"]),
            "z_low": float(r["z_low"]),
            "proper_interval_s": float(r["proper_interval_s"]),
            "T_saved_K": float(r["T_saved_K"]),
            "nHII_cm3": float(r["nHII_cm3"]),
            "nHI_cm3": float(r["nHI_cm3"]),
            "epsilon_prescribed": epsilon,
            **b
        })
    ratios = [r["capacity_ratio_DeltaT_over_T"] for r in out]
    maxima = mass_general_max_ratio(epsilon)
    if any(x > maxima*(1+1e-12) for x in ratios):
        raise AssertionError("derived global snapshot maximum violated")
    imax = max(range(len(out)), key=lambda i: ratios[i])
    return out, {
        "unit": "BASS193_H_PLUS_H_FIXED_SNAPSHOT_DRIFT_ENERGY_CEILING",
        "input_sha256": SOURCE_SHA256,
        "parent_git_blob_sha1": SOURCE_GIT_BLOB_SHA1,
        "source_rei_pr": SOURCE_REI_PR,
        "source_bass_cr_pr": SOURCE_BASS_PR,
        "upstream_original_rei_zip_sha256_reported_not_independently_read":
            SOURCE_REI_ZIP_REPORTED_SHA256,
        "interval_count": len(out),
        "epsilon_prescribed_small_drift": epsilon,
        "max_source_capacity_ratio": max(ratios),
        "max_capacity_interval": out[imax]["interval"],
        "max_capacity_z_low": out[imax]["z_low"],
        "max_capacity_DeltaT_K": out[imax]["capacity_DeltaT_K"],
        "median_source_capacity_ratio": statistics.median(ratios),
        "min_source_capacity_ratio": min(ratios),
        "general_mass_theory_max_ratio": maxima,
        "count_capacity_ratio_below_1e_minus_4": sum(x < 1e-4 for x in ratios),
        "min_A7_conditional_nu_dt": min(r["nu_dt_A7_conditional"] for r in out),
        "max_A7_conditional_nu_dt": max(r["nu_dt_A7_conditional"] for r in out),
        "n_complete_thermalization_A7_conditional_ge_0p99": sum(
            r["drift_energy_conversion_fraction_A7_conditional"] >= .99 for r in out),
        "scientific_admission": "SCOPED_SOURCE_SNAPSHOT_DIAGNOSTIC_ONLY",
        "canonical_rei_DAG": "28/88_REPORTED_DELTA0",
        "rei_working_DAG": "33/88_REPORTED_DELTA0",
        "bass_cr_extension_DAG": "0/3_DELTA0",
        "original_full_DCS": "NOT_RETRIEVED",
        "NO_REI_MUTATION": True,
        "PRODUCTION": "HOLD",
    }


def write_results(out_dir: Path, rows: list, summary: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "BASS193_H_HPLUS_DRIFT_ENERGY_192.csv"
    json_path = out_dir / "SUMMARY.json"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n",
                         encoding="utf-8")
    return csv_path, json_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=SOURCE_CSV)
    ap.add_argument("--out", type=Path, default=HERE / "results")
    ap.add_argument("--epsilon", type=float, default=0.1)
    args = ap.parse_args()
    dat, meta = generate(args.input, args.epsilon)
    paths = write_results(args.out, dat, meta)
    print(json.dumps({**meta, "output_sha256": {p.name: hash256(p) for p in paths}},
                     sort_keys=True, indent=2))
