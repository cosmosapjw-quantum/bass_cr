"""One-shot, source-bound weak-K reference pilot (not run on atomic data here).

Use `prepare` on the execution host. Approval of that exact contract is separate.
The default request covers ONE matrix entry at ONE geometry, never a full-state
or capture claim. Failed/partial output is preserved and cannot be auto-reused.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,sys,time,traceback
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
sys.path.insert(0,str(ROOT/'source'))
from weak_kernel import Candidate,Context,cover
from cubature import Budget,entry_enclosure,scalar_dump
from dyadic import I

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    with open(p,'x') as f:json.dump(x,f,indent=2,sort_keys=True)
def observe():
    from fractions import Fraction
    def read(p):return Path(p).read_text().strip()
    limit=read('/sys/fs/cgroup/memory.max');current=int(read('/sys/fs/cgroup/memory.current'))
    info=dict(x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines())
    host=int(info['MemAvailable'].split()[0])*1024
    avail=host if limit=='max' else min(host,int(limit)-current)
    q,p=read('/sys/fs/cgroup/cpu.max').split();cpu=len(os.sched_getaffinity(0)) if q=='max' else min(len(os.sched_getaffinity(0)),float(Fraction(int(q),int(p))))
    return {'platform':platform.platform(),'python':sys.version,'python_executable':sys.executable,'python_sha256':sha(sys.executable),'available_bytes':avail,'cpu_quota':cpu,'affinity':sorted(os.sched_getaffinity(0)),'fixture':False,'dependencies':{name:__import__(name).__version__ for name in ('numpy','scipy','mpmath')}}
def pins():
    ps=sorted((ROOT/'source').glob('*.py'))+sorted((ROOT/'vendor').glob('*.py'))+[ROOT/'inputs/CANDIDATE.json',ROOT/'inputs/CANDIDATE.npz',ROOT/'inputs/ANCHOR_GEOMETRY.json']
    return {str(p.relative_to(ROOT)):sha(p) for p in ps}

def validate(c,contract_path,output,approval):
    if c['schema']!='R4AM_REFERENCE_PILOT_V1' or sha(contract_path)!=approval:raise ValueError('exact contract approval mismatch')
    if c['source_root']!=str(ROOT) or c['output']!=str(Path(output).resolve()):raise ValueError('root/output binding mismatch')
    if c['source_input_pins']!=pins():raise ValueError('source/input identity changed')
    if c['units']!={'length':'a0','time':'ta','energy':'Eh','hbar_numeric':'1'}:raise ValueError('unit convention mismatch')
    if c['scope']!='ONE_GEOMETRY_ONE_ENTRY_REFERENCE' or c['automatic_expansion']:raise ValueError('scope expansion prohibited')
    if c['entry']!=[0,0,0,0]:raise ValueError('this contract authorizes selected 1s entry only')
    if c['max_geometry']!=1 or c['attempt_cap']!=1 or c['method']['degree']!=32 or c['method']['rho']!='2':raise ValueError('registered method/scope changed')
    if c['method']['absolute_target_Eh']!='1/10000000000000000':raise ValueError('target changed')
    if c['method']['max_depth']!=6 or c['resource']['max_evaluations']!=3000000 or c['resource']['wall_seconds']!=1800:raise ValueError('resource/method budget changed')
    if c['resource']['minimum_available_bytes']!=2415919104 or c['resource']['minimum_cpu_quota']!=2:raise ValueError('admission policy changed')
    if c['environment'].get('fixture') is not False:raise ValueError('test fixture cannot authorize atomic execution')
    g=json.loads((ROOT/'inputs/ANCHOR_GEOMETRY.json').read_text())['geometry']
    expected={k:str(F(float(x))) for k,x in {'b':2,'z':g['actual_z_a0'],'v':g['speed_a0_per_ta'],'t':g['time_ta']}.items()}
    if c['context']!=expected:raise ValueError('actual geometry/epoch changed')
    if Path(output).exists():raise FileExistsError('consumed output/attempt')
    e=observe()
    if e['python_sha256']!=c['environment']['python_sha256'] or e['platform']!=c['environment']['platform'] or e['dependencies']!=c['environment']['dependencies']:raise ValueError('runtime identity changed')
    if e['available_bytes']<c['resource']['minimum_available_bytes'] or e['cpu_quota']<c['resource']['minimum_cpu_quota']:raise RuntimeError('actual resource admission failed')
    return e

def prepare(path,output):
    g=json.loads((ROOT/'inputs/ANCHOR_GEOMETRY.json').read_text())['geometry']
    p=Path(path);out=Path(output).resolve()
    if p.exists() or out.exists():raise FileExistsError('create-only contract/output')
    c={'schema':'R4AM_REFERENCE_PILOT_V1','source_root':str(ROOT),'output':str(out),'source_input_pins':pins(),'environment':observe(),
       'scope':'ONE_GEOMETRY_ONE_ENTRY_REFERENCE','entry':[0,0,0,0],'max_geometry':1,'attempt_cap':1,'automatic_expansion':False,
       'units':{'length':'a0','time':'ta','energy':'Eh','hbar_numeric':'1'},
       'context':{k:str(F(float(x))) for k,x in {'b':2,'z':g['actual_z_a0'],'v':g['speed_a0_per_ta'],'t':g['time_ta']}.items()},
       'method':{'degree':32,'rho':'2','absolute_target_Eh':'1/10000000000000000','max_depth':6},
       'resource':{'minimum_available_bytes':2415919104,'minimum_cpu_quota':2,'wall_seconds':1800,'max_evaluations':3000000},
       'approval_created':False,'production':'HOLD'}
    p.parent.mkdir(parents=True,exist_ok=True);write(p,c)
    print(json.dumps({'contract':str(p),'sha256':sha(p),'science_evaluations':0,'authorization':'NOT_CREATED'}))

def execute(path,output,approval):
    c=json.loads(Path(path).read_text());env=validate(c,path,output,approval)
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    write(out/'RESERVATION.json',{'contract_sha256':sha(path),'environment':env,'time':time.time(),'attempt':1})
    start=time.monotonic();budget=Budget(c['resource']['max_evaluations'],start+c['resource']['wall_seconds'])
    try:
        ctx=Context(**{k:F(v) for k,v in c['context'].items()});candidate=Candidate.load(ROOT/'inputs/CANDIDATE.npz',ROOT/'inputs/CANDIDATE.json')
        cells,coverage=cover(candidate,ctx.R);write(out/'COVER.json',coverage)
        checkpoint=out/'CELLS.jsonl'
        with open(checkpoint,'x') as f:
            def save(rec):f.write(json.dumps(rec,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
            r=entry_enclosure(candidate,cells,ctx,tuple(c['entry']),absolute_target=F(c['method']['absolute_target_Eh']),degree=32,rho=F(2),max_depth=6,budget=budget,checkpoint=save)
        r.pop('cell_records');r['values']={k:scalar_dump(v) for k,v in r['values'].items()};r['radius_upper']=r['radius_upper'].dump()
        r.update({'candidate':candidate.identity,'wall_seconds':time.monotonic()-start,'contract_sha256':sha(path),'production':'HOLD','full18_K_certificate':False,'physical_bridge_upper':None,'full_stencil_total_upper':[None,None]})
        write(out/'RESULT.json',r);write(out/'COMPLETED.json',{'result_sha256':sha(out/'RESULT.json'),'target_met':r['target_met']})
    except Exception as exc:
        write(out/'FAILURE.json',{'exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'wall_seconds':time.monotonic()-start,'evaluations':budget.evaluations,'automatic_retry':False});raise
    finally:
        write(out/'RETURN_MANIFEST.json',{'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()},'science_scope':'single-entry pilot only'})

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='command',required=True)
    p=sp.add_parser('prepare');p.add_argument('--contract',required=True);p.add_argument('--output',required=True)
    r=sp.add_parser('run');r.add_argument('--contract',required=True);r.add_argument('--output',required=True);r.add_argument('--approve-sha256',required=True)
    args=ap.parse_args()
    if args.command=='prepare':prepare(args.contract,args.output)
    else:execute(args.contract,args.output,args.approve_sha256)
if __name__=='__main__':main()
