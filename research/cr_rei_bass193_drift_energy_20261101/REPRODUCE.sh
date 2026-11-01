#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest -v test_reservoir
python3 -O -m unittest -v test_reservoir
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
python3 reservoir.py --out "$scratch" >/dev/null
cmp "$scratch/BASS193_H_HPLUS_DRIFT_ENERGY_192.csv" results/BASS193_H_HPLUS_DRIFT_ENERGY_192.csv
cmp "$scratch/SUMMARY.json" results/SUMMARY.json
sha256sum -c EXPECTED_OUTPUT.sha256
echo 'REPRODUCTION_PASS_SCOPED'
