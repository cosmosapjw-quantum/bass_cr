"""Use unchanged R17B2A baseline for NEW surrogate eta=.5,1 experiments.
No old eta=0 suite or original donor trajectory is run. Auxiliary continuum
quadrature has an independent mathematical error budget; point solve error
remains unvalidated, so all reported point/tangent/finite-dose values are diagnostic.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import sys,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'inherited/R17B2A/src'))
from birth_response import Background
from quadrature_bound import auxiliary
sys.path.insert(0,str(ROOT/'src'))
from homotopy import load_contract
from fractions import Fraction as F

def run():
 original=load_contract()['plan'];rows=[]
 for n in [16,32]:
  for eta in [.5,1.]:
   auxiliary_rows,budget=auxiliary(n,eta);combined={}
   for b in original['same_births']:
    weight=original['same_source_weight_boxes'][str(b)]['weight']*(1-eta);combined[b]=weight
   for row in auxiliary_rows:combined[row['birth_proper_s']]=combined.get(row['birth_proper_s'],0)+eta*row['weight']
   births=sorted(combined);surrogate=dict(same_births=births,same_source_weight_boxes={str(b):dict(weight=combined[b]) for b in births})
   base=Background(surrogate);base.backward();points=[]
   for b in [.1,.3540127993818848,.8]:
    fw=base.probe(b);bw=base.probe_adjoint(b);gap=abs(fw['K_tau']-bw['K_tau'])/max(abs(fw['K_tau']),1e-30)
    assert gap<1e-8;assert abs(fw['charge_identity_residual'])<1e-11;assert abs(fw['old_heat_identity_residual'])<1e-14
    points.append(dict(forward=fw,backward=bw,relative_gap=gap))
   doses=[];control=None
   if n==16 and eta==.5:
    tangent=points[1]['forward']['K_tau']
    for dose in [1e-3,5e-4,2.5e-4]:
     r=base.positive_dose(.3540127993818848,dose);r['relative_tangent_bias']=abs(r['K_tau_forward_difference']/tangent-1);doses.append(r)
    assert doses[-1]['relative_tangent_bias']<doses[0]['relative_tangent_bias']
    control=base.probe(.3540127993818848,memory=False)
    assert abs(control['charge_identity_residual'])>1e-10,'NEGATIVE_CONTROL_MUST_BREAK_PHOTON_CLOSURE'
   rows.append(dict(eta=eta,auxiliary_midpoints_per_cell=n,quadrature_budget=budget,queries=points,positive_doses=doses,local_opacity_only_negative_control=control,nominal_weight_energy_only=True))
 return dict(status='DIAGNOSTIC_ONLY_NEW_ETA_SURROGATES',rows=rows,full_physical_continuous_source_proof=False,old_nominal_suite_reruns=0,unique_nonlinear_trajectories=7,backgrounds=4,finite_dose_trajectories=3,full_forward_probes=12,background_adjoints=4,arbitrary_birth_adjoint_integrals=12,negative_controls=1)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();r=run()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(r['status'],'max_forward_backward_gap',max(q['relative_gap'] for row in r['rows'] for q in row['queries']))
