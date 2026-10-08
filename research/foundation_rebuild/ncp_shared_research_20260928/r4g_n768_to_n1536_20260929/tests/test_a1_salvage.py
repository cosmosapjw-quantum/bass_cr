"""Non-native admission checks for the immutable A1 partial archive."""
import json
import os
from pathlib import Path
import shutil
import sys
import time

import pytest

HERE = Path(__file__).resolve().parents[1]
for directory in (HERE, HERE.parent / "r4f_parallel_migration_20260929",
                  HERE.parent / "r4c_temporal_continuation"):
    sys.path.insert(0, str(directory))

from a1_salvage import A1_ARCHIVE_SHA256, A1_RAW_ATTEMPTS, validate_a1_partial, resume_receipts
from adaptive_workers import build_useful_pilot_plan
from parallel_bridge import GlobalBudget, InvalidPair, publish_pair, validate_pair
from successor import (CONTEXT_ID, PREDECESSOR_SHA256, plan_n1536,
                       plan_receipts, required_missing, validate_predecessor)
from cr_repro.observables import projectile_speed_au


def _archives():
    return (Path(os.environ.get("BASS_R4K_PREDECESSOR_ARCHIVE",
        "/root/.local/state/bass_r4f/runs/R4F-N768-MIGRATION-REPAIR-20260929-A2/output_RETURN.zip")),
        Path(os.environ.get("BASS_R4K_A1_ARCHIVE",
        "/root/.local/state/bass_r4g/runs/R4G-N1536-ADAPTIVE-20260930-A1/output_RETURN.zip")))


@pytest.fixture(scope="module")
def admitted(tmp_path_factory):
    root = tmp_path_factory.mktemp("r4k_real_salvage")
    predecessor, a1 = _archives()
    prior = validate_predecessor(predecessor, PREDECESSOR_SHA256, root / "predecessor")
    contract = prior["contract"]
    v = projectile_speed_au(contract["energy_keV_per_u"])
    required = plan_n1536(CONTEXT_ID, contract["z_initial_a0"] / v,
                          contract["z_final_a0"] / v)
    base = root / "predecessor" / "runtime_queries"
    missing = required_missing(required, {p.stem for p in base.glob("*.json")})
    stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
    _, pilot = plan_receipts(required, missing, stages, remainder, "a" * 40, "b" * 40)
    salvage = validate_a1_partial(a1, A1_ARCHIVE_SHA256, root / "a1", root / "predecessor",
                                  contract, required, pilot, CONTEXT_ID)
    return root, contract, required, missing, pilot, salvage


def test_real_a1_salvage_exact_counts_and_lifetime_budget(admitted, tmp_path):
    root, contract, required, missing, pilot, salvage = admitted
    assert (salvage["predecessor_pairs"], salvage["canonical_pairs"],
            salvage["new_midpoint_pairs"], salvage["remaining_midpoint_ids"]) == (2047, 2063, 16, 1520)
    assert salvage["imported_ids"] == pilot["stages"][0]["query_ids"]
    assert salvage["a1_raw_attempts"] == 54
    assert salvage["native_calls_in_repair_preflight"] == 0
    resume, continuation = resume_receipts(required, missing, pilot, salvage, "a" * 40, "b" * 40)
    assert len(resume["remaining_midpoint_ids"]) == 1520
    assert (resume["strict_remaining_worst_raw"], resume["strict_lifetime_worst_raw"],
            resume["strict_lifetime_raw_margin"]) == (16720, 16774, 122)
    assert continuation["no_stage8_reexecution"] is True
    assert [s["workers"] for s in continuation["new_stages"]] == [16, 32]
    budget = GlobalBudget.create(tmp_path / "budget", parent_attempts=A1_RAW_ATTEMPTS,
                                 maximum=16896, deadline_unix=time.time() + 60)
    assert budget.used() == 54
    assert budget.reserve("synthetic", 1, 1) == 55
    assert budget.used() == 55


def test_a1_pair_hash_context_qualification_orphan_and_conflict(admitted, tmp_path):
    root, contract, required, _, _, salvage = admitted
    q = {item.query_id: item for item in required}[salvage["imported_ids"][0]]
    source = root / "a1" / "runtime_queries"
    pair = tmp_path / "pair"
    pair.mkdir()
    for ext in (".json", ".npz"):
        shutil.copyfile(source / (q.query_id + ext), pair / (q.query_id + ext))
    assert validate_pair(pair, q, CONTEXT_ID, contract)["query_id"] == q.query_id
    canonical = tmp_path / "canonical"
    published = publish_pair(pair, canonical, q, CONTEXT_ID, contract)
    assert published["raw_attempts"] >= 2
    assert all((canonical / (q.query_id + ext)).read_bytes() ==
               (source / (q.query_id + ext)).read_bytes() for ext in (".json", ".npz"))
    with pytest.raises(FileExistsError):
        publish_pair(pair, canonical, q, CONTEXT_ID, contract)
    doc = json.loads((pair / (q.query_id + ".json")).read_text())
    doc["context_id"] = "wrong"
    (pair / (q.query_id + ".json")).write_text(json.dumps(doc))
    with pytest.raises(InvalidPair, match="identity"):
        validate_pair(pair, q, CONTEXT_ID, contract)
    shutil.copyfile(source / (q.query_id + ".json"), pair / (q.query_id + ".json"))
    doc = json.loads((pair / (q.query_id + ".json")).read_text())
    doc["qualification"]["status"] = "UNQUALIFIED"
    (pair / (q.query_id + ".json")).write_text(json.dumps(doc))
    with pytest.raises(InvalidPair, match="qualification"):
        validate_pair(pair, q, CONTEXT_ID, contract)
    shutil.copyfile(source / (q.query_id + ".json"), pair / (q.query_id + ".json"))
    (pair / (q.query_id + ".npz")).write_bytes(b"corrupt")
    with pytest.raises(InvalidPair, match="sha256"):
        validate_pair(pair, q, CONTEXT_ID, contract)
    (pair / (q.query_id + ".npz")).unlink()
    with pytest.raises(InvalidPair, match="missing"):
        validate_pair(pair, q, CONTEXT_ID, contract)


def test_a1_wrong_hash_rejected_before_extraction(tmp_path):
    _, archive = _archives()
    with pytest.raises(ValueError, match="SHA256/size"):
        validate_a1_partial(archive, "0" * 64, tmp_path / "must_not_exist",
                            tmp_path / "unused", {}, [], {}, CONTEXT_ID)
    assert not (tmp_path / "must_not_exist").exists()
