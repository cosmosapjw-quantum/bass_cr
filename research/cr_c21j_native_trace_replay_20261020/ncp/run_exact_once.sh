#!/usr/bin/env bash
# One invocation of the frozen C21I native runner. No build, sweep, retry, or FD follow-up.
# The NCP executor first completes the current inventory and allocation described
# in NCP_C21J_EXACT_PILOT_KO.md. Affinity membership is not exclusive allocation.
set -euo pipefail
umask 077

for c21j_name in C21J_WORKTREE C21J_CONTROL_DIR C21J_NATIVE_BINARY \
  C21J_BRIDGE_BINARY C21J_BRIDGE_BUILD_RECEIPT C21J_PYTHON \
  C21J_ALLOCATED_CPU C21J_RUN_ROOT; do
  if [[ -z "${!c21j_name:-}" ]]; then
    printf 'NCP executor must resolve %s from the current verified context.\n' "$c21j_name" >&2
    exit 64
  fi
done
for c21j_name in C21J_WORKTREE C21J_CONTROL_DIR C21J_NATIVE_BINARY \
  C21J_BRIDGE_BINARY C21J_BRIDGE_BUILD_RECEIPT C21J_PYTHON C21J_RUN_ROOT; do
  if [[ "${!c21j_name}" != /* ]]; then
    printf '%s must be an absolute path.\n' "$c21j_name" >&2
    exit 64
  fi
done
if [[ ! "$C21J_ALLOCATED_CPU" =~ ^(0|[1-9][0-9]*)$ || "$C21J_ALLOCATED_CPU" == 55 ]]; then
  printf 'One explicitly allocated CPU other than protected CPU55 is required.\n' >&2
  exit 64
fi
if [[ ! -x "$C21J_PYTHON" || ! -x "$C21J_NATIVE_BINARY" || ! -x "$C21J_BRIDGE_BINARY" ]]; then
  printf 'The resolved Python, native binary, and bridge must be executable.\n' >&2
  exit 66
fi
if [[ -e "$C21J_RUN_ROOT" || -L "$C21J_RUN_ROOT" ]]; then
  printf 'Refusing an existing run root: %s\n' "$C21J_RUN_ROOT" >&2
  exit 73
fi
if [[ -n "${C21J_TIME_BINARY:-}" && ( "$C21J_TIME_BINARY" != /* || ! -x "$C21J_TIME_BINARY" ) ]]; then
  printf 'C21J_TIME_BINARY, when selected, must be the verified absolute GNU time executable.\n' >&2
  exit 66
fi

export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
c21j_i="$C21J_WORKTREE/research/cr_c21i_callback_optimization_20261020"
c21j_source="$C21J_WORKTREE/research/cr_c21e_event_native_20261018"
c21j_g="$C21J_WORKTREE/research/cr_c21g_reference_refinement_20261019"
mkdir -- "$C21J_RUN_ROOT"

# Read-only prelaunch identity check; this process imports no scientific package
# and starts no native process. The frozen runner still owns its full admission.
set +e
"$C21J_PYTHON" - "$C21J_NATIVE_BINARY" "$c21j_i/run_optimized_pilot.py" \
  "$C21J_ALLOCATED_CPU" > "$C21J_RUN_ROOT/prelaunch.json" \
  2> "$C21J_RUN_ROOT/prelaunch.stderr" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import sys

native, runner = (Path(value).resolve(strict=True) for value in sys.argv[1:3])
cpu = int(sys.argv[3])
expected_native = "1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40"
expected_runner = "1a3f4d9066bedc3a8d7466723e8f344fa451c0c6a85c48bf0efe03210d6d8a43"
def record(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
native_record, runner_record = record(native), record(runner)
if native_record["sha256"] != expected_native:
    raise SystemExit("SELECTED_PILOT_REQUIRES_VERIFIED_PR82_NATIVE_BINARY_HASH")
if runner_record["sha256"] != expected_runner:
    raise SystemExit("SELECTED_PILOT_REQUIRES_FROZEN_FE6_C21I_RUNNER_BYTES")
if cpu == 55 or cpu not in os.sched_getaffinity(0):
    raise SystemExit("CPU_NOT_ADMITTED")
print(json.dumps({
    "schema": "C21J_EXACT_PACKET_PRELAUNCH_V1",
    "native": native_record,
    "runner": runner_record,
    "allocated_cpu": cpu,
    "exclusive_allocation": "MUST_BE_VERIFIED_BY_CURRENT_NCP_INVENTORY",
    "native_execution": "NOT_RUN_BY_PRELAUNCH",
    "global_error_bound": None,
}, indent=2))
PY
c21j_prelaunch_exit=$?
set -e
printf '%s\n' "$c21j_prelaunch_exit" > "$C21J_RUN_ROOT/prelaunch_exit_code.txt"
if ((c21j_prelaunch_exit)); then
  exit "$c21j_prelaunch_exit"
fi

c21j_command=("$C21J_PYTHON" "$c21j_i/run_optimized_pilot.py" native
  --optimization vectorized_exact
  --publication-receipt "$C21J_CONTROL_DIR/I_PUBLICATION.json"
  --c21h-publication-receipt "$C21J_CONTROL_DIR/H_PUBLICATION.json"
  --source-dir "$c21j_source" --c21g-unit "$c21j_g"
  --baseline-dir "$c21j_source/evidence/C21F_NATIVE_NCP_20261018T1358Z"
  --bridge "$C21J_BRIDGE_BINARY" --bridge-build-receipt "$C21J_BRIDGE_BUILD_RECEIPT"
  --native "$C21J_NATIVE_BINARY" --cpu "$C21J_ALLOCATED_CPU"
  --fixture common_ic --method vigilode-rodas5p --variant base
  --out "$C21J_RUN_ROOT/job")
printf '%q ' "${c21j_command[@]}" > "$C21J_RUN_ROOT/command.sh.txt"
printf '\n' >> "$C21J_RUN_ROOT/command.sh.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$C21J_RUN_ROOT/started_at_utc.txt"
set +e
if [[ -n "${C21J_TIME_BINARY:-}" ]]; then
  "$C21J_TIME_BINARY" -v -o "$C21J_RUN_ROOT/process.time.txt" \
    "${c21j_command[@]}" > "$C21J_RUN_ROOT/runner.stdout" 2> "$C21J_RUN_ROOT/runner.stderr"
else
  "${c21j_command[@]}" > "$C21J_RUN_ROOT/runner.stdout" 2> "$C21J_RUN_ROOT/runner.stderr"
fi
c21j_exit=$?
set -e
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$C21J_RUN_ROOT/ended_at_utc.txt"
printf '%s\n' "$c21j_exit" > "$C21J_RUN_ROOT/runner_exit_code.txt"
exit "$c21j_exit"
