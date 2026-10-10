"""One bounded component campaign; preserve the first receipt and test output."""

from __future__ import annotations

import ast
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import unittest

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    # A repeat must use a separately authorized repair path, not erase evidence.
    with (evidence / "FIRST_RUN.log").open("x") as raw:
        start_wall = time.perf_counter()
        start_cpu = time.process_time()
        started = datetime.now(timezone.utc).isoformat()
        command = f"python3 -B {ROOT.relative_to(REPO)}/validate.py"
        raw.write(f"COMMAND: {command}\nSTART_UTC: {started}\n")
        raw.flush()
        report = {
            "id": "CR-PHYS02C-NIST-TABLE01-VALIDATION",
            "command": command,
            "start_utc": started,
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "cpu_affinity_count": len(os.sched_getaffinity(0))},
            "campaign": 1,
            "repair_campaigns": 0,
            "solver_intervals": 0,
            "claim": "SOURCE_BACKED_ATOMIC_COMPONENT_ONLY",
            "independent_review": "PENDING_PARENT",
            "holds": ["model-error budget", "physical interpolation-error bound", "kernel connection",
                      "old HeI 23s closure replacement", "full CR/IGM history", "global scientific admission"],
            "seed": "NOT_APPLICABLE_DETERMINISTIC_TABLE",
            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
            "git_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=REPO, text=True).strip(),
        }
        try:
            contract = json.loads((ROOT / "CONTRACT.json").read_text())
            if report["git_head"] != contract["base_commit"] or report["git_tree"] != contract["base_tree"]:
                raise ValueError("BASE_IDENTITY_CHANGED_BEFORE_RUN")
            tracked_diff = subprocess.check_output(["git", "diff", "--name-only", "HEAD"],
                                                   cwd=REPO, text=True).splitlines()
            report["tracked_diff_before"] = tracked_diff
            if tracked_diff:
                raise ValueError("PRE_EXISTING_TRACKED_FILE_CHANGED")
            executed = ("CONTRACT.json", "SOURCE_MANIFEST.json", "nist_table.py", "validate.py",
                        "tests/test_nist_table.py", "sources/table.json", "sources/j74sto.pdf")
            report["executed_input_source_sha256"] = {name: digest(ROOT / name) for name in executed}
            for relative in ("nist_table.py", "validate.py", "tests/test_nist_table.py"):
                ast.parse((ROOT / relative).read_text(), filename=relative)
            raw.write("SYNTAX: 3 files PASS\n")
            test_output = io.StringIO()
            suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
            result = unittest.TextTestRunner(stream=test_output, verbosity=2).run(suite)
            raw.write(test_output.getvalue())
            raw.flush()
            report["focused_tests"] = {"run": result.testsRun, "failures": len(result.failures),
                                       "errors": len(result.errors), "skipped": len(result.skipped),
                                       "passed": result.wasSuccessful()}
            if not result.wasSuccessful():
                raise ValueError("FOCUSED_COMPONENT_TEST_FAILURE")

            from nist_table import NistTableProvider
            provider = NistTableProvider.from_local_sources()
            report["table_entries"] = [asdict(provider.evaluate(transition.transition_id, energy))
                                       for transition in provider.transitions
                                       for energy in (1000, 1500, 2000, 3000)]
            report["midpoint_entries"] = [asdict(provider.evaluate(transition.transition_id, energy))
                                          for transition in provider.transitions
                                          for energy in (1250, 1750, 2500)]
            tracked_after = subprocess.check_output(["git", "diff", "--name-only", "HEAD"],
                                                    cwd=REPO, text=True).splitlines()
            report["tracked_diff_after"] = tracked_after
            if tracked_after:
                raise ValueError("PRE_EXISTING_TRACKED_FILE_CHANGED")
            report["checks"] = {
                "syntax": "PASS", "local_pdf_and_table_identity": "PASS",
                "eight_source_table_entries": "PASS", "six_linear_midpoints": "PASS",
                "units_and_explicit_transition_energies": "PASS", "domain_and_finite_guards": "PASS",
                "nonnegative_convex_interpolation": "PASS", "existing_tracked_files_unchanged": "PASS",
                "physical_model_error": "HOLD_NOT_MEASURED", "kernel_connection": "HOLD_NOT_EXECUTED",
                "convergence_to_true_cross_section": "NOT_TESTED_NOT_CLAIMED",
            }
            report["status"] = "PASS_SCOPED"
        except Exception:
            report["status"] = "FAIL"
            report["first_failure"] = traceback.format_exc()
            raw.write(report["first_failure"])

        report["process_cpu_s"] = time.process_time() - start_cpu
        report["process_wall_s"] = time.perf_counter() - start_wall
        report["overhead"] = "UNKNOWN_NOT_ZERO; git subprocess CPU and source acquisition not included"
        if report["process_wall_s"] > 30:
            report["status"] = "FAIL"
            report["wall_limit_failure"] = "MAXIMUM_WALL_30S_EXCEEDED"
        report["exit_code"] = 0 if report["status"] == "PASS_SCOPED" else 1
        raw.write(f"STATUS: {report['status']}\nEXIT_CODE: {report['exit_code']}\n")
        raw.flush()
    with (evidence / "VALIDATION.json").open("x") as output:
        json.dump(report, output, indent=2, allow_nan=False)
        output.write("\n")
    print(json.dumps({key: report[key] for key in
                      ("status", "exit_code", "process_cpu_s", "process_wall_s", "solver_intervals")}))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
