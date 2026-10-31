#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest test_phys23.py -q
python -O -m unittest test_phys23.py -q
python phys23.py
python plot_science.py