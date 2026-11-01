#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
echo "READ ORIGINAL OWNER, NO REI MUTATION; SOURCE-CONDITIONAL ONLY"
python3 -m unittest -q test_ehi2p_source
python3 -O -m unittest -q test_ehi2p_source
sha256sum -c EXPECTED_OUTPUT.sha256
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 ehi2p_source.py --out "$tmp" > /dev/null
(cd "$tmp" && sha256sum -c "$HERE/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo "SOURCE-SCOPED REPLAY_OK; 28/88 CENTRAL, 33/88 WORKING, 0/3 CR EXTENSION, ALL DELTA0"
