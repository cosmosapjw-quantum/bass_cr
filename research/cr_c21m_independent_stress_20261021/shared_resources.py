"""Observed Linux resources and cooperative leases for independent C21M cases.

No nominal NCP specification is treated as an observed allocation. CPU55 is
always excluded. Only this process's own flock handles are released.
"""
from __future__ import annotations

import fcntl
import math
import os
from pathlib import Path
import platform
import socket
import time

GIB = 1024**3
MIB = 1024**2
PROTECTED_CPU = 55
THREAD_VARIABLES = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                    'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
                    'VECLIB_MAXIMUM_THREADS')


def cpu_set(value):
    result = set()
    for part in value.strip().split(','):
        if not part:
            continue
        bounds = part.split('-')
        lo, hi = int(bounds[0]), int(bounds[-1])
        if lo < 0 or hi < lo or len(bounds) > 2:
            raise ValueError('INVALID_CPU_LIST')
        result.update(range(lo, hi + 1))
    return result


def read_optional(path):
    try:
        return Path(path).read_text().strip()
    except (FileNotFoundError, PermissionError):
        return None


def cgroup_locations(cgroup_text=None, mountinfo_text=None):
    """Resolve v1/v2 memberships against visible cgroup mounts and ancestors."""
    cgroup_text = Path('/proc/self/cgroup').read_text() if cgroup_text is None else cgroup_text
    mountinfo_text = Path('/proc/self/mountinfo').read_text() if mountinfo_text is None else mountinfo_text
    memberships = []
    for line in cgroup_text.splitlines():
        _, controllers, relative = line.split(':', 2)
        memberships.append((set(controllers.split(',')) - {''}, relative))
    locations = []
    for line in mountinfo_text.splitlines():
        if ' - ' not in line:
            continue
        left, right = line.split(' - ', 1)
        a, b = left.split(), right.split()
        if b[0] not in ('cgroup', 'cgroup2'):
            continue
        mountroot = a[3].replace('\\040', ' ')
        mount = Path(a[4].replace('\\040', ' '))
        controllers = set(b[2].split(',')) if len(b) > 2 else set()
        for group_controllers, group_path in memberships:
            if b[0] == 'cgroup2' and group_controllers:
                continue
            if b[0] == 'cgroup' and not (controllers & group_controllers):
                continue
            if group_path == mountroot:
                relative = ''
            elif group_path.startswith(mountroot.rstrip('/') + '/'):
                relative = group_path[len(mountroot):].lstrip('/')
            else:
                relative = ''  # namespace exposes only its mounted root
            candidate = (mount / relative).resolve()
            fallback = not candidate.is_relative_to(mount.resolve()) or not candidate.is_dir()
            if fallback:
                candidate = mount
            while candidate.is_relative_to(mount):
                row = {'path': str(candidate), 'version': 2 if b[0] == 'cgroup2' else 1,
                       'controllers': sorted(group_controllers),
                       'namespace_root_fallback': fallback}
                if row not in locations:
                    locations.append(row)
                if candidate == mount:
                    break
                candidate = candidate.parent
    return locations


def decode_cgroup(location, reader=read_optional):
    p = Path(location['path'])
    row = dict(location)
    if row['version'] == 2:
        names = ('cpu.max', 'cpu.stat', 'cpuset.cpus.effective', 'memory.max', 'memory.current')
        values = {n: reader(p / n) for n in names}
        quota = values['cpu.max']
        row['quota_cores'] = None if not quota or quota.split()[0] == 'max' else int(quota.split()[0]) / int(quota.split()[1])
        row['cpuset'] = values['cpuset.cpus.effective']
        stats = dict(line.split() for line in (values['cpu.stat'] or '').splitlines())
        row['usage_seconds'] = int(stats['usage_usec']) / 1e6 if 'usage_usec' in stats else None
        limit, usage = values['memory.max'], values['memory.current']
    else:
        names = ('cpu.cfs_quota_us', 'cpu.cfs_period_us', 'cpuacct.usage',
                 'cpuset.effective_cpus', 'cpuset.cpus',
                 'memory.limit_in_bytes', 'memory.usage_in_bytes')
        values = {n: reader(p / n) for n in names}
        quota, period = values['cpu.cfs_quota_us'], values['cpu.cfs_period_us']
        row['quota_cores'] = int(quota) / int(period) if quota and period and int(quota) >= 0 else None
        row['cpuset'] = values['cpuset.effective_cpus'] or values['cpuset.cpus']
        row['usage_seconds'] = int(values['cpuacct.usage']) / 1e9 if values['cpuacct.usage'] else None
        limit, usage = values['memory.limit_in_bytes'], values['memory.usage_in_bytes']
    row['memory_limit'] = int(limit) if limit and limit != 'max' and int(limit) < 2**60 else None
    row['memory_remaining'] = max(0, row['memory_limit'] - int(usage)) if row['memory_limit'] is not None and usage is not None else None
    row['raw'] = values
    return row


