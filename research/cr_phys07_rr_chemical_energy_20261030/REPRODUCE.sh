#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SOURCE="${1:-sources/PR131_ORIGINAL_SOURCE.zip}"
python -m unittest discover -s . -p 'test_energy_transfer.py' -v > results/TEST_NORMAL.log 2>&1
python -O -m unittest discover -s . -p 'test_energy_transfer.py' -v > results/TEST_OPTIMIZED.log 2>&1
python -m compileall -q energy_transfer.py independent_mp.py test_energy_transfer.py plot_transfer.py
python energy_transfer.py --source-zip "$SOURCE" --out results > results/STDOUT.json
python independent_mp.py > results/MP80_STDOUT.json
python plot_transfer.py
printf 'CR_PHYS07_SOURCE_LOCKED_REPLAY_PASS\n'
