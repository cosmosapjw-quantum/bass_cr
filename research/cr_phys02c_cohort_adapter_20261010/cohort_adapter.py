"""Fresh age-zero cohort adapter; no receiver evolution or physical closure."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
PACKET = ROOT.parent / 'cr_phys02c_crossing_flux_20261010/evidence/BOUNDARY_PACKET_RECOMPUTED.json'
PACKET_SHA = 'df8b917a4fffe665e698d32f1ccf7763200d150f565c24e63a72f33a82da6005'
P02B_SHA = 'ea72b12d07bc500cb7c917c5e500325c6864da77cdd90637ddceab7aeddfa0da'
CLOCK = 'elapsed gas-proper seconds'
NORMALIZATION = 'per initial electron; no volume or bin width'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

F = load('cohort_crossing', ROOT.parent / 'cr_phys02c_crossing_flux_20261010/crossing_flux.py')
P = load('cohort_projection', ROOT.parent / 'cr_phys02b_delay_20261010/causal_generator.py')

def verify_inputs():
    for path, expected in [(PACKET, PACKET_SHA), (Path(P.__file__), P02B_SHA)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('PINNED_INPUT_MISMATCH')

def time(value):
    if not np.isfinite(value) or value < 0 or value > 1e13:
        raise ValueError('PROPER_TIME_DOMAIN')
    return float(value)

@dataclass(frozen=True)
class BoundarySource:
    graph: object
    clock: str = CLOCK
    normalization: str = NORMALIZATION
    source_identity: str = PACKET_SHA

    @classmethod
    def from_energy(cls, energy_eV, enabled=True):
        verify_inputs()
        return cls(F.K.make_graph(energy_eV, enabled))

    def validate(self):
        if self.clock != CLOCK or self.normalization != NORMALIZATION:
            raise ValueError('CLOCK_OR_NORMALIZATION_MISMATCH')
        if self.source_identity != PACKET_SHA:
            raise ValueError('SOURCE_IDENTITY_MISMATCH')

@dataclass(frozen=True)
class BoundaryRate:
    energy_meV: np.ndarray
    rate_per_upstream_electron_s: np.ndarray
    m_H: np.ndarray
    n_He: np.ndarray
    proper_time_s: float
    source_identity: str
    clock: str = CLOCK
    normalization: str = NORMALIZATION

    def validate(self):
        time(self.proper_time_s)
        if self.clock != CLOCK or self.normalization != NORMALIZATION or self.source_identity != PACKET_SHA:
            raise ValueError('BOUNDARY_IDENTITY_OR_UNITS')
        e, r = np.asarray(self.energy_meV), np.asarray(self.rate_per_upstream_electron_s)
        if (e.ndim != 1 or r.shape != e.shape or np.asarray(self.m_H).shape != e.shape
                or np.asarray(self.n_He).shape != e.shape or np.any(~np.isfinite(e))
                or np.any(e != np.floor(e)) or np.any(e <= 978782) or np.any(e > 1000000)
                or np.any(~np.isfinite(r)) or np.any(r < 0)):
            raise ValueError('BOUNDARY_RATE_DOMAIN')
        if (np.any(np.asarray(self.m_H) < 0) or np.any(np.asarray(self.n_He) < 0)
                or np.any(~np.isfinite(self.m_H)) or np.any(~np.isfinite(self.n_He))
                or np.any(np.asarray(self.m_H) != np.floor(self.m_H))
                or np.any(np.asarray(self.n_He) != np.floor(self.n_He))):
            raise ValueError('UPSTREAM_BOOKKEEPING_DOMAIN')

def sample_boundary(source, tau):
    source.validate()
    tau = time(tau)
    graph = source.graph
    ids = F.boundary(graph)
    rate = BoundaryRate(graph.energies_meV[ids].copy(),
                        F.flux(graph, F.K.sparse_evolve(graph, tau)),
                        graph.states[ids, 0].copy(), graph.states[ids, 1].copy(),
                        tau, source.source_identity)
    rate.validate()
    return rate

def project_boundary_rate(rate):
    """P02B layout: n grid rates, 3 ion, 3 excitation, plasma, cutoff N/E."""
    rate.validate()
    grid = P.make_grid(128)
    counts, cutoff_n, cutoff_e = P.project_daughters(
        grid, rate.energy_meV.astype(float) / 1000, rate.rate_per_upstream_electron_s)
    out = np.zeros(len(grid) + 9)
    out[:len(grid)] = counts
    out[len(grid)+7:len(grid)+9] = cutoff_n, cutoff_e
    return out

@dataclass(frozen=True)
class Cohort:
    birth_time_s: float
    quadrature_weight_s: float
    initial_population: np.ndarray
    boundary_rate: BoundaryRate
    initial_age_s: float = 0.0

    def age_at(self, observation_time_s):
        return age_at(observation_time_s, self.birth_time_s)

def age_at(observation_time_s, birth_time_s):
    age = time(observation_time_s) - time(birth_time_s)
    if age < 0:
        raise ValueError('OBSERVATION_BEFORE_COHORT_BIRTH')
    return age

def cohort_quadrature(source, left_s, right_s, order):
    left_s, right_s = time(left_s), time(right_s)
    if right_s < left_s or order not in (16, 32):
        raise ValueError('COHORT_QUADRATURE_DOMAIN')
    if right_s == left_s:
        return ()
    nodes, weights = np.polynomial.legendre.leggauss(order)
    half = (right_s-left_s)/2
    cohorts = []
    for x, w in zip(nodes, weights):
        tau, ws = left_s+half*(x+1), half*w
        rate = sample_boundary(source, tau)
        cohorts.append(Cohort(tau, ws, ws*project_boundary_rate(rate), rate))
    return tuple(cohorts)
