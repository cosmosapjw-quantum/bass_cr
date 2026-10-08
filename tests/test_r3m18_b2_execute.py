import copy
import json
from pathlib import Path

import pytest

from scripts import r3m18_b2_execute as run
from scripts.r3m17_preflight import build_preflight


ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def frozen_inputs(tmp_path, monkeypatch):
    root = tmp_path / "B2"
    (root / "preparation").mkdir(parents=True)
    (root / "preparation/initial.npy").write_bytes(b"test")
    write(root / "preparation/receipt.json", {
        "status": "COMPLETE", "source_digest": run.FROZEN_SOURCE,
    })
    write(root / "resource.json", {"status": "PASS_RESOURCE_PREFLIGHT"})
    cfg_path = ROOT / "configs/r3m17/B2.json"
    cfg = json.loads(cfg_path.read_text())
    plan = build_preflight(cfg, config_path=cfg_path, job_root=root)
    monkeypatch.setattr(run, "sha", lambda path: run.CANONICAL_INITIAL_SHA256)
    monkeypatch.setattr(run, "source_digest", lambda: run.FROZEN_SOURCE)
    return root, cfg_path, plan


def test_plan_has_exactly_29_ordered_collision_generation_pairs(tmp_path, monkeypatch):
    root, cfg_path, plan = frozen_inputs(tmp_path, monkeypatch)
    cfg, commands = run.validate_inputs(root, cfg_path, plan)
    assert cfg["dt"] == .0125
    assert len(commands) == 58
    assert commands[0]["phase"] == "collision_chunk"
    assert commands[1]["phase"] == "checkpoint_snapshot"
    assert commands[-1]["expected_completed_steps"] == 3586


def test_changed_chunk_count_is_rejected(tmp_path, monkeypatch):
    root, cfg_path, plan = frozen_inputs(tmp_path, monkeypatch)
    plan = copy.deepcopy(plan)
    plan["numerical"]["chunk_count"] = 28
    with pytest.raises(ValueError, match="chunk"):
        run.validate_inputs(root, cfg_path, plan)


def test_completed_b2_is_never_rerun(tmp_path):
    root = tmp_path / "B2"
    root.mkdir()
    write(root / "COMPLETE.json", {"status": "COMPLETE"})
    with pytest.raises(FileExistsError, match="must not be rerun"):
        run.execute(root, tmp_path / "config.json", tmp_path / "plan.json")


def test_existing_generation_requires_full_inventory_match(tmp_path, monkeypatch):
    generation = tmp_path / "g000128"
    generation.mkdir()
    write(generation / run.guard.MANIFEST_NAME, {
        "schema": run.guard.SCHEMA,
        "status": "PUBLISHED_VERIFIED_LOCAL",
        "done": 128,
        "nstep": 3586,
        "files": {"state.npy": {"sha256": "manifest"}},
    })
    monkeypatch.setattr(run.guard, "validate_checkpoint", lambda *_args, **_kwargs: {
        "done": 128,
        "nstep": 3586,
        "files": {"state.npy": {"sha256": "actual"}},
    })
    with pytest.raises(ValueError, match="manifest mismatch"):
        run.validate_generation(generation, {}, 128)
