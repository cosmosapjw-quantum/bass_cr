"""CPU contract/gate tests; these are not a production-grid GPU oracle."""
import math
from contextlib import contextmanager
import json
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from scripts import r3m25_event_window as event
from scripts.r3m25_event_window import assess, event_geometry, required_worst_matvecs


def test_exact_event_geometry_and_warmup():
    value = event_geometry(1152, 3586, 0.01249892352238994,
                           -30.0, 60.0)
    assert value['start_step'] == 1194
    assert value['warmup_steps'] == 42
    assert value['t0'] < 0 < value['t1']
    assert value['steps'] == 4
    assert value['warmup_is_historical_checkpoint'] is False


def test_out_of_reach_event_rejected():
    with pytest.raises(ValueError):
        event_geometry(1200, 3586, 0.01249892352238994, -30.0, 60.0)


def test_fourth_order_self_scaled_reference_and_distinct_scales():
    result = assess(dict(d4_8=1.6e-6, d8_16=1e-7, d16_32=6.25e-9,
                         substep_repeat=1e-13, tight_repeat=1e-13,
                         strang_scale=2e-5, physical_norm=1.0,
                         substep_independence='CHANGED_WORK',
                         tightening_status='EXECUTED',
                         tightening_independence='CHANGED_WORK'))
    assert result['self_scaled_reference'] == 'PASS_LOCAL_SELF_SCALED'
    assert result['reference_for_strang'] == 'PASS_LOCAL_STRANG_SCALE'
    assert result['order_characterization'] == 'PASS_LOCAL_FOURTH_ORDER_COMPATIBLE'
    assert result['orders'] == pytest.approx([4., 4.])


def test_unchanged_tightening_cannot_be_called_independent():
    result = assess(dict(d4_8=1.6e-6, d8_16=1e-7, d16_32=6.25e-9,
                         substep_repeat=1e-9, tight_repeat=None,
                         strang_scale=2e-5, physical_norm=1.0,
                         substep_independence='CHANGED_WORK',
                         tightening_status='SKIPPED_UNCHANGED_WORK',
                         tightening_independence='UNCHANGED_WORK_NOT_INDEPENDENT'))
    assert result['self_scaled_reference'] == 'PASS_LOCAL_SELF_SCALED'
    assert result['tightening_is_independent'] is False


def test_fp_floor_is_unresolved_not_false_order_failure():
    result = assess(dict(d4_8=1e-12, d8_16=6.25e-14, d16_32=4e-15,
                         substep_repeat=1e-15, tight_repeat=None,
                         strang_scale=1e-5, physical_norm=1.0,
                         substep_independence='CHANGED_WORK',
                         tightening_status='SKIPPED_UNCHANGED_WORK',
                         tightening_independence='UNCHANGED_WORK_NOT_INDEPENDENT'))
    assert result['order_characterization'] == 'UNRESOLVED_FP_FLOOR'
    assert result['self_scaled_reference'] == 'PASS_LOCAL_SELF_SCALED'


def test_fp_floor_scales_repeat_by_100_but_not_machine_term():
    result = assess(dict(d4_8=2.56e-10, d8_16=1.6e-11, d16_32=1e-12,
                         substep_repeat=1e-15, tight_repeat=None,
                         strang_scale=1e-6, physical_norm=1.0,
                         substep_independence='CHANGED_WORK',
                         tightening_status='SKIPPED_UNCHANGED_WORK',
                         tightening_independence='UNCHANGED_WORK_NOT_INDEPENDENT'))
    assert result['order_characterization'] == 'PASS_LOCAL_FOURTH_ORDER_COMPATIBLE'
    assert result['order_signal_floor'] == 1e-13


def test_non_fourth_order_signal_is_local_no_go_only():
    result = assess(dict(d4_8=1e-3, d8_16=2.5e-4, d16_32=6.25e-5,
                         substep_repeat=1e-8, tight_repeat=1e-8,
                         strang_scale=1e-2, physical_norm=1.0,
                         substep_independence='CHANGED_WORK',
                         tightening_status='EXECUTED',
                         tightening_independence='CHANGED_WORK'))
    assert result['order_characterization'] == 'NO_GO_LOCAL_ORDER'
    assert result['production_admission'] is False


def test_missing_independent_substep_repeat_blocks_reference():
    result = assess(dict(d4_8=1e-3, d8_16=6.25e-5, d16_32=3.9e-6,
                         substep_repeat=1e-8, tight_repeat=None,
                         strang_scale=1e-2, physical_norm=1.0,
                         substep_independence='UNCHANGED_WORK_NOT_INDEPENDENT',
                         tightening_status='SKIPPED_UNCHANGED_WORK',
                         tightening_independence='UNCHANGED_WORK_NOT_INDEPENDENT'))
    assert result['self_scaled_reference'] == 'UNRESOLVED_INDEPENDENT_REPEAT'
    assert result['reference_for_strang'] == 'UNRESOLVED_INDEPENDENT_REPEAT'


