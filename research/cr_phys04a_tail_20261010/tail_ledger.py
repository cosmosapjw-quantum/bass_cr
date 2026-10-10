# SPDX-License-Identifier: GPL-3.0-only
"""CR-PHYS04a: a separate 4--10 MeV neutral-ionization tail ledger.

The source normalization, birth measure and Bianchi characteristics are the
existing CR-PHYS01 ones. Rudd primary binding and secondary kinetic energy are
partitioned by electron energy at the pinned FS10 table endpoint. Neither
partition is deposited as heat or routed into the production provider.

Final-proton boundaries are mapped back to birth energy by transport_population;
splitting there resolves the onset of above-table secondary electrons. The
unsplit option exists solely to preserve the first refinement failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "cr_phys01_20261010" / "src"
sys.path.insert(0, str(SOURCE))
from injection import EV_J, InjectionModel, transport_population  # noqa: E402
import rudd  # noqa: E402
from fs10 import FS10Table  # noqa: E402

SECONDARY_MAX_EV = 9937.21
PROTON_EDGES_EV = (4e6, 4567804.2094395505, 4572846.425549054, 1e7)
REFINEMENT_BOUND = 2e-6
MOMENT_KEYS = ("rate_m3_s", "binding_j_m3_s", "secondary_j_m3_s", "loss_j_m3_s")
BANDS = ("all", "within_table_energy", "above_table_energy")


def _empty_moments():
    return dict.fromkeys(MOMENT_KEYS, 0.0)


def _sum_moments(parts):
    return {key: math.fsum(part[key] for part in parts) for key in MOMENT_KEYS}


def _weighted_moments(kinetic, flux, target, lower, upper):
    if not len(kinetic):
        return _empty_moments()
    moments = rudd.cross_section_moments(kinetic, target, lower, upper)
    values = [float(np.dot(flux, moments[key])) * factor for key, factor in (
        ("sigma_m2", 1.0), ("binding_eV_m2", EV_J),
        ("secondary_eV_m2", EV_J), ("loss_eV_m2", EV_J))]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("NONFINITE_OR_NEGATIVE_TAIL_MOMENT")
    return dict(zip(MOMENT_KEYS, values))


def build_tail_ledger(energy_order=48, age_order=8, mu_order=8, *,
                      dt_s=1e10, enabled=True, split_protons=True):
    """Diagnose a fixed 100 K, xi=.01, Y=.248, nH=140/m^3 scenario.

    These are local end-population collision rates; no gas state or CR
    population is advanced with collisions. "within_table_energy" describes
    energy support only, and does not certify a terminal or causal cascade.
    """
    if type(split_protons) is not bool:
        raise ValueError("split_protons must be bool")
    model = InjectionModel(enabled=enabled)
    edges = PROTON_EDGES_EV if split_protons else (PROTON_EDGES_EV[0], PROTON_EDGES_EV[-1])
    n_h, y, xi = 140.0, .248, .01
    n_he = n_h * y / (4 * (1 - y))
    segments = []
    max_loss_rate_s = {target: 0.0 for target in rudd.TARGETS}
    for low, high in zip(edges[:-1], edges[1:]):
        population = transport_population(
            model, dt_s, 3.3e-17, 3.3e-18, collision_window_eV=(low, high),
            energy_order=energy_order, age_order=age_order, mu_order=mu_order)
        kinetic = population["nodes"]["kinetic_eV"]
        number = population["nodes"]["number_density_m3"]
        targets = {}
        for target, neutral_density in (("H", n_h*(1-xi)), ("He", n_he*(1-xi))):
            speed = rudd.proton_speed_m_s(kinetic) if len(kinetic) else kinetic
            flux = number * speed * neutral_density
            targets[target] = {
                "all": _weighted_moments(kinetic, flux, target, 0.0, None),
                "within_table_energy": _weighted_moments(
                    kinetic, flux, target, 0.0, SECONDARY_MAX_EV),
                "above_table_energy": _weighted_moments(
                    kinetic, flux, target, SECONDARY_MAX_EV,
                    # A common finite integration cap covers every model endpoint.
                    float(rudd.secondary_max_eV(PROTON_EDGES_EV[-1], target))),
            }
            if len(kinetic):
                loss = rudd.cross_section_moments(kinetic, target)["loss_eV_m2"]
                max_loss_rate_s[target] = max(max_loss_rate_s[target],
                    float(np.max(speed * neutral_density * loss / kinetic)))
        segments.append({"proton_window_eV": [low, high], "targets": targets,
                         "population_node_count": len(kinetic),
                         "active_cr_energy_j_m3": population["budgets"]["active_CR_energy_J_m3"]})
    totals = {target: {band: _sum_moments([segment["targets"][target][band]
                                       for segment in segments])
                      for band in BANDS} for target in rudd.TARGETS}
    combined = {band: _sum_moments([totals[target][band] for target in rudd.TARGETS])
                for band in BANDS}
    return {
        "schema": "cr-phys04a-tail-ledger.v1", "solver_intervals": 0,
        "scope": "INSTANTANEOUS_NEUTRAL_IONIZATION_TAIL_DIAGNOSTIC",
        "deposition_status": "NOT_COMPUTED", "causal_history_status": "HOLD",
        "source": model.metadata(),
        "gas": {"n_h_m3": n_h, "n_he_m3": n_he, "xi": xi,
                "temperature_k": 100.0, "y_he_mass_fraction": y},
        "background": population["background"],
        "orders": [energy_order, age_order, mu_order],
        "proton_edges_eV": list(edges), "secondary_split_eV": SECONDARY_MAX_EV,
        "segments": segments, "targets": totals, "combined": combined,
        "active_cr_energy_j_m3": math.fsum(s["active_cr_energy_j_m3"] for s in segments),
        "sampled_fractional_ionization_loss_age_estimate":
            math.fsum(max_loss_rate_s.values()) * float(dt_s),
        "loss_estimate_semantics": "sum of final-node maxima times age; not a trajectory supremum or certified bound",
        "ledger_semantics": "primary binding + secondary kinetic = ionization loss; both secondary bands remain unallocated, never heat",
        "unmodelled": ["other stopping channels", "protons outside 4..10 MeV",
                       "secondary delay and deposition", "collision feedback"],
    }


def refinement(coarse, fine):
    """Every target/band/moment, with the fine value as relative denominator."""
    differences = {}
    for target in rudd.TARGETS:
        for band in BANDS:
            for key in MOMENT_KEYS:
                a, b = coarse["targets"][target][band][key], fine["targets"][target][band][key]
                differences[f"{target}/{band}/{key}"] = abs(a-b)/abs(b) if b else (0.0 if a == b else math.inf)
    maximum = max(differences.values())
    return {"status": "PASS_SCOPED" if maximum <= REFINEMENT_BOUND else "FAIL",
            "bound": REFINEMENT_BOUND, "maximum_relative_difference": maximum,
            "differences": differences}


def source_identity():
    table = FS10Table(.01)
    if float(table.energy_eV[-1]) != SECONDARY_MAX_EV:
        raise ValueError("FS10_ENDPOINT_IDENTITY_MISMATCH")
    paths = [SOURCE / "injection.py", SOURCE / "rudd.py", SOURCE / "fs10.py",
             SOURCE.parent / table.relative_path, Path(__file__), HERE / "CONTRACT.json"]
    return {str(path.relative_to(HERE.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def validation_campaign():
    started = time.perf_counter()
    cpu = time.process_time()
    results = {}
    for name, split in (("raw_unsplit", False), ("repaired_split", True)):
        coarse = build_tail_ledger(48, 8, 8, split_protons=split)
        fine = build_tail_ledger(64, 12, 12, split_protons=split)
        results[name] = {"coarse": coarse, "fine": fine, "refinement": refinement(coarse, fine)}
    return {"contract": "CR-PHYS04a-TAIL-LEDGER", "source_sha256": source_identity(),
            "python": platform.python_version(), "numpy": np.__version__,
            "command": " ".join(sys.argv), "results": results,
            "measured_wall_s": time.perf_counter()-started,
            "measured_process_cpu_s": time.process_time()-cpu,
            "scientific_scope": "finite quadrature diagnostic; no continuum bound or physical-history admission"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", action="store_true", help="preserve unsplit FAIL and split refinement")
    parser.add_argument("--output", type=Path, help="write generated JSON evidence; otherwise print")
    args = parser.parse_args()
    result = validation_campaign() if args.validation else build_tail_ledger()
    output = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("output already exists; choose a new evidence path")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    else:
        print(output, end="")
    if args.validation and result["results"]["repaired_split"]["refinement"]["status"] != "PASS_SCOPED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
