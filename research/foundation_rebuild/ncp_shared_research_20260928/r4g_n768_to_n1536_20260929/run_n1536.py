#!/usr/bin/env python3
"""One explicitly authorized N768 to N1536 successor rung; no automatic continuation."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import signal
import sys
import tempfile
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
R4F = HERE.parent / "r4f_parallel_migration_20260929"
R4C = HERE.parent / "r4c_temporal_continuation"
for directory in (HERE, R4F, R4C):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import continue_temporal as serial
from adaptive_workers import (DEFAULT_STAGES, StageObservation, build_useful_pilot_plan,
                              fastest_healthy_stage, summarize_scaling)
from parallel_bridge import (CacheOnlyProvider, GlobalBudget, dispatch_bounded,
                             publish_pair, validate_pair)
from qualified_provider import restore_query_store
from successor import (CONTEXT_ID, D768_REFERENCE_DISTANCE, MISSING_COUNT, PREDECESSOR_SHA256,
                       NATIVE_SOURCE_SHA256, NATIVE_LIBRARY_SHA256, NATIVE_BUILD_SHA256,
                       REQUIRED_COUNT, UNION_COUNT, admission_scope,
                       live_resource_census, plan_n1536, plan_receipts, required_missing,
                       validate_predecessor)
from worker_runtime import compute_query, initialize_worker
from execution_admission import check_native_build

_STOP = False


def _signal(signum, frame):
    global _STOP
    _STOP = True
    raise InterruptedError("N1536 coordinator received signal " + str(signum))


def _worker_with_rss(item):
    start = time.monotonic()
    receipt = compute_query(item)
    query = serial.strict_json(Path(receipt["task_dir"]) / "runtime_queries" /
                               (item.query_id + ".json"))
    receipt["selected_resolution"] = query["qualification"]["selected_resolution"]
    receipt["task_wall_seconds"] = time.monotonic() - start
    receipt["worker_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    return receipt


def _run_stage(items, *, source, args, contract, budget, out, canonical, workers):
    """Bounded spawn pool; completed pairs are published create-only before next dispatch."""
    if not items:
        raise ValueError("empty useful stage")
    cpus = [int(x) for x in args.cpus.split(",")][:workers]
    census = live_resource_census(cpus, workers, args.worker_ram_bytes)
    start_used = budget.used()
    start = time.monotonic()
    ctx = multiprocessing.get_context("spawn")
    publish_failures = 0
    published_receipts = {}
    try:
        with ProcessPoolExecutor(max_workers=workers, mp_context=ctx,
                                 initializer=initialize_worker,
                                 initargs=(str(source), args.analytic_build, contract, CONTEXT_ID,
                                           str(budget.root), str(out / "worker_tasks"),
                                           cpus, args.worker_ram_bytes)) as pool:
            def on_result(item, receipt):
                nonlocal publish_failures
                if receipt["query_id"] != item.query_id or not 2 <= receipt["raw_attempts"] <= len(contract["runtime_reference_resolutions"]):
                    raise ValueError("worker receipt identity or ladder bound mismatch")
                if (not math.isfinite(receipt["task_wall_seconds"])
                    or receipt["task_wall_seconds"] <= 0):
                    raise ValueError("worker task wall time invalid")
                try:
                    publish_pair(Path(receipt["task_dir"]) / "runtime_queries",
                                 canonical, item, CONTEXT_ID, contract)
                    published_receipts[item.query_id] = receipt
                except BaseException:
                    publish_failures += 1
                    raise
            receipts = dispatch_bounded(items, pool, _worker_with_rss, on_result,
                                        max_inflight=workers, deadline_unix=args.deadline_unix,
                                        cancelled=lambda: _STOP)
    except BaseException as exc:
        try:
            budget.cancel(type(exc).__name__ + ": " + str(exc))
        except FileExistsError:
            pass
        completed = [x.query_id for x in items
                     if (canonical / (x.query_id + ".json")).is_file()
                     and (canonical / (x.query_id + ".npz")).is_file()]
        failures = [x.query_id for x in items
                    if (out / "worker_tasks" / x.query_id / "TASK_FAILURE.json").is_file()]
        elapsed = time.monotonic() - start
        histogram = {}
        for receipt in published_receipts.values():
            rule = receipt["selected_resolution"]
            key = f"q{rule['order']}_h{rule['subdivisions']}"
            histogram[key] = histogram.get(key, 0) + 1
        serial.write_new(out / ("STAGE_" + str(workers) + "_FAILURE.json"),
                         {"schema": "BASS_R4G_USEFUL_STAGE_FAILURE_V1",
                          "workers": workers, "cpus": cpus,
                          "resource_census": census,
                          "query_ids": [x.query_id for x in items],
                          "completed_query_ids": completed, "completed_query_count": len(completed),
                          "failed_query_ids": failures, "failed_query_count": len(failures),
                          "wall_seconds": elapsed,
                          "queries_per_second": len(completed) / elapsed if elapsed > 0 else None,
                          "raw_attempts_consumed": budget.used() - start_used,
                          "raw_attempts_per_completed_query": (
                              (budget.used() - start_used) / len(completed) if completed else None),
                          "selected_resolution_histogram": histogram,
                          "per_query_task_wall_seconds":
                              {qid: receipt["task_wall_seconds"]
                               for qid, receipt in published_receipts.items()},
                          "peak_worker_rss_bytes":
                              max((r["worker_peak_rss_bytes"]
                                   for r in published_receipts.values()), default=None),
                          "coordinator_peak_rss_bytes":
                              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                          "filesystem_publish_failures": publish_failures,
                          "failure_type": type(exc).__name__, "failure": str(exc)})
        raise
    elapsed = time.monotonic() - start
    histogram = {}
    task_wall = {}
    for item, receipt in receipts.items():
        rule = receipt["selected_resolution"]
        key = f"q{rule['order']}_h{rule['subdivisions']}"
        histogram[key] = histogram.get(key, 0) + 1
        task_wall[item.query_id] = receipt["task_wall_seconds"]
    return {"schema": "BASS_R4G_USEFUL_STAGE_V1", "workers": workers,
            "cpus": cpus, "resource_census": census,
            "query_ids": [x.query_id for x in items],
            "completed_query_ids": [x.query_id for x in receipts],
            "completed_query_count": len(receipts),
            "failed_query_ids": [], "failed_query_count": 0,
            "wall_seconds": elapsed,
            "queries_per_second": len(receipts) / elapsed,
            "raw_attempts_per_completed_query": (budget.used() - start_used) / len(receipts),
            "selected_resolution_histogram": histogram,
            "per_query_task_wall_seconds": task_wall,
            "peak_worker_rss_bytes": max((r["worker_peak_rss_bytes"] for r in receipts.values()), default=None),
            "coordinator_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "raw_attempts_consumed": budget.used() - start_used,
            "filesystem_publish_failures": publish_failures}


def _science(args, out, admission):
    from cr_repro.observables import projectile_speed_au
    from metric_transport import phase_aligned_metric_distance, run_candidate
    from transport_policy import assess_temporal_pair

    with tempfile.TemporaryDirectory(prefix="bass_r4g_predecessor_") as tmp:
        source = Path(tmp) / "source"
        prior = validate_predecessor(Path(args.predecessor_archive),
                                     args.expected_predecessor_sha256, source)
        contract = prior["contract"]
        serial.write_new(out / "PREDECESSOR_ADMISSION.json",
                         {k: v for k, v in prior.items() if k not in ("previous_candidate", "contract")})
        deps = serial.verify_pinned_dependencies()
        serial.write_new(out / "PINNED_NUMERICAL_DEPENDENCIES.json", deps)
        native = check_native_build(Path(args.analytic_build), contract,
                                    serial.ANALYTIC / "moment_kernel.cpp")
        if (native["source_sha256"] != NATIVE_SOURCE_SHA256
            or native["library_sha256"] != NATIVE_LIBRARY_SHA256
            or native["build_receipt_sha256"] != NATIVE_BUILD_SHA256):
            raise ValueError("frozen native source/library/BUILD identity changed")
        pins_path = Path(args.source_pins)
        if serial.sha256_path(pins_path) != args.expected_source_pins_sha256:
            raise ValueError("approved source-pins SHA256 mismatch")
        pins = serial.strict_json(pins_path)
        if (pins.get("execution_commit") != admission["execution_commit"]
            or pins.get("execution_tree") != admission["execution_tree"]
            or pins.get("predecessor_archive_sha256") != PREDECESSOR_SHA256
            or pins.get("predecessor_manifest_sha256") != prior["manifest_sha256"]
            or pins.get("predecessor_report_sha256") != prior["report_sha256"]
            or pins.get("predecessor_admission_sha256") != prior["admission_sha256"]
            or pins.get("native") != native
            or pins.get("pinned_dependency_manifest_sha256") !=
               serial.sha256_path(serial.HERE / "PINNED_DEPENDENCIES.json")):
            raise ValueError("approved source-pins content mismatch")
        serial.copy_new(pins_path, out / "SOURCE_PINS.json")
        if serial.sha256_path(out / "SOURCE_PINS.json") != args.expected_source_pins_sha256:
            raise ValueError("source-pins changed during admission")
        serial.write_new(out / "NATIVE_PRELOAD_CHECK.json", native)
        v = projectile_speed_au(contract["energy_keV_per_u"])
        t0 = contract["z_initial_a0"] / v
        tf = contract["z_final_a0"] / v
        required = plan_n1536(CONTEXT_ID, t0, tf)
        qdir = source / "runtime_queries"
        present = {p.stem for p in qdir.glob("*.json")}
        missing = required_missing(required, present)
        stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
        if [len(s.query_ids) for s in stages] != [16, 32, 64] or len(remainder) != 1424:
            raise ValueError("adaptive useful pilot partition mismatch")
        by_id = {q.query_id: q for q in missing}
        plan, pilot = plan_receipts(required, missing, stages, remainder,
                                    admission["execution_commit"], admission["execution_tree"])
        serial.write_new(out / "REQUIRED_MISSING_QUERY_PLAN.json", plan)
        serial.write_new(out / "USEFUL_PILOT_PLAN.json", pilot)
        if (serial.sha256_path(out / "REQUIRED_MISSING_QUERY_PLAN.json") != args.expected_query_plan_sha256
            or serial.sha256_path(out / "USEFUL_PILOT_PLAN.json") != args.expected_useful_pilot_plan_sha256
            or pins.get("query_plan_sha256") != args.expected_query_plan_sha256
            or pins.get("useful_pilot_plan_sha256") != args.expected_useful_pilot_plan_sha256):
            raise ValueError("approved exact query/pilot plan hash mismatch")
        restored = restore_query_store(source, out, CONTEXT_ID)
        if restored != 2047:
            raise ValueError("predecessor cache restoration count mismatch")
        canonical = out / "runtime_queries"
        for rel in ("BASIS.json", "BASIS.npz", "SCIENCE_CONTEXT.json",
                    "REFERENCE_STATES.npz", "REFERENCE_RECEIPT.json",
                    "METRIC_CONNECTION.json", "CANDIDATE_N768.json", "CANDIDATE_N768.npz"):
            serial.copy_new(source / rel, out / rel)
        # Durable one-shot consumption precedes any worker/native library load.
        authroot = Path.home() / ".local/state/bass_r4g/authorizations"
        authroot.mkdir(parents=True, exist_ok=True)
        consumed = {**admission, "out": str(out),
                    "state": "CONSUMED_BEFORE_NATIVE_WORKERS",
                    "created_unix_seconds": time.time(),
                    "query_plan_sha256": serial.sha256_path(out / "REQUIRED_MISSING_QUERY_PLAN.json")}
        serial.write_new(authroot / (args.authorization_id + ".json"), consumed)
        serial.write_new(out / "AUTHORIZATION_CONSUMED.json", consumed)
        budget = GlobalBudget.create(out / "global_budget", parent_attempts=0,
                                     maximum=args.global_raw_attempt_cap,
                                     deadline_unix=args.deadline_unix)
        (out / "worker_tasks").mkdir()
        observations = []
        stage_records = []
        for stage_index, stage in enumerate(stages):
            try:
                record = _run_stage([by_id[qid] for qid in stage.query_ids],
                                    source=source, args=args, contract=contract,
                                    budget=budget, out=out, canonical=canonical,
                                    workers=stage.workers)
            except ValueError as exc:
                # A pre-dispatch live resource rejection may exclude a higher stage.
                if "live " not in str(exc) and "competing BASS" not in str(exc):
                    raise
                record = {"schema": "BASS_R4G_USEFUL_STAGE_V1",
                          "workers": stage.workers, "query_ids": list(stage.query_ids),
                          "cpus": [int(x) for x in args.cpus.split(",")][:stage.workers],
                          "resource_census": {"rejected": str(exc)},
                          "resource_valid": False, "failure": str(exc),
                          "completed_query_ids": [], "completed_query_count": 0,
                          "failed_query_ids": [], "failed_query_count": 0,
                          "wall_seconds": None, "queries_per_second": None,
                          "raw_attempts_consumed": 0,
                          "raw_attempts_per_completed_query": None,
                          "selected_resolution_histogram": {},
                          "per_query_task_wall_seconds": {},
                          "peak_worker_rss_bytes": None,
                          "coordinator_peak_rss_bytes":
                              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                          "filesystem_publish_failures": 0}
                # A higher resource stage is unavailable: preserve all unstarted
                # pilot IDs for the best healthy lower stage, without duplication.
                unstarted = [qid for later in stages[stage_index:]
                             for qid in later.query_ids]
                remainder = tuple(unstarted) + tuple(remainder)
            stage_records.append(record)
            serial.write_new(out / ("STAGE_" + str(stage.workers) + ".json"), record)
            if record.get("resource_valid") is False:
                for later in stages[stage_index + 1:]:
                    skipped = {"schema": "BASS_R4G_USEFUL_STAGE_V1",
                               "workers": later.workers, "query_ids": list(later.query_ids),
                               "cpus": [int(x) for x in args.cpus.split(",")][:later.workers],
                               "resource_census": {"not_started": True},
                               "resource_valid": False,
                               "failure": "NOT_STARTED_AFTER_LOWER_STAGE_RESOURCE_REJECTION",
                               "completed_query_ids": [], "completed_query_count": 0,
                               "failed_query_ids": [], "failed_query_count": 0,
                               "wall_seconds": None, "queries_per_second": None,
                               "raw_attempts_consumed": 0,
                               "raw_attempts_per_completed_query": None,
                               "selected_resolution_histogram": {},
                               "per_query_task_wall_seconds": {},
                               "peak_worker_rss_bytes": None,
                               "coordinator_peak_rss_bytes": None,
                               "filesystem_publish_failures": 0}
                    stage_records.append(skipped)
                    serial.write_new(out / ("STAGE_" + str(later.workers) + ".json"), skipped)
                break
            observations.append(StageObservation(stage.workers, len(record["completed_query_ids"]),
                                                 record["wall_seconds"], 0,
                                                 record["peak_worker_rss_bytes"], True))
        selected = fastest_healthy_stage(observations)
        summary = summarize_scaling(observations)
        serial.write_new(out / "ADAPTIVE_SELECTION.json",
                         {"stage_records": stage_records, "scaling": summary,
                          "selected_workers": selected,
                          "remaining_query_count": len(remainder)})
        # Selection is durable and linked to the initial admission, not a silent scope change.
        serial.write_new(out / "SELECTED_STAGE_RECEIPT.json",
                         {"authorization_id": args.authorization_id,
                          "admission_sha256": serial.sha256_path(out / "EXECUTION_ADMISSION.json"),
                          "selected_stage": selected})
        serial.write_new(out / "EXECUTION_ADMISSION_SELECTED.json",
                         {**admission, "selected_stage": selected,
                          "base_admission_sha256": serial.sha256_path(out / "EXECUTION_ADMISSION.json"),
                          "selection_receipt_sha256": serial.sha256_path(out / "SELECTED_STAGE_RECEIPT.json")})
        if remainder:
            fill = _run_stage([by_id[qid] for qid in remainder],
                              source=source, args=args, contract=contract,
                              budget=budget, out=out, canonical=canonical, workers=selected)
            serial.write_new(out / "FILL_STAGE.json", fill)
        for q in required:
            validate_pair(canonical, q, CONTEXT_ID, contract)
        if len(list(canonical.glob("*.json"))) != UNION_COUNT:
            raise ValueError("canonical union coverage mismatch")
        serial.write_new(out / "CACHE_COVERAGE_AUDIT.json",
                         {"required": REQUIRED_COUNT, "verified": REQUIRED_COUNT,
                          "inherited_exact_hits": 2, "new_unique_query_times": MISSING_COUNT,
                          "union_pairs": UNION_COUNT, "global_raw_attempts_used": budget.used()})
        with np.load(source / "REFERENCE_STATES.npz", allow_pickle=False) as f:
            reference_final = np.array(f["final_state"])
        previous = prior["previous_candidate"]
        provider = CacheOnlyProvider(canonical, CONTEXT_ID, contract["screens"],
                                     {q.query_id for q in required})
        current = run_candidate(provider, previous.initial_state, t0, tf, 1536)
        if provider.reads != REQUIRED_COUNT or provider.native_calls != 0:
            raise ValueError("cache-only replay native call/read mismatch")
        sf = provider.at(tf).S
        pair = assess_temporal_pair(previous, current, reference_final, sf,
                                    phase_aligned_metric_distance, contract["screens"])
        # Persist expensive state and metrics before classifying the temporal gate.
        np.savez_compressed(out / "CANDIDATE_N1536.npz",
                            initial_state=current.initial_state, final_state=current.final_state,
                            norm_history=current.norm_history)
        serial.write_new(out / "CANDIDATE_N1536.json",
                         {"nstep": 1536, "dt": float(current.dt),
                          "max_norm_drift": float(current.max_norm_drift),
                          "max_generator_defect": float(current.max_generator_defect)})
        serial.write_new(out / "TEMPORAL_PAIR_N768_N1536.json", pair)
        serial.write_new(out / "CACHE_ONLY_REPLAY_AUDIT.json",
                         {"required_query_count": REQUIRED_COUNT, "cache_reads": provider.reads,
                          "native_operator_calls": provider.native_calls,
                          "original_initial_state_used": True})
        rr = serial.strict_json(source / "REFERENCE_RECEIPT.json")
        reference_norm_pass = float(rr["max_norm_drift"]) <= float(contract["screens"]["reference_norm_drift_max"])
        dprevious = phase_aligned_metric_distance(previous.final_state, reference_final, sf)
        dref = pair["candidate_reference_metric_distance"]
        dself = pair["candidate_refinement_metric_distance"]
        triangle_ok = (math.isclose(dprevious, D768_REFERENCE_DISTANCE, rel_tol=0, abs_tol=1e-12)
                       and dprevious <= dref + dself + 1e-12
                       and dref <= dprevious + dself + 1e-12
                       and dself <= dprevious + dref + 1e-12)
        if not triangle_ok:
            raise ValueError("METRIC_OR_EVIDENCE_INCONSISTENCY")
        gate = bool(pair["qualified"] and reference_norm_pass)
        status = ("N1536_TEMPORAL_GATE_CLOSED" if gate
                  else "N1536_TEMPORAL_GATE_UNRESOLVED")
        serial.write_new(out / "TEMPORAL_GATE.json",
                         {"status": status, "previous_reference_distance": dprevious,
                          "triangle_consistent": triangle_ok, "pair": pair,
                          "reference_norm_pass": reference_norm_pass,
                          "all_required_operators_qualified": True})
        return {"status": status, "selected_workers": selected,
                "pair": pair, "reference_norm_pass": reference_norm_pass,
                "cache_only_replay_native_calls": provider.native_calls,
                "global_raw_attempts_used": budget.used(),
                "temporal_gate_qualified": gate}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("out", "predecessor-archive", "expected-predecessor-sha256",
                 "source-pins", "expected-source-pins-sha256",
                 "expected-query-plan-sha256", "expected-useful-pilot-plan-sha256",
                 "authorization-id", "expected-commit", "expected-tree",
                 "analytic-build", "stages", "cpus", "cost-scope"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--deadline-unix", type=float, required=True)
    p.add_argument("--max-wall-seconds", type=int, required=True)
    p.add_argument("--hard-max-workers", type=int, required=True)
    p.add_argument("--worker-ram-bytes", type=int, required=True)
    p.add_argument("--total-worker-ram-cap-bytes", type=int, required=True)
    p.add_argument("--global-raw-attempt-cap", type=int, required=True)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out = Path(args.out).resolve()
    if out.exists() or out.with_name(out.name + "_RETURN.zip").exists():
        print("OUTPUT_EXISTS", file=sys.stderr)
        return 3
    admission = admission_scope(args)
    if (Path.home() / ".local/state/bass_r4g/authorizations" /
        (args.authorization_id + ".json")).exists():
        raise PermissionError("N1536 authorization ID already consumed")
    out.mkdir(parents=True)
    serial.write_new(out / "EXECUTION_ADMISSION.json", admission)
    signal.signal(signal.SIGTERM, _signal)
    start = time.monotonic()
    code = 0
    report = {"schema": "BASS_R4G_N1536_RETURN_V1",
              "status": "IN_PROGRESS", **serial.CLAIM_CEILING,
              "capture_run_performed": False, "b_grid_run_performed": False,
              "full_window_transport_qualified": False,
              "execution_head": admission["execution_commit"],
              "execution_tree": admission["execution_tree"]}
    try:
        report.update(_science(args, out, admission))
    except BaseException as exc:
        code = 2
        report["status"] = ("METRIC_OR_EVIDENCE_INCONSISTENCY"
                            if str(exc) == "METRIC_OR_EVIDENCE_INCONSISTENCY"
                            else "N1536_EXECUTION_BLOCKED")
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        with (out / "failure.traceback.txt").open("x") as f:
            f.write(traceback.format_exc())
    report["wall_seconds"] = time.monotonic() - start
    serial.write_new(out / "RETURN_REPORT.json", report)
    print(json.dumps({"status": report["status"], "report": str(out / "RETURN_REPORT.json"),
                      "exit_code": code}, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
