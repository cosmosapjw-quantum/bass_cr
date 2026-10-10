"""Fixed-bath direct-born electron source convolution; no history admission.

Source coefficients A(W) have units m^-3 s^-2 eV^-1, Q(W,t)=t*A(W).
Integrated observables are proper m^-3 counts or eV m^-3 energies. Each
cohort is observed on its own characteristic grid before aggregation.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
RESEARCH = ROOT.parent
T_END = 1e10
OBSERVABLES = (
    "active_electron_number", "active_energy_eV", "binding_energy_eV",
    "excitation_energy_eV", "coulomb_heat_eV", "cutoff_electron_number",
    "cutoff_energy_eV", "number_ledger", "energy_ledger_eV",
    "ion_HI", "ion_HeI", "ion_HeII", "exc_HI", "exc_HeI", "exc_HeII",
)
ENERGY_FIELDS = ("active_energy_eV", "binding_energy_eV", "excitation_energy_eV",
                 "coulomb_heat_eV", "cutoff_energy_eV")


@lru_cache(maxsize=1)
def modules():
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text())
    found = []
    for name, relative in zip(("injection", "rudd", "kernel"),
                             manifest["local_source_files_sha256"]):
        path = RESEARCH.parent / relative
        expected = manifest["local_source_files_sha256"][relative]
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("SOURCE_BYTES_MISMATCH:" + relative)
        spec = importlib.util.spec_from_file_location("cr_phys05_" + name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        found.append(module)
    found[-1].verify_sources()
    return tuple(found)


@lru_cache(maxsize=6)
def gauss(order):
    if type(order) is not int or order not in (8, 16, 32, 64, 96):
        raise ValueError("QUADRATURE_CONTRACT")
    return np.polynomial.legendre.leggauss(order)


def relative(a, b):
    a, b = np.asarray(a), np.asarray(b)
    scale = np.maximum(np.abs(a), np.abs(b))
    return np.divide(np.abs(a-b), scale, out=np.zeros_like(scale), where=scale > 0)


class DirectSource:
    def __init__(self, order=64, enabled=True):
        if order not in (64, 96) or type(order) is not int:
            raise ValueError("SOURCE_ORDER_CONTRACT")
        if type(enabled) is not bool:
            raise ValueError("ENABLED_MUST_BE_BOOL")
        self.injection, self.rudd, self.kernel = modules()
        self.order = order
        self.enabled = enabled
        self.model = self.injection.InjectionModel(enabled=enabled)
        x, w = gauss(order)
        lo, hi = np.log([1e6, 4e6])
        self.k = np.exp((hi+lo)/2 + (hi-lo)/2*x)
        self.weights = (hi-lo)/2*w*self.k*self.model.q_proper_m3_s_eV(self.k)
        self.densities = {"H": 140*.99, "He": 140*.248/(4*(1-.248))*.99}
        self.coefficients = self._coefficients(self.k, self.weights)

    def _coefficients(self, k, weights):
        out = {}
        for target, density in self.densities.items():
            p = self.rudd.TARGETS[target]
            ion = p["I_eV"]
            f1, f2 = self.rudd.rudd_factors(k, target)
            scale = 4*np.pi*self.rudd.A0_M**2*p["N"]*(self.rudd.RYDBERG_EV/ion)**2/ion
            flux = weights*self.rudd.proton_speed_m_s(k)*density
            out[target] = np.array([scale*np.dot(flux, f1), scale*np.dot(flux, f2), ion])
        return out

    def spectrum(self, energy):
        energy = np.asarray(energy, dtype=float)
        if np.any(~np.isfinite(energy)) or np.any(energy < 0) or np.any(energy > 1000):
            raise ValueError("SPECTRUM_DOMAIN_0_1000_EV")
        out = np.zeros_like(energy)
        for c1, c2, ion in self.coefficients.values():
            x = energy/ion
            out += (c1+c2*x)/(1+x)**3
        return out

    def moments(self, lower=0.0, upper=None):
        number = energy = binding = 0.0
        for target, density in self.densities.items():
            moments = self.rudd.cross_section_moments(self.k, target, lower, upper)
            flux = self.weights*self.rudd.proton_speed_m_s(self.k)*density
            number += float(flux @ moments["sigma_m2"])
            energy += float(flux @ moments["secondary_eV_m2"])
            binding += float(flux @ moments["binding_eV_m2"])
        return {"number_m3_s2": number, "kinetic_eV_m3_s2": energy,
                "primary_binding_eV_m3_s2": binding}

    def partitions(self):
        return {key: self.moments(lo, hi) for key, lo, hi in
                (("below_10", 0, 10), ("selected_10_1000", 10, 1000),
                 ("above_1000", 1000, None), ("all", 0, None))}

    def projected(self, generator):
        """Conservative spectrum projection; normalize only for conditioning."""
        x, w = gauss(self.order)
        lo, hi = generator.grid[:-1], generator.grid[1:]
        energy = (lo[:, None]+hi[:, None])/2+(hi-lo)[:, None]/2*x
        weights = (hi-lo)[:, None]/2*w*self.spectrum(energy)
        counts, cutoff_n, cutoff_e = self.kernel.project_daughters(
            generator.grid, energy.ravel(), weights.ravel())
        state = np.r_[counts, np.zeros(7), cutoff_n, cutoff_e]
        norm = self.moments(10, 1000)["number_m3_s2"]
        if norm:
            state /= norm
        return state, norm

    def bianchi_samples(self):
        rows = []
        for time_s in (.25*T_END, .5*T_END, T_END):
            pop = self.injection.transport_population(
                self.model, time_s, 3.3e-17, 3.3e-18,
                energy_order=48, age_order=8, mu_order=8)
            coefficients = self._coefficients(pop["nodes"]["kinetic_eV"],
                                             pop["nodes"]["number_density_m3"])
            errors = {target: relative(values[:2], time_s*self.coefficients[target][:2]).tolist()
                      for target, values in coefficients.items()}
            rows.append({"time_s": time_s, "relative_by_target": errors})
        return rows


def birth_rule(time_s, order):
    if not np.isscalar(time_s) or isinstance(time_s, (bool, np.bool_)):
        raise ValueError("TIME_CONTRACT")
    if not np.isfinite(time_s) or not 0 <= time_s <= T_END:
        raise ValueError("TIME_CONTRACT")
    if order not in (8, 16, 32) or type(order) is not int:
        raise ValueError("BIRTH_ORDER_CONTRACT")
    x, w = gauss(order)
    birth = time_s*(1+x)/2
    return birth, time_s-birth, time_s*w/2


def arrival_birth_rule(time_s, order, generator):
    """Panel only at the unchanged kernel's exact cutoff arrival ages."""
    birth_rule(time_s, order)  # The original domain/order contract applies.
    _, _, kernel = modules()
    arrival = kernel.cooling_time(generator.grid, generator.gas)
    interior = time_s-arrival[(arrival > 0) & (arrival < time_s)]
    boundaries = np.unique(np.r_[0., interior, time_s])
    if time_s == 0:
        return (*birth_rule(0, order), boundaries)
    x, w = gauss(order)
    lower, upper = boundaries[:-1], boundaries[1:]
    births = ((lower[:, None]+upper[:, None])/2+(upper-lower)[:, None]/2*x).ravel()
    weights = ((upper-lower)[:, None]/2*w).ravel()
    return births, time_s-births, weights, boundaries


