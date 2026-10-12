"""Create-only wrapper recording one actual independent reference invocation."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

here = Path(__file__).resolve().parent
unit = here.parent
receipt = here / "INDEPENDENT_REFERENCE_ACTUAL_EXECUTION.json"
if receipt.exists() or (here / "INDEPENDENT_REFERENCE.stdout.txt").exists():
    raise FileExistsError("INDEPENDENT_REFERENCE_ALREADY_ATTEMPTED")
paths = [here / "independent_reference.py", here / "REFERENCE_CONTRACT.json", Path(__file__),
         unit / "finite_age_closure.py", unit / "inputs/CACHED_RESPONSE.json",
         unit / "inputs/QUADRATIC_RESPONSE.json", unit / "results/RESPONSE_ERROR_MAP.json"]
source_sha256 = {str(path.relative_to(unit)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
command = [sys.executable, "-B", str(here / "independent_reference.py")]
start_utc = dt.datetime.now(dt.timezone.utc).isoformat()
start_clock = time.perf_counter()
with (here / "INDEPENDENT_REFERENCE.stdout.txt").open("x") as out, (here / "INDEPENDENT_REFERENCE.stderr.txt").open("x") as err:
    result = subprocess.run(command, cwd=unit, stdout=out, stderr=err)
wall_s = time.perf_counter() - start_clock
record = {"command": command, "cwd": str(unit), "started_utc": start_utc,
          "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "wall_s": wall_s,
          "exit_code": result.returncode, "python": sys.version, "reviewer": "/root/independent_review",
          "source_sha256": source_sha256, "actual_reference_invocations": 1,
          "old_evaluator_calls": 0, "owner_test_suite_calls": 0, "G": 0, "NCP": 0,
          "stdout_sha256": hashlib.sha256((here / "INDEPENDENT_REFERENCE.stdout.txt").read_bytes()).hexdigest(),
          "stderr_sha256": hashlib.sha256((here / "INDEPENDENT_REFERENCE.stderr.txt").read_bytes()).hexdigest()}
with receipt.open("x") as stream:
    json.dump(record, stream, indent=2)
    stream.write("\n")
print(json.dumps({"exit_code": result.returncode, "wall_s": wall_s, "receipt": str(receipt)}))
sys.exit(result.returncode)
