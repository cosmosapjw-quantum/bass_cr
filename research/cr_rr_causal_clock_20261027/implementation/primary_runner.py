"""Execute only the frozen new finite-age HeIII pulse response."""
import json
import sys
import time
import traceback
from pathlib import Path

from export_adapter import export_event, PulseReturnBook
from runner_common import Context, args, write_new, require, tighten, difference, photon, clock_metadata


def execute(ctx):
    result = {"schema": "CR_CLOCK_PRIMARY_RESULT_V1", "run_id": ctx.args.run_id,
              "status": "RUNNING", "cases": [], "checks": [], "failures": [],
              "old_science_replay": 0, "new_provider_evaluations": 0,
              "new_all_time_solves": 0, "actual_two_rhs_solve_steps": 0,
              "actual_factorizations": 0, "actual_source_contractions": 0,
              "source_history": None, "exposure_s": None, "actual_nb_m3": None,
              "global_physical_error_bound": None, "physical_heating_complete": None,
              "central": {"completed": 27, "total": 88, "count_effect": 0}}
    acceptance = ctx.contract["acceptance"]
    def check(name, value, limit):
        ok = value <= limit
        result["checks"].append({"name": name, "value": value, "limit": limit, "pass": ok})
        if not ok:
            result["failures"].append(name)
    for case in ctx.manifest["cases"]:
        ctx.guard_cpu()
        p, identities = ctx.load_case(case)
        raw = [ctx.engine.horizon(p, 0., 64, .5)]
        max_arithmetic = 0.
        minimum_nominal = float("inf")
        for T in ctx.contract["observation_horizons_s"][1:]:
            for m, delta in case["levels"]:
                ctx.guard_cpu()
                h = ctx.engine.horizon(p, float(T), m, delta)
                raw.append(h)
                for side in ("minus", "plus"):
                    clock = h["clocks"][side]
                    result["actual_two_rhs_solve_steps"] += m
                    result["actual_factorizations"] += 1
                    result["actual_source_contractions"] += 6
                    minimum_nominal = min(minimum_nominal, *clock["arithmetic_certificate"]["minimum_nominal_solution"])
                    for s, row in enumerate(clock["source_rows"]):
                        for j, label in enumerate(("count", "kinetic")):
                            if p.p_upper[s, j] > 0:
                                max_arithmetic = max(max_arithmetic, row[label]["A_radius"]/float(p.p_upper[s,j]))
        source_rows, exports = [], []
        widths = []
        for s, sid in enumerate(p.source_ids):
            times = tighten(raw, s, ctx.contract["observation_horizons_s"])
            ncap = [float(p.p_lower[s,0]), float(p.p_upper[s,0])]
            ecap = [float(p.p_lower[s,1]), float(p.p_upper[s,1])]
            bins = []
            book = PulseReturnBook("bath_frame_rest_target", case_id=case["case_id"], source_id=sid)
            for first, second in zip(times, times[1:]):
                count = difference(second["count_cm3"], first["count_cm3"], ncap)
                energy = difference(second["kinetic_eV_cm3"], first["kinetic_eV_cm3"], ecap)
                event = export_event(case_id=case["case_id"], source_id=sid,
                    source_identity=identities[s], time_start_s=float(first["T_s"]),
                    time_end_s=float(second["T_s"]), count_cm3=count, kinetic_eV_cm3=energy,
                    frame="bath_frame_rest_target", clock_metadata=clock_metadata(
                        [h for h in raw if h["horizon_s"] in (first["T_s"],second["T_s"])]), nb_m3=None)
                book.append(event)
                exports.append(event)
                bins.append({"time_start_s": first["T_s"], "time_end_s": second["T_s"],
                             "count_cm3": count, "kinetic_eV_cm3": energy,
                             "photon_eV_cm3": photon(count, energy), "canonical_event_id": event["canonical_event_id"]})
            for row in times:
                widths += [(row["count_cm3"][1]-row["count_cm3"][0])/ncap[1],
                           (row["kinetic_eV_cm3"][1]-row["kinetic_eV_cm3"][0])/ecap[1]]
            source_rows.append({"source_id": sid, "source_identity": identities[s],
                "all_time_count_cm3": ncap, "all_time_kinetic_eV_cm3": ecap,
                "all_time_photon_eV_cm3": photon(ncap,ecap), "horizons": times, "bins": bins})
        check(case["case_id"]+":clock_width", max(widths), acceptance["finest_clock_width_over_alltime_upper_max"])
        check(case["case_id"]+":arithmetic_radius", max_arithmetic, acceptance["arithmetic_scalar_radius_over_alltime_upper_max"])
        check(case["case_id"]+":negative_nominal_magnitude", -minimum_nominal, 0.)
        raw_name = case["case_id"]+"_RAW.json"
        export_name = case["case_id"]+"_BIN_EXPORTS.json"
        write_new(ctx.output/raw_name, {"case":case,"raw_horizons":raw,"witness_beta_lower":p.beta_lower})
        write_new(ctx.output/export_name, {"schema":"CR_CLOCK_DISJOINT_BIN_BOOK_V1","case":case["case_id"],"exports":exports,
                   "cumulative_views_not_added_to_book":True,"actual_nb_m3":None})
        result["cases"].append({"case_id":case["case_id"],"chi":case["chi"],"R":case["R"],"N":case["N"],
            "actual_active_N":p.n,"source_rows":source_rows,"witness_beta_lower":p.beta_lower,
            "all_time_arithmetic_radius":p.p_radius.tolist(),"all_time_nominal":p.p_nominal.tolist(),
            "raw_horizon_file":raw_name,"bin_export_file":export_name,"max_clock_width_over_alltime":max(widths),
            "max_arithmetic_radius_over_alltime":max_arithmetic,"minimum_nominal_solution":minimum_nominal})
        write_new(ctx.output/(case["case_id"]+"_SUMMARY.json"),result["cases"][-1])
    # These finite discretization comparisons are diagnostics, not a continuum certificate.
    for chi in (1.5,3):
        fine=next(c for c in result["cases"] if c["chi"]==chi and c["R"]==80 and c["N"]==2048)
        for kind, other in [("grid",next(c for c in result["cases"] if c["chi"]==chi and c["R"]==80 and c["N"]==1024)),
                            ("domain",next(c for c in result["cases"] if c["chi"]==chi and c["R"]==40 and c["N"]==2048))]:
            value=0.
            for fs,os in zip(fine["source_rows"],other["source_rows"]):
                for ft,ot in zip(fs["horizons"],os["horizons"]):
                    for field,cap in [("count_cm3","all_time_count_cm3"),("kinetic_eV_cm3","all_time_kinetic_eV_cm3")]:
                        value=max(value,*(abs(a-b)/fs[cap][1] for a,b in zip(ft[field],ot[field])))
            limit=acceptance["grid_endpoint_difference_over_finest_alltime_upper_max" if kind=="grid" else "domain_endpoint_difference_over_R80_alltime_upper_max"]
            check("chi"+str(chi)+":"+kind+"_endpoint",value,limit)
    require(result["actual_two_rhs_solve_steps"]==81408 and result["actual_factorizations"]==120,"PRIMARY_FOOTPRINT")
    result["actual_RHS_solved"]=2*result["actual_two_rhs_solve_steps"]
    result["status"]="COMPLETED"
    result["decision"]="PASS_SCOPED_FINITE_K_PULSE" if not result["failures"] else "PARTIAL_SCOPED_WITH_RETAINED_FAILED_GATES"
    result["worker_cpu_before_serialization_s"]=time.process_time()
    write_new(ctx.output/"RESULT.json",result)
    print(json.dumps({"decision":result["decision"],"cases":len(result["cases"]),"RHS":result["actual_RHS_solved"],"failed_gates":result["failures"],"cpu_s":time.process_time()}))
    return 0 if not result["failures"] else 1


def main():
    a=args()
    try:
        ctx=Context(a)
        return execute(ctx)
    except Exception as e:
        out=a.output/"payload";out.mkdir(parents=True,exist_ok=True)
        write_new(out/"FAILURE.json",{"error":type(e).__name__,"message":str(e),"traceback":traceback.format_exc(),"worker_cpu_s":time.process_time(),"science_outputs_retained":True})
        print(str(e),file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
