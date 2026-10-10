# SPDX-License-Identifier: GPL-3.0-only
"""Frozen scalar diagnostic and plot assembly. No Cascade/G/evolve construction."""
import os
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):os.environ[k]='1'
from pathlib import Path
import hashlib,json,sys,time,traceback,platform,signal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/diagnostics'
INPUTS=[ROOT/'state/DIAGNOSTIC_CONTRACT.json',ROOT/'state/SCIENTIFIC_CONTRACT.json',ROOT/'evidence/runs/R001/NUMERICAL_RESULT.json',ROOT/'evidence/runs/R001/SPECTRUM_fullBED_4800.npz',ROOT.parent/'cr_phys02b_20261010/evidence/runs/R002/NUMERICAL_RESULT.json',ROOT.parent/'cr_phys02b_20261010/evidence/runs/R002/CANONICAL_SPECTRUM.npz',ROOT/'src/coherent_bed.py',Path(__file__)]
def ident(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest={'state':'FROZEN_BEFORE_DIAGNOSTIC_COMPUTATION','start_utc':now(),'command':sys.argv,'cwd':str(Path.cwd()),'python':sys.version,'thread_environment':{k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS')},'inputs_and_code':{str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):ident(p) for p in INPUTS}}
 save(OUT/'EXECUTION_MANIFEST.json',manifest)
 start=time.monotonic();code=1;receipt={'start_utc':now(),'transport_calls':0,'generator_constructions':0}
 try:
  import numpy as np
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from threadpoolctl import threadpool_info
  sys.path.insert(0,str(ROOT/'src'));import coherent_bed as bed
  cc=bed.parent;dc=json.loads(INPUTS[0].read_text());new=json.loads(INPUTS[2].read_text());legacy=json.loads(INPUTS[4].read_text())
  if new['status']!='PASS_SCOPED' or new['actual_exit']!=0:raise RuntimeError('NEW_RESULT_NOT_ACTUAL_PASS')
  if ident(INPUTS[5])!={k:dc['legacy_spectrum'][k] for k in ('bytes','sha256')}:raise ValueError('LEGACY_SPECTRUM_PIN_MISMATCH')
  if any(x['num_threads']!=1 for x in threadpool_info()):raise RuntimeError('THREAD_ADMISSION_FAILED')
  nr=next(r for r in new['grid_results'] if r['cells']==[1600,3200]);lr=next(r for r in legacy['grid_results'] if r['cells']==[1600,3200])
  n=np.load(INPUTS[3]);l=np.load(INPUTS[5]);E=n['energy_eV'];scale=float(n['physical_energy_scale_eV_m3'])
  if not np.array_equal(E,l['energy_eV']) or scale!=float(l['physical_energy_scale_eV_m3']):raise ValueError('ENERGY_OR_PHYSICAL_SCALE_MISMATCH')
  heat={};checks=[]
  for label,z,row in [('fullBED',n,nr),('legacy',l,lr)]:
   final=z['state_normalized'][-1,:len(E),:];b=cc.stopping_eV_s(E,quantum_constant=0.)
   h={}
   for i,tag in enumerate(dc['tag_definition']):
    h[tag]={mask:float(scale*cc.EV_J*np.sum(b[sel]/E[sel]*final[sel,i])) for mask,sel in [('all',np.ones(len(E),dtype=bool)),('low',E<=10),('high',E>10)]}
    stored=row['final']['components'][tag]['heat_power_J_m3_s'];err=abs(h[tag]['all']-stored)/abs(stored)
    checks.append({'id':label+'_'+tag+'_HEAT_LEDGER_IDENTITY','relative_residual':err,'tolerance':1e-11,'status':'PASS_SCOPED' if err<1e-11 else 'FAIL'})
   direct=h['direct_0p1_10']['all'];h['ratios']={'high_birth_all_over_direct_low_birth_all':h['direct_10_900']['all']/direct,'high_birth_low_mask_over_direct_low_birth_all':h['direct_10_900']['low']/direct};heat[label]=h
  heat['new_vs_legacy_percent']={k:100*(heat['fullBED']['ratios'][k]/heat['legacy']['ratios'][k]-1) for k in heat['fullBED']['ratios']}
  fine={};fractions={}
  for tag in nr['final']['components']:
   fine[tag]={};fractions[tag]={}
   denominator=nr['final']['components']['selected_total']['injected_energy_J_m3']
   for k,v in nr['final']['components'][tag].items():
    old=lr['final']['components'][tag][k];fine[tag][k]={'fullBED':v,'legacy':old,'delta':v-old,'percent_of_legacy':100*(v-old)/abs(old) if old else None}
    if k.endswith('_J_m3'):fractions[tag][k]={'fullBED_fraction_of_selected_injected_energy':v/denominator,'legacy_fraction_of_selected_injected_energy':old/lr['final']['components']['selected_total']['injected_energy_J_m3'],'denominator_fullBED_selected_Uin_J_m3':denominator}
  sigma={}
  oldatomic=cc.AtomicData()
  for sp in ('HI','HeI'):
   atom=bed.Ionization(sp);energy=np.geomspace(1.001*atom.B_eV,900,400);snew=atom.total_m2(energy);sold=oldatomic.ionization[sp].total_m2(energy)
   sigma[sp]={'incident_energy_eV':energy.tolist(),'fullBED_sigma_m2':snew.tolist(),'legacy_sigma_m2':sold.tolist(),'relative_percent':(100*(snew/sold-1)).tolist()}
  keys=['heat_power','heat','binding_HI','binding_HeI','ionizations_HI','ionizations_HeI','low_cross_energy','low_cross_number','cutoff_energy','cutoff_number'];paired=[next(x for x in new['paired_deltas'] if x['group']=='parent_output_vector_normalized' and x['observable']==k) for k in keys]
  plotdata={'sigma':sigma,'paired_observables':paired,'annotation':dc['figure']['annotation'],'interpretation':'Physical representation comparison; no errorbars or certified physical error'};save(OUT/'PLOT_DATA.json',plotdata)
  tables={'schema':'cr-phys02c-report-tables.v1','selected_energy_fractions':fractions,'fine_exact_values_and_deltas':fine,'fine_normalized_output_vector':{k:{'fullBED':v,'legacy':lr['metrics_normalized'][k],'delta':v-lr['metrics_normalized'][k]} for k,v in nr['metrics_normalized'].items()},'endpoint_Coulomb_heat_power_J_m3_s':heat,'diagnostic_checks':checks,'paired_deltas_all':new['paired_deltas'],'inherited_gates':json.loads(INPUTS[1].read_text())['inherited_gates'],'interpretation':'Direct-low differences at roundoff are not physical effects. Fractions use selected injected energy, not total direct source energy.'};save(ROOT/'REPORT_TABLES.json',tables);save(OUT/'HEAT_DIAGNOSTIC.json',{'heat':heat,'checks':checks})
  fig,axes=plt.subplots(1,2,figsize=(13,6.8),gridspec_kw={'width_ratios':[1.05,1.3]})
  for sp,color in [('HI','#1864ab'),('HeI','#c05621')]:axes[0].plot(sigma[sp]['incident_energy_eV'],sigma[sp]['relative_percent'],label='H I' if sp=='HI' else 'He I',color=color,lw=2)
  axes[0].set_xscale('log');axes[0].axhline(0,color='0.6',lw=.8);axes[0].set_xlabel('Incident electron energy (eV)');axes[0].set_ylabel('100 × (σ full BED / σ legacy − 1) (%)');axes[0].set_title('(a) Ionization total representation');axes[0].legend(frameon=False);axes[0].grid(alpha=.2)
  y=np.arange(len(keys));labels=['Heat power','Accumulated heat','H I binding','He I binding','H I ionizations','He I ionizations','Low crossing energy','Low crossing number','Cutoff energy','Cutoff number']
  axes[1].barh(y-.17,[x['percent_of_legacy_coarse'] for x in paired],height=.30,color='#9ecae1',label='2400 nodes');axes[1].barh(y+.17,[x['percent_of_legacy_fine'] for x in paired],height=.30,color='#1864ab',label='4800 nodes');axes[1].set_yticks(y,labels);axes[1].invert_yaxis();axes[1].axvline(0,color='0.5',lw=.8);axes[1].set_xlabel('Paired model delta / matching legacy (%)');axes[1].set_title('(b) Finite-time cascade comparison');axes[1].legend(frameon=False);axes[1].grid(axis='x',alpha=.2)
  fig.subplots_adjust(left=.08,right=.98,bottom=.18,top=.90,wspace=.47);fig.text(.5,.07,'Fixed bath · selected 0.1–900 eV source · T = 10¹⁰ s\nTwo-grid changes are empirical; no physical error certificate. Inherited global gates unchanged.',ha='center',fontsize=10)
  fig.savefig(OUT/'ATOMIC_CASCADE_COMPARISON.png',dpi=180);fig.savefig(OUT/'ATOMIC_CASCADE_COMPARISON.pdf');plt.close(fig)
  receipt.update({'checks':checks,'runtime':{'numpy':np.__version__,'matplotlib':matplotlib.__version__,'threadpools':threadpool_info()},'output_identities':{str(p.relative_to(ROOT)):ident(p) for p in [ROOT/'REPORT_TABLES.json',OUT/'PLOT_DATA.json',OUT/'HEAT_DIAGNOSTIC.json',OUT/'ATOMIC_CASCADE_COMPARISON.png',OUT/'ATOMIC_CASCADE_COMPARISON.pdf']},'status':'PASS_SCOPED' if all(x['status']=='PASS_SCOPED' for x in checks) else 'FAIL'});code=0 if receipt['status']=='PASS_SCOPED' else 1
 except Exception:receipt.update({'status':'DIAGNOSTIC_FAILED','exception':traceback.format_exc()});traceback.print_exc()
 finally:receipt.update({'actual_exit':code,'end_utc':now(),'wall_seconds':time.monotonic()-start});save(OUT/'ACTUAL_EXIT.json',receipt)
 return code
if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('DIAGNOSTIC_WALL_60S')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(60);sys.exit(main())
