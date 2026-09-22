import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from cr_repro.r3m11 import ControlledTDLRunner, file_sha, source_digest
from cr_repro.util import atomic_json, atomic_npy

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r3m13 = load_module("r3m13_fixture", ROOT / "scripts/r3m13_initial_state_pair.py")
witness = load_module("r3m14_witness", ROOT / "scripts/r3m14_collision_initial_witness.py")


def cfg():
    return dict(
        energy_keV_per_u=100.0,
        b=2.0,
        backend="numpy",
        dt=0.05,
        grid=dict(xlim=[-2, 2], ylim=[-2, 2], zlim=[-2, 4], dx=1.0),
        z_start=-1.0,
        z_stop=1.0,
        absorber_width=1.0,
        absorber_power=0.125,
        absorber_reference_dt=0.05,
        project_nmax=1,
        capture_plane=1.0,
        checkpoint_stride=1,
        initial_state="imag_time",
        imag_dt=0.025,
        imag_steps=2,
    )


def pin_current_source():
    """Fixture helper may be reconstructed; production branch should equal the pin."""
    actual = source_digest()
    witness.EXPECTED_SOURCE_DIGEST = actual
    r3m13.EXPECTED_SOURCE_DIGEST = actual
    return actual


def prepare(root, config):
    return r3m13.prepare(config, root)


def test_witness_does_not_change_one_step(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    plain = tmp_path / "plain"
    bound = tmp_path / "bound"
    ControlledTDLRunner(config).run(plain, max_steps=1)
    witness.run_bound(
        config_path, prepared, bound, 1, expected_source_digest=actual
    )

    np.testing.assert_array_equal(
        np.load(plain / "state.npy"), np.load(bound / "state.npy")
    )
    binding = json.loads((bound / "r3m14_initial_binding.json").read_text())
    assert binding["schema"] == "BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V2"
    assert binding["status"] == "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED"
    assert binding["numerical_state_substituted"] is False
    assert binding["numerical_state_renormalized"] is False
    assert binding["environment_match"] is True
    assert binding["norm_match"] is True
    assert json.loads((bound / "state.json").read_text())["done"] == 1


def test_resume_requires_same_prepared_bytes(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    out = tmp_path / "run"

    witness.run_bound(config_path, prepared, out, 1, expected_source_digest=actual)
    state = np.load(prepared / "initial.npy").copy()
    state.flat[0] += 1e-12
    atomic_npy(prepared / "initial.npy", state)

    with pytest.raises(ValueError, match="hash mismatch"):
        witness.run_bound(config_path, prepared, out, 1, expected_source_digest=actual)


def test_mismatched_rehashed_prepared_initial_fails_before_propagation(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    # Keep the fixture preparation self-consistent at the file-hash level while
    # changing its numerical array. The R3M14 identity witness must catch this.
    state = np.roll(np.load(prepared / "initial.npy").copy(), 1, axis=0)
    atomic_npy(prepared / "initial.npy", state)
    receipt = json.loads((prepared / "receipt.json").read_text())
    receipt["initial_state_sha256"] = file_sha(prepared / "initial.npy")
    atomic_json(prepared / "receipt.json", receipt)

    out = tmp_path / "run"
    with pytest.raises(ValueError, match="not byte-identical"):
        witness.run_bound(config_path, prepared, out, 1, expected_source_digest=actual)
    assert not (out / "state.json").exists()
    binding = json.loads((out / "r3m14_initial_binding.json").read_text())
    assert binding["status"] == "FAIL_INTERNAL_INITIAL_NOT_IDENTICAL"


def test_canonical_config_identity_is_fail_closed(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)

    altered = dict(config)
    # bool is numerically equal to 1 in Python, so this catches accidental use
    # of ordinary dict equality as an identity proof.
    altered["capture_plane"] = True
    config_path = tmp_path / "altered.json"
    config_path.write_text(json.dumps(altered))

    with pytest.raises(ValueError, match="canonical config"):
        witness.run_bound(
            config_path, prepared, tmp_path / "run", 1, expected_source_digest=actual
        )


def test_helper_script_hash_is_bound(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)
    receipt = json.loads((prepared / "receipt.json").read_text())
    receipt["script_sha256"] = "0" * 64
    atomic_json(prepared / "receipt.json", receipt)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    with pytest.raises(ValueError, match="helper script hash"):
        witness.run_bound(
            config_path, prepared, tmp_path / "run", 1, expected_source_digest=actual
        )


def test_preparation_environment_mismatch_fails_before_propagation(tmp_path):
    config = cfg()
    actual = pin_current_source()
    prepared = tmp_path / "prep"
    prepare(prepared, config)
    receipt = json.loads((prepared / "receipt.json").read_text())
    receipt["environment"]["numpy"] = "deliberately-different"
    atomic_json(prepared / "receipt.json", receipt)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

    out = tmp_path / "run"
    with pytest.raises(ValueError, match="environment-bound"):
        witness.run_bound(config_path, prepared, out, 1, expected_source_digest=actual)
    assert not (out / "state.json").exists()
    binding = json.loads((out / "r3m14_initial_binding.json").read_text())
    assert binding["environment_match"] is False
