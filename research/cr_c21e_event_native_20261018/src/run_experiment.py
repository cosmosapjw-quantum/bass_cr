"""C21E chronological source-age integration and independent continuous oracle.

Modes share one frozen input fixture, source impulses and event grid. The fixed
refinement never silently accepts a clipped state or changes its mesh after a
rejection. Native and manufactured microphysics are never relabelled.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import argparse,hashlib,json,math,subprocess,time,traceback
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from event_coupler import (BIND_EV,EV_ERG,KB_EV,H,cross,FIT,C_CM_S,N_H0,Y_HE,
                          MODES,Controls,ZeroMicro,ManufacturedMicro,MicroRates,
                          alpha,binding_weights,event_fractions,gas_from_temperature,
                          require_state,reaction_step,StepRejected,DomainError,ProviderFailure,temperature)
from radau_exposure_oracle import make_cohorts
from native_micro import NativeMicro,OWNER
X4,W4=leggauss(4)


def write_json(path:Path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    with temp.open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush()
    if path.exists():temp.unlink();raise FileExistsError(path)
    temp.rename(path)


@dataclass(frozen=True)
class Fixture:
    x0:float
    dx:float
    nh0:float
    Y:float
    gas0:tuple[float,...]
    q:tuple[float,...]
    birth:tuple[float,...]
    amounts:tuple[float,...]
    opacity_scale:float
    source_identity:str
    scope:str='FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT'

    def validate(self):
        require_state(np.array(self.gas0),self.Y)
        q=np.asarray(self.q);b=np.asarray(self.birth);n=np.asarray(self.amounts)
        if q.ndim!=1 or not (len(q)==len(b)==len(n)) or len(q)>4096:raise DomainError('FIXTURE_PACKET_SHAPE')
        if not all(np.isfinite(v).all() for v in (q,b,n)) or (q<=0).any() or (n<0).any():raise DomainError('FIXTURE_PACKETS')
        if not all(math.isfinite(v) for v in (self.x0,self.dx,self.nh0,self.opacity_scale)):raise DomainError('FIXTURE_SCALAR')
        if not 0<self.dx<=.1 or self.nh0<=0 or self.opacity_scale<0:raise DomainError('FIXTURE_TIME_DENSITY')
        if math.exp(self.x0)<1/21 or math.exp(self.x0+self.dx)>.2:raise DomainError('FIXTURE_MD14_EPOCH')
        if (b<self.x0).any() or (b>self.x0+self.dx).any():raise DomainError('FIXTURE_BIRTH_ORDER')
        if not self.source_identity:raise DomainError('FIXTURE_SOURCE_IDENTITY')
        return self

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self),sort_keys=True,separators=(',',':')).encode()).hexdigest()


def make_fixture(a0=1/12,dx=.002,opacity_scale=.001,source_on=True,Y=Y_HE):
    x0=math.log(a0);cohorts,_=make_cohorts(x0,dx)
    if not source_on:cohorts=tuple(c for c in cohorts if c.birth_x==x0)
    gas=gas_from_temperature([.2,.15 if Y else 0.,.01 if Y else 0.],8500.,Y)
    return Fixture(x0,dx,N_H0,Y,tuple(gas),tuple(c.q20 for c in cohorts),tuple(c.birth_x for c in cohorts),
                   tuple(c.start_n for c in cohorts),opacity_scale,'PINNED_PR79_MD14_RATE_MANUFACTURED_3_ENERGY_GAS').validate()


def fixture_from_native_source(binary:Path,a0,dx,subdivisions,quadrature,output:Path)->Fixture:
    """Get actual native total-H densities, rate and cells; explicit gas is ours."""
    out=subprocess.run([str(binary.resolve()),'--export-source',repr(a0),repr(dx),str(subdivisions)],capture_output=True,text=True,timeout=30,check=False)
    (output/'source_export_stdout.tsv').write_text(out.stdout)
    (output/'source_export_stderr.log').write_text(out.stderr)
    if out.returncode:raise ProviderFailure('NATIVE_SOURCE_EXPORT_FAILED '+out.stderr)
    lines=out.stdout.splitlines()
    if not lines or lines[0]!=f'C21E_SOURCE_V1\t{OWNER}':raise ProviderFailure('SOURCE_OWNER_ID')
    density=[];births=[];cells=[]
    for line in lines[1:]:
        fields=line.split('\t');v=list(map(float,fields[1:]))
        if fields[0]=='DENSITY':density.append(v)
        elif fields[0]=='BIRTH':births.append(v)
        elif fields[0]=='CELL':cells.append(v)
        else:raise ProviderFailure('SOURCE_EXPORT_ROW')
    if len(density)!=1 or len(density[0])!=2 or len(births)!=2 or len(cells)!=3*subdivisions:raise ProviderFailure('SOURCE_EXPORT_SCHEMA')
    nh0,nhe0=density[0];Y=nhe0/nh0
    if not math.isclose(math.fsum(c[3] for c in cells),1.,rel_tol=2e-12):raise ProviderFailure('SOURCE_CELL_NORMALIZATION')
    x0=math.log(a0);q=[];b=[];amounts=[]
    for E,n in zip((13.8,24.8,55.),(.014,.010,.008)):
        q.append(a0*E);b.append(x0);amounts.append(n)
    for xb,hub,rate in births:
        if not math.isclose(hub,H(xb),rel_tol=3e-13):raise ProviderFailure('SOURCE_CLOCK_MISMATCH')
        emission=dx*.5*rate/hub
        for lo,hi,centroid,weight in cells:
            if not 0<lo<=centroid<=hi or weight<0:raise ProviderFailure('SOURCE_CELL_DOMAIN')
            if quadrature=='centroid':es=np.array([centroid]);ws=np.array([weight])
            else:
                nodes,weights=leggauss(8);es=(lo+hi)/2+(hi-lo)/2*nodes
                raw=weights*(hi-lo)/2*es**2/np.expm1(es/(KB_EV*50000.))
                ws=weight*raw/raw.sum()
            for E,w in zip(es,ws):q.append(math.exp(xb)*float(E));b.append(xb);amounts.append(emission*float(w))
    gas=gas_from_temperature([.2,.15,.01],8500.,Y)
    identity=f'NATIVE_{OWNER}_MD14_CELLS{subdivisions*3}_{quadrature}_GL2_GLOBAL_BIRTH_EXPLICIT_GAS'
    return Fixture(x0,dx,nh0,Y,tuple(gas),tuple(q),tuple(b),tuple(amounts),1.,identity).validate()


def breakpoints(f:Fixture):
    end=f.x0+f.dx
    cuts={f.x0,end}
    for q,b in zip(f.q,f.birth):
        if f.x0<b<end:cuts.add(b)
        for threshold in FIT:
            x=math.log(q/threshold)
            if max(f.x0,b)<x<end:cuts.add(x)
    return sorted(cuts)


def initial(f):
    return np.array(f.gas0),np.array([n if b==f.x0 else 0. for n,b in zip(f.amounts,f.birth)])


def opacity(f,x):
    E=np.asarray(f.q)*math.exp(-x)
    k=np.array([[f.opacity_scale*C_CM_S*f.nh0*math.exp(-3*x)*cross(j,float(e)) for j in range(3)] for e in E])
    return E,k


def geom(g,n,q,lo,hi):
    w=g[3];out=g.copy();out[3]*=math.exp(-2*(hi-lo))
    # Positive expm1 differences avoid subtraction of nearly equal inventories.
    wp=float(np.dot(n,q*math.exp(-lo))*(-math.expm1(-(hi-lo))))
    wg=w*(-math.expm1(-2*(hi-lo)))
    return out,wp,wg


def totals(f,g,n,ledgers):
    g0,n0=initial(f);q=np.asarray(f.q)
    end=f.x0+f.dx
    b=binding_weights(f.Y)
    u0=float(n0@(q*math.exp(-f.x0)));u1=float(n@(q*math.exp(-end)))
    photo=np.asarray(ledgers['photo']);ci=np.asarray(ledgers['ci']);rr=np.asarray(ledgers['rr']);dr=ledgers['dr']
    species=g[:3]-g0[:3]-event_fractions(photo+ci-rr-np.array([0.,dr,0.]),f.Y)
    mass=math.fsum(n0)+ledgers['source_n']-math.fsum(n)-math.fsum(photo)
    energy=math.fsum([u1-u0,g[3]-g0[3],float(b@(g[:3]-g0[:3])),ledgers['escape'],-ledgers['cmb'],ledgers['photon_work'],ledgers['gas_work'],-ledgers['source_u']])
    return {'gas':g.tolist(),'photons':n.tolist(),'temperature_K':temperature(g,f.Y),
            'photon_number':float(n.sum()),'photon_energy_eV_H':u1,'number_defect_H':mass,'energy_defect_eV_H':energy,
            'species_defect':species.tolist(),'ledgers':ledgers}


def run_history(f:Fixture,subdivisions:int,provider,mode='FULLMID',output:Path|None=None,max_steps=4096):
    f.validate()
    if subdivisions<1 or subdivisions>512:raise DomainError('STEP_COUNT_DOMAIN')
    controls=MODES[mode];g,n=initial(f);q=np.asarray(f.q)
    cuts=breakpoints(f)
    if subdivisions*(len(cuts)-1)>max_steps:raise DomainError('TOTAL_STEP_BUDGET')
    logs=[]
    led={'photo':np.zeros(3),'ci':np.zeros(3),'rr':np.zeros(3),'dr':0.,'heat':0.,'escape':0.,'cmb':0.,'photon_work':0.,'gas_work':0.,'source_n':0.,'source_u':0.}
    rhs_calls=0;t0=time.monotonic();partial=None
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        partial=(output/'accepted_steps.jsonl').open('x')
    try:
        for left,right in zip(cuts[:-1],cuts[1:]):
            points=np.linspace(left,right,subdivisions+1)
            for lo,hi in zip(points[:-1],points[1:]):
                mid=.5*(lo+hi);dt=.5*(hi-lo)*sum(float(w)/H(mid+.5*(hi-lo)*float(x)) for x,w in zip(X4,W4))
                gm,wp0,wg0=geom(g,n,q,lo,mid)
                E,k=opacity(f,mid)
                step=reaction_step(gm,n,E,k,dt,math.exp(mid),f.nh0,f.Y,provider,controls)
                gn,wp1,wg1=geom(step.gas,step.photons,q,mid,hi)
                # Commit all fields once only after both suboperators succeeded.
                g=gn;n=step.photons
                led['photo']+=step.events.sum(axis=0);led['heat']+=step.heat_ev_h
                led['ci']+=dt*step.micro.ci_h_s;led['rr']+=dt*step.micro.rr_h_s;led['dr']+=dt*step.micro.dr_h_s
                led['escape']+=dt*step.micro.escaped_ev_h_s;led['cmb']+=dt*step.micro.cmb_ev_h_s
                led['photon_work']+=wp0+wp1;led['gas_work']+=wg0+wg1
                rhs_calls+=step.nfev
                row={'x0':float(lo),'x1':float(hi),'dt_s':dt,'gas':g.tolist(),'n':float(n.sum()),'photo_H':step.events.sum(axis=0).tolist(),
                     'energy_defect':step.energy_defect,'number_defect':step.number_defect,'residual':step.residual.tolist(),'rhs_calls':step.nfev,'iterations':step.iterations}
                logs.append(row)
                if partial:partial.write(json.dumps(row,allow_nan=False)+'\n');partial.flush()
            for index,birth in enumerate(f.birth):
                if birth==right and birth>f.x0:
                    amount=f.amounts[index]
                    n[index]+=amount;led['source_n']+=amount;led['source_u']+=amount*f.q[index]*math.exp(-birth)
    finally:
        if partial:partial.close()
    for key in ('photo','ci','rr'):led[key]=led[key].tolist()
    result=totals(f,g,n,led)
    result.update(schema='C21E_FIXED_SOURCE_EVENT_NATIVE_TRANSACTION_V1',fixture_sha256=f.digest,mode=mode,microphysics=provider.kind,
                  steps=len(logs),subdivisions_per_event_interval=subdivisions,rhs_calls=rhs_calls,wall_s=time.monotonic()-t0,
                  max_step_energy_defect=max([abs(r['energy_defect']) for r in logs],default=0),
                  max_step_nonlinear_residual=max([max(abs(v) for v in r['residual']) for r in logs],default=0),
                  status='PASS_SCOPED_FIXED_GRID_TRANSACTION',source_time_refinement='NOT_RUN_FIXED_GLOBAL_GL2_BIRTHS')
    if output:write_json(output/'result.json',result)
    return result


def _run_reference_population(f:Fixture,provider,rtol=2e-10,atol=2e-13,max_cohorts=128):
    """Independent Radau continuous photon+gas ODE; not discrete-event solver."""
    f.validate();M=len(f.q)
    if M>max_cohorts:raise DomainError('RADAU_DENSE_COHORT_BUDGET')
    g,n=initial(f)
    # N[M], gas[4], photo[3], ci[3], rr[3], dr, escape, cmb, photonwork, gaswork, heat
    y=np.zeros(M+4+15);y[:M]=n;y[M:M+4]=g
    ix={'photo':M+4,'ci':M+7,'rr':M+10,'dr':M+13,'escape':M+14,'cmb':M+15,'photon_work':M+16,'gas_work':M+17,'heat':M+18}
    source_n=0.;source_u=0.;nfev=0;start=time.monotonic();cuts=breakpoints(f)
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        active=np.array([birth<=lo for birth in f.birth])
        def rhs(x,v):
            # Endpoint samples use the smooth-cell one-sided limit only.
            xx=min(max(x,lo+1e-9*(hi-lo)),hi-1e-9*(hi-lo))
            gv=v[M:M+4];require_state(gv,f.Y)
            if (v[:M]<0).any():raise DomainError('RADAU_INTERNAL_NEGATIVE_PHOTON')
            micro=provider(math.exp(xx),gv,f.nh0,f.Y);micro.validate(f.Y)
            E,k=opacity(f,xx);rates=v[:M,None]*k*alpha(gv,f.Y)[None,:]*active[:,None]
            h=H(xx);species=rates.sum(axis=0);heat=float(np.sum(rates*(E[:,None]-np.array(BIND_EV)[None,:])))
            out=np.zeros_like(v);out[:M]=-rates.sum(axis=1)/h
            out[M:M+3]=(event_fractions(species,f.Y)+micro.fraction_s)/h
            out[M+3]=(heat+micro.thermal_ev_h_s)/h-2*gv[3]
            out[ix['photo']:ix['photo']+3]=species/h
            out[ix['ci']:ix['ci']+3]=micro.ci_h_s/h;out[ix['rr']:ix['rr']+3]=micro.rr_h_s/h
            out[ix['dr']]=micro.dr_h_s/h;out[ix['escape']]=micro.escaped_ev_h_s/h;out[ix['cmb']]=micro.cmb_ev_h_s/h
            out[ix['photon_work']]=float((v[:M]*active)@E);out[ix['gas_work']]=2*gv[3];out[ix['heat']]=heat/h
            return out
        sol=solve_ivp(rhs,(lo,hi),y,method='Radau',rtol=rtol,atol=atol,max_step=(hi-lo)/8)
        if not sol.success:raise StepRejected('RADAU_FAILED '+sol.message)
        y=sol.y[:,-1].copy();nfev+=sol.nfev
        for index,birth in enumerate(f.birth):
            if birth==hi and birth>f.x0:
                y[index]+=f.amounts[index];source_n+=f.amounts[index];source_u+=f.amounts[index]*f.q[index]*math.exp(-birth)
    led={k:y[v:v+3].tolist() if k in ('photo','ci','rr') else float(y[v]) for k,v in ix.items()}
    led.update(source_n=source_n,source_u=source_u)
    result=totals(f,y[M:M+4],y[:M],led)
    result.update(schema='C21E_CONTINUOUS_RADAU_REFERENCE_V1',fixture_sha256=f.digest,microphysics=provider.kind,nfev=nfev,wall_s=time.monotonic()-start,
                  status='PASS_SCOPED_CONTINUOUS_IVP',independence='Independent time integration and continuous photo RHS; identical microphysics kernel')
    return result



def run_reference(f:Fixture,provider,rtol=2e-10,atol=2e-13,max_cohorts=128,coordinates='optical-depth'):
    """Selectable mathematically equivalent reference; no silent fallback."""
    if coordinates=='population':
        result=_run_reference_population(f,provider,rtol,atol,max_cohorts)
        result['reference_coordinates']='population'
        return result
    if coordinates!='optical-depth':raise DomainError('REFERENCE_COORDINATE_SELECTION')
    from reference_tau import run_reference_tau
    return run_reference_tau(f,provider,rtol,atol,max_cohorts)


def native_point_parity(binary:Path,f:Fixture,output:Path):
    """Actual PreparedAbsorption delta-point identity, NOT full driver parity."""
    from native_micro import OWNER
    a=1./21.;g=np.asarray(f.gas0);dt=1e9
    Evals=(13.60,13.61,24.58,24.59,54.41,54.42,80.)
    args=[];expected=[]
    for E in Evals:
        args.append('ABSORB\t'+'\t'.join(format(float(x),'.17e') for x in (a,dt,f.nh0,f.nh0*f.Y,*g[:3],E,1e-5)))
        k=np.array([C_CM_S*f.nh0/a**3*cross(j,E) for j in range(3)])
        lam=k*alpha(g,f.Y);tau=lam.sum()*dt;n1=1e-5/(1+tau)
        events=n1*lam*dt
        expected.append(np.r_[n1,E*n1,events,events*(E-np.array(BIND_EV))])
    p=subprocess.run([str(binary.resolve())],input='\n'.join(args+['QUIT'])+'\n',text=True,capture_output=True,timeout=30)
    (output/'prepared_point_stdout.tsv').write_text(p.stdout);(output/'prepared_point_stderr.log').write_text(p.stderr)
    lines=p.stdout.splitlines()
    if p.returncode or len(lines)!=len(args)+1 or lines[0]!=f'C21E_NONPHOTO_V1\t{OWNER}':raise ProviderFailure('PREPARED_POINT_PROTOCOL')
    records=[]
    for E,line,target in zip(Evals,lines[1:],expected):
        tokens=line.split('\t')
        if tokens[0]!='ABSORBED':raise ProviderFailure('PREPARED_POINT_FAILED '+line)
        val=np.array(list(map(float,tokens[1:])))
        if val.shape!=(8,) or not np.isfinite(val).all():raise ProviderFailure('PREPARED_POINT_VALUES')
        if not np.allclose(val,target,rtol=2e-11,atol=2e-22):raise ProviderFailure('PREPARED_POINT_PARITY')
        records.append({'energy_eV':E,'native':val.tolist(),'independent_BE':target.tolist(),'max_abs_difference':float(np.max(abs(val-target)))})
    write_json(output/'prepared_point_parity.json',{'scope':'delta-point fixed-gas BE only, not production history','records':records,'passed':len(records)})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--micro',choices=['manufactured','zero','native'],default='manufactured')
    p.add_argument('--native',type=Path)
    p.add_argument('--fixture',type=Path)
    p.add_argument('--a0',type=float,default=1/12);p.add_argument('--dx',type=float,default=.002)
    p.add_argument('--opacity-scale',type=float,default=.001)
    p.add_argument('--source',choices=['manufactured3','native-centroid','native-gl8'],default='manufactured3')
    p.add_argument('--source-subdivisions',type=int,default=4)
    p.add_argument('--steps',type=int,nargs='+',default=[8,16,32,64])
    p.add_argument('--modes',nargs='+',choices=list(MODES),default=list(MODES))
    p.add_argument('--no-reference',action='store_true');p.add_argument('--cpu',type=int)
    p.add_argument('--reference-coordinates',choices=['optical-depth','population'],default='optical-depth')
    p.add_argument('--max-native-calls',type=int,default=20000);p.add_argument('--call-timeout',type=float,default=15.)
    args=p.parse_args()
    if args.micro=='native' and (args.native is None or not args.native.is_file()):p.error('--micro native requires compiled --native')
    if args.cpu is not None:
        if not hasattr(__import__('os'),'sched_getaffinity'):p.error('affinity unsupported')
        import os
        if args.cpu not in os.sched_getaffinity(0):p.error('CPU outside allocation')
        os.sched_setaffinity(0,{args.cpu})
    args.out.mkdir(parents=True,exist_ok=False)
    try:
        if args.fixture:f=Fixture(**json.loads(args.fixture.read_text())).validate()
        elif args.source.startswith('native-'):
            if args.native is None:p.error('native source export requires binary')
            f=fixture_from_native_source(args.native,args.a0,args.dx,args.source_subdivisions,args.source.split('-')[1],args.out)
        else:f=make_fixture(args.a0,args.dx,args.opacity_scale)
        write_json(args.out/'fixture.json',asdict(f))
        if args.micro=='native':native_point_parity(args.native,f,args.out)
        def provider(path):
            if args.micro=='native':return NativeMicro([str(args.native.resolve())],path,args.call_timeout,args.max_native_calls)
            return ManufacturedMicro() if args.micro=='manufactured' else ZeroMicro()
        reference=None;rows=[]
        if not args.no_reference:
            micro=provider(args.out/'reference_process')
            try:reference=run_reference(f,micro,coordinates=args.reference_coordinates)
            finally:
                if isinstance(micro,NativeMicro):micro.close()
            write_json(args.out/'radau.json',reference)
        for mode in args.modes:
            for n in args.steps:
                case=args.out/f'{mode}_{n:04d}';micro=provider(case/'process')
                try:r=run_history(f,n,micro,mode,case)
                finally:
                    if isinstance(micro,NativeMicro):micro.close()
                if reference:
                    delta=np.abs(np.asarray(r['gas'])-reference['gas'])
                    r['fraction_max_abs_error']=float(delta[:3].max())
                    r['thermal_abs_error_eV_H']=float(delta[3])
                    r['normalized_state_error']=float(max(delta[:3].max(),delta[3]/f.gas0[3]))
                    r['photon_max_abs_error']=float(np.max(abs(np.asarray(r['photons'])-reference['photons'])))
                rows.append(r)
        write_json(args.out/'SUMMARY.json',{'schema':'C21E_COMPLETE_MATRIX_V1','fixture_sha256':f.digest,'microphysics':rows[0]['microphysics'],'cases':rows,
                  'reference_status':reference['status'] if reference else 'NOT_RUN','native_science':args.micro=='native',
                  'claim_ceiling':'One specified fixed birth/spectral/geometry model; not source-age/spectral/global EoR convergence'})
        print(json.dumps({'status':'COMPLETE_SCOPED','cases':len(rows),'micro':args.micro,'output':str(args.out)}))
    except BaseException as e:
        # Preserve partial accepted step JSONL and native calls. Never mark failure PASS.
        write_json(args.out/'FAILURE.json',{'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'native_claim':'NOT_ADMITTED'})
        raise
if __name__=='__main__':main()
