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
                             file_identity,kernel_process_identity,safe_relative,sha,utc,write_new)


def control_json(path,warnings,label):
    """Malformed control files remain original payload, never a collection gate."""
    path=Path(path)
    try:data=json.loads(path.read_text())
    except (OSError,UnicodeError,ValueError) as error:
        warnings.append(dict(code='MALFORMED_OR_UNREADABLE_CONTROL_JSON',label=label,path=str(path),error_type=type(error).__name__))
        return None
    if not isinstance(data,dict):
        warnings.append(dict(code='CONTROL_JSON_OBJECT_REQUIRED',label=label,path=str(path)))
        return None
    return data


def owned_session_groups(run,nonce,warnings):
    """Read only two generated marker keys; never expose full environments.

    The unpredictable per-launch marker and exact run path must match every
    live member of a same-UID session/group. Discovery covers a qualifier death
    between Popen and event append, without treating arbitrary event PIDs as
    ownership proof.
    """
    expected_nonce=('CR_PHYS02H_LAUNCH_NONCE='+nonce).encode()
    expected_run=('CR_PHYS02H_RUN_MARKER='+str(Path(run).resolve())).encode()
    sessions={};unreadable=set()
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            identity=kernel_process_identity(int(entry.name))
            if identity['uid']!=os.getuid() or identity['session_id']!=identity['process_group']:continue
            # Zombies cannot execute and no longer have a readable environment.
            stat=(entry/'stat').read_text();state=stat[stat.rfind(')')+2:].split()[0]
            if state=='Z':continue
            values=(entry/'environ').read_bytes().split(b'\0')
            marked=expected_nonce in values and expected_run in values
            sessions.setdefault(identity['process_group'],[]).append((identity,marked))
        except (FileNotFoundError,ProcessLookupError):continue
        except (OSError,ValueError,IndexError,StopIteration):
            try:unreadable.add(kernel_process_identity(int(entry.name))['process_group'])
            except (OSError,ValueError,IndexError,StopIteration):pass
    owned={}
    for group,members in sessions.items():
        if any(marked for _,marked in members):
            if group in unreadable or not all(marked for _,marked in members):
                warnings.append(dict(code='OWNED_SESSION_MEMBERSHIP_NOT_FULLY_VERIFIABLE',process_group=group))
                continue
            owned[group]=[identity for identity,_ in members]
    return owned


def cancel_owned_sessions(run,nonce,qualifier_pid=None,qualifier_start_ticks=None):
    """Cancel science first on every exit; qualifier grace is evidence-only."""
    begun=time.monotonic();warnings=[];events=Path(run)/'PROCESS_EVENTS.jsonl';declared=set()
    signaled=[]
    initial=owned_session_groups(run,nonce,warnings)
    for group,members in initial.items():
        try:os.killpg(group,signal.SIGTERM)
        except ProcessLookupError:continue
        except OSError as error:
            warnings.append(dict(code='OWNED_GROUP_SIGNAL_FAILED',process_group=group,error_type=type(error).__name__));continue
        signaled.append(dict(process_group=group,signal=signal.SIGTERM,
                      live_member_kernel_identities=members,ownership_verified=True))
    # Control parsing follows cancellation, so damaged or large metadata cannot
    # delay the first science-stop signal at the watchdog boundary.
    if events.exists():
        try:lines=events.read_text().splitlines()
        except (OSError,UnicodeError):
            warnings.append(dict(code='UNREADABLE_PROCESS_EVENTS',path=str(events)));lines=[]
        for number,line in enumerate(lines,1):
            try:item=json.loads(line)
            except ValueError:
                warnings.append(dict(code='MALFORMED_PROCESS_EVENT_JSON',line=number,path=str(events)));continue
            if not isinstance(item,dict):
                warnings.append(dict(code='PROCESS_EVENT_OBJECT_REQUIRED',line=number));continue
            group=item.get('process_group')
            if group is None:continue  # terminal exit events have no new session
            owner=item.get('ownership',{})
            valid=(type(group) is int and group>1 and isinstance(owner,dict)
                and owner.get('qualifier_pid')==qualifier_pid
                and owner.get('qualifier_start_ticks')==qualifier_start_ticks
                and owner.get('uid')==os.getuid() and owner.get('launch_nonce')==nonce
                and owner.get('run_directory')==str(Path(run).resolve()))
            if valid:declared.add(group)
            else:warnings.append(dict(code='UNVERIFIED_PROCESS_EVENT_OWNERSHIP',line=number,process_group=group if type(group) is int else None))
    for group in sorted(set(initial)-declared-({qualifier_pid} if qualifier_pid else set())):
        warnings.append(dict(code='OWNED_SESSION_DISCOVERED_WITHOUT_DURABLE_EVENT',process_group=group))
    time.sleep(.15)
    # Re-discovery closes the event-append race and a concurrent final spawn.
    # The qualifier gets a separate evidence-only grace after science groups
    # have already been stopped; it is not killed during this short stage.
    for group,members in owned_session_groups(run,nonce,warnings).items():
        if group==qualifier_pid:continue
        try:os.killpg(group,signal.SIGKILL)
        except ProcessLookupError:continue
        except OSError as error:
            warnings.append(dict(code='OWNED_GROUP_SIGNAL_FAILED',process_group=group,error_type=type(error).__name__));continue
        signaled.append(dict(process_group=group,signal=signal.SIGKILL,
                     live_member_kernel_identities=members,ownership_verified=True))
    remaining=owned_session_groups(run,nonce,warnings)
    return dict(utc=utc(),cancel_wall_s=time.monotonic()-begun,signaled=signaled,warnings=warnings,
          remaining_verified_live_owned_science_groups=sorted(set(remaining)-({qualifier_pid} if qualifier_pid else set())),
          qualifier_evidence_grace_group_present=qualifier_pid in remaining,
          scope='exact generated launch nonce/run marker, current UID and matching live session/group; no arbitrary PID kill',
          full_environment_values_recorded=False)


