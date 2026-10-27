"""Proper-time source and return ports for a fixed physical-volume cell.

This module performs finite algebraic changes of measure and polynomial-history
integrals. It contains no collision solver, source quadrature, spectral inversion,
or thermalization model. All energies are eV on input and joules at the native25
boundary. Source histories use coefficients in *native clock elapsed from each
segment start*. Native rates per native volume/native clock are converted once.

CR_PROPER_SOURCE_V1 fields are described by ``validate_source``. An optional
``bins`` array is a finite atomic measure (already integrated energy-bin weights),
never differential samples. Missing history is represented by None. Nonnegative
degree <= 2 coefficients are the deliberately bounded history class.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re

EV_J = 1.602176634e-19
RTOL = 2e-13
NATIVE21 = ("n", "H1I", "H1II", "DI", "DII", "TI", "TII", "He3I",
            "He3II", "He3III", "He4I", "He4II", "He4III", "Li6I",
            "Li6II", "Li6III", "Li6IV", "Li7I", "Li7II", "Li7III", "Li7IV")
BARYON_A = (1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7)
CHARGE_Q = (0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3)
RESERVOIRS = ("binding", "thermal_kinetic", "fast_kinetic", "radiation",
              "recoil", "escaped", "external")
TOKENS = ["clock", "volume", "target_density"]
APPROVED_HE4_MAPPINGS = frozenset((
    "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4",
    "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
))


class ContractError(ValueError):
    """An input fails the scoped physical or representation contract."""


def need(condition, code):
    if not condition:
        raise ContractError(code)


def real(value, name, *, nonnegative=False, positive=False):
    need(not isinstance(value, bool) and isinstance(value, (int, float)),
         name + ":EXPLICIT_REAL_REQUIRED")
    result = float(value)
    need(math.isfinite(result) and (not nonnegative or result >= 0)
         and (not positive or result > 0), name + ":FINITE_DOMAIN_REQUIRED")
    return result


def text(value, name):
    need(isinstance(value, str) and bool(value.strip()), name + ":REQUIRED")
    return value


def keys(value, required, name):
    need(type(value) is dict and set(value) == set(required), name + ":EXACT_FIELDS_REQUIRED")


def digest(value):
    """Canonical JSON digest, with NaN and Infinity prohibited."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _sha256(value, name):
    need(re.fullmatch(r"[0-9a-f]{64}", str(value)) is not None, name + ":SHA256_REQUIRED")
    return value


def _support(values, name):
    need(isinstance(values, list) and len(values) == 2, name + ":SUPPORT_REQUIRED")
    lo, hi = [real(value, name, nonnegative=True) for value in values]
    need(hi > lo, name + ":NONDEGENERATE_SUPPORT_REQUIRED")
    return [lo, hi]


def build_source_event(*, physical_definition_sha256, energy_array_sha256,
                       source_array_sha256, family_native_birth_support_eV,
                       native_birth_support_eV, clock_origin_s):
    """Bind one physical source family independently of transport producer bytes.

    The three digests identify the physical source definition, raw energy array
    and raw source array. Transport-operator/NPZ/revision identities are excluded.
    Partition bounds remain outside the family hash so overlapping partitions
    of that family can be detected. Times in histories are elapsed proper seconds
    from the explicit fixed ``clock_origin_s``.
    """
    definition = _sha256(physical_definition_sha256, "physical_definition")
    energy = _sha256(energy_array_sha256, "energy_array")
    source = _sha256(source_array_sha256, "source_array")
    family_support = _support(family_native_birth_support_eV, "family_birth_support")
    partition = _support(native_birth_support_eV, "native_birth_support")
    need(family_support[0] <= partition[0] < partition[1] <= family_support[1],
         "BIRTH_PARTITION_OUTSIDE_FAMILY_SUPPORT")
    origin = real(clock_origin_s, "clock_origin_s")
    identity = {"physical_definition_sha256": definition, "energy_array_sha256": energy,
                "source_array_sha256": source,
                "family_native_birth_support_eV": family_support, "clock_origin_s": origin}
    return dict(identity, family_id="cr-source-family-" + digest(identity),
                native_birth_support_eV=partition,
                partition_id="birth-partition-" + digest(partition))


def validate_source_event(event, support_eV):
    need(type(event) is dict, "EXPLICIT_SOURCE_EVENT_FAMILY_REQUIRED")
    required = ("physical_definition_sha256", "energy_array_sha256", "source_array_sha256",
                "family_native_birth_support_eV", "native_birth_support_eV", "clock_origin_s",
                "family_id", "partition_id")
    keys(event, required, "source_event")
    expected = build_source_event(**{key: event[key] for key in required
                                     if key not in ("family_id", "partition_id")})
    need(event == expected, "SOURCE_EVENT_FAMILY_OR_PARTITION_ID_MISMATCH")
    need(_support(support_eV, "source_support") == expected["native_birth_support_eV"],
         "SOURCE_EVENT_BIRTH_SUPPORT_MISMATCH")
    return expected


