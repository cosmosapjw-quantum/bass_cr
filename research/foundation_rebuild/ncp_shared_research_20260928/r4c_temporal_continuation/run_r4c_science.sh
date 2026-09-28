#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${ALLOW_NEW_NATIVE_R4C:-}" != "YES_I_AUTHORIZE_ONE_RUNG" ]]; then
  echo "R4C_NATIVE_NOT_AUTHORIZED: set ALLOW_NEW_NATIVE_R4C=YES_I_AUTHORIZE_ONE_RUNG only after explicit user authorization" >&2
  exit 64
fi
: "${RESUME_ARCHIVE:?set RESUME_ARCHIVE}"
: "${EXPECTED_RESUME_SHA256:?set EXPECTED_RESUME_SHA256}"
: "${EXPECTED_COMMIT:?set EXPECTED_COMMIT}"
: "${ANALYTIC_BUILD:?set ANALYTIC_BUILD}"
PREVIOUS_NSTEP="${PREVIOUS_NSTEP:-384}"
NEXT_NSTEP="${NEXT_NSTEP:-768}"
OUT="${1:?usage: run_r4c_science.sh OUT}"
python "$HERE/continue_temporal.py" \
  --out "$OUT" \
  --resume-archive "$RESUME_ARCHIVE" \
  --expected-resume-archive-sha256 "$EXPECTED_RESUME_SHA256" \
  --previous-nstep "$PREVIOUS_NSTEP" \
  --next-nstep "$NEXT_NSTEP" \
  --expected-commit "$EXPECTED_COMMIT" \
  --analytic-build "$ANALYTIC_BUILD"
