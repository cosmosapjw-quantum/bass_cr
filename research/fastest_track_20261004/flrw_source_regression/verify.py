"""Finite source-bound equation checks, never a solver/history admission.

The receiver is compiled unmodified. Expected event inventories use exact
rationals of the supplied f64 inputs, not another copy of its solver.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
TOL = F.from_float(4e-14)  # Finite f64 comparator, not a scientific gate.


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(rows):
    assertions = 0
    worst = 0.0
    groups = dict.fromkeys(("L", "R", "P", "G", "E"), 0)
    negatives = {"fixed_ne_is_not_dynamic_ne": 0,
                 "missing_upper_spectral_inflow": 0,
                 "arbitrary_redshift_coefficient": 0,
                 "lower_threshold_loss_not_total_number_conservation": 0}
    last_l = None

    def eq(actual, expected, scale=None):
        nonlocal assertions, worst
        a, b = F(actual), F(expected)
        assert math.isfinite(actual), "nonfinite result"
        s = abs(b) if scale is None else F(scale)
        error = abs(a - b)
        if s == 0:
            assert error == 0, f"exact zero mismatch: {actual}"
        else:
            relative = error / s
            worst = max(worst, float(relative))
            assert relative <= TOL, f"finite comparison mismatch: {actual}, {float(b)}, {float(relative)}"
        assertions += 1

    for tag, _index, d in rows:
        groups[tag] += 1
        if tag == "L":
            nh, nhe = map(F, d["n"])
            h, he1, he2 = map(F, d["x"])
            ne = nh*h+nhe*(he1+2*he2)
            eq(d["ne"], ne)
            temp = 2*F(d["u"])/(3*F(d["kb"])*(nh+nhe+ne))
            eq(d["temperature"], temp)
            # Independent species inventory: HI,HII,HeI,HeII,HeIII.
            lower = [nh*(1-h), nhe*(1-he1-he2), nhe*he1]
            upper = [nh*h, nhe*he1, nhe*he2]
            photo = [[F(d["c"])*lower[a]*F(d["sigma"][a][g])*F(d["photons"][g])
                      for g in range(3)] for a in range(3)]
            coll = [lower[a]*ne*F(d["beta"][a]) for a in range(3)]
            rec = [upper[a]*ne*F(d["alpha"][a]) for a in range(3)]
            net = [sum(photo[a])+coll[a]-rec[a] for a in range(3)]
            for a in range(3):
                for g in range(3): eq(d["photo"][a][g], photo[a][g])
                eq(d["collision"][a], coll[a]); eq(d["recombination"][a], rec[a])
            # Fraction equations are compared only for populated nuclei.
            if nh: eq(d["rhs"][0], net[0]/nh, (sum(photo[0])+coll[0]+rec[0])/nh)
            if nhe:
                eq(d["rhs"][1], (net[1]-net[2])/nhe,
                   (sum(photo[1])+sum(photo[2])+coll[1]+rec[1]+coll[2]+rec[2])/nhe)
                eq(d["rhs"][2], net[2]/nhe, (sum(photo[2])+coll[2]+rec[2])/nhe)
            for g in range(3): eq(d["rhs"][4+g], -sum(photo[a][g] for a in range(3)))
            ev, kb = F(d["ev"]), F(d["kb"])
            chi, energy = list(map(F,d["chi"])), list(map(F,d["energy"]))
            heat = sum(photo[a][g]*(energy[g]-chi[a])*ev for a in range(3) for g in range(3))
            ci_loss = sum(coll[a]*chi[a]*ev for a in range(3))
            rr_loss = sum(rec)*F(3,2)*kb*temp
            escape = sum(rec[a]*(chi[a]*ev+F(3,2)*kb*temp) for a in range(3))
            eq(d["rhs"][3], heat-ci_loss-rr_loss, abs(heat)+ci_loss+rr_loss)
            eq(d["escape"], escape)
            binding_dot = nh*F(d["rhs"][0])*chi[0]*ev
            binding_dot += nhe*(F(d["rhs"][1])*chi[1]+F(d["rhs"][2])*(chi[1]+chi[2]))*ev
            primary_dot = sum(F(d["rhs"][4+g])*energy[g]*ev for g in range(3))
            terms = [F(d["rhs"][3]),binding_dot,primary_dot,F(d["escape"])]
            eq(float(sum(terms)), 0, sum(map(abs,terms)))
            if nhe == 0:
                # Joint pure-H photon/atom budget eliminates photo absorption.
                lhs = nh*F(d["rhs"][0])+sum(map(F,d["rhs"][4:]))
                eq(float(lhs), coll[0]-rec[0], sum(photo[0])+coll[0]+rec[0])
                if coll[0] == 0 and sum(photo[0]) == 0:
                    eq(d["rhs"][0], -F(d["alpha"][0])*nh*h*h)
            last_l = d
        elif tag == "R":
            nh, alpha, x0, t = (F(d[k]) for k in ("nh","alpha","x0","t"))
            exact_x = x0/(1+alpha*nh*x0*t)
            eq(d["x"], exact_x)
            assert last_l["x"][0] == d["x"] and last_l["n"][0] == d["nh"]
            # Only instantaneous RHS samples on the analytical static curve.
            eq(last_l["rhs"][0], -alpha*nh*F(d["x"])**2)
            if t:
                dynamic = -alpha*nh*F(d["x"])**2
                fixed_ne = -alpha*nh*x0*F(d["x"])
                assert abs(dynamic-fixed_ne) > TOL*abs(dynamic)
                negatives["fixed_ne_is_not_dynamic_ne"] += 1
        elif tag == "P":
            a, mpc, c = F(d["a"]), F(d["mpc"]), F(d["c"])
            volume = (a*mpc)**3
            n, energy, counts = (list(map(F,d[k])) for k in ("n","energy","counts"))
            # Fit accuracy was checked in F01. Here sigma is an input to the
            # unit/owner ledger, not an independently certified atomic value.
            sigma = [list(map(F,row)) for row in d["sigma"]]
            events = [[c*n[i]*sigma[i][g]*counts[g]/volume for g in range(3)] for i in range(3)]
            total = sum(sum(row) for row in events)
            eq(d["loss"], volume*total)
            eq(float(F(d["loss"])/volume), sum(map(F,d["events"])), total)
            for i in range(3):
                gamma = sum(c*sigma[i][g]*counts[g]/volume for g in range(3))
                eq(d["gamma"][i],gamma); eq(d["events"][i],sum(events[i]))
                for g in range(3): eq(d["hhe_photo"][i][g],events[i][g])
            for g in range(3): eq(d["hhe_photon_rhs"][g],-sum(events[i][g] for i in range(3)))
            absorbed = sum(events[i][g]*energy[g]*F(1.602176634e-12) for i in range(3) for g in range(3))
            eq(d["absorbed"],absorbed)
            eq(float(sum(map(F,d["heat"]))+sum(map(F,d["binding"]))),absorbed)
            if not any(counts) or not any(n): eq(d["loss"],0)
        elif tag == "G":
            amp, h = d["amp"], d["h"]
            edges = d["edges"]
            for g in range(4): eq(d["n"][g],amp*(math.exp(-edges[g])-math.exp(-edges[g+1])))
            for g in range(5): eq(d["flux"][g],h*edges[g]*amp*math.exp(-edges[g]))
            n, flux = list(map(F,d["n"])), list(map(F,d["flux"]))
            absorption = [F(d["c"])*F(d["kappa"][g])*n[g]/F(d["mpc"]) for g in range(4)]
            actual_flux = [F(h)*F(d["coeff"][g])*n[g] for g in range(4)]
            for g in range(4):
                rhs=F(d["source"][g])-absorption[g]-actual_flux[g]
                if g<3: rhs+=actual_flux[g+1]
                eq(d["rhs"][g],rhs,abs(F(d["source"][g]))+absorption[g]+actual_flux[g]+(actual_flux[g+1] if g<3 else 0))
            summed=sum(map(F,d["rhs"]));scale=sum(abs(F(v)) for v in d["rhs"])+sum(absorption)+sum(flux)
            expected_physical=flux[4]-flux[0]-sum(absorption)
            if d["mode"]==0:
                eq(float(summed),expected_physical,scale)
                assert flux[0]>0
                negatives["lower_threshold_loss_not_total_number_conservation"]+=1
            elif d["mode"]==1:
                # The same spectrum with omitted top inflow has exact deficit.
                eq(float(summed-expected_physical),-flux[4],scale)
                assert abs(summed-expected_physical)>TOL*scale
                negatives["missing_upper_spectral_inflow"]+=1
            else:
                assert abs(summed-expected_physical)>TOL*scale
                negatives["arbitrary_redshift_coefficient"]+=1
        elif tag == "E":
            for actual, source in zip(d["rhs"],d["source"]): eq(actual,source)
            for v in d["gamma"]: eq(v,0)

    assert groups == {"L":46,"R":18,"P":36,"G":6,"E":2}, groups
    assert all(negatives.values()), negatives
    # Density dilution cancels in the fraction. This is exact algebra only;
    # the pinned F03 function has no expansion argument or H!=0 execution.
    nh, x, q = F(1,1024), F(1,4), F(3,2**40)
    for H in (F(0),F(1,2**30),F(3,2**25)):
        dn=-3*H*nh; dni=nh*q-3*H*nh*x
        eq(float((dni*nh-nh*x*dn)/(nh*nh)),q)
    return {"status":"SCOPED_FINITE_SOURCE_REGRESSION_PASS","rows":groups,
            "assertions":assertions,"finite_relative_tolerance":float(TOL),
            "max_scaled_discrepancy":worst,"negative_controls":negatives,
            "L_lane":"ACTUAL_STATIC_HHE_RHS_PLUS_EXACT_ALGEBRA_DILUTION",
            "P_lane":"ACTUAL_F01_F03_EVENT_LEDGER_AND_PROFILE_BOUND_LEGACY_EDGES",
            "Q_lane":"NOT_APPLICABLE_TO_HOMOGENEOUS_STATE",
            "CR_F0":"MODEL_OFF_DECLARED_RUNTIME_DISPATCH_NOT_BOUND",
            "general_FLRW_consumer":"NOT_IMPLEMENTED_IN_PINNED_STATIC_MAP",
            "diffuse_photon_number_adapter":"NOT_IMPLEMENTED",
            "uniform_error_enclosure":False,"physical_admission":False,
            "history_integrations":0,"old_suites_replayed":0,
            "independent_agent_or_human_review":False}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--receiver",type=Path,required=True)
    ap.add_argument("--rustc",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    receiver=args.receiver.resolve();out=args.output.resolve()
    lock=json.loads((ROOT/"SOURCE_INPUT_LOCK.json").read_text())
    head=subprocess.check_output(["git","-C",str(receiver),"rev-parse","HEAD"],text=True).strip()
    assert head==lock["receiver_commit"], "receiver commit mismatch"
    for record in lock["receiver_files"]:
        assert digest(receiver/record["path"])==record["sha256"], record["path"]
    out.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env.update(OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1")
    commands=[]
    cpu=min(os.sched_getaffinity(0))
    def run(cmd,name):
        start=time.monotonic()
        with (out/name).open("wb") as f:
            r=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT,env=env,
                             timeout=90,preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
        commands.append({"command":list(map(str,cmd)),"exit_code":r.returncode,
                         "wall_seconds":time.monotonic()-start,"evidence_path":name})
        (out/"COMMANDS.json").write_text(json.dumps(commands,indent=2)+"\n")
        r.check_returncode()
    run([args.rustc,"--version","--verbose"],"RUSTC.txt")
    run([args.rustc,"--edition=2021","--crate-name","rei_microphysics","--crate-type=rlib",
         "-C","opt-level=0","-C","codegen-units=1",receiver/"rust/rei_microphysics/src/lib.rs",
         "-o",out/"librei_microphysics.rlib"],"BUILD_LIBRARY.log")
    run([args.rustc,"--edition=2021","-C","opt-level=0","-C","codegen-units=1",ROOT/"probe.rs",
         "--extern",f"rei_microphysics={out/'librei_microphysics.rlib'}","-o",out/"probe"],"BUILD_PROBE.log")
    run([out/"probe"],"ACTUAL_ROWS.tsv")
    rows=[]
    for line in (out/"ACTUAL_ROWS.tsv").read_text().splitlines():
        tag,index,data=line.split("\t");rows.append((tag,int(index),json.loads(data)))
    result=verify(rows)
    result.update(receiver_commit=head,source_lock_sha256=digest(ROOT/"SOURCE_INPUT_LOCK.json"),
                  probe_source_sha256=digest(ROOT/"probe.rs"),verifier_source_sha256=digest(Path(__file__)),
                  native_probe_sha256=digest(out/"probe"),native_library_sha256=digest(out/"librei_microphysics.rlib"),
                  rustc_sha256=digest(args.rustc),affinity_cpu=cpu,
                  rhs_function_evaluations=82,homogeneous_photo_evaluations=36,
                  legacy_photon_rate_evaluations=8)
    run(["ldd",out/"probe"],"LIBRARIES.txt")
    libs={}
    for line in (out/"LIBRARIES.txt").read_text().splitlines():
        for token in line.split():
            p=Path(token)
            if token.startswith("/") and p.is_file(): libs[str(p.resolve())]=digest(p.resolve())
    result["observed_dynamic_library_sha256"]=libs
    for record in lock["receiver_files"]:
        assert digest(receiver/record["path"])==record["sha256"], "receiver modified during run"
    (out/"RESULTS.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
