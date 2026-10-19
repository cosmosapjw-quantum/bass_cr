#!/usr/bin/env python3
"""Read-only, independent postprocessing of the archived C21F NCP matrices.

This program never imports a solver, calls a native binary, or reruns an IVP.
Only new JSON/CSV products under a previously nonexistent --out are written.
Source literals are read through ast.literal_eval; source code is not executed.

Reusable invocation (paths are inputs, not inferred archive locations)::

    python3 analyze_native_evidence.py \
      --source SNAPSHOT/research/cr_c21e_event_native_20261018 \
      --evidence SNAPSHOT/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z \
      --executable-manifest SNAPSHOT/authority_pr81/C21F_EXECUTABLE_MANIFEST.json \
      --receipts intake_receipts_01.json intake_receipts_02.json intake_receipts_03.json intake_receipts_04.json \
      --out NEW_OUTPUT_DIRECTORY

--source is the work-unit directory, two levels below the snapshot root used by
the GitHub receipt paths. --executable-manifest is the separately retained PR81
execution authority. --receipts contains GitHub intake metadata, not fit results.
The output directory must not already exist. Archive date labels are preserved.
"""
from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys

MODES = ("BE", "MIDPHOTO_ENDMICRO", "FULLMID")
LEVELS = (8, 16, 32, 64)
LANES = ("common_ic", "native_source")
FIXTURE_KEYS = {"x0", "dx", "nh0", "Y", "gas0", "q", "birth", "amounts",
                "opacity_scale", "source_identity", "scope"}
GAS_NAMES = ("x_HII", "y_HeII", "z_HeIII", "w_eV_H")
METRIC_KEYS = {"fraction_max_abs_error", "thermal_abs_error_eV_H",
               "normalized_state_error", "photon_max_abs_error"}


