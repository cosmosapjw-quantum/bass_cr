"""Read-only C21B signed/source-age multi-species reference comparison.

Uses exact independently retained parent PR76 source. Does not call/claim
NCP native Rust or original `igm_point_rhs`.
"""
from __future__ import annotations
from dataclasses import asdict
import math
import pathlib,sys
import numpy as np
from exposure_contract import native_photo_rates
from radau_exposure_oracle import run_reference,make_cohorts,N_H0,H


def parent_source():
    import os
    candidates=[pathlib.Path(os.environ['C21B_PYTHON_PATH'])] if 'C21B_PYTHON_PATH' in os.environ else [
        pathlib.Path(__file__).resolve().parents[2]/'cr_c21b_age_reactor_20261016'/'src',
        pathlib.Path(__file__).resolve().parents[1]/'vendor'/'pr76']
    p=next((q for q in candidates if (q/'c21b_age_reactor.py').is_file()),candidates[0])
    if not (p/'c21b_age_reactor.py').exists():
        raise FileNotFoundError('Need exact published C21B PR76 source; do not use surrogate')
    sys.path.insert(0,str(p))
    import c21b_age_reactor as b
    return b


def run_split_reference(steps_per_interval:int, x0=math.log(1/12),dx=.025,opacity_scale=.001):
    b=parent_source()
    cohorts,old=make_cohorts(x0,dx)
    model=b.PhotonReactor(source_scale=0.0,opacity_scale=opacity_scale)
    initial=tuple((c.q20/math.exp(x0),c.start_n) for c in cohorts[:old])
    s=b.initial_state(x0,T_K=8500.,fractions=(.2,.15,.01),injected_initial=initial)
    ends=sorted({c.birth_x for c in cohorts[old:]})+[x0+dx]
    for end in ends:
        s=model.advance(s,end,steps_per_interval,source_on=False,split_thresholds=True)
        for c in cohorts[old:]:
            if c.birth_x==end:
                # Impulse is a separately specified original source-age transaction.
                # Every packet's birth_x and q are retained (no centroid collapse).
                s.photons.append(b.Photon(c.q20,c.start_n,c.birth_x,c.q20/math.exp(c.birth_x),len(s.photons)+1))
                s.source_n+=c.start_n
                s.source_u+=c.start_n*c.q20/math.exp(c.birth_x)
    s.validation()
    return s


def compare(steps=(2,4,8,16,32,64),dx=.025,opacity_scale=.001):
    ref=run_reference(dx=dx,opacity_scale=opacity_scale)
    j=len(ref.cohorts)
    exact=np.r_[ref.yfinal[:j],ref.yfinal[j:j+5],ref.yfinal[j+5]]
    data=[]
    for m in steps:
        s=run_split_reference(m,dx=dx,opacity_scale=opacity_scale)
        candidate=np.r_[[p.number for p in s.photons],s.atoms,s.thermal_ev]
        d=float(np.max(abs(candidate-exact)))
        # Reconstruct real-time exposure only from the independently integrated
        # trajectory, not summed Strang pseudo-time subflows.
        alpha_end=(s.atoms[0],s.atoms[2],s.atoms[3])
        bridge=native_photo_rates(s.photo_events,s.photoheat,ref.exposures,alpha_end,
                 ref.endpoint_rates.delta_t_s,N_H0*math.exp(-3*s.x))
        led=s.ledgers()
        data.append(dict(segments_per_birth_interval=m,state_difference_inf=d,
                         number_residual=led['number_residual'],
                         energy_residual_ev_H=led['energy_residual_ev_per_H'],
                         gamma_endpoint_s=bridge.gamma_endpoint_s,
                         rate_condition=bridge.endpoint_condition,
                         total_photoevents=s.photo_events,
                         thermal_ev=s.thermal_ev,
                         final_fractions=s.fractions()))
    for a,b1 in zip(data,data[1:]):
        a['next_refinement_observed_order']=math.log(a['state_difference_inf']/b1['state_difference_inf'],2) if a['state_difference_inf']>0 and b1['state_difference_inf']>0 else None
    return dict(reference=dict(cohorts=j,split_segments=ref.segments,
      number_residual=ref.mass_res,energy_residual_ev_H=ref.energy_res,
      gamma_exposure_s=ref.endpoint_rates.gamma_exposure_s,
      gamma_endpoint_s=ref.endpoint_rates.gamma_endpoint_s,
      endpoint_condition=ref.endpoint_rates.endpoint_condition,
      photon_events_H=ref.endpoint_rates.events_H,
      photothermal_ev_H=ref.endpoint_rates.photoheat_ev_H,
      exposure_H_s=ref.exposures,
      source_n=ref.source_n,source_u_ev_H=ref.source_u,
      gas_end=ref.yfinal[j:j+5].tolist(),thermal_end_ev_H=ref.yfinal[j+5]),
      controlled=dict(dx=dx,opacity_scale=opacity_scale,old_packets=3,source_births=2,
      source_energy_nodes_each=3,positive_time_segments=3,method='C21B Strang exact pairs vs independent physical Radau exposure ODE'),
      sequence=data)

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=pathlib.Path,required=True)
    p.add_argument('--n',nargs='+',type=int,default=[2,4,8,16,32,64])
    args=p.parse_args()
    res=compare(args.n)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(res,indent=2)+'\n')
    for r in res['sequence']:
        print('n',r['segments_per_birth_interval'],'error',r['state_difference_inf'],'next_order',r.get('next_refinement_observed_order'),'energy_res',r['energy_residual_ev_H'])
