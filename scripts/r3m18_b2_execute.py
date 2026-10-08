#!/usr/bin/env python3
"""Execute the frozen R3M17 B2 command plan with immutable generations."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cr_repro.r3m11 import source_digest
from scripts import r3m16_coordinator as supervisor
from scripts import r3m17_checkpoint_guard as guard
from scripts.r3m17_preflight import (
    FROZEN_SOURCE, SCIENCE_PYTHON, build_preflight, validate_b2_config,
)

# Kept local to this outer coordinator so it cannot be mistaken for numerical
# source authority. The same value is pinned by r3m17_temporal.py.
CANONICAL_INITIAL_SHA256 = (
    "ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa"
)


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_new(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def validate_inputs(root: Path, config: Path, plan: dict) -> tuple[dict, list[dict]]:
    cfg = read_json(config)
    # R3M19 repair: equality between two supplied inputs does not establish the
    # frozen B2 family, nor authorize the executable argv carried in the plan.
    # Rebuild only metadata here; never launch an interpreter or allocate a grid.
    validate_b2_config(cfg)
    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source digest mismatch")
    if plan.get("job") != "B2" or plan.get("status") != "PLAN_ONLY_NOT_EXECUTED":
        raise ValueError("invalid B2 preflight plan")
    if plan.get("config") != cfg or plan["numerical"].get("chunk_count") != 29:
        raise ValueError("preflight/config/chunk identity mismatch")
    if plan["numerical"].get("nstep") != 3586:
        raise ValueError("unexpected B2 step count")
    expected = build_preflight(cfg, config_path=config, job_root=root,
                               scientific_python=SCIENCE_PYTHON)
    for key in (
        'schema', 'frozen_authority_commit', 'numerical_source_digest',
        'instrumentation_sha256', 'reference_B1_config_sha256',
        'config_path', 'config_file_sha256', 'job_root',
        'command_working_directory', 'command_environment_required',
        'prerequisites', 'checkpoint_retention', 'command_plan',
    ):
        # JSON comparison also distinguishes booleans from numeric lookalikes.
        if json.dumps(plan.get(key), sort_keys=True, allow_nan=False) != json.dumps(
                expected[key], sort_keys=True, allow_nan=False):
            raise ValueError(f'canonical B2 execution plan mismatch: {key}')
    if plan.get('runtime', {}).get('required_scientific_interpreter') != SCIENCE_PYTHON:
        raise ValueError('canonical B2 execution plan interpreter mismatch')
    if sha(root / "preparation/initial.npy") != CANONICAL_INITIAL_SHA256:
        raise ValueError("B2 preparation is not byte-identical to canonical B")
    receipt = read_json(root / "preparation/receipt.json")
    if receipt.get("status") != "COMPLETE" or receipt.get("source_digest") != FROZEN_SOURCE:
        raise ValueError("B2 preparation receipt mismatch")
    if read_json(root / "resource.json").get("status") != "PASS_RESOURCE_PREFLIGHT":
        raise ValueError("resource preflight is not PASS")
    commands = plan.get("command_plan", [])[2:]
    if len(commands) != 58:
        raise ValueError("expected exactly 29 collision/snapshot command pairs")
    for index in range(29):
        collision, snapshot = commands[2 * index:2 * index + 2]
        if collision.get("phase") != "collision_chunk" or collision.get("chunk") != index + 1:
            raise ValueError("collision command ordering mismatch")
        if snapshot.get("phase") != "checkpoint_snapshot" or snapshot.get("chunk") != index + 1:
            raise ValueError("snapshot command ordering mismatch")
    return cfg, commands


def validate_generation(generation: Path, cfg: dict, expected_done: int) -> dict:
    manifest_path = generation / guard.MANIFEST_NAME
    manifest = read_json(manifest_path)
    if (manifest.get("schema") != guard.SCHEMA or
            manifest.get("status") != "PUBLISHED_VERIFIED_LOCAL"):
        raise ValueError("existing generation manifest is not published")
    inventory = guard.validate_checkpoint(generation, cfg)
    for key, value in inventory.items():
        if manifest.get(key) != value:
            raise ValueError(f"existing generation manifest mismatch: {key}")
    if inventory["done"] != expected_done:
        raise ValueError("existing generation done mismatch")
    return manifest


def execute(root: Path, config: Path, plan_path: Path) -> dict:
    if (root / "COMPLETE.json").exists():
        raise FileExistsError("completed B2 must not be rerun")
    plan = read_json(plan_path)
    cfg, commands = validate_inputs(root, config, plan)
    collision_dir = root / "collision"
    receipts = root / "receipts"
    generations = root / "generations"
    receipts.mkdir(exist_ok=True)
    generations.mkdir(exist_ok=True)

    with (root / "gpu.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for index in range(29):
            collision, snapshot = commands[2 * index:2 * index + 2]
            chunk = index + 1
            expected_done = snapshot["expected_completed_steps"]
            generation = generations / f"g{expected_done:06d}"
            if generation.exists():
                validate_generation(generation, cfg, expected_done)
                continue

            # If the writer completed but supervision stopped before publishing
            # the generation, publish it now; never repeat the collision chunk.
            publish_only = False
            if collision_dir.exists():
                inventory = guard.validate_checkpoint(collision_dir, cfg)
                if inventory["done"] == expected_done:
                    publish_only = True
                elif inventory["done"] != expected_done - collision["maximum_steps_in_chunk"]:
                    raise ValueError("active checkpoint is outside the frozen chunk frontier")

            if not publish_only:
                supervisor.command(
                    f"collision.chunk{chunk:03d}", collision["argv"], root,
                    timeout=7200, memory_guard=True,
                )
                inventory = guard.validate_checkpoint(collision_dir, cfg)
                if inventory["done"] != expected_done:
                    raise ValueError("successful chunk did not reach expected done")

            supervisor.command(
                f"snapshot.g{expected_done:06d}", snapshot["argv"], root,
                timeout=1800, memory_guard=False,
            )
            manifest = validate_generation(generation, cfg, expected_done)
            if manifest.get("done") != expected_done or manifest.get("nstep") != 3586:
                raise ValueError("published generation frontier mismatch")
            write_new(receipts / f"chunk{chunk:03d}.committed.json", {
                "status": "CHUNK_AND_GENERATION_COMMITTED",
                "chunk": chunk,
                "done": expected_done,
                "generation": str(generation),
                "generation_manifest_sha256": sha(generation / guard.MANIFEST_NAME),
                "collision_state_sha256": manifest["files"]["state.npy"]["sha256"],
                "next_chunk_authorized": chunk < 29,
            })

    final = guard.validate_checkpoint(collision_dir, cfg)
    result = read_json(collision_dir / "result.json")
    if final["done"] != final["nstep"] or result.get("status") != "completed":
        raise ValueError("B2 did not complete")
    complete = {
        "status": "COMPLETE",
        "job": "B2",
        "new_full_collisions": 1,
        "chunks": 29,
        "retained_generations": 29,
        "done": final["done"],
        "nstep": final["nstep"],
        "result_sha256": sha(collision_dir / "result.json"),
        "final_generation_manifest_sha256": sha(
            generations / "g003586" / guard.MANIFEST_NAME
        ),
    }
    write_new(root / "COMPLETE.json", complete)
    return complete


def main() -> None:
    import mlflow

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
    mlflow.set_tracking_uri("sqlite:///" + str(root.parent / "mlflow.db"))
    mlflow.set_experiment("R3M18_B2_TEMPORAL_RESOLUTION")
    try:
        value = execute(root, args.config.resolve(), args.plan.resolve())
    except BaseException as exc:
        failure = root / "FIRST_FAILURE.json"
        if not failure.exists():
            write_new(failure, {
                "status": "FAILED_OR_INTERRUPTED",
                "type": type(exc).__name__,
                "message": str(exc),
                "automatic_collision_retry": False,
                "damaged_paths_overwritten": False,
            })
        raise
    print(json.dumps(value, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
