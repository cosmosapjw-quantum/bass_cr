"""Leite17/MD14 proton injection and exact constant Bianchi-I characteristics.

Source model CRP_L17_MD14_v1:
  Leite et al. 2017, arXiv:1703.09337v1, Eqs. (23)--(24);
  Madau & Dickinson 2014, arXiv:1403.0007v3, Eqs. (15)--(16).
The MD14 Salpeter k_CC=0.0068/Msun is used, not Leite's Larson-IMF 0.01.

All kinetic energies and pc are eV; volume/time units are proper m^3 and s.
The source is normalized over 10 keV--1 PeV, never over the collision window.
The finite experiment starts with zero CR population and holds MD14(z_snapshot)
and H,s fixed. It is collisionless transport of the injected population, not a
full cosmological history or a self-consistent stopping/cascade solution.
A later thin-target collision operator may consume the returned population.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np

MODEL_ID = "CRP_L17_MD14_v1"
LEITE_SOURCE = "https://arxiv.org/abs/1703.09337v1"
MD14_SOURCE = "https://arxiv.org/abs/1403.0007v3"
PROTON_REST_EV = 938272088.16  # CODATA 2018; matches selected Rudd adapter.
EV_J = 1.602176634e-19
MPC_M = 3.085677581491367e22
JULIAN_YEAR_S = 31557600.0
SOURCE_K_MIN_EV = 1.0e4
SOURCE_K_MAX_EV = 1.0e15
REFERENCE_K_EV = 1.0e9
DEFAULT_COLLISION_WINDOW_EV = (1.0e6, 4.0e6)


def _real(name, value, *, lower=None, upper=None, strict_lower=False):
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(name + ": finite real scalar required")
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(name + ": finite real scalar required") from exc
    if not math.isfinite(value):
        raise ValueError(name + ": finite real scalar required")
    if lower is not None and (value <= lower if strict_lower else value < lower):
        raise ValueError(name + ": below supported domain")
    if upper is not None and value > upper:
        raise ValueError(name + ": above supported domain")
    return value


def _order(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(name + ": integer quadrature order required")
    if not 2 <= value <= 512:
        raise ValueError(name + ": supported quadrature order is 2..512")
    return int(value)


def _positive_energy(energy):
    energy = np.asarray(energy, dtype=float)
    if np.any(~np.isfinite(energy)) or np.any(energy <= 0):
        raise ValueError("Finite strictly positive kinetic energies required")
    return energy


def md14_sfrd(z):
    """Eq15: Msun / (Julian yr comoving Mpc^3), explicit z<=8 fit-use gate."""
    z = _real("z", z, lower=0.0, upper=8.0)
    return 0.015 * (1.0 + z)**2.7 / (1.0 + ((1.0 + z)/2.9)**5.6)


def momentum_c_eV(kinetic_eV):
    k = _positive_energy(kinetic_eV)
    return np.sqrt(k) * np.sqrt(k + 2.0 * PROTON_REST_EV)


def kinetic_from_pc_eV(pc_eV):
    """Stable sqrt((pc)^2+m^2)-m without nonrelativistic cancellation."""
    pc = np.asarray(pc_eV, dtype=float)
    if np.any(~np.isfinite(pc)) or np.any(pc < 0):
        raise ValueError("Finite nonnegative pc required")
    return pc * (pc / (np.hypot(pc, PROTON_REST_EV) + PROTON_REST_EV))


def leite_shape(kinetic_eV, alpha=2.2):
    """Leite Eq23 shape: beta^-1 * [p(K)^2/p(K0)^2]^(-alpha/2)."""
    k = _positive_energy(kinetic_eV)
    alpha = _real("alpha", alpha, lower=0.0, strict_lower=True)
    pc = momentum_c_eV(k)
    pc0 = math.sqrt(REFERENCE_K_EV * (REFERENCE_K_EV + 2.0*PROTON_REST_EV))
    beta = pc / (k + PROTON_REST_EV)
    # log form avoids an unnecessary power of the 11-decade energy ratio.
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        shape = np.exp(-alpha * np.log(pc / pc0)) / beta
    if np.any(~np.isfinite(shape)) or np.any(shape <= 0):
        raise ValueError("Spectrum shape exceeds finite positive numerical domain")
    return shape


@lru_cache(maxsize=32)
def _legendre(order):
    order = _order("order", order)
    x, w = np.polynomial.legendre.leggauss(order)
    x.setflags(write=False)
    w.setflags(write=False)
    return x, w


def _log_nodes(lower, upper, order):
    """Smooth finite log-K quadrature, including dK in the weights."""
    if not upper > lower:
        return np.empty(0), np.empty(0)
    x, w = _legendre(order)
    lo, hi = math.log(lower), math.log(upper)
    half = (hi - lo)/2.0
    k = np.exp((hi+lo)/2.0 + half*x)
    return k, half*w*k


@lru_cache(maxsize=32)
def source_energy_shape_integral(alpha=2.2, order=128):
    """Integral K*shape(K)dK in eV^2 over the complete declared source."""
    alpha = _real("alpha", alpha, lower=0.0, strict_lower=True)
    order = _order("normalization_order", order)
    k, weights = _log_nodes(SOURCE_K_MIN_EV, SOURCE_K_MAX_EV, order)
    integral = float(np.dot(weights, k*leite_shape(k, alpha)))
    if not math.isfinite(integral) or integral <= 0:
        raise ValueError("Nonfinite/nonpositive full-spectrum normalization")
    return integral


@dataclass(frozen=True)
class InjectionModel:
    z_snapshot: float = 8.0
    alpha: float = 2.2
    supernova_energy_J: float = 1.0e44  # 1e51 erg.
    cr_efficiency: float = 0.1
    escape_fraction: float = 1.0  # A declared full-escape scenario.
    k_cc_per_solar_mass: float = 0.0068  # MD14 Salpeter convention.
    enabled: bool = True
    normalization_order: int = 128

    def __post_init__(self):
        _real("z_snapshot", self.z_snapshot, lower=0.0, upper=8.0)
        _real("alpha", self.alpha, lower=0.0, strict_lower=True)
        _real("supernova_energy_J", self.supernova_energy_J,
              lower=0.0, strict_lower=True)
        _real("cr_efficiency", self.cr_efficiency, lower=0.0, upper=1.0)
        _real("escape_fraction", self.escape_fraction, lower=0.0, upper=1.0)
        _real("k_cc_per_solar_mass", self.k_cc_per_solar_mass,
              lower=0.0, strict_lower=True)
        _order("normalization_order", self.normalization_order)
        if type(self.enabled) is not bool:
            raise ValueError("enabled must be a bool")

    def power_comoving_J_m3_s(self):
        if not self.enabled or self.cr_efficiency == 0 or self.escape_fraction == 0:
            return 0.0
        power = (self.supernova_energy_J * self.cr_efficiency * self.escape_fraction
                * self.k_cc_per_solar_mass * md14_sfrd(self.z_snapshot)
                / JULIAN_YEAR_S / MPC_M**3)
        if not math.isfinite(power) or power <= 0:
            raise ValueError("Injected power exceeds finite positive numerical domain")
        return power

    def power_proper_J_m3_s(self):
        """a^-3 conversion, with a0=1 and a=1/(1+z_snapshot)."""
        power = self.power_comoving_J_m3_s() * (1.0+self.z_snapshot)**3
        if not math.isfinite(power):
            raise ValueError("Proper power exceeds finite numerical domain")
        return power

    def normalization_m3_s_eV(self):
        power = self.power_proper_J_m3_s()
        if power == 0:
            return 0.0
        return power / (EV_J * source_energy_shape_integral(
            self.alpha, self.normalization_order))

    def q_proper_m3_s_eV(self, kinetic_eV):
        """Angle-integrated dN/(proper m^3 s dK); isotropic dmu/2 separately."""
        k = _positive_energy(kinetic_eV)
        normalization = self.normalization_m3_s_eV()
        if normalization == 0:
            return np.zeros_like(k)
        inside = (k >= SOURCE_K_MIN_EV) & (k <= SOURCE_K_MAX_EV)
        # No extrapolated source beyond the explicit source cutoffs.
        out = np.zeros_like(k)
        out[inside] = normalization * leite_shape(k[inside], self.alpha)
        return out

    def metadata(self):
        return {
            "model_id": MODEL_ID, "source_urls": [LEITE_SOURCE, MD14_SOURCE],
            "z_snapshot": self.z_snapshot, "alpha": self.alpha,
            "source_window_eV": [SOURCE_K_MIN_EV, SOURCE_K_MAX_EV],
            "reference_K_eV": REFERENCE_K_EV,
            "sfrd_Msun_yr_comoving_Mpc3": md14_sfrd(self.z_snapshot),
            "k_CC_Msun_inverse": self.k_cc_per_solar_mass,
            "supernova_energy_J": self.supernova_energy_J,
            "cr_efficiency": self.cr_efficiency,
            "escape_fraction_scenario": self.escape_fraction,
            "power_comoving_J_m3_s": self.power_comoving_J_m3_s(),
            "power_proper_J_m3_s": self.power_proper_J_m3_s(),
            "comoving_to_proper_factor": (1.0+self.z_snapshot)**3,
            "source_held_fixed_during_local_window": True,
            "initial_CR_population": "zero; controlled turn-on",
            "angular_measure": "isotropic birth dmu/2; phi integrated",
            "normalization": "full source spectrum; no active-window renormalization",
        }


def characteristic(kinetic_birth_eV, mu_birth, age_s, H_s, shear_s):
    """Exact local non-tilted axisymmetric Bianchi I collisionless momentum.

    H_perp=H-s, H_parallel=H+2s. s is a shear rate, NOT a shear scalar.
    p_perp and p_parallel below are stored multiplied by c, in eV.
    """
    k = _positive_energy(kinetic_birth_eV)
    mu = np.asarray(mu_birth, dtype=float)
    age = np.asarray(age_s, dtype=float)
    H = _real("H_s", H_s)
    s = _real("shear_s", shear_s)
    if np.any(~np.isfinite(mu)) or np.any(np.abs(mu) > 1):
        raise ValueError("Finite mu_birth in [-1,1] required")
    if np.any(~np.isfinite(age)) or np.any(age < 0):
        raise ValueError("Finite nonnegative age required")
    # Numerical scope guard, not a claim that contraction is impossible.
    if np.any(np.abs((H-s)*age) > 50) or np.any(np.abs((H+2*s)*age) > 50):
        raise ValueError("Constant-background characteristic exceeds bounded exponent scope")
    p0 = momentum_c_eV(k)
    pp = p0 * np.sqrt((1.0-mu)*(1.0+mu)) * np.exp(-(H-s)*age)
    pz = p0 * mu * np.exp(-(H+2*s)*age)
    pc = np.hypot(pp, pz)
    return {"kinetic_eV": kinetic_from_pc_eV(pc),
            "mu": pz/pc, "pc_eV": pc,
            "pc_perp_eV": pp, "pc_parallel_eV": pz}


def _empty_population(metadata, dt, H, s, window):
    node_keys = ["kinetic_eV", "birth_kinetic_eV", "mu", "birth_mu",
                 "age_s", "birth_time_s", "number_density_m3"]
    return {
        "source": metadata,
        "background": {"H_s": H, "shear_s": s, "H_perp_s": H-s,
                       "H_parallel_s": H+2*s, "dt_s": dt},
        "collision_window_eV": list(window),
        "nodes": {key: np.empty(0) for key in node_keys},
        "budgets": dict.fromkeys([
            "raw_birth_injected_energy_J_m3", "dilution_weighted_birth_energy_J_m3",
            "final_CR_energy_J_m3", "active_CR_energy_J_m3",
            "below_collision_window_energy_J_m3", "above_collision_window_energy_J_m3",
            "outside_collision_window_energy_J_m3", "adiabatic_work_J_m3",
            "final_CR_number_m3", "active_CR_number_m3",
            "source_tail_birth_energy_J_m3"], 0.0),
        "transport": "exact collisionless characteristics; bounded quadrature",
        "collision_feedback": "not applied; caller must establish thin-target regime",
        "unresolved_tail_policy": "retain as CR energy; never convert to heat",
        "rates_semantics": "nodes represent instantaneous end-of-window population",
    }


def transport_population(model, dt_s, H_s, shear_s,
                         collision_window_eV=DEFAULT_COLLISION_WINDOW_EV,
                         age_order=12, mu_order=12, energy_order=48):
    """Return source-weighted end-of-window population in a collision domain.

    Integrate birth ages and birth mu, then split the BIRTH kinetic-energy
    integral at the exact inverse images of the FINAL collision-band edges.
    Thus no discontinuous top-hat mask is sampled by quadrature. The two
    outside intervals are included in the full population/energy budgets.

    Final number weight = exp(-3H age) q(K0) dK0 dage dmu0/2.
    No additional energy/angular Jacobian is needed in these birth coordinates.
    """
    if not isinstance(model, InjectionModel):
        raise TypeError("InjectionModel required")
    dt = _real("dt_s", dt_s, lower=0.0)
    H = _real("H_s", H_s)
    s = _real("shear_s", shear_s)
    if len(collision_window_eV) != 2:
        raise ValueError("Two collision-window endpoints required")
    low, high = [_real("collision energy", v, lower=0.0, strict_lower=True)
                 for v in collision_window_eV]
    if high <= low:
        raise ValueError("Strictly ordered collision window required")
    age_order = _order("age_order", age_order)
    mu_order = _order("mu_order", mu_order)
    energy_order = _order("energy_order", energy_order)
    if max(abs((H-s)*dt), abs((H+2*s)*dt), abs(3*H*dt)) > 50:
        raise ValueError("Interval exceeds bounded exponent scope")
    result = _empty_population(model.metadata(), dt, H, s, (low, high))
    power = model.power_proper_J_m3_s()
    if dt == 0 or power == 0:
        return result
    xa, wa = _legendre(age_order)
    mus, wm = _legendre(mu_order)
    ages = 0.5*dt*(xa+1.0)
    age_weights = 0.5*dt*wa
    pc_limits = momentum_c_eV(np.array([low, high]))
    chunks = {key: [] for key in result["nodes"]}
    totals = np.zeros((3, 3))  # below, active, above: number, birth E, final E
    for age, time_weight in zip(ages, age_weights):
        dilution = math.exp(-3.0*H*age)
        for mu, angular_weight in zip(mus, 0.5*wm):
            g = math.hypot(math.sqrt((1-mu)*(1+mu))*math.exp(-(H-s)*age),
                           mu*math.exp(-(H+2*s)*age))
            inverse_edges = kinetic_from_pc_eV(pc_limits/g)
            cut_low, cut_high = np.clip(inverse_edges, SOURCE_K_MIN_EV, SOURCE_K_MAX_EV)
            edges = (SOURCE_K_MIN_EV, cut_low, cut_high, SOURCE_K_MAX_EV)
            measure = time_weight * angular_weight * dilution
            for region, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
                k0, dk = _log_nodes(left, right, energy_order)
                if not len(k0):
                    continue
                weight = measure * dk * model.q_proper_m3_s_eV(k0)
                propagated = characteristic(k0, mu, age, H, s)
                kf = propagated["kinetic_eV"]
                totals[region] += [np.sum(weight), np.dot(weight,k0)*EV_J,
                                   np.dot(weight,kf)*EV_J]
                if region == 1:
                    values = {
                        "kinetic_eV": kf, "birth_kinetic_eV": k0,
                        "mu": np.broadcast_to(propagated["mu"], k0.shape),
                        "birth_mu": np.full_like(k0, mu),
                        "age_s": np.full_like(k0, age),
                        "birth_time_s": np.full_like(k0, dt-age),
                        "number_density_m3": weight,
                    }
                    for key, value in values.items():
                        chunks[key].append(value)
    result["nodes"] = {key: np.concatenate(parts) if parts else np.empty(0)
                       for key, parts in chunks.items()}
    weighted_birth = float(np.sum(totals[:, 1]))
    final_energy = float(np.sum(totals[:, 2]))
    tail_energy = float(totals[0, 2]+totals[2, 2])
    result["budgets"] = {
        "raw_birth_injected_energy_J_m3": power*dt,
        "dilution_weighted_birth_energy_J_m3": weighted_birth,
        "final_CR_energy_J_m3": final_energy,
        "active_CR_energy_J_m3": float(totals[1, 2]),
        "below_collision_window_energy_J_m3": float(totals[0, 2]),
        "above_collision_window_energy_J_m3": float(totals[2, 2]),
        "outside_collision_window_energy_J_m3": tail_energy,
        "adiabatic_work_J_m3": weighted_birth-final_energy,
        "final_CR_number_m3": float(np.sum(totals[:, 0])),
        "active_CR_number_m3": float(totals[1, 0]),
        "source_tail_birth_energy_J_m3": float(totals[0, 1]+totals[2, 1]),
    }
    result["quadrature_orders"] = {"age": age_order, "birth_mu": mu_order,
                                    "energy_per_smooth_region": energy_order,
                                    "source_normalization": model.normalization_order}
    result["budget_semantics"] = {
        "raw_birth": "sum of local proper injection energy over dt, before dilution",
        "weighted_birth": "birth energy weighted to final proper-volume measure",
        "adiabatic_work": "weighted birth minus final kinetic; signed under contraction",
        "source_tail_birth": "birth energy of particles outside collision band at final time",
        "not_deposition": "all budgets are CR kinetic storage/work, not gas heating",
    }
    return result

