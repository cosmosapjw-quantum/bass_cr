"""Tiny CPU restart fault injections; no production scientific computation."""
import errno
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest

from cr_repro import tdl
from cr_repro.r3m11 import ControlledTDLRunner, file_sha
from cr_repro.util import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load_script("r3m17_checkpoint_guard")


def config():
    return dict(energy_keV_per_u=100., b=2., backend="numpy",
        grid=dict(xlim=[-2, 2], ylim=[-2, 2], zlim=[-2, 4], dx=1.),
        dt=.01, z_start=-1., z_stop=1., initial_state="analytic",
        absorber_width=1., absorber_power=.25, absorber_reference_dt=.05,
        checkpoint_stride=1, project_nmax=1, capture_plane=1.)


@pytest.fixture
def checkpoint(tmp_path):
    path = tmp_path / "run"
    ControlledTDLRunner(config()).run(path, max_steps=1)
    return path


def snapshot(checkpoint, out):
    return guard.snapshot_generation(checkpoint, out, config(), require_witness=False)


def test_previous_generation_survives_next_state_replace_and_restores(checkpoint, tmp_path, monkeypatch):
    generation = tmp_path / "gen0001"
    snapshot(checkpoint, generation)
    state_sha = file_sha(checkpoint / "state.npy")
    assert os.stat(checkpoint / "state.npy").st_ino == os.stat(generation / "state.npy").st_ino
    old_json = (checkpoint / "state.json").read_bytes()
    original = tdl.atomic_json

    def fail_after_state_replacement(path, value):
        if Path(path).name == "state.json":
            raise KeyboardInterrupt("after state.npy replace, before state.json")
        return original(path, value)

    with monkeypatch.context() as patch:
        patch.setattr(tdl, "atomic_json", fail_after_state_replacement)
        with pytest.raises(KeyboardInterrupt):
            ControlledTDLRunner(config()).run(checkpoint, max_steps=1)
    assert file_sha(checkpoint / "state.npy") != state_sha
    assert (checkpoint / "state.json").read_bytes() == old_json
    with pytest.raises(ValueError, match="checkpoint hash mismatch"):
        ControlledTDLRunner(config()).run(checkpoint, max_steps=1)
    assert file_sha(generation / "state.npy") == state_sha
    restored = tmp_path / "restored"
    receipt = guard.restore_generation(generation, restored, config(), require_witness=False)
    assert receipt["status"] == "RESTORED_VERIFIED_LOCAL"
    assert file_sha(restored / "state.npy") == state_sha
    assert (restored / "state.json").read_bytes() == old_json
    result = ControlledTDLRunner(config()).run(restored, max_steps=1)
    assert result["done"] == 2
    reference = tmp_path / "reference"
    ControlledTDLRunner(config()).run(reference, max_steps=2)
    np.testing.assert_array_equal(np.load(restored / "state.npy"), np.load(reference / "state.npy"))
    assert file_sha(generation / "state.npy") == state_sha


@pytest.mark.parametrize("name", ["state.npy", "state.json", "r3m11_checkpoint_seal.json"])
def test_corrupted_checkpoint_not_published(checkpoint, tmp_path, name):
    with (checkpoint / name).open("ab") as stream:
        stream.write(b"corruption")
    out = tmp_path / "generation"
    with pytest.raises(ValueError):
        snapshot(checkpoint, out)
    assert not (out / guard.MANIFEST_NAME).exists()


def test_rehashed_invalid_done_is_not_trusted(checkpoint, tmp_path):
    meta = json.loads((checkpoint / "state.json").read_text())
    meta["done"] = meta["nstep"] + 1
    atomic_json(checkpoint / "state.json", meta)
    seal = json.loads((checkpoint / "r3m11_checkpoint_seal.json").read_text())
    seal["files"]["state.json"] = file_sha(checkpoint / "state.json")
    atomic_json(checkpoint / "r3m11_checkpoint_seal.json", seal)
    with pytest.raises(ValueError, match="done"):
        snapshot(checkpoint, tmp_path / "generation")


def test_config_identity_must_match(checkpoint, tmp_path):
    cfg = config()
    cfg["dt"] /= 2
    with pytest.raises(ValueError, match="config"):
        guard.snapshot_generation(checkpoint, tmp_path / "generation", cfg, require_witness=False)


def test_snapshot_and_restore_never_overwrite(checkpoint, tmp_path):
    generation = tmp_path / "generation"
    snapshot(checkpoint, generation)
    manifest = (generation / guard.MANIFEST_NAME).read_bytes()
    with pytest.raises(FileExistsError):
        snapshot(checkpoint, generation)
    with pytest.raises(FileExistsError):
        guard.restore_generation(generation, checkpoint, config(), require_witness=False)
    assert (generation / guard.MANIFEST_NAME).read_bytes() == manifest


@pytest.mark.parametrize("symlink_kind", ["state", "source_directory", "output_parent"])
def test_symlinks_rejected(checkpoint, tmp_path, symlink_kind):
    out = tmp_path / "generation"
    source = checkpoint
    if symlink_kind == "state":
        state = checkpoint / "state.npy"
        state.rename(checkpoint / "actual.npy")
        state.symlink_to(checkpoint / "actual.npy")
    elif symlink_kind == "source_directory":
        source = tmp_path / "alias"
        source.symlink_to(checkpoint, target_is_directory=True)
    else:
        parent = tmp_path / "alias"
        parent.symlink_to(tmp_path, target_is_directory=True)
        out = parent / "generation"
    with pytest.raises(ValueError, match="symlink"):
        snapshot(source, out)


