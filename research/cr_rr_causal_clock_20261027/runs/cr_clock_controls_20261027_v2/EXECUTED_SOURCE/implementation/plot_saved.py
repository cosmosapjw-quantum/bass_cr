"""Plot pinned saved clock intervals only; no solver/native/provider imports.

Numerical RESULT.json remains authoritative. Float ratios and midpoints below are
display operations, not new certified scientific outputs.
"""
from __future__ import annotations

import time
_STARTED_CPU = time.process_time()
_STARTED_WALL = time.monotonic()

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import sys
import tempfile


PRIMARY_DEFAULT = "runs/cr_clock_primary_20261027_v1/payload/RESULT.json"
SOURCE_IDS = ("2.316", "2.479", "2.649")
FIGURE_STEM = "FINITE_AGE_RR_FRACTIONS"
DPI = 130
I_EV_DISPLAY = 54.42


class PlotError(RuntimeError):
    pass


def need(ok, message):
    if not ok:
        raise PlotError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def real(value, name, nonnegative=False):
    need(not isinstance(value, bool) and isinstance(value, (int, float)),
         name + ": EXPLICIT_REAL_REQUIRED")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        raise PlotError(name + ": FINITE_REAL_REQUIRED") from None
    need(math.isfinite(result), name + ": FINITE_REAL_REQUIRED")
    if isinstance(value, int):
        need(int(result) == value, name + ": INTEGER_NOT_EXACT_BINARY64")
    need(not nonnegative or result >= 0, name + ": NONNEGATIVE_REQUIRED")
    return result


def interval(value, name):
    need(isinstance(value, (list, tuple)) and len(value) == 2,
         name + ": TWO_ENDPOINTS_REQUIRED")
    lo, hi = (real(x, name, nonnegative=True) for x in value)
    need(lo <= hi, name + ": INTERVAL_ORDER")
    return lo, hi


def write_json_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


class CpuGuard:
    def __init__(self):
        text = os.environ.get("CR_CLOCK_WORKER_CPU_CAP_S", "5")
        try:
            requested = float(text)
        except (ValueError, OverflowError):
            raise PlotError("INVALID_CPU_CAP_ENVIRONMENT") from None
        need(math.isfinite(requested) and requested > 0, "INVALID_CPU_CAP_ENVIRONMENT")
        self.cap = min(5.0, requested)
        self.reserve = min(0.1, 0.1*self.cap)
        self.stop = self.cap-self.reserve
        self.previous = None
        self.armed = False

    def _expired(self, signum, frame):
        signal.setitimer(signal.ITIMER_PROF, 0)
        raise PlotError("PLOT_COOPERATIVE_CPU_CAP_REACHED")

    def arm(self):
        need(signal.getitimer(signal.ITIMER_PROF) == (0.0, 0.0),
             "EXISTING_CPU_TIMER_MUST_NOT_BE_OVERWRITTEN")
        remaining = self.stop-(time.process_time()-_STARTED_CPU)
        need(remaining > 0, "PLOT_CPU_CAP_EXHAUSTED_BEFORE_IMPORTS")
        self.previous = signal.getsignal(signal.SIGPROF)
        signal.signal(signal.SIGPROF, self._expired)
        signal.setitimer(signal.ITIMER_PROF, remaining)
        self.armed = True

    def check(self):
        need(time.process_time()-_STARTED_CPU < self.stop,
             "PLOT_COOPERATIVE_CPU_CAP_REACHED")

    def close(self):
        if self.armed:
            signal.setitimer(signal.ITIMER_PROF, 0)
            signal.signal(signal.SIGPROF, self.previous)
            self.armed = False


def pin_records(document):
    """Accept files-list, files-map, or a direct path-to-hash map."""
    need(isinstance(document, dict), "PINS_OBJECT_REQUIRED")
    collection = document.get("files", document)
    if isinstance(collection, list):
        for row in collection:
            need(isinstance(row, dict), "PIN_RECORD_OBJECT_REQUIRED")
            yield row
    elif isinstance(collection, dict):
        for path, value in collection.items():
            if isinstance(value, str):
                yield {"path": path, "sha256": value}
            elif isinstance(value, dict):
                row = dict(value)
                row.setdefault("path", path)
                yield row
    else:
        raise PlotError("UNSUPPORTED_PINS_COLLECTION")


