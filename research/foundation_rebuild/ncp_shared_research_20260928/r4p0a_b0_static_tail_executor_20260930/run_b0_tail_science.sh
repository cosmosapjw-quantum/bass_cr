#!/usr/bin/env bash
set -euo pipefail
: "${BASS_R4P0_PYTHON:?verified absolute Python required}"
: "${R4P0_PROPOSAL:?exact proposal path required}"
: "${R4P0_SOURCE_PINS:?exact source pins path required}"
: "${R4P0_INPUTS:?exact bank/input path required}"
: "${ANALYTIC_BUILD:?frozen build path required}"
: "${R4P0_APPROVED_PROPOSAL_SHA256:?explicitly approved proposal SHA256 required}"
[[ "${ALLOW_NEW_NATIVE_R4P0:-}" == YES_I_AUTHORIZE_EIGHT_B0_STATIC_SNAPSHOTS ]] || exit 2
[[ "$BASS_R4P0_PYTHON" = /* && -x "$BASS_R4P0_PYTHON" ]] || exit 2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
SIDE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$BASS_R4P0_PYTHON" -I -B "$SIDE/supervise_tail.py" \
  --proposal "$R4P0_PROPOSAL" --source-pins "$R4P0_SOURCE_PINS" \
  --inputs "$R4P0_INPUTS" --build "$ANALYTIC_BUILD" --out "${1:?fresh OUT required}" \
  --approved-proposal-sha256 "$R4P0_APPROVED_PROPOSAL_SHA256"
