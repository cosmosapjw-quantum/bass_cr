#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
echo "SOURCE-LOCKED REI F05 PHYSICS PARTITION ONLY; NO REI MUTATION"
python3 -m unittest -q test_partition
python3 -O -m unittest -q test_partition
sha256sum -c EXPECTED_OUTPUT.sha256
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 partition.py --out "$tmp" > /dev/null
(cd "$tmp" && sha256sum -c "$HERE/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo "16/16 normal, 16/16 -O, deterministic original-source replay PASS; REI central 28/88, working 33/88, BASS-CR 0/3, all delta0"
