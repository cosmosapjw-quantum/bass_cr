"""Bounded physical-t=0 B2 event-window experiment; never a collision runner.

Freeze a contract after committing this source. An exact SHA is required for
one fresh GPU attempt. All old numerical kernels, inputs and gates stay frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import traceback

import numpy as np

from .r3m24_cross_window import (CONFIG, ROOT, SELECTION, canonical_specs,
                                  runtime_identity, source_snapshot)
from .r3m24_guard import (bind_generation, file_sha, object_sha, publish_json,
                           read_json)
from .r3m24_gpu import (Budget, CAL_LIMIT, GPU_RESERVE, HOST_RESERVE, INNER,
                         MAX_BASIS, TIGHT, work_trace)
from .r3m24_metrics import repeat_kind, tightening_is_unchanged

PARENT = 'ddcfd91eca55f9d1a2e1d846737c26e2d9febb45'
DESIGN = 'docs/r3m25/RESEARCH_PLAN.md'
SELF = 'scripts/r3m25_event_window.py'
LIMITS = dict(kinetic_matvecs=4000, total_seconds=7200,
              window_seconds=3600)
SCHEMA = 'BASS_CR_R3M25_PHYSICAL_T0_V1'


def event_geometry(saved_done: int, nstep: int, dt: float,
                   z_start: float, z_stop: float) -> dict:
    if (type(saved_done) is not int or type(nstep) is not int or
            not 0 <= saved_done < nstep or not math.isfinite(dt) or dt <= 0 or
            not all(math.isfinite(v) for v in (z_start, z_stop)) or
            not z_start < 0 < z_stop):
        raise ValueError('invalid frozen event geometry')
    initial = z_start / (z_stop - z_start) * nstep * dt
    start = math.floor(-initial / dt) - 1
    if saved_done > start or start + 4 > nstep:
        raise ValueError('sealed generation cannot reach event window')
    t0, t1 = initial + start * dt, initial + (start + 4) * dt
    if not t0 < 0 < t1:
        raise ValueError('four-step window does not bracket t=0')
    return dict(start_step=start, warmup_steps=start - saved_done,
                steps=4, t0=t0, t1=t1, horizon_au=4 * dt,
                initial_time_au=initial,
                warmup_is_historical_checkpoint=False)


def required_worst_matvecs(warmup_steps: int, max_basis: int) -> int:
    if type(warmup_steps) is not int or warmup_steps < 0 or type(max_basis) is not int or max_basis < 1:
        raise ValueError('positive work dimensions required')
    # Probe; warmup; Strang ladder/parity; two one-step calibrations;
    # CF4 n4/8/16/32 sub2, n8 sub4, n16 tighter sub2.
    return 3 + warmup_steps + 34 + (2*1*(2+4) + 2*(4+8+16+32)*2 +
                                    2*8*4 + 2*16*2) * max_basis


def _distance(a, b, dv: float) -> float:
    return float(np.linalg.norm((a - b).ravel()) * math.sqrt(dv))


def assess(d: dict) -> dict:
    required = ('d4_8', 'd8_16', 'd16_32', 'substep_repeat',
                'strang_scale', 'physical_norm')
    if any(not isinstance(d.get(k), (int, float)) or
           not math.isfinite(d[k]) or d[k] < 0 for k in required):
        raise ValueError('finite nonnegative distances and norm required')
    if min(d['d4_8'], d['strang_scale'], d['physical_norm']) <= 0:
        raise ValueError('positive scales and norm required')
    tight_status = d['tightening_status']
    if tight_status not in ('EXECUTED', 'SKIPPED_UNCHANGED_WORK'):
        raise ValueError('unknown tightening status')
    if tight_status == 'EXECUTED':
        tight = d['tight_repeat']
        if (not isinstance(tight, (int, float)) or not math.isfinite(tight) or tight < 0 or
                d['tightening_independence'] != 'CHANGED_WORK'):
            raise ValueError('tightening needs changed work and finite distance')
    elif d['tight_repeat'] is not None or d['tightening_independence'] != 'UNCHANGED_WORK_NOT_INDEPENDENT':
        raise ValueError('unchanged tightening is not an independent repeat')
    independent = d['substep_independence'] == 'CHANGED_WORK'
    tight = d['tight_repeat'] if tight_status == 'EXECUTED' else 0.0
    error = max(d['d16_32'], d['substep_repeat'], tight)
    def gate(scale, name):
        if not independent:
            return 'UNRESOLVED_INDEPENDENT_REPEAT'
        return 'PASS_LOCAL_' + name if error < .01 * scale else 'NO_GO_LOCAL_' + name
    machine_floor = 128 * np.finfo(float).eps * d['physical_norm']
    repeat_floor = max(d['substep_repeat'], tight)
    floor = max(machine_floor, 100 * repeat_floor)
    signal = (d['d4_8'], d['d8_16'], d['d16_32'])
    orders = None
    if not independent:
        order = 'UNRESOLVED_INDEPENDENT_REPEAT'
    elif min(signal) <= floor:
        order = 'UNRESOLVED_FP_FLOOR'
    else:
        orders = [math.log2(signal[0]/signal[1]),
                  math.log2(signal[1]/signal[2])]
        order = ('PASS_LOCAL_FOURTH_ORDER_COMPATIBLE' if
                 all(3 <= p <= 5 for p in orders) else 'NO_GO_LOCAL_ORDER')
    return dict(self_scaled_reference=gate(d['d4_8'], 'SELF_SCALED'),
                reference_for_strang=gate(d['strang_scale'], 'STRANG_SCALE'),
                order_characterization=order, orders=orders,
                self_scaled_denominator=d['d4_8'],
                self_scaled_one_percent=.01 * d['d4_8'],
                strang_one_percent=.01 * d['strang_scale'],
                order_signal_floor=floor,
                tightening_is_independent=tight_status == 'EXECUTED',
                scope='FOUR_B2_STEP_PHYSICAL_T0_LOCAL_ONLY',
                global_time_error='NOT_EVALUATED',
                production_admission=False)


def _git(*args: str) -> str:
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def _sources() -> dict:
    value = source_snapshot()
    value[SELF] = file_sha(ROOT / SELF)
    value[DESIGN] = file_sha(ROOT / DESIGN)
    return value


def freeze() -> dict:
    head = _git('rev-parse', 'HEAD')
    if head == PARENT or _git('merge-base', PARENT, head) != PARENT:
        raise ValueError('commit R3M25 source on a descendant branch before freeze')
    cfg, selection = read_json(ROOT/CONFIG), read_json(ROOT/SELECTION)
    spec = canonical_specs(cfg, selection)[1]
    geo = event_geometry(spec['done'], spec['nstep'], spec['actual_dt_au'],
                         cfg['z_start'], cfg['z_stop'])
    if (geo['start_step'] != 1194 or geo['warmup_steps'] != 42 or
            geo['t0'] != -0.016665231363186095 or
            geo['t1'] != 0.033330462726373966):
        raise ValueError('event geometry drift')
    plan = dict(schema=SCHEMA, root=str(ROOT), parent_commit=PARENT,
                implementation_commit=head, source_hashes=_sources(),
                config=cfg, generation=spec, event=geo,
                runtime_identity=runtime_identity(), limits=LIMITS,
                max_basis=MAX_BASIS, inner_budget=INNER,
                tight_budget=TIGHT, calibration_limit=CAL_LIMIT,
                required_worst_matvecs=required_worst_matvecs(42, MAX_BASIS),
                scope='FOUR_B2_STEP_PHYSICAL_T0_LOCAL_ONLY',
                production_admission=False,
                execution_policy='ONE_FRESH_SHA_APPROVED_ATTEMPT_NO_RETRY')
    plan['computation_key'] = object_sha(plan)
    return plan


def validate(plan: dict) -> None:
    if (plan.get('schema') != SCHEMA or plan.get('root') != str(ROOT) or
            plan.get('parent_commit') != PARENT or
            _git('rev-parse', 'HEAD') != plan.get('implementation_commit') or
            _git('merge-base', PARENT, plan['implementation_commit']) != PARENT or
            plan.get('source_hashes') != _sources() or
            plan.get('runtime_identity') != runtime_identity() or
            plan.get('limits') != LIMITS or plan.get('max_basis') != MAX_BASIS or
            plan.get('inner_budget') != INNER or plan.get('tight_budget') != TIGHT or
            plan.get('calibration_limit') != CAL_LIMIT or
            plan.get('required_worst_matvecs') != required_worst_matvecs(42, MAX_BASIS) or
            plan.get('scope') != 'FOUR_B2_STEP_PHYSICAL_T0_LOCAL_ONLY' or
            plan.get('production_admission') is not False):
        raise ValueError('frozen source/runtime/limits/scope mismatch')
    cfg, selection = read_json(ROOT/CONFIG), read_json(ROOT/SELECTION)
    spec = canonical_specs(cfg, selection)[1]
    geo = event_geometry(spec['done'], spec['nstep'], spec['actual_dt_au'],
                         cfg['z_start'], cfg['z_stop'])
    if plan['config'] != cfg or plan['generation'] != spec or plan['event'] != geo:
        raise ValueError('frozen configuration/generation/event mismatch')
    core = dict(plan)
    key = core.pop('computation_key')
    if object_sha(core) != key:
        raise ValueError('computation key mismatch')


def _resources(cp, budget: Budget, minimum: dict,
               upcoming_host_bytes: int = 0) -> None:
    from .r3m19_performance import hardware_inventory
    free = int(cp.cuda.runtime.memGetInfo()[0])
    host = int(hardware_inventory(include_gpu=False)['memory']['available_bytes'])
    minimum['gpu'].append(free)
    minimum['host'].append(host)
    if (free < GPU_RESERVE or host - upcoming_host_bytes < HOST_RESERVE):
        raise MemoryError('GPU/host reserve lost')
    budget.check()


def _cf4(mf, cp, state, spec, n: int, substeps: int, inner: float,
         budget: Budget, key: str, minimum: list[int]):
    current = state.copy()
    infos = []
    before = budget.count
    mark = time.monotonic()
    for j in range(n):
        current, info = mf.cf4_step(current,
            spec['actual_start_time_au'] + j*spec['horizon_au']/n,
            spec['horizon_au']/n, physical_step_budget=inner/n,
            action_substeps=substeps, max_basis=MAX_BASIS,
            max_basis_bytes=(MAX_BASIS+1)*int(state.nbytes))
        infos.append(info)
        _resources(cp, budget, minimum)
    cp.cuda.get_current_stream().synchronize()
    wall = time.monotonic() - mark
    _resources(cp, budget, minimum, upcoming_host_bytes=int(state.nbytes))
    mark = time.monotonic()
    host = cp.asnumpy(current)
    transfer = time.monotonic() - mark
    _resources(cp, budget, minimum)
    del current
    if not np.isfinite(host).all():
        raise FloatingPointError('nonfinite CF4 endpoint')
    sha = hashlib.sha256(memoryview(host).cast('B')).hexdigest()
    trace = work_trace(spec, key, n, substeps, infos, sha, 'cupy')
    if trace['matvecs'] != budget.count-before:
        raise ValueError('CF4 kinetic work accounting mismatch')
    actions = [a for step in infos for a in step['actions']]
    row = dict(sha256=sha, physical_norm=float(np.linalg.norm(host.ravel())*math.sqrt(mf.runner.dv)),
               finite=True, fft_matvecs=trace['matvecs'],
               fft_transforms=2*trace['matvecs'], propagation_seconds=wall,
               host_transfer_seconds=transfer, actual_work=trace,
               actions=actions, requested_global_inner_budget=inner,
               accumulated_exact_arithmetic_inner_bound=sum(a['physical_upper_bound'] for a in actions),
               bound_semantics='EXACT_ARITHMETIC_NOT_FP_CERTIFICATE')
    return host, row


def _gpu(plan: dict, out: Path, pinned, progress: dict) -> dict:
    import cupy as cp
    from cr_repro.r3m11 import ControlledTDLRunner
    from .r3m19_performance import hardware_inventory
    from .r3m22_inner_action import BoundedMatrixFreeFullH
    from .r3m23_cross_window import _strang_ladder
    inventory = hardware_inventory(include_gpu=True)
    modeled = 20 * int(pinned.array.nbytes)
    if (inventory['gpu'].get('status') != 'AVAILABLE' or
            inventory['gpu']['device_free_bytes'] < modeled + GPU_RESERVE or
            inventory['memory']['available_bytes'] < HOST_RESERVE):
        raise MemoryError('full-H basis/static/input reservation cannot fit')
    budget = Budget(plan['limits'])
    minimum = {'gpu': [], 'host': []}
    progress.update(budget=budget, minimum=minimum, stage='GPU_PREFLIGHT')
    runner = ControlledTDLRunner(plan['config'])
    if not math.isclose(runner.dt_actual, plan['generation']['actual_dt_au'],
                        rel_tol=0, abs_tol=1e-14):
        raise ValueError('runner/selected actual timestep mismatch')
    mf = BoundedMatrixFreeFullH(runner)
    mf.matvec_monitor = budget.tick
    state = cp.asarray(pinned.array)
    cp.cuda.get_current_stream().synchronize()
    pinned.assert_current()
    held = [cp.empty_like(state) for _ in range(MAX_BASIS+1+4)]
    _resources(cp, budget, minimum)
    probe_seconds = []
    for _ in range(3):
        before = time.monotonic()
        acted = mf.generator_matvec(state, plan['generation']['actual_start_time_au'])
        cp.cuda.get_current_stream().synchronize()
        probe_seconds.append(time.monotonic()-before)
        del acted
        _resources(cp, budget, minimum)
    held.clear()
    cp.get_default_memory_pool().free_all_blocks()
    publish_json(out/'PREFLIGHT.json', dict(status='PASS', probe_matvecs=3,
        probe_seconds=probe_seconds, inventory=inventory,
        minimum_gpu_free_bytes=min(minimum['gpu']),
        minimum_host_available_bytes=min(minimum['host']),
        required_worst_matvecs=plan['required_worst_matvecs'],
        cap=LIMITS['kinetic_matvecs'],
        worst_case_can_fit_cap=plan['required_worst_matvecs'] <= LIMITS['kinetic_matvecs']))
    geometry = plan['event']
    progress['stage'] = 'DERIVED_WARMUP'
    start = plan['generation']['done']
    dt = plan['generation']['actual_dt_au']
    mark = time.monotonic()
    for j in range(start, geometry['start_step']):
        budget.tick()
        state = runner.step(state, geometry['initial_time_au'] + (j+.5)*dt)
        if (j-start) % 8 == 7:
            _resources(cp, budget, minimum)
    cp.cuda.get_current_stream().synchronize()
    warmup_wall = time.monotonic()-mark
    _resources(cp, budget, minimum)
    pinned.assert_current()
    _resources(cp, budget, minimum, upcoming_host_bytes=int(state.nbytes))
    warmup_host = cp.asnumpy(state)
    _resources(cp, budget, minimum)
    warmup_sha = hashlib.sha256(memoryview(warmup_host).cast('B')).hexdigest()
    warmup_norm = float(np.linalg.norm(warmup_host.ravel())*math.sqrt(runner.dv))
    del warmup_host
    publish_json(out/'WARMUP.json', dict(status='DERIVED_NOT_HISTORICAL_CHECKPOINT',
        input_state_sha256=pinned.receipt['state_sha256'],
        endpoint_sha256=warmup_sha, start_step=start,
        end_step=geometry['start_step'], steps=geometry['warmup_steps'],
        input_time_au=plan['generation']['actual_start_time_au'],
        endpoint_time_au=geometry['t0'],
        kinetic_matvecs=geometry['warmup_steps'], fft_transforms=2*geometry['warmup_steps'],
        physical_norm=warmup_norm, wall_seconds=warmup_wall,
        minimum_gpu_free_bytes=min(minimum['gpu']),
        minimum_host_available_bytes=min(minimum['host'])))
    budget.begin_window()
    progress['stage'] = 'EVENT_STRANG_PARITY'
    count_before = budget.count
    event_spec = dict(plan['generation'], actual_start_time_au=geometry['t0'],
                      horizon_au=geometry['horizon_au'],
                      expected_state_npy_sha256=warmup_sha)
    strang, strang_rows, parity = _strang_ladder(
        runner, mf, state, geometry['t0'], geometry['horizon_au'], budget)
    del runner.kin, runner.mask, runner.cap_half
    cp.get_default_memory_pool().free_all_blocks()
    _resources(cp, budget, minimum)
    cal_spec = dict(event_spec, horizon_au=geometry['horizon_au']/32)
    progress['stage'] = 'EVENT_INNER_CALIBRATION'
    cal2, c2 = _cf4(mf,cp,state,cal_spec,1,2,INNER/32,budget,
                    plan['computation_key'],minimum)
    cal4, c4 = _cf4(mf,cp,state,cal_spec,1,4,INNER/32,budget,
                    plan['computation_key'],minimum)
    cal_distance = _distance(cal2,cal4,runner.dv)
    del cal2,cal4
    if repeat_kind(c2['actual_work'],c4['actual_work']) != 'CHANGED_WORK' or cal_distance >= CAL_LIMIT:
        raise ValueError('independent event-state inner calibration unresolved')
    endpoints, rows = {}, {}
    for n in (4,8,16,32):
        progress['stage'] = f'EVENT_CF4_N{n}'
        endpoints[n], rows[n] = _cf4(mf,cp,state,event_spec,n,2,INNER,budget,
                                    plan['computation_key'],minimum)
    progress['stage'] = 'EVENT_CF4_SUBSTEP_REPEAT'
    sub, subrow = _cf4(mf,cp,state,event_spec,8,4,INNER,budget,
                       plan['computation_key'],minimum)
    subkind = repeat_kind(rows[8]['actual_work'],subrow['actual_work'])
    subdistance = _distance(endpoints[8],sub,runner.dv)
    del sub
    if tightening_is_unchanged(rows[16]['actions'],TIGHT):
        tightening = dict(status='SKIPPED_UNCHANGED_WORK',
                          independence='UNCHANGED_WORK_NOT_INDEPENDENT',distance=None)
    else:
        progress['stage'] = 'EVENT_CF4_TIGHTENING'
        tight, tightrow = _cf4(mf,cp,state,event_spec,16,2,TIGHT,budget,
                              plan['computation_key'],minimum)
        tightening = dict(status='EXECUTED',
                          independence=repeat_kind(rows[16]['actual_work'],
                                                   tightrow['actual_work']),
                          distance=_distance(endpoints[16],tight,runner.dv),
                          endpoint=tightrow)
        del tight
    distances = dict(d4_8=_distance(endpoints[4],endpoints[8],runner.dv),
                     d8_16=_distance(endpoints[8],endpoints[16],runner.dv),
                     d16_32=_distance(endpoints[16],endpoints[32],runner.dv),
                     substep_repeat=subdistance,
                     tight_repeat=tightening['distance'],
                     strang_scale=min(_distance(x,endpoints[32],runner.dv)
                                      for x in strang.values()),
                     physical_norm=rows[32]['physical_norm'],
                     substep_independence=subkind,
                     tightening_status=tightening['status'],
                     tightening_independence=tightening['independence'])
    gates = assess(distances)
    progress['stage'] = 'EVENT_GATE_AND_CLEANUP'
    wall = budget.end_window()
    result = dict(schema='BASS_CR_R3M25_EVENT_RESULT_V1',
                  input_consumption=pinned.receipt,
                  derived_warmup_sha256=warmup_sha,
                  event=geometry, calibration=dict(sub2=c2,sub4=c4,
                      distance=cal_distance,limit=CAL_LIMIT),
                  strang_endpoints=strang_rows, parity=parity,
                  cf4_endpoints={f'n{n}':rows[n] for n in (4,8,16,32)},
                  substep_endpoint=subrow, tightening=tightening,
                  distances=distances, gates=gates,
                  event_kinetic_matvecs=budget.count-count_before,
                  event_fft_transforms=2*(budget.count-count_before),
                  event_wall_seconds=wall,
                  total_work=budget.snapshot(),
                  minimum_sampled_gpu_free_bytes=min(minimum['gpu']),
                  minimum_sampled_host_available_bytes=min(minimum['host']),
                  production_admission=False,
                  full_collision=False, preparation_rerun=False,
                  checkpoint_write=False, projection='NOT_RUN')
    del endpoints,strang,state,mf,runner
    cp.get_default_memory_pool().free_all_blocks()
    _resources(cp, budget, minimum)
    result['total_work'] = budget.snapshot()
    result['minimum_sampled_gpu_free_bytes'] = min(minimum['gpu'])
    result['minimum_sampled_host_available_bytes'] = min(minimum['host'])
    return result


def run(contract: Path, approval: str, out: Path) -> dict:
    plan = read_json(contract, approval)
    validate(plan)
    out.mkdir(parents=False, exist_ok=False)
    publish_json(out/'RUN.json', dict(contract_sha256=approval,
        computation_key=plan['computation_key'],
        implementation_commit=plan['implementation_commit'],
        automatic_retry=False, production_admission=False))
    stage = 'INPUT_INTAKE'
    progress = {}
    try:
        with bind_generation(plan['generation']) as pinned:
            stage = 'GPU_PREFLIGHT_AND_EVENT'
            result = _gpu(plan,out,pinned,progress)
            pinned.assert_current()
        stage = 'RESULT_SEAL'
        publish_json(out/'RESULT.json',result)
        publish_json(out/'MANIFEST.json',dict(schema='BASS_CR_R3M25_EVENT_MANIFEST_V1',
            result_sha256=file_sha(out/'RESULT.json'),
            warmup_sha256=file_sha(out/'WARMUP.json'),
            preflight_sha256=file_sha(out/'PREFLIGHT.json'),
            contract_sha256=approval))
        publish_json(out/'COMPLETED.json',dict(status='LOCAL_EVENT_COMPLETE',
            manifest_sha256=file_sha(out/'MANIFEST.json'),
            production_admission=False))
        return result
    except BaseException as exc:
        budget = progress.get('budget')
        minimum = progress.get('minimum', {})
        failure=dict(schema='BASS_CR_R3M25_FIRST_FAILURE_V1',stage=progress.get('stage',stage),
            exception_type=type(exc).__name__,message=str(exc),
            traceback=traceback.format_exc(),
            resource_limited=isinstance(exc,(TimeoutError,MemoryError)),
            scientific_nonconvergence='UNDETERMINED',
            work_at_failure=budget.snapshot() if budget is not None else None,
            minimum_sampled_gpu_free_bytes=min(minimum['gpu']) if minimum.get('gpu') else None,
            minimum_sampled_host_available_bytes=min(minimum['host']) if minimum.get('host') else None,
            production_admission=False)
        try:
            publish_json(out/'FIRST_FAILURE.json',failure)
        except Exception:
            pass  # The original exception remains authoritative.
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('freeze');p.add_argument('--contract',type=Path,required=True)
    p=sub.add_parser('run');p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--approve-sha256',required=True);p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='freeze':
        publish_json(args.contract,freeze())
        print(json.dumps(dict(contract=str(args.contract),
                              sha256=file_sha(args.contract),gpu_work=0)))
    else:
        result=run(args.contract,args.approve_sha256,args.out)
        print(json.dumps(dict(gates=result['gates'],
                              work=result['total_work'],
                              production_admission=False)))


if __name__=='__main__':
    main()
