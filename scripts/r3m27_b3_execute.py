#!/usr/bin/env python3
"""B3-only outer coordinator; frozen numerical and checkpoint code stay intact."""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cr_repro.r3m11 import source_digest
from scripts import r3m17_checkpoint_guard as guard
from scripts.r3m17_preflight import numerical_metadata

SOURCE = '581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
INITIAL = 'ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa'
FORECAST = '5eb9920d10ed467df7bc512cbbf983ee1ce95d2df94a15d21aa8e6940ebf743e'
FORECAST_PAYLOAD = 'be693bbae3a90420b25f441431ee0f63b2dd8131fd1c2017c81c847e83a4c64e'
B2_RESULT = 'f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc'
PARENT = 'e32f62864ded928580d00b31f2dcdbb4ea688ed9'
SCIENCE = '/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python'
CONFIG = ROOT / 'configs/r3m27/B3.json'
FORECAST_PATH = ROOT / 'results/R3M26/temporal/B3_FROZEN_FORECAST.json'
B2_RESULT_PATH = ROOT / 'results/R3M20_N1/intake/collision/result.json'
CHUNK = 128
NSTEP = 7172
CHUNKS = 57
STATE_BYTES = 1_008_000_128
GPU_RESERVE = 2 * 1024**3
HOST_RESERVE = 8 * 1024**3
DISK_REQUIRED = 80 * 1024**3
DISK_REMAIN = 100 * 1024**3
TOTAL_SECONDS = 14_400
COMMAND_SECONDS = {'resource': 600, 'prepare': 3600, 'collision': 3600, 'snapshot': 1800}
SOURCE_PATHS = (
    'scripts/r3m27_b3_execute.py', 'tests/test_r3m27_b3_execute.py',
    'scripts/r3m13_initial_state_pair.py', 'scripts/r3m14_collision_initial_witness.py',
    'scripts/r3m17_checkpoint_guard.py', 'scripts/r3m15_resource_probe.py',
    'scripts/r3m26_temporal.py', 'scripts/r3m26_budget.py',
)


def sha(path: Path) -> str:
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def publish(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def git(*args: str) -> str:
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def validate_b3_config(cfg: dict) -> None:
    expected = read(ROOT / 'configs/r3m16/B1.json')
    if sha(ROOT / 'configs/r3m16/B1.json') != '7a7fc7a4ea484fa65d73d38eeb49b628760a7b4ed144075275988139c0c8ab2c':
        raise ValueError('frozen B1 config bytes changed')
    expected['dt'] = .00625
    if cfg != expected or type(cfg.get('dt')) is not float:
        raise ValueError('B3 must equal frozen B1 family except requested dt=.00625')
    if source_digest() != SOURCE:
        raise ValueError('frozen numerical source digest mismatch')
    n = numerical_metadata(cfg)
    if (n['grid_shape'] != [350, 300, 600] or n['nstep'] != NSTEP or
            n['chunk_count'] != CHUNKS or n['last_chunk_steps'] != 4 or
            not math.isclose(n['actual_dt'], .00624946176119497, rel_tol=0, abs_tol=1e-16) or
            not math.isclose(n['physical_horizon_au'], 44.821139751290325, rel_tol=0, abs_tol=1e-11)):
        raise ValueError('B3 geometry/timestep drift')


def _science_env() -> dict:
    env = os.environ.copy()
    env.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE='1',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MLFLOW_DISABLE_AGENT_HINT='1')
    libraries = (
        '/home/cosmosapjw/.local/lib/python3.10/site-packages/nvidia/cufft/lib',
        '/home/cosmosapjw/.local/lib/python3.10/site-packages/nvidia/cublas/lib',
        '/usr/local/cuda/lib64', '/usr/lib/x86_64-linux-gnu/dri',
        '/usr/lib/x86_64-linux-gnu/gallium-pipe',
    )
    env['LD_LIBRARY_PATH'] = ':'.join(libraries + (env.get('LD_LIBRARY_PATH', ''),))
    return env


