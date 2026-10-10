from pathlib import Path
from fractions import Fraction as F
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from ft03_point import *
from kernel_regularity import second_jump

def check(folder):
    r=json.loads((folder/'RESPONSE.json').read_text());ind=json.loads((folder/'INDEPENDENT.json').read_text())
    traces=json.loads((folder/'ADJOINT_BOUNDARIES.json').read_text());plan=json.loads((ROOT/'inputs/BIRTH_PLAN.json').read_text())
    cases=r['probe_cases'];checks=[]
    def require(name,condition):
        checks.append({'name':name,'pass':bool(condition)})
        if not condition:raise AssertionError(name)
    require('all_finite_probe_outputs',all(np.isfinite(p['forward']['K_tau']) for p in cases))
    nonend=[p for p in cases if p['forward']['b_u']<1]
    require('sampled_terminal_optical_response_positive',all(p['forward']['K_tau']>0 for p in nonend))
    require('sampled_terminal_temperature_response_negative',all(p['forward']['delta_temperature_K']<0 for p in nonend))
    require('forward_backward_relative_gap',max(p['dual_relative_gap'] for p in cases)<5e-11)
    require('physical_count_linearized_ledger',max(abs(p['forward']['charge_identity_residual']) for p in cases)<5e-13)
    require('background_heat_redshift_identity',max(abs(p['forward']['old_heat_identity_residual']) for p in cases)<5e-18)
    require('retained_background_photons_nonnegative_at_terminal',all(min(p['forward']['retained_existing'])>=0 for p in nonend))
    require('background_integrated_photoheat_decreases_in_samples',all(p['forward']['existing_photoheat_eV']<0 for p in nonend))
    require('T_endpoint_probe_zero_response',cases[-1]['forward']['K_tau']==cases[-1]['forward']['delta_temperature_K']==0)
    require('no_negative_base_photons',min(r['base_final'][4:11])>=0)
    require('base_gas_admissible',0<=r['base_final'][0]<=1 and r['base_final'][1]>=0 and r['base_final'][2]>=0 and sum(r['base_final'][1:3])<=1)
    require('temperature_in_pinned_band',30000<r['base_temperature_final_K']<110000)
    sel=next(p for p in cases if abs(p['forward']['b_u']-.35401279938188477)<1e-14)
    fd=[abs(p['K_tau_forward_difference']/sel['forward']['K_tau']-1) for p in r['positive_dose_checks']]
    require('positive_dose_difference_improves',fd[2]<fd[1]<fd[0]<1e-4)
    require('donor_point_backend_agreement',ind['max_rhs_relative']<3e-12 and ind['max_jac_relative']<3e-11)
    require('exact_lower_birth_jump_algebra',ind['jump_orders_0_1_2_zero'])
    require('third_derivative_counterexample_retained',ind['exact_nonzero_third_jump_example']=='-93/20000')
    exact_births=[];jgap=[]
    model=Model(np.r_[0.,np.array(plan['same_births'])/TEND])
    for j,tr in enumerate(traces[1:],1):
        g=np.array(tr['right_state'][:4]);en,a,k,V,gr=model.geometry(tr['u'],g);l=np.array(tr['adjoint']);psi=l[4+j]
        weight=plan['same_source_weight_boxes'][str(plan['same_births'][j-1])]['weight']
        e=second_jump(weight=F.from_float(weight),kappa_background=F.from_float(k[j]),grad_background=[F.from_float(v) for v in gr[j]],yield_background=[F.from_float(v) for v in V[:,j]],psi_background=F.from_float(psi),kappa_probe=F.from_float(k[j]),grad_probe=[F.from_float(v) for v in gr[j]],yield_probe=[F.from_float(v) for v in V[:,j]],psi_probe=F.from_float(psi),lambda_g=[F.from_float(v) for v in l[:4]])
        require('same_channel_K_second_jump_zero_'+str(j),e['kernel_second_jump']==0)
        require('gas_continuity_at_birth_'+str(j),tr['left_state'][:4]==tr['right_state'][:4])
        peer=next(p for p in cases if p['forward']['b_u']==tr['u'])
        gap=abs(TAU_SCALE*psi-peer['adjoint']['K_tau'])/abs(peer['adjoint']['K_tau']);jgap.append(gap)
        exact_births.append({'u':tr['u'],'opacity_term':{'num':str(e['opacity_term'].numerator),'den':str(e['opacity_term'].denominator)},'second_jump_exact':'0','direct_adjoint_photon_match_relative':gap})
    require('original_cohort_adjoint_matches_new_probe_at_birth',max(jgap)<1e-10)
    late=cases[-2]['forward'];en,aa,kk,*_=Model([1.]).geometry(1,np.array(r['base_final'][:4]));leading=.5*TAU_SCALE*np.exp(-3*H*TEND)*kk[0]
    late_ratio=late['K_tau']/(1-late['b_u'])**2/leading
    require('late_kernel_quadratic_asymptotic_diagnostic',abs(late_ratio-1)<1e-4)
    out={'status':'PASS_SCOPED_NOMINAL_PHYSICS_DIAGNOSTIC','checks':checks,'count':len(checks),'probes':len(cases),'positive_b_less_T':len(nonend),'max_dual_relative_gap':max(p['dual_relative_gap'] for p in cases),'max_charge_ledger_abs':max(abs(p['forward']['charge_identity_residual']) for p in cases),'max_old_heat_ledger_abs':max(abs(p['forward']['old_heat_identity_residual']) for p in cases),'finite_dose_relative_errors':fd,'late_coefficient':float(leading),'late_observed_ratio':late_ratio,'exact_birth_jump_samples':exact_births,'no_homotopy_uniform_certificate':True,'source_interval_unchanged':True}
    (folder/'CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('checks','exact_birth_jump_samples')},indent=2));return out
if __name__=='__main__':check(Path(sys.argv[1]))
