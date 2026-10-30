#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
expected=json.loads((r/'EXPECTED_OUTPUT_SHA256.json').read_text())['numeric_outputs']
for name,sha in expected.items():
    raw=(r/'results'/name).read_bytes()
    got=hashlib.sha256(raw).hexdigest()
    if got!=sha:raise ValueError(f'OUTPUT_HASH_DRIFT: {name}: {got} != {sha}')
print(f'REGENERATED_NUMERIC_BYTES: {len(expected)}/{len(expected)} PASS')