class EvidenceError(ValueError):
    """Input evidence is missing, has changed, or violates its stated contract."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def number(value, name):
    require(type(value) in (int, float) and math.isfinite(value),
            f"NONFINITE_OR_NONNUMERIC: {name}")
    return float(value)


def vector(value, length, name):
    require(isinstance(value, list) and len(value) == length, f"SHAPE: {name}")
    return [number(v, f"{name}[{i}]") for i, v in enumerate(value)]


def finite_tree(obj, label="JSON"):
    if isinstance(obj, float):
        require(math.isfinite(obj), f"NONFINITE: {label}")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            finite_tree(value, f"{label}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            finite_tree(value, f"{label}[{i}]")


def _pairs_unique(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, f"DUPLICATE_JSON_KEY: {k}")
        out[k] = v
    return out


def parse_json(raw, label):
    try:
        obj = json.loads(raw, object_pairs_hook=_pairs_unique)
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError(f"INVALID_JSON: {label}: {exc}") from exc
    finite_tree(obj, label)
    return obj


def hashes(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}


def safe_relative(name):
    if name.startswith("./"):
        name = name[2:]
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts and bool(path.parts),
            f"UNSAFE_RELATIVE_PATH: {name}")
    return str(path)


def load_receipts(paths):
    receipts = {}
    provenance = []
    for p in paths:
        p = Path(p)
        require(p.is_file(), f"MISSING_RECEIPT: {p}")
        raw = p.read_bytes()
        records = parse_json(raw, str(p))
        require(isinstance(records, list), f"RECEIPT_SCHEMA: {p}")
        provenance.append({"path": str(p.resolve()), **hashes(raw)})
        for row in records:
            require(isinstance(row, dict), f"RECEIPT_ROW: {p}")
            key = safe_relative(row["path"])
            require(key not in receipts or receipts[key] == row,
                    f"CONFLICTING_RECEIPTS: {key}")
            receipts[key] = row
    return receipts, provenance


class EvidenceReader:
    """Verify every primary input before parsing it; do not certify unfetched files."""
    def __init__(self, repo_root, evidence, receipts):
        self.repo_root = Path(repo_root).resolve()
        self.evidence = Path(evidence).resolve()
        self.receipts = receipts
        self.records = {}
        self.manifest = {}
        raw = self.read(self.evidence / "MANIFEST.sha256", manifest=False)
        for line in raw.decode("utf-8").splitlines():
            require(bool(re.fullmatch(r"[a-f0-9]{64}  .+", line)), "MANIFEST_LINE_FORMAT")
            digest, name = line.split("  ", 1)
            key = safe_relative(name)
            require(key not in self.manifest, f"MANIFEST_DUPLICATE: {key}")
            self.manifest[key] = digest

    def read(self, path, manifest=True):
        path = Path(path).resolve()
        require(path.is_file(), f"MISSING_RAW_EVIDENCE: {path}")
        try:
            key = path.relative_to(self.repo_root).as_posix()
        except ValueError as exc:
            raise EvidenceError(f"INPUT_OUTSIDE_SNAPSHOT: {path}") from exc
        require(key in self.receipts, f"MISSING_GITHUB_INTAKE_RECEIPT: {key}")
        receipt = self.receipts[key]
        raw = path.read_bytes()
        actual = hashes(raw)
        for field in ("bytes", "sha256", "git_blob"):
            require(actual[field] == receipt.get(field), f"GITHUB_{field.upper()}_MISMATCH: {key}")
        rec = {"path": key, **actual, "source_ref": receipt.get("source_ref"),
               "github_intake_verified": True, "immutable_manifest_verified": False}
        if manifest:
            try:
                rel = path.relative_to(self.evidence).as_posix()
            except ValueError as exc:
                raise EvidenceError(f"INPUT_OUTSIDE_EVIDENCE: {path}") from exc
            require(rel in self.manifest, f"NOT_IN_IMMUTABLE_MANIFEST: {rel}")
            require(actual["sha256"] == self.manifest[rel], f"RAW_MANIFEST_SHA256_MISMATCH: {rel}")
            rec["immutable_manifest_verified"] = True
        self.records[key] = rec
        return raw

    def obj(self, path, manifest=True):
        return parse_json(self.read(path, manifest), str(path))


def literal_from_source(raw, name, class_name=None):
    nodes = ast.parse(raw).body
    if class_name is not None:
        classes = [n for n in nodes if isinstance(n, ast.ClassDef) and n.name == class_name]
        require(len(classes) == 1, f"SOURCE_CLASS: {class_name}")
        nodes = classes[0].body
    values = []
    for node in nodes:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            values.append(ast.literal_eval(node.value))
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            values.append(ast.literal_eval(node.value))
    require(len(values) == 1, f"SOURCE_LITERAL: {name}")
    return values[0]


def validate_fixture(f, expected_digest=None):
    require(isinstance(f, dict) and set(f) == FIXTURE_KEYS, "FIXTURE_SCHEMA_EXACT_KEYS")
    for key in ("x0", "dx", "nh0", "Y", "opacity_scale"):
        number(f[key], f"fixture.{key}")
    require(0 < f["dx"] <= 0.1 and f["nh0"] > 0 and f["Y"] >= 0 and f["opacity_scale"] >= 0,
            "FIXTURE_TIME_DENSITY_DOMAIN")
    require(math.log(1 / 21) <= f["x0"] and f["x0"] + f["dx"] <= math.log(0.2),
            "FIXTURE_MD14_EPOCH_DOMAIN")
    validate_gas(f["gas0"], f["Y"], "fixture.gas0")
    require(isinstance(f["q"], list) and 0 < len(f["q"]) <= 4096, "FIXTURE_COHORT_COUNT")
    count = len(f["q"])
    q = vector(f["q"], count, "fixture.q")
    birth = vector(f["birth"], count, "fixture.birth")
    amounts = vector(f["amounts"], count, "fixture.amounts")
    require(all(v > 0 for v in q) and all(v >= 0 for v in amounts), "FIXTURE_PACKET_DOMAIN")
    require(all(f["x0"] <= v <= f["x0"] + f["dx"] for v in birth), "FIXTURE_BIRTH_DOMAIN")
    require(isinstance(f["source_identity"], str) and f["source_identity"], "FIXTURE_SOURCE_IDENTITY")
    require(f["scope"] == "FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT", "FIXTURE_SCOPE_UNSUPPORTED")
    # Preserve numeric types, sequence order, and key set of the archived object.
    # This reproduces the declared JSON canonicalization, not the pretty file bytes.
    digest = hashlib.sha256(json.dumps(f, sort_keys=True, separators=(",", ":"),
                                       allow_nan=False).encode("utf-8")).hexdigest()
    if expected_digest is not None:
        require(digest == expected_digest, "FIXTURE_CANONICAL_DIGEST_MISMATCH")
    return digest


def validate_gas(gas, Y, label):
    x, y, z, w = vector(gas, 4, label)
    require(0 <= x <= 1 and y >= 0 and z >= 0 and y + z <= 1 and w > 0,
            f"GAS_POSITIVE_DOMAIN: {label}")
    require(Y > 0 or (y == 0 and z == 0), f"ABSENT_HELIUM_DOMAIN: {label}")


def close(a, b, atol=2e-14, rtol=2e-12):
    return abs(a - b) <= atol + rtol * max(abs(a), abs(b))


def temperature(g, Y, kb_ev):
    return g[3] / (1.5 * kb_ev * (1 + Y + g[0] + Y * (g[1] + 2 * g[2])))


def conserved_budgets(f, result, bind, kb_ev):
    """Reconstruct physical total-H stocks without the solver's totals function."""
    g = vector(result["gas"], 4, "result.gas")
    validate_gas(g, f["Y"], "result.gas")
    photons = vector(result["photons"], len(f["q"]), "result.photons")
    require(all(v >= 0 for v in photons), "FINAL_PHOTON_POSITIVE_DOMAIN")
    require(all(v <= n + 2e-15 for v, n in zip(photons, f["amounts"])), "PHOTON_EXCEEDS_COHORT_BIRTH")
    led = result["ledgers"]
    photo = vector(led["photo"], 3, "ledgers.photo")
    ci = vector(led["ci"], 3, "ledgers.ci")
    rr = vector(led["rr"], 3, "ledgers.rr")
    for key in ("dr", "heat", "escape", "cmb", "photon_work", "gas_work", "source_n", "source_u"):
        number(led[key], "ledgers." + key)
    require(all(v >= 0 for v in photo + ci + rr) and
            all(led[k] >= 0 for k in ("dr", "heat", "escape", "photon_work", "gas_work", "source_n", "source_u")),
            "NEGATIVE_EVENT_OR_ESCAPE_LEDGER")
    initial = [n if b == f["x0"] else 0.0 for n, b in zip(f["amounts"], f["birth"])]
    source_n = math.fsum(n for n, b in zip(f["amounts"], f["birth"]) if b > f["x0"])
    source_u = math.fsum(n * q * math.exp(-b) for n, q, b in zip(f["amounts"], f["q"], f["birth"]) if b > f["x0"])
    require(close(source_n, led["source_n"], 2e-17), "SOURCE_NUMBER_LEDGER_MISMATCH")
    require(close(source_u, led["source_u"], 2e-16), "SOURCE_ENERGY_LEDGER_MISMATCH")
    initial_u = math.fsum(n * q * math.exp(-f["x0"]) for n, q in zip(initial, f["q"]))
    final_u = math.fsum(n * q * math.exp(-f["x0"] - f["dx"]) for n, q in zip(photons, f["q"]))
    delta_stock = [g[0] - f["gas0"][0], f["Y"] * (g[1] - f["gas0"][1]),
                   f["Y"] * (g[2] - f["gas0"][2])]
    net = [math.fsum((photo[j], ci[j], -rr[j], -led["dr"] if j == 1 else 0.0)) for j in range(3)]
    expected = [net[0], net[1] - net[2], net[2]]
    species_H = [a - b for a, b in zip(delta_stock, expected)]
    species_fraction = [species_H[0], species_H[1] / f["Y"] if f["Y"] else 0.0,
                        species_H[2] / f["Y"] if f["Y"] else 0.0]
    if not f["Y"]:
        require(all(v == 0 for v in photo[1:] + ci[1:] + rr[1:]) and led["dr"] == 0,
                "HELIUM_EVENTS_WITHOUT_HELIUM")
    binding_change = math.fsum((bind[0] * delta_stock[0], bind[1] * delta_stock[1],
                               (bind[1] + bind[2]) * delta_stock[2]))
    initial_binding = math.fsum((bind[0] * f["gas0"][0],
                                 f["Y"] * bind[1] * f["gas0"][1],
                                 f["Y"] * (bind[1] + bind[2]) * f["gas0"][2]))
    photon_terms = [math.fsum(initial), source_n, -math.fsum(photons), -math.fsum(photo)]
    energy_terms = [final_u - initial_u, g[3] - f["gas0"][3], binding_change,
                    led["escape"], -led["cmb"], led["photon_work"], led["gas_work"], -source_u]
    mass = math.fsum(photon_terms)
    energy = math.fsum(energy_terms)
    stored_species = vector(result["species_defect"], 3, "result.species_defect")
    stored_deltas = {"number_defect_H": mass - result["number_defect_H"],
                     "energy_defect_eV_H": energy - result["energy_defect_eV_H"],
                     "species_defect": [a - b for a, b in zip(species_fraction, stored_species)]}
    require(all(abs(v) < 2e-14 for v in [stored_deltas["number_defect_H"],
                                       stored_deltas["energy_defect_eV_H"], *stored_deltas["species_defect"]]),
            "STORED_BUDGET_RECOMPUTATION_MISMATCH")
    reconstructed_T = temperature(g, f["Y"], kb_ev)
    require(close(reconstructed_T, result["temperature_K"], 1e-9, 1e-13), "TEMPERATURE_RECONSTRUCTION")
    require(close(math.fsum(photons), result["photon_number"], 2e-17), "PHOTON_NUMBER_RECONSTRUCTION")
    require(close(final_u, result["photon_energy_eV_H"], 2e-15), "PHOTON_ENERGY_RECONSTRUCTION")
    return {"number_defect_H": mass, "energy_defect_eV_H": energy,
            "species_stock_defect_per_total_H": species_H, "species_fraction_defect": species_fraction,
            "photon_number": math.fsum(photons), "photon_energy_eV_H": final_u,
            "temperature_K": reconstructed_T, "source_number_from_fixture": source_n,
            "source_energy_from_fixture_eV_H": source_u,
            "binding_inventory_change_eV_H": binding_change,
            "number_terms_H": photon_terms, "energy_terms_eV_H": energy_terms,
            "number_defect_over_inventory": abs(mass) / max(math.fsum(initial) + source_n, 1e-300),
            "initial_total_photon_thermal_binding_energy_eV_H": initial_u + f["gas0"][3] + initial_binding,
            "energy_defect_over_initial_total_energy": abs(energy) / (initial_u + f["gas0"][3] + initial_binding),
            "recomputed_minus_recorded": stored_deltas,
            "assessment": "NUMERICALLY_CHECKED_LEDGER_CLOSURE_ONLY; consistency is not a model-accuracy certificate"}


