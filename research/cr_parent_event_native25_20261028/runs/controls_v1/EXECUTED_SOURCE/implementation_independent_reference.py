#!/usr/bin/env python3
"""Independent small-arithmetic reference for the frozen parent-event unit.

Author: /root/theory_review (theory/reference author, not production author).
No production imports; no proton quadrature, old source regeneration, old RR
propagation, or inherited test-suite execution.  The source identification uses
the distinct Eq. 8 antiderivatives and an unscaled raw-M elimination.  All
floating inputs are lifted exactly before 90-digit Decimal arithmetic.

Execution requires the current unit's C4 runner environment and create-only
reservation.  This file is source only until the root coordinator dispatches it.
The runner, not this reference, owns CPU accounting and the 6 CPU-s reservation.
"""
from __future__ import annotations

import argparse
import ast
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import zipfile


UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
PRECISION = 90
CONTRACT_SHA = "01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162"
MANIFEST_SHA = "2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3"
CONDITION_SHA = "90f0b4e049ab289fbf0a7dd205f4dbc720dbf32547f99f3444a3d3a83b4059bc"
SOURCE_PATH = "research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json"
MOMENT_PATH = ("research/cr_source_binding_20261012/inputs/source_lineage/sources/"
               "research/cr_phys02a_20261010/evidence/NUMERICAL_RESULT.json")
COVERAGE_PATH = ("research/cr_source_binding_20261012/inputs/source_lineage/sources/"
                 "research/cr_phys02c_20261011/evidence/runs/R001/NUMERICAL_RESULT.json")
SAVED_PATH = "research/cr_low_birth_causal_rr_20261027/runs/primary_v1/RESULT.json"
SAVED_ARRAYS_PATH = "research/cr_low_birth_causal_rr_20261027/runs/primary_v1/ARRAYS.npz"
THETA_ORDER = ["theta_H", "theta_He1", "theta_He2"]
SPECIES = ["n", "H1I", "H1II", "DI", "DII", "TI", "TII", "He3I", "He3II",
           "He3III", "He4I", "He4II", "He4III", "Li6I", "Li6II", "Li6III",
           "Li6IV", "Li7I", "Li7II", "Li7III", "Li7IV"]
CHARGES = [0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3]
MASSES = [1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7]
ZERO = Decimal(0)
ONE = Decimal(1)
T_END = Decimal("1e10")
EV_J = Decimal("1.602176634e-19")
KB = Decimal("1.380649e-23")
IH_SOURCE = Decimal("13.605693122994")
IHE_SOURCE = Decimal("24.59")
IH_NATIVE = Decimal("13.6")
IHE_NATIVE = Decimal("24.59")
IHE2_NATIVE = Decimal("54.42")
IH_RR = Decimal("13.60")
IHE_RR = Decimal("24.59")
LEDGER_TOL = Decimal("1e-11")
TARGET_TOL = Decimal("1e-9")
HOLDOUT_TOL = Decimal("2e-12")
ATOM_TOL = Decimal("2e-11")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def lift(value):
    """Original floats are exact binary64 lifts; new decimal strings stay exact."""
    if isinstance(value, Decimal):
        result = value
    elif type(value) is float:
        result = Decimal.from_float(value)
    elif type(value) is int:
        result = Decimal(value)
    elif type(value) is str:
        if "/" in value:
            numerator, denominator = value.split("/")
            result = Decimal(numerator) / Decimal(denominator)
        else:
            result = Decimal(value)
    else:
        raise TypeError("Finite numeric scalar required: " + repr(value))
    need(result.is_finite(), "Non-finite scalar")
    return result


def jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def resolve_unit(value):
    candidate = Path(value)
    path = (candidate if candidate.is_absolute() else UNIT / candidate).resolve()
    need(path.is_relative_to(UNIT.resolve()), "Path outside this unit")
    return path


def guarded_arguments(argv):
    need(argv.count("--out") == 1 and not any(a.startswith("--out=") for a in argv),
         "Exactly one canonical --out token is required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--primary", required=True)
    args = parser.parse_args(argv)
    out = resolve_unit(args.out)
    primary = resolve_unit(args.primary)
    need(UNIT.name == "cr_parent_event_native25_20261028", "Wrong installed unit")
    need(out.parent == (UNIT / "runs").resolve(), "Expected unique runs/<run_id>")
    need(out.is_dir() and not (out / "RESULT.json").exists(), "Output must be reserved and new")
    need(primary.name == "RESULT.json" and primary.parent != out, "Primary RESULT path required")
    need(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID, "Bounded unit environment required")
    need(os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "Bounded output mismatch")
    reservation = json.loads((out / "RESERVATION.json").read_bytes())
    need(reservation.get("unit") == UNIT_ID and reservation.get("run_id") == out.name,
         "Exact same-unit reservation required")
    need(reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID")
         and bool(reservation.get("attempt_id")), "Bounded attempt mismatch")
    budget_raw = (UNIT / "EXECUTION_BUDGET.json").read_bytes()
    budget = json.loads(budget_raw)
    need(budget.get("unit") == UNIT_ID
         and budget.get("budget_id") == "CR_PARENT_EVENT_20261028_NEW40"
         and budget.get("status") == "FROZEN_C4_ADMITTED", "Actual C4 budget required")
    need(budget.get("local_science_cpu_cap_s") == 40
         and budget.get("historical_allowance_transferred") is False
         and budget.get("parallel_project_budget_transferred") is False,
         "Fresh separate 40 CPU-s budget required")
    allocation = [a for a in budget["run_allocations"] if a["run_id"] == out.name]
    need(len(allocation) == 1 and allocation[0]["role"] == "independent"
         and allocation[0]["worker_cpu_reservation_s"] == 6
         and allocation[0]["selected_memory_limit_bytes"] == 268435456,
         "Frozen independent allocation must be 6 CPU-s / 256 MiB")
    need(budget.get("native_threads") == 1, "One native thread required")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        need(os.environ.get(key) == "1", "Frozen one-thread environment required: " + key)
    return out, primary, reservation, budget, sha(budget_raw)


class Checks:
    def __init__(self):
        self.rows = []

    def exact(self, name, observed, expected, category="identity"):
        ok = observed == expected
        self.rows.append({"id": name, "category": category, "pass": ok,
                          "observed": jsonable(observed), "expected": jsonable(expected),
                          "comparison": "exact"})
        return ok

    def predicate(self, name, ok, evidence, category="scope"):
        self.rows.append({"id": name, "category": category, "pass": bool(ok),
                          "evidence": jsonable(evidence), "comparison": "predicate"})
        return bool(ok)

    def number(self, name, observed, expected, tolerance=LEDGER_TOL,
               *, scale=None, category="ledger"):
        observed, expected, tolerance = lift(observed), lift(expected), lift(tolerance)
        denominator = (max(abs(observed), abs(expected)) if scale is None else abs(lift(scale)))
        difference = abs(observed - expected)
        error = difference / denominator if denominator else ZERO
        ok = difference == ZERO if denominator == ZERO else error <= tolerance
        self.rows.append({"id": name, "category": category, "pass": ok,
                          "observed": str(observed), "expected": str(expected),
                          "absolute_difference": str(difference), "scale": str(denominator),
                          "relative_error": str(error), "tolerance": str(tolerance),
                          "zero_rule": "exact when scale is zero"})
        return ok

    def vector(self, name, observed, expected, *, category="native_affine"):
        self.exact(name + ".length", len(observed), len(expected), category)
        if len(observed) == len(expected):
            for i, (a, b) in enumerate(zip(observed, expected)):
                self.number(name + "." + str(i), a, b, category=category)

    def summary(self):
        groups = {}
        for row in self.rows:
            group = groups.setdefault(row["category"], {"executed": 0, "passed": 0,
                                                       "failed": 0, "max_relative_error": ZERO})
            group["executed"] += 1
            group["passed" if row["pass"] else "failed"] += 1
            if "relative_error" in row:
                group["max_relative_error"] = max(group["max_relative_error"],
                                                   lift(row["relative_error"]))
        return {"executed": len(self.rows), "passed": sum(r["pass"] for r in self.rows),
                "failed": sum(not r["pass"] for r in self.rows),
                "by_category": jsonable(groups), "inherited_checks_added": 0}


