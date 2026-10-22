#!/usr/bin/env python3
"""Saved-array C22A analysis. No model import, rate evaluation, or ODE call."""
from __future__ import annotations
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/c22a_matplotlib")

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import math
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SECONDS_PER_MYR = 365.25 * 86400. * 1e6
TIME_LINTHRESH_MYR = 1e-5
DIAGNOSTICS = ("energy_relative_residual", "nucleus_max_relative_residual",
               "charge_photon_relative_residual", "photon_number_relative_residual")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf8")


def json_create(path, value):
    with Path(path).open("x", encoding="utf8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def read_run(directory, allow_partial=False):
    base = Path(directory).resolve()
    inputs = json.loads((base / "INPUT.json").read_text())
    source = json.loads((base / "SOURCE_IDENTITY.json").read_text())
    runtime = json.loads((base / "RUNTIME.json").read_text())
    payload = dict(source)
    recorded_sha = payload.pop("identity_sha256")
    if recorded_sha != hashlib.sha256(canonical(payload)).hexdigest():
        raise ValueError("SOURCE_MANIFEST_DIGEST_MISMATCH")
    input_sha = hashlib.sha256(canonical(inputs)).hexdigest()
    if runtime["input_sha256"] != input_sha or runtime["source_identity_sha256"] != recorded_sha:
        raise ValueError("RUN_INPUT_OR_SOURCE_BINDING_MISMATCH")
    rows, missing = {}, []
    for case in inputs["cases"]:
        folder = base / "cases" / case["name"]
        if not (folder / "COMPLETE.json").is_file():
            missing.append({"name": case["name"], "failure_record": str(folder / "FAILURE.json")
                            if (folder / "FAILURE.json").is_file() else None})
            continue
        complete = json.loads((folder / "COMPLETE.json").read_text())
        receipt = json.loads((folder / "RECEIPT.json").read_text())
        raw_history = (folder / "history.npz").read_bytes()
        raw_history_sha = hashlib.sha256(raw_history).hexdigest()
        if (complete.get("status") != "COMPLETED_SCOPED"
                or complete["source_identity_sha256"] != recorded_sha
                or complete["input_sha256"] != input_sha
                or complete["history_sha256"] != raw_history_sha
                or complete["receipt_sha256"] != sha256(folder / "RECEIPT.json")
                or receipt["case"] != case or receipt["source_identity_sha256"] != recorded_sha
                or receipt["input_sha256"] != input_sha
                or receipt["history_sha256"] != complete["history_sha256"]
                or receipt["model_metadata_sha256"] != sha256(folder / "MODEL.json")):
            raise ValueError("CASE_BYTE_OR_IDENTITY_MISMATCH: " + case["name"])
        with np.load(io.BytesIO(raw_history), allow_pickle=False) as data:
            history = {key: data[key] for key in data.files}
        for key, value in history.items():
            if key == "cancellation_fraction":
                defined = history.get("cancellation_fraction_defined")
                if (defined is None or defined.dtype.kind != "b" or defined.shape != value.shape
                        or np.any(np.isinf(value)) or not np.array_equal(np.isfinite(value), defined)
                        or not np.all(np.isnan(value[~defined]))):
                    raise ValueError("INVALID_UNDEFINED_CANCELLATION_MASK")
            elif value.dtype.kind in "fci" and not np.all(np.isfinite(value)):
                raise ValueError("NONFINITE_HISTORY_ARRAY: " + key)
        n = len(history["eta"])
        for key in ("z", "proper_elapsed_s", "temperature_K", "n_e_cm3", "tau_T",
                    "energy_relative_residual", "energy_residual_eV_per_H"):
            if history[key].shape != (n,) or not np.all(np.isfinite(history[key])):
                raise ValueError("INVALID_HISTORY_VECTOR: " + key)
        if history["UV_photons_per_H"].shape != (n, 6):
            raise ValueError("UV_HISTORY_MUST_HAVE_TIME_BY_6_SHAPE")
        if not np.all(np.diff(history["proper_elapsed_s"]) > 0) or not np.all(np.diff(history["z"]) < 0):
            raise ValueError("NONMONOTONIC_TIME_OR_REDSHIFT")
        rows[case["name"]] = {"case": case, "history": history, "receipt": receipt,
                               "history_sha256": complete["history_sha256"]}
    if missing and not allow_partial:
        raise ValueError("INCOMPLETE_RUN; explicit --allow-partial required: "
                         + ",".join(row["name"] for row in missing))
    if not rows:
        raise ValueError("NO_COMPLETED_CASES")
    return {"path": str(base), "input": inputs, "source": source, "runtime": runtime,
            "rows": rows, "missing": missing}


def interp_with_extrapolation(value, xp, fp):
    arr = np.asarray(value, dtype=float)
    flat = arr.ravel()
    out = np.interp(flat, xp, fp)
    low, high = flat < xp[0], flat > xp[-1]
    out[low] = fp[0] + (flat[low] - xp[0]) * (fp[1] - fp[0]) / (xp[1] - xp[0])
    out[high] = fp[-1] + (flat[high] - xp[-1]) * (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    return out.reshape(arr.shape)


def axes_time_redshift(ax, history):
    t = history["proper_elapsed_s"] / SECONDS_PER_MYR
    z = history["z"]
    ax.set_xlim(t[0], t[-1])
    ax.set_xscale("symlog", linthresh=TIME_LINTHRESH_MYR, linscale=.6)
    ax.set_xlabel("Elapsed proper time from z=20 [Myr]\nsymlog; linear below 10 years")
    # A secondary_xaxis function transform does not automatically preserve a
    # symlog parent transform. Use an explicitly identical time scale, placing
    # redshift labels at their actual per-case time coordinates.
    sec = ax.twiny()
    sec.set_xscale("symlog", linthresh=TIME_LINTHRESH_MYR, linscale=.6)
    sec.set_xlim(t[0], t[-1])
    sec.set_xlabel("Redshift z (selected times)", labelpad=5)
    sec.tick_params(labelsize=9, pad=3)
    label_tol = 64 * np.finfo(float).eps * max(1., abs(z[0]), abs(z[-1]))
    marks = [x for x in (20, 10, 2) if z[-1] - label_tol <= x <= z[0] + label_tol]
    locations = interp_with_extrapolation(marks, z[::-1], t[::-1])
    sec.set_xticks(locations, labels=[str(x) for x in marks])
    sec.set_xticks([], minor=True)
    ax.set_title(ax.get_title(), pad=54, fontsize=11)
    ax.grid(alpha=.2)


def physical_scale(ax, values, zero_threshold=1e-12):
    """Use log only when all plotted values are positive; never floor data."""
    values = np.asarray(values)
    if np.all(values > 0):
        ax.set_yscale("log")
    elif np.all(values == 0):
        ax.set_yscale("linear")
    else:
        ax.set_yscale("symlog", linthresh=zero_threshold)


def savefig(fig, output, stem):
    fig.savefig(output / (stem + ".png"), dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(output / (stem + ".pdf"), bbox_inches="tight", facecolor="white",
                metadata={"Title": "C22A finite-UV thermochemical LRS pilot",
                          "CreationDate": None, "ModDate": None})
    plt.close(fig)


def make_case_figure(name, row, output):
    h = row["history"]
    t = h["proper_elapsed_s"] / SECONDS_PER_MYR
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(t, h["temperature_K"], color="#bd4c21")
    physical_scale(ax, h["temperature_K"])
    ax.set_ylabel("Gas temperature [K]")
    ax.set_title("Evolved thermal state")
    ax = axes[0, 1]
    ax.plot(t, h["n_e_cm3"], color="#1768a5")
    physical_scale(ax, h["n_e_cm3"], 1e-15)
    ax.set_ylabel(r"Free-electron density [cm$^{-3}$]")
    ax.set_title("Algebraic charge closure")
    ax = axes[0, 2]
    uv = h["UV_photons_per_H"]
    for j in range(6):
        energy0 = h["UV_cohort_energies_eV"][0, j]
        ax.plot(t, uv[:, j], lw=1.2, label=f"E0 = {energy0:g} eV")
    ax.plot(t, uv.sum(axis=1), "k--", lw=1.4, label="total")
    physical_scale(ax, uv, 1e-14)
    ax.set_ylabel(r"UV photons / reference H nucleus")
    ax.set_title("Finite cohorts; photon energies redshift")
    ax.legend(fontsize=8, ncol=2)
    ax = axes[1, 0]
    energy_keys = (("thermal_energy_eV_per_H", "thermal"),
                   ("ionization_energy_eV_per_H", "ionization"),
                   ("UV_energy_eV_per_H", "UV"),
                   ("escaped_energy_eV_per_H", "cumulative RR export"),
                   ("gas_work_eV_per_H", "gas expansion work"),
                   ("UV_work_eV_per_H", "UV redshift work"))
    for key, label in energy_keys:
        ax.plot(t, h[key], label=label, lw=1.15)
    physical_scale(ax, np.stack([h[key] for key, _ in energy_keys]), 1e-10)
    ax.set_ylabel("Energy accounting [eV / reference H nucleus]")
    ax.set_title("Reservoirs and accumulated transfers")
    ax.legend(fontsize=8, ncol=2)
    ax = axes[1, 1]
    ax.plot(t, h["energy_relative_residual"], color="#71409b")
    ax.axhline(0, color=".4", lw=.6)
    ax.set_yscale("symlog", linthresh=1e-12)
    ax.set_ylabel("Signed relative energy-accounting residual")
    ax.set_title("Energy conservation residual")
    ax = axes[1, 2]
    ledger_items = (("nucleus_max_relative_residual", "nuclei"),
                       ("charge_photon_relative_residual", "charge + photo/RR ledger"),
                       ("photon_number_relative_residual", "UV photon count"))
    ledger_max = max(float(np.max(abs(h[key]))) for key, _ in ledger_items)
    exponent = int(math.floor(math.log10(ledger_max))) if ledger_max else 0
    display_scale = 10.**exponent
    for key, label in ledger_items:
        ax.plot(t, h[key]/display_scale, label=label)
    ax.axhline(0, color=".4", lw=.6)
    ax.set_yscale("linear")
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    ax.set_ylabel(r"Relative invariant residual [$\times10^{" + str(exponent) + r"}$]")
    ax.set_title("Number conservation residuals")
    ax.legend(fontsize=8)
    for ax in axes.flat:
        axes_time_redshift(ax, h)
    title = {"dark_expansion": "Expansion and residual recombination: no UV",
             "finite_uv_flrw": "FLRW: finite-UV thermochemical pilot",
             "finite_uv_lrs": "LRS: finite-UV thermochemical pilot"}.get(name, name)
    fig.suptitle(f"{title}\n"
                 "Finite initial UV + photoionization / Case-A RR; imposed isotropic UV closure", fontsize=14)
    savefig(fig, output, "THERMOCHEMISTRY_" + name)


def compare_runs(left, right):
    if left["source"]["identity_sha256"] != right["source"]["identity_sha256"]:
        raise ValueError("COMPARISON_REQUIRES_IDENTICAL_EXECUTION_SOURCE")
    comparisons = {}
    for name in sorted(set(left["rows"]) & set(right["rows"])):
        a, b = left["rows"][name], right["rows"][name]
        if a["case"] != b["case"]:
            raise ValueError("COMPARISON_PHYSICS_INPUT_MISMATCH: " + name)
        if not np.array_equal(a["history"]["eta"], b["history"]["eta"]):
            raise ValueError("COMPARISON_SAVED_GRID_MISMATCH: " + name)
        measures = {}
        for key in ("temperature_K", "n_e_cm3", "tau_T", "UV_photons_per_H",
                    "atomic_scaled", "energy_relative_residual", "Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F"):
            aa, bb = a["history"][key], b["history"][key]
            diff = float(np.max(np.abs(aa - bb)))
            scale = float(max(np.max(np.abs(aa)), np.max(np.abs(bb))))
            measures[key] = {"saved_max_absolute_difference": diff,
                             "difference_over_max_signal": diff / scale if scale else 0.,
                             "signal_scale": scale}
        comparisons[name] = measures
    if not comparisons:
        raise ValueError("NO_MATCHING_CASE_NAMES_FOR_COMPARISON")
    return {"left_run": left["path"], "right_run": right["path"],
            "left_method": left["input"]["method"], "right_method": right["input"]["method"],
            "left_tolerances": {k: left["input"][k] for k in ("rtol", "atol")},
            "right_tolerances": {k: right["input"][k] for k in ("rtol", "atol")},
            "cases": comparisons, "scope": "common cases only; same source, physical input and saved eta grid",
            "global_error_bound": None}


def analyze(run_path, output_path=None, compare_path=None, allow_partial=False):
    run = read_run(run_path, allow_partial)
    other = read_run(compare_path, allow_partial) if compare_path else None
    comparison = compare_runs(run, other) if other else None
    output = Path(output_path).resolve() if output_path else Path(run["path"]) / "analysis"
    output.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 9,
                         "legend.fontsize": 8, "axes.spines.right": False})
    endpoint_rows, case_summary = [], {}
    for name, row in run["rows"].items():
        h = row["history"]
        endpoint = {"name": name, "elapsed_Myr": float(h["proper_elapsed_s"][-1] / SECONDS_PER_MYR),
                    "redshift": float(h["z"][-1])}
        for key in ("temperature_K", "n_e_cm3", "tau_T", "Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F",
                    "energy_total_eV_per_H", "energy_residual_eV_per_H", "energy_relative_residual"):
            endpoint[key] = float(h[key][-1])
        endpoint["UV_photons_per_H_total"] = float(h["UV_photons_per_H"][-1].sum())
        endpoint_rows.append(endpoint)
        case_summary[name] = {"history_sha256": row["history_sha256"],
                              "solver_wall_seconds": row["receipt"]["wall_seconds"],
                              "saved_times": len(h["eta"]), "endpoint": endpoint,
                              "saved_extrema": {key: {"min": float(np.min(h[key])),
                                                       "max": float(np.max(h[key])),
                                                       "max_abs": float(np.max(np.abs(h[key])))}
                                                  for key in DIAGNOSTICS},
                              "minimum_saved_population": float(np.min(h["atomic_scaled"])),
                              "minimum_saved_UV_cohort": float(np.min(h["UV_photons_per_H"])),
                              "minimum_saved_temperature_K": float(np.min(h["temperature_K"]))}
        make_case_figure(name, row, output)
    with (output / "ENDPOINTS.csv").open("x", newline="", encoding="utf8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(endpoint_rows[0]))
        writer.writeheader()
        writer.writerows(endpoint_rows)
    scalar_keys = ("temperature_K", "n_e_cm3", "tau_T", "UV_energy_eV_per_H",
                   "thermal_energy_eV_per_H", "ionization_energy_eV_per_H", "escaped_energy_eV_per_H",
                   "gas_work_eV_per_H", "UV_work_eV_per_H", "energy_total_eV_per_H",
                   "energy_residual_eV_per_H", *DIAGNOSTICS,
                   "Sigma_F", "Pi_m_F", "Pi_r_F", "Pi_tot_F")
    with (output / "HISTORY.csv").open("x", newline="", encoding="utf8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "eta", "z", "elapsed_Myr", *scalar_keys,
                         *[f"UV_cohort_{j+1}_per_H" for j in range(6)]])
        for name, row in run["rows"].items():
            h = row["history"]
            for i in range(len(h["eta"])):
                writer.writerow([name, h["eta"][i], h["z"][i], h["proper_elapsed_s"][i] / SECONDS_PER_MYR,
                                 *[h[key][i] for key in scalar_keys], *h["UV_photons_per_H"][i]])
    if comparison:
        json_create(output / "COMPARISON.json", comparison)
    summary = {"schema": "C22A_SAVED_ANALYSIS_V1", "utc": datetime.now(timezone.utc).isoformat(),
               "status": "PARTIAL_ANALYSIS" if run["missing"] else "COMPLETE_SAVED_DATA_ANALYSIS",
               "run_path": run["path"], "input_identity_sha256": run["runtime"]["input_sha256"],
               "input_file_sha256": sha256(Path(run["path"]) / "INPUT.json"),
               "source_identity_sha256": run["source"]["identity_sha256"],
               "cases": case_summary, "missing_cases": run["missing"],
               "comparison": comparison,
               "plot_contract": {"x_axis": "elapsed proper Myr from z20; symlog, zero preserved",
                                 "x_linthresh_Myr": TIME_LINTHRESH_MYR,
                                 "secondary_x_axis": "explicit shared-symlog time transform with per-case interpolated redshift tick positions",
                                 "physical_y": "log when every plotted value is positive; otherwise symlog/linear",
                                 "residual_y": "energy signed symlog; number ledgers linear scientific notation; zero retained",
                                 "saved_value_clipping_or_floor": "NONE"},
               "scientific_scope": "Finite-cohort thermal/ionization/radiative accounting; acceptance is separately reviewed",
               "undefined_0_over_0": "cancellation_fraction NaN is retained only where its explicit boolean defined mask is false; infinity forbidden",
               "global_error_bound": None, "ODE_evaluations_by_analyzer": 0}
    json_create(output / "SUMMARY.json", summary)
    artifacts = [{"name": p.name, "size_bytes": p.stat().st_size, "sha256": sha256(p)}
                 for p in sorted(output.iterdir()) if p.is_file()]
    json_create(output / "ARTIFACTS.json", {"files": artifacts, "global_error_bound": None})
    print(json.dumps({"analysis": str(output), "cases": list(run["rows"]),
                      "status": summary["status"], "new_ODE": 0}, allow_nan=False))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--compare-run", type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args(argv)
    analyze(args.run, args.out, args.compare_run, args.allow_partial)


if __name__ == "__main__":
    main()
