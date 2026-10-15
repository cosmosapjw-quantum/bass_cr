"""Matched source corpus, adaptive-vs-uniform q support; not cosmological simulation."""
import argparse,json,time
import numpy as np
from adaptive_q import PositivePacketOracle,AdaptiveQGrid
from source_subcells import source_quadrature, reaction_fraction, reference_edges, PHYSICAL_BINDING

EMITTED=4.298036114764196e-8
REAL_RHO=(0.0017575700008892194,.0001429214010766023,0.)
REAL_DT=1e10
BUDGET=(1e-8,1e-9,1e-12,1e-7,1e-8,1e-11)
HEI_FOCUS_BUDGET=(.1,1e-10,.1,.1,.1,.1)

def current_packets(hardened=False):
    if not hardened:
        s=source_quadrature(1024,order=8)
        return PositivePacketOracle(s.energy_nodes_ref_eV,s.photon_weight_per_initial_H*EMITTED,'MD14_BB50K_NATIVE48','ray-mu-0.25',0.),1.,REAL_RHO,REAL_DT
    old=source_quadrature(512,ratio_R=.98,order=8)
    new=source_quadrature(512,ratio_R=1.,order=8)
    gas_pre=(.001,.00012,.00001)
    frac,survivors=reaction_fraction(old.energy_nodes_ref_eV*.99,gas_pre,2e9)
    energies=np.r_[old.energy_nodes_ref_eV,new.energy_nodes_ref_eV]
    weights=np.r_[old.photon_weight_per_initial_H*.5*EMITTED*survivors,new.photon_weight_per_initial_H*.5*EMITTED]
    return PositivePacketOracle(energies,weights,'MD14_TWO_BIRTH_PACKET_ORACLE','ray-mu-0.25',0.),.97,(.0008,.00009,.000005),4e9


def packet_truth(oracle,ratio,gas,dt):
    energies=np.asarray([float(e)*ratio for e in oracle.energies])
    counts=np.asarray([float(n) for n in oracle.counts])
    events,_=reaction_fraction(energies,gas,dt)
    val=events@counts
    heat=(events*(energies[None,:]-np.asarray(PHYSICAL_BINDING)[:,None]))@counts
    return np.r_[val,heat]


def run_case(oracle,ratio,gas,dt,base=64,targets=(80,96,128),node_order=4,budgets=BUDGET):
    edges=np.geomspace(13.6,433.,base+1)
    model=AdaptiveQGrid(oracle,edges,ratio,gas,dt,budgets,nodes_per_branch=node_order)
    truth=packet_truth(oracle,ratio,gas,dt)
    results=[]
    start=time.perf_counter()
    for target in targets:
        t0=time.perf_counter()
        out=model.run(target)
        elapsed=time.perf_counter()-t0
        ranges=np.asarray(out['event']+out['heat'])
        assert np.all(ranges[:,0]<=truth+5e-26) and np.all(ranges[:,1]>=truth-5e-26),('missed actual positive packet observable',target)
        results.append(dict(n_cells=target,n_active=out['nonempty'],elapsed_step_s=elapsed,
                            total_elapsed_s=time.perf_counter()-start,heI_width=out['widths'][1],
                            heI_halfwidth_per_true=out['widths'][1]/(2*truth[1]),
                            HI_width=out['widths'][0],heat_sum_width=sum(out['widths'][3:]),
                            shape_free_ranges=ranges.tolist(),memory_bytes=out['stored_moments_bytes'],
                            n_splits=out['splits'],precision_gate=out['precision_gate']))
    return model,results,truth


def uniform(oracle,ratio,gas,dt,n,order=4):
    t0=time.perf_counter()
    model=AdaptiveQGrid(oracle,reference_edges(n),ratio,gas,dt,BUDGET,nodes_per_branch=order)
    out=model.summary()
    return dict(n_cells=n,nonempty=out['nonempty'],elapsed_s=time.perf_counter()-t0,
                heI_width=out['widths'][1],HI_width=out['widths'][0],
                heat_sum_width=sum(out['widths'][3:]),memory_bytes=out['stored_moments_bytes'])


def main():
    arg=argparse.ArgumentParser();arg.add_argument('--base',type=int,default=64);arg.add_argument('--max',type=int,default=128);arg.add_argument('--hardened',action='store_true');arg.add_argument('--uniform',type=int,nargs='*',default=[64,128]);arg.add_argument('--order',type=int,default=4);arg.add_argument('--priority',choices=('HEI','SIX'),default='HEI');p=arg.parse_args()
    oracle,r,gas,dt=current_packets(p.hardened)
    targets=tuple(x for x in (48,64,80,96,128,192,256) if x>p.base and x<=p.max)
    budgets=HEI_FOCUS_BUDGET if p.priority=='HEI' else BUDGET
    model,adapt,truth=run_case(oracle,r,gas,dt,p.base,targets,p.order,budgets)
    uni=[uniform(oracle,r,gas,dt,n,p.order) for n in p.uniform]
    result={'scope':'ONE_ANGULAR_LANE_ONE_CURRENT_PROPER_TIME; TRUE_CHILD_PACKETS_REQUIRED',
            'kind':'TWO_BIRTH_HARDENED' if p.hardened else 'ORIGINAL_NATIVE48_BB50K',
            'original_source':'MD14_Z002_FESC_BB50K_13P6_100_V1_NATIVE48',
            'moments':'exact_fraction_reconstruction_of_stored_binary64_packets',
            'ratio_R':r,'neutrals_cm3':gas,'dt_s':dt,'packet_count':len(oracle.counts),
            'truth_events':truth[:3].tolist(),'truth_heat':truth[3:].tolist(),
            'initial_bins':p.base,'score_objective':p.priority,'observable_budgets':budgets,'adaptive':adapt,'uniform':uni,
            'adaptive_last_edges':model.sorted_edges(),
            'note':'The physical photon packets are additional input. Cannot refine arbitrary SOURCE07 N/U parent without genuine child moments.'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
