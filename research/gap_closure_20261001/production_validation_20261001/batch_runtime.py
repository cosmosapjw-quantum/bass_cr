"""Bounded, fail-fast local partitions of unchanged R4U whole-query ladders.

This is a local process supervisor, not an MPI launcher or scaling benchmark.
Planning loads no native evaluator. Exact manifests bind content, not approval.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
PROVIDER = HERE.parent/'production_solver_20261001'/'provider'
sys.path.insert(0, str(PROVIDER))
import precompute_cli as pc

SCHEMA = 'BASS_R4V_LOCAL_PARTITION_BATCH_V1'
GiB = pc.GiB
CLAIMS = dict(capture=False, production_admission='HOLD', all_bound='OPEN',
              b_grid='NO_GO', continuous_trajectory_error_bound=False,
              mpi_physical_execution=False, ncp64_scaling_measured=False)


def source_identity():
    return {str(Path(__file__).resolve()): pc.hp.sha(__file__),
            str(Path(pc.__file__).resolve()): pc.hp.sha(pc.__file__),
            str(Path(pc.resources.__file__).resolve()): pc.hp.sha(pc.resources.__file__)}


def canonical_times(times):
    result = []
    for t in times:
        if isinstance(t, bool):
            raise ValueError('boolean is not a time')
        f = float.fromhex(t) if isinstance(t, str) else float(t)
        if not math.isfinite(f):
            raise ValueError('finite exact times required')
        result.append(f.hex())
    if not result or len(set(result)) != len(result):
        raise ValueError('nonempty unique exact times required')
    return result


def partitions(times, lanes, cap):
    n = len(times)
    if not 1 <= n <= 72 or type(lanes) is not int or not 1 <= lanes <= min(4,n):
        raise ValueError('one to 72 queries and at most four nonempty lanes required')
    if type(cap) is not int or not n <= cap <= min(792,11*n):
        raise ValueError('global cap must lie between query count and 11 times count')
    counts = [n//lanes + (i < n % lanes) for i in range(lanes)]
    caps = [cap*c//n for c in counts]
    for i in range(cap-sum(caps)):
        caps[i] += 1
    result = []; offset = 0; reservation_offset = 0
    for count, maximum in zip(counts, caps):
        result.append({'start':offset, 'stop':offset+count,
                       'times_hex':times[offset:offset+count], 'max_attempts':maximum,
                       'global_reservation_range':[reservation_offset+1,reservation_offset+maximum]})
        offset += count
        reservation_offset += maximum
    return result


def aggregate_admit(info, allocations, frozen_reserve=0):
    if not allocations:
        raise ValueError('at least one lane allocation required')
    cpus = []
    requested = 0
    logical = allocations[0]['logical_cpus_explicit']
    for r in allocations:
        if r['ranks'] != 1 or r['logical_cpus_explicit'] != logical:
            raise ValueError('only uniform-CPU-unit serial lanes are supported')
        pc.admit(info, 1, r['threads'], r['cpus'], r['per_rank_gib'], logical)
        cpus.extend(r['cpus'])
        requested += math.ceil(r['per_rank_gib']*GiB)
    if len(cpus) != len(set(cpus)):
        raise ValueError('CPU allocations overlap between lanes')
    if not logical and len(set(pc._core_ids(cpus))) != len(cpus):
        raise ValueError('CPU allocations share physical cores between lanes')
    slots = min(info['usable_cpu_budget'], info['logical_cpus'] if logical else info['physical_cores'])
    if len(cpus) > slots:
        raise ValueError('aggregate allocation exceeds current CPU budget')
    memory = min(info['memory_limit_bytes'], info['memory_available_bytes'])
    reserve = max(GiB, memory//8, frozen_reserve)
    if requested + reserve > memory:
        raise ValueError('aggregate RSS estimate plus reserve exceeds available memory')
    return {'cpus':cpus, 'total_compute_threads':len(cpus),
            'estimated_total_rss_bytes':requested, 'memory_reserve_bytes':reserve,
            'memory_budget_bytes':memory-reserve, 'logical_cpus_explicit':logical,
            'memory_is_estimate_not_os_limit':True, 'census':info}


def make_batch(*, inputs, build, times, manifest, output, cpus, lanes=4,
               threads=2, per_lane_gib=0.5, max_attempts=792,
               timeout_seconds=1800., overall_timeout_seconds=None,
               logical=False, backend='fortran'):
    times = canonical_times(times)
    parts = partitions(times, lanes, max_attempts)
    if type(threads) is not int or threads < 1 or len(cpus) != lanes*threads:
        raise ValueError('exact lanes times threads CPU list required')
    if not math.isfinite(per_lane_gib) or per_lane_gib < 0.5:
        raise ValueError('at least 0.5 GiB per lane is required for this scope')
    if overall_timeout_seconds is None:
        overall_timeout_seconds = timeout_seconds + 30.
    if (not math.isfinite(overall_timeout_seconds) or
            not timeout_seconds+30 <= overall_timeout_seconds <= 86430):
        raise ValueError('overall deadline must cover lane timeout plus at least 30 seconds')
    path = pc._outside_repo(manifest); out = pc._outside_repo(output)
    if path.exists() or out.exists() or not path.parent.is_dir() or not out.parent.is_dir():
        raise ValueError('batch plan/output must be new with existing parents')
    rows = []
    for i, part in enumerate(parts):
        lane_path = path.with_name(path.name+f'.lane{i:02}.json')
        lane_out = out.with_name(out.name+f'.lane{i:02}')
        if lane_path.exists():
            raise ValueError('lane manifest path already consumed')
        lane = pc.make_manifest(inputs=inputs, build=build,
             times=[float.fromhex(t) for t in part['times_hex']], output=lane_out,
             backend=backend, ranks=1, threads=threads, cpus=cpus[i*threads:(i+1)*threads],
             max_attempts=part['max_attempts'], timeout_seconds=timeout_seconds,
             per_rank_gib=per_lane_gib, logical=logical)
        if any(len(t['levels']) != 11 for t in lane['tasks']):
            raise ValueError('this bounded batch requires the unchanged 11-level ladder')
        rows.append({'lane_index':i, **part, 'manifest':str(lane_path),
                     'output':str(lane_out), 'plan':lane})
    census = pc.resources.census()
    admission = aggregate_admit(census, [r['plan']['resources'] for r in rows])
    for row in rows:
        pc.hp.write_new(row['manifest'], row.pop('plan'))
        row['execution_sha256'] = pc.hp.sha(row['manifest'])
    result = {'schema':SCHEMA, 'batch_id':str(uuid.uuid4()), 'output':str(out),
        'times_hex':times, 'lanes':rows, 'source_identity':source_identity(),
        'host':pc._host(), 'python':pc._binary(sys.executable),
        'runtime_versions':pc._runtime_versions(), 'resources':admission,
        'limits':{'global_max_attempts':max_attempts,
                  'lane_timeout_seconds':timeout_seconds,
                  'overall_timeout_seconds':overall_timeout_seconds,
                  'cancellation_grace_seconds':15.},
        'partition_policy':'CONTIGUOUS_FIXED_NO_TRANSFER_NO_RETRY',
        'scope':'finite exact-time physical operator queries; local process lanes',
        'native_calls_during_plan':0, 'old_approval_reused':False,
        'execution_sha_is_content_binding_not_user_approval':True,
        'model_routing':'UNAVAILABLE_NO_INFERENCE', **CLAIMS}
    pc.hp.write_new(path, result)
    return {'manifest':str(path), 'execution_sha256':pc.hp.sha(path),
            'lane_count':lanes, 'query_count':len(times), 'native_calls':0}


def validate_batch(m, *, fresh=True):
    if m['schema'] != SCHEMA or m['source_identity'] != source_identity():
        raise ValueError('batch schema or source identity changed')
    if m['host'] != pc._host() or m['python'] != pc._binary(sys.executable):
        raise ValueError('batch host/boot or Python executable changed')
    if m['runtime_versions'] != pc._runtime_versions():
        raise ValueError('batch runtime changed')
    if any(m.get(k) != v for k, v in CLAIMS.items()):
        raise ValueError('batch claim ceiling changed')
    if m['partition_policy'] != 'CONTIGUOUS_FIXED_NO_TRANSFER_NO_RETRY':
        raise ValueError('fixed no-transfer partition required')
    times = canonical_times(m['times_hex'])
    if times != m['times_hex']:
        raise ValueError('exact canonical time bytes required')
    parts = partitions(times, len(m['lanes']), m['limits']['global_max_attempts'])
    manifests = []; common_context = None
    out = pc._outside_repo(m['output'])
    paths = {str(out)}
    for i, (row, part) in enumerate(zip(m['lanes'], parts)):
        if row['lane_index'] != i or any(row[k] != v for k,v in part.items()):
            raise ValueError('fixed ordered partition or lane cap changed')
        lane_path = pc._outside_repo(row['manifest'])
        lane = pc.read_bound(lane_path, row['execution_sha256'])
        pc.validate_manifest(lane)  # input/native/source/runtime identities, no evaluator
        if common_context is None:
            common_context = lane['context']
        elif common_context != lane['context']:
            raise ValueError('every lane must share the exact same physical/numerical context')
        if (lane['output'] != row['output'] or
            row['output'] != str(out.with_name(out.name+f'.lane{i:02}')) or
            [t['time_hex'] for t in lane['tasks']] != part['times_hex'] or
            lane['limits']['max_attempts'] != part['max_attempts'] or
            lane['limits']['hard_timeout_seconds'] != m['limits']['lane_timeout_seconds'] or
            any(len(t['levels']) != 11 for t in lane['tasks']) or
            lane['resources']['per_rank_gib'] < 0.5):
            raise ValueError('lane differs from fixed batch contract')
        if str(lane_path) in paths or lane['output'] in paths:
            raise ValueError('batch paths collide')
        paths.update([str(lane_path), lane['output']])
        manifests.append(lane)
    wall = m['limits']['overall_timeout_seconds']
    if (not math.isfinite(wall) or
        not m['limits']['lane_timeout_seconds']+30 <= wall <= 86430 or
        m['limits']['cancellation_grace_seconds'] != 15.):
        raise ValueError('invalid batch deadline')
    allocations = [p['resources'] for p in manifests]
    frozen = aggregate_admit(m['resources']['census'], allocations)
    if frozen != m['resources']:
        raise ValueError('frozen aggregate resource census inconsistent')
    if fresh:
        info = pc.resources.census()
        if info['cpu_model'] != m['resources']['census']['cpu_model']:
            raise ValueError('CPU model changed')
        current = aggregate_admit(info, allocations, m['resources']['memory_reserve_bytes'])
    else:
        current = frozen
    return manifests, current


def _descendants(exclude_roots=()):
    """Snapshot exact procfs identities under this batch; handles PID namespaces."""
    me = pc._process(); rows = {}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            row = pc._process(int(p.name))
            if row['pid_namespace'] == me['pid_namespace']:
                rows[row['pid']] = row
        except (OSError, ValueError, KeyError, StopIteration):
            pass
    selected = {me['pid']}
    while True:
        more = {pid for pid, row in rows.items() if row['ppid'] in selected and pid not in exclude_roots}
        if more <= selected:
            break
        selected |= more
    return [row for pid,row in rows.items() if pid != me['pid'] and pid in selected]


def _kill_exact(rows):
    for row in rows:
        try:
            actual = pc._process(row['pid'])
            # Parent PID may change on orphaning; PID/start/namespace identity may not.
            if all(actual[k] == row[k] for k in ('pid','signal_pid','start_ticks','pid_namespace')):
                os.kill(row['signal_pid'], signal.SIGKILL)
        except (OSError, ValueError, KeyError, StopIteration):
            pass


def _subreaper(value=None):
    """Linux process-local subreaper; constants from linux/prctl.h, no physics."""
    libc = ctypes.CDLL(None, use_errno=True)
    current = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(current), 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_GET_CHILD_SUBREAPER failed')
    if value is not None and libc.prctl(36, int(value), 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER failed')
    return current.value


def _identity(row):
    return tuple(row[k] for k in ('pid','signal_pid','start_ticks','pid_namespace'))


def _alive_exact(row):
    try:
        actual = pc._process(row['pid'])
        state = (Path('/proc')/str(row['pid'])/'stat').read_text().rsplit(')',1)[1].split()[0]
        return _identity(actual) == _identity(row) and state != 'Z'
    except (OSError, ValueError, KeyError, StopIteration):
        return False


def _receipt_descendants(specs, children, owner):
    """Accept only fresh lane receipts bound to an owned direct wrapper identity."""
    rows=[]; rejected=[]
    for i,spec in enumerate(specs):
        if i not in children:
            continue
        base=Path(spec['output']); sp=base/'SUPERVISOR.json'; ap=base/'ADMISSION.json'
        if not sp.is_file() or not ap.is_file():
            continue
        try:
            supervisor=json.loads(sp.read_text()); admission=json.loads(ap.read_text())
            wrapper=supervisor['process']
            if (supervisor['execution_sha256'] != spec['execution_sha256'] or
                admission['execution_sha256'] != spec['execution_sha256'] or
                wrapper['signal_pid'] != children[i].pid or wrapper['ppid'] != owner['pid'] or
                wrapper['pid_namespace'] != owner['pid_namespace'] or
                wrapper['start_ticks'] < owner['start_ticks']):
                raise ValueError('receipt is not bound to this owned wrapper')
            ranks=admission['ranks']
            if len(ranks)!=1 or ranks[0]['rank']!=0:
                raise ValueError('one exact serial rank is required')
            rank=ranks[0]; worker=rank['process']
            if (rank.get('execution_sha256') != spec['execution_sha256'] or
                rank.get('context_id') != spec['context_id'] or
                worker['ppid'] != wrapper['pid'] or
                worker['pid_namespace'] != wrapper['pid_namespace'] or
                worker['start_ticks'] < wrapper['start_ticks']):
                # Failed pre-native admission may omit execution/context fields.
                if rank.get('ok') is False:
                    continue
                raise ValueError('rank identity is not a direct child of the owned wrapper')
            rows.append(worker)
        except (OSError,ValueError,KeyError,TypeError) as exc:
            rejected.append({'lane_index':i,'reason':type(exc).__name__+': '+str(exc)})
    return rows,rejected


def _terminal_cleanup(known, exclude_roots):
    """Kill and reap owned adopted descendants even when no wrapper remains active."""
    identities={_identity(row):row for row in known}
    for row in _descendants(exclude_roots):identities[_identity(row)]=row
    live_before=[row for row in identities.values() if _alive_exact(row)]
    _kill_exact(live_before)
    deadline=time.monotonic()+2.
    while True:
        for row in identities.values():
            try:
                if _identity(pc._process(row['pid']))==_identity(row):
                    os.waitpid(row['signal_pid'],os.WNOHANG)
            except (OSError,ValueError,KeyError,StopIteration):pass
        survivors=[row for row in identities.values() if _alive_exact(row)]
        if not survivors or time.monotonic()>=deadline:
            # A child may become a zombie between waitpid and the state read.
            for row in identities.values():
                try:
                    if _identity(pc._process(row['pid']))==_identity(row):
                        os.waitpid(row['signal_pid'],os.WNOHANG)
                except (OSError,ValueError,KeyError,StopIteration):pass
            break
        time.sleep(0.02)
    return {'live_before_cleanup':live_before,'survivors':survivors,
            'owned_processes_observed':len(identities),'adopted_children_reaped':True}


def monitor(commands, out, *, timeout_seconds, grace_seconds=15., lane_specs=()):
    """Start bound lane wrappers, cancel peers on first observed failure; no retry."""
    out = Path(out); start = time.monotonic(); active = {}; finished = {}
    first_failure = None; cancelled = False; cancel_start = None; identities = []
    logs = []; children={}; known={}; receipt_rejections=[]; owner=pc._process()
    excluded={r['pid'] for r in _descendants()}
    prior_subreaper=_subreaper(1)
    terminal=None
    def snapshot():
        for row in _descendants(excluded):known[_identity(row)]=row
        rows,rejected=_receipt_descendants(lane_specs,children,owner)
        for row in rows:known[_identity(row)]=row
        for item in rejected:
            if item not in receipt_rejections:receipt_rejections.append(item)
        return list(known.values())
    try:
        for i, command in enumerate(commands):
            stdout = (out/f'lane{i:02}.stdout.log').open('xb')
            stderr = (out/f'lane{i:02}.stderr.log').open('xb')
            logs.extend([stdout, stderr])
            active[i] = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                         start_new_session=True)
            children[i]=active[i]
        while active:
            snapshot()
            for i, child in list(active.items()):
                code = child.poll()
                if code is not None:
                    finished[i] = {'lane_index':i, 'returncode':code,
                                   'observed_wall_seconds':time.monotonic()-start}
                    del active[i]
                    if code != 0 and first_failure is None:
                        first_failure = {'kind':'LANE_EXIT', **finished[i]}
            now = time.monotonic()
            if now >= start+timeout_seconds and first_failure is None and active:
                first_failure = {'kind':'OVERALL_TIMEOUT', 'observed_wall_seconds':now-start}
            if first_failure is not None and not cancelled:
                pc.hp.write_new(out/'FIRST_FAILURE.json', first_failure)
                identities = snapshot()
                for child in active.values():
                    child.send_signal(signal.SIGTERM)
                # Dead wrappers' reparented children are now our adopted children.
                active_pids={child.pid for child in active.values()}
                _kill_exact([r for r in _descendants(excluded)
                             if r['ppid']==owner['pid'] and r['signal_pid'] not in active_pids])
                cancel_start = now; cancelled = True
            if cancelled and active and now >= cancel_start+grace_seconds:
                _kill_exact(identities + snapshot())
                for child in active.values():
                    if child.poll() is None:
                        child.kill()
                for i, child in list(active.items()):
                    finished[i] = {'lane_index':i, 'returncode':child.wait(timeout=5),
                                   'forced_after_cancellation_grace':True,
                                   'observed_wall_seconds':time.monotonic()-start}
                    del active[i]
            if active:
                time.sleep(0.05)
    except BaseException as exc:
        cancelled = True
        if first_failure is None:
            first_failure = {'kind':'BATCH_SUPERVISOR_ERROR',
                             'error':type(exc).__name__+': '+str(exc)}
            try:
                pc.hp.write_new(out/'FIRST_FAILURE.json', first_failure)
            except OSError as receipt_error:
                first_failure['receipt_write_error']=str(receipt_error)
        identities = snapshot()
        for child in active.values():
            if child.poll() is None:
                child.send_signal(signal.SIGTERM)
        deadline = time.monotonic()+grace_seconds
        for i, child in active.items():
            try:
                code = child.wait(timeout=max(0.01, deadline-time.monotonic()))
            except subprocess.TimeoutExpired:
                _kill_exact(identities+snapshot()); child.kill(); code=child.wait(timeout=5)
            finished[i] = {'lane_index':i, 'returncode':code}
    finally:
        for stream in logs:
            stream.close()
        try:
            terminal=_terminal_cleanup(snapshot(),excluded)
        finally:
            _subreaper(prior_subreaper)
    if first_failure is None and (terminal['live_before_cleanup'] or receipt_rejections):
        first_failure={'kind':'OWNED_DESCENDANT_OR_RECEIPT_FAILURE',
                       'live_descendants':terminal['live_before_cleanup'],
                       'receipt_rejections':receipt_rejections}
        pc.hp.write_new(out/'FIRST_FAILURE.json',first_failure)
    return {'success':first_failure is None and len(finished)==len(commands) and not terminal['survivors'],
            'first_failure':first_failure, 'cancelled_live_lanes':cancelled,
            'lanes':[finished[i] for i in sorted(finished)],
            'terminal_cleanup':terminal,'receipt_rejections':receipt_rejections,
            'subreaper_previous_value_restored':prior_subreaper,
            'wall_seconds':time.monotonic()-start}


def run_batch(m, execution_sha):
    manifests, admitted = validate_batch(m)
    out = Path(m['output'])
    if any(Path(p['output']).exists() for p in manifests):
        raise ValueError('one or more lane outputs already consumed')
    out.mkdir(exist_ok=False)
    pc.hp.write_new(out/'BATCH_EXECUTION.json', m)
    pc.hp.write_new(out/'BATCH_ADMISSION.json', {'execution_sha256':execution_sha,
         'admitted':True, 'resources':admitted, 'native_calls_before_admission':0})
    pc.hp.write_new(out/'GLOBAL_RESERVATION_BLOCKS.json', {
        'execution_sha256':execution_sha,
        'global_max_attempts':m['limits']['global_max_attempts'],
        'blocks':[{'lane_index':r['lane_index'], 'lane_execution_sha256':r['execution_sha256'],
                   'global_reservation_range':r['global_reservation_range'],
                   'lane_cap':r['max_attempts']} for r in m['lanes']],
        'mapping':'global_id = block_start + local_durable_reservation_id - 1',
        'issued_by_single_batch_coordinator_before_any_child_launch':True,
        'blocks_transferable':False, 'unused_reservations_reissued':False})
    commands = [[m['python']['path'], '-I', str(Path(__file__).resolve()), '_lane',
                 '--manifest', row['manifest'], '--execution-sha256',row['execution_sha256'],
                 '--batch-source-sha256',m['source_identity'][str(Path(__file__).resolve())]]
                for row in m['lanes']]
    affinity = os.sched_getaffinity(0)
    def cancel(signum, frame):
        raise KeyboardInterrupt('batch supervisor cancellation')
    prior_handler = signal.signal(signal.SIGTERM, cancel)
    try:
        os.sched_setaffinity(0, set(admitted['cpus']))
        if os.sched_getaffinity(0) != set(admitted['cpus']):
            raise ValueError('batch coordinator CPU binding failed')
        result = monitor(commands, out, timeout_seconds=m['limits']['overall_timeout_seconds'],
                         grace_seconds=m['limits']['cancellation_grace_seconds'],
                         lane_specs=[{'output':r['output'],'execution_sha256':r['execution_sha256'],
                                      'context_id':p['context']['context_id']}
                                      for r,p in zip(m['lanes'],manifests)])
    finally:
        signal.signal(signal.SIGTERM, prior_handler)
        os.sched_setaffinity(0, affinity)
    receipts = []
    for row in m['lanes']:
        lane_out = Path(row['output']); receipt = {'lane_index':row['lane_index'],
            'output':str(lane_out), 'execution_sha256':row['execution_sha256'], 'files':{}}
        for name in ('SUPERVISOR_RESULT.json','ADMISSION.json','RESULT.json','FAILURE.json',
                     'queue/QUEUE_RECEIPT.json'):
            p=lane_out/name
            if p.is_file():
                receipt['files'][name]={'sha256':pc.hp.sha(p), 'data':json.loads(p.read_text())}
        if not receipt['files'].get('SUPERVISOR_RESULT.json',{}).get('data',{}).get('success'):
            result['success']=False
        if not receipt['files'].get('RESULT.json',{}).get('data',{}).get('ok'):
            result['success']=False
        queue_receipt = receipt['files'].get('queue/QUEUE_RECEIPT.json',{}).get('data',{})
        used = queue_receipt.get('raw_attempts_reserved')
        if (type(used) is not int or not 0 <= used <= row['max_attempts'] or
                queue_receipt.get('max_attempts') != row['max_attempts']):
            result['success']=False
        receipt.update(raw_attempts_reserved=used,
                       global_reservation_range=row['global_reservation_range'])
        receipts.append(receipt)
    result.update(execution_sha256=execution_sha, lane_receipts=receipts,
         global_max_attempts=m['limits']['global_max_attempts'],
         maximum_proof='sum of immutable disjoint lane caps; no cap transfer or retry',
         **CLAIMS)
    pc.hp.write_new(out/'BATCH_RESULT.json', result)
    return result


def run_lane(manifest, execution_sha, batch_source_sha):
    def cancel(signum, frame):
        raise KeyboardInterrupt('batch cancellation')
    signal.signal(signal.SIGTERM, cancel)
    try:
        if pc.hp.sha(__file__) != batch_source_sha:
            raise ValueError('batch wrapper source changed')
        m = pc.read_bound(manifest, execution_sha)
        pc.validate_manifest(m)
        r = m['resources']
        if r['ranks'] != 1:
            raise ValueError('local batch wrapper accepts only a single rank')
        pc.hp.bind_rank(0, 1, r['threads'], r['cpus'])
        result = pc.run_manifest(m, execution_sha)
        print(json.dumps(result))
        return 0 if result['success'] else 1
    except KeyboardInterrupt:
        return 130


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    subs=p.add_subparsers(dest='action', required=True)
    q=subs.add_parser('plan', allow_abbrev=False)
    for key in ('inputs','build','times-json','manifest','output','cpus'):
        q.add_argument('--'+key, required=True)
    q.add_argument('--lanes', type=int, default=4); q.add_argument('--threads',type=int,default=2)
    q.add_argument('--per-lane-gib',type=float,default=0.5)
    q.add_argument('--max-attempts',type=int,required=True)
    q.add_argument('--timeout-seconds',type=float,required=True)
    q.add_argument('--overall-timeout-seconds',type=float)
    q.add_argument('--logical-cpus',action='store_true')
    q.add_argument('--backend',choices=('fortran','reference'),default='fortran')
    for name in ('run','_lane'):
        q=subs.add_parser(name,allow_abbrev=False)
        q.add_argument('--manifest',required=True);q.add_argument('--execution-sha256',required=True)
        if name=='_lane':q.add_argument('--batch-source-sha256',required=True)
    a=p.parse_args(argv)
    if a.action=='plan':
        result=make_batch(inputs=a.inputs,build=a.build,times=json.loads(Path(a.times_json).read_text()),
            manifest=a.manifest,output=a.output,cpus=[int(x) for x in a.cpus.split(',')],
            lanes=a.lanes,threads=a.threads,per_lane_gib=a.per_lane_gib,max_attempts=a.max_attempts,
            timeout_seconds=a.timeout_seconds,overall_timeout_seconds=a.overall_timeout_seconds,
            logical=a.logical_cpus,backend=a.backend)
        print(json.dumps(result));return 0
    if a.action=='_lane':return run_lane(a.manifest,a.execution_sha256,a.batch_source_sha256)
    result=run_batch(pc.read_bound(a.manifest,a.execution_sha256),a.execution_sha256)
    print(json.dumps(result));return 0 if result['success'] else 1


if __name__=='__main__':
    raise SystemExit(main())
