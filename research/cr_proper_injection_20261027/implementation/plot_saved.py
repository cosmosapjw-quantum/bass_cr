#!/usr/bin/env python3
"""Plot saved actual/reference JSON only; no source or transport recalculation.

One figure is exported once to PNG and once to SVG. The original JSON retains
the authoritative values and precision. Run only through the admitted runner.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


TAGS = ("direct_0p1_10", "direct_10_900", "selected_total")
TAG_LABELS = ("Low birth: 0.1-10 eV", "High birth: 10-900 eV",
              "Selected total: 0.1-900 eV")
COLORS = ("#0072B2", "#D55E00", "#009E73")
FIELDS = ("number_m3", "coordinate_energy_J_m3")
EXPECTED_STATE = "PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_saved(path, schema):
    raw = path.read_bytes()
    data = json.loads(raw)
    need(isinstance(data, dict) and data.get("schema") == schema,
         "EXPECTED_SAVED_RESULT_SCHEMA:" + str(path))
    return data, {"path": str(path), "bytes": len(raw),
                  "sha256": hashlib.sha256(raw).hexdigest()}


def number(value, name):
    need(type(value) in (int, float) and math.isfinite(value) and value >= 0,
         name + ":FINITE_NONNEGATIVE_SAVED_VALUE_REQUIRED")
    return float(value)


def row_key(row):
    need(isinstance(row, dict) and row.get("tag") in TAGS, "SAVED_BIRTH_TAG_REQUIRED")
    window = row.get("window_s")
    need(isinstance(window, list) and len(window) == 2, "SAVED_WINDOW_PAIR_REQUIRED")
    start, stop = (number(value, "window_s") for value in window)
    need(start <= stop, "ORDERED_SAVED_WINDOW_REQUIRED")
    return row["tag"], start.hex(), stop.hex()


def window_label(window):
    # Labels are display-roundings of recorded boundaries, never new windows.
    return "[" + format(window[0], ".7g") + ",\n " + format(window[1], ".7g") + "]"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--out-prefix", required=True, type=Path)
    args = parser.parse_args(argv)
    actual, actual_pin = load_saved(args.actual, "CR_PROPER_ACTUAL_RESULTS_V1")
    reference, reference_pin = load_saved(args.reference,
                                         "CR_PROPER_INJECTION_DECIMAL80_REFERENCE_V1")
    need(reference.get("status") == "PASS_SCOPED"
         and reference.get("producer_comparison") == "COMPLETED",
         "SAVED_INDEPENDENT_COMPARISON_PASS_REQUIRED")
    need(reference.get("producer_output_pin", {}).get("sha256") == actual_pin["sha256"],
         "REFERENCE_MUST_PIN_THIS_ACTUAL_JSON")
    checks = reference.get("checks")
    need(isinstance(checks, list) and bool(checks)
         and reference.get("check_count") == len(checks)
         and reference.get("pass_count") == len(checks)
         and all(check.get("pass") is True for check in checks),
         "COMPLETE_SAVED_REFERENCE_PASS_REQUIRED")
    need(actual.get("actual_RR_admitted") is False
         and actual.get("actual_nb_m3") is None
         and actual.get("actual_native25") is None
         and actual.get("physical_heating_complete") is False,
         "ACTUAL_SCOPE_AND_NULLS_CHANGED")
    physical_definition = actual.get("physical_definition", {})
    need(physical_definition.get("state") == EXPECTED_STATE
         and physical_definition.get("known_time_s") == [0.0, 1.0e10],
         "EXACT_SAVED_PHYS02_STATE_AND_CLOCK_REQUIRED")
    actual_rows = actual.get("rows")
    reference_rows = reference.get("rows")
    need(isinstance(actual_rows, list) and isinstance(reference_rows, list),
         "SAVED_ROWS_REQUIRED")
    actual_by_key, reference_by_key = {}, {}
    windows = []
    for row in actual_rows:
        key = row_key(row)
        need(key not in actual_by_key, "DUPLICATE_ACTUAL_ROW")
        actual_by_key[key] = row
        if row["window_s"] not in windows:
            windows.append(row["window_s"])
        for field in FIELDS:
            number(row.get(field), "actual." + field)
    for row in reference_rows:
        key = row_key(row)
        need(key not in reference_by_key, "DUPLICATE_REFERENCE_ROW")
        reference_by_key[key] = row
        for field in FIELDS:
            value = row.get(field + "_decimal")
            need(isinstance(value, str), "SAVED_DECIMAL_REFERENCE_REQUIRED")
            number(float(value), "reference." + field)
    expected = {(tag, float(window[0]).hex(), float(window[1]).hex())
                for tag in TAGS for window in windows}
    need(len(windows) == 6 and len(expected) == 18
         and set(actual_by_key) == expected and set(reference_by_key) == expected,
         "EXACT_SAVED_18_ROW_WINDOW_TAG_COVERAGE_REQUIRED")
    png = Path(str(args.out_prefix) + ".png")
    svg = Path(str(args.out_prefix) + ".svg")
    manifest_path = Path(str(args.out_prefix) + "_MANIFEST.json")
    need(args.out_prefix.parent.is_dir(), "PRECREATED_OUTPUT_DIRECTORY_REQUIRED")
    need(all(not path.exists() for path in (png, svg, manifest_path)),
         "CREATE_ONLY_PLOT_OUTPUTS_REQUIRED")

    # Matplotlib is the only non-stdlib dependency. No production module, NumPy
    # decoder, provider, quadrature, projection or reference solver is imported.
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams.update({"text.usetex": False, "font.family": "DejaVu Sans",
                                "svg.fonttype": "none", "axes.unicode_minus": False,
                                "font.size": 9})
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter

    figure = Figure(figsize=(13.0, 6.0), facecolor="white")
    FigureCanvasAgg(figure)
    axes = figure.subplots(1, 2)
    figure.subplots_adjust(left=0.075, right=0.985, bottom=0.25, top=0.77, wspace=0.28)
    legend_handles = []
    width = 0.23
    for panel, (axis, field) in enumerate(zip(axes, FIELDS)):
        positive = []
        for index, (tag, label, color) in enumerate(zip(TAGS, TAG_LABELS, COLORS)):
            keys = [(tag, float(window[0]).hex(), float(window[1]).hex()) for window in windows]
            values = [number(actual_by_key[key][field], field) for key in keys]
            saved_reference = [float(reference_by_key[key][field + "_decimal"]) for key in keys]
            positions = [i + (index - 1) * width for i in range(len(windows))]
            bars = axis.bar(positions, values, width=width * 0.94, color=color,
                            edgecolor="white", linewidth=0.4, label=label, zorder=3)
            axis.plot(positions, saved_reference, linestyle="none", marker="o",
                      markersize=3.4, markerfacecolor="none", markeredgewidth=0.8,
                      markeredgecolor="#202020", zorder=4)
            positive.extend(value for value in values if value > 0)
            if panel == 0:
                legend_handles.append(bars)
        need(bool(positive), "POSITIVE_SAVED_SOURCE_VALUES_REQUIRED")
        # A symmetric-log axis displays both six-decade small windows and the
        # exactly zero [T,T] interval without replacing zero by a fabricated floor.
        axis.set_yscale("symlog", linthresh=min(positive) / 5, linscale=0.4, base=10)
        axis.set_ylim(0, max(positive) * 8)
        axis.yaxis.set_major_formatter(FuncFormatter(lambda value, position:
                                                     "0" if value == 0 else format(value, ".0e")))
        axis.set_xticks(range(len(windows)), [window_label(window) for window in windows])
        axis.tick_params(axis="x", labelsize=7.5)
        axis.grid(axis="y", color="#dddddd", linewidth=0.6, zorder=0)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.set_xlabel("Recorded proper-time window (s)", labelpad=9)
        axis.set_title("Integrated source number" if panel == 0 else "Integrated source kinetic energy",
                       fontsize=11, fontweight="semibold", pad=12)
        axis.set_ylabel("Electron number density (m^-3)" if panel == 0 else
                        "Kinetic energy density (J m^-3)", labelpad=9)
        for index, window in enumerate(windows):
            if window[0] == window[1]:
                axis.annotate("exactly zero", (index, 0), xytext=(0, 7),
                              textcoords="offset points", ha="center", fontsize=7)
    legend_handles.append(Line2D([], [], color="#202020", linestyle="none", marker="o",
                                 markerfacecolor="none", markersize=4))
    figure.suptitle("Actual saved PHYS02 source: finite proper-time integrals",
                   fontsize=15, fontweight="semibold", y=0.96)
    figure.legend(legend_handles, (*TAG_LABELS, "Saved Decimal reference"),
                  loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=4,
                  frameon=False, fontsize=9, handlelength=1.5, columnspacing=1.6)
    figure.text(0.075, 0.12,
                "Bars: saved actual JSON. Open circles: saved independent reference. "
                "The raw JSON values and precision are authoritative.", fontsize=8.5)
    figure.text(0.075, 0.083,
                "Symlog vertical axes preserve exact zero and small-window values. "
                "T = 10^10 proper seconds; bath temperature = 100 K.", fontsize=8.5)
    figure.text(0.075, 0.046,
                "Finite recorded history only. nb, native25 and RR return remain null; "
                "no physical heating or post-record continuation is inferred.",
                fontsize=8.5, color="#404040")
    with png.open("xb") as stream:
        figure.savefig(stream, format="png", dpi=120,
                       metadata={"Software": "CR proper injection saved-result plot"})
    with svg.open("xb") as stream:
        figure.savefig(stream, format="svg", metadata={"Creator": "plot_saved.py", "Date": None})
    figure.clear()
    outputs = []
    for path in (png, svg):
        raw = path.read_bytes()
        outputs.append({"path": str(path), "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {
        "schema": "CR_PROPER_SAVED_PLOT_MANIFEST_V1",
        "inputs": {"actual": actual_pin, "reference": reference_pin},
        "outputs": outputs, "rows": len(expected), "tags": list(TAGS), "windows_s": windows,
        "displayed_fields": list(FIELDS), "authoritative_numeric_source": "original input JSON",
        "reference_decimal_to_binary64_for_display_only": True,
        "saved_reference_status": reference["status"],
        "saved_reference_pass_count": reference["pass_count"],
        "source_calculation": False, "source_quadrature_replay": 0,
        "source_projection_replay": 0, "transport_solver_replay": 0,
        "production_module_imported": False, "physical_heating_complete": False,
    }
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"outputs": outputs, "manifest": str(manifest_path),
                      "source_calculation": False, "rows": len(expected)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
