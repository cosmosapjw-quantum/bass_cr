#!/usr/bin/env bash
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D"
PY="${REI_F05_PYTHON:-/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/pinned_env/bin/python}"
OWNER="${REI_F05_REPO:-/home/cosmosapjw/worktrees/rei-f05-photon-moment-volterra-20261101}"
REC="${REC195_SOURCE_ZIP:-/home/cosmosapjw/research_backups/rec_bianchi/REC195_ORIGINAL_F05_ACCEPTED_4EPOCH_SOURCE_FULL_20261102.zip}"
echo "ORIGINAL REI F05 H CASE-B SOURCE-QUADRATURE: 26-event; READ-ONLY"
"$PY" -m unittest -q test_native_h_caseb
"$PY" -O -m unittest -q test_native_h_caseb
sha256sum -c EXPECTED_OUTPUT.sha256
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
"$PY" native_h_caseb.py --rei-repo "$OWNER" --rec195-zip "$REC" --out "$scratch/replay" > "$scratch/replay_stdout.log"
(cd "$scratch/replay" && sha256sum -c "$D/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo "ORIGINAL 9-MAP SOURCE REPLAY BYTE PASS; REI 28/88; WORKING 33/88; FAST 4/7; BASS_CR 0/3; ALL DELTA0"
