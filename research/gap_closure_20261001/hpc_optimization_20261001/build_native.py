"""Build separate strict-FP reference and Fortran candidates; no science run."""
from pathlib import Path
import argparse, hashlib, json, os, platform, shutil, subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
REFERENCE=REPO/'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/moment_kernel.cpp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(out,*,fc='gfortran',cxx='g++',native_arch=False):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    compilers={k:shutil.which(v) for k,v in [('fc',fc),('cxx',cxx)]}
    if not all(compilers.values()):raise RuntimeError('Fortran and C++ compilers required; no build claimed')
    common=['-O3','-fPIC','-shared','-fno-fast-math','-ffp-contract=off']
    if native_arch:common+=['-march=native']
    cmds=[([compilers['cxx'],*common,'-std=c++17',str(REFERENCE),'-o',str(out/'libreference.so')],'reference'),
          ([compilers['fc'],*common,'-fopenmp','-fprotect-parens','-ffree-line-length-none','-fopt-info-vec-optimized='+str(out/'VECTORIZATION.txt'),str(HERE/'native/moment_kernel_real.f90'),'-o',str(out/'libmoments_f90.so')],'fortran')]
    rows=[]
    for cmd,name in cmds:
        r=subprocess.run(cmd,cwd=out,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(name+'_build.log')).write_text(r.stdout);rows.append({'name':name,'command':cmd,'exit_code':r.returncode})
        if r.returncode:raise RuntimeError(name+' build failed; log retained')
    receipt={'schema':'BASS_HPC_STRICT_BUILD_V1','machine':platform.machine(),'system':platform.system(),'native_arch':native_arch,
             'source_hashes':{'reference':sha(REFERENCE),'fortran':sha(HERE/'native/moment_kernel_real.f90')},
             'libraries':{n:sha(out/n) for n in ['libreference.so','libmoments_f90.so']},'builds':rows,
             'compiler_versions':{k:subprocess.check_output([v,'--version'],text=True).splitlines()[0] for k,v in compilers.items()},
             'physical_admission':False,'numerical_parity_status':'NOT_YET_RUN','old_context_reuse':False}
    (out/'BUILD_HPC.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--fc',default=os.getenv('FC','gfortran'));p.add_argument('--cxx',default=os.getenv('CXX','g++'));p.add_argument('--native-arch',action='store_true');a=p.parse_args();print(json.dumps(build(a.out,fc=a.fc,cxx=a.cxx,native_arch=a.native_arch),indent=2))
