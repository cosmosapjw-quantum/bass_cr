#!/usr/bin/env python3
"""Bounded, create-only C21G runner. No build, scheduler, watcher or git mutation.

plan validates pinned inputs without a native process. run uses one explicitly
allocated CPU and one foreground worker at a time. --reuse reads verified,
completed C21G jobs; no existing output directory is resumed in place.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True

from campaign_contract import (
    HERE, DEFAULT_SOURCE, RAW_NAME, POLICY, TIERS, NATIVE_KIND,
    read_json, write_new_json, sha256, file_record, canonical_hash,
    reference_controls, verify_inputs, verify_native_binary, verify_files,
)

def utc():
    return datetime.now(timezone.utc).isoformat()

def runtime_identity():
    versions = {'python': platform.python_version()}
    for name in ('numpy', 'scipy'):
        versions[name] = importlib.metadata.version(name)
    return versions

def snapshot(source, cpu):
    """Read-only inventory; the caller is responsible for CPU allocation."""
    allowed = sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    commands = {
        'processes': ['ps', '-eo', 'pid,ppid,pgid,psr,pcpu,rss,etime,comm', '--sort=-pcpu'],
        'git_status': ['git', '-C', str(source), 'status', '--porcelain=v1', '--untracked-files=normal'],
        'git_head': ['git', '-C', str(source), 'rev-parse', 'HEAD'],
        'memory': ['free', '-b'],
    }
    records = {}
    env = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}
    for name, command in commands.items():
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=10, env=env)
            records[name] = {'argv': command, 'exit_code': p.returncode,
                             'stdout': p.stdout, 'stderr': p.stderr}
        except (OSError, subprocess.TimeoutExpired) as error:
            records[name] = {'argv': command, 'status': 'UNAVAILABLE', 'error': str(error)}
    return {'time_utc': utc(), 'hostname': platform.node(), 'platform': platform.platform(),
            'allowed_cpu_ids': allowed, 'requested_allocated_cpu': cpu,
            'load_average': list(os.getloadavg()) if hasattr(os, 'getloadavg') else None,
            'read_only_inventory': records, 'runtime': runtime_identity(),
            'allocation_owner': 'Operator supplies a CPU after checking current campaigns; affinity membership alone is not an allocation certificate.',
            'mutations': 'Only this new output and this process affinity; no git checkout/reset, scheduler, watcher or existing checkpoint changes.'}

def stop_owned_group(process):
    """Signal only the process group created by this launcher's new session."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    # The leader may exit while a descendant ignores SIGTERM. Its exit alone
    # does not prove that our process group has finished.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()

def launch_process(argv, output, timeout_s, env=None):
    """Bound only our new process group, preserving stdout/stderr on failure."""
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    start = utc(); clock = time.monotonic(); timed_out = False
    with (output / 'stdout.log').open('x') as stdout, (output / 'stderr.log').open('x') as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            process.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            stop_owned_group(process)
        except BaseException:
            stop_owned_group(process)
            raise
    return {'argv': argv, 'started_at_utc': start, 'finished_at_utc': utc(),
            'wall_s': time.monotonic() - clock, 'exit_code': process.returncode,
            'timed_out': timed_out,
            'execution_status': 'TIMED_OUT' if timed_out else 'EXIT_0' if process.returncode == 0 else 'FAILED'}

