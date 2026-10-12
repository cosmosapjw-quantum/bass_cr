# SPDX-License-Identifier: GPL-3.0-only
"""CR-PHYS02A: a causal, conditional direct-electron stopping component.

The inherited proton source is normalized over 10 keV--1 PeV. Only impacts
of 1--4 MeV protons and their directly ejected 0.1--10 eV electrons are used
here. This module does not complete FS10's secondary cascade or update REI.

Gas is prescribed. Electron stopping uses a classical superthermal,
leading-log Coulomb closure; its physical error is not certified. Residual
energy at the 0.1 eV boundary is retained, never silently deposited as heat.
The time-dependent source is Q_e(W,t)=t*A(W), the leading H*t local limit
of the inherited initially empty proton population.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib
import importlib.util
import json
import math

import numpy as np
from scipy.constants import e as EV_J, epsilon_0, m_e, k as K_B, hbar
from scipy.optimize import brentq
from scipy.special import expi

ROOT = Path(__file__).resolve().parents[1]
YEAR_S = 31557600.0
KAPPA = EV_J**2 / (4.0 * math.pi * epsilon_0)
E_MIN = 0.1
E_MAX = 10.0
T_END = 1.0e10
DEFAULT_NE_M3 = .01 * (140.0 + 140.0*.248/(4*(1-.248)))


def _scalar(name, x, lower=0.0, strict=False):
    if isinstance(x, (bool, np.bool_)) or not np.isscalar(x):
        raise ValueError(f'{name}: finite real scalar required')
    x = float(x)
    if not math.isfinite(x) or (x <= lower if strict else x < lower):
        raise ValueError(f'{name}: outside declared domain')
    return x


@lru_cache(maxsize=1)
def parent_modules():
    """Read exact inherited bytes before executing the two local modules."""
    manifest = json.loads((ROOT / 'inputs/PARENT_SOURCE_MANIFEST.json').read_text())
    parent = ROOT.parent / 'cr_phys01_20261010'
    modules = []
    for name in ('injection', 'rudd'):
        path = parent / 'src' / (name + '.py')
        expected = manifest['files']['src/' + name + '.py']['sha256']
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('PARENT_SOURCE_HASH_MISMATCH: ' + name)
        # dataclasses needs the module present in sys.modules during execution.
        import sys
        unique = 'cr_phys02_parent_' + name
        spec = importlib.util.spec_from_file_location(unique, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique] = module
        spec.loader.exec_module(module)
        modules.append(module)
    return tuple(modules)


@lru_cache(maxsize=12)
def gauss(order):
    if isinstance(order, bool) or not isinstance(order, int) or not 4 <= order <= 512:
        raise ValueError('quadrature order must be an integer in [4,512]')
    return np.polynomial.legendre.leggauss(order)


def integrate(fun, lo, hi, order=64):
    if hi <= lo:
        return 0.0
    x, w = gauss(order)
    nodes = (hi + lo)/2 + (hi - lo)/2*x
    return float((hi-lo)/2 * np.dot(w, fun(nodes)))


@dataclass(frozen=True)
class CoulombClock:
    n_e_m3: float = DEFAULT_NE_M3
    temperature_k: float = 100.0
    cutoff_eV: float = E_MIN
    upper_eV: float = E_MAX

    def __post_init__(self):
        _scalar('n_e_m3', self.n_e_m3, strict=True)
        _scalar('temperature_k', self.temperature_k, strict=True)
        # This study is deliberately not an arbitrary-state plasma provider.
        if (self.n_e_m3 != DEFAULT_NE_M3 or self.temperature_k != 100.0
                or self.cutoff_eV != E_MIN or self.upper_eV != E_MAX):
            raise ValueError('STATE_OUTSIDE_SCOPED_STUDY')

    @property
    def omega_p_s(self):
        return math.sqrt(self.n_e_m3 * EV_J**2 / (epsilon_0*m_e))

    @property
    def amplitude(self):
        # b(E_eV) = amplitude * ln(B E_eV^(3/2))/sqrt(E_eV).
        return 4*math.pi*KAPPA**2*self.n_e_m3 / (math.sqrt(2*m_e)*EV_J**1.5)

    @property
    def log_B(self):
        return math.log(math.sqrt(2/m_e)*EV_J**1.5/(KAPPA*self.omega_p_s))

    def _energy(self, energy):
        arr = np.asarray(energy, dtype=float)
        if np.any(~np.isfinite(arr)) or np.any(arr < self.cutoff_eV) or np.any(arr > self.upper_eV):
            raise ValueError('ELECTRON_ENERGY_OUT_OF_DOMAIN')
        return arr

    def coulomb_log(self, energy):
        E = self._energy(energy)
        return self.log_B + 1.5*np.log(E)

    def stopping_eV_s(self, energy):
        E = self._energy(energy)
        return self.amplitude*self.coulomb_log(E)/np.sqrt(E)

    def clock_s(self, energy):
        """Integral_cutoff^E dE'/b(E'), via an exact Ei antiderivative."""
        E = self._energy(energy)
        scale = 2/(3*self.amplitude*math.exp(self.log_B))
        value = scale * (expi(self.coulomb_log(E)) - expi(self.coulomb_log(self.cutoff_eV)))
        return np.where(E == self.cutoff_eV, 0.0, value)

    def energy_after(self, initial_eV, age_s):
        E0 = float(self._energy(initial_eV))
        age = _scalar('age_s', age_s)
        if age == 0 or E0 == self.cutoff_eV:
            return E0
        target = float(self.clock_s(E0)) - age
        if target <= 0:
            return self.cutoff_eV
        return brentq(lambda x: float(self.clock_s(x))-target,
                      self.cutoff_eV, E0, xtol=2e-13, rtol=2e-14)

    def ramp_response(self, initial_eV, time_s, order=64):
        """Response per source coefficient A for Q_e(E0,t)=A*t.

        Returned power/A has units eV*s; cumulative energy/A is eV*s^2.
        Deposited stopping energy is independent of any FS10 terminal yield.
        """
        E0 = float(self._energy(initial_eV))
        t = _scalar('time_s', time_s)
        if t == 0:
            return dict(power_per_A=0.0, deposited_per_A=0.0,
                        active_kinetic_per_A=0.0, cutoff_kinetic_per_A=0.0,
                        injected_per_A=0.0, cutoff_number_per_A=0.0,
                        cutoff_number_rate_per_A=0.0)
        tau = float(self.clock_s(E0))
        left = self.energy_after(E0, t)
        def available_birth_time(E):
            return t - tau + self.clock_s(E)
        power = integrate(available_birth_time, left, E0, order)
        heat = .5*integrate(lambda E: available_birth_time(E)**2, left, E0, order)
        cutoff_n = .5*max(t-tau, 0.0)**2
        cutoff = self.cutoff_eV*cutoff_n
        injected = .5*E0*t*t
        active = injected-heat-cutoff
        if active < -2e-12*max(injected, 1):
            raise ArithmeticError('NEGATIVE_ACTIVE_KINETIC_ENERGY')
        return dict(power_per_A=power, deposited_per_A=heat,
                    active_kinetic_per_A=active, cutoff_kinetic_per_A=cutoff,
                    injected_per_A=injected, cutoff_number_per_A=cutoff_n,
                    cutoff_number_rate_per_A=max(t-tau, 0.0))


class DirectElectronSource:
    """Exact low-W rational shape of the inherited Rudd SDCS convolution.

    coefficient_mode='local_ramp': Q_e(W,t)=t*A(W).
    Exact Bianchi source coefficients at a specified t can also be inspected;
    they are not used to silently change the leading-order response model.
    """
    def __init__(self, order=64, enabled=True):
        if type(enabled) is not bool:
            raise ValueError('enabled must be a bool')
        self.inj, self.rudd = parent_modules()
        self.model = self.inj.InjectionModel(enabled=enabled)
        self.order = order
        x, w = gauss(order)
        lo, hi = np.log([1e6, 4e6])
        self.K = np.exp((lo+hi)/2+(hi-lo)/2*x)
        self.weights = (hi-lo)/2*w*self.K*self.model.q_proper_m3_s_eV(self.K)
        self.nH = 140.0
        self.nHe = self.nH*.248/(4*(1-.248))
        self.densities = {'H': self.nH*.99, 'He': self.nHe*.99}
        self.coefficients = self._coefficients(self.K, self.weights)

    def _coefficients(self, K, number_weight):
        out = {}
        for target, density in self.densities.items():
            data = self.rudd.TARGETS[target]
            I = data['I_eV']
            f1, f2 = self.rudd.rudd_factors(K, target)
            scale = 4*math.pi*self.rudd.A0_M**2*data['N']*(self.rudd.RYDBERG_EV/I)**2/I
            flux = number_weight*self.rudd.proton_speed_m_s(K)*density
            out[target] = (scale*float(np.dot(flux, f1)),
                           scale*float(np.dot(flux, f2)), I)
        return out

    def spectrum_A(self, energy):
        W = np.asarray(energy, dtype=float)
        if np.any(~np.isfinite(W)) or np.any(W < 0) or np.any(W > E_MAX):
            raise ValueError('DIRECT_LOW_ENERGY_SPECTRUM_DOMAIN')
        value = np.zeros_like(W)
        for c1, c2, I in self.coefficients.values():
            x = W/I
            value += (c1+c2*x)/(1+x)**3
        return value

    def source_energy_coefficient(self, lower=0.0, upper=None):
        total = 0.0
        for target, density in self.densities.items():
            moment = self.rudd.cross_section_moments(self.K, target, lower, upper)
            total += float(np.dot(self.weights*self.rudd.proton_speed_m_s(self.K)*density,
                                  moment['secondary_eV_m2']))
        return total  # eV m^-3 s^-2

    def primary_number_coefficients(self):
        return {target:float(np.dot(self.weights*self.rudd.proton_speed_m_s(self.K)*density,
                         self.rudd.cross_section_moments(self.K,target)['sigma_m2']))
                for target,density in self.densities.items()}

    def bianchi_coefficients(self, time_s, energy_order=48, age_order=8, mu_order=8):
        t = _scalar('time_s', time_s)
        pop = self.inj.transport_population(self.model, t, 3.3e-17, 3.3e-18,
              energy_order=energy_order,age_order=age_order,mu_order=mu_order)
        return self._coefficients(pop['nodes']['kinetic_eV'], pop['nodes']['number_density_m3'])


def aggregate(source, clock, time_s, energy_order=64, kernel_order=64):
    t = _scalar('time_s', time_s)
    if t > T_END:
        raise ValueError('SOURCE_LOCAL_TIME_WINDOW_EXCEEDED')
    fields = ('power_per_A','deposited_per_A','active_kinetic_per_A',
              'cutoff_kinetic_per_A','injected_per_A','cutoff_number_per_A',
              'cutoff_number_rate_per_A')
    totals = np.zeros(len(fields))
    # Split where an electron born at t=0 just reaches the tracking boundary.
    edges = [clock.cutoff_eV, clock.upper_eV]
    if 0 < t < float(clock.clock_s(clock.upper_eV)):
        edges.insert(1, brentq(lambda E: float(clock.clock_s(E))-t,
                              clock.cutoff_eV, clock.upper_eV))
    x, w = gauss(energy_order)
    for lo, hi in zip(edges[:-1],edges[1:]):
        nodes = (lo+hi)/2+(hi-lo)/2*x
        weights = (hi-lo)/2*w*source.spectrum_A(nodes)
        for E, weight in zip(nodes,weights):
            d = clock.ramp_response(float(E), t, kernel_order)
            totals += weight*np.array([d[f] for f in fields])
    out = {name:float(value) for name,value in zip(fields,totals)}
    return {
        'time_s':t, 'time_year':t/YEAR_S,
        'stopping_heat_power_J_m3_s':out['power_per_A']*EV_J,
        'deposited_stopping_energy_J_m3':out['deposited_per_A']*EV_J,
        'active_electron_kinetic_J_m3':out['active_kinetic_per_A']*EV_J,
        'cutoff_residual_kinetic_J_m3':out['cutoff_kinetic_per_A']*EV_J,
        'injected_selected_electron_energy_J_m3':out['injected_per_A']*EV_J,
        'cutoff_electron_number_m3':out['cutoff_number_per_A'],
        'cutoff_electron_number_rate_m3_s':out['cutoff_number_rate_per_A'],
        'cutoff_residual_energy_flux_J_m3_s':clock.cutoff_eV*out['cutoff_number_rate_per_A']*EV_J,
        'terminal_selected_heat_power_J_m3_s':t*source.source_energy_coefficient(E_MIN,E_MAX)*EV_J,
        'source_model':'Q_e(W,t)=t*A(W); leading local H*t limit',
        'state':'CONDITIONAL_STOPPING_COMPONENT; full delay admission false',
    }
