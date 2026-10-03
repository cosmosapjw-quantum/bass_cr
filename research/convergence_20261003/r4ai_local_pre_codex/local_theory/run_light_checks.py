"""New light reference checks only. Does not import or execute R4AH/Gaussian code."""
import json,math,platform,sys,time,resource,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import scipy
from scipy.integrate import quad,solve_ivp
import sympy as sp
import mpmath as mp
from cr_reion.kinetics import relative_speed_pdf_scaled,constant_sigma_mean_speed_scaled,maxwell_shell_tail_majorant
from cr_reion.core import state_error_bound,population_error_bound
from cr_reion.metric import metric_defect

root=Path(__file__).resolve().parent; out=root/'evidence'/'LIGHT_REFERENCE_RESULTS.json'
if out.exists():raise SystemExit('refusing to overwrite an existing check result')
t0=time.monotonic()
rows=[]
for a in [0,1e-8,.1,1,10,100]:
    l=max(-float(a),-12.);h=12.
    p=quad(lambda t:relative_speed_pdf_scaled(a+t,a),l,h,epsabs=1e-12,epsrel=1e-12)[0]
    m=quad(lambda t:(a+t)*relative_speed_pdf_scaled(a+t,a),l,h,epsabs=1e-12,epsrel=1e-12)[0]
    m2=quad(lambda t:(a+t)**2*relative_speed_pdf_scaled(a+t,a),l,h,epsabs=1e-11,epsrel=1e-12)[0]
    analytic=constant_sigma_mean_speed_scaled(a)
    rows.append({'a':a,'normalization':p,'mean':m,'analytic_mean':analytic,
                 'second_moment':m2,'analytic_second_moment':a*a+3,
                 'normalization_error':abs(p-1),'mean_difference':abs(m-analytic),
                 'second_relative_difference':abs(m2-(a*a+3))/(a*a+3)})
# Independent original target-speed/angular integral, rather than the collapsed PDF.
angular=[]
for a in [.1,1,10]:
    def inner(r):
        return quad(lambda mu:math.sqrt(max(0,a*a+r*r-2*a*r*mu)),-1,1,
                    epsabs=1e-10,epsrel=1e-10)[0]/2
    orig=quad(lambda r:math.sqrt(2/math.pi)*r*r*math.exp(-r*r/2)*inner(r),
              0,12,points=[a] if a<12 else None,epsabs=2e-9,epsrel=2e-9)[0]
    angular.append({'a':a,'original_velocity_integral':orig,
                    'difference_from_analytic_mean':abs(orig-constant_sigma_mean_speed_scaled(a))})
# Exact symbolic moving-metric identity for a genuinely nonorthogonal triangular basis.
t=sp.symbols('t',real=True)
T=sp.Matrix([[1,t],[0,1]]);S=T.T*T;Dt=T.T*sp.diff(T,t);h=sp.Matrix([[1,sp.I],[-sp.I,2]])
H=T.T*h*T
K=sp.simplify(sp.diff(S,t)-Dt-Dt.conjugate().T+sp.I*(H.conjugate().T-H))
assert K==sp.zeros(2)
# Small independent ODE: moving diagonal basis plus Hermitian physical Hamiltonian.
hn=np.array([[.7,.2],[.2,-.4]],complex);c0=np.array([1.,0.],complex)
def rhs(t,c):
    T=np.diag(np.exp(np.array([.15,-.1])*t));Tp=np.diag(np.array([.15,-.1]))@T
    return np.linalg.solve(T,-1j*hn@T@c-Tp@c)
sol=solve_ivp(rhs,(0,2),c0,rtol=1e-11,atol=1e-13,dense_output=True)
assert sol.success
normerr=max(abs(np.vdot(sol.sol(t),np.diag(np.exp(np.array([.3,-.2])*t))@sol.sol(t)).real-1) for t in np.linspace(0,2,31))
# Exact error-bound fixture versus independently computed constant-generator solution.
mp.mp.dps=80
bound=state_error_bound(F(1,100),[(2,F(1,5),F(3,100))])
exact=mp.exp(mp.mpf('.2'))*mp.mpf('.01')+mp.mpf('.3')*mp.expm1(mp.mpf('.2'))
assert mp.mpf(bound.numerator)/bound.denominator>=exact
result={'status':'NEW_REFERENCE_CHECKS_PASS','not_atomic_scattering':True,
 'physical_source_or_host_admitted':False,'maxwell_pdf_checks':rows,
 'independent_original_angular_checks':angular,
 'symbolic_nonorthogonal_metric_defect':str(K),
 'moving_basis_ODE':{'success':sol.success,'nfev':sol.nfev,'max_norm_error':normerr},
 'conditional_state_bound':{'upper':str(bound),'independent_value':str(exact),
                          'premises':'synthetic constant kappa/rho bounds; not a BASS trajectory certificate'},
 'tail_formula_diagnostic':{'a':10,'L':8,'probability_and_first_moment':maxwell_shell_tail_majorant(10,8),
                            'certified_floating_tail':False},
 'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                'mpmath':mp.__version__,'sympy':sp.__version__,'platform':platform.platform()},
 'wall_seconds':time.monotonic()-t0,'maxRSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
 'old_suites_replayed':0,'shifted_atomic_integrals':0,'M9_replays':0}
assert max(r['normalization_error'] for r in rows)<1e-10
assert max(r['second_relative_difference'] for r in rows)<1e-10
assert max(r['difference_from_analytic_mean'] for r in angular)<1e-7
assert normerr<1e-9
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