def runtime_identity() -> dict:
    code = ('import json,platform,sys,numpy,scipy,cupy as cp; '
            'print(json.dumps(dict(python=platform.python_version(),executable=sys.executable,'
            'numpy=numpy.__version__,scipy=scipy.__version__,cupy=cp.__version__,'
            'cuda_runtime=cp.cuda.runtime.runtimeGetVersion(),'
            'cuda_driver_api=cp.cuda.runtime.driverGetVersion(),'
            'device=cp.cuda.runtime.getDeviceProperties(0)["name"].decode())))')
    read_text = subprocess.check_output([SCIENCE, '-B', '-c', code],
                                        cwd=ROOT, env=_science_env(), text=True, timeout=60)
    value = json.loads(read_text.strip())
    required = dict(python='3.12.3', executable=SCIENCE, numpy='2.5.3',
                    scipy='1.18.1', cupy='14.2.0', cuda_runtime=12090,
                    cuda_driver_api=13020, device='NVIDIA GeForce RTX 3090')
    if value != required:
        raise ValueError(f'scientific runtime differs from frozen environment: {value}')
    return value


def command_plan(config: Path, root: Path) -> list[dict]:
    prepared, collision = root / 'preparation', root / 'collision'
    commands = [
        dict(phase='resource', argv=[SCIENCE, str(ROOT/'scripts/r3m15_resource_probe.py'),
                                     '--config', str(config), '--out', str(root/'resource.json')]),
        dict(phase='prepare', argv=[SCIENCE, str(ROOT/'scripts/r3m13_initial_state_pair.py'),
                                    'prepare', '--config', str(config), '--out', str(prepared)]),
    ]
    for chunk in range(1, CHUNKS + 1):
        done = min(chunk * CHUNK, NSTEP)
        steps = done - (chunk - 1) * CHUNK
        commands.append(dict(phase='collision', chunk=chunk, done=done, steps=steps,
            argv=[SCIENCE, str(ROOT/'scripts/r3m14_collision_initial_witness.py'),
                  '--config', str(config), '--prepared', str(prepared),
                  '--out', str(collision), '--max-steps', str(CHUNK)]))
        commands.append(dict(phase='snapshot', chunk=chunk, done=done,
            argv=[SCIENCE, str(ROOT/'scripts/r3m17_checkpoint_guard.py'), 'snapshot',
                  '--run', str(collision), '--out', str(root/'generations'/f'g{done:06d}'),
                  '--config', str(config)]))
    return commands


