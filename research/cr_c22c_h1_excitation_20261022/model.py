"""C22C finite CCC H1 n=2 excitation and immediate escaping-radiation closure.

The parent C22B is immutable. Two cumulative event coordinates extend its
75-state output to 77, with 74 active solver coordinates. The physical omitted
tail, continuum accuracy, other species/processes and radiation transport OPEN.
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
from excitation import CCCFiniteExcitation, DELTA_E_EV, ACTIVE_T_DOMAIN_K, PROCESS, constants_record

HERE = Path(__file__).resolve().parent
C22B = HERE.parent / "cr_c22b_compton_bath_20261022"
sys.path.insert(0, str(C22B))
_spec = importlib.util.spec_from_file_location("c22c_immutable_c22b_model", C22B / "model.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


class ThermochemicalFactory:
    def __init__(self, ellmax=8):
        self.base_factory = _base.ThermochemicalFactory(ellmax=ellmax)
        self.excitation = CCCFiniteExcitation()

    def build(self, case):
        case = dict(case)
        base_case = {k: v for k, v in case.items() if k != "h1_n2_excitation_enabled"}
        if "required_processes" in base_case:
            base_case["required_processes"] = sorted(set(base_case["required_processes"]) - {PROCESS})
        base = self.base_factory.build(base_case)
        return H1ExcitationModel(base, case, self.excitation)


class H1ExcitationModel(_base.ComptonBathModel):
    # Reuse only the checked projection/lift, fields, temperature and transition
    # interfaces; do not reinitialize a second Compton bath.
    def __init__(self, base, case, provider):
        self.base, self.case, self.provider = base, dict(case), provider
        for key in ("parent", "kinetic", "atomic", "nk", "ax", "gx", "iu", "iesc", "iwg",
                    "iwr", "irr", "iabs", "itau", "eta_end", "thresholds", "binding", "parameters",
                    "initial_photons", "initial_electrons", "initial_temperature", "photon_scale",
                    "ibath", "Tcmb0"):
            setattr(self, key, getattr(base, key))
        self.excitation_enabled = case.get("h1_n2_excitation_enabled", True)
        if not isinstance(self.excitation_enabled, bool):
            raise ValueError("EXCITATION_SWITCH_MUST_BE_BOOL")
        if PROCESS in case.get("required_processes", []) and not self.excitation_enabled:
            raise ValueError("REQUIRED_EXCITATION_PROCESS_DISABLED")
        self.ic2s, self.ic2p = base.size, base.size + 1
        self.size = base.size + 2
        self.invariant_indices = base.invariant_indices.copy()
        self.active_indices = np.setdiff1d(np.arange(self.size), self.invariant_indices)
        self.solver_size = len(self.active_indices)
        self.h1_ground = self.atomic.blocks["H1"][0]
        self._y0 = np.r_[base.initial_state(), 0., 0.]
        self.project(self._y0)
        self.initial_energy = self.energy(0., self._y0)

    def compton(self, eta, full, fields=None):
        return self.base.compton(eta, np.asarray(full)[:self.base.size], fields=fields)

    def excitation_events(self, eta, full, fields=None):
        if not self.excitation_enabled:
            return np.zeros(2)  # Keep parent domain; no source guard in OFF mode.
        q = self.fields(eta, full) if fields is None else fields
        t = q["temperature_K"]
        if not ACTIVE_T_DOMAIN_K[0] <= t <= ACTIVE_T_DOMAIN_K[1]:
            raise ValueError("C22C_ACTIVE_TEMPERATURE_SELECTOR")
        rates = self.provider.evaluate(t)["q_cm3_s"]
        h0 = self.atomic.physical_abundances(full[self.ax])[self.h1_ground]
        return q["n_e_cm3"] * h0 * rates / q["H"]

    def rhs(self, eta, full):
        q = self.fields(eta, full)
        derivative = np.r_[self.base.rhs(eta, np.asarray(full)[:self.base.size]), 0., 0.]
        events = self.excitation_events(eta, full, q)
        derivative[self.iu] -= DELTA_E_EV * float(np.sum(events))
        derivative[self.ic2s:self.ic2p + 1] = events
        return derivative

    def energy(self, eta, full):
        return (self.base.energy(eta, np.asarray(full)[:self.base.size])
                + DELTA_E_EV * float(full[self.ic2s] + full[self.ic2p]))

    def rhs_energy_residual(self, eta, full):
        dy = self.rhs(eta, full)
        return float(dy[self.iu] + self.binding @ (self.atomic.scales * dy[self.ax])
                     + self.photon_energies(eta) @ dy[self.gx]
                     - self.photon_energies(eta) @ full[self.gx]
                     + dy[self.iesc] + dy[self.iwg] + dy[self.iwr] + dy[self.ibath]
                     + DELTA_E_EV * (dy[self.ic2s] + dy[self.ic2p]))

    def summarize(self, eta, full):
        eta, full = np.asarray(eta), np.asarray(full)
        self.project(full)
        h = self.base.summarize(eta, full[:self.base.size])
        h["Y"] = full
        cs, cp = full[self.ic2s], full[self.ic2p]
        escaped = DELTA_E_EV * (cs + cp)
        total = h["energy_total_eV_per_H"] + escaped
        h.update(excitation_2s_events_per_H=cs, excitation_2p_events_per_H=cp,
                 excitation_escaped_energy_eV_per_H=escaped,
                 excitation_escaped_photon_count_per_H=2 * cs + cp,
                 energy_total_eV_per_H=total,
                 energy_residual_eV_per_H=total - self.initial_energy,
                 energy_relative_residual=(total - self.initial_energy) / max(abs(self.initial_energy), 1e-30))
        # These provider diagnostics describe the source at T even if disabled.
        values = [self.provider.evaluate(t) for t in h["temperature_K"]]
        h["H1_excitation_core_q_cm3_s"] = np.array([v["q_cm3_s"] for v in values]).T
        h["H1_excitation_core_log10_q_cm3_s"] = np.array([v["log10_q_cm3_s"] for v in values]).T
        h["H1_excitation_source_underflow"] = np.array([v["float64_underflow"] for v in values]).T
        h["H1_excitation_log10_tail_coefficient_per_assumed_a0sq"] = np.array([
            v["log10_conditional_tail_per_sigma_cap_a0sq"] for v in values])
        events = np.array([self.excitation_events(t, y) for t, y in zip(eta, full.T)]).T
        h["H1_excitation_events_per_H_per_eta"] = events
        h["H1_excitation_cooling_eV_per_H_per_eta"] = DELTA_E_EV * np.sum(events, axis=0)
        return h

    def metadata(self):
        data = self.base.metadata()
        data.update(schema="C22C_H1_N2_FINITE_CCC_EXCITATION_ESCAPE_V1", case=self.case,
                    state_size=self.size, solver_state_size=self.solver_size,
                    excitation_constants=constants_record(), excitation_enabled=self.excitation_enabled,
                    active_coordinate_indices=self.active_indices.tolist(),
                    excitation_event_indices={"2s": self.ic2s, "2p": self.ic2p},
                    excitation_rate="finite tabulated-energy PL contribution only; physical tail and continuum error OPEN",
                    activation_temperature_selector_K=list(ACTIVE_T_DOMAIN_K),
                    radiation_boundary="instantaneous ground return; perfect escape;2p1/2s2 outgoing photons; no absorption/spectrum model",
                    parent_C22B_source_identity="e4e5ce42693d473939e72ac3cd2ade32cd4a342993524df94ccf121eb6afbd52",
                    full_thermochemical_radiative_closure="OPEN", global_error_bound=None)
        data["available_processes"] = sorted(set(data["available_processes"]) | {PROCESS})
        data["unmodeled_processes"] += ["physical H1 excitation tail and interpolation accuracy",
            "H1 higher-n/D/T/He/Li excitation", "line trapping/reabsorption and2s mixing"]
        return data
