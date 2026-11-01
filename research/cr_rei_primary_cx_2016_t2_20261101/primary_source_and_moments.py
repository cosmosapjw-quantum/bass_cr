#!/usr/bin/env python3
"""Source-anchored proton + neutral H transport validation.

This module DOES NOT supply missing original quantum DCS; the primary table
is Schultz et al. (2016), J Phys B 49 084004, Table 2.
Angular integration consumes PREWEIGHTED 2*pi*sin(theta)*d_sigma/dOmega.
The Maxwellian two-fluid closure is conditional on a valid charge-labelled
sigma_mt and small relative drift and temperature separation.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "cr_rei_bass193_low_energy_cx_20261101"
sys.path.insert(0, str(BASE))
import source_cx_screen as original  # source-matched parent; DO NOT edit

A0SQ_CM2_PUBLISHED_ROUNDED = 2.8003e-17  # Schultz et al. 2016 appendix
TABLE2 = HERE / "PRIMARY_CX_SCHULTZ2016_TABLE2.csv"
SOURCE_DOI = "10.1088/0953-4075/49/8/084004"


def table2():
    with TABLE2.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    expected = (1e-4, 1e-3, 1e-2, 1e-1, 1., 10., 100.)
    if len(rows) != len(expected):
        raise ValueError("original Table 2 benchmark rows missing")
    parsed = []
    for row, e in zip(rows, expected):
        data = {k: float(v) for k, v in row.items()}
        if data["E_cm_eV"] != e or min(data.values()) <= 0:
            raise ValueError("unexpected original benchmark value or order")
        parsed.append(data)
    return parsed


def cm_speed_from_energy_cm_s(E_cm_eV, mu_g=original.MU_G):
    if not math.isfinite(E_cm_eV) or E_cm_eV <= 0 or mu_g <= 0:
        raise ValueError("positive CM energy and reduced mass required")
    return math.sqrt(2. * E_cm_eV * original.EV_ERG / mu_g)


def energy_cm_eV_from_speed(v_cm_s, mu_g=original.MU_G):
    if not math.isfinite(v_cm_s) or v_cm_s <= 0 or mu_g <= 0:
        raise ValueError("positive CM relative speed and mass required")
    return 0.5 * mu_g * v_cm_s * v_cm_s / original.EV_ERG


def crosswalk():
    """Published seven original CX total cross sections, never inferred DCS."""
    out = []
    for row in table2():
        e = row["E_cm_eV"]
        g = cm_speed_from_energy_cm_s(e)
        original_sigma = row["cx_2016_a0_sq"] * A0SQ_CM2_PUBLISHED_ROUNDED
        fitted_sigma = original.sigma_cx_cm2(g)
        out.append({
            "E_cm_eV": e,
            "relative_speed_km_s": g * 1.e-5,
            "primary_cx_total_a0_sq": row["cx_2016_a0_sq"],
            "primary_cx_total_cm2": original_sigma,
            "previous_l0_omitted_cx_a0_sq": row["cx_no_l0_a0_sq"],
            "relative_missing_l0_correction": (
                row["cx_2016_a0_sq"] / row["cx_no_l0_a0_sq"] - 1.
            ),
            "published_A4_cx_total_cm2": fitted_sigma,
            "A4_vs_primary_fraction": fitted_sigma / original_sigma - 1.,
            "within_existing_3_to_200_km_s_fit_window": (
                original.V_MIN_CM_S <= g <= original.V_MAX_CM_S
            ),
            "source": "Schultz et al (2016), Table 2, distinguishable CX",
            "published_number_not_raw_DCS": True
        })
    return out


def angular_moments_preweighted(theta_rad, angular_dSigma_dTheta_a0sq,
                                angle_frame):
    """Trapezoidal moments of angular DCS preweighted by 2*pi*sin(theta).

    theta in [0,pi] measured from outgoing charged ion for 'charged_cm';
    for a CX differential table with nuclear-labelled angle use
    'nuclear_cx_cm', converting cos(theta_charge)=-cos(theta_nuclear).
    Never multiply by 2*pi*sin(theta) again.
    Returns total, charge-labelled momentum-transfer and viscosity (a0^2).
    Not an identical-proton spin-average or a joint channel operator.
    """
    if angle_frame not in ("charged_cm", "nuclear_cx_cm"):
        raise ValueError("explicit documented angular convention required")
    if len(theta_rad) != len(angular_dSigma_dTheta_a0sq) or len(theta_rad) < 3:
        raise ValueError("incomplete angle grid")
    old_theta = -1.
    for th, ds in zip(theta_rad, angular_dSigma_dTheta_a0sq):
        if not math.isfinite(th) or not math.isfinite(ds) or ds < 0:
            raise ValueError("nonfinite or negative preweighted DCS")
        if not 0 <= th <= math.pi or th <= old_theta:
            raise ValueError("grid must be strictly increasing in [0,pi]")
        old_theta = th
    sign = 1. if angle_frame == "charged_cm" else -1.
    weight = []
    for th, ds in zip(theta_rad, angular_dSigma_dTheta_a0sq):
        c = sign * math.cos(th)
        weight.append((ds, ds * (1. - c), ds * (1. - c*c)))
    ans = [0., 0., 0.]
    for j in range(len(theta_rad)-1):
        h = theta_rad[j+1] - theta_rad[j]
        for k in range(3):
            ans[k] += 0.5*h*(weight[j][k]+weight[j+1][k])
    return {"sigma_total_a0_sq": ans[0],
            "sigma_mt_charge_a0_sq": ans[1],
            "sigma_viscosity_a0_sq": ans[2]}


def linear_momentum_energy_exchange(k_mt_cm3_s, n_ion_cm3, n_H_cm3,
                                    u_ion_cm_s, u_H_cm_s, T_ion_K, T_H_K,
                                    m_ion_g=original.MP_G, m_H_g=original.MH_G):
    """Leading two-Maxwellian moment closure, not a native Bianchi IVP.

    K_mt=<2/(3a^2) sigma_mt(g)g^3> at a reference common temperature.
    Accuracy requires |U|/a << 1 and |Ti-Tn|/Tref << 1, both reported
    and NOT assumed true from a REI source. For unequal temperatures
    K_mt at Tref contributes only higher-order mixed corrections.
    """
    vals = (k_mt_cm3_s, n_ion_cm3, n_H_cm3, T_ion_K, T_H_K,
            m_ion_g, m_H_g, *u_ion_cm_s, *u_H_cm_s)
    if len(u_ion_cm_s) != 3 or len(u_H_cm_s) != 3:
        raise ValueError("local 3-vectors required")
    if any(not math.isfinite(v) for v in vals):
        raise ValueError("nonfinite moment input")
    if min(k_mt_cm3_s, n_ion_cm3, n_H_cm3) < 0 or min(
            T_ion_K, T_H_K, m_ion_g, m_H_g) <= 0:
        raise ValueError("positive temperature/masses and nonnegative density/K")
    M = m_ion_g + m_H_g
    mu = m_ion_g * m_H_g / M
    U = tuple(x-y for x,y in zip(u_ion_cm_s,u_H_cm_s))
    V = tuple((m_ion_g*x+m_H_g*y)/M for x,y in zip(u_ion_cm_s,u_H_cm_s))
    gam = mu * n_ion_cm3 * n_H_cm3 * k_mt_cm3_s
    Ri = tuple(-gam*x for x in U)
    Rn = tuple(-x for x in Ri)
    dT = T_ion_K - T_H_K
    Qi = sum(x*y for x,y in zip(V,Ri)) - (
        3.*mu/M * original.KB_ERG_K *
        n_ion_cm3 * n_H_cm3 * k_mt_cm3_s * dT
    )
    Qn = -Qi
    Si = Qi - sum(x*y for x,y in zip(u_ion_cm_s,Ri))
    Sn = Qn - sum(x*y for x,y in zip(u_H_cm_s,Rn))
    Tbar = 0.5*(T_ion_K+T_H_K)
    a = math.sqrt(2.*original.KB_ERG_K*Tbar*(1./m_ion_g+1./m_H_g))
    return {
        "R_ion_g_cm_minus2_s_minus2": Ri,
        "R_H_g_cm_minus2_s_minus2": Rn,
        "Q_ion_erg_cm_minus3_s_minus1": Qi,
        "Q_H_erg_cm_minus3_s_minus1": Qn,
        "S_ion_erg_cm_minus3_s_minus1": Si,
        "S_H_erg_cm_minus3_s_minus1": Sn,
        "total_frictional_internal_heating_erg_cm_minus3_s_minus1": Si+Sn,
        "drift_speed_over_thermal_width": math.sqrt(sum(v*v for v in U))/a,
        "relative_temperature_difference": abs(dT)/Tbar,
        "linear_drift_relaxation_s_minus1": mu*k_mt_cm3_s*(
            n_H_cm3/m_ion_g+n_ion_cm3/m_H_g),
        "linear_temperature_relaxation_s_minus1": (
            2.*mu/M*k_mt_cm3_s*(n_ion_cm3+n_H_cm3)),
        "closure": "leading small U and delta T; optional input K; no original DCS"
    }


def write_crosswalk(outfile):
    rows = crosswalk()
    keys = list(rows[0])
    with Path(outfile).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    out = HERE / "PRIMARY_CX_2016_TABLE2_VS_A4_CROSSWALK.csv"
    rows = write_crosswalk(out)
    print(json.dumps({
        "source_DOI": SOURCE_DOI,
        "source": "Schultz et al 2016 Table 2, seven published total-CX points",
        "original_DCS_bytes": "NOT_RETRIEVED",
        "within_stated_speed_window": sum(
            r["within_existing_3_to_200_km_s_fit_window"] for r in rows),
        "CM_energy_window_eV": [
            energy_cm_eV_from_speed(original.V_MIN_CM_S),
            energy_cm_eV_from_speed(original.V_MAX_CM_S)],
        "output": str(out),
        "DAG": {"REI_central": "28/88_REPORTED",
                "REI_working": "33/88_REPORTED", "CR_extension": "0/3"}
    }, sort_keys=True))