def verify_inputs(checks):
    for relative, digest in (("CONTRACT.json", CONTRACT_SHA),
                             ("inputs/INPUT_MANIFEST.json", MANIFEST_SHA),
                             ("inputs/CONDITIONING_DEFINITION.json", CONDITION_SHA)):
        raw = (UNIT / relative).read_bytes()
        need(checks.exact("pinned." + relative, sha(raw), digest), "Frozen pin mismatch")
    manifest = json.loads((UNIT / "inputs/INPUT_MANIFEST.json").read_bytes())
    need(checks.exact("input_count", len(manifest["files"]), 17), "Expected exactly 17 source pins")
    pins, cache = {}, {}
    selected_json = {SOURCE_PATH, MOMENT_PATH, COVERAGE_PATH, SAVED_PATH}
    for row in manifest["files"]:
        relative = row["path"]
        need(relative not in pins, "Duplicate input pin")
        path = (REPO / relative).resolve()
        need(path.is_relative_to(REPO.resolve()), "Input path escape")
        raw = path.read_bytes()
        actual = {"path": relative, "bytes": len(raw), "sha256": sha(raw)}
        need(checks.exact("input." + relative, actual, row), "Actual source bytes changed")
        pins[relative] = actual
        if relative in selected_json:
            cache[relative] = json.loads(raw)
    return pins, cache


def primitive_pair(I, W):
    """Eq. 8 direct antiderivatives, distinct from production positive primitives."""
    u = ONE + W / I
    n0 = -I / (2 * u * u)
    n1 = I * (-ONE / u + ONE / (2 * u * u))
    e0 = I * n1
    e1 = I * I * (u.ln() + 2 / u - ONE / (2 * u * u))
    return n0, n1, e0, e1


def basis_moments(a, b):
    """Three number and energy moments on exactly lifted original endpoints."""
    a, b = lift(a), lift(b)
    need(ZERO <= a <= b <= 1000, "Outside common identification support")
    if a == b:
        return [ZERO] * 3, [ZERO] * 3
    rows = []
    for I in (lift(13.605693122994), lift(24.59)):
        left, right = primitive_pair(I, a), primitive_pair(I, b)
        rows.append([right[k] - left[k] for k in range(4)])
    h, he = rows
    return [(Decimal(7) / 3) * h[0] + h[1], he[0], he[1]], [
        (Decimal(7) / 3) * h[2] + h[3], he[2], he[3]]


def solve_raw(matrix, rhs):
    """Independent partial-pivot Gaussian elimination on raw M (no scaled solve)."""
    n = len(rhs)
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    pivots = []
    for col in range(n):
        pivot = max(range(col, n), key=lambda k: abs(a[k][col]))
        need(a[pivot][col] != ZERO, "Singular raw matrix")
        pivots.append({"column": col, "row": pivot, "pivot": str(a[pivot][col])})
        a[col], a[pivot] = a[pivot], a[col]
        for row in range(col + 1, n):
            factor = a[row][col] / a[col][col]
            a[row][col] = ZERO
            for k in range(col + 1, n + 1):
                a[row][k] -= factor * a[col][k]
    answer = [ZERO] * n
    for row in range(n - 1, -1, -1):
        answer[row] = (a[row][n] - sum((a[row][k] * answer[k]
                                      for k in range(row + 1, n)), ZERO)) / a[row][row]
    return answer, pivots


def dot(a, b):
    return sum((lift(x) * lift(y) for x, y in zip(a, b)), ZERO)


def identify_independently(moment_document, checks):
    bands = moment_document["details"]["direct_electron_source_bands"]
    expected = [(0.0, .1), (.1, 1.0), (1.0, 3.0), (3.0, 10.0),
                (10.0, 100.0), (100.0, 1000.0)]
    need(len(bands) >= 6, "Six original source bands required")
    for i, interval in enumerate(expected):
        need(checks.exact("moment_band." + str(i),
                          [bands[i]["lower_eV"], bands[i]["upper_eV"]], list(interval)),
             "Wrong source moment band")
    moments = [basis_moments(a, b) for a, b in expected]
    anchors = [0, 3, 5]
    M = [moments[i][1] for i in anchors]
    b = [lift(bands[i]["electron_energy_coefficient_eV_m3_s2"]) for i in anchors]
    theta, pivots = solve_raw(M, b)
    row_scales = [ONE / item for item in b]
    RM = [[row_scales[i] * M[i][j] for j in range(3)] for i in range(3)]
    column_scales = [ONE / max(abs(RM[i][j]) for i in range(3)) for j in range(3)]
    B = [[RM[i][j] * column_scales[j] for j in range(3)] for i in range(3)]
    inverse_columns = [solve_raw(B, [ONE if i == j else ZERO for i in range(3)])[0]
                       for j in range(3)]
    inverse_B = [[inverse_columns[j][i] for j in range(3)] for i in range(3)]
    norm_B = max(sum((abs(x) for x in row), ZERO) for row in B)
    norm_inverse = max(sum((abs(x) for x in row), ZERO) for row in inverse_B)
    rcond = ONE / (norm_B * norm_inverse)
    z = [theta[j] / column_scales[j] for j in range(3)]
    dz = [HOLDOUT_TOL * sum((abs(x) for x in row), ZERO) for row in inverse_B]
    sensitivity = [dz[j] / abs(z[j]) for j in range(3)]
    positive_lower = [z[j] - dz[j] for j in range(3)]
    checks.predicate("conditioning.rcond", rcond >= Decimal("1e-6"), rcond, "conditioning")
    for j in range(3):
        checks.predicate("conditioning.sensitivity." + str(j),
                         sensitivity[j] <= Decimal("1e-8"), sensitivity[j], "conditioning")
        checks.predicate("conditioning.positive_envelope." + str(j),
                         positive_lower[j] > ZERO, positive_lower[j], "conditioning")
    predictions = []
    for i in range(6):
        observed = lift(bands[i]["electron_energy_coefficient_eV_m3_s2"])
        prediction = dot(moments[i][1], theta)
        category = "moment_anchor" if i in anchors else "moment_holdout"
        checks.number("moment_prediction." + str(i), prediction, observed, HOLDOUT_TOL,
                      category=category)
        predictions.append({"interval_eV": list(expected[i]), "saved": str(observed),
                            "predicted": str(prediction), "kind": category,
                            "relative_error": str(abs(prediction - observed) / abs(observed))})
    low_n, low_e = basis_moments(.1, 10.0)
    targets = {"H": {"number": theta[0] * low_n[0], "energy": theta[0] * low_e[0]},
               "He": {"number": theta[1] * low_n[1] + theta[2] * low_n[2],
                      "energy": theta[1] * low_e[1] + theta[2] * low_e[2]}}
    return {"theta_order": THETA_ORDER, "theta": theta, "M": M, "B": B,
            "inverse_B": inverse_B, "row_scales": row_scales,
            "column_scales": column_scales, "z": z, "rcond_inf": rcond,
            "sensitivity": sensitivity, "positive_lower_z": positive_lower,
            "raw_M_pivots": pivots, "bands": predictions, "targets": targets,
            "solver": "independent raw-M partial-pivot Gaussian elimination",
            "primitive": "Eq8 direct rational/log antiderivative differences",
            "decimal_precision": PRECISION}