def close(a, b, name):
    a, b = real(a, name), real(b, name)
    scale = max(abs(a), abs(b))
    need(abs(a - b) <= RTOL * scale, name + ":MISMATCH")


def _coefficients(values, name):
    need(isinstance(values, list) and 1 <= len(values) <= 3,
         name + ":POLYNOMIAL_DEGREE_0_TO_2_REQUIRED")
    return [real(v, name, nonnegative=True) for v in values]


def _pair(number_coefficients, energy_coefficients, support):
    n = _coefficients(number_coefficients, "number_coefficients")
    u = _coefficients(energy_coefficients, "energy_coefficients_eV")
    need(len(n) == len(u), "COEFFICIENT_LENGTH_MISMATCH")
    lo, hi = support
    for nv, uv in zip(n, u):
        need((nv == 0 and uv == 0) or (nv > 0 and
             lo * nv * (1 - RTOL) <= uv <= hi * nv * (1 + RTOL)),
             "MOMENT_OUTSIDE_NATIVE_SUPPORT_OR_ZERO_COUNTERPART")
    return n, u


def _validate_history(history, representation, support):
    if history is None:
        return
    need(isinstance(history, list) and bool(history), "FINITE_HISTORY_REQUIRED")
    previous_stop = None
    for segment in history:
        need(type(segment) is dict, "HISTORY_SEGMENT_REQUIRED")
        start = real(segment.get("start_s"), "start_s", nonnegative=True)
        stop = real(segment.get("stop_s"), "stop_s", positive=True)
        need(stop > start, "POSITIVE_HISTORY_INTERVAL_REQUIRED")
        need(previous_stop is None or start >= previous_stop, "OVERLAPPING_HISTORY")
        previous_stop = stop
        n, u = _pair(segment.get("number_coefficients"),
                     segment.get("energy_coefficients_eV"), support)
        if representation == "atomic_bins":
            bins = segment.get("bins")
            need(isinstance(bins, list) and bool(bins), "ATOMIC_BINS_REQUIRED")
            for atom in bins:
                energy = real(atom.get("energy_eV"), "atom_energy", nonnegative=True)
                need(support[0] <= energy <= support[1], "SUPPORT_EXTENSION")
                nc = _coefficients(atom.get("number_coefficients"), "bin_coefficients")
                need(len(nc) == len(n), "BIN_COEFFICIENT_LENGTH_MISMATCH")
            for k in range(len(n)):
                close(math.fsum(b["number_coefficients"][k] for b in bins), n[k],
                      "BIN_NUMBER_MOMENT")
                close(math.fsum(b["energy_eV"] * b["number_coefficients"][k]
                                for b in bins), u[k], "BIN_ENERGY_MOMENT")
        else:
            need("bins" not in segment, "MOMENTS_MUST_NOT_IMPLY_SPECTRUM")


