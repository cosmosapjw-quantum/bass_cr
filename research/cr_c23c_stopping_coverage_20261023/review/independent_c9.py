"""One independent Decimal80 C9 pass over the saved C23C binding campaign.

Numerical oracle: CSV decimal atoms, direct source/stoichiometric expressions,
direct prefix candidate enumeration, and independently classified six cross cells.
The oracle imports no production numerical function. Production is imported only
after the audit, for focused API/actual-source threshold-equality witnesses.
Run exclusively through implementation/dispatch.py under a fresh lease.
"""
from __future__ import annotations
import argparse
import copy
import csv
from decimal import Decimal as D, localcontext
from fractions import Fraction
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "runs/c23c_source_cutoff_binding_20261023_v1"
EXPECTED_ATOM_SHA = "f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3"
OLD_IMPLEMENTATION_SHA = "1e1771a0eca01cfdbef109c01774937bd5a23a638ce6f87f3a3d8fa99282e7c1"
OLD_VENDOR_SHA = "427ccb65c8f11d5cbe2035415f2f45abeaca6b23aa818027a09152b2cbfe67f0"
RELATIVE_ACCEPTANCE = D("1e-40")
POP = ("HI", "HII", "HeI", "HeII", "HeIII")
ABSORB = ("HI", "HeI", "HeII")
THRESHOLD = {"HI": D("13.60"), "HeI": D("24.59"), "HeII": D("54.42")}
REQUIRED = {"redshift", "normalization", "proper_duration_s", "initial_temperature_K",
            "chi", "frame", "rate_unit", "initial_electron_model"}


def write(path, data):
    with path.open("x") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def dec(value):
    if isinstance(value, D):
        return value
    if isinstance(value, bool):
        raise TypeError("Boolean is not a numerical value")
    s = str(value)
    if "/" in s:
        a, b = s.split("/")
        return D(a) / D(b)
    return D(s)


def digest(path):
    b = path.read_bytes()
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def direct_counts(spec):
    v = dec(spec["proper_volume_cm3"])
    if spec["mode"] == "density":
        return {p: dec(spec["values_cm3"][p]) * v for p in POP}
    if spec["mode"] == "abundance":
        nref = dec(spec["reference_density_cm3"])
        return {p: dec(spec["values_per_reference"][p]) * nref * v for p in POP}
    raise AssertionError("unexpected admitted normalization")


