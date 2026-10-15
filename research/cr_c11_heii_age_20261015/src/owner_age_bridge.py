"""Positive source-age quadrature with HeII species-resolved closure.

Exploratory supplier for rei_bianchi SOURCE07 C8. Source and background physics
are loaded read-only from the owner's pinned C8 Python reference. This module
does not update any owner chemistry, radiation, or Bianchi radiation state.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import linprog

FEATURE_NAMES = (
    "emitted_number", "physical_energy_eV",
    "HI_absorbed", "HeI_absorbed", "HeII_absorbed",
    "HI_heat_eV", "HeI_heat_eV", "HeII_heat_eV",
)
AGE_SOURCE_SHA = "f8a7d7ecbf7b839ef138c024384bed0fa16ec6889a332ef2ade2dc7c9d47b72b"
EMISSION_SOURCE_SHA = "43f7805703f08516b2b4b8e686b097b1c38e2140ac06b556e7de07159cf42b06"
SOURCE_AGE = Path("research/source07_c8_age_compression_20261015/experiment.py")
SOURCE_EMISSION = Path("research/source07_c1_baseline_20261014/q_emission_baseline.py")
SOURCE_SCENARIO = Path("research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json")
SCENARIO_SHA = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"


def source_identity(root: Path) -> dict[str, str]:
    """Do not run against silently changed owner formulas or constants."""
    paths = {"age": SOURCE_AGE, "emission": SOURCE_EMISSION, "scenario": SOURCE_SCENARIO}
    expected = {"age": AGE_SOURCE_SHA, "emission": EMISSION_SOURCE_SHA, "scenario": SCENARIO_SHA}
    actual = {k: hashlib.sha256((root / p).read_bytes()).hexdigest()
              for k, p in paths.items()}
    for k, h in actual.items():
        if h != expected[k]:
            raise ValueError(f"owner source changed: {paths[k]} expected {expected[k]} got {h}")
    return actual


def owner_namespace(root: Path) -> dict:
    """Same reference namespace extraction method as the owner's C8 multistate pilot."""
    root = Path(root)
    source_identity(root)
    f = root / SOURCE_AGE
    data = f.read_text()
    marker = "\nresults=[]\n"
    if data.count(marker) != 1:
        raise ValueError("unrecognized owner C8 reference layout")
    # The trusted user-owned file is executed through the same method as
    # research/source07_c8_multistate_20261015/experiment.py.
    ns = {"__file__": str(f), "__name__": "c8_external_reference"}
    exec(compile(data.split(marker)[0], str(f), "exec"), ns)
    return ns


def verner_sigma_array(E: np.ndarray, p: tuple) -> np.ndarray:
    """Vectorize the exact owner Verner fit; energy in eV, sigma in cm^2."""
    chi, e0, s0, ya, po, yw, y0, y1 = p
    x = np.asarray(E, dtype=float) / e0 - y0
    y = np.hypot(x, y1)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        fit = (s0 * ((x - 1.) ** 2 + yw * yw) *
               y ** (po / 2. - 5.5) * (1. + np.sqrt(y / ya)) ** (-po) * 1e-18)
    return np.where(np.asarray(E) < chi, 0., fit)


@dataclass
class EmissionPackets:
    age_starts: np.ndarray
    flux: np.ndarray
    physical_eV: np.ndarray
    sigma_cm2: np.ndarray
    bind_eV: np.ndarray
    dt_seconds: float
    c_cm_s: float

    @property
    def nage(self) -> int:
        return len(self.age_starts)

    def response(self, gases: np.ndarray) -> np.ndarray:
        """Fully vectorized, gas-batched reaction moments [gas, age, feature].

        No interpolated spectrum or fictitious child moments. Each age uses the
        actual owner threshold-split source quadrature sampled on its true nodes.
        All absorption is frozen-neutral and independent of subsequent gas evolution.
        """
        gas = np.asarray(gases, dtype=float)
        if gas.ndim != 2 or gas.shape[1] != 3 or not np.all(np.isfinite(gas)) or np.any(gas < 0):
            raise ValueError("gases must be finite nonnegative (nHI,nHeI,nHeII) in cm^-3")
        # optical depth per (packet, gas, species)
        tau_species = self.dt_seconds * self.c_cm_s * self.sigma_cm2[:, None, :] * gas[None, :, :]
        tau = np.sum(tau_species, axis=2)
        # Lim_{tau -> 0} (1-exp(-tau))/tau = 1.
        factor = np.ones_like(tau)
        np.divide(-np.expm1(-tau), tau, out=factor, where=tau > 0)
        absorption = tau_species * factor[:, :, None]
        # Every packet has 0 <= sum_j P(absorb_j) <= 1.
        per_packet = self.flux[:, None, None] * absorption
        photoheat = per_packet * (self.physical_eV[:, None, None] - self.bind_eV[None, None, :])
        sum_abs = np.add.reduceat(per_packet, self.age_starts, axis=0)
        sum_heat = np.add.reduceat(photoheat, self.age_starts, axis=0)
        n = np.add.reduceat(self.flux, self.age_starts)
        e = np.add.reduceat(self.flux * self.physical_eV, self.age_starts)
        out = np.zeros((len(gas), self.nage, len(FEATURE_NAMES)))
        out[:, :, 0] = n
        out[:, :, 1] = e
        out[:, :, 2:5] = sum_abs.transpose(1, 0, 2)
        out[:, :, 5:8] = sum_heat.transpose(1, 0, 2)
        return out