def validate_source(source):
    """Validate a raw pinned source without assigning a history or physical state.

    Required objects: source(repository, revision, payload_sha256, evidence_kind),
    particle(kind, isotope, state, energy_coordinate), medium(state_id, frame,
    temperature_K, proper_volume_mode, proper_volume_m3), isotope_mapping,
    support_eV, representation(moments|atomic_bins), normalization, history,
    source_event from ``build_source_event``, and
    history_boundary='unknown_outside_recorded_segments'. A separately
    supplied 'zero_outside_recorded_segments' boundary can be retained as source
    evidence, but this implementation never queries outside the known window.
    Gaps remain unknown unless history_gap_policy='explicit_zero_gaps' or zero
    polynomial segments explicitly fill them.

    Normalization's two Jacobians are d(native clock)/d(proper seconds) and
    d(native volume)/d(proper m^3). A rate_coefficient amplitude is explicitly
    per target number density in proper m^-3; that density is multiplied once.
    """
    need(type(source) is dict, "SOURCE_OBJECT_REQUIRED")
    need(source.get("schema") == "CR_PROPER_SOURCE_V1", "RAW_SOURCE_REQUIRED")
    pin = source.get("source", {})
    text(pin.get("repository"), "source.repository")
    need(re.fullmatch(r"[0-9a-f]{40}", str(pin.get("revision", ""))) is not None,
         "IMMUTABLE_SOURCE_REVISION_REQUIRED")
    need(re.fullmatch(r"[0-9a-f]{64}", str(pin.get("payload_sha256", ""))) is not None,
         "SOURCE_PAYLOAD_SHA256_REQUIRED")
    need(pin.get("evidence_kind") in ("stored_physical", "synthetic_control"),
         "SOURCE_EVIDENCE_KIND_REQUIRED")
    particle = source.get("particle", {})
    kind = particle.get("kind")
    need(kind in ("electron", "photon", "baryon"), "PARTICLE_KIND_REQUIRED")
    isotope = text(particle.get("isotope"), "particle.isotope")
    text(particle.get("state"), "particle.state")
    if kind == "electron":
        need(isotope == "e-" and particle.get("energy_coordinate") == "kinetic_eV",
             "ELECTRON_ISOTOPE_ENERGY_MISMATCH")
    elif kind == "photon":
        need(isotope == "gamma" and particle.get("energy_coordinate") == "photon_energy_eV",
             "PHOTON_ISOTOPE_ENERGY_MISMATCH")
    else:
        need((isotope == "n" or re.fullmatch(r"[A-Z][a-z]?[1-9][0-9]*", isotope))
             and particle.get("energy_coordinate") == "kinetic_eV",
             "EXPLICIT_BARYON_ISOTOPE_REQUIRED")
    text(source.get("isotope_mapping"), "isotope_mapping")
    medium = source.get("medium", {})
    text(medium.get("state_id"), "medium.state_id")
    text(medium.get("frame"), "medium.frame")
    real(medium.get("temperature_K"), "medium.temperature_K", positive=True)
    need(medium.get("proper_volume_mode") == "fixed", "VARYING_VOLUME_UNIMPLEMENTED")
    need("proper_volume_m3" in medium, "EXPLICIT_VOLUME_AVAILABILITY_REQUIRED")
    if medium["proper_volume_m3"] is not None:
        real(medium["proper_volume_m3"], "proper_volume_m3", positive=True)
    support = source.get("support_eV")
    need(isinstance(support, list) and len(support) == 2, "ENERGY_SUPPORT_REQUIRED")
    lo, hi = (real(v, "support_eV", nonnegative=True) for v in support)
    need(hi > lo, "NONDEGENERATE_ENERGY_SUPPORT_REQUIRED")
    need(source.get("representation") in ("moments", "atomic_bins"),
         "SOURCE_REPRESENTATION_REQUIRED")
    norm = source.get("normalization", {})
    keys(norm, ("clock_measure", "volume_measure", "d_native_clock_d_proper_s",
                "d_native_volume_d_proper_m3", "target_density_mode", "target_density_m3",
                "applied_tokens"), "normalization")
    need(norm.get("applied_tokens") == [], "NORMALIZATION_ALREADY_APPLIED")
    cf = real(norm.get("d_native_clock_d_proper_s"), "clock_jacobian", positive=True)
    vf = real(norm.get("d_native_volume_d_proper_m3"), "volume_jacobian", positive=True)
    need(norm.get("clock_measure") in ("proper_s", "native_clock"), "CLOCK_MEASURE_REQUIRED")
    need(norm.get("volume_measure") in ("proper_m3", "native_volume"), "VOLUME_MEASURE_REQUIRED")
    if norm["clock_measure"] == "proper_s":
        need(cf == 1, "PROPER_CLOCK_RESCALING_REJECTED")
    if norm["volume_measure"] == "proper_m3":
        need(vf == 1, "PROPER_VOLUME_RESCALING_REJECTED")
    target_mode = norm.get("target_density_mode")
    need(target_mode in ("already_included", "rate_coefficient"), "TARGET_DENSITY_MODE_REQUIRED")
    if target_mode == "already_included":
        need(norm.get("target_density_m3") is None, "DUPLICATE_TARGET_DENSITY")
    else:
        real(norm.get("target_density_m3"), "target_density_m3", nonnegative=True)
    need(source.get("history_boundary") in ("unknown_outside_recorded_segments",
                                             "zero_outside_recorded_segments"),
         "EXPLICIT_HISTORY_BOUNDARY_REQUIRED")
    need(source.get("history_gap_policy", "unknown_gaps") in
         ("unknown_gaps", "explicit_zero_gaps"), "EXPLICIT_HISTORY_GAP_POLICY_REQUIRED")
    need("history" in source, "EXPLICIT_HISTORY_AVAILABILITY_REQUIRED")
    _validate_history(source["history"], source["representation"], (lo, hi))
    validate_source_event(source.get("source_event"), source["support_eV"])
    return source


