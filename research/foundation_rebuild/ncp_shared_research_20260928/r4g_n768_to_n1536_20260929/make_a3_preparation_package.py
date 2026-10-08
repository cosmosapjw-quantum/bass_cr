#!/usr/bin/env python3
"""Build a create-only, self-contained NON-NATIVE A3 fill-only handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
for directory in (HERE, HERE.parent / "r4f_parallel_migration_20260929",
                  HERE.parent / "r4c_temporal_continuation"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import continue_temporal as serial
from adaptive_workers import build_useful_pilot_plan
from a1_salvage import A1_ARCHIVE_SHA256, A1_AUTH, validate_a1_partial
from a2_salvage import (A2_ARCHIVE_SHA256, A2_AUTH, A2_EVIDENCE_SHA256,
                        LIFETIME_RAW, a3_resume_receipts, validate_a2_partial)
from cr_repro.observables import projectile_speed_au
from execution_admission import check_native_build
from make_preparation_package import (EXTRA_SOURCE_CLOSURE, PACKAGE_FILES,
                                      TEST_FIXTURE_ARCHIVE, TEST_FIXTURE_SHA256)
from successor import (CONTEXT_ID, NATIVE_BUILD_SHA256, NATIVE_LIBRARY_SHA256,
                       NATIVE_SOURCE_SHA256, PREDECESSOR_SHA256, plan_n1536,
                       plan_receipts, required_missing, validate_predecessor)

REPO = serial.REPO
CORE = "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929"
NEW_FILES = tuple(CORE + "/" + name for name in (
    "RESOURCE_SHARING_POLICY.json", "a2_salvage.py", "run_a3.py",
    "run_a3_science.sh", "supervise_a3.py", "make_a3_preparation_package.py",
    "verify_a3_preparation_package.py"))


def create_package(predecessor: Path, a1_archive: Path, a2_archive: Path,
                   build: Path, out: Path, expected_tests: int) -> dict:
    predecessor, a1_archive, a2_archive = map(lambda x: Path(x).resolve(),
                                              (predecessor, a1_archive, a2_archive))
    out = Path(out).resolve()
    if out.exists() or out.with_name(out.name + ".zip").exists():
        raise FileExistsError("A3 preparation output must be create-only")
    head, tree = serial.git_identity()
    if (not head or subprocess.check_output(["git", "-C", str(REPO), "status",
                                              "--porcelain", "--untracked-files=all"], text=True)
        or out.is_relative_to(REPO)):
        raise ValueError("A3 package requires exact clean commit and external output")
    if serial.sha256_path(REPO / TEST_FIXTURE_ARCHIVE) != TEST_FIXTURE_SHA256:
        raise ValueError("historical focused fixture SHA mismatch")
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="bass_r4m_pack_") as tmp:
        tmp = Path(tmp)
        source, a1, a2 = tmp / "predecessor", tmp / "a1", tmp / "a2"
        prior = validate_predecessor(predecessor, PREDECESSOR_SHA256, source)
        contract = prior["contract"]
        native = check_native_build(build, contract, serial.ANALYTIC / "moment_kernel.cpp")
        if (native["source_sha256"] != NATIVE_SOURCE_SHA256
            or native["library_sha256"] != NATIVE_LIBRARY_SHA256
            or native["build_receipt_sha256"] != NATIVE_BUILD_SHA256):
            raise ValueError("frozen native source/library/BUILD hash mismatch")
        deps = serial.verify_pinned_dependencies()
        v = projectile_speed_au(contract["energy_keV_per_u"])
        required = plan_n1536(CONTEXT_ID, contract["z_initial_a0"] / v,
                              contract["z_final_a0"] / v)
        present = {p.stem for p in (source / "runtime_queries").glob("*.json")}
        missing = required_missing(required, present)
        stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
        plan, pilot = plan_receipts(required, missing, stages, remainder, head, tree)
        serial.write_new(out / "PROPOSED_N1536_QUERY_PLAN.json", plan)
        serial.write_new(out / "USEFUL_PILOT_PLAN.json", pilot)
        validate_a1_partial(a1_archive, A1_ARCHIVE_SHA256, a1, source,
                            contract, required, pilot, CONTEXT_ID)
        salvage = validate_a2_partial(a2_archive, A2_ARCHIVE_SHA256, a2,
                                      source, a1, contract, required, pilot, CONTEXT_ID)
        old_nonce = Path.home() / ".local/state/bass_r4g/authorizations" / (A2_AUTH + ".json")
        if (not old_nonce.is_file() or serial.sha256_path(old_nonce) !=
            A2_EVIDENCE_SHA256["AUTHORIZATION_CONSUMED.json"]):
            raise ValueError("A2 consumed nonce identity mismatch")
        fill, selected = a3_resume_receipts(required, missing, pilot, salvage, head, tree)
        serial.write_new(out / "A2_CUMULATIVE_SALVAGE_MANIFEST.json", salvage)
        serial.write_new(out / "N1536_REMAINING_FILL_PLAN.json", fill)
        serial.write_new(out / "A2_SELECTED_STAGE_EVIDENCE.json", selected)
        policy_sha = serial.sha256_path(HERE / "RESOURCE_SHARING_POLICY.json")
        pins = {"schema": "BASS_R4M_A3_SOURCE_PINS_V1",
                "execution_commit": head, "execution_tree": tree,
                "predecessor_archive_sha256": PREDECESSOR_SHA256,
                "predecessor_manifest_sha256": prior["manifest_sha256"],
                "a1_archive_sha256": A1_ARCHIVE_SHA256,
                "a2_archive_sha256": A2_ARCHIVE_SHA256,
                "a2_evidence_sha256": A2_EVIDENCE_SHA256,
                "a2_consumed_nonce_sha256": A2_EVIDENCE_SHA256["AUTHORIZATION_CONSUMED.json"],
                "context_id": CONTEXT_ID, "native": native,
                "resource_sharing_policy": "COOPERATIVE_SHARED_HOST",
                "resource_policy_sha256": policy_sha,
                "pinned_dependency_manifest_sha256":
                    serial.sha256_path(serial.HERE / "PINNED_DEPENDENCIES.json"),
                "pinned_dependency_count": len(deps["actual"]),
                "query_plan_sha256": serial.sha256_path(out / "PROPOSED_N1536_QUERY_PLAN.json"),
                "useful_pilot_plan_sha256": serial.sha256_path(out / "USEFUL_PILOT_PLAN.json"),
                "salvage_manifest_sha256": serial.sha256_path(out / "A2_CUMULATIVE_SALVAGE_MANIFEST.json"),
                "fill_plan_sha256": serial.sha256_path(out / "N1536_REMAINING_FILL_PLAN.json"),
                "selected_stage_sha256": serial.sha256_path(out / "A2_SELECTED_STAGE_EVIDENCE.json")}
        serial.write_new(out / "SOURCE_PINS.json", pins)
        template = {"schema": "BASS_R4M_A3_FUTURE_AUTHORIZATION_TEMPLATE_V1",
                    "status": "NATIVE_AUTHORIZATION_PENDING",
                    "execution_commit": head, "execution_tree": tree,
                    "predecessor_authorization_id":
                        "R4F-N768-MIGRATION-REPAIR-20260929-A2",
                    "a1_authorization_id": A1_AUTH,
                    "prior_authorization_id": A2_AUTH,
                    "predecessor_archive_sha256": PREDECESSOR_SHA256,
                    "a1_partial_archive_sha256": A1_ARCHIVE_SHA256,
                    "a2_partial_archive_sha256": A2_ARCHIVE_SHA256,
                    "a2_consumed_nonce_sha256":
                        A2_EVIDENCE_SHA256["AUTHORIZATION_CONSUMED.json"],
                    "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                    "query_plan_sha256": pins["query_plan_sha256"],
                    "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"],
                    "salvage_manifest_sha256": pins["salvage_manifest_sha256"],
                    "fill_plan_sha256": pins["fill_plan_sha256"],
                    "selected_stage_sha256": pins["selected_stage_sha256"],
                    "resource_policy_sha256": policy_sha,
                    "resource_sharing_policy": "COOPERATIVE_SHARED_HOST",
                    "selected_workers": 32, "pilot_queries_reused": 112,
                    "pilot_queries_to_run": 0, "remaining_midpoint_queries": 1424,
                    "approved_cpu_list": "LIVE_CENSUS_AND_USER_APPROVAL_REQUIRED",
                    "worker_ram_bytes": 1 << 30,
                    "total_worker_ram_cap_bytes": 32 << 30,
                    "minimum_live_available_bytes": 36 << 30,
                    "prior_raw_attempts": LIFETIME_RAW,
                    "lifetime_raw_attempt_cap": 16896,
                    "strict_remaining_worst_raw": 1424 * 11,
                    "strict_lifetime_worst_raw": LIFETIME_RAW + 1424 * 11,
                    "lifetime_raw_margin": 16896 - LIFETIME_RAW - 1424 * 11,
                    "native_parity": "NONE",
                    "fresh_authorization_id": "USER_APPROVAL_REQUIRED",
                    "deadline_unix": "USER_APPROVAL_REQUIRED",
                    "wall_seconds": "USER_APPROVAL_REQUIRED",
                    "termination_grace_seconds": "USER_APPROVAL_REQUIRED",
                    "cost_scope": "USER_APPROVAL_REQUIRED",
                    "recommended_wall_seconds": 21600,
                    "recommended_termination_grace_seconds": 60,
                    "recommended_a1_a2_a3_cumulative_cost_ceiling_krw_including_vat": 40000,
                    "suggested_host_scope": "ONE_EXISTING_HIGH_CPU_G3_HOST_NO_NEW_VM_OR_RESIZE",
                    "no_native_authorization_conferred": True}
        serial.write_new(out / "FUTURE_AUTHORIZATION_TEMPLATE.json", template)
        tests = tuple(str(p.relative_to(REPO)) for p in sorted(
            (HERE.parent / "r4f_parallel_migration_20260929/tests").glob("test_*.py"))) + tuple(
            str(p.relative_to(REPO)) for p in sorted((HERE / "tests").glob("test_*.py")))
        closure = sorted(set(PACKAGE_FILES) | set(EXTRA_SOURCE_CLOSURE) |
                         set(NEW_FILES) | set(tests) | {TEST_FIXTURE_ARCHIVE} |
                         set(deps["manifest"]["files"]))
        for rel in closure:
            serial.copy_new(REPO / rel, out / rel)
        for path, name in ((predecessor, "R4F_A2_PREDECESSOR_RETURN.zip"),
                           (a1_archive, "R4G_A1_PARTIAL_RETURN.zip"),
                           (a2_archive, "R4K_A2_PARTIAL_RETURN.zip")):
            serial.copy_new(path, out / "artifacts" / name)
        serial.write_new(out / "REPLAY_INSTRUCTIONS.json",
            {"schema": "BASS_R4M_A3_PORTABLE_NON_NATIVE_REPLAY_V1",
             "test_command": ["python", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/tests",
               "research/foundation_rebuild/ncp_shared_research_20260928/r4g_n768_to_n1536_20260929/tests"],
             "expected_passed": expected_tests,
             "predecessor_sha256": PREDECESSOR_SHA256,
             "a1_sha256": A1_ARCHIVE_SHA256, "a2_sha256": A2_ARCHIVE_SHA256,
             "resource_policy_sha256": policy_sha,
             "external_repository_source_required": False,
             "native_science_authorized": False})
        files = {}
        for path in sorted(out.rglob("*")):
            if path.is_file():
                files[str(path.relative_to(out))] = {
                    "bytes": path.stat().st_size, "sha256": serial.sha256_path(path)}
        serial.write_new(out / "MANIFEST.json", files)
        archive = out.with_name(out.name + ".zip")
        with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(out.rglob("*")):
                if path.is_file():
                    bundle.write(path, str(path.relative_to(out)))
        with zipfile.ZipFile(archive) as bundle:
            if bundle.testzip() is not None:
                raise ValueError("A3 preparation package ZIP CRC failure")
        return {"status": "R4M_A3_SHARED_HOST_RESUME_IMPLEMENTATION_READY__LIVE_CENSUS_AND_FRESH_AUTH_PENDING",
                "execution_commit": head, "execution_tree": tree,
                "package_path": str(archive), "package_bytes": archive.stat().st_size,
                "package_sha256": serial.sha256_path(archive),
                "source_pins_sha256": serial.sha256_path(out / "SOURCE_PINS.json"),
                "query_plan_sha256": pins["query_plan_sha256"],
                "useful_pilot_plan_sha256": pins["useful_pilot_plan_sha256"],
                "salvage_manifest_sha256": pins["salvage_manifest_sha256"],
                "fill_plan_sha256": pins["fill_plan_sha256"],
                "selected_stage_sha256": pins["selected_stage_sha256"],
                "resource_policy_sha256": policy_sha}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("predecessor-archive", "a1-partial-archive", "a2-partial-archive",
                 "analytic-build", "out"):
        p.add_argument("--" + name, required=True, type=Path)
    p.add_argument("--expected-tests", type=int, required=True)
    args = p.parse_args()
    print(json.dumps(create_package(args.predecessor_archive, args.a1_partial_archive,
                                    args.a2_partial_archive, args.analytic_build,
                                    args.out, args.expected_tests), indent=2))


if __name__ == "__main__":
    main()
