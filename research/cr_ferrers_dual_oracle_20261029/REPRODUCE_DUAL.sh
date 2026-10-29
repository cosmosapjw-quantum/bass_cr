#!/usr/bin/env bash
set -euo pipefail
# In the restored PR124 SOURCE tree after applying the child overlay.
cd "$(dirname "$0")"
sha256sum -c NPZ_SHA256.txt
${CXX:-g++} -O2 -std=c++20 -Wall -Wextra -Werror prefix_ssp.cpp -o prefix_ssp
python -m unittest -q test_prefix test_prefix_dual
python -O -m unittest -q test_prefix test_prefix_dual
python -m compileall -q prefix_bridge.py prefix_dual_oracle.py test_prefix_dual.py
if [[ "${RUN_LARGE:-0}" == 1 ]]; then python benchmark_dual_oracle.py && python benchmark_dual_oracle_repeat.py; fi