def verify_payload(source, path):
    validate_source(source)
    raw = Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == source["source"]["payload_sha256"],
         "SOURCE_PAYLOAD_BYTES_MISMATCH")
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def normalize_to_proper(source):
    validate_source(source)
    out = deepcopy(source)
    norm = out["normalization"]
    cf, vf = norm["d_native_clock_d_proper_s"], norm["d_native_volume_d_proper_m3"]
    density = 1.0 if norm["target_density_mode"] == "already_included" else norm["target_density_m3"]
    base = real(cf * vf * density, "normalization_factor", nonnegative=True)
    for segment in out["history"] or []:
        for key in ("number_coefficients", "energy_coefficients_eV"):
            segment[key] = [real(value * base * cf ** k, "proper_coefficient", nonnegative=True)
                            for k, value in enumerate(segment[key])]
        for atom in segment.get("bins", []):
            atom["number_coefficients"] = [real(value * base * cf ** k, "proper_bin_coefficient", nonnegative=True)
                                           for k, value in enumerate(atom["number_coefficients"])]
    out["schema"] = "CR_PROPER_INJECTION_V1"
    out["raw_source_digest"] = digest(source)
    out["raw_input"] = deepcopy(source)
    norm["applied_tokens"] = TOKENS.copy()
    norm["applied_rate_factor"] = base
    out["clock_of_polynomial"] = "elapsed_proper_seconds_from_segment_start"
    return out


def _validate_proper(source):
    need(type(source) is dict and source.get("schema") == "CR_PROPER_INJECTION_V1",
         "PROPER_INJECTION_REQUIRED")
    need(source.get("normalization", {}).get("applied_tokens") == TOKENS,
         "EXACTLY_ONCE_NORMALIZATION_REQUIRED")
    need(re.fullmatch(r"[0-9a-f]{64}", str(source.get("raw_source_digest", ""))) is not None,
         "RAW_SOURCE_DIGEST_REQUIRED")
    need(source.get("clock_of_polynomial") == "elapsed_proper_seconds_from_segment_start",
         "PROPER_POLYNOMIAL_CLOCK_REQUIRED")
    raw = source.get("raw_input")
    validate_source(raw)
    need(source["raw_source_digest"] == digest(raw), "RAW_SOURCE_DIGEST_MISMATCH")
    need(source == normalize_to_proper(raw), "PROPER_INJECTION_CHANGED_AFTER_NORMALIZATION")
    _validate_history(source.get("history"), source.get("representation"), source["support_eV"])


def _poly_integral(coefficients, left, right):
    # Difference of powers is factored to avoid cancellation for short subwindows.
    width = right - left
    terms = []
    for k, coefficient in enumerate(coefficients):
        geometric_sum = math.fsum(right ** (k - j) * left ** j for j in range(k + 1))
        terms.append(coefficient * width * geometric_sum / (k + 1))
    return real(math.fsum(terms), "polynomial_integral", nonnegative=True)


def _poly_value(coefficients, time):
    return real(math.fsum(c * time ** k for k, c in enumerate(coefficients)),
                "polynomial_rate", nonnegative=True)


