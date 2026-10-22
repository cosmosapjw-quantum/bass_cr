#!/usr/bin/env python3
"""Verify or create-only restore C22B delivery from the same verified memory bytes.

No scientific model is imported, and no ODE, RHS or analysis is executed.
Use the separate final authority's ZIP SHA256 and size for transport verification.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(path, expected_sha256=None, expected_size=None, restore_root=None):
    raw=Path(path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if expected_sha256 and digest!=expected_sha256:raise ValueError('ZIP_SHA256_MISMATCH')
    if expected_size is not None and len(raw)!=expected_size:raise ValueError('ZIP_SIZE_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('DUPLICATE_ARCHIVE_NAME')
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if p.is_absolute() or any(x in ('..','.') for x in p.parts) or '\\' in info.filename or info.is_dir():raise ValueError('UNSAFE_ARCHIVE_NAME')
            if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('SYMLINK_FORBIDDEN')
        if z.testzip() is not None:raise ValueError('CRC_FAILED')
        manifest=json.loads(z.read('MANIFEST.json'))
        rows=manifest['files']
        if len({x['path'] for x in rows})!=len(rows):raise ValueError('DUPLICATE_MANIFEST_PATH')
        if set(names)!={'MANIFEST.json',*(x['path'] for x in rows)}:raise ValueError('MEMBER_SET_MISMATCH')
        verified={}
        for row in rows:
            data=z.read(row['path'])
            if len(data)!=row['size_bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('MEMBER_HASH_OR_SIZE_FAILED:'+row['path'])
            verified[row['path']]=data
        if restore_root is not None:
            dest=Path(restore_root).resolve();dest.mkdir(parents=True,exist_ok=False)
            # Extraction uses only the memory bytes already verified above.
            for name,data in verified.items():
                path=dest.joinpath(*PurePosixPath(name).parts);path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('xb') as f:f.write(data)
            with (dest/'MANIFEST.json').open('xb') as f:f.write(z.read('MANIFEST.json'))
    return {'status':'PASS','path':str(Path(path).resolve()) if restore_root is None else str(Path(restore_root).resolve()),
        'size_bytes':len(raw),'sha256':digest,'members':len(names),'payload_files':len(rows),
        'CRC':'PASS','all_member_size_SHA256':'PASS','source_identity_sha256':manifest['execution_source_identity'],
        'restore':'CREATE_ONLY_SAME_VERIFIED_MEMORY_BYTES' if restore_root is not None else 'NOT_REQUESTED',
        'old_ODE_runs':0,'new_ODE_runs':0,'global_error_bound':None}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('zip',type=Path)
    p.add_argument('--expected-sha256');p.add_argument('--expected-size',type=int);p.add_argument('--restore-root',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.zip,a.expected_sha256,a.expected_size,a.restore_root),indent=2))
