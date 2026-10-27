#!/usr/bin/env python3
"""Evaluate only four exact-half oracle repairs from the saved independent run.

Author: /root/theory_review (original independent-reference/theory author;
not production author).  No production or original reference module imports.
The original 3446 PASS rows and four FAILED rows are immutable input evidence.
Only s=N*(1-2*f)-p at the declared p=0,f=1/2 boundary is newly evaluated,
using Fraction on the original independent window_reference decimal strings.
No fit, moment primitive, Q8 projection, source or RR propagation is rerun.
This source is unexecuted until root's revised manifest/budget dispatch.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import sys


UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
UNIT = Path(__file__).resolve().parents[1]
CONTRACT_SHA = "01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162"
MANIFEST_SHA = "2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3"
ORIGINAL_RESULT = {"path": "runs/independent_v1/RESULT.json", "bytes": 1651412,
                   "sha256": "fedc2a34a857f5de7c8035db580bdc746319366914efa9094a36a71e6923f8c9"}
ORIGINAL_RECEIPT = {"path": "runs/independent_v1/RECEIPT.json", "bytes": 12103,
                    "sha256": "8b033baf8c39fd45ec75eadd5ae478c108f34144f1e8f54838224d16e25cf756"}
ORIGINAL_CODE = {"path": "runs/independent_v1/EXECUTED_SOURCE/implementation_independent_reference.py",
                 "bytes": 61964, "sha256": "52511cdb8762b4a33b125bbeb72e46adfdeb7acc6c793d20622785ad1f786f55"}
ORIGINAL_MANIFEST = {"path": "runs/independent_v1/EXECUTED_SOURCE_MANIFEST.json", "bytes": 1036,
                     "sha256": "98785041f04fe422ad4068b7457259a2f4b0a1b41032662124a8fa7464b59641"}
PRIMARY = {"path": "runs/primary_v2/RESULT.json", "bytes": 399835,
           "sha256": "efbd18ba864982ca6436345b1d25d75ad084b3c5f77db6e3bb40186db07b4901"}
TARGETS = ("prefixes.0.fixture.2.s_m3", "prefixes.2.fixture.2.s_m3",
           "prefixes.3.fixture.2.s_m3", "observation_bins.0.fixture.2.s_m3")
TOLERANCE = Fraction(1, 100000000000)  # unchanged 1e-11, no floor


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "Duplicate JSON key")
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError("Nonfinite JSON constant: " + value)


def decode(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def resolve_unit(value):
    candidate = Path(value)
    path = candidate if candidate.is_absolute() else UNIT / candidate
    need(path == path.resolve() and path.is_relative_to(UNIT), "Exact nonsymlink unit-local path required")
    return path


def read_pinned(pin):
    path = resolve_unit(pin["path"])
    need(path.is_file() and not path.is_symlink(), "Regular pinned input required")
    raw = path.read_bytes()
    need(len(raw) == pin["bytes"] and sha(raw) == pin["sha256"], "Actual input byte pin mismatch: " + pin["path"])
    return raw


def rational(value):
    """Exact lift of the saved decimal/rational text, without Decimal arithmetic."""
    need(type(value) is str and bool(value), "Saved numeric text required")
    if "/" in value:
        numerator, denominator = value.split("/")
        need(numerator.lstrip("+-").isdigit() and denominator.lstrip("+-").isdigit(),
             "Integer rational text required")
        return Fraction(int(numerator), int(denominator))
    decimal = Decimal(value)  # construction preserves every supplied digit
    need(decimal.is_finite(), "Finite saved decimal required")
    return Fraction(decimal)


def fraction_text(value):
    return str(value.numerator) if value.denominator == 1 else str(value.numerator) + "/" + str(value.denominator)


def write_new(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {"path": str(path.relative_to(UNIT)), "bytes": len(raw), "sha256": sha(raw)}


def guard(argv):
    need(argv.count("--out") == 1 and not any(value.startswith("--out=") for value in argv),
         "Exactly one canonical --out required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--failed-reference", required=True)
    parser.add_argument("--primary", required=True)
    args = parser.parse_args(argv)
    out = resolve_unit(args.out)
    need(out.name == "independent_v2" and out.parent == UNIT / "runs" and out.is_dir(),
         "Unique root-reserved independent_v2 directory required")
    need(not (out / "RESULT.json").exists() and not (out / "ACCEPTED_REFERENCE.json").exists(),
         "Create-only recovery outputs required")
    need(resolve_unit(args.failed_reference) == UNIT / ORIGINAL_RESULT["path"]
         and resolve_unit(args.primary) == UNIT / PRIMARY["path"], "Only the exact observed failure/primary pair is supported")
    need(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID
         and os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "Actual bounded runner environment required")
    reservation = decode((out / "RESERVATION.json").read_bytes())
    need(reservation.get("unit") == UNIT_ID and reservation.get("run_id") == out.name
         and reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID")
         and bool(reservation.get("attempt_id")), "Exact current attempt reservation required")
    budget_raw = (UNIT / "EXECUTION_BUDGET.json").read_bytes()
    budget = decode(budget_raw)
    need(budget.get("unit") == UNIT_ID and budget.get("budget_id") == "CR_PARENT_EVENT_20261028_NEW40"
         and budget.get("status") == "FROZEN_C4_ADMITTED" and budget.get("local_science_cpu_cap_s") == 40
         and budget.get("historical_allowance_transferred") is False
         and budget.get("parallel_project_budget_transferred") is False, "Same-unit revised admitted 40 CPU budget required")
    allocations = [a for a in budget["run_allocations"] if a.get("run_id") == out.name]
    need(len(allocations) == 1 and allocations[0].get("role") == "independent"
         and allocations[0].get("worker_cpu_reservation_s") == 6
         and allocations[0].get("coordinator_cpu_reservation_s") == 2.05
         and allocations[0].get("selected_memory_limit_bytes") == 268435456,
         "Existing independent cap6/coordinator2.05/256MiB contract required")
    need(budget.get("native_threads") == 1 and all(os.environ.get(key) == "1" for key in
         ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")),
         "One-thread environment required")
    need(sha((UNIT / "CONTRACT.json").read_bytes()) == CONTRACT_SHA
         and sha((UNIT / "inputs/INPUT_MANIFEST.json").read_bytes()) == MANIFEST_SHA,
         "Frozen contract/input manifest changed")
    return out, reservation, sha(budget_raw)


def verify_original():
    original = decode(read_pinned(ORIGINAL_RESULT))
    primary = decode(read_pinned(PRIMARY))
    receipt = decode(read_pinned(ORIGINAL_RECEIPT))
    read_pinned(ORIGINAL_CODE)
    manifest = decode(read_pinned(ORIGINAL_MANIFEST))
    source_rows = [r for r in manifest if r.get("path") == "implementation/independent_reference.py"]
    need(len(source_rows) == 1 and source_rows[0].get("sha256") == ORIGINAL_CODE["sha256"]
         and source_rows[0].get("bytes") == ORIGINAL_CODE["bytes"], "Original executed reference identity mismatch")
    need(original.get("schema") == "CR_PARENT_EVENT_INDEPENDENT_REFERENCE_V1"
         and original.get("unit") == UNIT_ID and original.get("status") == "FAILED"
         and original.get("primary") == PRIMARY and original.get("production_imports") == []
         and original.get("old_science_replays") == 0, "Exact original FAILED independent run required")
    checks = original["checks"]
    need(len(checks) == 3450 and len({row["id"] for row in checks}) == 3450
         and sum(row["pass"] is True for row in checks) == 3446
         and all(type(row["pass"]) is bool for row in checks), "Original actual check inventory mismatch")
    failed = {row["id"]: row for row in checks if row["pass"] is False}
    need(set(failed) == set(TARGETS) and original["acceptance"]["executed"] == 3450
         and original["acceptance"]["passed"] == 3446 and original["acceptance"]["failed"] == 4
         and original["acceptance"]["inherited_checks_added"] == 0, "Exact four observed oracle failures required")
    for row in failed.values():
        need(row["category"] == "conditional_family" and row["observed"] == "0"
             and row["tolerance"] == "1E-11" and row["zero_rule"] == "exact when scale is zero",
             "Original failure semantics changed")
    need(primary.get("unit") == UNIT_ID and primary.get("schema") == "CR_PARENT_EVENT_RESULT_V1"
         and primary.get("status") == "PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN", "Exact accepted primary required")
    need(receipt.get("unit") == UNIT_ID and receipt.get("run_id") == "independent_v1"
         and receipt.get("status") == "failed" and receipt.get("terminal_debit") is True
         and receipt.get("cpu_accounting_complete") is True, "Original failed cost receipt must remain acknowledged")
    return original, primary, receipt, failed


def recover_four(original, primary, failed, rows):
    for ident in TARGETS:
        group, index_text, _, fixture_text, _ = ident.split(".")
        index, fixture_index = int(index_text), int(fixture_text)
        saved = original["window_reference"][group][index]
        fixture = primary[group][index]["conditional_closed_He_family"][fixture_index]
        need(saved["interval_s"] == primary[group][index]["interval_s"], "Saved window/primary mismatch")
        N_text = saved["source"]["He"]["number_m3"]
        N = rational(N_text)
        fraction = rational(fixture["d_fraction_of_selected_He"])
        p = rational(fixture["p_m3"])
        need(N > 0 and fraction == Fraction(1, 2) and p == 0
             and fixture.get("label") == "all_selected_pairs_fixture"
             and fixture.get("conditional") is True and fixture.get("actual_branch_measurement") is False
             and fixture.get("actual_full_native25") is None, "Only declared positive-N/p0/half conditional fixture is admitted")
        # Independent exact arithmetic on saved independent N.  No production
        # coefficient or already rounded d is used to construct the expectation.
        expected = N * (1 - 2 * fraction) - p
        observed = rational(fixture["s_m3"])
        difference = abs(observed - expected)
        scale = max(abs(observed), abs(expected))
        relative = difference / scale if scale else Fraction(0)
        passed = difference == 0 if scale == 0 else relative <= TOLERANCE
        rows.append({"id": ident, "category": "conditional_family", "pass": passed,
            "observed": fixture["s_m3"], "expected": fraction_text(expected),
            "absolute_difference": fraction_text(difference), "scale": fraction_text(scale),
            "relative_error": fraction_text(relative), "tolerance": "1E-11",
            "zero_rule": "exact when scale is zero", "comparison": "exact Fraction, same frozen own-scale criterion",
            "independent_N_decimal_as_saved": N_text,
            "independent_N_json_pointer": "/window_reference/" + group + "/" + index_text + "/source/He/number_m3",
            "identity": "s=N*(1-2*f)-p; p=0, f=1/2 implies exact s=0",
            "exact_expected_fraction": {"numerator": expected.numerator, "denominator": expected.denominator},
            "superseded_original_oracle_failure": failed[ident],
            "old_successful_check_reexecuted": False})
    return rows


def composite(original, recovery, recovery_pin, rows):
    replacement = {row["id"]: row for row in rows}
    accepted = [replacement.get(row["id"], row) for row in original["checks"]]
    need(len(accepted) == 3450 and len(replacement) == 4
         and all(row["pass"] is True for row in accepted), "Composite only exists after all four new checks pass")
    groups = {}
    for row in accepted:
        group = groups.setdefault(row["category"], {"unique_checks": 0, "passed": 0, "failed": 0,
                                                   "max_relative_error": "0"})
        group["unique_checks"] += 1
        group["passed" if row["pass"] else "failed"] += 1
        if "relative_error" in row and Decimal(row["relative_error"]) > Decimal(group["max_relative_error"]):
            group["max_relative_error"] = row["relative_error"]
    return {"schema": "CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1", "unit": UNIT_ID,
        "status": "PASS_SCOPED_INDEPENDENT_REFERENCE_COMPOSITE", "primary": PRIMARY,
        "production_imports": [], "old_science_replays": 0, "inherited_checks_added": 0,
        "source_results": {"original_reference": ORIGINAL_RESULT, "targeted_recovery": recovery_pin,
                           "original_failed_receipt": ORIGINAL_RECEIPT, "original_executed_reference": ORIGINAL_CODE},
        "acceptance": {"unique_checks": 3450, "passed": 3450, "failed": 0,
                       "actual_evaluations": 3454, "reused_passed_checks": 3446,
                       "newly_evaluated_checks": 4, "previous_failed_evaluations": 4,
                       "inherited_checks_added": 0, "by_category": groups},
        "actual_evaluation_history": {
            "original": {"status": "FAILED", "executed": 3450, "passed": 3446, "failed": 4},
            "targeted_recovery": {"status": recovery["status"], "executed": 4, "passed": 4, "failed": 0}},
        "checks": accepted, "superseded_oracle_failures": [row for row in original["checks"] if row["pass"] is False],
        "full_reference_rerun": False, "old_successful_checks_reexecuted": 0,
        "primary_recomputed": False, "fit_or_Q8_or_old_source_or_RR_replay": 0,
        "original_failure_erased": False, "exact_zero_oracle_repaired_not_tolerance_relaxed": True,
        "arithmetic_interval_certificate": False, "physical_heating_complete": False,
        "global_physical_completion": None, "global_physical_error": None,
        "actual_full_native25": None, "actual_external_work": None, "global_budget_remaining": None, "currency": None,
        "resource_accounting": "Original failed and new targeted attempts remain separately charged by the runner ledger",
        "accepted_row_provenance": "3446 original PASS rows copied byte-value-for-byte-value; only the four named oracle checks replaced"}


def main(argv=None):
    out, reservation, budget_sha = guard(sys.argv[1:] if argv is None else list(argv))
    result = {"schema": "CR_PARENT_EVENT_INDEPENDENT_TARGETED_RECOVERY_V1", "unit": UNIT_ID,
        "author_role": "original independent-reference/theory author; not production author",
        "run_id": out.name, "attempt_id": reservation["attempt_id"], "budget_sha256": budget_sha,
        "primary": PRIMARY, "original_reference": ORIGINAL_RESULT, "original_failed_receipt": ORIGINAL_RECEIPT,
        "original_executed_reference": ORIGINAL_CODE, "original_executed_manifest": ORIGINAL_MANIFEST,
        "selected_check_ids": list(TARGETS), "production_imports": [],
        "old_science_replays": 0, "old_successful_checks_reexecuted": 0,
        "fit_or_Q8_or_old_source_or_RR_replay": 0, "tolerance_changed": False, "absolute_floor_added": False,
        "original_reference_file_modified": False, "original_failure_erased": False,
        "original_status_as_saved": "FAILED", "scope": "only four exact-half conditional-family scalar identities",
        "metadata_accounting_not_new_checks": "Input pin/guard validation and aggregation of prior boolean check records",
        "resource_accounting": "Actual runner RECEIPT and immutable debit ledger; no self-reported CPU success"}
    rows, original = [], None
    try:
        original, primary, receipt, failed = verify_original()
        recover_four(original, primary, failed, rows)
        for pin in (ORIGINAL_RESULT, ORIGINAL_RECEIPT, ORIGINAL_CODE, ORIGINAL_MANIFEST, PRIMARY):
            read_pinned(pin)
        result["original_failed_cost_as_saved"] = {key: receipt[key] for key in
            ("attempt_id", "status", "worker_cpu_s", "coordinator_cpu_through_receipt_s",
             "receipt_tail_reserve_s", "charged_cpu_s")}
    except Exception as error:
        result["fatal_exception"] = {"type": type(error).__name__, "message": str(error)}
    result["checks"] = rows
    result["acceptance"] = {"executed": len(rows), "passed": sum(row["pass"] for row in rows),
                             "failed": sum(not row["pass"] for row in rows), "inherited_checks_added": 0}
    passed = len(rows) == 4 and all(row["pass"] for row in rows) and "fatal_exception" not in result
    result["status"] = "PASS_SCOPED_EXACT_HALF_RECOVERY" if passed else "FAILED_TARGETED_RECOVERY"
    result_pin = write_new(out / "RESULT.json", result)
    accepted_pin = None
    if passed:
        accepted_pin = write_new(out / "ACCEPTED_REFERENCE.json", composite(original, result, result_pin, rows))
    print(json.dumps({"unit": UNIT_ID, "status": result["status"], "new_checks": result["acceptance"],
                      "RESULT": result_pin, "ACCEPTED_REFERENCE": accepted_pin}, allow_nan=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
