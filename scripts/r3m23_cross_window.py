"""One bounded GPU job comparing the two selected immutable B2 short windows.

This sidecar never advances or writes a production checkpoint or runs a collision.
Every reference claim is local to one identical-start, four-B2-dt restart.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m19_performance import accuracy_metrics, hardware_inventory
from scripts.r3m20_matrix_free import FROZEN_SOURCE
from scripts.r3m20_short_window import ProductionBufferedStep, preflight as allocation_preflight
from scripts.r3m22_inner_action import BoundedMatrixFreeFullH


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/R3M23"
SELECTION = ROOT / "results/R3M20_N1/windows/SELECTION.json"
CONFIG = ROOT / "configs/r3m17/B2.json"
STRICT_CPU = ROOT / "results/R3M22/CPU_ORACLE_STRICT.json"
PRIOR = ROOT / "results/R3M22/GPU_RESULT.json"
MAX_FFT = 4000
MAX_GPU_WALL = 7200
MAX_WINDOW_WALL = 1800
GPU_RESERVE = 2 * 1024**3
HOST_RESERVE = 8 * 1024**3
MAX_BASIS = 10
GLOBAL_INNER_BUDGET = 1e-14
TIGHT_INNER_BUDGET = 1e-15
CALIBRATION_LIMIT = 2.103970853068276e-14
# 3 preflight + twice (160 calibration + 34 Strang/overlap FFTs + 1600
# required CF4) = 3591. Optional n8/sub4 is at most 640 per window.
REQUIRED_PER_WINDOW_MAX = 160 + 34 + 1600
OPTIONAL_SUBSTEP_MAX = 640
REQUIRED_TOTAL_MAX = 3 + 2 * REQUIRED_PER_WINDOW_MAX


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


class Budget:
    def __init__(self, started, preflight_count):
        self.started = started
        self.count = preflight_count
        self.window_started = None

    def begin_window(self):
        self.window_started = time.perf_counter()

    def check(self):
        now = time.perf_counter()
        if now - self.started >= MAX_GPU_WALL:
            raise TimeoutError("R3M23 total GPU wall cap reached")
        if self.window_started is not None and now - self.window_started >= MAX_WINDOW_WALL:
            raise TimeoutError("R3M23 short-window wall cap reached")

    def tick(self):
        self.check()
        if self.count >= MAX_FFT:
            raise TimeoutError("R3M23 FFT matvec cap reached")
        self.count += 1

    def reserve(self, future_max):
        self.check()
        return self.count + future_max <= MAX_FFT

    def end_window(self):
        self.check()
        elapsed = time.perf_counter() - self.window_started
        self.window_started = None
        return elapsed


def _distance(a, b, dv):
    return float(np.linalg.norm((a - b).ravel()) * math.sqrt(dv))


def assess_window(distances, optional_ran):
    """Admit only a same-window Strang-scale comparison with both repeats."""
    scale = min(distances[k] for k in ("strang_4_vs_cf4_16",
                                        "strang_8_vs_cf4_16",
                                        "strang_16_vs_cf4_16"))
    threshold = .01 * scale
    passed = bool(scale > 0 and math.isfinite(scale) and
                  distances["cf4_8_to_16"] < threshold and
                  distances["inner_16_repeat"] < threshold and
                  optional_ran and distances["substep_8_repeat"] < threshold)
    return scale, threshold, passed


def _endpoint(host, wall, transfer, dv, *, fft_matvecs, infos=None):
    row = dict(sha256=hashlib.sha256(host.tobytes()).hexdigest(),
               norm=float(np.vdot(host, host).real * dv),
               finite=bool(np.isfinite(host).all()),
               fft_matvecs=fft_matvecs,
               propagation_seconds=wall,
               host_transfer_seconds=transfer)
    if infos is not None:
        row.update(max_basis_used=max(a["basis_dimension"] for i in infos for a in i["actions"]),
                   accumulated_exact_arithmetic_inner_bound=sum(
                       i["accumulated_exact_arithmetic_upper_bound"] for i in infos))
    if not row["finite"] or not math.isfinite(row["norm"]):
        raise FloatingPointError("nonfinite endpoint")
    return row


def _to_host(cp, state):
    mark = time.perf_counter()
    host = cp.asnumpy(state)
    return host, time.perf_counter() - mark


def _cf4(mf, state, t0, horizon, n, substeps, global_budget, budget, basis_bytes):
    import cupy as cp
    current = state.copy()
    infos = []
    before = budget.count
    mark = time.perf_counter()
    for j in range(n):
        current, info = mf.cf4_step(
            current, t0 + j * horizon / n, horizon / n,
            physical_step_budget=global_budget / n,
            action_substeps=substeps, max_basis=MAX_BASIS,
            max_basis_bytes=basis_bytes)
        infos.append(info)
    cp.cuda.get_current_stream().synchronize()
    wall = time.perf_counter() - mark
    host, transfer = _to_host(cp, current)
    del current
    budget.check()
    if budget.count - before != sum(i["total_fft_matvec"] for i in infos):
        raise RuntimeError("full-H FFT matvec accounting mismatch")
    return host, _endpoint(host, wall, transfer, mf.runner.dv,
                           fft_matvecs=budget.count - before, infos=infos)


def _strang_ladder(runner, mf, state, t0, horizon, budget):
    import cupy as cp
    endpoints, rows, parity = {}, {}, {}
    dt = horizon / 4
    candidate = ProductionBufferedStep(runner)
    mark = time.perf_counter()
    budget.tick()
    frozen_one = runner.step(state.copy(), t0 + .5 * dt)
    budget.tick()
    buffered_one = candidate.step(state.copy(), t0 + .5 * dt)
    cp.cuda.get_current_stream().synchronize()
    one_a, _ = _to_host(cp, frozen_one)
    one_b, _ = _to_host(cp, buffered_one)
    parity["one_step"] = accuracy_metrics(one_a, one_b)
    parity["one_step_wall_seconds_including_transfers"] = time.perf_counter() - mark
    del frozen_one, buffered_one, one_a, one_b
    if parity["one_step"]["status"] != "PASS_SAME_DISCRETIZATION_PARITY":
        raise ValueError("frozen/buffer one-step parity failed")
    for n in (4, 8, 16):
        step_dt = horizon / n
        current = state.copy()
        before = budget.count
        mark = time.perf_counter()
        if n == 4:
            for j in range(n):
                budget.tick()
                current = runner.step(current, t0 + (j + .5) * step_dt)
        else:
            kinetic_phase = cp.exp(-.5j * step_dt * runner.k2)
            cap_half = cp.exp(-.5 * step_dt * mf.W)
            for j in range(n):
                budget.tick()
                phase = cp.exp(-.5j * step_dt * runner.Vmid(
                    t0 + (j + .5) * step_dt)) * cap_half
                current = phase * current
                current = cp.fft.ifftn(kinetic_phase * cp.fft.fftn(current))
                current = phase * current
            del kinetic_phase, cap_half
        cp.cuda.get_current_stream().synchronize()
        wall = time.perf_counter() - mark
        host, transfer = _to_host(cp, current)
        budget.check()
        endpoints[f"S{n}"] = host
        rows[f"S{n}"] = _endpoint(host, wall, transfer, runner.dv,
                                  fft_matvecs=budget.count - before)
        del current
    current = state.copy()
    before = budget.count
    mark = time.perf_counter()
    for j in range(4):
        budget.tick()
        current = candidate.step(current, t0 + (j + .5) * dt)
    cp.cuda.get_current_stream().synchronize()
    wall = time.perf_counter() - mark
    buffered, transfer = _to_host(cp, current)
    rows["B4"] = _endpoint(buffered, wall, transfer, runner.dv,
                            fft_matvecs=budget.count - before)
    parity["four_step"] = accuracy_metrics(endpoints["S4"], buffered)
    del candidate, current, buffered
    budget.check()
    if parity["four_step"]["status"] != "PASS_SAME_DISCRETIZATION_PARITY":
        raise ValueError("frozen/buffer four-step parity failed")
    return endpoints, rows, parity


def _one_window(row, cfg, budget, *, reserve_next_required):
    import cupy as cp
    source = np.load(Path(row["generation_directory"]) / "state.npy",
                     mmap_mode="r", allow_pickle=False)
    mark = time.perf_counter()
    runner = ControlledTDLRunner(cfg)
    state = cp.asarray(source)
    cp.cuda.get_current_stream().synchronize()
    upload = time.perf_counter() - mark
    mf = BoundedMatrixFreeFullH(runner)
    mf.matvec_monitor = budget.tick
    free = int(cp.cuda.runtime.memGetInfo()[0])
    min_free = free
    if free < GPU_RESERVE or hardware_inventory(include_gpu=False)["memory"]["available_bytes"] < HOST_RESERVE:
        raise MemoryError("resource reserve lost after selected checkpoint upload")
    budget.begin_window()
    start_count = budget.count
    t0, horizon = row["actual_start_time_au"], row["horizon_au"]
    basis_bytes = (MAX_BASIS + 1) * int(state.nbytes)
    strang, strang_rows, parity = _strang_ladder(runner, mf, state, t0, horizon, budget)
    del runner.kin, runner.mask, runner.cap_half
    cp.get_default_memory_pool().free_all_blocks()
    min_free = min(min_free, int(cp.cuda.runtime.memGetInfo()[0]))
    if min_free < GPU_RESERVE:
        raise MemoryError("GPU reserve lost before full-H calibration")
    calibration, cal_states = {}, {}
    for label, substeps, inner in (("sub2", 2, GLOBAL_INNER_BUDGET),
                                   ("sub4", 4, GLOBAL_INNER_BUDGET),
                                   ("sub2_tight", 2, TIGHT_INNER_BUDGET)):
        host, info = _cf4(mf, state, t0, horizon / 16, 1, substeps,
                          inner / 16, budget, basis_bytes)
        cal_states[label], calibration[label] = host, info
        min_free = min(min_free, int(cp.cuda.runtime.memGetInfo()[0]))
        if min_free < GPU_RESERVE:
            raise MemoryError("GPU reserve lost during calibration")
    cal_dist = dict(substep_repeat=_distance(cal_states["sub2"], cal_states["sub4"], runner.dv),
                    tighter_inner_repeat=_distance(cal_states["sub2"], cal_states["sub2_tight"], runner.dv))
    del cal_states
    if any(value >= CALIBRATION_LIMIT for value in cal_dist.values()):
        elapsed = budget.end_window()
        return dict(status="INNER_CALIBRATION_UNRESOLVED", label=row["label"],
                    calibration=calibration, calibration_distances=cal_dist,
                    calibration_limit=CALIBRATION_LIMIT,
                    frozen_buffer_parity=parity, strang_endpoints=strang_rows,
                    window_wall_seconds=elapsed, fft_matvecs=budget.count - start_count,
                    full_methods="NOT_RUN", input_upload_seconds=upload,
                    minimum_gpu_free_bytes=min_free)
    endpoints, methods = {}, {}
    for label, n, substeps, inner in (("CF4_8", 8, 2, GLOBAL_INNER_BUDGET),
                                     ("CF4_16", 16, 2, GLOBAL_INNER_BUDGET),
                                     ("CF4_16_tight", 16, 2, TIGHT_INNER_BUDGET)):
        endpoints[label], methods[label] = _cf4(mf, state, t0, horizon, n,
                                               substeps, inner, budget, basis_bytes)
        min_free = min(min_free, int(cp.cuda.runtime.memGetInfo()[0]))
        if min_free < GPU_RESERVE:
            raise MemoryError("GPU reserve lost during full-H ladder")
    optional_reserve = OPTIONAL_SUBSTEP_MAX + reserve_next_required
    optional_ran = budget.reserve(optional_reserve)
    if optional_ran:
        endpoints["CF4_8_sub4"], methods["CF4_8_sub4"] = _cf4(
            mf, state, t0, horizon, 8, 4, GLOBAL_INNER_BUDGET, budget, basis_bytes)
        min_free = min(min_free, int(cp.cuda.runtime.memGetInfo()[0]))
        if min_free < GPU_RESERVE:
            raise MemoryError("GPU reserve lost during substep repeat")
    budget.check()
    distances = dict(strang_4_to_8=_distance(strang["S4"], strang["S8"], runner.dv),
                     strang_8_to_16=_distance(strang["S8"], strang["S16"], runner.dv),
                     cf4_8_to_16=_distance(endpoints["CF4_8"], endpoints["CF4_16"], runner.dv),
                     inner_16_repeat=_distance(endpoints["CF4_16"], endpoints["CF4_16_tight"], runner.dv),
                     strang_4_vs_cf4_16=_distance(strang["S4"], endpoints["CF4_16"], runner.dv),
                     strang_8_vs_cf4_16=_distance(strang["S8"], endpoints["CF4_16"], runner.dv),
                     strang_16_vs_cf4_16=_distance(strang["S16"], endpoints["CF4_16"], runner.dv))
    if optional_ran:
        distances["substep_8_repeat"] = _distance(endpoints["CF4_8"], endpoints["CF4_8_sub4"], runner.dv)
    scale, threshold, comparison_pass = assess_window(distances, optional_ran)
    elapsed = budget.end_window()
    result = dict(schema="BASS_CR_R3M23_WINDOW_RESULT_V1", label=row["label"],
                  done=row["done"], start_time_au=t0, horizon_au=horizon,
                  checkpoint_sha256=row["expected_state_npy_sha256"],
                  status=("STRANG_SCALE_REFERENCE_CONSISTENT" if comparison_pass
                          else "STRANG_SCALE_REFERENCE_UNRESOLVED"),
                  calibration=calibration, calibration_distances=cal_dist,
                  calibration_limit=CALIBRATION_LIMIT,
                  frozen_buffer_parity=parity, strang_endpoints=strang_rows,
                  full_h_endpoints=methods, distances=distances,
                  strang_comparison_scale=scale, one_percent_threshold=threshold,
                  full_window_substep_repeat=("RUN" if optional_ran else "NOT_RUN_RESOURCE_RESERVE"),
                  fft_matvecs=budget.count - start_count,
                  window_wall_seconds=elapsed, input_upload_seconds=upload,
                  minimum_gpu_free_bytes=min_free,
                  reference_semantics="FOUR_B2_DT_SAME_DISCRETE_H_STRANG_SCALE_ONLY",
                  independent_production_ode=False, production_admission=False,
                  remote_restore="NOT_TESTED")
    del state, mf, runner, endpoints, strang
    cp.get_default_memory_pool().free_all_blocks()
    return result


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    budget = None
    stage = "INPUT_GUARD"
    try:
        guard = json.loads((OUT / "INPUT_GUARD.json").read_text())
        selection = json.loads(SELECTION.read_text())
        strict = json.loads(STRICT_CPU.read_text())
        prior = json.loads(PRIOR.read_text())
        if (guard["status"] != "PASS_LOCAL_GENERATION_IDENTITY" or
                guard["selection_sha256"] != _sha(SELECTION) or
                guard["config_sha256"] != _sha(CONFIG) or
                guard["strict_cpu_oracle_sha256"] != _sha(STRICT_CPU) or
                source_digest() != FROZEN_SOURCE or not strict["all_oracle_resolved"] or
                prior["status"] != "REFERENCE_RESOLVED_AT_PRIOR_4_TO_8_SCALE" or
                [x["label"] for x in guard["selected_rows"]] != ["closest", "outgoing"] or
                REQUIRED_TOTAL_MAX > MAX_FFT):
            raise ValueError("R3M23 frozen inputs or required work invalid")
        stage = "PREFLIGHT"
        probe = allocation_preflight()
        prior_rate = prior["gpu_wall_seconds"] / prior["gpu_fft_matvec_total_including_preflight"]
        forecast = MAX_FFT * prior_rate
        probe.update(schema="BASS_CR_R3M23_PREFLIGHT_V1",
                     required_max_fft=REQUIRED_TOTAL_MAX,
                     possible_optional_max_fft=2 * OPTIONAL_SUBSTEP_MAX,
                     total_fft_cap=MAX_FFT,
                     forecast_total_seconds_at_full_cap=forecast,
                     forecast_is_measurement=False,
                     prior_measured_seconds_per_fft=prior_rate,
                     source_sha256=_sha(Path(__file__)),
                     inner_action_source_sha256=_sha(ROOT / "scripts/r3m22_inner_action.py"),
                     input_guard_sha256=_sha(OUT / "INPUT_GUARD.json"))
        if (probe["status"] != "PASS" or forecast > .8 * 2 * MAX_WINDOW_WALL or
                probe["gpu_free_after_matvec_probe"] < GPU_RESERVE or
                probe["actual_inventory"]["memory"]["available_bytes"] < HOST_RESERVE):
            probe["status"] = "COST_OR_RESOURCE_BLOCKED"
        _write_new(OUT / "PREFLIGHT.json", probe)
        if probe["status"] != "PASS":
            raise RuntimeError("R3M23 preflight blocked")
        budget = Budget(started, probe["preflight_fft_matvecs"])
        cfg = json.loads(CONFIG.read_text())
        windows = []
        for index, row in enumerate(selection["windows"][1:]):
            stage = "WINDOW_" + row["label"].upper()
            if (row["expected_state_npy_sha256"] != guard["selected_rows"][index]["state_npy_sha256"] or
                    row["horizon_au"] > 4 * selection["actual_dt_au"] * (1 + 1e-14)):
                raise ValueError("selected window identity changed")
            reserve = REQUIRED_PER_WINDOW_MAX if index == 0 else 0
            if not budget.reserve(REQUIRED_PER_WINDOW_MAX + reserve):
                raise TimeoutError("required next-window FFT reserve unavailable")
            window = _one_window(row, cfg, budget, reserve_next_required=reserve)
            windows.append(window)
            if window["status"] != "STRANG_SCALE_REFERENCE_CONSISTENT":
                break
        budget.check()
        result = dict(schema="BASS_CR_R3M23_GPU_RESULT_V1",
                      status=("TWO_WINDOWS_STRANG_SCALE_CONSISTENT" if len(windows) == 2 and
                              all(w["status"] == "STRANG_SCALE_REFERENCE_CONSISTENT" for w in windows)
                              else "CROSS_WINDOW_REFERENCE_UNRESOLVED"),
                      input_guard_sha256=_sha(OUT / "INPUT_GUARD.json"),
                      preflight_sha256=_sha(OUT / "PREFLIGHT.json"),
                      windows=windows, omitted_window_labels=[
                          x["label"] for x in selection["windows"][1 + len(windows):]],
                      gpu_fft_matvec_total_including_preflight=budget.count,
                      gpu_wall_seconds=time.perf_counter() - started,
                      max_fft_matvec=MAX_FFT, max_window_wall_seconds=MAX_WINDOW_WALL,
                      max_gpu_wall_seconds=MAX_GPU_WALL,
                      full_collision=False, preparation_run=False,
                      finer_h=False, representation_change=False,
                      projection="NOT_RUN", checkpoint_write="NOT_RUN",
                      production_admission=False, remote_restore="NOT_TESTED")
        if result["gpu_wall_seconds"] >= MAX_GPU_WALL:
            raise TimeoutError("total GPU wall exceeded after final result assembly")
        _write_new(OUT / "GPU_RESULT.json", result)
        return result
    except BaseException as exc:
        _write_new(OUT / "FIRST_FAILURE.json",
                   dict(schema="BASS_CR_R3M23_FIRST_FAILURE_V1", stage=stage,
                        type=type(exc).__name__, message=str(exc),
                        elapsed_seconds=time.perf_counter() - started,
                        fft_matvec_count=None if budget is None else budget.count,
                        automatic_retry=False, full_collision=False,
                        original_checkpoint_modified=False))
        raise


def main():
    result = run()
    print(json.dumps(dict(status=result["status"],
                          windows=[w["label"] for w in result["windows"]],
                          fft_matvecs=result["gpu_fft_matvec_total_including_preflight"],
                          wall_seconds=result["gpu_wall_seconds"])))


if __name__ == "__main__":
    main()
