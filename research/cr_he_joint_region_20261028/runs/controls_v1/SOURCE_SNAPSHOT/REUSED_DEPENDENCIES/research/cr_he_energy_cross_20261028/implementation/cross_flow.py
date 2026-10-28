"""Exact cross-partition fractional matching through a compact flow network.

Only pairs of distinct partitions with ``E_i + E_j <= K`` are counted.
Each atom has a nonnegative rational capacity ``w_i``; unused capacity is a
single event. This module does not assign a physical value to K or reconstruct
an exclusive helium kernel.

The bipartite double cover has capacity w_i on source->L_i and R_i->sink.
An allowed L_i->R_j edge has capacity greater than total atom mass. Its
maximum flow F gives C_max=F/2: symmetrize the directed pair flow by
``x_ij=(f_ij+f_ji)/2``. Conversely, any fractional undirected matching gives
a directed feasible flow of twice its mass. Thus this transformation is exact.

Right vertices are represented by one sorted prefix chain per partition.
L_i connects only to the highest eligible vertex of each other partition;
downward infinite-capacity chain arcs reach precisely its eligible atoms.
This uses 2n+2 vertices and O(k*n) edges for k partitions, avoiding the
explicit O(n**2) pair graph. Sorting/bisection, exact rational bit costs,
integer-capacity max flow, and flow decomposition remain separate costs.
In particular, no linear-time claim is made for the iterative Dinic solver.

All public numeric inputs must be Python int or Fraction, excluding bool.
No imports, scientific execution, or tests were performed while authoring.
"""

from __future__ import annotations

from bisect import bisect_right
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from math import lcm


@dataclass(frozen=True, slots=True)
class Atom:
    key: str
    energy_eV: Fraction | int
    coefficient: Fraction | int
    partition: int = 0


@dataclass(frozen=True, slots=True)
class Event:
    """A single or an unordered pair; the coefficient counts events."""

    electrons: tuple[str, ...]
    coefficient: Fraction


@dataclass(frozen=True, slots=True)
class Solution:
    cross_C: Fraction
    pairs: tuple[Event, ...]
    singles: tuple[Event, ...]
    flow_value: Fraction
    mincut_capacity: Fraction
    mincut_dual: tuple[tuple[str, Fraction], ...]
    reachable_nodes: tuple[int, ...]
    source_side_atom_keys: tuple[str, ...]
    target_side_atom_keys: tuple[str, ...]
    atom_count: int
    partition_count: int
    network_nodes: int
    network_edges: int
    capacity_denominator: int
    dinic_phases: int
    augmentations: int


def _exact_nonnegative(value: object, label: str) -> Fraction:
    if type(value) not in (int, Fraction):
        raise ValueError(f"{label}_REQUIRES_INT_OR_FRACTION")
    answer = Fraction(value)
    if answer < 0:
        raise ValueError(f"{label}_NEGATIVE")
    return answer


def validate_atoms(atoms: object) -> tuple[Atom, ...]:
    """Validate and normalize a finite list/tuple, preserving atom order."""

    if type(atoms) not in (list, tuple):
        raise ValueError("ATOMS_REQUIRE_FINITE_LIST_OR_TUPLE")
    seen: set[str] = set()
    normalized: list[Atom] = []
    for atom in atoms:
        if not isinstance(atom, Atom):
            raise ValueError("ATOM_RECORD_REQUIRED")
        if type(atom.key) is not str or not atom.key:
            raise ValueError("ATOM_KEY_REQUIRES_NONEMPTY_STRING")
        if atom.key in seen:
            raise ValueError("DUPLICATE_ATOM_KEY")
        seen.add(atom.key)
        if type(atom.partition) is not int or atom.partition < 0:
            raise ValueError("PARTITION_REQUIRES_NONNEGATIVE_INT")
        normalized.append(
            Atom(
                atom.key,
                _exact_nonnegative(atom.energy_eV, "ENERGY"),
                _exact_nonnegative(atom.coefficient, "COEFFICIENT"),
                atom.partition,
            )
        )
    return tuple(normalized)


