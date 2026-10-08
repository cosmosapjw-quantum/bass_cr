"""Read-only validation and byte-preserving admission of the stopped A1 cache."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from parallel_bridge import PlannedQuery, validate_pair

A1_AUTH = "R4G-N1536-ADAPTIVE-20260930-A1"
A1_COMMIT = "830b2849741f70078ac7bc779ee40c3f249c3fab"
A1_TREE = "922c976e5bb3aa8f6a87d96d482ea5b28e82eaf0"
A1_ARCHIVE_SHA256 = "82a8997ad57ad2a7dee70bce67bd0c5b2871df0ca4f23f04362bfb7f8e9b5b7e"
A1_ARCHIVE_BYTES = 51269880
A1_RAW_ATTEMPTS = 54
A1_CONSUMED_SHA256 = "436c15add837c8657cac06eed4f4f85627de40580678658e66a26e215813a45a"
A1_STAGE8_SHA256 = "275b485ef1d7cdac3d89490f57752eb74282e92fbd0e9465e2b7a247c2f25f37"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("A1 evidence JSON object required: " + str(path))
    return value


def validate_a1_partial(archive: Path, expected_sha256: str, destination: Path,
                        predecessor: Path, contract: dict,
                        required: list[PlannedQuery], pilot: dict,
                        context_id: str) -> dict:
    """Verify every archived byte and all 16 extra pairs before any import."""
    archive = Path(archive).resolve()
    destination = Path(destination)
    predecessor = Path(predecessor)
    if (expected_sha256 != A1_ARCHIVE_SHA256 or archive.stat().st_size != A1_ARCHIVE_BYTES
        or _sha(archive) != A1_ARCHIVE_SHA256):
        raise ValueError("A1 partial archive SHA256/size mismatch")
    if destination.exists():
        raise FileExistsError("A1 extraction target already exists")
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or z.testzip() is not None:
            raise ValueError("A1 partial ZIP CRC/duplicate failure")
        for info in z.infolist():
            p = Path(info.filename)
            if (p.is_absolute() or ".." in p.parts or "\\" in info.filename
                or ((info.external_attr >> 16) & 0o170000) == 0o120000):
                raise ValueError("unsafe A1 partial ZIP member")
        z.extractall(destination)
    manifest = _json(destination / "MANIFEST.json")
    if set(names) != set(manifest) | {"MANIFEST.json"} or len(manifest) != 4218:
        raise ValueError("A1 partial manifest membership/count mismatch")
    for rel, row in manifest.items():
        p = destination / rel
        if not p.is_file() or p.is_symlink() or p.stat().st_size != row["bytes"] or _sha(p) != row["sha256"]:
            raise ValueError("A1 partial manifest byte mismatch: " + rel)
    admission = _json(destination / "EXECUTION_ADMISSION.json")
    consumed = _json(destination / "AUTHORIZATION_CONSUMED.json")
    report = _json(destination / "RETURN_REPORT.json")
    supervisor = _json(destination / "SUPERVISOR_RECEIPT.json")
    stage8 = _json(destination / "STAGE_8.json")
    stage16 = _json(destination / "STAGE_16.json")
    stage32 = _json(destination / "STAGE_32.json")
    prior_pilot = _json(destination / "USEFUL_PILOT_PLAN.json")
    if (admission.get("authorization_id") != A1_AUTH
        or admission.get("execution_commit") != A1_COMMIT
        or admission.get("execution_tree") != A1_TREE
        or consumed.get("authorization_id") != A1_AUTH
        or consumed.get("state") != "CONSUMED_BEFORE_NATIVE_WORKERS"
        or consumed.get("execution_commit") != A1_COMMIT
        or consumed.get("execution_tree") != A1_TREE
        or _sha(destination / "AUTHORIZATION_CONSUMED.json") != A1_CONSUMED_SHA256):
        raise ValueError("A1 authorization/commit/tree lineage mismatch")
    if (report.get("status") != "N1536_EXECUTION_BLOCKED"
        or report.get("execution_head") != A1_COMMIT
        or report.get("execution_tree") != A1_TREE
        or report.get("first_failure") != {"type": "ValueError",
            "message": "competing BASS workload overlaps approved worker CPUs"}):
        raise ValueError("A1 first-failure evidence mismatch")
    if (supervisor.get("deadline_reached") is not False
        or supervisor.get("child_exit_status") != 2
        or supervisor.get("descendants_exited") is not True
        or supervisor.get("termination", {}).get("group_exited") is not True):
        raise ValueError("A1 supervisor exit evidence mismatch")
    if prior_pilot != pilot:
        raise ValueError("A1 pilot query IDs differ from exact successor plan")
    stage_ids = [row["query_ids"] for row in pilot["stages"]]
    if (stage8.get("workers") != 8 or stage8.get("query_ids") != stage_ids[0]
        or _sha(destination / "STAGE_8.json") != A1_STAGE8_SHA256
        or set(stage8.get("completed_query_ids", [])) != set(stage_ids[0])
        or stage8.get("completed_query_count") != 16
        or stage8.get("failed_query_count") != 0
        or stage8.get("failed_query_ids") != []
        or stage8.get("filesystem_publish_failures") != 0
        or stage8.get("raw_attempts_consumed") != A1_RAW_ATTEMPTS
        or stage8.get("wall_seconds") != 193.6389812209818
        or stage8.get("queries_per_second") != 0.08262799101251579):
        raise ValueError("A1 stage8 completion/telemetry mismatch")
    if (stage16.get("workers") != 16 or stage16.get("query_ids") != stage_ids[1]
        or stage16.get("completed_query_count") != 0
        or stage16.get("raw_attempts_consumed") != 0
        or stage16.get("resource_valid") is not False
        or stage16.get("failure") != "competing BASS workload overlaps approved worker CPUs"
        or stage32.get("workers") != 32 or stage32.get("query_ids") != stage_ids[2]
        or stage32.get("completed_query_count") != 0
        or stage32.get("failure") != "NOT_STARTED_AFTER_LOWER_STAGE_RESOURCE_REJECTION"):
        raise ValueError("A1 unstarted stage evidence mismatch")
    for rel in ("CANDIDATE_N1536.json", "CANDIDATE_N1536.npz",
                "TEMPORAL_PAIR_N768_N1536.json", "CACHE_ONLY_REPLAY_AUDIT.json",
                "FILL_STAGE.json"):
        if (destination / rel).exists():
            raise ValueError("A1 partial claims unperformed N1536 work: " + rel)
    qdir = destination / "runtime_queries"
    base = predecessor / "runtime_queries"
    ajson = {p.stem for p in qdir.glob("*.json")}
    anpz = {p.stem for p in qdir.glob("*.npz")}
    bjson = {p.stem for p in base.glob("*.json")}
    bnpz = {p.stem for p in base.glob("*.npz")}
    if (ajson != anpz or bjson != bnpz or len(ajson) != 2063
        or len(bjson) != 2047 or ajson - bjson != set(stage_ids[0])
        or bjson - ajson):
        raise ValueError("A1 partial canonical pair/orphan/extra count mismatch")
    for qid in sorted(bjson):
        for ext in (".json", ".npz"):
            if _sha(qdir / (qid + ext)) != _sha(base / (qid + ext)):
                raise ValueError("A1 base cache conflicts with predecessor: " + qid)
    by_id = {q.query_id: q for q in required}
    records = [validate_pair(qdir, by_id[qid], context_id, contract)
               for qid in stage_ids[0]]
    tasks = list((destination / "worker_tasks").glob("*/TASK_RECEIPT.json"))
    failures = list((destination / "worker_tasks").glob("*/TASK_FAILURE.json"))
    if (len(tasks) != 16 or failures
        or {p.parent.name for p in tasks} != set(stage_ids[0])
        or sum(_json(p)["raw_attempts"] for p in tasks) != A1_RAW_ATTEMPTS):
        raise ValueError("A1 worker task/raw-attempt evidence mismatch")
    ledger = destination / "global_budget" / "RESERVATIONS.jsonl"
    if sum(1 for _ in ledger.open()) != A1_RAW_ATTEMPTS:
        raise ValueError("A1 global raw reservation count mismatch")
    return {"schema": "BASS_R4K_A1_SALVAGE_MANIFEST_V1",
            "a1_archive_sha256": A1_ARCHIVE_SHA256,
            "a1_archive_bytes": A1_ARCHIVE_BYTES,
            "a1_execution_commit": A1_COMMIT, "a1_execution_tree": A1_TREE,
            "a1_authorization_id": A1_AUTH,
            "a1_admission_sha256": _sha(destination / "EXECUTION_ADMISSION.json"),
            "a1_consumed_sha256": _sha(destination / "AUTHORIZATION_CONSUMED.json"),
            "a1_report_sha256": _sha(destination / "RETURN_REPORT.json"),
            "a1_supervisor_sha256": _sha(destination / "SUPERVISOR_RECEIPT.json"),
            "a1_stage8_sha256": _sha(destination / "STAGE_8.json"),
            "a1_pilot_plan_sha256": _sha(destination / "USEFUL_PILOT_PLAN.json"),
            "predecessor_pairs": 2047, "canonical_pairs": 2063,
            "imported_ids": stage_ids[0], "imported_records": records,
            "new_midpoint_pairs": 16, "remaining_midpoint_ids": 1520,
            "a1_raw_attempts": A1_RAW_ATTEMPTS,
            "native_calls_in_repair_preflight": 0}


def resume_receipts(required: list[PlannedQuery], missing: list[PlannedQuery],
                    pilot: dict, salvage: dict, head: str, tree: str) -> tuple[dict, dict]:
    imported = set(salvage["imported_ids"])
    remaining = [q.query_id for q in missing if q.query_id not in imported]
    if (len(required) != 1538 or len(missing) != 1536 or len(imported) != 16
        or len(remaining) != 1520 or imported != set(pilot["stages"][0]["query_ids"])):
        raise ValueError("A2 resume query accounting mismatch")
    plan = {"schema": "BASS_R4K_N1536_RESUME_QUERY_PLAN_V1",
            "execution_commit": head, "execution_tree": tree,
            "a1_archive_sha256": A1_ARCHIVE_SHA256,
            "predecessor_pairs": 2047, "imported_a1_midpoint_ids": pilot["stages"][0]["query_ids"],
            "initial_canonical_pairs": 2063, "initial_exact_hits": 2,
            "remaining_midpoint_ids": remaining, "remaining_midpoint_count": 1520,
            "active_required_count": 1538, "eventual_union_count": 3583,
            "a1_raw_attempts": A1_RAW_ATTEMPTS, "lifetime_raw_cap": 16896,
            "strict_remaining_worst_raw": 1520 * 11,
            "strict_lifetime_worst_raw": A1_RAW_ATTEMPTS + 1520 * 11,
            "strict_lifetime_raw_margin": 16896 - A1_RAW_ATTEMPTS - 1520 * 11}
    continuation = {"schema": "BASS_R4K_A2_PILOT_CONTINUATION_V1",
                    "execution_commit": head, "execution_tree": tree,
                    "a1_stage8_sha256": salvage["a1_stage8_sha256"],
                    "historical_stage8": {"workers": 8, "query_ids": pilot["stages"][0]["query_ids"],
                                          "completed": 16, "wall_seconds": 193.6389812209818,
                                          "queries_per_second": 0.08262799101251579,
                                          "raw_attempts": 54},
                    "new_stages": pilot["stages"][1:],
                    "post_pilot_remaining_ids": pilot["remaining_ids"],
                    "no_stage8_reexecution": True, "successful_pilot_pairs_retained": True}
    return plan, continuation
