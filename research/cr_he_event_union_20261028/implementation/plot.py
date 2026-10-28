#!/usr/bin/env python3
"""C8: render one stored primary RESULT; never replay source or RR physics.

Only presentation ratios and exact input-consistency checks are evaluated here.
The parent run_bounded.py owns CPU accounting, memory limits and timeouts.
Deterministic bytes require the same input and Matplotlib/font/runtime versions.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import sys


UNIT = "CR_PHYS02_HE_EVENT_UNION_V1"
INPUT_SCHEMA = "CR_HE_EVENT_UNION_PRIMARY_V1"
NPZ_SHA = "1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47"
SOURCE_SHA = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
WITNESSES = ("single", "diagonal", "halfshift")
STEM = "HE_EVENT_UNION_SCOPE"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value):
    require(type(value) in (str, int), "EXACT_SERIALIZED_NUMBER_REQUIRED")
    return Fraction(value)


def finite_float(value):
    number = float(value)
    require(math.isfinite(number), "NONFINITE_DISPLAY_VALUE")
    return number


def sci(value):
    return format(finite_float(value), ".4e")


def load_primary(path):
    """Read exactly one scientific input file, once, and bind its actual bytes."""
    require(path.name == "RESULT.json", "PRIMARY_RESULT_FILE_REQUIRED")
    require(path.stat().st_size <= 16 * 1024 * 1024, "PRIMARY_RESULT_TOO_LARGE")
    raw = path.read_bytes()
    data = json.loads(raw)
    require(data.get("schema") == INPUT_SCHEMA, "PRIMARY_SCHEMA_MISMATCH")
    require(data.get("unit") == UNIT, "PRIMARY_UNIT_MISMATCH")
    require(data.get("status") == "PASS_SCOPED", "ACCEPTED_PRIMARY_REQUIRED")
    inp = data["input"]
    require(inp.get("sha256") == NPZ_SHA, "ATTRIBUTION_NPZ_PIN_MISMATCH")
    require(inp.get("canonical_source_sha256") == SOURCE_SHA, "CANONICAL_SOURCE_PIN_MISMATCH")
    require(inp.get("attribution_provenance") == "STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS",
            "ACTUAL_SAVED_ATTRIBUTION_REQUIRED")
    require(inp.get("attribution_is_not_canonical_source_replacement") is True,
            "ATTRIBUTION_SCOPE_MISMATCH")
    require(data.get("actual_Ccross") is None and data.get("actual_exclusive_measure") is None
            and data.get("actual_full_native25") is None and data.get("physical_activation") is False,
            "UNRESOLVED_PHYSICAL_FIELDS_CHANGED")
    require(data.get("old_source_fit_or_projection_calls") == 0 and data.get("old_RR_calls") == 0,
            "NO_REPLAY_CONTRACT_MISMATCH")
    require(data["logical_check_count"] == data["logical_pass_count"] > 0
            and all(item.get("pass") is True for item in data["checks"]),
            "PRIMARY_CHECKS_NOT_ALL_ACCEPTED")
    require(data["atomwise_comparison_count"] == data["atomwise_pass_count"] == 3 * 3201,
            "PRIMARY_ATOMWISE_ACCEPTANCE_MISMATCH")
    counts = tuple(exact(x) for x in data["coefficient_count_m3_s2"])
    atom_counts = data["partition_atom_counts"]
    require(len(counts) == len(atom_counts) == len(data["partition_labels"]) == 4,
            "FOUR_BIRTH_PARTITIONS_REQUIRED")
    require(all(x > 0 for x in counts) and atom_counts[0] == 1
            and sum(atom_counts[1:]) == 3200, "SAVED_BIRTH_PARTITION_SCOPE_MISMATCH")
    final = data["final_prefix"]
    n = exact(final["N_He_m3"])
    cmax = exact(final["Cmax_m3"])
    require(n > 0 and 0 < cmax <= n / 2, "POSITIVE_SAVED_BOUND_REQUIRED")
    require(exact(final["Cmax_over_N"]) == cmax / n, "SAVED_NORMALIZED_BOUND_MISMATCH")
    require(len(data["prefixes"]) == len(data["disjoint_birth_time_bins"]) == 4,
            "FINITE_HISTORY_PARTITION_MISMATCH")
    require(tuple(exact(x) for x in data["prefixes"][-1]["window_s"]) == (0, 10000000000),
            "SAVED_FINAL_PREFIX_HISTORY_MISMATCH")
    witness_values = []
    for name in WITNESSES:
        consumer = data["witnesses"][name]["consumer"]
        union = consumer["union"]
        require(exact(union["selected_electrons"]) == n
                and exact(union["selected_energy_eV_m3"]) == exact(final["U_He_eV_m3"]),
                "WITNESS_FIXED_MARGINAL_MISMATCH")
        require(consumer["actual_full_native25"] is None
                and consumer["actual_exclusive_event_measure"] is None
                and consumer["full_physical_consumer_activation"] is False,
                "WITNESS_PHYSICAL_GATE_CHANGED")
        require(exact(consumer["RR_correction"]) == exact(consumer["retained_photon_correction"]) == 0,
                "SEPARATE_RR_OR_PHOTON_PORT_CHANGED")
        witness_values.append(tuple(exact(v) / n for v in
                                    (union["parents"], union["d"], consumer["cross_duplicate_parent_density"])))
    half = data["witnesses"]["halfshift"]["consumer"]
    correction = tuple(exact(x) / n for x in half["correction_to_sum_of_partition_ion_density21"][10:13])
    charge = exact(half["ionic_charge_correction_m3"]) / n
    require(correction == (cmax / n, 0, -cmax / n) and charge == -2 * cmax / n,
            "SAVED_CORRECTION_ENDPOINT_MISMATCH")
    require(witness_values[0][2] == witness_values[1][2] == 0
            and witness_values[2][2] == cmax / n, "SAVED_WITNESS_ENDPOINT_MISMATCH")
    return data, counts, n, cmax, witness_values, correction, charge, {
        "path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "schema": data["schema"], "unit": data["unit"],
        "attribution_npz_sha256": inp["sha256"],
        "atom_content_sha256": inp["atom_content_sha256"],
        "canonical_source_sha256": inp["canonical_source_sha256"],
        "source_pin_verification": "pins in the single accepted primary result; source bytes not reread here",
    }


def artifact(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main(outdir=None, input_path=None):
    unit = Path(os.environ.get("CR_UNIT_ROOT", str(Path(__file__).resolve().parents[1]))).resolve()
    configured_outdir = os.environ.get("CR_BOUNDED_OUTDIR")
    require(outdir is not None or configured_outdir is not None, "BOUNDED_OUTPUT_DIRECTORY_REQUIRED")
    outdir = Path(outdir if outdir is not None else configured_outdir).resolve()
    if configured_outdir is not None:
        require(outdir == Path(configured_outdir).resolve(), "BOUNDED_OUTPUT_DIRECTORY_MISMATCH")
    require(outdir.is_dir() and outdir.is_relative_to(unit), "RUNNER_CREATED_UNIT_OUTPUT_REQUIRED")
    selected = input_path or os.environ.get("CR_PLOT_INPUT") or "runs/primary_v1/RESULT.json"
    source_path = Path(selected)
    if not source_path.is_absolute():
        source_path = unit / source_path
    source_path = source_path.resolve()
    require(source_path.is_relative_to(unit) and source_path.parent != outdir, "SAME_UNIT_PRIMARY_INPUT_REQUIRED")
    data, counts, n, cmax, values, correction, charge, input_meta = load_primary(source_path)
    png_path, svg_path, result_path = (outdir / (STEM + ".png"), outdir / (STEM + ".svg"), outdir / "RESULT.json")
    require(not any(p.exists() for p in (png_path, svg_path, result_path)), "CREATE_ONLY_PLOT_OUTPUTS_REQUIRED")
    os.environ.setdefault("MPLCONFIGDIR", str(outdir / "mplcache"))
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogLocator, LogFormatterMathtext, MaxNLocator

    settings = {
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 11,
        "axes.labelsize": 9, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.7, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "svg.hashsalt": input_meta["sha256"], "svg.fonttype": "path",
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "text.usetex": False, "path.simplify": False,
    }
    with matplotlib.rc_context(settings):
        fig = plt.figure(figsize=(15.0, 7.2), dpi=160)
        grid = fig.add_gridspec(1, 3, left=0.08, right=0.985, bottom=0.34, top=0.76,
                               wspace=0.48, width_ratios=(1.0, 1.0, 1.13))
        ax_a, ax_b, ax_c = (fig.add_subplot(grid[0, k]) for k in range(3))
        fig.suptitle("He source-parent union at a fixed PHYS02 electron marginal", y=0.96,
                     fontsize=17, fontweight="bold")
        fig.text(0.5, 0.905, "Conditional 100 K H1/He4 inventory | gas-rest proper-density frame | finite birth history [0, 10^10] s",
                 ha="center", fontsize=10)
        fig.text(0.5, 0.864, "Actual C: UNKNOWN    |    Actual exclusive He kernel: NULL    |    Full physical native25: NULL",
                 ha="center", fontsize=10, color="#8C3D28", fontweight="bold",
                 bbox={"facecolor": "#FCF2EC", "edgecolor": "#E7C1AE", "boxstyle": "round,pad=0.45"})

        # A: source coefficients, not time-integrated events or atom cardinalities.
        xvalues = [finite_float(x) for x in counts]
        lower = 10.0 ** (math.floor(math.log10(min(xvalues))) - 0.15)
        upper = max(xvalues) * 6.0
        ax_a.barh(range(4), xvalues, height=0.58,
                  color=("#9A9A9A", "#2E7799", "#348F8C", "#5B6FA9"), zorder=3)
        ax_a.set_xscale("log")
        ax_a.set_xlim(lower, upper)
        ax_a.set_yticks(range(4),
                       [f"Ghost at 0.1 eV\n1 stored atom",
                        f"(0.1, 1] eV\n{data['partition_atom_counts'][1]} atoms",
                        f"(1, 3] eV\n{data['partition_atom_counts'][2]} atoms",
                        f"(3, 10] eV\n{data['partition_atom_counts'][3]} atoms"])
        ax_a.invert_yaxis()
        ax_a.xaxis.set_major_locator(LogLocator(base=10, numticks=5))
        ax_a.xaxis.set_major_formatter(LogFormatterMathtext())
        ax_a.grid(axis="x", alpha=0.2, zorder=0)
        ax_a.set_title("A  Birth-partition coefficients", loc="left", pad=15)
        ax_a.set_xlabel(r"$\sum_{j\in A_i} A_j$  [proper m$^{-3}$ s$^{-2}$], log axis", labelpad=8)
        for y, value in enumerate(xvalues):
            ax_a.text(0.98, y, format(value, ".3e"), transform=ax_a.get_yaxis_transform(),
                      ha="right", va="center", fontsize=8,
                      bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.0})
        ax_a.text(0, -0.26, "q_j(t) = t A_j; 3,200 active atoms + 1 cutoff ghost.\nThe ghost does not supply a sub-cutoff spectrum.",
                  transform=ax_a.transAxes, va="top", fontsize=9, linespacing=1.5)

        # B: all intervals are saved endpoints normalized by one fixed saved N.
        bound = finite_float(cmax / n)
        endpoints = (bound, finite_float(correction[0]), finite_float(correction[2]), finite_float(charge))
        labels = (r"$C/N$", r"$\delta n_{\rm HeI}/N$", r"$\delta n_{\rm HeIII}/N$", r"$\delta Q_{\rm ion}/N$")
        for y, endpoint in enumerate(endpoints):
            color = "#2E7799" if endpoint > 0 else "#B46836"
            ax_b.plot([min(0.0, endpoint), max(0.0, endpoint)], [y, y], color=color, linewidth=6,
                      solid_capstyle="butt", alpha=0.72)
            ax_b.scatter([0.0, endpoint], [y, y], color=color, marker="|", s=110, zorder=3)
        ax_b.axvline(0.0, color="#444444", linewidth=0.8, zorder=0)
        ax_b.set_yticks(range(4), labels)
        ax_b.set_ylim(3.6, -0.6)
        ax_b.set_xlim(-2.30 * bound, 1.3 * bound)
        ax_b.xaxis.set_major_locator(MaxNLocator(5))
        ax_b.grid(axis="x", alpha=0.2, zorder=0)
        ax_b.set_title("B  Allowed union correction", loc="left", pad=15)
        ax_b.set_xlabel("Density correction / fixed N", labelpad=8)
        chem = data["final_prefix"]["chemical_correction_interval_eV_m3"]
        ax_b.text(0, -0.26,
                  f"C in [0, {sci(cmax)}] proper m^-3; delta HeII = 0.\n"
                  f"Chemical correction: [{sci(exact(chem[0]))}, {sci(exact(chem[1]))}] eV m^-3.\n"
                  "Corrections are to separately summed partition returns.\n"
                  "This envelope is not a confidence or source-error interval.",
                  transform=ax_b.transAxes, va="top", fontsize=9, linespacing=1.5)

        # C: source parent counts distinguish a total double count from cross C.
        metric_labels = ("Distinct parent count / N", "Total double-event count / N", "Cross-duplicate count C / N")
        metric_colors = ("#4E647A", "#63A09A", "#D28A43")
        width = 0.22
        for metric in range(3):
            heights = [finite_float(v[metric]) for v in values]
            positions = [k + (metric - 1) * width for k in range(3)]
            ax_c.bar(positions, heights, width=width, label=metric_labels[metric],
                     color=metric_colors[metric], zorder=3)
            for x, height in zip(positions, heights):
                ax_c.text(x, height + 0.018, format(height, ".3g"), ha="center", va="bottom", fontsize=8)
        ax_c.set_xticks(range(3), ("All single", "Within-atom\ndouble", "Half-shift\npairing"))
        ax_c.set_ylim(0, 1.20)
        ax_c.set_xlim(-0.6, 2.6)
        ax_c.grid(axis="y", alpha=0.2, zorder=0)
        ax_c.set_ylabel("Density / fixed N")
        ax_c.set_title("C  Three conditional witnesses", loc="left", pad=15)
        ax_c.legend(loc="upper right", fontsize=7.5, frameon=False)
        ax_c.text(0, -0.26,
                  "All three retain the same electron count and energy.\n"
                  "C is distinct from the total double-event count.\n"
                  "Witnesses do not select an actual exclusive event kernel.",
                  transform=ax_c.transAxes, va="top", fontsize=9, linespacing=1.5)

        fig.text(0.08, 0.10,
                 f"One stored final birth prefix: N = {sci(n)} proper m^-3.  "
                 "Four cumulative prefixes are not added.  RR and retained photons stay separate, once-only ports.",
                 fontsize=9, color="#444444")
        fig.text(0.08, 0.058, "Primary RESULT SHA256: " + input_meta["sha256"], fontsize=8,
                 family="DejaVu Sans Mono", color="#555555")
        fig.text(0.08, 0.031, "Display only: stored accepted coefficients and witness outputs; no source-fit, projection, transport or RR replay.",
                 fontsize=8, color="#555555")
        description = "Conditional He event-union figure; primary RESULT SHA256 " + input_meta["sha256"]
        try:
            with png_path.open("xb") as stream:
                fig.savefig(stream, format="png", dpi=160,
                            metadata={"Software": UNIT + " C8", "Description": description})
            with svg_path.open("xb") as stream:
                fig.savefig(stream, format="svg",
                            metadata={"Date": None, "Creator": UNIT + " C8", "Description": description,
                                      "Title": "He source-parent event-union conditional scope"})
        finally:
            plt.close(fig)

    result = {
        "schema": "CR_HE_EVENT_UNION_PLOT_V1", "unit": UNIT, "status": "PASS_SCOPED",
        "scope": "CONDITIONAL_HE_EVENT_UNION_PLOT", "input": input_meta,
        "actual_input_sha256": input_meta["sha256"], "scientific_input_files_read": 1,
        "plots": {"png": artifact(png_path), "svg": artifact(svg_path)},
        "figure_count": 1, "panel_count": 3, "renderer": {"matplotlib": matplotlib.__version__, "backend": "Agg"},
        "actual_Ccross": None, "actual_exclusive_measure": None, "actual_full_native25": None,
        "physical_activation": False, "old_source_fit_or_projection_calls": 0, "old_RR_calls": 0,
        "presentation": {"A": "Four saved birth-partition coefficient counts; log axis and atom cardinalities separated",
                         "B": "Saved conditional union-correction endpoints divided by one saved final-prefix N",
                         "C": "Stored parent, total-double and cross-duplicate counts for three conditional witnesses divided by N",
                         "new_physical_estimate": False, "interval_is_confidence_or_source_error": False,
                         "determinism": "fixed layout, Agg, bundled DejaVu fonts, input-SHA SVG salt, no timestamp metadata; same rendering runtime required"},
        "budget": "Measured and charged only by the parent run_bounded.py receipt",
    }
    with result_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "scope": result["scope"],
                      "actual_input_sha256": input_meta["sha256"],
                      "plot_paths": {"png": str(png_path), "svg": str(svg_path)},
                      "result_path": str(result_path)}, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outdir", nargs="?")
    parser.add_argument("--input", dest="input_path")
    args = parser.parse_args()
    result = main(args.outdir, args.input_path)
    sys.exit(0 if result["status"] == "PASS_SCOPED" else 1)