@dataclass(slots=True)
class _Edge:
    to: int
    reverse: int
    capacity: int
    initial: int


class _Network:
    def __init__(self, size: int):
        self.adj: list[list[_Edge]] = [[] for _ in range(size)]
        self.forward: list[tuple[int, int]] = []
        self.phases = 0
        self.augmentations = 0

    def add(self, start: int, end: int, capacity: int) -> tuple[int, int]:
        if start == end or capacity < 0:
            raise RuntimeError("INVALID_INTERNAL_NETWORK_EDGE")
        reference = (start, len(self.adj[start]))
        reverse_index = len(self.adj[end])
        self.adj[start].append(_Edge(end, reverse_index, capacity, capacity))
        self.adj[end].append(_Edge(start, reference[1], 0, 0))
        self.forward.append(reference)
        return reference

    def edge_flow(self, reference: tuple[int, int]) -> int:
        start, offset = reference
        edge = self.adj[start][offset]
        value = edge.initial - edge.capacity
        if value < 0 or value > edge.initial:
            raise RuntimeError("INTERNAL_EDGE_FLOW_OUTSIDE_CAPACITY")
        return value

    def _levels(self, source: int) -> list[int]:
        level = [-1] * len(self.adj)
        level[source] = 0
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            next_level = level[vertex] + 1
            for edge in self.adj[vertex]:
                if edge.capacity > 0 and level[edge.to] < 0:
                    level[edge.to] = next_level
                    queue.append(edge.to)
        return level

    def _augment_one(
        self,
        source: int,
        sink: int,
        maximum: int,
        level: list[int],
        cursor: list[int],
    ) -> int:
        """One admissible-path augmentation, without recursive Python calls."""

        vertices = [source]
        path: list[tuple[int, int]] = []
        bottleneck = [maximum]
        while vertices:
            vertex = vertices[-1]
            if vertex == sink:
                amount = bottleneck[-1]
                if amount <= 0:
                    raise RuntimeError("INTERNAL_NONPOSITIVE_AUGMENTATION")
                for start, offset in path:
                    edge = self.adj[start][offset]
                    edge.capacity -= amount
                    self.adj[edge.to][edge.reverse].capacity += amount
                return amount

            outgoing = self.adj[vertex]
            while cursor[vertex] < len(outgoing):
                offset = cursor[vertex]
                edge = outgoing[offset]
                if edge.capacity > 0 and level[edge.to] == level[vertex] + 1:
                    path.append((vertex, offset))
                    vertices.append(edge.to)
                    bottleneck.append(min(bottleneck[-1], edge.capacity))
                    break
                cursor[vertex] += 1
            else:
                # Residual reverse edges point backwards in this level graph;
                # a dead vertex cannot acquire a new admissible route in it.
                level[vertex] = -1
                vertices.pop()
                bottleneck.pop()
                if path:
                    parent, _offset = path.pop()
                    cursor[parent] += 1
        return 0

    def max_flow(self, source: int, sink: int, bound: int) -> int:
        total = 0
        while total < bound:
            level = self._levels(source)
            if level[sink] < 0:
                break
            self.phases += 1
            cursor = [0] * len(self.adj)
            while total < bound:
                amount = self._augment_one(
                    source, sink, bound - total, level, cursor
                )
                if amount == 0:
                    break
                self.augmentations += 1
                total += amount
        return total

    def reachable(self, source: int) -> set[int]:
        reached = {source}
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            for edge in self.adj[vertex]:
                if edge.capacity > 0 and edge.to not in reached:
                    reached.add(edge.to)
                    queue.append(edge.to)
        return reached

    def cut_capacity(self, reachable: set[int]) -> int:
        total = 0
        for start, offset in self.forward:
            edge = self.adj[start][offset]
            if start in reachable and edge.to not in reachable:
                total += edge.initial
        return total