def compare_identification(primary, reference, checks):
    actual = primary["coefficient_identification"]
    checks.exact("theta_order", actual["theta_order"], THETA_ORDER, "coefficient_comparison")
    mappings = [("theta_decimal", "theta"), ("row_scales_decimal", "row_scales"),
                ("column_scales_decimal", "column_scales"), ("z_decimal", "z"),
                ("sensitivity_decimal", "sensitivity"),
                ("positive_lower_z_decimal", "positive_lower_z")]
    for field, key in mappings:
        checks.vector("coefficient." + field, actual[field], reference[key],
                      category="coefficient_comparison")
    checks.number("coefficient.rcond_inf", actual["rcond_inf_decimal"],
                  reference["rcond_inf"], category="coefficient_comparison")
    for field, key in (("M_decimal", "M"), ("B_decimal", "B"),
                       ("inverse_B_decimal", "inverse_B")):
        checks.exact("coefficient." + field + ".rows", len(actual[field]), 3)
        for i in range(3):
            checks.vector("coefficient." + field + "." + str(i), actual[field][i],
                          reference[key][i], category="coefficient_comparison")
    checks.predicate("coefficient.precision_at_least80",
                     actual["precision_decimal_digits"] >= 80,
                     actual["precision_decimal_digits"], "coefficient_comparison")
    for j in range(3):
        checks.exact("coefficient.float_hex." + str(j),
                     float(actual["theta_float64"][j]).hex(), actual["theta_float64_hex"][j])
        checks.number("coefficient.float_value." + str(j), actual["theta_float64"][j],
                      reference["theta"][j], category="coefficient_comparison")
    holdouts = actual["holdout_results"]
    need(checks.exact("reported_holdout_count", len(holdouts), 3), "Three holdouts required")
    for row, band_index in zip(holdouts, (1, 2, 4)):
        expected = reference["bands"][band_index]
        checks.exact("reported_holdout.interval." + str(band_index),
                     row["interval_eV"], expected["interval_eV"])
        checks.exact("reported_holdout.saved_hex." + str(band_index),
                     float(row["saved_binary64"]).hex(), row["saved_hex"])
        checks.number("reported_holdout.saved." + str(band_index), row["saved_binary64"],
                      expected["saved"], ZERO, category="moment_holdout")
        checks.number("reported_holdout.prediction." + str(band_index), row["predicted_decimal"],
                      expected["predicted"], LEDGER_TOL, category="moment_holdout")
        checks.exact("reported_holdout.pass." + str(band_index), row["pass"], True,
                     "moment_holdout")
    for target in ("H", "He"):
        observed = primary["projection_validation"]["target_totals"][target]
        for kind, field in (("number", "number_coefficient_m3_s2"),
                            ("energy", "energy_coefficient_eV_m3_s2")):
            checks.number("target_integral." + target + "." + kind, observed[field],
                          reference["targets"][target][kind], TARGET_TOL,
                          category="analytic_target_vs_Q8")
            checks.number("target_analytic_report." + target + "." + kind,
                          observed["analytic_" + field], reference["targets"][target][kind],
                          LEDGER_TOL, category="analytic_target_report")


def read_npy(raw):
    """Metadata/raw-payload parser only; no NumPy or scientific-code import."""
    need(raw[:6] == b"\x93NUMPY", "Invalid NPY member")
    version = tuple(raw[6:8])
    if version == (1, 0):
        length = struct.unpack("<H", raw[8:10])[0]
        start = 10
    elif version in ((2, 0), (3, 0)):
        length = struct.unpack("<I", raw[8:12])[0]
        start = 12
    else:
        raise ValueError("Unsupported NPY format")
    header = ast.literal_eval(raw[start:start + length].decode("latin1"))
    need(header["descr"] == "<f8" and header["fortran_order"] is False,
         "Expected exact C-order little-endian binary64 payload")
    payload = raw[start + length:]
    count = 1
    for size in header["shape"]:
        need(type(size) is int and size >= 0, "Bad array shape")
        count *= size
    need(len(payload) == count * 8, "NPY payload length mismatch")
    return {"shape": list(header["shape"]), "dtype": "<f8", "order": "C",
            "sha256": sha(payload)}, payload


