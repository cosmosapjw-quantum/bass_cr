"""Typed proper-second crossing flux from the unchanged NIST impulse graph."""
from pathlib import Path
import importlib.util
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
KERNEL_PATH = ROOT.parent / "cr_phys02c_nist_kernel_20261010/excitation_kernel.py"
SPEC = importlib.util.spec_from_file_location("crossing_flux_pinned_kernel", KERNEL_PATH)
K = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = K
SPEC.loader.exec_module(K)


def boundary(graph):
    return np.flatnonzero(~graph.active)


def flux(graph, population):
    """F_B=Q_BA p_A, per initial electron per proper gas second."""
    return np.asarray(graph.generator[~graph.active][:, graph.active] @ population[graph.active])


def slab_flux(graph, left_s, right_s, order):
    if not (np.isfinite(left_s) and np.isfinite(right_s) and 0 <= left_s <= right_s):
        raise ValueError("SLAB_PROPER_TIME_DOMAIN")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    half = (right_s - left_s) / 2
    out = np.zeros(np.count_nonzero(~graph.active))
    for node, weight in zip(nodes, weights):
        out += half * weight * flux(graph, K.sparse_evolve(graph, left_s + half * (node + 1)))
    return out


def packet_row(graph, epoch_s, population):
    ids = boundary(graph)
    return {"initial_energy_eV": graph.initial_eV, "proper_time_s": epoch_s,
            "normalization": "per initial electron; no volume or bin width",
            "boundary": [{"energy_meV": int(graph.energies_meV[i]),
                          "m_H": int(graph.states[i, 0]), "n_He": int(graph.states[i, 1]),
                          "flux_per_initial_electron_per_s": float(f),
                          "cumulative_crossing_count_per_initial_electron": float(population[i])}
                         for i, f in zip(ids, flux(graph, population))]}
