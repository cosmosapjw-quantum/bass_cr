"""Exact C++ max-flow seam for the unchanged, byte-pinned cross solver.

Only ``cross_flow._Network.max_flow`` is replaced, for one synchronous call.
The original prefix graph, FIFO decomposition, symmetrization and Solution
record remain in cross_flow.  Every returned integer flow is verified before
the original forward/reverse residual edges are changed.  This module does
not compile the executable or allocate a scientific execution budget.

The temporary class-method replacement requires a single-threaded caller;
nested calls are refused and the method is always restored in ``finally``.
"""

from __future__ import annotations

from collections import deque
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


CAPACITY_LIMIT = 1 << 126
PROTOCOL = "BASS_CR_INTEGER_FLOW_V1"
_RESEARCH = Path(__file__).resolve().parents[2]
_PATCH_ACTIVE = False


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load_pinned_module(name, relative_path, expected_sha256):
    """Use one module instance, checking its original file before execution."""
    path = (_RESEARCH / relative_path).resolve()
    _require(hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256,
             "PINNED_MODULE_BYTE_IDENTITY:" + name)
    existing = sys.modules.get(name)
    if existing is not None:
        location = getattr(existing, "__file__", None)
        _require(location is not None and Path(location).resolve() == path,
                 "PINNED_MODULE_INSTANCE_PATH:" + name)
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None,
             "PINNED_MODULE_SPEC:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if sys.modules.get(name) is module:
            del sys.modules[name]
        raise
    return module


cf = load_pinned_module(
    "cross_flow", "cr_he_energy_cross_20261028/implementation/cross_flow.py",
    "3bac2933c6b0b2c3de5fe28c05472ac5ad3e02afca57fb30566e27f051f7585f")


