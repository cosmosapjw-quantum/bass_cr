"""Eight create-only R4X static probes; prepare and execute are separate actions.

No qualification ladder, finite difference, propagation or capture is evaluated.
The coordinator owns the global raw-attempt budget; an attempt is durably reserved
before a worker is launched, and failed attempts are never retried automatically.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
import traceback

import operator_bootstrap
from operator_bootstrap import HERE, REPO, FND, HPC
import numpy as np
from runtime import load_bank, atomic_file, write_json
from resource_profile import census

GiB = 1024**3
ENV = {key: '1' for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
       'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OMP_NUM_THREADS')}
ENV.update(OMP_DYNAMIC='FALSE', OMP_MAX_ACTIVE_LEVELS='1')
INPUTS = {'BASIS.npz': '889001a751cd3cae93ad217336587f5fc58db11c0a496843ecc7e7bbd93f83ec',
          'BASIS.json': '3cf2359dd9802e84f9ec4dc45f3585e0aa9712de38a3fb0a077300d257150131',
          'SCIENCE_CONTEXT.json': 'cf484b252092d642c8c8487a8bf70deb61e7b0b9f2bc2f522a3325a146e7f746'}
RAW_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def sources():
    """Broad read-only source pinning, excluding tests and changing run records."""
    files = set(FND.rglob('*.py')) | set((REPO / 'cr_repro').rglob('*.py'))
    files |= set(HERE.glob('*.py')) | set(HERE.glob('*.f90')) | set(HPC.glob('*.py')) | set((HPC / 'native').glob('*.f90'))
    files.add(FND / 'tp2a_analytic_pruning_20260926/code/moment_kernel.cpp')
    return {str(p.resolve()): sha(p) for p in sorted(files) if not p.name.startswith('test_')}


def validate_pins(pins):
    for name, expected in pins.items():
        if sha(name) != expected:
            raise ValueError('pinned file changed: ' + name)


def check_environment():
    if any(os.environ.get(k) != v for k, v in ENV.items()):
        raise ValueError('strict one-thread environment required before Python/NumPy import')


def admit_resources(workers, info):
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError('workers must be 1..4')
    slots = workers + 1  # explicit coordinator CPU, even when mostly waiting
    if slots > min(info['usable_cpu_budget'], len(info['affinity_cpus'])):
        raise ValueError('workers plus coordinator exceed admitted CPU quota')
    available = min(info['memory_limit_bytes'], info['memory_available_bytes'])
    reserve = max(GiB, available // 8)
    estimated = workers * GiB + GiB // 2
    if estimated > available - reserve:
        raise ValueError('worker/coordinator RSS estimate exceeds memory after reserve')
    cpus = info['affinity_cpus'][:slots]
    return {'workers': workers, 'worker_cpu_ids': cpus[:workers], 'coordinator_cpu_id': cpus[-1],
            'threads_per_worker': 1, 'estimated_total_rss_bytes': estimated,
            'memory_reserve_bytes': reserve, 'memory_available_estimate_bytes': available,
            'rss_estimate_not_enforcement': True, 'MPI_execution': False,
            'NCP64_scaling': 'NOT_RUN', 'environment': ENV}


def candidate_bank(directory):
    from basis_representation import load_candidate
    return load_candidate(directory, backend='python'), read_json(Path(directory) / 'CANDIDATE.json')


def make_manifest(inputs, candidate, build, workers):
    check_environment()
    inputs, candidate, build = [Path(p).resolve() for p in (inputs, candidate, build)]
    if {n: sha(inputs / n) for n in INPUTS} != INPUTS:
        raise ValueError('original archived input bytes changed')
    bank, record = load_bank(inputs)
    new_bank, new_record = candidate_bank(candidate)
    if len(bank) != 5 or len(new_bank) != 5:
        raise ValueError('exact archived five-mode bank required')
    for old, new in zip(bank, new_bank):
        if (old.l, old.principal_n, old.energy) != (new.l, new.principal_n, new.energy):
            raise ValueError('candidate changed mode labels or stored eigenvalues')
        if not np.array_equal(old.edges, new.edges):
            raise ValueError('candidate changed radial mesh')
        new.payload_fingerprint()
    contract = read_json(HERE / 'TASK_CONTRACT.json')
    static = contract['static_probe_plan']
    fixed = {'z_a0': [-32.0, 0.0], 'b_a0': 2.0, 'energy_keV_per_u': 100.0,
             'orders': [32, 40], 'representations': ['original', 'candidate'],
             'same_center_order': 20, 'subdivisions': 1, 'phase_budget': None,
             'sector': 'full', 'cross_call_cap': 8, 'trajectory_or_capture_calls': 0}
    if any(static.get(k) != v for k, v in fixed.items()):
        raise ValueError('fixed bounded probe contract changed')
    original_science = read_json(inputs / 'SCIENCE_CONTEXT.json')['context']['contract']
    if any(original_science[k] != fixed[k] for k in ('b_a0', 'energy_keV_per_u')):
        raise ValueError('original trajectory contract mismatch')
    native = read_json(build / 'BUILD_HPC.json')
    expected_sources = {'reference': sha(FND / 'tp2a_analytic_pruning_20260926/code/moment_kernel.cpp'),
                        'fortran': sha(HPC / 'native/moment_kernel_real.f90')}
    if native['source_hashes'] != expected_sources or set(native['libraries']) != {'libreference.so', 'libmoments_f90.so'}:
        raise ValueError('native source/library identity mismatch')
    for filename, expected in native['libraries'].items():
        if sha(build / filename) != expected:
            raise ValueError('native binary changed')
    from cr_repro.observables import projectile_speed_au
    speed = projectile_speed_au(100.0)
    tasks = []
    for rep in fixed['representations']:
        for z in fixed['z_a0']:
            for order in fixed['orders']:
                task = {'index': len(tasks), 'representation': rep, 'z_a0': z,
                        'time_hex': float(z / speed).hex(), 'order': order}
                tasks.append({**task, 'task_id': digest(task)})
    if len(tasks) != 8 or len({x['task_id'] for x in tasks}) != 8:
        raise ValueError('exact eight distinct tasks required')
    files = {str(inputs / n): h for n, h in INPUTS.items()}
    for p in (candidate / 'CANDIDATE.npz', candidate / 'CANDIDATE.json',
              build / 'BUILD_HPC.json', build / 'libreference.so', build / 'libmoments_f90.so',
              HERE / 'TASK_CONTRACT.json'):
        files[str(p)] = sha(p)
    info = census()
    core = {'schema': 'BASS_R4X_STATIC_COMPARISON_MANIFEST_V1', 'inputs': str(inputs),
            'candidate': str(candidate), 'build': str(build), 'input_pins': files,
            'source_pins': sources(), 'original_basis_identity': record['identity'],
            'candidate_basis_identity': new_record['identity'],
            'kernel_backend': 'BASS_HPC_CXX_STRICT_REFERENCE_V1', 'kernel_threads': 1,
            'candidate_evaluator': 'PYTHON_FP64_SHARED_ENDPOINT_BUBBLE',
            'speed_a0_per_ta': speed, 'static_probe_plan': fixed, 'tasks': tasks,
            'diagnostic_acceptance': contract['diagnostic_acceptance'],
            'resources': admit_resources(workers, info), 'initial_census': info,
            'raw_attempt_budget': 8, 'automatic_retries': 0, 'timeout_seconds_per_attempt': 900,
            'old_context_reuse': False, 'qualification': False, 'G02': 'UNRESOLVED',
            'production_admission': 'HOLD', 'capture_execution_allowed': False,
            'all_bound': 'OPEN', 'b_grid': 'NO_GO'}
    return {**core, 'manifest_id': digest(core)}


def prepare(args):
    manifest = make_manifest(args.inputs, args.candidate, args.build, args.workers)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / 'MANIFEST.json', manifest)
    return {'status': 'PREPARED_NO_PHYSICAL_CALLS', 'manifest': str(out / 'MANIFEST.json'),
            'manifest_sha256': sha(out / 'MANIFEST.json'), 'manifest_id': manifest['manifest_id']}


def load_manifest(out, expected_sha):
    out = Path(out).resolve()
    if sha(out / 'MANIFEST.json') != expected_sha:
        raise ValueError('manifest byte hash mismatch')
    m = read_json(out / 'MANIFEST.json')
    if m.get('schema') != 'BASS_R4X_STATIC_COMPARISON_MANIFEST_V1' or digest({k: v for k, v in m.items() if k != 'manifest_id'}) != m['manifest_id']:
        raise ValueError('manifest content identity mismatch')
    if m['raw_attempt_budget'] != 8 or len(m['tasks']) != 8:
        raise ValueError('exact bounded attempt budget required')
    validate_pins(m['input_pins'])
    validate_pins(m['source_pins'])
    check_environment()
    return out, m


def _npz(path, arrays):
    atomic_file(path, lambda f: np.savez_compressed(f, **arrays))


def run_worker(out, expected_sha, index, cpu):
    out, manifest = load_manifest(out, expected_sha)
    if type(index) is not int or not 0 <= index < 8:
        raise ValueError('worker index must be 0..7')
    task = manifest['tasks'][index]
    reservation = read_json(out / 'reservations' / f'{index:03}.json')
    if reservation != {'manifest_id': manifest['manifest_id'], 'global_attempt': index + 1,
                       'task': task, 'worker_cpu_id': cpu, 'raw_attempt_budget': 8}:
        raise ValueError('durable reservation identity mismatch')
    if cpu not in manifest['resources']['worker_cpu_ids'] or cpu not in os.sched_getaffinity(0):
        raise ValueError('worker CPU was not admitted')
    os.sched_setaffinity(0, {cpu})
    if os.sched_getaffinity(0) != {cpu}:
        raise ValueError('worker binding failed')
    dest = out / 'attempts' / f'{index:03}'
    dest.mkdir(parents=True, exist_ok=False)
    write_json(dest / 'STARTED.json', {'task': task, 'manifest_id': manifest['manifest_id'],
               'pid': os.getpid(), 'affinity': sorted(os.sched_getaffinity(0)),
               'raw_attempt_reserved_before_start': True})
    started = time.monotonic()
    try:
        from kernel import HPCMomentKernel
        from bass_foundations.two_center import Trajectory, symmetric_channels
        if task['representation'] == 'original':
            bank, rec = load_bank(manifest['inputs'])
            import exact_cross as cross_module
            import full_operator as full_module
        elif task['representation'] == 'candidate':
            bank, rec = candidate_bank(manifest['candidate'])
            import continuous_exact_cross as cross_module
            import continuous_full_operator as full_module
        else:
            raise ValueError('unknown representation')
        expected_identity = manifest[task['representation'] + '_basis_identity']
        if rec['identity'] != expected_identity:
            raise ValueError('loaded bank identity mismatch')
        channels = symmetric_channels(bank)
        if len(channels) != 18:
            raise ValueError('exact full18 basis required')
        tr = Trajectory(((0., 0., 0.), (2., 0., 0.)),
                        ((0., 0., 0.), (0., 0., manifest['speed_a0_per_ta'])))
        kernel = HPCMomentKernel(manifest['build'], backend='reference', threads=1)
        t = float.fromhex(task['time_hex'])
        raw = cross_module.cross(tr, channels, t, kernel=kernel, order=task['order'],
                                 subdivisions=1, phase_budget=None, batch=1024, sector='full')
        raw['metadata'].update(backend=kernel.backend_identity, kernel_build=kernel.receipt,
                               r4x_manifest_id=manifest['manifest_id'], representation=task['representation'],
                               archived_context_compatible=False, evaluator=manifest['candidate_evaluator']
                               if task['representation'] == 'candidate' else 'ORIGINAL_FEMRADIAL_FP64')
        _npz(dest / 'RAW.npz', {k: raw[k] for k in RAW_KEYS})
        write_json(dest / 'RAW.json', {'metadata': raw['metadata'], 'sha256': sha(dest / 'RAW.npz')})
        cross = full_module._bind_cross(tr, channels, t, raw, raw['metadata'])
        full = full_module.assemble_full(tr, channels, t, same_order=20, cross=cross)
        arrays = {name: full[name] for name in ('S', 'H', 'D')}
        for center in ('T', 'P'):
            block = full['same_center'][center]
            for name in ('S', 'H', 'D', 'H0', 'V_other', 'A', 'indices'):
                arrays[center + '__' + name] = block[name]
        _npz(dest / 'FULL.npz', arrays)
        receipt = {'status': 'COMPLETED_STATIC_DIAGNOSTIC', 'task': task,
                   'manifest_id': manifest['manifest_id'], 'basis_identity': rec['identity'],
                   'raw_sha256': sha(dest / 'RAW.npz'), 'full_sha256': sha(dest / 'FULL.npz'),
                   'metadata': full['metadata'], 'diagnostics': full['diagnostics'],
                   'wall_seconds': time.monotonic() - started,
                   'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'pid': os.getpid(), 'affinity': sorted(os.sched_getaffinity(0)),
                   'production_admission': 'HOLD', 'capture_execution_allowed': False}
        write_json(dest / 'COMPLETED.json', receipt)
        return receipt
    except BaseException as exc:
        write_json(dest / 'FAILED.json', {'task': task, 'manifest_id': manifest['manifest_id'],
                   'exception': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc(),
                   'wall_seconds': time.monotonic() - started, 'no_retry': True})
        raise


def metric_difference(a, b):
    delta = b - a
    return {'maximum_entry_absolute': float(np.max(np.abs(delta))),
            'frobenius_absolute': float(np.linalg.norm(delta)),
            'spectral_absolute': float(np.linalg.norm(delta, 2)),
            'reference_frobenius': float(np.linalg.norm(a)),
            'relative_frobenius': float(np.linalg.norm(delta) / max(np.linalg.norm(a), 1e-300))}


def summarize(out, manifest):
    rows, payloads = [], {}
    for task in manifest['tasks']:
        dest = out / 'attempts' / f"{task['index']:03}"
        rec = read_json(dest / 'COMPLETED.json')
        if rec['task'] != task or rec['manifest_id'] != manifest['manifest_id']:
            raise ValueError('completion identity mismatch')
        if sha(dest / 'RAW.npz') != rec['raw_sha256'] or sha(dest / 'FULL.npz') != rec['full_sha256']:
            raise ValueError('completion payload changed')
        with np.load(dest / 'FULL.npz', allow_pickle=False) as data:
            full = {k: data[k].copy() for k in data.files}
        with np.load(dest / 'RAW.npz', allow_pickle=False) as data:
            raw = {k: data[k].copy() for k in RAW_KEYS}
        for k in ('S', 'H', 'D'):
            if full[k].shape != (18, 18) or not np.isfinite(full[k]).all():
                raise ValueError('invalid full matrix')
            if not np.array_equal(full[k][:9, 9:], raw[k + '_tp']) or not np.array_equal(full[k][9:, :9], raw[k + '_pt']):
                raise ValueError('full/raw assembly changed')
        key = (task['representation'], task['z_a0'], task['order'])
        payloads[key] = {'full': full, 'raw': raw}
        skew = {center: float(np.max(abs(full[center + '__D'] + full[center + '__D'].conj().T))) for center in ('T', 'P')}
        rows.append({'task': task, 'diagnostics': rec['diagnostics'], 'same_center_Dsum_maximum_entry': skew,
                     'same_center_Dsum_screen_pass': max(skew.values()) <= manifest['diagnostic_acceptance']['same_center_D_plus_Ddagger_entry_max'],
                     'metric_ratio_screen_pass': rec['diagnostics']['metric_ratio'] >= manifest['diagnostic_acceptance']['full_metric_min_ratio'],
                     'wall_seconds': rec['wall_seconds'], 'peak_rss_kib': rec['peak_rss_kib'],
                     'raw_sha256': rec['raw_sha256'], 'full_sha256': rec['full_sha256']})
    comparisons, resolutions = [], []
    atol, rtol = manifest['diagnostic_acceptance']['paired_operator_entry_difference_absolute_max_OR_relative_frobenius_max']
    for z in (-32.0, 0.0):
        for order in (32, 40):
            a, b = [payloads[(rep, z, order)] for rep in ('original', 'candidate')]
            for block, names in (('full', ('S', 'H', 'D')), ('raw', RAW_KEYS)):
                for name in names:
                    d = metric_difference(a[block][name], b[block][name])
                    comparisons.append({'z_a0': z, 'order': order, 'block': block, 'operator': name, **d,
                                        'local_screen_pass': d['maximum_entry_absolute'] <= atol or d['relative_frobenius'] <= rtol})
        for rep in ('original', 'candidate'):
            a, b = [payloads[(rep, z, order)] for order in (32, 40)]
            for block, names in (('full', ('S', 'H', 'D')), ('raw', RAW_KEYS)):
                for name in names:
                    resolutions.append({'z_a0': z, 'representation': rep, 'block': block, 'operator': name,
                                        **metric_difference(a[block][name], b[block][name]),
                                        'interpretation': 'ORDER_32_TO_40_OBSERVATION_NOT_CERTIFIED_QUADRATURE_ERROR'})
    return {'schema': 'BASS_R4X_STATIC_COMPARISON_SUMMARY_V1', 'manifest_id': manifest['manifest_id'],
            'status': 'COMPLETED_STATIC_DIAGNOSTIC', 'actual_cross_calls': 8,
            'actual_propagation_calls': 0, 'rows': rows, 'paired_representation_differences': comparisons,
            'within_representation_resolution_differences': resolutions,
            'local_paired_operator_screens_pass': all(x['local_screen_pass'] for x in comparisons),
            'local_same_center_screens_pass': all(x['same_center_Dsum_screen_pass'] for x in rows),
            'local_metric_screens_pass': all(x['metric_ratio_screen_pass'] for x in rows),
            'G02': 'UNRESOLVED', 'production_admission': 'HOLD', 'capture_execution_allowed': False,
            'all_bound': 'OPEN', 'b_grid': 'NO_GO'}


def execute(out, expected_sha):
    out, m = load_manifest(out, expected_sha)
    actual = census()
    fresh = admit_resources(m['resources']['workers'], actual)
    if fresh['worker_cpu_ids'] != m['resources']['worker_cpu_ids'] or fresh['coordinator_cpu_id'] != m['resources']['coordinator_cpu_id']:
        raise ValueError('fresh CPU allocation changed')
    write_json(out / 'STARTED.json', {'manifest_id': m['manifest_id'], 'fresh_census': actual,
               'resource_admission': fresh, 'pid': os.getpid(), 'no_prior_approval_reuse': True})
    original_affinity = os.sched_getaffinity(0)
    running, completed, next_index, reserved_attempts = {}, [], 0, 0
    started = time.monotonic()
    try:
        os.sched_setaffinity(0, {m['resources']['coordinator_cpu_id']})
        if os.sched_getaffinity(0) != {m['resources']['coordinator_cpu_id']}:
            raise ValueError('coordinator CPU binding failed')
        slots = list(m['resources']['worker_cpu_ids'])
        while next_index < len(m['tasks']) or running:
            for cpu in slots:
                if cpu in running or next_index >= len(m['tasks']):
                    continue
                index = next_index
                task = m['tasks'][index]
                validate_pins(m['source_pins'])
                validate_pins(m['input_pins'])
                reservation = {'manifest_id': m['manifest_id'], 'global_attempt': index + 1,
                               'task': task, 'worker_cpu_id': cpu, 'raw_attempt_budget': 8}
                write_json(out / 'reservations' / f'{index:03}.json', reservation)
                reserved_attempts += 1
                logpath = out / 'logs' / f'{index:03}.log'
                logpath.parent.mkdir(exist_ok=True)
                log = logpath.open('xb')
                command = [sys.executable, str(Path(__file__).resolve()), 'worker', '--out', str(out),
                           '--manifest-sha256', expected_sha, '--index', str(index), '--cpu', str(cpu)]
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, **ENV}, start_new_session=True,
                                        preexec_fn=lambda cpu=cpu: os.sched_setaffinity(0, {cpu}))
                running[cpu] = (proc, log, index, time.monotonic())
                next_index += 1
            for cpu, (proc, log, index, tick) in list(running.items()):
                code = proc.poll()
                if code is None:
                    if time.monotonic() - tick > m['timeout_seconds_per_attempt']:
                        raise TimeoutError(f'raw attempt {index} exceeded frozen timeout')
                    continue
                log.close()
                del running[cpu]
                if code != 0:
                    raise RuntimeError(f'raw attempt {index} failed, exit {code}; no retry')
                completed.append(index)
                print(json.dumps({'event': 'attempt_completed', 'index': index, 'completed_count': len(completed)}), flush=True)
            if running:
                time.sleep(0.1)
        summary = summarize(out, m)
        summary['batch_wall_seconds'] = time.monotonic() - started
        summary['wall_times_overlap_do_not_sum'] = True
        write_json(out / 'SUMMARY.json', summary)
        write_json(out / 'COMPLETED.json', {'manifest_id': m['manifest_id'], 'summary_sha256': sha(out / 'SUMMARY.json'),
                   'actual_cross_calls': len(completed), 'worker_processes_remaining': 0})
        return {'status': summary['status'], 'summary': str(out / 'SUMMARY.json'),
                'actual_cross_calls': len(completed), 'manifest_id': m['manifest_id']}
    except BaseException as exc:
        for proc, log, index, tick in running.values():
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
        deadline = time.monotonic() + 2
        for proc, log, index, tick in running.values():
            try:
                proc.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
            log.close()
        write_json(out / 'FAILED.json', {'manifest_id': m['manifest_id'], 'exception': type(exc).__name__,
                   'message': str(exc), 'reserved_attempts': reserved_attempts, 'completed_indices': completed,
                   'no_retry': True, 'worker_processes_remaining': 0})
        raise
    finally:
        os.sched_setaffinity(0, original_affinity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    for key in ('inputs', 'candidate', 'build', 'out'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--workers', type=int, default=4)
    for name in ('run', 'worker'):
        p = sub.add_parser(name)
        p.add_argument('--out', required=True)
        p.add_argument('--manifest-sha256', required=True)
        if name == 'worker':
            p.add_argument('--index', type=int, required=True)
            p.add_argument('--cpu', type=int, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args)
    elif args.command == 'run':
        result = execute(args.out, args.manifest_sha256)
    else:
        result = run_worker(args.out, args.manifest_sha256, args.index, args.cpu)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