def test_cross_filesystem_does_not_copy_state(checkpoint, tmp_path, monkeypatch):
    def fail_link(*args, **kwargs):
        raise OSError(errno.EXDEV, "Invalid cross-device link")
    monkeypatch.setattr(guard.os, "link", fail_link)
    out = tmp_path / "generation"
    with pytest.raises(OSError, match="same filesystem"):
        snapshot(checkpoint, out)
    assert not (out / "state.npy").exists()
    assert not (out / guard.MANIFEST_NAME).exists()
    assert out.is_dir()  # Interrupted evidence is never cleaned up silently.


def test_interrupted_snapshot_retained_but_cannot_restore(checkpoint, tmp_path, monkeypatch):
    out = tmp_path / "generation"
    def fail_copy(*args, **kwargs):
        raise KeyboardInterrupt("injected metadata-copy interruption")
    monkeypatch.setattr(guard, "_copy_exclusive", fail_copy)
    with pytest.raises(KeyboardInterrupt):
        snapshot(checkpoint, out)
    assert (out / "state.npy").is_file()
    assert not (out / guard.MANIFEST_NAME).exists()
    with pytest.raises(ValueError, match="unpublished"):
        guard.restore_generation(out, tmp_path / "restored", config(), require_witness=False)


def test_snapshot_corruption_rejected_at_restore(checkpoint, tmp_path):
    generation = tmp_path / "generation"
    snapshot(checkpoint, generation)
    # Atomic replace does not damage current run inode.
    changed = generation / "changed.npy"
    changed.write_bytes(b"bad state")
    changed.replace(generation / "state.npy")
    with pytest.raises(ValueError, match="hash mismatch"):
        guard.restore_generation(generation, tmp_path / "restored", config(), require_witness=False)
    assert not (tmp_path / "restored").exists()


def test_production_default_requires_v2_witness(checkpoint, tmp_path):
    with pytest.raises(ValueError, match="witness"):
        guard.snapshot_generation(checkpoint, tmp_path / "generation", config())


def make_bound_checkpoint(tmp_path):
    prep = load_script("r3m13_initial_state_pair")
    witness = load_script("r3m14_collision_initial_witness")
    cfg = config()
    cfg.update(initial_state="imag_time", imag_dt=.025, imag_steps=2)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(cfg))
    prepared = tmp_path / "prepared"
    prep.prepare(cfg, prepared)
    run = tmp_path / "run"
    witness.run_bound(config_path, prepared, run, 1)
    return run, cfg, config_path, prepared, witness


def test_v2_bound_checkpoint_restores_and_resumes(tmp_path):
    run, cfg, config_path, prepared, witness = make_bound_checkpoint(tmp_path)
    generation = tmp_path / "generation"
    manifest = guard.snapshot_generation(run, generation, cfg)
    assert "r3m14_initial_binding.json" in manifest["files"]
    assert "r3m14_witness_run_receipt.json" in manifest["files"]
    restored = tmp_path / "restored"
    guard.restore_generation(generation, restored, cfg)
    for name in ("r3m14_initial_binding.json", "r3m14_witness_run_receipt.json"):
        assert (restored / name).read_bytes() == (run / name).read_bytes()
    result = witness.run_bound(config_path, prepared, restored, 1)
    assert result["done"] == 2
    receipt = json.loads((run / "r3m14_witness_run_receipt.json").read_text())
    receipt["done"] += 1
    atomic_json(run / "r3m14_witness_run_receipt.json", receipt)
    with pytest.raises(ValueError, match="receipt"):
        guard.snapshot_generation(run, tmp_path / "invalid_generation", cfg)


@pytest.mark.parametrize("field", ["prepared_array_digest", "internal_array_digest",
                                    "prepared_state_file_sha256", "prepared_receipt_sha256"])
@pytest.mark.parametrize("replacement", [None, "", "A" * 64, "0" * 63])
def test_missing_or_invalid_witness_digest_rejected(tmp_path, field, replacement):
    run, cfg, *_ = make_bound_checkpoint(tmp_path)
    witness = json.loads((run / "r3m14_initial_binding.json").read_text())
    # In particular both missing array digests previously compared as None==None.
    if field in ("prepared_array_digest", "internal_array_digest"):
        witness.pop("prepared_array_digest")
        witness.pop("internal_array_digest")
    if replacement is None:
        witness.pop(field, None)
    else:
        witness[field] = replacement
    atomic_json(run / "r3m14_initial_binding.json", witness)
    with pytest.raises(ValueError, match="witness.*digest"):
        guard.snapshot_generation(run, tmp_path / "generation", cfg)
    assert not (tmp_path / "generation" / guard.MANIFEST_NAME).exists()


@pytest.mark.parametrize("runtime", [None, {}, "numpy", {"python": "3", "numpy": "2", "backend": "cupy"},
                                    {"python": None, "numpy": "2", "backend": "numpy"}])
def test_missing_or_invalid_runtime_environment_rejected(tmp_path, runtime):
    run, cfg, *_ = make_bound_checkpoint(tmp_path)
    for name in ("r3m14_initial_binding.json", "r3m14_witness_run_receipt.json"):
        evidence = json.loads((run / name).read_text())
        evidence["runtime_environment"] = runtime
        atomic_json(run / name, evidence)
    with pytest.raises(ValueError, match="witness.*environment"):
        guard.snapshot_generation(run, tmp_path / "generation", cfg)
    assert not (tmp_path / "generation" / guard.MANIFEST_NAME).exists()
