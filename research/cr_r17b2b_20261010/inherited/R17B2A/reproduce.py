"""Verify pinned sources; optionally reproduce only the NEW R17B2A diagnostics."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    m=json.loads((ROOT/'MANIFEST.json').read_text())
    for name,row in m['files'].items():
        p=ROOT/name
        if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:raise ValueError('PACKAGE_IDENTITY:'+name)
    s=json.loads((ROOT/'SOURCE_BINDING.json').read_text())
    for row in s['selected']:
        if sha(ROOT/row['local'])!=row['sha256']:raise ValueError('DONOR_IDENTITY:'+row['local'])
    return len(m['files'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
    print('MANIFEST',verify(),flush=True)
    if a.verify_only:return
    if not a.output: p.error('--output required unless --verify-only')
    a.output.mkdir(parents=True,exist_ok=False)
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
    cmds=[('UNIT',[sys.executable,'-B','-m','unittest','discover','-s','tests','-v']),
          ('SCIENCE',[sys.executable,'-B','run_research.py','--output',str(a.output/'science')]),
          ('INDEPENDENT',[sys.executable,'-B','independent_check.py','--input',str(a.output/'science'),'--output',str(a.output/'science/INDEPENDENT.json')]),
          ('ACCEPT',[sys.executable,'-B','accept_results.py',str(a.output/'science')])]
    runs=[]
    for name,cmd in cmds:
        t=time.time();r=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=40)
        record={'argv':cmd,'exit':r.returncode,'wall_s':time.time()-t,'stdout':r.stdout,'stderr':r.stderr}
        (a.output/(name+'_RUN.json')).write_text(json.dumps(record,indent=2)+'\n');runs.append(record)
        if r.returncode:raise RuntimeError(name+': '+r.stderr[-4000:])
    compared=[]
    for name in ['RESPONSE.json','BASE_SAMPLES.json','ADJOINT_BOUNDARIES.json','INDEPENDENT.json','CHECKS.json']:
        match=sha(a.output/'science'/name)==sha(ROOT/'results/final'/name)
        compared.append({'file':name,'byte_equal':match})
        if not match:raise ValueError('NUMERICAL_REPRODUCTION_CHANGED:'+name)
    (a.output/'RECONCILIATION.json').write_text(json.dumps({'status':'PASS','files':compared,'parent_science_suites_replayed':False},indent=2)+'\n')
    print('PASS',json.dumps(compared),flush=True)
if __name__=='__main__':main()