def integrate_history(source, window_s=None):
    """Integrate the supplied history; never use a capture mean as exposure.

    The endpoint rate is the left-hand limit at the requested window end, or
    None when that left-hand limit is outside the supplied history. A
    missing history returns null integrated quantities, rates, exposure and
    native25, even if separate population moments are known elsewhere.
    Positive-duration queries crossing an unknown gap are refused. No source
    shutoff or continuation outside the recorded finite window is inferred.
    """
    proper = normalize_to_proper(source) if source.get("schema") == "CR_PROPER_SOURCE_V1" else deepcopy(source)
    _validate_proper(proper)
    history = proper["history"]
    out = {"schema": "CR_INTEGRATED_INJECTION_V1", "source": deepcopy(proper["source"]),
           "raw_source_digest": proper["raw_source_digest"], "medium": deepcopy(proper["medium"]),
           "source_event": deepcopy(proper["source_event"]),
           "particle": deepcopy(proper["particle"]), "isotope_mapping": proper["isotope_mapping"],
           "support_eV": list(proper["support_eV"]), "representation": proper["representation"],
           "number_m3": None, "coordinate_energy_eV_m3": None, "coordinate_energy_J_m3": None,
           "proper_time_window_s": None, "exposure_s": None, "supported_duration_s": None,
           "endpoint_number_rate_m3_s": None, "endpoint_energy_rate_J_m3_s": None,
           "endpoint_rate_side": "left", "spectrum": None, "worldtube_count": None,
           "worldtube_coordinate_energy_J": None, "native25": None, "nb_m3": None,
           "rr_return": None, "retained_photon_port": None,
           "physical_heating_J_m3": None, "physical_heating_complete": False,
           "state_update_applied": False, "normalization_tokens": TOKENS.copy(),
           "history_boundary": proper["history_boundary"],
           "history_gap_policy": proper.get("history_gap_policy", "unknown_gaps"),
           "known_zero_gap_duration_s": None, "time_extrapolation": False,
           "history_digest": digest(history)}
    if history is None:
        need(window_s is None, "MISSING_HISTORY_CANNOT_ACCEPT_EXPOSURE")
        out["status"] = "INPUT_DEPENDENCY_HISTORY_MISSING"
        return out
    if window_s is None:
        a, b = history[0]["start_s"], history[-1]["stop_s"]
    else:
        need(isinstance(window_s, (list, tuple)) and len(window_s) == 2, "WINDOW_REQUIRED")
        a, b = (real(v, "window", nonnegative=True) for v in window_s)
        need(b >= a, "ORDERED_WINDOW_REQUIRED")
        need(history[0]["start_s"] <= a <= b <= history[-1]["stop_s"], "TIME_SUPPORT_EXTENSION")
    zero_gaps = proper.get("history_gap_policy", "unknown_gaps") == "explicit_zero_gaps"
    gap_duration = 0.0
    end_n = end_u = None
    for previous, current in zip(history, history[1:]):
        gap_start, gap_stop = previous["stop_s"], current["start_s"]
        overlap = max(0.0, min(b, gap_stop) - max(a, gap_start))
        need(overlap == 0 or zero_gaps, "TIME_HISTORY_GAP_UNQUALIFIED")
        if a == b and gap_start < b < gap_stop:
            need(zero_gaps, "TIME_HISTORY_GAP_UNQUALIFIED")
        if zero_gaps:
            gap_duration += overlap
            if gap_start < b <= gap_stop:
                end_n = end_u = 0.0
    ns, us, durations, spectrum = [], [], [], []
    for segment in history:
        left, right = max(a, segment["start_s"]), min(b, segment["stop_s"])
        if right > left:
            x, y = left - segment["start_s"], right - segment["start_s"]
            ns.append(_poly_integral(segment["number_coefficients"], x, y))
            us.append(_poly_integral(segment["energy_coefficients_eV"], x, y))
            durations.append(right - left)
            for atom in segment.get("bins", []):
                spectrum.append({"energy_eV": atom["energy_eV"],
                                 "count_m3": _poly_integral(atom["number_coefficients"], x, y),
                                 "segment_start_s": segment["start_s"]})
        if segment["start_s"] < b <= segment["stop_s"]:
            end_n = _poly_value(segment["number_coefficients"], b - segment["start_s"])
            end_u = _poly_value(segment["energy_coefficients_eV"], b - segment["start_s"])
    n = real(math.fsum(ns), "integrated_number", nonnegative=True)
    u = real(math.fsum(us), "integrated_energy", nonnegative=True)
    out.update(status="PASS_SCOPED_PROPER_INJECTION_INTEGRAL", number_m3=n,
               coordinate_energy_eV_m3=u, coordinate_energy_J_m3=u * EV_J,
               proper_time_window_s=[a, b], exposure_s=b - a,
               supported_duration_s=math.fsum(durations), endpoint_number_rate_m3_s=end_n,
               endpoint_energy_rate_J_m3_s=None if end_u is None else end_u * EV_J,
               known_zero_gap_duration_s=gap_duration,
               spectrum=spectrum if proper["representation"] == "atomic_bins" else None)
    volume = proper["medium"]["proper_volume_m3"]
    if volume is not None:
        out["worldtube_count"] = real(n * volume, "worldtube_count", nonnegative=True)
        out["worldtube_coordinate_energy_J"] = real(u * EV_J * volume, "worldtube_energy", nonnegative=True)
    return out


