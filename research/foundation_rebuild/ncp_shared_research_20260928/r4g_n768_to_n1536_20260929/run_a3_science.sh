#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${ALLOW_NEW_NATIVE_R4M:-}" == YES_I_AUTHORIZE_A3_FILL_ONLY ]] || { echo A3_NATIVE_NOT_AUTHORIZED >&2; exit 64; }
: "${BASS_R4M_PYTHON:?prepared absolute Python path required}"
: "${PREDECESSOR_ARCHIVE:?completed N768 ZIP required}"
: "${EXPECTED_PREDECESSOR_SHA256:?completed N768 ZIP SHA required}"
: "${A1_PARTIAL_ARCHIVE:?A1 partial ZIP required}"
: "${EXPECTED_A1_SHA256:?A1 SHA required}"
: "${A2_PARTIAL_ARCHIVE:?A2 partial ZIP required}"
: "${EXPECTED_A2_SHA256:?A2 SHA required}"
: "${SOURCE_PINS:?A3 source pins required}"
: "${EXPECTED_SOURCE_PINS_SHA256:?A3 source pins SHA required}"
: "${EXPECTED_QUERY_PLAN_SHA256:?exact query plan SHA required}"
: "${EXPECTED_USEFUL_PILOT_PLAN_SHA256:?original pilot plan SHA required}"
: "${EXPECTED_SALVAGE_MANIFEST_SHA256:?A2 salvage manifest SHA required}"
: "${EXPECTED_FILL_PLAN_SHA256:?remaining fill plan SHA required}"
: "${EXPECTED_SELECTED_STAGE_SHA256:?A2 selected stage SHA required}"
: "${RESOURCE_POLICY:?shared-host policy path required}"
: "${EXPECTED_RESOURCE_POLICY_SHA256:?shared-host policy SHA required}"
: "${R4G_RESOURCE_SHARING_POLICY:?approved sharing policy required}"
: "${R4M_AUTHORIZATION_ID:?fresh A3 authorization required}"
: "${PRIOR_AUTHORIZATION_ID:?consumed A2 authorization required}"
: "${EXPECTED_COMMIT:?exact A3 execution commit required}"
: "${EXPECTED_TREE:?exact A3 execution tree required}"
: "${ANALYTIC_BUILD:?frozen native build required}"
: "${R4M_DEADLINE_UNIX:?approved deadline required}"
: "${R4M_MAX_WALL_SECONDS:?approved wall cap required}"
: "${R4M_TERMINATION_GRACE_SECONDS:?approved grace required}"
: "${R4M_WORKERS:?approved workers required}"
: "${R4M_CPUS:?approved CPU list required}"
: "${R4M_WORKER_RAM_BYTES:?approved worker RAM required}"
: "${R4M_TOTAL_WORKER_RAM_CAP_BYTES:?approved total RAM required}"
: "${R4M_GLOBAL_RAW_ATTEMPT_CAP:?approved lifetime raw cap required}"
: "${R4M_COST_SCOPE:?approved cumulative cost scope required}"
[[ "$BASS_R4M_PYTHON" == /* && -x "$BASS_R4M_PYTHON" ]] || { echo ABSOLUTE_PREPARED_PYTHON_REQUIRED >&2; exit 64; }
[[ "$R4G_RESOURCE_SHARING_POLICY" == COOPERATIVE_SHARED_HOST ]] || { echo SHARING_POLICY_MISMATCH >&2; exit 64; }
OUT="${1:?usage: bash run_a3_science.sh OUT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec "$BASS_R4M_PYTHON" -I -B "$HERE/supervise_a3.py" \
  --deadline-unix "$R4M_DEADLINE_UNIX" \
  --grace-seconds "$R4M_TERMINATION_GRACE_SECONDS" \
  --receipt "${OUT}_SUPERVISOR.json" --out "$OUT" -- \
  "$BASS_R4M_PYTHON" -I -B "$HERE/run_a3.py" \
  --out "$OUT" --predecessor-archive "$PREDECESSOR_ARCHIVE" \
  --expected-predecessor-sha256 "$EXPECTED_PREDECESSOR_SHA256" \
  --a1-partial-archive "$A1_PARTIAL_ARCHIVE" --expected-a1-sha256 "$EXPECTED_A1_SHA256" \
  --a2-partial-archive "$A2_PARTIAL_ARCHIVE" --expected-a2-sha256 "$EXPECTED_A2_SHA256" \
  --source-pins "$SOURCE_PINS" --expected-source-pins-sha256 "$EXPECTED_SOURCE_PINS_SHA256" \
  --expected-query-plan-sha256 "$EXPECTED_QUERY_PLAN_SHA256" \
  --expected-useful-pilot-plan-sha256 "$EXPECTED_USEFUL_PILOT_PLAN_SHA256" \
  --expected-salvage-manifest-sha256 "$EXPECTED_SALVAGE_MANIFEST_SHA256" \
  --expected-fill-plan-sha256 "$EXPECTED_FILL_PLAN_SHA256" \
  --expected-selected-stage-sha256 "$EXPECTED_SELECTED_STAGE_SHA256" \
  --resource-policy "$RESOURCE_POLICY" \
  --expected-resource-policy-sha256 "$EXPECTED_RESOURCE_POLICY_SHA256" \
  --resource-sharing-policy "$R4G_RESOURCE_SHARING_POLICY" \
  --authorization-id "$R4M_AUTHORIZATION_ID" --prior-authorization-id "$PRIOR_AUTHORIZATION_ID" \
  --expected-commit "$EXPECTED_COMMIT" --expected-tree "$EXPECTED_TREE" \
  --analytic-build "$ANALYTIC_BUILD" \
  --deadline-unix "$R4M_DEADLINE_UNIX" --max-wall-seconds "$R4M_MAX_WALL_SECONDS" \
  --workers "$R4M_WORKERS" --cpus "$R4M_CPUS" \
  --worker-ram-bytes "$R4M_WORKER_RAM_BYTES" \
  --total-worker-ram-cap-bytes "$R4M_TOTAL_WORKER_RAM_CAP_BYTES" \
  --global-raw-attempt-cap "$R4M_GLOBAL_RAW_ATTEMPT_CAP" \
  --cost-scope "$R4M_COST_SCOPE"
