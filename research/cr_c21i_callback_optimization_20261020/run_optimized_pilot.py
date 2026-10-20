"""C21I modes through the unchanged, source-pinned C21H single-job runner.

Plan and manufactured smoke jobs may run before publication. Native jobs need
the current PUBLISHED H and I receipts and an isolated detached I content
checkout. External document receipts resolve historical pending receipts in a
content commit. This runner changes private bindings only; H owns the job,
budgets, worker policy, create-only output, FD parent checks and cleanup.
"""
from __future__ import annotations

import argparse
import builtins
import copy
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from types import ModuleType
import uuid

HERE = Path(__file__).resolve().parent
C21H = HERE.parent / "cr_c21h_vigilode_bridge_20261019"
REPOSITORY = "cosmosapjw-quantum/bass_cr"
C21H_MANIFEST_SHA256 = "7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb"
OPTIMIZATIONS = ("baseline", "vectorized", "vectorized_exact")
RUNTIME_FILES = frozenset(("run_optimized_pilot.py", "optimized_adapter.py",
                           "native_cache_contract.py"))


class OptimizedPilotError(RuntimeError):
    pass


def _record_bytes(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _manifest_files(unit):
    unit = Path(unit).resolve()
    manifest_path = unit / "EXECUTION_MANIFEST.json"
    if manifest_path.is_symlink():
        raise OptimizedPilotError("EXECUTION_MANIFEST_SYMLINK")
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    files = {}
    for name, expected in manifest["runtime_files"].items():
        rel = Path(name)
        path = unit / rel
        if (rel.is_absolute() or ".." in rel.parts or path.is_symlink()
                or not path.resolve().is_relative_to(unit)):
            raise OptimizedPilotError("RUNTIME_SOURCE_PATH " + name)
        data = path.read_bytes()
        if _record_bytes(data) != expected:
            raise OptimizedPilotError("RUNTIME_SOURCE_MISMATCH " + name)
        files[name] = data
    return manifest, raw, files


def _verified_h(unit=C21H):
    manifest, raw, files = _manifest_files(unit)
    if (hashlib.sha256(raw).hexdigest() != C21H_MANIFEST_SHA256
            or len(files) != 8):
        raise OptimizedPilotError("PINNED_C21H_EIGHT_SOURCE_MANIFEST_REQUIRED")
    return manifest, raw, files


def verify_i_source(mode, unit=HERE):
    if mode not in OPTIMIZATIONS:
        raise OptimizedPilotError("UNKNOWN_OPTIMIZATION")
    manifest, raw, files = _manifest_files(unit)
    if (manifest.get("schema") != "C21I_EXECUTION_MANIFEST_V1"
            or set(files) != RUNTIME_FILES
            or manifest.get("c21h_manifest_sha256") != C21H_MANIFEST_SHA256):
        raise OptimizedPilotError("C21I_THREE_SOURCE_MANIFEST_REQUIRED")
    return ({"schema": "C21I_SOURCE_IDENTITY_V1", "optimization": mode,
             "manifest": _record_bytes(raw),
             "runtime_files": copy.deepcopy(manifest["runtime_files"]),
             "c21h_manifest_sha256": C21H_MANIFEST_SHA256}, files)


def _private_module(path, raw, *, local_builtins=None):
    module = ModuleType("_c21i_private_" + Path(path).stem + "_" + uuid.uuid4().hex)
    module.__file__ = str(Path(path).resolve())
    module.__package__ = ""
    if local_builtins is not None:
        module.__dict__["__builtins__"] = local_builtins
    exec(compile(raw, module.__file__, "exec", dont_inherit=True,
                 optimize=sys.flags.optimize), module.__dict__)
    return module


def load_private_h(unit=C21H):
    """Run H's environment/NumPy guard before loading either adapter.

    A module-local import hook lazily supplies the verified H optical adapter.
    It neither replaces sys.modules['optical_adapter'] nor imports NumPy first.
    H's original BudgetedNativeMicro code and namespace remain source-defined.
    """
    unit = Path(unit).resolve()
    _, _, files = _verified_h(unit)
    adapter = None
    original_import = builtins.__import__

    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        nonlocal adapter
        if name == "optical_adapter" and level == 0:
            if adapter is None:
                adapter = _private_module(unit / "optical_adapter.py",
                                          files["optical_adapter.py"])
            return adapter
        return original_import(name, globals, locals, fromlist, level)

    local_builtins = dict(vars(builtins))
    local_builtins["__import__"] = local_import
    return _private_module(unit / "run_pilot.py", files["run_pilot.py"],
                           local_builtins=local_builtins)


def _git(root, *args, allowed=(0,)):
    completed = subprocess.run(["git", "-C", str(root), *args],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=15, check=False)
    if completed.returncode not in allowed:
        raise OptimizedPilotError("PUBLICATION_GIT_CHECK_FAILED " + " ".join(args))
    return completed


def _publication(receipt_path, unit, own):
    """Bind receipt claims to actual local committed manifest/runtime bytes."""
    unit = Path(unit).resolve()
    root = Path(_git(unit, "rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()
    relative = unit.relative_to(root).as_posix()
    path = Path(receipt_path).resolve()
    raw = path.read_bytes()
    receipt = json.loads(raw)
    commit = receipt.get("content_commit")
    if (receipt.get("status") != "PUBLISHED"
            or receipt.get("repository") != REPOSITORY
            or receipt.get("unit", "").rstrip("/") != relative
            or not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None
            or not isinstance(receipt.get("branch"), str) or not receipt["branch"]
            or receipt.get("execution_manifest_sha256") != own["manifest"]["sha256"]):
        raise OptimizedPilotError("NATIVE_REQUIRES_MATCHING_PUBLISHED_RECEIPT " + relative)
    if _git(root, "cat-file", "-t", commit).stdout.strip() != b"commit":
        raise OptimizedPilotError("PUBLISHED_CONTENT_COMMIT_REQUIRED")
    records = {"EXECUTION_MANIFEST.json": own["manifest"], **own["runtime_files"]}
    for name, expected in records.items():
        committed = _git(root, "show", commit + ":" + relative + "/" + name).stdout
        if _record_bytes(committed) != expected:
            raise OptimizedPilotError("PUBLISHED_RUNTIME_CONTENT_MISMATCH " + name)
    return {"receipt_path": str(path), "receipt": _record_bytes(raw),
            "repository": REPOSITORY, "unit": relative,
            "content_commit": commit, "manifest": own["manifest"]}, root


def verify_publications(h_receipt, i_receipt, h_own, i_own,
                        h_unit=C21H, i_unit=HERE):
    h, h_root = _publication(h_receipt, h_unit, h_own)
    i, i_root = _publication(i_receipt, i_unit, i_own)
    if h_root != i_root:
        raise OptimizedPilotError("PUBLISHED_UNITS_REQUIRE_ONE_CHECKOUT")
    _git(i_root, "merge-base", "--is-ancestor", h["content_commit"], i["content_commit"])
    head = _git(i_root, "rev-parse", "HEAD").stdout.decode().strip()
    attached = _git(i_root, "symbolic-ref", "-q", "HEAD", allowed=(0, 1))
    if head != i["content_commit"] or attached.returncode != 1:
        raise OptimizedPilotError("DETACHED_PUBLISHED_C21I_CONTENT_CHECKOUT_REQUIRED")
    return {"schema": "C21I_NATIVE_PUBLICATION_IDENTITY_V1", "c21h": h, "c21i": i}


def bind_runner(h, optimizer, admission, mode, *, unit=HERE, h_unit=C21H,
                publication_receipt=None, c21h_publication_receipt=None):
    """Install one job's scoped bindings in an already private H module."""
    unit, h_unit = Path(unit).resolve(), Path(h_unit).resolve()
    i_identity, _ = verify_i_source(mode, unit)
    h_context, h_verify, h_write = h.context, h.verify_own_source, h.write_new_json
    state = {"i_identity": i_identity, "publication": None}

    def own_source():
        _verified_h(h_unit)
        own = h_verify()
        current, _ = verify_i_source(mode, unit)
        if current != i_identity:
            raise OptimizedPilotError("C21I_SOURCE_CHANGED_DURING_JOB")
        # Leave the eight H records intact: H's build receipt consumes them.
        return {**own, "C21I_SOURCE_IDENTITY": current}

    initial_own = own_source()

    class NativeAuthority:
        def __init__(self, original, args):
            self.original, self.args = original, args

        def __getattr__(self, name):
            return getattr(self.original, name)

        def verify_native_binary(self, *args, **kwargs):
            if own_source() != initial_own:
                raise OptimizedPilotError("NATIVE_SOURCE_CONTEXT_DRIFT")
            published = verify_publications(
                c21h_publication_receipt or h_unit / "PUBLICATION_RECEIPT.json",
                publication_receipt or unit / "PUBLICATION_RECEIPT.json",
                initial_own, i_identity, h_unit, unit)
            if state["publication"] is None:
                h_write(self.args.out / "C21I_PUBLICATION_IDENTITY.json", published)
                state["publication"] = published
            elif state["publication"] != published:
                raise OptimizedPilotError("PUBLICATION_RECEIPT_CHANGED_DURING_JOB")
            actual = self.original.verify_native_binary(*args, **kwargs)
            if "native_identity" in state and state["native_identity"] != actual:
                raise OptimizedPilotError("NATIVE_IDENTITY_DRIFT")
            state["native_identity"] = actual
            return actual

    def context(args):
        source, c21g, baseline, contract, identity = h_context(args)
        authority = NativeAuthority(contract, args) if args.command == "native" else contract
        state.update(args=args, source=source, c21g=c21g, baseline=baseline,
                     authority=authority, input_identity=identity)
        return source, c21g, baseline, authority, identity

    def write(path, value):
        path = Path(path)
        if path.name in ("JOB_RECEIPT.json", "PLAN_RECEIPT.json"):
            value["c21i_runner"] = {"optimization": mode,
                                     "source_identity": i_identity}
            try:
                if own_source() != initial_own:
                    raise OptimizedPilotError("C21I_TERMINAL_SOURCE_DRIFT")
            except Exception as error:
                if path.name == "PLAN_RECEIPT.json":
                    raise
                value["execution"] = "FAILED"
                value["c21i_postcheck_error"] = {"class": type(error).__name__,
                                                 "error": str(error)}
                h_write(path.parent / "C21I_POSTCHECK_ERROR.json", value["c21i_postcheck_error"])
                value["payload_files"] = h.payload_inventory(path.parent)
        h_write(path, value)
        if path.name == "C21H_SOURCE_IDENTITY.json":
            h_write(path.parent / "C21I_SOURCE_IDENTITY.json", i_identity)

    def run(fixture, provider, source, binary, out, scales, **kwargs):
        wall = kwargs["wall_s"]
        if not math.isfinite(wall) or wall <= 0:
            raise OptimizedPilotError("POSITIVE_FINITE_REMAINING_JOB_WALL_REQUIRED")
        # This is H's remaining budget, not a new 300-second job epoch.
        deadline = time.monotonic() + wall
        provider_deadline = getattr(provider, "deadline", None)
        if provider_deadline is not None:
            deadline = min(deadline, provider_deadline)
        guard, cache_contract = None, None
        try:
            if own_source() != initial_own:
                raise OptimizedPilotError("PRE_CALLBACK_SOURCE_DRIFT")
            args = state["args"]
            if args.command == "native" and mode == "vectorized_exact":
                actual = state["authority"].verify_native_binary(args.native, source, args.build_dir)
                fixture_identity = {"sha256": fixture.digest, "fixture": asdict(fixture)}
                source_identity = {"own": initial_own, "input": state["input_identity"],
                    "source_directory": str(Path(source).resolve()),
                    "c21g_directory": str(state["c21g"]),
                    "publication": state["publication"]}
                cache_contract, guard = admission.admit_native_cache(
                    provider, actual, fixture_identity, source_identity)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise OptimizedPilotError("C21I_SETUP_EXHAUSTED_ORIGINAL_JOB_WALL")
            kwargs["wall_s"] = remaining
            result = optimizer.run_optimized_reference(
                fixture, provider, source, binary, out, scales, **kwargs,
                optimization=mode, cache_contract=cache_contract, cache_guard=guard,
                c21h_dir=h_unit, c21g_dir=state["c21g"])
            if time.monotonic() >= deadline:
                raise OptimizedPilotError("C21I_ORIGINAL_JOB_WALL_EXCEEDED")
            return result
        finally:
            # H closes the provider only after this function returns/raises.
            try:
                if guard is not None:
                    guard(full_hash=True, current_provider=provider)
            finally:
                if own_source() != initial_own:
                    raise OptimizedPilotError("POST_CALLBACK_SOURCE_DRIFT")
                if time.monotonic() >= deadline:
                    raise OptimizedPilotError("C21I_ORIGINAL_JOB_WALL_EXCEEDED")

    h.context, h.verify_own_source = context, own_source
    h.run_rust_reference, h.write_new_json = run, write
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--optimization", choices=OPTIMIZATIONS, default="vectorized")
    parser.add_argument("--publication-receipt", type=Path)
    parser.add_argument("--c21h-publication-receipt", type=Path)
    options, remaining = parser.parse_known_args(argv)
    # H must observe fresh-process NumPy state and set all five workers first.
    h = load_private_h()
    _, files = verify_i_source(options.optimization)
    optimizer = _private_module(HERE / "optimized_adapter.py", files["optimized_adapter.py"])
    admission = _private_module(HERE / "native_cache_contract.py", files["native_cache_contract.py"])
    bind_runner(h, optimizer, admission, options.optimization,
                publication_receipt=options.publication_receipt,
                c21h_publication_receipt=options.c21h_publication_receipt)
    return h.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
