"""Opt-in CuPy adapter over frozen R3M22 CF4 and R3M23 Strang kernels.

Importing this module performs no CUDA operation. The historical source and
Hamiltonian are not patched. CPU coordinator tests are not GPU validation.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import sys
import time

import numpy as np

from .r3m24_metrics import repeat_kind, strang_gate, tightening_is_unchanged

MAX_BASIS=10
INNER=1e-14
TIGHT=1e-15
CAL_LIMIT=2.103970853068276e-14
GPU_RESERVE=2*1024**3
HOST_RESERVE=8*1024**3


def required_matvecs(windows: int) -> int:
    if type(windows) is not int or not 0 <= windows <= 2:
        raise ValueError('zero, one or two selected windows required')
    # Per window: calibration <=160; Strang/parity=34; n8/n16/tight <=1600;
    # REQUIRED independent n8/sub4 <=640. No optional gate prerequisite.
    return 0 if windows==0 else 3+windows*(160+34+1600+640)


def validate_work_capacity(plan: dict, windows: int) -> None:
    if required_matvecs(windows) > plan['limits']['kinetic_matvecs']:
        raise ValueError('resource cap cannot cover required independent repeats')


class Budget:
    def __init__(self, limits: dict, *, clock=time.monotonic):
        self.limits=dict(limits); self.clock=clock; self.started=clock()
        self.window_started=None; self.count=0
        if (type(limits['kinetic_matvecs']) is not int or limits['kinetic_matvecs'] < 1 or
                any(not math.isfinite(limits[k]) or limits[k] <= 0 for k in ('total_seconds','window_seconds'))):
            raise ValueError('positive finite resource limits required')
    def check(self):
        now=self.clock()
        if now-self.started >= self.limits['total_seconds']:
            raise TimeoutError('total wall cap reached')
        if self.window_started is not None and now-self.window_started >= self.limits['window_seconds']:
            raise TimeoutError('window wall cap reached')
    def tick(self):
        self.check()
        if self.count >= self.limits['kinetic_matvecs']:
            raise TimeoutError('kinetic matvec cap reached before work')
        self.count+=1
    def begin_window(self):
        self.check(); self.window_started=self.clock()
    def end_window(self):
        self.check(); elapsed=self.clock()-self.window_started
        self.window_started=None
        return elapsed
    def snapshot(self):
        return dict(kinetic_matvecs=self.count,fft_transforms=2*self.count,
                    wall_seconds=self.clock()-self.started,
                    fft_semantics='TWO_TRANSFORMS_PER_FOURIER_KINETIC_APPLICATION')


def work_trace(spec, source_key, n, substeps, infos, endpoint_sha, backend):
    actions=[a for step in infos for a in step['actions']]
    dims=[a['basis_dimension'] for a in actions]
    matvecs=sum(step['total_fft_matvec'] for step in infos)
    if len(dims)!=2*n*substeps or sum(dims)!=matvecs:
        raise ValueError('actual CF4 action accounting mismatch')
    return dict(input_sha256=spec['expected_state_npy_sha256'],source_key=source_key,
                t0=spec['actual_start_time_au'],horizon=spec['horizon_au'],n=n,
                action_substeps=substeps,backend=backend,dtype=np.dtype('complex128').str,
                basis_dimensions=dims,matvecs=matvecs,endpoint_sha256=endpoint_sha)


class GPUBackend:
    """Construct only after every current input and output reservation is checked."""
    def __init__(self, plan):
        from .r3m24_cross_window import validate_contract
        validate_contract(plan)
        self.plan=plan
        remaining=sum(s['label'] not in plan['reuse'] for s in plan['windows'])
        validate_work_capacity(plan,remaining)
        self.budget=Budget(plan['limits']); self.partial={}; self.minimum_free=None
        # Import numerical modules before CuPy allocation, then bind their paths.
        from cr_repro.r3m11 import ControlledTDLRunner
        from scripts.r3m22_inner_action import BoundedMatrixFreeFullH
        from scripts.r3m23_cross_window import _strang_ladder
        from scripts.r3m19_performance import hardware_inventory
        root=Path(plan['root']).resolve()
        for name, mod in tuple(sys.modules.items()):
            if name=='cr_repro' or name.startswith('cr_repro.') or name.startswith('scripts.r3m'):
                filename=getattr(mod,'__file__',None)
                if filename is None:
                    continue
                path=Path(filename).resolve()
                if not path.is_relative_to(root) or str(path.relative_to(root)) not in plan['sources']:
                    raise ValueError(f'unbound imported module: {name}: {path}')
        self.Runner=ControlledTDLRunner; self.FullH=BoundedMatrixFreeFullH
        self.strang=_strang_ladder; self.inventory=hardware_inventory
        import cupy as cp
        self.cp=cp

    def _resources(self):
        free=int(self.cp.cuda.runtime.memGetInfo()[0])
        self.minimum_free=free if self.minimum_free is None else min(self.minimum_free,free)
        host=self.inventory(include_gpu=False)['memory']['available_bytes']
        if free < GPU_RESERVE or host < HOST_RESERVE:
            raise MemoryError('GPU/host reserve lost')
        self.budget.check()

    def _upload(self, pinned):
        pinned.assert_current()
        state=self.cp.asarray(pinned.array)
        self.cp.cuda.get_current_stream().synchronize()
        pinned.assert_current()  # Catch a write/replacement during transfer.
        return state

    def probe(self, pinned):
        cp=self.cp; inventory=self.inventory(include_gpu=True)
        modeled=20*int(pinned.array.nbytes)
        if (inventory['gpu'].get('status')!='AVAILABLE' or
                inventory['gpu']['device_free_bytes'] < modeled+GPU_RESERVE or
                inventory['memory']['available_bytes'] < HOST_RESERVE):
            raise MemoryError('required basis/static/input reservation cannot fit')
        runner=self.Runner(self.plan['config']); mf=self.FullH(runner)
        mf.matvec_monitor=self.budget.tick
        del runner.kin,runner.mask,runner.cap_half
        cp.get_default_memory_pool().free_all_blocks()
        state=self._upload(pinned); held=[]; samples=[]
        try:
            for _ in range(MAX_BASIS+1+4): held.append(cp.empty_like(state))
            self._resources()
            for _ in range(3):
                cp.cuda.get_current_stream().synchronize(); mark=time.monotonic()
                acted=mf.generator_matvec(state,self.plan['probe']['actual_start_time_au'])
                cp.cuda.get_current_stream().synchronize()
                samples.append(time.monotonic()-mark); del acted
                self._resources()
            return dict(status='PASS',kinetic_matvecs=3,fft_transforms=6,
                        required_matvecs=required_matvecs(sum(s['label'] not in self.plan['reuse'] for s in self.plan['windows'])),
                        actual_inventory=inventory,matvec_seconds=samples,
                        minimum_gpu_free_bytes=self.minimum_free,
                        production_admission=False)
        finally:
            held.clear(); del state,mf,runner
            cp.get_default_memory_pool().free_all_blocks()

    def _cf4(self, mf, state, spec, n, substeps, budget):
        cp=self.cp; current=state.copy(); infos=[]
        count=self.budget.count; mark=time.monotonic()
        for j in range(n):
            current,info=mf.cf4_step(current,spec['actual_start_time_au']+j*spec['horizon_au']/n,
                spec['horizon_au']/n,physical_step_budget=budget/n,action_substeps=substeps,
                max_basis=MAX_BASIS,max_basis_bytes=(MAX_BASIS+1)*int(state.nbytes))
            infos.append(info)
        cp.cuda.get_current_stream().synchronize(); wall=time.monotonic()-mark
        mark=time.monotonic(); host=cp.asnumpy(current); transfer=time.monotonic()-mark
        del current; self._resources()
        if not np.isfinite(host).all(): raise FloatingPointError('nonfinite CF4 endpoint')
        sha=hashlib.sha256(memoryview(host).cast('B')).hexdigest()
        trace=work_trace(spec,self.plan['computation_key'],n,substeps,infos,sha,'cupy')
        if trace['matvecs']!=self.budget.count-count: raise ValueError('CF4 FFT accounting mismatch')
        actions=[a for step in infos for a in step['actions']]
        row=dict(sha256=sha,norm=float(np.vdot(host,host).real*mf.runner.dv),finite=True,
            fft_matvecs=trace['matvecs'],fft_transforms=2*trace['matvecs'],
            propagation_seconds=wall,host_transfer_seconds=transfer,actual_work=trace,
            actions=actions,requested_global_inner_budget=budget,
            accumulated_exact_arithmetic_inner_bound=sum(a['physical_upper_bound'] for a in actions),
            bound_semantics='EXACT_ARITHMETIC_NOT_FP_CERTIFICATE',
            observable_probabilities='NOT_RUN',phase_alignment=False)
        return host,row

    def window(self, spec, pinned):
        cp=self.cp; self.budget.begin_window(); count=self.budget.count
        runner=self.Runner(self.plan['config']); mf=self.FullH(runner)
        mf.matvec_monitor=self.budget.tick
        state=self._upload(pinned); self._resources()
        distance=lambda a,b: float(np.linalg.norm((a-b).ravel())*math.sqrt(runner.dv))
        strang,rows,parity=self.strang(runner,mf,state,spec['actual_start_time_au'],
                                     spec['horizon_au'],self.budget)
        self.partial=dict(label=spec['label'],strang_endpoints=rows,parity=parity)
        del runner.kin,runner.mask,runner.cap_half
        cp.get_default_memory_pool().free_all_blocks(); self._resources()
        cal_spec=dict(spec,horizon_au=spec['horizon_au']/16)
        cal2,cal2row=self._cf4(mf,state,cal_spec,1,2,INNER/16)
        cal4,cal4row=self._cf4(mf,state,cal_spec,1,4,INNER/16)
        cal_distance=distance(cal2,cal4)
        calibration=dict(sub2=cal2row,sub4=cal4row,substep_distance=cal_distance)
        if (repeat_kind(cal2row['actual_work'],cal4row['actual_work'])!='CHANGED_WORK' or
                cal_distance >= CAL_LIMIT):
            raise ValueError('required independent calibration unresolved')
        if tightening_is_unchanged(cal2row['actions'],TIGHT/16):
            calibration['tightening']=dict(status='SKIPPED_UNCHANGED_WORK',distance=None)
        else:
            tight,tr=self._cf4(mf,state,cal_spec,1,2,TIGHT/16)
            d=distance(cal2,tight); calibration['tightening']=dict(status='EXECUTED',distance=d,endpoint=tr)
            if d >= CAL_LIMIT: raise ValueError('tight calibration unresolved')
            del tight
        del cal2,cal4
        a8,r8=self._cf4(mf,state,spec,8,2,INNER)
        a16,r16=self._cf4(mf,state,spec,16,2,INNER)
        if tightening_is_unchanged(r16['actions'],TIGHT):
            tightening=dict(status='SKIPPED_UNCHANGED_WORK',distance=None,independent=False)
        else:
            tighter,rt=self._cf4(mf,state,spec,16,2,TIGHT)
            tightening=dict(status='EXECUTED',distance=distance(a16,tighter),endpoint=rt,
                            kind=repeat_kind(r16['actual_work'],rt['actual_work']))
            del tighter
        sub4,rs4=self._cf4(mf,state,spec,8,4,INNER)  # Required, never optional.
        independence=repeat_kind(r8['actual_work'],rs4['actual_work'])
        scale=min(distance(value,a16) for value in strang.values())
        outer=distance(a8,a16); inner=distance(a8,sub4)
        gate=strang_gate(scale,outer,inner,independence)
        if tightening['status']=='EXECUTED' and (tightening['distance'] >= gate['threshold'] or
                                                  tightening['kind']!='CHANGED_WORK'):
            gate['status']='UNRESOLVED_TIGHTENING'
        wall=self.budget.end_window()
        result=dict(label=spec['label'],checkpoint_sha256=spec['expected_state_npy_sha256'],
            status='STRANG_SCALE_REFERENCE_CONSISTENT' if gate['status']=='PASS_STRANG_SCALE_ONLY' else 'STRANG_SCALE_REFERENCE_UNRESOLVED',
            production_admission=False,gate=gate,calibration=calibration,tightening=tightening,
            full_h_endpoints=dict(CF4_8=r8,CF4_16=r16,CF4_8_sub4=rs4),
            strang_endpoints=rows,parity=parity,distances=dict(cf4_8_to_16=outer,
                substep_8_repeat=inner,strang_scale=scale),
            fft_matvecs=self.budget.count-count,fft_transforms=2*(self.budget.count-count),
            window_wall_seconds=wall,actual_start_time_au=spec['actual_start_time_au'],
            horizon_au=spec['horizon_au'],projection='NOT_RUN',
            input_consumption=pinned.receipt,minimum_gpu_free_bytes=self.minimum_free)
        self.partial={}; del state,mf,runner,a8,a16,sub4,strang
        cp.get_default_memory_pool().free_all_blocks()
        return result

    def snapshot(self):
        return dict(self.budget.snapshot(),backend='cupy',minimum_gpu_free_bytes=self.minimum_free,
                    partial_diagnostic=self.partial,orthogonalization_and_sync_profile='NOT_SEPARATELY_MEASURED')

    def close(self):
        self.cp.get_default_memory_pool().free_all_blocks()
