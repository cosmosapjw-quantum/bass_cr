#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${REI_SOURCE_ZIP:?Set REI_SOURCE_ZIP to original frozen REI PR311 ZIP path}"
cd "$ROOT"
export PYTHONPATH="$ROOT"
python -m unittest discover -s "$ROOT" -p 'test_cx_screen.py' -v
python -O -m unittest discover -s "$ROOT" -p 'test_cx_screen.py' -q
python "$ROOT/source_cx_screen.py" --source "$REI_SOURCE_ZIP" --out "$ROOT/results"
python "$ROOT/plot_science.py" --source-csv "$ROOT/results/BASS193_H_HPLUS_CX_SOURCE_CONDITIONAL_192.csv" --out "$ROOT/figures"
