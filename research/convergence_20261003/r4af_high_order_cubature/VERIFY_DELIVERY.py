"""Verify delivered bytes only; no numerical routine is imported or executed."""
import sys,json,hashlib
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
manifest=json.loads((root/'MANIFEST.json').read_text());count=0
for x in manifest['files']:
    p=(root/x['path']).resolve()
    if root not in p.parents or not p.is_file():raise SystemExit('unsafe or absent path: '+x['path'])
    b=p.read_bytes()
    if len(b)!=x['bytes'] or hashlib.sha256(b).hexdigest()!=x['sha256']:raise SystemExit('identity mismatch: '+x['path'])
    count+=1
print(json.dumps({'status':'ALL_PAYLOAD_IDENTITIES_MATCH','files':count,'science_calls':0}))
