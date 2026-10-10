"""Read-only-science analysis of frozen saved group errors, no evolutions."""
import json
from pathlib import Path
import validate

def main():
    root=Path(__file__).resolve().parent
    path=root/"evidence/GROUP_ACCEPTANCE.json"
    if path.exists(): raise FileExistsError(path)
    raw=json.loads((root/"evidence/VALIDATION.json").read_text())
    if "grid_refinement" not in raw:
        raise RuntimeError("HOLD_CAMPAIGN_INCOMPLETE")
    grids=raw["grid_refinement"]
    groups=[]
    for branch in (0,1,"total"):
        values=[max(r["value"] for r in rows["rows"] if r["branch"]==branch) for rows in grids]
        groups.append({"branch":branch,"coarse":values[0],"fine":values[1],
                       "pass":values[1]<=.02 and values[1]<values[0]})
    checks=dict(raw["checks"])
    checks["grid"]=all(g["pass"] for g in groups)
    result={"status":"PASS_SCOPED" if all(checks.values()) else "FAIL_FIRST_CAMPAIGN",
            "raw_campaign_status":raw["status"],"groups":groups,"checks":checks,
            "additional_evolve_calls":0,"authority":"Astra final clarification: H/He/total group maxima each decrease; no per-channel decrease"}
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))

if __name__=="__main__":main()
