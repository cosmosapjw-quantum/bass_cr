"""C22D finite-source H1 CI with one consistent H-family energy registry.

This is a new conditional model. Frozen C22A/B/C files and completed solutions
are never modified. H1/D/T share the explicitly approximate electronic PI/RR
registry; the new CI source is H1-only, so an H1/D isotope quotient is invalid.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
import importlib.util
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C22C = HERE.parent / "cr_c22c_h1_excitation_20261022"
sys.path.insert(0, str(C22C))
_base = _load("c22d_frozen_c22c_model", C22C / "model.py")
_ci = _load("c22d_ci_finite", HERE / "ci_finite.py")
_opt = _load("c22d_optimized_kernel", HERE / "optimized_kernel.py")
CHI_EV = 13.6058
REGISTRY = "Hfamily_CCC13.6058_PI_support_refined_V1"
PROCESS = _ci.PROCESS
ACTIVE_T_DOMAIN_K = (3.0, 20000.0)  # RR lower endpoint is strictly excluded.


class AlignedPhotoProvider:
    """Retain PH2 coefficients and incident-energy axis; refine HI support.

    The approximation is explicit: sigma_new(E)=sigma_VF(E) for E>=13.6058eV,
    zero below this adopted CCC-aligned model support. The old 13.6eV support is not
    silently translated. Independent total RR/capture fits are unchanged; no
    claim of a Milne-consistent or LTE-complete cross-section set is made.
    13.6058eV is a source convention, not the precision physical H1 threshold.
    """
    def __init__(self, source):
        self.source = source

    def __getattr__(self, name):
        return getattr(self.source, name)

    def sigma(self, ion, energy_eV):
        sigma = self.source.sigma(ion, energy_eV)
        if ion == "HI":
            sigma = np.where(np.asarray(energy_eV) >= CHI_EV, sigma, 0.0)
        return sigma


class AlignedAtomicView:
    """Composition over immutable AtomicNetwork21; no configuration bypass."""
    def __init__(self, source):
        self.source = source
        self.provider = AlignedPhotoProvider(source.provider)

    def __getattr__(self, name):
        return getattr(self.source, name)


def align_new_model(c):
    """Update only freshly constructed A/B/C objects, never shared arrays."""
    b, a = c.base, c.base.base
    atomic = AlignedAtomicView(a.atomic)
    thresholds = a.thresholds.copy()
    thresholds[0] = CHI_EV
    binding = np.zeros_like(a.binding)
    for lower, upper, channel in atomic.edges:
        binding[upper] = binding[lower] + thresholds[channel]
    thresholds.flags.writeable = False
    binding.flags.writeable = False
    for layer in (a, b, c):
        layer.atomic, layer.thresholds, layer.binding = atomic, thresholds, binding
        # All energy methods delegate down, so establish new energies bottom-up.
        layer.initial_energy = layer.energy(0.0, layer.initial_state())
    return c


class ThermochemicalFactory:
    def __init__(self, ellmax=8):
        self.base_factory = _base.ThermochemicalFactory(ellmax=ellmax)
        self.ci_provider = _ci.CCCFiniteH1CI(HERE / "sources/CCC_TICS_1S.txt")

    def build(self, case):
        case = dict(case)
        if case.get("energy_registry", REGISTRY) != REGISTRY:
            raise ValueError("C22D_ENERGY_REGISTRY_MISMATCH")
        enabled = case.get("h1_ci_enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError("CI_SWITCH_MUST_BE_BOOL")
        if PROCESS in case.get("required_processes", []) and not enabled:
            raise ValueError("REQUIRED_CI_PROCESS_DISABLED")
        base_case = {k: v for k, v in case.items()
                     if k not in ("energy_registry", "h1_ci_enabled")}
        if "required_processes" in base_case:
            base_case["required_processes"] = sorted(set(base_case["required_processes"]) - {PROCESS})
        c = align_new_model(self.base_factory.build(base_case))
        return H1IonizationModel(c, case, self.ci_provider)


class H1IonizationModel(_base.H1ExcitationModel):
    """78 full / 75 active coordinates at ellmax8; one cumulative CI count."""
    def __init__(self, base, case, ci_provider):
        self.base, self.case, self.ci_provider = base, dict(case), ci_provider
        for key in ("parent", "kinetic", "atomic", "nk", "ax", "gx", "iu", "iesc",
                    "iwg", "iwr", "irr", "iabs", "itau", "eta_end", "thresholds",
                    "binding", "parameters", "initial_photons", "initial_electrons",
                    "initial_temperature", "photon_scale", "ibath", "Tcmb0",
                    "ic2s", "ic2p", "h1_ground", "provider", "excitation_enabled"):
            setattr(self, key, getattr(base, key))
        self.ci_enabled = case.get("h1_ci_enabled", True)
        self.optimized_excitation = _opt.OptimizedExcitation(
            base.provider, sys.modules[_base.CCCFiniteExcitation.__module__])
        self.ici, self.size = base.size, base.size + 1
        self.h1_ion = self.atomic.blocks["H1"][1]
        self.invariant_indices = base.invariant_indices.copy()
        self.active_indices = np.setdiff1d(np.arange(self.size), self.invariant_indices)
        self.solver_size = len(self.active_indices)
        self._y0 = np.r_[base.initial_state(), 0.0]
        self.project(self._y0)
        self.initial_energy = self.energy(0.0, self._y0)

    def fields(self, eta, full):
        full = np.asarray(full)
        if full.shape != (self.size,) or not np.all(np.isfinite(full)):
            raise ValueError("C22D_INVALID_FULL_STATE")
        return self.base.fields(eta, full[:self.base.size])

    def ci_events(self, eta, full, fields=None):
        if not self.ci_enabled:
            return 0.0  # Explicit switch; no assertion about an absent rate.
        q = self.fields(eta, full) if fields is None else fields
        temperature = q["temperature_K"]
        if not ACTIVE_T_DOMAIN_K[0] < temperature <= ACTIVE_T_DOMAIN_K[1]:
            raise ValueError("C22D_ACTIVE_TEMPERATURE_SELECTOR")
        if q["nH_ref_cm3"] > 0.01:
            raise ValueError("C22D_DILUTE_PILOT_DENSITY_SELECTOR")
        rate = self.ci_provider.evaluate(temperature).q_cm3_s
        neutral = self.atomic.physical_abundances(full[self.ax])[self.h1_ground]
        return float(q["n_e_cm3"] * neutral * rate / q["H"])

    def rhs(self, eta, full):
        q = self.fields(eta, full)
        derivative = np.zeros(self.size)
        derivative[:self.base.size] = _opt.c22c_rhs_from_fields(
            self.base, eta, np.asarray(full)[:self.base.size], q,
            excitation_provider=self.optimized_excitation)
        events = self.ci_events(eta, full, q)
        derivative[self.ax.start + self.h1_ground] -= events / self.atomic.scales[self.h1_ground]
        derivative[self.ax.start + self.h1_ion] += events / self.atomic.scales[self.h1_ion]
        derivative[self.iu] -= CHI_EV * events
        derivative[self.ici] = events
        return derivative

    def energy(self, eta, full):
        # CI exchanges gas kinetic and binding energies; no escaped CI reservoir.
        return self.base.energy(eta, np.asarray(full)[:self.base.size])

    def summarize(self, eta, full):
        eta, full = np.asarray(eta), np.asarray(full)
        self.project(full)
        h = self.base.summarize(eta, full[:self.base.size])
        count = full[self.ici]
        h["Y"] = full
        abundance = self.atomic.scales[:, None] * full[self.ax]
        ne = self.atomic.q @ abundance
        h["charge_photon_relative_residual"] = (
            ne + full[self.irr] - full[self.iabs] - count - self.initial_electrons
        ) / max(self.initial_photons, 1.0)
        h["H1_CI_events_per_H"] = count
        h["H1_CI_thermal_to_binding_eV_per_H"] = CHI_EV * count
        values = [self.ci_provider.evaluate(t) for t in h["temperature_K"]]
        for source, target in (("q_cm3_s", "H1_CI_core_q_cm3_s"),
                               ("log10_q_cm3_s", "H1_CI_core_log10_q_cm3_s"),
                               ("float64_underflow", "H1_CI_source_underflow")):
            h[target] = np.array([getattr(v, source) for v in values])
        h["H1_CI_log10_tail_coefficient_per_assumed_a0sq"] = np.array([
            self.ci_provider.log10_conditional_tail_per_a0sq_cap(t) for t in h["temperature_K"]])
        h["H1_CI_events_per_H_per_eta"] = np.array([
            self.ci_events(t, y) for t, y in zip(eta, full.T)])
        return h

    def metadata(self):
        data = self.base.metadata()
        data.update(schema="C22D_H1_FINITE_CI_ALIGNED_ENERGY_V1", case=self.case,
                    state_size=self.size, solver_state_size=self.solver_size,
                    ci_enabled=self.ci_enabled, ci_count_index=self.ici,
                    energy_registry=REGISTRY, hydrogen_family_chi_eV=CHI_EV,
                    active_coordinate_indices=self.active_indices.tolist(),
                    activation_temperature_selector_K=list(ACTIVE_T_DOMAIN_K),
                    activation_lower_endpoint="strict because inherited RR domain is T>3K",
                    dilute_pilot_density_selector_nHref_cm3=0.01,
                    ci_rate="finite CCC TICS PL moment; continuum and physical tail OPEN",
                    PI_adapter="HI support E>=13.6058eV; original PH2 shape and energy axis retained",
                    RR_adapter="number/capture fits unchanged; export uses common new binding increment",
                    energy_identity="dU_CI=-chi*r; d(binding)_CI=+chi*r; escaped_CI=0",
                    particle_count="N=sum nuclear populations+electrons; T=2U/(3kB*N) includes -T*Nprime/N once",
                    charge_ledger="ne_per_H+C_RR-C_PI-C_CI-ne_initial",
                    isotope_quotient="H1/D shared ionization-fraction quotient INVALID when H1-only CI active",
                    optimization="one fresh fields dictionary per RHS; no cross-state or temperature cache; same per-entry arithmetic order",
                    full_thermochemical_radiative_closure="OPEN", global_error_bound=None)
        data["available_processes"] = sorted(set(data["available_processes"]) | {PROCESS})
        data["unmodeled_processes"] = [p for p in data["unmodeled_processes"]
                                      if p not in ("collisional_ionization", "collisional_excitation_cooling")]
        data["unmodeled_processes"] += [
            "CI physical tail/interpolation error and other species CI",
            "three_body_recombination; omission assessed conditionally at observed density",
            "nonthermal electron distribution and secondary-electron energy partition",
            "excitation channels beyond explicit H1 n2 finite source"]
        return data
