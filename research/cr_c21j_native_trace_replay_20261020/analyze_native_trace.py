#!/usr/bin/env python3
"""Read-only reconstruction of C21H/I native callback requests.

No ODE is integrated, no provider is called, and no native binary is launched.
The complete physical integrated state (including tau and every ledger), the
unclamped callback time, and the event-cell scope define the C21I cache key.
Native EVAL strings are a separate, lower-dimensional projection.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import sys


SOURCE_PINS = {
    "cr_c21h_vigilode_bridge_20261019/optical_adapter.py":
        "53c8644b64f937fcca022c5307295d8666de8aee6c07244d139be139badcb387",
    "cr_c21i_callback_optimization_20261020/optimized_adapter.py":
        "bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e",
    "cr_c21e_event_native_20261018/src/reference_tau.py":
        "714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0",
    "cr_c21e_event_native_20261018/src/native_micro.py":
        "ce27acea344604c08159e08d6e703f66a85d51f0729b4e30aa2248a3337ecc27",
    "cr_c21e_event_native_20261018/src/event_coupler.py":
        "24386145f4337b2e01a32219a56ec2446080e4aa4a679a8f956a3eb7ff2ab819",
}
JOBS = ("H_common_ic_vigilode_rodas5p_base",
        "I_common_ic_vigilode_vectorized_base",
        "I_common_ic_vigilode_vectorized_fd_half")
PACKAGE_MANIFEST = "PACKAGE_PAYLOAD_SHA256SUMS.txt"
PACKAGE_MANIFEST_SHA256 = "40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a"
# This payload manifest is anchored by the independently retrieved archive
# 2722e479...468de3, whose complete compressed bytes and 155 payloads matched.
NATIVE_ARCHIVE_SHA256 = "2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3"


class TraceError(ValueError):
    """Insufficient or inconsistent captured evidence; never a physical no-go."""


def require(condition, message):
    if not condition:
        raise TraceError(message)


def bits(value):
    return struct.pack("<d", float(value))


def vector_bits(values):
    return b"".join(bits(v) for v in values)


def physical_key(t, u):
    """Same bit identity as (pack('<d',t), np.asarray(u,dtype='<f8').tobytes())."""
    require(math.isfinite(t) and all(map(math.isfinite, u)), "NONFINITE_KEY")
    return bits(t) + vector_bits(u)


def bit_equal(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(bit_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(bit_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return isinstance(b, (int, float)) and not isinstance(b, bool) and bits(a) == bits(b)
    return type(a) is type(b) and a == b


def lru_opportunities(keys, capacity=16):
    require(isinstance(capacity, int) and capacity > 0, "CACHE_CAPACITY")
    cache = OrderedDict()
    hits, previous, evictions = [], [], 0
    for i, key in enumerate(keys):
        hit = key in cache
        previous.append(cache.get(key))
        hits.append(hit)
        if hit:
            cache.move_to_end(key)
        cache[key] = i
        if len(cache) > capacity:
            cache.popitem(last=False)
            evictions += 1
    return {"hits": hits, "previous": previous, "evictions": evictions,
            "peak_entries": min(capacity, len(set(keys)))}


def gas_valid(g, helium):
    if len(g) != 4 or not all(map(math.isfinite, g)) or not math.isfinite(helium) or helium < 0:
        return False
    x, y, z, w = g
    return (0 <= x <= 1 and y >= 0 and z >= 0 and y + z <= 1 and w > 0
            and (helium > 0 or (y == 0 and z == 0)))


@dataclass(frozen=True)
class Cell:
    lo: float
    hi: float
    scales: tuple
    dynamic: tuple
    cohorts: int
    helium: float
    fd_relative: float
    time_fd_fraction: float

    @property
    def left(self):
        return self.lo + 1e-9 * (self.hi - self.lo)

    @property
    def right(self):
        return self.hi - 1e-9 * (self.hi - self.lo)

    def full(self, u):
        full = [0.] * (self.cohorts + 19)
        for index, value in zip(self.dynamic, u):
            full[index] = value
        return full

    def physical(self, t, z):
        require(self.lo <= t <= self.hi, "CALLBACK_OUTSIDE_CELL")
        require(len(z) == len(self.scales) == len(self.dynamic), "STATE_SHAPE")
        # Separate binary64 multiplication, exactly as the pinned NumPy ufunc.
        u = [float(value) * float(scale) for value, scale in zip(z, self.scales)]
        require(all(map(math.isfinite, u)), "PHYSICAL_NONFINITE")
        require(gas_valid(self.full(u)[self.cohorts:self.cohorts+4], self.helium), "PHYSICAL_GAS_DOMAIN")
        return u


def reconstruct_gas_nodes(cell, u, j, captured):
    """Recover saved offsets and independently match pinned node construction.

    The returned bit patterns must agree both with u+offset and with the
    source's finite search. Thus a subtraction that lost node information is
    not silently accepted merely because its rounded difference agrees.
    """
    require(len(captured["offsets"]) == 2, "GAS_TWO_NODES_REQUIRED")
    desired = cell.fd_relative * max(abs(float(u[j])), cell.scales[j])
    generated = None
    for k in range(24):
        candidates = {}
        for multiple in (-2, -1, 1, 2):
            v = u.copy()
            v[j] = float(u[j]) + multiple * math.ldexp(desired, -k)
            if (v[j] != u[j] and math.isfinite(v[j])
                    and gas_valid(cell.full(v)[cell.cohorts:cell.cohorts+4], cell.helium)):
                candidates[multiple] = v
        if -1 in candidates and 1 in candidates:
            generated = (candidates[-1], candidates[1], "central")
            break
        for sign in (1, -1):
            if sign in candidates and 2 * sign in candidates:
                generated = (candidates[sign], candidates[2*sign], "one_sided")
                break
        if generated:
            break
    require(generated is not None, "NO_SOURCE_GAS_NODES")
    require(generated[2] == captured["stencil"], "GAS_STENCIL_MISMATCH")
    reconstructed, exact_subtractions = [], 0
    for original_node, offset in zip(generated[:2], captured["offsets"]):
        require(bits(original_node[j] - u[j]) == bits(offset), "GAS_OFFSET_SOURCE_MISMATCH")
        node = u.copy()
        node[j] = u[j] + offset
        require(vector_bits(node) == vector_bits(original_node), "OFFSET_RESTORATION_ROUNDED")
        exact_subtractions += (Fraction(node[j]) - Fraction(u[j]) == Fraction(offset))
        reconstructed.append(node)
    return reconstructed, exact_subtractions


def reconstruct_time_nodes(cell, t, captured):
    desired = cell.time_fd_fraction * (cell.hi - cell.lo)
    generated = None
    for k in range(24):
        candidates = {}
        for multiple in (-2, -1, 1, 2):
            node = t + multiple * math.ldexp(desired, -k)
            if cell.left < node < cell.right and node != t:
                candidates[multiple] = node
        if -1 in candidates and 1 in candidates:
            generated = (candidates[-1], candidates[1], "central")
            break
        signs = (1, -1) if cell.right - t >= t - cell.left else (-1, 1)
        found = next((s for s in signs if s in candidates and 2*s in candidates), None)
        if found is not None:
            generated = (candidates[found], candidates[2*found], "one_sided")
            break
    require(generated is not None, "NO_SOURCE_TIME_NODES")
    require(bit_equal(list(generated[:2]), captured["nodes"]), "TIME_NODES_SOURCE_MISMATCH")
    require(generated[2] == captured["stencil"], "TIME_STENCIL_MISMATCH")
    require(bit_equal([x-t for x in captured["nodes"]], captured["offsets"]), "TIME_OFFSET_MISMATCH")
    return captured["nodes"]


def expand_requests(requests, fd_nodes, cell):
    """Expand captured RPC order into calls of original(t, physical_state)."""
    pointer, rows, counts = 0, [], Counter()

    def consume(kind, t, index=None):
        nonlocal pointer
        require(pointer < len(fd_nodes), "MISSING_DERIVATIVE_NODE")
        node = fd_nodes[pointer]
        pointer += 1
        require(node["kind"] == kind and bits(node["time"]) == bits(t), "DERIVATIVE_ORDER_MISMATCH")
        if index is not None:
            require(node["full_index"] == index, "GAS_FULL_INDEX_MISMATCH")
        return node

    for message in requests:
        op, t, ident = message["op"], message["t"], message["id"]
        u = cell.physical(t, message["y"])
        calls = []
        counts[op+"_requests"] += 1
        if op == "rhs":
            calls.append((t, u, "rhs"))
        elif op == "jacobian":
            calls.append((t, u, "jacobian_base"))
            for j, full_index in enumerate(cell.dynamic):
                if cell.cohorts <= full_index < cell.cohorts + 4:
                    node = consume("gas", t, full_index)
                    recovered, exact = reconstruct_gas_nodes(cell, u, j, node)
                    counts["gas_fd_columns"] += 1
                    counts["gas_fd_one_sided_columns"] += node["stencil"] == "one_sided"
                    counts["gas_offset_exact_subtractions"] += exact
                    for i, v in enumerate(recovered):
                        calls.append((t, v, "gas_node_"+str(i)))
            counts["analytic_tau_columns"] += cell.cohorts
            counts["exact_passive_columns"] += 15
        elif op == "partial_t":
            if t <= cell.left or t >= cell.right:
                counts["time_flat_branch"] += 1
            else:
                node = consume("time", t)
                points = reconstruct_time_nodes(cell, t, node)
                calls.append((t, u, "partial_t_base"))
                calls.extend((x, u.copy(), "time_node_"+str(i)) for i, x in enumerate(points))
                counts["time_fd_one_sided"] += node["stencil"] == "one_sided"
        else:
            raise TraceError("UNKNOWN_RPC_OPERATION")
        for tx, ux, role in calls:
            rows.append({"rpc_id": ident, "rpc_operation": op, "role": role,
                         "t": tx, "u": ux, "key_sha256": hashlib.sha256(physical_key(tx, ux)).hexdigest()})
    require(pointer == len(fd_nodes), "UNCONSUMED_DERIVATIVE_NODES")
    counts["original_rhs_evaluations"] = len(rows)
    return rows, dict(counts)


def captured_requests(rpc):
    requests, pending, terminal = [], None, None
    for row in rpc:
        msg = row["message"]
        if row["direction"] == "rust_to_python" and msg.get("type") == "request":
            require(pending is None and msg["id"] == len(requests)+1, "RPC_SEQUENCE")
            requests.append(msg)
            pending = msg["id"]
        elif row["direction"] == "python_to_rust" and "id" in msg:
            require(msg["id"] == pending and msg.get("ok") is True, "RPC_RESPONSE_FAILURE")
            pending = None
        elif row["direction"] == "rust_to_python" and msg.get("type") == "result":
            require(pending is None and terminal is None, "RPC_TERMINAL_SEQUENCE")
            terminal = msg
    require(pending is None and terminal is not None, "INCOMPLETE_RPC_TRACE")
    require(terminal.get("success") is True and terminal.get("ok") is True, "UNSUCCESSFUL_RPC_TRACE")
    return requests, terminal


class Inputs:
    def __init__(self, root, manifest_sha256=None):
        self.root, self.records = Path(root).resolve(), {}
        self.expected = None
        if manifest_sha256 is not None:
            raw = (self.root / PACKAGE_MANIFEST).read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            require(actual == manifest_sha256, "PACKAGE_MANIFEST_AUTHORITY_MISMATCH")
            self.records[PACKAGE_MANIFEST] = {"bytes": len(raw), "sha256": actual}
            self.expected = {}
            for line in raw.decode("ascii").splitlines():
                expected, relative = line.split("  ", 1)
                path = Path(relative)
                require(not path.is_absolute() and ".." not in path.parts, "MANIFEST_PATH")
                require(str(path) not in self.expected, "MANIFEST_DUPLICATE_PATH")
                self.expected[str(path)] = expected

    def read(self, relative):
        relative = Path(relative)
        require(not relative.is_absolute() and ".." not in relative.parts, "INPUT_PATH")
        require(relative.name != "LIVE_INVENTORY.json", "PRIVATE_PAYLOAD_EXCLUDED")
        raw = (self.root / relative).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if self.expected is not None:
            require(str(relative) in self.expected, "UNPINNED_RETURN_FILE:"+str(relative))
            require(actual == self.expected[str(relative)], "RETURN_PAYLOAD_IDENTITY:"+str(relative))
        self.records[str(relative)] = {"bytes": len(raw), "sha256": actual}
        return raw

    def json(self, relative):
        return json.loads(self.read(relative), parse_constant=lambda x: (_ for _ in ()).throw(TraceError("NONFINITE_JSON")))

    def jsonl(self, relative):
        return [json.loads(line) for line in self.read(relative).splitlines() if line.strip()]

    def unchanged(self):
        return all(hashlib.sha256((self.root/rel).read_bytes()).hexdigest() == r["sha256"]
                   for rel, r in self.records.items())


def endpoint_state(result):
    ledger = result["ledgers"]
    return (result["optical_depth"] + result["gas"] + ledger["photo"] + ledger["ci"] + ledger["rr"]
            + [ledger[k] for k in ("dr", "escape", "cmb", "photon_work", "gas_work", "heat")])


def numeric_comparison(a, b, scales):
    require(len(a) == len(b) == len(scales), "COMPARISON_STATE_SHAPE")
    differences = [x-y for x, y in zip(a, b)]
    return {"bitwise_equal": vector_bits(a) == vector_bits(b),
            "max_absolute_difference": max(map(abs, differences), default=0.),
            "max_fixed_scale_difference": max((abs(d)/s for d, s in zip(differences, scales)), default=0.),
            "differences": differences,
            "interpretation": "OBSERVED_ENDPOINT_DIFFERENCE_NOT_GLOBAL_ERROR_BOUND"}


def selected_timing(raw):
    # Deliberately exclude the full command, host inventory, and process list.
    wanted = ("User time (seconds)", "System time (seconds)",
              "Maximum resident set size (kbytes)", "Exit status")
    result = {}
    for line in raw.decode().splitlines():
        line = line.strip()
        for label in wanted:
            if line.startswith(label + ":"):
                result[label] = float(line[len(label)+1:].strip())
        label = "Elapsed (wall clock) time (h:mm:ss or m:ss):"
        if line.startswith(label):
            values = list(map(float, line[len(label):].strip().split(":")))
            result["elapsed_wall_s"] = sum(x * 60**k for k, x in enumerate(reversed(values)))
    return result


def analyze_job(inputs, name, out):
    rel = Path("evidence") / name
    result = inputs.json(rel/"result.json")
    receipt = inputs.json(rel/"JOB_RECEIPT.json")
    fixture = inputs.json(rel/"fixture.json")
    native_identity = inputs.json(rel/"NATIVE_IDENTITY.json")
    native = inputs.jsonl(rel/"native/native_points.jsonl")
    independent_balances = inputs.json(rel/"INDEPENDENT_BALANCES.json")
    for leaf in ("C21H_SOURCE_IDENTITY.json", "INPUT_IDENTITY.json"):
        inputs.json(rel/leaf)
    if name.startswith("I_"):
        inputs.json(rel/"C21I_SOURCE_IDENTITY.json")
    require(receipt["execution"] == "COMPLETE" and receipt["native_exit_code"] == 0, "JOB_NOT_SUCCESSFUL")
    require(receipt["native_executed"] is True and receipt["native_process_started"] is True, "NATIVE_NOT_EXECUTED")
    tol = result["tolerance_contract"]
    dynamic, full_scales = tuple(tol["dynamic_indices"]), tol["fixed_diagonal_scaling"]["values"]
    m = len(fixture["q"])
    expected_dynamic = tuple(j for j in range(m+19) if not (fixture["Y"] == 0 and j in (m+1, m+2)))
    require(dynamic == expected_dynamic, "NONCANONICAL_DYNAMIC_MAP")
    require(len(full_scales) == m+19 and all(math.isfinite(s) and s > 0 for s in full_scales), "SCALE_DOMAIN")
    rows, segments, offset = [], [], 0
    callback_totals = Counter()
    native_cost_full_hit, native_cost_string_hit = [], []
    native_duplicate_only = Counter()
    accepted, raw_results = [], []
    for segment_index, segment_path in enumerate(sorted((inputs.root/rel/"segments").glob("segment_*"))):
        seg_rel = rel/"segments"/segment_path.name
        config = inputs.json(seg_rel/"config.json")
        segment_receipt = inputs.json(seg_rel/"receipt.json")
        process_exit = inputs.json(seg_rel/"process_exit.json")
        raw_result = inputs.json(seg_rel/"result.json")
        nodes = inputs.json(seg_rel/"derivative_nodes.json")
        rpc = inputs.jsonl(seg_rel/"rpc.jsonl")
        requests, terminal = captured_requests(rpc)
        require(bit_equal(terminal, raw_result), "RPC_TERMINAL_RESULT_MISMATCH")
        require(segment_receipt["status"] == "COMPLETE" and process_exit["exit_code"] == 0, "SEGMENT_NOT_SUCCESSFUL")
        cell = Cell(config["t0"], config["t1"], tuple(full_scales[j] for j in dynamic),
                    dynamic, m, fixture["Y"], tol["gas_fd_relative"], tol["time_fd_fraction"])
        require(cell.lo <= cell.left < cell.right <= cell.hi, "CELL_CLAMP_DOMAIN")
        expanded, counted = expand_requests(requests, nodes, cell)
        for key, value in segment_receipt["callbacks"].items():
            if key in counted or key in ("gas_fd_one_sided_columns", "time_fd_one_sided", "time_flat_branch"):
                require(counted.get(key, 0) == value, "CALLBACK_COUNTER_MISMATCH:"+key)
        require(len(requests) == segment_receipt["rpc_requests"], "RPC_COUNTER_MISMATCH")
        native_slice = native[offset:offset+len(expanded)]
        require(len(native_slice) == len(expanded), "MISSING_NATIVE_ROWS")
        full_lru = lru_opportunities([physical_key(x["t"], x["u"]) for x in expanded])
        projected_lru = lru_opportunities([x["request"] for x in native_slice])
        roles = Counter()
        for i, (row, point) in enumerate(zip(expanded, native_slice)):
            gas = cell.full(row["u"])[m:m+4]
            clamped = min(max(row["t"], cell.left), cell.right)
            args = [math.exp(clamped), fixture["nh0"], fixture["nh0"]*fixture["Y"], *gas]
            request = "EVAL\t" + "\t".join(format(float(x), ".17e") for x in args)
            require(request == point["request"], "NATIVE_REQUEST_RECONSTRUCTION_MISMATCH")
            response = point.get("response", "").split("\t")
            require(response[0] == "OK" and len(response) == 24, "NATIVE_RESPONSE_MISSING_OR_BAD")
            require(all(math.isfinite(float(x)) for x in response[1:]), "NATIVE_RESPONSE_NONFINITE")
            hit, projected_hit = full_lru["hits"][i], projected_lru["hits"][i]
            row.update(cell=segment_index, native_row=offset+i,
                       full_key_lru16_hit=hit, native_string_lru16_hit=projected_hit,
                       native_logged_seconds=point["seconds"])
            roles[row["role"]] += hit
            if hit:
                native_cost_full_hit.append(point["seconds"])
            if projected_hit:
                native_cost_string_hit.append(point["seconds"])
            if projected_hit and not hit:
                previous = expanded[projected_lru["previous"][i]]
                changed = [dynamic[j] for j, (x, y) in enumerate(zip(row["u"], previous["u"])) if bits(x) != bits(y)]
                categories = []
                if bits(row["t"]) != bits(previous["t"]):
                    categories.append("time")
                if any(j < m for j in changed):
                    categories.append("optical_depth")
                if any(m <= j < m+4 for j in changed):
                    categories.append("gas")
                if any(j >= m+4 for j in changed):
                    categories.append("passive_ledgers")
                native_duplicate_only["+".join(categories) or "LRU_HISTORY_ONLY"] += 1
        for t, z in zip(raw_result["accepted_times"], raw_result["accepted_states"]):
            accepted.append({"cell": segment_index, "t": t, "full_physical_state": cell.full(cell.physical(t, z))})
        callback_totals.update(segment_receipt["callbacks"])
        segments.append({"cell": segment_index, "lo": cell.lo, "hi": cell.hi,
                         "requests": len(expanded), "full_key_lru16_hits": sum(full_lru["hits"]),
                         "full_key_lru16_misses": len(expanded)-sum(full_lru["hits"]),
                         "full_key_lru16_evictions": full_lru["evictions"],
                         "native_string_lru16_hits": sum(projected_lru["hits"]),
                         "hit_roles": dict(roles), "expanded_counters": counted,
                         "segment_wall_s": segment_receipt["wall_s"],
                         "segment_after_cleanup_wall_s": process_exit["wall_s_after_cleanup"]})
        offset += len(expanded)
        rows.extend(expanded)
        raw_results.append(raw_result)
    require(offset == len(native) == result["rhs_evaluations"] == receipt["native_calls_attempted"], "TOTAL_NATIVE_CALL_MISMATCH")
    require(vector_bits(accepted[-1]["full_physical_state"]) == vector_bits(endpoint_state(result)), "ENDPOINT_FULL_STATE_MISMATCH")
    response_map, inconsistent_responses = {}, 0
    for point in native:
        if point["request"] in response_map and response_map[point["request"]] != point["response"]:
            inconsistent_responses += 1
        response_map[point["request"]] = point["response"]
    # Validate every inspected payload listed in the immutable job receipt.
    for relative, actual in inputs.records.items():
        prefix = str(rel) + "/"
        if relative.startswith(prefix):
            leaf = relative[len(prefix):]
            if leaf in receipt["payload_files"]:
                require(actual == receipt["payload_files"][leaf], "PAYLOAD_HASH_MISMATCH:"+relative)
    total_hits = sum(s["full_key_lru16_hits"] for s in segments)
    timing_name = name.lower().replace("h_common", "h_common", 1)+".time.txt"
    timing = selected_timing(inputs.read(Path("logs")/timing_name))
    with (out/(name+"_reconstructed_requests.jsonl")).open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, allow_nan=False, separators=(",", ":"))+"\n")
    summary = {
        "job": name, "scope": "captured common_ic native job only",
        "native_calls_historically_executed": len(native), "native_calls_executed_by_this_analysis": 0,
        "fixture_sha256": receipt["fixture_sha256"],
        "native_binary_identity_from_receipt": {k: native_identity[k] for k in ("sha256", "bytes", "owner", "status")},
        "bridge_binary_identity_from_receipt": {k: receipt["bridge_identity"][k] for k in ("sha256", "bytes")},
        "vigilode_commit": result["vigilode_commit"], "reference_source_sha256": result["original_reference_source_sha256"],
        "full_physical_request_reconstruction": "PASS_SCOPED_SOURCE_RULES_PLUS_ALL_NATIVE_REQUEST_STRINGS",
        "native_request_string_comparisons": len(native), "native_request_string_mismatches": 0,
        "full_key_definition": "event-cell instance; little-endian binary64 unclamped t and entire physical integrated u, including tau and every passive ledger; signed zeros preserved",
        "full_key_lru16_hits": total_hits, "full_key_lru16_misses": len(native)-total_hits,
        "full_key_lru16_hit_fraction": total_hits/len(native),
        "native_string_distinct": len(response_map),
        "native_string_lru16_hits_with_cell_reset": sum(s["native_string_lru16_hits"] for s in segments),
        "native_string_lru16_hits_without_cell_reset": sum(lru_opportunities([x["request"] for x in native])["hits"]),
        "native_projection_hits_not_full_rhs_hits": dict(native_duplicate_only),
        "duplicate_native_request_response_disagreements": inconsistent_responses,
        "exact_mode_historical_execution": "NOT_RUN",
        "cache_performance_prediction_status": "OPPORTUNITY_COUNT_ONLY_NOT_MEASURED_SPEEDUP",
        "global_error_bound": None,
        "timings": {
            "process": timing, "job_receipt_wall_s": receipt["wall_s"], "reference_result_wall_s": result["wall_s"],
            "segment_wall_sum_s": math.fsum(s["segment_wall_s"] for s in segments),
            "segment_after_cleanup_wall_sum_s": math.fsum(s["segment_after_cleanup_wall_s"] for s in segments),
            "instrumented_original_rhs_execution_s": callback_totals.get("original_rhs_execution_ns", 0)/1e9 if "original_rhs_execution_ns" in callback_totals else None,
            "native_logged_request_intervals_sum_s": math.fsum(x["seconds"] for x in native),
            "native_logged_intervals_at_full_key_hits_s": math.fsum(native_cost_full_hit),
            "native_logged_intervals_at_native_string_hits_s": math.fsum(native_cost_string_hit),
            "native_timer_scope": "stdin write/flush and response wait/read; excludes response parsing/validation, microphysics setup, Python RHS assembly and log flush after timestamp",
            "interpretation": "Nested observed timer scopes; not independent additive phases and not a cache-on wall-time prediction",
        },
        "callback_counters_summed": dict(callback_totals),
        "solver_counters": {k: result["solver_diagnostics"][k] for k in ("nfev", "njev", "nlu", "accepted_steps", "rhs_evaluations")},
        "segments": segments, "endpoint_full_physical_state": endpoint_state(result),
        "endpoint": {k: result[k] for k in ("gas", "photons", "temperature_K", "photon_number", "photon_energy_eV_H", "optical_depth", "log_survivor", "ledgers", "number_defect_H", "energy_defect_eV_H", "species_defect")},
        "independent_balance_record": independent_balances,
    }
    return summary, result, accepted, raw_results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True, help="Frozen repo research/ directory")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    require(sys.float_info.radix == 2 and sys.float_info.mant_dig == 53, "BINARY64_RUNTIME_REQUIRED")
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = Inputs(args.archive, PACKAGE_MANIFEST_SHA256)
    sources = Inputs(args.source_root)
    for rel, expected in SOURCE_PINS.items():
        sources.read(rel)
        require(sources.records[rel]["sha256"] == expected, "SOURCE_PIN_MISMATCH:"+rel)
    jobs = [analyze_job(inputs, name, args.out) for name in JOBS]
    h, i, f = (job[1] for job in jobs)
    scales = h["tolerance_contract"]["fixed_diagonal_scaling"]["values"]
    endpoint_keys = tuple(jobs[0][0]["endpoint"])
    comparison = {
        "H_I_endpoint": numeric_comparison(endpoint_state(h), endpoint_state(i), scales),
        "H_I_all_endpoint_fields_bitwise_equal": all(bit_equal(h[k], i[k]) for k in endpoint_keys),
        "H_I_all_raw_segment_result_objects_bitwise_equal": bit_equal(jobs[0][3], jobs[1][3]),
        "H_I_complete_accepted_physical_traces_bitwise_equal": bit_equal(jobs[0][2], jobs[1][2]),
        "H_I_accepted_points_including_cell_initial_points": len(jobs[0][2]),
        "I_FDhalf_endpoint": numeric_comparison(endpoint_state(f), endpoint_state(i), scales),
        "I_FDhalf_temperature_change_K": f["temperature_K"]-i["temperature_K"],
        "I_FDhalf_photon_number_change_H": f["photon_number"]-i["photon_number"],
        "I_FDhalf_photon_energy_change_eV_H": f["photon_energy_eV_H"]-i["photon_energy_eV_H"],
        "I_FDhalf_accepted_grid_bitwise_equal": all(bit_equal(a["accepted_times"], b["accepted_times"]) for a, b in zip(jobs[1][3], jobs[2][3])),
        "global_error_bound": None,
        "wall_speedup_generalization": "NOT_ESTABLISHED_SINGLE_SEQUENTIAL_NATIVE_RUN_PER_MODE",
    }
    unchanged = inputs.unchanged() and sources.unchanged()
    require(unchanged, "INPUT_CHANGED_DURING_READ_ONLY_ANALYSIS")
    summary = {"schema": "C21J_NATIVE_CAPTURE_TRACE_ANALYSIS_V1",
               "execution_scope": "read-only analysis of new saved native return; no ODE, native provider, old suite, or manufactured benchmark execution",
               "python": sys.version, "platform": platform.platform(),
               "source_pins": sources.records, "inputs": inputs.records,
               "native_archive_sha256_authority": NATIVE_ARCHIVE_SHA256,
               "package_payload_manifest_sha256": PACKAGE_MANIFEST_SHA256,
               "compressed_archive_rehashed_by_this_analysis": False,
               "return_admission": "Every inspected return file is checked against the frozen archive payload manifest; full archive identity was verified separately at intake.",
               "original_input_bytes_unchanged": unchanged,
               "private_live_inventory_read_or_copied": False,
               "global_error_bound": None,
               "jobs": [job[0] for job in jobs], "comparisons": comparison}
    with (args.out/"ANALYSIS.json").open("x") as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": "PASS_SCOPED", "output": str(args.out/"ANALYSIS.json"),
                      "native_calls_executed_by_this_analysis": 0,
                      "full_key_hits": [job[0]["full_key_lru16_hits"] for job in jobs],
                      "H_I_full_state_and_ledgers_equal": comparison["H_I_all_endpoint_fields_bitwise_equal"],
                      "H_I_complete_accepted_traces_equal": comparison["H_I_complete_accepted_physical_traces_bitwise_equal"],
                      "I_FDhalf_max_fixed_scale_change": comparison["I_FDhalf_endpoint"]["max_fixed_scale_difference"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
