#!/usr/bin/env python3
"""Read completed C21O arrays; make CSV/NPZ and PNG/PDF without any ODE call."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/c21o_mplconfig")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_run(path):
    base = Path(path).resolve()
    manifest = json.loads((base / "MANIFEST.json").read_text())
    rows = {}
    for case in manifest["grid"]["cases"]:
        folder = base / "cases" / case["case_id"]
        complete = json.loads((folder / "COMPLETE.json").read_text())
        receipt = json.loads((folder / "RECEIPT.json").read_text())
        if (complete["history_sha256"] != sha(folder / "history.npz") or
                complete["receipt_sha256"] != sha(folder / "RECEIPT.json") or receipt["case"] != case or
                receipt["source_identity_sha256"] != manifest["source"]["identity_sha256"]):
            raise ValueError("INPUT_BYTE_OR_IDENTITY_MISMATCH:" + case["case_id"])
        with np.load(folder / "history.npz", allow_pickle=False) as f:
            history = {k: f[k] for k in f.files}
        rows[case["case_id"]] = {"input": case, "receipt": receipt, "history": history,
                                  "history_sha256": complete["history_sha256"]}
    return manifest, rows


def savefig(fig, out, stem):
    fig.savefig(out / (stem + ".png"), dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(out / (stem + ".pdf"), bbox_inches="tight", facecolor="white",
                metadata={"CreationDate": None, "ModDate": None,
                          "Title": "C21O conditional H/He/Li LRS pilot"})
    plt.close(fig)


def axis_time(ax):
    ax.set_xlim(20, 2)
    ax.set_xlabel("Redshift z (time advances to the right)")
    ax.grid(alpha=.18)


def analyze(grid_path, controls_path, output_path):
    out = Path(output_path).resolve()
    out.mkdir(parents=True, exist_ok=False)
    gm, rows = read_run(grid_path)
    cm, controls = read_run(controls_path)
    if gm["source"]["identity_sha256"] != cm["source"]["identity_sha256"]:
        raise ValueError("GRID_CONTROL_SOURCE_MISMATCH")
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10,
                         "legend.fontsize": 9, "figure.titlesize": 15,
                         "axes.spines.top": False, "axes.spines.right": False})
    data = [r["history"] for r in rows.values()]
    z = data[0]["z"]
    cmap = plt.get_cmap("coolwarm")
    def stress_color(s):
        return "#555555" if s == 0 else cmap((s+.6)/1.2)
    initial_s = np.array([r["input"]["signed_sigma"] for r in rows.values()])
    endpoints = []
    for name, row in rows.items():
        h, inp = row["history"], row["input"]
        endpoints.append({"case_id": name, "S0_signed_full": inp["signed_sigma"],
                          "Pm0_signed_full": inp["signed_pi_m"], "Pr0_signed_full": inp["signed_pi_r"],
                          **{key: float(h[key][-1]) for key in ("Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F",
                                  "signed_Sigma_F", "signed_Pi_m_F", "signed_Pi_r_F", "signed_Pi_tot_F",
                                  "cancellation_fraction", "n_e_cm3", "tau_T", "temperature_K")}})
    with (out / "ENDPOINTS45.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(endpoints[0]))
        writer.writeheader(); writer.writerows(endpoints)
    aggregate = {"z": z, "eta": data[0]["eta"], "case_id": np.array(list(rows), dtype="U24"),
                 "initial_signed_Sigma": initial_s,
                 "initial_signed_Pi_m": np.array([r["input"]["signed_pi_m"] for r in rows.values()]),
                 "initial_signed_Pi_r": np.array([r["input"]["signed_pi_r"] for r in rows.values()])}
    for key in ("Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F", "signed_Sigma_F", "signed_Pi_m_F",
                "signed_Pi_r_F", "signed_Pi_tot_F", "cancellation_fraction", "n_e_cm3", "tau_T",
                "atomic_scaled", "atomic_abundance_per_Href", "omitted_trace_energy_H2_fraction"):
        aggregate[key] = np.stack([h[key] for h in data])
    with (out / "ENSEMBLE45.npz").open("xb") as f:
        np.savez_compressed(f, **aggregate)
    labels = list(data[0]["atomic_state_labels"])
    with (out / "ION_HISTORY45.csv").open("x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "z", "eta", "proper_elapsed_s", "n_e_cm3", "T_K", "tau_T"]
                        + ["Y_per_Href_" + str(k) for k in labels])
        for name, row in rows.items():
            h = row["history"]
            for i in range(z.size):
                writer.writerow([name, h["z"][i], h["eta"][i], h["proper_elapsed_s"][i],
                                 h["n_e_cm3"][i], h["temperature_K"][i], h["tau_T"][i]]
                                + h["atomic_abundance_per_Href"][:, i].tolist())

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    specs = [("Sigma_F", r"$\Sigma=\sqrt{6}|s|/H$", 1e-6),
             ("Pi_m_F", r"$\Pi_m$  (nonbaryonic massive stress)", 1e-8),
             ("Pi_r_F", r"$\Pi_r=|P_\gamma+P_\nu|$", 1e-8),
             ("Pi_tot_F", r"$\Pi_{\rm tot}=|P_m+P_r|$", 1e-8)]
    for ax, (key, label, lin) in zip(axes.flat, specs):
        for s, h in zip(initial_s, data):
            ax.plot(z, h[key], color=stress_color(s), lw=.9, alpha=.74)
        ax.set_title(label)
        ax.set_yscale("symlog", linthresh=lin)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Full Frobenius scalar norm (dimensionless)")
        axis_time(ax)
    handles = [Line2D([0], [0], color=stress_color(s), label=f"signed S0 = {s:g}")
               for s in (-.6, -.3, 0., .3, .6)]
    axes[0, 0].legend(handles=handles, ncol=2, loc="upper right")
    fig.suptitle("45 new LRS trajectories, z=20 to 2\nPrescribed UV/T; photo + Case-A RR; electron–Thomson coupling; L=8")
    savefig(fig, out, "STRESS_EVOLUTION45")

    center = rows["grid022"]["history"]
    fraction = aggregate["atomic_scaled"]
    fig, axes = plt.subplots(3, 3, figsize=(13.5, 10), constrained_layout=True)
    panels = [("H1", (1, 2)), ("D", (3, 4)), ("T", (5, 6)),
              ("He3", (7, 8, 9)), ("He4", (10, 11, 12)), ("electron", ()),
              ("Li6", (17, 18, 19, 20)), ("Li7", (13, 14, 15, 16)), ("n", (0,))]
    colors = ("#1f77b4", "#e67e22", "#2ca02c", "#ad2fad")
    for ax, (name, indices) in zip(axes.flat, panels):
        if name == "electron":
            electron = np.stack([h["n_e_cm3"] / h["nH_ref_cm3"] for h in data])
            ax.fill_between(z, electron.min(0), electron.max(0), color="#4576b5", alpha=.25)
            ax.plot(z, center["n_e_cm3"] / center["nH_ref_cm3"], color="#174a7c", lw=1.6)
            ax.set_title("Free electrons (algebraic charge closure)")
            ax.set_ylabel(r"$n_e/n_{H,ref}$")
        else:
            for q, index in enumerate(indices):
                values = fraction[:, index]
                ax.fill_between(z, values.min(0), values.max(0), color=colors[q], alpha=.16)
                ax.plot(z, center["atomic_scaled"][index], color=colors[q], lw=1.5, label=f"q={q}")
            ax.set_title(name + (" (zero initial parent)" if name in ("T", "n") else " charge fractions"))
            if name in ("T", "n"):
                ax.text(.5, .5, "All saved populations = 0\nDeclared late-time initial condition\nBeta adapters are implemented",
                        ha="center", va="center", transform=ax.transAxes, fontsize=9)
            ax.set_ylim(-.035, 1.04)
            ax.set_ylabel("Scaled abundance x = Y / isotope scale")
            ax.legend(ncol=min(4, len(indices)), loc="upper right")
        axis_time(ax)
    fig.suptitle("All 21 tracked populations and free electrons\nLine: FLRW case; band: min–max across 45 cases. Isotopes share electronic rates by assumption.")
    savefig(fig, out, "ION_EVOLUTION21")

    plus, minus = (controls[k]["history"] for k in ("cancellation_mplus", "cancellation_mminus"))
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for key, label, color in (("signed_Pi_m_F", "$P_m$", "#e67e22"),
                              ("signed_Pi_r_F", "$P_r$", "#2166ac"),
                              ("signed_Pi_tot_F", "$P_{tot}$", "#222222")):
        axes[0, 0].plot(z, plus[key], label=label, color=color)
    axes[0, 0].set_title(r"Initially $P_m=+5\times10^{-4},\ P_r=-5\times10^{-4}$")
    axes[0, 0].set_ylabel("Signed full stress coordinate")
    axes[0, 0].set_yscale("symlog", linthresh=1e-7)
    for h, lab, color in ((plus, "Pm0 > 0", "#e67e22"), (minus, "Pm0 < 0", "#2166ac")):
        axes[0, 1].plot(z, h["signed_Sigma_F"], label=lab, color=color)
        axes[1, 0].plot(z, h["cancellation_fraction"], label=lab, color=color)
    axes[0, 1].set_title("Shear generated from S0 = 0")
    axes[0, 1].set_ylabel(r"Signed $S_F=\sqrt{6}s/H$")
    axes[1, 0].set_title(r"$1-|P_m+P_r|/(|P_m|+|P_r|)$")
    axes[1, 0].set_ylabel("Cancellation fraction")
    axes[1, 0].set_ylim(0, 1.02)
    for key, label, color in (("signed_Pi_gamma_F", "CMB photons", "#d95f02"),
                              ("signed_Pi_nu_F", "Massless neutrinos", "#7570b3")):
        axes[1, 1].plot(z, plus[key], label=label, color=color)
    axes[1, 1].set_title("Separate radiation sectors (Pm0 > 0 case)")
    axes[1, 1].set_ylabel("Signed full stress coordinate")
    for ax in axes.flat:
        axis_time(ax); ax.legend()
        if ax is not axes[1, 0]:
            ax.axhline(0, color=".45", lw=.5)
    fig.suptitle("Tensor cancellation is not addition of scalar norms\nActual tiny initial floating-point offsets are retained")
    savefig(fig, out, "SIGNED_CANCELLATION")

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    for s, h in zip(initial_s, data):
        axes[0, 0].plot(z, h["tau_T"], color=cmap((s+.6)/1.2), lw=.8, alpha=.6)
        axes[0, 2].plot(z, h["omitted_trace_energy_H2_fraction"], color=cmap((s+.6)/1.2), lw=.8, alpha=.6)
    axes[0, 0].set_title("Accumulated optical depth from z=20")
    axes[0, 0].set_ylabel(r"$\tau_T(20\to z)$ (not optical depth to z=0)")
    axes[0, 1].plot(z, center["temperature_K"], color="#c45b28")
    axes[0, 1].set_title("Prescribed temperature input")
    axes[0, 1].set_ylabel("T [K]")
    axes[0, 2].set_title("Omitted thermal + ionization + UV energy")
    axes[0, 2].set_ylabel(r"Instantaneous $\epsilon_{H^2}$; no trajectory bound")
    axes[0, 2].set_yscale("log")
    numerical = {}
    for gname, cname, label in (("grid000", "negative_extreme_L12", "negative extreme"),
                                ("grid044", "positive_extreme_L12", "positive extreme")):
        base, ref = rows[gname]["history"], controls[cname]["history"]
        values = {k: float(np.max(abs(base[k]-ref[k]))) for k in ("Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F")}
        moment_diff = np.max(np.stack([np.max(abs(base[k]-ref[k][:, :9]), axis=1)
                                      for k in ("E_gamma", "N_gamma", "E_nu", "N_nu")]), axis=0)
        values["common_radiation_modes_ell_0_to_8_max_absolute"] = float(np.max(moment_diff))
        numerical[cname] = values
        line, = axes[1, 0].plot(z, np.maximum(abs(base["Sigma_F"]-ref["Sigma_F"]), 1e-19), label=label + " Sigma")
        axes[1, 0].plot(z, np.maximum(moment_diff, 1e-19), ls="--", color=line.get_color(), label=label + " modes")
    axes[1, 0].set_title("L8 vs L12: shear and common radiation modes")
    axes[1, 0].set_ylabel(r"Absolute difference; display floor $10^{-19}$ only")
    axes[1, 0].set_yscale("log"); axes[1, 0].legend(fontsize=8)
    radau = controls["flrw_radau"]["history"]
    diff = np.max(abs(center["atomic_scaled"]-radau["atomic_scaled"]), axis=0)
    axes[1, 1].plot(z, np.maximum(diff, 1e-19), color="#477a46")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_title("One FLRW BDF vs Radau comparison")
    axes[1, 1].set_ylabel(r"max$_i |\Delta x_i|$; display floor $10^{-19}$ only")
    on, off = rows["grid044"]["history"], controls["positive_extreme_thomson_off"]["history"]
    for key, label in (("signed_Pi_gamma_F", r"$P_\gamma$"), ("signed_Pi_nu_F", r"$P_\nu$")):
        axes[1, 2].plot(z, on[key]-off[key], label=label)
    axes[1, 2].set_title("Thomson on − off: different physical models")
    axes[1, 2].set_ylabel("Signed stress difference"); axes[1, 2].legend()
    for ax in axes.flat:
        axis_time(ax)
    fig.suptitle("Coupling and focused numerical diagnostics\nComparisons apply only to the displayed cases; global_error_bound = null")
    savefig(fig, out, "COUPLING_AND_NUMERICS")

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5), constrained_layout=True)
    for ax, s in zip(axes.flat, (-.6, -.3, 0., .3, .6)):
        matrix = np.array([r["Sigma_F"] for r in endpoints if r["S0_signed_full"] == s]).reshape(3, 3)
        im = ax.imshow(matrix, origin="lower", cmap="viridis", aspect="auto")
        for iy in range(3):
            for ix in range(3):
                mantissa, exponent = f"{matrix[iy, ix]:.3e}".split("e")
                cell_label = mantissa + "\n" + r"$\times10^{" + str(int(exponent)) + "}$"
                ax.text(ix, iy, cell_label, ha="center", va="center",
                        color="white" if matrix[iy, ix] < (matrix.max()+matrix.min())/2 else "black", fontsize=8)
        ax.set_xticks((0, 1, 2), ("−1.2e−3", "0", "+1.2e−3"))
        ax.set_yticks((0, 1, 2), ("−5e−4", "0", "+5e−4"))
        ax.set_xlabel("Initial signed Pr0"); ax.set_ylabel("Initial signed Pm0")
        ax.set_title(f"Initial signed S0 = {s:g}")
        fig.colorbar(im, ax=ax, label=r"$\Sigma(z=2)$", fraction=.046)
    axes[1, 2].axis("off")
    axes[1, 2].text(.02, .85, "Independent three-coordinate grid\n\n5 signed shear values × 3 matter × 3 radiation\n45 completed trajectories\n\nEach panel has its own labeled color scale.\nCompare annotated values across panels.\n\nNorms are nonnegative; input coordinates are signed.", va="top", fontsize=11)
    fig.suptitle("Endpoint shear across the independent-stress grid\nConditional LRS photo/RR–Thomson pilot, z=20 to 2")
    savefig(fig, out, "ENDPOINT_SLICES45")

    summary = {"status": "ANALYSIS_COMPLETED_SCOPED", "grid_cases": len(rows), "additional_cases": len(controls),
               "z_start": float(z[0]), "z_end": float(z[-1]), "time_samples": z.size,
               "source_identity_sha256": gm["source"]["identity_sha256"],
               "norm": "full Frobenius; source half norm times sqrt(2)",
               "global_error_bound": None, "new_ODE_runs_in_analyzer": 0,
               "endpoint_ranges": {k: {"min": float(min(r[k] for r in endpoints)), "max": float(max(r[k] for r in endpoints))}
                                   for k in ("Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F", "tau_T", "n_e_cm3")},
               "trajectory_maxima": {k: float(np.max(aggregate[k])) for k in ("Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F", "omitted_trace_energy_H2_fraction")},
               "FLRW_atomic_BDF_Radau_max_absolute": float(diff.max()),
               "L8_L12_selected_differences": numerical,
               "Thomson_on_off_max_signed_photon_Pi_difference": float(np.max(abs(on["signed_Pi_gamma_F"]-off["signed_Pi_gamma_F"]))),
               "FLRW_endpoint_scaled_populations": dict(zip(labels, map(float, center["atomic_scaled"][:, -1]))),
               "FLRW_ne_per_Href_endpoint": float(center["n_e_cm3"][-1]/center["nH_ref_cm3"][-1]),
               "cancellation_cases": {name: {"initial_signed_Ptot": float(row["history"]["signed_Pi_tot_F"][0]),
                                             "final_Sigma_F": float(row["history"]["Sigma_F"][-1]),
                                             "final_cancellation": float(row["history"]["cancellation_fraction"][-1])}
                                      for name, row in controls.items() if name.startswith("cancellation_")},
               "input_raw_sha256": {name: row["history_sha256"] for name, row in {**rows, **controls}.items()},
               "plot_scope": "preliminary conditional model; explicit panel scales/display floors; not full thermochemical nuclear prediction"}
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    output_manifest = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
                       for p in sorted(out.iterdir()) if p.is_file()]
    (out / "OUTPUT_MANIFEST.json").write_text(json.dumps(output_manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "grid_cases": len(rows), "additional_cases": len(controls),
                      "endpoint_ranges": summary["endpoint_ranges"], "new_ODE_runs": 0}), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid-run", required=True)
    p.add_argument("--control-run", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    analyze(a.grid_run, a.control_run, a.output)