def snapshot(affinity=None):
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemTotal', 'MemAvailable'):
            mem[key] = int(value.split()[0]) * 1024
    original = set(os.sched_getaffinity(0) if affinity is None else affinity)
    cpus = set(original)
    rows = [decode_cgroup(x) for x in cgroup_locations()]
    for row in rows:
        if row['cpuset']:
            cpus &= cpu_set(row['cpuset'])
    quotas = [r['quota_cores'] for r in rows if r['quota_cores'] is not None]
    limits = [r['memory_limit'] for r in rows if r['memory_limit'] is not None]
    remaining = [r['memory_remaining'] for r in rows if r['memory_remaining'] is not None]
    return {'affinity': sorted(original), 'allowed_cpus': sorted(cpus - {PROTECTED_CPU}),
            'quota': min(quotas) if quotas else None,
            'memory_limit': min([mem['MemTotal']] + limits),
            'memory_available': min([mem['MemAvailable']] + remaining),
            'cgroups': rows, 'cgroup_scope': 'visible memberships and visible ancestors',
            'protected_cpu': PROTECTED_CPU,
            'host_load_average': list(os.getloadavg()),
            'observed_monotonic': time.monotonic()}


def memory_budget():
    # Conservative analytical allocation budget, not a measured peak claim.
    # Canonical q/mu subcell grid: 24 * 12 * 3^2 = 2592 nodes.
    arrays = 64 * (24 * 12 * 3**2) * 8
    trajectories = 128 * 101 * 8
    return {'worker_budget_bytes': 512 * MIB, 'coordinator_budget_bytes': 256 * MIB,
            'array_and_trajectory_allowance_bytes': arrays + trajectories,
            'basis': '64 FP64 node buffers + 128 saved scalar channels; 512 MiB worker ceiling includes Python/NumPy/SciPy and a large allocation margin',
            'measured_peak_claim': False}


def capacity(s, workers, remaining_tasks, restrict=None, external_cores=0.):
    if workers < 1 or remaining_tasks < 0:
        raise ValueError('INVALID_WORKER_OR_TASK_COUNT')
    cpus = set(s['allowed_cpus']) - {PROTECTED_CPU}
    if restrict is not None:
        cpus &= set(restrict)
    slots = len(cpus)
    if s['quota'] is not None:
        slots = min(slots, max(0, math.floor(s['quota'] - max(0., external_cores) + 1e-9)))
    budget = memory_budget()
    reserve = max(GIB, math.ceil(s['memory_limit'] / 8))
    usable = max(0, s['memory_available'] - reserve - budget['coordinator_budget_bytes'])
    memory_slots = usable // budget['worker_budget_bytes']
    n = max(0, min(workers, remaining_tasks, slots - 1, memory_slots))
    return {'cpu_candidates': sorted(cpus), 'maximum_workers': n,
            'cpu_slots_including_coordinator': slots,
            'external_cgroup_cores_observed': external_cores,
            'memory_reserve_bytes': reserve, 'memory_worker_slots': memory_slots, **budget}


def proc_cpu():
    out = {}
    for line in Path('/proc/stat').read_text().splitlines():
        words = line.split()
        if words and words[0].startswith('cpu') and words[0][3:].isdigit():
            values = list(map(int, words[1:]))
            out[int(words[0][3:])] = (sum(values[:8]), values[3] + values[4])
    return out


