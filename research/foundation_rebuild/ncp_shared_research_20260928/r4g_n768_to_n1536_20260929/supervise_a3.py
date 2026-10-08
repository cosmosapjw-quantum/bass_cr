#!/usr/bin/env python3
"""Own one dedicated A3 fill-only process group and enforce its deadline."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zipfile


def _exists(pgid: int) -> bool:
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==pgid and fields[0] not in ('Z','X'):
                return True
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            continue
    return False


def _terminate_group(pgid: int, grace: int) -> dict:
    result = {'term_sent': False, 'kill_sent': False, 'group_exited': True}
    if not _exists(pgid):
        return result
    os.killpg(pgid, signal.SIGTERM)
    result['term_sent'] = True
    until = time.monotonic() + grace
    while _exists(pgid) and time.monotonic() < until:
        time.sleep(0.2)
    if _exists(pgid):
        os.killpg(pgid, signal.SIGKILL)
        result['kill_sent'] = True
        until = time.monotonic() + 5
        while _exists(pgid) and time.monotonic() < until:
            time.sleep(0.2)
    result['group_exited'] = not _exists(pgid)
    return result


def _sha(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def _package(out: Path, receipt: dict) -> dict | None:
    if not out.is_dir():
        return None
    with (out/'SUPERVISOR_RECEIPT.json').open('x') as f:
        json.dump(receipt,f,indent=2,allow_nan=False)
        f.flush();os.fsync(f.fileno())
    files={}
    for path in sorted(out.rglob('*')):
        if path.is_file():
            files[str(path.relative_to(out))]={'bytes':path.stat().st_size,
                                               'sha256':_sha(path)}
    with (out/'MANIFEST.json').open('x') as f:
        json.dump(files,f,indent=2,allow_nan=False)
        f.flush();os.fsync(f.fileno())
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                z.write(path,str(path.relative_to(out)))
    return {'path':str(archive),'bytes':archive.stat().st_size,
            'sha256':_sha(archive)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deadline-unix', type=float, required=True)
    p.add_argument('--grace-seconds', type=int, required=True)
    p.add_argument('--receipt', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args(argv)
    if (os.environ.get('ALLOW_NEW_NATIVE_R4M') != 'YES_I_AUTHORIZE_A3_FILL_ONLY'
        or not 1 <= args.grace_seconds <= 120
        or time.time() >= args.deadline_unix):
        raise ValueError('explicit migration approval/deadline/grace required')
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        raise ValueError('child command required')
    receipt_path = Path(args.receipt)
    if receipt_path.exists():
        raise FileExistsError('supervisor receipt already exists')
    child = subprocess.Popen(command, start_new_session=True)
    pgid = child.pid
    start = time.time()
    stop_requested = False

    def handler(signum, frame):
        nonlocal stop_requested
        stop_requested = True

    old_term = signal.signal(signal.SIGTERM, handler)
    old_int = signal.signal(signal.SIGINT, handler)
    termination = {'term_sent': False, 'kill_sent': False, 'group_exited': True}
    try:
        while child.poll() is None and not stop_requested and time.time() < args.deadline_unix:
            time.sleep(0.5)
        timed_out = time.time() >= args.deadline_unix
        if child.poll() is None or _exists(pgid):
            termination = _terminate_group(pgid, args.grace_seconds)
        status = child.wait()
        if _exists(pgid):
            termination = _terminate_group(pgid, args.grace_seconds)
        record = {'schema':'BASS_R4M_A3_DEDICATED_GROUP_SUPERVISOR_V1',
                  'child_pid':child.pid,'process_group':pgid,
                  'started_unix':start,'ended_unix':time.time(),
                  'deadline_unix':args.deadline_unix,
                  'grace_seconds':args.grace_seconds,
                  'deadline_reached':timed_out,'external_stop_requested':stop_requested,
                  'child_exit_status':status,'termination':termination,
                  'descendants_exited':not _exists(pgid)}
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        with receipt_path.open('x') as f:
            json.dump(record,f,indent=2,allow_nan=False)
            f.flush();os.fsync(f.fileno())
        archive=_package(Path(args.out),record)
        if archive is not None:
            with Path(str(args.out)+'_ARCHIVE_RECEIPT.json').open('x') as f:
                json.dump(archive,f,indent=2,allow_nan=False)
                f.flush();os.fsync(f.fileno())
        return status if not timed_out and not stop_requested else 124
    finally:
        signal.signal(signal.SIGTERM,old_term)
        signal.signal(signal.SIGINT,old_int)


if __name__ == '__main__':
    raise SystemExit(main())
