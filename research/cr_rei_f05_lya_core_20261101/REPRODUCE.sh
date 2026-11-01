#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SOURCE="${REI_F05_OWNER_PREVIEW:-/home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101/primary/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz}"
test -f "$SOURCE"
export REI_F05_OWNER_PREVIEW="$SOURCE"
python3 -m unittest -q test_lya_f05_opacity
python3 -O -m unittest -q test_lya_f05_opacity
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT
python3 lya_f05_opacity.py --input "$SOURCE" --out "$SCRATCH" >/dev/null
cmp "$SCRATCH/REI_F05_HI_LYA_TO_THOMSON_46080.csv.gz" REI_F05_HI_LYA_TO_THOMSON_46080.csv.gz
cmp "$SCRATCH/RESULT.json" RESULT.json
sha256sum -c EXPECTED_OUTPUT.sha256
sha256sum -c MANIFEST.sha256
echo 'SOURCE_SCOPED_REI_F05_LYA_VOIGT_CAPACITY_REPRODUCTION_PASS'