def build_plan(config: Path, root: Path) -> dict:
    config, root = Path(config).absolute(), Path(root).absolute()
    if config != CONFIG or not root.is_absolute() or root == ROOT or ROOT in root.parents:
        raise ValueError('canonical B3 config and external output root required')
    cfg = read(config)
    validate_b3_config(cfg)
    if sha(FORECAST_PATH) != FORECAST or sha(B2_RESULT_PATH) != B2_RESULT:
        raise ValueError('frozen forecast or B2 raw result bytes changed')
    frozen = read(FORECAST_PATH)
    payload = json.dumps(frozen['payload'], sort_keys=True, separators=(',', ':'), allow_nan=False)
    if frozen.get('payload_sha256') != FORECAST_PAYLOAD or hashlib.sha256(payload.encode()).hexdigest() != FORECAST_PAYLOAD:
        raise ValueError('frozen forecast payload changed')
    head = git('rev-parse', 'HEAD')
    if git('merge-base', PARENT, head) != PARENT or head == PARENT:
        raise ValueError('B3 coordinator must be committed on descendant branch')
    n = numerical_metadata(cfg)
    return dict(schema='BASS_CR_R3M27_B3_CONTRACT_V1', canonical_node=
        'N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT',
        experiment_id='R3M27_B3_100KEVU_B2_H020_DT000625_20260924',
        hypothesis='One held-out B3 point tests fixed-h selected-span temporal envelope.',
        model_id='NONRELATIVISTIC_ONE_ELECTRON_FIXED_TARGET_STRAIGHT_LINE_POINT_COULOMB_V1',
        source_commit=head, parent_commit=PARENT, source_digest=SOURCE,
        source_hashes={name: sha(ROOT/name) for name in SOURCE_PATHS},
        config=cfg, config_path=str(config), config_sha256=sha(config),
        changed_parameter='requested real dt only: .025/.0125 family to .00625',
        numerical=n, initial_reference_sha256=INITIAL,
        b2_result_sha256=B2_RESULT, forecast_sha256=FORECAST,
        forecast_payload_sha256=FORECAST_PAYLOAD,
        runtime=runtime_identity(), output_root=str(root),
        commands=command_plan(config, root),
        observable=dict(id='Gram P_span_by_nmax cumulative n<=1/2/3',
                        scope='100 keV/u b=2 fixed-h selected finite spans', units='probability'),
        acceptance=dict(pair_relative=.001, empirical_time_relative=.001,
                        forecast_immutable=True, production_admission=False),
        resources=dict(gpu_jobs=1, gpu_reserve_bytes=GPU_RESERVE,
                       host_reserve_bytes=HOST_RESERVE, state_bytes=STATE_BYTES,
                       generation_count=CHUNKS,
                       generations_bytes=STATE_BYTES*CHUNKS,
                       disk_required_free_bytes=DISK_REQUIRED,
                       disk_remaining_floor_bytes=DISK_REMAIN,
                       total_seconds_cap=TOTAL_SECONDS,
                       command_seconds_cap=COMMAND_SECONDS,
                       cpu_workers=1, retained_generations=CHUNKS),
        retry_policy='NO_AUTOMATIC_RETRY; explicit resume only after verified frontier',
        new_full_collision_limit=1,
        failure_branch='Preserve first failure and frontier; do not reinterpret resource stop as numerical failure.',
        production_admission=False)


def validate_plan(plan: dict, config: Path, root: Path) -> None:
    expected = build_plan(config, root)
    if json.dumps(plan, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('B3 exact contract/config/argv/source/runtime mismatch')


def frontier_action(chunk: int, done: int, expected: int, has_generation: bool) -> str:
    if type(chunk) is not int or not 1 <= chunk <= CHUNKS or type(done) is not int:
        raise ValueError('invalid chunk/done type or range')
    if expected != min(chunk*CHUNK, NSTEP):
        raise ValueError('expected B3 frontier mismatch')
    if has_generation:
        return 'SKIP_VERIFIED_GENERATION'
    before = (chunk-1)*CHUNK
    if done == before:
        return 'RUN_CHUNK'
    if done == expected:
        return 'PUBLISH_ONLY'
    raise ValueError('active checkpoint outside frozen B3 frontier')


def validate_generation(generation: Path, cfg: dict, expected_done: int) -> dict:
    manifest = read(generation/guard.MANIFEST_NAME)
    if manifest.get('schema') != guard.SCHEMA or manifest.get('status') != 'PUBLISHED_VERIFIED_LOCAL':
        raise ValueError('generation is not published')
    inventory = guard.validate_checkpoint(generation, cfg)
    if any(manifest.get(key) != value for key, value in inventory.items()):
        raise ValueError('generation manifest/inventory mismatch')
    if inventory['done'] != expected_done or inventory['nstep'] != NSTEP:
        raise ValueError('generation frontier differs from B3 contract')
    return manifest


def _host_available() -> int:
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1])*1024
    raise ValueError('MemAvailable unavailable')


def _gpu_free() -> int:
    output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free',
                                      '--format=csv,noheader,nounits'], text=True, timeout=15)
    return int(output.splitlines()[0].strip())*1024**2


