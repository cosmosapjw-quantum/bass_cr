"""Bounded, opt-in split-step performance experiments; never a production runner.

The frozen two-center H, CAP, complex128 precision, midpoint and actual timestep
are shared within each comparison. Native-buffer reuse saves intermediate
allocations without kernel fusion. The optional CPU SciPy FFT candidate changes
only the FFT implementation and explicitly records its worker count. NumPy FFT
is NOT controlled by BLAS thread limits. GPU work uses unchanged CuPy FFT APIs.

No shape above 2**20 points, dimension above 256, or trajectory above 8 steps
is admitted. Timing includes two warmups per implementation and alternating
measurement order. CUDA events and synchronization distinguish device time,
host enqueue time, and synchronized wall time. No CPU fallback, production
checkpoint writing, scientific admission, or full-grid speed extrapolation.

Run in a fresh, dedicated process on an otherwise idle GPU. Working-byte models
are conservative screening estimates, NOT proven FFT peak bounds. A temporary
CuPy pool limit and FFT-cache limits apply only inside this sidecar; CUDA context
and library allocations remain outside the pool. Record observed device/pool/
cache counters separately, never add overlapping counters into a fake peak.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import statistics
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from cr_repro.util import config_hash

FROZEN_SOURCE = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
SCHEMA = "BASS_CR_R3M19_BOUNDED_PERFORMANCE_V1"
MAX_POINTS = 2**20
MAX_WORKING_BYTES = 1024**3
HOST_RESERVE = 128 * 1024**2
GPU_RESERVE = 1024**3
RELATIVE_STATE_TOL = 5e-13
RELATIVE_NORM_TOL = 2e-13


def _text(path):
    try:
        return Path(path).read_text().strip()
    except FileNotFoundError:
        return None


def _positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _gpu_counters(cp):
    free, total = cp.cuda.runtime.memGetInfo()
    pool = cp.get_default_memory_pool()
    cache = cp.fft.config.get_plan_cache()
    return dict(device_free_bytes=int(free), device_total_bytes=int(total),
                pool_used_bytes=int(pool.used_bytes()), pool_reserved_bytes=int(pool.total_bytes()),
                pool_limit_bytes=int(pool.get_limit()),
                fft_cache_current_bytes=int(cache.get_curr_memsize()),
                fft_cache_current_plans=int(cache.get_curr_size()),
                fft_cache_limit_bytes=int(cache.get_memsize()), fft_cache_limit_plans=int(cache.get_size()))


def hardware_inventory(*, include_gpu=False):
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else list(range(os.cpu_count() or 1))
    cores = set()
    for cpu in affinity:
        base = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
        package, core = _text(base / "physical_package_id"), _text(base / "core_id")
        if package is not None and core is not None:
            cores.add((package, core))
    quota = _text("/sys/fs/cgroup/cpu.max")
    quota_capacity = None
    if quota and quota.split()[0] != "max":
        amount, period = map(int, quota.split())
        quota_capacity = amount / period
    info = {}
    for line in (_text("/proc/meminfo") or "").splitlines():
        key, value = line.split(":", 1)
        info[key] = int(value.strip().split()[0]) * 1024
    available = info.get("MemAvailable")
    cgroup_max, cgroup_current = _text("/sys/fs/cgroup/memory.max"), _text("/sys/fs/cgroup/memory.current")
    if cgroup_max and cgroup_max != "max" and cgroup_current:
        remaining = max(0, int(cgroup_max) - int(cgroup_current))
        available = min(available, remaining) if available is not None else remaining
    cpu_models = [line.split(":", 1)[1].strip() for line in (_text("/proc/cpuinfo") or "").splitlines()
                  if line.startswith("model name")]
    gpu = {"status": "NOT_PROBED"}
    if include_gpu:
        try:
            cp = importlib.import_module("cupy")
        except ModuleNotFoundError as exc:
            if exc.name != "cupy":
                raise
            gpu = {"status": "CUPY_NOT_INSTALLED", "cpu_fallback": False}
        else:
            if cp.cuda.runtime.getDeviceCount() < 1:
                gpu = {"status": "NO_CUDA_DEVICE", "cpu_fallback": False}
            else:
                device = cp.cuda.Device()
                name = cp.cuda.runtime.getDeviceProperties(device.id)["name"]
                gpu = dict(status="AVAILABLE", device_id=int(device.id),
                           device_name=name.decode() if isinstance(name, bytes) else str(name),
                           cupy=cp.__version__, cuda_runtime=int(cp.cuda.runtime.runtimeGetVersion()),
                           cuda_driver_api=int(cp.cuda.runtime.driverGetVersion()),
                           context_initialized_for_inventory=True, **_gpu_counters(cp))
    return dict(schema="BASS_CR_R3M19_HARDWARE_INVENTORY_V1", python=platform.python_version(),
                numpy=np.__version__, platform=platform.platform(),
                cpu=dict(model_names=sorted(set(cpu_models)), affinity=affinity,
                         affinity_logical_count=len(affinity), physical_cores_in_affinity=len(cores) or None,
                         quota_logical_capacity=quota_capacity),
                memory=dict(available_bytes=available, host_total_bytes=info.get("MemTotal"),
                            cgroup_max_bytes=int(cgroup_max) if cgroup_max and cgroup_max != "max" else None,
                            cgroup_current_bytes=int(cgroup_current) if cgroup_current else None), gpu=gpu)


def plan_benchmark(inventory, *, shape=(64, 64, 96), backend="numpy", candidate="buffer_reuse",
                   steps=4, repeats=5, fft_workers=1, max_working_bytes=512 * 1024**2,
                   max_seconds=30.):
    if backend not in ("numpy", "cupy"):
        raise ValueError("explicit backend numpy or cupy required; no fallback")
    if candidate not in ("buffer_reuse", "scipy_fft_workers"):
        raise ValueError("unknown candidate")
    if len(shape) != 3 or any(type(n) is not int or not 4 <= n <= 256 for n in shape):
        raise ValueError("shape must have 3 dimensions in [4,256]")
    if any(n % 2 for n in shape):
        raise ValueError("even shape required to avoid Coulomb grid nodes")
    points = math.prod(shape)
    if points > MAX_POINTS:
        raise ValueError("shape exceeds bounded microbenchmark point cap")
    for name, value, maximum in (("steps", steps, 8), ("repeats", repeats, 10)):
        if _positive_integer(value, name) > maximum:
            raise ValueError(f"{name} exceeds hard work cap {maximum}")
    _positive_integer(fft_workers, "FFT workers")
    cpu = inventory["cpu"]
    worker_cap = cpu["physical_cores_in_affinity"] or cpu["affinity_logical_count"]
    if cpu.get("quota_logical_capacity") is not None:
        worker_cap = min(worker_cap, max(1, math.floor(cpu["quota_logical_capacity"])))
    worker_cap = min(worker_cap, cpu["affinity_logical_count"])
    if fft_workers > worker_cap:
        raise ValueError("FFT workers exceed observed affinity/physical-core/quota cap")
    if candidate == "buffer_reuse" and fft_workers != 1:
        raise ValueError("numpy.fft/CuPy native FFT has no controlled CPU workers here; select scipy_fft_workers")
    if candidate == "scipy_fft_workers" and backend != "numpy":
        raise ValueError("SciPy FFT workers candidate requires numpy backend")
    if _positive_integer(max_working_bytes, "memory budget") > MAX_WORKING_BYTES:
        raise ValueError("memory budget exceeds 1 GiB hard cap")
    if isinstance(max_seconds, bool) or not math.isfinite(max_seconds) or not 0 < max_seconds <= 60:
        raise ValueError("wall-time budget must be finite and <=60 seconds")
    # Arrays for runner, initial/reference/candidate, FFT results and scratch;
    # plus an explicit 64-MiB allowance. This is a screening model, not a peak proof.
    estimate = 256 * points + 64 * 1024**2
    if estimate > max_working_bytes:
        raise ValueError("estimated memory exceeds requested working budget")
    available = inventory["memory"].get("available_bytes")
    if not isinstance(available, int) or available < estimate + HOST_RESERVE:
        raise ValueError("insufficient/unknown available host memory")
    if backend == "cupy":
        gpu = inventory["gpu"]
        if gpu.get("status") != "AVAILABLE":
            raise ValueError("requested GPU unavailable; CPU fallback forbidden")
        if gpu["device_free_bytes"] < max_working_bytes + GPU_RESERVE:
            raise ValueError("insufficient free GPU memory for budget plus reserve")
        if gpu.get("pool_reserved_bytes", 0) > max_working_bytes:
            raise ValueError("existing GPU pool exceeds fresh-process benchmark budget")
    cfg = dict(energy_keV_per_u=100., b=2., backend=backend,
               grid=dict(xlim=[-shape[0] / 4, shape[0] / 4],
                         ylim=[-shape[1] / 4, shape[1] / 4],
                         zlim=[-shape[2] / 4, shape[2] / 4], dx=.5),
               dt=.0125, z_start=-2., z_stop=2., initial_state="analytic",
               absorber_width=1., absorber_power=.125, absorber_reference_dt=.05,
               checkpoint_stride=128, project_nmax=1, capture_plane=1.)
    request = dict(shape=list(shape), backend=backend, candidate=candidate, steps=steps,
                   repeats=repeats, fft_workers=fft_workers, max_working_bytes=max_working_bytes,
                   max_seconds=float(max_seconds))
    return dict(schema=SCHEMA, status="PLAN_ONLY_NOT_EXECUTED", inventory=inventory,
                request=request, config=cfg, config_sha256=config_hash(cfg),
                points=points, estimated_working_bytes=estimate,
                memory_estimate_is_peak_guarantee=False, worker_cap=worker_cap,
                blas_threads=1, numpy_fft_worker_control=False, warmup_repeats=2,
                total_bounded_step_calls=2 * (repeats + 2) * steps,
                production_admitted=False)


class BufferedSplitStep:
    """No operator change; no fast-math, fused exponentials, or state mutation."""
    def __init__(self, runner, *, candidate="buffer_reuse", fft_workers=1):
        if math.prod(runner.spec.shape()) > MAX_POINTS:
            raise ValueError("candidate shape exceeds bounded microbenchmark point cap")
        self.runner = runner
        self.xp = runner.xp
        self.phase = self.xp.empty(runner.spec.shape(), dtype=self.xp.complex128)
        self.work = self.xp.empty_like(self.phase)
        self.fft = self.xp.fft
        self.fft_options = {}
        if candidate == "scipy_fft_workers":
            if runner.backend != "numpy":
                raise ValueError("SciPy FFT candidate requires numpy state")
            self.fft = importlib.import_module("scipy.fft")
            self.fft_options = dict(workers=fft_workers)
        elif candidate != "buffer_reuse":
            raise ValueError("unknown performance candidate")

    def step(self, psi, t_mid):
        if psi.shape != self.work.shape or psi.dtype != self.xp.dtype("complex128"):
            raise ValueError("complex128 state shape required")
        xp, runner = self.xp, self.runner
        xp.multiply(runner.Vmid(t_mid), -.5j * runner.dt_actual, out=self.phase)
        xp.exp(self.phase, out=self.phase)
        xp.multiply(self.phase, runner.cap_half, out=self.phase)
        xp.multiply(self.phase, psi, out=self.work)
        spectrum = self.fft.fftn(self.work, **self.fft_options)
        xp.multiply(spectrum, runner.kin, out=spectrum)
        result = self.fft.ifftn(spectrum, **self.fft_options)
        xp.multiply(result, self.phase, out=result)
        return result


def accuracy_metrics(reference, candidate):
    reference, candidate = np.asarray(reference), np.asarray(candidate)
    if reference.shape != candidate.shape or not np.isfinite(reference).all() or not np.isfinite(candidate).all():
        raise ValueError("finite states with equal shapes required")
    norm = float(np.linalg.norm(reference.ravel()))
    if norm <= 0:
        raise ValueError("positive reference norm required")
    candidate_norm = float(np.linalg.norm(candidate.ravel()))
    relative_state = float(np.linalg.norm((candidate - reference).ravel()) / norm)
    relative_norm = abs(candidate_norm**2 - norm**2) / norm**2
    passed = relative_state <= RELATIVE_STATE_TOL and relative_norm <= RELATIVE_NORM_TOL
    return dict(status="PASS_SAME_DISCRETIZATION_PARITY" if passed else "FAIL_SAME_DISCRETIZATION_PARITY",
                relative_unaligned_state_l2=relative_state, relative_squared_norm_difference=relative_norm,
                state_tolerance=RELATIVE_STATE_TOL, norm_tolerance=RELATIVE_NORM_TOL,
                observable_probabilities="NOT_EVALUATED_NOT_A_PRODUCTION_CHANNEL_BENCHMARK")


@contextmanager
def _gpu_limits(cp, budget):
    pool, cache = cp.get_default_memory_pool(), cp.fft.config.get_plan_cache()
    previous = pool.get_limit(), cache.get_size(), cache.get_memsize()
    try:
        pool.set_limit(size=budget)
        cache.set_size(2)
        cache.set_memsize(min(64 * 1024**2, budget // 4))
        yield
    finally:
        pool.set_limit(size=previous[0])
        cache.set_size(previous[1])
        cache.set_memsize(previous[2])


def _write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def benchmark(plan):
    """Execute a validated bounded plan; no `.run()` or checkpoint writer call."""
    expected = plan_benchmark(plan["inventory"], **plan["request"])
    if expected != plan:
        raise ValueError("plan identity/configuration changed")
    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source mismatch")
    request = plan["request"]
    gpu = request["backend"] == "cupy"
    actual_inventory = hardware_inventory(include_gpu=gpu)
    plan_benchmark(actual_inventory, **request)  # Recheck current resource availability before runner allocation.
    cp = importlib.import_module("cupy") if gpu else None
    from contextlib import nullcontext
    from threadpoolctl import threadpool_info, threadpool_limits
    if request["candidate"] == "scipy_fft_workers":
        scipy = importlib.import_module("scipy.fft")
        scipy_version = importlib.import_module("scipy").__version__
    else:
        scipy_version = None
    started = time.perf_counter()
    deadline = started + request["max_seconds"]
    observed = []
    timing = {f"{name}_{clock}_seconds": [] for name in ("reference", "candidate")
              for clock in ("wall", "enqueue", "device")}
    original_pools = threadpool_info()
    metrics = None
    with _gpu_limits(cp, request["max_working_bytes"]) if gpu else nullcontext():
        runner = ControlledTDLRunner(plan["config"])
        initial, _ = runner.relaxed_initial()
        original_host = cp.asnumpy(initial) if gpu else np.asarray(initial).copy()
        initial_sha = hashlib.sha256(original_host.tobytes()).hexdigest()
        candidate = BufferedSplitStep(runner, candidate=request["candidate"], fft_workers=request["fft_workers"])
        if gpu:
            cp.cuda.get_current_stream().synchronize()
            observed.append(_gpu_counters(cp))
        # BLAS libraries are limited to one thread independently of FFT workers.
        # Import candidate FFT libraries first so threadpoolctl sees their pools.
        with threadpool_limits(limits=1):
            active_pools = threadpool_info()
            for repetition in range(plan["warmup_repeats"] + request["repeats"]):
                outputs = {}
                order = ("reference", "candidate") if repetition % 2 == 0 else ("candidate", "reference")
                for name in order:
                    state = initial.copy()  # reset excluded from step timing
                    if gpu:
                        cp.cuda.get_current_stream().synchronize()
                        counters = _gpu_counters(cp)
                        if counters["device_free_bytes"] < GPU_RESERVE:
                            raise MemoryError("GPU free-memory reserve violated; no fallback")
                        start_event, end_event = cp.cuda.Event(), cp.cuda.Event()
                        start_event.record()
                    wall_start = time.perf_counter()
                    advance = runner.step if name == "reference" else candidate.step
                    for step in range(request["steps"]):
                        if time.perf_counter() >= deadline:
                            raise TimeoutError("bounded benchmark wall-time budget exhausted")
                        state = advance(state, runner.t0 + (step + .5) * runner.dt_actual)
                    enqueue_seconds = time.perf_counter() - wall_start
                    device_seconds = None
                    if gpu:
                        end_event.record()
                        end_event.synchronize()
                        device_seconds = cp.cuda.get_elapsed_time(start_event, end_event) / 1000.
                    wall_seconds = time.perf_counter() - wall_start
                    if gpu:
                        observed.append(_gpu_counters(cp))
                    if repetition >= plan["warmup_repeats"]:
                        timing[f"{name}_wall_seconds"].append(wall_seconds)
                        timing[f"{name}_enqueue_seconds"].append(enqueue_seconds)
                        if gpu:
                            timing[f"{name}_device_seconds"].append(device_seconds)
                    outputs[name] = cp.asnumpy(state) if gpu else np.asarray(state)
                current = accuracy_metrics(outputs["reference"], outputs["candidate"])
                if current["status"] != "PASS_SAME_DISCRETIZATION_PARITY":
                    metrics = current
                    break
                if metrics is None or current["relative_unaligned_state_l2"] > metrics["relative_unaligned_state_l2"]:
                    metrics = current
            unchanged = cp.asnumpy(initial) if gpu else initial
            if hashlib.sha256(unchanged.tobytes()).hexdigest() != initial_sha:
                raise ValueError("candidate mutated shared initial state")
    passed = metrics["status"] == "PASS_SAME_DISCRETIZATION_PARITY"
    speedup = (statistics.median(timing["reference_wall_seconds"]) /
               statistics.median(timing["candidate_wall_seconds"])) if passed else None
    device_speedup = (statistics.median(timing["reference_device_seconds"]) /
                      statistics.median(timing["candidate_device_seconds"])) if passed and gpu else None
    return dict(schema=SCHEMA, status="BENCHMARK_COMPLETE_PARITY_PASSED" if passed else "PARITY_FAILED_SPEED_CLAIM_BLOCKED",
                plan=plan, actual_inventory=actual_inventory, numerical_source_digest=source_digest(),
                instrumentation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                initial_array_bytes_sha256=initial_sha, initial_dtype=str(initial.dtype),
                requested_dt=runner.dt, actual_dt=runner.dt_actual,
                actual_horizon=request["steps"] * runner.dt_actual,
                scipy_version=scipy_version, timing=timing, accuracy=metrics,
                median_wall_speedup= speedup, median_device_speedup=device_speedup,
                gpu_memory_observations=observed, memory_counters_are_peak_proof=False,
                process_peak_rss_kib=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                elapsed_total_seconds=time.perf_counter() - started,
                blas_pools_before=original_pools, blas_pools_inside=active_pools,
                blas_pools_after=threadpool_info(), production_admitted=False, full_collision_executed=False,
                timing_scope="WARM_MATCHED_MICROTRAJECTORY_EXCLUDES_SETUP_RESET_VALIDATION_IO",
                production_extrapolation="FORBIDDEN_NO_63M_POINT_SPEED_OR_ACCURACY_CLAIM")


def execute_benchmark(plan, out):
    out = Path(out)
    out.mkdir(exist_ok=False)
    _write_new(out / "PLAN.json", plan)
    try:
        result = benchmark(plan)
        _write_new(out / "RESULT.json", result)
    except BaseException as exc:
        _write_new(out / "FIRST_FAILURE.json", dict(status="FAILED_OR_INTERRUPTED", type=type(exc).__name__,
                   message=str(exc), cpu_fallback=False, automatic_retry=False))
        raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "plan", "benchmark"))
    parser.add_argument("--backend", choices=("numpy", "cupy"), default="numpy")
    parser.add_argument("--candidate", choices=("buffer_reuse", "scipy_fft_workers"), default="buffer_reuse")
    parser.add_argument("--shape", default="64,64,96")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--fft-workers", type=int, default=1)
    parser.add_argument("--max-working-mib", type=int, default=512)
    parser.add_argument("--max-seconds", type=float, default=30.)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    inventory = hardware_inventory(include_gpu=args.backend == "cupy")
    if args.command == "inventory":
        result = inventory
    else:
        result = plan_benchmark(inventory, shape=tuple(map(int, args.shape.split(","))), backend=args.backend,
                    candidate=args.candidate, steps=args.steps, repeats=args.repeats, fft_workers=args.fft_workers,
                    max_working_bytes=args.max_working_mib * 1024**2, max_seconds=args.max_seconds)
        if args.command == "benchmark":
            if args.out is None:
                parser.error("benchmark requires exclusive --out directory")
            result = execute_benchmark(result, args.out)
    if args.out is not None and args.command != "benchmark":
        _write_new(args.out, result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
