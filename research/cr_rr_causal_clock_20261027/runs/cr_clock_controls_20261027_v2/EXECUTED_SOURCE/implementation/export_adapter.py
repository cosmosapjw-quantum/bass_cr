"""Correlated He4III finite-age/bin RR event export candidate.

This pure scalar adapter does not compute RR, recover a source, run an ODE,
construct an instantaneous RHS, or apply a state update. N/E bounds are supplied
by the independently qualified clock calculation. Exact rational coefficients
and directed final binary64 rounding preserve enclosure under the linear map.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
import re

UNIT = "CR_RR_CAUSAL_ERLANG_CLOCK_V1"
SCHEMA = "CR_HEIII_CAUSAL_CORRELATED_EVENT_V1"
FRAME = "bath_frame_rest_target"
TIME_BASIS = "comoving_proper_seconds"
I_EV_EXACT = Fraction(2721, 50)                 # exact decimal 54.42
EV_J_EXACT = Fraction(1602176634, 10**28)       # exact SI 1.602176634e-19
CM3_TO_M3_EXACT = Fraction(10**6)
EV_CM3_TO_J_M3_EXACT = CM3_TO_M3_EXACT * EV_J_EXACT

IDENTITY_HASH_KEYS = (
    "count_projection_sha256", "operator_sha256", "bath_sha256", "raw_atom_sha256",
)
STOICHIOMETRY = {"He4:2": -1, "He4:1": 1, "e:fast": -1, "photon": 1}
RESERVOIRS = (
    "internal", "thermal_kinetic", "fast_kinetic", "retained_photon",
    "recoil", "escaped", "external",
)
FROZEN_SCOPE = {
    "inherited_contract": "CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1",
    "source_science_commit": "4e72c89b714431eb4c6ae07def777bbf72a5ae4c",
    "source_document_commit": "ec463db0c7e5c7fb5070796071c926caa4db6445",
    "isotope_assignment": "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
    "component": "ground_spontaneous_only",
    "mass_model": "stationary_heavy_target_zero_recoil",
    "angular_scope": "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
    "native_channel": "HeII",
    "native_threshold_eV_exact_decimal": "54.42",
    "native_maximum_photon_eV": 50000,
}
ENERGY_MAP_EV = {name: (Fraction(0), Fraction(0)) for name in RESERVOIRS}
ENERGY_MAP_EV.update(
    internal=(-I_EV_EXACT, Fraction(0)),
    fast_kinetic=(Fraction(0), Fraction(-1)),
    retained_photon=(I_EV_EXACT, Fraction(1)),
)


class ExportError(ValueError):
    """Invalid input, provenance, interval or unrepresentable finite output."""


def need(condition, message):
    if not condition:
        raise ExportError(message)


def fp64(value, label, *, nonnegative=False, positive=False):
    """Accept finite Python binary64 values and exactly representable integers."""
    need(not isinstance(value, bool) and isinstance(value, (int, float)),
         label + ": EXPLICIT_REAL_REQUIRED")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ExportError(label + ": FINITE_BINARY64_REQUIRED") from None
    need(math.isfinite(result), label + ": FINITE_BINARY64_REQUIRED")
    if isinstance(value, int):
        need(Fraction.from_float(result) == Fraction(value),
             label + ": INTEGER_NOT_EXACTLY_REPRESENTABLE_IN_BINARY64")
    need(not nonnegative or result >= 0, label + ": NONNEGATIVE_REQUIRED")
    need(not positive or result > 0, label + ": POSITIVE_REQUIRED")
    return 0.0 if result == 0 else result


def interval(values, label):
    need(type(values) in (list, tuple) and len(values) == 2,
         label + ": TWO_ENDPOINT_INTERVAL_REQUIRED")
    lo, hi = (fp64(value, label, nonnegative=True) for value in values)
    need(lo <= hi, label + ": REVERSED_INTERVAL")
    return (lo, hi)


def text_id(value, label):
    need(isinstance(value, str) and value.strip() and value == value.strip()
         and not any(ord(c) < 32 for c in value), label + ": NONEMPTY_ID_REQUIRED")
    return value


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError):
        raise ExportError("FINITE_JSON_SERIALIZABLE_METADATA_REQUIRED") from None


def source_identity_checked(value):
    need(type(value) is dict, "EXPLICIT_SOURCE_IDENTITY_REQUIRED")
    result = deepcopy(value)
    text_id(result.get("distribution_id"), "distribution_id")
    for key in IDENTITY_HASH_KEYS:
        need(isinstance(result.get(key), str)
             and re.fullmatch(r"[0-9a-f]{64}", result[key]), "SOURCE_HASH_PIN_REQUIRED:" + key)
    # Contradictory caller-supplied scope is rejected; absence does not create
    # new qualification. The upstream verified byte/contract binding is required.
    for key, expected in FROZEN_SCOPE.items():
        if key in result:
            need(type(result[key]) is type(expected) and result[key] == expected,
                 "FROZEN_SOURCE_SCOPE_MISMATCH:" + key)
    canonical(result)
    return result


def physical_identity(value):
    return {key: value[key] for key in ("distribution_id", *IDENTITY_HASH_KEYS)}


def rational_json(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def round_fraction(value, *, upper):
    """Round an exact rational outward to a finite binary64 value."""
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ExportError("FINITE_OUTPUT_BINARY64_RANGE_REQUIRED") from None
    need(math.isfinite(result), "FINITE_OUTPUT_BINARY64_RANGE_REQUIRED")
    represented = Fraction.from_float(result)
    if (upper and represented < value) or (not upper and represented > value):
        result = math.nextafter(result, math.inf if upper else -math.inf)
    need(math.isfinite(result), "OUTWARD_ENDPOINT_OVERFLOWS_BINARY64")
    result = 0.0 if result == 0 else result
    represented = Fraction.from_float(result)
    need(represented >= value if upper else represented <= value,
         "DIRECTED_CONVERSION_POSTCONDITION")
    return result


def rational_interval(lo, hi):
    need(lo <= hi, "INTERNAL_REVERSED_RATIONAL_INTERVAL")
    return [round_fraction(lo, upper=False), round_fraction(hi, upper=True)]


def linear_interval(basis, coefficients):
    lo = hi = Fraction(0)
    for (a, b), coefficient in zip(basis, coefficients):
        lo += coefficient * (a if coefficient >= 0 else b)
        hi += coefficient * (b if coefficient >= 0 else a)
    return rational_interval(lo, hi)


def mapped(basis, rows):
    bounds, linear_map = {}, {}
    for name, coefficients in rows.items():
        bounds[name] = linear_interval(basis, coefficients)
        linear_map[name] = {
            "N_cm3": rational_json(coefficients[0]),
            "E_eV_cm3": rational_json(coefficients[1]),
        }
    return bounds, linear_map


def positive_int(value, label):
    need(type(value) is int and value > 0, label + ": POSITIVE_INTEGER_REQUIRED")
    return value


def clock_metadata_checked(value, required_horizons):
    """Preserve exact encoded gamma provenance; do not reevaluate a tail/solver."""
    need(type(value) is dict and value.get("time_units") == "proper_s"
         and value.get("gamma_units") == "s^-1", "EXPLICIT_CLOCK_UNITS_REQUIRED")
    records = value.get("records")
    need(type(records) is list, "CLOCK_RECORD_LIST_REQUIRED")
    canonical(value)
    result, observed = [], set()
    for original in records:
        need(type(original) is dict, "TYPED_CLOCK_RECORD_REQUIRED")
        horizon = fp64(original.get("horizon_s"), "clock horizon", nonnegative=True)
        observed.add(horizon)
        if horizon == 0:
            need(original.get("clocks") in (None, {}), "ZERO_HORIZON_HAS_NO_FINITE_ERLANG_GAMMA")
            row = {"horizon_s": 0.0, "endpoint": "ZERO_HORIZON", "clocks": None}
            if "m" in original:
                row["m"] = positive_int(original["m"], "clock m")
            result.append(row)
            continue
        m = positive_int(original.get("m"), "clock m")
        pair = original.get("clocks")
        need(type(pair) is dict and set(pair) == {"minus", "plus"}, "BOTH_CLOCK_BRANCHES_REQUIRED")
        row = {"horizon_s": horizon, "m": m, "clocks": {}}
        if "delta_requested" in original:
            delta = fp64(original["delta_requested"], "delta requested", positive=True)
            need(delta < 1, "DELTA_REQUESTED_LT_ONE")
            row["delta_requested"] = delta
        for side in ("minus", "plus"):
            c = pair[side]
            need(type(c) is dict, "TYPED_CLOCK_BRANCH_REQUIRED")
            gamma = fp64(c.get("gamma_s_inverse"), "clock gamma", positive=True)
            need(isinstance(c.get("gamma_hex"), str) and c["gamma_hex"] == gamma.hex(),
                 "EXACT_GAMMA_HEX_IDENTITY_REQUIRED")
            numerator = positive_int(c.get("a_numerator"), "clock a numerator")
            denominator = positive_int(c.get("a_denominator"), "clock a denominator")
            a = Fraction(numerator, denominator)
            need(a == Fraction.from_float(gamma) * Fraction.from_float(horizon) / m,
                 "ENCODED_GAMMA_TIME_A_IDENTITY")
            need(a > 1 if side == "minus" else 0 < a < 1, "CLOCK_BRANCH_ORIENTATION")
            tail = fp64(c.get("tail_upper"), "clock tail upper", positive=True)
            need(tail < 1, "CLOCK_TAIL_UPPER_LT_ONE")
            row["clocks"][side] = {
                "gamma_s_inverse": gamma, "gamma_hex": gamma.hex(),
                "a_numerator": a.numerator, "a_denominator": a.denominator,
                "tail_upper": tail,
            }
        if "arithmetic_certificate" in original:
            row["arithmetic_certificate"] = deepcopy(original["arithmetic_certificate"])
        result.append(row)
    need(set(required_horizons) <= observed, "POSITIVE_OBSERVATION_ENDPOINT_CLOCK_PROVENANCE_REQUIRED")
    return {
        "time_units": "proper_s", "gamma_units": "s^-1",
        "method": "AUXILIARY_ERLANG_OBSERVATION_CLOCK_NOT_A_PHYSICAL_SOURCE_CLOCK",
        "records": result,
        "tail_or_solver_recomputed_by_exporter": False,
        "upstream_N_E_certificate_validity_inferred": False,
    }


def canonical_event_id(*, case_id, source_id, source_identity, frame,
                       time_start_s, time_end_s):
    # Exclude bound values, clock m/gamma, nb, and the finite-age/bin label.
    # Alternative certificates of the same physical pulse window are one event.
    payload = {
        "unit": UNIT, "case_id": case_id, "source_id": source_id,
        "source": physical_identity(source_identity), "frame": frame,
        "time_basis": TIME_BASIS, "start_hex": time_start_s.hex(),
        "end_hex": time_end_s.hex(), "channel": "He4III+e:fast->He4II(1s)+photon",
    }
    return "heiii-causal-" + hashlib.sha256(canonical(payload)).hexdigest()


def export_event(*, case_id, source_id, source_identity, time_start_s, time_end_s,
                 count_cm3, kinetic_eV_cm3, frame, clock_metadata,
                 observation_kind="finite_bin", nb_m3=None, frame_gamma=1.0):
    """Export one paired N/E interval on a declared finite proper-time window.

    observation_kind is finite_age (start=0, end>=0) or finite_bin (start<end).
    nb_m3=None is the actual research export; positive explicit nb is a
    conditional algebraic native25 projection, not a native RHS/state update.
    """
    case_id, source_id = text_id(case_id, "case_id"), text_id(source_id, "source_id")
    identity = source_identity_checked(source_identity)
    need(frame == FRAME, "EXPLICIT_ADMITTED_FRAME_REQUIRED")
    frame_gamma = fp64(frame_gamma, "frame Lorentz gamma", positive=True)
    need(frame_gamma == 1.0, "ONLY_COMOVING_REST_FRAME_GAMMA_ONE_ADMITTED")
    start = fp64(time_start_s, "time start proper_s", nonnegative=True)
    end = fp64(time_end_s, "time end proper_s", nonnegative=True)
    need(observation_kind in ("finite_age", "finite_bin"), "OBSERVATION_KIND_REQUIRED")
    if observation_kind == "finite_age":
        need(start == 0 and end >= start, "FINITE_AGE_START_ZERO_REQUIRED")
    else:
        need(start < end, "FINITE_BIN_POSITIVE_WIDTH_REQUIRED")
    n, e = interval(count_cm3, "count cm^-3"), interval(kinetic_eV_cm3, "kinetic eV cm^-3")
    if end == 0:
        need(n == (0.0, 0.0) and e == (0.0, 0.0), "EXACT_ZERO_AGE_HAS_ZERO_RR_REWARD")
    if nb_m3 is not None:
        nb_m3 = fp64(nb_m3, "explicit nb_m3", positive=True)
    clocks = clock_metadata_checked(clock_metadata, {t for t in (start, end) if t > 0})
    basis = tuple(tuple(Fraction.from_float(v) for v in values) for values in (n, e))
    count_si = linear_interval(basis, (CM3_TO_M3_EXACT, Fraction(0)))
    kinetic_si = linear_interval(basis, (Fraction(0), EV_CM3_TO_J_M3_EXACT))
    energy_ev, energy_ev_map = mapped(basis, ENERGY_MAP_EV)
    energy_si_rows = {name: tuple(EV_CM3_TO_J_M3_EXACT * c for c in row)
                      for name, row in ENERGY_MAP_EV.items()}
    energy_si, energy_si_map = mapped(basis, energy_si_rows)
    density_rows = {name: (Fraction(sign) * CM3_TO_M3_EXACT, Fraction(0))
                    for name, sign in STOICHIOMETRY.items()}
    density_si, density_si_map = mapped(basis, density_rows)
    need(tuple(sum(row[i] for row in ENERGY_MAP_EV.values()) for i in range(2))
         == (Fraction(0), Fraction(0)), "SHARED_ENERGY_LINEAR_IDENTITY")

    native = None
    photon_per_baryon = None
    if nb_m3 is not None:
        nb = Fraction.from_float(nb_m3)
        rows = [(Fraction(0), Fraction(0)) for _ in range(25)]
        rows[11] = (CM3_TO_M3_EXACT / nb, Fraction(0))
        rows[12] = (-CM3_TO_M3_EXACT / nb, Fraction(0))
        rows[21] = (-CM3_TO_M3_EXACT / nb, Fraction(0))
        rows[22] = (Fraction(0), -EV_CM3_TO_J_M3_EXACT / nb)
        native = {
            "nb_m3": nb_m3, "basis": "Y[21],zeta,w_nt,w_ext,logT",
            "delta_intervals": [linear_interval(basis, row) for row in rows],
            "linear_map_nonzero_rows": {
                str(i): {"N_cm3": rational_json(rows[i][0]), "E_eV_cm3": rational_json(rows[i][1])}
                for i in (11, 12, 21, 22)
            },
            "species_indices": {"He4II": 11, "He4III": 12},
            "binding_owner": "native ionization-energy vector evaluated with the same DeltaY basis",
            "thermal_electron_count_delta_per_baryon": [0.0, 0.0],
            "thermal_particle_count_delta_per_baryon": [0.0, 0.0],
            "state_update_applied": False, "is_instantaneous_rhs": False,
        }
        photon_row = tuple(c / nb for c in energy_si_rows["retained_photon"])
        photon_per_baryon = {
            "count": linear_interval(basis, (CM3_TO_M3_EXACT / nb, Fraction(0))),
            "energy_J": linear_interval(basis, photon_row),
            "energy_linear_map": {
                "N_cm3": rational_json(photon_row[0]), "E_eV_cm3": rational_json(photon_row[1]),
            },
            "native_w_ext_owner": False,
        }

    average = None
    if observation_kind == "finite_bin":
        duration = Fraction.from_float(end) - Fraction.from_float(start)
        rate_rows = {name: tuple(c / duration for c in row) for name, row in energy_si_rows.items()}
        rate_energy, rate_map = mapped(basis, rate_rows)
        average = {
            "label": "CONDITIONAL_DECLARED_PULSE_BIN_AVERAGE_RETURN",
            "duration_s_interval": rational_interval(duration, duration),
            "duration_exact_s": rational_json(duration),
            "count_m3_s": linear_interval(basis, (CM3_TO_M3_EXACT / duration, Fraction(0))),
            "energy_J_m3_s": rate_energy,
            "energy_linear_map": rate_map,
            "count_linear_map": {
                "N_cm3": rational_json(CM3_TO_M3_EXACT / duration),
                "E_eV_cm3": rational_json(Fraction(0)),
            },
            "instantaneous_physical_rate": False,
            "continuous_source_rate": False,
        }

    event = {
        "schema": SCHEMA, "unit": UNIT,
        "canonical_event_id": canonical_event_id(
            case_id=case_id, source_id=source_id, source_identity=identity, frame=frame,
            time_start_s=start, time_end_s=end),
        "case_id": case_id, "source_id": source_id, "source_identity": identity,
        "frame": frame, "frame_gamma": frame_gamma, "time_basis": TIME_BASIS,
        "observation_kind": observation_kind, "time_start_s": start, "time_end_s": end,
        "clock_metadata": clocks, "source_qualified_scope": deepcopy(FROZEN_SCOPE),
        "upstream_source_bytes_verified_by_exporter": False,
        "common_basis": {
            "order": ["N_cm3", "E_eV_cm3"],
            "N_cm3": {"interval": list(n), "unit": "cm^-3", "endpoint_hex": [v.hex() for v in n]},
            "E_eV_cm3": {"interval": list(e), "unit": "eV cm^-3", "endpoint_hex": [v.hex() for v in e]},
            "representation": "Exact values represented by the supplied binary64 interval endpoints",
            "pair_must_be_the_same_for_all_reservoirs": True,
            "independent_reservoir_interval_corners_are_not_joint_events": True,
            "nominal_value": None,
        },
        "linear_map": {
            "coefficient_representation": "EXACT_RATIONAL",
            "energy_eV_cm3": energy_ev_map, "energy_J_m3": energy_si_map,
            "density_m3": density_si_map,
        },
        "conversion": {
            "count_cm3_to_m3": rational_json(CM3_TO_M3_EXACT),
            "eV_to_J_exact": rational_json(EV_J_EXACT),
            "energy_eV_cm3_to_J_m3": rational_json(EV_CM3_TO_J_M3_EXACT),
            "threshold_eV_exact": rational_json(I_EV_EXACT),
            "SI_conversion_once_from_original_common_basis": True,
            "rounding": "EXACT_RATIONAL_SCALAR_MAP_THEN_DIRECTED_OUTWARD_BINARY64",
        },
        "count_m3": count_si, "kinetic_removed_magnitude_J_m3": kinetic_si,
        "energy_eV_cm3": energy_ev, "energy_J_m3": energy_si, "density_delta_m3": density_si,
        "correlated_conservation": {
            "energy_identity": "-E - 54.42*N + (E + 54.42*N) = 0",
            "exact_for_each_shared_basis_pair": True,
            "He4_nuclei_and_charge_identity": True,
            "independent_interval_corners_conserve": False,
            "floating_endpoint_sum_asserted_zero": False,
        },
        "native_nb_m3": nb_m3, "native25": native,
        "retained_photon_port": {
            "count_m3": count_si, "energy_J_m3": energy_si["retained_photon"],
            "per_baryon": photon_per_baryon, "native_w_ext_owner": False,
            "spectrum": None, "transport_cascade_escape_solved": False,
        },
        "conditional_pulse_bin_average": average,
        "actual_continuous_injection_history": None,
        "source_time_history": None, "exposure_s": None,
        "event_rate_m3_s": None, "instantaneous_physical_rate_m3_s": None,
        "instantaneous_rhs": None, "native25_rhs": None,
        "emission_time_history": None, "emission_spectrum": None,
        "physical_heating_J_m3": None, "physical_stopping_rate": None,
        "irreversible_assimilation": False, "finite_coupled_abundance_update": False,
        "thermal_source_in_selected_model_J_m3": [0.0, 0.0],
        "normalization": "RETURN_FROM_DECLARED_SAVED_PULSE_PER_PROPER_VOLUME",
        "interval_validity": "Conditional on caller-qualified paired N/E bounds; exporter certifies only its exact scalar map and rounding",
        "gates": {"N4": "PARTIAL_OPEN", "N5": "PARTIAL_OPEN",
                  "N6": "PREDECESSOR_GATED", "N7": "PREDECESSOR_GATED", "L4": False},
    }
    canonical(event)  # finite JSON, never NaN/Infinity
    return event


def validate_event(event):
    """Reconstruct the scalar map and reject changed signs, ports or scope."""
    need(type(event) is dict and event.get("schema") == SCHEMA, "TYPED_CAUSAL_EVENT_REQUIRED")
    try:
        expected = export_event(
            case_id=event["case_id"], source_id=event["source_id"], source_identity=event["source_identity"],
            time_start_s=event["time_start_s"], time_end_s=event["time_end_s"],
            count_cm3=event["common_basis"]["N_cm3"]["interval"],
            kinetic_eV_cm3=event["common_basis"]["E_eV_cm3"]["interval"],
            frame=event["frame"], frame_gamma=event["frame_gamma"], clock_metadata=event["clock_metadata"],
            observation_kind=event["observation_kind"], nb_m3=event["native_nb_m3"])
    except (KeyError, TypeError):
        raise ExportError("INCOMPLETE_CAUSAL_EVENT") from None
    # JSON equality distinguishes Boolean false from numerical zero.
    need(canonical(event) == canonical(expected), "CORRELATED_EVENT_RECONSTRUCTION_MISMATCH")
    return {
        "status": "SCALAR_MAP_AND_PROVENANCE_STRUCTURE_MATCH",
        "common_basis_energy_identity": True, "independent_corner_energy_closure": False,
        "source_or_clock_solver_reexecuted": False, "physical_scope_promoted": False,
    }


class PulseReturnBook:
    """Deduplicated diagnostics for one case/source; no aggregation operation.

    Different finite-age returns generally overlap. This container never sums
    them, and case/grid/source alternatives cannot share a book.
    """
    def __init__(self, frame, *, case_id, source_id):
        need(frame == FRAME, "EXPLICIT_ADMITTED_FRAME_REQUIRED")
        self.frame = frame
        self.case_id, self.source_id = text_id(case_id, "case_id"), text_id(source_id, "source_id")
        self._identity = None
        self._ids, self._events = set(), []

    @property
    def events(self):
        return deepcopy(self._events)

    def append(self, event):
        need(type(event) is dict, "TYPED_CAUSAL_EVENT_REQUIRED")
        need(event.get("frame") == self.frame, "BOOK_FRAME_MISMATCH")
        need((event.get("case_id"), event.get("source_id")) == (self.case_id, self.source_id),
             "ALTERNATIVE_CASES_OR_SOURCES_NOT_ADDITIVE")
        validate_event(event)
        fingerprint = canonical(physical_identity(event["source_identity"]))
        need(self._identity is None or self._identity == fingerprint, "BOOK_SOURCE_OPERATOR_BATH_IDENTITY_MISMATCH")
        key = event["canonical_event_id"]
        need(key not in self._ids, "DUPLICATE_CANONICAL_PULSE_WINDOW_EVENT")
        self._identity = fingerprint
        self._ids.add(key)
        self._events.append(deepcopy(event))

