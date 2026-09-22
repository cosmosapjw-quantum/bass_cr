"""Preserve sealed chunk boundaries without changing the frozen numerical runner.

Call snapshot ONLY after the v2 witness CLI has returned successfully, and await
it before starting the next chunk. No writer may run concurrently. The frozen
``atomic_npy`` uses os.replace; hardlinks therefore retain the old state inode
when a later save replaces state.npy. In-place writes to either hardlink are NOT
supported. This is an application-level create-only protocol, not filesystem
write protection or a claim of protection against arbitrary storage failure.

Each generation eventually retains another full state inode. A 63,000,000-point
complex128 state is about 1,008,000,128 bytes: 29 retained generations cost about
29.232 GB (about 27.23 GiB), PLUS current/temporary state, initial/final arrays and
other artifacts. A successful hardlink itself needs little space; it is NOT a
promise of negligible retained storage. Budget disk before the collision. No
pruning, cross-filesystem copy fallback, or restore over an old run is performed.

An exclusive output directory is reserved first; the manifest/restore receipt
is published last. Interrupted output, including .pending files, is preserved.
Only a fully verified manifest authorizes restore, and restore always creates a
fresh directory. Run files, witness, and hashes are verified without allocating
a GPU runner or reading an entire state into RAM. Local restart verification
does not imply remote backup or remote restore verification.
"""
from __future__ import annotations

import argparse
import errno
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat

import numpy as np

from cr_repro.grid import GridSpec
from cr_repro.observables import projectile_speed_au
from cr_repro.r3m11 import file_sha, source_digest
from cr_repro.util import config_hash
from scripts.r3m14_collision_initial_witness import (
    EXPECTED_SOURCE_DIGEST,
    ROOT,
    SCHEMA as WITNESS_SCHEMA,
    load_json,
)

SCHEMA = "BASS_CR_R3M17_CHECKPOINT_GENERATION_V1"
MANIFEST_NAME = "r3m17_generation_manifest.json"
RESTORE_RECEIPT = "r3m17_restore_receipt.json"
SEAL = "r3m11_checkpoint_seal.json"
WITNESS = "r3m14_initial_binding.json"
RECEIPT = "r3m14_witness_run_receipt.json"
REQUIRED = ("state.npy", "state.json", SEAL)
OPTIONAL = (WITNESS, RECEIPT, "result.json")


def _safe_path(path: Path) -> Path:
    """Reject symlinks including parent components; never resolve through one."""
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        if part.is_symlink():
            raise ValueError(f"symlink path is forbidden: {part}")
    return path


def _regular(path: Path) -> None:
    _safe_path(path)
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as exc:
        raise ValueError(f"missing required regular file: {path.name}") from exc
    if not stat.S_ISREG(mode):
        raise ValueError(f"not a regular file: {path}")


