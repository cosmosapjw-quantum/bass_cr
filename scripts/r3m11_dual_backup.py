#!/usr/bin/env python3
"""Create-only upload with existing authorized rclone remotes and raw SHA readback.

No credentials are collected or printed. No remote is configured by this script.
Both destinations are required. A failed upload/readback is not a dual backup.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    h=hashlib.sha256();n=0
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b);n+=len(b)
    return h.hexdigest(),n


def remote_digest(path):
    with tempfile.TemporaryFile() as errfile:
        proc=subprocess.Popen(['rclone','cat',path],stdout=subprocess.PIPE,stderr=errfile)
        h=hashlib.sha256();n=0
        for b in iter(lambda:proc.stdout.read(4*1024*1024),b''):
            h.update(b);n+=len(b)
        code=proc.wait();errfile.seek(0)
        err=errfile.read().decode(errors='replace')
    if code:raise RuntimeError(f'remote readback failed ({code}): {err[-1500:]}')
    return h.hexdigest(),n


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--file',required=True);p.add_argument('--drive-remote',required=True)
    p.add_argument('--dropbox-remote',required=True);p.add_argument('--receipt',required=True)
    p.add_argument('--folder',default='BASS_DERIVATION_DOSSIERS_20260912')
    a=p.parse_args();source=Path(a.file).resolve();receipt=Path(a.receipt)
    if receipt.exists():raise FileExistsError('use a new detached receipt path')
    if not source.is_file():raise FileNotFoundError(source)
    if not shutil.which('rclone'):raise RuntimeError('rclone unavailable; no remote mutation performed')
    for r in [a.drive_remote,a.dropbox_remote]:
        if ':' not in r or '/' in r.split(':')[0] or not r.split(':')[0]:
            raise ValueError('provide existing rclone remote:path, never a local synchronized folder')
    if a.drive_remote==a.dropbox_remote:raise ValueError('two distinct provider destinations required')
    listing=subprocess.run(['rclone','listremotes','--long'],capture_output=True,text=True)
    if listing.returncode:raise RuntimeError('cannot verify remote provider types; no upload performed')
    types={}
    for line in listing.stdout.splitlines():
        fields=line.split()
        if len(fields)>=2:types[fields[0].rstrip(':')]=fields[1]
    if types.get(a.drive_remote.split(':')[0])!='drive' or types.get(a.dropbox_remote.split(':')[0])!='dropbox':
        raise ValueError('two raw remotes with verified drive/dropbox types are required; aliases/crypt are not silently treated as independent providers')
    sha,size=digest(source)
    result=dict(schema='R3M11_DUAL_RAW_BACKUP_V1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        artifact=dict(name=source.name,sha256=sha,bytes=size),providers={},dual_backup_complete=False)
    for provider,remote in [('google_drive',a.drive_remote),('dropbox',a.dropbox_remote)]:
        target=remote.rstrip('/')
        if not target.endswith(':'):target+='/'
        target+=a.folder.strip('/')+'/'+source.name
        status=dict(destination=target,status='PENDING')
        try:
            # --immutable refuses modification of an existing different file.
            cp=subprocess.run(['rclone','copyto','--immutable',str(source),target],capture_output=True,text=True)
            if cp.returncode:raise RuntimeError(f'copyto failed ({cp.returncode}): {cp.stderr[-1500:]}')
            remote_sha,remote_size=remote_digest(target)
            if (remote_sha,remote_size)!=(sha,size):raise RuntimeError('remote raw SHA/size mismatch')
            status.update(status='REMOTE_OBJECT_PRESENT_RAW_READBACK_VERIFIED',sha256=remote_sha,bytes=remote_size,
                          new_object_creation_claimed=False)
        except Exception as e:
            status.update(status='FAILED_OR_UNVERIFIED',error=str(e))
        result['providers'][provider]=status
        receipt.parent.mkdir(parents=True,exist_ok=True)
        receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    result['dual_backup_complete']=all(x['status']=='REMOTE_OBJECT_PRESENT_RAW_READBACK_VERIFIED' for x in result['providers'].values())
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['dual_backup_complete'] else 2

if __name__=='__main__':sys.exit(main())
