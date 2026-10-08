"""Bounded AOCC moving-basis diagnostics, without propagating a trajectory.

The independently differentiated overlap/Cholesky factor is essential: the
existing generator constructs its Hermitian connection from D+D† and hence
cannot, by anti-Hermiticity alone, test the derivative of the actual metric.
This sidecar changes neither the scientific matrices nor their propagator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import solve_triangular

from cr_repro.aocc import OneElectronAOCC
from cr_repro.r3m11 import source_digest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
METRIC_HERMITICITY_RTOL = 1e-11
MAX_PRIMITIVES_PER_CENTER = 32
MAX_TIME_SAMPLES = 9
MAX_EPSILON_SAMPLES = 8


def file_sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path: Path, value) -> None:
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _bounded_preflight(cfg, times, epsilons, atol, rtol):
    """Reject expensive/invalid input before constructing any AOCC matrices."""
    if not isinstance(cfg, dict):
        raise ValueError("AOCC config must be a JSON object")
    counts = {}
    for name, default, minimum in (("ns", 10, 1), ("np", 6, 0)):
        value = cfg.get(name, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be an integer")
        if not math.isfinite(value) or value != int(value) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
        counts[name] = int(value)
    primitive_count = counts["ns"] + 3 * counts["np"]
    if primitive_count > MAX_PRIMITIVES_PER_CENTER:
        raise ValueError(f"bounded primitive budget exceeded: {primitive_count} > {MAX_PRIMITIVES_PER_CENTER}")
    if not isinstance(epsilons, (list, tuple)) or not 2 <= len(epsilons) <= MAX_EPSILON_SAMPLES:
        raise ValueError(f"bounded epsilon sample count must be 2..{MAX_EPSILON_SAMPLES}")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0
           for x in epsilons):
        raise ValueError("positive finite derivative steps required")
    if any(a <= b for a, b in zip(epsilons, epsilons[1:])):
        raise ValueError("derivative ladder must strictly decrease")
    if times is not None:
        if not isinstance(times, (list, tuple)) or not 1 <= len(times) <= MAX_TIME_SAMPLES:
            raise ValueError(f"bounded time sample count must be 1..{MAX_TIME_SAMPLES}")
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
               for x in times):
            raise ValueError("finite physical time samples required")
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool)
               and math.isfinite(x) and x >= 0 for x in (atol, rtol)):
        raise ValueError("nonnegative finite diagnostic tolerances required")
    return {"primitive_count_per_center": primitive_count,
            "dense_matrix_dimension_upper_bound": 2 * primitive_count,
            "max_primitives_per_center": MAX_PRIMITIVES_PER_CENTER,
            "max_time_samples": MAX_TIME_SAMPLES, "max_epsilon_samples": MAX_EPSILON_SAMPLES}


def _matrix(value, name, shape=None):
    value = np.asarray(value, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or value.shape[0] == 0:
        raise ValueError(f"{name} must be a nonempty square matrix")
    if shape is not None and value.shape != shape:
        raise ValueError(f"{name} shape mismatch")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} contains nonfinite values")
    return value


def _factor_metric(metric):
    metric = _matrix(metric, "O")
    scale = float(np.linalg.norm(metric))
    defect = float(np.linalg.norm(metric - metric.conj().T))
    if defect > METRIC_HERMITICITY_RTOL * scale:
        raise ValueError("metric is not Hermitian; symmetrization is forbidden")
    # Cholesky fails for non-positive metrics; no eigenvalue floor or repair.
    factor = np.linalg.cholesky(metric).conj().T
    eigenvalues = np.linalg.eigvalsh(metric)
    return factor, {
        "hermiticity_absolute": defect,
        "eigenvalue_min": float(eigenvalues[0]),
        "eigenvalue_max": float(eigenvalues[-1]),
        "condition_2": float(eigenvalues[-1] / eigenvalues[0]),
    }


def _residual(error, scale, atol, rtol):
    absolute = float(np.linalg.norm(error))
    scale = float(scale)
    threshold = float(atol + rtol * scale)
    return {
        "absolute": absolute, "scale": scale,
        "relative": absolute / scale if scale > 0 else None,
        "threshold": threshold, "passes": absolute <= threshold,
    }


def matrix_diagnostic(metric, hamiltonian, connection, metric_minus, metric_plus,
                      epsilon, *, atol=1e-9, rtol=1e-6):
    """Evaluate both the independent and the algebraically constructed tests.

    O=Phi†Phi, D=Phi†dot(Phi), O=R†R, y=RC, atomic units.
    G_fd=dot(R)_fd R^-1-R^-† D R^-1-i R^-† H R^-1.
    No Hermitian/anti-Hermitian projection is applied to G_fd.
    """
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive and finite")
    if not all(math.isfinite(x) and x >= 0 for x in (atol, rtol)):
        raise ValueError("nonnegative finite diagnostic tolerances required")
    metric = _matrix(metric, "O")
    hamiltonian = _matrix(hamiltonian, "H", metric.shape)
    connection = _matrix(connection, "D", metric.shape)
    metric_minus = _matrix(metric_minus, "O_minus", metric.shape)
    metric_plus = _matrix(metric_plus, "O_plus", metric.shape)
    factor, diagnostics = _factor_metric(metric)
    factor_minus, _ = _factor_metric(metric_minus)
    factor_plus, _ = _factor_metric(metric_plus)
    inverse = solve_triangular(factor, np.eye(len(metric)), lower=False)
    metric_derivative = (metric_plus - metric_minus) / (2 * epsilon)
    connection_sum = connection + connection.conj().T
    factor_derivative = (factor_plus - factor_minus) / (2 * epsilon)
    transformed_d = inverse.conj().T @ connection @ inverse
    transformed_h = inverse.conj().T @ hamiltonian @ inverse
    independent_generator = factor_derivative @ inverse - transformed_d - 1j * transformed_h

    # This duplicates the existing algebra solely to exhibit its blind spot.
    w = transformed_d + transformed_d.conj().T
    constructed_x = np.triu(w, 1) + np.diag(np.real(np.diag(w)) / 2)
    constructed_generator = constructed_x - transformed_d - 1j * transformed_h
    return {
        "epsilon_t_a": float(epsilon),
        "metric": diagnostics,
        "hamiltonian_hermiticity": _residual(
            hamiltonian - hamiltonian.conj().T, np.linalg.norm(hamiltonian), atol, rtol),
        "metric_identity": _residual(
            metric_derivative - connection_sum,
            max(np.linalg.norm(metric_derivative), np.linalg.norm(connection_sum)), atol, rtol),
        "independent_raw_generator": _residual(
            independent_generator + independent_generator.conj().T,
            np.linalg.norm(independent_generator), atol, rtol),
        "constructed_generator": _residual(
            constructed_generator + constructed_generator.conj().T,
            np.linalg.norm(constructed_generator), atol, rtol),
        "constructed_generator_is_independent_metric_test": False,
        "generator_symmetrization_applied": False,
    }


def audit_time(matrix_fn, time, epsilons, *, atol=1e-9, rtol=1e-6):
    epsilons = [float(value) for value in epsilons]
    if len(epsilons) < 2 or any(not math.isfinite(x) or x <= 0 for x in epsilons):
        raise ValueError("at least two positive finite derivative steps required")
    if any(a <= b for a, b in zip(epsilons, epsilons[1:])):
        raise ValueError("derivative ladder must strictly decrease")
    if not math.isfinite(time):
        raise ValueError("finite physical time required")
    metric, hamiltonian, connection = matrix_fn(time)
    rows = []
    for epsilon in epsilons:
        minus = matrix_fn(time - epsilon)[0]
        plus = matrix_fn(time + epsilon)[0]
        rows.append(matrix_diagnostic(
            metric, hamiltonian, connection, minus, plus, epsilon, atol=atol, rtol=rtol))
    passed = all(
        row[name]["passes"] for row in rows[-2:]
        for name in ("hamiltonian_hermiticity", "metric_identity", "independent_raw_generator")
    )
    errors = [row["metric_identity"]["absolute"] for row in rows]
    return {
        "time_t_a": float(time), "rows": rows,
        "finest_two_steps_required": True,
        "metric_errors_strictly_decrease": all(a > b for a, b in zip(errors, errors[1:])),
        "status": "PASS_LOCAL_METRIC_IDENTITY_ONLY" if passed else "METRIC_IDENTITY_UNRESOLVED_OR_FAILED",
    }


def run_audit(config_path, output, *, epsilons=(0.004, 0.002, 0.001, 0.0005),
              times=None, atol=1e-9, rtol=1e-6, expected_source=SOURCE):
    """Create-only matrix evaluations; all partial/failing output is retained."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    provenance = {"started_utc": started, "scientific_trajectory_count": 0}
    try:
        actual_source = source_digest()
        provenance.update(numerical_source_digest=actual_source,
                          expected_numerical_source_digest=expected_source)
        if actual_source != expected_source:
            raise ValueError("frozen numerical source digest mismatch")
        config_path = Path(config_path).resolve()
        cfg = json.loads(config_path.read_text())
        bounds = _bounded_preflight(cfg, times, epsilons, atol, rtol)
        provenance.update(
            config_path=str(config_path), config_file_sha256=file_sha(config_path),
            config=cfg,
            instrumentation_sha256=file_sha(Path(__file__)),
            aocc_source_sha256=file_sha(ROOT / "cr_repro/aocc.py"),
            analytic_primitive_sha256=file_sha(ROOT / "vendor_w1r/gaussian_cartesian.py"),
            repository_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            runtime={"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "backend": "CPU_NUMPY_SCIPY", "platform": platform.platform()},
            diagnostic_tolerances={"absolute": atol, "relative": rtol,
                                   "physical_error_budget": False},
            resource_preflight=bounds,
        )
        write_new(output / "provenance.json", provenance)
        model = OneElectronAOCC(cfg)
        evaluation_times = [model.t0, 0.0, model.tf] if times is None else list(times)
        if not evaluation_times:
            raise ValueError("at least one evaluation time required")
        rows = []
        for index, time in enumerate(evaluation_times):
            row = audit_time(model.matrix, time, epsilons, atol=atol, rtol=rtol)
            write_new(output / f"time_{index:03d}.json", row)
            rows.append(row)
        passed = all(row["status"] == "PASS_LOCAL_METRIC_IDENTITY_ONLY" for row in rows)
        result = {
            "schema": "R3M17_AOCC_METRIC_DIAGNOSTIC_V1",
            "status": "PASS_LOCAL_METRIC_IDENTITY_ONLY" if passed else "METRIC_IDENTITY_UNRESOLVED_OR_FAILED",
            "rows": rows, "provenance": provenance,
            "basis": {"nbasis": model.nb, "angular_scope": "s+p_only",
                      "retained_atomic_energies_Eh": model.epsk.tolist(),
                      "center_and_atomic_index": [[center, int(index)] for center, index in model.basis]},
            "claim_ceiling": {
                "metric_identity_at_sampled_times_only": True,
                "full_trajectory_run": False, "basis_convergence_established": False,
                "d_channels_validated": False, "capture_observables_validated": False,
                "production_admission": "HOLD",
            },
        }
        write_new(output / "result.json", result)
        manifest = {
            "files": [{"path": path.name, "size_bytes": path.stat().st_size,
                       "sha256": file_sha(path)} for path in sorted(output.glob("*.json"))],
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        }
        write_new(output / "manifest.json", manifest)
        return result
    except Exception as error:
        # Evidence is saved and the original error is re-raised; no fallback.
        write_new(output / "failure.json", {
            "status": "FAILED_RETAINED", "provenance": provenance,
            "exception_type": type(error).__name__, "message": str(error),
            "traceback": traceback.format_exc(),
        })
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--epsilons", nargs="+", type=float, default=[0.004, 0.002, 0.001, 0.0005])
    parser.add_argument("--times", nargs="+", type=float)
    parser.add_argument("--atol", type=float, default=1e-9)
    parser.add_argument("--rtol", type=float, default=1e-6)
    args = parser.parse_args()
    result = run_audit(args.config, args.out, epsilons=args.epsilons,
                       times=args.times, atol=args.atol, rtol=args.rtol)
    print(json.dumps({"status": result["status"], "sampled_times": len(result["rows"]),
                      "nbasis": result["basis"]["nbasis"], "scientific_trajectory_count": 0}))
    return 0 if result["status"] == "PASS_LOCAL_METRIC_IDENTITY_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
