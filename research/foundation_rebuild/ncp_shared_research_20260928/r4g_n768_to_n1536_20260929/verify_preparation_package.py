#!/usr/bin/env python3
"""Verify a portable R4G ZIP from a fresh extracted tree without native science."""
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


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(archive: Path, python: Path, receipt_path: Path) -> dict:
    archive = Path(archive).resolve()
    # Keep the venv entry point: resolving its symlink may select system Python.
    python = Path(os.path.abspath(os.path.expanduser(python)))
    receipt_path = Path(receipt_path).resolve()
    if receipt_path.exists() or not archive.is_file() or not python.is_file():
        raise ValueError("create-only receipt, existing ZIP and Python required")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    nonce = Path.home() / ".local/state/bass_r4g/authorizations/R4G-N1536-SYNTHETIC-TRAP.json"
    if nonce.exists():
        raise ValueError("synthetic trap nonce already exists")
    with tempfile.TemporaryDirectory(prefix="bass_r4g_portable_replay_") as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            if len(names) != len(set(names)) or z.testzip() is not None:
                raise ValueError("package ZIP duplicate or CRC failure")
            for info in z.infolist():
                rel = Path(info.filename)
                if (rel.is_absolute() or ".." in rel.parts or "\\" in info.filename
                    or ((info.external_attr >> 16) & 0o170000) == 0o120000):
                    raise ValueError("unsafe package member")
            manifest = json.loads(z.read("MANIFEST.json"))
            if set(names) != set(manifest) | {"MANIFEST.json"}:
                raise ValueError("package manifest membership mismatch")
            z.extractall(root)
        for rel, row in manifest.items():
            data = (root / rel).read_bytes()
            if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
                raise ValueError("extracted package manifest mismatch: " + rel)
        instructions = json.loads((root / "REPLAY_INSTRUCTIONS.json").read_text())
        if instructions["external_repository_source_required"] is not False:
            raise ValueError("package claims external source dependency")
        policy = json.loads((root / CORE / "ADAPTIVE_WORKER_POLICY.json").read_text())
        pilot = json.loads((root / "USEFUL_PILOT_PLAN.json").read_text())
        continuation = json.loads((root / "PILOT_CONTINUATION_PLAN.json").read_text())
        resume = json.loads((root / "N1536_RESUME_QUERY_PLAN.json").read_text())
        template = json.loads((root / "FUTURE_AUTHORIZATION_TEMPLATE.json").read_text())
        a1_fixture = root / "artifacts/R4G_A1_PARTIAL_RETURN.zip"
        predecessor_fixture = root / "artifacts/R4F_A2_PREDECESSOR_RETURN.zip"
        if (_sha(a1_fixture.read_bytes()) != instructions["a1_partial_fixture_sha256"]
            or _sha(predecessor_fixture.read_bytes()) != instructions["predecessor_fixture_sha256"]):
            raise ValueError("portable A1/predecessor fixture SHA256 mismatch")
        env["BASS_R4K_A1_ARCHIVE"] = str(a1_fixture)
        env["BASS_R4K_PREDECESSOR_ARCHIVE"] = str(predecessor_fixture)
        expected_pilot = {"worker_stages": [8, 16, 32],
                          "pilot_query_counts": [16, 32, 64],
                          "pilot_query_total": 112,
                          "post_pilot_remaining": 1424}
        if ({key: template.get(key) for key in expected_pilot} != expected_pilot
            or policy["stages"] != expected_pilot["worker_stages"]
            or [len(stage["query_ids"]) for stage in pilot["stages"]]
                != expected_pilot["pilot_query_counts"]
            or len(pilot["remaining_ids"]) != expected_pilot["post_pilot_remaining"]
            or "pilot_queries" in template
            or len(continuation["new_stages"]) != 2
            or [x["workers"] for x in continuation["new_stages"]] != [16, 32]
            or resume["remaining_midpoint_count"] != 1520
            or resume["a1_raw_attempts"] != 54
            or template["lifetime_raw_attempt_cap"] != 16896
            or template["prior_a1_raw_attempts"] != 54):
            raise ValueError("portable pilot authority/template mismatch")
        compile_cmd = [str(python), "-B", "-m", "py_compile"] + [
            str(root / CORE / name) for name in (
                "adaptive_workers.py", "successor.py", "run_n1536.py",
                "a1_salvage.py", "resource_census.py",
                "supervise_n1536.py", "make_preparation_package.py")]
        compiled = subprocess.run(compile_cmd, cwd=root, env=env, text=True,
                                  capture_output=True, timeout=30)
        if compiled.returncode:
            raise ValueError("extracted package py_compile failed: " + compiled.stderr[-2000:])
        source_check = (
            "import sys,pathlib;"
            "r=pathlib.Path.cwd().resolve();"
            "sys.path.insert(0,str(r/'research/foundation_rebuild/"
            "ncp_shared_research_20260928/r4c_temporal_continuation'));"
            "sys.path.insert(0,str(r/'research/foundation_rebuild/"
            "ncp_shared_research_20260928/r4g_n768_to_n1536_20260929'));"
            "sys.path.insert(0,str(r/'research/foundation_rebuild/"
            "ncp_shared_research_20260928/r4f_parallel_migration_20260929'));"
            "import continue_temporal,metric_transport,reference_transport,cr_repro.observables,a1_salvage,resource_census;"
            "m=(continue_temporal,metric_transport,reference_transport,cr_repro.observables,a1_salvage,resource_census);"
            "assert all(pathlib.Path(x.__file__).resolve().is_relative_to(r) for x in m);"
            "print([str(pathlib.Path(x.__file__).resolve().relative_to(r)) for x in m])"
        )
        imported = subprocess.run([str(python), "-B", "-c", source_check],
                                  cwd=root, env=env, text=True, capture_output=True,
                                  timeout=30)
        if imported.returncode:
            raise ValueError("extracted source import closure failed: " + imported.stderr[-2000:])
        command = [str(python)] + instructions["test_command"][1:]
        tested = subprocess.run(command, cwd=root, env=env, text=True,
                                capture_output=True, timeout=120)
        match = re.search(r"(\d+) passed in [\d.]+s", tested.stdout)
        if tested.returncode or not match or int(match.group(1)) != instructions["expected_passed"]:
            raise ValueError("extracted focused suite failed: " +
                             (tested.stdout + tested.stderr)[-4000:])
        if nonce.exists():
            raise ValueError("synthetic native-trap nonce was consumed")
        result = {"schema": "BASS_R4G_SELF_CONTAINED_TEST_REPLAY_V1",
                  "SELF_CONTAINED_TEST_REPLAY_VERIFIED": True,
                  "package_sha256": _sha(archive.read_bytes()),
                  "package_bytes": archive.stat().st_size,
                  "zip_crc": "PASS", "manifest_verified_files": len(manifest),
                  "pilot_authority_template_verified": True,
                  "a1_partial_fixture_sha256_verified": True,
                  "predecessor_fixture_sha256_verified": True,
                  "py_compile_command": compile_cmd,
                  "py_compile_exit": compiled.returncode,
                  "source_imports_relative_to_extracted_root": imported.stdout.strip(),
                  "test_command": command, "test_exit": tested.returncode,
                  "tests_passed": int(match.group(1)), "tests_failed": 0,
                  "tests_skipped": 0,
                  "launcher_parser_native_trap_in_suite": True,
                  "native_operator_calls": 0,
                  "authorization_nonce_consumed": False,
                  "external_PYTHONPATH_used": False}
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", required=True, type=Path)
    p.add_argument("--python", required=True, type=Path)
    p.add_argument("--receipt", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(verify(args.archive, args.python, args.receipt), indent=2))


if __name__ == "__main__":
    main()
