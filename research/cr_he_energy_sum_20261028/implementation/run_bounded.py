#!/usr/bin/env python3
"""Serial jobs charged only to the separate CR energy-sum 40 CPU-s unit.

The worker has CPU/address-space/wall limits.  Aggregate coordinator+worker
accounting is measured, rounded upward, and charged with a 0.05 s tail.  This
is not a proof of a preventive aggregate hard cap.  Metadata/provider/CAS
costs remain separately unmeasured/null and old/foreign budgets do not move.
"""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time

U = Path(os.environ.get("CR_UNIT_ROOT", str(Path(__file__).resolve().parents[1]))).resolve()
UNIT = "CR_PHYS02_HE_ENERGY_SUM_V1"
CAP = 40
MEMORY = 536870912
WALL = 50
TAIL = 0.05
MODES = ("probe", "primary", "controls", "independent", "plot", "targeted")
ADMITTED = ("PASS", "PASS_SCOPED", "PASS_SCOPED_ENERGY_SUM")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    os.replace(temporary, path)


def source_paths():
    return sorted((p for directory in ("implementation", "reference")
                   for p in (U / directory).glob("*.py")), key=lambda p: p.relative_to(U).as_posix())


def identity(path, raw=None):
    raw = path.read_bytes() if raw is None else raw
    return {"path": path.relative_to(U).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def snapshot(out):
    manifest = []
    destination = out / "EXECUTED_SOURCE"
    destination.mkdir()
    for path in source_paths():
        raw = path.read_bytes()
        row = identity(path, raw)
        copy = destination / row["path"]
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(raw)
        manifest.append(row)
    write(out / "SOURCE_MANIFEST.json", manifest)
    return manifest


def kill_owned(proc):
    if proc is not None and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def interrupted(signum, frame):
    raise InterruptedError(f"COORDINATOR_SIGNAL_{signum}")


def main():
    require(len(sys.argv) == 4, "USAGE: run_bounded.py RUN_ID MODE RESERVATION_CPU_S")
    run_id, mode, reservation = sys.argv[1], sys.argv[2], float(sys.argv[3])
    require(mode in MODES, "UNKNOWN_BOUNDED_MODE")
    require(math.isfinite(reservation) and reservation >= 2, "FINITE_RESERVATION_AT_LEAST_TWO_REQUIRED")
    require(bool(run_id) and run_id.isascii()
            and all(c.isalnum() or c in "_-" for c in run_id), "SAFE_CREATE_ONLY_RUN_ID_REQUIRED")
    lock = (U / "BUDGET.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    budget = json.loads((U / "BUDGET.json").read_text())
    require(budget["unit"] == UNIT and budget["cap_cpu_s"] == CAP, "WRONG_UNIT_OR_CAP")
    require(budget.get("science_closed") is False
            and budget.get("additional_science_allowance_cpu_s", 0) > 0, "UNIT_SCIENCE_CLOSED")
    require(not any(row.get("status") == "RESERVED" for row in budget["attempts"]),
            "UNSETTLED_RESERVED_ATTEMPT_REQUIRES_RECOVERY")
    require(budget["charge_cpu_s"] + reservation <= CAP
            and reservation <= budget["additional_science_allowance_cpu_s"], "INSUFFICIENT_OWN_UNIT_ALLOWANCE")
    out = U / "runs" / run_id
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {"run_id": run_id, "mode": mode, "status": "RESERVED", "utc": started,
              "reservation_cpu_s": reservation, "worker_memory_limit_bytes": MEMORY,
              "native_threads": 1, "wall_timeout_s": WALL, "unit": UNIT}
    budget["attempts"].append(record.copy())
    write(U / "BUDGET.json", budget)
    write(out / "RESERVATION.json", record)

    # Everything below is part of this reserved attempt, including preparation
    # failures.  Previously completed or failed attempts are never replaced.
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    proc = None
    code = None
    manifest = None
    stdout = stderr = ""
    failures = []
    t0 = time.monotonic()
    try:
        manifest = snapshot(out)
        environment = os.environ.copy()
        for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
            environment[name] = "1"
        environment.update(CR_UNIT_ROOT=str(U), CR_BOUNDED_OUTDIR=str(out),
                           MPLCONFIGDIR=str(out / "mplcache"), PYTHONDONTWRITEBYTECODE="1")
        hard = int(math.floor(reservation - 0.5))

        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (hard, hard))
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))

        if mode == "probe":
            program = ('import sys,numpy,resource,json; '
                       'print(json.dumps({"runtime":"PYTHON_PASS","numpy":numpy.__version__,'
                       '"python":sys.version.split()[0],'
                       '"max_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))')
            command = [sys.executable, "-c", program]
        else:
            command = [sys.executable, str(U / "implementation" / (mode + ".py")), str(out)]
        write(out / "COMMAND.json", {"argv": command, "cwd": str(U),
              "limits": {"cpu_hard_s": hard, "wall_timeout_s": WALL, "memory_bytes": MEMORY},
              "single_owned_process_group": True, "execution_source": "ORIGINAL_PATH_BOUND_TO_SOURCE_MANIFEST"})
        proc = subprocess.Popen(command, cwd=U, env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True,
                                preexec_fn=limits)
        try:
            stdout, stderr = proc.communicate(timeout=WALL)
        except subprocess.TimeoutExpired:
            failures.append("OWNED_PROCESS_WALL_TIMEOUT")
            kill_owned(proc)
            stdout, stderr = proc.communicate()
        code = proc.returncode
    except BaseException as error:
        failures.append(type(error).__name__ + ": " + str(error))
        kill_owned(proc)
        if proc is not None:
            stdout, stderr = proc.communicate()
            code = proc.returncode

    (out / "stdout.txt").write_text(stdout)
    (out / "stderr.txt").write_text(stderr)
    if code != 0:
        failures.append("WORKER_EXIT_CODE_" + str(code))
    try:
        final_manifest = [identity(path) for path in source_paths()]
        unchanged = manifest is not None and final_manifest == manifest
        write(out / "FINAL_SOURCE_MANIFEST.json", final_manifest)
    except Exception as error:
        unchanged = False
        failures.append("SOURCE_CHECK_" + type(error).__name__ + ": " + str(error))
    if not unchanged:
        failures.append("EXECUTED_SOURCE_SET_OR_BYTES_CHANGED")
    scientific = None
    if mode == "probe":
        try:
            probe = json.loads(stdout)
            require(probe.get("runtime") == "PYTHON_PASS", "RUNTIME_PROBE_STATUS_MISMATCH")
            write(out / "PROBE.json", probe)
        except Exception as error:
            failures.append("PROBE_OUTPUT_" + type(error).__name__ + ": " + str(error))
    else:
        try:
            scientific = json.loads((out / "RESULT.json").read_text()).get("status")
        except Exception as error:
            scientific = "UNPARSEABLE_OR_MISSING"
            failures.append("RESULT_" + type(error).__name__ + ": " + str(error))
        if scientific not in ADMITTED:
            failures.append("SCIENTIFIC_RESULT_STATUS_NOT_ADMITTED")

    # Includes startup, snapshotting, worker launch/wait, source recheck and
    # result parsing.  The conservative tail covers the remaining ledger work;
    # it is explicitly not asserted to be a hard preventive bound.
    self_usage = resource.getrusage(resource.RUSAGE_SELF)
    child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    coordinator = self_usage.ru_utime + self_usage.ru_stime
    worker = child_usage.ru_utime + child_usage.ru_stime
    measured = coordinator + worker
    rounded = math.ceil(measured * 1e6) / 1e6
    charge = round(rounded + TAIL, 6)
    if charge > reservation:
        failures.append("MEASURED_CHARGE_EXCEEDS_RESERVATION")
    success = code == 0 and unchanged and not failures
    record.update(status="PASS" if success else "FAIL", exit_code=code,
                  failure=failures[0] if failures else None, failure_reasons=failures,
                  measured_cpu_s=measured, worker_cpu_s=worker, coordinator_cpu_s=coordinator,
                  tails_cpu_s=TAIL, rounding_tail_cpu_s=rounded - measured,
                  charged_cpu_s=charge, wall_s=time.monotonic() - t0,
                  source_unchanged=unchanged, scientific_status=scientific,
                  maximum_worker_rss_kib=child_usage.ru_maxrss,
                  source_snapshot_preserves_directories=True,
                  metadata_provider_publication_CPU_s=None, remote_CAS_CPU_s=None,
                  preventive_aggregate_hard_cap_proof=False)
    budget["attempts"][-1] = record
    budget["charge_cpu_s"] = round(sum(row["charged_cpu_s"] for row in budget["attempts"]), 6)
    budget["measured_cpu_s"] = sum(row["measured_cpu_s"] for row in budget["attempts"])
    budget["tails_cpu_s"] = sum(row["tails_cpu_s"] + row["rounding_tail_cpu_s"] for row in budget["attempts"])
    budget["remaining_cpu_s"] = round(CAP - budget["charge_cpu_s"], 6)
    budget["additional_science_allowance_cpu_s"] = (0 if budget["science_closed"]
                                                   else budget["remaining_cpu_s"])
    budget["status"] = "OPEN" if not budget["science_closed"] else "SCIENCE_CLOSED"
    budget["all_runtime_attempts_pass"] = all(row["status"] == "PASS" for row in budget["attempts"])
    budget["preventive_aggregate_hard_cap_proof"] = False
    write(out / "RECEIPT.json", record)
    write(U / "BUDGET.json", budget)
    print(json.dumps(record, allow_nan=False))
    fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()
    return 0 if success else 2


if __name__ == "__main__":
    sys.exit(main())
