#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
source_zip="${1:-$here/sources/PR128_ORIGINAL_SOURCE.zip}"
python "$here/spectral_survival.py" --source-zip "$source_zip" --out "$here/results"
python -m unittest discover -s "$here" -p 'test_spectral_survival.py' -v
python -O -m unittest discover -s "$here" -p 'test_spectral_survival.py' -v
python "$here/independent_mp.py"
python -m compileall -q "$here/spectral_survival.py" "$here/test_spectral_survival.py" "$here/independent_mp.py"
