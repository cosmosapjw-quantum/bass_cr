import json,sys,platform,os,importlib.metadata,subprocess,datetime
r={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'environment':{k:os.environ.get(k) for k in ['CUDA_PATH','LD_LIBRARY_PATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE']}}
for key,cmd in [('nvidia_smi',['nvidia-smi']),('memory',['free','-b']),('cpu',['lscpu'])]:
 p=subprocess.run(cmd,capture_output=True,text=True);r[key]={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
try:
 import cupy as cp
 r['cupy']={'version':cp.__version__,'device_count':cp.cuda.runtime.getDeviceCount(),'cuda_runtime':cp.cuda.runtime.runtimeGetVersion(),'cuda_driver':cp.cuda.runtime.driverGetVersion()}
except Exception as e:r['cupy']={'status':'UNAVAILABLE','error':repr(e)}
print(json.dumps(r,indent=2))
