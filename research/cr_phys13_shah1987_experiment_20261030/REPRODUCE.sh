#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest -q test_phys13
python -O -m unittest -q test_phys13
python -m compileall -q phys13_shah.py blind_referee.py verify_outputs.py verify_manifest.py test_phys13.py
python blind_referee.py
REGEN="$(mktemp -d)"; trap 'rm -rf "$REGEN"' EXIT
python phys13_shah.py --out "$REGEN" > /dev/null
python verify_outputs.py --out "$REGEN"
echo 'CLEAN_REPRODUCE_EXIT0'
