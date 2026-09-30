import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from resource_census import (ExternalResourceOverlap, OwnPoolTeardownIncomplete,
                             collect_bass_candidates, live_resource_census,
                             verify_prior_pool_teardown)


def proc(root, pid, ppid, pgid, sid, cmd, cpus, mapping):
    d = root / str(pid)
    d.mkdir()
    (d / "stat").write_text(f"{pid} (python) S {ppid} {pgid} {sid} 0 0 0 0\n")
    (d / "cmdline").write_bytes(cmd.encode() + b"\0")
    (d / "cgroup").write_text("0::/user.slice/test.scope\n")
    mapping[pid] = set(cpus)


def test_process_ownership_external_overlap_durable_and_no_environment(tmp_path, monkeypatch):
    root = tmp_path / "proc";root.mkdir()
    mapping = {0: set(range(32))}
    proc(root, 1, 0, 7, 7, "python BASS_HE parent", range(32), mapping)
    proc(root, 10, 1, 99, 99, "python bass_cr current", range(32), mapping)
    proc(root, 20, 1, 99, 99, "python bass_cr same-run", [0, 1], mapping)
    proc(root, 30, 1, 100, 100, "python BASS_HE external --token do-not-copy-secret", [2, 3], mapping)
    proc(root, 31, 1, 101, 101, "python WU088_HH outside", [40], mapping)
    proc(root, 40, 1, 102, 102, "python unrelated", [0], mapping)
    monkeypatch.setenv("SECRET_FOR_TEST", "do-not-copy-secret")
    receipt = tmp_path / "resource.json"
    with pytest.raises(ExternalResourceOverlap, match="EXTERNAL_BASS_CPU_OVERLAP: 30"):
        live_resource_census(list(range(8)), 8, 1 << 30,
            receipt_path=receipt, proc_root=root, affinity_lookup=lambda pid: mapping[pid],
            self_pid=10, run_pgid=99, allowed=set(range(32)),
            mem_available_bytes=50 << 30, quota_cores=32)
    data = json.loads(receipt.read_text())
    assert data["external_offender_pids"] == [30]
    assert {p["pid"]: p["ownership"] for p in data["candidate_processes"]} == {
        1: "ANCESTOR", 10: "SELF", 20: "SAME_RUN_PROCESS_GROUP",
        30: "EXTERNAL", 31: "EXTERNAL"}
    assert data["candidate_processes"][-2]["requested_cpu_intersection"] == [2, 3]
    assert "do-not-copy-secret" not in receipt.read_text()
    assert all("environ" not in row for row in data["candidate_processes"])


def test_external_nonoverlap_and_benign_process_do_not_block(tmp_path):
    root=tmp_path/"proc";root.mkdir();mapping={0:set(range(32))}
    proc(root, 10, 1, 99, 99, "python bass_cr current", range(32), mapping)
    proc(root, 31, 1, 101, 101, "python BASS_HE external", [40], mapping)
    proc(root, 40, 1, 102, 102, "python unrelated", [0], mapping)
    receipt=tmp_path/"ok.json"
    data=live_resource_census(list(range(8)),8,1<<30,receipt_path=receipt,
        proc_root=root,affinity_lookup=lambda pid:mapping[pid],self_pid=10,
        run_pgid=99,allowed=set(range(32)),mem_available_bytes=50<<30,quota_cores=32)
    assert data["status"]=="PASS" and data["external_offender_pids"]==[]
    assert {r["pid"] for r in data["candidate_processes"]}=={10,31}


def test_prior_worker_gone_and_same_run_lingering_worker(tmp_path):
    root=tmp_path/"proc";root.mkdir();mapping={10:{0},20:{1}}
    proc(root,10,1,99,99,"python bass_cr coordinator",[0],mapping)
    proc(root,20,10,99,99,"python worker bass_cr",[1],mapping)
    receipt=tmp_path/"teardown.json"
    with pytest.raises(OwnPoolTeardownIncomplete,match="OWN_POOL_TEARDOWN_INCOMPLETE"):
        verify_prior_pool_teardown({20},run_pgid=99,receipt_path=receipt,
            settle_seconds=0,proc_root=root,affinity_lookup=lambda pid:mapping[pid])
    data=json.loads(receipt.read_text())
    assert data["lingering_workers"][0]["pid"]==20
    assert {r["pid"] for r in data["same_run_process_group"]}=={10,20}
    for p in (root/"20").iterdir():p.unlink()
    (root/"20").rmdir()
    clean=verify_prior_pool_teardown({20},run_pgid=99,
        receipt_path=tmp_path/"settled.json",settle_seconds=0,
        proc_root=root,affinity_lookup=lambda pid:mapping[pid])
    assert clean["status"]=="PASS" and clean["lingering_workers"]==[]


def test_unreceipted_same_group_spawn_worker_blocks_and_preserves_evidence(tmp_path):
    root=tmp_path/"proc";root.mkdir();mapping={10:{0},21:{1}}
    proc(root,10,1,99,99,"python bass_cr coordinator",[0],mapping)
    proc(root,21,10,99,99,"python -c from multiprocessing.spawn import spawn_main",[1],mapping)
    receipt=tmp_path/"teardown.json"
    with pytest.raises(OwnPoolTeardownIncomplete,match="OWN_POOL_TEARDOWN_INCOMPLETE"):
        verify_prior_pool_teardown(set(),run_pgid=99,receipt_path=receipt,
            settle_seconds=0,proc_root=root,affinity_lookup=lambda pid:mapping[pid])
    data=json.loads(receipt.read_text())
    assert [r["pid"] for r in data["unreceipted_same_group_workers"]]==[21]
