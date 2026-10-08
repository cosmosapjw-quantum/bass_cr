"""One-shot R4AF point pilot. No old solver, window jet, D or V entrypoint.

All source/input/native/output identities are checked BEFORE reserving an
attempt. Completed cell outputs are durable. A consumed attempt cannot resume
by silently reusing the contract; recovery requires a new explicit contract.
"""
from __future__ import annotations
import os,sys,json,time,hashlib,subprocess,resource,signal
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import numpy as np
from dyadic import I,ZERO,SCALE
from geometry import polygons
from provider import Candidate,prepare_cell,write_native
from quadrature import certified_rule,radius_l1_bound

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):
    path=Path(path);tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)
def fraction_upper(a):return str(F(I(a).hi,SCALE))

def validate_contract(c,authorization_path):
    auth=json.loads(Path(authorization_path).read_text())
    if auth['contract_sha256']!=sha(c):raise ValueError('outer contract pin')
    c=json.loads(Path(c).read_text())
    if c['schema']!='R4AF_POINT_EXECUTION_V1' or c['caps']!={'point_geometry':1,'window_jet':0,'Vother':0,'D':0,'attempts':1}:raise ValueError('scope/cap changed')
    if Path(c['output']).resolve()!=Path(auth['output']).resolve():raise ValueError('outer output pin')
    if Path(c['output']).exists():raise FileExistsError('consumed output/attempt')
    for p,h in auth['pins'].items():
        q=(ROOT/p).resolve()
        if ROOT not in q.parents or not q.is_file() or sha(q)!=h:raise ValueError('source/input/native pin: '+p)
    if c['candidate_identity']!='17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef':raise ValueError('candidate identity')
    if c['z']!='-32' or c['precision_bits']!=256 or c['rho']!='2':raise ValueError('unregistered geometry/arithmetic')
    if F(c['target_radius'])!=F(1,10**16) or F(c['quadrature_budget'])!=F(1,10**18):raise ValueError('posthoc accuracy change')
    if c['workers'] not in (1,2,3) or c['max_cells']>10000 or c['max_split_depth']>5:raise ValueError('resource profile')
    if c['degrees']!=[16,24,32,40,48,56,64]:raise ValueError('degree profile')
    aff=set(os.sched_getaffinity(0))
    if any(x not in aff for x in c['worker_cpu_ids']) or len(c['worker_cpu_ids'])!=c['workers']:raise ValueError('CPU affinity contract')
    q=Path('/sys/fs/cgroup/cpu.max').read_text().split()
    if q[0]!='max' and F(int(q[0]),int(q[1]))<c['workers']:raise ValueError('CPU quota')
    mem=Path('/sys/fs/cgroup/memory.max').read_text().strip()
    if mem!='max' and int(mem)<c['workers']*c['native_memory_bytes']+c['coordinator_and_reserve_bytes']:raise ValueError('memory admission')
    return c,auth

def radius(matrix):
    s=ZERO
    for pair in matrix:
        for x in pair:s=s+I(x.radius())**2
    return (2*s).sqrt().abs_upper()