def event_cuts(f, fit):
    lo, hi = f["x0"], f["x0"] + f["dx"]
    cuts = {lo, hi}
    for q, birth in zip(f["q"], f["birth"]):
        if lo < birth < hi:
            cuts.add(birth)
        for threshold in fit:
            cross = math.log(q / threshold)
            if max(lo, birth) < cross < hi:
                cuts.add(cross)
    return sorted(cuts)


def accepted_step_checks(raw, f, result, fit, nonlinear_tol, max_newton):
    rows = [parse_json(line, f"accepted_step_{i + 1}") for i, line in enumerate(raw.splitlines())]
    require(rows and len(rows) == result["steps"], "ACCEPTED_STEP_COUNT")
    cuts = event_cuts(f, fit)
    nsub = result["subdivisions_per_event_interval"]
    require(type(nsub) is int and nsub in LEVELS, "UNEXPECTED_REFINEMENT_LEVEL")
    require(len(rows) == nsub * (len(cuts) - 1), "EVENT_GRID_STEP_COUNT")
    grid = []
    for left, right in zip(cuts[:-1], cuts[1:]):
        for k in range(nsub):
            grid.append((left + (right - left) * k / nsub,
                         right if k + 1 == nsub else left + (right - left) * (k + 1) / nsub))
    previous_g = f["gas0"]
    previous_n = math.fsum(n for n, b in zip(f["amounts"], f["birth"]) if b == f["x0"])
    max_normalized = max_residual = max_stored_energy = max_number_balance = 0.0
    max_adjacent_jump = 0.0
    rhs_calls = 0
    accumulated_photo = [[], [], []]
    dt_total = []
    for i, (row, (expect_lo, expect_hi)) in enumerate(zip(rows, grid)):
        lo = number(row["x0"], "step.x0")
        hi = number(row["x1"], "step.x1")
        dt = number(row["dt_s"], "step.dt_s")
        require(hi > lo and dt > 0, f"STEP_TIME_DOMAIN: {i}")
        eps = 4 * max(math.ulp(expect_lo), math.ulp(expect_hi))
        require(abs(lo - expect_lo) <= eps and abs(hi - expect_hi) <= eps, f"EVENT_GRID_MISMATCH: {i}")
        if i:
            gap = lo - rows[i - 1]["x1"]
            max_adjacent_jump = max(max_adjacent_jump, abs(gap))
            require(gap == 0, f"STEP_GAP_OR_OVERLAP: {i}")
        gas = vector(row["gas"], 4, "step.gas")
        validate_gas(gas, f["Y"], f"accepted[{i}]")
        aggregate = number(row["n"], "step.n")
        require(aggregate >= 0, f"AGGREGATE_PHOTON_DOMAIN: {i}")
        photo = vector(row["photo_H"], 3, "step.photo_H")
        require(all(v >= 0 for v in photo), f"STEP_PHOTO_DOMAIN: {i}")
        residual = vector(row["residual"], 4, "step.residual")
        # Logged gas is after the second geometric half-step; the Newton thermal
        # scale belongs to the preceding state after the first geometric half-step.
        mid = 0.5 * (lo + hi)
        reaction_initial_w = previous_g[3] * math.exp(-2 * (mid - lo))
        normalized = max(abs(v) / scale for v, scale in zip(residual, (1, 1, 1, max(reaction_initial_w, 1e-8))))
        require(normalized <= nonlinear_tol, f"STEP_NEWTON_RESIDUAL_DOMAIN: {i}")
        require(type(row["iterations"]) is int and 0 <= row["iterations"] <= max_newton,
                f"STEP_NEWTON_ITERATION_DOMAIN: {i}")
        require(type(row["rhs_calls"]) is int and row["rhs_calls"] > 0, f"STEP_RHS_COUNT: {i}")
        number_defect = math.fsum([previous_n, -aggregate, -math.fsum(photo)])
        require(abs(number_defect) <= 2e-14, f"STEP_NUMBER_BALANCE: {i}")
        max_number_balance = max(max_number_balance, abs(number_defect))
        max_normalized = max(max_normalized, normalized)
        max_residual = max(max_residual, *map(abs, residual))
        max_stored_energy = max(max_stored_energy, abs(number(row["energy_defect"], "step.energy_defect")))
        number(row["number_defect"], "step.number_defect")
        for j, v in enumerate(photo):
            accumulated_photo[j].append(v)
        rhs_calls += row["rhs_calls"]
        dt_total.append(dt)
        previous_g = gas
        # Source impulses are committed after the row at their right boundary.
        births = math.fsum(n for n, b in zip(f["amounts"], f["birth"]) if b == hi and b > f["x0"])
        previous_n = aggregate + births
    require(rows[0]["x0"] == f["x0"] and rows[-1]["x1"] == f["x0"] + f["dx"], "TIME_COVERAGE")
    require(rows[-1]["gas"] == result["gas"], "TERMINAL_GAS_LOG_MISMATCH")
    require(close(previous_n, math.fsum(result["photons"]), 2e-16), "TERMINAL_PHOTON_LOG_MISMATCH")
    require(rhs_calls == result["rhs_calls"], "RHS_CALLS_SUM_MISMATCH")
    require(max_residual == result["max_step_nonlinear_residual"], "RECORDED_MAX_RESIDUAL_MISMATCH")
    require(max_stored_energy == result["max_step_energy_defect"], "RECORDED_MAX_ENERGY_DEFECT_MISMATCH")
    photo_sums = [math.fsum(v) for v in accumulated_photo]
    require(all(close(a, b, 2e-16) for a, b in zip(photo_sums, result["ledgers"]["photo"])), "PHOTO_LEDGER_SUM_MISMATCH")
    return {"rows": len(rows), "event_intervals": len(cuts) - 1, "event_cuts_x": cuts,
            "x_start": rows[0]["x0"], "x_end": rows[-1]["x1"], "proper_time_sum_s": math.fsum(dt_total),
            "max_gap_or_overlap_x": max_adjacent_jump,
            "max_normalized_newton_residual": max_normalized, "nonlinear_tolerance": nonlinear_tol,
            "max_raw_newton_residual": max_residual, "max_logged_step_energy_defect_eV_H": max_stored_energy,
            "max_recomputed_step_number_defect_H": max_number_balance,
            "summed_photo_events_H": photo_sums, "rhs_calls_from_accepted_steps": rhs_calls,
            "gas_domain_checked": True, "aggregate_photon_domain_checked": True,
            "per_cohort_accepted_step_domain": "NOT_RECORDED; only endpoint cohort vectors available",
            "individual_step_energy_reconstruction": "UNAVAILABLE_FROM_ACCEPTED_LOG; per-step nonphoto ledgers absent",
            "internal_trial_state_domain": "NOT_ASSESSED_FROM_ACCEPTED_STEPS"}


