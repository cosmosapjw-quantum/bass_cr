"""Bind existing C23B atoms and C23E signed events without replaying their science."""
from __future__ import annotations

import csv
import io
import json
from math import fsum
from pathlib import Path

from contracts import (EV_J, ContractError, Domain, Event, EventBook, IsotopeMapping,
                       NativeMeasure, Scaling, SourcePin, Species, normalize)

BASE = "8d0a5c375589fbddadc2bb90c8117311c80bad09"
C23E_HEAD = "8623d7b2035677fc231976d85fea309f48afd57c"
B = "research/cr_c23b_source_frame_20261023/source_providers/runs/c23b_pw19_spectral_source_20261023_v1/"
E = "research/cr_c23e_d43_source_binding_20261024/runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1/"
PINS = {
    "atoms": SourcePin("cosmosapjw-quantum/bass_cr", BASE, B + "photoelectron_atoms.csv",
                       "f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3"),
    "cases": SourcePin("cosmosapjw-quantum/bass_cr", BASE, B + "CASES.json",
                       "82113ce0eaf0b706ab4daa2e1775f51df6470001db018f851a4dbd98856c4511"),
    "c23e_events": SourcePin("cosmosapjw-quantum/bass_cr", C23E_HEAD, E + "POINT_SOURCES.json",
                       "ac837c52b633b672bc654e5562026082143b96e0cf0a7c352d8da568dfb9f8c2"),
}
Z = (2.316, 2.479, 2.649)
THRESHOLD = {"HI": 13.60, "HeI": 24.59, "HeII": 54.42}
# Prescribed snapshot matches the existing N5 bath. No density evolution.
DENSITY_CM3 = {"HI": 0.9, "HeI": 0.07, "HeII": 0.02}
LABELS = {"HI": ("H1:0", "H1:1", "H1", 0),
          "HeI": ("He4:0", "He4:1", "He4", 0),
          "HeII": ("He4:1", "He4:2", "He4", 1)}
E_FAST = Species("e:fast", -1, ())
E_THERMAL = Species("e:thermal", -1, ())
PHOTON = Species("photon", 0, ())


def relative(a: float, b: float) -> float:
    scale = max(abs(a), abs(b))
    return abs(a - b) / scale if scale else 0.0


def consume_c23b(root: Path) -> dict:
    raw = PINS["atoms"].verify(root)
    cases = json.loads(PINS["cases"].verify(root))
    grouped = {(z, c): ([], []) for z in Z for c in THRESHOLD}
    for row in csv.DictReader(io.StringIO(raw.decode())):
        key = (float(row["redshift"]), row["channel"])
        if key not in grouped:
            raise ContractError("unadmitted epoch/channel in pinned atoms")
        grouped[key][0].append(float(row["kinetic_eV"]))
        grouped[key][1].append(float(row["number_weight_per_target_s"]))
    saved = {(c["redshift"], c["channel"]): c for c in cases}
    if set(saved) != set(grouped):
        raise ContractError("saved source cases do not match atomic measure")
    out, books = [], {z: EventBook("bath_frame_rest_target") for z in Z}
    for (z, channel), (energy, weights) in grouped.items():
        i = THRESHOLD[channel]
        target, ion, nucleus, charge = LABELS[channel]
        mapping = IsotopeMapping(channel, target, "CONDITIONAL_ELEMENTAL_ASSIGNMENT",
                                 "PR105 conditional H1/He4 source assignment; no empirical isotope resolution")
        mapping.require(channel, target)
        Domain("kinetic", (0.0, 50000.0 - i), Z, "bath_frame_rest_target", "isotropic",
               "stationary_heavy_target_zero_recoil").require(
            energy_coordinate="kinetic", energies_eV=tuple(energy), redshift=z,
            frame="bath_frame_rest_target", angular="isotropic",
            mass_model="stationary_heavy_target_zero_recoil")
        native = NativeMeasure(f"C23B:{z}:{channel}", "electron", "e:fast", "kinetic",
                               510998.95069, tuple(energy), tuple(weights),
                               "per_target_per_proper_s", "bath_frame_rest_target", "isotropic")
        source = normalize(native, Scaling(target_density_m3=DENSITY_CM3[channel] * 1e6))
        m = source.moments()
        old = saved[z, channel]["result"]
        checks = {
            "count_relative": relative(m["number_m3_s"], old["number_per_target_s"] * DENSITY_CM3[channel] * 1e6),
            "kinetic_relative": relative(m["coordinate_energy_J_m3_s"], old["kinetic_eV_per_target_s"] * DENSITY_CM3[channel] * 1e6 * EV_J),
        }
        if max(checks.values()) > 2e-14:
            raise ContractError("saved source/SI transfer differs beyond inherited source ledger tolerance")
        mean_k = m["coordinate_energy_J_m3_s"] / m["number_m3_s"]
        event = Event(source.native.source_id, "C23B_PW19_VERNER_GROUND_50KEV", "C23B_immutable_source",
                      "bass_cr_external_source_consumer", m["number_m3_s"],
                      ((Species(target, charge, ((nucleus, 1),)), -1),
                       (Species(ion, charge + 1, ((nucleus, 1),)), 1), (E_FAST, 1), (PHOTON, -1)),
                      (("binding", i * EV_J), ("thermal_kinetic", 0.0), ("fast_kinetic", mean_k),
                       ("radiation", -fsum((i * EV_J, mean_k))), ("recoil", 0.0),
                       ("escaped", 0.0), ("external", 0.0)), "bath_frame_rest_target", "photoionization")
        validation = books[z].append(event)
        out.append({"z": z, "channel": channel, "source_atoms": len(weights),
                    "target_species": target, "isotope_status": mapping.status,
                    "target_density_cm3": DENSITY_CM3[channel], "source_moments_SI": m,
                    "source_transfer_checks": checks, "event_validation": validation,
                    "native_threshold_eV": i, "frame": source.native.frame,
                    "finite_mass_status": "STATIONARY_HEAVY_TARGET_ZERO_RECOIL",
                    "physical_heating": None, "irreversible_assimilation": False})
    return {"source_atoms_consumed": sum(len(x[0]) for x in grouped.values()), "cases": out,
            "per_epoch_energy_rates_J_m3_s": {str(z): book.energy_rates() for z, book in books.items()},
            "new_source_quadrature": 0, "new_ODE": 0}


