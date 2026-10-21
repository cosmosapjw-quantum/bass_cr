"""Conditional primordial charge kinetics coupled to the frozen LRS moments.

New C21O physical problem, not a reexecution of the collisionless C21L/M/N IVP.
40 LRS states (L=8), 21 nuclear/atomic populations, one Thomson-depth state.
The gas temperature and isotropic UV cohort field are prescribed inputs.
Only the gas electron density feeds back, through elastic photon Thomson
scattering. Gas thermal/ionization energy and UV energy are trace diagnostics,
not added to the Einstein source. Atomic gas anisotropic stress is zero by
an explicit isotropic-gas closure. This is NOT a full thermochemical model.
"""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"

import copy
from dataclasses import replace
import math
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import atomic_mass, Boltzmann, elementary_charge

HERE = Path(__file__).resolve().parent
C21N = HERE.parent / "cr_c21n_mass_shell_cache_20261021"
sys.path.insert(0, str(C21N))
from builder import IndependentStressBuilder, component_fields
from mass_shell_derivatives import packet_derivatives
from lrs_boltzmann import legendre_matrix, thomson_coeffs, GAMMA_PER_NE
from atomic_network import AtomicNetwork21

RTOL = 3e-11
ATOL = 3e-13
Z_START = 20.0
Z_END = 2.0
N_OUTPUT = 201
OMEGA_B = 0.049309230511847414
C_SI = 299792458.0


class CoupledFactory:
    """One immutable momentum/angular preparation and atomic provider per worker."""
    def __init__(self, ellmax=8, optimized=True):
        self.ellmax = int(ellmax)
        self.builder = IndependentStressBuilder(optimized=optimized)
        template = copy.copy(self.builder.template)
        # A new immutable time-domain source; old lock/manifests remain intact.
        template.source = replace(template.source, aend=1 / (1 + Z_END))
        if self.ellmax != template.ellmax:
            template.ellmax = self.ellmax
            template.n = self.ellmax + 1
            template.energy_matrix = legendre_matrix(self.ellmax, power=4)
            template.number_matrix = legendre_matrix(self.ellmax, power=3)
            template.thomson = thomson_coeffs(self.ellmax)
            for arr in (template.energy_matrix, template.number_matrix, template.thomson):
                arr.flags.writeable = False
        self.builder.template = template
        self.atomic = AtomicNetwork21(electronic_isotope_equality=True)

    def build(self, signed_sigma, signed_pi_m, signed_pi_r, *, thomson=True):
        obj, mapping = self.builder.build(signed_sigma, signed_pi_m, signed_pi_r)
        return CoupledModel(obj, self.atomic, mapping, thomson=thomson)