def run(contract_path,auth_path):
    c,auth=validate_contract(contract_path,auth_path);out=Path(c['output']);out.mkdir(parents=False,exist_ok=False)
    start=time.monotonic();deadline=start+c['wall_seconds'];children=[]
    dump(out/'RESERVATION.json',{'contract_sha256':sha(contract_path),'authorization_sha256':sha(auth_path),'state':'STARTED','pid':os.getpid(),'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'caps':c['caps']})
    def budget():
        if time.monotonic()>deadline:raise TimeoutError('registered wall budget')
    try:
        cand=Candidate.load(ROOT/'inputs/CANDIDATE.npz',ROOT/'inputs/CANDIDATE.json')
        geo=json.loads((ROOT/'inputs/GEOMETRY.json').read_text())['geometry']
        z=F(float(geo['actual_z_a0']));v=F(float(geo['speed_a0_per_ta']));t=F(float(geo['time_ta']));b=F(2)
        if z!=F(-32):raise ValueError('actual z changed')
        R=I(b*b+z*z).sqrt();epoch=v*z/2-v*v*t/2
        tris=polygons(cand.edges,R)
        polygon_hash=hashlib.sha256(json.dumps([a.dump() for a in tris],sort_keys=True).encode()).hexdigest()
        if len(tris)!=1229 or polygon_hash!=c['parent_polygon_sha256']:raise ValueError('polygon equivalence failed')
        tasks=[];proof=[];hist=Counter();root_tol=F(c['quadrature_budget'])/len(tris)
        for ix,tri in enumerate(tris):
            queue=[((F(0),F(1),F(0),F(1)),0)]
            while queue:
                budget();box,level=queue.pop();tol=root_tol/4**level
                failure=None
                try:p=prepare_cell(cand,tri,b,z,v,R,epoch,box,tol,c['degrees'],F(c['rho']))
                except (ZeroDivisionError,OverflowError) as e:p=None;failure=str(e)
                if p is None:
                    if level>=c['max_split_depth']:raise ArithmeticError('analytic pole/degree cap at triangle '+str(ix)+' '+str(failure))
                    u0,u1,w0,w1=box;um=(u0+u1)/2;wm=(w0+w1)/2
                    queue.extend([((aa,bb,cc,dd),level+1) for aa,bb in [(u0,um),(um,u1)] for cc,dd in [(w0,wm),(wm,w1)]][::-1]);continue
                p['triangle']=tri;p['id']=len(tasks);p['parent_triangle']=ix;p['split_level']=level
                tasks.append(p);hist[p['n']]+=1
                if len(tasks)>c['max_cells']:raise ArithmeticError('cell cap')
                proof.append({'id':p['id'],'parent_triangle':ix,'split_level':level,'box':[str(x) for x in box],'n':p['n'],
                    'triangle':tri.dump(),'mu':[[fraction_upper(x) for x in r] for r in p['mu']],
                    'mw':[[fraction_upper(x) for x in r] for r in p['mw']],
                    'errors':[[fraction_upper(x) for x in r] for r in p['errors']],
                    'radius_l1_upper':fraction_upper(p['radius_upper']),'budget':str(tol)})
            if (ix+1)%64==0 or ix+1==len(tris):
                dump(out/'PROGRESS.json',{'phase':'ANALYTIC_COVER','triangles_completed':ix+1,'total':len(tris),'cells':len(tasks),'degree_histogram':dict(hist)})
                print('bounds',ix+1,len(tasks),dict(hist),flush=True)
        dump(out/'CELL_CERTIFICATES.json',{'rho':c['rho'],'polygon_sha256':polygon_hash,'tasks':proof,'complete_triangles':len(tris)})
        rules={n:certified_rule(n) for n in sorted(hist)};budget()
        dump(out/'GAUSS_RULES.json',{str(n):{'nodes':[x.dump() for x in a[0]],'weights':[x.dump() for x in a[1]],'root_brackets':a[2]} for n,a in rules.items()})
        input_path=out/'NATIVE_INPUT.txt';write_native(input_path,cand,b,z,v,R,epoch,rules,tasks)
        dump(out/'NATIVE_DISPATCH.json',{'input_sha256':sha(input_path),'executable_sha256':sha(ROOT/'source/native_cubature'),'cells':len(tasks),'quadrature_nodes':sum(p['n']**2 for p in tasks),'workers':c['workers'],'wall_remaining_seconds':deadline-time.monotonic(),'degree_histogram':dict(hist)})
        logs=[];env=os.environ.copy();env.update({'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
        def limits():
            resource.setrlimit(resource.RLIMIT_AS,(c['native_memory_bytes'],c['native_memory_bytes']))
            os.sched_setaffinity(0,{c['worker_cpu_ids'][worker]})
        for worker in range(c['workers']):
            stream=open(out/f'worker_{worker}.stderr','w');logs.append(stream)
            proc=subprocess.Popen([str(ROOT/'source/native_cubature'),str(input_path),str(out/f'worker_{worker}.intervals'),str(worker),str(c['workers'])],stdout=stream,stderr=stream,env=env,preexec_fn=limits)
            children.append(proc)
        while any(p.poll() is None for p in children):
            budget();time.sleep(1)
            if any(p.poll() is not None and p.returncode!=0 for p in children):raise RuntimeError('native worker failed')
        for f in logs:f.close()
        if any(p.returncode!=0 for p in children):raise RuntimeError('native exit status')
        cells={}
        for worker in range(c['workers']):
            lines=(out/f'worker_{worker}.intervals').read_text().splitlines();seen=0
            for line in lines:
                a=line.split()
                if a[0]=='DONE':
                    if int(a[1])!=seen:raise ValueError('native DONE count')
                    continue
                if a[0]!='CELL' or len(a)!=326:raise ValueError('native result shape')
                idx=int(a[1]);vals=[I.raw(int(a[j]),int(a[j+1])) for j in range(2,len(a),2)]
                if idx in cells or idx% c['workers']!=worker:raise ValueError('duplicate/mispartitioned cell')
                cells[idx]=[(vals[k],vals[k+1]) for k in range(0,162,2)];seen+=1
            if not lines or not lines[-1].startswith('DONE '):raise ValueError('incomplete native output')
        if sorted(cells)!=list(range(len(tasks))):raise ValueError('missing cell result')
        raw=[(ZERO,ZERO) for _ in range(81)];errs=[ZERO for _ in range(81)]
        for idx,p in enumerate(tasks):
            for k in range(81):
                r,i=raw[k];rr,ii=cells[idx][k];raw[k]=(r+rr,i+ii);errs[k]=errs[k]+p['errors'][k//9][k%9]
        enclosed=[]
        for (r,i),e in zip(raw,errs):
            s=I.raw(-e.hi,e.hi);enclosed.append((r+s,i+s))
        rad=radius(enclosed);rrad=radius(raw);analytic=2*sum(errs,ZERO)
        # Compare saved arrays only after sealing the new S-only enclosure.
        dump(out/'S_ENCLOSURE.json',{'candidate':cand.identity,'geometry_sha256':sha(ROOT/'inputs/GEOMETRY.json'),'R':R.dump(),'epoch_offset':str(epoch),'matrix_shape':[9,9],
             'entries':[{'re':r.dump(),'im':i.dump()} for r,i in enclosed],'raw_quadrature_entries':[{'re':r.dump(),'im':i.dump()} for r,i in raw],
             'analytic_component_errors':[e.dump() for e in errs],'full_cross_radius_upper':fraction_upper(rad),'native_arithmetic_radius_upper':fraction_upper(rrad),
             'analytic_full_cross_L1_upper':fraction_upper(analytic)})
        dump(out/'S_ONLY_SEAL.json',{'file':'S_ENCLOSURE.json','sha256':sha(out/'S_ENCLOSURE.json'),'D_read':False})
        saved=np.load(ROOT/'inputs/S.npy',allow_pickle=False)
        if saved.shape!=(18,18) or not np.isfinite(saved).all():raise ValueError('saved S shape')
        ds=ZERO
        for i in range(9):
            for j in range(9):
                re,im=enclosed[i*9+j]
                # Do not assume separately stored TP/PT were projected.
                for value,sign in [(saved[i,j+9],1),(saved[j+9,i],-1)]:
                    dr=(re-I(F(float(value.real)))).abs_upper();di=(im*sign-I(F(float(value.imag)))).abs_upper();ds=ds+dr*dr+di*di
        saved_error=ds.sqrt().abs_upper();target=F(c['target_radius']);met=F(rad.hi,SCALE)<=target
        result={'schema':'R4AF_POINT_RESULT_V1','status':'HIGH_ORDER_POINT_ENCLOSURE_TARGET_MET' if met else 'VALID_ENCLOSURE_POINT_TARGET_NOT_MET','candidate':cand.identity,
                'scope':'same finite 18-channel s+p candidate, one exact stored z=-32/time geometry; not shifted stencil samples',
                'full_cross_radius_upper':fraction_upper(rad),'native_arithmetic_radius_upper':fraction_upper(rrad),'analytic_full_cross_L1_upper':fraction_upper(analytic),
                'saved_S_absolute_error_upper':fraction_upper(saved_error),'target_radius':str(target),'target_met':met,'triangle_count':len(tris),'cell_count':len(tasks),
                'degree_histogram':dict(hist),'quadrature_evaluations':sum(p['n']**2 for p in tasks),'point_geometry':1,'window_jet':0,'Vother':0,'D':0,'old_solver_calls':0,'historical_replays':0,
                'parent_M9_recomputed':False,'parent_M9_source_sha256':sha(ROOT/'evidence/R4AE_WINDOW_JET.json'),'parent_result_sha256':sha(ROOT/'evidence/R4AE_RESULT.json'),
                'wall_seconds':time.monotonic()-start,'coordinator_maxRSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'native_maxRSS_KiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO','full_stencil_total_upper':None}
        dump(out/'RESULT.json',result);dump(out/'COMPLETED.json',{'result_sha256':sha(out/'RESULT.json'),'state':'COMPLETE','all_native_exit_zero':True});print(json.dumps(result,indent=2),flush=True)
    except BaseException as e:
        for p in children:
            if p.poll() is None:p.terminate()
        dump(out/'FAILURE.json',{'type':type(e).__name__,'message':str(e),'elapsed':time.monotonic()-start,'partial_outputs_preserved':True,'automatic_retry':False});raise

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('run_pilot.py CONTRACT AUTHORIZATION')
    run(sys.argv[1],sys.argv[2])
