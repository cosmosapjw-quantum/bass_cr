"""Standalone excitation-only fixed-bath event graph. No production imports.

Each state retains integer H/He event counts, including absorbing crossing
states. Thus all residual electron energy and excitation ledgers are retained.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
import importlib.util
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import csc_matrix, eye
from scipy.sparse.linalg import expm_multiply
from scipy.stats import poisson

ROOT = Path(__file__).resolve().parent
PROVIDER_PATH = ROOT.parent / "cr_phys02c_nist_table_20261010/nist_table.py"
SPEC = importlib.util.spec_from_file_location("nist_kernel_table_provider", PROVIDER_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
C = 2.99792458e10
ME = 510998.9461
DELTAS_MEV = (10204, 21218)
CHANNELS = ("HI_1s_2p", "HeI_1s2_1S_1s2p_1P")
TARGET_CM3 = (1e-6 * 140 * .99, 1e-6 * 140 * .248 / (4 * (1 - .248)) * .99)


@lru_cache(maxsize=1)
def provider():
    return MODULE.NistTableProvider.from_local_sources()


def rates(energy_eV):
    """Proper-second rates; domain is enforced by the frozen table provider."""
    p = provider()
    cross_sections = [p.evaluate(channel, energy_eV).cross_section_cm2 for channel in CHANNELS]
    velocity = C * np.sqrt(1 - 1 / (1 + energy_eV / ME)**2)
    return np.asarray(TARGET_CM3) * cross_sections * velocity


@dataclass(frozen=True)
class EventGraph:
    initial_eV: float
    states: np.ndarray
    energies_meV: np.ndarray
    active: np.ndarray
    generator: csc_matrix
    max_rate: float

    def observables(self, population):
        energy = self.energies_meV.astype(float) / 1000
        return np.array([
            population[self.active].sum(), population[~self.active].sum(),
            population[self.active] @ energy[self.active],
            population[~self.active] @ energy[~self.active],
            population @ self.states[:, 0], population @ self.states[:, 1],
        ])


def make_graph(initial_eV, enabled=True):
    exact = Decimal(str(initial_eV)) * 1000
    if not exact.is_finite() or exact != exact.to_integral_value():
        raise ValueError("INITIAL_ENERGY_REQUIRES_EXACT_INTEGER_MEV")
    initial_meV = int(exact)
    if not 1000000 < initial_meV <= 3000000:
        raise ValueError("INITIAL_ENERGY_DOMAIN")
    states, index = [(0, 0)], {(0, 0): 0}
    rows, cols, values = [], [], []
    max_rate = 0.0
    cursor = 0
    while cursor < len(states):
        m, n = states[cursor]
        energy = initial_meV - DELTAS_MEV[0] * m - DELTAS_MEV[1] * n
        if enabled and energy > 1000000:
            channel_rates = rates(energy / 1000)
            total_rate = float(channel_rates.sum())
            max_rate = max(max_rate, total_rate)
            rows.append(cursor); cols.append(cursor); values.append(-total_rate)
            for channel, rate in enumerate(channel_rates):
                target = (m + (channel == 0), n + (channel == 1))
                if target not in index:
                    index[target] = len(states)
                    states.append(target)
                    if len(states) > 10000:
                        raise ValueError("STATE_BUDGET_EXCEEDED")
                rows.append(index[target]); cols.append(cursor); values.append(float(rate))
        cursor += 1
    states = np.asarray(states, dtype=np.int64)
    energies = initial_meV - states @ np.asarray(DELTAS_MEV, dtype=np.int64)
    size = len(states)
    generator = csc_matrix((values, (rows, cols)), shape=(size, size))
    return EventGraph(initial_meV / 1000, states, energies, energies > 1000000,
                      generator, max_rate)


def sparse_evolve(graph, time_s):
    if not np.isfinite(time_s) or time_s < 0:
        raise ValueError("PROPER_TIME_DOMAIN")
    initial = np.zeros(len(graph.states)); initial[0] = 1
    if time_s == 0 or graph.max_rate == 0:
        return initial
    return expm_multiply(graph.generator * time_s, initial)


def uniformize(graph, time_s):
    """Independent Poisson-series evolution; no clipping/renormalization."""
    if not np.isfinite(time_s) or time_s < 0:
        raise ValueError("PROPER_TIME_DOMAIN")
    initial = np.zeros(len(graph.states)); initial[0] = 1
    mu = graph.max_rate * time_s
    if mu == 0:
        return initial, 0.0, 0
    last = int(poisson.isf(1e-15, mu))
    tail = float(poisson.sf(last, mu))
    if tail >= 1e-13:
        raise ValueError("UNIFORMIZATION_TAIL")
    transition = eye(len(initial), format="csc") + graph.generator / graph.max_rate
    term = initial
    result = np.zeros_like(initial)
    # PMF evaluation avoids underflow in exp(-mu) recursion for large mu.
    weights = poisson.pmf(np.arange(last + 1), mu)
    for weight in weights:
        result += weight * term
        term = transition @ term
    return result, tail, last
