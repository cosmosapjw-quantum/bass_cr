"""Measured-runner entry point for independent saved-certificate checking.

Authoring only: this file was not executed/imported/compiled by its author.
Invocation: python implementation/independent.py OUTDIR [--input INPUT_JSON]
Only the frozen reference and explicit saved JSON are read.  No production
module, source fit, NPZ loader, old consumer, or CAS is imported here.
"""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import traceback
from types import ModuleType


UNIT = "CR_PHYS02_HE_ENERGY_SUM_V1"
SCHEMA = "CR_HE_ENERGY_SUM_INDEPENDENT_RESULT_V1"
EXPECTED_REFERENCE_SHA256 = "58ede1228866a8ca29cce838b7fbfb473c872ea9ef20ec0faf69066df276983b"
EXPECTED_SMALL_CASES = 48
EXPECTED_NATIVE_CASES = 9
EXPECTED_NATIVE_ATOMS = 3201


class IndependentCheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise IndependentCheckError(message)


def exact(value):
    require(type(value) in (int, str, Fraction), "EXACT_SCALAR_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise IndependentCheckError("FINITE_EXACT_SCALAR_REQUIRED") from exc


def json_exact(value):
    if type(value) is Fraction:
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_exact(v) for v in value]
    return value


class Groups:
    """Count explicit worker groups, not every internal reference predicate."""

    def __init__(self):
        self.records = []
        self.failures = []

    def check(self, group_id, kind, action, *, result_path):
        try:
            result = action()
        except Exception as exc:
            failure = {
                "group_id": group_id,
                "exception": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            self.records.append({
                "id": group_id, "kind": kind, "status": "FAIL",
                "result_path": result_path, "failure_index": len(self.failures),
            })
            self.failures.append(failure)
            return False, None
        reused = isinstance(result, dict) and result.get("evidence_reused") is True
        self.records.append({
            "id": group_id, "kind": kind,
            "status": "PASS_REUSED_IDENTICAL_ARGUMENTS" if reused else "PASS",
            "result_path": result_path,
        })
        return True, result

    def skip(self, group_id, kind, reason, *, result_path):
        self.records.append({
            "id": group_id, "kind": kind, "status": "NOT_RUN",
            "reason": reason, "result_path": result_path,
        })

    def summary(self):
        return {
            "total": len(self.records),
            "passed": sum(r["status"].startswith("PASS") for r in self.records),
            "fresh_passed": sum(r["status"] == "PASS" for r in self.records),
            "reused_passed": sum(
                r["status"] == "PASS_REUSED_IDENTICAL_ARGUMENTS"
                for r in self.records
            ),
            "failed": sum(r["status"] == "FAIL" for r in self.records),
            "not_run": sum(r["status"] == "NOT_RUN" for r in self.records),
            "counting_rule": "Explicit named worker groups; internal reference predicates are not counted separately.",
        }


def read_input(path):
    raw = path.read_bytes()

    def reject_constant(value):
        raise IndependentCheckError("NONFINITE_JSON_LITERAL:" + value)

    data = json.loads(raw, parse_constant=reject_constant)
    require(type(data) is dict, "PRIMARY_OBJECT_REQUIRED")
    require(data.get("unit") == UNIT, "PRIMARY_UNIT_IDENTITY_MISMATCH")
    for field in ("small_cases", "native_atoms", "native_cases"):
        require(type(data.get(field)) is list, "PRIMARY_LIST_REQUIRED:" + field)
    return {
        "data": data,
        "metadata": {
            "path": str(path), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
    }


def load_frozen_reference(path):
    """Execute exactly the byte string whose digest was checked."""
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == EXPECTED_REFERENCE_SHA256, "FROZEN_REFERENCE_SHA_MISMATCH")
    module = ModuleType("cr_he_energy_sum_frozen_independent_reference")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    require(module.FIXTURE_COUNT == EXPECTED_SMALL_CASES, "REFERENCE_FIXTURE_COUNT_MISMATCH")
    return {
        "module": module,
        "metadata": {
            "path": str(path), "bytes": len(raw), "sha256": digest,
            "expected_sha256": EXPECTED_REFERENCE_SHA256,
            "production_imports": False,
        },
    }


def verify_coverage(data, fixtures):
    require(len(fixtures) == EXPECTED_SMALL_CASES, "REFERENCE_FIXTURE_SET_SIZE")
    fixture_ids = [fixture["id"] for fixture in fixtures]
    require(len(set(fixture_ids)) == len(fixture_ids), "REFERENCE_FIXTURE_IDS_DUPLICATED")
    cases = data["small_cases"]
    require(len(cases) == EXPECTED_SMALL_CASES, "PRIMARY_SMALL_CASE_COUNT_MISMATCH")
    require(all(type(case) is dict for case in cases), "SMALL_CASE_OBJECT_REQUIRED")
    case_ids = [case.get("id") for case in cases]
    require(case_ids == fixture_ids, "PRIMARY_SMALL_FIXTURE_ID_OR_ORDER_MISMATCH")

    native = data["native_cases"]
    require(len(native) == EXPECTED_NATIVE_CASES, "PRIMARY_NATIVE_CASE_COUNT_MISMATCH")
    require(all(type(case) is dict for case in native), "NATIVE_CASE_OBJECT_REQUIRED")
    native_ids = [case.get("id") for case in native]
    require(
        all(type(ident) is str and ident for ident in native_ids),
        "NATIVE_NONEMPTY_CASE_ID_REQUIRED",
    )
    require(len(set(native_ids)) == len(native_ids), "NATIVE_CASE_ID_DUPLICATED")
    require(len(data["native_atoms"]) == EXPECTED_NATIVE_ATOMS, "NATIVE_ATOM_COUNT_MISMATCH")
    return {
        "small_case_count": len(cases),
        "native_case_count": len(native),
        "native_atom_count": len(data["native_atoms"]),
        "small_ids": case_ids,
        "native_ids": native_ids,
    }


def parse_case(case, atoms, expected_fixture=None):
    require(type(case) is dict, "CASE_OBJECT_REQUIRED")
    require(type(case.get("id")) is str and case["id"], "CASE_ID_REQUIRED")
    require(type(atoms) is list, "ATOM_RECORD_LIST_REQUIRED")
    for field in ("K_eV", "dmax", "target_d", "dual_by_key", "max_events", "events"):
        require(field in case, "CASE_FIELD_MISSING:" + field)
    require(type(case["dual_by_key"]) is dict, "DUAL_MAP_REQUIRED")
    require(type(case["max_events"]) is list, "MAX_EVENT_LIST_REQUIRED")
    require(type(case["events"]) is list, "TARGET_EVENT_LIST_REQUIRED")

    cap = exact(case["K_eV"])
    maximum = exact(case["dmax"])
    target = exact(case["target_d"])
    require(cap >= 0 and maximum >= 0, "NONNEGATIVE_CAP_AND_MAXIMUM_REQUIRED")
    require(0 <= target <= maximum, "TARGET_OUTSIDE_DECLARED_INTERVAL")
    energies = []
    weights = []
    for atom in atoms:
        require(type(atom) is dict, "ATOM_OBJECT_REQUIRED")
        for field in ("key", "energy_eV", "coefficient"):
            require(field in atom, "ATOM_FIELD_MISSING:" + field)
        energies.append(exact(atom["energy_eV"]))
        weights.append(exact(atom["coefficient"]))
    require(all(e >= 0 for e in energies), "NONNEGATIVE_ENERGIES_REQUIRED")
    require(all(w >= 0 for w in weights), "NONNEGATIVE_WEIGHTS_REQUIRED")

    if expected_fixture is not None:
        require(case["id"] == expected_fixture["id"], "FIXTURE_ID_MISMATCH")
        require(tuple(energies) == expected_fixture["energies"], "FIXTURE_ENERGIES_MISMATCH")
        require(tuple(weights) == expected_fixture["weights"], "FIXTURE_WEIGHTS_MISMATCH")
        require(cap == expected_fixture["K"], "FIXTURE_CAP_MISMATCH")
    return {
        "K": cap, "dmax": maximum, "target_d": target,
        "energies": tuple(energies), "weights": tuple(weights),
        "atom_count": len(atoms),
    }


def compare_oracle(reference, parsed, fixture):
    result = reference.dual_oracle(
        parsed["energies"], parsed["weights"], parsed["K"]
    )
    require(result["dmax"] == parsed["dmax"], "PRODUCTION_ORACLE_MAXIMUM_MISMATCH")
    anchor = fixture["analytic_anchor_dmax"]
    if anchor is not None:
        require(result["dmax"] == anchor, "MANUAL_ANCHOR_ORACLE_MISMATCH")
    result["manual_anchor_dmax"] = anchor
    result["production_dmax_equal"] = True
    return result


def maximum_certificate(reference, case, atoms, parsed):
    return reference.verify_certificate(
        atoms, parsed["K"], case["max_events"], case["dual_by_key"],
        expected_dmax=parsed["dmax"], target_d=parsed["dmax"],
        require_optimal=True,
    )


def target_certificate(reference, case, atoms, parsed, maximum, maximum_group):
    # Exact same records, same atom list/K/dual, and same requested d are the
    # same mathematical check.  Reuse is explicit; a distinct target is run.
    if (
        maximum is not None
        and parsed["target_d"] == parsed["dmax"]
        and case["events"] == case["max_events"]
    ):
        require(
            maximum["double_coefficient"] == parsed["target_d"],
            "REUSED_TARGET_MASS_MISMATCH",
        )
        return {
            "evidence_reused": True,
            "source_group": maximum_group,
            "identity_basis": "Same atoms, K, explicit dual, exact event records and target_d=dmax.",
            "performed_additional_reference_evaluation": False,
            "certificate": maximum,
        }
    result = reference.verify_certificate(
        atoms, parsed["K"], case["events"], case["dual_by_key"],
        expected_dmax=parsed["dmax"], target_d=parsed["target_d"],
        require_optimal=False,
    )
    return {
        "evidence_reused": False,
        "performed_additional_reference_evaluation": True,
        "certificate": result,
    }


def process_case(groups, reference, case, atoms, index, kind, fixture=None):
    prefix = kind + "." + str(index)
    result_path = "results." + kind + "[" + str(index) + "]"
    row = {"id": case.get("id") if type(case) is dict else None}
    parsed_ok, parsed = groups.check(
        prefix + ".input", "EXACT_INPUT_AND_FIXTURE_IDENTITY",
        lambda: parse_case(case, atoms, fixture),
        result_path=result_path + ".input",
    )
    if not parsed_ok:
        row["input"] = None
        for label in (("oracle",) if fixture is not None else ()) + ("maximum", "target"):
            groups.skip(
                prefix + "." + label, "DEPENDENT_CASE_CHECK",
                "Exact case input group failed.",
                result_path=result_path + "." + label,
            )
        return row
    row["input"] = {
        key: parsed[key] for key in ("K", "dmax", "target_d", "atom_count")
    }
    if fixture is not None:
        _, row["oracle"] = groups.check(
            prefix + ".oracle", "EXHAUSTIVE_GENERIC_DUAL_ORACLE",
            lambda: compare_oracle(reference, parsed, fixture),
            result_path=result_path + ".oracle",
        )
    _, row["maximum"] = groups.check(
        prefix + ".maximum", "EXACT_FULL_PRIMAL_DUAL_CERTIFICATE",
        lambda: maximum_certificate(reference, case, atoms, parsed),
        result_path=result_path + ".maximum",
    )
    _, row["target"] = groups.check(
        prefix + ".target", "EXACT_REQUESTED_TARGET_CERTIFICATE",
        lambda: target_certificate(
            reference, case, atoms, parsed, row["maximum"], prefix + ".maximum"
        ),
        result_path=result_path + ".target",
    )
    return row


def run(input_path, reference_path):
    groups = Groups()
    result = {
        "schema": SCHEMA,
        "unit": UNIT,
        "status": "FAIL",
        "sourcefile_SHA256": None,
        "primary_input": None,
        "reference": None,
        "results": {"small": [], "native": []},
        "scope": {
            "claim": "Exact finite conditional energy-sum event envelope and explicit saved certificates.",
            "actual_physical_completion": None,
            "actual_K": None,
            "actual_kernel": None,
            "actual_C": None,
            "actual_D": None,
            "actual_full_native25": None,
            "physical_activation": False,
            "source_fit_replays": 0,
            "NPZ_loads": 0,
            "production_imports": 0,
            "CPU_accounting": "External measured runner; no additional allowance is created here.",
        },
    }
    input_ok, loaded = groups.check(
        "global.input", "PRIMARY_SAVED_FILE_AND_UNIT",
        lambda: read_input(input_path),
        result_path="primary_input",
    )
    reference_ok, loaded_reference = groups.check(
        "global.reference", "FROZEN_REFERENCE_BYTES_AND_LOAD",
        lambda: load_frozen_reference(reference_path),
        result_path="reference",
    )
    if input_ok:
        result["primary_input"] = loaded["metadata"]
        result["sourcefile_SHA256"] = loaded["metadata"]["sha256"]
    if reference_ok:
        result["reference"] = loaded_reference["metadata"]

    if input_ok and reference_ok:
        data = loaded["data"]
        reference = loaded_reference["module"]
        fixture_ok, fixtures = groups.check(
            "global.fixtures", "INDEPENDENT_FIXTURE_CONSTRUCTION",
            reference.deterministic_fixtures,
            result_path="fixture_inventory",
        )
        if fixture_ok:
            coverage_ok, coverage = groups.check(
                "global.coverage", "EXPECTED_CASE_AND_NATIVE_ATOM_INVENTORY",
                lambda: verify_coverage(data, fixtures),
                result_path="coverage",
            )
            result["coverage"] = coverage
            result["fixture_inventory"] = {
                "count": len(fixtures),
                "ids": [fixture["id"] for fixture in fixtures],
            }
            if coverage_ok:
                for i, (case, fixture) in enumerate(zip(data["small_cases"], fixtures)):
                    result["results"]["small"].append(
                        process_case(
                            groups, reference, case, case.get("atoms"), i,
                            "small", fixture,
                        )
                    )
                for i, case in enumerate(data["native_cases"]):
                    result["results"]["native"].append(
                        process_case(
                            groups, reference, case, data["native_atoms"], i,
                            "native",
                        )
                    )
            else:
                groups.skip(
                    "global.case_execution", "ALL_CASE_CHECKS",
                    "Case inventory/identity coverage failed.",
                    result_path="results",
                )
    else:
        groups.skip(
            "global.case_execution", "ALL_CASE_CHECKS",
            "Saved input or frozen reference could not be loaded.",
            result_path="results",
        )

    result["checks"] = groups.records
    result["check_groups"] = groups.summary()
    result["failures"] = groups.failures
    complete_cases = (
        len(result["results"]["small"]) == EXPECTED_SMALL_CASES
        and len(result["results"]["native"]) == EXPECTED_NATIVE_CASES
    )
    if not groups.failures and complete_cases and result["check_groups"]["not_run"] == 0:
        result["status"] = "PASS_SCOPED_ENERGY_SUM"
    return result


def main(argv=None):
    unit_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "outdir", nargs="?", type=Path,
        default=unit_root / "runs" / "independent_v1",
    )
    parser.add_argument(
        "--input", type=Path,
        default=unit_root / "runs" / "primary_v2" / "PRIMARY_CERTIFICATES.json",
    )
    args = parser.parse_args(argv)
    result = run(args.input, unit_root / "reference" / "generic_dual.py")
    worker_path = Path(__file__).resolve()
    worker_bytes = worker_path.read_bytes()
    result["worker"] = {
        "path": str(worker_path), "bytes": len(worker_bytes),
        "sha256": hashlib.sha256(worker_bytes).hexdigest(),
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    result_path = args.outdir / "RESULT.json"
    # The measured runner chooses a fresh output directory.  Preserve any
    # earlier actual result instead of silently overwriting its evidence.
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(json_exact(result), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "status": result["status"],
        "result": str(result_path),
        "check_groups": result["check_groups"],
        "sourcefile_SHA256": result["sourcefile_SHA256"],
    }, ensure_ascii=False))
    return 0 if result["status"] == "PASS_SCOPED_ENERGY_SUM" else 1


if __name__ == "__main__":
    sys.exit(main())

