"""Read-only SHA-256/size/path verification; never builds or runs research code."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path, PurePosixPath

def verify(root):
    root=Path(root).resolve()
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise ValueError('duplicate JSON key')
            d[k]=v
        return d
    m=json.loads((root/'RELEASE_MANIFEST.json').read_text(),object_pairs_hook=pairs)
    if m.get('schema')!='R4AJ_RELEASE_MANIFEST_V1' or not isinstance(m.get('files'),list):
        raise ValueError('manifest schema')
    seen=set()
    for e in m['files']:
        s=e.get('path');p=PurePosixPath(s) if isinstance(s,str) else None
        if p is None or not s or p.is_absolute() or '..' in p.parts or '\\' in s or s in seen or s=='RELEASE_MANIFEST.json':
            raise ValueError('invalid/duplicate manifest path')
        seen.add(s);f=root.joinpath(*p.parts)
        if any(x.is_symlink() for x in (f,*f.parents) if x!=root and x.is_relative_to(root)):
            raise ValueError('symlink in payload')
        if not f.is_file() or not f.resolve().is_relative_to(root):raise ValueError('missing or escaping payload: '+s)
        h=hashlib.sha256();n=0
        with f.open('rb') as fh:
            for b in iter(lambda:fh.read(1024*1024),b''):h.update(b);n+=len(b)
        if n!=e['bytes'] or h.hexdigest()!=e['sha256']:raise ValueError('payload identity mismatch: '+s)
    return {'status':'ALL_LISTED_RELEASE_PAYLOADS_SHA256_SIZE_MATCH', 'files':len(seen),
            'science_calls':0,'remote_restore_verified':False,
            'limitation':'verifies pinned payload bytes; not authenticity of the manifest or scientific correctness'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',nargs='?',default='.')
    a=p.parse_args()
    try:print(json.dumps(verify(a.root),sort_keys=True))
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(2)
