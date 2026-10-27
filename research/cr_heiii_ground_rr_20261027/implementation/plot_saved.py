"""Plot six saved finest-grid rows; no provider, engine, solver or ODE import."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import dispatch


def writej(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def run(unit, out, runid):
    started = time.process_time()
    c = json.loads((unit / "inputs/CONFIG.json").read_text())
    dispatch.authorize_run(unit, c, "plot", runid)
    source = unit / "runs" / dispatch.selected_input_run(unit, c, "primary") / "SOURCE_WEIGHTED_RESULTS.json"
    raw = source.read_bytes()
    allrows = json.loads(raw)["rows"]
    rows = sorted((row for row in allrows if row["R"] == 80 and row["N"] == 2048),
                  key=lambda row: (row["chi"], float(row["z"])))
    if len(rows) != 6:
        raise ValueError("SIX_SAVED_FINEST_ROWS_REQUIRED")
    fields = ["chi", "z", "P_HeII_RR_active", "conditional_HeII_RR_photon_eV",
              "delta_time_s_active", "delta_CE_active", "delta_H1_RR_active", "delta_HeI_RR_active"]
    values = [{key: row[key] for key in fields} for row in rows]
    writej(out / "PLOT_ROWS.json", {"source": str(source.relative_to(unit)),
        "source_sha256": hashlib.sha256(raw).hexdigest(), "rows": values, "source_RHS_replay": 0})
    with (out / "PLOT_ROWS.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(values)
    plt.rcParams.update({"font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.4), layout="constrained")
    axes = axes.ravel()
    for chi, color in ((1.5, "#186ca5"), (3, "#b75121")):
        subset = [row for row in rows if row["chi"] == chi]
        z = [float(row["z"]) for row in subset]
        curves = [[row["P_HeII_RR_active"] for row in subset],
                  [row["conditional_HeII_RR_photon_eV"] for row in subset],
                  [-1e3 * row["delta_time_s_active"] for row in subset],
                  [-row["delta_HeI_RR_active"] for row in subset]]
        for ax, curve in zip(axes, curves):
            ax.plot(z, curve, "o-", color=color, label=fr"$\chi={chi:g}$", linewidth=1.6, markersize=5)
    titles = ["HeIII ground capture probability", "Conditional retained photon energy",
              "Stored-column mean-time reduction", "Stored-column HeI capture reduction"]
    labels = ["Probability per active initial electron", "Energy (eV)",
              "Reduction (ms; positive = earlier stop)", "Probability reduction per active electron"]
    for ax, title, label in zip(axes, titles, labels):
        ax.set(title=title, xlabel="Saved source redshift z", ylabel=label)
        ax.grid(alpha=.22)
        ax.set_xticks([2.316, 2.479, 2.649])
        ax.legend(frameon=False)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 4), useOffset=False)
    fig.suptitle("He4III + fast electron -> He4II(1s) + retained photon\n"
                 "T = 10000 K; R = 80; nominal N = 2048; conditional elemental He4 mapping", fontsize=11)
    fig.savefig(out / "HEIII_RR_SAVED_RESULTS.png", dpi=180)
    fig.savefig(out / "HEIII_RR_SAVED_RESULTS.pdf")
    plt.close(fig)
    writej(out / "RESULT.json", {"schema": "CR_HEIII_SAVED_PLOT_V1", "status": "PASS", "rows": 6,
        "new_solver_calls": 0, "source_provider_calls": 0, "new_ODE": 0,
        "process_cpu_s": time.process_time() - started, "physical_heating": None})
    print("PASS six saved finest rows rendered")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit.resolve(), args.output.resolve(), args.run_id))
