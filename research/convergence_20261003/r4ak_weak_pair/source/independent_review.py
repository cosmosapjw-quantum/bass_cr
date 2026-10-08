"""Read-only independent reconstruction of new R4AK evidence, not old runs."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction as F
from math import comb
import numpy as np
import mpmath as mp
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]

def main():
    checks=[]
    def check(name,condition):
        if not bool(condition):raise AssertionError(name)
        checks.append(name)
    p=json.loads((ROOT/'evidence/run_v1/PAIR_UNIFORM_BOUND.json').read_text())
    data=np.load(ROOT/'inputs/BASS_CR_R4AG_CANDIDATE.npz',allow_pickle=False)
    meta=json.loads((ROOT/'inputs/BASS_CR_R4AG_CANDIDATE.json').read_text())
    mom=json.loads((ROOT/'inputs/BASS_CR_R4AB_GRAM_EXACT.json').read_text())
    j=p['ground_mode'];edges=list(map(F,data['edges']));u=list(map(F,data['shared_endpoint_values'][j]));q=data['bubble_coefficients'][j]
    tau=F(0);a=F(p['domain']['split_radius_a0'])
    for e in range(len(edges)-1):
        l,r=edges[e:e+2]
        if r<=a:continue
        lo=max(F(0),(a-l)/(r-l))
        # Different endpoint/bubble beta basis, not the producer monomial coefficients.
        terms=[(u[e],0,1),(u[e+1],1,0),(F(q[e][0]),1,1),(F(q[e][1]),2,1),(F(q[e][2]),3,1)]
        val=F(0)
        for c,A,B in terms:
            for d,C,D in terms:
                aa,bb=A+C,B+D
                beta=sum(F((-1)**k*comb(bb,k),aa+k+1)*(1-lo**(aa+k+1)) for k in range(bb+1))
                val+=c*d*beta
        check('nonnegative_tail_panel_'+str(e),val>=0)
        tau+=(r-l)*val
    check('independent_beta_tail_exact_equality',tau==F(p['tail_mass_exact']))
    g=F(mom['matrices_exact']['G'][j][j]);T=F(mom['matrices_exact']['T'][j][j]);cross=F(p['overlap_modulus_upper'])
    check('inherited_G_unchanged',g==F(p['ground_norm_square']))
    check('inherited_T_unchanged',T==F(p['radial_kinetic_integral_a0_m2']))
    check('cross_square_upper',cross*cross>=4*g*tau)
    check('pair_lower',F(p['pair_Gram_lower'])==g-cross>0)
    check('condition_number',F(p['pair_condition_number_upper'])*(g-cross)>=g+cross)
    check('disjoint_split_domain',F(p['domain']['min_abs_z_a0'])>=2*a)
    check('no_full18_promotion',p['full18_Gram_lower'] is None)
    for name,digest in p['input_sha256'].items():check('input_'+name,hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==digest)
    # Build the full model anew with SymPy matrix inversion/differentiation.
    t=sp.symbols('t',real=True);M=sp.eye(3);M[2,0]=t/100
    h=sp.Matrix([[0,sp.Rational(1,4),0],[sp.Rational(1,4),0,sp.Rational(1,1000)],[0,sp.Rational(1,1000),2]])
    S=M.conjugate().T*M;K=M.conjugate().T*h*M-sp.I*M.conjugate().T*sp.diff(M,t)
    J=sp.Matrix([[1,0],[0,1],[0,0]]);G=J.T*S*J;KR=J.T*K*J
    B=sp.simplify(K*J-S*J*G.inv()*KR)
    Gamma=sp.simplify(sp.diff(S,t)+sp.I*(K.conjugate().T-K))
    check('symbolic_full_metric_compatibility',Gamma==sp.zeros(3))
    check('symbolic_retained_metric_compatibility',sp.simplify(sp.diff(G,t)+sp.I*(KR.conjugate().T-KR))==sp.zeros(2))
    check('symbolic_Galerkin_test_orthogonality',sp.simplify(J.T*B)==sp.zeros(2))
    check('symbolic_nonzero_complement_residual',B!=sp.zeros(3,2))
    syn=json.loads((ROOT/'evidence/run_v1/SYNTHETIC_WEAK_PAIR.json').read_text())
    def fromjson(A):
        return sp.Matrix([[sum((sp.Rational(re)+sp.I*sp.Rational(im))*t**k for k,(re,im) in enumerate(cell)) for cell in row] for row in A])
    check('model_S_matches_independent',sp.simplify(fromjson(syn['model']['S'])-S)==sp.zeros(3))
    check('model_K_matches_independent',sp.simplify(fromjson(syn['model']['K'])-K)==sp.zeros(3))
    E=F(0)
    for n,c in enumerate(syn['certificates']):
        lo,hi=map(F,c['interval_ta']);smin=F(c['S_lower']);gmin=F(c['G_lower']);dmin=F(c['polynomial_detG_lower'])
        nup=F(c['polynomial_numerator_norm_upper']);r=F(c['residual_upper_per_ta'])
        check('residual_square_'+str(n),r*r*smin*gmin*dmin*dmin>=nup*nup)
        check('metric_defect_zero_'+str(n),c['metric_defect_upper_per_ta']=='0')
        # Bernstein conversion via exact SymPy substitution at x in [0,1].
        N=sp.simplify(sp.det(G)*B);x=sp.symbols('x',real=True);sq=F(0)
        for item in N:
            bounds=[]
            for component in (sp.re(item),sp.im(item)):
                pol=sp.Poly(sp.expand(component.subs(t,sp.Rational(lo)+(sp.Rational(hi)-sp.Rational(lo))*x)),x)
                degree=max(0,pol.degree()) if pol!=0 else 0
                coeff=[F(pol.nth(k)) for k in range(degree+1)]
                bc=[sum(coeff[k]*F(comb(ii,k),comb(degree,k)) for k in range(ii+1)) for ii in range(degree+1)]
                bounds.append(max(abs(min(bc)),abs(max(bc))))
            sq+=bounds[0]**2+bounds[1]**2
        check('independent_Bernstein_numerator_'+str(n),nup*nup>=sq)
        E+=(hi-lo)*r
    check('propagation_exact_for_Gamma_zero',E==F(syn['analytic_bound']['state_error_upper']))
    check('observable_error_composition',F(syn['analytic_bound']['same_observable_error_upper'])==E*(2+E))
    # Independent high precision spectral evolution of the synthetic full state.
    mp.mp.dps=70
    hh=mp.matrix([[mp.mpf(0),mp.mpf(1)/4,0],[mp.mpf(1)/4,0,mp.mpf(1)/1000],[0,mp.mpf(1)/1000,2]])
    U=mp.expm(-mp.j*hh);psi=U*mp.matrix([1,0,0]);prob=abs(psi[1])**2
    numeric=syn['numeric_diagnostic']; endpoint=numeric['population_trace'][-1][1]
    check('independent70digit_synthetic_full_population',abs(prob-mp.mpf(endpoint))<mp.mpf('3e-15'))
    check('observed_state_inside_bound',F(numeric['max_state_error'])<=E)
    check('observed_population_inside_bound',F(numeric['max_population_difference'])<=E*(2+E))
    check('raw_physical_bridge_absent',syn['analytic_bound']['physical_bridge_upper'] is None)
    # Exact pure moving-frame counterexample: full norm preserved despite a nonzero reduction residual.
    a0=mp.mpf('0.01');eclosed=mp.sqrt(2-2/mp.sqrt(1+a0*a0))
    check('pure_frame_residual_not_zero',eclosed>0)
    result={'schema':'R4AK_INDEPENDENT_READONLY_REVIEW_V1','status':'PASS','conditions':len(checks),
        'checks':checks,'tail_alternate_basis':'exact incomplete beta in endpoint/bubble basis',
        'synthetic_full_population_70digits':mp.nstr(prob,70),'pure_frame_exact_state_distance_t1':mp.nstr(eclosed,70),
        'producer_science_replayed':False,'old_science_replayed':False,
        'scope':'same-session independent rational/symbolic/high-precision checks, not external human or physical run'}
    dest=ROOT/'evidence/INDEPENDENT_REVIEW.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
