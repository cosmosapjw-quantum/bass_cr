"""Single bounded CPU0 worker; raw C23D observables and measured checks."""
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[name]='1'
import sys,pathlib,json,time,resource,math,csv,copy,hashlib
import numpy as np
from scipy.linalg import solve_banded
from scipy.constants import e,m_e,c
from source_ee_bridge import anchor,read_source,load_provider,project,mfpt_dimensionless,CSV,PROVIDER,ROOT,validate

def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def evolve(W,pulse,th,rate,mod,n,dt):
 E=np.geomspace(min(1e-6*th,float(W.min())/2),40*th,n);N,projection=project(W,pulse,E);N0=N.copy();model=mod.MaxwellianCoulomb(th,2*th*rate,th,20.,False);Q,pi,conductance=mod.reversible_generator(E,model);Q=Q/rate;co=conductance/rate
 band=np.zeros((3,n));band[0,1:]=-dt*np.diag(Q,1);band[1]=1-dt*np.diag(Q);band[2,:-1]=-dt*np.diag(Q,-1)
 count=N.sum();initial_energy=float(E@N);entropy0=float(np.sum(np.where(N>0,N*np.log(np.maximum(N,1e-300)/(count*pi)),0)));samples=[];checks={'max_count_relative_drift':0.,'minimum_population':float(N.min()),'max_entropy_increase':0.,'max_opposite_energy_residual':0.,'max_common_face_residual':0.,'projection':projection};previous_entropy=entropy0
 targets={round(t/dt):t for t in [0.,.1,1.,5.,20.]}
 for step in range(round(20/dt)+1):
  if step in targets:
   J=co*(N[:-1]/pi[:-1]-N[1:]/pi[1:]);rhs=np.r_[-J[0],J[:-1]-J[1:],J[-1]];physical_rhs=rhs*rate;test_rate=float(E@physical_rhs);bath=mod.bath_energy_rate(E,physical_rhs);moment_scale=float(np.sum(np.abs(E*physical_rhs)));opposite=abs(test_rate+bath)/max(moment_scale,1e-300);checks['max_opposite_energy_residual']=max(checks['max_opposite_energy_residual'],opposite)
   entropy=float(np.sum(np.where(N>0,N*np.log(np.maximum(N,1e-300)/(count*pi)),0)));entry={'tau':targets[step],'time_s':targets[step]/rate,'count_cm3':float(N.sum()),'energy_eV_cm3':float(E@N),'mean_energy_eV':float(E@N/N.sum()),'relative_entropy_count_cm3':entropy,'test_energy_rate_eV_cm3_s':test_rate,'background_only_bath_heat_rate_eV_cm3_s':bath,'opposite_bath_energy_change_eV_cm3':initial_energy-float(E@N),'partitions':[]}
   for chi in [1.5,3.]:
    faces=(E[:-1]+E[1:])/2;edge=int(np.argmin(abs(faces-chi*th)));q=float(faces[edge]);current=float(J[edge]*rate);I=float((E[edge+1]-q)*current+np.dot(np.diff(E)[edge+1:],J[edge+1:])*rate);ledger=mod.moving_interface(current,q,I,0.,0.);tail=float(E[edge+1:]@physical_rhs[edge+1:]);tail_count=float(physical_rhs[edge+1:].sum());scale=max(abs(q*current)+abs(I),float(np.sum(np.abs(E[edge+1:]*physical_rhs[edge+1:]))),1e-300);res=abs(tail-ledger['tail_energy'])/scale;checks['max_common_face_residual']=max(checks['max_common_face_residual'],res)
    entry['partitions'].append({'chi':chi,'requested_q_eV':chi*th,'q_h_eV':q,'edge_index':edge,'tail_count_cm3':float(N[edge+1:].sum()),'core_count_cm3':float(N[:edge+1].sum()),'tail_energy_eV_cm3':float(E[edge+1:]@N[edge+1:]),'core_energy_eV_cm3':float(E[:edge+1]@N[:edge+1]),'J_edge_cm3_s':current,'I_h_eV_cm3_s':I,'reservoir_interpretation':'background bath plus low-energy tagged core','same_current_ledger':ledger,'direct_tail_count_rate':tail_count,'common_face_energy_relative_residual':res})
   samples.append(entry)
  if step==round(20/dt):break
  N=solve_banded((1,1),band,N,overwrite_ab=False,overwrite_b=False,check_finite=False)
  if np.any(N<0):raise RuntimeError('negative populations: no clipping')
  ent=float(np.sum(np.where(N>0,N*np.log(np.maximum(N,1e-300)/(count*pi)),0)));checks['max_entropy_increase']=max(checks['max_entropy_increase'],(ent-previous_entropy)/max(1.,abs(entropy0)));previous_entropy=ent;checks['max_count_relative_drift']=max(checks['max_count_relative_drift'],abs(N.sum()-count)/count);checks['minimum_population']=min(checks['minimum_population'],float(N.min()))
 return {'centres_eV':E.tolist(),'initial_counts_cm3':N0.tolist(),'final_counts_cm3':N.tolist(),'equilibrium_pi':pi.tolist(),'N':n,'delta_tau':dt,'samples':samples,'checks':checks,'finite_band':'reflecting endpoints; midpoint equilibrium normalized on chosen finite geometric band'}