def claim_injection(integrated, registry):
    """Claim a source-family rectangle once before accumulating its return.

    A registry is an owned list of earlier claims. Positive overlap in both
    proper time and native birth energy is rejected. Touching interval boundaries
    have zero measure under this interval-claim contract. A separately identified
    nonzero boundary atom must use its own source/event ownership contract.
    This guard compares physical family identity, not producer/NPZ identities.
    """
    need(type(integrated) is dict and integrated.get("schema") == "CR_INTEGRATED_INJECTION_V1",
         "INTEGRATED_INJECTION_REQUIRED")
    need(integrated.get("number_m3") is not None, "UNKNOWN_HISTORY_CANNOT_BE_CLAIMED")
    need(isinstance(registry, list), "INJECTION_REGISTRY_REQUIRED")
    event = validate_source_event(integrated.get("source_event"), integrated.get("support_eV"))
    window = integrated.get("proper_time_window_s")
    need(isinstance(window, list) and len(window) == 2, "INJECTION_WINDOW_REQUIRED")
    a, b = [real(value, "injection_window", nonnegative=True) for value in window]
    need(b >= a, "ORDERED_INJECTION_WINDOW_REQUIRED")
    lo, hi = event["native_birth_support_eV"]
    for previous in registry:
        need(type(previous) is dict, "INJECTION_REGISTRY_RECORD_REQUIRED")
        need(re.fullmatch(r"cr-source-family-[0-9a-f]{64}", str(previous.get("family_id", ""))) is not None,
             "REGISTRY_SOURCE_FAMILY_REQUIRED")
        previous_support = _support(previous.get("native_birth_support_eV"), "registry_birth_support")
        previous_window = previous.get("proper_time_window_s")
        need(isinstance(previous_window, list) and len(previous_window) == 2,
             "REGISTRY_TIME_WINDOW_REQUIRED")
        old_a, old_b = [real(value, "registry_window", nonnegative=True) for value in previous_window]
        need(old_b >= old_a, "REGISTRY_ORDERED_WINDOW_REQUIRED")
        previous_physical = {"family_id": previous["family_id"],
                             "native_birth_support_eV": previous_support,
                             "proper_time_window_s": [old_a, old_b]}
        need(previous.get("claim_id") == "cr-injection-claim-" + digest(previous_physical),
             "REGISTRY_CLAIM_ID_MISMATCH")
        if previous.get("family_id") != event["family_id"]:
            continue
        old_lo, old_hi = previous_support
        time_overlap = max(a, old_a) < min(b, old_b)
        energy_overlap = max(lo, old_lo) < min(hi, old_hi)
        need(not (time_overlap and energy_overlap), "OVERLAPPING_SAME_SOURCE_EVENT_CLAIM")
    physical = {"family_id": event["family_id"], "native_birth_support_eV": [lo, hi],
                "proper_time_window_s": [a, b]}
    record = dict(physical, claim_id="cr-injection-claim-" + digest(physical),
                  raw_source_digest=integrated["raw_source_digest"],
                  producer_source=deepcopy(integrated["source"]),
                  clock_origin_s=event["clock_origin_s"])
    registry.append(deepcopy(record))
    return record


def project_native25(density_delta, nb_context, *, source_state_id, frame,
                     initial_native25=None):
    """Project an explicit integrated event ledger, never infer its chemistry.

    density_delta contains native21_m3[21], fast_electrons_m3, w_nt_J_m3,
    w_ext_J_m3 and baryons_m3. For Delta nb != 0 the full initial native25 is
    required; all 24 count/energy ratios use (Delta X - x Delta nb)/(nb+Delta nb).
    Temperature has no implicit source: delta logT=0 is a declared frozen-T
    diagnostic only. This function never applies a coupled state update.
    """
    if nb_context is None:
        return None
    need(type(nb_context) is dict, "EXPLICIT_NB_CONTEXT_REQUIRED")
    need(nb_context.get("donor_state_id") == source_state_id
         and nb_context.get("recipient_state_id") == source_state_id,
         "DONOR_RECIPIENT_STATE_MISMATCH")
    need(nb_context.get("frame") == frame, "MIXED_FRAME")
    nb = real(nb_context.get("nb_m3"), "nb_m3", positive=True)
    need(nb_context.get("normalization") == "actual_baryon_density",
         "ACTUAL_BARYON_NORMALIZATION_REQUIRED")
    heavy = density_delta.get("native21_m3")
    need(isinstance(heavy, list) and len(heavy) == 21, "NATIVE21_DENSITY_REQUIRED")
    heavy = [real(v, "native21_delta") for v in heavy]
    dnb = real(density_delta.get("baryons_m3"), "delta_nb")
    close(math.fsum(a * v for a, v in zip(BARYON_A, heavy)), dnb, "BARYON_LEDGER")
    values = heavy + [real(density_delta.get(k), k) for k in
                      ("fast_electrons_m3", "w_nt_J_m3", "w_ext_J_m3")]
    if initial_native25 is None:
        need(dnb == 0, "CHANGING_NB_REQUIRES_INITIAL_STATE")
        initial = [0.0] * 25
    else:
        need(isinstance(initial_native25, list) and len(initial_native25) == 25,
             "NATIVE25_INITIAL_STATE_REQUIRED")
        initial = [real(v, "initial_native25") for v in initial_native25]
        need(all(v >= 0 for v in initial[:23]), "NONNEGATIVE_INITIAL_POPULATIONS_REQUIRED")
        close(math.fsum(a * y for a, y in zip(BARYON_A, initial[:21])), 1.0,
              "INITIAL_BARYON_NORMALIZATION")
    denominator = real(nb + dnb, "final_nb", positive=True)
    delta = [real((value - initial[i] * dnb) / denominator, "native25_delta")
             for i, value in enumerate(values)] + [0.0]
    if initial_native25 is not None:
        need(all(initial[i] + delta[i] >= -RTOL * max(abs(initial[i]), abs(delta[i]))
                 for i in range(23)), "NEGATIVE_FINAL_POPULATION_OR_ENERGY")
    return {"nb_initial_m3": nb, "nb_final_m3": denominator, "delta": delta,
            "basis": "Y[21],zeta,w_nt,w_ext,logT", "units_w": "J_per_baryon",
            "density_delta": deepcopy(density_delta),
            "normalization": "EXACT_FINITE_QUOTIENT" if dnb else "FIXED_NB_INTEGRATED_EVENT",
            "temperature_policy": "FROZEN_T_DIAGNOSTIC", "state_update_applied": False}


