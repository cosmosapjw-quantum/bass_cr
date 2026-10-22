"""Independent C23A audit: 80-digit augmented matrix exponential, no ODE.

The production source snapshot is the system under test. The oracle is an
independently assembled 8x8 continuous reaction/event generator evaluated by
mpmath.expm. No production kernel or production event formula enters the oracle.
Outputs are create-only and the reviewed source bytes are fixed by SHA256.
"""
from __future__ import annotations
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"
os.sched_setaffinity(0, {4})
import sys
import math
import json
import time
import hashlib
import importlib.util
import platform
from pathlib import Path
from datetime import datetime, timezone
import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "photo_subflow_snapshot.py"
EXPECTED = "36af631c24b3d1a2c34c9d7a4f470cbe85334a505e3cbad9ea3228d862c95079"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location("photo_subflow_under_review_v2", SOURCE)
sut = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sut
spec.loader.exec_module(sut)
mp.mp.dps = 80
POPS = ("HI", "HII", "HeI", "HeII", "HeIII")
EVENTS = ("HI", "HeI", "HeII")
CHI = (13.598434599702, 24.587389011, 54.4177655282)
EXCESS = (3.0, 7.0, 20.0)
KB = mp.mpf(1.380649e-23) / mp.mpf(1.602176634e-19)
PAB = mp.mpf("2e-12")
EAB = mp.mpf("5e-12")
REL = mp.mpf("1e-10")
RMIN = mp.mpf("1e-10")

def write_json(name, obj):
    with (ROOT/name).open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")

def f64(x):
    return float(x)

def matrix_reference(gamma, duration):
    # The state consists of five species plus three cumulative reaction counts.
    G = mp.matrix(8, 8)
    gh, ga, gb = (mp.mpf(x) for x in gamma)
    G[0, 0], G[1, 0], G[5, 0] = -gh, gh, gh
    G[2, 2], G[3, 2], G[6, 2] = -ga, ga, ga
    G[3, 3], G[4, 3], G[7, 3] = -gb, gb, gb
    return mp.expm(G * mp.mpf(duration))

def relative(error, truth):
    return abs(error / truth) if truth else mp.mpf(0) if not error else mp.inf

def fmt(v):
    return mp.nstr(v, 25)

thetas = [0.0, 1e-14, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2,
          0.1, 0.5, 1.0, 2.0, 4.0, 10.0, 20.0, 100.0,
          1e3, 1e4, 1e5, 1e6]
ratios = [0.0, 1e-14, 1e-8, 1e-4, 0.1, 1.0-2.0**-52,
          1.0, 1.0+2.0**-52, 10.0, 1e4, 1e8, 1e14, "infinite"]
patterns = [(f"basis_{k}", tuple(float(i == k) for i in range(5))) for k in range(5)]
patterns += [("neutral_H_He", (0.76, 0., 0.24, 0., 0.)),
             ("mixed_H_He", (0.10, 0.30, 0.20, 0.15, 0.25))]
cases = []
for theta in thetas:
    for ratio in ratios:
        if ratio == "infinite":
            a, b = 0., theta
        elif ratio <= 1:
            a, b = theta, theta*ratio
        else:
            a, b = theta/ratio, theta
        cases.append({"label":f"theta={theta:.17g};ratio={ratio}",
                      "gamma":(0.37*theta, a, b), "duration":1.0,
                      "patterns":patterns, "origin":"synthetic numerical stress"})

# Rate-unit scale invariance and very small/large inventory are separate cases.
for scale in (1e-200, 1e-20, 1., 1e20, 1e200):
    cases.append({"label":f"inventory_scale={scale:.1e}",
                  "gamma":(0.31, 0.7, 0.11), "duration":2.0,
                  "patterns":[("scaled_mixed",tuple(scale*x for x in patterns[-1][1]))],
                  "origin":"synthetic inventory scaling"})
for rate_scale in (1e-200, 1e-100, 1e-12, 1.0, 1e100, 1e200):
    cases.append({"label":f"rate_time_units={rate_scale:.1e}",
                  "gamma":(0.37*rate_scale, rate_scale, 0.1*rate_scale),
                  "duration":1.0/rate_scale,
                  "patterns":[patterns[-1]], "origin":"same dimensionless operator, varied units"})

