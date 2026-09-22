"""Frozen A1/B1 collision contract and witness integration tests."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r3m16_coord", ROOT / "scripts/r3m16_coordinator.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


@pytest.mark.parametrize("job,dx", [("A1", 0.25), ("B1", 0.20)])
def test_only_two_frozen_collision_configs(job, dx):
    cfg = json.loads((ROOT / "configs/r3m16" / f"{job}.json").read_text())
    MOD.validate_config(job, cfg)
    assert cfg["grid"]["dx"] == dx
    assert cfg["dt"] == 0.025
    assert cfg["imag_dt"] * cfg["imag_steps"] == 30.0


@pytest.mark.parametrize("job", ["A0", "B0", "C1", "A2", "B2"])
def test_no_unregistered_collision(job):
    with pytest.raises(ValueError):
        MOD.validate_config(job, {})


@pytest.mark.parametrize("key,value", [("b", 3), ("energy_keV_per_u", 50), ("dt", 0.0125), ("backend", "auto"), ("imag_steps", 9600), ("absorber_width", 5)])
def test_no_silent_collision_drift(key, value):
    cfg = json.loads((ROOT / "configs/r3m16/A1.json").read_text())
    cfg[key] = value
    with pytest.raises(ValueError, match="frozen A1/B1 config"):
        MOD.validate_config("A1", cfg)


def test_new_collision_invokes_v2_witness():
    argv = MOD.collision_argv(Path("cfg.json"), Path("prep"), Path("out"), 128)
    assert "scripts/r3m14_collision_initial_witness.py" in argv
    assert argv[argv.index("--max-steps") + 1] == "128"


def test_fresh_preparation_config_must_match_collision_config():
    cfg = json.loads((ROOT / "configs/r3m16/A1.json").read_text())
    assert MOD.preparation_config(cfg) == cfg


def test_failed_or_partial_job_is_never_overwritten(tmp_path):
    (tmp_path / "FAILURE.json").write_text("{}")
    with pytest.raises(FileExistsError, match="preserve existing"):
        MOD.assert_fresh_job(tmp_path)