class CoupledModel:
    def __init__(self, kinetic, atomic, mapping, *, thomson=True):
        self.kinetic, self.atomic, self.mapping = kinetic, atomic, mapping
        self.thomson = bool(thomson)
        self.nk = 4 + 4 * kinetic.n
        self.size = self.nk + 22
        x0 = atomic.initial_state()
        abundance = atomic.physical_abundances(x0)
        self.baryons_per_Href = float(np.dot(atomic.A, abundance))
        self.nHref0_cm3 = (OMEGA_B * kinetic.source.rhocrit_j_m3 / C_SI**2
                           / atomic_mass / self.baryons_per_Href / 1e6)
        if not self.nHref0_cm3 > 0:
            raise ValueError("INVALID_BARYON_NORMALIZATION")

    def initial_state(self):
        return np.r_[self.kinetic.initial_state(), self.atomic.initial_state(), 0.0]

    def fields(self, eta, y):
        if np.shape(y) != (self.size,) or not np.isfinite(y).all():
            raise ValueError("INVALID_COMBINED_STATE")
        q = self.kinetic.fields(float(eta), y[:self.nk])
        q["z"] = 1 / q["a"] - 1
        q["nH_ref_cm3"] = self.nHref0_cm3 / q["a"]**3
        q["n_e_cm3"] = q["nH_ref_cm3"] * self.atomic.electrons_per_H(y[self.nk:-1])
        q["GammaT_physical"] = q["n_e_cm3"] * GAMMA_PER_NE
        q["GammaT"] = q["GammaT_physical"] if self.thomson else 0.0
        return q

    def rhs(self, eta, y):
        obj = self.kinetic
        q = self.fields(eta, y)
        h, s = q["H"], q["s"]
        v, gamma = s / h, q["GammaT"] / h
        eg, ng, en, nn = (q[k] for k in ("E_gamma", "N_gamma", "E_nu", "N_nu"))
        # Same FP64 expressions and reduction order as CanonicalFVSpecies.rhs.
        # A fresh result array is necessary: solve_ivp retains derivative arrays.
        dy = np.empty(self.size, dtype=np.float64)
        dy[:4] = (obj.source.href / h, v,
                  -3 * y[2] + 3 * obj.source.h0**2 / (obj.source.href * h)
                  * (q["Pi_radiation_norm"] + q["Pi_matter_norm"]), 0.0)
        n = obj.n
        dy[4:4+n] = v * (obj.energy_matrix @ eg) - gamma * obj.thomson * eg
        dy[4+n:4+2*n] = v * (obj.number_matrix @ ng) - gamma * obj.thomson * ng
        dy[4+2*n:4+3*n] = v * (obj.energy_matrix @ en)
        dy[4+3*n:4+4*n] = v * (obj.number_matrix @ nn)
        dy[self.nk:-1] = self.atomic.rhs(q["z"], y[self.nk:-1], h, q["nH_ref_cm3"])
        # Always record the physical optical depth; an off-control only removes
        # its action on the moments, not the physical electron diagnostic.
        dy[-1] = q["GammaT_physical"] / h
        return dy

    def jacobian(self, eta, y):
        """Analytic block Jacobian; no changes to the production RHS.

        Packet-pressure derivatives reuse the already admitted C21N mass-shell
        differential identities. These differentiate the mathematical sums,
        not the discrete FP rounding operation.
        """
        obj = self.kinetic
        q = self.fields(eta, y)
        h, s, a = q["H"], q["s"], q["a"]
        n, nk, N = obj.n, self.nk, self.size
        hg = np.zeros(N)
        hg[1] = -3 * obj.source.h0**2 * q["Pi_matter_norm"] / h
        hg[2] = obj.source.href * s / h
        hg[4] = obj.source.h0**2 * obj.omega_gamma / (2 * h * a**4)
        hg[4+2*n] = obj.source.h0**2 * obj.omega_nu / (2 * h * a**4)
        vg = -s / h**2 * hg
        vg[2] += obj.source.href / h
        gg = -q["GammaT"] / h**2 * hg
        pg = -q["GammaT_physical"] / h**2 * hg
        charge_gradient = (q["nH_ref_cm3"] * np.asarray(self.atomic.q)
                           * np.asarray(self.atomic.scales) * GAMMA_PER_NE / h)
        pg[nk:-1] = charge_gradient
        if self.thomson:
            gg[nk:-1] = charge_gradient
        pgrad = np.zeros(N)
        d0 = packet_derivatives(obj.momentum, eta, q["b"], 0.0)
        d1 = packet_derivatives(obj.momentum, eta, q["b"], 1.0)
        pgrad[1] = obj._mass_pref * (d1["pi_s_eta"] - d0["pi_s_eta"])
        pgrad[6] = obj.omega_gamma / (3 * a**4)
        pgrad[6+2*n] = obj.omega_nu / (3 * a**4)
        J = np.zeros((N, N), dtype=np.float64)
        J[0] = -obj.source.href / h**2 * hg
        J[1] = vg
        total_p = q["Pi_radiation_norm"] + q["Pi_matter_norm"]
        J[2] = (3 * obj.source.h0**2 / obj.source.href
                * (pgrad / h - total_p / h**2 * hg))
        J[2, 2] -= 3
        for i, (key, matrix) in enumerate((("E_gamma", obj.energy_matrix),
                                           ("N_gamma", obj.number_matrix),
                                           ("E_nu", obj.energy_matrix),
                                           ("N_nu", obj.number_matrix))):
            sl = slice(4+i*n, 4+(i+1)*n)
            moment = q[key]
            J[sl] = np.outer(matrix @ moment, vg)
            J[sl, sl] += (s / h) * matrix
            if i < 2:
                J[sl] -= np.outer(obj.thomson * moment, gg)
                J[sl, sl] -= (q["GammaT"] / h) * np.diag(obj.thomson)
        dx = self.atomic.rhs(q["z"], y[nk:-1], h, q["nH_ref_cm3"])
        J[nk:-1] = -np.outer(dx / h, hg)
        J[nk:-1, nk:-1] = self.atomic.jacobian(q["z"], y[nk:-1], h, q["nH_ref_cm3"])
        J[-1] = pg
        return J

    def integrate(self, *, method="BDF", n=N_OUTPUT, rtol=RTOL, atol=ATOL,
                  analytic_jacobian=True):
        before = time.perf_counter()
        kwargs = {"jac": self.jacobian} if analytic_jacobian and method in ("BDF", "Radau") else {}
        result = solve_ivp(self.rhs, (0., self.kinetic.source.xmax), self.initial_state(),
                           method=method, rtol=rtol, atol=atol,
                           t_eval=np.linspace(0., self.kinetic.source.xmax, n), **kwargs)
        elapsed = time.perf_counter() - before
        if not result.success:
            error = RuntimeError("COUPLED_INTEGRATION_FAILED: " + result.message)
            error.partial_solution = result
            raise error
        history, diagnostics = self.summarize(result.t, result.y)
        receipt = {"method": method, "rtol": rtol, "atol": atol,
                   "analytic_jacobian": bool(kwargs), "ellmax": self.kinetic.ellmax,
                   "nfev": result.nfev, "njev": result.njev, "nlu": result.nlu,
                   "wall_seconds": elapsed, "state_shape": list(result.y.shape),
                   "initial_mapping": self.mapping, "diagnostics": diagnostics,
                   "thomson_moment_feedback": self.thomson,
                   "endpoint": {k: float(history[k][-1]) for k in
                                ("z", "Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F",
                                 "n_e_cm3", "tau_T", "temperature_K")},
                   "global_error_bound": None}
        return history, receipt

    def summarize(self, eta, y):
        obj, nk = self.kinetic, self.nk
        q = [self.fields(float(t), y[:, i]) for i, t in enumerate(eta)]
        comp = [component_fields(d) for d in q]
        x = y[nk:-1]
        abundance = np.asarray(self.atomic.scales)[:, None] * x
        history = {"eta": eta, "Y": y, "atomic_scaled": x,
                   "atomic_abundance_per_Href": abundance,
                   "atomic_state_labels": np.asarray(self.atomic.state_labels, dtype="U24"),
                   "proper_elapsed_s": y[0] / obj.source.href, "tau_T": y[-1]}
        for key in ("a", "z", "b", "H", "s", "n_e_cm3", "nH_ref_cm3", "GammaT"):
            history[key] = np.array([d[key] for d in q])
        for key in comp[0]:
            history[key] = np.array([np.nan if d[key] is None else d[key] for d in comp])
        for sector in ("m", "gamma", "nu", "r", "tot"):
            p = history["p_" + sector + "_J_m3"]
            history["pi_" + sector + "_orthonormal_diagonal_J_m3"] = np.stack((-p, -p, 2*p), axis=1)
        history["sigma_orthonormal_diagonal_s_inverse"] = np.stack(
            (-history["s"], -history["s"], 2*history["s"]), axis=1)
        for key in ("E_gamma", "N_gamma", "E_nu", "N_nu"):
            history[key] = np.stack([d[key] for d in q])
        rates = [self.atomic.rate_data(d["z"]) for d in q]
        temp = np.array([r.temperature_K for r in rates])
        history["temperature_K"] = temp
        history["photo_rates_s_inverse"] = np.stack([r.photo_rates_s for r in rates])
        history["RR_rates_cm3_s"] = np.stack([r.rr_cm3_s for r in rates])
        history["UV_flux_cohorts_cm2_s"] = np.stack([r.diagnostic["cohort_flux_cm2_s"] for r in rates])
        history["UV_cohort_energies_eV"] = np.array(self.atomic.energies_eV)
        ne_m3 = history["n_e_cm3"] * 1e6
        nuclei_m3 = history["nH_ref_cm3"] * 1e6 * np.sum(abundance, axis=0)
        gas_u = 1.5 * (nuclei_m3 + ne_m3) * Boltzmann * temp
        grav_energy = np.array([obj.source.rhocrit_j_m3 *
                               (d["dust_energy_norm"] + d["massive_energy_norm"] +
                                d["rad_energy_norm"]) for d in q])
        history["gas_thermal_energy_J_m3"] = gas_u
        history["gas_thermal_to_gravitating_energy"] = gas_u / grav_energy
        ion_cost_eV = np.zeros(21)
        thresholds = (13.6, 24.59, 54.42, 5.392, 75.64, 122.5)
        for lower, upper, channel in self.atomic.edges:
            ion_cost_eV[upper] = ion_cost_eV[lower] + thresholds[channel]
        ion_u = (ion_cost_eV @ abundance) * history["nH_ref_cm3"] * 1e6 * elementary_charge
        uv_u = (history["UV_flux_cohorts_cm2_s"] @ self.atomic.energies_eV
                * 1e4 * elementary_charge / C_SI)
        history["atomic_ionization_energy_J_m3"] = ion_u
        history["prescribed_UV_energy_J_m3"] = uv_u
        critical_H_energy = obj.source.rhocrit_j_m3 * (history["H"] / obj.source.h0)**2
        eps_trace = (gas_u + ion_u + uv_u) / critical_H_energy
        history["omitted_trace_energy_H2_fraction"] = eps_trace
        history["frozen_state_H_shift_energy_only"] = np.expm1(.5 * np.log1p(eps_trace))
        history["trace_bound_scope"] = np.asarray("instantaneous added-energy diagnostic; not trajectory or missing-reaction error bound")
        photo_energy = [self.atomic.energy_diagnostics(d["z"], x[:, i], d["nH_ref_cm3"])
                        for i, d in enumerate(q)]
        for key in ("absorbed_energy_J_cm3_s", "ionization_threshold_J_cm3_s", "primary_photoelectron_J_cm3_s"):
            history[key] = np.array([e[key] for e in photo_energy])
        # A deliberately conservative upper diagnostic: every baryon carries
        # 200 eV of unmodeled binding/thermal-scale energy. This is not a
        # numerical error bound nor a bound on missing reaction physics.
        history["omitted_200eV_per_baryon_energy_ratio"] = (
            history["nH_ref_cm3"] * 1e6 * self.baryons_per_Href * 200 * elementary_charge
            / grav_energy)
        baryon = np.asarray(self.atomic.A) @ abundance
        hres = max(abs(d["Einstein_H2"] / d["H"]**2 - 1) for d in q)
        nres = max(max(abs(d["N_gamma"][0]-1), abs(d["N_nu"][0]-1)) for d in q)
        # A dense angular sample is a diagnostic, not a global positivity proof.
        mu = np.linspace(-1, 1, 1025)
        basis = np.polynomial.legendre.legvander(mu, obj.ellmax)
        weights = 2 * np.arange(obj.n) + 1
        minangular = min(float(np.min(history[key] * weights @ basis.T))
                         for key in ("E_gamma", "N_gamma", "E_nu", "N_nu"))
        mnumber = max(abs(d["massive_physical_number_norm"] * math.exp(3 * float(t))
                          / obj.momentum.total_cell_number - 1) for t, d in zip(eta, q))
        diagnostics = {"Hamiltonian_max_relative": hres,
                       "radiation_number_max_abs": nres,
                       "massive_number_max_relative": mnumber,
                       "baryon_max_relative": float(np.max(abs(baryon / self.baryons_per_Href - 1))),
                       "min_scaled_atomic_state": float(np.min(x)),
                       "min_radiation_angular_sample": minangular,
                       "angular_positivity_scope": "1025 mu samples at each saved state; not a proof",
                       "max_abs_b": float(np.max(abs(y[1]))),
                       "max_thermal_energy_fraction": float(np.max(history["gas_thermal_to_gravitating_energy"])),
                       "max_omitted_trace_energy_H2_fraction": float(np.max(eps_trace)),
                       "max_frozen_state_H_shift_energy_only": float(np.max(history["frozen_state_H_shift_energy_only"])),
                       "max_200eV_baryon_energy_diagnostic": float(np.max(history["omitted_200eV_per_baryon_energy_ratio"])),
                       "electron_closure": "algebraic charge neutrality; no independent electron ODE"}
        if (hres > 3e-13 or nres > 2e-10 or mnumber > 3e-13
                or diagnostics["baryon_max_relative"] > 2e-9
                or diagnostics["min_scaled_atomic_state"] < -2e-10
                or minangular < -2e-10 or diagnostics["max_abs_b"] > 1):
            error = ArithmeticError("COUPLED_DIAGNOSTIC_GUARD: " + repr(diagnostics))
            error.partial_history = history
            error.diagnostics = diagnostics
            raise error
        return history, diagnostics
