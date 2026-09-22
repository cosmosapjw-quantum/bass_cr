"""R3M14 fail-closed wrapper binding the actual collision initial state to R3M13 prep.

The numerical evolution remains entirely in
``cr_repro.r3m11.ControlledTDLRunner``.  This sidecar reuses the canonical
R3M13 preparation loader as the preparation-state SSOT, observes the exact
state returned by the inherited ``relaxed_initial()``, records an identity
witness before the first real-time step, and returns the original state object
unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path

import numpy as np

from cr_repro.backend import asnumpy
from cr_repro.r3m11 import ControlledTDLRunner, file_sha, source_digest
from cr_repro.util import atomic_json, config_hash

EXPECTED_SOURCE_DIGEST = (
    "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
)
SCHEMA = "BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V2"
ROOT = Path(__file__).resolve().parents[1]
R3M13_HELPER = ROOT / "scripts/r3m13_initial_state_pair.py"
NORM_TOL = 2e-10
HASH_CHUNK_BYTES = 16 * 1024 * 1024
NORM_CHUNK_ELEMENTS = 1 << 20


def load_json(path: Path):
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out

    def bad_constant(token):
        raise ValueError(f"nonfinite JSON: {token}")

    return json.loads(
        Path(path).read_text(),
        object_pairs_hook=hook,
        parse_constant=bad_constant,
    )


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_r3m13_helper():
    """Load the checked-out canonical R3M13 helper without copying its logic."""
    spec = importlib.util.spec_from_file_location(
        "_bass_cr_r3m13_initial_state_pair", R3M13_HELPER
    )
    if spec is None or spec.loader is None:
        raise ValueError("cannot load canonical R3M13 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime_environment(backend: str) -> dict:
    """Record exact runtime identity used for the witness and restart binding."""
    env = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "backend": backend,
    }
    try:
        import cupy as cp

        env.update(
            cupy=cp.__version__,
            cuda_runtime=int(cp.cuda.runtime.runtimeGetVersion()),
            cuda_driver=int(cp.cuda.runtime.driverGetVersion()),
        )
        if backend == "cupy":
            device = cp.cuda.Device()
            env["cuda_device_id"] = int(device.id)
            try:
                name = cp.cuda.runtime.getDeviceProperties(device.id)["name"]
                env["cuda_device_name"] = (
                    name.decode() if isinstance(name, bytes) else str(name)
                )
            except Exception:
                pass
    except Exception:
        pass
    return env


def ndarray_digest(array) -> str:
    """Typed SHA-256 over dtype, shape, and C-order numerical bytes."""
    arr = np.asarray(array)
    if arr.dtype.hasobject or not np.isfinite(arr).all():
        raise ValueError("finite non-object numerical array required")

    h = hashlib.sha256()
    h.update(b"BASS_CR_NDARRAY_SHA256_V1\0")
    h.update(arr.dtype.str.encode("ascii") + b"\0")
    h.update(
        json.dumps(list(arr.shape), separators=(",", ":")).encode("ascii") + b"\0"
    )

    if arr.flags.c_contiguous:
        raw = memoryview(arr).cast("B")
        for offset in range(0, len(raw), HASH_CHUNK_BYTES):
            h.update(raw[offset : offset + HASH_CHUNK_BYTES])
    else:
        for slab in arr:
            h.update(np.ascontiguousarray(slab).view(np.uint8).tobytes())
    return h.hexdigest()


def weighted_norm(array, dv: float) -> float:
    arr = np.asarray(array).reshape(-1)
    partials = []
    for offset in range(0, arr.size, NORM_CHUNK_ELEMENTS):
        chunk = arr[offset : offset + NORM_CHUNK_ELEMENTS]
        partials.append(float(np.vdot(chunk, chunk).real) * dv)
    return math.fsum(partials)


def validate_prepared(
    prepared_dir: Path,
    raw_cfg: dict,
    expected_source_digest: str,
) -> dict:
    """Validate preparation through the canonical R3M13 loader, then add bindings."""
    prepared_dir = Path(prepared_dir)
    helper = load_r3m13_helper()

    if getattr(helper, "EXPECTED_SOURCE_DIGEST", None) != expected_source_digest:
        raise ValueError("R3M13 helper source pin mismatch")

    # SSOT reuse: this verifies R3M13 status/source, dynamics_fingerprint,
    # initial.npy file hash, grid shape, and dv exactly as R3M13 defined them.
    state, receipt = helper.load_prepared(prepared_dir)

    if receipt.get("schema") != "BASS_CR_R3M13_PREPARATION_V1":
        raise ValueError("unexpected R3M13 preparation schema")
    helper_sha = file_sha(R3M13_HELPER)
    if receipt.get("script_sha256") != helper_sha:
        raise ValueError("R3M13 helper script hash mismatch")
    if canonical_json(receipt.get("config")) != canonical_json(raw_cfg):
        raise ValueError("prepared-state canonical config differs from collision config")

    dv = float(receipt["dv"])
    norm = weighted_norm(state, dv)
    if abs(norm - 1.0) > NORM_TOL:
        raise ValueError("prepared state is not normalized in its grid measure")

    return {
        "receipt": receipt,
        "receipt_sha256": file_sha(prepared_dir / "receipt.json"),
        "state_file_sha256": file_sha(prepared_dir / "initial.npy"),
        "array_digest": ndarray_digest(state),
        "shape": list(state.shape),
        "dtype": state.dtype.str,
        "dv": dv,
        "norm": norm,
        "helper_sha256": helper_sha,
    }


class WitnessControlledTDLRunner(ControlledTDLRunner):
    """Observe and bind the inherited initial state without modifying it."""

    def __init__(
        self,
        cfg,
        *,
        collision_out: Path,
        prepared_info: dict,
        expected_source_digest: str,
        instrumentation_sha256: str,
    ):
        self._witness_out = Path(collision_out)
        self._prepared_info = prepared_info
        self._expected_source_digest = expected_source_digest
        self._instrumentation_sha256 = instrumentation_sha256
        super().__init__(cfg)

    def relaxed_initial(self):
        psi, info = super().relaxed_initial()
        host = np.asarray(asnumpy(psi))
        internal_digest = ndarray_digest(host)
        internal_norm = weighted_norm(host, self.dv)

        prepared_env = self._prepared_info["receipt"].get("environment", {})
        runtime_env = runtime_environment(self.backend)
        # R3M13 records exactly these three fields. Extra CUDA/CuPy identity is
        # bound separately across collision restarts below.
        environment_match = all(
            prepared_env.get(key) == runtime_env.get(key)
            for key in ("python", "numpy", "backend")
        )
        digest_match = internal_digest == self._prepared_info["array_digest"]
        norm_match = abs(internal_norm - 1.0) <= NORM_TOL
        same = digest_match and environment_match and norm_match

        witness = {
            "schema": SCHEMA,
            "status": (
                "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED"
                if same
                else "FAIL_INTERNAL_INITIAL_NOT_IDENTICAL"
            ),
            "numerical_state_substituted": False,
            "numerical_state_renormalized": False,
            "collision_propagation_started_when_written": False,
            "expected_source_digest": self._expected_source_digest,
            "actual_source_digest": source_digest(),
            "instrumentation_sha256": self._instrumentation_sha256,
            "r3m13_helper_sha256": self._prepared_info["helper_sha256"],
            "prepared_receipt_sha256": self._prepared_info["receipt_sha256"],
            "prepared_state_file_sha256": self._prepared_info["state_file_sha256"],
            "prepared_array_digest": self._prepared_info["array_digest"],
            "internal_array_digest": internal_digest,
            "array_digest_match": digest_match,
            "prepared_norm": self._prepared_info["norm"],
            "internal_norm": internal_norm,
            "norm_match": norm_match,
            "prepared_environment": prepared_env,
            "runtime_environment": runtime_env,
            "environment_match": environment_match,
            "shape": list(host.shape),
            "dtype": host.dtype.str,
            "dv": self.dv,
            "backend": self.backend,
            "enriched_config_hash": config_hash(self.cfg),
            "initial_metadata": info,
            "physical_rate_evaluated": False,
            "bgrid": "NO_GO",
            "claim_scope": "IDENTITY_BINDING_ONLY_NOT_CONVERGENCE",
        }
        atomic_json(self._witness_out / "r3m14_initial_binding.json", witness)

        if not same:
            raise ValueError(
                "actual collision initial state is not "
                "byte-identical/environment-bound to prepared initial state"
            )
        # Critical noninterference property: return the inherited object exactly.
        return psi, info


def validate_resume(
    out: Path,
    prepared_info: dict,
    runner: ControlledTDLRunner,
    expected_source_digest: str,
    instrumentation_sha256: str,
):
    witness_path = out / "r3m14_initial_binding.json"
    if not witness_path.is_file():
        raise ValueError("existing collision checkpoint lacks R3M14 initial binding witness")
    witness = load_json(witness_path)
    if (
        witness.get("schema") != SCHEMA
        or witness.get("status")
        != "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED"
    ):
        raise ValueError("initial binding witness is not PASS")

    checks = {
        "expected_source_digest": expected_source_digest,
        "actual_source_digest": source_digest(),
        "instrumentation_sha256": instrumentation_sha256,
        "r3m13_helper_sha256": prepared_info["helper_sha256"],
        "prepared_receipt_sha256": prepared_info["receipt_sha256"],
        "prepared_state_file_sha256": prepared_info["state_file_sha256"],
        "prepared_array_digest": prepared_info["array_digest"],
        "enriched_config_hash": config_hash(runner.cfg),
        "runtime_environment": runtime_environment(runner.backend),
    }
    for key, expected in checks.items():
        if witness.get(key) != expected:
            raise ValueError(f"resume binding mismatch: {key}")
    return witness


def run_bound(
    config_path: Path,
    prepared_dir: Path,
    out: Path,
    max_steps: int | None,
    expected_source_digest: str = EXPECTED_SOURCE_DIGEST,
):
    if source_digest() != expected_source_digest:
        raise ValueError("unexpected cr_repro source digest")

    raw_cfg = load_json(config_path)
    prepared = validate_prepared(prepared_dir, raw_cfg, expected_source_digest)
    out = Path(out)
    script_sha = file_sha(Path(__file__))
    runner = WitnessControlledTDLRunner(
        raw_cfg,
        collision_out=out,
        prepared_info=prepared,
        expected_source_digest=expected_source_digest,
        instrumentation_sha256=script_sha,
    )

    has_checkpoint = (out / "state.json").exists() or (out / "state.npy").exists()
    if has_checkpoint:
        validate_resume(out, prepared, runner, expected_source_digest, script_sha)
    elif out.exists() and any(out.iterdir()):
        raise ValueError("fresh collision directory must be empty")

    result = runner.run(out, max_steps=max_steps)
    atomic_json(
        out / "r3m14_witness_run_receipt.json",
        {
            "schema": "BASS_CR_R3M14_WITNESS_RUN_RECEIPT_V2",
            "status": result.get("status"),
            "done": result.get("done", result.get("nstep")),
            "nstep": result.get("nstep"),
            "source_digest": source_digest(),
            "r3m13_helper_sha256": prepared["helper_sha256"],
            "instrumentation_sha256": script_sha,
            "runtime_environment": runtime_environment(runner.backend),
            "initial_binding_status": load_json(
                out / "r3m14_initial_binding.json"
            )["status"],
            "state_json_sha256": (
                file_sha(out / "state.json") if (out / "state.json").is_file() else None
            ),
            "state_npy_sha256": (
                file_sha(out / "state.npy") if (out / "state.npy").is_file() else None
            ),
            "seal_sha256": (
                file_sha(out / "r3m11_checkpoint_seal.json")
                if (out / "r3m11_checkpoint_seal.json").is_file()
                else None
            ),
            "physical_rate_evaluated": False,
            "bgrid": "NO_GO",
        },
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--prepared", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-steps", type=int)
    args = parser.parse_args()
    result = run_bound(
        Path(args.config),
        Path(args.prepared),
        Path(args.out),
        args.max_steps,
    )
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
