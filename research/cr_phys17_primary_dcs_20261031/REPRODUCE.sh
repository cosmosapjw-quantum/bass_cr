#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="$(mktemp -d -t cr_phys17_clean_XXXXXXXX)"
trap 'rm -rf "$RUN"' EXIT
mkdir -p "$RUN/sources" "$RUN/results" "$RUN/figures"
cp "$HERE"/*.py "$RUN/"
cp "$HERE/EXPECTED_OUTPUT_SHA256.json" "$RUN/"
cp "$HERE/sources/PR141_PHYS16_SOURCE.zip" "$RUN/sources/"
cd "$RUN"
python - <<'PY'
import hashlib,zipfile
from pathlib import Path
p=Path('sources/PR141_PHYS16_SOURCE.zip')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='3b316c595fc1b40109f39d91af92873ba5a215281040d70bcb177dd1ab74a7dc'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 pre='research/cr_phys16_lya_recoil_20261031/'
 for src,dst in [('sources/PR140_PHYS15_SOURCE.zip','sources/PR140_PHYS15_SOURCE.zip'),('results/SOURCE_EMISSION_PROFILES.npz','sources/PHYS16_SOURCE_EMISSION_PROFILES.npz'),('results/SOURCE_RECOIL_MODEL_CROSSWALK.csv','sources/PHYS16_SOURCE_RECOIL_MODEL_CROSSWALK.csv')]:
  Path(dst).write_bytes(z.read(pre+src))
print('EXACT_PARENT_SOURCE_RESTORED')
PY
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python primary_tables.py
python phys17_primary_dcs.py > phase1.log
python phys17_time_scatter.py > phase2.log
python plot_science.py
python -m unittest -q test_phys17
python -O -m unittest -q test_phys17
python verify_outputs.py "$RUN"
echo 'CR_PHYS17_CLEAN_REPLAY_PASS'