def process_seconds(pid):
    try:
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        return (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')
    except (FileNotFoundError, ProcessLookupError):
        return 0.


def observe_load(process_ids=(), affinity=None, seconds=.2):
    before = snapshot(affinity)
    cpu_before = proc_cpu()
    own_before = sum(process_seconds(p) for p in set(process_ids) | {os.getpid()})
    started = time.monotonic()
    time.sleep(seconds)
    after = snapshot(affinity)
    elapsed = time.monotonic() - started
    own_after = sum(process_seconds(p) for p in set(process_ids) | {os.getpid()})
    cpu_after = proc_cpu()
    loads = {}
    for cpu, (total, idle) in cpu_after.items():
        old = cpu_before.get(cpu)
        if old is not None:
            dt = total - old[0]
            loads[cpu] = min(1., max(0., 1 - (idle - old[1]) / dt)) if dt else 1.
    old_groups = {r['path']: r for r in before['cgroups']}
    quota_available = []
    quota_observations = []
    own_rate = max(0., own_after - own_before) / elapsed
    for row in after['cgroups']:
        old = old_groups.get(row['path'], {})
        if row['quota_cores'] is not None and row['usage_seconds'] is not None and old.get('usage_seconds') is not None:
            rate = max(0., row['usage_seconds'] - old['usage_seconds']) / elapsed
            external = max(0., rate - own_rate)
            quota_available.append(max(0., row['quota_cores'] - external))
            quota_observations.append({'path': row['path'], 'quota_cores': row['quota_cores'],
                                       'total_group_cores': rate, 'external_cores': external})
    # Apply each ancestor's usage to that ancestor's own quota. Subtracting
    # the largest ancestor usage from the smallest descendant quota would
    # incorrectly block an otherwise available descendant allocation.
    available = min(quota_available) if quota_available else after['quota']
    effective_external = max(0., after['quota'] - available) if after['quota'] is not None and available is not None else 0.
    return {'snapshot': after, 'per_cpu': loads,
            'external_cgroup_cores': effective_external,
            'quota_observations': quota_observations,
            'available_quota_cores': available,
            'measurement_seconds': elapsed, 'own_process_cores': own_rate,
            'idle_threshold': .35}


def acquire_cpu(directory, cpu):
    handle = (Path(directory) / f'cpu_{cpu}.lock').open('a+b')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def try_admit(workers, remaining_tasks, lease_dir, restrict=None, affinity=None):
    observed = observe_load(affinity=affinity)
    cap = capacity(observed['snapshot'], workers, remaining_tasks, restrict,
                   observed['external_cgroup_cores'])
    observed['capacity'] = cap
    handles = []
    if cap['maximum_workers']:
        Path(lease_dir).mkdir(parents=True, exist_ok=True)
        for cpu in sorted(cap['cpu_candidates'], key=lambda c: (observed['per_cpu'].get(c, 1.), c)):
            if observed['per_cpu'].get(cpu, 1.) > observed['idle_threshold']:
                continue
            handle = acquire_cpu(lease_dir, cpu)
            if handle is not None:
                handles.append((cpu, handle))
            if len(handles) >= cap['maximum_workers'] + 1:
                break
    if len(handles) < 2:
        for _, handle in handles:
            handle.close()
        return None, [], observed
    plan = {'coordinator_cpu': handles[0][0], 'worker_cpus': [c for c, _ in handles[1:]],
            'lease_directory': str(Path(lease_dir).resolve()), 'observation': observed,
            'unmanaged_jobs': 'observed only; cooperative leases cover the same directory'}
    return plan, handles, observed


def dispatch_cpus(observation, active_cpus, idle_cpus, workers, remaining_tasks,
                  leased_cpus, coordinator_cpu):
    """Shrink new dispatch as external load grows; never interrupt active cases."""
    cap = capacity(observation['snapshot'], workers, remaining_tasks + len(active_cpus),
                   set(leased_cpus) | {coordinator_cpu},
                   observation['external_cgroup_cores'])
    allowance = max(0, cap['maximum_workers'] - len(active_cpus))
    eligible = [c for c in idle_cpus if c in cap['cpu_candidates']
                and observation['per_cpu'].get(c, 1.) <= observation['idle_threshold']]
    return sorted(eligible, key=lambda c: (observation['per_cpu'].get(c, 1.), c))[:min(allowance, remaining_tasks)]


def execution_metadata(site):
    return {'execution_site': site, 'execution_site_basis': 'operator-declared; host identity recorded separately',
            'NCP_execution': site == 'ncp', 'observed_hostname': socket.gethostname(),
            'observed_platform': platform.platform()}
