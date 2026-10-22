#!/usr/bin/env python3
"""Independent saved-array review. Imports no research/ODE/rate modules."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[key] = '1'
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import time
import numpy as np

ROOT = Path('/workspace/scratch/30d955d9ea43')
REPO = ROOT/'resume_c22c_20261022/recovery/restored_c22b/repository'
D = REPO/'research/cr_c22d_cold_ci_20261022'
A = D/'analysis_v1'
OUT = ROOT/'c22d_20261022/review_final'
started = dt.datetime.now(dt.timezone.utc).isoformat()
wall, cpu = time.monotonic(), time.process_time()
affinity = sorted(os.sched_getaffinity(0))
chosen = 4 if 4 in affinity else next(c for c in affinity if c not in (0,3,55))
os.sched_setaffinity(0,{chosen})
pins, checks, measures = {}, {}, {}

def data(path):
    path = Path(path)
    raw = path.read_bytes()
    pins[str(path)] = {'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
    return raw

def js(path):
    return json.loads(data(path))

def arr(path):
    with np.load(io.BytesIO(data(path)),allow_pickle=False) as z:
        return {k:z[k] for k in z.files}

def check(name,value):
    checks[name] = bool(value)

def peak(a):
    return float(np.max(np.abs(a)))

contract = js(D/'CONTRACT.json')
gates = contract['preregistered_gates']
summary = js(A/'SUMMARY.json')
freeze = js(D/'evidence/SOURCE_FREEZE.json')
for row in freeze['files']:
    raw=data(REPO/row['path'])
    check('frozen_source:'+row['path'],len(raw)==row['size_bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'])
check('executed_analyzer_identity',hashlib.sha256(data(A/'analyzer_executed_v1.py')).hexdigest()==summary['analyzer_pin']['sha256'])
artifact_manifest=js(A/'ARTIFACT_MANIFEST.json')
for row in artifact_manifest['files']:
    raw=data(row['path'])
    check('analysis_artifact:'+Path(row['path']).name,len(raw)==row['size_bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'])

histories={}
for role,runid in [('nominal','c22d_h1_ci_bdf_20261022_v1'),('reference','c22d_h1_ci_radau_20261022_v1')]:
    run=D/'runs'/runid
    inp=js(run/'INPUT.json')
    expected=contract['new_runs'][role]
    expected_cases=expected['cases'] if role=='nominal' else [expected['case']]
    check(role+':registered_input',inp['cases']==expected_cases and all(inp[k]==expected[k] for k in ('method','rtol','atol')))
    for case in inp['cases']:
        name=case['name']; key=role+':'+name; folder=run/'cases'/name
        raw=data(folder/'history.npz'); receipt=js(folder/'RECEIPT.json'); complete=js(folder/'COMPLETE.json'); meta=js(folder/'MODEL.json')
        check(key+':raw_receipt',len(raw)==receipt['history_bytes'] and hashlib.sha256(raw).hexdigest()==receipt['history_sha256']==complete['history_sha256'])
        check(key+':receipt_binding',hashlib.sha256(data(folder/'RECEIPT.json')).hexdigest()==complete['receipt_sha256'])
        saved=arr(folder/'history.npz')
        diagnostic=arr(A/(role+'_'+name+'_SAVED_DIAGNOSTICS.npz'))
        check(key+':diagnostic_grid',np.array_equal(saved['eta'],diagnostic['eta']))
        saved.update(diagnostic)
        accepted=arr(A/(role+'_'+name+'_ACCEPTED.npz'))
        check(key+':accepted_raw_binding',np.array_equal(accepted['eta'],saved['accepted_eta']) and np.array_equal(accepted['Y'],saved['accepted_Y']))
        histories[key]={'saved':saved,'accepted':accepted}
        for mesh,h in histories[key].items():
            tag=key+':'+mesh; n=len(h['eta']); reported=summary['audits'][key][mesh]
            check(tag+':recorded_gates',reported['mesh_points']==n and all(reported['checks'].values()) and reported['status']=='PASS_SCOPED')
            check(tag+':shapes',h['Y'].shape==(78,n) and h['atomic_abundance_per_Href'].shape==(21,n) and meta['solver_state_size']==75)
            labels=list(h['atomic_state_labels']); abundance=h['atomic_abundance_per_Href']
            charges=[int(label.rsplit('_',1)[1]) if '_' in label else 0 for label in labels]
            electrons=np.array([math.fsum(float(charges[i])*float(abundance[i,j]) for i in range(21)) for j in range(n)])
            atoms=np.array([math.fsum(float(abundance[i,j]) for i in range(21)) for j in range(n)])
            particles=atoms+electrons
            photons=np.array([math.fsum(float(v) for v in row) for row in h['UV_photons_per_H']])
            charge_residual=(electrons+h['recombination_count_per_H']-h['absorption_count_per_H']-h['H1_CI_events_per_H']-electrons[0])/max(float(photons[0]),1.)
            photon_residual=(photons+h['absorption_count_per_H']-photons[0])/max(float(photons[0]),1.)
            energy_keys=('thermal_energy_eV_per_H','ionization_energy_eV_per_H','UV_energy_eV_per_H','escaped_energy_eV_per_H','gas_work_eV_per_H','UV_work_eV_per_H','bath_energy_received_eV_per_H','excitation_escaped_energy_eV_per_H')
            energy=np.array([math.fsum(float(h[k][j]) for k in energy_keys) for j in range(n)])
            energy_residual=(energy-energy[0])/abs(energy[0])
            nucleus=[]
            for species in sorted({x.split('_')[0] for x in labels}):
                ids=[i for i,x in enumerate(labels) if x.split('_')[0]==species]
                conserved=np.array([math.fsum(float(abundance[i,j]) for i in ids) for j in range(n)])
                if conserved[0]==0:
                    check(tag+':zero_inventory:'+species,np.all(conserved==0))
                else:
                    nucleus.append(peak(conserved/conserved[0]-1.))
            temp=2*h['thermal_energy_eV_per_H']/(3*(1.380649e-23/1.602176634e-19)*particles)
            check(tag+':independent_energy',peak(energy_residual)<=gates['energy_relative_saved_and_accepted_max_abs'])
            check(tag+':independent_nuclei',max(nucleus)<=gates['nucleus_max_relative_residual'])
            check(tag+':independent_charge',peak(charge_residual)<=gates['charge_and_photon_absolute_normalized'])
            check(tag+':independent_photon',peak(photon_residual)<=gates['charge_and_photon_absolute_normalized'])
            check(tag+':independent_ne',peak(electrons-h['n_e_cm3']/h['nH_ref_cm3'])<2e-15)
            check(tag+':independent_T',peak(temp/h['temperature_K']-1)<2e-14)
            check(tag+':declared_face',np.all(h['Y'][meta['invariant_coordinate_indices']]==0))
            check(tag+':domain',float(min(h['temperature_K']))>gates['temperature_strict_min_K'] and float(max(h['temperature_K']))<=gates['temperature_max_K'] and float(max(h['nH_ref_cm3']))<=gates['nHref_max_cm3'])
            check(tag+':population',float(np.min(h['atomic_scaled']))>=gates['minimum_scaled_population'])
            check(tag+':UV',float(np.min(h['UV_photons_per_H']))>=gates['minimum_UV_count_per_H'])
            check(tag+':signed_radiation',peak(h['signed_Pi_r_F']-(h['signed_Pi_gamma_F']+h['signed_Pi_nu_F']))<1e-15)
            check(tag+':radiation_norm',peak(h['Pi_r_F']-abs(h['signed_Pi_r_F']))<1e-15)
            check(tag+':total_norm',peak(h['Pi_tot_F']-abs(h['signed_Pi_m_F']+h['signed_Pi_r_F']))<1e-15)
            mask=h['cancellation_fraction_defined']; denom=abs(h['signed_Pi_m_F'])+abs(h['signed_Pi_r_F'])
            check(tag+':cancellation_mask',np.array_equal(mask,denom!=0) and np.all(np.isnan(h['cancellation_fraction'][~mask])))
            check(tag+':cancellation_formula',peak(h['cancellation_fraction'][mask]-(1-h['Pi_tot_F'][mask]/denom[mask]))<2e-15 if np.any(mask) else True)
            check(tag+':CI_counter',np.array_equal(h['H1_CI_events_per_H'],h['Y'][77]) and h['H1_CI_events_per_H'][0]==0)
            check(tag+':CI_binding',np.array_equal(h['H1_CI_thermal_to_binding_eV_per_H'],13.6058*h['H1_CI_events_per_H']))
            if not case['h1_ci_enabled']:
                check(tag+':CI_disabled',np.all(h['H1_CI_events_per_H']==0) and np.all(h['H1_CI_events_per_H_per_eta']==0))
            check(tag+':log_underflow',np.all(np.isfinite(h['H1_CI_core_log10_q_cm3_s'])) and np.array_equal(h['H1_CI_source_underflow'],h['H1_CI_core_q_cm3_s']==0))
            measures[tag]={'points':n,'fsum_energy_max_relative':peak(energy_residual),'fsum_nuclei_max_relative':max(nucleus),'fsum_charge_max':peak(charge_residual),'fsum_photon_max':peak(photon_residual),'T_formula_max_relative':peak(temp/h['temperature_K']-1.)}

nom=histories['nominal:ci_lrs']['saved']; ref=histories['reference:ci_lrs']['saved']; off=histories['nominal:registry_control_lrs']['saved']
strict=js(A/'STRICT_REFERENCE.json'); stored=arr(A/'STRICT_REFERENCE_ARRAYS.npz')
check('reference:grids',np.array_equal(nom['eta'],ref['eta']))
ref_rows=[]
for row in strict['fields']:
    f=row['field']; a=nom[f]; b=ref[f]; p=peak(b)
    scale=max(p,1e-30) if f in ('bath_energy_received_eV_per_H','excitation_escaped_energy_eV_per_H','H1_CI_events_per_H') else np.maximum(abs(b),max(p*1e-8,1e-30))
    difference=abs(a-b)/scale
    maximum=peak(difference)
    check('reference:'+f,maximum<=gates['reference_scaled_max_difference'] and maximum==row['scaled_max_difference'] and np.array_equal(difference,stored[f+'_scaled_abs_difference']))
    ref_rows.append({'field':f,'scaled_max':maximum,'absolute_max':peak(a-b),'tolerance':gates['reference_scaled_max_difference']})
check('reference:exact_fields',[r['field'] for r in strict['fields']]==gates['reference_fields'])
effects=js(A/'MATCHED_EFFECTS.json')
old=arr(REPO/'research/cr_c22c_h1_excitation_20261022/runs/c22c_h1_excitation_bdf_20261022_v1/cases/finite_uv_excitation_lrs/history.npz')
for category,actual,baseline in [('CI_same_registry',nom,off),('registry_only',off,old)]:
    check(category+':grids',np.array_equal(actual['eta'],baseline['eta']))
    for row in effects[category]['fields']:
        f=row['field']; delta=actual[f]-baseline[f]
        check(category+':'+f,float(delta[-1])==row['final_absolute_change'] and peak(delta)==row['max_abs_change'])
check('global_error_bound',contract['global_error_bound'] is None and summary['global_error_bound'] is None)
check('analysis_no_ODE_RHS',summary['analysis_ODE_calls']==summary['model_RHS_calls']==summary['old_ODE_reruns']==0)

result={'schema':'C22D_INDEPENDENT_SAVED_ARRAY_REVIEW_V1','status':'PASS_SCOPED' if all(checks.values()) else 'FAIL_PRESERVED','method':'Independent reviewer reads saved arrays, labels and pins; conservation recomputed with math.fsum, no research modules imported; strict reference and matched differences recomputed directly.','scope':'Finite saved/accepted arrays and recorded runtime/source identities; no continuous extrema/global physical error proof.','checks':checks,'failed_checks':[k for k,v in checks.items() if not v],'measurements':measures,'strict_reference':ref_rows,'new_ODE':0,'old_ODE_reruns':0,'RHS_calls':0,'rate_provider_calls':0,'input_pins':pins,'global_error_bound':None,'resource':{'affinity_observed':affinity,'affinity_used':[chosen],'native_thread_env':1,'CPU55_protected':55 not in os.sched_getaffinity(0),'started_utc':started,'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-wall,'cpu_seconds':time.process_time()-cpu},'stage':{'EXECUTION':'SAVED_ARRAY_REVIEW_ONLY','PUBLICATION':'PARENT_OWNS_FINAL_PUBLICATION','BACKUP':'PARENT_OWNS_FINAL_BACKUP','DAG':'Scoped review; line-energy closure remains next dependency'}}
target=OUT/'SAVED_ARRAY_REVIEW.json'
with target.open('x') as f:
    json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failed':result['failed_checks'],'path':str(target),'wall_seconds':result['resource']['wall_seconds']},ensure_ascii=False))
