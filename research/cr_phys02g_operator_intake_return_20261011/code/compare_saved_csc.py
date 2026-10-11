#!/usr/bin/env python3
"""One bounded comparison of two explicitly bound, persisted CSC triples."""
import argparse
import ast
import bisect
import hashlib
import json
import math
import os
import struct
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MAX_BLOCK = 262144
LIMIT = 90.0
REF = "6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd"
CUR = "8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa"


def utc():
    return datetime.now(timezone.utc).isoformat()


def json_finite(obj):
    if isinstance(obj, float) and not math.isfinite(obj):
        return "NaN" if math.isnan(obj) else "+Infinity" if obj > 0 else "-Infinity"
    if isinstance(obj, dict):
        return {k: json_finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_finite(v) for v in obj]
    return obj


def check(deadline):
    if time.monotonic() >= deadline:
        raise TimeoutError("saved comparison exceeded 90 seconds")


def npy(path, member, out, deadline):
    """Return a file and raw offset. NPZ members spool only inside output directory."""
    temp = None
    if member:
        with zipfile.ZipFile(path) as z:
            info = z.getinfo(member)
            if info.file_size > 1073741824:
                raise ValueError("member exceeds 1 GiB")
            with z.open(info) as source, tempfile.NamedTemporaryFile(dir=out, delete=False) as target:
                temp = target.name
                while True:
                    check(deadline)
                    b = source.read(1048576)
                    if not b:
                        break
                    target.write(b)
        path = temp
    f = open(path, "rb")
    try:
        if f.read(6) != b"\x93NUMPY":
            raise ValueError("not NPY")
        major, minor = f.read(2)
        if major == 1:
            n = struct.unpack("<H", f.read(2))[0]
        elif major in (2, 3):
            n = struct.unpack("<I", f.read(4))[0]
        else:
            raise ValueError("unsupported NPY version")
        if n > 65536:
            raise ValueError("oversized NPY header")
        header = ast.literal_eval(f.read(n).decode("latin1" if major < 3 else "utf8"))
        dtype = header["descr"]
        shape = tuple(header["shape"])
        if header["fortran_order"] or len(shape) != 1 or dtype not in ("<f8", "<i4", "<i8"):
            raise ValueError("requires 1D little-endian C-order f8/i4/i8")
        offset = f.tell()
        size = int(dtype[-1]) * shape[0]
        if os.fstat(f.fileno()).st_size != offset + size:
            raise ValueError("NPY payload length mismatch")
        return {"file": f, "temp": temp, "dtype": dtype, "shape": shape, "offset": offset, "bytes": size, "path": str(path), "member": member}
    except BaseException:
        f.close()
        if temp:
            os.unlink(temp)
        raise


def raw_hash(a, deadline):
    f = a["file"]
    f.seek(a["offset"])
    h = hashlib.sha256()
    remaining = a["bytes"]
    while remaining:
        check(deadline)
        b = f.read(min(1048576, remaining))
        if not b:
            raise ValueError("short raw payload")
        h.update(b)
        remaining -= len(b)
    return h.hexdigest()


def values(a, block, deadline):
    f = a["file"]
    f.seek(a["offset"])
    fmt = {"<f8": "d", "<i4": "i", "<i8": "q"}[a["dtype"]]
    width = int(a["dtype"][-1])
    for base in range(0, a["shape"][0], block):
        check(deadline)
        count = min(block, a["shape"][0] - base)
        raw = f.read(count * width)
        if len(raw) != count * width:
            raise ValueError("short raw payload")
        yield base, struct.unpack("<" + fmt * count, raw)


def first_structure_difference(x, y, block, deadline):
    if x["shape"] != y["shape"] or x["dtype"] != y["dtype"]:
        return {"kind": "metadata", "reference": {"shape": x["shape"], "dtype": x["dtype"]}, "current": {"shape": y["shape"], "dtype": y["dtype"]}}
    for (base, aa), (_, bb) in zip(values(x, block, deadline), values(y, block, deadline)):
        for j, (v, w) in enumerate(zip(aa, bb)):
            if v != w:
                return {"kind": "value", "index": base + j, "reference": v, "current": w}
    return None


