"""Single SOURCE01 qualification. Existing raw results are never overwritten."""
from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.integrate import quad

import endpoint_source as es


def main():
    output = es.ROOT / "evidence" / "VALIDATION.json"
    if output.exists():
        raise RuntimeError("FIRST_RESULT_ALREADY_EXISTS")
    started, cpu = time.perf_counter(), time.process_time()
    checks, emitted = [], []

    def check(name, metric, limit):
        row = {"id": name, "metric": float(metric), "limit": limit,
               "status": "PASS" if np.isfinite(metric) and metric <= limit else "FAIL"}
        checks.append(row)
        message = json.dumps(row)
        emitted.append(message)
        print(message, flush=True)

    test_command = [sys.executable, "-m", "unittest", "discover", "-s", str(es.ROOT / "tests"), "-v"]
    tests = subprocess.run(test_command, capture_output=True, text=True, timeout=30)
    check("FOCUSED_TEST_EXIT", tests.returncode, 0)
    source, coarse = es.EndpointSource(96), es.EndpointSource(64)
    all_points = [0., 10., 1000., 1001., 1500., 3000., 5000., 8000.]
    for target in es.TARGETS:
        lower, upper = source.endpoint(target, es.K_MIN), source.endpoint(target)
        all_points.extend([lower-1e-5, lower, lower+1e-5, upper*(1-1e-6), upper, upper+1e-5])
    points = np.unique(all_points)
    spectra = source.spectrum_by_target(points)
    coarse_spectra = coarse.spectrum_by_target(points)
    parity, parity_rows, integration_error = [], [], []
    for target in es.TARGETS:
        for energy, candidate in zip(points, spectra[target]):
            low = max(es.K_MIN, (energy+source.ionization_eV(target))/source.endpoint_factor)
            if low >= es.K_MAX:
                direct, reported = 0., 0.
            else:
                def raw(log_k):
                    k = math.exp(log_k)
                    return float(k*source.model.q_proper_m3_s_eV(k)
                                 * source.rudd.proton_speed_m_s(k)*source.densities[target]
                                 * source.rudd.dsigma_dW_m2_per_eV(k, energy, target))
                # Integration limits depend on W; this calls raw SDCS, not F1/F2 coefficients.
                direct, reported = quad(raw, math.log(low), math.log(es.K_MAX),
                                        epsabs=1e-80, epsrel=1e-11, limit=100)
            difference = float(es.relative(candidate, direct))
            parity.append(difference)
            integration_error.append(reported/max(abs(direct), 1e-300))
            parity_rows.append({"target": target, "W_eV": float(energy), "candidate_A": float(candidate),
                                "raw_SDCS_A": direct, "relative_difference": difference})
    check("RAW_SDCS_ADAPTIVE_PARITY", max(parity), 2e-10)
    spectrum_refinement = max(float(es.relative(spectra[s], coarse_spectra[s]).max()) for s in es.TARGETS)
    check("SPECTRUM_GL64_TO_96", spectrum_refinement, 2e-7)

    parts, coarse_parts = source.partitions(), coarse.partitions()
    analytic = {name: source.analytic_K_moments(lo, hi) for name, lo, hi in
                (("below_10", 0., 10.), ("10_to_1000", 10., 1000.),
                 ("above_1000", 1000., None), ("all", 0., None))}
    analytic_errors, moment_refinement = [], []
    for band in parts:
        for target in es.TARGETS:
            for field in es.FIELDS:
                candidate = parts[band]["by_target"][target][field]
                analytic_errors.append(float(es.relative(candidate, analytic[band]["by_target"][target][field])))
                moment_refinement.append(float(es.relative(candidate, coarse_parts[band]["by_target"][target][field])))
    check("W_INTEGRALS_VS_ANALYTIC_K_MOMENTS", max(analytic_errors), 2e-7)
    check("MOMENTS_GL64_TO_96", max(moment_refinement), 2e-7)
    partition_errors = []
    for target in es.TARGETS:
        for field in es.FIELDS:
            value = math.fsum(parts[band]["by_target"][target][field]
                              for band in ("below_10", "10_to_1000", "above_1000"))
            partition_errors.append(float(es.relative(value, parts["all"]["by_target"][target][field])))
    check("BELOW10_MIDDLE_ABOVE1000_PARTITIONS", max(partition_errors), 2e-12)

    dense = np.unique(np.r_[np.linspace(0., max(source.endpoint(s) for s in es.TARGETS), 257), points])
    dense_spectra = source.spectrum_by_target(dense)
    finite_nonnegative = all(np.all(np.isfinite(v)) and np.all(v >= 0) for v in dense_spectra.values())
    finite_nonnegative &= all(np.isfinite(v) and v >= 0 for band in parts.values()
                              for species in band["by_target"].values() for v in species.values())
    check("FINITE_NONNEGATIVE_SOURCE_AND_MOMENTS", int(not finite_nonnegative), 0)
    endpoint_values = [float(source.spectrum_by_target(energy)[target])
                       for target in es.TARGETS for energy in
                       (source.endpoint(target), np.nextafter(source.endpoint(target), np.inf), 1e300)]
    check("TARGET_ENDPOINT_AND_ABOVE_EXACT_ZERO", max(map(abs, endpoint_values)), 0)
    off = es.EndpointSource(96, False)
    check("OFF_AND_T0_EXACT_ZERO", max(float(np.abs(off.spectrum(dense)).max()),
                                        float(np.abs(source.rate(dense, 0.)).max())), 0)
    controls = []
    for target in es.TARGETS:
        for energy in (3000., 5000., 8000.):
            actual = float(source.spectrum_by_target(energy)[target])
            wrong = float(source.wrong_constant_coefficient_control(energy, target))
            controls.append({"target": target, "W_eV": energy, "endpoint_aware_A": actual,
                             "wrong_constant_A": wrong, "relative_disagreement": float(es.relative(actual, wrong))})
    minimum_control_difference = min(row["relative_disagreement"] for row in controls)
    check("CONSTANT_COEFFICIENT_NEGATIVE_CONTROL_DETECTED",
          int(minimum_control_difference < .001), 0)
    check("RAMP_RATE_AND_CUMULATIVE_DIMENSION", int(not np.array_equal(
        source.rate(points, es.T_END), es.T_END*source.spectrum(points))), 0)
    wall = time.perf_counter()-started
    check("CAMPAIGN_WALL_BUDGET", wall, 120)
    status = "PASS_SCOPED_PENDING_INDEPENDENT_REVIEW" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    exit_code = 0 if status.startswith("PASS") else 1
    artifact_sources = ["CONTRACT.json", "SOURCE_MANIFEST.json", "endpoint_source.py", "validate.py", "tests/test_endpoint_source.py"]
    report = {
        "id": "CR-PHYS02C-SOURCE01-FIRST-QUALIFICATION", "status": status,
        "claim_ceiling": "Endpoint-aware direct-born source only, fixed 100K bath and PR24 1-4MeV proton local ramp; no deposition/cascade/history",
        "checks": checks,
        "species_endpoints_eV": {s: {"1MeV": source.endpoint(s, es.K_MIN), "4MeV": source.endpoint(s)} for s in es.TARGETS},
        "W_panels_eV": source.energy_panels(),
        "raw_SDCS_parity": parity_rows,
        "raw_SDCS_adaptive_max_relative_error_estimate": max(integration_error),
        "source_moments_GL96": parts,
        "source_moments_GL64": coarse_parts,
        "analytic_K_moments_GL96": analytic,
        "above_1000_fraction": {f: parts["above_1000"]["total"][f]/parts["all"]["total"][f] for f in es.FIELDS},
        "cumulative_source_at_1e10s": {band: {f.removesuffix("_s2"): .5*es.T_END**2*v for f, v in values["total"].items()} for band, values in parts.items()},
        "spectrum_samples": {"W_eV": dense.tolist(), "A_by_target": {s: v.tolist() for s, v in dense_spectra.items()}},
        "negative_controls": controls,
        "execution": {"command": "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/cr_phys02c_source_20261010/validate.py", "exit_code": exit_code,
                      "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform(),
                      "wall_s": wall, "parent_process_cpu_s": time.process_time()-cpu, "child_test_cpu_s": "NOT_MEASURED", "solver_intervals": 0,
                      "source_sha256": {name: hashlib.sha256((es.ROOT/name).read_bytes()).hexdigest() for name in artifact_sources}},
        "focused_tests": {"command": test_command, "exit_code": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr},
        "independent_review": "NOT_RUN", "global_scientific_admission": "HOLD",
    }
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    emitted.append(json.dumps({"status": status, "exit_code": exit_code, "wall_s": wall}))
    (output.parent / "FIRST_RUN.log").write_text("\n".join(emitted)+"\n")
    print(emitted[-1], flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
