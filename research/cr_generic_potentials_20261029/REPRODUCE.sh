#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_ZIP="${1:-$HERE/PR121_ORIGINAL_SOURCE_ZIP.zip}"
if [[ ! -f "$PARENT_ZIP" ]]; then echo "SOURCE_ARCHIVE_MISSING: $PARENT_ZIP" >&2;exit 1;fi
printf '%s  %s\n' '12c406744b9b33632ba2cdfaf0afa63da50d2f29bc452f939ddad3ad01a3a566' "$PARENT_ZIP" | sha256sum -c -
WORK="${BASS_CR_REPRO_WORK:-$(mktemp -d)}"
mkdir -p "$WORK/parent" "$WORK/build"
unzip -q "$PARENT_ZIP" -d "$WORK/parent"
SRC="$WORK/parent/CR_GENERIC_BUDGET_SSP_20261029"
[[ -d "$SRC" ]] || { echo 'BAD_PARENT_ARCHIVE_ROOT' >&2; exit 1; }
sha256sum "$SRC/ATTRIBUTION_ARRAYS.npz" | grep -q '^1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
"${CXX:-g++}" -std=c++20 -O2 -Wall -Wextra -Werror "$HERE/potentials_ssp.cpp" -o "$HERE/potentials_ssp"
export PYTHONPATH="$HERE:$SRC:${PYTHONPATH:-}"
python -m unittest -v test_potentials_bridge
if [[ "${RUN_PARENT:-0}" == "1" ]]; then python -m unittest -q test_native_budget test_generic_budget_flow; fi
python -O -m unittest -q test_potentials_bridge
if [[ "${RUN_OPT_PARENT:-0}" == "1" ]]; then python -O -m unittest -q test_native_budget test_generic_budget_flow; fi
if [[ "${RUN_LARGE:-0}" == "1" ]]; then
  python "$HERE/benchmark_native.py" "$SRC"
fi
printf '%s\n' 'EXACT_POTENTIALS_SCOPED_TESTS_PASS (full 3201 budget benchmarks only when RUN_LARGE=1)'