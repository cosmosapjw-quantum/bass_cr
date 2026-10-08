#!/usr/bin/env python3
"""Stop only the reidentified serial Python child after migration approval."""
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

PARENT_COMMIT='4c2c0be5171c74a52b4a6e96b04c33fa00c62481'
PARENT_AUTH='R4C-N768-BRIDGE-20260929-A1'


def probe(pid: int) -> dict | None:
    root=Path('/proc')/str(pid)
    try:
        stat=(root/'stat').read_text().rsplit(')',1)[1].split()
        cmd=[x.decode(errors='replace') for x in (root/'cmdline').read_bytes().split(b'\0') if x]
        return {'pid':pid,'state':stat[0],'ppid':int(stat[1]),'pgid':int(stat[2]),
                'sid':int(stat[3]),'start_ticks':int(stat[19]),
                'cmdline':cmd,'cwd':str(root.joinpath('cwd').resolve()),
                'cgroup':(root/'cgroup').read_text().strip()}
    except (FileNotFoundError,ProcessLookupError):
        return None


def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def _ledger(out: Path) -> dict:
    path=out/'RAW_EVALUATION_LEDGER.jsonl'
    rows=[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    started=[r for r in rows if r.get('event')=='attempt_started']
    completed=[r for r in rows if r.get('event')=='attempt_completed']
    failed=[r for r in rows if r.get('event')=='attempt_failed']
    qdir=out/'runtime_queries'
    j={p.stem for p in qdir.glob('*.json')}
    n={p.stem for p in qdir.glob('*.npz')}
    partial=[p.name for p in qdir.glob('.partial_*')]
    return {'raw_started':len(started),'raw_completed':len(completed),
            'raw_failed':len(failed),'last_started':started[-1] if started else None,
            'committed_pair_filenames':len(j&n),
            'orphan_ids':sorted(j^n),'partial_files':sorted(partial)}


def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False)
        f.flush();os.fsync(f.fileno())


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--python-pid',type=int,required=True)
    p.add_argument('--start-ticks',type=int,required=True)
    p.add_argument('--supervisor-pid',type=int,required=True)
    p.add_argument('--pgid',type=int,required=True)
    p.add_argument('--parent-out',required=True)
    p.add_argument('--parent-auth-id',required=True)
    p.add_argument('--migration-auth-id',required=True)
    p.add_argument('--expected-commit',required=True)
    p.add_argument('--expected-tree',required=True)
    p.add_argument('--grace-seconds',type=int,required=True)
    p.add_argument('--receipt',required=True)
    args=p.parse_args(argv)
    if (os.environ.get('R4F_STOP_APPROVED')!='YES_ONE_CONTROLLED_STOP'
        or os.environ.get('ALLOW_NEW_NATIVE_R4F')!='YES_I_AUTHORIZE_MIGRATION'
        or args.parent_auth_id!=PARENT_AUTH
        or args.migration_auth_id==args.parent_auth_id
        or args.migration_auth_id!=os.environ.get('R4F_AUTHORIZATION_ID')
        or not 1<=args.grace_seconds<=120):
        raise PermissionError('fresh linked migration stop approval required')
    here=Path(__file__).resolve().parents[4]
    new_commit=subprocess.check_output(['git','-C',str(here),'rev-parse','HEAD'],text=True).strip()
    new_tree=subprocess.check_output(['git','-C',str(here),'rev-parse','HEAD^{tree}'],text=True).strip()
    if (new_commit!=args.expected_commit or new_tree!=args.expected_tree
        or subprocess.check_output(['git','-C',str(here),'status','--porcelain','--untracked-files=all'],text=True)):
        raise ValueError('migration implementation identity/cleanliness changed; no signal sent')
    receipt=Path(args.receipt)
    if receipt.exists():
        raise FileExistsError('stop receipt already exists')
    parent=Path(args.parent_out).resolve()
    consumed=json.loads((parent/'AUTHORIZATION_CONSUMED.json').read_text())
    if (consumed.get('authorization_id')!=args.parent_auth_id
        or consumed.get('pid')!=args.python_pid
        or Path(consumed.get('out','')).resolve()!=parent):
        raise ValueError('consumed parent authorization does not match target')
    before=probe(args.python_pid);supervisor=probe(args.supervisor_pid)
    if before is None or supervisor is None:
        raise ValueError('target or supervisor already gone; no signal sent')
    try:
        observed_commit=subprocess.check_output(['git','-C',before['cwd'],'rev-parse','HEAD'],text=True).strip()
        observed_tree=subprocess.check_output(['git','-C',before['cwd'],'rev-parse','HEAD^{tree}'],text=True).strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError('parent code identity unavailable; no signal sent') from exc
    if (observed_commit!=PARENT_COMMIT
        or observed_tree!='2e1a3175a7d20cf9c0218fb15f07f72d4afcb425'
        or before['start_ticks']!=args.start_ticks
        or before['ppid']!=args.supervisor_pid
        or before['pgid']!=args.pgid or supervisor['pgid']!=args.pgid
        or not any('continue_temporal.py' in x for x in before['cmdline'])
        or PARENT_COMMIT not in before['cmdline']
        or str(parent) not in before['cmdline']
        or not any(x.endswith('/timeout') or x=='timeout' for x in supervisor['cmdline'][:1])):
        raise ValueError('live exact process identity changed; no signal sent')
    if (parent/'RETURN_REPORT.json').exists():
        raise ValueError('parent already has final report; no planned stop sent')
    start_ledger=_ledger(parent)
    os.kill(args.python_pid,signal.SIGTERM)
    sent=time.time();kill_sent=False
    until=time.monotonic()+args.grace_seconds
    while time.monotonic()<until:
        live=probe(args.python_pid)
        if live is None or live['state']=='Z':
            break
        if live['start_ticks']!=args.start_ticks:
            raise ValueError('PID reused during stop; refuse further signal')
        time.sleep(0.2)
    live=probe(args.python_pid)
    if live is not None and live['state']!='Z':
        if live['start_ticks']!=args.start_ticks:
            raise ValueError('PID reused at grace boundary')
        if os.environ.get('R4F_KILL_AFTER_GRACE_APPROVED')!='YES_EXACT_CHILD_ONLY':
            raise TimeoutError('exact Python child survived grace; SIGKILL not approved')
        os.kill(args.python_pid,signal.SIGKILL)
        kill_sent=True
    until=time.monotonic()+10
    while time.monotonic()<until and (probe(args.python_pid) is not None or probe(args.supervisor_pid) is not None):
        time.sleep(0.2)
    after=_ledger(parent)
    report_path=parent/'RETURN_REPORT.json'
    report=json.loads(report_path.read_text()) if report_path.exists() else None
    parent_status_file=parent.parent/'EXIT_STATUS.txt'
    parent_exit=int(parent_status_file.read_text()) if parent_status_file.exists() else None
    result={'schema':'BASS_R4F_CONTROLLED_PARENT_STOP_V1',
            'classification':'PLANNED_SERIAL_TO_PARALLEL_MIGRATION',
            'parent_authorization_id':args.parent_auth_id,
            'migration_authorization_id':args.migration_auth_id,
            'python_pid':args.python_pid,'python_start_ticks':args.start_ticks,
            'supervisor_pid':args.supervisor_pid,'pgid':args.pgid,
            'python_before':before,'supervisor_before':supervisor,
            'term_sent_unix':sent,'grace_seconds':args.grace_seconds,
            'kill_after_grace_sent':kill_sent,
            'child_exited':probe(args.python_pid) is None,
            'supervisor_exited':probe(args.supervisor_pid) is None,
            'parent_exit_status':parent_exit,
            'parent_report':report,
            'parent_report_sha256':_sha(report_path) if report_path.exists() else None,
            'loss_ledger_before':start_ledger,'loss_ledger_after':after}
    if report is not None and report.get('first_failure',{}).get('type') not in ('InterruptedError',):
        result['classification']='PARENT_SCIENTIFIC_OR_RUNTIME_FAILURE_FIRST'
    _write(receipt,result)
    _write(receipt.with_name(receipt.stem+'_LOSS_LEDGER.json'),{
        'schema':'BASS_R4F_LOSS_LEDGER_V1',
        'before':start_ledger,'after':after,
        'unsaved_inflight_query_possible':True,
        'raw_attempts_may_exceed_committed_queries':True})
    if not result['child_exited'] or not result['supervisor_exited'] or result['classification']!='PLANNED_SERIAL_TO_PARALLEL_MIGRATION':
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
