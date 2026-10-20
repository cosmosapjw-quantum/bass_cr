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
INPUT_PINS_SHA256 = "ac339fc832ccc2e4b177034151a6adcf1510d82646b0c7e04d68bfc2be7aea90"
INPUT_PINS_CANONICAL_SHA256 = "5c741dcaf415961d09bb4f1bf10c9dad600c0af3d0791e18750655b006957fea"
NATIVE_ARCHIVE_SHA256 = "2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3"
HELLO = {"diffsol_version": "0.17.1", "methods": ["vigilode-rodas5p", "diffsol-bdf"],
         "protocol": "C21H_V1", "type": "hello",
         "vigilode_commit": "8a8bd409b1d96c7b7421f496d229e119fd3d284e"}
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


def parse_json(text):
    def nonfinite(value):
        raise ReplayError("NONFINITE_JSON " + value)
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ReplayError("DUPLICATE_JSON_KEY " + key)
            result[key] = value
        return result
    return json.loads(text, parse_constant=nonfinite, object_pairs_hook=unique_object)


def read_json(path):
    return parse_json(Path(path).read_text())


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
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
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
    # The two maps are not a user-supplied declaration of which inputs to trust.
    # Their canonical digest binds every required filename, size and hash to this
    # reviewed frozen dataset, including the exact 24-source/60-return file set.
    if (pins.get("schema") != "C21J_PINNED_TRACE_INPUTS_V1"
            or pins.get("source_content") != SOURCE_COMMIT
            or pins.get("native_return_head") != RETURN_COMMIT
            or pins.get("native_archive_sha256") != NATIVE_ARCHIVE_SHA256
            or pins.get("private_inventory_included") is not False):
        raise ReplayError("INPUT_PIN_METADATA_IDENTITY")
    encoded = json.dumps(pins, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode()
    if hashlib.sha256(encoded).hexdigest() != INPUT_PINS_CANONICAL_SHA256:
        raise ReplayError("INPUT_PIN_AUTHORITY_IDENTITY")
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


def rpc_pairs(path, expected_config=None, expected_result=None):
    path = Path(path)
    rows = [parse_json(line) for line in path.read_text().splitlines()]
    if len(rows) < 5:
        raise ReplayError("SAVED_RPC_INCOMPLETE")
    if not equal_structure(rows[0], {"direction": "rust_to_python", "message": HELLO}):
        raise ReplayError("SAVED_RPC_HELLO_IDENTITY")
    if expected_config is None:
        expected_config = read_json(path.with_name("config.json"))
    if expected_result is None:
        expected_result = read_json(path.with_name("result.json"))
    if not equal_structure(rows[1], {"direction": "python_to_rust", "message": expected_config}):
        raise ReplayError("SAVED_RPC_CONFIG_IDENTITY")
    terminal = rows[-1]
    message = terminal.get("message", {})
    if (terminal.get("direction") != "rust_to_python"
            or message.get("type") != "result"
            or message.get("protocol") != HELLO["protocol"]
            or message.get("vigilode_commit") != HELLO["vigilode_commit"]
            or message.get("ok") is not True or message.get("success") is not True
            or message.get("complete_output") is not True
            or message.get("accepted_grid_complete") is not True
            or message.get("callback_failure") is not None
            or message.get("pending_request") is not None):
        raise ReplayError("SAVED_RPC_SUCCESSFUL_TERMINAL_REQUIRED")
    if not equal_structure(terminal, {"direction": "rust_to_python", "message": expected_result}):
        raise ReplayError("SAVED_RPC_RESULT_IDENTITY")
    pairs, pending, expected_id = [], None, 1
    for row in rows[2:-1]:
        if set(row) != {"direction", "message"}:
            raise ReplayError("SAVED_RPC_ROW_SHAPE")
        message = row["message"]
        if row["direction"] == "rust_to_python" and message.get("type") == "request":
            if (pending is not None or type(message.get("id")) is not int
                    or message.get("id") != expected_id):
                raise ReplayError("SAVED_RPC_REQUEST_SEQUENCE")
            if (set(message) != {"type", "id", "op", "t", "y"}
                    or message.get("op") not in ("rhs", "jacobian", "partial_t")):
                raise ReplayError("SAVED_RPC_OPERATION")
            if bits(message["y"])[0] != (expected_config["dimension"],):
                raise ReplayError("SAVED_RPC_STATE_SHAPE")
            if bits(message["t"])[0] != ():
                raise ReplayError("SAVED_RPC_TIME_SHAPE")
            pending = message
        elif row["direction"] == "python_to_rust":
            if (pending is None or set(message) != {"id", "ok", "value"}
                    or type(message.get("id")) is not int
                    or message.get("id") != expected_id or message.get("ok") is not True):
                raise ReplayError("SAVED_RPC_RESPONSE_SEQUENCE")
            shape = ((expected_config["dimension"],) *
                     (2 if pending["op"] == "jacobian" else 1))
            if bits(message["value"])[0] != shape:
                raise ReplayError("SAVED_RPC_REPLY_SHAPE")
            pairs.append((pending, message["value"]))
            pending = None
            expected_id += 1
        else:
            raise ReplayError("SAVED_RPC_UNEXPECTED_MESSAGE")
    if pending is not None or not pairs:
        raise ReplayError("SAVED_RPC_INCOMPLETE")
    counters = expected_result["rpc_counters"]
    if (counters["requests_attempted"] != len(pairs)
            or counters["responses_validated"] != len(pairs)
            or any(counters[op + "_requests"] != sum(r["op"] == op for r, _ in pairs)
                   for op in ("rhs", "jacobian", "partial_t"))):
        raise ReplayError("SAVED_RPC_COUNTER_IDENTITY")
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
    native_rows = [parse_json(line) for line in (job / "native/native_points.jsonl").read_text().splitlines()]
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
        raw = read_json(directory / "result.json")
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
        pairs = rpc_pairs(directory / "rpc.jsonl", config, raw)
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
    if digest(args.input_pins) != INPUT_PINS_SHA256:
        raise ReplayError("INPUT_PIN_FILE_IDENTITY")
    pins = read_json(args.input_pins)
    before = verify_inputs(repo, return_root, pins)
    args.out.mkdir(parents=True, exist_ok=False)
    report = {"schema": "C21J_CALLBACK_REPLAY_V1", "source_commit": SOURCE_COMMIT,
              "return_commit": RETURN_COMMIT, "status": "RUNNING", "cases": [],
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "input_pins_sha256": digest(args.input_pins),
              "input_pins_canonical_sha256": INPUT_PINS_CANONICAL_SHA256,
              "source_file_count": len(pins["source_files"]),
              "return_file_count": len(pins["return_files"]),
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
