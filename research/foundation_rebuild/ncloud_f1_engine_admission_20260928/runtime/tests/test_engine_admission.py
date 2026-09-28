from types import SimpleNamespace

import numpy as np
import pytest

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import admit_query, metric_sentinels

KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')


def policy():
    return {'runtime_reference_resolutions': [{'order': q, 'subdivisions': 1} for q in (32, 40, 48)],
            'parity_policy': {'numpy_allclose': {'rtol': 1e-11, 'atol': 1e-12},
                'raw_cross_keys': list(KEYS), 'compare_selected_full_arrays': ['S', 'H', 'D'],
                'operator_hermiticity_relative_max': 1e-11, 'metric_min_ratio': 1e-8,
                'runtime_raw_cross_convergence_max': 1e-9,
                'metric_connection_sentinels_z_a0': [-12, -6, 0, 6, 12],
                'epsilon_z_a0': 1e-4, 'metric_derivative_relative_max': 1e-6}}


def evidence():
    arrays = {'selected__S': np.eye(2), 'selected__H': np.eye(2), 'selected__D': np.zeros((2, 2))}
    for q in (32, 40):
        for key in KEYS:
            arrays[f'q{q}_h1__{key}'] = np.ones((1, 1))
    rec = {'query_id': 'exact-query', 'context_id': 'context', 'time_hex': '0x0.0p+0',
           'qualification': {'selected_resolution': {'order': 40, 'subdivisions': 1}},
           'attempts': [{'resolution': {'order': q, 'subdivisions': 1}} for q in (32, 40)]}
    return SimpleNamespace(record=rec, arrays=arrays, representative={'query_id': 'exact-query',
            'time_hex': '0x0.0p+0', 'selected_resolution': {'order': 40, 'subdivisions': 1}})


def evaluator(t, q, h):
    return ({key: np.ones((1, 1)) for key in KEYS},
            {'S': np.eye(2), 'H': np.eye(2), 'D': np.zeros((2, 2))})


def test_exact_selected_and_all_historical_raw_arrays_pass():
    calls = []
    def counted(t, q, h):
        calls.append((q, h))
        return evaluator(t, q, h)
    result = admit_query(evidence(), counted, policy())
    assert result['status'] == 'PASS' and result['selected_resolution'] == {'order': 40, 'subdivisions': 1}
    assert len(result['raw_comparisons']) == 12
    assert len(result['full_comparisons']) == 3
    assert calls == [(32, 1), (40, 1), (48, 1)]


def test_q_h_policy_selection_drift_is_distinct():
    def drifting(t, q, h):
        raw, full = evaluator(t, q, h)
        value = 1.0 if q == 32 else 1.1
        return {k: a * value for k, a in raw.items()}, full
    with pytest.raises(Exception, match='POLICY_SELECTION_DRIFT'):
        admit_query(evidence(), drifting, policy())


def test_attempted_raw_cross_parity_failure():
    def wrong_raw(t, q, h):
        raw, full = evaluator(t, q, h)
        if q in (32, 40):
            raw['D_pt'] = raw['D_pt'] + 0.01
        return raw, full
    with pytest.raises(Exception, match='F1_RAW_PARITY_FAILED'):
        admit_query(evidence(), wrong_raw, policy())


def test_selected_full_operator_parity_failure():
    def wrong_full(t, q, h):
        raw, full = evaluator(t, q, h)
        full['H'] = full['H'] + np.eye(2) * 0.01
        return raw, full
    with pytest.raises(Exception, match='F1_FULL_OPERATOR_PARITY_FAILED'):
        admit_query(evidence(), wrong_full, policy())


def test_nonhermitian_or_bad_metric_screen_rejected():
    def bad_metric(t, q, h):
        raw, full = evaluator(t, q, h)
        full['S'] = np.diag([-1., 1.])
        return raw, full
    with pytest.raises(Exception, match='F1_FULL_OPERATOR_PARITY_FAILED'):
        admit_query(evidence(), bad_metric, policy())


class SyntheticProvider:
    identity = 'synthetic-exact'

    def __init__(self, d=0.01):
        self.d = d

    def at(self, t):
        return SimpleNamespace(S=np.eye(2) * (1 + 0.02 * t), D=np.eye(2) * self.d,
                               qualification={'selected_resolution': {'order': 40, 'subdivisions': 1}})


def test_metric_connection_sentinels_record_exact_time_and_resolution():
    rows = metric_sentinels(SyntheticProvider(), 1.0, policy())
    assert [r['z_a0'] for r in rows] == [-12, -6, 0, 6, 12]
    assert rows[2]['time_hex'] == '0x0.0p+0'
    assert all(r['relative_residual'] <= 1e-6 for r in rows)


def test_metric_connection_failure_is_distinct():
    with pytest.raises(Exception, match='F1_METRIC_CONNECTION_FAILED'):
        metric_sentinels(SyntheticProvider(d=0.02), 1.0, policy())


def test_admission_orchestrates_representative_and_five_sentinels():
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import run_admission
    class E:
        representatives = {'query_count': 1, 'queries': [evidence().representative]}
        def query(self, rep):
            return evidence()
    parity, metric = run_admission(E(), evaluator, 1.0, policy(), 'new-engine')
    assert len(parity) == 1 and parity[0]['status'] == 'PASS'
    assert len(metric) == 5
