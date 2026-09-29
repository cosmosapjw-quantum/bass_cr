#!/usr/bin/env python3
"""Create-only, non-native N1536 implementation handoff from verified bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

from adaptive_workers import build_useful_pilot_plan
from successor import (CONTEXT_ID, NATIVE_BUILD_SHA256, NATIVE_LIBRARY_SHA256,
                       NATIVE_SOURCE_SHA256, PREDECESSOR_SHA256, plan_n1536, plan_receipts,
                       required_missing, validate_predecessor)
import continue_temporal as serial
from cr_repro.observables import projectile_speed_au
from execution_admission import check_native_build

HERE = Path(__file__).resolve().parent
REPO = serial.REPO
PACKAGE_FILES = (
    "AGENTS.md",
    "docs/READBACK_POLICY.md",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "CODEX_HANDOFF_N1536_ADAPTIVE_WORKERS_KO.md",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "R4G_RESEARCH_AND_HANDOFF_KO.md",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "ADAPTIVE_WORKER_POLICY.json",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "adaptive_workers.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "successor.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "run_n1536.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "run_n1536_science.sh",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "supervise_n1536.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "make_preparation_package.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "IMPLEMENTATION_HANDOFF_KO.md",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "tests/test_adaptive_workers.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "tests/test_successor.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "parallel_bridge.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "worker_runtime.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation/"
    "continue_temporal.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation/"
    "execution_admission.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation/"
    "PINNED_DEPENDENCIES.json",
    "research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/"
    "qualified_provider.py",
    "research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/"
    "transport_policy.py",
    "research/foundation_rebuild/tp1_short_transport_20260926/metric_transport.py",
)


def _put(path: Path, value: dict):
    serial.write_new(path, value)


def create_package(predecessor: Path, build: Path, out: Path) -> dict:
    out = Path(out).resolve()
    if out.exists() or out.with_name(out.name + ".zip").exists():
        raise FileExistsError("create-only preparation output already exists")
    head, tree = serial.git_identity()
    if not head or subprocess.check_output(
        ["git", "-C", str(REPO), "status", "--porcelain", "--untracked-files=all"], text=True
    ):
        raise ValueError("exact clean implementation commit required for package")
    if out.is_relative_to(REPO):
        raise ValueError("package output must be outside source worktree")
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="bass_r4g_pack_") as temp:
        source = Path(temp) / "source"
        prior = validate_predecessor(predecessor, PREDECESSOR_SHA256, source)
        native = check_native_build(build, prior["contract"], serial.ANALYTIC / "moment_kernel.cpp")
        if (native["source_sha256"] != NATIVE_SOURCE_SHA256
            or native["library_sha256"] != NATIVE_LIBRARY_SHA256
            or native["build_receipt_sha256"] != NATIVE_BUILD_SHA256):
            raise ValueError("frozen native source/library/BUILD hash mismatch")
        dependency = serial.verify_pinned_dependencies()
        contract = prior["contract"]
        v = projectile_speed_au(contract["energy_keV_per_u"])
        required = plan_n1536(CONTEXT_ID, contract["z_initial_a0"] / v,
                              contract["z_final_a0"] / v)
        present = {p.stem for p in (source / "runtime_queries").glob("*.json")}
        missing = required_missing(required, present)
        stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
        plan, pilot = plan_receipts(required, missing, stages, remainder, head, tree)
        _put(out / "PROPOSED_N1536_QUERY_PLAN.json", plan)
        _put(out / "USEFUL_PILOT_PLAN.json", pilot)
        pins = {"schema": "BASS_R4G_N1536_SOURCE_PINS_V1",
                "execution_commit": head, "execution_tree": tree,
                "predecessor_archive_sha256": PREDECESSOR_SHA256,
                "predecessor_archive_bytes": Path(predecessor).stat().st_size,
                "predecessor_manifest_sha256": prior["manifest_sha256"],
                "predecessor_report_sha256": prior["report_sha256"],
                "predecessor_admission_sha256": prior["admission_sha256"],
                "context_id": CONTEXT_ID,
                "native": native,
                "pinned_dependency_manifest_sha256":
                    serial.sha256_path(serial.HERE / "PINNED_DEPENDENCIES.json"),
                "pinned_dependency_count": len(dependency["actual"]),
                "query_plan_sha256": serial.sha256_path(out / "PROPOSED_N1536_QUERY_PLAN.json"),
                "useful_pilot_plan_sha256": serial.sha256_path(out / "USEFUL_PILOT_PLAN.json")}
        _put(out / "SOURCE_PINS.json", pins)
        policy = json.loads((HERE / "ADAPTIVE_WORKER_POLICY.json").read_text())
        template = {"schema": "BASS_R4G_N1536_FUTURE_AUTHORIZATION_TEMPLATE_V1",
                    "status": "NATIVE_AUTHORIZATION_PENDING",
                    "execution_commit": head, "execution_tree": tree,
                    "predecessor_archive_sha256": pins["predecessor_archive_sha256"],
                    "predecessor_manifest_sha256": pins["predecessor_manifest_sha256"],
                    "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                    "query_plan_sha256": pins["query_plan_sha256"],
                    "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"],
                    "worker_stages": policy["stages"],
                    "hard_max_workers": policy["hard_max_workers"],
                    "per_worker_ram_bytes": policy["worker_ram_bytes"],
                    "minimum_total_worker_ram_cap_bytes": policy["maximum_stage_worker_ram_bytes"],
                    "approved_cpu_list": "USER_APPROVAL_REQUIRED",
                    "fresh_authorization_id": "USER_APPROVAL_REQUIRED",
                    "incremental_raw_attempt_cap_proposal": 16896,
                    "optional_parity": "NOT_INCLUDED_REQUIRES_SEPARATE_JUSTIFICATION",
                    "deadline_unix": "USER_APPROVAL_REQUIRED",
                    "wall_seconds": "USER_APPROVAL_REQUIRED",
                    "termination_grace_seconds": "USER_APPROVAL_REQUIRED",
                    "cost_scope": "USER_APPROVAL_REQUIRED",
                    "no_native_authorization_conferred": True}
        _put(out / "FUTURE_AUTHORIZATION_TEMPLATE.json", template)
        for rel in PACKAGE_FILES:
            serial.copy_new(REPO / rel, out / rel)
        files = {}
        for p in sorted(out.rglob("*")):
            if p.is_file():
                files[str(p.relative_to(out))] = {
                    "bytes": p.stat().st_size, "sha256": serial.sha256_path(p)}
        _put(out / "MANIFEST.json", files)
        archive = out.with_name(out.name + ".zip")
        with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob("*")):
                if p.is_file():
                    z.write(p, str(p.relative_to(out)))
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError("preparation archive CRC failed")
        return {"status": "N1536_ADAPTIVE_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING",
                "execution_commit": head, "execution_tree": tree,
                "package_path": str(archive), "package_bytes": archive.stat().st_size,
                "package_sha256": serial.sha256_path(archive),
                "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                "query_plan_sha256": pins["query_plan_sha256"],
                "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predecessor-archive", required=True, type=Path)
    p.add_argument("--analytic-build", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(create_package(args.predecessor_archive, args.analytic_build,
                                    args.out), indent=2))


if __name__ == "__main__":
    main()
