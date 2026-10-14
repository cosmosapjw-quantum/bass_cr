"""Native-source-compatible Python offline component benchmarks (not native history)."""
from __future__ import annotations
from math import isfinite
from scipy.integrate import quad
from threshold_rt import (
    TaggedGrid, OriginalGrid, frozen_grid, frozen_source, verner, source_shape,
    ION_NAMES, ATOMIC, SOURCE_EDGES, C_CM_S
)

NEUTRALS=(1.0e-3,8.0e-5,2.0e-5)  # fixed illustrative cm^-3, not AXBI history input
TIME_S=1.0e9


def integrated_true(redshift_factor:float=1.0,neutral=NEUTRALS,dt=TIME_S):
    """True continuum *source* reference for one frozen-neutral BE transaction."""
    s_norm=sum(quad(source_shape,a,b,epsabs=0,epsrel=2e-12)[0] for a,b in zip(SOURCE_EDGES,SOURCE_EDGES[1:]))
    lower=SOURCE_EDGES[0]/redshift_factor
    cutpoints=sorted(set([*SOURCE_EDGES,*[ATOMIC[k][0]/redshift_factor for k in ION_NAMES]]))
    bounds=[p for p in cutpoints if SOURCE_EDGES[0]<=p<=SOURCE_EDGES[-1]]
    active_low=max(SOURCE_EDGES[0],lower)
    out={'events':{k:0.0 for k in ION_NAMES},'heat':{k:0.0 for k in ION_NAMES},'binding':{k:0.0 for k in ION_NAMES}}
    def integrate_part(f):
        total=0.
        for a,b in zip(bounds,bounds[1:]):
            lo=max(active_low,a)
            if lo<b:total+=quad(f,lo,b,epsabs=1e-40,epsrel=2e-11,limit=100)[0]
        return total/s_norm
    for j,k in enumerate(ION_NAMES):
        def event_kernel(E):
            E1=E*redshift_factor
            sigma=[verner(a,E1) for a in ION_NAMES]
            rates=[dt*C_CM_S*n*s for n,s in zip(neutral,sigma)]
            return source_shape(E)*rates[j]/(1+sum(rates))
        val=integrate_part(event_kernel)
        out['events'][k]=val
        out['binding'][k]=val*ATOMIC[k][0]
        out['heat'][k]=integrate_part(lambda E:event_kernel(E)*(E*redshift_factor-ATOMIC[k][0]))
    out['photon_boundary_probability']=quad(source_shape,SOURCE_EDGES[0],min(SOURCE_EDGES[-1],active_low),epsabs=0,epsrel=2e-12)[0]/s_norm if active_low>SOURCE_EDGES[0] else 0.
    return out


def benchmark_one(n:int,redshift_factor:float=1.,neutral=NEUTRALS,dt=TIME_S):
    baseline=OriginalGrid(frozen_grid(n));tagged=TaggedGrid(frozen_grid(n))
    b=baseline.from_frozen_source(n);t=tagged.from_frozen_source(n)
    b,br=baseline.redshift(b,redshift_factor);t,tr=tagged.redshift(t,redshift_factor)
    b2,bl=baseline.absorb_backward_euler(b,neutral,dt)
    t2,tl=tagged.absorb_backward_euler(t,neutral,dt)
    ref=integrated_true(redshift_factor,neutral,dt)
    summary={'cells_per_segment':n,'redshift_factor':redshift_factor,'total_receiver_nodes_baseline':len(baseline.states),'tagged':len(tagged.states),
             'reference':ref,'baseline':bl,'tagged_result':tl,
             'boundary_counts':{'reference':ref['photon_boundary_probability'],'baseline':br['boundary_count'],'tagged':tr['boundary_count']},
             'source_energy_eV':baseline.moments(b)[1],
             'relative_error':{'baseline':{},'tagged':{}}}
    for method,led in [('baseline',bl),('tagged',tl)]:
        for kind in ('events','heat'):
            for name in ION_NAMES:
                reference=ref[kind][name]
                if reference>0:
                    summary['relative_error'][method][f'{kind}_{name}']=led['photo_events_per_H' if kind=='events' else 'direct_photoheat_eV_per_H'][name]/reference-1
    return summary


