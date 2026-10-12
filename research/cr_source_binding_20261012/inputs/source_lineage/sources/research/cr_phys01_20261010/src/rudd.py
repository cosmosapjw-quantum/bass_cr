# SPDX-License-Identifier: GPL-3.0-only
"""Bounded CR proton impact-ionization kernel for neutral atomic H and He.

Formula/parameter port from CRIPTIC, Mark R. Krumholz and contributors,
commit e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92,
Src/Losses/Ionization.H; upstream GNU GPL v3.  The accompanying
GPL-3.0.txt applies to this module.  Modifications: Python/SI-eV interface,
an explicit selected 1--10 MeV proton window, ejected-electron SDCS and
conservative analytic moments.  Total ionization is integrated from
the SDCS, correcting the missing square in upstream's F2*wmax term.

This is a published-model ionization-channel adapter, NOT a complete
proton stopping/transport model or a measured-accuracy certification.
The atomic-H parameters are the upstream Williams-limit choice, not
the molecular-H2 Rudd fit.  No He+ or nuclear/isotope reaction is supplied.
Energies are kinetic eV, cross sections m^2, and first energy moments
m^2 eV.  Convert to SI energy exactly once using EV_J.
"""

from __future__ import annotations

import math
import numpy as np

SOURCE_COMMIT = "e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92"
SOURCE_URL = "https://bitbucket.org/krumholz/criptic/src/" + SOURCE_COMMIT + "/Src/Losses/Ionization.H"
MODEL_ID = "CRIPTIC_RUDD_H_HE_IONIZATION_1_10MEV_v1"
PROTON_MIN_EV = 1.0e6
PROTON_MAX_EV = 1.0e7
EV_J = 1.602176634e-19
A0_M = 5.29177210903e-11  # CODATA 2018, units explicitly pinned here
RYDBERG_EV = 13.605693122994
ME_OVER_MP = 5.44617021487e-4
PROTON_REST_EV = 938272088.16
C_M_S = 299792458.0

TARGETS = {
    "H": {"I_eV": RYDBERG_EV, "N": 1, "model": "upstream_Williams_limit"},
    "He": {"I_eV": 24.59, "N": 2, "model": "Rudd_1992_empirical",
           "A1": 1.02, "B1": 2.4, "C1": 0.70, "D1": 1.15, "E1": 0.70,
           "A2": 0.84, "B2": 6.0, "C2": 0.70, "D2": 0.50},
}


def _target(target: str) -> dict:
    if target not in TARGETS:
        raise ValueError("Only neutral atomic targets 'H' and 'He' are supported")
    return TARGETS[target]


def active_proton_mask(proton_eV):
    """Selected support only; caller MUST retain all inactive CRs in transport."""
    t = np.asarray(proton_eV, dtype=float)
    return np.isfinite(t) & (t >= PROTON_MIN_EV) & (t <= PROTON_MAX_EV)


def _checked_proton(proton_eV):
    t = np.asarray(proton_eV, dtype=float)
    if not np.all(active_proton_mask(t)):
        raise ValueError("Proton kinetic energy outside selected [1e6, 1e7] eV window; retain as unresolved CR energy, do not extrapolate or heat")
    return t


def proton_speed_m_s(proton_eV):
    """Exact massive-particle speed; positive kinetic energies required."""
    t = np.asarray(proton_eV, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t < 0):
        raise ValueError("Finite nonnegative kinetic energy required")
    return C_M_S * np.sqrt(t * (t + 2 * PROTON_REST_EV)) / (t + PROTON_REST_EV)


def rudd_factors(proton_eV, target: str):
    t = _checked_proton(proton_eV)
    d = _target(target)
    v2 = ME_OVER_MP * t / d["I_eV"]
    if target == "H":
        return 7.0 / (3.0 * v2), 1.0 / v2
    h1 = d["A1"] * np.log1p(v2) / (v2 + d["B1"] / v2)
    l1 = d["C1"] * v2 ** (d["D1"] / 2) / (1 + d["E1"] * v2 ** (d["D1"] / 2 + 2))
    h2 = d["A2"] / v2 + d["B2"] / v2**2
    l2 = d["C2"] * v2 ** (d["D2"] / 2)
    return h1 + l1, h2 * l2 / (h2 + l2)


