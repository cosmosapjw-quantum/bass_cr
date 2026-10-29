#!/usr/bin/env python3
"""Independent mpmath exact-input representation check of selected PR125 photon atoms.

Independently reimplements Verner form and pointwise spectral survivor/absorber
probabilities. Same original source and Table parameters but a different arithmetic
backend; NOT a different-author R6/C9 review.
"""
from __future__ import annotations
import json
from pathlib import Path
import mpmath as mp
import numpy as np
import spectral_survival as m
mp.mp.dps=80
R=mp.mpf


def sigma(E,p):
    eth,emax,e0,sigma0,ya,P,yw,y0,y1=[R(str(x)) for x in p]
    E=R(str(E))
    if E<eth or E>emax:return R(0)
    x=E/e0-y0;y=mp.sqrt(x*x+y1*y1)
    return (sigma0*R('1e-22'))*((x-1)**2+yw*yw)*y**(P/2-R('5.5'))*(1+mp.sqrt(y/ya))**(-P)


def np_dbl_err(observed,reference):
    return float(abs(R(str(float(observed)))-reference)/max(R('1e-99'),abs(reference)))


def check():
    arrays,den,params,sig,_,_=m.source_load()
    max_rel_sig=0.;max_rel_survival=0.;max_rel_absorber=0.;n=0
    # Both photon families, every time source bin and several original atoms.
    for ch in m.SOURCES:
        E=arrays[f'photon_{ch}_eV']
        for ii in [0,1,31,131,777,1234,2087,3199]:
            e=float(E[ii]);sgH=sigma(e,params['HI']);sgHe=sigma(e,params['HeI'])
            max_rel_sig=max(max_rel_sig,np_dbl_err(sig[ch]['HI'][ii],sgH),np_dbl_err(sig[ch]['HeI'][ii],sgHe))
            aH=sgH*R(str(den['HI']));aHe=sgHe*R(str(den['HeI']));a=aH+aHe
            for j in range(4):
                l,r=[float(x) for x in arrays['time_edges_s'][j:j+2]]
                T=float(m.TIMES[(j*2+1)]) # a genuine interior time of each original birth bin
                w=1. # conditional probability, independent of tiny source number
                cvals=m.atom_components(np.array([w]),np.array([sig[ch]['HI'][ii]*den['HI']]),np.array([sig[ch]['HeI'][ii]*den['HeI']]),l,r,T)
                # t is within birth bin: survivor upper=1, lower=0, absorption lower=0.
                dt=R(str(T-l));pH=(aH/a)*(-mp.expm1(-a*R(str(m.C))*dt))
                pHe=(aHe/a)*(-mp.expm1(-a*R(str(m.C))*dt))
                max_rel_absorber=max(max_rel_absorber,np_dbl_err(cvals[5][0],pH),np_dbl_err(cvals[7][0],pHe))
                assert cvals[2][0]==0 and cvals[3][0]==1
                # After all source bins: upper survivor for latest birth in current bin.
                T2=float(m.TIMES[-1]);parts=m.atom_components(np.array([w]),np.array([sig[ch]['HI'][ii]*den['HI']]),np.array([sig[ch]['HeI'][ii]*den['HeI']]),l,r,T2)
                s_early=mp.exp(-a*R(str(m.C))*R(str(T2-l)))
                s_late=mp.exp(-a*R(str(m.C))*R(str(T2-r)))
                max_rel_survival=max(max_rel_survival,np_dbl_err(parts[2][0],s_early),np_dbl_err(parts[3][0],s_late))
                n+=1
    out={'schema':'CR_PHYS04_MP80_INDEPENDENT_SOURCE_CONTROLS_V1','mp_dps':80,
         'atom_times_tested':n,'reference':'independent mpmath Verner coefficients and expm1, same locked inputs',
         'max_rel_sigma':max_rel_sig,'max_rel_survival':max_rel_survival,
         'max_rel_absorber':max_rel_absorber,'distinct_author_review':False,
         'passes':max(max_rel_sig,max_rel_survival,max_rel_absorber)<5e-13}
    if not out['passes']:raise AssertionError(out)
    (m.ROOT/'results'/'MP80.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2))
    return out
if __name__=='__main__':check()
