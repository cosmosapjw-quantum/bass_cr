#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
python -m compileall -q phys15_lya.py test_phys15.py blind_referee.py plot_science.py verify_outputs.py
python -m unittest test_phys15 -q >/tmp/phys15-test-normal.log
python -O -m unittest test_phys15 -q >/tmp/phys15-test-optimized.log
TEMP=$(mktemp -d); trap 'rm -rf "$TEMP"' EXIT
python phys15_lya.py --parent-source sources/PR139_ORIGINAL_SOURCE.zip --out "$TEMP/results" > "$TEMP/science-run.log"
python verify_outputs.py --results "$TEMP/results"
python blind_referee.py > "$TEMP/blind.log"
python plot_science.py >/dev/null
python - <<'PY'
from pathlib import Path
p=Path('figures'); fs=list(p.glob('PHYS15_*.png'))
assert len(fs)==3 and all(x.stat().st_size>5000 for x in fs)
print('Figures:',len(fs),'nonempty')
PY
cat /tmp/phys15-test-normal.log /tmp/phys15-test-optimized.log
printf '\nPHYS15 CLEAN REPRODUCE PASS\n'