def payload_files(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError('PAYLOAD_DIRECTORY_SYMLINK')
    directory = directory.resolve()
    records = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise ValueError('PAYLOAD_PATH_ESCAPE')
        if path.is_file():
            records[str(path.relative_to(directory))] = file_record(path)
    return records

def input_identity_hash(identity):
    # The source records are portable; the observed local manifest path is not.
    return canonical_hash({key: value for key, value in identity.items() if key != 'manifest_path'})

def verify_execution_closure(source, baseline, identity, native_identity=None):
    """Check the originally frozen records, including this executable file."""
    manifest = Path(identity.get('manifest_path', HERE / 'EXECUTION_MANIFEST.json'))
    if sha256(manifest) != identity['manifest_sha256']:
        raise ValueError('FROZEN_MANIFEST_MISMATCH')
    if identity['policy_sha256'] != canonical_hash(POLICY):
        raise ValueError('FROZEN_POLICY_MISMATCH')
    code = identity['c21g_runtime_files']
    if 'run_campaign.py' not in code or file_record(Path(__file__).resolve()) != code['run_campaign.py']:
        raise ValueError('RUNNER_NOT_PINNED_OR_CHANGED')
    verify_files(source, identity['c21f_runtime_files'])
    verify_files(baseline, identity['baseline_files'])
    verify_files(HERE, code)
    if native_identity is not None:
        expected = {key: native_identity[key] for key in ('bytes', 'sha256')}
        if file_record(native_identity['path']) != expected:
            raise ValueError('NATIVE_BINARY_CHANGED')
    return {'verified': True, 'input_identity_sha256': input_identity_hash(identity),
            'manifest_sha256': identity['manifest_sha256'],
            'runner_sha256': code['run_campaign.py']['sha256'],
            'native_binary_sha256': native_identity['sha256'] if native_identity else None,
            'verified_at_utc': utc()}

def expected_execution(f, job):
    common = {'kind': job['kind'], 'cohorts': len(f['q']),
              'x0': f['x0'], 'x1': f['x0'] + f['dx']}
    if job['kind'] == 'reference':
        if job['tier'] not in TIERS:
            raise ValueError('REFERENCE_TIER_OUTSIDE_POLICY')
        controls = reference_controls(f, job['tier'])
        return {**common, 'schema': 'C21F_OPTICAL_DEPTH_RADAU_REFERENCE_V1',
                'status': 'PASS_SCOPED_CONTINUOUS_IVP',
                **{key: controls[key] for key in ('rtol', 'atol', 'max_step_divisor', 'max_evaluations')}}
    if job['kind'] == 'history':
        if job['mode'] not in POLICY['new_native_modes'] or type(job['subdivisions']) is not int or job['subdivisions'] < 1:
            raise ValueError('HISTORY_CONTROLS_DOMAIN')
        return {**common, 'schema': 'C21E_FIXED_SOURCE_EVENT_NATIVE_TRANSACTION_V1',
                'status': 'PASS_SCOPED_FIXED_GRID_TRANSACTION',
                'mode': job['mode'], 'subdivisions': job['subdivisions']}
    raise ValueError('UNKNOWN_JOB_KIND')

def validate_signature_data(data, signature):
    if canonical_hash(data) != signature:
        raise ValueError('JOB_SIGNATURE_DATA_MISMATCH')
    if data['micro'] not in ('native', 'manufactured'):
        raise ValueError('MICROPHYSICS_MODE_DOMAIN')
    if canonical_hash(data['fixture']) != data['fixture_sha256']:
        raise ValueError('JOB_FIXTURE_DIGEST_MISMATCH')
    if expected_execution(data['fixture'], data['job']) != data['expected_execution']:
        raise ValueError('REQUESTED_EXECUTION_CONTRACT_MISMATCH')
    if data['micro'] == 'native':
        plan = job_plan()
        if data['job'] not in plan['references'] + plan['conditional_histories']:
            raise ValueError('NATIVE_JOB_OUTSIDE_BOUNDED_PLAN')
        if not isinstance(data.get('binary_sha256'), str) or len(data['binary_sha256']) != 64:
            raise ValueError('NATIVE_BINARY_IDENTITY_MISSING')

def validate_completed_payload(payload, signature, data):
    """Validate completion semantics; physical agreement is assessed later."""
    payload = Path(payload)
    validate_signature_data(data, signature)
    expected = data['expected_execution']; native = data['micro'] == 'native'
    required = {'result.json', 'worker_receipt.json'}
    if expected['kind'] == 'history':
        required.add('accepted_steps.jsonl')
    if native:
        required.update({'process/native_points.jsonl', 'process/native_process.json', 'process/native_stderr.log'})
    if not all((payload / name).is_file() for name in required):
        raise ValueError('COMPLETE_PAYLOAD_MISSING_REQUIRED_FILES')
    result = read_json(payload / 'result.json'); worker_record = read_json(payload / 'worker_receipt.json')
    kind = NATIVE_KIND if native else 'MANUFACTURED_CONSERVATIVE_MICRO_NOT_GRACKLE'
    if (worker_record.get('status') != 'COMPLETE' or worker_record.get('signature') != signature
            or worker_record.get('runtime') != data['runtime'] or worker_record.get('microphysics') != kind
            or worker_record.get('input_identity_sha256') != data['input_identity_sha256']):
        raise ValueError('WORKER_COMPLETION_IDENTITY_MISMATCH')
    for key in ('execution_closure_before', 'execution_closure_after'):
        check = worker_record.get(key, {})
        if check.get('verified') is not True or check.get('input_identity_sha256') != data['input_identity_sha256']:
            raise ValueError('WORKER_EXECUTION_CLOSURE_MISSING')
    if worker_record.get('native_process_exit_code') != (0 if native else None):
        raise ValueError('NATIVE_PROCESS_NOT_COMPLETED')
    if (result.get('schema') != expected['schema'] or result.get('status') != expected['status']
            or result.get('fixture_sha256') != data['fixture_sha256'] or result.get('microphysics') != kind):
        raise ValueError('RESULT_IDENTITY_OR_STATUS_MISMATCH')
    if len(result.get('gas', [])) != 4 or len(result.get('photons', [])) != expected['cohorts']:
        raise ValueError('RESULT_STATE_SHAPE_MISMATCH')
    if not all(math.isfinite(value) for value in result['gas'] + result['photons']):
        raise ValueError('RESULT_STATE_NONFINITE')
    if expected['kind'] == 'reference':
        controls = result.get('tolerance_contract', {})
        if any(controls.get(key) != expected[key] for key in ('rtol', 'atol', 'max_step_divisor')):
            raise ValueError('RESULT_REFERENCE_CONTROLS_MISMATCH')
        if not result.get('solver_diagnostics', {}).get('segments'):
            raise ValueError('REFERENCE_SOLVER_DIAGNOSTICS_MISSING')
        reported_calls = result.get('rhs_evaluations')
    else:
        if result.get('mode') != expected['mode'] or result.get('subdivisions_per_event_interval') != expected['subdivisions']:
            raise ValueError('RESULT_HISTORY_CONTROLS_MISMATCH')
        count = 0; endpoint = expected['x0']; calls = 0
        with (payload / 'accepted_steps.jsonl').open() as stream:
            for line in stream:
                row = json.loads(line)
                if row['x0'] != endpoint or row['x1'] <= row['x0']:
                    raise ValueError('HISTORY_STEP_COVERAGE_MISMATCH')
                endpoint = row['x1']; count += 1; calls += row['rhs_calls']
        if count == 0 or count != result.get('steps') or endpoint != expected['x1'] or calls != result.get('rhs_calls'):
            raise ValueError('HISTORY_STEP_COUNT_OR_CALLS_MISMATCH')
        reported_calls = result.get('rhs_calls')
    budget = (expected['max_evaluations'] if expected['kind'] == 'reference'
              else POLICY['max_native_calls_per_job'])
    if type(reported_calls) is not int or not 0 < reported_calls <= budget:
        raise ValueError('RESULT_EVALUATION_COUNT_DOMAIN')
    if native:
        process = read_json(payload / 'process/native_process.json')
        from campaign_contract import OWNER
        if (process.get('owner') != OWNER or process.get('binary_sha256') != data['binary_sha256']
                or process.get('timeout_s') != POLICY['native_call_timeout_s']
                or process.get('max_calls') != POLICY['max_native_calls_per_job']):
            raise ValueError('NATIVE_PROCESS_IDENTITY_MISMATCH')
        actual_calls = worker_record.get('provider_calls')
        with (payload / 'process/native_points.jsonl').open('rb') as stream:
            logged_calls = sum(1 for line in stream if line.strip())
        if type(actual_calls) is not int or actual_calls < 1 or actual_calls != reported_calls or logged_calls != actual_calls:
            raise ValueError('NATIVE_POINT_LOG_INCOMPLETE')
    return result

def _verify_payload_record(receipt, payload_directory=None):
    """Verify a receipt in place, or at an explicitly grounded restored path."""
    if receipt.get('status') != 'COMPLETE':
        raise ValueError('JOB_NOT_COMPLETE')
    data = receipt['signature_data']; signature = receipt['signature']
    if receipt.get('job') != data.get('job'):
        raise ValueError('RECEIPT_JOB_IDENTITY_MISMATCH')
    process = receipt.get('process', {})
    if process.get('exit_code') != 0 or process.get('timed_out') is not False or process.get('execution_status') != 'EXIT_0':
        raise ValueError('JOB_PROCESS_NOT_COMPLETED')
    payload = Path(payload_directory) if payload_directory is not None else Path(receipt['payload_directory'])
    if not payload.is_dir():
        raise ValueError('PAYLOAD_DIRECTORY_MISSING')
    expected_files = receipt.get('payload_files', {})
    for name in expected_files:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('PAYLOAD_MANIFEST_PATH_DOMAIN')
    if payload_files(payload) != expected_files:
        raise ValueError('PAYLOAD_MANIFEST_MISMATCH')
    return validate_completed_payload(payload, signature, data)

def verify_payload_record(receipt, payload_directory=None):
    """Return verified result or ValueError, including for malformed schemas."""
    try:
        return _verify_payload_record(receipt, payload_directory)
    except (OSError, KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError('INVALID_COMPLETION_RECORD ' + type(error).__name__) from error

def verify_reusable_job(receipt_path, wanted_signature):
    receipt_path = Path(receipt_path)
    r = read_json(receipt_path)
    if r.get('signature') != wanted_signature or r.get('status') != 'COMPLETE':
        return None
    verify_payload_record(r)
    return {**r, 'reuse_receipt': str(receipt_path), 'reused_without_execution': True}

def run_job(out, job, source, baseline, input_identity, native_identity, cpu, reuse=(), micro='native', fixture_override=None):
    out = Path(out)
    if Path(job['id']).name != job['id'] or job['id'] in ('', '.', '..'):
        raise ValueError('JOB_PATH_DOMAIN')
    directory = out / 'jobs' / job['id']
    directory.mkdir(parents=True, exist_ok=False)
    payload = directory / 'payload'; payload.mkdir()
    write_new_json(directory / 'JOB_START.json', {'job': job, 'started_at_utc': utc(),
                   'state': 'PREPARING', 'native_process_started': False})
    process = None; signature = None; signature_data = None
    before = None; after = None; interrupt = None
    receipt = {'schema': 'C21G_JOB_RECEIPT_V1', 'job': job, 'status': 'FAILED',
               'payload_directory': str(payload.resolve()),
               'payload_relative_to_campaign': str(payload.relative_to(out)),
               'reused_without_execution': False, 'native_science': micro == 'native',
               'raw_publication': 'PENDING_NEW_EXECUTION_DELIVERY',
               'raw_backup': 'PENDING_NEW_EXECUTION_DELIVERY'}
    try:
        before = verify_execution_closure(source, baseline, input_identity, native_identity)
        f = fixture_override if fixture_override is not None else read_json(Path(baseline) / job['fixture'] / 'fixture.json')
        signature_data = {'job': job, 'fixture': f, 'fixture_sha256': canonical_hash(f),
                          'input_manifest_sha256': input_identity['manifest_sha256'],
                          'input_identity_sha256': input_identity_hash(input_identity),
                          'runtime': runtime_identity(), 'micro': micro,
                          'binary_sha256': native_identity.get('sha256') if native_identity else None,
                          'expected_execution': expected_execution(f, job)}
        signature = canonical_hash(signature_data)
        validate_signature_data(signature_data, signature)
        if micro == 'native' and signature_data['fixture_sha256'] != input_identity['fixtures'][job['fixture']]['sha256']:
            raise ValueError('NATIVE_FIXTURE_OUTSIDE_FROZEN_BASELINE')
        spec = {'job': job, 'source_directory': str(Path(source).resolve()),
                'baseline_directory': str(Path(baseline).resolve()), 'fixture': f,
                'input_identity': input_identity, 'native_identity': native_identity,
                'payload_directory': str(payload.resolve()), 'micro': micro,
                'native_binary': native_identity['path'] if native_identity else None,
                'cpu': cpu, 'policy': POLICY, 'signature': signature,
                'signature_data': signature_data}
        write_new_json(directory / 'spec.json', spec)
        for previous in reuse:
            prior = Path(previous) / 'job_receipts' / (job['id'] + '.json')
            if prior.is_file():
                reused = verify_reusable_job(prior, signature)
                if reused is not None:
                    after = verify_execution_closure(source, baseline, input_identity, native_identity)
                    if runtime_identity() != signature_data['runtime']:
                        raise ValueError('RUNTIME_CHANGED_DURING_REUSE')
                    reused['reuse_execution_closure_before'] = before
                    reused['reuse_execution_closure_after'] = after
                    reused['payload_relative_to_campaign'] = None
                    write_new_json(out / 'job_receipts' / (job['id'] + '.json'), reused)
                    return reused
        env = {**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
               'PYTHONDONTWRITEBYTECODE': '1'}
        process = launch_process([sys.executable, str(HERE / 'run_campaign.py'), '_worker',
                                  '--spec', str(directory / 'spec.json')], directory,
                                 POLICY['wall_timeout_s_per_job'], env)
        after = verify_execution_closure(source, baseline, input_identity, native_identity)
        if runtime_identity() != signature_data['runtime']:
            raise ValueError('RUNTIME_CHANGED_DURING_JOB')
        receipt.update(signature=signature, signature_data=signature_data, process=process,
                       status='COMPLETE', payload_files=payload_files(payload))
        verify_payload_record(receipt)
    except BaseException as error:
        if before is not None and after is None:
            try:
                after = verify_execution_closure(source, baseline, input_identity, native_identity)
            except Exception as closure_error:
                after = {'verified': False, 'error': str(closure_error), 'time_utc': utc()}
        receipt['status'] = 'FAILED'
        receipt['failure'] = {'error_type': type(error).__name__, 'error': str(error),
                              'traceback': traceback.format_exc(), 'time_utc': utc()}
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            interrupt = error
    receipt.update(signature=signature, signature_data=signature_data, process=process,
                   execution_closure_before=before, execution_closure_after=after)
    try:
        final_files = payload_files(payload)
        if receipt['status'] == 'COMPLETE' and final_files != receipt['payload_files']:
            raise ValueError('PAYLOAD_CHANGED_DURING_ADMISSION')
        receipt['payload_files'] = final_files
    except (OSError, ValueError) as error:
        receipt['status'] = 'FAILED'; receipt['payload_integrity_error'] = str(error)
        receipt['payload_files'] = {}
    for name in ('stdout', 'stderr'):
        path = directory / (name + '.log')
        receipt[name] = file_record(path) if path.is_file() else None
    write_new_json(out / 'job_receipts' / (job['id'] + '.json'), receipt)
    if interrupt is not None:
        raise interrupt
    return receipt

def worker(spec_path):
    spec = read_json(spec_path); out = Path(spec['payload_directory'])
    provider = None
    try:
        data = spec['signature_data']
        validate_signature_data(data, spec['signature'])
        if (spec['job'] != data['job'] or spec['fixture'] != data['fixture'] or spec['micro'] != data['micro']
                or input_identity_hash(spec['input_identity']) != data['input_identity_sha256']
                or canonical_hash(spec['policy']) != canonical_hash(POLICY)):
            raise ValueError('WORKER_SPEC_IDENTITY_MISMATCH')
        native = spec['native_identity']
        if spec['micro'] == 'native':
            if native is None or spec['native_binary'] != native['path'] or native['sha256'] != data['binary_sha256']:
                raise ValueError('WORKER_NATIVE_SPEC_MISMATCH')
            if data['fixture_sha256'] != spec['input_identity']['fixtures'][spec['job']['fixture']]['sha256']:
                raise ValueError('WORKER_NATIVE_FIXTURE_MISMATCH')
            if type(spec['cpu']) is not int or spec['cpu'] in POLICY['protected_cpu_ids']:
                raise ValueError('WORKER_CPU_ALLOCATION_REQUIRED')
        before = verify_execution_closure(spec['source_directory'], spec['baseline_directory'], spec['input_identity'], native)
        if runtime_identity() != data['runtime']:
            raise ValueError('WORKER_RUNTIME_MISMATCH')
        if spec['cpu'] is not None:
            os.sched_setaffinity(0, {spec['cpu']})
        sys.path.insert(0, str(Path(spec['source_directory']) / 'src'))
        from run_experiment import Fixture, run_history
        from event_coupler import ManufacturedMicro
        from native_micro import NativeMicro
        from reference_tau import run_reference_tau
        fixture = Fixture(**spec['fixture']).validate()
        p = spec['policy']
        for key in ('max_native_calls_per_job', 'max_reference_rhs_evaluations'):
            if type(p[key]) is not int or p[key] < 1:
                raise ValueError('INTEGER_EVALUATION_BUDGET_REQUIRED')
        provider = NativeMicro([spec['native_binary']], out / 'process', p['native_call_timeout_s'],
                               p['max_native_calls_per_job']) if spec['micro'] == 'native' else ManufacturedMicro()
        job = spec['job']
        if job['kind'] == 'reference':
            controls = reference_controls(spec['fixture'], job['tier'])
            kwargs = {k: v for k, v in controls.items() if k != 'scale_contract'}
            result = run_reference_tau(fixture, provider, **kwargs)
            result['c21g_scale_contract'] = controls['scale_contract']
            write_new_json(out / 'result.json', result)
        elif job['kind'] == 'history':
            result = run_history(fixture, job['subdivisions'], provider, job['mode'], out)
        else:
            raise ValueError('UNKNOWN_JOB_KIND')
        native_exit = None
        if isinstance(provider, NativeMicro):
            provider.close()
            native_exit = provider.process.returncode
            if native_exit != 0:
                raise RuntimeError('NATIVE_PROCESS_EXIT_' + str(native_exit))
        after = verify_execution_closure(spec['source_directory'], spec['baseline_directory'], spec['input_identity'], native)
        if runtime_identity() != data['runtime']:
            raise ValueError('WORKER_RUNTIME_CHANGED')
        write_new_json(out / 'worker_receipt.json', {'status': 'COMPLETE', 'signature': spec['signature'],
                       'finished_at_utc': utc(), 'runtime': runtime_identity(),
                       'microphysics': provider.kind, 'native_process_exit_code': native_exit,
                       'input_identity_sha256': data['input_identity_sha256'],
                       'execution_closure_before': before, 'execution_closure_after': after,
                       'provider_calls': getattr(provider, 'calls', None),
                       'scope': 'C21G_NATIVE_FIXED_FIXTURE_PILOT' if spec['micro'] == 'native' else 'MANUFACTURED_WIRING_SMOKE_NOT_NATIVE'})
    except BaseException as error:
        write_new_json(out / 'FAILURE.json', {'status': 'FAILED', 'error_type': type(error).__name__,
                       'error': str(error), 'traceback': traceback.format_exc(), 'time_utc': utc(),
                       'native_claim': 'NOT_ADMITTED'})
        raise
    finally:
        if provider is not None and hasattr(provider, 'close'):
            provider.close()

def job_plan():
    refs = [{'id': name + '_reference_' + tier['name'], 'fixture': name,
             'kind': 'reference', 'tier': dict(tier)}
            for name in POLICY['fixtures'] for tier in TIERS]
    histories = [{'id': 'native_source_' + mode + '_' + str(n), 'fixture': 'native_source',
                  'kind': 'history', 'mode': mode, 'subdivisions': n}
                 for n in POLICY['new_native_subdivisions'] for mode in POLICY['new_native_modes']]
    return {'references': refs, 'conditional_histories': histories,
            'old_runs_repeated': [], 'maximum_new_jobs': len(refs) + len(histories)}

def paths(args):
    source = args.source_dir.resolve()
    baseline = args.baseline_dir.resolve() if args.baseline_dir else source / 'evidence' / RAW_NAME
    return source, baseline

def can_refine(reference_assessment):
    """All reference execution must finish; common-IC budget is independent."""
    return (reference_assessment.get('execution_status') == 'COMPLETE'
            and reference_assessment.get('fixtures', {}).get('native_source', {}).get('pilot_status')
            == 'REF_READY_FOR_BOUNDED_REFINEMENT')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('plan', 'run', 'smoke'):
        p = sub.add_parser(name)
        p.add_argument('--out', type=Path, required=True)
        p.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE)
        p.add_argument('--baseline-dir', type=Path)
        if name == 'run':
            p.add_argument('--native', type=Path, required=True)
            p.add_argument('--build-dir', type=Path)
            p.add_argument('--cpu', type=int, required=True)
            p.add_argument('--references-only', action='store_true')
            p.add_argument('--reuse', type=Path, action='append', default=[])
    p = sub.add_parser('_worker'); p.add_argument('--spec', type=Path, required=True)
    args = parser.parse_args()
    if args.command == '_worker':
        worker(args.spec); return
    source, baseline = paths(args)
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    try:
        inputs = verify_inputs(source, baseline)
        write_new_json(out / 'INPUT_IDENTITY.json', inputs)
        write_new_json(out / 'PLAN.json', {'policy': POLICY, **job_plan(),
                       'source_directory': str(source), 'baseline_directory': str(baseline),
                       'created_at_utc': utc(), 'native_status': 'NOT_RUN'})
        if args.command == 'plan':
            print(json.dumps({'status': 'PLAN_READY', 'maximum_new_jobs': 12, 'output': str(out)})); return
        if args.command == 'smoke':
            sys.path.insert(0, str(source / 'src'))
            from dataclasses import asdict
            from run_experiment import make_fixture
            fixture = asdict(make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003, Y=0.))
            jobs = [{'id': 'smoke_reference_L1', 'fixture': 'manufactured_smoke', 'kind': 'reference', 'tier': dict(TIERS[0])},
                    {'id': 'smoke_FULLMID_4', 'fixture': 'manufactured_smoke', 'kind': 'history', 'mode': 'FULLMID', 'subdivisions': 4},
                    {'id': 'smoke_MIDPHOTO_ENDMICRO_4', 'fixture': 'manufactured_smoke', 'kind': 'history', 'mode': 'MIDPHOTO_ENDMICRO', 'subdivisions': 4}]
            receipts = [run_job(out, j, source, baseline, inputs, None, None,
                                micro='manufactured', fixture_override=fixture) for j in jobs]
            complete = all(r['status'] == 'COMPLETE' for r in receipts)
            write_new_json(out / 'SMOKE_RESULT.json', {'status': 'PASS_WIRING_SMOKE' if complete else 'FAILED',
                           'native_science': False, 'fixture': fixture, 'jobs': receipts})
            if not complete:
                raise RuntimeError('MANUFACTURED_WIRING_SMOKE_FAILED')
            print(json.dumps({'status': 'PASS_WIRING_SMOKE', 'jobs': 3, 'native_science': False})); return
        inventory = snapshot(source, args.cpu)
        write_new_json(out / 'LIVE_INVENTORY.json', inventory)
        if inventory['allowed_cpu_ids'] is None or args.cpu not in inventory['allowed_cpu_ids']:
            raise ValueError('CPU_OUTSIDE_ALLOWED_AFFINITY')
        if args.cpu in POLICY['protected_cpu_ids']:
            raise ValueError('PROTECTED_CAMPAIGN_CPU')
        native = verify_native_binary(args.native, source, args.build_dir)
        write_new_json(out / 'NATIVE_IDENTITY.json', native)
        os.sched_setaffinity(0, {args.cpu})
        receipts = []
        for job in job_plan()['references']:
            r = run_job(out, job, source, baseline, inputs, native, args.cpu, args.reuse)
            receipts.append(r)
            print(json.dumps({'job': job['id'], 'status': r['status'], 'reused': r['reused_without_execution']}), flush=True)
        from analyze_campaign import analyze_references, analyze_refinement
        references = analyze_references(baseline, receipts)
        write_new_json(out / 'REFERENCE_ASSESSMENT.json', references)
        ready = (can_refine(references) and len(receipts) == len(job_plan()['references'])
                 and all(receipt['status'] == 'COMPLETE' for receipt in receipts))
        if ready and not args.references_only:
            for job in job_plan()['conditional_histories']:
                r = run_job(out, job, source, baseline, inputs, native, args.cpu, args.reuse)
                receipts.append(r)
                print(json.dumps({'job': job['id'], 'status': r['status'], 'reused': r['reused_without_execution']}), flush=True)
        refinement = analyze_refinement(baseline, receipts, references)
        write_new_json(out / 'REFINEMENT_ASSESSMENT.json', refinement)
        status = 'COMPLETED_BOUNDED_PILOT' if ready and refinement['execution_status'] == 'COMPLETE' else 'REFERENCES_ONLY' if args.references_only and ready else 'PARTIAL_OR_REFERENCE_HOLD'
        write_new_json(out / 'RETURN_TO_CHATGPT.json', {'schema': 'C21G_EXECUTION_RETURN_V1', 'status': status,
                       'created_at_utc': utc(), 'input_identity': inputs, 'native_identity': native,
                       'reference_status': {k: v['pilot_status'] for k, v in references['fixtures'].items()},
                       'refinement_execution': refinement['execution_status'], 'jobs': receipts,
                       'science': 'Scoped fixed-fixture diagnostics; interpret signed component errors, ledger closure and reference sensitivity separately.',
                       'global_error_bound': None, 'holds': POLICY['holds'],
                       'publication': 'PENDING_NEW_EXECUTION_DELIVERY', 'backup': 'PENDING_NEW_EXECUTION_DELIVERY',
                       'all_new_files': payload_files(out)})
        print(json.dumps({'status': status, 'output': str(out), 'reference_ready': ready}))
        if any(r['status'] != 'COMPLETE' for r in receipts):
            raise RuntimeError('ONE_OR_MORE_JOBS_FAILED_SEE_RETURN_RECEIPT')
    except BaseException as error:
        failure = out / 'FAILURE.json'
        if not failure.exists():
            write_new_json(failure, {'status': 'FAILED', 'type': type(error).__name__, 'error': str(error),
                           'traceback': traceback.format_exc(), 'time_utc': utc(),
                           'partial_jobs_preserved': True, 'next_action': 'Use a new output path and --reuse this directory after fixing the diagnosed dependency.'})
        raise

if __name__ == '__main__':
    main()
