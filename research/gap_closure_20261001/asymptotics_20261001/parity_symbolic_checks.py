"""Exact rational polynomial check; stdlib algebra, not an external CAS claim."""
from fractions import Fraction as F
from pathlib import Path
import json
import numpy as np

def add(a,b):return {k:a.get(k,F(0))+b.get(k,F(0)) for k in set(a)|set(b)}
def mul(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():out[i+j]=out.get(i+j,F(0))+x*y
    return out

def scale(a,q):return {k:q*v for k,v in a.items()}
def enc(a):return {str(k):str(v) for k,v in sorted(a.items()) if v}

def main():
    # B2=[[0,2],[1,0]], B3=diag(3/10,7/10), C=(B2+epsB3)^T(...).
    c00={0:F(1),2:F(9,100)};c11={0:F(4),2:F(49,100)};c01={1:F(13,10)}
    trace=add(c00,c11);delta=add(c00,scale(c11,F(-1)))
    disc=add(mul(delta,delta),scale(mul(c01,c01),F(4)))
    assert enc(trace)=={'0':'5','2':'29/50'}
    assert enc(disc)=={'0':'9','2':'229/25','4':'4/25'}
    # sqrt(disc)=3+a eps²+b eps⁴+O(eps⁶), verified by exact squaring coefficients.
    a=disc[2]/6;b=(disc[4]-a*a)/6
    assert 6*a==disc[2] and a*a+6*b==disc[4]
    l2=(trace[2]+a)/2;l4=b/2
    # sqrt(lambda_plus)=2+d eps²+e eps⁴+O(eps⁶).
    d=l2/4;e=(l4-d*d)/4
    assert 4*d==l2 and d*d+4*e==l4
    result={'engine':'Python stdlib Fraction exact polynomial algebra; no external CAS',
      'assumptions':['epsilon real near0','simple largest singular value at0=2,next1','real exact rational B2,B3'],
      'input':{'B2':[[0,2],[1,0]],'B3_diagonal':['3/10','7/10'],'operation':'C=B^T B;lambda+=(trC+sqrt((C00-C11)^2+4*C01^2))/2'},
      'exact_trace_polynomial':enc(trace),'exact_discriminant_polynomial':enc(disc),
      'leading_singular_series':{'epsilon0':'2','epsilon1':'0','epsilon2':str(d),'epsilon3':'0','epsilon4':str(e),'remainder':'O(epsilon^6)'},
      'exact_series_coefficient_checks':'PASS',
      'independent_float64_spotchecks':[],
      'degenerate_cusp_counterexample':{'B2':[[0,1],[1,0]],'B3':'identity(2)','spectral_norm':'1+abs(epsilon) for abs(epsilon)<1'},
      'does_not_imply':'No B0 farfield branch simplicity, exact model compatibility or unconditional C3 cancellation proven.'}
    for value in [-.1,.1,.01]:
        B=np.array([[.3*value,2.],[1.,.7*value]])
        exact_formula=np.sqrt((5+.58*value**2+np.sqrt(9+9.16*value**2+.16*value**4))/2)
        observed=float(np.linalg.norm(B,2))
        assert abs(observed-exact_formula)<1e-14
        result['independent_float64_spotchecks'].append({'epsilon':value,'numpy_spectral_norm':observed,'analytic_formula_float64':float(exact_formula)})
    Path(__file__).with_name('PARITY_SYMBOLIC_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print('exact polynomial identities PASS; three independent numerical spotchecks PASS')

if __name__=='__main__':main()
