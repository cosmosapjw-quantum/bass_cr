#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/results" "$TMP/figures" "$TMP/sources" "$TMP/parent/results"
cp "$ROOT"/phys18_stokes.py "$ROOT"/plot_phys18.py "$ROOT"/test_phys18.py "$TMP/"
cp "$ROOT"/sources/PR142_PHYS17_SOURCE.zip "$TMP/sources/"
cp "$ROOT"/parent/*.py "$TMP/parent/"
cp "$ROOT"/parent/results/SOURCE_UB2P_RECOIL_CROSSWALK.csv "$TMP/parent/results/"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$TMP/phys18_stokes.py" --out "$TMP"
python "$TMP/plot_phys18.py"
python "$TMP/test_phys18.py" -q
python -O "$TMP/test_phys18.py" -q
python "$ROOT/verify_outputs.py" --root "$TMP"
echo 'REPRODUCE_EXIT_0'
