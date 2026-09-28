#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${RESUME_ARCHIVE:?set RESUME_ARCHIVE}"
: "${EXPECTED_RESUME_SHA256:?set EXPECTED_RESUME_SHA256}"
: "${EXPECTED_COMMIT:?set EXPECTED_COMMIT}"
PREVIOUS_NSTEP="${PREVIOUS_NSTEP:-384}"
NEXT_NSTEP="${NEXT_NSTEP:-768}"
OUT="${1:?usage: run_r4c_preflight.sh OUT}"
python -m py_compile "$HERE/continue_temporal.py"
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest -q -p no:cacheprovider "$HERE/tests/test_planner.py"
python "$HERE/continue_temporal.py" \
  --out "$OUT" \
  --resume-archive "$RESUME_ARCHIVE" \
  --expected-resume-archive-sha256 "$EXPECTED_RESUME_SHA256" \
  --previous-nstep "$PREVIOUS_NSTEP" \
  --next-nstep "$NEXT_NSTEP" \
  --expected-commit "$EXPECTED_COMMIT" \
  --preflight-only
