"""Small independent algebra checks; these never validate a production trajectory."""
from pathlib import Path
import importlib.util
import json

import numpy as np
import pytest
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r3m26_foundation', ROOT / 'scripts/r3m26_foundation.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_closed_triangular_exponential_against_independent_pade_expm():
    for t in (0., .31, 1.3):
        np.testing.assert_allclose(MOD.triangular_exponential(t), expm(MOD.A * t), atol=3e-15, rtol=3e-15)


@pytest.mark.parametrize('with_initial_error', [False, True])
def test_duhamel_identity_includes_forcing_sign_and_initial_error(with_initial_error):
    out = MOD.forced_system_check(with_initial_error=with_initial_error)
    assert out['hermitian_part_largest_eigenvalue'] < -.4
    assert out['nonnormal_commutator_norm'] > .1
    assert out['duhamel_error_norm'] < 2e-14
    assert out['terminal_state_error_norm'] <= out['contraction_expression_delta']
    assert out['wrong_residual_sign_error_norm'] > 1e-3
    assert out['certified_global_bound'] is False
    assert (out['initial_error_norm'] > 0) == with_initial_error


def test_adjoint_goal_identity_checks_linear_quadratic_and_initial_terms():
    out = MOD.forced_system_check(with_initial_error=True)
    goal = out['goal']
    assert goal['identity_absolute_residual'] < 2e-14
    assert goal['quadratic_terminal_term'] > 1e-7
    assert abs(goal['initial_term']) > 1e-5
    assert abs(goal['direct_delta_q'] - goal['linear_terms']) == pytest.approx(goal['quadratic_terminal_term'], abs=2e-14)
    assert goal['scalar_observable_bound_holds']


def test_weighted_gram_matches_whitened_qr_and_preserves_span():
    out = MOD.projector_check()
    assert out['weighted_gram_minus_qr_probability'] < 2e-14
    assert out['weighted_projector_minus_qr_norm'] < 2e-14
    assert out['basis_change_probability_difference'] < 2e-14
    assert out['channel_phase_probability_difference'] < 2e-14
    assert out['projector_idempotence_norm'] < 2e-14
    assert out['whitened_hermiticity_norm'] < 2e-14
    assert out['weighted_operator_norm'] == pytest.approx(1., abs=2e-14)
    assert 0 < out['gram_probability'] < out['state_weighted_norm_squared']


def test_normalized_nonorthogonal_columns_double_count_raw_overlaps():
    bad = MOD.projector_check()['nonorthogonal_counterexample']
    assert bad['each_basis_vector_norm_squared'] == pytest.approx([1., 1.])
    assert bad['raw_overlap_sum'] == pytest.approx(1.5)
    assert bad['correct_projected_probability'] == pytest.approx(1.)
    assert bad['raw_overlap_sum'] > bad['state_norm_squared']
    assert bad['changed_basis_raw_overlap_sum'] != pytest.approx(bad['raw_overlap_sum'])
    assert bad['changed_basis_correct_probability'] == pytest.approx(1.)


def test_stable_eigenvalues_and_euclidean_norm_are_insufficient_shortcuts():
    out = MOD.assumption_counterexamples()
    stable = out['stable_nondissipative']
    assert stable['eigenvalue_real_parts'] == [-1., -1.]
    assert stable['hermitian_part_largest_eigenvalue'] == pytest.approx(1.)
    assert stable['propagator_norm_at_t_point3'] > 1.3
    metric = out['weighted_projector']
    assert metric['weighted_operator_norm'] == pytest.approx(1., abs=2e-14)
    assert metric['euclidean_operator_norm'] == pytest.approx(np.sqrt(1.36), abs=2e-14)
    assert metric['euclidean_nonhermiticity_norm'] > .8


def test_run_claim_ceiling_and_create_only_output(tmp_path):
    out = MOD.run_foundation_checks()
    assert out['algebra_checks_passed'] is True
    assert out['production_admitted'] is False
    assert out['production_global_error_evaluated'] is False
    assert out['evidence_scope'] == 'SYNTHETIC_SMALL_MATRIX_ALGEBRA_ONLY'
    path = tmp_path / 'result.json'
    MOD.write_new(path, out)
    before = path.read_bytes()
    assert json.loads(before)['algebra_checks_passed']
    with pytest.raises(FileExistsError):
        MOD.write_new(path, {'replacement': True})
    assert path.read_bytes() == before


def test_invalid_quadrature_and_nonfinite_time_fail_explicitly():
    with pytest.raises(ValueError):
        MOD.forced_system_check(quadrature_nodes=0)
    with pytest.raises(ValueError):
        MOD.triangular_exponential(float('nan'))
