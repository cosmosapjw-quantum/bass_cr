"""Conditional primordial 21-state photoionization / Case-A RR network.

This is a new, reduced kinetic closure, not the old collisionless calculation
and not a complete primordial reaction network.  The six photon cohorts and
T(z) are prescribed external scenarios, not a measured UV background or a
self-consistent thermal/radiative-transfer solution.  Each electronic isotope
equality approximation requires an explicit constructor opt-in.

Coordinates: x_i = (n_i / n_H_ref) / scales_i, eta = ln(a/a_initial).
``H`` is in s^-1; ``nH_ref`` is the proper reference density in cm^-3 at z.
The electron is algebraic, not a 22nd evolved state.  No abundance clipping or
renormalization is used; finite signed Newton trial states are permitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import struct
from types import MappingProxyType

import numpy as np


BASE = Path(__file__).resolve().parent
VENDOR = BASE / "vendor" / "atomic"
EV_J = 1.602176634e-19
CHANNELS = (
    {"Z": 1, "N": 1, "ion": "HI", "shell": 1, "chi_eV": 13.6, "saha_d": 1},
    {"Z": 2, "N": 2, "ion": "HeI", "shell": 1, "chi_eV": 24.59, "saha_d": 4},
    {"Z": 2, "N": 1, "ion": "HeII", "shell": 1, "chi_eV": 54.42, "saha_d": 1},
    {"Z": 3, "N": 3, "ion": "LiI", "shell": 2, "chi_eV": 5.392, "saha_d": 1},
    {"Z": 3, "N": 2, "ion": "LiII", "shell": 1, "chi_eV": 75.64, "saha_d": 4},
    {"Z": 3, "N": 1, "ion": "LiIII", "shell": 1, "chi_eV": 122.5, "saha_d": 1},
)
CHANNEL_NAMES = tuple(c["ion"] for c in CHANNELS)
ISOTOPES = (
    ("n", 1, 0, 0.0, 1.0),
    ("H1", 1, 1, 1.0, 1.0),
    ("D", 2, 1, 2.5e-5, 2.5e-5),
    ("T", 3, 1, 0.0, 1e-20),
    ("He3", 3, 2, 1e-5, 1e-5),
    ("He4", 4, 2, 0.082, 0.082),
    ("Li7", 7, 3, 5e-10, 5e-10),
    ("Li6", 6, 3, 1e-14, 1e-14),
)
SOURCE_FILES = {
    "r9_li_thermal_rates.py": "74b2a8c30c62f4a50e7c5c4bcf92cb159549ffcb904a3e423a793169c2f2bb27",
    "phfit2.f": "8df982535a4a2b952e33ca2ffb6d81600e156d7373fbf547a0c0170c1cecc296",
    "photo_table.dat": "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389",
    "partial_table.dat": "fd0a315f100a78f8edb6b3fb12c0022246309cbc834394cbd0e8e5305d00b393",
    "rrfit.f": "81ff692a44622665d4d216e8f66445bfaa6699701f80ec9c02c80ebe8fd42cf9",
    "rr_table.dat": "2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091",
    "rr_description.txt": "fa24b34f734f8d346163df77f6c277af848b799daa693387251c892f86c14ca4",
}


def _frozen(values):
    """FP64 array with immutable bytes backing, including through its base."""
    a = np.asarray(values, dtype=np.float64)
    return np.frombuffer(a.tobytes(order="C"), dtype=np.float64).reshape(a.shape)


def _load_provider():
    for name, expected in SOURCE_FILES.items():
        actual = hashlib.sha256((VENDOR / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Atomic source identity mismatch: {name}")
    spec = importlib.util.spec_from_file_location("c21o_r9_atomic_provider", VENDOR / "r9_li_thermal_rates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = {key: VENDOR / value for key, value in {
        "phfit2": "phfit2.f", "photo_table": "photo_table.dat",
        "partial_table": "partial_table.dat", "rrfit": "rrfit.f",
        "rr_table": "rr_table.dat",
    }.items()}
    return module.Provider(paths, CHANNELS)


@dataclass(frozen=True)
class RateData:
    temperature_K: float
    photo_rates_s: np.ndarray
    rr_cm3_s: np.ndarray
    diagnostic: dict

    @property
    def diagnostics(self):
        return self.diagnostic


class AtomicNetwork21:
    """Exact evaluation of the frozen fits, with no rate interpolation.

    Included: adjacent ground-state valence photoionization and all-level
    spontaneous RR (Case A: recombination photons escape this closure).
    Unmodeled: collisional ionization, dielectronic recombination, charge
    exchange, molecules, nuclear collisions, Li I core/Auger ionization,
    multilevel atoms, and radiation/temperature backreaction.
    """

    channel_names = CHANNEL_NAMES
    z_domain = (2.0, 20.0)
    rr_temperature_domain_K = (3.0, 1e9)
    electronic_isotope_approximations = (
        "H1,D,T use the same H electronic thresholds and rate fits",
        "He3,He4 use the same He electronic thresholds and rate fits",
        "Li6,Li7 use the same Li electronic thresholds and rate fits",
        "No reduced-mass isotope shifts or isotope-resolved electronic rates",
    )
    unmodeled_channels = (
        "collisional_ionization", "dielectronic_recombination", "charge_exchange",
        "molecular_reactions", "nuclear_collision_reactions", "LiI_core_Auger",
        "secondary_electron_ionization", "multilevel_atoms", "photon_transport",
    )

    _locked_configuration = frozenset({
        "provider", "state_labels", "scales", "A", "q", "blocks",
        "initial_nucleus_totals", "energies_eV", "soft_weights", "hard_weights",
        "sigma_cm2", "soft_flux_normalization", "hard_flux_normalization",
        "edges", "_photo_basis", "_rr_basis", "_beta", "beta_rates_s",
        "beta_status", "beta_edges", "_rr_identity", "z_domain",
        "rr_temperature_domain_K", "channel_names",
    })

    def __setattr__(self, name, value):
        if getattr(self, "_configuration_frozen", False) and name in self._locked_configuration:
            raise AttributeError(f"Immutable network configuration: {name}")
        object.__setattr__(self, name, value)

    def __init__(self, *, electronic_isotope_equality=False):
        if electronic_isotope_equality is not True:
            raise ValueError("Explicit electronic_isotope_equality=True is required for this conditional model")
        self.provider = _load_provider()
        labels, scale, masses, charge, blocks, total = [], [], [], [], {}, {}
        for name, a, z, abundance, normalization in ISOTOPES:
            start = len(labels)
            for q in range(z + 1):
                labels.append("n" if name == "n" else f"{name}_{q}")
                scale.append(normalization)
                masses.append(a)
                charge.append(q)
            blocks[name] = tuple(range(start, len(labels)))
            total[name] = abundance
        self.state_labels = tuple(labels)
        self.scales, self.A, self.q = map(_frozen, (scale, masses, charge))
        self.blocks, self.initial_nucleus_totals = MappingProxyType(blocks), MappingProxyType(total)
        self.energies_eV = _frozen([10., 20., 40., 60., 100., 150.])
        # These are incident number-flux cohorts, integrated over direction:
        # F_i = c n_gamma,i [photons cm^-2 s^-1], Gamma = sum_i F_i sigma_i.
        self.soft_weights = _frozen([1., 1., 0.3, 0.05, 0., 0.])
        self.hard_weights = _frozen([0., 0., 0., 0.1, 0.5, 1.])
        self.sigma_cm2 = _frozen([
            self.provider.sigma(name, self.energies_eV) * 1e-18
            for name in CHANNEL_NAMES
        ])
        # For non-LiI channels the PH2 author table covers threshold..50 keV.
        # LiI has PH2 below64.39eV and the original PH1 2s partial above it.
        # A below-threshold zero is physical support, not an unavailable rate.
        if np.any(self.energies_eV <= 0) or np.any(self.energies_eV > 5e4):
            raise ValueError("Photon cohort outside the adopted photo-fit domain")
        if not np.all(np.isfinite(self.sigma_cm2)) or np.any(self.sigma_cm2 < 0):
            raise ValueError("Invalid primary cross-section values")
        self.soft_flux_normalization = 1e-13 / float(self.sigma_cm2[0] @ self.soft_weights)
        self.hard_flux_normalization = 2e-14 / float(self.sigma_cm2[0] @ self.hard_weights)
        # Each edge has a source/destination state and a shared electronic row.
        edges = []
        for name in ("H1", "D", "T", "He3", "He4", "Li7", "Li6"):
            block = self.blocks[name]
            offset = 0 if len(block) == 2 else 1 if len(block) == 3 else 3
            edges.extend((block[j], block[j + 1], offset + j) for j in range(len(block) - 1))
        self.edges = tuple(edges)
        p, r = np.zeros((6, 21, 21)), np.zeros((6, 21, 21))
        for lower, upper, channel in self.edges:
            p[channel, lower, lower] -= 1.
            p[channel, upper, lower] += 1.
            r[channel, upper, upper] -= 1.
            r[channel, lower, upper] += 1.
        self._photo_basis, self._rr_basis = _frozen(p), _frozen(r)
        # Historical sourced constants, not a claim about current world averages.
        # UCNtau2021: neutron mean lifetime877.75s (NOT a half-life).
        # Fuller/Smith2010: tritium half-life12.33yr; Julian year365.25d.
        # Electronic charge-independent beta rates and the q->q+1 mapping are
        # additional conditional approximations; neutrino/decay heating is not
        # supplied to the prescribed temperature. Both parents start at zero.
        self.beta_rates_s = {
            "n_to_H1_1": 1. / 877.75,
            "T_to_He3_q_plus_1": math.log(2.) / (12.33 * 31557600.),
        }
        self.beta_status = {
            "n_to_H1_1": "SOURCED_HISTORICAL_MEAN_LIFETIME;zero_initial_parent",
            "T_to_He3_q_plus_1": "SOURCED_HISTORICAL_HALF_LIFE;charge_independent_approximation;zero_initial_parent",
        }
        beta = np.zeros((21, 21))
        self.beta_edges = (
            (self.blocks["n"][0], self.blocks["H1"][1], self.beta_rates_s["n_to_H1_1"]),
            (self.blocks["T"][0], self.blocks["He3"][1], self.beta_rates_s["T_to_He3_q_plus_1"]),
            (self.blocks["T"][1], self.blocks["He3"][2], self.beta_rates_s["T_to_He3_q_plus_1"]),
        )
        for source, daughter, rate in self.beta_edges:
            beta[source, source] -= rate
            beta[daughter, source] += rate
        self._beta = _frozen(beta)
        self.beta_rates_s = MappingProxyType(self.beta_rates_s)
        self.beta_status = MappingProxyType(self.beta_status)
        # The reused provider's code remains byte-identical; freezing its parsed
        # coefficient metadata does not change any evaluation or reduction.
        self.provider.rows = MappingProxyType({
            name: MappingProxyType({k: tuple(v) if isinstance(v, list) else v for k, v in row.items()})
            for name, row in self.provider.rows.items()
        })
        self.provider.core = tuple(self.provider.core)
        self._rr_identity = tuple(tuple(self.provider.rows[name]["RR"]) for name in CHANNEL_NAMES)
        self._last_z_key, self._last_rates, self._last_operators = None, None, None
        self._configuration_frozen = True

    def initial_state(self):
        x = np.zeros(21, dtype=np.float64)
        for name, abundance in self.initial_nucleus_totals.items():
            block = self.blocks[name]
            if abundance == 0:
                continue
            if name in ("H1", "D"):
                x[block[0]], x[block[1]] = 1. - 2e-4, 2e-4
            elif name.startswith("Li"):
                x[block[1]] = 1.  # Declared LiII IC, not an imported late history.
            else:
                x[block[0]] = 1.
        return x

    def _state(self, x):
        a = np.asarray(x)
        if a.shape != (21,) or not np.all(np.isfinite(a)):
            raise ValueError("Expected a finite 21-component scaled state")
        return a

    def physical_abundances(self, x):
        """Fresh n_i/n_H_ref array, retaining trace-isotope normalization."""
        return self.scales * self._state(x)

    def electrons_per_H(self, x):
        """Algebraic charge-neutral free electrons per reference H nucleus."""
        return self.q @ self.physical_abundances(x)

    def _evaluate_rates(self, z):
        z = float(z)
        if not math.isfinite(z) or not 2.0 <= z <= 20.0:
            raise ValueError("This declared UV/temperature scenario is defined only for 2 <= z <= 20")
        soft = 0.5 * (1. + math.tanh((8. - z) / 1.))
        hard = 0.5 * (1. + math.tanh((3.2 - z) / 0.35))
        temperature = 8. * ((1. + z) / 21.) ** 2 + 1e4 * soft + 5e3 * hard
        # The actual scenario stays above3K. No floor or rate extrapolation.
        if not self.rr_temperature_domain_K[0] < temperature < self.rr_temperature_domain_K[1]:
            raise ValueError("Prescribed temperature lies outside the primary total-RR fit domain")
        flux = self.soft_flux_normalization * soft * self.soft_weights + self.hard_flux_normalization * hard * self.hard_weights
        photo = self.sigma_cm2 @ flux
        rr = np.asarray([self.provider.rr(name, temperature) for name in CHANNEL_NAMES], dtype=float)
        if not np.all(np.isfinite(photo)) or not np.all(np.isfinite(rr)) or np.any(photo < 0) or np.any(rr <= 0):
            raise ValueError("Nonfinite or nonphysical atomic coefficients")
        thresholds = np.asarray([c["chi_eV"] for c in CHANNELS])
        absorption = (self.sigma_cm2 * self.energies_eV) @ flux * EV_J
        threshold_power = thresholds * photo * EV_J
        # sigma below threshold is identically zero, so no negative deposited
        # energy is introduced by the signed (E-chi) factor at those nodes.
        heating = (self.sigma_cm2 * (self.energies_eV[None, :] - thresholds[:, None])) @ flux * EV_J
        diagnostic = MappingProxyType({
            "scenario": "prescribed_optically_thin_cohorts_v1_not_observational_UVB",
            "soft_on": soft, "hard_on": hard,
            "cohort_flux_cm2_s": _frozen(flux),
            "absorbed_energy_J_per_target_s": _frozen(absorption),
            "ionization_threshold_J_per_target_s": _frozen(threshold_power),
            "primary_photoelectron_J_per_target_s": _frozen(heating),
            "energy_partition_residual_J_per_target_s": _frozen(absorption - threshold_power - heating),
            "LiI_photo_scope": "2s_valence_only;1s_core_and_Auger_UNMODELED",
            "HeI_RR_row": "HeI b; original rrfit selection",
            "rate_interpolation": "NONE; exact fit evaluation at current prescribed T(z)",
            "temperature_floor_applied": False,
        })
        return RateData(temperature, _frozen(photo), _frozen(rr), diagnostic)

    def _cache_guard(self):
        # Protect the source identity even if somebody replaces the original
        # provider's rows attribute after construction. No stale cached rates.
        rr = tuple(tuple(self.provider.rows[name]["RR"]) for name in CHANNEL_NAMES)
        if rr != self._rr_identity:
            raise ValueError("Atomic RR coefficient metadata changed after construction")

    def rate_data(self, z):
        """One exact-binary64-z cache entry; no interpolation or tolerance key."""
        z = float(z)
        self._cache_guard()
        if not math.isfinite(z) or not 2.0 <= z <= 20.0:
            raise ValueError("This declared UV/temperature scenario is defined only for 2 <= z <= 20")
        key = struct.pack("!d", z)
        if key != self._last_z_key:
            data = self._evaluate_rates(z)
            self._last_z_key, self._last_rates, self._last_operators = key, data, None
        return self._last_rates

    def _evaluate_operators(self, data):
        p = np.tensordot(data.photo_rates_s, self._photo_basis, axes=(0, 0))
        r = np.tensordot(data.rr_cm3_s, self._rr_basis, axes=(0, 0))
        return _frozen(p), _frozen(r)

    def _operators(self, z):
        data = self.rate_data(z)
        if self._last_operators is None:
            self._last_operators = self._evaluate_operators(data)
        return self._last_operators

    @staticmethod
    def _density_inputs(H, nH_ref):
        H, nH_ref = float(H), float(nH_ref)
        if not math.isfinite(H) or H <= 0 or not math.isfinite(nH_ref) or nH_ref <= 0:
            raise ValueError("H[s^-1] and proper nH_ref[cm^-3] must be positive finite")
        return H, nH_ref

    def rhs(self, z, x, H, nH_ref):
        """Return a fresh dx/deta; finite Newton trial states are not clipped."""
        H, nH_ref = self._density_inputs(H, nH_ref)
        y = self.physical_abundances(x)
        p, r = self._operators(z)
        ne = nH_ref * (self.q @ y)
        return ((p + self._beta) @ y + ne * (r @ y)) / self.scales / H

    def jacobian(self, z, x, H, nH_ref):
        """Exact derivative of rhs with respect to all21 scaled populations.

        The rank-one term includes the electron-density response to every ion;
        H, proper reference density and prescribed T/UV history are held fixed.
        """
        H, nH_ref = self._density_inputs(H, nH_ref)
        y = self.physical_abundances(x)
        p, r = self._operators(z)
        jy = p + self._beta + nH_ref * ((self.q @ y) * r + np.outer(r @ y, self.q))
        return (jy * self.scales[None, :]) / self.scales[:, None] / H

    def frozen_electron_generator(self, z, x, H, nH_ref):
        """Linear physical-Y generator at a frozen, algebraic electron density.

        Column sums vanish. Off-diagonal entries are nonnegative for physical
        x>=0; this is not the nonlinear Jacobian and is not a production solver.
        """
        H, nH_ref = self._density_inputs(H, nH_ref)
        y = self.physical_abundances(x)
        p, r = self._operators(z)
        return (p + self._beta + nH_ref * (self.q @ y) * r) / H

    def energy_diagnostics(self, z, x, nH_ref):
        """External-photo absorption/heating budgets, not a solved heat equation.

        Per-H-reference powers are J/s per reference nucleus. Volume powers
        are J/cm^3/s. No secondary-ionization or recombination-cooling model
        is silently added to the prescribed temperature history.
        """
        nH_ref = float(nH_ref)
        if not math.isfinite(nH_ref) or nH_ref <= 0:
            raise ValueError("proper nH_ref must be positive and finite")
        data, y = self.rate_data(z), self.physical_abundances(x)
        targets = np.zeros(6, dtype=y.dtype)
        for lower, _, channel in self.edges:
            targets[channel] += y[lower]
        result = {}
        for key in ("absorbed_energy", "ionization_threshold", "primary_photoelectron"):
            power = targets @ data.diagnostic[f"{key}_J_per_target_s"]
            result[f"{key}_J_per_H_ref_s"] = float(power)
            result[f"{key}_J_cm3_s"] = float(power * nH_ref)
        result["budget_scope"] = "external_photo_injection_only;T_prescribed;RR_cooling_UNMODELED"
        return result

    def model_metadata(self):
        """JSON-ready scientific closure and source identity for run manifests."""
        return {
            "model": "C21O_conditional_photo_RR_21_v1",
            "state_labels": list(self.state_labels), "scales": self.scales.tolist(),
            "A": self.A.tolist(), "q": self.q.tolist(),
            "initial_nucleus_totals_per_H_ref": dict(self.initial_nucleus_totals),
            "initial_H1_D_ionized_fraction": 2e-4,
            "initial_He": "neutral", "initial_Li": "LiII;declared_illustrative_IC",
            "initial_abundances_scope": "illustrative_prior;not_a_BBN_prediction",
            "electronic_isotope_equality": True,
            "electronic_isotope_approximations": list(self.electronic_isotope_approximations),
            "unmodeled_channels": list(self.unmodeled_channels),
            "beta_status": dict(self.beta_status),
            "beta_rates_s": dict(self.beta_rates_s),
            "beta_lifetimes": {
                "neutron_mean_lifetime_s": 877.75,
                "neutron_source": "https://arxiv.org/abs/2106.10375v2",
                "tritium_half_life_Julian_years": 12.33,
                "tritium_source": "https://arxiv.org/abs/1009.0277",
                "status": "selected_historical_constants_not_current_world_average",
                "decay_energy_closure": "UNMODELED;zero_initial_parents_for_this_scenario",
            },
            "photon_energies_eV": self.energies_eV.tolist(),
            "soft_weights": self.soft_weights.tolist(), "hard_weights": self.hard_weights.tolist(),
            "soft_flux_normalization_cm2_s": self.soft_flux_normalization,
            "hard_flux_normalization_cm2_s": self.hard_flux_normalization,
            "full_soft_HI_Gamma_s_inverse": 1e-13,
            "full_hard_HI_Gamma_s_inverse": 2e-14,
            "temperature_formula": "8*((1+z)/21)^2 + 1e4*soft(z) + 5e3*hard(z) K; no floor",
            "soft_on_formula": "(1+tanh((8-z)/1))/2",
            "hard_on_formula": "(1+tanh((3.2-z)/0.35))/2",
            "UV_temperature_domain_z": list(self.z_domain),
            "RR_domain_K": list(self.rr_temperature_domain_K),
            "photo_LiI_scope": "ground_2s_valence;1s_core_Auger_unmodeled",
            "RR_closure": "all_level_spontaneous_Case_A_escape;HeI_b_row",
            "electron_closure": "ne_cm^-3=nH_ref_cm^-3*sum_i(q_i*scales_i*x_i)",
            "rhs_coordinate": "eta=ln(a/a_initial);dx/deta=dx/dt/H",
            "nH_ref_argument": "proper instantaneous cm^-3;not present-day comoving density",
            "rate_interpolation": False,
            "rate_cache": "bounded1entry;exact_binary64_z;immutable_T_UV_cohorts;guarded_RR_coefficients;no_x_or_ne_cache",
            "source_sha256": dict(SOURCE_FILES),
            "global_error_bound": None,
        }


if __name__ == "__main__":
    network = AtomicNetwork21(electronic_isotope_equality=True)
    print(json.dumps(network.model_metadata(), indent=2))
