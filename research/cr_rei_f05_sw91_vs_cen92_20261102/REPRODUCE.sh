#!/usr/bin/env bash
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D"
echo 'REI ORIGINAL F05 SOURCE-LOCKED COOLING MODEL SPREAD; READ ONLY'
python3 -m unittest -q test_cooling_spread
python3 -O -m unittest -q test_cooling_spread
sha256sum -c EXPECTED_OUTPUT.sha256
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 cooling_spread.py --out "$tmp" > /dev/null
(cd "$tmp" && sha256sum -c "$D/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo 'SOURCE_NATIVE_REPLAY_PASS; REI_CENTRAL_28/88; WORKING_33/88; BASS_CR_0/3; ALL_DELTA_0'
