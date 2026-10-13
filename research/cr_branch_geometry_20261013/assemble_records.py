"""Assemble this unit's research records without executing scientific checks."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json

ROOT=Path(__file__).resolve().parent
UNIT='CR-THEORY-BRANCH-GEOMETRY-20261013'
BASE='c450b00108dc05885a25d0d9c042cdcfe41bd659'
REPO='cosmosapjw-quantum/bass_cr'
BRANCH='research/cr-branch-geometry-20261013'
REPO_UNIT='research/cr_branch_geometry_20261013'
SELECTED=['CR_THEORY_COUPLED_BRANCH_SOLVER','CR_THEORY_GEOMETRY_KERNEL_REBIND']

def read(name):return json.loads((ROOT/name).read_text())
def write(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def main():
    if (ROOT/'review/CANDIDATE_MANIFEST.json').exists():
        raise SystemExit('Candidate is frozen; assembly is disabled. Apply only reviewed status/publication updates to live metadata.')
    now=datetime.now(timezone.utc).isoformat()
    review=read('review/DECISION.json') if (ROOT/'review/DECISION.json').exists() else None
    accepted=bool(review and review.get('decision')=='PROMOTE_SCOPED' and review.get('status')=='PASS')
    status='PROMOTE_SCOPED' if accepted else 'CANDIDATE_REVIEW_PENDING'
    claim_status='PROMOTE_SCOPED' if accepted else 'PROPOSED_FOR_REVIEW'
    contract={
        'schema':'bass-cr-theory-contract.v1','unit':UNIT,
        'mode':'theory_with_focused_reference_implementation','skill':'physmath-research-loop',
        'policy_version':'1.0.0','date_local':'2026-10-13','timezone':'Asia/Seoul',
        'baseline':{'repository':REPO,'branch':'research/cr-kernel-cutoff-20261013','verified_head':BASE,
                    'prior_science_commit':'a5c29ad4070acb931d92d2bec42a927a57f479ca','source_reuse':'inputs/PRIOR_REUSE.json'},
        'question':'Construct actual-kernel coupled atomic branches, reaction-driven crossing and prescribed massive Bianchi energy/kernel rebind with rigorous scoped error statements.',
        'selected_prior_dag_nodes':SELECTED,
        'assumptions':[
            {'id':'A1','statement':'Metric (-,+,+,+), physical proper time, c/hbar/k_B retained, SI energy with explicit eV conversion. Expansion tensor is K=H gamma+sigma with units 1/s and positive H for expansion.','basis':'BG.1–7; source constants'},
            {'id':'A2','statement':'Accepted PHYS02C full-BED HI/HeI and PHYS02B stopping/projector at pinned source identities; new collision examples use named contributions and energies within original support.','basis':'inputs/prior/inputs/KERNEL_SOURCE_BINDING.json; CB input; geometry witness'},
            {'id':'A3','statement':'One-temperature nonrelativistic ideal-gas EOS U=(3/2)k_B N T. Thermal N includes all nuclei plus thermal electrons; rate-screening ne includes only thermal electrons. Positive base count/energy; retained raw atoms are counted once.','basis':'CB fixed-branch EOS; RB.1–4'},
            {'id':'A4','statement':'Each collision step uses the same immutable initial raw state, initial active donor mask and zero-support policy. A common event extent updates every state component and reservoir.','basis':'accepted KA/CP; CB/RB construction'},
            {'id':'A5','statement':'Constructed fixed-branch domain x in [0,1/20], s in [0,1], V=1m3, h=1e14s, chi=20; source frozen-parameter positive Coulomb logarithm and rational log enclosure.','basis':'results/COUPLED_BRANCH_CHECKS.json'},
            {'id':'A6','statement':'Atomic scan: finite distinct ordered energy support, nonnegative varying weights, N_B>0, U_B>0, chi>=3/2 and equality thermal. The inherited branch is specified. Reaction fixture chi=4 is separate from the fixed-branch fixture.','basis':'RB.1–18'},
            {'id':'A7','statement':'Prescribed geodesic synchronous homogeneous Bianchi normal for local work law; exact finite momentum map uses diagonal Bianchi I with positive scale factors. Raw angular packet counts are retained; unresolved bath geometry needs its own closure.','basis':'BG.1–14; geometry implementation'},
            {'id':'A8','statement':'Positive barycentric energy projection conserves count/first energy moment; Lipschitz or C2 weak error requires its stated within-cell regularity/domain. Threshold indicators and massive angular momentum/stress require their own treatment.','basis':'GEOMETRY_REBIND_KO.md; results/GEOMETRY_REBIND_CHECKS.json'},
            {'id':'A9','statement':'Rational certificates apply to declared finite-source coefficient models and endpoint equations; FP64 geometry and model/quadrature/time errors are distinct. Constructed examples are not an observed or selected cosmological history.','basis':'results error semantics; all four derivations'}],
        'acceptance':['Actual source-bound endpoint with a proved self-map and q<1','Conservative reaction-driven crossing of a created atom with explicit branch selection','Massive covariant geometry law and actual moved-energy kernel identity','Scoped representation/error bounds and new actual Wolfram/xAct checks','Independent review of exact candidate files','LaTeX/PDF, preserved DAG, resumable source and additive research publication'],
        'evidence_reuse':{'file_index':'inputs/PRIOR_REUSE.json','prior_scientific_reruns':0,'meaning':'Copied predecessor evidence is reused at matched bytes/hashes; only new branch/geometry obligations are executed.'},
        'execution':{'full_generator_builds':0,'new_physical_ODE_integrations':0,'NCP_jobs':0,'actual_source_component_evaluations':True,'local_new_reference_checks':True,'actual_wolfram':True,'actual_xact':True},
        'publication':{'repository':REPO,'branch':BRANCH,'base_branch':'research/cr-kernel-cutoff-20261013','repository_unit':REPO_UNIT,'kind':'additive research draft PR','backup':'Dropbox and Google Drive create-only source archive; selective R1','authorization':'Persistent owner instruction, current next-loop request and previously authorized publication workflow'},
        'status':status,
        'conventions':{'counts':'particle counts of one fixed comoving cell; physical volume varies during geometry','thermal_count':'N_nuc+N_e,thermal','screening_density':'N_e,thermal/V','source_speed':'unchanged nonrelativistic source speed','geometry_momentum':'physical orthonormal momentum in kg m/s','geometry_energy':'exact massive formula evaluated in finite arithmetic','cutoff_ownership':'equality thermal; same raw reference every trial','geometry_work':'signed background work accumulator separate from collision heat and cutoff reclassification'}}
    write('CONTRACT.json',contract)
    data=[
        ('BG1','Actual fixed-branch coupled endpoint','Constructed HI sharing contribution plus separate stopping edge on the stated two-extent domain.','A strict self-map with q <= 31/100000 < 1 has one endpoint in this branch; T and ne are reconstructed from the common event state.','derivations/COUPLED_BRANCH_KO.md','CB fixed-point/self-map derivation',['examples/COUPLED_BRANCH_INPUT.json','results/COUPLED_BRANCH_CHECKS.json']),
        ('BG2','Finite-model endpoint error certificate','The source finite-parameter logarithmic stopping model and exact rational endpoint arithmetic.','An 8-term positive log enclosure and fixed-point defect bound certify extent, temperature and cutoff errors; physical/time/source errors are not set to zero.','derivations/COUPLED_BRANCH_KO.md','CB log/residual derivation',['results/COUPLED_BRANCH_CHECKS.json','results/WOLFRAM_SCALAR_RAW.json']),
        ('BG3','Finite scan with reaction-changing atom weights','Finite fixed support, nonnegative weights, positive base EOS and chi>=3/2.','Starting from an inherited branch, the endpoint repair scan terminates in at most M additions or removals, preserves count/energy partition and supplies the threshold jump formula.','derivations/REACTION_BRANCH_KO.md','RB.1–9',['reaction_branch_continuation.py','results/WOLFRAM_SCALAR_RAW.json']),
        ('BG4','Source-bound created-atom crossing construction','Actual HI j4762/sharing38 contribution, constructed neutral inventory, chi=4 and extent path [0,1/2].','The created first-node atom crosses at s=1/4; all four invariants and the self-consistent extent equation hold exactly. At s=1/5 two EOS branches exist and the inherited branch selects continuation.','derivations/REACTION_BRANCH_KO.md','RB.10–18',['results/REACTION_BRANCH_CHECKS.json']),
        ('BG5','Covariant massive Bianchi energy and work','Geodesic synchronous Bianchi normal; finite exact direction map specialized to diagonal Bianchi I.','dW/dt=−c²Kqq/E, its shear form and Bianchi-I momentum map are derived; packet energy work and proper-volume dilution are distinguished from heat/cutoff transfer.','derivations/COVARIANT_GEOMETRY_KO.md','BG.1–14',['results/WOLFRAM_XACT_RAW.json','results/WOLFRAM_SCALAR_RAW.json','results/GEOMETRY_REBIND_CHECKS.json']),
        ('BG6','Actual moved-energy HI/HeI event rebind','Pinned original source formulas evaluated at the represented moved parent energy in source domain.','New sharing, thresholds, source rates and daughter projections are bound to the same moved parent with exact finite event ledgers; lower trace and support guards are explicit.','derivations/GEOMETRY_REBIND_KO.md','GR geometry/rebind derivation',['examples/GEOMETRY_REBIND_WITNESS.json','results/GEOMETRY_REBIND_CHECKS.json']),
        ('BG7','Conservative energy projection and scoped weak error','Positive barycentric map and regular test functions on the declared within-cell source interval.','Count/first energy moment are exact; explicit Lipschitz/C2 bounds include a source HeI rate example. Arbitrary momentum/stress exactness and smooth bounds across threshold are not claimed.','derivations/GEOMETRY_REBIND_KO.md','GR representation/error derivation',['results/GEOMETRY_REBIND_CHECKS.json','results/WOLFRAM_SCALAR_RAW.json'])]
    claims=[dict(zip(['id','title','scope','result','derivation','equations','evidence'],x),status=claim_status) for x in data]
    write('CLAIMS.json',{'schema':'bass-cr-claims.v1','unit':UNIT,'status':status,'claims':claims})
    prior=read('inputs/prior/NEXT_DAG.json');dag=deepcopy(prior)
    future=[
        {'id':'CR_THEORY_MULTI_FAMILY_BRANCH_CONTINUATION','status':'READY_AFTER_SCOPED_ACCEPTANCE','depends_on':[SELECTED[0]],'owner':'bass_cr next theory loop','work':'Couple full actual sharing families and stopping across branch transitions, where thermal electron feedback changes the extents themselves.','first_construction':'Bind adjacent prefix-specific extent maps, bound both domains, locate a compatible crossing and continue the inherited branch.','completion_criteria':['At least two interacting actual families','One crossing with different branch-dependent rate feedback','Local compatibility/uniqueness or an explicit selected multiplicity statement','Targeted refinement/error evidence'],'external_scenario_required':False,'heavy_execution_planned':False},
        {'id':'CR_THEORY_GEOMETRY_COLLISION_COMPOSITION','status':'READY_AFTER_SCOPED_ACCEPTANCE','depends_on':SELECTED,'owner':'bass_cr next theory loop','work':'Compose prescribed geometry and nonlinear collision/cutoff maps with one common work ledger and a local splitting-error budget.','first_construction':'Derive the energy/rate commutator on a threshold-separated interval and an event-aware alternative at a crossing.','completion_criteria':['Explicit order of geometry, rebind, collision and classification','Geometry and collision energy/work accounting','Local error bound plus one step-refinement comparison'],'external_scenario_required':False,'heavy_execution_planned':False},
        {'id':'CR_THEORY_ANGULAR_MOMENT_REMAP','status':'READY_OPTIONAL_THEORY','depends_on':[SELECTED[1]],'owner':'bass_cr future representation research','work':'Construct or characterize positive remapping constraints for massive momentum/stress observables while retaining count and energy.','first_construction':'Use raw angular atoms to formulate finite convex moment feasibility and an observable-specific error bound.','external_scenario_required':False,'heavy_execution_planned':False}]
    original_nodes={n['id']:deepcopy(n) for n in prior['nodes']}
    for node in dag['nodes']:
        if node['id'] not in SELECTED:continue
        node['status']=status
        node['completed_results']=[x['id'] for x in claims if (x['id'] in ('BG1','BG2','BG3','BG4'))==(node['id']==SELECTED[0])]
        node['outputs']=['CONTRACT.json','CLAIMS.json','RESULTS.json','review/DECISION.json']
        node['acceptance']=status
        node['evidence_scope']='Actual finite constructed subfamilies and prescribed geometry; selected physical history remains independently unbound.'
        node['next_obligation']=future[0]['id'] if node['id']==SELECTED[0] else future[1]['id']
    dag['nodes'].extend(future)
    for node in future:
        for parent in node['depends_on']:dag['edges'].append({'from':parent,'to':node['id']})
    dag.update(unit=UNIT,status=status,date_utc=now[:10],date_kst='2026-10-13',created_utc=now,
               base_science_commit=BASE,prior_git_branch_head=BASE,selected_theory_node_ids=SELECTED,
               completed_selected_nodes=SELECTED if accepted else [],new_theory_node_ids=[n['id'] for n in future],added_node_ids=[n['id'] for n in future],
               next_here=[future[0]['id'],future[1]['id']],next_theoretical_task_after_acceptance=future[0],parallel_next_theoretical_task=future[1],
               global_states_promoted=False,new_NCP_dispatch=False)
    dag['acceptance_update']={'unit':UNIT,'status':status,'claims':[x['id'] for x in claims],'review':'review/DECISION.json'}
    dag['current_execution_evidence']={'new_reference_groups':['COUPLED_BRANCH','REACTION_BRANCH','GEOMETRY_REBIND'],'new_xact_identities':8,'new_scalar_identities':24,'new_scalar_inequalities':4,'prior_scientific_reruns':0,'NCP_jobs':0,'ODE_runs':0}
    dag['scheduling_change']={'scope':'Advance the two actual theory nodes without inventing a selected physical scenario or observable budget.','dependency':'All unchanged historical/application nodes and global overlay remain as recorded.'}
    unchanged=[n['id'] for n in prior['nodes'] if n['id'] not in SELECTED]
    current={n['id']:n for n in dag['nodes']}
    assert all(current[x]==original_nodes[x] for x in unchanged)
    assert dag['edges'][:len(prior['edges'])]==prior['edges']
    assert dag['global_overlay_snapshot']==prior['global_overlay_snapshot']
    indegree={k:0 for k in current};children={k:[] for k in current}
    for e in dag['edges']:
        assert e['from'] in current and e['to'] in current
        indegree[e['to']]+=1;children[e['from']].append(e['to'])
    ready=sorted(k for k,v in indegree.items() if v==0);order=[]
    while ready:
        key=ready.pop(0);order.append(key)
        for child in children[key]:
            indegree[child]-=1
            if indegree[child]==0:ready.append(child)
    assert len(order)==len(current)
    preservation={'immediate_prior_path':'inputs/prior/NEXT_DAG.json','sha256':sha('inputs/prior/NEXT_DAG.json'),'prior_nodes':len(prior['nodes']),'prior_edges':len(prior['edges']),'unchanged_prior_nodes':len(unchanged),'updated_prior_nodes':SELECTED,'unchanged_prior_node_ids':unchanged,'all_prior_edges_preserved':True,'global_overlay_preserved_exactly':True,'global_overlay_sha256':canonical(prior['global_overlay_snapshot']),'structural_check':'results/DAG_CHECKS.json'}
    dag['immediate_prior_preservation']=preservation
    dag['historical_immediate_prior_metadata']={
        'source_unit':'CR-THEORY-KERNEL-CUTOFF-20261013',
        'source_path':'inputs/prior/NEXT_DAG.json',
        'source_sha256':sha('inputs/prior/NEXT_DAG.json'),
        'preservation':deepcopy(prior.get('preservation',{})),
        'reference_resolution':deepcopy(prior.get('reference_resolution',{})),
        'semantics':'Exact historical metadata of the immediate predecessor. Its current/local labels refer to that predecessor, not this unit.'}
    dag['preservation']={
        'immediate_prior_nodes':len(prior['nodes']),'current_nodes':len(current),
        'selected_updated_nodes':SELECTED,'unchanged_prior_nodes':len(unchanged),
        'immediate_prior_edges':len(prior['edges']),'current_edges':len(dag['edges']),
        'prior_edges_retained':True,'new_edges':len(dag['edges'])-len(prior['edges']),
        'parent_dag_sha256':sha('inputs/prior/NEXT_DAG.json'),
        'prior_unit':'CR-THEORY-KERNEL-CUTOFF-20261013',
        'historical_metadata':'historical_immediate_prior_metadata'}
    inherited=prior['reference_resolution']
    ancestor=inherited['unchanged_ancestral_resolution']
    kc_base='https://github.com/'+REPO+'/blob/'+BASE+'/research/cr_kernel_cutoff_20261013/'
    dag['reference_resolution']={
        'rule':'Current node paths use the current unit. Every unchanged node uses the explicit origin group below. Absolute URLs retain their own identity.',
        'current_unit':{'unit':UNIT,'relative_path_base':REPO_UNIT+'/'},
        'current_nodes':SELECTED+[n['id'] for n in future],
        'immediate_prior':{'repository_path':'research/cr_kernel_cutoff_20261013','commit':BASE,'dag_sha256':sha('inputs/prior/NEXT_DAG.json')},
        'prior_kernel_cutoff_nodes':{'node_ids':['CR_THEORY_KERNEL_EVENT_ADAPTER','CR_THEORY_THERMAL_CUTOFF_FEEDBACK'],'relative_path_base':kc_base,'source_unit':'CR-THEORY-KERNEL-CUTOFF-20261013','source_science_commit':'a5c29ad4070acb931d92d2bec42a927a57f479ca','source_delivery_head':BASE},
        'prior_feedback_nodes':deepcopy(inherited['prior_feedback_nodes']),
        'prior_theory_nodes':deepcopy(ancestor['prior_theory_nodes']),
        'original_source_nodes':deepcopy(ancestor['original_source_nodes']),
        'historical_metadata':'historical_immediate_prior_metadata.reference_resolution'}
    origin_ids=[node_id for group in ['prior_kernel_cutoff_nodes','prior_feedback_nodes','prior_theory_nodes','original_source_nodes'] for node_id in dag['reference_resolution'][group]['node_ids']]
    assert len(origin_ids)==len(set(origin_ids)) and set(origin_ids)==set(unchanged)
    write('NEXT_DAG.json',dag)
    write('results/DAG_CHECKS.json',{'unit':UNIT,'status':'PASS','kind':'read-only JSON structural check; no prior science suite execution','node_count':len(current),'edge_count':len(dag['edges']),'acyclic':True,'topological_order':order,'preservation':preservation})
    results={'schema':'bass-cr-results.v1','unit':UNIT,'decision':status,'science_status':status,'claims':{x['id']:claim_status for x in claims},
             'new_evidence':{'coupled':'results/COUPLED_BRANCH_CHECKS.json','reaction':'results/REACTION_BRANCH_CHECKS.json','geometry':'results/GEOMETRY_REBIND_CHECKS.json','xact':'results/WOLFRAM_XACT_RAW.json','scalar':'results/WOLFRAM_SCALAR_RAW.json','dag':'results/DAG_CHECKS.json'},
             'review':{'decision':'review/DECISION.json','report':'review/REVIEW_KO.md','status':'PASS' if accepted else 'PENDING'},
             'execution_summary':{'new_local_reference_programs':3,'new_xact_identities':8,'new_scalar_identities':24,'new_scalar_inequalities':4,'prior_scientific_reruns':0,'ODE_integrations':0,'full_generator_builds':0,'NCP_jobs':0},
             'separate_gates':prior.get('preserved_scientific_gates',{}),'source_physics_adoption':False,'selected_history_effect_claim':False,'new_strong_no_go':False}
    write('RESULTS.json',results)
    handoff={'schema':'bass-cr-theory-handoff.v1','unit':UNIT,'created_utc':now,'science_status':status,'review_decision':status,'review_status':'PASS' if accepted else 'PENDING','publication_status':'PENDING','delivery_status':'PENDING','start_here':['REPORT_KO.md','CONTRACT.json','CLAIMS.json','review/DECISION.json','NEXT_DAG.json'],'baseline':contract['baseline'],'research_branch':BRANCH,'repository':REPO,'repository_unit':REPO_UNIT,'accepted_claims':[x['id'] for x in claims] if accepted else [],'candidate_claims':[x['id'] for x in claims],'retained_evidence':'inputs/PRIOR_REUSE.json','execution_summary':results['execution_summary'],'report':{'source':'latex/report.tex','pdf':'latex/report.pdf'},'next_here':[future[0],future[1]],'application_dependencies':{'consumer_budget':prior.get('consumer_budget'),'state':'Existing scenario/source, selected observable budget and receiver admission retain their own unbound/pending states.'},'preserve':prior.get('preserved_scientific_gates',{}),'loop_steps':{'R1_R2':'Matched baseline and reusable evidence','R3_R5':'Actual coupled branch, reaction crossing, massive geometry and remap derivations','R6_R8':'New exact/reference checks and independent review','R9_R10':'Source/PDF/DAG and additive research handoff','C1_C10':'Focused reference code linked to formula domain/input/output and actual targeted evidence; no production solver execution'},'verification_tier':'R1 metadata for additive backup; no default raw redownload','archive_stage_note':'Source archive snapshot precedes final provider receipts; final handoff binds immutable archive and delivery receipt.'}
    write('HANDOFF.json',handoff)
    print(json.dumps({'status':status,'claims':len(claims),'nodes':len(current),'edges':len(dag['edges']),'unchanged_prior_nodes':len(unchanged)},ensure_ascii=False))

if __name__=='__main__':main()