def rr_compatibility(injection, response):
    """Return every missing/mismatched dependency without inventing a return."""
    reasons = []
    if injection.get("number_m3") is None:
        reasons.append("ACTUAL_HISTORY_MISSING")
    medium = injection.get("medium", {})
    if response.get("state_id") != medium.get("state_id") or response.get("temperature_K") != medium.get("temperature_K"):
        reasons.append("DONOR_RECIPIENT_STATE_MISMATCH")
    if response.get("frame") != medium.get("frame"):
        reasons.append("MIXED_FRAME")
    if response.get("isotope_mapping") != injection.get("isotope_mapping"):
        reasons.append("ISOTOPE_MAPPING_MISMATCH")
    if response.get("raw_source_digest") != injection.get("raw_source_digest"):
        reasons.append("SOURCE_IDENTITY_MISMATCH")
    if response.get("history_digest") != injection.get("history_digest"):
        reasons.append("SOURCE_HISTORY_MISMATCH")
    if response.get("evidence_kind") != injection.get("source", {}).get("evidence_kind"):
        reasons.append("SYNTHETIC_PHYSICAL_PROVENANCE_MISMATCH")
    if response.get("input_support_eV") != injection.get("support_eV"):
        reasons.append("SUPPORT_MISMATCH")
    if response.get("source_distribution_qualification") != "same_full_source_distribution":
        reasons.append("SOURCE_SPECTRAL_PROJECTION_UNQUALIFIED")
    horizon = response.get("return_horizon")
    if horizon not in ("finite", "eventual"):
        reasons.append("EXPLICIT_RETURN_HORIZON_REQUIRED")
    if horizon == "finite" and response.get("proper_time_window_s") != injection.get("proper_time_window_s"):
        reasons.append("FINITE_RETURN_WINDOW_MISMATCH")
    if response.get("method") == "conditional_mean_time_as_exposure":
        reasons.append("MEAN_TIME_IS_NOT_EXPOSURE")
    if horizon == "finite" and response.get("method") == "saved_resolvent_eventual":
        reasons.append("EVENTUAL_RESOLVENT_NOT_FINITE_RETURN")
    return {"compatible": not reasons, "reasons": reasons, "rr_return": None,
            "native25": None, "retained_photon_port": None}


def canonical_event_id(injection, response):
    event = validate_source_event(injection.get("source_event"), injection.get("support_eV"))
    window = [real(value, "injection_window", nonnegative=True)
              for value in injection["proper_time_window_s"]]
    return "cr-proper-rr-" + digest({
        "family_id": event["family_id"], "native_birth_support_eV": event["native_birth_support_eV"],
        "window": window, "channel": "He4III_to_He4II_1s"})


def _candidate_return_claim(injection, response, registry):
    """Validate return ownership without mutating either ownership registry."""
    need(isinstance(registry, list), "SHARED_RETURN_REGISTRY_REQUIRED")
    channel = response["channel"]
    same_channel = []
    for record in registry:
        need(type(record) is dict and record.get("registry_kind") == "RR_RETURN",
             "RR_RETURN_REGISTRY_RECORD_REQUIRED")
        text(record.get("channel"), "return_registry.channel")
        if record["channel"] == channel:
            same_channel.append(deepcopy(record))
    try:
        candidate = claim_injection(injection, same_channel)
    except ContractError as exc:
        if str(exc) == "OVERLAPPING_SAME_SOURCE_EVENT_CLAIM":
            raise ContractError("OVERLAPPING_SAME_RR_RETURN_CLAIM") from exc
        raise
    candidate.update(registry_kind="RR_RETURN", channel=channel,
                     canonical_event_id=canonical_event_id(injection, response),
                     return_horizon=response["return_horizon"])
    return candidate


