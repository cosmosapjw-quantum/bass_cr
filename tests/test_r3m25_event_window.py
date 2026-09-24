"""CPU contract/gate tests; these are not a production-grid GPU oracle."""
import math
from contextlib import contextmanager
import json
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