def source_and_artifacts(primary, primary_path, pins, cache, checks):
    rows = [row for row in cache[SOURCE_PATH] if row["tag"] == "direct_0p1_10"]
    need(len(rows) == 1, "One exact low-birth tag required")
    source = rows[0]["source"]
    checks.exact("source.support", source["support_eV"], [.1, 10.0])
    checks.exact("source.representation", source["representation"], "atomic_bins")
    checks.exact("source.particle", source["particle"],
                 {"kind": "electron", "isotope": "e-", "state": "PHYS02_direct_secondary_birth",
                  "energy_coordinate": "kinetic_eV"})
    checks.exact("source.isotope_mapping", source["isotope_mapping"],
                 "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4")
    checks.exact("source.state", source["medium"]["state_id"],
                 "PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED")
    checks.exact("source.frame", source["medium"]["frame"], "prescribed_gas_rest_frame_scalar")
    checks.exact("source.temperature", source["medium"]["temperature_K"], 100.0)
    checks.exact("source.absolute_volume", source["medium"]["proper_volume_m3"], None)
    normalization = source["normalization"]
    for key, expected in (("clock_measure", "proper_s"), ("volume_measure", "proper_m3"),
                          ("d_native_clock_d_proper_s", 1), ("d_native_volume_d_proper_m3", 1),
                          ("target_density_mode", "already_included"), ("applied_tokens", [])):
        checks.exact("source.normalization." + key, normalization[key], expected)
    history = source["history"]
    need(checks.exact("source.history_segments", len(history), 1), "One source segment required")
    segment = history[0]
    checks.exact("source.history", [segment["start_s"], segment["stop_s"]], [0., 1e10])
    checks.exact("source.history_outside", source["history_boundary"],
                 "unknown_outside_recorded_segments")
    atoms = segment["bins"]
    need(checks.exact("source.atom_count", len(atoms), 3201), "Wrong selected source atom count")
    checks.predicate("source.active_indices",
                     all(row["stored_node_index"] == i for i, row in enumerate(atoms[:-1])),
                     {"count": len(atoms) - 1, "expected_indices": "0..3199 in original order"},
                     "identity")
    checks.exact("source.direct_cutoff_index", atoms[-1]["stored_node_index"], "cutoff_boundary")
    checks.exact("source.direct_cutoff_energy", atoms[-1]["energy_eV"], .1)
    checks.exact("source.last_active_energy", atoms[-2]["energy_eV"], 10.0)
    checks.predicate("source.linear_ramp_only",
                     all(row["number_coefficients"][0] == 0 and
                         len(row["number_coefficients"]) == 2 for row in atoms),
                     {"atom_count": len(atoms)}, "identity")
    input_identity = primary["input_identity"]
    for key, path in (("source_record", SOURCE_PATH), ("moment_source", MOMENT_PATH),
                      ("coverage_source", COVERAGE_PATH), ("saved_response", SAVED_PATH),
                      ("saved_response_arrays", SAVED_ARRAYS_PATH)):
        checks.exact("primary.input_identity." + key, input_identity[key], pins[path])
    for key in ("family_id", "partition_id"):
        checks.exact("primary.input_identity." + key, input_identity[key],
                     source["source_event"][key])
    checks.exact("primary.source_payload", input_identity["source_payload_sha256"],
                 source["source"]["payload_sha256"])
    checks.exact("primary.source_revision", input_identity["source_revision"],
                 source["source"]["revision"])
    checks.exact("primary.retained_revision", input_identity["retained_revision"],
                 "4ca5a90de79c8fb82a25fd9e83615bec0dfa870b")
    coverage = cache[COVERAGE_PATH]["coverage"]
    minimum = lift(coverage["minimum_sampled_proton_ejection_endpoint_eV"])
    checks.predicate("common_support_below_actual_endpoint", minimum > 1000,
                     {"minimum_sampled_endpoint_eV": str(minimum), "maximum_fit_energy_eV": 1000},
                     "scope")
    artifact = primary["artifacts"]["ATTRIBUTION_ARRAYS.npz"]
    artifact_path = primary_path.parent / "ATTRIBUTION_ARRAYS.npz"
    artifact_raw = artifact_path.read_bytes()
    checks.exact("attribution_npz.bytes", len(artifact_raw), artifact["bytes"])
    checks.exact("attribution_npz.sha256", sha(artifact_raw), artifact["sha256"])
    payloads = {}
    with zipfile.ZipFile(artifact_path) as archive:
        for member, metadata in artifact["arrays"].items():
            description, payload = read_npy(archive.read(member + ".npy"))
            checks.exact("attribution_member." + member,
                         dict(description, bytes=len(payload)), metadata)
            payloads[member] = payload
    ordered = [atoms[-1]] + atoms[:-1]
    energy_bytes = struct.pack("<3201d", *(row["energy_eV"] for row in ordered))
    source_bytes = struct.pack("<3201d", *(row["number_coefficients"][1] for row in ordered))
    checks.exact("canonical_grid_payload_sha", sha(payloads["energy_eV_with_cutoff"]), sha(energy_bytes))
    checks.exact("canonical_source_payload_sha", sha(payloads["canonical_A_m3_s2"]), sha(source_bytes))
    values = {key: struct.unpack("<3201d", payloads[key]) for key in
              ("energy_eV_with_cutoff", "canonical_A_m3_s2", "identified_A_H_m3_s2",
               "identified_A_He_m3_s2")}
    maximum_atom_error = ZERO
    for canonical, h, he in zip(values["canonical_A_m3_s2"], values["identified_A_H_m3_s2"],
                                values["identified_A_He_m3_s2"]):
        canonical, h, he = lift(canonical), lift(h), lift(he)
        need(canonical >= 0 and h >= 0 and he >= 0, "Negative source attribution atom")
        error = abs(h + he - canonical) / canonical if canonical else ZERO
        need(canonical != ZERO or h + he == ZERO, "Exact zero source atom violated")
        maximum_atom_error = max(maximum_atom_error, error)
    checks.predicate("attribution_own_atom_scale", maximum_atom_error <= ATOM_TOL,
                     {"max_relative_error": str(maximum_atom_error), "tolerance": str(ATOM_TOL)},
                     "new_attribution_atoms")
    for target in ("H", "He"):
        coefficients = values["identified_A_" + target + "_m3_s2"]
        number = sum((lift(x) for x in coefficients), ZERO)
        energy = dot(coefficients, values["energy_eV_with_cutoff"])
        expected = primary["projection_validation"]["target_totals"][target]
        checks.number("artifact_target_sum." + target + ".number", number,
                      expected["number_coefficient_m3_s2"], category="new_attribution_atoms")
        checks.number("artifact_target_sum." + target + ".energy", energy,
                      expected["energy_coefficient_eV_m3_s2"], category="new_attribution_atoms")
    saved_members = cache[SAVED_PATH]["artifacts"]["ARRAYS.npz"]["arrays"]
    with zipfile.ZipFile(REPO / SAVED_ARRAYS_PATH) as archive:
        for channel in ("H", "He"):
            for member in ("capture_" + channel + "_prefix_m3", "capture_" + channel + "_bins_m3",
                           "photon_" + channel + "_energy_eV"):
                description, _payload = read_npy(archive.read(member + ".npy"))
                checks.exact("saved_retained_member." + member, description, saved_members[member])
    return source, saved_members


def expected_baseline(primary, checks):
    nH, nHe, ne, nb = Decimal(140), Decimal(1085) / 94, Decimal(2849) / 1880, Decimal(8750) / 47
    y = [ZERO] * 21
    y[1], y[2] = nH * Decimal(".99") / nb, nH * Decimal(".01") / nb
    y[10], y[11] = nHe * Decimal(".99") / nb, nHe * Decimal(".01") / nb
    baseline = primary["baseline"]
    checks.exact("baseline.species_order", baseline["species_order"], SPECIES)
    checks.exact("baseline.charges", baseline["charges"], CHARGES)
    checks.exact("baseline.mass_numbers", baseline["mass_numbers"], MASSES)
    checks.vector("baseline.Y", baseline["Y_decimal"], y, category="same_state_inventory")
    checks.number("baseline.nb", baseline["n_b_m3_decimal"], nb, category="same_state_inventory")
    npart = nH + nHe + ne
    checks.number("baseline.npart", baseline["n_part0_m3_decimal"], npart, category="same_state_inventory")
    checks.number("baseline.T0", baseline["T0_K_decimal"], 100, category="same_state_inventory")
    checks.number("baseline.baryon_identity", dot(MASSES, y), ONE, category="same_state_inventory")
    checks.number("baseline.charge_identity", dot(CHARGES, y), ne / nb, category="same_state_inventory")
    return {"nH": nH, "nHe": nHe, "ne": ne, "nb": nb, "npart": npart,
            "T0": Decimal(100), "cv": 3 * KB / 2, "Y": y,
            "producer_Y": list(map(lift, baseline["Y_decimal"]))}


def affine_species(J, N, CH, CHe, nb):
    intercept, cp, cd = [ZERO] * 21, [ZERO] * 21, [ZERO] * 21
    intercept[1], intercept[2] = (-J + CH) / nb, (J - CH) / nb
    intercept[10], intercept[11] = (-N + CHe) / nb, (N - CHe) / nb
    cp[11], cp[12] = -ONE / nb, ONE / nb
    cd[10], cd[11], cd[12] = ONE / nb, -2 / nb, ONE / nb
    return intercept, cp, cd


def saved_terms(saved, prefix):
    return {"C_H": saved["channels"]["H"]["capture_number_m3"],
            "C_He": saved["channels"]["He"]["capture_number_m3"],
            "K_H": saved["channels"]["H"]["capture_kinetic_eV_m3"],
            "K_He": saved["channels"]["He"]["capture_kinetic_eV_m3"],
            "retained_photon_H": saved["channels"]["H"]["retained_photon_energy_eV_m3"],
            "retained_photon_He": saved["channels"]["He"]["retained_photon_energy_eV_m3"],
            "cutoff_direct_N": saved["cutoff_direct_number_m3"],
            "cutoff_drift_N": saved["cutoff_drift_number_m3"],
            "cutoff_N": saved["cutoff_number_m3"], "cutoff_U": saved["cutoff_energy_eV_m3"],
            "Coulomb_Q": saved["coulomb_energy_eV_m3"],
            "active_N_change": saved["active_number_m3" if prefix else "active_number_change_m3"],
            "active_U_change": saved["active_energy_eV_m3" if prefix else "active_energy_change_eV_m3"]}


