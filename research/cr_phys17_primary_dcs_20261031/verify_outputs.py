#!/usr/bin/env python3
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
r=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT
expected=json.loads((ROOT/'EXPECTED_OUTPUT_SHA256.json').read_text())['members']
for path,m in expected.items():
 b=(r/path).read_bytes()
 assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'],('SHA_MISMATCH',path)
print('REPLAY_SHA256_PASS',len(expected),'/',len(expected))
