"""Bounded actual-bank parity/reference and strict OpenMP microbenchmark."""
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import platform
import resource
import time
import numpy as np
from basis_representation import load_candidate,exact_coefficients,sha256,admitted_cpus

def timed(call,n=3):
    call()
    values=[]
    for _ in range(n):
        t=time.perf_counter();call();values.append(time.perf_counter()-t)
    return {'seconds':values,'median_seconds':float(np.median(values)),'min_seconds':min(values),'max_seconds':max(values)}

def run(candidate,native_manifest,out):
    if Path(out).exists():raise FileExistsError('validation result create-only')
    bank=load_candidate(candidate);native=load_candidate(candidate,'fortran',native_manifest,1)
    rng=np.random.default_rng(20261002)
    radii=np.concatenate([rng.uniform(0,70,4096),bank[0].edges,np.nextafter(bank[0].edges[1:],-np.inf),np.nextafter(bank[0].edges,np.inf)])
    parity=[];reference=[]
    for k,(py,ft) in enumerate(zip(bank,native)):
        a=py.evaluate(radii);b=ft.evaluate(radii)
        parity.append({'mode':k,'u_bitwise_equal':np.array_equal(a[0].view(np.uint64),b[0].view(np.uint64)),'du_bitwise_equal':np.array_equal(a[1].view(np.uint64),b[1].view(np.uint64)), 'max_u_difference':float(np.max(abs(a[0]-b[0]))),'max_du_difference':float(np.max(abs(a[1]-b[1])))})
        rows=exact_coefficients(py);errors=[];dererrors=[];scales=[];derscales=[]
        rr=np.concatenate([radii[:128],py.edges])
        got=py.evaluate(rr)
        for i,r in enumerate(rr):
            if r>=py.edges[-1]:u=du=Fraction(0);scale=dscale=1.
            else:
                e=int(np.searchsorted(py.edges,r,side='right')-1)
                h=Fraction.from_float(float(py.edges[e+1]))-Fraction.from_float(float(py.edges[e]))
                s=(Fraction.from_float(float(r))-Fraction.from_float(float(py.edges[e])))/h
                c=rows[e];u=sum(v*s**j for j,v in enumerate(c));du=sum(j*c[j]*s**(j-1) for j in range(1,5))/h
                scale=max(1.,sum(abs(float(x)) for x in c));dscale=max(1.,sum(j*abs(float(c[j])) for j in range(1,5))/float(h))
            errors.append(float(abs(Fraction.from_float(float(got[0][i]))-u)));dererrors.append(float(abs(Fraction.from_float(float(got[1][i]))-du)))
            scales.append(scale);derscales.append(dscale)
        eps=np.finfo(float).eps
        reference.append({'mode':k,'sample_count':len(rr),'max_u_absolute_error':max(errors),'max_du_absolute_error':max(dererrors),'max_u_error_over_64eps_coefficient_scale':max(np.array(errors)/(64*eps*np.array(scales))),'max_du_error_over_64eps_derivative_scale':max(np.array(dererrors)/(64*eps*np.array(derscales)))})
    if not all(x['u_bitwise_equal'] and x['du_bitwise_equal'] for x in parity):raise AssertionError('Python/Fortran serial parity failed')
    if not all(x['max_u_error_over_64eps_coefficient_scale']<=1 and x['max_du_error_over_64eps_derivative_scale']<=1 for x in reference):raise AssertionError('reference screen failed')
    # Exact SHA+range validation also covers direct public ctypes wrapper inputs.
    ft=native[0];invalid_count=0
    for cells,s,h in [(np.array([-1]),np.array([.5]),np.array([1.])),(np.array([40]),np.array([.5]),np.array([1.])),(np.array([0]),np.array([np.nan]),np.array([1.])),(np.array([0]),np.array([.5]),np.array([0.])),(np.array([0,1]),np.array([.5]),np.array([1.]))]:
        try:ft.native.evaluate(ft,cells,s,h,1)
        except ValueError:invalid_count+=1
        else:raise AssertionError('invalid direct native input accepted')
    workload=np.linspace(0.,64.,1000000,endpoint=False,dtype=np.float64)
    pytime=timed(lambda:bank[0].evaluate(workload))
    cells=np.searchsorted(bank[0].edges,workload,side='right')-1
    h=bank[0].edges[cells+1]-bank[0].edges[cells];s=(workload-bank[0].edges[cells])/h
    reference_u,reference_du=bank[0].evaluate(workload)
    baseline=None;bench=[]
    for threads in [x for x in (1,2,4,8) if x<=admitted_cpus()]:
        mode=load_candidate(candidate,'fortran',native_manifest,threads)[0]
        u,du=mode.evaluate(workload)
        equal=np.array_equal(u.view(np.uint64),reference_u.view(np.uint64)) and np.array_equal(du.view(np.uint64),reference_du.view(np.uint64))
        if not equal:raise AssertionError('thread-count parity failed')
        end=timed(lambda:mode.evaluate(workload));kernel=timed(lambda:mode.native.evaluate(mode,cells,s,h,threads))
        observed=mode.native.last_observed_threads
        if baseline is None:baseline=kernel['median_seconds']
        bench.append({'requested_threads':threads,'observed_threads':observed,'bitwise_equal_to_python':equal,'end_to_end':end,'prelocated_kernel_with_ctypes_and_validation':kernel,'end_to_end_speedup_vs_python':pytime['median_seconds']/end['median_seconds'],'kernel_speedup_vs_one_thread':baseline/kernel['median_seconds']})
    result={'schema':'BASS_R4X_EVALUATOR_VALIDATION_V1','decision':'PASS_LOCAL_EVALUATOR_ONLY','physical_calls':0,'production_adopted':False,'candidate_manifest_sha256':sha256(Path(candidate)/'CANDIDATE.json'),'native_manifest_sha256':sha256(native_manifest),'validation_source_sha256':sha256(__file__),'parity':parity,'exact_rational_reference':reference,'reference_screen':'64*eps*max(1,absolute coefficient sum), derivative coefficient/h sum; empirical screen not certified bound','direct_native_invalid_cases_rejected':invalid_count,'workload':{'points':len(workload),'modes':1,'radii_sha256':__import__('hashlib').sha256(workload.tobytes()).hexdigest(),'repetitions':3,'warmups_per_timing':1},'python_end_to_end':pytime,'fortran_benchmarks':bench,'environment':{'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'affinity':sorted(os.sched_getaffinity(0)),'admitted_cpus':admitted_cpus(),'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_max':Path('/sys/fs/cgroup/memory.max').read_text().strip(),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'OMP_DYNAMIC':os.environ.get('OMP_DYNAMIC'),'OMP_PROC_BIND':os.environ.get('OMP_PROC_BIND'),'OMP_PLACES':os.environ.get('OMP_PLACES')},'limits':['Local admitted host only; no MPI or NCP64 scaling claim.','End-to-end time includes Python allocation/location/gathering and identity validation.','Prelocated benchmark still includes ctypes, validation, output allocation; not pure kernel-cycle timing.','Parity/reference check does not certify full operator or trajectory.']}
    Path(out).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',required=True);p.add_argument('--native-manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    r=run(a.candidate,a.native_manifest,a.out);print(json.dumps({'decision':r['decision'],'benchmarks':r['fortran_benchmarks']}))
