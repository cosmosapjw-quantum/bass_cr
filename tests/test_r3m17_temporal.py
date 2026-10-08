import copy
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.r3m17_temporal import (
    temporal_triplet, validate_result, validate_witness, historical_baseline,
    SOURCE, ROOT,
)


def test_unequal_actual_steps_recover_signed_second_order():
    dt = [0.04996782580968821, 0.02499784704477988, 0.01249892352238994]
    values = [0.008 + 0.04 * t**2 for t in dt]
    result = temporal_triplet(values, dt)
    assert result['observed_order'] == pytest.approx(2, abs=1e-10)
    assert result['extrapolated_value'] == pytest.approx(.008, abs=1e-14)
    assert result['conditional_fine_error_absolute'] == pytest.approx(values[2]-.008)
    assert result['certified_error_bound'] is None
    assert result['budget_closed'] is False


def test_pair_screen_alone_does_not_close_budget():
    result = temporal_triplet([.01, .010000001, .01], [.05, .025, .0125])
    assert result['fine_pair_screen'] == 'PASS_PAIR_ONLY'
    assert result['status'] == 'SIGN_CHANGE_NONASYMPTOTIC'
    assert result['budget_closed'] is False
    assert result['extrapolated_value'] is None


@pytest.mark.parametrize('values,status', [
    ([.01, .01, .01], 'UNRESOLVED_DIFFERENCES'),
    ([.01, .011, .013], 'NO_CONTRACTION'),
    ([0., 0., 0.], 'ABSOLUTE_TOLERANCE_REQUIRED'),
])
def test_failure_classification(values, status):
    result = temporal_triplet(values, [.05, .025, .0125])
    assert result['status'] == status
    assert not result['budget_closed']


def test_exact_zero_gets_only_explicit_absolute_pair_screen():
    result = temporal_triplet([2e-12, 1e-12, 0.], [.05, .025, .0125], absolute_tolerance=2e-12)
    assert result['fine_pair_relative'] is None
    assert result['fine_pair_screen'] == 'PASS_ABSOLUTE_PAIR_ONLY'
    assert not result['budget_closed']


@pytest.mark.parametrize('values,steps', [
    ([.01, np.nan, .01], [.05, .025, .0125]),
    ([.01, .01, .01], [.05, .025, .025]),
    ([.01, .01, .01], [.05, 0., .0125]),
])
def test_invalid_values_are_rejected(values, steps):
    with pytest.raises(ValueError):
        temporal_triplet(values, steps)


def data():
    cfg = json.loads((ROOT/'configs/r3m16/B1.json').read_text())
    result = json.loads((ROOT/'results/R3M16/collisions/B1_result.json').read_text())
    return cfg, result


def test_real_canonical_baseline_accepted():
    result = historical_baseline()
    assert result['B0']['P3'] == pytest.approx(.007911255992446844)
    assert result['B1']['P3'] == pytest.approx(.008063449050040342)
    assert result['initial_bytes_match']


@pytest.mark.parametrize('mutation', ['status', 'dt', 'grid', 'source', 'nan', 'gram', 'channels', 'nstep', 'norm'])
def test_mislabeled_or_corrupted_result_rejected(mutation):
    cfg, result = data()
    if mutation == 'status': result['status'] = 'checkpoint'
    elif mutation == 'dt': result['config']['dt'] = .5
    elif mutation == 'grid': result['config']['grid']['dx'] = .125
    elif mutation == 'source': result['config']['_r3m11_source_digest'] = 'bad'
    elif mutation == 'nan': result['analysis']['gram_audit']['P_span_by_nmax']['1'] = float('nan')
    elif mutation == 'gram': result['analysis']['gram_audit']['Gram_eigenvalues'][0] = 0
    elif mutation == 'channels': result['analysis']['gram_audit']['quantum_numbers'].pop()
    elif mutation == 'nstep': result['nstep'] += 1
    elif mutation == 'norm': result['analysis']['gram_audit']['wavefunction_norm'] = .001
    with pytest.raises(ValueError): validate_result(result, cfg)


def test_actual_dt_must_match_full_horizon():
    cfg, result = data()
    result['dt_actual'] = .025
    with pytest.raises(ValueError, match='actual'):
        validate_result(result, cfg)


def test_historical_witness_matches_config_and_initial_identity():
    cfg = json.loads((ROOT/'configs/r3m15/B.json').read_text())
    witness = json.loads((ROOT/'results/R3M15/B/collision/r3m14_initial_binding.json').read_text())
    expected = historical_baseline()['initial_state_sha256']
    validate_witness(witness, cfg, expected)
    witness = copy.deepcopy(witness)
    witness['prepared_array_digest'] = '0'*64
    with pytest.raises(ValueError): validate_witness(witness, cfg, expected)


def test_invalid_probability_or_tolerance_rejected():
    with pytest.raises(ValueError): temporal_triplet([-.1, .1, .1], [.05,.025,.0125])
    with pytest.raises(ValueError): temporal_triplet([.1,.1,.1], [.05,.025,.0125], relative_tolerance=float('nan'))
