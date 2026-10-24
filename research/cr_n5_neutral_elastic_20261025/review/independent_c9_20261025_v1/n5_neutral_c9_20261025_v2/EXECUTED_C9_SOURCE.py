#!/usr/bin/env python3
"""Independent C9 reference. No production scientific module is imported."""
import argparse, datetime, decimal, gzip, hashlib, json, os, resource, signal, subprocess, sys, time, traceback
from pathlib import Path
MIB=1024**2
SELECTED=("chi1.5_R80_N2048","chi3_R80_N2048")
FIRST=("u_s","u_p","u_entry","t","r_s","r_p")
BATH=("EE","H1+","He4+","He4++","H1neutral","He4neutral")
NAMES=FIRST+("v_s","v_p")+tuple("H_"+s for s in BATH)
def writej(path,obj):
    with Path(path).open("x") as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
def pin(path,base=None):
    p=Path(path);b=p.read_bytes()
    return dict(path=str(p.relative_to(base)) if base else str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def worker(unit,out):
    import numpy as np
    import mpmath as mp
    decimal.getcontext().prec=70;mp.mp.dps=70;D=decimal.Decimal
    dec=lambda x:D.from_float(float(x))
    cfg=json.loads((unit/"inputs/CASE_V3.json").read_text())
    primary=unit/"runs/n5_neutral_primary_20261025_v1";baseline=unit/"inputs/reused/pr103"
    checks=[];cases=[];executed=0;cpu0=time.process_time()
    paths=[unit/"inputs/CASE_V3.json",unit/"inputs/INPUT_MANIFEST_V3.json"]+[unit/s["input"] for s in cfg["neutral_species"]]
    for name in SELECTED:paths += [primary/(name+".npz"),baseline/(name+".npz")]
    before=[pin(p,unit) for p in paths];writej(out/"INPUT_PINS.json",before)
    def check(name,value,limit=0.0):
        checks.append(dict(name=name,value=float(value),limit=float(limit),passed=bool(float(value)<=float(limit))))
    def scaled(a,b,floor=1e-300):
        a,b=np.asarray(a),np.asarray(b)
        return float(np.max(np.abs(a-b))/max(float(np.max(np.abs(b))),floor))
    def table(s):
        rows=[]
        for line in (unit/s["input"]).read_text().splitlines():
            f=line.split()
            if len(f)!=2:continue
            try:a,b=mp.mpf(f[0]),mp.mpf(f[1])
            except (ValueError,TypeError):continue
            rows.append((a,b))
        if len(rows)!=s["row_count"] or not all(a>0 and b>0 for a,b in rows):raise ValueError("MTCS row/positivity guard")
        if not all(rows[i][0]<rows[i+1][0] for i in range(len(rows)-1)):raise ValueError("MTCS order")
        return rows
    tables={s["label"]:table(s) for s in cfg["neutral_species"]}
    def coeff(Ef,s):
        import bisect
        E=mp.mpf(float(Ef));tab=tables[s["label"]];xx=[x[0] for x in tab]
        if E<xx[0] or E>xx[-1]:raise ValueError("MTCS extrapolation refused")
        j=min(bisect.bisect_right(xx,E)-1,len(tab)-2);a,sa=tab[j];b,sb=tab[j+1]
        slope=(sb-sa)/(b-a);sigma=sa+slope*(E-a);theta=mp.mpf(float(cfg["theta_eV"]))
        nu=mp.mpf(float(s["n_cm3"]))*1000000*mp.sqrt(2*E*mp.mpf(float(cfg["eV_J"]))/mp.mpf(float(cfg["electron_mass_kg"])))*sigma
        eps=1/mp.mpf(float(s["r"]));diff=2*eps*theta*E*nu
        drift=2*eps*nu*(theta*(2+E*slope/sigma)-E);x=E/theta
        P=mp.erf(mp.sqrt(x))-2*mp.sqrt(x)*mp.exp(-x)/mp.sqrt(mp.pi)
        dee=theta*mp.mpf(float(cfg["b_anchor_eV_s"]))*mp.sqrt(theta/E)*P
        return diff,drift,dee
    def factor(diag,lower,upper):
        p=[dec(x) for x in diag];l=[dec(x) for x in lower];u=[dec(x) for x in upper];m=[]
        for i in range(len(l)):
            if p[i]<=0:raise ValueError("Nonpositive Thomas pivot")
            z=l[i]/p[i];m.append(z);p[i+1]-=z*u[i]
        if p[-1]<=0:raise ValueError("Nonpositive final Thomas pivot")
        return p,m,u
    def solve(F,cols):
        p,m,u=F;n=len(p);ys=[[x if isinstance(x,D) else dec(x) for x in c] for c in cols]
        for c in ys:
            for i in range(1,n):c[i]-=m[i-1]*c[i-1]
            c[-1]/=p[-1]
            for i in range(n-2,-1,-1):c[i]=(c[i]-u[i]*c[i+1])/p[i]
        return ys
    try:
        check("charge_neutrality",abs(sum(s["n_cm3"]*s["Z"] for s in cfg["species"])-cfg["ne_cm3"]),cfg["tolerances"]["charge"])
        check("missing_isotope_null",0 if all(v is None for v in cfg["missing_isotope_densities"].values()) else 1)
        check("no_MTCS_event_hazard",0 if cfg["elastic_event_hazard"] is None and cfg["elastic_event_count"] is None else 1)
        for name in SELECTED:
            with np.load(primary/(name+".npz"),allow_pickle=False) as z:new={k:z[k] for k in z.files}
            with np.load(baseline/(name+".npz"),allow_pickle=False) as z:old={k:z[k] for k in z.files}
            E,pi=new["E_eV"],new["pi"];n=len(E);mid=(E[:-1]+E[1:])/2
            for k in ("E_eV","pi","conductance_EE"):
                check(name+"."+k+".exact_reuse",0 if np.array_equal(new[k],old[k]) else 1)
            for z in cfg["source_z"]:
                for pfx in ("source_","active_mask_"):
                    check(name+"."+pfx+z+".exact_reuse",0 if np.array_equal(new[pfx+z],old[pfx+z]) else 1)
            check(name+".old_bath4_exact",0 if np.array_equal(new["rhs_bath6"][:,:4],old["rhs_bath4"]) else 1)
            check(name+".old_CE_time_RHS_exact",0 if np.array_equal(new["rhs_first6"][:,[0,1,3,4,5]],old["rhs_first6"][:,[0,1,3,4,5]]) else 1)
            cn=[];coeff_results=[]
            for s in cfg["neutral_species"]:
                label=s["label"];c=new["conductance_"+label];cn.append(c)
                ix=set(np.linspace(0,n-2,24,dtype=int).tolist())
                for knot,_ in tables[label]:
                    j=int(np.searchsorted(mid,float(knot)))
                    for i in (j-1,j):
                        if 0<=i<n-1:ix.add(i)
                md=mm=mc=0.
                for i in sorted(ix):
                    diff,drift,dee=coeff(mid[i],s)
                    cref=mp.mpf(float(old["conductance_EE"][i]))*diff/dee
                    md=max(md,float(abs(mp.mpf(float(new["D_mid_"+label][i]))/diff-1)))
                    mm=max(mm,float(abs(mp.mpf(float(new["mu_mid_"+label][i]))-drift)/max(abs(drift),mp.mpf("1e-40"))))
                    mc=max(mc,float(abs(mp.mpf(float(c[i]))/cref-1)))
                for kind,v in (("D",md),("mu",mm),("c",mc)):check(name+"."+label+"."+kind+".independent",v,cfg["tolerances"]["independent"])
                coeff_results.append(dict(species=label,selected_edges=len(ix),D_relative=md,mu_relative=mm,conductance_relative=mc))
            ct=old["conductance_total"]+cn[0]+cn[1]
            check(name+".conductance_total",scaled(new["conductance_total"],ct),cfg["tolerances"]["generator"])
            up=ct/pi[:-1];down=ct/pi[1:];qd=-np.r_[up,0.]-np.r_[0.,down]
            for k,v in (("Q_total_lower",up),("Q_total_upper",down),("Q_total_diag",qd)):
                check(name+"."+k+".graph_construction",scaled(new[k],v),cfg["tolerances"]["generator"])
            hs,hp=old["rhs_first6"][:,0],old["rhs_first6"][:,1]
            for k,v in (("K_diag",-qd[1:]+hs+hp),("K_lower",-down[1:]),("K_upper",-up[1:])):
                check(name+"."+k+".physical_construction",scaled(new[k],v),cfg["tolerances"]["generator"])
            check(name+".weighted_K_symmetry",scaled(pi[1:-1]*new["K_upper"],pi[2:]*new["K_lower"]),cfg["tolerances"]["generator"])
            check(name+".SPD_graph_positive_weights",0 if np.all(pi>0) and np.all(ct>0) and np.all(hs>=0) and np.all(hp>=0) else 1)
            # pi*K quadratic form = c0*z0² + sum c_(i+1)*(z_(i+1)-z_i)² + sum pi_i*lambda_i*z_i².
            entry=np.zeros(n-1);entry[0]=down[0]
            phys=np.column_stack((hs,hp,entry,np.ones(n-1),E[1:]*hs,E[1:]*hp))
            for j,k in enumerate(FIRST):check(name+".RHS."+k,scaled(new["rhs_first6"][:,j],phys[:,j]),cfg["tolerances"]["generator"])
            for j,c in enumerate(cn):
                gain=c*np.diff(E)/pi[1:];gain[:-1]-=c[1:]*np.diff(E)[1:]/pi[1:-1]
                check(name+".RHS."+BATH[4+j],scaled(new["rhs_bath6"][:,4+j],gain),cfg["tolerances"]["generator"])
            F=factor(new["K_diag"],new["K_lower"],new["K_upper"])
            first=solve(F,[new["rhs_first6"][:,j] for j in range(6)]);executed+=6
            cond=solve(F,[first[0],first[1]]);executed+=2
            baths=solve(F,[new["rhs_bath6"][:,j] for j in range(6)]);executed+=6
            refs=first+cond+baths
            actual=[new[k] for k in FIRST]+[new["v_s"],new["v_p"]]+[new["H"][:,j] for j in range(6)]
            comparisons=[]
            for k,ref,stored in zip(NAMES,refs,actual):
                err=max(abs(dec(y)-x) for x,y in zip(ref,stored))/max(max(abs(x) for x in ref),D("1e-300"))
                check(name+".solve."+k,float(err),cfg["tolerances"]["independent"])
                comparisons.append(dict(rhs=k,max_norm_relative=str(err)))
            for j,k in enumerate(("v_s","v_p")):
                check(name+".conditional_RHS."+k,scaled(new["rhs_time2"][:,j],new[FIRST[j]]),cfg["tolerances"]["generator"])
            dd=[dec(x) for x in new["K_diag"]];dl=[dec(x) for x in new["K_lower"]];du=[dec(x) for x in new["K_upper"]]
            rhs=[[dec(x) for x in new["rhs_first6"][:,j]] for j in range(6)]+[first[0],first[1]]+[[dec(x) for x in new["rhs_bath6"][:,j]] for j in range(6)]
            residual=D(0)
            for ref,b in zip(refs,rhs):
                for i in range(n-1):
                    terms=[dd[i]*ref[i]]
                    if i:terms.append(dl[i-1]*ref[i-1])
                    if i<n-2:terms.append(du[i]*ref[i+1])
                    rr=abs(sum(terms)-b[i])/max(sum(abs(x) for x in terms)+abs(b[i]),D("1e-300"))
                    residual=max(residual,rr)
            check(name+".reference_backward_residual",float(residual),1e-60)
            part=max(abs(first[0][i]+first[1][i]+first[2][i]-1) for i in range(n-1))
            check(name+".reference_partition",float(part),cfg["tolerances"]["partition"])
            energy=max(abs(sum(baths[j][i] for j in range(6))+dec(E[0])*first[2][i]+first[4][i]+first[5][i]-dec(E[i+1]))/max(dec(E[i+1]),D(1)) for i in range(n-1))
            check(name+".reference_signed_energy",float(energy),cfg["tolerances"]["energy"])
            tail=D(0);inc=[D(0)]*(n-1)
            for i in range(n-2,-1,-1):
                tail+=dec(pi[i+1]);inc[i]=tail/dec(new["conductance_total"][i])
            tm=[D(0)]
            for v in inc:tm.append(tm[-1]+v)
            mferr=max(abs(dec(x)-y) for x,y in zip(new["mfpt_total"],tm))/max(tm)
            check(name+".NEW_noCE_MFPT_formula",float(mferr),cfg["tolerances"]["independent"])
            delta=float(np.max((cn[0]+cn[1])/old["conductance_total"]))
            told,tnew=old["mfpt_total"][1:],new["mfpt_total"][1:]
            check(name+".old_MFPT_exact_reuse",0 if np.array_equal(new["mfpt_old"],old["mfpt_total"]) else 1)
            check(name+".MFPT_upper_bound",float(np.max(np.maximum(tnew/told-1,0))),cfg["tolerances"]["bound"])
            check(name+".MFPT_lower_bound",float(np.max(np.maximum(told/((1+delta)*tnew)-1,0))),cfg["tolerances"]["bound"])
            private=dict(case=name,precision=70,RHS_names=NAMES,reference_columns=[[str(x) for x in col] for col in refs])
            with (out/("PRIVATE_REFERENCE_"+name+".json.gz")).open("xb") as f:
                f.write(gzip.compress(json.dumps(private,separators=(",",":")).encode(),compresslevel=1,mtime=0))
            case=dict(case=name,nodes=n,physical_RHS=14,RHS_names=NAMES,coefficient_comparisons=coeff_results,
                      solution_comparisons=comparisons,reference_backward_residual=str(residual),
                      reference_partition=str(part),reference_energy_scaled=str(energy),
                      min_Thomas_pivot=str(min(F[0])),new_noCE_MFPT_max_relative=str(mferr))
            cases.append(case);writej(out/(name+"_REVIEW.json"),case)
        check("all_input_bytes_unchanged",0 if before==[pin(p,unit) for p in paths] else 1)
        failures=[c for c in checks if not c["passed"]]
        result=dict(schema="CR_N5_NEUTRAL_INDEPENDENT_C9_V1",status="PASS_SCOPED_INDEPENDENT_C9_ALL14_PHYSICAL_RHS" if not failures else "FAIL_SCOPED_RETAINED_NO_ADMISSION",
                    run_id=out.name,independent_role="/root/provider_census_next",production_modules_imported=[],
                    methods=["literal MTCS parser and mp70 PL/units/drift/diffusion","independent Decimal70 Thomas factorization",
                             "all14 physical RHS including t/v_s/v_p","weighted SPD graph form and signed energy ledger"],
                    selected_cases=list(SELECTED),physical_RHS_solved=executed,
                    RHS_types_per_case=dict(probability_time_incoming_energy=6,conditional_time=2,bath_reward=6),
                    case_results=cases,checks=checks,check_count=len(checks),blocking_findings=failures,
                    worker_process_cpu_s=time.process_time()-cpu0,old_baseline_solves=0,old_science_replay=0,new_ODE=0,
                    source_quadrature=0,source_projection=0,global_error_bound=None,global_completion_percent=None,
                    EXECUTION="PASS" if not failures else "FAIL",PUBLICATION="ROOT_OWNED",BACKUP="ROOT_PENDING",DAG="N5_PARENT_OPEN_N6_N7_NOT_ACTIVATED")
        writej(out/"RESULT.json",result);return 0 if not failures else 1
    except BaseException as e:
        writej(out/"FAILED_RETAINED.json",dict(error=repr(e),traceback=traceback.format_exc(),physical_RHS_solved=executed,
               completed_cases=[c["case"] for c in cases],checks=checks,process_cpu_s=time.process_time()-cpu0))
        raise
def dispatch(unit,out):
    wall0=time.monotonic();cpu0=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    out.mkdir(parents=True,exist_ok=False);lease=out.parent/".neutral_c9_owned_lease"
    leased=started=False;status="FAILED_RETAINED";error=rc=None
    try:
        with lease.open("x") as f:json.dump(dict(pid=os.getpid(),run_id=out.name,role="independentC9"),f)
        leased=True
        if (unit/"implementation/.neutral_task_lease").exists():raise RuntimeError("Production lease active")
        cg=Path("/sys/fs/cgroup");st=dict((k,int(v)) for k,v in (line.split() for line in (cg/"memory.stat").read_text().splitlines()))
        current,maximum=int((cg/"memory.current").read_text()),int((cg/"memory.max").read_text())
        clean=max(0,st.get("inactive_file",0)-st.get("file_dirty",0)-st.get("file_writeback",0))
        avail=max(0,maximum-current)+clean-64*MIB
        state=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),affinity=sorted(os.sched_getaffinity(0)),
                   cpu_max=(cg/"cpu.max").read_text().strip(),memory_current=current,memory_max=maximum,
                   clean_inactive_file_reclaimable=clean,memory_available_after_reserve=avail,
                   memory_events=(cg/"memory.events").read_text(),production_task_lease_absent=True,
                   root_holds_plot_during_C9=True,NCP_runtime="UNOBSERVED",NCP_lease="UNOBSERVED")
        writej(out/"RESOURCE_ADMISSION.json",state)
        if avail<512*MIB or not {1,8}.issubset(os.sched_getaffinity(0)):raise RuntimeError("Resource admission rejected")
        receipts=[json.loads(p.read_text()) for p in (unit/"runs").glob("*/DISPATCH_RECEIPT.json")]
        used=sum(x.get("worker_cpu_s",0.) for x in receipts)
        prior_review=[json.loads(p.read_text()) for p in out.parent.glob("n5_neutral_c9_*/DISPATCH_RECEIPT.json")]
        review_spent=sum(x.get("worker_cpu_s",0.) for x in prior_review)
        review_wall_spent=sum(x.get("wall_s",0.) for x in prior_review)
        cpu_limit=int(10-review_spent);wall_limit=40-review_wall_spent
        if cpu_limit<1 or wall_limit<=0 or used+10>60:raise RuntimeError("Cumulative allocation exceeded")
        os.sched_setaffinity(0,{8});src=Path(__file__).resolve();copy=out/"EXECUTED_C9_SOURCE.py"
        with copy.open("xb") as f:f.write(src.read_bytes())
        dependency=out.parent/"dependencies/mpmath-1.3.0-py3-none-any.whl"
        if pin(dependency)["sha256"]!="a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c":raise RuntimeError("Dependency pin mismatch")
        writej(out/"PRE_EXECUTION.json",dict(source_pin=pin(copy),dependency_pin=pin(dependency),CPU_limit_s=cpu_limit,wall_limit_s=wall_limit,RLIMIT_AS_bytes=512*MIB,
               worker_cpu=1,coordinator_cpu=8,native_threads=1,inherited_known_worker_cpu_s=29.870022114,
               new_unit_previous_worker_cpu_s=used,C9_previous_worker_cpu_s=review_spent,C9_previous_wall_s=review_wall_spent,new_unit_ceiling_cpu_s=60.,
               selected=list(SELECTED),planned_physical_RHS=28,old_baseline_solves=0,
               root_release="C9_EXECUTION_RELEASE after S1 actual dual ACK"))
        env=dict(os.environ);env.update({k:"1" for k in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"]})
        env["PYTHONDONTWRITEBYTECODE"]="1"
        env["PYTHONPATH"]=str(dependency)+(os.pathsep+env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        def limits():
            os.sched_setaffinity(0,{1});resource.setrlimit(resource.RLIMIT_AS,(512*MIB,512*MIB))
            resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        with (out/"stdout.txt").open("x") as so,(out/"stderr.txt").open("x") as se:
            p=subprocess.Popen([sys.executable,str(copy),"--worker",str(unit),str(out)],stdout=so,stderr=se,env=env,cwd=out,preexec_fn=limits,start_new_session=True);started=True
            try:rc=p.wait(timeout=wall_limit)
            except subprocess.TimeoutExpired:
                error="WALL_TIMEOUT_REMAINING_C9_ALLOWANCE_OWN_CHILD_ONLY";os.killpg(p.pid,signal.SIGTERM)
                try:rc=p.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
        status="PASS" if rc==0 else "FAILED_RETAINED"
    except BaseException as e:error=repr(e)
    finally:
        if leased:lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt=dict(schema="CR_N5_C9_BOUNDED_DISPATCH_V1",run_id=out.name,status=status,error=error,child_started=started,returncode=rc,
                     worker_cpu_s=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
                     worker_peak_RSS_KiB=after.ru_maxrss if started else None,coordinator_cpu_s=time.process_time()-cpu0,wall_s=time.monotonic()-wall0,
                     CPU_limit_s=locals().get("cpu_limit"),wall_limit_s=locals().get("wall_limit"),C9_total_CPU_allowance_s=10,C9_total_wall_allowance_s=40,native_threads=1,worker_cpu=1,coordinator_cpu=8,
                     inherited_known_worker_cpu_s=29.870022114,global_spend=None,remaining=None,currency=None,
                     EXECUTION=status,PUBLICATION="ROOT_OWNED",BACKUP="ROOT_PENDING",DAG="N5_PARENT_OPEN_N6_N7_NOT_ACTIVATED")
        writej(out/"DISPATCH_RECEIPT.json",receipt);print(json.dumps(receipt))
    return 0 if status=="PASS" else 1
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--worker",action="store_true");ap.add_argument("unit",type=Path);ap.add_argument("out",type=Path);a=ap.parse_args()
    sys.exit(worker(a.unit.resolve(),a.out.resolve()) if a.worker else dispatch(a.unit.resolve(),a.out.resolve()))
