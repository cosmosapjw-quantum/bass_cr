#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c NPZ_SHA256.txt
CXX=${CXX:-g++}
"$CXX" -O2 -std=c++20 -Wall -Wextra -Werror prefix_ssp.cpp -o prefix_ssp
python -m unittest -q test_prefix
python -O -m unittest -q test_prefix
# Full-size end-to-end checks are opt-in, each run costs scientific CPU.
if [[ "${RUN_SOURCE:-0}" == 1 ]]; then python benchmark_source.py; fi
if [[ "${RUN_ADVERSARIAL:-0}" == 1 ]]; then python adversarial_bins.py; fi
if [[ "${RUN_PARENT_BENCH:-0}" == 1 ]]; then
  "$CXX" -O2 -std=c++20 potentials_batch.cpp -o potentials_batch
  python benchmark_parent_actual.py
fi
