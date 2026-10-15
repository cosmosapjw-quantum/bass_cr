"""Compact reproducible benchmark, source ratios and physics readout (not EoR)."""
from __future__ import annotations
import json,statistics,time,platform,sys
from math import isclose
from threshold_rt import frozen_source
from compressed_cohorts import CompressionHold, frozen_be_readout
from fast_compression import HeapCompressedCohortTransport
from curvature_bounds import CurvatureHeapCompressedCohortTransport,frozen_be_readout_binding
from directed_curvature import DirectedCurvatureHeap,second_sigma_up
NN=(1e-3,8e-5,2e-5)
OWNER_BIND=(13.598434599702,24.587389011,54.41776)
DT=1e9


def case(name,cls,start,cap,binding=None,repeats=7):
    history=[]; instance=None; cert=None; status=None
    for _ in range(repeats):
        args=dict(binding_eV=binding) if binding is not None and cls==DirectedCurvatureHeap else {}
        obj=cls(start,cap,**args)
        t=time.perf_counter()
        try:
            got=obj.compress(NN,DT,.995,.01,1.)
            out='PASS'
        except CompressionHold:
            got=None
            out='HOLD'
        history.append((time.perf_counter()-t)*1e3)
        if status is not None:assert out==status
        status=out;instance=obj;cert=got
    res=dict(method=name,cap=cap,status=status,median_ms=statistics.median(history),timings_ms=history)
    if cert:
        res.update(initial=cert.initial_cohorts,final=cert.final_cohorts,merges=cert.merges,
                   event_abs_bound=list(cert.event_absolute_bounds),
                   heat_abs_bound_eV=list(cert.heat_absolute_bounds_eV),
                   number_energy=list(instance.moments()),certificate_status=cert.status)
        def diff(aa,bb):return [bb[i]-aa[i] for i in range(3)]
        reference=frozen_be_readout_binding if binding is not None else frozen_be_readout
        samples=[]
        for ratio in (1,.999,.997,.995):
            args=dict(binding_eV=binding) if binding is not None else {}
            before,heat0=reference(start,NN,DT,ratio,**args)
            after,heat1=reference(instance.cohorts,NN,DT,ratio,**args)
            de=diff(before,after);dh=diff(heat0,heat1)
            for k in range(3):
                assert abs(de[k])<=(cert.event_absolute_bounds[k]+1e-13)
                assert abs(dh[k])<=(cert.heat_absolute_bounds_eV[k]+1e-13)
            samples.append(dict(ratio=ratio,event_differences=de,heat_differences_eV=dh))
        res['actual_signed_differences']=samples
    return res


def execute(repeats=7):
    start=frozen_source(16)
    assert len(start)==48
    cases=[case('FIRST_ORDER_HEAP',HeapCompressedCohortTransport,start,26,repeats=repeats),
           case('FIRST_ORDER_HEAP',HeapCompressedCohortTransport,start,22,repeats=repeats),
           case('SECOND_ORDER_FLOAT_HEAP',CurvatureHeapCompressedCohortTransport,start,22,repeats=repeats),
           case('SECOND_ORDER_DECIMAL85_HEAP',DirectedCurvatureHeap,start,22,repeats=repeats),
           case('SECOND_ORDER_DECIMAL85_PHYSICAL_BINDING',DirectedCurvatureHeap,start,22,OWNER_BIND,repeats=repeats),
           case('SECOND_ORDER_DECIMAL85_HEAP',DirectedCurvatureHeap,start,20,repeats=repeats)]
    info=second_sigma_up.cache_info()
    return dict(source='MD14_BB50K_SOURCE_COHORT_16_VERNNER_REAL_REF',
      scope='frozen-neutrals 1e9s one-step BE only; no coupled cosmic history',
      env=dict(python=sys.version.split()[0],machine=platform.machine(),repeats=repeats),
      neutrals_cm3=NN,proper_dt_s=DT,energy_redshift_range=(.995,1.),
      event_budget_count_per_H_per_species=.01,heat_budget_eV_per_H_per_species=1.,
      source_cohorts=48,source_first_moments=[sum(n for e,n in start),sum(e*n for e,n in start)],
      physical_binding_eV=OWNER_BIND,fit_cutoffs_eV=(13.60,24.59,54.42),
      cases=cases,decimal_cache=dict(hits=info.hits,misses=info.misses,maxsize=info.maxsize))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--repeats',type=int,default=7)
    opts=parser.parse_args()
    print(json.dumps(execute(opts.repeats),indent=2))
