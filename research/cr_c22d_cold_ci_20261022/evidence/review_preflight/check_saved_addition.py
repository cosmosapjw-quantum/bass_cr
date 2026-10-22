"""Independent rational review of saved CI on/off scalar additions; ODE/RHS0."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import math
import struct
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
DIAG = Path("/workspace/scratch/30d955d9ea43/resume_c22c_20261022/recovery/restored_c22b/repository/research/cr_c22d_cold_ci_20261022/evidence/model_delta_checks_v1/FAILURE_DIAGNOSIS.json")

def bits(x):
    return struct.pack(">d", x).hex()

def exact(x):
    return Fraction.from_float(float(x))

raw = DIAG.read_bytes()
source = json.loads(raw)
rows = []
for row in source["rows"]:
    coords = []
    for index, off, delta, observed in zip(row["coordinates"], row["doff"], row["expected"], row["don"]):
        target = exact(off) + exact(delta)
        correctly_rounded = float(target)
        error = exact(observed) - target
        exact_difference = exact(observed) - exact(off)
        float_difference = observed - off
        spacing = exact(math.ulp(observed))
        coords.append({
            "index": index,
            "off_hex": float(off).hex(),
            "delta_hex": float(delta).hex(),
            "observed_hex": float(observed).hex(),
            "correct_rounding_hex": correctly_rounded.hex(),
            "exact_sum": str(target),
            "exact_addition_error": str(error),
            "correctly_rounded_addition_bitwise": bits(observed) == bits(correctly_rounded),
            "addition_error_at_most_half_ULP": abs(error) <= spacing/2,
            "addition_error_ULP": float(abs(error)/spacing),
            "subtraction_is_exact": exact(float_difference) == exact_difference,
            "exact_increment_error": str(exact_difference-exact(delta)),
        })
    denom = max(abs(exact(v)) for v in row["expected"])
    maxerr = max(abs((exact(on)-exact(off))-exact(delta))
                 for on, off, delta in zip(row["don"],row["doff"],row["expected"]))
    rows.append({
        "T_K":row["T_K"],"ion":row["ion"],"mode":row["mode"],
        "coordinates":coords,
        "CI_relative_error_from_exact_saved_floats":float(maxerr/denom),
        "owner_reported_CI_relative_increment_error":row["CI_relative_increment_error"],
        "old_5e_12_CI_relative_predicate":float(maxerr/denom)<5e-12,
        "max_addition_error_ULP":max(x["addition_error_ULP"] for x in coords),
    })
checks = [x for row in rows for x in row["coordinates"]]
result = {
    "schema":"C22D_INDEPENDENT_SAVED_ADDITION_REVIEW_V1",
    "utc":datetime.now(timezone.utc).isoformat(),
    "status":"PASS_EXACT_INPUT_ROUNDING_DIAGNOSIS" if all(x["correctly_rounded_addition_bitwise"] and x["addition_error_at_most_half_ULP"] and x["subtraction_is_exact"] for x in checks) else "FAIL_PRESERVED",
    "diagnosis_path":str(DIAG),"diagnosis_sha256":hashlib.sha256(raw).hexdigest(),
    "review_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "rows":rows,"scalar_additions":len(checks),
    "correctly_rounded_bitwise_count":sum(x["correctly_rounded_addition_bitwise"] for x in checks),
    "exact_subtraction_count":sum(x["subtraction_is_exact"] for x in checks),
    "maximum_addition_error_ULP":max(x["addition_error_ULP"] for x in checks),
    "method":"Fraction.from_float exact binary64 inputs; correctly round exact rational sum; compare bits and roundoff; inspect no imported science modules",
    "conclusion":"The stored don equals the correctly-rounded off+expected in every reviewed coordinate. Subtraction is exact on these saved inputs; the CI-relative discrepancy was introduced by adding a small increment to the large baseline, then exposing that expected rounding with subtraction. Removing UV alone cannot remove expansion/recombination/Compton baseline scale.",
    "review_scope":"Saved 6 point diagnostics, 4 CI coordinates each. Does not independently certify physical rate accuracy or the whole RHS.",
    "RHS_calls":0,"new_ODE":0,"old_ODE_reruns":0,"global_error_bound":None,
}
with (HERE/"SAVED_ADDITION_REVIEW.json").open("x") as f:
    json.dump(result,f,indent=2);f.write("\n")
print(json.dumps({k:v for k,v in result.items() if k not in ("rows","conclusion","review_scope")}))
for row in rows:
    print(json.dumps({k:v for k,v in row.items() if k!="coordinates"}))
if result["status"]!="PASS_EXACT_INPUT_ROUNDING_DIAGNOSIS":
    raise SystemExit(1)

