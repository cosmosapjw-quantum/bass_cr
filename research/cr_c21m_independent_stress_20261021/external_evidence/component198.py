#!/usr/bin/env python3
"""Bounded additive matter/radiation split; parent source and raw rows are immutable."""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[name]='1'
import argparse,contextlib,csv,hashlib,json,math,multiprocessing as mp,sys,time,traceback
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
sys.path.insert(0,str(PARENT))
import pilot as parent
from canonical_fv import CanonicalMomentumFV,CanonicalFVSpecies
FRAME='comoving orthonormal normal frame; pi_hat=diag(-p,-p,2p); dust anisotropic stress=0'
RTOL=parent.RTOL;ATOL=parent.ATOL;WORKER=None
COLS=('x','zbar','elapsed_seconds','b','s_over_H','Sigma','H_per_s','E0','E2','p_m_J_m3','p_r_J_m3','signed_Pi_m','signed_Pi_r','signed_Pi_total','Pi_m','Pi_r','Pi_total','work_m_J_m3_per_x','work_r_J_m3_per_x')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):parent.dump(path,obj)
def write_csv(path,rows):
    rows=list(rows)
    if rows:
        with Path(path).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def components(d):
    src=parent.source_lock();x=d['x'];a=src.aref*np.exp(x)
    pm=src.rhocrit_j_m3*(parent.FM*src.omega_m/src.aref**3)*d['massive_pi_s_norm']
    pr=src.rhocrit_j_m3*(src.omega_r/a**4)*d['E2']/3
    # K*rho_crit,0=3H0^2, with J/m^3 pressure and cosmic proper-time seconds.
    scale=math.sqrt(3)*3*src.h0**2/(src.rhocrit_j_m3*d['H_per_s']**2)
    pim=scale*pm;pir=scale*pr;pit=pim+pir
    return {'p_m_J_m3':pm,'p_r_J_m3':pr,'signed_Pi_m':pim,'signed_Pi_r':pir,'signed_Pi_total':pit,'Pi_m':abs(pim),'Pi_r':abs(pir),'Pi_total':abs(pit),'work_m_J_m3_per_x':-6*d['s_over_H']*pm,'work_r_J_m3_per_x':-6*d['s_over_H']*pr}

