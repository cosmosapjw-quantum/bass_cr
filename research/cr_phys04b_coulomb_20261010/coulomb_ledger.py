# SPDX-License-Identifier: GPL-3.0-only
"""CR-PHYS04b: instantaneous free-electron Coulomb energy-transfer diagnostic.

Formula port from CRIPTIC Coulomb.H (Mark Krumholz and contributors), commit
e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92, GPL v3. See NOTICE.md.
The CGS expression is retained. Its SI conversion divides by 4*pi*eps0;
the upstream MKS multiply survives solely as a negative regression control.

The positive loss is energy transferred out of the projectile, not an adopted
thermal heat, secondary spectrum, or ionization/deposition provider. Fixed
100 K PHYS01 gas and collisionless transport are sampled without feedback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "cr_phys01_20261010" / "src"
sys.path.insert(0, str(SOURCE))
from injection import EV_J, PROTON_REST_EV, InjectionModel, transport_population  # noqa: E402

COMMIT = "e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92"
UPSTREAM_HASHES = {
    "Src/Losses/Coulomb.H": "76d7cba91376d11a57bf721833cd05eb575ff5bd454a22273f958e00fa2614e0",
    "Src/Utils/Constants.H": "fbc502bb70ca5ad3ebc8505f47cc63d121e45201a6b5a7ca0192a219eb3ed2d4",
    "Src/Gas/GasData.H": "1ca5f69a6fb51d479b950c986ffce1e5db79a1d7f0af61d8ae846a0feb6550b0",
}
# Explicit CODATA 2018 values; no claim to reproduce an unspecified GSL build.
C_M_S = 299792458.0
ME_KG = 9.1093837015e-31
EPS0 = 8.8541878128e-12
HBAR_J_S = 6.62607015e-34 / (2 * math.pi)
E_C = 1.602176634e-19
ALPHA = 7.2973525693e-3
KB_J_K = 1.380649e-23
# Gaussian charge: sqrt(e_SI^2 / (4*pi*eps0) * 1e9), units sqrt(erg cm).
# Pinned independently here so the CGS route does not call the SI expression.
E_STATC = 4.8032047138777412e-10
GAMMA_C = 0.5615
REFINEMENT_BOUND = 2e-6


def electron_density(n_h_m3=140.0, y_he=.248, x_hii=.01,
                     x_heii=.01, x_heiii=0.0):
    """Charge-neutral proper density; helium fractions are per He nucleus."""
    values = (n_h_m3, y_he, x_hii, x_heii, x_heiii)
    if any(isinstance(v, (bool, np.bool_)) or not np.isscalar(v) or
           not math.isfinite(float(v)) for v in values):
        raise ValueError("FINITE_SCALAR_GAS_REQUIRED")
    if not (n_h_m3 >= 0 and 0 <= y_he < 1 and 0 <= x_hii <= 1
            and x_heii >= 0 and x_heiii >= 0 and x_heii+x_heiii <= 1):
        raise ValueError("GAS_OUTSIDE_DOMAIN")
    return n_h_m3*x_hii + n_h_m3*y_he/(4*(1-y_he))*(x_heii+2*x_heiii)


def _kinematics(kinetic_eV, ne_m3):
    kinetic = np.asarray(kinetic_eV, dtype=float)
    if np.any(~np.isfinite(kinetic)) or np.any(kinetic < 1e6) or np.any(kinetic > 1e7):
        raise ValueError("COULOMB_DIAGNOSTIC_PROTON_DOMAIN_1_TO_10_MEV")
    if isinstance(ne_m3, (bool, np.bool_)) or not np.isscalar(ne_m3):
        raise ValueError("FINITE_NONNEGATIVE_NE_REQUIRED")
    ne = float(ne_m3)
    if not math.isfinite(ne) or ne < 0:
        raise ValueError("FINITE_NONNEGATIVE_NE_REQUIRED")
    gamma = 1.0 + kinetic / PROTON_REST_EV
    beta = np.sqrt(kinetic * (kinetic + 2*PROTON_REST_EV)) / (kinetic + PROTON_REST_EV)
    return gamma, beta, ne


def _positive(rate):
    if np.any(~np.isfinite(rate)) or np.any(rate <= 0):
        raise ValueError("NONFINITE_OR_NONPOSITIVE_COULOMB_LOSS")
    return rate


def proton_loss_si_J_s(kinetic_eV, ne_m3):
    """Positive projectile energy loss, corrected SI port of the CGS formula."""
    gamma, beta, ne = _kinematics(kinetic_eV, ne_m3)
    if ne == 0:
        return np.zeros_like(beta)
    omega = E_C * math.sqrt(ne/(ME_KG*EPS0))
    bfac = .5*np.log1p((GAMMA_C*beta/ALPHA)**2)
    bstop = np.log(2*gamma*ME_KG*C_M_S**2*beta**2/(HBAR_J_S*omega)) - beta**2/2 + bfac
    return _positive(E_C**2 * omega**2 / (4*math.pi*EPS0*beta*C_M_S) * bstop)


def proton_loss_cgs_J_s(kinetic_eV, ne_m3):
    """Independent Gaussian-CGS arithmetic, converted from erg/s to J/s."""
    gamma, beta, ne = _kinematics(kinetic_eV, ne_m3)
    if ne == 0:
        return np.zeros_like(beta)
    ne_cm3 = ne * 1e-6
    me_g, c_cm_s, hbar_erg_s = ME_KG*1e3, C_M_S*1e2, HBAR_J_S*1e7
    omega = E_STATC * math.sqrt(4*math.pi*ne_cm3/me_g)
    stopping = (np.log(2*gamma*me_g*c_cm_s**2*beta**2/(hbar_erg_s*omega))
                - beta**2/2 + .5*np.log1p((GAMMA_C*beta/ALPHA)**2))
    loss_erg_s = E_STATC**2 * omega**2/(beta*c_cm_s) * stopping
    return _positive(loss_erg_s*1e-7)


def upstream_mks_loss_negative_control_J_s(kinetic_eV, ne_m3):
    """Evidence only: literal upstream MKS multiply instead of SI division."""
    gamma, beta, ne = _kinematics(kinetic_eV, ne_m3)
    if ne == 0:
        return np.zeros_like(beta)
    omega = E_C*math.sqrt(ne/(ME_KG*EPS0))
    stopping = (np.log(2*gamma*ME_KG*C_M_S**2*beta**2/(HBAR_J_S*omega))
                - beta**2/2 + .5*np.log1p((GAMMA_C*beta/ALPHA)**2))
    return (4*math.pi*EPS0)*E_C**2*omega**2/(beta*C_M_S)*stopping


def build_ledger(energy_order=48, age_order=8, mu_order=8, *,
                 dt_s=1e10, enabled=True, window_eV=(1e6, 1e7)):
    """Sample the declared fixed gas; rate at final proper time, not dt*rate."""
    low, high = window_eV
    if not 1e6 <= low < high <= 1e7:
        raise ValueError("COULOMB_DIAGNOSTIC_PROTON_DOMAIN_1_TO_10_MEV")
    model = InjectionModel(enabled=enabled)
    population = transport_population(model, dt_s, 3.3e-17, 3.3e-18,
        collision_window_eV=window_eV, energy_order=energy_order,
        age_order=age_order, mu_order=mu_order)
    kinetic = population["nodes"]["kinetic_eV"]
    numbers = population["nodes"]["number_density_m3"]
    ne = electron_density()
    transferred, sampled_fraction = 0.0, 0.0
    if len(kinetic):
        loss = proton_loss_si_J_s(kinetic, ne)
        transferred = float(np.dot(numbers, loss))
        sampled_fraction = float(np.max(loss/(kinetic*EV_J)))*float(dt_s)
    if not math.isfinite(transferred) or transferred < 0:
        raise ValueError("INVALID_TRANSFER_MOMENT")
    return {
        "schema": "cr-phys04b-coulomb-ledger.v1",
        "scope": "INSTANTANEOUS_FREE_ELECTRON_PLASMA_TRANSFER_DIAGNOSTIC",
        "solver_intervals": 0, "orders": [energy_order, age_order, mu_order],
        "source": model.metadata(), "background": population["background"],
        "gas": {"n_h_m3": 140.0, "n_he_m3": 140*.248/(4*(1-.248)),
                "x_hii": .01, "x_heii": .01, "x_heiii": 0.0,
                "ne_m3": ne, "temperature_k": 100.0, "y_he_mass_fraction": .248},
        "proton_window_eV": list(window_eV), "population_node_count": len(kinetic),
        "plasma_transferred_energy_j_m3_s": transferred,
        "active_cr_energy_j_m3": population["budgets"]["active_CR_energy_J_m3"],
        "sampled_fractional_coulomb_loss_age_estimate": sampled_fraction,
        "loss_estimate_semantics": "maximum over final quadrature nodes times source age; not a trajectory supremum or certified bound",
        "ledger_semantics": "positive projectile loss equals plasma transferred energy; thermal heat partition and secondary spectrum are unresolved",
        "deposition_status": "NOT_COMPUTED", "causal_history_status": "HOLD",
        "collision_feedback": "NOT_APPLIED",
    }


def source_identity():
    identities = {}
    for name, expected in UPSTREAM_HASHES.items():
        path = HERE / "vendor" / "criptic" / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("IMMUTABLE_SOURCE_HASH_MISMATCH:" + name)
        identities[str(path.relative_to(HERE.parent))] = actual
    for path in (Path(__file__), HERE/"CONTRACT.json", SOURCE/"injection.py"):
        identities[str(path.relative_to(HERE.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return identities


def validation_campaign():
    started, cpu = time.perf_counter(), time.process_time()
    identities = source_identity()
    coarse = build_ledger(48, 8, 8)
    fine = build_ledger(64, 12, 12)
    low = build_ledger(64, 12, 12, window_eV=(1e6, 4e6))
    high = build_ledger(64, 12, 12, window_eV=(4e6, 1e7))
    key = "plasma_transferred_energy_j_m3_s"
    refinement = abs(coarse[key]/fine[key]-1)
    additivity = abs(math.fsum([low[key], high[key]])/fine[key]-1)
    energies = np.geomspace(1e6, 1e7, 17)
    ne = electron_density()
    si = proton_loss_si_J_s(energies, ne)
    cgs = proton_loss_cgs_J_s(energies, ne)
    raw = upstream_mks_loss_negative_control_J_s(energies, ne)
    parity = float(np.max(np.abs(cgs/si-1)))
    status = "PASS_SCOPED" if refinement <= 2e-6 and additivity <= 3e-13 and parity <= 3e-14 else "FAIL"
    return {
        "contract": "CR-PHYS04b-COULOMB-LOSS", "status": status,
        "source_sha256": identities, "upstream_commit": COMMIT,
        "command": " ".join(sys.argv), "python": platform.python_version(), "numpy": np.__version__,
        "coarse": coarse, "fine": fine, "one_to_four": low, "four_to_ten": high,
        "refinement_relative": refinement, "refinement_bound": 2e-6,
        "interval_additivity_relative": additivity, "cgs_si_relative_max": parity,
        "kernel_samples": {"proton_energy_eV": energies.tolist(), "si_J_s": si.tolist(), "cgs_J_s": cgs.tolist()},
        "original_upstream_mks_negative_control": {
            "classification": "EXPECTED_UNIT_CONVERSION_FAILURE",
            "raw_to_corrected_ratio": (raw/si).tolist(),
            "predicted_ratio": (4*math.pi*EPS0)**2,
            "relative_error_max": float(np.max(np.abs(raw/si-1)))},
        "minimum_proton_speed_to_electron_thermal_speed": float(
            C_M_S*math.sqrt(1e6*(1e6+2*PROTON_REST_EV))/(1e6+PROTON_REST_EV)
            / math.sqrt(2*KB_J_K*100/ME_KG)),
        "measured_wall_s": time.perf_counter()-started,
        "measured_process_cpu_s": time.process_time()-cpu,
        "claim_ceiling": "fixed-state instantaneous model diagnostic; no deposition, time integral, stopping evolution, continuum bound, or global history admission",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("output exists; choose a new evidence path")
    result = validation_campaign() if args.validation else build_ledger()
    output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    else:
        print(output, end="")
    if args.validation and result["status"] != "PASS_SCOPED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
