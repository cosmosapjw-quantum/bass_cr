#!/usr/bin/env python3
"""Same-author independent-implementation adversarial audit, not distinct-author R6/C9."""
import csv,hashlib,io,json,math,sys,tempfile,zipfile,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
INNER='research/cr_phys10_energy_causal_20261030/sources/PR134_ORIGINAL_SOURCE.zip'
INNER2='research/cr_phys09_chemistry_neutral_response_20261030/'
EXPECTED='faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033'
PARENT=ROOT/'sources/PR135_ORIGINAL_SOURCE.zip'
EV=1.602176634e-19

def get_direct_source():
    b=PARENT.read_bytes()
    assert hashlib.sha256(b).hexdigest()==EXPECTED
    with zipfile.ZipFile(io.BytesIO(b)) as z:p9=z.read(INNER)
    with zipfile.ZipFile(io.BytesIO(p9)) as z:
        code=z.read(INNER2+'neutral_response.py')
        p8=z.read(INNER2+'sources/PR133_ORIGINAL_SOURCE.zip')
    with tempfile.TemporaryDirectory(prefix='blind_') as d:
        d=Path(d); c=d/'neutral_response.py';p=d/'PR133_ORIGINAL_SOURCE.zip'
        c.write_bytes(code);p.write_bytes(p8)
        sp=importlib.util.spec_from_file_location('phys11_audit_direct_owner',c)
        mod=importlib.util.module_from_spec(sp)
        sys.modules[sp.name]=mod;sp.loader.exec_module(mod)
        edges,prep,params,dens,_=mod.original_source(p)
    return edges,prep,params

def direct_first(ka,ke,s,T,b,u,v,lamb):
    if s>=T:return np.zeros_like(ka)
    cuts=sorted(set([float(s),float(T)]+[float(x) for x in (u,v) if s<x<T]))
    survival=np.ones_like(ka,dtype=float); prob=np.zeros_like(ka,dtype=float)
    for l,r in zip(cuts[:-1],cuts[1:]):
        x=math.exp(lamb) if u<=(l+r)*0.5<v else 1.
        h=ka*(x if b==0 else 1)
        e=ke*(x if b==1 else 1)
        tot=h+e
        d=r-l
        p=np.where(tot>0,np.divide(h,tot,out=np.zeros_like(tot),where=tot>0)*(-np.expm1(-tot*d)),0.)
        prob+=survival*p
        survival*=np.exp(-tot*d)
    return prob

def check():
    edges,prep,params=get_direct_source()
    he=[p for p in prep if p['source']=='He'][0]
    ih=float(params['HI'][0]); ihe=float(params['HeI'][0]); E=he['energy'];mask=E>=2*ih
    assert ih==13.6 and ihe==24.59
    assert np.count_nonzero(mask)==2389
    assert max(np.max(p['energy']) for p in prep)-ih<ihe
    base={}
    h=1e-4;T=1e10;u=2.5e9;v=3.75e9
    for policy in ('earliest','latest'):
        val=[]
        for j in range(4):
            s=({'earliest':edges[j],'latest':edges[j+1]})[policy]
            kH=he['k']*he['frac'][0];kHe=he['k']*he['frac'][1]
            if s>=T:continue
            first=(kH/(kH+kHe))*(-np.expm1(-(kH+kHe)*(T-s)))
            val.append(math.fsum(he['weights'][j]*mask*first))
        base[policy]=math.fsum(val)
    tab={q['birth_policy']:float(q['H_secondary_upper_events_m3']) for q in csv.DictReader((ROOT/'results/TIME_TOTAL_CAPACITY.csv').open()) if float(q['observation_s'])==T}
    err=max(abs(base[k]-tab[k]) for k in base)
    relerr=err/max(base.values())
    if relerr>2e-13:raise AssertionError(('independent_first_count',relerr,err))
    fromtab={}
    for q in csv.DictReader((ROOT/'results/CAUSAL_H_SECONDARY_CAPACITY.csv').open()):
        if float(q['observation_s'])==T and q['birth_policy']=='earliest' and q['source']=='He' and q['first_absorber']=='HI' and int(q['window_index'])==2:
            fromtab[q['neutral_parameter']]=float(q['d_H_capacity_dln_neutral_m3'])
    results={}; max_rel=0.
    for b,name in ((0,'HI'),(1,'HeI')):
        run=[]
        for j in range(4):
            s=edges[j]
            kp=he['k']*he['frac'][0];ke=he['k']*he['frac'][1]
            plus=direct_first(kp,ke,s,T,b,u,v,+h)
            minus=direct_first(kp,ke,s,T,b,u,v,-h)
            run.append(math.fsum(he['weights'][j]*mask*(plus-minus))/(2*h))
        fd=math.fsum(run)
        analytic=fromtab[name]
        rel=abs(analytic-fd)/max(abs(analytic),1e-50)
        max_rel=max(rel,max_rel)
        results[name]={'finite_difference_m3':fd,'analytic_m3':analytic,'relative_error':rel}
    assert max_rel<2.0e-8,(max_rel,results)
    outcome={'method':'direct-source alternate first-event probability with independent interval integration and finite density log difference','reviewer':'same model, same author, blind-style script separated from PHYS11 construction','source_original_SHA256':EXPECTED,'eligible_energy_atoms':2389,'source_capacity':base,'source_energy_thresholds':{'HI':ih,'HeI':ihe,'HeII_NIST':54.4177655282},'max_total_relative_error_vs_primary':relerr,'independent_causal_FD':results,'max_fd_rel':max_rel,'pass':True,'independent_distinct_author':False}
    (ROOT/'BLIND_STYLE_AUDIT.json').write_text(json.dumps(outcome,sort_keys=True,indent=2)+'\n')
    print(json.dumps(outcome,indent=2))

if __name__=='__main__':check()
