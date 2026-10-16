#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m pytest -q tests/test_c21d.py -p no:cacheprovider
python src/c21d_trilane.py --out evidence/TRILANE_REGENERATED.json --n 2 4 8 16 32 64 128
python -m src.run_scope_matrix
