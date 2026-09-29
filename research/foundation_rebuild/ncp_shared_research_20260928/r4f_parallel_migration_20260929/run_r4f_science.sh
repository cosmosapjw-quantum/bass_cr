#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${ALLOW_NEW_NATIVE_R4F:-}" == YES_I_AUTHORIZE_MIGRATION ]] || { echo R4F_NATIVE_NOT_AUTHORIZED >&2; exit 64; }
: "${BASS_R4F_PYTHON:?prepared absolute Python path required}"
: "${RESUME_ARCHIVE:?original archive required}"
: "${EXPECTED_RESUME_SHA256:?original archive SHA256 required}"
: "${EXPECTED_COMMIT:?new exact execution commit required}"
: "${EXPECTED_TREE:?new exact execution tree required}"
: "${ANALYTIC_BUILD:?frozen native build required}"
: "${PARENT_OUT:?stopped parent output required}"
: "${STOP_RECEIPT:?exact parent stop receipt required}"
: "${PARENT_AUTH_ID:?consumed parent authorization ID required}"
: "${R4F_AUTHORIZATION_ID:?new user-approved migration authorization ID required}"
: "${R4F_DEADLINE_UNIX:?approved original-envelope deadline required}"
: "${R4F_TERMINATION_GRACE_SECONDS:?approved termination grace required}"
: "${R4F_WORKERS:?approved worker cap required}"
: "${R4F_CPUS:?approved CPU list required}"
: "${R4F_WORKER_RAM_BYTES:?approved worker RAM cap required}"
: "${R4F_COST_SCOPE:?approved cost scope required}"
[[ "$BASS_R4F_PYTHON" == /* && -x "$BASS_R4F_PYTHON" ]] || { echo ABSOLUTE_PREPARED_PYTHON_REQUIRED >&2; exit 64; }
OUT="${1:?usage: run_r4f_science.sh OUT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec "$BASS_R4F_PYTHON" -I -B "$HERE/supervise.py" \
  --deadline-unix "$R4F_DEADLINE_UNIX" \
  --grace-seconds "$R4F_TERMINATION_GRACE_SECONDS" \
  --receipt "${OUT}_SUPERVISOR.json" --out "$OUT" -- \
  "$BASS_R4F_PYTHON" -I -B "$HERE/run_parallel_bridge.py" \
  --out "$OUT" --resume-archive "$RESUME_ARCHIVE" \
  --expected-resume-sha256 "$EXPECTED_RESUME_SHA256" \
  --parent-out "$PARENT_OUT" --stop-receipt "$STOP_RECEIPT" \
  --parent-authorization-id "$PARENT_AUTH_ID" \
  --authorization-id "$R4F_AUTHORIZATION_ID" \
  --expected-commit "$EXPECTED_COMMIT" --expected-tree "$EXPECTED_TREE" \
  --analytic-build "$ANALYTIC_BUILD" \
  --deadline-unix "$R4F_DEADLINE_UNIX" \
  --workers "$R4F_WORKERS" --pilot-queries 8 --parity-count 2 \
  --cpus "$R4F_CPUS" --worker-ram-bytes "$R4F_WORKER_RAM_BYTES" \
  --cost-scope "$R4F_COST_SCOPE"
