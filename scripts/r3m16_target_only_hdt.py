"""R3M16 target-only point-Coulomb/FFT h-dt diagnostics.

This additive sidecar never calls the two-center potential or applies a CAP.
It consumes immutable R3M15 preparation bytes and reports diagnostics, not a
capture-probability error bound or a cross-grid state theorem.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path

import numpy as np

from cr_repro.backend import asnumpy
from cr_repro.r3m11 import ControlledTDLRunner, source_digest

SOURCE = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/r3m13_initial_state_pair.py"
NUMERIC_FLOOR = 1e-13


def sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _load_helper():
    spec = importlib.util.spec_from_file_location("_r3m16_r3m13", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime_environment(backend: str) -> dict:
    result = {"python": platform.python_version(), "numpy": np.__version__, "backend": backend}
    try:
        import cupy as cp
        result.update(cupy=cp.__version__, cuda_runtime=int(cp.cuda.runtime.runtimeGetVersion()),
                      cuda_driver=int(cp.cuda.runtime.driverGetVersion()))
        if backend == "cupy":
            device = cp.cuda.Device()
            props = cp.cuda.runtime.getDeviceProperties(device.id)
            name = props["name"]
            result.update(cuda_device_id=int(device.id),
                          cuda_device_name=name.decode() if isinstance(name, bytes) else str(name))
    except Exception:
        pass
    return result


def fixed_horizon_steps(horizon: float, requested_dt: float) -> tuple[int, float]:
    if not math.isfinite(horizon) or not math.isfinite(requested_dt) or horizon <= 0 or requested_dt <= 0:
        raise ValueError("positive finite horizon and dt required")
    nstep = math.ceil(horizon / requested_dt)
    return nstep, horizon / nstep


def step_identity(requested_dt: float, actual_dt: float, nstep: int, horizon: float) -> dict:
    if not math.isclose(nstep * actual_dt, horizon, rel_tol=0.0, abs_tol=2e-15):
        raise ValueError("actual dt does not close the fixed horizon")
    return {"requested_dt": float(requested_dt), "actual_dt": float(actual_dt),
            "nstep": int(nstep), "physical_end_time": float(horizon)}

def _phase_metrics(a, b, dv: float, xp=np) -> dict:
    na = float(asnumpy(xp.sum(xp.abs(a) ** 2) * dv))
    nb = float(asnumpy(xp.sum(xp.abs(b) ** 2) * dv))
    if min(na, nb) <= 0 or not all(math.isfinite(x) for x in (na, nb)):
        raise ValueError("finite nonzero states required")
    overlap = complex(asnumpy(xp.sum(xp.conj(a) * b) * dv))
    fidelity = abs(overlap) ** 2 / (na * nb)
    fidelity = min(1.0, max(0.0, fidelity))
    distance = math.sqrt(max(0.0, 2.0 - 2.0 * math.sqrt(fidelity)))
    return {"ray_distance": distance, "overlap_abs": abs(overlap),
            "fidelity": fidelity, "norm_first": na, "norm_second": nb}


def ray_distance(a, b, dv: float) -> float:
    return _phase_metrics(np.asarray(a), np.asarray(b), dv)["ray_distance"]


def bind_same_grid_states(first: Path, second: Path, first_grid: dict, second_grid: dict) -> dict:
    if first_grid != second_grid:
        raise ValueError("cross-grid state-pair theorem is forbidden")
    first, second = Path(first), Path(second)
    if sha(first) != sha(second) or first.read_bytes() != second.read_bytes():
        raise ValueError("saved state bytes differ within one h-grid")
    return {"byte_identical": True, "state_sha256": sha(first), "grid": first_grid}


def target_only_step(runner: ControlledTDLRunner, psi, dt: float):
    """Symmetric exp(V/2) exp(T) exp(V/2), with target V only and no CAP."""
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("positive finite dt required")
    xp = runner.xp
    potential_half = xp.exp(-0.5j * dt * runner.Vtarget)
    kinetic = xp.exp(-0.5j * dt * runner.k2)
    psi = potential_half * psi
    psi = xp.fft.ifftn(kinetic * xp.fft.fftn(psi))
    return potential_half * psi


def stationary_residual(runner: ControlledTDLRunner, psi) -> tuple[float, float]:
    xp = runner.xp
    hpsi = xp.fft.ifftn(0.5 * runner.k2 * xp.fft.fftn(psi)) + runner.Vtarget * psi
    energy = float(asnumpy(xp.real(xp.sum(xp.conj(psi) * hpsi) * runner.dv)))
    residual = float(asnumpy(xp.sqrt(xp.sum(xp.abs(hpsi - energy * psi) ** 2) * runner.dv)))
    return energy, residual


def empirical_order(d01: float, d12: float) -> dict:
    if not all(math.isfinite(x) and x >= 0 for x in (d01, d12)):
        return {"status": "INVALID", "order": None}
    if min(d01, d12) <= NUMERIC_FLOOR:
        return {"status": "UNRESOLVED", "order": None}
    if d12 >= d01:
        return {"status": "NONMONOTONE", "order": None}
    return {"status": "EMPIRICAL_ORDER", "order": math.log(d01 / d12) / math.log(2.0)}


def _fit_one_step(rows: list[dict]) -> dict:
    dt = np.asarray([row["actual_dt"] for row in rows], float)
    values = np.asarray([row["ray_distance"] for row in rows], float)
    matrix = np.column_stack([dt, dt ** 3])
    coef, _, rank, singular = np.linalg.lstsq(matrix, values, rcond=None)
    fitted = matrix @ coef
    return {"model": "d1(dt)=a_h*dt+b_h*dt^3", "a_h": float(coef[0]),
            "b_h": float(coef[1]), "rank": int(rank),
            "singular_values": singular.tolist(),
            "residual_l2": float(np.linalg.norm(values - fitted)),
            "positive_coefficients_forced": False, "certified_error_law": False}


def _load_prepared(prepared: Path, config: dict):
    helper = _load_helper()
    if source_digest() != SOURCE or getattr(helper, "EXPECTED_SOURCE_DIGEST", None) != SOURCE:
        raise ValueError("frozen numerical source mismatch")
    host, receipt = helper.load_prepared(prepared)
    if receipt["config"] != config:
        raise ValueError("preparation config identity mismatch")
    path = Path(prepared) / "initial.npy"
    return path, host, receipt


def run_diagnostics(config_path: Path, prepared: Path, collision_result: Path,
                    output: Path, horizon: float = 1.0, one_step_only: bool = False) -> dict:
    config = json.loads(Path(config_path).read_text())
    state_path, host, receipt = _load_prepared(Path(prepared), config)
    collision = json.loads(Path(collision_result).read_text())
    if collision["config"] != config or collision["status"] != "completed":
        raise ValueError("collision result is not the exact preparation config authority")
    dt0 = float(collision["dt_actual"])
    runner = ControlledTDLRunner(config)
    if list(host.shape) != list(runner.spec.shape()):
        raise ValueError("state/grid shape mismatch")
    psi0 = runner.xp.asarray(host)
    energy0, residual = stationary_residual(runner, psi0)
    norm0 = runner.norm(psi0)
    nominal = float(config["dt"])
    one_step = []
    for level in range(3):
        actual = dt0 / (2 ** level)
        requested = nominal / (2 ** level)
        final = target_only_step(runner, psi0, actual)
        phase = _phase_metrics(psi0, final, runner.dv, runner.xp)
        energy = runner.target_energy(final)
        one_step.append({"level": level, "requested_dt": requested, "actual_dt": actual,
                         **phase, "energy_before_Eh": energy0, "energy_after_Eh": energy,
                         "energy_drift_Eh": energy - energy0,
                         "norm_drift": runner.norm(final) - norm0})
    fixed_horizon = None
    if not one_step_only:
        horizon_rows, finals = [], []
        for requested in (0.05, 0.025, 0.0125):
            nstep, actual = fixed_horizon_steps(horizon, requested)
            state = psi0.copy()
            for _ in range(nstep):
                state = target_only_step(runner, state, actual)
            phase = _phase_metrics(psi0, state, runner.dv, runner.xp)
            energy = runner.target_energy(state)
            horizon_rows.append({**step_identity(requested, actual, nstep, horizon), **phase,
                                 "energy_before_Eh": energy0, "energy_after_Eh": energy,
                                 "energy_drift_Eh": energy - energy0,
                                 "norm_drift": runner.norm(state) - norm0})
            finals.append(state)
        d01 = _phase_metrics(finals[0], finals[1], runner.dv, runner.xp)["ray_distance"]
        d12 = _phase_metrics(finals[1], finals[2], runner.dv, runner.xp)["ray_distance"]
        order = empirical_order(d01, d12)
        clean = order["status"] == "EMPIRICAL_ORDER" and 1.5 <= order["order"] <= 2.5
        fixed_horizon = {"T_probe": horizon, "runs": horizon_rows, "D01": d01, "D12": d12,
                         "empirical_order": order, "clean_second_order_diagnostic": clean,
                         "clean_rule": "D01>D12>1e-13 and 1.5<=p_time<=2.5; diagnostic only"}
    result = {
        "schema": "BASS_CR_R3M16_TARGET_ONLY_HDT_V1", "status": "COMPLETE",
        "claim_scope": "TARGET_ONLY_DIAGNOSTIC_NOT_CAPTURE_PROBABILITY_ERROR",
        "projectile_potential_included": False, "CAP_included": False,
        "cross_grid_state_pair_theorem_used": False,
        "config_sha256": sha(Path(config_path)), "prepared_receipt_sha256": sha(Path(prepared) / "receipt.json"),
        "state_sha256": sha(state_path), "collision_result_sha256": sha(Path(collision_result)),
        "numerical_source_digest": source_digest(), "instrumentation_sha256": sha(Path(__file__)),
        "runtime_environment": runtime_environment(runner.backend), "grid": config["grid"],
        "initial": {"norm": norm0, "target_energy_Eh": energy0,
                    "stationary_residual_Eh": residual,
                    "receipt_stationary_residual_Eh": receipt["initial"]["stationary_residual_Eh"]},
        "one_step": one_step, "one_step_fit": _fit_one_step(one_step),
        "fixed_horizon": fixed_horizon,
    }
    write_new(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared", required=True, type=Path)
    parser.add_argument("--collision-result", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--horizon", type=float, default=1.0)
    parser.add_argument("--one-step-only", action="store_true")
    args = parser.parse_args()
    try:
        result = run_diagnostics(args.config, args.prepared, args.collision_result, args.out,
                                 args.horizon, args.one_step_only)
    except BaseException as exc:
        failure = args.out.with_name(args.out.stem + ".failure.json")
        if not failure.exists():
            write_new(failure, {"status": "FAILED_OR_INTERRUPTED", "type": type(exc).__name__,
                                "message": str(exc), "partial_overwritten": False})
        raise
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
