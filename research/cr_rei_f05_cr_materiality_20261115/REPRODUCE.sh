#!/usr/bin/env bash
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D"
echo "BASS-CR source-native original REI F05 CR hazard and heat materiality, READ-ONLY"
python3 -m unittest -q test_materiality
python3 -O -m unittest -q test_materiality
sha256sum -c EXPECTED_OUTPUT.sha256
X="$(mktemp -d)"
trap 'rm -rf "$X"' EXIT
python3 cr_materiality.py --out "$X/main"
python3 independent_audit.py --science-result "$X/main/SCIENCE_RESULT.json" --out "$X/main/INDEPENDENT_AUDIT.json"
(cd "$X/main" && sha256sum -c "$D/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo "REAL 184320 SOURCE ROWS & INDEPENDENT AUDIT COLD BYTE REPLAY PASS; REI 28/88, working 33/88, fast 4/7, BASS_CR 0/3, all DELTA0"
