"""RR kinetic-energy moment implied by a Verner--Ferland Maxwellian rate fit.

This is a new constitutive approximation derived from a rate fit. The integral
identity is exact for a temperature-independent RR cross section and Maxwellian
electrons. A fit's pointwise rate accuracy does not certify derivative accuracy.
Units: alpha [cm^3/s], T [K], cooling [erg cm^3/s].
"""
from __future__ import annotations

import numpy as np

K_B_CGS = 1.380649e-16


def rr_energy_factor(parameters, temperature_K):
    """Return <E_capture>/(k_B T), stably for the selected VF fit family.

    For b in [-1,1], the sum below is manifestly positive and smaller than one.
    Its form avoids subtractive cancellation in the hot limit.
    """
    a, b, t0, t1 = map(float, parameters)
    t = np.asarray(temperature_K, dtype=float)
    if not np.all(np.isfinite(t)) or np.any(t <= 0):
        raise ValueError("temperature must be finite and positive")
    if not (a > 0 and t0 > 0 and t1 > 0 and -1 <= b <= 1):
        raise ValueError("parameters outside proven positive-factor family")
    return (1-b)/(2*(1+np.sqrt(t/t0))) + (1+b)/(2*(1+np.sqrt(t/t1)))


def vf_alpha(parameters, temperature_K):
    a, b, t0, t1 = map(float, parameters)
    t = np.asarray(temperature_K, dtype=float)
    s0 = np.sqrt(t/t0)
    return a/(s0*(1+s0)**(1-b)*(1+np.sqrt(t/t1))**(1+b))


def rr_cooling_erg_cm3_s(parameters, temperature_K):
    t = np.asarray(temperature_K, dtype=float)
    return K_B_CGS*t*vf_alpha(parameters,t)*rr_energy_factor(parameters,t)
