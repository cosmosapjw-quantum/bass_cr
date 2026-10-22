#!/usr/bin/env python3
"""One bounded coefficient/ledger validation; optional frozen-history diagnostic.

No model import, RHS, ODE integration, interpolation or extrapolation.
"""
import argparse
import hashlib
import io
import json
import platform
import time
from pathlib import Path
import sys
import numpy as np
from decimal import Decimal, getcontext
sys.path.insert(0,str(Path(__file__).resolve().parent/'code'))
import hydrogen_excitation as h


def reference(t,coefficients):
    # Separate direct polynomial summation at80digits; coefficients exactly
    # interpreted as the decimal numbers transcribed from Table3.
    tm=Decimal(str(float(t))); y=tm.ln()
    p=sum(Decimal(str(a))*y**j for j,a in enumerate(coefficients))
    dp=sum(j*Decimal(str(a))*y**(j-1) for j,a in enumerate(coefficients) if j)
    k=Decimal('1.380649e-23')/Decimal('1.602176634e-19')
    delta=Decimal('0.75')*Decimal('13.605693122994')
    return (p-delta/(k*tm)).exp(),dp+delta/(k*tm)


def run(out,history=None,expected_sha=None):
    start=time.monotonic();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    getcontext().prec=80
    grids=[np.geomspace(2000,np.nextafter(6e4,0),21),
           np.geomspace(6e4,np.nextafter(6e6,0),21),np.geomspace(6e6,1e8,21)]
    worst_q=0.;worst_slope=0.;rows=[]
    for upper in ('2s','2p'):
        for region,ts in enumerate(grids):
            q,slope,valid,regions=h.excitation(ts,upper)
            assert valid.all() and np.all(regions==region) and np.all(q>0)
            for t,qi,si in zip(ts,q,slope):
                qr,sr=reference(t,h.COEFFICIENTS[upper][region])
                worst_q=max(worst_q,float(abs(Decimal(float(qi))/qr-1)))
                worst_slope=max(worst_slope,float(abs(Decimal(float(si))-sr)))
                rows.append([upper,region,float(t),float(qi),float(si)])
    assert worst_q<2e-10,("FP64_vs80digit_rate",worst_q)
    assert worst_slope<2e-10,("FP64_vs80digit_slope",worst_slope)
    invalid=np.array([-1.,0.,1999.,np.nextafter(2000.,0),np.nextafter(1e8,np.inf),np.inf,np.nan])
    q,slope,valid,region=h.excitation(invalid,'2s')
    assert not valid.any() and np.isnan(q).all() and np.isnan(slope).all() and np.all(region==-1)
    for b in h.BREAKS_K:
        assert h.excitation(b,'2s')[3]==list(h.BREAKS_K).index(b)+1
    gas,escaped,valid,_=h.optically_thin_paired_flux_eV_cm3_s(np.concatenate(grids),1e-4,2e-4)
    assert np.array_equal(gas+escaped,np.zeros_like(gas)) and np.all(escaped>0)
    negative_rejected=False
    try:h.optically_thin_paired_flux_eV_cm3_s(1e4,-1,1)
    except ValueError:negative_rejected=True
    assert negative_rejected
    jumps=[]
    for upper in ('2s','2p'):
        for j,b in enumerate(h.BREAKS_K):
            lo,_=reference(b,h.COEFFICIENTS[upper][j])
            hi,_=reference(b,h.COEFFICIENTS[upper][j+1])
            jumps.append({'upper':upper,'boundary_K':b,'relative_upper_minus_lower':float(hi/lo-1),
                          'interpretation':'rounded_original_piecewise_fits;not_smoothed;one_sided_derivative'})
    result={'schema':'CR22_EXCITATION_CHECK_V1','status':'PASS_SCOPED_NUMERIC_AND_LEDGER',
            'checks':{'coefficient_cases':len(rows),'precision_reference_digits':80,
                      'max_rate_relative_roundoff':worst_q,'max_log_slope_absolute_roundoff':worst_slope,
                      'numeric_comparison_threshold':2e-10,'domain_mask_cases':len(invalid),
                      'energy_pair_max_absolute':float(np.max(abs(gas+escaped))),
                      'negative_density_rejected':negative_rejected},
            'piecewise_jumps':jumps,'ODE_runs':0,'RHS_calls':0,
            'active_C22B_changes':0,'physical_fit_accuracy_independently_validated':False,
            'global_error_bound':None,'python':platform.python_version(),'numpy':np.__version__}
    if history:
        raw=Path(history).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest!=expected_sha:raise ValueError('HISTORY_SHA256_MISMATCH')
        with np.load(io.BytesIO(raw),allow_pickle=False) as data:
            t=data['temperature_K'];tt=data['proper_elapsed_s'];ne=data['n_e_cm3']
            labels=[str(x) for x in data['atomic_state_labels']]
            neutral=data['atomic_abundance_per_Href'][labels.index('H1_0')]
            if not np.all(np.diff(tt)>0):raise ValueError('NONMONOTONE_HISTORY')
            if not np.all(np.isfinite(ne)) or np.any(ne<0) or not np.all(np.isfinite(neutral)) or np.any(neutral<0):raise ValueError('INVALID_H1_DENSITY')
            coefficient,valid,region=h.cooling_coefficient_eV_cm3_s(t)
            loss=coefficient*ne*neutral
            adjacent=valid[:-1]&valid[1:]
            partial=float(np.sum((loss[:-1][adjacent]+loss[1:][adjacent])*.5*np.diff(tt)[adjacent])) if adjacent.any() else None
            result['frozen_history_diagnostic']={
                'history_name':Path(history).name,'sha256':digest,'samples':len(t),
                'T_min_K':float(t.min()),'T_max_K':float(t.max()),'valid_samples':int(valid.sum()),
                'valid_adjacent_intervals':int(adjacent.sum()),
                'covered_duration_fraction':float(np.diff(tt)[adjacent].sum()/(tt[-1]-tt[0])),
                'available_interval_trapezoid_loss_eV_per_Href':partial,
                'maximum_available_loss_eV_per_Href_s':float(np.max(loss[valid])) if valid.any() else None,
                'status':'PARTIAL_TEMPERATURE_COVERAGE;H1_ONLY;NOT_ACTIVE_TRAJECTORY;NOT_ERROR_BOUND',
                'quadrature':'available_adjacent_saved_endpoints_only;no_gap_bridging;no_continuous_domain_certificate',
                'isotope_extension':'NOT_ASSUMED'}
            np.savez(out/'HISTORY_DIAGNOSTIC.npz',temperature_K=t,valid=valid,region=region,
                     loss_eV_per_Href_s=loss,proper_elapsed_s=tt)
    result['elapsed_seconds']=time.monotonic()-start
    assert result['elapsed_seconds']<30,'budget exceeded'
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (out/'COEFFICIENT_SAMPLES.csv').open('x') as f:
        f.write('upper,region,T_K,q_cm3_s,dlogq_dlogT\n')
        for row in rows:f.write(','.join(map(str,row))+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--history');p.add_argument('--expected-history-sha256')
    a=p.parse_args()
    if bool(a.history)!=bool(a.expected_history_sha256):p.error('history and expected hash must be paired')
    run(a.out,a.history,a.expected_history_sha256)
