#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
echo 'ORIGINAL F05 ACCEPTED-HISTORY CASE-B MINIMUM REACTION BUDGET; READ ONLY'
python3 -m unittest -q test_accepted_recomb_min
python3 -O -m unittest -q test_accepted_recomb_min
sha256sum -c EXPECTED_OUTPUT.sha256
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
python3 accepted_recomb_min.py --out "$temp" >/dev/null
(cd "$temp" && sha256sum -c "$HERE/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo 'SCIENCE_SOURCE_REPLAY_PASS, REI_CENTRAL 28/88, WORKING 33/88, FAST 4/7, BASS_CR 0/3, ALL DELTA0'
