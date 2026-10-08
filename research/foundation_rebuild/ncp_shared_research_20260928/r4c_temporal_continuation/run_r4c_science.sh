#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${ALLOW_NEW_NATIVE_R4C:-}" == "YES_I_AUTHORIZE_ONE_RUNG" ]] || { echo 'R4C_NATIVE_NOT_AUTHORIZED' >&2; exit 64; }
[[ "${PREVIOUS_NSTEP:-384}" == 384 && "${NEXT_NSTEP:-768}" == 768 ]] || { echo 'R4C_ONLY_N384_TO_N768_AUTHORIZED' >&2; exit 64; }
: "${RESUME_ARCHIVE:?set RESUME_ARCHIVE}"
: "${EXPECTED_RESUME_SHA256:?set EXPECTED_RESUME_SHA256}"
: "${EXPECTED_COMMIT:?set EXPECTED_COMMIT}"
: "${EXPECTED_TREE:?set EXPECTED_TREE}"
: "${ANALYTIC_BUILD:?set ANALYTIC_BUILD}"
: "${BASS_R4C_PYTHON:?set prepared absolute Python path}"
: "${R4C_AUTHORIZATION_ID:?set unique user-approved attempt ID}"
: "${R4C_MAX_WALL_SECONDS:?set newly approved wall-clock budget}"
[[ "$R4C_MAX_WALL_SECONDS" =~ ^[1-9][0-9]{0,8}$ ]] || { echo 'INVALID_WALL_BUDGET' >&2; exit 64; }
[[ "$BASS_R4C_PYTHON" == /* && -x "$BASS_R4C_PYTHON" ]] || { echo 'ABSOLUTE_PREPARED_PYTHON_REQUIRED' >&2; exit 64; }
command -v timeout >/dev/null || { echo 'TIMEOUT_SUPERVISOR_REQUIRED' >&2; exit 64; }
OUT="${1:?usage: run_r4c_science.sh OUT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
# SIGTERM gives Python a chance to preserve evidence; SIGKILL bounds a stuck C call.
# The 60-second termination grace is part of the explicit approval contract.
exec timeout --signal=TERM --kill-after=60s "${R4C_MAX_WALL_SECONDS}s" \
 "$BASS_R4C_PYTHON" -I -B "$HERE/continue_temporal.py" \
 --out "$OUT" --resume-archive "$RESUME_ARCHIVE" \
 --expected-resume-archive-sha256 "$EXPECTED_RESUME_SHA256" \
 --previous-nstep 384 --next-nstep 768 --expected-commit "$EXPECTED_COMMIT" \
 --expected-tree "$EXPECTED_TREE" --analytic-build "$ANALYTIC_BUILD"
