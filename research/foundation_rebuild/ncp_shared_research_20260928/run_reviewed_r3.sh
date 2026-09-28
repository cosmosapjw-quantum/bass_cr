#!/usr/bin/env bash
# Delivered cache-only executor. No automatic test suite, install, compile or retry.
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "usage: bash run_reviewed_r3.sh NEW_OUTPUT_DIR" >&2; exit 2; fi
SIDE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$SIDE" rev-parse --show-toplevel)"
PY="${BASS_R3_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
exec "$PY" "$SIDE/runtime_r3/run_cache_audit.py" --repo-root "$REPO" --out "$1"
