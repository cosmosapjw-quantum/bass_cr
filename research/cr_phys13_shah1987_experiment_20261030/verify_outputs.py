#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=root/'results');a=p.parse_args()
expected=json.loads((root/'EXPECTED_OUTPUT_SHA256.json').read_text())
for name,h in expected.items():
    f=a.out/name
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise SystemExit('OUTPUT_BYTES_FAIL:'+name)
print('OUTPUT_SHA256_REPLAY',len(expected),'/',len(expected),'PASS')
