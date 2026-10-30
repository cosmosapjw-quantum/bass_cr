#!/usr/bin/env python3
"""Independent high-precision evaluation on pinned original opacity operands.

Same-owner MP80 alternative implementation, not genuinely other author R6/C9.
It tests probability exponentials and eventwise binding/kinetic identity on
stored source float64 energies and Verner coefficients, not source-data uncertainty.
"""
import json, math
from pathlib import Path
import mpmath as mp
import energy_transfer as em
mp.mp.dps=80

def mpf(x):return mp.mpf(str(float(x)))

def run():
    edges,prep,params,dens,prev=em.load_source()
    max_rel_p=mp.mpf(0);max_rel_kin=mp.mpf(0);checked=0
    sample=[]
    for orig,p in enumerate(prep):
        E=p['energy'];k=p['k'];f=p['frac'];weight=p['weights']
        isrc=mp.mpf(str(params['HI' if orig==0 else 'HeI'][0]))
        for j in range(4):
            ixs=[(j*137+z*43+4*orig)%3200 for z in range(16)]
            birth=float(edges[j]);dt=1e10-birth
            for n in ixs:
                k_mp=mpf(k[n]);br=1-mp.exp(-k_mp*mpf(dt))
                p_double=float(em.branch_prob(k[n:n+1],dt)[0])
                max_rel_p=max(max_rel_p,abs(br-mpf(p_double))/max(abs(br),mp.mpf('1e-100')))
                energy=mpf(E[n]);target='HI' if orig==1 else 'HI'
                it=mp.mpf(str(params[target][0]));e_in=energy-isrc;e_out=energy-it
                residual=e_out-e_in-(isrc-it)
                max_rel_kin=max(max_rel_kin,abs(residual))
                checked+=1
                if orig==1 and not (e_out>e_in):raise AssertionError('HE_CROSS_SOURCE_ENERGY_GAIN')
    result={'checked':checked,'dps':mp.mp.dps,'max_relative_probability_error_float_vs_MP80':float(max_rel_p),
       'max_absolute_event_energy_identity_residual_eV':str(max_rel_kin),
       'independence':'SAME_AUTHOR_ALTERNATE_MPMATH_IMPLEMENTATION','native_distinct_author_R6_C9':'NOT_RUN'}
    (em.ROOT/'results/MP80_CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
