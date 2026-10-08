"""Independent moving-metric checks; no AOCC trajectories are propagated."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r3m17_aocc_metric", ROOT / "scripts/r3m17_aocc_metric.py"
)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def translated_gaussians(t, wrong_sign=False):
    """Exact overlap for normalized equal-exponent GTOs with projectile ETF.

    Target at zero, projectile at (b,0,v*t), phase exp(i*v*z-i*v*v*t/2).
    H=0 suffices to isolate the changing-basis identity.
    """
    alpha, velocity, impact = 0.7, 0.9, 1.2
    overlap = np.exp(
        -alpha * (impact**2 + (velocity * t)**2) / 2
        -velocity**2 / (8 * alpha)
    )
    metric = np.array([[1, overlap], [overlap, 1]], dtype=complex)
    connection = np.array(
        [[0, -alpha * velocity**2 * t * overlap], [0, -0.5j * velocity**2]],
        dtype=complex,
    )
    if wrong_sign:
        connection = -connection
    return metric, np.zeros_like(metric), connection


def test_exact_translated_gaussian_etf_identity_converges():
    result = audit.audit_time(
        translated_gaussians, 0.8, [0.008, 0.004, 0.002, 0.001],
        atol=1e-9, rtol=1e-6,
    )
    errors = [row["metric_identity"]["absolute"] for row in result["rows"]]
    assert all(a > b > 0 for a, b in zip(errors, errors[1:]))
    assert errors[0] / errors[1] == pytest.approx(4.0, rel=0.01)
    assert result["status"] == "PASS_LOCAL_METRIC_IDENTITY_ONLY"
    assert result["rows"][-1]["independent_raw_generator"]["passes"]


def test_actual_primitive_translation_and_etf_match_closed_gaussian_integral():
    # aocc imports the unchanged analytic integral module into sys.path.
    from gaussian_cartesian import Shell, moving_ket_overlap, overlap

    alpha, velocity, impact, time = 0.7, 0.9, 1.2, 0.8
    target = Shell(np.array([alpha]), (0, 0, 0), np.zeros(3), np.zeros(3))
    projectile = Shell(
        np.array([alpha]), (0, 0, 0), np.array([impact, 0.0, velocity * time]),
        np.array([0.0, 0.0, velocity]),
    )
    moving_velocity = np.array([0.0, 0.0, velocity])
    phase = np.exp(-0.5j * velocity**2 * time)
    primitive_overlap = overlap(target, projectile)[0, 0]
    actual_connection = phase * (
        moving_ket_overlap(target, projectile, moving_velocity)[0, 0]
        -0.5j * velocity**2 * primitive_overlap
    )
    metric, _, connection = translated_gaussians(time)
    np.testing.assert_allclose(phase * primitive_overlap, metric[0, 1], atol=1e-14, rtol=1e-14)
    np.testing.assert_allclose(actual_connection, connection[0, 1], atol=1e-14, rtol=1e-14)


def test_wrong_connection_is_not_hidden_by_constructed_antihermiticity():
    result = audit.audit_time(
        lambda t: translated_gaussians(t, wrong_sign=True), 0.8,
        [0.004, 0.002, 0.001], atol=1e-9, rtol=1e-6,
    )
    assert result["status"] == "METRIC_IDENTITY_UNRESOLVED_OR_FAILED"
    for row in result["rows"]:
        assert row["constructed_generator"]["absolute"] < 1e-14
        assert not row["metric_identity"]["passes"]
        assert not row["independent_raw_generator"]["passes"]


def test_stationary_orthonormal_family_handles_zero_scale_without_floor():
    zero = np.zeros((2, 2), dtype=complex)
    result = audit.audit_time(
        lambda t: (np.eye(2), np.diag([1, 2]), zero),
        0.0, [0.002, 0.001], atol=1e-12, rtol=1e-6,
    )
    assert result["rows"][0]["metric_identity"]["relative"] is None
    assert result["rows"][0]["metric_identity"]["absolute"] == 0
    assert result["status"] == "PASS_LOCAL_METRIC_IDENTITY_ONLY"


@pytest.mark.parametrize("steps", [[0.0, 0.001], [0.001, 0.002], [float("nan"), 0.001]])
def test_bad_derivative_ladder_rejected(steps):
    with pytest.raises(ValueError):
        audit.audit_time(translated_gaussians, 0.2, steps)


@pytest.mark.parametrize("kind", ["indefinite", "nonhermitian", "nonfinite"])
def test_bad_metric_is_rejected_without_eigenvalue_floor(kind):
    metric, hamiltonian, connection = translated_gaussians(0.2)
    if kind == "indefinite":
        metric[1, 1] = -1
    elif kind == "nonhermitian":
        metric[0, 1] += 0.1j
    else:
        metric[0, 0] = np.nan
    with pytest.raises((ValueError, np.linalg.LinAlgError)):
        audit.audit_time(lambda t: (metric, hamiltonian, connection), 0.2, [0.002, 0.001])


def test_actual_aocc_matrix_passes_independent_derivative_without_evolution(monkeypatch):
    cfg = json.loads((ROOT / "configs/aocc_smoke_100kevu_b2.json").read_text())
    cfg.update(ns=3, np=1)
    model = audit.OneElectronAOCC(cfg)
    monkeypatch.setattr(model, "run", lambda: pytest.fail("trajectory not authorized"))
    result = audit.audit_time(model.matrix, 0.75, [0.0004, 0.0002, 0.0001])
    assert result["status"] == "PASS_LOCAL_METRIC_IDENTITY_ONLY"


def test_create_only_json_preserves_first_result(tmp_path):
    path = tmp_path / "result.json"
    audit.write_new(path, {"first": True})
    first = path.read_bytes()
    with pytest.raises(FileExistsError):
        audit.write_new(path, {"replacement": True})
    assert path.read_bytes() == first


def test_runtime_or_config_failure_leaves_evidence(tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"energy_keV_per_u": 100, "b": 2}')
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="source"):
        audit.run_audit(config, output, expected_source="not-the-source")
    failure = json.loads((output / "failure.json").read_text())
    assert failure["status"] == "FAILED_RETAINED"
    assert failure["exception_type"] == "ValueError"


@pytest.mark.parametrize("change,options", [
    ({"ns": 33, "np": 0}, {}),
    ({"ns": 10, "np": 8}, {}),
    ({"ns": -1}, {}),
    ({"np": -1}, {}),
    ({"ns": 2.5}, {}),
    ({"np": True}, {}),
    ({}, {"times": [0.0] * 10}),
    ({}, {"times": [float("nan")]}),
    ({}, {"epsilons": [0.5**i for i in range(9)]}),
    ({}, {"epsilons": [0.001, 0.002]}),
])
def test_bounded_preflight_rejects_before_any_constructor_allocation(tmp_path, monkeypatch, change, options):
    cfg = json.loads((ROOT / "configs/aocc_smoke_100kevu_b2.json").read_text())
    cfg.update(change)
    config = tmp_path / "config.json"
    config.write_text(json.dumps(cfg))
    constructor_calls = []

    def forbidden_constructor(config):
        constructor_calls.append(config)
        pytest.fail("unbounded input reached AOCC constructor")

    monkeypatch.setattr(audit, "OneElectronAOCC", forbidden_constructor)
    with pytest.raises(ValueError):
        audit.run_audit(config, tmp_path / "result", **options)
    assert constructor_calls == []
    assert (tmp_path / "result/failure.json").exists()
