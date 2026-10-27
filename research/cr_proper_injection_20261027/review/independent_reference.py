#!/usr/bin/env python3
"""Independent Decimal80 PHYS02 proper-time source-moment reference.

Prepared by /root/theory_review.  This module does not import production ports,
actual_adapter, any old source provider, quadrature, projection, or solver.
Execution is reserved to the root-owned bounded runner.  It reads exact original
binary64 NPZ values and performs only the newly requested algebraic moment sums
and finite-window integrations.  Decimal precision does not improve the physical
accuracy of the retained source arrays.

Canonical producer comparison JSON, if provided, has ``rows`` entries with
``tag`` and ``window_s`` plus the five float fields listed in COMPARE_FIELDS.
Reference numeric outputs are decimal strings.  The comparison uses each
quantity's own scale, never an absolute unit floor.

Before its first execution, the corrected reference was extended to perform the
C3-promised saved-producer half-window, source-tag and energy-unit identities.
The prior unexecuted reference SHA256 is
b529b27f5e816d35d9894f838412483d38c48f777294e3e8f4796e066275d0dc.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys


NPZ_SHA256 = "7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc"
ORIGINAL_RESULT_SHA256 = "0b33ad9af1be50297e54fa8b38570471c35b5e342ce771d834bb576458a91500"
T_FLOAT = 1.0e10
ACTIVE_COUNT = 9600
CUTOFF_ENERGY_INDEX = 9605
CUTOFF_NUMBER_INDEX = 9608
LOW_CROSS_INDICES = (9609, 9610)
TAGS = ("direct_0p1_10", "direct_10_900", "selected_total")
EV_J = Decimal("1.602176634e-19")
INDEPENDENT_LIMIT = Decimal("2e-13")
SAVED_MOMENT_LIMIT = Decimal("2e-12")
ADDITIVITY_UNIT_LIMIT = Decimal("2e-14")
COMPARE_FIELDS = (
    "number_m3",
    "coordinate_energy_eV_m3",
    "coordinate_energy_J_m3",
    "endpoint_number_rate_m3_s",
    "endpoint_energy_rate_J_m3_s",
)
INTEGRATED_FIELDS = COMPARE_FIELDS[:3]


def need(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def original_float(value, name: str) -> float:
    need(not isinstance(value, bool) and isinstance(value, (int, float)),
         name + ":EXPLICIT_REAL_REQUIRED")
    result = float(value)
    need(math.isfinite(result), name + ":FINITE_REAL_REQUIRED")
    return result


def binary64_decimal(value, name: str) -> Decimal:
    need(not isinstance(value, bool), name + ":BOOLEAN_FORBIDDEN")
    return Decimal.from_float(original_float(float(value), name))


def file_pin(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    need(actual == expected, "ORIGINAL_INPUT_HASH_MISMATCH:" + path.name)
    return {"path": str(path), "sha256": actual, "bytes": len(raw)}


def relative_error(actual: Decimal, expected: Decimal) -> Decimal:
    scale = max(abs(actual), abs(expected))
    if scale == 0:
        return Decimal(0)
    return abs(actual - expected) / scale


def check_value(check_id: str, actual: Decimal, expected: Decimal,
                limit: Decimal) -> dict:
    error = relative_error(actual, expected)
    return {"id": check_id, "actual_decimal": str(actual),
            "expected_decimal": str(expected), "relative_error": str(error),
            "relative_limit": str(limit), "pass": error <= limit}


def check_identity(check_id: str, actual: Decimal, expected: Decimal,
                   group: str) -> dict:
    """Compare saved finite quantities, with exact handling of a zero identity."""
    result = check_value(check_id, actual, expected, ADDITIVITY_UNIT_LIMIT)
    result["group"] = group
    result["comparison_mode"] = "EXACT_ZERO" if expected == 0 else "OWN_SCALE_RELATIVE"
    if expected == 0:
        result["pass"] = actual == 0
    return result


def declared_windows() -> list[tuple[float, float]]:
    """Construct the same actual binary64 boundaries as the producer contract.

    Decimal subsequently receives these represented values.  T/3 and the short
    end window are deliberately not silently replaced with ideal rational
    values, which would test a different input.
    """
    t = T_FLOAT
    return [(0.0, t), (0.0, t / 2), (t / 2, t),
            (t / 3, 2 * t / 3), (t * (1 - 1e-6), t), (t, t)]


def window_key(tag: str, window) -> tuple[str, str, str]:
    need(tag in TAGS and isinstance(window, (list, tuple)) and len(window) == 2,
         "ROW_ID_REQUIRED")
    a, b = (original_float(v, "window") for v in window)
    need(0 <= a <= b <= T_FLOAT, "REFERENCE_WINDOW_OUT_OF_DOMAIN")
    return tag, a.hex(), b.hex()


def saved_producer_identities(values: dict) -> list[dict]:
    """Use only the saved 18-row producer values already validated by identity.

    Integrals add over disjoint time windows. Endpoint rates add over source
    birth tags at the same endpoint; they are not time-integrated quantities.
    The energy-unit check uses the exact SI eV-to-joule conversion constant.
    """
    checks = []
    windows = declared_windows()
    whole, first_half, second_half = windows[:3]
    for tag in TAGS:
        all_values = values[window_key(tag, whole)]
        first_values = values[window_key(tag, first_half)]
        second_values = values[window_key(tag, second_half)]
        for field in INTEGRATED_FIELDS:
            checks.append(check_identity(
                "identity:half_window:" + tag + ":" + field,
                all_values[field], first_values[field] + second_values[field],
                "producer_half_window_additivity"))
    for window in windows:
        low = values[window_key(TAGS[0], window)]
        high = values[window_key(TAGS[1], window)]
        total = values[window_key(TAGS[2], window)]
        boundary_id = ":".join(window_key(TAGS[2], window)[1:])
        for field in COMPARE_FIELDS:
            checks.append(check_identity(
                "identity:source_tags:" + boundary_id + ":" + field,
                total[field], low[field] + high[field],
                "producer_source_tag_additivity"))
    for key, saved in values.items():
        checks.append(check_identity(
            "identity:energy_unit:" + ":".join(key),
            saved["coordinate_energy_J_m3"],
            saved["coordinate_energy_eV_m3"] * EV_J,
            "producer_energy_units"))
    return checks


def compare_producer(producer_path: Path, rows: list[dict]
                     ) -> tuple[list[dict], dict, list[dict]]:
    raw = producer_path.read_bytes()
    producer = json.loads(raw)
    need(isinstance(producer, dict) and isinstance(producer.get("rows"), list),
         "CANONICAL_PRODUCER_ROWS_REQUIRED")
    expected = {window_key(row["tag"], row["window_s"]): row for row in rows}
    seen = set()
    checks = []
    values = {}
    for row in producer["rows"]:
        need(isinstance(row, dict), "PRODUCER_ROW_REQUIRED")
        key = window_key(row.get("tag"), row.get("window_s"))
        need(key in expected and key not in seen, "EXACT_UNIQUE_PRODUCER_ROW_REQUIRED")
        seen.add(key)
        ref = expected[key]
        values[key] = {}
        for field in COMPARE_FIELDS:
            value = original_float(row.get(field), "producer." + field)
            actual = Decimal.from_float(value)
            values[key][field] = actual
            wanted = Decimal(ref[field + "_decimal"])
            checks.append(check_value("producer:" + ":".join(key) + ":" + field,
                                      actual, wanted, INDEPENDENT_LIMIT))
    need(seen == set(expected), "MISSING_PRODUCER_REFERENCE_ROWS")
    identities = saved_producer_identities(values)
    return checks, {"path": str(producer_path), "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "rows": len(seen), "compared_fields_per_row": len(COMPARE_FIELDS)}, identities


def check_group_summary(checks: list[dict], limit: Decimal,
                        *, executed: bool = True) -> dict:
    return {"status": "NOT_RUN" if not executed else
            ("PASS" if all(check["pass"] for check in checks) else "FAIL"),
            "checks": len(checks), "passed": sum(check["pass"] for check in checks),
            "relative_limit": str(limit),
            "maximum_relative_error": str(max(
                (Decimal(check["relative_error"]) for check in checks),
                default=Decimal(0))) if executed else None}


def build_reference(npz_path: Path, original_result_path: Path,
                    producer_path: Path | None = None) -> dict:
    # NumPy is used only as the safe NPZ decoder; all moment reductions below
    # use independent Decimal operations, not numpy.sum/dot or producer helpers.
    import numpy as np

    pins = [file_pin(npz_path, NPZ_SHA256),
            file_pin(original_result_path, ORIGINAL_RESULT_SHA256)]
    original = json.loads(original_result_path.read_bytes())
    fullbed_rows = [row for row in original["grid_results"] if row["label"] == "fullBED"]
    need(len(fullbed_rows) == 1, "UNIQUE_ORIGINAL_FULLBED_ROW_REQUIRED")
    saved = fullbed_rows[0]["final"]["components"]
    need(float(fullbed_rows[0]["final"]["time_s"]) == T_FLOAT,
         "ORIGINAL_TIME_WINDOW_MISMATCH")

    with np.load(npz_path, allow_pickle=False) as stored:
        energy = stored["energy_eV"]
        source = stored["source_vectors"]
        scale_value = stored["physical_energy_scale_eV_m3"]
        birth_tags = stored["birth_tags"]
        time_values = stored["time_s"]
        need(energy.shape == (ACTIVE_COUNT,) and source.shape == (ACTIVE_COUNT + 11, 2),
             "ORIGINAL_SOURCE_SHAPE_MISMATCH")
        need(energy.dtype == np.dtype("float64") and source.dtype == np.dtype("float64"),
             "ORIGINAL_SOURCE_BINARY64_REQUIRED")
        need(scale_value.shape == (), "ORIGINAL_SCALE_SCALAR_REQUIRED")
        need(tuple(str(t) for t in birth_tags) == TAGS[:2], "ORIGINAL_BIRTH_TAGS_MISMATCH")
        need(time_values.shape == (2,) and float(time_values[0]) == 0
             and float(time_values[1]) == T_FLOAT, "ORIGINAL_TIME_NODES_MISMATCH")
        need(bool(np.all(np.isfinite(energy))) and bool(np.all(np.isfinite(source)))
             and bool(np.all(source >= 0)), "ORIGINAL_SOURCE_FINITE_NONNEGATIVE_REQUIRED")
        need(bool(np.all(np.diff(energy) > 0)) and float(energy[0]) >= 0.1
             and float(energy[-1]) <= 900, "ORIGINAL_ENERGY_SUPPORT_MISMATCH")

        with localcontext() as context:
            context.prec = 80
            zero = Decimal(0)
            two = Decimal(2)
            T = Decimal.from_float(T_FLOAT)
            Ustar = binary64_decimal(scale_value.item(), "physical_energy_scale")
            need(Ustar > 0, "POSITIVE_ORIGINAL_SCALE_REQUIRED")
            S = Ustar / (T * T)
            E = [Decimal.from_float(float(v)) for v in energy]
            moments = {}
            for column, tag in enumerate(TAGS[:2]):
                b = [Decimal.from_float(float(v)) for v in source[:, column]]
                # Original Cascade.project stores active ENERGY coordinates:
                # b_i = E_i * normalized number weight.  This is independently
                # established from the frozen original source, not guessed
                # from array names or the production adapter.
                number_weight = sum((v / e for e, v in zip(E, b[:ACTIVE_COUNT])), zero)
                number_weight += b[CUTOFF_NUMBER_INDEX]
                energy_weight = sum(b[:ACTIVE_COUNT], zero)
                energy_weight += b[CUTOFF_ENERGY_INDEX]
                moments[tag] = {
                    "number_weight": number_weight,
                    "energy_weight": energy_weight,
                    "A_number": S * number_weight,
                    "A_energy_eV": S * energy_weight,
                    "cutoff_number_weight": b[CUTOFF_NUMBER_INDEX],
                    "cutoff_energy_weight": b[CUTOFF_ENERGY_INDEX],
                    "excluded_low_cross_energy": b[LOW_CROSS_INDICES[0]],
                    "excluded_low_cross_number": b[LOW_CROSS_INDICES[1]],
                }
            # The total is the exact Decimal sum of the two represented source
            # columns, not a new binary64-rounded source vector or rescaling.
            moments[TAGS[2]] = {
                key: moments[TAGS[0]][key] + moments[TAGS[1]][key]
                for key in moments[TAGS[0]]
            }
            rows, checks = [], []
            for tag in TAGS:
                mom = moments[tag]
                for a_float, b_float in declared_windows():
                    a, b = Decimal.from_float(a_float), Decimal.from_float(b_float)
                    ramp_integral = (b - a) * (b + a) / two
                    number = mom["A_number"] * ramp_integral
                    energy_eV = mom["A_energy_eV"] * ramp_integral
                    number_rate = mom["A_number"] * b
                    energy_rate_J = mom["A_energy_eV"] * b * EV_J
                    rows.append({
                        "tag": tag, "window_s": [a_float, b_float],
                        "window_binary64_hex": [a_float.hex(), b_float.hex()],
                        "window_decimal": [str(a), str(b)],
                        "number_m3_decimal": str(number),
                        "coordinate_energy_eV_m3_decimal": str(energy_eV),
                        "coordinate_energy_J_m3_decimal": str(energy_eV * EV_J),
                        "endpoint_number_rate_m3_s_decimal": str(number_rate),
                        "endpoint_energy_rate_J_m3_s_decimal": str(energy_rate_J),
                        "endpoint_rate_side": "left",
                    })
                whole = next(row for row in rows if row["tag"] == tag
                             and row["window_s"] == [0.0, T_FLOAT])
                checks.extend([
                    check_value("saved:" + tag + ":number_m3",
                                Decimal(whole["number_m3_decimal"]),
                                binary64_decimal(saved[tag]["injected_number_m3"], "saved_number"),
                                SAVED_MOMENT_LIMIT),
                    check_value("saved:" + tag + ":energy_J_m3",
                                Decimal(whole["coordinate_energy_J_m3_decimal"]),
                                binary64_decimal(saved[tag]["injected_energy_J_m3"], "saved_energy"),
                                SAVED_MOMENT_LIMIT),
                ])
            saved_checks = list(checks)
            producer_pin = None
            producer_checks, identity_checks = [], []
            if producer_path is not None:
                producer_checks, producer_pin, identity_checks = compare_producer(producer_path, rows)
                checks.extend(producer_checks)
                checks.extend(identity_checks)
            groups = {
                "original_saved_moments": check_group_summary(saved_checks, SAVED_MOMENT_LIMIT),
                "independent_fields": check_group_summary(
                    producer_checks, INDEPENDENT_LIMIT, executed=producer_path is not None),
            }
            for group in ("producer_half_window_additivity",
                          "producer_source_tag_additivity", "producer_energy_units"):
                groups[group] = check_group_summary(
                    [check for check in identity_checks if check["group"] == group],
                    ADDITIVITY_UNIT_LIMIT, executed=producer_path is not None)
            result = {
                "schema": "CR_PROPER_INJECTION_DECIMAL80_REFERENCE_V1",
                "reviewer": "/root/theory_review",
                "status": "PASS_SCOPED" if all(c["pass"] for c in checks) else "FAIL",
                "scope": "actual original PHYS02 binary64 source measure and finite ramp integrals",
                "input_pins": pins, "producer_output_pin": producer_pin,
                "decimal_precision_digits": 80,
                "source_coefficient_scale_S_decimal": str(S),
                "physical_energy_scale_eV_m3_decimal": str(Ustar),
                "T_s_decimal": str(T), "eV_J_exact_decimal": str(EV_J),
                "normalization": "active energy-coordinate b_i: A_Ni=(Ustar/T^2)*b_i/E_i; cutoffN direct; A_E=(Ustar/T^2)*(sum active b_i+cutoffE); Q_i(t)=t*A_Ni",
                "original_coordinate_authority": "causal_cascade.py Cascade.project: out[:n]=E*active_counts; functionals: number[:n]=1/E and energy[:n]=1",
                "moment_units": {"number_weight": "eV^-1", "energy_weight": "dimensionless", "A_number": "m^-3 s^-2", "A_energy_eV": "eV m^-3 s^-2"},
                "active_coordinates": ACTIVE_COUNT,
                "cutoff_energy_index": CUTOFF_ENERGY_INDEX,
                "cutoff_number_index": CUTOFF_NUMBER_INDEX,
                "excluded_diagnostic_indices": list(LOW_CROSS_INDICES),
                "moments": {tag: {key: str(value) for key, value in mom.items()}
                            for tag, mom in moments.items()},
                "rows": rows, "checks": checks,
                "check_groups": groups,
                "check_count": len(checks),
                "pass_count": sum(check["pass"] for check in checks),
                "producer_comparison": "NOT_RUN" if producer_path is None else "COMPLETED",
                "independent_relative_limit": str(INDEPENDENT_LIMIT),
                "saved_source_relative_limit": str(SAVED_MOMENT_LIMIT),
                "additivity_energy_unit_relative_limit": str(ADDITIVITY_UNIT_LIMIT),
                "producer_identity_zero_rule": "expected zero requires actual exactly zero; no absolute unit floor",
                "reference_revision_history": {
                    "prior_corrected_unexecuted_sha256": "b529b27f5e816d35d9894f838412483d38c48f777294e3e8f4796e066275d0dc",
                    "change": "C3-promised saved-row additivity and energy-unit checks added before first independent execution",
                    "prior_independent_executions": 0,
                    "production_imports_added": False,
                },
                "old_source_solver_replay": 0,
                "source_quadrature_replay": 0,
                "source_projection_replay": 0,
                "production_module_imported": False,
                "spectrum_inferred_from_moments": False,
                "physical_uncertainty_improved_by_decimal": False,
                "nb_m3": None, "native25": None, "rr_return": None,
                "retained_photon_port": None, "physical_heating_complete": False,
                "global_physical_error_bound": None,
            }
            return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", type=Path, required=True)
    parser.add_argument("--original-result", type=Path, required=True)
    parser.add_argument("--producer-output", "--producer", dest="producer_output", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    need(not args.output.exists(), "CREATE_ONLY_REFERENCE_OUTPUT_REQUIRED")
    result = build_reference(args.npz, args.original_result, args.producer_output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "rows": len(result["rows"]),
                      "checks": result["check_count"], "passed": result["pass_count"],
                      "producer_comparison": result["producer_comparison"]}, sort_keys=True))
    return 0 if result["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