def solve(atoms: object, K_eV: object) -> Solution:
    """Return an exact maximum cross-pair witness and atomwise singles.

    The numeric vertex IDs used in ``reachable_nodes`` are source=0,
    L_i=1+i, R_i=1+n+i, sink=1+2n, with i the validated input order.
    ``mincut_dual`` contains a half-integral fractional vertex cover derived
    from that minimum cut. The caller can independently verify each allowed
    edge, primal marginal, objective, and this dual certificate.

    Equal-energy ordering uses atom keys; events are returned in stable key
    order. Zero-weight records are omitted from the event tuples. Empty data,
    all-zero masses, missing eligible pairs, and one-partition data are valid.
    """

    data = validate_atoms(atoms)
    cap = _exact_nonnegative(K_eV, "K")
    n = len(data)
    source = 0
    sink = 2 * n + 1
    network = _Network(sink + 1)

    denominator = 1
    for atom in data:
        denominator = lcm(denominator, atom.coefficient.denominator)
    capacities = [
        atom.coefficient.numerator * (denominator // atom.coefficient.denominator)
        for atom in data
    ]
    total_capacity = sum(capacities)
    infinite = total_capacity + 1

    groups: dict[int, list[int]] = {}
    for index, atom in enumerate(data):
        groups.setdefault(atom.partition, []).append(index)
    for indices in groups.values():
        indices.sort(key=lambda i: (data[i].energy_eV, data[i].key))
    group_energies = {
        partition: [data[i].energy_eV for i in indices]
        for partition, indices in groups.items()
    }

    source_arcs: list[tuple[int, int]] = []
    sink_arcs: list[tuple[int, int]] = []
    for index, amount in enumerate(capacities):
        source_arcs.append(network.add(source, 1 + index, amount))
        sink_arcs.append(network.add(1 + n + index, sink, amount))

    chain_arcs: list[tuple[int, int] | None] = [None] * n
    for partition in sorted(groups):
        indices = groups[partition]
        for offset in range(1, len(indices)):
            index = indices[offset]
            lower = indices[offset - 1]
            chain_arcs[index] = network.add(
                1 + n + index, 1 + n + lower, infinite
            )

    # Every source atom enters a destination partition at most once. The
    # metadata below later decomposes those aggregate flows into exact pairs.
    incoming: list[list[tuple[int, tuple[int, int]]]] = [[] for _ in range(n)]
    for left_index, atom in enumerate(data):
        for partition in sorted(groups):
            if partition == atom.partition:
                continue
            endpoint = bisect_right(
                group_energies[partition], cap - atom.energy_eV
            ) - 1
            if endpoint < 0:
                continue
            right_index = groups[partition][endpoint]
            edge = network.add(1 + left_index, 1 + n + right_index, infinite)
            incoming[right_index].append((left_index, edge))

    integer_flow = network.max_flow(source, sink, total_capacity)
    reachable = network.reachable(source)
    cut = network.cut_capacity(reachable)
    if sink in reachable or cut != integer_flow:
        raise RuntimeError("INTERNAL_MAX_FLOW_MIN_CUT_MISMATCH")
    if sum(network.edge_flow(edge) for edge in source_arcs) != integer_flow:
        raise RuntimeError("INTERNAL_SOURCE_FLOW_MISMATCH")
    if sum(network.edge_flow(edge) for edge in sink_arcs) != integer_flow:
        raise RuntimeError("INTERNAL_SINK_FLOW_MISMATCH")

    # Values below are numerators at denominator 2*denominator after
    # symmetrization. Each directed flow block contributes once to its
    # unordered pair; the reverse block, if present, contributes again.
    pair_numerators: dict[tuple[str, str], int] = {}
    directed_total = 0
    for partition in sorted(groups):
        queue: deque[tuple[int, int]] = deque()
        pending = 0
        for right_index in reversed(groups[partition]):
            for left_index, edge in incoming[right_index]:
                amount = network.edge_flow(edge)
                if amount:
                    queue.append((left_index, amount))
                    pending += amount
            demanded = network.edge_flow(sink_arcs[right_index])
            if demanded > pending:
                raise RuntimeError("INTERNAL_PREFIX_DECOMPOSITION_SHORTAGE")
            pending -= demanded
            while demanded:
                if not queue:
                    raise RuntimeError("INTERNAL_EMPTY_DECOMPOSITION_QUEUE")
                left_index, available = queue.popleft()
                allocated = min(available, demanded)
                left = data[left_index]
                right = data[right_index]
                if left.partition == right.partition or left.energy_eV + right.energy_eV > cap:
                    raise RuntimeError("INTERNAL_DECOMPOSED_PAIR_SUPPORT_FAILURE")
                keys = tuple(sorted((left.key, right.key)))
                pair_numerators[keys] = pair_numerators.get(keys, 0) + allocated
                directed_total += allocated
                demanded -= allocated
                available -= allocated
                if available:
                    queue.appendleft((left_index, available))
            chain = chain_arcs[right_index]
            carried = network.edge_flow(chain) if chain is not None else 0
            if pending != carried:
                raise RuntimeError("INTERNAL_PREFIX_FLOW_CONSERVATION_FAILURE")
        if pending or queue:
            raise RuntimeError("INTERNAL_UNCONSUMED_PREFIX_FLOW")
    if directed_total != integer_flow:
        raise RuntimeError("INTERNAL_PAIR_FLOW_TOTAL_MISMATCH")

    used_numerators = {atom.key: 0 for atom in data}
    pairs: list[Event] = []
    for keys, numerator in sorted(pair_numerators.items()):
        if numerator <= 0:
            raise RuntimeError("INTERNAL_NONPOSITIVE_PAIR_RECORD")
        used_numerators[keys[0]] += numerator
        used_numerators[keys[1]] += numerator
        pairs.append(Event(keys, Fraction(numerator, 2 * denominator)))

    singles: list[Event] = []
    for atom, amount in sorted(zip(data, capacities), key=lambda row: row[0].key):
        residual = 2 * amount - used_numerators[atom.key]
        if residual < 0:
            raise RuntimeError("INTERNAL_ATOM_MARGINAL_OVERRUN")
        if residual:
            singles.append(Event((atom.key,), Fraction(residual, 2 * denominator)))

    cross_C = Fraction(integer_flow, 2 * denominator)
    if sum((event.coefficient for event in pairs), Fraction(0)) != cross_C:
        raise RuntimeError("INTERNAL_CROSS_OBJECTIVE_MISMATCH")

    dual = tuple(sorted(
        (
            atom.key,
            Fraction(int(1 + index not in reachable) + int(1 + n + index in reachable), 2),
        )
        for index, atom in enumerate(data)
    ))
    dual_by_key = dict(dual)
    if sum((atom.coefficient * dual_by_key[atom.key] for atom in data), Fraction(0)) != cross_C:
        raise RuntimeError("INTERNAL_MINCUT_DUAL_OBJECTIVE_MISMATCH")

    return Solution(
        cross_C=cross_C,
        pairs=tuple(pairs),
        singles=tuple(singles),
        flow_value=Fraction(integer_flow, denominator),
        mincut_capacity=Fraction(cut, denominator),
        mincut_dual=dual,
        reachable_nodes=tuple(sorted(reachable)),
        source_side_atom_keys=tuple(sorted(
            atom.key for index, atom in enumerate(data) if 1 + index in reachable
        )),
        target_side_atom_keys=tuple(sorted(
            atom.key for index, atom in enumerate(data) if 1 + n + index in reachable
        )),
        atom_count=n,
        partition_count=len(groups),
        network_nodes=len(network.adj),
        network_edges=len(network.forward),
        capacity_denominator=denominator,
        dinic_phases=network.phases,
        augmentations=network.augmentations,
    )
