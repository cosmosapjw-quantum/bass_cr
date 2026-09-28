#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${RESUME_ARCHIVE:?set RESUME_ARCHIVE}"
: "${EXPECTED_RESUME_SHA256:?set EXPECTED_RESUME_SHA256}"
: "${EXPECTED_COMMIT:?set EXPECTED_COMMIT}"
: "${BASS_R4C_PYTHON:?set prepared absolute Python path}"
[[ "${PREVIOUS_NSTEP:-384}" == 384 && "${NEXT_NSTEP:-768}" == 768 ]] || { echo 'R4C_ONLY_N384_TO_N768'; exit 64; }
OUT="${1:?usage: run_r4c_preflight.sh OUT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
"$BASS_R4C_PYTHON" -I -B "$HERE/continue_temporal.py" \
 --out "$OUT" --resume-archive "$RESUME_ARCHIVE" \
 --expected-resume-archive-sha256 "$EXPECTED_RESUME_SHA256" \
 --previous-nstep 384 --next-nstep 768 --expected-commit "$EXPECTED_COMMIT" --preflight-only
