"""Same-input local kernel benchmark; does not claim NCP/end-to-end speedup."""
from pathlib import Path
import argparse,hashlib,json,os,statistics,time
import numpy as np
from kernel import HPCMomentKernel
from synthetic_inputs import inputs
from resource_profile import census
def run(directory,out,threads=(1,2,4),repeat=7,calls=10):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[];data=inputs(1024,9,9,moving=True)
    ref=HPCMomentKernel(directory,backend='reference');expected=ref.accumulate(*data,real_coefficients=True)
    for backend,t in [('reference',1),*[('fortran',t) for t in threads]]:
        k=HPCMomentKernel(directory,backend=backend,threads=t);actual=k.accumulate(*data,real_coefficients=True)
        np.testing.assert_array_equal(actual.view(np.uint64),expected.view(np.uint64))
        times=[]
        for _ in range(repeat):
            start=time.perf_counter()
            for _ in range(calls):k.accumulate(*data,real_coefficients=True)
            times.append((time.perf_counter()-start)/calls)
        rows.append({'backend':backend,'threads':t,'seconds_median':statistics.median(times),'seconds_samples':times,'bitwise_reference_equal':True})
    baseline=rows[0]['seconds_median']
    for x in rows:x['speedup_vs_strict_cpp']=baseline/x['seconds_median']
    result={'schema':'BASS_HPC_SYNTHETIC_KERNEL_BENCHMARK_V1','status':'PASS','scope':'same artificial 1024-point9x9 moving-target kernel inputs including Python wrapper; not physical B0 or NCP64 scaling','census':census(),'repeat':repeat,'calls_per_repeat':calls,'rows':rows,'physical_queries':0,'result_sha256':hashlib.sha256(expected.tobytes()).hexdigest(),'floating_acceptance':'bitwise equality to unchanged C++ source compiled with same strict FP policy','build':json.loads((Path(directory)/'BUILD_HPC.json').read_text())}
    (out/'BENCHMARK.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',required=True);p.add_argument('--out',required=True);p.add_argument('--threads',default='1,2,4');a=p.parse_args();print(json.dumps(run(a.build,a.out,tuple(map(int,a.threads.split(',')))),indent=2))
