"""Small event adapter for the pinned BASS_CR PHYS02C/PHYS02B kernel.

Loads the actual saved 9600-node energy array. Only selected unchanged source
definitions are executed; no source, generator, matrix exponential, or ODE is
built. The exact event layer interprets finite source inputs as rationals.
Physical state energies are SI joules; source tabulations retain eV labels.
"""
from __future__ import annotations

import ast
from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from types import MethodType, ModuleType, SimpleNamespace

import numpy as np
from scipy.constants import e as EV_J_FLOAT, epsilon_0, m_e, hbar

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "inputs/kernel_sources"
EV_J = Q("1.602176634e-19")
K_B = Q("1.380649e-23")
PARENT_PATH = "research/cr_phys02b_20261010/src/causal_cascade.py"
BED_PATH = "research/cr_phys02c_20261011/src/coherent_bed.py"
NPZ_PATH = ("research/cr_phys02c_paired_9600_closeout_20261011/raw/"
            "THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_fullBED_9600.npz")
GRID_SHA256 = "6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292"


def _unchanged_definitions(path, names, namespace, *, owner=None):
    """Execute named AST nodes without importing a source module's side effects."""
    tree = ast.parse(path.read_text(), filename=str(path))
    candidates = tree.body
    if owner:
        candidates = next(x.body for x in tree.body
                          if isinstance(x, ast.ClassDef) and x.name == owner)
    nodes = []
    found = set()
    for node in candidates:
        name = getattr(node, "name", None)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
        if name in names:
            nodes.append(node)
            found.add(name)
    if found != set(names):
        raise ValueError(f"Missing exact source definitions: {set(names)-found}")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)


@dataclass(frozen=True)
class Projection:
    active: dict[int, Q]
    absorbed_count: Q
    absorbed_energy_eV: Q
    actual_subcut_count: Q
    actual_subcut_energy_eV: Q
    ghost_count: Q
    ghost_energy_eV: Q


@dataclass(frozen=True)
class Event:
    name: str
    kind: str
    parent: int
    species: str | None
    column: dict[str, Q]
    probability: Q
    coefficient: Q
    daughters_eV: tuple[Q, ...]
    projection: Projection
    heat_eV: Q = Q(0)
    reservoir_eV: Q = Q(0)