def make_packets(ns: dict, q: float, ages: np.ndarray) -> EmissionPackets:
    """Same 12-mu/16-E Gauss and exact threshold split as owner C8."""
    model, spec = ns["model"], ns["spec"]
    fit = ns["fit"]
    mu, wm = ns["mu"], ns["muw"]
    x, wx = ns["e_nodes"], ns["e_weights"]
    rp, rz = model.ratios(.2, float(q))
    f_list, e_list, s_list, starts = [], [], [], []
    packet_count = 0
    for age in ages:
        starts.append(packet_count)
        rpa, rza = model.ratios(float(age), float(q))
        rpx, rzx = rp / rpa, rz / rza
        for m, wmu in zip(mu, wm):
            scale = float(np.sqrt(rpx ** 2 * (1. - m ** 2) + rzx ** 2 * m ** 2))
            cuts = sorted(set([13.6, 100.] +
                [p[0] / scale for p in fit if 13.6 < p[0] / scale < 100.]))
            for lo, hi in zip(cuts, cuts[1:]):
                emit = (lo + hi) / 2 + (hi - lo) / 2 * x
                f = (wmu / 2 * (hi - lo) / 2) * wx * spec.phi(emit)
                energy = emit * scale
                sigma = np.column_stack([verner_sigma_array(energy, p) for p in fit])
                f_list.append(f)
                e_list.append(energy)
                s_list.append(sigma)
                packet_count += len(f)
    return EmissionPackets(
        age_starts=np.array(starts, dtype=int),
        flux=np.concatenate(f_list),
        physical_eV=np.concatenate(e_list),
        sigma_cm2=np.concatenate(s_list),
        bind_eV=np.asarray(ns["bind"], float),
        dt_seconds=float(ns["dt"]), c_cm_s=float(ns["C"]),
    )


def gas_states(ns: dict) -> tuple[np.ndarray, np.ndarray, list]:
    """H neutral fraction and HeII fraction are independent test coordinates."""
    nh, nhe = ns["nh"], ns["nhe"]
    train_labels = [(1.0, 0.0), (0.6, 0.25), (0.3, 0.8)]
    holdout_labels = [(a, b) for a in (.2, .4, .8, 1.) for b in (0., .1, .5, .9, 1.)]
    def state(p):
        xhi, xheii = p
        return (nh * xhi, nhe * (1. - xheii), nhe * xheii)
    return (np.asarray([state(x) for x in train_labels]),
            np.asarray([state(x) for x in holdout_labels]),
            holdout_labels)


def design_positive(weights: np.ndarray, tensor: np.ndarray, ntrain: int) -> np.ndarray:
    """Positive LP exact moment matching at selected training gas receivers."""
    nw = len(weights)
    raw = np.concatenate((np.ones((1, nw)),
                        *(tensor[j].T for j in range(ntrain))), axis=0)
    scale = np.maximum(np.max(np.abs(raw), axis=1), 1e-30)
    A = raw / scale[:, None]
    rhs = A @ weights
    result = linprog(np.linspace(0., 1., nw), A_eq=A, b_eq=rhs,
                     bounds=(0, None), method="highs",
                     options={"primal_feasibility_tolerance": 1e-10,
                              "dual_feasibility_tolerance": 1e-10})
    if not result.success:
        raise RuntimeError(f"positive LP failed: {result.message}")
    w = result.x
    if np.any(w < -1e-12) or abs(np.sum(w) - 1) > 1e-8:
        raise RuntimeError("positive source-age normalization/positivity failed")
    return np.maximum(w, 0.)