def component_values(result):
    return [*result["gas"], *result["photons"], result["temperature_K"],
            result["photon_number"], result["photon_energy_eV_H"]]


def component_metadata(f):
    names = [*GAS_NAMES, *[f"photon_{i:03d}" for i in range(len(f["q"]))],
             "temperature_K", "photon_total_H", "photon_energy_eV_H"]
    units = ["1", "1", "1", "eV/H"] + ["photons/H"] * len(f["q"]) + ["K", "photons/H", "eV/H"]
    return names, units


def component_errors(f, result, reference):
    names, units = component_metadata(f)
    actual, ref = component_values(result), component_values(reference)
    gas_scales = [1.0, 1.0, 1.0, f["gas0"][3]]
    deltas = [a - b for a, b in zip(actual, ref)]
    normalized_gas = [d / s for d, s in zip(deltas[:4], gas_scales)]
    active = max(range(4), key=lambda j: abs(normalized_gas[j]))
    rows = []
    for j, (name, unit, value, target, delta) in enumerate(zip(names, units, actual, ref, deltas)):
        rows.append({"component": name, "unit": unit, "value": value, "radau_value": target,
                     "signed_error": delta, "absolute_error": abs(delta),
                     "gas_scale": gas_scales[j] if j < 4 else None,
                     "signed_normalized_gas_error": normalized_gas[j] if j < 4 else None})
    metric = {"fraction_max_abs_error": max(map(abs, deltas[:3])),
              "thermal_abs_error_eV_H": abs(deltas[3]),
              "normalized_state_error": abs(normalized_gas[active]),
              "photon_max_abs_error": max(map(abs, deltas[4:4 + len(f["q"])])),
              "active_gas_component": names[active], "active_component_signed_error": deltas[active]}
    return rows, metric


