#!/usr/bin/env python3
"""Verify a detached SHA-256 manifest without executing or mutating its payload."""
import argparse
import hashlib
from pathlib import Path

def verify(manifest):
    manifest=Path(manifest).resolve();root=manifest.parent;count=0
    for line in manifest.read_text().splitlines():
        if not line.strip():continue
        expected,relative=line.split('  ',1);path=(root/relative).resolve()
        if not path.is_relative_to(root):raise ValueError('manifest path escapes root')
        h=hashlib.sha256()
        with path.open('rb') as f:
            for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
        if h.hexdigest()!=expected:raise ValueError(f'hash mismatch: {relative}')
        count+=1
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');a=p.parse_args()
    print(f'{verify(a.manifest)} files SHA-256 verified')
