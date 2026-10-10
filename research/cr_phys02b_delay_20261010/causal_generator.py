"""Absolute-time fixed-gas electron cascade using pinned DarkHistory old rates.

This is a research sidecar. It neither imports the complete-cooling matrix nor
modifies the CR production provider. Units: eV, proper seconds, proper cm^-3.
Population entries are expected electron numbers per initial injected electron.
The <=10 eV reservoir remains unresolved, not converted into heat.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parent
SPECIES = ("HI", "HeI", "HeII")
# Constants, including reduced-mass Rydberg, match pinned physics.py exactly.
MP = 0.938272081e9
ME = 510998.9461
HBAR = 6.58211951e-16
C = 299792458e2
ALPHA = 1 / 137.035999139
MU_EP = MP * ME / (MP + ME)
RYDBERG = 0.5 * MU_EP * ALPHA**2
BOHR = HBAR * C / (MU_EP * ALPHA)
LYA = 0.75 * RYDBERG
ION = np.array([RYDBERG, 24.5873891, 4 * RYDBERG])
EXC = np.array([LYA, 2 * np.pi * HBAR * C * 159855.9745, 4 * LYA])
EPS = np.array([8.0, 15.8, 32.6])
CUTOFF = 10.0
EMAX = 1000.0


@lru_cache(maxsize=3)
def gauss_rule(order):
    return leggauss(order)


@dataclass(frozen=True)
class Gas:
    n_h_m3: float = 140.0
    helium_mass_fraction: float = 0.248
    x_hii_per_h: float = 0.01
    x_heii_per_he: float = 0.01
    x_heiii_per_he: float = 0.0
    temperature_k: float = 100.0

    def __post_init__(self):
        vals = tuple(self.__dict__.values())
        if not all(np.isfinite(v) for v in vals):
            raise ValueError("NONFINITE_GAS")
        if not (self.n_h_m3 > 0 and 0 <= self.helium_mass_fraction < 1):
            raise ValueError("GAS_DENSITY_DOMAIN")
        if not (0 <= self.x_hii_per_h <= 1 and 0 <= self.x_heii_per_he
                and 0 <= self.x_heiii_per_he
                and self.x_heii_per_he + self.x_heiii_per_he <= 1):
            raise ValueError("IONIC_DOMAIN")
        if self.temperature_k != 100.0:
            raise ValueError("ONLY_100K_CONTRACT")

    @property
    def n_he_m3(self):
        y = self.helium_mass_fraction
        return self.n_h_m3 * y / (4 * (1 - y))

    @property
    def target_cm3(self):
        return 1e-6 * np.array([
            self.n_h_m3 * (1 - self.x_hii_per_h),
            self.n_he_m3 * (1 - self.x_heii_per_he - self.x_heiii_per_he),
            self.n_he_m3 * self.x_heii_per_he,
        ])

    @property
    def electron_cm3(self):
        return 1e-6 * (self.n_h_m3 * self.x_hii_per_h
                      + self.n_he_m3 * (self.x_heii_per_he
                                        + 2 * self.x_heiii_per_he))


def verify_sources():
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text())
    for relative, expected in manifest["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"SOURCE_BYTES_MISMATCH:{relative}")
    return manifest


def _energy(energy):
    e = np.asarray(energy, dtype=float)
    if not np.all(np.isfinite(e)) or np.any(e < CUTOFF) or np.any(e > EMAX):
        raise ValueError("ELECTRON_RATE_DOMAIN_10_1000_EV")
    return e


def ionization_xsec(energy, species):
    """Old Arnaud/Rothenflug rate fit, cm^2, not a normalized probability."""
    e = _energy(energy)
    k = SPECIES.index(species)
    a, b, cc, d = [(22.8, -12.0, 1.9, -22.6),
                   (17.8, -11.0, 7.0, -23.2),
                   (14.4, -5.6, 1.9, -13.3)][k]
    u = e / ION[k]
    sigma = 1e-14 / (u * ION[k]**2) * (
        a * (1 - 1 / u) + b * (1 - 1 / u)**2
        + cc * np.log(u) + d * np.log(u) / u)
    return np.where(e <= ION[k], 0.0, sigma)


def excitation_xsec(energy, species):
    """Pinned old-method effective excitation cross sections, cm^2."""
    e = _energy(energy)
    k = SPECIES.index(species)
    if k < 2:
        a, b, cc = [(0.5555, 0.2718, 0.0001), (0.1771, -0.0822, 0.0356)][k]
        sigma = 4 * np.pi * BOHR**2 * RYDBERG / (e + ION[k] + EXC[k]) * (
            a * np.log(e / RYDBERG) + b + cc * RYDBERG / e)
    else:
        x = e / EXC[k]
        sigma = np.pi * BOHR**2 / (16 * x) * (
            3.22 * np.log(x) + 0.357 * np.log(x) / x
            + 0.00157 + 1.59 / x + 0.764 / x**2)
    return np.where(e <= EXC[k], 0.0, sigma)


def velocity(energy):
    e = _energy(energy)
    return C * np.sqrt(1 - 1 / (1 + e / ME)**2)


def coulomb_loss(energy, gas):
    """Positive eV/s loss with explicit proper electron density.

    This is upstream old Spitzer/Shull Coulomb drag. Temperature dependence and
    diffusion are absent in that formula; 100 K is the frozen background only.
    """
    e = _energy(energy)
    if gas.electron_cm3 == 0:
        return np.zeros_like(e)
    ne_natural = gas.electron_cm3 * (HBAR * C)**3
    beta = velocity(e) / C
    log_lambda = np.log(4 * e * (4 * np.pi * ALPHA * ne_natural / ME)**(-0.5))
    loss = 4 * np.pi * ALPHA**2 * ne_natural * log_lambda / (ME * beta) / HBAR
    if np.any(~np.isfinite(loss)) or np.any(loss < 0):
        raise ValueError("COULOMB_FORMULA_DOMAIN")
    return loss


def make_grid(intervals):
    if not isinstance(intervals, int) or not 16 <= intervals <= 512:
        raise ValueError("GRID_BUDGET")
    # Partition at the physical thresholds and all frozen impulses. Piecewise
    # logarithmic panels avoid almost coincident inserted knots and keep every
    # level nested: each panel's subdivision count doubles with intervals.
    anchors = np.sort(np.r_[CUTOFF, ION, EXC, 20.0, 100.0, EMAX])
    base = min(intervals, 128)
    shares = (base - (len(anchors) - 1)) * np.diff(np.log(anchors)) / np.log(EMAX / CUTOFF)
    base_counts = 1 + np.floor(shares).astype(int)
    remainder = base - int(base_counts.sum())
    base_counts[np.argsort(-(shares - np.floor(shares)))[:remainder]] += 1
    factor = max(1, intervals // 128)
    panels = [np.geomspace(lo, hi, int(count * factor) + 1)[:-1]
              for lo, hi, count in zip(anchors[:-1], anchors[1:], base_counts)]
    return np.r_[np.concatenate(panels), EMAX]


def project_daughters(grid, energy, weight):
    """Return grid counts plus subcutoff number and energy, with exact moments.

    Node zero (10 eV) is inert. Daughters below it retain their actual energy in
    a separate reservoir. Above it, barycentric weights preserve N and E.
    """
    e, w = np.broadcast_arrays(np.atleast_1d(energy), np.atleast_1d(weight))
    if (np.any(~np.isfinite(e)) or np.any(~np.isfinite(w))
            or np.any(e < 0) or np.any(e > grid[-1]) or np.any(w < 0)):
        raise ValueError("DAUGHTER_DOMAIN")
    below = e < grid[0]
    out = np.zeros(len(grid))
    cutoff_n = float(w[below].sum())
    cutoff_e = float(np.dot(e[below], w[below]))
    keep_e, keep_w = e[~below], w[~below]
    upper = np.searchsorted(grid, keep_e, side="left")
    at_bottom = upper == 0
    out[0] = keep_w[at_bottom].sum()
    upper = upper[~at_bottom]
    if len(upper):
        e1, w1 = keep_e[~at_bottom], keep_w[~at_bottom]
        frac = (e1 - grid[upper - 1]) / (grid[upper] - grid[upper - 1])
        np.add.at(out, upper, w1 * frac)
        np.add.at(out, upper - 1, w1 * (1 - frac))
    return out, cutoff_n, cutoff_e


def ionization_daughters(grid, parent_e, k, order):
    """Conditional two-electron old-method distribution at one ionization.

    Each quadrature outcome pairs e and parent_e-I-e. Normalization fixes one
    lower electron; both daughter counts and their combined energy follow from
    the pairing. It does not normalize the absolute collision rate or cooling.
    Breakpoints include both daughters' projection changes.
    """
    available = parent_e - ION[k]
    if available <= 0:
        raise ValueError("IONIZATION_BELOW_THRESHOLD")
    half = 0.5 * available
    breaks = np.unique(np.concatenate(([0.0, half],
                                      grid[(grid > 0) & (grid < half)],
                                      (available - grid)[
                                          (available - grid > 0)
                                          & (available - grid < half)])))
    nodes, weights = gauss_rule(order)
    midpoint = 0.5 * (breaks[1:] + breaks[:-1])
    radius = 0.5 * np.diff(breaks)
    low_e = (midpoint[:, None] + radius[:, None] * nodes).ravel()
    raw_w = (radius[:, None] * weights).ravel() / (1 + (low_e / EPS[k])**2.1)
    prob = raw_w / raw_w.sum()
    return project_daughters(grid, np.concatenate((low_e, available - low_e)),
                             np.concatenate((prob, prob)))


@dataclass
class Generator:
    grid: np.ndarray
    matrix: csc_matrix
    gas: Gas
    quadrature_order: int

    @property
    def n(self):
        return len(self.grid)

    @property
    def rho(self):
        # Retain the original step-size budget even though drag is now exact.
        drift = coulomb_loss(self.grid[1:], self.gas) / np.diff(self.grid)
        return float(np.max(-self.matrix.diagonal()[1:self.n] + drift))

    def impulse(self, energy):
        if not CUTOFF <= energy <= EMAX or not np.isfinite(energy):
            raise ValueError("IMPULSE_DOMAIN")
        counts, cn, ce = project_daughters(self.grid, energy, 1.0)
        state = np.zeros(self.n + 9)
        state[:self.n] = counts
        state[-2:] = cn, ce
        return state

    def weights(self, grid=None):
        energy = np.r_[self.grid if grid is None else grid, ION, EXC, 1.0, 0.0, 1.0]
        number = np.r_[np.ones(self.n), -np.ones(3), np.zeros(4), 1.0, 0.0]
        return number, energy

    def observe(self, state):
        grid = getattr(state, "energy_grid", self.grid)
        active = grid > CUTOFF
        ion_counts = state[self.n:self.n + 3]
        exc_counts = state[self.n + 3:self.n + 6]
        return {
            "active_electron_number": float(state[:self.n][active].sum()),
            "active_energy_eV": float(grid[active] @ state[:self.n][active]),
            "ionization_counts": ion_counts.tolist(),
            "binding_energy_eV": float(ION @ ion_counts),
            "excitation_counts": exc_counts.tolist(),
            "excitation_energy_eV": float(EXC @ exc_counts),
            "coulomb_heat_eV": float(state[-3]),
            "cutoff_electron_number": float(state[:self.n][~active].sum() + state[-2]),
            "cutoff_energy_eV": float(CUTOFF * state[:self.n][~active].sum() + state[-1]),
            "minimum_state": float(state.min()),
            "number_ledger": float(self.weights()[0] @ state),
            "energy_ledger_eV": float(self.weights(grid)[1] @ state),
        }


def assemble(intervals=128, gas=None, quadrature_order=8):
    verify_sources()
    if quadrature_order not in (8, 12):
        raise ValueError("QUADRATURE_CONTRACT")
    gas = Gas() if gas is None else gas
    grid = make_grid(intervals)
    return Generator(grid, collision_matrix(grid, gas, quadrature_order), gas,
                     quadrature_order)


def collision_matrix(grid, gas, quadrature_order):
    """Unchanged absolute collision terms on the current characteristic grid."""
    n = len(grid)
    a = np.zeros((n + 9, n + 9))
    speed = velocity(grid)
    for k, species in enumerate(SPECIES):
        irates = gas.target_cm3[k] * speed * ionization_xsec(grid, species)
        erates = gas.target_cm3[k] * speed * excitation_xsec(grid, species)
        if np.any(irates < 0) or np.any(erates < 0):
            raise ValueError("NEGATIVE_ATOMIC_RATE")
        for j in range(1, n):
            if irates[j] > 0:
                daughters, cn, ce = ionization_daughters(grid, grid[j], k, quadrature_order)
                a[j, j] -= irates[j]
                a[:n, j] += irates[j] * daughters
                a[n + k, j] += irates[j]
                a[-2, j] += irates[j] * cn
                a[-1, j] += irates[j] * ce
            if erates[j] > 0:
                daughters, cn, ce = project_daughters(grid, grid[j] - EXC[k], 1.0)
                a[j, j] -= erates[j]
                a[:n, j] += erates[j] * daughters
                a[n + 3 + k, j] += erates[j]
                a[-2, j] += erates[j] * cn
                a[-1, j] += erates[j] * ce
    if np.any(~np.isfinite(a)):
        raise ValueError("NONFINITE_GENERATOR")
    return csc_matrix(a)


def cooling_time(energy, gas):
    """Physical flight time to 10 eV; Gauss integration is not a population grid."""
    energy = _energy(energy)
    if gas.electron_cm3 == 0:
        return np.where(energy == CUTOFF, 0.0, np.inf)
    return flight_time(CUTOFF, energy, gas)


def flight_time(lower, upper, gas):
    """Integrate the actual flight segment, avoiding subtraction of large ages."""
    nodes, weights = gauss_rule(64)
    half = 0.5 * (upper - lower)
    sample = np.asarray(lower)[..., None] + half[..., None] * (1 + nodes)
    return half * np.sum(weights / coulomb_loss(sample, gas), axis=-1)


def characteristic_grid(grid, gas, time_s):
    """Exact deterministic drag with an absorbing, unresolved cutoff.

    Nodes that arrive remain at 10 eV. No population or energy is discarded;
    their number and kinetic energy remain in the cutoff reservoir.
    """
    if time_s == 0 or gas.electron_cm3 == 0:
        return grid.copy()
    arrival = cooling_time(grid, gas)
    moving = arrival > time_s
    out = np.full_like(grid, CUTOFF)
    target = arrival[moving] - time_s
    original = grid[moving]
    ratio = target / arrival[moving]
    energy = (CUTOFF**1.5 + ratio * (original**1.5 - CUTOFF**1.5))**(2 / 3)
    for _ in range(6):
        energy += (flight_time(energy, original, gas) - time_s) * coulomb_loss(energy, gas)
    if np.any(energy < CUTOFF) or np.any(energy > original):
        raise ValueError("CHARACTERISTIC_ROOT_DOMAIN")
    residual = np.abs(flight_time(energy, original, gas) - time_s)
    if np.any(residual > 2e-12 * np.maximum(arrival[moving], 1.0)):
        raise ValueError("CHARACTERISTIC_ROOT_RESIDUAL")
    out[moving] = energy
    return out


class CharacteristicState(np.ndarray):
    """Population/reservoir array with its own instantaneous energy nodes."""

    def __new__(cls, values, grid, time_s):
        out = np.asarray(values).view(cls)
        out.energy_grid = grid.copy()
        out.time_s = time_s
        return out

    def __array_finalize__(self, obj):
        if obj is not None:
            self.energy_grid = getattr(obj, "energy_grid", None)
            self.time_s = getattr(obj, "time_s", None)


def _characteristic_evolve(generator, initial, edges, method):
    state = np.asarray(initial).copy()
    old_grid = generator.grid.copy()
    for start, stop in zip(edges[:-1], edges[1:]):
        dt = stop - start
        midpoint = 0.5 * (start + stop)
        mid_grid = characteristic_grid(generator.grid, generator.gas, midpoint)
        new_grid = characteristic_grid(generator.grid, generator.gas, stop)
        state[-3] += (old_grid - mid_grid) @ state[:generator.n]
        matrix = collision_matrix(mid_grid, generator.gas, generator.quadrature_order)
        if method == "ssprk2":
            if dt * float(np.max(-matrix.diagonal())) > 0.4 * (1 + 4 * np.finfo(float).eps):
                raise ValueError("SSPRK2_COLLISION_CFL")
            stage = state + dt * (matrix @ state)
            state = 0.5 * state + 0.5 * (stage + dt * (matrix @ stage))
        elif method == "dense":
            state = expm(matrix.toarray() * dt) @ state
        else:
            state = expm_multiply(matrix * dt, state,
                                  traceA=float(matrix.diagonal().sum() * dt))
        state[-3] += (mid_grid - new_grid) @ state[:generator.n]
        old_grid = new_grid
    return CharacteristicState(state, old_grid, edges[-1])


def evolve(generator, initial, time_s, enabled=True, steps=None, method="sparse"):
    """Conservative characteristic drag and dimensional collision stages."""
    if not np.isfinite(time_s) or not 0 <= time_s <= 1e13:
        raise ValueError("TIME_CONTRACT")
    if initial.shape[0] != generator.n + 9 or initial.ndim not in (1, 2) or np.any(initial < 0) or not np.all(np.isfinite(initial)):
        raise ValueError("INITIAL_STATE_DOMAIN")
    if time_s == 0 or not enabled:
        return initial.copy()
    if not np.any(initial[1:generator.n]):
        # The cutoff and all accumulated reservoirs are exactly stationary.
        return initial.copy()
    if steps is not None:
        if not isinstance(steps, int) or not 1 <= steps <= 65536:
            raise ValueError("STEP_BUDGET")
        edges = np.linspace(0, time_s, steps + 1)
    else:
        # Fixed deterministic step schedule, shared by every grid level.
        edges = [0.0]
        while edges[-1] < time_s:
            dt = min(1e11, max(2e9, 0.04 * edges[-1]))
            edges.append(min(time_s, edges[-1] + dt))
        edges = np.asarray(edges)
    return _characteristic_evolve(generator, initial, edges, method)


def evolve_ssprk2(generator, initial, time_s, steps):
    """Independent positive time discretization for the finite-time audit."""
    if not isinstance(steps, int) or not 1 <= steps <= 65536:
        raise ValueError("STEP_BUDGET")
    if not np.isfinite(time_s) or not 0 <= time_s <= 1e13:
        raise ValueError("TIME_CONTRACT")
    dt = time_s / steps
    if dt * generator.rho > 0.4 * (1 + 4 * np.finfo(float).eps):
        raise ValueError("SSPRK2_CFL")
    return evolve(generator, initial, time_s, steps=steps, method="ssprk2")


def energy_channels(generator, state):
    obs = generator.observe(state)
    return np.array([obs[k] for k in ("active_energy_eV", "binding_energy_eV",
                                     "excitation_energy_eV", "coulomb_heat_eV",
                                     "cutoff_energy_eV")])