def checked_source(unit, config, pins):
    declared = config.get("primary_result_path", PRIMARY_DEFAULT)
    need(isinstance(declared, str) and declared.strip() == declared and declared,
         "PRIMARY_RESULT_PATH_REQUIRED")
    path = Path(declared)
    path = path.resolve() if path.is_absolute() else (unit/path).resolve()
    try:
        relative = path.relative_to(unit).as_posix()
    except ValueError:
        raise PlotError("PRIMARY_RESULT_MUST_BE_INSIDE_UNIT") from None
    matches = []
    for row in pin_records(pins):
        named = row.get("path")
        if not isinstance(named, str):
            continue
        candidate = Path(named)
        candidate = candidate.resolve() if candidate.is_absolute() else (unit/candidate).resolve()
        if candidate == path:
            matches.append(row)
    need(len(matches) == 1, "EXACTLY_ONE_PRIMARY_RESULT_PIN_REQUIRED")
    pin = matches[0]
    expected = pin.get("sha256")
    need(isinstance(expected, str) and len(expected) == 64 and
         all(c in "0123456789abcdef" for c in expected), "PRIMARY_SHA256_REQUIRED")
    raw = path.read_bytes()
    observed = sha256(raw)
    need(observed == expected, "PRIMARY_RESULT_SHA256_MISMATCH")
    if "bytes" in pin:
        need(type(pin["bytes"]) is int and pin["bytes"] == len(raw),
             "PRIMARY_RESULT_BYTE_COUNT_MISMATCH")
    result = json.loads(raw)
    need(isinstance(result, dict), "PRIMARY_RESULT_OBJECT_REQUIRED")
    return result, {"path": relative, "sha256": observed, "bytes": len(raw),
                    "pin_matched": True}


def selected_curves(result):
    """Read only saved finest-case bounds; create visual float ratios."""
    cases = result.get("cases")
    need(isinstance(cases, list), "RESULT_CASES_REQUIRED")
    chosen = {}
    for case in cases:
        need(isinstance(case, dict), "CASE_OBJECT_REQUIRED")
        if case.get("R") == 80 and case.get("N") == 2048:
            chi = real(case.get("chi"), "case chi")
            if chi in (1.5, 3.0):
                need(chi not in chosen, "DUPLICATE_FINEST_CASE")
                chosen[chi] = case
    need(set(chosen) == {1.5, 3.0}, "TWO_FINEST_CASES_REQUIRED")
    curves, zero_rows, identities = {}, [], []
    time_grid = None
    for chi in (1.5, 3.0):
        case = chosen[chi]
        case_id = case.get("case_id")
        need(isinstance(case_id, str) and bool(case_id), "CASE_ID_REQUIRED")
        rows = case.get("source_rows")
        need(isinstance(rows, list), "SOURCE_ROWS_REQUIRED")
        keyed = {}
        for row in rows:
            need(isinstance(row, dict), "SOURCE_ROW_OBJECT_REQUIRED")
            sid = row.get("source_id")
            need(isinstance(sid, str) and sid not in keyed, "UNIQUE_SOURCE_ID_REQUIRED")
            keyed[sid] = row
        need(set(keyed) == set(SOURCE_IDS), "THREE_SAVED_SOURCE_ALTERNATIVES_REQUIRED")
        identities.append({"case_id":case_id,"chi":chi,"R":80,"N":2048})
        for sid in SOURCE_IDS:
            row = keyed[sid]
            n0 = interval(row.get("all_time_count_cm3"), "all-time count")
            e0 = interval(row.get("all_time_kinetic_eV_cm3"), "all-time kinetic")
            p0 = (e0[0]+I_EV_DISPLAY*n0[0], e0[1]+I_EV_DISPLAY*n0[1])
            need(n0[0] > 0 and p0[0] > 0 and all(map(math.isfinite,p0)),
                 "POSITIVE_FINITE_ALL_TIME_LOWER_REQUIRED_FOR_DISPLAY_RATIO")
            horizons = row.get("horizons")
            need(isinstance(horizons,list), "SAVED_HORIZONS_REQUIRED")
            points, seen, zero_seen = [], set(), False
            for h in horizons:
                need(isinstance(h,dict), "HORIZON_OBJECT_REQUIRED")
                T = real(h.get("T_s"), "proper-time horizon", nonnegative=True)
                need(T not in seen, "DUPLICATE_SOURCE_HORIZON")
                seen.add(T)
                ni = interval(h.get("count_cm3"), "horizon count")
                ei = interval(h.get("kinetic_eV_cm3"), "horizon kinetic")
                pi = interval(h.get("photon_eV_cm3"), "horizon photon")
                if T == 0:
                    need(ni == (0.0,0.0) and ei == (0.0,0.0) and pi == (0.0,0.0),
                         "ZERO_HORIZON_RR_ENDPOINT_REQUIRED")
                    zero_seen = True
                    zero_rows.append({"case_id":case_id,"source_id":sid,"T_s":0.0,
                        "count_cm3":list(ni),"kinetic_eV_cm3":list(ei),
                        "photon_eV_cm3":list(pi),"omitted_from_log_plot":True})
                    continue
                ratios = ((ni[0]/n0[1],ni[1]/n0[0]),
                          (pi[0]/p0[1],pi[1]/p0[0]))
                need(all(math.isfinite(x) and x >= 0 for pair in ratios for x in pair),
                     "NONFINITE_VISUAL_RATIO")
                need(all(lo <= hi for lo,hi in ratios), "VISUAL_RATIO_ORDER")
                points.append((T,ratios))
            need(zero_seen and len(points) >= 2, "ZERO_AND_POSITIVE_HORIZONS_REQUIRED")
            points.sort(key=lambda p:p[0])
            current_grid = tuple(p[0] for p in points)
            if time_grid is None:
                time_grid = current_grid
            need(current_grid == time_grid, "COMMON_SAVED_HORIZON_GRID_REQUIRED")
            curves[(chi,sid)] = points
    return curves, zero_rows, identities, list(time_grid)


