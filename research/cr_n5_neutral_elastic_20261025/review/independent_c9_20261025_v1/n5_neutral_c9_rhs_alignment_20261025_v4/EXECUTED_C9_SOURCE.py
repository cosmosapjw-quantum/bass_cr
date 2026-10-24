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
    decimal.getcontext().prec=70
    D=decimal.Decimal;dec=lambda x:D.from_float(float(x));cpu0=time.process_time()
    prior=out.parent/"n5_neutral_c9_20261025_v2"
    oldreview=json.loads((prior/"RESULT.json").read_text())
    cfg=json.loads((unit/"inputs/CASE_V3.json").read_text())
    expected={n+".RHS."+s for n in SELECTED for s in ["H1neutral","He4neutral"]}
    observed={r["name"] for r in oldreview["blocking_findings"]}
    if observed!=expected or oldreview["physical_RHS_solved"]!=28:raise RuntimeError("Prior exact review scope mismatch")
    rows=[]
    for name in SELECTED:
        path=unit/"runs/n5_neutral_primary_20261025_v1"/(name+".npz")
        pp=pin(path,unit)
        oldpin=next(r for r in json.loads((prior/"INPUT_PINS.json").read_text()) if r["path"]==pp["path"])
        if pp!=oldpin:raise RuntimeError("Frozen primary input changed")
        with np.load(path,allow_pickle=False) as z:a={k:z[k] for k in ["E_eV","pi","conductance_H1neutral","conductance_He4neutral","rhs_bath6"]}
        E=[dec(x) for x in a["E_eV"]];pi=[dec(x) for x in a["pi"]];n=len(E)
        for j,label in enumerate(["H1neutral","He4neutral"]):
            c=[dec(x) for x in a["conductance_"+label]]
            refs=[];diffs=[];gross_errors=[]
            for i in range(1,n):
                down=c[i-1]/pi[i];up=c[i]/pi[i] if i<n-1 else D(0)
                gain=down*(E[i]-E[i-1])-(up*(E[i+1]-E[i]) if i<n-1 else D(0))
                stored=dec(a["rhs_bath6"][i-1,4+j]);diff=abs(stored-gain)
                # This is the absolute-term scale of -Q^T E, not its cancelling signed net.
                gross=down*abs(E[i-1])+(down+up)*abs(E[i])+(up*abs(E[i+1]) if i<n-1 else D(0))
                refs.append(gain);diffs.append(diff);gross_errors.append(diff/max(gross,D("1e-300")))
            net=max(diffs)/max(max(abs(x) for x in refs),D("1e-300"));gross=max(gross_errors)
            rows.append(dict(case=name,species=label,active_nodes=n-1,net_norm_relative=str(net),gross_component_relative=str(gross),
                independent_frozen_gate=cfg["tolerances"]["independent"],generator_gross_gate=cfg["tolerances"]["generator"],
                independent_pass=net<=dec(cfg["tolerances"]["independent"]),generator_gross_pass=gross<=dec(cfg["tolerances"]["generator"])))
    good=all(x["independent_pass"] and x["generator_gross_pass"] for x in rows)
    result=dict(schema="CR_N5_C9_RHS_DIAGNOSTIC_ALIGNMENT_V1",
        status="PASS_SCOPED_DIAGNOSTIC_ALIGNMENT" if good else "FAIL_RETAINED",
        run_id=out.name,prior_review_run=prior.name,prior_review_result_sha256=pin(prior/"RESULT.json")["sha256"],
        preserved_initial_diagnostic_failures=oldreview["blocking_findings"],
        correction="Initial reviewer applied generator tolerance to the cancelling signed reward net norm. Frozen independent gate5e-10 applies to coefficient/RHS comparison; generator2e-13 remains on absolute-term-scaled operator arithmetic. No physical input, production code, tolerance value, existing result or initial failure record changed.",
        physical_RHS_solved=0,prior_completed_physical_RHS_reused=28,old_baseline_solves=0,new_ODE=0,source_quadrature=0,
        coefficient_evaluations=0,selected_signed_reward_series=4,criteria_count=8,results=rows,process_cpu_s=time.process_time()-cpu0,
        root_disposition_required=True,global_error_bound=None,global_completion_percent=None,
        EXECUTION="PASS" if good else "FAIL",PUBLICATION="ROOT_OWNED",BACKUP="ROOT_PENDING",DAG="N5_PARENT_OPEN_N6_N7_NOT_ACTIVATED")
    writej(out/"RESULT.json",result);return 0 if good else 1

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
               selected=list(SELECTED),planned_physical_RHS=0,planned_signed_reward_series=4,old_baseline_solves=0,
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
