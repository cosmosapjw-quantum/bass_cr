#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
v=json.loads((root/'EXPECTED_OUTPUT_SHA256.json').read_text())
results=Path(sys.argv[1]) if len(sys.argv)>1 else root/'results'
errors=[]
for name,checksum in v['outputs'].items():
    p=results/name
    if not p.exists():errors.append('MISSING:'+name);continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=checksum:errors.append('SHA256_MISMATCH:'+name+' '+got)
if errors:
    print('\n'.join(errors),file=sys.stderr)
    sys.exit(1)
print('OUTPUT_BYTES_PASS',len(v['outputs']))
