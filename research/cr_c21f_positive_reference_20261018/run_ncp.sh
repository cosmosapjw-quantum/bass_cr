#!/usr/bin/env bash
# Reuses immutable C21E native owner/transaction; changes only independent reference
# and preservation of independent failed/completed comparator lanes.
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PARENT=$(dirname "$HERE")/cr_c21e_event_native_20261018
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo 'usage: bash run_ncp.sh NEW_OUTPUT ALLOCATED_CPU [EXISTING_OWNER_REPO]' >&2; exit 2
fi
OUT=$(realpath -m "$1"); CPU="$2"
case "$CPU" in ''|*[!0-9]*) echo 'CPU must be an integer' >&2; exit 2;; esac
if [ "$CPU" -eq 55 ]; then echo 'Historical CPU55 is protected; select another allocated CPU' >&2; exit 2; fi
if [ -e "$OUT" ]; then echo 'Refusing existing output root' >&2; exit 2; fi
mkdir -p "$OUT"
trap 'code=$?; printf "exit_code=%s\n" "$code" > "$OUT/exit_code.txt"' EXIT
export PATH="$HOME/.cargo/bin:$PATH"
export PYTHONPATH="$HERE/src${PYTHONPATH:+:$PYTHONPATH}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
{ date -u -Is; hostname; nproc; free -h; uptime; ps -eo pid,psr,pcpu,rss,args --sort=-pcpu | head -15; } > "$OUT/resources.txt" || true
python - "$CPU" <<'PY'
import os,sys
import numpy,scipy,pytest
if int(sys.argv[1]) not in os.sched_getaffinity(0):raise SystemExit('CPU not in allocation')
print(numpy.__version__,scipy.__version__,pytest.__version__)
PY
taskset -c "$CPU" python -m pytest -q "$HERE/tests" -p no:cacheprovider > "$OUT/python_tests.log" 2>&1
if [ "$#" -eq 3 ]; then
 timeout --kill-after=10s 180s taskset -c "$CPU" bash "$PARENT/build_native.sh" "$OUT/build" "$3" > "$OUT/build.log" 2>&1
else
 timeout --kill-after=10s 180s taskset -c "$CPU" bash "$PARENT/build_native.sh" "$OUT/build" > "$OUT/build.log" 2>&1
fi
# No lane is silently retried, clipped or relabelled. A failed matrix is preserved
# while the independent second fixture still gets its explicitly requested run.
set +e
timeout --kill-after=10s 300s taskset -c "$CPU" python "$HERE/src/campaign.py" \
 --out "$OUT/common_ic" --micro native --native "$OUT/build/native_point" \
 --a0 .09 --dx .0001 --opacity-scale .001 --steps 8 16 32 64 --cpu "$CPU" \
 > "$OUT/common_ic_stdout.log" 2> "$OUT/common_ic_stderr.log"
A=$?;printf '%s\n' "$A" > "$OUT/common_ic_exit.txt"
timeout --kill-after=10s 300s taskset -c "$CPU" python "$HERE/src/campaign.py" \
 --out "$OUT/native_source" --micro native --native "$OUT/build/native_point" \
 --a0 .09 --dx .0001 --source native-centroid --source-subdivisions 4 \
 --steps 8 16 32 64 --cpu "$CPU" \
 > "$OUT/native_source_stdout.log" 2> "$OUT/native_source_stderr.log"
B=$?;printf '%s\n' "$B" > "$OUT/native_source_exit.txt"
set -e
python - "$OUT" "$A" "$B" <<'PY'
from pathlib import Path
import hashlib,json,sys
out=Path(sys.argv[1]); codes=list(map(int,sys.argv[2:]));files={}
for p in out.rglob('*'):
 if p.is_file() and 'build' not in p.relative_to(out).parts:
  files[str(p.relative_to(out))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
receipt={'status':'COMPLETE_SCOPED' if codes==[0,0] else 'PARTIAL_OR_FAILED',
         'matrix_exit_codes':codes,'files':files,
         'scope':'Original C21E native microphysics and discrete transaction; new positive continuous coordinate only.',
         'holds':['native full-driver equivalence','source-age/spectral/angular convergence','full EoR']}
(out/'RETURN_TO_CHATGPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
PY
if [ "$A" -ne 0 ] || [ "$B" -ne 0 ]; then exit 2; fi
