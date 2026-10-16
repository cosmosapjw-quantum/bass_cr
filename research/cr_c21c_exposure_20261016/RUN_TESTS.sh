#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$ROOT/src"
python3 -m pytest -q tests -p no:cacheprovider
python3 src/compare_c21b.py --out evidence/REFERENCE_COMPARE_REGEN.json --n 2 4 8 16 32 64 128
python3 src/run_scope_matrix.py --out evidence/SCOPED_MATRIX_REGEN.json
