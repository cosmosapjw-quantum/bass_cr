#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$ROOT"
python -m compileall -q neutral_response.py test_neutral_response.py independent_mp.py plot_susceptibility.py
python -m unittest -q test_neutral_response
python -O -m unittest -q test_neutral_response
python neutral_response.py --source-zip "$ROOT/sources/PR133_ORIGINAL_SOURCE.zip" --out "$TMP" > "$TMP/STDOUT.json"
python independent_mp.py --out "$TMP/MP70.json" > "$TMP/MP70_STDOUT.json"
python - "$ROOT" "$TMP" <<'PY'
import hashlib, json, pathlib, sys
root=pathlib.Path(sys.argv[1]);tmp=pathlib.Path(sys.argv[2]);want=json.loads((root/'EXPECTED_OUTPUT_SHA256.json').read_text())
for f,digest in want.items():
 got=hashlib.sha256((tmp/f).read_bytes()).hexdigest()
 if got!=digest:raise SystemExit(f'OUTPUT_REPLAY_SHA256_MISMATCH: {f}: {got} vs {digest}')
print('OUTPUT_REPLAY',len(want),'of',len(want),'byte-exact')
PY
