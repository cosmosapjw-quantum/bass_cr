#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export REI_F05_OWNER_REPO="${REI_F05_OWNER_REPO:-/home/cosmosapjw/worktrees/rei-f05-v2-versioned-owner-decision-20261101}"
export REI_F05_PREVIEW_CSV="${REI_F05_PREVIEW_CSV:-/home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101/primary/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz}"
export REI_F05_ORIGINAL_INCREMENT_CSV="${REI_F05_ORIGINAL_INCREMENT_CSV:-/home/cosmosapjw/archives/rei_f05_direct_interval_audit_20261101/primary/REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz}"
test -f "$REI_F05_PREVIEW_CSV"
test -f "$REI_F05_ORIGINAL_INCREMENT_CSV"
python3 -m unittest -q test_native_caseb_lya
python3 -O -m unittest -q test_native_caseb_lya
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 native_caseb_lya.py --preview "$REI_F05_PREVIEW_CSV" --increments "$REI_F05_ORIGINAL_INCREMENT_CSV" --out "$TMP" >/dev/null 2>/dev/null
cmp "$TMP/ORIGINAL_REI_F05_CASEB_LYA_RECOMB_46080.csv.gz" ORIGINAL_REI_F05_CASEB_LYA_RECOMB_46080.csv.gz
cmp "$TMP/RESULT.json" RESULT.json
sha256sum -c EXPECTED_OUTPUT.sha256
sha256sum -c MANIFEST.sha256
echo "F05_CASEB_ORIGINAL_SOURCE_REPLAY_PASS"
