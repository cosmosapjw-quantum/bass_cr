#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
PY="${REI_F05_PYTHON:-/home/cosmosapjw/archives/rec_f05_accepted_trajectory_20261102/pinned_env/bin/python}"
OWNER="${REI_F05_REPO:-/home/cosmosapjw/worktrees/rei-f05-photon-moment-volterra-20261101}"
REC="${REC195_SOURCE_ZIP:-/home/cosmosapjw/research_backups/rec_bianchi/REC195_ORIGINAL_F05_ACCEPTED_4EPOCH_SOURCE_FULL_20261102.zip}"
echo "ORIGINAL REI F05 MPRK22 H CHEMISTRY: source read-only, CR-OFF"
"$PY" -m unittest -q test_mprk_effective_h
"$PY" -O -m unittest -q test_mprk_effective_h
sha256sum -c EXPECTED_OUTPUT.sha256
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
"$PY" mprk_effective_h.py --rei-repo "$OWNER" --rec195-zip "$REC" --out "$scratch/replay" > "$scratch/replay.stdout"
(cd "$scratch/replay" && sha256sum -c "$HERE/EXPECTED_OUTPUT.sha256")
sha256sum -c MANIFEST.sha256
echo "ORIGINAL NINE MAPS, MPRK SOURCE RECOMPUTE BYTE IDENTITY PASS; REI 28/88; WORKING 33/88; FAST 4/7; BASS_CR 0/3, ALL DELTA0"