def collect(root,run,out,ready_path=READY_REL,external_logs=None):
    begun=time.monotonic();started=utc();root=Path(root).resolve();run=Path(run).resolve();out=Path(out).resolve()
    if not run.is_dir():raise Hold('RUN_DIRECTORY_MISSING',str(run))
    if out.is_relative_to(run) or out.is_relative_to(root):raise Hold('RETURN_MUST_BE_OUTSIDE_RUN_AND_SOURCE')
    out.mkdir(parents=True,exist_ok=True)
    archive=out/('CR_PHYS02H_NCP_RETURN_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex[:12]+'.zip')
    payload={};missing=[];mismatches=[];expected={};warnings=[]
    def add(name,path,pin=None):
        path=Path(path)
        if path.is_symlink() or not path.is_file():
            missing.append(dict(name=name,path=str(path),reason='MISSING_OR_SYMLINK'));return
        if name in payload and payload[name]!=path:raise Hold('COLLECTION_DUPLICATE_PATH',name)
        payload[name]=path
        if pin:
            if not isinstance(pin,dict) or not isinstance(pin.get('sha256'),str):
                warnings.append(dict(code='INVALID_COLLECTION_IDENTITY_RECORD',name=name));return
            expected[name]=pin
            if sha(path)!=pin['sha256'] or ('bytes' in pin and path.stat().st_size!=pin['bytes']):
                mismatches.append(dict(name=name,expected=pin,observed=file_identity(path)))
    for path in sorted(run.rglob('*')):
        if path.is_symlink():missing.append(dict(path=str(path),reason='SYMLINK_NOT_FOLLOWED'))
        elif path.is_file():add('run/'+path.relative_to(run).as_posix(),path)
    start_path=run/'START.json'
    start=control_json(start_path,warnings,'START') if start_path.exists() else None
    binding=start.get('source_binding') if start else None
    if binding is not None and (not isinstance(binding,dict) or
            any(not isinstance(binding.get(key),dict) for key in ('execution_files','input_files','dependency_files',
                'execution_manifest','input_manifest','independent_review','ready')) or
            not isinstance(binding.get('ready_path'),str)):
        warnings.append(dict(code='INVALID_START_SOURCE_BINDING',path=str(start_path)));binding=None
    def add_source(name,pin=None):
        try:path=safe_relative(root,name)
        except (Hold,TypeError,ValueError) as error:
            warnings.append(dict(code='UNSAFE_DECLARED_COLLECTION_SOURCE',error_type=type(error).__name__));return None
        add('source/'+name,path,pin);return path
    if binding:
        for group in ('execution_files','input_files','dependency_files'):
            for name,pin in binding[group].items():add_source(name,pin)
        for group in ('execution_manifest','input_manifest','independent_review'):
            pin=binding[group]
            if not isinstance(pin.get('path'),str):warnings.append(dict(code='INVALID_START_SOURCE_PATH',group=group));continue
            add_source(pin['path'],pin)
        add_source(binding['ready_path'],binding['ready'])
    else:
        # Failed admission remains collectable. Use declared manifests only as
        # expected identity inventory, never as proof of scientific admission.
        ready=add_source(ready_path)
        if ready is not None and ready.is_file():
            data=control_json(ready,warnings,'NCP_READY') or {}
            for group in ('execution_manifest','input_manifest','independent_review'):
                pin=data.get(group,{})
                if not isinstance(pin,dict) or not pin.get('path'):continue
                path=add_source(pin['path'],pin)
                if group!='independent_review' and path is not None and path.is_file():
                    manifest=control_json(path,warnings,group) or {}
                    files=manifest.get('files',{})
                    if not isinstance(files,dict):warnings.append(dict(code='INVALID_FALLBACK_MANIFEST_FILES',path=str(path)));continue
                    for name,item in files.items():add_source(name,item)
        else:missing.append(dict(path=str(ready),reason='NCP_READY_MISSING_BEFORE_ADMISSION'))
        for subdirectory in ('ncp','state','inputs','src','tests'):
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
       expected_source_identities=expected,missing=missing,source_identity_mismatches=mismatches,collection_warnings=warnings,
       source_binding_status='COLLECTION_DOES_NOT_ATTEST_SOURCE_ADMISSION',
       collection_status='COMPLETE_OBSERVED_PAYLOAD' if not missing and not mismatches and not warnings else 'PARTIAL_OR_MISMATCHED_EVIDENCE_PRESERVED',
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
          missing=missing,source_identity_mismatches=mismatches,collection_warnings=warnings,status=manifest['collection_status'])
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
    nonce=uuid.uuid4().hex
    write_new(logs/'WRAPPER_START.json',dict(command=command,utc=utc(),whole_command_wall_s=900,automatic_retry=0,
         launch_nonce=nonce,run_marker=str(run.resolve())))
    timed_out=False;process=None;signal_received=None;qualifier_identity=None;cleanup_records=[]
    previous={}
    def interrupted(signum,frame):
        nonlocal signal_received
        signal_received=signum
        raise Hold('WRAPPER_INTERRUPTED',signum)
    for signum in (signal.SIGTERM,signal.SIGINT):previous[signum]=signal.signal(signum,interrupted)
    with (logs/'COMMAND_STDOUT.txt').open('xb') as stdout,(logs/'COMMAND_STDERR.txt').open('xb') as stderr:
        try:
            environment=os.environ.copy();environment['CR_PHYS02H_WRAPPER_PID']=str(os.getpid())
            environment['CR_PHYS02H_LAUNCH_NONCE']=nonce;environment['CR_PHYS02H_RUN_MARKER']=str(run.resolve())
            process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True,env=environment)
            try:qualifier_identity=kernel_process_identity(process.pid)
            except (OSError,ValueError,StopIteration,IndexError):qualifier_identity=None
            while process.poll() is None:
                remaining=900-(time.monotonic()-entered)
                if remaining<=0:timed_out=True;break
                time.sleep(min(.25,remaining))
        except BaseException as error:
            write_new(logs/'WRAPPER_FIRST_FAILURE.json',dict(utc=utc(),error=repr(error),signal=signal_received))
        finally:
            if process is not None:
                cleanup_records.append(cancel_owned_sessions(run,nonce,process.pid,
                          qualifier_identity['start_ticks'] if qualifier_identity else None))
            if process is not None and process.poll() is None:
                # Science groups were canceled above, before this root-only
                # evidence/receipt grace. Popen still owns this unreaped PID.
                process.terminate()
                try:process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait(timeout=2)
            if process is not None:
                cleanup_records.append(cancel_owned_sessions(run,nonce,process.pid,
                          qualifier_identity['start_ticks'] if qualifier_identity else None))
            write_new(logs/'OWNED_GROUP_CLEANUP.json',dict(records=cleanup_records,
                      before_collection=True,qualifier_kernel_identity=qualifier_identity))
            for signum,handler in previous.items():signal.signal(signum,handler)
    actual_exit=process.returncode if process is not None else 1
    write_new(logs/'WRAPPER_ACTUAL_EXIT.json',dict(utc=utc(),actual_exit=actual_exit,
        watchdog_timeout=timed_out,command_wall_including_cleanup_s=time.monotonic()-entered,
        automatic_retry=0,collection_not_started=True,
        owned_cleanup_before_root_grace=True,cleanup_warnings=[warning for item in cleanup_records for warning in item['warnings']]))
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
