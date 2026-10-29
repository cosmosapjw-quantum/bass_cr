#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c NPZ_SHA256.txt
command -v g++ >/dev/null
# Build only in the current writable directory, never in the immutable source archive.
g++ -std=c++20 -O2 -Wall -Wextra -Wconversion -Wshadow potentials_batch.cpp -o potentials_batch
g++ -std=c++20 -O2 -Wall -Wextra CR_GENERIC_POTENTIALS_20261029/potentials_ssp.cpp -o potentials_ssp
PYTHONPATH=. python -m unittest -q test_batch_bridge
PYTHONPATH=. python -O -m unittest -q test_batch_bridge
# Explicitly opt in to the expensive original source calculation:
if [[ "${1:-}" == "--original" ]];then PYTHONPATH=. python benchmark_batch.py; fi
if [[ "${1:-}" == "--synthetic" ]];then PYTHONPATH=. python benchmark_matched_synthetic.py; fi
