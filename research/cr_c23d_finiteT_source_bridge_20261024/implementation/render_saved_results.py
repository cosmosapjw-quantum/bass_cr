"""Saved-output diagnostics and figure only; never reruns the EE evolution."""
import pathlib,json,csv,time,resource
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
U=pathlib.Path(__file__).resolve().parents[1];primary=U/'runs/c23d_source_ee_20261023T220714Z_v1';supp=U/'runs/c23d_source_ee_supplement_20261023T220810Z_v1'
def j(p):return json.loads(p.read_text())
def w(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
evols=[j(primary/f) for f in ['EVOLUTION_N256_DT0.005.json','EVOLUTION_N512_DT0.01.json','EVOLUTION_N512_DT0.005.json']];entropy=[]
for v in evols:
 count=v['samples'][0]['count_cm3'];vals=[x['relative_entropy_count_cm3']/count for x in v['samples']];delta=np.diff(vals);entropy.append({'N':v['N'],'delta_tau':v['delta_tau'],'initial_count_cm3':count,'per_particle_relative_entropy':vals,'tau':[x['tau'] for x in v['samples']],'max_sample_entropy_increase_per_particle':float(max(0.,max(delta))),'relative_increase_to_max1_initial':float(max(0.,max(delta))/max(1.,abs(vals[0]))),'interpretation':'saved sampled H/count, diagnostic only; original each-step count-weighted entropy checks retained'})
w(U/'mechanical/PER_PARTICLE_ENTROPY.json',{'scope':'postprocess stored trajectory entropy/count only; no new evolution','trajectories':entropy})
w(primary/'RESULT_CLARIFICATION.json',{'schema':'C23D_EXECUTION_SEMANTIC_CLARIFICATION_V1','original_result_unchanged':True,'original_new_ODE_0_meaning':'zero new cosmological/thermochemical coupled ODE campaigns; ambiguous label retained only as historical original','new_cosmological_or_coupled_physical_ODE':0,'new_linear_EE_population_ODE_trajectories_required_by_contract':3,'method':'semidiscrete fixed-Maxwellian population ODE integrated by backward Euler','supplemental_trajectory':{'run':supp.name,'actual_completed':True,'required_by_clarified_contract':False,'admission_basis':False,'reason':'Worker dispatched N256/dtau0.01 completeness supplement before root clarification arrived; preserve/charge actual observation, no further optional run'},'new_linear_EE_population_ODE_trajectories_total_observed':4,'old_scientific_suite_replays':0,'delivery_repair':'path resolution only; production physical/numerical methods unchanged; original executed scripts preserved in implementation/history/primary_20261023T220714Z/'})
rows=list(csv.DictReader((primary/'ATOMS_2.479.csv').open()));W=np.array([float(x['W_eV']) for x in rows]);drift=np.array([float(x['signed_drift_eV_s']) for x in rows]);weights=np.array([float(x['pulse_count_cm3']) for x in rows]);app=j(primary/'APPLICABILITY.json');th=app['anchor']['theta_eV'];base=evols[-1]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False});fig,ax=plt.subplots(1,3,figsize=(13.6,4.1),constrained_layout=True)
colors={'HI':'#2166ac','HeI':'#b35806','HeII':'#4d9221'}
for ch,color in colors.items():
 sel=np.array([r['channel']==ch for r in rows]);ax[0].scatter(W[sel],drift[sel],s=9,c=color,label=ch,alpha=.8)
ax[0].axhline(0,color='.4',lw=.7);ax[0].set(xlabel='Selected electron energy (eV)',ylabel='Signed EE drift (eV s$^{-1}$)',title='Real saved source, z = 2.479');ax[0].legend(frameon=False,fontsize=8)
for v in evols:ax[1].plot([s['tau'] for s in v['samples']],[s['mean_energy_eV'] for s in v['samples']],marker='o',ms=3,label=f"N={v['N']}, Δτ={v['delta_tau']}")
ax[1].axhline(1.5*th,color='.5',ls='--',lw=.8,label='continuum 3θ/2 reference');ax[1].set(xlabel='Dimensionless time τ',ylabel='Mean tagged energy (eV)',title='Prescribed bath; reflecting finite band');ax[1].legend(frameon=False,fontsize=8)
for v in entropy:ax[2].plot(v['tau'],v['per_particle_relative_entropy'],marker='o',ms=3,label=f"N={v['N']}, Δτ={v['delta_tau']}")
ax[2].set_yscale('log');ax[2].set(xlabel='Dimensionless time τ',ylabel='Relative entropy per tagged particle',title='Inherited discrete Maxwell equilibrium');fig.suptitle('C23D low-10 eV EE source pulse • fixed 10⁴ K bath • no escape',fontsize=13)
for ext in ['png','pdf']:fig.savefig(U/'figures'/('C23D_SOURCE_EE.'+ext),dpi=180)
plt.close(fig)
results=j(primary/'RESULT.json');supp_result=j(supp/'RESULT.json');w(U/'mechanical/EXECUTION_SUMMARY.json',{'primary_run':primary.name,'primary_dispatch':j(primary/'DISPATCH_COMPLETE.json'),'primary_result':results,'supplement_run':supp.name,'supplement_dispatch':j(supp/'DISPATCH_COMPLETE.json'),'supplement_measurements':supp_result,'supplement_admission_basis':False,'worker_cpu_total_s':results['cpu_s']+supp_result['cpu_s'],'worker_wall_total_s':results['wall_s']+supp_result['wall_s'],'dispatch_wall_total_s':j(primary/'DISPATCH_COMPLETE.json')['dispatch_wall_s']+j(supp/'DISPATCH_COMPLETE.json')['dispatch_wall_s'],'inherited_spend':None,'remaining':None,'currency':None,'requested_model':'gpt-6.1-sol','observed_model':'UNOBSERVED','EXECUTION':'PRIMARY_TARGETED_PASS_PENDING_INDEPENDENT_REVIEW; SUPPLEMENTAL_NOT_REQUIRED_OBSERVATION','PUBLICATION':'NOT_ATTEMPTED','BACKUP':'NOT_ATTEMPTED','DAG':'C23D_SCOPED_RESULT_CANDIDATE; FULL_STOPPING_PARTIAL_OPEN'})