class ComponentReduced(parent.Reduced):
    def set_amplitude(self,A):
        if not -1<=A<=2:raise ValueError('SOURCE_POSITIVITY_AMPLITUDE')
        self.momentum=CanonicalMomentumFV(30.,float(A),24,12,gauss_order=3)
    def initial_component_fields(self,signed_sigma):
        src=self.src;m=self.momentum.moments(0.,0.)
        base=src.h0**2*((1-parent.FM)*src.omega_m/src.aref**3+self.mpref*m.rho+src.omega_r/src.aref**4+src.omega_lambda)
        q=signed_sigma/math.sqrt(3-signed_sigma**2)*math.sqrt(base)/src.href
        h2=base+(src.href*q)**2
        pim=math.sqrt(3)*3*src.h0**2*self.mpref*m.pi_s/h2
        return q,h2,pim
    def initial(self,signed_sigma,pim_target,pir_target):
        def f(A):
            self.set_amplitude(A)
            return self.initial_component_fields(signed_sigma)[2]-pim_target
        flo=f(-1.);fhi=f(2.)
        if flo*fhi>0:raise ValueError('UNREALIZABLE_MATTER_TARGET')
        amplitude=brentq(f,-1.,2.,xtol=1e-13,rtol=1e-14)
        self.set_amplitude(amplitude)
        q,h2,pim=self.initial_component_fields(signed_sigma)
        k=pir_target*h2/(math.sqrt(3)*3*self.src.h0**2)*15/(self.src.omega_r/self.src.aref**4)
        if not math.isfinite(k) or abs(k)>.5:raise ValueError('UNREALIZABLE_RADIATION_K')
        y=np.zeros(8);y[2]=q;y[3]=1.;y[4]=k/5
        d=self.diagnostics(np.array([0.]),y[:,None])
        realized={'signed_Sigma0':math.sqrt(3)*float(d['s_over_H'][0]),'signed_Pi_m0':float(d['signed_Pi_m'][0]),'signed_Pi_r0':float(d['signed_Pi_r'][0])}
        axis_error=max(abs(realized['signed_Sigma0']-signed_sigma),abs(realized['signed_Pi_m0']-pim_target),abs(realized['signed_Pi_r0']-pir_target))
        if axis_error>1e-12:raise ArithmeticError('INITIAL_COMPONENT_AXIS_ERROR:'+str(axis_error))
        return y,{'A_m':float(amplitude),'q':q,'k':k,'axis_error':axis_error,'target':{'signed_Sigma0':signed_sigma,'signed_Pi_m0':pim_target,'signed_Pi_r0':pir_target},'realized':realized,'attainable_signed_Pi_m0_at_A_minus1':flo+pim_target,'attainable_signed_Pi_m0_at_A_plus2':fhi+pim_target}
    def diagnostics(self,x,y):
        d=super().diagnostics(x,y);d.update(components(d))
        if not all(np.isfinite(v).all() for v in d.values()):raise ArithmeticError('NONFINITE_COMPONENT_HISTORY')
        return d
    def solve(self,signed_sigma,pim,pir):
        from scipy.integrate import solve_ivp
        y,initial=self.initial(signed_sigma,pim,pir);start=time.monotonic()
        sol=solve_ivp(self.rhs,(0,self.src.xmax),y,method='DOP853',rtol=RTOL,atol=ATOL,t_eval=np.linspace(0,self.src.xmax,parent.SAMPLES))
        if not sol.success:raise RuntimeError(sol.message)
        d=self.diagnostics(sol.t,sol.y)
        meta={'initial':initial,'nfev':int(sol.nfev),'solve_wall_s':time.monotonic()-start,'state_count':8,'min_massive_cell_population':float(self.momentum.cell_numbers.min()),'minimum_sampled_angular_brightness':float(d['sampled_min_angular_brightness'].min()),'endpoint':{k:float(d[k][-1]) for k in COLS if k!='x'},'frame':FRAME}
        if meta['min_massive_cell_population']<0:raise ArithmeticError('NEGATIVE_MASSIVE_POPULATION')
        return sol,d,meta

def identity():
    parent_files=parent.model_identity()
    return {'new_model_sha256':sha(HERE/'component_pilot.py'),'contract_sha256':sha(HERE/'CONTRACT_KO.md'),'parent_immutable_files':parent_files,'reference_controls_sha256':sha(HERE/'reference_controls.json'),'config':{'fm':.1,'mass_Tref':30,'cells':[24,12],'gauss':3,'L':8,'rtol':RTOL,'atol':ATOL,'samples':65,'matter_signed_max':.0004,'new_sweep_count':606,'frame':FRAME}}

def case_grid():
    ss=[(0,0,0.)]+[(i,s,i*.004/12) for i in range(1,13) for s in (-1,1)]
    cases=[{'id':f'm_s{i:02d}_{s:+d}_p{j:02d}_{t:+d}','lane':'MATTER_SLICE','sigma_index':i,'pi_m_index':j,'eps_sigma':s,'eps_m':t,'signed_Sigma0':s*sigma,'signed_Pi_m0':t*j*.0004/12,'signed_Pi_r0':0.} for i,s,sigma in ss for j in range(1,13) for t in (-1,1)]
    for sigma in (0.,.004,-.004):
        for sign in (-1,1):cases.append({'id':f'mixed_s{int(np.sign(sigma)):+d}_m{sign:+d}','lane':'MIXED_CANCELLATION','sigma_index':0 if not sigma else 12,'pi_m_index':12,'eps_sigma':int(np.sign(sigma)),'eps_m':sign,'signed_Sigma0':sigma,'signed_Pi_m0':sign*.0004,'signed_Pi_r0':-sign*.0004})
    return cases

