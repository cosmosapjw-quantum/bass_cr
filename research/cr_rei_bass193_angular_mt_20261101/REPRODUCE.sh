#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${REI_SOURCE_ZIP:?Set REI_SOURCE_ZIP to the original private SHA-locked REI PR311 ZIP}"
cd "$HERE"
python3 -m unittest -v test_angular_mt.py
python3 -O -m unittest -q test_angular_mt.py
python3 angular_mt.py --source "$REI_SOURCE_ZIP" --out "$HERE/results"
mkdir -p "$HERE/figures"
python3 plot_science.py
sha256sum "$HERE/results/BASS193_CX_A7_LINEAR_DRAG_192.csv" "$HERE/results/RESULT.json"