def resources(root: Path) -> dict:
    disk = shutil.disk_usage(root.parent)
    value = dict(disk_free_bytes=disk.free, gpu_free_bytes=_gpu_free(),
                 host_available_bytes=_host_available(),
                 gpu_free_semantics='NVIDIA_SMI_SAMPLED_MIB',
                 disk_required_free_bytes=DISK_REQUIRED,
                 disk_remaining_floor_bytes=DISK_REMAIN)
    if (disk.free < DISK_REQUIRED + DISK_REMAIN or
            value['gpu_free_bytes'] < GPU_RESERVE or
            value['host_available_bytes'] < HOST_RESERVE):
        raise MemoryError(f'B3 resource preflight failed: {value}')
    return value


def _command(label: str, spec: dict, root: Path, started: float) -> dict:
    phase = spec['phase']
    cap = COMMAND_SECONDS[phase]
    argv = spec['argv']
    minimum = {'gpu': _gpu_free(), 'host': _host_available(), 'disk': shutil.disk_usage(root).free}
    stop = None
    begin = time.monotonic()
    begin_wall = time.time()
    witness_path = root/'collision'/'r3m14_initial_binding.json'
    first_witness = phase == 'collision' and not witness_path.exists()
    try:
        import mlflow
    except ImportError:
        mlflow = None
    trace = mlflow.start_span(name=label) if mlflow else contextlib.nullcontext(None)
    with trace as span:
        if span:
            span.set_inputs(dict(argv=argv, cwd=str(ROOT), contract_phase=phase))
        with (root/(label+'.stdout')).open('x') as stdout, (root/(label+'.stderr')).open('x') as stderr:
            process = subprocess.Popen(argv, cwd=ROOT, env=_science_env(),
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            while process.poll() is None:
                try:
                    minimum['gpu'] = min(minimum['gpu'], _gpu_free())
                    minimum['host'] = min(minimum['host'], _host_available())
                    minimum['disk'] = min(minimum['disk'], shutil.disk_usage(root).free)
                    if minimum['gpu'] < GPU_RESERVE or minimum['host'] < HOST_RESERVE or minimum['disk'] < DISK_REMAIN:
                        stop = 'RESOURCE_RESERVE_BREACH'
                except BaseException as exc:
                    stop = 'RESOURCE_MONITOR_FAILED:' + repr(exc)
                if time.monotonic()-begin > cap or time.monotonic()-started > TOTAL_SECONDS:
                    stop = 'COMMAND_OR_TOTAL_DEADLINE'
                if stop:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    break
                time.sleep(2)
            code = process.wait()
        row = dict(label=label, phase=phase, argv=argv, exit_code=code,
                   wall_seconds=time.monotonic()-begin, stop_reason=stop,
                   minimum_sampled_gpu_free_bytes=minimum['gpu'],
                   minimum_sampled_host_available_bytes=minimum['host'],
                   minimum_sampled_disk_free_bytes=minimum['disk'],
                   stdout_sha256=sha(root/(label+'.stdout')),
                   stderr_sha256=sha(root/(label+'.stderr')),
                   trace_id=span.trace_id if span else None)
        if first_witness and witness_path.exists():
            row['internal_initial_witness_elapsed_seconds_including_setup'] = max(
                0.0, witness_path.stat().st_mtime - begin_wall)
            row['internal_preparation_work'] = dict(imag_steps=4800,
                imag_dt_au=.00625,
                wall_semantics='WITNESS_FILE_BOUNDARY_INCLUDES_RUNNER_SETUP_HASH_AND_PREPARATION')
        if span:
            span.set_outputs(row)
    if mlflow:
        mlflow.flush_trace_async_logging()
    publish(root/'receipts'/(label+'.json'), row)
    if code or stop:
        raise RuntimeError(f'{label}: exit={code}; stop={stop}')
    return row


def _prepared(root: Path, cfg: dict) -> dict:
    from scripts.r3m14_collision_initial_witness import validate_prepared
    value = validate_prepared(root/'preparation', cfg, SOURCE)
    if value['state_file_sha256'] != INITIAL or value['receipt']['config'] != cfg:
        raise ValueError('B3 fresh preparation differs from canonical B initial/config')
    return value


def execute(contract: Path, approval: str, *, explicit_resume: bool = False) -> dict:
    contract = Path(contract).absolute()
    if sha(contract) != approval:
        raise ValueError('explicit B3 contract SHA approval mismatch')
    plan = read(contract)
    root, config = Path(plan['output_root']), Path(plan['config_path'])
    validate_plan(plan, config, root)
    if root.exists() and not explicit_resume:
        raise FileExistsError('fresh B3 output required; explicit frontier-checked resume only')
    if not root.exists():
        root.mkdir(parents=True, exist_ok=False)
        publish(root/'RUN.json', dict(contract_sha256=approval,
            source_commit=plan['source_commit'], new_full_collision_limit=1,
            automatic_retry=False, production_admission=False))
    elif read(root/'RUN.json')['contract_sha256'] != approval:
        raise ValueError('resume contract SHA mismatch')
    (root/'receipts').mkdir(exist_ok=True)
    (root/'generations').mkdir(exist_ok=True)
    try:
        import mlflow
    except ImportError:
        pass  # Numerical execution and durable receipts do not depend on tracing.
    else:
        os.environ.setdefault('MLFLOW_DISABLE_AGENT_HINT', '1')
        if not (os.environ.get('MLFLOW_TRACKING_URI') and os.environ.get('MLFLOW_EXPERIMENT_ID')):
            mlflow.set_tracking_uri('sqlite:///' + str(root/'mlflow.db'))
            mlflow.set_experiment('R3M27_B3_FULL_COLLISION')
    started = time.monotonic()
    stage = 'RESOURCE_PREFLIGHT'
    with (root/'gpu.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            if (root/'COMPLETE.json').exists():
                raise FileExistsError('completed B3 must not rerun')
            if not (root/'RESOURCE_INVENTORY.json').exists():
                publish(root/'RESOURCE_INVENTORY.json', resources(root))
            else:
                resources(root)
            if not (root/'resource.json').exists():
                _command('resource_preflight', plan['commands'][0], root, started)
            if not (root/'receipts/resource_preflight.json').is_file():
                raise ValueError('resource output without completed command receipt')
            if read(root/'resource.json').get('status') != 'PASS_RESOURCE_PREFLIGHT':
                raise ValueError('FFT resource preflight did not pass')
            stage = 'PREPARATION'
            if not (root/'preparation').exists():
                _command('prepare', plan['commands'][1], root, started)
            if not (root/'receipts/prepare.json').is_file():
                raise ValueError('preparation output without completed command receipt')
            prepared = _prepared(root, plan['config'])
            if not (root/'PREPARATION_BINDING.json').exists():
                publish(root/'PREPARATION_BINDING.json', dict(
                    status='PASS_EXACT_B3_CONFIG_AND_CANONICAL_INITIAL',
                    receipt_sha256=prepared['receipt_sha256'],
                    initial_sha256=prepared['state_file_sha256'],
                    seconds=prepared['receipt']['seconds'],
                    internal_preparation_expected_once_on_first_collision_chunk=True))
            commands = plan['commands'][2:]
            for i in range(CHUNKS):
                collision, snapshot = commands[2*i:2*i+2]
                chunk, expected = i+1, snapshot['done']
                stage = f'COLLISION_CHUNK_{chunk:03d}'
                if source_digest() != SOURCE:
                    raise ValueError('frozen numerical source changed before chunk')
                generation = root/'generations'/f'g{expected:06d}'
                if generation.exists():
                    validate_generation(generation, plan['config'], expected)
                    continue
                active = root/'collision'
                done = guard.validate_checkpoint(active, plan['config'])['done'] if (active/'state.json').exists() else 0
                action = frontier_action(chunk, done, expected, False)
                if action == 'RUN_CHUNK':
                    _command(f'collision.chunk{chunk:03d}', collision, root, started)
                    inventory = guard.validate_checkpoint(active, plan['config'])
                    if inventory['done'] != expected:
                        raise ValueError('writer returned without exact B3 frontier')
                stage = f'SNAPSHOT_CHUNK_{chunk:03d}'
                _command(f'snapshot.g{expected:06d}', snapshot, root, started)
                manifest = validate_generation(generation, plan['config'], expected)
                publish(root/'receipts'/f'chunk{chunk:03d}.committed.json', dict(
                    status='CHUNK_AND_GENERATION_COMMITTED', chunk=chunk, done=expected,
                    generation_manifest_sha256=sha(generation/guard.MANIFEST_NAME),
                    state_sha256=manifest['files']['state.npy']['sha256'],
                    next_chunk_authorized=chunk<CHUNKS))
            stage = 'FINAL_AUDIT'
            final = guard.validate_checkpoint(root/'collision', plan['config'])
            result = read(root/'collision/result.json')
            if final['done'] != NSTEP or result.get('status') != 'completed':
                raise ValueError('B3 final result/checkpoint incomplete')
            complete = dict(status='COMPLETE', job='B3', chunks=CHUNKS,
                retained_generations=CHUNKS, done=NSTEP, nstep=NSTEP,
                contract_sha256=approval,
                preparation_receipt_sha256=prepared['receipt_sha256'],
                result_sha256=sha(root/'collision/result.json'),
                final_generation_manifest_sha256=sha(root/'generations'/'g007172'/guard.MANIFEST_NAME),
                new_full_collisions=1, production_admission=False)
            publish(root/'COMPLETE.json', complete)
            return complete
        except BaseException as exc:
            failure = root/'FIRST_FAILURE.json'
            if not failure.exists():
                try:
                    publish(failure, dict(stage=stage, exception_type=type(exc).__name__,
                        message=str(exc), traceback=traceback.format_exc(),
                        automatic_retry=False, scientific_nonconvergence='UNDETERMINED',
                        completed_generations=len(list((root/'generations').glob('g*/r3m17_generation_manifest.json'))),
                        production_admission=False))
                except BaseException:
                    pass
            raise


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    f = sub.add_parser('freeze')
    f.add_argument('--config', type=Path, default=CONFIG)
    f.add_argument('--root', type=Path, required=True)
    f.add_argument('--contract', type=Path, required=True)
    r = sub.add_parser('run')
    r.add_argument('--contract', type=Path, required=True)
    r.add_argument('--approve-sha256', required=True)
    r.add_argument('--explicit-resume', action='store_true')
    args = parser.parse_args(argv)
    if args.command == 'freeze':
        dirty = git('status', '--porcelain', '--', 'scripts/r3m27_b3_execute.py',
                    'tests/test_r3m27_b3_execute.py', 'configs/r3m27/B3.json')
        if dirty:
            raise ValueError('commit B3 source/config/tests before freeze')
        plan = build_plan(args.config, args.root)
        if args.root.exists():
            raise FileExistsError('fresh B3 output root required')
        resources(args.root)
        publish(args.contract, plan)
        manifest = args.contract.with_name('HASH_MANIFEST.json')
        publish(manifest, dict(contract_sha256=sha(args.contract),
            config_sha256=plan['config_sha256'], forecast_sha256=FORECAST,
            forecast_payload_sha256=FORECAST_PAYLOAD,
            source_hashes=plan['source_hashes'], output_root=plan['output_root']))
        print(json.dumps(dict(contract=str(args.contract), sha256=sha(args.contract),
                              generations=CHUNKS, gpu_work=0)))
    else:
        print(json.dumps(execute(args.contract, args.approve_sha256,
                                 explicit_resume=args.explicit_resume), sort_keys=True))


if __name__ == '__main__':
    main()