# Actual P19 table values are used directly, without the reviewed adapter, to
# check the intended input scale as well as the artificial stress domain.
source_table = ROOT.parents[1]/"igm_supply/sources/P19V1_rates_fiducial.txt"
table_bytes = source_table.read_bytes()
assert hashlib.sha256(table_bytes).hexdigest() == "5b4cca58fcc46e821970c0a5a8cbb188cf2b5e6c00f56d6942588c86806662fe"
table = np.loadtxt(source_table)
for row_index in (0, 20, 40, 58):
    row = table[row_index]
    for duration in (1e10, 1e14, 1e17):
        cases.append({"label":f"P19_row={row_index};z={row[0]};dt={duration}",
                      "gamma":tuple(map(float,row[[1,3,5]])),
                      "heat":tuple(map(float,row[[2,4,6]])),
                      "duration":duration, "patterns":patterns,
                      "origin":"actual P19v1 fiducial source table"})

plan = {"run_id":"c23a_photo_subflow_v2_independent_operator_audit",
        "workflow_version":"1.0.0", "selected_stage":"C9 with C6-C8 independent evidence",
        "source_sha256":EXPECTED, "source_bytes":SOURCE.stat().st_size,
        "oracle":"mpmath 80-digit expm of independently built 8x8 species/event generator",
        "oracle_source":"this audit file; no production kernel formula reused",
        "mpmath_version":mp.__version__, "numpy_version":np.__version__,
        "python":platform.python_version(), "affinity":sorted(os.sched_getaffinity(0)),
        "native_threads":1, "new_ODE":0, "historical_reruns":0,
        "rate_cases":len(cases),
        "operator_calls_planned":sum(len(c["patterns"]) for c in cases),
        "criteria":{"population_abs_per_total_nuclei":"2e-12",
                    "event_abs_per_total_nuclei":"5e-12",
                    "relative":"1e-10 for oracle magnitude/total_nuclei >= 1e-10",
                    "output":"no negative or nonfinite accepted output",
                    "energy_ledger":"report independent state/event residuals; same normalized event tolerance with energy scale"},
        "theta_grid":thetas,"ratio_grid":ratios,
        "created_utc":datetime.now(timezone.utc).isoformat()}
write_json("PLAN.json", plan)
start_wall, start_cpu = time.perf_counter(), time.process_time()
records, failures = [], []
maxima = {}

def set_max(name, value, case, field):
    value = float(value)
    if name not in maxima or value > maxima[name]["value"]:
        maxima[name] = {"value":value,"case":case,"field":field}

