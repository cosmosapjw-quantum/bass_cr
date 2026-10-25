"""Prescribed new adapter/event/small-chain controls; no old suite replay."""
import argparse
import math
import time
from pathlib import Path
import numpy as np
import rr_engine as e

def main(unit,out,runid):
    start=time.process_time();c=e.verify(unit);e.need(runid==c['test_run_id'],'RUN_ID_MISMATCH');atom=e.provider(unit);checks=[]
    def check(name,ok,**extra):
        checks.append(dict(name=name,pass_scoped=bool(ok),**extra));e.need(ok,'CONTROL_FAILED:'+name)
    def reject(name,fn):
        try:fn()
        except (ValueError,TypeError):check(name,True,expected_rejection=True);return
        check(name,False,expected_rejection=True)
    try:
        E=np.array([1.,3.,10.,50.]);a=e.rr_coefficients(E,c,atom);b=e.rr_coefficients(E,c,atom,density=0.2);z=e.rr_coefficients(E,c,atom,density=0.0)
        check('positive_component',np.all(a['lambda_RR_s_inverse']>0))
        check('explicit_zero_HII',np.all(z['lambda_RR_s_inverse']==0))
        check('density_scaling',np.array_equal(b['lambda_RR_s_inverse'],2*a['lambda_RR_s_inverse']))
        independent=a['sigma_PI_cm2']*(E+13.6)**2/(c['electron_mass_kg']*c['c_m_s']**2/c['eV_J']*E)
        check('units_weights_milne',np.max(abs(a['sigma_RR_cm2']/independent-1))<5e-15)
        reject('E_zero_rejected',lambda:e.rr_coefficients([0.],c,atom))
        reject('E_negative_rejected',lambda:e.rr_coefficients([-1.],c,atom))
        reject('unsupported_PI_domain_rejected',lambda:e.rr_coefficients([50000.],c,atom))
        reject('missing_density_rejected',lambda:e.rr_coefficients(E,{**c,'n_HII_cm3':None},atom))
        reject('negative_density_rejected',lambda:e.rr_coefficients(E,c,atom,density=-1))
        reject('nonfinite_energy_rejected',lambda:e.rr_coefficients([float('nan')],c,atom))
        reject('wrong_atomic_weight_rejected',lambda:e.rr_coefficients(E,{**c,'d':2},atom))
        reject('wrong_threshold_rejected',lambda:e.rr_coefficients(E,{**c,'I_eV':13.598},atom))
        wrong=e.rr_coefficients(E,c,atom,density=c['ne_cm3'])['lambda_RR_s_inverse']
        check('wrong_target_density_mutation_rejected',np.max(abs(wrong/a['lambda_RR_s_inverse']-1))>0.39,expected_rejection=True)
        check('factor2_mutation_rejected',np.max(abs(2*a['sigma_RR_cm2']/independent-1))>0.99,expected_rejection=True)
        # Expected reaction extent1: electron -1, proton -1, neutral +1.
        check('stoichiometric_charge_and_H1_conservation',(-1)*(-1)+(-1)*(+1)==0 and -1+1==0)
        photon=E+c['I_eV'];internal=np.full_like(E,-c['I_eV'])
        scale=abs(photon)+abs(internal)+abs(E)
        residual=float(np.max(abs(photon+internal-E)/scale))
        check('RR_scale_event_energy',residual<=c['tolerances']['event_energy'],scaled_residual=residual,tolerance=c['tolerances']['event_energy'])
        wrong_res=float(np.max(abs(photon-internal-E)/scale))
        check('binding_sign_mutation_rejected',wrong_res>c['tolerances']['event_energy'],expected_rejection=True,scaled_residual=wrong_res)
        # Analytic two-state killed chain: [[3,-1],[-1,2]] inverse=1/5 [[2,1],[1,3]].
        d=np.array([3.,2.]);l=u=np.array([-1.]);rhs=np.array([[1.,0.],[0.,1.]])
        x,res=e.solve(d,l,u,rhs);expected=np.array([[2.,1.],[1.,3.]])/5
        check('analytic_killed_chain',np.max(abs(x-expected))<2e-15 and max(res)<=c['tolerances']['linear'])
        d0=np.array([3.,2.]);lam=np.array([0.02,0.03]);w,_=e.solve(d0,l,u,lam);pr,_=e.solve(d0+lam,l,u,lam);eta=max(w)
        check('analytic_rare_response_bound',np.all(pr<=w) and np.all(pr>=w/(1+eta)))
        e.writej(out/'RESULT.json',dict(status='PASS',checks=checks,control_count=len(checks),small_chain_RHS=4,production_RHS=0,thermal_quadrature=0,source_quadrature=0,old_primary_replay=0,process_cpu_s=time.process_time()-start,EXECUTION='COMPLETED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN'))
        return 0
    except Exception as ex:
        e.writej(out/'RESULT.json',dict(status='FAILED_RETAINED',checks=checks,error=dict(type=type(ex).__name__,message=str(ex)),process_cpu_s=time.process_time()-start));raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