def check_saved_reference(row, saved, group, index, pins, members, checks, label):
    reference = row["saved_response_reference"]
    expected_result = dict(pins[SAVED_PATH], json_pointer="/" + group + "/" + str(index))
    checks.exact(label + ".saved_result_reference", reference["result"], expected_result)
    checks.exact(label + ".saved_arrays_reference", reference["arrays"], pins[SAVED_ARRAYS_PATH])
    checks.exact(label + ".saved_row_unchanged", reference["row_as_saved"], saved)
    original = saved_terms(saved, group == "prefixes")
    for key, value in original.items():
        observed = row["event_terms"][key]
        checks.exact(label + ".term." + key, observed, value, "saved_event_terms")
        checks.exact(label + ".term_hex." + key, row["event_terms"]["saved_binary64_hex"][key],
                     float(value).hex(), "saved_event_terms")
    checks.exact(label + ".saved_channels", row["event_terms"]["saved_channels"], saved["channels"],
                 "saved_event_terms")
    for channel in ("H", "He"):
        descriptor = row["retained_photon_reference"][channel]
        count_member = "capture_" + channel + ("_prefix_m3" if group == "prefixes" else "_bins_m3")
        energy_member = "photon_" + channel + "_energy_eV"
        checks.exact(label + ".photon_file." + channel, descriptor["arrays_file"], pins[SAVED_ARRAYS_PATH])
        checks.exact(label + ".photon_member." + channel,
                     [descriptor["count_member"], descriptor["energy_member"], descriptor["row_index"]],
                     [count_member, energy_member, index])
        checks.exact(label + ".photon_member_hash." + channel, descriptor["member_sha256"],
                     {"count": members[count_member]["sha256"], "energy": members[energy_member]["sha256"]})
        checks.exact(label + ".photon_port." + channel, descriptor["saved_port"],
                     saved["retained_photon_ports"][channel])
    return {key: lift(value) for key, value in original.items()}


def caloric_reference(saved, previous, mode, baseline):
    """Direct EOS energies/particle counts and log ratio; no production log1p helper."""
    assimilation = mode == "assimilation"
    Q = lift(saved["coulomb_energy_eV_m3"])
    previous_Q = ZERO if previous is None else lift(previous["coulomb_energy_eV_m3"])
    count = lift(saved["cutoff_number_m3"]) if assimilation else ZERO
    previous_count = (lift(previous["cutoff_number_m3"])
                      if assimilation and previous is not None else ZERO)
    if assimilation:
        Q += lift(saved["cutoff_energy_eV_m3"])
        if previous is not None:
            previous_Q += lift(previous["cutoff_energy_eV_m3"])
    Q *= EV_J
    previous_Q *= EV_J
    U0 = baseline["cv"] * baseline["npart"] * baseline["T0"]
    Ua, Da = U0 + previous_Q, baseline["npart"] + previous_count
    before_T = Ua / (baseline["cv"] * Da)
    after_T = (Ua + Q) / (baseline["cv"] * (Da + count))
    ratio = after_T / before_T
    return {"Q_J_m3": Q, "thermal_count_m3": count,
            "baseline_thermal_energy_J_m3": Ua, "baseline_particle_density_m3": Da,
            "baseline_energy_origin": U0, "baseline_energy_prefix_increment": previous_Q,
            "baseline_particle_origin": baseline["npart"], "baseline_particle_prefix_increment": previous_count,
            "delta_T_ratio": ratio - ONE, "delta_logT": ratio.ln(),
            "temperature_before_K": before_T, "temperature_after_K": after_T}


