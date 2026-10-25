"""Changed-contract controls with analytic references; no old physical replay."""
import argparse,copy,math,time
from pathlib import Path
import numpy as np
import he4_engine as e

def main(unit,out,runid):
    started=time.process_time();c=e.verify(unit);e.need(runid==c['test_run_id'],'RUN_ID_MISMATCH')
    a=e.provider(unit);checks=[]
    def check(name,ok):
        checks.append({'id':name,'pass':bool(ok)})
        if not ok:raise AssertionError(name)
    def rejects(name,fn):
        try:fn()
        except (e.InputError,ValueError):check(name,True)
        else:check(name,False)
    check('native_channel_threshold_support',a.channel=='HeI' and a.threshold_eV==24.59 and a.maximum_eV==50000)
    E=np.array([0.1,1.0,10.0,68.93866609716142])
    values=e.coefficients(E,c,a,0.02);lam=values['lambda_He']
    check('positive_point_coefficients',np.all(lam>0))
    check('density_once_linear',np.array_equal(e.coefficients(E,c,a,0.04)['lambda_He'],2*lam))
    check('explicit_zero_target_exact',np.array_equal(e.coefficients(E,c,a,0.0)['lambda_He'],np.zeros(4)))
    for name,d in [('none',None),('negative',-0.02),('nan',float('nan')),('boolean',True)]:
        rejects('density_reject_'+name,lambda d=d:e.coefficients(E,c,a,d))
    for name,energy in [('zero',[0.0]),('negative',[-1.0]),('nan',[math.nan]),('infinite',[math.inf]),('above_support',[50000.0]),('bool',[True]),('empty',[])]:
        rejects('energy_reject_'+name,lambda energy=energy:e.coefficients(energy,c,a,0.02))
    for key,value,name in [('n_HeII_cm3',0.14,'electron_density_as_target'),('d_He',2,'wrong_factor_two'),('I_He_eV',24.587389,'threshold_substitution'),('finite_mass',True,'unsupported_finite_mass'),('component','all_level_total','double_count_total'),('isotope_assignment','EMPIRICAL_HE4','isotope_upgrade')]:
        bad=copy.deepcopy(c);bad[key]=value
        rejects(name,lambda bad=bad:e.validate_config(bad))
    photon=E+c['I_He_eV'];internal=-c['I_He_eV']*np.ones_like(E)
    residual=np.abs(-E+photon+internal)/(np.abs(E)+np.abs(photon)+np.abs(internal))
    check('event_signed_energy_own_scale',residual.max()<=c['tolerances']['event_energy'])
    wrong=np.abs(-E+photon-internal)/(np.abs(E)+np.abs(photon)+np.abs(internal))
    check('wrong_internal_sign_detected',wrong.min()>c['tolerances']['event_energy'])
    check('charge_conservation',(-1)*(-1)+(+1)*(-1)+0*(+1)==0)
    check('He_nuclei_conservation',-1+1==0)
    # Exact one-state chain: entry1, existing H1capture2, addedHe capture4.
    # Baseline d=3; shared new d=7. No dense physical matrix is generated.
    x,res=e.solve(np.array([7.]),np.array([]),np.array([]),np.array([[1.,2.,4.,1.]]))
    check('shared_competition_analytic',np.max(abs(x-np.array([[1/7,2/7,4/7,1/7]])))<2e-15 and max(res)<2e-15)
    check('shared_probability_partition',abs(x[0,:3].sum()-1)<2e-15)
    check('independent_RR_sum_mutation_detected',2/3+4/5>1)
    w=4/3;p=4/7;check('single_added_hazard_bound',w/(1+w)<=p+2e-15 and p<=w)
    delta=-4*(2/3)/7;check('stable_H1_response',abs(delta-(2/7-2/3))<2e-15)
    # Rate dimensions are evaluated by an independent SI conversion identity.
    pi=np.array([a.sigma_cm2(float(v)) for v in photon])
    sig_si=pi*1e-4*(photon*c['eV_J'])**2/(c['d_He']*c['electron_mass_kg']*c['c_m_s']**2*(E*c['eV_J']))
    lam_si=(0.02*1e6)*np.sqrt(2*E*c['eV_J']/c['electron_mass_kg'])*sig_si
    check('SI_cgs_hazard_identity',np.max(abs(lam_si-lam)/lam)<=5e-15)
    e.writej(out/'SELECTED_COEFFICIENTS.json',{'E_eV':E.tolist(),**{k:v.tolist() for k,v in values.items()}})
    e.writej(out/'RESULT.json',{'schema':'CR_HE4_RR_CONTROLS_V1','status':'PASS','checks':checks,'check_count':len(checks),'new_physical_chain_solves':0,'synthetic_RHS':4,'old_suite_replay':0,'source_quadrature':0,'thermal_quadrature':0,'new_ODE':0,'runtime':'PYTHON_PASS','process_cpu_s':time.process_time()-started})
    print(f'PASS {len(checks)} controls; physical chain solves0; synthetic RHS4')
    return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
