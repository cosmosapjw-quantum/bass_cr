"""Fresh, byte-bound full-operator precomputation under an external watchdog.

`plan` hashes inputs and source without loading native libraries. `run` consumes
one create-only output directory. The execution SHA binds a concrete manifest;
it is not a user approval or a scientific certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # also supports python -I
import hpc_provider as hp
from mpi_queue import run_queue
import resource_profile as resources

GiB = 1024**3
SCHEMA = 'BASS_R4U_PHYSICAL_EXECUTION_V1'


def read_bound(path, expected):
    data = Path(path).read_bytes()
    if not isinstance(expected, str) or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('execution manifest byte SHA256 mismatch')
    return json.loads(data)


def _outside_repo(path):
    p = Path(path).resolve()
    if p == hp.REPO or hp.REPO in p.parents:
        raise ValueError('execution manifests and outputs must be outside the source tree')
    return p


def _core_ids(cpus):
    result = []
    for cpu in cpus:
        p = Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
        result.append(((p/'physical_package_id').read_text().strip(),
                       (p/'core_id').read_text().strip()))
    return result


def admit(info, ranks, threads, cpus, per_rank_gib, logical):
    if any(type(x) is not int or x < 1 for x in (ranks, threads)):
        raise ValueError('positive integral rank/thread counts required')
    if threads > 64 or len(cpus) != ranks*threads or len(set(cpus)) != len(cpus):
        raise ValueError('exact disjoint CPU allocation including rank zero required')
    if any(type(c) is not int or c < 0 for c in cpus) or not set(cpus) <= set(info['affinity_cpus']):
        raise ValueError('CPU allocation outside current affinity')
    if not logical and len(set(_core_ids(cpus))) != len(cpus):
        raise ValueError('physical-core allocation contains sibling logical CPUs')
    slots = min(info['usable_cpu_budget'], info['logical_cpus'] if logical else info['physical_cores'])
    if ranks*threads > slots:
        raise ValueError('allocation exceeds actual cgroup/topology CPU budget')
    if not math.isfinite(per_rank_gib) or per_rank_gib <= 0:
        raise ValueError('positive per-rank memory estimate required')
    memory = min(info['memory_limit_bytes'], info['memory_available_bytes'])
    reserve = max(GiB, memory//8)
    requested = math.ceil(per_rank_gib*GiB)*ranks
    if requested > memory-reserve:
        raise ValueError('memory estimate exceeds available budget after reserve')
    # Use the existing R4S planner for MPI resource arithmetic and environment.
    if ranks > 1:
        base = resources.plan(info, ranks, threads, per_rank_gib, logical=logical)
        env = base['environment']
    else:
        env = {k:'1' for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS',
                               'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
    env.update(OMP_NUM_THREADS=str(threads), OMP_DYNAMIC='FALSE', OMP_MAX_ACTIVE_LEVELS='1',
               OMP_PROC_BIND='close', OMP_PLACES='threads' if logical else 'cores',
               BASS_HPC_ADMITTED_CPUS=','.join(map(str,cpus)),
               BASS_HPC_CPU_UNIT='logical' if logical else 'physical_core')
    return {'ranks':ranks,'worker_ranks':1 if ranks == 1 else ranks-1,'threads':threads,
            'cpus':cpus,'logical_cpus_explicit':logical,'per_rank_gib':per_rank_gib,
            'estimated_total_rss_bytes':requested,'memory_reserve_bytes':reserve,
            'memory_budget_bytes':memory-reserve,'rss_is_estimate_not_os_enforcement':True,
            'environment':env,'census':info}


def _host():
    return {'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'machine':platform.machine(),'node':platform.node()}


def _runtime_versions():
    import scipy
    return {'python':sys.version,'platform':platform.platform(),
            'numpy':hp.np.__version__,'scipy':scipy.__version__}


def _binary(path):
    p = Path(path).resolve()
    return {'path':str(p),'sha256':hp.sha(p)}


def _mpi_identity(path):
    p = shutil.which(path)
    if not p:
        raise ValueError('requested OpenMPI launcher unavailable')
    run = subprocess.run([p,'--version'], capture_output=True, text=True, timeout=10, check=True)
    version = run.stdout + run.stderr
    if 'Open MPI' not in version and 'OpenRTE' not in version:
        raise ValueError('OpenMPI launcher required')
    return {**_binary(p),'version':version}


def make_manifest(*, inputs, build, times, output, backend, ranks, threads, cpus,
                  max_attempts, timeout_seconds, per_rank_gib=1., logical=False,
                  contract=None, mpiexec='mpiexec'):
    inputs = Path(inputs).resolve(); build = Path(build).resolve()
    output = _outside_repo(output)
    if output.exists() or not output.parent.is_dir():
        raise ValueError('output must be new, with an existing parent')
    if contract is None:
        contract = json.loads((inputs/'SCIENCE_CONTEXT.json').read_text())['context']['contract']
    context = hp.prepare_context(inputs, build, contract, backend=backend, threads=threads)
    tasks = hp.build_tasks(context['context_id'], times, contract)
    if type(max_attempts) is not int or not 1 <= max_attempts <= len(tasks)*len(tasks[0]['levels']):
        raise ValueError('positive global attempt cap cannot exceed the declared task ladders')
    if not math.isfinite(timeout_seconds) or not 1 <= timeout_seconds <= 86400:
        raise ValueError('hard timeout must be between 1 and 86400 seconds')
    allocation = admit(resources.census(), ranks, threads, cpus, per_rank_gib, logical)
    return {'schema':SCHEMA,'execution_id':str(uuid.uuid4()),'inputs':str(inputs),'build':str(build),
            'output':str(output),'context':context,'tasks':tasks,'resources':allocation,
            'limits':{'max_attempts':max_attempts,'hard_timeout_seconds':timeout_seconds,
                      'queue_timeout_seconds':timeout_seconds},
            'host':_host(),'python':_binary(sys.executable),'runtime_versions':_runtime_versions(),
            'mpi':None if ranks == 1 else _mpi_identity(mpiexec),
            'scope':'fresh bounded full-operator qualification; no propagation or capture',
            'execution_sha_is_content_binding_not_user_approval':True,
            'old_approval_reused':False,'capture':False,'production_admission':'HOLD',
            'all_bound':'OPEN','b_grid':'NO_GO','continuous_trajectory_error_bound':False}


def validate_manifest(m):
    if m['schema'] != SCHEMA or m['host'] != _host():
        raise ValueError('execution schema or exact host/boot identity mismatch')
    if m['runtime_versions'] != _runtime_versions():
        raise ValueError('Python/platform/NumPy/SciPy runtime versions changed')
    if m['python'] != _binary(sys.executable):
        raise ValueError('Python executable changed')
    r = m['resources']; c = m['context']; limits = m['limits']
    fresh = hp.prepare_context(m['inputs'],m['build'],c['qualification_contract'],
                               backend=c['backend'],threads=c['threads'])
    if fresh != c:
        raise ValueError('fresh source/native/input/context identity mismatch')
    times = [float.fromhex(t['time_hex']) for t in m['tasks']]
    if hp.build_tasks(c['context_id'],times,c['qualification_contract']) != m['tasks']:
        raise ValueError('task plan changed')
    if r['threads'] != c['threads']:
        raise ValueError('native and rank thread counts differ')
    maximum = limits['max_attempts']; wall = limits['hard_timeout_seconds']
    if type(maximum) is not int or not 1 <= maximum <= sum(len(t['levels']) for t in m['tasks']):
        raise ValueError('invalid global attempt cap')
    if not math.isfinite(wall) or not 1 <= wall <= 86400 or limits['queue_timeout_seconds'] != wall:
        raise ValueError('invalid external/queue timeout contract')
    # Validate the frozen arithmetic too; current availability is checked per rank.
    expected = admit(r['census'],r['ranks'],r['threads'],r['cpus'],r['per_rank_gib'],r['logical_cpus_explicit'])
    if expected != r:
        raise ValueError('frozen resource admission is inconsistent')
    if (r['ranks'] == 1) != (m['mpi'] is None):
        raise ValueError('serial/MPI manifest mismatch')
    if m['mpi'] is not None and _mpi_identity(m['mpi']['path']) != m['mpi']:
        raise ValueError('OpenMPI launcher changed')
    _outside_repo(m['output'])


def _process(pid=None):
    # /proc may expose an ancestor PID namespace. Keep both the procfs PID and
    # the signal PID in our namespace; never assume os.getpid() indexes /proc.
    proc = Path('/proc/self') if pid is None else Path(f'/proc/{pid}')
    raw = (proc/'stat').read_text()
    fields = raw.rsplit(')',1)[1].split()
    status = (proc/'status').read_text().splitlines()
    ns = next(line.split()[1:] for line in status if line.startswith('NSpid:'))
    return {'pid':int(raw.split(' ',1)[0]),'ppid':int(fields[1]),
            'signal_pid':int(ns[-1]),'pid_namespace':os.readlink(proc/'ns/pid'),
            'start_ticks':int(fields[19])}


def _supervision_check(m, execution_sha):
    rec = json.loads((Path(m['output'])/'SUPERVISOR.json').read_text())
    if rec['execution_sha256'] != execution_sha or time.monotonic() >= rec['deadline_monotonic']:
        raise ValueError('missing matching live external watchdog deadline')
    expected = rec['process']; actual = _process(expected['pid'])
    if actual['start_ticks'] != expected['start_ticks']:
        raise ValueError('watchdog process identity changed')
    pid = _process()['pid']
    for _ in range(100):
        pid = _process(pid)['ppid']
        if pid == expected['pid']:
            return
        if pid <= 1:
            break
    raise ValueError('worker is not a descendant of the external watchdog')


def rank_admission(m, comm, execution_sha):
    rank = comm.Get_rank()
    try:
        _supervision_check(m,execution_sha)
        validate_manifest(m)
        r = m['resources']
        if comm.Get_size() != r['ranks']:
            raise ValueError('actual communicator size differs from manifest')
        for key,value in r['environment'].items():
            if os.environ.get(key) != value:
                raise ValueError('thread/binding environment differs: '+key)
        info = resources.census()
        now = admit(info,r['ranks'],r['threads'],r['cpus'],r['per_rank_gib'],r['logical_cpus_explicit'])
        if info['cpu_model'] != r['census']['cpu_model']:
            raise ValueError('CPU model changed')
        # Preserve the larger frozen reserve even if current free memory is lower.
        if min(info['memory_limit_bytes'],info['memory_available_bytes']) < (
                r['estimated_total_rss_bytes']+r['memory_reserve_bytes']):
            raise ValueError('fresh memory cannot cover frozen RSS plus reserve')
        binding = hp.bind_rank(rank,r['ranks'],r['threads'],r['cpus'])
        return {'ok':True,'rank':rank,'process':_process(),'binding':binding,
                'fresh_memory_budget_bytes':now['memory_budget_bytes'],
                'execution_sha256':execution_sha,'context_id':m['context']['context_id']}
    except Exception as exc:
        return {'ok':False,'rank':rank,'error':type(exc).__name__+': '+str(exc),
                'process':_process()}


def execute(m, comm, execution_sha):
    """All ranks enter; no evaluator exists until every admission has passed."""
    rank = comm.Get_rank(); out = Path(m['output'])
    statuses = comm.allgather(rank_admission(m,comm,execution_sha))
    decision = None
    if rank == 0:
        try:
            admitted = all(s.get('ok') is True for s in statuses)
            hp.write_new(out/'ADMISSION.json',{'execution_sha256':execution_sha,
                         'admitted':admitted,'ranks':statuses,'native_calls_before_admission':0})
            decision = {'ok':admitted,'error':'one or more ranks failed admission'}
        except Exception as exc:
            decision = {'ok':False,'error':'admission receipt failed: '+str(exc)}
    decision = comm.bcast(decision,root=0)
    if not decision['ok']:
        raise RuntimeError(decision['error'])
    evaluator = None
    def worker(task,reserve):
        nonlocal evaluator
        if evaluator is None:
            evaluator = hp.PinnedEvaluator(m['inputs'],m['build'],m['context'])
        return hp.qualified_task(task,reserve,evaluator,m['context']['context_id'],
                                 m['context']['qualification_contract'])
    rows = run_queue(comm,m['tasks'] if rank == 0 else None,worker,
                     max_attempts=m['limits']['max_attempts'],output_dir=out/'queue',
                     timeout_seconds=m['limits']['queue_timeout_seconds'])
    result = None
    if rank == 0:
        try:
            cache = hp.collect_cache(rows,out/'cache',m['context']['context_id'],m['context']['qualification_contract'])
            result = {'ok':True,'execution_sha256':execution_sha,'context_id':m['context']['context_id'],
                      'cache':cache,'capture':False,'production_admission':'HOLD'}
            hp.write_new(out/'RESULT.json',result)
        except Exception as exc:
            result = {'ok':False,'error':type(exc).__name__+': '+str(exc)}
    result = comm.bcast(result,root=0)
    if not result['ok']:
        raise RuntimeError(result['error'])
    return result if rank == 0 else None


def _kill_workers(child, out):
    # MPI descendants may have their own process groups. Admission records exact
    # rank PIDs/start times before any native evaluation; kill those as well.
    try:
        rows = json.loads((out/'ADMISSION.json').read_text())['ranks']
        for row in rows:
            p = row.get('process',{})
            try:
                actual = _process(p['pid'])
                if (actual['start_ticks'] == p['start_ticks'] and
                        actual['pid_namespace'] == _process()['pid_namespace']):
                    os.kill(actual['signal_pid'],signal.SIGKILL)
            except (OSError,KeyError,ValueError):
                pass
    except (OSError,ValueError,KeyError):
        pass
    try:
        os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:
        pass


def supervise(command, out, timeout_seconds, execution_sha, env):
    """Hard OS watchdog, outside the interpreter doing scientific work."""
    out = Path(out); start = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    hp.write_new(out/'SUPERVISOR.json',{'execution_sha256':execution_sha,
                  'process':_process(),'command':command,
                  'deadline_monotonic':start+timeout_seconds,'hard_timeout_seconds':timeout_seconds})
    child = None; timed_out = False; error = None; code = None
    try:
        with (out/'stdout.log').open('xb') as stdout, (out/'stderr.log').open('xb') as stderr:
            child = subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env,start_new_session=True)
            try:
                code = child.wait(timeout=max(0.001,start+timeout_seconds-time.monotonic()))
                if code != 0:
                    _kill_workers(child,out)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill_workers(child,out)
                code = child.wait(timeout=10)
    except BaseException as exc:
        error = type(exc).__name__+': '+str(exc)
        if child is not None:
            _kill_workers(child,out)
            child.wait(timeout=10)
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):
            code = 130
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    measured = {'max_child_rss_kib':usage.ru_maxrss,
                'user_cpu_seconds':usage.ru_utime-usage_before.ru_utime,
                'system_cpu_seconds':usage.ru_stime-usage_before.ru_stime,
                'minor_page_faults':usage.ru_minflt-usage_before.ru_minflt,
                'major_page_faults':usage.ru_majflt-usage_before.ru_majflt,
                'scope':'RUSAGE_CHILDREN; RSS is lifetime max waited-child high-water, not summed MPI peak'}
    result = {'execution_sha256':execution_sha,'status':'HARD_TIMEOUT' if timed_out else
              ('EXITED' if error is None else 'SUPERVISOR_ERROR'),
              'returncode':code,'wall_seconds':time.monotonic()-start,'error':error,
              'resources_measured':measured,
              'success':not timed_out and error is None and code == 0}
    hp.write_new(out/'SUPERVISOR_RESULT.json',result)
    return result


def run_manifest(m, execution_sha):
    validate_manifest(m)
    out = Path(m['output']); out.mkdir(exist_ok=False)
    hp.write_new(out/'EXECUTION.json',m)
    # Bind the copied manifest's bytes separately; the supplied digest remains
    # the original plan's byte identity in every receipt.
    copied_sha = hp.sha(out/'EXECUTION.json')
    env = os.environ.copy(); env.update(m['resources']['environment'])
    command = [m['python']['path'],'-I',str(Path(__file__).resolve()),'_execute',
               '--manifest',str(out/'EXECUTION.json'),'--execution-sha256',copied_sha,
               '--plan-sha256',execution_sha]
    if m['mpi'] is not None:
        # OS bind_rank enforces the explicit, disjoint allocation before native
        # load. No root override, oversubscription, or launcher fallback exists.
        command = [m['mpi']['path'],'-np',str(m['resources']['ranks']),
                   '--nooversubscribe','--bind-to','none']+command
    return supervise(command,out,m['limits']['hard_timeout_seconds'],execution_sha,env)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    sub = parser.add_subparsers(dest='action',required=True)
    plan = sub.add_parser('plan',allow_abbrev=False)
    for key in ('inputs','build','times-json','manifest','output','cpus'):
        plan.add_argument('--'+key,required=True)
    plan.add_argument('--backend',choices=('fortran','reference'),default='fortran')
    plan.add_argument('--ranks',type=int,default=1);plan.add_argument('--threads',type=int,default=1)
    plan.add_argument('--max-attempts',type=int,required=True)
    plan.add_argument('--timeout-seconds',type=float,required=True)
    plan.add_argument('--per-rank-gib',type=float,default=1.)
    plan.add_argument('--logical-cpus',action='store_true');plan.add_argument('--contract')
    plan.add_argument('--mpiexec',default='mpiexec')
    for name in ('run','_execute'):
        p = sub.add_parser(name,allow_abbrev=False)
        p.add_argument('--manifest',required=True);p.add_argument('--execution-sha256',required=True)
        if name == '_execute':p.add_argument('--plan-sha256',required=True)
    a = parser.parse_args(argv)
    if a.action == 'plan':
        times = json.loads(Path(a.times_json).read_text())
        times = [float.fromhex(t) if isinstance(t,str) else float(t) for t in times]
        contract = None if a.contract is None else json.loads(Path(a.contract).read_text())
        m = make_manifest(inputs=a.inputs,build=a.build,times=times,output=a.output,
             backend=a.backend,ranks=a.ranks,threads=a.threads,cpus=[int(x) for x in a.cpus.split(',')],
             max_attempts=a.max_attempts,timeout_seconds=a.timeout_seconds,per_rank_gib=a.per_rank_gib,
             logical=a.logical_cpus,contract=contract,mpiexec=a.mpiexec)
        path = _outside_repo(a.manifest)
        hp.write_new(path,m)
        print(json.dumps({'manifest':str(path),'execution_sha256':hp.sha(path),
                          'context_id':m['context']['context_id'],'native_calls':0}))
        return 0
    m = read_bound(a.manifest,a.execution_sha256)
    if a.action == 'run':
        result = run_manifest(m,a.execution_sha256)
        print(json.dumps(result));return 0 if result['success'] else 1
    comm = hp.SerialComm()
    if m['resources']['ranks'] > 1:
        from mpi4py import MPI
        if MPI.get_vendor()[0] != 'Open MPI':
            raise ValueError('mpi4py must use OpenMPI')
        comm = MPI.COMM_WORLD
    try:
        execute(m,comm,a.plan_sha256)
    except Exception as exc:
        if comm.Get_rank() == 0:
            hp.write_new(Path(m['output'])/'FAILURE.json',{'execution_sha256':a.plan_sha256,
                          'type':type(exc).__name__,'message':str(exc),'capture':False})
        raise
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
