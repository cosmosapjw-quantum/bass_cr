"""Run one C21K epoch-cached job through the unchanged private H runner.

The new runtime is published and admitted separately from H/I. The original H
provider, CLI, budgets, build checks, base validation and cleanup remain intact.
No old source file, global import hook, sys.modules entry or receipt is patched.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import asdict
from pathlib import Path
import math
import sys
import time
from types import ModuleType
import uuid

HERE = Path(__file__).resolve().parent
C21I = HERE.parent / "cr_c21i_callback_optimization_20261020"


def private_module(path, raw):
    module = ModuleType("_c21k_runner_" + Path(path).stem + "_" + uuid.uuid4().hex)
    module.__file__ = str(Path(path).resolve())
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True,
                 optimize=sys.flags.optimize), module.__dict__)
    return module


_CONTRACT_PATH = HERE / "epoch_pilot_contract.py"
_CONTRACT_BYTES = _CONTRACT_PATH.read_bytes()
contract = private_module(_CONTRACT_PATH, _CONTRACT_BYTES)
EpochPilotError = contract.EpochPilotError
OPTIMIZATIONS = contract.OPTIMIZATIONS


def load_private_i(i_unit=C21I):
    """Read the fixed I/H closure without importing a scientific package."""
    _, _, payload = contract.verify_inherited_sources(i_unit)
    return private_module(Path(i_unit) / "run_optimized_pilot.py",
                          payload["run_optimized_pilot.py"]), payload


def bind_runner(h, inherited_i, optimizer, admission, mode, *, unit=HERE,
                i_unit=C21I, publication_receipt=None,
                c21i_publication_receipt=None, c21h_publication_receipt=None):
    """Install bindings only in this job's private H module.

    I's old publication verifier intentionally requires detached HEAD=fe6. This
    separate K verifier admits the new K content plus the unchanged H/I ancestry;
    it neither calls that incompatible verifier nor falsifies an I receipt.
    """
    unit, i_unit = Path(unit).resolve(), Path(i_unit).resolve()
    h_unit = i_unit.parent / contract.H_NAME
    k_identity, k_payload = contract.verify_k_source(mode, unit)
    if unit == HERE and k_payload["epoch_pilot_contract.py"] != _CONTRACT_BYTES:
        raise EpochPilotError("LOADED_C21K_CONTRACT_SOURCE_DRIFT")
    initial_h, _, _ = contract.verify_inherited_sources(i_unit)
    i_identity, _ = inherited_i.verify_i_source(mode, i_unit)
    h_context, h_verify, h_write, h_base = (
        h.context, h.verify_own_source, h.write_new_json, h.verified_base)
    runner_identity = {"schema": "C21K_RUNNER_IDENTITY_V1", "optimization": mode,
                       "epoch_policy": contract.EPOCH_POLICY,
                       "source_identity": k_identity,
                       "inherited_c21i_source_identity": i_identity}
    state = {"k_identity": k_identity, "i_identity": i_identity,
             "publication": None, "runner_identity": runner_identity}

    def own_source():
        current_h, _, _ = contract.verify_inherited_sources(i_unit)
        current_i, _ = inherited_i.verify_i_source(mode, i_unit)
        current_k, _ = contract.verify_k_source(mode, unit)
        own = h_verify()
        if (current_h != initial_h or current_i != i_identity or current_k != k_identity
                or own != initial_h):
            raise EpochPilotError("C21K_OR_INHERITED_SOURCE_CHANGED_DURING_JOB")
        # Keep H's eight records unchanged: its build receipt consumes them.
        return {**own, "C21I_SOURCE_IDENTITY": current_i,
                "C21K_SOURCE_IDENTITY": current_k}

    initial_own = own_source()

    class NativeAuthority:
        def __init__(self, original, args):
            self.original, self.args = original, args

        def __getattr__(self, name):
            return getattr(self.original, name)

        def verify_native_binary(self, *args, **kwargs):
            if own_source() != initial_own:
                raise EpochPilotError("NATIVE_SOURCE_CONTEXT_DRIFT")
            published = contract.verify_publications(
                publication_receipt, c21i_publication_receipt,
                c21h_publication_receipt, k_identity, i_identity, initial_h,
                k_unit=unit, i_unit=i_unit)
            if state["publication"] is None:
                h_write(self.args.out / "C21K_PUBLICATION_IDENTITY.json", published)
                state["publication"] = published
            elif state["publication"] != published:
                raise EpochPilotError("PUBLICATION_RECEIPT_CHANGED_DURING_JOB")
            actual = self.original.verify_native_binary(*args, **kwargs)
            if "native_identity" in state and state["native_identity"] != actual:
                raise EpochPilotError("NATIVE_IDENTITY_DRIFT")
            state["native_identity"] = actual
            return actual

    def context(args):
        research = i_unit.parent
        if (args.source_dir.resolve() != research / contract.F_NAME
                or args.c21g_unit.resolve() != research / contract.G_NAME):
            raise EpochPilotError("C21K_REQUIRES_SAME_INHERITED_RESEARCH_CHECKOUT")
        source, c21g, baseline, authority, identity = h_context(args)
        authority = NativeAuthority(authority, args) if args.command == "native" else authority
        state.update(args=args, source=source, c21g=c21g, baseline=baseline,
                     authority=authority, input_identity=identity)
        return source, c21g, baseline, authority, identity

    def write(path, value):
        path = Path(path)
        if path.name in ("JOB_RECEIPT.json", "PLAN_RECEIPT.json"):
            value["c21k_runner"] = copy.deepcopy(runner_identity)
            if path.name == "JOB_RECEIPT.json":
                value["inherited_receipt_schema"] = value.get("schema")
                value["schema"] = "C21K_JOB_RECEIPT_V1"
            try:
                if own_source() != initial_own:
                    raise EpochPilotError("C21K_TERMINAL_SOURCE_DRIFT")
            except Exception as error:
                if path.name == "PLAN_RECEIPT.json":
                    raise
                value["execution"] = "FAILED"
                value["c21k_postcheck_error"] = {"class": type(error).__name__,
                                                 "error": str(error)}
                h_write(path.parent / "C21K_POSTCHECK_ERROR.json", value["c21k_postcheck_error"])
                value["payload_files"] = h.payload_inventory(path.parent)
        h_write(path, value)
        if path.name == "C21H_SOURCE_IDENTITY.json":
            h_write(path.parent / "C21I_SOURCE_IDENTITY.json", i_identity)
            h_write(path.parent / "C21K_SOURCE_IDENTITY.json", k_identity)

    def verified_base(path, command, *args, **kwargs):
        parent = Path(path).resolve()
        receipt = contract.read_json((parent / "JOB_RECEIPT.json").read_bytes())
        if (receipt.get("schema") != "C21K_JOB_RECEIPT_V1"
                or receipt.get("c21k_runner") != runner_identity
                or contract.read_json((parent / "C21K_SOURCE_IDENTITY.json").read_bytes()) != k_identity):
            raise EpochPilotError("FD_FOLLOWUP_REQUIRES_MATCHING_C21K_MODE_AND_RUNTIME")
        if command == "native":
            publication = contract.read_json((parent / "C21K_PUBLICATION_IDENTITY.json").read_bytes())
            if (state["publication"] is None
                    or publication.get("c21k", {}).get("content_commit")
                    != state["publication"]["c21k"]["content_commit"]):
                raise EpochPilotError("FD_FOLLOWUP_C21K_PUBLICATION_MISMATCH")
        # Original H still requires COMPLETE/base, exact fixture/method/input/
        # native/bridge/source identity and a complete unchanged payload map.
        return h_base(path, command, *args, **kwargs)

    def run(fixture, provider, source, binary, out, scales, **kwargs):
        wall = kwargs["wall_s"]
        if not math.isfinite(wall) or wall <= 0:
            raise EpochPilotError("POSITIVE_FINITE_REMAINING_JOB_WALL_REQUIRED")
        deadline = time.monotonic() + wall
        provider_deadline = getattr(provider, "deadline", None)
        if provider_deadline is not None:
            deadline = min(deadline, provider_deadline)
        guard, cache_contract = None, None
        try:
            if own_source() != initial_own:
                raise EpochPilotError("PRE_CALLBACK_SOURCE_DRIFT")
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
                raise EpochPilotError("C21K_SETUP_EXHAUSTED_ORIGINAL_JOB_WALL")
            kwargs["wall_s"] = remaining
            result = optimizer.run_optimized_reference(
                fixture, provider, source, binary, out, scales, **kwargs,
                optimization=mode, cache_contract=cache_contract, cache_guard=guard,
                c21h_dir=h_unit, c21g_dir=state["c21g"], c21i_dir=i_unit)
            if time.monotonic() >= deadline:
                raise EpochPilotError("C21K_ORIGINAL_JOB_WALL_EXCEEDED")
            return result
        finally:
            # The original live provider is still open; H owns later cleanup.
            try:
                if guard is not None:
                    guard(full_hash=True, current_provider=provider)
            finally:
                if own_source() != initial_own:
                    raise EpochPilotError("POST_CALLBACK_SOURCE_DRIFT")
                if time.monotonic() >= deadline:
                    raise EpochPilotError("C21K_ORIGINAL_JOB_WALL_EXCEEDED")

    h.context, h.verify_own_source = context, own_source
    h.run_rust_reference, h.write_new_json, h.verified_base = run, write, verified_base
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--optimization", choices=OPTIMIZATIONS, default="vectorized_exact")
    parser.add_argument("--c21i-unit", type=Path, default=C21I)
    parser.add_argument("--publication-receipt", type=Path)
    parser.add_argument("--c21i-publication-receipt", type=Path)
    parser.add_argument("--c21h-publication-receipt", type=Path)
    options, remaining = parser.parse_known_args(argv)
    _, k_payload = contract.verify_k_source(options.optimization, HERE)
    if k_payload["epoch_pilot_contract.py"] != _CONTRACT_BYTES:
        raise EpochPilotError("LOADED_C21K_CONTRACT_SOURCE_DRIFT")
    inherited_i, i_payload = load_private_i(options.c21i_unit)
    h_unit = options.c21i_unit.resolve().parent / contract.H_NAME
    # H must observe fresh-process NumPy state and set its thread variables
    # before importing the K adapter or any other scientific package.
    h = inherited_i.load_private_h(h_unit)
    optimizer = private_module(HERE / "epoch_adapter.py", k_payload["epoch_adapter.py"])
    admission = private_module(options.c21i_unit / "native_cache_contract.py",
                               i_payload["native_cache_contract.py"])
    bind_runner(h, inherited_i, optimizer, admission, options.optimization,
                i_unit=options.c21i_unit, publication_receipt=options.publication_receipt,
                c21i_publication_receipt=options.c21i_publication_receipt,
                c21h_publication_receipt=options.c21h_publication_receipt)
    return h.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
