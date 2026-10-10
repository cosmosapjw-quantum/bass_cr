"""Frozen continuous first-crossing source into independent age cohorts.

Each evolution carries two residual-energy columns. Observables are evaluated
on each cohort's instantaneous characteristic grid before quadrature summation.
Upstream NIST excitation and downstream old-method excitation stay separate.
"""
from pathlib import Path
import importlib.util
import sys
import math
import time
import numpy as np

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("continuous_adapter", ROOT.parent / "cr_phys02c_cohort_adapter_20261010/cohort_adapter.py")
A = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = A
spec.loader.exec_module(A)
P = A.P
E0 = 1000.001
RESIDUAL = np.array([989.797, 978.783])
UPSTREAM_DELTA = np.array([10.204, 21.218])
T = 1e10
BRANCHES = ("HI_NIST_2p", "HeI_NIST_singlet")
OBSERVABLES = ("active_electron_number", "active_energy_eV", "ionization_counts",
               "binding_energy_eV", "excitation_counts", "excitation_energy_by_species_eV",
               "coulomb_heat_eV", "cutoff_electron_number", "cutoff_energy_eV")
ENERGIES = ("active_energy_eV", "binding_energy_eV", "excitation_energy_by_species_eV",
            "coulomb_heat_eV", "cutoff_energy_eV")


def source(time_s, enabled=True):
    if not np.isfinite(time_s) or not 0 <= time_s <= T:
        raise ValueError("SOURCE_TIME_DOMAIN")
    rates = A.F.K.rates(E0) if enabled else np.zeros(2)
    total = float(rates.sum())
    survival = math.exp(-total * time_s)
    cumulative = rates / total * -math.expm1(-total * time_s) if total else np.zeros(2)
    return rates * survival, cumulative, survival


def panels(g):
    return np.unique(np.r_[0., T, (T-P.cooling_time(g.grid, g.gas))[
        (P.cooling_time(g.grid, g.gas) > 0) & (P.cooling_time(g.grid, g.gas) < T)]])


def cohort_observables(g, state, column):
    # Slicing CharacteristicState preserves its own energy_grid metadata.
    obs = g.observe(state[:, column])
    obs["excitation_energy_by_species_eV"] = (P.EXC * np.asarray(obs["excitation_counts"])).tolist()
    return {key: np.asarray(obs[key], dtype=float) for key in OBSERVABLES}


def fresh_initial(g):
    # Project anew for each grid; accumulated low-energy counters start at zero.
    return np.column_stack([g.impulse(e) for e in RESIDUAL])


def integrate(intervals, order, method="sparse", enabled=True, receiver=True,
              call_cap=None, wall_limit=1800., cpu_limit=3600., progress=None):
    A.verify_inputs()
    g = P.assemble(intervals, gas=P.Gas())
    cuts = panels(g)
    expected = (len(cuts)-1)*order
    if call_cap is not None and expected > call_cap:
        raise RuntimeError("HOLD_CALL_BUDGET_PREFLIGHT")
    initial = fresh_initial(g)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    obs = [{key: np.zeros_like(cohort_observables(g, initial, j)[key])
            for key in OBSERVABLES} for j in range(2)]
    integrated_source = np.zeros(2)
    calls = 0
    wall0, cpu0 = time.monotonic(), time.process_time()
    maximum_steps = 0
    for left, right in zip(cuts[:-1], cuts[1:]):
        for x, w in zip(nodes, weights):
            if time.monotonic()-wall0 > wall_limit or time.process_time()-cpu0 > cpu_limit:
                raise RuntimeError("HOLD_EXECUTION_BUDGET")
            birth = .5*(left+right)+.5*(right-left)*x
            age = A.age_at(T, birth)
            rate, _, _ = source(birth, enabled)
            mass = .5*(right-left)*w*rate
            if method == "ssprk2":
                steps = max(128, math.ceil(age*g.rho/.2))
                if steps > 256:
                    raise RuntimeError("HOLD_SSPRK2_STEP_CAP")
                maximum_steps = max(maximum_steps, steps)
                state = P.evolve(g, initial, age, enabled=receiver,
                                 steps=steps, method="ssprk2")
            else:
                state = P.evolve(g, initial, age, enabled=receiver)
            calls += 1
            if progress is not None:
                progress(calls, time.monotonic()-wall0, time.process_time()-cpu0)
            if not np.all(np.isfinite(state)) or np.min(state) < 0:
                raise RuntimeError("HOLD_NONFINITE_OR_NEGATIVE")
            integrated_source += mass
            for j in range(2):
                current = cohort_observables(g, state, j)
                for key in OBSERVABLES:
                    obs[j][key] += mass[j]*current[key]
    _, cumulative, survival = source(T, enabled)
    branch_ledger = []
    for j in range(2):
        n = obs[j]["active_electron_number"] + obs[j]["cutoff_electron_number"] - np.sum(obs[j]["ionization_counts"])
        energy = sum(np.sum(obs[j][key]) for key in ENERGIES)
        branch_ledger.append({"number":float(n), "energy_eV":float(energy),
            "expected_number":float(cumulative[j]), "expected_energy_eV":float(RESIDUAL[j]*cumulative[j])})
    total = {key:obs[0][key]+obs[1][key] for key in OBSERVABLES}
    total_number = survival + sum(b["number"] for b in branch_ledger)
    total_energy = E0*survival + sum(b["energy_eV"] for b in branch_ledger) + float(UPSTREAM_DELTA@cumulative)
    return {"intervals":intervals,"order":order,"method":method,"panels":len(cuts)-1,
        "panel_edges_s":cuts.tolist(),"calls":calls,"columns_per_call":2,
        "maximum_steps":maximum_steps,"wall_s":time.monotonic()-wall0,
        "cpu_s":time.process_time()-cpu0,"branches":[{k:v.tolist() for k,v in o.items()} for o in obs],
        "total":{k:v.tolist() for k,v in total.items()},"integrated_source":integrated_source.tolist(),
        "analytic_C":cumulative.tolist(),"survival":survival,
        "upstream_excitation_energy_eV":(UPSTREAM_DELTA*cumulative).tolist(),
        "branch_ledgers":branch_ledger,"total_number_ledger":float(total_number),
        "total_energy_ledger_eV":float(total_energy),"Ucross_eV":float(RESIDUAL@cumulative)}
