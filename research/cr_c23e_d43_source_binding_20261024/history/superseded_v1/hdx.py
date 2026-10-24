"""C23E frozen Lambda=1 candidate; Savin2002 literal fits remain distinct.
Formula provenance: Savin ApJ566,599 Eq6/Table2; Grackle source pin in inputs.
"""
import math
from reuse.atomic_contract import POPULATION_LABELS, inventory, conservation_residuals, INDEX
KB=1.380649e-23/1.602176634e-19
DELTA=0.0037

def raw_savin(T):
    if isinstance(T,bool) or not math.isfinite(T) or not 2.7<=T<=200000: raise ValueError('T outside fit support')
    f=2e-10*T**.402*math.exp(-37.1/T)-3.31e-17*T**1.48
    r=2.06e-10*T**.396*math.exp(-33/T)+2.03e-9*T**(-.332)
    if f<=0 or r<=0: raise ValueError('nonpositive fit')
    return f,r

def balanced_candidate(T):
    f,r=raw_savin(T);m=(math.log(f)+math.log(r))/2;lr=-DELTA/(KB*T)
    return math.exp(m+lr/2),math.exp(m-lr/2)

def validate_inventory(values): return inventory(values)

def net_vector():
    n=[0]*22
    for k,v in [('D:0',-1),('D:1',1),('H1:0',1),('H1:1',-1)]: n[INDEX[k]]=v
    return n

def isothermal_extent(t,state,pair):
    if not math.isfinite(t) or t<0: raise ValueError('bad time')
    d0,dp,h0,hp=state;f,r=pair
    if min(state)<0 or min(pair)<=0: raise ValueError('bad populations/pair')
    A=f-r;B=f*(d0+hp)+r*(dp+h0);C=f*d0*hp-r*dp*h0
    if t==0 or C==0:return 0.
    s=math.sqrt(B*B-4*A*C)
    if s==0:return C*t/(1+B*t/2)
    u=-math.expm1(-s*t)
    return 2*C*u/(B*u+s*(2-u))

def case_parameters(T0,ratio,y0):
    NH=.1;ND=NH*ratio;hp=.05;h0=.05;dp=ND*y0;d0=ND-dp
    values={k:'0' for k in POPULATION_LABELS}
    for k,v in [('D:0',d0),('D:1',dp),('H1:0',h0),('H1:1',hp)]:values[k]=repr(v)
    validate_inventory(values)
    ne=hp+dp;Nth=NH+ND+ne;CV=1.5*KB*Nth
    f,r=balanced_candidate(T0);B0=f*(d0+hp)+r*(dp+h0)
    return dict(T0=T0,ratio=ratio,y0=y0,NH=NH,ND=ND,h0=h0,hp=hp,dp=dp,d0=d0,ne=ne,Nth=Nth,CV=CV,B0=B0,inventory=values)

def reconstruct(y,p):
    x=p['ND']*(y-p['y0']);T=p['T0']-DELTA*x/p['CV']
    state=(p['d0']-x,p['dp']+x,p['h0']+x,p['hp']-x)
    if min(state)<-2e-11*max(p['ND'],p['NH']) or not 2.7<=T<=200000:raise ValueError('physical coverage exit')
    return x,T,state

def rhs(tau,y,p):
    x,T,state=reconstruct(float(y[0]),p);f,r=balanced_candidate(T)
    return [(f*(1-y[0])*(p['hp']-x)-r*y[0]*(p['h0']+x))/p['B0']]

def entropy(T,state,pair):
    d0,dp,h0,hp=state;f,r=pair;rf=f*d0*hp;rr=r*dp*h0
    if min(rf,rr)<=0:return dict(status='BOUNDARY_LIMIT',rf=rf,rr=rr,production=None,normalized=None)
    affinity=-DELTA/(KB*T)+math.log(d0)+math.log(hp)-math.log(dp)-math.log(h0)
    prod=KB*(rf-rr)*affinity
    return dict(status='INTERIOR',rf=rf,rr=rr,affinity_over_kB=affinity,production=prod,normalized=prod/(KB*(rf+rr)))
