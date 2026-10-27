"""Changed-algorithm controls and four frozen full-grid m4 qualifications."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
import math
import sys
import time
import traceback

import numpy as np
from clock_engine import ClockError
from export_adapter import ExportError, export_event, PulseReturnBook
from runner_common import Context, args, require, write_new, sha, clock_metadata


def execute(ctx):
    checks=[]
    def check(name, condition):
        checks.append({"name":name,"pass":bool(condition)})
        require(condition,"CONTROL_FAILED:"+name)
    def rejects(name, fn):
        try:
            fn()
        except (ClockError,ExportError,ValueError,OverflowError):
            check(name,True)
        else:
            check(name,False)
    engine=ctx.engine
    check("native_extended64_and_binary64",engine.native_info["long_double_mantissa_bits"]==64 and engine.native_info["double_bytes"]==8)
    d=np.array([2.]);empty=np.array([],dtype=np.float64)
    r=np.array([[.25,.5]]);weights=np.array([[.25],[.75]])
    p=engine.prepare(d,empty,empty,r,weights,np.array([.5]),r/2,["toyA","toyB"])
    for m in (1,4,64):
        c=engine.clock(p,1.25,m)
        ratio=F(5,13)
        for s,w in enumerate((F(1,4),F(3,4))):
            for label,reward in (("count",F(1,4)),("kinetic",F(1,2))):
                exact=w*reward/F(2)*(1-ratio**m)
                interval=c["source_rows"][s][label]
                check("scalar_exact_resolvent_m"+str(m)+"_"+str(s)+label,
                      F.from_float(interval["A_lower"])<=exact<=F.from_float(interval["A_upper"]))
    for T in (.1,1.,10.):
        h=engine.horizon(p,T,64,.5)
        with localcontext() as dc:
            dc.prec=80
            exact=Decimal(1)/Decimal(32)*(1-(-2*Decimal.from_float(T)).exp())
            lo,hi=h["source_rows"][0]["count_cm3"]
            check("scalar_time_bracket_"+str(T),Decimal.from_float(lo)<=exact<=Decimal.from_float(hi))
    zero=engine.prepare(d,empty,empty,np.zeros((1,2)),weights,np.array([.5]),np.zeros((1,2)),["toyA","toyB"])
    zr=engine.horizon(zero,1.,4,.5)
    check("zero_reward_exact",all(row["count_cm3"]==[0.,0.] and row["kinetic_eV_cm3"]==[0.,0.] for row in zr["source_rows"]))
    check("zero_age_exact",engine.horizon(p,0.,4,.5)["source_rows"][0]["count_cm3"]==[0.,0.])
    # C9-F01: positive error propagation must remain an upper bound through LD underflow.
    tiny=math.ldexp(1.,-1074);huge=math.ldexp(1.,1023)
    under=engine.prepare(np.array([huge]),empty,empty,np.array([[tiny,tiny]]),
        np.ones((1,1)),np.ones(1),np.zeros((1,2)),["underflow_control"])
    uc=engine.clock(under,tiny,8,capture=True)
    exact_last=F.from_float(tiny)**8/(F.from_float(huge)+F.from_float(tiny))**8
    radius=uc["qualification"]["step_radius"][7,0,0]
    center=uc["qualification"]["z_steps"][7,0,0]
    check("positive_error_underflow_upper_survives",radius>0 and abs(exact_last-F.from_float(float(center)))<=F.from_float(float(radius)))
    # Independent rational inverse recurrence for a nonsymmetric two-state matrix.
    dm=np.array([2.,1.]);lm=np.array([-.25]);um=np.array([-.5])
    rr=np.array([[.25,.5],[.125,.25]]);ww=np.array([[1.,0.],[0.,1.]])
    det=F(15,8);inverse=[[F(1)/det,F(1,2)/det],[F(1,4)/det,F(2)/det]]
    xr=np.array([[float(sum(inverse[i][j]*F.from_float(rr[j,k]) for j in range(2))) for k in range(2)] for i in range(2)])
    pp=engine.prepare(dm,lm,um,rr,ww,np.ones(2),xr,["left","right"])
    cc=engine.clock(pp,.5,4)
    detb=F(5,2)*F(3,2)-F(1,8)
    ib=[[F(3,2)/detb,F(1,2)/detb],[F(1,4)/detb,F(5,2)/detb]]
    for k,label in enumerate(("count","kinetic")):
        previous=[F.from_float(v) for v in rr[:,k]];total=[F(0),F(0)]
        for step in range(4):
            z=[sum(ib[i][j]*previous[j] for j in range(2)) for i in range(2)]
            total=[total[i]+z[i] for i in range(2)]
            previous=[F(1,2)*v for v in z]
        for s in range(2):
            row=cc["source_rows"][s][label]
            check("nonsymmetric_exact_"+label+str(s),F.from_float(row["A_lower"])<=total[s]<=F.from_float(row["A_upper"]))
    for bad in (True,"1",float("nan"),float("inf"),-1.,2**54+1):
        rejects("invalid_horizon_"+repr(bad),lambda bad=bad:engine.horizon(p,bad,4,.5))
    for bad in (True,0,1.5):
        rejects("invalid_order_"+repr(bad),lambda bad=bad:engine.horizon(p,1.,bad,.5))
    for bad in (0.,1.,True):
        rejects("invalid_delta_"+repr(bad),lambda bad=bad:engine.horizon(p,1.,4,bad))
    rejects("negative_reward",lambda:engine.prepare(d,empty,empty,-r,weights,np.array([.5]),r/2))
    rejects("negative_source",lambda:engine.prepare(d,empty,empty,r,-weights,np.array([.5]),r/2))
    rejects("nonpositive_witness",lambda:engine.prepare(d,empty,empty,r,weights,np.array([0.]),r/2))
    rejects("wrong_dtype",lambda:engine.prepare(d.astype(np.float32),empty,empty,r,weights,np.array([.5]),r/2))
    rejects("not_Z_matrix",lambda:engine.prepare(dm,-lm,um,rr,ww,np.ones(2),xr))
    qualifications=[]
    chosen=[c for c in ctx.manifest["cases"] if c["R"]==80 and c["N"]==2048]
    example=None
    for case in chosen:
        ctx.guard_cpu()
        problem,identities=ctx.load_case(case)
        T=1e5 if case["chi"]==1.5 else 1e6
        h=engine.horizon(problem,T,4,.5,capture=True)
        check(case["case_id"]+":positive_witness",problem.beta_lower>0)
        for side in ("minus","plus"):
            c=h["clocks"][side];capture=c.pop("qualification")
            base=case["case_id"]+"_"+side
            arrays=ctx.output/(base+"_QUALIFICATION.npz")
            np.savez_compressed(arrays,**{k:v for k,v in capture.items() if isinstance(v,np.ndarray)})
            meta={"case":case["case_id"],"clock_label":side,"T_s":T,"m":4,"delta":.5,
                  "gamma_hex":c["gamma_hex"],"gamma_s_inverse":c["gamma_s_inverse"],
                  "epsilon_steps_hex":capture["epsilon_steps_hex"],
                  "source_rows":[{"z":row["source_id"],"count":row["count"],"kinetic":row["kinetic"]} for row in c["source_rows"]],
                  "arithmetic_certificate":c["arithmetic_certificate"]}
            metapath=ctx.output/(base+"_QUALIFICATION.json");write_new(metapath,meta)
            qualifications.append({"case":case["case_id"],"clock_label":side,
                "arrays":{"path":str(arrays.relative_to(ctx.unit)),"sha256":sha(arrays),"bytes":arrays.stat().st_size},
                "metadata":{"path":str(metapath.relative_to(ctx.unit)),"sha256":sha(metapath),"bytes":metapath.stat().st_size}})
        if example is None:
            row=h["source_rows"][0]
            kwargs=dict(case_id=case["case_id"],source_id=problem.source_ids[0],source_identity=identities[0],
                time_start_s=0.,time_end_s=T,count_cm3=row["count_cm3"],kinetic_eV_cm3=row["kinetic_eV_cm3"],
                frame="bath_frame_rest_target",clock_metadata=clock_metadata([h]))
            example=export_event(**kwargs,nb_m3=10.)
            no_nb=export_event(**kwargs)
            check("actual_nb_null",no_nb["native25"] is None and no_nb["event_rate_m3_s"] is None)
            check("native_indices_and_zero_wext_T",example["native25"]["delta_intervals"][11][0]>=0 and example["native25"]["delta_intervals"][12][1]<=0 and example["native25"]["delta_intervals"][23:]==[[0.,0.],[0.,0.]])
            check("retained_photon_separate",not example["retained_photon_port"]["native_w_ext_owner"])
            # Independently evaluate known exact linear rows at one common basis pair.
            N=sum(map(F.from_float,row["count_cm3"]))/2;E=sum(map(F.from_float,row["kinetic_eV_cm3"]))/2
            exacts={"fast_kinetic":-E,"internal":-F(2721,50)*N,"retained_photon":E+F(2721,50)*N}
            for key,exact in exacts.items():
                lo,hi=example["energy_eV_cm3"][key]
                check("correlated_energy_"+key,F.from_float(lo)<=exact<=F.from_float(hi))
            check("shared_energy_exact",sum(exacts.values())==0 and not example["correlated_conservation"]["independent_interval_corners_conserve"])
            book=PulseReturnBook("bath_frame_rest_target",case_id=case["case_id"],source_id=problem.source_ids[0]);book.append(no_nb)
            rejects("duplicate_window",lambda:book.append(no_nb))
            for key,bad in (("nb_m3",True),("nb_m3",0.),("frame","unknown"),("frame_gamma",2.),("count_cm3",[1.,0.]),("time_end_s",True)):
                altered=dict(kwargs);altered[key]=bad
                rejects("export_invalid_"+key+repr(bad),lambda altered=altered:export_event(**altered))
            altered=deepcopy(kwargs);altered["clock_metadata"]["records"][0]["clocks"]["minus"]["gamma_hex"]="0x1.0000000000000p+0"
            rejects("clock_identity_mismatch",lambda:export_event(**altered))
            write_new(ctx.output/"EXPLICIT_NB_ALGEBRA_CONTROL.json",{"scope":"Synthetic explicit nb=10 algebra control, not actual physical baryon normalization","event":example})
    write_new(ctx.output/"QUALIFICATION_INDEX.json",{"schema":"CR_CLOCK_QUALIFICATION_INDEX_V1","records":qualifications,"full_grid_two_rhs_steps":16,"full_grid_rhs":32})
    result={"schema":"CR_CLOCK_CONTROLS_RESULT_V1","decision":"PASS_SCOPED_CHANGED_IMPLEMENTATION","checks":checks,
        "qualification_clocks":4,"qualification_RHS":32,"old_science_replay":0,"new_provider_evaluations":0,
        "actual_primary_RHS":0,"native_info":engine.native_info,"worker_cpu_before_serialization_s":time.process_time()}
    write_new(ctx.output/"RESULT.json",result)
    print(json.dumps({"checks":len(checks),"all_pass":all(x["pass"] for x in checks),"qualification_RHS":32,"cpu_s":time.process_time()}))
    return 0


def main():
    a=args()
    try:
        return execute(Context(a))
    except Exception as e:
        out=a.output/"payload";out.mkdir(parents=True,exist_ok=True)
        write_new(out/"FAILURE.json",{"error":type(e).__name__,"message":str(e),"traceback":traceback.format_exc(),"worker_cpu_s":time.process_time()})
        print(str(e),file=sys.stderr);return 1


if __name__=="__main__":
    raise SystemExit(main())