def errors(reference: np.ndarray, approx: np.ndarray) -> np.ndarray:
    """Small absolute floor only for zero reference observables."""
    return np.abs(reference - approx) / np.maximum(np.abs(reference), 1e-14)


def q_experiment(q: float, root: str, nstates: tuple[int, ...] = (1, 3)) -> dict:
    t0 = time.perf_counter()
    ns = owner_namespace(Path(root))
    ages = np.geomspace(ns["model"].ar, .2, 36)
    tr, ho, hold_labels = gas_states(ns)
    packets = make_packets(ns, q, ages)
    tensor = packets.response(np.vstack([tr, ho]))
    initial = np.ones(len(ages)) / len(ages)
    full = np.einsum("gaf,a->gf", tensor, initial)
    designs = {}
    for n in nstates:
        w = design_positive(initial, tensor, n)
        actual = np.einsum("gaf,a->gf", tensor, w)
        err = errors(full, actual)
        designs[str(n)] = {
            "retained_age_count": int(np.sum(w > 1e-9)),
            "weights": [[int(i), float(w[i])] for i in np.where(w > 1e-9)[0]],
            "training_max_error": float(np.max(err[:n])),
            "holdout_max_error": float(np.max(err[len(tr):])),
            "holdout_max_by_feature": np.max(err[len(tr):], axis=0).tolist(),
            "holdout_max_by_gas": np.max(err[len(tr):], axis=1).tolist(),
            "all_gas_max_abs_error_by_feature": np.max(np.abs(full-actual),axis=0).tolist(),
            "photon_budget_violation": float(max(0., np.max(np.sum(actual[:,2:5],axis=1)-actual[:,0]))),
            "min_weight": float(np.min(w)),
        }
    if np.any(tensor[:, :, 2:5] < -1e-15) or np.any(tensor[:, :, 5:8] < -1e-15):
        raise RuntimeError("negative absorption/heat moments")
    if np.any(tensor[:, :, 2:5].sum(axis=2) > tensor[:, :, 0] + 1e-12):
        raise RuntimeError("photo-absorption exceeds photon stock")
    return {
        "q_ref":q, "gas_coordinates": ["neutral_HI_fraction", "HeII_fraction_of_helium"],
        "holdout_coordinates":hold_labels, "feature_names":FEATURE_NAMES,
        "n_ages":len(ages), "n_packets":len(packets.flux),
        "full_reference_by_gas":full.tolist(),
        "designs":designs,
        "elapsed_seconds":time.perf_counter()-t0,
    }


def run(root: Path, workers: int, qs=(-.01, 0., .01)) -> dict:
    root = Path(root).resolve()
    src = source_identity(root)
    before = time.perf_counter()
    if workers == 1:
        rows = [q_experiment(float(q), str(root)) for q in qs]
    else:
        with ProcessPoolExecutor(max_workers=min(workers, len(qs)),
                                 mp_context=get_context("spawn")) as pool:
            rows = list(pool.map(q_experiment, [float(q) for q in qs],
                                 [str(root)] * len(qs)))
    return {
        "schema":"BASS_CR_TO_REI_SOURCE07_HEII_AGE_EXPLORATORY_V1",
        "source_sha256":src,
        "claim":"manufactured equal-weight ages, prescribed gas, photon/heat moments, NOT physical EoR history",
        "physics":{"gas":"proper cm^-3", "energy":"physical eV", "clock":"proper seconds",
                   "source":"normalized BB50k, 13.6-100eV original emission", "owner_J":"unchanged; applied externally, not by this reference"},
        "num_processes":workers,"wall_seconds":time.perf_counter()-before,
        "records":rows, "scientific_gate":"HOLD_NOT_ADMITTED",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rei-root",required=True,type=Path)
    parser.add_argument("--workers",type=int,choices=(1,2,3),default=1)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    result=run(args.rei_root,args.workers)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
        "wall_seconds":result["wall_seconds"],"processes":args.workers,
        "per_q":[{"q":r["q_ref"],"seconds":r["elapsed_seconds"],
            "designs":{k:{"retained":v["retained_age_count"],
                "max_holdout_error":v["holdout_max_error"]} for k,v in r["designs"].items()}}
                    for r in result["records"]]
    },indent=2))
