#!/usr/bin/env python3
"""Light black-box checks against an actual built bridge, with raw receipts.

These manufactured IVPs test the solver bridge. They do not execute the native
chemistry provider or certify the C21G physical reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


VIGILODE = "8a8bd409b1d96c7b7421f496d229e119fd3d284e"


def config(method: str, case: str) -> dict:
    c = {"protocol": "C21H_V1", "dimension": 2, "t0": 0.0,
         "t1": 0.02, "y0": [1.0, 1.0], "rtol": 1e-7, "atol": 1e-10,
         "h0": 1e-5, "h_min": 1e-15, "h_max": 0.004,
         "max_steps": 10000, "method": method}
    if case == "nonautonomous":
        c.update(dimension=1, t0=-2.4, t1=-2.3999, y0=[0.5],
                 h0=1e-7, h_min=math.ulp(-2.4), h_max=1e-5)
    elif case == "partial":
        c["max_steps"] = 1
    elif case == "invalid_config":
        c["rtol"] = 0.0
    return c


def rhs_response(request: dict, c: dict, case: str) -> dict:
    assert request["type"] == "request"
    assert math.isfinite(request["t"]) and c["t0"] <= request["t"] <= c["t1"]
    assert len(request["y"]) == c["dimension"]
    assert all(math.isfinite(v) for v in request["y"])
    if case == "callback_failure":
        return {"id": request["id"], "ok": False, "error": "NATIVE_SENTINEL_REJECTION"}
    if case == "wrong_id":
        return {"id": request["id"] + 1, "ok": True, "value": [0.0]}
    op, t, y = request["op"], request["t"], request["y"]
    if case == "nonautonomous":
        value = {"rhs": [math.cos(t)], "jacobian": [[0.0]],
                 "partial_t": [-math.sin(t)]}[op]
    else:
        value = {"rhs": [-y[0], -1000.0 * y[1]],
                 "jacobian": [[-1.0, 0.0], [0.0, -1000.0]],
                 "partial_t": [0.0, 0.0]}[op]
    return {"id": request["id"], "ok": True, "value": value}


def run_case(binary: Path, folder: Path, method: str, case: str) -> dict:
    folder.mkdir()
    c = config(method, case)
    start = time.monotonic()
    sent, received = [], []
    with (folder / "stderr.log").open("xb") as stderr:
        process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=stderr,
                                   start_new_session=True)
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        buffer = bytearray()

        def send(value: dict) -> None:
            wire = json.dumps(value, allow_nan=False, separators=(",", ":")).encode() + b"\n"
            sent.append(wire)
            process.stdin.write(wire)
            process.stdin.flush()

        def read() -> dict:
            while b"\n" not in buffer:
                remaining = 30.0 - (time.monotonic() - start)
                if remaining <= 0 or not selector.select(remaining):
                    raise TimeoutError("30 second manufactured bridge check limit")
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("bridge EOF before terminal record")
                buffer.extend(chunk)
                if len(buffer) > 32 * 1024 * 1024:
                    raise RuntimeError("bridge output exceeds test transport limit")
            wire, _, rest = buffer.partition(b"\n")
            buffer[:] = rest
            received.append(bytes(wire) + b"\n")
            return json.loads(wire)

        try:
            hello = read()
            assert hello["type"] == "hello" and hello["protocol"] == "C21H_V1"
            assert hello["vigilode_commit"] == VIGILODE
            assert hello["diffsol_version"] == "0.17.1"
            send(c)
            requests = 0
            while True:
                record = read()
                if record["type"] == "result":
                    result = record
                    break
                requests += 1
                assert record["id"] == requests
                assert requests <= 100000
                send(rhs_response(record, c, case))
            process.stdin.close()
            exit_code = process.wait(timeout=5)
            # Any post-terminal data violates the single-result contract.
            assert not buffer and process.stdout.read() == b""
            if case in {"stiff_linear", "nonautonomous"}:
                assert exit_code == 0 and result["ok"] and result["success"]
                assert result["complete_output"] and result["accepted_grid_complete"]
                assert result["times"] == [c["t0"], c["t1"]]
                assert len(result["states"]) == 2
                times, states = result["accepted_times"], result["accepted_states"]
                assert len(times) == len(states) == result["internal_steps"] + 1
                assert times[0] == c["t0"] and times[-1] == c["t1"]
                assert all(0.0 < b - a <= c["h_max"] for a, b in zip(times, times[1:]))
                assert all(len(y) == c["dimension"] and all(math.isfinite(v) for v in y) for y in states)
                exact = ([math.exp(-0.02), math.exp(-20.0)] if case == "stiff_linear"
                         else [0.5 + math.sin(c["t1"]) - math.sin(c["t0"])])
                budget = 2e-6 if case == "stiff_linear" else 2e-10
                error = max(abs(a - b) for a, b in zip(result["states"][-1], exact))
                assert error <= budget, (error, budget)
                assert result["rpc_counters"]["requests_attempted"] == requests
                assert result["rpc_counters"]["responses_validated"] == requests
            elif case == "partial":
                assert exit_code != 0 and not result["success"]
                assert not result["complete_output"] and not result["accepted_grid_complete"]
            else:
                assert exit_code != 0 and not result["ok"]
                assert requests == (0 if case == "invalid_config" else 1)
                if case == "callback_failure":
                    assert "NATIVE_SENTINEL_REJECTION" in result["error"]
                if case == "wrong_id":
                    assert "id mismatch" in result["error"]
            status, error_message = "PASS", None
        except BaseException as error:
            status, error_message = "FAIL", f"{type(error).__name__}: {error}"
            result = locals().get("result")
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            exit_code = process.wait()
        finally:
            selector.close()
            for stream in (process.stdin, process.stdout):
                if stream and not stream.closed:
                    stream.close()
    for name, data in (("stdin.jsonl", b"".join(sent)), ("stdout.jsonl", b"".join(received))):
        with (folder / name).open("xb") as stream:
            stream.write(data)
    receipt = {"case": case, "method": method, "status": status, "error": error_message,
               "exit_code": exit_code, "wall_seconds": time.monotonic() - start,
               "manufactured": True, "native_chemistry_executed": False,
               "config": c, "result": result,
               "files": {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                         for name in ("stdin.jsonl", "stdout.jsonl", "stderr.log")}}
    with (folder / "receipt.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return {key: receipt[key] for key in ("case", "method", "status", "error", "exit_code", "wall_seconds")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        parser.error("--binary must name an actual executable bridge")
    args.output_dir.mkdir()
    cases = ["stiff_linear", "nonautonomous", "partial", "callback_failure", "wrong_id", "invalid_config"]
    rows = []
    for method in ["vigilode-rodas5p", "diffsol-bdf"]:
        for case in cases:
            row = run_case(binary, args.output_dir / f"{method}_{case}", method, case)
            rows.append(row)
            print(json.dumps(row, allow_nan=False), flush=True)
    summary = {"schema": "C21H_ACTUAL_RUST_BRIDGE_BLACKBOX_V1", "binary": str(binary),
               "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
               "test_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "rows": rows, "all_pass": all(row["status"] == "PASS" for row in rows),
               "native_chemistry_executed": False}
    with (args.output_dir / "SUMMARY.json").open("x") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
