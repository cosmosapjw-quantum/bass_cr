"""R3M17 independent temporal oracle and cancellation-resistant state metrics."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r3m17_reference", ROOT / "scripts/r3m17_reference.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_resolves_1e_minus_10_distance_legacy_formula_rounds_to_zero():
    a = np.array([1, 0], complex)
    b = np.array([1, 1e-10], complex)
    legacy = np.sqrt(max(0, 2 - 2 * abs(np.vdot(a, b)) / (np.linalg.norm(a)*np.linalg.norm(b))))
    assert legacy == 0
    assert MOD.stable_phase_metrics(a, b, 1)["ray_distance"] == pytest.approx(1e-10, rel=1e-14)


def test_global_phase_and_scale_do_not_hide_probability_norm_loss():
    a = np.array([1+2j, 3-1j], complex)
    b = 0.3*np.exp(1.7j)*a
    metrics = MOD.stable_phase_metrics(a, b, 0.2)
    assert metrics["ray_distance"] < 6e-16
    assert metrics["norm_second"] == pytest.approx(0.09*metrics["norm_first"])
    assert metrics["phase_aligned_state_distance"] == pytest.approx(0.7*np.sqrt(metrics["norm_first"]))


@pytest.mark.parametrize("a,b,dv", [
    ([1, 0], [1], 1), ([0, 0], [1, 0], 1), ([np.nan, 1], [1, 0], 1),
    ([1, 0], [np.inf, 0], 1), ([1, 0], [1, 0], 0),
    ([1, 0], [1, 0], -1), ([1, 0], [1, 0], np.nan),
])
def test_bad_metric_inputs_are_rejected(a, b, dv):
    with pytest.raises(ValueError):
        MOD.stable_phase_metrics(a, b, dv)


def test_orthogonal_rays_have_sqrt_two_distance():
    metrics = MOD.stable_phase_metrics([1, 0], [0, 2j], 0.3)
    assert metrics["ray_distance"] == pytest.approx(np.sqrt(2))
    assert metrics["fidelity"] == 0


def test_expectation_and_variance_are_normalization_invariant():
    H = np.diag([1., 3.])
    for scale in [0.01, 1., 4.]:
        m = MOD.normalized_hamiltonian_moments(scale*np.ones(2, complex), H, 0.125)
        assert m["energy_Eh"] == pytest.approx(2)
        assert m["variance_Eh2"] == pytest.approx(1)
        assert m["stationary_residual_Eh"] == pytest.approx(1)


def test_nonhermitian_reference_is_rejected():
    with pytest.raises(ValueError, match="Hermitian"):
        MOD.normalized_hamiltonian_moments(np.ones(2), np.array([[1, 1j], [1j, 2]]), 1)


def test_explicit_fourier_H_action_matches_fft_on_nonsquare_grid():
    shape = (3, 4, 2); h = 0.7
    rng = np.random.default_rng(43)
    V = rng.normal(size=shape)
    psi = rng.normal(size=shape)+1j*rng.normal(size=shape)
    H = MOD.dense_fourier_hamiltonian(shape, h, V)
    k = [2*np.pi*np.fft.fftfreq(n, d=h) for n in shape]
    k2 = k[0][:,None,None]**2+k[1][None,:,None]**2+k[2][None,None,:]**2
    fft_result = np.fft.ifftn(0.5*k2*np.fft.fftn(psi))+V*psi
    assert np.max(abs(H@psi.ravel()-fft_result.ravel())) < 6e-14


@pytest.mark.parametrize("shape", [(9, 8, 8), (0, 4, 4), (2.5, 4, 4), (True, 4, 4)])
def test_dense_budget_or_invalid_dimensions_refuse_before_allocation(shape):
    with pytest.raises((ValueError, MemoryError)):
        MOD.dense_fourier_hamiltonian(shape, 0.2, None)


def test_absolute_point_limit_cannot_be_overridden():
    with pytest.raises((ValueError, MemoryError)):
        MOD.dense_fourier_hamiltonian((9, 8, 8), 0.2, None, max_points=10000)


def test_exact_discrete_eigenstate_has_no_ray_drift_but_splitter_does():
    report = MOD.run_reference_experiment(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32))
    coulomb = report["cases"]["cell_centered_coulomb"]
    assert coulomb["initial"]["stationary_residual_Eh"] < 1e-13
    assert coulomb["exact_eigenstate_ray_drift"] < 1e-13
    assert coulomb["runs"][0]["ray_error_vs_exact_same_H"] > 1e-7
    assert max(abs(row["norm_drift"]) for row in coulomb["runs"]) < 5e-13
    assert report["production_admission"] is False
    assert report["continuum_spatial_validation"] is False


def test_smooth_fixed_horizon_ladder_has_true_global_second_order():
    report = MOD.run_reference_experiment(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32))
    smooth = report["cases"]["smooth_periodic"]
    assert all(1.95 < p < 2.05 for p in smooth["empirical_orders_vs_exact"])
    assert all(row["physical_end_time"] == 0.4 for row in smooth["runs"])
    assert smooth["oracle_method"] == "EXPLICIT_DFT_FULL_H_DENSE_EIGH"


def test_target_split_no_projectile_or_cap(monkeypatch):
    runner = MOD.make_tiny_runner((4,4,4), 0.7)
    monkeypatch.setattr(runner, "Vmid", lambda t: (_ for _ in ()).throw(AssertionError("projectile called")))
    psi = np.ones((4,4,4), complex)
    result = MOD.target_only_step(runner, psi, 0.01)
    assert runner.norm(result) == pytest.approx(runner.norm(psi), abs=2e-13)


def test_write_new_preserves_existing_bytes(tmp_path):
    path = tmp_path / "report.json"
    MOD.write_new(path, {"original": 1})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        MOD.write_new(path, {"replacement": 2})
    assert path.read_bytes() == original


def test_cli_create_only_and_bounded(tmp_path):
    output = tmp_path / "oracle.json"
    argv = [sys.executable, str(ROOT/"scripts/r3m17_reference.py"), "--out", str(output), "--shape", "2", "2", "2"]
    result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text())
    assert report["numerical_source_digest"] == MOD.FROZEN_SOURCE
    assert report["runtime"]["numpy"] == np.__version__
    original = output.read_bytes()
    assert subprocess.run(argv, cwd=ROOT, text=True, capture_output=True).returncode != 0
    assert output.read_bytes() == original


def test_moving_two_center_oracle_resolves_temporal_error_and_norm():
    report = MOD.run_moving_reference(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32))
    assert report["oracle_method"] == "EXPLICIT_DFT_KINETIC_PLUS_MOVING_COULOMB_DOP853"
    assert report["source_under_test"] == "ControlledTDLRunner.step"
    assert report["oracle_refinement_resolved"] is True
    assert report["oracle_repeat_ray_distance"] < 1e-3*report["runs"][-1]["ray_error_vs_reference"]
    assert max(abs(row["norm_drift"]) for row in report["runs"]) < 1e-12
    assert all(1.8 < p < 2.2 for p in report["empirical_orders_vs_reference"])
    assert report["minimum_projectile_transverse_distance_a0"] > 0
    assert report["CAP_included"] is False
    assert report["production_collision"] is False


def test_moving_oracle_has_matching_physical_end_times_and_initial_bytes():
    report = MOD.run_moving_reference(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32))
    initial_hashes = {row["same_saved_initial_array_sha256"] for row in report["runs"]}
    assert len(initial_hashes) == 1
    for row in report["runs"]:
        assert row["physical_start_time"] == report["physical_start_time"]
        assert row["physical_end_time"] == report["physical_end_time"]
        assert row["actual_dt"]*row["nstep"] == pytest.approx(0.4, abs=1e-15)
