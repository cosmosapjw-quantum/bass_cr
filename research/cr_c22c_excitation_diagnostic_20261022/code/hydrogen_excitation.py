"""SW91 Table3 H1s->2s/2p diagnostic; never activates an old trajectory.

Scholz & Walters1991, ApJ380,302, doi:10.1086/170587, Eqs12,13,16,17.
Coefficients were read from the primary PDF printed p305, not a graph.
Fit domain2000..1e8K; below-domain returns NaN/False, never extrapolated0.
Maxwellian electrons, ground-state H, original one-Ry energy convention.
"""
from __future__ import annotations
import numpy as np

KB_EV_K = 1.380649e-23 / 1.602176634e-19
RYDBERG_EV = 13.605693122994
DELTA_EV = 0.75 * RYDBERG_EV
DOMAIN_K = (2000.0, 1e8)
BREAKS_K = (6e4, 6e6)
# Rows: [2000,60000), [60000,6000000), [6000000,1e8]K.
# Columns: polynomial powers y^0,...,y^5, y=natural log(T/K).
COEFFICIENTS = {
    "2s": (
        (-32.99613,18.58848,-6.052265,.8603783,-.05717760,.001451330),
        (286.9759,-107.7956,15.24107,-1.080538,.03836975,-.0005467273),
        (-2760.4708,793.39351,-91.198462,5.1993362,-.14685343,.0016404093),
    ),
    "2p": (
        (-163.0155,87.95711,-20.57117,2.359573,-.1339059,.003021507),
        (527.9996,-193.9399,27.18982,-1.883399,.06462462,-.0008811076),
        (-2813.3632,815.09685,-94.418414,5.4280565,-.15467120,.0017439112),
    ),
}


def _polynomial_and_derivative(y, coefficients):
    """Horner P(y),P'(y), no finite differences or rate interpolation."""
    p = np.full_like(y, coefficients[-1])
    d = np.zeros_like(y)
    for a in reversed(coefficients[:-1]):
        d = d*y+p
        p = p*y+a
    return p,d


def excitation(temperature_K, upper):
    """Return q[cm3/s], dlogq/dlogT, valid mask, piecewise region.

    At either internal boundary, the upper region owns the value. The fits
    are only approximately continuous; derivative is one-sided there.
    """
    if upper not in COEFFICIENTS:
        raise ValueError("upper must be 2s or 2p")
    t = np.asarray(temperature_K,dtype=np.float64)
    valid = np.isfinite(t)&(t>=DOMAIN_K[0])&(t<=DOMAIN_K[1])
    q = np.full(t.shape,np.nan)
    slope = np.full(t.shape,np.nan)
    region = np.full(t.shape,-1,dtype=np.int8)
    region[valid]=np.searchsorted(BREAKS_K,t[valid],side="right")
    for i,c in enumerate(COEFFICIENTS[upper]):
        active=valid&(region==i)
        y=np.log(t[active])
        p,d=_polynomial_and_derivative(y,c)
        u=DELTA_EV/(KB_EV_K*t[active])
        q[active]=np.exp(p-u)
        slope[active]=d+u
    return q,slope,valid,region


def cooling_coefficient_eV_cm3_s(temperature_K):
    """H n=2 excitation-only kinetic loss; excludes CI,n>2,He/Li."""
    qs,_,valid,region=excitation(temperature_K,"2s")
    qp,_,_,_=excitation(temperature_K,"2p")
    return DELTA_EV*(qs+qp),valid,region


def optically_thin_paired_flux_eV_cm3_s(temperature_K,ne_cm3,nH1s_cm3):
    """Gas loss and emitted-photon ledger gain from a single shared flux.

    Prompt radiative decay/escape is a separate low-density, optically-thin
    closure; photons are not inserted into a finite UV cohort or Einstein
    source by this helper. D/T isotope sharing is not silently assumed.
    """
    t,ne,nh=np.broadcast_arrays(np.asarray(temperature_K,dtype=float),
                               np.asarray(ne_cm3,dtype=float),
                               np.asarray(nH1s_cm3,dtype=float))
    if not (np.isfinite(ne).all() and np.isfinite(nh).all()) or np.any(ne<0) or np.any(nh<0):
        raise ValueError("finite nonnegative electron and ground-state H densities required")
    coefficient,valid,region=cooling_coefficient_eV_cm3_s(t)
    emitted=coefficient*ne*nh
    return -emitted,emitted,valid,region
