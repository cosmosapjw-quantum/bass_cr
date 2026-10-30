#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
python -m unittest test_phys12 -q
python -O -m unittest test_phys12 -q
python -m compileall -q phys12_h_eii.py blind_referee.py test_phys12.py verify_outputs.py
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
python phys12_h_eii.py --source-zip sources/PR136_ORIGINAL_SOURCE.zip --out "$TEMP" > "$TEMP/STDOUT.json"
python verify_outputs.py "$TEMP"
python blind_referee.py
python verify_outputs.py results
printf 'PHYS12_CLEAN_REPRODUCE_EXIT0\n'
