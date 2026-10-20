#!/usr/bin/env python3
"""Read preserved benchmark bytes; emit a create-only summary, without reruns."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct


def bits(values):
    return b"".join(struct.pack(">d", value) for value in values)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def timing(values):
    return {"count": len(values), "median_ns": statistics.median(values),
            "min_ns": min(values), "max_ns": max(values),
            "mean_ns": statistics.mean(values), "stdev_ns": statistics.stdev(values)}


def load_input(path, m, g):
    blocks = {name: [] for name in ("shift", "A", "B", "C", "P", "Q", "rhs")}
    with path.open() as stream:
        for row in csv.DictReader(stream):
            value = struct.unpack(">d", struct.pack(">Q", int(row["binary64_hex"], 16)))[0]
            assert math.isfinite(value)
            assert bits([value]) == bits([float(row["value"])]), "decimal/bit input mismatch"
            target = blocks[row["block"]]
            assert int(row["index"]) == len(target)
            target.append(value)
    expected = {"shift": 1, "A": m*g, "B": m*g, "C": g*g,
                "P": 15*m, "Q": 15*g, "rhs": m+g+15}
    assert {name: len(v) for name, v in blocks.items()} == expected
    n = m+g+15
    jac = [[0.0]*n for _ in range(n)]
    for name, ro, co, nr, nc in (("A", 0, m, m, g), ("B", m, 0, g, m),
                                ("C", m, m, g, g), ("P", m+g, 0, 15, m),
                                ("Q", m+g, m, 15, g)):
        for i in range(nr):
            for j in range(nc):
                jac[ro+i][co+j] = blocks[name][i*nc+j]
    shift = blocks["shift"][0]
    matrix = [[(1.0 if i == j else 0.0)-shift*jac[i][j]
               for j in range(n)] for i in range(n)]
    return blocks, jac, matrix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_directory", type=Path)
    parser.add_argument("new_summary", type=Path)
    args = parser.parse_args()
    base = args.benchmark_directory
    contract = json.loads((base/"contract.json").read_text())
    with (base/"solve_repeats.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    with (base/"jvp_repeats.csv").open() as stream:
        jrows = list(csv.DictReader(stream))
    with (base/"cache_stats.csv").open() as stream:
        caches = list(csv.DictReader(stream))
    solutions = [json.loads(line) for line in (base/"solutions.jsonl").read_text().splitlines()]
    jvp_outputs = [json.loads(line) for line in (base/"jvp_outputs.jsonl").read_text().splitlines()]
    assert len(rows) == len(solutions) == 312
    assert len(jrows) == len(jvp_outputs) == 240
    inputs = {(m, g): load_input(base/f"input_m{m}_g{g}.csv", m, g)
              for g in (2, 4) for m in (9, 64, 256)}
    max_independent_residual = 0.0
    unique = set()
    full_vectors = {}
    for row, record in zip(rows, solutions):
        key = (int(row["M"]), int(row["G"]), row["phase"], row["method"], int(row["iteration"]))
        assert key == (record["m"], record["g"], record["phase"], record["method"], record["iteration"])
        assert key not in full_vectors
        x = record["solution"]
        assert len(x) == int(row["N"]) == record["m"]+record["g"]+15
        assert all(math.isfinite(v) for v in x)
        assert int(row["workers"]) == 1
        assert 0.0 <= float(row["full_backward_error"]) <= contract["max_backward_error"]
        full_vectors[key] = x
        identity = (key[0], key[1], bits(x))
        if identity in unique:
            continue
        unique.add(identity)
        blocks, _, matrix = inputs[key[:2]]
        residual = max(abs(math.fsum(a*b for a, b in zip(w, x))-rhs)
                       for w, rhs in zip(matrix, blocks["rhs"]))
        denominator = max(math.fsum(abs(v) for v in w) for w in matrix)*max(map(abs, x)) + max(map(abs, blocks["rhs"]))
        eta = residual/denominator if denominator else 0.0
        assert eta <= contract["max_backward_error"]
        max_independent_residual = max(max_independent_residual, eta)
    max_forward_difference = 0.0
    for (m, g, phase, method, iteration), x in full_vectors.items():
        y = full_vectors[m, g, phase, "dense_reference", iteration]
        max_forward_difference = max(max_forward_difference, max(abs(a-b)/(1.0+abs(b)) for a, b in zip(x, y)))
    jvp_by_case = {}
    jvp_bitwise = True
    for row, record in zip(jrows, jvp_outputs):
        m, g = int(row["M"]), int(row["G"])
        assert (m, g, row["method"], int(row["iteration"])) == (record["m"], record["g"], record["method"], record["iteration"])
        values = record["output"]
        assert len(values) == m+g+15 and all(math.isfinite(v) for v in values)
        if (m, g) in jvp_by_case:
            jvp_bitwise &= bits(values) == jvp_by_case[m, g]
        else:
            jvp_by_case[m, g] = bits(values)
            blocks, jac, _ = inputs[m, g]
            expected = [math.fsum(a*b for a, b in zip(row, blocks["rhs"])) for row in jac]
            assert max(abs(a-b) for a, b in zip(values, expected)) <= 1e-13
    groups = []
    for g in (2, 4):
        for m in (9, 64, 256):
            case = {"M": m, "G": g, "L": 15, "N": m+g+15}
            for phase, count in (("cold_factorization", 5), ("warm_reuse", 20)):
                methods = {method: [int(r["elapsed_ns"]) for r in rows
                           if (int(r["M"]), int(r["G"]), r["phase"], r["method"]) == (m, g, phase, method)]
                           for method in ("schur", "dense_reference")}
                assert all(len(v) == count for v in methods.values())
                case[phase] = {method: timing(values) for method, values in methods.items()}
                case[phase]["ratio_of_medians_dense_over_schur"] = statistics.median(methods["dense_reference"])/statistics.median(methods["schur"])
            methods = {method: [int(r["elapsed_ns"]) for r in jrows
                       if (int(r["M"]), int(r["G"]), r["method"]) == (m, g, method)]
                       for method in ("structured_jvp_into", "dense_matvec_into")}
            assert all(len(v) == 20 for v in methods.values())
            case["jvp"] = {method: timing(values) for method, values in methods.items()}
            case["jvp"]["ratio_of_medians_dense_over_structured"] = statistics.median(methods["dense_matvec_into"])/statistics.median(methods["structured_jvp_into"])
            cache = next(c for c in caches if (int(c["M"]), int(c["G"])) == (m, g))
            assert [int(cache[k]) for k in ("requests", "hits", "factorization_attempts", "factorization_failures")] == [21, 20, 1, 0]
            case["cache"] = {k: int(v) for k, v in cache.items()}
            groups.append(case)
    summary = {"schema": "C21I_BLOCK_BENCH_ANALYSIS_V1", "status": "PASS_SCOPED",
               "scope": contract["kind"], "native_performance": "NOT_EVALUATED",
               "c21h_backend_integrated": False, "global_error_bound": None,
               "solve_record_count": len(rows), "jvp_record_count": len(jrows),
               "unique_solutions_independently_checked": len(unique),
               "reported_max_backward_error": max(float(r["full_backward_error"]) for r in rows),
               "independent_python_fsum_max_backward_error": max_independent_residual,
               "max_component_difference_over_one_plus_dense_magnitude": max_forward_difference,
               "jvp_bitwise_identical_within_case": jvp_bitwise,
               "groups": groups,
               "input_artifact_sha256": {p.name: sha(p) for p in sorted(base.iterdir()) if p.is_file()},
               "limits": ["One current host; CPU0 affinity is not exclusive allocation.",
                          "Sub-microsecond timings and outliers require the raw dispersion; no universal speedup claim.",
                          "Cold means fresh factorization, not cache flushing or process startup.",
                          "Warm uses a deliberately fixed matrix, not a measured C21H Jacobian/shift reuse distribution.",
                          "The dense comparator is scalar reference code, not Faer/LAPACK or a deployed solver."]}
    with args.new_summary.open("x") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("groups", "input_artifact_sha256", "limits")}, indent=2))


if __name__ == "__main__":
    main()