def ulp(a, b):
    ua = struct.unpack("<Q", struct.pack("<d", a))[0]
    ub = struct.unpack("<Q", struct.pack("<d", b))[0]
    # Monotone integer ordering across the signed IEEE-754 bit patterns.
    oa = (~ua & ((1 << 64) - 1)) if ua >> 63 else ua | (1 << 63)
    ob = (~ub & ((1 << 64) - 1)) if ub >> 63 else ub | (1 << 63)
    return abs(oa - ob)


def main():
    started = time.monotonic()
    deadline = started + LIMIT
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--reference-binding", required=True, help="JSON receipt binding all three original saved arrays to recorded reference G")
    p.add_argument("--current-binding", required=True, help="JSON receipt binding all three original saved arrays to recorded failed-current G")
    p.add_argument("--block", type=int, default=MAX_BLOCK)
    a = p.parse_args()
    if not 1 <= a.block <= MAX_BLOCK:
        raise SystemExit("block outside 1..262144")
    out = Path(a.out).absolute()
    if out.is_symlink() or not out.is_dir():
        raise SystemExit("output must be existing nonsymlink diagnostic directory")
    result = {"schema": "cr-phys02g-saved-csc-comparison.v1", "start_utc": utc(), "command": sys.argv, "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "status": "INCOMPLETE", "physics_execution_counters": {k: 0 for k in ("G_builds", "resolvent", "linear_solves", "pulse", "expm", "F_retry", "G_frontier")}, "comparison_runs": 1}
    opened = []
    exit_code = 0
    try:
        bindings = []
        for label, file, expected in (("reference", a.reference_binding, REF), ("failed_current", a.current_binding, CUR)):
            b = json.loads(Path(file).read_text())
            if b.get("recorded_G_data_sha256") != expected or b.get("binding_status") != "ORIGINAL_PERSISTED_CSC_BYTE_BOUND":
                raise ValueError(label + " binding does not certify exact original persisted CSC identity")
            arrays = {}
            for kind in ("data", "indices", "indptr"):
                spec = b["arrays"][kind]
                path = Path(spec["path"])
                if path.is_symlink() or any(q.is_symlink() for q in path.parents):
                    raise ValueError("symlink array path")
                obj = npy(path, spec.get("member"), out, deadline)
                opened.append(obj)
                obj["raw_sha256"] = raw_hash(obj, deadline)
                if obj["raw_sha256"] != spec["raw_C_sha256"]:
                    raise ValueError(label + " " + kind + " raw hash mismatches binding")
                arrays[kind] = obj
            if arrays["data"]["raw_sha256"] != expected:
                raise ValueError(label + " data hash mismatches recorded G")
            bindings.append(arrays)
        ref, cur = bindings
        result["bound_inputs"] = [{k: {"path": v["path"], "member": v["member"], "dtype": v["dtype"], "shape": v["shape"], "raw_sha256": v["raw_sha256"]} for k, v in side.items()} for side in bindings]
        if ref["data"]["dtype"] != "<f8" or cur["data"]["dtype"] != "<f8":
            raise ValueError("CSC data must be little-endian float64")
        for kind in ("indices", "indptr"):
            if ref[kind]["dtype"] not in ("<i4", "<i8") or cur[kind]["dtype"] not in ("<i4", "<i8"):
                raise ValueError("CSC structure must be little-endian integer")
            difference = first_structure_difference(ref[kind], cur[kind], a.block, deadline)
            result[kind + "_difference"] = difference
            if difference:
                result["status"] = "CSC_STRUCTURE_DIFFERENT"
                return 0
        indptr = [v for _, part in values(ref["indptr"], a.block, deadline) for v in part]
        n = ref["data"]["shape"][0]
        if cur["data"]["shape"] != (n,) or ref["indices"]["shape"] != (n,) or len(indptr) < 2 or indptr[0] != 0 or indptr[-1] != n or any(x > y for x, y in zip(indptr, indptr[1:])):
            raise ValueError("invalid CSC dimensions or indptr")
        difference_count = 0
        first = None
        max_abs = {"value": 0.0, "at": None}
        max_rel = {"value": 0.0, "at": None, "denominator": "max(abs(reference), abs(current)); zero/zero=0"}
        max_ulp = {"value": 0, "at": None}
        categories = {"signed_zero_only": 0, "zero_vs_nonzero": 0, "opposite_sign": 0, "nan": 0, "infinity": 0, "finite_same_sign": 0}
        signed_extrema = {"minimum": None, "maximum": None}
        samples = []
        index_stream = values(ref["indices"], a.block, deadline)
        for (base, aa), (_, bb), (_, ii) in zip(values(ref["data"], a.block, deadline), values(cur["data"], a.block, deadline), index_stream):
            for j, (x, y) in enumerate(zip(aa, bb)):
                bits_differ = struct.pack("<d", x) != struct.pack("<d", y)
                if not bits_differ:
                    continue
                k = base + j
                col = bisect.bisect_right(indptr, k) - 1
                loc = {"index": k, "row": ii[j], "column": col}
                difference_count += 1
                if first is None:
                    first = {**loc, "reference": x, "current": y}
                if len(samples) < 16:
                    samples.append({**loc, "reference": x, "current": y})
                if math.isnan(x) or math.isnan(y):
                    categories["nan"] += 1
                    continue
                if math.isinf(x) or math.isinf(y):
                    categories["infinity"] += 1
                    continue
                if x == 0 and y == 0:
                    categories["signed_zero_only"] += 1
                elif x == 0 or y == 0:
                    categories["zero_vs_nonzero"] += 1
                elif (x < 0) != (y < 0):
                    categories["opposite_sign"] += 1
                else:
                    categories["finite_same_sign"] += 1
                    u = ulp(x, y)
                    if u > max_ulp["value"]:
                        max_ulp = {"value": u, "at": loc}
                signed = y - x
                for key, pred in (("minimum", lambda v: signed < v), ("maximum", lambda v: signed > v)):
                    old = signed_extrema[key]
                    if old is None or pred(old["value"]):
                        signed_extrema[key] = {"value": signed, "at": loc}
                absolute = abs(signed)
                denominator = max(abs(x), abs(y))
                relative = absolute / denominator if denominator else 0.0
                if absolute > max_abs["value"]:
                    max_abs = {"value": absolute, "at": loc}
                if relative > max_rel["value"]:
                    max_rel = {"value": relative, "at": loc, "denominator": "max(abs(reference), abs(current)); zero/zero=0"}
        result.update(status="SAVED_CSC_COMPARED_NO_SCIENTIFIC_ADOPTION", data_difference_count=difference_count, first_data_difference=first, max_absolute_difference=max_abs, max_zero_aware_relative_difference=max_rel, max_finite_same_sign_ulp=max_ulp, categories=categories, signed_difference_extrema=signed_extrema, first_16_samples=samples)
    except (OSError, ValueError, KeyError, TimeoutError, zipfile.BadZipFile) as e:
        result["error"] = type(e).__name__ + ": " + str(e)
        exit_code = 2
    finally:
        for obj in opened:
            obj["file"].close()
            if obj["temp"]:
                os.unlink(obj["temp"])
        result["end_utc"] = utc()
        result["wall_s"] = time.monotonic() - started
        result["exit_code"] = exit_code
        (out / "SAVED_CSC_COMPARISON.json").write_text(json.dumps(json_finite(result), indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(json.dumps({"status": result["status"], "exit_code": exit_code, "result": str(out / "SAVED_CSC_COMPARISON.json")}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