def attach_rr_return(injection, response, *, return_registry=None, seen_event_ids=None,
                     nb_context=None):
    """Attach already-qualified HeIII RR moments; this is not an RR solver.

    Returns a typed refusal for actual missing dependencies. A successful event
    keeps retained photons separate from native w_ext and physical heating. A
    successful attachment requires the caller's shared ``return_registry`` list,
    even for a single event (initially []). Family/channel/time/birth-support
    overlap is checked independently of supplemental exact event IDs. A gated
    dependency result requires no registry and consumes no ownership claim.
    """
    verdict = rr_compatibility(injection, response)
    if not verdict["compatible"]:
        return dict(verdict, status="INPUT_DEPENDENCY_RR_RETURN_GATED")
    need(isinstance(return_registry, list), "SHARED_RETURN_REGISTRY_REQUIRED")
    need(injection.get("particle", {}).get("kind") == "electron", "RR_REQUIRES_ELECTRON_SOURCE")
    need(response.get("channel") == "He4III_to_He4II_1s", "UNQUALIFIED_RR_CHANNEL")
    need(injection.get("isotope_mapping") in APPROVED_HE4_MAPPINGS,
         "HE4_ISOTOPE_MAPPING_UNQUALIFIED")
    need(response.get("target_isotope") == "He4", "RR_TARGET_ISOTOPE_MISMATCH")
    need(response.get("final_state") == "1s", "RR_FINAL_STATE_MISMATCH")
    need(response.get("component") == "ground_spontaneous_only", "RR_COMPONENT_MISMATCH")
    need(response.get("angular_scope") == "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
         "RR_ANGULAR_SCOPE_MISMATCH")
    need(response.get("threshold_eV") == 54.42, "NATIVE_THRESHOLD_MISMATCH")
    need(response.get("native_photon_max_eV") == 50000.0, "NATIVE_PHOTON_SUPPORT_MISMATCH")
    need(response.get("mass_model") == "stationary_heavy_target_zero_recoil", "MASS_MODEL_MISMATCH")
    capture_support = response.get("capture_kinetic_support_eV")
    need(isinstance(capture_support, list) and len(capture_support) == 2,
         "CAPTURE_ENERGY_SUPPORT_REQUIRED")
    capture_low, capture_high = [real(v, "capture_support", positive=True) for v in capture_support]
    need(capture_high >= capture_low and capture_high + 54.42 <= 50000.0,
         "NATIVE_RR_SUPPORT_EXTENSION")
    need(re.fullmatch(r"[0-9a-f]{40}", str(response.get("revision", ""))) is not None,
         "RR_REVISION_REQUIRED")
    need(re.fullmatch(r"[0-9a-f]{64}", str(response.get("payload_sha256", ""))) is not None,
         "RR_PAYLOAD_SHA256_REQUIRED")
    event_id = canonical_event_id(injection, response)
    seen = set() if seen_event_ids is None else seen_event_ids
    need(isinstance(seen, set), "EVENT_SET_REQUIRED")
    need(event_id not in seen, "DUPLICATE_SAME_EVENT")
    n = real(response.get("count_m3"), "RR_count", nonnegative=True)
    u = real(response.get("kinetic_energy_eV_m3"), "RR_kinetic_energy", nonnegative=True)
    need(n <= injection["number_m3"] * (1 + RTOL), "TAGGED_RR_COUNT_EXCEEDS_INJECTION")
    need((n == 0 and u == 0) or (n > 0 and u > 0), "RR_ZERO_COUNTERPART")
    if n:
        need(capture_low * (1 - RTOL) <= u / n <= capture_high * (1 + RTOL),
             "RR_MOMENT_OUTSIDE_CAPTURE_SUPPORT")
    energies = {key: 0.0 for key in RESERVOIRS}
    energies.update(binding=-54.42 * n * EV_J, fast_kinetic=-u * EV_J,
                    radiation=(u + 54.42 * n) * EV_J)
    residual = math.fsum(energies.values())
    need(abs(residual) <= RTOL * math.fsum(abs(v) for v in energies.values()), "RR_ENERGY_CLOSURE")
    densities = [0.0] * 21
    densities[11], densities[12] = n, -n
    density_delta = {"native21_m3": densities, "fast_electrons_m3": -n,
                     "w_nt_J_m3": -u * EV_J, "w_ext_J_m3": 0.0, "baryons_m3": 0.0}
    native = project_native25(density_delta, nb_context,
                             source_state_id=injection["medium"]["state_id"],
                             frame=injection["medium"]["frame"])
    return_claim = _candidate_return_claim(injection, response, return_registry)
    seen.add(event_id)
    return_registry.append(deepcopy(return_claim))
    return {"status": "PASS_SCOPED_QUALIFIED_INTEGRATED_RR_RETURN", "compatible": True,
            "reasons": [], "canonical_event_id": event_id, "return_horizon": response["return_horizon"],
            "return_ownership_claim": return_claim,
            "finite_return_claim": response["return_horizon"] == "finite",
            "integrated_count_m3": n, "integrated_energy_J_m3": energies,
            "density_delta": density_delta, "energy_residual_J_m3": residual,
            "native25": native, "retained_photon_port": {
                "integrated_count_m3": n, "integrated_energy_J_m3": energies["radiation"],
                "spectrum": None, "time_history": None, "native_w_ext_owner": False},
            "event_rate_m3_s": None, "instantaneous_rhs": None,
            "physical_heating_J_m3": None, "physical_heating_complete": False,
            "state_update_applied": False}
