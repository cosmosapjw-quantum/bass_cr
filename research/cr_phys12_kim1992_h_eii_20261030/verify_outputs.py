#!/usr/bin/env python3
"""Exact deterministic output readback, not scientific independent review."""
import hashlib,sys,json,pathlib
base=pathlib.Path(__file__).resolve().parent
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'results'
w=json.loads((base/'EXPECTED_OUTPUT_SHA256.json').read_text())
for name,hexd in w['outputs'].items():
   data=(root/name).read_bytes()
   got=hashlib.sha256(data).hexdigest()
   if got!=hexd:raise RuntimeError(f'{name} BAD_SHA {got} expected {hexd}')
print('OUTPUT_SHA256',len(w['outputs']),'/',len(w['outputs']),'PASS')
