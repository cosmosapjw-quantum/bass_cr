#!/usr/bin/env python3
"""Opt-in same-host 18-channel performance/parity benchmark, not a new scan."""
from __future__ import annotations
import run_tp2a  # sets one BLAS thread before numerical imports
from pathlib import Path
import argparse,concurrent.futures as cf,json,multiprocessing as mp,os,resource,subprocess,sys,time,traceback
import numpy as np
from paths import REPO
from runtime import write_json,atomic_file,save_bank
from aligned_cross import cross_blocks
from fast_cross import fast_cross
from native_ring import NativeRing
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from cr_repro.observables import projectile_speed_au

KEYS=('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')
def evaluate(args):
    kind,bank,native_dir=args;ch=symmetric_channels(bank);v=projectile_speed_au(100.)
    tr=Trajectory(((0.,0.,0.),(2.,0.,0.)),((0.,0.,0.),(0.,0.,v)))
    evaluator=NativeRing(native_dir) if kind=='native' else None
    start=time.perf_counter();cpu=time.process_time()
    if kind=='original':x=cross_blocks(tr,ch,bank[0].edges,-12./v,order=24)
    else:x=fast_cross(tr,ch,bank[0].edges,-12./v,order=24,evaluator=evaluator)
    return {'backend':kind,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
            'peak_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'pid':os.getpid(),
            'arrays':{k:x[k] for k in KEYS}}

def parity(got,ref):
    rows={};passed=True
    for k in KEYS:
        a=float(np.linalg.norm(got[k]-ref[k]));n=float(np.linalg.norm(ref[k]));r=a/n if n else (0. if a==0 else None)
        ok=a<=1e-12+1e-10*n;passed &= ok
        rows[k]={'absolute':a,'relative':r,'reference_norm':n,'pass':ok}
    return passed,rows

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);ap.add_argument('--native-build',required=True)
    ap.add_argument('--workers',type=int);ap.add_argument('--expected-commit');a=ap.parse_args(argv)
    out=Path(a.out).resolve()
    if out.exists() or out.with_name(out.name+'_RETURN.zip').exists():ap.error('create-only output exists')
    out.mkdir(parents=True);r={'schema':'BASS_TP2A_BENCHMARK_V1','capture_execution_allowed':False,'production_admission':'HOLD',
                              'all_bound':'OPEN','b_grid':'NO_GO','single_host_order24_z_minus12':True,'timing_repetitions':1};code=0
    try:
        r['sources']=run_tp2a.verify_sources()
        if a.expected_commit:
            head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
            if head!=a.expected_commit:raise ValueError('commit identity mismatch')
            r['execution_head']=head
        native=str(Path(a.native_build).resolve());r['native_build']=NativeRing(native).receipt
        limits=run_tp2a.resource_limits();n=a.workers if a.workers is not None else limits['default_workers']
        if not 1<=n<=limits['max_safe_workers']:raise ValueError('workers exceeds resource budget')
        r['resources']=limits;r['new_tests']=run_tp2a.run_new_tests(out,'native')
        bank=atomic_bank(RadialSpec(radius=64,elements=40,degree=4,lmax=1,bound_nmax=2,positive_per_l=1,positive_emax=2,quad_order=12,grading=2))
        r['basis']=save_bank(out,bank);records=[];reference=None
        for kind in ('original','numpy','native'):
            print(json.dumps({'event':'benchmark_start','backend':kind,'out':str(out)}),flush=True)
            result=evaluate((kind,bank,native));arrays=result.pop('arrays')
            atomic_file(out/(kind+'.npz'),lambda f:np.savez_compressed(f,**arrays))
            if reference is None:reference=arrays
            ok,p=parity(arrays,reference);result['parity']=p;records.append(result)
            write_json(out/(kind+'.json'),result);print(json.dumps({'event':'benchmark_complete','backend':kind,'wall_seconds':result['wall_seconds'],'parity':ok}),flush=True)
            if not ok:raise ArithmeticError('implementation parity failed; parallel benchmark prohibited')
        r['serial']=records;r['speedup_original_over_numpy']=records[0]['wall_seconds']/records[1]['wall_seconds']
        r['speedup_original_over_native']=records[0]['wall_seconds']/records[2]['wall_seconds']
        start=time.perf_counter()
        with cf.ProcessPoolExecutor(max_workers=n,mp_context=mp.get_context('spawn')) as pool:rs=list(pool.map(evaluate,[('native',bank,native)]*n))
        wall=time.perf_counter()-start;passed=all(parity(x['arrays'],reference)[0] for x in rs)
        r['parallel']={'workers':n,'jobs':n,'wall_seconds_including_spawn':wall,'sum_worker_cpu_seconds':sum(x['cpu_seconds'] for x in rs),
            'effective_used_cores':sum(x['cpu_seconds'] for x in rs)/wall,'parity_pass':passed,
            'worker_timings':[{k:v for k,v in x.items() if k!='arrays'} for x in rs]}
        if not passed:raise ArithmeticError('parallel parity failed')
        r['status']='PERFORMANCE_PARITY_BENCHMARK_PASS';r['TP2A_geometry_scan_status']='NOT_RUN_BY_THIS_BENCHMARK'
    except BaseException as e:
        code=130 if isinstance(e,KeyboardInterrupt) else 3;r['status']='BENCHMARK_BLOCKED_OR_FAILED';r['first_failure']={'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    run_tp2a.finish(out,r);return code
if __name__=='__main__':raise SystemExit(main())
