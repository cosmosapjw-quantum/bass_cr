#!/usr/bin/env python3
"""Create-only, non-native N1536 implementation handoff from verified bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
R4C = HERE.parent / "r4c_temporal_continuation"
for directory in (HERE, R4C):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from adaptive_workers import build_useful_pilot_plan
from successor import (CONTEXT_ID, NATIVE_BUILD_SHA256, NATIVE_LIBRARY_SHA256,
                       NATIVE_SOURCE_SHA256, PREDECESSOR_SHA256, plan_n1536, plan_receipts,
                       pilot_authority_fields, required_missing, validate_predecessor)
import continue_temporal as serial
from cr_repro.observables import projectile_speed_au
from execution_admission import check_native_build
from a1_salvage import (A1_ARCHIVE_SHA256, A1_ARCHIVE_BYTES, A1_AUTH,
                        A1_CONSUMED_SHA256, A1_STAGE8_SHA256,
                        resume_receipts, validate_a1_partial)

REPO = serial.REPO
TEST_FIXTURE_ARCHIVE = (
    "research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/"
    "tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip")
TEST_FIXTURE_SHA256 = "630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35"
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
    "a1_salvage.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/"
    "resource_census.py",
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
    "verify_preparation_package.py",
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
EXTRA_SOURCE_CLOSURE = (
    "cr_repro/__init__.py",
    "research/foundation_rebuild/src/bass_foundations/__init__.py",
    "research/foundation_rebuild/src/bass_foundations/kernels.py",
    "research/foundation_rebuild/tp2a_perf_20260926/paths.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "run_parallel_bridge.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "controlled_stop.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "supervise.py",
    "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/"
    "run_r4f_science.sh",
)
R4F_TESTS = tuple(str(p.relative_to(REPO)) for p in
                  sorted((HERE.parent / "r4f_parallel_migration_20260929" / "tests").glob("test_*.py")))
R4G_TESTS = tuple(str(p.relative_to(REPO)) for p in
                  sorted((HERE / "tests").glob("test_*.py")))
PORTABLE_A1 = "artifacts/R4G_A1_PARTIAL_RETURN.zip"
PORTABLE_PREDECESSOR = "artifacts/R4F_A2_PREDECESSOR_RETURN.zip"


def _put(path: Path, value: dict):
    serial.write_new(path, value)


def create_package(predecessor: Path, prior_partial: Path, build: Path, out: Path) -> dict:
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
        if serial.sha256_path(REPO / TEST_FIXTURE_ARCHIVE) != TEST_FIXTURE_SHA256:
            raise ValueError("portable focused-test fixture archive SHA256 mismatch")
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
        salvage = validate_a1_partial(prior_partial, A1_ARCHIVE_SHA256,
            Path(temp) / "a1_partial", source, contract, required, pilot, CONTEXT_ID)
        nonce = Path.home() / ".local/state/bass_r4g/authorizations" / (A1_AUTH + ".json")
        if not nonce.is_file() or serial.sha256_path(nonce) != A1_CONSUMED_SHA256:
            raise ValueError("A1 consumed nonce identity mismatch")
        resume, continuation = resume_receipts(required, missing, pilot, salvage, head, tree)
        _put(out / "A1_SALVAGE_MANIFEST.json", salvage)
        _put(out / "N1536_RESUME_QUERY_PLAN.json", resume)
        _put(out / "PILOT_CONTINUATION_PLAN.json", continuation)
        pins = {"schema": "BASS_R4G_N1536_SOURCE_PINS_V1",
                "execution_commit": head, "execution_tree": tree,
                "predecessor_archive_sha256": PREDECESSOR_SHA256,
                "predecessor_archive_bytes": Path(predecessor).stat().st_size,
                "predecessor_manifest_sha256": prior["manifest_sha256"],
                "predecessor_report_sha256": prior["report_sha256"],
                "predecessor_admission_sha256": prior["admission_sha256"],
                "a1_authorization_id": A1_AUTH,
                "a1_partial_archive_sha256": A1_ARCHIVE_SHA256,
                "a1_partial_archive_bytes": A1_ARCHIVE_BYTES,
                "a1_admission_sha256": salvage["a1_admission_sha256"],
                "a1_report_sha256": salvage["a1_report_sha256"],
                "a1_supervisor_sha256": salvage["a1_supervisor_sha256"],
                "a1_consumed_nonce_sha256": A1_CONSUMED_SHA256,
                "a1_stage8_sha256": A1_STAGE8_SHA256,
                "context_id": CONTEXT_ID,
                "native": native,
                "pinned_dependency_manifest_sha256":
                    serial.sha256_path(serial.HERE / "PINNED_DEPENDENCIES.json"),
                "pinned_dependency_count": len(dependency["actual"]),
                "query_plan_sha256": serial.sha256_path(out / "PROPOSED_N1536_QUERY_PLAN.json"),
                "useful_pilot_plan_sha256": serial.sha256_path(out / "USEFUL_PILOT_PLAN.json"),
                "a1_salvage_manifest_sha256": serial.sha256_path(out / "A1_SALVAGE_MANIFEST.json"),
                "resume_plan_sha256": serial.sha256_path(out / "N1536_RESUME_QUERY_PLAN.json"),
                "pilot_continuation_plan_sha256": serial.sha256_path(out / "PILOT_CONTINUATION_PLAN.json")}
        _put(out / "SOURCE_PINS.json", pins)
        policy = json.loads((HERE / "ADAPTIVE_WORKER_POLICY.json").read_text())
        pilot_fields = pilot_authority_fields(policy, pilot)
        template = {"schema": "BASS_R4G_N1536_FUTURE_AUTHORIZATION_TEMPLATE_V1",
                    "status": "NATIVE_AUTHORIZATION_PENDING",
                    "execution_commit": head, "execution_tree": tree,
                    "predecessor_archive_sha256": pins["predecessor_archive_sha256"],
                    "predecessor_manifest_sha256": pins["predecessor_manifest_sha256"],
                    "prior_authorization_id": A1_AUTH,
                    "prior_partial_archive_sha256": A1_ARCHIVE_SHA256,
                    "a1_stage8_sha256": A1_STAGE8_SHA256,
                    "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                    "query_plan_sha256": pins["query_plan_sha256"],
                    "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"],
                    "a1_salvage_manifest_sha256": pins["a1_salvage_manifest_sha256"],
                    "resume_plan_sha256": pins["resume_plan_sha256"],
                    "pilot_continuation_plan_sha256": pins["pilot_continuation_plan_sha256"],
                    **pilot_fields,
                    "hard_max_workers": policy["hard_max_workers"],
                    "per_worker_ram_bytes": policy["worker_ram_bytes"],
                    "minimum_total_worker_ram_cap_bytes": policy["maximum_stage_worker_ram_bytes"],
                    "total_worker_ram_cap_bytes": policy["maximum_stage_worker_ram_bytes"],
                    "minimum_live_available_bytes": policy["maximum_stage_worker_ram_bytes"] + (4 << 30),
                    "approved_cpu_list": "LIVE_CENSUS_AND_USER_APPROVAL_REQUIRED",
                    "cpu_order_semantics": "FIRST_8_THEN_FIRST_16_THEN_FIRST_32",
                    "fresh_authorization_id": "USER_APPROVAL_REQUIRED",
                    "lifetime_raw_attempt_cap": 16896,
                    "prior_a1_raw_attempts": 54,
                    "remaining_midpoint_queries": 1520,
                    "strict_remaining_worst_raw": 16720,
                    "strict_lifetime_worst_raw": 16774,
                    "strict_lifetime_raw_margin": 122,
                    "optional_parity": "NOT_INCLUDED_REQUIRES_SEPARATE_JUSTIFICATION",
                    "deadline_unix": "USER_APPROVAL_REQUIRED",
                    "wall_seconds": "USER_APPROVAL_REQUIRED",
                    "termination_grace_seconds": "USER_APPROVAL_REQUIRED",
                    "cost_scope": "USER_APPROVAL_REQUIRED",
                    "recommended_wall_seconds": 28800,
                    "recommended_termination_grace_seconds": 60,
                    "cumulative_a1_a2_cost_ceiling_krw_including_vat": "USER_APPROVAL_REQUIRED",
                    "recommended_keep_prior_cumulative_cost_ceiling_krw_including_vat": 40000,
                    "suggested_host_scope": "ONE_EXISTING_HIGH_CPU_G3_HOST_NO_NEW_VM_OR_RESIZE",
                    "no_native_authorization_conferred": True}
        _put(out / "FUTURE_AUTHORIZATION_TEMPLATE.json", template)
        closure = sorted(set(PACKAGE_FILES) | set(EXTRA_SOURCE_CLOSURE)
                         | {TEST_FIXTURE_ARCHIVE}
                         | set(R4F_TESTS) | set(R4G_TESTS)
                         | set(dependency["manifest"]["files"]))
        for rel in closure:
            serial.copy_new(REPO / rel, out / rel)
        serial.copy_new(prior_partial, out / PORTABLE_A1)
        serial.copy_new(predecessor, out / PORTABLE_PREDECESSOR)
        _put(out / "REPLAY_INSTRUCTIONS.json",
             {"schema": "BASS_R4G_PORTABLE_NON_NATIVE_REPLAY_V1",
              "test_command": [
                  "python", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                  "research/foundation_rebuild/ncp_shared_research_20260928/"
                  "r4f_parallel_migration_20260929/tests",
                  "research/foundation_rebuild/ncp_shared_research_20260928/"
                  "r4g_n768_to_n1536_20260929/tests"],
              "run_from": "EXTRACTED_PACKAGE_ROOT",
              "historical_test_fixture_sha256": TEST_FIXTURE_SHA256,
              "a1_partial_fixture_sha256": A1_ARCHIVE_SHA256,
              "predecessor_fixture_sha256": PREDECESSOR_SHA256,
              "expected_passed": 69,
              "external_repository_source_required": False,
              "native_science_authorized": False})
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
        return {"status": "R4K_A2_RESUME_IMPLEMENTATION_READY__LIVE_CENSUS_AND_FRESH_AUTHORIZATION_PENDING",
                "execution_commit": head, "execution_tree": tree,
                "package_path": str(archive), "package_bytes": archive.stat().st_size,
                "package_sha256": serial.sha256_path(archive),
                "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                "query_plan_sha256": pins["query_plan_sha256"],
                "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"],
                "a1_salvage_manifest_sha256": pins["a1_salvage_manifest_sha256"],
                "resume_plan_sha256": pins["resume_plan_sha256"],
                "pilot_continuation_plan_sha256": pins["pilot_continuation_plan_sha256"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predecessor-archive", required=True, type=Path)
    p.add_argument("--prior-partial-archive", required=True, type=Path)
    p.add_argument("--analytic-build", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(create_package(args.predecessor_archive, args.prior_partial_archive,
                                    args.analytic_build,
                                    args.out), indent=2))


if __name__ == "__main__":
    main()
