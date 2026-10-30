#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python phys10_energy.py --source-zip sources/PR134_ORIGINAL_SOURCE.zip --out results
python compare_parent.py
python -m unittest test_phys10 -v
python -O -m unittest test_phys10 -v
python -m compileall -q phys10_energy.py compare_parent.py test_phys10.py
python verify_outputs.py
