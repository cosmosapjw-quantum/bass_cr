"""Independent arithmetic checks on saved endpoint receipts; no RHS/ODE."""
from pathlib import Path
import json, hashlib, math, struct
from datetime import datetime, timezone
HERE = Path(__file__).resolve().parent
EVIDENCE = Path("/workspace/scratch/30d955d9ea43/resume_c22c_20261022/recovery/restored_c22b/repository/research/cr_c22d_cold_ci_20261022/evidence/NEW_REGISTRY_ENDPOINT_CHECKS.json")
source = json.loads(EVIDENCE.read_bytes())
# The inherited fixed UV cohort energies, also present in initial boundary receipt.
initial = source["checks"][0]["left"]["evaluation_energies_eV"]
def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0
def bits(x):
    return struct.pack(">d",float(x))
rows=[]
for segment in source["checks"]:
    left=segment["left"]["boundary_eta"]
    right=segment["right"]["boundary_eta"]
    for side in ("left","right"):
        item=segment[side];ev=item["evaluation_eta"];ref=item["reference_eta"]
        target=right if side=="left" else left
        stepped=item["boundary_eta"]
        for _ in range(item["ulp_steps"]):
            stepped=math.nextafter(stepped,target)
        e=[x*math.exp(-ev) for x in initial]
        er=[x*math.exp(-ref) for x in initial]
        actual=[[sign(x-th) for th in item["thresholds_eV"]] for x in e]
        expected=[[sign(x-th) for th in item["thresholds_eV"]] for x in er]
        checks={
            "strict_segment_interior":left < ev < right,
            "ULP_walk_exact":bits(stepped)==bits(ev),
            "saved_energy_bits":all(bits(x)==bits(y) for x,y in zip(e,item["evaluation_energies_eV"])),
            "computed_actual_equals_saved":actual==item["actual_sides"],
            "computed_expected_equals_saved":expected==item["expected_sides"],
            "same_strict_branch":actual==expected and all(v!=0 for a in actual for v in a),
            "bounded_ULPs":1<=item["ulp_steps"]<=item["max_ulps"]==256,
            "no_state_mutation_claim":item["state_mutation"]=="NONE",
        }
        rows.append({"segment":segment["segment"],"side":side,"ulp_steps":item["ulp_steps"],"checks":checks,"pass":all(checks.values())})
result={
    "schema":"C22D_INDEPENDENT_SAVED_ENDPOINT_REVIEW_V1",
    "utc":datetime.now(timezone.utc).isoformat(),
    "status":"PASS_SAVED_BRANCH_ARITHMETIC" if all(x["pass"] for x in rows) else "FAIL_PRESERVED",
    "rows":rows,"endpoint_checks":len(rows),"passed":sum(x["pass"] for x in rows),
    "max_ULP_steps":max(x["ulp_steps"] for x in rows),
    "source_receipt_sha256":hashlib.sha256(EVIDENCE.read_bytes()).hexdigest(),
    "review_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "runtime_model_sha256":source["model_sha256"],"runtime_driver_sha256":source["driver_sha256"],
    "RHS_calls":0,"ODE_runs":0,"scope":"Independent stdlib arithmetic on saved endpoint evidence; no scientific trajectory or runtime endpoint call",
    "global_error_bound":None,
}
with (HERE/"SAVED_ENDPOINT_REVIEW.json").open("x") as f:
    json.dump(result,f,indent=2);f.write("\n")
print(json.dumps({k:v for k,v in result.items() if k!="rows"}))
assert result["passed"]==36

