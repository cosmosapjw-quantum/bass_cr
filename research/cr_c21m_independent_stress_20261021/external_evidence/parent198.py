#!/usr/bin/env python3
"""Additive collisionless LRS pilot; frozen PR147 source remains in vendor/."""
from __future__ import annotations
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_key]='1'
import argparse, contextlib, csv, hashlib, json, math, multiprocessing as mp
from pathlib import Path
import sys,time,traceback
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss,legvander
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'))
from canonical_fv import CanonicalMomentumFV,CanonicalFVSpecies
from lrs_boltzmann import SourceLock,legendre_matrix
FM=.1
RTOL=3e-11
ATOL=3e-13
SAMPLES=65
WORKER=None

def dump(path,value):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)

def source_lock():
    lock=json.loads((HERE/'vendor/REI_BACKGROUND_FAMILY_LOCK.json').read_text())
    c=lock['cosmology'];t=lock['clock']
    return SourceLock(c['H0_per_s'],c['Omega_m'],c['Omega_r'],c['Omega_lambda'],t['a_ref'],t['a_end'])

def model_identity():
    files=['pilot.py','SOURCE_ATTRIBUTION.json']+['vendor/'+p.name for p in sorted((HERE/'vendor').glob('*')) if p.is_file()]
    return {p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in files}

