#!/usr/bin/env python3
"""One authorized A3 fill-only N1536 successor; completed A1/A2 work is immutable."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
for directory in (HERE, HERE.parent / "r4f_parallel_migration_20260929",
                  HERE.parent / "r4c_temporal_continuation"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import continue_temporal as serial
from adaptive_workers import build_useful_pilot_plan
from a1_salvage import A1_ARCHIVE_SHA256, A1_AUTH, validate_a1_partial
from a2_salvage import (A2_ARCHIVE_SHA256, A2_AUTH, A2_EVIDENCE_SHA256, LIFETIME_RAW,
                        a3_resume_receipts, validate_a2_partial)
from execution_admission import check_native_build
from parallel_bridge import CacheOnlyProvider, GlobalBudget, publish_pair, validate_pair
from qualified_provider import restore_query_store
from resource_census import live_resource_census
import run_n1536 as stage_runner
from successor import (CONTEXT_ID, D768_REFERENCE_DISTANCE, NATIVE_BUILD_SHA256,
                       NATIVE_LIBRARY_SHA256, NATIVE_SOURCE_SHA256,
                       PREDECESSOR_AUTH, PREDECESSOR_SHA256, REQUIRED_COUNT, UNION_COUNT,
                       plan_n1536, plan_receipts, required_missing, validate_predecessor)

MODE = "COOPERATIVE_SHARED_HOST"
_STOP = False


def _signal(signum, frame):
    global _STOP
    _STOP = True
    stage_runner._STOP = True
    raise InterruptedError("A3 coordinator received signal " + str(signum))


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("out", "predecessor-archive", "expected-predecessor-sha256",
                 "a1-partial-archive", "expected-a1-sha256", "a2-partial-archive",
                 "expected-a2-sha256", "source-pins", "expected-source-pins-sha256",
                 "expected-query-plan-sha256", "expected-useful-pilot-plan-sha256",
                 "expected-salvage-manifest-sha256", "expected-fill-plan-sha256",
                 "expected-selected-stage-sha256", "resource-policy",
                 "expected-resource-policy-sha256", "resource-sharing-policy",
                 "authorization-id", "prior-authorization-id", "expected-commit",
                 "expected-tree", "analytic-build", "cpus", "cost-scope"):
        p.add_argument("--" + name, required=True)
    for name in ("max-wall-seconds", "workers", "worker-ram-bytes",
                 "total-worker-ram-cap-bytes", "global-raw-attempt-cap"):
        p.add_argument("--" + name, type=int, required=True)
    p.add_argument("--deadline-unix", type=float, required=True)
    return p.parse_args(argv)


def admission_scope(args):
    if os.environ.get("ALLOW_NEW_NATIVE_R4M") != "YES_I_AUTHORIZE_A3_FILL_ONLY":
        raise PermissionError("A3_NATIVE_NOT_AUTHORIZED")
    head, tree = serial.git_identity()
    if (head != args.expected_commit or tree != args.expected_tree
        or subprocess.check_output(["git", "-C", str(serial.REPO), "status", "--porcelain",
                                    "--untracked-files=all"], text=True)):
        raise ValueError("A3 exact clean execution commit/tree required")
    if Path(args.out).resolve().is_relative_to(serial.REPO):
        raise ValueError("A3 output must be outside source tree")
    import scipy
    if (not sys.flags.isolated or sys.version_info < (3, 11)
        or np.__version__ != "2.3.5" or scipy.__version__ != "1.17.0"):
        raise ValueError("A3 pinned isolated Python/numerical environment required")
    if any(os.environ.get(k) != "1" for k in
           ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")):
        raise ValueError("A3 single numerical thread per worker required")
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{15,95}", args.authorization_id)
        or args.authorization_id in (PREDECESSOR_AUTH, A1_AUTH, A2_AUTH)
        or args.prior_authorization_id != A2_AUTH):
        raise ValueError("A3 fresh authorization/A2 lineage required")
    nonce = Path.home() / ".local/state/bass_r4m/authorizations" / (args.authorization_id + ".json")
    if nonce.exists():
        raise PermissionError("A3 authorization ID already consumed")
    old_nonce = Path.home() / ".local/state/bass_r4g/authorizations" / (A2_AUTH + ".json")
    if (not old_nonce.is_file() or serial.sha256_path(old_nonce) !=
        A2_EVIDENCE_SHA256["AUTHORIZATION_CONSUMED.json"]):
        raise ValueError("A2 consumed authorization nonce identity mismatch")
    if (args.expected_predecessor_sha256 != PREDECESSOR_SHA256
        or args.expected_a1_sha256 != A1_ARCHIVE_SHA256
        or args.expected_a2_sha256 != A2_ARCHIVE_SHA256):
        raise ValueError("A3 predecessor/A1/A2 archive pin mismatch")
    if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in
           (args.expected_source_pins_sha256, args.expected_query_plan_sha256,
            args.expected_useful_pilot_plan_sha256,
            args.expected_salvage_manifest_sha256, args.expected_fill_plan_sha256,
            args.expected_selected_stage_sha256, args.expected_resource_policy_sha256)):
        raise ValueError("A3 authority SHA256 format invalid")
    policy_path = Path(args.resource_policy)
    policy = serial.strict_json(policy_path)
    if (args.resource_sharing_policy != MODE or policy.get("effective_mode") != MODE
        or serial.sha256_path(policy_path) != args.expected_resource_policy_sha256
        or policy.get("external_affinity_overlap") != "TELEMETRY_ONLY"
        or policy.get("own_pool_teardown") != "HARD_BLOCK"):
        raise ValueError("A3 cooperative sharing policy identity mismatch")
    cpus = [int(x) for x in args.cpus.split(",")]
    if (len(cpus) != 32 or len(set(cpus)) != 32 or args.workers != 32
        or args.worker_ram_bytes != 1 << 30
        or args.total_worker_ram_cap_bytes != 32 << 30
        or args.global_raw_attempt_cap != 16896):
        raise ValueError("A3 worker/CPU/RAM/raw scope mismatch")
    now = time.time()
    if (not math.isfinite(args.deadline_unix) or now >= args.deadline_unix
        or args.max_wall_seconds < 1
        or args.deadline_unix > now + args.max_wall_seconds + 1
        or not args.cost_scope.strip()):
        raise ValueError("A3 explicit live wall/deadline/cost scope required")
    census_path = Path(args.out).resolve().with_name(Path(args.out).name + "_INITIAL_RESOURCE_CENSUS.json")
    census = live_resource_census(cpus, 32, args.worker_ram_bytes,
        receipt_path=census_path, sharing_policy=MODE)
    return {"schema": "BASS_R4M_A3_ADMISSION_V1", "execution_commit": head,
            "execution_tree": tree, "authorization_id": args.authorization_id,
            "predecessor_authorization_id": PREDECESSOR_AUTH,
            "a1_authorization_id": A1_AUTH, "prior_authorization_id": A2_AUTH,
            "predecessor_archive_sha256": PREDECESSOR_SHA256,
            "a1_partial_archive_sha256": A1_ARCHIVE_SHA256,
            "a2_partial_archive_sha256": A2_ARCHIVE_SHA256,
            "source_pins_sha256": args.expected_source_pins_sha256,
            "query_plan_sha256": args.expected_query_plan_sha256,
            "useful_pilot_plan_sha256": args.expected_useful_pilot_plan_sha256,
            "salvage_manifest_sha256": args.expected_salvage_manifest_sha256,
            "fill_plan_sha256": args.expected_fill_plan_sha256,
            "selected_stage_sha256": args.expected_selected_stage_sha256,
            "resource_policy_sha256": args.expected_resource_policy_sha256,
            "resource_sharing_policy": MODE, "workers": 32, "cpus": cpus,
            "worker_ram_bytes": args.worker_ram_bytes,
            "total_worker_ram_cap_bytes": args.total_worker_ram_cap_bytes,
            "prior_raw_attempts": LIFETIME_RAW,
            "global_raw_attempt_cap": args.global_raw_attempt_cap,
            "deadline_unix": args.deadline_unix, "max_wall_seconds": args.max_wall_seconds,
            "cost_scope": args.cost_scope, "native_parity": "NONE",
            "pilot_reexecution": False, "initial_resource_census": census}


def _science(args, out: Path, admission: dict):
    from cr_repro.observables import projectile_speed_au
    from metric_transport import phase_aligned_metric_distance, run_candidate
    from transport_policy import assess_temporal_pair

    with tempfile.TemporaryDirectory(prefix="bass_r4m_a3_") as tmp:
        tmp = Path(tmp)
        source, a1, a2 = tmp / "predecessor", tmp / "a1", tmp / "a2"
        prior = validate_predecessor(Path(args.predecessor_archive),
                                     args.expected_predecessor_sha256, source)
        contract = prior["contract"]
        deps = serial.verify_pinned_dependencies()
        native = check_native_build(Path(args.analytic_build), contract,
                                    serial.ANALYTIC / "moment_kernel.cpp")
        if (native["source_sha256"] != NATIVE_SOURCE_SHA256
            or native["library_sha256"] != NATIVE_LIBRARY_SHA256
            or native["build_receipt_sha256"] != NATIVE_BUILD_SHA256):
            raise ValueError("A3 frozen native identity mismatch")
        pins_path = Path(args.source_pins)
        if serial.sha256_path(pins_path) != args.expected_source_pins_sha256:
            raise ValueError("A3 source pins SHA256 mismatch")
        pins = serial.strict_json(pins_path)
        expected_pin_fields = {
            "execution_commit": admission["execution_commit"],
            "execution_tree": admission["execution_tree"],
            "predecessor_archive_sha256": PREDECESSOR_SHA256,
            "a1_archive_sha256": A1_ARCHIVE_SHA256,
            "a2_archive_sha256": A2_ARCHIVE_SHA256,
            "a2_evidence_sha256": A2_EVIDENCE_SHA256,
            "a2_consumed_nonce_sha256":
                A2_EVIDENCE_SHA256["AUTHORIZATION_CONSUMED.json"],
            "context_id": CONTEXT_ID, "native": native,
            "resource_sharing_policy": MODE,
            "resource_policy_sha256": args.expected_resource_policy_sha256,
            "query_plan_sha256": args.expected_query_plan_sha256,
            "useful_pilot_plan_sha256": args.expected_useful_pilot_plan_sha256,
            "salvage_manifest_sha256": args.expected_salvage_manifest_sha256,
            "fill_plan_sha256": args.expected_fill_plan_sha256,
            "selected_stage_sha256": args.expected_selected_stage_sha256,
            "pinned_dependency_manifest_sha256":
                serial.sha256_path(serial.HERE / "PINNED_DEPENDENCIES.json")}
        if any(pins.get(k) != v for k, v in expected_pin_fields.items()):
            raise ValueError("A3 source pins content mismatch")
        serial.write_new(out / "PINNED_NUMERICAL_DEPENDENCIES.json", deps)
        serial.write_new(out / "NATIVE_PRELOAD_CHECK.json", native)
        serial.copy_new(pins_path, out / "SOURCE_PINS.json")
        serial.copy_new(Path(args.resource_policy), out / "RESOURCE_SHARING_POLICY.json")
        v = projectile_speed_au(contract["energy_keV_per_u"])
        t0, tf = contract["z_initial_a0"] / v, contract["z_final_a0"] / v
        required = plan_n1536(CONTEXT_ID, t0, tf)
        present = {p.stem for p in (source / "runtime_queries").glob("*.json")}
        missing = required_missing(required, present)
        stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
        plan, pilot = plan_receipts(required, missing, stages, remainder,
                                    admission["execution_commit"], admission["execution_tree"])
        serial.write_new(out / "PROPOSED_N1536_QUERY_PLAN.json", plan)
        serial.write_new(out / "USEFUL_PILOT_PLAN.json", pilot)
        if (serial.sha256_path(out / "PROPOSED_N1536_QUERY_PLAN.json") != args.expected_query_plan_sha256
            or serial.sha256_path(out / "USEFUL_PILOT_PLAN.json") != args.expected_useful_pilot_plan_sha256):
            raise ValueError("A3 frozen query/pilot plan mismatch")
        a1_manifest = validate_a1_partial(Path(args.a1_partial_archive),
            args.expected_a1_sha256, a1, source, contract, required, pilot, CONTEXT_ID)
        salvage = validate_a2_partial(Path(args.a2_partial_archive),
            args.expected_a2_sha256, a2, source, a1, contract, required, pilot, CONTEXT_ID)
        fill_plan, selected = a3_resume_receipts(required, missing, pilot, salvage,
            admission["execution_commit"], admission["execution_tree"])
        for name, value, expected in (
            ("A2_CUMULATIVE_SALVAGE_MANIFEST.json", salvage, args.expected_salvage_manifest_sha256),
            ("N1536_REMAINING_FILL_PLAN.json", fill_plan, args.expected_fill_plan_sha256),
            ("A2_SELECTED_STAGE_EVIDENCE.json", selected, args.expected_selected_stage_sha256)):
            serial.write_new(out / name, value)
            if serial.sha256_path(out / name) != expected:
                raise ValueError("A3 salvage/fill/selection pin mismatch: " + name)
        if restore_query_store(source, out, CONTEXT_ID) != 2047:
            raise ValueError("A3 predecessor cache restore count mismatch")
        canonical = out / "runtime_queries"
        by_id = {q.query_id: q for q in missing}
        imported = [publish_pair(a2 / "runtime_queries", canonical, by_id[qid],
                                 CONTEXT_ID, contract) for qid in salvage["imported_ids"]]
        if (len(imported) != 112 or len(list(canonical.glob("*.json"))) != 2159
            or len(list(canonical.glob("*.npz"))) != 2159):
            raise ValueError("A3 byte-preserving A2 import mismatch")
        serial.write_new(out / "A2_IMPORT_RECEIPT.json",
            {"schema": "BASS_R4M_A2_IMPORT_V1", "a2_archive_sha256": A2_ARCHIVE_SHA256,
             "salvage_manifest_sha256": args.expected_salvage_manifest_sha256,
             "imported_pairs": 112, "canonical_pairs_after_import": 2159,
             "new_native_calls": 0, "records": imported})
        for name in ("STAGE_8.json", "STAGE_16.json", "STAGE_32.json", "ADAPTIVE_SELECTION.json"):
            serial.copy_new(a2 / name, out / name)
        for name in ("BASIS.json", "BASIS.npz", "SCIENCE_CONTEXT.json",
                     "REFERENCE_STATES.npz", "REFERENCE_RECEIPT.json",
                     "METRIC_CONNECTION.json", "CANDIDATE_N768.json", "CANDIDATE_N768.npz"):
            serial.copy_new(source / name, out / name)
        serial.write_new(out / "PREDECESSOR_ADMISSION.json",
            {k: v for k, v in prior.items() if k not in ("previous_candidate", "contract")})
        serial.write_new(out / "A1_SALVAGE_MANIFEST.json", a1_manifest)
        # A3 is consumed only after all non-native lineage checks have passed.
        if time.time() >= args.deadline_unix:
            raise TimeoutError("A3 deadline expired during non-native preflight")
        nonce_root = Path.home() / ".local/state/bass_r4m/authorizations"
        nonce_root.mkdir(parents=True, exist_ok=True)
        consumed = {**admission, "state": "CONSUMED_BEFORE_NATIVE_WORKERS",
                    "out": str(out), "created_unix_seconds": time.time()}
        serial.write_new(nonce_root / (args.authorization_id + ".json"), consumed)
        serial.write_new(out / "AUTHORIZATION_CONSUMED.json", consumed)
        budget = GlobalBudget.create(out / "global_budget", parent_attempts=LIFETIME_RAW,
                                     maximum=args.global_raw_attempt_cap,
                                     deadline_unix=args.deadline_unix)
        (out / "worker_tasks").mkdir()
        items = [by_id[qid] for qid in fill_plan["remaining_ids"]]
        fill = stage_runner._run_stage(items, source=source, args=args, contract=contract,
                          budget=budget, out=out, canonical=canonical, workers=32,
                          stage_label="A3_FILL")
        serial.write_new(out / "FILL_STAGE.json", fill)
        for q in required:
            validate_pair(canonical, q, CONTEXT_ID, contract)
        if len(list(canonical.glob("*.json"))) != UNION_COUNT:
            raise ValueError("A3 canonical union coverage mismatch")
        serial.write_new(out / "CACHE_COVERAGE_AUDIT.json",
            {"required": REQUIRED_COUNT, "verified": REQUIRED_COUNT,
             "inherited_exact_hits": 2, "new_unique_query_times": 1536,
             "union_pairs": UNION_COUNT, "lifetime_raw_attempts_used": budget.used()})
        with np.load(source / "REFERENCE_STATES.npz", allow_pickle=False) as data:
            reference_final = np.array(data["final_state"])
        previous = prior["previous_candidate"]
        provider = CacheOnlyProvider(canonical, CONTEXT_ID, contract["screens"],
                                     {q.query_id for q in required})
        current = run_candidate(provider, previous.initial_state, t0, tf, 1536)
        if provider.reads != REQUIRED_COUNT or provider.native_calls != 0:
            raise ValueError("A3 cache-only replay native call/read mismatch")
        sf = provider.at(tf).S
        pair = assess_temporal_pair(previous, current, reference_final, sf,
                                    phase_aligned_metric_distance, contract["screens"])
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
        reference_norm_pass = (float(rr["max_norm_drift"])
                               <= float(contract["screens"]["reference_norm_drift_max"]))
        dprevious = phase_aligned_metric_distance(previous.final_state, reference_final, sf)
        dref, dself = pair["candidate_reference_metric_distance"], pair["candidate_refinement_metric_distance"]
        triangle = (math.isclose(dprevious, D768_REFERENCE_DISTANCE, rel_tol=0, abs_tol=1e-12)
                    and dprevious <= dref + dself + 1e-12
                    and dref <= dprevious + dself + 1e-12
                    and dself <= dprevious + dref + 1e-12)
        if not triangle:
            raise ValueError("METRIC_OR_EVIDENCE_INCONSISTENCY")
        gate = bool(pair["qualified"] and reference_norm_pass)
        status = "N1536_TEMPORAL_GATE_CLOSED" if gate else "N1536_TEMPORAL_GATE_UNRESOLVED"
        serial.write_new(out / "TEMPORAL_GATE.json",
            {"status": status, "previous_reference_distance": dprevious,
             "triangle_consistent": triangle, "pair": pair,
             "reference_norm_pass": reference_norm_pass,
             "all_required_operators_qualified": True})
        return {"status": status, "selected_workers": 32, "pair": pair,
                "reference_norm_pass": reference_norm_pass,
                "cache_only_replay_native_calls": provider.native_calls,
                "lifetime_raw_attempts_used": budget.used(),
                "temporal_gate_qualified": gate}


def main(argv=None):
    args = parse_args(argv)
    out = Path(args.out).resolve()
    if out.exists() or out.with_name(out.name + "_RETURN.zip").exists():
        print("OUTPUT_EXISTS", file=sys.stderr)
        return 3
    admission = admission_scope(args)
    out.mkdir(parents=True)
    serial.write_new(out / "EXECUTION_ADMISSION.json", admission)
    signal.signal(signal.SIGTERM, _signal)
    start = time.monotonic()
    code = 0
    report = {"schema": "BASS_R4M_A3_RETURN_V1", "status": "IN_PROGRESS",
              **serial.CLAIM_CEILING, "capture_run_performed": False,
              "b_grid_run_performed": False, "full_window_transport_qualified": False,
              "execution_head": admission["execution_commit"],
              "execution_tree": admission["execution_tree"],
              "resource_sharing_policy": MODE}
    try:
        report.update(_science(args, out, admission))
    except BaseException as exc:
        code = 2
        report["status"] = ("METRIC_OR_EVIDENCE_INCONSISTENCY" if str(exc) ==
                            "METRIC_OR_EVIDENCE_INCONSISTENCY" else "N1536_EXECUTION_BLOCKED")
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        with (out / "failure.traceback.txt").open("x") as stream:
            stream.write(traceback.format_exc())
    report["wall_seconds"] = time.monotonic() - start
    serial.write_new(out / "RETURN_REPORT.json", report)
    print(json.dumps({"status": report["status"], "report": str(out / "RETURN_REPORT.json"),
                      "exit_code": code}, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
