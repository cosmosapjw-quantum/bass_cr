"""Create-only C21M independent-stress runs with bounded adaptive dispatch.

Requires an explicit new JSON grid; never generates or reruns the C21L 81 grid.
--plan-only creates neither an output directory nor a lease directory.
--resume admits only never-started cases and verifies completed raw + receipts.
"""
from __future__ import annotations

import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['OMP_DYNAMIC'] = 'FALSE'
os.environ['OMP_MAX_ACTIVE_LEVELS'] = '1'
import sys
sys.dont_write_bytecode = True

import argparse
import csv
import fcntl
import hashlib
import importlib
import importlib.metadata
import json
import math
import multiprocessing as mp
from pathlib import Path
import platform
import queue
import re
import resource
import tempfile
import time
import traceback

import shared_resources as resources

HERE = Path(__file__).resolve().parent
CODE_FILES = ('builder.py', 'shared_runner.py', 'shared_resources.py')


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    return digest_bytes(Path(path).read_bytes())


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())


def canonical_digest(value):
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def load_grid(path):
    raw = Path(path).read_bytes()
    grid = json.loads(raw)
    if grid.get('schema') != 'C21M_GRID_V1' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', grid.get('run_id', '')):
        raise ValueError('GRID_SCHEMA_OR_RUN_ID')
    cases = grid.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('NONEMPTY_EXPLICIT_CASES_REQUIRED')
    ids, targets = set(), set()
    normalized = []
    for case in cases:
        key = case.get('case_id', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', key) or key in ids:
            raise ValueError('INVALID_OR_DUPLICATE_CASE_ID')
        values = tuple(case.get(k) for k in ('S0', 'Pm0', 'Pr0'))
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ValueError('NONFINITE_OR_MISSING_SIGNED_INITIAL_TARGET')
        values = tuple(map(float, values))
        if values in targets:
            raise ValueError('DUPLICATE_PHYSICAL_CASE_IN_GRID')
        ids.add(key)
        targets.add(values)
        normalized.append(dict(case_id=key, **dict(zip(('S0', 'Pm0', 'Pr0'), values))))
    return {'schema': grid['schema'], 'run_id': grid['run_id'], 'cases': normalized}, digest_bytes(raw)


def manifest_for(grid, grid_hash, site, backend_module='builder'):
    backend = importlib.import_module(backend_module)
    # This constructs initial quadrature/operator data, never integrates an ODE.
    builder = backend.IndependentStressBuilder()
    identity = builder.identity()
    del builder
    contract = {'schema': 'C21M_INDEPENDENT_STRESS_RUN_V1', 'grid': grid,
                'grid_file_sha256': grid_hash, 'source': identity,
                'code_sha256': {f: digest_file(HERE / f) for f in CODE_FILES},
                'software': {'python': platform.python_version(),
                             'numpy': importlib.metadata.version('numpy'),
                             'scipy': importlib.metadata.version('scipy')},
                'signed_coordinates': 'full Frobenius (S0, Pm0, Pr0); retain signs',
                'execution_site': site, 'site_basis': 'operator declaration',
                'science_scope': 'preliminary non-tilted collisionless LRS Bianchi I' if backend_module == 'builder' else 'OPERATIONAL_TEST_DOUBLE_NO_SCIENCE',
                'operational_test_double': backend_module != 'builder',
                'global_error_bound': None}
    return contract, canonical_digest(contract)


def resume_status(directory, identity, case):
    directory = Path(directory)
    if not directory.exists():
        return 'NOT_STARTED'
    reservation_path = directory / 'RESERVATION.json'
    if not reservation_path.is_file():
        raise RuntimeError('CASE_RESERVATION_MISSING:' + str(directory))
    reservation = json.loads(reservation_path.read_text())
    if reservation.get('identity') != identity or reservation.get('case') != case:
        raise RuntimeError('CASE_INPUT_IDENTITY_MISMATCH:' + str(directory))
    result, started, seal = (directory / n for n in ('RESULT.json', 'STARTED.json', 'COMPLETE.json'))
    if seal.exists():
        mark = json.loads(seal.read_text())
        if mark.get('identity') != identity or mark.get('case_id') != case['case_id']:
            raise RuntimeError('COMPLETE_IDENTITY_MISMATCH')
        raw = directory / 'history.npz'
        if not result.is_file() or not raw.is_file() or digest_file(result) != mark['result_sha256'] or digest_file(raw) != mark['history_sha256']:
            raise RuntimeError('COMPLETED_RAW_OR_RECEIPT_CHANGED:' + str(directory))
        receipt = json.loads(result.read_text())
        if receipt.get('identity') != identity or receipt.get('case') != case or receipt.get('status') != 'COMPLETE' or receipt.get('history_sha256') != mark['history_sha256']:
            raise RuntimeError('COMPLETED_RECEIPT_BINDING_MISMATCH')
        return 'COMPLETE'
    if result.exists():
        receipt = json.loads(result.read_text())
        if receipt.get('identity') != identity or receipt.get('case') != case:
            raise RuntimeError('FAILED_OR_UNSEALED_RECEIPT_BINDING_MISMATCH')
        return 'FAILED' if receipt.get('status') == 'FAILED' else 'INTERRUPTED_UNSEALED'
    return 'INTERRUPTED_NO_AUTORETRY' if started.exists() else 'NOT_STARTED'


def verify_worker_contract(template, expected_source, expected_code):
    if {name: digest_file(HERE / name) for name in CODE_FILES} != expected_code:
        raise RuntimeError('WORKER_CODE_IDENTITY_MISMATCH')
    if template.identity() != expected_source:
        raise RuntimeError('WORKER_SOURCE_IDENTITY_MISMATCH')


def worker(cpu, tasks, results, site, backend_module, expected_source, expected_code):
    os.sched_setaffinity(0, {cpu})
    import numpy as np
    try:
        backend = importlib.import_module(backend_module)
        template = backend.IndependentStressBuilder()
        verify_worker_contract(template, expected_source, expected_code)
    except BaseException:
        results.put({'kind': 'INIT_FAILED', 'cpu': cpu, 'error': traceback.format_exc()})
        return
    results.put({'kind': 'READY', 'cpu': cpu})
    while True:
        job = tasks.get()
        if job is None:
            return
        case, path, identity = job
        directory = Path(path)
        started = time.monotonic()
        try:
            write_new(directory / 'STARTED.json', {'case': case, 'identity': identity,
                      'pid': os.getpid(), 'cpu': cpu,
                      'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            receipt, history = backend.solve_case(template, case['S0'], case['Pm0'], case['Pr0'])
            with (directory / 'history.npz').open('xb') as handle:
                np.savez_compressed(handle, **history)
                handle.flush()
                os.fsync(handle.fileno())
            raw_hash = digest_file(directory / 'history.npz')
            receipt.update(status='COMPLETE', case=case, identity=identity,
                           history_sha256=raw_hash, total_worker_wall_s=time.monotonic() - started,
                           operational_test_double=backend_module != 'builder',
                           runtime={'pid': os.getpid(), 'cpu': cpu,
                                    'affinity': sorted(os.sched_getaffinity(0)),
                                    'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                                    'peak_rss_scope': 'process high-water including prior cases',
                                    'observed_thread_count_at_return': len(list(Path('/proc/self/task').iterdir())),
                                    'threads': {k: os.environ[k] for k in resources.THREAD_VARIABLES},
                                    **resources.execution_metadata(site)})
            write_new(directory / 'RESULT.json', receipt)
            write_new(directory / 'COMPLETE.json', {'identity': identity,
                      'case_id': case['case_id'], 'history_sha256': raw_hash,
                      'result_sha256': digest_file(directory / 'RESULT.json')})
            results.put({'kind': 'DONE', 'case_id': case['case_id'], 'status': 'COMPLETE', 'cpu': cpu})
        except BaseException:
            error = traceback.format_exc()
            if not (directory / 'RESULT.json').exists():
                write_new(directory / 'RESULT.json', {'status': 'FAILED', 'case': case,
                          'identity': identity, 'error': error,
                          'operational_test_double': backend_module != 'builder',
                          'runtime': resources.execution_metadata(site), 'global_error_bound': None})
            results.put({'kind': 'DONE', 'case_id': case['case_id'], 'status': 'FAILED', 'cpu': cpu, 'error': error})


def summarize(output, grid, identity, attempt, site):
    rows, states = [], {}
    for case in grid['cases']:
        directory = output / 'cases' / case['case_id']
        state = resume_status(directory, identity, case)
        states[case['case_id']] = state
        row = dict(case, status=state)
        if state == 'COMPLETE':
            receipt = json.loads((directory / 'RESULT.json').read_text())
            row.update({key + '_end': value for key, value in receipt['endpoint'].items()})
            row.update(receipt.get('diagnostics', {}))
            row.update(solver_wall_s=receipt.get('solver_wall_s'), nfev=receipt.get('nfev'))
        rows.append(row)
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with (output / f'endpoints_{attempt}.csv').open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    counts = {state: list(states.values()).count(state) for state in sorted(set(states.values()))}
    summary = {'status': 'COMPLETE_SCOPED' if counts.get('COMPLETE') == len(grid['cases']) else 'PARTIAL',
               'identity': identity, 'run_id': grid['run_id'], 'attempt': attempt,
               'requested_cases': len(grid['cases']), 'completion_counts': counts,
               'states': states, 'global_error_bound': None,
               'performance_benchmark': False, **resources.execution_metadata(site)}
    write_new(output / f'SUMMARY_{attempt}.json', summary)
    return summary


def run(args, _backend_module='builder'):
    # Legacy source imports pyplot. Confine its optional cache to this attempt;
    # preserve the caller's configuration and leave no persistent plan cache.
    previous_mpl = os.environ.get('MPLCONFIGDIR')
    with tempfile.TemporaryDirectory(prefix='c21m_mpl_') as mpl:
        os.environ['MPLCONFIGDIR'] = mpl
        try:
            return _run_scoped(args, _backend_module)
        finally:
            if previous_mpl is None:
                os.environ.pop('MPLCONFIGDIR', None)
            else:
                os.environ['MPLCONFIGDIR'] = previous_mpl


def _run_scoped(args, _backend_module='builder'):
    grid, grid_hash = load_grid(args.grid)
    manifest, identity = manifest_for(grid, grid_hash, args.execution_site, _backend_module)
    output = args.output.resolve()
    restriction = resources.cpu_set(args.cpu_list) if args.cpu_list else None
    original_affinity = set(os.sched_getaffinity(0))
    if args.workers < 1 or not 0 < args.timeout_seconds <= 86400 or not 0 <= args.active_grace_seconds <= 3600:
        raise ValueError('INVALID_WORKER_OR_BOUNDED_TIME_BUDGET')
    if args.plan_only:
        observed = resources.snapshot(original_affinity)
        plan = {'identity': identity, 'run_id': grid['run_id'],
                'case_count': len(grid['cases']), 'manifest': manifest,
                'snapshot': observed,
                'capacity_upper_bound_before_idle_and_lease_checks': resources.capacity(observed, args.workers, len(grid['cases']), restriction),
                'execution': 'NOT_RUN', 'output_created': False, 'leases_acquired': False}
        print(json.dumps(plan, indent=2, allow_nan=False))
        return 0
    if args.resume:
        if not output.is_dir() or json.loads((output / 'MANIFEST.json').read_text()) != {'identity': identity, 'manifest': manifest}:
            raise RuntimeError('RESUME_MANIFEST_SOURCE_GRID_OR_SOFTWARE_MISMATCH')
    else:
        output.mkdir(parents=True, exist_ok=False)
        (output / 'cases').mkdir()
        write_new(output / 'MANIFEST.json', {'identity': identity, 'manifest': manifest})
    lock = (output / 'coordinator.lock').open('a+b')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError('OUTPUT_COORDINATOR_BUSY')
    attempt = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '_' + str(os.getpid()) + '_' + str(time.monotonic_ns())
    handles, processes, queues = [], {}, {}
    active, idle, failed_workers = {}, set(), set()
    started = time.monotonic()
    deadline = started + args.timeout_seconds
    failure = None
    pending = []
    events = (output / f'EVENTS_{attempt}.jsonl').open('x')

    def event(value):
        item = {'elapsed_s': time.monotonic() - started, **value}
        events.write(json.dumps(item, sort_keys=True, allow_nan=False) + '\n')
        events.flush()
        print(json.dumps(item, sort_keys=True, allow_nan=False), flush=True)

    try:
        pending = [case for case in grid['cases'] if resume_status(output / 'cases' / case['case_id'], identity, case) == 'NOT_STARTED']
        event({'kind': 'ATTEMPT', 'pending_never_started': len(pending), 'case_count': len(grid['cases']),
               'operational_test_double': _backend_module != 'builder'})
        if pending:
            plan = None
            while plan is None and time.monotonic() < deadline:
                plan, handles, observation = resources.try_admit(min(args.workers, len(pending)), len(pending), args.lease_dir, restriction, original_affinity)
                if plan is None:
                    event({'kind': 'WAIT_FOR_SHARED_RESOURCES', 'observation': observation})
                    time.sleep(.5)
            if plan is None:
                failure = 'RESOURCE_WAIT_BUDGET_EXPIRED; no case started'
            else:
                write_new(output / f'RESOURCES_{attempt}.json', {**plan, **resources.execution_metadata(args.execution_site)})
                os.sched_setaffinity(0, {plan['coordinator_cpu']})
                ctx = mp.get_context('spawn')
                results = ctx.Queue(maxsize=2 * len(plan['worker_cpus']) + 1)
                for cpu in plan['worker_cpus']:
                    tasks = ctx.Queue(maxsize=1)
                    process = ctx.Process(target=worker, args=(cpu, tasks, results, args.execution_site, _backend_module,
                                                              manifest['source'], manifest['code_sha256']))
                    process.start()
                    processes[cpu], queues[cpu] = process, tasks
                last_observe = -math.inf
                observation = plan['observation']
                while pending or active or any(p.is_alive() and c not in idle and c not in failed_workers for c, p in processes.items()):
                    try:
                        message = results.get(timeout=.1)
                        cpu = message['cpu']
                        if message['kind'] == 'READY':
                            idle.add(cpu)
                        elif message['kind'] == 'DONE':
                            active.pop(cpu, None)
                            idle.add(cpu)
                        else:
                            failed_workers.add(cpu)
                            idle.discard(cpu)
                        event(message)
                    except queue.Empty:
                        pass
                    for cpu, process in processes.items():
                        if not process.is_alive() and process.exitcode is not None and cpu not in failed_workers:
                            event({'kind': 'OWN_WORKER_EXITED', 'cpu': cpu, 'exitcode': process.exitcode, 'active_case': active.pop(cpu, None)})
                            failed_workers.add(cpu)
                            idle.discard(cpu)
                    now = time.monotonic()
                    if now >= deadline:
                        failure = 'DISPATCH_BUDGET_EXPIRED; active cases may complete within drain grace'
                        if not active or now >= deadline + args.active_grace_seconds:
                            break
                    if pending and now < deadline and idle:
                        if now - last_observe >= .5:
                            observation = resources.observe_load([p.pid for p in processes.values() if p.is_alive()], original_affinity)
                            last_observe = time.monotonic()
                            event({'kind': 'RESOURCE_REFRESH', 'observation': observation})
                        live_idle = {cpu for cpu in idle if cpu not in failed_workers and processes[cpu].is_alive()}
                        cpus = resources.dispatch_cpus(observation, set(active), live_idle, len(processes), len(pending), set(processes), plan['coordinator_cpu'])
                        for cpu in cpus:
                            case = pending.pop(0)
                            directory = output / 'cases' / case['case_id']
                            if not directory.exists():
                                directory.mkdir(exist_ok=False)
                                write_new(directory / 'RESERVATION.json', {'schema': 'C21M_CASE_QUEUE_V1', 'identity': identity,
                                          'case': case, 'state': 'QUEUED_NOT_STARTED', 'automatic_retry': False})
                            queues[cpu].put((case, str(directory), identity))
                            active[cpu] = case['case_id']
                            idle.remove(cpu)
                            event({'kind': 'DISPATCH', 'case_id': case['case_id'], 'cpu': cpu,
                                   'inflight_cases': len(active), 'inflight_bound': len(processes)})
                    if pending and not any(p.is_alive() for p in processes.values()):
                        failure = 'ALL_OWN_WORKERS_EXITED; never-started cases preserved'
                        break
    except BaseException:
        failure = traceback.format_exc()
        event({'kind': 'COORDINATOR_EXCEPTION', 'error': failure})
    finally:
        # Only process objects spawned by this coordinator are eligible for cleanup.
        for cpu, process in processes.items():
            if process.is_alive():
                try:
                    queues[cpu].put_nowait(None)
                except queue.Full:
                    pass
        grace = time.monotonic() + 2.
        for process in processes.values():
            process.join(max(0., grace - time.monotonic()))
        for process in processes.values():
            if process.is_alive():
                process.terminate()
        grace = time.monotonic() + 2.
        for process in processes.values():
            process.join(max(0., grace - time.monotonic()))
        for process in processes.values():
            if process.is_alive():
                process.kill()
                process.join(2.)
        os.sched_setaffinity(0, original_affinity)
        for _, handle in handles:
            handle.close()
        events.flush()
        os.fsync(events.fileno())
        events.close()
        try:
            summary = summarize(output, grid, identity, attempt, args.execution_site)
            write_new(output / f'RETURN_{attempt}.json', {'failure': failure,
                      'wall_seconds': time.monotonic() - started,
                      'own_worker_exit_codes': {str(c): p.exitcode for c, p in processes.items()},
                      'summary': summary, 'global_error_bound': None})
        finally:
            lock.close()
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'COMPLETE_SCOPED' else 2


def parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grid', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cpu-list')
    parser.add_argument('--lease-dir', default='/tmp/bass_cpu_leases')
    parser.add_argument('--timeout-seconds', type=float, default=3600.)
    parser.add_argument('--active-grace-seconds', type=float, default=300.)
    parser.add_argument('--execution-site', choices=('sandbox', 'ncp', 'other'), required=True)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--plan-only', action='store_true')
    return parser


if __name__ == '__main__':
    raise SystemExit(run(parser().parse_args()))
