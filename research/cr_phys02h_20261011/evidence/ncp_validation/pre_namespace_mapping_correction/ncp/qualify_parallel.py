#!/usr/bin/env python3
"""Bounded full9600 same-runtime qualification; plan imports only stdlib.

Numerical dependencies are imported only in admitted, fresh child lanes.
No retry, propagation, pulse, matrix exponential, or solve exists in this adapter.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import multiprocessing as mp
from multiprocessing.connection import wait
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve()
H_REL = 'research/cr_phys02h_20261011'
DEFAULT_ROOT = HERE.parents[3]
CONTRACT_REL = H_REL+'/ncp/NCP_EXECUTION_CONTRACT.json'
CONTRACT_SHA = 'c47efd512545ef1862343889a7056b1c8dcd112137ef20c561e58460315ffd6f'
AMENDMENT_REL = H_REL+'/ncp/NCP_RESOURCE_AMENDMENT.json'
AMENDMENT_SHA = '6c1b014cd66724bf85901c0644536b20ad6d01ce4dc793b6681698a00242c22f'
WRAPPER_AMENDMENT_REL = H_REL+'/ncp/NCP_WRAPPER_ACCOUNTING_AMENDMENT.json'
WRAPPER_AMENDMENT_SHA = '95eb9e33bbdc5f277123c7b2fa221e0f79b0d42ca191062fabdccc0ee8dca144'
OPS_REL = 'research/cr_phys02f_20261011/ncp/ops.py'
OPS_SHA = '8360e9f123bfc5814507728d6f946acd5109daaff2b475048d7c6ff586a4f2e7'
F_DEP_REL = 'research/cr_phys02f_20261011/inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
HISTORICAL_REL = H_REL+'/inputs/HISTORICAL_OPERATOR_IDENTITIES.json'
READY_REL = H_REL+'/ncp/NCP_READY.json'
GIB = 2**30
THREADS = ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS',
           'NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS')
UNIT = 'CR-PHYS02H-NCP-FULL9600-COLUMN-PARALLEL-QUALIFICATION'
REQUIRED_SOURCE = (H_REL+'/ncp/qualify_parallel.py',H_REL+'/ncp/run_and_collect.py',
                   H_REL+'/src/parallel_operator.py',H_REL+'/state/SCIENTIFIC_CONTRACT.json',
                   CONTRACT_REL, AMENDMENT_REL, WRAPPER_AMENDMENT_REL, OPS_REL)
REQUIRED_INPUT = (F_DEP_REL, HISTORICAL_REL, WRAPPER_AMENDMENT_REL,
                   'research/cr_phys02e_20261011/inputs/INPUT_IDENTITIES.json',
                   'research/cr_phys02g_20261011/inputs/F_CACHED_NUMERICAL_ARTIFACT.json',
                   'research/cr_phys02e_20261011/src/saved_grid.py',
                   'research/cr_phys02b_20261010/src/causal_cascade.py',
                   'research/cr_phys02c_20261011/src/coherent_bed.py',
                   'research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_fullBED_9600.npz',
                   'research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_legacy_9600.npz')


class Hold(ValueError):
    def __init__(self, code, detail=''):
        self.code = code
        super().__init__(code+(': '+str(detail) if detail else ''))


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def file_identity(path):
    return dict(bytes=Path(path).stat().st_size, sha256=sha(path))


def write_new(path, data):
    path = Path(path)
    with path.open('x') as handle:
        json.dump(data,handle,indent=2,allow_nan=False)
        handle.write('\n');handle.flush();os.fsync(handle.fileno())
    sync_dir(path.parent)


def sync_dir(path):
    descriptor = os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


def append_durable(path, data):
    with Path(path).open('a') as handle:
        handle.write(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
        handle.flush();os.fsync(handle.fileno())


def safe_relative(root, name):
    if not isinstance(name,str):raise Hold('INVALID_MANIFEST_PATH',repr(name))
    rel=Path(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name:
        raise Hold('UNSAFE_MANIFEST_PATH',name)
    root=Path(root).resolve();path=root/rel
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise Hold('SOURCE_PATH_ESCAPE',name)
    return path


def verify_pin(path,pin):
    if not isinstance(pin,dict) or not isinstance(pin.get('sha256'),str):
        raise Hold('MISSING_IDENTITY',str(path))
    if not Path(path).is_file() or sha(path)!=pin['sha256']:
        raise Hold('SOURCE_IDENTITY_MISMATCH',str(path))
    if 'bytes' in pin and (type(pin['bytes']) is not int or Path(path).stat().st_size!=pin['bytes']):
        raise Hold('SOURCE_SIZE_MISMATCH',str(path))
    return file_identity(path)


def verify_manifest(root,path):
    manifest=json.loads(Path(path).read_text())
    files=manifest.get('files')
    if manifest.get('path_basis')!='repository-root' or not isinstance(files,dict) or not files:
        raise Hold('MANIFEST_SCHEMA_INVALID',str(path))
    for name,pin in files.items():
        if type(pin.get('bytes')) is not int:raise Hold('MANIFEST_SIZE_REQUIRED',name)
        verify_pin(safe_relative(root,name),pin)
    return files


def load_ops(root):
    path=safe_relative(root,OPS_REL)
    verify_pin(path,dict(sha256=OPS_SHA))
    spec=importlib.util.spec_from_file_location('cr_phys02h_pinned_resource_ops',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def contract(root):
    path=safe_relative(root,CONTRACT_REL)
    verify_pin(path,dict(sha256=CONTRACT_SHA))
    verify_pin(safe_relative(root,AMENDMENT_REL),dict(sha256=AMENDMENT_SHA))
    verify_pin(safe_relative(root,WRAPPER_AMENDMENT_REL),dict(sha256=WRAPPER_AMENDMENT_SHA))
    return json.loads(path.read_text())


def admission(observed):
    """Pure contract admission over a fully observed resource fixture."""
    if not observed.get('capacity_established'):
        raise Hold('RESOURCE_MAPPING_HOLD',observed.get('reason'))
    cpus=len(observed['effective_allowed_cpus'])
    quota=observed.get('cpu_quota')
    capacity=min(64,cpus,quota if quota is not None else cpus)
    bounded=observed['bounded_memory_bytes']
    reserve=max(16*GIB,bounded//8)
    available=observed['available_before_reserve_bytes']
    working=max(0,available-reserve)
    cpu_workers=min(29,math.floor((capacity-6)/2))
    memory_workers=math.floor((working-4*GIB-128*2**20)/(2*512*2**20))
    workers=min(cpu_workers,memory_workers)
    if working<24*GIB or workers<2 or observed['free_disk_bytes']<16*GIB:
        raise Hold('RESOURCE_ADMISSION_HOLD',dict(capacity=capacity,working=working,workers=workers,
                   free_disk_bytes=observed['free_disk_bytes']))
    return dict(workers_per_model=workers,cpu_capacity=capacity,
                peak_process_count=6+2*workers,root_coordinators=1,lane_coordinators=2,
                wrapper_watchdog_processes=1,spawn_support_processes=2,total_fixed_cpu_slots=6,
                total_fixed_support_memory_bytes=64*2**20,
                total_fixed_wrapper_memory_bytes=64*2**20,
                logical_CPU_scope='affinity intersect effective cpuset and minimum visible quota; not physical core count',
                bounded_memory_bytes=bounded,available_before_reserve_bytes=available,
                reserve_bytes=reserve,working_limit_bytes=working,
                paired_reference_working_bytes=24*GIB,
                paired_candidate_working_bytes=4*GIB+2*workers*512*2**20+128*2**20,
                free_disk_bytes=observed['free_disk_bytes'])


def bound_sources(root,ready_path=READY_REL,review_override=None):
    ready_path=safe_relative(root,ready_path)
    if not ready_path.is_file():raise Hold('NCP_READY_MISSING',str(ready_path))
    ready=json.loads(ready_path.read_text())
    if ready.get('status')!='NCP_READY':raise Hold('NCP_NOT_READY',ready.get('status'))
    paths={}
    for key in ('execution_manifest','input_manifest','independent_review'):
        pin=ready.get(key)
        if not isinstance(pin,dict) or 'path' not in pin:raise Hold('READY_BINDING_MISSING',key)
        name=review_override if key=='independent_review' and review_override else pin['path']
        path=safe_relative(root,name)
        verify_pin(path,pin);paths[key]=path
    review=json.loads(paths['independent_review'].read_text())
    if (review.get('status')!='PASS_SCOPED' or review.get('independent_of_implementation') is not True
            or review.get('ncp_preparation_admitted') is not True or review.get('unit')!=UNIT
            or review.get('execution_manifest_sha256')!=ready['execution_manifest']['sha256']):
        raise Hold('INDEPENDENT_NCP_REVIEW_HOLD',review)
    execution=verify_manifest(root,paths['execution_manifest'])
    inputs=verify_manifest(root,paths['input_manifest'])
    required=set(REQUIRED_SOURCE)|{paths['input_manifest'].relative_to(Path(root).resolve()).as_posix()}
    if not required.issubset(execution):raise Hold('REQUIRED_EXECUTION_PINS_MISSING',sorted(required-set(execution)))
    if not set(REQUIRED_INPUT).issubset(inputs):raise Hold('REQUIRED_INPUT_PINS_MISSING',sorted(set(REQUIRED_INPUT)-set(inputs)))
    dependencies=verify_manifest(root,safe_relative(root,F_DEP_REL))
    # Full F manifest is checked independently; its records cannot be silently
    # replaced by an H subset. H may pin the exact manifest instead of duplicating it.
    return dict(ready_path=ready_path.relative_to(Path(root).resolve()).as_posix(),ready=file_identity(ready_path),
                execution_manifest=dict(path=ready['execution_manifest']['path'],**file_identity(paths['execution_manifest'])),
                input_manifest=dict(path=ready['input_manifest']['path'],**file_identity(paths['input_manifest'])),
                independent_review=dict(path=paths['independent_review'].relative_to(Path(root).resolve()).as_posix(),
                                        **file_identity(paths['independent_review'])),
                execution_files=execution,input_files=inputs,dependency_files=dependencies,
                review_fields=review)


def plan(root,run_parent,ready_path=READY_REL,review_override=None):
    root=Path(root).resolve();c=contract(root)
    for key in THREADS:os.environ[key]='1'
    ops=load_ops(root);observed=ops.probe(run_parent)
    result=dict(status='PLAN_ONLY_NO_GENERATOR_CALLS',unit=c['unit'],source_root=str(root),
                observed_resource=observed,call_counts=dict(G=0,pulse=0,expm=0,resolvent=0,linear_solve=0),
                execution_status='NOT_EXECUTED',contract_identity=file_identity(root/CONTRACT_REL))
    result['resource_amendment_identity']=file_identity(root/AMENDMENT_REL)
    result['wrapper_accounting_amendment_identity']=file_identity(root/WRAPPER_AMENDMENT_REL)
    failures=[]
    try:result['admission']=admission(observed)
    except Hold as error:failures.append(dict(code=error.code,detail=str(error)))
    expected=dict(python='3.12.3',numpy='2.4.2',scipy='1.17.0')
    versions=dict(python=platform.python_version())
    for name in ('numpy','scipy'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    result['runtime_version_observation']=dict(observed=versions,expected=expected,
                 scope='stdlib package metadata only; no numerical imports or library/CPU-dispatch attestation',
                 status='VERSION_METADATA_COMPATIBLE' if versions==expected else 'RUNTIME_HOLD')
    if versions!=expected:failures.append(dict(code='RUNTIME_HOLD',detail='Observed version metadata differs from frozen NCP runtime',observed=versions,expected=expected))
    try:result['source_binding']=bound_sources(root,ready_path,review_override)
    except (Hold,OSError,ValueError) as error:failures.append(dict(code=getattr(error,'code','SOURCE_HOLD'),detail=str(error)))
    result['holds']=failures;result['ready_for_execute']=not failures
    return result


class Budget:
    """One shared durable ledger; reservation is permanent and cannot reset."""
    def __init__(self,directory,max_builds=8,max_columns=76800):
        self.directory=Path(directory);self.max_builds=max_builds;self.max_columns=max_columns
        self.path=self.directory/'RESERVATIONS.jsonl';self.lock=self.directory/'BUDGET.lock'

    def reserve(self,job,columns=9600):
        with self.lock.open('a') as locked:
            fcntl.flock(locked,fcntl.LOCK_EX)
            rows=[json.loads(line) for line in self.path.read_text().splitlines()] if self.path.exists() else []
            if any(row['job']==job for row in rows):raise Hold('DUPLICATE_LOGICAL_BUILD',job)
            if len(rows)>=self.max_builds or sum(row['columns_reserved'] for row in rows)+columns>self.max_columns:
                raise Hold('CUMULATIVE_BUDGET_EXHAUSTED',job)
            row=dict(job=job,utc=utc(),logical_G_reserved=1,columns_reserved=columns,
                     reservation_index=len(rows)+1,no_retry=True)
            append_durable(self.path,row);sync_dir(self.directory)
            return row

    def rows(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()] if self.path.exists() else []


def check_deadline(deadline):
    if time.monotonic()>=deadline:raise Hold('WHOLE_COMMAND_TIMEOUT','900s deadline')


def cleanup_groups(processes):
    """Kills owned groups, including surviving grandchildren after lane exit."""
    for process in processes:
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
    until=time.monotonic()+.4
    for process in processes:
        try:process.wait(timeout=max(.001,until-time.monotonic()))
        except subprocess.TimeoutExpired:pass
    for process in processes:
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    for process in processes:
        try:process.wait(timeout=2)
        except subprocess.TimeoutExpired:pass


def kernel_process_identity(pid):
    """No command lines or environment values: exact live kernel identity."""
    entry=Path('/proc')/str(pid)
    stat=(entry/'stat').read_text();fields=stat[stat.rfind(')')+2:].split()
    status=(entry/'status').read_text()
    uid=int(next(line for line in status.splitlines() if line.startswith('Uid:')).split()[1])
    return dict(pid=pid,process_group=int(fields[2]),session_id=int(fields[3]),
                start_ticks=int(fields[19]),uid=uid)


def register_session(run,process,job,command):
    try:identity=kernel_process_identity(process.pid)
    except (OSError,ValueError,StopIteration,IndexError):identity=dict(pid=process.pid,identity_unavailable=True)
    owner=kernel_process_identity(os.getpid())
    append_durable(Path(run)/'PROCESS_EVENTS.jsonl',dict(utc=utc(),job=job,pid=process.pid,
          process_group=process.pid,command=command,kernel_identity=identity,
          ownership=dict(qualifier_pid=os.getpid(),qualifier_start_ticks=owner['start_ticks'],
             uid=os.getuid(),run_directory=str(Path(run).resolve()),
             launch_nonce=os.environ.get('CR_PHYS02H_LAUNCH_NONCE'))))


def require_wrapper(root,run):
    """Only the reviewed watchdog route admits real execution; plan stays direct."""
    raw=os.environ.get('CR_PHYS02H_WRAPPER_PID');nonce=os.environ.get('CR_PHYS02H_LAUNCH_NONCE')
    marker=os.environ.get('CR_PHYS02H_RUN_MARKER')
    if not raw or not nonce or len(nonce)!=32 or any(c not in '0123456789abcdef' for c in nonce) or marker!=str(Path(run).resolve()):
        raise Hold('VERIFIED_WRAPPER_REQUIRED')
    try:
        pid=int(raw);identity=kernel_process_identity(pid)
        arguments=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
        wrapper=Path(root)/H_REL/'ncp/run_and_collect.py'
        script=Path(os.fsdecode(arguments[1])).resolve() if len(arguments)>1 else None
    except (OSError,ValueError,IndexError,StopIteration) as error:
        raise Hold('WRAPPER_PARENT_IDENTITY_HOLD') from error
    if pid!=os.getppid() or identity['uid']!=os.getuid() or script!=wrapper.resolve() or b'--execute' not in arguments:
        raise Hold('WRAPPER_PARENT_IDENTITY_HOLD')
    return dict(parent_pid=pid,kernel_identity=identity,launch_nonce=nonce,run_marker=marker,
                verified_watchdog_source=str(wrapper.resolve()))


def process_measurements(groups,other_pids=()):
    """Current RSS is sampled; no sum of lifetime maxima is presented as peak."""
    rows=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            stat=(entry/'stat').read_text();fields=stat[stat.rfind(')')+2:].split()
            group=int(fields[2])
            if group not in groups and int(entry.name) not in {os.getpid(),*other_pids}:continue
            status=(entry/'status').read_text()
            rss=next(int(line.split()[1])*1024 for line in status.splitlines() if line.startswith('VmRSS:'))
            rows.append(dict(pid=int(entry.name),process_group=group,current_RSS_bytes=rss))
        except (OSError,StopIteration,ValueError,IndexError):continue
    return rows


def monitor_check(observed,admitted,groups,wrapper_pid=None,wrapper_start_ticks=None):
    if not observed.get('capacity_established'):raise Hold('RESOURCE_ADMISSION_LOST',observed.get('reason'))
    cap=min(64,len(observed['effective_allowed_cpus']),observed['cpu_quota'] or 64)
    reserve=max(16*GIB,observed['bounded_memory_bytes']//8)
    if cap<admitted['peak_process_count'] or observed['available_before_reserve_bytes']<reserve:
        raise Hold('RESOURCE_ADMISSION_LOST','CPU capacity or protected memory reserve')
    if wrapper_pid is not None:
        try:wrapper=kernel_process_identity(wrapper_pid)
        except (OSError,ValueError,IndexError,StopIteration) as error:raise Hold('WRAPPER_WATCHDOG_LOST') from error
        if wrapper['start_ticks']!=wrapper_start_ticks:raise Hold('WRAPPER_WATCHDOG_LOST')
    return dict(utc=utc(),resource=observed,owned_process_current_RSS=process_measurements(groups,() if wrapper_pid is None else (wrapper_pid,)),
                scope='host MemAvailable and every visible cgroup ancestor; sampled /proc current RSS for owned groups plus qualifier root and verified wrapper parent when present')


def wait_lanes(processes,deadline,monitor):
    while True:
        check_deadline(deadline)
        exits=[p.poll() for p in processes]
        if any(code is not None and code!=0 for code in exits):
            raise Hold('LANE_FIRST_FAILURE',exits)
        monitor()
        if all(code is not None for code in exits):return exits
        time.sleep(min(.25,max(0,deadline-time.monotonic())))


def runtime_preflight(root,op):
    expected=dict(python='3.12.3',numpy='2.4.2',scipy='1.17.0')
    observed=dict(python=platform.python_version(),numpy=op.np.__version__,scipy=op.scipy.__version__)
    if observed!=expected:raise Hold('RUNTIME_IDENTITY_HOLD',observed)
    if any(os.environ.get(key)!='1' for key in THREADS):raise Hold('THREAD_ENVIRONMENT_HOLD')
    pools=op.threadpool_info()
    if any(p.get('num_threads',1)!=1 for p in pools):raise Hold('THREADPOOL_NOT_SINGLE')
    modules={name:file_identity(module.__file__)|{'path':str(Path(module.__file__).resolve())}
             for name,module in sorted(sys.modules.items())
             if name.startswith(('numpy','scipy')) and getattr(module,'__file__',None)
             and Path(module.__file__).is_file()}
    libraries={p['filepath']:file_identity(p['filepath']) for p in pools if p.get('filepath')}
    cpu_features=getattr(op.np._core._multiarray_umath,'__cpu_features__',{})
    return dict(versions=observed,executable=dict(path=sys.executable,**file_identity(sys.executable)),
                loaded_numerical_modules=modules,threadpools=pools,libraries=libraries,
                CPU_dispatch_observed=cpu_features,CPU_dispatch_forced=False,
                thread_environment={key:os.environ.get(key) for key in THREADS})


def load_builder(root):
    sys.path.insert(0,str(Path(root)/H_REL/'src'))
    import parallel_operator as op
    return op


def verify_job(run,job):
    start=json.loads((Path(run)/'START.json').read_text())
    reservations=Budget(run).rows()
    if not any(row['job']==job and row['columns_reserved']==9600 for row in reservations):
        raise Hold('LANE_WITHOUT_SHARED_RESERVATION',job)
    if start['source_root']!=str(Path(start['source_root']).resolve()):raise Hold('SOURCE_ROOT_NOT_ABSOLUTE')
    check_deadline(start['deadline_monotonic'])
    actual=bound_sources(Path(start['source_root']),start['source_binding']['ready_path'],
                         start['source_binding']['independent_review']['path'])
    if actual!=start['source_binding']:raise Hold('ADMISSION_BINDING_MUTATED')
    return start


def tile_worker(connection,root,run,job,model,E,tile,index,deadline):
    directory=Path(run)/job/'tiles'/f'tile_{index:03d}'
    try:
        start=verify_job(run,job);op=load_builder(root)
        op.dependencies(model)
        runtime=runtime_preflight(root,op)
        check_deadline(deadline)
        payload=op.serial_build(model,E,(3200,6400),tuple(tile))
        check_deadline(deadline)
        op.persist(payload,directory)
        check_deadline(deadline)
        write_new(directory/'TILE_DONE.json',dict(columns_completed=list(tile),generator_invocations=1,
                   runtime=runtime,source_manifest_sha256=start['source_binding']['execution_manifest']['sha256']))
        connection.send(('ok',str(directory)))
    except BaseException as error:
        # A failed tile's already-written arrays remain in its immutable directory.
        directory.parent.mkdir(parents=True,exist_ok=True)
        failure=directory.parent/(directory.name+'_FAILURE.json')
        if not failure.exists():write_new(failure,dict(utc=utc(),error=repr(error),traceback=traceback.format_exc(),
                           columns_reserved=list(tile),completed_columns='UNKNOWN_UNLESS_TILE_DONE_EXISTS'))
        try:connection.send(('error',str(failure)))
        except (BrokenPipeError,EOFError):pass
    finally:connection.close()


def candidate_build(op,root,run,job,model,E,workers,deadline):
    """Same restricted-generator/gather API, with durable raw tiles on failure."""
    columns=tuple(range(9600));tiles=op.partition_columns(columns,workers,9600)
    directory=Path(run)/job
    write_new(directory/'PARTITION.json',dict(requested=list(columns),tiles=[list(t) for t in tiles],
               all_columns_exactly_once=op.validate_partition(columns,tiles,9600),workers=workers))
    ctx=mp.get_context('spawn');children=[];connections={};payloads=[]
    try:
        for index,tile in enumerate(tiles):
            check_deadline(deadline)
            receiver,sender=ctx.Pipe(duplex=False)
            process=ctx.Process(target=tile_worker,args=(sender,root,run,job,model,E,tile,index,deadline))
            process.start();sender.close();children.append(process);connections[receiver]=process
        while connections:
            check_deadline(deadline)
            for connection in wait(list(connections),timeout=min(.25,max(0,deadline-time.monotonic()))):
                process=connections.pop(connection)
                try:kind,value=connection.recv()
                except EOFError as error:raise Hold('TILE_EXIT_WITHOUT_PAYLOAD',process.pid) from error
                finally:connection.close()
                if kind!='ok':raise Hold('TILE_FIRST_FAILURE',value)
                payloads.append(op.load_persisted(value))
            if any(p.exitcode is not None and p.exitcode!=0 for p in connections.values()):
                raise Hold('TILE_NONZERO_EXIT')
        for process in children:
            check_deadline(deadline);process.join(timeout=min(2,max(0,deadline-time.monotonic())))
            if process.exitcode!=0:raise Hold('TILE_BAD_EXIT',process.exitcode)
        output=op.gather(payloads,columns,E)
        output.telemetry=dict(actual_generator_invocations=workers,worker_processes=[p.telemetry for p in payloads],
                    candidate_coordinator_peakRSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    peakRSS_scope='fresh lane coordinator lifetime and individual fresh worker lifetime; root reports sampled aggregate RSS',
                    worker_exitcodes=[p.exitcode for p in children])
        return output
    finally:
        for connection in connections:connection.close()
        for process in children:
            if process.is_alive():process.terminate()
        for process in children:
            process.join(timeout=.2)
            if process.is_alive():process.kill();process.join(timeout=.2)


def lane(root,run,job,model,kind,workers):
    lane_entered=time.monotonic()
    start=verify_job(run,job);deadline=start['deadline_monotonic']
    if str(Path(root).resolve())!=start['source_root'] or job not in (
            f'{model}_rep1_{kind}',f'{model}_rep2_{kind}') or workers!=start['admission']['workers_per_model']:
        raise Hold('LANE_ARGUMENT_BINDING_MISMATCH')
    directory=Path(run)/job
    directory.mkdir(exist_ok=False)
    try:
        for key in THREADS:os.environ[key]='1'
        op=load_builder(root)
        E,preflight=op.saved_energy()
        op.dependencies(model)
        runtime=runtime_preflight(root,op)
        write_new(directory/'RUNTIME.json',runtime)
        if len(E)!=9600 or op.raw_hash(E)!='6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292':
            raise Hold('SAVED_GRID_IDENTITY_HOLD')
        write_new(directory/'INPUT_PREFLIGHT.json',preflight)
        check_deadline(deadline)
        begin=time.monotonic()
        payload=(op.serial_build(model,E,(3200,6400)) if kind=='serial' else
                 candidate_build(op,root,run,job,model,E,workers,deadline))
        check_deadline(deadline)
        sidecar=op.persist(payload,directory/'raw')
        check_deadline(deadline)
        wall=time.monotonic()-begin
        write_new(directory/'DONE.json',dict(status='BUILD_AND_PERSIST_COMPLETED',actual_exit=0,utc=utc(),
             job=job,model=model,kind=kind,columns_completed=9600,logical_G_completed=1,
             actual_generator_invocations=1 if kind=='serial' else workers,build_and_persist_wall_s=wall,
             fresh_lane_wall_s=time.monotonic()-lane_entered,
             lane_peakRSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
             peakRSS_scope='fresh lane process lifetime maximum; excludes child peaks',
             raw_sidecar_identity=file_identity(directory/'raw/SIDECAR.json')))
        return 0
    except BaseException as error:
        write_new(directory/'FIRST_FAILURE.json',dict(status='FIRST_FAILURE',utc=utc(),error=repr(error),
                  error_code=getattr(error,'code',None),traceback=traceback.format_exc(),actual_exit=1))
        raise


def compare_lanes(root,run,job,candidate,deadline):
    start=verify_job(run,job);op=load_builder(root);runtime_preflight(root,op)
    if str(Path(root).resolve())!=start['source_root']:raise Hold('SOURCE_ROOT_BINDING_MISMATCH')
    check_deadline(deadline)
    ref=op.load_persisted(Path(run)/job/'raw');cand=op.load_persisted(Path(run)/candidate/'raw')
    if ref.columns!=tuple(range(9600)) or cand.columns!=tuple(range(9600)):
        raise Hold('FULL_COLUMN_COVERAGE_FAILURE')
    if ref.G.shape!=(9611,9611) or cand.G.shape!=(9611,9611):raise Hold('FULL_CSC_SHAPE_FAILURE')
    checks=op.parity(ref,cand);check_deadline(deadline)
    path=Path(run)/('PARITY_'+job+'__'+candidate+'.json')
    write_new(path,dict(status='EXACT_RAW_PARITY',checks=checks,
               source_manifest_sha256=start['source_binding']['execution_manifest']['sha256']))


def counts(run):
    rows=Budget(run).rows();completed=[];partial=[]
    for row in rows:
        directory=Path(run)/row['job'];done=directory/'DONE.json'
        if done.exists():completed.append(json.loads(done.read_text()))
        else:
            tiles=[]
            for path in sorted(directory.glob('tiles/tile_*/TILE_DONE.json')):
                tiles.extend(json.loads(path.read_text())['columns_completed'])
            partial.append(dict(job=row['job'],reserved_columns=row['columns_reserved'],
                    durably_completed_columns=len(tiles),durably_completed_column_indices=tiles,
                    unevidenced_columns='UNKNOWN_IN_FLIGHT_OR_NEVER_STARTED; not counted as completed'))
    return dict(logical_G_reserved=len(rows),columns_reserved=sum(r['columns_reserved'] for r in rows),
                logical_G_completed=len(completed),columns_completed=sum(r['columns_completed'] for r in completed),
                actual_generator_invocations_completed=sum(r.get('actual_generator_invocations',0) for r in completed),
                partial_generator_invocations_durably_completed=sum(len(list((Path(run)/r['job']).glob('tiles/tile_*/TILE_DONE.json'))) for r in partial),
                completed_builds=completed,partial_builds=partial)


def historical_comparisons(root,run):
    """Historical metadata comparison is informational, never an acceptance gate."""
    historic=json.loads(safe_relative(root,HISTORICAL_REL).read_text())
    result=[]
    for record in historic['records']:
        # Original record files are exact input payload dependencies. Verify
        # their identity without treating hashes as recovered original arrays.
        source=record['source'];verify_pin(safe_relative(root,source['path']),source)
        for repetition in (1,2):
            for kind in ('serial','candidate'):
                job=f"{record['model']}_rep{repetition}_{kind}"
                sidecar_path=Path(run)/job/'raw/SIDECAR.json'
                if not sidecar_path.is_file():
                    result.append(dict(label=record['label'],job=job,status='NO_COMPLETE_FRESH_SIDECAR'))
                    continue
                fresh=json.loads(sidecar_path.read_text())['arrays']
                comparisons={name:dict(historical=pin,
                     fresh={key:fresh[name][key] for key in ('raw_sha256','dtype','shape')},
                     exactly_equal=all(fresh[name][key]==pin[key] for key in ('raw_sha256','dtype','shape')))
                       for name,pin in record['arrays'].items()}
                result.append(dict(label=record['label'],job=job,status='INFORMATIONAL_ONLY',comparisons=comparisons))
    return dict(records=result,acceptance_gate=False,
         original_values_recovered=False,original_pulse_or_source_approval_adopted=False,
         scope='Historical raw fingerprints only; differences preserve prior F HOLD and do not invalidate exact fresh same-runtime parity')


def execute(root,run,ready_path=READY_REL,review_override=None):
    entered=time.monotonic();deadline=entered+900;root=Path(root).resolve();run=Path(run)
    if not run.is_absolute() or run.resolve()!=run or run.is_relative_to(root):
        raise Hold('RUN_MUST_BE_FRESH_ABSOLUTE_OUTSIDE_SOURCE',str(run))
    run.mkdir(parents=False,exist_ok=False)
    write_new(run/'START_INTENT.json',dict(utc=utc(),command=sys.argv,source_root=str(root),
               run_directory=str(run),entered_monotonic=entered,deadline_monotonic=deadline,
               whole_command_wall_limit_s=900,ready_path=ready_path,review_override=review_override,
               launcher_identity=file_identity(HERE),execution_status='ADMISSION_PENDING'))
    children=[];logs=[];receipt=dict(status='FIRST_FAILURE',actual_exit=1)
    previous_handlers={}
    def interrupted(signum,frame):
        raise Hold('OWNED_COMMAND_INTERRUPTED',signum)
    for signum in (signal.SIGTERM,signal.SIGINT):
        previous_handlers[signum]=signal.signal(signum,interrupted)
    try:
        contract(root);check_deadline(deadline)
        wrapper_binding=require_wrapper(root,run)
        binding=bound_sources(root,ready_path,review_override)
        for key in THREADS:os.environ[key]='1'
        # Version checks use stdlib metadata here; fresh numerical runtime is
        # attested in each lane before its first generator invocation.
        versions=dict(python=platform.python_version(),numpy=importlib.metadata.version('numpy'),
                      scipy=importlib.metadata.version('scipy'))
        if versions!=dict(python='3.12.3',numpy='2.4.2',scipy='1.17.0'):
            raise Hold('RUNTIME_IDENTITY_HOLD',versions)
        ops=load_ops(root);observed=ops.probe(run);admitted=admission(observed);check_deadline(deadline)
        wrapper_pid=wrapper_binding['parent_pid']
        wrapper_start_ticks=wrapper_binding.get('kernel_identity',{}).get('start_ticks')
        launch_nonce=os.environ.get('CR_PHYS02H_LAUNCH_NONCE')
        if launch_nonce and os.environ.get('CR_PHYS02H_RUN_MARKER')!=str(run):raise Hold('WRAPPER_RUN_MARKER_MISMATCH')
        start=dict(utc=utc(),source_root=str(root),run_directory=str(run),deadline_monotonic=deadline,
                   entered_monotonic=entered,source_binding=binding,resource=observed,admission=admitted,
                   runtime_versions=versions,contract_identity=file_identity(root/CONTRACT_REL),
                   resource_amendment_identity=file_identity(root/AMENDMENT_REL),
                   wrapper_accounting_amendment_identity=file_identity(root/WRAPPER_AMENDMENT_REL),
                   wrapper_parent_pid=wrapper_pid,
                   verified_wrapper_binding=wrapper_binding,
                   process_inventory=dict(wrapper_watchdog=1,qualifier_root=1,model_lane_coordinators=2,
                       lane_resource_trackers=2,tile_workers=2*admitted['workers_per_model'],
                       maximum_reserved_slots=admitted['peak_process_count'],
                       direct_qualifier_plan='uses same reserved layout; execution requires verified watchdog parent',
                       comparisons='fresh comparator replaces completed numerical lanes; no overlap',
                       collection='existing wrapper after qualifier exit; stdlib ZIP collection has no child process'),
                   command=sys.argv,model_assignment='gpt-6.1-sol requested; no backend attestation',
                   inherited_F='HOLD_OPERATOR_BINDING_UNRESOLVED',G_frontier='BLOCKED_BY_F_OPERATOR_BINDING_HOLD')
        write_new(run/'START.json',start);budget=Budget(run)
        for repetition in (1,2):
            for kind in ('serial','candidate'):
                jobs=[];phase=[]
                # Shared permanent reservations occur before either lane starts.
                for model in ('fullBED','legacy'):
                    check_deadline(deadline);job=f'{model}_rep{repetition}_{kind}'
                    budget.reserve(job);jobs.append((model,job))
                for model,job in jobs:
                    check_deadline(deadline)
                    stdout=(run/(job+'.stdout')).open('xb');stderr=(run/(job+'.stderr')).open('xb')
                    logs.extend((stdout,stderr))
                    command=[sys.executable,str(root/H_REL/'ncp/qualify_parallel.py'),'--lane',
                       '--source-root',str(root),'--run',str(run),'--job',job,'--model',model,
                       '--kind',kind,'--workers',str(admitted['workers_per_model'])]
                    process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True)
                    children.append(process);phase.append(process)
                    register_session(run,process,job,command)
                monitor=lambda:append_durable(run/'RESOURCE_SAMPLES.jsonl',
                         monitor_check(ops.probe(run),admitted,{p.pid for p in children},wrapper_pid,wrapper_start_ticks))
                wait_lanes(phase,deadline,monitor)
                for process in phase:
                    append_durable(run/'PROCESS_EVENTS.jsonl',dict(utc=utc(),pid=process.pid,actual_exit=process.returncode))
                if kind=='candidate':
                    comparisons=[(f'{model}_rep{repetition}_serial',f'{model}_rep{repetition}_candidate') for model in ('fullBED','legacy')]
                    if repetition==2:comparisons += [(f'{model}_rep1_serial',f'{model}_rep2_serial') for model in ('fullBED','legacy')]
                    # Fresh comparator children avoid retaining either full matrix
                    # in the root, and are covered by the same command deadline.
                    for reference,candidate in comparisons:
                        check_deadline(deadline)
                        command=[sys.executable,str(root/H_REL/'ncp/qualify_parallel.py'),'--compare',
                           '--source-root',str(root),'--run',str(run),'--job',reference,'--candidate',candidate]
                        with (run/('compare_'+reference+'__'+candidate+'.stdout')).open('xb') as stdout, \
                             (run/('compare_'+reference+'__'+candidate+'.stderr')).open('xb') as stderr:
                            process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True)
                            children.append(process)
                            register_session(run,process,'compare_'+reference+'__'+candidate,command)
                            wait_lanes([process],deadline,monitor)
        check_deadline(deadline)
        import statistics
        performances={}
        for model in ('fullBED','legacy'):
            times={kind:[json.loads((run/f'{model}_rep{rep}_{kind}'/'DONE.json').read_text())['build_and_persist_wall_s']
                         for rep in (1,2)] for kind in ('serial','candidate')}
            ratio=statistics.median(times['serial'])/statistics.median(times['candidate'])
            performances[model]=dict(times_s=times,observed_median_serial_over_candidate_ratio=ratio,
                 status='PERFORMANCE_IMPROVED_LOCALLY_ON_ACTUAL_NCP' if ratio>1 else 'PERFORMANCE_NOT_IMPROVED',
                 scope='actual host same-input build-and-persist; includes candidate spawn, raw tile persistence, gather and full persistence')
        actual=counts(run)
        if actual['logical_G_completed']!=8 or actual['columns_completed']!=76800:raise Hold('COMPLETION_COUNT_FAILURE',actual)
        write_new(run/'QUALIFICATION.json',dict(status='EXACT_SAME_RUNTIME_FULL9600_ASSEMBLY_CHECKED_PENDING_INDEPENDENT_REVIEW',
            performance=performances,counts=actual,claim_ceiling='SAME_RUNTIME_FULL9600_ASSEMBLY_EQUIVALENCE requires independent final review',
            historical_identity='Fresh reconstruction; old reference and failed fingerprints informational only; old pulse/source approvals not adopted'))
        write_new(run/'HISTORICAL_COMPARISONS.json',historical_comparisons(root,run))
        check_deadline(deadline)
        receipt=dict(status='EXACT_ASSEMBLY_CHECKED_PENDING_INDEPENDENT_REVIEW',actual_exit=0,performance=performances)
    except BaseException as error:
        cleanup_groups(children)
        write_new(run/'FIRST_FAILURE.json',dict(utc=utc(),error=repr(error),error_code=getattr(error,'code',None),
                   traceback=traceback.format_exc(),automatic_retry=0))
        receipt.update(error=repr(error),error_code=getattr(error,'code',None))
    finally:
        cleanup_groups(children)
        for handle in logs:handle.close()
        receipt.update(start_monotonic=entered,end_utc=utc(),coordinator_whole_wall_s=time.monotonic()-entered,
                   whole_command_wall_limit_s=900,counts=counts(run),
                   owned_lane_exitcodes=[dict(pid=p.pid,actual_exit=p.returncode) for p in children],
                   root_peakRSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                   peakRSS_scope='root process lifetime maximum; lane/worker lifetime maxima and aggregate current RSS samples separately recorded',
                   call_counts=dict(pulse=0,expm=0,resolvent=0,linear_solve=0,F_retry=0,G_frontier=0),
                   automatic_retry=0,terminal_receipt_overhead_scope='failure cleanup/receipt overhead reported in whole wall; no extra science after deadline')
        write_new(run/'ACTUAL_EXIT.json',receipt)
        for signum,handler in previous_handlers.items():signal.signal(signum,handler)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--plan',action='store_true');modes.add_argument('--execute',action='store_true')
    modes.add_argument('--lane',action='store_true',help=argparse.SUPPRESS)
    modes.add_argument('--compare',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--source-root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--ready',default=READY_REL)
    parser.add_argument('--review',help='repository-relative alternate path; must match the READY review SHA')
    parser.add_argument('--job');parser.add_argument('--candidate')
    parser.add_argument('--model',choices=('fullBED','legacy'))
    parser.add_argument('--kind',choices=('serial','candidate'))
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();root=args.source_root.resolve()
    if args.plan:
        parent=args.run.parent if args.run else Path.cwd()
        result=plan(root,parent,args.ready,args.review);print(json.dumps(result,indent=2));return 0
    if args.run is None:parser.error('--run is required')
    if args.lane:
        if not all((args.job,args.model,args.kind)):parser.error('internal lane arguments required')
        return lane(root,args.run,args.job,args.model,args.kind,args.workers)
    if args.compare:
        start=verify_job(args.run,args.job)
        compare_lanes(root,args.run,args.job,args.candidate,start['deadline_monotonic']);return 0
    result=execute(root,args.run,args.ready,args.review);print(json.dumps(result,indent=2));return result['actual_exit']


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print(json.dumps(dict(status='OPERATIONAL_HOLD',error=repr(error),error_code=getattr(error,'code',None))),file=sys.stderr)
        sys.exit(1)
