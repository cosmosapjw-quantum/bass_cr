
"""Independent high-precision point equations and exact-rational Krawczyk replay.
Finite reference roots are checks, not the proof of uniform parameter coverage."""
from pathlib import Path
from fractions import Fraction as Q
import json, math, struct
import mpmath as m
m.mp.dps=70
ROOT=Path(__file__).resolve().parents[1]
def real(x):
    if isinstance(x,int):return m.mpf(x)
    n,d=float(x).as_integer_ratio();return m.mpf(n)/d
def bits(n):return real(struct.unpack('<d',struct.pack('<Q',n))[0])
f=json.loads((ROOT/'inputs/NEW_STAGES.json').read_text())[0]
H=real(1e-14); nh=real(f['nh']); fhe=real(.083)
nhe=real(float(f['nh'])*.083); feff=nhe/nh
kb=real(1.380649e-16);ev=real(1.602176634e-12);c=real(29979245800.)
chi=list(map(real,[13.598434599702,24.587389011,54.41776]))
dt=real(f['dt'])
def sigma(E,a=0):
    rows=[(13.6,.4298,5.475e4,32.88,2.963,0.,0.,0.),
          (24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
          (54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)]
    r=rows[a]
    cut,e0,s0,ya,p,yw,y0,y1=map(real,r)
    if E<cut:return m.mpf(0)
    x=E/e0-y0;y=m.sqrt(x*x+y1*y1)
    # p/2-5.5 and yw^2,y1^2 use the declared source's pre-evaluated f64 constants.
    power=real(r[4]/2-5.5)
    return s0*((x-1)**2+real(r[5]*r[5]))*y**power*(1+m.sqrt(y/ya))**(-p)*real(1e-18)
def rhs(y,E,p0):
    x,a,b,w=y; xe=x+feff*(a+2*b)
    T=2*w*ev/(3*kb*(1+feff+xe))
    low=[1-x,feff*(1-a-b),feff*a]; high=[x,feff*a,feff*b]
    L=list(map(real,[315614.,570670.,1263030.]))
    AA=list(map(real,[21.11,32.38,19.95]));pp=list(map(real,[-1.089,-1.146,-1.089]))
    cc=list(map(real,[.354,.416,.553]));rr=list(map(real,[.874,.987,.735]));dd=list(map(real,[1.101,1.056,1.275]))
    rrates=[];ci=[];eps=[]
    for i in range(3):
        l=L[i]/T
        if i==1:alpha=real(3e-14)*l**real(.654);g=real(-.654)
        else:
            u=(l/real(.522))**real(.470)
            alpha=(2 if i==2 else 1)*real(1.269e-13)*l**real(1.503)/(1+u)**real(1.923)
            g=real(-1.503)+real(1.923)*real(.470)*u/(1+u)
        beta=AA[i]*T**real(-1.5)*m.exp(-l/2)*l**pp[i]/(1+(l/cc[i])**rr[i])**dd[i]
        rrates.append(nh*xe*high[i]*alpha);ci.append(nh*xe*low[i]*beta)
        eps.append(kb*T*(real(1.5)+g)/ev)
    da=bits(0x3f5f8b1ba9b90acb);bb=[bits(0x411caf2e364afdee),bits(0x412135e886f9cb6f)]
    dr=[nh*xe*feff*a*fac*da*T**real(-1.5)*m.exp(-bval/T) for fac,bval in zip([m.mpf(1),real(.3)],bb)]
    lowp=[1-x,fhe*(1-a-b),fhe*a]
    ph=[m.mpf(0)]*3; photons=[]; events=[]; heats=m.mpf(0); absorbed=m.mpf(0)
    for en,pin in zip(E,p0):
        sig=[sigma(en,s) for s in range(3)]
        kap=c*nh*sum(lowp[s]*sig[s] for s in range(3))
        pj=pin/(1+dt*kap); photons.append(pj)
        jj=[dt*c*nh*lowp[s]*sig[s]*pj for s in range(3)]
        events.append(jj)
        for ss in range(3):
            ph[ss]+=jj[ss]/dt
            heats+=(en-chi[ss])*jj[ss]
            absorbed+=en*jj[ss]
    # Non-photo number derivatives normalize with the actual nHe/nH. Photo with declared stage fHe.
    non=[ci[s]-rrates[s] for s in range(3)];non[1]-=sum(dr)
    nonw=-sum(ci[s]*chi[s]+rrates[s]*eps[s] for s in range(3))-sum(dr[i]*kb*bb[i]/ev for i in range(2))
    heat=heats/dt
    out=[non[0]+ph[0],(non[1]-non[2])/feff+(ph[1]-ph[2])/fhe,non[2]/feff+ph[2]/fhe,nonw+heat-2*H*w]
    return out,dict(p=photons,J=events,heat=heats,A=absorbed,T=T)
def res(y,old,E,p0):
    r,_=rhs(y,E,p0)
    return m.matrix([y[i]-old[i]-dt*r[i] for i in range(4)])
def inside(v,b):
    return real(b[0])<=v<=real(b[1])


def configure(nh_float, dt_float):
    global nh, nhe, feff, dt
    nh=real(nh_float); nhe=real(float(nh_float)*.083); feff=nhe/nh; dt=real(dt_float)
