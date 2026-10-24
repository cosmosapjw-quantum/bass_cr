"""Unexecuted v3 neutral contract controls; no physical matrix replay."""
import argparse,copy,json,time
from pathlib import Path
import numpy as np
import engine_v3 as e

def main(unit,out,runid):
    start=time.process_time();c=e.verify(unit);e.need(runid==c['test_run_id'],'RUN_ID_MISMATCH');checks=[]
    def check(name,condition):
        checks.append(dict(name=name,pass_scoped=bool(condition)));e.need(condition,name)
    def rejects(name,fn):
        try:fn()
        except e.InputError:check(name,True);return
        check(name,False)
    tables={s['label']:e.parse_mtcs(unit/s['input'],s) for s in c['neutral_species']}
    check('input_hashes_and_MTCS_support_rows_units_targets',True)
    bad=copy.deepcopy(c);bad['neutral_species'][0]['T_K']+=1
    rejects('unequal_temperature_rejected',lambda:e.validate_case(bad))
    bad=copy.deepcopy(c);bad['neutral_species'].pop()
    rejects('missing_species_rejected',lambda:e.validate_case(bad))
    bad=copy.deepcopy(c);bad['neutral_species'][0]['n_cm3']=None
    rejects('null_density_rejected',lambda:e.validate_case(bad))
    bad=copy.deepcopy(c);bad['units']['density']='m^-3'
    rejects('wrong_density_units_rejected',lambda:e.validate_case(bad))
    for sp in c['neutral_species']:
        tab=tables[sp['label']];x,y=tab;q=1.5*c['theta_eV'];E=np.array([q,2*q,10.]);slope=np.zeros(3);sig=np.full(3,2e-20);th=c['theta_eV']
        rejects(sp['label']+'_outside_upper_support',lambda:e.interpolate(np.array([x[-1]+1]),tab))
        rejects(sp['label']+'_outside_lower_support',lambda:e.interpolate(np.array([x[0]/2]),tab))
        value,der=e.interpolate(x,tab)
        check(sp['label']+'_knots_exact',np.allclose(value,y,rtol=2e-15,atol=0))
        expected=np.r_[np.diff(y)/np.diff(x),(y[-1]-y[-2])/(x[-1]-x[-2])]
        check(sp['label']+'_right_derivative_last_left',np.array_equal(der,expected))
        mu,D,nu=e.leading(E,sig,slope,th,sp['n_cm3'],sp['r'],c)
        check(sp['label']+'_constant_sigma',np.allclose(mu,2/sp['r']*nu*(2*th-E),rtol=2e-15,atol=0))
        check(sp['label']+'_SI_speed_and_density',np.allclose(nu,sp['n_cm3']*1e6*np.sqrt(2*E*c['eV_J']/c['electron_mass_kg'])*sig,rtol=2e-15,atol=0))
        for a in [-.5,1.,2.]:
            sig=2e-20*(E/q)**a;slope=a*sig/E
            mu,D,nu=e.leading(E,sig,slope,th,sp['n_cm3'],sp['r'],c)
            check(sp['label']+f'_power_{a}',np.allclose(mu,2/sp['r']*nu*(th*(2+a)-E),rtol=3e-15,atol=1e-30))
            Dprime=D*(1.5+a)/E;logpi=.5/E-1/th
            check(sp['label']+f'_Maxwell_zero_flux_{a}',np.all(abs(mu-Dprime-D*logpi)<=2e-14*(abs(mu)+abs(Dprime)+abs(D*logpi))))
        z=e.leading(E,sig,slope,th,0.,sp['r'],c)
        check(sp['label']+'_zero_density',all(np.all(v==0) for v in z))
        z=e.leading(E,sig,slope,th,sp['n_cm3'],float('inf'),c)
        check(sp['label']+'_infinite_mass',np.all(z[0]==0)&np.all(z[1]==0))
        mu,D,nu=e.leading(E,sig,slope,0.,sp['n_cm3'],sp['r'],c)
        check(sp['label']+'_cold_recoil_sign_and_factor',np.all(mu<0)&np.all(D==0)&np.allclose(mu,-2/sp['r']*E*nu,rtol=2e-15,atol=0))
        m,d,n=e.coefficient(np.array([1e-12,q]),c,sp,tab,q)
        check(sp['label']+'_subq_null_no_extrapolation',np.isnan(m[0]) and np.isnan(d[0]) and np.isnan(n[0]) and np.isfinite(m[1]) and d[1]>0)
    pi=np.array([.2,.3,.5]);g,ch=e.generator(np.array([.4,.7]),pi)
    check('synthetic_generator_detailed_balance_conservation',max(ch.values())<=2e-13)
    check('synthetic_energy_ownership',abs(pi@e.electron_drift(np.array([1.,2.,4.]),g))<1e-15)
    result=dict(schema='N5_NEUTRAL_CONTROLS_V3',status='PASS',run_id=runid,checks=checks,check_count=len(checks),physical_matrices=0,physical_RHS=0,synthetic_generators=1,coefficient_quadrature=0,source_quadrature=0,old_science_replay=0,new_ODE=0,process_cpu_s=time.process_time()-start)
    e.writej(out/'TEST_RESULT.json',result);print(json.dumps(result));return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True)
    a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))