def _capacity(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(label + "_REQUIRES_NONNEGATIVE_INT")
    if value >= CAPACITY_LIMIT:
        raise OverflowError(label + "_MUST_BE_BELOW_2_POW_126")
    return value


def _index(value, size, label):
    _require(type(value) is int and 0 <= value < size,
             label + "_OUTSIDE_NODE_OR_EDGE_RANGE")
    return value


def _output_integer(token, label):
    _require(bool(token) and all("0" <= c <= "9" for c in token),
             label + "_REQUIRES_DECIMAL_DIGITS")
    # This also avoids Python's large-integer text conversion limit on a
    # malformed backend response.  Leading zeroes carry no numeric value.
    significant = token.lstrip("0") or "0"
    if len(significant) > 38:
        raise OverflowError(label + "_MUST_BE_BELOW_2_POW_126")
    return _capacity(int(significant), label)


def _executable_path(executable):
    _require(isinstance(executable, (str, os.PathLike)),
             "CPP_EXECUTABLE_PATH_REQUIRED")
    value = os.fspath(executable)
    _require(type(value) is str and bool(value), "CPP_EXECUTABLE_PATH_REQUIRED")
    path = Path(value).resolve()
    _require(path.is_file() and os.access(path, os.X_OK),
             "CPP_EXECUTABLE_NOT_FOUND_OR_NOT_EXECUTABLE")
    return path


def _max_flow(network, source, sink, bound, executable):
    """Validate a fresh network, execute once, certify, then restore flows."""
    _require(type(network.adj) is list and len(network.adj) >= 2,
             "CPP_NETWORK_ADJACENCY_REQUIRED")
    size = len(network.adj)
    _require(size <= (1 << 31) - 1, "CPP_NODE_COUNT_OUTSIDE_INT_RANGE")
    source = _index(source, size, "SOURCE")
    sink = _index(sink, size, "SINK")
    _require(source != sink, "CPP_SOURCE_EQUALS_SINK")
    bound = _capacity(bound, "FLOW_BOUND")
    _require(type(network.forward) is list, "CPP_FORWARD_REFERENCE_LIST_REQUIRED")
    count = len(network.forward)
    _require(count <= ((1 << 31) - 1) // 2,
             "CPP_EDGE_COUNT_OUTSIDE_INT_RANGE")

    rows = []
    occupied = set()
    for reference in network.forward:
        _require(type(reference) is tuple and len(reference) == 2,
                 "CPP_FORWARD_REFERENCE_REQUIRED")
        start = _index(reference[0], size, "EDGE_START")
        _require(type(network.adj[start]) is list, "CPP_ADJACENCY_ROW_REQUIRED")
        offset = _index(reference[1], len(network.adj[start]), "EDGE_OFFSET")
        edge = network.adj[start][offset]
        end = _index(edge.to, size, "EDGE_END")
        _require(start != end, "CPP_SELF_NETWORK_ARC_REFUSED")
        _require(type(network.adj[end]) is list, "CPP_ADJACENCY_ROW_REQUIRED")
        reverse_offset = _index(edge.reverse, len(network.adj[end]), "REVERSE_OFFSET")
        reverse = network.adj[end][reverse_offset]
        amount = _capacity(edge.initial, "EDGE_CAPACITY")
        remaining = _capacity(edge.capacity, "EDGE_RESIDUAL_CAPACITY")
        reverse_initial = _capacity(reverse.initial, "REVERSE_INITIAL_CAPACITY")
        reverse_remaining = _capacity(reverse.capacity, "REVERSE_RESIDUAL_CAPACITY")
        _require(remaining == amount and reverse_initial == reverse_remaining == 0,
                 "CPP_FRESH_NETWORK_REQUIRED")
        reverse_end = _index(reverse.to, size, "REVERSE_END")
        reverse_back = _index(reverse.reverse, len(network.adj[start]), "REVERSE_BACK_OFFSET")
        _require(reverse_end == start and reverse_back == offset,
                 "CPP_REVERSE_REFERENCE_MISMATCH")
        reverse_reference = (end, reverse_offset)
        _require(reference not in occupied and reverse_reference not in occupied,
                 "CPP_DUPLICATE_NETWORK_REFERENCE")
        occupied.update((reference, reverse_reference))
        rows.append((start, end, amount, edge, reverse))
    _require(all(type(row) is list for row in network.adj)
             and sum(map(len, network.adj)) == 2 * count,
             "CPP_UNLISTED_NETWORK_ARC")

    # Capacity and bound checks above precede even executable resolution.
    # In particular, an overflow is refused before launching any process.
    path = _executable_path(executable)
    lines = [PROTOCOL, f"{size} {count} {source} {sink} {bound}"]
    lines.extend(f"{u} {v} {capacity}" for u, v, capacity, _, _ in rows)
    payload = "\n".join(lines) + "\n"
    environment = dict(os.environ)
    environment.update(LC_ALL="C", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                       MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    try:
        process = subprocess.run([str(path)], input=payload, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 check=False, env=environment)
    except OSError as error:
        raise ValueError("CPP_PROCESS_START_FAILED:" + str(error)) from error
    if process.returncode != 0:
        raise ValueError("CPP_PROCESS_FAILED:" + str(process.returncode) + ":"
                         + process.stderr.strip()[:2000])

    tokens = process.stdout.split()
    _require(len(tokens) == count + 6 and tokens[0] == PROTOCOL,
             "CPP_OUTPUT_PROTOCOL_OR_LENGTH")
    returned_size = _output_integer(tokens[1], "OUTPUT_NODES")
    returned_count = _output_integer(tokens[2], "OUTPUT_EDGES")
    _require(returned_size == size and returned_count == count,
             "CPP_OUTPUT_NETWORK_IDENTITY")
    value = _output_integer(tokens[3], "OUTPUT_FLOW")
    phases = _output_integer(tokens[4], "OUTPUT_PHASES")
    augmentations = _output_integer(tokens[5], "OUTPUT_AUGMENTATIONS")
    _require(value <= bound, "CPP_FLOW_EXCEEDS_BOUND")
    _require(phases <= size and augmentations <= value,
             "CPP_COUNTER_RANGE")
    _require((value == 0 and phases == augmentations == 0)
             or (value > 0 and phases > 0 and augmentations > 0),
             "CPP_COUNTER_ZERO_INCONSISTENCY")
    flows = [_output_integer(token, "OUTPUT_EDGE_FLOW") for token in tokens[6:]]

    balance = [0] * size
    residual = [[] for _ in range(size)]
    for (start, end, capacity, _, _), flow in zip(rows, flows):
        _require(flow <= capacity, "CPP_EDGE_FLOW_OUTSIDE_CAPACITY")
        balance[start] -= flow
        balance[end] += flow
        if flow < capacity:
            residual[start].append(end)
        if flow:
            residual[end].append(start)
    _require(balance[source] == -value and balance[sink] == value,
             "CPP_SOURCE_OR_SINK_FLOW_MISMATCH")
    _require(all(balance[v] == 0 for v in range(size) if v not in (source, sink)),
             "CPP_INTERNAL_FLOW_CONSERVATION")
    reachable = {source}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in residual[vertex]:
            if neighbor not in reachable:
                reachable.add(neighbor)
                queue.append(neighbor)
    cut = sum(capacity for start, end, capacity, _, _ in rows
              if start in reachable and end not in reachable)
    _require(sink not in reachable and cut == value,
             "CPP_RESIDUAL_MINCUT_CERTIFICATE_FAILED")

    # No original network edge is changed until every returned certificate
    # obligation above is closed.  Existing edge references remain valid.
    for (_, _, capacity, edge, reverse), flow in zip(rows, flows):
        edge.capacity = capacity - flow
        reverse.capacity = flow
    network.phases = phases
    network.augmentations = augmentations
    return value


def solve(atoms, K, executable):
    """Return the original ``cross_flow.Solution`` through a checked backend.

    Execution time/memory and the executable's byte identity are owned by
    the caller's bounded runner.  No shell, compiler, worker thread or
    unmeasured fallback solver is launched by this wrapper.
    """
    global _PATCH_ACTIVE
    _require(not _PATCH_ACTIVE, "CPP_NESTED_MONKEYPATCH_REFUSED")
    data = cf.validate_atoms(atoms)
    cap = cf._exact_nonnegative(K, "K")
    previous = cf._Network.max_flow

    def replacement(network, source, sink, bound):
        return _max_flow(network, source, sink, bound, executable)

    _PATCH_ACTIVE = True
    try:
        cf._Network.max_flow = replacement
        return cf.solve(data, cap)
    finally:
        cf._Network.max_flow = previous
        _PATCH_ACTIVE = False
