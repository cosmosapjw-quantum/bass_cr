"""BRIDGE12: instantaneous FT03 H/He + one finite birth cohort.
Exact binary64 source literals are interpreted as real constants. Continuous
nHe = fhe*nH, nH(t), and E(t) are real functions, not rounded stage lookups.
The native frozen-stage BE photon elimination is deliberately NOT the RHS.
"""
from pathlib import Path
import json, sys, struct
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import interval_decimal as ia
ia.DIM=5
from interval_decimal import IV,AD,D
from packet_flow import loss
CELL=json.loads((ROOT/'inputs/NEXT_CELL_INPUT.json').read_text())
H=IV(1e-14); NH0=IV(1e-4); FHE=IV(.083); C=IV(29979245800.)
KB=IV(1.380649e-16); EV=IV(1.602176634e-12)
DURATION=IV(CELL['time_s'][1]); W0=IV(CELL['seed']['gas'][3]); P0=IV(CELL['seed']['p'][0])
EB=IV(*CELL['seed']['energy_box'][0]); EBNOM=IV(CELL['seed']['energy'][0]); CUT=IV(13.6)
CHI=[IV(x) for x in [13.598434599702,24.587389011,54.41776]]
SCALE=[IV(1)]*3+[W0,P0]
# Normalize by symbolic identity for w0/w0 and P0/P0, not independent intervals.
Z0=[IV(v) for v in CELL['seed']['gas'][:3]]+[IV(1),IV(1)]
Z1=[IV(v)/a for v,a in zip(CELL['source_point']['gas']+CELL['source_point']['p1'],SCALE)]
RAW_INITIAL=CELL['seed']['gas_box']+CELL['seed']['p_box']
assert all(v[0]==v[1]==x for v,x in zip(RAW_INITIAL,CELL['seed']['gas']+CELL['seed']['p']))
INITIAL_FAMILY=[IV(v) for v in Z0]
DISCRETE_BOX=[IV(*v)/a for v,a in zip(CELL['source_root']['carry_gas']+CELL['source_root']['carry_photons'],SCALE)]
LAM=[IV(v) for v in [315614.,570670.,1263030.]]
def frombits(n): return IV(struct.unpack('<d',struct.pack('<Q',n))[0])
DRA=frombits(0x3f5f8b1ba9b90acb)
DRB=[frombits(0x411caf2e364afdee),frombits(0x412135e886f9cb6f)]

def sigma(e):
    v=e.v if isinstance(e,AD) else IV(e)
    if v.lo<CUT.hi or v.hi>=IV(24.59).lo:
        raise ValueError('SMOOTH_SOFT_HI_SUPPORT_REQUIRED')
    x=e/IV(.4298)
    # The exponent is the source's pre-evaluated f64 expression.
    power=IV(2.963/2-5.5)
    return IV(5.475e4)*(x-1)**2*x**power.lo*(1+(x/IV(32.88))**.5)**(-2.963)*IV(1e-18)

def coeff(T):
    rr=[]; slopes=[]; ci=[]
    ca=[21.11,32.38,19.95];cp=[-1.089,-1.146,-1.089]
    cc=[.354,.416,.553];cr=[.874,.987,.735];cd=[1.101,1.056,1.275]
    for a in range(3):
        l=LAM[a]/T
        if a==1:
            rr.append(IV(3e-14)*l**.654); slopes.append(IV(-.654))
        else:
            u=(l/IV(.522))**.470
            rr.append((2 if a==2 else 1)*IV(1.269e-13)*l**1.503/(1+u)**1.923)
            slopes.append(IV(-1.503)+IV(1.923)*IV(.470)*u/(1+u))
        ci.append(IV(ca[a])*T**-1.5*(-l/2).exp()*l**cp[a]/(1+(l/IV(cc[a]))**cr[a])**cd[a])
    dr=[fac*DRA*T**-1.5*(-b/T).exp() for fac,b in zip([IV(1),IV(.3)],DRB)]
    return rr,slopes,ci,dr

def temperature(z):
    x,y,b=z[:3];w=z[3]*W0
    nu=1+FHE+x+FHE*(y+2*b)
    return 2*w*EV/(3*KB*nu)

def geometry(s,eb=EB):
    return NH0*(-3*H*DURATION*s).exp(),eb*(-H*DURATION*s).exp()

def rhs(s,z,eb=EB):
    if len(z)!=5:raise ValueError('FIVE_STATE_COMPONENTS_REQUIRED')
    x,y,b=z[:3];w=z[3]*W0;phot=z[4]*P0
    T=temperature(z); tv=T.v if isinstance(T,AD) else T
    if tv.lo<D(30000) or tv.hi>D(110000): raise ValueError('FT03_TEMPERATURE_DOMAIN')
    nh,en=geometry(s,eb); ne=x+FHE*(y+2*b)
    rr0,g,ci0,dr0=coeff(T)
    lower=[1-x,FHE*(1-y-b),FHE*y]; upper=[x,FHE*y,FHE*b]
    ci=[nh*ne*lower[j]*ci0[j] for j in range(3)]
    rr=[nh*ne*upper[j]*rr0[j] for j in range(3)]
    dr=[nh*ne*FHE*y*d for d in dr0]
    kap=C*nh*(1-x)*sigma(en)
    photon_rhs=loss(kap,phot)
    photo=-photon_rhs
    net=[photo+ci[0]-rr[0],ci[1]-rr[1]-sum(dr),ci[2]-rr[2]]
    heat=(en-CHI[0])*photo
    kin=sum(r*KB*T*(IV(1.5)+slope)/EV for r,slope in zip(rr,g))
    kindr=sum(j*KB*b/EV for j,b in zip(dr,DRB))
    fw=heat-sum(j*c for j,c in zip(ci,CHI))-kin-kindr-2*H*w
    physical=[net[0],(net[1]-net[2])/FHE,net[2]/FHE,fw,photon_rhs]
    escape=sum(j*c for j,c in zip(rr,CHI))+kin+CHI[1]*sum(dr)+kindr
    aux={'T':T,'nh':nh,'E':en,'photo':photo,'ci':ci,'rr':rr,'dr':dr,'heat':heat,'escape':escape,'photon_energy_rate':-H*en*phot+en*photon_rhs,'gas_work_rate':2*H*w,'radiation_work_rate':H*en*phot}
    return [v*DURATION/a for v,a in zip(physical,SCALE)],aux

def reconstruction(s): return [a+s*(b-a) for a,b in zip(Z0,Z1)]

def serialize(v):
    if isinstance(v,IV):return v.data()
    if isinstance(v,AD):return {'value':v.v.data(),'gradient':[serialize(x) for x in v.g]}
    if isinstance(v,D):return str(v)
    if isinstance(v,(list,tuple)):return [serialize(x) for x in v]
    if isinstance(v,dict):return {k:serialize(x) for k,x in v.items()}
    return v