def summary_matches_result(summary_row, result):
    require(set(summary_row) == set(result) | METRIC_KEYS, "SUMMARY_RESULT_KEYS")
    for key, value in result.items():
        require(summary_row[key] == value, f"SUMMARY_RESULT_MISMATCH: {key}")


def log_order(left, right):
    return math.log2(abs(left)) - math.log2(abs(right)) if left != 0 and right != 0 else None


def same_nonzero_sign(left, right):
    return left != 0 and right != 0 and (left > 0) == (right > 0)


def three_level_differences(values, levels=LEVELS):
    """Signed differences and order diagnostic; a sign reversal is never hidden."""
    rows = []
    for i in range(len(levels) - 2):
        n0, n1, n2 = levels[i:i + 3]
        require(n1 == 2 * n0 and n2 == 2 * n1, "NON_DYADIC_THREE_LEVEL_GRID")
        a, b, c = values[n0], values[n1], values[n2]
        delta0, delta1 = a - b, b - c
        resolution = 32 * max(math.ulp(a), math.ulp(b), math.ulp(c))
        rows.append({"n": n0, "n2": n1, "n4": n2,
                     "delta_n_n2": delta0, "delta_n2_n4": delta1,
                     "observed_p": log_order(delta0, delta1),
                     "same_difference_sign": same_nonzero_sign(delta0, delta1),
                     "roundoff_resolution_proxy": resolution,
                     "roundoff_sensitive": min(abs(delta0), abs(delta1)) <= resolution,
                     "status": "DIAGNOSTIC_REFERENCE_FREE_NOT_ORDER_PROOF"})
    return rows


def fit_inverse_powers(levels, values):
    require(len(levels) >= 2 and len(levels) == len(values), "FIT_INPUT_LENGTH")
    x, z = [1 / n for n in levels], [1 / n**2 for n in levels]
    xx = math.fsum(v * v for v in x)
    xz = math.fsum(a * b for a, b in zip(x, z))
    zz = math.fsum(v * v for v in z)
    xy = math.fsum(a * b for a, b in zip(x, values))
    zy = math.fsum(a * b for a, b in zip(z, values))
    det = xx * zz - xz * xz
    require(det > 0, "SINGULAR_FIT")
    A, B = (xy * zz - zy * xz) / det, (zy * xx - xy * xz) / det
    fitted = [A / n + B / n**2 for n in levels]
    residuals = [v - p for v, p in zip(values, fitted)]
    cross = -B / A if A else None
    sign_mismatches = [n for n, actual, prediction in zip(levels, values, fitted)
                       if actual != 0 and not same_nonzero_sign(actual, prediction)]
    brackets = [[levels[i], levels[i + 1]] for i in range(len(levels) - 1)
                if values[i] != 0 and values[i + 1] != 0
                and not same_nonzero_sign(values[i], values[i + 1])]
    observed_zeros = [n for n, v in zip(levels, values) if v == 0]
    crossing_within_observed_bracket = any(lo <= cross <= hi for lo, hi in brackets) if cross is not None else False
    if sign_mismatches or (brackets and not crossing_within_observed_bracket):
        crossing_status = "INADEQUATE_FOR_CROSSING_PREDICTION"
    elif brackets:
        crossing_status = "CONSISTENT_WITH_OBSERVED_SIGN_BRACKET_DIAGNOSTIC_ONLY"
    else:
        crossing_status = "NO_OBSERVED_SIGN_BRACKET_DIAGNOSTIC_ONLY"
    return {"levels": list(levels), "A": A, "B": B, "fitted": fitted,
            "signed_residuals": residuals,
            "max_abs_fit_residual": max(map(abs, residuals)),
            "zero_crossing_n_formal": cross,
            "zero_crossing_n_positive": cross if cross is not None and cross > 0 else None,
            "crossing_fit_assessment": {"status": crossing_status,
                                         "fitted_sign_mismatch_levels": sign_mismatches,
                                         "observed_sign_change_brackets": brackets,
                                         "observed_exact_zero_levels": observed_zeros,
                                         "formal_crossing_inside_observed_sign_bracket": crossing_within_observed_bracket,
                                         "certified_crossing_prediction": None},
            "status": "DIAGNOSTIC_LEAST_SQUARES_FIT_NOT_ASYMPTOTIC_CERTIFICATE"}