def render(curves, output, guard):
    # Import cost is included in the already armed CPU guard.
    with tempfile.TemporaryDirectory(prefix="cr-clock-mpl-") as cache:
        old_cache = os.environ.get("MPLCONFIGDIR")
        os.environ["MPLCONFIGDIR"] = cache
        try:
            import matplotlib
            matplotlib.use("Agg", force=True)
            import matplotlib.pyplot as plt
            import numpy as np
            import PIL
            guard.check()
            plt.rcParams.update({
                "font.family":"DejaVu Sans","font.size":9,
                "axes.titlesize":11,"axes.labelsize":10,
                "legend.fontsize":9,"pdf.fonttype":42,
            })
            fig, axes = plt.subplots(2,2,figsize=(11.5,7.2),sharex=True,sharey="row")
            colors = ("#1f77b4","#ff7f0e","#2ca02c")
            styles = ("-","--",":")
            markers = ("o","s","^")
            max_upper = [1.0,1.0]
            handles = []
            for col,chi in enumerate((1.5,3.0)):
                axes[0,col].set_title(f"chi = {chi:g}")
                for si,sid in enumerate(SOURCE_IDS):
                    points = curves[(chi,sid)]
                    x = np.asarray([p[0] for p in points],dtype=float)
                    for row in range(2):
                        lo = np.asarray([p[1][row][0] for p in points],dtype=float)
                        hi = np.asarray([p[1][row][1] for p in points],dtype=float)
                        midpoint = lo+(hi-lo)*0.5  # display only, not a new estimate
                        ax = axes[row,col]
                        ax.fill_between(x,lo,hi,color=colors[si],alpha=0.16,linewidth=0)
                        line, = ax.plot(x,midpoint,color=colors[si],linestyle=styles[si],
                            marker=markers[si],markersize=3.2,linewidth=1.45,
                            label=f"Saved source z = {sid}")
                        if row == 0 and col == 0:
                            handles.append(line)
                        max_upper[row] = max(max_upper[row],float(np.max(hi)))
                for row in range(2):
                    axes[row,col].set_xscale("log")
                    axes[row,col].grid(which="major",alpha=0.22,linewidth=0.55)
                    axes[row,col].axhline(1.0,color="0.45",linewidth=0.65,linestyle=":")
                    axes[row,col].set_xlim(points[0][0],points[-1][0])
                    if row == 1:
                        axes[row,col].set_xlabel("Proper time after declared pulse (s)")
            axes[0,0].set_ylabel("RR count fraction")
            axes[1,0].set_ylabel("Retained-photon energy fraction")
            for row in range(2):
                top = max(1.03,1.02*max_upper[row])
                for col in range(2):
                    axes[row,col].set_ylim(0,top)
            fig.suptitle("Conditional He III ground-RR pulse response\n"
                         "Frozen 10,000 K bath; R = 80; nominal N = 2048",
                         fontsize=12,y=0.985)
            fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(0.5,0.90),
                       ncol=3,frameon=False)
            fig.text(0.5,0.055,
                "Bands: transformed saved finite-K intervals. Lines: interval midpoints (display only).\n"
                "Each row is normalized by its saved all-time count or retained-photon energy. "
                "Zero-time endpoints are omitted from log axes.\n"
                "The pinned RESULT.json remains the authoritative numerical source.",
                ha="center",va="center",fontsize=8)
            fig.tight_layout(rect=(0.015,0.115,0.995,0.855))
            guard.check()
            png = output/(FIGURE_STEM+".png")
            pdf = output/(FIGURE_STEM+".pdf")
            try:
                with png.open("xb") as stream:
                    fig.savefig(stream,format="png",dpi=DPI,
                                metadata={"Software":"CR clock saved-results plot"})
                guard.check()
                with pdf.open("xb") as stream:
                    fig.savefig(stream,format="pdf",dpi=DPI,
                        metadata={"Creator":"CR clock saved-results plot",
                                  "CreationDate":None,"ModDate":None})
                guard.check()
            finally:
                plt.close(fig)
            versions = {"python":sys.version,"matplotlib":matplotlib.__version__,
                        "numpy":np.__version__,"pillow":PIL.__version__,
                        "backend":matplotlib.get_backend(),"platform":platform.platform()}
        finally:
            if old_cache is None:
                os.environ.pop("MPLCONFIGDIR",None)
            else:
                os.environ["MPLCONFIGDIR"] = old_cache
    guard.check()
    figures = []
    for path in (png,pdf):
        raw = path.read_bytes()
        figures.append({"file":path.name,"bytes":len(raw),"sha256":sha256(raw)})
    return figures,versions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--run-id",required=True)
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--pins",type=Path,required=True)
    args = parser.parse_args()
    unit, output = args.unit.resolve(),args.output.resolve()
    need(bool(args.run_id.strip()) and args.run_id == args.run_id.strip(),
         "RUN_ID_REQUIRED")
    output.mkdir(parents=True,exist_ok=True)
    receipt_path = output/"PLOT_RECEIPT.json"
    need(not receipt_path.exists() and
         not (output/(FIGURE_STEM+".png")).exists() and
         not (output/(FIGURE_STEM+".pdf")).exists(), "IMMUTABLE_PLOT_OUTPUT_EXISTS")
    guard = CpuGuard()
    receipt = {"schema":"CR_CLOCK_SAVED_PLOT_RECEIPT_V1","run_id":args.run_id,
        "status":"STARTED","new_solver_calls":0,"source_provider_calls":0,
        "new_ODE":0,"recomputed_scientific_error_bounds":False,
        "numerical_source_authority":"pinned saved RESULT.json",
        "display_midpoint_is_scientific_estimator":False,
        "display_ratio_arithmetic":"ordinary float for visualization only",
        "CPU_cap_s":guard.cap,"cooperative_CPU_stop_s":guard.stop,
        "receipt_CPU_reserve_s":guard.reserve}
    try:
        guard.arm()
        config_raw, pins_raw = args.config.read_bytes(),args.pins.read_bytes()
        config,pins = json.loads(config_raw),json.loads(pins_raw)
        need(isinstance(config,dict), "CONFIG_OBJECT_REQUIRED")
        result,source = checked_source(unit,config,pins)
        receipt.update({"source":source,"config_sha256":sha256(config_raw),
                        "pins_sha256":sha256(pins_raw),
                        "executed_script_sha256":sha256(Path(__file__).read_bytes())})
        curves,zeros,cases,times = selected_curves(result)
        figures,versions = render(curves,output,guard)
        receipt.update({"status":"PLOT_CREATED_FROM_PINNED_SOURCE",
            "figures":figures,"actual_versions":versions,"selected_cases":cases,
            "source_ids":list(SOURCE_IDS),"positive_horizons_s":times,
            "zero_horizon_records":zeros,"zero_horizons_omitted_from_log_axes":True,
            "layout":"2x2: rows count/photon fraction, columns chi1.5/3",
            "interval_ratio":"[numerator_lower/denominator_upper, numerator_upper/denominator_lower]",
            "all_time_photon_display_formula":"kinetic + 54.42 * count",
            "requested_PNG_dpi":DPI,"requested_figure_inches":[11.5,7.2],
            "physical_heating_complete":None,"new_physical_source_history":None})
        guard.check()
    except Exception as exc:
        receipt.update({"status":"FAILED","error_type":type(exc).__name__,"error":str(exc)})
        receipt["process_cpu_s_before_receipt_write"] = time.process_time()-_STARTED_CPU
        receipt["wall_s_before_receipt_write"] = time.monotonic()-_STARTED_WALL
        if not receipt_path.exists():
            write_json_new(receipt_path,receipt)
        raise
    else:
        receipt["process_cpu_s_before_receipt_write"] = time.process_time()-_STARTED_CPU
        receipt["wall_s_before_receipt_write"] = time.monotonic()-_STARTED_WALL
        receipt["external_worker_lease_receipt_owns_full_process_CPU"] = True
        write_json_new(receipt_path,receipt)
        print("PLOT_CREATED_FROM_PINNED_SOURCE",receipt_path)
        return 0
    finally:
        guard.close()


if __name__ == "__main__":
    raise SystemExit(main())

