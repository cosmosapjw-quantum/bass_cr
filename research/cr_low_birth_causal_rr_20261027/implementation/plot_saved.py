#!/usr/bin/env python3
"""Render the saved new response once; no source, coefficient, or solver calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path


UNIT_ID = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--result-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    need(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID
         and os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "C4_OWNED_RUNNER_REQUIRED")
    reservation = json.loads((out / "RESERVATION.json").read_bytes())
    need(reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID")
         and reservation.get("unit") == UNIT_ID, "EXACT_RUNNER_RESERVATION_REQUIRED")
    raw = args.result.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == args.result_sha256, "SAVED_RESULT_IDENTITY_MISMATCH")
    data = json.loads(raw)
    need(data.get("unit") == UNIT_ID
         and data.get("numerical_acceptance", {}).get("internal_pass") is True,
         "ACCEPTED_SAVED_PRIMARY_RESULT_REQUIRED")
    prefixes, bins = data["prefixes"], data["observation_bins"]
    need(len(prefixes) == len(bins) == 4, "FOUR_SAVED_PREFIXES_AND_BINS_REQUIRED")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"text.usetex": False, "font.family": "DejaVu Sans",
                                "font.size": 10, "axes.titlesize": 11,
                                "svg.hashsalt": UNIT_ID})
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5), constrained_layout=True)
    x = [1, 2, 3, 4]
    labels = ["T/4", "T/2", "3T/4", "T"]
    categories = [
        ("active_energy_eV_m3", "Active electrons", "#2166ac"),
        ("cutoff_energy_eV_m3", "Unresolved cutoff", "#777777"),
        ("coulomb_energy_eV_m3", "Prescribed Coulomb transfer", "#e08214"),
    ]
    for key, label, color in categories:
        y = [row[key] / row["injected_energy_eV_m3"] for row in prefixes]
        axes[0].plot(x, y, "o-", label=label, color=color, linewidth=1.8, markersize=5)
    axes[0].set(xticks=x, xticklabels=labels, xlabel="Known-history endpoint (T = 10 billion s)",
                ylabel="Fraction of cumulative injected kinetic energy",
                title="Finite prefix energy diagnostics", ylim=(0, 1.05))
    axes[0].grid(axis="y", alpha=.25)
    axes[0].legend(loc="best", fontsize=8, frameon=False)
    axes[0].text(.03, .03, "Cutoff and caloric terms do not certify physical heating.",
                 transform=axes[0].transAxes, fontsize=8, wrap=True)
    all_positive = True
    for channel, label, color in (("H", "H1 ground RR", "#1b9e77"),
                                 ("He", "He4 ground RR", "#7570b3")):
        y = [row["channels"][channel]["retained_photon_number_m3"] for row in bins]
        all_positive = all_positive and all(value > 0 for value in y)
        axes[1].plot(x, y, "o-", label=label, color=color, linewidth=1.8, markersize=5)
    if all_positive:
        axes[1].set_yscale("log")
    axes[1].set(xticks=x, xticklabels=["0–T/4", "T/4–T/2", "T/2–3T/4", "3T/4–T"],
                xlabel="Disjoint proper-time observation bin",
                ylabel="Retained photons per proper cubic metre",
                title="Causal capture returns by observation bin")
    axes[1].tick_params(axis="x", labelsize=8)
    axes[1].grid(axis="y", alpha=.25)
    axes[1].legend(loc="best", fontsize=9, frameon=False)
    fig.suptitle("PHYS02 low birth (0.1–10 eV): fixed 100 K, conditional H1/He4", fontsize=12)
    artifacts = []
    try:
        for suffix, fmt in (("png", "png"), ("svg", "svg")):
            path = out / ("LOW_BIRTH_CAUSAL_RR." + suffix)
            with path.open("xb") as stream:
                fig.savefig(stream, format=fmt, dpi=140,
                            metadata={"Creator": UNIT_ID} if fmt == "svg" else {"Software": UNIT_ID})
            content = path.read_bytes()
            artifacts.append({"path": path.name, "bytes": len(content),
                              "sha256": hashlib.sha256(content).hexdigest()})
    finally:
        plt.close(fig)
    receipt = {"schema": "CR_LOW_BIRTH_SAVED_PLOT_V1", "unit": UNIT_ID,
               "saved_input_sha256": args.result_sha256, "artifacts": artifacts,
               "source_or_solver_execution": 0, "old_plot_rerendered": False,
               "raw_result_is_authoritative": True,
               "physical_heating_completed": False}
    with (out / "RESULT.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": "SAVED_NEW_RESULT_RENDERED", "files": len(artifacts)}))


if __name__ == "__main__":
    main()
