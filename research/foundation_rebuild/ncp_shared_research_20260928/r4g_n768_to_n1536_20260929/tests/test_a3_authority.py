"""A3 fill-only authorization and non-native launcher boundaries."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
for directory in (HERE, HERE.parent / "r4f_parallel_migration_20260929",
                  HERE.parent / "r4c_temporal_continuation"):
    sys.path.insert(0, str(directory))


def test_a3_policy_is_explicit_cooperative_and_pinned():
    policy = json.loads((HERE / "RESOURCE_SHARING_POLICY.json").read_text())
    assert policy["effective_mode"] == "COOPERATIVE_SHARED_HOST"
    assert policy["external_affinity_overlap"] == "TELEMETRY_ONLY"
    assert policy["own_pool_teardown"] == "HARD_BLOCK"
    assert policy["cpu_pressure"] == "DIAGNOSTIC_ONLY"


def test_a3_launcher_and_parser_trap_do_not_consume_nonce(tmp_path):
    module = importlib.import_module("run_a3")
    launcher = HERE / "run_a3_science.sh"
    env = os.environ.copy()
    env.pop("ALLOW_NEW_NATIVE_R4M", None)
    result = subprocess.run(["bash", str(launcher), str(tmp_path / "out")],
                            env=env, text=True, capture_output=True)
    assert result.returncode == 64
    assert "A3_NATIVE_NOT_AUTHORIZED" in result.stderr
    nonce = Path.home() / ".local/state/bass_r4m/authorizations/R4G-N1536-A3-SYNTHETIC-TRAP.json"
    assert not nonce.exists()
    args = module.parse_args([
        "--out", str(tmp_path / "out"),
        "--predecessor-archive", "/unused-predecessor.zip",
        "--expected-predecessor-sha256", "a"*64,
        "--a1-partial-archive", "/unused-a1.zip",
        "--expected-a1-sha256", "b"*64,
        "--a2-partial-archive", "/unused-a2.zip",
        "--expected-a2-sha256", "c"*64,
        "--source-pins", "/unused-pins.json",
        "--expected-source-pins-sha256", "d"*64,
        "--expected-query-plan-sha256", "e"*64,
        "--expected-useful-pilot-plan-sha256", "f"*64,
        "--expected-salvage-manifest-sha256", "1"*64,
        "--expected-fill-plan-sha256", "2"*64,
        "--expected-selected-stage-sha256", "3"*64,
        "--resource-policy", "/unused-policy.json",
        "--expected-resource-policy-sha256", "4"*64,
        "--resource-sharing-policy", "COOPERATIVE_SHARED_HOST",
        "--authorization-id", "R4G-N1536-A3-SYNTHETIC-TRAP",
        "--prior-authorization-id", "R4G-N1536-ADAPTIVE-RESUME-20260930-A2",
        "--expected-commit", "a"*40, "--expected-tree", "b"*40,
        "--analytic-build", "/unused-build", "--deadline-unix", "9999999999",
        "--max-wall-seconds", "21600", "--workers", "32",
        "--cpus", ",".join(map(str,range(32))),
        "--worker-ram-bytes", str(1<<30),
        "--total-worker-ram-cap-bytes", str(32<<30),
        "--global-raw-attempt-cap", "16896",
        "--cost-scope", "synthetic non-native scope"])
    assert args.workers == 32 and args.resource_sharing_policy == "COOPERATIVE_SHARED_HOST"
    with pytest.raises(PermissionError, match="A3_NATIVE_NOT_AUTHORIZED"):
        module.admission_scope(args)
    assert not nonce.exists()
