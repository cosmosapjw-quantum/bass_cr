#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SOURCE="${HK1980_SOURCE_ZIP:-/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip}"
test -f "$SOURCE"
python3 hk_primary_joint.py --source-zip "$SOURCE" >/dev/null
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 hk_angular_grid.py --source-zip "$SOURCE" --out "$tmp" >/dev/null
cmp "$tmp/HK1980_SOURCE_DCS_2E_2CHANNELS_768ANGLES.csv.gz" HK1980_SOURCE_DCS_2E_2CHANNELS_768ANGLES.csv.gz
cmp "$tmp/ANGULAR_SCIENCE_RESULT.json" ANGULAR_SCIENCE_RESULT.json
python3 -m unittest -q test_hk_primary_joint test_hk_angular_grid
python3 -O -m unittest -q test_hk_primary_joint test_hk_angular_grid
sha256sum -c EXPECTED_OUTPUT.sha256
sha256sum -c MANIFEST.sha256
echo 'SCOPED_QUANTUM_SOURCE_REPRODUCTION_PASS'
