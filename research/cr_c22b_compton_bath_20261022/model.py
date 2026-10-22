"""C22B Compton-feedback model over the immutable C22A atomic/kinetic model.

Full output has 75 states; the solver acts on the 72-dimensional declared
n=T0=T1=0 invariant face. These declared populations remain explicit in output.
Positive unsupported n/T input fails closed. No stored C22A state is repaired.
"""
from __future__ import annotations
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
import importlib.util
import math
from pathlib import Path
import sys
import numpy as np
from compton import gas_exchange_eV_per_H_s, constants_record, TCMB0_K, K_B_CGS, M_E_G, C_CGS

HERE = Path(__file__).resolve().parent
C22A = HERE.parent / "cr_c22a_thermochemical_20261022"
sys.path.insert(0, str(C22A))
_spec = importlib.util.spec_from_file_location("c22b_immutable_c22a_model", C22A / "model.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
K_B_EV_K = _base.K_B_EV_K


class ThermochemicalFactory:
    def __init__(self, ellmax=8):
        self.base_factory = _base.ThermochemicalFactory(ellmax=ellmax)

    def build(self, case):
        case = dict(case)
        base_case = {k: v for k, v in case.items() if k not in ("compton_enabled", "Tcmb0_K")}
        required = set(base_case.get("required_processes", _base.AVAILABLE_PROCESSES))
        permitted = _base.AVAILABLE_PROCESSES | {"prescribed_isotropic_Compton_bath"}
        if required - permitted:
            raise ValueError("ATOMIC_ENERGY_COVERAGE_MISSING:" + ",".join(sorted(required-permitted)))
        base_case["required_processes"] = sorted(required - {"prescribed_isotropic_Compton_bath"})
        base = self.base_factory.build(base_case)
        return ComptonBathModel(base, case)


class ComptonBathModel:
    def __init__(self, base, case):
        self.base, self.case = base, dict(case)
        for key in ("parent", "kinetic", "atomic", "nk", "ax", "gx", "iu", "iesc", "iwg",
                    "iwr", "irr", "iabs", "itau", "eta_end", "thresholds", "binding", "parameters",
                    "initial_photons", "initial_electrons", "initial_temperature", "photon_scale"):
            setattr(self, key, getattr(base, key))
        self.enabled = case.get("compton_enabled", True)
        if not isinstance(self.enabled, bool):
            raise ValueError("COMPTON_SWITCH_MUST_BE_BOOL")
        self.Tcmb0 = float(case.get("Tcmb0_K", TCMB0_K))
        if not math.isfinite(self.Tcmb0) or self.Tcmb0 <= 0:
            raise ValueError("INVALID_PRESCRIBED_CMB_T0")
        self.ibath, self.size = base.size, base.size + 1
        self.invariant_indices = np.array(sorted(self.ax.start+i
            for name in ("n", "T") for i in self.atomic.blocks[name]), dtype=int)
        self.active_indices = np.setdiff1d(np.arange(self.size), self.invariant_indices)
        self.solver_size = len(self.active_indices)
        self._y0 = np.r_[base.initial_state(), 0.0]
        self.project(self._y0)  # Explicit initial invariant-face admission.
        self.initial_energy = self.energy(0.0, self._y0)

    def initial_state(self):
        return self._y0.copy()

    def project(self, full):
        full = np.asarray(full)
        if full.shape[0] != self.size or not np.isfinite(full).all():
            raise ValueError("INVALID_FULL_STATE_FOR_INVARIANT_PROJECTION")
        if np.any(full[self.invariant_indices] != 0.0):
            raise ValueError("NONZERO_DECLARED_INVARIANT_INPUT_REJECTED")
        return full[self.active_indices].copy()

    def lift(self, active):
        active = np.asarray(active)
        if active.shape[0] != self.solver_size or not np.isfinite(active).all():
            raise ValueError("INVALID_ACTIVE_STATE_FOR_INVARIANT_LIFT")
        full = np.zeros((self.size,) + active.shape[1:], dtype=float)
        full[self.active_indices] = active
        return full

    def solver_rhs(self, eta, active):
        full = self.lift(active)
        derivative = self.rhs(eta, full)
        if np.any(derivative[self.invariant_indices] != 0.0):
            raise ArithmeticError("DECLARED_INVARIANT_RHS_NOT_ZERO")
        return derivative[self.active_indices]

    def fields(self, eta, full):
        return self.base.fields(eta, np.asarray(full)[:self.base.size])

    def temperature(self, full):
        return self.base.temperature(np.asarray(full)[:self.base.size])

    def photon_energies(self, eta):
        return self.base.photon_energies(eta)

    def transition_times(self):
        return self.base.transition_times()

    def compton(self, eta, full, fields=None):
        q = self.fields(eta, full) if fields is None else fields
        tg = self.Tcmb0 / q["a"]
        if not self.enabled:
            return 0.0, tg  # Preserve the parent RHS domain when the process is disabled.
        ne = self.atomic.electrons_per_H(full[self.ax])
        rate = gas_exchange_eV_per_H_s(q["temperature_K"], tg, ne)
        return rate, tg

    def rhs(self, eta, full):
        q = self.fields(eta, full)
        derivative = np.r_[self.base.rhs(eta, np.asarray(full)[:self.base.size]), 0.0]
        rate, _ = self.compton(eta, full, q)
        flux = rate / q["H"]
        derivative[self.iu] += flux
        derivative[self.ibath] = -flux
        return derivative

    def energy(self, eta, full):
        return self.base.energy(eta, np.asarray(full)[:self.base.size]) + float(full[self.ibath])

    def rhs_energy_residual(self, eta, full):
        dy = self.rhs(eta, full)
        return float(dy[self.iu] + self.binding @ (self.atomic.scales*dy[self.ax])
                     + self.photon_energies(eta) @ dy[self.gx]
                     - self.photon_energies(eta) @ full[self.gx]
                     + dy[self.iesc] + dy[self.iwg] + dy[self.iwr] + dy[self.ibath])

    def summarize(self, eta, full):
        eta, full = np.asarray(eta), np.asarray(full)
        self.project(full)  # No post hoc clipping or tolerated inactive leakage.
        h = self.base.summarize(eta, full[:self.base.size])
        h["Y"] = full
        bath = full[self.ibath]
        total = h["energy_total_eV_per_H"] + bath
        h.update(bath_energy_received_eV_per_H=bath,
                 energy_total_eV_per_H=total,
                 energy_residual_eV_per_H=total-self.initial_energy,
                 energy_relative_residual=(total-self.initial_energy)/max(abs(self.initial_energy),1e-30))
        transfer = [self.compton(t, y) for t, y in zip(eta, full.T)]
        h["Compton_gas_rate_eV_per_H_s"] = np.array([x[0] for x in transfer])
        h["prescribed_CMB_temperature_K"] = np.array([x[1] for x in transfer])
        h["Compton_gas_per_eta"] = h["Compton_gas_rate_eV_per_H_s"] / h["H"]
        h["Compton_nonrelativistic_parameter"] = K_B_CGS*np.maximum(
            h["temperature_K"], h["prescribed_CMB_temperature_K"])/(M_E_G*C_CGS**2)
        return h

    def metadata(self):
        data = self.base.metadata()
        data.update(schema="C22B_PRESCRIBED_COMPTON_BATH_V1", case=self.case,
                    state_size=self.size, solver_state_size=self.solver_size,
                    constants=constants_record(), Tcmb0_K=self.Tcmb0,
                    compton_enabled=self.enabled,
                    bath_ledger="signed cumulative energy received by external thermostat, not resident radiation",
                    Compton_closure="prescribed isotropic blackbody thermostat; self-consistent radiation spectrum OPEN",
                    no_extra_Einstein_radiation_density=True,
                    inherited_CMB_energy_backreaction="OPEN;elastic angular Thomson sector retained",
                    active_coordinate_indices=self.active_indices.tolist(),
                    invariant_coordinate_indices=self.invariant_indices.tolist(),
                    invariant_labels=[self.atomic.state_labels[i-self.ax.start] for i in self.invariant_indices],
                    invariant_policy="exact declared zero n/T face; nonzero inputs rejected; no clipping",
                    parent_C22A_source_identity="f5f0f30b1358d79a361045823ec68daeca72c10da3675e7882ccb5775c3053cd",
                    full_thermochemical_radiative_closure="OPEN", global_error_bound=None)
        data["available_processes"] = sorted(set(data["available_processes"]) | {"prescribed_isotropic_Compton_bath"})
        data["unmodeled_processes"] = [x for x in data["unmodeled_processes"] if x != "Compton_energy_exchange"]
        data["unmodeled_processes"].append("self_consistent_spectral_CMB_Compton_energy_feedback")
        return data
