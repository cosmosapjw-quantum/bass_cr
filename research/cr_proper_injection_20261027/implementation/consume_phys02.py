"""Consume existing PHYS02 discrete source and its independently recorded time law.

No provider, source quadrature, projection, generator or transport solve is run.
"""
from pathlib import Path
import hashlib,json,math,os,resource,sys
import numpy as np
from ports import (EV_J, ContractError, build_source_event, digest,
                   integrate_history, attach_rr_return, claim_injection)

UNIT=Path(__file__).resolve().parents[1];REPO=UNIT.parents[1]
RAW=REPO/'research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01'
NPZ_SHA='7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc'
NATIVE_SHA='07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609'
ENERGY_SHA='6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292'
REV='ec463db0c7e5c7fb5070796071c926caa4db6445'
STATE='PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED'
FRAME='prescribed_gas_rest_frame_scalar'
MAPPING='CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4'

def write(path,data):
 with path.open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')

def main():
 out=Path(sys.argv[1]);assert out.is_dir()
 raw=RAW/'SPECTRUM_fullBED_9600.npz';b=raw.read_bytes();assert hashlib.sha256(b).hexdigest()==NPZ_SHA
 with np.load(raw,allow_pickle=False) as f:
  E=f['energy_eV'].copy();B=f['source_vectors'].copy();scale=float(f['physical_energy_scale_eV_m3']);times=f['time_s'].tolist();tags=f['birth_tags'].tolist()
 assert E.shape==(9600,) and B.shape==(9611,2)
 assert hashlib.sha256(E.tobytes()).hexdigest()==ENERGY_SHA
 assert hashlib.sha256(B.tobytes()).hexdigest()==NATIVE_SHA
 assert times==[0.0,1e10] and scale==1.1242596728743301e-13
 assert np.all(np.isfinite(E)) and np.all(E>0) and np.all(np.isfinite(B)) and np.all(B>=0)
 assert np.all(B[9600:9605,:]==0) and np.all(B[9606:9608,:]==0)
 T=times[-1];S=scale/(T*T)
 defn={'source_model':'PHYS02_Qe_tA_leading_local','state':STATE,'frame':FRAME,'mapping':MAPPING,'energy_scale_eV_m3':scale,'known_time_s':times,'native_secondary_eV':[.1,900.0],'proton_collision_eV':[1e6,4e6],'normalization':'proper_volume_clock_target_angle_already_included'}
 physical_hash=digest(defn)
 records=[];rows=[];source_checks=[]
 windows=[[0.0,T],[0.0,T/2],[T/2,T],[T/3,2*T/3],[T*(1-1e-6),T],[T,T]]
 for col,tag,support in [(0,tags[0],[.1,10.0]),(1,tags[1],[10.0,900.0]),(None,'selected_total',[.1,900.0])]:
  weights=[float(B[i,col]) if col is not None else math.fsum([float(B[i,0]),float(B[i,1])]) for i in range(9611)]
  atoms=[]
  for i,(en,be) in enumerate(zip(E,weights[:9600])):
   if be:
    atoms.append({'energy_eV':float(en),'number_coefficients':[0.0,S*be/float(en)],'stored_node_index':i})
  cutoffN,cutoffE=weights[9608],weights[9605]
  if cutoffN:
   assert abs(cutoffE-.1*cutoffN)<=2e-13*abs(cutoffE)
   atoms.append({'energy_eV':.1,'number_coefficients':[0.0,S*cutoffN],'stored_node_index':'cutoff_boundary'})
  AN=math.fsum(a['number_coefficients'][1] for a in atoms)
  AE=S*math.fsum(weights[:9600]+[cutoffE])
  event=build_source_event(physical_definition_sha256=physical_hash,energy_array_sha256=ENERGY_SHA,source_array_sha256=NATIVE_SHA,family_native_birth_support_eV=[.1,900.0],native_birth_support_eV=support,clock_origin_s=0.0)
  source={'schema':'CR_PROPER_SOURCE_V1','source':{'repository':'cosmosapjw-quantum/bass_cr','revision':REV,'payload_sha256':NPZ_SHA,'evidence_kind':'stored_physical'},'particle':{'kind':'electron','isotope':'e-','state':'PHYS02_direct_secondary_birth','energy_coordinate':'kinetic_eV'},'medium':{'state_id':STATE,'frame':FRAME,'temperature_K':100.0,'proper_volume_mode':'fixed','proper_volume_m3':None},'isotope_mapping':MAPPING,'support_eV':support,'source_event':event,'representation':'atomic_bins','normalization':{'clock_measure':'proper_s','volume_measure':'proper_m3','d_native_clock_d_proper_s':1.0,'d_native_volume_d_proper_m3':1.0,'target_density_mode':'already_included','target_density_m3':None,'applied_tokens':[]},'history_boundary':'unknown_outside_recorded_segments','history':[{'start_s':0.0,'stop_s':T,'number_coefficients':[0.0,AN],'energy_coefficients_eV':[0.0,AE],'bins':atoms}]}
  records.append({'tag':tag,'source':source})
  for window in windows:
   r=integrate_history(source,window);spectrum=r.pop('spectrum')
   r['spectrum_payload']={'representation':'actual_stored_source_atoms_time_integrated','atoms':len(spectrum),'sha256':digest(spectrum),'source_record_tag':tag,'source_file':'ACTUAL_SOURCE_RECORDS.json','no_moment_inversion':True}
   mismatch={'state_id':'PR107_T10000K_frozen','temperature_K':10000.0,'frame':'bath_frame_rest_target','isotope_mapping':MAPPING,'revision':'4e72c89b714431eb4c6ae07def777bbf72a5ae4c','payload_sha256':None,'method':'saved_resolvent_eventual','return_horizon':'eventual'}
   r['RR_link_attempt']=attach_rr_return(r,mismatch)
   assert 'DONOR_RECIPIENT_STATE_MISMATCH' in r['RR_link_attempt']['reasons']
   assert r['nb_m3'] is None and r['native25'] is None and r['rr_return'] is None and r['retained_photon_port'] is None
   r['tag']=tag;r['window_s']=window;rows.append(r)
  source_checks.append({'tag':tag,'active_atoms':len(atoms)-(1 if cutoffN else 0),'cutoff_number_weight':cutoffN,'cutoff_energy_weight':cutoffE,'diagnostic_low_cross_excluded':[weights[9609],weights[9610]],'A_number_m3_s2':AN,'A_energy_eV_m3_s2':AE})
 sourcefile=out/'ACTUAL_SOURCE_RECORDS.json';write(sourcefile,records)
 # Actual duplicate-family guard: low+high valid, total cannot be added again.
 registry=[];claim_injection(rows[0],registry);claim_injection(rows[6],registry)
 duplicate=False
 try:claim_injection(rows[12],registry)
 except ContractError:duplicate=True
 assert duplicate
 result={'schema':'CR_PROPER_ACTUAL_RESULTS_V1','source_model':'actual_saved_PHYS02_leading_local_not_observed_cosmology','source_npz_sha256':NPZ_SHA,'source_records_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'physical_definition':defn,'physical_definition_sha256':physical_hash,'common_scale_eV_m3_s2':S,'source_checks':source_checks,'rows':rows,'actual_rows':len(rows),'source_partition_duplicate_refused':duplicate,'actual_RR_admitted':False,'actual_nb_m3':None,'actual_native25':None,'physical_heating_complete':False,'global_physical_error':None,'global_physical_completion':None,'old_science_replays':0,'new_source_quadrature':0,'new_projection':0,'new_ODE':0,'environment':{'python':sys.version,'numpy':np.__version__,'affinity':sorted(os.sched_getaffinity(0)),'RLIMIT_AS':list(resource.getrlimit(resource.RLIMIT_AS)),'RLIMIT_CPU':list(resource.getrlimit(resource.RLIMIT_CPU)),'native_threads_env':{k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']}}}
 write(out/'RESULT.json',result)
 print(json.dumps({'rows':len(rows),'source_checks':source_checks,'result':str(out/'RESULT.json'),'actual_rr_admitted':False,'native25':None}))

if __name__=='__main__':main()
