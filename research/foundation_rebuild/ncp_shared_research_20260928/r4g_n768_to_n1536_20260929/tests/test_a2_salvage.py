"""Non-native admission of the immutable A2 partial and its 112 useful pairs."""
import importlib
import json
import os
from pathlib import Path
import shutil
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
for directory in (HERE, HERE.parent / "r4f_parallel_migration_20260929",
                  HERE.parent / "r4c_temporal_continuation"):
    sys.path.insert(0, str(directory))

from a1_salvage import A1_ARCHIVE_SHA256, validate_a1_partial
from adaptive_workers import build_useful_pilot_plan
from parallel_bridge import GlobalBudget, InvalidPair, publish_pair, validate_pair
from successor import (CONTEXT_ID, PREDECESSOR_SHA256, plan_n1536,
                       plan_receipts, required_missing, validate_predecessor)
from cr_repro.observables import projectile_speed_au


@pytest.fixture(scope="module")
def admitted(tmp_path_factory):
    a2_module = importlib.import_module("a2_salvage")
    root = tmp_path_factory.mktemp("r4m_real_a2")
    predecessor = Path(os.environ.get("BASS_R4K_PREDECESSOR_ARCHIVE",
        "/root/.local/state/bass_r4f/runs/R4F-N768-MIGRATION-REPAIR-20260929-A2/output_RETURN.zip"))
    a1 = Path(os.environ.get("BASS_R4K_A1_ARCHIVE",
        "/root/.local/state/bass_r4g/runs/R4G-N1536-ADAPTIVE-20260930-A1/output_RETURN.zip"))
    a2 = Path(os.environ.get("BASS_R4M_A2_ARCHIVE",
        "/root/.local/state/bass_r4k/runs/R4G-N1536-ADAPTIVE-RESUME-20260930-A2/output_RETURN.zip"))
    prior = validate_predecessor(predecessor, PREDECESSOR_SHA256, root / "predecessor")
    contract = prior["contract"]
    v = projectile_speed_au(contract["energy_keV_per_u"])
    required = plan_n1536(CONTEXT_ID, contract["z_initial_a0"] / v,
                          contract["z_final_a0"] / v)
    present = {p.stem for p in (root / "predecessor/runtime_queries").glob("*.json")}
    missing = required_missing(required, present)
    stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
    _, pilot = plan_receipts(required, missing, stages, remainder, "a" * 40, "b" * 40)
    a1_manifest = validate_a1_partial(a1, A1_ARCHIVE_SHA256, root / "a1",
        root / "predecessor", contract, required, pilot, CONTEXT_ID)
    a2_manifest = a2_module.validate_a2_partial(a2, a2_module.A2_ARCHIVE_SHA256,
        root / "a2", root / "predecessor", root / "a1", contract,
        required, pilot, CONTEXT_ID)
    return root, contract, required, missing, pilot, a1_manifest, a2_manifest, a2_module


def test_a2_exact_salvage_and_no_pilot_recomputation(admitted, tmp_path):
    root, contract, required, missing, pilot, a1, a2, module = admitted
    assert (a2["predecessor_pairs"], a2["a1_stage8_pairs"],
            a2["a2_stage16_pairs"], a2["a2_stage32_pairs"],
            a2["canonical_pairs"]) == (2047,16,32,64,2159)
    assert a2["selected_workers"] == 32
    assert a2["prior_raw_attempts"] == 368
    plan, selection = module.a3_resume_receipts(required, missing, pilot, a2,
                                                 "a" * 40, "b" * 40)
    all_pilot = {qid for stage in pilot["stages"] for qid in stage["query_ids"]}
    assert not all_pilot.intersection(plan["remaining_ids"])
    assert len(plan["remaining_ids"]) == 1424
    assert plan["initial_canonical_pairs"] == 2159
    assert plan["eventual_union_pairs"] == 3583
    assert (plan["strict_remaining_worst_raw"], plan["strict_lifetime_worst_raw"],
            plan["lifetime_raw_margin"]) == (15664,16032,864)
    assert selection["selected_workers"] == 32 and selection["no_pilot_reexecution"] is True
    budget = GlobalBudget.create(tmp_path / "budget", parent_attempts=368,
                                 maximum=16896, deadline_unix=9999999999)
    assert budget.used() == 368 and budget.seed["maximum"] == 16896


def test_a2_extra_pair_hash_context_orphan_and_conflict(admitted, tmp_path):
    root, contract, required, _, pilot, _, _, _ = admitted
    qid = pilot["stages"][1]["query_ids"][0]
    q = {x.query_id:x for x in required}[qid]
    src = root / "a2/runtime_queries"
    pair = tmp_path / "pair";pair.mkdir()
    for ext in (".json", ".npz"):
        shutil.copyfile(src / (qid + ext), pair / (qid + ext))
    assert validate_pair(pair, q, CONTEXT_ID, contract)["query_id"] == qid
    dest = tmp_path / "canonical"
    publish_pair(pair, dest, q, CONTEXT_ID, contract)
    with pytest.raises(FileExistsError): publish_pair(pair, dest, q, CONTEXT_ID, contract)
    doc=json.loads((pair/(qid+".json")).read_text())
    doc["context_id"]="wrong"
    (pair/(qid+".json")).write_text(json.dumps(doc))
    with pytest.raises(InvalidPair,match="identity"):validate_pair(pair,q,CONTEXT_ID,contract)
    shutil.copyfile(src/(qid+".json"),pair/(qid+".json"))
    (pair/(qid+".npz")).write_bytes(b"bad")
    with pytest.raises(InvalidPair,match="sha256"):validate_pair(pair,q,CONTEXT_ID,contract)
    (pair/(qid+".npz")).unlink()
    with pytest.raises(InvalidPair,match="missing"):validate_pair(pair,q,CONTEXT_ID,contract)


def test_a2_wrong_hash_rejected_before_extraction(tmp_path):
    a2_module = importlib.import_module("a2_salvage")
    archive = Path(os.environ.get("BASS_R4M_A2_ARCHIVE",
        "/root/.local/state/bass_r4k/runs/R4G-N1536-ADAPTIVE-RESUME-20260930-A2/output_RETURN.zip"))
    with pytest.raises(ValueError,match="SHA256/size"):
        a2_module.validate_a2_partial(archive,"0"*64,tmp_path/"not-created",
            tmp_path/"unused",tmp_path/"unused2",{},[],{},CONTEXT_ID)
    assert not (tmp_path/"not-created").exists()
