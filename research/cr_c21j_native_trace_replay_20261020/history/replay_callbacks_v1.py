#!/usr/bin/env python3
"""Replay frozen C21H/I callbacks against recorded native replies and RPCs.

This program never launches a native/bridge process or integrates an ODE.
The original reference's solve_ivp binding consumes the saved accepted states;
only its RHS closures, callbacks, event bookkeeping, and endpoint reconstruction
are evaluated. Exact-cache admission here applies to an immutable reply table,
not to a running native provider. No replay timing is a native speed benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys
import traceback
from types import SimpleNamespace

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
SOURCE_COMMIT = "fe6bbaec2de5032b938aed0713623b9618ba70e6"
RETURN_COMMIT = "d3eaf596e46be4f994723fb742237a7399c290ed"
I_REL = "research/cr_c21i_callback_optimization_20261020"
H_REL = "research/cr_c21h_vigilode_bridge_20261019"
G_REL = "research/cr_c21g_reference_refinement_20261019"
F_REL = "research/cr_c21e_event_native_20261018"
PHYSICAL_FIELDS = (
    "gas", "photons", "temperature_K", "photon_number", "photon_energy_eV_H",
    "number_defect_H", "energy_defect_eV_H", "species_defect", "ledgers",
    "optical_depth", "log_survivor", "underflowed_positive_cohorts",
    "min_internal_optical_depth", "min_accepted_optical_depth",
)


class ReplayError(RuntimeError):
    pass


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def nonfinite(value):
        raise ReplayError("NONFINITE_JSON " + value)
    return json.loads(Path(path).read_text(), parse_constant=nonfinite)


def bits(value):
    """Shape and binary64 bytes; signed zero is significant."""
    array = np.asarray(value, dtype="<f8")
    if not np.isfinite(array).all():
        raise ReplayError("NONFINITE_REPLAY_VALUE")
    return array.shape, array.tobytes(order="C")


def equal_structure(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equal_structure(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equal_structure(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return struct.pack("<d", float(a)) == struct.pack("<d", float(b))
    return type(a) is type(b) and a == b


def verify_record(path, expected):
    path = Path(path)
    actual = {"bytes": path.stat().st_size, "sha256": digest(path)}
    if actual != expected:
        raise ReplayError("INPUT_IDENTITY_MISMATCH " + str(path))
    return actual


def verify_inputs(repo, return_root, pins):
    verified = []
    for relative, expected in pins["source_files"].items():
        verify_record(repo / relative, expected)
        verified.append("source:" + relative)
    for relative, expected in pins["return_files"].items():
        verify_record(return_root / relative, expected)
        verified.append("return:" + relative)
    return verified


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ReplyTable:
    """Only exact ASCII EVAL strings present in this particular job may resolve."""

    def __init__(self, rows):
        self.replies = {}
        self.queries = []
        self.row_count = 0
        for row in rows:
            request, response = row.get("request"), row.get("response")
            if not isinstance(request, str) or not request.startswith("EVAL\t"):
                raise ReplayError("INVALID_RECORDED_REQUEST")
            if not isinstance(response, str) or not response.startswith("OK\t"):
                raise ReplayError("ONLY_SUCCESSFUL_NATIVE_REPLIES_ALLOWED")
            if request in self.replies and self.replies[request] != response:
                raise ReplayError("INCONSISTENT_EXACT_NATIVE_REPLY")
            self.replies[request] = response
            self.row_count += 1

    def resolve(self, request):
        if request not in self.replies:
            raise ReplayError("RECORDED_NATIVE_POINT_MISSING " + hashlib.sha256(request.encode()).hexdigest())
        self.queries.append(request)
        return self.replies[request]


def make_recorded_provider(native_module, table):
    """Reuse the pinned response parser and checks without its process constructor."""
    class RecordedProvider:
        kind = "RECORDED_NATIVE_REPLY_TABLE_NO_NATIVE_EXECUTION"
        # Calls below are table queries. They must never be reported as new native calls.
        __call__ = native_module.NativeMicro.__call__

        def __init__(self):
            self.closed = False
            self.calls = 0
            self.max_calls = 200000
            self.log = io.StringIO()
            self.pending = None
            self.process = SimpleNamespace(stdin=SimpleNamespace(write=self.write, flush=lambda: None))

        def write(self, value):
            if self.pending is not None or not value.endswith(b"\n"):
                raise ReplayError("REPLAY_REQUEST_SEQUENCE")
            self.pending = value[:-1].decode("ascii")

        def _line(self):
            if self.pending is None:
                raise ReplayError("REPLAY_REPLY_WITHOUT_REQUEST")
            request, self.pending = self.pending, None
            return table.resolve(request)

        def close(self):
            self.closed = True

    return RecordedProvider()


def rpc_pairs(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    pairs, pending, expected_id = [], None, 1
    for row in rows:
        message = row["message"]
        if row["direction"] == "rust_to_python" and message.get("type") == "request":
            if pending is not None or message.get("id") != expected_id:
                raise ReplayError("SAVED_RPC_REQUEST_SEQUENCE")
            if message.get("op") not in ("rhs", "jacobian", "partial_t"):
                raise ReplayError("SAVED_RPC_OPERATION")
            pending = message
        elif row["direction"] == "python_to_rust" and "id" in message:
            if pending is None or message.get("id") != expected_id or message.get("ok") is not True:
                raise ReplayError("SAVED_RPC_RESPONSE_SEQUENCE")
            pairs.append((pending, message["value"]))
            pending = None
            expected_id += 1
    if pending is not None or not pairs:
        raise ReplayError("SAVED_RPC_INCOMPLETE")
    return pairs


def replay_one(repo, job, mode):
    original = read_json(job / "result.json")
    receipt = read_json(job / "JOB_RECEIPT.json")
    if receipt.get("execution") != "COMPLETE" or receipt.get("native_executed") is not True:
        raise ReplayError("MATCHING_COMPLETED_NATIVE_JOB_REQUIRED")
    optimizer = load_module(repo / I_REL / "optimized_adapter.py", "_c21j_optimizer_" + mode)
    base = optimizer.load_frozen_adapter(repo / H_REL)
    optimizer.source_snapshot(repo / F_REL, repo / G_REL)
    vendor = str(repo / F_REL / "vendor/pr79")
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    reference = base.private_reference(repo / F_REL)
    from run_experiment import Fixture
    import native_micro
    fixture = Fixture(**read_json(job / "fixture.json")).validate()
    if fixture.digest != original["fixture_sha256"] or fixture.digest != receipt["fixture_sha256"]:
        raise ReplayError("FIXTURE_CANONICAL_IDENTITY")
    controls = original["tolerance_contract"]
    dynamic = np.asarray(controls["dynamic_indices"], dtype=int)
    scales = np.asarray(controls["fixed_diagonal_scaling"]["values"], float)[dynamic]
    native_rows = [json.loads(line) for line in (job / "native/native_points.jsonl").read_text().splitlines()]
    table = ReplyTable(native_rows)
    provider = make_recorded_provider(native_micro, table)
    admission = {
        "schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
        "deterministic_successful_rhs": True,
        "provider_identity": {"native_points_sha256": digest(job / "native/native_points.jsonl")},
        "provider_kind": provider.kind,
        "admitted_by": "Immutable exact ASCII reply table; duplicate requests checked for identical replies",
    }
    callback_type = base.CellCallbacks if mode == "original_H" else optimizer.make_callback_type(
        base, mode, cache_contract=admission if mode == "vectorized_exact" else None)
    segments = sorted((job / "segments").glob("segment_*"))
    index = 0
    records = []

    def consume_saved_segment(fun, t_span, y0, *, method, rtol, atol, max_step, **kwargs):
        nonlocal index
        if kwargs or method != "Radau" or index >= len(segments):
            raise ReplayError("REPLAY_REFERENCE_CALL_CONTRACT")
        directory = segments[index]
        config = read_json(directory / "config.json")
        if bits(t_span) != bits([config["t0"], config["t1"]]):
            raise ReplayError("REPLAY_EVENT_CELL_IDENTITY")
        if bits(np.asarray(y0) / scales) != bits(config["y0"]):
            raise ReplayError("REPLAY_SCALED_INITIAL_IDENTITY")
        if bits(atol) != bits(config["atol"] * scales):
            raise ReplayError("REPLAY_TOLERANCE_IDENTITY")
        if bits([rtol, max_step]) != bits([config["rtol"], config["h_max"]]):
            raise ReplayError("REPLAY_METHOD_CONTROLS")
        cb = callback_type(fun, fixture, *t_span, scales, dynamic, reference,
                           controls["gas_fd_relative"], controls["time_fd_fraction"])
        pairs = rpc_pairs(directory / "rpc.jsonl")
        values, output_hash = 0, hashlib.sha256()
        queries_before = len(table.queries)
        for request, expected in pairs:
            actual = getattr(cb, request["op"])(request["t"], request["y"])
            if bits(actual) != bits(expected):
                a, e = np.asarray(actual), np.asarray(expected)
                raise ReplayError("CALLBACK_REPLY_MISMATCH " + json.dumps({
                    "segment": index, "id": request["id"], "op": request["op"],
                    "shape_actual": list(a.shape), "shape_expected": list(e.shape),
                    "max_abs_difference": float(np.max(np.abs(a-e))) if a.shape == e.shape else None}))
            values += np.asarray(actual).size
            output_hash.update(bits(actual)[1])
        if not equal_structure(cb.fd_nodes, read_json(directory / "derivative_nodes.json")):
            raise ReplayError("REPLAY_DERIVATIVE_NODE_IDENTITY")
        raw = read_json(directory / "result.json")
        times, states = np.asarray(raw["accepted_times"]), np.asarray(raw["accepted_states"])
        if not raw["accepted_grid_complete"] or len(times) != raw["internal_steps"] + 1:
            raise ReplayError("SAVED_ACCEPTED_TRACE_INCOMPLETE")
        records.append({"segment": index, "rpc_replies": len(pairs), "binary64_values": values,
                        "reply_values_sha256": output_hash.hexdigest(), "callbacks": dict(cb.counts),
                        "recorded_provider_queries": len(table.queries)-queries_before,
                        "new_native_calls": 0, "new_IVP_solves": 0})
        index += 1
        return SimpleNamespace(t=times, y=(states*scales[None, :]).T, success=True, status=0,
                               message="SAVED_ACCEPTED_STATES_REPLAY_NO_IVP_SOLVE",
                               nfev=cb.counts["rhs_requests"], njev=cb.counts["jacobian_requests"],
                               nlu=raw["counters"]["direct_factorizations"])

    reference.solve_ivp = consume_saved_segment
    replayed = reference.run_reference_tau(fixture, provider, rtol=controls["rtol"],
        atol=controls["atol"], max_step_divisor=controls["max_step_divisor"], max_evaluations=200000)
    if index != len(segments):
        raise ReplayError("UNCONSUMED_SAVED_SEGMENTS")
    same = {key: equal_structure(replayed[key], original[key]) for key in PHYSICAL_FIELDS}
    if not all(same.values()):
        raise ReplayError("REPLAY_PHYSICAL_SUMMARY_MISMATCH " + str([k for k,v in same.items() if not v]))
    return {"job": job.name, "mode": mode, "status": "PASS_SCOPED",
            "fixture_sha256": fixture.digest, "segments": records,
            "recorded_native_rows": table.row_count, "unique_recorded_native_requests": len(table.replies),
            "recorded_provider_queries": provider.calls,
            "physical_fields_bitwise_equal": same,
            "new_native_calls": 0, "new_IVP_solves": 0,
            "native_process_admission_verified_by_replay": False,
            "global_error_bound": None}


def run(args):
    repo, return_root = args.repo.resolve(), args.native_return.resolve()
    pins = read_json(args.input_pins)
    before = verify_inputs(repo, return_root, pins)
    args.out.mkdir(parents=True, exist_ok=False)
    report = {"schema": "C21J_CALLBACK_REPLAY_V1", "source_commit": SOURCE_COMMIT,
              "return_commit": RETURN_COMMIT, "status": "RUNNING", "cases": [],
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "new_native_calls": 0, "new_IVP_solves": 0, "global_error_bound": None,
              "meaning": "Original callbacks on saved RPC points with an immutable native reply table; saved accepted states are consumed, never integrated."}
    original_popen, original_solve = subprocess.Popen, scipy.integrate.solve_ivp

    def forbidden(*_args, **_kwargs):
        raise ReplayError("FORBIDDEN_NEW_PROCESS_OR_IVP_SOLVE")

    subprocess.Popen = forbidden
    scipy.integrate.solve_ivp = forbidden
    try:
        for job_name, mode in [
            ("I_common_ic_vigilode_vectorized_base", "original_H"),
            ("I_common_ic_vigilode_vectorized_base", "vectorized"),
            ("I_common_ic_vigilode_vectorized_base", "vectorized_exact"),
            ("I_common_ic_vigilode_vectorized_fd_half", "vectorized_exact"),
        ]:
            report["cases"].append(replay_one(repo, return_root / "evidence" / job_name, mode))
        report["input_files_unchanged"] = before == verify_inputs(repo, return_root, pins)
        report["status"] = "PASS_SCOPED"
    except Exception as error:
        report.update(status="FAILED", error_class=type(error).__name__, error=str(error))
        (args.out / "failure.txt").write_text(traceback.format_exc())
    finally:
        subprocess.Popen, scipy.integrate.solve_ivp = original_popen, original_solve
        (args.out / "REPLAY_REPORT.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return 0 if report["status"] == "PASS_SCOPED" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--native-return", type=Path, required=True)
    parser.add_argument("--input-pins", type=Path, default=HERE / "INPUT_PINS.json")
    parser.add_argument("--out", type=Path, required=True)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
