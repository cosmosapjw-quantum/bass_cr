#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${ALLOW_NEW_NATIVE_R4G:-}" == YES_I_AUTHORIZE_N1536 ]] || { echo N1536_NATIVE_NOT_AUTHORIZED >&2; exit 64; }
: "${BASS_R4G_PYTHON:?prepared absolute Python path required}"
: "${PREDECESSOR_ARCHIVE:?completed N768 ZIP required}"
: "${EXPECTED_PREDECESSOR_SHA256:?completed N768 ZIP SHA256 required}"
: "${SOURCE_PINS:?verified source-pins file required}"
: "${EXPECTED_SOURCE_PINS_SHA256:?source-pins SHA256 required}"
: "${EXPECTED_QUERY_PLAN_SHA256:?exact query-plan SHA256 required}"
: "${EXPECTED_USEFUL_PILOT_PLAN_SHA256:?useful pilot-plan SHA256 required}"
: "${R4G_AUTHORIZATION_ID:?fresh N1536 authorization required}"
: "${EXPECTED_COMMIT:?exact N1536 execution commit required}"
: "${EXPECTED_TREE:?exact N1536 execution tree required}"
: "${ANALYTIC_BUILD:?frozen native build required}"
: "${R4G_DEADLINE_UNIX:?approved deadline required}"
: "${R4G_MAX_WALL_SECONDS:?approved wall cap required}"
: "${R4G_TERMINATION_GRACE_SECONDS:?approved grace required}"
: "${R4G_WORKER_STAGES:?approved worker stages required}"
: "${R4G_HARD_MAX_WORKERS:?approved hard worker cap required}"
: "${R4G_CPUS:?approved CPU list required}"
: "${R4G_WORKER_RAM_BYTES:?approved worker RAM required}"
: "${R4G_TOTAL_WORKER_RAM_CAP_BYTES:?approved total worker RAM required}"
: "${R4G_GLOBAL_RAW_ATTEMPT_CAP:?approved raw cap required}"
: "${R4G_COST_SCOPE:?approved cost scope required}"
[[ "$BASS_R4G_PYTHON" == /* && -x "$BASS_R4G_PYTHON" ]] || { echo ABSOLUTE_PREPARED_PYTHON_REQUIRED >&2; exit 64; }
OUT="${1:?usage: bash run_n1536_science.sh OUT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec "$BASS_R4G_PYTHON" -I -B "$HERE/supervise_n1536.py" \
  --deadline-unix "$R4G_DEADLINE_UNIX" \
  --grace-seconds "$R4G_TERMINATION_GRACE_SECONDS" \
  --receipt "${OUT}_SUPERVISOR.json" --out "$OUT" -- \
  "$BASS_R4G_PYTHON" -I -B "$HERE/run_n1536.py" \
  --out "$OUT" --predecessor-archive "$PREDECESSOR_ARCHIVE" \
  --expected-predecessor-sha256 "$EXPECTED_PREDECESSOR_SHA256" \
  --source-pins "$SOURCE_PINS" \
  --expected-source-pins-sha256 "$EXPECTED_SOURCE_PINS_SHA256" \
  --expected-query-plan-sha256 "$EXPECTED_QUERY_PLAN_SHA256" \
  --expected-useful-pilot-plan-sha256 "$EXPECTED_USEFUL_PILOT_PLAN_SHA256" \
  --authorization-id "$R4G_AUTHORIZATION_ID" \
  --expected-commit "$EXPECTED_COMMIT" --expected-tree "$EXPECTED_TREE" \
  --analytic-build "$ANALYTIC_BUILD" \
  --deadline-unix "$R4G_DEADLINE_UNIX" \
  --max-wall-seconds "$R4G_MAX_WALL_SECONDS" \
  --stages "$R4G_WORKER_STAGES" --hard-max-workers "$R4G_HARD_MAX_WORKERS" \
  --cpus "$R4G_CPUS" --worker-ram-bytes "$R4G_WORKER_RAM_BYTES" \
  --total-worker-ram-cap-bytes "$R4G_TOTAL_WORKER_RAM_CAP_BYTES" \
  --global-raw-attempt-cap "$R4G_GLOBAL_RAW_ATTEMPT_CAP" \
  --cost-scope "$R4G_COST_SCOPE"
