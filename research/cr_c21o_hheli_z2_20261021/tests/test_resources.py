"""Focused admission fixtures; no science, workers, remote calls or benchmarks."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "resource_control.py"
SPEC = importlib.util.spec_from_file_location("c21o_resource_control", SOURCE)
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


def fixture(cpus=tuple(range(9)), quota=8., available=7 * rc.GIB,
            limit=8 * rc.GIB, busy=None):
    return {"affinity": list(cpus), "allowed_cpus": list(cpus),
            "affinity_observed": True, "cpu_limit_observed": True,
            "cpu_quota_cores": quota, "cpu_quota_spare_cores": quota,
            "per_cpu_busy": busy or {c: 0. for c in cpus},
            "memory_limit_bytes": limit, "memory_available_bytes": available,
            "memory_observation_complete": True, "host_load_average": [100., 100., 100.],
            "cgroups": [], "warnings": []}


def choose(s, **kwargs):
    with patch.object(rc, "observe_resources", return_value=deepcopy(s)):
        return rc.choose_workers(**kwargs)


class ResourceFixtures(unittest.TestCase):
    def test_quota_reserves_coordinator_and_pending_caps_workers(self):
        s = fixture()
        n, r = choose(s, task_count=50, requested=20)
        self.assertEqual(n, 7)  # quota 8, one quota core for coordinator
        self.assertEqual(len(r["selected_worker_cpus"]), 7)
        self.assertNotIn(r["coordinator_cpu"], r["selected_worker_cpus"])
        self.assertEqual(choose(s, task_count=2, requested=20)[0], 2)
        s["cpu_quota_spare_cores"] = 2.5
        self.assertEqual(choose(s, task_count=20)[0], 1)
        self.assertEqual(choose(s, task_count=0)[0], 0)

    def test_cpu55_is_protected_and_62_cap(self):
        s = fixture(cpus=tuple(range(64)), quota=64., available=120 * rc.GIB, limit=128 * rc.GIB)
        n, r = choose(s, task_count=1000, requested=64)
        self.assertEqual(n, 62)
        self.assertNotIn(55, r["selected_worker_cpus"])
        self.assertNotEqual(r["coordinator_cpu"], 55)

    def test_memory_reserve_and_coordinator_are_real_costs(self):
        exact = rc.GIB + 768 * rc.MIB + 2 * 512 * rc.MIB
        s = fixture(available=exact)
        n, r = choose(s, task_count=20)
        self.assertEqual(n, 2)
        self.assertEqual(r["memory_reserve_bytes"], rc.GIB)
        s["memory_available_bytes"] -= 1
        self.assertEqual(choose(s, task_count=20)[0], 1)
        s["memory_observation_complete"] = False
        self.assertEqual(choose(s, task_count=20)[0], 0)

    def test_busy_other_work_leaves_a_safe_slot(self):
        s = fixture(busy={c: .98 if c < 6 else .01 for c in range(9)})
        s["cpu_quota_spare_cores"] = 2.2
        n, r = choose(s, task_count=2)
        self.assertEqual(n, 1)
        self.assertGreaterEqual(r["coordinator_cpu"], 6)
        self.assertGreaterEqual(r["selected_worker_cpus"][0], 6)
        # A large host-wide load average does not veto an observed local slot.
        self.assertEqual(r["snapshot"]["host_load_average"][0], 100.)

    def test_leases_are_read_only_and_unknown_is_not_empty(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.json"
            raw = json.dumps({"schema": "C21_CPU_LEASES_V1", "leases": [
                {"owner": "another-session", "cpus": [0, 1, 55]}]}).encode()
            path.write_bytes(raw)
            n, r = choose(fixture(), task_count=2, lease_path=path)
            self.assertEqual(n, 2)
            self.assertTrue({0, 1}.isdisjoint(r["selected_worker_cpus"] + [r["coordinator_cpu"]]))
            self.assertEqual(path.read_bytes(), raw)
            self.assertFalse(r["lease"]["modified"])
            path.write_text(json.dumps({"schema": "future", "queue": {"cpus": [2, 3]}}))
            _, r = choose(fixture(), task_count=2, lease_path=path)
            self.assertEqual(r["lease"]["status"], "UNKNOWN_SCHEMA_INFERRED_RESERVED")
            self.assertTrue({2, 3}.isdisjoint(r["selected_worker_cpus"] + [r["coordinator_cpu"]]))
            path.write_text('{"status":"occupied but undocumented"}')
            n, r = choose(fixture(), task_count=2, lease_path=path)
            self.assertEqual(n, 0)
            self.assertEqual(r["lease"]["status"], "UNKNOWN_SCHEMA_RESERVED_ALL")

    def test_v2_finite_headroom_and_unlimited_cpu_decode(self):
        values = {"cpu.max": "250000 100000", "cpu.stat": "usage_usec 7000000\nnr_throttled 2",
                  "cpuset.cpus.effective": "0-3,55", "memory.max": str(8 * rc.GIB),
                  "memory.current": str(3 * rc.GIB)}
        loc = {"path": "/fixture", "version": 2, "controllers": []}
        with patch.object(rc, "_read_text", side_effect=lambda p: values.get(Path(p).name)):
            row = rc._decode_group(loc)
        self.assertEqual(row["quota_cores"], 2.5)
        self.assertEqual(row["memory_headroom_bytes"], 5 * rc.GIB)
        self.assertEqual(row["usage_seconds"], 7.)
        values["cpu.max"] = "max 100000"
        with patch.object(rc, "_read_text", side_effect=lambda p: values.get(Path(p).name)):
            row = rc._decode_group(loc)
        self.assertTrue(row["cpu_limit_observed"])
        self.assertIsNone(row["quota_cores"])

    def test_visible_ancestor_membership_is_retained(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "parent/child").mkdir(parents=True)
            mountinfo = "1 0 0:1 / " + td + " rw - cgroup2 cgroup rw\n"
            rows = rc._cgroup_locations("0::/parent/child\n", mountinfo)
            self.assertEqual([r["path"] for r in rows],
                             [str(root / "parent/child"), str(root / "parent"), str(root)])

    def test_adaptive_dispatch_pauses_only_new_work(self):
        _, budget = choose(fixture(), task_count=4)
        s = fixture()
        self.assertTrue(rc.dispatch_allowed(s, 3, budget)[0])
        self.assertFalse(rc.dispatch_allowed(s, 4, budget)[0])
        s["memory_available_bytes"] = rc.GIB
        ok, detail = rc.dispatch_allowed(s, 2, budget)
        self.assertFalse(ok)
        self.assertIn("MEMORY_HEADROOM_LOW_OR_UNKNOWN", detail["reasons"])
        self.assertEqual(detail["existing_worker_action"], "UNCHANGED")
        s = fixture()
        s["cpu_quota_spare_cores"] = 1.9
        self.assertIn("CPU_QUOTA_HEADROOM_LOW", rc.dispatch_allowed(s, 1, budget)[1]["reasons"])
        s = fixture()
        for cpu in budget["selected_worker_cpus"]:
            s["per_cpu_busy"][cpu] = .99
        self.assertIn("NO_IDLE_ADMITTED_WORKER_CPU", rc.dispatch_allowed(s, 1, budget)[1]["reasons"])

    def test_dispatch_preserves_worker_admission_after_coordinator_pin(self):
        _, budget = choose(fixture(), task_count=4)
        s = fixture()
        s["affinity"] = [budget["coordinator_cpu"]]
        s["allowed_cpus"] = [budget["coordinator_cpu"]]
        s["cgroup_cpuset"] = list(range(9))
        ok, detail = rc.dispatch_allowed(s, 1, budget)
        self.assertTrue(ok)
        self.assertEqual(detail["idle_worker_cpus"], sorted(budget["selected_worker_cpus"]))
        s["cgroup_cpuset"] = [budget["coordinator_cpu"]]
        self.assertFalse(rc.dispatch_allowed(s, 1, budget)[0])
        # The observer itself retains per-CPU samples outside its own affinity.
        s = fixture(cpus=(0,))
        s["cgroup_cpuset"] = [0, 1]
        with patch.object(rc, "_snapshot_once", side_effect=[deepcopy(s), deepcopy(s)]), \
                patch.object(rc, "_proc_cpu", side_effect=[{0: (100, 90), 1: (100, 90)},
                                                         {0: (110, 100), 1: (110, 99)}]), \
                patch.object(rc.time, "sleep"), \
                patch.object(rc.time, "monotonic", side_effect=[1., 1.1]), \
                patch.object(rc.time, "process_time", side_effect=[0., .001]):
            observed = rc.observe_resources()
        self.assertEqual(set(observed["per_cpu_busy"]), {0, 1})
        self.assertLess(observed["per_cpu_busy"][1], rc.IDLE_THRESHOLD)


if __name__ == "__main__":
    unittest.main(verbosity=2)