def thermal_cancellation(rows_by_mode, reference):
    result = {"definition": "d_n = w_MIDPHOTO_ENDMICRO(n) - w_FULLMID(n), in eV per total H",
              "rows": [], "fits": {}, "reference_uncertainty": "NOT_BOUNDED_BY_THIS_ARCHIVE; one Radau tolerance only"}
    hybrid_error, full_error, differences = [], [], []
    for n in LEVELS:
        h = rows_by_mode["MIDPHOTO_ENDMICRO"][n]["gas"][3] - reference["gas"][3]
        f = rows_by_mode["FULLMID"][n]["gas"][3] - reference["gas"][3]
        d = rows_by_mode["MIDPHOTO_ENDMICRO"][n]["gas"][3] - rows_by_mode["FULLMID"][n]["gas"][3]
        hybrid_error.append(h)
        full_error.append(f)
        differences.append(d)
        result["rows"].append({"n": n, "hybrid_signed_error": h, "fullmid_signed_error": f,
                               "d_n": d, "n_times_d_n": n * d,
                               "cancellation_ratio_abs_hybrid_over_fullmid": abs(h / f) if f else None})
    for label, indices in (("all_four_levels", range(4)), ("finest_three_levels", range(1, 4))):
        ns = [LEVELS[i] for i in indices]
        h = [hybrid_error[i] for i in indices]
        f = [full_error[i] for i in indices]
        d = [differences[i] for i in indices]
        hfit, ffit, dfit = [fit_inverse_powers(ns, v) for v in (h, f, d)]
        minus = fit_inverse_powers(ns, [a - b for a, b in zip(h, f)])
        plus = fit_inverse_powers(ns, [a + b for a, b in zip(h, f)])
        predictions = []
        for n in (128, 256, 512):
            ph = hfit["A"] / n + hfit["B"] / n**2
            pf = ffit["A"] / n + ffit["B"] / n**2
            predictions.append({"n": n, "hybrid_signed_error_fit": ph, "fullmid_signed_error_fit": pf,
                                "hybrid_to_fullmid_abs_error_fit": abs(ph / pf) if pf else None,
                                "status": "NOT_ADMISSIBLE_AS_PREDICTION; unexecuted algebraic fit evaluation"})
        result["fits"][label] = {"hybrid_minus_fullmid": dfit, "hybrid_minus_radau": hfit,
                                 "fullmid_minus_radau": ffit,
                                 "equal_abs_thermal_errors_n_hybrid_equals_fullmid": minus["zero_crossing_n_positive"],
                                 "equal_abs_thermal_errors_n_hybrid_equals_minus_fullmid": plus["zero_crossing_n_positive"],
                                 "unexecuted_extrapolation": predictions}
    result["claim_gate"] = ("Zero crossings and extrapolations are diagnostic fits to existing raw values. "
                            "No predicted grid was executed; no reference accuracy or asymptotic order is proved.")
    return result


def check_reference_survivors(f, reference):
    require(reference["reference_coordinates"] == "cumulative_optical_depth", "REFERENCE_COORDINATES")
    count = len(f["q"])
    tau = vector(reference["optical_depth"], count, "reference.optical_depth")
    logs = reference["log_survivor"]
    require(isinstance(logs, list) and len(logs) == count, "LOG_SURVIVOR_SHAPE")
    max_relative = max_log_difference = 0.0
    underflows = 0
    for i, (initial, optical, photons, stored_log) in enumerate(zip(f["amounts"], tau, reference["photons"], logs)):
        require(optical >= 0, "NEGATIVE_REFERENCE_OPTICAL_DEPTH")
        if initial == 0:
            require(photons == 0 and stored_log is None, f"ZERO_COHORT_REFERENCE: {i}")
            continue
        value = math.log(initial) - optical
        number(stored_log, "log_survivor")
        max_log_difference = max(max_log_difference, abs(value - stored_log))
        expected = math.exp(value)
        underflows += int(expected == 0)
        require(close(photons, expected, 0.0, 2e-13), f"REFERENCE_SURVIVOR_RECONSTRUCTION: {i}")
        if expected:
            max_relative = max(max_relative, abs(photons / expected - 1))
    require(max_log_difference < 2e-13, "LOG_SURVIVOR_RECONSTRUCTION")
    require(underflows == reference["underflowed_positive_cohorts"], "UNDERFLOW_COUNT_MISMATCH")
    require(reference["photon_clipping"] is False, "REFERENCE_CLIPPING_CONTRACT")
    return {"max_relative_survivor_reconstruction_error": max_relative,
            "max_log_survivor_reconstruction_error": max_log_difference,
            "underflowed_positive_cohorts": underflows,
            "max_optical_depth": max(tau), "min_terminal_photon": min(reference["photons"]),
            "scope": "Endpoint representation identity only; no re-integration or Radau-tolerance refinement"}