def multistep(n:int=16,ratios=(.997,.992,.986),neutral=NEUTRALS,dt=TIME_S):
    results={}
    for cls,label in ((OriginalGrid,'baseline'),(TaggedGrid,'tagged')):
        grid=cls(frozen_grid(n));p=grid.from_frozen_source(n);overall_boundary=0;overall_boundary_energy=0;overall_work=0;overall_births=0;overall_heat=0;overall_binding=0
        before_n,before_u=grid.moments(p)
        steps=[]
        for ratio in ratios:
            p,ledger=grid.redshift(p,ratio)
            q,le=grid.absorb_backward_euler(p,neutral,dt)
            n_in,u_in=grid.moments(p);n_out,u_out=grid.moments(q)
            overall_boundary+=ledger['boundary_count'];overall_boundary_energy+=ledger['boundary_energy_eV'];overall_work+=ledger['photon_redshift_work_eV']
            overall_births+=le['free_electron_births_per_H'];overall_heat+=sum(le['direct_photoheat_eV_per_H'].values());overall_binding+=sum(le['binding_eV_per_H'].values())
            steps.append({'N_after':n_out,'U_after_eV':u_out,'boundary_count':ledger['boundary_count'],'redshift_work_eV':ledger['photon_redshift_work_eV'],
                          'absorption_count_residual':le['count_ledger_residual'],'absorption_energy_residual':le['energy_ledger_residual_eV']})
            p=q
        final_n,final_u=grid.moments(p)
        results[label]={'steps':steps,'boundary_count_total':overall_boundary,'boundary_energy_total_eV':overall_boundary_energy,'redshift_work_total_eV':overall_work,'absorbed_total':overall_births,
                        'direct_heat_total_eV':overall_heat,'binding_total_eV':overall_binding,'final_N':final_n,'final_U_eV':final_u,
                        'number_balance':before_n-final_n-overall_boundary-overall_births,
                        'energy_balance':before_u-final_u-overall_boundary_energy-overall_work-overall_heat-overall_binding,
                        'status':'MULTISTEP_FROZEN_NEUTRALS_NOT_COUPLED_REI_HISTORY'}
    return results

if __name__=='__main__':
    import json
    x={'initial':[benchmark_one(n) for n in (16,32,64,128)],'redshift':[benchmark_one(n,.98) for n in (16,32,64)],
       'multistep':multistep(),'scope':'isolated source/spectral transport and frozen-neutral one-step implicit absorption only'}
    print(json.dumps(x,indent=2))


def exact_packet_control(n:int=16,redshift_factor:float=1.,neutral=NEUTRALS,dt=TIME_S):
    """No re-projection: centroids transported on characteristics, then BE absorbed.

    Diagnostic only. Number of packets grows with source injections in production.
    """
    if not 0<redshift_factor<=1:raise ValueError('redshift factor must be in (0,1]')
    events={k:0. for k in ION_NAMES}; heat={k:0. for k in ION_NAMES}
    binding={k:0. for k in ION_NAMES}; boundary=0.
    for E,f in frozen_source(n):
        e=E*redshift_factor
        if e<SOURCE_EDGES[0]:
            boundary+=f;continue
        rate=[dt*C_CM_S*dens*verner(k,e) for dens,k in zip(neutral,ION_NAMES)]
        surviving=f/(1+sum(rate))
        for j,k in enumerate(ION_NAMES):
            count=surviving*rate[j]; events[k]+=count
            binding[k]+=count*ATOMIC[k][0]; heat[k]+=count*(e-ATOMIC[k][0])
    return {'events':events,'heat':heat,'binding':binding,'boundary_probability':boundary,
            'reference':'unprojected source centroids, not continuous source and not production memory/cost'}
