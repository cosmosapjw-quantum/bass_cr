"""One targeted repair of the raw comparator's near-endpoint coordinates."""
import hashlib
import json
import math
import subprocess
import sys
import time

import numpy as np
from scipy.integrate import quad

import endpoint_source as es


def raw_integral(source, energy, target):
    lower = max(es.K_MIN, (energy+source.ionization_eV(target))/source.endpoint_factor)
    if lower >= es.K_MAX:
        return 0., 0.
    width = es.K_MAX-lower

    def raw(unit):
        k = lower+width*unit
        return float(width*source.model.q_proper_m3_s_eV(k)
                     * source.rudd.proton_speed_m_s(k)*source.densities[target]
                     * source.rudd.dsigma_dW_m2_per_eV(k, energy, target))
    return quad(raw, 0., 1., epsabs=1e-80, epsrel=1e-11, limit=100)


def main():
    output = es.ROOT / "evidence" / "REPAIR_VALIDATION.json"
    if output.exists():
        raise RuntimeError("REPAIR_RESULT_ALREADY_EXISTS")
    started, cpu = time.perf_counter(), time.process_time()
    initial_path = output.parent / "VALIDATION.json"
    initial = json.loads(initial_path.read_text())
    for path, expected in initial["execution"]["source_sha256"].items():
        if hashlib.sha256((es.ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError("UNCHANGED_FIRST_RUN_SOURCE_MISMATCH:" + path)
    source = es.EndpointSource(96)
    rows, width_rows = [], []
    for row in initial["raw_SDCS_parity"]:
        target, energy = row["target"], row["W_eV"]
        actual = float(source.spectrum_by_target(energy)[target])
        raw, error = raw_integral(source, energy, target)
        rows.append({"target": target, "W_eV": energy, "candidate_A": actual,
                     "raw_SDCS_A": raw, "relative_difference": float(es.relative(actual, raw)),
                     "adaptive_absolute_error_estimate": error})
    # Independent elementary oracle explains the original false rejection.
    for target in es.TARGETS:
        energy = source.endpoint(target)*(1-1e-6)
        lower = (energy+source.ionization_eV(target))/source.endpoint_factor
        width = es.K_MAX-lower
        mapped, _ = quad(lambda u: width, 0., 1., epsabs=1e-15, epsrel=1e-12)
        unstable = es.K_MAX*(-math.expm1(math.log(lower)-math.log(es.K_MAX)))
        width_rows.append({"target": target, "K_width_eV": width,
                           "mapped_constant_integral_eV": mapped,
                           "original_log_bounds_width_eV": unstable,
                           "mapped_relative_error": float(es.relative(mapped, width)),
                           "log_bounds_relative_error": float(es.relative(unstable, width))})
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(es.ROOT/"tests"),
                            "-p", "test_reference_repair.py", "-v"], capture_output=True, text=True, timeout=30)
    checks = []
    for name, metric, limit in (
        ("RAW_SDCS_ADAPTIVE_PARITY", max(row["relative_difference"] for row in rows), 2e-10),
        ("NEAR_ENDPOINT_CONSTANT_INTEGRAND", max(row["mapped_relative_error"] for row in width_rows), 2e-15),
        ("FOCUSED_REFERENCE_REGRESSION_EXIT", tests.returncode, 0),
        ("REPAIR_WALL_BUDGET", time.perf_counter()-started, 120),
    ):
        check = {"id": name, "metric": float(metric), "limit": limit,
                 "status": "PASS" if np.isfinite(metric) and metric <= limit else "FAIL"}
        checks.append(check)
        print(json.dumps(check), flush=True)
    reused = [c for c in initial["checks"] if c["id"] != "RAW_SDCS_ADAPTIVE_PARITY"]
    status = "PASS_SCOPED_PENDING_INDEPENDENT_REVIEW" if all(c["status"] == "PASS" for c in checks+reused) else "FAIL"
    exit_code = int(not status.startswith("PASS"))
    report = {
        "id": "CR-PHYS02C-SOURCE01-REFERENCE-REPAIR01", "status": status,
        "first_failure_preserved": {"path": "evidence/VALIDATION.json", "sha256": hashlib.sha256(initial_path.read_bytes()).hexdigest()},
        "changed_component": "Independent raw-SDCS adaptive-reference coordinate only; source code unchanged",
        "checks": checks, "unchanged_acceptance_rows_reused": reused,
        "raw_SDCS_parity": rows, "constant_integrand_oracle": width_rows,
        "focused_regression": {"exit_code": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr},
        "execution": {"command": "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/cr_phys02c_source_20261010/repair.py", "exit_code": exit_code,
                      "wall_s": time.perf_counter()-started, "parent_process_cpu_s": time.process_time()-cpu,
                      "child_test_cpu_s": "NOT_MEASURED", "solver_intervals": 0,
                      "source_sha256": {path: hashlib.sha256((es.ROOT/path).read_bytes()).hexdigest() for path in
                                       ("repair.py", "REPAIR_CONTRACT.json", "tests/test_reference_repair.py")}},
        "independent_review": "NOT_RUN", "global_scientific_admission": "HOLD",
    }
    output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    (output.parent/"REPAIR_RUN.log").write_text("\n".join(json.dumps(c) for c in checks)+"\n"+json.dumps({"status": status, "exit_code": exit_code})+"\n")
    print(json.dumps({"status": status, "exit_code": exit_code}), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
