"""C23E V2 conditional D43K source binding. No import-time science/writes.
CX formula extracted from WU79_collisional.py d_cx_rates detailed_balance;
PI source and conditional RR moment reuse exact C23B/C22A modules.
"""
import math
from reuse.atomic_contract import POPULATION_LABELS, SPECIES, INDEX
from reuse.c23b.spectral_photo_source import PW19Spectrum,Verner96,EV_ERG
from reuse.c22a.rr_energy_moment import rr_energy_factor,vf_alpha
KB=1.380649e-23/1.602176634e-19
DELTA=43*KB
CHI_H=13.6
CHI_D=CHI_H+DELTA
POTENTIAL={'H1:0':0.,'H1:1':CHI_H,'D:0':0.,'D:1':CHI_D,'delta_eV':DELTA}

def temperature(T):
    if isinstance(T,bool) or not math.isfinite(T) or not 3<=T<=200000:raise ValueError('JOINT_T_DOMAIN')
    return T

def d_cx_rates(T):
    temperature(T)
    reverse=2.06e-10*T**.396*math.exp(-33./T)+2.03e-9*T**(-.332)
    return reverse*math.exp(-43./T),reverse

def band(spectrum,order):
    from numpy.polynomial.legendre import leggauss
    nodes,weights=leggauss(order);atom=Verner96.from_table('HI')
    edges=[CHI_H]+[E for E in spectrum.energy_eV if CHI_H<E<CHI_D]+[CHI_D]
    sums=[[],[],[]]
    for a,b in zip(edges,edges[1:]):
        for n,w in zip(nodes,weights):
            E=(a+b)/2+(b-a)*float(n)/2
            q=spectrum.evaluate(E)*atom.sigma_cm2(E)/(EV_ERG*E*E)
            v=(b-a)*float(w)*q/2
            for out,term in zip(sums,(v,E*v,(CHI_D-E)*v)):out.append(term)
    return tuple(math.fsum(a) for a in sums)

def transfer(parent,bandmom):
    G,K,A=parent;g,a,b=bandmom
    return G-g,math.fsum([K,-DELTA*G,b]),A-a

def source(T,dens,nthermal,nfast,moments,rrparams,potential):
    temperature(T)
    if set(dens)!=set(POPULATION_LABELS):raise ValueError('ALL_21_KEYS_REQUIRED')
    if any(isinstance(x,bool) or not math.isfinite(x) or x<0 for x in dens.values()):raise ValueError('BAD_DENSITY')
    if potential!=POTENTIAL:raise ValueError('POTENTIAL_MISMATCH')
    if any(not math.isfinite(x) or x<0 for x in (nthermal,nfast)):raise ValueError('BAD_POOL')
    charge=math.fsum(s.charge*dens[s.label] for s in SPECIES[:-1])
    if abs(charge-nthermal-nfast)>max(1e-30,2e-13*charge):raise ValueError('POOL_SUM_MISMATCH')
    alpha=float(vf_alpha(rrparams,T));Kcap=KB*T*float(rr_energy_factor(rrparams,T))
    f,r=d_cx_rates(T);events=[]
    for X,chi in [('H1',CHI_H),('D',CHI_D)]:
        G,K,A=moments[X];rate=dens[X+':0']*G
        events.append(dict(id=X+'_PI',rate=rate,net={X+':0':-rate,X+':1':rate},thermal_e=0.,fast_e=rate,bind=chi*rate,thermal=0.,fast=dens[X+':0']*K,escaped=0.,absorbed=dens[X+':0']*A))
        rate=alpha*dens[X+':1']*nthermal
        events.append(dict(id=X+'_RR',rate=rate,net={X+':0':rate,X+':1':-rate},thermal_e=-rate,fast_e=0.,bind=-chi*rate,thermal=-Kcap*rate,fast=0.,escaped=(chi+Kcap)*rate,absorbed=0.))
    J=f*dens['D:0']*dens['H1:1']-r*dens['D:1']*dens['H1:0']
    events.append(dict(id='HD_CX',rate=J,net={'D:0':-J,'D:1':J,'H1:0':J,'H1:1':-J},thermal_e=0.,fast_e=0.,bind=DELTA*J,thermal=-DELTA*J,fast=0.,escaped=0.,absorbed=0.))
    dn={k:math.fsum(e['net'].get(k,0.) for e in events) for k in POPULATION_LABELS}
    sums={k:math.fsum(e[k] for e in events) for k in ['thermal_e','fast_e','bind','thermal','fast','escaped','absorbed']}
    de=math.fsum(s.charge*dn[s.label] for s in SPECIES[:-1])
    terms=[sums[k] for k in ['bind','thermal','fast','escaped']]+[-sums['absorbed']]
    energy=math.fsum(terms);energy_scale=math.fsum(abs(e[k]) for e in events for k in ['bind','thermal','fast','escaped','absorbed'])
    contraction=math.fsum(potential[k]*dn[k] for k in ['H1:0','H1:1','D:0','D:1'])
    constituent=math.fsum(abs(potential[k]*e['net'].get(k,0.)) for e in events for k in ['H1:0','H1:1','D:0','D:1'])
    nuclides={n:math.fsum(dn[s.label] for s in SPECIES[:-1] if s.nuclide==n) for n in {s.nuclide for s in SPECIES[:-1]}}
    scale=math.fsum(abs(v) for e in events for v in e['net'].values())
    pool=math.fsum([de,-sums['thermal_e'],-sums['fast_e']])
    return dict(T=T,dn=dn,events=events,totals=sums,charge_e_source=de,nuclide_residuals=nuclides,nucleus_normalized=max(map(abs,nuclides.values()))/scale if scale else 0.,pool_residual=pool,pool_normalized=abs(pool)/scale if scale else 0.,energy_residual=energy,energy_normalized=abs(energy)/energy_scale if energy_scale else 0.,potential_residual=contraction-sums['bind'],potential_normalized=abs(contraction-sums['bind'])/constituent if constituent else 0.)
