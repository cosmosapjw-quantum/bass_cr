"""One bounded incoming-B2 CF4 outer-reference job; never a full collision.

All endpoint distances are raw and use the frozen production grid/H/CAP. The
Arnoldi indicator is empirical; an outer reference is admitted only by the
registered independent outer, tolerance, and action-substep repeats.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m19_performance import hardware_inventory
from scripts.r3m20_matrix_free import FROZEN_SOURCE, MatrixFreeFullH
from scripts.r3m20_short_window import preflight as allocation_preflight

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/R3M21"
SELECTION = ROOT / "results/R3M20_N1/windows/SELECTION.json"
PRIOR = ROOT / "results/R3M20_N1/windows/FIRST_WINDOW.json"
CONFIG = ROOT / "configs/r3m17/B2.json"
MAX_MATVECS = 4000
MAX_GPU_SECONDS = 7200
MAX_WINDOW_SECONDS = 1800
GPU_RESERVE = 2 * 1024**3
HOST_RESERVE = 8 * 1024**3
MAX_BASIS = 10
LADDER = (("CF4_4_sub8", 4, 8, 1e-12),
          ("CF4_8_sub8", 8, 8, 1e-12),
          ("CF4_8_sub4", 8, 4, 1e-12),
          ("CF4_16_sub4", 16, 4, 1e-12),
          ("CF4_32_sub4", 32, 4, 1e-12),
          ("CF4_16_sub4_tight", 16, 4, 1e-13))


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024**2), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def input_guard():
    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source changed")
    selection = json.loads(SELECTION.read_text())
    prior = json.loads(PRIOR.read_text())
    row = selection["windows"][0]
    state_path = Path(row["generation_directory"]) / "state.npy"
    if (row["label"] != "incoming" or row["done"] != 384
            or selection["actual_dt_au"] != prior["actual_dt_au"]
            or row["expected_state_npy_sha256"] != prior["checkpoint_sha256"]
            or _sha(CONFIG) != selection["B2_config_sha256"]
            or _sha(state_path) != row["expected_state_npy_sha256"]
            or prior["reference_semantics"] != "CF4_DT2_CONDITIONAL_NO_INDEPENDENT_PRODUCTION_ODE_OR_DT4"):
        raise ValueError("incoming checkpoint or predecessor evidence mismatch")
    return dict(schema="BASS_CR_R3M21_INPUT_GUARD_V1", status="PASS",
                source_digest=FROZEN_SOURCE, selection_sha256=_sha(SELECTION),
                prior_window_sha256=_sha(PRIOR), config_sha256=_sha(CONFIG),
                state_npy_sha256=row["expected_state_npy_sha256"],
                state_npy_bytes=state_path.stat().st_size,
                prior_cf4_8_endpoint_sha256=prior["method_endpoints"]["CF4_8"]["sha256"],
                prior_cf4_4_to_8_distance=prior["cf4_outer_dt_to_dt2_raw_distance"],
                remote_restore="NOT_TESTED"), selection, prior


class Budget:
    def __init__(self, started, initial_count):
        self.started = started
        self.window_started = time.perf_counter()
        self.count = initial_count

    def tick(self):
        now = time.perf_counter()
        if (self.count >= MAX_MATVECS or now - self.started >= MAX_GPU_SECONDS
                or now - self.window_started >= MAX_WINDOW_SECONDS):
            raise TimeoutError("R3M21 GPU/FFT/window ceiling reached before next matvec")
        self.count += 1


def raw_distance(a, b, dv):
    return float(np.linalg.norm((a - b).ravel()) * math.sqrt(dv))


def reference_gate(distances, prior_distance):
    """One-percent gate against the already observed CF4 4→8 signal."""
    if not math.isfinite(prior_distance) or prior_distance <= 0:
        raise ValueError("positive predecessor signal required")
    if any(not math.isfinite(x) or x < 0 for x in distances.values()):
        raise ValueError("finite nonnegative repeat distances required")
    required = ("outer_16_to_32", "inner_16_repeat", "substep_8_repeat")
    if any(key not in distances for key in required):
        return "REFERENCE_UNRESOLVED_INCOMPLETE_REPEATS"
    return ("REFERENCE_RESOLVED_FOR_PRIOR_CF4_4_ERROR_SCALE"
            if all(distances[key] < .01 * prior_distance for key in required)
            else "REFERENCE_UNRESOLVED_ONE_PERCENT_GATE")


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    stage = "INPUT_GUARD"
    budget = None
    try:
        guard, selection, prior = input_guard()
        _write_new(OUT / "INPUT_GUARD.json", guard)
        stage = "RESOURCE_PREFLIGHT"
        probe = allocation_preflight()
        inventory = probe["actual_inventory"]
        if (probe["status"] != "PASS" or probe["gpu_free_after_matvec_probe"] < GPU_RESERVE
                or inventory["memory"]["available_bytes"] < HOST_RESERVE):
            raise MemoryError("production allocation/matvec probe failed")
        # Previous measured 8-step 8-substep CF4 cost is 131.8 s. Extrapolation
        # is a planning estimate only; each matvec has an independent live cap.
        predecessor_seconds = prior["method_endpoints"]["CF4_8"]["propagation_seconds"]
        estimate = predecessor_seconds * (1 + .65 + .75 + 1.25 + 2.5 + 1.25)
        probe.update(schema="BASS_CR_R3M21_GPU_PREFLIGHT_V1",
                     predecessor_cf4_8_measured_seconds=predecessor_seconds,
                     ladder_forecast_seconds=estimate,
                     forecast_is_measurement=False,
                     ladder=[list(x) for x in LADDER],
                     source_sha256=_sha(Path(__file__)),
                     input_guard_sha256=_sha(OUT / "INPUT_GUARD.json"))
        if estimate > .8 * MAX_WINDOW_SECONDS:
            probe["status"] = "COST_BLOCKED"
        _write_new(OUT / "PREFLIGHT.json", probe)
        if probe["status"] != "PASS":
            raise RuntimeError("preflight cost/resource gate failed")

        stage = "CF4_LADDER"
        import cupy as cp
        row = selection["windows"][0]
        state_map = np.load(Path(row["generation_directory"]) / "state.npy",
                            mmap_mode="r", allow_pickle=False)
        runner = ControlledTDLRunner(json.loads(CONFIG.read_text()))
        state = cp.asarray(state_map)
        mf = MatrixFreeFullH(runner)
        del runner.kin, runner.mask, runner.cap_half
        cp.get_default_memory_pool().free_all_blocks()
        if (cp.cuda.runtime.memGetInfo()[0] < GPU_RESERVE
                or hardware_inventory(include_gpu=False)["memory"]["available_bytes"] < HOST_RESERVE):
            raise MemoryError("live reserve lost after state upload")
        budget = Budget(started, probe["preflight_fft_matvecs"])
        mf.matvec_monitor = budget.tick
        t0 = row["actual_start_time_au"]
        horizon = row["horizon_au"]
        endpoints = {}
        records = {}
        min_free = int(cp.cuda.runtime.memGetInfo()[0])
        for label, n, substeps, tol in LADDER:
            step = horizon / n
            current = state.copy()
            infos = []
            mark = time.perf_counter()
            for j in range(n):
                current, info = mf.step(current, t0 + j * step, step, method="cf4",
                                        tol=tol, max_basis=MAX_BASIS,
                                        max_basis_bytes=(MAX_BASIS + 1) * int(state.nbytes),
                                        action_substeps=substeps)
                infos.append(info)
            cp.cuda.get_current_stream().synchronize()
            wall = time.perf_counter() - mark
            min_free = min(min_free, int(cp.cuda.runtime.memGetInfo()[0]))
            if min_free < GPU_RESERVE:
                raise MemoryError("GPU reserve lost after CF4 endpoint")
            transfer_start = time.perf_counter()
            host = cp.asnumpy(current)
            transfer_seconds = time.perf_counter() - transfer_start
            if not np.isfinite(host).all():
                raise FloatingPointError("nonfinite CF4 endpoint")
            endpoints[label] = host
            records[label] = dict(steps=n, action_substeps=substeps, inner_tolerance=tol,
                                  propagation_seconds=wall, host_transfer_seconds=transfer_seconds,
                                  fft_matvecs=sum(x["total_fft_matvec"] for x in infos),
                                  max_basis_used=max(a["basis_dimension"] for x in infos for a in x["actions"]),
                                  max_inner_residual_indicator=max(a["residual_indicator"] for x in infos for a in x["actions"]),
                                  norm=float(np.vdot(host, host).real * runner.dv),
                                  sha256=hashlib.sha256(host.tobytes()).hexdigest())
            del current
        stage = "HOST_REFERENCE_GATE"
        d = {
            "outer_4_to_32": raw_distance(endpoints["CF4_4_sub8"], endpoints["CF4_32_sub4"], runner.dv),
            "outer_4_to_8_repeat": raw_distance(endpoints["CF4_4_sub8"], endpoints["CF4_8_sub8"], runner.dv),
            "outer_8_to_16": raw_distance(endpoints["CF4_8_sub4"], endpoints["CF4_16_sub4"], runner.dv),
            "outer_16_to_32": raw_distance(endpoints["CF4_16_sub4"], endpoints["CF4_32_sub4"], runner.dv),
            "inner_16_repeat": raw_distance(endpoints["CF4_16_sub4"], endpoints["CF4_16_sub4_tight"], runner.dv),
            "substep_8_repeat": raw_distance(endpoints["CF4_8_sub8"], endpoints["CF4_8_sub4"], runner.dv),
        }
        gate = reference_gate(d, d["outer_4_to_32"])
        result = dict(schema="BASS_CR_R3M21_CF4_OUTER_LADDER_V1", status=gate,
                      reference_scope="INCOMING_4_B2_DT_SAME_DISCRETE_H_AND_CAP",
                      input_guard_sha256=_sha(OUT / "INPUT_GUARD.json"),
                      preflight_sha256=_sha(OUT / "PREFLIGHT.json"),
                      checkpoint_done=384, horizon_au=horizon, initial_time_au=t0,
                      prior_cf4_4_to_8_distance=guard["prior_cf4_4_to_8_distance"],
                      prior_cf4_4_hash_equal=records["CF4_4_sub8"]["sha256"] == prior["method_endpoints"]["CF4_4"]["sha256"],
                      prior_cf4_8_hash_equal=records["CF4_8_sub8"]["sha256"] == guard["prior_cf4_8_endpoint_sha256"],
                      distances=d, gate_fraction=.01, endpoints=records,
                      gpu_fft_matvec_total_including_preflight=budget.count,
                      gpu_wall_seconds=time.perf_counter()-started,
                      window_wall_seconds=time.perf_counter()-budget.window_started,
                      minimum_gpu_free_bytes=min_free,
                      remote_restore="NOT_TESTED", full_collision=False,
                      preparation_run=False, projection="NOT_RUN",
                      production_admission=False,
                      interpretation="empirical production-grid discrete-H reference at prior CF4_4 error scale only; no global collision/observable certificate")
        _write_new(OUT / "CF4_OUTER_LADDER.json", result)
        return result
    except BaseException as exc:
        _write_new(OUT / "FIRST_FAILURE.json",
                   dict(schema="BASS_CR_R3M21_FIRST_FAILURE_V1", stage=stage,
                        type=type(exc).__name__, message=str(exc),
                        elapsed_seconds=time.perf_counter()-started,
                        fft_matvec_count=None if budget is None else budget.count,
                        automatic_retry=False, full_collision=False,
                        original_checkpoint_modified=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", choices=("run",))
    args = parser.parse_args()
    result = run()
    print(json.dumps({"status": result["status"],
                      "matvecs": result["gpu_fft_matvec_total_including_preflight"],
                      "wall_seconds": result["gpu_wall_seconds"]}))


if __name__ == "__main__":
    main()
