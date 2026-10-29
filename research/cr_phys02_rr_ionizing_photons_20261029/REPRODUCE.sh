#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
source_zip="${CR_PR110_SOURCE:-$here/BASS_CR_LOW_BIRTH_SOURCE_20261027_2eed7ef835c5.zip}"
if [[ ! -f "$source_zip" ]]; then echo "SOURCE input missing: $source_zip" >&2; exit 2; fi
export CR_PR110_SOURCE="$source_zip"
python "$here/cr_ionizing_rr.py" --source "$source_zip" --out "$here/results"
PYTHONPATH="$here" python -m unittest discover -s "$here" -p 'test_cr_photon.py' -q
PYTHONPATH="$here" python -O -m unittest discover -s "$here" -p 'test_cr_photon.py' -q
python "$here/independent_reference.py" --source "$source_zip" --out "$here/results/INDEPENDENT_DECIMAL80.json"
python "$here/plot_photons.py"
