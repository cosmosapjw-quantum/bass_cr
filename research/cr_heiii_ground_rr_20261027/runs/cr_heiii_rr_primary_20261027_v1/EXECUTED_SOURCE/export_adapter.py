"""Integrated He4III -> He4II return; no rate, exposure, spectrum or state update.

The seven signed energy reservoirs share one integrated event count.  Retained
photons have their own port; native w_ext keeps its external-transfer meaning.
This module deliberately does not construct the rate-valued external Event API.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re

EV_J = 1.602176634e-19
I_EV = 54.42
ENERGY_RTOL = 2e-13
FRAME = "bath_frame_rest_target"
UNIT = "CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1"
THEORY_SHA = "3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae"
TABLE_SHA = "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389"
PROVIDER_SHA = "71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d"
SOURCE_COMMIT = "b11b2e9255f2b10fb5582376412e045bd1e9151c"
RESERVOIRS = ("binding", "thermal_kinetic", "fast_kinetic", "radiation",
              "recoil", "escaped", "external")
STOICHIOMETRY = {"He4:2": -1, "He4:1": 1, "e:fast": -1, "photon": 1}


class ExportError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ExportError(message)


def number(value, label, *, nonnegative=False, positive=False):
    need(not isinstance(value, bool) and isinstance(value, (int, float)),
         label + ": EXPLICIT_REAL_REQUIRED")
    value = float(value)
    need(math.isfinite(value) and (not nonnegative or value >= 0)
         and (not positive or value > 0), label + ": FINITE_DOMAIN_REQUIRED")
    return value


def closed(values, label):
    values = tuple(number(x, label) for x in values)
    residual, scale = math.fsum(values), math.fsum(abs(v) for v in values)
    need(abs(residual) <= ENERGY_RTOL * scale, label + ": ENERGY_CLOSURE")
    return residual


def validate_qualification(q):
    need(type(q) is dict, "EXPLICIT_SOURCE_QUALIFICATION_REQUIRED")
    required = {
        "source_contract": UNIT,
        "source_commit": SOURCE_COMMIT,
        "native_channel": "HeII", "native_threshold_eV": I_EV,
        "native_maximum_eV": 50000.0,
        "table_sha256": TABLE_SHA, "provider_sha256": PROVIDER_SHA,
        "theory_sha256": THEORY_SHA,
        "isotope_assignment": "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
        "component": "ground_spontaneous_only",
        "mass_model": "stationary_heavy_target_zero_recoil",
        "angular_scope": "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
        "review_decision": "PASS_SCOPED_AFTER_TARGETED_REPAIR",
    }
    need(all(q.get(k) == v for k, v in required.items()), "SOURCE_QUALIFICATION_MISMATCH")
    for key in ("review_sha256", "native25_map_sha256", "input_manifest_sha256"):
        need(isinstance(q.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", q[key]),
             "SOURCE_REVIEW_PIN_REQUIRED:" + key)
    need(q.get("review_path") == "review/R6_THEORY.json", "SOURCE_REVIEW_PATH_REQUIRED")
    need(q.get("native25_map_path") == "intake/HEIII_NATIVE25_MAP_R5.json",
         "NATIVE25_MAP_PATH_REQUIRED")
    return q


def qualification(config, manifest, review, manifest_sha256):
    """Construct a qualification only after engine.verify binds these bytes."""
    authorities = {v["path"]: v for v in manifest["authority_files"]}
    need(review.get("reviewed_final_THEORY_sha256", review.get("identity", {}).get(
        "reviewed_final_THEORY_sha256")) == THEORY_SHA, "REVIEWED_THEORY_IDENTITY")
    q = {
        "source_contract": UNIT, "source_commit": SOURCE_COMMIT,
        "native_channel": "HeII", "native_threshold_eV": I_EV,
        "native_maximum_eV": 50000.0, "table_sha256": TABLE_SHA,
        "provider_sha256": PROVIDER_SHA, "theory_sha256": THEORY_SHA,
        "isotope_assignment": config["isotope_assignment"],
        "component": config["component"],
        "mass_model": "stationary_heavy_target_zero_recoil",
        "angular_scope": "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
        "review_decision": review["decision"],
        "review_path": "review/R6_THEORY.json",
        "review_sha256": authorities["review/R6_THEORY.json"]["sha256"],
        "native25_map_path": "intake/HEIII_NATIVE25_MAP_R5.json",
        "native25_map_sha256": authorities["intake/HEIII_NATIVE25_MAP_R5.json"]["sha256"],
        "input_manifest_sha256": manifest_sha256,
    }
    return validate_qualification(q)


def canonical_id(input_id, case, z):
    need(all(isinstance(x, str) and x for x in (input_id, case, z)),
         "CANONICAL_INPUT_CASE_SOURCE_ID_REQUIRED")
    payload = {"unit": UNIT, "input_id": input_id, "case": case, "z": z,
               "channel": "He4III+e:fast->He4II(1s)+photon"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "heiii-integrated-" + hashlib.sha256(raw).hexdigest()


def per_event_template(kinetic_eV, frame, source_qualification):
    validate_qualification(source_qualification)
    need(frame == FRAME, "EXPLICIT_ADMITTED_FRAME_REQUIRED")
    if kinetic_eV is None:
        energy = None
    else:
        kinetic_eV = number(kinetic_eV, "event kinetic energy", positive=True)
        need(kinetic_eV + I_EV <= 50000, "NATIVE_PI_SUPPORT_REQUIRED")
        energy = {k: 0.0 for k in RESERVOIRS}
        energy.update(binding=-I_EV * EV_J, fast_kinetic=-kinetic_eV * EV_J,
                      radiation=(kinetic_eV + I_EV) * EV_J)
        closed(energy.values(), "per event")
    return {
        "process": "radiative_recombination", "initial_ion": "He4III",
        "final_ion": "He4II", "final_state": "1s ground",
        "number_per_event": dict(STOICHIOMETRY),
        "energy_J_per_event": energy,
        "conditional_mean_kinetic_eV": kinetic_eV,
        "energy_representation": "MOMENT_EQUIVALENT_NOT_MONOENERGETIC_SPECTRUM"
        if kinetic_eV is not None else "UNDEFINED_ZERO_COUNT",
        "frame": frame, "physical_heating_J_per_event": None,
        "thermal_source_in_selected_model_J_per_event": 0.0,
    }


def integrated_event(*, input_id, case, z, count_cm3, kinetic_eV_cm3,
                     frame, source_qualification, nb_m3=None):
    """Make one event from integrated zeroth/first moments, without a time factor."""
    n = number(count_cm3, "integrated count cm^-3", nonnegative=True)
    u = number(kinetic_eV_cm3, "integrated kinetic eV cm^-3", nonnegative=True)
    need((n == 0 and u == 0) or (n > 0 and u > 0), "ZERO_COUNTERPART_REQUIRED")
    n_si = number(n * 1e6, "integrated count m^-3", nonnegative=True)
    u_si = number(u * (1e6 * EV_J), "integrated kinetic J m^-3", nonnegative=True)
    photon = number((u + I_EV * n) * (1e6 * EV_J), "retained energy", nonnegative=True)
    mean = u / n if n else None
    template = per_event_template(mean, frame, source_qualification)
    energy = {key: 0.0 for key in RESERVOIRS}
    energy.update(binding=-I_EV * n * (1e6 * EV_J), fast_kinetic=-u_si,
                  radiation=photon)
    closed(energy.values(), "integrated event")
    native = None
    a = wp = None
    if nb_m3 is not None:
        nb_m3 = number(nb_m3, "explicit nb_m3", positive=True)
        a, wp = n_si / nb_m3, photon / nb_m3
        delta = [0.0] * 25
        delta[11], delta[12], delta[21], delta[22] = a, -a, -a, -u_si / nb_m3
        need(all(math.isfinite(v) for v in delta) and math.isfinite(wp),
             "FINITE_NATIVE_PROJECTION_REQUIRED")
        native = {"nb_m3": nb_m3, "delta": delta,
                  "basis": "Y[21],zeta,w_nt,w_ext,logT",
                  "binding_owner": "native ionization-energy vector with DeltaY",
                  "thermal_electron_count_delta_per_baryon": 0.0,
                  "thermal_particle_count_delta_per_baryon": 0.0,
                  "state_update_applied": False}
    event = {
        "schema": "CR_HEIII_INTEGRATED_EVENT_V1",
        "canonical_event_id": canonical_id(input_id, case, z),
        "input_id": input_id, "case": case, "z": z,
        "source_id": "saved-PR104:" + case + ":z=" + z,
        "frame": frame, "source_qualification": deepcopy(source_qualification),
        "per_event_template": template,
        "integrated_count_m3": n_si, "integrated_energy_J_m3": energy,
        "density_delta_m3": {k: v * n_si for k, v in STOICHIOMETRY.items()},
        "native25": native,
        "retained_photon_port": {
            "integrated_count_m3": n_si, "integrated_energy_J_m3": photon,
            "count_per_baryon": a, "energy_J_per_baryon": wp,
            "native_w_ext_owner": False,
        },
        "event_rate_m3_s": None, "exposure_s": None, "instantaneous_rhs": None,
        "emission_time_history": None, "emission_spectrum": None,
        "physical_heating_J_m3": None, "irreversible_assimilation": False,
        "thermal_source_in_selected_model_J_m3": 0.0,
        "normalization": "INTEGRATED_PER_PROPER_VOLUME",
        "finite_coupled_abundance_update": False,
    }
    validate_event(event)
    return event


def validate_event(event):
    need(type(event) is dict and event.get("schema") == "CR_HEIII_INTEGRATED_EVENT_V1",
         "TYPED_INTEGRATED_EVENT_REQUIRED")
    validate_qualification(event.get("source_qualification"))
    need(event.get("frame") == FRAME, "EXPLICIT_ADMITTED_FRAME_REQUIRED")
    need(event.get("canonical_event_id") == canonical_id(event.get("input_id"),
         event.get("case"), event.get("z")), "CANONICAL_EVENT_ID_MISMATCH")
    need(event.get("source_id") == "saved-PR104:" + event["case"] + ":z=" + event["z"],
         "SOURCE_ID_MISMATCH")
    for name in ("event_rate_m3_s", "exposure_s", "instantaneous_rhs",
                 "emission_time_history", "emission_spectrum", "physical_heating_J_m3"):
        need(name in event and event[name] is None, "INTEGRATED_NOT_RATE_OR_HEATING:" + name)
    need(event.get("irreversible_assimilation") is False
         and event.get("finite_coupled_abundance_update") is False,
         "UNQUALIFIED_PHYSICAL_PROMOTION")
    n = number(event["integrated_count_m3"], "integrated count", nonnegative=True)
    need(event["density_delta_m3"] == {k: v * n for k, v in STOICHIOMETRY.items()},
         "HEIII_NATIVE_STOICHIOMETRY")
    energy = event["integrated_energy_J_m3"]
    need(type(energy) is dict and set(energy) == set(RESERVOIRS), "EXACT_ENERGY_OWNERS_REQUIRED")
    for name in RESERVOIRS:
        number(energy[name], "energy:" + name)
    need(all(energy[k] == 0 for k in ("thermal_kinetic", "recoil", "escaped", "external")),
         "UNSUPPLIED_ENERGY_PROCESS")
    need(energy["binding"] <= 0 and energy["fast_kinetic"] <= 0 and energy["radiation"] >= 0,
         "RR_ENERGY_SIGNS")
    closed(energy.values(), "integrated validation")
    closed((energy["binding"], I_EV * EV_J * n), "binding ownership")
    u = -energy["fast_kinetic"]
    need((n == 0 and u == 0) or (n > 0 and u > 0), "ZERO_COUNTERPART_REQUIRED")
    if n == 0:
        need(all(v == 0 for v in energy.values()), "ZERO_EVENT_ENERGY_REQUIRED")
    template = event["per_event_template"]
    mean = u / (EV_J * n) if n else None
    expected = per_event_template(mean, event["frame"], event["source_qualification"])
    need(template["number_per_event"] == expected["number_per_event"]
         and template["frame"] == event["frame"], "TEMPLATE_IDENTITY")
    if n:
        actual_mean = number(template["conditional_mean_kinetic_eV"], "conditional mean", positive=True)
        closed((actual_mean, -mean), "conditional moment representation")
        need(set(template["energy_J_per_event"]) == set(RESERVOIRS), "TEMPLATE_ENERGY_OWNERS")
        for key in RESERVOIRS:
            closed((template["energy_J_per_event"][key] * n, -energy[key]),
                   "event-to-integrated:" + key)
    else:
        need(template["conditional_mean_kinetic_eV"] is None
             and template["energy_J_per_event"] is None, "ZERO_CONDITIONAL_MUST_BE_NULL")
    port = event["retained_photon_port"]
    need(port["integrated_count_m3"] == n and port["integrated_energy_J_m3"] == energy["radiation"]
         and port["native_w_ext_owner"] is False, "RETAINED_PHOTON_PORT_IDENTITY")
    native = event["native25"]
    if native is None:
        need(port["count_per_baryon"] is None and port["energy_J_per_baryon"] is None,
             "NO_IMPLICIT_BARYON_NORMALIZATION")
    else:
        nb = number(native["nb_m3"], "explicit nb_m3", positive=True)
        a, delta = n / nb, [0.0] * 25
        delta[11], delta[12], delta[21], delta[22] = a, -a, -a, -u / nb
        need(native["delta"] == delta and native.get("state_update_applied") is False,
             "NATIVE25_INTEGRATED_PROJECTION")
        need(port["count_per_baryon"] == a and port["energy_J_per_baryon"] == energy["radiation"] / nb,
             "NATIVE_RETAINED_PHOTON_PORT")
    return {"energy_residual_J_m3": math.fsum(energy.values()),
            "charge_residual": 0.0, "He4_nuclei_residual": 0.0,
            "thermal_count_delta": 0.0, "energy_rtol": ENERGY_RTOL}


class IntegratedBook:
    """One scenario only; case/grid/epoch alternatives must never be summed."""
    def __init__(self, frame, *, case, z):
        need(frame == FRAME, "EXPLICIT_ADMITTED_FRAME_REQUIRED")
        need(isinstance(case, str) and case and isinstance(z, str) and z,
             "EXPLICIT_SCENARIO_REQUIRED")
        self.frame, self.case, self.z = frame, case, z
        self._ids, self.events = set(), []

    def append(self, event):
        need(event.get("frame") == self.frame, "INTEGRATED_BOOK_FRAME_MISMATCH")
        need((event.get("case"), event.get("z")) == (self.case, self.z),
             "ALTERNATIVE_SCENARIOS_NOT_ADDITIVE")
        validate_event(event)
        key = event["canonical_event_id"]
        need(key not in self._ids, "DUPLICATE_CANONICAL_INTEGRATED_EVENT")
        self._ids.add(key)
        self.events.append(deepcopy(event))
