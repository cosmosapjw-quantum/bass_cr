"""Bounded new coefficient controls; no inherited suite or primary replay."""
import argparse,copy,hashlib,importlib.util,json,math,tempfile,time
from pathlib import Path
import numpy as np
from scipy.special import gammainc
from scipy.integrate import quad
import engine as e

def main(unit,out,run_id):
    t=time.process_time();quadratures_started=0;c=e.verify(unit);e.need(run_id==c['test_run_id'],'RUN_ID_MISMATCH');checks=[]
    def check(name,ok,**data):
        checks.append(dict(id=name,pass_scoped=bool(ok),**data))
        if not ok:e.writej(out/'FAILED_CONTROL.json',dict(status='FAILED_RETAINED',checks=checks,new_coefficient_validation_quadratures=quadratures_started,source_quadrature=0,thermalrate_provider_quadrature=0,process_cpu_s=time.process_time()-t))
        e.need(ok,'CONTROL_FAILED:'+name)
    def rejected(name,fn):
        try:fn()
        except e.InputError:check(name,True);return
        check(name,False)
    # Exercise the real immutable-input validator with altered source bytes.
    with tempfile.TemporaryDirectory(dir=out) as temp:
        fake=Path(temp);(fake/'inputs').mkdir();payload=b'altered-source-bytes';(fake/'inputs/source').write_bytes(payload)
        manifest=dict(files=[dict(path='inputs/source',bytes=len(payload),sha256=hashlib.sha256(b'original-source').hexdigest())])
        (fake/'inputs/INPUT_MANIFEST.json').write_text(json.dumps(manifest));rejected('wrong_source_hash',lambda:e.verify(fake))
        try:(fake/'inputs').mkdir(exist_ok=False)
        except FileExistsError:check('create_only_run_path_reuse_rejected',True)
        else:check('create_only_run_path_reuse_rejected',False)
    for field,value in [('units',dict(c['units'],E='keV')),('frame','laboratory moving frame'),('clock','coordinate seconds')]:
        alt=copy.deepcopy(c);alt[field]=value;rejected('wrong_'+field,lambda:e.validate_case(alt))
    E=np.array(c['coefficient_control_E_eV']);sp=copy.deepcopy(c['species'][0]);sp.update(r=1.,n_cm3=c['ne_cm3'],Z=1.)
    spec=importlib.util.spec_from_file_location('_targeted_pr59',unit/'inputs/reused/pr59/coulomb_partition.py');ref=importlib.util.module_from_spec(spec);import sys;sys.modules[spec.name]=ref;spec.loader.exec_module(ref)
    model=ref.MaxwellianCoulomb(c['anchor_energy_eV'],c['b_anchor_eV_s'],c['theta_eV'],c['lnLambda_ee'],False);mu,D=e.coefficient(E,c,sp);rm,rD,_,_=model.coefficients(E)
    err=max(float(np.max(abs((mu-rm)/rm))),float(np.max(abs((D-rD)/rD))));check('r1_PR59_targeted_coefficients',err<=c['tolerances']['r1'],relative_error=err,positive_E_eV=E.tolist())
    base=c['species'][0];mu,D=e.coefficient(E,c,base)
    for label,field,factor,power in [('density','n_cm3',3.,1),('charge_square','Z',2.,2)]:
        alt=dict(base);alt[field]*=factor;m,d=e.coefficient(E,c,alt);err=max(float(np.max(abs(m-factor**power*mu)/(abs(mu)*factor**power))),float(np.max(abs(d-factor**power*D)/(D*factor**power))));check(label,err<=5e-14,relative_error=err)
    for field in ['n_cm3','Z']:
        alt=dict(base);alt[field]=0.;m,d=e.coefficient(E,c,alt);check('explicit_zero_'+field,np.all(m==0)&np.all(d==0))
    for field in ['n_cm3','Z','r','theta_eV','lnLambda']:
        alt=dict(base);alt[field]=None;rejected('null_'+field,lambda:e.coefficient(E,c,alt))
    alt=copy.deepcopy(c);alt['species'][0]['T_K']*=2;rejected('different_T_consumer',lambda:e.validate_case(alt));alt=copy.deepcopy(base);alt['theta_eV']*=2;m,d=e.coefficient(E,c,alt);check('different_T_single_coefficient_valid',np.all(np.isfinite(m))&np.all(d>0))
    check('charge_sum',abs(sum(s['n_cm3']*s['Z'] for s in c['species'])-c['ne_cm3'])<=c['tolerances']['charge'])
    x=np.array([1e-16,1e-12,1e-8]);series=4*x**1.5/(3*math.sqrt(math.pi))*(1-3*x/5+3*x*x/14);a=gammainc(1.5,x);err=float(np.max(abs(a-series)/series));check('small_x_positive_series',np.all(a>0) and err<2e-14,relative_error=err)
    high=np.array([1.,10.,100.]);m,d=e.coefficient(high,c,base);b=c['b_anchor_eV_s']*np.sqrt(c['anchor_energy_eV']/high)*e.eta(c,base);err=max(float(np.max(abs(m+b/base['r'])/(b/base['r']))),float(np.max(abs(d-c['theta_eV']*b/base['r'])/(c['theta_eV']*b/base['r']))));check('high_x_heavy_mass_limit',err<5e-14,relative_error=err)
    heavy=dict(base,r=base['r']*10);hm,hD=e.coefficient(high,c,heavy);check('inverse_mass_high_energy',np.allclose(hm*10,m,rtol=5e-14,atol=0) and np.allclose(hD*10,d,rtol=5e-14,atol=0))
    # Five-point derivative is independent of the production analytic drift expression.
    points=np.array([1e-5,1e-3,.1,1.]);h=points*2e-4
    d_m2=e.coefficient(points-2*h,c,base)[1];d_m=e.coefficient(points-h,c,base)[1];d_p=e.coefficient(points+h,c,base)[1];d_p2=e.coefficient(points+2*h,c,base)[1]
    deriv=(d_m2-8*d_m+8*d_p-d_p2)/(12*h);m,d=e.coefficient(points,c,base);eq=deriv+d*(.5/points-1/base['theta_eV']);err=float(np.max(abs(m-eq)/(abs(m)+abs(deriv)+abs(d*(.5/points-1/base['theta_eV'])))));check('Maxwell_equilibrium_identity',err<2e-10,scaled_error=err)
    # Scalar quadrature is a coefficient-control oracle, never a physical source/rate database.
    thermal=[]
    for ratio in [.5,1.,2.]:
        quadratures_started+=1
        with (out/'COEFFICIENT_QUADRATURE_ATTEMPTS.jsonl').open('a') as log:log.write(json.dumps(dict(attempt=quadratures_started,theta_population_to_bath_ratio=ratio,status='STARTED'))+'\n')
        tt=c['theta_eV']*ratio;C=c['b_anchor_eV_s']*math.sqrt(c['anchor_energy_eV'])*e.eta(c,base)
        exact=2*C*(base['theta_eV']-tt)/(math.sqrt(math.pi)*base['r']*(tt+base['theta_eV']/base['r'])**1.5)
        def integrand(y):
            energy=tt*y;return float(e.coefficient(energy,c,base)[0])*2*math.sqrt(y)*math.exp(-y)/math.sqrt(math.pi)
        # Split at the narrow ion-bath thermal scale to resolve its heating contribution.
        split=base['theta_eV']/(base['r']*tt)
        val=sum(quad(integrand,a,b,epsabs=1e-17,epsrel=1e-9,limit=100)[0] for a,b in [(0,split),(split,1),(1,math.inf)])
        scale=2*C/(math.sqrt(math.pi)*base['r']*math.sqrt(tt));err=abs(val-exact)/scale
        good=err<2e-9 and (ratio==1 or val*(1-ratio)>0);thermal.append(dict(theta_population_eV=tt,numerical_mu_eV_s=val,analytic_mu_eV_s=exact,noncancelling_scaled_error=err));check('thermal_exchange_'+str(ratio),good,**thermal[-1])
    e.writej(out/'TEST_RESULT.json',dict(status='PASS',checks=checks,new_combined_matrices=0,new_primary_RHS=0,old_generator_calls=0,old_suite_replay=0,new_coefficient_validation_quadratures=quadratures_started,coefficient_validation_integrator_interval_calls=3*quadratures_started,source_quadrature=0,thermalrate_provider_quadrature=0,process_cpu_s=time.process_time()-t))
    return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))
