"""New coefficient checks; never integrates any C21O historical trajectory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad

from rr_energy_moment import K_B_CGS, rr_energy_factor, vf_alpha, rr_cooling_erg_cm3_s


def hg_h_cooling(t):
    lam=2*157807./t
    return 1.778e-29*t*lam**1.965/(1+(lam/.541)**.502)**2.697


def hg_heiii_printed_cooling(t):
    lam=2*631515./t
    return 8*1.778e-29*t*lam**1.965/(1+(lam/.541)**.502)**2.697


def hg_heii_cooling(t):
    return K_B_CGS*t*3e-14*(2*285335./t)**.654


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.source.resolve()))
    from atomic_network import AtomicNetwork21
    net=AtomicNetwork21(electronic_isotope_equality=True)
    rows={name:tuple(net.provider.rows[name]['RR']) for name in net.channel_names}
    t=np.geomspace(3.,1e9,10001)
    results=[]
    eps=1e-4
    for name,pars in rows.items():
        f=rr_energy_factor(pars,t)
        # Independent finite differences of the original, frozen provider.
        xp=np.log(net.provider.rr(name,t*np.exp(eps)))
        xm=np.log(net.provider.rr(name,t*np.exp(-eps)))
        fd=1.5+(xp-xm)/(2*eps)
        err=float(np.max(np.abs(f-fd)))
        results.append(dict(channel=name,parameters=list(pars),min_factor=float(f.min()),max_factor=float(f.max()),max_absolute_log_derivative_residual=err,positive=bool(np.all((f>0)&(f<1)))))
        assert err < 1e-8
        assert np.all((f>0)&(f<1))
    # Independent dimensionless Maxwell integral with sigma(E)=E^-1 exp(-E/E0).
    # alpha(T) proportional to T^-1/2 /(1+T/E0), so exact factor=1/(1+T/E0).
    quad_results=[]
    for x in (.01,1.,100.):
        den=quad(lambda u:np.exp(-(1+x)*u),0,np.inf,epsabs=1e-13)[0]
        num=quad(lambda u:u*np.exp(-(1+x)*u),0,np.inf,epsabs=1e-13)[0]
        fquad=num/den
        ferr=abs(fquad-1/(1+x))
        quad_results.append(dict(T_over_E0=x,factor_quadrature=fquad,factor_analytic=1/(1+x),absolute_residual=ferr))
        assert ferr<1e-11
    compare=[]
    for name,ref,label,ranges in [
        ('HI',hg_h_cooling,'Hui_Gnedin_1997_H_CaseA',[(3.,1e9),(100.,1e6),(1e3,1e5)]),
        ('HeI',hg_heii_cooling,'Hui_Gnedin_1997_HeII_simple_CaseA',[(5e3,5e5)]),
        ('HeII',hg_heiii_printed_cooling,'Hui_Gnedin_1997_HeIII_printed_8prefactor',[(5e3,5e5)])]:
        for tmin,tmax in ranges:
            tt=np.geomspace(tmin,tmax,5001)
            ratio=rr_cooling_erg_cm3_s(rows[name],tt)/ref(tt)
            compare.append(dict(channel=name,reference=label,Tmin_K=tmin,Tmax_K=tmax,grid_count=len(tt),ratio_min=float(ratio.min()),ratio_max=float(ratio.max()),max_abs_relative_difference=float(np.max(abs(ratio-1))),claim='comparison_only_not_error_bound'))
    record={
        'schema':'BASS_RR_ENERGY_MOMENT_CHECK_v1',
        'status':'PASS_SCOPED_ALGEBRA_POSITIVITY_AND_NEW_COEFFICIENT_CHECKS',
        'old_C21O_ODE_runs':0,
        'source':str(a.source.resolve()),
        'source_provider_sha256':hashlib.sha256((a.source/'vendor/atomic/r9_li_thermal_rates.py').read_bytes()).hexdigest(),
        'temperature_domain_K':[3.,1e9],
        'grid_count':len(t),
        'rows':results,'independent_maxwell_quadrature':quad_results,
        'literature_comparisons':compare,
        'scientific_accuracy_status':'DERIVED_RATE_FIT_MOMENT; derivative_accuracy_not_certified',
        'HeIII_reference_status':'UNRESOLVED_NORMALIZATION_DIFFERENCE; no reference-pass asserted',
        'global_error_bound':None,
    }
    (a.out/'CHECKS.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
