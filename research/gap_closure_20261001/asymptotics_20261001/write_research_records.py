"""Build source-bound G03 records from local, already acquired inputs."""
import json,hashlib,sqlite3,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
WORK=REPO.parent.parent
DB=WORK/'user_import_v3/deliverables/BASS_CR_SOURCE_DATABASE_20261001_v3.sqlite'
PACKAGE=WORK/'user_import_v3/package'
science=REPO/'research/foundation_rebuild/ncp_shared_research_20260928'
old=science/'r4p0a_b0_static_tail_executor_20260930'
plan=json.loads((old/'BOUND_B0_TAIL_QUERY_PLAN.json').read_text())
binding=json.loads((old/'BINDING_INPUTS.json').read_text())
models=json.loads((HERE/'ASYMPTOTIC_MODELS.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):(HERE/name).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
c=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
citations={
'RungeMicha1996':{'pdf_pages':[2,3],'printed_pages':['1389','1390'],'equations':['2','3','22','23'],'supports':'Traveling atomic orbitals and explicit ETF; population conventions are distinct, not a theorem for BASS rho.'},
'Toshima1999':{'pdf_pages':[1,2,7],'printed_pages':['1981','1982','1987'],'equations':['1','2'],'supports':'Finite pseudostate and Gaussian AO representation; basis convergence is separate from a local-rate power law.'},
'ThorsonDelos1978':{'pdf_pages':[1,4,5],'printed_pages':['117','120','121'],'equations':['2.14'],'supports':'ETF modifies nonadiabatic couplings and correct channel boundary conditions; no bound on BASS W.'},
'Dollard1964':{'pdf_pages':[2,3],'printed_pages':['729','730'],'equations':[],'supports':'Coulomb scattering needs a modified long-range asymptotic comparison; no transferable B0 finite-matrix certificate.'}}
source=[]
for sid,cite in citations.items():
 w=dict(c.execute('select * from works where work_id=?',(sid,)).fetchone())
 f=dict(c.execute('select * from files where version_id=?',(w['selected_version_id'],)).fetchone())
 p=PACKAGE/f['local_path'];actual=sha(p)
 assert actual==f['sha256']
 source.append({'source_id':sid,'title':w['title'],'doi':w['doi'],'selected_version_id':w['selected_version_id'],
                'version_class':w['version_class'],'package_local_path':f['local_path'],'pdf_sha256':actual,
                'pdf_page_count':f['page_count'],'citation':cite})
codepaths=[
'research/foundation_rebuild/full_operator_20260926/full_operator.py',
'research/foundation_rebuild/src/bass_foundations/radial_basis.py',
'research/foundation_rebuild/src/bass_foundations/two_center.py',
'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/exact_cross.py',
'research/foundation_rebuild/ncp_shared_research_20260928/r4p0_tail_basis_preflight_20260930/receipts/B0_B3_BASIS_REGISTRY_CONTRACT.json']
write('SOURCE_EVIDENCE.json',{'database':{'filename':DB.name,'sha256':sha(DB)},
      'database_gap_row':dict(c.execute("select * from report_gaps where gap_id='REPORT_GAP_03'").fetchone()),
      'sources':source,'project_source_files':[{'path':p,'sha256':sha(REPO/p)} for p in codepaths],
      'source_csv':models['source_csv'],'basis_identity':binding['basis_identity'],
      'research_commit':binding['research_commit'],'native_calls_for_this_study':0})
v=plan['context']['velocity_au']
queries=[{'z_a0':z,'R_a0':math.hypot(z,2),'time_au':z/v,'time_hex':(z/v).hex(),
          'predictions':next(x['model_predictions'] for x in models['candidate_predictions']['incoming' if z<0 else 'outgoing'] if x['abs_z_a0']==48)} for z in [-48.,48.]]
contract={'schema':'BASS_CR_G03_MINIMUM_STATIC_DISCRIMINATOR_V1',
 'status':'SPECIFIED_NOT_AUTHORIZED_EXECUTOR_BINDING_REQUIRED',
 'scientific_question':'Does the outer |z|20,24,32 near-R^-2 class predict an independent signed pair at48, and is the |z|16 correction preasymptotic?',
 'research_source_commit':binding['research_commit'],
 'new_execution_commit':None,'execution_commit_rule':'Bind final delivered new executor commit/tree/source hash before a fresh run; old fixed-eight-query executor rejects this plan.',
 'finished_offline_analyzer':'asymptotic_models.py','returned_pair_analysis_command':'python asymptotic_models.py --return-json externally_verified_signed48.json --output G03_RETURN_ANALYSIS.json','native_executor_remaining_delta':'New context/plan digest, exact-two-query admission, maximum22 budget, fresh authorization digest, unchanged native operator worker; do not edit historical hardcoded eight-query evidence.',
 'runtime_inputs':binding['runtime_inputs'],'native_pins':binding['native'],'basis_identity':binding['basis_identity'],
 'physics':{'energy_keV_per_u':100.,'b_a0':2.,'velocity_au':v,'basis':'B0','channels':18,'selected_indices':[9,10,12,13,14]},
 'queries':queries,'number_of_qualified_queries':2,
 'same_center_order':20,'qualification_ladder':plan['context']['qualification_ladder'],
 'active_screens':plan['active_screens'],
 'resources':{'maximum_raw_operator_evaluations':22,'maximum_attempts_per_query':11,'maximum_workers':2,'threads_per_worker':1,'maximum_total_wall_seconds':900,'proposed_worker_memory_bytes':4294967296,'allocation_requires_fresh_resource_binding':True},
 'information_value':{'all_four_radius_model_prediction_relative_range_at48':next(x['relative_range_over_median'] for x in models['candidate_predictions']['outgoing'] if x['abs_z_a0']==48),
   'reason':'One signed pair beyond32 tests outward continuation, sign parity and current13.48percent spread without jumping past the64-radius or128-disjoint-support regimes. 40 only8.23percent;48 uses1.5times outerz; larger jumps risk regime mixing.',
   'limitation':'Single pair cannot uniquely distinguish all nested models, since outer-three fits largely coincide. Do not claim optimality without cost data.'},
 'predeclared_analysis':{
   'primary_fit_region':'|z|>=20 for outer hypothesis; retain all-four fits as sensitivity check, never delete16',
   'primary_holdout':'±48 are holdout until predictions scored',
   'score':'abs(observed-predicted)/observed for each sign; report every M1-M4 residual',
   'empirical_screen':'residual <= max(0.02,10*observed adjacent-level relative rho discrepancy). This is a diagnostic, not a confidence interval or certified error bound.',
   'exponent_stability_screen':'report p from20..32 and20..48; empirical class near2 requires abs(p-2)<=0.05 and abs(delta_p)<=0.05; no p confidence interval from deterministic four radii',
   'symmetry':'score negative and positive independently; neither may be reused from the other',
   'followup_decision':'If near-R^-2 class predicts48 within empirical screen, freeze refit and propose off-grid±44 as new holdout; if all models miss or exponent unstable, diagnose matrices/qualification first and only then propose±64 as different-regime discriminator.',
   'budget_separation':'No automatic second pair. Every followup requires separately fixed predictions, source, ceiling and new authorization.',
   'empirical_G03_closure_candidate':'Only after accepted outer48 plus heldout44, stability under exclusion16 and pairwise resolution checks; identify an empirical predictive class, not unique coefficients. If multiple models indistinguishable retain that limitation.',
   'continuous_claims':'None; successful heldout fits do not close G04 orG05.'},
 'stop_rules':['Stop after exactly two qualified signed queries, no propagation/state reuse.',
               'Stop immediately on source/input/native pin mismatch, nonfinite operator, SPD/rank failure or resource ceiling.',
               'If either sign exhausts11 resolutions, return attempted evidence and no qualified-pair success.',
               'Do not rerun N768/N1536, previous static points or launch larger radius pool automatically.'],
 'return_schema':['fresh_authorization_receipt','exact_source_commit_tree_and_hashes','exact_input_and_native_hashes',
                  'per_attempt_resolution_and_wall_time','raw_attempt_global_ledger',
                  'raw_S_H_D_npz_per_returned_resolution','rho_and_full_generalized_spectrum','SPD_Hermiticity_generalized_residuals',
                  'dominant_plus_minus_pair_invariant_subspace_and_next_pair_gap','adjacent_level_rho_discrepancy',
                  'per_sign_frozen_holdout_residuals','failures_and_unused_budget','P_selected=unavailable_without_state','Pdot=unavailable_without_state'],
 'authorization':{'new_native_run_authorized':False,'old_authorization_reuse':False,'authorization_consumed_here':0},
 'claim_ceiling':binding['claim_ceiling']}
write('MINIMUM_STATIC_DISCRIMINATOR_CONTRACT.json',contract)
write('CLAIM_UPDATE.json',{'gap_id':'G03','database_gap_id':'REPORT_GAP_03',
 'status_before':'REPORTED_RECOMMENDATION_NOT_VALIDATED','status_after':'RESOLVED_WITH_LIMITATION',
 'evidence_status':['LITERATURE_SUPPORTED','DERIVED','SYMBOLICALLY_VERIFIED','NUMERICALLY_CHECKED','IMPLEMENTATION_VERIFIED'],
 'claims_closed':['Actual B0 finite-FEM overlap asymptotics differs from infinite-support AO idealization.',
                  'Conditional smooth dominant-branch parity removes C3; an exact degenerate cusp counterexample proves symmetry alone insufficient.',
                  'M1-M4 signed fits, leave-one-radius-out errors and outer-window sensitivity computed from exact frozen rows.',
                  'Two-query signed48 discriminator specified with frozen predictions and stops.'],
 'claims_open':['Unique asymptotic model or leading coefficient not empirically identified.',
                'Pure R^-2 law for actual stored model not proved; isolated-generator residual may yield asymptotic floor.',
                'Continuous majorant, infinite-tail certificate and propagated state probabilities not available.'],
 'blocker_class':'NUMERICAL_METHOD_BLOCKER','execution_blocker':{'class':'IMPLEMENTATION_BLOCKER','first_failing_artifact':'r4p0a_b0_static_tail_executor_20260930/static_tail.py: exact_items/verify_static_budget use fixed8queries/88attempts','completed':'twoquerycontract and offline returnedpair analyzer','minimum_repair':'source-bound separate G03 exact-two-query admission/nonce/budget22; G02 fixed66query adapter does not cover G03'},'exact_failing_claim':'Four distinct radii do not identify a stable M1-M4 law: M2 exponent changes2.121808to1.998387 when16 is withheld; all leave-one-out maximum errors9.21to10.69percent.',
 'minimum_repair':'Source-bind narrow two-query executor and seek fresh authorization for±48; first analyze its frozen predictions. G04 independently requires exact-model residual closure.',
 'next_minimum_action':'MINIMUM_STATIC_DISCRIMINATOR_CONTRACT.json',
 'tests':{'command':'python -m unittest discover -s research/gap_closure_20261001/asymptotics_20261001 -p test_asymptotic_models.py -v','count':7,'result':'PASS','log':'TEST_RESULTS.log'},
 'source_ids':list(citations),'new_external_runs':0,'new_native_calls':0,'authorization_consumed':0,
 'claim_gate_change':'Only G03 formulation and empirical diagnosis reduced; G03_EMPIRICAL_MODEL_IDENTIFIED remains OPEN. No scientific ceiling promoted.',
 'artifacts':['ASYMPTOTIC_REPORT.md','ASYMPTOTIC_MODELS.json','SOURCE_EVIDENCE.json','MINIMUM_STATIC_DISCRIMINATOR_CONTRACT.json','asymptotic_models.py','test_asymptotic_models.py','PARITY_SYMBOLIC_CHECK.json','parity_symbolic_checks.py','G03_RUNTIME.json'],
 'claim_ceiling':binding['claim_ceiling']})
print('Wrote source evidence, minimum contract and claim update.')
