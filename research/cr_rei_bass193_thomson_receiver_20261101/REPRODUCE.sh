#!/usr/bin/env bash
set -euo pipefail
: "${REI_SOURCE_ZIP:?Set REI_SOURCE_ZIP to original private source ZIP; do not substitute another source}"
cd "$(dirname "$0")"
python src/receiver_tau.py --source "$REI_SOURCE_ZIP" --out results --figures figures
python -m unittest discover -s tests -p 'test_receiver.py' -v
python -O -m unittest discover -s tests -p 'test_receiver.py' -v
printf '%s\n' 'BASS193_FINITE_WINDOW_RECEIVER_REPLAY_COMPLETE'
