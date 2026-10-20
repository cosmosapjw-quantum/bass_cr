"""Bounded tests of trace reconstruction; no ODE or native process execution."""
from copy import deepcopy
import math
import unittest

from analyze_native_trace import (
    Cell, TraceError, bit_equal, bits, captured_requests, expand_requests,
    lru_opportunities, physical_key, reconstruct_gas_nodes,
)


def example():
    scales = [1.] * 20
    scales[4] = 2.
    cell = Cell(0., 1., tuple(scales), tuple(range(20)), 1, .08, 2.**-10, 2.**-12)
    z = [0., .25, .125, .0625, 1.] + [0.] * 15
    return cell, z


class ExactKeyTests(unittest.TestCase):
    def test_signed_zero_is_preserved_in_time_and_state(self):
        self.assertNotEqual(physical_key(0., [1.]), physical_key(-0., [1.]))
        self.assertNotEqual(physical_key(1., [0.]), physical_key(1., [-0.]))
        self.assertFalse(bit_equal([0.], [-0.]))

    def test_entire_state_and_unclamped_time_matter(self):
        cell, z = example()
        u = cell.physical(0., z)
        changed = u.copy()
        changed[-1] = math.nextafter(0., 1.)
        self.assertEqual(u[1:5], changed[1:5])
        self.assertNotEqual(physical_key(0., u), physical_key(0., changed))
        self.assertEqual(min(max(0., cell.left), cell.right), min(max(cell.left, cell.left), cell.right))
        self.assertNotEqual(physical_key(0., u), physical_key(cell.left, u))

    def test_lru_capacity_and_cell_reset(self):
        data = list(range(17)) + [0, 16]
        result = lru_opportunities(data, 16)
        self.assertEqual(result["hits"], [False] * 18 + [True])
        self.assertEqual(result["evictions"], 2)
        self.assertEqual(lru_opportunities([0])["hits"], [False])
        self.assertEqual(lru_opportunities([0])["hits"], [False])


class ReconstructionTests(unittest.TestCase):
    def test_nonunit_thermal_scale(self):
        cell, z = example()
        self.assertEqual(cell.physical(0., z)[4], 2.)
        self.assertNotEqual(physical_key(0., z), physical_key(0., cell.physical(0., z)))

    def test_central_and_one_sided_nodes(self):
        cell, z = example()
        u = cell.physical(0., z)
        central, exact = reconstruct_gas_nodes(cell, u, 1, {"offsets": [-2.**-10, 2.**-10], "stencil": "central"})
        self.assertEqual([v[1] for v in central], [.25-2.**-10, .25+2.**-10])
        self.assertEqual(exact, 2)
        u[1] = 0.
        one_sided, exact = reconstruct_gas_nodes(cell, u, 1, {"offsets": [2.**-10, 2.**-9], "stencil": "one_sided"})
        self.assertEqual([v[1] for v in one_sided], [2.**-10, 2.**-9])
        self.assertEqual(exact, 2)

    def test_all_gas_nodes_time_flat_and_two_time_nodes(self):
        cell, z = example()
        messages = [{"id": k+1, "op": op, "t": t, "y": z.copy()} for k, (op, t) in
                    enumerate((("jacobian", 0.), ("partial_t", 0.), ("rhs", 0.), ("partial_t", .5), ("rhs", .5)))]
        records = [{"kind": "gas", "time": 0., "full_index": j,
                    "offsets": [-delta, delta], "stencil": "central"}
                   for j, delta in ((1, 2.**-10), (2, 2.**-10), (3, 2.**-10), (4, 2.**-9))]
        records.append({"kind": "time", "time": .5, "nodes": [.5-2.**-12, .5+2.**-12],
                        "offsets": [-2.**-12, 2.**-12], "stencil": "central"})
        rows, count = expand_requests(messages, records, cell)
        self.assertEqual(count["original_rhs_evaluations"], 14)
        self.assertEqual(count["time_flat_branch"], 1)
        self.assertEqual(count["gas_fd_columns"], 4)
        self.assertEqual(count["gas_offset_exact_subtractions"], 8)
        self.assertEqual([r["role"] for r in rows[-4:]], ["partial_t_base", "time_node_0", "time_node_1", "rhs"])
        self.assertEqual(sum(lru_opportunities([physical_key(r["t"], r["u"]) for r in rows])["hits"]), 2)
        missing = deepcopy(records[:-1])
        with self.assertRaisesRegex(TraceError, "MISSING_DERIVATIVE_NODE"):
            expand_requests(messages, missing, cell)

    def test_corrupt_node_and_unconsumed_node_are_rejected(self):
        cell, z = example()
        with self.assertRaisesRegex(TraceError, "GAS_OFFSET_SOURCE_MISMATCH"):
            reconstruct_gas_nodes(cell, cell.physical(0., z), 1,
                                  {"offsets": [-2.**-11, 2.**-10], "stencil": "central"})
        with self.assertRaisesRegex(TraceError, "UNCONSUMED_DERIVATIVE_NODES"):
            expand_requests([], [{"kind": "gas"}], cell)

    def test_reduced_absent_helium_keeps_entire_dynamic_state(self):
        cell, z = example()
        dynamic = tuple(j for j in range(20) if j not in (2, 3))
        reduced = Cell(0., 1., tuple(cell.scales[j] for j in dynamic), dynamic, 1, 0., 2.**-10, 2.**-12)
        zr = [z[j] for j in dynamic]
        full = reduced.full(reduced.physical(0., zr))
        self.assertEqual(full[1:5], [.25, 0., 0., 2.])
        self.assertEqual(len(physical_key(0., reduced.physical(0., zr))), 8*(len(dynamic)+1))


class CapturedProtocolTests(unittest.TestCase):
    def test_successful_request_response_pair_and_terminal(self):
        rpc = [{"direction": "rust_to_python", "message": {"type": "request", "id": 1, "op": "rhs", "t": 0., "y": [1.]}},
               {"direction": "python_to_rust", "message": {"id": 1, "ok": True, "value": [2.]}},
               {"direction": "rust_to_python", "message": {"type": "result", "success": True, "ok": True}}]
        self.assertEqual(len(captured_requests(rpc)[0]), 1)
        with self.assertRaisesRegex(TraceError, "RPC_TERMINAL_SEQUENCE"):
            captured_requests([rpc[0], rpc[2]])
        bad = deepcopy(rpc)
        bad[1]["message"]["ok"] = False
        with self.assertRaisesRegex(TraceError, "RPC_RESPONSE_FAILURE"):
            captured_requests(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
