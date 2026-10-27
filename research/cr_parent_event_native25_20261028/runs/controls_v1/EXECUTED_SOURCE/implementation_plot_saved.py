"""Plot saved parent attribution and explicitly conditional caloric increments.

No source fitting, propagation, response reconstruction, or physical activation.
Execution requires the current unit's bounded worker reservation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
UNIT = Path(__file__).resolve().parents[1]


def digest(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(UNIT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", default="runs/primary_v1/RESULT.json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = (UNIT / args.out).resolve()
    if os.environ.get("CR_BOUNDED_UNIT") != UNIT_ID:
        raise RuntimeError("BOUNDED_CURRENT_UNIT_REQUIRED")
    if os.environ.get("CR_BOUNDED_OUTDIR") != str(out):
        raise RuntimeError("OWNED_OUTPUT_REQUIRED")
    attempt = os.environ.get("CR_BOUNDED_ATTEMPT_ID")
    reservation = json.loads((out / "RESERVATION.json").read_text())
    if not attempt or reservation.get("attempt_id") != attempt:
        raise RuntimeError("MATCHING_CURRENT_ATTEMPT_REQUIRED")
    if reservation.get("run_id") != out.name or not out.is_relative_to(UNIT / "runs"):
        raise RuntimeError("MATCHING_RUN_RESERVATION_REQUIRED")

    primary = (UNIT / args.primary).resolve()
    if not primary.is_relative_to(UNIT / "runs"):
        raise RuntimeError("SAVED_UNIT_RESULT_REQUIRED")
    array_path = primary.parent / "ATTRIBUTION_ARRAYS.npz"
    input_pins = [digest(primary), digest(array_path)]
    result = json.loads(primary.read_text())
    if result.get("unit") != UNIT_ID or not result.get("status", "").startswith("PASS"):
        raise RuntimeError("ACCEPTED_SCOPED_SAVED_RESULT_REQUIRED")

    # Scientific/plotting imports occur only after the bounded-attempt guard.
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with np.load(array_path, allow_pickle=False) as saved:
        energy = saved["energy_eV_with_cutoff"].copy()
        ah = saved["identified_A_H_m3_s2"].copy()
        ahe = saved["identified_A_He_m3_s2"].copy()
        residual = saved["atom_relative_error"].copy()
    if any(v.shape != (3201,) for v in (energy, ah, ahe, residual)):
        raise ValueError("EXPECTED_ORIGINAL_3200_ACTIVE_PLUS_GHOST")
    if not all(np.all(np.isfinite(v)) for v in (energy, ah, ahe, residual)):
        raise ValueError("NONFINITE_SAVED_PLOT_VALUE")
    if not (np.all(energy > 0) and np.all(ah >= 0) and np.all(ahe >= 0)
            and np.all(residual >= 0)):
        raise ValueError("SAVED_ATTRIBUTION_DOMAIN")

    prefixes = result["prefixes"]
    if len(prefixes) != 4:
        raise ValueError("FOUR_SAVED_PREFIXES_REQUIRED")
    times = [float(row["interval_s"][1]) / 1e10 for row in prefixes]
    retention = [float(row["conditional_caloric"]["retention"]["delta_logT"])
                 for row in prefixes]
    assimilation = [float(row["conditional_caloric"]["assimilation"]["delta_logT"])
                    for row in prefixes]
    tolerance = 2e-11  # Frozen R1 atom gate, not an estimated physical error.
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9,
                         "axes.titlesize": 10, "legend.fontsize": 8,
                         "svg.fonttype": "none", "savefig.facecolor": "white"})
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.2), constrained_layout=True)
    ax = axes[0]
    ax.loglog(energy[1:], ah[1:], color="#215c9a", label="H-origin electrons")
    ax.loglog(energy[1:], ahe[1:], color="#b35a17", label="He-origin electrons")
    ax.scatter([energy[0]], [ah[0]], facecolors="none", edgecolors="#215c9a",
               s=30, marker="s", zorder=4)
    ax.scatter([energy[0]], [ahe[0]], facecolors="none", edgecolors="#b35a17",
               s=30, marker="s", zorder=4)
    ax.set(xlabel="Original atom energy [eV]",
           ylabel=r"Projected $A_j$ [m$^{-3}$ s$^{-2}$]",
           title="Model-identified attribution")
    ax.text(.03, .04, "Squares: separate cutoff ghost", transform=ax.transAxes,
            fontsize=8)
    ax.legend(loc="upper right")
    ax.grid(True, which="major", alpha=.22)

    ax = axes[1]
    ax.plot(energy, residual, lw=.7, color="#3d6c55", label="Saved atom residual")
    ax.axhline(tolerance, color="#a12d35", lw=1.1, ls="--", label="Frozen 2e-11 gate")
    ax.set_xscale("log")
    # symlog keeps literal zero values visible; no epsilon/floor is added to data.
    ax.set_yscale("symlog", linthresh=1e-17)
    ax.set_ylim(0, max(2 * tolerance, 2 * float(np.max(residual))))
    ax.set(xlabel="Original atom energy [eV]",
           ylabel=r"$|A_H+A_{He}-A_{canonical}|/|A_{canonical}|$",
           title="Canonical-source consistency")
    ax.legend(loc="upper right")
    ax.grid(True, which="major", alpha=.22)

    ax = axes[2]
    ax.plot(times, retention, "o-", color="#215c9a", label="Retained cutoff + EOS")
    ax.plot(times, assimilation, "s--", color="#b35a17", label="Instant assimilation + EOS")
    ax.set(xlabel=r"Proper endpoint / $10^{10}$ s", ylabel=r"Saved $\Delta\log T$",
           title="Conditional p=d=0 fixtures")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useOffset=False)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=.22)
    fig.suptitle("PHYS02 selected low-birth source: partial return, actual full state unresolved",
                 fontsize=11)
    artifacts = []
    for name in ("PARENT_EVENT_DIAGNOSTICS.svg", "PARENT_EVENT_DIAGNOSTICS.png"):
        path = out / name
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=130)
        artifacts.append(digest(path))
    plt.close(fig)

    table = out / "PLOT_DATA.json"
    with table.open("x") as stream:
        json.dump({"schema": "CR_PARENT_EVENT_SAVED_PLOT_DATA_V1",
                   "input_pins": input_pins, "time_over_1e10_s": times,
                   "retention_delta_logT": retention,
                   "assimilation_delta_logT": assimilation,
                   "max_atom_relative_error": float(np.max(residual)),
                   "atom_tolerance": tolerance, "ghost_separate": True,
                   "actual_He_branch": None, "physical_heating_complete": False},
                  stream, indent=2)
        stream.write("\n")
    artifacts.append(digest(table))
    if input_pins != [digest(primary), digest(array_path)]:
        raise RuntimeError("SAVED_INPUT_CHANGED_DURING_PLOTTING")
    receipt = {"schema": "CR_PARENT_EVENT_SAVED_PLOT_RECEIPT_V1", "unit": UNIT_ID,
               "status": "PLOT_GENERATED_PENDING_VISUAL_AUDIT", "attempt_id": attempt,
               "input_pins": input_pins, "artifacts": artifacts, "figures": 1,
               "panels": 3, "scientific_recomputation": False,
               "old_source_RR_replay": 0, "new_fitting_calls": 0,
               "curve_values": "copied from saved arrays/scalars; float64 display conversion only",
               "limits": "Model attribution and p=d=0 conditional EOS; no exclusive He data or physical heating activation"}
    with (out / "PLOT_RECEIPT.json").open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "figures": 1, "panels": 3}))


if __name__ == "__main__":
    main()