def main(run):
 start=time.perf_counter();cpu=time.process_time();inp=json.loads((ROOT/'cr_stopping_loop_20261024/inputs/CASE.json').read_text());validate(inp);a=anchor(inp);mod=load_provider();rows=read_source(inp);th=a['theta_eV'];rate=a['tau_per_s'];model=mod.MaxwellianCoulomb(th,a['loss_anchor_eV_s'],th,20.,False);summaries=[];selected={}
 write(run/'SOURCE_IDENTITY.json',{'input_csv':{'path':str(CSV),'bytes':CSV.stat().st_size,'sha256':hashlib.sha256(CSV.read_bytes()).hexdigest()},'provider':{'path':str(PROVIDER),'bytes':PROVIDER.stat().st_size,'sha256':hashlib.sha256(PROVIDER.read_bytes()).hexdigest()},'new_sources':[{ 'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in pathlib.Path(__file__).parent.glob('*.py')],'requested_model':inp['requested_model'],'observed_model':inp['observed_model'],'old_suites_replayed':0})
 for z in inp['redshifts']:
  rr=[x for x in rows if x['redshift']==z];W=np.array([float(x['kinetic_eV']) for x in rr]);q=np.array([float(x['number_weight_per_target_s']) for x in rr]);density=np.array([inp['density_cm3'][x['channel']] for x in rr]);source=density*q;sel=(W>0)&(W<10);pulse=source[sel]*inp['exposure_s'];selected[z]=(W[sel],pulse);drift,D,_,_=model.coefficients(W[sel]);parent={p:inp['exposure_s']*sum(float(x['number_weight_per_target_s']) for x in rr if x['channel']==p) for p in ['HI','HeI','HeII']};totalN=float(source.sum());totalU=float(source@W);nratio=float(pulse.sum()/inp['n_e_thermal_cm3']);uratio=float((pulse@W[sel])/(1.5*inp['n_e_thermal_cm3']*th));s={'redshift':z,'all_atoms':len(rr),'selected_atoms':int(sel.sum()),'source_all_count_cm3_s':totalN,'source_all_energy_eV_cm3_s':totalU,'selected_count_source_cm3_s':float(source[sel].sum()),'selected_energy_source_eV_cm3_s':float(source[sel]@W[sel]),'selected_count_fraction':float(source[sel].sum()/totalN),'selected_energy_fraction':float((source[sel]@W[sel])/totalU),'excluded_count_cm3_s':float(source[~sel].sum()),'excluded_energy_eV_cm3_s':float(source[~sel]@W[~sel]),'endpoint_0_count_cm3_s':float(source[W==0].sum()),'endpoint_10_count_cm3_s':float(source[W==10].sum()),'pulse_count_cm3':float(pulse.sum()),'pulse_energy_eV_cm3':float(pulse@W[sel]),'count_diluteness_ratio':nratio,'energy_diluteness_ratio':uratio,'applicability_pass':nratio<=1e-3 and uratio<=1e-3,'occupied_parent_depletion_all_atoms':parent,'selected_Emax_over_mec2':float(W[sel].max()*e/(m_e*c*c)),'all_source_Emax_over_mec2':float(W.max()*e/(m_e*c*c)),'upward_drift_count_fraction':float(pulse[drift>0].sum()/pulse.sum()),'downward_drift_count_fraction':float(pulse[drift<0].sum()/pulse.sum()),'upward_drift_energy_fraction':float((pulse[drift>0]@W[sel][drift>0])/(pulse@W[sel])),'downward_drift_energy_fraction':float((pulse[drift<0]@W[sel][drift<0])/(pulse@W[sel])),'source_weighted_drift_eV_cm3_s2':float(source[sel]@drift),'pulse_test_initial_energy_rate_eV_cm3_s':float(pulse@drift),'pulse_bath_initial_heat_rate_eV_cm3_s':-float(pulse@drift)};summaries.append(s)
  with (run/('ATOMS_'+z+'.csv')).open('w') as f:
   writer=csv.writer(f);writer.writerow(['channel','W_eV','source_count_cm3_s','pulse_count_cm3','signed_drift_eV_s','diffusion_eV2_s']);writer.writerows(zip(np.array([x['channel'] for x in rr])[sel],W[sel],source[sel],pulse,drift,D))
 write(run/'APPLICABILITY.json',{'anchor':a,'epochs':summaries});print(json.dumps({'phase':'APPLICABILITY','epochs':summaries,'anchor':a}),flush=True)
 if not all(s['applicability_pass'] for s in summaries):raise RuntimeError('Frozen-bath diluteness screen failed; preserve measurements for root')
 mfpts=[]
 # Same bath shape: evaluate each unique selected energy once for each chi,R.
 allW=np.unique(np.concatenate([v[0] for v in selected.values()]));mf_cache={}
 for chi in [1.5,3.]:
  for R in [40.,80.]:mf_cache[chi,R]=mfpt_dimensionless(allW/th,chi,R,mod)
 for z,(W,pulse) in selected.items():
  idx=np.searchsorted(allW,W)
  for chi in [1.5,3.]:
   active=W>chi*th;records={}
   for R in [40.,80.]:
    vals,err=mf_cache[chi,R];T=vals[idx]/rate;records[str(int(R))]={'active_weighted_mean_s':float(pulse[active]@T[active]/pulse[active].sum()),'all_selected_weighted_mean_s':float(pulse@T/pulse.sum()),'minimum_s':float(T.min()),'maximum_s':float(T.max()),'active_minimum_s':float(T[active].min()),'quadrature_error_max_dimensionless':err,'active_fraction':float(pulse[active].sum()/pulse.sum())}
   delta=abs(records['80']['active_weighted_mean_s']-records['40']['active_weighted_mean_s'])/records['80']['active_weighted_mean_s'];mfpts.append({'redshift':z,'chi':chi,'upper_boundaries_theta':records,'upper_truncation_active_mean_relative':delta,'mean_to_prescribed_evolution_1e10s':records['40']['active_weighted_mean_s']/1e10,'observable':'first entry only; initial W<=q time0; no permanent assimilation time'})
 write(run/'MFPT.json',mfpts)
 evol=[]
 for n,dt in [(256,.005),(512,.01),(512,.005)]:
  v=evolve(*selected['2.479'],th,rate,mod,n,dt);evol.append(v);write(run/(f'EVOLUTION_N{n}_DT{dt}.json'),v)
 baseline=evol[2];spatial=max(abs(x['mean_energy_eV']-y['mean_energy_eV'])/abs(y['mean_energy_eV']) for x,y in zip(evol[0]['samples'][1:],baseline['samples'][1:]));temporal=max(abs(x['mean_energy_eV']-y['mean_energy_eV'])/abs(y['mean_energy_eV']) for x,y in zip(evol[1]['samples'][1:],baseline['samples'][1:]));checks={'spatial_mean_energy_relative':spatial,'temporal_mean_energy_relative':temporal,'MFPT_upper_truncation_max':max(v['upper_truncation_active_mean_relative'] for v in mfpts),'projection_pass':all(max(x['checks']['projection']['count_relative_residual'],x['checks']['projection']['energy_relative_residual'])<=1e-12 and x['checks']['projection']['minimum_weight']>=0 for x in evol),'count_pass':all(x['checks']['max_count_relative_drift']<=1e-9 for x in evol),'energy_current_pass':all(max(x['checks']['max_opposite_energy_residual'],x['checks']['max_common_face_residual'])<=1e-11 for x in evol),'entropy_pass':all(x['checks']['max_entropy_increase']<=1e-11 for x in evol),'nonnegative_pass':all(x['checks']['minimum_population']>=0 for x in evol)}
 checks['spatial_pass']=spatial<=5e-3;checks['temporal_pass']=temporal<=3e-3;checks['MFPT_truncation_pass']=checks['MFPT_upper_truncation_max']<=1e-8
 # Meaningful adapter guards, changing one declared physical field at a time.
 guards=[]
 for key,value in [('frame','other'),('time_unit','coordinate_seconds'),('rate_unit','other'),('redshifts',['0']),('temperature_K',0),('log_lambda',0),('n_e_thermal_cm3',-1),('density_cm3',{'HI':.9})]:
  bad=copy.deepcopy(inp);bad[key]=value
  try:validate(bad);guards.append({'field':key,'rejected':False})
  except ValueError as exc:guards.append({'field':key,'rejected':True,'reason':str(exc)})
 bad=copy.deepcopy(inp);bad.pop('n_e_thermal_cm3')
 try:validate(bad);guards.append({'field':'missing_n_e_thermal','rejected':False})
 except ValueError as exc:guards.append({'field':'missing_n_e_thermal','rejected':True,'reason':str(exc)})
 write(run/'GUARDS.json',guards);checks['guards_pass']=all(v['rejected'] for v in guards);passed=all(v for k,v in checks.items() if k.endswith('_pass'));usage=resource.getrusage(resource.RUSAGE_SELF);result={'status':'PASS_TARGETED_PENDING_INDEPENDENT_REVIEW' if passed else 'FAILED_FROZEN_CRITERIA','checks':checks,'wall_s':time.perf_counter()-start,'cpu_s':time.process_time()-cpu,'maxrss_KiB':usage.ru_maxrss,'worker_cpu_index':0,'native_threads':1,'new_ODE':0,'new_source_evolution':'backward Euler discrete EE linear population evolution; new C23B pulse','old_suites_replayed':0,'global_error_bound':None,'full_physical_stopping':None};write(run/'RESULT.json',result);print(json.dumps(result),flush=True)
 if not passed:return 2
 return 0
if __name__=='__main__':
 run=pathlib.Path(sys.argv[1]);resource.setrlimit(resource.RLIMIT_CPU,(120,121));os.sched_setaffinity(0,{0})
 try:sys.exit(main(run))
 except Exception as exc:
  write(run/'FAILURE.json',{'type':type(exc).__name__,'message':str(exc)});raise
