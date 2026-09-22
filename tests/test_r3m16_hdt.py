"""Fail-closed tests for the R3M16 target-only h-dt sidecar."""
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r3m16_hdt", ROOT / "scripts/r3m16_target_only_hdt.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def small_cfg():
    return {
        "energy_keV_per_u": 100.0, "b": 2.0, "backend": "numpy", "dt": 0.05,
        "grid": {"xlim": [-2, 2], "ylim": [-2, 2], "zlim": [-2, 4], "dx": 1.0},
        "z_start": -1.0, "z_stop": 1.0, "absorber_width": 1.0,
        "absorber_power": 0.125, "absorber_reference_dt": 0.05,
        "project_nmax": 1, "capture_plane": 1.0, "checkpoint_stride": 1,
        "initial_state": "imag_time", "imag_dt": 0.025, "imag_steps": 2,
    }


def test_target_only_step_never_calls_projectile_potential(monkeypatch):
    runner = MOD.ControlledTDLRunner(small_cfg())
    psi, _ = runner.relaxed_initial()
    monkeypatch.setattr(runner, "Vmid", lambda _t: (_ for _ in ()).throw(AssertionError("projectile")))
    out = MOD.target_only_step(runner, psi, 0.05)
    assert out.shape == psi.shape


def test_no_cap_step_is_norm_unitary_to_floating_tolerance():
    runner = MOD.ControlledTDLRunner(small_cfg())
    psi, _ = runner.relaxed_initial()
    out = MOD.target_only_step(runner, psi, 0.05)
    assert runner.norm(out) == pytest.approx(runner.norm(psi), abs=5e-13)


def test_same_grid_state_binding_requires_exact_saved_bytes(tmp_path):
    state = np.arange(24, dtype=np.float64).reshape(2, 3, 4).astype(np.complex128)
    first = tmp_path / "first.npy"; second = tmp_path / "second.npy"
    np.save(first, state, allow_pickle=False); np.save(second, state, allow_pickle=False)
    result = MOD.bind_same_grid_states(first, second, {"dx": 1.0}, {"dx": 1.0})
    assert result["byte_identical"] is True
    state.flat[0] += 1
    np.save(second, state, allow_pickle=False)
    with pytest.raises(ValueError, match="saved state bytes"):
        MOD.bind_same_grid_states(first, second, {"dx": 1.0}, {"dx": 1.0})


def test_cross_grid_state_pair_theorem_forbidden(tmp_path):
    state = np.ones((2, 2, 2), complex)
    a = tmp_path / "a.npy"; b = tmp_path / "b.npy"
    np.save(a, state); np.save(b, state)
    with pytest.raises(ValueError, match="cross-grid"):
        MOD.bind_same_grid_states(a, b, {"dx": 0.25}, {"dx": 0.20})


@pytest.mark.parametrize("requested", [0.05, 0.025, 0.0125])
def test_fixed_horizon_has_exact_common_physical_end_time(requested):
    nstep, actual = MOD.fixed_horizon_steps(1.0, requested)
    assert nstep * actual == pytest.approx(1.0, abs=1e-15)
    assert actual <= requested


def test_phase_aligned_distance_is_global_phase_invariant():
    a = np.array([1 + 2j, 3 - 1j], complex)
    for phase in [0.2, -1.7, 2.9]:
        assert MOD.ray_distance(a, np.exp(1j * phase) * a, 0.25) == pytest.approx(0, abs=2e-8)


def test_step_record_separates_requested_and_actual_dt():
    record = MOD.step_identity(0.05, 1.0 / 21, 21, 1.0)
    assert record["requested_dt"] == 0.05
    assert record["actual_dt"] == pytest.approx(1.0 / 21)
    assert record["requested_dt"] != record["actual_dt"]


def test_temporal_order_not_forced_for_nonmonotone_or_unresolved_data():
    assert MOD.empirical_order(1e-3, 2e-3)["status"] == "NONMONOTONE"
    assert MOD.empirical_order(0.0, 0.0)["status"] == "UNRESOLVED"
    assert MOD.empirical_order(4e-3, 1e-3)["order"] == pytest.approx(2.0)


def test_partial_diagnostic_is_create_only(tmp_path):
    path = tmp_path / "result.json"
    MOD.write_new(path, {"status": "PARTIAL"})
    with pytest.raises(FileExistsError):
        MOD.write_new(path, {"status": "COMPLETE"})
    assert json.loads(path.read_text())["status"] == "PARTIAL"


def test_historical_r3m15_files_remain_byte_identical():
    base = "65c456b61bab6a5665a0ab5d7ee63a00976ee03e"
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", base, "docs/r3m15", "results/R3M15"], cwd=ROOT, text=True).splitlines()
    for rel in paths:
        old = subprocess.check_output(["git", "show", f"{base}:{rel}"], cwd=ROOT)
        assert (ROOT / rel).read_bytes() == old, rel