calls = 0
for case_index, case in enumerate(cases):
    gamma = case["gamma"]
    heat = case.get("heat", tuple(g*e for g,e in zip(gamma,EXCESS)))
    dt = case["duration"]
    transition = matrix_reference(gamma,dt)
    for pname, values in case["patterns"]:
        calls += 1
        label = case["label"]+";inventory="+pname
        inv = mp.fsum(mp.mpf(x) for x in values)
        U = float(inv)*2.0
        before = mp.matrix([mp.mpf(x) for x in values]+[mp.mpf(0)]*3)
        exact = transition*before
        true_pop, true_counts = list(exact[:5]), list(exact[5:])
        result = sut.advance(dict(zip(POPS,values)),U,dt,
                             dict(zip(EVENTS,gamma)),dict(zip(EVENTS,heat)),
                             dict(zip(EVENTS,CHI)))
        actual_pop = [result.populations[k] for k in POPS]
        actual_events = [result.events[k] for k in EVENTS]
        issues, errs = [], {}
        for group, actual, true, names, atol in (
            ("population",actual_pop,true_pop,POPS,PAB),
            ("event",actual_events,true_counts,EVENTS,EAB)):
            group_abs, group_rel = mp.mpf(0),mp.mpf(0)
            for field, got, expected in zip(names,actual,true):
                if not math.isfinite(got) or got < 0:
                    issues.append({"kind":"invalid_output","field":field,"group":group,"got":str(got)})
                    continue
                ae = abs(mp.mpf(got)-expected)
                normalized = ae/inv
                re = relative(ae,expected)
                group_abs = max(group_abs, normalized)
                set_max(group+"_abs_per_inventory",normalized,label,field)
                if abs(expected)/inv >= RMIN:
                    group_rel=max(group_rel,re)
                    set_max(group+"_relative_qualified",re,label,field)
                if normalized > atol or (abs(expected)/inv >= RMIN and re > REL):
                    issues.append({"kind":"accuracy","group":group,"field":field,
                                   "actual":got,"reference_80digit":fmt(expected),
                                   "absolute_per_inventory":fmt(normalized),
                                   "relative":fmt(re),"relative_criterion_applied":bool(abs(expected)/inv >= RMIN)})
            errs[group+"_max_abs_per_inventory"]=float(group_abs)
            errs[group+"_max_relative_qualified"]=float(group_rel)
        e_before = mp.mpf(values[1])+mp.mpf(values[3])+2*mp.mpf(values[4])
        e_after = mp.mpf(actual_pop[1])+mp.mpf(actual_pop[3])+2*mp.mpf(actual_pop[4])
        true_e = mp.fsum(true_counts)
        true_heat = mp.fsum(c*mp.mpf(h)/mp.mpf(g) for c,h,g in zip(true_counts,heat,gamma) if g>0)
        true_binding = mp.fsum(c*mp.mpf(ch) for c,ch in zip(true_counts,CHI))
        true_import = true_heat+true_binding
        true_particles = mp.fsum(true_pop)+true_pop[1]+true_pop[3]+2*true_pop[4]
        true_temperature = 2*(mp.mpf(U)+true_heat)/(3*KB*true_particles)
        energy_scale = inv*max([mp.mpf(1)]+[mp.mpf(ch) for ch in CHI]+
                               [mp.mpf(h)/mp.mpf(g) for h,g in zip(heat,gamma) if g>0])
        energy_got = (result.heat_increment_ev,result.binding_increment_ev,
                      result.imported_energy_ev,result.thermal_energy_ev)
        energy_true = (true_heat,true_binding,true_import,mp.mpf(U)+true_heat)
        energy_names = ("heat","binding","imported","thermal_final")
        for name, got, expected in zip(energy_names,energy_got,energy_true):
            error = abs(mp.mpf(got)-expected)
            set_max(name+"_abs_per_energy_scale",error/energy_scale,label,name)
            if abs(expected)/energy_scale>=RMIN:
                set_max(name+"_relative_qualified",relative(error,expected),label,name)
            if not math.isfinite(got) or got < 0:
                issues.append({"kind":"invalid_energy","field":name,"actual":str(got)})
        charge = e_after-e_before-mp.fsum(mp.mpf(x) for x in actual_events)
        h_inventory = mp.fsum(mp.mpf(v) for v in actual_pop[:2])-mp.fsum(mp.mpf(v) for v in values[:2])
        he_inventory = mp.fsum(mp.mpf(v) for v in actual_pop[2:])-mp.fsum(mp.mpf(v) for v in values[2:])
        def binding_of(pop):
            return mp.mpf(CHI[0])*mp.mpf(pop[1])+mp.mpf(CHI[1])*mp.mpf(pop[3])+(mp.mpf(CHI[1])+mp.mpf(CHI[2]))*mp.mpf(pop[4])
        state_binding_delta = binding_of(actual_pop)-binding_of(values)
        binding_state_residual = state_binding_delta-mp.mpf(result.binding_increment_ev)
        total_state_ledger = mp.mpf(result.thermal_energy_ev)-mp.mpf(U)+state_binding_delta-mp.mpf(result.imported_energy_ev)
        electron_event_error=abs(mp.mpf(result.electron_increment)-true_e)/inv
        for name, value in (("H_inventory",h_inventory/inv),
                            ("He_inventory",he_inventory/inv),
                            ("charge_event",charge/inv),
                            ("electron_reference",electron_event_error),
                            ("binding_state",binding_state_residual/energy_scale),
                            ("energy_state",total_state_ledger/energy_scale)):
            set_max(name+"_residual",abs(value),label,name)
            errs[name+"_residual"] = float(value)
        set_max("temperature_relative",relative(mp.mpf(result.temperature_K)-true_temperature,true_temperature),label,"temperature_K")
        record={"case":label,"origin":case["origin"],"gamma_s_inv":gamma,
                "heat_ev_s_inv":heat,"duration_s":dt,"initial_populations":dict(zip(POPS,values)),
                "actual_populations":result.populations,"actual_events":result.events,
                "inventory":fmt(inv),"errors":errs,"failure_count":len(issues),
                "diagnostics":result.diagnostics}
        records.append(record)
        if issues:
            failures.append({"case":label,"input":record,"issues":issues})
    if case_index%25==0:
        print(json.dumps({"progress_rate_case":case_index+1,"total":len(cases),"operator_calls":calls,
                          "failing_calls":len(failures),"elapsed_wall_s":time.perf_counter()-start_wall}),flush=True)

