"""Freeze a metadata-only, unique targeted control repair; no science replay."""
import hashlib
import json
import math
import pathlib

UNIT = pathlib.Path(__file__).resolve().parents[1]
UNIT_ID = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


budget_path = UNIT / "EXECUTION_BUDGET.json"
preserved = UNIT / "evidence/C06_FIRST_CONTROL_CONTEXT_PRESERVED"
assert budget_path.read_bytes() == (preserved / "EXECUTION_BUDGET.json").read_bytes()
budget = json.loads(budget_path.read_bytes())
assert budget["unit"] == UNIT_ID and budget["local_science_cpu_cap_s"] == 40
ledger = json.loads((UNIT / "evidence/EXECUTION_LEDGER.json").read_bytes())
assert ledger["unit"] == UNIT_ID and len(ledger["attempts"]) == 2
assert {x["run_id"] for x in ledger["attempts"]} == {"prepare_v1", "controls_v1"}
failed = json.loads((UNIT / "runs/controls_v1/RESULT.json").read_bytes())
assert failed["count"] == 46 and failed["passed"] == 45 and not failed["all_pass"]
assert [x["name"] for x in failed["checks"] if not x["pass"]] == ["direct_cutoff_has_no_active_RR"]
assert sha(UNIT / "implementation/controls.py") == "edee3395a229bdd7453fc52c24e78129c08d909e1c4b1d2857c533a509978e6d"

old_manifest = json.loads((UNIT / budget["code_manifest"]).read_bytes())
manifest = {"unit": UNIT_ID, "files": []}
changed = []
for row in old_manifest["files"]:
    path = UNIT / row["path"]
    item = {"path": row["path"], "bytes": path.stat().st_size, "sha256": sha(path)}
    manifest["files"].append(item)
    if item != row:
        changed.append(row["path"])
assert changed == ["implementation/controls.py"]
manifest_path = UNIT / "evidence/C06_CODE_MANIFEST_V3.json"
new_json(manifest_path, manifest)

budget["original_C4_nominal_plan"] = {key: budget[key] for key in (
    "nominal_worker_sum_s", "nominal_coordinator_reservations_s",
    "unallocated_failure_and_repair_reserve_s")}
budget["run_allocations"].append({
    "run_id": "controls_v2", "worker_cpu_reservation_s": 2,
    "selected_memory_limit_bytes": 268435456,
    "scope": "only direct_cutoff_has_no_active_RR; 45 accepted prior controls reused"})
future = [row for row in budget["run_allocations"]
          if row["run_id"] not in {"prepare_v1", "controls_v1"}]
budget["nominal_worker_sum_s"] = math.fsum(row["worker_cpu_reservation_s"] for row in future)
budget["nominal_coordinator_reservations_s"] = len(future) * budget["coordinator_reserve_per_attempt_s"]
budget["nominal_accounting_basis"] = "remaining named attempts after immutable actual prepare_v1 and failed controls_v1 debits"
budget["already_charged_at_C6_repair_s"] = ledger["charged_cpu_s"]
budget["unallocated_failure_and_repair_reserve_s"] = 40 - ledger["charged_cpu_s"] - budget["nominal_worker_sum_s"] - budget["nominal_coordinator_reservations_s"]
assert budget["unallocated_failure_and_repair_reserve_s"] > 0
budget["code_manifest"] = str(manifest_path.relative_to(UNIT))
budget["code_manifest_sha256"] = sha(manifest_path)
budget["repair_context"] = "C06_TARGETED_EXACT_CUTOFF_ORACLE_V2"
budget["preserved_previous_budget"] = str((preserved / "EXECUTION_BUDGET.json").relative_to(UNIT))
context = {
    "unit": UNIT_ID, "context": budget["repair_context"],
    "previous_budget_sha256": sha(budget_path),
    "new_code_manifest_sha256": sha(manifest_path),
    "changed_files": changed, "scientific_tolerances_changed": False,
    "failed_attempt_preserved": "runs/controls_v1", "failed_attempt_charged_s": 0.640928,
    "accepted_prior_controls_reused": 45, "targeted_new_control_count": 1,
    "preparation_reused_without_reexecution": "runs/prepare_v1",
    "preparation_sha256": sha(UNIT / "runs/prepare_v1/PREPARATION.json"),
    "already_charged_s": ledger["charged_cpu_s"],
    "remaining_worker_and_coordinator_reservations_s": budget["nominal_worker_sum_s"] + budget["nominal_coordinator_reservations_s"],
    "cap_s": 40, "old_budget_transfer": False,
    "metadata_authoring_only_no_scientific_execution": True,
    "fresh_host_admission": "performed and charged by the unchanged runner at launch",
    "central_completed": 27, "central_total": 88, "central_count_effect": 0,
}
new_json(UNIT / "evidence/C06_REPAIR_CONTEXT.json", context)
budget_path.write_text(json.dumps(budget, indent=2, allow_nan=False) + "\n")
print(json.dumps({"context": context["context"], "budget_sha256": sha(budget_path),
                  "charged_s": ledger["charged_cpu_s"], "reserve_s": budget["unallocated_failure_and_repair_reserve_s"]}))