def test_worst_work_fits_new_owner_authorized_cap_without_relaxing_gate():
    assert required_worst_matvecs(42, 10) == 3879
    assert required_worst_matvecs(42, 10) <= 4000
    assert math.isfinite(required_worst_matvecs(42, 10))


def test_host_reserve_loss_after_endpoint_transfer_is_rejected(monkeypatch):
    state = np.ones((2, 2), dtype=np.complex128)
    avail = [event.HOST_RESERVE + state.nbytes + 10,
             event.HOST_RESERVE + state.nbytes + 10,
             event.HOST_RESERVE - 1]
    transfers = []
    from scripts import r3m19_performance
    monkeypatch.setattr(r3m19_performance, 'hardware_inventory',
                        lambda **_: {'memory': {'available_bytes': avail.pop(0)}})
    cp = SimpleNamespace(cuda=SimpleNamespace(
        runtime=SimpleNamespace(memGetInfo=lambda: (event.GPU_RESERVE + 1, 0)),
        get_current_stream=lambda: SimpleNamespace(synchronize=lambda: None)),
        asnumpy=lambda value: transfers.append(True) or np.asarray(value))
    mf = SimpleNamespace(cf4_step=lambda value, *_args, **_kwargs:
                         (value, {'actions': []}))
    budget = SimpleNamespace(count=0, check=lambda: None)
    spec = dict(actual_start_time_au=0., horizon_au=.1)
    with pytest.raises(MemoryError, match='reserve lost'):
        event._cf4(mf, cp, state, spec, 1, 2, 1e-14,
                   budget, 'key', {'gpu': [], 'host': []})
    assert transfers == [True]


def test_first_failure_keeps_original_exception_and_consumed_work(tmp_path, monkeypatch):
    monkeypatch.setattr(event, 'read_json', lambda *_args:
                        {'generation': {}, 'computation_key': 'k'*64,
                         'implementation_commit': 'h'*40})
    monkeypatch.setattr(event, 'validate', lambda *_args: None)
    @contextmanager
    def intake(_spec):
        yield SimpleNamespace(assert_current=lambda: None)
    monkeypatch.setattr(event, 'bind_generation', intake)
    def failing_gpu(_plan, _out, _pinned, progress):
        progress.update(stage='EVENT_CF4_N32',
                        budget=SimpleNamespace(snapshot=lambda:
                            {'kinetic_matvecs': 2761, 'wall_seconds': 123.}),
                        minimum={'gpu': [event.GPU_RESERVE+1],
                                 'host': [event.HOST_RESERVE+1]})
        raise MemoryError('injected reserve loss')
    monkeypatch.setattr(event, '_gpu', failing_gpu)
    out = tmp_path/'fresh'
    with pytest.raises(MemoryError, match='injected reserve loss'):
        event.run(tmp_path/'contract', 'a'*64, out)
    failure = json.loads((out/'FIRST_FAILURE.json').read_text())
    assert failure['stage'] == 'EVENT_CF4_N32'
    assert failure['work_at_failure']['kinetic_matvecs'] == 2761
    assert failure['resource_limited'] is True
    assert not (out/'COMPLETED.json').exists()


def test_probe_releases_split_step_buffers_before_held_basis_allocation(monkeypatch):
    runner = SimpleNamespace(kin=object(), mask=object(), cap_half=object())
    budget = SimpleNamespace(count=0, check=lambda: None)
    def act(value, _time):
        budget.count += 1
        return value
    mf = SimpleNamespace(generator_matvec=act)
    state = np.ones((2, 2), dtype=np.complex128)
    allocated = []
    def empty_like(value):
        assert value is state
        assert not any(hasattr(runner, name) for name in ('kin','mask','cap_half'))
        allocated.append(True)
        return np.empty_like(value)
    pool = SimpleNamespace(free_all_blocks=lambda: None)
    cp = SimpleNamespace(empty_like=empty_like,
        get_default_memory_pool=lambda: pool,
        cuda=SimpleNamespace(get_current_stream=lambda:
            SimpleNamespace(synchronize=lambda: None)))
    monkeypatch.setattr(event, '_resources', lambda *_args, **_kwargs: None)
    samples = event._probe_with_released_split_buffers(
        cp, runner, mf, state, budget, {'gpu': [], 'host': []}, 0.)
    assert len(samples) == 3
    assert budget.count == 3
    assert len(allocated) == event.MAX_BASIS + 1 + 4


