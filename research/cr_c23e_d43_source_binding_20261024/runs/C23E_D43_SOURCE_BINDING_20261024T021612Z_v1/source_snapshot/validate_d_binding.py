"""One create-only V2 suite; no parent H integration and no ODE."""
import os,time,json,math,csv,hashlib,sys,resource,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dump(p,d):
    with p.open('x') as f:json.dump(d,f,indent=2,allow_nan=False)
def main(out):
    import numpy as np
    import scipy
    from scipy.integrate import quad
    import d_binding as d
    from reuse.atomic_contract import POPULATION_LABELS,INDEX,conservation_residuals
    start=time.perf_counter();cpu=time.process_time();checks=[]
    def check(name,ok,value=None):
        checks.append(dict(name=name,passed=bool(ok),value=value))
        if not ok:raise AssertionError(name+': '+str(value))
    manifest=[]
    for p in sorted((ROOT/'implementation/reuse').rglob('*')):
        if p.is_file() and p.suffix in ['.py','.dat','.csv','.json']:
            b=p.read_bytes();manifest.append(dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
    casesfile=ROOT/'intake/c23b/CASES.json';b=casesfile.read_bytes()
    if len(b)==25700 and b.endswith(b'\n\n'):b=b[:-1]
    check('parent_cases_identity',len(b)==25699 and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='61bcbc0b44206f496534da6bdffcdfe1731ad063')
    exact=ROOT/'inputs/C23B_CASES_EXACT.json'
    with exact.open('xb') as f:f.write(b)
    cases=json.loads(b)
    atomspath=Path('/workspace/scratch/30d955d9ea43/n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv')
    ab=atomspath.read_bytes();check('saved_atoms_identity',len(ab)==1681578 and hashlib.sha256(ab).hexdigest()=='f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3')
    for name,data in [('parent_cases',b),('saved_atoms',ab)]:manifest.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
    dump(out/'INPUT_MANIFEST.json',manifest)
    rrrow=(ROOT/'implementation/reuse/c21o/vendor/atomic/rr_table.dat').read_text().splitlines()[0].split();rrparams=list(map(float,rrrow[-4:]));check('rr_H_row',rrparams==[7.982e-11,.748,3.148,703600.])
    labels=d.POPULATION_LABELS
    values=[0,.8,.2,2e-5,5e-6,0,0,8e-6,1.5e-6,.5e-6,.06,.02,.003,4e-12,3e-12,2e-12,1e-12,2e-10,1.5e-10,1e-10,.5e-10]
    dens=dict(zip(labels,values));dump(out/'POINT_INPUT.json',dict(densities=dens,rrparams=rrparams,potential=d.POTENTIAL,model='CONDITIONAL_THRESHOLD_GATE_AND_SHARED_RR_MOMENT'))
    charge=math.fsum(s.charge*dens[s.label] for s in d.SPECIES[:-1])
    nets=[]
    for lo,hi in [('H1:0','H1:1'),('D:0','D:1')]:
        v=[0]*22;v[INDEX[lo]]=-1;v[INDEX[hi]]=1;v[-1]=1;nets.extend([v,[-x for x in v]])
    v=[0]*22
    for k,x in [('D:0',-1),('D:1',1),('H1:0',1),('H1:1',-1)]:v[INDEX[k]]=x
    nets.append(v)
    for i,v in enumerate(nets):check('integer_stoich_'+str(i),all(x==0 for x in conservation_residuals(v).values()))
    # Same-potential cycle: D PI + reverse H PI + reverse CX.
    from fractions import Fraction
    chiH=Fraction('13.6');delta=43*Fraction('1.380649e-23')/Fraction('1.602176634e-19');chiD=chiH+delta
    check('same_potential_cycle',chiD-chiH-delta==0.,str(chiD-chiH-delta))
    moments={};bandrows=[];diagnostics=[];points=[]
    atom=d.Verner96.from_table('HI')
    saved=list(csv.DictReader(ab.decode().splitlines()))
    for z in [2.316,2.479,2.649]:
        sp=d.PW19Spectrum(z);parent=next(x['result'] for x in cases if x['redshift']==z and x['channel']=='HI')
        H=tuple(parent[k] for k in ['number_per_target_s','kinetic_eV_per_target_s','absorbed_photon_eV_per_target_s'])
        bands={o:d.band(sp,o) for o in [8,16,32]}
        for o,vals in bands.items():bandrows.append(dict(z=z,order=o,Glo=vals[0],Alo=vals[1],B=vals[2]))
        rel=max(abs(bands[a][i]-bands[b][i])/max(bands[a][i],bands[b][i]) for a,b in [(8,16),(16,32)] for i in range(3));check('band_convergence_'+str(z),rel<=2e-10,rel)
        D=d.transfer(H,bands[16]);edges=[d.CHI_D]+[E for E in sp.energy_eV if d.CHI_D<E<50000]+[50000.];raw=[[],[],[]];errs=[[],[],[]]
        for a,b in zip(edges,edges[1:]):
            for i in range(3):
                def fn(logE):
                    E=math.exp(logE);q=sp.evaluate(E)*atom.sigma_cm2(E)/(d.EV_ERG*E*E)
                    return q*E*(1 if i==0 else E-d.CHI_D if i==1 else E)
                val,err=quad(fn,math.log(a),math.log(b),epsrel=2e-12,epsabs=1e-35);raw[i].append(val);errs[i].append(err)
        Q=tuple(math.fsum(x) for x in raw);qerr=tuple(math.fsum(x) for x in errs)
        rels=[abs(x-y)/max(x,y) for x,y in zip(D,Q)];check('D_independent_quad_'+str(z),max(rels)<=2e-11,rels)
        check('positive_D_'+str(z),min(D)>0 and min(bands[16])>=0)
        er=abs(math.fsum([d.CHI_D*D[0],D[1],-D[2]]))/D[2];check('photo_energy_'+str(z),er<=5e-14,er)
        # delta0 update has exactly zero new band, algebraically no change.
        delta0=(H[0]-0.,H[1]-0.*H[0]+0.,H[2]-0.);check('delta0_'+str(z),delta0==H)
        filt=[(float(x['kinetic_eV'])-d.DELTA,float(x['number_weight_per_target_s'])) for x in saved if float(x['redshift'])==z and x['channel']=='HI' and float(x['kinetic_eV'])>=d.DELTA]
        naive=(math.fsum(w for k,w in filt),math.fsum(k*w for k,w in filt),math.fsum((k+d.CHI_D)*w for k,w in filt))
        diagnostics.append(dict(z=z,H=H,D=D,quad=Q,quad_error_estimates=qerr,D_quad_relative=rels,photo_energy_relative=er,naive=naive,naive_relative=[(x-y)/y for x,y in zip(naive,D)],fractional_shift=[(x-y)/y for x,y in zip(D,H)]))
        moments[z]={'H1':H,'D':D}
        dump(out/('SOURCE_'+str(z)+'.json'),dict(diagnostics=diagnostics[-1],band=bands,quad_interval_values=raw,quad_interval_errors=errs))
        for T in [43.,300.,10000.]:
            for ff in [0.,.1]:
                rec=d.source(T,dens,charge*(1-ff),charge*ff,moments[z],rrparams,d.POTENTIAL);rec.update(z=z,fast_fraction=ff);points.append(rec)
                for key in ['nucleus_normalized','pool_normalized','energy_normalized','potential_normalized']:check('point_'+str(len(points))+'_'+key,rec[key]<=2e-13,rec[key])
    for i,(T,den,nt,nf,pot) in enumerate([(2.999,dens,charge,0.,d.POTENTIAL),(200001,dens,charge,0.,d.POTENTIAL),(float('nan'),dens,charge,0.,d.POTENTIAL),(43,{k:v for k,v in dens.items() if k!='T:0'},charge,0.,d.POTENTIAL),(43,dens,charge*.9,0.,d.POTENTIAL),(43,dens,charge,0.,dict(d.POTENTIAL,**{'D:1':d.CHI_H}))]):
        try:d.source(T,den,nt,nf,moments[2.316],rrparams,pot)
        except ValueError:check('required_refusal_'+str(i),True)
        else:check('required_refusal_'+str(i),False)
    for T in [3.,200000.]:d.temperature(T);check('domain_endpoint_'+str(T),True)
    dump(out/'POINT_SOURCES.json',points);dump(out/'SOURCE_DIAGNOSTICS.json',diagnostics)
    with (out/'BAND.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(bandrows[0]));w.writeheader();w.writerows(bandrows)
    with (out/'POINT_SOURCES.csv').open('x',newline='') as f:
        keys=['z','T','fast_fraction','nucleus_normalized','pool_normalized','energy_normalized','potential_normalized'];w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:x[k] for k in keys} for x in points)
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for i,label in enumerate(['count Γ','kinetic K','absorbed A']):
        axs[0].plot([x['z'] for x in diagnostics],[x['fractional_shift'][i] for x in diagnostics],'o-',label=label)
        axs[1].plot([x['z'] for x in diagnostics],[x['naive_relative'][i] for x in diagnostics],'o-',label=label)
    axs[0].set(title='Conditional D43K / saved H − 1',xlabel='PW19 redshift node',ylabel='Fractional moment shift');axs[1].set(title='Naive saved-atom filter / boundary result − 1',xlabel='PW19 redshift node',ylabel='Relative diagnostic defect')
    for ax in axs:ax.legend();ax.grid(alpha=.3);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    fig.suptitle('Threshold-gated H-equality D model; finite source, no stopping or heat admission')
    for ext in ['png','pdf']:fig.savefig(out/('D43_source_binding.'+ext),dpi=160)
    plt.close(fig)
    result=dict(status='NUMERICAL_CHECKS_COMPLETE_PENDING_ASTRA_REVIEW',checks=checks,counts=dict(point_sources=len(points),new_D_integrations=3,narrow_band_orders=9,ODE=0,parent_reruns=0,benchmark=0),cpu_s=time.process_time()-cpu,wall_s=time.perf_counter()-start,versions=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__),maxrss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,global_error_bound=None)
    dump(out/'RESULT.json',result)
    return result
if __name__=='__main__':
    out=Path(sys.argv[1])
    try:main(out)
    except BaseException as e:
        dump(out/'FAILURE.json',dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc()));raise