def observation_vector(generator, state):
    obs = generator.observe(state)
    obs.update(zip(("ion_HI", "ion_HeI", "ion_HeII"), obs["ionization_counts"]))
    obs.update(zip(("exc_HI", "exc_HeI", "exc_HeII"), obs["excitation_counts"]))
    return np.array([obs[name] for name in OBSERVABLES])


def convolve(time_s=T_END, intervals=128, birth_order=32, enabled=True, panelized=False):
    """Evaluate both frozen source rules through the same causal cohorts."""
    births, ages, weights = birth_rule(time_s, birth_order)
    if type(enabled) is not bool:
        raise ValueError("ENABLED_MUST_BE_BOOL")
    _, _, kernel = modules()
    generator = kernel.assemble(intervals=intervals)
    boundaries = np.array([0., time_s])
    if panelized:
        births, ages, weights, boundaries = arrival_birth_rule(time_s, birth_order, generator)
    sources = [DirectSource(order, enabled) for order in (64, 96)]
    projected = [source.projected(generator) for source in sources]
    initial = np.column_stack([row[0] for row in projected])
    norms = np.array([row[1] for row in projected])
    totals = np.zeros((2, len(OBSERVABLES)))
    minimum = 0.0
    rows = []
    if time_s > 0 and enabled:
        for birth, age, weight in zip(births, ages, weights):
            evolved = kernel.evolve(generator, initial, float(age))
            grid = getattr(evolved, "energy_grid", generator.grid)
            minimum = min(minimum, float(evolved.min()))
            observations = np.vstack([
                observation_vector(generator, kernel.CharacteristicState(evolved[:, j], grid, age))
                for j in range(2)])
            totals += weight*birth*norms[:, None]*observations
            rows.append({"birth_time_s": float(birth), "age_s": float(age),
                         "integration_weight_s": float(weight),
                         "minimum_state": float(evolved.min())})
    return {
        "time_s": time_s, "grid_intervals": intervals, "birth_order": birth_order,
        "source_orders": [64, 96],
        "observables": [dict(zip(OBSERVABLES, map(float, total))) for total in totals],
        "injected": [{key.removesuffix("_s2"): .5*time_s**2*value for key, value in source.moments(10, 1000).items()}
                     for source in sources],
        "minimum_state": minimum, "cohorts": rows,
        "birth_panel_boundaries_s": boundaries.tolist(),
        "birth_rule": "arrival-panelized GL" if panelized else "global GL",
        "grid_semantics": "each cohort observed with its own characteristic grid",
        "cutoff_status": "unresolved count and kinetic energy; not passed to P02A",
    }
