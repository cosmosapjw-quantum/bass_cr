"""Numerical companion source quadrature and arbitrary-birth coupled tangent.
Gauss companion replacement and finite eta sampling are DIAGNOSTICS ONLY.
No result here is a uniform kernel/interval proof. No frozen gas replacement.
Forward DOP853 and backward RK45 solve separately on the same diagnostic base.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import sys,json,argparse,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from source_kernel import load_pins,nonphoto_rhs,sigma,T,H,NH,C,FHE,CHI,W0,EB
ST=6.6524587e-25

def setup(n,eta,weight_corner='nominal'):
 pin=load_pins();plan=pin['BIRTH_PLAN.json'];seed=pin['INITIAL.json']['seed'];p=[seed['p'][0]];b=[0.]
 for bb in plan['same_births']:
  w=plan['same_source_weight_boxes'][str(bb)];b.append(bb/T);p.append((1-eta)*w[{'nominal':'weight','lo':'lo','hi':'hi'}[weight_corner]])
 gl,gw=np.polynomial.legendre.leggauss(n)
 coeff=pin['COEFFICIENTS.json']
 def rat(v):return int(v['num'])/int(v['den'])
 for cell in coeff['cells']:
  left,right=map(rat,cell['proper_interval_s']);length=(right-left)/T
  for x,w in zip(gl,gw):b.append(left/T+(x+1)*length/2);p.append(eta*5e-15*T*length*w/2)
 b=np.array(b);mass=np.array(p);d=4+len(b);state=np.r_[seed['gas'][:3],1.,np.zeros(len(b))];state[4]=mass[0]
 events=sorted(set(b[1:]))
 def photo(u,z):
  nh=NH*np.exp(-3*H*T*u);e=(sum(EB)/2)*np.exp(-H*T*(u-b));a=T*C*nh*sigma(e)
  # Dormant p=0 for all future births; energy extrapolation never contributes.
  return a,(e-CHI[0])/W0
 def rhs(u,z):
  f,_=nonphoto_rhs(u,z[:4]);a,q=photo(u,z);kap=a*(1-z[0]);v=kap*z[4:]
  return np.r_[np.asarray(f)+np.array([sum(v),0,0,np.dot(q,v)]),-v]
 def matrix(u,z):
  A=np.zeros((d,d));a,q=photo(u,z);kap=a*(1-z[0]);phot=z[4:]
  for j in range(4):
   zz=z[:4].astype(complex);zz[j]+=1e-25j
   A[:4,j]=np.imag(np.asarray(nonphoto_rhs(u,zz)[0]))/1e-25
  A[0,0]-=np.dot(a,phot);A[3,0]-=np.dot(q*a,phot)
  A[0,4:]=kap;A[3,4:]=q*kap;A[4:,0]=a*phot
  A[4:,4:]=np.diag(-kap)
  return A
 segments=[];left=0.;calls=0
 for right in [*events,1.]:
  sol=solve_ivp(rhs,(left,right),state,method='DOP853',rtol=2e-12,atol=2e-15,dense_output=True)
  if not sol.success:raise ValueError(sol.message)
  segments.append((left,right,sol));calls+=sol.nfev;state=sol.y[:,-1].copy()
  if right<1:state[4:]+=np.where(b==right,mass,0)
  left=right
 def base(u):
  # Physical right trace at injection. Gas is continuous; photons jump.
  i=np.searchsorted([s[1] for s in segments],u,side='right');i=min(i,len(segments)-1)
  return segments[i][2].sol(u)
 return dict(b=b,mass=mass,segments=segments,base=base,matrix=matrix,d=d,calls=calls,final=state)

def response(model,birth):
 d=model['d'];state=np.zeros(d+2);state[d]=1;forward_calls=0
 segments=[(max(l,birth),r) for l,r,_ in model['segments'] if r>birth]
 def forcing(u,z):
  e=(sum(EB)/2)*np.exp(-H*T*(u-birth));a=T*C*NH*np.exp(-3*H*T*u)*sigma(e);kap=a*(1-z[0]);q=(e-CHI[0])/W0
  f=np.zeros(d);f[0]=kap;f[3]=q*kap
  return f,kap
 def goal(u):
  g=np.zeros(d);g[:3]=T*C*ST*NH*np.exp(-3*H*T*u)*np.array([1,FHE,2*FHE]);return g
 def forward(u,v):
  z=model['base'](u);A=model['matrix'](u,z);f,k=forcing(u,z)
  return np.r_[A@v[:d]+f*v[d],-k*v[d],np.dot(goal(u),v[:d])]
 for l,r in segments:
  sol=solve_ivp(forward,(l,r),state,method='DOP853',rtol=1e-11,atol=np.r_[np.full(d,2e-14),2e-14,2e-26])
  if not sol.success:raise ValueError(sol.message)
  state=sol.y[:,-1];forward_calls+=sol.nfev
 lam=np.zeros(d+1);backward_calls=0
 def backward(u,v):
  z=model['base'](u);A=model['matrix'](u,z);f,k=forcing(u,z)
  return np.r_[-A.T@v[:d]-goal(u),-np.dot(f,v[:d])+k*v[d]]
 for l,r in reversed(segments):
  sol=solve_ivp(backward,(r,l),lam,method='RK45',rtol=3e-12,atol=2e-26)
  if not sol.success:raise ValueError(sol.message)
  lam=sol.y[:,-1];backward_calls+=sol.nfev
 rel=abs(state[-1]-lam[-1])/max(abs(state[-1]),1e-30)
 if rel>2e-7:raise ValueError('FORWARD_BACKWARD_DIAGNOSTIC_DISAGREE')
 return {'birth_proper_s':birth*T,'forward_K':float(state[-1]),'backward_K':float(lam[-1]),'relative_gap':float(rel),'forward_nfev':forward_calls,'backward_nfev':backward_calls,'survival_final':float(state[d]),'probe_is_arbitrary':True}

def run(n):
 rows=[]
 # One interior arbitrary birth and physical traces at source/output boundaries.
 # Sampling diagnoses continuity; it does not enclose jumps or derivatives.
 births=[0.,.123456789,187029267.95272577/T,698002730.5019861/T,885031998.4547119/T]
 for eta in [0.,.5,1.]:
  model=setup(n,eta);out=[response(model,b) for b in births]
  rows.append(dict(eta=eta,companion_quadrature_per_cell=n,positive_total_mass=float(sum(model['mass'])),base_nfev=model['calls'],final_gas=model['final'][:4].tolist(),responses=out))
 return {'classification':'FINITE_SAMPLING_AND_COMPANION_QUADRATURE_DIAGNOSTIC_ONLY','signed_measure':'continuous-minus-discrete','goal_identity':'eta integral required; sampled eta=0,.5,1 is not its proof','rows':rows,'kernel_uniform_proof':False,'source_bound':None,'numerical_methods':['base and forward DOP853','independent backward RK45'],'reduction':'fixed index order single thread','gas_feedback':'nonphoto Jacobian + current photons + companion photon response + survival-memory'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--n',type=int,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args();start=time.monotonic();r=run(x.n);r['elapsed_s']=time.monotonic()-start
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print('DIAGNOSTIC',x.n,'max_relative_gap',max(y['relative_gap'] for row in r['rows'] for y in row['responses']),'elapsed',r['elapsed_s'])