class Reduced:
    def __init__(self,L=8):
        self.src=source_lock(); self.L=L
        self.momentum=CanonicalMomentumFV(30.,0.,24,12,gauss_order=3)
        self.mat=legendre_matrix(L,power=4)[::2,::2].copy()
        self.mat.flags.writeable=False
        self.mpref=FM*self.src.omega_m/self.src.aref**3
        mu,_=leggauss(128)
        self.brightness_basis=(legvander(mu,L)[:,::2]*np.arange(1,2*L+2,4)).T
        self.brightness_basis.flags.writeable=False
    def initial(self,sigma,pi_signed,sign):
        src=self.src;m=self.momentum.moments(0.,0.)
        base_h2=src.h0**2*((1-FM)*src.omega_m/src.aref**3+self.mpref*m.rho+src.omega_r/src.aref**4+src.omega_lambda)
        q=sign*sigma/math.sqrt(3-sigma*sigma)*math.sqrt(base_h2)/src.href if sigma else 0.
        h2=base_h2+(src.href*q)**2
        target_p=pi_signed*h2/(math.sqrt(3)*3*src.h0**2)
        k=15*(target_p-self.mpref*m.pi_s)/(src.omega_r/src.aref**4)
        if not math.isfinite(k) or abs(k)>.5:raise ValueError('UNREALIZABLE_K:'+str(k))
        y=np.zeros(3+(self.L//2+1));y[2]=q;y[3]=1.;y[4]=k/5
        d=self.diagnostics(np.array([0.]),y[:,None])
        err=max(abs(d['Sigma'][0]-sigma),abs(d['signed_Pi'][0]-pi_signed))
        if err>1e-12:raise ArithmeticError('INITIAL_PHYSICAL_AXIS:'+str(err))
        return y,{'q':q,'k':k,'axis_error':float(err),'realized_Sigma':float(d['Sigma'][0]),'realized_signed_Pi':float(d['signed_Pi'][0])}
    def rhs(self,x,y):
        src=self.src;a=src.aref*math.exp(x);m=self.momentum.moments(x,float(y[1]))
        r=src.omega_r/a**4
        h=math.sqrt(src.h0**2*((1-FM)*src.omega_m/a**3+self.mpref*m.rho+r*y[3]+src.omega_lambda)+(src.href*y[2])**2)
        shear=src.href*y[2]/h
        p=r*y[4]/3+self.mpref*m.pi_s
        z=np.empty_like(y);z[0]=src.href/h;z[1]=shear
        z[2]=-3*y[2]+3*src.h0**2*p/(src.href*h)
        z[3:]=shear*(self.mat@y[3:])
        return z
    def diagnostics(self,x,y):
        src=self.src;a=src.aref*np.exp(x);m=self.momentum.moment_batch(x,y[1])
        r=src.omega_r/a**4;s=src.href*y[2]
        h=np.sqrt(src.h0**2*((1-FM)*src.omega_m/a**3+self.mpref*m[:,0]+r*y[3]+src.omega_lambda)+s*s)
        p=r*y[4]/3+self.mpref*(m[:,2]-m[:,1])/3
        signed_pi=math.sqrt(3)*3*src.h0**2*p/(h*h)
        d={'x':x,'zbar':1/a-1,'elapsed_seconds':y[0]/src.href,'b':y[1], 's_over_H':s/h,'Sigma':math.sqrt(3)*abs(s)/h,
            'signed_Pi':signed_pi,'Pi':abs(signed_pi),'H_per_s':h,'E0':y[3],'E2':y[4],
            'massive_rho_norm':m[:,0],'massive_pi_s_norm':(m[:,2]-m[:,1])/3,
            'sampled_min_angular_brightness':np.min(y[3:].T@self.brightness_basis,axis=1)}
        if not all(np.isfinite(v).all() for v in d.values()) or np.any(h<=0) or np.any(y[3]<=0):raise ArithmeticError('NONPOSITIVE_NONFINITE_ENERGY_H')
        return d
    def solve(self,sigma,pi_signed,sign,rtol=RTOL,atol=ATOL):
        y,initial=self.initial(sigma,pi_signed,sign);start=time.monotonic()
        sol=solve_ivp(self.rhs,(0,self.src.xmax),y,method='DOP853',rtol=rtol,atol=atol,t_eval=np.linspace(0,self.src.xmax,SAMPLES))
        wall=time.monotonic()-start
        if not sol.success:raise RuntimeError(sol.message)
        d=self.diagnostics(sol.t,sol.y)
        meta={'initial':initial,'nfev':int(sol.nfev),'solve_wall_s':wall,'state_count':len(y),'min_massive_cell_population':float(self.momentum.cell_numbers.min()),
              'minimum_sampled_angular_brightness':float(d['sampled_min_angular_brightness'].min()),
              'endpoint':{k:float(d[k][-1]) for k in ('Sigma','Pi','signed_Pi','s_over_H','b','E0','E2')}}
        return sol,d,meta

def validate(out):
    out.mkdir(parents=True,exist_ok=False);model=Reduced();metrics={'comparisons':[],'angular_checks':[],'moment_identity':[]}
    cases=[(0,0,0),(0,.001,0),(0,-.001,0),(.004,.001,1),(.004,-.001,1),(.004,.001,-1)]
    for i,(sigma,pi,sign) in enumerate(cases):
        sol,d,meta=model.solve(sigma,pi,sign)
        q=meta['initial']['q'];ref_sigma=math.sqrt(3)*abs(q)/math.sqrt(1+q*q)
        obj=CanonicalFVSpecies(model.src,2.7255,8,Sigma_ref=ref_sigma,orientation=int(np.sign(q)),kappa_gamma=meta['initial']['k'],kappa_nu=meta['initial']['k'],mass_fraction=FM,massive_A=0.,mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
        fs,fd,fw=obj.integrate(n=SAMPLES,rtol=RTOL,atol=ATOL)
        full={'b':np.array([z['b'] for z in fd]),'s_over_H':np.array([z['s']/z['H'] for z in fd]),'E0':np.array([z['E_gamma'][0] for z in fd]),'E2':np.array([z['E_gamma'][2] for z in fd]),'signed_Pi':np.array([math.sqrt(3)*3*model.src.h0**2*(z['Pi_radiation_norm']+z['Pi_matter_norm'])/z['H']**2 for z in fd])}
        diffs={k:float(np.max(abs(d[k]-full[k]))) for k in full}
        constraint=max(abs(z['Einstein_H2']/z['H']**2-1) for z in fd)
        number=max(abs(z[k][0]-1) for z in fd for k in ('N_gamma','N_nu'))
        gamma_nu=max(float(np.max(abs(z['E_gamma']-z['E_nu']))) for z in fd)
        entry={'case':[sigma,pi,sign],'max_abs_difference':diffs,'source_constraint_max_relative':constraint,'source_number_monopole_max_abs':float(number),'source_gamma_nu_energy_max_abs':gamma_nu,'source_wall_s':fw,**meta}
        metrics['comparisons'].append(entry)
        np.savez_compressed(out/f'comparison_{i}.npz',x=sol.t,reduced_state=sol.y,full_state=fs.y,**{'reduced_'+k:v for k,v in d.items()},**{'full_'+k:v for k,v in full.items()})
        dump(out/'metrics.json',metrics)
        assert max(diffs.values())<=1e-8 and constraint<=2e-13 and number<=2e-10 and meta['min_massive_cell_population']>=0
        assert all(z['H']>0 and z['E_gamma'][0]>0 and z['E_nu'][0]>0 for z in fd)
        if i==0:assert np.max(abs(d['s_over_H']))<=1e-12 and np.max(abs(d['b']))<=1e-12
        print('FULL_CASE_VALIDATED',i,json.dumps(entry),flush=True)
    for pi,sign in [(-.001,1),(.001,-1)]:
        _,d8,_=model.solve(.004,pi,sign);s12,d12,m12=Reduced(12).solve(.004,pi,sign)
        diff={k:float(abs(d8[k][-1]-d12[k][-1])) for k in ('Sigma','b','E2')}
        metrics['angular_checks'].append({'case':[.004,pi,sign],'endpoint_L8_L12_abs':diff})
        np.savez_compressed(out/f'L12_pi{pi}_sign{sign}.npz',state=s12.y,**d12)
        assert max(diff.values())<=1e-7
    _,d8,_=model.solve(.004,-.001,1);st,dt,mt=model.solve(.004,-.001,1,rtol=RTOL/10,atol=ATOL/10)
    metrics['tolerance_check']={'case':[.004,-.001,1],'endpoint_abs':{k:float(abs(d8[k][-1]-dt[k][-1])) for k in ('Sigma','b','E2')}}
    np.savez_compressed(out/'tighter_tolerance.npz',state=st.y,**dt)
    assert max(metrics['tolerance_check']['endpoint_abs'].values())<=1e-8
    h=1e-5
    for x,b,v in [(.2,-.003,.004),(.7,.002,-.003),(1.1,0.,.001)]:
        m=model.momentum.moments(x,b)
        fd=(model.momentum.moments(x+h,b+h*v).rho-model.momentum.moments(x-h,b-h*v).rho)/(2*h)
        exact=-3*(m.rho+m.pbar)-6*v*m.pi_s
        residual=abs(fd-exact)/abs(exact)
        metrics['moment_identity'].append({'x':x,'b':b,'bprime':v,'h':h,'finite_difference':fd,'identity_rhs':exact,'relative_residual':residual})
        assert residual<=1e-7
    metrics['status']='PASS_MINIMAL_VALIDATION';dump(out/'metrics.json',metrics)
    print(metrics['status'],flush=True)
    return metrics

def case_grid():
    axis=[(0,0,0.)]+[(i,s,float(i*.004/12)) for i in range(1,13) for s in (-1,1)]
    pis=[(0,0,0.)]+[(j,t,float(j*.001/12)) for j in range(1,13) for t in (-1,1)]
    return [{'id':f's{i:02d}_{s:+d}_p{j:02d}_{t:+d}','sigma_index':i,'pi_index':j,'Sigma0':sigma,'Pi0':pi,'eps_sigma':s,'eps_pi':t} for i,s,sigma in axis for j,t,pi in pis]

def cpu_sample():
    def read():
        a=np.array(list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:])),dtype=float)
        return a.sum()-a[8:10].sum(),a[3]+a[4]
    a,i=read();time.sleep(.25);b,j=read()
    return float((j-i)/(b-a)) if b>a else 0.

