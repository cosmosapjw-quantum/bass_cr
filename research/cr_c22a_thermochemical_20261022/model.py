"""C22A: dynamic thermal/finite-UV extension of the preserved C21O LRS model.

Units: eta=ln(a/a_initial), proper H [s^-1], atomic/UV counts per reference
hydrogen nucleus, energies eV per reference hydrogen nucleus.  Atomic gas and
the added UV cohorts have an imposed isotropic stress closure.  Existing
nonbaryonic Vlasov, CMB and neutrino moments retain their C21O conventions.
Thermal/chemical/UV trace energies are diagnosed but are not Einstein sources.

This separately identified model has photoionization + Case-A RR.  Its RR
kinetic cooling is the energy moment implied by the frozen VF rate fit; that
constitutive approximation is not certified by the number-rate fit accuracy.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import math
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
C21O = HERE.parent / "cr_c21o_hheli_z2_20261021"
sys.path.insert(0, str(C21O))
from coupled_model import CoupledFactory, GAMMA_PER_NE, component_fields
from atomic_network import CHANNELS, CHANNEL_NAMES
from rr_energy_moment import rr_energy_factor

K_B_EV_K = 1.380649e-23 / 1.602176634e-19
EV_J = 1.602176634e-19
C_CM_S = 29979245800.0
UV_INITIAL_PER_H = np.array([0.05, 0.25, 0.003, 0.0002, 0.00001, 0.000001])
AVAILABLE_PROCESSES = frozenset({"valence_photoionization", "Case_A_RR",
                                "VF_fit_RR_energy_moment", "finite_UV_depletion",
                                "mean_expansion_work", "electron_Thomson_feedback"})
PARENT_SCIENCE_COMMIT = "6b6db06e8148e6826a2d5bf7dbc53d362126ca62"
PARENT_RECOVERY_COMMIT = "a5e12c5f3e6d323e211d65fefad34060ec07eff0"
PARENT_SOURCE_IDENTITY = "c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f"


class ThermochemicalFactory:
    def __init__(self, ellmax=8):
        self.parent = CoupledFactory(ellmax=ellmax)

    def build(self, case):
        case = dict(case)
        parent = self.parent.build(float(case.get("signed_sigma", 0.0)),
                                   float(case.get("signed_pi_m", 0.0)),
                                   float(case.get("signed_pi_r", 0.0)),
                                   thomson=case.get("thomson", True))
        return ThermochemicalModel(parent, case)


class ThermochemicalModel:
    def __init__(self, parent, case):
        self.parent = parent
        self.kinetic = parent.kinetic
        self.atomic = parent.atomic
        self.case = dict(case)
        supported = {"name", "signed_sigma", "signed_pi_m", "signed_pi_r",
                     "photon_scale", "temperature_K", "initial_ionized",
                     "thomson", "required_processes", "ellmax"}
        if set(case)-supported:
            raise ValueError("UNSUPPORTED_INITIAL_OR_MODEL_INPUT: " + ",".join(sorted(set(case)-supported)))
        requested = set(case.get("required_processes", AVAILABLE_PROCESSES))
        missing = requested - AVAILABLE_PROCESSES
        if missing:
            raise ValueError("ATOMIC_ENERGY_COVERAGE_MISSING: " + ",".join(sorted(missing)))
        self.nk = parent.nk
        self.ax = slice(self.nk, self.nk + 21)
        self.gx = slice(self.nk + 21, self.nk + 27)
        self.iu, self.iesc, self.iwg, self.iwr, self.irr, self.iabs, self.itau = range(self.nk + 27, self.nk + 34)
        self.size = self.nk + 34
        self.eta_end = float(self.kinetic.source.xmax)
        self.thresholds = np.array([r["chi_eV"] for r in CHANNELS])
        self.binding = np.zeros(21)
        for lower, upper, ch in self.atomic.edges:
            self.binding[upper] = self.binding[lower] + self.thresholds[ch]
        self.parameters = np.array([self.atomic.provider.rows[k]["RR"] for k in CHANNEL_NAMES])
        if np.any(abs(self.parameters[:, 1]) > 1):
            raise ValueError("RR_ENERGY_POSITIVITY_DOMAIN")
        self.initial_temperature = float(case.get("temperature_K", 300.0))
        self.photon_scale = float(case.get("photon_scale", 1.0))
        if not math.isfinite(self.photon_scale) or self.photon_scale < 0:
            raise ValueError("INVALID_PHOTON_INVENTORY")
        lo, hi = self.atomic.rr_temperature_domain_K
        if not lo < self.initial_temperature < hi:
            raise ValueError("RR_T_DOMAIN")
        self._y0 = self._make_initial_state()
        self.initial_energy = self.energy(0.0, self._y0)
        self.initial_photons = float(np.sum(self._y0[self.gx]))
        self.initial_electrons = float(self.atomic.electrons_per_H(self._y0[self.ax]))

    def _make_initial_state(self):
        y = np.zeros(self.size)
        y[:self.nk] = self.kinetic.initial_state()
        x = self.atomic.initial_state()
        if self.case.get("initial_ionized", False):
            for name, total in self.atomic.initial_nucleus_totals.items():
                if total > 0:
                    ids = self.atomic.blocks[name]
                    x[list(ids)] = 0.0
                    x[ids[-1]] = total / self.atomic.scales[ids[-1]]
        y[self.ax] = x
        # No nuclear or beta energy closure is supplied in this model.  The
        # inherited zero n/T inventory is retained as an exact invariant face.
        if any(np.any(x[list(self.atomic.blocks[k])] != 0.0) for k in ("n", "T")):
            raise ValueError("BETA_ENERGY_COVERAGE_REQUIRED_FOR_NONZERO_N_T")
        y[self.gx] = UV_INITIAL_PER_H * self.photon_scale
        abundance = self.atomic.physical_abundances(x)
        npart = float(np.sum(abundance) + self.atomic.q @ abundance)
        y[self.iu] = 1.5 * K_B_EV_K * self.initial_temperature * npart
        return y

    def initial_state(self):
        return self._y0.copy()

    def photon_energies(self, eta):
        # Isotropic moment closure: E redshifts with the mean scale factor.
        return np.asarray(self.atomic.energies_eV) * math.exp(-float(eta))

    def transition_times(self):
        # Split exactly at every adopted support/algorithm threshold.  This
        # avoids fitting a smooth ODE step across a moving support boundary.
        bounds = {0.0, self.eta_end}
        for energy in self.atomic.energies_eV:
            for chi in list(self.thresholds) + [64.39]:
                value = math.log(float(energy) / chi)
                if 0 < value < self.eta_end:
                    bounds.add(value)
        return sorted(bounds)

    def temperature(self, y):
        abundance = self.atomic.physical_abundances(y[self.ax])
        npart = float(np.sum(abundance) + self.atomic.q @ abundance)
        if not math.isfinite(npart) or npart <= 0:
            raise ValueError("NONPOSITIVE_THERMAL_PARTICLE_COUNT")
        temp = float(y[self.iu]) / (1.5 * K_B_EV_K * npart)
        lo, hi = self.atomic.rr_temperature_domain_K
        if not math.isfinite(temp) or not lo <= temp <= hi:
            raise ValueError(f"RR_T_DOMAIN: {temp!r} outside [{lo},{hi}] K")
        return temp

    def fields(self, eta, y):
        if np.shape(y) != (self.size,) or not np.isfinite(y).all():
            raise ValueError("INVALID_C22A_STATE")
        q = self.kinetic.fields(float(eta), y[:self.nk])
        q["z"] = 1 / q["a"] - 1
        q["nH_ref_cm3"] = self.parent.nHref0_cm3 / q["a"]**3
        q["n_e_cm3"] = q["nH_ref_cm3"] * self.atomic.electrons_per_H(y[self.ax])
        q["GammaT_physical"] = q["n_e_cm3"] * GAMMA_PER_NE
        q["GammaT"] = q["GammaT_physical"] if self.parent.thomson else 0.0
        q["temperature_K"] = self.temperature(y)
        return q

    def events(self, eta, y, fields=None):
        q = self.fields(eta, y) if fields is None else fields
        abundance = self.atomic.physical_abundances(y[self.ax])
        energy = self.photon_energies(eta)
        sigma = np.array([self.atomic.provider.sigma(k, energy) * 1e-18 for k in CHANNEL_NAMES])
        temp = q["temperature_K"]
        alpha = np.array([self.atomic.provider.rr(k, temp) for k in CHANNEL_NAMES])
        factors = np.array([rr_energy_factor(p, temp) for p in self.parameters])
        capture_energy = K_B_EV_K * temp * factors
        photo = np.empty((len(self.atomic.edges), 6))
        recombination = np.empty(len(self.atomic.edges))
        invh = 1.0 / q["H"]
        for edge, (lower, upper, ch) in enumerate(self.atomic.edges):
            photo[edge] = (C_CM_S * q["nH_ref_cm3"] * abundance[lower]
                           * sigma[ch] * y[self.gx] * invh)
            recombination[edge] = q["n_e_cm3"] * abundance[upper] * alpha[ch] * invh
        return photo, recombination, capture_energy, energy

    def rhs(self, eta, y):
        obj = self.kinetic
        q = self.fields(eta, y)
        h, s = q["H"], q["s"]
        v, gamma = s / h, q["GammaT"] / h
        dy = np.zeros(self.size)
        dy[:4] = (obj.source.href / h, v,
                   -3*y[2] + 3*obj.source.h0**2/(obj.source.href*h)
                   * (q["Pi_radiation_norm"] + q["Pi_matter_norm"]), 0.0)
        n = obj.n
        for i, (key, matrix) in enumerate((("E_gamma", obj.energy_matrix),
                                          ("N_gamma", obj.number_matrix),
                                          ("E_nu", obj.energy_matrix),
                                          ("N_nu", obj.number_matrix))):
            sl = slice(4+i*n, 4+(i+1)*n)
            dy[sl] = v * (matrix @ q[key])
            if i < 2:
                dy[sl] -= gamma * obj.thomson * q[key]
        photo, rr, capture, energy = self.events(eta, y, q)
        dx, dg = dy[self.ax], dy[self.gx]
        dy[self.iu] = -2.0 * y[self.iu]
        dy[self.iwg] = 2.0 * y[self.iu]
        dy[self.iwr] = float(energy @ y[self.gx])
        for edge, (lower, upper, ch) in enumerate(self.atomic.edges):
            p = photo[edge]
            ionizations = float(np.sum(p))
            r = rr[edge]
            net = ionizations - r
            dx[lower] -= net / self.atomic.scales[lower]
            dx[upper] += net / self.atomic.scales[upper]
            dg -= p
            dy[self.iu] += float((energy-self.thresholds[ch]) @ p) - capture[ch]*r
            dy[self.iesc] += (self.thresholds[ch] + capture[ch])*r
            dy[self.irr] += r
            dy[self.iabs] += ionizations
        dy[self.itau] = q["GammaT_physical"] / h
        return dy

    def energy(self, eta, y):
        abundance = self.atomic.physical_abundances(y[self.ax])
        return float(y[self.iu] + self.binding @ abundance
                     + self.photon_energies(eta) @ y[self.gx]
                     + y[self.iesc] + y[self.iwg] + y[self.iwr])

    def rhs_energy_residual(self, eta, y):
        dy = self.rhs(eta, y)
        return float(dy[self.iu] + self.binding @ (self.atomic.scales * dy[self.ax])
                     + self.photon_energies(eta) @ dy[self.gx]
                     - self.photon_energies(eta) @ y[self.gx]
                     + dy[self.iesc] + dy[self.iwg] + dy[self.iwr])

    def metadata(self):
        return {"schema": "C22A_THERMOCHEMICAL_MODEL_V1", "case": self.case,
                "state_size": self.size, "ellmax": self.kinetic.ellmax,
                "parent_science_commit": PARENT_SCIENCE_COMMIT,
                "parent_recovery_commit": PARENT_RECOVERY_COMMIT,
                "parent_execution_source_identity": PARENT_SOURCE_IDENTITY,
                "initial_mapping": self.parent.mapping,
                "initial_temperature_K": self.initial_temperature,
                "initial_UV_per_H": self._y0[self.gx].tolist(),
                "initial_UV_energies_eV": self.photon_energies(0).tolist(),
                "RR_energy_closure": "VF_fit_implied_Maxwellian_kinetic_moment;derivative_accuracy_not_certified",
                "RR_T_domain_K": list(self.atomic.rr_temperature_domain_K),
                "photo_scope": "ground_valence;LiI_2s_only;no_Auger",
                "gas_stress": "isotropic", "UV_stress": "imposed_isotropic_moment_closure",
                "matter_stress": "separate_nonbaryonic_Vlasov",
                "new_T_and_UV": "dynamical;finite_initial_photon_inventory;no_external_emissivity",
                "available_processes": sorted(AVAILABLE_PROCESSES),
                "CMB_feedback": "algebraic_ne_to_elastic_Thomson",
                "cancellation_fraction_missing": "NaN_with_defined_mask_only_for_exact_zero_denominator",
                "Einstein_trace_energy_feedback": "NOT_INCLUDED;diagnosed_separately",
                "beta_nuclear": "inactive_declared_zero_n_T;nonzero_inventory_requires_energy_contract",
                "atomic_populations": list(self.atomic.state_labels),
                "unmodeled_processes": [x for x in self.atomic.unmodeled_channels if x != "photon_transport"]
                    + ["angular_spectral_UV_transport_beyond_isotropic_cohorts", "Compton_energy_exchange",
                       "collisional_excitation_cooling", "free_free_cooling", "stellar_emissivity"],
                "transition_times_eta": self.transition_times(),
                "global_error_bound": None}

    def summarize(self, eta, Y):
        eta, Y = np.asarray(eta), np.asarray(Y)
        if Y.shape != (self.size, len(eta)):
            raise ValueError("HISTORY_SHAPE")
        q = [self.fields(t, y) for t, y in zip(eta, Y.T)]
        comp = [component_fields(d) for d in q]
        abundance = self.atomic.scales[:, None] * Y[self.ax]
        energies = np.array([self.photon_energies(t) for t in eta])
        total = np.array([self.energy(t, y) for t, y in zip(eta, Y.T)])
        ne = self.atomic.q @ abundance
        photons = np.sum(Y[self.gx], axis=0)
        nres = np.zeros(len(eta))
        for name, initial in self.atomic.initial_nucleus_totals.items():
            current = np.sum(abundance[list(self.atomic.blocks[name])], axis=0)
            if initial > 0:
                nres = np.maximum(nres, np.abs(current/initial-1))
            elif np.any(current != 0):
                raise ArithmeticError("ZERO_INITIAL_INVENTORY_CHANGED")
        escale = max(abs(self.initial_energy), 1e-30)
        pscale = max(self.initial_photons, 1.0)
        h = {"eta": eta, "Y": Y, "proper_elapsed_s": Y[0]/self.kinetic.source.href,
             "temperature_K": np.array([d["temperature_K"] for d in q]),
             "tau_T": Y[self.itau], "UV_photons_per_H": Y[self.gx].T,
             "UV_cohort_energies_eV": energies,
             "UV_energy_eV_per_H": np.sum(energies*Y[self.gx].T, axis=1),
             "thermal_energy_eV_per_H": Y[self.iu],
             "ionization_energy_eV_per_H": self.binding @ abundance,
             "escaped_energy_eV_per_H": Y[self.iesc],
             "gas_work_eV_per_H": Y[self.iwg], "UV_work_eV_per_H": Y[self.iwr],
             "recombination_count_per_H": Y[self.irr], "absorption_count_per_H": Y[self.iabs],
             "energy_total_eV_per_H": total,
             "energy_residual_eV_per_H": total-self.initial_energy,
             "energy_relative_residual": (total-self.initial_energy)/escale,
             "nucleus_max_relative_residual": nres,
             "charge_photon_relative_residual": (ne+Y[self.irr]-Y[self.iabs]-self.initial_electrons)/pscale,
             "photon_number_relative_residual": (photons+Y[self.iabs]-self.initial_photons)/pscale,
             "atomic_scaled": Y[self.ax], "atomic_abundance_per_Href": abundance,
             "atomic_state_labels": np.asarray(self.atomic.state_labels, dtype="U24")}
        for key in ("a", "z", "H", "s", "nH_ref_cm3", "n_e_cm3"):
            h[key] = np.array([d[key] for d in q])
        for key in comp[0]:
            h[key] = np.array([np.nan if d[key] is None else d[key] for d in comp])
        h["cancellation_fraction_defined"] = np.array(
            [d["cancellation_fraction"] is not None for d in comp], dtype=bool)
        trace = (h["thermal_energy_eV_per_H"]+h["ionization_energy_eV_per_H"]
                 +h["UV_energy_eV_per_H"])*h["nH_ref_cm3"]*1e6*EV_J
        critical = self.kinetic.source.rhocrit_j_m3*(h["H"]/self.kinetic.source.h0)**2
        h["omitted_trace_energy_H2_fraction"] = trace/critical
        h["H1_ionized_fraction"] = Y[self.ax][self.atomic.blocks["H1"][1]]
        h["RR_capture_factor"] = np.array([[rr_energy_factor(p, t) for p in self.parameters]
                                          for t in h["temperature_K"]])
        h["minimum_population_scaled"] = np.min(Y[self.ax], axis=0)
        h["minimum_UV_count_per_H"] = np.min(Y[self.gx], axis=0)
        return h