def window_reference(row, saved, previous, group, index, targets, baseline,
                     pins, members, checks):
    label = group + "." + str(index)
    prefix = group == "prefixes"
    expected_interval = [0.0 if prefix else index * 2.5e9, (index + 1) * 2.5e9]
    checks.exact(label + ".index", row["index"], index)
    checks.exact(label + ".interval", row["interval_s"], expected_interval)
    checks.exact(label + ".role", row["role"],
                 "nonadditive_cumulative_prefix" if prefix else "disjoint_observation_bin")
    checks.exact(label + ".saved_interval", saved["interval_s"], expected_interval)
    a, b = map(lift, expected_interval)
    factor = (b * b - a * a) / 2
    reference_source = {}
    for target, key in (("H", "source_H_N_E"), ("He", "source_He_electron_N_E")):
        reference_source[target] = {"number_m3": factor * targets[target]["number"],
                                    "energy_eV_m3": factor * targets[target]["energy"],
                                    "endpoint_number_rate_m3_s": b * targets[target]["number"],
                                    "endpoint_energy_rate_eV_m3_s": b * targets[target]["energy"]}
        for field, expected in reference_source[target].items():
            checks.number(label + ".source." + target + "." + field, row[key][field],
                          expected, TARGET_TOL, category="analytic_target_window")
    J, N = reference_source["H"]["number_m3"], reference_source["He"]["number_m3"]
    UH, UHe = reference_source["H"]["energy_eV_m3"], reference_source["He"]["energy_eV_m3"]
    terms = check_saved_reference(row, saved, group, index, pins, members, checks, label)
    CH, CHe = terms["C_H"], terms["C_He"]
    checks.number(label + ".J_H", row["event_terms"]["J_H"], J, TARGET_TOL, category="analytic_target_window")
    checks.number(label + ".N_eHe", row["event_terms"]["N_eHe"], N, TARGET_TOL, category="analytic_target_window")
    canonicalN, canonicalU = lift(saved["injected_number_m3"]), lift(saved["injected_energy_eV_m3"])
    checks.exact(label + ".canonical_source", row["canonical_source_N_E"],
                 {"number_m3": saved["injected_number_m3"], "energy_eV_m3": saved["injected_energy_eV_m3"]})
    # Residuals are compared on their declared input scale; they may be nearly zero.
    checks.number(label + ".split_residual.N", row["split_residuals"]["number_m3"],
                  J + N - canonicalN, TARGET_TOL, scale=canonicalN, category="split_residual")
    checks.number(label + ".split_residual.U", row["split_residuals"]["energy_eV_m3"],
                  UH + UHe - canonicalU, TARGET_TOL, scale=canonicalU, category="split_residual")
    intercept, cp, cd = affine_species(J, N, CH, CHe, baseline["nb"])
    affine = row["native_affine_Y"]
    checks.exact(label + ".native.parameter_units", affine["parameter_units"], "proper m^-3", "scope")
    for key, expected in (("intercept_decimal", intercept), ("coefficient_p_decimal", cp),
                          ("coefficient_d_decimal", cd)):
        checks.vector(label + ".native." + key, affine[key], expected)
    checks.exact(label + ".actual_He_parameters", affine["actual_parameters"],
                 {"s": None, "p": None, "d": None}, "null_gates")
    checks.exact(label + ".intercept_not_actual", affine["intercept_is_actual_branch"], False, "null_gates")
    checks.exact(label + ".partner_addendum", affine["unknown_partner_addendum"], None, "null_gates")
    actual_intercept = list(map(lift, affine["intercept_decimal"]))
    actual_cp, actual_cd = list(map(lift, affine["coefficient_p_decimal"])), list(map(lift, affine["coefficient_d_decimal"]))
    scale = (J + N + CH + CHe) / baseline["nb"]
    checks.number(label + ".baryon.intercept", dot(MASSES, actual_intercept), ZERO,
                  scale=scale, category="stoichiometry")
    checks.number(label + ".charge.intercept", dot(CHARGES, actual_intercept),
                  (J + N - CH - CHe) / baseline["nb"], category="stoichiometry")
    for key, vector, charge in (("p", actual_cp, ONE / baseline["nb"]), ("d", actual_cd, ZERO)):
        checks.number(label + ".baryon." + key, dot(MASSES, vector), ZERO,
                      scale=ONE / baseline["nb"], category="stoichiometry")
        checks.number(label + ".charge." + key, dot(CHARGES, vector), charge,
                      scale=ONE / baseline["nb"], category="stoichiometry")
    for mode, retained_cutoff in (("retention", True), ("assimilation_fixture", False)):
        selected = row["selected_nonthermal_component"][mode]
        deltaN = terms["active_N_change"] + (terms["cutoff_N"] if retained_cutoff else ZERO)
        deltaU = terms["active_U_change"] + (terms["cutoff_U"] if retained_cutoff else ZERO)
        checks.number(label + ".selected." + mode + ".zeta", selected["delta_zeta"], deltaN / baseline["nb"])
        checks.number(label + ".selected." + mode + ".w_nt", selected["delta_w_nt_J_per_baryon"],
                      deltaU * EV_J / baseline["nb"])
    for key in ("actual_partner_addendum", "actual_full_nonthermal_state", "cutoff_spectrum_below_boundary"):
        checks.exact(label + ".selected.null." + key, row["selected_nonthermal_component"][key], None,
                     "null_gates")
    for key in ("nb_division_count", "eV_to_J_conversion_count"):
        checks.exact(label + ".selected.once." + key, row["selected_nonthermal_component"][key], 1,
                     "interval_ownership")
    for channel, I in (("H", IH_RR), ("He", IHE_RR)):
        capture, kinetic, photon = terms["C_" + channel], terms["K_" + channel], terms["retained_photon_" + channel]
        checks.number(label + ".RR_own_scale." + channel, photon, kinetic + I * capture,
                      LEDGER_TOL, category="individual_RR_energy")
        checks.exact(label + ".RR_count_identity." + channel,
                     saved["channels"][channel]["retained_photon_number_m3"],
                     saved["channels"][channel]["capture_number_m3"], "individual_RR_energy")
    sidecars = row["energy_sidecars"]
    L0 = canonicalU + IH_SOURCE * J + IHE_SOURCE * N
    chemical = IH_NATIVE * (J - CH) + IHE_NATIVE * (N - CHe)
    literal = (IH_SOURCE - IH_NATIVE) * J + (IHE_SOURCE - IHE_NATIVE) * N \
        + (IH_NATIVE - IH_RR) * CH + (IHE_NATIVE - IHE_RR) * CHe
    selected_balance = L0 - (terms["active_U_change"] + terms["Coulomb_Q"] + terms["cutoff_U"]
                            + terms["retained_photon_H"] + terms["retained_photon_He"] + chemical)
    saved_residual = canonicalU - (terms["active_U_change"] + terms["Coulomb_Q"] + terms["cutoff_U"]
                                  + terms["retained_photon_H"] + terms["retained_photon_He"]
                                  - IH_RR * CH - IHE_RR * CHe)
    expected_energy = {"L0_eV_m3": L0, "chemical_intercept_eV_m3": chemical,
                       "chemical_coefficient_p_eV": IHE2_NATIVE,
                       "chemical_coefficient_d_eV": IHE2_NATIVE - IHE_NATIVE,
                       "literal_convention_residual_eV_m3": literal,
                       "selected_balance_intercept_eV_m3": selected_balance}
    for key, value in expected_energy.items():
        checks.number(label + ".energy." + key, sidecars[key], value,
                      category="energy_sidecars")
    literal_terms = {"source_H_convention": (IH_SOURCE - IH_NATIVE) * J,
                     "source_He_convention": (IHE_SOURCE - IHE_NATIVE) * N,
                     "RR_H_convention": (IH_NATIVE - IH_RR) * CH,
                     "RR_He_convention": (IHE_NATIVE - IHE_RR) * CHe}
    for key, value in literal_terms.items():
        checks.number(label + ".literal_term." + key, sidecars["literal_terms_eV_m3"][key],
                      value, category="individual_binding_terms")
    checks.number(label + ".literal_H_exact_difference", sidecars["literal_H_difference_eV"],
                  IH_SOURCE - IH_NATIVE, ZERO, category="individual_binding_terms")
    for key, value in (("source_binding_H_eV_m3", IH_SOURCE * J),
                       ("source_binding_He_electron_equivalent_eV_m3", IHE_SOURCE * N),
                       ("RR_binding_release_H_eV_m3", IH_RR * CH),
                       ("RR_binding_release_He_eV_m3", IHE_RR * CHe)):
        checks.number(label + ".individual_binding." + key, sidecars[key], value,
                      category="individual_binding_terms")
    branch = sidecars["branch_lift"]
    checks.number(label + ".branch_lift.p", branch["coefficient_p_eV"], IHE2_NATIVE,
                  category="affine_branch_energy")
    checks.number(label + ".branch_lift.d", branch["coefficient_d_eV"], IHE2_NATIVE - IHE_NATIVE,
                  category="affine_branch_energy")
    checks.exact(label + ".branch_lift.actual", branch["actual_value_eV_m3"], None, "null_gates")
    checks.exact(label + ".branch_lift.separate", branch["separate_from_literal_convention"],
                 True, "null_gates")
    checks.exact(label + ".required_donor_functional", sidecars["required_donor_work_symbolic"],
                 "L0+U_partner+I2src*p+(I2src-I1src)*d+residual_excitation", "affine_branch_energy")
    checks.exact(label + ".branch_residual_functional", sidecars["branch_convention_residual_symbolic"],
                 "(I2src-I2star)*p+((I2src-I1src)-(I2star-I1star))*d", "affine_branch_energy")
    for field in ("actual_I2_source_eV", "actual_partner_energy_eV_m3",
                  "actual_residual_excitation_eV_m3", "actual_required_donor_work_eV_m3",
                  "actual_proton_debit", "actual_external_work"):
        checks.exact(label + ".energy_null." + field, sidecars[field], None, "null_gates")
    checks.exact(label + ".chemical_intercept_not_actual", sidecars["chemical_intercept_is_actual_branch"],
                 False, "null_gates")
    checks.exact(label + ".residual_not_heating", sidecars["literal_or_branch_residual_deposited_as_heat"],
                 False, "null_gates")
    for field in ("retained_photon_w_ext_contribution", "scoped_projected_w_ext"):
        checks.exact(label + ".energy_zero." + field, sidecars[field], 0, "null_gates")
    checks.number(label + ".eV_J_exact", sidecars["eV_J_exact"], EV_J, ZERO, category="identity")
    checks.number(label + ".energy.saved_residual", sidecars["saved_energy_residual_eV_m3"],
                  saved_residual, scale=canonicalU, category="energy_sidecars")
    checks.number(label + ".energy.after_saved", sidecars["balance_residual_after_saved_eV_m3"],
                  selected_balance - literal - saved_residual,
                  scale=max(abs(literal), abs(saved_residual)), category="energy_sidecars")
    checks.number(label + ".energy.shared_convention_identity", selected_balance - literal,
                  saved_residual, scale=canonicalU, category="energy_sidecars")
    for original, reported in (("kinetic_energy_residual_eV_m3", "saved_kinetic_residual_as_stored_eV_m3"),
                               ("total_energy_residual_eV_m3", "saved_total_residual_as_stored_eV_m3")):
        checks.exact(label + ".original_residual." + original, sidecars[reported], saved[original],
                     "saved_event_terms")
    caloric = {}
    for mode in ("retention", "assimilation"):
        expected = caloric_reference(saved, None if prefix else previous, mode, baseline)
        observed = row["conditional_caloric"][mode]
        for key in ("Q_J_m3", "thermal_count_m3", "baseline_thermal_energy_J_m3",
                    "baseline_particle_density_m3", "delta_T_ratio", "delta_logT"):
            checks.number(label + ".caloric." + mode + "." + key, observed[key], expected[key],
                          category="conditional_caloric")
        checks.number(label + ".caloric_float." + mode, observed["delta_logT_float64"],
                      expected["delta_logT"], category="conditional_caloric")
        for coordinate in ("energy", "particle"):
            parts = observed["baseline_" + coordinate + "_two_part"]
            for part in ("origin", "prefix_increment"):
                checks.number(label + ".caloric_two_part." + mode + "." + coordinate + "." + part,
                              parts[part], expected["baseline_" + coordinate + "_" + part],
                              category="conditional_caloric_two_part")
        for key, value in (("conditional", True), ("actual_temperature_point", None),
                           ("physical_heating_complete", False), ("coupled_thermal_history_solved", False),
                           ("rate_feedback_recomputed", False)):
            checks.exact(label + ".caloric_scope." + mode + "." + key, observed[key], value,
                         "null_gates")
        checks.exact(label + ".caloric_previous_prefix." + mode, observed["baseline_prefix_index"],
                     None if prefix or index == 0 else index - 1, "interval_ownership")
        caloric[mode] = expected
    fixtures = row["conditional_closed_He_family"]
    need(checks.exact(label + ".conditional_fixture_count", len(fixtures), 3), "Three declared fixtures required")
    for k, fraction in enumerate((ZERO, Decimal(1) / 4, Decimal(1) / 2)):
        fixture = fixtures[k]
        d = N * fraction
        p, s = ZERO, N - 2 * d
        checks.exact(label + ".fixture.conditional." + str(k), fixture["conditional"], True, "conditional_family")
        checks.exact(label + ".fixture.not_actual." + str(k), fixture["actual_branch_measurement"], False, "null_gates")
        checks.exact(label + ".fixture.actual_full_native25." + str(k), fixture["actual_full_native25"], None, "null_gates")
        for key, value in (("p_m3", p), ("d_m3", d), ("s_m3", s),
                           ("d_fraction_of_selected_He", fraction)):
            checks.number(label + ".fixture." + str(k) + "." + key, fixture[key], value,
                          category="conditional_family")
        expected_Y = [intercept[i] + cp[i] * p + cd[i] * d for i in range(21)]
        checks.vector(label + ".fixture.Y." + str(k), fixture["delta_Y_decimal"], expected_Y,
                      category="conditional_family")
        previous_delta = [ZERO] * 21
        if not prefix and previous is not None:
            previous_J = (a * a / 2) * targets["H"]["number"]
            previous_N = (a * a / 2) * targets["He"]["number"]
            previous_affine, _previous_cp, previous_cd = affine_species(previous_J, previous_N,
                lift(previous["channels"]["H"]["capture_number_m3"]),
                lift(previous["channels"]["He"]["capture_number_m3"]), baseline["nb"])
            previous_delta = [previous_affine[j] + previous_cd[j] * previous_N * fraction
                              for j in range(21)]
        # Cancel the already independently checked Decimal baseline, not a
        # rounded binary64 endpoint.  This checks sub-ulp prior increments on
        # their own scale instead of the much larger ambient inventory.
        observed_prior_delta = [lift(fixture["baseline_Y_decimal"][j]) - baseline["producer_Y"][j]
                                for j in range(21)]
        checks.vector(label + ".fixture.prior_increment." + str(k), observed_prior_delta,
                      previous_delta, category="conditional_family_two_part")
        checks.number(label + ".fixture.branch_lift." + str(k), fixture["branch_lift_eV_m3"],
                      IHE2_NATIVE * p + (IHE2_NATIVE - IHE_NATIVE) * d, category="conditional_family")
    for field in ("actual_full_native25", "actual_external_work", "actual_temperature_point"):
        checks.exact(label + ".null." + field, row[field], None, "null_gates")
    checks.exact(label + ".physical_heating_complete", row["physical_heating_complete"], False, "null_gates")
    checks.exact(label + ".response_birth_history", row["response_cohort_birth_time_support_s"],
                 [0., float(b)], "interval_ownership")
    checks.exact(label + ".distinct_birth_and_observation_windows",
                 row["birth_interval_and_response_observation_interval_are_distinct"], True,
                 "interval_ownership")
    checks.exact(label + ".prior_survivors", row["includes_prior_injected_survivors"], not prefix,
                 "interval_ownership")
    checks.exact(label + ".claim_partition", row["claim_identity"]["birth_partition_id"],
                 "birth-partition-0a332c1184f24587f59e32404c7c1673c5f84fedc0e3d93ffe2b376bc2c75204",
                 "interval_ownership")
    checks.exact(label + ".claim_saved_response", row["claim_identity"]["selected_response_sha256"],
                 pins[SAVED_PATH]["sha256"], "interval_ownership")
    return {"interval_s": expected_interval, "source": reference_source,
            "native_intercept": intercept, "native_coefficient_p": cp, "native_coefficient_d": cd,
            "energy": expected_energy, "saved_energy_residual": saved_residual,
            "caloric": caloric, "actual_He_parameters": None, "actual_external_work": None}


