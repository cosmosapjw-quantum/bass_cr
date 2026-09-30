"""Read-only A2 partial admission and exact fill-only A3 query accounting."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from parallel_bridge import PlannedQuery, validate_pair

A2_AUTH = "R4G-N1536-ADAPTIVE-RESUME-20260930-A2"
A2_COMMIT = "1f18e871ff5929ec8f231597c845b833ea485e2b"
A2_TREE = "4495579b08f5950751a139725cd347f3dbdafc65"
A2_ARCHIVE_SHA256 = "5cf950123996a4d2a1c07868fc74ae2d116acfd2a565ee9be62ef22d846f2b98"
A2_ARCHIVE_BYTES = 55748349
A2_EVIDENCE_SHA256 = {
    "AUTHORIZATION_CONSUMED.json": "839ea98d472fccf8febf4bcc6cbd92ab612857aa38a9f6811a2dbc142355c765",
    "STAGE_16.json": "aa517ddfa129c8d25192afce1bdb38f45000802a70413e992a0707a467b33736",
    "STAGE_32.json": "2003319bca3ed250405b85fad8e6f24cc1f5741da7c005d0423615acdb300cc7",
    "ADAPTIVE_SELECTION.json": "8270ff48fa50976426736e8d08a4a23fc8a3a3c46035c3f76f8cc55592744f54",
    "RESOURCE_CENSUS_FILL_32.json": "d7fda6708d6969f86b7336cec723a53c2b8a8df19befacb7d9b7292bcd42cf60",
    "RETURN_REPORT.json": "87e5420c847acd62f04f40b71f06e13a01269efd9d94f628b440101e1abd309f",
    "SUPERVISOR_RECEIPT.json": "dfcac3505b0324d7f9592167288221bee7f2c1cf7874baab5429c2f628590abb",
}
A2_NEW_RAW = 104 + 210
LIFETIME_RAW = 54 + A2_NEW_RAW


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("A2 evidence JSON object required: " + str(path))
    return value


def validate_a2_partial(archive: Path, expected_sha256: str, destination: Path,
                        predecessor: Path, a1: Path, contract: dict,
                        required: list[PlannedQuery], pilot: dict,
                        context_id: str) -> dict:
    """Admit only the byte-pinned 2159-pair A2 partial; never infer completion."""
    archive = Path(archive).resolve()
    destination = Path(destination)
    predecessor = Path(predecessor)
    a1 = Path(a1)
    if (expected_sha256 != A2_ARCHIVE_SHA256 or archive.stat().st_size != A2_ARCHIVE_BYTES
        or _sha(archive) != A2_ARCHIVE_SHA256):
        raise ValueError("A2 partial archive SHA256/size mismatch")
    if destination.exists():
        raise FileExistsError("A2 extraction target already exists")
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or bundle.testzip() is not None:
            raise ValueError("A2 partial ZIP CRC/duplicate failure")
        for info in bundle.infolist():
            part = Path(info.filename)
            if (part.is_absolute() or ".." in part.parts or "\\" in info.filename
                or ((info.external_attr >> 16) & 0o170000) == 0o120000):
                raise ValueError("unsafe A2 partial ZIP member")
        bundle.extractall(destination)
    manifest = _json(destination / "MANIFEST.json")
    if set(names) != set(manifest) | {"MANIFEST.json"} or len(manifest) != 4739:
        raise ValueError("A2 partial manifest membership/count mismatch")
    for rel, row in manifest.items():
        path = destination / rel
        if (not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"]
            or _sha(path) != row["sha256"]):
            raise ValueError("A2 partial manifest byte mismatch: " + rel)
    for name, expected in A2_EVIDENCE_SHA256.items():
        if _sha(destination / name) != expected:
            raise ValueError("A2 immutable evidence SHA256 mismatch: " + name)
    admission = _json(destination / "EXECUTION_ADMISSION.json")
    consumed = _json(destination / "AUTHORIZATION_CONSUMED.json")
    report = _json(destination / "RETURN_REPORT.json")
    supervisor = _json(destination / "SUPERVISOR_RECEIPT.json")
    stage8 = _json(destination / "STAGE_8.json")
    stage16 = _json(destination / "STAGE_16.json")
    stage32 = _json(destination / "STAGE_32.json")
    selection = _json(destination / "ADAPTIVE_SELECTION.json")
    fill_census = _json(destination / "RESOURCE_CENSUS_FILL_32.json")
    prior_pilot = _json(destination / "USEFUL_PILOT_PLAN.json")
    if (admission.get("authorization_id") != A2_AUTH
        or consumed.get("authorization_id") != A2_AUTH
        or consumed.get("state") != "CONSUMED_BEFORE_NATIVE_WORKERS"
        or any(row.get("execution_commit") != A2_COMMIT or row.get("execution_tree") != A2_TREE
               for row in (admission, consumed))
        or admission.get("prior_failed_authorization_id") != "R4G-N1536-ADAPTIVE-20260930-A1"
        or admission.get("prior_partial_archive_sha256") !=
           "82a8997ad57ad2a7dee70bce67bd0c5b2871df0ca4f23f04362bfb7f8e9b5b7e"):
        raise ValueError("A2 authorization/commit/tree/A1 lineage mismatch")
    if (report.get("status") != "N1536_EXECUTION_BLOCKED"
        or report.get("execution_head") != A2_COMMIT or report.get("execution_tree") != A2_TREE
        or report.get("first_failure", {}).get("type") != "ExternalResourceOverlap"
        or "EXTERNAL_BASS_CPU_OVERLAP: 276112,276115" not in
           report.get("first_failure", {}).get("message", "")):
        raise ValueError("A2 first-failure evidence mismatch")
    if (supervisor.get("deadline_reached") is not False
        or supervisor.get("child_exit_status") != 2
        or supervisor.get("descendants_exited") is not True
        or supervisor.get("termination", {}).get("group_exited") is not True):
        raise ValueError("A2 supervisor exit evidence mismatch")
    if (fill_census.get("status") != "EXTERNAL_BASS_CPU_OVERLAP"
        or fill_census.get("external_offender_pids") != [276112, 276115]
        or any(p.get("ownership") != "EXTERNAL" for p in fill_census.get("candidate_processes", []))):
        raise ValueError("A2 fill resource failure evidence mismatch")
    if prior_pilot != pilot:
        raise ValueError("A2 pilot plan differs from exact N1536 plan")
    ids8, ids16, ids32 = [row["query_ids"] for row in pilot["stages"]]
    if (stage8 != _json(a1 / "STAGE_8.json")
        or stage16.get("workers") != 16 or stage32.get("workers") != 32
        or stage16.get("query_ids") != ids16 or stage32.get("query_ids") != ids32
        or set(stage16.get("completed_query_ids", [])) != set(ids16)
        or set(stage32.get("completed_query_ids", [])) != set(ids32)
        or stage16.get("completed_query_count") != 32
        or stage32.get("completed_query_count") != 64
        or stage16.get("failed_query_count") != 0 or stage32.get("failed_query_count") != 0
        or stage16.get("filesystem_publish_failures") != 0
        or stage32.get("filesystem_publish_failures") != 0
        or stage16.get("raw_attempts_consumed") != 104
        or stage32.get("raw_attempts_consumed") != 210
        or selection.get("selected_workers") != 32
        or selection.get("remaining_query_count") != 1424):
        raise ValueError("A2 completed pilots/adaptive selection mismatch")
    for name in ("CANDIDATE_N1536.json", "CANDIDATE_N1536.npz",
                 "TEMPORAL_PAIR_N768_N1536.json", "CACHE_ONLY_REPLAY_AUDIT.json",
                 "FILL_STAGE.json", "STAGE_16_FAILURE.json", "STAGE_32_FAILURE.json"):
        if (destination / name).exists():
            raise ValueError("A2 partial claims unperformed work: " + name)
    query_dir = destination / "runtime_queries"
    base_dir = predecessor / "runtime_queries"
    a1_dir = a1 / "runtime_queries"
    json_ids = {p.stem for p in query_dir.glob("*.json")}
    npz_ids = {p.stem for p in query_dir.glob("*.npz")}
    base_ids = {p.stem for p in base_dir.glob("*.json")}
    if (json_ids != npz_ids or len(json_ids) != 2159 or len(base_ids) != 2047
        or json_ids - base_ids != set(ids8) | set(ids16) | set(ids32)
        or base_ids - json_ids):
        raise ValueError("A2 canonical pair/orphan/extra count mismatch")
    for qid in sorted(base_ids | set(ids8)):
        original = base_dir if qid in base_ids else a1_dir
        for ext in (".json", ".npz"):
            if _sha(query_dir / (qid + ext)) != _sha(original / (qid + ext)):
                raise ValueError("A2 canonical pair conflicts with predecessor/A1: " + qid)
    by_id = {q.query_id: q for q in required}
    imported_ids = ids8 + ids16 + ids32
    records = [validate_pair(query_dir, by_id[qid], context_id, contract)
               for qid in imported_ids]
    task_receipts = sorted((destination / "worker_tasks").glob("*/TASK_RECEIPT.json"))
    task_failures = list((destination / "worker_tasks").glob("*/TASK_FAILURE.json"))
    if (len(task_receipts) != 96 or task_failures
        or {p.parent.name for p in task_receipts} != set(ids16) | set(ids32)
        or sum(_json(p)["raw_attempts"] for p in task_receipts) != A2_NEW_RAW):
        raise ValueError("A2 completed worker task/raw-attempt mismatch")
    seed = _json(destination / "global_budget" / "SEED.json")
    ledger = (destination / "global_budget" / "RESERVATIONS.jsonl").read_text().splitlines()
    if (seed.get("parent_raw_attempts") != 54 or seed.get("maximum") != 16896
        or len(ledger) != A2_NEW_RAW
        or [json.loads(line)["global_attempt"] for line in ledger]
           != list(range(55, LIFETIME_RAW + 1))):
        raise ValueError("A2 cumulative global raw reservation mismatch")
    return {"schema": "BASS_R4M_A2_CUMULATIVE_SALVAGE_V1",
            "a2_archive_sha256": A2_ARCHIVE_SHA256, "a2_archive_bytes": A2_ARCHIVE_BYTES,
            "a2_execution_commit": A2_COMMIT, "a2_execution_tree": A2_TREE,
            "a2_authorization_id": A2_AUTH,
            "a2_admission_sha256": _sha(destination / "EXECUTION_ADMISSION.json"),
            "a2_evidence_sha256": A2_EVIDENCE_SHA256,
            "a1_archive_sha256": admission["prior_partial_archive_sha256"],
            "predecessor_archive_sha256": admission["predecessor_archive_sha256"],
            "predecessor_pairs": 2047, "a1_stage8_pairs": 16,
            "a2_stage16_pairs": 32, "a2_stage32_pairs": 64,
            "canonical_pairs": 2159, "imported_ids": imported_ids,
            "imported_records": records, "selected_workers": 32,
            "remaining_midpoint_ids": 1424,
            "prior_raw_attempts": LIFETIME_RAW,
            "new_native_calls_in_validation": 0}


def a3_resume_receipts(required: list[PlannedQuery], missing: list[PlannedQuery],
                       pilot: dict, salvage: dict, head: str, tree: str) -> tuple[dict, dict]:
    imported = set(salvage["imported_ids"])
    remaining = [q.query_id for q in missing if q.query_id not in imported]
    all_pilot = {qid for stage in pilot["stages"] for qid in stage["query_ids"]}
    if (len(required) != 1538 or len(missing) != 1536 or len(imported) != 112
        or imported != all_pilot or len(remaining) != 1424
        or remaining != pilot["remaining_ids"] or salvage["selected_workers"] != 32
        or salvage["prior_raw_attempts"] != LIFETIME_RAW):
        raise ValueError("A3 fill-only query/selection accounting mismatch")
    plan = {"schema": "BASS_R4M_N1536_FILL_ONLY_QUERY_PLAN_V1",
            "execution_commit": head, "execution_tree": tree,
            "a2_archive_sha256": A2_ARCHIVE_SHA256,
            "initial_canonical_pairs": 2159, "initial_exact_hits": 2,
            "already_completed_pilot_ids": [q for q in salvage["imported_ids"]],
            "remaining_ids": remaining, "remaining_midpoint_count": 1424,
            "active_required_count": 1538, "eventual_union_pairs": 3583,
            "prior_raw_attempts": LIFETIME_RAW, "lifetime_raw_cap": 16896,
            "remaining_raw_reservation_capacity": 16896 - LIFETIME_RAW,
            "strict_remaining_worst_raw": 1424 * 11,
            "strict_lifetime_worst_raw": LIFETIME_RAW + 1424 * 11,
            "lifetime_raw_margin": 16896 - LIFETIME_RAW - 1424 * 11}
    selected = {"schema": "BASS_R4M_A2_SELECTED_STAGE_EVIDENCE_V1",
                "execution_commit": head, "execution_tree": tree,
                "a2_archive_sha256": A2_ARCHIVE_SHA256,
                "a2_selection_sha256": A2_EVIDENCE_SHA256["ADAPTIVE_SELECTION.json"],
                "a2_stage16_sha256": A2_EVIDENCE_SHA256["STAGE_16.json"],
                "a2_stage32_sha256": A2_EVIDENCE_SHA256["STAGE_32.json"],
                "selected_workers": 32, "no_pilot_reexecution": True,
                "new_native_pilot_queries": 0}
    return plan, selected