def analyze(source, evidence, receipt_paths, executable_manifest):
    source, evidence = Path(source).resolve(), Path(evidence).resolve()
    repo_root = source.parents[1]
    receipts, receipt_provenance = load_receipts(receipt_paths)
    reader = EvidenceReader(repo_root, evidence, receipts)
    manifest_raw = Path(executable_manifest).read_bytes()
    source_manifest = parse_json(manifest_raw, str(executable_manifest))
    require(source_manifest["path_base"] == source.relative_to(repo_root).as_posix(), "SOURCE_MANIFEST_PATH_BASE")
    source_identity = []
    for rel, expected in source_manifest["files"].items():
        raw = reader.read(source / safe_relative(rel), manifest=False)
        actual = hashes(raw)
        require(all(actual[k] == expected[k] for k in ("bytes", "sha256", "git_blob")),
                f"EXECUTED_SOURCE_IDENTITY_MISMATCH: {rel}")
        source_identity.append({"path": rel, **actual})
    literals = reader.read(source / "vendor/pr79/exposure_contract.py", manifest=False)
    bind = list(literal_from_source(literals, "BIND_EV"))
    ev_erg = literal_from_source(literals, "EV_ERG")
    fit = list(literal_from_source(reader.read(source / "vendor/pr79/radau_exposure_oracle.py", False), "FIT"))
    coupler = reader.read(source / "src/event_coupler.py", False)
    nonlinear_tol = literal_from_source(coupler, "nonlinear_tol", "Controls")
    max_newton = literal_from_source(coupler, "max_newton", "Controls")
    kb_ev = 1.380649e-16 / ev_erg
    owner = literal_from_source(reader.read(source / "src/native_micro.py", False), "OWNER")
    stored_owner = reader.read(evidence / "build/owner_commit.txt").decode().strip()
    require(owner == stored_owner, "NATIVE_OWNER_MISMATCH")
    build_inputs = {}
    for line in reader.read(evidence / "build/input_sha256.txt").decode().splitlines():
        require(bool(re.fullmatch(r"[a-f0-9]{64}  /.+", line)), "BUILD_INPUT_HASH_SCHEMA")
        digest, path = line.split("  ", 1)
        require(Path(path).name not in build_inputs, "DUPLICATE_BUILD_INPUT_BASENAME")
        build_inputs[Path(path).name] = {"recorded_path": path, "sha256": digest}
    native_source_hash = hashes(reader.read(source / "native/native_point.rs", False))["sha256"]
    require(build_inputs["native_point.rs"]["sha256"] == native_source_hash, "BRIDGE_SOURCE_BUILD_HASH_MISMATCH")
    binding_source = {"BIND_EV": bind, "EV_ERG": ev_erg, "kB_erg_K": 1.380649e-16,
                      "kB_eV_K": kb_ev, "FIT_CUTOFF_EV": fit, "owner_commit": owner,
                      "interpretation": "Binding energies belong to species stocks; fit cutoffs determine grid discontinuities."}
    output = {"schema": "C21F_RAW_NATIVE_EVIDENCE_ASSESSMENT_V1",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_root": str(evidence), "source_root": str(source),
              "source_execution_commit": source_manifest["source_commit"],
              "source_manifest_sha256": hashes(manifest_raw)["sha256"],
              "recorded_build_inputs": build_inputs,
              "binary_identity_scope": "Build receipt and process hashes cross-checked; executable binary bytes are not used by this analyzer",
              "executed_source_identity_verified": source_identity,
              "constants_from_source_authority": binding_source,
              "contracts": {
                  "state": "gas=(x_HII,y_HeII,z_HeIII,w_eV_per_total_H); Y=nHe_total/nH_total",
                  "photon": "per-total-H cohort stocks; q=E_eV*a; births at x=ln(a)",
                  "epoch": "Original fixture domain 1/21 <= a <= 1/5, 0 < delta_ln_a <= 0.1",
                  "matrix": {"lanes": list(LANES), "modes": list(MODES), "levels": list(LEVELS)},
                  "time": "Archive dates identify provenance only; scientific time is x=ln(a), proper intervals in seconds",
                  "normalization": "max(|dx_HII|,|dy_HeII|,|dz_HeIII|,|dw|/w_initial), gas components only",
                  "independence": "No solver imports, provider calls, point-replay calls, or IVP execution",
                  "reference": "Same physical kernel; archived Radau endpoint is a comparator with unbounded residual numerical uncertainty",
                  "scope": "Fixed source birth/spectrum and FLRW geometry; no Full48/source-age/spectral/angular/Case-B/Bianchi/full-EoR promotion"},
              "lanes": {}, "input_receipts": receipt_provenance}
    all_errors, all_orders, all_balances, all_cancellation = [], [], [], []
    for lane in LANES:
        directory = evidence / lane
        fixture = reader.obj(directory / "fixture.json")
        digest = validate_fixture(fixture)
        summary = reader.obj(directory / "SUMMARY.json")
        reference = reader.obj(directory / "radau.json")
        require(summary["fixture_sha256"] == digest == reference["fixture_sha256"], "LANE_FIXTURE_IDENTITY_MISMATCH")
        require(summary["schema"] == "C21E_COMPLETE_MATRIX_V1" and len(summary["cases"]) == 12, "SUMMARY_MATRIX_SCHEMA")
        require(summary["microphysics"] == reference["microphysics"] == "NATIVE_ORIGINAL_NONPHOTO_RUST", "MICROPHYSICS_LABEL_MISMATCH")
        require(summary["native_science"] is True and reference["status"] == summary["reference_status"] == "PASS_SCOPED_CONTINUOUS_IVP",
                "REFERENCE_EXECUTION_STATUS")
        ref_process = reader.obj(directory / "reference_process/native_process.json")
        require(ref_process["owner"] == owner, "REFERENCE_PROCESS_OWNER")
        require(ref_process["binary_sha256"] == build_inputs["native_point"]["sha256"], "REFERENCE_BINARY_BUILD_HASH_MISMATCH")
        require(reader.read(directory / "reference_process/native_stderr.log") == b"", "REFERENCE_STDERR_NONEMPTY")
        reference_balances = conserved_budgets(fixture, reference, bind, kb_ev)
        summary_rows = {}
        for row in summary["cases"]:
            key = (row["mode"], row["subdivisions_per_event_interval"])
            require(key not in summary_rows, "SUMMARY_DUPLICATE_CASE")
            summary_rows[key] = row
        require(set(summary_rows) == {(m, n) for m in MODES for n in LEVELS}, "SUMMARY_MISSING_OR_EXTRA_CASES")
        rows_by_mode = {m: {} for m in MODES}
        lane_out = {"fixture_canonical_sha256": digest, "fixture_raw_sha256": hashes((directory / "fixture.json").read_bytes())["sha256"],
                    "fixture": fixture, "cohort_count": len(fixture["q"]),
                    "reference": {"raw_result": reference, "independent_balances": reference_balances,
                                  "survivor_representation": check_reference_survivors(fixture, reference)},
                    "runs": {}, "orders_vs_radau": [], "reference_free_orders": []}
        for mode in MODES:
            for n in LEVELS:
                case = f"{mode}_{n:04d}"
                result = reader.obj(directory / case / "result.json")
                require(result["fixture_sha256"] == digest and result["mode"] == mode and result["subdivisions_per_event_interval"] == n,
                        f"RUN_IDENTITY: {lane}/{case}")
                require(result["microphysics"] == "NATIVE_ORIGINAL_NONPHOTO_RUST" and result["status"] == "PASS_SCOPED_FIXED_GRID_TRANSACTION",
                        f"RUN_STATUS: {lane}/{case}")
                summary_matches_result(summary_rows[(mode, n)], result)
                process = reader.obj(directory / case / "process/native_process.json")
                require(process["owner"] == owner and process["binary_sha256"] == ref_process["binary_sha256"], "PROCESS_OWNER_OR_BINARY_MISMATCH")
                require(reader.read(directory / case / "process/native_stderr.log") == b"", "RUN_STDERR_NONEMPTY")
                budgets = conserved_budgets(fixture, result, bind, kb_ev)
                steps = accepted_step_checks(reader.read(directory / case / "accepted_steps.jsonl"), fixture,
                                             result, fit, nonlinear_tol, max_newton)
                error_rows, metric = component_errors(fixture, result, reference)
                for key in METRIC_KEYS:
                    require(close(metric[key], summary_rows[(mode, n)][key], 2e-18, 1e-12), f"SUMMARY_METRIC_MISMATCH: {key}")
                lane_out["runs"][case] = {"result": result, "independent_balances": budgets, "accepted_steps": steps,
                                          "errors": error_rows, "gas_error_metric": metric,
                                          "process_binary_sha256": process["binary_sha256"]}
                rows_by_mode[mode][n] = result
                for row in error_rows:
                    all_errors.append({"lane": lane, "mode": mode, "n": n, **row})
                all_balances.append({"lane": lane, "mode": mode, "n": n,
                                     "number_defect_H": budgets["number_defect_H"], "energy_defect_eV_H": budgets["energy_defect_eV_H"],
                                     "HII_defect_H": budgets["species_stock_defect_per_total_H"][0],
                                     "HeII_defect_H": budgets["species_stock_defect_per_total_H"][1],
                                     "HeIII_defect_H": budgets["species_stock_defect_per_total_H"][2],
                                     "max_normalized_newton_residual": steps["max_normalized_newton_residual"],
                                     "normalized_state_error": metric["normalized_state_error"], "active_component": metric["active_gas_component"]})
        names, units = component_metadata(fixture)
        for mode in MODES:
            for j, (name, unit) in enumerate(zip(names, units)):
                values = {n: component_values(rows_by_mode[mode][n])[j] for n in LEVELS}
                for order in three_level_differences(values):
                    row = {"lane": lane, "mode": mode, "component": name, "unit": unit, **order}
                    lane_out["reference_free_orders"].append(row)
                    all_orders.append(row)
                target = component_values(reference)[j]
                for n, n2 in zip(LEVELS[:-1], LEVELS[1:]):
                    a, b = values[n] - target, values[n2] - target
                    lane_out["orders_vs_radau"].append({"mode": mode, "component": name, "unit": unit, "n": n, "n2": n2,
                                                          "signed_error_n": a, "signed_error_n2": b, "observed_p": log_order(a, b),
                                                          "same_error_sign": same_nonzero_sign(a, b)})
        lane_out["thermal_cancellation_diagnostic"] = thermal_cancellation(rows_by_mode, reference)
        for row in lane_out["thermal_cancellation_diagnostic"]["rows"]:
            all_cancellation.append({"lane": lane, **row})
        output["lanes"][lane] = lane_out
    verified = list(reader.records.values())
    output["verified_inputs"] = sorted(verified, key=lambda r: r["path"])
    output["verification_counts"] = {"selected_input_files": len(verified),
                                     "manifest_verified_raw_files": sum(r["immutable_manifest_verified"] for r in verified),
                                     "immutable_manifest_total_entries": len(reader.manifest),
                                     "runs": 24, "references": 2,
                                     "accepted_steps": sum(v["accepted_steps"]["rows"] for lane in output["lanes"].values() for v in lane["runs"].values()),
                                     "github_source_refs": sorted({r["source_ref"] for r in verified})}
    output["selected_evidence_assessment"] = "IMPLEMENTATION_VERIFIED_POSTPROCESSING_SCOPED"
    output["unverified_archive_payloads"] = sorted(set(reader.manifest) - {
        str((repo_root / r["path"]).relative_to(evidence)) for r in verified if r["immutable_manifest_verified"]})
    return output, {"component_errors.csv": all_errors, "reference_free_orders.csv": all_orders,
                    "balances_and_metrics.csv": all_balances, "thermal_cancellation.csv": all_cancellation}


def write_products(out, assessment, tables):
    out = Path(out)
    require(not out.exists(), f"OUTPUT_ALREADY_EXISTS_CREATE_ONLY: {out}")
    out.mkdir(parents=True, exist_ok=False)
    with (out / "ASSESSMENT.json").open("x", encoding="utf-8") as stream:
        json.dump(assessment, stream, indent=2, allow_nan=False)
        stream.write("\n")
    for filename, rows in tables.items():
        require(rows, f"EMPTY_OUTPUT_TABLE: {filename}")
        with (out / filename).open("x", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    products = {p.name: hashes(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}
    with (out / "PRODUCT_HASHES.json").open("x", encoding="utf-8") as stream:
        json.dump(products, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--executable-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        require(not args.out.exists(), f"OUTPUT_ALREADY_EXISTS_CREATE_ONLY: {args.out}")
        assessment, tables = analyze(args.source, args.evidence, args.receipts, args.executable_manifest)
        write_products(args.out, assessment, tables)
        print(json.dumps({"status": assessment["selected_evidence_assessment"],
                          "counts": assessment["verification_counts"], "out": str(args.out.resolve())}))
        return 0
    except (EvidenceError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "EVIDENCE_ASSESSMENT_REJECTED", "type": type(exc).__name__, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
