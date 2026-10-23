"""Pinned PW19-release spectral photoelectron supply; no cascade or ODE.

The release column is S=4*pi*nu*J_nu, not energy integrated in a bin.
q(K) = S(K+chi) sigma(K+chi)/(EV_ERG*(K+chi)**2).
All yields are per absorbing target per proper second in the bath frame.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EV_ERG = 1.602176634e-12
CHANNELS = {"HI": (1, 1), "HeI": (2, 2), "HeII": (2, 1)}
DATA_SHA256 = "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389"
# Exact float values of the three rows in the SHA-pinned official table.
# Constructor validation binds *all* coefficients, not merely a channel label.
_ADMITTED_ROWS = {
    "HI": (13.60, 50000., .4298, 54750., 32.88, 2.963, 0., 0., 0.),
    "HeI": (24.59, 50000., 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    "HeII": (54.42, 50000., 1.720, 13690., 32.88, 2.963, 0., 0., 0.),
}


def finite_number(value, label, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label+": finite real number required")
    value = float(value)
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(label+": invalid domain")
    return value


@dataclass(frozen=True)
class Verner96:
    channel: str
    threshold_eV: float
    maximum_eV: float
    E0_eV: float
    sigma0_Mb: float
    ya: float
    P: float
    yw: float
    y0: float
    y1: float

    def __post_init__(self):
        self.validate_admitted()

    def validate_admitted(self):
        actual = (self.threshold_eV,self.maximum_eV,self.E0_eV,self.sigma0_Mb,
                  self.ya,self.P,self.yw,self.y0,self.y1)
        if (self.channel not in _ADMITTED_ROWS
            or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in actual)
            or actual != _ADMITTED_ROWS[self.channel]):
            raise ValueError("ATOMIC_PARAMETERS_NOT_THE_PINNED_ADMITTED_ROW")

    @classmethod
    def from_table(cls, channel, data_dir=None):
        if channel not in CHANNELS:
            raise ValueError("UNSUPPORTED_ATOMIC_CHANNEL_NOT_ZERO")
        path = (Path(data_dir) if data_dir else ROOT/"data")/"verner_photo.dat"
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != DATA_SHA256:
            raise ValueError("VERNER_SOURCE_IDENTITY_MISMATCH")
        matches = []
        for line in data.decode("ascii").splitlines():
            row = line.split()
            if (int(row[0]), int(row[1])) == CHANNELS[channel]:
                matches.append([float(x) for x in row[2:]])
        if len(matches) != 1:
            raise ValueError("VERNER_ROW_MISSING_OR_DUPLICATED")
        return cls(channel, *matches[0])

    def sigma_cm2(self, photon_eV):
        self.validate_admitted()
        energy = finite_number(photon_eV, "photon_eV", True)
        if energy > self.maximum_eV:
            raise ValueError("ATOMIC_RATE_ABOVE_DOMAIN_UNKNOWN_NOT_ZERO")
        if energy < self.threshold_eV:
            return 0.0
        x = energy/self.E0_eV-self.y0
        y = math.hypot(x, self.y1)
        return (1e-18*self.sigma0_Mb*((x-1)**2+self.yw**2)
                *y**(0.5*self.P-5.5)*(1+math.sqrt(y/self.ya))**(-self.P))


class PW19Spectrum:
    """Three exact release nodes with paired original-format byte evidence.

    Positive log-log interpolation is our declared finite representation.
    No redshift interpolation, clipping, extrapolation, or z=0 repair.
    """
    def __init__(self, redshift, data_dir=None):
        z = finite_number(redshift, "redshift", True)
        contract = json.loads((ROOT/"CONTRACT.json").read_text())
        entries = {row["redshift"]:row for row in contract["spectra"]}
        if z not in entries:
            raise ValueError("REDSHIFT_NOT_ONE_OF_THREE_ADMITTED_NODES")
        entry = entries[z]
        path = (Path(data_dir) if data_dir else ROOT/"data")/entry["filename"]
        data = path.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("SPECTRUM_SOURCE_IDENTITY_MISMATCH")
        rows = list(csv.DictReader(data.decode().splitlines()))
        energy = tuple(float(row["E (eV)"]) for row in rows)
        spectral = tuple(float(row["I (erg/s/cm**2)"]) for row in rows)
        if len(rows) != 626 or any(not math.isfinite(x) or x <= 0 for x in energy+spectral):
            raise ValueError("NONPOSITIVE_OR_INVALID_SPECTRUM")
        if any(b <= a for a,b in zip(energy, energy[1:])):
            raise ValueError("NONMONOTONIC_SPECTRUM")
        self.redshift = z
        self.energy_eV = energy
        self.spectral_S = spectral
        self.log_energy = tuple(math.log(x) for x in energy)
        self.log_S = tuple(math.log(x) for x in spectral)
        self.source_sha256 = entry["sha256"]

    def evaluate(self, photon_eV):
        energy = finite_number(photon_eV, "photon_eV", True)
        if not self.energy_eV[0] <= energy <= self.energy_eV[-1]:
            raise ValueError("SPECTRAL_ENERGY_OUT_OF_DOMAIN")
        i = bisect_right(self.energy_eV, energy)-1
        if energy == self.energy_eV[i]:
            return self.spectral_S[i]
        theta = math.log(energy/self.energy_eV[i])/math.log(self.energy_eV[i+1]/self.energy_eV[i])
        return math.exp((1-theta)*self.log_S[i]+theta*self.log_S[i+1])

    def photon_flux_moments(self, low_eV, high_eV):
        """Known radiation count flux and energy flux only; no absorption rate.

        Piecewise power-law integrals are analytic. Units cm^-2 s^-1 and
        eV cm^-2 s^-1. Values outside the tabulated spectrum are rejected.
        """
        low = finite_number(low_eV, "low_eV", True)
        high = finite_number(high_eV, "high_eV", True)
        if not self.energy_eV[0] <= low < high <= self.energy_eV[-1]:
            raise ValueError("RADIATION_FLUX_INTERVAL_OUT_OF_DOMAIN")
        edges = [low]+[x for x in self.energy_eV if low < x < high]+[high]
        number, energy = [], []
        for a,b in zip(edges,edges[1:]):
            sa,sb = self.evaluate(a),self.evaluate(b)
            width = math.log(b/a)
            slope = math.log(sb/sa)/width
            def kernel(power):
                exponent = power*width
                return width if exponent == 0 else math.expm1(exponent)/power
            number.append(sa/(EV_ERG*a)*kernel(slope-1))
            energy.append(sa/EV_ERG*kernel(slope))
        return {"number_cm2_s":math.fsum(number),"energy_eV_cm2_s":math.fsum(energy)}


def electron_density(spectrum, atom, kinetic_eV):
    if not isinstance(spectrum,PW19Spectrum) or not isinstance(atom,Verner96):
        raise TypeError("EXPLICIT_PINNED_SOURCE_AND_ATOMIC_PROVIDER_REQUIRED")
    atom.validate_admitted()
    kinetic = finite_number(kinetic_eV, "kinetic_eV", True)
    photon = kinetic+atom.threshold_eV
    sigma = atom.sigma_cm2(photon)
    return spectrum.evaluate(photon)*sigma/(EV_ERG*photon*photon)


@lru_cache(maxsize=4)
def _gauss(order):
    if type(order) is not int or order not in (8,16,32):
        raise ValueError("SUPPORTED_GAUSS_ORDERS_8_16_32")
    from numpy.polynomial.legendre import leggauss
    x,w = leggauss(order)
    if any(v <= 0 for v in w):
        raise ArithmeticError("NONPOSITIVE_QUADRATURE_WEIGHT")
    return tuple(zip(map(float,x),map(float,w)))


def photoelectron_atoms(spectrum, atom, *, order=16, kinetic_cuts_eV=(10.0,9937.21)):
    """Positive finite quadrature measure; electron weights per target/s.

    Splits at every spectral node and each requested kinetic boundary.
    The atomic upper photon energy is retained as a source support limit.
    """
    if not isinstance(spectrum,PW19Spectrum) or not isinstance(atom,Verner96):
        raise TypeError("EXPLICIT_PINNED_SOURCE_AND_ATOMIC_PROVIDER_REQUIRED")
    atom.validate_admitted()
    low,high = atom.threshold_eV,atom.maximum_eV
    if not spectrum.energy_eV[0] <= low < high <= spectrum.energy_eV[-1]:
        raise ValueError("SOURCE_DOES_NOT_COVER_ATOMIC_DOMAIN")
    cuts = tuple(finite_number(x,"kinetic_cut",True) for x in kinetic_cuts_eV)
    if any(b <= a for a,b in zip(cuts,cuts[1:])) or any(not 0 < x < high-low for x in cuts):
        raise ValueError("KINETIC_CUTS_STRICT_INTERIOR_ASCENDING_REQUIRED")
    edges = sorted(set([low,high]+[x for x in spectrum.energy_eV if low < x < high]+[low+x for x in cuts]))
    nodes = _gauss(order)
    result = []
    for a,b in zip(edges,edges[1:]):
        loga,logb = math.log(a),math.log(b)
        centre,half = (loga+logb)/2,(logb-loga)/2
        for node,weight in nodes:
            photon = math.exp(centre+half*node)
            kinetic = photon-low
            # dN/dln(photon energy) = S*sigma/(EV_ERG*photon).
            rate = half*weight*spectrum.evaluate(photon)*atom.sigma_cm2(photon)/(EV_ERG*photon)
            if not math.isfinite(rate) or rate <= 0 or kinetic < 0:
                raise ArithmeticError("INVALID_POSITIVE_SOURCE_QUADRATURE")
            result.append((kinetic,rate))
    return tuple(result)


def summarize_atoms(atoms, threshold_eV, *, kinetic_cuts_eV=(10.0,9937.21)):
    threshold = finite_number(threshold_eV,"threshold_eV",True)
    rows = tuple(atoms)
    if not rows or any(not math.isfinite(k) or not math.isfinite(w) or k < 0 or w <= 0 for k,w in rows):
        raise ValueError("POSITIVE_FINITE_ATOMS_REQUIRED")
    cuts = tuple(finite_number(x,"kinetic_cut",True) for x in kinetic_cuts_eV)
    if any(b <= a for a,b in zip(cuts,cuts[1:])):
        raise ValueError("KINETIC_CUTS_ASCENDING_REQUIRED")
    number = math.fsum(w for k,w in rows)
    kinetic = math.fsum(k*w for k,w in rows)
    binding = threshold*number
    absorbed = math.fsum((k+threshold)*w for k,w in rows)
    bins = []
    for i in range(len(cuts)+1):
        selected = [(k,w) for k,w in rows if bisect_right(cuts,k)==i]
        bins.append({"number_per_target_s":math.fsum(w for k,w in selected),
                     "kinetic_eV_per_target_s":math.fsum(k*w for k,w in selected)})
    return {"number_per_target_s":number,"kinetic_eV_per_target_s":kinetic,
            "binding_eV_per_target_s":binding,"absorbed_photon_eV_per_target_s":absorbed,
            "energy_ledger_residual_eV_per_target_s":absorbed-binding-kinetic,
            "bins":bins,"atom_count":len(rows),"frame":"bath_frame_rest_target",
            "normalization":"per_absorbing_target_per_proper_second",
            "secondary_heat_eV_per_target_s":None,"global_error_bound":None}
