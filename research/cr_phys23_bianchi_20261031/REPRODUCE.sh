#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python phys23.py
python -m unittest test_phys23.py -q
python -O -m unittest test_phys23.py -q
python plot_science.py
