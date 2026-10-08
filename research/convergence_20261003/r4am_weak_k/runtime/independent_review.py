"""Read-only independent algebra and interval-result review.
Does not import the producer or run an atomic integral.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math
import sympy as s
RDIR=Path(__file__).resolve().parents[1]
count=0

def check(b):
    global count
    assert b
    count+=1

def endpoint(d):
    # Immutable dyadic serialization contains explicit rational endpoints.
    if isinstance(d,list):return tuple(F(x) for x in d)
    scale=1 << d['denominator_power2']
    return F(int(d['lower_numerator']),scale),F(int(d['upper_numerator']),scale)

def main():
    # Origin material-coordinate Jacobian: r_other=R+r*eta.
    r,R,e=s.symbols('r R e',positive=True,real=True)
    aT=-e+r*(1-e*e)/(2*R);aP=e-r*(1-e*e)/(2*R)
    for aa in (aT,aP):
        check(s.simplify(s.diff(aa,e)**2-(1+r*e/R)**2)==0)
    # Exact first-panel cancellation, independently in physical r powers.
    c=s.symbols('c1:5');u=sum(c[j-1]*r**j for j in range(1,5));f=u/r
    check(s.simplify(s.diff(f,r)-(s.diff(u,r)/r-u/r**2))==0)
    check(s.limit(f,r,0)==c[0])
    # Gradients with phi=F(r)*c.n. The regular polynomial field formula has
    # r*grad = rF' (c.n)n + F(c-(c.n)n).
    x,y,z=s.symbols('x y z',real=True);rr=s.sqrt(x*x+y*y+z*z)
    cx,cy,cz=s.symbols('cx cy cz');cf=cx*x+cy*y+cz*z
    ff=sum(c[j]*rr**j for j in range(4));cn=cf/rr
    for j,coord in enumerate((x,y,z)):
        expected=rr*sum(k*c[k]*rr**(k-1) for k in range(1,4))*cn*coord/rr+ff*((cx,cy,cz)[j]-cn*coord/rr)
        check(s.simplify(rr*s.diff(ff*cn,coord)-expected)==0)
    # Phase and kinetic/connection signs from an independent formal expansion.
    v,nu=s.symbols('v nu',real=True);ft,fp,gt,gp,hpot=s.symbols('ft fp gt gp hpot')
    kinetic=s.I*v*gt*fp/2+hpot
    dt=ft*(-v*gp-s.I*nu*fp)
    expected=kinetic+s.I*v*ft*gp-nu*ft*fp
    check(s.expand(kinetic-s.I*dt-expected)==0)
    # Independently expand the Bessel generating series through sufficient order,
    # checking the compact derivative identity coefficient by coefficient.
    k,q=s.symbols('k q');J=9
    phi0=sum((-k*k*q/4)**j/s.factorial(j)**2 for j in range(J+1))
    for n in range(5):
        compact=0
        for j in range(n//2+1):
            m=n-j;ph=sum((-k*k*q/4)**t/(s.factorial(t)*s.factorial(t+m)) for t in range(J+1))
            compact+=s.factorial(n)*ph*(-k*q/2)**(n-2*j)*(-q/4)**j/(s.factorial(n-2*j)*s.factorial(j))
        lhs=s.diff(phi0,k,n)
        check(s.series(lhs-compact,k,0,10).removeO().expand()==0)
    cov=json.loads((RDIR/'evidence/ACTUAL_COVER.json').read_text())
    # Recorded point output is arithmetic/coverage evidence, not a point-width claim.
    cover=cov.get('cover',cov)
    if 'coverage' in cov:cover=cov['coverage']
    check(cover['regular_triangles']+cover['replaced_origin_triangles']==cover['original_triangles'])
    check(cover['origin_charts']==2 and cover['dropped_regions']==0)
    check(F(cover['distance_plane_origin_area_each'])==F(cover['origin_radius_a0'])**2)
    res=json.loads((RDIR/'evidence/LIGHT_FIXTURE_RESULT.json').read_text())
    ctr=RDIR/'contracts/LIGHT_FIXTURE_CONTRACT.json'
    check(hashlib.sha256(ctr.read_bytes()).hexdigest()==res['contract_sha256'])
    contract=json.loads(ctr.read_text())
    for rel,h in contract['source_pins'].items():check(hashlib.sha256((RDIR/rel).read_bytes()).hexdigest()==h)
    for item in res['fixture_results']:
        enc=item['enclosure']
        for name,x in item['expected'].items():
            lo,hi=endpoint(enc['values'][name]['real']);il,ih=endpoint(enc['values'][name]['imag'])
            check(lo<=F(x)<=hi and il<=0<=ih)
        kap=F(64,15)/((F(enc['rho'])-1)*F(enc['rho'])**(2*enc['degree']-1))
        b=list(map(F,enc['box']));factor=2*(b[1]-b[0])/2*(b[3]-b[2])/2*kap
        for name in enc['values']:
            ml,mh=endpoint(enc['analytic_sup_u'][name]);nl,nh=endpoint(enc['analytic_sup_w'][name]);el,eh=endpoint(enc['analytic_modulus_error'][name])
            check(eh>=factor*(mh+nh))
        check(F(item['radius_l1_upper'])<=F(contract['target_per_complex_entry']))
    check(res['real_atomic_matrix_evaluations']==0)
    result={'schema':'R4AM_INDEPENDENT_READONLY_V1','status':'PASS','checks':count,
            'result_sha256':hashlib.sha256((RDIR/'evidence/LIGHT_FIXTURE_RESULT.json').read_bytes()).hexdigest(),
            'independent_of_producer_import':True,'atomic_integrals':0,'limitations':['same session, not independent human or proof assistant','primary interval library and analytic majorant proof not formally verified','no actual atomic K matrix or continuous-time error certified']}
    (RDIR/'evidence/INDEPENDENT_REVIEW.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
if __name__=='__main__':main()
