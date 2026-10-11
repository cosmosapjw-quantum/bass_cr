#!/usr/bin/env python3
"""Watchdog wrapper and separately timed complete evidence collection.

Collection is allowed after any failure or exhausted 900s command deadline.
The collector uses stdlib and never executes a generator or adopts old approval.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid
import zipfile

from qualify_parallel import (DEFAULT_ROOT,H_REL,READY_REL,Hold,append_durable,cleanup_groups,
                             file_identity,safe_relative,sha,utc,write_new)


def collect(root,run,out,ready_path=READY_REL,external_logs=None):
    begun=time.monotonic();started=utc();root=Path(root).resolve();run=Path(run).resolve();out=Path(out).resolve()
    if not run.is_dir():raise Hold('RUN_DIRECTORY_MISSING',str(run))
    if out.is_relative_to(run) or out.is_relative_to(root):raise Hold('RETURN_MUST_BE_OUTSIDE_RUN_AND_SOURCE')
    out.mkdir(parents=True,exist_ok=True)
    archive=out/('CR_PHYS02H_NCP_RETURN_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex[:12]+'.zip')
    payload={};missing=[];mismatches=[];expected={}
    def add(name,path,pin=None):
        path=Path(path)
        if path.is_symlink() or not path.is_file():
            missing.append(dict(name=name,path=str(path),reason='MISSING_OR_SYMLINK'));return
        if name in payload and payload[name]!=path:raise Hold('COLLECTION_DUPLICATE_PATH',name)
        payload[name]=path
        if pin:
            expected[name]=pin
            if sha(path)!=pin['sha256'] or ('bytes' in pin and path.stat().st_size!=pin['bytes']):
                mismatches.append(dict(name=name,expected=pin,observed=file_identity(path)))
    for path in sorted(run.rglob('*')):
        if path.is_symlink():missing.append(dict(path=str(path),reason='SYMLINK_NOT_FOLLOWED'))
        elif path.is_file():add('run/'+path.relative_to(run).as_posix(),path)
    start_path=run/'START.json'
    binding=json.loads(start_path.read_text()).get('source_binding') if start_path.exists() else None
    if binding:
        for group in ('execution_files','input_files','dependency_files'):
            for name,pin in binding[group].items():add('source/'+name,safe_relative(root,name),pin)
        for group in ('execution_manifest','input_manifest','independent_review'):
            pin=binding[group];add('source/'+pin['path'],safe_relative(root,pin['path']),pin)
        add('source/'+binding['ready_path'],safe_relative(root,binding['ready_path']),binding['ready'])
    else:
        # Failed admission remains collectable. Use declared manifests only as
        # expected identity inventory, never as proof of scientific admission.
        ready=safe_relative(root,ready_path)
        if ready.is_file():
            add('source/'+ready_path,ready)
            data=json.loads(ready.read_text())
            for group in ('execution_manifest','input_manifest','independent_review'):
                pin=data.get(group,{})
                if not isinstance(pin,dict) or not pin.get('path'):continue
                path=safe_relative(root,pin['path']);add('source/'+pin['path'],path,pin)
                if group!='independent_review' and path.is_file():
                    manifest=json.loads(path.read_text())
                    for name,item in manifest.get('files',{}).items():add('source/'+name,safe_relative(root,name),item)
        else:missing.append(dict(path=str(ready),reason='NCP_READY_MISSING_BEFORE_ADMISSION'))
        for subdirectory in ('ncp','state','inputs'):
            base=root/H_REL/subdirectory
            if base.exists():
                for path in sorted(base.rglob('*')):
                    if path.is_file() and not path.is_symlink():add('source/'+path.relative_to(root).as_posix(),path)
    for base in external_logs or ():
        base=Path(base)
        for path in sorted(base.rglob('*')):
            if path.is_file() and not path.is_symlink():add('wrapper/'+base.name+'/'+path.relative_to(base).as_posix(),path)
    inventory={name:file_identity(path) for name,path in payload.items()}
    manifest=dict(schema='cr-phys02h-ncp-complete-return.v1',path_basis='archive-root',files=inventory,
       expected_source_identities=expected,missing=missing,source_identity_mismatches=mismatches,
       collection_status='COMPLETE_OBSERVED_PAYLOAD' if not missing and not mismatches else 'PARTIAL_OR_MISMATCHED_EVIDENCE_PRESERVED',
       qualification_status='INDEPENDENT_FINAL_REVIEW_REQUIRED',
       raw_values_included=sorted(name for name in payload if name.endswith('.npy')),
       collection_start_utc=started,science_deadline_extended=False)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as bundle:
        for name,path in sorted(payload.items()):bundle.write(path,name)
        bundle.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    receipt=dict(archive=str(archive),**file_identity(archive),collection_start_utc=started,
          collection_end_utc=utc(),collection_wall_s=time.monotonic()-begun,
          science_execution_time_included=False,automatic_retry=0,
          payload_files=len(payload),raw_value_files=len(manifest['raw_values_included']),
          missing=missing,source_identity_mismatches=mismatches,status=manifest['collection_status'])
    write_new(archive.with_suffix('.COLLECTION_RECEIPT.json'),receipt)
    return receipt


def execute_and_collect(root,run,out,ready_path=READY_REL,review=None):
    entered=time.monotonic();root=Path(root).resolve();run=Path(run);out=Path(out).resolve()
    if not run.is_absolute() or run.exists():raise Hold('FRESH_ABSOLUTE_RUN_REQUIRED',str(run))
    if out.is_relative_to(root) or out.is_relative_to(run):raise Hold('OUTSIDE_SOURCE_RETURN_REQUIRED')
    out.mkdir(parents=True,exist_ok=True)
    logs=out/('LAUNCH_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex[:12])
    logs.mkdir(exist_ok=False)
    command=[sys.executable,str(root/H_REL/'ncp/qualify_parallel.py'),'--execute','--source-root',str(root),
             '--run',str(run),'--ready',ready_path]
    if review:command+=['--review',review]
    write_new(logs/'WRAPPER_START.json',dict(command=command,utc=utc(),whole_command_wall_s=900,automatic_retry=0))
    timed_out=False;process=None;signal_received=None
    previous={}
    def interrupted(signum,frame):
        nonlocal signal_received
        signal_received=signum
        raise Hold('WRAPPER_INTERRUPTED',signum)
    for signum in (signal.SIGTERM,signal.SIGINT):previous[signum]=signal.signal(signum,interrupted)
    with (logs/'COMMAND_STDOUT.txt').open('xb') as stdout,(logs/'COMMAND_STDERR.txt').open('xb') as stderr:
        try:
            process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True)
            while process.poll() is None:
                remaining=900-(time.monotonic()-entered)
                if remaining<=0:timed_out=True;break
                time.sleep(min(.25,remaining))
        except BaseException as error:
            write_new(logs/'WRAPPER_FIRST_FAILURE.json',dict(utc=utc(),error=repr(error),signal=signal_received))
        finally:
            if process is not None and process.poll() is None:
                # SIGTERM lets the source-pinned root clean its separately owned
                # model process groups. The fallback also kills every logged group.
                process.terminate()
                try:process.wait(timeout=8)
                except subprocess.TimeoutExpired:cleanup_groups([process])
                events=run/'PROCESS_EVENTS.jsonl'
                if events.exists():
                    for line in events.read_text().splitlines():
                        item=json.loads(line);group=item.get('process_group')
                        if type(group) is int:
                            try:os.killpg(group,signal.SIGKILL)
                            except ProcessLookupError:pass
            for signum,handler in previous.items():signal.signal(signum,handler)
    actual_exit=process.returncode if process is not None else 1
    write_new(logs/'WRAPPER_ACTUAL_EXIT.json',dict(utc=utc(),actual_exit=actual_exit,
        watchdog_timeout=timed_out,command_wall_including_cleanup_s=time.monotonic()-entered,
        automatic_retry=0,collection_not_started=True))
    if not run.exists():
        return dict(actual_exit=actual_exit,watchdog_timeout=timed_out,status='COMMAND_FAILED_BEFORE_RUN_CREATION',
                    wrapper_logs=str(logs),collection='RUN_DIRECTORY_MISSING')
    returned=collect(root,run,out,ready_path,[logs])
    return dict(actual_exit=actual_exit,watchdog_timeout=timed_out,return_bundle=returned)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',action='store_true');mode.add_argument('--execute',action='store_true')
    mode.add_argument('--collect',action='store_true')
    parser.add_argument('--source-root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path)
    parser.add_argument('--ready',default=READY_REL);parser.add_argument('--review')
    args=parser.parse_args()
    if args.plan:
        from qualify_parallel import plan
        result=plan(args.source_root,args.run.parent,args.ready,args.review)
    elif args.collect:
        if args.out is None:parser.error('--out required for collection')
        result=collect(args.source_root,args.run,args.out,args.ready)
    else:
        if args.out is None:parser.error('--out required for execution and collection')
        result=execute_and_collect(args.source_root,args.run,args.out,args.ready,args.review)
    print(json.dumps(result,indent=2));return result.get('actual_exit',0)


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print(json.dumps(dict(status='OPERATIONAL_HOLD',error=repr(error))),file=sys.stderr);sys.exit(1)
