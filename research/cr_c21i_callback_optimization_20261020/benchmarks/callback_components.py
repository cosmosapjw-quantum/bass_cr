"""Bounded original-RHS callback component benchmark; no IVP/native solve.

Run in a fresh Python process.  The original reference event driver supplies
the actual first-cell RHS closure, intercepted immediately before solve_ivp.
Manufactured M64/128 fixtures replicate the original nine cohorts.  The
synthetic callback sequences and warm exact-cache best case are not measured
solver trajectories.  Two-worker batches own separate callbacks/providers.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import threading
import time
import traceback


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE.parent / "cr_c21e_event_native_20261018"
C21G = HERE.parent / "cr_c21g_reference_refinement_20261019"
EXPECTED_ADAPTER_SHA256 = "bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e"
WORKER_ENV = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
OPERATIONS = ("jacobian", "rhs", "partial_t")
MODES = ("original", "vectorized", "vectorized_exact")
REGIMES = ("cold_sequence", "warm_identical_point")
REPEATS = 3
POINTS_PER_TASK = 3
TOTAL_WALL_LIMIT_S = 90.0
MAX_ORIGINAL_RHS_PER_CLOSURE = 200000


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def append_json(stream, value):
    stream.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
    stream.flush()


def text_if_present(path):
    p = Path(path)
    return p.read_text().strip() if p.is_file() else None


def closure_value(fun, name):
    values = dict(zip(fun.__code__.co_freevars, fun.__closure__ or ()))
    if name not in values:
        raise RuntimeError("EXPECTED_ORIGINAL_CLOSURE_CELL_MISSING " + name)
    return values[name].cell_contents


class CapturedBeforeIntegrator(RuntimeError):
    pass


def summary_stats(values):
    return {"n": len(values), "min": min(values), "median": statistics.median(values),
            "max": max(values), "raw": values}


def source_snapshot(opt):
    h_manifest, _ = opt._verified_files(opt.DEFAULT_C21H, opt.C21H_MANIFEST_SHA256,
                                        "runtime_files")
    g_manifest, _ = opt._verified_files(C21G, opt.C21G_MANIFEST_SHA256,
                                        "c21g_runtime_files")
    return {"benchmark": record(__file__), "optimized_adapter": record(HERE / "optimized_adapter.py"),
            "c21h_manifest_sha256": opt.C21H_MANIFEST_SHA256,
            "c21h_runtime_files": h_manifest["runtime_files"],
            "c21g_manifest_sha256": opt.C21G_MANIFEST_SHA256,
            "c21g_runtime_files": g_manifest["c21g_runtime_files"],
            "c21f_source_identity": opt.source_snapshot(SOURCE, C21G)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=HERE / "evidence/component_benchmark_01")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started_utc = utc()
    started = time.monotonic()
    deadline = started + TOTAL_WALL_LIMIT_S
    files_before = None
    opt = None
    measured_rows = []
    batch_rows = []
    total_actual_calls = 0

    def guard():
        if time.monotonic() >= deadline:
            raise RuntimeError("COMPONENT_BENCHMARK_WALL_LIMIT")

    try:
        if "numpy" in sys.modules or "scipy" in sys.modules:
            raise RuntimeError("FRESH_PROCESS_BEFORE_NUMPY_REQUIRED")
        sys.dont_write_bytecode = True
        environment_before = {key: os.environ.get(key) for key in WORKER_ENV}
        for key in WORKER_ENV:
            os.environ[key] = "1"
        if not hasattr(os, "sched_getaffinity"):
            raise RuntimeError("ACTUAL_LINUX_AFFINITY_REQUIRED")
        affinity_before = sorted(os.sched_getaffinity(0))
        affinity = [cpu for cpu in affinity_before if cpu != 55][:2]
        if len(affinity) != 2:
            raise RuntimeError("TWO_CURRENT_ALLOWED_CPUS_REQUIRED")
        os.sched_setaffinity(0, affinity)
        if sorted(os.sched_getaffinity(0)) != affinity:
            raise RuntimeError("AFFINITY_APPLICATION_FAILED")
        import numpy as np
        import scipy
        spec = importlib.util.spec_from_file_location("c21i_component_adapter", HERE / "optimized_adapter.py")
        opt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(opt)
        if record(HERE / "optimized_adapter.py")["sha256"] != EXPECTED_ADAPTER_SHA256:
            raise RuntimeError("BENCHMARK_ADAPTER_IDENTITY_MISMATCH")
        files_before = source_snapshot(opt)
        write_json(output / "SOURCE_BEFORE.json", files_before)
        base = opt.load_frozen_adapter()
        base.private_reference(SOURCE)
        sys.path.insert(0, str(C21G))
        from campaign_contract import fixture_scales
        from run_experiment import make_fixture
        from event_coupler import ManufacturedMicro, Y_HE
        try:
            from threadpoolctl import threadpool_info
        except ImportError:
            pool_info = {"status": "OPTIONAL_TOOL_NOT_INSTALLED", "actual_worker_count": None}
        else:
            pool_info = {"status": "OBSERVED", "pools": threadpool_info()}
            if any(pool.get("num_threads") != 1 for pool in pool_info["pools"]):
                raise RuntimeError("LOADED_LIBRARY_WORKER_COUNT_NOT_ONE")
        inventory = {"recorded_at_utc": utc(), "python": sys.version,
                     "numpy": np.__version__, "scipy": scipy.__version__,
                     "platform": platform.platform(), "machine": platform.machine(),
                     "processor": platform.processor(), "pid": os.getpid(),
                     "environment_before": environment_before,
                     "environment_applied": {key: os.environ[key] for key in WORKER_ENV},
                     "affinity_before": affinity_before, "affinity_applied": affinity,
                     "exclusive_cpu_allocation_established": False,
                     "affinity_scope": "local benchmark process; not NCP allocation evidence",
                     "cpu_max": text_if_present("/sys/fs/cgroup/cpu.max"),
                     "memory_max": text_if_present("/sys/fs/cgroup/memory.max"),
                     "load_average": list(os.getloadavg()), "threadpools": pool_info,
                     "clock": vars(time.get_clock_info("perf_counter"))}
        write_json(output / "RUNTIME_INVENTORY.json", inventory)
        contract = {"schema": "C21I_CALLBACK_COMPONENT_BENCHMARK_CONTRACT_V1",
                    "registered_at_utc": utc(), "cohorts": [9, 64, 128],
                    "helium": [0.0, Y_HE], "modes": list(MODES),
                    "operations_in_order": list(OPERATIONS), "repeats": REPEATS,
                    "points_per_task": POINTS_PER_TASK, "tasks_per_batch": 2,
                    "schedules": ["serial_two_callbacks", "two_thread_batch"],
                    "regimes": {"cold_sequence": "fresh empty callback cache; three distinct represented state/time pairs",
                                "warm_identical_point": "one separately recorded untimed warmup triplet; three identical-point triplets"},
                    "source": "actual original source-pinned first-cell RHS closure, intercepted before solve_ivp",
                    "provider": "exact unchanged ManufacturedMicro class, no stateful subclass; independent instance per task",
                    "larger_fixture": "replicate original nine q/birth cohorts and divide each original amount by its replication count",
                    "clock_scope": "operation: callback only; batch: both tasks and loop/instrumentation; threaded batch includes executor creation/dispatch/join/shutdown",
                    "setup_scope": "private source load, original driver capture and callback construction recorded separately; warmup separately",
                    "cold_does_not_mean": "CPU cache flush or new Python interpreter per operation",
                    "numerical_acceptance": "all measured output arrays bitwise identical to independently evaluated original callback at each exact point",
                    "counter_acceptance": "actual original RHS closure counter delta equals callback original_rhs_evaluations delta",
                    "native_chemistry": "NOT_RUN", "ode_solver": "NOT_RUN",
                    "new_rust_binary_execution": "NOT_RUN", "global_error_bound": None,
                    "timing_claim_ceiling": "manufactured local callback components and two-task batch only; synthetic request order, not observed trajectory cache rate",
                    "max_original_rhs_per_closure": MAX_ORIGINAL_RHS_PER_CLOSURE,
                    "total_wall_limit_s": TOTAL_WALL_LIMIT_S,
                    "protected_cpu_ids": [55], "affinity": affinity,
                    "worker_count": 1, "batch_thread_count": 2,
                    "publication": "root-managed, not inferred by this harness"}
        write_json(output / "contract.json", contract)
        (output / "inputs").mkdir()
        (output / "reference_outputs").mkdir()
        (output / "different_outputs").mkdir()

        def array_bytes(value):
            return np.ascontiguousarray(value, dtype="<f8").tobytes()

        def capture(fixture):
            guard()
            ref = base.private_reference(SOURCE)
            provider = ManufacturedMicro()
            if type(provider) is not ManufacturedMicro or vars(provider):
                raise RuntimeError("EXACT_MANUFACTURED_PROVIDER_REQUIRED")
            scale = fixture_scales(asdict(fixture))
            captured = {}

            def sentinel(fun, span, y0, **controls):
                captured.update(fun=fun, span=tuple(span), y0=np.array(y0, copy=True), controls=controls)
                raise CapturedBeforeIntegrator()

            ref.solve_ivp = sentinel
            try:
                ref.run_reference_tau(fixture, provider, rtol=2e-11,
                                      atol=2e-14*np.asarray(scale["values"]),
                                      max_evaluations=MAX_ORIGINAL_RHS_PER_CLOSURE)
            except CapturedBeforeIntegrator:
                pass
            else:
                raise RuntimeError("ORIGINAL_EVENT_DRIVER_SENTINEL_NOT_REACHED")
            fun = captured["fun"]
            original_rhs = closure_value(fun, "rhs")
            dynamic = np.array(closure_value(fun, "dynamic"), copy=True)
            if closure_value(original_rhs, "provider") is not provider:
                raise RuntimeError("CAPTURED_PROVIDER_IDENTITY_MISMATCH")
            if closure_value(original_rhs, "calls") != 0:
                raise RuntimeError("RHS_CALLED_BEFORE_CAPTURE")
            captured.update(ref=ref, provider=provider, original_rhs=original_rhs,
                            dynamic=dynamic, scales=np.asarray(scale["values"])[dynamic], scale_contract=scale)
            return captured

        cases = []
        canonical = {}
        reference_records = []
        for count in (9, 64, 128):
            for helium in (0.0, Y_HE):
                fixture = make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003, Y=helium)
                original_digest = fixture.digest
                original_q, original_birth, original_amounts = fixture.q, fixture.birth, fixture.amounts
                replication = Counter(j % len(original_q) for j in range(count))
                if count != 9:
                    fixture = replace(fixture,
                        q=tuple(original_q[j % 9] for j in range(count)),
                        birth=tuple(original_birth[j % 9] for j in range(count)),
                        amounts=tuple(original_amounts[j % 9]/replication[j % 9] for j in range(count)),
                        source_identity=fixture.source_identity + f"_C21I_REPLICATED_M{count}")
                fixture = opt._freeze_fixture(fixture)
                name = f"m{count}_g{2 if helium == 0 else 4}"
                data = capture(fixture)
                callback = base.CellCallbacks(data["fun"], fixture, *data["span"],
                    data["scales"], data["dynamic"], data["ref"])
                points = []
                for point_id in range(POINTS_PER_TASK):
                    u = data["y0"].copy()
                    u[:count] = np.linspace(-.0125 + .001*point_id, .175 + .001*point_id, count)
                    for j, full in enumerate(data["dynamic"]):
                        if full == count:
                            u[j] = .31 + .001*point_id
                        elif full == count+1:
                            u[j] = .125 + .0001*point_id
                        elif full == count+2:
                            u[j] = .03125 + .0001*point_id
                        elif full == count+3:
                            u[j] *= 1.07 + .001*point_id
                    t = callback.lo + (.25 + .25*point_id)*(callback.hi-callback.lo)
                    z = u/callback.scales
                    z.setflags(write=False)
                    points.append((float(t), z))
                    for operation in OPERATIONS:
                        guard()
                        value = getattr(callback, operation)(t, z)
                        guard()
                        canonical[(name, point_id, operation)] = np.array(value, copy=True)
                        path = output / "reference_outputs" / f"{name}_p{point_id}_{operation}.npy"
                        with path.open("xb") as stream:
                            np.save(stream, value, allow_pickle=False)
                        reference_records.append({"case": name, "point": point_id, "operation": operation,
                            "shape": list(value.shape), "float64_bytes_sha256": digest(array_bytes(value)),
                            "artifact": str(path.relative_to(output)), "artifact_identity": record(path)})
                actual_calls = closure_value(data["original_rhs"], "calls")
                if actual_calls != callback.counts["original_rhs_evaluations"]:
                    raise RuntimeError("REFERENCE_ORIGINAL_RHS_COUNTER_MISMATCH")
                total_actual_calls += actual_calls
                write_json(output / "inputs" / (name + ".json"), {
                    "case": name, "fixture": asdict(fixture), "fixture_sha256": fixture.digest,
                    "original_nine_cohort_fixture_sha256": original_digest,
                    "replication_counts": dict(replication), "original_amounts": original_amounts,
                    "replicated_group_amount_fsum": [math.fsum(fixture.amounts[j] for j in range(count) if j % 9 == i) for i in range(9)],
                    "active_first_cell": callback.active.tolist(), "cell": data["span"],
                    "full_dimension": count+19, "integrated_dimension": callback.n,
                    "dynamic": data["dynamic"].tolist(), "scales": data["scale_contract"],
                    "points": [{"point": i, "time": t, "time_hex": t.hex(),
                                "scaled_state": z.tolist(), "scaled_state_float64_le_hex": array_bytes(z).hex()}
                               for i, (t, z) in enumerate(points)],
                    "capture": "original run_reference_tau solve_ivp sentinel; no numerical integration",
                    "reference_callback_counts": callback.counts,
                    "reference_actual_rhs_calls": actual_calls,
                    "reference_fd_nodes": callback.fd_nodes})
                cases.append({"name": name, "fixture": fixture, "points": points})
        write_json(output / "REFERENCE_OUTPUT_INDEX.json", reference_records)

        def prepare_task(case, mode):
            begin = time.perf_counter_ns()
            fixture = case["fixture"]
            data = capture(fixture)
            if mode == "original":
                callback_type = base.CellCallbacks
            else:
                admission = {"schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
                    "deterministic_successful_rhs": True,
                    "provider_kind": data["provider"].kind,
                    "provider_identity": {"class": "event_coupler.ManufacturedMicro",
                        "source_sha256": files_before["c21f_source_identity"]["runtime_files"]["src/event_coupler.py"]["sha256"],
                        "fixture_sha256": fixture.digest},
                    "admitted_by": "source-pinned exact immutable ManufacturedMicro instance and original closure in this bounded benchmark"}
                callback_type = opt.make_callback_type(base, mode,
                    cache_contract=admission, cache_guard=guard)
            callback = callback_type(data["fun"], fixture, *data["span"],
                                     data["scales"], data["dynamic"], data["ref"])
            guard()
            return {"callback": callback, "data": data,
                    "setup_ns": time.perf_counter_ns()-begin}

        def run_task(task, case, regime):
            callback, data = task["callback"], task["data"]
            before = dict(callback.counts)
            actual_before = closure_value(data["original_rhs"], "calls")
            rows = []
            for cycle in range(POINTS_PER_TASK):
                point = cycle if regime == "cold_sequence" else 0
                t, z = case["points"][point]
                for operation in OPERATIONS:
                    guard()
                    begin = time.perf_counter_ns()
                    value = getattr(callback, operation)(t, z)
                    elapsed = time.perf_counter_ns()-begin
                    guard()
                    rows.append((cycle, point, operation, elapsed, value))
            after = dict(callback.counts)
            actual_after = closure_value(data["original_rhs"], "calls")
            if actual_after-actual_before != after["original_rhs_evaluations"]-before["original_rhs_evaluations"]:
                raise RuntimeError("MEASURED_ORIGINAL_RHS_COUNTER_MISMATCH")
            return {"operations": rows, "counts_before": before, "counts_after": after,
                    "count_deltas": {key: after[key]-before[key] for key in before},
                    "actual_rhs_before": actual_before, "actual_rhs_after": actual_after,
                    "thread_ident": threading.get_ident(), "native_thread_id": threading.get_native_id(),
                    "thread_affinity": sorted(os.sched_getaffinity(0)),
                    "fd_nodes": list(callback.fd_nodes)}

        with (output / "operation_repeats.jsonl").open("x") as operation_stream, \
             (output / "task_repeats.jsonl").open("x") as task_stream, \
             (output / "batch_repeats.jsonl").open("x") as batch_stream:
            for repeat in range(REPEATS):
                modes = MODES[repeat:]+MODES[:repeat]
                schedules = ("serial_two_callbacks", "two_thread_batch") if repeat % 2 == 0 else ("two_thread_batch", "serial_two_callbacks")
                for case in cases:
                    for regime in REGIMES:
                        for mode in modes:
                            for schedule in schedules:
                                batch_id = f"r{repeat}_{case['name']}_{regime}_{mode}_{schedule}"
                                tasks = [prepare_task(case, mode) for _ in range(2)]
                                if tasks[0]["data"]["provider"] is tasks[1]["data"]["provider"] or tasks[0]["callback"] is tasks[1]["callback"]:
                                    raise RuntimeError("BATCH_CALLBACK_OR_PROVIDER_SHARED")
                                warmup_ns = 0
                                warmup_calls = 0
                                if regime == "warm_identical_point":
                                    warmup_begin = time.perf_counter_ns()
                                    for task in tasks:
                                        t, z = case["points"][0]
                                        for operation in OPERATIONS:
                                            guard()
                                            value = getattr(task["callback"], operation)(t, z)
                                            if array_bytes(value) != array_bytes(canonical[(case["name"], 0, operation)]):
                                                raise RuntimeError("WARMUP_BITWISE_OUTPUT_MISMATCH")
                                            guard()
                                        warmup_calls += closure_value(task["data"]["original_rhs"], "calls")
                                    warmup_ns = time.perf_counter_ns()-warmup_begin
                                guard()
                                batch_begin = time.perf_counter_ns()
                                if schedule == "serial_two_callbacks":
                                    results = [run_task(task, case, regime) for task in tasks]
                                else:
                                    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="c21i_components") as executor:
                                        futures = [executor.submit(run_task, task, case, regime) for task in tasks]
                                        results = [future.result() for future in futures]
                                batch_elapsed = time.perf_counter_ns()-batch_begin
                                guard()
                                actual_batch_calls = 0
                                operation_sum_ns = 0
                                for worker, result in enumerate(results):
                                    actual_calls = result["actual_rhs_after"]-result["actual_rhs_before"]
                                    actual_batch_calls += actual_calls
                                    total_actual_calls += result["actual_rhs_after"]
                                    for cycle, point, operation, elapsed, value in result.pop("operations"):
                                        expected = canonical[(case["name"], point, operation)]
                                        equal = value.shape == expected.shape and array_bytes(value) == array_bytes(expected)
                                        row = {"batch": batch_id, "repeat": repeat, "case": case["name"],
                                               "regime": regime, "mode": mode, "schedule": schedule,
                                               "worker": worker, "cycle": cycle, "point": point,
                                               "operation": operation, "elapsed_ns": elapsed,
                                               "shape": list(value.shape), "float64_bytes_sha256": digest(array_bytes(value)),
                                               "bitwise_equal_original": equal}
                                        append_json(operation_stream, row)
                                        measured_rows.append(row)
                                        operation_sum_ns += elapsed
                                        if not equal:
                                            path = output / "different_outputs" / f"{batch_id}_w{worker}_c{cycle}_{operation}.npy"
                                            with path.open("xb") as stream:
                                                np.save(stream, value, allow_pickle=False)
                                            raise RuntimeError("MEASURED_BITWISE_OUTPUT_MISMATCH " + str(path))
                                    task_row = {"batch": batch_id, "worker": worker,
                                                "setup_ns": tasks[worker]["setup_ns"], **result}
                                    append_json(task_stream, task_row)
                                row = {"batch": batch_id, "repeat": repeat, "case": case["name"],
                                       "regime": regime, "mode": mode, "schedule": schedule,
                                       "elapsed_ns": batch_elapsed, "setup_ns": sum(task["setup_ns"] for task in tasks),
                                       "warmup_ns": warmup_ns, "warmup_actual_rhs_calls": warmup_calls,
                                       "measured_actual_rhs_calls": actual_batch_calls,
                                       "sum_operation_ns": operation_sum_ns, "operation_count": 2*POINTS_PER_TASK*len(OPERATIONS),
                                       "thread_ids": [result["native_thread_id"] for result in results]}
                                row["including_setup_and_warmup_ns"] = row["elapsed_ns"] + row["setup_ns"] + row["warmup_ns"]
                                append_json(batch_stream, row)
                                batch_rows.append(row)

        grouped_ops = defaultdict(list)
        grouped_batches = defaultdict(list)
        for row in measured_rows:
            key = (row["case"], row["regime"], row["mode"], row["schedule"], row["operation"])
            grouped_ops[key].append(row["elapsed_ns"])
        for row in batch_rows:
            key = (row["case"], row["regime"], row["mode"], row["schedule"])
            grouped_batches[key].append(row["elapsed_ns"])
        operation_summary = [{**dict(zip(("case", "regime", "mode", "schedule", "operation"), key)),
                              "elapsed_ns": summary_stats(values)} for key, values in sorted(grouped_ops.items())]
        batch_summary = [{**dict(zip(("case", "regime", "mode", "schedule"), key)),
                          "elapsed_ns": summary_stats(values)} for key, values in sorted(grouped_batches.items())]
        by_key = {(row["repeat"], row["case"], row["regime"], row["mode"], row["schedule"]): row for row in batch_rows}
        paired = []
        for case in cases:
            for regime in REGIMES:
                for mode in MODES:
                    thread_speedups = [by_key[(r, case["name"], regime, mode, "serial_two_callbacks")]["elapsed_ns"] /
                                       by_key[(r, case["name"], regime, mode, "two_thread_batch")]["elapsed_ns"] for r in range(REPEATS)]
                    paired.append({"case": case["name"], "regime": regime, "mode": mode,
                                   "comparison": "same two tasks serial wall / threaded batch wall",
                                   "ratio": summary_stats(thread_speedups)})
                    if mode != "original":
                        for schedule in ("serial_two_callbacks", "two_thread_batch"):
                            speedups = [by_key[(r, case["name"], regime, "original", schedule)]["elapsed_ns"] /
                                        by_key[(r, case["name"], regime, mode, schedule)]["elapsed_ns"] for r in range(REPEATS)]
                            paired.append({"case": case["name"], "regime": regime, "mode": mode, "schedule": schedule,
                                           "comparison": "original batch wall / optimized batch wall",
                                           "ratio": summary_stats(speedups)})
        write_json(output / "SUMMARY.json", {"operation_groups": operation_summary,
            "batch_groups": batch_summary, "paired_comparisons": paired,
            "measured_operations": len(measured_rows), "measured_batches": len(batch_rows),
            "bitwise_comparison": "PASS", "original_rhs_counter_check": "PASS",
            "total_actual_original_rhs_calls_including_reference_and_warmup": total_actual_calls,
            "native_calls": 0, "ode_integrations": 0, "global_error_bound": None,
            "scope": contract["timing_claim_ceiling"]})
        files_after = source_snapshot(opt)
        write_json(output / "SOURCE_AFTER.json", files_after)
        if files_after != files_before:
            raise RuntimeError("BENCHMARK_DEPENDENCY_SOURCE_CHANGED")
        guard()
        receipt = {"schema": "C21I_CALLBACK_COMPONENT_BENCHMARK_RECEIPT_V1", "status": "COMPLETE_SCOPED",
                   "started_at_utc": started_utc, "finished_at_utc": utc(),
                   "wall_s": time.monotonic()-started, "benchmark_source": files_before["benchmark"],
                   "optimized_source": files_before["optimized_adapter"], "source_identity": "PASS_BEFORE_AFTER",
                   "original_rhs_capture": "ACTUAL_PINNED_CLOSURE", "formula_surrogate": False,
                   "batches": len(batch_rows), "tasks": 2*len(batch_rows), "operations": len(measured_rows),
                   "bitwise_outputs": "PASS", "actual_original_rhs_counter": "PASS",
                   "actual_original_rhs_calls_including_reference_and_warmup": total_actual_calls,
                   "native_calls": 0, "ode_integrations": 0, "global_error_bound": None,
                   "current_affinity": sorted(os.sched_getaffinity(0)), "protected_cpu_55_used": False}
        write_json(output / "EXECUTION_RECEIPT.json", receipt)
        print(json.dumps(receipt, sort_keys=True, allow_nan=False))
    except BaseException as error:
        with (output / "failure_traceback.txt").open("x") as stream:
            traceback.print_exc(file=stream)
        failure = {"status": "FAILED_SCOPED", "started_at_utc": started_utc,
                   "finished_at_utc": utc(), "wall_s": time.monotonic()-started,
                   "error": str(error), "exception_type": type(error).__name__,
                   "completed_operations": len(measured_rows), "completed_batches": len(batch_rows),
                   "native_calls": 0, "ode_integrations": 0, "global_error_bound": None}
        write_json(output / "FAILURE_RECEIPT.json", failure)
        print(json.dumps(failure, sort_keys=True, allow_nan=False))
        raise
    finally:
        payload = {str(path.relative_to(output)): record(path)
                   for path in sorted(output.rglob("*")) if path.is_file() and path.name != "PAYLOAD_MANIFEST.json"}
        write_json(output / "PAYLOAD_MANIFEST.json", {"schema": "C21I_COMPONENT_BENCHMARK_PAYLOAD_V1",
            "files": payload, "payload_count": len(payload), "payload_bytes": sum(item["bytes"] for item in payload.values()),
            "self_included": False})


if __name__ == "__main__":
    main()
