#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"
python -m compileall -q phys11_capacity.py test_phys11.py blind_style_audit.py verify_outputs.py
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/results" "$work/sources"
cp phys11_capacity.py test_phys11.py blind_style_audit.py verify_outputs.py EXPECTED_OUTPUT_SHA256.json "$work/"
cp sources/PR135_ORIGINAL_SOURCE.zip "$work/sources/PR135_ORIGINAL_SOURCE.zip"
python "$work/phys11_capacity.py" --parent-zip "$work/sources/PR135_ORIGINAL_SOURCE.zip" --out "$work/results" > "$work/GENERATED_SUMMARY.json"
python "$work/verify_outputs.py" "$work/results"
(cd "$work" && python -m unittest -q test_phys11)
(cd "$work" && python -O -m unittest -q test_phys11)
(cd "$work" && python blind_style_audit.py > "$work/BLIND_STYLE_AUDIT_RESULT.json")
echo 'PHYS11 CLEAN_RESTORE, NORMAL, OPTIMIZED, BLIND_STYLE_SAME_MODEL, OUTPUT_BYTES: PASS'
