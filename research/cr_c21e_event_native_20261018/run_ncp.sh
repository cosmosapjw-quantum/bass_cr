#!/usr/bin/env bash
# User/operator supplies ONE currently allocated CPU. Does not launch in background.
# Checks historical protected CPU55 but does not assume other CPUs are idle.
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo 'usage: bash run_ncp.sh NEW_OUTPUT_ROOT ALLOCATED_CPU [EXISTING_OWNER_GIT_REPOSITORY]' >&2;exit 2
fi
OUT=$(realpath -m "$1");CPU="$2"
case "$CPU" in ''|*[!0-9]*) echo 'CPU must be an integer' >&2;exit 2;; esac
if [ "$CPU" -eq 55 ];then echo 'CPU55 was reserved by a separate campaign; choose another allocated CPU' >&2;exit 2;fi
if [ -e "$OUT" ];then echo 'Refusing existing output root' >&2;exit 2;fi
mkdir -p "$OUT"
trap 'code=$?; printf "exit_code=%s\n" "$code" > "$OUT/exit_code.txt"' EXIT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$HERE/src${PYTHONPATH:+:$PYTHONPATH}"
{ date -u -Is;hostname;uname -a;nproc;free -h;uptime;ps -eo pid,pcpu,rss,args --sort=-pcpu | head -12; } > "$OUT/resources.txt" || true
python - "$CPU" <<'PY'
import os,sys
cpu=int(sys.argv[1])
if cpu not in os.sched_getaffinity(0):raise SystemExit('CPU is outside allowed affinity')
import numpy,scipy,pytest
print('Required Python modules available',numpy.__version__,scipy.__version__,pytest.__version__)
PY
# Tests validate this implementation/protocol, not a native astrophysical run.
taskset -c "$CPU" python -m pytest -q "$HERE/tests" -p no:cacheprovider > "$OUT/portable_tests.log" 2>&1
if [ "$#" -eq 3 ];then
  timeout 180s taskset -c "$CPU" bash "$HERE/build_native.sh" "$OUT/build" "$3" > "$OUT/build.log" 2>&1
else
  timeout 180s taskset -c "$CPU" bash "$HERE/build_native.sh" "$OUT/build" > "$OUT/build.log" 2>&1
fi
# First common-IC bridge comparison uses the retained three-energy fixture.
# Full native rates are NOT replaced by the manufactured test provider.
timeout 300s taskset -c "$CPU" python "$HERE/src/run_experiment.py" \
 --out "$OUT/common_ic" --micro native --native "$OUT/build/native_point" \
 --a0 0.09 --dx .0001 --opacity-scale .001 --steps 8 16 32 64 --cpu "$CPU" \
 > "$OUT/common_ic_stdout.log" 2> "$OUT/common_ic_stderr.log"
# Next, use original native MD14 cell masses and proper density, physical opacity.
# 12 source cells, fixed GL2 births. Continuous spectral convergence not claimed.
timeout 300s taskset -c "$CPU" python "$HERE/src/run_experiment.py" \
 --out "$OUT/native_source" --micro native --native "$OUT/build/native_point" \
 --a0 0.09 --dx .0001 --source native-centroid --source-subdivisions 4 \
 --steps 8 16 32 64 --cpu "$CPU" \
 > "$OUT/native_source_stdout.log" 2> "$OUT/native_source_stderr.log"
python "$HERE/src/analyze_results.py" "$OUT/common_ic"
python "$HERE/src/analyze_results.py" "$OUT/native_source"
python - "$OUT" <<'PY'
from pathlib import Path
import hashlib,json,sys
out=Path(sys.argv[1]);root_files={}
for p in out.rglob('*'):
 if p.is_file() and 'build' not in p.relative_to(out).parts:
  root_files[str(p.relative_to(out))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
receipt={'status':'TWO_FIXED_NATIVE_MATRICES_COMPLETED','files':root_files,
 'scope':'original nonphoto native point kernel + new Python integrated-photo method; no complete production driver parity',
 'holds':['full source48','source birth quadrature convergence','spectral/angular refinement','global EoR','Bianchi','Case B']}
(out/'RETURN_TO_CHATGPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
PY
printf 'Completed bounded native matrices at %s\n' "$OUT"