def secondary_max_eV(proton_eV, target: str):
    """Upstream NONRELATIVISTIC ejection endpoint, not an exact relativistic one."""
    t = _checked_proton(proton_eV)
    return 4.0 * ME_OVER_MP * t - _target(target)["I_eV"]


def dsigma_dW_m2_per_eV(proton_eV, electron_eV, target: str):
    """Singly differential ionization cross section, integrated over angles.

    A scalar or NumPy-broadcastable T,W pair is accepted. Negative/nonfinite W
    is an error; W above the model endpoint has zero differential support.
    The provider contains no ejected-electron angular distribution.
    """
    t = _checked_proton(proton_eV)
    w_ev = np.asarray(electron_eV, dtype=float)
    if np.any(~np.isfinite(w_ev)) or np.any(w_ev < 0):
        raise ValueError("Electron kinetic energies must be finite and nonnegative")
    d = _target(target)
    f1, f2 = rudd_factors(t, target)
    w = w_ev / d["I_eV"]
    scale = 4 * math.pi * A0_M**2 * d["N"] * (RYDBERG_EV / d["I_eV"])**2
    val = scale / d["I_eV"] * (f1 + f2 * w) / (1 + w)**3
    return np.where(w_ev <= secondary_max_eV(t, target), val, 0.0)


def cross_section_moments(proton_eV, target: str, lower_eV=0.0, upper_eV=None):
    """Exact SDCS integrals over a secondary-energy interval.

    Returns number cross section, primary binding cost, secondary kinetic
    energy and their sum.  Intervals are intersected with [0,Wmax], with
    empty intersections returning zero.  This clipping is an integration
    support operation, never an extrapolation or reassignment to heat.
    The complete partition must sum intervals covering [0,Wmax].
    """
    t = _checked_proton(proton_eV)
    d = _target(target)
    lo = np.asarray(lower_eV, dtype=float)
    hi = secondary_max_eV(t, target) if upper_eV is None else np.asarray(upper_eV, dtype=float)
    if np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo < 0) or np.any(hi < lo):
        raise ValueError("Finite interval 0 <= lower <= upper required")
    maximum = secondary_max_eV(t, target)
    a = np.minimum(lo, maximum) / d["I_eV"]
    b = np.minimum(hi, maximum) / d["I_eV"]
    f1, f2 = rudd_factors(t, target)
    scale = 4 * math.pi * A0_M**2 * d["N"] * (RYDBERG_EV / d["I_eV"])**2
    def prim(w):
        r = w / (1.0 + w)
        number = f1 * (r - 0.5 * r*r) + 0.5 * f2 * r*r
        loss = f2 * np.log1p(w) + (f1 - f2) * r
        return number, loss
    na, la = prim(a)
    nb, lb = prim(b)
    sigma = scale * (nb - na)
    loss = scale * d["I_eV"] * (lb - la)
    binding = d["I_eV"] * sigma
    secondary = loss - binding
    return {"sigma_m2": sigma, "binding_eV_m2": binding,
            "secondary_eV_m2": secondary, "loss_eV_m2": loss}


def upstream_reported_total_cross_section_m2(proton_eV, target: str):
    """Evidence-only reproduction of upstream Eq26 missing-square discrepancy.

    Do not use this for transport or rate normalization.  At wmax>0 the
    F2 term is wmax in upstream; the SDCS antiderivative requires wmax^2.
    """
    t = _checked_proton(proton_eV)
    d = _target(target)
    w = secondary_max_eV(t, target) / d["I_eV"]
    f1, f2 = rudd_factors(t, target)
    scale = 4 * math.pi * A0_M**2 * d["N"] * (RYDBERG_EV / d["I_eV"])**2
    return scale * (f2*w + f1*w*(2+w)) / (2*(1+w)**2)
