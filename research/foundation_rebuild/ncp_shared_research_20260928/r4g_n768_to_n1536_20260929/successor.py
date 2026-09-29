"""Successor-only, non-native admission and exact N1536 query planning."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
R4F = HERE.parent / "r4f_parallel_migration_20260929"
R4C = HERE.parent / "r4c_temporal_continuation"
for directory in (HERE, R4F, R4C):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import continue_temporal as serial
from adaptive_workers import DEFAULT_STAGES, validate_resource_scope
from parallel_bridge import PlannedQuery, query_id, validate_pair
from execution_admission import strict_json

PREDECESSOR_SHA256 = "dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3"
PREDECESSOR_COMMIT = "11100b35f78ec26100ea732971bb4ce0f9925719"
PREDECESSOR_TREE = "05976e386c0a39591247d69c32c8cb28fa3f2a97"
PREDECESSOR_AUTH = "R4F-N768-MIGRATION-REPAIR-20260929-A2"
D768_REFERENCE_DISTANCE = 6.586233081176365e-7
CONTEXT_ID = "bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda"
REQUIRED_COUNT = 1538
MISSING_COUNT = 1536
UNION_COUNT = 3583
NATIVE_SOURCE_SHA256 = "90913155c0cfa80962d1cb00bb1b7ec0443170917c25913ac5e359979738ab30"
NATIVE_LIBRARY_SHA256 = "966146f0ca713251f8b73999b4d89595cf1820a8c2d36f5c6290387b70c68035"
NATIVE_BUILD_SHA256 = "180a74d3acf2588d3b8c7944effe4709a4fd4f6241cb4df736cd8f0c94430af1"
THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")


def plan_n1536(context_id: str, t0: float, tf: float) -> list[PlannedQuery]:
    if context_id != CONTEXT_ID or not np.isfinite((t0, tf)).all() or not tf > t0:
        raise ValueError("frozen context and finite increasing window required")
    dt = (tf - t0) / 1536
    def item(t: float, j: int | None = None, width: float | None = None) -> PlannedQuery:
        th = float(t).hex()
        return PlannedQuery(query_id(context_id, th), th, j, None if width is None else float(width).hex())
    result = [item(t0)]
    for j in range(1536):
        ta = t0 + j * dt
        tb = ta + dt
        result.append(item(0.5 * (ta + tb), j, tb - ta))
    result.append(item(tf))
    if len(result) != REQUIRED_COUNT or len({q.query_id for q in result}) != REQUIRED_COUNT:
        raise ValueError("N1536 required query identity collision")
    return result


def _json_member(source: Path, name: str) -> dict:
    return strict_json(source / name)


def validate_predecessor(source: Path, expected_sha256: str, destination: Path) -> dict:
    """Verify every archived byte and the completed A2 evidence before reuse."""
    source = Path(source).resolve()
    destination = Path(destination)
    if expected_sha256 != PREDECESSOR_SHA256 or serial.sha256_path(source) != PREDECESSOR_SHA256:
        raise ValueError("completed N768 archive SHA256 mismatch")
    if destination.exists():
        raise FileExistsError("predecessor extraction target exists")
    destination.mkdir(parents=True)
    with zipfile.ZipFile(source) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or z.testzip() is not None:
            raise ValueError("predecessor ZIP duplicate or CRC failure")
        for info in z.infolist():
            p = Path(info.filename)
            if (p.is_absolute() or ".." in p.parts or "\\" in info.filename
                or ((info.external_attr >> 16) & 0o170000) == 0o120000):
                raise ValueError("unsafe predecessor ZIP member")
        z.extractall(destination)
    manifest = _json_member(destination, "MANIFEST.json")
    if set(names) != set(manifest) | {"MANIFEST.json"}:
        raise ValueError("predecessor manifest membership mismatch")
    for rel, row in manifest.items():
        p = destination / rel
        if p.stat().st_size != row["bytes"] or serial.sha256_path(p) != row["sha256"]:
            raise ValueError("predecessor manifest byte mismatch: " + rel)
    report = _json_member(destination, "RETURN_REPORT.json")
    admission = _json_member(destination, "EXECUTION_ADMISSION.json")
    consumed = _json_member(destination, "AUTHORIZATION_CONSUMED.json")
    replay = _json_member(destination, "CACHE_ONLY_REPLAY_AUDIT.json")
    coverage = _json_member(destination, "CACHE_COVERAGE_AUDIT.json")
    if (report.get("status") != "R4E_N768_BRIDGE_COMPLETE__N1536_DECISION_PENDING"
        or report.get("execution_head") != PREDECESSOR_COMMIT
        or report.get("execution_tree") != PREDECESSOR_TREE
        or report.get("pair", {}).get("selected_nstep") != 768
        or not math.isclose(float(report.get("pair", {}).get("candidate_reference_metric_distance", math.nan)),
                            D768_REFERENCE_DISTANCE, rel_tol=0, abs_tol=1e-15)
        or admission.get("authorization_id") != PREDECESSOR_AUTH
        or admission.get("execution_commit") != PREDECESSOR_COMMIT
        or admission.get("execution_tree") != PREDECESSOR_TREE
        or consumed.get("authorization_id") != PREDECESSOR_AUTH
        or replay.get("native_operator_calls") != 0
        or replay.get("original_initial_state_used") is not True
        or coverage.get("verified") != 770):
        raise ValueError("completed predecessor admission/replay mismatch")
    for key, expected in serial.CLAIM_CEILING.items():
        if report.get(key) != expected:
            raise ValueError("predecessor claim ceiling mismatch")
    sc = _json_member(destination, "SCIENCE_CONTEXT.json")
    if serial.digest(sc["context"]) != sc.get("context_id") or sc["context_id"] != CONTEXT_ID:
        raise ValueError("predecessor context mismatch")
    contract = sc["context"]["contract"]
    if contract["max_unique_runtime_queries"] != 2048:
        raise ValueError("frozen active query cap changed")
    if (len(contract["runtime_reference_resolutions"]) != 11
        or contract["analytic_source_sha256"] != NATIVE_SOURCE_SHA256
        or contract["analytic_library_sha256"] != NATIVE_LIBRARY_SHA256):
        raise ValueError("frozen native source/library or ladder changed")
    basis = _json_member(destination, "BASIS.json")
    if (serial.digest({k: v for k, v in basis.items() if k != "identity"}) != basis.get("identity")
        or serial.sha256_path(destination / "BASIS.npz") != basis.get("matrix_sha256")
        or basis.get("identity") != sc["context"]["physics_identity"]["basis_identity"]):
        raise ValueError("predecessor basis mismatch")
    rr = _json_member(destination, "REFERENCE_RECEIPT.json")
    if (rr["method"] != contract["reference_solver"]["method"]
        or float(rr["rtol"]) != float(contract["reference_solver"]["rtol"])
        or float(rr["atol"]) != float(contract["reference_solver"]["atol"])
        or float(rr["max_norm_drift"]) > float(contract["screens"]["reference_norm_drift_max"])):
        raise ValueError("predecessor reference receipt mismatch")
    metric = _json_member(destination, "METRIC_CONNECTION.json")
    if (len(metric) != len(contract["metric_sentinel_z_a0"])
        or any(float(x["relative_residual"]) > float(contract["screens"]["metric_derivative_relative_max"]) for x in metric)):
        raise ValueError("predecessor metric evidence mismatch")
    candidate = serial.load_candidate(destination, 768)
    with np.load(destination / "REFERENCE_STATES.npz", allow_pickle=False) as f:
        if (f["initial_state"].shape != (18,) or f["final_state"].shape != (18,)
            or not np.isfinite(f["initial_state"]).all() or not np.isfinite(f["final_state"]).all()
            or not np.allclose(f["initial_state"], candidate.initial_state, rtol=0, atol=1e-14)):
            raise ValueError("predecessor reference/initial state mismatch")
    qdir = destination / "runtime_queries"
    json_ids = {p.stem for p in qdir.glob("*.json")}
    npz_ids = {p.stem for p in qdir.glob("*.npz")}
    if len(json_ids) != 2047 or json_ids != npz_ids:
        raise ValueError("predecessor canonical query store mismatch")
    for qid in sorted(json_ids):
        row = strict_json(qdir / (qid + ".json"))
        item = PlannedQuery(qid, row["time_hex"], None, None)
        validate_pair(qdir, item, CONTEXT_ID, contract)
    return {"source_sha256": PREDECESSOR_SHA256, "source_bytes": source.stat().st_size,
            "manifest_sha256": serial.sha256_path(destination / "MANIFEST.json"),
            "report_sha256": serial.sha256_path(destination / "RETURN_REPORT.json"),
            "admission_sha256": serial.sha256_path(destination / "EXECUTION_ADMISSION.json"),
            "canonical_query_pairs": len(json_ids), "context_id": CONTEXT_ID,
            "previous_candidate": candidate, "contract": contract}


def required_missing(required: list[PlannedQuery], present_ids: set[str]) -> list[PlannedQuery]:
    hits = [q for q in required if q.query_id in present_ids]
    missing = [q for q in required if q.query_id not in present_ids]
    if (len(required) != REQUIRED_COUNT or len(hits) != 2 or len(missing) != MISSING_COUNT
        or hits != [required[0], required[-1]] or len(present_ids) != 2047
        or len(present_ids | {q.query_id for q in required}) != UNION_COUNT):
        raise ValueError("N1536 exact-hit/missing/union contract mismatch")
    return missing


def plan_receipts(required, missing, stages, remainder, head: str, tree: str):
    plan = {"schema": "BASS_R4G_N1536_EXACT_QUERY_PLAN_V1",
            "execution_commit": head, "execution_tree": tree,
            "predecessor_archive_sha256": PREDECESSOR_SHA256,
            "required": [q.__dict__ for q in required],
            "initial_exact_hits": 2, "missing_ids": [q.query_id for q in missing],
            "active_required_count": REQUIRED_COUNT, "eventual_union_count": UNION_COUNT}
    pilot = {"schema": "BASS_R4G_USEFUL_PILOT_PLAN_V1",
             "stages": [{"workers": s.workers, "query_ids": list(s.query_ids)} for s in stages],
             "remaining_ids": list(remainder), "pilot_results_retained": True}
    return plan, pilot


def pilot_authority_fields(policy: dict, pilot: dict | None = None) -> dict:
    """Bind admission and the future template to the useful pilot plan."""
    workers = list(policy["stages"])
    counts = [n * policy["pilot_queries_per_worker"] for n in workers]
    total = sum(counts)
    remaining = MISSING_COUNT - total
    if (tuple(workers) != DEFAULT_STAGES or counts != [16, 32, 64]
        or total != 112 or remaining != 1424
        or policy["stage_useful_query_counts"] != counts
        or policy["stage_useful_queries_total"] != total
        or policy["post_pilot_remaining_queries"] != remaining):
        raise ValueError("adaptive pilot authority policy mismatch")
    if pilot is not None and (
        [row["workers"] for row in pilot["stages"]] != workers
        or [len(row["query_ids"]) for row in pilot["stages"]] != counts
        or len(pilot["remaining_ids"]) != remaining
    ):
        raise ValueError("adaptive pilot authority plan mismatch")
    return {"worker_stages": workers, "pilot_query_counts": counts,
            "pilot_query_total": total, "post_pilot_remaining": remaining}


def live_resource_census(cpus: list[int], workers: int, worker_ram_bytes: int) -> dict:
    """Fail closed before a stage if affinity, free RAM, or competing BASS work changes."""
    allowed = os.sched_getaffinity(0)
    requested = set(cpus[:workers])
    if len(requested) != workers or not requested.issubset(allowed):
        raise ValueError("live CPU affinity no longer admits worker stage")
    cpu_max = Path("/sys/fs/cgroup/cpu.max")
    quota_cores = None
    if cpu_max.is_file():
        quota, period = cpu_max.read_text().split()[:2]
        if quota != "max":
            quota_cores = int(quota) / int(period)
            if quota_cores < workers:
                raise ValueError("live CPU quota below worker stage")
    meminfo = (Path("/proc/meminfo").read_text())
    match = re.search(r"^MemAvailable:\s+(\d+) kB$", meminfo, re.M)
    if not match:
        raise ValueError("live free RAM unavailable")
    available = int(match.group(1)) * 1024
    cgroup_max = Path("/sys/fs/cgroup/memory.max")
    cgroup_current = Path("/sys/fs/cgroup/memory.current")
    if cgroup_max.is_file() and cgroup_current.is_file():
        limit = cgroup_max.read_text().strip()
        if limit != "max":
            available = min(available, max(0, int(limit) - int(cgroup_current.read_text().strip())))
    need = workers * worker_ram_bytes + (4 << 30)
    if available < need:
        raise ValueError("live free RAM below worker envelope plus coordinator reserve")
    competing = []
    ancestors = {os.getpid()}
    parent = os.getppid()
    while parent > 1 and parent not in ancestors:
        ancestors.add(parent)
        try:
            stat = (Path("/proc") / str(parent) / "stat").read_text().rsplit(")", 1)[1].split()
            parent = int(stat[1])
        except (OSError, IndexError, ValueError):
            break
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) in ancestors:
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            if not re.search(r"(BASS_HE|WU088_HH|bass_cr)", command, re.I):
                continue
            if not re.search(r"(python|worker|science|runtime)", command, re.I):
                continue
            other = os.sched_getaffinity(int(proc.name))
            if requested & other:
                competing.append({"pid": int(proc.name), "cmdline": command[:300]})
        except (OSError, ProcessLookupError):
            continue
    if competing:
        raise ValueError("competing BASS workload overlaps approved worker CPUs")
    return {"cpus": sorted(requested), "affinity": sorted(allowed),
            "cpu_quota_cores": quota_cores,
            "mem_available_bytes": available, "required_available_bytes": need,
            "competing_bass_processes": competing, "checked_unix": time.time()}


def admission_scope(args) -> dict:
    if os.environ.get("ALLOW_NEW_NATIVE_R4G") != "YES_I_AUTHORIZE_N1536":
        raise PermissionError("N1536_NATIVE_NOT_AUTHORIZED")
    head, tree = serial.git_identity()
    if head != args.expected_commit or tree != args.expected_tree:
        raise ValueError("successor execution commit/tree mismatch")
    if subprocess.check_output(["git", "-C", str(serial.REPO), "status",
                                "--porcelain", "--untracked-files=all"], text=True):
        raise ValueError("successor worktree must be clean")
    if Path(args.out).resolve().is_relative_to(serial.REPO):
        raise ValueError("output must be outside source tree")
    import scipy
    if not sys.flags.isolated or sys.version_info < (3, 11) or np.__version__ != "2.3.5" or scipy.__version__ != "1.17.0":
        raise ValueError("pinned isolated Python/numerical environment required")
    if any(os.environ.get(k) != "1" for k in THREAD_KEYS):
        raise ValueError("one numerical thread per worker required")
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{15,95}", args.authorization_id)
        or args.authorization_id == PREDECESSOR_AUTH):
        raise ValueError("unique explicit N1536 authorization ID required")
    if args.expected_predecessor_sha256 != PREDECESSOR_SHA256:
        raise ValueError("predecessor SHA pin mismatch")
    for value in (args.expected_source_pins_sha256, args.expected_query_plan_sha256,
                  args.expected_useful_pilot_plan_sha256):
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("exact source/query/pilot SHA256 required")
    stages = tuple(int(x) for x in args.stages.split(","))
    if stages != DEFAULT_STAGES or args.hard_max_workers != 32:
        raise ValueError("only approved 8/16/32 worker policy allowed")
    cpus = [int(x) for x in args.cpus.split(",")]
    scope = validate_resource_scope(stages=stages, cpu_ids=cpus,
        worker_ram_bytes=args.worker_ram_bytes,
        total_worker_ram_cap_bytes=args.total_worker_ram_cap_bytes,
        hard_max=args.hard_max_workers)
    if not set(cpus).issubset(os.sched_getaffinity(0)):
        raise ValueError("approved CPU scope outside live affinity")
    if args.worker_ram_bytes != 1 << 30 or args.global_raw_attempt_cap < 1 or args.global_raw_attempt_cap > 16896:
        raise ValueError("RAM/raw contract outside prepared scope")
    now = time.time()
    if (not math.isfinite(args.deadline_unix) or now >= args.deadline_unix
        or args.max_wall_seconds < 1 or args.deadline_unix > now + args.max_wall_seconds + 1
        or not args.cost_scope.strip()):
        raise ValueError("explicit live deadline and cost scope required")
    census = live_resource_census(cpus, 8, args.worker_ram_bytes)
    pilot_fields = pilot_authority_fields(json.loads((HERE / "ADAPTIVE_WORKER_POLICY.json").read_text()))
    return {"schema": "BASS_R4G_N1536_ADMISSION_V1",
            "execution_commit": head, "execution_tree": tree,
            "predecessor_commit": PREDECESSOR_COMMIT, "predecessor_tree": PREDECESSOR_TREE,
            "predecessor_authorization_id": PREDECESSOR_AUTH,
            "predecessor_archive_sha256": PREDECESSOR_SHA256,
            "source_pins_sha256": args.expected_source_pins_sha256,
            "query_plan_sha256": args.expected_query_plan_sha256,
            "useful_pilot_plan_sha256": args.expected_useful_pilot_plan_sha256,
            "authorization_id": args.authorization_id, "worker_policy": scope,
            "selected_stage": None, **pilot_fields,
            "global_raw_attempt_cap": args.global_raw_attempt_cap,
            "deadline_unix": args.deadline_unix, "cost_scope": args.cost_scope,
            "max_wall_seconds": args.max_wall_seconds,
            "cost_limit_enforced_by_code": False,
            "threads": {k: os.environ[k] for k in THREAD_KEYS},
            "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
            "initial_resource_census": census}
