"""Independent donor Decimal60 interval RHS and separate MP110 Hessian check.
Only direct equation evaluations are used; NO original root/IVP/suite runs.
Explicit p/P0 -> p/H and donor short clock -> full proper clock transformations.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import sys,json,argparse
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from interval_backend import I
from ad2 import D2
from interval_rhs import nonphoto_rhs,full_blocks,W0,H,NH,T,EV,KB,FHE,CHI,DRA,DRB,EB
mp.mp.dps=110
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

def check():
 z=[.9,.3,.6,1.];uu=.371234567;mpz=list(map(m,z));rows=nonphoto_rhs(I(uu),[D2.var(I(v),j) for j,v in enumerate(z)])[0]
 hchecks=0
 for i,row in enumerate(rows):
  assert contains_mp(row.v,independent_np(m(uu),mpz)[i])
  for j in range(4):
   f=lambda xx:independent_np(m(uu),[xx if k==j else v for k,v in enumerate(mpz)])[i]
   assert contains_mp(row.g[j],mp.diff(f,mpz[j]))
   for k in range(4):
    if j==k:value=mp.diff(f,mpz[j],2)
    else:
     ff=lambda xx,yy:independent_np(m(uu),[xx if l==j else yy if l==k else v for l,v in enumerate(mpz)])[i]
     value=mp.diff(ff,(mpz[j],mpz[k]),(1,1))
    assert contains_mp(row.h[j][k],value),('HESSIAN',i,j,k);hchecks+=1
 donor=ROOT/'inherited/R17B2A/inputs/donor'
 sys.path[:0]=[str(donor/'source'),str(donor/'research')]
 import cell_model as old
 import interval_decimal as di
 di.DIM=5
 # Compare independently implemented interval equations on a full clock/time
 # panel, including broad gas and photon states. Widths need not be identical.
 u=I('.1','.6');zz=[I('.89','.91'),I('.29','.31'),I('.59','.61'),I('.99','1.01')];p=I('.0498','.05')
 field,J=full_blocks(u,zz,[p],[I(0)],I(*EB))
 iv=lambda v:di.IV(str(v.lo),str(v.hi))
 s=iv(u)*di.IV(T)/old.DURATION
 states=[di.AD.var(iv(v),j) for j,v in enumerate(zz)]+[di.AD.var(iv(p)/old.P0,4)]
 ff,_=old.rhs(s,states,eb=di.IV(*EB));scale=di.IV(T)/old.DURATION
 vals=[];matrix=[]
 for i,row in enumerate(ff):
  rr=old.P0 if i==4 else di.IV(1);vals.append(row.v*scale*rr)
  matrix.append([x*scale*rr/(old.P0 if j==4 else di.IV(1)) for j,x in enumerate(row.g)])
 def overlap(a,b):assert max(mp.mpf(str(a.lo)),mp.mpf(str(b.lo)))<=min(mp.mpf(str(a.hi)),mp.mpf(str(b.hi)))
 for a,b in zip(field,vals):overlap(a,b)
 for ar,br in zip(J,matrix):
  for a,b in zip(ar,br):overlap(a,b)
 # Interval inclusion of a source-authentic point backend after all scale
 # transformations; 8 corner points verify normalization independently.
 sys.path.insert(0,str(ROOT/'inherited/R17B2A/src'));from ft03_point import Model
 import numpy as np
 model=Model([0.]);corners=0
 for time in [.1,.6]:
  for x in [.89,.91]:
   for photon in [.0498,.05]:
    state=np.array([x,.3,.6,1.,photon]);point=model.rhs(time,state);jac=model.jac(time,state)
    assert all(box.contains(float(v)) for box,v in zip(field,point))
    assert all(box.contains(float(v)) for rr,pp in zip(J,jac) for box,v in zip(rr,pp));corners+=1
 return dict(status='INDEPENDENT_INTERVAL_RHS_AND_HESSIAN_PASS',independently_written_MP_nonphoto_values=4,independently_written_MP_gradients=16,independently_written_MP_Hessians=hchecks,independent_donor_interval_RHS_components=5,independent_donor_interval_Jacobian_components=25,point_interval_inclusion_corners=corners,source_photon_coordinate='p/H',donor_photon_coordinate='p/P0',clock_conversion='s=u*T/donor_DURATION; rows multiplied by T/donor_DURATION',R16B_shared_AD_panels_used=False,old_donor_suite_runs=0,donor_code_mutations=0,interval_RHS_independent_of_new_transcription=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();r=check()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r))
