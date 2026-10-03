"""Read-only exact LDL/residual and independent high-precision fixture review."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import numpy as np
import sympy as sp
import mpmath as mp

def R(x):
 x=F(float(x));return sp.Rational(x.numerator,x.denominator)
def rf(x):return F(int(sp.numer(x)),int(sp.denom(x)))
def main():
 root=Path(__file__).resolve().parents[1];p=root/'evidence/run_v1/RESULT.json'
 result=json.loads(p.read_text());c=result['stored_matrix_certificate'];checks=[]
 def ck(name,v):
  checks.append({'name':name,'pass':bool(v)})
  if not v:raise AssertionError(name)
 with np.load(root/'inputs/BASS_CR_R4AB_INTRINSIC.npz',allow_pickle=False) as a:
  S=sp.Matrix([[R(v) for v in row] for row in a['S']]);H=sp.Matrix([[R(v) for v in row] for row in a['H0']])
 beta=sp.Rational(-126,1000);alpha=sp.Rational(-499,1000)
 # LDL is distinct from producer diagonal-dominance certificate construction.
 _,sd=S.LDLdecomposition(hermitian=False)
 _,cd=(H[1:,1:]-beta*S[1:,1:]).LDLdecomposition(hermitian=False)
 for i in range(9):ck('S_exact_LDL_positive_'+str(i),sd[i,i]>0)
 for i in range(8):ck('complement_exact_LDL_positive_'+str(i),cd[i,i]>0)
 mu=H[0,0]/S[0,0];e=sp.eye(9)[:,0];y=(H-mu*S)*e
 r2=(y.T*S.inv()*y)[0]/S[0,0]
 ck('trial_rayleigh_upper',mu<=alpha)
 ck('minmax_gap_value',F(c['gap_lower'])==rf(beta-alpha))
 ck('residual_exact_inverse_below_bound',rf(r2)<=F(c['residual_norm_square_upper']))
 ck('residual_sqrt_direction',F(c['residual_norm_upper'])**2>=rf(r2))
 ck('mapping_bound_residual_inequality',F(c['raw_trial_to_stored_ground_projector_upper'])**2*rf(beta-mu)**2>=rf(r2))
 ck('old_selector_rank_norm_one',result['old_rank5_to_rank1_projector_distance']=='1')
 ck('pair_reference_zero_measurement_gap',result['reference_cluster']['single_measurement_to_full_complement_gap']=='0')
 ck('finite_separation_gap_unassigned',result['reference_cluster']['finite_separation_gap_lower'] is None)
 ck('whole_bridge_not_filled',result['physical_bridge']['upper'] is None)
 ck('no_atomic_evaluations',result['new_atomic_integrals']==0)
 # Independent arbitrary-precision spectral exponential of the NEW fixture.
 mp.mp.dps=70
 A=mp.matrix([[0,mp.mpf(1)/4,mp.mpf(1)/1000],[mp.mpf(1)/4,0,0],[mp.mpf(1)/1000,0,2]])
 lam,U=mp.eigsy(A)
 evo=U*mp.diag([mp.exp(-6j*lam[i]) for i in range(3)])*U.T
 pf=abs(evo[1,0])**2
 ck('mpmath_vs_scipy_fixture_probability',abs(pf-result['synthetic']['projectile_population_full'])<mp.mpf('2e-14'))
 ck('reference_rabi_probability',abs(mp.sin(mp.mpf('1.5'))**2-result['synthetic']['projectile_population_reference'])<mp.mpf('2e-14'))
 ck('large_internal_transfer_despite_external_gap',pf>mp.mpf('.99'))
 ck('new_fixture_propagator_difference_below_bound',result['synthetic']['unitary_operator_difference']<float(F(result['synthetic']['conditional_bound']['state_distance_upper'])))
 # A time-dependent scalar energy gauge must cancel from the Sylvester equation.
 t=sp.symbols('t',real=True);x,b=sp.symbols('x b');er,eq=sp.symbols('er eq',real=True)
 ck('common_scalar_gauge_cancels',sp.expand((eq+t)*x-x*(er+t)-(eq-er)*x)==0)
 # Equal-rank projectors not assumed equal by name or energy label.
 ck('raw_labels_not_spectral_certificate',result['semantic_selector']['energy_labels_are_spectral_enclosures'] is False)
 out={'schema':'R4AJ_INDEPENDENT_REVIEW_V1','status':'ALL_LISTED_CHECKS_PASS','checks':checks,'check_count':len(checks),'result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'exact_generalized_residual_square':str(rf(r2)),'high_precision_fixture_probability':str(pf),'old_tests_or_atomic_replays':0,'review_limits':'exact stored matrices plus new synthetic fixture; no independent atomic integration, continuous bounds or separate human reviewer'}
 target=root/'evidence/INDEPENDENT_REVIEW.json'
 with target.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps({'checks':len(checks),'status':out['status'],'fixture_probability':str(pf)},indent=2))
if __name__=='__main__':main()
