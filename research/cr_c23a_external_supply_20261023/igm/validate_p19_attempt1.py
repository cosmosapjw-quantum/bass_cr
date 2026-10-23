"""Small source/adapter validation; no ODE and no inherited-model imports."""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from html.parser import HTMLParser
import hashlib
import json
import math
import os
from pathlib import Path
import time

os.sched_setaffinity(0, {4})
from p19_uvb import P19Fiducial, CHANNELS

ROOT = Path(__file__).parent


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = self.row = self.cell = None

    def handle_starttag(self, tag, attributes):
        if tag == "table":
            self.table = {"attributes": dict(attributes), "rows": []}
        elif self.table is not None and tag == "tr":
            self.row = []
        elif self.table is not None and tag in ("td", "th"):
            self.cell = []

    def handle_data(self, content):
        if self.cell is not None:
            self.cell.append(content)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            if self.row is not None:
                self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.table is not None:
                self.table["rows"].append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def main():
    start = time.perf_counter()
    cpu_start = time.process_time()
    model = P19Fiducial()
    checks = []
    def check(name, passed, **detail):
        checks.append({"name": name, "result": "PASS_SCOPED" if passed else "FAIL", **detail})

    parsed = Tables()
    parsed.feed((ROOT / "sources/P19V1_article.html").read_text())
    table = next(t for t in parsed.tables if t["attributes"].get("id") == "A4.T3.2")
    independent_rows = tuple(tuple(map(float, row)) for row in table["rows"][2:])
    check("author_HTML_Table3_vs_ancillary_all_59_by_7_values",
          independent_rows == tuple(row[:7] for row in model.rows),
          scalar_comparisons=413,
          scope="Two representations of the same author's source; not independent physical calibration")
    exact_nodes = 0
    for row in model.rows:
        r = model.evaluate(row[0])
        expected = row[1:7]
        got = tuple(v for pair in zip(r.gamma_s_inv, r.heat_ev_s_inv) for v in pair)
        exact_nodes += sum(a.hex() == b.hex() for a, b in zip(got, expected))
    check("exact_node_binary64_identity", exact_nodes == 354, scalar_comparisons=354)

    max_mid_rel = 0.0
    for left, right in zip(model.rows, model.rows[1:]):
        z = math.expm1((math.log1p(left[0])+math.log1p(right[0]))/2)
        r = model.evaluate(z)
        got = tuple(v for pair in zip(r.gamma_s_inv, r.heat_ev_s_inv) for v in pair)
        with localcontext() as c:
            c.prec = 60
            expected = [float((Decimal(str(a))*Decimal(str(b))).sqrt())
                        for a, b in zip(left[1:7], right[1:7])]
        max_mid_rel = max(max_mid_rel, *(abs(a-b)/b for a,b in zip(got, expected)))
        if not all(min(a,b) <= v <= max(a,b) for a,b,v in zip(left[1:7],right[1:7],got)):
            check("between_nodes_positive_bounded", False, redshift=z)
    check("log_coordinate_midpoints_vs_60_digit_geometric_mean", max_mid_rel < 5e-14,
          max_relative_difference=max_mid_rel, scalar_comparisons=348, tolerance=5e-14)
    check("positive_process_rates", all(v > 0 for row in model.rows for v in row[1:7]))

    bad_z = [float("nan"), float("inf"), -float("inf"), -1e-10, 15.10000001, 20.0]
    for z in bad_z:
        try:
            model.evaluate(z)
            rejected = False
        except ValueError:
            rejected = True
        check("fail_closed_redshift_" + repr(z), rejected)
    xs = {"HI":0.7,"HeI":0.05,"HeII":0.02}
    chis = {"HI":13.6058,"HeI":24.6,"HeII":54.4}
    for label, xb, cb in [
        ("missing_channel", {"HI":0.7}, chis),
        ("unsupported_isotope", dict(xs,D=1e-5), chis),
        ("negative_population", dict(xs,HI=-1), chis),
        ("nonfinite_population", dict(xs,HI=float("nan")), chis),
        ("missing_binding", xs, {"HI":13.6}),
        ("invalid_binding", xs, dict(chis,HI=0))]:
        try:
            model.source_budget(2,xb,cb)
            rejected = False
        except ValueError:
            rejected = True
        check("fail_closed_"+label,rejected)

    budget = model.source_budget(2,xs,chis)
    r = model.evaluate(2)
    with localcontext() as c:
        c.prec=60
        decimal_q = sum(Decimal(str(xs[k]))*Decimal(str(h)) for k,h in zip(CHANNELS,r.heat_ev_s_inv))
        decimal_b = sum(Decimal(str(xs[k]))*Decimal(str(g))*Decimal(str(chis[k])) for k,g in zip(CHANNELS,r.gamma_s_inv))
        rel = abs(float(decimal_q+decimal_b)-budget["external_energy_ev_per_reference_s"])/float(decimal_q+decimal_b)
    check("moment_defined_energy_import_vs_decimal",rel < 5e-16,relative_difference=rel,
          scope="Explicit caller binding convention, not source-spectrum validation")
    samples = []
    for z in [0,2,6.14,10,15.1]:
        r=model.evaluate(z)
        samples.append({"z":z,"Gamma_s_inv":dict(zip(CHANNELS,r.gamma_s_inv)),
                        "heat_ev_s_inv":dict(zip(CHANNELS,r.heat_ev_s_inv)),
                        "mean_excess_ev":dict(zip(CHANNELS,(h/g for h,g in zip(r.heat_ev_s_inv,r.gamma_s_inv))))})
    result={"status":"PASS_SCOPED" if all(c["result"]=="PASS_SCOPED" for c in checks) else "FAIL",
            "created_utc":datetime.now(timezone.utc).isoformat(),"cpu_affinity":sorted(os.sched_getaffinity(0)),
            "native_threads":{k:os.environ.get(k) for k in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]},
            "wall_seconds":time.perf_counter()-start,"cpu_seconds":time.process_time()-cpu_start,
            "ODE_executions":0,"old_model_imports":0,"checks":checks,"samples":samples,
            "global_error_bound":None}
    with (ROOT/"P19_VALIDATION.json").open("x") as f:json.dump(result,f,indent=2);f.write("\n")
    print(json.dumps(result,indent=2))
    return 0 if result["status"]=="PASS_SCOPED" else 1


if __name__=="__main__":
    raise SystemExit(main())