base = {"populations":dict(zip(POPS,(0.76,0.,0.24,0.,0.))),
        "thermal_energy_ev":2.0,"duration_s":1.0,
        "gamma_s_inv":dict(zip(EVENTS,(.3,.5,.7))),
        "heat_ev_s_inv":dict(zip(EVENTS,(1.,2.,3.))),
        "binding_ev":dict(zip(EVENTS,CHI))}
invalids=[]
def altered(name, field, value):
    kw={k:(dict(v) if isinstance(v,dict) else v) for k,v in base.items()}
    if isinstance(field,tuple):
        kw[field[0]][field[1]]=value
    else:
        kw[field]=value
    invalids.append((name,kw))
altered("missing_population","populations",{"HI":1.0})
altered("unsupported_isotope_population","populations",dict(base["populations"],D=1e-5))
altered("empty_inventory","populations",dict.fromkeys(POPS,0.0))
altered("missing_gamma","gamma_s_inv",{"HI":1.0})
altered("extra_gamma","gamma_s_inv",dict(base["gamma_s_inv"],DI=1.0))
altered("missing_heat","heat_ev_s_inv",{"HI":1.0})
altered("missing_binding","binding_ev",{"HI":13.6})
for field in ("populations","gamma_s_inv","heat_ev_s_inv","binding_ev"):
    key=POPS[0] if field=="populations" else EVENTS[0]
    for value,label in ((-1.,"negative"),(math.nan,"nan"),(math.inf,"inf")):
        altered(field+"_"+label,(field,key),value)
altered("zero_binding",("binding_ev","HI"),0.0)
for field in ("thermal_energy_ev","duration_s"):
    for value,label in ((-1.,"negative"),(math.nan,"nan"),(math.inf,"inf")):
        altered(field+"_"+label,field,value)
altered("heat_without_ionization",("gamma_s_inv","HI"),0.0)
altered("theta_above_contract","duration_s",1.0e7)
invalid_results=[]
for name,kw in invalids:
    try:
        sut.advance(**kw)
    except (ValueError,ArithmeticError) as exc:
        invalid_results.append({"name":name,"pass":True,"exception":type(exc).__name__,"message":str(exc)})
    else:
        invalid_results.append({"name":name,"pass":False,"reason":"accepted invalid input"})

execution={"status":"completed","exit_code":0,"source_sha256":EXPECTED,
           "rate_cases":len(cases),"operator_calls":calls,"failing_operator_calls":len(failures),
           "invalid_input_checks":len(invalid_results),"invalid_input_failures":sum(not r["pass"] for r in invalid_results),
           "wall_s":time.perf_counter()-start_wall,"cpu_s":time.process_time()-start_cpu,
           "cpu_affinity":sorted(os.sched_getaffinity(0)),"native_threads":1,
           "mpmath_dps":mp.mp.dps,"new_ODE":0,"historical_ODE_reruns":0,
           "maxima":maxima,"overall_accuracy":"FAIL" if failures else "PASS_SCOPED",
           "created_utc":datetime.now(timezone.utc).isoformat()}
write_json("OPERATOR_RESULTS.json",records)
write_json("FAILURES.json",failures)
write_json("FAILCLOSED.json",invalid_results)
write_json("EXECUTION.json",execution)
print(json.dumps(execution,indent=2),flush=True)
