#!/usr/bin/env python3
"""F1-R2 exact parallel precompute; execution requires a new, bound authorization."""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
import hashlib
from importlib import metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[4]
SIDE = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class R2NotAuthorized(ValueError):
    pass


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def _event(root, phase, started, **details):
    row = {'phase': phase, 'elapsed_seconds': time.monotonic() - started, **details}
    with (Path(root) / 'PROGRESS.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def check_authorization(path, head, tree):
    if path is None or not Path(path).is_file():
        raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: external authorization missing')
    try:
        auth = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: invalid authorization') from exc
    if (auth.get('schema') != 'BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1'
            or auth.get('implementation_commit') != head
            or auth.get('implementation_tree') != tree
            or auth.get('native_admission_allowed') is not True):
        raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: schema/implementation/native permission mismatch')
    wall = auth.get('max_wall_seconds')
    cost = auth.get('spending_limit_krw')
    if type(wall) is not int or wall <= 0:
        raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: positive wall budget required')
    if cost is None:
        if auth.get('prepaid_host_approved') is not True:
            raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: cost or prepaid approval required')
    elif type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
        raise R2NotAuthorized('R2_EXECUTION_NOT_AUTHORIZED: finite nonnegative cost required')
    return auth


def _identity():
    head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
    tree = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD^{tree}'], text=True).strip()
    return head, tree


def verify_source_manifest():
    manifest = json.loads((SIDE / 'SOURCE_MANIFEST.json').read_text())
    for relative, item in manifest['files'].items():
        payload = (REPO / relative).read_bytes()
        if len(payload) != item['bytes'] or hashlib.sha256(payload).hexdigest() != item['sha256']:
            raise ValueError('R2_SOURCE_MANIFEST_BLOCKED: ' + relative)
    return manifest


def verify_numeric_environment(requirements_path):
    pins = {}
    for line in Path(requirements_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, separator, version = line.partition('==')
        if not separator or not name or not version or name in pins:
            raise ValueError('R2_ENVIRONMENT_BLOCKED: invalid exact pin file')
        pins[name] = version
    if set(pins) != {'numpy', 'scipy', 'pytest', 'mpmath'}:
        raise ValueError('R2_ENVIRONMENT_BLOCKED: pinned package set drift')
    found = {name: metadata.version(name) for name in pins}
    if found != pins or sys.version_info[:3] != (3, 12, 3):
        raise ValueError('R2_ENVIRONMENT_BLOCKED: Python or package version drift')
    return {'python': '.'.join(str(x) for x in sys.version_info[:3]), **found}


def verify_timeout_evidence():
    base = REPO / 'research/foundation_rebuild/ncloud_c64g3_20260928/execution_evidence/F1/20260928T064313Z'
    manifest = json.loads((base / 'EVIDENCE_MANIFEST.json').read_text())
    if (manifest['execution']['exit_code'] != 124 or manifest['execution']['wall_seconds'] != 7200
            or manifest['scientific_status'] is not None or 'RETURN_REPORT.json' not in manifest['missing_requested_files']):
        raise ValueError('R2_TIMEOUT_EVIDENCE_BLOCKED: historical timeout identity drift')
    for item in manifest['files']:
        path = REPO / item['published_path']
        if _sha(path) != item['published']['sha256'] or path.stat().st_size != item['published']['bytes']:
            raise ValueError('R2_TIMEOUT_EVIDENCE_BLOCKED: published file drift')
    lines = (base / 'PROGRESS.jsonl').read_text().splitlines()
    if not lines or json.loads(lines[-1])['phase'] != 'engine_loaded':
        raise ValueError('R2_TIMEOUT_EVIDENCE_BLOCKED: last phase drift')
    return manifest


def _pool_factory(workers, *, initializer, initargs):
    return ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn'),
                               initializer=initializer, initargs=initargs)


def execute_precompute(tasks, store, worker_fn, workers, *, deadline=None, progress=None,
                       executor_factory=None, initializer=None, initializer_args=()):
    """Parent persists each returned task before requesting more work."""
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.resources import memory_info
    task_list = list(tasks)
    pending = []
    restored = 0
    for spec in task_list:
        if store.has(spec):
            store.load(spec)
            restored += 1
        else:
            pending.append(spec)
    counts = {'planned': len(task_list), 'restored': restored, 'submitted': 0,
              'running': 0, 'completed': 0, 'persisted': restored, 'failed': 0,
              'workers': workers}
    started = time.monotonic()
    def emit(phase):
        try:
            available = memory_info()['MemAvailable']
        except (OSError, RuntimeError, ValueError, KeyError):
            available = None
        row = {**counts, 'phase': phase, 'elapsed_seconds': time.monotonic() - started,
               'parent_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'mem_available_bytes': available}
        _event(store.root, phase, started, **{k: v for k, v in row.items() if k not in ('phase', 'elapsed_seconds')})
        if progress:
            progress(row)
    status = 'R2_TASK_PRECOMPUTE_COMPLETE'
    first_failure = None
    executor = None
    futures = {}
    cursor = 0
    try:
        emit('precompute_started')
        if pending:
            if workers < 1:
                raise ValueError('R2_HOST_MISMATCH: no workers for pending tasks')
            factory = executor_factory or _pool_factory
            executor = factory(workers, initializer=initializer, initargs=initializer_args)
            def submit_window():
                nonlocal cursor
                while cursor < len(pending) and len(futures) < workers * 2:
                    if deadline is not None:
                        deadline()
                    if memory_info()['MemAvailable'] < 5_368_709_120:
                        raise RuntimeError('R2_MEMORY_BLOCKED: critical available memory')
                    spec = pending[cursor]
                    future = executor.submit(worker_fn, spec)
                    futures[future] = spec
                    cursor += 1
                    counts['submitted'] += 1
                    counts['running'] = len(futures)
            submit_window()
            while futures:
                remaining = deadline() if deadline is not None else 1.0
                done, _ = wait(futures, timeout=min(1.0, remaining), return_when=FIRST_COMPLETED)
                for future in done:
                    spec = futures.pop(future)
                    counts['running'] = len(futures)
                    result = future.result()
                    if result['task_id'] != spec['task_id']:
                        raise ValueError('R2_WORKER_IDENTITY_BLOCKED: returned task mismatch')
                    counts['completed'] += 1
                    store.save(spec, result['raw'], result['full'])
                    counts['persisted'] += 1
                    if counts['completed'] % 10 == 0:
                        emit('precompute_progress')
                submit_window()
        emit('precompute_completed')
    except (TimeoutError, KeyboardInterrupt) as exc:
        status = 'R2_INTERRUPTED'
        first_failure = type(exc).__name__ + ': ' + str(exc)
        counts['failed'] += 1
        try:
            emit('precompute_interrupted')
        except BaseException:
            pass
    except BaseException as exc:
        status = 'R2_OPERATOR_TASK_FAILED'
        first_failure = type(exc).__name__ + ': ' + str(exc)
        counts['failed'] += 1
        try:
            emit('precompute_failed')
        except BaseException:
            pass
    finally:
        if executor is not None:
            processes = tuple((getattr(executor, '_processes', None) or {}).values())
            executor.shutdown(wait=status == 'R2_TASK_PRECOMPUTE_COMPLETE', cancel_futures=True)
            if status != 'R2_TASK_PRECOMPUTE_COMPLETE':
                for process in processes:
                    if process.is_alive():
                        process.terminate()
        counts['running'] = 0
        summary = {'schema': 'BASS_NCLOUD_F1_R2_PARTIAL_TASK_SUMMARY_V1',
                   'status': status, **counts, 'first_failure': first_failure,
                   'elapsed_seconds': time.monotonic() - started}
        _write_new(store.root / 'PARTIAL_TASK_SUMMARY.json', summary)
        if status != 'R2_TASK_PRECOMPUTE_COMPLETE':
            _write_new(store.root / 'RETURN_REPORT.json',
                       {'schema': 'BASS_NCLOUD_F1_R2_RUN_RETURN_V1', 'status': status,
                        'scientific_admission_pass': False, 'first_failure': first_failure,
                        'task_summary': summary})
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorization', help='external NEW R2 authorization; never generated here')
    parser.add_argument('--out', required=True, help='create-only R2 run directory')
    parser.add_argument('--archive', help='exact historical TP2D archive')
    parser.add_argument('--resume-from', help='read-only exact-context prior R2 output')
    args = parser.parse_args(argv)
    out = Path(args.out)
    if out.exists():
        print('R2_OUTPUT_COLLISION: output already exists', file=sys.stderr)
        return 3
    try:
        head, tree = _identity()
        authorization = check_authorization(args.authorization, head, tree)
    except (R2NotAuthorized, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    return execute_authorized(args, out, head, tree, authorization)


def execute_authorized(args, out, head, tree, authorization):
    """Later separately authorized run; never called by this implementation session."""
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.archive_evidence import open_evidence
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.cloud_engine import build_engine, verify_engine_identity, verify_source_pins
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import EngineAdmissionError, run_admission
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.run_f1_engine_admission import verify_f0_durable
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.cache_evaluator import cached_evaluator
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.resources import enforce_thread_policy, host_receipt
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import plan_tasks
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_store import TaskStore
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.worker import evaluate_task, initialize_worker
    from cr_repro.observables import projectile_speed_au

    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    r2_contract = json.loads((SIDE / 'R2_CONTRACT.json').read_text())
    ceiling = r2_contract['inherited_claim_ceiling']
    report = {'schema': 'BASS_NCLOUD_F1_R2_RUN_RETURN_V1', 'status': 'R2_INPUT_IDENTITY_BLOCKED',
              'implementation_commit': head, 'implementation_tree': tree,
              'scientific_execution_performed': False, 'scientific_admission_pass': False,
              'first_failure': None, 'claim_ceiling': ceiling}
    def remaining():
        value = authorization['max_wall_seconds'] - (time.monotonic() - started)
        if value <= 0:
            raise TimeoutError('R2 wall budget exhausted')
        return value
    try:
        f1_side = REPO / 'research/foundation_rebuild/ncloud_f1_engine_admission_20260928'
        f1_path = f1_side / 'F1_CONTRACT.json'
        rep_path = f1_side / 'F1_REPRESENTATIVE_QUERIES.json'
        if (_sha(f1_path) != r2_contract['inherited_scientific_contract']['sha256']
                or _sha(rep_path) != r2_contract['inherited_representative_set']['sha256']):
            raise ValueError('R2_INPUT_IDENTITY_BLOCKED: inherited contract/query hash mismatch')
        verify_source_manifest()
        verify_f0_durable(REPO)
        verify_timeout_evidence()
        environment = verify_numeric_environment(REPO / 'research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/requirements-tested.txt')
        _write_new(out / 'ENVIRONMENT_RECEIPT.json', environment)
        f1_contract = json.loads(f1_path.read_text())
        reps = json.loads(rep_path.read_text())
        pins = json.loads((f1_side / 'SOURCE_PINS.json').read_text())
        verify_source_pins(REPO, pins)
        archive = Path(args.archive) if args.archive else REPO / f1_contract['historical_tp2d_archive']['path']
        evidence = open_evidence(archive, f1_contract, reps)
        tp2d = json.loads((REPO / 'research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/CONTRACT.json').read_text())
        speed = projectile_speed_au(tp2d['energy_keV_per_u'])
        _event(out, 'input_identity_verified', started)
        remaining()
        report['status'] = 'R2_TESTS_FAILED'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        test = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                               str(SIDE / 'runtime_r2/tests')], cwd=REPO, env=env,
                              text=True, capture_output=True, timeout=remaining(), check=False)
        (out / 'FOCUSED_TESTS.log').write_text(test.stdout + test.stderr)
        if test.returncode:
            raise RuntimeError('R2 focused tests failed')
        _event(out, 'focused_tests_passed', started)
        remaining()
        report['status'] = 'R2_BUILD_FAILED'
        source = REPO / f1_contract['build_policy']['source_path']
        engine_dir = out / 'engine'
        build = build_engine(source, engine_dir, f1_contract, timeout_seconds=remaining())
        identity = verify_engine_identity(engine_dir)
        for name in ('ENGINE_BUILD.json', 'ENGINE_IDENTITY.json'):
            shutil.copyfile(engine_dir / name, out / name)
        basis = evidence.materialize_basis(out / 'basis')
        _event(out, 'engine_loaded', started, library_sha256=build['library_sha256'])
        remaining()
        report['status'] = 'R2_TASK_PLAN_BLOCKED'
        context = {'engine_identity_sha256': identity['identity_sha256'],
                   'historical_archive_sha256': f1_contract['historical_tp2d_archive']['sha256'],
                   'contract_sha256': hashlib.sha256((r2_contract['schema'] + _sha(SIDE / 'R2_CONTRACT.json')
                       + _sha(f1_path) + _sha(rep_path)).encode()).hexdigest()}
        plan = plan_tasks(reps, f1_contract, speed, context['engine_identity_sha256'],
                          context['historical_archive_sha256'])
        if plan.representative_specs != 165 or plan.metric_specs != 165 or len(plan.tasks) > 330:
            raise ValueError('R2_TASK_PLAN_BLOCKED: frozen workload drift')
        store = TaskStore(out, context)
        imported = store.import_valid(args.resume_from, plan.tasks) if args.resume_from else 0
        remaining_tasks = len(plan.tasks) - imported
        enforce_thread_policy()
        report['status'] = 'R2_HOST_MISMATCH'
        host = host_receipt(remaining_tasks)
        _write_new(out / 'HOST_RESOURCE_RECEIPT.json', host)
        report['status'] = 'R2_INTERRUPTED'
        report['scientific_execution_performed'] = True
        _event(out, 'precompute_ready', started, planned=len(plan.tasks), imported=imported, **host)
        status = execute_precompute(plan.tasks, store, evaluate_task, host['workers'], deadline=remaining,
                                    initializer=initialize_worker,
                                    initializer_args=(REPO, engine_dir, basis, tp2d))
        if status != 'R2_TASK_PRECOMPUTE_COMPLETE':
            report['status'] = status
            report['first_failure'] = json.loads((out / 'PARTIAL_TASK_SUMMARY.json').read_text())['first_failure']
            return 3
        report['status'] = 'R2_CACHE_MISS_NO_FALLBACK'
        for spec in plan.tasks:
            store.load(spec)
        _event(out, 'cache_complete', started)
        parity, metric = run_admission(evidence, cached_evaluator(store, context), speed, f1_contract,
                                       identity['identity_sha256'], check_budget=remaining)
        _write_new(out / 'REPRESENTATIVE_PARITY.json', {'queries': parity,
                   'engine_identity_sha256': identity['identity_sha256']})
        _write_new(out / 'METRIC_CONNECTION_PARITY.json', {'sentinels': metric,
                   'engine_identity_sha256': identity['identity_sha256']})
        _write_new(out / 'ENGINE_ADMISSION.json', {'status': f1_contract['success_status'],
                   'representative_queries': len(parity), 'metric_sentinels': len(metric),
                   'engine_identity_sha256': identity['identity_sha256'], 'claim_ceiling': ceiling})
        report['status'] = f1_contract['success_status']
        report['scientific_admission_pass'] = True
        _event(out, 'admission_completed', started)
        return 0
    except EngineAdmissionError as exc:
        report['status'] = exc.status
        report['first_failure'] = str(exc)
    except (TimeoutError, KeyboardInterrupt, subprocess.TimeoutExpired) as exc:
        report['status'] = 'R2_INTERRUPTED'
        report['first_failure'] = type(exc).__name__ + ': ' + str(exc)
    except BaseException as exc:
        report['first_failure'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        report['elapsed_seconds'] = time.monotonic() - started
        if not (out / 'PARTIAL_TASK_SUMMARY.json').exists():
            _write_new(out / 'PARTIAL_TASK_SUMMARY.json',
                       {'status': report['status'], 'planned': 0, 'persisted': 0,
                        'first_failure': report['first_failure']})
        if not (out / 'RETURN_REPORT.json').exists():
            _write_new(out / 'RETURN_REPORT.json', report)
    _event(out, 'stopped', started, status=report['status'])
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
