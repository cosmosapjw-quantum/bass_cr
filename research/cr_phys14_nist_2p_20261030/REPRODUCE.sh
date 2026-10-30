#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m compileall -q phys14_compete.py blind_referee.py test_phys14.py verify_outputs.py plot_science.py
python phys14_compete.py --source sources/PR138_ORIGINAL_SOURCE.zip --nist nist_h_2p_cross_sections.csv --out results > /dev/null
python -m unittest test_phys14 -q
python -O -m unittest test_phys14 -q
python blind_referee.py
python plot_science.py
python verify_outputs.py
