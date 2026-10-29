#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
source_zip="${1:-$here/sources/PR129_ORIGINAL_SOURCE.zip}"
python "$here/window_ionization.py" --source-zip "$source_zip" --out "$here/results" > "$here/results/REPRODUCE_META.json"
PYTHONPATH="$here" python -m unittest discover -s "$here" -p 'test_window_ionization.py' -v
PYTHONPATH="$here" python -O -m unittest discover -s "$here" -p 'test_window_ionization.py' -v
PYTHONPATH="$here" python "$here/independent_mp.py"
python -m compileall -q "$here/window_ionization.py" "$here/test_window_ionization.py" "$here/independent_mp.py"
