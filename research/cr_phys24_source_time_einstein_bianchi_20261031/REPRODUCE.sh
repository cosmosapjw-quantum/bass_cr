#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 phys24.py
python3 -m unittest test_phys24.py -q
python3 -O -m unittest test_phys24.py -q
python3 plot_science.py
echo "PHYS24_LOCAL_REPRO_COMPLETE"
