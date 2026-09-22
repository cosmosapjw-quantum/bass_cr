"""R3M14 collision wrapper with a fail-closed initial-state identity witness.

Numerical evolution remains in cr_repro.r3m11.ControlledTDLRunner. This sidecar
subclass observes the exact internally prepared state, hashes it, compares it to
an immutable R3M13 preparation artifact, and returns the original array object
unchanged. It never substitutes or renormalizes the state.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np

from cr_repro.backend import asnumpy
from cr_repro.r3m11 import ControlledTDLRunner, file_sha, source_digest
from cr_repro.util import atomic_json, config_hash

EXPECTED_SOURCE_DIGEST = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
SCHEMA = "BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V1"


def load_json(path: Path):
    def hook(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f"duplicate JSON key: {k}")
            out[k] = v
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=hook,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"nonfinite JSON: {x}")))


def ndarray_digest(array) -> str:
    """SHA-256 over dtype, shape and C-order numerical bytes, chunked."""
    a = np.asarray(array)
    if a.dtype.hasobject or not np.isfinite(a).all():
        raise ValueError("finite non-object numerical array required")
    h = hashlib.sha256()
    h.update(b"BASS_CR_NDARRAY_SHA256_V1\0")
    h.update(a.dtype.str.encode("ascii") + b"\0")
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii") + b"\0")
    if a.flags.c_contiguous:
        raw = memoryview(a).cast("B")
        chunk = 16 * 1024 * 1024
        for i in range(0, len(raw), chunk):
            h.update(raw[i:i+chunk])
    else:
        for slab in a:
            h.update(np.ascontiguousarray(slab).view(np.uint8).tobytes())
    return h.hexdigest()


def validate_prepared(prepared_dir: Path, raw_cfg: dict, expected_source_digest: str):
    prepared_dir = Path(prepared_dir)
    receipt_path = prepared_dir / "receipt.json"
    state_path = prepared_dir / "initial.npy"
    receipt = load_json(receipt_path)
    if receipt.get("schema") != "BASS_CR_R3M13_PREPARATION_V1" or receipt.get("status") != "COMPLETE":
        raise ValueError("prepared state is not a complete R3M13 preparation")
    if receipt.get("source_digest") != expected_source_digest:
        raise ValueError("prepared-state source digest mismatch")
    if receipt.get("config") != raw_cfg:
        raise ValueError("prepared-state config differs from collision config")
    if file_sha(state_path) != receipt.get("initial_state_sha256"):
        raise ValueError("prepared initial.npy file hash mismatch")
    a = np.load(state_path, mmap_mode="r", allow_pickle=False)
    if list(a.shape) != receipt.get("shape"):
        raise ValueError("prepared state shape mismatch")
    dv = float(receipt.get("dv"))
    if not math.isfinite(dv) or dv <= 0:
        raise ValueError("invalid prepared-state volume element")
    return {
        "receipt": receipt,
        "receipt_sha256": file_sha(receipt_path),
        "state_file_sha256": file_sha(state_path),
        "array_digest": ndarray_digest(a),
        "shape": list(a.shape),
        "dtype": a.dtype.str,
        "dv": dv,
    }


class WitnessControlledTDLRunner(ControlledTDLRunner):
    def __init__(self, cfg, *, collision_out: Path, prepared_info: dict,
                 expected_source_digest: str, instrumentation_sha256: str):
        self._witness_out = Path(collision_out)
        self._prepared_info = prepared_info
        self._expected_source_digest = expected_source_digest
        self._instrumentation_sha256 = instrumentation_sha256
        super().__init__(cfg)

    def relaxed_initial(self):
        psi, info = super().relaxed_initial()
        host = np.asarray(asnumpy(psi))
        internal_digest = ndarray_digest(host)
        prepared_backend = self._prepared_info["receipt"].get("environment", {}).get("backend")
        backend_match = prepared_backend == self.backend if prepared_backend is not None else True
        digest_match = internal_digest == self._prepared_info["array_digest"]
        same = digest_match and backend_match
        witness = {
            "schema": SCHEMA,
            "status": "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED" if same else "FAIL_INTERNAL_INITIAL_NOT_IDENTICAL",
            "numerical_state_substituted": False,
            "numerical_state_renormalized": False,
            "collision_propagation_started_when_written": False,
            "expected_source_digest": self._expected_source_digest,
            "actual_source_digest": source_digest(),
            "instrumentation_sha256": self._instrumentation_sha256,
            "prepared_receipt_sha256": self._prepared_info["receipt_sha256"],
            "prepared_state_file_sha256": self._prepared_info["state_file_sha256"],
            "prepared_array_digest": self._prepared_info["array_digest"],
            "internal_array_digest": internal_digest,
            "array_digest_match": digest_match,
            "prepared_backend": prepared_backend,
            "backend_match": backend_match,
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
            raise ValueError("actual collision initial state is not byte-identical to prepared initial state")
        return psi, info


def validate_resume(out: Path, prepared_info: dict, runner: ControlledTDLRunner,
                    expected_source_digest: str, instrumentation_sha256: str):
    witness_path = out / "r3m14_initial_binding.json"
    if not witness_path.is_file():
        raise ValueError("existing collision checkpoint lacks R3M14 initial binding witness")
    w = load_json(witness_path)
    if w.get("schema") != SCHEMA or w.get("status") != "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED":
        raise ValueError("initial binding witness is not PASS")
    checks = {
        "expected_source_digest": expected_source_digest,
        "actual_source_digest": source_digest(),
        "instrumentation_sha256": instrumentation_sha256,
        "prepared_receipt_sha256": prepared_info["receipt_sha256"],
        "prepared_state_file_sha256": prepared_info["state_file_sha256"],
        "prepared_array_digest": prepared_info["array_digest"],
        "enriched_config_hash": config_hash(runner.cfg),
    }
    for k, v in checks.items():
        if w.get(k) != v:
            raise ValueError(f"resume binding mismatch: {k}")
    return w


def run_bound(config_path: Path, prepared_dir: Path, out: Path, max_steps: int | None,
              expected_source_digest: str = EXPECTED_SOURCE_DIGEST):
    if source_digest() != expected_source_digest:
        raise ValueError("unexpected cr_repro source digest")
    raw_cfg = load_json(config_path)
    prepared = validate_prepared(prepared_dir, raw_cfg, expected_source_digest)
    out = Path(out)
    script_sha = file_sha(Path(__file__))
    runner = WitnessControlledTDLRunner(raw_cfg, collision_out=out, prepared_info=prepared,
                                        expected_source_digest=expected_source_digest,
                                        instrumentation_sha256=script_sha)
    has_checkpoint = (out / "state.json").exists() or (out / "state.npy").exists()
    if has_checkpoint:
        validate_resume(out, prepared, runner, expected_source_digest, script_sha)
    elif out.exists() and any(out.iterdir()):
        raise ValueError("fresh collision directory must be empty")
    result = runner.run(out, max_steps=max_steps)
    atomic_json(out / "r3m14_witness_run_receipt.json", {
        "schema": "BASS_CR_R3M14_WITNESS_RUN_RECEIPT_V1",
        "status": result.get("status"),
        "done": result.get("done", result.get("nstep")),
        "nstep": result.get("nstep"),
        "source_digest": source_digest(),
        "instrumentation_sha256": script_sha,
        "initial_binding_status": load_json(out / "r3m14_initial_binding.json")["status"],
        "state_json_sha256": file_sha(out / "state.json") if (out / "state.json").is_file() else None,
        "state_npy_sha256": file_sha(out / "state.npy") if (out / "state.npy").is_file() else None,
        "seal_sha256": file_sha(out / "r3m11_checkpoint_seal.json") if (out / "r3m11_checkpoint_seal.json").is_file() else None,
        "physical_rate_evaluated": False,
        "bgrid": "NO_GO",
    })
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--prepared", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-steps", type=int)
    a = p.parse_args()
    out = run_bound(Path(a.config), Path(a.prepared), Path(a.out), a.max_steps)
    print(json.dumps(out, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