def _integer(value, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return value


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _publish_json(path: Path, value: dict) -> None:
    """Publish complete bytes without ever replacing existing evidence."""
    pending = path.with_name(path.name + ".pending")
    payload = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    with pending.open("x") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(pending, path, follow_symlinks=False)
    _fsync_directory(path.parent)
    pending.unlink()
    _fsync_directory(path.parent)


def _copy_exclusive(source: Path, target: Path) -> None:
    _regular(source)
    with source.open("rb") as src, target.open("xb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())


def _link_state(source: Path, target: Path) -> None:
    _regular(source)
    if source.stat().st_dev != target.parent.stat().st_dev:
        raise OSError(errno.EXDEV, "state hardlink requires the same filesystem; no copy fallback")
    try:
        os.link(source, target, follow_symlinks=False)
    except OSError as exc:
        if exc.errno == errno.EXDEV:
            raise OSError(errno.EXDEV, "state hardlink requires the same filesystem; no copy fallback") from exc
        raise
    # The writer already fsyncs state bytes before atomic replacement. Retain
    # that durability boundary without modifying the shared inode or mode.
    with target.open("rb") as stream:
        os.fsync(stream.fileno())


def _enriched_config(raw_cfg: dict) -> dict:
    cfg = dict(raw_cfg)
    cfg["_r3m11_controls"] = "FIXED_CAP_SYMMETRIC_V1"
    cfg["_r3m11_source_digest"] = EXPECTED_SOURCE_DIGEST
    return cfg


def validate_checkpoint(run_dir: Path, raw_cfg: dict, *, require_witness: bool = True) -> dict:
    """Validate sealed bytes, source/config, step count and optional v2 evidence.

    This intentionally does not instantiate ControlledTDLRunner: an inspection
    must not allocate the production FFT arrays or change the GPU environment.
    Existing witness runtime identity is preserved; the original v2 CLI checks
    it against the actual scientific runtime and preparation again on restart.
    """
    root = _safe_path(run_dir)
    if source_digest() != EXPECTED_SOURCE_DIGEST:
        raise ValueError("frozen numerical source digest mismatch")
    for name in REQUIRED:
        _regular(root / name)
    seal = load_json(root / SEAL)
    if seal.get("schema") != "R3M11_CHECKPOINT_SEAL_V1":
        raise ValueError("invalid checkpoint seal schema")
    if seal.get("source_digest") != EXPECTED_SOURCE_DIGEST:
        raise ValueError("checkpoint seal source mismatch")
    hashes = {name: file_sha(root / name) for name in REQUIRED}
    if seal.get("files") != {name: hashes[name] for name in ("state.json", "state.npy")}:
        raise ValueError("checkpoint hash mismatch")
    meta = load_json(root / "state.json")
    ident = config_hash(_enriched_config(raw_cfg))
    if meta.get("config_hash") != ident:
        raise ValueError("checkpoint config mismatch")
    done = _integer(meta.get("done"), "done")
    nstep = _integer(meta.get("nstep"), "nstep")
    v = projectile_speed_au(raw_cfg["energy_keV_per_u"])
    total_time = (float(raw_cfg.get("z_stop", 60.)) - float(raw_cfg.get("z_start", -30.))) / v
    dt = float(raw_cfg["dt"])
    if not math.isfinite(total_time) or total_time <= 0 or not math.isfinite(dt) or dt <= 0:
        raise ValueError("invalid configured horizon or dt")
    expected_nstep = math.ceil(total_time / dt)
    if nstep != expected_nstep or not 0 <= done <= nstep:
        raise ValueError("invalid checkpoint done/nstep")
    if meta.get("backend") != raw_cfg.get("backend", "numpy"):
        raise ValueError("checkpoint backend mismatch")
    norm = meta.get("norm")
    if isinstance(norm, bool) or not isinstance(norm, (int, float)) or not math.isfinite(norm) or norm <= 0:
        raise ValueError("invalid checkpoint norm")
    array = np.load(root / "state.npy", mmap_mode="r", allow_pickle=False)
    if array.shape != GridSpec.from_dict(raw_cfg["grid"]).shape() or array.dtype != np.dtype("complex128"):
        raise ValueError("checkpoint state shape/dtype mismatch")
    del array
    present = []
    for name in OPTIONAL:
        if os.path.lexists(root / name):
            _regular(root / name)
            hashes[name] = file_sha(root / name)
            present.append(name)
    if require_witness and (WITNESS not in present or RECEIPT not in present):
        raise ValueError("production checkpoint requires v2 witness and completed-chunk receipt")
    if (WITNESS in present) != (RECEIPT in present):
        raise ValueError("partial witness/receipt pair; wait for successful v2 CLI return")
    if WITNESS in present:
        witness = load_json(root / WITNESS)
        for key in ("prepared_array_digest", "internal_array_digest",
                    "prepared_state_file_sha256", "prepared_receipt_sha256"):
            value = witness.get(key)
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise ValueError(f"v2 witness invalid digest: {key}")
        runtime = witness.get("runtime_environment")
        prepared_environment = witness.get("prepared_environment")
        for name, environment in (("runtime", runtime), ("prepared", prepared_environment)):
            if not isinstance(environment, dict):
                raise ValueError(f"v2 witness missing {name} environment")
            for key in ("python", "numpy", "backend"):
                value = environment.get(key)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"v2 witness invalid {name} environment: {key}")
            if environment["backend"] != meta["backend"]:
                raise ValueError(f"v2 witness {name} environment backend mismatch")
        if any(runtime[key] != prepared_environment[key] for key in ("python", "numpy", "backend")):
            raise ValueError("v2 witness prepared/runtime environment mismatch")
        checks = {
            "schema": WITNESS_SCHEMA,
            "status": "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED",
            "expected_source_digest": EXPECTED_SOURCE_DIGEST,
            "actual_source_digest": EXPECTED_SOURCE_DIGEST,
            "enriched_config_hash": ident,
            "instrumentation_sha256": file_sha(ROOT / "scripts/r3m14_collision_initial_witness.py"),
            "r3m13_helper_sha256": file_sha(ROOT / "scripts/r3m13_initial_state_pair.py"),
            "array_digest_match": True,
            "environment_match": True,
            "norm_match": True,
            "numerical_state_substituted": False,
            "numerical_state_renormalized": False,
            "backend": meta["backend"],
            "shape": list(GridSpec.from_dict(raw_cfg["grid"]).shape()),
            "dtype": np.dtype("complex128").str,
            "dv": GridSpec.from_dict(raw_cfg["grid"]).dv,
        }
        for key, value in checks.items():
            if (witness.get(key) != value
                    or (type(value) is bool and witness.get(key) is not value)):
                raise ValueError(f"v2 witness mismatch: {key}")
        if witness.get("prepared_array_digest") != witness.get("internal_array_digest"):
            raise ValueError("v2 witness array digest mismatch")
        receipt = load_json(root / RECEIPT)
        _integer(receipt.get("done"), "receipt done")
        _integer(receipt.get("nstep"), "receipt nstep")
        checks = {
            "schema": "BASS_CR_R3M14_WITNESS_RUN_RECEIPT_V2",
            "status": "completed" if done == nstep else "checkpoint",
            "done": done, "nstep": nstep,
            "source_digest": EXPECTED_SOURCE_DIGEST,
            "initial_binding_status": witness["status"],
            "instrumentation_sha256": witness["instrumentation_sha256"],
            "r3m13_helper_sha256": witness["r3m13_helper_sha256"],
            "runtime_environment": runtime,
            "state_json_sha256": hashes["state.json"],
            "state_npy_sha256": hashes["state.npy"],
            "seal_sha256": hashes[SEAL],
        }
        for key, value in checks.items():
            if receipt.get(key) != value:
                raise ValueError(f"v2 receipt mismatch: {key}")
    if "result.json" in present:
        result = load_json(root / "result.json")
        if (done != nstep or result.get("status") != "completed"
                or config_hash(result.get("config", {})) != ident
                or result.get("nstep") != nstep):
            raise ValueError("result/checkpoint mismatch")
    return dict(done=done, nstep=nstep, config_hash=ident,
                source_digest=EXPECTED_SOURCE_DIGEST,
                files={name: dict(sha256=sha, size=(root / name).stat().st_size)
                       for name, sha in hashes.items()},
                witness_present=WITNESS in present)


def _fresh_destination(path: Path) -> Path:
    path = _safe_path(path)
    if os.path.lexists(path):
        raise FileExistsError(f"fresh output directory required: {path}")
    if not path.parent.is_dir():
        raise ValueError("output parent must already exist on the state filesystem")
    return path


def _materialize(source: Path, out: Path, inventory: dict) -> None:
    out.mkdir(exist_ok=False)
    _fsync_directory(out.parent)
    _link_state(source / "state.npy", out / "state.npy")
    for name in inventory["files"]:
        if name != "state.npy":
            _copy_exclusive(source / name, out / name)
    _fsync_directory(out)


def snapshot_generation(run_dir: Path, generation_dir: Path, raw_cfg: dict,
                        *, require_witness: bool = True) -> dict:
    """Create an exclusive immutable generation after one completed chunk."""
    source = _safe_path(run_dir)
    out = _fresh_destination(generation_dir)
    before = validate_checkpoint(source, raw_cfg, require_witness=require_witness)
    _materialize(source, out, before)
    after = validate_checkpoint(out, raw_cfg, require_witness=require_witness)
    if after != before:
        raise ValueError("checkpoint changed during snapshot; retain incomplete evidence")
    manifest = dict(schema=SCHEMA, status="PUBLISHED_VERIFIED_LOCAL",
                    source_directory=str(source), **after,
                    state_storage="SAME_FILESYSTEM_HARDLINK_ATOMIC_REPLACE_ONLY",
                    retained_state_bytes_per_generation=after["files"]["state.npy"]["size"],
                    guard_sha256=file_sha(Path(__file__)),
                    remote_restore_status="NOT_EVALUATED")
    _publish_json(out / MANIFEST_NAME, manifest)
    return manifest


def restore_generation(generation_dir: Path, fresh_dir: Path, raw_cfg: dict,
                       *, require_witness: bool = True) -> dict:
    """Restore only to a fresh directory; leave any damaged current run intact."""
    generation = _safe_path(generation_dir)
    out = _fresh_destination(fresh_dir)
    if not (generation / MANIFEST_NAME).exists():
        raise ValueError("unpublished generation: missing manifest")
    _regular(generation / MANIFEST_NAME)
    manifest = load_json(generation / MANIFEST_NAME)
    if manifest.get("schema") != SCHEMA or manifest.get("status") != "PUBLISHED_VERIFIED_LOCAL":
        raise ValueError("invalid generation manifest")
    inventory = validate_checkpoint(generation, raw_cfg, require_witness=require_witness)
    for key, value in inventory.items():
        if manifest.get(key) != value:
            raise ValueError(f"generation manifest mismatch: {key}")
    _materialize(generation, out, inventory)
    restored = validate_checkpoint(out, raw_cfg, require_witness=require_witness)
    if restored != inventory:
        raise ValueError("restored checkpoint identity mismatch; retain incomplete evidence")
    receipt = dict(schema="BASS_CR_R3M17_CHECKPOINT_RESTORE_V1",
                   status="RESTORED_VERIFIED_LOCAL", **restored,
                   generation_directory=str(generation),
                   manifest_sha256=file_sha(generation / MANIFEST_NAME),
                   restored_directory=str(out),
                   guard_sha256=file_sha(Path(__file__)),
                   remote_restore_status="NOT_EVALUATED")
    _publish_json(out / RESTORE_RECEIPT, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("snapshot", "restore"):
        item = sub.add_parser(command)
        item.add_argument("--run" if command == "snapshot" else "--generation", required=True)
        item.add_argument("--out", required=True)
        item.add_argument("--config", required=True)
        item.add_argument("--allow-unwitnessed", action="store_true",
                          help="explicit tiny CPU diagnostic mode; forbidden for production collisions")
    args = parser.parse_args()
    cfg = load_json(Path(args.config))
    if args.allow_unwitnessed and cfg.get("backend", "numpy") != "numpy":
        parser.error("unwitnessed diagnostic mode requires numpy backend")
    fn = snapshot_generation if args.command == "snapshot" else restore_generation
    source = args.run if args.command == "snapshot" else args.generation
    value = fn(Path(source), Path(args.out), cfg, require_witness=not args.allow_unwitnessed)
    print(json.dumps(value, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
