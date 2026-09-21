"""Host execution recorder; does not alter physics or run b grids."""
import os,sys,json,time,hashlib,subprocess,threading,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
 return h.hexdigest()
def main():
 name,limit,*args=sys.argv[1:]; limit=float(limit)
 out=ROOT/'runs'/name; out.mkdir(exist_ok=False)
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',CUDA_PATH='/usr/local/cuda-12.8',CUDA_HOME='/usr/local/cuda-12.8',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONUNBUFFERED='1')
 env['LD_LIBRARY_PATH']='/home/cosmosapjw/cosmo_lab/.venv/lib/python3.12/site-packages/nvidia/cufft/lib:'+env.get('LD_LIBRARY_PATH','')
 config=None
 with (out/'environment.json').open('w') as ef:
  subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'environment_receipt.py')],env=env,stdout=ef,check=True)
 if '--config' in args:
  p=Path(args[args.index('--config')+1]);p= p if p.is_absolute() else SRC/p
  data=p.read_bytes(); (out/'config.json').write_bytes(data);config=digest(p)
  args[args.index('--config')+1]=str(out/'config.json')
 args=[x.replace('{OUT}',str(out)) for x in args]
 cmd=[str(ROOT/'.venv/bin/python'),*args]
 hashes={str(p.relative_to(SRC)):digest(p) for folder in ('cr_repro','vendor_w1r') for p in (SRC/folder).glob('*.py')}
 rec={'name':name,'argv':cmd,'cwd':str(SRC),'config_sha256':config,'code_hashes':hashes,'code_digest':hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),'environment_receipt':'environment.json','runner_sha256':digest(Path(__file__)),'entrypoint_hashes':{str(Path(a)):digest(Path(a)) for a in args if Path(a).is_file()},'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limit_seconds':limit,'status':'RUNNING'}
 (out/'receipt.json').write_text(json.dumps(rec,indent=2))
 start=time.monotonic();stop=threading.Event(); samples=[]
 with (out/'stdout.txt').open('xb') as stdout,(out/'stderr.txt').open('xb') as stderr:
  p=subprocess.Popen(['/usr/bin/time','-v','-o',str(out/'resource.txt'),*cmd],cwd=SRC,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
  rec['wrapper_pid']=p.pid;(out/'receipt.json').write_text(json.dumps(rec,indent=2))
  def monitor():
   while not stop.wait(2):
    try:
     r=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=3)
     owned=[]
     for line in r.stdout.splitlines():
      fields=line.split(',')
      try:
       if os.getpgid(int(fields[0]))==p.pid: owned.append({'pid':int(fields[0]),'MiB':int(fields[1])})
      except (ValueError,ProcessLookupError,PermissionError):pass
     sample={'elapsed':time.monotonic()-start,'gpu_processes':r.stdout.strip(),'owned':owned};samples.append(sample)
     with (out/'gpu_memory_samples.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
    except Exception:pass
  t=threading.Thread(target=monitor,daemon=True);t.start()
  try:code=p.wait(timeout=limit);status='PASS' if code==0 else 'FAILED'
  except subprocess.TimeoutExpired:
   import signal
   os.killpg(p.pid,signal.SIGTERM)
   try:code=p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait()
   status='TIMEOUT_ABORTED'
  finally:stop.set();t.join(timeout=4)
 rec.update(status=status,exit_code=code,wall_seconds=time.monotonic()-start,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 rec['output_hashes']={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='receipt.json'}
 (out/'receipt.json').write_text(json.dumps(rec,indent=2))
 if status!='PASS':
  with (ROOT/'receipts/failure_ledger.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 print(json.dumps({'name':name,'status':status,'wall_seconds':rec['wall_seconds'],'path':str(out)}),flush=True)
 return 0 if status=='PASS' else 1
if __name__=='__main__':sys.exit(main())
