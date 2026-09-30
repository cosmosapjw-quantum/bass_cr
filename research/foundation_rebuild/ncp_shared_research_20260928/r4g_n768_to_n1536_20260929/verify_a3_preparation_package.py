#!/usr/bin/env python3
"""Replay the focused NON-NATIVE A3 suite from a fresh portable extraction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

CORE = "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(archive: Path, python: Path, receipt_path: Path) -> dict:
    archive = Path(archive).resolve()
    python = Path(os.path.abspath(os.path.expanduser(python)))
    receipt_path = Path(receipt_path).resolve()
    if receipt_path.exists() or not archive.is_file() or not python.is_file():
        raise ValueError("create-only receipt, package ZIP and Python required")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "ALLOW_NEW_NATIVE_R4M"):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    nonce_root = Path.home() / ".local/state/bass_r4m/authorizations"
    before_nonces = {p.name for p in nonce_root.glob("*.json")} if nonce_root.exists() else set()
    with tempfile.TemporaryDirectory(prefix="bass_r4m_a3_portable_") as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            if len(names) != len(set(names)) or bundle.testzip() is not None:
                raise ValueError("A3 package ZIP CRC/duplicate failure")
            for info in bundle.infolist():
                rel = Path(info.filename)
                if (rel.is_absolute() or ".." in rel.parts or "\\" in info.filename
                    or ((info.external_attr >> 16) & 0o170000) == 0o120000):
                    raise ValueError("unsafe A3 package ZIP member")
            manifest = json.loads(bundle.read("MANIFEST.json"))
            if set(names) != set(manifest) | {"MANIFEST.json"}:
                raise ValueError("A3 package manifest membership mismatch")
            bundle.extractall(root)
        for rel, row in manifest.items():
            path = root / rel
            if (not path.is_file() or path.stat().st_size != row["bytes"]
                or _sha(path) != row["sha256"]):
                raise ValueError("A3 package manifest byte mismatch: " + rel)
        instructions = json.loads((root / "REPLAY_INSTRUCTIONS.json").read_text())
        template = json.loads((root / "FUTURE_AUTHORIZATION_TEMPLATE.json").read_text())
        pins = json.loads((root / "SOURCE_PINS.json").read_text())
        policy = root / CORE / "RESOURCE_SHARING_POLICY.json"
        salvage = json.loads((root / "A2_CUMULATIVE_SALVAGE_MANIFEST.json").read_text())
        fill = json.loads((root / "N1536_REMAINING_FILL_PLAN.json").read_text())
        selected = json.loads((root / "A2_SELECTED_STAGE_EVIDENCE.json").read_text())
        if (instructions["external_repository_source_required"] is not False
            or instructions["native_science_authorized"] is not False
            or template["resource_sharing_policy"] != "COOPERATIVE_SHARED_HOST"
            or pins["resource_sharing_policy"] != "COOPERATIVE_SHARED_HOST"
            or pins["resource_policy_sha256"] != _sha(policy)
            or template["resource_policy_sha256"] != _sha(policy)
            or template["source_pins_sha256"] != _sha(root / "SOURCE_PINS.json")
            or template["salvage_manifest_sha256"] != _sha(root / "A2_CUMULATIVE_SALVAGE_MANIFEST.json")
            or template["fill_plan_sha256"] != _sha(root / "N1536_REMAINING_FILL_PLAN.json")
            or template["selected_stage_sha256"] != _sha(root / "A2_SELECTED_STAGE_EVIDENCE.json")
            or salvage["canonical_pairs"] != 2159
            or salvage["prior_raw_attempts"] != 368
            or len(fill["remaining_ids"]) != 1424
            or selected["selected_workers"] != 32):
            raise ValueError("A3 portable authority/selection mismatch")
        fixtures = {
            "BASS_R4K_PREDECESSOR_ARCHIVE": ("R4F_A2_PREDECESSOR_RETURN.zip", "predecessor_sha256"),
            "BASS_R4K_A1_ARCHIVE": ("R4G_A1_PARTIAL_RETURN.zip", "a1_sha256"),
            "BASS_R4M_A2_ARCHIVE": ("R4K_A2_PARTIAL_RETURN.zip", "a2_sha256")}
        for key, (filename, sha_key) in fixtures.items():
            path = root / "artifacts" / filename
            if _sha(path) != instructions[sha_key]:
                raise ValueError("A3 portable fixture SHA256 mismatch: " + filename)
            env[key] = str(path)
        core = root / CORE
        compile_cmd = [str(python), "-B", "-m", "py_compile"] + [str(core / name)
            for name in ("resource_census.py", "a2_salvage.py", "run_a3.py",
                         "supervise_a3.py", "make_a3_preparation_package.py")]
        compiled = subprocess.run(compile_cmd, cwd=root, env=env, text=True,
                                  capture_output=True, timeout=30)
        if compiled.returncode:
            raise ValueError("A3 portable py_compile failure: " + compiled.stderr[-2000:])
        launched = subprocess.run(["bash", str(core / "run_a3_science.sh"),
                                   str(root / "native_trap_out")], cwd=root, env=env,
                                  text=True, capture_output=True, timeout=10)
        if launched.returncode != 64 or "A3_NATIVE_NOT_AUTHORIZED" not in launched.stderr:
            raise ValueError("A3 portable launcher native trap failed")
        command = [str(python)] + instructions["test_command"][1:]
        tested = subprocess.run(command, cwd=root, env=env, text=True,
                                capture_output=True, timeout=240)
        match = re.search(r"(\d+) passed in [\d.]+s", tested.stdout)
        if (tested.returncode or not match
            or int(match.group(1)) != instructions["expected_passed"]):
            raise ValueError("A3 portable focused suite failed: " +
                             (tested.stdout + tested.stderr)[-5000:])
        after_nonces = {p.name for p in nonce_root.glob("*.json")} if nonce_root.exists() else set()
        if after_nonces != before_nonces:
            raise ValueError("A3 portable replay consumed authorization nonce")
        result = {"schema": "BASS_R4M_A3_SELF_CONTAINED_REPLAY_V1",
                  "SELF_CONTAINED_TEST_REPLAY_VERIFIED": True,
                  "package_sha256": _sha(archive), "package_bytes": archive.stat().st_size,
                  "zip_crc": "PASS", "manifest_verified_files": len(manifest),
                  "py_compile_exit": compiled.returncode,
                  "tests_passed": int(match.group(1)), "tests_failed": 0, "tests_skipped": 0,
                  "launcher_parser_native_trap": "PASS",
                  "native_operator_calls": 0,
                  "authorization_nonce_consumed": False,
                  "external_PYTHONPATH_used": False,
                  "test_command": command}
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--python", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.archive, args.python, args.receipt), indent=2))


if __name__ == "__main__":
    main()
