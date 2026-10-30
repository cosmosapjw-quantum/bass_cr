#!/usr/bin/env bash
# Recompute new source-owned physical tables in a fresh scratch tree, 35+35 tests,
# exact numerical/figure output SHA identity. Does not modify packaged originals.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/cr_phys16_replay.XXXXXXXX")"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP"/{results,figures,sources}
cp "$ROOT"/{phys16_spectral.py,phys16_time_scatter.py,plot_science.py,test_phys16.py} "$TMP"/
cp "$ROOT/sources/PR140_PHYS15_SOURCE.zip" "$TMP/sources/"
python - "$TMP/sources/PR140_PHYS15_SOURCE.zip" <<'PY'
from pathlib import Path
from hashlib import sha256
import sys
p=Path(sys.argv[1]); b=p.read_bytes();assert len(b)==9325625
assert sha256(b).hexdigest()=="48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316"
print('IMMUTABLE_SOURCE_LOCK_PASS',p.stat().st_size)
PY
python "$TMP/phys16_spectral.py" --source "$TMP/sources/PR140_PHYS15_SOURCE.zip" --output "$TMP/results" > "$TMP/spectral.log"
python "$TMP/phys16_time_scatter.py" --source "$TMP/sources/PR140_PHYS15_SOURCE.zip" --output "$TMP/results" > "$TMP/first_scatter.log"
python "$TMP/plot_science.py" > "$TMP/figures.log"
(
 cd "$TMP"
 python -m unittest test_phys16 -q
 python -O -m unittest test_phys16 -q
)
python "$ROOT/verify_outputs.py" --root "$TMP" --expected "$ROOT/EXPECTED_OUTPUT_SHA256.json"
python - "$TMP/results/RESULT.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r['source_photons']==6400 and r['source_2p_qualified']==2066
assert r['central_DAG']=='28/88 DELTA0' and r['extension_DAG']=='0/3 DELTA0'
assert r['production']=='HOLD'
assert r['R06_distinct_author']=='NOT_RUN' and r['C09_distinct_author']=='NOT_RUN'
print('PHYS16_REPLAY_SCIENCE_PASS','first_scatter_earliest_BORN',r['time_ordered_first_scatter_integrals']['earliest:BORN_DIPOLE']['first_scatter_x16_lower_m3'])
PY
