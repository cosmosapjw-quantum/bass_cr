import hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[2]
PINS=json.loads((HERE/'UPSTREAM_PINS.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_upstream_files_match_frozen_tp2b_bytes():
    for row in PINS['files']:
        assert digest(REPO/row['path'])==row['sha256']