def check_additivity(primary, expected_rows, checks):
    for target, source_key in (("H", "source_H_N_E"), ("He", "source_He_electron_N_E")):
        for field in ("number_m3", "energy_eV_m3"):
            cumulative = ZERO
            for i in range(4):
                cumulative += lift(primary["observation_bins"][i][source_key][field])
                endpoint = primary["prefixes"][i][source_key][field]
                checks.number("additivity." + target + "." + field + "." + str(i),
                              cumulative, endpoint, category="interval_additivity")
    for mode in ("retention", "assimilation"):
        cumulative_log = ZERO
        for i in range(4):
            cumulative_log += lift(primary["observation_bins"][i]["conditional_caloric"][mode]["delta_logT"])
            endpoint_log = primary["prefixes"][i]["conditional_caloric"][mode]["delta_logT"]
            checks.number("caloric_telescope." + mode + "." + str(i), cumulative_log,
                          endpoint_log, category="interval_additivity")
            independent_log = sum((expected_rows["observation_bins"][j]["caloric"][mode]["delta_logT"]
                                   for j in range(i + 1)), ZERO)
            checks.number("caloric_independent_telescope." + mode + "." + str(i), independent_log,
                          expected_rows["prefixes"][i]["caloric"][mode]["delta_logT"],
                          category="interval_additivity")
    for term in ("C_H", "C_He", "K_H", "K_He"):
        cumulative = ZERO
        for i in range(4):
            cumulative += lift(primary["observation_bins"][i]["event_terms"][term])
            checks.number("rare_RR_term_telescope." + term + "." + str(i), cumulative,
                          primary["prefixes"][i]["event_terms"][term],
                          category="individual_RR_additivity")