def history_rows(case_id,d,kind):
    for j in range(len(d['x'])):yield {'case_id':case_id,'provenance':kind,**{k:float(d[k][j]) for k in COLS}}

def decompose(out):
    out.mkdir(parents=True,exist_ok=False);(out/'cases').mkdir()
    oldrun=json.loads((PARENT/'results/pilot/run.json').read_text());references=[];endpoints=[];plotrows=[];maxresidual=0.;file_count=0
    representative={'s12_+1_p12_+1','s12_+1_p12_-1','s12_+1_p00_+0','s00_+0_p12_+1'}
    fullpath=out/'histories.csv'
    with fullpath.open('w') as f:
        writer=None
        for path in sorted((PARENT/'results/pilot/cases').glob('*.npz')):
            cid=path.stem;old=json.loads(path.with_suffix('.json').read_text())
            if old['status']!='COMPLETED':raise ValueError('OLD_CASE_NOT_COMPLETE')
            if old['identity']!=oldrun['identity']:raise ValueError('OLD_CASE_IDENTITY')
            with np.load(path) as original:d={k:original[k].copy() for k in original.files if k!='state'}
            d.update(components(d));residual=float(np.max(abs(d['signed_Pi_total']-d['signed_Pi'])))
            if residual>1e-12:raise ArithmeticError('OLD_COMPONENT_RECONSTRUCTION')
            maxresidual=max(maxresidual,residual);np.savez_compressed(out/'cases'/(cid+'.npz'),**{k:d[k] for k in COLS})
            for row in history_rows(cid,d,'OLD_HISTORY_DECOMPOSITION_NO_ODE'):
                if writer is None:writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader()
                writer.writerow(row)
                if cid in representative:plotrows.append(row)
            endpoint={'case_id':cid,**old['case'],'provenance':'OLD_HISTORY_DECOMPOSITION_NO_ODE',**{k:float(d[k][-1]) for k in COLS if k!='x'}};endpoints.append(endpoint)
            if old['case']['pi_index']==0:
                references.append({'provenance':'REFERENCE_REUSE','old_case_id':cid,'old_case':old['case'],'old_initial':old['initial'],'old_case_identity':old['identity'],'old_npz_sha256':sha(path),'old_json_sha256':sha(path.with_suffix('.json')),'actual_initial':{k:float(d[k][0]) for k in ('Sigma','signed_Pi_m','signed_Pi_r','signed_Pi_total')},'endpoint':{k:float(d[k][-1]) for k in COLS if k!='x'}})
            file_count+=1
    assert file_count==625 and len(references)==25
    write_csv(out/'endpoints.csv',endpoints);write_csv(HERE/'old_representative_histories.csv',plotrows)
    reference={'schema':'rei.matter_radiation.reference_reuse.v1','provenance':'REFERENCE_REUSE','new_trajectory_count':0,'source_old_run_identity':oldrun['identity'],'source_old_run_sha256':sha(PARENT/'results/pilot/run.json'),'references':references}
    if (HERE/'reference_controls.json').exists():raise FileExistsError(HERE/'reference_controls.json')
    dump(HERE/'reference_controls.json',reference)
    receipt={'status':'COMPLETE_DECOMPOSITION_NO_ODE','old_cases':file_count,'saved_samples':file_count*parent.SAMPLES,'reference_controls':25,'new_ODE_solves':0,'component_sum_max_abs_difference':maxresidual,'parent_executed_identity':oldrun['identity'],'frame':FRAME,'units':{'p_m_J_m3':'J/m^3','p_r_J_m3':'J/m^3','work_m_J_m3_per_x':'J/m^3 per unit ln(a/a_ref)','work_r_J_m3_per_x':'J/m^3 per unit ln(a/a_ref)'}}
    dump(out/'decomposition_receipt.json',receipt);print(json.dumps(receipt),flush=True)

