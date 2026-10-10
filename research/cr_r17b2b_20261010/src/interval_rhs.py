"""Same FT03 interval RHS in gas w/W0, photons/H and global u=t/T.
Full block C=-p*grad(kappa) is retained. No photon/P0 coordinate here.
"""
from pathlib import Path
import json,struct
from interval_backend import I,AD,Jet
from ad2 import D2
ROOT=Path(__file__).resolve().parents[1]
T=1250000000;H=1e-14;NH=1e-4;FHE=.083;C=29979245800.;EV=1.602176634e-12;KB=1.380649e-16
CHI=[13.598434599702,24.587389011,54.41776]
DRA=struct.unpack('<d',struct.pack('<Q',0x3f5f8b1ba9b90acb))[0]
DRB=[struct.unpack('<d',struct.pack('<Q',x))[0] for x in [0x411caf2e364afdee,0x412135e886f9cb6f]]
def exp(x):return x.exp() if hasattr(x,'exp') else __import__('numpy').exp(x)
def constant(v,like):return I(v) if isinstance(like,(I,AD,Jet,D2)) else v

def sigma(e):
 k=lambda v:constant(v,e);x=e/k(.4298)
 return k(5.475e4)*(x-1)**2*x**(2.963/2-5.5)*(1+(x/k(32.88))**.5)**(-2.963)*k(1e-18)

def nonphoto(z):
 x,y,b,q=z;k=lambda v:constant(v,q)
 w=q*k(W0);ne=x+k(FHE)*(y+2*b);temp=2*w*k(EV)/(3*k(KB)*(1+k(FHE)+ne))
 ci=[];rr=[];sl=[]
 for j,lam in enumerate([315614.,570670.,1263030.]):
  l=k(lam)/temp
  if j==1:rr.append(k(3e-14)*l**.654);sl.append(k(-.654))
  else:
   u=(l/k(.522))**.470;rr.append((2 if j==2 else 1)*k(1.269e-13)*l**1.503/(1+u)**1.923);sl.append(k(-1.503)+k(1.923)*k(.470)*u/(1+u))
  ci.append(k([21.11,32.38,19.95][j])*temp**-1.5*exp(-l/2)*l**[-1.089,-1.146,-1.089][j]/(1+(l/k([.354,.416,.553][j]))**[.874,.987,.735][j])**[1.101,1.056,1.275][j])
 dr=[fac*k(DRA)*temp**-1.5*exp(-k(v)/temp) for fac,v in zip([1,k(.3)],DRB)]
 low=[1-x,k(FHE)*(1-y-b),k(FHE)*y];high=[x,k(FHE)*y,k(FHE)*b]
 ion=[ne*low[j]*ci[j] for j in range(3)];rec=[ne*high[j]*rr[j] for j in range(3)];die=[ne*k(FHE)*y*v for v in dr]
 net=[ion[0]-rec[0],ion[1]-rec[1]-sum(die),ion[2]-rec[2]]
 kin=sum(v*k(KB)*temp*(k(1.5)+ss)/k(EV) for v,ss in zip(rec,sl));kindr=sum(v*k(KB)*k(bb)/k(EV) for v,bb in zip(die,DRB))
 return [net[0],(net[1]-net[2])/k(FHE),net[2]/k(FHE),(-sum(v*k(c) for v,c in zip(ion,CHI))-kin-kindr)/k(W0)],temp

# Immutable initial thermal normalization, read from pinned bytes at import.
W0=json.loads((ROOT/'inherited/R17B2A/inputs/donor/inputs/NEXT_CELL_INPUT.json').read_text())['seed']['gas'][3]
EB=json.loads((ROOT/'inherited/R17B2A/inputs/donor/inputs/NEXT_CELL_INPUT.json').read_text())['seed']['energy_box'][0]

def nonphoto_rhs(u,z):
 f,temp=nonphoto(z);k=lambda v:constant(v,z[3]);nh=k(NH)*exp(-3*k(H)*T*u)
 return [T*nh*f[j]-(2*k(H)*T*z[3] if j==3 else 0) for j in range(4)],temp


def physical_domain(u,z,eb):
 e=I(eb)*exp(-I(H)*T*u);temp=nonphoto(z)[1]
 tv=temp.v if hasattr(temp,'v') else temp
 if e.lo<=I(13.6).hi or e.hi>=I(24.59).lo:raise ValueError('ENERGY_BRANCH')
 if tv.lo<=30000 or tv.hi>=110000:raise ValueError('THERMAL_BRANCH')
 return e,tv

def geometry(u,z,b,eb):
 e=eb*exp(-I(H)*T*(u-b));nh=I(NH)*exp(-I(3)*H*T*u)
 a=I(T)*C*nh*sigma(e);kap=a*(1-z[0]);v=[I(1),I(0),I(0),(e-CHI[0])/W0]
 return a,kap,v

def full_blocks(u,z,photons,births,eb):
 rows,_=nonphoto_rhs(u,[D2.var(v,j) for j,v in enumerate(z)])
 n=len(photons);J=[[I(0) for _ in range(4+n)] for _ in range(4+n)]
 for i in range(4):J[i][:4]=rows[i].g.copy()
 rates=[]
 for j,(p,b) in enumerate(zip(photons,births)):
  a,kap,v=geometry(u,z,b,eb);rates.append(kap*p)
  for i in range(4):J[i][0]-=v[i]*a*p;J[i][4+j]=v[i]*kap
  J[4+j][0]=a*p;J[4+j][4+j]=-kap
 field=[r.v for r in rows]+[I(0)]*n
 for j,(p,b) in enumerate(zip(photons,births)):
  a,kap,v=geometry(u,z,b,eb)
  for i in range(4):field[i]+=v[i]*kap*p
  field[4+j]=-kap*p
 return field,J
