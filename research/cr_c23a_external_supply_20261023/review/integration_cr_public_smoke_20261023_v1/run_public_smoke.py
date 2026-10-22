"""One newly declared public-subset input; no historical audit replay."""
from __future__ import annotations
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import types

OUT = Path(__file__).resolve().parent
W = OUT.parent.parent
NEW = W / "recovery/restored/repository/research/cr_c23a_external_supply_20261023"
PUBLIC = NEW / "deposition"
OWNER = "c23a_cr_public_smoke_20261023_v1"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
HELPER_SHA256 = "6140de414736080e18c9dc46528f1378b18231ac66502dc917f2f7516ba86f7f"
RESOURCE_SHA256 = "5b87e4a5fbe32c21ec8391a1f432895e13064a86b7a404cc55652606607cf5c7"
INPUT = {"energy_eV": [20.0, 100.0, 1000.0], "PL_number_rate": [0.002, 0.001, 0.0], "units": "electrons_per_Href_per_eta_per_eV", "xi": 0.5}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(name, value):
    with (OUT / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def digest(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def from_bytes(name, path, data):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def worker():
    os.sched_setaffinity(0, {3})
    resource.setrlimit(resource.RLIMIT_CPU, (9, 9))
    started, cpu0 = time.perf_counter(), time.process_time()
    snapshot = OUT / "CONSUMER_SNAPSHOT.py"
    helper_bytes = snapshot.read_bytes()
    if hashlib.sha256(helper_bytes).hexdigest() != HELPER_SHA256:
        raise RuntimeError("HELPER_SOURCE_CHANGED")
    helper = from_bytes("c23a_public_smoke_consumer", snapshot, helper_bytes)
    opened = []
    tracking = [False]

    def audit(event, arguments):
        if event != "open" or not tracking[0] or not isinstance(arguments[0], (str, bytes)):
            return
        path = Path(os.fsdecode(arguments[0])).resolve()
        if str(path).startswith("/workspace/scratch/") and not path.is_relative_to(PUBLIC):
            raise RuntimeError("NONPUBLIC_WORKSPACE_DEPENDENCY: " + str(path))
        opened.append(str(path))

    sys.addaudithook(audit)
    tracking[0] = True
    try:
        result = helper.consume_public_subset(PUBLIC)
    finally:
        tracking[0] = False
    if json.loads(json.dumps(result["input"])) != INPUT:
        raise AssertionError("ACTUAL_INPUT_DIFFERS_FROM_PREDECLARED_SINGLE_CASE")
    write("RESPONSE.json", result)
    workspace_reads = sorted({p for p in opened if p.startswith("/workspace/scratch/")})
    write("CONSUMER_OPEN_RECEIPT.json", {
        "scope": "audit hook active only during consumer call; Python standard-library reads listed separately",
        "workspace_reads": workspace_reads,
        "all_workspace_reads_inside_public_subset": all(Path(p).is_relative_to(PUBLIC) for p in workspace_reads),
        "standard_library_or_runtime_reads": sorted(set(opened) - set(workspace_reads)),
        "original_upstream_archive_or_table_reads": 0,
    })
    summary = {
        "status": "PASS_SCOPED", "scope": "one new public-only packaging smoke input",
        "input_cases": 1, "consumer_calls": 1,
        "source_queries": 1, "physical_coupling": "NOT_ADMITTED",
        "old_audit_reruns": 0, "old_benchmark_reruns": 0, "source_campaign_reruns": 0,
        "new_cosmological_ODE": 0, "global_error_bound": None,
        "actual_cpu_affinity": sorted(os.sched_getaffinity(0)),
        "native_threads": 1, "thread_environment": {k: os.environ[k] for k in THREADS},
        "wall_s": time.perf_counter() - started, "cpu_s": time.process_time() - cpu0,
        "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "external_wall_limit_s": 10, "cpu_rlimit_s": 9, "finished_utc": utc(),
        "prior_syntax_NOT_RUN_report": "PRESERVED_UNCHANGED; this is a later actual-execution receipt",
    }
    write("RESULT.json", summary)
    print(json.dumps(summary))


def dispatch():
    helper_path = W / "review/integration_cr/consume_mit_mirror_example.py"
    helper_bytes = helper_path.read_bytes()
    if hashlib.sha256(helper_bytes).hexdigest() != HELPER_SHA256:
        raise RuntimeError("REVIEWED_HELPER_IDENTITY_MISMATCH")
    with (OUT / "CONSUMER_SNAPSHOT.py").open("xb") as handle:
        handle.write(helper_bytes)
    write("INPUT.json", INPUT)
    receipt = json.loads((PUBLIC / "EXTERNAL_REUSE_DOWNLOADS.json").read_text())
    names = ["fs2010_operator.py", "EXTERNAL_REUSE_DOWNLOADS.json"] + [
        "external_comparison/21cmFAST/" + row["path"]
        for row in receipt["files"] if row["repo"] == "21cmFAST"
    ]
    if len(names) != 17 or len(set(names)) != 17:
        raise RuntimeError("EXPECTED_SEVENTEEN_PUBLIC_DEPENDENCIES")
    inputs = [{"path": name, "absolute_path": str(PUBLIC / name), **digest((PUBLIC / name).read_bytes())} for name in names]
    write("PUBLIC_17_HASH_RECEIPT.json", {"public_root": str(PUBLIC), "count": len(inputs), "files": inputs})
    resource_path = NEW / "runtime/resource_control.py"
    resource_bytes = resource_path.read_bytes()
    if hashlib.sha256(resource_bytes).hexdigest() != RESOURCE_SHA256:
        raise RuntimeError("RESOURCE_OBSERVER_IDENTITY_CHANGED")
    identity = {"helper": digest(helper_bytes), "input": digest((OUT / "INPUT.json").read_bytes()),
                "public17": digest((OUT / "PUBLIC_17_HASH_RECEIPT.json").read_bytes()),
                "harness": digest(Path(__file__).read_bytes()), "resource_observer": digest(resource_bytes)}
    write("SOURCE_IDENTITY.json", identity)
    observer = from_bytes("c23a_public_smoke_resource_observer", resource_path, resource_bytes)
    observed = observer.observe_resources()
    write("RESOURCE_OBSERVED.json", observed)
    spare, memory = observed.get("cpu_quota_spare_cores"), observed.get("memory_available_bytes")
    if (3 not in os.sched_getaffinity(0) or spare is None or spare < 1.0 or memory is None
            or memory < 256 * 1024**2 or not observed.get("memory_observation_complete")):
        write("BLOCKED.json", {"status": "RESOURCE_BLOCKED", "consumer_calls": 0})
        raise RuntimeError("CURRENT_RESOURCE_NOT_ADMITTED")
    lease_dir = Path("/tmp/rei-bianchi-cooperative-leases")
    lease_dir.mkdir(exist_ok=True)
    lease_path = lease_dir / (OWNER + "_cpu3.json")
    lease = {"schema": "C21_CPU_LEASES_V1", "leases": [{"owner": OWNER, "cpus": [3], "pid": os.getpid()}]}
    seen = []
    with (lease_dir / "leases.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for path in lease_dir.glob("*.json"):
            data = path.read_bytes()
            doc = json.loads(data)
            if not isinstance(doc, dict):
                raise RuntimeError("UNKNOWN_LEASE_WITHHOLDS_CPU3")
            entries = doc.get("leases", [doc])
            if not isinstance(entries, list):
                raise RuntimeError("UNKNOWN_LEASE_WITHHOLDS_CPU3")
            for item in entries:
                if not isinstance(item, dict) or not isinstance(item.get("cpus"), list) or any(type(c) is not int or c < 0 for c in item["cpus"]):
                    raise RuntimeError("UNKNOWN_CPU_ENCODING_WITHHOLDS_CPU3")
                if 3 in item["cpus"]:
                    raise RuntimeError("CPU3_ALREADY_LEASED")
            seen.append({"path": str(path), **digest(data)})
        with lease_path.open("x") as handle:
            json.dump(lease, handle)
        write("LEASE_START.json", {"lease": lease, "observed_other_leases": seen, "created_utc": utc(), "native_threads": 1, "wall_limit_s": 10})
    try:
        proc = subprocess.run([sys.executable, str(Path(__file__)), "--worker"],
                              env=os.environ.copy(), capture_output=True, text=True, timeout=10)
        with (OUT / "STDOUT.txt").open("x") as handle:
            handle.write(proc.stdout)
        with (OUT / "STDERR.txt").open("x") as handle:
            handle.write(proc.stderr)
        write("DISPATCH_COMPLETE.json", {"returncode": proc.returncode, "wall_limit_s": 10, "finished_utc": utc()})
        if proc.returncode:
            raise RuntimeError("PUBLIC_SMOKE_WORKER_FAILED")
        print(proc.stdout)
    except subprocess.TimeoutExpired as exc:
        write("TIMEOUT.json", {"status": "FAILED_TIMEOUT", "wall_limit_s": 10, "observed_utc": utc()})
        raise
    finally:
        with (lease_dir / "leases.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text()) == lease:
                lease_path.unlink()
        write("LEASE_RELEASED.json", {"owner": OWNER, "cpu": 3, "status": "RELEASED", "released_utc": utc()})


if __name__ == "__main__":
    worker() if sys.argv[1:] == ["--worker"] else dispatch()
