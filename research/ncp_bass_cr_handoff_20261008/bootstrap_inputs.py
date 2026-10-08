#!/usr/bin/env python3
"""Stage SHA-pinned bass_cr inputs on NCP; no guessed source, no overwrites.

Downloads only from already user-owned Google Drive/Dropbox destinations (if
rclone is configured), or from a user-owned mirrored local input directory.
Never creates/changes sharing permissions; never claims upload or remote restore.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time
import zipfile

BASE = Path(__file__).resolve().parent
MANIFEST = BASE / "INPUTS.json"

def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as src:
        for block in iter(lambda: src.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def verify(path: Path, row: dict) -> None:
    if not path.is_file() or path.stat().st_size != row['size']:
        raise ValueError('FILE_MISSING_OR_SIZE_MISMATCH')
    if file_hash(path) != row['sha256']:
        raise ValueError('SHA256_MISMATCH')
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            key = PurePosixPath(member.filename)
            if key.is_absolute() or '..' in key.parts or '\\' in member.filename:
                raise ValueError('ZIP_PATH_UNSAFE')
            if ((member.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('ZIP_SYMLINK_FORBIDDEN')
        if archive.testzip() is not None:
            raise ValueError('ZIP_CRC_FAILED')

def run_copy(cmd: list[str], where: Path, label: str) -> bool:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=900, check=False)
    p = where / (label + '.json')
    p.write_text(json.dumps({'argv_redacted': ['rclone' if cmd[0]=='rclone' else cmd[0], 'copyto', '<configured remote>', '<temporary local file>'],
                            'exit':proc.returncode, 'stdout_tail':proc.stdout[-500:].decode('utf8','replace'),
                            'stderr_tail':proc.stderr[-1200:].decode('utf8','replace')},indent=2)+'\n')
    return proc.returncode==0

def configured_remotes() -> set[str]:
    if not shutil.which('rclone'): return set()
    p=subprocess.run(['rclone','listremotes'],capture_output=True,text=True,timeout=25)
    return set(v.strip() for v in p.stdout.splitlines()) if p.returncode==0 else set()

def read_inputs(out: Path, allow_network: bool, source_dir: Path | None) -> int:
    spec = json.loads(MANIFEST.read_text())
    specs = spec['packages']
    failures=out/'failures'; inputs=out/'inputs'
    failures.mkdir(exist_ok=True,parents=True); inputs.mkdir(exist_ok=True,parents=True)
    remotes=configured_remotes() if allow_network else set()
    drive=os.environ.get('NCP_GDRIVE_REMOTE','gdrive:').rstrip(':')+':'
    dropbox=os.environ.get('NCP_DROPBOX_REMOTE','dropbox:').rstrip(':')+':'
    receipt={'schema':'bass-cr.ncp.source-inventory.v1','created_epoch':time.time(),
             'source_manifest_sha256':file_hash(MANIFEST), 'items':{},'all_ready':False}
    for row in specs:
        name=row['name']; target=inputs/name
        entry={'name':name,'expected_sha256':row['sha256'],'status':'BLOCKED_INPUT','method':None}
        if target.exists():
            try: verify(target,row);entry.update(status='VERIFIED_EXISTING',method='local')
            except Exception as exc: entry['error']='EXISTING_INVALID_'+type(exc).__name__
        else:
            alternatives=[]
            if source_dir is not None:
                alternatives.append(('local',source_dir/name))
            if allow_network and dropbox in remotes:
                alternatives.append(('dropbox',[ 'rclone','copyto',dropbox+row['dropbox_path'].lstrip('/'),'{dst}']))
            if allow_network and drive in remotes:
                alternatives.append(('drive',[ 'rclone','copyto','--drive-root-folder-id',spec['drive_parent_id'],drive+name,'{dst}']))
            if allow_network and shutil.which('gdown'):
                alternatives.append(('gdown',['gdown','--id',row['drive_id'],'--output','{dst}']))
            for kind,loc in alternatives:
                tmp=inputs/(name+'.'+kind+'.partial')
                if tmp.exists(): tmp.rename(failures/(tmp.name+'.preexisting'))
                try:
                    if kind=='local':
                        if not loc.is_file():continue
                        shutil.copyfile(loc,tmp)
                    else:
                        if not run_copy([tmp.as_posix() if a=='{dst}' else a for a in loc],failures,name+'.'+kind):
                            continue
                    verify(tmp,row)
                    tmp.rename(target)
                    entry.update(status='VERIFIED_FRESH',method=kind)
                    break
                except Exception as exc:
                    entry['last_error']=type(exc).__name__
                    if tmp.exists():tmp.rename(failures/(tmp.name+'.failed'))
            if entry['status']=='BLOCKED_INPUT' and not alternatives:
                entry['last_error']='NO_LOCAL_COPY_OR_ACCESSIBLE_REMOTE_OR_PUBLIC_DOWNLOAD'
        receipt['items'][name]=entry
        receipt['all_ready']=all(v['status'].startswith('VERIFIED') for v in receipt['items'].values()) and len(receipt['items'])==len(specs)
        (out/'SOURCE_INVENTORY.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
        print(name,entry['status'],entry['method'] or '')
    return 0 if receipt['all_ready'] else 3

def safe_extract(out:Path) -> None:
    root=out/'extracted'
    if root.exists(): raise FileExistsError('EXTRACTION_ALREADY_EXISTS_CREATE_NEW_WORKDIR')
    root.mkdir()
    manifest=json.loads(MANIFEST.read_text())
    for row in manifest['packages']:
        target=root/row['name'].removesuffix('.zip')
        target.mkdir()
        p=out/'inputs'/row['name']
        verify(p,row)
        with zipfile.ZipFile(p) as z:
            if sum(x.file_size for x in z.infolist())>100_000_000:
                raise ValueError('ZIP_UNPACK_TOO_LARGE')
            z.extractall(target)

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--workdir',type=Path,required=True)
    cli.add_argument('--source-dir',type=Path,default=None,help='optional already mirrored input folder')
    cli.add_argument('--offline',action='store_true')
    cli.add_argument('--extract',action='store_true')
    cli.add_argument('--resume',action='store_true')
    args=cli.parse_args()
    if args.workdir.exists() and not args.resume:
        cli.error('WORKDIR_EXISTS: choose a fresh directory or --resume')
    args.workdir.mkdir(parents=True,exist_ok=True)
    status=read_inputs(args.workdir,not args.offline,args.source_dir)
    if status==0 and args.extract: safe_extract(args.workdir)
    sys.exit(status)
