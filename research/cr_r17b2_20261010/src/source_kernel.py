"""Same FT03 continuum-source functional and arbitrary-birth response operators.
No interpolation of cohort adjoints; companion births enter via integrals.
The quadrature trajectory consumer is explicitly diagnostic.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,struct
from interval_backend import I,AD,Jet
ROOT=Path(__file__).resolve().parents[1]
T=1250000000;H=1e-14;NH=1e-4;FHE=.083;C=29979245800.;EV=1.602176634e-12;KB=1.380649e-16
CHI=[13.598434599702,24.587389011,54.41776]
DRA=struct.unpack('<d',struct.pack('<Q',0x3f5f8b1ba9b90acb))[0]
DRB=[struct.unpack('<d',struct.pack('<Q',x))[0] for x in [0x411caf2e364afdee,0x412135e886f9cb6f]]
class MissingProof(ValueError):pass

def load_pins(overrides=None,clock=T):
 binding=json.loads((ROOT/'SOURCE_BINDING.json').read_text());data={}
 for name,row in binding['files'].items():
  raw=(overrides or {}).get(name,(ROOT/'inputs'/name).read_bytes())
  if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('SOURCE_BYTES:'+name)
  if name.endswith('.json'):data[name]=json.loads(raw)
 p=data['BIRTH_PLAN.json']
 if clock!=T or p['window_s']!=[0,T] or p['same_plan']!=binding['same_plan']:raise ValueError('SOURCE_CLOCK_OR_PLAN')
 S=F.from_float(5e-15);weights=[p['same_source_weight_boxes'][str(b)]['weight'] for b in p['same_births']]
 data['mass_mismatch']=S*T-sum((F.from_float(w) for w in weights),F(0))
 return data

def local_derivatives(global_u,h,total=T):
 return [v*(I(h)/total)**r for r,v in enumerate(global_u)]

def require_proof(evidence):
 # This consumer accepts no self-attested boolean or sampled substitute.
 # No whole-kernel proof producer is implemented yet; fail closed even if all
 # familiar field names are present. Conditional operators below are not one.
 if evidence.get('frozen_gas'):raise MissingProof('FROZEN_GAS_NOT_FULL_COUPLED')
 raise MissingProof('MISSING_VALIDATED_BIRTH_RESOLVENT_JETS_0_TO_4_AND_ONE_SIDED_TRACES_OVER_ETA_WEIGHT_FAMILY')

def exp(x):return x.exp() if hasattr(x,'exp') else __import__('numpy').exp(x)
def constant(v,like):return I(v) if isinstance(like,(I,AD,Jet)) else v

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
W0=json.loads((ROOT/'inputs/INITIAL.json').read_text())['seed']['gas'][3]
EB=json.loads((ROOT/'inputs/INITIAL.json').read_text())['seed']['energy_box'][0]

def nonphoto_rhs(u,z):
 f,temp=nonphoto(z);k=lambda v:constant(v,z[3]);nh=k(NH)*exp(-3*k(H)*T*u)
 return [T*nh*f[j]-(2*k(H)*T*z[3] if j==3 else 0) for j in range(4)],temp

def probe(t,b,optical_memory,eb=None):
 tv=t.c[0] if isinstance(t,Jet) else I(t);bv=b.c[0] if isinstance(b,Jet) else I(b)
 if tv.lo<bv.hi:raise ValueError('NONCAUSAL_PROBE')
 mv=optical_memory.c[0] if isinstance(optical_memory,Jet) else I(optical_memory)
 if mv.lo<0:raise ValueError('NEGATIVE_OPACITY_MEMORY')
 eb=I(*EB) if eb is None else eb
 return eb*exp(-I(H)*(t-b)),exp(-optical_memory)

def memory_response(survival,opacity_variation_integral):
 return -survival*opacity_variation_integral

def continuum_rhs(u,z,initial_survival,integrate_births,eta,weights):
 """Functional of the actual companion survivor field, not seven cohorts.
 integrate_births(f) must integrate f over previous continuous and discrete
 births against pinned mu_eta; return enclosure for proof, value for diagnostics.
 Parameter eta and weights are owned by the integrator, never normalized here.
 """
 f,temp=nonphoto_rhs(u,z);k=lambda v:constant(v,z[3]);nh=k(NH)*exp(-3*k(H)*T*u)
 def fields(b,survival,eb):
  e=eb*exp(-constant(H,eb)*T*(u-b));a=T*constant(C,eb)*nh*sigma(e);p=a*(1-z[0])*survival
  return p,(e-CHI[0])*p/W0
 e0=I(*EB)*exp(-I(H)*T*u) if isinstance(u,I) else sum(EB)/2*exp(-H*T*u)
 a0=T*k(C)*nh*sigma(e0);photo0=a0*(1-z[0])*initial_survival
 source_photo,source_heat=integrate_births(fields,eta,weights)
 f[0]=f[0]+photo0+source_photo;f[3]=f[3]+(e0-CHI[0])*photo0/W0+source_heat
 return f,temp

def tangent_functional(u,z,dz,probe_birth,probe_survival,initial_pair,integrate_response):
 """Exact linearized gas functional at fixed nominal companion fields.
 integrate_response integrates [p*(-a*dx)+kap*dp] and its heat counterpart;
 each dp=-survival*integral_b^t(delta kap ds), so every previous birth feeds back.
 """
 base,_=nonphoto_rhs(I(u),[AD.variable(v,j) for j,v in enumerate(z)])
 out=[sum((v*dd for v,dd in zip(row.g,dz)),I(0)) for row in base]
 nh=I(NH)*exp(-I(3)*H*T*u)
 def response(b,p,dp,eb):
  e=eb*exp(-I(H)*T*(I(u)-b));a=I(T)*C*nh*sigma(e)
  photo=-a*p*dz[0]+a*(1-z[0])*dp
  return photo,(e-CHI[0])*photo/W0
 c,h=response(I(0),*initial_pair,I(*EB));cs,hs=integrate_response(response)
 e=I(*EB)*exp(-I(H)*T*(I(u)-probe_birth));a=I(T)*C*nh*sigma(e);q=a*(1-z[0])*probe_survival
 out[0]=out[0]+c+cs+q;out[3]=out[3]+h+hs+(e-CHI[0])*q/W0
 return out

def linear_tangent_rhs(A,v,forcing):
 return [sum((a*x for a,x in zip(row,v)),I(0))+f for row,f in zip(A,forcing)]

def linear_adjoint_rhs(A,lam,goal):
 return [-sum((A[i][j]*lam[i] for i in range(len(A))),I(0))-goal[j] for j in range(len(A))]

def photon_adjoint_rhs(u,b,z,lamgas,lamphoton,eb):
 """Backward continuum photon adjoint, valid for I or birth Jet arguments.
 d_t lambda_b = kap_b*(lambda_b-lambda_x-q_b*lambda_w).
 The trace lambda_b at t=b is the arbitrary-birth kernel, provided the full
 backward flow and its mixed t/b jets are validated (not implemented here).
 """
 k=lambda v:constant(v,eb)
 e=eb*exp(-k(H)*T*(u-b));nh=k(NH)*exp(-3*k(H)*T*u)
 kap=T*k(C)*nh*(1-z[0])*sigma(e);q=(e-k(CHI[0]))/k(W0)
 return kap*(lamphoton-lamgas[0]-q*lamgas[3])

def adjoint_functional(u,z,lamgas,initial_photon_pair,integrate_companion_adjoint):
 """Full gas adjoint including the *distribution* of previous birth adjoints.
 integrator returns int a_b*p_b*(lambda_x+q_b*lambda_w-lambda_b) dmu_eta.
 Initial pair=(actual remaining initial photons, initial photon adjoint).
 Companion adjoints are fields; they cannot be interpolated from seven cohorts.
 """
 np,_=nonphoto_rhs(I(u),[AD.variable(v,j) for j,v in enumerate(z)])
 J=[row.g for row in np];nh=I(NH)*exp(-I(3)*H*T*u)
 goal=[I(T)*C*I(6.6524587e-25)*nh*a for a in [I(1),I(FHE),I(2)*FHE,I(0)]]
 gas=linear_adjoint_rhs(J,lamgas,goal)
 def contribution(b,p,lam_b,eb):
  e=eb*exp(-I(H)*T*(I(u)-b));a=I(T)*C*nh*sigma(e);q=(e-CHI[0])/W0
  return a*p*(lamgas[0]+q*lamgas[3]-lam_b)
 direct=contribution(I(0),*initial_photon_pair,I(*EB));memory=integrate_companion_adjoint(contribution)
 gas[0]=gas[0]+direct+memory
 return gas
