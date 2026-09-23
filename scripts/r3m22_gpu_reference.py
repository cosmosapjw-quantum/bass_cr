"""One guarded GPU job for incoming-B2 contractive-action CF4 reference.

No production collision, projection, checkpoint write, or automatic retry.
Preflight and one-step calibration are counted in the same 4000-matvec cap.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m19_performance import hardware_inventory
from scripts.r3m20_matrix_free import FROZEN_SOURCE
from scripts.r3m20_short_window import preflight as allocation_preflight
from scripts.r3m22_inner_action import BoundedMatrixFreeFullH

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/R3M22'
SELECTION=ROOT/'results/R3M20_N1/windows/SELECTION.json'
PRIOR=ROOT/'results/R3M21/CF4_OUTER_LADDER.json'
CONFIG=ROOT/'configs/r3m17/B2.json'
MAX_FFT=4000
MAX_GPU_WALL=7200
MAX_WINDOW_WALL=1800
GPU_RESERVE=2*1024**3
HOST_RESERVE=8*1024**3
MAX_BASIS=10
GLOBAL_INNER_BUDGET=1e-14
TIGHT_INNER_BUDGET=1e-15
METHODS=(("CF4_4",4,2,GLOBAL_INNER_BUDGET),
         ("CF4_8",8,2,GLOBAL_INNER_BUDGET),
         ("CF4_16",16,2,GLOBAL_INNER_BUDGET),
         ("CF4_32",32,2,GLOBAL_INNER_BUDGET),
         ("CF4_16_tight",16,2,TIGHT_INNER_BUDGET),
         ("CF4_8_sub4",8,4,GLOBAL_INNER_BUDGET))


def _sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for b in iter(lambda:stream.read(4*1024**2),b''):
            h.update(b)
    return h.hexdigest()


def _write_new(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')


class Budget:
    def __init__(self,started,preflight_count):
        self.started=started
        self.window_started=time.perf_counter()
        self.count=preflight_count

    def tick(self):
        now=time.perf_counter()
        if (self.count>=MAX_FFT or now-self.started>=MAX_GPU_WALL
                or now-self.window_started>=MAX_WINDOW_WALL):
            raise TimeoutError('R3M22 FFT/GPU/window ceiling reached before next matvec')
        self.count+=1


def _distance(a,b,dv):
    return float(np.linalg.norm((a-b).ravel())*math.sqrt(dv))


def input_guard():
    if source_digest()!=FROZEN_SOURCE:
        raise ValueError('frozen numerical source digest changed')
    selection=json.loads(SELECTION.read_text())
    prior=json.loads(PRIOR.read_text())
    row=selection['windows'][0]
    state_path=Path(row['generation_directory'])/'state.npy'
    if (row['label']!='incoming' or row['done']!=384
            or selection['B2_config_sha256']!=_sha(CONFIG)
            or row['expected_state_npy_sha256']!=_sha(state_path)
            or prior['status']!='REFERENCE_UNRESOLVED_ONE_PERCENT_GATE'
            or prior['checkpoint_done']!=384):
        raise ValueError('incoming B2 or R3M21 predecessor identity mismatch')
    r3m20=json.loads((ROOT/'results/R3M20_N1/windows/FIRST_WINDOW.json').read_text())
    signal=float(r3m20['cf4_outer_dt_to_dt2_raw_distance'])
    if not math.isfinite(signal) or signal<=0:
        raise ValueError('pre-existing independent gate signal invalid')
    return dict(schema='BASS_CR_R3M22_INPUT_GUARD_V1',status='PASS',
                state_npy_sha256=row['expected_state_npy_sha256'],
                state_npy_bytes=state_path.stat().st_size,
                source_digest=FROZEN_SOURCE,config_sha256=_sha(CONFIG),
                selection_sha256=_sha(SELECTION),r3m21_result_sha256=_sha(PRIOR),
                prior_signal=signal,one_percent_threshold=.01*signal,
                remote_restore='NOT_TESTED'),selection


def _record_endpoint(host,infos,wall,transfer,dv):
    return dict(sha256=hashlib.sha256(host.tobytes()).hexdigest(),
                norm=float(np.vdot(host,host).real*dv),
                fft_matvecs=sum(i['total_fft_matvec'] for i in infos),
                max_basis_used=max(a['basis_dimension'] for i in infos for a in i['actions']),
                sum_contractively_bounded_inner_error=sum(i['accumulated_exact_arithmetic_upper_bound'] for i in infos),
                propagation_seconds=wall,host_transfer_seconds=transfer,
                finite=bool(np.isfinite(host).all()))


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    budget=None
    stage='INPUT_GUARD'
    try:
        guard,selection=input_guard()
        _write_new(OUT/'INPUT_GUARD.json',guard)
        stage='PREFLIGHT'
        probe=allocation_preflight()
        prior=json.loads(PRIOR.read_text())
        # Every action uses at most 10 matvecs: 16 calibration actions plus
        # 16+32+64+128+64+64 full-window actions = 3840, plus 3 probe matvecs.
        max_plan_fft=3843
        prior_seconds_per_fft=prior['gpu_wall_seconds']/prior['gpu_fft_matvec_total_including_preflight']
        forecast=max_plan_fft*prior_seconds_per_fft
        probe.update(schema='BASS_CR_R3M22_GPU_PREFLIGHT_V1',
                     prior_measured_seconds_per_fft=prior_seconds_per_fft,
                     max_plan_fft_matvecs=max_plan_fft,
                     forecast_seconds=forecast,forecast_is_measurement=False,
                     source_sha256=_sha(Path(__file__)),
                     action_source_sha256=_sha(ROOT/'scripts/r3m22_inner_action.py'),
                     input_guard_sha256=_sha(OUT/'INPUT_GUARD.json'))
        if (probe['status']!='PASS' or max_plan_fft>MAX_FFT
                or forecast>.8*MAX_WINDOW_WALL
                or probe['gpu_free_after_matvec_probe']<GPU_RESERVE
                or probe['actual_inventory']['memory']['available_bytes']<HOST_RESERVE):
            probe['status']='COST_OR_RESOURCE_BLOCKED'
        _write_new(OUT/'PREFLIGHT.json',probe)
        if probe['status']!='PASS':
            raise RuntimeError('resource/work preflight did not pass')
        stage='GPU_INPUT_UPLOAD'
        import cupy as cp
        row=selection['windows'][0]
        state_map=np.load(Path(row['generation_directory'])/'state.npy',mmap_mode='r',allow_pickle=False)
        mark=time.perf_counter()
        runner=ControlledTDLRunner(json.loads(CONFIG.read_text()))
        state=cp.asarray(state_map)
        cp.cuda.get_current_stream().synchronize()
        upload_seconds=time.perf_counter()-mark
        mf=BoundedMatrixFreeFullH(runner)
        del runner.kin,runner.mask,runner.cap_half
        cp.get_default_memory_pool().free_all_blocks()
        free=int(cp.cuda.runtime.memGetInfo()[0])
        if (free<GPU_RESERVE or hardware_inventory(include_gpu=False)['memory']['available_bytes']<HOST_RESERVE):
            raise MemoryError('live resource reserve lost after input upload')
        budget=Budget(started,probe['preflight_fft_matvecs'])
        mf.matvec_monitor=budget.tick
        min_free=free
        t0=row['actual_start_time_au']; horizon=row['horizon_au']
        threshold=guard['one_percent_threshold']
        basis_bytes=(MAX_BASIS+1)*int(state.nbytes)

        stage='ONE_STEP_INNER_CALIBRATION'
        calibration={}
        calibration_states={}
        for label,substeps,global_budget in (("sub2",2,GLOBAL_INNER_BUDGET),
                                             ("sub4",4,GLOBAL_INNER_BUDGET),
                                             ("sub2_tight",2,TIGHT_INNER_BUDGET)):
            mark=time.perf_counter()
            current,info=mf.cf4_step(state.copy(),t0,horizon/32,
                                      physical_step_budget=global_budget/32,
                                      action_substeps=substeps,max_basis=MAX_BASIS,
                                      max_basis_bytes=basis_bytes)
            cp.cuda.get_current_stream().synchronize()
            wall=time.perf_counter()-mark
            transfer_start=time.perf_counter()
            host=cp.asnumpy(current)
            transfer=time.perf_counter()-transfer_start
            if not np.isfinite(host).all():
                raise FloatingPointError('nonfinite one-step calibration')
            calibration_states[label]=host
            calibration[label]=_record_endpoint(host,[info],wall,transfer,runner.dv)
            min_free=min(min_free,int(cp.cuda.runtime.memGetInfo()[0]))
            if min_free<GPU_RESERVE:
                raise MemoryError('GPU reserve lost during inner calibration')
            del current
        calibration_distances=dict(
            substep_repeat=_distance(calibration_states['sub2'],calibration_states['sub4'],runner.dv),
            tighter_inner_repeat=_distance(calibration_states['sub2'],calibration_states['sub2_tight'],runner.dv))
        del calibration_states
        calibration_pass=all(value<threshold for value in calibration_distances.values())
        if not calibration_pass:
            result=dict(schema='BASS_CR_R3M22_GPU_RESULT_V1',status='INNER_CALIBRATION_UNRESOLVED',
                        calibration=calibration,calibration_distances=calibration_distances,
                        one_percent_threshold=threshold,full_window_methods='NOT_RUN',
                        gpu_fft_matvec_total_including_preflight=budget.count,
                        gpu_wall_seconds=time.perf_counter()-started,
                        window_wall_seconds=time.perf_counter()-budget.window_started,
                        minimum_gpu_free_bytes=min_free,input_upload_seconds=upload_seconds,
                        full_collision=False,production_admission=False,remote_restore='NOT_TESTED')
            _write_new(OUT/'GPU_RESULT.json',result)
            return result

        stage='CF4_OUTER_LADDER'
        endpoints={};records={}
        for label,n,substeps,global_budget in METHODS:
            current=state.copy();infos=[]
            mark=time.perf_counter()
            for j in range(n):
                current,info=mf.cf4_step(current,t0+j*horizon/n,horizon/n,
                                          physical_step_budget=global_budget/n,
                                          action_substeps=substeps,max_basis=MAX_BASIS,
                                          max_basis_bytes=basis_bytes)
                infos.append(info)
            cp.cuda.get_current_stream().synchronize()
            wall=time.perf_counter()-mark
            transfer_start=time.perf_counter()
            host=cp.asnumpy(current)
            transfer=time.perf_counter()-transfer_start
            if not np.isfinite(host).all():
                raise FloatingPointError(f'nonfinite endpoint {label}')
            endpoints[label]=host
            records[label]=dict(steps=n,action_substeps=substeps,
                                global_inner_budget=global_budget,
                                **_record_endpoint(host,infos,wall,transfer,runner.dv))
            min_free=min(min_free,int(cp.cuda.runtime.memGetInfo()[0]))
            if min_free<GPU_RESERVE:
                raise MemoryError('GPU reserve lost during CF4 ladder')
            del current

        stage='HOST_REFERENCE_GATE'
        d=dict(outer_4_to_8=_distance(endpoints['CF4_4'],endpoints['CF4_8'],runner.dv),
               outer_8_to_16=_distance(endpoints['CF4_8'],endpoints['CF4_16'],runner.dv),
               outer_16_to_32=_distance(endpoints['CF4_16'],endpoints['CF4_32'],runner.dv),
               inner_16_repeat=_distance(endpoints['CF4_16'],endpoints['CF4_16_tight'],runner.dv),
               substep_8_repeat=_distance(endpoints['CF4_8'],endpoints['CF4_8_sub4'],runner.dv))
        ratio=d['outer_8_to_16']/d['outer_16_to_32'] if d['outer_16_to_32']>0 else None
        reference_resolved=bool(all(d[k]<threshold for k in
                                    ('outer_16_to_32','inner_16_repeat','substep_8_repeat'))
                                and d['outer_4_to_8']>d['outer_8_to_16']>d['outer_16_to_32']
                                and ratio is not None and ratio>=4)
        result=dict(schema='BASS_CR_R3M22_GPU_RESULT_V1',
                    status='REFERENCE_RESOLVED_AT_PRIOR_4_TO_8_SCALE' if reference_resolved
                           else 'REFERENCE_UNRESOLVED_AT_PRIOR_4_TO_8_SCALE',
                    input_guard_sha256=_sha(OUT/'INPUT_GUARD.json'),
                    preflight_sha256=_sha(OUT/'PREFLIGHT.json'),
                    checkpoint_done=384,horizon_au=horizon,
                    reference_semantics='INCOMING_FOUR_B2_DT_SAME_DISCRETE_H_ONLY',
                    calibration=calibration,calibration_distances=calibration_distances,
                    endpoints=records,distances=d,outer_refinement_ratio_8_to_16_over_16_to_32=ratio,
                    one_percent_threshold=threshold,
                    gpu_fft_matvec_total_including_preflight=budget.count,
                    gpu_wall_seconds=time.perf_counter()-started,
                    window_wall_seconds=time.perf_counter()-budget.window_started,
                    minimum_gpu_free_bytes=min_free,input_upload_seconds=upload_seconds,
                    analytic_bound_semantics='EXACT_ARITHMETIC_NONEXPANSIVE_NOT_FLOATING_POINT_CERTIFICATE',
                    full_collision=False,preparation_run=False,projection='NOT_RUN',
                    checkpoint_write='NOT_RUN',production_admission=False,
                    remote_restore='NOT_TESTED')
        _write_new(OUT/'GPU_RESULT.json',result)
        return result
    except BaseException as exc:
        _write_new(OUT/'FIRST_FAILURE.json',dict(schema='BASS_CR_R3M22_FIRST_FAILURE_V1',
                   stage=stage,type=type(exc).__name__,message=str(exc),
                   elapsed_seconds=time.perf_counter()-started,
                   fft_matvec_count=None if budget is None else budget.count,
                   automatic_retry=False,original_checkpoint_modified=False,
                   full_collision=False))
        raise


def main():
    result=run()
    print(json.dumps({'status':result['status'],
                      'fft_matvecs':result['gpu_fft_matvec_total_including_preflight'],
                      'wall_seconds':result['gpu_wall_seconds']}))


if __name__=='__main__':
    main()