class BoundKernel:
    def __init__(self):
        binding = json.loads((ROOT / "inputs/KERNEL_SOURCE_BINDING.json").read_text())
        self.binding = binding
        for record in binding["files"]:
            raw = (SOURCES / record["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != record["sha256"]:
                raise ValueError("Pinned source hash mismatch: " + record["path"])
        with np.load(SOURCES / NPZ_PATH) as saved:
            self.E = np.array(saved["energy_eV"], copy=True)
        if (self.E.dtype.str != "<f8" or len(self.E) != 9600
                or hashlib.sha256(self.E.tobytes(order="C")).hexdigest() != GRID_SHA256):
            raise ValueError("Saved energy-grid identity mismatch")
        self.Eq = tuple(Q(float(x)) for x in self.E)

        parent = ModuleType("bass_cr_kernel_pinned_definitions")
        sys.modules[parent.__name__] = parent
        ns = vars(parent)
        ns.update(np=np, math=math, dataclass=dataclass, lru_cache=lru_cache,
                  EV_J=EV_J_FLOAT, epsilon_0=epsilon_0, m_e=m_e, hbar=hbar)
        names = {"CUT", "SPLIT", "UPPER", "T_END", "N_H", "N_HE", "N_E",
                 "DENSITIES", "A0_M", "KAPPA", "LEDGERS", "ENERGY_LEDGERS",
                 "gauss", "checked_energy", "Ionization", "stopping_eV_s"}
        _unchanged_definitions(SOURCES / PARENT_PATH, names, ns)
        self.parent = parent
        self.cut = Q(float(parent.CUT))
        oracle = json.loads((SOURCES / "research/cr_phys02c_20261011/research/"
                             "ionization_sources/SOURCE_ALGEBRA_RESULT.json").read_text())
        bed = {"np": np, "math": math, "parent": parent, "ORACLE": oracle}
        _unchanged_definitions(SOURCES / BED_PATH, {"Ionization"}, bed)
        self.ions = {sp: bed["Ionization"](sp) for sp in ("HI", "HeI")}

        _unchanged_definitions(SOURCES / PARENT_PATH, {"project", "_sharing"},
                              ns, owner="Cascade")
        _unchanged_definitions(SOURCES / PARENT_PATH, {"excitation_sigma"},
                              ns, owner="AtomicData")
        obj = SimpleNamespace(E=self.E, n=len(self.E),
                              size=len(self.E)+len(parent.LEDGERS),
                              ix={s: len(self.E)+i for i, s in enumerate(parent.LEDGERS)},
                              sharing_order=4, normalization_diagnostics=[])
        obj.project = MethodType(ns["project"], obj)
        obj._sharing = MethodType(ns["_sharing"], obj)
        self.original = obj
        self._sharing_cache = {}
        self.channels = {}
        used = json.loads((SOURCES / "research/cr_phys02b_20261010/inputs/"
                           "CCC_USED_CHANNELS.json").read_text())
        for relative in ("inputs/ccc/HI/2P.1S", "inputs/ccc/HeI/t2S.s1S"):
            channel = next(c for c in used["channels"] if c["path"] == relative)
            raw_path = SOURCES / "research/cr_phys02b_20261010" / relative
            data = np.loadtxt(raw_path, comments="#", usecols=(0, 1))
            factor = used["a0_m"]**2 if channel["native_unit"] == "a0^2" else 1.e-4
            if (np.any(np.diff(data[:, 0]) <= 0) or np.any(data[:, 1] < 0)
                    or np.any(~np.isfinite(data)) or data[-1, 0] < parent.UPPER):
                raise ValueError("Invalid selected native CCC table")
            self.channels[relative] = dict(channel, energy=data[:, 0],
                                           sigma=data[:, 1]*factor)

    def sharing(self, index, species):
        key = (index, species)
        if key not in self._sharing_cache:
            w, p = self.original._sharing(self.ions[species], float(self.E[index]))
            p_exact = tuple(Q(float(x)) for x in p)
            normalizer = sum(p_exact, Q(0))
            self._sharing_cache[key] = (w, p, tuple(x/normalizer for x in p_exact))
        return self._sharing_cache[key]

    def project_exact(self, energies, counts=None):
        values = tuple(Q(x) for x in energies)
        weights = tuple(Q(x) for x in counts) if counts is not None else (Q(1),)*len(values)
        if len(values) != len(weights):
            raise ValueError("Energy/count lengths differ")
        active = {}
        actual_n = actual_u = ghost_n = Q(0)
        for w, count in zip(values, weights):
            if w < 0 or w > self.Eq[-1] or count < 0:
                raise ValueError("Projection outside selected physical domain")
            if w <= self.cut:
                actual_n += count
                actual_u += w*count
                continue
            j = bisect_left(self.Eq, w)
            upper = self.Eq[j]
            lower = self.cut if j == 0 else self.Eq[j-1]
            beta = (w-lower)/(upper-lower)
            active[j] = active.get(j, Q(0)) + count*beta
            if j:
                active[j-1] = active.get(j-1, Q(0)) + count*(1-beta)
            else:
                ghost_n += count*(1-beta)
        active = {j: a for j, a in active.items() if a}
        return Projection(active, actual_n+ghost_n, actual_u+self.cut*ghost_n,
                          actual_n, actual_u, ghost_n, self.cut*ghost_n)

    def _electron_column(self, index, projected):
        col = {f"A:{j}": count for j, count in projected.active.items()}
        key = f"A:{index}"
        col[key] = col.get(key, Q(0))-1
        col["e_th"] = projected.absorbed_count
        col["U_th"] = EV_J*projected.absorbed_energy_eV
        return {name: value for name, value in col.items() if value}

    def ion_event(self, index, species, quadrature_index):
        ion = self.ions[species]
        slow, _, p = self.sharing(index, species)
        w = Q(float(slow[quadrature_index]))
        binding = Q(float(ion.B_eV))
        fast = self.Eq[index]-binding-w
        proj = self.project_exact((w, fast))
        col = self._electron_column(index, proj)
        col[species] = Q(-1)
        col[{"HI": "HII", "HeI": "HeII"}[species]] = Q(1)
        speed = math.sqrt(2*float(self.E[index])*EV_J_FLOAT/m_e)
        coefficient = Q(float(speed*ion.total_m2(float(self.E[index]))))*p[quadrature_index]
        return Event(f"ion:{species}:{index}:{quadrature_index}", "ionization", index,
                     species, col, p[quadrature_index], coefficient, (w, fast), proj,
                     reservoir_eV=binding)

    def excitation_event(self, index, relative):
        channel = self.channels[relative]
        energy = float(self.E[index])
        sigma = float(self.parent.excitation_sigma(None, channel, energy))
        if sigma <= 0:
            raise ValueError("Select a node with positive excitation cross section")
        cost = Q(float(channel["adopted_effective_cost_eV"]))
        daughter = self.Eq[index]-cost
        proj = self.project_exact((daughter,))
        col = self._electron_column(index, proj)
        col["E_exc_"+channel["species"]] = EV_J*cost
        coefficient = Q(float(math.sqrt(2*energy*EV_J_FLOAT/m_e)*sigma))
        return Event(f"exc:{relative}:{index}", "excitation", index, channel["species"],
                     col, Q(1), coefficient, (daughter,), proj, reservoir_eV=cost)

    def coulomb(self, index, n_e, *, quantum_constant=0.):
        if quantum_constant not in (0., -.5) or not math.isfinite(n_e) or n_e <= 0:
            raise ValueError("Positive bath density and declared Coulomb prescription required")
        energy = float(self.E[index])
        speed = math.sqrt(2*energy*EV_J_FLOAT/m_e)
        omega = math.sqrt(n_e*EV_J_FLOAT**2/(epsilon_0*m_e))
        classical = math.log(speed*energy*EV_J_FLOAT/(self.parent.KAPPA*omega))
        quantum = math.log(2*energy*EV_J_FLOAT/(hbar*omega))+quantum_constant
        log_l = min(classical, quantum)
        if log_l <= 0:
            raise ValueError("Selected positive Coulomb-log domain required")
        alpha = 4*math.pi*self.parent.KAPPA**2/(m_e*speed*EV_J_FLOAT)
        delta = float(self.Eq[index]-(self.cut if index == 0 else self.Eq[index-1]))
        return {"n_e_m3": n_e, "L": log_l, "alpha": alpha,
                "b_eV_per_s": alpha*n_e*log_l,
                "lambda_per_s": alpha*n_e*log_l/delta,
                "d_lambda_d_ne": alpha*(log_l-.5)/delta,
                "delta_eV": delta}

    def drift_event(self, index, n_e):
        previous = self.cut if index == 0 else self.Eq[index-1]
        proj = self.project_exact((previous,))
        col = self._electron_column(index, proj)
        heat = self.Eq[index]-previous
        col["U_th"] = col.get("U_th", Q(0))+EV_J*heat
        rate = Q(float(self.coulomb(index, float(n_e))["lambda_per_s"]))
        return Event(f"drift:{index}", "drift", index, None, col, Q(1), rate,
                     (previous,), proj, heat_eV=heat)

    def invariants(self, active_indices):
        return {
            "H_nuclei": {"HI": Q(1), "HII": Q(1)},
            "He_nuclei": {"HeI": Q(1), "HeII": Q(1)},
            "charge_over_e": {**{f"A:{j}": Q(-1) for j in active_indices},
                              "e_th": Q(-1), "HII": Q(1), "HeII": Q(1)},
            "energy_J": {**{f"A:{j}": EV_J*self.Eq[j] for j in active_indices},
                         "HII": EV_J*Q(float(self.ions["HI"].B_eV)),
                         "HeII": EV_J*Q(float(self.ions["HeI"].B_eV)),
                         "U_th": Q(1), "E_exc_HI": Q(1), "E_exc_HeI": Q(1)},
        }

    def proposal(self, event, base_state, volume, *, initial_cutoff_eV=None,
                 trial_thermal_electron_count=None, trial_species_counts=None):
        """Freeze the initial active mask; trial EOS changes only coefficients.

        Raw A:j may include retained thermal-owned atoms. They are donors only
        when W_j exceeds the initial accepted cutoff. The thermal electron
        count supplied for stopping includes the base bath and thermal-owned
        atoms, and excludes nuclei. Trial neutral counts provide the actual
        target-density feedback on the fixed positive base support. Omitting
        trial counts specializes to frozen target densities. No trial mask is
        written into event columns.
        """
        volume = Q(volume)
        if volume <= 0:
            raise ValueError("Physical volume must be positive")
        cutoff = self.cut if initial_cutoff_eV is None else Q(initial_cutoff_eV)
        if self.Eq[event.parent] <= cutoff:
            return Q(0)
        coefficient = event.coefficient
        if event.kind == "drift" and trial_thermal_electron_count is not None:
            n_e = float(Q(trial_thermal_electron_count)/volume)
            coefficient = Q(float(self.coulomb(event.parent, n_e)["lambda_per_s"]))
        value = coefficient*Q(base_state.get(f"A:{event.parent}", 0))
        if event.species:
            base_target = Q(base_state.get(event.species, 0))
            if base_target <= 0:
                return Q(0)
            target = base_target if trial_species_counts is None else Q(trial_species_counts[event.species])
            if target < 0:
                raise ValueError("Trial neutral counts must be nonnegative")
            value *= target/volume
        return value


def dot(row, state):
    return sum((Q(weight)*Q(state.get(name, 0)) for name, weight in row.items()), Q(0))


def event_json(event, kernel):
    p = event.projection
    return {
        "name": event.name, "kind": event.kind, "species": event.species,
        "parent": {"index": event.parent, "W_eV": float(kernel.E[event.parent]),
                   "W_eV_exact_binary_rational": str(kernel.Eq[event.parent])},
        "probability": float(event.probability),
        "coefficient": float(event.coefficient),
        "coefficient_unit": "1/s" if event.kind == "drift" else "m^3/s",
        "raw_daughters_eV": [float(w) for w in event.daughters_eV],
        "raw_daughters_eV_exact": [str(w) for w in event.daughters_eV],
        "active_daughters": [{"index": j, "W_eV": float(kernel.E[j]),
                              "A_count": float(a), "A_count_exact": str(a)}
                             for j, a in sorted(p.active.items())],
        "subcut_actual": {"count": float(p.actual_subcut_count),
                           "energy_eV": float(p.actual_subcut_energy_eV)},
        "cutoff_ghost": {"count": float(p.ghost_count),
                         "energy_eV": float(p.ghost_energy_eV)},
        "thermal_electron_increment": float(p.absorbed_count),
        "thermal_U_increment_J": float(event.column.get("U_th", 0)),
        "separate_source_heat_eV": float(event.heat_eV),
        "chemical_or_excitation_reservoir_eV": float(event.reservoir_eV),
        "column_exact": {key: str(value) for key, value in event.column.items()},
    }
