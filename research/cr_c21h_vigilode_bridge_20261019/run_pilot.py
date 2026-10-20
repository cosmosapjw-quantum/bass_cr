"""Create-only single-job C21H comparisons. Native execution is opt-in and bounded."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import importlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback

sys.dont_write_bytecode = True
# Set before NumPy/SciPy or any Rust child can initialise a worker pool.
NUMPY_ALREADY_IMPORTED = "numpy" in sys.modules
THREAD_ENV = {name:"1" for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS",
    "MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","RAYON_NUM_THREADS")}
os.environ.update(THREAD_ENV)
from optical_adapter import (AdapterError, METHODS, VIGILODE_COMMIT, file_hash,
                             private_reference, run_rust_reference, write_new_json)

HERE = Path(__file__).resolve().parent
C21G_MANIFEST_SHA256 = "7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed"
PILOT = {
    "schema":"C21H_PILOT_CONTRACT_V1", "fixtures":["common_ic","native_source"],
    "methods":list(METHODS), "rtol":2e-11, "atol_multiplier":2e-14,
    "max_step_divisor":8., "wall_s_per_job":300., "max_original_rhs_calls_per_job":200000,
    "max_concurrency":1, "protected_cpu_ids":[55], "variants":["base","fd_half"],
    "base_jobs":4, "conditional_fd_jobs":4,
    "fd_followup_rule":"Only after the corresponding base job completes; halve both explicit derivative probe scales and preserve both outputs.",
    "comparison_reference":"Pinned C21F L0 endpoint first; verified completed C21G higher-tolerance receipts may be added as new assessments.",
    "C21G_reference_ladder":"REMAINS_READY; do not rerun a completed matching job or substitute these candidates for C21G receipts",
    "interpretation":"Independent integration-method/derivative sensitivity candidate; no native science promotion from process completion.",
    "global_error_bound":None,
    "holds":["Full48","source-age","spectral","angular","Case B","signed Bianchi","full EoR","standalone Grackle driver parity"],
}

def utc():
    return datetime.now(timezone.utc).isoformat()

def read_json(path):
    return json.loads(Path(path).read_text())

def file_record(path):
    p=Path(path)
    return {"bytes":p.stat().st_size,"sha256":file_hash(p)}

class BudgetedNativeMicro:
    """Bound each original provider call by the one job deadline."""
    def __init__(self, native, deadline):
        self.native, self.deadline = native, deadline
    @property
    def kind(self): return self.native.kind
    @property
    def calls(self): return self.native.calls
    @property
    def process(self): return self.native.process
    def __call__(self, *args):
        remaining = self.deadline-time.monotonic()
        if remaining<=0: raise AdapterError("NATIVE_JOB_WALL_BUDGET")
        self.native.timeout=min(15.,remaining)
        value=self.native(*args)
        if time.monotonic()>self.deadline: raise AdapterError("NATIVE_JOB_WALL_BUDGET")
        return value
    def close(self): self.native.close()

def verify_own_source():
    manifest=read_json(HERE/"EXECUTION_MANIFEST.json")
    for rel,expected in manifest["runtime_files"].items():
        p=Path(rel)
        if p.is_absolute() or ".." in p.parts or file_record(HERE/p)!=expected:
            raise AdapterError("C21H_EXECUTION_MANIFEST_MISMATCH "+rel)
    if manifest["vigilode_commit"]!=VIGILODE_COMMIT:
        raise AdapterError("C21H_VIGILODE_PIN_MISMATCH")
    return {"manifest":file_record(HERE/"EXECUTION_MANIFEST.json"),"runtime_files":manifest["runtime_files"]}

def context(args):
    source=args.source_dir.resolve(); c21g=args.c21g_unit.resolve()
    baseline=(args.baseline_dir or source/"evidence/C21F_NATIVE_NCP_20261018T1358Z").resolve()
    if file_hash(c21g/"EXECUTION_MANIFEST.json")!=C21G_MANIFEST_SHA256:
        raise AdapterError("PINNED_C21G_MANIFEST_MISMATCH")
    for name in ("campaign_contract","diagnostics","run_campaign"):
        if name in sys.modules and Path(sys.modules[name].__file__).resolve().parent!=c21g:
            raise AdapterError("C21G_IMPORT_LOCATION "+name)
    sys.path.insert(0,str(c21g))
    contract=importlib.import_module("campaign_contract")
    identity=contract.verify_inputs(source,baseline)
    private_reference(source)
    return source,c21g,baseline,contract,identity

def payload_inventory(root):
    root=Path(root).resolve(); records={}
    for path in sorted(root.rglob("*")):
        if path.is_symlink(): raise AdapterError("PAYLOAD_SYMLINK")
        if path.is_file() and path!=root/"JOB_RECEIPT.json":
            records[str(path.relative_to(root))]=file_record(path)
    return records

def verified_base(path, command, fixture_name, fixture_sha256, method,
                  input_identity, binary_identity, native_identity, own):
    """An fd-half probe requires a completed, matching, byte-verified base."""
    path=Path(path).resolve(); receipt=read_json(path/"JOB_RECEIPT.json")
    if receipt.get("execution")!="COMPLETE" or receipt.get("variant")!="base":
        raise AdapterError("FD_FOLLOWUP_BASE_NOT_COMPLETE")
    if receipt.get("command")!=command or receipt.get("fixture_name")!=fixture_name or receipt.get("fixture_sha256")!=fixture_sha256 or receipt.get("method")!=method:
        raise AdapterError("FD_FOLLOWUP_BASE_IDENTITY")
    if receipt.get("input_identity")!=input_identity or receipt.get("bridge_identity")!=binary_identity or receipt.get("native_identity")!=native_identity or receipt.get("source_identity")!=own:
        raise AdapterError("FD_FOLLOWUP_CONTEXT_MISMATCH")
    if command=="native" and read_json(path/"NATIVE_IDENTITY.json")!=native_identity:
        raise AdapterError("FD_FOLLOWUP_NATIVE_IDENTITY")
    if receipt["payload_files"]!=payload_inventory(path):
        raise AdapterError("FD_FOLLOWUP_PAYLOAD_CHANGED")
    return {"path":str(path),"receipt":file_record(path/"JOB_RECEIPT.json")}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=("plan","smoke","native"))
    p.add_argument("--source-dir",type=Path,default=HERE.parent/"cr_c21e_event_native_20261018")
    p.add_argument("--c21g-unit",type=Path,default=HERE.parent/"cr_c21g_reference_refinement_20261019")
    p.add_argument("--baseline-dir",type=Path)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--bridge",type=Path)
    p.add_argument("--bridge-build-receipt",type=Path)
    p.add_argument("--method",choices=METHODS,default=METHODS[0])
    p.add_argument("--fixture",choices=PILOT["fixtures"],default="common_ic")
    p.add_argument("--variant",choices=PILOT["variants"],default="base")
    p.add_argument("--base-job",type=Path)
    p.add_argument("--native",type=Path)
    p.add_argument("--build-dir",type=Path)
    p.add_argument("--cpu",type=int)
    args=p.parse_args(argv)
    source,c21g,baseline,contract,identity=context(args)
    own=verify_own_source()
    args.out.mkdir(parents=True,exist_ok=False)
    write_new_json(args.out/"INPUT_IDENTITY.json",identity)
    write_new_json(args.out/"C21H_SOURCE_IDENTITY.json",own)
    write_new_json(args.out/"PLAN.json",PILOT)
    if args.command=="plan":
        write_new_json(args.out/"PLAN_RECEIPT.json",{"status":"READY_EXECUTABLE_INPUTS_VERIFIED","native_executed":False,"at":utc()})
        return 0
    receipt={"schema":"C21H_JOB_RECEIPT_V1","started_at":utc(),"execution":"RUNNING",
        "source_identity":own,"input_identity":identity,"variant":args.variant,
        "command":args.command,"thread_environment":THREAD_ENV,
        "method":args.method,"fixture_name":args.fixture,"native_executed":False,
        "native_identity":None,"native_process_started":False,"native_launch_attempted":False,
        "physics":"NOT_EVALUATED","numerics":"NOT_EVALUATED","global_error_bound":None}
    start=time.monotonic(); deadline=start+PILOT["wall_s_per_job"]; provider=None
    try:
        if args.bridge is None: raise AdapterError("BRIDGE_BINARY_REQUIRED")
        binary=args.bridge.resolve(); bridge_identity={"path":str(binary),**file_record(binary)}
        receipt["bridge_identity"]=bridge_identity
        if args.command=="native" and args.bridge_build_receipt is None:
            raise AdapterError("NATIVE_JOB_REQUIRES_BRIDGE_BUILD_RECEIPT")
        if args.bridge_build_receipt is not None:
            build=read_json(args.bridge_build_receipt)
            # The build script's recorded source and binary must match this job.
            if build.get("binary_sha256")!=bridge_identity["sha256"] or build.get("vigilode_commit")!=VIGILODE_COMMIT or build.get("diffsol_version")!="0.17.1" or build.get("exit_code")!=0:
                raise AdapterError("BRIDGE_BUILD_PROVENANCE_MISMATCH")
            if build.get("source_files")!={key:own["runtime_files"][key] for key in ("rust_bridge/Cargo.toml","rust_bridge/Cargo.lock","rust_bridge/src/main.rs")}:
                raise AdapterError("BRIDGE_BUILD_SOURCE_MISMATCH")
            receipt["bridge_build_receipt"]={"path":str(args.bridge_build_receipt.resolve()),**file_record(args.bridge_build_receipt)}
        from run_experiment import Fixture, make_fixture
        from event_coupler import ManufacturedMicro
        if args.command=="native":
            if NUMPY_ALREADY_IMPORTED: raise AdapterError("NATIVE_REQUIRES_FRESH_SINGLE_THREAD_PYTHON_PROCESS")
            if args.native is None or args.cpu is None: raise AdapterError("NATIVE_BINARY_AND_EXPLICIT_ALLOCATED_CPU_REQUIRED")
            if args.cpu==55 or args.cpu not in os.sched_getaffinity(0): raise AdapterError("CPU_NOT_ADMITTED")
            # --cpu records the executor's explicit current campaign allocation;
            # membership in affinity alone is not proof of exclusive availability.
            from run_campaign import snapshot
            write_new_json(args.out/"LIVE_INVENTORY.json",snapshot(source,args.cpu))
            os.sched_setaffinity(0,{args.cpu})
            native_identity=contract.verify_native_binary(args.native,source,args.build_dir)
            write_new_json(args.out/"NATIVE_IDENTITY.json",native_identity)
            receipt["native_identity"]=native_identity
            f=Fixture(**read_json(baseline/args.fixture/"fixture.json")).validate()
        else:
            f=make_fixture(a0=.09,dx=1e-7,opacity_scale=.0003,Y=0.)
            receipt["fixture_name"]="manufactured_wiring_Y0"
        fixture=asdict(f); write_new_json(args.out/"fixture.json",fixture)
        receipt["fixture_sha256"]=f.digest
        if args.variant=="fd_half":
            if args.base_job is None: raise AdapterError("FD_FOLLOWUP_REQUIRES_BASE_JOB")
            receipt["base_job"]=verified_base(args.base_job,args.command,receipt["fixture_name"],
                f.digest,args.method,identity,bridge_identity,receipt["native_identity"],own)
        if args.command=="native":
            from native_micro import NativeMicro
            remaining=deadline-time.monotonic()
            if remaining<=0: raise AdapterError("NATIVE_JOB_WALL_BUDGET")
            receipt.update(native_launch_attempted=True,native_process_started=None)
            raw_provider=NativeMicro([str(args.native.resolve())],args.out/"native",
                timeout=min(15.,remaining),max_calls=200000)
            provider=BudgetedNativeMicro(raw_provider,deadline)
            receipt["native_process_started"]=True
        else:
            provider=ManufacturedMicro()
        receipt["microphysics"]=provider.kind
        factor=.5 if args.variant=="fd_half" else 1.
        import numpy as np
        result=run_rust_reference(f,provider,source,binary,args.out/"segments",contract.fixture_scales(fixture),
            rtol=PILOT["rtol"],alpha=PILOT["atol_multiplier"],max_step_divisor=8.,method=args.method,
            fd_relative=factor*np.finfo(float).eps**(1/3),time_fd_fraction=factor*1e-4,
            max_evaluations=200000,wall_s=deadline-time.monotonic())
        write_new_json(args.out/"result.json",result)
        from diagnostics import compare_endpoints, recompute_balances
        write_new_json(args.out/"INDEPENDENT_BALANCES.json",recompute_balances(fixture,result))
        if args.command=="native":
            reference=read_json(baseline/args.fixture/"radau.json")
            comparison=compare_endpoints(fixture,result,reference)
            write_new_json(args.out/"COMPARE_TO_PINNED_L0.json",comparison)
            receipt["numerics"]="OBSERVED_COMPARISON_TO_L0; C21G_LADDER_AND_NATIVE_ADOPTION_PENDING"
        else:
            receipt["numerics"]="MANUFACTURED_WIRING; SEE_INDEPENDENT_ANALYTIC_VALIDATION"
        if args.variant=="fd_half":
            # Recheck the base after the job as well, before using its endpoint.
            post_base=verified_base(args.base_job,args.command,receipt["fixture_name"],f.digest,args.method,
                identity,bridge_identity,receipt["native_identity"],own)
            if post_base!=receipt["base_job"]: raise AdapterError("FD_FOLLOWUP_BASE_DRIFT")
            write_new_json(args.out/"COMPARE_FD_HALF_TO_BASE.json",
                compare_endpoints(fixture,result,read_json(args.base_job/"result.json")))
        receipt["physics"]="LEDGER_RESIDUALS_RECORDED_IN_RESULT; NATIVE_ACCEPTANCE_SEPARATE"
        receipt["execution"]="COMPLETE"
        # Source and native identities are checked again after the actual calls.
        if contract.verify_inputs(source,baseline)!=identity or verify_own_source()!=own or file_record(binary)!={"bytes":bridge_identity["bytes"],"sha256":bridge_identity["sha256"]}:
            raise AdapterError("POST_EXECUTION_IDENTITY_DRIFT")
        if args.command=="native" and contract.verify_native_binary(args.native,source,args.build_dir)!=native_identity:
            raise AdapterError("NATIVE_IDENTITY_DRIFT")
        if args.command=="native" and provider.calls!=result["rhs_evaluations"]:
            raise AdapterError("NATIVE_CALL_AND_ORIGINAL_RHS_COUNT_MISMATCH")
    except BaseException as error:
        receipt.update(execution="FAILED",error_class=type(error).__name__,error=str(error))
        with (args.out/"failure_traceback.log").open("x") as stream: stream.write(traceback.format_exc())
    finally:
        if args.command=="native" and provider is not None:
            receipt["native_calls_attempted"]=provider.calls
            receipt["native_executed"]=provider.calls>0
        try:
            if provider is not None and hasattr(provider,"close"): provider.close()
        except BaseException as error:
            receipt.update(execution="FAILED",cleanup_error_class=type(error).__name__,cleanup_error=str(error))
        if args.command=="native" and provider is not None and provider.process is not None:
            receipt["native_exit_code"]=provider.process.poll()
        import numpy, scipy
        receipt.update(finished_at=utc(),wall_s=time.monotonic()-start,python=platform.python_version(),
                       numpy=numpy.__version__,scipy=scipy.__version__,
                       payload_files=payload_inventory(args.out))
        write_new_json(args.out/"JOB_RECEIPT.json",receipt)
    print(json.dumps({"out":str(args.out.resolve()),"execution":receipt["execution"],"native_executed":receipt["native_executed"]}))
    return 0 if receipt["execution"]=="COMPLETE" else 1

if __name__=="__main__":
    raise SystemExit(main())