def test_strang_helper_guards_each_of_six_host_transfers(monkeypatch):
    from scripts import r3m20_short_window, r3m23_cross_window
    class Buffered:
        def __init__(self, runner): self.runner = runner
        def step(self, state, time): return self.runner.step(state, time)
    monkeypatch.setattr(r3m20_short_window, 'ProductionBufferedStep', Buffered)
    monkeypatch.setattr(r3m23_cross_window, 'ProductionBufferedStep', Buffered)
    fake_cp = SimpleNamespace(exp=np.exp, fft=np.fft, asnumpy=np.asarray,
        cuda=SimpleNamespace(get_current_stream=lambda:
            SimpleNamespace(synchronize=lambda: None)))
    monkeypatch.setitem(sys.modules, 'cupy', fake_cp)
    state = np.ones((2,2,2), dtype=np.complex128)
    runner = SimpleNamespace(k2=np.zeros_like(state), dv=1.,
        Vmid=lambda _time: np.zeros_like(state),
        step=lambda value, _time: value.copy())
    mf = SimpleNamespace(W=np.zeros_like(state))
    class Counter:
        count=0
        def tick(self): self.count += 1
        def check(self): pass
    budget = Counter()
    checks=[]
    monkeypatch.setattr(event, '_resources', lambda _cp, _budget, _minimum,
                        upcoming_host_bytes=0: checks.append(upcoming_host_bytes))
    endpoints, rows, parity = event._guarded_strang_ladder(
        runner,mf,state,0.,.1,budget,{'gpu':[],'host':[]})
    assert set(endpoints) == {'S4','S8','S16'}
    assert set(rows) == {'S4','S8','S16','B4'}
    assert parity['one_step']['status'] == 'PASS_SAME_DISCRETIZATION_PARITY'
    assert parity['four_step']['status'] == 'PASS_SAME_DISCRETIZATION_PARITY'
    assert budget.count == 34
    assert checks == [state.nbytes,0]*6
    frozen_budget=Counter()
    frozen_endpoints,frozen_rows,frozen_parity = r3m23_cross_window._strang_ladder(
        runner,mf,state,0.,.1,frozen_budget)
    assert frozen_budget.count == budget.count
    assert all(np.array_equal(endpoints[key],frozen_endpoints[key]) for key in endpoints)
    assert all(rows[key]['sha256']==frozen_rows[key]['sha256'] for key in rows)
    assert parity['one_step']==frozen_parity['one_step']
    assert parity['four_step']==frozen_parity['four_step']


def test_probe_objects_release_before_fresh_warmup_runner(tmp_path, monkeypatch):
    from cr_repro import r3m11
    from scripts import r3m19_performance, r3m22_inner_action
    released=[]; created=[]; uploads=[]
    class Runner:
        def __init__(self, _config):
            if created:
                assert released == [0]
            created.append(len(created))
            self.index=created[-1]
            self.dt_actual=.0125
        def __del__(self): released.append(self.index)
    class FullH:
        def __init__(self, runner): self.runner=runner
    monkeypatch.setattr(r3m11, 'ControlledTDLRunner', Runner)
    monkeypatch.setattr(r3m22_inner_action, 'BoundedMatrixFreeFullH', FullH)
    state=np.ones((2,2),dtype=np.complex128)
    monkeypatch.setattr(r3m19_performance, 'hardware_inventory', lambda **_:
        {'gpu': {'status':'AVAILABLE','device_free_bytes':
                 20*state.nbytes+event.GPU_RESERVE+1},
         'memory': {'available_bytes':event.HOST_RESERVE+state.nbytes+1}})
    def upload(value):
        uploads.append(True)
        if len(uploads)==2: raise MemoryError('injected second upload stop')
        return value
    cp=SimpleNamespace(asarray=upload,
        cuda=SimpleNamespace(get_current_stream=lambda:
            SimpleNamespace(synchronize=lambda: None)),
        get_default_memory_pool=lambda:
            SimpleNamespace(free_all_blocks=lambda: None))
    monkeypatch.setitem(sys.modules,'cupy',cp)
    def probe(_cp,_runner,_mf,_state,budget,minimum,_time):
        budget.count=3
        minimum['gpu'].append(event.GPU_RESERVE+1)
        minimum['host'].append(event.HOST_RESERVE+1)
        return [0.,0.,0.]
    monkeypatch.setattr(event,'_probe_with_released_split_buffers',probe)
    pinned=SimpleNamespace(array=state,assert_current=lambda:None)
    plan={'config':{},'generation':{'actual_dt_au':.0125,
          'actual_start_time_au':0.},'limits':event.LIMITS,
          'required_worst_matvecs':3879}
    with pytest.raises(MemoryError,match='second upload stop'):
        event._gpu(plan,tmp_path,pinned,{})
    assert len(created)==2
    assert uploads==[True,True]
    assert (tmp_path/'PREFLIGHT.json').exists()
    assert not (tmp_path/'WARMUP.json').exists()
