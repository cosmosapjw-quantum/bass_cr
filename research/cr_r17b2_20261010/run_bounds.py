"""Whole homotopy common gas/survival tube and zeroth-kernel bound.
Every estimate is directed interval arithmetic over the entire macro and all
weights. High order resolvent jets and traces are explicitly NOT inferred.
"""
import sys,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from interval_backend import I,AD
from source_kernel import *

def compute():
 p=load_pins();plan=p['BIRTH_PLAN.json'];initial=p['INITIAL.json']['seed'];z0=[I(v) for v in initial['gas'][:3]]+[I(1)]
 tube=[I('.89','.91'),I('.29','.31'),I('.59','.61'),I('.99','1.01')]
 u=I(0,1);e=I(*EB)*(-I(H)*T*u).exp();nh=I(NH)*(-I(3)*H*T*u).exp()
 if e.lo<I(13.6).hi or e.hi>=I(24.59).lo:raise ValueError('ENERGY_SUPPORT')
 np,temp=nonphoto_rhs(u,[AD.variable(v,j) for j,v in enumerate(tube)])
 if temp.v.lo<30000 or temp.v.hi>110000:raise ValueError('THERMAL_DOMAIN')
 masses=[I(v['lo'],v['hi']) for v in plan['same_source_weight_boxes'].values()]
 disc=sum(masses,I(0));cont=I(5e-15)*T
 source_max=max(disc.hi,cont.hi);P=I(initial['p'][0])+I(source_max)
 # All eta in [0,1]: total positive mass <= max(Q_total,S*T), not their sum.
 A=I(T)*C*nh*sigma(e);kap=A*(1-tube[0]);photo=kap*I(0,P.hi);heat=(e-CHI[0])*photo/W0
 field=[v.v for v in np];field[0]+=photo;field[3]+=heat
 radii=[I(v.mag()) for v in field]
 margins=[min((v-I(box.lo)).lo,(I(box.hi)-v).lo) for v,box in zip(z0,tube)]
 selfmap=all(r.hi<m for r,m in zip(radii,margins))
 if not selfmap:raise ValueError('COMMON_TUBE_SELF_MAP_FAILED')
 Lnp=max(sum((I(v.mag()) for v in row.g),I(0)).hi for row in np)
 # Companion variation: |dp_b(t)|<=p_b(t)*int_b^t A(s)|dx(s)|ds.
 # The current-photon term and survival-memory term are both retained.
 gain=P*I(A.hi)*(1+I(kap.hi));heat_gain=gain*I((e-CHI[0]).mag())/W0
 q=I(Lnp)+I(max(gain.hi,heat_gain.hi))
 if q.hi>=1:raise ValueError('COMMON_TUBE_CONTRACTION_FAILED')
 direct=I(kap.hi)*I(max(I(1).hi,(I((e-CHI[0]).mag())/W0).hi))
 response=direct/(1-q)
 goal=I(T)*C*I(6.6524587e-25)*nh*(I(1)+I(3)*FHE)
 K0=goal*response
 return {'classification':'BOUNDED_COMMON_HOMOTOPY_TUBE_AND_COARSE_ARBITRARY_BIRTH_K0',
 'eta_domain':[0,1],'weights':'all pinned boxes independently; no mass renormalization',
 'gas_tube':[v.data() for v in tube],'gas_selfmap_scaled_radii':[v.data() for v in radii],'initial_to_tube_margins':[str(v) for v in margins],
 'thermal_tube_K':temp.v.data(),'energy_tube_eV':e.data(),'companion_total_mass_bound':P.data(),
 'nonphoto_Jacobian_4x4':[[v.data() for v in row.g] for row in np],
 'nonphoto_L':I(Lnp).data(),'current_and_memory_gain':gain.data(),'heat_current_and_memory_gain':heat_gain.data(),
 'q_contraction':q.data(),'probe_survival':[(-I(kap.hi)).exp().data()[0],'1'],
 'all_birth_K0_signed_enclosure':[(-I(K0.hi)).data()[0],I(K0.hi).data()[1]],
 'anchor_1_2_3':None,'regular_fourth':None,'jumps_0_1_2_3':None,
 'source_error_interval':None,'source_sharpening':'NO_CERTIFIED_SOURCE_SHARPENING',
 'missing':'Validated birth-resolvent derivative flow through order4, time/birth boundary traces through order3 over full eta and original weight family. The common gas tube bounds values and gas Jacobians, not those derivative flows.',
 'later_cells':'Covered by unchanged latest causal whole-macro fallback; no partial source replacement.',
 'new_time_interval':None,'old_bounds':'UNCHANGED'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args()
 r=compute()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:r[k] for k in ['classification','q_contraction','all_birth_K0_signed_enclosure','source_sharpening']}))
