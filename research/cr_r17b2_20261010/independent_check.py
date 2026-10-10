"""MPFR256 directed primitive checks and independently written MP high precision
FT03 nonphoto equations. Finite numerical checks supplement, never replace,
the directed arithmetic theorem or whole-interval tube inequalities.
"""
import sys,json,argparse,random,struct
from pathlib import Path
import gmpy2 as g
import mpmath as mp
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from interval_backend import I,AD,Jet
from source_kernel import nonphoto_rhs,sigma,W0,H,NH,T,EV,KB,FHE,CHI,DRA,DRB,probe
mp.mp.dps=110
DN=g.context(precision=256,round=g.RoundDown);UP=g.context(precision=256,round=g.RoundUp)
def op(c,f):
 with g.context(c):return f()
def m(v):return mp.mpf(v)
def independent_np(u,z):
 # Physical rates are reconstructed independently, not imported RHS functions.
 x,he1,he2,wscaled=z;w=wscaled*m(W0);xe=x+m(FHE)*(he1+2*he2)
 temp=2*m(EV)*w/(3*m(KB)*(1+m(FHE)+xe));n=m(NH)*mp.exp(-3*m(H)*T*u)
 recomb=[];ion=[];slopes=[]
 for j,lam in enumerate([315614.,570670.,1263030.]):
  ell=m(lam)/temp
  if j==1:rr=m(3e-14)*mp.power(ell,m(.654));sl=-m(.654)
  else:
   s=mp.power(ell/m(.522),m(.470));rr=(1 if j==0 else 2)*m(1.269e-13)*mp.power(ell,m(1.503))/mp.power(1+s,m(1.923));sl=-m(1.503)+m(1.923)*m(.470)*s/(1+s)
  ci=m([21.11,32.38,19.95][j])*mp.power(temp,m(-1.5))*mp.exp(-ell/2)*mp.power(ell,m([-1.089,-1.146,-1.089][j]))/mp.power(1+mp.power(ell/m([.354,.416,.553][j]),m([.874,.987,.735][j])),m([1.101,1.056,1.275][j]))
  recomb.append(n*xe*[x,m(FHE)*he1,m(FHE)*he2][j]*rr);ion.append(n*xe*[1-x,m(FHE)*(1-he1-he2),m(FHE)*he1][j]*ci);slopes.append(sl)
 die=[n*xe*m(FHE)*he1*fac*m(DRA)*mp.power(temp,m(-1.5))*mp.exp(-m(bb)/temp) for fac,bb in zip([1,m(.3)],DRB)]
 f0=ion[0]-recomb[0];f2=ion[2]-recomb[2];f1=ion[1]-recomb[1]-sum(die)-f2
 thermal=-sum(v*m(c) for v,c in zip(ion,CHI))-sum(v*m(KB)*temp*(m(1.5)+s)/m(EV) for v,s in zip(recomb,slopes))-sum(v*m(KB)*m(bb)/m(EV) for v,bb in zip(die,DRB))-2*m(H)*w
 return [T*f0,T*f1/m(FHE),T*f2/m(FHE),T*thermal/m(W0)]
def contains_mp(a,v):return mp.mpf(str(a.lo))<=v<=mp.mpf(str(a.hi))

def checks():
 rng=random.Random(1702);count=0
 for _ in range(80):
  a=rng.uniform(.05,8);b=rng.uniform(.05,8);ia=I(a);ib=I(b)
  for name,iv,fn in [('add',ia+ib,lambda x,y:x+y),('mul',ia*ib,lambda x,y:x*y),('div',ia/ib,lambda x,y:x/y)]:
   low=op(DN,lambda:fn(g.mpfr(a),g.mpfr(b)));hi=op(UP,lambda:fn(g.mpfr(a),g.mpfr(b)))
   # MPFR has fewer mantissa bits than Decimal80: independently rounded
   # representations should overlap, not be nested in one direction.
   dlo=op(DN,lambda:g.mpfr(str(iv.lo)));dhi=op(UP,lambda:g.mpfr(str(iv.hi)))
   assert dlo<=hi and low<=dhi,name;count+=1
  for iv,fn in [(ia.exp(),g.exp),(ia.ln(),g.log)]:
   lo=op(DN,lambda:fn(g.mpfr(a)));hi=op(UP,lambda:fn(g.mpfr(a)))
   assert op(DN,lambda:g.mpfr(str(iv.lo)))<=hi and lo<=op(UP,lambda:g.mpfr(str(iv.hi)));count+=1
 z=[.9,.3,.6,1.];u=.371234567;mpz=list(map(m,z));uu=m(u)
 vals=nonphoto_rhs(I(u),[AD.variable(I(v),j) for j,v in enumerate(z)])[0]
 exact=independent_np(uu,mpz);jac=0
 for j in range(4):
  assert contains_mp(vals[j].v,exact[j]),('RHS',j,vals[j].v.data(),str(exact[j]))
  for k in range(4):
   f=lambda xx:independent_np(uu,[xx if kk==k else zz for kk,zz in enumerate(mpz)])[j]
   value=mp.diff(f,mpz[k]);assert contains_mp(vals[j].g[k],value),('JAC',j,k,vals[j].g[k].data(),str(value));jac+=1
 # A source-energy/probe-memory jet includes supplied memory derivatives.
 # This checks the algebra only; it does NOT certify the missing memory jets.
 b0=187029267.95272577;time=885031998.4547119
 birth=Jet.variable(I(b0));memory=Jet([I('.0003'),I('1e-13'),I('2e-24'),I('3e-35'),I('4e-46')])
 en,surv=probe(I(time),birth,memory)
 a=sigma(en)*surv;coeff=[mp.mpf('.0003'),mp.mpf('1e-13'),mp.mpf('2e-24'),mp.mpf('3e-35'),mp.mpf('4e-46')]
 eb=13.7;en,surv=probe(I(time),birth,memory,eb=I(eb));a=sigma(en)*surv
 def direct(db):
  e=m(eb)*mp.exp(-m(H)*(m(time)-m(b0)-db));x=e/m(.4298)
  sig=m(5.475e4)*(x-1)**2*x**m(2.963/2-5.5)*(1+mp.sqrt(x/m(32.88)))**m(-2.963)*m(1e-18)
  return sig*mp.exp(-sum(v*db**k for k,v in enumerate(coeff)))
 for r,box in enumerate(a.derivatives()):assert contains_mp(box,mp.diff(direct,0,r)),('JET',r)
 # Independently differentiate all four gas rows through fourth order.
 rows=nonphoto_rhs(I(u),[Jet.variable(I(z[0]))]+[Jet([I(v)]) for v in z[1:]])[0]
 for j,row in enumerate(rows):
  for r,box in enumerate(row.derivatives()):
   expected=mp.diff(lambda xx:independent_np(uu,[xx,*mpz[1:]])[j],mpz[0],r)
   assert contains_mp(box,expected),('GAS_JET',j,r)
 return {'MPFR_directed_primitive_checks':count,'independent_RHS_values':4,'independent_nonphoto_Jacobian':jac,'probe_energy_survival_source_jets_0_to_4':5,'nonphoto_jets_0_to_4':20,'status':'PASS','independent_RHS_formula':True,'full_kernel_derivative_flow_certified':False,'MPFR_version':g.mpfr_version(),'mpmath_dps':mp.mp.dps}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();r=checks()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r))
