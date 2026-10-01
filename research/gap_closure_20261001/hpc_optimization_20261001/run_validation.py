"""Build and validate the new HPC lane only; no physical B0 calls."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time
from resource_profile import census,plan
HERE=Path(__file__).resolve().parent
def run(out,fc,native_arch=False,synthetic_unbound=False):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);info=census();rows=[]
    if min(info['usable_cpu_budget'],info['physical_cores'])<4:raise RuntimeError('full bounded validation requires4 admitted physical cores; no PASS with skipped MPI paths')
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_MAX_ACTIVE_LEVELS='1',PYTHONDONTWRITEBYTECODE='1')
    if os.geteuid()==0:env.update(OMPI_ALLOW_RUN_AS_ROOT='1',OMPI_ALLOW_RUN_AS_ROOT_CONFIRM='1')
    def step(name,args):
        start=time.monotonic();r=subprocess.run(args,cwd=HERE,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(name+'.log')).write_text(r.stdout);rows.append({'name':name,'command':args,'exit_code':r.returncode,'wall_seconds':time.monotonic()-start})
        if r.returncode:raise RuntimeError(name+' failed; first log retained')
        return r.stdout
    status='FAILED';failure=None;count=None
    try:
        cmd=[sys.executable,str(HERE/'build_native.py'),'--out',str(out/'build'),'--fc',fc]
        if native_arch:cmd.append('--native-arch')
        step('build',cmd);env['BASS_HPC_BUILD']=str(out/'build')
        log=step('tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py','-v'])
        count=int(re.search(r'Ran (\d+) tests',log).group(1))
        if 'skipped=' in log:raise RuntimeError('skipped tests cannot establish HPC validation')
        threads=','.join(str(t) for t in [1,2,4,8] if t<=info['usable_cpu_budget'])
        step('kernel_benchmark',[sys.executable,str(HERE/'benchmark_kernel.py'),'--build',str(out/'build'),'--out',str(out/'benchmark'),'--threads',threads])
        hybrid_threads=2 if min(info['usable_cpu_budget'],info['physical_cores'])>=8 else 1
        launch=plan(info,4,hybrid_threads,.25,program=[sys.executable,str(HERE/'mpi_kernel_benchmark.py'),'--build',str(out/'build'),'--out',str(out/'mpi_kernel'),'--threads',str(hybrid_threads)])
        version=subprocess.check_output(['mpirun','--version'],text=True);match=re.search(r'(?:Open MPI|OpenRTE)\)?\s+(\d+)\.',version)
        if not match:raise RuntimeError('OpenMPI runtime required')
        btl='sm' if int(match.group(1))>=5 else 'vader'
        cmd=launch['argv'];cmd[1:1]=['--mca','pml','ob1','--mca','btl','self,'+btl]
        if synthetic_unbound:
            cmd[cmd.index('--bind-to')+1]='none';cmd[cmd.index('--map-by')+1]='slot';cmd.append('--synthetic-unbound')
            cmd=[('OMP_PROC_BIND=FALSE' if x=='OMP_PROC_BIND=close' else x) for x in cmd]
        step('mpi_kernel',cmd);status='PASS'
    except Exception as e:failure={'type':type(e).__name__,'message':str(e)}
    result={'schema':'BASS_R4S_HPC_VALIDATION_V1','status':status,'first_failure':failure,'tests':count,'skipped':0 if status=='PASS' else None,'steps':rows,'census':info,'physical_queries':0,'physical_transport_runs':0,'synthetic_native_calls_performed':True,'ncp64_scaling_measured':False,'cpu_binding_verified':status=='PASS' and not synthetic_unbound,'sources':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}}
    (out/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','tests','skipped','first_failure']}));return 0 if status=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--fc',default=os.getenv('FC','gfortran'));p.add_argument('--native-arch',action='store_true');p.add_argument('--synthetic-unbound',action='store_true');a=p.parse_args();raise SystemExit(run(a.out,a.fc,a.native_arch,a.synthetic_unbound))
