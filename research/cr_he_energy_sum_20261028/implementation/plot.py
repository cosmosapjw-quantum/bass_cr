"""Publication figure from saved primary/independent results only.

Authoring status: no execution/import/compilation by the plot author.
Usage: python implementation/plot.py OUTDIR [--summary SUMMARY_JSON]
       [--independent INDEPENDENT_RESULT_JSON]

The worker reads two saved JSON files, checks their actual PASS evidence,
and draws conditional finite-atom envelopes.  It imports no production
module, NPZ loader, source model, oracle or CAS.  Root performs visual QA
on the generated PNG after this measured worker finishes.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import traceback


UNIT = "CR_PHYS02_HE_ENERGY_SUM_V1"
PASS = "PASS_SCOPED_ENERGY_SUM"
REFERENCE_SHA = "58ede1228866a8ca29cce838b7fbfb473c872ea9ef20ec0faf69066df276983b"
STORED_CUTOFF = Fraction(3602879701896397, 36028797018963968)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value):
    require(type(value) in (int, str, Fraction), "EXACT_SAVED_SCALAR_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("FINITE_SAVED_SCALAR_REQUIRED") from exc


def json_exact(value):
    if type(value) is Fraction:
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_exact(v) for v in value]
    return value


def scientific_text(value):
    """Readable label without binary64 underflow for a tiny exact ratio."""
    if value == 0:
        return "0"
    with localcontext() as context:
        context.prec = 5
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal, ".3E")


def read_saved(path):
    raw = path.read_bytes()

    def reject_constant(value):
        raise ValueError("NONFINITE_JSON_LITERAL:" + value)

    content = json.loads(raw, parse_constant=reject_constant)
    require(type(content) is dict, "SAVED_JSON_OBJECT_REQUIRED")
    require(content.get("unit") == UNIT, "SAVED_UNIT_MISMATCH")
    require(content.get("status") == PASS, "SAVED_INPUT_NOT_ACTUAL_PASS")
    return content, {
        "path": str(path), "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "unit": content["unit"], "status": content["status"],
    }


def validate_saved(summary, independent):
    """Check saved values and cross-file identities; do not rerun science."""
    require(summary.get("native_atom_count") == 3201, "SAVED_NATIVE_ATOM_COUNT")
    require(summary.get("active_atom_count") == 3200, "SAVED_ACTIVE_ATOM_COUNT")
    require(summary.get("cutoff_ghost_count") == 1, "SAVED_GHOST_COUNT")
    require(summary.get("small_case_count") == 48, "SAVED_SMALL_CASE_COUNT")
    require(summary.get("native_case_count") == 9, "SAVED_NATIVE_CASE_COUNT")
    cutoff = exact(summary["cutoff_energy_eV"])
    ghost = exact(summary["cutoff_coefficient"])
    total = exact(summary["N"])
    require(cutoff == STORED_CUTOFF, "STORED_CUTOFF_IDENTITY_MISMATCH")
    require(ghost >= 0 and total > 0 and ghost <= total, "SAVED_SOURCE_MASS_DOMAIN")

    groups = independent["check_groups"]
    require(groups["failed"] == 0 and groups["not_run"] == 0, "INDEPENDENT_CHECKS_INCOMPLETE")
    require(groups["passed"] == groups["total"], "INDEPENDENT_GROUP_COUNT_MISMATCH")
    require(
        independent["reference"]["sha256"] == REFERENCE_SHA,
        "INDEPENDENT_REFERENCE_IDENTITY_MISMATCH",
    )
    results = independent["results"]
    small = results["small"]
    native = results["native"]
    require(type(small) is list and len(small) == 48, "INDEPENDENT_SMALL_RESULT_COUNT")
    require(type(native) is list and len(native) == 9, "INDEPENDENT_NATIVE_RESULT_COUNT")

    oracle_agreements = 0
    maximum_gaps = []
    marginal_residuals = []
    for row in small:
        oracle = row["oracle"]
        require(oracle["production_dmax_equal"] is True, "ORACLE_AGREEMENT_FLAG")
        require(exact(oracle["dmax"]) == exact(row["input"]["dmax"]), "SAVED_ORACLE_DMAX_MISMATCH")
        oracle_agreements += 1
        maximum = row["maximum"]
        target = row["target"]["certificate"]
        require(maximum["optimality_certified"] is True, "SMALL_MAXIMUM_NOT_CERTIFIED")
        maximum_gaps.append(abs(exact(maximum["primal_dual_gap"])))
        marginal_residuals.extend((
            abs(exact(maximum["marginal_max_abs_residual"])),
            abs(exact(target["marginal_max_abs_residual"])),
        ))

    native_by_id = {row["id"]: row for row in native}
    require(len(native_by_id) == 9, "NATIVE_RESULT_IDS_DUPLICATED")
    raw_rows = summary["native_cap_rows"]
    require(type(raw_rows) is list and len(raw_rows) == 9, "SAVED_CAP_ROW_COUNT")
    expected_caps = (
        Fraction(0), Fraction(1, 5), 2 * cutoff, Fraction(1),
        Fraction(2), Fraction(3), Fraction(6), Fraction(10), Fraction(20),
    )
    rows = []
    previous_maximum = Fraction(0)
    native_certificates = 0
    for raw, expected_cap in zip(raw_rows, expected_caps):
        cap = exact(raw["K_eV"])
        n = exact(raw["N"])
        maximum_value = exact(raw["dmax"])
        requested = exact(raw["target_d"])
        fraction = exact(raw["dmax_over_N"])
        parent_lower = exact(raw["parent_min_over_N"])
        require(cap == expected_cap, "SAVED_CAP_ORDER_OR_EXACT_VALUE_MISMATCH")
        require(n == total, "SAVED_TOTAL_MASS_INCONSISTENT")
        require(0 <= requested <= maximum_value <= n / 2, "SAVED_ENVELOPE_DOMAIN")
        require(fraction == maximum_value / n, "SAVED_DOUBLE_FRACTION_MISMATCH")
        require(parent_lower == (n - maximum_value) / n, "SAVED_PARENT_FRACTION_MISMATCH")
        require(maximum_value >= previous_maximum, "SAVED_CAP_MONOTONICITY_FAILURE")
        previous_maximum = maximum_value
        require(exact(raw["primal_dual_gap"]) == 0, "PRIMARY_MAXIMUM_GAP_NONZERO")
        require(exact(raw["marginal_residual"]) == 0, "PRIMARY_MARGINAL_RESIDUAL_NONZERO")

        checked = native_by_id[raw["id"]]
        require(checked["input"]["atom_count"] == 3201, "CHECKED_NATIVE_ATOM_COUNT")
        require(exact(checked["input"]["K"]) == cap, "CROSS_FILE_CAP_MISMATCH")
        require(exact(checked["input"]["dmax"]) == maximum_value, "CROSS_FILE_DMAX_MISMATCH")
        require(exact(checked["input"]["target_d"]) == requested, "CROSS_FILE_TARGET_MISMATCH")
        maximum = checked["maximum"]
        target = checked["target"]["certificate"]
        require(maximum["status"] == "PASS_EXACT_EXPLICIT_CERTIFICATE", "NATIVE_MAXIMUM_STATUS")
        require(maximum["optimality_certified"] is True, "NATIVE_MAXIMUM_NOT_CERTIFIED")
        require(target["upper_bound_certified"] is True, "NATIVE_TARGET_NOT_CERTIFIED")
        require(exact(maximum["N"]) == n, "CHECKED_NATIVE_TOTAL_MASS")
        require(exact(maximum["double_coefficient"]) == maximum_value, "CHECKED_NATIVE_DMAX")
        require(exact(target["double_coefficient"]) == requested, "CHECKED_NATIVE_TARGET")
        require(
            exact(target["primal_dual_gap"]) == maximum_value - requested,
            "TARGET_UPPER_BOUND_GAP_MISMATCH",
        )
        maximum_gaps.append(abs(exact(maximum["primal_dual_gap"])))
        marginal_residuals.extend((
            abs(exact(maximum["marginal_max_abs_residual"])),
            abs(exact(target["marginal_max_abs_residual"])),
        ))
        native_certificates += 1
        rows.append({
            "id": raw["id"], "K_eV": cap, "N": n,
            "dmax": maximum_value, "target_d": requested,
            "dmax_over_N": fraction, "parent_min_over_N": parent_lower,
        })

    require(oracle_agreements == 48 and native_certificates == 9, "CERTIFICATE_COVERAGE_INCOMPLETE")
    max_gap = max(maximum_gaps, default=Fraction(0))
    max_residual = max(marginal_residuals, default=Fraction(0))
    require(max_gap == 0 and max_residual == 0, "SAVED_EXACT_CERTIFICATE_RESIDUAL_NONZERO")
    require(rows[1]["dmax"] == 0, "DECIMAL_CUTOFF_EXPECTED_ZERO")
    require(rows[2]["dmax"] == ghost / 2, "STORED_CUTOFF_GHOST_HALF_IDENTITY")
    require(2 * cutoff > Fraction(1, 5), "EXACT_CUTOFF_CAP_DISTINCTION_LOST")
    return {
        "rows": rows, "N": total,
        "cutoff_energy_eV": cutoff, "cutoff_coefficient": ghost,
        "cutoff_cap_difference_eV": 2 * cutoff - Fraction(1, 5),
        "oracle_agreements": oracle_agreements,
        "small_case_count": len(small),
        "native_maximum_certificates": native_certificates,
        "native_case_count": len(native),
        "maximum_witness_max_dual_gap": max_gap,
        "maximum_marginal_abs_residual": max_residual,
        "native_atom_count": summary["native_atom_count"],
        "active_atom_count": summary["active_atom_count"],
        "cutoff_ghost_count": summary["cutoff_ghost_count"],
        "independent_check_groups": groups,
    }


def file_identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def draw_figure(saved, outdir):
    # Delayed import: invalid saved evidence fails before plotting startup.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "axes.edgecolor": "#53616F",
        "xtick.color": "#33414D",
        "ytick.color": "#33414D",
        "text.color": "#172B3A",
        "mathtext.fontset": "dejavusans",
        "svg.fonttype": "none",
        "svg.hashsalt": UNIT,
        "savefig.facecolor": "white",
    })
    rows = saved["rows"]
    xs = [float(row["K_eV"]) for row in rows]
    double_fraction = [float(row["dmax_over_N"]) for row in rows]
    parent_lower = [float(row["parent_min_over_N"]) for row in rows]
    blue, orange, gray = "#245E85", "#BB5B2A", "#9BA7B1"

    fig = plt.figure(figsize=(13.6, 5.8), facecolor="white")
    grid = fig.add_gridspec(
        1, 3, width_ratios=(1.20, 1.20, 1.02),
        left=0.065, right=0.985, bottom=0.29, top=0.77, wspace=0.34,
    )
    ax_double = fig.add_subplot(grid[0, 0])
    ax_parent = fig.add_subplot(grid[0, 1])
    ax_cutoff = fig.add_subplot(grid[0, 2])

    fig.text(
        0.065, 0.963, "Conditional He event envelope under pair-energy caps",
        fontsize=17, fontweight="bold", ha="left", va="top",
    )
    fig.text(
        0.065, 0.894,
        "Declared conditional K only. Actual physical K and the exclusive He kernel remain unresolved.",
        fontsize=10.2, ha="left", va="center", color="#704016",
        bbox={"boxstyle": "round,pad=0.42", "facecolor": "#FFF4E5", "edgecolor": "#E7CDA8", "linewidth": 0.8},
    )

    for axis in (ax_double, ax_parent):
        axis.set_xlim(-0.6, 20.7)
        axis.set_xticks((0, 1, 3, 6, 10, 20))
        axis.set_xlabel(r"Conditional pair-energy cap $K$ (eV)")
        axis.grid(axis="y", color="#DFE5EA", linewidth=0.7)

    ax_double.scatter(xs, double_fraction, s=43, c=blue, edgecolors="white", linewidths=0.6, zorder=3)
    ax_double.scatter(
        (xs[1], xs[2]), (double_fraction[1], double_fraction[2]),
        s=(48, 52), c=(gray, orange), marker="D", edgecolors="white",
        linewidths=0.6, zorder=4,
    )
    ax_double.set_ylim(-0.018, 0.535)
    ax_double.set_yticks((0, 0.1, 0.2, 0.3, 0.4, 0.5))
    ax_double.set_ylabel(r"Maximum double fraction $d_{\max}/N$")
    ax_double.set_title(f"(a) {len(rows)} saved cap samples", loc="left", pad=12)
    ax_double.text(
        0.045, 0.92, "Markers only; no interpolation.\nThe cutoff pair is resolved in (c).",
        transform=ax_double.transAxes, fontsize=8.1, ha="left", va="top",
        color="#52616D",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.92, "pad": 2},
    )

    ax_parent.vlines(xs, parent_lower, [1.0] * len(xs), color=blue, linewidth=1.7, zorder=2)
    ax_parent.scatter(xs, parent_lower, marker="_", s=55, c=blue, linewidths=1.6, zorder=3)
    ax_parent.scatter(xs, [1.0] * len(xs), marker="_", s=55, c=blue, linewidths=1.6, zorder=3)
    ax_parent.set_ylim(0.475, 1.035)
    ax_parent.set_yticks((0.5, 0.6, 0.7, 0.8, 0.9, 1.0))
    ax_parent.set_ylabel(r"Parent-event coefficient $\nu/N$")
    ax_parent.set_title("(b) Feasible parent intervals", loc="left", pad=12)
    ax_parent.text(
        0.5, -0.27,
        r"Each segment is $[N-d_{\max},\,N]/N$." "\n"
        "The native inventory gate is a separate condition.",
        transform=ax_parent.transAxes, fontsize=8.3, ha="center", va="top",
        color="#52616D",
    )

    boundary = (rows[1], rows[2])
    ghost = saved["cutoff_coefficient"]
    if ghost > 0:
        heights = [float(row["dmax"] / (ghost / 2)) for row in boundary]
        ylabel = r"Maximum double mass $d_{\max}/(w_0/2)$"
        boundary_mode = "DMAX_NORMALIZED_BY_POSITIVE_GHOST_HALF_MASS"
        ax_cutoff.text(
            0.5, -0.27, r"Vertical unit: $w_0/2$; labels give $d_{\max}/N$.",
            transform=ax_cutoff.transAxes, fontsize=8.1, ha="center", va="top",
            color="#52616D",
        )
    else:
        heights = [
            float(2 * saved["cutoff_energy_eV"] <= row["K_eV"])
            for row in boundary
        ]
        ylabel = "Ghost diagonal permitted (0 / 1)"
        boundary_mode = "ZERO_GHOST_MASS_SUPPORT_ADMISSIBILITY"
        ax_cutoff.text(
            0.5, -0.27, "Ghost mass is zero; both double maxima are zero.",
            transform=ax_cutoff.transAxes, fontsize=8.1, ha="center", va="top",
            color="#52616D",
        )
    ax_cutoff.bar((0, 1), heights, width=0.53, color=(gray, orange), zorder=3)
    ax_cutoff.scatter((0, 1), heights, s=18, c=(gray, orange), zorder=4)
    for i, (height, row) in enumerate(zip(heights, boundary)):
        ax_cutoff.text(
            i, height + 0.065,
            "dmax/N = " + scientific_text(row["dmax_over_N"]),
            ha="center", va="bottom", fontsize=8.3, color="#243746",
        )
    ax_cutoff.set_xticks((0, 1))
    ax_cutoff.set_xticklabels((
        "Decimal cap\n" + r"$K=1/5$ eV",
        "Stored-energy equality\n" + r"$K=2E_0$",
    ), fontsize=8.5)
    ax_cutoff.set_ylim(-0.035, 1.30)
    ax_cutoff.set_yticks((0, 0.5, 1.0))
    ax_cutoff.set_ylabel(ylabel, fontsize=9.1)
    ax_cutoff.set_title("(c) Exact cutoff distinction", loc="left", pad=12)
    ax_cutoff.grid(axis="y", color="#DFE5EA", linewidth=0.7)
    ax_cutoff.text(
        0.5, -0.36,
        "Exact cap gap: " + str(saved["cutoff_cap_difference_eV"]) + " eV",
        transform=ax_cutoff.transAxes, fontsize=7.8, ha="center", va="top",
        color="#52616D",
    )

    annotations = (
        "Saved exact evidence: "
        f"{saved['oracle_agreements']}/{saved['small_case_count']} oracle agreements; "
        f"{saved['native_maximum_certificates']}/{saved['native_case_count']} native maximum certificates; "
        f"max marginal residual = {saved['maximum_marginal_abs_residual']}; "
        f"max optimum-certificate gap = {saved['maximum_witness_max_dual_gap']}."
    )
    fig.text(0.065, 0.069, annotations, ha="left", va="center", fontsize=9.0, color="#243746")
    fig.text(
        0.065, 0.026,
        f"Source support: {saved['active_atom_count']} active atoms + "
        f"{saved['cutoff_ghost_count']} separate cutoff ghost "
        f"({saved['native_atom_count']} atoms total).",
        ha="left", va="center", fontsize=8.4, color="#52616D",
    )

    outputs = []
    png = outdir / "energy_sum_envelope.png"
    svg = outdir / "energy_sum_envelope.svg"
    require(not png.exists() and not svg.exists(), "CREATE_ONLY_FIGURE_PATH_EXISTS")
    with png.open("xb") as stream:
        fig.savefig(
            stream, format="png", dpi=200,
            metadata={
                "Title": "Conditional He pair-energy event envelope",
                "Description": "Saved results only; actual physical K unresolved.",
                "Software": UNIT,
            },
        )
    outputs.append(file_identity(png))
    with svg.open("x", encoding="utf-8") as stream:
        fig.savefig(
            stream, format="svg",
            metadata={
                "Title": "Conditional He pair-energy event envelope",
                "Description": "Saved results only; actual physical K unresolved.",
                "Creator": UNIT,
                "Date": None,
            },
        )
    outputs.append(file_identity(svg))
    plt.close(fig)
    return {
        "figures": outputs,
        "boundary_panel_mode": boundary_mode,
        "annotation_text": annotations,
        "raster_dimensions_px": [2720, 1160],
        "display_policy": "Nine saved cap markers only; no interpolation. Parent intervals are coefficient envelopes.",
        "visual_QA": "PENDING_ROOT_PNG_INSPECTION",
    }


def main(argv=None):
    unit_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outdir", nargs="?", type=Path, default=unit_root / "runs" / "plot_v1")
    parser.add_argument("--summary", type=Path, default=unit_root / "runs" / "primary_v1" / "SUMMARY.json")
    parser.add_argument("--independent", type=Path, default=unit_root / "runs" / "independent_v1" / "RESULT.json")
    args = parser.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    result_path = args.outdir / "RESULT.json"
    require(not result_path.exists(), "CREATE_ONLY_PLOT_RESULT_EXISTS")
    result = {
        "schema": "CR_HE_ENERGY_SUM_SAVED_PLOT_RESULT_V1",
        "unit": UNIT,
        "status": "FAIL",
        "scope": "Saved-result publication visualization; no source or scientific solver replay.",
        "inputs": {},
        "scientific_replays": 0,
        "NPZ_loads": 0,
        "production_imports": 0,
        "actual_physical_K_eV": None,
        "physical_activation": False,
        "checks": [],
    }
    phase = "read_saved_inputs"
    try:
        summary, summary_id = read_saved(args.summary)
        result["inputs"]["primary_summary"] = summary_id
        independent, independent_id = read_saved(args.independent)
        result["inputs"]["independent_result"] = independent_id
        result["checks"].append({
            "id": "actual_saved_input_pass_and_unit", "status": "PASS",
            "evidence": ["inputs.primary_summary", "inputs.independent_result"],
        })
        phase = "saved_exact_value_and_certificate_validation"
        saved = validate_saved(summary, independent)
        result["checks"].append({
            "id": "saved_exact_ratios_and_certificate_evidence", "status": "PASS",
            "oracle_agreements": saved["oracle_agreements"],
            "native_maximum_certificates": saved["native_maximum_certificates"],
            "maximum_witness_max_dual_gap": saved["maximum_witness_max_dual_gap"],
            "maximum_marginal_abs_residual": saved["maximum_marginal_abs_residual"],
        })
        result["plotted_values"] = {
            "native_cap_rows": saved["rows"],
            "cutoff_energy_eV": saved["cutoff_energy_eV"],
            "cutoff_coefficient": saved["cutoff_coefficient"],
            "cutoff_cap_difference_eV": saved["cutoff_cap_difference_eV"],
        }
        phase = "render_saved_result_figure"
        result.update(draw_figure(saved, args.outdir))
        result["checks"].append({
            "id": "png_and_svg_created_with_hashes", "status": "PASS",
            "evidence": [row["path"] for row in result["figures"]],
        })
        result["status"] = PASS
    except Exception as exc:
        result["failure"] = {
            "phase": phase, "exception": type(exc).__name__,
            "message": str(exc), "traceback": traceback.format_exc(),
        }
        result["checks"].append({"id": phase, "status": "FAIL"})
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(json_exact(result), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "unit": UNIT, "status": result["status"], "result": str(result_path),
        "visual_QA": result.get("visual_QA", "NOT_REACHED"),
    }, ensure_ascii=False))
    return 0 if result["status"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())

