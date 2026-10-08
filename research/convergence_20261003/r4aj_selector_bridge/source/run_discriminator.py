"""One new saved-matrix/reference discriminator; never invokes atomic solvers."""
from pathlib import Path
from fractions import Fraction as F
import os,json,hashlib,time,platform,resource
import numpy as np
from scipy.linalg import eigh,expm
from bridge import *
from frames import span_projector

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=Path(__file__).resolve().parents[1]
 contract=json.loads((root/'contracts/LIGHT_EXECUTION_CONTRACT.json').read_text())
 lockfile=root/'INPUT_LOCK.json'
 if sha(lockfile)!=contract['input_lock_sha256']:raise ContractError('input manifest binding')
 for name,h in json.loads(lockfile.read_text())['files'].items():
  if sha(root/name)!=h:raise ContractError('input bytes changed: '+name)
 out=root/contract['result_directory'];out.mkdir(parents=True,exist_ok=False)
 reservation={'contract_sha256':sha(root/'contracts/LIGHT_EXECUTION_CONTRACT.json'),'source_sha256':{p:sha(root/p) for p in contract['source_paths']},'python':platform.python_version(),'numpy':np.__version__,'attempt':1,'atomic_evaluations':0}
 (out/'RESERVATION.json').write_text(json.dumps(reservation,indent=2)+'\n')
 started=time.monotonic()
 with np.load(root/'inputs/BASS_CR_R4AB_INTRINSIC.npz',allow_pickle=False) as raw:
  S,H=raw['S'],raw['H0']
 cert=stored_ground_gap(S.tolist(),H.tolist(),contract['alpha_Eh'],contract['beta_Eh'])
 meta=json.loads((root/'inputs/BASS_CR_R4AG_CANDIDATE.json').read_text())
 registry=json.loads((root/'inputs/BASS_CR_R4AG_NODE_REGISTRY.json').read_text())
 selector=select_channels(meta,registry)
 ref=doubled_reference_discriminator(cert)
 eig=eigh(H,S,eigvals_only=True)
 # Constant, exactly declared rational 3x3 model: two resonant retained states.
 B=F(1,1000);k=F(1,4);T=F(6);G=F(7,4)
 hd=np.array([[0,float(k),0],[float(k),0,0],[0,0,2]],float)
 hf=hd.copy();hf[0,2]=hf[2,0]=float(B)
 u=expm(-1j*hf*float(T));ud=expm(-1j*hd*float(T))
 bound=clustered_action_bound(BlockBounds(G,B,0,0,T,1,'R4AJ_CONSTANT_3X3_FIXTURE'))
 diff=float(np.linalg.norm(u-ud,2));p=float(abs((u@np.array([1,0,0]))[1])**2)
 assert diff<=float(F(bound['state_distance_upper']))+1e-13
 assert p>.9
 synthetic={'profile':'SYNTHETIC_CONSTANT_3X3_NOT_ATOMIC','duration_ta':str(T),'internal_kappa_Eh':str(k),'external_coupling_Eh':str(B),'ordered_gap_Eh':str(G),'conditional_bound':bound,'unitary_operator_difference':diff,'projectile_population_full':p,'projectile_population_reference':float(abs(ud[1,0])**2),'out_of_cluster_population':float(abs(u[2,0])**2),'purpose':'small eliminated-space error does not bound retained resonant transfer'}
 overlapS=np.array([[1,.3,0],[.3,1,0],[0,0,1.]])
 j=np.eye(3)[:,:2];pr=span_projector(overlapS,j)
 naive=span_projector(overlapS,j[:,:1])+span_projector(overlapS,j[:,1:])
 result={'schema':'R4AJ_LOCAL_DISCRIMINATOR_RESULT_V1','status':'SELECTOR_AND_REFERENCE_RESONANCE_DISCRIMINATED','candidate':meta['identity'],'semantic_selector':selector,'stored_matrix_certificate':cert,'reference_cluster':ref,'diagnostic_eigenvalues_Eh':eig.tolist(),'diagnostic_gap_Eh':float(eig[1]-eig[0]),'diagnostic_not_interval_or_physical':True,'old_rank5_to_rank1_projector_distance':str(exact_projector_rank_distance(1,5,18)),'synthetic':synthetic,'nonorthogonal_fixture':{'projector_defect':float(np.linalg.norm(pr@pr-pr)),'naive_sum_defect':float(np.linalg.norm(naive@naive-naive))},'physical_bridge':probability_bridge_total(None,None,None,None),'old_raw_bridge_504_54_not_recomputed':True,'no_original_scientific_gate_closed':True,'external_m64_status':'NOT_RUN','new_atomic_integrals':0,'historical_scientific_tests_replayed':0,'wall_seconds':time.monotonic()-started,'maxRSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 (out/'COMPLETED.json').write_text(json.dumps({'result_sha256':sha(out/'RESULT.json'),'reservation_sha256':sha(out/'RESERVATION.json'),'scope':'new saved-matrix and synthetic analysis only'},indent=2)+'\n')
 print(json.dumps({'gap_lower':cert['gap_lower'],'mapping_upper':float(F(cert['raw_trial_to_stored_ground_projector_upper'])),'synthetic':synthetic,'wall_seconds':result['wall_seconds']},indent=2))
if __name__=='__main__':main()