def compare_scope(primary, checks):
    checks.exact("primary.schema", primary["schema"], "CR_PARENT_EVENT_RESULT_V1")
    checks.exact("primary.unit", primary["unit"], UNIT_ID)
    checks.exact("primary.status", primary["status"], "PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN")
    scope = primary["scope"]
    for key, expected in (("old_science_replays", 0), ("original_RR_chain_replay", False),
                          ("full9600_G_recovery", False), ("foreign_consumer_activation", False),
                          ("physical_heating_complete", False), ("global_physical_completion", None),
                          ("global_physical_error", None), ("global_budget_remaining", None),
                          ("currency", None)):
        checks.exact("scope." + key, scope[key], expected, "null_gates")
    for key, expected in (("birth_tag", "direct_0p1_10"), ("native_birth_support_eV", [.1, 10.]),
                          ("identification_support_eV", [0., 1000.]), ("history_s", [0., 1e10]),
                          ("history_outside", None), ("proper_clock", "proper_s"),
                          ("frame", "prescribed_gas_rest_frame_scalar"),
                          ("proper_volume_mode", "fixed"), ("absolute_proper_volume_m3", None),
                          ("T_K", "100"), ("nH_total_m3", "140"), ("nHe_total_m3", "1085/94"),
                          ("nb_m3", "8750/47"), ("actual_full_physical_native25", None),
                          ("actual_external_work", None)):
        checks.exact("scope." + key, scope[key], expected, "scope")
    unresolved = primary["unresolved_inputs"]
    for field in ("actual_s", "actual_p", "actual_d", "actual_HeII_residual_state", "partner_energy",
                  "partner_history", "partner_pool", "partner_native_response", "actual_proton_work",
                  "actual_full_physical_native25", "full9600_native25", "absolute_worldtube_totals"):
        checks.exact("unresolved." + field, unresolved[field], None, "null_gates")
    checks.exact("acceptance.no_inherited_count", primary["acceptance"]["old_reference_or_controls_added_to_new_count"],
                 False, "scope")


def check_claims(primary, source, checks):
    registry = primary["adoption_registry"]
    for key, expected in (("scope", "partial_bookkeeping_only_no_full_consumer_activation"),
                          ("prefixes_additively_adopted", False), ("aggregate_includes_prior_RR", True),
                          ("full_consumer_activation", False), ("all_response_components_once", True)):
        checks.exact("ownership." + key, registry[key], expected, "interval_ownership")
    claims = registry["claims"]
    checks.exact("ownership.reported_count", registry["claim_count"], len(claims), "interval_ownership")
    checks.exact("ownership.expected_count", len(claims), 16, "interval_ownership")
    observed = []
    for i, claim in enumerate(claims):
        label = "ownership.claim." + str(i)
        checks.exact(label + ".family", claim["family_id"], source["source_event"]["family_id"],
                     "interval_ownership")
        checks.exact(label + ".recipient", claim["recipient_identity"],
                     "CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1", "interval_ownership")
        checks.exact(label + ".support", claim["native_birth_support_eV"], [.1, 10.], "interval_ownership")
        checks.exact(label + ".clock", [claim["clock"], claim["clock_origin_s"]],
                     ["proper_s", 0.], "interval_ownership")
        checks.exact(label + ".interval_meaning", claim["interval_meaning"],
                     "birth_interval" if claim["component"] == "birth" else "observation_interval",
                     "interval_ownership")
        observed.append((claim["component"], tuple(claim["interval_s"])))
    expected = [(component, (i * 2.5e9, (i + 1) * 2.5e9))
                for i in range(4) for component in ("birth", "RR:H", "RR:He", "cutoff")]
    checks.exact("ownership.unique_disjoint_component_claims", sorted(observed), sorted(expected),
                 "interval_ownership")


def run_reference(primary_path, checks):
    pins, cache = verify_inputs(checks)
    primary_raw = primary_path.read_bytes()
    primary = json.loads(primary_raw)
    compare_scope(primary, checks)
    source, members = source_and_artifacts(primary, primary_path, pins, cache, checks)
    check_claims(primary, source, checks)
    reference = identify_independently(cache[MOMENT_PATH], checks)
    compare_identification(primary, reference, checks)
    baseline = expected_baseline(primary, checks)
    expected_rows = {}
    saved_document = cache[SAVED_PATH]
    for group in ("prefixes", "observation_bins"):
        need(checks.exact(group + ".count", len(primary[group]), 4), "Four windows required")
        need(len(saved_document[group]) == 4, "Four stored response windows required")
        expected_rows[group] = []
        for i in range(4):
            previous = saved_document["prefixes"][i - 1] if group == "observation_bins" and i else None
            expected_rows[group].append(window_reference(primary[group][i], saved_document[group][i],
                previous, group, i, reference["targets"], baseline, pins, members, checks))
    check_additivity(primary, expected_rows, checks)
    return {"primary": {"path": str(primary_path.relative_to(UNIT)),
                         "bytes": len(primary_raw), "sha256": sha(primary_raw)},
            "source_inputs": list(pins.values()), "source_family": source["source_event"],
            "coefficient_reference": reference, "baseline_reference": baseline,
            "window_reference": expected_rows,
            "symbolic_unknown_branch_reference": {
                "actual_I2src": None, "actual_partner_work": None, "actual_p_d": None,
                "required_work_p_coefficient": {"I2src": 1, "constant_eV": ZERO},
                "required_work_d_coefficient": {"I2src": 1, "constant_eV": -IHE_SOURCE},
                "convention_residual_p_coefficient": {"I2src": 1, "constant_eV": -IHE2_NATIVE},
                "convention_residual_d_coefficient": {
                    "I2src": 1, "constant_eV": -IHE_SOURCE - IHE2_NATIVE + IHE_NATIVE},
                "outside_partner_energy_and_residual_excitation": "independent unresolved additive ports",
                "is_a_measured_branch_or_proton_history": False}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    out, primary_path, reservation, budget, budget_sha = guarded_arguments(argv)
    checks = Checks()
    result = {"schema": "CR_PARENT_EVENT_INDEPENDENT_REFERENCE_V1", "unit": UNIT_ID,
              "author_role": "theory and independent reference author; not production author",
              "production_imports": [], "decimal_precision": PRECISION,
              "method": "Eq8 direct antiderivative; rawM elimination; analytic target moments; direct EOS log ratio",
              "attempt_id": reservation["attempt_id"], "run_id": out.name,
              "budget_sha256": budget_sha,
              "allocation": {"worker_CPU_s": 6, "native_threads": 1, "memory_bytes": 268435456},
              "old_science_replays": 0, "old_source_quadrature_replays": 0,
              "old_RR_propagation_replays": 0, "inherited_checks_added": 0,
              "physical_heating_complete": False, "global_physical_completion": None,
              "global_physical_error": None, "actual_full_native25": None,
              "actual_external_work": None, "global_budget_remaining": None, "currency": None,
              "arithmetic_interval_certificate": False, "preventive_hard_CPU_cap_proof": False,
              "resource_accounting": "Only the runner receipt/immutable debit ledger is authoritative"}
    try:
        with localcontext() as ctx:
            ctx.prec = PRECISION
            result.update(run_reference(primary_path, checks))
    except Exception as error:
        checks.predicate("reference_fatal_exception", False,
                         {"type": type(error).__name__, "message": str(error)}, "fatal")
        result["fatal_exception"] = {"type": type(error).__name__, "message": str(error)}
    result["acceptance"] = checks.summary()
    result["checks"] = checks.rows
    result["status"] = "PASS_SCOPED_INDEPENDENT_REFERENCE" if not result["acceptance"]["failed"] else "FAILED"
    payload = json.dumps(jsonable(result), ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8") + b"\n"
    with (out / "RESULT.json").open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    print(json.dumps({"unit": UNIT_ID, "status": result["status"],
                      "acceptance": result["acceptance"], "RESULT_sha256": sha(payload)},
                     ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] == "PASS_SCOPED_INDEPENDENT_REFERENCE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