def species(name: str) -> Species:
    nuclide, charge = name.split(":")
    return Species(name, int(charge), ((nuclide, 1),))


def consume_c23e(root: Path) -> dict:
    """C23E already owns target/electron density; only units and ledger representation change."""
    rows = json.loads(PINS["c23e_events"].verify(root))
    output, all_errors = [], []
    for row in rows:
        if row["z"] not in Z or row["T"] not in (43.0, 300.0, 10000.0) or row["fast_fraction"] not in (0.0, 0.1):
            raise ContractError("unexpected saved C23E context")
        book = EventBook("bath_frame_rest_target")
        validations = []
        for r in row["events"]:
            rate = abs(r["rate"])
            if rate == 0:
                raise ContractError("zero event needs an explicit unscaled stoichiometric template")
            number_rows = tuple((species(k), v / rate) for k, v in r["net"].items())
            number_rows += ((E_THERMAL, r["thermal_e"] / rate), (E_FAST, r["fast_e"] / rate))
            flow = {"binding": r["bind"], "thermal_kinetic": r["thermal"], "fast_kinetic": r["fast"],
                    "radiation": -r["absorbed"], "recoil": 0.0, "escaped": r["escaped"], "external": 0.0}
            event = Event(f"C23E:{row['z']}:{row['T']}:{row['fast_fraction']}:{r['id']}",
                          "C23E_D43_CONDITIONAL_PI_RR_CX", "WU79+C23B+C22A_as_bound_by_C23E",
                          "bass_cr_external_source_consumer", rate * 1e6, number_rows,
                          tuple((k, v / rate * EV_J) for k, v in flow.items()), "bath_frame_rest_target",
                          "photoionization" if r["id"].endswith("_PI") else
                          "radiative_recombination" if r["id"].endswith("_RR") else "charge_exchange")
            validations.append(book.append(event))
        totals = book.energy_rates()
        old_keys = {"binding": "bind", "thermal_kinetic": "thermal", "fast_kinetic": "fast",
                    "radiation": "absorbed", "escaped": "escaped"}
        # Signed cancellation is compared to the original sum of absolute event terms.
        errors = {}
        for key, old_key in old_keys.items():
            sign = -1.0 if key == "radiation" else 1.0
            expected = sign * row["totals"][old_key] * 1e6 * EV_J
            scale = fsum(abs(r[old_key]) for r in row["events"]) * 1e6 * EV_J
            errors[key] = abs(totals[key] - expected) / scale if scale else abs(totals[key] - expected)
        if max(errors.values()) > 2e-13:
            raise ContractError("C23E signed-event transfer fails frozen2e-13 criterion")
        all_errors.extend(errors.values())
        output.append({"z": row["z"], "T_K": row["T"], "fast_fraction": row["fast_fraction"],
                       "event_count": len(validations), "energy_rates_J_m3_s": totals,
                       "max_transfer_error_normalized": max(errors.values()),
                       "isotope_model": "D43K_THRESHOLD_GATE_SHARED_H_RR_CONDITIONAL",
                       "momentum_status": "SCALAR_ENSEMBLE_ONLY"})
    if len(rows) != 18:
        raise ContractError("C23E saved point count changed")
    return {"saved_points_consumed": len(rows), "saved_events_consumed": sum(x["event_count"] for x in output),
            "max_transfer_error_normalized": max(all_errors), "points": output,
            "new_C23E_source_evaluations": 0, "new_rate_evaluations": 0, "new_ODE": 0}


def consume_all(root: Path) -> dict:
    return {"schema": "CR_EXTERNAL_SOURCE_SAVED_CONSUMER_RESULT_V1",
            "status": "IMPLEMENTATION_VERIFIED_SCOPED_SOURCE_AND_EVENT_CONSUMER",
            "C23B": consume_c23b(root), "C23E": consume_c23e(root),
            "full_external_physics_coverage": "PARTIAL_INPUT_DEPENDENCIES",
            "N6": "PREDECESSOR_GATED", "N7": "PREDECESSOR_GATED",
            "global_error_bound": None, "global_completion_percent": None}
