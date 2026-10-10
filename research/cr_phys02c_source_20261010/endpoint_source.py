# SPDX-License-Identifier: GPL-3.0-only
"""Conditional direct-born source Q(W,t)=t*A(W), including >1 keV support.

A is per proper m^3 s^2 eV; W is electron kinetic eV. Photon transport,
electron degradation, heat deposition and gas feedback are not implemented.
The frozen PR24 nonrelativistic endpoint is retained, not extrapolated.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
K_MIN, K_MAX = 1e6, 4e6
T_END = 1e10
TARGETS = ("H", "He")
FIELDS = ("number_m3_s2", "kinetic_eV_m3_s2", "primary_binding_eV_m3_s2")


@lru_cache(maxsize=1)
def modules():
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text())
    found = []
    for name in ("injection", "rudd"):
        relative = f"research/cr_phys01_20261010/src/{name}.py"
        path = REPO / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["local_source_files_sha256"][relative]:
            raise ValueError("SOURCE_BYTES_MISMATCH:" + relative)
        spec = importlib.util.spec_from_file_location("cr_phys02c_" + name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        found.append(module)
    return tuple(found)


@lru_cache(maxsize=2)
def gauss(order):
    if type(order) is not int or order not in (64, 96):
        raise ValueError("SOURCE_ORDER_CONTRACT_64_96")
    x, w = np.polynomial.legendre.leggauss(order)
    x.setflags(write=False)
    w.setflags(write=False)
    return x, w


def relative(a, b):
    a, b = np.asarray(a), np.asarray(b)
    scale = np.maximum(np.abs(a), np.abs(b))
    return np.divide(np.abs(a-b), scale, out=np.zeros_like(scale), where=scale > 0)


class EndpointSource:
    """Frozen fixed-bath source with species-specific proton lower bounds."""

    def __init__(self, order=64, enabled=True):
        gauss(order)
        if type(enabled) is not bool:
            raise ValueError("ENABLED_MUST_BE_BOOL")
        self.injection, self.rudd = modules()
        self.order = order
        self.enabled = enabled
        self.model = self.injection.InjectionModel(enabled=enabled)
        self.densities = {"H": 140.0*.99, "He": 140.0*.248/(4*(1-.248))*.99}
        self.endpoint_factor = 4*self.rudd.ME_OVER_MP

    def ionization_eV(self, target):
        if target not in TARGETS:
            raise ValueError("NEUTRAL_H_HE_ONLY")
        return self.rudd.TARGETS[target]["I_eV"]

    def endpoint(self, target, proton_eV=K_MAX):
        if proton_eV not in (K_MIN, K_MAX):
            raise ValueError("PROTON_ENDPOINT_CONTRACT")
        return self.endpoint_factor*proton_eV-self.ionization_eV(target)

    @staticmethod
    def _energy(energy):
        value = np.asarray(energy, dtype=float)
        if np.any(~np.isfinite(value)) or np.any(value < 0):
            raise ValueError("FINITE_NONNEGATIVE_ELECTRON_EV_REQUIRED")
        return value

    def _coefficient_at_lower(self, lower, target):
        """Evaluate two coefficients for each nonempty lower..4 MeV interval."""
        lower = np.asarray(lower, dtype=float)
        c1, c2 = np.zeros_like(lower), np.zeros_like(lower)
        active = lower < K_MAX
        if not self.enabled or not np.any(active):
            return c1, c2
        x, w = gauss(self.order)
        lo = np.log(lower[active])[:, None]
        # log1p preserves intervals very close to the upper endpoint.
        delta = np.log1p((K_MAX-lower[active])/lower[active])[:, None]
        k = np.exp(lo + .5*delta*(1+x))
        weights = .5*delta*w*k
        f1, f2 = self.rudd.rudd_factors(k, target)
        ion = self.ionization_eV(target)
        data = self.rudd.TARGETS[target]
        scale = 4*math.pi*self.rudd.A0_M**2*data["N"]*(self.rudd.RYDBERG_EV/ion)**2/ion
        flux = (weights*self.model.q_proper_m3_s_eV(k)
                * self.rudd.proton_speed_m_s(k)*self.densities[target])
        c1[active] = scale*np.sum(flux*f1, axis=1)
        c2[active] = scale*np.sum(flux*f2, axis=1)
        return c1, c2

    def spectrum_by_target(self, energy):
        """A_s(W), exact zero at/above the selected upper endpoint."""
        energy = self._energy(energy)
        flat = energy.reshape(-1)
        out = {}
        for target in TARGETS:
            ion = self.ionization_eV(target)
            supported = flat < self.endpoint(target)
            lower = np.maximum(K_MIN, (flat[supported]+ion)/self.endpoint_factor)
            c1, c2 = self._coefficient_at_lower(lower, target)
            ratio = flat[supported]/ion
            result = np.zeros_like(flat)
            result[supported] = (c1+c2*ratio)/(1+ratio)**3
            out[target] = result.reshape(energy.shape)
        return out

    def spectrum(self, energy):
        values = self.spectrum_by_target(energy)
        return values["H"]+values["He"]

    def above_1kev(self, energy):
        energy = self._energy(energy)
        if np.any(energy <= 1000):
            raise ValueError("DIRECT_BORN_ABOVE_1000_EV_ONLY")
        return self.spectrum(energy)

    def rate(self, energy, time_s):
        if (isinstance(time_s, (bool, np.bool_)) or not np.isscalar(time_s)
                or not math.isfinite(time_s) or not 0 <= time_s <= T_END):
            raise ValueError("LOCAL_RAMP_TIME_CONTRACT")
        return time_s*self.spectrum(energy)

    def wrong_constant_coefficient_control(self, energy, target):
        """Intentionally invalid above Wmax(1MeV), for negative tests only."""
        energy = self._energy(energy)
        c1, c2 = self._coefficient_at_lower(np.array([K_MIN]), target)
        ratio = energy/self.ionization_eV(target)
        return (c1[0]+c2[0]*ratio)/(1+ratio)**3

    def energy_panels(self, lower=0.0, upper=None):
        lower = float(self._energy(lower))
        maximum = max(self.endpoint(target) for target in TARGETS)
        upper = maximum if upper is None else float(self._energy(upper))
        if upper < lower:
            raise ValueError("ORDERED_ENERGY_INTERVAL_REQUIRED")
        hi = min(upper, maximum)
        if lower >= hi:
            return []
        edges = [lower, hi]
        for value in (10., 1000., *(self.endpoint(s, k) for s in TARGETS for k in (K_MIN, K_MAX))):
            if lower < value < hi:
                edges.append(value)
        return sorted(set(edges))

    def moments(self, lower=0.0, upper=None):
        """Integrate A(W), W*A(W), I_s*A_s(W) over all split W panels."""
        edges = self.energy_panels(lower, upper)
        result = {s: dict.fromkeys(FIELDS, 0.0) for s in TARGETS}
        x, w = gauss(self.order)
        for target in TARGETS:
            ion = self.ionization_eV(target)
            counts, energies = [], []
            for left, right in zip(edges[:-1], edges[1:]):
                lo, hi = np.log1p(np.array([left, right])/ion)
                coord = .5*(hi+lo)+.5*(hi-lo)*x
                energy = ion*np.expm1(coord)
                weights = .5*(hi-lo)*w*(energy+ion)
                values = self.spectrum_by_target(energy)[target]
                counts.append(float(weights @ values))
                energies.append(float(weights @ (energy*values)))
            number, kinetic = math.fsum(counts), math.fsum(energies)
            result[target] = dict(zip(FIELDS, (number, kinetic, ion*number)))
        return {"by_target": result, "total": {f: math.fsum(result[s][f] for s in TARGETS) for f in FIELDS}}

    def analytic_K_moments(self, lower=0.0, upper=None):
        """Independent order of integration: analytic SDCS W moments first."""
        self.energy_panels(lower, upper)  # Validate interval without changing it.
        result = {}
        x, w = gauss(self.order)
        for target in TARGETS:
            edges = [K_MIN, K_MAX]
            ion = self.ionization_eV(target)
            for energy in (lower, upper):
                if energy is not None:
                    split = (energy+ion)/self.endpoint_factor
                    if K_MIN < split < K_MAX:
                        edges.append(split)
            rows = []
            edges.sort()
            for left, right in zip(edges[:-1], edges[1:]):
                lo, hi = np.log([left, right])
                k = np.exp(.5*(lo+hi)+.5*(hi-lo)*x)
                weight = .5*(hi-lo)*w*k*self.model.q_proper_m3_s_eV(k)
                flux = weight*self.rudd.proton_speed_m_s(k)*self.densities[target]
                raw = self.rudd.cross_section_moments(k, target, lower, upper)
                rows.append([float(flux @ raw[f]) for f in ("sigma_m2", "secondary_eV_m2", "binding_eV_m2")])
            result[target] = {f: math.fsum(row[i] for row in rows) for i, f in enumerate(FIELDS)}
        return {"by_target": result, "total": {f: math.fsum(result[s][f] for s in TARGETS) for f in FIELDS}}

    def partitions(self):
        return {name: self.moments(lo, hi) for name, lo, hi in
                (("below_10", 0., 10.), ("10_to_1000", 10., 1000.),
                 ("above_1000", 1000., None), ("all", 0., None))}