def resources(cap):
    affinity=len(os.sched_getaffinity(0));quota=affinity
    p=Path('/sys/fs/cgroup/cpu.max')
    if p.exists():
        q,period=p.read_text().split()
        if q!='max':quota=max(1,float(q)/float(period))
    mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    available=mem['MemAvailable'];cmax=Path('/sys/fs/cgroup/memory.max');ccur=Path('/sys/fs/cgroup/memory.current')
    if cmax.exists() and cmax.read_text().strip()!='max':available=min(available,max(0,int(cmax.read_text())-int(ccur.read_text())))
    reserve=max(512*1024**2,int(available*.1));bound=max(0,int((available-reserve)//(256*1024**2)))
    idle=cpu_sample();spare=max(1,math.floor(min(affinity,quota)*idle))
    slots=min(cap,affinity,max(1,math.floor(quota)),bound,spare)
    return {'affinity_cpus':affinity,'cpu_quota':quota,'host_idle_fraction':idle,'available_bytes':available,'reserve_bytes':reserve,'memory_slots':bound,'observed_spare_slots':spare,'selected_slots':slots,'cap':cap}

def init_worker():
    global WORKER
    try:os.nice(10)
    except OSError:pass
    WORKER=Reduced()

def worker(task):
    case,root,identity=task;root=Path(root);case_id=case['id'];t=time.monotonic()
    with (root/(case_id+'.stdout.log')).open('x') as stdout,(root/(case_id+'.stderr.log')).open('x') as stderr,contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
        try:
            sol,d,meta=WORKER.solve(case['Sigma0'],case['eps_pi']*case['Pi0'],case['eps_sigma'])
            path=root/(case_id+'.npz');tmp=root/(case_id+'.tmp.npz')
            np.savez_compressed(tmp,state=sol.y,**d);tmp.replace(path)
            row={'status':'COMPLETED','case':case,'identity':identity,**meta}
            print(json.dumps(row),flush=True)
        except BaseException as exc:
            traceback.print_exc();row={'status':'FAILED','case':case,'identity':identity,'error':str(exc)}
        row['child_wall_s']=time.monotonic()-t;row['exit_status']=0 if row['status']=='COMPLETED' else 1
        dump(root/(case_id+'.json'),row)
    return row

def sweep(args):
    if args.max_workers> (8 if args.site=='local' else 64):raise ValueError('site worker cap exceeded')
    if not(0<args.wall_seconds<=900 and 0<args.child_seconds<=3600):raise ValueError('frozen wall caps')
    root=args.output;root.mkdir(parents=True,exist_ok=args.resume);casesdir=root/'cases';casesdir.mkdir(exist_ok=args.resume)
    identity={'model_files':model_identity(),'configuration':{'L':8,'fm':FM,'mass_Tref':30,'massive_A':0,'radial_cells':24,'angular_cells':12,'Gauss':3,'rtol':RTOL,'atol':ATOL,'samples':SAMPLES,'grid':'25x25_signed_physical_axes'}}
    receiptpath=root/'run.json'
    if receiptpath.exists():
        receipt=json.loads(receiptpath.read_text())
        if receipt['identity']!=identity:raise ValueError('RESUME_IDENTITY_MISMATCH')
    else:receipt={'identity':identity,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'resource_observations':[]}
    rows=[];pending=[]
    for c in case_grid():
        p=casesdir/(c['id']+'.json')
        if p.exists():
            r=json.loads(p.read_text())
            if r['identity']!=identity or r['case']!=c:raise ValueError('CASE_RESUME_IDENTITY_MISMATCH')
            if r['status']=='COMPLETED' and not (casesdir/(c['id']+'.npz')).exists():raise ValueError('MISSING_COMPLETED_HISTORY')
            rows.append(r)
        elif any((casesdir/(c['id']+suffix)).exists() for suffix in ('.stdout.log','.stderr.log','.npz','.tmp.npz')):
            raise ValueError('UNFINISHED_CASE_NO_AUTOMATIC_RETRY:'+c['id'])
        else:pending.append(c)
    start=time.monotonic();childsum=sum(r.get('child_wall_s',0.) for r in rows)
    # Continuation budgets include prior invocations recorded in this run.
    prior_wall=receipt.get('consumed_wall_s',0.)
    try:
        while pending and childsum<args.child_seconds and prior_wall+time.monotonic()-start<args.wall_seconds:
            obs=resources(args.max_workers);receipt['resource_observations'].append(obs);dump(receiptpath,receipt)
            slots=obs['selected_slots']
            if slots<1:receipt['resource_deferral']='INSUFFICIENT_MEMORY';break
            # Bound one batch's worst-case aggregate solve wall by remaining debit.
            batch_count=min(len(pending),slots*8)
            remaining_child=args.child_seconds-childsum
            remaining_wall=args.wall_seconds-prior_wall-(time.monotonic()-start)
            batch_timeout=min(remaining_wall,remaining_child/slots)
            if batch_timeout<=0:break
            batch=pending[:batch_count];pending=pending[batch_count:]
            pool=mp.get_context('spawn').Pool(slots,initializer=init_worker)
            try:
                jobs=[pool.apply_async(worker,((c,str(casesdir),identity),)) for c in batch]
                deadline=time.monotonic()+batch_timeout
                for job in jobs:
                    row=job.get(timeout=max(.001,deadline-time.monotonic()));rows.append(row);childsum+=row['child_wall_s']
                pool.close();pool.join()
            except BaseException:
                pool.terminate();pool.join();raise
            print('BATCH',len(rows),'of',625,'child_wall',childsum,flush=True)
    finally:
        receipt.update({'consumed_wall_s':prior_wall+time.monotonic()-start,'aggregate_child_wall_s':childsum,'completed':sum(r['status']=='COMPLETED' for r in rows),'failed':sum(r['status']=='FAILED' for r in rows),'total_cases':625})
        receipt['status']='COMPLETE' if receipt['completed']==625 else 'PARTIAL_OR_FAILED'
        dump(receiptpath,receipt);endpoints(root)
    if receipt['completed']!=625:raise RuntimeError('PILOT_INCOMPLETE: inspect preserved rows/logs, no automatic retry')
    print('PILOT_COMPLETE',receipt['completed'],flush=True)

def endpoints(root):
    rows=[]
    for p in sorted((root/'cases').glob('*.json')):
        r=json.loads(p.read_text())
        if r['status']=='COMPLETED':rows.append({**r['case'],**r['endpoint'],'q':r['initial']['q'],'k':r['initial']['k'],'axis_error':r['initial']['axis_error'],'minimum_sampled_angular_brightness':r['minimum_sampled_angular_brightness'],'child_wall_s':r['child_wall_s']})
    if rows:
        with (root/'endpoints.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    v=sub.add_parser('validate');v.add_argument('--output',type=Path,required=True)
    s=sub.add_parser('sweep');s.add_argument('--output',type=Path,required=True);s.add_argument('--resume',action='store_true');s.add_argument('--site',choices=['local','ncp'],default='local');s.add_argument('--max-workers',type=int,default=8);s.add_argument('--wall-seconds',type=float,default=900);s.add_argument('--child-seconds',type=float,default=3600)
    a=ap.parse_args()
    if a.action=='validate':validate(a.output)
    else:
        if a.max_workers<1:raise ValueError('positive workers')
        sweep(a)
if __name__=='__main__':main()
