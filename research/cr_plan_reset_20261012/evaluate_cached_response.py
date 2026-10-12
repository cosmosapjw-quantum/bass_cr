"""Evaluate existing decimal moments; no CR generator or evolution imports.

This is postprocessing of recorded finite-model constraints, not a new kernel
evaluation. Fractions remain authoritative; floats are only for plotting.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED = "dfdca59ca0b4131c6143fe3cf0e402a7b18efb113a9af9bcc82a66696f5ec6f5"
FIELDS = ("H0", "p", "R", "S", "mu_s", "m2_s2")


def rendered(value: Fraction) -> dict:
    with localcontext() as ctx:
        ctx.prec = 50
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"numerator": str(value.numerator),
            "denominator": str(value.denominator), "decimal50": decimal}


def main() -> None:
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    raw = (BASE / "inputs/F_CACHED_NUMERICAL_ARTIFACT.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    obj = json.loads(raw, parse_float=str, parse_int=str)
    window = Fraction(obj["T_s"])
    year = Fraction(obj["year_s"])
    rows = []
    values = {}
    for model, record in obj["models"].items():
        selected = {k: Fraction(record["selected"][k]) for k in FIELDS}
        births = [{k: Fraction(c[k]) for k in FIELDS}
                  for c in record["birth_columns"]]
        total_heat = sum((c["H0"] for c in births), Fraction(0))
        birth_defined = {"H0": total_heat}
        birth_defined.update({k: sum((c["H0"] * c[k] for c in births), Fraction(0))
                              / total_heat for k in FIELDS if k != "H0"})
        for representation, moment in (("selected_record", selected),
                                       ("birth_defined", birth_defined)):
            # These are local arithmetic/domain checks, not a rerun of H proofs.
            h0, p, r, s = (moment[k] for k in ("H0", "p", "R", "S"))
            assert h0 > 0 and 0 <= s <= r <= p <= 1
            m1 = window * (p-r)
            m2 = window**2 * (p-2*r+s)
            assert m1 >= 0 and m2 >= 0
            response = {"constant": p, "linear": r, "quadratic": s}
            row = {"model": model, "representation": representation,
                   "moments": {k: rendered(v) for k, v in moment.items()},
                   "response_over_H0_q0": {k: rendered(v) for k,v in response.items()},
                   "instantaneous_normalized_deficit": {k: rendered(1-v) for k,v in response.items()},
                   "heating_coefficient_per_q0_in_original_normalization":
                       {k: rendered(h0*v) for k,v in response.items()},
                   "truncated_m1_s": rendered(m1),
                   "truncated_m2_s2": rendered(m2),
                   "source_curvature_bound_coefficient_s2": rendered(m2/2),
                   "constant_source_cumulative_heat_over_H0_q0_T": rendered(r),
                   "linear_source_cumulative_heat_over_H0_q0_T_over2": rendered(s)}
            rows.append(row)
            values[model, representation] = (moment, response)
    differences = {}
    for rep in ("selected_record", "birth_defined"):
        f, rf = values["fullBED", rep]
        l, rl = values["legacy", rep]
        differences[rep] = {
            "H0_fullBED_over_legacy_minus1": rendered(f["H0"]/l["H0"]-1),
            "normalized_response_fullBED_over_legacy_minus1": {
                k: rendered(rf[k]/rl[k]-1) for k in rf},
            "heating_coefficient_fullBED_over_legacy_minus1": {
                k: rendered(f["H0"]*rf[k]/(l["H0"]*rl[k])-1) for k in rf}}
    result = {
        "schema": "cr-cached-onset-response.v1",
        "status": "EXACT_RATIONAL_POSTPROCESSING_OF_RECORDED_MOMENTS",
        "source_sha256": EXPECTED,
        "T_s": rendered(window), "T_years": rendered(window/year),
        "assumptions": ["Fixed nonnegative causal kernel with H0>0",
                        "Fixed bath and injection spectral shape; zero prehistory",
                        "Recorded decimal constraints are treated exactly",
                        "No inference of physical input error or mesh convergence"],
        "rows": rows, "model_differences": differences,
        "representation_policy": "Keep selected_record and birth_defined separate",
        "prohibited_claims": ["cosmological production history", "Bianchi-specific observable",
                              "unique reconstructed kernel", "physical-model error bound",
                              "historical F binding recovery", "measured NCP speedup"]}
    out = BASE / "results"
    out.mkdir(exist_ok=True)
    target = out / "CACHED_RESPONSE.json"
    if target.exists():
        raise FileExistsError("Existing completed postprocessing must be reused")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    with (out / "CACHED_RESPONSE.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(["model", "representation", "H0", "p", "R", "S",
                         "H0_p", "H0_R", "H0_S", "m1_truncated_s", "m2_truncated_s2"])
        for row in rows:
            writer.writerow([row["model"], row["representation"]]
                + [row["moments"][k]["decimal50"] for k in ("H0","p","R","S")]
                + [row["heating_coefficient_per_q0_in_original_normalization"][k]["decimal50"]
                   for k in ("constant","linear","quadratic")]
                + [row["truncated_m1_s"]["decimal50"], row["truncated_m2_s2"]["decimal50"]])
    arithmetic_wall = time.monotonic()-started
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.5), layout="constrained")
    labels = ["Constant", "Linear onset", "Quadratic onset"]
    colors = {"fullBED":"#2463a6", "legacy":"#ba6430"}
    for model, shift in (("fullBED",-.17),("legacy",.17)):
        _, response = values[model, "selected_record"]
        y = [100*float(response[k]) for k in ("constant","linear","quadratic")]
        bars=axes[0].bar([i+shift for i in range(3)], y, width=.32,
                        color=colors[model], label=model)
        axes[0].bar_label(bars, fmt="%.4f", fontsize=8, padding=3)
    axes[0].set_xticks(range(3),labels)
    axes[0].set_ylim(0,7.3)
    axes[0].set_ylabel(r"Heating at $T$ / instantaneous heating (%)")
    axes[0].set_title("Finite-age response; instantaneous = 100%", fontsize=11)
    axes[0].legend(frameon=False)
    diff=differences["selected_record"]
    delta=[100*float(values["fullBED","selected_record"][0]["H0"]
                     /values["legacy","selected_record"][0]["H0"]-1)]
    delta += [100*float(values["fullBED","selected_record"][0]["H0"]
                      *values["fullBED","selected_record"][1][k]
                      /(values["legacy","selected_record"][0]["H0"]
                        *values["legacy","selected_record"][1][k])-1)
              for k in ("constant","linear","quadratic")]
    bars=axes[1].bar(range(4),delta,color=["#606c76"]+["#2463a6"]*3,width=.6)
    axes[1].bar_label(bars,fmt="%+.4f",fontsize=8,padding=3)
    axes[1].axhline(0,color="#697780",lw=.8)
    axes[1].set_xticks(range(4),[r"$H_0$",r"$H_0p$",r"$H_0R$",r"$H_0S$"])
    axes[1].set_ylabel("(fullBED / legacy - 1) (%)")
    axes[1].set_ylim(-.215,.07)
    axes[1].set_title("Total-yield and finite-age response differences",fontsize=11)
    for axis in axes:
        axis.spines[["top","right"]].set_visible(False)
        axis.grid(axis="y",alpha=.18)
        axis.set_axisbelow(True)
    fig.suptitle(r"Recorded fixed-kernel response at $T=10^{10}$ s (316.88 yr)",fontsize=13)
    fig.supxlabel("Selected decimal records; birth-defined values are retained separately in the table.\nNo cosmological-history, physical-error, or new-cascade qualification is implied.",fontsize=9)
    fig.savefig(out/"CACHED_RESPONSE.png",dpi=180)
    fig.savefig(out/"CACHED_RESPONSE.pdf")
    plt.close(fig)
    receipt={"schema":"cr-cached-response-execution.v1", "started_utc":started_utc,
        "finished_utc":datetime.now(timezone.utc).isoformat(),
        "python":sys.version, "platform":platform.platform(),
        "postprocessing_invocations":1, "arithmetic_wall_s":arithmetic_wall,
        "in_process_total_wall_s":time.monotonic()-started,
        "counts":{"rows":4,"onset_response_functionals":12,"old_suite_runs":0,
                  "G":0,"pulse":0,"expm":0,"resolvent":0,"linear_solve":0,"NCP":0,"F_retry":0},
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs":[{"path":p.name,"bytes":p.stat().st_size,
                    "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in sorted(out.iterdir()) if p.is_file()]}
    (BASE/"evidence/POSTPROCESS_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"arithmetic_wall_s":arithmetic_wall,
                      "total_wall_s":receipt["in_process_total_wall_s"],"rows":4,"G":0}))


if __name__ == "__main__":
    main()
