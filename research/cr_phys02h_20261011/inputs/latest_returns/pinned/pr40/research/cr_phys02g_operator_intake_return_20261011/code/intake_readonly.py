#!/usr/bin/env python3
"""Bounded, read-only intake of already recorded operator evidence. Stdlib only."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import stat
import sys
import sysconfig
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

LIMIT = 170.0  # Leave ten seconds for the receipt before the parent's 180 s kill.
MAX_FILES = 10000
REF = "6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd"
CUR = "8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa"
ENV_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_CORETYPE", "LD_LIBRARY_PATH")


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path, deadline):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("diagnostic window elapsed during hash")
            b = f.read(1048576)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def path_record(path, deadline, archive=False):
    p = Path(path)
    row = {"path": str(p)}
    try:
        if any(q.is_symlink() for q in p.parents):
            row.update(kind="blocked_symlink_ancestor", traversed=False)
            return row
        st = p.lstat()
        row["kind"] = "symlink" if stat.S_ISLNK(st.st_mode) else "file" if stat.S_ISREG(st.st_mode) else "directory" if stat.S_ISDIR(st.st_mode) else "other"
        row["bytes"] = st.st_size
        if row["kind"] == "file":
            row["sha256"] = digest(p, deadline)
            if archive and p.suffix.lower() == ".npz":
                with zipfile.ZipFile(p) as z:
                    row["archive_members"] = [{"name": i.filename, "bytes": i.file_size, "compressed_bytes": i.compress_size, "crc32": f"{i.CRC:08x}"} for i in z.infolist()[:MAX_FILES]]
                    row["archive_member_count"] = len(z.infolist())
        elif row["kind"] == "symlink":
            row["target"] = os.readlink(p)
    except (OSError, TimeoutError, zipfile.BadZipFile) as e:
        row["error"] = type(e).__name__ + ": " + str(e)
    return row


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def safe_walk(root, deadline, count):
    """Inventory exact recorded run/cache roots; never follow a symlink."""
    rows = []
    stack = [Path(root)]
    while stack and count[0] < MAX_FILES and time.monotonic() < deadline:
        p = stack.pop()
        if any(q.is_symlink() for q in p.parents):
            rows.append({"path": str(p), "kind": "blocked_symlink_ancestor", "traversed": False})
            continue
        try:
            st = p.lstat()
        except OSError as e:
            rows.append({"path": str(p), "error": type(e).__name__ + ": " + str(e)})
            continue
        if stat.S_ISLNK(st.st_mode):
            rows.append({"path": str(p), "kind": "symlink", "target": os.readlink(p), "traversed": False})
        elif stat.S_ISDIR(st.st_mode):
            try:
                stack.extend(sorted(p.iterdir(), reverse=True))
            except OSError as e:
                rows.append({"path": str(p), "error": type(e).__name__ + ": " + str(e)})
        elif stat.S_ISREG(st.st_mode):
            count[0] += 1
            rows.append(path_record(p, deadline, archive=p.suffix.lower() == ".npz"))
    return rows, {"file_limit_reached": count[0] >= MAX_FILES, "time_limit_reached": time.monotonic() >= deadline}


def main():
    started = time.monotonic()
    deadline = started + LIMIT
    a = argparse.ArgumentParser()
    a.add_argument("--root", required=True)
    a.add_argument("--out", required=True)
    args = a.parse_args()
    root = Path(args.root).absolute()
    out = Path(args.out).absolute()
    if out != root / "diagnostic" or out.is_symlink() or root.is_symlink():
        raise SystemExit("out must be root/diagnostic; symlink roots forbidden")
    out.mkdir(mode=0o700, exist_ok=True)
    result = {"schema": "cr-phys02g-readonly-intake.v1", "start_utc": utc(), "command": sys.argv, "code": path_record(__file__, deadline), "status": "MISSING_PERSISTED_OPERATOR_VALUES", "expected_raw_data_sha256": {"reference": REF, "failed_current": CUR}, "execution_counters_this_intake": {k: 0 for k in ("G_builds", "resolvent", "linear_solves", "pulse", "expm", "F_retry", "G_frontier", "saved_comparison")}, "saved_comparison_status": "NOT_EXECUTED_NO_BOUND_PAIR", "original_records": [], "recorded_paths": [], "scoped_search": [], "runtime": {}}
    exit_code = 0
    try:
        names = [root / "e_return_numeric/actual_run/G_COMPLETION_1.json", root / "e_return_numeric/actual_run/G_COMPLETION_2.json", root / "e_return_numeric/actual_run/RUNTIME.json", root / "e_return_numeric/actual_run/ACTUAL_EXIT.json", root / "f_actual_original/F/run/G_COMPLETION_1.json", root / "f_actual_original/F/run/RUNTIME.json", root / "f_actual_original/F/run/ACTUAL_EXIT.json", root / "f_actual_original/F/run/WRAPPER_ACTUAL_EXIT.json", root / "f_actual_original/F/run/stderr.log", root / "f_actual_original/F/external_logs/host_probe.json", root / "f_actual_original/F/return/WRAPPER_COLLECTION_EXIT.json", root / "f_actual_original/F/return/WRAPPER_ACTUAL_EXIT.json", root / "f_actual_numeric/actual_run/G_COMPLETION_1.json", root / "f_actual_numeric/actual_run/RUNTIME.json", root / "f_actual_numeric/actual_run/ACTUAL_EXIT.json", root / "f_actual_numeric/dependencies/actual_fullBED_G/G_COMPLETION_1.json", root / "f_actual_numeric/dependencies/actual_runtime/RUNTIME.json"]
        texts = []
        for p in names:
            rec = path_record(p, deadline)
            result["original_records"].append(rec)
            if rec.get("kind") == "file" and p.suffix == ".json":
                try:
                    texts.append((str(p), json.loads(p.read_text())))
                except (OSError, ValueError) as e:
                    rec["parse_error"] = str(e)
        found = set()
        roots = set()
        for source, obj in texts:
            for s in strings(obj):
                if s.startswith("/") and "\n" not in s and len(s) < 4096:
                    found.add((source, s))
                    parts = Path(s).parts
                    for marker in ("run", "actual_run", "cache"):
                        if marker in parts:
                            roots.add(str(Path(*parts[:parts.index(marker) + 1])))
        for source, p in sorted(found):
            result["recorded_paths"].append({"record": source, **path_record(p, deadline)})
        count = [0]
        for p in sorted(roots):
            if p in ("/", "/root", "/tmp", "/home"):
                continue
            rows, limits = safe_walk(p, deadline, count)
            result["scoped_search"].append({"recorded_root": p, "root_presence": path_record(p, deadline), "entries": rows, **limits})
        result["search_total_files"] = count[0]
        result["search_exhaustive"] = bool(roots) and count[0] < MAX_FILES and time.monotonic() < deadline
        result["candidate_arrays"] = [{"path": x["path"], "sha256": x.get("sha256"), "source_binding": "UNBOUND_CANDIDATE_ONLY"} for scope in result["scoped_search"] for x in scope["entries"] if x.get("kind") == "file" and x["path"].lower().endswith((".npy", ".npz"))]
        if result["candidate_arrays"]:
            result["status"] = "FOUND_UNBOUND_CANDIDATE"
        observed_exe = os.readlink("/proc/self/exe") if Path("/proc/self/exe").is_symlink() else None
        result["runtime"] = {"python": sys.version, "executable_invocation": path_record(sys.executable, deadline), "proc_self_exe_link": observed_exe, "observed_executable_target": path_record(observed_exe, deadline) if observed_exe else None, "platform": platform.platform(), "sysconfig": {k: sysconfig.get_config_var(k) for k in ("SOABI", "MULTIARCH", "LIBDIR", "LDLIBRARY", "CONFIG_ARGS")}, "environment_allowlist": {k: os.environ.get(k) for k in ENV_KEYS}, "current_blas_dispatch": "NOT_OBSERVED_WITHOUT_NUMERICAL_IMPORT"}
        cpu = Path("/proc/cpuinfo")
        if cpu.is_file():
            for line in cpu.read_text().splitlines():
                if line.startswith(("model name", "flags", "Features")):
                    result["runtime"].setdefault("cpu_capabilities", {})[line.split(":", 1)[0].strip()] = line.split(":", 1)[1].strip()
                    if len(result["runtime"]["cpu_capabilities"]) >= 2:
                        break
        maps = Path("/proc/self/maps")
        if maps.is_file():
            mapped = sorted({line.split()[-1] for line in maps.read_text().splitlines() if "/" in line and (".so" in line or "/python" in line)})
            result["runtime"]["loaded_binaries"] = [path_record(p, deadline) for p in mapped if Path(p).is_absolute()]
        packages = {}
        for name in ("numpy", "scipy", "threadpoolctl"):
            try:
                d = importlib.metadata.distribution(name)
                wheel = d.read_text("WHEEL")
                packages[name] = {"version": d.version, "dist_info": str(d._path), "wheel_metadata": wheel, "wheel_sha256": hashlib.sha256(wheel.encode()).hexdigest() if wheel else None}
                for f in d.files or ():
                    fp = Path(d.locate_file(f))
                    if fp.suffix in (".so", ".dll", ".dylib") or ".so." in fp.name:
                        packages[name].setdefault("libraries", []).append(path_record(fp, deadline))
                site = Path(d.locate_file(""))
                for libdir in (site / "numpy.libs", site / "scipy.libs"):
                    if libdir.is_dir() and not libdir.is_symlink():
                        packages[name].setdefault("libraries", []).extend(path_record(p, deadline) for p in sorted(libdir.iterdir()) if p.is_file() and not p.is_symlink())
            except (importlib.metadata.PackageNotFoundError, OSError, TimeoutError) as e:
                packages[name] = {"status": "MISSING_OR_UNREADABLE", "detail": str(e)}
        result["runtime"]["installed_distributions_without_import"] = packages
        result["historical_actual_F"] = {"G_reserved": 1, "G_completed": 1, "execute_exit": 1, "wrapper_exit": 1, "resolvent": 0, "linear_solves": 0, "pulse": 0, "expm": 0}
        result["interpretation"] = "Original reference/current fingerprints differ; no bound persisted data arrays were adopted. Recorded old paths may be inaccessible here. Hardware flags do not establish actual numerical dispatch."
    except (OSError, TimeoutError, ValueError) as e:
        result["intake_error"] = type(e).__name__ + ": " + str(e)
        exit_code = 2
    result["end_utc"] = utc()
    result["wall_s"] = time.monotonic() - started
    result["exit_code"] = exit_code
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "result": str(out / "RESULT.json"), "exit_code": exit_code, "wall_s": result["wall_s"]}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
