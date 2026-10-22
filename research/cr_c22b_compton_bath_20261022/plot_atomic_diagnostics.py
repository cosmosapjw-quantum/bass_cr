#!/usr/bin/env python3
"""Plot preserved A/B LRS accepted atomic diagnostics; create-only, ODE0/RHS0."""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from diagnose_atomic import resource_admission

HERE = Path(__file__).resolve().parent
DATA = HERE / "atomic_diagnostics_v1"
CASES = {"C22A": "finite_uv_lrs", "C22B": "finite_uv_compton_lrs"}
COLORS = {"C22A": "#B65A20", "C22B": "#126FAD"}
RATE_FIELDS = {
    "HG_H_excitation": "HG_H_excitation_thermal_sink_eV_per_Href_s",
    "SW91_H1_CI": "SW91_H1_CI_thermal_sink_eV_per_Href_s"}
MASK_FIELDS = {"HG_H_excitation": "HG_H_excitation_valid_temperature",
               "SW91_H1_CI": "SW91_H1_CI_valid_temperature"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    with Path(path).open("x", encoding="utf8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def load_inputs():
    manifest_raw = (DATA / "ARTIFACTS.json").read_bytes()
    manifest = json.loads(manifest_raw)
    records = {row["path"]: row for row in manifest["files"]}
    reports, arrays, bindings = {}, {}, []
    for cohort, case in CASES.items():
        folder = DATA / cohort / case / "accepted"
        stored = {}
        for name in ("DIAGNOSTICS.json", "DIAGNOSTICS.npz"):
            path = folder / name
            raw = path.read_bytes()
            expected = records[str(path.relative_to(DATA))]
            if len(raw) != expected["size_bytes"] or digest(raw) != expected["sha256"]:
                raise RuntimeError("PLOT_INPUT_MANIFEST_MISMATCH:" + str(path))
            stored[name] = raw
            bindings.append({"path": str(path), "size_bytes": len(raw), "sha256": digest(raw)})
        reports[cohort] = json.loads(stored["DIAGNOSTICS.json"])
        with np.load(io.BytesIO(stored["DIAGNOSTICS.npz"]), allow_pickle=False) as npz:
            arrays[cohort] = {key: np.array(npz[key], copy=True) for key in npz.files}
        values = arrays[cohort]
        for process in RATE_FIELDS:
            rate = values[RATE_FIELDS[process]]
            valid = values[MASK_FIELDS[process]]
            if (valid.dtype.kind != "b" or not np.array_equal(np.isfinite(rate), valid)
                    or not np.all(np.isnan(rate[~valid])) or np.any(rate[valid] <= 0)):
                raise ValueError("PLOT_RATE_MASK_OR_LOG_SIGN:" + cohort + ":" + process)
        if np.any(values["temperature_K"] <= 0):
            raise ValueError("NONPOSITIVE_TEMPERATURE")
        rr = values["included_RR_cooling_eV_per_Href_s"]
        if not np.isfinite(rr).all() or np.any(rr <= 0):
            raise ValueError("RR_LOG_PLOT_REQUIRES_POSITIVE_AVAILABLE_RATES")
    return reports, arrays, {"artifact_manifest_sha256": digest(manifest_raw),
                            "files": bindings,
                            "reader": "same_manifest_verified_bytes_to_JSON_or_np.load(BytesIO)"}


def time_axis(ax):
    ax.set_xscale("symlog", linthresh=1e-4, linscale=.7)
    ax.set_xlim(0, np.log(7))
    ax.set_xlabel(r"$\eta=\ln(a/a_{\rm initial})$", fontsize=10)
    ax.grid(True, which="major", color="#DBE0E4", linewidth=.65)
    ax.tick_params(labelsize=9)


def build_figure(reports, arrays):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 12, "axes.titleweight": "semibold",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "savefig.facecolor": "white"})
    fig, axes = plt.subplots(2, 2, figsize=(14.6, 10.7))
    a, b, c, d = axes.flat
    for ax in (a, b, c):
        time_axis(ax)
        ax.set_yscale("log")
    a.set_title("(a) Gas temperature and lower fit limits", loc="left", pad=12)
    a.set_ylabel("Gas temperature [K]")
    for cohort in CASES:
        x = arrays[cohort]
        a.plot(x["eta"], x["temperature_K"], color=COLORS[cohort], lw=1.8, label=cohort)
    a.axhline(2000, color="#6A4D8C", ls="--", lw=.9)
    a.axhline(5000, color="#3D7755", ls=":", lw=1.1)
    a.text(.985, 2000, "CI: 2000 K", transform=a.get_yaxis_transform(),
           ha="right", va="bottom", fontsize=8.5, color="#6A4D8C",
           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2})
    a.text(.985, 5000, "Excitation: 5000 K", transform=a.get_yaxis_transform(),
           ha="right", va="bottom", fontsize=8.5, color="#3D7755",
           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2})
    a.legend(loc="lower left", frameon=True, fontsize=9)
    a.set_ylim(4, 20000)

    b.set_title("(b) HG excitation and included RR cooling", loc="left", pad=12)
    b.set_ylabel(r"Thermal sink [eV H$_{\rm ref}^{-1}$ s$^{-1}$]")
    for cohort in CASES:
        x = arrays[cohort]
        # Original NaNs remain in these line arrays. No interpolation or
        # filtering that would connect separated valid-temperature segments.
        b.plot(x["eta"], x[RATE_FIELDS["HG_H_excitation"]], color=COLORS[cohort], lw=1.9)
        b.plot(x["eta"], x["included_RR_cooling_eV_per_Href_s"],
               color=COLORS[cohort], lw=1.2, ls="--", alpha=.8)
    b.legend(handles=[Line2D([0], [0], color="#333333", lw=1.8, label="HG excitation"),
                      Line2D([0], [0], color="#333333", lw=1.2, ls="--", label="RR kinetic capture cooling")],
             loc="lower left", fontsize=8.8, frameon=True)
    b.text(.98, .97, "Colors: C22A orange / C22B blue", transform=b.transAxes,
           ha="right", va="top", fontsize=8.6)

    c.set_title("(c) SW91 H1 collisional ionization", loc="left", pad=12)
    c.set_ylabel(r"Thermal sink [eV H$_{\rm ref}^{-1}$ s$^{-1}$]")
    for cohort in CASES:
        x = arrays[cohort]
        c.plot(x["eta"], x[RATE_FIELDS["SW91_H1_CI"]], color=COLORS[cohort], lw=1.8)
    c.text(.025, .045, "H1 only; one-Ry energy per CI event\n"
           "CI energy enters ionization, not a separate radiative sink",
           transform=c.transAxes, ha="left", va="bottom", fontsize=8.7,
           bbox={"facecolor": "white", "edgecolor": "#D6DCE0", "alpha": .95, "pad": 4})

    d.set_title("(d) Partial energy integrals on accepted meshes", loc="left", pad=12)
    d.set_yscale("log")
    d.set_ylabel(r"Integrated kinetic loss [eV H$_{\rm ref}^{-1}$]")
    positions = np.arange(3, dtype=float)
    width = .31
    all_values = []
    for index, cohort in enumerate(CASES):
        report = reports[cohort]
        values = [report["included_RR_cooling_integral_eV_per_Href"]["value"]]
        values += [report["diagnostics"][key]["integrated_absolute_energy_eV_per_Href"]["value"]
                   for key in ("HG_H_excitation", "SW91_H1_CI")]
        all_values.extend(values)
        locs = positions + (index-.5)*width
        d.bar(locs, values, width=width, color=COLORS[cohort], alpha=.92, label=cohort, zorder=3)
        for x, value in zip(locs, values):
            d.text(x, value*1.18, f"{value:.4g}", ha="center", va="bottom", fontsize=8.3)
    d.set_ylim(min(all_values)/3, max(all_values)*3)
    coverage = {}
    for key in ("HG_H_excitation", "SW91_H1_CI"):
        coverage[key] = [100*reports[cohort]["diagnostics"][key]["integrated_absolute_energy_eV_per_Href"]["available_duration_fraction"] for cohort in CASES]
    d.set_xticks(positions, ["RR kinetic capture\n100% / 100%",
                 f"HG excitation\n{coverage['HG_H_excitation'][0]:.5g}% / {coverage['HG_H_excitation'][1]:.5g}%",
                 f"SW91 H1 CI\n{coverage['SW91_H1_CI'][0]:.5g}% / {coverage['SW91_H1_CI'][1]:.5g}%"])
    d.set_xlabel("Below each process: available proper time, C22A / C22B", fontsize=9, labelpad=10)
    d.tick_params(labelsize=9)
    d.grid(True, axis="y", which="major", color="#DBE0E4", lw=.65, zorder=0)
    d.legend(loc="upper right", fontsize=9, frameon=True)

    fig.suptitle("LRS atomic-process diagnostics before and after active Compton feedback", fontsize=16, y=.985)
    fig.text(.5, .950, "C22A baseline and C22B open CMB bath  |  original accepted meshes  |  no new ODE or RHS evaluations",
             ha="center", fontsize=10, color="#3E4A52")
    fig.tight_layout(rect=[0, .185, 1, .927], pad=1.5, h_pad=3.2, w_pad=2.3)
    footer = [
        "HG excitation: energy coefficient [erg cm³ s⁻¹], 5000–500000 K; H1+D+T electronic-isotope equality.",
        "SW91 H1 CI: rate coefficient [cm³ s⁻¹], 2000–1e8 K; thermal sink uses 1 Ry = 13.605693122994 eV/event (active chemistry: 13.6 eV).",
        "Unavailable coefficients remain NaN and are not joined by lines. Partial integrals use only valid adjacent endpoints; proper-time coverage is shown above.",
        "RR means kinetic capture cooling from the inherited fit-derived energy moment, not total exported recombination energy.",
        "These are trajectory diagnostics with finite-mesh quadrature, not self-consistent additions of CI/excitation. Full network coverage OPEN; global_error_bound = null."]
    for index, line in enumerate(footer):
        fig.text(.055, .140-.025*index, line, ha="left", va="center", fontsize=8.9,
                 color="#36434B")
    return fig, coverage


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "atomic_diagnostic_figures_v1")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--exclude-cpu", type=int, action="append", default=[])
    args = parser.parse_args(argv)
    if args.out.exists():
        raise FileExistsError("CREATE_ONLY_OUTPUT_EXISTS:" + str(args.out))
    runs = [HERE / "runs/c22b_compton_bdf_20261022_v1",
            HERE / "runs/c22b_compton_radau_20261022_v1",
            HERE.parent / "cr_c22a_thermochemical_20261022/runs/c22a_finite_uv_bdf_20261022_v1"]
    resource = resource_admission(runs, args.cpu, args.exclude_cpu)
    reports, arrays, binding = load_inputs()
    fig, coverage = build_figure(reports, arrays)
    args.out.mkdir(parents=True, exist_ok=False)
    outputs = []
    for extension in ("png", "pdf"):
        path = args.out / ("LRS_atomic_diagnostics." + extension)
        with path.open("xb") as handle:
            fig.savefig(handle, format=extension, dpi=180,
                        metadata={"Title": "LRS atomic-process diagnostics: C22A and C22B"})
        raw = path.read_bytes()
        outputs.append({"path": path.name, "size_bytes": len(raw), "sha256": digest(raw)})
    plt.close(fig)
    source_raw = Path(__file__).read_bytes()
    receipt = {"schema": "C22B_ATOMIC_DIAGNOSTIC_FIGURE_V1",
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "EXECUTION": "FIGURES_CREATED_FROM_PRESERVED_DIAGNOSTICS;ODE0;RHS0",
               "PUBLICATION": "PENDING_PARENT", "BACKUP": "PENDING_PARENT",
               "DAG": "PLOT_REVIEW_PENDING;FULL_NETWORK_COVERAGE_OPEN",
               "source_script_sha256": digest(source_raw), "matplotlib_version": matplotlib.__version__,
               "inputs": binding, "outputs": outputs, "resource": resource,
               "proper_time_coverage_percent": coverage,
               "unavailable_plot_policy": "original_NaN_values_in_lines;no_interpolation_or_gap_bridging",
               "RR_label": "kinetic capture cooling; not total exported recombination energy",
               "CI_energy_eV_per_event": 13.605693122994,
               "active_C22B_chemical_increment_eV": 13.6,
               "CI_scope": "SW91 H1 only; not extrapolated to D/T",
               "HG_scope": "existing C22A H1+D+T electronic-isotope-equality diagnostic profile",
               "plot_xaxis": "eta=ln(a/a_initial), symlog with linear threshold1e-4; no secondary redshift axis",
               "new_ODE_runs": 0, "RHS_evaluations": 0, "visual_review": "PENDING",
               "global_error_bound": None}
    write_json(args.out / "FIGURE_RECEIPT.json", receipt)
    print(json.dumps({"output": str(args.out), "files": outputs, "visual_review": "PENDING", "new_ODE_runs": 0}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
