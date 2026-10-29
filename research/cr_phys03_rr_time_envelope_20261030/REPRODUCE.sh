#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PR125_SOURCE_ZIP="${1:?Provide byte-locked PR125 SOURCE ZIP from backup}"
python "$HERE/generate.py" --source-zip "$PR125_SOURCE_ZIP" --output "$HERE/results"
python -m unittest discover -s "$HERE" -p 'test_timeline.py' -v
python -O -m unittest discover -s "$HERE" -p 'test_timeline.py' -v
python "$HERE/independent_mp.py"
python -m compileall -q "$HERE/generate.py" "$HERE/test_timeline.py" "$HERE/independent_mp.py"
