#!/usr/bin/env python3
"""Independent saved-data C22A review; no RHS or ODE integrator is called.

The failed Radau run remains FAILED_PRESERVED and its exact-zero gate remains
FAIL.  Derived diagnostics are a separate review of the original saved bytes.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
            'BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
import argparse, ast, datetime, hashlib, io, json, math, sys
from pathlib import Path
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', required=True, type=Path)
parser.add_argument('--nominal-run', required=True)
parser.add_argument('--reference-run', required=True)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
PROJECT = args.project.resolve()
UNIT = PROJECT/'research/cr_c22a_thermochemical_20261022'
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=False)
sys.dont_write_bytecode = True

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def read_json(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), {'path':str(path),'size_bytes':len(raw),'sha256':sha(raw)}

def read_npz(path):
    raw = Path(path).read_bytes()
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        data = {k:z[k].copy() for k in z.files}
    return data, {'path':str(path),'size_bytes':len(raw),'sha256':sha(raw),
                  'loaded_from_same_hashed_memory_bytes':True}

def maximum_abs(x):
    return float(np.max(np.abs(x)))

def equality_error(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    error = maximum_abs(actual-expected)
    peak = maximum_abs(expected)
    return {'maximum_absolute_difference':error,
            'over_expected_peak':error/peak if peak else None,
            'exact_equal':bool(np.array_equal(actual, expected))}

contract, contract_file = read_json(UNIT/'CONTRACT.json')
gates = contract['acceptance_gates']
source_freeze, source_freeze_file = read_json(UNIT/'evidence/SOURCE_FREEZE.json')
source_payload = {k:v for k,v in source_freeze.items() if k!='identity_sha256'}
assert sha(canonical(source_payload)) == source_freeze['identity_sha256']

def check_current_sources():
    rows = []
    for rec in source_freeze['files']:
        p = PROJECT/rec['path']; raw = p.read_bytes()
        assert len(raw)==rec['size_bytes'] and sha(raw)==rec['sha256'], rec['path']
        rows.append({'path':rec['path'],'sha256':sha(raw),'size_bytes':len(raw)})
    return rows

source_before = check_current_sources()
# Literal inventories are data, not imported model implementations.
atomic_path = PROJECT/'research/cr_c21o_hheli_z2_20261021/atomic_network.py'
literal = {}
for node in ast.parse(atomic_path.read_text()).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {'ISOTOPES','CHANNELS'}:
                literal[target.id] = ast.literal_eval(node.value)
ISOTOPES, CHANNELS = literal['ISOTOPES'], literal['CHANNELS']
labels, scales, charges, binding, groups, totals = [], [], [], [], {}, {}
for name, A, Z, total, scale in ISOTOPES:
    groups[name] = list(range(len(labels),len(labels)+Z+1)); totals[name]=total
    increments = [] if Z==0 else [13.6] if Z==1 else [24.59,54.42] if Z==2 else [5.392,75.64,122.5]
    levels = np.r_[0.,np.cumsum(increments)]
    for charge in range(Z+1):
        labels.append('n' if name=='n' else name+'_'+str(charge))
        scales.append(scale); charges.append(charge); binding.append(levels[charge])
assert len(labels)==21
assert set(groups)=={'n','H1','D','T','He3','He4','Li6','Li7'}
scales, charges, binding = map(np.asarray,(scales,charges,binding))
zero_ids = groups['n']+groups['T']
K_B = 1.380649e-23/1.602176634e-19
E0 = np.asarray(contract['physics']['UV_energies_initial_eV'])
thresholds = np.unique([row['chi_eV'] for row in CHANNELS]+[64.39])

def reconstruct(eta, Y, meta, atol):
    assert Y.shape == (74,len(eta)) and np.all(np.isfinite(Y))
    assert len(eta)>1 and np.all(np.diff(eta)>0)
    assert meta['atomic_populations']==labels and meta['state_size']==74
    atomic = scales[:,None]*Y[40:61]
    electron = charges@atomic
    particles = np.sum(atomic,axis=0)+electron
    assert np.all(particles>0)
    T = Y[67]/(1.5*K_B*particles)
    E = E0[:,None]*np.asarray([math.exp(-float(t)) for t in eta])
    V = np.sum(E*Y[61:67],axis=0)
    B = binding@atomic
    total_energy = Y[67]+B+V+Y[68]+Y[69]+Y[70]
    e_rel = (total_energy-total_energy[0])/abs(total_energy[0])
    q_rel = (electron+Y[71]-Y[72]-electron[0])/max(np.sum(Y[61:67,0]),1.)
    p_rel = (np.sum(Y[61:67],axis=0)+Y[72]-np.sum(Y[61:67,0]))/max(np.sum(Y[61:67,0]),1.)
    nucleus = {name:maximum_abs(np.sum(atomic[ids],axis=0)/totals[name]-1.)
               for name,ids in groups.items() if totals[name]>0}
    leaks = {}
    for i in zero_ids:
        j=int(np.argmax(np.abs(Y[40+i])))
        leaks[labels[i]]={'maximum_absolute_scaled':abs(float(Y[40+i,j])),
                         'maximum_absolute_abundance_per_H':abs(float(atomic[i,j])),
                         'scaled_over_solver_atol':abs(float(Y[40+i,j]))/atol,
                         'eta_at_maximum':float(eta[j]),
                         'minimum_scaled':float(np.min(Y[40+i])),
                         'maximum_scaled':float(np.max(Y[40+i])),
                         'exact_zero':bool(np.all(Y[40+i]==0.))}
    iso_errors={}
    for left,right in [('H1','D'),('He3','He4'),('Li6','Li7')]:
        iso_errors[left+'_'+right]=maximum_abs(Y[40+np.array(groups[left])]-Y[40+np.array(groups[right])])
    values={'max_abs_energy_relative_residual':maximum_abs(e_rel),
            'max_nucleus_relative_residual':max(nucleus.values()),
            'max_abs_charge_photon_relative_residual':maximum_abs(q_rel),
            'max_abs_photon_number_relative_residual':maximum_abs(p_rel),
            'min_population_scaled':float(np.min(Y[40:61])),
            'min_UV_counts_per_H':float(np.min(Y[61:67]))}
    checks={key:bool(value>=gates[key] if key.startswith('min_') else value<=gates[key])
            for key,value in values.items()}
    checks['declared_zero_n_T']=all(row['exact_zero'] for row in leaks.values())
    domain=contract['RR_temperature_fit_domain_K']
    checks['temperature_inside_adopted_fit_domain']=bool(np.all((T>=domain[0])&(T<=domain[1])))
    diagnostic={'points':len(eta),'state_shape':list(Y.shape),'finite_states':True,
                'metrics':values,'gates':checks,'all_preregistered_state_gates_pass':all(checks.values()),
                'temperature_min_K':float(T.min()),'temperature_max_K':float(T.max()),
                'temperature_final_K':float(T[-1]),'nucleus_residual_by_isotope':nucleus,
                'zero_inventory_absolute_residuals':leaks,
                'isotope_scaled_charge_fraction_max_abs_difference':iso_errors,
                'energy_initial_eV_per_H':float(total_energy[0]),
                'recombination_count_final_per_H':float(Y[71,-1]),
                'absorption_count_final_per_H':float(Y[72,-1]),
                'tau_T_final':float(Y[73,-1]),'H1_ionized_fraction_final':float(Y[42,-1]),
                'clipping_or_zero_replacement':'NONE'}
    arrays={'eta':eta,'temperature_K':T,'electron_count_per_H':electron,
            'tau_T':Y[73],'H1_ionized_fraction':Y[42],
            'energy_total_eV_per_H':total_energy,'energy_relative_residual':e_rel,
            'charge_photon_relative_residual':q_rel,'photon_number_relative_residual':p_rel,
            'atomic_abundance_per_Href':atomic,'UV_energy_eV_per_H':V,
            'ionization_energy_eV_per_H':B,'neutron_scaled_original':Y[40],
            'UV_cohort_energies_eV':E.T}
    return diagnostic,arrays

def endpoint_audit(records, meta):
    expected_breaks = meta['transition_times_eta']
    assert len(records)==len(expected_breaks)-1
    maximum_ulp = 0
    for rec,left,right in zip(records,expected_breaks[:-1],expected_breaks[1:]):
        assert rec['success'] and rec['eta_start']==left and rec['eta_end']==right
        mid = left+.5*(right-left)
        desired = np.sign(E0[:,None]*math.exp(-mid)-thresholds[None,:])
        assert np.all(desired!=0)
        for which in ['left','right']:
            side=rec['endpoint_branch_checks'][which]
            t=side['evaluation_eta']
            actual=np.sign(E0[:,None]*math.exp(-t)-thresholds[None,:])
            assert left<t<right and np.array_equal(actual,desired)
            assert np.array_equal(side['actual_sides'],actual)
            assert np.array_equal(side['expected_sides'],desired)
            assert np.array_equal(side['thresholds_eV'],thresholds)
            assert side['state_mutation']=='NONE'
            assert 1<=side['ulp_steps']<=side['max_ulps']
            maximum_ulp=max(maximum_ulp,side['ulp_steps'])
    return {'segments':len(records),'solver_success_all_segments':True,
            'endpoints':2*len(records),'branch_comparisons':2*len(records)*len(E0)*len(thresholds),
            'maximum_ulp_steps':maximum_ulp,'actual_energy_sides_recomputed':True}

def load_run(name, expected_method):
    run=UNIT/'runs'/name
    inputs,input_file=read_json(run/'INPUT.json')
    runtime,runtime_file=read_json(run/'RUNTIME.json')
    src,src_file=read_json(run/'SOURCE_IDENTITY.json')
    summ,summ_file=read_json(run/'SUMMARY.json')
    assert inputs['run_id']==name and inputs['method']==expected_method
    assert inputs['saved_times']==201 and inputs['global_error_bound'] is None
    assert sha(canonical(inputs))==runtime['input_sha256']
    assert src==source_freeze and src['identity_sha256']==runtime['source_identity_sha256']
    assert summ['source_identity_sha256']==src['identity_sha256']
    assert all(v=='1' for v in runtime['thread_environment'].values())
    resource,resource_file=read_json(run/'RESOURCE.json')
    admission=resource['admission']
    assert 55 not in admission['selected_worker_cpus'] and admission['coordinator_cpu']!=55
    assert admission['coordinator_cpu'] not in admission['selected_worker_cpus']
    assert resource['run_worker_cap']==2 and resource['lease_observation']['modified'] is False
    return run,inputs,runtime,summ,{'input':input_file,'runtime':runtime_file,'source_identity':src_file,
                'summary':summ_file,'resource':resource_file,
                'resource_checks':'CPU55 protected; coordinator distinct; one-thread env; bounded lease receipt read'}

nomrun,nominputs,nomruntime,nomsummary,nombindings=load_run(args.nominal_run,'BDF')
refrun,refinputs,refruntime,refsummary,refbindings=load_run(args.reference_run,'Radau')
assert nomsummary['status']=='COMPLETE_SCOPED'
assert refsummary['status']=='PARTIAL_PRESERVED'
nominal=[]; histories={}; raw_arrays={}
for case in nominputs['cases']:
    name=case['name']; path=nomrun/'cases'/name
    meta,mfile=read_json(path/'MODEL.json'); rec,rfile=read_json(path/'RECEIPT.json')
    complete,cfile=read_json(path/'COMPLETE.json'); h,hfile=read_npz(path/'history.npz')
    assert meta['case']==case and rec['case']==case
    assert rec['input_sha256']==nomruntime['input_sha256']
    assert rec['source_identity_sha256']==source_freeze['identity_sha256']
    assert rec['history_sha256']==hfile['sha256'] and rec['history_bytes']==hfile['size_bytes']
    assert rec['model_metadata_sha256']==mfile['sha256']
    assert complete['receipt_sha256']==rfile['sha256'] and complete['history_sha256']==hfile['sha256']
    assert complete['status']=='COMPLETED_SCOPED'
    for key,value in h.items():
        assert value.dtype.kind!='O'
        if key=='cancellation_fraction':
            assert np.array_equal(np.isfinite(value),h['cancellation_fraction_defined'])
            assert not np.isinf(value).any()
        elif value.dtype.kind in 'fci':
            assert np.isfinite(value).all(),key
    assert h['atomic_state_labels'].tolist()==labels
    expected_grid=np.r_[0.,np.geomspace(1e-10,.02,100),np.linspace(.02,math.log(7),101)[1:]]
    assert np.array_equal(h['eta'],expected_grid)
    d,arrays=reconstruct(h['eta'],h['Y'],meta,nominputs['atol'])
    accepted,unused=reconstruct(h['accepted_eta'],h['accepted_Y'],meta,nominputs['atol'])
    assert all(d['gates'].values()) and all(accepted['gates'].values())
    derived_parity={}
    for key in ['temperature_K','energy_total_eV_per_H','energy_relative_residual',
                'charge_photon_relative_residual','photon_number_relative_residual',
                'atomic_abundance_per_Href','UV_energy_eV_per_H','ionization_energy_eV_per_H',
                'UV_cohort_energies_eV','tau_T','H1_ionized_fraction']:
        derived_parity[key]=equality_error(h[key],arrays[key])
        assert np.allclose(h[key],arrays[key],rtol=5e-14,atol=3e-15 if 'residual' in key else 1e-30),key
    assert np.allclose(h['n_e_cm3'],arrays['electron_count_per_H']*h['nH_ref_cm3'],rtol=5e-15,atol=0)
    assert np.allclose(h['nH_ref_cm3']*h['a']**3,h['nH_ref_cm3'][0]*h['a'][0]**3,rtol=5e-15)
    factor=math.sqrt(6)*8*math.pi*6.67430e-11/299792458.**2/h['H']**2
    p={x:h['p_'+x+'_J_m3'] for x in ['m','gamma','nu']}
    p['r']=p['gamma']+p['nu'];p['tot']=p['m']+p['r']
    stress_errors={}
    for sector,value in p.items():
        expected=factor*value
        for key,want in [('p_'+sector+'_J_m3',value),('signed_Pi_'+sector+'_F',expected),
                         ('Pi_'+sector+'_F',np.abs(expected))]:
            assert np.allclose(h[key],want,rtol=5e-14,atol=1e-300),key
            stress_errors[key]=equality_error(h[key],want)
    assert np.allclose(h['Sigma_F'],math.sqrt(6)*np.abs(h['s'])/h['H'],rtol=5e-14,atol=1e-300)
    denom=np.abs(p['m'])+np.abs(p['r'])
    defined=denom!=0
    assert np.array_equal(defined,h['cancellation_fraction_defined'])
    assert np.allclose(h['cancellation_fraction'][defined],1-np.abs(p['tot'][defined])/denom[defined],rtol=5e-14,atol=1e-15)
    d['stress_signed_then_frobenius']='PASS_ALL_201_SAVED_TIMES'
    d['stress_parity']=stress_errors
    d['derived_saved_field_parity']=derived_parity
    d['endpoint_checks']=endpoint_audit(rec['segments'],meta)
    d['accepted_mesh']=accepted
    d['case']=case
    d['proper_elapsed_final_Myr']=float(h['proper_elapsed_s'][-1]/(365.25*86400*1e6))
    d['omitted_retained_trace_H2_fraction_saved_max']=float(h['omitted_trace_energy_H2_fraction'].max())
    d['files']={'history':hfile,'model':mfile,'receipt':rfile,'complete':cfile}
    if name=='dark_expansion':
        d['pure_reaction_free_adiabat_oracle']='NOT_APPLICABLE: residual initial ionization undergoes nonzero RR'
        d['temperature_difference_from_300_exp_minus2eta_max_relative']=maximum_abs(h['temperature_K']/(300*np.exp(-2*h['eta']))-1.)
    nominal.append(d);histories[name]=h;raw_arrays[name]=arrays

assert len(refinputs['cases'])==1
refcase=refinputs['cases'][0];name=refcase['name']
assert refcase==next(c for c in nominputs['cases'] if c['name']==name)
rpath=refrun/'cases'/name
meta,mfile=read_json(rpath/'MODEL.json'); fail,ffile=read_json(rpath/'FAILURE.json')
segments,sfile=read_json(rpath/'FAILED_SEGMENTS.json')
raw,rawfile=read_npz(rpath/'FAILED_ACCEPTED_SOLUTION.npz')
assert fail['status']=='FAILED_PRESERVED' and 'ZERO_INITIAL_INVENTORY_CHANGED' in fail['exception']
assert fail['input_sha256']==refruntime['input_sha256'] and fail['source_identity_sha256']==source_freeze['identity_sha256']
assert set(raw)=={'eta','Y'} and np.array_equal(raw['eta'],histories[name]['eta'])
reference,refarrays=reconstruct(raw['eta'],raw['Y'],meta,refinputs['atol'])
assert not reference['gates']['declared_zero_n_T']
assert all(v for k,v in reference['gates'].items() if k!='declared_zero_n_T')
reference['original_status']='FAILED_PRESERVED'
reference['strict_zero_inventory_gate']='FAIL_PRESERVED_UNMODIFIED'
reference['accepted_mesh_states']='UNAVAILABLE: preserved NPZ contains 201 dense saved samples only'
reference['endpoint_checks']=endpoint_audit(segments,meta)
reference['files']={'raw_saved_solution':rawfile,'model':mfile,'failure':ffile,'failed_segments':sfile}
reference['causal_scope']='n RHS is identically zero in inspected model; small numerical solver leakage is consistent with data, exact floating-point mechanism not diagnosed'
# Frozen fields only: no RHS, summarize, or ODE calls.  This supplies H and
# source-sector stresses for the six preregistered field comparisons.
sys.path.insert(0,str(UNIT))
from model import ThermochemicalFactory
model=ThermochemicalFactory(ellmax=meta['ellmax']).build(refcase)
fields=[model.fields(float(t),y) for t,y in zip(raw['eta'],raw['Y'].T)]
H=np.array([q['H'] for q in fields]);s=np.array([q['s'] for q in fields])
refarrays['n_e_cm3']=refarrays['electron_count_per_H']*np.array([q['nH_ref_cm3'] for q in fields])
refarrays['Sigma_F']=math.sqrt(6)*np.abs(s)/H
signed_pr=np.array([q['Pi_gamma_J_m3']+q['Pi_nu_J_m3'] for q in fields])
refarrays['Pi_r_F']=math.sqrt(6)*8*math.pi*6.67430e-11/299792458.**2/H**2*np.abs(signed_pr)
assert np.allclose(refarrays['temperature_K'],[q['temperature_K'] for q in fields],rtol=3e-15,atol=0)
comparison={}
for key in gates['reference_fields']:
    got=histories[name][key];ref=refarrays[key]
    row=equality_error(got,ref)
    row['maximum_absolute_difference_over_reference_peak']=row.pop('over_expected_peak')
    row['gate_limit']=gates['reference_max_abs_difference_over_reference_peak']
    row['numerical_difference_gate_pass']=row['maximum_absolute_difference_over_reference_peak']<=row['gate_limit']
    comparison[key]=row
assert all(r['numerical_difference_gate_pass'] for r in comparison.values())
source_after=check_current_sources()
assert source_before==source_after
npz_path=OUT/'REFERENCE_DIAGNOSTICS.npz'
with npz_path.open('xb') as f:np.savez_compressed(f,**refarrays)
reference['derived_diagnostics_artifact']={'path':str(npz_path),'sha256':sha(npz_path.read_bytes()),
   'scope':'separate no-ODE review; not a successful run history; original neutron entries unchanged'}
report={'schema':'C22A_INDEPENDENT_SAVED_DATA_REVIEW_V1',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'execution':{'new_ODE':0,'old_ODE':0,'RHS_calls':0,'frozen_fields_evaluations':201,
                     'solver_imported_indirectly':True,'solver_called':False,
                     'source_unchanged_before_after':True,'source_files_verified':len(source_before)},
        'source_identity_sha256':source_freeze['identity_sha256'],
        'contract_file':contract_file,'source_freeze_file':source_freeze_file,
        'nominal_run_bindings':nombindings,'reference_run_bindings':refbindings,
        'nominal_cases':nominal,'reference_saved_data':reference,
        'method_comparison':{'same_physical_case':True,'same_frozen_execution_source':True,
                            'same_201_eta_grid':True,'nominal_method':'BDF','nominal_rtol':nominputs['rtol'],
                            'nominal_atol':nominputs['atol'],'reference_method':'Radau',
                            'reference_rtol':refinputs['rtol'],'reference_atol':refinputs['atol'],
                            'fields':comparison,'all_field_difference_gates_pass':True,
                            'formal_reference_acceptance':'FAIL_EXACT_ZERO_GATE_RETAINED',
                            'meaning':'Limited numerical agreement of saved trajectories; failed reference run is not promoted; no global error bound'},
        'decision':{'nominal_3_cases':'PASS_SCOPED_PREREGISTERED_SAVED_AND_ACCEPTED_STATE_GATES',
                    'reference_case':'FAILED_PRESERVED_EXACT_ZERO_INVENTORY_GATE',
                    'reference_other_numeric_state_gates':'PASS_SCOPED_SAVED_201',
                    'matched_field_comparison':'PASS_SCOPED_DIAGNOSTIC_ONLY',
                    'full_physical_closure':'OPEN'},
        'script_sha256':sha(Path(__file__).read_bytes()),
        'stage':{'EXECUTION':'SAVED_DATA_REVIEW_COMPLETE; reviewer ODE0',
                 'PUBLICATION':'PARENT_OWNED','BACKUP':'PARENT_OWNED',
                 'DAG':'Nominal scoped result accepted; exact-zero reference gate unresolved; omitted physics/full closure OPEN'},
        'global_error_bound':None}
with (OUT/'SAVED_DATA_REVIEW.json').open('x') as f:
    json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'decision':report['decision'],'comparison':comparison,
                  'reference_zero_face':reference['zero_inventory_absolute_residuals'],
                  'output':str(OUT/'SAVED_DATA_REVIEW.json')},indent=2))
