#!/usr/bin/env python3
"""One finite same-author adversarial physics pass; independent scalar quadrature.
No different-author R06/C09 may be claimed from this audit.
"""
from __future__ import annotations
import json,math,csv
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import phys12_h_eii as parent
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'sources/PR136_ORIGINAL_SOURCE.zip'

def f_alt(E):
    # Independent scalar formula, no call to parent.kim_sigma_m2.
    if E<=13.61:return 0.
    x=E/13.61
    return 1.0e-20*(0.7576*math.log(x)+(-5.521*math.log(x)+5.867*(x-1))/(x+2.948))/x

def two_scalar(h,he,n,dt):
    if dt<=0:return 0.
    # Independent QUADPACK with original probability integrand.
    return quad(lambda tau:h*math.exp(-(h+he)*tau)*(-math.expm1(-n*(dt-tau))),0.,dt,epsabs=1e-20,epsrel=5e-13,limit=100)[0]

def audit():
    mod,edges,prep,params,dens=parent.load_owner(SRC)
    photon=next(pp for pp in prep if pp['source']=='He')
    em=np.asarray(photon['energy'])-float(params['HI'][0]);kh=np.asarray(photon['k']*photon['frac'][0]);he=np.asarray(photon['k']*photon['frac'][1]);
    cases=[i for i,e in enumerate(em) if e>13.61]
    selected=list(dict.fromkeys([cases[0],cases[1],cases[49],cases[100],cases[300],cases[600],cases[1200],cases[-1]]))
    worst=0.;worstcase=None;checked=0;maxfd=0.
    for idx in selected:
        E=float(em[idx]);rate=float(dens['HI'])*f_alt(E)*math.sqrt(2*parent.EV_J*E/parent.ME_KG)
        for dt in [1.25e9,3.75e9,7.5e9,10e9]:
            alternate=two_scalar(float(kh[idx]),float(he[idx]),rate,dt)
            tested=float(parent.bound_probability(np.array([kh[idx]]),np.array([kh[idx]+he[idx]]),np.array([rate]),dt)[0]);
            err=abs(alternate-tested)/max(abs(alternate),abs(tested),1e-100)
            checked+=1
            if err>worst:worst=err;worstcase=dict(idx=idx,eV=E,dt=dt,direct=alternate,gauss=tested)
    # Compare analytic d/dln n_H and d/dln n_He to fully independent density perturbations.
    for idx in selected:
        E=float(em[idx]);r=float(dens['HI'])*f_alt(E)*math.sqrt(2*parent.EV_J*E/parent.ME_KG)
        h=2e-4;dt=1e10
        for neutral in ['HI','HeI']:
            z=float(parent.bound_gradient_uniform(np.array([kh[idx]]),np.array([he[idx]]),np.array([r]),dt,neutral)[0])
            if neutral=='HI':
                pp=two_scalar(float(kh[idx])*math.exp(h),float(he[idx]),r*math.exp(h),dt)
                mm=two_scalar(float(kh[idx])*math.exp(-h),float(he[idx]),r*math.exp(-h),dt)
            else:
                pp=two_scalar(float(kh[idx]),float(he[idx])*math.exp(h),r,dt)
                mm=two_scalar(float(kh[idx]),float(he[idx])*math.exp(-h),r,dt)
            # finite-difference truncation O(h²), not target quadrature precision
            fd=(pp-mm)/(2*h)
            ef=abs(z-fd)/max(abs(z),abs(fd),1e-90)
            maxfd=max(maxfd,ef)
    # Extrapolation audit against Shah1987 first measured energy E_incident>=14.6eV.
    counts=dict(PHYS11_kinematic=sum(float(e)>=13.6 for e in em),Kim_fit_positive=sum(float(e)>13.61 for e in em),
        fit_only_below_Shah1987_min=sum(13.61<float(e)<14.6 for e in em),measured_domain_14_6_plus=sum(float(e)>=14.6 for e in em))
    total_rows=[]
    for row in csv.DictReader((ROOT/'results/TIME_TOTAL_TWO_EVENT.csv').open()):
        if float(row['observation_s'])==1e10:total_rows.append(row)
    issue=[
        {'severity':'BLOCK_NOW_FOR_GLOBAL_PHYSICAL_K','finding':'No electron loss/transport/trajectory and no full coupled clock/geometry; finite-horizon EII exposure is a stationary-gas fit-model upper bound only'},
        {'severity':'KEEP_MODEL_SCOPE','finding':'Original PHYS11 source H 13.60 eV; Kim1992 fit uses 13.61 eV; 3 original kinematically eligible photon energy atoms are zeroed by rounded fit, not physically impossible'},
        {'severity':'KEEP_SOURCE_PROVENANCE','finding':'Kim1992 Eq(2) Table1 is a fit to Shah 1987 total measured ionization, not the raw pointwise measurements; incident energy below Shah experimental 14.6 eV is empirical fit extrapolation'},
        {'severity':'KEEP_CONDITION','finding':'Monotonic sigma*v needs initial-electron non-increasing kinetic energy and nonrel local rates. Original 100 K background is treated as stationary target, no collision thermal tail or field acceleration'},
        {'severity':'NO_PROMOTION','finding':'R06/C09 actual different-author review not run; upstream central DAG 28/88 remains, source-global He kernel/K unbound'}]
    d=dict(method='independent_scalar_quadpack_and_finite_differences_same_author',parent_source_sha=parent.PHYS11_SHA256,cases=checked,max_relative_quad_difference=worst,worst_case=worstcase,max_relative_log_response_fd_difference=maxfd,counts=counts,final_rows=total_rows,findings=issue,distinct_author_R06='NOT_RUN',distinct_author_C09='NOT_RUN')
    (ROOT/'BLIND_REFEREE_EVIDENCE.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    assert worst<2e-10,(worst,worstcase)
    assert maxfd<2e-7,maxfd
    assert counts['PHYS11_kinematic']==2389
    assert counts['Kim_fit_positive']==2386
    print(json.dumps({k:d[k] for k in ['cases','max_relative_quad_difference','max_relative_log_response_fd_difference','counts']},indent=2))
if __name__=='__main__':audit()