def validate(out):
    out.mkdir(parents=True,exist_ok=False);model=ComponentReduced();metrics={'comparisons':[],'directional_energy_checks':[],'status':'IN_PROGRESS'}
    for i,(sigma,pim,pir) in enumerate([(.004,.0004,0.),(-.004,-.0004,0.),(0.,.0004,-.0004),(.004,-.0004,.0004)]):
        sol,d,meta=model.solve(sigma,pim,pir);ic=meta['initial'];q=ic['q']
        obj=CanonicalFVSpecies(model.src,2.7255,8,Sigma_ref=math.sqrt(3)*abs(q)/math.sqrt(1+q*q),orientation=int(np.sign(q)),kappa_gamma=ic['k'],kappa_nu=ic['k'],mass_fraction=.1,massive_A=ic['A_m'],mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
        fs,fd,wall=obj.integrate(n=65,rtol=RTOL,atol=ATOL)
        full={k:np.array([z[k] for z in fd]) for k in ('b',)}
        full.update({'s_over_H':np.array([z['s']/z['H'] for z in fd]),'E0':np.array([z['E_gamma'][0] for z in fd]),'E2':np.array([z['E_gamma'][2] for z in fd])})
        full['signed_Pi_m']=np.array([math.sqrt(3)*3*model.src.h0**2*z['Pi_matter_norm']/z['H']**2 for z in fd]);full['signed_Pi_r']=np.array([math.sqrt(3)*3*model.src.h0**2*z['Pi_radiation_norm']/z['H']**2 for z in fd]);full['signed_Pi_total']=full['signed_Pi_m']+full['signed_Pi_r']
        errors={k:float(np.max(abs(d[k]-full[k]))) for k in full};constraint=max(abs(z['Einstein_H2']/z['H']**2-1) for z in fd)
        entry={'targets':[sigma,pim,pir],'max_abs_difference':errors,'source_constraint_max_relative':constraint,'source_wall_s':wall,'source_number_monopole_max_abs':float(max(abs(z[k][0]-1) for z in fd for k in ('N_gamma','N_nu'))),**meta}
        metrics['comparisons'].append(entry);np.savez_compressed(out/f'comparison_{i}.npz',x=sol.t,reduced_state=sol.y,full_state=fs.y,**{'reduced_'+k:v for k,v in d.items()},**{'full_'+k:v for k,v in full.items()});dump(out/'metrics.json',metrics)
        if max(errors.values())>1e-8 or constraint>2e-13:raise ArithmeticError('NEW_FULL_SOURCE_COMPARISON')
        if not all(z['H']>0 and z['E_gamma'][0]>0 and z['E_nu'][0]>0 for z in fd):raise ArithmeticError('SOURCE_ENERGY_H')
        print('NEW_FULL_CASE_VALIDATED',i,json.dumps(entry),flush=True)
    for A,x,b,w in [(.8275,.4,.002,.003),(-.8275,.9,-.003,-.004)]:
        model.set_amplitude(A);h=1e-5;m=model.momentum.moments(x,b)
        fd=(model.momentum.moments(x+h,b+w*h).rho-model.momentum.moments(x-h,b-w*h).rho)/(2*h);rhs=-3*(m.rho+m.pbar)-6*w*m.pi_s;residual=abs(fd-rhs)/abs(rhs)
        metrics['directional_energy_checks'].append({'A_m':A,'x':x,'b':b,'w_s_over_H':w,'h':h,'finite_difference':fd,'identity_rhs':rhs,'relative_residual':residual})
        if residual>1e-7:raise ArithmeticError('NEW_MASSIVE_ENERGY_IDENTITY')
    metrics['status']='PASS_NEW_MINIMAL_VALIDATION_PENDING_INDEPENDENT_REVIEW';dump(out/'metrics.json',metrics);print(metrics['status'],flush=True)

def init_worker():
    global WORKER
    try:os.nice(10)
    except OSError:pass
    WORKER=ComponentReduced()

def worker(task):
    case,root,ident=task;root=Path(root);cid=case['id'];start=time.monotonic()
    with (root/(cid+'.stdout.log')).open('x') as out,(root/(cid+'.stderr.log')).open('x') as err,contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
        try:
            sol,d,meta=WORKER.solve(case['signed_Sigma0'],case['signed_Pi_m0'],case['signed_Pi_r0'])
            temp=root/(cid+'.tmp.npz');np.savez_compressed(temp,state=sol.y,**d);temp.replace(root/(cid+'.npz'))
            row={'status':'COMPLETED','provenance':'NEW_COUPLED_ODE','case':case,'identity':ident,**meta};print(json.dumps(row),flush=True)
        except BaseException as exc:traceback.print_exc();row={'status':'FAILED','provenance':'NEW_COUPLED_ODE','case':case,'identity':ident,'error':str(exc)}
        row.update({'child_wall_s':time.monotonic()-start,'logical_task_exit_status':0 if row['status']=='COMPLETED' else 1});dump(root/(cid+'.json'),row)
    return row

def assemble(root):
    rows=[];histories=[]
    for path in sorted((root/'cases').glob('*.json')):
        row=json.loads(path.read_text())
        if row['status']!='COMPLETED':continue
        c=row['case'];rows.append({**c,'provenance':'NEW_COUPLED_ODE',**row['endpoint'],'A_m':row['initial']['A_m'],'k':row['initial']['k'],'axis_error':row['initial']['axis_error']})
    write_csv(root/'endpoints.csv',rows)
    matter=[r for r in rows if r['lane']=='MATTER_SLICE']
    for ref in json.loads((HERE/'reference_controls.json').read_text())['references']:
        old=ref['old_case'];matter.append({'id':ref['old_case_id'],'lane':'MATTER_SLICE_REFERENCE','sigma_index':old['sigma_index'],'pi_m_index':0,'eps_sigma':old['eps_sigma'],'eps_m':0,'signed_Sigma0':ref['old_initial']['realized_Sigma']*old['eps_sigma'],'signed_Pi_m0':ref['actual_initial']['signed_Pi_m'],'signed_Pi_r0':ref['actual_initial']['signed_Pi_r'],'provenance':'REFERENCE_REUSE',**ref['endpoint'],'A_m':0.,'k':ref['old_initial']['k'],'axis_error':ref['old_initial']['axis_error']})
    write_csv(root/'matter_slice_with_reference_controls.csv',matter)
    if len(rows)==606:
        with (root/'histories.csv').open('w') as f:
            writer=None
            for row in rows:
                cid=row['id']
                with np.load(root/'cases'/(cid+'.npz')) as data:
                    for item in history_rows(cid,data,'NEW_COUPLED_ODE'):
                        if writer is None:writer=csv.DictWriter(f,fieldnames=list(item));writer.writeheader()
                        writer.writerow(item)

def sweep(args):
    if not 1<=args.max_workers<=(8 if args.site=='local' else 64):raise ValueError('SITE_WORKER_CAP')
    if not(0<args.wall_seconds<=900 and 0<args.child_seconds<=3600):raise ValueError('FROZEN_RESOURCE_CAP')
    root=args.output;root.mkdir(parents=True,exist_ok=args.resume);cases=root/'cases';cases.mkdir(exist_ok=args.resume);ident=identity();rp=root/'run.json'
    receipt=json.loads(rp.read_text()) if rp.exists() else {'identity':ident,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'resource_observations':[]}
    if receipt['identity']!=ident:raise ValueError('RESUME_IDENTITY_MISMATCH')
    rows=[];pending=[]
    for c in case_grid():
        path=cases/(c['id']+'.json')
        if path.exists():
            r=json.loads(path.read_text())
            if r['identity']!=ident or r['case']!=c:raise ValueError('CASE_IDENTITY_MISMATCH')
            if r['status']=='COMPLETED' and not (cases/(c['id']+'.npz')).exists():raise ValueError('MISSING_COMPLETED_HISTORY')
            rows.append(r)
        elif any((cases/(c['id']+suffix)).exists() for suffix in ('.stdout.log','.stderr.log','.npz','.tmp.npz')):raise ValueError('NO_AUTOMATIC_RETRY_UNFINISHED:'+c['id'])
        else:pending.append(c)
    start=time.monotonic();prior=receipt.get('consumed_wall_s',0.);childsum=sum(r['child_wall_s'] for r in rows)
    try:
        while pending and prior+time.monotonic()-start<args.wall_seconds and childsum<args.child_seconds:
            obs=parent.resources(args.max_workers);receipt['resource_observations'].append(obs)
            receipt.update({'consumed_wall_s':prior+time.monotonic()-start,'aggregate_child_wall_s':childsum});dump(rp,receipt)
            slots=obs['selected_slots']
            if slots<1:receipt['resource_deferral']='INSUFFICIENT_MEMORY';break
            timeout=min(args.wall_seconds-prior-(time.monotonic()-start),(args.child_seconds-childsum)/slots)
            if timeout<=0:break
            batch=pending[:slots*8];pending=pending[slots*8:];pool=mp.get_context('spawn').Pool(slots,initializer=init_worker)
            try:
                jobs=[pool.apply_async(worker,((c,str(cases),ident),)) for c in batch];deadline=time.monotonic()+timeout
                for job in jobs:
                    r=job.get(timeout=max(.001,deadline-time.monotonic()));rows.append(r);childsum+=r['child_wall_s']
                pool.close();pool.join()
            except BaseException:pool.terminate();pool.join();raise
            print('NEW_BATCH',len(rows),'of',606,flush=True)
    finally:
        receipt.update({'consumed_wall_s':prior+time.monotonic()-start,'aggregate_child_wall_s':childsum,'completed':sum(r['status']=='COMPLETED' for r in rows),'failed':sum(r['status']=='FAILED' for r in rows),'new_trajectory_target':606,'reused_controls':25,'scientific_status':'PENDING_INDEPENDENT_REVIEW'})
        receipt['status']='COMPLETE' if receipt['completed']==606 else 'PARTIAL_OR_FAILED';dump(rp,receipt);assemble(root)
    if receipt['completed']!=606:raise RuntimeError('INCOMPLETE_NEW_SWEEP_NO_AUTOMATIC_RETRY')
    summary={'new_completed':606,'new_failed':0,'reference_controls':25,'max_initial_axis_error':max(r['initial']['axis_error'] for r in rows),'max_abs_A_m':max(abs(r['initial']['A_m']) for r in rows),'min_massive_cell_population':min(r['min_massive_cell_population'] for r in rows),'minimum_sampled_angular_brightness':min(r['minimum_sampled_angular_brightness'] for r in rows),'frame':FRAME,'scientific_status':'PENDING_INDEPENDENT_REVIEW'}
    dump(root/'summary.json',summary);print(json.dumps(summary),flush=True)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    for name in ('decompose','validate'):
        p=sub.add_parser(name);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('sweep');p.add_argument('--output',type=Path,required=True);p.add_argument('--resume',action='store_true');p.add_argument('--site',choices=['local','ncp'],default='local');p.add_argument('--max-workers',type=int,default=8);p.add_argument('--wall-seconds',type=float,default=900);p.add_argument('--child-seconds',type=float,default=3600)
    a=ap.parse_args()
    if a.action=='decompose':decompose(a.output)
    elif a.action=='validate':validate(a.output)
    else:sweep(a)
if __name__=='__main__':main()
