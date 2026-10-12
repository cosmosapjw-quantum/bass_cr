from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parent
OLD = Path('/workspace/scratch/18ee842bf84f/bass_cr/research/cr_rux_m1_m3_20261012/inputs/consumer_intake')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def readj(path):
    return json.loads(path.read_text())

def writej(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

sources = readj(ROOT / 'SOURCES_IMPORTED.json')
for row in sources:
    if row['name'] == 'pr110_c12_handoff':
        row['current_intake_read_extent'] = 'full'
    if row['name'] == 'pr110_cr_module':
        row['current_intake_read_extent'] = 'selected lines 5-39, 80-105, 343-392; full bytes retained'
    original = OLD / row['tool_response']
    target = ROOT / 'baseline' / row['tool_response']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(original.read_bytes())
    row['original_tool_response'] = str(target.relative_to(ROOT))
    row.pop('tool_response', None)

def pr(name):
    return readj(ROOT / 'tool_responses' / (name + '.json'))['structuredContent']

def branch(name):
    return json.loads(pr(name)['content'])[0]

heads = []
for name in ['pr110_current', 'pr97_current', 'pr83_current']:
    p = pr(name)
    heads.append({k:p.get(k) for k in ['number','title','head','head_sha','updated_at','draft','state','merged','url']})
    heads[-1]['evidence'] = 'tool_responses/' + name + '.json'
for name, ref in [('current_cr_branch_0','research/cr-phys03-fs10-xi01-20261010'),('current_cr_branch_1','research/cr-physical-receiver-20261010')]:
    p = branch(name)
    heads.append({'branch':ref, 'head_sha':p['sha'], 'committer_date':p['commit']['committer']['date'], 'evidence':'tool_responses/'+name+'.json'})

tools = []
for path in sorted((ROOT/'tool_responses').glob('*.json')):
    b = path.read_bytes()
    tools.append({'path':str(path.relative_to(ROOT)), 'bytes':len(b), 'sha256':digest(b)})
baseline = []
for path in sorted((ROOT/'baseline').glob('*.json')):
    b = path.read_bytes()
    baseline.append({'path':str(path.relative_to(ROOT)), 'bytes':len(b), 'sha256':digest(b), 'role':'inherited session evidence; not a new scientific execution'})
plan = ROOT/'baseline/PLAN_KO.md'
baseline.append({'path':str(plan.relative_to(ROOT)), 'bytes':plan.stat().st_size, 'sha256':digest(plan.read_bytes()), 'role':'parent selected source-binding plan'})

result = {
 'schema':'cr-electron-source-consumer-intake.v1',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'owner':'consumer_intake independent read-only intake',
 'status':'COMPLETE_BOUNDED_INTAKE_NO_NEW_CONSUMER_SELECTION_OBSERVED',
 'task':'latest rei_bianchi CR/RUX source, observable, bath, clock and downstream error-budget intake',
 'baseline_intake_created_utc':'2026-10-12 07:51:41 UTC',
 'report_baseline_time_exactly_bound':False,
 'baseline_time_note':'Parent refers to a report about two hours earlier. This check uses its underlying exact consumer heads and 07:51:41 intake, rather than inventing a report timestamp.',
 'harness':{'family':'gpt6-astra','version':'4.0.0','parent_host_metadata':'GPT-6 Astra Pro','core':'/workspace/scratch/18ee842bf84f/harness/research/PROJECT_INSTRUCTIONS.md','role':'evidence intake, not a scientific promotion reviewer'},
 'mutations_and_runs':{'remote_mutations':0,'consumer_repository_mutations':0,'scientific_runs':0,'test_runs':0,'old_suite_reruns':0},
 'repository':'cosmosapjw-quantum/rei_bianchi',
 'current_heads':heads,
 'change_since_baseline':{
   'pr110_head_unchanged':True,
   'cr_phys03_xi010_head_unchanged':True,
   'cr_original_receiver_head_unchanged':True,
   'new_cr_source_constructor_received_in_checked_scope':False,
   'new_selected_cr_observable_received_in_checked_scope':False,
   'new_cr_absolute_or_relative_error_budget_received_in_checked_scope':False,
   'new_qe_tA_binding_return_received_in_checked_scope':False,
   'rux_pr_query_matches':0,
   'rux_branch_query_matches':0,
   'other_recent_source_prs':[{'pr':112,'scope':'conditional synthetic FT03/RCT stepper; not CR electron-source binding','evidence':'tool_responses/source_prs_current.json'},{'pr':113,'scope':'saved warm P01 RCT rate-only diagnostic, RCT OFF; not CR electron-source binding','evidence':'tool_responses/source_prs_current.json'}],
   'absence_scope':'Only selected CR/RUX/source PR search, branch search and exact relevant heads; no repository-wide or cloud-wide absence claim.'
 },
 'actual_consumer':{
   'repository_commit':'17f8d0daa72e0f76a49cde01b110f650a6688c42',
   'function':'rust/rei_microphysics/src/axisym_cr_deposition.rs::cr_deposition_derivative',
   'kind':'instantaneous source-pinned FS10 terminal deposition packet on a prescribed collisionless CR proton snapshot',
   'available_local_observables':['primary and secondary H/He ionization event rates','gas heat power','stored ionization power','prompt excitation/continuum escape power','source-only temperature derivative from consistent event and heat ledger'],
   'selected_new_downstream_observable':None,
   'selected_cr_on_history':None,
   'general_evolving_bath_or_time_support':False,
   'qe_tA_scalar_history_directly_accepted_by_current_api':False,
   'source_refs':['pr110_cr_module','pr110_cr_pin','phys01_receiver_report']
 },
 'actual_snapshot':{
   'proper_time_s':1.0e10, 'n_h_m3':140.0,'n_he_m3':11.542553191489361,'temperature_k':100.0,'y_he_mass_fraction':0.248,
   'xi_knots':[0.01,0.1], 'composition':'x_HII=x_HeII=xi; x_HeIII=0','xi_interpolation':False,
   'H_s':3.3e-17, 'shear_s':3.3e-18,'geometry':'a_relative=exp(H*t), b=shear*t; same snapshot is enforced by the receiver',
   'source_redshift':8.0, 'active_proton_window_eV':[1e6,4e6],
   'provider_manifest_orders':{'energy':48,'mu':8,'age':8},
   'closure':'FS10_LOCAL_DEPOSITION_PROMPT_EXCITATION_AND_CONTINUUM_ESCAPE',
   'source_refs':['phys01_manifest','pr110_cr_pin']
 },
 'actual_compiled_packets':[
   {'xi':0.01,'provider_id':'CRP_L17_MD14_RUDD_FS10_XI001_CONDITIONAL_V1','packet_sha256':'1bb0d4e1c4c71a409ca170e8741fabd17fabe02195b86fe24a06875712d0e373','manifest_canonical_sha256':'79835c5eaa891f37f663c1852d6035ee446a25778763164cfea2d20531cdd901','heat_power_J_m3_s':1.2093044641845817e-42,'ionization_stored_power_J_m3_s':1.3963750685843803e-42,'excitation_escape_power_J_m3_s':6.613224299070425e-43,'modelled_ionization_loss_power_J_m3_s':3.2670019626760045e-42,'full_proton_injection_power_J_m3_s':5.315371751092545e-34,'numerical_heat_projection_bound_J_m3_s':2.4489321098323726e-46},
   {'xi':0.1,'provider_id':'CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1','packet_sha256':'2ecb1413c93f5cbc9ab64689ac17c191020320c9734138ea4bfaf291e10b6d46','manifest_canonical_sha256':'d34b42d652b8b721caabeda95ad729753a850f6da7499f4cedfeb8b299c35b44','heat_power_J_m3_s':1.8054996515543073e-42,'ionization_stored_power_J_m3_s':9.476115446294631e-43,'excitation_escape_power_J_m3_s':2.1689058806714367e-43,'modelled_ionization_loss_power_J_m3_s':2.970001784250914e-42,'full_proton_injection_power_J_m3_s':5.315371751092545e-34,'numerical_heat_projection_bound_J_m3_s':2.2263019180294305e-46}
 ],
 'actual_archived_local_readout':{
   'xi':0.01,'electron_source_m3_s':5.979293938079537e-25,'source_only_temperature_derivative_K_s':3.811186545594215e-22,'temperature_derivative_with_geometry_K_s':-6.599999618881346e-15,
   'formula':'2*heat_power/(3*k_B*n_particles) - T*electron_source/n_particles',
   'source_ref':'phys01_receiver_report',
   'evidence_status':'archived receiver report read; no new execution or computation'
 },
 'constructor_identity':{
   'actual_compiled_native_packet':True,
   'actual_manifest_scenario':True,
   'new_proton_source_constructor_receipt':None,
   'alpha_cr_efficiency_escape_and_SN_parameters':'Inherited intake records byte-bound source defaults only, not a separately recovered actual call receipt; not promoted to selected constructor arguments.',
   'known_injection_file_sha256':'c5eda0e60302339af1bbdd0603ae1cd8a8921d9e6489c22d954e0bc92968c27d',
   'producer_source_semantics_from_prior_intake':'Angle-integrated proton dN/(proper m^3 s dK); isotropic dmu/2; full 10 keV..1 PeV energy normalization, no active-window renormalization.',
   'exact_Qe_AW_birth_tag_and_M0_binding_owner':'parent and dag_audit; not recomputed by this intake'
 },
 'error_budget':{
   'downstream_absolute':None,'downstream_relative':None,'denominator':None,'cr_heating_contribution_fraction':None,
   'new_named_consumer_budget_supplied':False,
   'local_table_projection_bound_is_downstream_budget':False,
   'C12_whole_history_time9_2e_minus6_spectral24_1e_minus3_gates_are_CR_budget':False,
   'basis':'Unchanged exact relevant heads, current packet/source API and selected handoff; baseline null fields remain unbound.'
 },
 'lightweight_reuse_route':{
   'parent_selected_application':'independent fixed-bath Qe(W,t)=t*A(W) application; selection belongs to parent, not a newly received REI consumer request',
   'sufficient_read_only_imports':['actual bath and clock above','source-manifest identity','existing local energy/species accounting semantics'],
   'producer_binding_required':['exact A(W) bytes and two birth-tag normalization','electron W support and species/threshold convention','same M0 bath/operator/selected_record representation','proper-time origin, source onset/prehistory and initial electron stock'],
   'safe_first_observable':'Parent may report source-bound fixed-bath causal heat power after its producer/kernel identity check; this is a new scoped BASS application, not a REI full-history result.',
   'temperature_extension_requirement':'A temperature source term needs the matching electron/ionization event ledger and particle density; old terminal electron production cannot silently be paired with a new causal heat source.',
   'current_receiver_on_accepts_new_causal_packet_without_source_change':False,
   'forbidden_shortcuts':['FS10 terminal heat times M0 p','use full proton injection as an unrequested observable denominator','xi ionization knot as CR energy efficiency or CR heat fraction','use xi=.1 terminal packet as xi=.01 M0 bath identity','declare current component API a general Qe history consumer'],
   'new_heavy_run_needed_for_this_intake':False
 },
 'M3_retained_status':{'local_off_contract':'NO_PATCH_JUSTIFIED','source_zero_and_provider_not_called':'retained source semantics and inherited historical evidence; no rerun','current_whole_history_receipt':'NOT_NEWLY_BOUND'},
 'sources':sources,
 'baseline_evidence':baseline,
 'direct_tool_responses':tools,
 'limitations':['Latest heads were queried on 2026-10-12 around 11:31-11:35 UTC. Mutable PR descriptions are metadata, not new source/binary receipts.','No full consumer checkout, exhaustive repository/cloud audit, scientific execution or suite rerun.','Five relevant source byte copies were reused from an already hash-verified intake; exact commit equality of current relevant heads was freshly checked.','The generic CR branch search returned a continuation cursor; no claim of exhaustive branch enumeration is made.','Default source parameters remain defaults absent an actual constructor receipt.']
}
writej(ROOT/'SOURCE_IDENTITY.json', result)
writej(ROOT/'SOURCES_IMPORTED.json', sources)
print(json.dumps({'manifest':str(ROOT/'SOURCE_IDENTITY.json'),'sha256':digest((ROOT/'SOURCE_IDENTITY.json').read_bytes()),'sources':len(sources),'tool_responses':len(tools)},ensure_ascii=False))
