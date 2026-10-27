"""224 new RHS on eight exact stored HeI chains; 24 integrated source returns."""
from __future__ import annotations

import argparse
import csv
import itertools
from pathlib import Path
import time

import numpy as np

import engine as e
import export_adapter as export
import dispatch

COMPARISON_OBSERVABLES = (
    "P_HeII_RR_active", "conditional_HeII_RR_kinetic_eV",
    "conditional_HeII_RR_photon_eV", "conditional_HeII_RR_time_s",
    "HeII_RR_photon_eV_per_selected", "HeII_RR_internal_eV_per_selected",
    "P_H1_RR_active", "P_HeI_RR_active", "P_CE_active", "mean_stop_s_active",
    "delta_CE_active", "delta_time_s_active", "delta_H1_RR_active", "delta_HeI_RR_active",
)


def arrays(path):
    with np.load(path, allow_pickle=False) as file:
        return {key: file[key] for key in file.files}


def run(unit, out, runid):
    started = time.process_time()
    actual, rows, cases, events = 0, [], [], []
    try:
        c = e.verify(unit)
        dispatch.authorize_run(unit, c, "primary", runid)
        atom = e.provider(unit)
        sources = {z: e.atoms(unit, z) for z in c["source_z"]}
        qualification = e.source_qualification(unit, c)

        def count(n):
            nonlocal actual
            actual += n
            e.need(actual <= c["planned_primary_rhs"], "PRIMARY_RHS_RESERVATION_EXCEEDED")

        for chi, radius, nominal in itertools.product(c["chi"], c["R"], c["grid_N"]):
            name = f"chi{chi:g}_R{radius}_N{nominal}"
            base = arrays(unit / "inputs/reused/pr104" / (name + ".npz"))
            old = arrays(unit / "inputs/reused/pr106" / (name + ".npz"))
            new, checks, passed = e.consume(base, old, c, atom, count)
            # Preserve every completed new array solve even if a later export fails.
            with (out / (name + ".npz")).open("xb") as file:
                np.savez_compressed(file, **new)
            for z, source in sources.items():
                row = dict(case=name, chi=chi, R=radius, N=nominal, z=z,
                           **e.source_average(base, old, new, source, z, c))
                passed &= row["ledger"]["scaled_residual"] <= c["tolerances"]["energy"]
                passed &= abs(row["source_partition_active"] - 1) <= c["tolerances"]["partition"]
                p, lo, hi = (row[key] for key in ("P_HeII_RR_active", "source_bound_lower", "source_bound_upper"))
                passed &= lo * (1 - c["tolerances"]["rare_bound"]) <= p <= hi * (1 + c["tolerances"]["rare_bound"])
                event = export.integrated_event(
                    input_id=c["input_id"], case=name, z=z,
                    count_cm3=row["expected_HeII_events_cm3"],
                    kinetic_eV_cm3=row["expected_HeII_kinetic_eV_cm3"],
                    frame=c["frame"], source_qualification=qualification,
                    nb_m3=c["native_nb_m3"])
                book = export.IntegratedBook(c["frame"], case=name, z=z)
                book.append(event)
                e.need(event["native25"] is None, "ACTUAL_EXPORT_HAS_NO_ADMITTED_NB")
                row["integrated_event_id"] = event["canonical_event_id"]
                rows.append(row)
                events.extend(book.events)
            metadata = dict(case=name, chi=chi, R=radius, N=nominal,
                            active_nodes=len(old["K_diag"]), new_RHS=28,
                            checks=checks, pass_scoped=bool(passed), global_error_bound=None)
            e.writej(out / (name + ".json"), metadata)
            cases.append(metadata)
            print(f"{name} pass_scoped={passed} new_RHS={actual}", flush=True)
            if not passed:
                e.writej(out / "PARTIAL_RESULTS.json", dict(status="FAILED_RETAINED",
                    cases=cases, source_rows=rows, integrated_events=events,
                    actual_primary_RHS=actual, process_cpu_s=time.process_time() - started))
                return 1

        comparisons = []
        index = {(row["chi"], row["R"], row["N"], row["z"]): row for row in rows}
        for chi, z in itertools.product(c["chi"], c["source_z"]):
            pairs = [("grid", index[chi, radius, 1024, z], index[chi, radius, 2048, z]) for radius in c["R"]]
            pairs.append(("boundary", index[chi, 40, 2048, z], index[chi, 80, 2048, z]))
            for kind, a, b in pairs:
                for key in COMPARISON_OBSERVABLES:
                    scale = max(abs(a[key]), abs(b[key]))
                    difference = abs(a[key] - b[key]) / scale if scale else 0.0
                    tolerance = c["tolerances"][("paired_" if key.startswith("delta_") else "") + kind]
                    comparisons.append(dict(chi=chi, z=z, kind=kind, observable=key,
                        a_case=a["case"], b_case=b["case"], relative_difference=difference,
                        tolerance=tolerance, pass_scoped=difference <= tolerance))
        e.need(actual == 224 and len(cases) == 8 and len(rows) == len(events) == 24,
               "EXPECTED_PRIMARY_COUNTS")
        e.need(len(comparisons) == 252, "EXPECTED_COMPARISON_COUNT")
        passed = all(value["pass_scoped"] for value in comparisons)
        e.writej(out / "SOURCE_WEIGHTED_RESULTS.json", dict(
            schema="CR_HEIII_SOURCE_WEIGHTED_V1", rows=rows, comparisons=comparisons,
            paired_effect_uncertainty="Stored PR106 HeI uncertainty is inherited; four stable responses use those columns. Direct subtraction is diagnostic.",
            source_projection_reused=True, global_error_bound=None, global_completion_percent=None))
        e.writej(out / "INTEGRATED_EVENT_EXPORTS.json", dict(
            schema="CR_HEIII_INTEGRATED_EXPORTS_V1", events=events,
            scenarios="24 case/source alternatives; not an additive population or time history",
            source_qualification=qualification, actual_native_nb_m3=None,
            energy_rtol=export.ENERGY_RTOL, event_rate_m3_s=None, exposure_s=None,
            instantaneous_rhs=None, physical_heating_J_m3=None,
            irreversible_assimilation=False, full_feedback=False))
        fields = ["case", "chi", "R", "N", "z", *COMPARISON_OBSERVABLES,
                  "expected_HeII_events_cm3", "expected_HeII_kinetic_eV_cm3",
                  "source_bound_lower", "source_bound_upper"]
        with (out / "SOURCE_WEIGHTED_ROWS.csv").open("x", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        result = dict(schema="CR_HEIII_RR_PRIMARY_V1", status="PASS" if passed else "FAILED_RETAINED",
            input_id=c["input_id"], run_id=runid, case_count=len(cases), planned_primary_RHS=224,
            actual_primary_RHS=actual, physical_RHS=144, conditional_RHS=40,
            physical_conditional_RHS=184, response_diagnostic_RHS=40,
            source_rows=len(rows), integrated_exports=len(events), comparisons=len(comparisons),
            comparison_failures=[value for value in comparisons if not value["pass_scoped"]],
            old_primary_replay=0, old_generator_calls=0, old_source_projection_calls=0,
            source_quadrature=0, thermal_rate_quadrature=0, new_ODE=0,
            process_cpu_s=time.process_time() - started, global_error_bound=None,
            global_completion_percent=None, EXECUTION="COMPLETED",
            PUBLICATION="ROOT_OWNED", BACKUP="ROOT_PENDING", DAG="N5_PARTIAL_OPEN_N6_N7_PREDECESSOR_GATED")
        e.writej(out / "RESULT.json", result)
        return 0 if passed else 1
    except Exception as error:
        e.writej(out / "FAILURE.json", dict(status="FAILED_RETAINED", type=type(error).__name__,
            message=str(error), actual_primary_RHS=actual, completed_cases=len(cases),
            completed_source_rows=len(rows), process_cpu_s=time.process_time() - started))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit.resolve(), args.output.resolve(), args.run_id))
