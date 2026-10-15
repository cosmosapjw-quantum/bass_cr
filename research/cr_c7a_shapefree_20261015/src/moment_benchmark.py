"""Actual source and two-epoch hardened spectrum test with shape-free envelopes."""
import argparse,json,time,sys,math
import numpy as np
from source_subcells import (source_quadrature, source_and_reaction,
                             reaction_fraction, reference_edges)
from moment_envelopes import make_template,enclose_q_bins,cached_template

SOURCE=4.298036114764196e-8
RHO=(0.0017575700008892194,0.0001429214010766023,0.)
BINDING=(13.598434599702,24.587389011,54.41776)
DT=1e10


def single(n:int,order:int=4):
    q=source_quadrature(n,order=8);N,U=q.number_and_energy();ref=reference_edges(n)
    true=source_and_reaction(q,RHO,DT,SOURCE)
    beg=time.perf_counter()
    bounds=enclose_q_bins(ref,N*SOURCE,U*SOURCE,1.,RHO,DT,order)
    dur=time.perf_counter()-beg
    t=np.r_[true['absorb_species'].sum(axis=1),true['heat_species'].sum(axis=1)]
    ranges=np.vstack([bounds['event'],bounds['heat']]); assert np.all(ranges[:,0]<=t+1e-26) and np.all(t<=ranges[:,1]+1e-26)
    return dict(n_energy=n,nonempty=int(np.count_nonzero(N)),duration_s=dur,
                event_true=t[:3].tolist(),event_lower=bounds['event'][:,0].tolist(),
                event_upper=bounds['event'][:,1].tolist(),
                heat_true=t[3:].tolist(),heat_lower=bounds['heat'][:,0].tolist(),
                heat_upper=bounds['heat'][:,1].tolist(),
                HeI_relative_halfwidth=(bounds['event'][1,1]-bounds['event'][1,0])/(2*t[1]))


def mixed_age(n:int=256):
    # Two different emission ages sharing q-bin support, then older packets
    # partially pre-absorbed. The original BB source shape no longer applies.
    q_old=source_quadrature(n,ratio_R=.98,order=8)
    q_new=source_quadrature(n,ratio_R=1.0,order=8)
    ratio_now=.97
    gas_pre=(.001,.00012,.00001)
    f_pre,survive_old=reaction_fraction(q_old.energy_nodes_ref_eV*.99,gas_pre,2e9)
    old_weights=q_old.photon_weight_per_initial_H*.5*SOURCE*survive_old
    new_weights=q_new.photon_weight_per_initial_H*.5*SOURCE
    indices=np.r_[q_old.q_index,q_new.q_index]
    energies_ref=np.r_[q_old.energy_nodes_ref_eV,q_new.energy_nodes_ref_eV]
    weights=np.r_[old_weights,new_weights]
    N=np.bincount(indices,weights=weights,minlength=n)
    U=np.bincount(indices,weights=weights*energies_ref,minlength=n)
    physical=energies_ref*ratio_now
    gas_now=(.0008,.00009,.000005)
    frac,_=reaction_fraction(physical,gas_now,4e9)
    truth_e=np.sum(frac*weights[None,:],axis=1)
    truth_h=np.sum(frac*weights[None,:]*(physical[None,:]-np.asarray(BINDING)[:,None]),axis=1)
    edges=reference_edges(n)
    before=time.perf_counter()
    b=enclose_q_bins(edges,N,U,ratio_now,gas_now,4e9,4)
    sec=time.perf_counter()-before
    assert np.all(b['event'][:,0]<=truth_e+1e-25) and np.all(b['event'][:,1]>=truth_e-1e-25)
    assert np.all(b['heat'][:,0]<=truth_h+1e-22) and np.all(b['heat'][:,1]>=truth_h-1e-22)
    return dict(qbin=n,birth_ratios=[.98,1.],eval_ratio=.97,
                preabsorption_gas=gas_pre,preabsorption_dt_s=2e9,
                current_gas=gas_now,current_dt_s=4e9,
                two_ages_no_BB_reclosure=True,mass=float(N.sum()),
                physical_energy=float((U*ratio_now).sum()),
                event_truth=truth_e.tolist(),event_lower=b['event'][:,0].tolist(),event_upper=b['event'][:,1].tolist(),
                heat_truth=truth_h.tolist(),heat_lower=b['heat'][:,0].tolist(),heat_upper=b['heat'][:,1].tolist(),
                elapsed_s=sec)


def preview_speed(samples=10000):
    rho=(.001,.0001,.00001)
    t=cached_template(24.,26.,rho,DT,6)
    means=np.linspace(24,26,samples)
    masses=np.linspace(.01,1.,samples)
    beg=time.perf_counter();vec=t.vector_preview(masses,means)
    fast=time.perf_counter()-beg
    beg=time.perf_counter();serial=[t.evaluate(float(n),float(m)) for n,m in zip(masses,means)]
    slow=time.perf_counter()-beg
    for idx in sorted({0, min(13,samples-1), min(241,samples-1), min(3479,samples-1), samples-1}):
        assert math.isclose(vec['event_upper'][1,idx],serial[idx]['event'][1][1],rel_tol=2e-13,abs_tol=1e-14)
    return dict(samples=samples,vectorized_s=fast,exact_dyadic_serial_s=slow,speedup=slow/fast,
                preview_is_certified=False)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--single',type=int,nargs='*',default=[64,128,256,512,1024]);ap.add_argument('--preview',type=int,default=10000)
    args=ap.parse_args()
    results=dict(schema='bass-cr-moment-shape-free-v1',source='MD14_Z002_FESC_BB50K_13P6_100_V1_NATIVE48',
                 reference='source_subcells.py C10, q-energy support 13.6..433eV',
                 continuous_gas_only=True,
                 single=[single(n) for n in args.single],mixed_age=mixed_age(256),preview=preview_speed(args.preview))
    print(json.dumps(results,indent=2))
