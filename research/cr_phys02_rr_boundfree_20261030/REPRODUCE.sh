#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python rr_boundfree.py --source-zip BASS_CR_PHYS02_RR_IONIZING_PHOTON_SOURCE_20261029.zip --output results
python -m unittest -v test_boundfree
python -O -m unittest -v test_boundfree
python -m compileall -q rr_boundfree.py independent_reference.py test_boundfree.py validate_and_plot.py
python independent_reference.py
python validate_and_plot.py
