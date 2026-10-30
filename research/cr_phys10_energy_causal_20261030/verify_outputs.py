#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent
e=json.loads((r/'EXPECTED_OUTPUT_SHA256.json').read_text())
for name,sha in e.items():
    actual=hashlib.sha256((r/'results'/name).read_bytes()).hexdigest()
    assert actual==sha,(name,sha,actual)
print(f'REPRODUCED {len(e)}/{len(e)} ORIGINAL OUTPUT SHA256 BYTE EXACT')