def main(run, cpu):
    os.sched_setaffinity(0, {cpu})
    if cpu == 55:
        raise RuntimeError("CPU55 is protected")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(key) != "1":
            raise RuntimeError("native thread contract missing")
    t0, c0 = time.perf_counter(), time.process_time()
    paths = [
        ROOT / "inputs/photoelectron_atoms.csv", ROOT / "CONTRACT.json",
        ROOT / "implementation/source_cutoff_binding.py",
        ROOT / "implementation/history/v1/source_cutoff_binding.py",
        ROOT / "implementation/vendor/thermal_cutoff_solver.py",
        PRIOR / "CASES.json", PRIOR / "CUTS.csv", PRIOR / "TARGETED_CHECKS.json",
        PRIOR / "SOURCE_IDENTITY.json", PRIOR / "SUMMARY.json",
    ]
    pins = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    assert pins["inputs/photoelectron_atoms.csv"]["sha256"] == EXPECTED_ATOM_SHA
    assert pins["implementation/history/v1/source_cutoff_binding.py"]["sha256"] == OLD_IMPLEMENTATION_SHA
    assert pins["implementation/vendor/thermal_cutoff_solver.py"]["sha256"] == OLD_VENDOR_SHA
    prior_pins = json.loads((PRIOR / "SOURCE_IDENTITY.json").read_text())["files"]
    for name in ("inputs/photoelectron_atoms.csv", "CONTRACT.json",
                 "implementation/vendor/thermal_cutoff_solver.py"):
        assert pins[name] == prior_pins[name]
    assert prior_pins["implementation/source_cutoff_binding.py"] == pins[
        "implementation/history/v1/source_cutoff_binding.py"]
    raw = (ROOT / "inputs/photoelectron_atoms.csv").read_bytes()
    input_rows = list(csv.DictReader(io.StringIO(raw.decode(), newline="")))
    assert len(input_rows) == 32592
    cases = json.loads((PRIOR / "CASES.json").read_text())
    cuts = {r["case"]: r for r in csv.DictReader((PRIOR / "CUTS.csv").open())}
    assert len(cases) == len(cuts) == 18
    summaries, comparisons = [], []
    with localcontext() as ctx:
        ctx.prec = 80
        kb = D("1.380649e-23") / D("1.602176634e-19")
        cv = D("1.5") * kb
        source = {}
        for r in input_rows:
            source.setdefault(dec(r["redshift"]), []).append(
                (r["channel"], dec(r["kinetic_eV"]), dec(r["number_weight_per_target_s"])))

        def check(label, actual, expected):
            a, e = dec(actual), dec(expected)
            difference = abs(a - e)
            scale = max(abs(a), abs(e))
            relative = difference / scale if scale else D(0)
            assert relative <= RELATIVE_ACCEPTANCE, (label, str(a), str(e), str(relative))
            comparisons.append({"field": label, "relative": str(relative)})
            return relative

        for row in cases:
            req, state = row["request"], row["state"]
            assert set(req) == REQUIRED
            assert req["frame"] == "bath_frame_rest_target"
            assert req["rate_unit"] == "per_absorbing_target_per_proper_second"
            assert req["initial_electron_model"] == "charge_neutral_thermal_no_resolved_nonthermal"
            z, dt = dec(req["redshift"]), dec(req["proper_duration_s"])
            temp0, chi = dec(req["initial_temperature_K"]), dec(req["chi"])
            p = direct_counts(req["normalization"])
            nn = sum(p.values(), D(0))
            ne = p["HII"] + p["HeII"] + 2 * p["HeIII"]
            nb = nn + ne
            ub = cv * temp0 * nb
            rate = {k: sum((w for ch, _, w in source[z] if ch == k), D(0)) for k in ABSORB}
            exposure = {k: dt * rate[k] for k in ABSORB}
            extent = {k: p[k] * exposure[k] for k in ABSORB}
            after = {"HI": p["HI"] - extent["HI"], "HII": p["HII"] + extent["HI"],
                     "HeI": p["HeI"] - extent["HeI"],
                     "HeII": p["HeII"] + extent["HeI"] - extent["HeII"],
                     "HeIII": p["HeIII"] + extent["HeII"]}
            assert min(after.values()) >= 0
            assert all(exposure[k] <= 1 for k in ABSORB if p[k] > 0)
            packets = [(k, w * p[ch] * dt) for ch, k, w in source[z]]
            all_n = sum((n for _, n in packets), D(0))
            all_e = sum((k * n for k, n in packets), D(0))
            bind_e = sum((THRESHOLD[k] * extent[k] for k in ABSORB), D(0))
            # Direct grouping and prefix candidate enumeration, without vendor calls.
            grouped = {}
            for k, n in packets:
                if n:
                    grouped[k] = grouped.get(k, D(0)) + n
            groups = sorted(grouped.items())
            ns, es = nb, ub
            consistent = []
            independent_states = {}
            for j in range(len(groups) + 1):
                if j:
                    k, n = groups[j - 1]
                    ns, es = ns + n, es + k * n
                t = es / (cv * ns)
                cut = chi * kb * t
                lower = j == 0 or groups[j - 1][0] <= cut
                upper = j == len(groups) or cut < groups[j][0]
                if lower and upper:
                    consistent.append(j)
                    independent_states[j] = (t, cut, ns, es)
            assert consistent, row["case"]
            j = state["thermal_groups"]
            assert j == consistent[0], (row["case"], "forward policy", j, consistent[:10])
            assert j == row["branch_crossings"]
            t, cut, nt, et = independent_states[j]
            # Independent ownership classification uses saved cutoff; ledger and
            # agreement with independently enumerated cutoff are checked below.
            stored_cut = dec(state["cutoff"])
            low_n = sum((n for k, n in packets if k <= stored_cut), D(0))
            low_e = sum((k*n for k, n in packets if k <= stored_cut), D(0))
            cross = {a+"_"+b: [D(0), D(0)] for a in ("cutoff_thermal", "cutoff_active")
                     for b in ("below_fs", "inside_fs", "above_fs")}
            for k, n in packets:
                owner = "cutoff_thermal" if k <= stored_cut else "cutoff_active"
                band = "below_fs" if k < 10 else "above_fs" if k > D("9937.21") else "inside_fs"
                cross[owner+"_"+band][0] += n
                cross[owner+"_"+band][1] += k*n
            expected = {
                "common_count": nb + all_n, "common_energy_eV": ub + all_e,
                "base_count": nb, "base_energy_eV": ub,
                "nucleus_count": nn, "initial_free_electron_count": ne,
                "new_free_electron_count": all_n, "all_free_electron_count": ne + all_n,
                "cutoff_thermal_electron_count": ne + low_n,
                "cutoff_active_electron_count": all_n - low_n,
                "primary_kinetic_eV": all_e, "binding_supply_eV": bind_e,
                "absorbed_photon_eV": all_e + bind_e,
                "cutoff_classified_source_count": low_n,
                "cutoff_classified_source_eV": low_e,
                "partition_delta_temperature_K": (low_e - cv * temp0 * low_n) / (cv * (nb+low_n)),
            }
            state_expected = {"temperature": t, "cutoff": cut, "thermal_count": nt,
                              "thermal_energy": et, "active_count": all_n-low_n,
                              "active_energy": all_e-low_e}
            start = len(comparisons)
            for name, value in expected.items():
                check(row["case"]+"."+name, row[name], value)
            for name, value in state_expected.items():
                check(row["case"]+".state."+name, state[name], value)
            for name, values in (("initial_counts", p), ("predicted_counts", after),
                                 ("channel_extents", extent), ("target_exposure", exposure)):
                for key, value in values.items():
                    check(row["case"]+"."+name+"."+key, row[name][key], value)
            for key, values in cross.items():
                for k, value in enumerate(values):
                    check(row["case"]+"."+key+"."+str(k), row["cross_partitions"][key][k], value)
            check(row["case"]+".charge_check", after["HII"]+after["HeII"]+2*after["HeIII"], ne+all_n)
            check(row["case"]+".nuclei_check", sum(after.values(), D(0)), nn)
            check(row["case"]+".source_count_all_channels", all_n, sum(extent.values(), D(0)))
            check(row["case"]+".EOS_direct", cv * dec(state["temperature"]) * (nb+low_n), ub+low_e)
            assert row["source_rows"] == len(source[z]) == 10864
            assert row["distinct_positive_energy_groups"] == len(groups)
            assert state["threshold_consistent"] is True
            assert all(dec(v) == 0 for v in row["exact_residuals"].values())
            assert len(row["exact_residuals"]) == 13
            for key in ("physical_heating_eV_per_s", "stopping_time_s", "global_error_bound",
                        "source_time_discretization_error_bound"):
                assert row[key] is None, (row["case"], key)
            # CUTS.csv is explicitly the binary64 presentation, separate from
            # the Decimal80/1e-40 scientific-output relation.
            preview = {
                "caloric_temperature_K": t, "cutoff_eV": cut,
                "partition_delta_temperature_K": expected["partition_delta_temperature_K"],
                "source_count": all_n, "source_kinetic_eV": all_e,
                "source_below_cut_count_fraction": low_n/all_n,
                "source_below_cut_energy_fraction": low_e/all_e,
                "active_below_fs_count_fraction": cross["cutoff_active_below_fs"][0]/all_n,
                "active_below_fs_energy_fraction": cross["cutoff_active_below_fs"][1]/all_e,
            }
            for key, value in preview.items():
                got, want = float(cuts[row["case"]][key]), float(value)
                assert math.isfinite(got) and got == want, (row["case"], key, got, want)
            assert cuts[row["case"]]["physical_heating_eV_per_s"] == "null"
            nearest_margin = min(abs(k-stored_cut)/max(k,stored_cut) for k,_ in groups
                                 if max(k, stored_cut))
            assert nearest_margin > D("1e-50"), (row["case"], "near numerical branch ambiguity")
            summaries.append({
                "case": row["case"], "checks": len(comparisons)-start,
                "max_relative": str(max(dec(x["relative"]) for x in comparisons[start:])),
                "selected_prefix": j, "all_consistent_prefix_count": len(consistent),
                "nearest_relative_threshold_margin": str(nearest_margin),
                "source_packets": len(packets), "physical_heating": None,
            })

        maxrel = max(dec(x["relative"]) for x in comparisons)
        # Verify changed API and a new actual-source equality boundary. These
        # focused production calls do not recompute any C23B source quadrature.
        sys.path.insert(0, str(ROOT / "implementation"))
        from source_cutoff_binding import SavedSupplier, bind, normalization_counts
        supplier = SavedSupplier(raw)
        base_req = copy.deepcopy(cases[0]["request"])
        guards = []
        for key, value in (("preexisting_nonthermal_atoms", []),
                           ("initial_free_electron_count", "123"),
                           ("physical_heating_eV_per_s", "999")):
            bad = dict(base_req, **{key:value})
            try:
                bind(supplier, bad)
            except (ValueError, TypeError):
                guards.append({"name":"unknown:"+key, "status":"PASS_REJECTED"})
            else:
                raise AssertionError("unknown top-level key silently ignored: "+key)
        try:
            bind(supplier, ["not", "a", "mapping"])
        except (ValueError, TypeError):
            guards.append({"name":"nonobject_request", "status":"PASS_REJECTED"})
        else:
            raise AssertionError("nonobject request accepted")
        for key in sorted(REQUIRED):
            bad = copy.deepcopy(base_req)
            del bad[key]
            blocked = bind(supplier, bad)
            assert blocked["status"] == "BLOCKED_MISSING_BATH_OR_SOURCE_CONTRACT"
            assert blocked["missing_fields"] == [key]
            assert blocked["inventory"] is None and blocked["physical_heating_eV_per_s"] is None
            guards.append({"name":"missing:"+key, "status":"PASS_BLOCKED"})
        # Independent algebra of density and abundance normalization.
        spec = copy.deepcopy(base_req["normalization"])
        spec["proper_volume_cm3"] = "7/3"
        abundance = {"mode":"abundance", "proper_volume_cm3":"7/3",
                     "reference_density_cm3":"5/2",
                     "values_per_reference":{k:str(Fraction(v)/Fraction(5,2))
                                              for k,v in spec["values_cm3"].items()}}
        a, b = normalization_counts(spec), normalization_counts(abundance)
        assert a == b
        for key in POP:
            check("normalization_new."+key, a[key], direct_counts(spec)[key])
        # New equality witness: choose the actual lowest saved K and set
        # chi=3/2, T0=K/(chi*kB), so including equality atoms leaves T fixed.
        z_text = base_req["redshift"]
        candidates = [r for r in input_rows if Fraction(r["redshift"]) == Fraction(z_text)]
        minimum = min(Fraction(r["kinetic_eV"]) for r in candidates)
        kb_exact = Fraction("1.380649e-23") / Fraction("1.602176634e-19")
        equality_req = dict(base_req, initial_temperature_K=str(minimum/(Fraction(3,2)*kb_exact)),
                            chi="3/2", proper_duration_s="17")
        eq = bind(supplier, equality_req)
        eq_expected_n = sum((Fraction(r["number_weight_per_target_s"])
                             * Fraction(base_req["normalization"]["values_cm3"][r["channel"]])
                             * Fraction(17)
                             for r in candidates if Fraction(r["kinetic_eV"]) == minimum), Fraction(0))
        assert eq["state"].cutoff == minimum
        assert eq["state"].temperature == Fraction(equality_req["initial_temperature_K"])
        assert eq["cutoff_classified_source_count"] == eq_expected_n > 0
        assert eq["cutoff_classified_source_eV"] == minimum * eq_expected_n
        assert eq["state"].thermal_groups == 1 and eq["state"].threshold_consistent
        assert eq["physical_heating_eV_per_s"] is None
        equality = {"case":"actual_source_lowest_atom_exact_equality",
                    "request":equality_req, "lowest_energy_eV":str(minimum),
                    "thermal_source_count":str(eq_expected_n),
                    "thermal_source_energy_eV":str(minimum*eq_expected_n),
                    "selected_prefix":1, "equality_owner":"THERMAL", "status":"EXACT_PASS"}
        maxrel = max(dec(x["relative"]) for x in comparisons)

    write(run/"INPUT_OUTPUT_PINS.json", pins)
    write(run/"CASE_AUDIT.json", summaries)
    write(run/"COMPARISONS.json", comparisons)
    write(run/"TARGETED_REVIEW.json", {"guards":guards,
          "new_normalization_pair":"EXACT_AND_DECIMAL_PASS", "equality":equality})
    result = {
        "status":"PASS_SCOPED", "independent_oracle":"Decimal80 direct raw-CSV sums and prefix enumeration",
        "production_numerical_import_for_saved_case_audit":False,
        "decimal_precision":80, "relative_acceptance":str(RELATIVE_ACCEPTANCE),
        "saved_cases_audited":18, "scalar_comparisons":len(comparisons),
        "maximum_relative_difference":str(maxrel),
        "cross_cells_per_case":6, "exact_recorded_residuals_per_case":13,
        "new_actual_source_equality_witnesses":1, "new_normalization_pairs":1,
        "api_guards":len(guards), "source_quadratures":0, "new_ODE":0,
        "old_KC_or_C23B_suite_reruns":0,
        "finding":{"id":"C9-F1","class":"implementation_input_contract",
                   "status":"CLOSED_BY_GUARD_REVISION","actual18cases_affected":False,
                   "old_source_sha256":OLD_IMPLEMENTATION_SHA,
                   "new_source_sha256":pins["implementation/source_cutoff_binding.py"]["sha256"]},
        "wall_s":time.perf_counter()-t0, "cpu_s":time.process_time()-c0,
        "maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "worker_cpu":cpu, "native_threads":1, "cpu55_used":False,
        "physical_heating":None, "global_error_bound":None,
    }
    write(run/"RESULT.json",result)
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--worker",type=Path,required=True)
    p.add_argument("--cpu",type=int,required=True)
    a=p.parse_args()
    main(a.worker,a.cpu)

