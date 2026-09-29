"""Spawned, single-thread native worker. Never import this to run a query inline."""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import sys
import traceback

from parallel_bridge import GlobalBudget, PlannedQuery, validate_pair

HERE = Path(__file__).resolve().parent
R4C = HERE.parent / 'r4c_temporal_continuation'
if str(R4C) not in sys.path:
    sys.path.insert(0, str(R4C))

_STATE = None


def initialize_worker(source_dir: str, build_dir: str, contract: dict, context_id: str,
                      budget_dir: str, tasks_dir: str, cpus: list[int], ram_bytes: int) -> None:
    """Check frozen bytes and architecture before MomentKernel may dlopen."""
    global _STATE
    from execution_admission import THREAD_KEYS, check_native_build
    if any(os.environ.get(k) != '1' for k in THREAD_KEYS):
        raise ValueError('all worker thread limits must equal one')
    if ram_bytes <= 0 or not cpus:
        raise ValueError('worker RAM/CPU bounds required')
    allowed = os.sched_getaffinity(0)
    if not set(cpus).issubset(allowed):
        raise ValueError('approved worker CPU set exceeds current affinity')
    os.sched_setaffinity(0, set(cpus))
    resource.setrlimit(resource.RLIMIT_AS, (ram_bytes, ram_bytes))

    import continue_temporal as serial
    native = check_native_build(Path(build_dir), contract,
                                serial.ANALYTIC / 'moment_kernel.cpp')
    from bass_foundations.two_center import Trajectory, symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from exact_cross import MomentKernel
    from assemble import assemble
    from runtime import load_bank
    from analytic_adapter import AnalyticEvaluator

    source = Path(source_dir)
    bank, basis_record = load_bank(source)
    if basis_record['identity'] != serial.strict_json(source/'SCIENCE_CONTEXT.json')['context']['physics_identity']['basis_identity']:
        raise ValueError('worker basis identity mismatch')
    channels = symmetric_channels(bank)
    velocity = projectile_speed_au(contract['energy_keV_per_u'])
    trajectory = Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),
                            ((0.,0.,0.),(0.,0.,velocity)))
    kernel = MomentKernel(str(Path(build_dir).resolve()))
    if (kernel.receipt.get('source_sha256') != native['source_sha256']
        or kernel.receipt.get('library_sha256') != native['library_sha256']):
        raise ValueError('worker native constructor identity mismatch')
    evaluator = AnalyticEvaluator(assemble, trajectory=trajectory,
                                 channels=channels, kernel=kernel)
    _STATE = {'evaluator': evaluator, 'contract': contract,
              'context_id': context_id, 'budget': GlobalBudget(Path(budget_dir)),
              'tasks_dir': Path(tasks_dir), 'native': native}


def compute_query(item: PlannedQuery) -> dict:
    """Run the unchanged ordered resolution ladder for exactly one time query."""
    if _STATE is None:
        raise RuntimeError('spawn worker was not initialized')
    from execution_admission import EvaluationLedger
    from qualified_provider import ResolutionQualifiedProvider

    state = _STATE
    task = state['tasks_dir'] / item.query_id
    task.mkdir(parents=True, exist_ok=False)
    ledger = EvaluationLedger(state['evaluator'], task)

    def evaluate(t, order, subdivisions):
        state['budget'].reserve(item.query_id, order, subdivisions)
        return ledger(t, order, subdivisions)

    try:
        provider = ResolutionQualifiedProvider(
            evaluate=evaluate,
            resolutions=state['contract']['runtime_reference_resolutions'],
            screens=state['contract']['screens'],
            context_id=state['context_id'], out_dir=task,
            max_unique_queries=1)
        provider.at(float.fromhex(item.time_hex))
        record = validate_pair(task/'runtime_queries', item,
                               state['context_id'], state['contract'])
        record.update({'schema': 'BASS_R4F_WORKER_TASK_V1',
                       'raw_attempts': ledger.attempts,
                       'worker_pid': os.getpid(), 'task_dir': str(task),
                       'native_check': state['native']})
        with (task/'TASK_RECEIPT.json').open('x') as f:
            json.dump(record, f, indent=2, allow_nan=False)
            f.flush(); os.fsync(f.fileno())
        return record
    except BaseException as exc:
        with (task/'TASK_FAILURE.json').open('x') as f:
            json.dump({'type': type(exc).__name__, 'message': str(exc),
                       'traceback': traceback.format_exc()}, f, indent=2)
            f.flush(); os.fsync(f.fileno())
        raise
