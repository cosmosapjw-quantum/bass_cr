"""Integrated OpenMPI/Fortran synthetic work; exact C++ hash parity on rank0."""
from pathlib import Path
import argparse,hashlib,json,time,resource,os
import numpy as np
from mpi4py import MPI
from kernel import HPCMomentKernel
from synthetic_inputs import inputs
from mpi_queue import run_queue
from resource_profile import verify_rank_allocation,census
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',required=True);p.add_argument('--out',required=True);p.add_argument('--threads',type=int,default=1);p.add_argument('--tasks',type=int,default=24);p.add_argument('--synthetic-unbound',action='store_true',help='explicit test-only fallback when host denies CPU binding; never proves NCP affinity');a=p.parse_args()
    if not 1<=a.tasks<=1024:raise ValueError('synthetic task count1..1024')
    comm=MPI.COMM_WORLD;rank=comm.Get_rank()
    try:
        if a.synthetic_unbound:
            info=census();allowed={int(x) for x in os.environ['BASS_HPC_ADMITTED_CPUS'].split(',')}
            if not set(info['affinity_cpus'])<=allowed or comm.Get_size()*a.threads>info['usable_cpu_budget']:raise ValueError('synthetic unbound still requires total CPU admission and inherited allocation')
            binding={'ok':True,'affinity_cpus':info['affinity_cpus'],'slots':a.threads,'binding_verified':False,'mode':'EXPLICIT_UNBOUND_SYNTHETIC_ONLY'}
        else:binding={'ok':True,'binding_verified':True,**verify_rank_allocation(a.threads)}
    except Exception as e:binding={'ok':False,'error':str(e)}
    bindings=comm.allgather(binding)
    if not all(x['ok'] for x in bindings):raise RuntimeError('rank allocation failed before native load: '+str(bindings))
    masks=[set(x['affinity_cpus']) for x in bindings]
    if not a.synthetic_unbound and any(masks[i]&masks[j] for i in range(len(masks)) for j in range(i)):raise RuntimeError('overlapping rank affinity masks')
    kernel=HPCMomentKernel(a.build,threads=a.threads)
    tasks=[{'levels':[4096],'seed':1900+i} for i in range(a.tasks)] if rank==0 else None
    def worker(task,reserve):
        data=inputs(4096,9,9,seed=task['seed'],moving=True);reserve(0)
        result=kernel.accumulate(*data,real_coefficients=True)
        return {'seed':task['seed'],'sha256':hashlib.sha256(result.tobytes()).hexdigest()}
    comm.Barrier();start=time.perf_counter()
    result=run_queue(comm,tasks,worker,max_attempts=a.tasks,output_dir=a.out,timeout_seconds=180)
    elapsed=time.perf_counter()-start
    peak_rss=comm.gather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,root=0)
    if rank==0:
        reference=HPCMomentKernel(a.build,backend='reference');t0=time.perf_counter();expected=[]
        for task in tasks:
            x=reference.accumulate(*inputs(4096,9,9,seed=task['seed'],moving=True),real_coefficients=True)
            expected.append({'seed':task['seed'],'sha256':hashlib.sha256(x.tobytes()).hexdigest()})
        reference_seconds=time.perf_counter()-t0
        if result!=expected:raise AssertionError('integrated MPI result differs from serial strict C++')
        receipt={'schema':'BASS_HPC_INTEGRATED_MPI_BENCHMARK_V1','status':'PASS','ranks_including_coordinator':comm.Get_size(),'worker_ranks':max(1,comm.Get_size()-1),'omp_threads_per_rank':a.threads,'tasks':a.tasks,'all_result_hashes_match_reference':True,'queue_wall_seconds':elapsed,'serial_cpp_reference_wall_seconds':reference_seconds,'observed_speedup_including_queue_overhead':reference_seconds/elapsed,'physical_queries':0,'scope':'artificial ABI inputs; current local runtime only; not NCP64 or complete operator/transport performance','ordered_results':result}
        receipt['actual_rank_bindings']=bindings
        receipt['cpu_binding_verified']=not a.synthetic_unbound
        receipt['per_rank_peak_rss_bytes']=peak_rss
        receipt['sum_peak_rss_upper_estimate_bytes']=sum(peak_rss)
        (Path(a.out)/'MPI_KERNEL_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='ordered_results'}))
if __name__=='__main__':main()
