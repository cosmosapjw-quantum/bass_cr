"""Nonrelativistic isotropic-blackbody thermostat energy exchange.

Qgas > 0 heats electrons/gas. Return eV per conserved Href per proper second.
The reservoir's opposite cumulative export is implemented in model.py.
This module never adds a second CMB density to the Einstein equations.
"""
from __future__ import annotations
import math
from scipy.constants import Boltzmann, Planck, c, electron_mass

EV_ERG = 1.602176634e-12
K_B_CGS = Boltzmann * 1e7
C_CGS = c * 100.0
M_E_G = electron_mass * 1000.0
H_CGS = Planck * 1e7
SIGMA_T_CM2 = 6.6524587051e-25  # Exact inherited numerical constant.
A_R_CGS = 8 * math.pi**5 * K_B_CGS**4 / (15 * H_CGS**3 * C_CGS**3)
TCMB0_K = 2.7255
RELATIVISTIC_SELECTOR_MAX = 0.01


def gas_exchange_eV_per_H_s(temperature_K, radiation_temperature_K, electrons_per_H):
    t, tg, ne = map(float, (temperature_K, radiation_temperature_K, electrons_per_H))
    if not all(math.isfinite(x) for x in (t, tg, ne)) or t <= 0 or tg <= 0 or ne < 0:
        raise ValueError("COMPTON_INPUT_DOMAIN")
    if K_B_CGS * max(t, tg) / (M_E_G * C_CGS**2) > RELATIVISTIC_SELECTOR_MAX:
        raise ValueError("COMPTON_NONRELATIVISTIC_SELECTOR_EXCEEDED")
    return (4 * SIGMA_T_CM2 * C_CGS * A_R_CGS * tg**4 * ne
            * K_B_CGS * (tg - t) / (M_E_G * C_CGS**2) / EV_ERG)


def constants_record():
    return {"sigma_T_cm2": SIGMA_T_CM2, "c_cm_s": C_CGS,
            "kB_erg_K": K_B_CGS, "h_erg_s": H_CGS, "electron_mass_g": M_E_G,
            "radiation_constant_erg_cm3_K4": A_R_CGS,
            "electron_mass_source": "scipy.constants;exact runtime version recorded",
            "sigma_T_source": "frozen C21O lrs_boltzmann.py constant",
            "source_formula": "Hui_Gnedin1997 AppendixA;isotropic nonrelativistic blackbody thermostat",
            "relativistic_selector_max": RELATIVISTIC_SELECTOR_MAX}
