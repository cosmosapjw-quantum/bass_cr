"""SW91 H ground-state CI diagnostic candidate; no ODE or active C22B use.

Scholz & Walters, ApJ380302 (1991), Eq6/9 and Table2. Temperature domain
2000..1e8 K. CI reduced prefactor is independently checked against Table1.
The 1s->2s/2p coefficients have not been independently read in this intake;
those processes deliberately raise instead of fabricating coverage.
Local coefficient transcription is source-referenced, not original PDF-byte
verified. Source publication: https://doi.org/10.1086/170587 .
"""
from __future__ import annotations
import numpy as np

TEMPERATURE_DOMAIN_K = (2000.0, 1.0e8)
CI_POLYNOMIAL_A0_TO_A6 = (
    -96.1443, 37.9523, -7.96885, 0.883922,
    -0.0534513, 0.00166344, -0.0000208888,
)
KB_EV_K = 1.380649e-23 / 1.602176634e-19
# Present CODATA infinite-mass Rydberg energy. SW91 threshold is one Ry.
# Do not silently replace it by C22A's adopted chemical increment13.6 eV.
RYDBERG_EV = 13.605693122994
SOURCE = {
    "doi": "10.1086/170587",
    "url": "https://adsabs.harvard.edu/pdf/1991ApJ...380..302S",
    "locations": "CI Eq6,Eq9,Table2; comparison Table1",
    "coefficient_reading": "primary_PDF_text_and_source_focused_search",
    "original_PDF_byte_hash": None,
    "coverage": "H_ground_CI_only; 1s_to_2s_and_2p_coefficients_unverified",
    "activation": "DIAGNOSTIC_ONLY_NOT_ACTIVE_C22B",
}


class RateUnavailable(ValueError):
    """Requested process lacks verified coefficients in this provider."""


def _domain(temperature_K):
    temperature=np.asarray(temperature_K,dtype=float)
    lo,hi=TEMPERATURE_DOMAIN_K
    valid=np.isfinite(temperature)&(temperature>=lo)&(temperature<=hi)
    return temperature,valid


def ci_reduced_prefactor_cm3_s(temperature_K):
    """Return (Gamma,valid). Invalid-domain entries are NaN, never zero."""
    temperature,valid=_domain(temperature_K)
    rate=np.full(temperature.shape,np.nan,dtype=float)
    x=np.log(temperature[valid])
    poly=np.zeros_like(x)+CI_POLYNOMIAL_A0_TO_A6[-1]
    for coefficient in reversed(CI_POLYNOMIAL_A0_TO_A6[:-1]):
        poly=poly*x+coefficient
    rate[valid]=np.exp(poly)
    return rate,valid


def h_ci_cm3_s(temperature_K):
    """SW91 H ground-state CI, one-Ry threshold; no isotope extrapolation.

    q=Gamma*exp[-Ry/(kBT)] in cm3/s. Above fit-domain accuracy should not
    be confused with universal plasma-model validity or a global bound.
    """
    temperature,valid=_domain(temperature_K)
    gamma,_=ci_reduced_prefactor_cm3_s(temperature)
    result=np.full(temperature.shape,np.nan,dtype=float)
    result[valid]=gamma[valid]*np.exp(-RYDBERG_EV/(KB_EV_K*temperature[valid]))
    return result,valid


def h_excitation_cm3_s(temperature_K, upper):
    """No coefficient fabrication for unresolved Table3 excitation data."""
    raise RateUnavailable("SW91_1s_TO_2s_2p_TABLE3_NOT_INDEPENDENTLY_VERIFIED")


def metadata():
    return {"schema":"C22B_SW91_DIAGNOSTIC_PARTIAL_PROVIDER_V1",
            "source":dict(SOURCE), "temperature_domain_K":list(TEMPERATURE_DOMAIN_K),
            "threshold_eV":RYDBERG_EV,
            "threshold_convention":"SW91_one_Ry; distinct_from_C22A_13.6eV_chemical_increment",
            "outside_domain":"NaN_AND_FALSE_MASK_NO_EXTRAPOLATION_NO_ZERO",
            "new_ODE_runs":0,"global_error_bound":None}
