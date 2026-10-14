"""Source-locked, frozen-neutral component benchmark. No owner REI history."""
from __future__ import annotations
import json
from compressed_cohorts import (
    CompressedCohortTransport,CompressionHold,frozen_be_readout
)
from threshold_rt import CohortTransport,frozen_source,ION_NAMES

NEUTRALS=(1e-3,8e-5,2e-5)
DT=1e9

def packet_comparison(axis=16,target=32,min_ratio=.99,event_budget=.01,heat_budget=1.):
    base=frozen_source(axis)
    item=CompressedCohortTransport(base,max_cohorts=target)
    cert=item.compress(NEUTRALS,DT,min_ratio,event_budget,heat_budget)
    snapshots=[]
    for r in (1.,.999,.995,min_ratio):
        old_ev,old_heat=frozen_be_readout(base,NEUTRALS,DT,r)
        new_ev,new_heat=frozen_be_readout(item.cohorts,NEUTRALS,DT,r)
        de=[abs(x-y) for x,y in zip(old_ev,new_ev)]
        dh=[abs(x-y) for x,y in zip(old_heat,new_heat)]
        snapshots.append({'redshift_ratio':r,'rate_event_actual_delta_abs':dict(zip(ION_NAMES,de)),
            'heat_actual_delta_abs_eV':dict(zip(ION_NAMES,dh)),
            'all_inside_local_bound':all(de[k]<=cert.event_absolute_bounds[k] and dh[k]<=cert.heat_absolute_bounds_eV[k] for k in range(3)),
            'reference_events':dict(zip(ION_NAMES,old_ev)), 'compressed_events':dict(zip(ION_NAMES,new_ev))})
    return {'axis':axis,'original_cohorts':len(base),'compressed_cohorts':len(item.cohorts),
        'local_analytical_certificate':dict(cert.__dict__), 'snapshots':snapshots,
        'note':'Only one frozen-neutral BE step across declared redshift tube; not a propagated full-history bound.'}


def repeated_injection_experiment(axis=16,steps=4,cap=32,injection_scale=.1):
    start=frozen_source(axis)
    ref=CohortTransport(start)
    compact=CompressedCohortTransport(start,max_cohorts=cap)
    initial=compact.compress(NEUTRALS,DT,.995,.05,10.)
    results=[]
    for i in range(steps):
        before_ref=ref.moments(); before_c=compact.moments()
        ref_red=ref.redshift(.997);cp_red=compact.redshift(.997)
        ref_abs=ref.absorb_backward_euler(NEUTRALS,DT)
        cmp_abs=compact.absorb_backward_euler(NEUTRALS,DT)
        source=[(e,n*injection_scale) for e,n in start]
        # Raw uncompressed reference source addition; physical transport is
        # otherwise identical in this controlled comparison.
        ref.cohorts.extend(source)
        cert=compact.inject_and_compress(source,NEUTRALS,DT,.995,.05,10.)
        event_deltas={k:cmp_abs['photo_events_per_H'][k]-ref_abs['photo_events_per_H'][k] for k in ION_NAMES}
        heat_deltas={k:cmp_abs['direct_photoheat_eV_per_H'][k]-ref_abs['direct_photoheat_eV_per_H'][k] for k in ION_NAMES}
        post_ref=ref.moments();post_c=compact.moments()
        results.append({'step':i+1,'raw_cohorts':len(ref.cohorts),'compressed_cohorts':len(compact.cohorts),
            'compression_merges':cert.merges,
            'source_injection_count':injection_scale,
            'event_deltas_comp_minus_uncompressed':event_deltas,'heat_deltas_eV':heat_deltas,
            'first_moment_after_ref':post_ref,'first_moment_after_compressed':post_c,
            'number_residual_raw':ref_red['number_residual']+ref_abs['number_residual'],
            'number_residual_compressed':cp_red['number_residual']+cmp_abs['number_residual'],
            'energy_residual_raw_eV':ref_red['energy_residual_eV']+ref_abs['energy_residual_eV'],
            'energy_residual_compressed_eV':cp_red['energy_residual_eV']+cmp_abs['energy_residual_eV']})
    return {'initial_compression':initial.__dict__,'rows':results,
        'note':'Empirical multi-step comparison; certificates at each compression are local only, not a global trajectory error guarantee.'}


def hold_case():
    obj=CompressedCohortTransport.frozen_source(16,max_cohorts=16)
    old=obj.cohorts.copy()
    try:obj.compress(NEUTRALS,DT,.98,.01,1.)
    except CompressionHold as exc:
        return {'status':'HOLD_EXPECTED', 'message':str(exc),'transactional':old==obj.cohorts}
    raise AssertionError('unexpected unsafe compression accepted')


def main():
    result={'source_id':'MD14_Z002_FESC_BB50K_13P6_100_V1',
            'one_step':packet_comparison(),
            'four_step':repeated_injection_experiment(),
            'explicit_hold':hold_case(),
            'admission':'SCOPED_COMPONENT_ONLY_REI_HISTORY_NOT_RUN'}
    assert all(a['all_inside_local_bound'] for a in result['one_step']['snapshots'])
    assert all(row['compressed_cohorts']<=32 for row in result['four_step']['rows'])
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
