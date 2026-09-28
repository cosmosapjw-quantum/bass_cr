"""Host admission and one-thread worker policy for the approved 64-vCPU class."""
import os
from pathlib import Path
import resource


THREAD_POLICY = {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                 'MKL_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1',
                 'OMP_DYNAMIC': 'FALSE', 'MKL_DYNAMIC': 'FALSE'}


def enforce_thread_policy():
    os.environ.update(THREAD_POLICY)
    return dict(THREAD_POLICY)


def select_workers(affinity_count, mem_total_bytes, remaining_tasks):
    if type(affinity_count) is not int or affinity_count < 64:
        raise RuntimeError('R2_HOST_MISMATCH: at least 64 affinity CPUs required')
    if type(mem_total_bytes) is not int or mem_total_bytes < 120_000_000_000:
        raise RuntimeError('R2_MEMORY_BLOCKED: configured memory below contract')
    if type(remaining_tasks) is not int or remaining_tasks < 0:
        raise ValueError('nonnegative remaining task count required')
    return min(60, affinity_count - 4, remaining_tasks)


def memory_info(path='/proc/meminfo'):
    values = {}
    for line in Path(path).read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemTotal', 'MemAvailable'):
            values[key] = int(value.strip().split()[0]) * 1024
    if set(values) != {'MemTotal', 'MemAvailable'}:
        raise RuntimeError('R2_MEMORY_BLOCKED: meminfo missing')
    return values


def host_receipt(remaining_tasks):
    affinity = len(os.sched_getaffinity(0))
    memory = memory_info()
    workers = select_workers(affinity, memory['MemTotal'], remaining_tasks)
    if memory['MemAvailable'] < 5_368_709_120:
        raise RuntimeError('R2_MEMORY_BLOCKED: available memory below 5 GiB')
    return {'affinity_count': affinity, 'mem_total_bytes': memory['MemTotal'],
            'mem_available_bytes': memory['MemAvailable'], 'workers': workers,
            'parent_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
