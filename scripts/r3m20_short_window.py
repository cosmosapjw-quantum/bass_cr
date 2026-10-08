"""One bounded GPU job on immutable B2 checkpoint windows.

The preflight only probes allocation and full-H matvec cost. It never advances
the checkpoint. A separate `run` command requires its exact PASS receipt.
All outputs are create-only; no production checkpoint or collision is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time

import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m19_performance import hardware_inventory
from scripts.r3m20_matrix_free import FROZEN_SOURCE, MatrixFreeFullH

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "results/R3M20_N1/windows/SELECTION.json"
OUT = ROOT / "results/R3M20_N1/windows"
CONFIG = ROOT / "configs/r3m17/B2.json"
MAX_FFT_MATVEC = 4000
MAX_GPU_WALL_SECONDS = 7200
MAX_WINDOW_SECONDS = 1800
GPU_RESERVE = 2 * 1024**3
HOST_RESERVE = 8 * 1024**3
MAX_BASIS = 10
ACTION_SUBSTEPS = 8


class ProductionBufferedStep:
    """Opt-in production-shape allocation reuse, algebraically same frozen step."""

    def __init__(self, runner):
        self.runner = runner
        self.xp = runner.xp
        self.phase = self.xp.empty(runner.spec.shape(), dtype=self.xp.complex128)
        self.work = self.xp.empty_like(self.phase)

    def step(self, psi, t_mid):
        runner, xp = self.runner, self.xp
        if psi.shape != self.phase.shape or psi.dtype != xp.dtype("complex128"):
            raise ValueError("complex128 state/grid mismatch")
        xp.multiply(runner.Vmid(t_mid), -.5j * runner.dt_actual, out=self.phase)
        xp.exp(self.phase, out=self.phase)
        xp.multiply(self.phase, runner.cap_half, out=self.phase)
        xp.multiply(self.phase, psi, out=self.work)
        spectrum = xp.fft.fftn(self.work)
        xp.multiply(spectrum, runner.kin, out=spectrum)
        result = xp.fft.ifftn(spectrum)
        xp.multiply(result, self.phase, out=result)
        return result


def _write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inputs():
    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source digest mismatch")
    selection = json.loads(SELECTION.read_text())
    cfg = json.loads(CONFIG.read_text())
    if (selection["schema"] != "BASS_CR_R3M20_N1_FROZEN_WINDOW_SELECTION_V1"
            or selection["B2_config_sha256"] != _sha(CONFIG)
            or len(selection["windows"]) != 3
            or any(row["horizon_au"] > 4 * selection["actual_dt_au"] * (1 + 1e-14)
                   for row in selection["windows"])):
        raise ValueError("frozen selection/config/horizon mismatch")
    guard = json.loads((OUT / "INCOMING_GUARD.json").read_text())
    if (guard["status"] != "PASS_LOCAL_GENERATION_IDENTITY"
            or guard["state_npy_sha256"] != selection["windows"][0]["expected_state_npy_sha256"]):
        raise ValueError("incoming generation guard absent or changed")
    return selection, cfg


def preflight():
    selection, cfg = _inputs()
    import cupy as cp
    inventory = hardware_inventory(include_gpu=True)
    if (inventory["gpu"].get("status") != "AVAILABLE"
            or inventory["gpu"]["device_free_bytes"] < GPU_RESERVE
            or inventory["memory"]["available_bytes"] < HOST_RESERVE):
        raise MemoryError("initial GPU/host reserve not met")
    row = selection["windows"][0]
    state_path = Path(row["generation_directory"]) / "state.npy"
    if state_path.stat().st_size != row["expected_state_npy_bytes"]:
        raise ValueError("selected checkpoint byte size changed")
    state_map = np.load(state_path, mmap_mode="r", allow_pickle=False)
    if state_map.dtype != np.dtype("complex128"):
        raise ValueError("selected checkpoint dtype changed")
    points = state_map.size
    vector_bytes = int(points * 16)
    # Conservative screen before CUDA allocations. Probe then tests actual
    # residency with basis+work+FFT allowances, not just this estimate.
    modeled_vectors = MAX_BASIS + 1 + 4 + 1  # basis, work/FFT allowance, input
    modeled_static = 4 * vector_bytes  # runner/static/potential/CUDA allowance
    modeled_total = modeled_vectors * vector_bytes + modeled_static
    if inventory["gpu"]["device_free_bytes"] < modeled_total + GPU_RESERVE:
        raise MemoryError("modeled basis/static/temporary bytes violate GPU reserve")
    runner = ControlledTDLRunner(cfg)
    mf = MatrixFreeFullH(runner)
    # The frozen splitter kinetic phase and mask are not needed for this
    # non-propagating action probe; W has already bound the mask.
    del runner.kin, runner.mask
    cp.get_default_memory_pool().free_all_blocks()
    state = cp.asarray(state_map)
    if cp.cuda.runtime.memGetInfo()[0] < GPU_RESERVE:
        raise MemoryError("post-input GPU reserve not met")
    held = []
    try:
        for _ in range(MAX_BASIS + 1 + 4):
            held.append(cp.empty_like(state))
        cp.cuda.get_current_stream().synchronize()
        free_with_probe = int(cp.cuda.runtime.memGetInfo()[0])
        if free_with_probe < GPU_RESERVE:
            raise MemoryError("basis-plus-temporary allocation probe violates GPU reserve")
        sample = []
        for _ in range(3):
            cp.cuda.get_current_stream().synchronize()
            start = time.perf_counter()
            acted = mf.generator_matvec(state, row["actual_start_time_au"])
            cp.cuda.get_current_stream().synchronize()
            sample.append(time.perf_counter() - start)
            del acted
        free_after_matvec = int(cp.cuda.runtime.memGetInfo()[0])
        if free_after_matvec < GPU_RESERVE:
            raise MemoryError("matvec allocation probe violates GPU reserve")
    finally:
        del held
        cp.get_default_memory_pool().free_all_blocks()
    observed_median = float(np.median(sample))
    # The first-window minimum set: 4/8/16 Strang, 4-step midpoint/average,
    # 4/8-step CF4, and one fixed-outer-step inner tightening. This is an
    # upper work estimate, not an assertion that every action needs m=10.
    planned_upper_matvec = (4 + 4 + 2*4 + 2*8 + 2*4) * ACTION_SUBSTEPS * MAX_BASIS
    estimated_seconds = observed_median * planned_upper_matvec
    status = "PASS" if (3 + planned_upper_matvec <= MAX_FFT_MATVEC and
                        estimated_seconds <= MAX_WINDOW_SECONDS * .8) else "COST_BLOCKED"
    result = dict(schema="BASS_CR_R3M20_N1_GPU_PREFLIGHT_V1", status=status,
                  input_selection_sha256=_sha(SELECTION), config_sha256=_sha(CONFIG),
                  matrix_free_source_sha256=_sha(ROOT / "scripts/r3m20_matrix_free.py"),
                  short_window_source_sha256=_sha(Path(__file__)),
                  label=row["label"], points=points, complex128_vector_bytes=vector_bytes,
                  max_basis=MAX_BASIS, action_substeps=ACTION_SUBSTEPS,
                  modeled_total_bytes=modeled_total, modeled_static_bytes=modeled_static,
                  actual_inventory=inventory, gpu_free_with_allocation_probe=free_with_probe,
                  gpu_free_after_matvec_probe=free_after_matvec,
                  matvec_wall_samples_seconds=sample, median_matvec_wall_seconds=observed_median,
                  preflight_fft_matvecs=3,
                  first_window_upper_fft_matvecs=planned_upper_matvec,
                  first_window_estimated_seconds=estimated_seconds,
                  gpu_reserve_bytes=GPU_RESERVE, host_reserve_bytes=HOST_RESERVE,
                  cost_estimate_is_full_window_measurement=False,
                  checkpoint_propagation_steps=0,
                  original_checkpoint_modified=False)
    return result


class WorkBudget:
    def __init__(self, *, initial_count, started):
        self.count = initial_count
        self.started = started
        self.window_started = time.perf_counter()

    def tick(self):
        now = time.perf_counter()
        if (self.count >= MAX_FFT_MATVEC or now - self.started >= MAX_GPU_WALL_SECONDS
                or now - self.window_started >= MAX_WINDOW_SECONDS):
            raise TimeoutError("frozen FFT/GPU/window budget exhausted before next matvec")
        self.count += 1


def _host_array(state, cp):
    start = time.perf_counter()
    value = cp.asnumpy(state)
    return value, time.perf_counter() - start


def _endpoint_record(state, dv):
    return dict(norm=float(np.vdot(state, state).real * dv),
                sha256=hashlib.sha256(state.tobytes()).hexdigest(),
                finite=bool(np.isfinite(state).all()))


def _compact_decomposition(s, mid, avg, ref, dv):
    names = ("split", "midpoint_quadrature", "time_ordering")
    parts = (s-mid, mid-avg, avg-ref)
    gram = [[complex(np.vdot(a,b)*dv) for b in parts] for a in parts]
    total = s-ref
    direct = float(np.vdot(total,total).real*dv)
    reconstructed = float(sum(value.real for row in gram for value in row))
    return dict(component_norms={name:math.sqrt(max(0.,gram[i][i].real)) for i,name in enumerate(names)},
                gram={f"{a},{b}":[gram[i][j].real,gram[i][j].imag]
                      for i,a in enumerate(names) for j,b in enumerate(names)},
                direct_squared_norm=direct, reconstructed_squared_norm=reconstructed,
                squared_norm_closure_residual=reconstructed-direct,
                vector_closure_norm=float(np.linalg.norm(sum(parts)-total)*math.sqrt(dv)),
                phase_alignment_used=False,
                semantics="RAW_SAME_INITIAL_SAME_HORIZON_PROVISIONAL_CF4_DT2_REFERENCE")


def run_first_window():
    import cupy as cp
    from scripts.r3m19_performance import accuracy_metrics
    selection, cfg = _inputs()
    preflight_path = OUT / "PREFLIGHT_v2.json"
    pre = json.loads(preflight_path.read_text())
    tiny = json.loads((ROOT / "results/R3M20_N1/tiny/MATRIX_FREE_TINY_v3.json").read_text())
    if (pre["status"] != "PASS" or pre["input_selection_sha256"] != _sha(SELECTION)
            or pre["config_sha256"] != _sha(CONFIG)
            or pre["matrix_free_source_sha256"] != _sha(ROOT / "scripts/r3m20_matrix_free.py")
            or pre["short_window_source_sha256"] != _sha(Path(__file__))
            or not tiny["all_oracle_resolved"]):
        raise ValueError("accuracy/identity/resource gates not all passed")
    current = hardware_inventory(include_gpu=True)
    if (current["gpu"].get("status") != "AVAILABLE"
            or current["gpu"]["device_free_bytes"] < pre["modeled_total_bytes"] + GPU_RESERVE
            or current["memory"]["available_bytes"] < HOST_RESERVE):
        raise MemoryError("live resource gate changed after preflight")
    row = selection["windows"][0]
    started = time.perf_counter()
    budget = WorkBudget(initial_count=pre["preflight_fft_matvecs"], started=started)
    timing = {}
    stage = "INPUT_UPLOAD"
    try:
        source = np.load(Path(row["generation_directory"]) / "state.npy",
                         mmap_mode="r", allow_pickle=False)
        mark = time.perf_counter()
        runner = ControlledTDLRunner(cfg)
        state = cp.asarray(source)
        cp.cuda.get_current_stream().synchronize()
        timing["runner_setup_and_checkpoint_upload_seconds"] = time.perf_counter() - mark
        mf = MatrixFreeFullH(runner)
        t0 = row["actual_start_time_au"]
        dt = selection["actual_dt_au"]
        horizon = 4 * dt
        initial_norm = float(cp.vdot(state,state).real.item() * runner.dv)
        if not math.isfinite(initial_norm) or initial_norm <= 0:
            raise ValueError("invalid checkpoint state norm")

        stage = "FROZEN_BUFFER_PARITY"
        candidate = ProductionBufferedStep(runner)
        mark = time.perf_counter()
        frozen_one = runner.step(state.copy(), t0 + .5*dt)
        budget.tick()
        buffered_one = candidate.step(state.copy(), t0 + .5*dt)
        budget.tick()
        cp.cuda.get_current_stream().synchronize()
        timing["one_step_parity_seconds"] = time.perf_counter() - mark
        one = accuracy_metrics(cp.asnumpy(frozen_one),cp.asnumpy(buffered_one))
        if one["status"] != "PASS_SAME_DISCRETIZATION_PARITY":
            raise ValueError("production-shape buffer parity failed")
        del frozen_one, buffered_one

        stage = "STRANG_DT_LADDER"
        endpoints = {}
        for n in (4,8,16):
            step_dt = horizon/n
            mark = time.perf_counter()
            current_state = state.copy()
            if n == 4:
                for j in range(n):
                    budget.tick()
                    current_state = runner.step(current_state, t0+(j+.5)*step_dt)
            else:
                kinetic_phase = cp.exp(-.5j*step_dt*runner.k2)
                cap_half = cp.exp(-.5*step_dt*mf.W)
                for j in range(n):
                    budget.tick()
                    ph = cp.exp(-.5j*step_dt*runner.Vmid(t0+(j+.5)*step_dt))*cap_half
                    current_state=ph*current_state
                    current_state=cp.fft.ifftn(kinetic_phase*cp.fft.fftn(current_state))
                    current_state=ph*current_state
                del kinetic_phase, cap_half
            cp.cuda.get_current_stream().synchronize()
            timing[f"strang_{n}_propagation_seconds"] = time.perf_counter()-mark
            endpoints[f"S{n}"],timing[f"strang_{n}_host_transfer_seconds"] = _host_array(current_state,cp)
            del current_state
        mark=time.perf_counter()
        buffer_state=state.copy()
        for j in range(4):
            budget.tick()
            buffer_state=candidate.step(buffer_state,t0+(j+.5)*dt)
        cp.cuda.get_current_stream().synchronize()
        timing["buffer_4_propagation_seconds"]=time.perf_counter()-mark
        buffered_host,timing["buffer_4_host_transfer_seconds"]=_host_array(buffer_state,cp)
        buffer_four=accuracy_metrics(endpoints["S4"],buffered_host)
        if buffer_four["status"] != "PASS_SAME_DISCRETIZATION_PARITY":
            raise ValueError("four-step production-shape buffer parity failed")
        del buffered_host, buffer_state, candidate
        del runner.kin, runner.mask, runner.cap_half
        cp.get_default_memory_pool().free_all_blocks()
        if cp.cuda.runtime.memGetInfo()[0] < GPU_RESERVE:
            raise MemoryError("GPU reserve lost before full-H action")

        stage = "FULL_H_ACTIONS"
        mf.matvec_monitor = budget.tick
        method_specs = (("E_mid4","midpoint",4,1e-12),
                        ("E_avg4","average",4,1e-12),
                        ("CF4_4","cf4",4,1e-12),
                        ("CF4_8","cf4",8,1e-12),
                        ("CF4_4_inner_tight","cf4",4,1e-13))
        action_info={}
        for label,method,n,tol in method_specs:
            step_dt=horizon/n
            current_state=state.copy()
            mark=time.perf_counter()
            infos=[]
            for j in range(n):
                current_state,info=mf.step(current_state,t0+j*step_dt,step_dt,
                                            method=method,tol=tol,max_basis=MAX_BASIS,
                                            max_basis_bytes=(MAX_BASIS+1)*int(state.nbytes),
                                            action_substeps=ACTION_SUBSTEPS)
                infos.append(info)
            cp.cuda.get_current_stream().synchronize()
            timing[f"{label}_propagation_seconds"]=time.perf_counter()-mark
            endpoints[label],timing[f"{label}_host_transfer_seconds"]=_host_array(current_state,cp)
            action_info[label]=dict(total_fft_matvec=sum(i["total_fft_matvec"] for i in infos),
                                    max_inner_residual_indicator=max(a["residual_indicator"] for i in infos for a in i["actions"]),
                                    max_basis_used=max(a["basis_dimension"] for i in infos for a in i["actions"]),
                                    action_substeps=ACTION_SUBSTEPS,relative_inner_tolerance=tol)
            del current_state
        if cp.cuda.runtime.memGetInfo()[0] < GPU_RESERVE:
            raise MemoryError("GPU reserve lost after full-H action")

        stage = "HOST_ANALYSIS"
        ref=endpoints["CF4_8"]
        inner_distance=float(np.linalg.norm((endpoints["CF4_4"]-endpoints["CF4_4_inner_tight"]).ravel())*math.sqrt(runner.dv))
        outer_distance=float(np.linalg.norm((endpoints["CF4_4"]-ref).ravel())*math.sqrt(runner.dv))
        if not math.isfinite(inner_distance) or not math.isfinite(outer_distance):
            raise ValueError("nonfinite reference refinement")
        records={}
        for label,value in endpoints.items():
            rec=_endpoint_record(value,runner.dv)
            if not rec["finite"]:
                raise ValueError(f"nonfinite endpoint: {label}")
            rec["raw_distance_to_cf4_dt2"]=float(np.linalg.norm((value-ref).ravel())*math.sqrt(runner.dv))
            rec["propagation_seconds"]=timing.get(f"{label}_propagation_seconds",timing.get(f"strang_{label[1:]}_propagation_seconds"))
            records[label]=rec
        decomp=_compact_decomposition(endpoints["S4"],endpoints["E_mid4"],endpoints["E_avg4"],ref,runner.dv)
        if abs(decomp["squared_norm_closure_residual"]) > 1e-8 or decomp["vector_closure_norm"] > 1e-8:
            raise ValueError("raw-vector/Gram decomposition failed closure")
        status="SHORT_WINDOW_COMPLETED_REFERENCE_CONDITIONAL"
        if inner_distance >= .01*min(x["raw_distance_to_cf4_dt2"] for k,x in records.items() if k!="CF4_8" and x["raw_distance_to_cf4_dt2"]>0):
            status="INNER_REFERENCE_UNRESOLVED"
        result=dict(schema="BASS_CR_R3M20_N1_FIRST_WINDOW_V1",status=status,
                    checkpoint_label=row["label"],checkpoint_done=row["done"],
                    checkpoint_sha256=row["expected_state_npy_sha256"],
                    input_selection_sha256=_sha(SELECTION),preflight_sha256=_sha(preflight_path),
                    actual_start_time_au=t0,actual_end_time_au=t0+horizon,
                    actual_dt_au=dt,horizon_au=horizon,initial_norm=initial_norm,
                    frozen_vs_buffer_one_step=one,frozen_vs_buffer_four_step=buffer_four,
                    method_endpoints=records,fullh_action_info=action_info,
                    inner_repeat_raw_distance=inner_distance,
                    cf4_outer_dt_to_dt2_raw_distance=outer_distance,
                    reference_semantics="CF4_DT2_CONDITIONAL_NO_INDEPENDENT_PRODUCTION_ODE_OR_DT4",
                    gram_decomposition=decomp,timing=timing,
                    gpu_fft_matvec_total_including_preflight=budget.count,
                    gpu_window_wall_seconds=time.perf_counter()-budget.window_started,
                    gpu_total_wall_seconds=time.perf_counter()-started,
                    projection="NOT_RUN",checkpoint_write="NOT_RUN",full_collision=False,
                    production_admission=False,remote_restore="NOT_TESTED")
        return result
    except BaseException as exc:
        _write_new(OUT/"FIRST_WINDOW_FIRST_FAILURE.json",
                   dict(schema="BASS_CR_R3M20_N1_FIRST_WINDOW_FAILURE_V1",stage=stage,
                        type=type(exc).__name__,message=str(exc),
                        elapsed_seconds=time.perf_counter()-started,
                        gpu_fft_matvec_count=budget.count,automatic_retry=False,
                        checkpoint_modified=False,full_collision=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "run"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.command == "preflight":
        try:
            report = preflight()
            _write_new(args.out or OUT / "PREFLIGHT.json", report)
            print(json.dumps({"status": report["status"],
                              "median_matvec_wall_seconds": report["median_matvec_wall_seconds"],
                              "estimated_first_window_seconds": report["first_window_estimated_seconds"]}))
        except BaseException as exc:
            _write_new(OUT / "PREFLIGHT_FIRST_FAILURE.json",
                       dict(status="FAILED", type=type(exc).__name__, message=str(exc),
                            propagation_steps=0, automatic_retry=False))
            raise
    else:
        report=run_first_window()
        _write_new(args.out or OUT / "FIRST_WINDOW.json",report)
        print(json.dumps({"status":report["status"],
                          "fft_matvecs":report["gpu_fft_matvec_total_including_preflight"],
                          "wall_seconds":report["gpu_window_wall_seconds"]}))


if __name__ == "__main__":
    main()
